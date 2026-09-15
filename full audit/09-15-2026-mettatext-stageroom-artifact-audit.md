# Mettaext stageroom artifact audit — discovery only, no code touched

Answers the question left open in `09-15-2026-mettatext-door-design-v1.md`:
before specifying the door's query matching, look at what Mettaext
actually produces. Read-only inspection of the live `stageroom/` tree
under `$ENGAIN_ROOT/tier3/mettaext`. Nothing implemented, nothing run.

## Caveat that governs everything below

**No real book chapter has ever been ingested.** `stageroom/output/`
currently holds exactly two processed sources, both synthetic smoke
tests:

- `chapter.999_abc_smoke` — 3 scenes, 44 words total, from
  `stageroom/input/chapters/chapter.999_abc_smoke.txt`.
- `chapter.engain_spatial_smoke_chapter` — 1 scene, 15 words
  ("The guard stood in front of the stone gate. / The torch burned
  behind the guard."), sourced from `/tmp/engain_spatial_smoke_chapter.txt`.

Meanwhile a real, large source registry already exists and is untouched:
`stageroom/input/vaults/vault_source_index.json` (contract
`mettaext.vault_source_index.v1`, `authority: source_discovery`) lists
**4,735 files** from an Obsidian vault at
`/home/mytruelove/Downloads/obsidianburdenNov25/.engain/`, including
real book chapters like `Book 6 the Ragnarok/29_bounty_hunter.md`
(45KB) with pre-assigned ids (`chapter.029_bounty_hunter`). None of
these have been run through `pipeline_runner`.

**Every finding below is characterized on 1-2 sentence toy content.**
Entity/landmark/inference extraction may behave very differently on
real, dense prose with actual proper nouns like "Falcon Ridge." Treat
this as a structural audit of the pipeline's output shape, not proof of
how well it extracts anything.

## Finding 1 — `out_pass1_*.txt` is not plain witness text

The first ~9 lines of every scene's pass1 file are `{type:narration}
@key: value` metadata (`@scene_id`, `@chapter_id`, `@boundary_start_line`,
etc.), followed by a `{type:scene_header} ---` marker. Only lines
*after* that marker are actual narrative prose.

The trap: metadata lines are also tagged `{type:narration}` — the same
tag as real prose lines. The `type` field alone does **not**
distinguish metadata from story content; only position relative to the
`---` marker does. Any door-side text search must skip everything
before that marker, or it will happily "find" a query term if it
happens to match inside a `@boundary_method: scene_tag` line.

## Finding 2 — structured semantic fields are empty in both samples

In both scenes' `.zonj.json`:

- `@entities: []` — never populated.
- `=inferred: {emotions: [], actions: [], thoughts: [], actors: []}` —
  pass2's "enhanced inference" found nothing in either toy scene
  (its `.metta` output is literally just empty section headers).
- `game_scenes/<scene_id>.json`'s `landmarks`/`boundaries` fields exist
  but are noisy substring fragments, not clean nouns — e.g. for "The
  guard stood in front of the stone gate," `landmarks: ["of the stone
  gate"]`, `boundaries: ["front of the stone gate."]`. Not something
  to match a query term against directly without expecting false
  negatives (a query for "stone gate" doesn't cleanly match "of the
  stone gate" via exact-phrase logic, though substring would).
- `unresolved_relations` in `level_design.layout_proof` shows the
  spatial-relation extractor found `in_front_of(guard, stone gate)`
  and `behind(burned, guard)` but couldn't resolve either subject to a
  known entity — consistent with `@entities` being empty.

Whether this is "not enough content in a 2-sentence smoke test" or "a
real gap in entity extraction" cannot be answered without a real
chapter. Flagged as the top open question.

## Finding 3 — region/environment/terrain fields are contaminated by hardcoded CLI defaults, not extracted from prose

`pipeline_runner.py` (the one real entrypoint) hardcodes Pass 4's
location arguments for *every* scene, in every chapter, unconditionally:

```python
subprocess.run([..., "pass4_zon_bridge", ..., "--era", "FirstAge", "--location", "Beach", ...])
```

The spatial-smoke scene's content is "guard / stone gate / torch" —
nothing beach-related — yet its output carries `@region: "Beach"`,
`@environment: "coastal"`, `@terrain_family: "beach"`, and an
`environment_inference` block claiming `"evidence": ["beach:1"]` at
`"confidence": 0.9`. That confidence number is almost certainly voting
on the injected default argument, not on anything in the sentence.

**Consequence for the door design: `region`/`environment`/
`terrain_family`/`@where` cannot be trusted as real semantic content
today.** They should not be used as query-matchable "what does the
story say about this place" evidence until `pipeline_runner.py` stops
hardcoding `FirstAge`/`Beach` for every chapter (a separate, pre-existing
bug worth its own fix, out of scope for the door itself).

## Finding 4 — scene IDs map cleanly across every artifact

For both scenes checked, the identical `scene_id` string
(`scene.engain_spatial_smoke_chapter.scene001`) appears verbatim across:
pass1 filename, pass1-spatial filename, pass2 filename, zonj `@id`,
`.zon`/`.zonj.json` filename, `game_scenes/<id>.json` filename, and the
chapterroom passB scene entry. `scene_identity.py`'s canonicalization
is doing real, consistent work — the door can treat `scene_id` as a
reliable join key across all artifact types without its own remapping
layer.

## Finding 5 — two non-interchangeable line-numbering spaces exist

- `out_passB_<chapter_id>.json`'s `boundary_start_line`/
  `boundary_end_line` are relative to the **original source chapter
  file's raw lines** (e.g. lines 1-2 for a 2-line source file).
- `out_pass1_<scene_id>.txt` / zonj `=segments[].line` are relative to
  the **generated pass1 output file**, which includes the ~9-line
  metadata preamble — so the same sentence is "line 1" in the original
  chapter but "line 11" in pass1's own numbering.

These must not be conflated. A provenance citation needs to pick one
space and label it. Recommendation: cite chapter-original line numbers
(from passB) when surfacing evidence to Dragon — "which line of the
book" is the meaningful answer, not "which line of an intermediate
artifact file."

## Finding 6 — the closest thing to a real "mentions X" index today

`out_pass1_spatial_<scene_id>.json` (Pass 1 Spatial) is the strongest
candidate evidence source found: each entry has `source_text` (the
exact witness sentence, not a fragment), `line` (pass1-file-relative,
see Finding 5), `relation`, `subject_hint`/`object_hint` (raw noun
phrases straight from the sentence, not routed through the broken
region-inference defaults), and a `confidence` score. It's real,
text-derived content — but only for sentences the spatial extractor
recognized as spatial/movement signals, so it's not full-sentence
coverage.

## Finding 7 — the done manifest is global, not per-source

`stageroom/mettaext_done_manifest.json` lives at a single fixed path.
Its `source_text_id` field reflects only the **most recently processed**
chapter (currently `chapter.engain_spatial_smoke_chapter`), even though
its `artifacts.*` lists have accumulated file paths from **both**
processed chapters across separate runs.

**Consequence: the manifest's `source_text_id` cannot answer "has
source X already been ingested?"** — checking it would give false
negatives for any chapter that isn't the literal most-recent one. The
door's ingest idempotency check needs to test for existence of the
expected output path instead (e.g.
`stageroom/output/chapterroom/out_passA_<chapter_id>.json`), not read
the manifest for that purpose. The manifest is a run receipt, not a
registry.

## Implication for the query design

The user's proposed v1 shape is confirmed sound given what's actually
here — no embeddings, no fuzzy search, no new index needed for v1:

```text
exact source selected
  -> enumerate that source's evidence artifacts
  -> case-insensitive text match
  -> return matching evidence blocks + provenance
```

Concretely, "enumerate that source's evidence artifacts" should mean,
per scene, searching only:

1. `out_pass1_<scene_id>.txt` narration lines **after** the
   `{type:scene_header} ---` marker (Finding 1).
2. `out_pass1_spatial_<scene_id>.json`'s `source_text` fields
   (Finding 6) — richer hits, come with relation/subject/object hints
   for free.

...and explicitly **not** trusting `@entities`, `=inferred`, or
`region`/`environment`/`terrain_family` as query-matchable content
until a real chapter proves otherwise (Findings 2-3).

## Recommended next step

Run `pipeline_runner` once against one real, short chapter pulled from
`vault_source_index.json` (pick a small `size_bytes` entry to keep the
first real trial cheap), and re-check Findings 2-3 specifically:
does entity/landmark extraction produce anything real on actual prose
with real proper nouns? That answer should come before locking the
query algorithm, not after. This has not been done — it's a proposal,
not an action taken.
