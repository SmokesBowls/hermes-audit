# Continuation TODO Item 1 — CLOSED

Written 2026-08-18, after both repos' item-1 commits were pushed and
remotely verified. This is a closure amendment against the original
continuation TODO (`08-17-2026-continuation-todo.md`) — that document,
and every design/proof document item 1 produced along the way, stay
exactly as written; nothing is edited or rewritten here.

## Item 1 — concurrent-`/dispatch` mutex for overridden bindings

> "Today's `/dispatch` handler has no lock of its own... A caller
> submitting an explicit override... has no equivalent guard."

Closed. The re-derivation found the gap was actually broader than the
original note stated — `/dispatch` had no serialization at all, for any
caller, override or not; `dragon_2d`/`dragon_3d` were only protected
against each other by accident (a shared frozen identity string), not by
design.

### Commits

- `fef2a00` (hermes-audit) — initial design note, plus the
  `SessionLedger.append()` `turn_id` race recorded as a new, separate
  TODO item.
- `23c6215` (hermes-audit) — corrected design amendment: a reviewer's
  traced interleaving showed the first draft's binding-sourcing
  conclusion was wrong (two non-contending claims could still both
  invoke the same native transcript, since the binding was re-derived
  from mutable Presence); replaced with the immutable-binding design.
- `2142d90` (EngAIn) — implementation, matching the corrected design.
- `ff8d8ff` (hermes-audit) — implementation/test/live-proof receipt.

All four pushed; `origin/main` verified to contain each of them in both
repos.

### What was proven, not just designed

- **`SessionClaimRegistry`** extended to a composite
  `(provider_id, provider_session_id)` key — the native provider
  transcript's real identity — while the public `/claim`/`/release` HTTP
  contract stayed untouched.
- **`ProviderSessionBinding` became a frozen input** to
  `SharedSessionBridge.handle_turn()`, constructed once by the caller
  from its own already-validated request, never re-derived from
  `PresenceRegistry` mid-dispatch — closing the exact race the design
  amendment was written to fix.
- **Claim lifetime** derived from each provider adapter's own real,
  enforced `subprocess.run(timeout=...)` ceiling (90s Hermes / 120s
  Claude Code) plus a fixed margin — one authoritative source, not a
  duplicated literal.
- **Claim ownership** is a UUID minted fresh per `/dispatch` call, never
  a caller-supplied `agent_id`/`instance_id` — so two genuinely
  concurrent calls from the same declared caller still correctly
  contend, confirmed by a dedicated test.
- **The deterministic regression test** (`test_presence_authority_dispatch.py`)
  forces, via real `threading.Event`s wrapped around a monkeypatched
  `presence.register` — never `sleep`-based timing — the exact
  worst-case interleaving the design amendment traced (A claims, B
  claims, A registers, B overwrites, both continue), and proves each
  caller's dispatcher still receives its own originally-requested
  `(provider_id, provider_session_id)`, never the other's.

### Suite results

```
EngAIn (tier1/engainos/tests/):   226/226   (215 baseline + 11 new)
engain_avatar:                     86/86    (unchanged; no code touched)
godot_engain_3d_avatar:           260/263   (unchanged baseline — same 3
                                              pre-existing, unrelated
                                              test_stage8_ticket3b_worker_ownership_red.py
                                              failures every receipt this
                                              session has recorded:
                                              test_ticket3b_runtime_boundary_makes_exactly_one_persistent_worker_available,
                                              test_ticket3b_multiple_submissions_share_one_observed_worker_identity,
                                              test_ticket3b_runtime_shutdown_requests_ticket2f_explicit_stop)
```

### Live proof

1. **Composed Dragon 3D, real HUD, real Hermes** — a real
   `launch_dragon3d.sh` run (composition + presence authority running the
   *new* code + real Godot), a real message typed into the actual
   `CollaborationInput` field of the running ControlHUD, a real Hermes
   response rendered in it. Confirms the new server-side claim coexists
   with the pre-existing worker-level client-side claim without
   disturbing the normal Dragon 3D path — proven live, not assumed.
2. **Real concurrent `/dispatch` contention** — `live_dispatch_mutex_contention_proof.py`:
   a real, standalone `presence_authority_server.py` process, one real
   minted Hermes session, two real concurrent HTTP `/dispatch` calls
   against the identical native transcript. Exactly one dispatch actually
   reached Hermes and returned a real response; the other was rejected
   immediately with `409 DISPATCH_BUSY`, naming the contended
   `provider_id`/`provider_session_id`, and never touched the Hermes CLI
   at all.

### Known, accepted, and intentionally not closed by this work

- The existing client-side/default-path claim in `hermes_session_adapter.py`
  (both avatar repos) was deliberately left unchanged. For the default,
  non-override path this means **temporary double protection** — the old
  client-side claim on the frozen identity string, and the new
  server-side claim on the composite key, both real, both held
  concurrently, redundant rather than conflicting. Retiring the
  client-side claim is production-cutover territory (item 3, still
  open), not this item.
- **`SessionLedger.append()`'s `turn_id` race remains open** — recorded
  as its own TODO item in `fef2a00`'s companion document
  (`08-18-2026-continuation-todo-amendment-ledger-turn-id-race.md`),
  explicitly not fixed as part of item 1, and explicitly not protected by
  this mutex: its contention key is `shared_session_id`, not
  `(provider_id, provider_session_id)`, so two dispatches sharing a
  `shared_session_id` but targeting different native provider sessions
  can still race it. This is next, ahead of restart persistence.

## Updated open-items order

1. ~~Concurrent-`/dispatch` mutex~~ — **done, this document.**
2. `SessionLedger.append()` `turn_id` race — **next.** Design stage first,
   same discipline as item 1: derive what `SessionLedger` actually
   promises about ordering across intentionally-shared `shared_session_id`
   operations before choosing a synchronization primitive.
3. Ledger/cursor persistence across a restart — still blocked behind
   item 2 (persisting an already-possibly-inconsistent ledger would be
   backwards).
4. Production cutover decision — not made.
5. ~~Real Godot launch through this integration~~ — done (2026-08-17).
6. `provider_session_ref`'s frozen-identity limitation — not fixed, still
   just named.
