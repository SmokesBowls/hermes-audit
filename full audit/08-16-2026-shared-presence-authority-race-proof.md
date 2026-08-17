# Shared Presence Authority — Real Cross-Process Claim Race Proof

Written: 2026-08-16, following the operator's correction that a per-process
`PresenceRegistry` would be false integration: two worker processes each
holding their own in-memory registry can never see each other, so
`resolve()` could not have enforced a single live owner of the shared
Hermes session — it would have looked protected in tests while leaving the
real concurrency race intact.

## What was built

1. `tier1/engainos/core/session_claim_registry.py` (EngAIn) — a new,
   separate mutex primitive. Distinct from `PresenceRegistry` on purpose:
   presence answers "is an instance reachable"; this answers "who currently
   holds the right to dispatch, right now." Thread-safe via one lock;
   8 offline tests, including a genuine 50-thread contention test with
   exactly one winner.
2. `tier1/engainos/server/presence_authority_server.py` (EngAIn) — the one
   process-shared owner of both `PresenceRegistry` and
   `SessionClaimRegistry`, over plain HTTP (`ThreadingHTTPServer`, stdlib
   only), bound to `127.0.0.1:8767`. This is what makes presence and claims
   real across process boundaries — an in-process object cannot do that.
   4 offline tests against a real bound socket in a background thread.
3. `presence_authority_client.py` — vendored (not imported cross-repo) into
   both `engain_avatar` and `godot_engain_3d_avatar`, stdlib-only HTTP
   client for the above.
4. `hermes_session_adapter.py` in both avatar repos — `prepare()` now
   registers with the shared authority using the worker's actually
   configured `provider`/`model` (read from `self.client`, never hardcoded
   in the new code); the real Hermes dispatch call in
   `_process_claimed_request` is now wrapped with
   `_acquire_dispatch_claim()` / `_release_dispatch_claim()`. A genuine
   `SESSION_OCCUPIED` produces a new mailbox failure code of the same name
   and never reaches Hermes. An unreachable authority server fails open
   (worker behaves exactly as before) — this was a deliberate choice so
   that a not-yet-normally-running side service can't break the currently
   working dragon; it is not the same thing as failing open on a genuine
   competing claim, which always blocks dispatch.

Diff size: `engain_avatar/hermes_session_adapter.py` — 139 lines added, 0
removed. `godot_engain_3d_avatar/hermes_session_adapter.py` — 93 lines
added, 0 removed. No existing method signature, mailbox schema, or GDScript
file was touched in either repo.

## Regression check

Both avatar repos' full offline suites were run before and after the edit.
`engain_avatar`: 73/73 passed, unchanged. `godot_engain_3d_avatar`: 232
passed, 3 failed — confirmed via `git stash` + rerun to be the identical 3
pre-existing Stage 8 Ticket 3B RED tests (reading `Main.gd`/
`EngAInBridge3D.gd`/`project.godot`, unrelated to this change), failing
identically before this edit. Not a regression.

## The actual race proof

Started `presence_authority_server.py` as a real background OS process.
Launched two genuinely separate OS processes — one per avatar repo, each
importing that repo's own vendored `presence_authority_client.py`, the
exact module its real `hermes_session_adapter.py` calls — both attempting
to `claim()` the real, shared, frozen session_id
(`20260731_065008_63a62d`) within milliseconds of each other:

```
2D worker (dragon2d-652313):
    {"instance_id": "dragon2d-652313", "outcome": "CLAIMED",
     "claim_token": "19409d47ddfc4777a9150a3bf439e89d"}
    {"instance_id": "dragon2d-652313", "outcome": "RELEASED", "released": true}

3D worker (dragon3d-652314):
    {"instance_id": "dragon3d-652314", "outcome": "SESSION_OCCUPIED",
     "current_agent_id": "hermes", "current_instance_id": "dragon2d-652313"}
```

Exactly one winner. The loser received a real rejection naming the real
winning instance — not a fixture, not a simulated peer, not two objects in
one test process. This is the property a per-process registry could not
have provided: two separate registries would have let both processes
"win" locally and neither would ever have known the other existed.

## Deliberately not done in this step

- No change to the mailbox request/response JSON schema in either repo.
- No change to either project's Godot-side GDScript.
- No lease-timeout background sweeper for `SessionClaimRegistry` (matches
  `PresenceRegistry`'s existing scope note: lazy expiry only, checked on
  read).
- No startup wiring — `presence_authority_server.py` is not part of either
  avatar project's or EngAIn's normal launch sequence yet. It must be
  started manually (`python3 tier1/engainos/server/presence_authority_server.py`)
  for the claim protection to be active; both workers fail open and behave
  exactly as before if it isn't running. Making it a required, supervised
  part of a real launcher is a separate decision, not made here.
- `hermes_session_adapter.py`'s continuity mechanism itself (Hermes's own
  `--resume`-based session persistence) is untouched. This step only adds a
  lock around *when* a worker is allowed to use it, not *how* it works.
