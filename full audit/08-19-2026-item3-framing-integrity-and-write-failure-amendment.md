# Item 3 Amendment — Header Integrity and Live-Process Write-Failure Policy

Written 2026-08-19, closing the two holes found in `ae701dd`'s framing
design before implementation. **Design only — no runtime code.** Both
fixes are real corrections to that document, not extensions of it —
`ae701dd` itself is left unedited, per this project's standing
discipline; this document supersedes its framing/recovery rules on the
two points below.

## 1. The length field must be validated before it's trusted

`ae701dd`'s frame checksum covered `magic + length + body` as one unit —
but that checksum can only be computed *after* `length` bytes of body
have already been read, which means `length` itself was trusted before
anything checked it. Traced the concrete failure this misses: a fully
committed, correctly-written final frame whose `length` field alone is
later corrupted **upward** (e.g. `100` → `100000`) produces exactly the
same symptom at replay as a genuinely interrupted write — "not enough
bytes remain" — and the old rule treated that symptom as an
unconditionally safe torn tail. It isn't; it's corruption of committed
history, misclassified as a harmless discard.

**Fix**: split frame integrity into two independently-checkable stages,
so `length` is validated *before* it's used to locate anything else.

```
FIXED-SIZE PREFIX (constant size, independent of body length)
    MAGIC
    VERSION
    BODY_LENGTH
    HEADER_CHECK        <- checksum over MAGIC+VERSION+BODY_LENGTH only

VARIABLE PART (only read once the prefix above is validated)
    BODY                (BODY_LENGTH bytes)
    FRAME_CHECK         <- checksum over the whole frame, defense in
                            depth, unchanged in spirit from ae701dd
```

Replay rule, replacing the old single-stage one:

```
read the fixed-size prefix
    ├─ fewer bytes remain than the fixed prefix size
    │      → TORN TAIL (the only case treated this way at this stage) —
    │        genuinely insufficient data to even have a header;
    │        discard, stop, everything before is valid
    │
    └─ enough bytes for the fixed prefix
           ├─ HEADER_CHECK does not match MAGIC+VERSION+BODY_LENGTH
           │      → CORRUPTION — quarantine this session's journal,
           │        regardless of how much data follows. BODY_LENGTH
           │        is never trusted once its own header fails
           │        verification — this is the actual fix.
           │
           └─ HEADER_CHECK matches → BODY_LENGTH is now trusted
                  ├─ fewer than BODY_LENGTH + FRAME_CHECK bytes remain
                  │      → TORN TAIL — the header committed but the
                  │        body/trailer didn't finish; discard, stop,
                  │        everything before is valid
                  │
                  └─ enough bytes remain → read BODY + FRAME_CHECK,
                         verify FRAME_CHECK over the whole frame
                             ├─ mismatch → CORRUPTION, quarantine
                             └─ match → valid frame, apply, continue
```

This produces exactly the distinction required:

```
invalid/unverifiable header  →  corruption; quarantine session
valid header + incomplete declared frame  →  torn final append; discard tail
```

**Applies identically to the once-per-file header**, not only per-record
frames — checked, not assumed, that the same flaw exists there too: the
file header (`ae701dd` §1, §11) carries a variable-length
`shared_session_id`, which means it has the exact same
"variable-length-field-trusted-before-its-own-length-is-verified"
shape. The file header needs its own fixed-size prefix
(`MAGIC`/`VERSION`/`SESSION_ID_LENGTH`/`HEADER_CHECK`) validated before
`SESSION_ID_LENGTH` is used to read the session ID bytes, same
two-stage principle, even though the file header's realistic failure
mode is later corruption rather than an interrupted live write (it's
written once, at creation, per `ae701dd` §6, before any frame ever
follows it — there's no legitimate "torn file header" case during
ordinary operation, only during the very first, already-specially-
handled creation sequence). Named for consistency, not because the
threat model differs.

## 2. Live-process partial-write policy: poison, not rollback

Traced the scenario precisely: a known-good journal offset exists,
`write()` (or `flush()`/`fsync()`) for the next frame fails partway —
some bytes may have reached the file, or none, or the OS's own buffering
makes it genuinely unknown — and the **process does not crash**. If
EngAIn were to catch this and simply attempt the *next* frame afterward,
the result is `valid frame 11, partial/uncertain frame 12, valid frame
13` — precisely the "corruption in the middle of committed-looking
history" case §4–5 of `ae701dd` already ruled must never be silently
tolerated, now self-inflicted by continuing to write past an unproven
tail instead of arriving from outside.

**Choice: poison the affected `shared_session_id` immediately, not
attempt a truncate-based rollback.** Reasoning, not just a lean: the
failure modes that actually cause a `write()`/`fsync()` to fail in the
first place (disk full, underlying I/O error, device failing) are
exactly the conditions under which a subsequent `ftruncate()` +
`fsync()` on the *same* file/filesystem is **also** not reliably
guaranteed to succeed — truncation can itself require free space or
healthy I/O on some filesystems. "Roll back and prove it" is not
actually simple in precisely the cases where it would matter most,
which makes it the wrong default for a design that has chosen the
conservative option at every other decision point in this item. Poison
is not merely the easier implementation — it's the one that doesn't
depend on the same failing resource cooperating a second time.

**The rule, stated absolutely, as instructed**: once an append attempt
for a `shared_session_id` has failed in a way that leaves the durable
tail's true state uncertain, **no further append may ever be attempted
for that session in this process generation.** Concretely:

- Mark that `shared_session_id` poisoned in memory (a new, small piece
  of state — doesn't exist today).
- Refuse **all** further `/dispatch` activity for it — not just further
  appends. Continuing to *serve* requests successfully while quietly
  giving up on persisting them would violate the durability-honesty
  requirement `08-19-2026-item3-crash-consistency-design.md` §4 already
  established (HTTP `200` must never be sent for a state that isn't
  actually durable) — silently degrading to in-memory-only operation is
  exactly that violation, just deferred and harder to notice. Refusing
  outright keeps the dishonesty from ever happening.
- Recovery is a full process restart (which naturally clears the
  in-memory poison flag and re-attempts replay for that session fresh
  next time it's touched) or an equivalent, not-yet-built narrower
  "reload this one session" operator action — not designed further
  here, matching how compaction/repair tooling was already deferred in
  the earlier passes.
- **If a rollback mechanism is ever added later as a refinement**, the
  same absolute rule still governs it: rollback must be *proven*
  successful (truncate return value checked, followed by its own
  `fsync`, itself checked) before another append is attempted — any
  failure or uncertainty in the rollback attempt itself must degrade to
  poisoning, never to "assume it worked and continue writing."

Note what this does *not* affect: the in-memory Ledger/Cursor for that
session, at the moment of the failed append, is unaffected and still
internally consistent — per `ae701dd` §12's own ordering (durable write
always precedes the in-memory mutation for that same turn), the failed
turn was never applied to memory either. The only uncertain thing is the
on-disk tail; poisoning exists specifically to stop anything from
writing past that uncertainty, not to imply memory itself is already
corrupt.

## 3. Replay must complete before a session can be mutated

Stated explicitly, matching the review's own framing, reconciled against
the lazy, per-session replay shape `ae701dd` §14 recommended (eager
whole-server replay was left open there as an alternative — both are
addressed below, since the choice is still deferred to implementation):

- **If eager, whole-server replay at startup is chosen**: the authority
  must not report healthy (`/health`) or accept `/dispatch` for *any*
  session until every discoverable journal has been scanned and any
  corrupt ones quarantined. A global readiness barrier, checked before
  `ThreadingHTTPServer` begins serving.
- **If lazy, per-session replay is chosen** (the shape actually
  recommended in `ae701dd`): there is no single global phase to gate on,
  but the identical race is still possible at a narrower scope — two
  requests for the *same*, not-yet-touched `shared_session_id` arriving
  together after a restart could both observe "no in-memory entry yet"
  and both attempt replay concurrently. This is closed by the same
  mechanism `ae701dd` §12 already established for ordering: **"replay
  this session if it hasn't been replayed yet in this process
  generation" becomes the first action taken *inside* that session's
  existing per-`shared_session_id` lock**, before any new append is
  attempted — the same lock that already serializes appends
  serializes first-touch replay for free, with no new synchronization
  primitive.

Either way, the invariant is: **no request may mutate a session whose
replay/quarantine status is not yet resolved.** Checked what the
authority does *today*, without persistence: `presence`, `claims`,
`ledger`, and `cursor` are constructed as module-level objects at import
time, strictly before `run()` is ever called, strictly before the
`ThreadingHTTPServer` binds — so the "initialize completely before
serving" property already holds trivially in the current, persistence-
free code. Once replay is added, that property must be *preserved*
deliberately (via one of the two mechanisms above, matching whichever
replay shape is chosen), not assumed to carry over automatically — and
should be directly tested at implementation time, per the review's own
suggestion, rather than only documented.

## Status

Both holes closed at the design level:
- Frame *and* file-header integrity now validate their own fixed-size,
  length-declaring portion before trusting it to locate anything
  variable-length — closing the "corrupted length misread as a torn
  tail" gap.
- Live-process partial-write failures are handled by immediate,
  absolute poisoning of the one affected session — never a continued
  append past an unproven tail, never a silent downgrade to
  undurable-but-still-served operation.
- Replay-before-mutation is stated as a hard invariant, with a concrete
  mechanism for both the eager and lazy implementation shapes still left
  open by `ae701dd` §14.

`ae701dd`'s other conclusions — per-session journals; `TURN_APPENDED` +
`RESPONSE_COMMITTED`; response+cursor evidence as one record; no
independent cursor persistence; hashed filenames; the per-session lock
extended only through `fsync`, never across the provider call; poison-
only-that-session as the general disk/RAM-divergence policy; opaque
payload encoding; no fabricated ZW shape — all unchanged, none reopened
by this amendment.

Not yet implemented. This was the last design pass named as a
precondition for implementation; the next step, when taken, is
implementation itself, still wanting its own review before merge/commit
of runtime code, same as every prior item.
