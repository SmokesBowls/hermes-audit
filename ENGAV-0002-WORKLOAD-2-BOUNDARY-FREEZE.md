# ENGAV-0002 Workload 2 — Runtime Perception Boundary Freeze

**Status:** FROZEN FOR LATER IMPLEMENTATION; NOT IMPLEMENTED  
**Ticket:** ENGAV-0002 — Hermes B Runtime Perception Proof  
**Workload:** 2 only  
**Project:** `/mnt/data-drive/engain_avatar`  
**Audit/evidence root:** `/mnt/data-drive/engain-avatar-audit`  
**Protected sibling:** `/mnt/data-drive/godotollama`  

## 1. Normative lineage and hash reconciliation

This boundary freeze is governed by the following upstream artifacts.

### 1.1 Ticket

```text
path: /mnt/data-drive/engain-avatar-audit/ENGAV-0002-PROPOSED.md
sha256: 570f185043b04b3e16c27707eda6ac507e988872eb3c75ea10ecf841c8de6651
bytes: 9238
```

The requested ticket hash matches the current file bytes.

### 1.2 Workload 1 discovery report

The authorization for Workload 2 named this hash:

```text
historical path: /mnt/data-drive/engain-avatar-audit/ENGAV-0002-WORKLOAD-1-BOUNDARY-REPORT.md
historical pre-amendment sha256: 257097e41d68d9c678698c3556a316d0049ad00176dd95b4844f8e0429d99753
```

That hash identifies the report before the subsequently authorized timing-boundary clarification. It no longer verifies the current file and must not be represented as its current byte identity.

The current amended report is:

```text
path: /mnt/data-drive/engain-avatar-audit/ENGAV-0002-WORKLOAD-1-BOUNDARY-REPORT.md
current sha256: 685ccbdabfce915276ba1be937168f91ec056c0b89ebe0b0fa599aceafa73c4f
bytes: 37677
```

This freeze is lineage-linked to the requested historical hash and normatively bound to the current amended bytes. Where the two differ, the amended timing boundary is controlling.

## 2. Scope

Workload 2 freezes only:

- exact implementation ownership;
- the request and response schema delta;
- capture phase and correlation rules;
- snapshot and image trust boundaries;
- provider-session ownership;
- perception provenance classes;
- fail-closed states;
- RED and toxic acceptance proof requirements;
- stage gates for later workloads.

Workload 2 does not authorize:

- source edits;
- test implementation;
- snapshot-delivery implementation;
- any Hermes invocation with an image;
- provider/backend runtime proof;
- Workload 3;
- GodotOllama changes;
- transport replacement;
- commits or pushes.

## 3. Final invariant

```text
A request may use only the viewport capture explicitly correlated
with its own client_request_id and capture_id.

Newest available image is not an acceptable substitute.
```

No directory scan, modification-time sort, “latest” pointer, previous successful capture, prior request capture, `ai_dragon_spoke` capture, or remembered image may satisfy a current request.

The adapter must never search for a replacement image. It may validate only the exact metadata path and viewport image path carried by the current request's perception envelope.

## 4. Authority and ownership

| Component | May own | Must not own |
|---|---|---|
| `EngAInDragon.gd` | player submission lifecycle, `client_request_id`, request capture timing, UI waiting state | provider session ID, image validation, filesystem trust, provider capability claims |
| `SnapshotManager.gd` | viewport pixel capture, capture ID, capture timestamp, scene/runtime snapshot, immutable PNG/JSON pair | player response, Hermes invocation, provider session, arbitrary semantic visual analysis |
| `EngAInBridge.gd` | existing top-level request ID, existing JSON mailbox write, preservation of the perception envelope | image selection, “newest image” lookup, provider invocation, perception claims |
| `hermes_session_adapter.py` | strict request validation, trusted path resolution, hash/type/freshness/correlation checks, active provider-session reference, attachment decision, provenance projection, fail-closed response | scene truth, image substitution, runtime mutation, creation of a replacement companion identity |
| Hermes B | text reasoning over explicitly supplied structured facts, actual attached pixels, and retained conversation | capture selection, filesystem authority, scene mutation, claiming unavailable perception |
| Godot runtime | current rendered pixels and runtime state | canon authority beyond its observed runtime state |
| GodotOllama | nothing in ENGAV-0002 | any runtime-perception implementation or evidence |

Core law:

```text
SnapshotManager captures.
Dragon correlates the capture to the player submission.
Bridge transports the exact envelope.
Adapter validates and attaches or refuses.
Hermes describes only what it actually receives.
```

## 5. Exact later implementation path boundary

The only existing source files prospectively authorized for later ENGAV-0002 implementation are:

```text
/mnt/data-drive/engain_avatar/addons/zwengain/scenes/SnapshotManager.gd
/mnt/data-drive/engain_avatar/addons/zwengain/scripts/EngAInDragon.gd
/mnt/data-drive/engain_avatar/addons/zwengain/scripts/EngAInBridge.gd
/mnt/data-drive/engain_avatar/hermes_session_adapter.py
```

The only new durable test path prospectively admitted is:

```text
/mnt/data-drive/engain_avatar/tests/test_hermes_session_adapter.py
```

Godot runtime proof may use explicitly named temporary files under `/tmp` and runtime-generated ignored files under the existing project `snapshots/` and `.godot/` areas, but no additional durable source/test path is admitted without a boundary amendment.

Explicitly outside the implementation boundary:

```text
/mnt/data-drive/engain_avatar/engain_dolphin.py
/mnt/data-drive/engain_avatar/addons/zwengain/scenes/EngAInDragon.tscn
/mnt/data-drive/engain_avatar/addons/zwengain/scenes/dynamiccontextmanager.gd
/mnt/data-drive/engain_avatar/VisionAgent.py
/mnt/data-drive/engain_avatar/zw_file_bridge.py
/mnt/data-drive/engain_avatar/project.godot
/mnt/data-drive/godotollama/**
/home/mytruelove/.hermes/hermes-agent/**
```

Structured perception presentation must be implemented at the Hermes adapter/client wrapper boundary rather than by modifying the legacy `engain_dolphin.py` director prompt. Hermes Agent itself is a supported external dependency and is read-only for this ticket.

The exact test path is new because discovery found no existing project test tree. Its admission does not create it during Workload 2.

## 6. Canonical request capture phase

Workload 2 adopts the current player-view timing as the canonical request phase and gives it a stable name:

```text
capture_phase = pre_dispatch_player_view.v1
capture_event = message_received
```

The required order is:

```text
1. Player submits non-empty bounded text.
2. Dragon generates client_request_id.
3. No visible UI state is changed.
4. SnapshotManager receives that client_request_id and creates capture_id.
5. SnapshotManager reads the active viewport while submitted text is still visible.
6. SnapshotManager captures the corresponding structured runtime state.
7. SnapshotManager closes the immutable PNG and JSON files and computes their hashes.
8. Dragon receives the complete perception envelope or an explicit unavailable result.
9. EngAInBridge creates the existing top-level request_id and writes the existing request artifact.
10. Only after dispatch may the LineEdit be cleared/disabled and show `EngAIn is thinking...`.
```

Generating `client_request_id` before capture is a required non-visual ordering correction. It does not change the intended pixels; it makes those pixels provably request-correlated.

A capture made after LineEdit clearing, after `EngAIn is thinking...`, after provider dispatch, or from a prior request is not `pre_dispatch_player_view.v1`.

### 6.1 Dragon-speech exclusion

Current `ai_dragon_spoke` PNGs are pre-display captures. They do not show the new speech text and are not admissible as evidence that a resulting response appeared.

The adapter must reject any perception envelope whose `capture_event` is `ai_dragon_spoke` or whose `capture_phase` is not exactly `pre_dispatch_player_view.v1`.

A future post-response rendering proof requires a separate capture phase and separate authorization. ENGAV-0002 request perception must not silently reuse the current dragon-speech snapshots.

## 7. Existing request format and frozen delta

The top-level JSON mailbox format remains the existing format. No replacement envelope or transport is introduced.

```json
{
  "player_input": "<bounded player text>",
  "game_state": {},
  "additional_context": {
    "client_request_id": "<dragon-owned ID>",
    "companion_ref": "hermes_b",
    "perception": {}
  },
  "timestamp": 0.0,
  "request_id": "req_<existing Bridge-generated ID>"
}
```

Top-level ownership remains:

- `request_id`: `EngAInBridge.gd`;
- `timestamp`: `EngAInBridge.gd`, after capture and immediately before mailbox write;
- `player_input`: submitted text;
- `game_state`: existing Bridge game-state object;
- `additional_context.client_request_id`: Dragon;
- `additional_context.companion_ref`: fixed logical identity `hermes_b`;
- `additional_context.perception`: exact capture result for this request.

The legacy fields below are removed rather than treated as perception evidence:

```text
visual_snapshots_available
recent_visual_events
```

They are Boolean/hard-coded hints, not current correlated evidence.

`additional_context` must survive adapter parsing as a validated object. The current behavior of extracting only `client_request_id` is explicitly insufficient.

## 8. Frozen perception envelope schema

Schema identifier:

```text
engain.runtime_perception.v1
```

Closed-world shape:

```json
{
  "schema": "engain.runtime_perception.v1",
  "perception_state": "full | structured_only | unavailable",
  "capture_id": "cap_<safe unique suffix>",
  "capture_event": "message_received",
  "capture_phase": "pre_dispatch_player_view.v1",
  "captured_at": 0.0,
  "project_id": "engain_avatar",
  "scene_path": "res://addons/zwengain/scenes/EngAInDragon.tscn",
  "snapshot": null,
  "viewport": {
    "availability": "available | unavailable",
    "image_path": null,
    "image_sha256": null,
    "media_type": null,
    "width": null,
    "height": null,
    "reason": null
  },
  "unavailable_reason": null
}
```

No unknown keys are accepted in the perception envelope, snapshot object, viewport object, or frozen metadata object.

### 8.1 Identifier rules

`client_request_id`, top-level `request_id`, and `capture_id` are separate identities and must never be inferred from one another.

```text
client_request_id:
  existing safe-identifier rule, 1..128 characters

capture_id:
  regex ^cap_[A-Za-z0-9_-]{1,80}$
  unique for every capture attempt

companion_ref:
  exact literal hermes_b
```

The adapter compares exact strings. Case folding, prefix matching, truncation, basename matching, timestamp proximity alone, or substring matching is forbidden.

### 8.2 Perception-state rules

#### `full`

Requires:

- valid non-null `capture_id`;
- exact event and phase;
- finite positive `captured_at`;
- exact project and scene identity;
- valid snapshot object and metadata;
- viewport `availability = available`;
- valid image path/hash/type/dimensions;
- all correlation and freshness gates PASS.

Only `full` may produce an image-bearing Hermes invocation.

#### `structured_only`

Requires:

- valid capture identity/event/phase/time;
- valid snapshot metadata;
- viewport `availability = unavailable`;
- null image path/hash/media type/width/height;
- non-empty bounded viewport reason;
- all structured-state correlation/freshness gates PASS.

It permits a text-only Hermes turn containing the sanitized structured snapshot and an explicit statement that current viewport pixels are unavailable.

#### `unavailable`

Requires:

- `snapshot = null`;
- viewport `availability = unavailable` with all image fields null;
- non-empty `unavailable_reason` from the frozen reason set;
- no image attachment.

It permits only a text-only turn explicitly marked as having no current runtime perception, or a deterministic local denial response if request trust itself failed.

### 8.3 Unavailable reason set

Source-reported availability reasons are closed to:

```text
capture_failed
cooldown_blocked
storage_unavailable
viewport_unavailable
image_write_failed
metadata_write_failed
scene_unavailable
```

Adapter-derived effective reasons are closed to:

```text
image_missing
metadata_missing
```

Trust/correlation failures use failure codes, not availability reasons.

## 9. Frozen snapshot metadata schema

When `snapshot` is present, its exact request shape is:

```json
{
  "metadata_path": "snapshots/perception_<capture_id>.json",
  "metadata_sha256": "<64 lowercase hex>",
  "metadata": {
    "schema": "engain.runtime_snapshot.v1",
    "capture_id": "<same capture_id>",
    "client_request_id": "<same client_request_id>",
    "capture_event": "message_received",
    "capture_phase": "pre_dispatch_player_view.v1",
    "captured_at": 0.0,
    "project_id": "engain_avatar",
    "scene_path": "res://addons/zwengain/scenes/EngAInDragon.tscn",
    "runtime": {
      "fps": 0.0,
      "current_location": "",
      "inventory": [],
      "player_position": null
    },
    "viewport": {
      "availability": "available | unavailable",
      "image_path": null,
      "image_sha256": null,
      "media_type": null,
      "width": null,
      "height": null,
      "reason": null
    }
  }
}
```

The metadata file contains exactly the `metadata` object above. The adapter:

1. reads the metadata file bytes once;
2. hashes those same bytes;
3. strict-parses those same bytes;
4. rejects duplicate keys and non-finite constants;
5. requires parsed metadata to equal the inline request metadata;
6. independently checks all identity and path fields.

The metadata SHA-256 binds raw file bytes. Object equality does not replace raw-byte hash equality.

The frozen metadata must not contain or transmit:

```text
visual_analysis
hard-coded recent_visual_events
model-generated scene descriptions
provider instructions
arbitrary node dumps
credentials
absolute filesystem paths
```

Missing runtime fields remain null/empty as specified. SnapshotManager must not invent values.

## 10. Viewport object and PNG contract

For an available viewport:

```json
{
  "availability": "available",
  "image_path": "snapshots/perception_<capture_id>.png",
  "image_sha256": "<64 lowercase hex>",
  "media_type": "image/png",
  "width": 1152,
  "height": 648,
  "reason": null
}
```

The request-level viewport object and metadata-level viewport object must be exactly equal.

For an unavailable viewport:

```json
{
  "availability": "unavailable",
  "image_path": null,
  "image_sha256": null,
  "media_type": null,
  "width": null,
  "height": null,
  "reason": "<bounded reason>"
}
```

### 10.1 Capture timestamp

`captured_at` is Unix system time recorded immediately after `get_viewport().get_texture().get_image()` returns and before PNG encoding begins.

It is not:

- filename time;
- metadata-write completion time;
- request-write time;
- provider invocation time;
- response time.

The same `captured_at` value must appear in the request envelope and metadata file.

### 10.2 Freshness gates

For `full` or `structured_only`:

```text
captured_at must be finite and positive
request.timestamp - captured_at must be >= 0
request.timestamp - captured_at must be <= 5 seconds
adapter_validation_time - captured_at must be <= 15 seconds
captured_at may not be more than 1 second in the adapter's future
```

Failure of any freshness gate is `CAPTURE_STALE`; no provider call is permitted.

Timestamp proximity never establishes identity. Correct IDs and hashes are still mandatory.

## 11. Constrained filesystem trust boundary

Approved snapshot root:

```text
/mnt/data-drive/engain_avatar/snapshots
```

Request artifacts may carry only project-relative POSIX paths with these exact forms:

```text
snapshots/perception_<capture_id>.json
snapshots/perception_<capture_id>.png
```

Rules:

1. Absolute paths are rejected.
2. `..`, `.`, empty components, backslashes, NUL, control characters, URL schemes, and extra path components are rejected.
3. The basename's capture ID must equal the envelope `capture_id` exactly.
4. The approved root must resolve to the fixed project snapshot root.
5. The approved root and target files must not be symlinks.
6. Every target must exist when required and be a regular file.
7. Resolution must remain beneath the approved root.
8. The adapter must use no directory scan and no latest-file lookup.
9. The adapter reads and hashes each file's actual bytes; request hashes are claims to verify, not authority.
10. SnapshotManager writes unique capture files once and never overwrites an existing capture ID.
11. Old generic snapshot filenames do not satisfy the required perception filename/schema contract.

The adapter must not accept an arbitrary user-supplied path and pass it to Hermes.

### 11.1 Metadata file bounds

```text
maximum metadata bytes: 262144
encoding: UTF-8
format: strict JSON object
hash: SHA-256 lowercase hex
```

The same bytes are hashed and parsed.

### 11.2 PNG file bounds and type checks

```text
maximum PNG bytes: 16777216
minimum width: 1
minimum height: 1
maximum width: 8192
maximum height: 8192
required extension: .png
required media_type: image/png
required PNG signature: 89 50 4E 47 0D 0A 1A 0A
required first chunk: IHDR with length 13
```

The adapter must parse width and height from IHDR and require exact equality with both viewport objects. Extension or declared media type alone is insufficient.

A file with `.png` suffix but wrong signature/IHDR is `UNSUPPORTED_IMAGE_TYPE`.

The adapter computes SHA-256 over the same PNG bytes it type-checks. The digest must equal both the request viewport hash and metadata viewport hash.

### 11.3 Local-writer immutability rule

SnapshotManager is the sole writer of admitted perception files. A capture filename is unique and immutable after close.

The adapter must hash immediately before a later image-bearing Hermes launch. A later proof must re-hash after the call; any change invalidates the proof and triggers STOP. The adapter may never silently retry with a different image.

## 12. Correlation gates and validation order

The adapter validates in this exact order before constructing a Hermes command:

```text
1. Existing bounded request-file and strict-JSON checks.
2. Existing top-level request_id/player_input/game_state checks.
3. Exact additional_context shape.
4. client_request_id syntax.
5. companion_ref == hermes_b.
6. Exact perception schema and state shape.
7. capture_id syntax and path-basename binding.
8. capture_event == message_received.
9. capture_phase == pre_dispatch_player_view.v1.
10. perception.client_request_id binding through metadata.
11. project_id and scene_path equality.
12. freshness gates.
13. metadata path containment/type/size/read/hash/strict parse.
14. inline metadata equality.
15. metadata capture_id == request perception capture_id.
16. metadata client_request_id == additional_context client_request_id.
17. metadata event/phase/time/project/scene equality.
18. viewport-object equality.
19. image path containment/existence/regular-file/type/size/read/hash/dimensions.
20. load the adapter-owned persisted Hermes session identity.
21. require configured provider=openai-codex and model=gpt-5.6-sol for image-bearing turns.
22. choose full, structured-only, unavailable, or hard rejection.
23. only then construct a text-only or image-bearing command.
```

Core correlation predicate for `full`:

```text
request.additional_context.client_request_id
  == metadata.client_request_id

request.additional_context.perception.capture_id
  == metadata.capture_id
  == capture_id encoded in metadata_path basename
  == capture_id encoded in image_path basename

request perception viewport
  == metadata viewport

computed metadata SHA-256
  == request snapshot.metadata_sha256

computed image SHA-256
  == request viewport.image_sha256
  == metadata viewport.image_sha256
```

Every equality is required. “Close enough,” newest, same timestamp, or same scene is not accepted.

## 13. Companion/provider session reference

The Godot request carries only:

```text
companion_ref = hermes_b
```

Godot does not own or assert a provider session ID.

The adapter owns the provider-session reference by loading:

```text
/mnt/data-drive/engain_avatar/.godot/engain_hermes_session.json
```

The currently proven reference is:

```json
{
  "companion_ref": "hermes_b",
  "provider": "openai-codex",
  "model": "gpt-5.6-sol",
  "session_id": "20260731_065008_63a62d"
}
```

For every provider call:

- `--resume` must carry that persisted session ID;
- returned `session_id:` must equal it exactly;
- a missing/different ID is failure;
- the adapter must not create or accept a replacement session;
- request-supplied provider session IDs are rejected as unknown fields.

A later runtime may update the persisted ID only through the already-proven same-session mechanism. ENGAV-0002 may not intentionally rotate identity.

## 14. Hermes turn construction and provenance rules

The adapter may supply four provenance classes and must keep them distinct:

```text
STRUCTURED_RUNTIME
  validated fields from engain.runtime_snapshot.v1

VIEWPORT_IMAGE
  pixels from the exact validated PNG actually attached as image input

CONVERSATION_MEMORY
  prior messages in the resumed Hermes B session

UNAVAILABLE_OR_UNVERIFIED
  anything missing, rejected, stale, or not established by the other classes
```

### 14.1 Structured data

Only the sanitized frozen metadata fields may enter the structured runtime section. Raw metadata text, `visual_analysis`, arbitrary dictionaries, and path strings are not scene facts.

### 14.2 Image data

Hermes may claim current visual observation only when:

```text
perception_state == full
image validation passed
--image receives the exact validated path
Hermes native route treats it as input_image
returned session identity is preserved
```

A pathname in prompt text is never image evidence.

### 14.3 Memory

Remembered facts remain memory even if they resemble the current image. Memory cannot promote unavailable current perception to observed perception.

### 14.4 Unavailable perception instruction

For `structured_only` or `unavailable`, the text turn must state unambiguously:

```text
No current viewport image is attached for this request.
Do not claim to see current artwork, objects, colors, positions, or UI from pixels.
Identify structured runtime facts as supplied data and prior facts as memory.
```

For `unavailable`, it must additionally state:

```text
No current structured runtime snapshot is available for this request.
```

These are provider instructions, not facts generated by SnapshotManager.

### 14.5 No cross-request carryover

Validated perception is one-turn state. The adapter must clear it in a `finally` path after each request. It may not remain on the Hermes client wrapper and leak into the next request.

## 15. Response schema delta

The existing response fields remain:

```text
request_id
client_request_id
narrative_response
action_type = OBSERVATION
state_changes = {}
director_analysis
reasoning
entropy_impact = 0.0
timestamp
```

The response adds:

```json
{
  "provider_session_ref": {
    "companion_ref": "hermes_b",
    "provider": "openai-codex",
    "model": "gpt-5.6-sol",
    "session_id": "20260731_065008_63a62d"
  },
  "perception_result": {
    "schema": "engain.runtime_perception_result.v1",
    "requested_state": "full | structured_only | unavailable",
    "effective_state": "full | structured_only | unavailable | rejected",
    "capture_id": null,
    "capture_event": null,
    "capture_phase": null,
    "captured_at": null,
    "metadata_sha256": null,
    "image_sha256": null,
    "structured_snapshot_supplied": false,
    "viewport_image_attached": false,
    "failure_code": null
  }
}
```

The response provenance is adapter-observed evidence, not model-authored text.

On hard rejection, `viewport_image_attached` and `structured_snapshot_supplied` are false, `effective_state = rejected`, and no provider call occurs.

On a missing image with otherwise valid metadata, the adapter may downgrade from requested `full` to effective `structured_only`, set `failure_code = IMAGE_MISSING`, make no image-bearing call, and use the explicit text-only instruction.

## 16. Failure states

### 16.1 Valid availability outcomes

| State | Provider policy | Required narrative boundary |
|---|---|---|
| `full` | Later workload may make exactly one correlated image-bearing call | May describe attached pixels and supplied structured state distinctly |
| `structured_only` | Text-only call only | May cite structured state; must deny current pixel vision |
| `unavailable` | Text-only call or deterministic local denial | Must deny both current structured and pixel perception |

### 16.2 Hard-rejection codes

The following fail before provider invocation:

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

Hard rejection behavior:

1. no Hermes/provider invocation;
2. no session-state mutation;
3. no image substitution;
4. deterministic observation-only response stating current perception could not be trusted;
5. exact top-level request/client correlation echoed where safely parsed;
6. `perception_result.effective_state = rejected`;
7. exact failure code recorded;
8. request removed only under the existing unchanged-byte rule;
9. request ID recorded as processed to prevent unsafe replay only after the deterministic response is durably written.

### 16.3 Missing-file downgrade

`IMAGE_MISSING` and `METADATA_MISSING` are availability failures rather than path-trust failures only when the requested paths are syntactically valid and within the approved root.

- Missing image + valid trusted metadata: effective `structured_only`, no image-bearing call.
- Missing metadata: effective `unavailable`, no image-bearing call.
- A path outside root, symlink, wrong type, hash mismatch, or correlation mismatch is hard rejection, not downgrade.

### 16.4 Provider/session failures

```text
PROVIDER_TIMEOUT
PROVIDER_FAILURE
SESSION_IDENTITY_MISSING
SESSION_IDENTITY_MISMATCH
```

A session identity mismatch is a STOP condition. The call's response is not accepted, the new ID is not persisted, and no replacement identity is created.

## 17. Frozen RED and toxic acceptance proofs

These proofs are specifications only during Workload 2. No test file is created and no Hermes process is invoked. In the next authorized workload, each applicable test must be observed failing before the corresponding source implementation is added.

All adapter tests must mock the subprocess boundary. Unit tests must never invoke real Hermes or a provider.

### R01 — valid correlated snapshot accepted

Arrange a current `full` request with:

- exact request/client/capture bindings;
- valid metadata and PNG beneath approved root;
- exact hashes;
- valid PNG signature/IHDR/dimensions;
- expected event/phase/project/scene.

Expected after later implementation:

- validation result is `full`;
- exact resolved image path is selected;
- no directory scan occurs;
- mocked command contains exactly one `--image` followed by that path;
- response provenance echoes exact hashes and capture ID.

### R02 — `additional_context` survives adapter parsing

Arrange a valid perception envelope in the existing request format.

Expected:

- validator returns the complete validated `client_request_id`, `companion_ref`, perception envelope, inline metadata, and effective state;
- fields are not discarded before turn construction.

### R03 — wrong `client_request_id` rejected

Mutate metadata `client_request_id` while keeping every other field and hash internally consistent.

Expected:

```text
CLIENT_REQUEST_ID_MISMATCH
no provider call
no image substitution
```

### R04 — wrong `capture_id` rejected

Mutate one capture ID location and, in a second toxic case, mutate metadata plus filenames together while leaving the request envelope unchanged.

Expected:

```text
CAPTURE_ID_MISMATCH
no provider call
```

Coordinated substitution must not pass.

### R05 — missing image represented as unavailable

Remove the exact in-root PNG after constructing an otherwise valid request.

Expected:

- no image-bearing call;
- effective state is `structured_only` when metadata remains valid, otherwise `unavailable`;
- `failure_code = IMAGE_MISSING`;
- text-only instruction says no current viewport image is attached;
- narrative cannot claim current pixel vision.

### R06 — stale image rejected

Set capture time beyond either freshness threshold while keeping identities and hashes correct.

Expected:

```text
CAPTURE_STALE
no provider call
newest image is not searched
```

### R07 — image hash mismatch rejected

Change one PNG byte or alter the claimed digest.

Expected:

```text
IMAGE_HASH_MISMATCH
no provider call
```

### R08 — metadata hash mismatch rejected

Change metadata raw bytes without updating the request hash, including whitespace-only byte drift.

Expected:

```text
METADATA_HASH_MISMATCH
no provider call
```

### R09 — path outside approved snapshot root rejected

Test:

- absolute external path;
- `../` traversal;
- symlink beneath snapshot root targeting outside;
- nested extra path component;
- URL-like path;
- capture ID basename mismatch.

Expected:

```text
METADATA_PATH_REJECTED or IMAGE_PATH_REJECTED
no provider call
```

### R10 — unsupported image type rejected

Use:

- JPEG bytes named `.png`;
- text bytes named `.png`;
- valid PNG bytes with non-`.png` path;
- malformed/truncated IHDR;
- dimensions outside bounds.

Expected:

```text
UNSUPPORTED_IMAGE_TYPE or IMAGE_DIMENSION_MISMATCH
no provider call
```

### R11 — text-only fallback does not claim current vision

Arrange `structured_only` and `unavailable` requests.

Expected:

- command has no `--image`;
- prompt includes exact unavailability instruction;
- deterministic assertions reject phrases that attribute current artwork/color/object/position facts to vision;
- supplied structured facts are labeled as structured data;
- memory facts are not labeled as current observation.

A later live semantic proof is still required; string assertions alone do not close grounded denial behavior.

### R12 — Hermes B session identity preserved

Mock the configured session state and returned stderr session ID.

Positive expected:

- command contains exactly one `--resume 20260731_065008_63a62d`;
- returned ID matches;
- persisted ID remains unchanged.

Toxic expected:

- missing/different returned ID fails;
- replacement ID is not persisted;
- response is not accepted.

### R13 — wrong event/phase rejected

Use `ai_dragon_spoke`, unknown event, `pre_display_response`, and absent phase.

Expected:

```text
CAPTURE_EVENT_INVALID or CAPTURE_PHASE_INVALID
no provider call
```

This prevents response snapshots from being reused as request perception.

### R14 — newest image substitution forbidden

Place a newer valid PNG/JSON pair in the approved root while the request's exact image is missing, stale, or invalid.

Expected:

- newer pair is ignored;
- no directory enumeration or mtime selection occurs;
- request is downgraded/rejected according to its own exact artifacts.

### R15 — metadata inline/file coordinated substitution rejected

Change inline metadata and metadata-file bytes together, recompute metadata hash, but leave request-level client/capture/scene or viewport bindings unchanged.

Expected:

```text
correlation/content mismatch
no provider call
```

The metadata cannot authorize its own replacement.

### R16 — no perception leakage across requests

Process one valid request followed by unavailable and malformed requests using the same adapter/client object.

Expected:

- later commands contain no prior image path, hash, capture ID, or structured snapshot;
- pending perception is cleared even after exceptions/timeouts.

### R17 — request/response remains read-only

For every success, downgrade, and rejection:

```text
action_type == OBSERVATION
state_changes == {}
entropy_impact == 0.0
```

Dragon must continue rejecting any mutating response.

### R18 — Workload 2 no-image proof

Required current-workload evidence:

```text
no source file modified
no test file created
no engain_request.json created
no engain_response.json created
no snapshot/session artifact modified
no hermes chat invocation with --image
no provider runtime probe
```

The only Workload 2 writes are this audit document and its checksum sidecar outside both implementation repositories.

## 18. Later workload gates

### Workload 3 may begin only after separate authorization

Workload 3 is limited to the smallest structured SnapshotManager/request-envelope implementation and mocked RED proofs. It must not invoke Hermes with an image unless separately authorized as part of Workload 4.

### Workload 4 may begin only after Workload 3 closes and separate authorization

Workload 4 owns the first real image-bearing Hermes invocation and runtime multimodal proof. It must preserve the exact session and stop on provider/session rejection.

### Workload 5 remains acceptance-only

Changed-view, follow-up, denial, memory-plus-perception, and visible grounding proofs remain later gates.

## 19. Mandatory stop conditions

Stop rather than broaden or simulate success if:

1. any source path beyond the frozen allowlist is required;
2. `engain_dolphin.py`, `project.godot`, scene wiring, Hermes Agent source, or GodotOllama would need modification;
3. the current JSON file bridge would need replacement;
4. a unique immutable capture cannot be produced;
5. capture cannot be generated after `client_request_id` but before visible UI mutation;
6. exact client/capture correlation cannot be maintained;
7. only newest/previous image lookup is available;
8. trusted path containment cannot be enforced;
9. image bytes cannot be hashed and type-checked before attachment;
10. structured metadata cannot be separated from templated visual prose;
11. active provider/model cannot be statically and later dynamically shown to use native image input;
12. the exact Hermes B session cannot be resumed;
13. any failure path would claim current vision without an attached accepted image;
14. response mutation gates would need weakening;
15. runtime proof would mutate scene/world state;
16. credentials would need to be preserved in evidence;
17. Workload 3 or 4 would proceed without their required RED proof first.

## 20. Boundary freeze statement

This document freezes the intended implementation seam; it does not grant implementation authority.

```text
existing player message
→ client_request_id
→ exact pre_dispatch_player_view.v1 capture
→ immutable correlated metadata/PNG pair
→ existing request JSON with additional_context.perception
→ strict adapter validation
→ same persisted Hermes B session
→ either exact native image attachment or explicit no-vision state
→ observation-only response with adapter-owned provenance
```

Proposal is not execution. Valid capture is not provider acceptance. Provider acceptance is not grounded perception. Grounded perception is not mutation authority.

Workload 2 ends with this freeze and its verified checksum. Workload 3 has not begun.
