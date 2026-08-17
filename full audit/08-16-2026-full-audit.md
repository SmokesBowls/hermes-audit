 AUDIT RESULT
    
    EngAIn no longer has one supported command that boots the complete runtime described in the request.
    
    The surviving canonical Python launcher starts only the Tier-1 AP/scene server. The 2D/3D mailbox listeners, persistent
    Presence renewal, shared-session service, and provider dispatcher are not wired into any runtime entry point. The recent
    Hermes and Claude scripts are isolated continuity proofs, not boot paths.
    
    Files changed: none. Final git status --short was clean.
    
    
    LIVE COLD-START TEST
    
    I tested both the intended top-level orchestrator and the currently blessed runnable entry point.
    
    1. Top-level orchestrator attempt
    
    Exact command:
    
        timeout --signal=INT --kill-after=5s 30s python3 -u start_button.py
    
    Result:
    
        [FAIL] Missing central manifest:
        /home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/manifests/engain_manifest.json
    
    Exit code: 1
    
    It exited before starting any process. Even if that manifest were restored, start_button.py:63-66 next calls:
    
        ./start_stack.fish
    
    That file is also absent. stop_stack.fish is absent as well.
    
    Processes/servers started: none.
    Mailbox leases activated: neither.
    Cleanup: unnecessary; nothing was launched.
    Ports 8080, 8090, 8765, and 8766 remained closed.
    
    2. Most complete runnable, code-designated canonical entry point
    
    Exact command:
    
        python3 -u tier1/engainos/launch_engine.py
    
    It remained alive for over a minute and was independently verified on port 8765.
    
    What it actually started:
    
    - One Python OS process:
      - python3 -u tier1/engainos/launch_engine.py
    - One daemon thread inside that process:
      - HTTPServer scene/AP query server on 127.0.0.1:8765
    - In-process AP runtime initialization:
      - scanned the Tier-1 game-scene files
      - initialized successfully
      - loaded zero AP rules
    - Imported the Godot adapter and printed:
      - Godot adapter: READY (stdin/stdout bound)
    
    Important: that last message did not represent a Godot process. Process inspection showed no Godot child and no other
    child process.
    
    Independent liveness evidence:
    
        LISTEN 127.0.0.1:8765 users:(("python3",pid=641610,fd=3))
    
    Both GET / and GET /health returned deterministic HTTP 404 JSON:
    
        {"status": "error", "message": "Endpoint not found"}
    
    Therefore port/process liveness was proven, but there is no health route on this server.
    
    Warnings during boot:
    
    - tools/trixel/ missing
    - godot/ missing under tier1/engainos/godot
    - AP initialized with zero rules
    
    Expected components that did not start:
    
    - Tier-2 simulation runtime on 8080
    - FastAPI facade on 8090
    - Trixel service on 8766
    - Root Godot project
    - Any 2D Godot/avatar process
    - Any 3D Godot/avatar process
    - UPBGE
    - 2D mailbox listener
    - 3D mailbox listener
    - background Presence renewal
    - shared-session bridge service
    - provider-selection/dispatch service
    - Hermes or Claude provider process
    
    Mailbox readiness leases:
    
    - Neither became active.
    - No mailbox listener implementation or readiness-lease implementation was found in this checkout—or elsewhere under
    /home/mytruelove.
    - PresenceRegistry existed only in memory inside tests/proof tools during this run, and launch_engine.py did not
    instantiate it.
    
    Health and shutdown:
    
    - The process stayed running until deliberately stopped.
    - It was stopped with SIGINT, equivalent to terminal Ctrl+C:
    
          kill -INT 641610
    
    - It printed ENGINE SHUTDOWN.
    - Exit code: 0.
    - Port 8765 disappeared.
    - PID 641610 disappeared.
    - No child process remained.
    - Cleanup therefore completed at the OS/process level. The scene-server thread is daemonized rather than explicitly
    joined, but process exit released the socket.
    
    
    ACTIVE RUNTIME ENTRY POINTS
    
    1. start_button.py
    
    Purpose:
    
    - Intended top-level “EngAIn START BUTTON.”
    - Supposed to call start_stack.fish.
    - Then runs cache-aware narrative compilation, merges scene artifacts, rebuilds the scene index, and probes 8080/8766.
    
    Current state:
    
    - Unusable from a cold terminal.
    - Fails first because manifests/engain_manifest.json is absent.
    - Its next dependency, start_stack.fish, is also absent.
    - It is partly a generated-artifact pipeline, not just a process launcher.
    
    2. tier1/engainos/launch_engine.py
    
    Documented command:
    
        cd /home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn
        python3 tier1/engainos/launch_engine.py
    
    Purpose:
    
    - Code labels itself the “ONLY blessed runtime entrypoint.”
    - Checks Tier-1 invariants.
    - Initializes APRuntimeIntegration.
    - Starts the 8765 scene/AP HTTP server.
    - Imports the Godot adapter.
    
    Does not start:
    
    - sim runtime
    - facade
    - Godot executable
    - mailbox listeners
    - Presence/shared session/provider services
    
    3. tier1/engainos/bridgeroom/scene_server.py
    
    Direct Python main:
    
        python3 -m tier1.engainos.bridgeroom.scene_server
    
    Purpose:
    
    - Starts only the 8765 HTTPServer.
    - Direct execution does not supply launch_engine’s AP message handler.
    
    This is a lower-level server entry point, not a whole-engine launcher.
    
    4. tier2/godotsim/sim_runtime.py
    
    Documented current command:
    
        cd /home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn
        python3 -m tier2.godotsim.sim_runtime
    
    Purpose:
    
    - Creates EngAInRuntime.
    - Starts the simulation loop owned by EngAInRuntime.
    - Binds ThreadingHTTPServer to 127.0.0.1:8080.
    - Owns the simulation snapshot and runtime HTTP API.
    - Has explicit Ctrl+C cleanup: closes the server and calls runtime.shutdown().
    
    It does not start Tier-1, FastAPI, Godot, or avatar/session services.
    
    5. tier1/engainos/engainos_server.py
    
    No built-in main().
    
    Documented invocation:
    
        NGAT_RT_BASE_URL=http://127.0.0.1:8080 \
        python3 -m uvicorn tier1.engainos.engainos_server:app \
          --host 127.0.0.1 --port 8090
    
    Purpose:
    
    - FastAPI facade over the already-running 8080 runtime.
    - Provides /api/health, /api/snapshot, command and HUD routes.
    
    It does not start its 8080 dependency.
    
    6. engainos_boot_kernel.py
    
    Direct command:
    
        python3 engainos_boot_kernel.py
    
    Purpose:
    
    - Runs boot gates in sequence.
    - Writes a presentation-only Godot boot-scene command packet.
    - Stops after gate/executor completion.
    
    It explicitly is not Godot execution and does not start a server, worker, Godot process, mailbox, Presence service, or
    provider.
    
    7. tier1/engainos/bridgeroom/godot_adapter.py
    
    Documented examples:
    
        python3 godot_adapter.py --scene chapter1_opening
        python3 godot_adapter.py --scene path/to/scene.json
    
    Current package-correct form would need the module path.
    
    Purpose:
    
    - One-shot scene conversion to JSON on stdout.
    - run_loop() explicitly outputs once and exits.
    
    It is not a listener or persistent bridge process.
    
    8. tier1/engainos/server/safe_runtime_server_entrypoint.py
    
    Not runnable.
    
    The file explicitly says:
    
    - scaffold only
    - no socket binding
    - not a live server
    - not executable as an entry point
    - port 8080 remains blocked for this scaffold
    
    9. Control centers
    
    These include:
    
    - engain_control/engain_master_control_center.py
    - tier1/engainos/engainos_control_center.py
    - corresponding subsystem control centers
    
    They are troubleshooting/gate boards. engain_master_control_center.py explicitly reports that it does not start workers
    or grant runtime authority.
    
    10. command_center/app.py
    
    Documented command:
    
        cd command_center
        python3 app.py
    
    Purpose:
    
    - Starts an Eel/browser control UI.
    - Shells out to interface/*.py.
    - Contains stub Godot-adapter buttons.
    
    It is not a runtime stack launcher.
    
    
    GODOT STARTUP PATHS
    
    Root Godot project:
    
        godot --path .
    
    project.godot declares:
    
        run/main_scene="res://scenes/GodotBootBridgeRunner.tscn"
    
    That scene attaches:
    
        godot/boot/GodotBootBridgeConsumeCommand.gd
    
    Flow:
    
    1. Reads runtime/godot_commands/BOOT_SCENE_LOAD_COMMAND_V1.json.
    2. Validates its presentation-only permissions.
    3. Changes to res://scenes/EngAInOSBootShell.tscn.
    4. That scene attaches godot/input/GodotInputListenerBridgeConsumeCommand.gd.
    5. The input listener reads PLAYER_INPUT_LISTENER_COMMAND_V1.json.
    6. It can capture narrowly allowed boot-shell input and write PLAYER_INPUT_PACKET_V1.json.
    
    This Godot input listener is not either requested mailbox listener. It has no shared-session, Presence, provider,
    2D-body, or 3D-body integration.
    
    Stale documented Godot command:
    
        cd .../EngAIn/godotnew/semantic
        godot --path .
    
    The godotnew/semantic path no longer exists in the current tiered checkout.
    
    Proof-only Godot launchers also exist under tier2/godotsim/gates/, including visible/headless launchers for:
    
    - floor/room rendering
    - player body and movement
    - piece recipe packs
    - trigger-zone/light proofs
    
    Those scripts launch temporary proof scenes, often terminate after a timeout, and are not production startup paths.
    
    
    SHARED SESSION, PRESENCE, AND PROVIDERS
    
    PresenceRegistry
    
    Location:
    
        tier1/engainos/core/presence_registry.py
    
    Current properties:
    
    - in-memory dictionaries only
    - lifetime of one process
    - default 300-second leases
    - lazy expiry during resolve()
    - no background sweeper
    - no persistence
    - no transport
    - no startup owner
    - no runtime call to renew()
    
    The contract itself still lists transport placement and renewal cadence as undecided.
    
    SharedSessionBridge
    
    Location:
    
        tier1/engainos/bridgeroom/shared_session_bridge.py
    
    Current properties:
    
    - ordinary in-process class
    - no server
    - no worker loop
    - no mailbox watcher
    - no startup entry point
    - default provider is a stub
    
    Its only live-provider construction sites are the two continuity proof tools.
    
    Provider adapters:
    
    - hermes_provider_adapter.py
    - claude_code_provider_adapter.py
    
    These are callable adapters, not dispatch daemons. They are referenced only by:
    
    - live_hermes_continuity_proof.py
    - live_claude_code_continuity_proof.py
    
    There is no central provider dispatcher that chooses the active occupant and runs continuously.
    
    Continuity proofs:
    
        python3 tier1/engainos/tools/live_hermes_continuity_proof.py
        python3 tier1/engainos/tools/live_claude_code_continuity_proof.py
    
    Each proof independently creates:
    
    - a new in-memory PresenceRegistry
    - a new in-memory SessionLedger
    - a SharedSessionBridge
    - one specific provider adapter
    
    They do not start Godot, mailbox listeners, 8080, 8090, or 8765. Their dragon_2d and dragon_3d values are provenance
    strings passed directly to handle_turn(), not messages received from running avatar bodies.
    
    
    LEGACY FULL-STACK SCRIPT
    
    The only script that attempts a multi-process stack is:
    
        out of root/tools/engain_stack_tmux.sh
    
    It attempts to open tmux windows for:
    
    - sim runtime on 8080
    - AP launch engine on 8765
    - FastAPI facade on 8090
    - Godot editor
    - UPBGE/Blender
    - a vault shell
    
    It is not usable now because:
    
    - it is under the preserved out of root/ historical tree, not tools/
    - AGENTS.md still documents the nonexistent tools/engain_stack_tmux.sh
    - it uses old /home/burdens/... paths
    - it uses pre-tier paths such as godotsim/ and godotengain/engainos/
    - it invokes python3 sim_runtime.py, which conflicts with current package-relative imports
    - tmux is not currently available
    - it has no mailbox, Presence, shared-session, or provider-dispatch windows
    - its “health” logic only checks occupied ports
    - attaching to tmux is part of the script, so it is not a clean noninteractive supervisor
    
    
    USABLE RUN SCRIPT?
    
    No usable whole-runtime run script currently exists.
    
    Usable individual commands exist for:
    
    - 8765 Tier-1 launch engine
    - 8080 Tier-2 simulation runtime
    - 8090 FastAPI facade
    - root Godot project
    
    But no command composes them, manages their readiness, adds the avatar/session/provider pieces, or shuts them down as one
    unit.
    
    
    SMALLEST LAUNCHER RESTORATION PROPOSAL — NOT IMPLEMENTED
    
    The smallest honest restoration would be one root-level supervisor command with two clearly separated responsibilities:
    
    1. Restore the currently existing stack
    
    Start, in order:
    
    - python3 -m tier2.godotsim.sim_runtime
    - python3 tier1/engainos/launch_engine.py
    - python3 -m uvicorn tier1.engainos.engainos_server:app --host 127.0.0.1 --port 8090
    - godot --path .
    
    Require real readiness checks, record PIDs, forward SIGINT/SIGTERM, and shut down all children in reverse order.
    
    2. Do not pretend the dragon bridge is launchable yet
    
    Before adding 2D/3D mailbox processes to that supervisor, a separately reviewed long-lived bridge host is needed to own
    exactly one:
    
    - PresenceRegistry
    - SessionLedger
    - SharedSessionBridge
    - provider-dispatch selector
    - Presence registration/renewal lifecycle
    - pair of body/mailbox ingress adapters
    
    Without that service boundary, a launcher would only start independent proof objects and falsely claim shared runtime
    continuity.
    
    No launcher or bridge host was created during this audit.


EXTENDED AUDIT RESULT
    
    Correction to the earlier audit:
    
    The 2D and 3D mailbox workers are not missing. They are external to EngAIn.
    
    - 2D implementation:
      /mnt/data-drive/engain_avatar
      Remote: git@github.com:SmokesBowls/engain_avatar.git
    - 3D implementation:
      /mnt/data-drive/godot_engain_3d_avatar
      Remote: git@github.com:SmokesBowls/godot_3d_avatar.git
    - Historical/live evidence:
      /mnt/data-drive/engain-avatar-audit
    
    Neither worker is imported or launched by the EngAIn checkout.
    
    Current live state:
    
    - /mnt/data-drive/engain-runtime-mailboxes is absent.
    - No 2D worker is running.
    - No 3D worker is running.
    - No corresponding Godot avatar process is running.
    - Neither readiness lease is active.
    - EngAIn remained clean.
    - No files were modified during this extension.
    
    
    1. WHERE THE MAILBOXES ARE CREATED
    
    2D ownership
    
    Python worker:
    
    /mnt/data-drive/engain_avatar/hermes_session_adapter.py
    
    Key constants:
    
    - DEFAULT_MAILBOX_ROOT:
      /mnt/data-drive/engain-runtime-mailboxes
    - CALLER_ID:
      dragon2d
    - request:
      /mnt/data-drive/engain-runtime-mailboxes/dragon2d/request.json
    - response:
      /mnt/data-drive/engain-runtime-mailboxes/dragon2d/response.json
    - listener lease:
      /mnt/data-drive/engain-runtime-mailboxes/dragon2d/listener.json
    
    The directory is created lazily. mark_listener_ready() writes listener.json through _atomic_write(), whose first
    operation is:
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    The 2D worker claims a request by atomically renaming:
    
    request.json
    
    to:
    
    .request.json.<pid>.<time_ns>.processing
    
    See:
    
    - hermes_session_adapter.py:805-811
    - hermes_session_adapter.py:791-803
    - hermes_session_adapter.py:1860-1867
    
    2D Godot producer/consumer:
    
    /mnt/data-drive/engain_avatar/addons/zwengain/scripts/EngAInBridge.gd
    
    It explicitly addresses the 2D mailbox at EngAInBridge.gd:7-9.
    
    For publication, Godot:
    
    1. Writes a temporary request inside the project.
    2. Executes:
    
       /usr/bin/python3 hermes_session_adapter.py --publish-request <temporary-path>
    
    3. The Python helper validates the request and live-listener lease.
    4. It hard-links the request into the external mailbox.
    5. Godot polls response.json.
    6. Godot uses --claim-response to consume the response through the adapter’s descriptor-bound claim implementation.
    
    Godot does not launch the persistent worker.
    
    3D ownership
    
    Python worker:
    
    /mnt/data-drive/godot_engain_3d_avatar/hermes_session_adapter.py
    
    Key constants:
    
    - DEFAULT_MAILBOX_ROOT:
      /mnt/data-drive/engain-runtime-mailboxes
    - CALLER_ID:
      dragon3d
    - request:
      /mnt/data-drive/engain-runtime-mailboxes/dragon3d/request.json
    - response:
      /mnt/data-drive/engain-runtime-mailboxes/dragon3d/response.json
    - listener lease:
      /mnt/data-drive/engain-runtime-mailboxes/dragon3d/listener.json
    
    Creation and claiming use the same pattern as 2D:
    
    - lease creation: hermes_session_adapter.py:1449-1455
    - request claim: hermes_session_adapter.py:1435-1447
    - parent creation: hermes_session_adapter.py:2590-2596
    
    3D Godot producer/consumer:
    
    /mnt/data-drive/godot_engain_3d_avatar/scripts/EngAInBridge3D.gd
    
    It explicitly declares:
    
    - project root at line 11
    - Dragon 3D mailbox root at line 12
    - request and response paths at lines 13-14
    - adapter path at line 15
    
    It publishes through the same provider-free Python helper boundary and then polls the response mailbox.
    
    
    2. REAL STARTUP COMMANDS
    
    2D current worker command
    
    The surviving current worker entry point is:
    
        cd /mnt/data-drive/engain_avatar
        python3 -u hermes_session_adapter.py \
          --project-dir /mnt/data-drive/engain_avatar
    
    The frozen provider and model default to:
    
    - provider: openai-codex
    - model: gpt-5.6-sol
    
    The explicit equivalent is:
    
        cd /mnt/data-drive/engain_avatar
        python3 -u hermes_session_adapter.py \
          --project-dir /mnt/data-drive/engain_avatar \
          --provider openai-codex \
          --model gpt-5.6-sol
    
    The separate 2D Godot command historically used is:
    
        godot --path /mnt/data-drive/engain_avatar
    
    The local godot command exists and resolves to:
    
        /home/mytruelove/applications/Godot_v4.6.1-stable_linux.x86_64
    
    Version:
    
        4.6.1.stable.official.14d19694e
    
    There is no current 2D composition launcher that starts the worker first, waits for readiness, launches Godot, and cleans
    up the worker afterward.
    
    Obsolete 2D commands
    
    The old sealed proof documented commands such as:
    
        python -u hermes_session_adapter.py \
          --project-dir /mnt/data-drive/engain_avatar \
          --state-file /tmp/engav0001-final6-state.json \
          --pid-file /tmp/engav0001-final6-adapter.pid
    
    Those exact commands are now obsolete.
    
    Current AdapterConfig requires --state-file, if supplied, to equal:
    
        /mnt/data-drive/engain_avatar/.godot/engain_hermes_session.json
    
    A /tmp/...state.json override now fails closed. The old proof command therefore should not be copied as the current
    startup command.
    
    The current persistent state file exists and records the accepted identity.
    
    There is also a stale 2D PID file:
    
        /mnt/data-drive/engain_avatar/.godot/engain_hermes_adapter.pid
    
    It contains PID 1668455, but that PID is no longer alive. This is not a permanent blocker: PidFileLock.acquire()
    detects a dead PID, removes the stale PID file, and retries. No such cleanup was performed during this read-only audit.
    
    3D canonical composed-runtime command
    
    Unlike 2D, 3D now has a real composition launcher:
    
    - /mnt/data-drive/godot_engain_3d_avatar/runtime_launcher.py
    - /mnt/data-drive/godot_engain_3d_avatar/runtime_composition.py
    
    Exact previously executed command:
    
        cd /mnt/data-drive/godot_engain_3d_avatar
        python3 runtime_composition.py \
          --godot-command /home/mytruelove/applications/Godot_v4.6.1-stable_linux.x86_64 \
          --project-dir /mnt/data-drive/godot_engain_3d_avatar \
          --shutdown-budget 5.0
    
    What it does:
    
    1. Acquires:
       .godot/engain_hermes_adapter.pid
    2. Constructs one in-process HermesSessionAdapter.
    3. Calls prepare().
    4. Requires worker_state == "READY".
    5. Starts one background servicing thread named:
       engain-hermes-mailbox-worker
    6. Launches Godot as a direct child:
    
           Godot_v4.6.1-stable_linux.x86_64 \
             --path /mnt/data-drive/godot_engain_3d_avatar
    
    7. Waits for Godot to exit.
    8. Requests worker stop.
    9. Removes the listener lease.
    10. Boundedly joins the service thread.
    11. Requires terminal STOPPED.
    12. Releases the PID lock.
    
    The audit evidence records that this command was run successfully on August 13, 2026:
    
    - launcher PID: 2663251
    - Godot child PID: 2663314
    - worker ready before Godot: pass
    - persistent worker servicing: pass
    - normal Godot exit: 0
    - launcher exit: 0
    - PID cleanup: pass
    - no remaining process: pass
    
    A later recorded run processed a real request:
    
    req_4168c47fc459dce168790ccf6e7d5b25
    
    Therefore the 3D composition is not merely a test double or an unexercised design.
    
    It is, however, currently untracked in Git:
    
    - runtime_launcher.py — untracked
    - runtime_composition.py — untracked
    
    A clean clone of godot_3d_avatar would not contain this launcher unless these working-tree components are preserved and
    promoted.
    
    
    3. READINESS-LEASE BEHAVIOR
    
    Both workers use the same filesystem lease shape:
    
        {
          "pid": <worker process PID>,
          "expires_at": <current Unix time + 2 seconds>
        }
    
    Lease duration:
    
        LISTENER_LEASE_SECONDS = 2.0
    
    Normal renewal cadence:
    
    - worker polling interval: 0.1 seconds
    - process_once() rewrites the lease before checking or claiming work
    - idle renewal is therefore approximately 10 Hz
    
    Publisher validation requires:
    
    1. listener.json exists.
    2. pid is a positive integer.
    3. expires_at is finite and still in the future.
    4. os.kill(pid, 0) confirms the PID exists.
    
    If validation fails, publication rejects immediately with:
    
        LISTENER_ABSENT: no live mailbox worker
    
    Other distinct mailbox states are:
    
    - MAILBOX_BUSY
    - MAILBOX_STALE
    
    Request lifetime:
    
        DEFAULT_CALL_LIFETIME_SECONDS = 185.0
    
    Provider timeout ceiling:
    
        MAX_HERMES_TIMEOUT_SECONDS = 180.0
    
    Important limitation
    
    Lease renewal occurs in the same thread that performs provider dispatch.
    
    When Hermes is running, process_once() may be blocked for as long as 180 seconds. During that period, the two-second
    listener lease expires because there is no independent heartbeat thread.
    
    The request is already renamed to a .processing claim, so additional publication normally observes a live pending call
    and returns MAILBOX_BUSY. But the lease does not mean “this worker remained continuously ready throughout provider
    execution.” It means “this worker recently reached its poll loop and its PID still existed.”
    
    2D shutdown behavior:
    
    - PID lock is released.
    - No explicit listener-file deletion exists.
    - The leftover lease becomes unusable after at most two seconds.
    - PID validation also rejects it immediately after the process exits.
    
    3D shutdown behavior:
    
    - request_stop() explicitly deletes listener.json.
    - The service thread is boundedly joined.
    - PID ownership is released after terminal STOPPED.
    
    Thus 3D has the stronger cleanup lifecycle.
    
    
    4. PROVIDER AND SESSION ASSUMPTIONS
    
    Both workers are hard-bound to the same companion identity:
    
    - companion: hermes_b
    - session ID: 20260731_065008_63a62d
    - provider: openai-codex
    - model: gpt-5.6-sol
    - Hermes executable:
      /home/mytruelove/.local/bin/hermes
    - expected Hermes executable SHA-256:
      e02455b2b8f5bb4dc9646c22bd1e6ca8869cd98aeb3b8b22e2c0840efaf1aa42
    
    The currently installed executable has exactly that SHA-256. That compatibility pin is currently satisfied.
    
    Persisted state:
    
    - 2D:
      /mnt/data-drive/engain_avatar/.godot/engain_hermes_session.json
    - 3D:
      /mnt/data-drive/godot_engain_3d_avatar/.godot/engain_hermes_session.json
    
    Both state files contain the same session ID, provider, model, and companion reference.
    
    3D additionally freezes:
    
    - Hermes profile: default
    - project: godot_3d_avatar
    - scene: res://scenes/Main.tscn
    - dragon scene: res://scenes/DragonAvatar3D.tscn
    
    3D invokes Hermes with the equivalent of:
    
        hermes -p default chat \
          -Q \
          --source tool \
          --pass-session-id \
          --ignore-rules \
          -t __engain_text_only_no_tools_v1__ \
          --provider openai-codex \
          -m gpt-5.6-sol \
          --resume 20260731_065008_63a62d \
          --no-restore-cwd \
          ...
    
    2D also resumes the frozen session, but its older path assumes the default Hermes profile rather than carrying the 3D
    worker’s explicit profile field.
    
    Both workers invoke Hermes directly. There is no provider-neutral dispatcher between the mailboxes and Hermes.
    
    
    5. COMPATIBILITY WITH ENGAIN PRESENCE/SESSION CLASSES
    
    Direct compatibility verdict:
    
        Not currently integrated.
    
    The external workers contain no imports or references to:
    
    - PresenceRegistry
    - SessionLedger
    - SharedSessionBridge
    - tier1.engainos
    
    PresenceRegistry compatibility
    
    External listener leases are not PresenceRecords.
    
    External lease fields:
    
    - pid
    - expires_at
    
    PresenceRecord fields:
    
    - agent_id
    - instance_id
    - session_id
    - capabilities
    - endpoint
    - lease_until
    
    Neither worker:
    
    - calls PresenceRegistry.register()
    - calls PresenceRegistry.renew()
    - calls PresenceRegistry.deregister()
    - exposes a PresenceRecord.endpoint
    - associates its filesystem lease with a Presence instance_id
    
    The external listener lease is therefore body/mailbox liveness, not provider Presence.
    
    SessionLedger compatibility
    
    Neither external worker appends requests or responses to SessionLedger.
    
    Instead:
    
    - 2D and 3D have separate persisted replay lists.
    - Each directly runs hermes chat --resume <same-session-id>.
    - Conversation continuity is delegated to Hermes’s own persisted session transcript.
    
    Consequences:
    
    - The two bodies may share Hermes conversational memory.
    - They do not share EngAIn’s in-memory SessionLedger.
    - EngAIn cannot read a complete cross-body turn ledger from these workers.
    - origin_body is not recorded in the EngAIn ledger.
    - EngAIn’s append-before-presence and response-actor validation invariants are bypassed.
    
    SharedSessionBridge compatibility
    
    The workers are not drop-in provider dispatchers for SharedSessionBridge.
    
    SharedSessionBridge expects a callable shaped like:
    
        provider_dispatch(
            PresenceRecord,
            List[Turn],
            player_input
        ) -> {
            "actor": ...,
            "response": ...
        }
    
    The external workers instead:
    
    - watch filesystem request schemas
    - invoke Hermes internally
    - write their own larger response schemas
    - include provider_session_ref
    - validate body-specific correlation and perception
    - do not accept a PresenceRecord
    - do not consume SessionLedger turns
    - do not return the bridge’s {actor, response} shape
    
    A compatibility adapter could be designed later, but it does not exist now.
    
    Cross-body concurrency limitation
    
    The 2D and 3D workers have separate:
    
    - mailbox directories
    - project PID locks
    - replay records
    - service loops
    
    Both can therefore invoke the same Hermes session concurrently. No shared lock or dispatcher serializes calls across
    dragon2d and dragon3d.
    
    That is materially different from one provider-neutral door with one active occupant.
    
    
    6. OTHER SEARCH ROOTS
    
    trixel3.2d
    
    Searched:
    
    /home/mytruelove/Desktop/burdens_of_a_forgotten_past/trixel3.2d
    
    Result:
    
    - no engain-runtime-mailboxes
    - no dragon2d
    - no dragon3d
    - no HermesSessionAdapter
    - no mailbox worker implementation
    
    Trixel3.2d does not own this runtime.
    
    Obsidian vault
    
    Searched:
    
    /home/mytruelove/Downloads/obsidianburdenNov25
    
    Result:
    
    - no external mailbox paths
    - no adapter startup commands
    - no runtime composition references
    - no worker implementation
    
    The vault is not a startup owner.
    
    Burdens workspace
    
    Searched:
    
    /home/mytruelove/Desktop/burdens_of_a_forgotten_past
    
    The active relevant findings remain:
    
    - EngAIn’s proof-only Presence/Ledger/SharedSession classes
    - external avatar repositories elsewhere under /mnt/data-drive
    - no in-tree launcher for those external repositories
    
    Audit repository
    
    /mnt/data-drive/engain-avatar-audit contains contracts, source snapshots, command transcripts, and live proof receipts.
    It does not own the current runtime implementation.
    
    
    7. CLASSIFICATION
    
    2D worker:
    
        EXTERNAL, PRESENT, MANUALLY STARTED,
        PARTLY STRANDED BEHIND OBSOLETE DOCUMENTED COMMANDS
    
    Why:
    
    - current implementation exists
    - current canonical persisted state exists
    - trusted Hermes hash matches
    - Godot executable exists
    - no combined 2D worker/Godot supervisor exists
    - old /tmp --state-file proof commands no longer satisfy current validation
    - stale PID file remains, although startup can recover it
    - mailbox/liveness edits are uncommitted
    
    3D worker:
    
        EXTERNAL, PRESENT, COMPOSED LAUNCHER SURVIVES,
        BUT LAUNCHER IS UNTRACKED
    
    Why:
    
    - real worker exists
    - real runtime composition exists
    - exact command was exercised successfully
    - Godot lifecycle and cleanup were proven
    - a later run processed a real request
    - runtime_launcher.py and runtime_composition.py are not committed
    - a clean clone does not reproduce the surviving launcher
    
    Mailboxes:
    
        ABSENT WHILE STOPPED, CREATED LAZILY BY WORKERS
    
    The missing /mnt/data-drive/engain-runtime-mailboxes directory does not mean the implementations are gone. It means
    neither worker currently owns a readiness generation.
    
    Presence/shared-session integration:
    
        NOT IMPLEMENTED
    
    The shared Hermes session ID proves provider transcript continuity. It does not prove EngAIn PresenceRegistry,
    SessionLedger, or SharedSessionBridge participation.
    
    
    8. REVISED SMALLEST LAUNCHER-RESTORATION PROPOSAL
    
    The earlier proposal to invent a new bridge host first was too broad. Real mailbox workers and one real 3D composition
    launcher already survive.
    
    The smallest process-restoration plan should reuse them rather than replacing them.
    
    Phase A: preserve the surviving source identities
    
    Before calling anything “supported”:
    
    1. Review and promote the intended 2D mailbox changes.
    2. Review and promote the intended 3D mailbox changes.
    3. Preserve runtime_launcher.py.
    4. Preserve runtime_composition.py.
    
    This is essential because the current working trees—not clean clones—contain the runtime being audited.
    
    Phase B: compose existing commands only
    
    A future outer launcher should supervise:
    
    1. EngAIn Tier-2 simulation:
    
           python3 -m tier2.godotsim.sim_runtime
    
    2. EngAIn Tier-1 AP/scene server:
    
           python3 tier1/engainos/launch_engine.py
    
    3. EngAIn FastAPI facade:
    
           python3 -m uvicorn tier1.engainos.engainos_server:app \
             --host 127.0.0.1 --port 8090
    
    4. Existing 2D worker:
    
           cd /mnt/data-drive/engain_avatar
           python3 -u hermes_session_adapter.py \
             --project-dir /mnt/data-drive/engain_avatar
    
    5. Existing 2D Godot project, only after validating the 2D listener.json lease:
    
           godot --path /mnt/data-drive/engain_avatar
    
    6. Existing 3D composed runtime as one child:
    
           cd /mnt/data-drive/godot_engain_3d_avatar
           python3 runtime_composition.py \
             --godot-command /home/mytruelove/applications/Godot_v4.6.1-stable_linux.x86_64 \
             --project-dir /mnt/data-drive/godot_engain_3d_avatar \
             --shutdown-budget 5.0
    
    The outer launcher should not separately launch a second 3D worker or second 3D Godot process; runtime_composition.py
    already owns both.
    
    Required readiness gates:
    
    - 8080: runtime health
    - 8765: listening process, since it has no /health
    - 8090: /api/health
    - 2D: valid live dragon2d/listener.json
    - 3D: valid live dragon3d/listener.json
    - corresponding Godot child processes present
    
    Required shutdown order:
    
    1. 2D Godot
    2. 2D worker
    3. 3D runtime_composition.py, allowing it to stop its own Godot and worker generation
    4. 8090 facade
    5. 8765 Tier-1 server
    6. 8080 Tier-2 runtime
    
    Scope warning
    
    That launcher would restore the currently surviving direct-Hermes runtime. It must not claim that PresenceRegistry,
    SessionLedger, or SharedSessionBridge are active.
    
    Making those classes authoritative is a separate integration change, not launcher restoration. It would require decisions
    about:
    
    - one persistent registry/ledger owner
    - filesystem mailbox-to-bridge adaptation
    - provider endpoint representation
    - cross-body provider-call serialization
    - Presence registration and renewal
    - response-actor revalidation
    - migration away from each worker directly invoking Hermes
    
    No implementation or source modification was performed.
