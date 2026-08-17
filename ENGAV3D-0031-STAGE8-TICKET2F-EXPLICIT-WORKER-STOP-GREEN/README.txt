ENGAV3D-0031 canonically admits Stage 8 Ticket 2F explicit worker
stop/state lifecycle GREEN.

Authorized changes:
- hermes_session_adapter.py
- tests/test_stage8_ticket2e_persistent_worker_red.py

The worker now exposes READY, STOPPING, and STOPPED plus request_stop(). Idle stop
requires no signal or provider activity. A request appearing after STOPPING remains
unclaimed, ownership persists through STOPPING, and the started instance is terminal
once STOPPED.

Focused Ticket 2E: 5 passed.
Protected suite: 196 passed.
Provider executions: 0.

No bridge, Godot, HUD, capture, avatar, routing, queueing, parallelism, retry, restart,
or active-provider-stop policy was implemented. Pre-existing Dragon/snapshot dirty
bytes remain unchanged.
