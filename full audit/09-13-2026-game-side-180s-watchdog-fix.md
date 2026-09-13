# 09-13-2026 — Game's 180s mailbox watchdog fixed (third layer of the same bug)

## Trigger

After the provider/client timeout fix (240s/255s), live UI showed
`Mailbox timeout after 180.0 seconds.` followed by `stale response
claimed and discarded; no active lifecycle.` — the provider timeout fix
didn't make anything worse; it let the underlying call survive long
enough to expose the next timer outside it.

## Traced (discovery-only pass, confirmed before any code changed)

`scripts/EngAInBridge3D.gd:30` — `WAIT_TIMEOUT_SEC := 180.0`, the game
process's own outermost watchdog on a player-submitted turn (`submit()`
sets `_busy`/`_active_started_msec`; `_process()` compares elapsed time
against this constant). Mechanically confirmed, not inferred:
`_end_active_lifecycle()` clears `_active_request_id`/`_busy` at 180s;
`_poll_response_mailbox()`'s own stale-response gate then discards the
real `response.json` once it finally arrives (allowed up to 255s under
continuity dispatch) — reproducing the exact reported message sequence.

Also noted, not fixed: `hermes_session_adapter.py`'s own local-path
`MAX_HERMES_TIMEOUT_SECONDS` was *already* numerically equal to this
same 180.0 — a latent instance of the identical bug, predating this
session, just not yet observed as a symptom.

Confirmed: affects normal player turns only. The coordination-only
automatic path never sets `_busy`/touches `response.json` (uses the
separate `tool_events` channel by design), so it was never exposed to
this watchdog at all.

## Fix

`WAIT_TIMEOUT_SEC` is no longer a `const` literal — resolved once in
`_ready()` via `_compute_wait_timeout_sec()`, which reads the same env
vars the Python-side chain already uses (`ENGAIN_HERMES_TIMEOUT`,
`ENGAIN_CONTINUITY_PROVIDER_TIMEOUT_S`, `ENGAIN_CONTINUITY_TIMEOUT_MARGIN_S`
— visible here since this process is normally launched as a sibling of
the Python worker from the same shell) and computes
`max(local_timeout, continuity_client_timeout) + margin` — correct
regardless of which mode is configured, reusing the same 15.0 margin
already established for this chain. Default: `max(180, 255) + 15 =
270.0`.

## Proof

`tests/test_engainbridge3d_wait_timeout.gd`, run as three real separate
subprocess invocations (Godot's `OS` singleton has no `set_environment()`
a script could call to mutate its own env mid-process — each scenario
genuinely is a fresh process, same constraint the Python-side tests
already work within):

- defaults → `270.0` ✓
- continuity leg raised past local (`ENGAIN_CONTINUITY_PROVIDER_TIMEOUT_S=300`)
  → `330.0` ✓
- local leg raised past continuity's default (`ENGAIN_HERMES_TIMEOUT=400`)
  → `415.0` ✓

All three real, executed, passing — proving `max()` correctly picks
whichever side actually needs it, not just always returning one input.
Reran `addons/hermes_editor/test_hermes_bridge_logic.gd`: ALL CHECKS
PASSED, unaffected.

## Not touched, per instruction

Reload/SIGABRT, authority, status wording, scene construction, session
rotation.

## Still open, noted not fixed

`EngAInBridge3D.gd`'s `CALL_LIFETIME_SEC := 185.0` (sets the outgoing
request's `expires_at` — the abandoned-call staleness window) is now
also numerically smaller than the continuity client's own 255s timeout.
Not observed as a live symptom yet, not raised by the user, not fixed
here — flagged for awareness only, same category of issue, adjacent to
this fix's scope.
