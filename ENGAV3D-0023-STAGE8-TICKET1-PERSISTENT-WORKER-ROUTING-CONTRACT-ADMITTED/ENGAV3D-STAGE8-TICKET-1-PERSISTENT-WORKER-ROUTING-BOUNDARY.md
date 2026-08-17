# ENGAV3D-STAGE8-TICKET-1
# Persistent Hermes Worker + Routing Boundary

**Status:** FROZEN CONTRACT; RUNTIME IMPLEMENTATION NOT AUTHORIZED  
**Repository:** `/mnt/data-drive/godot_engain_3d_avatar`  
**Repository authority at contract freeze:** `77593c205851c97a1b0b46ebdb6ade270309f81a`  
**Contract location:** `/mnt/data-drive/engain-avatar-audit`  
**Provider executions authorized by this ticket:** `0`

## 1. Purpose

This ticket freezes, without runtime wiring:

1. the lifecycle and ownership boundary of one persistent Hermes mailbox worker;
2. the deterministic pre-publication routing boundary between `text_only` and
   `current_perception`;
3. request identity, correlation, replay, and sequential-processing invariants;
4. the route-specific HUD lifecycle states future implementation must expose;
5. the exact schema gap that blocks honest `text_only` implementation under the
   current frozen mailbox contracts.

This document is an architecture contract, not an implementation plan and not
runtime authorization.

## 2. Normative upstream authority

This contract is downstream of, and does not weaken:

- `ENGAV3D-0001-IDENTITY-MAILBOX-PERCEPTION-FREEZE.md`;
- `ENGAV3D-0001-AMENDMENT-5-STAGE7-LIVE-PERCEPTION-LIFECYCLE.md`;
- sealed Stage 7 production HEAD
  `77593c205851c97a1b0b46ebdb6ade270309f81a`;
- sealed live proof
  `ENGAV3D-0021-STAGE7-LIVE-CURRENT-PERCEPTION`;
- the frozen request, response, perception, snapshot, and perception-result
  contracts already named by those authorities.

Stage 7 proves exact current-image capture and one-shot dispatch. Stage 8 may
reuse that proof but may not reinterpret it as persistent-worker proof.

## 3. Non-goals and forbidden work

Ticket 1 does not authorize:

- persistent subprocess management;
- adapter-loop implementation;
- Godot worker spawning or shutdown wiring;
- changes to any Godot script, scene, addon, HUD, or project setting;
- changes to `hermes_session_adapter.py`;
- provider execution;
- automatic restart;
- retries;
- queueing;
- parallel request processing;
- new memory semantics;
- a new perception producer;
- a new mailbox schema;
- use of a synthetic capture to disguise a text-only request;
- use of an unavailable perception envelope to disguise routing intent;
- implementation against an unresolved schema gap.

## 4. Frozen worker identity

The sole authoritative persistent worker for this project serves exactly:

```text
profile=default
companion_ref=hermes_b
provider=openai-codex
model=gpt-5.6-sol
session_id=20260731_065008_63a62d
```

The worker must resume that exact session. It must not create, accept, or
persist a replacement conversational identity.

Shared conversational identity does not merge project-local mailbox ownership
or replay ledgers with another host.

## 5. Authority and ownership

| Concern | Sole owner | Must not be owned by |
|---|---|---|
| frozen Hermes identity | sealed session state + worker validation | HUD text, provider prose, routing result |
| project mailbox lease | one authoritative persistent worker | a second worker, a request, the provider |
| routing policy | frozen local routing policy | provider interpretation after dispatch |
| `client_request_id` | admitted HUD submission lifecycle | capture producer, worker inference |
| `request_id` | mailbox publication lifecycle | capture producer, provider |
| `capture_id` | Stage 7 perception producer, current-perception only | text-only route, worker, HUD |
| request/response correlation | local bridge + worker validation | provider prose |
| processed-request ledger | authoritative project worker state | HUD, provider, prior response payload |
| viewport evidence | sealed Stage 7 producer/admission path | router, worker fallback search, provider |
| temporary HUD status | request lifecycle feedback | provider content |

The provider never owns routing mode, correlation identifiers, mailbox
ownership, retry permission, worker lifetime, or HUD lifecycle state.

## 6. Persistent worker lifecycle

### 6.1 Worker states

The implementation must expose behavior equivalent to this state machine:

```text
STOPPED
  -> STARTING
  -> READY
  -> ACTIVE_REQUEST
  -> READY
  -> ... zero or more later ACTIVE_REQUEST cycles ...
  -> STOPPING
  -> STOPPED

STARTING or READY or ACTIVE_REQUEST
  -> INTEGRITY_FAILED
  -> STOPPED
```

`ACTIVE_REQUEST -> READY` occurs after each terminal request outcome that does
not prove an unrecoverable worker integrity failure.

Successful processing of one request must not transition the worker to
`STOPPED`.

### 6.2 Authorized start and stop conditions

The worker may start with the Dragon runtime. It remains alive until exactly
one of:

- explicit runtime shutdown;
- explicit worker shutdown;
- unrecoverable local integrity failure.

Examples of unrecoverable integrity failure include inability to prove the
frozen identity, invalid or unsafe authoritative ledger state, loss of the
exclusive mailbox ownership guarantee, or corruption that makes subsequent
request correlation untrustworthy.

Ordinary request rejection, capture unavailability, publication failure,
provider failure, provider timeout, malformed provider output, or one bad
request is a terminal request outcome. None implicitly authorizes a second
worker or automatically terminates/replaces the authoritative worker.

### 6.3 Exclusive ownership

At most one authoritative worker may own the project mailbox at a time.

A later implementation must define and prove one exclusive project-local
ownership mechanism before entering `READY`. Ticket 1 does not choose the
filesystem lock, PID/lease representation, or process-supervision mechanism.

Failure to acquire exclusive ownership means the candidate process is not the
worker. It must not claim requests or invoke the provider.

No request failure creates permission to launch another worker.

## 7. Sequential request processing

Ticket 1 authorizes a sequential model only:

```text
READY
-> admit one request
-> ACTIVE_REQUEST
-> terminal request outcome
-> READY
-> admit a later request
```

Queueing and parallel processing are outside this ticket.

A submission attempted while a request is active is not queued. Future wiring
must retain one-in-flight/bounded-busy behavior unless a later contract amends
it. A non-admitted attempt does not receive lifecycle IDs.

Each admitted non-empty HUD submission receives fresh:

```text
client_request_id
request_id
```

An admitted `current_perception` submission additionally receives exactly one
fresh producer-owned:

```text
capture_id
```

An admitted `text_only` submission receives no `capture_id`.

A completed request must not prevent a later independent request. A prior
request must not supply the later request's IDs, response, routing mode,
perception, failure state, temporary HUD status, or provider receipt.

## 8. Correlation and replay invariants

For every admitted request, the worker must preserve:

- exact `request_id` correlation;
- exact `client_request_id` correlation;
- the frozen profile/companion/provider/model/session tuple;
- exactly-once processed-request ledger behavior;
- interrupted-attempt replay protection;
- no response inheritance across request boundaries.

The worker must reject or safely disposition malformed, duplicate, stale, or
mismatched responses without assigning them to a later request.

Completing request A adds only request A to the processed ledger. It must not
block fresh request B merely because A completed.

Restart behavior, retry policy, and ledger compaction are not defined by this
ticket.

## 9. Routing mode

Every admitted HUD message is assigned exactly one local mode before request
publication:

```text
text_only
current_perception
```

The routing decision is not provider content. It must be completed before
mailbox publication and before any provider invocation.

The provider may answer within the selected route but may not reinterpret,
upgrade, downgrade, or retry the route.

## 10. Frozen routing-policy normalization

Routing policy version:

```text
engav3d.routing.stage8.ticket1.v1
```

The classifier operates on the submitted message after the existing non-empty
trim check. For classification only, it derives a comparison form by:

1. Unicode NFKC normalization;
2. Unicode case folding;
3. replacing punctuation with spaces except apostrophes inside words;
4. collapsing consecutive whitespace to one ASCII space;
5. trimming leading and trailing whitespace.

The original submitted text remains the provider input. The comparison form is
routing evidence only.

A future implementation must use one deterministic implementation of this
normalization. Cross-runtime disagreement fails local routing admission; it
must not be resolved by asking the provider.

## 11. Closed routing predicates

The following ordered predicates are normative. The first matching rule wins.
If no current-view predicate matches, the route is `text_only`.

### Rule 1: explicit current-view phrase

Route `current_perception` when the normalized message contains a complete
word-boundary phrase from this closed set:

```text
what do you see
what can you see
what is visible
currently visible
current viewport
current view
current screen
current frame
current scene
current room
right now
in front of me
left side of the screen
right side of the screen
left side of the frame
right side of the frame
look at this
look here
look around
```

Exception: `what do you see` and `what can you see` route `text_only` when the
same message explicitly scopes the object to history using one of:

```text
in your memory
from memory
in the previous scene
in the prior scene
in the earlier scene
last time
previously
```

unless another explicit current-view phrase from the closed set also appears.

### Rule 2: anchored visual/deictic intent

Route `current_perception` when the normalized message contains at least one
anchor and at least one visual/spatial term.

Closed anchor set:

```text
this
these
here
currently
right now
at the moment
in front of me
on the screen
in the frame
in the viewport
```

Closed visual/spatial term set:

```text
see
look
visible
view
screen
frame
viewport
scene
room
object
dragon
color
colour
where
location
left
right
front
behind
above
below
near
far
different
compare
```

This rule makes a current/history comparison `current_perception` because the
current side of the comparison requires new evidence.

### Rule 3: default and history/conversation intent

All other admitted messages route `text_only`.

The following terms reinforce `text_only` but do not override a Rule 1 or Rule
2 match:

```text
remember
memory
previous
prior
earlier
before
last time
we discussed
we talked about
plan
reason
think
```

Unknown, novel, or ambiguous wording defaults to `text_only`. It must not cause
a speculative capture. Expanding the closed phrase/anchor/visual tables
requires a versioned contract amendment and deterministic tests.

## 12. Normative routing examples

| Message | Route | Capture allowed | Image allowed | Reason |
|---|---|---:|---:|---|
| `What do you see?` | `current_perception` | yes | yes, after Stage 7 admission | Rule 1 |
| `Where is the Dragon right now?` | `current_perception` | yes | yes, after Stage 7 admission | Rule 1/2 |
| `What color is the object in front of me?` | `current_perception` | yes | yes, after Stage 7 admission | Rule 1/2 |
| `What is on the left side of the screen?` | `current_perception` | yes | yes, after Stage 7 admission | Rule 1 |
| `Describe the current room.` | `current_perception` | yes | yes, after Stage 7 admission | Rule 1 |
| `What do you remember about the previous Dragon and room?` | `text_only` | no | no | Rule 3 |
| `How is this Dragon different from the one you remember?` | `current_perception` | yes | yes, after Stage 7 admission | Rule 2; current/history comparison |
| `What did we discuss earlier?` | `text_only` | no | no | Rule 3 |
| `Help me plan the next ticket.` | `text_only` | no | no | Rule 3 |
| `What did you see in the previous scene?` | `text_only` | no | no | history-scoped, no current anchor |
| `Explain this plan.` | `text_only` | no | no | `this` without a closed visual/spatial term |
| `Do you remember this Dragon on the screen?` | `current_perception` | yes | yes, after Stage 7 admission | Rule 2; explicit current reference wins |

These examples do not extend the closed tables. The ordered predicates remain
the authority.

## 13. Text-only route contract

For `text_only`:

- no viewport capture is permitted;
- no capture coroutine is invoked;
- no `capture_id` is allocated;
- no new PNG or metadata snapshot is produced;
- no current or previous image is attached;
- no newest-image, cached-image, prior-capture, or fallback-image search occurs;
- the frozen Hermes session remains available as conversational history;
- the provider receives only the admitted text/context authorized by the
  eventual text-only wire contract;
- absence of a current image is intentional routing, not `capture_failed`.

`text_only` must not be represented as failed perception merely to satisfy the
current schema.

## 14. Current-perception route contract

For `current_perception`:

- allocate one fresh producer-owned `capture_id`;
- use the sealed Stage 7 capture producer and capture ordering;
- preserve Stage 7 request/client/capture correlation;
- use the exact persisted PNG and metadata pair for that request;
- run the sealed provider-free image preparation/admission boundary;
- attach exactly the image admitted by that boundary;
- prohibit newest-image, alternate-image, regenerated-image, and retry
  substitution;
- preserve the Stage 7 unavailable-perception behavior where applicable.

A valid Stage 7 unavailable capture result remains an honest normal request
under the existing Stage 7 authority. It does not become a text-only request.
An invalid capture-result contract is a local terminal request failure.

## 15. Thinking-state contract

Temporary status is local lifecycle feedback. It is not provider prose and is
not added to provider history.

### 15.1 Text-only

```text
submission admitted
-> Dragon is thinking...
-> correlated response OR explicit terminal failure
-> temporary status absent
```

### 15.2 Current perception: full path

```text
submission admitted
-> Dragon is looking...
-> Stage 7 capture and exact-image admission complete
-> Dragon is thinking...
-> correlated response OR explicit terminal failure
-> temporary status absent
```

### 15.3 Current perception: valid unavailable result

Stage 7 remains authoritative. A producer-valid unavailable capture result may
publish one honest unavailable-perception request:

```text
submission admitted
-> Dragon is looking...
-> capture boundary returns valid unavailable perception
-> Dragon is thinking...
-> correlated response OR explicit terminal failure
-> temporary status absent
```

No image is admitted or attached on that path.

### 15.4 Terminal status clearing

Temporary status must be cleared on:

- successful correlated response;
- invalid capture-result failure;
- publication failure;
- image-preparation/admission failure;
- adapter/provider failure;
- timeout;
- explicit worker shutdown;
- runtime shutdown;
- unrecoverable integrity shutdown.

A temporary status must not survive a terminal request state or be inherited by
the next request.

## 16. Deterministic admission answers

For any proposed HUD message, an independent reader applies Sections 10–12 and
can answer:

1. **Route:** first matching routing predicate, otherwise `text_only`.
2. **Capture allowed:** only for `current_perception`.
3. **Image allowed:** only for a `current_perception` request after exact Stage 7
   image admission; never for `text_only` or unavailable perception.
4. **Worker owner:** the one persistent worker holding exclusive project mailbox
   authority and the frozen Hermes identity.
5. **HUD state:** `thinking` for text-only; `looking` then `thinking` for
   current-perception; absent after any terminal outcome.
6. **Worker lifetime:** returns to `READY` after ordinary terminal request
   outcomes; stops only under Section 6.2.

No provider interpretation is needed to answer any of the six questions.

## 17. Blocking wire-contract gap

Ticket 1 identifies a real contract gap and does not invent around it.

The frozen mailbox request requires an exact `additional_context.perception`
object. The frozen perception schema requires:

```text
capture_id
capture_event
capture_phase
captured_at
perception_state
snapshot
viewport
```

The frozen response requires `perception_result`, and the existing Godot
correlation path expects an active capture identity for normal non-rejected
perception results.

But this Stage 8 contract requires `text_only` to have:

```text
no capture
no capture_id
no current snapshot
no current image
intentional text-only routing, not capture failure
```

Therefore the current frozen mailbox request/response schemas cannot represent
an honest `text_only` request without violating at least one authority:

- generating a fake capture ID;
- mislabeling intentional text-only routing as unavailable/capture failure;
- attaching stale structured/image evidence;
- omitting required frozen fields;
- silently changing a frozen schema.

All are forbidden.

### 17.1 Required follow-up authority

Before runtime implementation, a separately authorized schema-boundary ticket
must define and freeze the honest text-only request and correlated response
representation. It must decide, with tests, whether to version the mailbox
schema or introduce another explicitly versioned envelope.

That follow-up must preserve:

- exact request/client correlation;
- frozen session continuity;
- no capture ID on text-only;
- no image attachment;
- no false failure reason;
- processed-request ledger behavior;
- strict closed-world validation;
- existing Stage 7 current-perception compatibility.

Ticket 1 does not choose the new field names, shapes, or schema version.

### 17.2 Implementation gate

Persistent worker and routing implementation is blocked until the text-only
wire gap is resolved by explicit authority.

The routing policy itself is frozen and may be used to design RED tests, but no
runtime may publish `text_only` using an invented placeholder envelope.

## 18. Red-line rules

Future implementation must fail closed if:

- the frozen Hermes identity cannot be resumed exactly;
- a second authoritative mailbox worker exists or ownership is ambiguous;
- routing produces zero or more than one mode;
- provider interpretation is required to select the mode;
- a text-only route allocates a capture ID, captures, or attaches an image;
- a current-perception route bypasses Stage 7 capture/admission;
- one request inherits another request's IDs, response, perception, status, or
  replay state;
- a terminal request leaves the HUD status indefinitely active;
- a request failure launches or authorizes a second worker;
- implementation begins before the wire-contract gap is resolved.

## 19. Ticket 1 admission verdict

The lifecycle, routing decision, capture permission, image permission, worker
ownership, HUD status, and worker termination rules are defined without runtime
invention.

```text
persistent worker lifecycle contract: FROZEN
routing policy v1:                    FROZEN
text-only/current-perception choice:  DETERMINISTIC
provider execution:                   0 AUTHORIZED
runtime wiring:                       NOT AUTHORIZED
text-only wire representation:        BLOCKED ON FOLLOW-UP SCHEMA AUTHORITY
```

## 20. Final invariant

```text
One frozen Dragon identity.
One authoritative project worker.
One independently correlated request at a time.
One deterministic route before publication.
No capture and no image for text-only conversation.
Exact sealed Stage 7 evidence for current perception.
The worker survives ordinary request completion and failure.
No invented wire representation crosses the unresolved text-only boundary.
```
