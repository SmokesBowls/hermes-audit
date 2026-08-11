# ENGAV3D-0001 Amendment 5
# Stage 7 Live Current-Perception Lifecycle

## 1. Purpose

Stage 6B proved:

Godot HUD
→ local mailbox
→ same frozen Hermes session
→ correlated response
→ existing Godot HUD.

The live request honestly used perception_state=unavailable.

Stage 7 adds current 3D viewport perception to that same proven mailbox path.

This amendment freezes identifier ownership, asynchronous capture sequencing,
HUD mutation timing, capture-failure behavior, and the live adapter's
nested-Dragon pre-dispatch identity proof.

It does not authorize a live provider call.

## 2. Frozen identity

Project:

godot_3d_avatar

Current scene:

res://scenes/Main.tscn

Nested Dragon presentation:

res://scenes/DragonAvatar3D.tscn

Hermes:

profile=default
companion_ref=hermes_b
provider=openai-codex
model=gpt-5.6-sol
session_id=20260731_065008_63a62d

## 3. Identifier ownership

### client_request_id

Owner:

3D submission lifecycle / EngAInBridge3D

Format:

^dragon3d_[0-9a-f]{32}_[1-9][0-9]*$

It must exist before current-perception capture begins.

The live capture producer must never generate, replace, infer, or derive the
client_request_id.

### request_id

Owner:

EngAInBridge3D

Format:

^req_[0-9a-f]{32}$

It belongs to the mailbox publication attempt.

The capture producer must never generate request_id for the live Stage 7 path.

### capture_id

Owner:

PerceptionCapture3D

Format:

^cap_[0-9a-f]{32}_[1-9][0-9]*$

EngAInBridge3D must never generate, replace, infer, or derive capture_id for
the live Stage 7 path.

All three identifiers remain distinct.

## 4. Stage 5A compatibility

The existing no-argument:

capture_once()

remains authorized solely as the historical Stage 5A harness.

Its accepted behavior and evidence must remain regression-compatible.

It is not the Stage 7 live submission API.

Stage 7 adds:

capture_for_submission(client_request_id: String) -> Dictionary

The live bridge must use capture_for_submission().

Stage 7 must not route the live mailbox through the standalone capture_once()
identity lifecycle.

## 5. Live capture API

capture_for_submission(client_request_id) shall:

1. validate the externally supplied client_request_id;
2. allocate one producer-owned capture_id before fallible capture work;
3. record the capture-attempt timestamp;
4. attempt one current viewport capture;
5. return one complete result object.

It must not generate:

- request_id;
- client_request_id.

## 6. Exact live capture-result shape

The producer returns exactly:

{
  "status": "full" | "unavailable",
  "client_request_id": "<exact supplied client_request_id>",
  "capture_id": "<producer-owned capture_id>",
  "captured_at": <finite timestamp>,
  "failure_code": null | "<producer-local failure code>",
  "perception": <complete frozen request perception object>
}

No unknown result keys are allowed.

For status=full:

failure_code = null

For status=unavailable:

failure_code is a non-empty producer-local diagnostic.

The bridge must not serialize failure_code into an unfrozen mailbox field.

## 7. Successful full capture

A successful live capture produces the already-frozen immutable PNG/JSON pair
under:

/mnt/data-drive/godot_engain_3d_avatar/snapshots

Wire-relative paths:

snapshots/perception_<capture_id>.json
snapshots/perception_<capture_id>.png

The complete request perception object has perception_state=full and remains
the exact frozen Stage 2 shape.

Required correlations include:

request.additional_context.client_request_id
==
metadata.client_request_id
==
capture-result.client_request_id

request.perception.capture_id
==
metadata.capture_id
==
capture-result.capture_id
==
metadata filename capture_id
==
image filename capture_id

request.perception.viewport
==
metadata.viewport

event, phase, project, scene, captured_at and all hashes/dimensions must remain
exactly correlated.

No newest-capture substitution is allowed.

## 8. Failed live capture

Known producer failures must still return a complete Stage 7 capture result.

The producer-owned capture_id and captured_at remain present.

No partially successful capture is relabeled as full.

The mailbox wire representation for all local current-capture failures is one
honest frozen unavailable perception envelope:

{
  "schema": "engain.runtime_perception.v1",
  "perception_state": "unavailable",
  "capture_id": "<producer-owned capture_id>",
  "capture_event": "message_received",
  "capture_phase": "pre_dispatch_player_view.v1",
  "captured_at": <capture attempt timestamp>,
  "project_id": "godot_3d_avatar",
  "scene_path": "res://scenes/Main.tscn",
  "snapshot": null,
  "viewport": {
    "availability": "unavailable",
    "image_path": null,
    "image_sha256": null,
    "media_type": null,
    "width": null,
    "height": null,
    "reason": "capture_failed"
  },
  "unavailable_reason": "capture_failed"
}

The detailed producer failure code remains local diagnostic evidence only.

Examples include, but are not limited to:

DRAGON_SCENE_UNAVAILABLE
CAPTURE_ROOT_REJECTED
PNG_DIMENSION_MISMATCH
FINAL_CORRELATION_FAILED

All map to the single frozen wire reason:

capture_failed

No new wire-level failure vocabulary is introduced.

## 9. Failed-capture publication rule

A normal capture failure does not abort the conversation.

If the producer returns a valid unavailable capture result:

EngAInBridge3D publishes exactly one correlated mailbox request containing
that unavailable perception envelope.

This preserves truthful conversational availability.

A producer contract violation, invalid result shape, invalid identifier, or
failure to produce a valid unavailable envelope fails locally:

- no mailbox publication;
- no provider execution;
- lifecycle released;
- HUD input remains available.

## 10. One-in-flight reservation

EngAInBridge3D must reserve the lifecycle before the first asynchronous capture
yield.

After accepting one non-empty submission:

1. confirm no active lifecycle;
2. confirm no blocking finalized request/response mailbox;
3. generate client_request_id;
4. set _busy=true;
5. set capture-pending state;
6. only then invoke/await capture_for_submission().

_busy therefore covers:

capture preparation
→ viewport capture
→ request publication
→ provider/response wait

until one of:

- valid correlated response;
- 180-second timeout;
- pre-publication local failure.

A second submission cannot enter while capture is awaiting frame boundaries.

## 11. No visible mutation before capture boundary

For an accepted submission, until capture_for_submission() has returned:

ControlHUD and EngAInBridge3D must not:

- clear the submitted input;
- disable the input;
- substitute placeholder text;
- append the accepted user message to the HUD;
- emit dragon_speaking(true);
- emit a capture-progress log line;
- otherwise deliberately mutate the visible player view.

The purpose is to ensure the captured viewport represents the player view at
message receipt before submission presentation changes it.

## 12. Repeated submit during capture

While capture-pending is true, repeated submit attempts are rejected without a
HUD-visible log mutation.

They:

- do not allocate another client_request_id;
- do not allocate another request_id;
- do not begin another capture;
- do not publish another mailbox request;
- do not emit MAILBOX_BUSY into the viewport before capture completes.

After the capture boundary has completed, normal bounded busy diagnostics may
resume.

## 13. Request timestamp

The bridge generates the mailbox request timestamp immediately after the
capture result returns and immediately before request construction/publication.

For full perception:

request.timestamp - captured_at

must remain within the already-frozen 0 through 5 second bound.

No stale capture may be published as current.

## 14. HUD commit acknowledgment

EngAInBridge3D adds:

signal submission_committed(
    client_request_id: String,
    submitted_text: String
)

This signal is emitted only after:

- the capture boundary has completed;
- one valid full or unavailable perception object exists;
- the exact mailbox request has been successfully published.

ControlHUD must not clear input before this signal.

On submission_committed:

ControlHUD clears the input only if the current input text still equals the
submitted_text associated with that commit.

If the user has edited the field meanwhile, the newer text remains untouched.

Button-triggered commands do not clear unrelated typed input.

## 15. Publication failure

If capture completed but mailbox publication fails:

- no submission_committed signal;
- input is not cleared by Stage 7;
- _busy is released;
- no provider execution occurs;
- a bounded local error may be displayed because the capture boundary has
  already completed.

A successfully persisted full capture pair remains immutable evidence even if
its mailbox publication later fails.

It is not automatically deleted or substituted.

## 16. Successful publication

After successful request publication:

- capture-pending becomes false;
- the existing accepted-user presentation may occur;
- submission_committed is emitted;
- dragon_speaking(true) may be emitted;
- _busy remains true while awaiting the response.

The existing Stage 6 response correlation and 180-second timeout lifecycle
remain authoritative.

## 17. Main.gd

Main.gd is not part of the Stage 7 live orchestration.

Its Stage 5A command-line capture harness remains unchanged.

The live bridge owns capture orchestration by creating/attaching or otherwise
using PerceptionCapture3D directly.

## 18. Live nested-Dragon identity proof

dragon_scene_path remains separate local preparation context and is not added
to the mailbox wire schema.

For every live mailbox request with:

perception_state=full

the adapter must, after loading the frozen project session and before any
provider execution, invoke the already-frozen Stage 5B preparation boundary:

prepare_image_dispatch(
    payload,
    dragon_scene_path=DRAGON_SCENE_PATH
)

where:

DRAGON_SCENE_PATH =
res://scenes/DragonAvatar3D.tscn

This invocation is provider-free.

It must succeed before client.chat/provider execution is authorized.

The returned preparation identity must agree with the active live request for:

request_id
client_request_id
capture_id
session_id
image_path
image_sha256

A mismatch or preparation rejection fails closed before provider execution.

No dragon_scene_path field is added to mailbox JSON.

Unavailable perception does not call the image-dispatch preparation boundary
because no current image exists.

## 19. Full-image provider path

For an accepted full live request:

the exact persisted image admitted by prepare_image_dispatch must be the image
supplied to the existing Hermes execution through --image.

No alternate capture, newest image, regenerated image, provider-generated
image, or manually substituted path is allowed.

## 20. Provider failure boundary

Stage 7 RED and offline GREEN consume zero provider executions.

No live Stage 7 provider request is authorized by this amendment.

## 21. Minimum Stage 7 production surface

Expected production files:

scripts/PerceptionCapture3D.gd
scripts/EngAInBridge3D.gd
scripts/ControlHUD.gd
hermes_session_adapter.py

Main.gd remains unchanged unless an independently demonstrated contract
conflict requires a later amendment.

## 22. Stage 7 RED gate

Tests must be written before Stage 7 production implementation.

RED must prove the current baseline lacks:

- externally bound live client_request_id capture;
- producer-exclusive live capture_id ownership;
- pre-await one-in-flight reservation;
- no-visible-mutation capture boundary;
- submission_committed acknowledgment;
- full/unavailable live perception construction;
- capture-failure unavailable publication;
- full live prepare_image_dispatch nested-Dragon proof.

Earlier protected tests must not be modified to manufacture Stage 7 GREEN.

Stage 7 provider executions:
0
