# ENGAV3D-STAGE8-TICKET-2A
# Text-Only Mailbox Representation Contract

**Status:** FROZEN RED CONTRACT GAP; RUNTIME IMPLEMENTATION NOT AUTHORIZED  
**Repository HEAD:** `77593c205851c97a1b0b46ebdb6ade270309f81a`  
**Routing authority:** `engav3d.routing.stage8.ticket1.v1 + amendment-1`  
**Provider executions authorized:** `0`

## 1. Purpose

Ticket 2A asks one wire-boundary question:

> What exact mailbox bytes honestly represent a `text_only` request without
> pretending that current perception exists?

This ticket evaluates the sealed Stage 7 request contract without production
modification. It does not implement a representation that the current schema
does not admit.

## 2. Mandatory fixture

Player input:

```text
Without using any current image, describe what you remember about the previous
Dragon and the room/environment you saw before this latest scene.
```

Frozen Ticket 1 routing result:

```text
route=text_only
capture_permitted=false
image_attachment_permitted=false
worker_remains_alive=true
```

## 3. Frozen source authority evaluated

```text
HEAD=77593c205851c97a1b0b46ebdb6ade270309f81a
hermes_session_adapter.py=f3add4a3011b09c9f88c489b436e4fc5e4751fd18ccb080810cac6ad06869e39
scripts/EngAInBridge3D.gd=64abb2a0770973cf8519449b918eb84fca6e87c2e5c298df5086c67a5ad18683
```

Upstream contract authority:

```text
Ticket 1=8d569dac608f268405630b36816cb5d8514fd6d74dc784840c4110218f2a880a
Ticket 1 Amendment 1=5bbc93fd4ed308f69722417be63f12b6db91e9012112776132b1baf394e0eeaf
```

## 4. Existing Stage 7 request key sets

The frozen request has exactly:

```text
player_input
game_state
additional_context
timestamp
request_id
```

The frozen `additional_context` has exactly:

```text
client_request_id
companion_ref
perception
```

The frozen `engain.runtime_perception.v1` object has exactly:

```text
schema
perception_state
capture_id
capture_event
capture_phase
captured_at
project_id
scene_path
snapshot
viewport
unavailable_reason
```

The frozen viewport object has exactly:

```text
availability
image_path
image_sha256
media_type
width
height
reason
```

Exact-key validation rejects omission and rejects unknown additions.

## 5. Existing perception states

The adapter admits only:

```text
full
structured_only
unavailable
```

It does not admit:

```text
text_only
not_requested
none
```

All three admitted states require a syntactically valid `capture_id`, capture
event, capture phase, and positive `captured_at`.

### 5.1 `full`

`full` means current capture was requested and admitted with available viewport
evidence. It may attach the exact sealed Stage 7 PNG after image admission.

### 5.2 `structured_only`

`structured_only` still means a capture event occurred. It requires capture
identity and structured snapshot evidence. It is not intentional absence of
perception.

### 5.3 `unavailable`

`unavailable` still requires:

```text
capture_id
capture_event=message_received
capture_phase=pre_dispatch_player_view.v1
captured_at
viewport.availability=unavailable
unavailable_reason from the capture/source failure reason set
viewport.reason matching unavailable_reason
```

The current unavailable reason set contains capture/source failures such as:

```text
capture_failed
cooldown_blocked
storage_unavailable
viewport_unavailable
image_write_failed
metadata_write_failed
```

`unavailable` therefore means perception was wanted but could not be supplied.
It does not mean perception was intentionally not requested.

## 6. Three states that must remain distinct

```text
A. text_only
   current image intentionally not requested
   capture_attempted=false

B. current_perception unavailable
   capture attempted or perception source invoked
   current evidence unavailable/failed

C. current_perception full
   capture attempted
   exact current evidence admitted
```

The pre-dispatch wire must distinguish A, B, and C structurally. Provider prose
must not supply the distinction.

## 7. Representation-question verdicts

### Question 1

Does a `text_only` request contain `additional_context.perception`?

Current Stage 7 answer:

```text
perception is mandatory for every admitted request
```

Ticket 2A answer:

```text
no honest text_only value is currently defined for that mandatory field
```

### Question 2

If perception is present, what exact representation means “no current
perception was requested”?

```text
NONE IN CURRENT CONTRACT
```

`unavailable` is not equivalent. `structured_only` is not equivalent. A new
string value is rejected.

### Question 3

If perception is omitted, is omission legal?

```text
NO
```

Omitting `perception` makes the exact `additional_context` key set invalid.
Setting it to `null` fails because perception must be an object.

### Question 4

Must a text-only request contain capture/snapshot/viewport/image fields?

There is no admitted text-only request. Every currently admitted perception
object must contain these keys:

```text
capture_id
captured_at
snapshot
viewport
```

Every viewport must contain these keys:

```text
image_path
image_sha256
```

For unavailable perception, snapshot and image values are null, but the
capture identity and failure semantics remain mandatory.

An honest future text-only representation must contractually forbid:

```text
capture_id
captured_at
snapshot
viewport
image_path
image_sha256
```

unless a future version places an explicit non-perception sentinel at another
wire level. Ticket 2A RED does not select that shape.

### Question 5

How does the adapter distinguish intentional text-only from capture failure?

```text
IT CANNOT UNDER THE CURRENT REQUEST CONTRACT
```

No routing discriminator exists. The only image-less admitted perception state
is still capture/source `unavailable` and requires capture identity plus a
failure reason.

### Question 6

How does the request structurally prevent accidental current-image attachment
on text-only?

```text
IT CANNOT, BECAUSE NO TEXT_ONLY REQUEST VARIANT EXISTS
```

The current full variant intentionally admits an image. The current schema has
no tagged text-only branch whose exact key set forbids perception/image fields.
A prompt instruction alone is not a structural control.

### Question 7

Does `routing_mode` belong in the wire, or is it derivable from a frozen field?

Current Stage 7 answer:

```text
routing_mode is absent
```

It cannot be derived honestly from `perception_state` because
`perception_state=unavailable` means capture/source failure, not deliberate
text-only routing.

Ticket 2A RED conclusion:

```text
AN EXPLICIT WIRE-LEVEL DISCRIMINATOR OR EQUIVALENT TAGGED REPRESENTATION IS REQUIRED
```

This RED ticket does not choose its key name, nesting location, or schema
version.

### Question 8

What exact key set is admitted for text-only?

```text
NONE IN CURRENT CONTRACT
```

No exact text-only JSON can be constructed without either omitting required
keys, adding an unknown discriminator, inventing a capture, or mislabeling
intentional absence as failure.

### Question 9

What exact key set remains admitted for current perception?

The sealed Stage 7 request, context, perception, snapshot, and viewport exact
key sets remain authoritative and unchanged. Both `full` and honest
`unavailable` current-perception forms remain valid under their existing
constraints.

### Question 10

Can text-only and current-perception coexist without changing sealed Stage 7
current-perception bytes?

```text
POSSIBLY, THROUGH A VERSIONED TAGGED UNION OR VERSIONED ENVELOPE
NOT POSSIBLE UNDER THE CURRENT SINGLE EXACT-KEY REQUEST VARIANT
```

A future amendment may preserve the existing Stage 7 current-perception branch
byte-for-byte while adding a separately tagged text-only branch. Ticket 2A RED
does not authorize or define that amendment.

## 8. Mandatory fixture construction verdict

An independent reader cannot construct admitted mailbox JSON for the mandatory
fixture under the current schema while preserving all Ticket 1 facts:

```text
route=text_only
capture_attempted=false
capture_id absent
image_attachment_permitted=false
current image structurally forbidden
capture failure structurally distinct
```

Any candidate fails at least one frozen boundary:

| Candidate | Current validator result | Contract violation |
|---|---|---|
| omit `additional_context.perception` | rejected | exact context keys differ |
| set `perception=null` | rejected | perception must be an object |
| set `perception_state=text_only` | rejected | state not admitted |
| add `routing_mode=text_only` | rejected | unknown exact-key addition |
| use `perception_state=unavailable` | may validate with capture identity/failure reason | collapses intentional absence into capture failure |
| synthesize `capture_id` | may satisfy syntax | falsely asserts capture lifecycle |
| attach an older/current image | may satisfy another route | violates no-current-image authority |

## 9. Fail-closed verdict

```text
STAGE8_TEXT_ONLY_MAILBOX_CONTRACT_GAP
```

The current mailbox schema cannot honestly represent state A without making it
look like state B or becoming malformed.

No runtime convention, provider prompt, synthetic identifier, stale image,
nullable-key trick, or overloaded failure state is admitted as a workaround.

## 10. Smallest follow-up boundary

A later separately authorized amendment should evaluate a wire-level tagged
representation that:

- explicitly identifies `text_only` before provider dispatch;
- gives text-only an exact closed key set;
- contractually forbids capture/image fields in that branch;
- preserves fresh request and client correlation;
- keeps intentional absence distinct from unavailable current perception;
- preserves the sealed Stage 7 current-perception representation as an admitted
  branch;
- gives the response side an equally honest correlated representation;
- remains provider-free through RED and offline GREEN.

Ticket 2A RED does not select the discriminator name or JSON shape.

## 11. Non-goals

Do not implement:

- persistent worker loop;
- worker process ownership;
- HUD thinking state;
- Godot routing code;
- adapter routing code;
- queueing;
- retries;
- provider calls;
- memory behavior;
- text-only dispatch;
- new request or response bytes.

## 12. Admission status

```text
Ticket 2A question:                         ANSWERED
Current honest text_only representation:    ABSENT
Current Stage 7 contract gap:               PROVEN
Mandatory text_only JSON:                   NOT CONSTRUCTIBLE
Stage 7 current_perception bytes:            UNCHANGED
Provider executions:                        0
Runtime implementation:                     NOT AUTHORIZED
Schema amendment:                           REQUIRED BUT NOT DEFINED HERE
```

Ticket 2A is a canonical RED boundary only after its independent verifier and
evidence bundle are admitted. It is not a GREEN mailbox representation.
