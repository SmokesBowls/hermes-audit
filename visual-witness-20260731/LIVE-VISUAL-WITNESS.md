# ENGAV-0001 Live Visual Witness

Witness date: 2026-07-31

Repository: `/mnt/data-drive/engain_avatar`

Sealed proof commit: `f00ff0424f714726f024c0d763b741f61dfc8178`

Annotated tag: `engav-0001-hermes-embodiment-proof`

## Why this witness matters

This is the first preserved interactive graphical run after the ENGAV-0001 proof was sealed. Unlike the headless acceptance harness, the user launched the actual Godot project, typed directly into the visible LineEdit, and observed the dragon's responses in the running avatar.

The run demonstrated:

- stale response rejection at startup;
- two-turn Hermes continuity through the visible avatar;
- contextual continuation beyond the fixed nonce exchange;
- SnapshotManager capture during actual graphical rendering;
- bounded timeout behavior without mutation authority.

## Commands

Godot was launched interactively with:

```bash
godot --path /mnt/data-drive/engain_avatar
```

The active adapter process was launched from the repository as:

```bash
python hermes_session_adapter.py
```

Its working directory was `/mnt/data-drive/engain_avatar` and its PID at preservation time was `1443331`.

## Hermes continuity state

The adapter's persisted live session was:

```text
session_id: 20260731_065008_63a62d
```

The captured state lists five processed request IDs. A byte-preserved copy is stored as `engain_hermes_session.json` in this witness directory.

## Exact visual nonce exchange

Turn 1 input:

```text
Remember this exact token for our next exchange: DRAGON-VISUAL-9A42. Reply with only: TOKEN STORED
```

Visible dragon response:

```text
TOKEN STORED
```

Turn 2 input:

```text
What exact token did I ask you to remember? Reply with only that token.
```

Visible dragon response:

```text
DRAGON-VISUAL-9A42
```

The corresponding SnapshotManager event captures are:

```text
snapshots/low_ai_dragon_spoke_2026-07-31T06_50_50.png
snapshots/low_ai_dragon_spoke_2026-07-31T06_50_50.json
snapshots/low_ai_dragon_spoke_2026-07-31T06_51_14.png
snapshots/low_ai_dragon_spoke_2026-07-31T06_51_14.json
```

The JSON records contain the exact spoken-event texts `TOKEN STORED` and `DRAGON-VISUAL-9A42`, Godot 4.6.1 identity, scene path, timestamps, and zero `reality_entropy`. Independent pixel inspection confirms that the PNGs capture the running graphical avatar scene and dragon, but the speech label had already returned to initialization/awaiting state (and the LineEdit showed `EngAIn is thinking...`) at image capture time. The PNG pixels therefore prove graphical runtime context, while the terminal transcript and JSON event payloads prove the exact responses; the PNGs must not be represented as visibly rendering those response strings.

## Contextual continuation

The next input was:

```text
hi
```

The visible response was:

```text
The constellation-wrapped dragon wakes one star at a time. It studies you, then carefully imitates your brevity.

"Hi."

A new constellation forms along its throat: DRAGON-VISUAL-9A42—the token you taught the interface to remember. The dragon glances toward it, pleased with itself.

"I kept your sign," it says. "May I keep a name for you, too?"
```

This is significant because it demonstrates continuity in a free-form third turn, not only compliance with the two fixed acceptance prompts. Its graphical-context and metadata witnesses are:

```text
snapshots/low_message_received_2026-07-31T06_51_45.png
snapshots/low_message_received_2026-07-31T06_51_45.json
snapshots/low_ai_dragon_spoke_2026-07-31T06_52_10.png
snapshots/low_ai_dragon_spoke_2026-07-31T06_52_10.json
```

As with the nonce captures, the PNG shows the running avatar scene rather than the full free-form response text; the exact response is preserved in the JSON event payload and user-supplied terminal transcript.

## Bounded timeout witness

The next input was:

```text
describe what you see
```

The provider exceeded its bounded budget. The visible response was:

```text
Hermes timed out. The dragon is still here; please try again.
```

This did not invalidate continuity. It exercised the intended bounded failure path and returned an inert observation response rather than state, entropy, action, or canon authority. Its witnesses are:

```text
snapshots/low_message_received_2026-07-31T06_52_26.png
snapshots/low_message_received_2026-07-31T06_52_26.json
snapshots/low_ai_dragon_spoke_2026-07-31T06_52_57.png
snapshots/low_ai_dragon_spoke_2026-07-31T06_52_57.json
```

## Startup stale-response witness

At startup, Godot found a pre-existing response file and emitted:

```text
📥 Found AI response file!
⚠️ Ignored stale or mismatched EngAIn response
```

This is positive adversarial evidence: a response not correlated to an active visible request was not spoken by the dragon.

## Preserved artifacts

This directory contains:

- the user-supplied terminal transcript in `USER-TERMINAL-TRANSCRIPT.txt`;
- the live Hermes session state;
- a consistent SQLite backup of `engain_memory.db` at witness time;
- all 15 SnapshotManager files present during the run;
- `SHA256SUMS` for byte verification;
- this witness report.

The snapshot metadata declares a four-hour retention window, so copying it outside the runtime snapshot directory was necessary for durable preservation.

## Repository drift warning

Launching Godot 4.6.1 changed tracked `project.godot` bytes:

```diff
+[animation]
+
+compatibility/default_parent_skeleton_in_mesh_instance_3d=true
+
-config/features=PackedStringArray("4.4", "GL Compatibility")
+config/features=PackedStringArray("4.6", "GL Compatibility")
```

This is runtime/editor migration drift, not ENGAV-0001 implementation. It is not included in the sealed proof commit and must not be committed as part of this witness. The earlier five `.import` drift files also remain separate.

## Scope statement

This witness preserves evidence only. It does not alter the sealed ENGAV-0001 commit or tag, does not promote SnapshotManager behavior into ENGAV-0001 scope, and does not authorize world-state, entropy, rendering, or canon mutation by Hermes.
