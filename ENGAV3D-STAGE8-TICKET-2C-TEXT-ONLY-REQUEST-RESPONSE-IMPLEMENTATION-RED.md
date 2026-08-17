# ENGAV3D-STAGE8-TICKET-2C
# Text-Only Request/Response Implementation RED

Status: FROZEN OFFLINE TEST-ONLY INTENTIONAL RED

## Authority

- Base repository: `/mnt/data-drive/godot_engain_3d_avatar`
- Base HEAD: `77593c205851c97a1b0b46ebdb6ade270309f81a`
- Request authority: Stage 8 Ticket 2A Amendment 1
- Response authority: Stage 8 Ticket 2B Amendment 1
- Provider executions authorized: `0`
- Production implementation: `NOT AUTHORIZED BY THE RED GATE`
- Persistent-worker behavior: out of scope

## Authorized repository changes

Only these new test files are authorized:

- `tests/test_stage8_ticket2c_text_only_adapter_red.py`
- `tests/test_stage8_ticket2c_text_only_bridge_red.py`

No production file may be edited by Ticket 2C, including:

- `hermes_session_adapter.py`
- `scripts/EngAInBridge3D.gd`
- `scripts/ControlHUD.gd`
- `scripts/PerceptionCapture3D.gd`
- `scripts/DragonAvatar3D.gd`

## R1 — adapter request admission

Given the exact admitted Ticket 2A request whose `additional_context` has exactly
`client_request_id`, `companion_ref`, and `routing_mode=text_only`, with
`perception` absent, the current adapter is expected to fail admission.

Future required behavior: accept it as the explicit `text_only` branch without
weakening the sealed Stage 7 branch.

## R2 — text-only image exclusion

Given an admitted `text_only` request:

- capture preparation must not occur;
- `prepare_image_dispatch(...)` must not occur;
- provider command construction must contain zero `--image` arguments;
- no current-image path or capture identity may be derived or attached;
- no Hermes/provider invocation may occur in this RED.

This requirement is tested using mocks and local command construction only.

## R3 — bridge text-only success admission

Given the originating request route `text_only`, deterministic correlation by
`request_id + client_request_id`, and a response with the existing response and
`perception_result` key sets using:

- `requested_state=not_requested`;
- `effective_state=not_requested`;
- all capture/image identities null;
- snapshot/image booleans false;

then the current bridge is expected to reject it.

Future required behavior: accept this route-coupled successful text-only result.
No response `routing_mode` is added.

## R4 — Stage 7 preservation

The focused RED suite must continue to pass preservation checks for:

- exact Stage 7 full request bytes and current adapter request admission;
- exact existing unavailable request bytes and current adapter request admission;
- exact Stage 7 0021 full response bytes and current bridge admission;
- exact existing unavailable response bytes and current bridge admission.

The copied full request may conservatively validate with an unavailable effective
state when its historical snapshot evidence is not re-homed into the repository.
The preservation assertion is exact bytes plus unchanged request branch admission,
not a fabricated replay of missing historical evidence.

## Route-coupled toxic cases

The new tests must define and preserve rejection for:

- `text_only + full/full` result;
- `text_only + unavailable/rejected` result;
- `current_perception + not_requested/not_requested` result;
- `text_only + perception present` request;
- untagged request with perception absent;
- `routing_mode=current_perception` request;
- `not_requested` result with non-null `capture_id`;
- `not_requested` result with non-null `image_sha256`.

The result route is supplied to the bridge test harness through the originating
request's active capture context. The response never self-declares its route.

## Canonical expected RED

Exactly these future-positive tests must fail against the unchanged production
implementation:

1. `test_ticket2c_adapter_admits_exact_text_only_request`
2. `test_ticket2c_text_only_dispatch_has_no_capture_preparation_or_image_argument`
3. `test_ticket2c_bridge_admits_correlated_text_only_success`

All fixture self-checks, Stage 7 preservation assertions, and route-coupled toxic
rejections must pass.

Canonical summary:

```text
STAGE8_TICKET2C_IMPLEMENTATION_RED
TEXT_ONLY_REQUEST_ADMISSION=FAIL_EXPECTED
TEXT_ONLY_IMAGE_SUPPRESSION=FAIL_EXPECTED
TEXT_ONLY_SUCCESS_RESPONSE_ADMISSION=FAIL_EXPECTED
STAGE7_FULL_REQUEST=PRESERVED
STAGE7_UNAVAILABLE_REQUEST=PRESERVED
STAGE7_FULL_RESPONSE=PRESERVED
STAGE7_UNAVAILABLE_RESPONSE=PRESERVED
ROUTE_COUPLED_TOXICS=DEFINED_AND_PASSING
FOCUSED_TESTS=3_FAILED_8_PASSED
PROVIDER_EXECUTIONS=0
PRODUCTION_FILES_CHANGED=0
IMPLEMENTATION_GAPS=3
```

Implementation gaps:

1. adapter has no admitted `text_only` request branch;
2. adapter has no reachable explicit zero-image `text_only` dispatch branch;
3. bridge has no `not_requested/not_requested` success branch.

A failure other than those exact three is not admitted by this RED authority.

## Unrelated dirty state

The following state pre-existed Ticket 2C and remains unrelated:

- modified `scripts/DragonAvatar3D.gd`;
- untracked `snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.json`;
- untracked `snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png`;
- untracked `snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png.import`.

Ticket 2C must not clean, restore, stage, rewrite, or absorb those files. Their
bytes are frozen in the canonical RED evidence solely to prove non-interference.

## Stop boundary

Passing this intentional RED does not authorize production changes. Ticket 2D
must receive separate explicit authorization before modifying adapter or bridge
implementation. Persistent worker lifecycle remains deferred to a later ticket.
