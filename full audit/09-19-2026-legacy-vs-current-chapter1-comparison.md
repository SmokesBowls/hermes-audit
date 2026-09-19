# Legacy vs. current Mettaext output, chapter 1, file-level comparison

Read-only investigation, per instruction. Nothing ingested, rebuilt,
migrated, or modified. Chapter 1 is the only chapter that exists in
both the legacy corpus (`legacy_pipeline_work/`, dated June 2026) and
the current pipeline's output (`chapterroom/`/`passroom/`, generated
this week) — this compares them directly, file by file, to give a real
basis for any future adapter rather than one designed from schema
names alone.

## Files compared

```text
Legacy (all dated 2026-06-13, except *.metta dated 2026-06-24):
  legacy_pipeline_work/001_the_ethereal_vigil.zon        (31KB, YAML-ish)
  legacy_pipeline_work/001_the_ethereal_vigil.zonj.json  (39KB, richer JSON)
  legacy_pipeline_work/zonj_001_the_ethereal_vigil.json  (43KB, a DIFFERENT,
                                                           simpler JSON schema)
  legacy_pipeline_work/out_pass1_001_the_ethereal_vigil.txt   (25KB)
  legacy_pipeline_work/out_pass2_001_the_ethereal_vigil.metta (1.7KB)

Current (all dated 2026-09-19, this week's controlled ingestion):
  chapterroom/out_passA_001_the_ethereal_vigil.json
  chapterroom/out_passB_chapter.book001.001_the_ethereal_vigil.json
  chapterroom/scene_packets/chapter.book001.001_the_ethereal_vigil/
    scene_packets_index.json + 4 scene .txt files
  passroom/scene.book001.001_the_ethereal_vigil.scene00{1-4}/
    (per scene: pass1 .txt, pass1 spatial .json, pass2 .metta, .zon,
    .zonj.json, zonj_ .json, game_scenes/ subfolder)
```

## 1. What information exists in both?

- **The same pipeline shape**: a pass1 (raw text extraction) → pass2
  (enhanced inference: entities, speakers, emotions, actions) → a
  combined zonj/JSON artifact. Same three-stage architecture, both
  eras.
- **The same underlying source prose**, close to verbatim (spot-checked
  the opening lines — "The Ethereal Realm existed in the spaces between
  thought and form..." appears identically in both).
- **Per-segment dialogue vs. narration typing**, line-numbered.
- **Speaker inference as a separate confidence-scored list**, keyed by
  line number, distinct from the per-segment `speaker` field itself
  (both eras keep these as two different things, not one).
- **Emotion/action inference**, same shape:
  `(emotion line:N subject emotion :confidence C)` /
  `(action line:N verb :confidence C)` in both `.metta` files.
- **The same four environment/region fields** — `@region`,
  `@terrain_family`, `@environment`, `@spatial_scale_hint` — present by
  the same exact names in both eras' zonj output (legacy: whole-chapter
  `environment: coastal`; current: independently-derived, scene-1-only
  `environment: coastal` — the two happen to agree here, not verified
  whether that's meaningful or coincidental).

## 2. What exists only in legacy?

- **Whole-chapter granularity as the only granularity.** Legacy never
  splits a chapter into scenes at all — one flat segment stream (195
  "meaningful" segments in `.zonj.json`, 274 total lines including
  headers in the alternate `zonj_*.json`) covering the entire chapter.
- **A second, simpler, internally-inconsistent legacy schema.**
  `zonj_001_the_ethereal_vigil.json` (`type`/`id`/`source_files`/
  `segments` only) is a *different* file from
  `001_the_ethereal_vigil.zonj.json` (the richer `@`/`=`-prefixed
  schema with `=inferred`) — not two views of the same data, two
  different serializations that happen to share a naming prefix. Any
  migration has to pick one, or reconcile both.
- **108 other chapters' worth of extraction** that the current pipeline
  has not touched at all (per the prior receipt, `3d317a5`).

## 3. What exists only in current?

- **Explicit, honest scene-boundary provenance flags** —
  `boundary_method: "mechanical_word_chunk"`,
  `authority_state: "SCENE_BOUNDARY_MECHANICAL"`,
  `authored_scene_boundaries_proven: false` — attached to every scene.
  Legacy has no equivalent because it never attempts scene splitting,
  so it's neither more nor less honest here; there's nothing for it to
  be honest or dishonest about.
- **The entire `known`/`spawnable`/`classification` concept.** This is
  the field this week's whole spawnable-vs-scene-presence design
  discussion was about (`9205232`), and it **does not exist anywhere in
  the legacy schema** — legacy's `@entities` is a bare name list, no
  known/spawnable/classification metadata at all. **This means reading
  the legacy corpus as-is would give Dragon zero spawnable information
  for any of the other 109 chapters** — that concept would have to be
  freshly computed, not migrated, even if the raw text/entity list
  transfers cleanly.
- **Structured, book-aware identifiers** —
  `chapter.book001.001_the_ethereal_vigil`,
  `scene.book001.001_the_ethereal_vigil.scene001` — vs. legacy's bare
  `scene.001_the_ethereal_vigil` (no book prefix, no scene index, since
  there's no scene concept).
- **A formal contract/schema-version field**
  (`engain.scene_provider_packet.v1`) — no equivalent in legacy.
- **Provenance metadata physically embedded as fake `narration`
  segments.** Every current per-scene segment stream opens with lines
  like `{"line": 1, "type": "narration", "text": "@scene_id: scene...."}`
  — the scene's own `@scene_id`/`@chapter_id`/`@boundary_method`/etc.
  are injected as the first 6-8 "narration" segments, indistinguishable
  by type from real story text. **This is not cosmetic — it visibly
  contaminates other extraction**: scene1's own `environment_inference`
  confidence computation cites *`"segments:1 narration @scene_id: scene.book001..."`*
  and *`"segments:4 narration @boundary_method: mechanical_word_chunk"`*
  as evidence text, meaning the keyword-based environment classifier is
  scanning its own injected header lines as if they were narrative
  content. Legacy has no equivalent because it stores this kind of
  metadata in genuinely separate top-level fields (`@id`, `=metadata`),
  never inside the segment stream.
- **A `game_scenes/` subfolder per scene** (`scene.*.scene001.json`,
  `scene_index.json`) — present in current output, not explored in
  depth here (out of scope for this specific comparison; flagged for a
  separate pass if it matters to the adapter question).

## 4. Can the legacy data answer the same kinds of scene queries Dragon just asked?

**Not at scene granularity, no — legacy has nothing to query at that
level.** Dragon's actual chapter-1 investigation (the ninth-live-test
result, `9205232`) asked specifically about "the first scene" and got
back a 4-scenes-exist, scene-1-specific answer. Legacy's data structure
cannot answer that question at all without first inventing a scene
split it never performed. **At chapter granularity, legacy can answer
a meaningful subset**: it has the full raw narrative, a (demonstrably
incomplete) entity list, speaker/emotion/action inference with
confidence scores, and a region/environment guess — enough to support
a "what happens in this chapter" query, not a "what happens in scene 1
of 4" query.

## 5. What information cannot be normalized without inventing meaning?

- **Mapping legacy's flat chapter stream onto current's 4 mechanical
  scenes.** Current's own `line_count` for the chapter is 172; legacy's
  segment stream runs to line 274. These are not the same line-counting
  scheme (most likely: current's `raw_text` excludes blank lines or
  some header content that legacy's pass1 extraction kept — not
  determined here). Without a verified, line-for-line alignment between
  the two, assigning any given legacy segment to one of current's four
  scene buckets would be a guess dressed as a mapping.
- **Spawnable/known/classification data for legacy-only chapters.**
  As above — this field doesn't exist in legacy at all. Producing it
  for the 109 legacy-only chapters requires running real classification
  logic against real text, not translating an existing field.
- **Reconciling the two legacy schemas with each other**, since they
  disagree in structure and it's not established which (if either) is
  authoritative.
- **Entity-list completeness is already unreliable in both eras and
  should not be trusted as-is by any normalizer.** Confirmed directly:
  the character **Lyaris** — explicitly named as speaking in the very
  first line of dialogue setup ("Lyaris was the first to notice the
  shift") — is **absent from every entity list examined**, legacy and
  current alike (legacy `@entities: [Mordain, Syreth, Vaelith]`;
  current scene-1 `@entities: [Mordain, Pelagor, Syreth, Theron, Tran,
  Vaelith]`). A normalizer that trusts either era's entity list as
  complete will silently drop a named speaking character.
- **A confirmed, persisted extraction defect in current, not just a
  query-time artifact.** The live investigation reported Dragon
  correctly refusing to treat a `Tran` query hit as a real character
  ("substring matches such as 'transformed'"). This comparison found
  something stronger: **`Tran` is already sitting inside scene 1's own
  generated `@entities` array** (`out_passA`'s downstream scene zonj),
  not something a live query merely stumbled into. Any future consumer
  reading `@entities` directly, without Dragon's own skepticism, would
  be handed a fabricated character as fact. Multi-word proper nouns
  also get split into single-token "entities" in both eras (current's
  `=entities_observed` lists bare `"Ethereal"` as its own 6-mention
  "known" entity, clearly a fragment of "the Ethereal Realm," not a
  character) — the earlier live finding of `Aeon`/`Keepers` being
  preserved as two separate unknown entities is the same defect class.

## 6. Are the old scene boundaries materially different from the new mechanical ones?

**There are no old scene boundaries to compare — legacy has none at
all.** The honest framing isn't "different," it's "absent vs. present."
Current's 4 boundaries are `mechanical_word_chunk` (roughly even
line-count slices: 1-55, 56-98, 99-140, 141-172), explicitly flagged as
not proven authored.

**The more important finding: the actual authored boundary is sitting
unused in the raw text itself, in both eras.** Current's own
`out_passA` raw_text begins:

```text
book 1
chapter 001-the ethereal vigil

day pre-0
scene 001.1 — ethereal watch / planetary stabilization

~~~The Garden Genesis~~~~
Part 1: The Ethereal Vigil
...
```

The author's own `scene 001.1 —` / `scene 001.2 —` headings (already
surfaced in the live investigation's "unresolved" list, `9205232`) are
present verbatim in the raw source text available to *both* pipelines.
**Neither pipeline uses them.** Legacy doesn't split scenes at all;
current's mechanical word-chunker produces 4 scenes that ignore these
2 authored headings entirely. The cheapest, most direct improvement
available — not evaluated further here, just named — would be
detecting and using these inline headings as the boundary source
before falling back to mechanical chunking, rather than treating
"proven authored boundary" as an unreachable standard when the author
already wrote one directly into the file.

## Net, for the adapter question

This is offered as evidence, not a recommendation — the user's own
framing was to get a real basis before designing anything:

- A migration/adapter cannot just "read the legacy schema" for
  scene-level answers, because legacy has no scenes.
- A migration/adapter cannot produce spawnable/classification data by
  translation, because that concept doesn't exist in legacy at all —
  it would need fresh computation either way.
- Whatever eventually generates or reads scene boundaries should
  probably look for the author's own inline `scene N.M —` headings
  first, in both a migration path and any future re-run of the current
  pipeline, since ignoring them is a shared weakness, not a
  legacy-vs-current difference.
- Both eras' entity extraction has real, confirmed defects (missing
  Lyaris; a persisted `Tran` false positive baked into generated
  evidence; single-word fragments of multi-word names) — a migration
  path is not "safe by default" just because it reuses legacy data
  instead of running fresh extraction; the fresh extraction has at
  least one of the same defect classes independently.

## What was not done, per instruction

No ingestion, migration, or rebuild was performed or proposed as code.
No file was modified. `game_scenes/`'s own content was not explored in
depth — flagged, not analyzed, since it wasn't necessary to answer the
six questions asked.
