# Item 1 Implementation: Concurrent-`/dispatch` Mutex — Receipt

Written 2026-08-18, implementing exactly the design approved in
`08-18-2026-item1-dispatch-mutex-design-analysis.md` (as amended by its
§9 correction, commit `23c6215` in this repo). This receipt covers
implementation, tests, and live proof only — the runtime code itself is
committed separately in the EngAIn repo, per instruction to keep the
implementation commit and this audit receipt distinct.

Only the approved dispatch-mutex work was implemented. Not touched:
the `SessionLedger.append()` `turn_id` race (already recorded as its own
TODO item), restart persistence, the production-cutover decision, or
`provider_session_ref`'s limitation.

## What changed, mapped to the design note

**`tier1/engainos/core/session_claim_registry.py`** — key type widened
from `str` to `Union[str, tuple[str, str]]` (`ClaimKey`). No behavior
change for existing string keys; the public `/claim`/`/release` HTTP
endpoints and their JSON contract are untouched — they still only ever
pass a plain string, exactly as before.

**`tier1/engainos/bridgeroom/hermes_provider_adapter.py` /
`claude_code_provider_adapter.py`** — each gained one named
`DEFAULT_TIMEOUT_S` constant (90.0 / 120.0, the exact values already in
use as default parameters, now sourced from one place instead of a bare
literal) so the dispatch-claim TTL can read the real enforced timeout
directly rather than duplicating it.

**`tier1/engainos/bridgeroom/shared_session_bridge.py`** —
`handle_turn()` gained a required `binding: ProviderSessionBinding`
parameter. Step 5 uses it directly; the
`ProviderSessionBinding.from_presence_record(record)` call that used to
construct it from Presence is gone from this path entirely. Steps 3 and
6 (Presence liveness gate, response-actor-authorization gate) are
unchanged — both were already correct, independent mechanisms; neither
one's result was ever meant to construct or replace the binding, which
is exactly what made the original code unsafe.

**`tier1/engainos/server/presence_authority_server.py`** —
`_handle_dispatch` now: constructs `binding` directly from the request
body's own required fields, before any claim or Presence call; acquires
a `claims.claim((provider_id, provider_session_id), ..., instance_id=<fresh
uuid4>, lease_seconds=<that provider's own DEFAULT_TIMEOUT_S + 15.0s
margin>)` before `presence.register()` runs at all; rejects a contending
caller immediately with `409 {"error": "DISPATCH_BUSY", "provider_id":
..., "provider_session_id": ..., "current_agent_id": ..., "claim_expires_at":
...}`; wraps everything from `presence.register()` through
`handle_turn()` returning or raising in a `try/finally` that always
releases the claim.

**`tier1/engainos/bridgeroom/mailbox_request_handler.py`** —
`handle_mailbox_request()` gained a required `binding` parameter,
threaded straight through to `handle_turn()`. This is a single-shot,
non-concurrent translation layer (not reachable from
`ThreadingHTTPServer`'s concurrent surface at all — see its own module
docstring), so a caller resolving its own binding once, synchronously,
before calling it carries none of the interleaving risk the design note
traces for `/dispatch`.

**Every existing `handle_turn()`/`handle_mailbox_request()` call site
updated, no fallback left reachable**: `test_shared_session_continuity_proof.py`
(8 calls), `test_continuity_identity_boundary.py` (13 calls, each
binding matching its own preceding `presence.register()`/`_endpoint()`
call exactly — this file's whole point is cursor-keying correctness, so
these bindings are not interchangeable), `test_mailbox_request_handler.py`
(5 calls), and all four `live_*_continuity_proof.py`/
`live_cross_provider_*_proof.py` tool scripts (their code paths verified
by syntax check and by the full offline suite; not re-run live here,
since none of their own logic changed — only the now-required parameter
they already had every field on hand to supply).

## Tests added

- `test_session_claim_registry.py`: composite-key claim/release, second
  claimant rejected, tuple-vs-string key non-collision, three-way
  different-key non-contention — 4 new tests.
- `test_presence_authority_dispatch.py`: 7 new tests —
  - same provider + same provider_session_id → contends, `DISPATCH_BUSY`
  - same provider + different provider_session_id → both proceed
  - different providers + same textual provider_session_id → both proceed
  - same declared caller (identical `agent_id`/`instance_id`) still
    contends, because the claim's owner identity is a fresh UUID, never
    body-derived
  - claim released after successful dispatch (verified via a second,
    sequential dispatch to the same key succeeding)
  - claim released after a dispatch failure (`HermesDispatchError`,
    verified the same way)
  - **the deterministic Presence-overwrite regression test** — forces,
    via real `threading.Event`s wrapped around a monkeypatched
    `presence.register`, the exact worst-case interleaving from the
    design note's §9 trace (A claims, B claims, A registers, B
    overwrites, both continue), and asserts each dispatcher was invoked
    with exactly its own caller's `(provider_id, provider_session_id)` —
    never the other's. One thing this test caught that the design note's
    prose didn't spell out: A's overall HTTP call correctly still gets
    rejected downstream, at the pre-existing, unrelated step-6
    response-actor-mismatch gate (Gate 11) — because both callers shared
    one `shared_session_id`, and B genuinely became the more-recently-
    registered agent for it. That's the *right*, unmodified behavior of
    an orthogonal mechanism, not a defect; the test asserts both the
    routing-correctness invariant (unconditional) and that specific,
    expected downstream interaction (documented in the test itself so a
    future reader doesn't mistake it for a bug).

All new tests pass, confirmed clean across 5 repeated runs with no
flakes (the concurrency tests use real threads and either a blocking
`threading.Event`-gated fake dispatcher or the register-overwrite
barrier above — never `sleep`-based timing).

**Existing public `/claim`/`/release` string-key behavior**: not a new
test — `test_presence_authority_server.py::test_two_different_worker_processes_racing_for_one_claim`
already covers it and continues to pass unmodified, confirming the HTTP
contract truly didn't change.

**Existing default avatar path compatibility**: covered by the live
proof below, not a new EngAIn-repo unit test, since that path lives in
the avatar repos.

## Offline suite results

```
EngAIn (tier1/engainos/tests/):        226 passed  (215 baseline + 11 new)
engain_avatar:                          86 passed  (unchanged baseline; no code touched)
godot_engain_3d_avatar:                260 passed, 3 failed (unchanged baseline —
                                         same pre-existing, unrelated
                                         test_stage8_ticket3b_worker_ownership_red.py
                                         failures every prior receipt this session
                                         has recorded; no code in this repo touched
                                         by item 1 either)
```
Full logs: `evidence/08-18-2026-item1-dispatch-mutex-implementation/*.log`.

## Live proof, in two parts

**1. Default avatar path unaffected by the server-side claim** — real
`launch_dragon3d.sh` launch (composition + presence authority running
the *new* code + real Godot), a real `hi from item1 proof` typed into the
actual `CollaborationInput` field of the real ControlHUD, and a real
Hermes response rendered (`"Hi—I hear your wonderfully strange
signal."`). Log confirms the pre-existing client-side claim still works
exactly as before (`POST /claim` → `POST /release` → `Processed EngAIn
request`) against the now-composite-key-capable `SessionClaimRegistry` —
full backward compatibility, live, not just offline-inferred. Clean
`SIGTERM` teardown afterward, no orphaned processes.
Screenshots + log: `evidence/.../01_before.png`, `02_after_submit.png`,
`dragon3d_launch.log`.

**2. Deliberate concurrent-`/dispatch` contention, real provider** — new
script `tier1/engainos/tools/live_dispatch_mutex_contention_proof.py`:
mints one real Hermes session, starts a real standalone
`presence_authority_server.py` subprocess, fires two real concurrent
HTTP `/dispatch` calls at the identical `(provider_id="hermes",
provider_session_id=<that real session>)`. Result: caller A's dispatch
actually reached Hermes and got back a real response (`"A-ACK"`, exactly
what was asked for); caller B was rejected immediately with `409
DISPATCH_BUSY` naming the exact contended `provider_id`/
`provider_session_id`, and never touched the Hermes CLI at all. Server
process cleanly reaped afterward. Full JSON receipt:
`evidence/.../LIVE_DISPATCH_MUTEX_CONTENTION_PROOF_V1.report.json` (also
written to the EngAIn repo's own `runtime/logs/`, matching this
project's existing live-proof convention).

## What this does and doesn't establish

Establishes: the concurrent-`/dispatch` mutex from the approved design is
implemented, matches the design note's invariant
(`claimed_provider_session_key == actual_provider_session_invoked`) by
construction, is covered by both a deterministic offline regression test
and a real live proof against a genuine provider call, and does not
disturb the existing default avatar dispatch path (proven live, not
assumed).

Does not establish: anything about the `SessionLedger.append()` `turn_id`
race, restart persistence, the production-cutover decision, or
`provider_session_ref`'s limitation — all untouched, as instructed.

## Commits

Runtime implementation (EngAIn repo) and this audit receipt are committed
separately, per instruction. Neither pushed — held for review.
