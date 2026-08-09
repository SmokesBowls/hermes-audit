# ENGAV-0002 Workload 1 — Read-Only Discovery and Supported/Unsupported Boundary Report

**Ticket:** ENGAV-0002 — Hermes B Runtime Perception Proof  
**Workload:** 1 only  
**Audit time:** 2026-08-01T05:34:00Z  
**Project:** `/mnt/data-drive/engain_avatar`  
**Protected sibling:** `/mnt/data-drive/godotollama`  
**Result:** **SUPPORTED WITH UNRESOLVED RUNTIME PROOF**

## 1. Scope and conclusion

Workload 1 was limited to read-only discovery. No project source, session state, snapshot, request/response artifact, retained evidence, or protected sibling repository was edited. No Hermes image-bearing turn was invoked. Workload 2 did not begin.

Static evidence establishes a genuine image route in the installed Hermes implementation:

```text
hermes chat --image PATH
→ local image validation and byte read
→ MIME detection and base64 data URL
→ OpenAI-style image_url content part
→ openai-codex codex_responses transport
→ Responses input_image part
→ client.responses.create(...)
```

For the configured active route, static capability metadata says:

```json
{
  "id": "gpt-5.6-sol",
  "attachment": true,
  "modalities": {
    "input": ["text", "image", "pdf"],
    "output": ["text"]
  }
}
```

The current EngAIn adapter does **not** use that route. It invokes Hermes with text only and never passes `--image`. Therefore actual image ingestion by the resumed Hermes B session remains unperformed and must be proved only in a later separately authorized workload.

The correct Workload 1 conclusion is:

> **SUPPORTED WITH UNRESOLVED RUNTIME PROOF** — the native route exists and static source traces through `input_image`, but no authorized live image-bearing invocation has proved acceptance by the active backend or by the resumed Hermes B session.

## 2. Read-only method and denied probe record

Evidence came from:

- direct source inspection with line-numbered reads;
- direct reads of retained JSON state and snapshot metadata;
- file type, timestamp, size, and SHA-256 inspection;
- visual inspection of three retained PNGs without invoking Hermes;
- Hermes CLI help;
- installed Hermes source inspection;
- static JSON inspection of the local models.dev cache;
- read-only Hermes session-history inspection;
- Git status, HEAD, and tree inspection.

Required denial record:

```text
capability probe attempted
→ approval denied
→ no retry or equivalent attempted
→ dynamic confirmation remains unperformed
```

The denied command would have imported and executed `decide_image_input_mode()` and `_lookup_supports_vision()` from the installed Hermes Python code. It did not run. It was not retried or rephrased. No equivalent execution-based capability probe was attempted.

A later Node command only parsed the already-retained `models_dev_cache.json` as static evidence. It did not import Hermes, execute routing code, invoke a provider, alter session state, or send an image.

## 3. Actual SnapshotManager APIs and outputs

Active implementation:

`/mnt/data-drive/engain_avatar/addons/zwengain/scenes/SnapshotManager.gd`

The active scene instantiates it as the root-level `SnapshotManager` node in:

`/mnt/data-drive/engain_avatar/addons/zwengain/scenes/EngAInDragon.tscn:234-235`

### 3.1 APIs

#### `capture_snapshot(event_type, zw_packet, state, priority=MEDIUM)`

Defined at `SnapshotManager.gd:87`.

Behavior:

1. Applies a cooldown keyed by priority, not by event (`:90`, `:185-189`).
2. Checks aggregate snapshot storage and may purge (`:93-97`).
3. obtains the node's viewport with `get_viewport()` (`:100`);
4. reads current pixels with `viewport.get_texture().get_image()` (`:101`);
5. saves a PNG under `snapshots/<priority>_<event>_<local-datetime>.png` (`:103-116`);
6. builds JSON metadata (`:121-139`);
7. saves the paired JSON under the same basename (`:141-148`);
8. returns:

```json
{
  "image": "snapshots/<basename>.png",
  "meta": "snapshots/<basename>.json",
  "priority": "<enum integer>"
}
```

The function returns `null` when cooldown, storage, image-save, or metadata-save gates fail.

#### `capture_event(event_name, data={})`

Defined at `SnapshotManager.gd:296-300`.

It derives priority from `event_priorities`, constructs:

```json
{"event": "<event_name>", "data": {}}
```

and calls `capture_snapshot()` with `_get_current_game_state()`.

Important limitation: `capture_event()` does not return the result of `capture_snapshot()`. Current callers cannot obtain the image path, metadata path, or capture failure from this API.

#### `manual_snapshot(description)`

Defined at `SnapshotManager.gd:305-306`. It calls `capture_event("manual_capture", ...)` and also does not return a result.

#### `get_storage_stats()`

Defined at `SnapshotManager.gd:308-316`. It returns:

```json
{
  "total_snapshots": 0,
  "storage_used_mb": 0.0,
  "storage_limit_mb": 500.0,
  "storage_percent": 0.0,
  "can_capture": true
}
```

Values are computed at runtime. The current Dragon uses only `total_snapshots > 0`.

#### `_get_current_game_state()`

Defined at `SnapshotManager.gd:262-277`. Current output is limited to:

- `timestamp`;
- current scene path;
- FPS;
- optional `player_position` only if `/root/Global.player` exposes `get_global_position`;
- `inventory` from `/root/Global`, defaulting to `[]`;
- `current_location` from `/root/Global`, defaulting to `""`.

### 3.2 Metadata format

Every retained JSON sample contains:

- `timestamp` — metadata creation time after PNG save;
- `event`;
- `priority` and `priority_name`;
- `zw_packet` with event-specific data;
- `state` with its own earlier timestamp;
- `retention_hours`;
- `file_size_kb` for the PNG;
- `visual_analysis`;
- reality/dream/anchor/broadcast values;
- Godot version;
- `scene_path`;
- FPS.

The metadata does **not** contain:

- EngAIn `request_id`;
- Dragon `client_request_id`;
- Hermes session ID;
- image pathname;
- metadata pathname;
- image SHA-256;
- explicit snapshot/capture ID;
- project path or project identifier;
- separate viewport-capture completion time;
- a success/failure correlation field.

PNG↔JSON pairing is only by identical basename.

### 3.3 `visual_analysis` is not visual perception

`SnapshotManager.gd:156-181` generates `visual_analysis` from a hard-coded template plus event text. It does not inspect image pixels.

The repeated claims about reality-control panels, timeline anchors, dimensional monitoring displays, and cosmic engineering are template text. They must not be presented to Hermes B as facts observed in the PNG.

## 4. Retained SnapshotManager samples

Seven PNG/JSON pairs were retained in:

`/mnt/data-drive/engain_avatar/snapshots`

All PNGs are valid, non-interlaced, 8-bit RGBA PNG files.

| Basename | Event | Metadata timestamp | State timestamp | Dimensions | PNG bytes |
|---|---|---:|---:|---:|---:|
| `low_message_received_2026-07-31T06_48_02` | `message_received` / `hello` | `1785505682.81011` | `1785505682.42896` | 1100×619 | 1,286,452 |
| `low_ai_dragon_spoke_2026-07-31T06_50_50` | `ai_dragon_spoke` / `TOKEN STORED` | `1785505851.09898` | `1785505850.69891` | 1152×648 | 1,350,209 |
| `low_ai_dragon_spoke_2026-07-31T06_51_14` | `ai_dragon_spoke` / `DRAGON-VISUAL-9A42` | `1785505874.63921` | `1785505874.24942` | 1152×648 | 1,349,992 |
| `low_message_received_2026-07-31T06_51_45` | `message_received` / `hi` | `1785505905.48119` | `1785505905.09971` | 1152×648 | 1,343,479 |
| `low_ai_dragon_spoke_2026-07-31T06_52_10` | `ai_dragon_spoke` / long Hermes response | `1785505930.4064` | `1785505930.01712` | 1152×648 | 1,350,899 |
| `low_message_received_2026-07-31T06_52_26` | `message_received` / `describe what you see` | `1785505947.11726` | `1785505946.71729` | 1152×648 | 1,348,914 |
| `low_ai_dragon_spoke_2026-07-31T06_52_57` | `ai_dragon_spoke` / Hermes timeout text | `1785505977.63778` | `1785505977.23468` | 1152×648 | 1,349,158 |

Filesystem mtimes are within approximately one millisecond of each paired metadata timestamp. The filename second can be one second earlier than the metadata timestamp because the basename is generated before image encoding and save.

### 4.1 Do these represent the active viewport?

At capture time: **yes**.

Static source calls `get_viewport().get_texture().get_image()` from the `SnapshotManager` node instantiated in the active `EngAInDragon.tscn` scene. Visual inspection confirms the PNGs show that running game's rendered viewport:

- the temple/cosmic-command-center background;
- the animated dragon at changing positions and frames;
- the speech label;
- the bottom LineEdit and its entered text or placeholder.

The retained `hello` message image visibly contains the text `hello` in the LineEdit and the label `EngAIn consciousness initializing...`.

The retained `describe what you see` message image visibly contains that exact command in the LineEdit, a red dragon, and `EngAIn Dragon awaits your input...`.

The latest `ai_dragon_spoke` image visibly contains the dragon and `EngAIn Dragon awaits your input...`; its bottom LineEdit still shows `EngAIn is thinking...`.

The PNGs are therefore real viewport captures, not generated descriptions. They are, however, historical retained captures from 2026-07-31. They do not prove what the viewport contains now.

### 4.2 Capture timing boundary

The event label and the visible frame are not guaranteed to represent a post-event state.

#### Normative phase boundary

The current `message_received` image is specifically a **pre-dispatch player-view capture**: it is taken after the player submits text, while that text is still visible in the LineEdit, but before `client_request_id` creation, request-artifact dispatch, LineEdit clearing, and the `EngAIn is thinking...` state. This may be the correct request-correlated perception phase, but it must not remain implicit. Before implementation, Workload 2 must either:

1. adopt and name this exact phase as the canonical request perception phase; or
2. authorize a different phase and define how its pixels, structured state, timestamps, and request identities are correlated.

Until that decision is frozen, `message_received` means only **pre-dispatch player view**. It must not be described as a post-dispatch, request-in-flight, or settled response view.

The current `ai_dragon_spoke` image is specifically a **pre-display response capture**. Because the capture occurs before `speech_label.text = text`, it does not show the resulting response even though its paired JSON contains that response text. It must not be reused as visual evidence that the response appeared on screen. A later proof of the resulting response requires a separately defined post-display/settled capture, or must omit any claim that the response was visibly rendered.

For player messages, `EngAInDragon.gd:46-48` captures before:

- generating `client_request_id` (`:58-61`);
- marking the request active;
- writing the request file (`:67-69`);
- clearing the LineEdit and setting `EngAIn is thinking...` (`:70-72`).

This explains why message snapshots include the typed command.

For dragon responses, `EngAInDragon.gd:279-285` captures `ai_dragon_spoke` before assigning the new speech text to the visible label at `:287-288`.

This explains why the latest paired metadata says the dragon spoke a timeout response while the captured image still shows the prior `awaits your input` label and `EngAIn is thinking...` placeholder.

A later proof must define whether perception is intended to represent pre-submit, request-in-flight, response-pre-display, or settled post-display state. Current samples do not encode that phase.

For avoidance of doubt, retained `ai_dragon_spoke` PNGs are admissible only as evidence of the viewport immediately before the new speech label was assigned. Their metadata may evidence which response triggered capture, but metadata text cannot upgrade the PNG into post-response visual evidence.

### 4.3 Retained sample SHA-256 values

PNG:

```text
ebe15a8f54a000b50a3939471b55bfea87f6d6648ddaaedc32210706ce485125  low_ai_dragon_spoke_2026-07-31T06_50_50.png
2d665b061259819c06fdc794c74f394f5a7b54442e57d4ce765a6bb48b4c86b0  low_ai_dragon_spoke_2026-07-31T06_51_14.png
7f95a5d2223d10d8dfa5e435451c0a85b1e7ffb65514dc1b5609961925de9c3f  low_ai_dragon_spoke_2026-07-31T06_52_10.png
788d701c19acc4a0ba5b1112a40c2ec08285c6ab3870fd10f45f117ca8fc08ec  low_ai_dragon_spoke_2026-07-31T06_52_57.png
ffb38bb39bc2c8851549f1a674bff5089e8d8aa9d4248f55ac0430c53b1d5e7b  low_message_received_2026-07-31T06_48_02.png
d5c2b67ff1be2fcc8f4fba25150022691bf86829d3ff3685ce6d2c4870b5a76d  low_message_received_2026-07-31T06_51_45.png
6f1b3f4aceee49491e24046fadcc9abe8097d708ec36d5304dbbdbece8567268  low_message_received_2026-07-31T06_52_26.png
```

JSON:

```text
43ae68f5cc655cd035c2439bdee1d88d215f4a230098fd39e44af28455b815d7  low_ai_dragon_spoke_2026-07-31T06_50_50.json
e49fa8b51ef119b335eac84c2a6ede0cdf9c9e165acc626d6d8d2844c84cc87e  low_ai_dragon_spoke_2026-07-31T06_51_14.json
742cd8119e313157c96ae38b1ed3ffa11a4cd7a21bdbde456e84af4005384a08  low_ai_dragon_spoke_2026-07-31T06_52_10.json
f452173f17e309e3c99c9f9a0164ded2cf9c412287e66aeedea3a7a2c9bcc280  low_ai_dragon_spoke_2026-07-31T06_52_57.json
cc17eb814569f2ac4a5433b44390c910606e9ca06b2243b408304c0432b6c360  low_message_received_2026-07-31T06_48_02.json
203363ce8bd901c9b9a18fa353ecbd34d7f1ecfedbc858519e0b2a276b920c7c  low_message_received_2026-07-31T06_51_45.json
d68282033f940b7c92c09dcb0a8f57b90d60c7c52f6bc08b13e940dd7dbf7267  low_message_received_2026-07-31T06_52_26.json
```

## 5. Actual request/response route

### 5.1 Godot request creation

`EngAInDragon.gd:32-72`:

```text
LineEdit.text_submitted
→ trim and validate player text
→ capture message_received snapshot
→ generate Dragon client_request_id
→ construct additional_context
→ EngAInBridge.send_to_engain(player_input, additional_context)
```

Current `additional_context` contains:

- `client_request_id`;
- Boolean `visual_snapshots_available`;
- hard-coded `recent_visual_events = ["dragon_flight", "energy_streams", "crowd_activity"]`.

It does not contain an image path, JSON path, snapshot ID, image timestamp, image hash, or current structured snapshot.

`EngAInBridge.gd:72-119` creates:

```json
{
  "player_input": "...",
  "game_state": {},
  "additional_context": {},
  "timestamp": 0.0,
  "request_id": "req_<unix-time-with-underscore>"
}
```

It writes directly to:

`/mnt/data-drive/engain_avatar/engain_request.json`

The Bridge has no atomic temporary-file/rename protocol. The adapter compensates by requiring two identical bounded reads before parsing.

### 5.2 Adapter consumption

`hermes_session_adapter.py:348-432`:

```text
poll fixed request path
→ reject symlink
→ perform two identical bounded reads
→ strict JSON parse
→ validate request
→ reject duplicate request_id
→ director_bridge.process_player_input(player_input, game_state)
→ sanitize to read-only observational response
→ atomic-write engain_response.json
→ save session state
→ remove request only if bytes are unchanged
```

`_validate_request()` at `:435-468` validates `additional_context` but extracts only `client_request_id`. All other context is discarded. Thus the current `visual_snapshots_available` and `recent_visual_events` fields never reach Hermes B.

`hermes_session_adapter.py:470-494` forces responses to:

- `action_type = OBSERVATION`;
- `state_changes = {}`;
- `entropy_impact = 0.0`.

### 5.3 Hermes invocation

`HermesCLIClient.chat()` at `hermes_session_adapter.py:164-223` currently invokes:

```text
hermes chat
  -Q
  --source tool
  --pass-session-id
  --ignore-rules
  -t __engain_text_only_no_tools_v1__
  --provider openai-codex
  -m gpt-5.6-sol
  --resume 20260731_065008_63a62d
  -q <formatted text prompt>
```

The exact `--resume` argument is included only after the adapter loads persisted state. The adapter enforces that Hermes returns the same session ID; a different returned ID is an error (`:214-222`).

The current command contains no `--image` argument.

### 5.4 Response consumption

The adapter atomically writes:

`/mnt/data-drive/engain_avatar/engain_response.json`

`EngAInBridge.gd:148-194` polls every 0.1 seconds, parses the file, accepts only a newer response timestamp, removes the response file, processes the decision, and emits `ai_decision_received`.

`EngAInDragon.gd:181-218` then requires:

- matching active `client_request_id`;
- non-empty narrative text;
- `action_type == OBSERVATION`;
- empty `state_changes`;
- zero `entropy_impact`.

Only then does it call `dragon_speak()`.

No `engain_request.json` or `engain_response.json` was retained at discovery completion. This is consistent with the route consuming and removing both artifacts. `engain_memory.db` remains present and is separate from Hermes session persistence.

## 6. Actual Hermes B session persistence

Persisted adapter state:

`/mnt/data-drive/engain_avatar/.godot/engain_hermes_session.json`

Exact content discovered:

```json
{
  "session_id": "20260731_065008_63a62d",
  "processed_request_ids": [
    "req_1785505682_81097",
    "req_1785505835_69897",
    "req_1785505860_89973",
    "req_1785505905_48308",
    "req_1785505947_11863"
  ]
}
```

SHA-256:

```text
3e5c70ccbf6afdd2383fd64ee96e295e089433850efa94a62114e00389e4db7b
```

Mechanism:

1. `AdapterConfig` defaults the state file to `.godot/engain_hermes_session.json` (`hermes_session_adapter.py:99-128`).
2. `_load_state()` validates size/type and assigns the stored ID to `self.client.session_id` (`:514-536`).
3. `HermesCLIClient.chat()` adds `--resume <session_id>` (`:186-188`).
4. Hermes resolves that session through its session database and restores its recorded conversation/workspace.
5. The adapter parses `session_id:` from Hermes stderr and rejects identity drift (`:214-222`).
6. `_save_state()` atomically persists the session ID and bounded processed-request list (`:538-545`).

Read-only session-history inspection confirmed:

- session: `20260731_065008_63a62d`;
- source: `tool`;
- model: `gpt-5.6-sol`;
- message count: 10, representing five user/assistant exchanges;
- the exact token was retained and recalled across turns.

The last retained user turn asked `describe what you see`. The answer described an invented thought-bridge, dead timelines, dragons, and towers. The session message contained text only and no image attachment. That answer is not evidence of viewport perception.

## 7. Actual viewport-capture options

### Supported now

1. `SnapshotManager.capture_snapshot(...)` can capture the live scene viewport and return relative PNG/JSON paths.
2. `SnapshotManager.capture_event(...)` can trigger the same capture, but currently hides the result.
3. Direct Godot viewport capture uses the supported Godot 4 route:

```text
get_viewport()
→ get_texture()
→ get_image()
→ Image.save_png(path)
```

4. The retained PNGs prove this route produced real viewport pixels.

### Not currently available

There is no current API that:

- returns the most recent valid pair;
- returns a fresh pair from `capture_event()`;
- associates a capture with EngAIn request identity;
- distinguishes capture phases;
- verifies image and metadata bytes are complete before request dispatch;
- includes image hash or immutable capture identity;
- reports capture failure to the Dragon request path;
- bypasses the priority-wide 15-second LOW cooldown for an explicitly requested perception turn.

The current auto-purge method is a stub, but emergency purge can delete old PNG/JSON pairs. Later code cannot assume a referenced path will remain indefinitely.

## 8. Static trace of native `openai-codex / gpt-5.6-sol` image input

Installed Hermes source root:

`/home/mytruelove/.hermes/hermes-agent`

Hermes Git identity during discovery:

```text
HEAD=0a2c245cd6af3dfcdde3f61077f7429bb9c8a48a
TREE=e7cb876680d51047e2bc3794816d0d0f89dcd063
```

The Hermes worktree already had a modified `package-lock.json`; Workload 1 did not alter it.

### 8.1 CLI acceptance

`hermes chat --help` exposes:

```text
--image IMAGE    Image file to include with the query
```

`cli.py:3739-3766` handles the explicit image argument:

- resolves the attachment path;
- rejects missing files;
- rejects unsupported extensions;
- collects and deduplicates the local image path.

`cli.py:17009-17014` enters single-query mode when either query or image is present and calls `_collect_query_images()`.

### 8.2 Provider/model capability decision

The adapter explicitly selects:

```text
provider=openai-codex
model=gpt-5.6-sol
```

The current Hermes config contains:

```yaml
agent:
  image_input_mode: auto
```

`agent/models_dev.py:141-148` maps `openai-codex` to the `openai` models.dev catalog.

`agent/models_dev.py:450-485` treats `"image"` in `modalities.input` as native vision support.

The static local models.dev cache entry for `gpt-5.6-sol` records:

```json
{
  "id": "gpt-5.6-sol",
  "name": "GPT-5.6 Sol",
  "attachment": true,
  "modalities": {
    "input": ["text", "image", "pdf"],
    "output": ["text"]
  },
  "reasoning": true,
  "tool_call": true,
  "limit": {
    "context": 1050000,
    "input": 922000,
    "output": 128000
  }
}
```

`agent/image_routing.py:387-458` resolves the capability, and `:461-506` selects `native` in auto mode when capability is true.

This is a static inference from source and retained metadata, not a runtime probe.

### 8.3 Local file to native content part

In quiet mode, which the EngAIn adapter uses, `cli.py:17052-17114`:

1. calls `decide_image_input_mode()` with active provider/model;
2. if native, calls `build_native_content_parts()`;
3. passes the resulting list as `effective_query` to `run_conversation()` (`:17131-17134`).

`agent/image_routing.py:669-725`:

- reads the image bytes;
- detects MIME from bytes;
- transcodes unsupported formats to PNG when possible;
- base64-encodes local bytes;
- constructs `data:<mime>;base64,<bytes>`.

`agent/image_routing.py:728-814` then constructs:

```json
[
  {
    "type": "text",
    "text": "<player text>\n\n[Image attached at: <path>]"
  },
  {
    "type": "image_url",
    "image_url": {
      "url": "data:image/png;base64,<actual image bytes>"
    }
  }
]
```

This is genuine byte attachment. It is not a filepath merely mentioned in text.

### 8.4 Provider selection

`hermes_cli/providers.py:62-65` defines:

```text
openai-codex
transport=codex_responses
auth_type=oauth_external
base_url=https://chatgpt.com/backend-api/codex
```

`hermes_cli/runtime_provider.py:429-431` forces `api_mode = codex_responses` for `openai-codex`.

`agent/transports/codex.py:591-594` registers `ResponsesApiTransport` for `codex_responses`.

### 8.5 `input_image` request emission

`agent/codex_responses_adapter.py:79-127` converts a chat-style image part:

```json
{
  "type": "image_url",
  "image_url": {"url": "data:image/png;base64,..."}
}
```

into a Responses API part:

```json
{
  "type": "input_image",
  "image_url": "data:image/png;base64,..."
}
```

`agent/codex_responses_adapter.py:555-560` preserves the multimodal parts in the user input item.

`agent/transports/codex.py:301-312` builds provider kwargs containing:

```json
{
  "model": "gpt-5.6-sol",
  "input": [
    {
      "role": "user",
      "content": [
        {"type": "input_text", "text": "..."},
        {"type": "input_image", "image_url": "data:image/png;base64,..."}
      ]
    }
  ],
  "store": false
}
```

`agent/codex_runtime.py:1213-1253` submits those kwargs through:

```text
active_client.responses.create(**stream_kwargs)
```

with `stream=True` added.

Static source therefore reaches genuine Responses API `input_image` emission.

### 8.6 Same-session compatibility boundary

The CLI accepts `--resume` and `--image` in the same invocation path. Source contains no guard forbidding a multimodal user message in a resumed session, and prior user/assistant history is converted before the new multimodal item.

However, Workload 1 did not invoke that combination. It remains unresolved whether the active authenticated backend will accept the exact retained PNG on the exact resumed Hermes B session under real runtime conditions.

## 9. Supported boundaries

Static and retained evidence supports all of the following:

1. The existing file-based request/response transport can remain in place.
2. The exact Hermes B session identity is persisted and resumed.
3. The adapter checks for provider-session identity drift.
4. SnapshotManager can produce real PNG captures of the active Godot scene viewport.
5. SnapshotManager can produce paired structured JSON metadata.
6. The installed Hermes CLI accepts a local image path through `--image`.
7. Local image bytes are encoded as a data URL, not merely mentioned in text.
8. `openai-codex` selects the Codex Responses transport.
9. Static capability data marks `gpt-5.6-sol` as accepting image input.
10. The active auto routing logic therefore has a native path.
11. The Codex adapter emits a native Responses `input_image` part.
12. The Responses transport submits that multimodal input through `client.responses.create()`.
13. Godot already rejects state-mutating responses at the Dragon boundary, and the adapter sanitizes them to observation-only responses.
14. GodotOllama is not required for the runtime perception proof.

## 10. Unsupported boundaries and unresolved facts

### 10.1 Unsupported in the current EngAIn route

1. The current adapter is explicitly text-only.
2. It does not pass `--image`.
3. It discards all `additional_context` except `client_request_id`.
4. It passes no structured SnapshotManager state to Hermes B.
5. It passes no PNG pathname to Hermes B.
6. It records no image/capture correlation in the response.
7. `capture_event()` does not return its captured paths or failure.
8. Snapshot metadata lacks both request identities and Hermes session identity.
9. Snapshot metadata lacks project identity and image hash.
10. LOW-priority cooldown can silently suppress a perception capture.
11. Snapshot event names describe requested events, not necessarily settled on-screen state.
12. `visual_analysis` is templated text, not pixel analysis.
13. Hard-coded `recent_visual_events` are not observed evidence.
14. The current EngAIn director prompt ignores arbitrary extra Godot state; `engain_dolphin.py:247-268` selects only a narrow `GameState` projection.
15. A historical text-only `describe what you see` answer hallucinated scene facts and must not be treated as visual proof.

### 10.2 Unresolved until later authorized runtime proof

1. Actual backend acceptance of `input_image` for this authenticated `openai-codex` account.
2. Actual backend acceptance for `gpt-5.6-sol` at invocation time.
3. Actual acceptance of an image-bearing turn while resuming session `20260731_065008_63a62d`.
4. Real latency relative to the adapter's 30-second timeout and Dragon's 50-second timeout.
5. Whether full-size ~1.3 MB PNGs are accepted without reactive resize/retry.
6. Whether the model accurately grounds its answer in these particular viewport pixels.
7. Whether a changed viewport produces a materially changed answer.
8. Whether no-image and stale-image failures produce honest denial.
9. Whether memory continuity remains intact after an image-bearing turn.
10. Exact test-artifact path: the project currently has no existing test tree or test-file convention.

## 11. Prospective later implementation ownership

This is discovery only, not an edit authorization or a frozen Workload 2 allowlist.

The smallest prospective existing-file surface is:

1. `/mnt/data-drive/engain_avatar/addons/zwengain/scenes/SnapshotManager.gd`
   - expose fresh capture result/failure;
   - provide deterministic capture identity/timestamps and paired paths;
   - make explicit-perception capture semantics separate from generic event cooldown.

2. `/mnt/data-drive/engain_avatar/addons/zwengain/scripts/EngAInDragon.gd`
   - request a precisely timed perception capture;
   - associate it with `client_request_id`;
   - pass the perception envelope into the existing bridge;
   - fail closed when perception is unavailable.

3. `/mnt/data-drive/engain_avatar/addons/zwengain/scripts/EngAInBridge.gd`
   - associate the internally generated request ID with the same perception envelope;
   - serialize bounded structured perception fields and paths through the existing JSON request artifact;
   - preserve the current file transport.

4. `/mnt/data-drive/engain_avatar/hermes_session_adapter.py`
   - validate bounded perception schema and path containment;
   - verify fresh/correlated PNG+JSON artifacts;
   - preserve/resume the same session;
   - add the supported `--image <path>` invocation;
   - include structured current state in the same user turn;
   - propagate provenance and fail closed.

Conditional only, not yet established as necessary:

5. `/mnt/data-drive/engain_avatar/engain_dolphin.py`
   - needed only if Workload 2 chooses to make the legacy director prompt, rather than the adapter's Hermes turn envelope, own structured-perception presentation.

No static evidence requires later ownership of:

- `project.godot`;
- `EngAInDragon.tscn`;
- `dynamiccontextmanager.gd`;
- `VisionAgent.py`;
- `zw_file_bridge.py`;
- any GodotOllama file.

`VisionAgent.py` is an Ollama placeholder/template lane and does not establish genuine image ingestion. It should not be reused as proof.

Workload 2 must freeze the final allowlist and exact test paths before any implementation edit.

## 12. Mandatory stop conditions

A later workload must stop without substituting a weaker proof if any of the following occurs:

1. The actual authenticated provider rejects native image input.
2. `gpt-5.6-sol` rejects `input_image` at runtime.
3. Hermes routes the image through text-only auxiliary description instead of native input when native input is required.
4. The resumed session cannot accept an image-bearing turn without creating a replacement session.
5. Hermes returns a different session identity.
6. The implementation would need to replace the proven JSON file bridge with HTTP or another transport.
7. A filepath would be mentioned in text without actual image-byte ingestion.
8. Snapshot capture returns no fresh PNG/JSON pair.
9. Snapshot cooldown suppresses capture and the request cannot honestly report perception unavailable.
10. PNG and JSON cannot be proven to belong to the same capture.
11. Snapshot and EngAIn request identities cannot be correlated.
12. The image is stale, missing, symlinked, outside the project-owned snapshot area, changed after validation, or unreadable.
13. Structured state and image timestamps cannot be associated with the same request.
14. The capture phase is ambiguous enough to misstate what was currently displayed.
15. Templated `visual_analysis` or hard-coded event labels would be passed as observed image facts.
16. The route introduces runtime/world mutation.
17. The Dragon's existing read-only response gate would need to be weakened.
18. GodotOllama would need modification.
19. Credentials would need to be copied, preserved, or embedded.
20. A full-size or transformed image cannot be tied back to its source capture.
21. Runtime proof cannot distinguish image-observed, structured-state, remembered, and unavailable facts.
22. Tests cannot demonstrate honest denial for missing/stale/unmatched perception.

## 13. Source byte identities

Project sources inspected:

```text
d8c1eb40710fe8050922d7bc497ce56692a2f97b55f5967f7ed6e28542548b2b  addons/zwengain/scenes/SnapshotManager.gd
89976b7dd04bcab1fd44520f9be8151da7e94121b5b8aee8ca1927c4cdc84840  addons/zwengain/scripts/EngAInBridge.gd
34d84f4536671b6e0b8118ee91e756142f9c31c02f8598775f98e838f7289bc9  addons/zwengain/scripts/EngAInDragon.gd
871d36d2c3dc80968fbe9a4161557bb3b498228aa0fbdc3c5ec495b4fbf8d95a  addons/zwengain/scenes/EngAInDragon.tscn
7828bdf556f2b16748dc1b11cf32bf64bba16f5c70908b7b5a05387dafac2355  hermes_session_adapter.py
2e93866bb05c43d31b050988f187e1359db9c9e0a2bf0b0c6dbedea24617dff2  engain_dolphin.py
3e5c70ccbf6afdd2383fd64ee96e295e089433850efa94a62114e00389e4db7b  .godot/engain_hermes_session.json
```

Installed Hermes sources inspected:

```text
4fa3fa0eb8fdabd000dc5762253b6e18698c9fc838567a72912041075ba8472e  cli.py
6948274fae2f6f48722df3a6dbe453899e4e0c1892cd2317e175ec5f10ead5b8  agent/image_routing.py
bc68a199e808893f57e3fefbd3548927622dfc211e6fa7f9c08ed8988dbc4b89  agent/models_dev.py
5b9863ccc4de5404f603cf5b7239d21fd29784e572461d60e8f3f38c811e2ec8  hermes_cli/providers.py
9d231462efe413630bfa55a1d21b9511b873655a304ae3142972fbde8d79e852  hermes_cli/runtime_provider.py
4608e8217d5917ec739cdec93ece3323ebcd868286c142e38973b26bc6520d3e  agent/codex_responses_adapter.py
db1bf2aab07897c8d2fca1c3f21ce2fd3c555047c53cc72e4adb44dd6a2834a4  agent/transports/codex.py
8f8359a0e6c87d3b914df18be97af586d2719f32e134dd5d51c9f0ee77223919  agent/codex_runtime.py
0bf7e7ed25ba8988e2e684b7790e34d9ed36408451f582d5aac5b3de6fe2bb95  /home/mytruelove/.hermes/models_dev_cache.json
```

## 14. Final repository state

### `/mnt/data-drive/engain_avatar`

```text
## main...origin/main [ahead 1]
 M addons/zwengain/scenes/idle_flap.png.import
 M addons/zwengain/scenes/idol_flap.png.import
 M assets/generation-6c5f80d1-6b4f-4b28-819b-9fcce84b0f25.png.import
 M assets/generation-6d2a77ce-fe3b-4b62-a899-c9d4c258d1f7(2).png.import
 M icon.svg.import
 M project.godot
HEAD=f00ff0424f714726f024c0d763b741f61dfc8178
TREE=2e8d83408d435e06277b38b2e0925bbf90915d3e
```

### `/mnt/data-drive/godotollama`

```text
## main...origin/main [ahead 7]
 M trixel_proof/screenshot_trixel_profile_broad_terraces.png
?? blender_proof/trixel32d_complete_edge/output/trixel32d_complete_edge_beauty.png.import
?? blender_proof/trixel32d_complete_edge/output/trixel32d_complete_edge_diagnostic.blend.import
?? blender_proof/trixel32d_complete_edge/output/trixel32d_complete_edge_wireframe.png.import
?? blender_proof/trixel32d_complete_edge/output_stone/trixel32d_complete_edge_beauty.png.import
?? blender_proof/trixel32d_complete_edge/output_stone/trixel32d_complete_edge_diagnostic.blend.import
?? blender_proof/trixel32d_complete_edge/output_stone/trixel32d_complete_edge_wireframe.png.import
?? docs/AGENT_PORTAL_CONTINUATION_TODO.md
?? docs/AGENT_PORTAL_EDITOR_PILOT_AUDIT_2026-07-31.md
?? trixel_proof/pyroclast/godot/pyroclast_field_consumer.gd.uid
?? trixel_proof/pyroclast/screenshots/pyroclast_field_8x8.png.import
?? trixel_proof/pyroclast/screenshots/pyroclast_one_patch.png.import
?? trixel_proof/trixel32d_apply_executor/diagnostics/trixel32d_apply_executor_visual_harness.gd.uid
?? trixel_proof/trixel32d_apply_executor/diagnostics/trixel32d_dual_slab_visual_harness.gd
?? trixel_proof/trixel32d_apply_executor/diagnostics/trixel32d_dual_slab_visual_harness.gd.uid
?? trixel_proof/trixel32d_apply_executor/diagnostics/trixel32d_turntable_harness.gd.uid
?? trixel_proof/trixel32d_apply_executor/fixtures/trixel32d_apply_authorization_stone_complete_edge.json
?? trixel_proof/trixel32d_apply_executor/fixtures/trixel32d_apply_authorization_ticket_a_grass_complete_edge.json
?? trixel_proof/trixel32d_apply_executor/fixtures/trixel32d_apply_authorization_ticket_a_stone_complete_edge.json
?? trixel_proof/trixel32d_apply_executor/godot/trixel32d_apply_executor.gd.uid
?? trixel_proof/trixel32d_apply_executor/screenshots/dual_slab/trixel32d_dual_slab_complete_edge.png.import
?? trixel_proof/trixel32d_apply_executor/screenshots/trixel32d_apply_executor_complete_edge.png.import
?? trixel_proof/trixel32d_apply_executor/screenshots/turntable/turntable_az000.png.import
?? trixel_proof/trixel32d_apply_executor/screenshots/turntable/turntable_az045.png.import
?? trixel_proof/trixel32d_apply_executor/screenshots/turntable/turntable_az090.png.import
?? trixel_proof/trixel32d_apply_executor/screenshots/turntable/turntable_az135.png.import
?? trixel_proof/trixel32d_apply_executor/screenshots/turntable/turntable_az180.png.import
?? trixel_proof/trixel32d_apply_executor/screenshots/turntable/turntable_az225.png.import
?? trixel_proof/trixel32d_apply_executor/screenshots/turntable/turntable_az270.png.import
?? trixel_proof/trixel32d_apply_executor/screenshots/turntable/turntable_az315.png.import
?? trixel_proof/trixel32d_apply_executor/screenshots/turntable/turntable_contact_sheet.png.import
?? trixel_proof/trixel32d_apply_executor/tests/test_trixel32d_apply_executor.gd.uid
?? trixel_proof/trixel32d_apply_executor/tests/test_trixel32d_apply_executor_dual_slab.gd.uid
?? trixel_proof/trixel32d_passive/diagnostics/trixel32d_surface_built_3x2_visual.png.import
?? trixel_proof/trixel32d_passive/diagnostics/trixel32d_surface_visual_harness.gd.uid
?? trixel_proof/trixel32d_passive/godot/trixel32d_surface_consumer.gd.uid
?? trixel_proof/trixel32d_passive/tests/test_trixel32d_surface_consumer.gd.uid
?? trixel_proof/trixel32d_passive/tests/test_trixel32d_surface_visual_harness.gd.uid
?? trixel_proof/trixel32d_runtime/README.md
?? trixel_proof/trixel32d_runtime/godot/trixel32d_runtime_attacher.gd
?? trixel_proof/trixel32d_runtime/godot/trixel32d_runtime_attacher.gd.uid
?? trixel_proof/trixel32d_runtime/tests/test_trixel32d_runtime_attachment.gd
?? trixel_proof/trixel32d_runtime/tests/test_trixel32d_runtime_attachment.gd.uid
HEAD=610499af117a743cd4ce0159c6cdd7a856e49e00
TREE=e4ef86600d745d36f3b70e5cf0e1a09bdf50317f
```

The dirty/untracked states above pre-existed Workload 1 and were not altered by it.

## 15. Workload boundary

Workload 1 ends here.

No Workload 2 schema, allowlist, test plan, implementation, source edit, provider invocation, runtime proof, GodotOllama change, commit, or push was performed.
