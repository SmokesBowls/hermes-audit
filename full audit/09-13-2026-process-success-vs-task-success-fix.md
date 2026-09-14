# 09-13-2026 — process_success vs task_success (load_probe_halo_06 no-op, fixed)

## Root cause (traced via `hermes sessions export`, not guessed)

`load_probe_halo_06`'s real Hermes session transcript ended with:

```
TERMINAL_STATUS: BLOCKED
...
BLOCKER: The prerequisite terminal inspection was explicitly denied by the
user/tool authorization boundary. Per that denial, I did not retry, bypass
it, inspect through an alternate route, or modify the live project.
STATUS: NOT_COMPLETED

No project files were changed.
```

Hermes had loaded its own pre-installed `human-driven-runtime-integration-
testing` skill (predates this session), whose Hard Boundary forbids it from
inspecting/verifying the live GUI/runtime itself. The request explicitly
asked it to "exercise the... runtime-reload path... report COMPLETED only
if the running world consumes the halo" — exactly what that skill reserves
for the human. Hermes correctly refused rather than fabricate a
verification claim it couldn't honestly make, and its own todo list shows
`inspect` started then cancelled, `create`/`validate`/`reload` never
attempted at all.

Confirmed independently (not just from the transcript): fingerprint diff
showed zero `live_tree_changes`; `LoadProbeHalo06.tscn` doesn't exist
anywhere (live tree, `.hermes_scratch/`, or git status).

**The actual bug, in our own code**: `hermes_bridge.gd`'s
`build_editor_report()` derived `status: "applied"` purely from
`edit_result["success"]` — the Hermes CLI subprocess's exit code. Hermes
exited 0 (it answered cleanly, it just declined to act), so the
coordination report claimed `applied`/DONE with zero files changed,
completely silent about Hermes's own explicit refusal.

## Fix

`extract_task_disposition(response_text)` — scans for Hermes's own
`TERMINAL_STATUS:`/`STATUS:` line; `BLOCKED`/`REFUSED`/`NOT_COMPLETED`/
`FAILED` → explicit non-completion, `COMPLETED` → explicit completion,
neither found → `""` (unknown, never treated as either outcome). Also
extracts a real `BLOCKER:` line when present for an honest, non-generic
error message.

`build_editor_report()`: `process_success` (the literal exit-code fact)
is now distinct from `task_blocked` (process succeeded but Hermes
explicitly said otherwise) and `succeeded` (`process_success and not
task_blocked` — the only thing gating `applied`). A blocked turn gets its
own `TASK_NOT_COMPLETED` error code (distinct from process-level
`TURN_FAILED`), carrying Hermes's own real blocker text.

Deliberately conservative: absence of any status marker changes nothing —
`succeeded` still equals `process_success` exactly as before. This is a
downgrade-only correction; it never invents a new path to claiming
success. The vast majority of ordinary turns (no such reporting
convention at all) are completely unaffected.

## Tests

`test_hermes_bridge_logic.gd`, all four required cases plus two pure
unit checks on the parser: exit 0 + `COMPLETED` → applied; exit 0 +
`BLOCKED`/`NOT_COMPLETED` → failed with `TASK_NOT_COMPLETED` and
Hermes's real blocker text (reproduces `load_probe_halo_06` verbatim);
nonzero exit → failed via the original `TURN_FAILED` path, unaffected;
exit 0 + no marker → still applied, existing fallback preserved exactly.
**ALL CHECKS PASSED**, including every pre-existing assertion in the
suite.

## Correction 2 — not a code change

For the next live probe: stop asking Hermes to verify runtime/viewport/
reload outcomes in the `[EDITOR_REQUEST]` body. Ask only for the file
edit + file-level validation; leave runtime consumption and visual
confirmation to the human or to the machinery already being tested
(mailbox artifacts, the mtime-triggered reload experiment). Nothing to
implement — this is a request-phrasing decision for whoever authors the
next `[EDITOR_REQUEST]`.

## What this unblocks

The next live DIRECT_WRITE probe, phrased per correction 2, should
actually write files this time — which is also the first real chance for
the `Main.tscn` mtime → `reload_scene_from_path()` experiment (still
pending its own first real observation) to finally fire.
