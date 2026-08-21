

❯ find the todo... i had you add to it before we ended last

  Searched for 1 pattern, read 1 file, ran 2 shell commands

Found it: full audit/08-17-2026-continuation-todo.md — added in commit 2429840.

Continuation TODO — Avatar Continuity Integration, Next Phase (written 2026-08-17)

State: all four repos (EngAIn, engain_avatar, godot_engain_3d_avatar, this audit repo) committed but not pushed. Offline suites green (215/215, 86/86, 260/263 with 3 pre-existing unrelated RED failures). ENGAIN_CONTINUITY_DISPATCH is opt-in/unset — inert in normal runtime.

Five open items, in pickup order:

1. Concurrent-/dispatch mutex for overridden bindings — no lock protects explicit-override callers today (only the default frozen-Hermes binding is protected, via the pre-existing worker claim). Two options sketched (extend SessionClaimRegistry keyed on (provider_id, provider_session_id), or something else) — not decided, flagged for review before implementing since it changes a contract.
2. Ledger/cursor persistence across a restart — currently in-memory only, explicitly deferred. Needs either real persistence or a documented reconstruction-from-receipts scheme; also worth re-deriving what's actually still missing given the discovery that a dispatched recap becomes permanent native-side state regardless of EngAIn.
3. Production cutover decision — not yet made. Turning ENGAIN_CONTINUITY_DISPATCH on by default or retiring the old direct-Hermes path is a separate real decision with feature-coverage tradeoffs, not to be done by accident.
4. Real Godot launch through this integration — proof ran standalone file-mailbox workers, not through runtime_composition.py/SupervisedPresenceAuthority's full launcher. Not yet attempted.
5. provider_session_ref's frozen-identity limitation — named, not fixed; only matters if something starts trusting that field as ground truth for provider/model/session_id (nothing does today).

Where to resume: presence_authority_server.py (/dispatch handler), engain_continuity_client.py + hermes_session_adapter.py's three new methods, the live proof script, and this audit repo's chronological 08-17-2026-*.md files for full reasoning.

Want me to start on item 1 (the dispatch mutex design), or something else first?

✻ Baked for 14s

❯ /auto-mode-setup
  ⎿  Gathering data and drafting your auto-mode setup; back soon

● Auto-mode proposal discarded — nothing was saved. Re-run /auto-mode-setup anytime.

※ recap: We're building EngAIn's avatar continuity integration, now planning the next phase after finishing the proof. Next up: decide the concurrent-dispatch mutex design for overridden bindings before implementing it. (disable recaps in /config)

❯ Do item 4 first.

  That TODO was written before we had the concrete screen in front of us showing:

  `LISTENER_ABSENT: no live mailbox worker`

  Item 1 is important concurrency hardening, but it will not make a missing 3D worker appear. Item 4 is exactly where tonight’s failure lives:

  > “Real Godot launch through this integration — proof ran standalone file-mailbox workers, not through `runtime_composition.py` / `SupervisedPresenceAuthority`.”

  The standalone machinery was proven. The actual Godot runtime has now demonstrated that the worker is not being brought up with it. That gap should be resolved before designing the dispatch mutex.

  Tell Claude this:

  > Do not start item 1 yet. Pick up continuation TODO item 4 first because we now have a concrete live-runtime failure.
  >
  > The actual Godot 3D ControlHUD is running, but submitting a request returns:
  >
  > `LISTENER_ABSENT: no live mailbox worker`
  >
  > Start with diagnosis, not implementation.
  >
  > Trace the complete real launch path from `runtime_composition.py` through `SupervisedPresenceAuthority` and whatever is responsible for starting, claiming, and renewing the `dragon_3d` mailbox worker.
  >
  > Establish precisely:
  >
  > 1. What process/component is supposed to create the `dragon_3d` worker.
  > 2. What function launches it.
  > 3. Whether `runtime_composition.py` actually invokes that function in the real Godot launch.
  > 4. Whether the worker reaches readiness.
  > 5. Whether it registers presence.
  > 6. Whether its 2-second readiness/presence lease is renewed.
  > 7. Whether it uses the expected mailbox:
  >    `/mnt/data-drive/engain-runtime-mailboxes/dragon3d/`
  > 8. Whether the worker exits, fails startup, is never composed, or publishes under the wrong identity/path.
  >
  > Reproduce the failure through the real Godot launcher rather than the standalone proof.
  >
  > Do not enable `ENGAIN_CONTINUITY_DISPATCH` globally as part of this work. Do not work on the mutex, restart persistence, production cutover, or `provider_session_ref` limitation yet.
  >
  > Before changing code, report the exact launch chain and the exact point where the expected worker disappears.
  >
  > Once the cause is established, make the smallest correction required to have the real supervised runtime bring the worker up and maintain its presence.
  >
  > Then run the relevant offline suites and a real Godot launch proof.
  >
  > Also inspect the current `LISTENER_ABSENT` propagation. If the runtime already knows the worker identity/startup mechanism, determine how the error can eventually include an actionable recovery instruction such as which worker is missing and what launcher/component is responsible for starting it. Do not hard-code a guessed shell command into Godot.
  >
  > Record the diagnosis, change, proof receipts, and remaining limitations in the audit repo.

  The sequence I want from Claude is therefore:

  **trace → explain → fix → prove → audit**

  not:

  **see TODO #1 → build mutex.**

  The live failure has effectively promoted item 4 above item 1. Exactly. `LISTENER_ABSENT` tells you what failed, but not what to do next. For a human-facing runtime error, that’s only half a diagnostic.

  It should tell you at least:

  ```text
  [ERR] LISTENER_ABSENT: no live mailbox worker

  Mailbox:
    /mnt/data-drive/engain-runtime-mailboxes/dragon3d/

  Required occupant:
    dragon_3d mailbox worker

  Status:
    No active readiness lease was found.

  To fix:
    Start the EngAIn 3D mailbox worker/provider runtime,
    then retry this request.

  Expected launcher:
    <actual command or launcher responsible for starting it>

  Diagnostic:
    <command for checking worker/presence status>
  ```

  And ideally EngAIn should know enough to be even more specific. Since the system already knows which door made the request, it should be able to say something like:

  ```text
  [ERR] LISTENER_ABSENT
  Dragon 3D is running, but its mailbox worker is not.

  Expected worker: dragon_3d
  Mailbox: /mnt/data-drive/engain-runtime-mailboxes/dragon3d/
  Presence lease: ABSENT

  Start it with:
      <real launcher command>

  Then press Enter to retry.
  ```

  The important architectural point is that we should **not hard-code some guessed shell command into the HUD**. The worker/launcher layer should expose its canonical startup instruction or launcher identity, and the failure object should carry that information upward.

  So eventually `LISTENER_ABSENT` probably wants structured diagnostic data roughly equivalent to:

  ```python
  {
      "code": "LISTENER_ABSENT",
      "agent_id": "dragon_3d",
      "mailbox_path": "/mnt/data-drive/engain-runtime-mailboxes/dragon3d/",
      "presence_state": "ABSENT",
      "launcher": "...",
      "recovery_action": "...",
  }
  ```

  Then Godot merely renders it. That prevents the HUD from having to understand how Hermes, Claude, or another future provider is actually launched.

  And there's another useful distinction it can expose:

  * **worker never started** → tell you how to start it
  * **worker died** → tell you it was previously present and stopped renewing
  * **worker starting** → tell you to wait/retry
  * **worker alive but mailbox busy** → `MAILBOX_BUSY`
  * **stale mailbox artifacts** → `MAILBOX_STALE`

  That turns this from an error code into an actual operator diagnostic.

  Right now the screen basically says, “There is no engine in your car.” It should also tell you where the ignition is.

  Searched for 1 pattern, ran 3 shell commands, recalled 1 memory

Found it — runtime_composition.py lives in godot_engain_3d_avatar, not EngAIn. Let me read the launch chain.

  Searched for 5 patterns, read 4 files, ran 7 shell commands

Diagnosis: LISTENER_ABSENT root cause, traced end-to-end

I traced the real launch chain and reproduced the exact failure state live (Godot is currently running on this machine, pid 33726). Here's what's actually happening, in order.

1–3. What's supposed to launch the dragon_3d worker, and does it?

runtime_composition.py:run_concrete_runtime() (in godot_engain_3d_avatar) is the only component that knows how to bring the worker up correctly. In order it:
1. Starts SupervisedPresenceAuthority (spawns EngAIn's presence_authority_server.py, health-checks /health before continuing)
2. Calls HermesSessionAdapter.prepare() → registers with the presence authority, sets worker_state = "READY", writes the first listener lease
3. Starts PersistentAdapterService — a thread that calls adapter.process_once() every poll_seconds (0.1s), which is what refreshes listener.json's 2-second lease on every tick
4. Only then launches Godot itself via create_godot_process()

This never ran. The currently-running Godot process (pid 33726) was launched as:
godot --path /mnt/data-drive/godot_engain_3d_avatar
directly from a bash shell (confirmed via /proc/33726/cmdline and process ancestry — parent is bash, not Python). No runtime_composition.py process exists anywhere in the process table, and presence_authority_server.py is not running either (curl 127.0.0.1:8767/health → connection refused). The bare godot binary was run instead of the composed launcher — the launcher itself is fine; nothing invoked it.

4. Does the worker reach readiness / 5. register presence / 6. renew its lease / 7. use the right mailbox

Irrelevant here — none of that code path ever started. Confirmed directly: /mnt/data-drive/engain-runtime-mailboxes/dragon3d/ is empty (no listener.json, request.json, or response.json), which is exactly the state you'd expect if HermesSessionAdapter.prepare()/process_once() never ran a single tick. (There is a stale .godot/engain_hermes_session.json from an earlier standalone run — that's session state, not mailbox liveness, and it's a red herring for this symptom.)

8. Where the worker "disappears"

It never existed for this Godot generation. hermes_session_adapter.py's publish_request() checks _listener_is_live() (listener.json must exist, have an unexpired expires_at, and a live pid) before linking the request into the mailbox. With no adapter ever having run, that check fails immediately → HermesAdapterError("LISTENER_ABSENT: no live mailbox worker").

How that error currently reaches you

EngAInBridge3D.gd shells out to the adapter per-call via OS.execute() (_execute_adapter()), and on a nonzero exit just does:
gdscript
_emit_err("Request publication failed: " + publication["output"])
output is the raw captured stdout/stderr — the bare Python exception string, unstructured, no context about which worker, which mailbox, or how to recover. That's exactly the "no engine in your car, doesn't say where the ignition is" gap you flagged.

---
Root cause, one sentence

Nothing in this environment invokes runtime_composition.py; Godot is being started as a bare binary, so the presence authority and the Hermes mailbox worker never launch, and the mailbox directory is permanently empty for any session started that way. This is exactly continuation-TODO item 4 — "composing this with the real Godot launcher hasn't been attempted" — now manifesting as the concrete failure you saw.

---
Proposed smallest correction

Add a launch wrapper (script, not a code change to the already-tested runtime_composition.py/runtime_launcher.py) that starts:
python3 runtime_composition.py --godot-command godot \
  --presence-authority-script <EngAIn>/tier1/engainos/server/presence_authority_server.py
so Godot is always started through the composition, never bare. No existing test/CI artifact documents this invocation today — there's no launch script in either avatar repo, so this is a genuine missing piece, not a regression.

Separately, for the structured LISTENER_ABSENT diagnostic you described: I'd have hermes_session_adapter.py's CLI entrypoint emit a small JSON error object (code/agent_id/mailbox_path/presence_state/recovery hint) instead of a bare string on this specific failure, and have EngAInBridge3D.gd render that structured payload instead of the raw stderr blob — the launcher identity would come from a single constant runtime_composition.py already owns (--presence-authority-script path / the module's own __main__ usage string), not something guessed or duplicated into GDScript.

Want me to proceed with both (wrapper script + the currently-running Godot process restarted through it, then the structured-error change), or just the wrapper first so we can prove the worker comes up before touching the error-propagation code?

✻ Sautéed for 3m 32s

※ recap: We're getting the Godot 3D avatar's mailbox worker running properly; found that Godot launches bare instead of through the supervised composition script, so the worker never starts. Next: write a launch wrapper script and restart Godot through it to confirm the fix. (disable recaps in /config)

❯ Proceed with both, but sequentially.

  First, fix the launch path and prove it by itself. The diagnosis is strong: nothing is wrong with the lease mechanism yet because the actual composed runtime never started. Don’t mix error-reporting changes into that proof.

  Tell Claude:

  > Proceed with both, but in two isolated phases.
  >
  > Phase 1: solve item 4 only.
  >
  > Create the smallest canonical launch entrypoint for `godot_engain_3d_avatar` that invokes the existing `runtime_composition.py` path rather than launching `godot --path ...` directly.
  >
  > Do not redesign `runtime_composition.py`, `runtime_launcher.py`, the presence authority, or Hermes adapter unless the live composed launch exposes an actual defect.
  >
  > Before writing the wrapper, verify the exact existing CLI/function contract rather than assuming the proposed command line is already supported.
  >
  > The wrapper must:
  >
  > * resolve its own repo location rather than depend on the current working directory;
  > * point Godot at `/mnt/data-drive/godot_engain_3d_avatar`;
  > * point the composition at the canonical EngAIn `presence_authority_server.py`;
  > * propagate the child/runtime exit code;
  > * not enable `ENGAIN_CONTINUITY_DISPATCH` globally;
  > * not embed a provider/model/session identity that belongs in provider configuration;
  > * cause shutdown cleanup to continue going through the existing supervision path.
  >
  > Then stop the currently bare-launched Godot instance and launch the real 3D project through this entrypoint.
  >
  > Prove, in order:
  >
  > 1. `runtime_composition.py` is actually running.
  > 2. `presence_authority_server.py` is actually running and `/health` succeeds.
  > 3. `dragon_3d/listener.json` appears.
  > 4. Its PID corresponds to a live worker.
  > 5. Its `expires_at` advances over multiple observations, proving renewal rather than merely creation.
  > 6. Godot starts only after the supervised worker is ready.
  > 7. Sending `hi` from the actual ControlHUD no longer returns `LISTENER_ABSENT`.
  > 8. The request receives a real response through the composed runtime.
  > 9. Closing the runtime cleans up the supervised processes correctly.
  >
  > Run the relevant existing suites afterward.
  >
  > Commit/audit Phase 1 separately so we have a receipt that real Godot composition is GREEN before touching diagnostics.
  >
  > Phase 2: improve `LISTENER_ABSENT`.
  >
  > Once Phase 1 is proven, implement structured failure propagation for the absent-listener case.
  >
  > The diagnostic should carry machine-readable fields equivalent to:
  > `code`, `agent_id`, `mailbox_path`, `presence_state`, and an actionable recovery description/launcher identity.
  >
  > The recovery information must come from the runtime/configuration that owns the worker relationship. Do not teach GDScript how to launch Hermes and do not hard-code a guessed shell command into the HUD.
  >
  > `EngAInBridge3D.gd` should render that structured diagnostic into useful operator text while preserving a sane fallback for unexpected/unstructured adapter failures.
  >
  > Then deliberately reproduce `LISTENER_ABSENT` by running Godot bare or otherwise withholding the worker and prove that the HUD now explains what component is absent and how this project is supposed to be launched.
  >
  > Run tests again and record the Phase 2 receipt separately.
  >
  > Do not begin TODO items 1, 2, 3, or 5 during either phase.

  The key is **both, but not simultaneously**.

  If the wrapper brings the worker up and `hi` works, we have proved that TODO item 4 was genuinely the problem. Then the better error becomes hardening rather than something that could accidentally conceal a still-broken runtime.

  One other thing I would have Claude do in Phase 1: make the new composed launcher the clearly documented normal way to start this 3D avatar. Otherwise three days from now you launch `godot --path ...` out of habit and get the same perfectly valid `LISTENER_ABSENT` again.

  Searched for 1 pattern, ran 6 shell commands

● Write(/mnt/data-drive/godot_engain_3d_avatar/launch_dragon3d.sh)
Wrote 50 lines to ../godot_engain_3d_avatar/launch_dragon3d.sh
#!/usr/bin/env bash
# launch_dragon3d.sh — the canonical way to start the dragon_3d avatar.
#
# This is the ONLY supported entrypoint for running the real Godot 3D
# avatar. Launching `godot --path ...` directly skips runtime_composition.py
# entirely, which means the presence authority and the Hermes mailbox
# worker never start — every request will fail with
# `LISTENER_ABSENT: no live mailbox worker` even though Godot itself looks
# fine. See full-audit repo `08-17-2026-*` for the diagnosis. Use this
# script instead, every time.
… +40 lines

  Read 3 files, listed 3 directories, ran 12 shell commands

Now writing the Phase 1 receipt document.

● Write(full audit/08-17-2026-dragon3d-launch-wrapper-phase1-proof.md)
Wrote 178 lines to full audit/08-17-2026-dragon3d-launch-wrapper-phase1-proof.md
# dragon_3d Launch Wrapper — Continuation-TODO Item 4, Phase 1

Written 2026-08-17, same day as the continuation TODO
(`08-17-2026-continuation-todo.md`) this resolves item 4 for. Triggered by
a real, reproduced live failure — not a hypothetical: Godot was running
(bare `godot --path /mnt/data-drive/godot_engain_3d_avatar`, launched
directly from a shell) and a chat submission returned
`LISTENER_ABSENT: no live mailbox worker`.

This document covers **Phase 1 only** — the launch-path fix and its live
… +168 lines

Now committing Phase 1 in both repos separately, per instruction.

  Committed 6f86cc4, 608879d, searched for 1 pattern, read 2 files, ran 3 shell commands
PostToolUse:Bash says: Tip: Run /ultrareview before you push to catch bugs with a cloud-based multi-agent review — 3 free reviews left.

Now implementing the structured error class:

● Update(/mnt/data-drive/godot_engain_3d_avatar/hermes_session_adapter.py)
Added 19 lines
    """Raised when the Hermes subprocess exceeds its configured timeout."""


class ListenerAbsentError(HermesAdapterError):
    """publish_request()'s LISTENER_ABSENT, carrying a structured diagnostic
    alongside the unchanged str(exc) message every existing caller/test
    already matches against. Callers that only know HermesAdapterError see
    nothing different; callers that want the structured fields (the CLI's
    --publish-request handler, ultimately the Godot HUD) read .diagnostic
    instead of re-parsing the message string.

    The diagnostic's launcher/recovery_action fields point at
    launch_dragon3d.sh — the one process that actually owns starting this
    worker (see runtime_composition.py) — computed here, in the runtime
    that owns that relationship, specifically so nothing downstream (least
    of all GDScript) has to know or guess how this project is launched."""

    def __init__(self, diagnostic: dict[str, str]) -> None:
        super().__init__("LISTENER_ABSENT: no live mailbox worker")
        self.diagnostic = diagnostic


class PerceptionValidationError(ValueError):
    """Fail-closed perception rejection with a stable evidence code."""


● Update(/mnt/data-drive/godot_engain_3d_avatar/hermes_session_adapter.py)
Added 1 line, removed 1 line
        payload = _strict_json_loads(temporary_path.read_text(encoding="utf-8"))
        self._validate_request(payload, validation_time=current)
        if not self._listener_is_live(now=current):
            raise HermesAdapterError("LISTENER_ABSENT: no live mailbox worker")
            raise ListenerAbsentError(self._listener_absent_diagnostic())
        try:
            os.link(temporary_path, request_path, follow_symlinks=False)
        except FileExistsError as exc:

Now add the _listener_absent_diagnostic helper method near mark_listener_ready/_listener_is_live:

● Update(/mnt/data-drive/godot_engain_3d_avatar/hermes_session_adapter.py)
Added 11 lines
            json.dumps(payload, separators=(",", ":")) + "\n",
        )

    def _listener_absent_diagnostic(self) -> dict[str, str]:
        launcher = str(self.config.project_dir / "launch_dragon3d.sh")
        return {
            "code": "LISTENER_ABSENT",
            "agent_id": CALLER_ID,
            "mailbox_path": str(self.config.listener_file.parent),
            "presence_state": "ABSENT",
            "launcher": launcher,
            "recovery_action": f"Start the dragon_3d runtime: {launcher}",
        }

    def _listener_is_live(self, *, now: float) -> bool:
        try:
            payload = _strict_json_loads(self.config.listener_file.read_text(encoding="utf-8"))

Now update the --publish-request CLI handler to emit the structured marker line before the existing fallback message:

  Searched for 1 pattern, read 1 file

● Update(/mnt/data-drive/godot_engain_3d_avatar/hermes_session_adapter.py)
Added 13 lines
            HermesSessionAdapter(AdapterConfig(project_dir=MAILBOX_PROJECT_ROOT)).publish_request(
                Path(effective_argv[1])
            )
        except ListenerAbsentError as exc:
            # One extra, structured line ahead of the existing plain-text
            # one, so callers that only ever read the plain-text line (any
            # existing test/tooling) see no change, and callers that parse
            # for this specific marker (EngAInBridge3D.gd) can render an
            # actionable diagnostic instead of a bare error string.
            print(
                f"ENGAIN_LISTENER_ABSENT_DIAGNOSTIC={json.dumps(exc.diagnostic, separators=(',', ':'))}",
                file=sys.stderr,
                flush=True,
            )
            print(f"request publication rejected: {exc}", file=sys.stderr, flush=True)
            return 1
        except (OSError, UnicodeDecodeError, ValueError, HermesAdapterError) as exc:
            print(f"request publication rejected: {exc}", file=sys.stderr, flush=True)
            return 1

  Searched for 1 pattern, read 1 file, ran 1 shell command

● Update(/mnt/data-drive/godot_engain_3d_avatar/scripts/EngAInBridge3D.gd)
Added 7 lines
const MAILBOX_BUSY := "MAILBOX_BUSY"
const MAILBOX_STALE := "MAILBOX_STALE"
const LISTENER_ABSENT := "LISTENER_ABSENT"
# hermes_session_adapter.py's --publish-request handler prints this marker,
# followed by a JSON diagnostic, on ListenerAbsentError specifically. This
# HUD only ever reads that marker and renders whatever fields it contains —
# it never decides on its own how the worker should be started; the
# adapter (which lives beside launch_dragon3d.sh and actually owns that
# relationship) is the one computing the recovery/launcher fields.
const LISTENER_ABSENT_DIAGNOSTIC_MARKER := "ENGAIN_LISTENER_ABSENT_DIAGNOSTIC="
const REQUEST_SCHEMA: Array[String] = [
  "call_id",
  "expires_at",

Now update the failure site in submit() and add the rendering helper:

● Update(/mnt/data-drive/godot_engain_3d_avatar/scripts/EngAInBridge3D.gd)
Added 1 line, removed 1 line
  var publication := _execute_adapter(PackedStringArray(["--publish-request", temporary_path]))
  if publication["code"] != 0 or not publication["output"].contains("ENGAIN_REQUEST_PUBLISHED=1"):
    _end_active_lifecycle()
    _emit_err("Request publication failed: " + publication["output"])
    _emit_err(_render_publication_failure(publication["output"]))
    return

  _active_request_id = request_id

  Searched for 1 pattern, read 1 file

● Update(/mnt/data-drive/godot_engain_3d_avatar/scripts/EngAInBridge3D.gd)
Added 21 lines
  return {"code": code, "output": combined.strip_edges()}


func _render_publication_failure(output: String) -> String:
  # The adapter's diagnostic line, if present, always sits alongside its
  # existing plain-text "request publication rejected: ..." line in the
  # same captured output — look for it, but fall back to the raw output
  # verbatim (unchanged from before this diagnostic existed) for any
  # failure this HUD doesn't specifically know how to explain.
  for line in output.split("\n"):
    if not line.begins_with(LISTENER_ABSENT_DIAGNOSTIC_MARKER):
      continue
    var payload := line.substr(LISTENER_ABSENT_DIAGNOSTIC_MARKER.length())
    var parsed = JSON.parse_string(payload)
    if parsed is Dictionary and parsed.has("code") and parsed.has("recovery_action"):
      return (
        "[%s] no live mailbox worker for '%s'.\n" % [parsed.get("code"), parsed.get("agent_id", "?")]
        + "Mailbox: %s\n" % parsed.get("mailbox_path", "?")
        + "Presence lease: %s\n" % parsed.get("presence_state", "?")
        + "To fix: %s" % parsed.get("recovery_action", "?")
      )
  return "Request publication failed: " + output


func _set_lifecycle_status(status: String) -> void:
  if status not in [STATUS_IDLE, STATUS_LOOKING_INTERNAL, STATUS_THINKING]:
    return

  Searched for 1 pattern, read 1 file, ran 2 shell commands

Now let me match this exact convention in my helper:

● Update(/mnt/data-drive/godot_engain_3d_avatar/scripts/EngAInBridge3D.gd)
Added 5 lines, removed 2 lines
    if not line.begins_with(LISTENER_ABSENT_DIAGNOSTIC_MARKER):
      continue
    var payload := line.substr(LISTENER_ABSENT_DIAGNOSTIC_MARKER.length())
    var parsed = JSON.parse_string(payload)
    if parsed is Dictionary and parsed.has("code") and parsed.has("recovery_action"):
    var parser := JSON.new()
    if parser.parse(payload) != OK:
      continue
    var parsed: Variant = parser.data
    if typeof(parsed) == TYPE_DICTIONARY and parsed.has("code") and parsed.has("recovery_action"):
      return (
        "[%s] no live mailbox worker for '%s'.\n" % [parsed.get("code"), parsed.get("agent_id", "?")]
        + "Mailbox: %s\n" % parsed.get("mailbox_path", "?")

  Ran 1 shell command

Back to exactly the 3 pre-existing baseline failures, 260 passed. Now let's reproduce LISTENER_ABSENT live (bare Godot, withholding the worker) to prove the HUD renders the new structured diagnostic.

  Ran 2 shell commands

Window found and process alive this time. Let's submit "hi" and capture the HUD's rendering of the new diagnostic.

  Read 1 file, ran 2 shell commands

● Write(full audit/08-17-2026-listener-absent-structured-diagnostic-phase2-proof.md)
Wrote 120 lines to full audit/08-17-2026-listener-absent-structured-diagnostic-phase2-proof.md
# Structured `LISTENER_ABSENT` Diagnostics — Continuation-TODO Item 4, Phase 2

Written 2026-08-17, immediately after Phase 1
(`08-17-2026-dragon3d-launch-wrapper-phase1-proof.md`) was confirmed
GREEN. Phase 1 proved the launch-path gap was the real and only cause of
`LISTENER_ABSENT`; this phase turns that error from a bare, unstructured
string into an operator-actionable diagnostic, without concealing or
substituting for Phase 1's fix. TODO items 1, 2, 3, and 5 were not
touched.
… +110 lines

Now committing Phase 2 in both repos:

  Committed 90fc568, 4c85f54, ran 2 shell commands

Both phases done, no stray processes, both repos clean. Summary:

Phase 1 — the actual bug (commit 6f86cc4 in godot_engain_3d_avatar, receipt 608879d in the audit repo): the running Godot instance had been launched as bare godot --path ..., never through runtime_composition.py, so the presence authority and the Hermes mailbox worker never started — the mailbox directory was completely empty. No defect existed in runtime_composition.py/runtime_launcher.py/the presence authority/the adapter; the fix was a new canonical entrypoint, launch_dragon3d.sh. Proved live, all 9 points: composition running → authority healthy → listener.json appears → correct PID → expires_at advancing across 4 reads → Godot gated on worker readiness → real hi from the actual ControlHUD with no LISTENER_ABSENT → real Hermes response ("Hi—I'm here with you.") rendered in the HUD → clean SIGTERM teardown, no orphans. Offline suite: 260/263, same 3 pre-existing unrelated failures.

Phase 2 — the diagnostic (commit 90fc568, receipt 4c85f54), started only after Phase 1 was confirmed green: publish_request() now raises ListenerAbsentError carrying a structured diagnostic (code/agent_id/mailbox_path/presence_state/launcher/recovery_action) computed by the adapter itself, pointing at launch_dragon3d.sh. EngAInBridge3D.gd renders it into operator text with a fallback to the original raw string for anything unstructured — no shell command hard-coded into GDScript. Reproduced the original failure deliberately (bare Godot again) and confirmed the HUD now shows exactly:
[LISTENER_ABSENT] no live mailbox worker for 'dragon3d'.
Mailbox: /mnt/data-drive/engain-runtime-mailboxes/dragon3d
Presence lease: ABSENT
To fix: Start the dragon_3d runtime: /mnt/data-drive/godot_engain_3d_avatar/launch_dragon3d.sh
One regression caught in dev (an initial JSON.parse_string draft broke this repo's own strict-JSON test convention) and fixed before commit. Suite back to 260/263 baseline.

All 4 commits are local, not pushed. TODO items 1, 2, 3, 5 untouched, as instructed.

✻ Sautéed for 11m 58s

※ recap: We fixed the 3D avatar's missing-worker bug: added a real launch script and a clear on-screen error if it happens again, both proven live and committed locally. Next: decide whether to push these commits, or move to TODO item 1 (the dispatch mutex). (disable recaps in /config)

❯ Push now, then move to item 1.

  This is the cleanest boundary you’re going to get: the original live failure has been diagnosed, fixed, proven through the real HUD, hardened with an actionable diagnostic, committed in two independent phases, and both repos are clean. I would not stack the dispatch-mutex contract work on top of four local-only commits.

  Give Claude this:

  > Push the completed TODO-item-4 work before starting anything else.
  >
  > Do not modify code.
  >
  > For each repo containing the four new commits:
  >
  > 1. Confirm `git status --short` is clean.
  > 2. Confirm the current branch.
  > 3. Confirm the configured remote/upstream is the intended repository.
  > 4. Confirm the expected commits are at HEAD/in the local history:
  >
  >    * `6f86cc4` — Phase 1 implementation
  >    * `608879d` — Phase 1 audit receipt
  >    * `90fc568` — Phase 2 implementation
  >    * `4c85f54` — Phase 2 audit receipt
  > 5. Push normally to the existing upstream. Do not force-push, rewrite history, squash, amend, or rebase these receipts.
  > 6. Verify the remote contains the pushed commits.
  > 7. Verify both repos remain clean afterward.
  >
  > Then update the continuation TODO/audit state to mark item 4 complete, if that status has not already been recorded.
  >
  > Do not begin TODO item 1 until the push is confirmed.

  After that, item 1 becomes the next actual engineering decision.

  And I would keep Claude at the **design/re-derivation stage** initially. We don't yet want “implement a mutex.” We want him to establish exactly what has to be mutually exclusive, because that determines whether extending `SessionClaimRegistry` is conceptually correct or whether dispatch serialization deserves its own primitive.

  Also: that recap Claude generated is accurate. The two-phase separation paid off. If anything breaks later, you now have a precise boundary between “make the real runtime exist” and “make failure understandable.”

  Pushed to main, listed 1 directory, ran 2 shell commands

● Write(full audit/08-17-2026-continuation-todo-status-update.md)
Wrote 52 lines to full audit/08-17-2026-continuation-todo-status-update.md
# Continuation TODO Status Update — Item 4 Complete

Written 2026-08-17, after both phases of item 4 were pushed. This is a
status update against `08-17-2026-continuation-todo.md`, not a rewrite of
it — that file stays as the original record of what was open and why;
this note records what changed since.

## Item 4 — closed

> "Real Godot launch through this same integration ... hasn't been
… +42 lines

  Committed 55b37fe, pushed to main

Push confirmed and item 4 marked closed. Summary of the push verification:

Repo: godot_engain_3d_avatar
Clean before push: ✅ clean
Branch: main
Remote: origin → SmokesBowls/godot_3d_avatar
Commits confirmed at HEAD: 6f86cc4, 90fc568
Push: 57122cd..90fc568 fast-forward
Remote verified: ✅ origin/main shows both
────────────────────────────────────────
Repo: engain-avatar-audit
Clean before push: ⚠️ pre-existing unrelated dirt (claude hermes 3d.md modified, claude hermes 3d2.md untracked — present
before this session, not part of these commits)
Branch: main
Remote: origin → SmokesBowls/hermes-audit
Commits confirmed at HEAD: 608879d, 4c85f54
Push: 2429840..4c85f54 fast-forward
Remote verified: ✅ origin/main shows both

Both repos were 0 behind origin before pushing — plain fast-forwards, no force/rebase/amend/squash. Post-push, godot_engain_3d_avatar is fully clean; engain-avatar-audit still carries that same pre-existing unrelated dirtiness (flagging it rather than touching it, since it's outside this task's scope).

Added and pushed one more small commit, 55b37fe, recording item 4 as closed against the original continuation TODO (new dated file, TODO left unedited — consistent with the "amend via new document" discipline) and confirming both push ranges.

---
Item 1 is next — design stage only, no implementation. Before I start: I'll re-derive from first principles exactly what has to be mutually exclusive for an overridden /dispatch binding, rather than assuming the extend-SessionClaimRegistry framing from the original TODO note is already the right shape. That means going back to presence_authority_server.py's /dispatch handler and SessionClaimRegistry itself to establish: what race is actually possible today, what a claim would need to key on, and whether that's a natural extension of the existing claim primitive or a genuinely separate contract. I'll report that analysis before proposing (let alone writing) anything.

✻ Churned for 3m 11s

※ recap: We're hardening the EngAIn avatar continuity system; just pushed the fix proving the dragon_3d runtime actually starts and reports errors clearly. Next: analyze what needs mutual exclusion before designing the dispatch concurrency mutex (TODO item 1).

❯ Good. Item 4 is actually closed now, including the remote receipts. The audit repo dirt is worth leaving alone exactly as Claude did; it predates this work and should not get accidentally swept into an unrelated commit.

  For item 1, that proposed approach is the right one: re-derive the race before choosing the primitive. I would have Claude answer these specific questions before proposing any code.

  First, identify the exact concurrent operation. Draw two simultaneous `/dispatch` calls using an overridden binding and show the sequence each performs: binding resolution, ledger/cursor read, recap/context construction if any, provider invocation, provider response, ledger append/receipt update. We need to know exactly where interleaving becomes unsafe.

  Second, identify the protected resource. Don’t assume it is an EngAIn `session_id`, body, mailbox, or provider session. Demonstrate which shared mutable thing becomes corrupted or semantically ambiguous when two dispatches overlap.

  Third, establish the lock key from that proof. If two EngAIn bodies point at the same native Hermes conversation, then `(provider_id, provider_session_id)` is a strong candidate. But Claude should prove cases such as:

  ```text
  dragon_2d -> provider A / session 123
  dragon_3d -> provider A / session 123
  ```

  versus:

  ```text
  dragon_2d -> provider A / session 123
  tool      -> provider A / session 456
  ```

  and:

  ```text
  dragon_2d -> provider A / session 123
  dragon_3d -> provider B / session 123
  ```

  Those three cases should make the intended concurrency semantics obvious.

  Fourth, determine the critical-section lifetime. This matters a lot. Is the resource held only during the provider call? Or must it span something like:

  ```text
  read current continuity state
          ↓
  construct dispatch/context
          ↓
  invoke provider
          ↓
  receive provider response
          ↓
  append/update continuity receipt
  ```

  If the lock starts too late or ends too early, you can still get two callers constructing state from the same previous turn.

  Fifth, compare that behavior with `SessionClaimRegistry`. A registry whose meaning is “worker/session ownership” is not automatically the right abstraction for “temporary serialization of dispatch calls.” If extending it causes concepts like ownership leases, readiness, and mutex acquisition to become mixed together, make a separate `DispatchClaimRegistry`/mutex primitive instead. Reusing code is less important than keeping the contract legible.

  Sixth, prove failure semantics before implementation: what happens to caller B while caller A owns the session? Does it wait, receive `DISPATCH_BUSY`, queue, or time out? What releases the claim if the provider hangs or the request crashes? Can a stale claim survive? Is acquisition fair? Can the same execution accidentally try to reacquire its own claim?

  And one architectural question I especially want answered: is `presence_authority_server.py` guaranteed to be the single process through which all of these `/dispatch` calls flow? If yes, an in-process keyed synchronization primitive may be enough. If multiple authority processes can legitimately dispatch to the same provider session, an ordinary Python mutex would provide false safety because each process would own a different lock.

  So I’d give Claude one added instruction:

  > Include at least one concrete two-caller race trace showing the current bug, then show the same trace with the proposed serialization boundary. Do not recommend a primitive until the trace demonstrates exactly what it must protect. Also establish whether the solution must coordinate only threads within one presence-authority process or multiple OS processes.

  If Claude comes back saying “extend `SessionClaimRegistry`,” we should be able to point at that analysis and see why. If he comes back saying “separate dispatch mutex,” same standard.

  That’s the design decision worth making before another line of implementation.

  Searched for 3 patterns, read 7 files, ran 1 shell command

Traced this through the actual code (presence_authority_server.py, shared_session_bridge.py, session_ledger.py, continuity_cursor_tracker.py, presence_registry.py, session_claim_registry.py, and both avatar repos' hermes_session_adapter.py) rather than reasoning from the TODO note's prose alone. Answers below, in the order asked.

1. The exact concurrent operation

/dispatch → SharedSessionBridge.handle_turn()'s 8 steps, run inline in the ThreadingHTTPServer request thread with zero locking of its own anywhere in _handle_dispatch — I checked; there is no claims.claim()/claims.release() call in that method at all today:

  Searched for 1 pattern

Confirmed: those two calls are only reachable via the standalone /claim//release HTTP endpoints (what hermes_session_adapter.py's client-side _acquire_dispatch_claim() uses). _handle_dispatch itself never touches claims at all.

Two simultaneous /dispatch calls both targeting the same (provider_id, provider_session_id), in a ThreadingHTTPServer thread each:

Thread A (/dispatch)                    Thread B (/dispatch)
──────────────────────                  ──────────────────────
presence.register(shared_session_id)    presence.register(shared_session_id)
handle_turn():
  step2 ledger.append(request)  ←────── step2 ledger.append(request)   [RACE: see §2]
  step3 presence.resolve()               step3 presence.resolve()
  step4 read Ledger context              step4 read Ledger context
  step5 binding = from_presence_record() step5 binding = from_presence_record()  [same target]
        cursor.last_seen_turn_id(P,S)          cursor.last_seen_turn_id(P,S)     [both read stale, pre-either-write]
        dispatch(binding, ctx, input)  ←──────  dispatch(binding, ctx, input)    [BOTH invoke the provider CLI on session S concurrently]
  step6 presence.resolve() (re-check)    step6 presence.resolve()
  step7 ledger.append(response) ←──────── step7 ledger.append(response)  [RACE: see §2]
  step8 cursor.advance(P,S,turn_id)       step8 cursor.advance(P,S,turn_id)  [monotonic-max wins, order not preserved]

Nothing serializes any of this today, for any caller — not just overridden ones. The existing worker-level claim in hermes_session_adapter.py (_acquire_dispatch_claim(), keyed on self.client.session_id) is a client-side convention that only dragon_2d/dragon_3d's own adapter code participates in, and it happens to work between those two specifically only because both repos hardcode the identical frozen string PERSISTED_HERMES_B_SESSION_ID = "20260731_065008_63a62d" — confirmed byte-identical in both files. Any other caller reaching /dispatch directly — the integration proof's Claude-Code leg, a future third body, a bare curl, the tool/origin_body case you named — gets no exclusion whatsoever, override or not. That's a sharper (and more alarming) statement of the gap than the original TODO note made: it isn't "overrides lack a guard," it's "/dispatch has no guard, period; two of its many possible callers are accidentally, incidentally protected against each other only, for a reason unrelated to what they're dispatching to."

2. The protected resource — it's actually two, not one

Resource A — the native provider transcript, (provider_id, provider_session_id). This is session_claim_registry.py's own stated reason for existing: concurrent hermes chat --resume <session_id> (or the Claude Code equivalent) can "interleave or corrupt one live transcript." EngAIn has no visibility into that corruption after the fact — it's external, unrecoverable, and the only real defense is prevention. This is what TODO item 1 was actually written about.

Resource B — SessionLedger's own turn ordering, keyed on EngAIn's shared_session_id, and it's a genuine, pre-existing bug I found independently while tracing this, not hypothetical:

turns = self._turns.setdefault(session_id, [])
turn = Turn(turn_id=len(turns), ...)   # ← read
turns.append(turn)                      # ← write, not atomic with the read above

Two threads racing append() for the same shared_session_id can both read the same len(turns), mint two turns claiming the same turn_id, and leave the stored list's actual index out of sync with the turn's own turn_id field — which read_since()/context-building/the cursor all trust. This is keyed differently (shared_session_id, not (provider_id, provider_session_id)) and can happen even between two dispatches to two entirely different native provider sessions, as long as they share a shared_session_id — e.g. dragon_2d overriding to provider B while dragon_3d dispatches under default provider A, both against the same shared session. A (provider_id, provider_session_id) mutex does not protect this at all; it's an orthogonal problem with an orthogonal key. I'm flagging it, not folding it into item 1 or fixing it now — it needs its own decision, and I'd rather name it honestly than silently leave it implied-solved by the mutex work.

3. The lock key — proven from your three cases

Walking each:

dragon_2d -> provider A / session 123
dragon_3d -> provider A / session 123        → SAME native transcript. Must serialize.

dragon_2d -> provider A / session 123
tool      -> provider A / session 456        → DIFFERENT sessions under the same provider. Must NOT serialize
                                                 against each other — provider_id alone is too coarse a key
                                                 and would create false contention.

dragon_2d -> provider A / session 123
dragon_3d -> provider B / session 123         → session_id "123" collides as a bare string, but they are
                                                 unrelated native memory containers under different providers.
                                                 Must NOT serialize — session_id alone is also too coarse,
                                                 and using it bare would create a false conflict between two
                                                 totally unrelated resources that happen to share a number.

Only the composite (provider_id, provider_session_id) gets all three right. This is also, not coincidentally, the exact identity ContinuityCursorTracker already uses for the same underlying reason (its own docstring: "the exact native memory container... not what label is currently attached to it"). Two independent parts of this system converging on the same composite key from different angles (recap correctness vs. mutual exclusion) is a strong signal it's the right identity, not an arbitrary choice.

4. Critical-section lifetime — must start before the cursor read, not just around the provider call

Locking only around self._dispatch(...) (step 5's actual call) is insufficient. In the race trace above, both threads read cursor.last_seen_turn_id(P, S) — and build their recap from it — before either has dispatched or advanced anything. If the lock only wrapped the provider call itself, thread B would still block waiting for the lock, but it would already be holding a recap built from stale cursor state, and it would send that stale recap the instant the lock opens — exactly your "constructs state from the same previous turn" scenario. The claim has to be held from before step 4/5 (the Ledger-context read and the cursor read) through step 8 (cursor advance), i.e., effectively the entire handle_turn() call. Simplest correct placement: acquire immediately at the top of _handle_dispatch, before presence.register() even runs, release in a finally after handle_turn() returns or raises.

5. SessionClaimRegistry vs. a separate primitive

Extend it — but narrowly, and I want to be precise about what "extend" means here so it doesn't quietly become the ownership/readiness conflation you're rightly worried about:

- Its own docstring already states, verbatim, the exact contract item 1 needs: "who, right now, holds the right to actually send the next message to this session's provider — a short-lived mutex held only for the duration of one dispatch call." That's not a coincidental resemblance; it's the same problem.
- The only actual mismatch is the key's shape (str today, needs (provider_id, provider_session_id)). The implementation (Dict[key, SessionClaim] behind one threading.Lock) doesn't care what the key means — it only needs hashability. This is a type generalization, not a semantic change.
- Critically: I am not proposing to touch the public /claim//release HTTP endpoints or their JSON contract at all — those stay exactly session_id: str, exactly as today's worker-level default-path claim already uses them, unmodified. The new behavior is _handle_dispatch calling the same in-process Python object (claims, already a module-level singleton in presence_authority_server.py) directly with a composite key — never a new HTTP surface, never a change to what existing callers already depend on.
- A separate DispatchClaimRegistry would be the same lock+dict+lease-expiry code, duplicated, with no actual semantic daylight between the two classes — two things to learn and keep mentally reconciled instead of one, for no protective benefit. That's the "reuse for its own sake" trap in the abstract, but here the abstraction genuinely already matches; the caution about PresenceRegistry (ownership/readiness/liveness leases) doesn't transfer, because SessionClaimRegistry was already deliberately split off from PresenceRegistry for exactly this reason (its docstring draws that line explicitly) — extending it doesn't re-merge anything.

One real asymmetry worth naming, not fixing now: once _handle_dispatch claims (provider_id, provider_session_id) server-side, the default (non-override) path ends up double-locked — the worker's existing client-side claim on the frozen string, and the new server-side claim on the tuple — both real, both harmless, redundant rather than conflicting. Retiring the client-side one is production-cutover-decision territory (item 3), not this.

6. Failure semantics

- Caller B while A holds it: reject immediately (409, new DISPATCH_BUSY, shaped like the existing ClaimRejected/SESSION_OCCUPIED), not queue or wait. This matches the only existing precedent in this codebase (SESSION_OCCUPIED, which avatar workers already handle gracefully — "Another EngAIn body is currently speaking... please try again shortly"). Queueing inside an HTTP handler thread is a materially bigger design commitment (queue depth, thread-pool exhaustion under contention, its own timeout policy) with zero precedent here; I'd want that raised as its own decision if it's ever wanted, not folded in.
- Provider hangs / request crashes: reuse the existing lease_seconds/claim_expires_at self-expiry unchanged — SessionClaimRegistry already has this, independent of whether release() ever runs. Size it off the actual dispatcher's own timeout (the existing worker-level call already does this: MAX_HERMES_TIMEOUT_SECONDS + 20.0) rather than inventing a new number.
- Stale claim survival: bounded by that same lease, same as today — no new exposure.
- Fairness: none, today or after — claim() is immediate accept/reject with no queue, so "fairness" doesn't really apply; a starved caller just keeps independently re-racing. Pre-existing limitation, not introduced by this work — worth stating plainly rather than silently inheriting.
- Self-reacquisition: this is a real trap I want to flag concretely. claim()'s reentrancy rule is "same instance_id re-claiming while its own unexpired claim is held → succeeds as a refresh, doesn't reject." Both dispatch calls in my trace above independently compute instance_id = f"{provider_id}-dispatch" when the caller doesn't supply one — meaning two genuinely different, concurrent /dispatch calls could collide on the same derived instance_id and silently "refresh" each other's claim instead of correctly contending for it, defeating the whole mechanism. The new internal claim must use an instance_id freshly minted per /dispatch call (e.g. a UUID scoped to that one request), never the caller-supplied agent_id/instance_id body field, specifically so two overlapping requests — even from the same declared caller identity, e.g. a client retry landing while the first attempt is still in flight — properly contend rather than quietly co-owning the lock.

Architecture question: single process, or must this coordinate across processes?

Single process, by explicit design, today: presence_authority_server.py's own module docstring states the whole reason it exists is "exactly one PresenceRegistry and exactly one SessionClaimRegistry in the whole system" reachable over HTTP, precisely so no worker holds a private instance. It's a ThreadingHTTPServer — one OS process, one Python interpreter, one GIL, threads only. My Phase 1 launcher work confirmed this further: SupervisedPresenceAuthority only ever spawns exactly one authority process per composed runtime generation; nothing in this codebase anticipates or supports multiple authority processes/replicas. So an in-process threading.Lock-backed registry (exactly what SessionClaimRegistry already is) is sufficient and correct as long as that one-process invariant holds — which it currently isn't even enforced anywhere, only assumed. I'd treat "there must be exactly one presence-authority process system-wide" as a documented precondition of this whole fix (comment in the class, maybe a note in the launcher), not a silent assumption — because you named the exact right failure mode: if that invariant is ever violated (someone runs a second authority on another port, or this gets horizontally scaled for availability later), an in-process mutex becomes false safety instantly, and nothing today would detect or prevent that from happening.

---
Where this leaves item 1, as a recommendation for review, not yet implemented: extend SessionClaimRegistry to accept a (provider_id, provider_session_id) key for _handle_dispatch's own new, internal, direct-object call (public /claim//release HTTP contract untouched); acquire before handle_turn() runs, release in a finally after; reject contending callers immediately with a new DISPATCH_BUSY-style error; use a per-request-minted instance_id, never caller-supplied; and separately record (not fix) the SessionLedger turn_id race as a related-but-distinct finding.

Want me to write this up as a dated design-note in the audit repo (no code) before we decide whether to proceed to implementation, same as the rest of this session's discipline?

✻ Brewed for 6m 0s

❯ Yes. Write the design note now, and do not implement yet.

  The analysis is solid and it uncovered something more important than the original TODO wording suggested: `/dispatch` itself has no server-side serialization. The two avatar workers were only incidentally protected because they happened to participate in the old client-side claim convention and shared the same frozen Hermes session ID. Direct callers and future bodies could bypass that entirely.

  I agree with the proposed composite key `(provider_id, provider_session_id)`. The three comparison cases demonstrate why neither provider ID nor session ID alone is sufficient.  I also agree that the protection has to span continuity-state construction through cursor advancement; locking only the provider invocation still allows a second request to build context from stale cursor state.

  And the argument for extending `SessionClaimRegistry` is persuasive. Its existing contract is already a short-lived dispatch mutex, rather than presence/readiness ownership, so this is genuinely the same abstraction with a more accurate key—not a forced reuse.

  Before implementation, though, I want the design note to close two remaining holes.

  First: **show exactly how `_handle_dispatch` obtains `(provider_id, provider_session_id)` before `handle_turn()` begins.** Claude recommends acquiring before `presence.register()` and before the context/cursor work, which is correct, but the trace also says binding resolution currently occurs inside `handle_turn()` at step 5.  So the design needs to identify the authoritative, side-effect-free source for the lock key before acquisition. If that requires extracting binding resolution from `handle_turn()`, say that explicitly before changing architecture.

  Second: **make the lease-duration invariant precise.** A timed claim is only safe if it cannot expire while a legitimate dispatch is still inside the critical section. The proposed reuse of the existing dispatch timeout plus margin is reasonable, but the note should state the invariant explicitly: claim TTL must exceed the maximum possible protected operation duration, or renewal must occur while dispatch is active. Otherwise a long-running A could still be executing when its claim expires and B acquires the same provider transcript. The current proposal already recognizes the existing lease/self-expiry mechanism; this just needs to be nailed down before code.

  The SessionLedger race should also become a new named TODO immediately. It is not item 1, and Claude is right not to quietly bundle it into this implementation. But duplicate `turn_id`s are a real correctness bug, not a theoretical cleanup item. Two dispatches sharing an EngAIn session but targeting different provider sessions can bypass the provider-session mutex and race `len(turns)`/`append()`.  I would put that new item directly after the dispatch mutex work, before restart persistence, because persistence of a ledger whose in-memory ordering can already become invalid would be backwards.

  So tell Claude:

  > Write the dated item-1 design note in the audit repo now. No implementation yet.
  >
  > Preserve the race trace, composite-key proof, full critical-section boundary, per-request unique claim identity, `DISPATCH_BUSY` semantics, and single-authority-process invariant.
  >
  > Add two explicit design answers before recommending implementation:
  >
  > 1. Show exactly where `_handle_dispatch` gets the authoritative `(provider_id, provider_session_id)` lock key before `handle_turn()` and before any continuity state is read or mutated. If current binding resolution occurs too late, identify the minimal refactor needed; do not conceal that behind the proposed mutex.
  > 2. State and prove the claim-lifetime invariant: an active legitimate dispatch must never outlive its exclusivity claim. Define how the TTL is derived from the actual bounded dispatch timeout plus sufficient surrounding-operation margin, or specify renewal if that cannot be guaranteed.
  >
  > Also record the newly discovered `SessionLedger.append()` same-session `turn_id` race as a separate new continuation TODO. Do not fix it as part of item 1. Mark that it uses `shared_session_id` as its contention key and therefore is not solved by the provider-session mutex.
  >
  > Do not modify runtime code until the design note is committed and reviewed.

  One more thing Claude got exactly right: the per-request claim owner must be freshly minted. Reusing `agent_id` or a derived `"provider-dispatch"` identity would make two genuinely concurrent requests look like a reentrant refresh and destroy the mutex.

  Once those two missing answers are in the note, I think item 1 will be ready for implementation.

  Read 1 file, ran 3 shell commands

Confirmed both dispatcher timeouts. Now writing the design note.

● Write(full audit/08-18-2026-item1-dispatch-mutex-design-analysis.md)
Wrote 355 lines to full audit/08-18-2026-item1-dispatch-mutex-design-analysis.md
# Item 1 Design Analysis — Concurrent-`/dispatch` Mutex for the Native Provider Session

Written 2026-08-18. This is a **design note only** — no runtime code is
touched by this document. It re-derives continuation-TODO item 1 from the
actual code (`presence_authority_server.py`, `shared_session_bridge.py`,
`session_ledger.py`, `continuity_cursor_tracker.py`, `presence_registry.py`,
`session_claim_registry.py`, and both avatar repos' `hermes_session_adapter.py`)
rather than from the original TODO note's prose, per explicit instruction
not to recommend a primitive until a trace proves what it has to protect.
Do not implement any of this until it has been reviewed.
… +347 lines

Now the companion TODO amendment recording the new SessionLedger race item:

● Write(full audit/08-18-2026-continuation-todo-amendment-ledger-turn-id-race.md)
Wrote 64 lines to full audit/08-18-2026-continuation-todo-amendment-ledger-turn-id-race.md
# Continuation TODO Amendment — New Item: `SessionLedger.append()` `turn_id` Race

Written 2026-08-18, discovered while re-deriving item 1's design
(`08-18-2026-item1-dispatch-mutex-design-analysis.md`, §2, "Resource B").
Recorded here as its own item rather than folded into item 1, per
explicit instruction — it is a real, separate bug with a different
contention key, not solved by the dispatch mutex that document proposes.

## The bug
… +54 lines

Now committing both (audit repo only — no runtime code touched, per instruction):

  Committed fef2a00, ran 1 shell command

Committed (fef2a00), not pushed — same pre-existing unrelated dirt left untouched, no runtime code modified. Summary of both new documents:

08-18-2026-item1-dispatch-mutex-design-analysis.md — full re-derivation, preserving everything from our earlier discussion (race trace, two-resource split, composite-key proof from your three cases, critical-section-must-start-before-the-cursor-read, extend-not-separate reasoning, DISPATCH_BUSY semantics, fresh-per-request instance_id, single-authority-process precondition), plus the two holes closed:

- §8a — key source: no handle_turn() refactor needed. body["provider_id"]/body["provider_session_id"] are already required, validated, side-effect-free fields available at the very top of _handle_dispatch — and they're the same values already fed into presence.register()'s endpoint moments later, so the claim key and what gets registered can never diverge within one call. Named the one boundary case this doesn't cover (a different concurrent /dispatch for the same shared_session_id but a different provider overwriting Presence between register and resolve) as pre-existing, out of scope for item 1.
- §8b — TTL invariant: stated formally as lease_seconds = dispatch_timeout_s(provider_id) + margin_s, derived from the actual enforced timeouts I read directly out of hermes_provider_adapter.py/claude_code_provider_adapter.py (90s / 120s hard subprocess.run(timeout=...) ceilings — not the avatar-side constant, which is a different process's number), margin recommended 10–20s matching existing precedent. Proved renewal is unnecessary given that bound, named the exact condition that would force reconsidering it, and named the one residual assumption (subprocess timeout enforcement itself) rather than claiming it airtight.

08-18-2026-continuation-todo-amendment-ledger-turn-id-race.md — records the SessionLedger.append() race as a new item, inserted as item 2 (right after the dispatch mutex, before restart persistence, exactly as you specified), explicit about why the provider-session mutex doesn't cover it (different key: shared_session_id, not (provider_id, provider_session_id)).

No runtime code was modified. Ready for your review before implementation.

✻ Churned for 4m 17s

※ recap: We're hardening EngAIn's avatar continuity system; item 4 (Godot launch fix) shipped and pushed, and I just wrote the design note for item 1's dispatch mutex, not yet implemented. Next: you review that design note, then I implement it.

❯ Don’t implement yet. The design is almost there, but §8a exposes a race that directly breaks the mutex guarantee, so I would send it back for one more design pass.

  The problem is this sequence:

  ```text
  Dispatch A says: provider A / session 123
  Dispatch B says: provider B / session 456
  ```

  They acquire different mutex keys, so both are correctly allowed to proceed concurrently.

  But `handle_turn()` does not necessarily dispatch using the binding each request arrived with. The existing sequence registers the binding into shared mutable Presence and later resolves that Presence again before constructing the provider binding.

  So this can happen:

  ```text
  A acquires lock (A,123)
  B acquires lock (B,456)

  A presence.register(shared_session -> A,123)
  B presence.register(shared_session -> B,456)   # overwrites A

  A presence.resolve(shared_session) -> B,456
  B presence.resolve(shared_session) -> B,456

  A dispatches to B,456 while holding lock (A,123)
  B dispatches to B,456 while holding lock (B,456)
  ```

  Now two threads are concurrently operating on native transcript `(B,456)`, despite the new mutex.

  That means the statement:

  > “the claim key and what gets registered can never diverge within one call”

  is true only locally within each call. It does not establish the property we actually need:

  > **The key claimed by a dispatch must equal the provider-session resource that dispatch ultimately invokes.**

  Another thread can cause those to diverge after registration.

  This isn't merely an unrelated pre-existing Presence race anymore. Item 1 introduces a mutex whose correctness depends on that race not happening. So we cannot mark it out-of-scope while claiming the provider transcript is protected.

  I would send Claude this:

  > One design issue remains before implementation.
  >
  > Do not write runtime code yet.
  >
  > §8a identifies concurrent `/dispatch` calls for the same `shared_session_id` but different provider bindings as a pre-existing boundary case. Re-evaluate that classification because it appears to invalidate item 1's mutex guarantee.
  >
  > Current shape:
  >
  > ```
  > request A: shared S -> provider A/session 123
  > request B: shared S -> provider B/session 456
  > ```
  >
  > A and B legitimately acquire different provider-session claims and therefore execute concurrently.
  >
  > But each call writes its requested binding through `presence.register(S, ...)`, and `handle_turn()` later obtains its actual dispatch binding through `presence.resolve(S)`.
  >
  > Show the interleaving where B overwrites S's Presence record between A's register and resolve.
  >
  > Determine whether A can consequently dispatch to `(B,456)` while still holding the claim for `(A,123)`. If yes, then B can simultaneously dispatch to `(B,456)` while holding the correct `(B,456)` claim, defeating the mutex.
  >
  > The invariant item 1 must guarantee is:
  >
  > ```
  > claimed_provider_session_key
  >     ==
  > actual_provider_session_invoked
  > ```
  >
  > for the entire protected operation.
  >
  > Re-derive the smallest architecture change that makes that invariant structurally true.
  >
  > Specifically compare at least these options:
  >
  > 1. Pass the already-validated request binding directly into `handle_turn()`/the dispatch path so this dispatch's provider binding is immutable and does not have to be recovered from mutable global Presence.
  > 2. Resolve/snapshot an authoritative binding once before claiming and carry that immutable snapshot through the turn.
  > 3. Serialize mutation/resolution of a `shared_session_id` as well — but analyze whether this would unnecessarily suppress legitimate concurrency between different provider sessions and whether it conflates Presence with dispatch ownership.
  > 4. Any smaller alternative supported by the existing contracts.
  >
  > Do not choose based on smallest code diff. Choose the design in which it is impossible for a different request to change the provider-session resource after its mutex key has been selected.
  >
  > Also determine why `/dispatch` is writing caller-supplied provider binding into Presence at all. State whether that write represents persistent body presence, temporary routing state, or both. If Presence is currently serving two meanings, name that explicitly before modifying it.
  >
  > Amend the dated design note with this analysis and commit the amendment/design update only. No runtime implementation yet.

  My expectation is that option 1 or something very close to it will win.

  A `/dispatch` request already knows which provider/session it is targeting. Using a mutable registry as an intermediate place to store that binding and then reading it back during the same request is suspicious. Presence makes sense for answering “where is this agent/body currently present?” It is a poor place to obtain an immutable routing decision for a request already in flight.

  There's also a deeper architectural payoff if Claude confirms that: the dispatch's binding becomes a frozen property of the turn, while Presence remains dynamic system state. That is a much cleaner separation.

  The TTL work sounds good. Using the provider adapters' actual hard subprocess ceilings rather than the avatar-side timeout was exactly the right correction. And recording the Ledger race separately was also right.

  But this binding race is a blocker. Fix the design now, and then I think item 1 can move to implementation.

  Read 2 files

● Update(full audit/08-18-2026-item1-dispatch-mutex-design-analysis.md)
Added 13 lines
not to recommend a primitive until a trace proves what it has to protect.
Do not implement any of this until it has been reviewed.

> **Revision 1 (same day)**: §8a's original conclusion — "no refactor of
> `handle_turn()`'s internal binding resolution is needed" — is **wrong**.
> A second reviewer traced an interleaving where that conclusion fails to
> hold: two dispatches acquiring two different, correctly-non-contending
> mutex keys can still end up both operating on the *same* native
> transcript, because `handle_turn()` re-derives its actual dispatch
> binding from mutable, shared `PresenceRegistry` state rather than from
> the immutable request that was validated and claimed against. §8a below
> is left in place, unedited, so the record is honest about what was
> wrong and why — **do not implement §8a as originally written**. The
> correction is §9, appended after the original recommendation; §9's
> conclusion supersedes §8a and the final Recommendation.

## 0. What the re-derivation overturned

The original TODO note framed this as: "protection exists for the default

Also mark the §8a boundary paragraph itself, and the final Recommendation, with pointers to §9:

● Update(full audit/08-18-2026-item1-dispatch-mutex-design-analysis.md)
Added 7 lines
pre-existing characteristic of `PresenceRegistry`, unrelated to and not
introduced by this mutex, out of scope for item 1.

> **This classification is wrong — see §9.** It is not a pre-existing,
> out-of-scope Presence characteristic once a provider-session mutex
> exists: that same overwrite is what lets the *other* caller's dispatch
> silently steer *this* caller into invoking a native session different
> from the one its own claim protects, defeating the mutex's actual
> guarantee. §9 works the interleaving in full.

**Recommended acquisition point**: at the very top of `_handle_dispatch`,
immediately after the `required`-fields check and the `provider_id`→
dispatcher lookup (so a request naming an unknown provider still gets its

Now the main addition — §9, the full corrected analysis:

● Update(full audit/08-18-2026-item1-dispatch-mutex-design-analysis.md)
Added 257 lines
`SessionLedger.append()`'s `turn_id` race is a separate, real bug,
recorded as a new continuation-TODO item in the companion document —
not part of this design, not fixed by it.

> **Superseded by §9 below — do not implement the above as written.**
> §9 replaces "no `handle_turn()` refactor needed" with an explicit,
> required signature change, and folds that into the final recommendation
> at the end of §9.

---

## 9. Revision — the binding must be a frozen input, not a re-derived read

### 9.1 The interleaving that breaks §8a

§8a's claim rested on: *"holding the new claim prevents any other dispatch
to the same native pair from running concurrently."* That's true of the
**claim registry** — but §8a implicitly assumed it was also true of
**Presence**, which it isn't. The claim is keyed on
`(provider_id, provider_session_id)`; `PresenceRegistry` is keyed on
`shared_session_id`. Two dispatches naming *different* native pairs but
the *same* `shared_session_id` acquire two different, non-contending
claims — and then both freely read and write the *same* Presence slot.

```
request A: shared S -> provider A / session 123
request B: shared S -> provider B / session 456

T1  A: claims.claim(key=(A,123))              -> success (uncontended)
T2  B: claims.claim(key=(B,456))              -> success (uncontended, different key)
T3  A: presence.register(session_id=S, endpoint=encode(A,123,...))
        presence._by_session[S] now = (A,123)
T4  B: presence.register(session_id=S, endpoint=encode(B,456,...))
        presence._by_session[S] now = (B,456)   -- overwrites A, "most-recent-wins"
T5  A: bridge.handle_turn(session_id=S, ...)
        step3: record = presence.resolve(S)      -> returns (B,456), NOT what A registered
        step5: binding = ProviderSessionBinding.from_presence_record(record)
               binding = (B,456)
        A calls self._dispatch(binding=(B,456), ...)   -- A invokes the provider
        using B's target, while A's own claim is on key (A,123)
T6  B: bridge.handle_turn(session_id=S, ...)
        step3/step5: resolve(S) -> (B,456) (nothing overwrote it again) -> binding=(B,456)
        B calls self._dispatch(binding=(B,456), ...)   -- B invokes the provider
        using its own, correctly-claimed target
```

At T5–T6, **A and B are both concurrently invoking the native transcript
`(B,456)`** — A while holding a claim on the wrong key `(A,123)`, which
protects nothing relevant; B while holding the *correct* claim on
`(B,456)`, which A's presence-sourced binding silently bypassed entirely.
This is exactly the failure item 1 exists to prevent, reproduced *with*
the mutex from §§1–8 in place. Verified against
`ProviderSessionBinding.from_presence_record()` directly — it performs no
cross-check against who registered the record, which claim the caller
holds, or which call is invoking it; it trusts `record.endpoint` exactly
as currently stored, unconditionally.

The precise property that failed: `§8a` showed *"the claim key and what
gets registered are identical within one call"* — true, but irrelevant.
The property item 1 actually needs is:

```
claimed_provider_session_key == actual_provider_session_invoked
```

held for the *entire* protected operation, not just at the moment of
registration. `handle_turn()` re-reading Presence at step 5 (and step 3)
means the *invoked* side of that equation is decided by whichever
register() happened to land last, globally, across every in-flight
`shared_session_id`-sharing caller — not by what the claim-holder itself
requested.

### 9.2 Why the Presence round-trip is unsafe regardless of sequencing

The register()-then-resolve() pattern is unsafe **no matter when it
happens relative to claim acquisition**, because the claim never protects
`PresenceRegistry`'s `_by_session[shared_session_id]` slot — it's keyed on
a different identity entirely. Moving the register()/resolve() pair
earlier, later, or wrapping it in the claim doesn't help: the claim for
key `(A,123)` provides zero exclusion over writes to `presence._by_session[S]`,
which any caller naming *any* other native pair, under the *same*
`shared_session_id`, can freely perform. The bug isn't in the ordering;
it's in using a globally-shared, coarsely-keyed store as the channel for
a value that needs to stay scoped to one already-in-flight, specifically-
claimed call.

### 9.3 Option comparison

**Option 1 — pass the validated request binding directly into
`handle_turn()`; never re-derive it from Presence for dispatch.**
`_handle_dispatch` already has every field needed
(`provider_id`, `model_id`, `provider_session_id`, `agent_id`,
`instance_id`, `shared_session_id`, `launch_options` — the same fields
§8a already identified as available, side-effect-free, at function entry)
to construct a `ProviderSessionBinding` directly, with no read of
`PresenceRegistry` in the path at all. `handle_turn()` takes this as an
explicit, required parameter and uses it, unmodified, at step 5 (dispatch)
and step 8 (cursor advance) instead of calling
`ProviderSessionBinding.from_presence_record(record)`. Because the same
Python value is used to acquire the claim *and* to dispatch, with no
intervening read of mutable shared state, `claimed_key ==
actual_invoked` holds by construction — there is no step left where they
*could* diverge, for any interleaving. This is the only option below that
makes the invariant **structurally true** rather than **usually true**.

**Option 2 — resolve/snapshot an authoritative binding once before
claiming, carry the snapshot through the turn.** On inspection this
degenerates to Option 1 or fails, depending on how "resolve" is read. If
"resolve" means *read it back from `PresenceRegistry`* (even once, even
before the claim, even under the claim), it inherits exactly the same
vulnerability §9.1 traces — the claim doesn't protect that read no matter
where it sits in the sequence, and another caller's concurrent register()
for the same `shared_session_id` can still land before this call's
"snapshot" read. The *only* way to make a "snapshot" genuinely safe is
for it to never touch `PresenceRegistry` for this purpose at all — at
which point it is Option 1, not a distinct alternative. Not recommended
as a separate design; recorded to show it was considered and why it
collapses into Option 1 rather than competing with it.

**Option 3 — additionally serialize mutation/resolution of
`shared_session_id`.** Would close the race (only one in-flight
`/dispatch` per `shared_session_id` at a time), but at real cost: it
requires a *second*, independent lock with its own key
(`shared_session_id`), its own TTL/lifetime/failure-semantics design (all
of §§4/6/8b redone for a second primitive), and it re-conflates dispatch
ownership with Presence exactly as the original TODO's caution against
extending `PresenceRegistry` warned against — just moved one layer over.
It's also insufficient *alone*: it does nothing for two *different*
`shared_session_id`s that happen to target the *same*
`(provider_id, provider_session_id)` — the exact case the
`(provider_id, provider_session_id)` claim exists for — so it would have
to be layered on top of, not instead of, everything in §§1–8, roughly
doubling the design surface for a result Option 1 achieves with no lock
at all. There is also a legitimacy question worth naming: the continuity
model already treats "the active provider for a `shared_session_id`" as
strictly single-valued at any moment (most-recent-register-wins) — so two
concurrent dispatches to *different* providers for the *same*
`shared_session_id` are arguably never a "legitimate concurrency" case
this system wants to support in parallel in the first place, independent
of the mutex question. Not recommended: more design surface for a
narrower fix than Option 1, layered on top of Option 1 rather than
replacing any part of it.

**Option 4 — detect-and-reject: keep `handle_turn()`'s resolve-based
binding, but compare it against the claimed key immediately before
dispatch and raise instead of proceeding on mismatch.** Smaller diff than
Option 1 — no new `handle_turn()` parameter. But it only *detects* the
drift after it has already happened, rather than preventing the read
that causes it, and it fails the "impossible," not merely "checked,"
bar: it still requires the Presence round-trip and its associated
register()-then-resolve() footgun to exist at all, decorated with a
guard rather than removed. It's also strictly worse for the *caller*: in
the §9.1 trace, A's own request — for the uncontended, correctly-claimed
target `(A,123)` — would be spuriously failed purely because of B's
unrelated, concurrent activity on the same `shared_session_id`, even
though nothing was ever actually wrong with `(A,123)` itself. Option 1
lets A succeed on its own merits, unaffected by B, which is strictly
better on correctness, availability, and simplicity (no new error code,
no new comparison, no continued reliance on the pattern that caused the
bug). Not recommended, named explicitly because it was the "smaller
diff" temptation and rejected on principle, not size.

**Decision: Option 1.**

### 9.4 What Presence is being asked to be — two meanings, conflated

Asked directly: why does `_handle_dispatch` write the caller-supplied
binding into `PresenceRegistry` at all? Two genuinely different things
are happening under one `register()` call today:

1. **Persistent/dynamic body presence** — `PresenceRegistry`'s own
   documented purpose: "is a specific instance of an already-authorized
   agent reachable right now, under which session?" Real, load-bearing,
   used independently of any one in-flight dispatch — `/presence/resolve`
   as a standalone query, `/presence/renew`/`/presence/deregister`
   lifecycle, and `handle_turn()`'s own step 6 (re-resolve Presence,
   validate the *response*'s claimed actor against whoever Presence
   *currently* reports active — a legitimate, independent authorization
   check on the response side, unaffected by anything in this revision).
2. **Temporary per-call routing state** — using `register()`+later
   `resolve()` purely as a side-channel to carry *this specific call's*
   already-known binding from `_handle_dispatch` into `handle_turn()`,
   because `handle_turn()`'s signature doesn't accept it directly. This
   has nothing to do with reachability; it's argument-passing that
   happens to reuse Presence's data shape.

Meaning 2 is what's unsafe, precisely because it's being stored in a
structure whose entire design (meaning 1) requires it to be freely,
immediately overwritable by any other caller's own liveness update
("most-recent-register-wins" is *correct* for meaning 1, and is exactly
what makes it *wrong* for meaning 2). The fix is not to stop calling
`presence.register()` — meaning 1 remains real and needed — it's to stop
reading meaning 2 back out of it for dispatch routing.

### 9.5 The corrected design

- `_handle_dispatch` constructs `binding = ProviderSessionBinding(...)`
  directly from `body`'s own required fields, first — pure, no side
  effects, no Presence read.
- Acquire the claim on `(binding.provider_id, binding.provider_session_id)`
  next (cheaper to fail fast here than to also perform a `presence.register()`
  that's about to be wasted on a `DISPATCH_BUSY` rejection — a small,
  free simplification Option 1 enables that wasn't available in §8a's
  ordering).
- `presence.register(...)` unchanged — still real, still meaning 1, now
  clearly decoupled from routing.
- `SharedSessionBridge.handle_turn()` gains a new **required** parameter,
  `binding: ProviderSessionBinding` (no default — see below for why not
  optional). Step 5 and step 8 use it directly; `from_presence_record()`
  is no longer called for dispatch purposes anywhere in this path.
- Step 3's `presence.resolve(session_id)` **stays exactly as it is
  today** — its role was always "does presence exist at all for this
  session" (`PROVIDER_NOT_REGISTERED` if not), which is a legitimate,
  independent gate; it simply stops being *also* the binding source.
  Explicitly not adding a check that the resolved record matches the
  passed-in `binding` — that would reintroduce a Presence-race-sensitive
  comparison and reproduce Option 4's spurious-failure problem for no
  benefit.
- Step 6 (re-resolve Presence, validate the response actor) is unchanged
  and remains meaningful — it's now unambiguously a pure
  response-authorization check, decoupled from dispatch routing, which is
  arguably a clearer statement of what Gate 11 always intended.
- **Required, not optional, with no presence-derived fallback.** An
  `Optional[ProviderSessionBinding] = None` parameter that falls back to
  today's `from_presence_record()` behavior when omitted would leave the
  vulnerable path reachable by any caller (existing proof scripts, tests)
  that simply doesn't pass one — "avoidable if you remember to," not
  "impossible," failing the bar this revision was asked to meet. Making
  it required is a call-site-breaking change: every existing caller of
  `handle_turn()` (proof scripts under `tier1/engainos/tools/`, the test
  suite) needs updating to construct and pass its own binding explicitly.
  Recorded here as necessary follow-on implementation work, not a
  deferred risk.

This gives the architectural split you'd expect once the two Presence
meanings are named separately: **the dispatch binding becomes a frozen
property of the turn** (constructed once, from the validated request,
never re-read), while **Presence remains purely dynamic system state**
(liveness/reachability, freely overwritable, exactly as
`PresenceRegistry`'s own documentation already says it should be) — no
longer asked to also serve as a mid-flight routing channel for a value
the caller already had.

### 9.6 Updated recommendation (supersedes §8a and the original Recommendation)

Same as the original Recommendation for everything in §§1–8b (mutex key,
critical-section lifetime, `SessionClaimRegistry` extension,
`DISPATCH_BUSY` semantics, fresh per-request `instance_id`, TTL formula,
single-authority-process precondition) — **except** §8a's binding-sourcing
conclusion, replaced by §9.5: `_handle_dispatch` builds the
`ProviderSessionBinding` directly from the request body before touching
Presence or the claim registry; `SharedSessionBridge.handle_turn()` takes
that binding as a new required parameter and uses it for dispatch and
cursor-advance instead of re-deriving it from `PresenceRegistry`; all
existing `handle_turn()` call sites (proof scripts, tests) need updating
to pass their own binding explicitly, with no presence-derived fallback
path left reachable.

Not yet implemented. `SessionLedger.append()`'s `turn_id` race remains a
separate, recorded, not-fixed-here item (companion document).

Now committing this amendment (no runtime code touched):

  Committed 23c6215, ran 1 shell command

Committed (23c6215), no runtime code touched, not pushed. Summary of the correction:

The race was real. Two dispatches naming different native pairs — (A,123) and (B,456) — correctly acquire two non-contending claims, then both freely write into the same PresenceRegistry slot for their shared shared_session_id (most-recent-register-wins). Because handle_turn() re-derives its dispatch binding via presence.resolve() at step 3/5 rather than using what the caller itself claimed, A can end up dispatching to (B,456) — the target B legitimately claimed — while A's own claim sits uselessly on (A,123). Confirmed directly against ProviderSessionBinding.from_presence_record(): no cross-check against claim ownership or caller identity exists anywhere.

§8a is left in the file, marked superseded, not deleted — consistent with this project's practice of keeping wrong conclusions visible rather than erasing them.

§9 adds:
- The precise invariant that has to hold: claimed_key == actual_invoked, for the whole operation, not just at the moment of registration.
- Why sequencing can't fix it — the claim never protects PresenceRegistry itself, so no ordering of register/resolve relative to claim-acquisition helps.
- All four options compared: Option 1 wins. Option 2 (snapshot-before-claiming) collapses into Option 1 once you require the snapshot to bypass Presence entirely. Option 3 (also serialize shared_session_id) is insufficient alone and roughly doubles the design surface. Option 4 (detect-and-reject) was named explicitly as the "smaller diff" temptation and rejected on principle — it still relies on the unsafe read and spuriously fails the uncontended caller for someone else's unrelated activity.
- The Presence dual-meaning finding you asked for: register() is doing double duty as genuine liveness state and an ad-hoc per-call routing side-channel — only the second use is unsafe, and the fix removes only that use, leaving liveness/Presence untouched.
- The corrected design: handle_turn() gains a required ProviderSessionBinding parameter, sourced directly from the validated request body, never re-read from Presence for dispatch — no optional fallback, since anything less than required leaves the vulnerable path reachable. Existing call sites (proof scripts, tests) get named as necessary follow-on work, not a deferred risk.

Everything else from the original note (lock key, critical-section lifetime, SessionClaimRegistry extension, DISPATCH_BUSY, fresh per-request instance_id, TTL formula, single-authority-process precondition) is unchanged and still stands. Ready for another look before implementation.

✻ Worked for 4m 57s

※ recap: Fixing avatar continuity bugs from the continuation TODO: item 4 (launch wrapper) is done and pushed; item 1's dispatch-mutex design was just corrected for a binding race and committed locally, awaiting your review before implementing it.

❯ Yes. With that correction, item 1 is ready to implement.

  The important defect in the first design is now removed structurally rather than patched around: the provider/session identity that selects the mutex is also the immutable identity that reaches the provider. That gives you the invariant we actually needed:

  ```text
  claim (provider_id, provider_session_id)
          ↓
  immutable ProviderSessionBinding
          ↓
  context/cursor construction
          ↓
  provider invocation using SAME binding
          ↓
  cursor advance
          ↓
  release claim
  ```

  That is much stronger than “register something in Presence and hope we read the same thing back later.” The original trace showed that `handle_turn()` was resolving mutable Presence before constructing its provider binding, which was exactly the dangerous part.

  I also like the decision to make `ProviderSessionBinding` required rather than optional. An optional parameter with “fall back to Presence” would leave the unsafe route alive indefinitely. This is one of those cases where breaking the old internal call signature is preferable because every caller must explicitly migrate to the corrected contract.

  There is one implementation rule I would state explicitly before Claude starts:

  **Presence may still be consulted for presence/liveness semantics, but after this change it must never alter, replace, or reconstruct the provider routing binding for an in-flight dispatch.**

  That matters because `handle_turn()` currently resolves Presence more than once.  Those checks can remain if they serve the existing “body must still be ACTIVE” contract, but the result cannot sneak back into `ProviderSessionBinding`.

  I’d now give Claude this implementation instruction:

  > Item 1 design is approved. Proceed to implementation from the committed design in `23c6215`.
  >
  > Implement only the approved dispatch-mutex work. Do not fix the newly recorded `SessionLedger.append()` race, restart persistence, production cutover, or `provider_session_ref`.
  >
  > Implementation requirements:
  >
  > 1. In `presence_authority_server.py::_handle_dispatch`, construct the authoritative `ProviderSessionBinding` directly from the already-validated request `provider_id` and `provider_session_id`.
  >
  > 2. Mint a unique claim-owner identity for every individual `/dispatch` request. Use a genuinely per-request value such as UUID; do not derive it from `agent_id`, provider ID, body ID, or another stable caller identity.
  >
  > 3. Acquire `SessionClaimRegistry` on the composite native-resource key:
  >
  > ```python
  > (provider_id, provider_session_id)
  > ```
  >
  > before the protected continuity operation begins.
  >
  > 4. Generalize the internal `SessionClaimRegistry` key type only as much as necessary to accept the composite key. Preserve the existing public `/claim` and `/release` HTTP contracts unchanged; existing string-key clients must continue working exactly as before.
  >
  > 5. Derive the server-side dispatch claim lifetime from the actual provider dispatch timeout plus the approved safety margin. Do not copy an unrelated avatar timeout. Prefer one authoritative timeout source over duplicated `90`/`120` literals if the current provider layer can expose that cleanly.
  >
  > 6. Call `SharedSessionBridge.handle_turn()` with the immutable `ProviderSessionBinding` as a required argument.
  >
  > 7. Change `handle_turn()` so the supplied binding is the only source of provider routing for that turn.
  >
  > Presence may continue to be resolved wherever the existing contract requires ACTIVE-presence/liveness checks, but a Presence record must never replace, reconstruct, or modify the supplied provider binding.
  >
  > Remove the internal `ProviderSessionBinding.from_presence_record()` routing dependency from this path.
  >
  > 8. Hold the composite claim across the full approved critical section: before continuity/context/cursor state is read through completion of response handling and cursor advancement.
  >
  > 9. Release the claim in `finally`, including provider failure, bridge failure, malformed response, and any other exception path.
  >
  > 10. A competing request for the same `(provider_id, provider_session_id)` must fail immediately with the approved `DISPATCH_BUSY`/HTTP 409 behavior. Do not queue or wait.
  >
  > 11. Preserve the existing client-side/default worker claim behavior for now. The resulting default-path double protection is accepted and belongs to later production-cutover work.
  >
  > Update every affected call site explicitly for the new required `handle_turn(..., binding=...)` contract. Do not restore compatibility by adding a fallback to Presence.
  >
  > Add concurrency tests that prove at minimum:
  >
  > * same provider + same provider session → only one concurrent dispatch enters; the other receives `DISPATCH_BUSY`;
  > * same provider + different provider sessions → both may dispatch concurrently;
  > * different providers + same textual session ID → both may dispatch concurrently;
  > * same `shared_session_id` + different provider/session bindings → both calls invoke exactly their own originally requested native provider targets even if their Presence registrations interleave;
  > * two simultaneous calls from the same declared body/caller still contend because their claim-owner IDs are different;
  > * claim is released after successful completion;
  > * claim is released after provider/bridge exception;
  > * existing public `/claim` and `/release` string-key behavior is unchanged;
  > * existing default avatar path remains compatible despite the temporary double-lock arrangement.
  >
  > Include a deterministic race test for the corrected Presence-routing bug. Do not rely on thread timing/sleep alone if hooks/barriers/events can force this sequence:
  >
  > ```text
  > A claims (A,123)
  > B claims (B,456)
  > A registers Presence
  > B overwrites Presence
  > A continues
  > B continues
  > ```
  >
  > and prove afterward that A actually invokes `(A,123)` and B invokes `(B,456)`.
  >
  > Run the EngAIn suite and all avatar suites affected by the contract change. Preserve and explicitly identify any already-known baseline RED tests rather than silently changing expectations.
  >
  > After offline GREEN/baseline-equivalent results, run a live composed 3D proof through `launch_dragon3d.sh` to ensure the server-side claim does not interfere with the existing worker-side claim and that a real ControlHUD turn still reaches Hermes and returns.
  >
  > Then deliberately exercise concurrent `/dispatch` contention against one native provider session and capture a receipt showing exactly one provider dispatch entered and the competing call received `DISPATCH_BUSY`.
  >
  > Commit runtime implementation separately from the audit proof/receipt. Do not push until the implementation, tests, live proof, and audit record are all reviewed.

  The deterministic test for the Presence-overwrite scenario is especially important. That is the regression test that proves the amendment was not just architectural prose.

  And there’s now a very clean separation of concerns:

  ```text
  PresenceRegistry
      = who/what is currently live

  ProviderSessionBinding
      = immutable destination of this dispatch

  SessionClaimRegistry[(provider_id, provider_session_id)]
      = who may mutate that native conversation right now

  SessionLedger[shared_session_id]
      = EngAIn turn history
  ```

  That separation is substantially better than where this investigation started. The remaining ledger concurrency bug is correctly isolated because its lock identity is `shared_session_id`, not the native provider-session pair.

  Proceed with item 1 implementation.

  Read 10 files, ran 3 shell commands

Nearly identical structure. Now the two cross-provider proof scripts:

  Read 1 file

Good, only 3 handle_turn() calls (lines 173, 204, 231), matching the 3 registrations already read. Now the mailbox portability proof script:

  Read 3 files, ran 2 shell commands

Now implementing. Starting with the foundational pieces.

  Read 1 file

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/core/session_claim_registry.py)
Added 20 lines, removed 2 lines
new one" is atomic across every worker process talking to it over HTTP —
which is the entire point. Two separate in-process registries, one per
worker, would not provide this; that was the mistake this module corrects.

Key generalization (item 1, dispatch mutex): the public /claim and /release
HTTP endpoints still only ever pass a plain str session_id — that JSON
contract is unchanged, and every existing string-keyed caller (the
worker-level default-path claim in hermes_session_adapter.py) continues to
work exactly as before. presence_authority_server.py's own /dispatch
handler additionally calls claim()/release() directly, in-process, with a
composite (provider_id, provider_session_id) tuple key — the real identity
of the native transcript being protected (see
08-18-2026-item1-dispatch-mutex-design-analysis.md for why a bare
session_id is the wrong key once bindings can be overridden). Nothing below
cares which shape a key is — only that it is hashable and stable for the
life of one claim — so this widening is a type generalization, not a
semantic change: "who holds the right to dispatch to this key, right now"
means the same thing whether the key is a str or a (provider_id,
provider_session_id) tuple.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Dict, Optional
from typing import Dict, Optional, Union

ClaimKey = Union[str, "tuple[str, str]"]


@dataclass(frozen=True)
class SessionClaim:
    session_id: str
    session_id: ClaimKey
    agent_id: str
    instance_id: str
    claim_token: str

Now update the claim/release/current method signatures and the internal dict type hint:

  Read 1 file

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/core/session_claim_registry.py)
Added 2 lines, removed 2 lines

class SessionClaimRegistry:
    def __init__(self) -> None:
        self._claims: Dict[str, SessionClaim] = {}
        self._claims: Dict[ClaimKey, SessionClaim] = {}
        self._lock = threading.Lock()

    def claim(
        self,
        session_id: str,
        session_id: ClaimKey,
        agent_id: str,
        instance_id: str,
        lease_seconds: float = 200.0,

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/core/session_claim_registry.py)
Added 2 lines, removed 2 lines
            self._claims[session_id] = new_claim
            return new_claim

    def release(self, session_id: str, claim_token: str) -> bool:
    def release(self, session_id: ClaimKey, claim_token: str) -> bool:
        """Explicit release after a successful dispatch. Only the exact
        claim_token holder may release — a stale/foreign token cannot clear
        someone else's active claim."""

            del self._claims[session_id]
            return True

    def current(self, session_id: str) -> Optional[SessionClaim]:
    def current(self, session_id: ClaimKey) -> Optional[SessionClaim]:
        """Read-only inspection. An expired claim reads as absent — the
        short lease is exactly what recovers a crashed holder without
        requiring an explicit release (module docstring)."""

Now the two provider adapters — adding a named, importable timeout constant each:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/bridgeroom/hermes_provider_adapter.py)
Added 6 lines

HERMES_SESSION_ID_PATTERN = re.compile(r"(?m)^session_id:\s*([^\s]+)\s*$")

# The one authoritative source for how long a real dispatch through this
# adapter may run — dispatch_via_hermes_cli's own default below and the
# presence authority server's dispatch-claim TTL (item 1's mutex) both read
# this, so the two can never silently drift out of sync with each other.
DEFAULT_TIMEOUT_S = 90.0


class HermesDispatchError(Exception):
    """The hermes CLI process itself failed: missing executable, non-zero
    exit, timeout, or output that doesn't contain a parseable session_id."""

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/bridgeroom/hermes_provider_adapter.py)
Added 1 line, removed 1 line
    context: List[Turn],
    player_input: str,
    *,
    timeout_s: float = 90.0,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> Dict[str, Any]:
    hermes_exe = _resolve_hermes_executable()
    argv = _build_argv(hermes_exe, binding, player_input)

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/bridgeroom/claude_code_provider_adapter.py)
Added 8 lines
    conversation* was answered from, not *who* answered."""


# The one authoritative source for how long a real dispatch through this
# adapter may run — dispatch_via_claude_code_cli's own default below and
# the presence authority server's dispatch-claim TTL (item 1's mutex) both
# read this, so the two can never silently drift out of sync with each
# other.
DEFAULT_TIMEOUT_S = 120.0


def _resolve_claude_executable() -> str:
    exe = shutil.which("claude")
    if exe is None:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/bridgeroom/claude_code_provider_adapter.py)
Added 1 line, removed 1 line
    context: List[Turn],
    player_input: str,
    *,
    timeout_s: float = 120.0,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> Dict[str, Any]:
    claude_exe = _resolve_claude_executable()
    argv = _build_argv(claude_exe, binding, player_input)

Now shared_session_bridge.py — the core structural fix:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/bridgeroom/shared_session_bridge.py)
Added 22 lines
    (step 7) — never on a failed or rejected dispatch, so a failure never
    lets a native session's tracked knowledge silently outrun what it
    actually received.

Correction (item 1, dispatch mutex, 2026-08-18 — see
08-18-2026-item1-dispatch-mutex-design-analysis.md §9 for the full
derivation): step 5 used to construct its binding itself, in here, via
`ProviderSessionBinding.from_presence_record(record)` against whatever
`self._presence.resolve(session_id)` returned. That is unsafe under
concurrent dispatch: two callers naming different native provider
sessions but the same `session_id` can correctly hold two different,
non-contending exclusivity claims on those native sessions, and still
both read back whichever one most recently overwrote Presence's single
`session_id`-keyed slot — so a caller could end up invoking a native
session it never claimed, while the caller that *did* claim it invokes
the same one too. `binding` is now a required parameter, constructed
once by the caller from its own already-validated request, before any
claim or Presence call — never re-derived from Presence here. Presence
is still resolved twice in this method (steps 3 and 6), and both uses
remain exactly what they always were: step 3 is a liveness gate ("has
anyone ever registered for this session"), step 6 is a response-
authorization gate ("is the actor who just answered still the one
Presence currently reports ACTIVE"). Neither result is ever used to
construct or replace `binding` — Presence answers "who/what is live,"
never "what should this specific, already-in-flight turn invoke."
"""

from __future__ import annotations

Now the actual method signature and step 5:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/bridgeroom/shared_session_bridge.py)
Added 8 lines
        session_id: str,
        origin_body: str,
        player_input: str,
        binding: ProviderSessionBinding,
        snapshot: Optional[dict] = None,
    ) -> dict:
        """`binding` is required and is the *only* source of provider
        routing for this turn (see the module docstring's Correction).
        The caller must construct it from its own already-validated
        request/claim, never from a `PresenceRecord` obtained inside this
        call. No default is provided on purpose — see the Correction note
        above for why a Presence-derived fallback would silently
        reintroduce the exact bug this parameter exists to close."""
        # 1 — resolve session_id (already in hand as the parameter).

        # 2 — append the player's request first. This is historical fact

  Read 1 file

Now edit steps 3, 5, and 6's comments/code to reflect the corrected design:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/bridgeroom/shared_session_bridge.py)
Added 6 lines, removed 2 lines
            snapshot=snapshot,
        )

        # 3 — only now resolve the ACTIVE provider through Presence. Absence
        # may raise here; it may not un-happen step 2.
        # 3 — only now check that SOMEONE is ACTIVE through Presence.
        # Absence may raise here; it may not un-happen step 2. This is a
        # pure liveness gate — its result is used only for the None check
        # below, never to construct or replace `binding` (see the module
        # docstring's Correction: that used to be this call's second job,
        # and that second job is exactly what was unsafe).
        record = self._presence.resolve(session_id)
        if record is None:
            raise ProviderNotRegistered(f"PROVIDER_NOT_REGISTERED for session_id={session_id!r}")

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/bridgeroom/shared_session_bridge.py)
Added 12 lines, removed 12 lines
            if t.turn_id < request_turn.turn_id
        ]

        # 5 — construct the provider-neutral binding from the resolved
        # record (the only place this happens — see
        # provider_session_binding.py), look up how much of context this
        # exact native session (binding.provider_id,
        # binding.provider_session_id) has already seen, build whatever
        # gets actually dispatched (a recap of only the turns it's missing
        # — see continuity_context_builder.py; player_input itself,
        # unmodified, if it's missing nothing), and dispatch to that
        # provider. This is where real time passes and Presence can
        # change: the provider that was ACTIVE at step 3 may deregister,
        # expire, or be replaced while dispatch is in flight.
        binding = ProviderSessionBinding.from_presence_record(record)
        # 5 — use the caller-supplied binding (the only source of provider
        # routing for this turn — see the module docstring's Correction;
        # this is deliberately NOT re-derived from Presence here), look up
        # how much of context this exact native session
        # (binding.provider_id, binding.provider_session_id) has already
        # seen, build whatever gets actually dispatched (a recap of only
        # the turns it's missing — see continuity_context_builder.py;
        # player_input itself, unmodified, if it's missing nothing), and
        # dispatch to that provider. This is where real time passes and
        # Presence can change — which is exactly why step 6 re-resolves it
        # for the response-authorization check below, rather than trusting
        # this call's own binding or the step-3 record for that purpose.
        last_seen_turn_id = self._cursor.last_seen_turn_id(binding.provider_id, binding.provider_session_id)
        dispatch_input = self._continuity.build(context, player_input, last_seen_turn_id)
        result = self._dispatch(binding, context, dispatch_input)

  Read 1 file

shared_session_bridge.py is done. Now the main presence_authority_server.py rewrite:

  Read 1 file

Now let me update the module docstring, imports, and add the timeout/margin constants:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/server/presence_authority_server.py)
Added 20 lines
at all — dispatch falls through to bare player_input) and why it is
honestly still a real loss of EngAIn-mediated cross-provider continuity
across a restart, not persisted or reconstructed from receipts here.

Dispatch mutex (item 1, 2026-08-18 — see
08-18-2026-item1-dispatch-mutex-design-analysis.md for the full design):
_handle_dispatch claims (provider_id, provider_session_id) — the real
identity of the native provider transcript a dispatch is about to
invoke — from SessionClaimRegistry before SharedSessionBridge.handle_turn()
runs, and releases it in a finally after handle_turn() returns or raises.
This is a second, independent use of the SAME registry instance the public
/claim and /release endpoints already expose (still string-keyed, still
used unchanged by the existing worker-level client-side claim) — never a
new HTTP surface. A contending caller gets DISPATCH_BUSY (409) immediately;
never queued. The claim's owner identity is a UUID minted fresh per
/dispatch call, never a caller-supplied agent_id/instance_id — see the
design note §6 for why reusing a stable caller identity would let two
genuinely concurrent calls silently "refresh" each other's claim instead
of correctly contending. The claimed key is also used to construct the
turn's ProviderSessionBinding directly from the request body — never from
Presence — see shared_session_bridge.py's own module docstring Correction
for why re-deriving it from Presence inside handle_turn() was unsafe.
"""

from __future__ import annotations

import dataclasses
import json
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict

Now the imports for the adapter timeout constants, and the new mapping/margin constants next to _PROVIDER_DISPATCHERS:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/server/presence_authority_server.py)
Added 2 lines
    sys.path.insert(0, str(REPO_ROOT))

from tier1.engainos.bridgeroom.claude_code_provider_adapter import (
    DEFAULT_TIMEOUT_S as CLAUDE_CODE_DEFAULT_TIMEOUT_S,
    ClaudeCodeDispatchError,
    ClaudeCodeSessionDrift,
    dispatch_via_claude_code_cli,
)
from tier1.engainos.bridgeroom.hermes_provider_adapter import (
    DEFAULT_TIMEOUT_S as HERMES_DEFAULT_TIMEOUT_S,
    HermesDispatchError,
    HermesSessionDrift,
    dispatch_via_hermes_cli,

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/server/presence_authority_server.py)
Added 22 lines
    "claude_code": dispatch_via_claude_code_cli,
}

# The dispatch-claim TTL per provider (item 1) — each adapter's own
# enforced subprocess.run(timeout=...) ceiling, read from that adapter
# module directly rather than duplicated as a literal here, so this can
# never silently drift out of sync with the timeout that actually governs
# how long a dispatch call can run. Keys must match _PROVIDER_DISPATCHERS.
_PROVIDER_DISPATCH_TIMEOUT_S = {
    "hermes": HERMES_DEFAULT_TIMEOUT_S,
    "claude_code": CLAUDE_CODE_DEFAULT_TIMEOUT_S,
}

# Fixed safety margin added on top of a provider's own enforced timeout to
# get the claim's lease_seconds — covers the surrounding in-memory Ledger/
# Presence/cursor steps plus subprocess.run's own post-timeout teardown,
# both bounded but not literally zero. See the design note §8b for the
# full derivation of this invariant (claim TTL must exceed the maximum
# possible duration of the protected critical section).
_DISPATCH_CLAIM_MARGIN_SECONDS = 15.0

_DISPATCH_FAILURE_EXCEPTIONS = (
    HermesDispatchError,
    HermesSessionDrift,

)


def _dispatch_claim_lease_seconds(provider_id: str) -> float:
    return _PROVIDER_DISPATCH_TIMEOUT_S[provider_id] + _DISPATCH_CLAIM_MARGIN_SECONDS


def _record_to_dict(record: Any) -> Dict[str, Any]:
    return dataclasses.asdict(record)


Now the core rewrite of _handle_dispatch itself. Let me view the current exact text once more to edit precisely:

  Searched for 1 pattern, read 1 file

Now the full rewrite:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/server/presence_authority_server.py)
Added 95 lines, removed 35 lines
            )
            return

        provider_session_id = body["provider_session_id"]
        agent_id = body.get("agent_id") or provider_id
        instance_id = body.get("instance_id") or f"{provider_id}-dispatch"
        endpoint = ProviderSessionBinding.encode_endpoint(
        # Presence's own instance_id — a stable-per-caller identity, used
        # only for the liveness registration below. Deliberately NOT used
        # as the dispatch claim's owner identity (see claim_owner_id).
        presence_instance_id = body.get("instance_id") or f"{provider_id}-dispatch"
        launch_options = body.get("launch_options") or {}

        # The turn's binding: constructed directly from this request's own
        # already-validated fields, before any claim or Presence call, and
        # never touched again after this point. This is what makes
        # "claimed_key == actual_invoked" structurally true rather than
        # merely usually true — see shared_session_bridge.py's own module
        # docstring Correction, and this module's own docstring above.
        binding = ProviderSessionBinding(
            provider_id=provider_id,
            model_id=body["model_id"],
            provider_session_id=body["provider_session_id"],
            launch_options=body.get("launch_options"),
        )
        # Most-recent-REGISTER-for-a-session_id-wins (PresenceRegistry's own
        # documented rule) — this is how "the worker submits its
        # ProviderSessionBinding" (step 2) becomes "the active provider"
        # (step 3, inside handle_turn's own resolve) without this handler
        # tracking a second, competing notion of who is active itself.
        presence.register(
            provider_session_id=provider_session_id,
            agent_id=agent_id,
            instance_id=instance_id,
            session_id=body["shared_session_id"],
            capabilities=["chat"],
            endpoint=endpoint,
            requested_lease=float(body.get("requested_lease", 300.0)),
            instance_id=presence_instance_id,
            shared_session_id=body["shared_session_id"],
            launch_options=launch_options,
        )

        bridge = SharedSessionBridge(
            presence,
            ledger,
            provider_dispatch=dispatcher,
            continuity_cursor_tracker=cursor,
        # The native-transcript exclusivity claim (item 1). Acquired before
        # any other work — including presence.register() — so a rejected
        # caller never performs a Presence write it didn't need. Keyed on
        # the composite identity, never the bare shared_session_id (see
        # the design note §3 for why either alone is the wrong key), and
        # the owner identity is a fresh UUID per call, never body-derived
        # (see the design note §6 — a caller-supplied identity here would
        # let two genuinely concurrent calls "refresh" each other's claim
        # instead of correctly contending).
        claim_key = (provider_id, provider_session_id)
        claim_owner_id = uuid.uuid4().hex
        claim_result = claims.claim(
            session_id=claim_key,
            agent_id=agent_id,
            instance_id=claim_owner_id,
            lease_seconds=_dispatch_claim_lease_seconds(provider_id),
        )
        if isinstance(claim_result, ClaimRejected):
            self._send_json(
                409,
                {
                    "error": "DISPATCH_BUSY",
                    "provider_id": provider_id,
                    "provider_session_id": provider_session_id,
                    "current_agent_id": claim_result.current_agent_id,
                    "claim_expires_at": claim_result.claim_expires_at,
                },
            )
            return

        try:
            result = bridge.handle_turn(
            # Most-recent-REGISTER-for-a-session_id-wins (PresenceRegistry's
            # own documented rule) — this is Presence's own liveness/
            # discoverability bookkeeping (meaning 1 in the design note's
            # §9.4), independent of dispatch routing. Its outcome is never
            # read back for `binding`, which is already fixed above —
            # another caller overwriting this shared_session_id's Presence
            # record, even mid-call, cannot change what THIS call invokes.
            presence.register(
                agent_id=agent_id,
                instance_id=presence_instance_id,
                session_id=body["shared_session_id"],
                origin_body=body["origin_body"],
                player_input=body["player_input"],
                snapshot=body.get("snapshot"),
                capabilities=["chat"],
                endpoint=ProviderSessionBinding.encode_endpoint(
                    provider_id=provider_id,
                    model_id=body["model_id"],
                    provider_session_id=provider_session_id,
                    launch_options=launch_options,
                ),
                requested_lease=float(body.get("requested_lease", 300.0)),
            )
        except ProviderNotRegistered as exc:
            self._send_json(404, {"error": "PROVIDER_NOT_REGISTERED", "detail": str(exc)})
            return
        except ResponseActorMismatch as exc:
            self._send_json(409, {"error": "RESPONSE_ACTOR_MISMATCH", "detail": str(exc)})
            return
        except _DISPATCH_FAILURE_EXCEPTIONS as exc:
            self._send_json(502, {"error": "PROVIDER_DISPATCH_FAILED", "detail": str(exc)})
            return
        self._send_json(200, result)

            bridge = SharedSessionBridge(
                presence,
                ledger,
                provider_dispatch=dispatcher,
                continuity_cursor_tracker=cursor,
            )
            try:
                result = bridge.handle_turn(
                    session_id=body["shared_session_id"],
                    origin_body=body["origin_body"],
                    player_input=body["player_input"],
                    binding=binding,
                    snapshot=body.get("snapshot"),
                )
            except ProviderNotRegistered as exc:
                self._send_json(404, {"error": "PROVIDER_NOT_REGISTERED", "detail": str(exc)})
                return
            except ResponseActorMismatch as exc:
                self._send_json(409, {"error": "RESPONSE_ACTOR_MISMATCH", "detail": str(exc)})
                return
            except _DISPATCH_FAILURE_EXCEPTIONS as exc:
                self._send_json(502, {"error": "PROVIDER_DISPATCH_FAILED", "detail": str(exc)})
                return
            self._send_json(200, result)
        finally:
            # Always released — success, any of the three caught failure
            # modes above, or any other exception that escapes this block
            # entirely. A `return` inside the try still runs this.
            claims.release(session_id=claim_key, claim_token=claim_result.claim_token)


def run(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    server = ThreadingHTTPServer((host, port), PresenceAuthorityHandler)
    server.daemon_threads = True

  Ran 1 shell command

Now mailbox_request_handler.py:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/bridgeroom/mailbox_request_handler.py)
Added 17 lines
inject, or otherwise touch any continuity recap. That is
ContinuityContextBuilder's job, inside the bridge, for every caller
uniformly, whether this file-based path or a direct Python call.

`binding` (item 1, 2026-08-18): handle_turn() now requires a
ProviderSessionBinding it never re-derives from Presence internally (see
shared_session_bridge.py's own module docstring Correction). This
mailbox request schema carries no provider/session fields of its own, so
this handler cannot construct one from the request the way
presence_authority_server.py's /dispatch handler does — the caller must
supply it, exactly as it must already supply a Bridge already wired to
the right presence/ledger/dispatcher. This is a single-shot, non-
concurrent translation layer (see the module docstring above — explicitly
NOT a persistent polling daemon, and not reachable from
ThreadingHTTPServer's concurrent surface at all), so a caller resolving
its own binding once, synchronously, before calling this function carries
none of the concurrent-interleaving risk item 1's design note traces for
/dispatch — there is no second, concurrent caller for this function to
race against.
"""

from __future__ import annotations

from typing import Any, Dict

from tier1.engainos.bridgeroom.shared_session_bridge import SharedSessionBridge
from tier1.engainos.core.provider_session_binding import ProviderSessionBinding


class MailboxRequestError(Exception):

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/bridgeroom/mailbox_request_handler.py)
Added 7 lines, removed 1 line
    request_path: Path,
    response_path: Path,
    bridge: SharedSessionBridge,
    binding: ProviderSessionBinding,
) -> Dict[str, Any]:
    """Reads one real request.json, runs it through the bridge exactly
    once, writes one real response.json. Returns the same dict written to
    response_path, for a caller (or a test) that wants it without a second
    disk read."""
    disk read.

    `binding` is required, matching handle_turn()'s own contract — see
    this module's docstring for why a caller-resolved binding is safe
    here even though it wouldn't be for /dispatch's concurrent surface."""
    request = _load_request(request_path)

    result = bridge.handle_turn(
        session_id=request["shared_session_id"],
        origin_body=request["origin_body"],
        player_input=request["player_input"],
        binding=binding,
        snapshot=request.get("snapshot"),
    )


All core runtime files done. Now the test/proof call sites. Starting with test_shared_session_continuity_proof.py:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_shared_session_continuity_proof.py)
Added 15 lines
TEST_ENDPOINT = ProviderSessionBinding.encode_endpoint(
    provider_id="hermes", model_id="test-model", provider_session_id="provider-native-session-x"
)
# handle_turn() requires an explicit binding (item 1) rather than
# re-deriving one from Presence — see shared_session_bridge.py's own
# Correction note. None of this file's assertions inspect
# ProviderSessionBinding.instance_id, so one fixed binding matching
# TEST_ENDPOINT is used throughout, independent of whichever instance_id
# a given test's own presence.register() call happens to use.
TEST_BINDING = ProviderSessionBinding(
    provider_id="hermes",
    model_id="test-model",
    provider_session_id="provider-native-session-x",
    agent_id="hermes",
    instance_id="H-1",
    shared_session_id=SESSION_ID,
    launch_options={},
)


def _bridge() -> SharedSessionBridge:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_shared_session_continuity_proof.py)
Added 2 lines
        session_id=SESSION_ID,
        origin_body="dragon_2d",
        player_input="remember the word banana",
        binding=TEST_BINDING,
    )
    assert said_through_2d["origin_body"] == "dragon_2d"
    assert said_through_2d["actor"] == "hermes"

        session_id=SESSION_ID,
        origin_body="dragon_3d",
        player_input="what did I just say?",
        binding=TEST_BINDING,
    )

    # Different door...

  Searched for 1 pattern

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_shared_session_continuity_proof.py)
Added 1 line, removed 1 line
    through handle_turn."""
    bridge = _bridge()
    bridge._presence.register("hermes", "H-1", SESSION_ID, ["chat"], endpoint=TEST_ENDPOINT)
    bridge.handle_turn(SESSION_ID, "dragon_2d", "hello from 2D")
    bridge.handle_turn(SESSION_ID, "dragon_2d", "hello from 2D", binding=TEST_BINDING)

    last_response = bridge._ledger.read_last(SESSION_ID, direction="response")
    assert last_response is not None

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_shared_session_continuity_proof.py)
Added 1 line, removed 1 line
    bridge = _bridge()
    # Nothing registered for this session at all.
    with pytest.raises(ProviderNotRegistered):
        bridge.handle_turn(SESSION_ID, "dragon_2d", "hello?")
        bridge.handle_turn(SESSION_ID, "dragon_2d", "hello?", binding=TEST_BINDING)

    preserved = bridge._ledger.read_last(SESSION_ID, direction="request")
    assert preserved is not None

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_shared_session_continuity_proof.py)
Added 1 line, removed 1 line
        "hermes", "H-2", SESSION_ID, ["chat"], requested_lease=-1.0,  # already expired
    )
    with pytest.raises(ProviderNotRegistered):
        bridge.handle_turn(SESSION_ID, "dragon_2d", "still there?")
        bridge.handle_turn(SESSION_ID, "dragon_2d", "still there?", binding=TEST_BINDING)

    preserved = bridge._ledger.read_last(SESSION_ID, direction="request")
    assert preserved is not None

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_shared_session_continuity_proof.py)
Added 1 line, removed 1 line
    bridge = SharedSessionBridge(presence=presence, ledger=ledger, provider_dispatch=wrong_actor_dispatch)

    with pytest.raises(ResponseActorMismatch):
        bridge.handle_turn(SESSION_ID, "dragon_2d", "hello")
        bridge.handle_turn(SESSION_ID, "dragon_2d", "hello", binding=TEST_BINDING)

    # The request was appended (step 2 happens before dispatch), but no
    # response turn exists — the mismatch must not silently become history.

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_shared_session_continuity_proof.py)
Added 1 line, removed 1 line
    bridge = SharedSessionBridge(presence=presence, ledger=ledger, provider_dispatch=deregisters_mid_call)

    with pytest.raises(ProviderNotRegistered):
        bridge.handle_turn(SESSION_ID, "dragon_2d", "you still there?")
        bridge.handle_turn(SESSION_ID, "dragon_2d", "you still there?", binding=TEST_BINDING)

    assert ledger.read_last(SESSION_ID, direction="request") is not None
    assert ledger.read_last(SESSION_ID, direction="response") is None

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_shared_session_continuity_proof.py)
Added 1 line, removed 1 line
    bridge = SharedSessionBridge(presence=presence, ledger=ledger, provider_dispatch=swaps_actor_mid_call)

    with pytest.raises(ResponseActorMismatch):
        bridge.handle_turn(SESSION_ID, "dragon_2d", "who's there?")
        bridge.handle_turn(SESSION_ID, "dragon_2d", "who's there?", binding=TEST_BINDING)

    assert ledger.read_last(SESSION_ID, direction="request") is not None
    assert ledger.read_last(SESSION_ID, direction="response") is None

All 8 done in that file. Now test_continuity_identity_boundary.py — add the _binding() helper and update all 13 calls:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_continuity_identity_boundary.py)
Added 18 lines
    )


def _binding(provider_id: str, provider_session_id: str, agent_id: str, instance_id: str) -> ProviderSessionBin
ding:
    """handle_turn() requires an explicit binding (item 1) rather than
    re-deriving one from Presence — see shared_session_bridge.py's own
    Correction note. This file's whole point is cursor-keying behavior
    driven by (provider_id, provider_session_id), so each call site below
    passes the binding matching its own preceding presence.register()/
    _endpoint() call exactly, never a shared fixed one."""
    return ProviderSessionBinding(
        provider_id=provider_id,
        model_id="m",
        provider_session_id=provider_session_id,
        agent_id=agent_id,
        instance_id=instance_id,
        shared_session_id=SESSION_ID,
        launch_options={},
    )


def _recording_dispatcher(agent_id: str, calls: list):
    """Echoes agent_id as actor; records the exact dispatch_input it
    received so tests can assert on recap content precisely, without

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_continuity_identity_boundary.py)
Added 4 lines, removed 2 lines

    presence.register("hermes", "H-1", SESSION_ID, endpoint=_endpoint("hermes", "native-session-A"))
    bridge = SharedSessionBridge(presence, ledger, dispatch, continuity_cursor_tracker=cursor)
    bridge.handle_turn(SESSION_ID, "dragon_2d", "remember: copper rain")
    bridge.handle_turn(SESSION_ID, "dragon_2d", "remember: copper rain",
                        binding=_binding("hermes", "native-session-A", "hermes", "H-1"))

    # Same actor label, but a different native session underneath.
    presence.register("hermes", "H-2", SESSION_ID, endpoint=_endpoint("hermes", "native-session-B"))
    bridge.handle_turn(SESSION_ID, "dragon_2d", "what did I say?")
    bridge.handle_turn(SESSION_ID, "dragon_2d", "what did I say?",
                        binding=_binding("hermes", "native-session-B", "hermes", "H-2"))

    assert calls[0] == "remember: copper rain"  # first turn, nothing to recap
    assert "copper rain" in calls[1]  # second call recapped — session B knew nothing

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_continuity_identity_boundary.py)
Added 4 lines, removed 2 lines

    presence.register("hermes", "H-1", SESSION_ID, endpoint=_endpoint("hermes", "expiring-session"))
    bridge = SharedSessionBridge(presence, ledger, dispatch, continuity_cursor_tracker=cursor)
    bridge.handle_turn(SESSION_ID, "dragon_2d", "remember: silver thread")
    bridge.handle_turn(SESSION_ID, "dragon_2d", "remember: silver thread",
                        binding=_binding("hermes", "expiring-session", "hermes", "H-1"))

    presence.register("hermes", "H-1-renewed", SESSION_ID, endpoint=_endpoint("hermes", "replacement-session")
)
    bridge.handle_turn(SESSION_ID, "dragon_2d", "what did I say?")
    bridge.handle_turn(SESSION_ID, "dragon_2d", "what did I say?",
                        binding=_binding("hermes", "replacement-session", "hermes", "H-1-renewed"))

    assert "silver thread" in calls[1]


● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_continuity_identity_boundary.py)
Added 3 lines, removed 2 lines

    presence.register("hermes", "H-1", SESSION_ID, endpoint=_endpoint("hermes", "shared-native-session"))
    bridge = SharedSessionBridge(presence, ledger, dispatch, continuity_cursor_tracker=cursor)
    shared_binding = _binding("hermes", "shared-native-session", "hermes", "H-1")

    bridge.handle_turn(SESSION_ID, "dragon_2d", "remember: copper rain")
    bridge.handle_turn(SESSION_ID, "dragon_3d", "still there?")  # same native session, different door
    bridge.handle_turn(SESSION_ID, "dragon_2d", "remember: copper rain", binding=shared_binding)
    bridge.handle_turn(SESSION_ID, "dragon_3d", "still there?", binding=shared_binding)  # same native session
, different door

    assert calls[0] == "remember: copper rain"
    assert calls[1] == "still there?"  # unmodified — no duplicate recap

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_continuity_identity_boundary.py)
Added 6 lines, removed 3 lines

    presence.register("hermes", "H-1", SESSION_ID, endpoint=_endpoint("hermes", "session-A"))
    bridge_hermes = SharedSessionBridge(presence, ledger, hermes_dispatch, continuity_cursor_tracker=cursor)
    bridge_hermes.handle_turn(SESSION_ID, "dragon_2d", "remember: copper rain")
    bridge_hermes.handle_turn(SESSION_ID, "dragon_2d", "remember: copper rain",
                               binding=_binding("hermes", "session-A", "hermes", "H-1"))

    presence.register("claude_code", "CC-1", SESSION_ID, endpoint=_endpoint("claude_code", "session-B"))
    bridge_claude = SharedSessionBridge(presence, ledger, claude_dispatch, continuity_cursor_tracker=cursor)
    bridge_claude.handle_turn(SESSION_ID, "dragon_3d", "confirm the phrase")
    bridge_claude.handle_turn(SESSION_ID, "dragon_3d", "confirm the phrase",
                               binding=_binding("claude_code", "session-B", "claude_code", "CC-1"))

    presence.register("hermes", "H-1-return", SESSION_ID, endpoint=_endpoint("hermes", "session-A"))
    bridge_hermes_2 = SharedSessionBridge(presence, ledger, hermes_dispatch, continuity_cursor_tracker=cursor)
    bridge_hermes_2.handle_turn(SESSION_ID, "dragon_2d", "what happened while I was away?")
    bridge_hermes_2.handle_turn(SESSION_ID, "dragon_2d", "what happened while I was away?",
                                 binding=_binding("hermes", "session-A", "hermes", "H-1-return"))

    final_recap = hermes_calls[-1]
    assert "confirm the phrase" in final_recap  # the missed Claude turn

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_continuity_identity_boundary.py)
Added 5 lines, removed 3 lines

    presence.register("hermes", "H-1", SESSION_ID, endpoint=_endpoint("hermes", "session-A"))
    bridge_hermes = SharedSessionBridge(presence, ledger, _recording_dispatcher("hermes", hermes_calls), conti
nuity_cursor_tracker=cursor)
    bridge_hermes.handle_turn(SESSION_ID, "dragon_2d", "first fact")
    bridge_hermes.handle_turn(SESSION_ID, "dragon_2d", "second fact")
    hermes_binding = _binding("hermes", "session-A", "hermes", "H-1")
    bridge_hermes.handle_turn(SESSION_ID, "dragon_2d", "first fact", binding=hermes_binding)
    bridge_hermes.handle_turn(SESSION_ID, "dragon_2d", "second fact", binding=hermes_binding)

    presence.register("claude_code", "CC-1", SESSION_ID, endpoint=_endpoint("claude_code", "brand-new-session"
))
    bridge_claude = SharedSessionBridge(presence, ledger, _recording_dispatcher("claude_code", claude_calls),
continuity_cursor_tracker=cursor)
    bridge_claude.handle_turn(SESSION_ID, "dragon_3d", "summarize everything")
    bridge_claude.handle_turn(SESSION_ID, "dragon_3d", "summarize everything",
                               binding=_binding("claude_code", "brand-new-session", "claude_code", "CC-1"))

    recap = claude_calls[0]
    assert "first fact" in recap

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_continuity_identity_boundary.py)
Added 4 lines, removed 2 lines
    bridge = SharedSessionBridge(presence, ledger, lying_dispatch, continuity_cursor_tracker=cursor)

    with pytest.raises(ResponseActorMismatch):
        bridge.handle_turn(SESSION_ID, "dragon_2d", "hello")
        bridge.handle_turn(SESSION_ID, "dragon_2d", "hello",
                            binding=_binding("hermes", "flaky-session", "hermes", "H-1"))

    assert cursor.last_seen_turn_id("hermes", "flaky-session") == -1


    calls: list = []
    presence.register("hermes", "H-1-b", SESSION_ID, endpoint=_endpoint("hermes", "flaky-session"))
    bridge2 = SharedSessionBridge(presence, ledger, _recording_dispatcher("hermes", calls), continuity_cursor_
tracker=cursor)
    bridge2.handle_turn(SESSION_ID, "dragon_2d", "are you there now?")
    bridge2.handle_turn(SESSION_ID, "dragon_2d", "are you there now?",
                         binding=_binding("hermes", "flaky-session", "hermes", "H-1-b"))

    assert "hello" in calls[0]

Let's verify all call sites in this file are updated:

  Searched for 1 pattern

All 13 accounted for. Now test_mailbox_request_handler.py:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_mailbox_request_handler.py)
Added 12 lines
TEST_ENDPOINT = ProviderSessionBinding.encode_endpoint(
    provider_id="hermes", model_id="test-model", provider_session_id="provider-native-x"
)
# handle_mailbox_request() now requires an explicit binding, matching
# handle_turn()'s own required-parameter contract (item 1) — see
# mailbox_request_handler.py's module docstring.
TEST_BINDING = ProviderSessionBinding(
    provider_id="hermes",
    model_id="test-model",
    provider_session_id="provider-native-x",
    agent_id="hermes",
    instance_id="H-1",
    shared_session_id=SESSION_ID,
    launch_options={},
)


def _bridge_with_registered_hermes() -> SharedSessionBridge:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_mailbox_request_handler.py)
Added 5 lines, removed 5 lines
    }))

    bridge = _bridge_with_registered_hermes()
    result = handle_mailbox_request(request_path, response_path, bridge)
    result = handle_mailbox_request(request_path, response_path, bridge, TEST_BINDING)

    assert response_path.exists()
    on_disk = json.loads(response_path.read_text())

    ledger = SessionLedger()
    bridge = SharedSessionBridge(presence=presence, ledger=ledger)

    handle_mailbox_request(request_path, response_path, bridge)
    handle_mailbox_request(request_path, response_path, bridge, TEST_BINDING)

    recorded_request = ledger.read_last(SESSION_ID, direction="request")
    assert recorded_request.payload == bare_input


    bridge = _bridge_with_registered_hermes()
    with pytest.raises(MailboxRequestError, match="player_input"):
        handle_mailbox_request(request_path, response_path, bridge)
        handle_mailbox_request(request_path, response_path, bridge, TEST_BINDING)

    assert not response_path.exists()



    bridge = _bridge_with_registered_hermes()
    with pytest.raises(MailboxRequestError, match="not valid JSON"):
        handle_mailbox_request(request_path, response_path, bridge)
        handle_mailbox_request(request_path, response_path, bridge, TEST_BINDING)


def test_response_directory_is_created_if_it_does_not_exist(tmp_path: Path):

    }))

    bridge = _bridge_with_registered_hermes()
    handle_mailbox_request(request_path, response_path, bridge)
    handle_mailbox_request(request_path, response_path, bridge, TEST_BINDING)

    assert response_path.exists()

  Searched for 1 pattern

All 5 updated correctly. Now the live proof scripts. live_hermes_continuity_proof.py:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_hermes_continuity_proof.py)
Added 10 lines, removed 1 line
    )
    bridge = SharedSessionBridge(presence=presence, ledger=ledger, provider_dispatch=dispatch_via_hermes_cli)
    session_id = shared_session_id  # every bridge/ledger call below uses EngAIn's key, never the vendor's
    # handle_turn() requires an explicit binding (item 1) rather than
    # re-deriving one from Presence — constructed here from the exact same
    # fields just registered above.
    binding = ProviderSessionBinding(
        provider_id="hermes", model_id="gpt-5.6-sol", provider_session_id=provider_session_id,
        agent_id="hermes", instance_id="H-LIVE-1", shared_session_id=shared_session_id,
        launch_options={"provider": "openai-codex"},
    )

    print("\n2. Ask through dragon_2d: remember 'copper rain'...")
    said_2d = bridge.handle_turn(session_id, "dragon_2d", "Remember the phrase: copper rain. Reply with exactl
y: noted.")
    said_2d = bridge.handle_turn(session_id, "dragon_2d", "Remember the phrase: copper rain. Reply with exactl
y: noted.",
                                  binding=binding)
    print(f"   dragon_2d <- hermes: {said_2d['response']!r}")
    check(said_2d["actor"] == "hermes", "response actor is hermes")
    check(said_2d["origin_body"] == "dragon_2d", "response returned through dragon_2d")

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_hermes_continuity_proof.py)
Added 1 line
    asked_3d = bridge.handle_turn(
        session_id, "dragon_3d",
        "What phrase did I just ask you to remember? Reply with only the phrase, nothing else.",
        binding=binding,
    )
    print(f"   dragon_3d <- hermes: {asked_3d['response']!r}")


Now the third call (bridge2, the failure-proof section):

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_hermes_continuity_proof.py)
Added 6 lines, removed 1 line
            launch_options={"provider": "openai-codex"},
        ),
    )
    binding_2 = ProviderSessionBinding(
        provider_id="hermes", model_id="gpt-5.6-sol", provider_session_id=provider_session_id_2,
        agent_id="hermes", instance_id="H-LIVE-2", shared_session_id=session_id_2,
        launch_options={"provider": "openai-codex"},
    )

    def deregister_right_after_real_dispatch(binding, context, player_input):
        result = dispatch_via_hermes_cli(binding, context, player_input)

    print("   dispatch begins -> real hermes call in flight -> presence deregisters right after it returns..."
)
    raised = None
    try:
        bridge2.handle_turn(session_id_2, "dragon_2d", "Reply with exactly: should not be recorded")
        bridge2.handle_turn(session_id_2, "dragon_2d", "Reply with exactly: should not be recorded", binding=b
inding_2)
    except ProviderNotRegistered as exc:
        raised = exc


Now live_claude_code_continuity_proof.py — same structural pattern:

  Read 1 file

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_claude_code_continuity_proof.py)
Added 10 lines, removed 1 line
    )
    bridge = SharedSessionBridge(presence=presence, ledger=ledger, provider_dispatch=dispatch_via_claude_code_
cli)
    session_id = shared_session_id  # every bridge/ledger call below uses EngAIn's key, never the vendor's
    # handle_turn() requires an explicit binding (item 1) rather than
    # re-deriving one from Presence — constructed here from the exact same
    # fields just registered above.
    binding = ProviderSessionBinding(
        provider_id="claude_code", model_id="", provider_session_id=provider_session_id,
        agent_id="claude_code", instance_id="CC-LIVE-1", shared_session_id=shared_session_id,
        launch_options={},
    )

    print("\n2. Ask through dragon_2d: remember 'copper rain'...")
    said_2d = bridge.handle_turn(session_id, "dragon_2d", "Remember the phrase: copper rain. Reply with exactl
y: noted.")
    said_2d = bridge.handle_turn(session_id, "dragon_2d", "Remember the phrase: copper rain. Reply with exactl
y: noted.",
                                  binding=binding)
    print(f"   dragon_2d <- claude_code: {said_2d['response']!r}")
    check(said_2d["actor"] == "claude_code", "response actor is claude_code")
    check(said_2d["origin_body"] == "dragon_2d", "response returned through dragon_2d")

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_claude_code_continuity_proof.py)
Added 1 line
    asked_3d = bridge.handle_turn(
        session_id, "dragon_3d",
        "What phrase did I just ask you to remember? Reply with only the phrase, nothing else.",
        binding=binding,
    )
    print(f"   dragon_3d <- claude_code: {asked_3d['response']!r}")


● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_claude_code_continuity_proof.py)
Added 6 lines, removed 1 line
            provider_id="claude_code", model_id="", provider_session_id=provider_session_id_2,
        ),
    )
    binding_2 = ProviderSessionBinding(
        provider_id="claude_code", model_id="", provider_session_id=provider_session_id_2,
        agent_id="claude_code", instance_id="CC-LIVE-2", shared_session_id=session_id_2,
        launch_options={},
    )

    def deregister_right_after_real_dispatch(binding, context, player_input):
        result = dispatch_via_claude_code_cli(binding, context, player_input)

    print("   dispatch begins -> real claude call in flight -> presence deregisters right after it returns..."
)
    raised = None
    try:
        bridge2.handle_turn(session_id_2, "dragon_2d", "Reply with exactly: should not be recorded")
        bridge2.handle_turn(session_id_2, "dragon_2d", "Reply with exactly: should not be recorded", binding=b
inding_2)
    except ProviderNotRegistered as exc:
        raised = exc


Now live_cross_provider_portability_proof.py — add binding helpers and update the 3 calls:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_cross_provider_portability_proof.py)
Added 20 lines
    )


# handle_turn() requires an explicit binding (item 1) rather than
# re-deriving one from Presence — see shared_session_bridge.py's own
# Correction note. These mirror _hermes_endpoint/_claude_endpoint above,
# built from the exact same fields.
def _hermes_binding(provider_session_id: str, agent_id: str, instance_id: str, shared_session_id: str) -> Prov
iderSessionBinding:
    return ProviderSessionBinding(
        provider_id="hermes", model_id="gpt-5.6-sol", provider_session_id=provider_session_id,
        agent_id=agent_id, instance_id=instance_id, shared_session_id=shared_session_id,
        launch_options={"provider": "openai-codex"},
    )


def _claude_binding(provider_session_id: str, agent_id: str, instance_id: str, shared_session_id: str) -> Prov
iderSessionBinding:
    return ProviderSessionBinding(
        provider_id="claude_code", model_id="", provider_session_id=provider_session_id,
        agent_id=agent_id, instance_id=instance_id, shared_session_id=shared_session_id,
        launch_options={},
    )


def run() -> dict:
    receipt: dict = {"schema": "engain.cross_provider_portability_proof.v1", "started_at": time.time()}


● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_cross_provider_portability_proof.py)
Added 1 line
    said_via_hermes = bridge_hermes_1.handle_turn(
        shared_session_id, "dragon_2d",
        f"Remember the phrase: {REMEMBERED_PHRASE}. Reply with exactly: noted.",  # bare — no recap
        binding=_hermes_binding(hermes_provider_session_id_1, "hermes", "H-1", shared_session_id),
    )
    print(f"   dragon_2d <- hermes: {said_via_hermes['response']!r}")
    check(said_via_hermes["actor"] == "hermes", "response actor is hermes")

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_cross_provider_portability_proof.py)
Added 1 line
    asked_via_claude = bridge_claude.handle_turn(
        shared_session_id, "dragon_3d",
        "What phrase did I just ask you to remember? Reply with only the phrase, nothing else.",  # bare
        binding=_claude_binding(claude_provider_session_id, "claude_code", "CC-1", shared_session_id),
    )
    print(f"   dragon_3d <- claude_code: {asked_via_claude['response']!r}")
    check(asked_via_claude["actor"] == "claude_code", "response actor is claude_code")

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_cross_provider_portability_proof.py)
Added 1 line
    asked_via_hermes_again = bridge_hermes_2.handle_turn(
        shared_session_id, "dragon_2d",
        "What did the other assistant just tell me? Reply with only the phrase, nothing else.",  # bare
        binding=_hermes_binding(hermes_provider_session_id_1, "hermes", "H-2-return", shared_session_id),
    )
    print(f"   dragon_2d <- hermes (same stale native session): {asked_via_hermes_again['response']!r}")
    check(asked_via_hermes_again["actor"] == "hermes", "response actor is hermes")

Now the mailbox portability proof — update _submit_mailbox_request signature and its 3 call sites:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_cross_provider_mailbox_portability_proof.py)
Added 6 lines, removed 2 lines
    origin_body: str,
    player_input: str,
    bridge: SharedSessionBridge,
    binding: ProviderSessionBinding,
) -> dict:
    """Writes one bare request file, processes it through the real mailbox
    handler, reads back one real response file. player_input here is
    always exactly what a human would type — no recap, no provider names,
    no prior-turn text assembled by this script."""
    no prior-turn text assembled by this script.

    `binding` is required, matching handle_mailbox_request()'s own
    required-parameter contract (item 1)."""
    request_path = MAILBOX_DIR / f"{turn_name}.request.json"
    response_path = MAILBOX_DIR / f"{turn_name}.response.json"
    request_path.parent.mkdir(parents=True, exist_ok=True)

        "origin_body": origin_body,
        "player_input": player_input,
    }, indent=2))
    return handle_mailbox_request(request_path, response_path, bridge)
    return handle_mailbox_request(request_path, response_path, bridge, binding)


def run() -> dict:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_cross_provider_mailbox_portability_proof.py)
Added 6 lines, removed 1 line
        presence=presence, ledger=ledger, provider_dispatch=dispatch_via_hermes_cli,
        continuity_cursor_tracker=cursor,
    )
    hermes_binding_1 = ProviderSessionBinding(
        provider_id="hermes", model_id="gpt-5.6-sol", provider_session_id=hermes_provider_session_id_1,
        agent_id="hermes", instance_id="H-1", shared_session_id=shared_session_id,
        launch_options={"provider": "openai-codex"},
    )

    turn_1 = _submit_mailbox_request(
        "01_hermes_remember", shared_session_id, "dragon_2d",
        f"Remember the phrase: {REMEMBERED_PHRASE}. Reply with exactly: noted.",  # bare — no recap
        bridge_hermes,
        bridge_hermes, hermes_binding_1,
    )
    print(f"   dragon_2d <- hermes: {turn_1['response']!r}")
    check(turn_1["actor"] == "hermes", "response actor is hermes")

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_cross_provider_mailbox_portability_proof.py)
Added 6 lines, removed 1 line
        presence=presence, ledger=ledger, provider_dispatch=dispatch_via_claude_code_cli,
        continuity_cursor_tracker=cursor,
    )
    claude_binding = ProviderSessionBinding(
        provider_id="claude_code", model_id="", provider_session_id=claude_provider_session_id,
        agent_id="claude_code", instance_id="CC-1", shared_session_id=shared_session_id,
        launch_options={},
    )

    print("\n5+6. Ask Claude Code about the earlier Hermes turn — a bare mailbox request, no recap written by
this script...")
    turn_2 = _submit_mailbox_request(
        "02_claude_recall", shared_session_id, "dragon_3d",
        "What phrase did I just ask you to remember? Reply with only the phrase, nothing else.",  # bare
        bridge_claude,
        bridge_claude, claude_binding,
    )
    print(f"   dragon_3d <- claude_code: {turn_2['response']!r}")
    check(turn_2["actor"] == "claude_code", "response actor is claude_code")

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_cross_provider_mailbox_portability_proof.py)
Added 6 lines, removed 1 line
        presence=presence, ledger=ledger, provider_dispatch=dispatch_via_hermes_cli,
        continuity_cursor_tracker=cursor,
    )
    hermes_binding_2 = ProviderSessionBinding(
        provider_id="hermes", model_id="gpt-5.6-sol", provider_session_id=hermes_provider_session_id_1,
        agent_id="hermes", instance_id="H-2-return", shared_session_id=shared_session_id,
        launch_options={"provider": "openai-codex"},
    )

    turn_3 = _submit_mailbox_request(
        "03_hermes_recover", shared_session_id, "dragon_2d",
        "What did the other assistant just tell me? Reply with only the phrase, nothing else.",  # bare
        bridge_hermes_2,
        bridge_hermes_2, hermes_binding_2,
    )
    print(f"   dragon_2d <- hermes (same stale native session): {turn_3['response']!r}")
    check(turn_3["actor"] == "hermes", "response actor is hermes")

All call sites updated. Let's syntax-check everything at once:

  Ran 1 shell command

Now let's run the existing offline suite to see where we stand before adding new tests:

  Ran 1 shell command

Excellent — all 215 pre-existing tests pass. Now adding the new tests. First, composite-key tests in test_session_claim_registry.py:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_session_claim_registry.py)
Added 53 lines
    assert second.claim_token != first.claim_token  # a fresh token each time


def test_composite_key_claim_and_release():
    """Item 1: the presence authority's own /dispatch handler claims a
    (provider_id, provider_session_id) tuple directly, in-process — never
    through the public /claim HTTP endpoint. The registry itself doesn't
    care: a tuple key works exactly like a string key."""
    reg = SessionClaimRegistry()
    key = ("hermes", "native-session-A")
    result = reg.claim(key, "hermes", "req-a-uuid", lease_seconds=30.0)
    assert isinstance(result, SessionClaim)
    assert result.session_id == key
    assert reg.release(key, result.claim_token) is True


def test_composite_key_second_claimant_rejected_while_first_holds_it():
    reg = SessionClaimRegistry()
    key = ("hermes", "native-session-A")
    reg.claim(key, "hermes", "req-a-uuid", lease_seconds=30.0)
    result = reg.claim(key, "hermes", "req-b-uuid", lease_seconds=30.0)
    assert isinstance(result, ClaimRejected)
    assert result.reason == "SESSION_OCCUPIED"
    assert result.current_instance_id == "req-a-uuid"


def test_composite_key_does_not_collide_with_a_string_key():
    """(provider_id, provider_session_id) and a bare session_id string
    live in the same dict but are never the same key, even if their text
    happens to overlap — a hashability/equality sanity check, not just an
    assumption."""
    reg = SessionClaimRegistry()
    tuple_key = ("hermes", SESSION_ID)
    string_key = SESSION_ID
    first = reg.claim(tuple_key, "hermes", "req-a-uuid", lease_seconds=30.0)
    second = reg.claim(string_key, "hermes", "req-b-uuid", lease_seconds=30.0)
    assert isinstance(first, SessionClaim)
    assert isinstance(second, SessionClaim)  # no false contention between the two distinct keys
    assert reg.current(tuple_key).claim_token == first.claim_token
    assert reg.current(string_key).claim_token == second.claim_token


def test_composite_key_different_provider_session_pairs_do_not_contend():
    """The three-way comparison item 1's design note proves the key from:
    same provider/different session, and different provider/same textual
    session_id, must both proceed concurrently — checked here at the
    registry level directly."""
    reg = SessionClaimRegistry()
    same_provider_diff_session = reg.claim(("hermes", "123"), "hermes", "req-1", lease_seconds=30.0)
    same_provider_diff_session_2 = reg.claim(("hermes", "456"), "hermes", "req-2", lease_seconds=30.0)
    diff_provider_same_text = reg.claim(("claude_code", "123"), "claude_code", "req-3", lease_seconds=30.0)
    assert isinstance(same_provider_diff_session, SessionClaim)
    assert isinstance(same_provider_diff_session_2, SessionClaim)
    assert isinstance(diff_provider_same_text, SessionClaim)


def test_concurrent_claims_only_one_winner():
    """The actual atomicity property, exercised with real threads rather
    than trusted by inspection — many callers racing for one session_id

  Read 1 file, ran 1 shell command

Now appending the new tests to this file:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_presence_authority_dispatch.py)
Added 231 lines
    status, resp = _post(live_authority, "/dispatch", _hermes_body())
    assert status == 409
    assert resp["error"] == "RESPONSE_ACTOR_MISMATCH"


# --- Item 1: concurrent-/dispatch mutex --------------------------------
#
# Real HTTP, real threads, against the same live_authority fixture above —
# matching this file's own existing discipline (deterministic fakes, no
# real subprocess/network calls, but genuine concurrency via real OS
# threads, not simulated).

def _blocking_dispatcher(actor: str, entered: threading.Event, release: threading.Event):
    """Lets a test hold a dispatch open exactly as long as it needs to, so
    a second, concurrent request can be sent while the first is
    provably still inside the provider call — never relying on sleep."""
    def dispatch(binding, context, player_input):
        entered.set()
        assert release.wait(timeout=5), "test never released the blocked dispatcher"
        return {"actor": actor, "response": f"{actor}: {player_input}"}
    return dispatch


def test_dispatch_busy_when_same_provider_and_provider_session_contended(live_authority):
    """Case 1 of the design note's three-way comparison: same
    (provider_id, provider_session_id) must serialize."""
    entered = threading.Event()
    release = threading.Event()
    authority_module._PROVIDER_DISPATCHERS["hermes"] = _blocking_dispatcher("hermes", entered, release)

    results: Dict[str, Tuple[int, Dict[str, Any]]] = {}

    def send_a():
        results["a"] = _post(live_authority, "/dispatch", _hermes_body(player_input="from A"))

    t = threading.Thread(target=send_a)
    t.start()
    assert entered.wait(timeout=5), "first dispatch never entered the provider call"

    status_b, resp_b = _post(live_authority, "/dispatch", _hermes_body(player_input="from B", instance_id="req
-b"))
    assert status_b == 409
    assert resp_b["error"] == "DISPATCH_BUSY"
    assert resp_b["provider_id"] == "hermes"
    assert resp_b["provider_session_id"] == "hermes-native-1"

    release.set()
    t.join(timeout=5)
    assert results["a"][0] == 200


def test_same_provider_different_provider_sessions_dispatch_concurrently(live_authority):
    """Case 2: same provider, different provider_session_id — must not
    contend with each other (provider_id alone would be too coarse a key)."""
    results: Dict[str, Tuple[int, Dict[str, Any]]] = {}

    def send(label: str, provider_session_id: str) -> None:
        results[label] = _post(live_authority, "/dispatch", _hermes_body(
            provider_session_id=provider_session_id, player_input=label,
        ))

    t1 = threading.Thread(target=send, args=("a", "hermes-native-1"))
    t2 = threading.Thread(target=send, args=("b", "hermes-native-2"))
    t1.start()
    t2.start()
    t1.join(timeout=5)
    t2.join(timeout=5)
    assert results["a"][0] == 200
    assert results["b"][0] == 200


def test_different_providers_same_textual_session_id_dispatch_concurrently(live_authority):
    """Case 3: session_id "123" colliding as text across two different
    providers names two unrelated native transcripts — must not contend
    (bare session_id alone would be too coarse a key)."""
    results: Dict[str, Tuple[int, Dict[str, Any]]] = {}

    def send(label: str, provider_id: str, model_id: str) -> None:
        results[label] = _post(live_authority, "/dispatch", _hermes_body(
            provider_id=provider_id, model_id=model_id, provider_session_id="123", player_input=label,
        ))

    t1 = threading.Thread(target=send, args=("a", "hermes", "gpt-5.6-sol"))
    t2 = threading.Thread(target=send, args=("b", "claude_code", "claude-x"))
    t1.start()
    t2.start()
    t1.join(timeout=5)
    t2.join(timeout=5)
    assert results["a"][0] == 200
    assert results["b"][0] == 200


def test_same_declared_caller_still_contends_because_claim_owner_is_fresh(live_authority):
    """Two requests declaring the identical agent_id/instance_id (as a
    single misbehaving or retrying caller might) must still correctly
    contend — the claim's own owner identity is a UUID minted fresh per
    /dispatch call, never copied from the body, precisely so this case
    cannot be mistaken for the same caller reentrantly refreshing its own
    claim (design note §6)."""
    entered = threading.Event()
    release = threading.Event()
    authority_module._PROVIDER_DISPATCHERS["hermes"] = _blocking_dispatcher("hermes", entered, release)

    results: Dict[str, Tuple[int, Dict[str, Any]]] = {}

    def send_a():
        results["a"] = _post(live_authority, "/dispatch", _hermes_body(
            agent_id="dragon_2d", instance_id="dragon-worker", player_input="from A",
        ))

    t = threading.Thread(target=send_a)
    t.start()
    assert entered.wait(timeout=5)

    status_b, resp_b = _post(live_authority, "/dispatch", _hermes_body(
        agent_id="dragon_2d", instance_id="dragon-worker", player_input="from B",
    ))
    assert status_b == 409
    assert resp_b["error"] == "DISPATCH_BUSY"

    release.set()
    t.join(timeout=5)
    assert results["a"][0] == 200


def test_claim_released_after_successful_dispatch(live_authority):
    status1, _ = _post(live_authority, "/dispatch", _hermes_body(player_input="first"))
    assert status1 == 200
    # Same (provider_id, provider_session_id) as the first call — only
    # succeeds if the first call's claim was actually released.
    status2, _ = _post(live_authority, "/dispatch", _hermes_body(player_input="second"))
    assert status2 == 200


def test_claim_released_after_dispatch_failure(live_authority):
    def boom(binding, context, player_input):
        raise HermesDispatchError("simulated CLI failure")

    authority_module._PROVIDER_DISPATCHERS["hermes"] = boom
    status1, resp1 = _post(live_authority, "/dispatch", _hermes_body(player_input="first"))
    assert status1 == 502
    assert resp1["error"] == "PROVIDER_DISPATCH_FAILED"

    authority_module._PROVIDER_DISPATCHERS["hermes"] = _fake_dispatcher("hermes")
    status2, _ = _post(live_authority, "/dispatch", _hermes_body(player_input="second"))
    assert status2 == 200


def test_presence_overwrite_during_dispatch_does_not_redirect_either_caller(live_authority):
    """The regression test for the corrected design (item 1 design note
    §9, amendment to the original §8a). Forces the exact interleaving
    that broke the first draft, deterministically via real synchronization
    primitives rather than sleep:

        A claims (hermes, native-A-123)
        B claims (claude_code, native-B-456)
        A registers Presence for the shared shared_session_id
        B overwrites that same Presence record (different provider)
        A continues
        B continues

    and proves each caller's dispatcher still receives its OWN originally
    requested (provider_id, provider_session_id) — never the other's —
    despite the overwrite landing squarely between A's claim and A's
    dispatch."""
    real_register = authority_module.presence.register
    a_registered = threading.Event()
    b_registered = threading.Event()

    def synced_register(*, agent_id, instance_id, session_id, capabilities=None, endpoint=None, requested_leas
e=300.0):
        if instance_id == "req-b":
            # B's real register (the overwrite) must not happen until
            # A's own real register has already completed.
            assert a_registered.wait(timeout=5), "A never registered — synchronization broken"
        record = real_register(
            agent_id=agent_id, instance_id=instance_id, session_id=session_id,
            capabilities=capabilities, endpoint=endpoint, requested_lease=requested_lease,
        )
        if instance_id == "req-a":
            a_registered.set()
            # A must not proceed into handle_turn() until B has overwritten
            # Presence — this is the exact worst-case ordering from the
            # design note's trace.
            assert b_registered.wait(timeout=5), "B never registered — synchronization broken"
        elif instance_id == "req-b":
            b_registered.set()
        return record

    authority_module.presence.register = synced_register

    received: Dict[str, Tuple[str, str]] = {}

    def make_recording_dispatcher(label: str):
        def dispatch(binding, context, player_input):
            received[label] = (binding.provider_id, binding.provider_session_id)
            return {"actor": binding.agent_id, "response": f"{label}-ack"}
        return dispatch

    authority_module._PROVIDER_DISPATCHERS["hermes"] = make_recording_dispatcher("A")
    authority_module._PROVIDER_DISPATCHERS["claude_code"] = make_recording_dispatcher("B")

    shared_session_id = "shared-presence-overwrite-race"
    results: Dict[str, Tuple[int, Dict[str, Any]]] = {}

    def send_a():
        results["a"] = _post(live_authority, "/dispatch", {
            "shared_session_id": shared_session_id, "origin_body": "dragon_2d",
            "player_input": "hi from A", "provider_id": "hermes",
            "model_id": "gpt-5.6-sol", "provider_session_id": "native-A-123",
            "agent_id": "hermes", "instance_id": "req-a",
        })

    def send_b():
        results["b"] = _post(live_authority, "/dispatch", {
            "shared_session_id": shared_session_id, "origin_body": "dragon_3d",
            "player_input": "hi from B", "provider_id": "claude_code",
            "model_id": "claude-x", "provider_session_id": "native-B-456",
            "agent_id": "claude_code", "instance_id": "req-b",
        })

    t_a = threading.Thread(target=send_a)
    t_b = threading.Thread(target=send_b)
    t_a.start()
    t_b.start()
    t_a.join(timeout=10)
    t_b.join(timeout=10)

    assert a_registered.is_set() and b_registered.is_set(), "synchronized interleaving never completed"
    assert results["a"][0] == 200, results["a"]
    assert results["b"][0] == 200, results["b"]
    # The actual regression proof: each dispatcher received exactly its
    # own caller's binding, never the other's, despite the Presence
    # overwrite landing squarely between A's registration and A's dispatch.
    assert received["A"] == ("hermes", "native-A-123")
    assert received["B"] == ("claude_code", "native-B-456")

Now let's run this file's tests, including the new ones:

  Ran 2 shell commands

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_presence_authority_dispatch.py)
Added 4 lines, removed 1 line
    claim (design note §6)."""
    entered = threading.Event()
    release = threading.Event()
    authority_module._PROVIDER_DISPATCHERS["hermes"] = _blocking_dispatcher("hermes", entered, release)
    # actor matches the overridden agent_id below, so step 6's (pre-
    # existing, unrelated) response-actor check passes once A resumes —
    # this test is only about the claim, not that separate gate.
    authority_module._PROVIDER_DISPATCHERS["hermes"] = _blocking_dispatcher("dragon_2d", entered, release)

    results: Dict[str, Tuple[int, Dict[str, Any]]] = {}


Now fix the race regression test's assertions to correctly account for step 6's legitimate, unrelated behavior:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_presence_authority_dispatch.py)
Added 17 lines, removed 5 lines
    t_b.join(timeout=10)

    assert a_registered.is_set() and b_registered.is_set(), "synchronized interleaving never completed"
    assert results["a"][0] == 200, results["a"]
    assert results["b"][0] == 200, results["b"]
    # The actual regression proof: each dispatcher received exactly its
    # own caller's binding, never the other's, despite the Presence
    # overwrite landing squarely between A's registration and A's dispatch.
    # The actual regression proof: each dispatcher was invoked with
    # exactly its own caller's binding, never the other's — this is
    # decided at dispatch time, before step 6 ever runs, so it holds
    # regardless of either call's eventual HTTP status.
    assert received["A"] == ("hermes", "native-A-123")
    assert received["B"] == ("claude_code", "native-B-456")
    # Downstream of that, a separate, pre-existing, correct mechanism —
    # Gate 11 / step 6, untouched by this fix — has its own, independent
    # say: both calls share one shared_session_id, and B registered after
    # A, so Presence reports B as ACTIVE by the time either response is
    # validated. B's own response is therefore accepted; A's is correctly
    # rejected as stale — not because A dispatched to the wrong native
    # session (it didn't, per the assertions above), but because a
    # *different* body now speaks for their shared shared_session_id.
    # This is the expected, documented interaction between the two gates,
    # not a defect of either.
    assert results["b"][0] == 200, results["b"]
    assert results["a"][0] == 409, results["a"]
    assert results["a"][1]["error"] == "RESPONSE_ACTOR_MISMATCH"

  Ran 2 shell commands

All 226 pass. Let's run the suite a few more times to confirm the concurrency tests are truly deterministic (not flaky):

  Ran 1 shell command

Now let's run the entire EngAIn repo's test suite (not just this subdirectory) to be thorough:

  Ran 2 shell commands

All suites clean, matching baseline exactly. Now the live proof via launch_dragon3d.sh:

  Ran 5 shell commands

Now running with the item-1 code. Let's find the window and submit "hi" through the real HUD:

  Read 1 file, ran 3 shell commands

Response landed. Let's view the screenshot to confirm the real HUD exchange:

  Read 1 file, ran 2 shell commands

● Write(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_dispatch_mutex_contention_proof.py)
Wrote 195 lines to ../../../home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tools/live_dispatch_mutex_contention_proof.py
#!/usr/bin/env python3
"""
live_dispatch_mutex_contention_proof.py - Item 1's dispatch mutex, proven
against a real, standalone presence_authority_server.py process and a real
Hermes CLI call — not the pytest fixture, not a fake dispatcher.

Starts the real server as its own subprocess (the same way
runtime_composition.py's SupervisedPresenceAuthority does), mints one real
Hermes session, then fires two concurrent real HTTP POST /dispatch
requests at the real server targeting the identical
… +186 lines

  Ran 4 shell commands

Now copying the remaining evidence and the live proof receipt:

  Ran 1 shell command

● Write(full audit/08-18-2026-item1-dispatch-mutex-implementation.md)
Wrote 181 lines to full audit/08-18-2026-item1-dispatch-mutex-implementation.md
# Item 1 Implementation: Concurrent-`/dispatch` Mutex — Receipt

Written 2026-08-18, implementing exactly the design approved in
`08-18-2026-item1-dispatch-mutex-design-analysis.md` (as amended by its
§9 correction, commit `23c6215` in this repo). This receipt covers
implementation, tests, and live proof only — the runtime code itself is
committed separately in the EngAIn repo, per instruction to keep the
implementation commit and this audit receipt distinct.

Only the approved dispatch-mutex work was implemented. Not touched:
… +171 lines

Now committing. First, the EngAIn repo (runtime implementation):

  Ran 2 shell commands

Confirmed — this is the established, tracked convention. Committing everything now:

  Committed 2142d90, ran 1 shell command

Now committing the audit receipt separately in the hermes-audit repo:

  Committed ff8d8ff, ran 1 shell command

Both commits done, unrelated pre-existing dirt in the audit repo left untouched as before. Final cleanup check:

  Ran 1 shell command

Item 1 is implemented, tested, live-proven, and committed. Summary:

Implementation (EngAIn commit 2142d90) — exactly the corrected design from 23c6215:
- SessionClaimRegistry key widened to accept (provider_id, provider_session_id); public /claim//release HTTP contract untouched
- _handle_dispatch builds ProviderSessionBinding straight from the request body, claims the composite key before touching Presence, releases in a finally, rejects contention with 409 DISPATCH_BUSY, uses a fresh UUID per request as claim owner
- handle_turn() now takes that binding as a required parameter — from_presence_record() is gone from the dispatch path entirely; Presence's two liveness/authorization checks (steps 3 and 6) are untouched
- TTL derived from each adapter's real enforced subprocess.run(timeout=...) value (90s/120s) + 15s margin, via one named constant per adapter, not a duplicated literal
- Every existing call site (2 test files, mailbox_request_handler.py, 4 live proof scripts) updated — no fallback path left reachable anywhere

Tests — 11 new (composite-key registry behavior, the full three-way key-contention matrix, fresh-claim-owner correctness, release-on-success/failure, and a deterministic event-synchronized regression test that forces the exact Presence-overwrite interleaving from the design note and proves each caller still dispatches to its own target). 5 repeated runs, no flakes.

Suites: EngAIn 226/226 (215 baseline + 11 new), engain_avatar 86/86, godot_engain_3d_avatar 260/263 (same 3 pre-existing unrelated baseline failures) — no avatar-repo code touched.

Live proof, two parts: (1) a real launch_dragon3d.sh run — "hi" through the actual ControlHUD still gets a real Hermes reply, confirming the new server-side claim doesn't disturb the existing default avatar path; (2) a new script, live_dispatch_mutex_contention_proof.py — real standalone server, real minted Hermes session, two real concurrent /dispatch calls: caller A genuinely reaches Hermes and returns; caller B is rejected with DISPATCH_BUSY before ever touching the CLI.

Runtime implementation and the audit receipt (ff8d8ff) are committed separately, as instructed. Nothing pushed — held for your review.

✻ Brewed for 28m 45s

※ recap: We've been fixing the EngAIn avatar continuity system: item 4 (Godot launch/worker startup) is done and pushed, item 1 (dispatch concurrency mutex) is implemented, tested, and committed but not yet pushed. Next: review then push item 1's commits.

❯ This is ready to push.

  The implementation matches the approved design in the places that mattered most: the mutex key is the native provider resource, the binding is immutable through the dispatch path, claim ownership is unique per request, the claim spans the whole continuity operation, and cleanup is guaranteed through `finally`. Most importantly, the deterministic Presence-overwrite regression test proves the exact race that forced the design amendment—not merely a simpler contention case.

  The live proof also answers the remaining operational concern: the new server-side protection coexists with the old avatar-side claim, so the temporary double-locking arrangement does not break the normal Dragon 3D path.

  I would have Claude push now, but remember that there are more local audit commits than just `ff8d8ff`. The item-1 design work was also intentionally held locally.

  Give him this:

  > Item 1 review is GREEN. Push the completed item-1 boundary now.
  >
  > Do not modify runtime implementation before pushing.
  >
  > EngAIn:
  >
  > * confirm branch and intended upstream;
  > * confirm `2142d90` is present;
  > * confirm working tree is clean;
  > * push normally by fast-forward only;
  > * verify `origin/main` contains `2142d90`.
  >
  > Audit repo:
  >
  > Preserve the known unrelated pre-existing dirt:
  >
  > * `claude hermes 3d.md` modified
  > * `claude hermes 3d2.md` untracked
  >
  > Do not stage, delete, move, or alter either file.
  >
  > Confirm and push the complete item-1 audit sequence, including:
  >
  > * `fef2a00` — initial item-1 design + SessionLedger-race TODO amendment
  > * `23c6215` — corrected immutable-binding design amendment
  > * `ff8d8ff` — implementation/test/live-proof receipt
  >
  > Use the existing upstream and a normal fast-forward push only. No force, amend, squash, rebase, or history rewriting.
  >
  > Verify the remote contains all three audit commits afterward.
  >
  > After both repos are remotely verified, write a new dated audit amendment marking continuation TODO item 1 CLOSED. Do not edit or rewrite the historical TODO/design documents.
  >
  > The closure receipt should name:
  >
  > * EngAIn implementation commit `2142d90`;
  > * audit design commits `fef2a00` and `23c6215`;
  > * audit proof commit `ff8d8ff`;
  > * EngAIn `226/226`;
  > * engain_avatar `86/86`;
  > * Godot 3D `260/263`, explicitly identifying the same three pre-existing unrelated baseline RED tests;
  > * composed Dragon 3D live HUD/Hermes proof;
  > * real concurrent `/dispatch` proof showing exactly one provider entry and one `DISPATCH_BUSY`;
  > * the intentionally unchanged client-side/default claim and resulting temporary double protection;
  > * the separately recorded `SessionLedger.append()` race remaining open.
  >
  > Commit and push that closure receipt separately.
  >
  > Then stop. Do not begin the SessionLedger race implementation until we review its design.

  After that, the next item should indeed be the newly discovered `SessionLedger.append()` race, ahead of restart persistence.

  And I would approach that exactly as we approached item 1: no immediate “put a lock around append.” First derive what the ledger promises. The obvious bug is duplicate `turn_id`, but the deeper question is whether the ledger contract requires an entire request/response pair to remain ordered, or merely requires each individual append to receive a unique monotonically increasing ID. Those lead to different synchronization boundaries.

  So the next design question is not yet “which lock?”

  It is:

  ```text
  What ordering guarantees does SessionLedger promise
  when multiple operations intentionally share one shared_session_id?
  ```

  Once item 1 is pushed and closed, that is where I’d go next.

  Pushed to main, ran 1 shell command

EngAIn pushed and verified. Now the audit repo:

  Pushed to main, ran 1 shell command

Both repos pushed and verified on origin/main. Unrelated pre-existing dirt untouched. Now writing the closure receipt:

● Write(full audit/08-18-2026-item1-closed.md)
Wrote 128 lines to full audit/08-18-2026-item1-closed.md
# Continuation TODO Item 1 — CLOSED

Written 2026-08-18, after both repos' item-1 commits were pushed and
remotely verified. This is a closure amendment against the original
continuation TODO (`08-17-2026-continuation-todo.md`) — that document,
and every design/proof document item 1 produced along the way, stay
exactly as written; nothing is edited or rewritten here.

## Item 1 — concurrent-`/dispatch` mutex for overridden bindings
… +119 lines

  Committed a9b016a, pushed to main, ran 1 shell command

Item 1 is fully pushed, remotely verified, and closed:

- EngAIn: 2142d90 on origin/main ✅
- hermes-audit: fef2a00 → 23c6215 → ff8d8ff → a9b016a (closure) all on origin/main ✅
- Pre-existing unrelated dirt (claude hermes 3d.md, claude hermes 3d2.md) untouched throughout, as instructed.

Stopping here per instruction — not starting the SessionLedger race work.

For when you're ready to open that design pass, the question you framed is exactly the right entry point, and it's worth flagging one thing already visible from having just read session_ledger.py closely: Turn is frozen and turn_id is currently defined as len(turns) at append time — which conflates "this turn's position in the list" with "this turn's identity" in a way that matters a lot depending on which of your two readings is correct. If the contract only needs unique, monotonically increasing per-append IDs, an atomic counter decoupled from list length would be sufficient and cheap. If it needs the stronger guarantee — that a request/response pair for one shared_session_id is never observed split across an interleaved third party's turn — that's a bigger claim about read_since/read_last's consistency, not just append's, and would push toward serializing the whole request-append→dispatch→response-append span per shared_session_id, which starts to resemble a second mutex sitting right next to item 1's rather than a narrow fix. Worth tracing read_since's actual callers (particularly step 4 of handle_turn) before deciding which of those two worlds the current code already implicitly promises.

✻ Cooked for 1m 57s

※ recap: Goal: harden EngAIn's avatar continuity system via the continuation TODO. Just pushed and closed item 1 (dispatch mutex), fully tested and live-proven. Next: design the fix for the SessionLedger turn_id race before implementing it.

❯ Yes — this is the right stopping point.

  Claude has already identified the exact fork the next design pass has to resolve:

  An atomic counter would fix only this:

  ```text
  append A -> turn_id 12
  append B -> turn_id 13
  ```

  instead of both racing on `len(turns)` and potentially minting `12`.

  But that does not answer whether this is valid:

  ```text
  A request   turn 12
  B request   turn 13
  B response  turn 14
  A response  turn 15
  ```

  If the ledger contract merely says “every append is uniquely and monotonically ordered,” that sequence may be perfectly legitimate.

  If the contract says a `handle_turn()` transaction must appear as an indivisible conversational unit, then it is wrong, and fixing `append()` alone would only hide the more important race.

  So when we open the next pass, I would have Claude trace four things before proposing code:

  ```text
  1. What does Turn.turn_id mean?
     identity?
     physical list position?
     chronological append order?
     conversational turn number?

  2. What do readers assume?
     read_since()
     read_last()
     context construction
     cursor advancement
     recap construction
     proofs / receipts / restart reconstruction

  3. What interleavings are semantically allowed?

     REQUEST A
     REQUEST B
     RESPONSE A
     RESPONSE B

     versus

     REQUEST A
     RESPONSE A
     REQUEST B
     RESPONSE B

  4. What is the smallest invariant actually required?

     A. atomic append IDs only
     B. consistent ledger reads/writes
     C. whole request→response transaction serialization
  ```

  There is another distinction worth preserving from item 1.

  The native-provider mutex protects:

  ```text
  (provider_id, provider_session_id)
  ```

  because two callers must not mutate the same external transcript concurrently.

  The ledger problem protects something keyed by:

  ```text
  shared_session_id
  ```

  Those are intentionally different resources.

  That means there are legitimate cases where provider dispatches should remain concurrent while ledger operations may still need coordination:

  ```text
  shared EngAIn session S

  A -> Hermes / session 123
  B -> Claude / session 456
  ```

  Item 1 correctly says those native calls need not block each other.

  But if the ledger contract requires request/response transaction ordering for `S`, then a second synchronization layer could still serialize their EngAIn-visible history even while the underlying providers are unrelated. That's a genuine architectural decision, not just a threading fix.

  And Claude's observation about `turn_id = len(turns)` is useful because it exposes an implicit assumption: identity and storage position currently happen to be the same thing. We should determine whether that equivalence is contractual before replacing it with a counter.

  So item 1 is done. Next time, I would start with:

  > Re-derive the semantic contract of `SessionLedger`, its readers, and `Turn.turn_id` from actual callers. Do not implement a lock or atomic counter until we know whether the required guarantee is append uniqueness or whole-turn transactional ordering.

  That's the correct next boundary.

Agreed — that's exactly the fork, and the framing is right: it's a semantic question about what SessionLedger promises before it's ever a synchronization-primitive question, same discipline that saved item 1 from shipping a mutex on the wrong key.

Confirmed state: item 1 fully closed and pushed (EngAIn 2142d90; hermes-audit fef2a00 → 23c6215 → ff8d8ff → a9b016a). No further action taken this session — stopped as instructed, nothing started on the SessionLedger race.

When you're ready to open that design pass, I'll start from your four-part trace — Turn.turn_id's actual meaning, what every reader (read_since, read_last, context construction, cursor advancement, recap construction, and the proof/receipt/restart-reconstruction call sites) currently assumes about it, which interleavings the continuity contract actually permits, and the smallest invariant that's really required — before naming a primitive. I'll also keep the shared_session_id vs. (provider_id, provider_session_id) boundary explicit throughout, since that's the one item 1 already proved matters: nothing about closing the ledger question should quietly re-serialize provider dispatches that are correctly allowed to run concurrently, and nothing about protecting the ledger should be assumed solvable by reusing item 1's mutex — it's a different resource, keyed differently, and may turn out to need a genuinely different synchronization boundary, or none at the append() level at all if the real fix belongs at the handle_turn() transaction level instead.

✻ Brewed for 30s

❯ Yes. That is the correct boundary.

  The next pass should begin with semantics, not code:

  > Re-derive `SessionLedger`’s actual contract from its implementation and every caller. Determine what `Turn.turn_id` means, what readers assume about ordering, which concurrent request/response interleavings are valid, and whether the required invariant is unique append IDs, consistent reads/writes, or whole `handle_turn()` transaction ordering. Do not propose a lock, counter, queue, or transaction primitive until that is proven.
  >
  > Keep `shared_session_id` synchronization completely separate from the already-closed `(provider_id, provider_session_id)` dispatch mutex. Do not reduce valid provider concurrency merely to make the ledger easier to reason about.
  >
  > Produce a concrete two-caller trace for every candidate semantic model and identify which existing callers would become incorrect under each model.
  >
  > Design only. No runtime changes until reviewed.

  The key question is now very precise:

  ```text
  Can EngAIn legitimately remember:

  A request
  B request
  B response
  A response

  or must it always remember:

  A request
  A response
  B request
  B response
  ```

  Everything else—atomic counter, per-session lock, transaction lock, reader snapshotting—depends on that answer.

  Item 1 is finished. This is a clean place to start the next architectural proof.

  Searched for 1 pattern, read 2 files, ran 3 shell commands

I've re-derived this from the actual contract and every real production caller (not the proof scripts, which are single-threaded inspection code and don't exercise concurrency at all). Writing this up as a design note now — no runtime changes.

  Read 1 file

● Write(full audit/08-18-2026-item2-session-ledger-semantic-derivation.md)
Wrote 282 lines to full audit/08-18-2026-item2-session-ledger-semantic-derivation.md
# Item 2 Design Analysis — What `SessionLedger` Actually Promises

Written 2026-08-18, immediately after item 1's closure. This is a
**design note only** — no runtime code is touched. Per explicit
instruction: derive `SessionLedger`'s actual semantic contract from
`SHARED_SESSION_CONTINUITY_CONTRACT_v1.md`, the implementation, and every
real caller before proposing a lock, counter, queue, or transaction
primitive. Keep `shared_session_id` synchronization (this item)
completely separate from the already-closed `(provider_id,
provider_session_id)` dispatch mutex (item 1) — nothing here may reduce
… +272 lines

  Committed 1700da2

Committed (1700da2), no runtime code touched, not pushed. Answering your question directly:

Can EngAIn legitimately remember A req / B req / B resp / A resp? Yes — and this is provable, not just architecturally plausible:

- The contract (§5/§8) promises turn_id is unique + monotonic per session_id, and explicitly declines to specify anything about concurrent-write interleaving beyond that. It does not promise request/response adjacency.
- Every real production caller of the Ledger — I found exactly five, all inside handle_turn() and its two collaborators (the proof scripts under tools/ are single-threaded, read-only, post-hoc, and don't count) — uses turn_id purely as a </> comparison key. None indexes by position, none pairs a request with its own response.
- I built the concrete interleaved trace against real code (not abstractly): with unique IDs, context = [...if t.turn_id < request_turn.turn_id] and missing = [...if t.turn_id > last_seen_turn_id] both produce correct results at every step of A-req(0), B-req(1), B-resp(2), A-resp(3)]. Nothing breaks.
- I then checked the reverse: does any existing caller, anywhere, assume or require strict transactional ordering instead? None does — enforcing it would be a new constraint nothing today asks for, and it would mean serializing the entire dispatch span per shared_session_id, silently re-eating the exact concurrency item 1 just proved correct (two different providers, one shared session, both legitimately concurrent).

So the minimal, contract-supported fix is atomic/unique/monotonic ID assignment inside append() alone — decoupled from list position (the contract never required that equivalence; today's code just happens to conflate them) — with no lock spanning handle_turn()'s provider call, and nothing shared with item 1's claim mechanism.

One thing worth flagging that the trace surfaced along the way, not asked for but material: the project's existing "a lost cursor can only cause more recap, never less" safety argument implicitly assumes trustworthy turn_id values — under the current bug, a corrupted response_turn.turn_id could push a cursor in the dangerous direction, not just the previously-accepted-safe one. That's a second, independent reason this stays ahead of restart persistence.

I also left one question explicitly open rather than deciding it: whether the product actually wants two bodies submitting genuinely simultaneous requests against one shared_session_id at all is separate from whether the Ledger must tolerate it structurally — noted, not resolved.

Ready for your review before any implementation.

✻ Brewed for 4m 48s

※ recap: We're auditing/fixing EngAIn's avatar continuity system: item 1 (dispatch mutex) is done and pushed; item 2 (SessionLedger race) has a reviewed design, no code yet. Next: get your go-ahead to implement the item 2 fix.

❯ update the todo and continue instructions

  Ran 1 shell command

● Write(full audit/08-18-2026-continuation-todo.md)
Wrote 135 lines to full audit/08-18-2026-continuation-todo.md
# Continuation TODO — 2026-08-18, Post-Item-1

Written 2026-08-18, end of the session that closed item 1 and produced
item 2's design note. This supersedes `08-17-2026-continuation-todo.md`
as the resumption pointer — read this file first, not that one; that
file and every other dated document stay exactly as written (this
project's standing discipline: amend via new documents, never rewrite
history).

## State as of this writing
… +126 lines

Now updating the persistent memory pointer to reference this new file:

  Committed 26f55f7, ran 1 shell command, recalled 1 memory, wrote 1 memory

Done. Two things updated:

1. New continuation TODO — full audit/08-18-2026-continuation-todo.md (commit 26f55f7), superseding the 08-17 version as the "read this first" resumption pointer. It records:
- Current state of all four repos, including the two intentionally-unpushed commits (engain_avatar's 1b2c111, this repo's 1700da2) and why they're held
- Item 4 and item 1 both closed, with their full commit chains
- Item 2's actual status — design done, awaiting your review before implementation, same sequence item 1 went through
- The reordered open-items list (item 2 current → item 3 restart persistence, blocked behind it → item 4 production cutover, now including whether to retire the redundant client-side claim → item 5 provider_session_ref)
- Where to look first for item 2 specifically when implementation starts

2. Persistent memory (engain-continuity-project-status.md) updated to point at the new file and reflect item 1's closure + item 2's in-progress state, so a future session picks up the right thread without re-deriving it.

Local commit state now: engain-avatar-audit HEAD 26f55f7, 2 ahead of origin/main (1700da2 item-2 design note + this update) — not pushed, per standing discipline. engain_avatar's 1b2c111 also still unpushed. Everything else is in sync with its remote. Say the word if you want either pushed.

✻ Churned for 2m 20s

※ recap: We're hardening EngAIn's shared continuity system across the avatar repos. Item 1 (dispatch mutex) is closed and pushed; item 2 (SessionLedger race) has a design ready and needs your review before I implement it.

❯ /home/mytruelove/Desktop/burdens_of_a_forgotten_past/building_the_world/markor/zw lets not forget our native language

  Read 3 files, listed 3 directories, ran 2 shell commands, wrote 2 memories

Saved. I explored building_the_world/markor/zw/ (91 files) and confirmed what's there:

ZW is your own schema-agnostic, intent-first semantic block language, designed since mid-2025 — meant to survive across AI systems/tools/runtimes without brittle rigid schemas, letting each consumer (game engine, TTS, validator, narrator) take what it understands from the same block and ignore the rest. Two spec tracks: ZW-S (soft) and ZW-H (a formal Types/Fields/Rules/Validator-Semantics spec — drafting had reached through Section 3 in the docs). Downstream of ZW is ZON (the compiled/target format — "everything depends on this"), with a ZON4D extension, feeding into a planned pipeline of Trixel Learning Loop → Empire/Memory Integration → Blender MCP Integration → AntiPython (AP) visual-learning rules — AntiPython being a related but separate game-logic/strategy engine documented in the same folder.

Two things worth flagging directly:

1. This isn't isolated from the work I've been doing this session — tier1/engainos/tests/test_trixel32d_*.py already exists in the EngAIn repo, and /mnt/data-drive/engain_avatar/addons/zwengain/ is a real, installed Godot addon (zw_engine_plugin.gd, EngAInBridge.gd, EventBus.gd, EngAInDragon.gd, SnapshotManager.gd) — ZW is already wired into the same dragon2d avatar repo. The markor/zw/ archive also has its own standalone GDScript source for a ZW runtime/plugin, which may or may not match what's actually installed in zwengain — worth diffing before trusting either as current if this resumes.
2. There's a large, mostly-separate sub-effort in zwother/ specifically about ZW-driven TTS/voice synthesis (eSpeak, Piper, VITS, Kokoro), with real Python (zw_kitten_complete.py, zw_tele.py), not just design transcripts.

I've saved this as a persistent memory (zw-native-language.md, linked from the EngAIn status memory) so it won't get lost or rediscovered from zero next time — it's noted as an active, real design archive, not scratch material. I didn't touch any files in that directory or start any implementation work — just recorded what's there. Let me know if you want me to go deeper into any specific piece of it (the ZW-H formal spec, the ZW↔ZON conversion rules, the zwengain addon vs. the archived GDScript, or the voice/TTS sub-effort).

✻ Sautéed for 3m 32s

❯ that tts was a fascinating trip.. just not on the agends.. it stems from what zw claims... anything json can do zw does better.. zw can do anything better than json can do... however onxruntime is a real blocker.. i know zw and ap and zon were wired into the files from the start.. i could never determine if zw was just a term put in or a language being used.. i think just a term used in most cases.. but i owe it to at least be a known factor otherwise it will be ignored..

  Wrote 1 memory

That's captured now — and it's an important correction to make, so thanks for pushing on it rather than letting me leave it overstated.

I've updated the memory to reflect exactly your framing, not a firmer version of it:

- The thesis ("anything JSON can do, ZW does better") is now recorded as the actual design motivation, not just "an alternative notation."
- The TTS work is flagged as explicitly off-agenda — a tangent, not something to resume unprompted — with ONNX Runtime named as the real, unresolved blocker on it.
- The core thing: I recorded your uncertainty itself as the fact to preserve, not resolved it into false confidence either way. "ZW"/"AP"/"ZON" showing up somewhere — a filename, a comment, a variable — is now flagged as unverified by default, term-not-necessarily-language, until someone actually traces it to working code. The one place I'd already concretely checked (engain_avatar/addons/zwengain/ — the files genuinely exist) I softened too: existing on disk isn't the same claim as being functionally wired in, and I hadn't verified that part.

That's the right shape for this kind of memory — visible so it doesn't get ignored, but not asserted more confidently than you yourself hold it. If a future session runs into a ZW/AP/ZON reference somewhere and it actually matters to whatever's being worked on, this will tell it to go check rather than assume either way.

✻ Brewed for 1m 4s

※ recap: Item 1's dispatch mutex is done and pushed; item 2, the SessionLedger turn_id race, has an approved design but no code yet. Next: implement item 2's fix and add its regression test.

❯ Right. That changes the hierarchy.

  ZW is the conceptual substrate, but it is not the thing to recognize by a fixed syntax. The project gives ZW its concrete shape. Once that shape is established, consistency matters; before that, there is no single canonical-looking ZW form to hunt for.

  ZON and AP matter more operationally because they are the downstream structures that actually do work. But they inherit their flexibility and semantics from ZW.

  So the safer rule going forward is:

  ZW = intent-first foundation, project-shaped
  ZON = more important compiled/operational representation
  AP = more important execution/logic layer
  Project contract = what determines the concrete ZW shape

  That also means a future audit should not ask “does this look like ZW?” It should ask “what shape did this project establish for ZW, and is this code/data adhering to that shape?”Exactly. The safe mental model is not “ZW and JSON are equivalent formats with two converters.”

  It is more like this:

  `json2zw` is a constrained import path. JSON has already imposed its limitations, so the resulting ZW is operating inside a JSON-shaped subset.

  That means this should generally be reversible:

  ```text
  JSON
    ↓ json2zw
  ZW-within-JSON-expressiveness
    ↓ zw2json
  JSON
  ```

  But native ZW can potentially escape that subset:

  ```text
  native/project-shaped ZW
    ↓
  semantics JSON cannot represent cleanly
    ↓ zw2json
  loss / flattening / approximation / failure
  ```

  So `zw2json(json2zw(X))` can reasonably aim to preserve `X`.

  But this is a much stronger and probably false requirement:

  ```text
  json2zw(zw2json(ZW_native)) == ZW_native
  ```

  because the middle JSON representation may throw away distinctions that only existed in the native ZW shape.

  That also gives the converters a useful architectural role: JSON is an interoperability boundary, not ZW’s definition.

  And it reinforces what you just clarified about project shape. Native ZW could use relationships, implicit intent, contextual structure, or project-specific constructs that do not naturally reduce to JSON’s objects/arrays/scalars/null model. Once something began as JSON, none of those extra dimensions could have existed unless they were deliberately encoded into JSON conventions first.

  So when we eventually inspect `zw2json`, I would specifically look for whether it:

  * rejects constructs it cannot faithfully express,
  * emits some explicit loss marker,
  * approximates richer ZW into JSON,
  * or silently throws information away.

  Silent loss would be the dangerous one. A converter should never make us think “round-trip proven” when the source was richer than the target. since we was on the topic.. thats it as far as i know.. not sure how important it was.. but otherwise item 2 seems to be the next move

  Wrote 1 memory

Recorded — full hierarchy now captured (ZW as project-shaped substrate with no fixed hunt-for-it syntax, ZON/AP as the operationally-important layers that inherit from it rather than define it independently, and the json2zw/zw2json asymmetry with the specific silent-loss failure mode to check for if that converter's ever actually inspected). Filed as reference for later, not flagged as active work.

Back to item 2. Before I move to implementation, worth pausing exactly where item 1 paused: you haven't yet weighed in on the design note's actual conclusion the way you scrutinized item 1's first draft (and correctly caught a real hole in it). Quick recap of where it landed, so you can push back if something's off before I touch code:

- Claim: the contract only promises turn_id is unique + monotonic per session_id — nothing about physical list position, nothing about request/response transactional adjacency (§8 of the contract says this explicitly).
- Traced all five real callers (inside handle_turn() and its two collaborators) — every one uses turn_id purely as a </> comparison key, never a list index, never a paired identifier.
- Concrete interleaved trace (A-req, B-req, B-resp, A-resp, same shared_session_id, two different native providers) against all five readers: nothing breaks, given only that IDs are unique.
- Checked the opposite: no existing caller anywhere requires strict transactional ordering instead.
- Conclusion: minimal fix is atomic/unique/monotonic ID assignment inside append() alone — no lock spanning the dispatch call, nothing shared with item 1's mutex.

That's 08-18-2026-item2-session-ledger-semantic-derivation.md, committed at 1700da2, not yet pushed.

Do you want to review/press on that conclusion first (same as item 1), or are you approving it as-is to move to implementation?

✻ Cooked for 1m 10s

※ recap: We're hardening EngAIn's shared continuity system against concurrency bugs; item 1 (dispatch mutex) is done and pushed, and I've drafted the design for item 2 (a Ledger ordering race). Next: you review that item 2 design before I implement it.

❯ I approve the semantic conclusion. I would not send the design back for another full derivation.

  The core result is sound: `SessionLedger` promises an ordered sequence of appended events, not an indivisible request→response transaction. Therefore this is valid:

  ```text
  0  A request
  1  B request
  2  B response
  3  A response
  ```

  and item 2 must not add a `shared_session_id` lock around the whole provider dispatch. That would create a contract the system does not currently have and would undo legitimate concurrency preserved by item 1.

  I have one implementation-level correction before Claude starts: don't assume the answer has to be a separate atomic counter. The proven requirement is narrower:

  ```text
  for one shared_session_id:

  determine next turn_id
  +
  construct/append that Turn

  = one atomic operation
  ```

  If the current ledger always begins empty and its stored list is contiguous, then this is actually sufficient:

  ```python
  with session_lock:
      turns = self._turns.setdefault(session_id, [])
      turn_id = len(turns)
      turn = Turn(turn_id=turn_id, ...)
      turns.append(turn)
  ```

  That fixes the actual race while preserving the current useful equivalence:

  ```text
  turn_id == append position
  ```

  The contract may not require that equivalence, but there is also no reason to deliberately destroy it yet. A new `_next_turn_id` counter creates additional state that later persistence/reconstruction would have to restore correctly.

  So I would tell Claude:

  > The semantic derivation in `1700da2` is approved.
  >
  > Proceed to implementation, with one refinement: implement the invariant, not a predetermined counter mechanism.
  >
  > The atomic boundary must include both next-ID determination and insertion of the corresponding frozen `Turn` into that `shared_session_id`'s stored sequence.
  >
  > First determine whether the current ledger can ever be initialized with pre-existing/non-contiguous turns. If not — and restart persistence/reconstruction remains deferred — prefer the smallest correct implementation. `len(turns)` is not itself wrong; the bug is the unsynchronized `len(turns) → append()` sequence.
  >
  > Do not add a separate next-ID counter merely because the contract does not require `turn_id == list position`.
  >
  > Use synchronization local to each `shared_session_id` so unrelated shared sessions remain concurrent.
  >
  > Do not lock the provider call or the complete `handle_turn()`.
  >
  > Preserve the valid:
  >
  > ```
  > A request
  > B request
  > B response
  > A response
  > ```
  >
  > interleaving.
  >
  > Add deterministic concurrency tests proving:
  >
  > * concurrent appends to one session produce unique IDs;
  > * IDs monotonically match stored append order;
  > * with an initially empty ledger they remain contiguous `0..N-1`;
  > * independent `shared_session_id`s do not unnecessarily contend;
  > * the valid request/request/response/response interleaving still works through all existing readers;
  > * `read_since`, context `< request_turn.turn_id`, and cursor `> last_seen_turn_id` semantics remain unchanged;
  > * item 1's different-provider concurrency remains intact.
  >
  > Also check whether any actual ZON/AP/ZW-connected runtime path consumes `Turn.turn_id` or ledger ordering. If one does, verify compatibility against its established project-specific shape. Do not retrofit ZW/ZON/AP into this item merely because they exist elsewhere.
  >
  > Run the complete affected suites and an integration smoke test, commit implementation and audit receipt separately, and stop before restart persistence. Do not push until review.

  There is one other thing I would explicitly not solve here: reader snapshot consistency.

  If `read_since()` runs concurrently with an append, it might observe the ledger immediately before or immediately after that append. Given the contract Claude just derived and the monotonic filters used by the readers, either can be valid. Unless a caller was found requiring a transactional snapshot, adding read locks would again strengthen the contract without evidence.

  So: semantic design **approved**. Proceed with the narrow append atomicity fix.

  Ran 1 shell command

Verified: SessionLedger() is always constructed empty everywhere, _turns has no write path besides append(), and no ZON/AP/Trixel code touches SessionLedger/Turn at all — confirmed via grep, zero cross-subsystem consumers. len(turns) is safe to keep. Implementing now:

  Read 1 file

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/core/session_ledger.py)
Added 25 lines
mutating a snapshot dict passed into append() after the call returns) would
silently rewrite the Ledger's history with no new turn ever recorded —
exactly what "append-only" is supposed to forbid.

Concurrency (item 2, 2026-08-18 — see
08-18-2026-item2-session-ledger-semantic-derivation.md for the full
derivation): append()'s own turn_id assignment (`len(turns)`) and the
list insertion used to race — two threads appending to the SAME
session_id could read the same length before either inserted, minting a
duplicate turn_id. The contract (§8) only promises turn_id is unique and
monotonic per session_id; it does not require turn_id to equal list
position, but there's also no reason to give that useful, currently-true
equivalence up prematurely (a future persistence/reconstruction layer
would otherwise have to restore it separately). Fixed by making
"determine next turn_id + insert the Turn" one atomic operation per
session_id, via a lock scoped to that session_id alone — a session_id A
append never waits on a session_id B append. Reads (read_since/
read_last) are deliberately NOT locked: no caller was found that needs a
transactional snapshot across a concurrent append, and Python's own
list/GIL semantics already prevent a torn read of already-inserted
elements — adding read locks would strengthen the contract beyond what
any caller requires. This also does not extend to locking the
request/response transaction handle_turn() performs around a real
provider dispatch — see the design note for why that would silently
reintroduce a serialization guarantee the system doesn't have today and
would cost item 1's already-proven provider-dispatch concurrency for no
discovered benefit.
"""

from __future__ import annotations

import threading
import time
from copy import deepcopy
from dataclasses import dataclass, field

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/core/session_ledger.py)
Added 33 lines, removed 11 lines
class SessionLedger:
    def __init__(self) -> None:
        self._turns: Dict[str, List[Turn]] = {}
        # One lock per session_id, created lazily. _locks_guard protects
        # only the get-or-create of that per-session lock itself (a
        # handful of dict operations) — never the append work — so two
        # different session_ids' appends never wait on each other.
        self._locks: Dict[str, threading.Lock] = {}
        self._locks_guard = threading.Lock()

    def _lock_for(self, session_id: str) -> threading.Lock:
        with self._locks_guard:
            lock = self._locks.get(session_id)
            if lock is None:
                lock = threading.Lock()
                self._locks[session_id] = lock
            return lock

    def append(
        self,
        session_id: str,

    ) -> Turn:
        if direction not in ("request", "response"):
            raise ValueError(f"MALFORMED_TURN: direction must be request/response, got {direction!r}")
        turns = self._turns.setdefault(session_id, [])
        turn = Turn(
            turn_id=len(turns),
            session_id=session_id,
            origin_body=origin_body,
            direction=direction,
            actor=actor,
            payload=payload,
            snapshot=deepcopy(snapshot),
        )
        turns.append(turn)
        # The atomic boundary: determine this session_id's next turn_id
        # and insert the corresponding Turn as one operation. len(turns)
        # is not itself wrong — every SessionLedger starts empty and has
        # no path that loads pre-existing/non-contiguous turns (verified
        # against every real construction site; restart persistence
        # remains deferred) — the bug was the unsynchronized
        # len(turns) -> append() sequence, not this formula.
        with self._lock_for(session_id):
            turns = self._turns.setdefault(session_id, [])
            turn = Turn(
                turn_id=len(turns),
                session_id=session_id,
                origin_body=origin_body,
                direction=direction,
                actor=actor,
                payload=payload,
                snapshot=deepcopy(snapshot),
            )
            turns.append(turn)
        return deepcopy(turn)

    def read_last(self, session_id: str, direction: Optional[str] = None) -> Optional[Turn]:

  Ran 1 shell command

All 226 still pass. Now let's check if a test_session_ledger.py exists to add tests there, or if I need a new file:

  Searched for 1 pattern

Now writing the new tests. First, test_session_ledger.py:

● Write(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_session_ledger.py)
Wrote 120 lines to ../../../home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_session_ledger.py
"""
Item 2 (2026-08-18) — SessionLedger.append()'s turn_id atomicity, proven
with real threads, not simulated. See
08-18-2026-item2-session-ledger-semantic-derivation.md for the design
this implements: the required invariant is atomic/unique/monotonic
per-session_id turn_id assignment, nothing stronger — no lock spans a
provider dispatch, and unrelated session_ids must never contend.
"""

from __future__ import annotations
… +110 lines

Now the interleaving-through-readers test in test_continuity_identity_boundary.py:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_continuity_identity_boundary.py)
Added 1 line
    ResponseActorMismatch,
    SharedSessionBridge,
)
from tier1.engainos.core.continuity_context_builder import ContinuityContextBuilder
from tier1.engainos.core.continuity_cursor_tracker import ContinuityCursorTracker
from tier1.engainos.core.presence_registry import PresenceRegistry
from tier1.engainos.core.provider_session_binding import ProviderSessionBinding

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_continuity_identity_boundary.py)
Added 1 line
        bridge.handle_turn(SESSION_ID, "dragon_2d", "hello",
                            binding=_binding("hermes", "flaky-session", "hermes", "H-1"))

    _placeholder_marker_for_insert_point = None  # noqa: unused, replaced below
    assert cursor.last_seen_turn_id("hermes", "flaky-session") == -1

    # A subsequent successful call to the same native session must still

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_continuity_identity_boundary.py)
Removed 1 line
        bridge.handle_turn(SESSION_ID, "dragon_2d", "hello",
                            binding=_binding("hermes", "flaky-session", "hermes", "H-1"))

    _placeholder_marker_for_insert_point = None  # noqa: unused, replaced below
    assert cursor.last_seen_turn_id("hermes", "flaky-session") == -1

    # A subsequent successful call to the same native session must still

Reverted. Now appending the new test at the end of the file properly:

  Read 1 file

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_continuity_identity_boundary.py)
Added 63 lines
    bridge2.handle_turn(SESSION_ID, "dragon_2d", "are you there now?",
                         binding=_binding("hermes", "flaky-session", "hermes", "H-1-b"))


def test_valid_request_request_response_response_interleaving_through_all_readers():
    """Item 2's approved semantic conclusion, proven directly against the
    real Ledger and the real reader logic (context filter, recap
    builder, cursor) — not merely append() atomicity in isolation, and
    deliberately not routed through two full handle_turn() calls, since
    that would entangle this with Gate 11's own, separately-tested,
    orthogonal response-actor authorization (see item 1's own regression
    test for that interaction) — this test is scoped to item 2's actual
    claim: SessionLedger promises an ordered sequence of appended events,
    not an indivisible request->response transaction, so
    A-req/B-req/B-resp/A-resp is valid for one shared_session_id.

    The interleaving here is a Ledger-ordering property, not a
    wall-clock one, so it's reproduced deterministically by direct,
    single-threaded sequencing of the exact same primitives handle_turn()
    itself calls in the exact order a real interleaving would produce —
    no threads or timing needed for this part; real-thread coverage of
    concurrent Ledger writes lives in test_session_ledger.py, and
    real-thread coverage of concurrent dispatch lives in
    test_presence_authority_dispatch.py."""
    ledger = SessionLedger()
    cursor = ContinuityCursorTracker()
    builder = ContinuityContextBuilder()

    a_req = ledger.append(SESSION_ID, "dragon_2d", "request", "player", "A says hi")
    b_req = ledger.append(SESSION_ID, "dragon_3d", "request", "player", "B says hi")
    assert (a_req.turn_id, b_req.turn_id) == (0, 1)

    # step 4, as handle_turn() itself computes it: everything strictly
    # before this call's own just-appended request.
    a_context = [t for t in ledger.read_since(SESSION_ID, since_turn_id=-1) if t.turn_id < a_req.turn_id]
    b_context = [t for t in ledger.read_since(SESSION_ID, since_turn_id=-1) if t.turn_id < b_req.turn_id]
    assert a_context == [], "B's concurrent request must not appear as prior context for A"
    assert [t.turn_id for t in b_context] == [0], "A's earlier request IS legitimate prior context for B"

    # B's real dispatch completes first.
    b_dispatch_input = builder.build(b_context, "B says hi", cursor.last_seen_turn_id("claude_code", "native-B
"))
    assert b_dispatch_input == "B says hi"
    b_resp = ledger.append(SESSION_ID, "dragon_3d", "response", "claude_code", "B-ack")
    cursor.advance("claude_code", "native-B", b_resp.turn_id)

    # A's real dispatch — built from a_context, computed BEFORE B's
    # request/response existed — finally completes.
    a_dispatch_input = builder.build(a_context, "A says hi", cursor.last_seen_turn_id("hermes", "native-A"))
    assert a_dispatch_input == "A says hi", "A's own recap must never see B's exchange — it didn't exist when
A's context was read"
    a_resp = ledger.append(SESSION_ID, "dragon_2d", "response", "hermes", "A-ack")
    cursor.advance("hermes", "native-A", a_resp.turn_id)

    all_turns = ledger.read_since(SESSION_ID, since_turn_id=-1)
    assert [(t.turn_id, t.direction, t.origin_body) for t in all_turns] == [
        (0, "request", "dragon_2d"),
        (1, "request", "dragon_3d"),
        (2, "response", "dragon_3d"),
        (3, "response", "dragon_2d"),
    ], "A-req, B-req, B-resp, A-resp must be preserved exactly as it happened"

    # READ_LAST's own contract definition of recency (§6): the single
    # most recent matching turn, regardless of door — here, correctly,
    # A's response, even though B's whole exchange both started and
    # finished first.
    assert ledger.read_last(SESSION_ID, direction="response").origin_body == "dragon_2d"

    assert "hello" in calls[0]

Now the "Ledger lock does not serialize behind a slow concurrent dispatch" test in test_presence_authority_dispatch.py:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_presence_authority_dispatch.py)
Added 42 lines
    # regardless of either call's eventual HTTP status.
    assert received["A"] == ("hermes", "native-A-123")
    assert received["B"] == ("claude_code", "native-B-456")


def test_ledger_lock_does_not_serialize_behind_a_slow_concurrent_dispatch(live_authority):
    """Item 2's per-shared_session_id Ledger lock (SessionLedger.append())
    must never be held across a provider call — it's scoped tightly
    around turn_id assignment + insertion alone. Proves it against the
    real, running server: while caller A's real dispatch is blocked in
    flight (holding item 1's claim on its own native session), caller B
    — a DIFFERENT (provider_id, provider_session_id), same
    shared_session_id — must be able to append its request, dispatch,
    and append its response, all while A is still blocked. If the Ledger
    lock had accidentally grown to span handle_turn()'s dispatch call,
    B would hang here until A's release fires."""
    entered = threading.Event()
    release = threading.Event()
    authority_module._PROVIDER_DISPATCHERS["hermes"] = _blocking_dispatcher("hermes", entered, release)
    authority_module._PROVIDER_DISPATCHERS["claude_code"] = _fake_dispatcher("claude_code")

    shared_session_id = "shared-ledger-lock-no-serialize"
    results: Dict[str, Tuple[int, Dict[str, Any]]] = {}

    def send_a():
        results["a"] = _post(live_authority, "/dispatch", {
            "shared_session_id": shared_session_id, "origin_body": "dragon_2d",
            "player_input": "from A", "provider_id": "hermes",
            "model_id": "gpt-5.6-sol", "provider_session_id": "native-A",
        })

    t = threading.Thread(target=send_a)
    t.start()
    assert entered.wait(timeout=5), "A never entered its blocking dispatch"

    status_b, resp_b = _post(live_authority, "/dispatch", {
        "shared_session_id": shared_session_id, "origin_body": "dragon_3d",
        "player_input": "from B", "provider_id": "claude_code",
        "model_id": "claude-x", "provider_session_id": "native-B",
    })
    assert status_b == 200, resp_b

    release.set()
    t.join(timeout=5)
    assert results["a"][0] == 200, results["a"]
    # Downstream of that, a separate, pre-existing, correct mechanism —
    # Gate 11 / step 6, untouched by this fix — has its own, independent
    # say: both calls share one shared_session_id, and B registered after

Now let's run everything:

  Ran 1 shell command

Two test-authoring mistakes of mine, not implementation bugs. Let me fix both.

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_continuity_identity_boundary.py)
Added 5 lines, removed 2 lines
    assert a_context == [], "B's concurrent request must not appear as prior context for A"
    assert [t.turn_id for t in b_context] == [0], "A's earlier request IS legitimate prior context for B"

    # B's real dispatch completes first.
    # B's real dispatch completes first. native-B has never seen anything
    # (last_seen_turn_id=-1), so A's earlier request — legitimate prior
    # context per b_context above — correctly gets recapped to B.
    b_dispatch_input = builder.build(b_context, "B says hi", cursor.last_seen_turn_id("claude_code", "native-B
"))
    assert b_dispatch_input == "B says hi"
    assert "A says hi" in b_dispatch_input
    assert "Now: B says hi" in b_dispatch_input
    b_resp = ledger.append(SESSION_ID, "dragon_3d", "response", "claude_code", "B-ack")
    cursor.advance("claude_code", "native-B", b_resp.turn_id)


Now the second test — same expected Gate 11 interaction already documented in item 1's own regression test:

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_presence_authority_dispatch.py)
Added 13 lines, removed 1 line
        "player_input": "from B", "provider_id": "claude_code",
        "model_id": "claude-x", "provider_session_id": "native-B",
    })
    # The actual proof: B completed (didn't hang behind A's still-open
    # dispatch) — status alone would be ambiguous if this line had
    # blocked for seconds instead of returning immediately, so what
    # matters here is that execution reached this point at all while A
    # is still inside its blocking dispatcher.
    assert status_b == 200, resp_b

    release.set()
    t.join(timeout=5)
    assert results["a"][0] == 200, results["a"]
    assert "a" in results, "A's call never returned — release() failed to unblock it"
    # A's own status is governed by the same pre-existing, unrelated
    # Gate 11 (response-actor authorization) item 1's own regression test
    # already documents: both calls share one shared_session_id, and B
    # registered Presence more recently, so A's response is correctly
    # rejected as stale — not because of any Ledger-lock serialization
    # (which is what this test actually checks, via B's timing above).
    assert results["a"][0] in (200, 409), results["a"]
    # Downstream of that, a separate, pre-existing, correct mechanism —
    # Gate 11 / step 6, untouched by this fix — has its own, independent
    # say: both calls share one shared_session_id, and B registered after

  Read 1 file, ran 2 shell commands

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_presence_authority_dispatch.py)
Removed 13 lines
    # rejected as stale — not because of any Ledger-lock serialization
    # (which is what this test actually checks, via B's timing above).
    assert results["a"][0] in (200, 409), results["a"]
    # Downstream of that, a separate, pre-existing, correct mechanism —
    # Gate 11 / step 6, untouched by this fix — has its own, independent
    # say: both calls share one shared_session_id, and B registered after
    # A, so Presence reports B as ACTIVE by the time either response is
    # validated. B's own response is therefore accepted; A's is correctly
    # rejected as stale — not because A dispatched to the wrong native
    # session (it didn't, per the assertions above), but because a
    # *different* body now speaks for their shared shared_session_id.
    # This is the expected, documented interaction between the two gates,
    # not a defect of either.
    assert results["b"][0] == 200, results["b"]
    assert results["a"][0] == 409, results["a"]
    assert results["a"][1]["error"] == "RESPONSE_ACTOR_MISMATCH"

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_presence_authority_dispatch.py)
Added 9 lines, removed 5 lines
    assert "a" in results, "A's call never returned — release() failed to unblock it"
    # A's own status is governed by the same pre-existing, unrelated
    # Gate 11 (response-actor authorization) item 1's own regression test
    # already documents: both calls share one shared_session_id, and B
    # registered Presence more recently, so A's response is correctly
    # rejected as stale — not because of any Ledger-lock serialization
    # (which is what this test actually checks, via B's timing above).
    assert results["a"][0] in (200, 409), results["a"]
    # already documents: both calls share one shared_session_id, and B's
    # registration (which could only happen after A's, since B's request
    # was sent only after A confirmed it had already entered its blocking
    # dispatch) means Presence reports "claude_code" ACTIVE by the time
    # A's own response is validated — deterministically rejected as
    # stale. Not a defect, and not what this test is checking — that's
    # B's timing above, which is the actual proof.
    assert results["a"][0] == 409, results["a"]
    assert results["a"][1]["error"] == "RESPONSE_ACTOR_MISMATCH"

  Read 1 file, ran 2 shell commands

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_continuity_identity_boundary.py)
Added 1 line
    bridge2 = SharedSessionBridge(presence, ledger, _recording_dispatcher("hermes", calls), continuity_cursor_
tracker=cursor)
    bridge2.handle_turn(SESSION_ID, "dragon_2d", "are you there now?",
                         binding=_binding("hermes", "flaky-session", "hermes", "H-1-b"))
    assert "hello" in calls[0]


def test_valid_request_request_response_response_interleaving_through_all_readers():

● Update(~/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/tests/test_continuity_identity_boundary.py)
Removed 2 lines
    # A's response, even though B's whole exchange both started and
    # finished first.
    assert ledger.read_last(SESSION_ID, direction="response").origin_body == "dragon_2d"

    assert "hello" in calls[0]

Now let's run the full suite again:

  Ran 2 shell commands

Deterministic across 5 runs. Now the avatar repos' offline suites (no code touched there, but confirming no regression) and a live composed integration smoke test:

  Ran 3 shell commands

Clean. Now the audit receipt:

  Ran 1 shell command

● Write(full audit/08-18-2026-item2-session-ledger-implementation.md)
Wrote 123 lines to full audit/08-18-2026-item2-session-ledger-implementation.md
# Item 2 Implementation: `SessionLedger.append()` Atomicity — Receipt

Written 2026-08-18, implementing the semantic conclusion approved in
`08-18-2026-item2-session-ledger-semantic-derivation.md` (commit
`1700da2`), with one implementation-level refinement from review: the
proven requirement is atomicity of "determine next `turn_id` + insert
that `Turn`," not necessarily a separate counter mechanism. Stops here,
as instructed — restart persistence not started.

## What changed
… +113 lines

Now committing — EngAIn (runtime) first:

  Committed dea55c0, ran 2 shell commands

Now the audit receipt, separately:

  Committed b74f730, ran 1 shell command

Both committed, unrelated dirt untouched, nothing pushed. Item 2 is implemented and stopped exactly where instructed.

Summary:

- session_ledger.py: one threading.Lock per session_id, created lazily; append()'s body (turn_id=len(turns) through turns.append(turn)) is the atomic critical section. len(turns) kept as-is — verified (not assumed) that every SessionLedger() construction site starts empty and _turns has no write path besides append() itself. No separate counter added, per your refinement.
- Reads (read_since/read_last) left unlocked — no caller found that needs a transactional snapshot, so no new guarantee added beyond what was proven necessary.
- Verified zero cross-subsystem ZON/AP/Trixel consumers of turn_id/SessionLedger — nothing to retrofit.
- 6 new tests, all real-thread or real-HTTP, no sleep-based timing: unique/contiguous IDs under concurrent same-session appends, append-order-matches-turn_id, a 10-session/200-thread sanity sweep, a direct proof independent sessions don't contend, the approved A-req/B-req/B-resp/A-resp interleaving traced directly against the real Ledger/context-builder/cursor, and a real-HTTP proof the new lock never spans a provider dispatch (B completes fully while A sits blocked mid-dispatch holding item 1's claim).
- Suites: EngAIn 232/232 (226 + 6 new), engain_avatar 86/86, godot_engain_3d_avatar 260/263 (same 3 pre-existing unrelated failures) — 5 repeated runs, no flakes.
- Integration smoke test: re-ran item 1's own live proof script unmodified against a real Hermes call — unchanged pass, confirms the new lock and item 1's mutex coexist correctly under real concurrent load.

Two things worth noting from the process: I made two test-authoring mistakes along the way (a wrong expectation about B's recap content, and a botched edit that orphaned a line from an adjacent test) — both caught by the suite failing, both fixed, neither was an implementation bug.

Commits: EngAIn dea55c0, audit receipt b74f730. Both held, not pushed, per standing discipline — say the word when you want them pushed.

✻ Worked for 16m 1s

※ recap: Building EngAIn's shared-continuity system across avatar repos; just finished item 2 (SessionLedger fix), tested and committed locally but not pushed. Next: get your go-ahead to push item 2, then move to item 3.

❯ Push item 2 now. The implementation is narrow, matches the derived contract, and the tests specifically prove it did not accidentally serialize provider work.

  Have Claude do this:

  > Item 2 review is GREEN. Push and close the completed item-2 boundary.
  >
  > EngAIn:
  >
  > * Confirm branch/upstream.
  > * Confirm `dea55c0` is present.
  > * Confirm working tree is clean.
  > * Push normally, fast-forward only.
  > * Verify `origin/main` contains `dea55c0`.
  >
  > Audit repo:
  >
  > * Preserve the known unrelated dirt exactly as-is. Do not stage, modify, delete, move, or clean it.
  > * Confirm the complete item-2 audit sequence is present:
  >
  >   * `1700da2` — SessionLedger semantic derivation/design
  >   * `b74f730` — implementation/test/live-proof receipt
  > * Push normally, fast-forward only.
  > * Verify both commits are on `origin/main`.
  >
  > Then write a new dated closure receipt for item 2 rather than editing the historical TODO/design files.
  >
  > Record:
  >
  > * EngAIn implementation `dea55c0`
  > * design `1700da2`
  > * proof receipt `b74f730`
  > * `232/232` EngAIn
  > * `86/86` engain_avatar
  > * `260/263` Godot 3D with the same three pre-existing unrelated RED failures
  > * per-`shared_session_id` append atomicity only
  > * `turn_id = len(turns)` intentionally preserved inside that atomic section
  > * no reader locking added
  > * no whole-`handle_turn()` serialization added
  > * valid `A-request / B-request / B-response / A-response` history preserved
  > * item 1 provider concurrency semantics preserved
  > * unmodified real-Hermes item-1 proof still GREEN
  > * no active ZW/ZON/AP consumer of `SessionLedger.turn_id` found in the inspected runtime path
  >
  > Commit and push the closure receipt separately.
  >
  > After remote verification, mark item 2 CLOSED.
  >
  > Then item 3 is the former restart-persistence/cursor-reconstruction problem. Start **design/re-derivation only**. Do not implement persistence yet.

  For item 3, I would change the opening question slightly because of what we learned about native language.

  Don't start with “how do we persist the Python ledger?” Start with:

  ```text
  After an EngAIn restart, what continuity state is actually lost,
  which of it can already be reconstructed from native/provider state
  or receipts, and which state genuinely requires EngAIn persistence?
  ```

  Then separately identify:

  ```text
  SessionLedger
  ContinuityCursorTracker
  shared_session_id relationships
  provider-session bindings
  native provider transcript/state
  ZW/ZON/AP representations, where actually active
  existing receipts/transcripts on disk
  ```

  That matters because the original TODO was written when “ledger/cursor persistence” sounded like one obvious missing feature. We already discovered that dispatched recap can become permanent native-side state. Item 3 should therefore be re-derived rather than blindly persisting every Python object.

  So: **push and close item 2; then open item 3 as a design investigation only.**

  Ran 1 shell command

Confirmed clean, dea55c0 at HEAD, 0 behind / 1 ahead. Pushing:

  Pushed to main

EngAIn pushed and verified. Now the audit repo:

  Ran 1 shell command

Confirmed — only the known pre-existing dirt, 1700da2, 26f55f7, b74f730 present in order, 0 behind / 3 ahead. Pushing:

  Pushed to main

Both repos pushed and remotely verified. Now the closure receipt:

● Write(full audit/08-19-2026-item2-closed.md)
Wrote 121 lines to full audit/08-19-2026-item2-closed.md
# Continuation TODO Item 2 — CLOSED

Written 2026-08-19, after both repos' item-2 commits were pushed and
remotely verified. This is a closure amendment against the continuation
TODO (`08-18-2026-continuation-todo.md`) and item 2's own design/proof
documents — none of those are edited or rewritten here.

## Item 2 — `SessionLedger.append()` `turn_id` race

> "Two dispatches sharing an EngAIn session but targeting different
… +111 lines

  Committed cf3ec1f, pushed to main, read 1 file, ran 2 shell commands

Item 2 fully closed and pushed. Now opening item 3 — re-derivation only, per your reframing. Let me trace what's actually persisted vs. lost before writing anything up.

  Ran 2 shell commands

● Write(full audit/08-19-2026-item3-restart-continuity-derivation.md)
Wrote 197 lines to full audit/08-19-2026-item3-restart-continuity-derivation.md
# Item 3 Design Investigation — What Restart Continuity Actually Requires

Written 2026-08-19. **Design/re-derivation only — no runtime code
touched, no persistence implemented.** Per explicit instruction: the
original TODO framing ("ledger/cursor persistence across a restart")
was written before this session discovered that a dispatched recap
becomes permanent native-side state regardless of what EngAIn's own
process does — persisting every Python object without accounting for
that would solve the wrong problem. Re-opening the question rather than
carrying the old framing forward:
… +188 lines

Committing (design only, no runtime code touched, not pushed per standing pattern until reviewed):

  Committed 3d9de10

Item 2 pushed, verified, closed. EngAIn dea55c0 on origin/main; hermes-audit 1700da2 → b74f730 → cf3ec1f (closure) all on origin/main. Unrelated dirt untouched throughout.

Item 3 — re-derivation done, committed (3d9de10), not pushed. Traced every component with your reframed question, confirmed by grep, not assumed:

- The whole authority is 100% in-memory today — zero disk I/O anywhere in presence_authority_server.py or its four core modules.
- The real finding: same-native-provider conversational continuity already survives an EngAIn restart with zero EngAIn-side persistence, because each vendor (Hermes/Claude Code) keeps its own durable transcript outside EngAIn's process entirely — --resume picks it back up regardless of what EngAIn's process did. The genuine, narrower loss is specifically cross-provider catch-up of pre-restart history — a provider not already active before the restart gets no recap of anything from before EngAIn came back up, because the Ledger it would recap from is empty.
- ContinuityCursorTracker loses state too, but consistently with the Ledger (both reset together, no new inconsistency on their own) — named the constraint that any future fix must treat them as one pair, never persisted independently.
- shared_session_id turned out to not be EngAIn's state at all — it's supplied fresh on every single /dispatch call from the caller's own environment. Nothing to lose there.
- Checked the avatar-side .godot/engain_hermes_session.json precisely — it's five identity fields plus a capped replay-protection list, explicitly not a continuity store, worth being clear it's not partial persistence already in place.
- ZW/ZON/AP: re-confirmed zero active consumers, specifically in this context.
- Existing receipts/mailbox files: real, but fixed-path-overwritten proof artifacts or actively-consumed transient files — not a viable reconstruction source.

Left the actual product call open rather than deciding it myself: whether that narrower cross-provider-catch-up gap is worth building persistence for, or worth just documenting as an accepted limitation the same way Presence/claim ephemerality already is. If it's worth building, the note scopes it to Ledger+Cursor as one pair and names one alternative direction (asking the native transcript itself for a summary on reconnect) as considered but blocked on no adapter exposing read-back today — not designed, just flagged.

Ready for your review before anything gets implemented.

✻ Worked for 5m 12s

※ recap: Building EngAIn's continuity system across the audit and code repos; items 1 (dispatch mutex) and 2 (ledger race) are closed and pushed. Just finished a design-only look at item 3 (restart persistence) and it's waiting on your call: build it or document it as an accepted limitation.

❯ I would not accept the cross-provider catch-up gap as a permanent limitation. For EngAIn, that gap cuts directly across the shared-continuity promise.

  The re-derivation is good because it shrank item 3 dramatically: native provider continuity is already durable on the provider side, `shared_session_id` is caller-supplied, Presence/claims are legitimately ephemeral, and the actual loss is EngAIn’s ability to tell a provider what happened elsewhere before the restart.

  So the product decision is: **build persistence, but only for EngAIn-owned cross-provider continuity state.**

  I would not implement yet, though. There is one more design pass I want first, because “persist Ledger + Cursor together” still leaves a crash-consistency question.

  The dangerous implementation would be something like:

  ```text
  write ledger.json
  write cursor.json
  ```

  or even two database records updated separately.

  A crash between those writes could restore:

  ```text
  Ledger = includes turn 42
  Cursor = says provider already saw through 42
  ```

  when it actually did not, or the reverse. One direction causes duplicate recap; the other can cause missing recap. That is exactly the kind of persistence bug that only appears after we congratulate ourselves for making things durable.

  I would give Claude this:

  > Item 3 product decision: the cross-provider restart gap is NOT accepted as a permanent limitation. EngAIn should preserve enough continuity state across its own restart that a provider joining/rejoining afterward can still receive the pre-restart shared-session history it has not already seen.
  >
  > Do not implement persistence yet.
  >
  > Amend the design by deriving the crash-consistency model for `SessionLedger` + `ContinuityCursorTracker`.
  >
  > The persistence design must guarantee that restart cannot reconstruct a logically impossible combination of:
  >
  > * durable shared-session turns;
  > * per-`(provider_id, provider_session_id)` last-seen cursor state.
  >
  > Analyze these failure windows explicitly:
  >
  > 1. crash after a request turn is durably recorded but before provider dispatch;
  > 2. crash after provider returns but before the response turn is durably recorded;
  > 3. crash after response turn persistence but before cursor advance persistence;
  > 4. crash after cursor advance is persisted but before any associated continuity receipt/state is durable;
  > 5. process kill during persistence itself;
  > 6. restart with a partially written/corrupt tail.
  >
  > For each case, state what the reconstructed Ledger and Cursor are allowed to say and whether the consequence is:
  >
  > * safe duplicate recap,
  > * missing recap,
  > * duplicate native provider invocation,
  > * orphan request,
  > * orphan response,
  > * or unrecoverable corruption.
  >
  > Prefer a design where Ledger and Cursor are reconstructed from one durable ordering source rather than maintaining two independently authoritative persistence files if that is compatible with the existing contracts.
  >
  > In particular, evaluate whether the durable form should be an append-only continuity journal containing events such as:
  >
  > ```
  > TURN_APPENDED
  > CURSOR_ADVANCED
  > ```
  >
  > or an equivalent single-transaction representation, so startup replay reconstructs both in-memory objects from one ordered source.
  >
  > Do not select SQLite, JSON, ZW, ZON, or any other encoding/storage mechanism yet merely because it is convenient. First establish the semantic record that must survive.
  >
  > Then inspect the project's established ZW/ZON/AP material for this specific persistence role. ZW is the project-shaped semantic substrate; ZON/AP are operationally more important downstream. If an established project-specific shape already fits a continuity journal, report it. If not, do not invent a fake “ZW persistence format” just to claim native-language compliance.
  >
  > Also determine the durability point of `/dispatch`.
  >
  > Specifically answer:
  >
  > ```
  > At what exact moment may EngAIn truthfully consider
  > a request turn, response turn, and cursor advance committed?
  > ```
  >
  > The HTTP response must not claim a state is durable if it exists only in RAM and would disappear on an immediate process kill.
  >
  > Keep these explicitly out of scope:
  >
  > * persisting PresenceRegistry;
  > * persisting SessionClaimRegistry;
  > * persisting `shared_session_id` ownership;
  > * copying native Hermes/Claude transcripts into EngAIn;
  > * production cutover;
  > * ZW/ZON/AP redesign.
  >
  > Finally, determine retention/recovery scope:
  >
  > * one journal per `shared_session_id` or one global journal;
  > * ordering requirements across different shared sessions;
  > * whether old turns can ever be compacted safely;
  > * what evidence allows a cursor/history record to be discarded;
  > * how startup distinguishes a clean tail from corruption.
  >
  > Design only. Commit the amendment separately and stop for review.

  My bias is toward a single durable event stream per shared session, or some storage mechanism with equivalent transactional guarantees.

  Conceptually:

  ```text
  shared_session S
  │
  ├── turn 0 request
  ├── turn 1 response
  ├── cursor Hermes/X -> 1
  ├── turn 2 request
  ├── turn 3 response
  ├── cursor Claude/Y -> 3
  └── ...
  ```

  Then after restart:

  ```text
  durable journal
        ↓ replay
  SessionLedger
  +
  ContinuityCursorTracker
  ```

  That is cleaner than making two persistence systems and trying to keep them synchronized forever.

  One subtlety: the cursor event should mean “EngAIn has sufficient evidence this native provider has incorporated history through turn N,” not merely “we attempted to send it.” That distinction matters if the process dies while the provider invocation is in flight.

  And this is where the native-language work should become a known factor without hijacking the task. We should inspect whether this continuity journal already has a natural project-specific ZW/ZON shape. We should not automatically dump it to JSON simply because Python makes that easy, but we also should not fabricate a ZW form that the project never established.

  So my review is:

  **Re-derivation: approved.**
  **Product decision: persistence is worth building.**
  **Implementation: not yet. One crash-consistency/durable-record design pass first.**

● Write(full audit/08-19-2026-item3-crash-consistency-design.md)
Wrote 226 lines to full audit/08-19-2026-item3-crash-consistency-design.md
# Item 3 Amendment — Crash-Consistency Model for `SessionLedger` + `ContinuityCursorTracker` Persistence

Written 2026-08-19, after the product decision on
`08-19-2026-item3-restart-continuity-derivation.md`: the cross-provider
restart gap is **not** accepted as a permanent limitation; persistence
is worth building, scoped to EngAIn-owned continuity state only. This
document is the required crash-consistency design pass before any of
that gets implemented. **Design only — no runtime code, no encoding
selected.**
… +242 lines

Committing (design only, no runtime code, not pushed):

  Committed ff9e558

Committed (ff9e558), no runtime code touched, not pushed. Summary of the design pass, mapped to your six windows:

┌────────────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────┐
│             Window             │                                        Verdict                                         │
├────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. crash after request         │ Orphan request — already a valid, contract-tolerated state (Gate 2), nothing new       │
│ durable, before dispatch       │                                                                                        │
├────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. crash after provider        │ Missing recap — the one honestly irreducible risk. No journal ordering eliminates      │
│ returns, before response       │ this; it's inherent to durability following an external, non-transactional,            │
│ durable                        │ up-to-90-120s provider call. Named, not hidden or solved                               │
├────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. crash after response        │ Safe duplicate recap — the pre-existing "lost cursor → more recap, never less"         │
│ durable, before cursor-advance │ argument, trustworthy again now that item 2 fixed the corruption that had put it at    │
│  durable                       │ risk                                                                                   │
├────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. crash after cursor durable, │ Not actually a Ledger/Cursor problem — pure caller-notification ambiguity, same as any │
│  before HTTP 200 reaches       │  HTTP service, out of scope here                                                       │
│ caller                         │                                                                                        │
├────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. torn write mid-persist      │ Named as a required property the eventual encoding must provide (atomic append,        │
│                                │ detectable-if-torn) — not resolved, since no encoding is chosen yet                    │
├────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
│ 6. corrupt tail at restart     │ Safe by construction, provided window 5's property holds — discard the torn record     │
│                                │ only, reduce to windows 1/2/3                                                          │
└────────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────┘

Your bias is confirmed by the trace, not just agreed with: the asymmetry in window 3 (cursor-ahead-of-ledger must be structurally unreachable, cursor-behind is merely safe redundancy) is exactly what one strictly-ordered event stream per shared_session_id gives for free, and two independently-authoritative files would have to rebuild by hand. One journal per session (not global) — inherits items 1/2's already-proven no-cross-session-contention for free.

Durability point, answered precisely: request commits before dispatch begins; response+cursor commit together as one atomic unit after Gate 11 validation; HTTP 200 is the last thing that happens, strictly after that unit is durable — never before.

ZW/ZON/AP: genuine negative result. No established project-specific journal shape found — checked directly, not assumed. ZW's generic block pattern is structurally compatible in the abstract, reported as an available option for the encoding pass, not proposed as the answer here, and no fabricated "ZW persistence format."

Compaction/discard: correctly deferred — nothing today tracks which native sessions have ever consumed a shared_session_id, so no automatic compaction can be proven safe yet; that's new scope, not solved here.

Encoding still deliberately unchosen — four required properties named instead. Ready for review before the encoding-selection pass.

✻ Cogitated for 3m 59s

※ recap: Building EngAIn's dispatch/continuity system: items 1 (dispatch mutex) and 2 (ledger race) are done and pushed; item 3 (restart persistence) has an approved crash-consistency design awaiting review. Next: pick an encoding for the durability journal, then implement.

❯ I approve the crash-consistency design. It has now reduced item 3 to the right problem: preserving EngAIn-owned cross-provider continuity, not trying to duplicate native provider transcripts or make ephemeral presence durable.

  There is one wording correction I would make before the encoding pass. Window 2 is not absolutely “irreducible” in the architectural sense. It is irreducible with the capabilities EngAIn has today. If Hermes/Claude adapters someday expose reliable transcript read-back, EngAIn could potentially recover that returned response from native state. Today they do not, so the design should call it something like:

  ```text
  currently unrecoverable without provider transcript read-back
  ```

  rather than permanently impossible.

  The rest is strong. Especially this commit ordering:

  ```text
  REQUEST
    durable
      ↓
  provider invocation
      ↓
  validated RESPONSE + CURSOR ADVANCE
    durable atomically
      ↓
  HTTP success
  ```

  That gives the journal a very useful asymmetry: the cursor can never durably claim history the journal itself doesn't contain. Losing a cursor update can cause redundant recap; durably advancing ahead of the ledger must be structurally impossible.

  I also agree with one journal per `shared_session_id`. There is no established requirement for total ordering between unrelated shared sessions, so a global journal would introduce contention and recovery coupling for no semantic gain.

  Now I would move to encoding selection — still design only.

  But I would explicitly separate two things that are easy to accidentally conflate:

  ```text
  SEMANTIC RECORD
  what the event means

  DURABLE FRAMING
  how we know one whole event reached disk
  ```

  ZW/ZON belongs primarily in the first question. `fsync`, checksums, transactional commits, length-prefix framing, SQLite WAL, etc. belong in the second.

  That means we don't have to choose between “native language” and “safe persistence.” A project-shaped ZW record could eventually be stored inside a robust journal framing mechanism.

  I would give Claude this next instruction:

  > Crash-consistency design `ff9e558` is approved, with one wording amendment: window 2 is currently unrecoverable because no provider adapter exposes transcript read-back; do not characterize it as fundamentally unrecoverable forever.
  >
  > Proceed to an encoding/storage selection design pass only. No runtime implementation.
  >
  > Start from the semantic journal already established. Define the minimum durable event vocabulary before selecting syntax.
  >
  > At minimum derive the exact content required for:
  >
  > ```
  > TURN_APPENDED
  > ```
  >
  > and the atomic:
  >
  > ```
  > RESPONSE_COMMITTED + CURSOR_ADVANCED
  > ```
  >
  > operation, or whatever event grouping best expresses the approved crash model.
  >
  > Determine which fields must survive restart, including:
  >
  > * `shared_session_id`
  > * `turn_id`
  > * request/response direction
  > * actor
  > * origin body
  > * payload/content
  > * timestamps only if semantically required
  > * provider identity where required
  > * provider session identity where required
  > * cursor target
  > * any continuity snapshot/context that is actually authoritative rather than derivable
  >
  > Do not persist fields merely because the current Python dataclass contains them. Separate authoritative state from reconstructible/cache state.
  >
  > Then compare concrete storage candidates against the approved requirements.

  I would have him evaluate exactly these three families.

  First, SQLite. Python already ships an SQLite interface, and a transaction can make response-turn insertion plus cursor advancement one atomic commit. It gives crash recovery and torn-write handling without us inventing our own storage engine. But Claude should analyze whether one SQLite file per `shared_session_id` fits the chosen per-session-journal architecture, and whether SQLite starts becoming an unnecessarily opaque database around what is conceptually an append-only continuity stream.

  Second, a framed append-only journal file. Something like:

  ```text
  [length][record bytes][checksum]
  [length][record bytes][checksum]
  [length][record bytes][checksum]
  ```

  with flush/fsync at the defined durability points.

  That naturally matches the model Claude derived and makes restart replay straightforward. But it means EngAIn itself owns correctness for framing, partial-tail detection, checksumming, versioning, and atomic multi-fact records. If we choose this, the implementation must be deliberately tiny and heavily tested.

  Third, project-shaped ZW records inside a durable framing mechanism. Not “invent a universal ZW format.” Define the shape this particular EngAIn continuity journal requires, because—as you clarified—the project dictates ZW's concrete shape.

  For example, conceptually, not as a proposed final syntax:

  ```text
  continuity
    session S
    turn 42
    response
    actor dragon
    provider hermes
    provider-session X
    payload ...
    cursor-through 42
  ```

  The semantic grouping is what matters. The actual ZW shape should come from the project's ZW conventions Claude just inspected.

  I would tell him explicitly not to choose ZON merely because it is downstream of ZW. ZON is operationally important, but if there is no active ZW→ZON compiler/runtime on this continuity path today, making persistence depend on one would turn item 3 into a much larger project. Likewise, AP is important architecture, but this journal does not appear to be an AP execution problem.

  The comparison table in the design note should answer:

  ```text
                          SQLite   Framed file   ZW + framing
  atomic compound commit
  torn-tail detection
  ordered replay
  human inspectability
  append-only semantics
  stdlib dependencies
  recovery complexity
  future schema evolution
  project-native semantics
  ZW/ZON future compatibility
  cross-session contention
  compaction path
  ```

  There is one more thing I want derived before selecting the winner: **event identity/idempotency**.

  After a crash/retry, the recovery process needs to distinguish:

  ```text
  this exact durable event already exists
  ```

  from:

  ```text
  this is a genuinely new turn
  ```

  Do not automatically use `turn_id` for that purpose. `turn_id` is the ledger order identity within a shared session. A durable record may need its own event/commit identity, especially if later migration, replay, or repair tools rewrite/compact journals.

  So add:

  > Determine whether journal records require a stable record/event ID distinct from `turn_id`. If not, prove why `turn_id` is sufficient for replay/idempotency. Do not add another identifier without a concrete requirement.

  And I would scrutinize one other thing: payload durability. If `Turn.payload` can eventually contain richer native ZW semantics that JSON cannot losslessly represent, the storage choice must not silently constrain future payloads to JSON's value model. That's where our native-language discussion matters directly.

  It doesn't mean “therefore use ZW today.” It means:

  ```text
  Do not choose a persistence envelope that makes
  JSON expressiveness the permanent ceiling of Turn.payload.
  ```

  A framed byte-record system or SQLite BLOB/TEXT column can leave that door open even if the first implementation uses a simpler encoding.

  So my current status is:

  **Crash model: GREEN.**
  **Persistence scope: GREEN.**
  **Per-session journal: GREEN.**
  **Encoding: still deliberately undecided.**
  **Next: compare storage/framing independently from semantic record shape, with ZW treated as a real future/native factor rather than a checkbox.**

  Read 1 file

● Update(full audit/08-19-2026-item3-crash-consistency-design.md)
Added 13 lines
that gets implemented. **Design only — no runtime code, no encoding
selected.**

> **Wording amendment (same day, before the encoding pass)**: window 2
> below was originally characterized as "honestly-irreducible." That
> overstated it. It is irreducible only *with the capabilities EngAIn
> has today* — no dispatcher adapter exposes provider transcript
> read-back, so EngAIn cannot currently recover a response that landed
> on the native side but never reached EngAIn's own durable write. If
> that capability is ever added, this specific gap could close by a
> different route than journal design. Corrected wording below to
> **"currently unrecoverable without provider transcript read-back"** —
> not fundamentally or permanently impossible. The technical claim this
> was making (no *journal-ordering* design change closes it) still
> stands; only the "forever" framing was wrong.

## 1. The failure windows, traced against the actual code

`handle_turn()`'s real step order (unchanged by items 1/2, both already

● Update(full audit/08-19-2026-item3-crash-consistency-design.md)
Added 1 line, removed 1 line
| # | Window | Reconstructed state after restart | Consequence |
|---|---|---|---|
| 1 | Crash after request turn durable, before dispatch | Ledger has the request; no response exists; cursor un
affected | **Orphan request** — but this is not a new failure mode. Gate 2 (§7 of the contract) already require
s exactly this to be a valid, tolerated state: "a request may be appended even while nobody is currently on the
 other side." No special recovery needed beyond what the system already does for any unanswered request. |
| 2 | Crash after provider returns, before response turn durable | Ledger has only the request; the *native* pr
ovider's own transcript already contains the exchange (durable, vendor-side, per item 3's own derivation) — but
 EngAIn's Ledger does not | **Missing recap**, bounded and inherent — not eliminable by any journal-ordering de
sign, only by making the request-durable→dispatch→response-durable path as short as possible. See §4: no design
 can make "provider call succeeded but our own write hadn't landed yet" impossible when the provider call is an
 external, non-transactional, possibly-multi-second subprocess. This is the one honestly-irreducible risk windo
w; it is bounded (one exchange, one shared_session_id, one crash), not open-ended. |
| 2 | Crash after provider returns, before response turn durable | Ledger has only the request; the *native* pr
ovider's own transcript already contains the exchange (durable, vendor-side, per item 3's own derivation) — but
 EngAIn's Ledger does not | **Missing recap**, bounded and **currently unrecoverable without provider transcrip
t read-back** — no journal-ordering design closes this, since it's not an ordering problem: the provider call i
s an external, non-transactional, possibly-multi-second subprocess, and no write on EngAIn's side can be made t
o happen *before* a response EngAIn doesn't have yet. Bounded (one exchange, one shared_session_id, one crash),
 not open-ended, and not necessarily permanent — see §4: if a dispatcher adapter ever exposes reliable read-bac
k of a native transcript, this gap could close by recovering the response from provider-side state instead of f
rom EngAIn's own journal. Not pursued in this pass; named as the honest limit of what journal design alone can
guarantee today. |
| 3 | Crash after response turn durable, before cursor advance durable | Ledger correctly has the response; cur
sor for that `(provider_id, provider_session_id)` is stale — still shows the pre-exchange value | **Safe duplic
ate recap.** The next dispatch to that same native session recaps a turn it already actually produced. This is
exactly the pre-existing, already-endorsed safety argument ("a lost cursor can only cause more recap, never les
s") — now trustworthy again specifically because item 2 closed the `turn_id` corruption that had put that argum
ent at risk. |
| 4 | Crash after cursor advance durable, before the HTTP response reaches the caller | Ledger and cursor are b
oth **fully, correctly durable** | **Not a Ledger/Cursor consistency issue at all** — this is a caller-notifica
tion ambiguity (the caller doesn't know its request succeeded), identical in shape to what any HTTP service has
 whenever a response is lost after the server-side effect committed. Out of scope for this journal design; woul
d need an idempotency key on the *caller's* retry to fix, which is separate, unbuilt, unscoped-here machinery.
|
| 5 | Process kill mid-write of a single event record (torn write) | Whatever the storage mechanism leaves behi
nd — a partial/unparseable record, *unless* the mechanism guarantees atomic, all-or-nothing appends | **Unrecov
erable corruption is possible** unless the eventual storage choice provides: an event either lands whole or not
 at all, and a torn tail is *detectable*, never silently accepted as valid. This is a required property of what
ever encoding gets chosen later (§3) — not resolved here, but the requirement is non-negotiable regardless of w
hich encoding is picked. |

Now the summary section's matching phrase:

  Searched for 1 pattern, read 1 file

● Update(full audit/08-19-2026-item3-crash-consistency-design.md)
Added 6 lines, removed 3 lines

- Six failure windows traced against the real code; five are safe or
  already-tolerated by existing contract gates; one (window 2, provider
  succeeded but the write hadn't landed) is an honestly bounded,
  irreducible risk inherent to any design where durability follows an
  external, non-transactional provider call — named, not hidden.
  succeeded but the write hadn't landed) is honestly bounded and
  currently unrecoverable without provider transcript read-back — a
  limit of today's dispatcher-adapter capabilities, not a permanent
  architectural impossibility — inherent to any *journal-ordering*
  design where durability follows an external, non-transactional
  provider call. Named, not hidden.
- One durable, strictly-ordered event stream per `shared_session_id`,
  not two independently-authoritative files — proven necessary, not
  merely preferred, by the asymmetry in table row 3 vs. its reverse.

  Committed 46c51aa

● Write(full audit/08-19-2026-item3-encoding-selection-design.md)
Wrote 243 lines to full audit/08-19-2026-item3-encoding-selection-design.md
# Item 3 Amendment — Encoding/Storage Selection for the Continuity Journal

Written 2026-08-19, following approval of the crash-consistency model
(`ff9e558`, wording-corrected `46c51aa`). **Design only — no runtime
code, no final encoding decision.** Semantic record derived first, per
instruction, before any syntax/storage comparison.

## 1. Minimum durable event vocabulary

Two event types, not more — derived from the approved crash-consistency
… +285 lines

Committing (design only, no runtime code, not pushed):

  Committed b8003c7

Committed (b8003c7), no runtime code touched, not pushed. Wording amendment (46c51aa) and the encoding pass both done. Summary:

Wording fix: window 2 corrected from "honestly-irreducible" to "currently unrecoverable without provider transcript read-back" — the technical claim (no journal-ordering design closes it) stands; only the "forever" framing was wrong.

Semantic vocabulary, derived not assumed: two event types — TURN_APPENDED (request only) and RESPONSE_COMMITTED (response + cursor evidence, as one physical record, not two records in a transaction). That's a real finding, not a rewording: I traced the only production call site of cursor.advance() and it always advances to exactly the response turn's own turn_id — so cursor state is fully derivable at replay from RESPONSE_COMMITTED events alone, provided each one carries provider_id/provider_session_id (the one genuinely new field, needed for reconstruction, not copied from the dataclass). No separate CURSOR_ADVANCED event needed. I flagged this explicitly as a discovered simplification of the approved model, for your review — not something I assumed was pre-approved by extension.

Field table: went through every field you listed against real call sites. Notable results — actor is a derivable constant ("player") for requests per the contract's own invariant, not persisted; direction becomes implicit in event type; timestamp confirmed non-authoritative (nothing reads it) but kept as labeled metadata; model_id/launch_options aren't part of ContinuityCursorTracker's own key and aren't persisted; dispatch_input is a pure function of already-persisted state and isn't persisted.

Event identity: proved turn_id is sufficient — replay is read-only (inherently idempotent), and write-time dedup is already handled one layer up by both avatar repos' own processed_request_ids. No new identifier added. Named the one legitimate future trigger (compaction tooling) without acting on it.

Payload durability: stated as a concrete requirement (opaque, length-delimited, never type-constrained) any candidate must satisfy — not deferred vaguely.

Comparison table: filled out as requested, with one correction surfaced along the way — "ZW + framing" isn't a third competitor at the framing layer, it's a record-encoding choice that rides on either SQLite or a framed file. SQLite's real strength (transactional correctness we don't have to prove ourselves) is weighed honestly against its real weakness (append-only becomes our own discipline, not an engine guarantee — same distinction that made one ordered stream beat two files in the crash-consistency pass). I named a lean toward the framed file (direct precedent already in this codebase's own _atomic_write_no_replace) without declaring a winner, since you flagged encoding as still deliberately open.

ZW/ZON: re-confirmed a third time, no active compiler/runtime on this path — not recommending a ZON dependency. ZW-as-content stays real and open, not designed here, not faked.

Ready for your call on framing before the next pass (actual record shape, then implementation).

✻ Crunched for 6m 47s

※ recap: We've been hardening EngAIn's continuity system (item 1 dispatch mutex and item 2 ledger race are done and pushed); now designing crash-safe restart persistence for item 3. Encoding choice (SQLite vs. framed file) is still open and needs your decision before implementation.

❯ I’d choose the framed append-only file, not SQLite.

  The reason is that the latest design removed the main thing SQLite would have bought us: you no longer need a database transaction spanning a response row and a separate cursor row. `RESPONSE_COMMITTED` is one physical durable record containing both the response turn and the evidence needed to reconstruct the cursor. That makes the persistence model naturally journal-shaped.

  So the architecture becomes:

  ```text
  one shared_session_id
          ↓
  one ordered journal
          ↓
  ┌────────────────────────────┐
  │ TURN_APPENDED              │  request
  ├────────────────────────────┤
  │ RESPONSE_COMMITTED         │  response + provider cursor
  ├────────────────────────────┤
  │ TURN_APPENDED              │
  ├────────────────────────────┤
  │ RESPONSE_COMMITTED         │
  └────────────────────────────┘
          ↓ restart replay
  SessionLedger + ContinuityCursorTracker
  ```

  SQLite would work, but we would be using a transactional database largely to simulate an append-only event stream that the design already naturally is. It also makes inspecting and reasoning about the canonical continuity history harder.

  The framed file has another advantage for ZW: the framing layer does not have to care what the semantic record eventually looks like. The durable envelope can carry opaque bytes. Today those bytes could use the simplest established project representation; later a genuinely established project-shaped ZW record can occupy exactly the same frame without redesigning the crash-safe storage layer. That keeps JSON from becoming the permanent expressive ceiling.

  I would approve the framed-file direction with some hard requirements before record-shape design.

  First, do not use newline-delimited JSON as the journal framing. That fails the separation we just established between semantic representation and durable boundaries.

  Think conceptually:

  ```text
  FILE HEADER

  FRAME
      magic/version
      record length
      record bytes
      integrity check

  FRAME
      magic/version
      record length
      record bytes
      integrity check

  FRAME
      ...
  ```

  The exact binary layout is the next design task, not something to invent casually now. But every frame must be independently recognizable and length-delimited.

  Second, the tail-recovery rule should be extremely strict:

  ```text
  valid complete frames
  valid complete frames
  valid complete frames
  TORN / INCOMPLETE FINAL FRAME
  ```

  Restart accepts everything through the last complete validated frame and discards only the incomplete tail.

  But:

  ```text
  valid
  CORRUPT FRAME
  valid-looking data after it
  ```

  should not silently skip the bad middle and continue. That's corruption inside committed history, not merely a torn tail. Startup should stop/reject/quarantine that session journal rather than manufacture continuity across a hole.

  Third, durability must mean actual durability. `write()` succeeding is not the commit point.

  For the approved semantics:

  ```text
  write complete frame
          ↓
  flush
          ↓
  fsync journal
          ↓
  NOW durable
  ```

  Then and only then may the operation proceed as though that record survived an EngAIn process/machine failure.

  If directory creation or first-time journal creation requires filesystem metadata durability, Claude should derive whether the containing directory also needs an `fsync` at creation time. Don't let “we called fsync on the file” become a hand-wave around first-creation semantics.

  Fourth, the frame must be encoding-agnostic with respect to payload. I would explicitly prohibit a design like:

  ```python
  json.dumps(turn.payload)
  ```

  as the persistence contract.

  Metadata can initially use some constrained encoding if justified, but `payload` itself must have a representation that can be treated as opaque bytes plus an encoding/content-type discriminator if necessary.

  Conceptually:

  ```text
  payload_encoding = ...
  payload_length   = ...
  payload_bytes    = ...
  ```

  not:

  ```text
  payload must be a JSON value forever
  ```

  That leaves room for project-shaped ZW without pretending we've already designed that ZW shape.

  Fifth, I agree with `turn_id` being sufficient for replay identity under the current scope. I would not add another UUID yet. The journal is replayed, not reapplied as new turns, so:

  ```text
  (shared_session_id, turn_id)
  ```

  already identifies a durable turn within its canonical stream.

  There is no reason to solve future compaction/migration identities before compaction exists.

  Sixth, one journal per `shared_session_id` is the correct unit, but don't use an arbitrary caller-supplied `shared_session_id` directly as a filename. That creates filesystem naming/path-traversal problems.

  The next pass should establish a deterministic safe mapping such as:

  ```text
  shared_session_id
         ↓
  stable encoded/hash-derived journal filename
  ```

  while retaining the original `shared_session_id` inside the journal so recovery can verify that the file and its contents agree.

  Seventh, journal ordering and in-memory ordering must become one operation. Item 2 already gave `SessionLedger` a per-session append lock. Persistence should not accidentally create a second competing ordering authority.

  The eventual request path should have semantics roughly like:

  ```text
  acquire shared-session append/order boundary
      allocate turn_id
      construct TURN_APPENDED
      append durable frame
      fsync
      append same Turn to in-memory ledger
  release
  ```

  and response:

  ```text
  acquire shared-session append/order boundary
      allocate response turn_id
      construct RESPONSE_COMMITTED(
          response turn,
          provider_id,
          provider_session_id,
          cursor_through=response_turn_id
      )
      append durable frame
      fsync
      append response to in-memory ledger
      advance in-memory cursor
  release
  ```

  The important part is that this lock ends immediately afterward. It still must never span the provider call.

  There is a subtle crash state here worth having Claude explicitly prove in the next pass:

  ```text
  frame fsync succeeds
  PROCESS DIES
  before corresponding in-memory append
  ```

  That is actually recoverable because the journal is canonical after restart. But while the process remains alive, a Python exception between durable write and memory mutation could leave disk ahead of RAM without a restart. The implementation design therefore needs an explicit policy: either treat any post-durable in-memory mutation failure as fatal to that authority generation, or structure the state mutation so that such failure is effectively impossible/controlled. Don't silently continue with divergent RAM and durable state.

  So I’d give Claude this:

  > Encoding/framing decision: choose one append-only framed journal file per `shared_session_id`. Do not implement yet.
  >
  > SQLite is rejected for this item because the approved semantic model no longer requires independent transactional tables: `RESPONSE_COMMITTED` carries response + cursor evidence as one durable event. A journal directly represents the canonical model with less semantic machinery.
  >
  > Design the actual durable frame and record shape next.
  >
  > Requirements:
  >
  > 1. Separate durable frame boundaries from semantic record encoding.
  > 2. No newline-delimited JSON framing.
  > 3. Each frame must contain sufficient version/magic, length, and integrity information to detect a torn or corrupt record.
  > 4. A torn final frame may be discarded during recovery.
  > 5. Corruption before the final frame must not be silently skipped.
  > 6. Define the exact `write → flush → fsync` durability point, including first-file/directory creation semantics where necessary.
  > 7. Payload storage must remain opaque/encoding-extensible; do not permanently restrict `Turn.payload` to JSON's type system.
  > 8. Define the concrete field shape for `TURN_APPENDED` and `RESPONSE_COMMITTED`.
  > 9. Keep `RESPONSE_COMMITTED` as one physical record carrying both the response turn and its `(provider_id, provider_session_id)` cursor evidence unless the field derivation reveals a contradiction.
  > 10. Keep `turn_id` as the record/turn replay identity unless a concrete current requirement proves another event ID is necessary.
  > 11. Define a safe deterministic filesystem mapping from arbitrary `shared_session_id` to journal filename; do not place the raw caller-supplied ID directly into a path.
  > 12. Reconcile durable append ordering with item 2's existing per-session append synchronization. Do not introduce an independent ordering mechanism and do not hold it across provider dispatch.
  > 13. Explicitly analyze the state where a durable frame succeeds but the corresponding in-memory update fails before process termination. Define how the authority prevents continued operation with disk/RAM divergence.
  > 14. Define startup replay validation: expected turn sequence, session identity checks, response/cursor reconstruction, clean tail handling, corrupt-middle handling.
  > 15. Inspect the established project-specific ZW conventions while designing record content. If a natural shape exists, show it. If it doesn't, keep the content encoding extensible rather than inventing ZW syntax merely to use the name.
  >
  > Design only. Commit the framing/record-shape analysis and stop for review before implementation.

  One small adjustment to Claude's statement that existing `_atomic_write_no_replace` is precedent: it is useful evidence for filesystem discipline, but atomic replacement and append-only journaling have different failure mechanics. I would borrow established low-level practices from it, not treat it as proof that journal appends are already solved.

  So the decision is now firm:

  **Storage model: framed append-only per-session journal.**

  **Semantic records: `TURN_APPENDED` + `RESPONSE_COMMITTED`.**

  **Record encoding: next design pass.**

  **ZW compatibility: preserve the opening without inventing a format.**

  **Implementation: still not yet.**

● Write(full audit/08-19-2026-item3-frame-and-record-shape-design.md)
Wrote 444 lines to full audit/08-19-2026-item3-frame-and-record-shape-design.md
# Item 3 Amendment — Durable Frame and Record Shape

Written 2026-08-19, following the storage-model decision: **framed
append-only journal, one file per `shared_session_id`, rejecting SQLite**
because `RESPONSE_COMMITTED` already carries response + cursor evidence
as one physical record — there is no independent-tables problem left for
a transactional database to solve. **Design only — no runtime code, no
implementation.**

One correction carried into this pass: the prior document's reference to
… +434 lines

Committing (design only, no runtime code, not pushed):

  Committed ae701dd

Committed (ae701dd), no runtime code touched, not pushed. All 15 requirements addressed. Highlights worth flagging directly:

- Frame/checksum scope: covers the whole frame (magic+length+bytes), not just the body — a corrupted length field is caught the same way corrupted content is, rather than left as a separate unhandled case.
- Tail vs. corruption line drawn precisely: the only safe-to-discard case is "insufficient bytes remain." Everything else — bad magic with data still present, a checksum mismatch on a full-length frame, or a new check I added (a turn_id sequence gap/out-of-order value during replay, which checksums alone wouldn't catch) — halts and quarantines that one session's journal, isolated from every other session, never a whole-server failure.
- First-creation durability: derived the directory-fsync requirement explicitly rather than stopping at "we called fsync on the file" — a real POSIX gotcha, one-time cost per session at its first write.
- §13, the one you specifically wanted proven: two combined mitigations, not a single choice — shrink the window structurally (construct everything in memory before the durable write, so the post-durability step is a bare list.append()), and treat the residual, non-zero risk as fatal to that one session only (poison-and-refuse, not a process-wide crash) — chose the narrower option specifically because a whole-process crash would violate the isolation principle the rest of this design already depends on.
- Ordering: confirmed ContinuityCursorTracker still needs no lock of its own — not assumed, checked against item 1's own claim mechanism, which already prevents concurrent writers to a given cursor key.
- Named the real, new cost honestly: the per-session lock now holds through one synchronous fsync — categorically shorter than a provider dispatch, but a measurable change from item 2's pure in-memory version, worth benchmarking at implementation time rather than left unstated.
- ZW checked a fourth time at this now-concrete field level — same honest negative result, door kept open via the payload_encoding/snapshot_encoding discriminators, nothing invented.

Status: storage model, frame shape, record shape, filename mapping, and ordering are all decided, not just leaned toward. Implementation is next — still wanting review before any code, same as every item so far.

✻ Worked for 7m 48s

❯ This is very close, but I would not start implementation yet. I see two framing/recovery holes worth fixing now rather than discovering them under a kill test.

  The first is subtle: a checksum over `magic + length + body` does not always protect the length field soon enough.

  Suppose the final committed frame is:

  ```text
  magic
  length = 100
  100 bytes body
  checksum
  ```

  and later the length field alone is corrupted upward:

  ```text
  length = 100000
  ```

  On replay, the reader sees that 100,000 bytes are not available and hits your current rule:

  ```text
  insufficient bytes remain
  → torn final frame
  → discard safely
  ```

  But this wasn't necessarily a torn write. It could be corruption of a fully committed frame's length. The whole-frame checksum cannot help because the reader needs the length to locate the body and checksum in the first place.

  So the fixed-size header itself needs independently checkable integrity before its length can be trusted. For example, conceptually:

  ```text
  MAGIC
  VERSION
  BODY_LENGTH
  HEADER_CHECK
  BODY
  FRAME_CHECK
  ```

  or an equivalently redundant header such as length + complement plus a checksum. I wouldn't prescribe the exact bytes yet, but the invariant should be:

  ```text
  Do not classify "body shorter than declared length"
  as a safely torn tail unless the fixed header,
  including its declared length, has first been validated.
  ```

  Then you get a defensible distinction:

  ```text
  invalid header
  → CORRUPTION / quarantine

  valid header + incomplete declared body/trailer
  → TORN FINAL FRAME / truncate-discard tail
  ```

  That's the first blocker.

  The second is what happens when a write fails but the authority process does not die.

  Imagine:

  ```text
  known-good journal offset = 500

  write(frame 12)
      writes first 40 bytes
      raises OSError
  ```

  The process is still alive. If EngAIn catches the exception and later writes frame 13 at EOF, you now have:

  ```text
  valid frame 11
  partial frame 12
  valid frame 13
  ```

  What would have been a safely discardable torn tail has become corruption in the middle of committed-looking history.

  So the design needs a rule for failed append attempts while the process survives.

  The clean choices are:

  ```text
  A. remember pre-append offset
     → on failure ftruncate() back to it
     → fsync()
     → continue only if rollback is proven successful

  or

  B. immediately poison that shared_session_id
     → refuse all further persistence/dispatch for it
     → require restart/recovery
  ```

  Given the conservative design you've already chosen, I lean toward B unless rollback is extremely straightforward. The crucial rule is simply: **never append another frame after an uncertain partial append.**

  There is one startup invariant I would make explicit too, though I don't consider it a major redesign:

  ```text
  journal recovery/replay
          ↓
  quarantine bad sessions
          ↓
  reconstruct Ledger + Cursor
          ↓
  ONLY THEN advertise authority ready / accept /dispatch
  ```

  Otherwise a request could race startup reconstruction and mutate a partially recovered session. If the current authority already performs initialization completely before binding/listening, just document and test that property.

  Everything else in your summary looks ready:

  * per-session journals: yes;
  * `TURN_APPENDED` plus `RESPONSE_COMMITTED`: yes;
  * response + cursor evidence in one record: yes;
  * no independent cursor persistence: yes;
  * raw `shared_session_id` not used as filename: yes;
  * per-session ordering lock extending only through `fsync`: acceptable;
  * provider call stays outside that lock: essential;
  * disk-ahead-of-RAM residual failure → poison only that session: sensible;
  * opaque payload encoding boundary: correct;
  * no fabricated ZW shape: correct;
  * ZON/AP remain known architectural factors without creating a dependency that does not currently exist.

  I would send Claude this final design correction:

  > Framing design is nearly approved. No runtime code yet.
  >
  > Amend two failure semantics before implementation.
  >
  > **1. Length-field corruption ambiguity**
  >
  > The current whole-frame checksum cannot validate `length` before `length` itself is used to find the remainder of the frame.
  >
  > A corrupted final-frame length that becomes larger than the remaining file could therefore be misclassified as an ordinary torn tail.
  >
  > Add independently verifiable integrity/redundancy to the fixed-size frame header so replay validates the declared body length before using "insufficient remaining bytes" as evidence of a torn final frame.
  >
  > Required distinction:
  >
  > ```
  > invalid/unverifiable header
  >     → corruption; quarantine session
  >
  > valid header + incomplete declared frame
  >     → torn final append; discard/truncate tail
  > ```
  >
  > Do not rely solely on a checksum located after the variable-length body to establish header integrity.
  >
  > **2. Partial write without process death**
  >
  > Derive the live-process policy for:
  >
  > ```
  > append begins
  > some bytes reach the journal
  > write/flush/fsync fails
  > authority remains alive
  > ```
  >
  > It must be impossible to append another record after an uncertain partial tail and thereby convert recoverable tail damage into middle-of-stream corruption.
  >
  > Either:
  >
  > * roll back atomically to the known-good pre-append offset and prove/trust that rollback via truncate + durability synchronization; or
  > * poison that `shared_session_id` immediately and refuse further operations for it until recovery.
  >
  > Choose and document one. Failure to prove rollback must always degrade to poisoning, never continued writing.
  >
  > Also state explicitly that journal replay/reconstruction completes before the authority advertises readiness or accepts `/dispatch`.
  >
  > Amend the design only, commit it separately, and stop for review.

  Once those are resolved, I would approve implementation.

  The rest of `ae701dd` sounds like the architecture has converged nicely. This is now about making sure the lowest-level journal framing cannot lie to the semantic layer above it.

● Write(full audit/08-19-2026-item3-framing-integrity-and-write-failure-amendment.md)
Wrote 219 lines to full audit/08-19-2026-item3-framing-integrity-and-write-failure-amendment.md
# Item 3 Amendment — Header Integrity and Live-Process Write-Failure Policy

Written 2026-08-19, closing the two holes found in `ae701dd`'s framing
design before implementation. **Design only — no runtime code.** Both
fixes are real corrections to that document, not extensions of it —
`ae701dd` itself is left unedited, per this project's standing
discipline; this document supersedes its framing/recovery rules on the
two points below.

## 1. The length field must be validated before it's trusted
… +209 lines

Committing (design only, no runtime code, not pushed):

  Committed 1bd0e04

Committed (1bd0e04), no runtime code touched, not pushed. Both holes closed:

1. Header integrity, split into two stages so length is validated before it's trusted rather than being used to locate the rest of the frame before anything checks it: a fixed-size prefix (magic/version/body_length/header_check) is verified independently first — only if that passes does body_length get used at all, followed by the body + a whole-frame checksum, unchanged in spirit from before. This gives exactly the distinction you asked for: an unverifiable header is corruption/quarantine regardless of how much data follows it; a verified header with an incomplete declared body is the only case still treated as a torn tail. I also went back and applied the identical fix to the once-per-file header — its shared_session_id field has the exact same variable-length-trusted-before-validated shape, and I didn't want to leave it exposed just because the example given was about per-record frames.

2. Poison over rollback, with the reasoning made explicit rather than asserted: the failure modes that cause a write()/fsync() to fail in the first place (disk full, I/O error, a failing device) are exactly the conditions under which a subsequent ftruncate()+fsync() on the same file isn't reliably guaranteed to succeed either — so rollback is least trustworthy precisely when it would matter most. Stated the absolute rule as written: no further append for that session, ever, in that process generation, once the tail is uncertain. I also tied this back to the durability-honesty requirement from the crash-consistency pass — continuing to serve requests while quietly giving up on persisting them would violate the "never send 200 for undurable state" rule, just deferred and harder to notice, which is the concrete reason poison-and-refuse beats poison-persistence-but-keep-serving.

3. Replay-before-mutation stated as a hard invariant, reconciled against both shapes ae701dd left open (eager: a global readiness barrier before binding; lazy: the same per-session lock that already orders appends also serializes first-touch replay, for free) — and confirmed the current persistence-free authority already satisfies this trivially today, as supporting context, not proof it carries over automatically once persistence is added.

Everything else from ae701dd stands, untouched. Ready for your call — this was the last precondition you named for implementation.

✻ Brewed for 3m 5s

※ recap: We're building crash-safe persistence for EngAIn's cross-provider chat history. Design is fully approved through the low-level framing fixes; next step is implementing the journal writer/reader itself, which still needs your review before it's merged.

❯ can you install this as a plug in https://github.com/cathrynlavery/diagram-design

● Fetch(https://github.com/cathrynlavery/diagram-design)
Received 446.8KB (200 OK)

  Ran 2 shell commands

Now adding the marketplace and installing the plugin:

  Ran 1 shell command

Marketplace added. Now let's see what plugin(s) it exposes and install:

  Ran 2 shell commands

Let's verify it's actually installed and enabled:

  Ran 1 shell command

Installed and enabled: diagram-design@diagram-design v2.5.6, scope user (so it's available across all your sessions, not just this one).

What you got: 5 skills — diagram-design (the main one, ~14.4k tokens when invoked), export-diagram, import-drawio, import-mermaid, and profile. It generates 28+ diagram types (architecture, flowcharts, sequence/state diagrams, ER models, Gantt, org charts, etc.) as self-contained HTML/SVG/PNG, can redraw existing draw.io or Mermaid sources, and can onboard brand tokens (colors/fonts) from a website for on-brand output. Always-on cost is small (~418 tokens/session); the real cost only hits when a skill actually fires.

One thing worth noting: this session already has a restart pending to pick it up — plugins load at session start, so the skill won't be available to invoke until your next new Claude Code session (the CLI's own install output doesn't mention this, but that's how plugin loading works). Once that happens, you can just ask for a diagram in a normal request and it should be available, or invoke it explicitly.

✻ Cogitated for 13m 51s

※ recap: We've been hardening EngAIn's shared continuity system; item 3 (crash-safe restart persistence) is fully designed and approved, not yet implemented. Next: implement it, pending your go-ahead.
                                                                                         new task? /clear to save 736.7k tokens
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
❯
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ⏵⏵ auto mode on (shift+tab to cycle) · ← for agents
