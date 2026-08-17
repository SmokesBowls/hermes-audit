# ENGAV3D-STAGE8-TICKET-2B
# Text-Only Response-Wire Compatibility Contract

**Status:** FROZEN RESPONSE-WIRE CONTRACT GAP; RUNTIME IMPLEMENTATION NOT AUTHORIZED  
**Repository HEAD authority:** `77593c205851c97a1b0b46ebdb6ade270309f81a`  
**Routing authority:** `engav3d.routing.stage8.ticket1.v1 + amendment-1`  
**Request-wire authority:** Stage 8 Ticket 2A Amendment 1  
**Stage 7 live-response authority:** `ENGAV3D-0021-STAGE7-LIVE-CURRENT-PERCEPTION`  
**Provider executions authorized:** `0`

## 1. Purpose

Ticket 2B determines whether the exact sealed Stage 7 response representation
can carry responses to both:

```text
A. current_perception request
B. text_only request
```

without changing Stage 7 response bytes or inventing unnecessary routing
fields.

This is offline contract analysis. No fixture in this ticket is a provider
response or runtime execution.

## 2. Base authorities

```text
HEAD=77593c205851c97a1b0b46ebdb6ade270309f81a
hermes_session_adapter.py=f3add4a3011b09c9f88c489b436e4fc5e4751fd18ccb080810cac6ad06869e39
scripts/EngAInBridge3D.gd=64abb2a0770973cf8519449b918eb84fca6e87c2e5c298df5086c67a5ad18683
```

Request-wire authority:

```text
Ticket 2A Amendment 1:
01b14eb7eb0c0c693fc63f590e01748bab645e16cce4a36e13dcd476a0c94f03

Mandatory text-only request:
5a5f856dcc157f885343c8d08bcfd9ebbf826a404bbab5fcf91c2a87fa69c4db
```

Stage 7 response fixture authority:

```text
ENGAV3D-0021-STAGE7-LIVE-CURRENT-PERCEPTION/LIVE/response-observed.json
SHA-256=5953bce251e8a8f684a175d5b43f13a82dcdf9d9c926f9aded127414472f35ad
```

## 3. Mandatory fixtures

### Fixture A — exact sealed Stage 7 response

The exact successful response bytes from 0021 are preserved unchanged.

### Fixture B — admitted text-only request

The exact Ticket 2A Amendment 1 request is preserved unchanged:

```text
routing_mode=text_only
perception absent
request_id=req_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
client_request_id=dragon3d_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb_1
```

### Fixture C — existing-schema hypothetical response

Fixture C uses only the existing Stage 7 response key sets and correlates to
Fixture B. It is contract analysis only and did not come from a provider.

Fixture C authority:

```text
ENGAV3D-STAGE8-TICKET-2B-FIXTURE-C-EXISTING-SCHEMA-TEXT-RESPONSE.json
SHA-256=a85c9dad2078fda1637b4972516349bbb3892482876d3c6c3e096d7f97a26588
```

It uses the only existing bridge-admitted no-capture shape:

```text
perception_result.requested_state=unavailable
perception_result.effective_state=rejected
capture_id=null
capture_event=null
capture_phase=null
captured_at=null
metadata_sha256=null
image_sha256=null
structured_snapshot_supplied=false
viewport_image_attached=false
```

That shape is syntactically admitted because the bridge returns true early for
`effective_state=rejected`. It is not an honest successful text-only perception
result.

## 4. Exact admitted Stage 7 response key set

The exact top-level response keys are:

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

The exact provider-session keys are:

```text
companion_ref
provider
model
session_id
```

The exact perception-result keys are:

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

## 5. Correlation identity

The response contains both:

```text
request_id
client_request_id
```

The Godot bridge requires exact equality with both active request identities.
The adapter copies both directly from the validated originating request into
success and correlated error responses.

Response ordering is not the sole correlation mechanism.

The provider-session tuple independently freezes:

```text
companion_ref=hermes_b
provider=openai-codex
model=gpt-5.6-sol
session_id=20260731_065008_63a62d
```

## 6. Perception-specific response fields

The response is not route-neutral. `perception_result` is mandatory.

The response contains these perception-specific keys:

```text
capture_id
captured_at
image_sha256
requested_state
effective_state
```

It does not contain:

```text
image_path
perception_state
routing_mode
```

The absence of `routing_mode` is not the compatibility problem. The mandatory
perception-result semantics are.

## 7. Existing result-state semantics

The bridge admits `requested_state` only from:

```text
full
structured_only
unavailable
```

It admits `effective_state` only from:

```text
full
structured_only
unavailable
rejected
```

For every non-rejected result, the bridge requires:

```text
capture_id == active_capture_id
capture_event == message_received
capture_phase == pre_dispatch_player_view.v1
```

A text-only request has no capture identity by contract. Therefore a successful
non-rejected text-only response cannot satisfy the current validator.

For a rejected result, the bridge bypasses capture correlation. The adapter's
no-perception provenance shape sets:

```text
requested_state=unavailable
effective_state=rejected
capture fields=null
```

That is an adapter rejection/failure representation. It cannot honestly mean a
successful text-only response in which current perception was intentionally
not requested.

## 8. Question verdicts

### Question 1

Exact Stage 7 response key set:

```text
DEFINED IN SECTION 4; 11 TOP-LEVEL KEYS
```

### Question 2

Response/request correlation fields:

```text
request_id
client_request_id
```

### Question 3

Is `client_request_id` represented?

```text
YES; BOTH request_id AND client_request_id ARE REQUIRED
```

### Question 4

Does the response contain perception-specific state?

```text
YES; perception_result IS MANDATORY
```

### Question 5

Presence matrix:

```text
capture_id:       present as a mandatory perception_result key
image_path:       absent
image_sha256:     present as a mandatory perception_result key
perception_state: absent; requested_state/effective_state are present instead
routing_mode:     absent
```

### Question 6

Can the exact existing schema represent both route responses without ambiguity?

```text
current_perception: YES
successful text_only: NO
```

The no-capture existing shape says `unavailable/rejected`; it does not say
intentional text-only success.

### Question 7

Does the response need to repeat `routing_mode`?

```text
NO FOR CORRELATION
```

Adding routing mode merely for symmetry is not authorized. Correlation can
recover the originating request branch.

### Question 8

Can routing remain a property of the originating request?

```text
YES
```

A future response validator can resolve request route from the exact correlated
request record. It need not infer route from narrative text or provider output.

### Question 9

Can sequential responses be associated deterministically?

```text
THE WIRE IDENTITIES ARE SUFFICIENT FOR SEQUENTIAL CORRELATION
```

Both IDs are explicit. A future persistent worker must retain the originating
request record until terminal response disposition and must not rely on arrival
order alone. Queueing and parallel processing remain out of scope.

The current Godot implementation keeps only one active request/client/capture
triple. That supports one-at-a-time correlation but is not itself persistent
worker proof.

### Question 10

Does this analysis mutate the sealed 0021 response?

```text
NO
```

Fixture A remains byte-identical with SHA-256
`5953bce251e8a8f684a175d5b43f13a82dcdf9d9c926f9aded127414472f35ad`.

## 9. Compatibility verdict

The preferred unchanged-schema outcome is not admissible.

Correlation is sufficient and route-neutral. Response provenance semantics are
not.

```text
STAGE8_TEXT_ONLY_RESPONSE_WIRE_CONTRACT_GAP
```

Exact missing semantic representation:

> The sealed response has no successful `text_only` / perception-not-requested
> result branch. Every non-rejected result requires capture correlation, while
> the only no-capture branch is `unavailable/rejected` adapter failure.

No response routing tag is required to fix correlation. No field is invented by
this gap analysis.

## 10. Fail-closed findings

Rejected contract proposals include:

- placing a non-null `capture_id` in a text-only response;
- placing image identity in a text-only response;
- treating `unavailable/rejected` as successful text-only;
- adding `routing_mode=current_perception` to sealed Stage 7 bytes;
- inferring route from narrative response content;
- asking the provider to recover correlation;
- using response order as the only identity;
- rewriting Fixture A;
- omitting mandatory `perception_result` under the current exact schema;
- using a non-rejected result with null capture identity.

## 11. Smallest follow-up boundary

A separately authorized response-wire amendment must define an honest
successful text-only result while preserving:

- the exact Stage 7 response branch unchanged;
- both request and client correlation IDs;
- no capture or image identity for text-only;
- request-owned routing without a redundant response routing tag, unless a
  later proof shows one is necessary;
- structural distinction between text-only success, current-perception
  unavailable, current-perception full, and adapter rejection;
- exact-key closed validation;
- provider execution count zero through contract RED/GREEN.

Ticket 2B does not choose the result tag, field names, nullability, or schema
version.

## 12. Non-goals

This ticket does not modify:

- `hermes_session_adapter.py`;
- `scripts/EngAInBridge3D.gd`;
- `scripts/ControlHUD.gd`;
- `scripts/PerceptionCapture3D.gd`.

It does not implement:

- persistent worker behavior;
- text-only adapter dispatch;
- response construction changes;
- image suppression;
- HUD lifecycle state;
- routing code;
- queues;
- retries;
- provider execution.

## 13. Final status

```text
Response correlation:                         SUFFICIENT
Response route tag:                           NOT REQUIRED FOR CORRELATION
Stage 7 current-perception response:           VALID AND UNCHANGED
Successful text-only response:                 NOT HONESTLY REPRESENTABLE
Missing boundary:                              SUCCESSFUL NO-PERCEPTION RESULT BRANCH
STAGE8_TEXT_ONLY_RESPONSE_WIRE_CONTRACT_GAP:   PROVEN
Provider executions:                          0
Runtime implementation:                       NOT AUTHORIZED
```
