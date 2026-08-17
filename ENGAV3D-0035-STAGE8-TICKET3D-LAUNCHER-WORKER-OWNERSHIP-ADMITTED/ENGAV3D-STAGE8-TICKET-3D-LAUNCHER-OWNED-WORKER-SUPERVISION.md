# ENGAV3D-STAGE8-TICKET-3D
# Launcher-Owned Persistent Worker Supervision Contract

**Status:** FROZEN OWNERSHIP CONTRACT; TICKET 3E IMPLEMENTATION NOT AUTHORIZED  
**Repository:** `/mnt/data-drive/godot_engain_3d_avatar`  
**Repository authority:** `77593c205851c97a1b0b46ebdb6ade270309f81a`  
**Provider executions authorized:** `0`

## 1. Decision

The runtime launcher/supervisor owns persistent-worker process supervision.
Godot consumes the already-available worker through the admitted mailbox boundary.
Godot does not spawn Python and does not directly terminate the adapter process.

```text
WORKER_SUPERVISION_OWNER=RUNTIME_LAUNCHER
GODOT_SPAWNS_PYTHON=FORBIDDEN
GODOT_DIRECTLY_STOPS_ADAPTER=FORBIDDEN
PROVIDER_IDENTITY_OWNER=FROZEN_ADAPTER_IDENTITY
```

This contract resolves the ownership choice left open by Ticket 3B. It does not
implement a launcher, choose an executable path, or wire runtime startup.

## 2. Normative upstream authority

This contract is downstream of and does not weaken:

- Stage 8 Ticket 1 persistent-worker/routing boundary;
- Stage 8 Ticket 2F explicit worker stop GREEN;
- Stage 8 Ticket 3A HUD/capture-order reconciliation;
- Stage 8 Ticket 3C Godot routing/HUD GREEN;
- the frozen identity, mailbox, replay, correlation, capture, and timeout rules.

## 3. Ownership split

| Concern | Sole owner | Forbidden owner |
|---|---|---|
| worker construction and preparation | runtime launcher/supervisor | Godot, HUD, provider |
| exclusive worker generation | runtime launcher/supervisor plus adapter ownership lock | mailbox existence, HUD submission |
| frozen provider/session identity | adapter validation and sealed state | launcher invention, Godot, provider prose |
| request routing and capture decision | Godot bridge under frozen routing contract | launcher, provider |
| request/response validation | admitted bridge and adapter boundaries | launcher reinterpretation |
| transient HUD state | bridge lifecycle, presented by HUD | launcher, provider prose |
| explicit worker stop request | runtime launcher/supervisor | Godot bridge, HUD |
| worker terminal state | adapter lifecycle observed by launcher | inferred mailbox emptiness |

The launcher supervises lifetime. It does not gain authority to alter routing,
mailbox bytes, provider identity, request correlation, capture identity, replay
state, conversation content, or HUD presentation.

## 4. Runtime generation

One launcher generation owns exactly one worker generation and at most one Godot
runtime generation.

```text
launcher generation starts
-> construct exactly one adapter worker instance
-> worker.prepare()
-> require worker state READY
-> start exactly one Godot runtime
-> generation ACTIVE

Godot submission 1 -> same worker instance
Godot submission 2 -> same worker instance
Godot submission N -> same worker instance

Godot runtime exits or launcher receives authorized shutdown
-> generation STOPPING
-> call request_stop() on that same worker instance
-> service worker lifecycle until STOPPED
-> require worker state STOPPED
-> generation CLOSED
```

A worker that reaches `STOPPED` is terminal. The launcher must not restart that
instance. Automatic replacement, retry, or restart requires a separate contract.

## 5. Readiness boundary

Worker readiness is established structurally by the launcher:

```text
worker.prepare() succeeds
AND
worker state == READY
AND
exclusive project-local ownership is held
BEFORE
Godot runtime becomes available
```

If readiness fails, Godot must not start. A running Godot process is therefore
evidence that its launcher generation previously admitted worker readiness, but
it is not authority to reconstruct worker identity.

Ticket 3D deliberately does not choose an external readiness representation.
No status JSON, readiness mailbox, socket, health endpoint, PID observation
protocol, or Godot polling mechanism is authorized here. Ticket 3E must first
attempt to prove structural ordering without inventing one.

## 6. Same-worker invariant

Every HUD submission admitted during one ACTIVE launcher generation is serviced
by the same prepared adapter instance and the same exclusive worker generation.
Fresh request identities do not imply a fresh worker.

The launcher must not infer sameness from mailbox existence, session ID alone,
PID text alone, or repeated successful responses. The implementation proof must
bind all submissions to the one instance constructed and retained by that
launcher generation.

## 7. Shutdown invariant

Godot shutdown clears only Godot/bridge transient status. It does not directly
stop Python.

The launcher observes Godot termination and owns this sequence:

```text
observe Godot terminal outcome
-> request_stop() on the same adapter instance
-> do not admit later requests
-> retain exclusive ownership through STOPPING
-> wait/service until worker state == STOPPED
-> release generation resources
-> exit
```

Mailbox files are not a shutdown protocol. Signal injection, deletion of mailbox
files, process killing as the normal path, and a second stop worker are forbidden.
Failure/timeout policy for a worker that cannot reach `STOPPED` remains a Ticket
3E RED/design question; this contract does not authorize an unbounded wait or a
silent success.

## 8. Strong prohibitions

Godot MUST NOT:

- invoke adapter `--once` per submission;
- invoke `process_once()` as its runtime worker;
- call `OS.create_process()` to construct the adapter;
- spawn a second adapter;
- invoke `request_stop()` on the adapter process;
- restart a `STOPPED` worker instance;
- infer worker identity or readiness merely because mailbox files exist;
- own provider, model, profile, companion, or session selection.

The launcher MUST NOT:

- start Godot before worker `READY` and exclusive ownership;
- construct more than one worker for a launcher generation;
- replace the worker after an ordinary request failure;
- route requests, allocate capture IDs, rewrite mailbox bytes, or interpret
  provider prose as lifecycle authority;
- report generation `CLOSED` before observing worker `STOPPED`.

## 9. Ticket 3E implementation gate

Ticket 3E may add the minimum launcher/runtime surface needed to prove this
contract. Its RED must determine concrete executable placement and startup
mechanics from the current repository rather than assuming them here.

Required future proofs:

```text
PERSISTENT_WORKER_AVAILABLE_TO_RUNTIME
-> READY and exclusive ownership precede Godot startup

SAME_WORKER_ACROSS_SUBMISSIONS
-> multiple sequential HUD/mailbox requests use the retained worker instance

RUNTIME_SHUTDOWN_REQUESTS_EXPLICIT_STOP
-> Godot exit causes launcher request_stop() on that instance and STOPPED is observed
```

The future offline integration proof must use zero real provider executions and
must cover one text-only request, one current-perception request, same-worker
identity, bridge-owned thinking lifecycle, and clean shutdown. A live Hermes
conversation test requires separate authorization after offline closure.

## 10. Non-goals

Ticket 3D does not authorize:

- launcher implementation or launcher tests;
- changes to Godot, adapter, project settings, or existing tests;
- provider execution or live HUD submission;
- external readiness/status protocol design;
- automatic worker restart, retry, queueing, or parallelism;
- multi-worker load balancing;
- changing the admitted routing, mailbox, response, capture, correlation, replay,
  timeout, or HUD lifecycle contracts;
- committing or cleaning the current working tree.

## 11. Final invariant

```text
one launcher generation
owns one prepared persistent worker generation
makes Godot available only after READY
retains the same worker across all submissions
and requests explicit stop after Godot terminates
until that same worker is STOPPED
```

Godot remains a mailbox consumer and presentation/runtime host. The launcher is
process-lifetime authority. The adapter remains provider/session and worker-state
authority. None may silently absorb another component's authority.
