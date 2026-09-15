# First real-chapter Mettaext ingest — live proof, corrections to the toy-chapter audit

Executes the "recommended next step" from
`09-15-2026-mettatext-stageroom-artifact-audit.md`: run `pipeline_runner`
once against one real, short chapter, and check whether entity/inference
extraction behaves differently on real prose than on the two synthetic
smoke chapters. It does — several findings from that audit are now
proven wrong or incomplete. This document corrects them rather than
editing that file in place, per established discipline.

## Source selection

Per instruction: only ever touch folders under
`/home/mytruelove/Downloads/obsidianburdenNov25/` whose name starts
with "book" (case-insensitive) — everything else in that vault
(`_mrlore/` 3414 files, `building_the_world/` 1172 files, `.obsidian/`,
`.trash/`, etc.) is out of bounds and was not read.

Queried `vault_source_index.json` for the smallest real chapter-shaped
file (`.md`, `chapter.*` id) across all `book*`-prefixed folders (140
candidates). Picked the smallest: `book_04_sage_saga/
016_the_choice_third_coming.md`, 8577 bytes, vault index predicted id
`chapter.016_the_choice_third_coming`. Ran, live, with no
capture/simulation:

```bash
cd /home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn
python3 -m tier3.mettaext.pipeline_runner \
  "/home/mytruelove/Downloads/obsidianburdenNov25/book_04_sage_saga/016_the_choice_third_coming.md"
```

Completed successfully (`✓ Pipeline complete!`), 2 scenes produced.

## Correction 1 — entities and inference DO populate on real prose (overturns audit Finding 2)

The toy-chapter audit found `@entities: []` and empty `=inferred` in
both synthetic samples and left open whether that was a real
limitation or just too little content. It was the latter. On this real
chapter:

- Scene 1: `@entities: ["Pazuzu", "Tran", "Zephyr"]`. Pass 2 extracted
  2 speaker inferences, 1 emotion inference, 2 action inferences.
- Scene 2: 3 characters, 1 speaker inference, 3 emotion inferences,
  1 action inference.

Structured entity/inference extraction works on real content.

## Correction 2 — but extraction is allowlist-gated against `world_rules.json`, silently dropping unregistered names (new finding, matters directly for query design)

Live stderr during the run:

```
[world_rules] loaded 36 entities from .../tier1/engainos/assets/world_rules.json
[pass2_entity_filter] UNKNOWN ENTITY BLOCKED: 'Igigi' (mentions=6). Add to manifests/world_rules.json if intentional.
[pass2_entity_filter] UNKNOWN ENTITY BLOCKED: 'Anunnaki' (mentions=4). Add to manifests/world_rules.json if intentional.
[pass2_entity_filter] UNKNOWN ENTITY BLOCKED: 'Elder' (mentions=3). Add to manifests/world_rules.json if intentional.
```

"Igigi," mentioned 6 times in this one short chapter, never appears in
`@entities` — it isn't in the 36-entity allowlist, so `pass2_entity_filter`
drops it regardless of mention count.

**Direct consequence for the door's query design:** a query for a name
that isn't already a known/registered entity (which is exactly the
"Falcon Ridge, first time anyone asks about it" case the whole MettaText
effort exists for) will be **invisible to `@entities`/`=inferred`**, no
matter how load-bearing that name is in the actual prose. This
confirms — more strongly than the toy-chapter audit could — that the
door's v1 query must search raw text (`out_pass1_*.txt` narration
lines, `out_pass1_spatial_*.json`'s `source_text`), not the structured
entity fields. The structured fields are a curated-vocabulary index,
not a general-purpose one.

## Correction 3 — `region`/`@where` are hardcoded exactly as suspected; `environment`/`terrain_family` are NOT, they're content-derived (refines audit Finding 3)

The earlier audit treated "region/environment/terrain_family" as one
contaminated group. That was imprecise. Now separable:

- `region` / `@where` / `@region`: **still hardcoded**, confirmed on
  real content. This chapter's actual setting is "the computational
  chambers of Eridu," with dialogue about "orbital mechanics" — a
  science-fiction interior, nothing beach-related — yet
  `@where: "Realm/Physical/Beach"`, `region: "Beach"`, same as the
  toy chapter. Still coming straight from `pipeline_runner.py`'s
  hardcoded `--location Beach` argument, not from the prose.
- `environment` / `terrain_family`: genuinely content-derived this
  time — both resolved to `"cosmic"`, with
  `environment_inference: {source: "inferred", profile: "cosmic",
  confidence: 0.73, evidence: ["kw:cosmic", "kw:orbital", "kw:space", ...]}`.
  Real keyword votes against real scene text.

So: **never trust `region`/`@where` as extracted content — it is
always the pipeline's hardcoded default.** `environment`/
`terrain_family` are worth including as door evidence, with the
caveat below.

**Caveat on the environment vote itself:** its own `evidence` list
mixes real content keywords (`kw:cosmic`) with hits against the
metadata preamble (`"segments:4 narration @boundary_method:
mechanical_word_chunk"`) — i.e. Mettaext's own environment classifier
does not skip the `@key: value` preamble described in the toy-chapter
audit's Finding 1 either. It happened to land on the right answer here
because the real keywords outweighed the noise, but the noise is
present in the vote, not just a theoretical risk for a downstream
consumer.

## Correction 4 (new, concrete bug) — `chapter_id` has three different, inconsistent values for the same source file, and the done manifest records the wrong one

Three separate places derive an id for this exact same input file, and
they disagree:

1. **`vault_source_index.json`'s pre-assigned id** (what the earlier
   audit assumed the door could rely on):
   `chapter.016_the_choice_third_coming` — naive, filename-only.
2. **The real id `passA_chapter_intake` actually derives and that every
   artifact on disk is named with** (folder-context-aware — picks up
   `book_04_sage_saga` → `book004`):
   `chapter.book004.016_the_choice_third_coming`. Confirmed against the
   real paths: `out_passB_chapter.book004.016_the_choice_third_coming.json`,
   `scene_packets/chapter.book004.016_the_choice_third_coming/`,
   `scene.book004.016_the_choice_third_coming.scene00{1,2}/`.
3. **What `pipeline_runner.py` writes into the done manifest**, right
   now, on disk: `source_text_id = "chapter.016_the_choice_third_coming"`
   — matches variant 1, not variant 2, even though variant 2 is the
   one every real artifact actually uses.

Root cause, read directly in `pipeline_runner.py`: the function reads
`passA_data["chapter_id"]` correctly (into a local `chapter_id`
variable, used correctly for locating packets/output dirs earlier in
the same function), but the final manifest-writing block ignores that
variable and independently re-derives `source_text_id` from
`chapter_path.stem` (the bare input filename) instead:

```python
source_text_id = chapter_path.stem                      # ignores the real chapter_id
if not source_text_id.startswith("chapter."):
    source_text_id = f"chapter.{source_text_id}"
subprocess.run([..., "--source-text-id", source_text_id], ...)
```

**This is reproducible right now** — `cat
tier3/mettaext/stageroom/mettaext_done_manifest.json` on this repo
today shows `source_text_id: "chapter.016_the_choice_third_coming"`
while every real artifact path it lists is tagged `book004`. The
`artifacts.*` lists themselves are still correct (they're built by
globbing the output directories by filename pattern, not by trusting
`source_text_id`), so nothing is lost — but any consumer that
constructs a lookup path *from* `source_text_id` (exactly what the
door's ingest-idempotency check and evidence lookup were planned to
do) will look in the wrong place and get a false "not ingested" or
miss the evidence entirely.

**Consequence for the door design:** the door cannot derive
`source_text_id`/`chapter_id` from the source filename alone (rules
out relying on `vault_source_index.json`'s pre-assigned id, contrary
to what the prior audit suggested), and cannot trust the done
manifest's `source_text_id` field either. The only reliable source of
truth is **`passA`'s own output file's `chapter_id` field**, read back
directly after ingest — e.g.
`stageroom/output/chapterroom/out_passA_<input_stem>.json` →
`.chapter_id`. The door should treat this as the one authoritative id
and use it for every subsequent lookup, never re-deriving it itself.

## Correction 5 (minor, structural) — narration text has a third zone: authored front matter, not just engine metadata

The toy-chapter audit's Finding 1 (skip everything before the first
`{type:scene_header} ---` marker) is necessary but not sufficient on
real chapter files. This scene's `out_pass1_*.txt` has **two** `---`
markers: the first ends the engine-generated `@key: value` preamble
(as in the toy case), but is immediately followed by the source
document's own front matter — "book 4", "chapter 016-the choice third
coming", "~~~OPENING MOVEMENT: THE CHOICE~~~~", "Subchapter 1: The
First Act of Freedom", "year 14000.... the third coming" — all still
tagged `{type:narration}`, before a *second* `---` marker that finally
opens the actual prose. A query for a term like "chapter" or "book"
would spuriously match this front matter, not story content. Also
noted: dialogue lines carry a distinct tag,
`{type:dialogue, speaker:he}`, separate from `{type:narration}` — a
future refinement could let the door label evidence as
narration-vs-dialogue for free.

## Net effect on the door's v1 query design

The proposed shape (exact source selected → enumerate evidence
artifacts → case-insensitive text match → return matches + provenance)
still stands and is now more confidently the right call, for a
sharper reason than before: structured fields aren't just sparse,
they're **actively gated** (Correction 2) and **partly wrong by
construction** (`region`, Correction 3). Two concrete requirements
this run adds to that design, beyond what the toy audit knew:

1. **id derivation must read `passA`'s actual `chapter_id` back from
   its output file** — never the filename, never the done manifest's
   `source_text_id` (Correction 4).
2. **Text matching should skip through the *last* leading
   `{type:scene_header} ---` marker**, not just the first, since
   authored front matter can sit between the engine preamble and the
   real prose (Correction 5) — or, more robustly, match against
   `out_pass1_spatial_*.json`'s `source_text` field, which only ever
   contains real sentences the spatial extractor scored, never
   preamble or headers.
