# Perception blindness as an engine state, not a model instruction — design, nothing implemented

Design conversation from 2026-09-14. **Nothing below has been
implemented.** Companion to
`09-14-2026-provider-seat-migration-roadmap.md` — this hardens the
perception boundary that matters most once the Dragon/Director seat
starts accepting alternate providers (step 9a of that roadmap).

## What exists today, verified against the actual code (not assumed)

- `scripts/EngAInBridge3D.gd` already has a real lifecycle machine:
  `STATUS_IDLE` / `STATUS_LOOKING_INTERNAL` / `STATUS_THINKING`
  (lines 72-74), a `status_changed(status: String)` signal (line 7),
  and `_set_lifecycle_status()` (line 711) as the single place that
  transitions and emits it.
- The capture-unavailable seam already exists and already hard-stops
  the turn: `_run_dragon_turn()`'s live-capture branch
  (`EngAInBridge3D.gd:285-294`) — `if capture_status != "full":
  _end_active_lifecycle(); _emit_err("Live viewport capture is
  unavailable; Runtime Dragon was not invoked."); return`. Today, an
  unavailable capture **never reaches Dragon at all** for this path —
  this is the exact seam the design below hardens, not a new gap being
  discovered.
- Separately, `hermes_session_adapter.py`'s `_format_messages()`
  (~line 1302-1311) has a **prose fallback** for whatever calls do
  reach the adapter without a usable perception attached:
  `PROVENANCE=UNAVAILABLE_OR_UNVERIFIED` / "No current viewport image
  is attached for this request... Do not claim to see current artwork,
  objects, colors, positions, or UI from pixels... Identify prior facts
  only as conversation memory." **This is the weak pattern the design
  replaces** — telling the model in English that it's blind, rather
  than the model structurally never receiving the evidence.

## The correction made to the first framing

Initial framing treated blindness as another phase alongside `IDLE`/
`THINKING`. Corrected: blindness is a **capability condition** that can
persist while the system is otherwise idle, thinking, or handling text
— not a lifecycle phase. So it's a second, orthogonal axis Godot owns,
not a fourth value slotted into the existing one:

```text
Lifecycle:              Perception capability:
IDLE                     SIGHTED
LOOKING_INTERNAL         BLIND
THINKING
```

## The state machine

```text
viewport capture failure
        ↓
Godot validates failure
        ↓
perception_state = BLIND
        ↓
emit perception_state_changed(BLIND, reason)
        ↓
physical/runtime systems react

BLIND
  ↓
next correlated capture succeeds
  ↓
Godot validates capture
  ↓
perception_state = SIGHTED
  ↓
emit perception_state_changed(SIGHTED)
```

No English sentence telling the model it can't see. Consequences are
structural instead:

- no viewport image exists for that turn;
- visual/perception-dependent capabilities are unavailable;
- anything requiring fresh rendered evidence fails closed;
- the HUD can visibly show `BLIND`;
- Dragon may still converse from nonvisual knowledge if desired;
- `@tool` can still inspect structural/project evidence — structural
  sight is a different channel (same distinction already recorded in
  `DRAGON_SCENE_UNDERSTANDING_CHANNELS.md`: rendered pixels vs. project
  structure are separate evidence classes, and session/history is not
  sensory freshness);
- nothing can promote structural evidence into "I see this rendered
  right now."

The model is never responsible for deciding, or being told, whether it
can see.

## Why this matters more once the driver seat becomes provider-neutral

Hermes, Claude, and Antigravity may each respond differently to a
prompt saying "pretend you didn't see X." They cannot respond
differently to **X never being supplied to their seat at all.** So the
governing invariant is:

> A provider does not enforce its own sensory boundary. EngAIn decides
> which evidence channels physically exist for that turn.

That's engine-level governance instead of prompt compliance — and it's
provider-neutral by construction, which is exactly the property step 9
of the migration roadmap needs from every subsystem it touches, not
just this one.

## Also proposed

Put `BLIND`/`SIGHTED` on Godot's internal signal bus (alongside the
existing `status_changed`) so other systems can subscribe —
Dragon-Sight UI dimming, sensor-dependent actions disabling, a visual
fault indicator — without adding another sentence to an LLM prompt for
any of them.

## Status

Design only. `perception_state`, `SIGHTED`/`BLIND`, and
`perception_state_changed` do not exist in the codebase yet. No code
changed. This document is the resumption pointer for this specific
design the next time it's picked up — likely alongside or just before
the provider-seat migration roadmap's step 9a (Dragon seat: Hermes →
alternate provider), since that is exactly when this invariant starts
paying for itself.
