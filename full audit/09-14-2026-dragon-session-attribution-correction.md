# Amendment — which session the scene-target correction actually reached

## Trigger

User asked, before marking the correction complete: did the fix reach
the instruction source Dragon uses to *generate* `[EDITOR_REQUEST]`, or
only the Hermes Editor *execution* session — and to say so plainly if it
was only the latter.

## Finding, checked against code and the live session store, not assumed

**The earlier receipt's own attribution was wrong.** It called
`session_id 20260731_065008_63a62d` (from
`.godot/engain_hermes_session.json`) "the same resumed Hermes Editor
session the dock uses." That is incorrect. Grepped both addon files for
the filename directly:

```
grep -n "engain_hermes_session" addons/hermes_editor/hermes_dock.gd
addons/hermes_editor/hermes_bridge.gd
-> zero matches in either file
```

That state file is defined and read/written exclusively inside
`hermes_session_adapter.py` (`fixed_state_file = project_dir /
".godot" / "engain_hermes_session.json"`). `hermes_bridge.gd`'s own
session_id is a plain in-memory Node property, never persisted to that
file or any other — its own comment says so directly ("in-memory Hermes
session_id — do not have to be destroyed/recreated"). These are two
separate Hermes conversations, not one:

| | Generating side (`hermes_session_adapter.py` → `HermesSessionAdapter`) | Execution side (`addons/hermes_editor/hermes_bridge.gd`) |
|---|---|---|
| Session identity | Persisted, `.godot/engain_hermes_session.json`, `20260731_065008_63a62d` | In-memory only, unknown to any file on disk |
| Tools | `-t __engain_text_only_no_tools_v1__` — a deliberately unknown toolset name, resolving to **zero tools** | Full read/write/shell/test access (SAFE/REVIEW or DIRECT_WRITE) |
| Role | Produces `narrative_response`, which `_extract_editor_directive()` scans for the `[EDITOR_REQUEST]` block — this is literally the code path that generates it | Receives the extracted `[EDITOR_REQUEST]` body as its message text and performs the actual file mutation |
| Can it write scene files itself? | No — no tools at all, text-only reasoning provider | Yes — this is its entire purpose |

Independent corroboration that these are genuinely different sessions,
not just differently described: `DRAGON_SCENE_UNDERSTANDING_CHANNELS.md`
(2026-08-23) records a resumed **Editor** session id
`20260823_122123_e96802` — a different ID entirely from
`20260731_065008_63a62d`, on the same date range this project has been
running both seats.

## What this means for the correction already sent

The 2026-09-14 correction was sent with `--resume
20260731_065008_63a62d` — the generating side's own persisted identity,
not the Editor's. That is the session whose output feeds
`_extract_editor_directive()`, i.e. **the actual source of
`[EDITOR_REQUEST]` text**. So the correction reached the right
instruction source the first time; the earlier receipt just named the
wrong owner for it. No second correction message was needed or sent.

Re-verified directly against `~/.hermes/state.db` just now: message id
49609 (the second correction turn's real reply) is still the newest row
in that session — 321 total messages, nothing sent since. The
correction sits at the head of the exact history
`HermesSessionAdapter` will resume from on its next real call.

## What is still NOT proven

No new player turn has been run since the correction, so no fresh,
live-generated `[EDITOR_REQUEST]` has actually been observed naming
`WorldComposition.tscn` on its own. That live acceptance test — Dragon
emitting a correctly-targeted request with the Editor needing no
downstream override — is the natural next live probe, not run here.

## Status

Documentation correction only (this file). No code changed, no new
chat message sent, no live probe run, per instruction to stop after
verification/correction.
