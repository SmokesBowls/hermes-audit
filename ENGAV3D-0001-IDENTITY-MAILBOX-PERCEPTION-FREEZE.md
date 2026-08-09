# ENGAV3D-0001 — Identity, Mailbox, and Runtime-Perception Freeze

**Status:** FROZEN BEFORE ADAPTER IMPLEMENTATION  
**Project:** `/mnt/data-drive/godot_engain_3d_avatar`  
**Purpose:** Freeze the 3D host identity and the exact first-parity communication/perception boundary before any 3D Hermes adapter source is written.

## 1. Evidence lineage

### 1.1 Current 3D baseline

```text
repository: /mnt/data-drive/godot_engain_3d_avatar
branch: main
HEAD: 5d2a46533f4b52cfed9a03a2169638bd0f93f6f9
tree: 0c70d0497e18c600f46e85f341b65b00034ed542
working tree at freeze discovery: clean
project.godot sha256: c10e68a11398e9166a38f379cc3b04c50c9aed9c1a93b18b7fdffeb5336a476d
scenes/Main.tscn sha256: 1fb879ea1bb88a8732c27a1f62586d649c38d9db5340fdcba2487713e8f42271
scenes/DragonAvatar3D.tscn sha256: ee718766810c76411caeb963aa9be153272a57ef9a01630125a73a1b9ec84b49
```

### 1.2 Accepted 2D donor proof

```text
repository: /mnt/data-drive/engain_avatar
HEAD at freeze discovery: ad4dc1ff0861f132dd8af49404d6713f742eb3a1
tree at freeze discovery: 51cc5049677b2be9de07658b4a589e50f57a3292
accepted lock: ENGAV-0002-EMBODIMENT-SESSION-LOCK.md
accepted lock sha256: d17da33b4949c076ba937e0dcd0dee09e819879d5f34beedc84f30532d6b867f
reference adapter sha256: 14dc0c7b687f31f2b7352b039feadfb31337326821160a117f436b65ae3c9b9a
```

The 2D repository is a read-only donor/reference for this ticket. The 3D implementation must be local to the 3D repository and must not live-import the 2D project.

## 2. Shared companion identity

These values are shared by the 2D and 3D presentations and identify one Dragon conversation:

```text
Hermes profile: default
Hermes session_id: 20260731_065008_63a62d
companion: hermes_b
provider: openai-codex
model: gpt-5.6-sol
```

Every 3D provider invocation must explicitly select:

```text
--profile default
--resume 20260731_065008_63a62d
--provider openai-codex
-m gpt-5.6-sol
```

The returned provider session ID must equal `20260731_065008_63a62d` exactly. A missing or different session ID is a STOP failure. The adapter must not create, accept, or persist a replacement identity.

The 2D and 3D projects may each maintain a project-local ignored operational state file:

```text
<project>/.godot/engain_hermes_session.json
```

Those files are not separate companion identities. Each must assert the same frozen profile/session/companion/provider/model tuple. Project-local replay/request bookkeeping must remain separate so one host cannot treat the other host's mailbox IDs as its own.

## 3. Host-specific identity

### 3.1 Existing 2D host

```text
project_id: engain_avatar
scene_path: res://addons/zwengain/scenes/EngAInDragon.tscn
```

### 3.2 New 3D host

```text
project_id: godot_3d_avatar
scene_path: res://scenes/Main.tscn
dragon_scene_path: res://scenes/DragonAvatar3D.tscn
```

`scene_path` is the actual running `SceneTree.current_scene.scene_file_path` and is therefore the value used in capture metadata and adapter correlation. `dragon_scene_path` identifies the nested 3D Dragon presentation instantiated by the running root scene. It is frozen separately to prevent the semantically tempting but false claim that the nested packed scene is Godot's current root scene.

A capture is admissible only when:

```text
current root scene == res://scenes/Main.tscn
and
an instantiated DragonAvatar3D presentation from
res://scenes/DragonAvatar3D.tscn is present at the frozen scene-owned path
```

The exact instantiated node path must be discovered from current scene bytes and frozen in the first SnapshotManager RED fixture before implementation. No fallback node search or newest-scene inference is authorized.

## 4. Mailbox location and transport

Transport remains a project-local file mailbox. HTTP, `/v1/engain/parse`, sockets, and shared cross-project mailbox files are outside this ticket.

```text
project root: /mnt/data-drive/godot_engain_3d_avatar
request mailbox: /mnt/data-drive/godot_engain_3d_avatar/engain_request.json
response mailbox: /mnt/data-drive/godot_engain_3d_avatar/engain_response.json
```

Publication and claiming must retain the proven fail-closed properties:

- one serialized in-flight request;
- atomic request publication;
- no overwrite of an unclaimed request or unread response;
- descriptor-bound/strict response claiming;
- strict JSON with duplicate keys and non-finite numbers rejected;
- bounded request, response, prompt, and provider-output sizes;
- processed-request and interrupted-replay protection;
- no directory scan for a replacement request, response, metadata file, or image.

## 5. Mailbox request schema/version

Contract identifier:

```text
engain.hermes_mailbox_request.v1
```

For first parity, this identifier names the exact proven five-key wire shape; it is a contract label and is not added as a sixth top-level wire key.

Exact top-level shape:

```json
{
  "player_input": "<bounded non-empty text>",
  "game_state": {},
  "additional_context": {
    "client_request_id": "<3D client request ID>",
    "companion_ref": "hermes_b",
    "perception": {}
  },
  "timestamp": 0.0,
  "request_id": "req_<32 lowercase hex>"
}
```

No unknown top-level or `additional_context` keys are admitted.

## 6. Mailbox response schema/version

Contract identifier:

```text
engain.hermes_mailbox_response.v1
```

For first parity, this identifier names the proven exact response wire shape; no additional top-level schema member is added.

Exact top-level keys:

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

Required safety values:

```text
action_type: OBSERVATION
state_changes: {}
entropy_impact: 0.0
```

`provider_session_ref` must contain exactly:

```json
{
  "companion_ref": "hermes_b",
  "provider": "openai-codex",
  "model": "gpt-5.6-sol",
  "session_id": "20260731_065008_63a62d"
}
```

The adapter, not model prose, owns these correlation and provenance fields.

## 7. Snapshot/capture schema versions

Request perception envelope:

```text
engain.runtime_perception.v1
```

Structured runtime snapshot:

```text
engain.runtime_snapshot.v1
```

Response perception result:

```text
engain.runtime_perception_result.v1
```

Frozen event and phase:

```text
capture_event: message_received
capture_phase: pre_dispatch_player_view.v1
```

The capture must occur after the 3D client request ID exists and before the HUD clears, disables, substitutes placeholder text, or otherwise changes the visible player view.

## 8. Capture directory and path rules

```text
absolute capture root: /mnt/data-drive/godot_engain_3d_avatar/snapshots
wire-relative capture root: snapshots/
metadata path: snapshots/perception_<capture_id>.json
image path: snapshots/perception_<capture_id>.png
```

Only project-relative POSIX paths matching those exact forms are accepted. Absolute paths, `..`, `.`, empty components, backslashes, URL schemes, control characters, nested extra components, symlinks, non-regular files, and paths outside the fixed root are rejected.

Each capture ID names one immutable PNG/JSON pair. The producer must never overwrite an existing pair. Missing, stale, or invalid files must never be replaced with the newest available capture.

## 9. Identifier formats and ownership

### 9.1 Request ID

Owner: 3D mailbox bridge.

```text
format: req_<32 lowercase hexadecimal characters>
regex: ^req_[0-9a-f]{32}$
rule: generated from 16 cryptographically random bytes; unique per publication attempt
```

A request ID is not derived from time, filename, client ID, capture ID, provider session, or prior request state.

### 9.2 Client request ID

Owner: 3D HUD/submission lifecycle.

```text
format: dragon3d_<32 lowercase hex>_<positive decimal sequence>
regex: ^dragon3d_[0-9a-f]{32}_[1-9][0-9]*$
rule: created before capture; unique per accepted player submission
```

### 9.3 Capture ID

Owner: 3D SnapshotManager.

```text
format: cap_<32 lowercase hex>_<positive decimal sequence>
regex: ^cap_[0-9a-f]{32}_[1-9][0-9]*$
rule: generated for every capture attempt, including unavailable attempts
```

`request_id`, `client_request_id`, and `capture_id` are distinct and must never be inferred from one another.

## 10. Image hash and image format

```text
hash algorithm: SHA-256
hash encoding: exactly 64 lowercase hexadecimal characters
allowed media type: image/png
allowed extension: .png
required PNG signature: 89 50 4E 47 0D 0A 1A 0A
required first chunk: IHDR
required IHDR length: 13
maximum image bytes: 16777216
```

The adapter hashes the same immutable PNG bytes that it validates and passes to Hermes. The computed digest must equal both the request viewport digest and metadata viewport digest.

No JPEG, WebP, SVG, text file, renamed foreign image, malformed PNG, or provider-generated substitute is admitted.

## 11. Required viewport-dimensions metadata

Both the request-level viewport object and metadata-file viewport object must contain:

```text
width: integer
height: integer
```

Rules:

```text
minimum width: 1
minimum height: 1
maximum width: 8192
maximum height: 8192
fixed resolution: none
```

The request-level and metadata-file viewport objects must be exactly equal. Width and height must exactly equal the dimensions parsed independently from the PNG IHDR. Declared dimensions alone are not evidence.

This freeze intentionally does not lock the current editor/window resolution. Resizing may change dimensions, but every request must carry and prove the dimensions of its own exact capture.

## 12. Capture freshness

For `full` or `structured_only` perception:

```text
captured_at is finite and positive
request.timestamp - captured_at >= 0 seconds
request.timestamp - captured_at <= 5 seconds
adapter_validation_time - captured_at <= 15 seconds
captured_at - adapter_validation_time <= 1 second
```

Timestamp proximity never establishes identity. All exact ID, path, content, and hash checks remain required.

## 13. Response correlation requirements

A response is accepted only when all applicable predicates pass.

### 13.1 Request identity

```text
response.request_id == active request.request_id
response.client_request_id == active request.additional_context.client_request_id
```

Stale, future, unsolicited, already-processed, or mismatched responses are rejected.

### 13.2 Capture identity

For non-rejected perception results:

```text
response.perception_result.capture_id
  == request.perception.capture_id
  == metadata.capture_id
  == capture ID encoded in metadata basename
  == capture ID encoded in image basename when an image is available
```

Also required:

```text
metadata.client_request_id == request.client_request_id
metadata.project_id == godot_3d_avatar
metadata.scene_path == res://scenes/Main.tscn
request viewport == metadata viewport
request capture event/phase/time == metadata event/phase/time
computed metadata SHA-256 == requested metadata SHA-256
computed image SHA-256 == requested image SHA-256 == metadata image SHA-256
```

### 13.3 Companion/provider identity

```text
companion_ref == hermes_b
Hermes profile == default
provider == openai-codex
model == gpt-5.6-sol
resumed session_id == returned session_id == 20260731_065008_63a62d
```

### 13.4 Read-only response authority

```text
action_type == OBSERVATION
state_changes is exactly an empty object
entropy_impact is finite and exactly 0.0
narrative_response is bounded non-empty text
```

Model prose cannot authorize movement, scene mutation, editor mutation, canon changes, entropy changes, or world-state changes.

### 13.5 Perception provenance

`effective_state = full` is accepted only when the exact validated image path was actually supplied through Hermes `--image` and `viewport_image_attached = true`.

For any effective state other than `full`, `viewport_image_attached` must be false. A pathname included in prompt text does not constitute image attachment.

## 14. Timeout and failure behavior

### 14.1 Timeouts

```text
Hermes provider timeout: 180 seconds
3D host/HUD wait timeout: 180 seconds
```

The host must not claim success or current perception after timeout. Timeout restores the input lifecycle safely and produces an explicit bounded failure/availability message. A late response whose active request lifecycle has ended is stale and must not be applied.

### 14.2 Capture availability outcomes

```text
full:
  validated structured snapshot plus exact validated image attachment

structured_only:
  validated structured snapshot; no image-bearing invocation;
  provider instruction explicitly denies current pixel vision

unavailable:
  no current trusted structured snapshot or image;
  provider instruction or deterministic local response explicitly denies current runtime perception
```

Allowed source availability reasons:

```text
capture_failed
cooldown_blocked
storage_unavailable
viewport_unavailable
image_write_failed
metadata_write_failed
scene_unavailable
```

Missing exact in-root files may downgrade honestly:

```text
IMAGE_MISSING -> structured_only when trusted metadata remains valid
METADATA_MISSING -> unavailable
```

No substitute file may be searched or selected.

### 14.3 Hard trust/correlation failures

At minimum, these fail before provider invocation:

```text
SCHEMA_INVALID
COMPANION_REF_INVALID
CLIENT_REQUEST_ID_MISMATCH
CAPTURE_ID_MISMATCH
CAPTURE_EVENT_INVALID
CAPTURE_PHASE_INVALID
PROJECT_ID_MISMATCH
SCENE_IDENTITY_MISMATCH
CAPTURE_STALE
METADATA_PATH_REJECTED
METADATA_HASH_MISMATCH
METADATA_CONTENT_MISMATCH
IMAGE_PATH_REJECTED
IMAGE_HASH_MISMATCH
UNSUPPORTED_IMAGE_TYPE
IMAGE_DIMENSION_MISMATCH
UNSUPPORTED_NATIVE_IMAGE_ROUTE
```

Hard rejection requires:

- no Hermes/provider invocation;
- no provider-session mutation;
- no image substitution;
- no runtime/world/editor mutation;
- deterministic observation-only failure response;
- `effective_state = rejected`;
- exact stable failure code;
- safe replay bookkeeping only after durable response publication.

### 14.4 Provider/session failures

```text
PROVIDER_TIMEOUT
PROVIDER_FAILURE
SESSION_IDENTITY_MISSING
SESSION_IDENTITY_MISMATCH
```

A missing or mismatched Hermes profile/session receipt is a STOP condition. No replacement session may be persisted. The 3D host may display a bounded failure but must not accept provider narrative from the wrong identity.

## 15. Explicit non-authorizations

This freeze does not authorize:

```text
editing /mnt/data-drive/engain_avatar
editing EngAIn donor/runtime repositories
reviving /v1/engain/parse
sharing one mutable mailbox across projects
loosening the accepted 2D contract
world or scene mutation
movement changes
camera-coupled autonomous vision
GodotOllama changes
Agent Portal implementation
new companion/session creation
commits or pushes
```

The 3D flight behavior and GodotOllama addon remain separate from the first Hermes parity lane.

## 16. Implementation gate

No 3D adapter implementation may be written until tests/fixtures encode this freeze and applicable tests are observed RED against the current 3D baseline.

The first implementation stage may add only the smallest 3D-local adapter/test surface needed to satisfy the frozen mailbox, identity, image, and failure contracts. SnapshotManager, bridge wiring, HUD integration, live acceptance, and commit authorization remain later gated stages.
