# ENGAV3D-STAGE8-TICKET-2E
# Persistent Hermes Worker Lifecycle RED

Status: OFFLINE TEST-ONLY INTENTIONAL RED
Date: 2026-08-11
Base authority: ENGAV3D-0029-STAGE8-TICKET2D-TEXT-ONLY-IMPLEMENTATION-GREEN
Base HEAD: 77593c205851c97a1b0b46ebdb6ade270309f81a
Provider executions: 0
Production implementation: NOT AUTHORIZED

## Scope

Ticket 2E tests persistent sequential worker behavior only. It does not authorize
changes to production code, Godot scripts, HUD behavior, routing UI, provider-backed
execution, queueing, parallel requests, retries, restart behavior, or thinking/looking
states.

The only repository addition is:

```text
tests/test_stage8_ticket2e_persistent_worker_red.py
```

Ticket 2C tests are immutable Ticket 2D authority and remain byte-identical.

## Discovery before RED

Ticket 2E did not assume a `--serve`, `run_worker()`, or `serve_forever()` API. It
inspected the current adapter and found the following existing mechanisms:

- default CLI execution owns one adapter instance and polls repeatedly;
- `process_once()` claims at most one request per poll;
- an unread response prevents claiming the next request;
- successful and locally rejected requests are terminal per-request outcomes;
- processed request IDs persist in the frozen session-state ledger;
- duplicate request IDs are suppressed before provider dispatch;
- one PID-file lock excludes a second authoritative mailbox owner;
- `KeyboardInterrupt` exits the polling loop and releases the PID lock.

Therefore the requested example list of six expected failures was not hard-coded.
Tests exercise actual production behavior and preserve the mechanisms already present.

## Frozen lifecycle fixtures

The focused test uses one adapter instance and one offline mock director. It publishes
sequentially, only after the prior response reaches terminal mailbox state:

```text
A = text_only
B = text_only
C = current_perception/unavailable
```

A and B use the admitted Ticket 2D text-only wire. C uses the preserved Stage 7
current-perception unavailable branch, which proves persistence is route-independent
without requiring image preparation.

The offline director records three logical dispatches and installs synthetic validated
provider receipts. A class-level hard-fail mock forbids the real provider subprocess
boundary for every test:

```text
mock logical dispatch count = 3
real provider executions = 0
```

All three logical dispatches retain exactly:

```text
profile       = default
companion     = hermes_b
provider      = openai-codex
model         = gpt-5.6-sol
session_id    = 20260731_065008_63a62d
```

## Passing observed lifecycle controls

The finalized focused RED proves these current behaviors already pass:

### One worker, three sequential route-independent transactions

```text
WORKER_START_COUNT=1
REQUEST_A_PROCESSED=1
REQUEST_B_PROCESSED=1
REQUEST_C_PROCESSED=1
RESPONSE_A_CORRELATED=PASS
RESPONSE_B_CORRELATED=PASS
RESPONSE_C_CORRELATED=PASS
SESSION_ID_A=SAME
SESSION_ID_B=SAME
SESSION_ID_C=SAME
WORKER_ALIVE_AFTER_A=true
WORKER_ALIVE_AFTER_B=true
WORKER_ALIVE_AFTER_C=true
MAILBOX_TERMINAL_CLEANUP=PASS
```

### Local request failure survival

```text
VALID_A=SUCCESS
MALFORMED_M=LOCAL_REJECTION
PROVIDER_DISPATCH_M=0
WORKER_ALIVE_AFTER_M=true
VALID_B=SUCCESS
SESSION_ID_B=SAME
```

### Duplicate exactly-once behavior

```text
REQUEST_A_DISPATCH_COUNT=1
DUPLICATE_REQUEST_A_DISPATCH_COUNT=0
PROCESSED_LEDGER_OCCURRENCE_A=1
WORKER_ALIVE_AFTER_DUPLICATE=true
```

### Exclusive worker ownership

```text
WORKER_1_OWNS_PID_LOCK=true
WORKER_2_ACQUIRE=FAIL_CLOSED
WORKER_1_REMAINS_AUTHORITATIVE=true
```

## Intentional missing behavior

The current polling loop has no explicit worker-owned stop request or observable worker
state. Shutdown is available only by injecting `KeyboardInterrupt` into `main()`.
Consequently production cannot directly prove the Ticket 1 lifecycle:

```text
READY -> STOPPING -> STOPPED
```

through a worker API/state boundary independent of process signal injection.

The one intentional future-positive test requires behavior, not a final method spelling.
It accepts an explicit callable named `request_stop`, `stop`, or `shutdown`, together
with an observable state in the frozen Ticket 1 state set. Ticket 2F may refine the
exact production API if it preserves this behavior.

## Finalized focused result

```text
1 failed, 4 passed
```

Exact intentional failure:

```text
test_ticket2e_worker_exposes_explicit_stop_lifecycle_without_signal_injection
```

Failure meaning:

```text
EXPLICIT_STOP_LIFECYCLE=FAIL_EXPECTED
NO_EXPLICIT_WORKER_STOP_BEHAVIOR=OBSERVED
NO_OBSERVABLE_WORKER_STATE=OBSERVED
```

The four lifecycle/preservation tests pass. Any future fixture, setup, collection,
provider-guard, A/B/C persistence, malformed-survival, duplicate-suppression, or
ownership failure invalidates this RED rather than adding an admitted implementation
gap.

## Canonical RED verdict

```text
STAGE8_TICKET2E_PERSISTENT_WORKER_RED

SINGLE_WORKER_MULTI_REQUEST=PASS_ALREADY_PRESENT
WORKER_SURVIVES_SUCCESS=PASS_ALREADY_PRESENT
WORKER_SURVIVES_LOCAL_REQUEST_FAILURE=PASS_ALREADY_PRESENT
DUPLICATE_REQUEST_EXACTLY_ONCE=PASS_ALREADY_PRESENT
SINGLE_AUTHORITATIVE_WORKER=PASS_ALREADY_PRESENT
EXPLICIT_STOP_LIFECYCLE=FAIL_EXPECTED

TICKET2D_TEXT_ONLY_TRANSACTION=PRESERVED
STAGE7_CURRENT_PERCEPTION=PRESERVED

FOCUSED_TESTS=1_FAILED_4_PASSED
PROVIDER_EXECUTIONS=0
PRODUCTION_FILES_CHANGED=0
PRE_EXISTING_DIRTY_STATE=BYTE_IDENTICAL

PERSISTENT_WORKER_IMPLEMENTATION=NOT_AUTHORIZED
HUD_ROUTING=NOT_AUTHORIZED
```

## Stop boundary

Ticket 2E admits one lifecycle RED gap only. It does not authorize implementing that
gap. Ticket 2F should be bounded by the observed result and should not rewrite already
passing multi-request, request-failure survival, duplicate, or ownership behavior.
