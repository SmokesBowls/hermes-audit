# Item 3 Implementation: Durable Per-`shared_session_id` Continuity Journal — Receipt

Written 2026-08-20, implementing the design approved across
`08-19-2026-item3-{restart-continuity-derivation,crash-consistency-design,
encoding-selection-design,frame-and-record-shape-design,
framing-integrity-and-write-failure-amendment}.md`. Lazy, per-session
replay-on-first-touch: on first touch of a `shared_session_id`, acquire
that session's existing ordering lock (item 2's, not a new one),
validate/replay its journal, rebuild `SessionLedger` + cursor state,
mark the session loaded, then allow mutation. A bad journal quarantines
only that session; unrelated sessions continue normally. Stops here, as
instructed — compaction, provider transcript read-back, and production
cutover not started.

## What changed

**New: `tier1/engainos/core/session_journal.py`** — the framing layer.
Two-layer binary format (file header once per file; per-event frames),
kept strictly separate from record encoding so a future project-shaped
ZW body is a new `payload_encoding`/`snapshot_encoding` tag, not a
framing change. Both the file header and every frame split a fixed-size
prefix (own checksum) from a variable-length remainder (own checksum) —
the framing-integrity amendment's own fix, implemented literally:
`BODY_LENGTH` (and the file header's `SESSION_ID_LENGTH`) is never
trusted until its own header checksum verifies. Exactly the replay rule
specified:

```
verified header + insufficient remaining bytes  ->  torn final append,
                                                      discard, safe
invalid header / bad checksum / turn_id gap or
out-of-order / wrong session identity           ->  CORRUPTION,
                                                      quarantine,
                                                      never scan past it
```

Two record types only — `TURN_APPENDED` (request; `actor="player"`
reconstructed, never stored) and `RESPONSE_COMMITTED` (response +
cursor evidence as one physical record: carries `provider_id`/
`provider_session_id`, the one field genuinely new relative to today's
in-memory `Turn`, so cursor state is fully derivable from
`RESPONSE_COMMITTED` frames alone — no separate `CURSOR_ADVANCED`
record, matching the encoding-selection pass's own derived
simplification). `payload`/`snapshot` are opaque, length-delimited,
encoding-tagged triples (`utf8-text` / `json-utf8` today) — never
parsed by the framing layer itself. `shared_session_id` never touches a
filesystem path directly (SHA-256 hex digest filename, verified against
the header's retained original ID on every open — a mismatch is
corruption, not "coincidence vs. bug" doesn't need to be distinguished).
First-creation sequence is `O_CREAT|O_EXCL` write header+first frame,
`flush`+`fsync(file)`, THEN a one-time `fsync` of the containing
directory (new dirent durability, paid once per `shared_session_id`,
never on ordinary appends to an already-existing file).

**Modified: `tier1/engainos/core/session_ledger.py`** — `journal_root`/
`cursor` are both optional constructor args, default `None`; every
pre-item-3 `SessionLedger()` call site is unaffected byte-for-byte, and
this was verified by running the full pre-existing suite unmodified
before writing a single new test. When `journal_root` is set, item 2's
existing per-`session_id` lock — not a second, independent persistence
lock — gains three jobs inside the same critical section: lazy
replay-on-first-touch (the first check inside the lock, so two
concurrent first-touches for the same `session_id` can't race — proven
directly, not assumed, see Tests below); durable write strictly before
the in-memory mutation; and poison-on-uncertainty. Poison
(`SessionPoisoned`) fires if the durable write itself fails
(write/flush/fsync, including the one-time directory fsync), OR if it
succeeds but the immediately-following bare in-memory mutation
(`list.append` / `cursor.advance`) unexpectedly raises — both cases
were named as required in the framing-integrity amendment and both are
now implemented and tested. Quarantine (`SessionQuarantined`) fires
when replay itself detects corruption; the journal file is moved to
`<journal_root>/corrupt/`. Both refusals are per-`session_id` only,
enforced via a `_blocked: Dict[str, SessionUnavailable]` map keyed the
same way as the existing per-session locks — structurally impossible
for one session's block to touch another's.

One design refinement made during implementation, flagged here rather
than silently taken: the design notes don't explicitly say whether
`read_last`/`read_since` should also refuse on a blocked session. Traced
the real call path — `handle_turn()` always appends the request (which
enforces the block) before ever reading context — and concluded reads
should be best-effort (attempt replay-on-first-touch, but never raise on
a blocked session; return whatever's already in memory, possibly empty)
rather than inventing a stronger "reads are blocked too" rule the
design never asked for. A read can't itself corrupt anything, so there
was no correctness reason to extend the refusal there.

**Modified: `tier1/engainos/bridgeroom/shared_session_bridge.py`** —
step 7's response append now passes `binding.provider_id`/
`provider_session_id` through. Step 8's own `cursor.advance()` call is
kept as-is (it's idempotent/monotonic — max-taking — so no double-effect
when the same tracker is wired into both the Ledger and the bridge, and
correct behavior either way if it isn't).

**Modified: `tier1/engainos/server/presence_authority_server.py`** —
module-level `ledger` now constructed with
`journal_root=REPO_ROOT/"runtime"/"sessions"` (an existing, previously
empty, reserved directory — confirmed via `git ls-files runtime/` that
sibling directories like `runtime/logs/`, `runtime/mailboxes/` are
already real, tracked runtime-artifact locations in this repo's own
convention) and `cursor=cursor`. `_handle_dispatch` fails fast on a
known-blocked `shared_session_id` before touching claims or Presence —
same claim-first, don't-do-wasted-work discipline item 1 already
established — and catches `SessionUnavailable` around `handle_turn()`
itself. Both return HTTP 423 with `SESSION_POISONED` or
`SESSION_QUARANTINED`, distinct from every pre-existing dispatch error
code (400/404/409/502). `--journal-root` CLI flag added for isolating a
test/proof run.

**Verified, not assumed, before writing code**: grepped again for any
cross-subsystem consumer of `SessionLedger`/`turn_id`/
`ContinuityCursorTracker` outside `tier1/engainos/` (same check items 2
and 3's design passes already ran) — none found, nothing to retrofit.
`PresenceRegistry`, `SessionClaimRegistry`, `shared_session_id`
ownership, and native provider transcripts are untouched by this
change — none of their modules are imported by `session_journal.py`.

## Tests added

**`tier1/engainos/tests/test_session_journal.py`** (16 tests) — frame/
header integrity at the `SessionJournal` level, forcing every failure
mode named in the instruction: clean round trip (exact field-for-field
reconstruction, including a present snapshot); torn tail after a
verified header — body truncated, checksum-trailer truncated, and zero
body bytes present all discard safely and reconstruct everything before
the torn frame; corrupted `body_length` in both directions is
corruption, never mistaken for a torn tail (the literal case the
framing-integrity amendment named); bad frame checksum on an otherwise
full-length frame; bad frame magic with data still following (not
treated as a torn tail just because it "doesn't parse"); `turn_id` gap
and out-of-order sequence, each across individually checksum-valid
frames (catches spliced-file corruption checksums alone can't); wrong
declared `shared_session_id` in the file header; truncated and
checksum-corrupted file header (both corruption, never "empty session");
mid-stream corruption with a valid-looking frame still following —
proves replay halts at the hole and never skips it to reach the later
frame; `quarantine()` moves the file and is idempotent under a second
call (two concurrent detectors can't crash each other).

**`tier1/engainos/tests/test_session_ledger_persistence.py`**
(11 tests) — `SessionLedger`-level: durable round trip read back by a
**fresh** `SessionLedger`+`ContinuityCursorTracker` object graph (not
the objects that wrote it — the file, not any cache, is what carries
state); `journal_root=None` byte-for-byte unaffected; a response turn
missing `provider_id`/`provider_session_id` is rejected once persisted.
Poison, forced five distinct ways: failed `os.write`, failed
`os.fsync`, a write that succeeds partially then fails mid-loop, a
failing one-time directory-fsync at first creation, and a
post-durability in-memory mutation that itself raises (a `list`
subclass whose `append()` always raises, injected directly) — each
poisons only that one `session_id`; repeated access after poison keeps
refusing (not just the first call, proven with three consecutive
attempts); a completely different `session_id` is proven unaffected in
every one of the five cases; for the in-memory-mutation-failure case
specifically, the durable write that DID land is proven to survive a
fresh reload (disk stayed correct even though this process's memory
poisoned itself). Quarantine: a journal corrupted on disk before any
`SessionLedger` ever touches it quarantines only that `session_id`,
actually moves the file, and leaves a different, healthy `session_id`
fully operational. Concurrency: two real threads racing first touch of
the *same*, pre-existing journal are proven (via an instrumented replay
call counter, not inferred from the lock's mere existence) to replay
exactly once; the same race with no prior journal at all still produces
unique, contiguous `0..N-1` `turn_id`s — item 2's own guarantee,
re-verified with persistence now engaged — confirmed against a fresh
reload of the durable file, not just in-memory.

All new tests pass; re-run 3× with no flakes. Real threads throughout,
no `sleep`-based timing in any concurrency test.

## Suite results

```
EngAIn (tier1/engainos/tests/):   259 passed  (232 baseline + 27 new)
engain_avatar:                     86 passed  (unchanged; no code touched)
godot_engain_3d_avatar:           260 passed, 3 failed (unchanged baseline —
                                    same 3 pre-existing unrelated
                                    test_stage8_ticket3b_worker_ownership_red.py
                                    failures every receipt this session
                                    has recorded)
```

## Live/process-restart proofs (new, required by instruction)

**`tier1/engainos/tools/live_journal_restart_proofs.py`** — two proofs,
each using a **genuinely separate `python3` subprocess** to stand in for
"process restart" (not a new object in the same interpreter), against
real `fsync`'d files in an isolated temp `journal_root`:

1. **Full reconstruction**: two sessions written in this process — one
   single-provider session with a persisted snapshot, one that switches
   provider mid-session (two distinct `(provider_id,
   provider_session_id)` pairs touching the same `shared_session_id`) —
   then fully reconstructed by a separate subprocess through only the
   public `SessionLedger`/`ContinuityCursorTracker` API. Verified exact:
   turn sequence and payloads for both sessions, the snapshot's content
   verbatim, and cursor state for all three native provider pairs.
2. **Truncated-final-frame recovery**: 4 committed frames written (2
   request/response pairs), then the file truncated at 4 distinct
   *interior* byte offsets within the 4th frame — roughly 1 byte in, a
   third in, two-thirds in, and 1 byte short of complete — plus a
   clean-frame-boundary control and a full-file control, each verified
   by its own separate subprocess. Every interior-offset trial recovers
   exactly the 3 fully-committed frames (`turn_id`s `[0, 1, 2]`) and
   nothing more; cursor state reflects only the fully-committed response
   (turn 1), never the torn 4th turn's evidence.

Receipt: `runtime/logs/LIVE_JOURNAL_RESTART_PROOFS_V1.report.json`
(EngAIn repo).

## Regression proofs against items 1 and 2 (required by instruction)

Re-ran both of the earlier items' own existing live/interleaving proofs
against this changed code, unmodified, so persistence can't quietly
regress either guarantee:

- **`live_dispatch_mutex_contention_proof.py`** (item 1's own script) —
  real standalone `presence_authority_server.py` process, now running
  with **real `journal_root=runtime/sessions/` persistence engaged**
  (not a fake/in-memory ledger, since this is the module's own default
  as of this item), one real minted Hermes session, two real concurrent
  `/dispatch` HTTP calls. Unchanged result: caller A genuinely reached
  Hermes and returned (`turn_id: 1`, confirming sequential request=0/
  response=1 assignment under real concurrent HTTP load with real disk
  persistence in the critical section); caller B rejected immediately
  with `409 DISPATCH_BUSY`, never touching the CLI. Updated receipt:
  `runtime/logs/LIVE_DISPATCH_MUTEX_CONTENTION_PROOF_V1.report.json`.
- **`test_continuity_identity_boundary.py`** (item 2's own
  `A-req/B-req/B-resp/A-resp` interleaving proof) — 7/7 passed,
  included in the 259-test full-suite count above and re-run in
  isolation to confirm directly.

## What this does and doesn't establish

Establishes: the lazy-replay-on-first-touch mechanism specified in the
instruction, implemented literally against item 2's existing lock; the
exact frame/header integrity rules from the five design passes,
verified by forcing every named failure mode rather than only testing
normal replay; poison and quarantine both proven to isolate to exactly
one `shared_session_id`, with repeated-access-after-poison, failed-
write/flush/fsync, simultaneous-first-touch, and poisoned-vs-healthy
isolation all directly tested rather than assumed; two real
process-restart proofs (not simulated) for both full reconstruction and
partial-tail-survival; items 1 and 2's own guarantees re-verified live
and unregressed under real persistence.

Does not establish: compaction/retention policy (still explicitly
undesigned, per the crash-consistency pass's own deferral); recovering
window 2's gap (provider succeeded, EngAIn's own write never landed) via
provider transcript read-back — not pursued, matches the crash-
consistency design's own wording-amended framing exactly; the
production-cutover decision; `provider_session_ref`'s frozen-identity
limitation, still just named.

## Commits

Three separate commits, per instruction's own commit-boundary diagram,
all held for review — **none pushed**:

- EngAIn repo, `601139c` — runtime implementation only
  (`session_journal.py` new; `session_ledger.py`,
  `shared_session_bridge.py`, `presence_authority_server.py` modified).
- EngAIn repo, `46b5b6f` — tests + live/process-restart proofs, separate
  from the implementation commit above.
- hermes-audit repo (this commit) — this receipt.

Not started, as instructed: compaction, provider-transcript read-back,
production cutover, the next TODO item.
