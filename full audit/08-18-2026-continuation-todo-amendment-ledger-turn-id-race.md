# Continuation TODO Amendment — New Item: `SessionLedger.append()` `turn_id` Race

Written 2026-08-18, discovered while re-deriving item 1's design
(`08-18-2026-item1-dispatch-mutex-design-analysis.md`, §2, "Resource B").
Recorded here as its own item rather than folded into item 1, per
explicit instruction — it is a real, separate bug with a different
contention key, not solved by the dispatch mutex that document proposes.

## The bug

`tier1/engainos/core/session_ledger.py`, `SessionLedger.append()`:

```python
turns = self._turns.setdefault(session_id, [])
turn = Turn(turn_id=len(turns), ...)   # read
turns.append(turn)                      # write — not atomic with the read above
```

Two threads calling `append()` for the same `shared_session_id`
concurrently can both read the same `len(turns)`, mint two `Turn`s
claiming the same `turn_id`, and leave the Ledger's actual stored order
out of sync with the `turn_id` field that `read_since()`, context
construction, and `ContinuityCursorTracker` all trust as authoritative.

## Why item 1's dispatch mutex does not fix this

The proposed mutex is keyed on `(provider_id, provider_session_id)` —
the native provider transcript's identity. This bug's contention key is
`shared_session_id` — EngAIn's own session identity, a different key
entirely. Two dispatches can share a `shared_session_id` while targeting
two different native provider sessions (e.g. `dragon_2d` overriding to
provider B while `dragon_3d` dispatches under default provider A,
against the same `shared_session_id`) — the mutex would correctly let
both proceed concurrently (they're different native transcripts, no
reason to serialize them against each other), and they would still race
`SessionLedger.append()` for that shared `shared_session_id`.

## Placement in the open-items list

Continuation TODO's original five items, with this inserted as the new
item 2 (immediately after the dispatch mutex, before restart
persistence — persisting a Ledger whose in-memory ordering can already
be invalid would be building on an unsound foundation):

1. Concurrent-`/dispatch` mutex for overridden bindings — design note
   written (`08-18-2026-item1-dispatch-mutex-design-analysis.md`), not
   yet implemented.
2. **New: `SessionLedger.append()` `turn_id` race for concurrent
   same-`shared_session_id` dispatches.** Not started. Needs its own
   concurrency-safe `turn_id` assignment (a lock around the
   read-then-append, or an atomic counter per `session_id`) — likely a
   small, self-contained fix once scoped, but not analyzed further here;
   this document only records the bug and its correct position in the
   queue, per instruction not to fix it as part of item 1.
3. Ledger/cursor persistence across a restart — not started. Should not
   be attempted before item 2 above, since persisting turn ordering that
   can already be internally inconsistent would durably encode the
   corruption instead of just risking it in memory.
4. Production cutover decision — not made.
5. ~~Real Godot launch through this integration~~ — done (see
   `08-17-2026-dragon3d-launch-wrapper-phase1-proof.md` /
   `08-17-2026-listener-absent-structured-diagnostic-phase2-proof.md`).
6. `provider_session_ref`'s frozen-identity limitation — not fixed,
   still just named.
