# Continuation TODO Item 3 — CLOSED

Written 2026-08-20, after all item-3 commits in both repos were pushed
and remotely verified. This is a closure amendment against item 3's own
design/proof documents — none of those are edited or rewritten here,
per this project's standing discipline (amend via new documents, never
rewrite history).

## Item 3 — Ledger/cursor persistence across a restart

Closed. Design was re-derived from first principles before any
persistence mechanism was proposed (`08-19-2026-item3-restart-
continuity-derivation.md`), then carried through a crash-consistency
model, an encoding/framing selection pass, a concrete frame/record
shape pass, and one integrity-and-write-failure amendment — each its
own reviewed document, same discipline as items 1 and 2 — before any
runtime code was written. Implementation then surfaced one real
lifecycle hole under review (torn-tail bytes left physically on disk
after a safe-to-ignore replay), which was traced, fixed, and proven
with a dedicated two-restart recovery test before push — not folded
silently into the original implementation receipt.

### Full audit/design lineage

```
ff9e558  Amendment: item 3 crash-consistency model for Ledger+Cursor persistence
46c51aa  Wording amendment: item 3 window 2 is not permanently irreducible
b8003c7  Amendment: item 3 encoding/storage selection design pass, no implementation
ae701dd  Amendment: item 3 durable frame and record shape, no implementation
1bd0e04  Amendment: item 3 header integrity + live-process write-failure policy
50fa738  Item 3 implementation receipt: durable per-shared_session_id continuity journal
0e6b395  Item 3 correction receipt: torn-tail repair before writable, two-restart proof
```

preceded by `3d9de10` (Design note: item 3 restart-continuity
re-derivation, no implementation) as the pass that opened the item.
All seven documents above, plus `3d9de10`, are the complete design/
proof lineage for this item — verified against the actual
`origin/main..HEAD` range at push time, not assumed from an earlier
summary (a prior push-request round flagged exactly this risk; the
range was inspected directly and matched the full lineage before
pushing, with nothing left behind).

### Runtime commits (EngAIn repo)

- `601139c` — runtime implementation: `session_journal.py` (new, the
  framing layer); `session_ledger.py`, `shared_session_bridge.py`,
  `presence_authority_server.py` modified.
- `46b5b6f` — tests + live/process-restart proofs, a separate commit
  from the implementation above, per this item's own requested commit
  boundaries.
- `7120f16` — the torn-tail recovery correction: physical repair
  (truncate + fsync) of a torn final frame before a session is ever
  marked writable, plus its own tests and live two-restart proof.

## What was proven

**Storage model**: one append-only, framed journal file per
`shared_session_id` — never a global journal, never newline-delimited
JSON. Two record types only: `TURN_APPENDED` (request turns; `actor=
"player"` is a reconstructed contract-level constant, never stored) and
`RESPONSE_COMMITTED` (response turns, carrying `provider_id`/
`provider_session_id` so cursor state is fully derivable from
`RESPONSE_COMMITTED` frames alone — response + cursor evidence
committed as one atomic physical record, no separate `CURSOR_ADVANCED`
event).

**Integrity**: both the file header and every frame split a fixed-size,
independently-checksummed prefix from their variable-length remainder —
a declared length is never trusted until its own header checksum
verifies. A verified header plus insufficient remaining bytes is the
only condition treated as a safe torn tail; an invalid header, a
checksum failure, a `turn_id` sequence gap or out-of-order value, or a
wrong declared `shared_session_id` are all corruption — replay halts
immediately (never scans past a hole looking for the next valid frame)
and the whole session's journal is quarantined.

**Lazy first-touch replay**: the first `append()` (or read) for a given
`shared_session_id` in a process generation replays its journal, if one
exists, as the first action inside that session's existing per-
`session_id` lock (item 2's lock — no second, independent persistence
lock introduced) — proven not to double-replay under two real threads
racing the same first touch, via an instrumented call counter, not
inferred from the lock's mere existence.

**Torn-tail physical repair before writable** (the correction): replay
reports the exact byte offset it stopped at; if that is less than the
file's actual size, the journal is physically truncated to that offset
and `fsync`'d BEFORE the session is marked loaded/writable — closing
the hole where a torn tail, merely ignored rather than removed, would
let a later valid append land behind it and turn recoverable damage
into permanent interior corruption on a subsequent restart. If the
truncation itself fails, the session is quarantined rather than marked
writable on an unproven repair.

**Corruption/quarantine semantics**: a session whose journal fails
integrity or sequence validation — at ordinary replay OR during torn-
tail repair — is quarantined (`SessionQuarantined`): its file is moved
to `<journal_root>/corrupt/`, and it refuses all further append/
`/dispatch` activity until a human resolves it. Isolated per
`shared_session_id`; proven not to affect any other session.

**Poison-on-uncertain-write and poison-on-post-durable-RAM-failure**: a
live durable-write failure (write, flush, fsync, or the one-time
directory fsync at first creation) poisons that one session
(`SessionPoisoned`) immediately — proven via forced failures of
`os.write`, `os.fsync`, a mid-write partial-then-failing loop, and the
directory-fsync call specifically. A durable write that DOES succeed,
followed by a forced in-memory mutation failure (the bare
`list.append`/`cursor.advance` step required to follow it), also
poisons the session — proven directly, not merely asserted — and is
proven to block every subsequent operation in that process generation
(`append()`, `raise_if_blocked()`, and reads correctly showing no trace
of the failed turn) while leaving a different `session_id` completely
unaffected throughout. Recovery from poison is a full process restart;
recovery from quarantine is an operator resolving the file — neither is
automatic.

**First-file directory `fsync`**: confirmed directly (not only inferred
from a failure test) that first-creation calls `os.fsync` exactly
twice, in order — the content descriptor first, then a second, distinct
descriptor opened `O_DIRECTORY` for the containing directory itself —
and that an ordinary append to an already-existing file fsyncs only its
own content, once. The one-time directory-fsync cost is genuinely
one-time, as designed.

**Four-offset two-restart sustainability proof**: the decisive evidence
for the correction. At four distinct interior byte offsets within a
real final frame — 10%, 50%, 90%, and one byte short of complete —
each trial: wrote valid records, physically truncated the final frame
at that offset, restarted (a genuinely separate `python3` subprocess)
to recover and physically repair the torn tail, appended a new valid
turn, then restarted again (a second, independent subprocess) and
proved the complete recovered-plus-new history replayed cleanly. The
determinative assertion at each offset was the journal file's own
physical byte size after repair, not merely that in-memory
reconstruction looked correct.

**Item 1's dispatch concurrency preserved**: `live_dispatch_mutex_
contention_proof.py` (item 1's own script, unmodified) re-run against
the real server with real journal persistence now engaged (not a fake
ledger) — unchanged result: caller A genuinely reached Hermes and
returned with sequential `turn_id`s under real concurrent HTTP load;
caller B rejected with `DISPATCH_BUSY` before touching the CLI.

**Item 2's legitimate interleaving preserved**:
`test_continuity_identity_boundary.py` (item 2's own `A-req/B-req/
B-resp/A-resp` interleaving proof, unmodified) — 7/7 passed, both
inside the full suite count below and re-run in isolation.

**ZW/ZON/AP compatibility left open without inventing a runtime
dependency**: checked a fifth time across this item's design passes and
the implementation itself — no established, project-specific ZW/ZON/AP
shape exists for this role, and none was fabricated to claim
compliance with something the project hasn't actually defined.
`payload_encoding`/`snapshot_encoding` are the deliberately-left-open
extension point: a future project-shaped ZW body would be a new tag
value, requiring no change to the framing layer, the file header, or
any metadata field. No ZON/AP dependency was introduced anywhere in
`session_journal.py`, `session_ledger.py`, `shared_session_bridge.py`,
or `presence_authority_server.py`.

**Explicitly still out of scope, unchanged**: `PresenceRegistry`,
`SessionClaimRegistry`, `shared_session_id` ownership, and native
provider transcripts are not persisted anywhere in this item — verified
by inspection, not merely asserted, since none of their modules are
imported by `session_journal.py`. Provider transcript read-back
(closing window 2's honestly-bounded gap — provider succeeded, EngAIn's
own write never landed), compaction/retention policy, and the
production-cutover decision all remain explicitly undesigned and
untouched, matching every design pass's own deferral exactly.

## Suite results

```
EngAIn (tier1/engainos/tests/):   264/264   (232 item-1/2 baseline + 27 item-3
                                              implementation + 5 torn-tail
                                              correction)
engain_avatar:                     86/86    (unchanged; no code touched)
godot_engain_3d_avatar:           260/263   (unchanged baseline — same 3
                                              pre-existing, unrelated
                                              test_stage8_ticket3b_worker_ownership_red.py
                                              failures every receipt this
                                              session has recorded)
```

All three EngAIn commits (`601139c`, `46b5b6f`, `7120f16`) and the
complete audit/design lineage above are confirmed present on
`origin/main` in both repos, verified directly against `git log
origin/main` and `git merge-base --is-ancestor` for every named commit
— not assumed from a prior summary.

## Updated open-items order

1. ~~Concurrent-`/dispatch` mutex~~ — done, `08-18-2026-item1-closed.md`.
2. ~~`SessionLedger.append()` `turn_id` race~~ — done,
   `08-19-2026-item2-closed.md`.
3. ~~Ledger/cursor persistence across a restart~~ — **done, this
   document.** Not merely persistence — restart persistence with
   defined corruption semantics (verified-header-before-length trust,
   torn-tail physical repair, quarantine) and proven-sustainable
   recovery (the four-offset two-restart proof), not a single-restart
   tolerance.
4. Production cutover decision — not made.
5. ~~Real Godot launch through this integration~~ — done (2026-08-17).
6. `provider_session_ref`'s frozen-identity limitation — not fixed,
   still just named.
7. Provider transcript read-back (would close item 3's own window-2
   gap) — not pursued, named as a future option only.
8. Compaction/retention policy for the continuity journal — not yet
   safe to design, per item 3's own crash-consistency pass; unchanged.

Nothing further started per instruction. Next TODO item not begun.
