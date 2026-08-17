# ENGAV3D-STAGE8-TICKET-2D
# Text-Only Request/Response Implementation GREEN

Status: IMPLEMENTED OFFLINE; PROVIDER EXECUTIONS 0

## Authority

- Repository: `/mnt/data-drive/godot_engain_3d_avatar`
- Base HEAD: `77593c205851c97a1b0b46ebdb6ade270309f81a`
- Stage 8 Ticket 1 + Amendment 1
- Stage 8 Ticket 2A + Amendment 1
- Stage 8 Ticket 2B + Amendment 1
- Ticket 2C RED: `ENGAV3D-0028-STAGE8-TICKET2C-TEXT-ONLY-IMPLEMENTATION-RED`

## Authorized scope

Production files:

- `hermes_session_adapter.py`
- `scripts/EngAInBridge3D.gd`

Test files:

- `tests/test_stage8_ticket2c_text_only_adapter_red.py`
- `tests/test_stage8_ticket2c_text_only_bridge_red.py`

No other production or test file is authorized.

## Implemented adapter boundary

The adapter now admits exactly two request context shapes:

```text
current_perception:
  exact keys = client_request_id, companion_ref, perception
  routing_mode absent

text_only:
  exact keys = client_request_id, companion_ref, routing_mode
  routing_mode = text_only
  perception absent
```

All mixed, untagged-no-perception, explicitly tagged current-perception, unknown-tag,
and extra-key combinations fail closed. Existing Stage 7 perception validation remains
unchanged after branch selection.

`ValidatedRequest.routing_mode` records the admitted originating request branch.
`ValidatedRequest.perception` is absent only for the admitted text-only branch.

For text-only, image preparation is unreachable because the full-perception guard
requires a non-null validated perception object. Command construction receives
`perception=None` and therefore emits zero `--image` arguments. Frozen identity and
session requirements remain unchanged.

Successful text-only response construction preserves both existing key sets and emits:

```text
requested_state = not_requested
effective_state = not_requested
capture_id = null
capture_event = null
capture_phase = null
captured_at = null
metadata_sha256 = null
image_sha256 = null
structured_snapshot_supplied = false
viewport_image_attached = false
failure_code = null
```

No response `routing_mode` is added.

## Implemented bridge boundary

The bridge admits `not_requested/not_requested` only when the active originating
transaction has no capture identity. A valid current-perception request always carries
a non-empty contract-validated capture identity, while the admitted text-only branch
carries none. Thus legality derives from retained originating-request state, never from
a response-side route declaration.

For the text-only branch, every capture/image/provenance identity must be null, both
supply booleans must be false, and `failure_code` must be null. Mixed `not_requested`
states and all other result branches are rejected for the text-only origin.

Existing current-perception full/unavailable response behavior and correlation by
`request_id + client_request_id` remain unchanged.

## Independently demonstrated Ticket 2C test defect

The frozen RED test
`test_ticket2c_text_only_dispatch_has_no_capture_preparation_or_image_argument`
failed after request admission became GREEN because it directly called
`build_contract_command(...)` on a newly constructed client without assigning the
frozen persisted session identity. The production command builder correctly rejected
that invalid harness state before reaching the zero-image assertion.

This was not a missing production behavior: the ticket explicitly requires dispatch
through the same frozen identity/session. The narrow correction assigns
`PERSISTED_HERMES_B_SESSION_ID` to the local mock client immediately before command
construction. No production invariant was weakened and provider execution remains
mock-forbidden.

Test identity progression:

```text
Ticket 2C frozen RED hash:
452097c103ab9d38fd7aed0ae0ab5196836b3d75d7582ef91407d2cd185c7377

Ticket 2D corrected hash:
17bf37dee6e3abb4208b8f2dd15ba14178f9e0e8a493581723804077c9e977af
```

The bridge RED test remains byte-identical:

```text
fc70cfc985a42428768c9c144da3f7fd3655defe766d80bc99912113cfbca465
```

## Verification

Focused Ticket 2C suite:

```text
11 passed
```

Complete protected repository suite:

```text
191 passed
```

Additional checks:

- Python compilation passed;
- Godot 4.6.1 headless editor initialization passed;
- `git diff --check` passed;
- direct provider-free successful response construction passed;
- response top-level keys remain 11;
- `perception_result` keys remain 12;
- complete route-coupled not-requested toxic matrix passed;
- provider executions remained 0.

## Non-goals preserved

Ticket 2D does not implement:

- persistent worker lifecycle;
- multiple sequential requests;
- worker spawn/restart behavior;
- request routing classifier in Godot;
- HUD routing or looking/thinking states;
- queueing, parallel requests, or retry policy;
- memory semantics;
- provider execution;
- changes to `PerceptionCapture3D.gd`, `ControlHUD.gd`, or `DragonAvatar3D.gd`.

## Dirty-state preservation

The pre-existing modified `scripts/DragonAvatar3D.gd` and three untracked
`perception_cap_cb1d91386b9fb24a1f969d439664566e_1.*` artifacts remain byte-identical.
They were not restored, cleaned, staged, or absorbed.

## Final invariant

Ticket 2D proves one honest text-only request/response transaction offline. It does not
prove a second transaction, process persistence, or worker/session lifecycle behavior.
Those remain reserved for a separately authorized Ticket 2E RED.
