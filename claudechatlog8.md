╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

 ▎ Keep working from anywhere
 ▎ Check progress or reply to any session from the mobile app, desktop app, or claude.ai. To keep a session in this terminal only, run /remote-control

❯ Hermes is doing the first one: it is overwriting the Godot resource on disk and relying on Godot’s external-file detection/reload path.

  It is not injecting raw GDScript into the running engine, and there is no evidence here of GDScript.new(), reload(), direct scene-tree mutation from a socket callback, or free()/queue_free() activity.

  The actual sequence we have reproduced is:

  Hermes/@tool
  → writes scenes/Main.tscn directly on disk
  → write completes successfully
  → resulting .tscn independently loads and instantiates correctly
  → Godot editor notices "file changed outside Godot"
  → Godot asks Reload from disk
  → HUMAN clicks Reload
  → editor process SIGSEGV

  That distinction is important: the editor does not crash when Hermes writes the file. It crashes when Godot subsequently reloads that externally modified scene into the already-running editor.

  We've also ruled out several things already:

  Bad .tscn syntax                    NO
  Scene fails to instantiate          NO
  Dragon request required             NO
  Hermes write itself immediately
  crashes Godot                       NO

  The exact same one-line valid change:

  -offset_top = 76.0
  +offset_top = 77.0

  was verified before reload, and Case 1 crashed despite there having been zero Runtime Dragon requests.

  So from that list, the first hypothesis is currently the closest:

  > Resource/file-watcher/reload lifecycle race.

  But I'd phrase it more specifically as:

  Godot external-scene reload lifecycle
  +
  something present in the composed EngAIn launch environment
  → native editor crash

  because we have another crucial result: a standalone/bare editor survived essentially the same external scene reload, while the launcher-composed editor has reproduced the SIGSEGV.

  So it isn't yet fair to say:

  Godot can't safely reload externally modified .tscn files

  The evidence instead says:

  bare editor reload                     → survived

  ./launch_dragon3d.sh composed editor
  external Main.tscn reload              → crashes reproducibly

  That makes me suspicious of something attached to the editor's lifecycle in the composed environment—possibly an addon/editor callback, runtime ownership interaction, or some object that remains referenced while Godot tears down/reconstructs the externally reloaded scene.

  The orphaned-instance idea is therefore still conceptually plausible, but not in the form of “Hermes replaced a running script.” Hermes didn't. It would instead have to be something Godot or an editor addon holds across the scene reload.

  And the free() versus queue_free() theory currently has no supporting evidence. I wouldn't chase that without seeing a relevant callback/node teardown path.

  So if I were answering that final question directly:

  > Hermes writes the .tscn file on disk. It does not inject code into the active Godot process. Godot detects the external modification, presents its normal “Reload from disk” dialog, and the native editor crashes only after we accept that reload.

  That narrows the bug considerably. The next debugging matrix you're already running—removing pieces of the composed environment—is exactly the right way to determine what makes that otherwise-normal external reload unsafe.

  Searched for 2 patterns, read 3 files, listed 1 directory, ran 2 shell commands

I read through the pasted analysis against the actual project on disk (/mnt/data-drive/godot_engain_3d_avatar, not this audit repo) and the reasoning holds up — the reload-lifecycle-plus-something-in-the-composed-environment framing is the right shape for the evidence you've got. A couple of things worth folding in:

What I found that's relevant:

addons/hermes_editor/hermes_bridge.gd has exactly the pattern your "orphaned reference held across reload" hypothesis describes — a NOTIFICATION_PREDELETE handler that blocks the main thread with _thread.wait_to_finish() when the node is freed while a Hermes turn is still in flight (comment cites a real prior "three-case investigation," and the case files are still sitting right there: _teardown_case1_completed_then_freed.gd, _teardown_case2_stop_mid_turn.gd, _teardown_case3_freed_mid_turn.gd, live_teardown_proof.gd).

That's real teardown-during-free danger in this addon — but it's scoped to the dock's own bridge node, which plugin.gd adds to the bottom panel (add_control_to_bottom_panel), not into the edited scene tree. So it's a sibling of Main.tscn, not a child of it — a Main.tscn external reload shouldn't ordinarily free it. Worth ruling in/out explicitly rather than assuming it's unrelated just because of scope, since it's the single most crash-shaped thing already living in this addon.

On the debugging matrix itself: your coredumpctl/gdb attempts so far were live-attach (gdb -p), which needs sudo and races the actual crash moment — the one clean sudo session you got exited normally without catching the SIGSEGV. You already have a saved core file (core.godot.1000...zst, 136.8M) from the earlier crash. coredumpctl debug <PID> (or coredumpctl gdb <PID>) opens gdb directly on that saved core, post-mortem, no attach race, no ptrace_scope fight — and bt full / thread apply all bt there would tell you which frame actually faulted, addon-callback or core Godot, without needing to reproduce it live again.

Want me to:

● User answered Claude's questions:
· What should I actually do next on this? → Something else

I don't have your actual answer text for "Something else" — the tool only confirmed you picked that option, it didn't pass through what you typed. What would you like me to do?

✻ Crunched for 1m 58s

❯ Choose 2.

  Option 1 has effectively already been done: Hermes ran post-mortem GDB against preserved cores with coredumpctl debug and collected all-thread backtraces. The official Godot binary is too stripped for those addresses to identify the responsible C++ path cleanly. Repeating that without symbols probably won’t buy us much.

  The new finding in hermes_bridge.gd is much more actionable:

  NOTIFICATION_PREDELETE
  → _thread.wait_to_finish()
  → potentially blocks during destruction

  That is exactly the sort of lifecycle behavior worth proving or eliminating.

  But don’t jump straight to “disable Hermes and see if it crashes.” First instrument the lifecycle so we know whether that path is even touched when Main.tscn reloads.

  I would tell it:

  Choose option 2.

  Trace the Hermes bridge/dock lifecycle specifically across the external
  Main.tscn Reload from disk boundary.

  Do not fix or redesign anything yet.

  I want evidence answering:

  1. Does the HermesBridge node receive NOTIFICATION_PREDELETE when
     Main.tscn is externally reloaded?

  2. Is a Hermes worker thread active at that moment?

  3. Does _thread.wait_to_finish() execute during the reload path?

  4. Are plugin.gd, hermes_dock.gd, or HermesBridge torn down,
     reconstructed, detached, or otherwise notified during the reload?

  5. Record timestamps/order for:
     - external Main.tscn modification detected
     - human Reload from disk
     - Hermes bridge lifecycle notifications
     - thread state
     - editor crash

  6. Keep the experiment in the real ./launch_dragon3d.sh composed
     environment.

  7. Do not send an @dragon request; Case 1 already proved one is unnecessary.

  8. Restore the exact sealed Main.tscn baseline before and after each case.

  9. Do not modify the crash behavior to make it safer yet. Instrument only.

  If the bridge PREDELETE/wait path is NOT entered, rule it out and continue
  component subtraction.

  If it IS entered immediately before the SIGSEGV, then build a minimal
  A/B test that suppresses only that teardown behavior without changing
  anything else.

  That gives us a decisive fork:

  Main reload
     ↓
  HermesBridge PREDELETE NOT CALLED
     → this particular teardown theory loses weight

  Main reload
     ↓
  HermesBridge PREDELETE CALLED
     ↓
  wait_to_finish / thread teardown
     ↓
  SIGSEGV
     → extremely strong lead

  The key is not to “fix” wait_to_finish() yet. First prove whether that code executes during the crash.

  And if it does not, go back to the subtraction matrix. The composed environment remains the proven distinguishing factor.

  Read 2 files, ran 1 shell command

● Write(/mnt/data-drive/godot_engain_3d_avatar/addons/hermes_editor/_lifecycle_probe.gd)
Wrote 50 lines to ../godot_engain_3d_avatar/addons/hermes_editor/_lifecycle_probe.gd
@tool
extends RefCounted

## _lifecycle_probe.gd — INSTRUMENTATION ONLY, added to answer one
## question in the composed-editor SIGSEGV-on-external-reload
## investigation: does anything in the Hermes bridge/dock lifecycle
## (plugin.gd, hermes_dock.gd, hermes_bridge.gd) get touched — entered,
## torn down, reconstructed, or blocked on — when Main.tscn is
## externally modified and the human accepts Godot's "Reload from disk"
## dialog.
… +40 lines

Now plugin.gd:

● Write(/mnt/data-drive/godot_engain_3d_avatar/addons/hermes_editor/plugin.gd)
Added 56 lines
## difference here is the dock is built procedurally in hermes_dock.gd's
## _ready() rather than loaded from a .tscn, so there is no separate scene
## resource to keep in sync with this script.
##
## INSTRUMENTATION (temporary, diagnostic only — see _lifecycle_probe.gd):
## traces this plugin's own _enter_tree()/_exit_tree() and, best-effort,
## whatever EditorFileSystem reload-related signals this Godot build
## actually exposes — added to answer whether an external Main.tscn
## "Reload from disk" touches this plugin's lifecycle at all. Purely
## additive; no existing behavior below changes because of it.

const HermesDockScript := preload("res://addons/hermes_editor/hermes_dock.gd")
const LifecycleProbe := preload("res://addons/hermes_editor/_lifecycle_probe.gd")

var dock_instance: Control


func _enter_tree() -> void:
  LifecycleProbe.trace("plugin._enter_tree: begin")
  dock_instance = HermesDockScript.new()
  dock_instance.name = "Hermes"
  dock_instance.editor_interface = get_editor_interface()
  add_control_to_bottom_panel(dock_instance, "Hermes")
  _connect_reload_probes()
  LifecycleProbe.trace("plugin._enter_tree: end")


func _exit_tree() -> void:
  LifecycleProbe.trace("plugin._exit_tree: begin")
  if is_instance_valid(dock_instance):
    remove_control_from_bottom_panel(dock_instance)
    dock_instance.queue_free()
  dock_instance = null
  LifecycleProbe.trace("plugin._exit_tree: end")


## Connects, best-effort, to whatever EditorFileSystem signals this
## Godot build actually exposes that could correlate with an external
## Main.tscn modification being noticed / reloaded. Uses the dynamic
## Object.has_signal()/connect() string API rather than typed signal
## access specifically so a signal name that doesn't exist in this
## Godot version is a logged skip, not a script load failure.
func _connect_reload_probes() -> void:
  var efs: Object = get_editor_interface().get_resource_filesystem()
  if efs == null:
    LifecycleProbe.trace("plugin._connect_reload_probes: no EditorFileSystem available")
    return
  _connect_probe_signal(efs, "filesystem_changed", Callable(self, "_on_filesystem_changed"))
  _connect_probe_signal(efs, "sources_changed", Callable(self, "_on_sources_changed"))
  _connect_probe_signal(efs, "resources_reimported", Callable(self, "_on_resources_reimported"))
  _connect_probe_signal(efs, "resources_reload", Callable(self, "_on_resources_reload"))


func _connect_probe_signal(efs: Object, sig_name: String, cb: Callable) -> void:
  if not efs.has_signal(sig_name):
    LifecycleProbe.trace("plugin._connect_reload_probes: signal %s not present on this build" % sig_name)
    return
  if not efs.is_connected(sig_name, cb):
    efs.connect(sig_name, cb)
  LifecycleProbe.trace("plugin._connect_reload_probes: connected %s" % sig_name)


func _on_filesystem_changed() -> void:
  LifecycleProbe.trace("EditorFileSystem.filesystem_changed fired")


func _on_sources_changed(exist: bool) -> void:
  LifecycleProbe.trace("EditorFileSystem.sources_changed fired: exist=%s" % str(exist))


func _on_resources_reimported(resources: PackedStringArray) -> void:
  LifecycleProbe.trace("EditorFileSystem.resources_reimported fired: %s" % [resources])


func _on_resources_reload(resources: PackedStringArray) -> void:
  LifecycleProbe.trace("EditorFileSystem.resources_reload fired: %s" % [resources])

Now hermes_dock.gd — add the probe const, trace _ready(), and a new _notification():

● Update(/mnt/data-drive/godot_engain_3d_avatar/addons/hermes_editor/hermes_dock.gd)
Added 1 line
var editor_interface: Object  # set by plugin.gd, matching godot_ollama_task_performer/assist_dock.gd's own con
vention

const HermesBridgeScript := preload("res://addons/hermes_editor/hermes_bridge.gd")
const LifecycleProbe := preload("res://addons/hermes_editor/_lifecycle_probe.gd")

var _bridge: Node
var _busy: bool = false

● Update(/mnt/data-drive/godot_engain_3d_avatar/addons/hermes_editor/hermes_dock.gd)
Added 15 lines


func _ready() -> void:
  LifecycleProbe.trace("dock._ready: begin (dock instance id=%d)" % get_instance_id())
  _build_ui()
  _bridge = HermesBridgeScript.new()
  add_child(_bridge)

  # _ensure_scratch_setup() for why this was moved out of _run_hermes().
  HermesBridgeScript._ensure_scratch_setup(HermesBridgeScript.project_root())
  _ensure_temporary_trial_ui()
  LifecycleProbe.trace("dock._ready: end (bridge instance id=%d)" % _bridge.get_instance_id())


## INSTRUMENTATION — see _lifecycle_probe.gd. Answers, for the dock
## Control itself (not the bridge Node — see hermes_bridge.gd's own
## _notification()), whether an external Main.tscn reload ever frees,
## exits, or unparents this dock.
func _notification(what: int) -> void:
  if what == NOTIFICATION_PREDELETE:
    LifecycleProbe.trace("dock._notification: NOTIFICATION_PREDELETE")
  elif what == NOTIFICATION_EXIT_TREE:
    LifecycleProbe.trace("dock._notification: NOTIFICATION_EXIT_TREE")
  elif what == NOTIFICATION_UNPARENTED:
    LifecycleProbe.trace("dock._notification: NOTIFICATION_UNPARENTED")


func _process(_delta: float) -> void:
  # Existing editor docks survive script hot reload. Upgrade the old,
  # disabled DIRECT WRITE row in place so the bridge node — and its

● Update(/mnt/data-drive/godot_engain_3d_avatar/addons/hermes_editor/hermes_bridge.gd)
Added 3 lines

signal turn_finished(result: Dictionary)

const LifecycleProbe := preload("res://addons/hermes_editor/_lifecycle_probe.gd")

var session_id: String = ""  # empty until the first real reply names one
var _thread: Thread
var _discard_pending: bool = false
var _thread_body_active: bool = false  # INSTRUMENTATION — see _run_hermes()/_run_hermes_impl() split below

const _SESSION_ID_LINE_PATTERN := "^session_id:\\s*(\\S+)\\s*$"
const SCRATCH_DIR_NAME := ".hermes_scratch"

● Update(/mnt/data-drive/godot_engain_3d_avatar/addons/hermes_editor/hermes_bridge.gd)
Added 12 lines
## hermes/model call takes), but it is not instant either.
func _notification(what: int) -> void:
  if what == NOTIFICATION_PREDELETE:
    LifecycleProbe.trace(
      "bridge._notification: NOTIFICATION_PREDELETE begin (thread_started=%s, thread_body_active=%s)" % [
        str(_thread != null and _thread.is_started()), str(_thread_body_active)
      ]
    )
    if _thread != null and _thread.is_started():
      LifecycleProbe.trace("bridge._notification: entering _thread.wait_to_finish() — will block here if the t
hread body is still running")
      _thread.wait_to_finish()
      LifecycleProbe.trace("bridge._notification: _thread.wait_to_finish() returned")
    LifecycleProbe.trace("bridge._notification: NOTIFICATION_PREDELETE end")
  elif what == NOTIFICATION_EXIT_TREE:
    LifecycleProbe.trace("bridge._notification: NOTIFICATION_EXIT_TREE")
  elif what == NOTIFICATION_UNPARENTED:
    LifecycleProbe.trace("bridge._notification: NOTIFICATION_UNPARENTED")


## Starts one turn in a background thread — OS.execute() blocks, and a

● Update(/mnt/data-drive/godot_engain_3d_avatar/addons/hermes_editor/hermes_bridge.gd)
Added 1 line
    _thread.wait_to_finish()
  var hermes_path := find_hermes_executable()
  _thread = Thread.new()
  LifecycleProbe.trace("bridge.send: starting new turn thread")
  _thread.start(_run_hermes.bind(hermes_path, message, session_id, model, provider, project_root(), mode))



● Update(/mnt/data-drive/godot_engain_3d_avatar/addons/hermes_editor/hermes_bridge.gd)
Added 22 lines
  _discard_pending = true


## INSTRUMENTATION — thin wrapper around the actual thread body
## (_run_hermes_impl, unchanged below) so _thread_body_active is set/
## cleared around EVERY return path in one place, instead of having to
## chase down each of _run_hermes_impl's own early returns individually.
## Thread.start() still binds to this exact function name/signature —
## nothing about how the thread is started changes.
func _run_hermes(
  hermes_path: String,
  message: String,

  cwd: String,
  mode: String
) -> void:
  _thread_body_active = true
  LifecycleProbe.trace("bridge._run_hermes: thread body entered")
  _run_hermes_impl(hermes_path, message, resume_session_id, model, provider, cwd, mode)
  LifecycleProbe.trace("bridge._run_hermes: thread body returning")
  _thread_body_active = false


func _run_hermes_impl(
  hermes_path: String,
  message: String,
  resume_session_id: String,
  model: String,
  provider: String,
  cwd: String,
  mode: String
) -> void:
  var effective_mode := normalize_mode(mode)
  var result := {
    "success": false,

  Searched for 1 pattern, read 1 file, ran 1 shell command

Clean — one wrapper, one impl, no duplicates. Everything is additive-only: no early return in _run_hermes_impl was touched, send()'s thread-start call is unchanged except the new trace line, and the dock/plugin edits only add tracing and lifecycle-probe wiring.

  Ran 1 shell command

Instrumentation is in place

Three files edited in /mnt/data-drive/godot_engain_3d_avatar, one new file added — all diagnostic-only, no control-flow changes:

- addons/hermes_editor/_lifecycle_probe.gd (new) — LifecycleProbe.trace(event), appends timestamped lines to /tmp/engain-debug-evidence/hermes_lifecycle_trace.log (outside the project tree, so it never touches the live-tree fingerprint audit or git status). Opens/writes/closes fresh every call — no buffered handle — so the last line survives a SIGSEGV.
- plugin.gd — traces _enter_tree/_exit_tree; best-effort-connects to whatever of filesystem_changed, sources_changed, resources_reimported, resources_reload this Godot build actually exposes on EditorFileSystem (guarded with has_signal, so an absent signal is a logged skip, not a load error).
- hermes_dock.gd — traces _ready() entry/exit, plus a new _notification() logging PREDELETE/EXIT_TREE/UNPARENTED for the dock Control itself.
- hermes_bridge.gd — traces the existing NOTIFICATION_PREDELETE handler (entry, whether wait_to_finish() is actually called, before/after that call) and EXIT_TREE/UNPARENTED; _run_hermes is now a thin wrapper (_thread_body_active = true → calls the untouched original body, renamed _run_hermes_impl → false) so "is a worker thread active" is tracked around every return path in one place instead of hunting each one.

This answers Q1–Q4 directly and gives ordered timestamps for Q5, with one caveat: I found no certain public signal for the scene-reload confirmation itself (only EditorFileSystem's rescan-related signals) — Godot's internal "Reload from disk" dialog accept isn't scriptable that I could confirm. So the EditorFileSystem line is your best automatic proxy for "external modification noticed"; you'll still need to note wall-clock when you click Reload yourself, and the log's last line before the crash is the strongest artifact regardless.

What I can't do: clicking "Reload" is a GUI action in your session — I have no hook into that dialog. Repro steps are yours to run:

1. cd /mnt/data-drive/godot_engain_3d_avatar && ./launch_dragon3d.sh
2. Restore the sealed Main.tscn baseline as you already do, make the external one-line edit, let Godot detect it, click Reload.
3. After the crash (or survival), cat /tmp/engain-debug-evidence/hermes_lifecycle_trace.log — paste it back to me or tell me to read it and I'll walk the fork for you.

Want me to also add a .gitignore line for _lifecycle_probe.gd region or just leave these as plain uncommitted diffs for you to git diff/revert when done?

✻ Churned for 5m 1s

※ recap: Investigating why the composed Godot editor SIGSEGVs on external Main.tscn reload; I added lifecycle tracing to the Hermes addon to catch the cause. Next: run launch_dragon3d.sh, trigger the reload, and share the trace log. (disable recaps in /config)

❯  ╭─mytruelove@mytruelove in ~ via  v3.14.7 took 0s
   ╰─λ cat /tmp/engain-debug-evidence/hermes_lifecycle_trace.log
  2026-08-25 02:33:09 | t_usec=5363862 | plugin._enter_tree: begin
  2026-08-25 02:33:09 | t_usec=5364035 | dock._ready: begin (dock instance id=1561338119856)
  2026-08-25 02:33:09 | t_usec=5367173 | dock._ready: end (bridge instance id=1562730628863)
  2026-08-25 02:33:09 | t_usec=5369545 | plugin._connect_reload_probes: connected filesystem_changed
  2026-08-25 02:33:09 | t_usec=5369664 | plugin._connect_reload_probes: connected sources_changed
  2026-08-25 02:33:09 | t_usec=5369743 | plugin._connect_reload_probes: connected resources_reimported
  2026-08-25 02:33:09 | t_usec=5369815 | plugin._connect_reload_probes: connected resources_reload
  2026-08-25 02:33:09 | t_usec=5369882 | plugin._enter_tree: end
  2026-08-25 02:33:09 | t_usec=5933392 | EditorFileSystem.filesystem_changed fired
  2026-08-25 02:33:10 | t_usec=6729022 | EditorFileSystem.sources_changed fired: exist=false
  2026-08-25 02:33:54 | t_usec=51200952 | EditorFileSystem.sources_changed fired: exist=false
  2026-08-25 02:33:54 | t_usec=51205572 | EditorFileSystem.sources_changed fired: exist=false
  2026-08-25 02:36:02 | t_usec=179221933 | bridge.send: starting new turn thread
  2026-08-25 02:36:02 | t_usec=179222227 | bridge._run_hermes: thread body entered
  2026-08-25 02:37:08 | t_usec=3280818 | plugin._enter_tree: begin
  2026-08-25 02:37:08 | t_usec=3281178 | dock._ready: begin (dock instance id=1565867968518)
  2026-08-25 02:37:08 | t_usec=3285690 | dock._ready: end (bridge instance id=1567260477525)
  2026-08-25 02:37:08 | t_usec=3286407 | plugin._connect_reload_probes: connected filesystem_changed
  2026-08-25 02:37:08 | t_usec=3286508 | plugin._connect_reload_probes: connected sources_changed
  2026-08-25 02:37:08 | t_usec=3286588 | plugin._connect_reload_probes: connected resources_reimported
  2026-08-25 02:37:08 | t_usec=3286665 | plugin._connect_reload_probes: connected resources_reload
  2026-08-25 02:37:08 | t_usec=3286735 | plugin._enter_tree: end
  2026-08-25 02:37:08 | t_usec=3293458 | EditorFileSystem.filesystem_changed fired
  2026-08-25 02:37:08 | t_usec=3463777 | EditorFileSystem.sources_changed fired: exist=false
  2026-08-25 02:37:08 | t_usec=3572006 | plugin._exit_tree: begin
  2026-08-25 02:37:08 | t_usec=3572141 | bridge._notification: NOTIFICATION_EXIT_TREE
  2026-08-25 02:37:08 | t_usec=3572646 | dock._notification: NOTIFICATION_EXIT_TREE
  2026-08-25 02:37:08 | t_usec=3573076 | dock._notification: NOTIFICATION_UNPARENTED
  2026-08-25 02:37:08 | t_usec=3573187 | plugin._exit_tree: end
  2026-08-25 02:37:08 | t_usec=3573316 | dock._notification: NOTIFICATION_PREDELETE
  2026-08-25 02:37:08 | t_usec=3573405 | bridge._notification: NOTIFICATION_PREDELETE begin (thread_started=false, thread_body_active=false)
  2026-08-25 02:37:08 | t_usec=3573486 | bridge._notification: NOTIFICATION_PREDELETE end
  2026-08-25 02:37:08 | t_usec=3573568 | bridge._notification: NOTIFICATION_UNPARENTED
  2026-08-25 02:39:38 | t_usec=394391875 | bridge._run_hermes: thread body returning
  2026-08-25 02:40:24 | t_usec=440722400 | EditorFileSystem.sources_changed fired: exist=false
  2026-08-25 02:40:42 | t_usec=458771016 | EditorFileSystem.sources_changed fired: exist=false

   ╭─mytruelove@mytruelove in ~ via  v3.14.7 took 0s This trace gives us something valuable, but it also reveals that the log currently mixes more than one Godot process, so we should not draw the wrong conclusion from the ordering.

  The strongest fact is this:

  ```text
  bridge._notification: NOTIFICATION_PREDELETE begin
  (thread_started=false, thread_body_active=false)

  bridge._notification: NOTIFICATION_PREDELETE end
  ```

  There is no:

  ```text
  wait_to_finish BEGIN
  ```

  So in the teardown that was actually captured, the dangerous `wait_to_finish()` branch was not taken. That weakens the theory that the crash is simply:

  ```text
  Main.tscn reload
  → HermesBridge PREDELETE
  → wait_to_finish()
  → SIGSEGV
  ```

  That did not happen in this successful run.

  But there is a more important issue in the trace. Look at the monotonic timestamps:

  ```text
  02:36:02 | t_usec=179222227
  bridge thread entered

  02:37:08 | t_usec=3280818
  plugin._enter_tree
  ```

  `t_usec` went from about 179 million back down to 3 million. A monotonic process timer does not normally go backwards like that inside one Godot process.

  Then later:

  ```text
  02:39:38 | t_usec=394391875
  bridge._run_hermes: thread body returning
  ```

  That jumps back to the older clock domain.

  So this file is almost certainly interleaving lifecycle events from at least two Godot processes.

  That means this apparent sequence:

  ```text
  thread started
  → plugin destroyed
  → thread returned two minutes later
  ```

  cannot safely be treated as one object's lifecycle. Those events may belong to different editor processes.

  That is the first thing I would fix in the instrumentation before another reproduction.

  Have the probe add the process PID to every line, ideally also the emitting object's instance ID. For example:

  ```text
  2026-08-25 ... |
  pid=123456 |
  t_usec=... |
  bridge_id=... |
  bridge._notification: PREDELETE ...
  ```

  For bridge lines I would want:

  ```text
  pid
  bridge instance_id
  thread_started
  thread_body_active
  event
  ```

  For dock lines:

  ```text
  pid
  dock instance_id
  event
  ```

  For plugin lines:

  ```text
  pid
  event
  ```

  Then we can split the trace by process and know exactly which lifecycle belonged to the editor that crashed.

  There is still a useful result from this successful run:

  ```text
  Hermes addon teardown events      YES
  Bridge PREDELETE                  YES
  Worker active at that PREDELETE   NO
  wait_to_finish executed           NO
  Reload survived                   YES
  ```

  So PREDELETE itself is clearly not sufficient to crash Godot.

  There is also something interesting here:

  ```text
  plugin._exit_tree: begin
  bridge EXIT_TREE
  dock EXIT_TREE
  dock UNPARENTED
  plugin._exit_tree: end
  dock PREDELETE
  bridge PREDELETE
  bridge UNPARENTED
  ```

  That is a clean teardown sequence for whichever process generated those lines. The bridge reached PREDELETE with no active thread and exited normally. That's a good control trace.

  What we need now is the same instrumentation on a crashing composed run, but with PID correlation. Then the comparison becomes genuinely useful:

  ```text
  SURVIVING PROCESS
  -----------------
  reload event
  Hermes lifecycle events
  thread state
  PREDELETE?
  wait_to_finish?
  survives

  CRASHING PROCESS
  ----------------
  reload event
  Hermes lifecycle events
  thread state
  PREDELETE?
  wait_to_finish?
  last recorded event
  SIGSEGV
  ```

  And I would add one more field while we're touching the probe: `OS.get_process_id()` is essential, because your launcher has several Godot-related processes alive simultaneously. Without PID, a shared `/tmp/.../hermes_lifecycle_trace.log` can make events from separate editors look causally connected when they aren't.

  So the current verdict is:

  ```text
  Hermes PREDELETE path is involved in some addon teardown.
  PREDELETE alone does not cause the crash.
  wait_to_finish was NOT exercised in the captured teardown.
  The current trace mixes process timelines.
  Root cause remains open.
  ```

  The next instrumentation change is tiny but important: **PID on every trace record before another crash test.**

● Update(/mnt/data-drive/godot_engain_3d_avatar/addons/hermes_editor/_lifecycle_probe.gd)
Added 10 lines
## mutation, and the sealed Main.tscn baseline restore before/after each
## case stays meaningful.
##
## CORRECTION (after the first captured trace): launch_dragon3d.sh keeps
## more than one Godot process alive at once (editor sidecar + composed
## runtime), and every process shares this one log path. Without a
## per-line process identity, two processes' lifecycle events interleave
## in the file and a monotonic-looking t_usec column can appear to jump
## backward across the boundary — that is a real, observed failure mode,
## not a hypothetical one. Every line now carries OS.get_process_id() so
## a crashing process's timeline can be isolated from a surviving one's
## by filtering on pid alone.
##
## Every write does its own open/write/close (no buffered handle kept
## across calls) specifically so that whatever line was written most
## recently is durable even if the process SIGSEGVs immediately after —

● Update(/mnt/data-drive/godot_engain_3d_avatar/addons/hermes_editor/_lifecycle_probe.gd)
Added 3 lines, removed 1 line
  var writer := FileAccess.open(LOG_PATH, FileAccess.WRITE)
  if writer != null:
    var wall_clock := Time.get_datetime_string_from_system(false, true)
    var line := "%s | t_usec=%d | %s\n" % [wall_clock, Time.get_ticks_usec(), event]
    var line := "%s | pid=%d | t_usec=%d | %s\n" % [
      wall_clock, OS.get_process_id(), Time.get_ticks_usec(), event
    ]
    writer.store_string(existing + line)
    writer.close()
  _mutex.unlock()

Now add a _bridge_trace helper to hermes_bridge.gd and route every call through it, carrying bridge_id/thread_started/thread_body_active on every line:

● Update(/mnt/data-drive/godot_engain_3d_avatar/addons/hermes_editor/hermes_bridge.gd)
Added 13 lines
var _discard_pending: bool = false
var _thread_body_active: bool = false  # INSTRUMENTATION — see _run_hermes()/_run_hermes_impl() split below


## INSTRUMENTATION — routes every bridge trace line through one place so
## bridge_id/thread_started/thread_body_active are on EVERY line, not
## just the ones that happened to mention them by hand. pid is added by
## LifecycleProbe.trace() itself.
func _bridge_trace(event: String) -> void:
  var thread_started := _thread != null and _thread.is_started()
  LifecycleProbe.trace(
    "bridge_id=%d | thread_started=%s | thread_body_active=%s | %s" % [
      get_instance_id(), str(thread_started), str(_thread_body_active), event
    ]
  )

const _SESSION_ID_LINE_PATTERN := "^session_id:\\s*(\\S+)\\s*$"
const SCRATCH_DIR_NAME := ".hermes_scratch"
const MODE_SAFE_REVIEW := "SAFE_REVIEW"

● Update(/mnt/data-drive/godot_engain_3d_avatar/addons/hermes_editor/hermes_bridge.gd)
Added 6 lines, removed 10 lines
## hermes/model call takes), but it is not instant either.
func _notification(what: int) -> void:
  if what == NOTIFICATION_PREDELETE:
    LifecycleProbe.trace(
      "bridge._notification: NOTIFICATION_PREDELETE begin (thread_started=%s, thread_body_active=%s)" % [
        str(_thread != null and _thread.is_started()), str(_thread_body_active)
      ]
    )
    _bridge_trace("_notification: NOTIFICATION_PREDELETE begin")
    if _thread != null and _thread.is_started():
      LifecycleProbe.trace("bridge._notification: entering _thread.wait_to_finish() — will block here if the t
hread body is still running")
      _bridge_trace("_notification: entering _thread.wait_to_finish() — will block here if the thread body is
still running")
      _thread.wait_to_finish()
      LifecycleProbe.trace("bridge._notification: _thread.wait_to_finish() returned")
    LifecycleProbe.trace("bridge._notification: NOTIFICATION_PREDELETE end")
      _bridge_trace("_notification: _thread.wait_to_finish() returned")
    _bridge_trace("_notification: NOTIFICATION_PREDELETE end")
  elif what == NOTIFICATION_EXIT_TREE:
    LifecycleProbe.trace("bridge._notification: NOTIFICATION_EXIT_TREE")
    _bridge_trace("_notification: NOTIFICATION_EXIT_TREE")
  elif what == NOTIFICATION_UNPARENTED:
    LifecycleProbe.trace("bridge._notification: NOTIFICATION_UNPARENTED")
    _bridge_trace("_notification: NOTIFICATION_UNPARENTED")


## Starts one turn in a background thread — OS.execute() blocks, and a

● Update(/mnt/data-drive/godot_engain_3d_avatar/addons/hermes_editor/hermes_bridge.gd)
Added 1 line, removed 1 line
    _thread.wait_to_finish()
  var hermes_path := find_hermes_executable()
  _thread = Thread.new()
  LifecycleProbe.trace("bridge.send: starting new turn thread")
  _bridge_trace("send: starting new turn thread")
  _thread.start(_run_hermes.bind(hermes_path, message, session_id, model, provider, project_root(), mode))



● Update(/mnt/data-drive/godot_engain_3d_avatar/addons/hermes_editor/hermes_bridge.gd)
Added 2 lines, removed 2 lines
  mode: String
) -> void:
  _thread_body_active = true
  LifecycleProbe.trace("bridge._run_hermes: thread body entered")
  _bridge_trace("_run_hermes: thread body entered")
  _run_hermes_impl(hermes_path, message, resume_session_id, model, provider, cwd, mode)
  LifecycleProbe.trace("bridge._run_hermes: thread body returning")
  _bridge_trace("_run_hermes: thread body returning")
  _thread_body_active = false



● Update(/mnt/data-drive/godot_engain_3d_avatar/addons/hermes_editor/hermes_dock.gd)
Added 16 lines, removed 9 lines


func _ready() -> void:
  LifecycleProbe.trace("dock._ready: begin (dock instance id=%d)" % get_instance_id())
  _dock_trace("_ready: begin")
  _build_ui()
  _bridge = HermesBridgeScript.new()
  add_child(_bridge)

  # _ensure_scratch_setup() for why this was moved out of _run_hermes().
  HermesBridgeScript._ensure_scratch_setup(HermesBridgeScript.project_root())
  _ensure_temporary_trial_ui()
  LifecycleProbe.trace("dock._ready: end (bridge instance id=%d)" % _bridge.get_instance_id())
  _dock_trace("_ready: end (bridge_id=%d)" % _bridge.get_instance_id())


## INSTRUMENTATION — see _lifecycle_probe.gd. Answers, for the dock
## Control itself (not the bridge Node — see hermes_bridge.gd's own
## _notification()), whether an external Main.tscn reload ever frees,
## exits, or unparents this dock.
## INSTRUMENTATION — routes every dock trace line through one place so
## dock_id is on EVERY line. pid is added by LifecycleProbe.trace()
## itself.
func _dock_trace(event: String) -> void:
  LifecycleProbe.trace("dock_id=%d | %s" % [get_instance_id(), event])


## See _lifecycle_probe.gd. Answers, for the dock Control itself (not
## the bridge Node — see hermes_bridge.gd's own _notification()),
## whether an external Main.tscn reload ever frees, exits, or unparents
## this dock.
func _notification(what: int) -> void:
  if what == NOTIFICATION_PREDELETE:
    LifecycleProbe.trace("dock._notification: NOTIFICATION_PREDELETE")
    _dock_trace("_notification: NOTIFICATION_PREDELETE")
  elif what == NOTIFICATION_EXIT_TREE:
    LifecycleProbe.trace("dock._notification: NOTIFICATION_EXIT_TREE")
    _dock_trace("_notification: NOTIFICATION_EXIT_TREE")
  elif what == NOTIFICATION_UNPARENTED:
    LifecycleProbe.trace("dock._notification: NOTIFICATION_UNPARENTED")
    _dock_trace("_notification: NOTIFICATION_UNPARENTED")


func _process(_delta: float) -> void:

  Searched for 1 pattern

All routed correctly — every bridge line now carries bridge_id/thread_started/thread_body_active, every dock line carries dock_id, every line from all three files carries pid automatically via LifecycleProbe.trace(). Let's clear the stale mixed-process log and confirm the file parses (quick headless syntax check):

  Ran 1 shell command

PID (auto, on every line via LifecycleProbe.trace()) plus per-object instance IDs are in now, exactly to your spec:

- bridge lines: pid | bridge_id | thread_started | thread_body_active | event — every _bridge_trace() call carries all four, not just the PREDELETE ones.
- dock lines: pid | dock_id | event — every _dock_trace() call.
- plugin lines: pid | event — unchanged shape, now with pid folded in automatically.

_lifecycle_probe.gd's doc comment now records why this was added (the mixed-process interleave you caught), and I cleared the stale log so the next run starts clean. Quick headless load of plugin.gd (which pulls in hermes_dock.gd/hermes_bridge.gd via preload) came back with no parser errors.

Your read on the captured trace matches what I see too: that teardown sequence (plugin._exit_tree → bridge/dock EXIT_TREE → dock UNPARENTED → dock/bridge PREDELETE → bridge UNPARENTED, all with thread_started=false) is a clean, ordinary plugin-disable/editor-close, not a Main.tscn-reload-triggered teardown — so it doesn't actually tell us anything about the reload path yet, crash or no crash. The wait_to_finish() branch not firing here doesn't weaken the theory for the reload case specifically, since we don't yet have a trace line proving that teardown was reload-caused rather than ordinary shutdown. With pid now on every line you can filter to the one process that actually SIGSEGVs and read its timeline in isolation — that's the run worth capturing next.

Ready when you are to run the crashing case again.

✻ Churned for 1m 48s

※ recap: We're tracing whether the Hermes addon's teardown causes the Godot editor crash on external scene reload. I added PID/instance-ID tags to the trace log; next step is to reproduce the crash and read the log for that process. (disable recaps in /config)

● Remote Control disconnected — OAuth token refresh failed — run /login to re-authenticate
                                                        get pinged when Claude finishes · enable push notifications in /config
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
❯
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ⏵⏵ auto mode on (shift+tab to cycle) · ← for agents
