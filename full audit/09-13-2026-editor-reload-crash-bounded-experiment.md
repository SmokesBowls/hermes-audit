# 09-13-2026 — Editor reload crash: trace + bounded experiment (not yet a fix)

## Trace findings (verification_monolith_04 crash, PID 1803107)

Precise timeline, all from real evidence (mtimes, `coredumpctl info`,
the project's own pre-existing `hermes_lifecycle_trace.log`):

```
09:45:31  Dragon request published (dragonreq_20260913_164531_e23c93c3)
09:55:52  Hermes turn thread starts
09:58:10  VerificationMonolith04.tscn written
09:58:17  Main.tscn written (instances the monolith)
09:59:01  ad-hoc validation subprocess: status:"PASS"
09:59:14  EditorFileSystem.sources_changed fires
09:59:32  EditorFileSystem.sources_changed fires -- LAST line in the
          entire trace log
09:59:34  godot --editor (PID 1803107) aborts, SIGABRT
```

The project had already built its own instrumentation for exactly this
question (`addons/hermes_editor/_lifecycle_probe.gd` + `plugin.gd`'s
`_connect_reload_probes()`, both predating this session). Reading
`/tmp/engain-debug-evidence/hermes_lifecycle_trace.log` directly: the
Hermes plugin (dock/bridge/threads) produces **zero** trace lines in the
~2.5 minutes before the abort — no thread activity, no
`NOTIFICATION_EXIT_TREE`/`PREDELETE`. Only Godot's own internal
`EditorFileSystem.sources_changed` fires, repeatedly, right up to 2
seconds before the crash.

**Proven**: the plugin was idle during the crash window; the fault is in
Godot's own editor-side reload/reconciliation, entered only after
"Reload from disk" is accepted.
**Not proven**: that the specific cause is new-subscene/UID
reconciliation (plausible, matches the evidence, not isolated as the
exact engine invariant) — or that any particular API call avoids the
same internal path.

Confirmed via `strings` on the actual installed Godot 4.6.1 binary (not
assumed): `EditorInterface.reload_scene_from_path()` is a real, exposed
method in this exact build.

## User's correction, accepted

Proposing `reload_scene_from_path()` as *the fix* would have been
premature — it may call the same crashing internal machinery the
dialog's own button does. Correct next step is a bounded, reversible
experiment that answers exactly one question: does this API survive
where the manual dialog does not, in this exact workflow?

## Experiment wired (not adopted as the fix)

`hermes_dock.gd`: `_experimental_reload_edited_scene_via_api()`, called
right after a successful DIRECT_WRITE turn with real live-tree changes.
Calls `editor_interface.reload_scene_from_path("res://scenes/Main.tscn")`,
traced immediately before and after via the existing `LifecycleProbe` —
so if the next crash's trace log ends at "...about to call..." with no
"...returned normally," the API call itself is where it died (same as
the manual button); if "...returned normally" appears, this survived a
case the dialog does not. Explicitly labeled experimental in its own
doc comment; narrow (only `Main.tscn`, only on a real change, no
toggle); does not touch runtime auto-reload, continuity, timeouts,
authority, or the lost-HUD-text issue.

## Why this can't be proven by an automated test

Requires a live, already-open editor session with `Main.tscn` open and
an actual human-clicked Execute (DIRECT_WRITE) — exactly the condition
under investigation. Parse-checked clean
(`godot --headless --check-only`) and the existing
`test_hermes_bridge_logic.gd` suite (unaffected, `editor_interface` is
null in that headless context so the new function no-ops safely) — but
the actual experiment needs one more live, human-triggered DIRECT_WRITE
turn, then reading the trace log afterward.

## Next step (not done yet)

Have Dragon make one more harmless, uniquely-identifiable edit request;
click Execute as normal; read `hermes_lifecycle_trace.log`'s tail
afterward together. Two outcomes: survives with "returned normally" and
no dialog → real candidate fix, worth adopting deliberately next time;
aborts at or before the reload call → rules this API out, and the
problem is confirmed to sit deeper inside Godot's own reload internals,
not reachable by this session's code.
