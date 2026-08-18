# dragon_3d Launch Wrapper — Continuation-TODO Item 4, Phase 1

Written 2026-08-17, same day as the continuation TODO
(`08-17-2026-continuation-todo.md`) this resolves item 4 for. Triggered by
a real, reproduced live failure — not a hypothetical: Godot was running
(bare `godot --path /mnt/data-drive/godot_engain_3d_avatar`, launched
directly from a shell) and a chat submission returned
`LISTENER_ABSENT: no live mailbox worker`.

This document covers **Phase 1 only** — the launch-path fix and its live
proof. Phase 2 (structured `LISTENER_ABSENT` diagnostics) is a separate
receipt, written only after this one was GREEN, per explicit instruction
not to mix the two. TODO items 1, 2, 3, and 5 were not touched.

## Diagnosis

Traced the real process tree for the running Godot instance
(`/proc/<pid>/cmdline`, parent chain) rather than assuming. Findings:

- The running `godot` process's parent was a bare interactive bash shell,
  not `runtime_composition.py`. No `runtime_composition.py`,
  `presence_authority_server.py`, or any Hermes adapter process existed
  anywhere in the process table.
- `presence_authority_server.py`'s `/health` (port 8767) refused the
  connection.
- `/mnt/data-drive/engain-runtime-mailboxes/dragon3d/` was completely
  empty — no `listener.json` had ever been written.
- That bare Godot process, additionally, had never mapped an X11 window at
  all (confirmed via `xdotool search --pid`), and was found to have
  already exited on its own by the time of inspection — it was not a
  healthy runtime silently missing one component, it was simply not the
  right way to start this project.

Root cause, one sentence: **nothing in this environment invoked
`runtime_composition.py`; Godot was being started as a bare binary, so the
presence authority and the Hermes mailbox worker never launched.** This is
exactly continuation-TODO item 4 ("composing this with the real Godot
launcher hasn't been attempted"), now manifesting as a concrete
production symptom rather than a named gap.

`hermes_session_adapter.py`'s `publish_request()` checks
`_listener_is_live()` (a `listener.json` lease, `LISTENER_LEASE_SECONDS =
2.0`, refreshed every `process_once()` tick by the worker's own service
loop) before admitting a request; with no adapter ever having run a
single tick, that check fails immediately, which is the exact and only
source of the `LISTENER_ABSENT` error observed. Nothing about the lease
mechanism itself is broken.

## Fix: `launch_dragon3d.sh`

Verified `runtime_composition.py`'s existing CLI contract first
(`python3 runtime_composition.py --help`) rather than assuming the
intended command line was already supported — it was: `--godot-command`,
`--project-dir`, `--presence-authority-script`, and related presence-
authority flags already exist exactly as needed. No changes to
`runtime_composition.py`, `runtime_launcher.py`, the presence authority,
or the Hermes adapter were made or needed — the live composed launch
exposed no defect in any of them.

Added one file, `godot_engain_3d_avatar/launch_dragon3d.sh` — the new
canonical entrypoint for this avatar. It:

- resolves its own real location via `${BASH_SOURCE[0]}`, independent of
  the caller's working directory;
- sets `--project-dir` to that resolved location (which is
  `/mnt/data-drive/godot_engain_3d_avatar`, matching
  `CANONICAL_PROJECT_ROOT`);
- sets `--presence-authority-script` to the canonical EngAIn checkout's
  `tier1/engainos/server/presence_authority_server.py`, path overridable
  via `ENGAIN_REPO_ROOT` for anyone working from a different checkout,
  defaulting to the known canonical location;
- `exec`s directly into `python3 runtime_composition.py ...` — no
  intermediate shell survives, so signals (SIGINT/SIGTERM) reach
  `runtime_composition.py`'s own installed handlers directly, and the
  wrapper's exit code is exactly `runtime_composition.py`'s own returned
  exit code (itself Godot's real exit code, per `main()`'s existing
  contract) with no translation layer;
- touches `ENGAIN_CONTINUITY_DISPATCH` nowhere — inherited from the
  caller's environment exactly as before (confirmed unset in this
  session before launch);
- embeds no provider/model/session identity — none of that belongs to a
  launch wrapper, and none was added; it remains entirely owned by
  `AdapterConfig`'s existing frozen fields.

## Live proof, in the order asked for

Killed the pre-existing bare `godot` process first (it had, as noted
above, already exited on its own). Then ran
`./launch_dragon3d.sh > dragon3d_launch.log 2>&1 &` from a completely
unrelated working directory, to prove cwd-independence.

1. **`runtime_composition.py` actually running** — confirmed via `ps -ef`:
   `python3 .../runtime_composition.py --godot-command godot
   --project-dir /mnt/data-drive/godot_engain_3d_avatar
   --presence-authority-script .../presence_authority_server.py`, exact
   args the wrapper was supposed to produce.
2. **`presence_authority_server.py` running, `/health` succeeds** —
   confirmed as a child process of the composition PID; `curl
   127.0.0.1:8767/health` → `{"status": "healthy"}`.
3. **`dragon3d/listener.json` appears** — confirmed, written within the
   same second the composition process started.
4. **Its PID corresponds to a live worker** — `listener.json`'s `pid`
   field matched the running `runtime_composition.py` PID exactly (the
   adapter's service loop runs as an in-process thread inside that same
   process, per `PersistentAdapterService`/`ComposedWorker` — there is no
   separate adapter subprocess in this composition, by design).
5. **`expires_at` advances over multiple observations** — read four times
   at ~1s intervals; `expires_at` increased on every read (renewal, not a
   one-shot write): observed values increased monotonically across all
   four reads, each roughly one lease period apart, confirming the
   service loop's own poll tick is what keeps the lease alive.
6. **Godot starts only after the supervised worker is ready** — confirmed
   by log ordering: `POST /presence/register` succeeded (i.e.
   `HermesSessionAdapter.prepare()` had already completed, setting
   `worker_state = READY`) strictly before the `Godot Engine v4.6.1...`
   startup banner appears in the same log, matching
   `run_runtime_generation`'s own enforced ordering
   (`worker.prepare()` → assert `READY` → only then `godot_launcher()`).
7. **Sending `hi` from the actual ControlHUD no longer returns
   `LISTENER_ABSENT`** — found the real Godot window via `xdotool search
   --pid`, clicked its `CollaborationInput` field, typed `hi`, pressed
   Enter (the HUD's own submit binding, `text_submitted`). Screenshot
   (`evidence/.../02_after_submit.png`) shows `[YOU] hi` accepted and
   "Dragon is thinking…", no error line.
8. **The request receives a real response through the composed runtime**
   — confirmed via the log (`Processed EngAIn request:
   req_3607a4b582e10039def32ea36f3047e1`, with a `/claim`+`/release`
   pair against the presence authority around it) and a follow-up
   screenshot (`evidence/.../03_response.png`) showing
   `[DRAGON] Hi—I'm here with you.` rendered in the actual HUD.
9. **Closing the runtime cleans up the supervised processes correctly** —
   sent `SIGTERM` to the composition process. Within 3s: the composition
   process, its Godot child, and the presence-authority child were all
   gone (`ps -ef` empty for all three PIDs), `/health` refused the
   connection again, and no defunct/zombie processes remained. Shutdown
   order matched `run_concrete_runtime`'s documented contract (worker →
   Godot reap → ownership release → authority stop last).

All nine points hold. Screenshots and the full launch log are committed
alongside this file under `evidence/08-17-2026-dragon3d-launch-wrapper/`.

## Tests

```
cd /mnt/data-drive/godot_engain_3d_avatar && python3 -m pytest -q
```
`260 passed, 3 failed` — the exact same three pre-existing
`test_stage8_ticket3b_worker_ownership_red.py` failures the continuation
TODO already named as unrelated ("RED" tests asserting a boundary that
doesn't exist yet, same failures the last full audit recorded). No new
failures; no regressions from adding the wrapper script, which is
consistent with it containing no logic beyond argument resolution and an
`exec` into already-tested code.

## What this does and doesn't establish

Establishes: continuation-TODO item 4's actual runtime gap was exactly
what it was named as — nobody invoking the composed launcher — and it is
now closed for the standard case. `launch_dragon3d.sh` is the documented,
canonical way to start this avatar from here forward; running
`godot --path ...` directly is no longer the supported path (the script
itself says so in its header comment).

Does not establish: anything about TODO items 1 (concurrent-`/dispatch`
mutex), 2 (Ledger/cursor restart persistence), 3 (production cutover
decision), or 5 (`provider_session_ref` limitation) — none were touched,
per instruction. Also does not change `ENGAIN_CONTINUITY_DISPATCH`'s
default (still unset/opt-in) — this proof exercised the pre-existing
direct-Hermes dispatch path, not the newer `/dispatch`-through-EngAIn
path from the prior day's integration proof.

## Next

Phase 2: structured `LISTENER_ABSENT` failure propagation (machine-
readable diagnostic fields, rendered by `EngAInBridge3D.gd` into operator-
useful text, recovery information sourced from the runtime/config that
owns the worker relationship — not hard-coded into GDScript). Separate
receipt, only after this one.
