# Repeated-turn durability — turns since the Violet proof

## Scope

Inspection only, no code changes. Covers every mailbox turn between the
Violet proof (`edit_id 20260913_225605_7461`) and now. Found **two**
new completed additive hotloads, not one:

1. `skyfire_orrery_12` → `edit_id 20260914_054628_9370`
2. `dragon_sight_toggle_13` → `edit_id 20260914_055945_3bb6`

No turns were missed in between (checked the full `coordination/consumed/`
and `outbox_handled/` listing by timestamp).

## Headline result

**Two consecutive additive hotloads now proven against one single,
continuously-running composed runtime process, with zero restart
between them** — this is the first time durability has moved past n=1.
A third, earlier hotload (Violet) chains into the same evidence via
file-hash continuity, but ran on a different (now-dead) process from
before this morning's runtime restart — see "PID continuity, precisely"
below for why that distinction matters and isn't blurred here.

## Per-turn acceptance evidence (same standard as the Violet proof)

### Turn 2: SKYFIRE_ORRERY_12

- **`WorldComposition.tscn` changed, `Main.tscn` untouched — independently, not from Dragon's report text.** Tamper-evident `EditReceiptStore` record (`edit_receipts/20260914_054628_9370/receipt.json`):
  - created: `scenes/SkyfireOrrery12.tscn`
  - modified: `scenes/WorldComposition.tscn`, **before_sha256 = `141b150f...ba49` — the exact `after_sha256` the Violet proof recorded.** `Main.tscn` does not appear in the changed-path set at all.
- **Editor report** (`coordination/consumed/editor_report.20260914_054944_fc1f...json`): `status: applied`, `files_modified: [WorldComposition.tscn]` only, both `packed_scene_load_and_instantiate` validation checks passed.
- **`[HOTLOAD]`/`[TOOL]`/`[DRAGON]` sequence** — confirmed directly from the user's own live screenshot, not taken from any report text: `[SYS] [HOTLOAD] added SKYFIRE_ORRERY_12 from res://scenes/SkyfireOrrery12.tscn`, `[TOOL] Request dragonreq_20260914_124617_aaa5725d: DONE — SkyfireOrrery12.tscn, WorldComposition.tscn updated; validation passed`, followed by a `[DRAGON]` reaction — message_id matches the mailbox file exactly (`dragonreq_20260914_124617_aaa5725d`).
- **Same PID, no restart**: runtime PID `2968110`, started `05:42:28`; this turn's report timestamp `05:49:45` postdates it with no intervening restart.
- **Prior objects preserved**: `WorldComposition.tscn`'s post-turn content still carries `FirstLightTower`, `RETURN-01`, `VERIFICATION_MONOLITH_04`, `LOAD_PROBE_DIAMOND_05`, `AMBER_CUBE_PROBE_08`, `VIOLET_CUBE_PROBE_11` — every prior transform byte-identical to the committed Violet-era version.
- **HUD/session intact**: same `ControlHUD` transcript, uninterrupted, per the screenshot.

### Turn 3: DRAGON_SIGHT_RIG_13 (the F1 toggle rig)

- **`WorldComposition.tscn` changed, `Main.tscn` untouched.** `edit_receipts/20260914_055945_3bb6/receipt.json`:
  - created: `scenes/DragonSightRig13.tscn`, `scripts/dragon_sight_rig_13.gd`
  - modified: `scenes/WorldComposition.tscn`, **before_sha256 = `d18fdd4b...3312f` — the exact `after_sha256` Skyfire's own receipt just recorded above.** `Main.tscn` absent from the changed-path set again.
- **Editor report** (`editor_report.20260914_060548_df56...json`): `status: applied`, `files_modified: [WorldComposition.tscn]` only, all three validation checks (`DragonSightRig13.tscn` load, `dragon_sight_rig_13.gd` script load, `WorldComposition.tscn` load) passed.
- **`[TOOL]` return**, from the mailbox's own tool-event record (`event_...ad29ec5b.json`): `Request dragonreq_20260914_125939_e743cad4: DONE — DragonSightRig13.tscn, dragon_sight_rig_13.gd, WorldComposition.tscn updated; validation passed`.
- **Same PID, no restart**: same runtime PID `2968110` — report timestamp `06:05:49`, still no restart since `05:42:28`, and none since either (checked: only one `godot --path ...` process exists right now, same PID).
- **Prior objects preserved**: current live `WorldComposition.tscn` on disk hashes to exactly `9adfb77b...ae977`, matching this receipt's own `after_sha256` — no drift since. All eight nodes present (six prior + `SKYFIRE_ORRERY_12` + `DRAGON_SIGHT_RIG_13`), prior six still transform-identical.
- **HUD/`[HOTLOAD]`/`[DRAGON]` — narrower evidence basis than turn 2, stated plainly**: this turn's report timestamp (06:05:49) is *after* the user's screenshot (06:00:08), so I have no independently-viewed HUD transcript line for this turn's `[HOTLOAD]`/`[TOOL]`/`[DRAGON]` sequence — only the mailbox tool-event record and the tamper-evident receipt above. Both are real, independently-checked artifacts (not Dragon's own prose), but they are not the same as seeing it appear live in the HUD the way turn 2 was confirmed. Flagging this rather than implying parity with turn 2's evidence.

## `Main.tscn`, checked across the whole span, not just per-turn

`Main.tscn`'s live on-disk hash (`45a37efb...e8b295`) is byte-identical
to the version committed in `ee418d4` (the original ownership-split
commit, Sept 13 night) — zero drift across the runtime restart and both
new turns.

## PID continuity, precisely

The runtime was restarted between the Violet proof and today's session
— expected and not a defect: Violet ran on PID `2719969` (started
Sept 13, 22:46:53, now dead), today's session runs on PID `2968110`
(started today, 05:42:28). That restart is a real process boundary, so
the honest claim is:

- **n=2, same process, zero restarts**: Skyfire → Dragon Sight Rig,
  both on PID `2968110`. This is new — the original proof was
  explicitly n=1.
- **n=3, content-continuous, one process boundary crossed**: Violet →
  Skyfire → Dragon Sight Rig chain via the unbroken before/after
  `WorldComposition.tscn` hash sequence, which proves nothing was lost
  or overwritten across the restart, but does not claim single-process
  uptime across all three.

## Incidental finding: the Sept 14 standing-instruction correction is visibly holding

Both new `[EDITOR_REQUEST]` bodies, generated by Dragon itself with no
prompting toward this specific wording, include verbatim: *"Instance
exactly one copy beneath the root of res://scenes/WorldComposition.tscn
... Do not create, modify, or instance anything in
res://scenes/Main.tscn."* This is the first live evidence, since the
correction was sent, that the generating session is producing correctly
-targeted requests on its own — consistent with, though not the same
formal acceptance test as, the live probe explicitly deferred earlier.

## Also observed, not investigated (out of scope here)

Dragon's own transcript message flags a real, pre-existing ordering
note on its own: `[SYS] [HOTLOAD]` prints before the correlated
`[TOOL]` confirmation arrives, so a hotload announcement can visually
precede its own verification. This is Dragon noticing existing behavior,
not something newly found here, and no code was touched for it.

## Repository state note

None of this is committed yet. `git status` in `godot_engain_3d_avatar`
currently shows `WorldComposition.tscn` modified and
`SkyfireOrrery12.tscn`/`DragonSightRig13.tscn`/`dragon_sight_rig_13.gd`
(+`.uid`) untracked, plus new untracked `snapshots/` capture pairs from
the ongoing live session — this is in-progress live state, not yet a
commit boundary, and this receipt does not create one.

## Status

Discovery/verification only. No code changed, nothing committed to the
game repo, no live probe initiated by me — all evidence above comes
from turns the user already ran while I was doing the hygiene audit.
