# EngAIn Avatar Preservation-First Archaeological Audit

Audit date: 2026-07-30

Repository requested: `/mnt/data-drive/engain-avatar`

Repository actually inspected, after explicit user approval of the underscore-path correction: `/mnt/data-drive/engain_avatar`

Audit artifacts: `/mnt/data-drive/engain-avatar-audit/`

No implementation, repair, cleanup, reset, commit, rename, bridge replacement, scene mutation, permission system, canon system, or generalized agent protocol was created.

## Baseline

Exact baseline command result:

```text
$ git status --short --untracked-files=all
<empty>
$ git rev-parse HEAD
22b0ffdf16c014da8aaf7760a031c5ae6788e9cd
$ git branch --show-current
main
```

The repository began clean. See `logs/baseline-git.txt` and `logs/baseline-tracked.sha256`.

## A. Current project run status

### Headless editor import/parse check

Command:

```text
godot --headless --path /mnt/data-drive/engain_avatar --editor --quit
```

Installed executable and version:

```text
/home/mytruelove/.local/bin/godot
Godot 4.6.1.stable.official.14d19694e
```

Result: **PASS**, exit status 0. Godot registered `DynamicContextManager` and `SnapshotManager`, initialized the enabled plugin, scanned the project, and imported all five image assets. It emitted no GDScript parse errors or warnings. Exact output is in `logs/godot-editor-import.log`.

### Bounded main-scene start

Command:

```text
timeout --signal=TERM --kill-after=3s 12s godot --headless --path /mnt/data-drive/engain_avatar
```

Result: **STARTS AND REMAINS RUNNING**. The process reached the configured scene and was deliberately terminated by the 12-second bound (`timeout` status 124). It emitted no runtime errors or warnings during that interval.

Observed startup evidence:

```text
EventBus: ZW Protocol event system ready
🧠 EngAIn Bridge: Ready for AI co-direction
📡 Communication channel: JSON file exchange
✅ Found EngAIn bridge at: EngAInBridge
✅ EngAIn bridge connected!
🧠 Connected to EngAIn AI Co-Director
📸 SnapshotManager connected for visual context
🌟 World event triggered: session_started
🐉 EngAIn Dragon: AI Co-Director integration ready!
SnapshotManager: Snapshots saved to: /mnt/data-drive/engain_avatar/snapshots/
SnapshotManager: Connected to EventBus
DynamicContextManager: Found SnapshotManager at: /root/Node2D/SnapshotManager
DynamicContextManager: Ready to replace static templates!
```

Exact output is in `logs/godot-main-scene.log`.

Important qualification: the project starts, but the typed conversational path does **not** return an AI response. Startup success is not conversational-loop success.

The required import command also caused Godot 4.6.1 to update five tracked Godot `.import` metadata files and create ignored `.godot/` cache plus an empty ignored `snapshots/` directory. No cleanup or reset was performed because the audit instructions prohibited it. Details are in section I.

## B. Exact existing architecture

### Project entry and scene tree

`project.godot:14` sets `run/main_scene="uid://dyw0rrveeb13w"`. That UID is declared by `addons/zwengain/scenes/EngAInDragon.tscn:1`; therefore `EngAInDragon.tscn` is both the configured main scene and the scene that is instantiated at startup.

The active scene tree is:

```text
Node2D                                      EngAInDragon.tscn root
├── Sprite2D                               background image
├── CharacterBody2D                        dragon body
│   ├── AnimatedSprite2D                   idle_flap frames
│   ├── CollisionShape2D
│   ├── Label                              dragon-visible text
│   └── EngAInBridge                       active bridge node
├── LineEdit                               typed interaction surface
├── SnapshotManager                        screenshot/metadata manager
└── DynamicContextManager                  snapshot-metadata context reader
```

Exact script attachments:

- `CharacterBody2D` → `res://addons/zwengain/scripts/EngAInDragon.gd` (`EngAInDragon.tscn:199-201`).
- `CharacterBody2D/EngAInBridge` → `res://addons/zwengain/scripts/EngAInBridge.gd` (`EngAInDragon.tscn:223-224`).
- root `SnapshotManager` → `res://addons/zwengain/scenes/SnapshotManager.gd` (`EngAInDragon.tscn:234-235`).
- root `DynamicContextManager` → `res://addons/zwengain/scenes/dynamiccontextmanager.gd` (`EngAInDragon.tscn:237-238`).
- `LineEdit.text_submitted` → `CharacterBody2D._on_line_edit_text_submitted` (`EngAInDragon.tscn:240`).

`addons/zwengain/scripts/animated_sprite_2d.gd` is not attached to `AnimatedSprite2D`; animation is started directly by `EngAInDragon.gd:_ready()`.

### Which bridge is active, and why there are two

The active implementation is:

```text
addons/zwengain/scripts/EngAInBridge.gd
```

It is attached to the `EngAInBridge` child in the main scene and its `_ready()` output was observed during runtime.

The second file is:

```text
addons/zwengain/scenes/engainbridge.gd
```

It contains only `extends Node`, has no class, signals, methods, scene attachment, or textual consumer. It is unused. The repository contains no evidence explaining why both files were retained; the most supportable classification is an empty duplicate/placeholder superseded by the scripts-side implementation. Chronology or authorial intent remains unknown.

### Autoloads and editor plugin

There is one autoload:

```text
EventBus="*res://addons/zwengain/scripts/EventBus.gd"
```

The project enables `addons/zwengain/plugin.cfg`, which points to `zw_engine_plugin.gd`. The editor plugin enters successfully but `_enter_tree()` and `_exit_tree()` are no-ops.

### Signals and event connectivity

Actual signal connections:

1. Scene-declared `LineEdit.text_submitted` → `EngAInDragon._on_line_edit_text_submitted`.
2. Runtime `EngAInBridge.ai_decision_received` → `EngAInDragon._on_ai_decision` in `EngAInDragon.gd:127-130`.
3. Internal timers:
   - `EngAInBridge.file_watcher_timer.timeout` → `_check_for_ai_response` every 0.1 seconds.
   - dragon timeout timer → `_on_ai_timeout` after 10 seconds.
   - `SnapshotManager.purge_timer.timeout` → `_auto_purge_snapshots` every 300 seconds.
   - `DynamicContextManager.context_update_timer.timeout` → `_update_context_from_visuals` every 30 seconds.

`EventBus.gd` declares nine signals, but no file emits or connects any of them. `SnapshotManager._connect_to_systems()` merely resolves `/root/EventBus` and prints “Connected”; it performs no `.connect(...)` call. `DynamicContextManager.context_updated` is emitted but has no consumer. `EngAInBridge.state_sync_complete` is declared but never emitted or connected.

### Existing transports

#### Active Godot bridge transport

`addons/zwengain/scripts/EngAInBridge.gd` implements current-working-directory JSON file exchange:

```text
engain_request.json  Godot writes; Python is expected to consume/remove
engain_response.json Python writes; Godot polls every 100 ms
```

Request fields are `player_input`, deep-copied `game_state`, `additional_context`, `timestamp`, and `request_id`. Response fields expected by the active route include `timestamp`, `action_type`, `reasoning`, `state_changes`, `entropy_impact`, and `narrative_response`.

The files are relative names, not `res://`/`user://` paths. The code prints a project-globalized path but passes only the relative filename to `FileAccess.open`. Python also uses relative paths. Consequently the transport depends on Godot and Python being launched with the same current working directory. There are no locks, atomic rename, request/response correlation on receipt, replay handling, session ID, or environment-variable path override. `DirAccess.remove_absolute(engain_response_file)` is given a relative filename and its return value is not checked.

#### `zw_file_bridge.py` transport

`zw_file_bridge.py:171-213` implements a different polling file protocol:

```text
godot_command.txt  Python polls every 100 ms, reads, then removes
python_response.json Python writes narrative/world-state JSON
snapshots/           Python searches for the latest PNG
```

No Godot file writes `godot_command.txt` or reads `python_response.json`. This transport is therefore not connected to the active scene. It also has no socket, port, subprocess, environment-variable configuration, lock, request ID, or receipt. It is an alternate present-but-unwired integration lane.

### Does Godot launch or communicate with Python?

No Godot code launches Python. The repository contains no `OS.execute`, `OS.create_process`, subprocess invocation, executable path, socket client, or Python lifecycle manager.

Godot has two attempted communication lanes:

1. The active `EngAInBridge.gd` file protocol, but only methods such as F10/manual API calls currently invoke `send_to_engain`.
2. `EngAInDragon.send_to_ai_director()` posts `{"input": ...}` to hard-coded `http://localhost:5000/engain`. It does not connect `HTTPRequest.request_completed`, inspect the request-start error, or process a response. No Python file in the repository implements an HTTP server or port 5000 endpoint. A live audit probe found no listener at port 5000.

### Python-side roles

#### `engain_dolphin.py`

This is the Python counterpart compatible with the active bridge's `engain_request.json` / `engain_response.json` filenames and response shape. Its `main()` manually starts an infinite current-directory poller. `EngAInBridge.process_player_input()` converts Godot state, asks `EngAInDirector`, and writes a response. `OllamaClient` calls hard-coded `http://localhost:11434/api/chat` with hard-coded model `dolphin-mistral:latest`.

It also creates current-directory `engain_memory.db` and persists decision, game-pattern, and player-preference tables. It is not launched by Godot and contains no Hermes integration.

The machine has Ollama 0.32.1 and its API answered HTTP 200, but `dolphin-mistral:latest` is not installed. `OllamaClient.chat()` catches all request/model errors and returns a local fallback JSON; therefore `main()`'s “Ollama connection successful” message is not a reliable health check.

#### `VisionAgent.py`

This is placeholder visual-context code. `VisionAgent.analyze_local()` reads image dimensions via Pillow and returns hard-coded interface prose selected partly from the filename; no actual vision model is initialized. Cloud analysis is TODO. `VisualZWBridge` packages text and the latest snapshot into a ZW-shaped dictionary.

It is imported only by `zw_file_bridge.py`, not by active Godot or `engain_dolphin.py`. It also has a no-screenshot type defect: `get_visual_context(None)` returns a string, while `create_visual_zw_packet()` immediately indexes it as a dictionary. `zw_file_bridge.py` catches that failure and falls back to nonvisual processing.

### Snapshot persistence

`SnapshotManager.capture_snapshot()` is intended to persist:

- a viewport PNG under `snapshots/`;
- a JSON metadata record containing timestamp, event, priority, ZW packet, supplied state, retention, file size, generated `visual_analysis`, optional global-system observations, Godot version, scene path, and FPS.

It does **not** persist Hermes identity, Hermes session continuity, conversation turns, dragon/player relationship state, or canonical state. `max_snapshots` is not enforced; `_auto_purge_snapshots()` only prints; `purge_older_than_hours` is unused; emergency purge is implemented. The scene-start audit created the directory but no snapshot file, consistent with the cooldown check suppressing early low-priority captures.

`engain_dolphin.py`, separately, can persist AI decisions in SQLite when manually run. That is provider-specific decision memory, not an active dragon-session record.

### Dynamic context exposed

`DynamicContextManager` reads the lexicographically latest `snapshots/*.json`, extracts `visual_analysis`, and exposes:

```text
location
environment
interface_elements
visual_description
timestamp
```

Location/environment/interface values are keyword heuristics. It emits `context_updated` and provides `get_current_context()`, `force_context_update()`, and `get_contextual_description()`. No active bridge, dragon method, or Python process consumes this dictionary, so it does not currently reach any provider request.

### Hard-coded paths, endpoints, and content

- `http://localhost:5000/engain` in `EngAInDragon.gd`.
- `http://localhost:11434` and `dolphin-mistral:latest` in `engain_dolphin.py`.
- Current-directory `engain_request.json`, `engain_response.json`, `engain_memory.db`, `godot_command.txt`, `python_response.json`, and `snapshots/`.
- `res://snapshots/` in `SnapshotManager.gd`.
- Node paths including `../SnapshotManager`, `/root/Node2D/SnapshotManager`, `/root/SnapshotManager`, `EngAInBridge`, `../EngAInBridge`, `/root/Node2D/EngAInBridge`, and `/root/EngAInBridge`.
- Static “Cosmic Command Center,” dragon council, entropy, crowd, and interface context throughout Godot and Python.
- No repository code reads environment variables.

### Missing external dependencies or runtime prerequisites

- No Python dependency manifest or lock file exists.
- Python modules `requests`, `PIL`, `sqlite3`, `dataclasses`, and `typing` are available on this machine. Python AST parsing passed for all three `.py` files.
- README's `pip install ... sqlite3 dataclasses typing` instruction is inaccurate for modern Python because the latter modules are standard-library modules.
- Ollama is installed and reachable, but required `dolphin-mistral:latest` is absent.
- Nothing provides the port 5000 HTTP endpoint used by typed input.
- Hermes Agent v0.19.0 is installed at `/home/mytruelove/.local/bin/hermes`, but the repository contains no Hermes command, API, adapter, session ID, profile, provider configuration, or response parser.
- Godot project features name 4.4, while this audit used installed Godot 4.6.1; that version difference caused tracked `.import` metadata updates.

## C. Active data-flow diagram

### Actual typed path today

```text
LineEdit.text_submitted
  → EngAInDragon._on_line_edit_text_submitted(text)
      → SnapshotManager.capture_event("message_received", {command: text})
      → EngAInDragon.send_to_ai_director(text)
          → HTTP POST http://localhost:5000/engain
          → no server in repo / no live listener
          → no request_completed signal connection
          → response body is never consumed even if a server existed
      → LineEdit is cleared
      → placeholder becomes "EngAIn is thinking..."
      → active EngAInBridge is found
      → additional_context and fallback local variables are built
      → EngAInBridge.send_to_engain(...) is NOT called
      → waiting_for_ai is never set true
      → timeout cannot invoke visible fallback
  → STOP: no textual response reaches dragon_speak()
```

### Existing but non-typed file lane

```text
F10 or another caller of EngAInBridge.send_to_engain(...)
  → current-directory engain_request.json
  → [engain_dolphin.py must be started manually]
  → Ollama localhost:11434 / dolphin-mistral:latest
      → currently falls back because model is absent
  → engain_memory.db decision record
  → current-directory engain_response.json
  → EngAInBridge._check_for_ai_response()
  → EngAInBridge.process_ai_decision()
      → applies provider-supplied in-memory state changes and entropy
      → emits ai_decision_received
  → EngAInDragon._on_ai_decision()
  → EngAInDragon.dragon_speak(narrative_response)
  → Label.text plus sprite color tween
```

### Event/context side lanes

```text
EventBus autoload
  → signals declared
  → no emits/connections

SnapshotManager
  → snapshots/*.png + snapshots/*.json when capture passes cooldown
  → DynamicContextManager reads latest JSON every 30 seconds
  → context_updated emitted
  → no consumer

zw_file_bridge.py
  → waits for godot_command.txt
  → writes python_response.json
  → no Godot producer/consumer
```

## D. Component classification table

The classification describes current repository/runtime evidence, not filename intent.

| File/component | Purpose | Entry points | Dependencies | Consumers | Side effects | Classification | Evidence |
|---|---|---|---|---|---|---|---|
| `project.godot` | Project startup/configuration | Godot project load | Godot 4.x; referenced resources | Godot | Enables autoload/plugin; selects scene | `ACTIVE_AND_WIRED` | Main scene, autoload, and plugin all observed at runtime |
| `addons/zwengain/plugin.cfg` | Editor plugin declaration | Editor initialization | `zw_engine_plugin.gd` | Godot editor | Loads no-op plugin | `ACTIVE_AND_WIRED` | Enabled in `project.godot`; editor import initialized plugins |
| `addons/zwengain/zw_engine_plugin.gd` | Editor plugin shell | `_enter_tree`, `_exit_tree` | `EditorPlugin` | Enabled plugin config | None; both methods `pass` | `ACTIVE_AND_WIRED` | Loaded by editor, but deliberately/no-op functionally |
| `addons/zwengain/scenes/EngAInDragon.tscn` | Main dragon/UI/manager composition | Project main scene UID | Scripts and three textures | Godot startup | Instantiates complete visible scene | `ACTIVE_AND_WIRED` | UID equals configured main scene; runtime child logs prove instantiation |
| `addons/zwengain/scripts/EngAInDragon.gd` | Dragon movement, typed input, response display, bridge hookup | `_ready`, `_physics_process`, `_input`, `_on_line_edit_text_submitted`, bridge signal callback | Scene child/sibling paths; HTTPRequest; bridge/snapshot methods | Main scene `CharacterBody2D` | HTTP request, snapshots, label/sprite changes, movement | `BROKEN` | Active and visible, but typed method bypasses active bridge, has no HTTP callback/server, never sets waiting flag, and never displays a provider response |
| `addons/zwengain/scripts/EngAInBridge.gd` | JSON request/response bridge and in-memory director state | `_ready`, `send_to_engain`, timer poll, public debug/event methods | Shared cwd; external response writer; Timer/FileAccess | Dragon finds it; F10/public callers; dragon consumes signal | Writes request JSON, reads/removes response, mutates in-memory state, emits signal | `ACTIVE_AND_WIRED` | Attached node and `_ready` observed; signal connected to dragon. Typed ingress defect is in the caller, and no Hermes producer exists |
| `addons/zwengain/scenes/engainbridge.gd` | Empty alternate bridge placeholder | None beyond hypothetical node ready | Node | None | None | `SUPERSEDED_OR_DUPLICATE` | Only `extends Node`; no scene attachment or textual reference; scripts-side bridge is active |
| `addons/zwengain/scenes/SnapshotManager.gd` | Viewport PNG and event/state metadata capture | `_ready`, `capture_event`, `capture_snapshot`, F12/manual and dragon calls | Viewport, filesystem, optional `/root/Global` and other nodes | Dragon; DynamicContextManager reads outputs | Creates `snapshots/`; writes/deletes PNG/JSON; timers | `ACTIVE_AND_WIRED` | Instantiated, found by dragon/context manager, startup observed. Retention and early-cooldown behavior are incomplete but core node is active |
| `addons/zwengain/scenes/dynamiccontextmanager.gd` | Derive heuristic context from latest snapshot metadata | `_ready`, 30s timer, public getters | SnapshotManager class/node; `snapshots/*.json` | No consumer of signal/getters found | Reads JSON; emits `context_updated`; prints | `PRESENT_BUT_UNWIRED` | Instantiated and timer active, but its produced context never enters bridge/provider requests |
| `addons/zwengain/scripts/EventBus.gd` | Global ZW signal declarations | Autoload `_ready` | Godot | SnapshotManager only resolves its node | Prints only | `PRESENT_BUT_UNWIRED` | Autoload is active, but no signal is emitted or connected anywhere |
| `addons/zwengain/scripts/animated_sprite_2d.gd` | Play `idle_flap` on ready | `_ready` if attached | AnimatedSprite2D animation | None | Starts animation if instantiated | `PRESENT_BUT_UNWIRED` | Scene's AnimatedSprite2D has no script attachment; dragon script starts the same animation |
| `engain_dolphin.py` | Ollama-based AI director, file worker, SQLite memory | `main()`, `EngAInBridge.process_player_input` | Python; requests; sqlite3; Ollama; missing model; shared cwd | Compatible with active GDScript bridge only when manually launched | Network POST; creates/updates DB and response JSON; deletes request JSON | `PRESENT_BUT_UNWIRED` | Protocol shape matches active bridge, but Godot never launches it; no process was active; required model absent; no Hermes support |
| `VisionAgent.py` | Placeholder screenshot description and ZW context packet | Class methods; standalone test main | Pillow; filesystem; optional future APIs | Only `zw_file_bridge.py` | Reads images/mtimes; prints tests | `PRESENT_BUT_UNWIRED` | Not in active bridge lane; actual vision is TODO; no-screenshot return shape is defective |
| `zw_file_bridge.py` | Alternate symbolic/narrative file poller with optional placeholder vision | `main()` infinite poller | `VisionAgent.py`; shared cwd | No Godot consumer/producer | Reads/deletes command text; writes response JSON; in-memory symbolic mutation | `PRESENT_BUT_UNWIRED` | Uses filenames/schema that no Godot file uses; not launched by Godot |
| Tracked `*.gd.uid`, `*.import` and ignored `.godot/**` | Godot identity/import/editor metadata | Godot scan/import | Godot version/importer | Godot editor/runtime | Cache/metadata generation and version updates | `GENERATED_OR_CACHE` | Not implementation truth; 4.6 import created cache and updated five `.import` files |
| `snapshots/` | Runtime screenshot/metadata destination | SnapshotManager startup/capture | Writable project directory | DynamicContextManager/Python candidates | Directory and possible PNG/JSON writes | `GENERATED_OR_CACHE` | Ignored in `.gitignore`; created empty during bounded run |

No relevant hand-authored file remains `UNKNOWN`. The reason for retaining the blank duplicate bridge is historically unknown, but its current connectivity is proven absent.

## E. Missing conversational link

The single absent component is a **Hermes session worker/adapter that consumes the existing active bridge request and returns a bridge-compatible textual response while retaining a Hermes session identifier**.

That is not a new generalized protocol and need not embed the Hermes TUI. Hermes can remain an external process. Installed CLI evidence shows one-shot input via `hermes chat -q`, quiet programmatic output via `-Q`, and continuity via `--resume SESSION_ID` or `--continue`.

One existing defect must also be repaired: `EngAInDragon._on_line_edit_text_submitted()` must call its already-instantiated `EngAInBridge.send_to_engain(text, additional_context)` rather than firing the dead port-5000 request and discarding the active bridge path. This is a narrow caller repair, not a new architecture.

Everything after the active bridge's `ai_decision_received` signal already exists for textual embodiment: `_on_ai_decision()` extracts `narrative_response`, calls `dragon_speak()`, changes the visible `Label`, and animates the sprite color.

## F. Smallest implementation work unit

A future, separately authorized work unit should do only this:

1. Repair the typed-input caller so the submitted text is passed unchanged to the existing `CharacterBody2D/EngAInBridge.send_to_engain()` before the LineEdit is cleared; set/clear `waiting_for_ai` consistently and stop using the dead unhandled port-5000 request for this path.
2. Add one external Hermes-specific worker that watches the existing `engain_request.json`, submits `player_input` to Hermes, stores/reuses the returned Hermes session ID, and writes only the fields the existing Godot response/display path needs—at minimum `timestamp`, `narrative_response`, and a non-mutating conversational `action_type`.
3. Do not enable existing provider-supplied `state_changes`, entropy changes, scene tools, file tools, canon effects, permissions, snapshots-as-canon, or world mutation in this work unit.
4. Start the worker externally for the proof; do not add Godot process ownership yet.

Components that can remain unchanged for this proof:

- `project.godot`
- `EngAInDragon.tscn`
- active `scripts/EngAInBridge.gd` file transport and response signal
- dragon `Label`, sprite, `_on_ai_decision()`, and `dragon_speak()`
- EventBus, SnapshotManager, DynamicContextManager, Ollama director, VisionAgent, and alternate ZW bridge can remain outside the proof path

## G. Files that work unit would be allowed to modify

Recommended maximum allowlist for that future work unit:

```text
MODIFY:
  addons/zwengain/scripts/EngAInDragon.gd

ADD:
  one Hermes-specific external worker at repository root
  (provisional name only: hermes_session_adapter.py)

DO NOT MODIFY:
  project.godot
  addons/zwengain/scenes/EngAInDragon.tscn
  addons/zwengain/scripts/EngAInBridge.gd
  addons/zwengain/scenes/engainbridge.gd
  addons/zwengain/scenes/SnapshotManager.gd
  addons/zwengain/scenes/dynamiccontextmanager.gd
  addons/zwengain/scripts/EventBus.gd
  engain_dolphin.py
  VisionAgent.py
  zw_file_bridge.py
  assets, .uid, .import, .godot, snapshots, or canon/state systems
```

The provisional filename is an audit recommendation, not a created file or frozen contract. If adding a file is not approved later, `engain_dolphin.py` could instead be adapted, but that would overwrite an intact Ollama candidate and is less preservation-friendly.

## H. Acceptance test for Godot → Hermes → dragon response

A future proof passes only if all of the following are observed without scene mutation:

1. Start the external Hermes worker against a known new Hermes session and record its session ID outside Godot.
2. Start the unchanged main scene except for the narrowly approved caller repair.
3. Type a unique nonce-bearing utterance into the existing LineEdit, for example: `Dragon, reply exactly EMBODIED-7F3A.`
4. Verify the existing bridge produces `engain_request.json` containing the exact submitted text.
5. Verify the Hermes worker consumes that request and reports the same Hermes session ID.
6. Verify it writes a bridge-compatible response whose `narrative_response` contains `EMBODIED-7F3A`.
7. Verify `EngAInBridge._check_for_ai_response()` emits `ai_decision_received` and `EngAInDragon.dragon_speak()` logs the response.
8. Verify the existing dragon `Label.text` visibly displays `EMBODIED-7F3A` and the existing speaking color tween occurs.
9. Submit a second turn asking what nonce was used; verify the same Hermes session ID is resumed and the dragon visibly answers `EMBODIED-7F3A`. This proves conversational continuity rather than two unrelated one-shot calls.
10. Verify no request is made to localhost:5000, no scene node/property is mutated beyond existing speech presentation, no tool/action proposal is executed, and no canon/world-state file is written.
11. Terminate and restart only the Godot scene while leaving/restarting the external worker with its persisted Hermes session ID; submit a third continuity question and verify the same session resumes. If restart persistence is outside the first narrow work unit, mark it explicitly deferred rather than claiming it.

## I. Repository preservation result

### Final Git evidence

```text
$ git status --short --untracked-files=all
 M addons/zwengain/scenes/idle_flap.png.import
 M addons/zwengain/scenes/idol_flap.png.import
 M assets/generation-6c5f80d1-6b4f-4b28-819b-9fcce84b0f25.png.import
 M assets/generation-6d2a77ce-fe3b-4b62-a899-c9d4c258d1f7(2).png.import
 M icon.svg.import

$ git rev-parse HEAD
22b0ffdf16c014da8aaf7760a031c5ae6788e9cd
```

HEAD and branch are unchanged, but Git status is **not equivalent** to baseline and tracked bytes are **not byte-for-byte identical**. The mandatory Godot 4.6.1 headless editor import updated five tracked Godot 4.4-era `.import` files by adding importer defaults:

```text
compress/uastc_level=0
compress/rdo_quality_loss=0.0
process/channel_remap/red=0
process/channel_remap/green=1
process/channel_remap/blue=2
process/channel_remap/alpha=3
```

It also created ignored/generated `.godot/` cache files and an empty ignored `snapshots/` directory. The full tree manifest grew from 41 to 61 entries.

Therefore:

```text
HEAD_EQUIVALENT: YES
BRANCH_EQUIVALENT: YES
GIT_STATUS_EQUIVALENT: NO
TRACKED_BYTES_EQUIVALENT: NO
FULL_REPOSITORY_BYTES_EQUIVALENT: NO
HAND_AUTHORED_IMPLEMENTATION_CHANGED_BY_AUDITOR: NO
IMPLEMENTATION_CREATED: NO
```

No cleanup, reset, checkout, manual reversion, or deletion was performed. This deliberately leaves the mandatory run's side effects visible rather than violating the instruction not to clean/reset/modify them. Exact evidence:

- `logs/final-git.txt`
- `logs/godot-import-metadata.diff`
- `logs/baseline-files.sha256`
- `logs/final-files.sha256`
- `logs/repository-byte-diff.txt`
- `logs/baseline-tracked.sha256`
- `logs/final-tracked.sha256`

## Audit conclusion

The intended vertical slice partially exists. The repository already has the visible dragon, typed LineEdit, main-scene composition, bridge node, file request/response machinery, response signal, dragon-visible label output, basic snapshot side system, and one compatible—but manually launched and Ollama-specific—Python provider candidate.

The slice does not close because typed input is misrouted to an unimplemented HTTP endpoint and no Hermes session worker exists. Preserve the existing scene and active bridge. The smallest future lane is one caller repair plus one external Hermes session adapter, with conversation text only and no game/world authority.
