# Runtime-side hot reload for scenes/Main.tscn

## Context

The Dragon <-> Editor DIRECT_WRITE coordination loop was confirmed fully
working end to end, automatically, via the `azure_cube_probe_09` live
test earlier the same day: mutation -> editor_report -> automatic
dispatch (no player turn needed) -> `[TOOL]`/`[DRAGON]` tool_events in
the live ControlHUD. What that test also exposed: after a real,
successful, validated DIRECT_WRITE edit, neither the open Editor's own
view of `Main.tscn` nor the already-running composed game process
(`runtime_composition.py` -> `godot --path ...`, no `--editor`) reflected
the change without a manual restart. The user's words: "we need hot
reload."

That splits into two separate problems:

1. **Editor-side reload** (the open Editor's own `Main.tscn` view
   catching up). Proven unsafe twice already this project — see
   `09-13-2026-editor-reload-crash-bounded-experiment.md` and
   `addons/hermes_editor/hermes_dock.gd`'s own
   `_experimental_reload_edited_scene_via_api()` doc header. Both the
   manual "Reload from disk" dialog and the programmatic
   `EditorInterface.reload_scene_from_path()` call produced a real
   SIGABRT. Left untouched, still disabled. Not attempted again here.

2. **Runtime-side reload** (the already-running composed game picking up
   a new node in `Main.tscn` without a process restart). Never
   attempted before this. This receipt covers only this half.

## Prior finding this builds on

Earlier the same day, a full grep of `scripts/*.gd` and
`runtime_composition.py` found zero existing file-watch or scene-reload
mechanism — "automatic runtime refresh" was a coincidence (composed
runtime process restarts alongside editor crashes), never a real
mechanism. This is greenfield; nothing existing needed preserving.

## Mechanism chosen, and why it's narrow

Every real DIRECT_WRITE edit run through this loop so far
(`amber_cube_probe_08`, `azure_cube_probe_09`, and the probes already
sitting in `Main.tscn` from before) takes the exact same shape: one new,
self-contained sub-scene (no script, no external deps, per the standing
`[EDITOR_REQUEST]` convention) added as one new `ext_resource` plus one
new instanced `[node ... parent="World" ... instance=ExtResource(...)]`
entry in `scenes/Main.tscn`, nothing else touched.

New file `scripts/RuntimeSceneSync3D.gd` only detects and instantiates
new entries of exactly that shape, under the live `World` node:

- Polls `FileAccess.get_modified_time("res://scenes/Main.tscn")` once a
  second (`POLL_INTERVAL_SEC`) — cheap, no diffing unless the mtime
  actually moved.
- On a real mtime change, re-reads the file's raw text and runs a pure,
  static parser (`find_new_instanced_nodes`) that finds
  `[node ... parent="World" ... instance=ExtResource("id")]` blocks whose
  `name` isn't already known, resolves `id` back to its `[ext_resource]`
  path declaration, and captures the node's own `transform = ...` line
  verbatim.
- For each genuinely new node: `ResourceLoader.load(path, "PackedScene",
  CACHE_MODE_IGNORE)` (forces a fresh read, bypassing any cache, since
  this file was never loaded in this process before), `.instantiate()`,
  set the parsed `Transform3D`, `add_child()` onto the real live `World`
  node. Never re-instances or reloads `Main.tscn` itself. Never touches
  an existing node, removes anything, or looks outside `parent="World"`
  (so the `UI` subtree, `DragonAvatar3D`, etc. are categorically out of
  scope). This is an ordinary, everyday Godot runtime operation — adding
  a freshly loaded `PackedScene` as a child of an already-running node —
  nothing like the Editor's own internal post-reload reconciliation that
  produced the two SIGABRTs in problem #1.
- Wired into `scripts/Main.gd`: instantiated in `_ready()`, started
  against the real `$World` node (seeding "already known" from the
  live tree's actual children at boot, so nothing already on disk at
  startup gets re-added), and its `node_hot_added` signal is relayed
  through `bridge.emit_signal("log_line", "sys", ...)` — the exact same
  channel `ControlHUD` already listens to for every other transcript
  line, so a hot-added node shows up in the live HUD with no new UI code.

## Real, executed proof (not mocked)

Two new test files, run the same way this project already runs its
GDScript tests (`godot --headless -s tests/....gd`, `extends SceneTree`,
`OK`/`FAIL` + `quit(0/1)`):

- `tests/test_runtime_scene_sync_parser.gd` — runs the pure parser
  against the REAL, current `scenes/Main.tscn` text on disk (not a
  fixture). Proves (a) every one of the six real probes already
  instanced under `World` today is treated as already-known and produces
  zero additions (the idempotent no-double-add case that matters once
  this runs continuously), and (b) dropping exactly one real,
  already-on-disk probe (`AMBER_CUBE_PROBE_08`) out of the known set
  makes it, and only it, reappear as a detected addition, with the exact
  real `ext_resource` path (`res://scenes/AmberCubeProbe08.tscn`) and
  the exact real `Transform3D` literal Main.tscn actually holds for that
  node.
- `tests/test_runtime_scene_sync_apply.gd` — proves the live half: a
  real, already-on-disk, self-contained probe scene
  (`res://scenes/LoadProbeDiamond05.tscn`, confirmed no script/deps)
  loaded fresh and `add_child()`-ed into a synthetic `Node3D` "world" in
  a real running `SceneTree`; asserts the node lands with the right
  name, the right `Transform3D` origin, brings its own real child
  content along, fires `node_hot_added` exactly once, and that replaying
  the same addition a second time does NOT duplicate the node
  (idempotence, matching the poll loop calling the parser repeatedly
  against an unchanged file).

Both ran real, live, against the real project — not simulated:

```
=== parser ===
OK all_known_probes=6 reappeared=AMBER_CUBE_PROBE_08 path=res://scenes/AmberCubeProbe08.tscn transform=Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, -3, 0.6, -1.33)
=== apply ===
OK hot_added=HOTLOAD_TEST_PROBE origin=(2.5, 0.5, -1.0) child_count_after_replay=1
```

Existing regression suites re-run clean afterward (no touch to their own
scope, confirmed rather than assumed):

```
=== hermes_bridge_logic === ALL CHECKS PASSED
=== engainbridge3d_wait_timeout (default env) === OK computed=270.0 expected=270.0
```

`godot --headless --check-only --script scripts/Main.gd` compiles clean.

## Real bugs a real test run actually caught (kept for the record)

- First attempt used `Expression.new().parse()/.execute()` to turn a
  captured `Transform3D(...)` text literal into a real value. Live-
  tested in isolation: `Expression` DOES support the 2-argument
  `Transform3D(Basis, Vector3)` form but silently fails execution
  (`has_execute_failed() == true`, value `null`) for the 12-scalar form
  Godot's own `.tscn` writer actually emits. Caught by the apply test
  asserting a real, non-zero transform origin and getting `(0,0,0)`
  instead — not by reasoning about the API in advance.
- Second attempt called the native `Transform3D(f,f,f,f,f,f,f,f,f,f,f,f)`
  12-scalar constructor directly from GDScript. That does not compile —
  "No constructor of Transform3D matches" — confirmed live. Fixed by
  building `Basis(x_axis, y_axis, z_axis)` from the first nine numbers
  and `Transform3D(basis, origin)` from the last three, which does exist.
  A compile failure at this call site, under `--headless -s`, produced a
  process that printed the error but never called `quit()` — it just sat
  running instead of exiting non-zero, which looked identical to an
  infinite loop from the outside until traced with `ps` state and a
  plain, dependency-free bisection script.
- The 12-number extraction regex, run directly against
  `"Transform3D(1, 0, ...)"` instead of the parenthesized argument list
  only, matched the literal `3` inside the word `Transform3D` itself as
  a 13th spurious number, which silently failed the `size() != 12`
  check and made every real transform look unparsable. Fixed by slicing
  to the substring between the first `(` and the last `)` before running
  the number regex — caught the same way, by a real test asserting a
  real transform and getting an empty/failed result back.

## What this does not do

- Does not touch the Editor-side reload problem at all — that one stays
  disabled, no new attempt made.
- Does not yet run against a *live* composed runtime process end to end
  with a real DIRECT_WRITE edit landing while the game is running — the
  currently-running composed runtime process (PID predates this change)
  has the old `Main.gd` in memory and needs one restart to pick up
  `RuntimeSceneSync3D` at all. Everything above is real, executed,
  non-mocked proof of the mechanism itself in isolation; the first live
  end-to-end run (start the runtime fresh, then run a new DIRECT_WRITE
  probe while it keeps running, and watch the object appear with zero
  manual action) is the natural next step and has not been done yet.
- `CALL_LIFETIME_SEC := 185.0` in `EngAInBridge3D.gd` remains flagged,
  not fixed, unrelated to this change.
