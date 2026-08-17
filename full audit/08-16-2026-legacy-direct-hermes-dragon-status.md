# Legacy Direct-Hermes Dragon Mailbox — Status & Diagnostic Notes

Written: 2026-08-16, same day as `08-16-2026-full-audit.md` and its extension.
This is a field note, not a contract. It documents what is now *known to be
true* about `hermes_session_adapter.py` (present, separately, in both
`engain_avatar` and `godot_engain_3d_avatar`), following a live operator test
that overturned an earlier wrong claim about it.

## Disposition

**ACTIVE — CURRENT PRODUCTION PATH. NOT RETIRED. NOT SCHEDULED FOR DELETION.**

This is not a Trae-style retirement. Trae was fully replaced and stopped
being dispatched to. This mechanism is, as of today, the *only* thing that
actually makes a dragon speak. It stays exactly as it is, untouched, until
an explicit, separately-authorized migration decision is made — and if that
migration turns out to be impractical without breaking the assumptions this
mechanism is built on, the fallback is to preserve it standing, on purpose,
not to force it into a shape it wasn't built for. Preserved and running is
an acceptable permanent outcome here, not just a transitional one.

## What was wrong, and what's actually true

An earlier claim in this audit trail (this session, 2026-08-16, prior to
this note) asserted that the frozen session `20260731_065008_63a62d` was
"a sealed transcript pinned in source as evidence" that would fail or be
rejected if resumed today. That was untested speculation, stated as fact.

A live operator run of the 2D avatar on this same day disproved it directly:
the frozen session resumed successfully across roughly two and a half weeks
and multiple process/machine restarts, correctly recalled context
(`GAZE`/`HOVER`/`RETURN`/`VETO`, from a substantially older exchange), and
produced a new, contextually appropriate answer about throne color that
depended on that recalled memory.

**Confirmed true:** Hermes's own session persistence is durable and
resumable across days and process restarts, independent of whether any
adapter process is currently running. The continuity is real, not
evidence-freeze theater.

**Confirmed still true (unaffected by the above):** both dragons are
hardcoded to one specific session/companion/provider/model tuple:

```
companion: hermes_b
session_id: 20260731_065008_63a62d
provider: openai-codex
model: gpt-5.6-sol
```

Neither worker dynamically resolves a session, provider, or model. Swapping
to a different provider (Claude Code, a different model) requires editing
source, not configuration, and there is no `PresenceRegistry`,
`SessionLedger`, or `SharedSessionBridge` involvement anywhere in either
worker — confirmed by the same-day full audit's search: no imports of, or
references to, `tier1.engainos` in either `hermes_session_adapter.py`.

## The concurrency point worth carrying forward

Because the continuity is now confirmed real rather than assumed fake, the
absence of serialization between the 2D and 3D workers is a sharper concern
than it looked before this note: both workers can invoke the same live,
stateful Hermes session concurrently, with no shared lock. This was already
identified in the same-day full audit's extension; this note just removes
the possible reading that it doesn't matter because "the session isn't
really live anyway." It is really live. Two doors with no lock on one live
conversation is a real race, not a theoretical one.

## One traced-and-closed item

The 2D live run's debug log showed a doubled filesystem path:

```
/mnt/data-drive/engain_avatar//mnt/data-drive/engain-runtime-mailboxes/dragon2d/request.json
```

Traced to `addons/zwengain/scripts/EngAInBridge.gd:127`:
`ProjectSettings.globalize_path("res://") + engain_request_file`, concatenating
two already-absolute paths. Confirmed cosmetic: that variable (`full_path`)
is only ever passed to `print()`. The actual write goes through a
project-relative temp file, published via the Python helper's
`--publish-request`, which hard-links it into the correct mailbox path — a
different code path entirely, unaffected by the doubled string. Not a
diagnostic false alarm to re-litigate later; closed here.

## Diagnostic value, going forward

Keep this mechanism runnable and unmodified as:

1. A known-working reference for what "real Hermes continuity" looks like,
   to compare against whenever the new `PresenceRegistry`/`SessionLedger`/
   `SharedSessionBridge` path is eventually pointed at a live dragon.
2. A fallback if the migration to dynamic provider/session resolution turns
   out to require breaking assumptions this mechanism depends on (the
   fixed mailbox schema, the fixed companion identity, the fixed
   `--resume` target).

No source modification was made to either `hermes_session_adapter.py` in the
course of writing this note.
