# Amendment: `[EDITOR_REQUEST]` source provenance (adds Publisher coordinates)

Amends `09-17-2026-editor-request-contract-v1.md` §1's `source` object.
That contract was frozen before the Publisher, tokenizer, crosswalk, or
orchestration designs existed — its `source` shape only carries
`scene_id`/`chapter_id`/`artifact` (Mettaext-door style), with no
passage-level coordinate at all. This closes that gap, caught directly
in the dependency audit rather than discovered after implementation.

## Old shape (§1 of the base contract, for reference)

```json
"source": {
  "scene_id": "scene.book008.047_mika.scene002",
  "chapter_id": "chapter.book008.047_mika",
  "artifact": "output/passroom/scene.book008.047_mika.scene002/out_pass1_scene.book008.047_mika.scene002.txt"
}
```

## New shape (locked)

```json
"source": {
  "source_id": "src.book008.chapter047.passage_C.0001",
  "source_hash": "sha256:...",
  "book_id": "book_008",
  "chapter_id": "chapter.book008.047_mika",
  "passage_id": "book_008.chapter_047.passage_C",
  "byte_start": 0, "byte_end": 0,
  "word_start": 0, "word_end": 0,

  "producer": "dragon",
  "producer_artifact_id": null,
  "producer_record_id": "req.book008.047_mika.scene002.0001",

  "mettaext_scene_id": "scene.book008.047_mika.scene002"
}
```

Nothing is removed — `scene_id` survives as `mettaext_scene_id`, still
present for cross-reference and human/tool readability. What changes is
its *role*: it's no longer part of `source`'s authority, it's a
retained label.

## The rule this closes (locked)

> **Mechanical Mettaext scene IDs do not become source authority.**
> `passage_id` + `byte_start`/`byte_end` (Publisher-defined, per
> `09-17-2026-publisher-input-authority-amendment.md`) are the
> authoritative answer to "where in the source." `producer` +
> `producer_artifact_id`/`producer_record_id` are the authoritative
> answer to "who claims this and on what record." `mettaext_scene_id`
> is retained only as a convenience label, exactly the same demotion
> the Publisher input-authority amendment already applied to Mettaext's
> tagging — a derived artifact may be cross-referenced, it may never
> define coordinates or stand in for provenance.

`producer` distinguishes who generated this `[EDITOR_REQUEST]`
(`"dragon"` for Dragon's own comprehension-driven proposals) from whose
*evidence* informed it, if any (`producer_artifact_id`, populated when
a specific upstream record — a Mettaext observation, an `unclelore`
artifact, a `tier1_mrlore` claim — directly grounded a structure or
relation; `null` when Dragon's own reading of the passage was the sole
basis, with no upstream evidence citation). This mirrors the authority
labeling already locked in `09-17-2026-dragon-orchestration-contract-
v1.md` §1–2 — `[EDITOR_REQUEST]` and the orchestration bundle now speak
the same producer/authority vocabulary, not two different ones.

## What does not change

- `structures[]`, `terrain_features[]`, `spatial_relations[]`,
  `unresolved_notes[]` — all four arrays, their fields, and the real
  Falcon Ridge worked example grounding them — are unaffected. This
  amendment touches only the top-level `source` object.
- The assembly stage design (`09-17-2026-assembly-stage-design-v1.md`)
  is unaffected — it consumes `structures[]`/`spatial_relations[]`, not
  `source`.
- `authority: "proposal_only"` at the top level of `[EDITOR_REQUEST]`
  stays exactly as originally locked — this amendment doesn't touch
  Dragon's own proposal-only standing, only how its source is cited.

## Status

Amendment locked, `09-17-2026-editor-request-contract-v1.md` §1 closed
by this document per the same standing amendment convention as
`09-17-2026-publisher-input-authority-amendment.md`. No code written.
Real word/byte offsets in the worked shape above are left `0`, same
honesty rule as everywhere else this session — the tokenizer reference
implementation doesn't exist yet.
