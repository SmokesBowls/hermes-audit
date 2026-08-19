# Continuation TODO Item 2 — CLOSED

Written 2026-08-19, after both repos' item-2 commits were pushed and
remotely verified. This is a closure amendment against the continuation
TODO (`08-18-2026-continuation-todo.md`) and item 2's own design/proof
documents — none of those are edited or rewritten here.

## Item 2 — `SessionLedger.append()` `turn_id` race

> "Two dispatches sharing an EngAIn session but targeting different
> provider sessions can bypass the provider-session mutex and race
> `len(turns)`/`append()`." (recorded 2026-08-18, discovered while
> re-deriving item 1)

Closed. Design was re-derived from the actual contract
(`SHARED_SESSION_CONTINUITY_CONTRACT_v1.md`) and every real caller
before any code was proposed, same discipline as item 1.

### Commits

- `1700da2` (hermes-audit) — semantic derivation: `turn_id` contractually
  means unique + monotonic identity per `session_id`, nothing about list
  position or request/response transactional adjacency; traced all five
  real callers; proved the valid `A-request/B-request/B-response/
  A-response` interleaving against them; concluded the minimal fix is
  atomic append-ID assignment alone, not whole-transaction serialization.
- `dea55c0` (EngAIn) — implementation, matching the derivation with one
  review refinement: atomicity of "determine next `turn_id` + insert
  that `Turn`," not a predetermined separate counter mechanism.
- `b74f730` (hermes-audit) — implementation/test/live-proof receipt.

All three pushed; `origin/main` verified to contain each of them in both
repos.

### What was proven

- **Fix scope**: one `threading.Lock` per `shared_session_id`, scoped
  tightly to `SessionLedger.append()`'s own body — `turn_id=len(turns)`
  through `turns.append(turn)` — nothing wider.
- **`turn_id == len(turns)` intentionally preserved** inside that atomic
  section — the contract doesn't require the equivalence, but there was
  no reason to discard it either, and a future persistence layer would
  otherwise have to reconstruct it separately.
- **No reader locking added** — `read_since`/`read_last` remain
  unlocked; no caller was found that needs a transactional snapshot
  across a concurrent append.
- **No whole-`handle_turn()` serialization added** — the fix never
  spans a provider dispatch call. Proven directly, not assumed: a real
  HTTP test holds caller A blocked mid-dispatch (inside item 1's claim)
  while caller B — a different native provider session, same
  `shared_session_id` — completes its full request/dispatch/response
  cycle without waiting on A.
- **The valid interleaving is preserved**: `A-request, B-request,
  B-response, A-response` for one `shared_session_id` proven directly
  against the real Ledger, `ContinuityContextBuilder`, and
  `ContinuityCursorTracker` — B's concurrent request correctly excluded
  from A's own prior context; A's earlier request correctly included in
  B's; final Ledger order and `read_last`'s recency semantics both exact.
- **Item 1's provider-dispatch concurrency semantics preserved** — the
  same real-HTTP test above is the direct proof; item 1's own tests
  (unrelated-provider-session non-contention, same-provider contention)
  continue to pass unmodified.
- **Item 1's own live proof still green, unmodified**: re-ran
  `live_dispatch_mutex_contention_proof.py` exactly as item 1 left it —
  real standalone server, real minted Hermes session, two real
  concurrent `/dispatch` calls — same result (caller A genuinely reaches
  Hermes; caller B rejected with `DISPATCH_BUSY` before touching the
  CLI), now additionally confirming sequential `turn_id`s (request=0,
  response=1) under real concurrent HTTP load.
- **No active ZW/ZON/AP consumer found** — grepped specifically for
  `turn_id`/`SessionLedger`/`ContinuityCursorTracker` references outside
  `tier1/engainos/`, including Trixel32d: none. Nothing in the inspected
  runtime path needed compatibility checking against those formats.

### Suite results

```
EngAIn (tier1/engainos/tests/):   232/232   (226 baseline + 6 new)
engain_avatar:                     86/86    (unchanged; no code touched)
godot_engain_3d_avatar:           260/263   (unchanged baseline — same 3
                                              pre-existing, unrelated
                                              test_stage8_ticket3b_worker_ownership_red.py
                                              failures every receipt this
                                              session has recorded)
```

## Updated open-items order

1. ~~Concurrent-`/dispatch` mutex~~ — done, `08-18-2026-item1-closed.md`.
2. ~~`SessionLedger.append()` `turn_id` race~~ — **done, this document.**
3. Ledger/cursor persistence across a restart — **next, design/
   re-derivation only, no implementation yet** (see below). No longer
   blocked on item 2 — the in-memory ordering a persistence layer would
   need to persist is confirmed no longer race-corrupted.
4. Production cutover decision — not made.
5. ~~Real Godot launch through this integration~~ — done (2026-08-17).
6. `provider_session_ref`'s frozen-identity limitation — not fixed,
   still just named.

## Item 3 opens now — re-derivation, not implementation

The original framing ("ledger/cursor persistence across a restart") was
written before this session's own discovery that a dispatched recap
becomes permanent native-side state regardless of what EngAIn's own
in-memory state does — persisting every Python object blind to that
fact would be solving the wrong problem. Re-opening the question rather
than carrying the old framing forward unmodified:

> After an EngAIn restart, what continuity state is actually lost, which
> of it can already be reconstructed from native/provider state or
> receipts, and which state genuinely requires EngAIn persistence?

To be traced separately before any persistence mechanism is proposed:
`SessionLedger`, `ContinuityCursorTracker`, `shared_session_id`
relationships, provider-session bindings, native provider transcript/
state, ZW/ZON/AP representations (only where an actual active consumer
is found — see item 2's own negative result above), and existing
receipts/transcripts already on disk.

Design/re-derivation only for this next phase. No runtime changes until
reviewed, same sequence as items 1 and 2.
