# Continuation TODO Status Update — Item 4 Complete

Written 2026-08-17, after both phases of item 4 were pushed. This is a
status update against `08-17-2026-continuation-todo.md`, not a rewrite of
it — that file stays as the original record of what was open and why;
this note records what changed since.

## Item 4 — closed

> "Real Godot launch through this same integration ... hasn't been
> attempted."

Attempted, diagnosed, fixed, and proven live, in two separate phases:

- **Phase 1** — `08-17-2026-dragon3d-launch-wrapper-phase1-proof.md`.
  Root cause: nothing invoked `runtime_composition.py`; Godot was being
  started as a bare binary. Fix: `launch_dragon3d.sh`
  (`godot_engain_3d_avatar` commit `6f86cc4`), the new canonical
  entrypoint. No defect found in `runtime_composition.py`,
  `runtime_launcher.py`, the presence authority, or the Hermes adapter.
- **Phase 2** — `08-17-2026-listener-absent-structured-diagnostic-phase2-proof.md`.
  `LISTENER_ABSENT` now carries a structured diagnostic
  (`ListenerAbsentError`, `godot_engain_3d_avatar` commit `90fc568`)
  rendered by the HUD into actionable operator text, pointing at
  `launch_dragon3d.sh` by name — sourced from the adapter, never
  hard-coded into GDScript.

Both phases pushed:

- `godot_3d_avatar` (`godot_engain_3d_avatar`): `57122cd..90fc568` —
  `6f86cc4`, `90fc568`.
- `hermes-audit` (this repo): `2429840..4c85f54` — `608879d`, `4c85f54`.

Working discipline held: normal fast-forward pushes only, no force/
rewrite; both repos were `0 behind` their upstream before pushing.

## Remaining open items — unchanged, still in the order the original
## TODO put them

1. Concurrent-`/dispatch` mutex for overridden bindings — not started.
2. Ledger/cursor persistence across a restart — not started.
3. Production cutover decision — not made.
4. ~~Real Godot launch through this integration~~ — **done, see above.**
5. `provider_session_ref`'s frozen-identity limitation — not fixed, still
   just named.

Item 1 is next: explicitly scoped as design/re-derivation first (what
actually has to be mutually exclusive, and whether that means extending
`SessionClaimRegistry` or a dispatch-serialization primitive of its own)
before any implementation, per the same "flag for review before
implementing, this changes a contract" caution the original TODO already
put on it.
