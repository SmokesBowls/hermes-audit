# ENGAV3D-STAGE8-TICKET-2B-AMENDMENT-1
# Successful-No-Perception Result Branch

**Status:** FROZEN RESPONSE-WIRE AMENDMENT; RUNTIME IMPLEMENTATION NOT AUTHORIZED  
**Repository HEAD authority:** `77593c205851c97a1b0b46ebdb6ade270309f81a`  
**Routing authority:** `engav3d.routing.stage8.ticket1.v1 + amendment-1`  
**Request-wire authority:** Stage 8 Ticket 2A Amendment 1  
**Response-gap authority:** Stage 8 Ticket 2B / ENGAV3D-0026  
**Stage 7 live-response authority:** `ENGAV3D-0021-STAGE7-LIVE-CURRENT-PERCEPTION`  
**Provider executions authorized:** `0`

## 1. Purpose

This amendment adds exactly one successful response-result value combination:

```text
originating request = text_only
successful provider response
current perception was intentionally not requested
→ requested_state=not_requested
→ effective_state=not_requested
```

It closes the semantic gap proven by Ticket 2B without adding a response routing
tag, changing request correlation, changing either response key set, or rewriting
sealed Stage 7 bytes.

This is an offline response-wire contract only. The successful text-only fixture
is hypothetical contract analysis, not provider output or runtime evidence.

## 2. Composite authority

This amendment is read with, and does not rewrite:

```text
Stage 8 Ticket 1 + Amendment 1
→ originating request route

Stage 8 Ticket 2A Amendment 1
→ exact request-wire closed union

Stage 8 Ticket 2B
→ correlation sufficient; successful no-perception result missing

Stage 7 / 0021
→ sealed successful full-perception response bytes
```

## 3. Preserved response structure

The response top-level exact key set remains:

```text
request_id
client_request_id
narrative_response
action_type
state_changes
director_analysis
reasoning
entropy_impact
timestamp
provider_session_ref
perception_result
```

The `provider_session_ref` exact key set remains:

```text
companion_ref
provider
model
session_id
```

The `perception_result` exact key set remains:

```text
schema
requested_state
effective_state
capture_id
capture_event
capture_phase
captured_at
metadata_sha256
image_sha256
structured_snapshot_supplied
viewport_image_attached
failure_code
```

No key is added, removed, renamed, defaulted, or inferred.

The schema value remains:

```text
engain.runtime_perception_result.v1
```

## 4. Correlation and route authority

Every response remains correlated by both:

```text
request_id
client_request_id
```

Both values MUST exactly match the originating admitted request. Response order
alone is never sufficient.

The originating request owns route classification:

```text
sealed perception object + routing_mode absent
→ current_perception

perception absent + routing_mode=text_only
→ text_only
```

A response MUST NOT self-declare or override its route. No `routing_mode` field
is added to the response.

`not_requested/not_requested` is a result admissible only when both correlation
identities resolve to an admitted `text_only` request.

## 5. New successful text-only result branch

For an originating `text_only` request and a successful response, the exact
`perception_result` values are:

```text
schema=engain.runtime_perception_result.v1
requested_state=not_requested
effective_state=not_requested
capture_id=null
capture_event=null
capture_phase=null
captured_at=null
metadata_sha256=null
image_sha256=null
structured_snapshot_supplied=false
viewport_image_attached=false
failure_code=null
```

This means:

```text
current perception intentionally not requested
capture attempted=false
image attachment permitted=false
successful response=true
```

It does not mean capture failure, source unavailability, adapter rejection, or
provider failure.

## 6. Canonical successful text-only response fixture

Artifact:

```text
ENGAV3D-STAGE8-TICKET-2B-AMENDMENT-1-SUCCESSFUL-TEXT-ONLY-RESPONSE.json
SHA-256=63fb4d28cdf03c0f4f6f8c39bc29ce59005a9de42ffde0ed2a94fc0150738d2b
```

It correlates exactly to the admitted Ticket 2A request:

```text
request_id=req_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
client_request_id=dragon3d_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb_1
```

Its narrative is synthetic contract text. No provider produced it.

## 7. Semantic matrix

### A. Current perception / full

Originating request:

```text
current_perception
```

Result:

```text
requested_state=full
effective_state=full
capture_id=required
capture_event=message_received
capture_phase=pre_dispatch_player_view.v1
captured_at=required
metadata_sha256=required
image_sha256=required
structured_snapshot_supplied=true
viewport_image_attached=true
failure_code=null
```

Disposition:

```text
ACCEPT under the existing sealed Stage 7 branch
```

The exact 0021 response remains unchanged.

### B. Current perception / unavailable or rejected

Originating request:

```text
current_perception
```

Existing current-perception unavailable/rejection semantics remain unchanged.
They continue to mean perception was intended but could not produce an admitted
full result. They MUST NOT use `not_requested`.

For the existing rejected/no-result shape:

```text
requested_state=unavailable
effective_state=rejected
capture_id=null
capture_event=null
capture_phase=null
captured_at=null
metadata_sha256=null
image_sha256=null
structured_snapshot_supplied=false
viewport_image_attached=false
failure_code=existing failure code or null as existing authority permits
```

Disposition:

```text
ACCEPT only for a correlated current_perception request under existing rules
```

This amendment does not alter existing admitted `unavailable` result behavior
with capture correlation. It adds no new current-perception combination.

### C. Text only / successful

Originating request:

```text
text_only
```

Result:

```text
requested_state=not_requested
effective_state=not_requested
all capture/image identity=null
structured_snapshot_supplied=false
viewport_image_attached=false
failure_code=null
```

Disposition:

```text
ACCEPT under this amendment
```

## 8. Route-coupled closed matrix

```text
text_only request + not_requested/not_requested
→ ACCEPT

current_perception request + existing full/full
→ ACCEPT under unchanged Stage 7 authority

current_perception request + existing unavailable/rejected
→ ACCEPT under unchanged current-perception failure authority

current_perception request + not_requested/not_requested
→ REJECT

text_only request + full/full
→ REJECT

text_only request + unavailable/rejected
→ REJECT
```

A result-state pair is never authoritative without the correlated originating
request.

## 9. Fail-closed value matrix

The only admitted new state pair is:

```text
requested_state=not_requested
effective_state=not_requested
```

Reject:

```text
requested_state=not_requested + effective_state=full
requested_state=not_requested + effective_state=structured_only
requested_state=not_requested + effective_state=unavailable
requested_state=not_requested + effective_state=rejected

requested_state=full + effective_state=not_requested
requested_state=structured_only + effective_state=not_requested
requested_state=unavailable + effective_state=not_requested

unknown requested_state
unknown effective_state
```

Existing Stage 7 state combinations remain governed by existing Stage 7 rules;
this amendment does not broaden them.

## 10. Text-only capture and image prohibition

For `not_requested/not_requested`, all of these exact frozen result fields MUST
have these values:

```text
capture_id=null
capture_event=null
capture_phase=null
captured_at=null
metadata_sha256=null
image_sha256=null
structured_snapshot_supplied=false
viewport_image_attached=false
failure_code=null
```

Reject `not_requested/not_requested` when any of those values differs.

Because all response objects retain exact closed key sets, capture/image identity
MUST NOT be hidden at the response top level, inside `provider_session_ref`, or
under any added nested key. Unknown keys fail closed.

Reject specifically:

```text
not_requested + capture_id non-null
not_requested + capture_event non-null
not_requested + capture_phase non-null
not_requested + captured_at non-null
not_requested + metadata_sha256 non-null
not_requested + image_sha256 non-null
not_requested + structured_snapshot_supplied=true
not_requested + viewport_image_attached=true
not_requested + failure_code non-null
not_requested + hidden capture/image key elsewhere
```

## 11. Response routing tag prohibition

This amendment MUST NOT add:

```text
routing_mode=text_only
routing_mode=current_perception
```

to any response.

Reason:

```text
originating request owns route
response carries two exact correlation identities
```

The result describes whether perception was requested and what happened. It does
not classify its own route.

## 12. Sequential correlation

For one-at-a-time sequential requests under the future persistent-worker
lifecycle:

```text
request_id + client_request_id
→ exact originating request record
→ authoritative request route
→ route-coupled result validation
```

Responses MUST NOT be associated by arrival order alone. Queueing and parallel
requests remain unauthorized and undefined.

## 13. Preserved authorities

This amendment preserves byte-exact:

```text
Stage 7 / 0021 successful full response
SHA-256=5953bce251e8a8f684a175d5b43f13a82dcdf9d9c926f9aded127414472f35ad

Ticket 2A mandatory text-only request
SHA-256=5a5f856dcc157f885343c8d08bcfd9ebbf826a404bbab5fcf91c2a87fa69c4db
```

It also preserves:

- the existing response top-level exact key set;
- the existing `perception_result` exact key set;
- existing current-perception full validation;
- existing current-perception unavailable/rejected semantics;
- both response correlation identities;
- the absence of response `routing_mode`.

## 14. Canonical verifier requirements

The canonical verifier MUST independently prove:

```text
STAGE8_TICKET2B_AMENDMENT1_ADMITTED

TEXT_ONLY_SUCCESS_RESULT=REPRESENTABLE
TEXT_ONLY_REQUEST_CORRELATION=DETERMINISTIC
TEXT_ONLY_REQUESTED_STATE=not_requested
TEXT_ONLY_EFFECTIVE_STATE=not_requested
TEXT_ONLY_CAPTURE_ID=null
TEXT_ONLY_IMAGE_SHA256=null

CURRENT_PERCEPTION_FULL=UNCHANGED
CURRENT_PERCEPTION_UNAVAILABLE=UNCHANGED
STAGE7_0021_RESPONSE_BYTES=UNCHANGED

TEXT_ONLY_PLUS_FULL_RESULT=REJECTED
TEXT_ONLY_PLUS_UNAVAILABLE_RESULT=REJECTED
CURRENT_PERCEPTION_PLUS_NOT_REQUESTED=REJECTED
NOT_REQUESTED_PLUS_CAPTURE_ID=REJECTED
NOT_REQUESTED_PLUS_IMAGE=REJECTED
NOT_REQUESTED_MIXED_STATE=REJECTED
UNKNOWN_REQUESTED_STATE=REJECTED
UNKNOWN_EFFECTIVE_STATE=REJECTED
HIDDEN_CAPTURE_IMAGE_IDENTITY=REJECTED

RESPONSE_TOP_LEVEL_KEYS=UNCHANGED
PERCEPTION_RESULT_KEYS=UNCHANGED
RESPONSE_ROUTING_MODE=NOT_ADDED
PROVIDER_EXECUTIONS=0
RUNTIME_IMPLEMENTATION=NOT_AUTHORIZED
```

## 15. Non-goals

This amendment does not modify:

- `hermes_session_adapter.py`;
- `scripts/EngAInBridge3D.gd`;
- `scripts/ControlHUD.gd`;
- `scripts/PerceptionCapture3D.gd`;
- `scripts/DragonAvatar3D.gd`;
- runtime snapshots or imports.

It does not implement:

- response construction;
- response validation;
- text-only adapter dispatch;
- image suppression;
- persistent worker behavior;
- Godot routing;
- HUD lifecycle state;
- queues;
- parallel requests;
- retries;
- provider execution.

Ticket 2C remains unauthorized until this amendment is canonically admitted.

## 16. Unrelated workspace state

The following pre-existing state is outside this amendment and MUST remain
untouched:

```text
M scripts/DragonAvatar3D.gd
?? snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.json
?? snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png
?? snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png.import
```

No cleanup, absorption, staging, or interpretation of those files is authorized.

## 17. Final invariant

```text
looked and succeeded
→ current_perception + full/full + capture/image identity

intended to look but failed
→ current_perception + existing unavailable/rejected semantics

intentionally did not look and succeeded
→ text_only + not_requested/not_requested + null capture/image identity
```

The request remains route authority. The response remains correlated evidence.
Neither narrative text nor result state may self-authorize a route.
