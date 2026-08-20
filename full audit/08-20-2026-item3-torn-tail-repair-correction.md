# Item 3 Correction: Torn-Tail Repair Before Writable — Receipt

Written 2026-08-20, in response to review of `08-20-2026-item3-implementation.md`
(EngAIn commits `601139c`, `46b5b6f`) before push. This document amends
that receipt — neither it nor the implementation commits it describes
are rewritten, per this project's standing discipline.

## The hole review found

`replay()`'s torn-tail detection was correct — a verified header plus
insufficient remaining bytes was safely treated as an interrupted final
append, discarding it and reconstructing everything before it. What was
missing: `replay()` never removed those torn bytes from the file. A
session marked loaded/writable in that state, then successfully
appended to, would place a new valid frame directly BEHIND the
still-present torn bytes:

```
generation 1:  FRAME 0 (valid)  FRAME 1 (valid)  FRAME 2 (partial) <- crash
generation 2:  detects torn tail, ignores it, marks session writable,
               appends a new frame -> lands AFTER the untouched partial
               bytes, not in their place
generation 3:  FRAME 0 (valid)  FRAME 1 (valid)  <torn bytes>  FRAME (valid)
               -> interior corruption. Quarantined. Permanently.
```

One restart tolerated the damage silently; a second would have
converted it into exactly the kind of mid-stream corruption this
journal's whole design exists to make unrecoverable-on-purpose — self-
inflicted, not arriving from outside. Confirmed by direct inspection
before writing any fix (`grep`/read of `replay()`'s body): it does open
the file `"rb"` (read-only) and never calls `ftruncate`/writes to it
anywhere. The gap was real, not hypothetical.

## The fix

`tier1/engainos/core/session_journal.py`:

- `ReplayResult` gains `bytes_consumed` — the exact offset the last
  verified frame ends at (equal to the file's actual size when there
  was no torn tail). `replay()` remains a pure read; it reports this
  value, it does not mutate anything.
- New `SessionJournal.truncate_to(offset)`: `os.open` (`O_WRONLY`),
  `os.ftruncate`, `os.fsync`, close. Raises `OSError` on any failure —
  by design, so the caller cannot silently proceed.

`tier1/engainos/core/session_ledger.py`:

- `_ensure_loaded_locked()`, immediately after a successful `replay()`:
  if `bytes_consumed < actual_file_size`, calls `truncate_to()` **before**
  installing any turns/cursor state or marking the session loaded. If
  the truncation itself fails, the session is quarantined
  (`SessionQuarantined`) — the same "don't continue on unproven
  durability" rule already governing live-write poisoning, now applied
  to the recovery path exactly as instructed: *"At startup/recovery,
  ... truncation is reasonable ... But if truncate/fsync fails, it must
  quarantine; it cannot continue."*

Sequence now matches the requested one exactly:

```
detect torn tail -> last_good_offset known -> truncate to it
                  -> flush/fsync the truncation -> ONLY THEN mark
                     replay complete/writable
```

## The requested two-restart proof

**`tier1/engainos/tools/live_torn_tail_recovery_proof.py`** — the exact
lifecycle requested, at 4 distinct interior byte offsets within a real
(not fabricated) final frame — 10%, 50%, 90%, and one byte short of
complete:

```
write valid records (2 committed turns)
-> physically truncate the 3rd frame's real bytes at the given offset
-> restart (subprocess 1): recover the 2 valid turns, repair
   (truncate) the torn tail, append a NEW valid turn (turn_id 2)
-> stop
-> restart (subprocess 2): prove the complete 3-turn history
   (2 recovered + 1 new) replays cleanly
```

Both restarts are genuinely separate `python3` subprocesses per trial —
not new objects in the same interpreter — matching the standard already
set by `live_journal_restart_proofs.py`. All 4 offsets pass. The
determinative assertion is physical, not behavioral: after restart 1,
the journal file's actual byte size is asserted equal to the valid-
prefix size (torn bytes verifiably gone from disk), not merely that the
in-memory reconstruction looked correct.

Also confirmed directly, per the two secondary requests — neither
needed redesign, both are now asserted rather than only implied:

- **First-creation directory fsync**: `os.fsync` is called exactly
  twice during first-file creation, in order — the content descriptor
  first (opened `O_WRONLY|O_CREAT|O_EXCL`), then a second, distinct
  descriptor opened `O_DIRECTORY` for the containing directory itself.
  An ordinary append to an already-existing file fsyncs only its own
  content, once — the directory-fsync cost is genuinely one-time, as
  designed.
- **Post-durability RAM-mutation failure**: a durable frame write that
  succeeds, followed by a forced in-memory mutation failure, poisons
  the session and is proven to block `append()`, `raise_if_blocked()`,
  **and** leaves `read_since()`/`read_last()` showing no trace of the
  failed turn (they don't raise, per the read-path's own documented
  best-effort policy, but they never show a phantom success either) —
  all in the same process generation, with a different `session_id`
  proven completely unaffected throughout.

A matching pytest-level test was also added (not just the standalone
live tool), so this lifecycle stays covered in the regular suite going
forward: `test_torn_tail_repair_is_sustainable_across_multiple_restarts`
(parametrized over the same 4 offsets, using fresh `SessionLedger`
instances per "generation" — the established in-process convention) and
`test_torn_tail_repair_failure_quarantines_instead_of_marking_writable`.

## Suite results

```
EngAIn (tier1/engainos/tests/):   264 passed  (259 prior + 5 new)
engain_avatar:                     86 passed  (unchanged; no code touched)
godot_engain_3d_avatar:           260 passed, 3 failed (unchanged baseline —
                                    same 3 pre-existing unrelated
                                    test_stage8_ticket3b_worker_ownership_red.py
                                    failures)
```

Re-ran, unmodified, to confirm this correction regresses nothing
already proven: `live_dispatch_mutex_contention_proof.py` (item 1) —
unchanged pass, real Hermes call, real concurrent `/dispatch`;
`test_continuity_identity_boundary.py` (item 2's interleaving proof) —
7/7; `live_journal_restart_proofs.py` (this item's original two
restart proofs, full reconstruction + single-restart truncation
recovery) — both still pass unchanged.

## What this does and doesn't establish

Establishes: torn-tail recovery is sustainable across repeated
restarts, not merely tolerant of exactly one — proven at 4 distinct
byte offsets with genuine process restarts, with the file's physical
size (not just reconstructed state) as the determinative assertion.
Truncation failure during recovery correctly quarantines rather than
proceeding on an unproven repair. Both secondary properties (directory
fsync at first creation; post-durability RAM-failure poisoning) were
already correctly implemented and are now directly asserted rather than
only implied by failure-path tests.

Does not establish anything new beyond the correction itself — no
unrelated semantics altered, no other TODO item started, matching
instruction exactly.

## Commits

- EngAIn repo, `7120f16` — the correction: implementation fix + tests +
  new live/process-restart proof, one commit (per this review round's
  own instruction — "a small corrective EngAIn commit").
- hermes-audit repo (this commit) — this receipt.

All EngAIn commits for item 3, in order — `601139c`, `46b5b6f`,
`7120f16` — and this repo's `08-20-2026-item3-implementation.md` and
this document, remain **unpushed**, held for review as instructed.
