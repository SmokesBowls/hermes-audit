# Live confirmation: Dragon's Chapter 2 recheck sees the fix through the real door — and a real gap it also found. Chapter 3 Scene 003.1 request now in flight.

Read-only trace, continuing from `3e436e7`. The pending
`recheck_chapter2_authored_scenes_02` request resolved while this was
being written. A second, new request immediately followed, targeting a
chapter this session's splitter work hasn't specifically exercised
through the door before — consistent with the user's own framing:
"we choosing a new chapter in case he is using memory."

## The Chapter 2 recheck resolved — and it's a real, independent confirmation

`editor_report.20260919_211004_59b0` (`consumed/`), answering
`dragonreq_20260920_040539_9058307a`. Full 47-query investigation,
terminal status `SUCCESS`, zero files touched (verified via
`git diff`/`git status` before and after).

**The headline result:**

```json
{"ok": true, "operation": "status", ...,
 "chapter_id": "chapter.book001.002_molten_descent",
 "scene_count": 1, "collision": null, "warning": null}
```

`scene_count: 1` — through the live, production `engain_door.py`
`status` call, independently, by a process that isn't this session.
This is the exact result `df4d7f8` claimed from a direct pipeline
rerun; now it's confirmed from the consumer side, through the same
boundary Dragon actually uses. Query hits for `scene 002.2`,
`scene 002.3`, `scene 002.4` all returned zero — there is genuinely
only one scene packet where there used to be four.

**A real gap this recheck surfaced, worth keeping**: the Editor
reported the *formal* authored-scene count and boundary-proof state as
`unresolved`/`unknown` — not because the splitter fix didn't work, but
because `authored_scene`, `authored scene`, `proven`, and `unproven`
all returned **zero query hits**. `d138fc8`'s `authority_state:
"SCENE_BOUNDARY_AUTHORED"` and `authored_scene_boundaries_proven: true`
are real, correct fields in the underlying Pass B/C JSON — but
`engain_door.py`'s `query` operation only does literal substring
matching over narrative *text*, and those are structured JSON fields,
not words that appear anywhere in the prose. The door's `status` call
already surfaces `scene_count`/`chapter_id`/`ingestion_status`
directly; it does not currently surface `authority_state`/
`boundary_method`/`authored_scene_boundaries_proven` the same way. The
Editor's own conclusion is exactly right, quoted directly: *"the door
does not explicitly classify or count that heading as an authored
scene."* **This is a real, honest limitation of the door's current
surface, not a defect in the splitter fix** — flagged here as a
plausible next door enhancement, not something to act on unprompted.

**The independent presence ledger the Editor built** (via literal
`query` calls alone, no knowledge of this session's `presence`/
`physicality` fields) lines up with the manifestation design almost
exactly: Senareth, Elyraen, Olythae, the Nephoretti assembly, and the
transformed Pelagor/Giants classified locally physically manifested
with specific narrative citations; Mordain and the Aeon Keepers
classified present only through consciousness/remote connection, with
physical presence explicitly marked unproven. Player-control assessment
correctly kept `spawnable`, Prime, coordinator, and focalization
separate from actual player-control evidence (zero hits for `player`/
`controllable`/`control`/`protagonist`/`focal`, reported as absence of
evidence, not proof about a future adaptation).

## Chapter 3, Scene 003.1 — new request now in flight

`dragonreq_20260920_041635_a5559b0a`, request id
`read_chapter003_scene003_1_01` — still pending as of this trace
(unclaimed in `coordination/outbox/`). This is a genuinely new target:
Chapter 3 is the 7-authored-scene case (`d138fc8`'s hardest acceptance
test), and this request has never been asked before in this mailbox.
Notably more careful than the Chapter 1/2 requests: it does **source
discovery by filename pattern** (`003_*` under the vault directory)
rather than a hardcoded path, explicitly stops if more than one
candidate exists, and scopes every finding strictly to the internal
heading `scene 003.1` — explicitly excluding evidence from Chapter 3's
other six scenes. It asks the same shape of questions as the Chapter 2
recheck (authored identity, metadata provenance, physical vs.
nonphysical presence ledger, chronological events, player-control
assessment) plus one Chapter 2 didn't ask: whether the scene-meta
fields are raw source text, generated metadata rendered as text, or
structured door metadata — directly probing the same
`@scene_meta_*` passthrough `d138fc8` added.

Not yet resolved. Also observed, incidentally: three older,
long-unclaimed requests from 2026-09-13/14 still sitting in
`coordination/outbox/` — not investigated further here, noted only in
case they matter to a future trace.

## What was not done

Nothing touched. Read-only trace of live mailbox files not written by
me. Recommend a follow-up trace once `a5559b0a` resolves.
