# Amendment: `status` surfaces authored-boundary provenance

Amends `09-15-2026-engain-door-contract-v1.md` (committed `d6ce833`),
additively. Does not rewrite that document in place, per established
discipline. One addition only: `status`'s JSON response gains three
fields that already existed in the underlying artifact and were simply
never read into it. Everything else in the frozen contract stands
unchanged.

## The gap this closes

Live-traced in `afa0624`: Dragon asked the door, through a real
`recheck_chapter2_authored_scenes_02` request, whether Chapter 2's
scene boundaries were authored and proven. The evidence exists —
`d138fc8`'s splitter sets `authority_state: "SCENE_BOUNDARY_AUTHORED"`
and `authored_scene_boundaries_proven: true` on every scene, and
`passC_scene_packet_writer.py` has recorded both, plus
`boundary_method`, at the top level of `scene_packets_index.json`
since that file was written. But `engain_door.py`'s `query` operation
only does literal substring matching over narrative *text* — those are
structured JSON fields, not words that appear in the prose — so
`authored_scene`, `authored scene`, `proven`, and `unproven` all
returned zero hits. The Editor's own, correct conclusion: *"the door
does not explicitly classify or count that heading as an authored
scene."* Not a Mettaext extraction problem, not a splitter problem — a
door-surface gap.

`resolve_status()` was already opening `scene_packets_index.json` to
read `scene_count`; it just discarded everything else in that dict.

## The fix

Three fields added to `status`'s existing "existing" response shape,
read straight through from the same already-opened
`scene_packets_index.json` — no new inference, no new file read, no
new consumer of Pass B/C's output beyond what already happened:

```json
{
  "ok": true,
  "operation": "status",
  "authority": "evidence_only",
  "source": { "path": "/abs/path/given", "exists": true },
  "ingestion_status": "existing",
  "chapter_id": "chapter.book001.003_first_contact",
  "scene_count": 7,
  "boundary_method": "authored_scene_marker",
  "authority_state": "SCENE_BOUNDARY_AUTHORED",
  "authored_scene_boundaries_proven": true,
  "collision": null,
  "warning": null
}
```

All three fields are `null` in every other status shape (`not_ingested`,
`stem_collision`, unparseable Pass A artifact) — additive and
consistent with the existing `null`-on-absence convention those shapes
already use for `chapter_id`/`scene_count`. Also `null` when an
existing `scene_packets_index.json` predates this fix and simply
doesn't have the keys yet (`.get()`, never a `KeyError`) — real
backward compatibility with already-ingested chapters, not just a
hypothetical.

`ingest` and `query` are unchanged. The instruction was specifically
about `status`; `op_ingest()` builds its own response dict rather than
forwarding `resolve_status()`'s wholesale, so this change has zero
effect on it.

## Live verification against real chapters

```json
// chapter.book001.002_molten_descent (1 authored scene)
"boundary_method": "authored_scene_marker",
"authority_state": "SCENE_BOUNDARY_AUTHORED",
"authored_scene_boundaries_proven": true

// chapter.book001.003_first_contact (7 authored scenes)
"boundary_method": "authored_scene_marker",
"authority_state": "SCENE_BOUNDARY_AUTHORED",
"authored_scene_boundaries_proven": true
```

Both confirmed live via `engain_door.py status --source <real vault
path>`, matching `d138fc8`'s implementation exactly.

## Tests

18 tests in `tests/test_engain_door.py` (14 previous + 4 new):
authored values surface correctly; mechanical values surface correctly
(not hardcoded to only recognize the authored case); an index predating
this fix returns `None` for all three, not an error; `not_ingested`
also returns `None` for all three. `write_scene_index()`'s test helper
gained optional keyword args for the three fields, defaulting to
omitted (existing call sites unaffected). Full suite: 18 passed.

## What was not done

`ingest` and `query` responses unchanged. No new inference added
anywhere — every value surfaced already existed in
`scene_packets_index.json` before this change.
