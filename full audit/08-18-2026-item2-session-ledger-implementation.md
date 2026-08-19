# Item 2 Implementation: `SessionLedger.append()` Atomicity — Receipt

Written 2026-08-18, implementing the semantic conclusion approved in
`08-18-2026-item2-session-ledger-semantic-derivation.md` (commit
`1700da2`), with one implementation-level refinement from review: the
proven requirement is atomicity of "determine next `turn_id` + insert
that `Turn`," not necessarily a separate counter mechanism. Stops here,
as instructed — restart persistence not started.

## What changed

**`tier1/engainos/core/session_ledger.py`** — `SessionLedger` gained
`_locks: Dict[str, threading.Lock]` (one lock per `session_id`, created
lazily) and `_locks_guard` (a single lock protecting only the
get-or-create of a per-session lock — never the append work itself, so
two different `session_id`s' appends never wait on each other).
`append()`'s body — `turn_id=len(turns)` through `turns.append(turn)` —
is now the atomic critical section, held under that session's own lock
only. Nothing else changed: `len(turns)` is unchanged (confirmed correct
per the design note — the contract doesn't forbid the equivalence,
there's no reason to give it up, and every `SessionLedger()` construction
site in the codebase starts empty with no pre-existing/non-contiguous
turns to worry about — verified by grep, not assumed: zero persistence/
load path exists anywhere `_turns` is touched). `read_since`/`read_last`
remain unlocked, per explicit instruction not to solve reader-snapshot
consistency without an found need for it.

**Verification done before writing code, per instruction**:
- Every `SessionLedger()` construction site in the repo takes no
  arguments and starts empty — grepped, not assumed.
- `_turns` has exactly one write path, `append()` itself — no other
  code anywhere populates it.
- Zero cross-subsystem consumers of `SessionLedger`/`Turn` outside
  `tier1/engainos/` — grepped specifically for ZON/AP/Trixel references
  to `turn_id`/`SessionLedger`/`ContinuityCursorTracker`: none found.
  Nothing to retrofit, nothing to check compatibility against.

## Tests added

**`tests/test_session_ledger.py`** (new file, 4 tests, real threads):
concurrent appends to one session produce unique IDs; IDs monotonically
match stored append order; a broader many-sessions-at-once sanity check
(10 sessions × 20 threads each, every session ends up exactly
`0..19`); independent `session_id`s provably do not contend (one
session's lock held open by the test itself while a different session's
append is proven to complete without waiting on it).

**`tests/test_continuity_identity_boundary.py`** (+1 test): the approved
semantic conclusion — `A-req, B-req, B-resp, A-resp` for one
`shared_session_id` — proven directly against the real `SessionLedger`,
`ContinuityContextBuilder`, and `ContinuityCursorTracker`, deliberately
*not* routed through two full `handle_turn()` calls (that would entangle
this with Gate 11's own, separately-tested, orthogonal response-actor
authorization — see item 1's own regression test for that interaction).
Confirms: B's concurrent request correctly does not appear as A's prior
context; A's earlier request correctly does appear as B's prior context
and gets recapped (native-B has never seen it); A's own dispatch input
never sees B's exchange, because it didn't exist yet when A's context
was read; final Ledger order is exactly `A-req(0), B-req(1), B-resp(2),
A-resp(3)`; `read_last(direction="response")` correctly returns A's
response per the contract's own recency definition, even though B's
whole exchange both started and finished first.

**`tests/test_presence_authority_dispatch.py`** (+1 test): a real,
HTTP-level proof that the per-`shared_session_id` Ledger lock never
spans a provider dispatch — while caller A's real dispatch is blocked in
flight (holding item 1's claim), caller B (a different
`(provider_id, provider_session_id)`, same `shared_session_id`)
completes its full request-append/dispatch/response-append while A is
still blocked. If the Ledger lock had ever grown to span
`handle_turn()`'s dispatch call, B would hang until A's release fires —
it doesn't. (A's own eventual status, `409 RESPONSE_ACTOR_MISMATCH`, is
the same pre-existing, unrelated Gate 11 interaction item 1's own
regression test already documents — not what this test is checking.)

All new tests pass, confirmed clean across 5 repeated runs of the full
affected-file set, no flakes — real threads throughout, no
`sleep`-based timing anywhere.

## Suite results

```
EngAIn (tier1/engainos/tests/):        232 passed  (226 baseline + 6 new)
engain_avatar:                          86 passed  (unchanged; no code touched)
godot_engain_3d_avatar:                260 passed, 3 failed (unchanged baseline —
                                         same 3 pre-existing unrelated
                                         test_stage8_ticket3b_worker_ownership_red.py
                                         failures every receipt this session
                                         has recorded)
```
Full logs: `evidence/08-18-2026-item2-session-ledger-implementation/*.log`.

## Integration smoke test

Re-ran `live_dispatch_mutex_contention_proof.py` (item 1's own live-proof
script, unmodified) end to end: real standalone `presence_authority_server.py`
process, one real minted Hermes session, two real concurrent `/dispatch`
HTTP calls. Result unchanged from item 1's own proof — caller A's
dispatch genuinely reached Hermes and returned (`turn_id: 1`, confirming
the new per-session lock correctly assigned sequential IDs — request
turn 0, response turn 1 — under real concurrent HTTP load); caller B
rejected immediately with `409 DISPATCH_BUSY`. Clean process teardown,
no orphans. Receipt: `evidence/.../live_smoke_test_receipt.json`.

## What this does and doesn't establish

Establishes: `SessionLedger.append()`'s `turn_id` race is closed with
the smallest correct fix — atomicity scoped to "determine next ID +
insert," per-`session_id`, never spanning a provider call — proven both
by targeted unit tests and by real concurrent HTTP load against the
live server. Item 1's provider-dispatch concurrency is unaffected,
proven directly, not assumed.

Does not establish: anything about restart persistence (item 3, still
blocked behind this — but now unblocked in the sense that the
in-memory ordering it would need to persist is no longer known-corrupt),
the production-cutover decision, or `provider_session_ref`'s limitation.
Not started, as instructed.

## Commits

Runtime implementation (EngAIn repo) and this audit receipt are
committed separately, per instruction. Neither pushed — held for review.
