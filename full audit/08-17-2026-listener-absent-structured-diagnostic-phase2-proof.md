# Structured `LISTENER_ABSENT` Diagnostics — Continuation-TODO Item 4, Phase 2

Written 2026-08-17, immediately after Phase 1
(`08-17-2026-dragon3d-launch-wrapper-phase1-proof.md`) was confirmed
GREEN. Phase 1 proved the launch-path gap was the real and only cause of
`LISTENER_ABSENT`; this phase turns that error from a bare, unstructured
string into an operator-actionable diagnostic, without concealing or
substituting for Phase 1's fix. TODO items 1, 2, 3, and 5 were not
touched.

## Problem being fixed

Before this change, `EngAInBridge3D.gd`'s only handling of a failed
`--publish-request` call was:
```gdscript
_emit_err("Request publication failed: " + publication["output"])
```
— the raw, concatenated stdout/stderr of the Python adapter subprocess,
verbatim. For `LISTENER_ABSENT` specifically, that put a bare
`LISTENER_ABSENT: no live mailbox worker` on screen with no indication of
which worker, which mailbox, or how to recover — "there is no engine in
your car" with no pointer to the ignition.

## Design

The diagnostic's fields and their source of truth:

- `hermes_session_adapter.py` gains `ListenerAbsentError(HermesAdapterError)`,
  raised by `publish_request()` in exactly the one place the old bare
  `HermesAdapterError("LISTENER_ABSENT: ...")` used to be raised.
  `str(exc)` is unchanged (`"LISTENER_ABSENT: no live mailbox worker"`),
  so every existing caller/test that only knows `HermesAdapterError`
  behaves identically. It additionally carries `.diagnostic`, a dict with
  `code`, `agent_id`, `mailbox_path`, `presence_state`, `launcher`, and
  `recovery_action` — built by a new `_listener_absent_diagnostic()`
  method on `HermesSessionAdapter`, which is the one place in the system
  that already knows its own `project_dir`, `CALLER_ID`, and mailbox
  layout.
- Critically, `recovery_action`/`launcher` point at
  **`launch_dragon3d.sh`** — the canonical entrypoint Phase 1 added,
  computed as `self.config.project_dir / "launch_dragon3d.sh"`. The
  adapter (which lives in the same repo, beside that script) is the
  runtime that actually owns the worker/launcher relationship; nothing
  about how to start Hermes or Godot is taught to, or guessed by,
  GDScript.
- The `--publish-request` CLI handler catches `ListenerAbsentError`
  specifically (before the pre-existing generic `HermesAdapterError`
  catch, which still handles every other failure unchanged) and prints
  one extra line to stderr:
  `ENGAIN_LISTENER_ABSENT_DIAGNOSTIC=<json>`, ahead of the existing
  plain-text `request publication rejected: ...` line — so tooling that
  only reads the old plain-text line sees no change.
- `EngAInBridge3D.gd` gained `_render_publication_failure(output)`: scans
  the captured output for that marker line, parses the JSON with this
  file's existing strict `JSON.new()`/`.parse()`/`get_error()` convention
  (matched exactly — an earlier attempt using `JSON.parse_string` was
  rejected by this repo's own `test_malformed_and_unknown_response_content_is_rejected`,
  which asserts that convention isn't used in this file), and if it's a
  well-formed diagnostic, renders:
  ```
  [<code>] no live mailbox worker for '<agent_id>'.
  Mailbox: <mailbox_path>
  Presence lease: <presence_state>
  To fix: <recovery_action>
  ```
  For anything else — a diagnostic-less failure, a malformed payload, any
  other error entirely — it falls back to the exact original
  `"Request publication failed: " + output` text, unchanged.

No hard-coded shell command was ever written into the `.gd` file; it
renders whatever the adapter's diagnostic says and nothing more.

## Live proof

Confirmed the mailbox was empty (no worker) — deliberately withheld it —
then launched Godot bare again (`godot --path
/mnt/data-drive/godot_engain_3d_avatar`, same as the original failure
mode this whole investigation started from) and submitted `hi` through
the real `CollaborationInput` field via the actual ControlHUD, same
method as Phase 1's positive proof.

Screenshot (`evidence/.../05_listener_absent_diagnostic.png`) shows the
HUD rendering:
```
[ERR] [LISTENER_ABSENT] no live mailbox worker for 'dragon3d'.
Mailbox: /mnt/data-drive/engain-runtime-mailboxes/dragon3d
Presence lease: ABSENT
To fix: Start the dragon_3d runtime: /mnt/data-drive/godot_engain_3d_avatar/launch_dragon3d.sh
```
in place of the old bare `LISTENER_ABSENT: no live mailbox worker` line —
confirming the diagnostic reaches the real UI end to end, and that it
correctly names the exact script Phase 1 proved brings the worker up.

## Tests

```
cd /mnt/data-drive/godot_engain_3d_avatar && python3 -m pytest -q
```
`260 passed, 3 failed` — the same three pre-existing, unrelated
`test_stage8_ticket3b_worker_ownership_red.py` failures from Phase 1 and
the last full audit; no new failures. One regression was caught and
fixed during development: the first draft used
`JSON.parse_string(payload)` in the new GDScript helper, which broke
`test_stage6a_godot_mailbox_bridge.py::test_malformed_and_unknown_response_content_is_rejected`
(this file's tests enforce `JSON.new()`/`.parse()`/`get_error()`
throughout, not `JSON.parse_string`); rewritten to match the existing
convention and the suite returned to the Phase 1 baseline.

## What this does and doesn't establish

Establishes: `LISTENER_ABSENT` is now a structured, machine-readable
diagnostic (`code`/`agent_id`/`mailbox_path`/`presence_state`/
`recovery_action`/`launcher`) with a real, working fallback path, sourced
entirely from the runtime that owns the worker relationship, rendered
without teaching the HUD anything about how to launch a worker.

Does not establish: coverage for `MAILBOX_BUSY`/`MAILBOX_STALE` or a
"worker died mid-run vs. never started" distinction — both named as
future extensions in the original design discussion, not built here.
Does not touch TODO items 1, 2, 3, or 5.
