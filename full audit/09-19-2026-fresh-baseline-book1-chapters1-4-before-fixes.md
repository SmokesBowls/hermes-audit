# Fresh baseline: book 1, chapters 1-4, current Mettaext, before any of the 5 fixes

Per explicit authorization, I ran `engain_door.py ingest` directly for
all four cleaned book-1 chapters (bypassing Dragon/the Editor — "just
looking for the results, not testing the Dragon pipeline"). This is
the "get new results before anything gets fixed" baseline the recovery
plan (`4c7bf79`) called for.

## What was done

1. Removed chapter 1's stale current-schema artifacts only —
   `chapterroom/out_passA_001_the_ethereal_vigil.json`,
   `out_passB_chapter.book001.001_the_ethereal_vigil.json`,
   `scene_packets/chapter.book001.001_the_ethereal_vigil/`, and all
   four `passroom/scene.book001.001_the_ethereal_vigil.scene00{1-4}/`
   directories. `legacy_pipeline_work/` was not touched.
2. Confirmed `status` returned `not_ingested` for chapter 1 afterward.
3. Ran `ENGAIN_ROOT=.../EngAIn PYTHONDONTWRITEBYTECODE=1 python3 -B
   engain_door.py ingest --source <chapter>.md` for all four chapters,
   from `/mnt/data-drive/godot_engain_3d_avatar`, same invocation shape
   Dragon itself used for chapter 1's original ingestion.

All four completed successfully (`"ok": true, "ingestion_status":
"created"`), each writing real chapterroom/passroom artifacts.

## Scene counts — none match the source's real structure

```text
Chapter                  Words   Scenes produced   Expected (per user)
001_the_ethereal_vigil   3139    4                  1
002_molten_descent       2775    4                  (not yet specified)
003_first_contact        2390    3                  7
004_the_convergence      3163    4                  (not yet specified)
```

Every chapter still used `boundary_method: mechanical_word_chunk`
(`--target-words 900`) — the scene counts track word count almost
exactly (`ceil(words / ~900)`), completely independent of any authored
structure in the text. Cleaning up chapter 1's source (removing the
duplicated `001.2`/`001.3` beat-label markers, per `772b26b`) did not
change its scene count at all — it's still 4, for the same mechanical
reason it was 4 before.

## Chapter 3 is now the clearest possible evidence for defect #1

Checked chapter 3's source directly. It has a **fully explicit,
structured, five-plus-day scene system**, not a subtle inline marker:

```text
day 1
scene 003.1 — first night on the beach
scene meta:
...

day 2
scene 003.2 — failed approach
scene meta:
continuity: Follows the first night on the beach in scene 003.1
...

day 3
scene 003.3 — solo approach
scene meta:
continuity: Follows the failed group approach on day 2 in scene 003.2
...

day 4
scene 003.4 — art offering
...

day 5
scene 003.5 — water breakthrough
...
```

Each scene has its own `day N` label, `scene 003.N —` heading, a
`scene meta:` block, and an explicit `continuity: Follows ... in scene
003.N-1` cross-reference to the previous one. This is about as
unambiguous an authored-boundary signal as source text could carry.
**The current pipeline produced exactly 3 mechanical scenes for this
chapter, ignoring all of it.** This is now the single clearest,
highest-confidence case for prioritizing the scene-heading-detection
fix (defect #1) — not a borderline or ambiguous one.

## Entity-extraction noise is systemic, not chapter-1-specific

The `Tran` false positive (confirmed baked into chapter 1's `@entities`
in `e2a6964`) reappears in every chapter run this session:

```text
Chapter 1: Entities: Mordain, Pelagor, Syreth, Theron, Tran, Vaelith
Chapter 2: Entities: Elyraen, Mordain, Olythae, Pelagor, Senareth, Tran, Vairis
Chapter 3: Entities: Elyraen, Kyreth, Olythae, Pelagor, Senareth, Torhh, Tran, Vairis
Chapter 4: (not yet inspected in detail)
```

Lyaris remains absent from chapter 1's fresh extraction, same as
before this rerun (`e2a6964` already established this; unchanged here).

The Sept 15 removal of the low-mention entity filter (`3f58af9`) is
now visibly trading under-extraction for noise: every chapter's ingest
log shows multiple `UNKNOWN ENTITY PRESERVED` lines for what are
almost certainly not characters — `Aeon`, `Keepers` (ch1, already
known), `Akashic`, `Zoup` (ch2), `Giant`, `Follows`, `Tomorrow` (ch3).
`Follows` and `Tomorrow` in particular are common words/sentence-
initial capitals, not names — concrete evidence that removing the
frequency floor without adding a stronger noise filter created a new
class of false positive across every chapter, not just persisted an
old one.

## `semantic_environment_extractor` is still missing

Recurred for chapter 1, scenes 2 and 3 (identical to the original
ingestion): `[pass5] Semantic Extractor failed: No module named
'semantic_environment_extractor'`. Confirms defect #5 is unrelated to
source content and will recur on every chapter until the module issue
itself is fixed.

## One new, previously-unseen data point

Chapter 2's scene 4 came back completely empty: `signal_count: 0`,
`Analyzed 0 characters, 0 scene objects`, `Characters: 0`, `Events: 0`.
Not investigated further here — likely just a short mechanical tail
chunk with little content — but worth knowing this baseline includes
at least one near-empty scene, not just over-full ones.

## Net

This is the clean "before" baseline requested. All five previously
identified defects reproduce here, on freshly-cleaned source text,
across multiple chapters — none of them were source-quality artifacts
that resolved themselves once the vault was cleaned up. Chapter 3 in
particular now provides the strongest, least ambiguous test case for
defect #1's fix: 7 real, explicitly-marked, cross-referenced scenes,
mechanically flattened to 3.

## What was not done

The five defects were not fixed. No comparison against the eventual
"after" rerun has been made — this receipt exists specifically so that
comparison can happen later without re-deriving the baseline.
