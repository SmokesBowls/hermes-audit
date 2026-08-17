# ENGAV3D-STAGE8-TICKET-2F
# Explicit Worker Stop/State Lifecycle GREEN

Status: OFFLINE PRODUCTION IMPLEMENTATION GREEN
Date: 2026-08-11
Base authority: ENGAV3D-0030-STAGE8-TICKET2E-PERSISTENT-WORKER-LIFECYCLE-RED
Base HEAD: 77593c205851c97a1b0b46ebdb6ade270309f81a
Provider executions: 0

## Authorized scope

Production:

- `hermes_session_adapter.py`

Test:

- `tests/test_stage8_ticket2e_persistent_worker_red.py`

No Godot, bridge, capture, HUD, avatar, routing, provider, queueing, concurrency,
retry, or restart implementation is authorized.

## Implemented lifecycle

A worker instance exposes exactly the observable lifecycle states required by Ticket 2F:

```text
READY
STOPPING
STOPPED
```

The adapter exposes the worker-owned operation:

```text
request_stop()
```

A newly constructed adapter is `STOPPED` because it does not yet own authoritative
worker service. Successful `prepare()` enters `READY`. A second `prepare()` on the
same started instance fails closed, so terminal `STOPPED` cannot restart that worker
instance.

For the authorized idle-stop lane:

```text
prepare under acquired PID ownership
→ READY

request_stop()
→ STOPPING

poll loop observes STOPPING
→ does not invoke process_once again
→ leaves authoritative service
→ releases PID ownership
→ marks the started worker STOPPED
```

`process_once()` returns false without claiming a mailbox request whenever a started
worker is not `READY`. This protects both `STOPPING` and terminal `STOPPED`.

Pre-ownership direct `process_once()` remains compatible with existing bounded unit
surfaces that exercise request validation without calling `prepare()`. That path is not
a started worker lifecycle and does not permit a terminal started worker to restart.

`request_stop()` is idempotent for the bounded Ticket 2F lifecycle: it transitions
`READY` to `STOPPING` and leaves `STOPPING` or `STOPPED` unchanged.

## Focused stop proof

The Ticket 2E explicit-stop test now proves, without signal injection:

```text
WORKER_STATE_READY=OBSERVABLE
WORKER_STATE_STOPPING=OBSERVABLE
WORKER_STATE_STOPPED=OBSERVABLE

EXPLICIT_STOP_WITHOUT_SIGNAL=PASS
PID_OWNERSHIP_PRESENT_IN_READY=PASS
PID_OWNERSHIP_PRESENT_IN_STOPPING=PASS
PID_OWNERSHIP_RELEASED_BEFORE_STOPPED=PASS

NEW_REQUEST_AFTER_STOP_REQUEST=NOT_ADMITTED
NEW_REQUEST_REMAINS_UNCLAIMED=PASS
RESPONSE_AFTER_STOP_REQUEST=ABSENT
PROVIDER_DISPATCH_AFTER_STOP_REQUEST=0
PROCESSED_LEDGER_AFTER_STOP_REQUEST=UNCHANGED

STOPPED_INSTANCE_REMAINS_STOPPED=PASS
STOPPED_PROCESS_ONCE_RETURNS_FALSE=PASS
```

The test deliberately requests stop while idle. Stop during provider dispatch remains
undefined and unauthorized.

## Existing lifecycle preservation

The four other Ticket 2E tests remain unchanged in purpose and pass:

```text
SINGLE_WORKER_MULTI_REQUEST=PRESERVED
WORKER_SURVIVES_SUCCESS=PRESERVED
WORKER_SURVIVES_LOCAL_REQUEST_FAILURE=PRESERVED
DUPLICATE_REQUEST_EXACTLY_ONCE=PRESERVED
SINGLE_AUTHORITATIVE_WORKER=PRESERVED
```

A/B/C still use one adapter instance and one frozen identity across text-only,
text-only, and current-perception routes. Malformed request M remains a local terminal
rejection with no provider dispatch. Duplicate A remains exactly once. A second PID
owner remains rejected.

## Verification

Focused Ticket 2E:

```text
5 passed
```

Protected repository suite:

```text
196 passed
```

Additional checks:

- Python compilation passed;
- Godot 4.6.1 headless editor initialization passed;
- `git diff --check` passed;
- real provider execution remained hard-forbidden by the Ticket 2E test;
- provider executions remained 0.

One compatibility defect was detected during protected verification: an older unit test
calls `process_once()` directly before `prepare()`. The initial state guard blocked that
established non-worker test surface. The guard was narrowed to started worker instances,
then the focused test, affected regression, and complete protected suite all passed.

## Preservation

Ticket 2F changes only:

- `hermes_session_adapter.py`;
- `tests/test_stage8_ticket2e_persistent_worker_red.py`.

`EngAInBridge3D.gd`, `ControlHUD.gd`, `PerceptionCapture3D.gd`, `DragonAvatar3D.gd`,
and the Ticket 2C tests remain byte-identical to their pre-Ticket-2F identities.
The unrelated modified Dragon file and three untracked snapshot artifacts remain
byte-identical and were not cleaned, staged, restored, or absorbed.

## Non-goals preserved

Ticket 2F does not implement:

- stop during an active provider transaction;
- cancellation or interruption;
- signal policy;
- restart or automatic replacement;
- queueing or parallel requests;
- retry policy;
- Godot worker spawning or shutdown wiring;
- Godot route selection;
- HUD looking/thinking states;
- provider-backed execution.

## Canonical GREEN verdict

```text
STAGE8_TICKET2F_EXPLICIT_STOP_GREEN

WORKER_STATE_READY=OBSERVABLE
WORKER_STATE_STOPPING=OBSERVABLE
WORKER_STATE_STOPPED=OBSERVABLE

EXPLICIT_STOP_WITHOUT_SIGNAL=PASS
NEW_REQUEST_AFTER_STOP_REQUEST=NOT_ADMITTED

SINGLE_WORKER_MULTI_REQUEST=PRESERVED
WORKER_SURVIVES_SUCCESS=PRESERVED
WORKER_SURVIVES_LOCAL_REQUEST_FAILURE=PRESERVED
DUPLICATE_REQUEST_EXACTLY_ONCE=PRESERVED
SINGLE_AUTHORITATIVE_WORKER=PRESERVED

FOCUSED_TICKET2E=5_PASSED
PROTECTED_SUITE=196_PASSED
PROVIDER_EXECUTIONS=0

AUTHORIZED_FILES_CHANGED_ONLY=PASS
PRE_EXISTING_DIRTY_STATE=BYTE_IDENTICAL

HUD_ROUTING=NOT_IMPLEMENTED
THINKING_STATE=NOT_IMPLEMENTED
GODOT_WORKER_WIRING=NOT_IMPLEMENTED
```
