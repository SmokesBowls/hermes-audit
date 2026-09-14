# Provider-seat migration roadmap — planning only, nothing started

Captures the sequencing decided in conversation on 2026-09-14, for
when this track is resumed. **Nothing below has been implemented.**
This is a plan document, not a receipt.

## Where this picks up from

- Hotload proven (`09-13-2026-first-live-additive-hotload-proof.md`),
  durability now at n=2 same-process / n=3 content-continuous
  (`09-14-2026-repeated-turn-durability-skyfire-dragonsight.md`).
- Repository hygiene audited, discovery only, cleanup not yet done
  (`09-14-2026-repository-hygiene-audit-discovery.md`).
- Dragon's persistent scene-target instruction corrected and confirmed
  holding (`09-14-2026-dragon-scene-target-instruction-correction.md` +
  its session-attribution amendment).

## The two seats (recap, established terminology — not new here)

- **Dragon/Director seat** — `hermes_session_adapter.py`'s
  `HermesSessionAdapter`, session_id `20260731_065008_63a62d`. Runs
  with `-t __engain_text_only_no_tools_v1__` — **zero tools**. Produces
  `narrative_response` / `[EDITOR_REQUEST]`. Currently occupied by
  Hermes.
- **Builder/Editor seat** — `addons/hermes_editor/hermes_bridge.gd`.
  Full read/write/shell/test access; executes the actual DIRECT_WRITE
  mutation. A separate, in-memory-only session, currently also occupied
  by Hermes.

## How the sequencing was decided

First proposal: solve session-identity extraction *before* the
real import, reasoning that otherwise you risk "proving an installer
that accidentally carries your hardcoded Hermes identity with it, and
then we have to change the installer immediately afterward."

Correction (yours, adopted): that gets the rollback property backwards.
`godot_engain_3d_avatar` — the current testbed, with its proven,
already-working Hermes session — needs to stay the **known-good rescue
point** until the imported/installed copy is independently proven. If
the import blows up, you don't want to have already dismantled the
working Dragon to build it. So session-identity extraction becomes the
**last** step of the import (the cut-over), not a prerequisite.

New explicit rule that fell out of this: **while both projects
temporarily point at the same Hermes session, never run both Dragons at
the same time.** Two clients resuming the same conversation identity
concurrently are exactly the shape of hazard the presence/session
protections already built for this project exist to catch — at minimum
it muddies conversation history, possibly worse.

## Agreed sequence

```
1. Cleanup current project (godot_engain_3d_avatar)
   -> the 7-step plan in 09-14-2026-repository-hygiene-audit-discovery.md
2. Prove stability again (rerun the live durability loop; confirm
   nothing regressed from cleanup)
3. Import/install into the real game project
   -> original project (godot_engain_3d_avatar) is NOT touched or
      changed at this step -- it remains bound to session
      20260731_065008_63a62d, untouched, the rollback anchor
4. Temporarily test the imported copy using the SAME proven Hermes
   session identity -- but only with the ORIGINAL runtime shut down
   first (the concurrency rule above)
5. Prove the imported system works: Dragon + Builder + hotload +
   return loop, same acceptance-evidence standard used throughout this
   whole track (WorldComposition changed / Main untouched / HOTLOAD /
   TOOL return / Dragon reaction / same PID / prior objects preserved /
   HUD-session intact)
6. ONLY THEN: give the imported project its own fresh Hermes session
   identity -- this is the actual cut-over, not a prerequisite. The
   original project keeps the old session; the real game gets its own.
   This step is also a clean test of the INSTALLER itself: if the fresh
   Dragon immediately understands WorldComposition.tscn,
   [EDITOR_REQUEST], and the validation boundary, the installer is
   carrying the right things from bootstrap/architecture rather than
   from accidental knowledge that was only ever living in old session
   history. If it doesn't, that gap is exactly what's missing from the
   installer.
7. Re-test the imported project under its new, independent session
8. Confirm the original project can still resume the old Dragon session
   if needed -- the actual rollback check, not just a stated intention
9. Only after all of the above: begin provider-seat abstraction, one
   seat at a time, everything else frozen while changing one occupant
   a. Dragon/Director seat first -- zero tools today, so it's the safer
      chair to experiment with. Hermes -> Claude, prove stability; then
      potentially Hermes -> Antigravity, prove stability.
   b. Builder/Editor seat last -- real write/tool authority, the
      scarier chair. Only touched once the Dragon seat is
      provider-neutral and proven stable across at least one alternate
      provider.
```

Full pipeline, as agreed:

```
working Hermes/Hermes system
        |
        v
cleanup
        |
        v
prove stability
        |
        v
import/install into real game (original project untouched, stays bound
to its existing session as rollback anchor)
        |
        v
temporarily run imported copy on the SAME session (original runtime
shut down -- never both live at once)
        |
        v
prove imported system works
        |
        v
imported project gets its OWN fresh session identity (the actual
cut-over step; doubles as a test of whether the installer carries the
right bootstrap knowledge)
        |
        v
re-test imported project under its new session
        |
        v
confirm original project can still resume its old Dragon (rollback
proof)
        |
        v
Dragon seat: Hermes -> alternate provider, prove stability
        |
        v
Builder seat: Hermes -> alternate provider, prove stability
```

## Why this order, restated plainly

- Don't detach the working Hermes identity from the current project
  until the imported Dragon is independently proven — the original
  project is the lifeboat.
- Session-identity extraction is not "solve identity first, then
  import" — it's the final cut-over step of the import itself.
- This is deliberately *not yet* a provider change. Hermes still
  occupies every seat through step 8. Steps 9+ are the actual
  provider-neutrality work, and they come last, one seat at a time,
  cheapest/safest seat (Dragon, zero tools) before the dangerous one
  (Builder, full write access).
- The session-identity step should be boring: the existing Dragon
  keeps behaving exactly as it does now through the whole cleanup →
  import → prove-stability arc. It only gets a new identity at the
  explicit cut-over step, and only for the *new* installation — the
  current Dragon in `godot_engain_3d_avatar` remains the current
  Dragon, untouched, throughout.

## Status

Planning only. No cleanup executed, no import started, no session
identity touched, no provider seat changed. This document is the
resumption pointer for this track the next time it's picked up.
