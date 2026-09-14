# Main.tscn / WorldComposition.tscn single-writer split

## The bug this replaces

`09-13-2026-runtime-side-hot-reload.md` built `RuntimeSceneSync3D`
watching `Main.tscn` directly. A live test right after
(`azure_cube_probe_09`, then `emerald_cube_probe_10`) showed "no crash,
no hot reload, no object" even though Hermes reported both turns DONE.

Traced with cryptographic certainty, not guesswork: the project's own
tamper-evident `EditReceiptStore` (before/after SHA-256 per file, per
turn, under `user://edit_receipts`) shows both turns' new probe scene
file (`AzureCubeProbe09.tscn`, `EmeraldCubeProbe10.tscn`) really was
created — but `Main.tscn`'s *actual* recorded before→after diff for
both turns was not the new node at all. It was an unrelated one-line
`DragonAvatar3D` transform change. Hashing the live file and diffing it
byte-for-byte against the receipt's own before-snapshot confirmed it:
zero difference other than that transform line.

Root cause: `~/.config/godot/editor_settings-4.6.tres` has
`run/auto_save/save_before_running = true`. With `Main.tscn` open in the
Editor, and "Ignore" clicked on the "changed externally" prompt (the
only real option — see the earlier reload-crash receipt for why "Reload
from disk" itself crashes), the Editor's in-memory copy of the scene
goes stale relative to disk. The next Play press silently resaves every
open modified scene from that stale in-memory copy, clobbering whatever
Hermes had written externally, with zero dialog or warning at save time
(unlike the one-time load-time prompt). The `EditorFileSystem
.filesystem_changed` timing in the lifecycle trace log lines up exactly
with this.

The user's call, correctly: **do not patch around this** with a global
autosave disable or generic Save/Play interception. That treats the
symptom. The actual defect is that `Main.tscn` had two writers — the
Editor (in-memory, persistently open) and Dragon/Hermes (external,
DIRECT_WRITE) — racing over one file with no merge. Fix the ownership,
not the race.

## The fix: single-writer boundary

```
Main.tscn (Editor-owned, stable shell)
├── World
│   ├── DirectionalLight3D, Camera3D, Ground   (persistent runtime systems)
│   ├── DragonAvatar3D (+ EngAInBridge)         (persistent runtime systems)
│   └── WorldComposition  (instance of WorldComposition.tscn)
└── UI  (ControlHUD, ...)                       (persistent runtime systems)

WorldComposition.tscn (Dragon/Hermes-owned, mutable content)
├── FirstLightTower
├── RETURN-01
├── VERIFICATION_MONOLITH_04
├── LOAD_PROBE_DIAMOND_05
└── AMBER_CUBE_PROBE_08
```

`Main.tscn` is never open... rather, `WorldComposition.tscn` is never
open as its own Editor tab — it only exists as a `PackedScene` instance
referenced from `Main.tscn`, so there is no in-memory Editor copy of
*it* to ever go stale. `Main.tscn` itself stops being rewritten by
DIRECT_WRITE edits at all under the new convention, so its own
in-memory Editor copy stops diverging from disk in the first place —
removing the precondition the autosave-clobber needed, rather than
guarding against its symptom.

## Discovery before implementing (per the user's instruction)

Grepped every script for any reference to the nodes being moved, before
moving anything:

```
scripts/Main.gd:6:@onready var bridge = $World/DragonAvatar3D/EngAInBridge
scripts/Main.gd:14:  _scene_sync.start($World)
scripts/PerceptionCapture3D.gd:7:const DRAGON_NODE_PATH := NodePath("World/DragonAvatar3D")
scripts/ControlHUD.gd:13:@export var bridge_path: NodePath = ^"../../World/DragonAvatar3D/EngAInBridge"
```

Every real path reference is to `World/DragonAvatar3D` (kept exactly
where it was — persistent runtime systems were never in scope to move).
Nothing referenced `FirstLightTower`, `RETURN-01`,
`VERIFICATION_MONOLITH_04`, `LOAD_PROBE_DIAMOND_05`, or
`AMBER_CUBE_PROBE_08` by path anywhere in code — safe to extract without
breaking anything.

## What changed

- **New `scenes/WorldComposition.tscn`** — the five content nodes
  extracted verbatim (same ext_resource references, same transforms),
  now direct children of its own root (`parent="."`).
- **`scenes/Main.tscn`** — the five removed node blocks and their five
  `ext_resource` lines replaced with one `ext_resource` for
  `WorldComposition.tscn` and one instancing node under `World`. Nothing
  else in `Main.tscn` touched — `DirectionalLight3D`, `Camera3D`,
  `Ground`, `DragonAvatar3D`, `UI`/`ControlHUD` all byte-identical to
  before.
- **`scripts/RuntimeSceneSync3D.gd`** — retargeted from `Main.tscn` to
  `WorldComposition.tscn`; the parser's parent match changed from
  `parent="World"` to `parent="."` (matching that new file's own root-
  relative addressing). Doc header rewritten to explain the ownership
  split and the exact live evidence that made watching `Main.tscn`
  unsafe. Narrow behavior otherwise unchanged: still only detects new,
  self-contained `instance=ExtResource(...)` additions; still never
  touches an existing node; still never reloads the file it watches.
- **`scripts/Main.gd`** — `_scene_sync.start($World)` ->
  `_scene_sync.start($World/WorldComposition)`. `bridge` path and
  everything else unchanged.

## Real, executed proof

Three tests, all run against the real project files (not fixtures):

```
=== parser (WorldComposition) ===
OK all_known_nodes=5 reappeared=AMBER_CUBE_PROBE_08 path=res://scenes/AmberCubeProbe08.tscn transform=Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, -3, 0.6, -1.33)
=== apply ===
OK hot_added=HOTLOAD_TEST_PROBE origin=(2.5, 0.5, -1.0) child_count_after_replay=1
=== main/worldcomposition split ===
OK bridge_path=/root/Main/World/DragonAvatar3D/EngAInBridge composition_children=["FirstLightTower", "RETURN-01", "VERIFICATION_MONOLITH_04", "LOAD_PROBE_DIAMOND_05", "AMBER_CUBE_PROBE_08"] known_seed_size=5
```

The third test (`tests/test_main_worldcomposition_split.gd`, new)
instantiates the REAL `Main.tscn` the way the composed runtime would,
and checks the real resulting tree: `World/DragonAvatar3D/EngAInBridge`
still resolves exactly where every consumer hardcodes it,
`World/WorldComposition` exists and holds the real five content nodes,
and `RuntimeSceneSync3D` was genuinely `start()`-ed against
`WorldComposition` (its seeded known-node set contains all five) rather
than against `World` itself. One real bug this test caught before it
was fixed: `_ready()` (where `Main.gd` wires up the scene-sync node)
runs on tree entry, which Godot defers to the next idle frame rather
than running synchronously inside `add_child()` — the first version of
this test checked children immediately and found none; adding one
`await process_frame` fixed it.

Existing regression suites re-run clean: `hermes_bridge_logic` (ALL
CHECKS PASSED), `wait_timeout` (`OK computed=270.0 expected=270.0`).
`--check-only --script` on both modified `.gd` files compiles clean.

## What this does not do yet

- **Dragon's own operating instructions still say "Instance ... into
  res://scenes/Main.tscn."** That phrasing lives in Dragon's own
  external system prompt, not in this repo, and needs the same kind of
  direct chat correction used earlier this project for the
  terminal-inspection and file-validation wording fixes — not a code
  change. Until that's updated, the next real probe request will still
  ask Dragon to target the wrong file.
- The composed runtime process already running (`godot --path ...`,
  PID predates every change from today, including the original
  `RuntimeSceneSync3D`) still needs one restart to load any of this at
  all — unrelated to today's split, flagged in the prior receipt too,
  still true.
- The acceptance test in the user's own instruction (12 numbered steps,
  ending in "`Main.tscn` hash remains unchanged throughout" and "No
  external-change dialog for `Main.tscn` occurs") has not been run
  live end-to-end yet — that requires an actual DIRECT_WRITE turn
  against `WorldComposition.tscn` while the composed runtime keeps
  running, which needs Dragon's instructions updated first (previous
  bullet) and the runtime restarted once (this bullet).
- `run/auto_save/save_before_running` was NOT changed, per explicit
  instruction — it was a real Godot setting doing exactly what it's
  documented to do; the fix was removing the reason it could clobber
  anything, not disabling it.

## Addendum: the clobber hit the split itself, live, before anyone opened the loop

Between writing this receipt and the user's next message, the Editor
did to this very edit exactly what the receipt above describes it doing
to Hermes's azure/emerald edits: `Main.tscn` was found reverted to the
pre-split, 5-nodes-directly-under-`World` shape (harness diff notice,
hash-confirmed) — the Editor's in-memory copy was still the OLD
(pre-split) `Main.tscn` it had open from before this change ever
happened, and some save (most likely another `save_before_running` on a
Play press) wrote that stale copy back over the split, the same way it
overwrote Hermes's work earlier. `DragonAvatar3D`'s transform had also
drifted again in the interim (ordinary viewport interaction, left as-is
rather than reverted — not this project's edit to make).

This was not a flaw in the split design; it is the exact same
precondition the split is supposed to eliminate GOING FORWARD (`Main.tscn`
never gets externally rewritten once Dragon/Hermes only touches
`WorldComposition.tscn`) catching one transitional edit made externally
while the Editor still held the pre-split scene in memory. Reapplied
identically (same content, current `DragonAvatar3D` transform carried
forward as-is) and reverified with
`tests/test_main_worldcomposition_split.gd` against the real file again
— passes.

**Operational consequence for closing this out cleanly:** the Editor's
in-memory `Main.tscn` must actually be refreshed from disk before doing
anything else with it, or the very next Play press can revert this
change again. The safe way to do that is NOT the "Reload from disk"
button (proven to crash) — it's an ordinary tab close (discard, don't
save — the in-memory copy is the stale one, there's nothing worth
keeping) followed by reopening `res://scenes/Main.tscn` fresh from the
FileSystem dock. That's a normal open/close, not a live reload of an
already-open scene, so it doesn't exercise the crash-prone path at all.
