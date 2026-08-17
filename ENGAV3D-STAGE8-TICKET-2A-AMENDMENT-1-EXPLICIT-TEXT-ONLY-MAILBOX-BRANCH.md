# ENGAV3D-STAGE8-TICKET-2A-AMENDMENT-1
# Explicit Text-Only Mailbox Branch

**Status:** FROZEN WIRE-CONTRACT AMENDMENT; RUNTIME IMPLEMENTATION NOT AUTHORIZED  
**Repository HEAD:** `77593c205851c97a1b0b46ebdb6ade270309f81a`  
**Provider executions authorized:** `0`

## 1. Purpose

This amendment resolves the canonical Ticket 2A RED by adding exactly one new
admitted request branch:

```text
text_only
```

It preserves the sealed Stage 7 current-perception request representation
unchanged.

This amendment defines request bytes and branch validation only. It does not
implement Godot routing, adapter dispatch, image suppression, a persistent
worker, provider execution, or response behavior.

## 2. Upstream authority

```text
Ticket 1:
8d569dac608f268405630b36816cb5d8514fd6d74dc784840c4110218f2a880a

Ticket 1 Amendment 1:
5bbc93fd4ed308f69722417be63f12b6db91e9012112776132b1baf394e0eeaf

Ticket 2A RED contract:
8c811933a9d9d6e882db7b9917e8b086a886d0423af7a0483ddd989a1a55d989

Ticket 2A canonical RED evidence:
ENGAV3D-0024-STAGE8-TICKET2A-TEXT-ONLY-MAILBOX-CONTRACT-RED
```

The RED proved that the existing single request variant cannot distinguish
intentional text-only absence from current-perception capture failure.

## 3. Unchanged top-level request envelope

Both admitted branches retain the exact top-level key set:

```text
additional_context
game_state
player_input
request_id
timestamp
```

No top-level `routing_mode`, perception, capture, snapshot, viewport, or image
field is admitted.

Existing request/client identity formats, player-input constraints, finite
timestamp requirement, game-state JSON safety, and `companion_ref=hermes_b`
remain upstream constraints.

## 4. Branch A — sealed Stage 7 current perception

The existing Stage 7 representation remains byte-compatible and unchanged.

Its `additional_context` exact key set remains:

```text
client_request_id
companion_ref
perception
```

It has no `routing_mode` key.

Within the Stage 7 producer/request scope frozen by this amendment, the
admitted requested perception states remain:

```text
full
unavailable
```

All existing Stage 7 validation remains authoritative, including:

- producer-owned capture identity;
- capture event and phase;
- capture timestamp;
- project and scene identity;
- snapshot and viewport exact key sets;
- persisted metadata/image correlation;
- full-image preparation and exact-image admission;
- unavailable capture/source failure semantics;
- no newest-image or replacement-image fallback.

Semantic branch selection:

```text
sealed perception object present
+
routing_mode absent
=> current_perception
```

This amendment does not add `routing_mode=current_perception` and does not
rewrite already-sealed Stage 7 request bytes.

## 5. Branch B — explicit text-only representation

The new text-only branch has this `additional_context` exact key set:

```text
client_request_id
companion_ref
routing_mode
```

Its exact discriminator value is:

```text
routing_mode=text_only
```

The `perception` key must be absent.

No capture identity or current-perception object is permitted.

Semantic branch selection:

```text
routing_mode=text_only
+
perception absent
=> text_only
```

## 6. Text-only forbidden fields

For the text-only branch, these field names are forbidden as object keys
anywhere in the request tree:

```text
perception
capture_id
captured_at
snapshot
viewport
image_path
image_sha256
```

They are forbidden whether their values are non-null, null, empty, stale, or
copied from another request.

A text-only request containing any current-perception representation is
rejected. A request containing both `routing_mode=text_only` and `perception`
is rejected before dispatch.

The forbidden-key scan applies to JSON object keys, not words inside
`player_input` text.

## 7. No new current-perception tag

This amendment does not admit:

```text
routing_mode=current_perception
```

Reason: Stage 7 current-perception bytes are already sealed and admitted.

The discriminator is introduced only to make intentional absence structurally
explicit:

```text
routing_mode absent + sealed perception object
=> current_perception

routing_mode=text_only + perception absent
=> text_only
```

Any other combination is rejected.

## 8. Fail-closed branch matrix

| perception | routing_mode | Result |
|---|---|---|
| present | absent | validate unchanged Stage 7 current-perception branch |
| absent | `text_only` | validate new text-only branch |
| absent | absent | reject |
| present | `text_only` | reject |
| absent or present | `current_perception` | reject |
| absent or present | any other value/type | reject |

No provider interpretation is involved in branch selection.

## 9. Three structurally distinct facts

### A. Intentional text-only

```text
routing_mode=text_only
perception absent
capture_attempted=false
```

### B. Current perception requested but unavailable

```text
routing_mode absent
perception.perception_state=unavailable
existing capture identity and failure semantics retained
```

### C. Current perception requested and full

```text
routing_mode absent
perception.perception_state=full
existing Stage 7 full evidence retained
```

A, B, and C are structurally distinguishable before provider dispatch.

## 10. Image-admission boundary

For `text_only`, future implementation must enforce:

```text
capture invocation count=0
prepare_image_dispatch invocation count=0
provider --image argument count=0
image path derivation from request=forbidden
```

The text-only exact branch contains no admitted image path or image hash from
which an image dispatch could be prepared.

For Stage 7 current perception, sealed image-admission behavior remains
unchanged.

This section is a future implementation obligation, not evidence that dispatch
code has been implemented by this amendment.

## 11. Mandatory fixture

Input:

```text
Without using any current image, describe what you remember about the previous
Dragon and the room/environment you saw before this latest scene.
```

Ticket 1 route:

```text
text_only
```

Frozen exact request artifact:

```text
ENGAV3D-STAGE8-TICKET-2A-AMENDMENT-1-MANDATORY-TEXT-ONLY-REQUEST.json
```

Artifact SHA-256:

```text
5a5f856dcc157f885343c8d08bcfd9ebbf826a404bbab5fcf91c2a87fa69c4db
```

The artifact is UTF-8 compact JSON with lexicographically ordered object keys
and one terminal LF byte. It has:

```text
routing_mode=text_only
perception absent
capture_id absent
captured_at absent
snapshot absent
viewport absent
image_path absent
image_sha256 absent
```

## 12. Stage 7 unchanged fixture

The canonical verifier must admit the exact sealed full request from:

```text
ENGAV3D-0021-STAGE7-LIVE-CURRENT-PERCEPTION/LIVE/request.json
```

without modifying its bytes. Its sealed SHA-256 is:

```text
5701b7d0d1e11c1e9307ccb54ad85752166ec7a6e51bb3017180c7c26da511b7
```

The verifier must also admit an exact unavailable Stage 7 branch with no
`routing_mode`, valid capture identity, null snapshot/image fields, and
existing capture-failure semantics.

## 13. Contract validator model

A contract validator evaluates `additional_context` as a closed tagged union:

```text
if exact keys are {client_request_id, companion_ref, perception}:
    require routing_mode absent
    validate sealed Stage 7 perception branch
    result=current_perception

else if exact keys are {client_request_id, companion_ref, routing_mode}:
    require routing_mode == text_only
    require all text-only forbidden keys absent from the request tree
    result=text_only

else:
    reject
```

The two exact key sets cannot overlap. Omission without a tag is invalid.
Presence of both tag and perception is invalid.

## 14. Admission assertions

Amendment admission requires one canonical provider-free verifier to prove:

```text
TEXT_ONLY_EXACT_JSON=CONSTRUCTIBLE
TEXT_ONLY_TAG=EXPLICIT
TEXT_ONLY_PERCEPTION=ABSENT
TEXT_ONLY_CAPTURE_ID=ABSENT
TEXT_ONLY_IMAGE_FIELDS=FORBIDDEN
TEXT_ONLY_AND_PERCEPTION=REJECTED
UNTAGGED_NO_PERCEPTION=REJECTED
UNKNOWN_ROUTING_MODE=REJECTED
STAGE7_FULL_FIXTURE=ACCEPTED_UNCHANGED
STAGE7_UNAVAILABLE_FIXTURE=ACCEPTED_UNCHANGED
INTENTIONAL_TEXT_ONLY_VS_CAPTURE_FAILURE=DISTINCT
PROVIDER_EXECUTIONS=0
RUNTIME_IMPLEMENTATION=NOT_AUTHORIZED
```

## 15. Non-goals

This amendment does not implement:

- persistent worker loop;
- Godot routing;
- HUD state;
- adapter request validation changes;
- adapter dispatch branching;
- capture suppression code;
- image suppression code;
- provider execution;
- memory behavior;
- worker restart;
- queueing;
- parallel requests;
- response-wire representation.

The response-side representation remains a later contract boundary.

## 16. Final authority

```text
One unchanged sealed Stage 7 current-perception branch.
One new explicit text-only request branch.
No current-perception routing tag.
No perception or capture/image field in text-only.
Every mixed, untagged, or unknown combination fails closed.
Provider executions remain zero.
Runtime implementation remains unauthorized.
```
