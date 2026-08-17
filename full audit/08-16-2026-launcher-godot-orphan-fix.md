# Launcher Godot-Orphan-on-Interrupt Fix

Written 2026-08-16, immediately following the presence authority
operationalization pass, which surfaced this as an honest, unfixed finding:
`SIGINT` to `runtime_composition.py` raised a bare `KeyboardInterrupt`
inside `godot_process.wait()`; the worker→authority shutdown ordering still
ran correctly through the `finally` chain, but Godot itself was left
running and had to be killed by hand. Reclassified from "unrelated
convenience" to launcher lifecycle correctness: the launcher started
Godot, so it owns stopping it.

## What changed

`runtime_launcher.py`:
- New `ShutdownRequested(BaseException)` — SIGTERM funnels through it, into
  the exact same shutdown path SIGINT's default `KeyboardInterrupt`
  already used.
- `GodotProcess` Protocol extended with `poll`/`terminate`/`kill` (was
  `wait`-only).
- `run_runtime_generation` gains a required `godot_terminator` parameter
  (no default — this module has no concrete subprocess implementations,
  consistent with its existing style). On `(KeyboardInterrupt,
  ShutdownRequested)` from `godot_process.wait()`: stop the worker first,
  then call the terminator, then re-raise — never swallowed, so the caller
  preserves the interruption.

`runtime_composition.py`:
- `terminate_and_reap_godot(process, shutdown_budget_seconds)`: already-dead
  check via `poll()` (still reaped via `wait()` either way), graceful
  `terminate()`, bounded `wait(timeout=...)`, escalate to `kill()` only on
  timeout, final `wait()` always called. Operates only on the exact `Popen`
  object `create_godot_process()` returned — no PID/name lookup, no
  process-group-wide signal, so it can never reach a process this
  generation didn't start. Idempotent by construction (`Popen` caches
  `returncode` after the first successful `wait()`/`poll()`).
- `run_concrete_runtime` threads `godot_terminator` through, defaulting to
  the real implementation.
- `main()` installs a `SIGTERM` handler (raises `ShutdownRequested`) around
  the run, catches `KeyboardInterrupt`/`ShutdownRequested` and returns
  `128 + signum` (130 / 143) instead of letting an uncaught exception print
  a traceback and return a generic code, and restores the previous SIGTERM
  handler in a `finally`.

Ordering enforced, both by construction and tested: **stop worker → release
session/presence (a consequence of stopping the worker — the service loop
finishes its current cycle, which is exactly where
`hermes_session_adapter.py`'s own dispatch `finally` releases any held
claim, before `request_stop()` returns) → terminate and reap Godot →
release ownership → stop the presence authority, last.**

## Byte-preservation pins re-sealed, not silently bypassed

`test_stage8_ticket3f_runtime_composition_red.py` pins sha256 hashes for
`runtime_launcher.py` and `test_stage8_ticket3e_launcher_supervision_red.py`.
Both were deliberately recomputed against the new, reviewed contents and
the pin constants updated with a comment explaining why — not regenerated
mechanically to make a failing assertion disappear.

`test_stage8_ticket3e_launcher_supervision_red.py`'s existing fakes needed
a no-op `godot_terminator` supplied to keep working, since it is now a
required parameter; none of that file's own tests interrupt
`godot_process.wait()`, so the terminator they supply is never actually
invoked — confirmed by it not appearing in any of those tests' expected
call sequences.

## Tests — one per acceptance-criteria scenario

`test_launcher_interrupt_lifecycle.py`, 11 tests:

- `test_already_dead_godot_is_reaped_not_signaled`
- `test_graceful_terminate_is_tried_first_and_suffices`
- `test_graceful_timeout_escalates_to_kill`
- `test_repeated_cleanup_is_idempotent`
- `test_interrupt_stops_worker_before_terminating_godot_and_reraises`
  (parametrized over both `KeyboardInterrupt` and `ShutdownRequested` —
  proves both signals take the identical path)
- `test_normal_godot_exit_never_calls_the_terminator`
- `test_full_interrupt_chain_preserves_required_ordering_and_reraises`
  (through `run_concrete_runtime` with fakes for worker/ownership/service/
  authority — asserts the four-step index ordering directly)
- `test_main_translates_keyboard_interrupt_to_128_plus_sigint`
- `test_main_translates_shutdown_requested_to_128_plus_sigterm`
- `test_main_restores_the_previous_sigterm_handler`

## Real launcher interruption proof

Started the real composed launcher exactly as in the earlier operationalization
proof (`--presence-authority-script` pointed at the real EngAIn checkout,
real Godot, real worker). Captured the Godot child PID
(`657723`) from `pgrep` before interrupting. Sent a real `SIGINT` to the
launcher process. Result, no manual cleanup performed this time:

```
Godot PID before interrupt: 657723
...
=== Godot PID 657723 still exists? ===
gone — no manual cleanup performed
=== any Godot process at all? ===
none
=== authority port ===
closed
=== listener lease ===
(empty — cleared)
=== PID lock ===
No such file or directory
```

Compare to the earlier operationalization proof, where the identical
interruption left Godot running and required a manual `kill`. Same
scenario, fixed outcome.

**Honest limitation of this specific live check:** the launcher's exact
numeric exit status (128 + `SIGINT` = 130) was not captured from this
particular backgrounded run — `wait` on a PID backgrounded in an earlier,
separate shell invocation isn't reliable across this tool's per-call shell
boundaries. The exit-status translation itself is directly unit-tested
(`test_main_translates_keyboard_interrupt_to_128_plus_sigint`, passing)
and not otherwise in question; this is a gap in this one proof's
observability, not a gap in what was verified overall.

## Regression, all three code repos

`godot_engain_3d_avatar`: 251 passed (240 + 11 new) / 3 failed — identical
pre-existing Stage 8 Ticket 3B RED failures, unrelated to any file touched
today. `engain_avatar`: 77/77, unaffected — no file in that repo was
touched by this fix. EngAIn: 183/183, unaffected — no file in that repo
was touched by this fix.

## Correction to the prior receipt

`08-16-2026-presence-authority-operationalization.md` has been amended in
place: Godot consuming the mailbox response in that day's composed proof
established that the live path was real and active, not the exact content
of the response. The rejection itself was, and remains, established by the
presence authority's own `409` on the second `/claim` and the adapter's
`SESSION_OCCUPIED` log line — both quoted in that document, unchanged.
