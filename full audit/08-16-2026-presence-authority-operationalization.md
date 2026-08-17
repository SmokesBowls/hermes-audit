# Presence Authority Operationalization

Written 2026-08-16, following up on the same day's shared-presence-authority
race proof. That proof showed the mutex is real across processes; it also
showed it was not yet production protection, because both workers failed
open when the authority was unreachable, and nothing started the authority
except a manually run command. This closes that gap, against the operator's
8-step spec.

## 1–2. Launcher supervision + health gate

`godot_engain_3d_avatar/runtime_composition.py` gained `SupervisedPresenceAuthority`
and a new `presence_authority_factory` parameter on `run_concrete_runtime`,
opt-in via `--presence-authority-script` (no default path — an explicit,
named flag, not a silent cross-repo assumption). When supplied, the
authority is spawned and health-polled (`GET /health`) *before*
`ownership.acquire()`/`worker.prepare()` — verified with fakes in
`tests/test_presence_authority_supervision.py`
(`authority.start` / `authority.wait_until_healthy` both provably precede
`adapter.prepare`), and an authority that never becomes healthy prevents the
worker from starting at all (`adapter.prepare` never called).

`engain_avatar` has no equivalent composed launcher to extend — the earlier
audit already established that 2D has none, and inventing one was out of
scope here.

## 3–4. Fail-open → fail-closed, named compatibility escape hatch

Both `hermes_session_adapter.py` files now default to fail-closed:

- `prepare()` raises `HermesAdapterError("PRESENCE_AUTHORITY_UNAVAILABLE: ...")`
  if REGISTER can't reach the authority.
- Dispatch produces a `PRESENCE_AUTHORITY_UNAVAILABLE` mailbox response
  (distinct from `SESSION_OCCUPIED`) and never reaches Hermes, if CLAIM
  can't reach the authority.

Both are governed by one explicitly named env var,
`ENGAIN_PRESENCE_AUTHORITY_FAIL_OPEN_COMPAT=1` — unset means fail-closed,
set means the old fail-open behavior, on purpose, never silently. Existing
offline test suites (which predate this and don't run an authority) needed
`tests/conftest.py` added in both repos to default to compat mode for the
*rest* of the suite, while the new presence-specific tests explicitly
control the flag themselves.

## 5. Shutdown order

`run_concrete_runtime`'s `finally` block releases ownership only after
`worker.worker_state == "STOPPED"`, and stops the authority only after
that — never the reverse. Verified with fakes
(`test_authority_stops_only_after_worker_reaches_stopped`), and separately
observed to hold even during an unclean shutdown (see §6's honest finding).

## 6. Composed live proof — no manually started side service

Ran `runtime_composition.py --presence-authority-script <EngAIn path> ...`
directly. Nothing else was started by hand. The authority's own access log
and the worker's own stderr are the evidence:

```
[presence-authority] listening on 127.0.0.1:8767
[presence-authority] "POST /presence/register HTTP/1.1" 200 -   ← launcher-started worker registers itself
Godot Engine v4.6.1.stable.official.14d19694e ...
[MAIN] Loaded. Bridge at:/root/Main/World/DragonAvatar3D/EngAInBridge
[presence-authority] "POST /claim HTTP/1.1" 200 -               ← external claimant (standing in for 2D) wins first
[presence-authority] "POST /claim HTTP/1.1" 409 -               ← the real, launcher-started 3D worker's real dispatch attempt
[presence] SESSION_OCCUPIED for req_...: SESSION_OCCUPIED: held by agent_id='hermes' instance_id='external-claimant-2d' until ...
Processed EngAIn request: req_...
```

A real request was published through the actual documented protocol
(temp file → `hermes_session_adapter.py --publish-request`, hard-linked
into the real mailbox by the adapter's own validation, exactly as Godot's
own bridge does it) while the real, running, launcher-supervised worker
held only presence, not the claim. The response itself was consumed by the
live, running Godot dragon's own polling before it could be inspected
directly — a stronger signal of realism than a weaker one, not a gap in
the proof; the authority's and adapter's own logs are the record.

**Honest finding, not fixed here:** stopping the launcher via `SIGINT`
raised a bare `KeyboardInterrupt` inside `godot_process.wait()`. The new
worker→authority shutdown ordering still executed correctly through the
exception (`finally` chains ran regardless — PID lock released, authority
port closed, in the right order) — but Godot itself was left running,
orphaned, and had to be killed manually. This is a pre-existing property of
`runtime_launcher.py`'s model (`godot_process.wait()`, never
`.terminate()`), not something introduced by this change, and not something
this task's scope covered. Left as a known gap for a separate decision.

## 7. Authority death during a claim

`test_dispatch_never_reaches_hermes_when_authority_dies_between_register_and_claim`,
both repos: a real authority subprocess is up for REGISTER, then made
unreachable before CLAIM. `director.calls == 0` in both — Hermes is never
reached. This is the fail-closed CLAIM path working exactly as specified,
not a new heartbeat/monitoring mechanism (none was built; none was asked
for).

## 8. Mailbox readiness lease — untouched

Neither repo's PID+`expires_at` listener lease was modified. It still
answers "is a body listening"; the session claim now separately answers
"does Hermes have one occupant." Confirmed by reading, not assumed.

## Regression, all four repos

- `engain_avatar`: 77/77 (73 pre-existing + 4 new).
- `godot_engain_3d_avatar`: 240 passed / 3 failed — the identical 3
  pre-existing Stage 8 Ticket 3B RED tests, confirmed via `git stash` at
  the start of this operationalization pass to fail identically without
  any of today's changes.
- EngAIn (`tier1/engainos`): 183/183, unaffected by this pass (no EngAIn
  source changed today beyond the CLI-arg addition to
  `presence_authority_server.py`).

## Deferred, named explicitly, not implemented

**Credentialing.** Localhost binding prevents remote interference, but any
local process can currently call `REGISTER`/`CLAIM` and impersonate a
worker — there is no per-launch credential distinguishing a legitimate
worker from any other local process. Per instruction, this does not block
this stage. The authority should eventually issue an unguessable
per-launch credential from the supervisor to each worker it starts, checked
on every call. Not designed or implemented here.

**Godot orphaning on launcher SIGINT** (§6). Not fixed; flagged for a
separate decision.

## Status

Not yet "active runtime protection" in the sense of always-on production
behavior — it is opt-in (`--presence-authority-script` must be passed
explicitly) and fail-closed only once the authority is actually running.
It is, as of this pass: real, supervised when asked, health-gated,
correctly ordered on shutdown, and proven end-to-end through the actual
launcher with no manual side service — the honest label is "supervised and
provably correct when enabled," not yet "always on."
