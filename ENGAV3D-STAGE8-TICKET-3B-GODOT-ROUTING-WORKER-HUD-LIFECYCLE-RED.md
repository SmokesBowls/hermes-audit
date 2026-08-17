# ENGAV3D-STAGE8-TICKET-3B
# Godot Routing / Worker Ownership / HUD Lifecycle RED

Status: OFFLINE TEST-ONLY INTENTIONAL RED
Date: 2026-08-11
Base authority: ENGAV3D-0032-STAGE8-TICKET3A-HUD-CAPTURE-ORDER-ADMITTED
Base HEAD: 77593c205851c97a1b0b46ebdb6ade270309f81a
Provider executions: 0
Production implementation: not authorized

## Scope

Ticket 3B adds only:

- `tests/test_stage8_ticket3b_godot_routing_red.py`;
- `tests/test_stage8_ticket3b_hud_lifecycle_red.py`;
- `tests/test_stage8_ticket3b_worker_ownership_red.py`.

The following remain read-only:

- `scripts/EngAInBridge3D.gd`;
- `scripts/ControlHUD.gd`;
- `scripts/PerceptionCapture3D.gd`;
- `scripts/Main.gd`;
- `hermes_session_adapter.py`.

Ticket 3B does not choose whether Godot or a project launcher owns the persistent
adapter process. It tests the observable ownership/readiness/shutdown contract only.

## Focused result

```text
7 failed, 7 passed
```

All failures are future-positive semantic gaps. There are no syntax, collection,
fixture, setup, provider, preservation, or unauthorized-production failures.

## Boundary A — Godot routing

### Already present

```text
CURRENT_PERCEPTION_ROUTE_SELECTION=PASS_ALREADY_PRESENT
CURRENT_PERCEPTION_CAPTURE_PRESERVATION=PASS_ALREADY_PRESENT
ROUTING_PROBE_PROVIDER_FREE=PASS_ALREADY_PRESENT
```

The current `submit()` path performs exactly one
`capture_for_submission(client_request_id)` before the no-replace mailbox publication.
It forwards the producer-owned sealed Stage 7 perception object and does not allocate a
capture identity in the request builder.

### Missing

```text
TEXT_ONLY_ROUTE_SELECTION=FAIL_EXPECTED
TEXT_ONLY_CAPTURE_SUPPRESSION=FAIL_EXPECTED
TEXT_ONLY_MAILBOX_PUBLICATION=FAIL_EXPECTED
```

The mandatory explicit no-current-image fixture has no local routing branch in Godot.
Every accepted submission currently enters capture before publication. Although the
adapter and bridge response validator already know the text-only wire/result forms,
Godot cannot construct or publish that request branch.

The exact submission method requiring separation is:

```text
EngAInBridge3D.submit(text)
```

This observation does not authorize its implementation.

## Boundary B — HUD lifecycle

### Already present

```text
VISIBLE_PRE_CAPTURE_MUTATION_FORBIDDEN=PASS_ALREADY_PRESENT
CORRELATED_STATUS_CLEAR_GATE=PASS_ALREADY_PRESENT
STALE_RESPONSE_CANNOT_CLEAR_GATE=PASS_ALREADY_PRESENT
CAPTURE_FAILURE_LIFECYCLE_RELEASE=PASS_ALREADY_PRESENT
PUBLICATION_FAILURE_LIFECYCLE_RELEASE=PASS_ALREADY_PRESENT
TIMEOUT_LIFECYCLE_RELEASE=PASS_ALREADY_PRESENT
```

The sealed Stage 7 pre-capture quiet boundary remains intact: no accepted user message,
dragon speech signal, looking text, thinking text, or input clear occurs before capture
returns. Response validation compares exact active `request_id` and
`client_request_id`; rejected responses return before `_end_active_lifecycle()`. Capture
and publication failures release the lifecycle before commit. Both capture-pending and
response-pending 180-second timeout paths release it.

### Missing

```text
INTERNAL_LOOKING_STATE=FAIL_EXPECTED
THINKING_AFTER_COMMIT=FAIL_EXPECTED
RUNTIME_SHUTDOWN_STATUS_CLEAR=FAIL_EXPECTED
```

No observable `LOOKING_INTERNAL` state exists before capture. No route-aware visible
thinking lifecycle exists after successful request commit. The existing
`dragon_speaking` boolean/signal is not the Ticket 3A thinking contract. Neither the
bridge nor HUD exposes a runtime-shutdown cleanup boundary for transient thinking.

Because thinking itself is absent, Ticket 3B records existing correlation and failure
release mechanisms separately rather than claiming a currently rendered status clears.

## Boundary C — Godot / worker lifetime

### Already present

```text
WORKER_OWNERSHIP_IMPLEMENTATION_CHOICE=OPEN_AND_PRESERVED
PER_SUBMISSION_ONCE_PROCESSING=ABSENT
DIRECT_PROVIDER_EXECUTION=ABSENT
```

Godot does not call adapter `--once` or `process_once()` for each submission. The bridge
uses bounded provider-free helper invocations only for request publication and response
claim. Ticket 3B does not force `OS.create_process()` or any other process spelling.

### Missing

```text
PERSISTENT_WORKER_AVAILABLE_TO_RUNTIME=FAIL_EXPECTED
SAME_WORKER_ACROSS_SUBMISSIONS=FAIL_EXPECTED
RUNTIME_SHUTDOWN_REQUESTS_EXPLICIT_STOP=FAIL_EXPECTED
```

No Godot/launcher-facing readiness or exclusive-owner observation exists. No stable
worker PID/state/identity is observable across submissions. No runtime shutdown boundary
requests Ticket 2F explicit stop and observes terminal `STOPPED`.

This is an ownership-boundary gap, not a finding that Godot must spawn Python. A later
GREEN may use either:

```text
Godot-owned adapter process
```

or:

```text
project launcher owns adapter + Godot;
Godot observes readiness/lifecycle
```

provided it satisfies the behavior contract.

## Exact expected failures

```text
test_ticket3b_text_only_fixture_selects_text_wire_without_capture
test_ticket3b_internal_looking_is_observable
test_ticket3b_thinking_begins_only_after_successful_request_commit
test_ticket3b_runtime_shutdown_clears_transient_status
test_ticket3b_runtime_boundary_makes_exactly_one_persistent_worker_available
test_ticket3b_multiple_submissions_share_one_observed_worker_identity
test_ticket3b_runtime_shutdown_requests_ticket2f_explicit_stop
```

## Exact already-passing tests

```text
test_ticket3b_current_perception_fixture_preserves_one_stage7_capture
test_ticket3b_routing_probe_has_no_provider_execution_surface
test_ticket3b_visible_precapture_mutation_remains_forbidden
test_ticket3b_only_exact_correlated_response_can_clear_active_status
test_ticket3b_capture_and_publication_failure_release_active_lifecycle
test_ticket3b_timeout_releases_active_lifecycle
test_ticket3b_worker_red_does_not_force_godot_to_spawn_python
```

## Preservation

Ticket 3B preserves:

- Stage 7 capture ordering and frozen tests;
- Ticket 2D text-only adapter/response wire;
- Ticket 2F persistent adapter lifecycle;
- exact production-file identities from Ticket 3A preflight;
- unrelated modified Dragon and untracked snapshot bytes;
- provider execution count zero.

No live memory or provider test is authorized.

## Canonical RED verdict

```text
STAGE8_TICKET3B_GODOT_LIFECYCLE_RED

TEXT_ONLY_ROUTE_SELECTION=FAIL_EXPECTED
CURRENT_PERCEPTION_ROUTE_SELECTION=PASS_ALREADY_PRESENT
TEXT_ONLY_CAPTURE_SUPPRESSION=FAIL_EXPECTED
CURRENT_PERCEPTION_CAPTURE_PRESERVATION=PASS_ALREADY_PRESENT

INTERNAL_LOOKING_STATE=FAIL_EXPECTED
VISIBLE_PRE_CAPTURE_MUTATION_FORBIDDEN=PASS_ALREADY_PRESENT
THINKING_AFTER_COMMIT=FAIL_EXPECTED
CORRELATED_STATUS_CLEAR_GATE=PASS_ALREADY_PRESENT
STALE_RESPONSE_CANNOT_CLEAR_GATE=PASS_ALREADY_PRESENT
TERMINAL_FAILURE_RELEASE=PASS_ALREADY_PRESENT
RUNTIME_SHUTDOWN_STATUS_CLEAR=FAIL_EXPECTED

PERSISTENT_WORKER_AVAILABLE_TO_RUNTIME=FAIL_EXPECTED
SAME_WORKER_ACROSS_SUBMISSIONS=FAIL_EXPECTED
RUNTIME_SHUTDOWN_REQUESTS_EXPLICIT_STOP=FAIL_EXPECTED
WORKER_OWNERSHIP_IMPLEMENTATION_CHOICE=OPEN

FOCUSED_TESTS=7_FAILED_7_PASSED
STAGE7_CAPTURE_ORDER=PRESERVED
TICKET2D_TEXT_ONLY_WIRE=PRESERVED
TICKET2F_WORKER_LIFECYCLE=PRESERVED

PROVIDER_EXECUTIONS=0
PRODUCTION_FILES_CHANGED=0
RUNTIME_IMPLEMENTATION=NOT_AUTHORIZED
```
