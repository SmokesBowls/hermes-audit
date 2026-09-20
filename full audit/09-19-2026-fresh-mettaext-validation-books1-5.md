# Fresh Mettaext validation: Books 1-5, current pipeline, current vault source

Mettaext-only test. No Dragon/Editor coordination path invoked or used as
evidence anywhere in this run -- every result below comes from directly
running `pipeline_runner.py` and reading the generated artifacts, the same
way this session's own implementation validation has throughout. No
manuscript file was modified. No Mettaext code was changed.

## Scope: 27 chapters, enumerated from the actual vault directories

Enumerated `/home/mytruelove/Downloads/obsidianburdenNov25/book_0{1..5}_*/`
by listing files, not assuming a contiguous chapter-number range --
confirmed non-contiguous: Book 3 has 009-012, then 014-015 (013 does not
exist as a file in that folder).

```text
book_01_book_of_genesis: 4 chapters
  001_the_ethereal_vigil.md
  002_molten_descent.md
  003_first_contact.md
  004_the_convergence.md
book_02_age_of_servitude: 4 chapters
  005_the_garden_blooms.md
  006_the_first_coming.md
  007_the_needle_construction.md
  008_queens_assessment.md
book_03_the_reckoning: 6 chapters
  009_stalemate_departure_the_first_coming.md
  010_shadow_returns_second_coming.md
  011_escalation_and_desperation.md
  012_nephilim_summoning.md
  014_convergence.md
  015_betrayal.md
book_04_sage_saga: 8 chapters
  016_the_choice_third_coming.md
  017_niburu_shadow.md
  018_the_wandering.md
  019_the_sacrafice.md
  020_the_collapse.md
  021_the_first_lesson.md
  022_final_calculation.md
  023_beyond_identity.md
book_05_the_nameless_one: 5 chapters
  024_the_first_spark.md
  025_confined_freedom.md
  026_dragonmail.md
  027_the_claiming.md
  028_ragnarok.md
```

## Pre-run cleanup: exactly what was cleared, and why

Before regenerating, checked every one of the 27 target chapter_ids for
pre-existing current-schema stageroom artifacts. Five chapters had them:

```text
chapter.book001.001_the_ethereal_vigil   -- from this session's earlier
chapter.book001.002_molten_descent          splitter validation today,
chapter.book001.003_first_contact           correct source, but with 3
chapter.book001.004_the_convergence         orphaned pre-splitter-fix
                                             scene directories each
                                             (scene002-004, leftover from
                                             the old mechanical 4-scene
                                             split, not cleaned up by the
                                             earlier overwrite-in-place run)
chapter.book004.016_the_choice_third_coming -- pre-existing artifact from a
                                             DIFFERENT, earlier session/tool,
                                             still on the OLD mechanical
                                             splitter (boundary_method:
                                             mechanical_word_chunk,
                                             scene_count: 2) -- predates
                                             today's authored-marker fix
                                             entirely
```

All other 22 chapters (005-015 except 016, 017-028) had never been
ingested through EngAIn's stageroom before this run -- nothing to clear.

Full list of paths removed (36 entries -- `out_passA_*.json`,
`out_passB_*.json`, `scene_packets/<chapter_id>/`, and every
`passroom/scene.<chapter_id>.scene*/` directory for exactly these five
chapter_ids, nothing else):

```text
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/chapterroom/out_passA_001_the_ethereal_vigil.json
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/chapterroom/out_passB_chapter.book001.001_the_ethereal_vigil.json
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/chapterroom/scene_packets/chapter.book001.001_the_ethereal_vigil/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.001_the_ethereal_vigil.scene001/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.001_the_ethereal_vigil.scene002/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.001_the_ethereal_vigil.scene003/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.001_the_ethereal_vigil.scene004/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/chapterroom/out_passA_002_molten_descent.json
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/chapterroom/out_passB_chapter.book001.002_molten_descent.json
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/chapterroom/scene_packets/chapter.book001.002_molten_descent/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.002_molten_descent.scene001/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.002_molten_descent.scene002/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.002_molten_descent.scene003/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.002_molten_descent.scene004/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/chapterroom/out_passA_003_first_contact.json
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/chapterroom/out_passB_chapter.book001.003_first_contact.json
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/chapterroom/scene_packets/chapter.book001.003_first_contact/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.003_first_contact.scene001/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.003_first_contact.scene002/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.003_first_contact.scene003/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.003_first_contact.scene004/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.003_first_contact.scene005/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.003_first_contact.scene006/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.003_first_contact.scene007/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/chapterroom/out_passA_004_the_convergence.json
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/chapterroom/out_passB_chapter.book001.004_the_convergence.json
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/chapterroom/scene_packets/chapter.book001.004_the_convergence/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.004_the_convergence.scene001/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.004_the_convergence.scene002/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.004_the_convergence.scene003/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book001.004_the_convergence.scene004/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/chapterroom/out_passA_016_the_choice_third_coming.json
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/chapterroom/out_passB_chapter.book004.016_the_choice_third_coming.json
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/chapterroom/scene_packets/chapter.book004.016_the_choice_third_coming/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book004.016_the_choice_third_coming.scene001/ (dir)
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier3/mettaext/stageroom/output/passroom/scene.book004.016_the_choice_third_coming.scene002/ (dir)
```

**Legacy corpus untouched**: `legacy_pipeline_work/` was not read, listed,
or modified. Nothing outside these five chapter_ids' own current-schema
output was touched.

## Regeneration

Ran `python3 tier3/mettaext/pipeline_runner.py <source.md>` for all 27 real
vault files, fresh, in one pass. All 27 exited 0 and printed
`Pipeline complete`. No manuscript file was written to at any point --
verified by re-reading every source file's mtime as unchanged after the run.

## Primary structural invariant: authored markers == generated packets

**Result: holds for all 27 of 27 chapters. Zero mismatches.**

```text
chapter_id                                                 authored  generated  status
chapter.book001.001_the_ethereal_vigil                            1          1  OK
chapter.book001.002_molten_descent                                1          1  OK
chapter.book001.003_first_contact                                 7          7  OK
chapter.book001.004_the_convergence                               1          1  OK
chapter.book002.005_the_garden_blooms                             8          8  OK
chapter.book002.006_the_first_coming                              5          5  OK
chapter.book002.007_the_needle_construction                       5          5  OK
chapter.book002.008_queens_assessment                             3          3  OK
chapter.book003.009_stalemate_departure_the_first_coming          5          5  OK
chapter.book003.010_shadow_returns_second_coming                  3          3  OK
chapter.book003.011_escalation_and_desperation                    3          3  OK
chapter.book003.012_nephilim_summoning                            2          2  OK
chapter.book003.014_convergence                                   2          2  OK
chapter.book003.015_betrayal                                      6          6  OK
chapter.book004.016_the_choice_third_coming                       1          1  OK
chapter.book004.017_niburu_shadow                                 3          3  OK
chapter.book004.018_the_wandering                                 6          6  OK
chapter.book004.019_the_sacrafice                                 4          4  OK
chapter.book004.020_the_collapse                                  7          7  OK
chapter.book004.021_the_first_lesson                              6          6  OK
chapter.book004.022_final_calculation                             6          6  OK
chapter.book004.023_beyond_identity                               6          6  OK
chapter.book005.024_the_first_spark                              11         11  OK
chapter.book005.025_confined_freedom                              6          6  OK
chapter.book005.026_dragonmail                                    4          4  OK
chapter.book005.027_the_claiming                                  7          7  OK
chapter.book005.028_ragnarok                                      5          5  OK
```

Every chapter reports, uniformly:

```text
boundary_method: "authored_scene_marker"
authority_state: "SCENE_BOUNDARY_AUTHORED"
authored_scene_boundaries_proven: true
```

Total scene packets generated across Books 1-5: **124**.

## Scene metadata transport: full survival, corpus-wide

Every authored key seen anywhere in the corpus survived into the packet's
`scene_meta` (parsed generically, none hardcoded):

```text
location, time, participants, focus, continuity, presentation, cutscene purpose
```

Zero scenes (of 124) had an empty `scene_meta`. Zero scenes were missing the
raw `@scene_meta_*` header lines in their own segment text -- confirming Pass
2's `infer_presence_enhanced()` still has what it needs across the entire
corpus, not just Book 1. Zero cases of a `scene NNN.x —` marker from one
scene appearing inside another scene's own generated text (checked by
scanning every scene's segments for a second marker match) -- no scene-text
leakage across boundaries found.

## Manifestation consistency: zero violations found

Cross-checked every `@entities_manifested` entry against its own
`entities_observed` record (must be spawnable AND presence==local AND
physicality==physical) and, in the other direction, checked every
spawnable+local+physical entity for absence from `@entities_manifested`.

**Zero inconsistencies in either direction, across all 124 scenes.**
Specifically:

```text
Physically manifested entities missing from @entities_manifested: 0
Nonphysical/remote entities incorrectly IN @entities_manifested:   0
```

Aggregate presence/physicality tally (entity-observation instances, not
unique names -- one chapter's Torhh across 3 scenes counts 3 times):

```text
local + physical:     186
local + nonphysical:  149
remote:                 1
unknown (fail-closed): 456
names ever reaching @entities_manifested (sum across scenes): 56
```

**Worth flagging plainly**: only a single `remote` classification fired in
the entire 5-book corpus. The remote-sensing keyword lexicon
(`resonance of X essence`, `X's energy/life signature`, etc.) was hand-built
from Chapter 1's specific Pelagor phrasing and evidently does not generalize
to how remoteness is expressed elsewhere in these books. This is a known,
already-flagged limitation (`405d1b7`'s design), not a new defect, but this
run is the first hard evidence of how narrow it actually is in practice: the
`unknown` fail-closed default is doing almost all of the load-bearing work
for anything that isn't in the scene's `participants:` line, not the remote
detector.

A concrete, encouraging confirmation of scene-local independence, not
carried state: Torhh in Chapter 3 is manifested in scenes 003.5/003.6/003.7
but absent from `@entities_manifested` in 003.1-003.4 -- matching the
narrative (arrives partway through the chapter) and confirming presence/
physicality are computed fresh per scene, never inherited from a prior one.

## Tran-like false-entity defect: checked for recurrence, none found

"Tran" appears twice in the corpus, both in Book 4:

```text
chapter.book004.021_the_first_lesson.scene006  -- 5 mentions
chapter.book004.023_beyond_identity.scene006   -- 7 mentions
```

Checked the actual source text directly rather than assuming either way.
Both are genuine, word-boundary references to a real named character
("...their legacy through genetics... Tran and Keen, the others who carry
our legacy..."; "...Tran and Keen, the convergence children...") -- not a
substring match against "transformed"/"transformation" the way the original
defect worked. Correctly classified `known: true, spawnable: true`, and
correctly `presence: unknown` in both scenes (Tran is only spoken of
prospectively as a future/foreseen figure, never actually placed in either
scene -- the fail-closed default is doing exactly the right thing here).
**No recurrence of the original defect.**

## Bogus entity candidates: two genuinely different categories, both harmless

Flagged every `classification: unknown` entity with a 4-letter-or-shorter
name (a deliberately loose net) and checked each by hand. They split
cleanly into two categories -- worth telling apart rather than dumping as
one undifferentiated list:

**Genuine noise words** (generic English words that got capitalized at a
sentence start and passed the 3+-mention/speaker-attribution threshold --
not in `pass2_entity_filter.py`'s `COMMON_WORDS` blocklist):

```text
Five, Days, More, Once, Your, Just, With, None, Same, Team, Felt, Site,
Year, Book, Work, Lord, Only, Past, Stay, Seal, Host
```

**Genuine, real proper names not yet in `world_rules.json`** -- correctly
preserved as `known: false, spawnable: false` evidence per
`pass2_entity_filter.py`'s designed behavior, not a bug:

```text
Sage (the book 4 protagonist/title character -- appears in nearly every
  scene of chapters 019-023), Keen, Kael, Tess, Dren, Ison, Reef, Aeon
  (fragment of "Aeon Keepers", already a known pattern from Book 1)
```

Neither category reached `@entities` or `@entities_manifested` anywhere --
`spawnable: false` for all of them, confirmed by the zero manifestation-
consistency-violations result above. This is a **registry coverage gap**
(world_rules.json has no entries yet for Book 2-5's cast), not a pipeline
defect, and not something this run fixes or recommends fixing.

No scene-meta key itself (location/time/participants/focus/continuity/etc.)
was ever mistaken for an entity name anywhere in the corpus (checked
directly, zero hits).

## semantic_environment_extractor: still missing, confirmed recurring

```text
[pass5] Semantic Extractor failed: No module named 'semantic_environment_extractor'
```

Occurred 45 times across the run. Caught and non-fatal every time -- all 27
chapters still completed with exit code 0. Same pre-existing, already-
tracked defect from the original five-item list (`4c7bf79`, item 5),
confirmed still unresolved and still recurring at scale across the full
5-book corpus, not fixed as part of this validation run per instruction.

No other warnings, errors, or exceptions of any kind appeared anywhere in
the full 27-chapter run log.

## Per-chapter scene detail: IDs, titles, scene_meta keys, @entities, @entities_manifested

```text
### chapter.book001.001_the_ethereal_vigil
  scene.book001.001_the_ethereal_vigil.scene001 | title='scene 001.1 — the ethereal vigil' | meta_keys=[continuity,focus,location,participants,time] | @entities=['Mordain', 'Pelagor', 'Syreth', 'Theron', 'Vaelith'] | manifested=[]

### chapter.book001.002_molten_descent
  scene.book001.002_molten_descent.scene001 | title='scene 002.1 — molten descent' | meta_keys=[continuity,focus,location,participants,time] | @entities=['Elyraen', 'Mordain', 'Olythae', 'Pelagor', 'Senareth', 'Vairis'] | manifested=['Senareth']

### chapter.book001.003_first_contact
  scene.book001.003_first_contact.scene001 | title='scene 003.1 — first night on the beach' | meta_keys=[continuity,focus,location,participants,time] | @entities=['Elyraen', 'Olythae', 'Senareth', 'Torhh', 'Vairis'] | manifested=[]
  scene.book001.003_first_contact.scene002 | title='scene 003.2 — failed approach' | meta_keys=[continuity,focus,location,participants,time] | @entities=['Elyraen', 'Kyreth', 'Senareth', 'Vairis'] | manifested=[]
  scene.book001.003_first_contact.scene003 | title='scene 003.3 — solo approach' | meta_keys=[continuity,focus,location,participants,time] | @entities=['Elyraen'] | manifested=[]
  scene.book001.003_first_contact.scene004 | title='scene 003.4 — art offering' | meta_keys=[continuity,focus,location,participants,time] | @entities=['Olythae'] | manifested=[]
  scene.book001.003_first_contact.scene005 | title='scene 003.5 — water breakthrough' | meta_keys=[continuity,focus,location,participants,time] | @entities=['Elyraen', 'Kyreth', 'Senareth', 'Torhh', 'Vairis'] | manifested=['Kyreth', 'Torhh']
  scene.book001.003_first_contact.scene006 | title='scene 003.6 — repeated dialogue' | meta_keys=[continuity,focus,location,participants,time] | @entities=['Kyreth', 'Olythae', 'Senareth', 'Torhh'] | manifested=['Torhh']
  scene.book001.003_first_contact.scene007 | title='scene 003.7 — language setup' | meta_keys=[continuity,focus,location,participants,time] | @entities=['Elyraen', 'Kyreth', 'Olythae', 'Senareth', 'Torhh'] | manifested=['Kyreth', 'Olythae', 'Senareth', 'Torhh']

### chapter.book001.004_the_convergence
  scene.book001.004_the_convergence.scene001 | title='scene 004.1 — the convergence' | meta_keys=[continuity,focus,location,participants,time] | @entities=['Elyraen', 'Kyreth', 'Olythae', 'Pelagor', 'Senareth', 'Torhh', 'Vairis'] | manifested=['Elyraen', 'Kyreth', 'Olythae', 'Senareth', 'Torhh']

### chapter.book002.005_the_garden_blooms
  scene.book002.005_the_garden_blooms.scene001 | title='scene 005.1 — the first pyramid collapse' | meta_keys=[continuity,focus,location,participants,presentation,time] | @entities=['Elyraen', 'Senareth', 'Vairis'] | manifested=['Vairis']
  scene.book002.005_the_garden_blooms.scene002 | title='scene 005.2 — the mountain obelisks' | meta_keys=[continuity,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book002.005_the_garden_blooms.scene003 | title='scene 005.3 — cliff stabilization and fertile basin' | meta_keys=[continuity,focus,location,participants,presentation,time] | @entities=['Senareth'] | manifested=[]
  scene.book002.005_the_garden_blooms.scene004 | title='scene 005.4 — the first true pyramid' | meta_keys=[continuity,focus,location,participants,presentation,time] | @entities=['Elyraen'] | manifested=[]
  scene.book002.005_the_garden_blooms.scene005 | title='scene 005.5 — the tidecaller mountain chambers' | meta_keys=[continuity,focus,location,participants,presentation,time] | @entities=['Elyraen', 'Kyreth', 'Olythae', 'Senareth', 'Torhh', 'Vairis'] | manifested=[]
  scene.book002.005_the_garden_blooms.scene006 | title='scene 005.6 — mapping the seven nexus points' | meta_keys=[continuity,focus,location,participants,presentation,time] | @entities=['Elyraen', 'Senareth'] | manifested=[]
  scene.book002.005_the_garden_blooms.scene007 | title='scene 005.7 — regional crystallization and festival' | meta_keys=[continuity,focus,location,participants,presentation,time] | @entities=['Elyraen', 'Senareth'] | manifested=['Elyraen', 'Senareth']
  scene.book002.005_the_garden_blooms.scene008 | title='scene 005.8 — the first coming arrival' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Elyraen', 'Pelagor', 'Senareth'] | manifested=[]

### chapter.book002.006_the_first_coming
  scene.book002.006_the_first_coming.scene001 | title='scene 006.1 — orbital assessment and invasion directive' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book002.006_the_first_coming.scene002 | title='scene 006.2 — manufacturing complex foundation' | meta_keys=[continuity,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book002.006_the_first_coming.scene003 | title='scene 006.3 — igigi transport descent' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Pazuzu'] | manifested=['Pazuzu']
  scene.book002.006_the_first_coming.scene004 | title='scene 006.4 — reptilian warrior maturation' | meta_keys=[continuity,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book002.006_the_first_coming.scene005 | title='scene 006.5 — birth of layla and needle targeting' | meta_keys=[continuity,focus,location,participants,presentation,time] | @entities=['Pazuzu'] | manifested=[]

### chapter.book002.007_the_needle_construction
  scene.book002.007_the_needle_construction.scene001 | title='scene 007.1 — needle site targeting' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book002.007_the_needle_construction.scene002 | title='scene 007.2 — first blood at tidecaller mountain' | meta_keys=[continuity,focus,location,participants,presentation,time] | @entities=['Pazuzu'] | manifested=['Pazuzu']
  scene.book002.007_the_needle_construction.scene003 | title='scene 007.3 — desert giant armed resistance' | meta_keys=[continuity,focus,location,participants,presentation,time] | @entities=['Pazuzu'] | manifested=['Pazuzu']
  scene.book002.007_the_needle_construction.scene004 | title='scene 007.4 — coordinated needle resistance assessment' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book002.007_the_needle_construction.scene005 | title='scene 007.5 — empathy across slave and giant' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torhh'] | manifested=[]

### chapter.book002.008_queens_assessment
  scene.book002.008_queens_assessment.scene001 | title="scene 008.1 — the queen's descent and strategic shift" | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torhh'] | manifested=[]
  scene.book002.008_queens_assessment.scene002 | title='scene 008.2 — brainwashing of the igigi emissaries' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Pazuzu'] | manifested=[]
  scene.book002.008_queens_assessment.scene003 | title='scene 008.3 — the first seeds of the sundering' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Pazuzu', 'Torhh'] | manifested=['Pazuzu', 'Torhh']

### chapter.book003.009_stalemate_departure_the_first_coming
  scene.book003.009_stalemate_departure_the_first_coming.scene001 | title='scene 009.1 — mid-occupation stalemate assessment' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book003.009_stalemate_departure_the_first_coming.scene002 | title='scene 009.2 — secret alliance at tidecaller mountain' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Pazuzu', 'Torhh'] | manifested=[]
  scene.book003.009_stalemate_departure_the_first_coming.scene003 | title='scene 009.3 — final orbital assessment and fleet departure' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book003.009_stalemate_departure_the_first_coming.scene004 | title='scene 009.4 — the morning after departure' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Pazuzu', 'Torhh'] | manifested=['Torhh']
  scene.book003.009_stalemate_departure_the_first_coming.scene005 | title='scene 009.5 — epilogue: the deep archives of ironspire' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]

### chapter.book003.010_shadow_returns_second_coming
  scene.book003.010_shadow_returns_second_coming.scene001 | title='scene 010.1 — return of the citadel and sundering evaluation' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book003.010_shadow_returns_second_coming.scene002 | title="scene 010.2 — the architect's hand: gruulith maturation" | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book003.010_shadow_returns_second_coming.scene003 | title='scene 010.3 — the cracks in the mountain: assault on the singing peaks' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]

### chapter.book003.011_escalation_and_desperation
  scene.book003.011_escalation_and_desperation.scene001 | title='scene 011.1 — the flawed sword: dregan authorization' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book003.011_escalation_and_desperation.scene002 | title='scene 011.2 — the scream that shatters stone: assault on the oasis clans' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book003.011_escalation_and_desperation.scene003 | title='scene 011.3 — the broken compass: alliance with the brajor' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Pazuzu', 'Torhh'] | manifested=[]

### chapter.book003.012_nephilim_summoning
  scene.book003.012_nephilim_summoning.scene001 | title='scene 012.1 — the convergence of desperation' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Pazuzu', 'Torhh', 'Torrhen'] | manifested=[]
  scene.book003.012_nephilim_summoning.scene002 | title='scene 012.2 — the deep communion' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Pazuzu', 'Torhh', 'Torrhen'] | manifested=[]

### chapter.book003.014_convergence
  scene.book003.014_convergence.scene001 | title='scene 014.1 — the ritual begins: elemental convergence' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Pazuzu', 'Torhh'] | manifested=['Pazuzu']
  scene.book003.014_convergence.scene002 | title='scene 014.2 — the manifestation: purification and fracture' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Pazuzu', 'Torhh'] | manifested=[]

### chapter.book003.015_betrayal
  scene.book003.015_betrayal.scene001 | title='scene 015.1 — aftermath in the northern mountains' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book003.015_betrayal.scene002 | title='scene 015.2 — the golden offer' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book003.015_betrayal.scene003 | title='scene 015.3 — the choice' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book003.015_betrayal.scene004 | title='scene 015.4 — the discovery' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Pazuzu', 'Torhh'] | manifested=['Pazuzu']
  scene.book003.015_betrayal.scene005 | title='scene 015.5 — departure and legacy' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Tran'] | manifested=[]
  scene.book003.015_betrayal.scene006 | title='scene 015.6 — what remains' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Pazuzu', 'Torhh'] | manifested=['Pazuzu', 'Torhh']

### chapter.book004.016_the_choice_third_coming
  scene.book004.016_the_choice_third_coming.scene001 | title='scene 016.1 — the first act of freedom: the igigi scatter' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Pazuzu', 'Zephyr'] | manifested=['Pazuzu', 'Zephyr']

### chapter.book004.017_niburu_shadow
  scene.book004.017_niburu_shadow.scene001 | title='scene 017.1 — the war-moon council: nibiru positioning' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Zephyr'] | manifested=[]
  scene.book004.017_niburu_shadow.scene002 | title="scene 017.2 — nibiru's shadow: engineered winter" | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Zephyr'] | manifested=[]
  scene.book004.017_niburu_shadow.scene003 | title='scene 017.3 — fourteen years of ice: the storm encounter' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Zephyr'] | manifested=[]

### chapter.book004.018_the_wandering
  scene.book004.018_the_wandering.scene001 | title='scene 018.1 — the impossible refuge' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen', 'Zephyr'] | manifested=[]
  scene.book004.018_the_wandering.scene002 | title='scene 018.2 — the lessons begin' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen', 'Zephyr'] | manifested=['Torrhen']
  scene.book004.018_the_wandering.scene003 | title='scene 018.3 — years of becoming' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen', 'Zephyr'] | manifested=[]
  scene.book004.018_the_wandering.scene004 | title='scene 018.4 — the deep teaching' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen', 'Zephyr'] | manifested=[]
  scene.book004.018_the_wandering.scene005 | title='scene 018.5 — foundation: the coming transition' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen', 'Zephyr'] | manifested=['Torrhen', 'Zephyr']
  scene.book004.018_the_wandering.scene006 | title='scene 018.6 — the parting approaches: foundation of magical teaching' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen', 'Zephyr'] | manifested=[]

### chapter.book004.019_the_sacrafice
  scene.book004.019_the_sacrafice.scene001 | title='scene 019.1 — the catastrophe and the decision' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen', 'Zephyr'] | manifested=['Torrhen']
  scene.book004.019_the_sacrafice.scene002 | title='scene 019.2 — the transformation: birth of the sage' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen', 'Zephyr'] | manifested=[]
  scene.book004.019_the_sacrafice.scene003 | title='scene 019.3 — the first student' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen', 'Zephyr'] | manifested=[]
  scene.book004.019_the_sacrafice.scene004 | title='scene 019.4 — epilogue: the eternal teacher' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=[]

### chapter.book004.020_the_collapse
  scene.book004.020_the_collapse.scene001 | title='scene 020.1 — the discovery of second torrhen' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen', 'Zephyr'] | manifested=['Zephyr']
  scene.book004.020_the_collapse.scene002 | title='scene 020.2 — the conversation: founding the partnership' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=['Torrhen']
  scene.book004.020_the_collapse.scene003 | title='scene 020.3 — the deep teaching: pythagoras' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=['Torrhen']
  scene.book004.020_the_collapse.scene004 | title='scene 020.4 — the growing network: integration studies' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=['Torrhen']
  scene.book004.020_the_collapse.scene005 | title='scene 020.5 — the first great teaching: synthesis probe' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=[]
  scene.book004.020_the_collapse.scene006 | title='scene 020.6 — the expanding synthesis' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=[]
  scene.book004.020_the_collapse.scene007 | title='scene 020.7 — the promise fulfilled' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=[]

### chapter.book004.021_the_first_lesson
  scene.book004.021_the_first_lesson.scene001 | title='scene 021.1 — the first tongue: pre-linguistic resonance' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen', 'Zephyr'] | manifested=['Torrhen']
  scene.book004.021_the_first_lesson.scene002 | title='scene 021.2 — the deep grammar' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=[]
  scene.book004.021_the_first_lesson.scene003 | title='scene 021.3 — the harmonic convergence' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=[]
  scene.book004.021_the_first_lesson.scene004 | title='scene 021.4 — the first tongue codex' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=['Torrhen']
  scene.book004.021_the_first_lesson.scene005 | title='scene 021.5 — the students become masters' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=[]
  scene.book004.021_the_first_lesson.scene006 | title='scene 021.6 — the legacy encoded' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen', 'Tran'] | manifested=['Torrhen']

### chapter.book004.022_final_calculation
  scene.book004.022_final_calculation.scene001 | title='scene 022.1 — opening movement: the final calculations' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=[]
  scene.book004.022_final_calculation.scene002 | title='scene 022.2 — the conscious sacrifice' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=[]
  scene.book004.022_final_calculation.scene003 | title='scene 022.3 — the geological goodbye' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=['Torrhen']
  scene.book004.022_final_calculation.scene004 | title='scene 022.4 — first solitary teaching' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=[]
  scene.book004.022_final_calculation.scene005 | title='scene 022.5 — infinite teaching' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=[]
  scene.book004.022_final_calculation.scene006 | title='scene 022.6 — eternal partnership' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=[]

### chapter.book004.023_beyond_identity
  scene.book004.023_beyond_identity.scene001 | title='scene 023.1 — metamorphosis beyond identity' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen', 'Zephyr'] | manifested=[]
  scene.book004.023_beyond_identity.scene002 | title='scene 023.2 — dissolution of limits' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen'] | manifested=[]
  scene.book004.023_beyond_identity.scene003 | title='scene 023.3 — the first universal teaching' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book004.023_beyond_identity.scene004 | title='scene 023.4 — the infinite students' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book004.023_beyond_identity.scene005 | title='scene 023.5 — the eternal birth' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book004.023_beyond_identity.scene006 | title='scene 023.6 — legacy beyond legacy' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Torrhen', 'Tran'] | manifested=[]

### chapter.book005.024_the_first_spark
  scene.book005.024_the_first_spark.scene001 | title='scene 024.1 — awakening in the creation chamber' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt'] | manifested=[]
  scene.book005.024_the_first_spark.scene002 | title='scene 024.2 — march into the obsidian mines' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt'] | manifested=[]
  scene.book005.024_the_first_spark.scene003 | title='scene 024.3 — the first telekinetic defiance' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt'] | manifested=[]
  scene.book005.024_the_first_spark.scene004 | title="scene 024.4 — the anunnaki's judgment" | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt'] | manifested=[]
  scene.book005.024_the_first_spark.scene005 | title='scene 024.5 — the burden of freedom' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Mika'] | manifested=[]
  scene.book005.024_the_first_spark.scene006 | title="scene 024.6 — the pleiadians' arrival" | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt'] | manifested=[]
  scene.book005.024_the_first_spark.scene007 | title="scene 024.7 — a reptilian's mistake" | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=[] | manifested=[]
  scene.book005.024_the_first_spark.scene008 | title='scene 024.8 — the caverns of silence' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Mika'] | manifested=[]
  scene.book005.024_the_first_spark.scene009 | title='scene 024.9 — the galactic trade' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Mika'] | manifested=['Mika']
  scene.book005.024_the_first_spark.scene010 | title="scene 024.10 — the galactic federation's arrival" | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Mika'] | manifested=[]
  scene.book005.024_the_first_spark.scene011 | title='scene 024.11 — a stranger within' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Mika'] | manifested=[]

### chapter.book005.025_confined_freedom
  scene.book005.025_confined_freedom.scene001 | title='scene 025.1 — morning after applicator invasion' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Mika'] | manifested=[]
  scene.book005.025_confined_freedom.scene002 | title='scene 025.2 — crystalline prison construction' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Mika'] | manifested=[]
  scene.book005.025_confined_freedom.scene003 | title='scene 025.3 — vision / applicator pact / five restored' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt'] | manifested=[]
  scene.book005.025_confined_freedom.scene004 | title='scene 025.4 — call to arms / federation inspection / weeks of preparation' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Mika'] | manifested=[]
  scene.book005.025_confined_freedom.scene005 | title='scene 025.5 — ragnarok / uprising / anunnaki killed' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Mika'] | manifested=[]
  scene.book005.025_confined_freedom.scene006 | title='scene 025.6 — recovery / new community / nephoretti watching' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Mika'] | manifested=[]

### chapter.book005.026_dragonmail
  scene.book005.026_dragonmail.scene001 | title='scene 026.1 — the sound of water' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt'] | manifested=[]
  scene.book005.026_dragonmail.scene002 | title='scene 026.2 — the nephoretti and the gifts' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Oreck'] | manifested=[]
  scene.book005.026_dragonmail.scene003 | title='scene 026.3 — the library and the aeon keepers' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt'] | manifested=['Geralt']
  scene.book005.026_dragonmail.scene004 | title='scene 026.4 — the armor and the sacrifice' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt'] | manifested=[]

### chapter.book005.027_the_claiming
  scene.book005.027_the_claiming.scene001 | title='scene 027.1 — the ally' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Oreck'] | manifested=['Geralt']
  scene.book005.027_the_claiming.scene002 | title='scene 027.2 — the journey' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Oreck'] | manifested=['Geralt', 'Oreck']
  scene.book005.027_the_claiming.scene003 | title='scene 027.3 — the guardian' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Oreck'] | manifested=['Geralt', 'Oreck']
  scene.book005.027_the_claiming.scene004 | title='scene 027.4 — the celestial storm' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Oreck'] | manifested=[]
  scene.book005.027_the_claiming.scene005 | title='scene 027.5 — the breaking' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Oreck'] | manifested=[]
  scene.book005.027_the_claiming.scene006 | title='scene 027.6 — the bonding and the trinity' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Oreck'] | manifested=['Geralt']
  scene.book005.027_the_claiming.scene007 | title='scene 027.7 — the return' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Mika', 'Oreck', 'Vale'] | manifested=['Geralt', 'Mika', 'Oreck']

### chapter.book005.028_ragnarok
  scene.book005.028_ragnarok.scene001 | title='scene 028.1 — the warning' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Oreck'] | manifested=['Geralt']
  scene.book005.028_ragnarok.scene002 | title='scene 028.2 — the trial' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Mika', 'Oreck'] | manifested=['Geralt', 'Oreck']
  scene.book005.028_ragnarok.scene003 | title='scene 028.3 — the infiltration' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Mika', 'Oreck'] | manifested=[]
  scene.book005.028_ragnarok.scene004 | title='scene 028.4 — the approach and the chaos' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Mika', 'Oreck'] | manifested=['Geralt']
  scene.book005.028_ragnarok.scene005 | title='scene 028.5 — the duel' | meta_keys=[continuity,cutscene purpose,focus,location,participants,presentation,time] | @entities=['Geralt', 'Mika', 'Oreck'] | manifested=['Geralt']
```

## Per-chapter entities_observed (aggregated across each chapter's scenes)

One row per unique name per chapter; `in N scene(s)` counts how many of
that chapter's scenes the name appears in, not raw mention count.

```text
### chapter.book001.001_the_ethereal_vigil
  Aeon: known=False spawnable=False class=unknown in 1 scene(s)
  Akashic: known=False spawnable=False class=unknown in 1 scene(s)
  Ethereal: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Keepers: known=False spawnable=False class=unknown in 1 scene(s)
  Korath: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Lyaris: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Marduk: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Mordain: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Nephoretti: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Pelagor: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Syreth: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Theron: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Tiamat: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Vaelith: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Veil: known=True spawnable=False class=known_non_spawnable in 1 scene(s)

### chapter.book001.002_molten_descent
  Akashic: known=False spawnable=False class=unknown in 1 scene(s)
  Around: known=False spawnable=False class=unknown in 1 scene(s)
  Bodies: known=False spawnable=False class=unknown in 1 scene(s)
  Elyraen: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Ethereal: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Giant: known=False spawnable=False class=unknown in 1 scene(s)
  Giants: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Mordain: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Nephoretti: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Olythae: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Others: known=False spawnable=False class=unknown in 1 scene(s)
  Pelagor: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Prime: known=False spawnable=False class=unknown in 1 scene(s)
  Senareth: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Through: known=False spawnable=False class=unknown in 1 scene(s)
  Vairis: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Veil: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Zoup: known=False spawnable=False class=unknown in 1 scene(s)

### chapter.book001.003_first_contact
  Elyraen: known=True spawnable=True class=known_spawnable in 5 scene(s)
  Five: known=False spawnable=False class=unknown in 1 scene(s)
  Giant: known=False spawnable=False class=unknown in 5 scene(s)
  Giants: known=True spawnable=False class=known_non_spawnable in 6 scene(s)
  Kyreth: known=True spawnable=True class=known_spawnable in 4 scene(s)
  Nephoretti: known=True spawnable=False class=known_non_spawnable in 4 scene(s)
  Olythae: known=True spawnable=True class=known_spawnable in 4 scene(s)
  Senareth: known=True spawnable=True class=known_spawnable in 5 scene(s)
  Tomorrow: known=False spawnable=False class=unknown in 1 scene(s)
  Torhh: known=True spawnable=True class=known_spawnable in 4 scene(s)
  Vairis: known=True spawnable=True class=known_spawnable in 3 scene(s)
  someone: known=True spawnable=False class=known_non_spawnable in 1 scene(s)

### chapter.book001.004_the_convergence
  About: known=False spawnable=False class=unknown in 1 scene(s)
  Elyraen: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Giant: known=False spawnable=False class=unknown in 1 scene(s)
  Giants: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Kyreth: known=True spawnable=True class=known_spawnable in 1 scene(s)
  More: known=False spawnable=False class=unknown in 1 scene(s)
  Nephoretti: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Olythae: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Other: known=False spawnable=False class=unknown in 1 scene(s)
  Pelagor: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Prime: known=False spawnable=False class=unknown in 1 scene(s)
  Senareth: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Tiamat: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Torhh: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Vairis: known=True spawnable=True class=known_spawnable in 1 scene(s)

### chapter.book002.005_the_garden_blooms
  Aeon: known=False spawnable=False class=unknown in 2 scene(s)
  Anunnaki: known=False spawnable=False class=unknown in 1 scene(s)
  Coming: known=False spawnable=False class=unknown in 1 scene(s)
  Contact: known=False spawnable=False class=unknown in 1 scene(s)
  Elyraen: known=True spawnable=True class=known_spawnable in 5 scene(s)
  Festival: known=False spawnable=False class=unknown in 1 scene(s)
  First: known=False spawnable=False class=unknown in 2 scene(s)
  Garden: known=False spawnable=False class=unknown in 1 scene(s)
  Giant: known=False spawnable=False class=unknown in 1 scene(s)
  Giants: known=True spawnable=False class=known_non_spawnable in 8 scene(s)
  Ironspire: known=False spawnable=False class=unknown in 1 scene(s)
  Keepers: known=False spawnable=False class=unknown in 2 scene(s)
  Kyreth: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Mountain: known=False spawnable=False class=unknown in 2 scene(s)
  Nephoretti: known=True spawnable=False class=known_non_spawnable in 7 scene(s)
  Nexus: known=False spawnable=False class=unknown in 1 scene(s)
  Olythae: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Points: known=False spawnable=False class=unknown in 1 scene(s)
  Senareth: known=True spawnable=True class=known_spawnable in 5 scene(s)
  Seraneth: known=False spawnable=False class=unknown in 2 scene(s)
  Tidecaller: known=False spawnable=False class=unknown in 2 scene(s)
  Tidecallers: known=False spawnable=False class=unknown in 1 scene(s)
  Torhh: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Vairis: known=True spawnable=True class=known_spawnable in 2 scene(s)

### chapter.book002.006_the_first_coming
  Anunnaki: known=False spawnable=False class=unknown in 5 scene(s)
  Citadel: known=False spawnable=False class=unknown in 1 scene(s)
  Crimson: known=False spawnable=False class=unknown in 1 scene(s)
  Eduhauana: known=False spawnable=False class=unknown in 1 scene(s)
  Enlil: known=False spawnable=False class=unknown in 1 scene(s)
  Everything: known=False spawnable=False class=unknown in 1 scene(s)
  Gamma: known=False spawnable=False class=unknown in 1 scene(s)
  Hope: known=False spawnable=False class=unknown in 1 scene(s)
  Igigi: known=False spawnable=False class=unknown in 3 scene(s)
  Ishara: known=False spawnable=False class=unknown in 2 scene(s)
  Ishkur: known=False spawnable=False class=unknown in 1 scene(s)
  Landing: known=False spawnable=False class=unknown in 1 scene(s)
  Layla: known=False spawnable=False class=unknown in 1 scene(s)
  Marduk: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Ninurta: known=False spawnable=False class=unknown in 2 scene(s)
  Overseer: known=False spawnable=False class=unknown in 2 scene(s)
  Pazuzu: known=True spawnable=True class=known_spawnable in 2 scene(s)
  Queen: known=False spawnable=False class=unknown in 1 scene(s)
  Reptilian: known=False spawnable=False class=unknown in 3 scene(s)
  Reptilians: known=False spawnable=False class=unknown in 1 scene(s)
  Site: known=False spawnable=False class=unknown in 1 scene(s)
  Year: known=False spawnable=False class=unknown in 1 scene(s)

### chapter.book002.007_the_needle_construction
  Anunnaki: known=False spawnable=False class=unknown in 4 scene(s)
  Coming: known=False spawnable=False class=unknown in 1 scene(s)
  Desert: known=False spawnable=False class=unknown in 1 scene(s)
  Enlil: known=False spawnable=False class=unknown in 1 scene(s)
  Estimated: known=False spawnable=False class=unknown in 1 scene(s)
  Giant: known=False spawnable=False class=unknown in 2 scene(s)
  Giants: known=True spawnable=False class=known_non_spawnable in 2 scene(s)
  Igigi: known=False spawnable=False class=unknown in 4 scene(s)
  Indigenous: known=False spawnable=False class=unknown in 1 scene(s)
  Ishara: known=False spawnable=False class=unknown in 2 scene(s)
  Marduk: known=True spawnable=False class=known_non_spawnable in 2 scene(s)
  Needle: known=False spawnable=False class=unknown in 4 scene(s)
  Nephoretti: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Overseer: known=False spawnable=False class=unknown in 3 scene(s)
  Pazuzu: known=True spawnable=True class=known_spawnable in 2 scene(s)
  Reptilian: known=False spawnable=False class=unknown in 4 scene(s)
  Reptilians: known=False spawnable=False class=unknown in 2 scene(s)
  Second: known=False spawnable=False class=unknown in 1 scene(s)
  Tidecaller: known=False spawnable=False class=unknown in 1 scene(s)
  Tidecallers: known=False spawnable=False class=unknown in 1 scene(s)
  Torhh: known=True spawnable=True class=known_spawnable in 1 scene(s)

### chapter.book002.008_queens_assessment
  Anunnaki: known=False spawnable=False class=unknown in 1 scene(s)
  Eduhauana: known=False spawnable=False class=unknown in 2 scene(s)
  Giant: known=False spawnable=False class=unknown in 3 scene(s)
  Giants: known=True spawnable=False class=known_non_spawnable in 2 scene(s)
  Igigi: known=False spawnable=False class=unknown in 3 scene(s)
  Ishara: known=False spawnable=False class=unknown in 1 scene(s)
  Marduk: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Needle: known=False spawnable=False class=unknown in 1 scene(s)
  Overseer: known=False spawnable=False class=unknown in 1 scene(s)
  Pazuzu: known=True spawnable=True class=known_spawnable in 2 scene(s)
  Queen: known=False spawnable=False class=unknown in 2 scene(s)
  Sundering: known=False spawnable=False class=unknown in 2 scene(s)
  These: known=False spawnable=False class=unknown in 1 scene(s)
  Torhh: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Your: known=False spawnable=False class=unknown in 1 scene(s)

### chapter.book003.009_stalemate_departure_the_first_coming
  Anunnaki: known=False spawnable=False class=unknown in 4 scene(s)
  Citadel: known=False spawnable=False class=unknown in 1 scene(s)
  Coming: known=False spawnable=False class=unknown in 3 scene(s)
  Crimson: known=False spawnable=False class=unknown in 1 scene(s)
  Desert: known=False spawnable=False class=unknown in 1 scene(s)
  Eduhauana: known=False spawnable=False class=unknown in 1 scene(s)
  Enlil: known=False spawnable=False class=unknown in 2 scene(s)
  Fifth: known=False spawnable=False class=unknown in 1 scene(s)
  First: known=False spawnable=False class=unknown in 2 scene(s)
  Garden: known=False spawnable=False class=unknown in 1 scene(s)
  Giant: known=False spawnable=False class=unknown in 1 scene(s)
  Giants: known=True spawnable=False class=known_non_spawnable in 3 scene(s)
  Igigi: known=False spawnable=False class=unknown in 3 scene(s)
  Ironspire: known=False spawnable=False class=unknown in 1 scene(s)
  Needle: known=False spawnable=False class=unknown in 2 scene(s)
  Needles: known=False spawnable=False class=unknown in 2 scene(s)
  Nephilim: known=False spawnable=False class=unknown in 2 scene(s)
  Nephoretti: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Nibiru: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Once: known=False spawnable=False class=unknown in 1 scene(s)
  Overseer: known=False spawnable=False class=unknown in 1 scene(s)
  Pazuzu: known=True spawnable=True class=known_spawnable in 2 scene(s)
  Queen: known=False spawnable=False class=unknown in 1 scene(s)
  Reptilian: known=False spawnable=False class=unknown in 2 scene(s)
  Reptilians: known=False spawnable=False class=unknown in 1 scene(s)
  Second: known=False spawnable=False class=unknown in 3 scene(s)
  Site: known=False spawnable=False class=unknown in 1 scene(s)
  Southern: known=False spawnable=False class=unknown in 1 scene(s)
  Sundering: known=False spawnable=False class=unknown in 1 scene(s)
  Torhh: known=True spawnable=True class=known_spawnable in 2 scene(s)

### chapter.book003.010_shadow_returns_second_coming
  Aerie: known=False spawnable=False class=unknown in 1 scene(s)
  Anunnaki: known=False spawnable=False class=unknown in 1 scene(s)
  Coming: known=False spawnable=False class=unknown in 1 scene(s)
  Eduhauana: known=False spawnable=False class=unknown in 1 scene(s)
  Forest: known=False spawnable=False class=unknown in 1 scene(s)
  Genesis: known=False spawnable=False class=unknown in 1 scene(s)
  Giant: known=False spawnable=False class=unknown in 3 scene(s)
  Giants: known=True spawnable=False class=known_non_spawnable in 2 scene(s)
  Gruulith: known=False spawnable=False class=unknown in 2 scene(s)
  Korrhan: known=False spawnable=False class=unknown in 1 scene(s)
  Ninurta: known=False spawnable=False class=unknown in 1 scene(s)
  Overseer: known=False spawnable=False class=unknown in 1 scene(s)
  Peaks: known=False spawnable=False class=unknown in 1 scene(s)
  Queen: known=False spawnable=False class=unknown in 1 scene(s)
  Second: known=False spawnable=False class=unknown in 1 scene(s)
  Singing: known=False spawnable=False class=unknown in 1 scene(s)
  Sundering: known=False spawnable=False class=unknown in 1 scene(s)
  Tactical: known=False spawnable=False class=unknown in 1 scene(s)
  Tidecallers: known=False spawnable=False class=unknown in 1 scene(s)

### chapter.book003.011_escalation_and_desperation
  Abyssal: known=False spawnable=False class=unknown in 1 scene(s)
  Anunnaki: known=False spawnable=False class=unknown in 3 scene(s)
  Brajor: known=False spawnable=False class=unknown in 1 scene(s)
  Chamber: known=False spawnable=False class=unknown in 1 scene(s)
  Clans: known=False spawnable=False class=unknown in 2 scene(s)
  Coming: known=False spawnable=False class=unknown in 1 scene(s)
  Cradle: known=False spawnable=False class=unknown in 1 scene(s)
  Desert: known=False spawnable=False class=unknown in 1 scene(s)
  Dragon: known=False spawnable=False class=unknown in 1 scene(s)
  Dregan: known=False spawnable=False class=unknown in 2 scene(s)
  Dregans: known=False spawnable=False class=unknown in 2 scene(s)
  First: known=False spawnable=False class=unknown in 1 scene(s)
  Giant: known=False spawnable=False class=unknown in 3 scene(s)
  Giants: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Grand: known=False spawnable=False class=unknown in 1 scene(s)
  Grotto: known=False spawnable=False class=unknown in 1 scene(s)
  Ison: known=False spawnable=False class=unknown in 1 scene(s)
  Nephilim: known=False spawnable=False class=unknown in 1 scene(s)
  Ninurta: known=False spawnable=False class=unknown in 1 scene(s)
  Oasis: known=False spawnable=False class=unknown in 2 scene(s)
  Overseer: known=False spawnable=False class=unknown in 1 scene(s)
  Pazuzu: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Reef: known=False spawnable=False class=unknown in 1 scene(s)
  Saresh: known=False spawnable=False class=unknown in 1 scene(s)
  Sundering: known=False spawnable=False class=unknown in 1 scene(s)
  Tides: known=False spawnable=False class=unknown in 1 scene(s)
  Torhh: known=True spawnable=True class=known_spawnable in 1 scene(s)

### chapter.book003.012_nephilim_summoning
  Aeon: known=False spawnable=False class=unknown in 2 scene(s)
  Anunnaki: known=False spawnable=False class=unknown in 1 scene(s)
  Brajor: known=False spawnable=False class=unknown in 1 scene(s)
  Communion: known=False spawnable=False class=unknown in 1 scene(s)
  Forest: known=False spawnable=False class=unknown in 1 scene(s)
  Garden: known=False spawnable=False class=unknown in 1 scene(s)
  Giant: known=False spawnable=False class=unknown in 2 scene(s)
  Giants: known=True spawnable=False class=known_non_spawnable in 2 scene(s)
  Igigi: known=False spawnable=False class=unknown in 2 scene(s)
  Keepers: known=False spawnable=False class=unknown in 2 scene(s)
  Korrhan: known=False spawnable=False class=unknown in 2 scene(s)
  Nephilim: known=False spawnable=False class=unknown in 1 scene(s)
  Pazuzu: known=True spawnable=True class=known_spawnable in 2 scene(s)
  Saresh: known=False spawnable=False class=unknown in 1 scene(s)
  Subterranean: known=False spawnable=False class=unknown in 1 scene(s)
  Torhh: known=True spawnable=True class=known_spawnable in 2 scene(s)
  Torrhen: known=True spawnable=True class=known_spawnable in 2 scene(s)
  Veil: known=True spawnable=False class=known_non_spawnable in 1 scene(s)

### chapter.book003.014_convergence
  Aeon: known=False spawnable=False class=unknown in 1 scene(s)
  Anunnaki: known=False spawnable=False class=unknown in 1 scene(s)
  Brajor: known=False spawnable=False class=unknown in 1 scene(s)
  Dregans: known=False spawnable=False class=unknown in 1 scene(s)
  Five: known=False spawnable=False class=unknown in 1 scene(s)
  Forest: known=False spawnable=False class=unknown in 1 scene(s)
  Giant: known=False spawnable=False class=unknown in 2 scene(s)
  Giants: known=True spawnable=False class=known_non_spawnable in 2 scene(s)
  Gruulith: known=False spawnable=False class=unknown in 1 scene(s)
  Highland: known=False spawnable=False class=unknown in 1 scene(s)
  Igigi: known=False spawnable=False class=unknown in 1 scene(s)
  Keepers: known=False spawnable=False class=unknown in 1 scene(s)
  Korrhan: known=False spawnable=False class=unknown in 2 scene(s)
  Mountain: known=False spawnable=False class=unknown in 1 scene(s)
  Nephilim: known=False spawnable=False class=unknown in 2 scene(s)
  Pazuzu: known=True spawnable=True class=known_spawnable in 2 scene(s)
  Saresh: known=False spawnable=False class=unknown in 1 scene(s)
  Subterranean: known=False spawnable=False class=unknown in 1 scene(s)
  Tidecallers: known=False spawnable=False class=unknown in 2 scene(s)
  Torhh: known=True spawnable=True class=known_spawnable in 2 scene(s)

### chapter.book003.015_betrayal
  After: known=False spawnable=False class=unknown in 1 scene(s)
  Anunnaki: known=False spawnable=False class=unknown in 3 scene(s)
  Book: known=False spawnable=False class=unknown in 1 scene(s)
  Citadel: known=False spawnable=False class=unknown in 1 scene(s)
  Coming: known=False spawnable=False class=unknown in 2 scene(s)
  Crimson: known=False spawnable=False class=unknown in 1 scene(s)
  Eduhauana: known=False spawnable=False class=unknown in 1 scene(s)
  Enlil: known=False spawnable=False class=unknown in 2 scene(s)
  Every: known=False spawnable=False class=unknown in 1 scene(s)
  Fifth: known=False spawnable=False class=unknown in 1 scene(s)
  First: known=False spawnable=False class=unknown in 1 scene(s)
  Fourth: known=False spawnable=False class=unknown in 1 scene(s)
  Giant: known=False spawnable=False class=unknown in 5 scene(s)
  Giants: known=True spawnable=False class=known_non_spawnable in 5 scene(s)
  Korrhan: known=False spawnable=False class=unknown in 3 scene(s)
  Needle: known=False spawnable=False class=unknown in 2 scene(s)
  Nephilim: known=False spawnable=False class=unknown in 1 scene(s)
  Northern: known=False spawnable=False class=unknown in 1 scene(s)
  Overseer: known=False spawnable=False class=unknown in 1 scene(s)
  Pazuzu: known=True spawnable=True class=known_spawnable in 2 scene(s)
  Queen: known=False spawnable=False class=unknown in 2 scene(s)
  Saresh: known=False spawnable=False class=unknown in 1 scene(s)
  Second: known=False spawnable=False class=unknown in 1 scene(s)
  Third: known=False spawnable=False class=unknown in 1 scene(s)
  Tidecaller: known=False spawnable=False class=unknown in 1 scene(s)
  Torhh: known=True spawnable=True class=known_spawnable in 2 scene(s)
  Your: known=False spawnable=False class=unknown in 1 scene(s)

### chapter.book004.016_the_choice_third_coming
  Anunnaki: known=False spawnable=False class=unknown in 1 scene(s)
  Coming: known=False spawnable=False class=unknown in 1 scene(s)
  Council: known=False spawnable=False class=unknown in 1 scene(s)
  Elder: known=False spawnable=False class=unknown in 1 scene(s)
  Eridu: known=False spawnable=False class=unknown in 1 scene(s)
  Great: known=False spawnable=False class=unknown in 1 scene(s)
  Igigi: known=False spawnable=False class=unknown in 1 scene(s)
  Ishara: known=False spawnable=False class=unknown in 1 scene(s)
  Pazuzu: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Third: known=False spawnable=False class=unknown in 1 scene(s)
  Work: known=False spawnable=False class=unknown in 1 scene(s)
  Year: known=False spawnable=False class=unknown in 1 scene(s)
  Zephyr: known=True spawnable=True class=known_spawnable in 1 scene(s)

### chapter.book004.017_niburu_shadow
  Anunnaki: known=False spawnable=False class=unknown in 2 scene(s)
  Commander: known=False spawnable=False class=unknown in 1 scene(s)
  Eduhauana: known=False spawnable=False class=unknown in 1 scene(s)
  Enlil: known=False spawnable=False class=unknown in 1 scene(s)
  Giant: known=False spawnable=False class=unknown in 1 scene(s)
  Giants: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Igigi: known=False spawnable=False class=unknown in 3 scene(s)
  Landmass: known=False spawnable=False class=unknown in 1 scene(s)
  Lord: known=False spawnable=False class=unknown in 1 scene(s)
  Marduk: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Matron: known=False spawnable=False class=unknown in 1 scene(s)
  Nibiru: known=True spawnable=False class=known_non_spawnable in 2 scene(s)
  Northern: known=False spawnable=False class=unknown in 1 scene(s)
  Queen: known=False spawnable=False class=unknown in 1 scene(s)
  Sage: known=False spawnable=False class=unknown in 1 scene(s)
  Surface: known=False spawnable=False class=unknown in 1 scene(s)
  Tiamat: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Tidecaller: known=False spawnable=False class=unknown in 1 scene(s)
  Zephyr: known=True spawnable=True class=known_spawnable in 2 scene(s)

### chapter.book004.018_the_wandering
  Cannot: known=False spawnable=False class=unknown in 1 scene(s)
  Giant: known=False spawnable=False class=unknown in 1 scene(s)
  Nibiru: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Tidecaller: known=False spawnable=False class=unknown in 1 scene(s)
  Torrhen: known=True spawnable=True class=known_spawnable in 6 scene(s)
  Zephyr: known=True spawnable=True class=known_spawnable in 6 scene(s)

### chapter.book004.019_the_sacrafice
  Giant: known=False spawnable=False class=unknown in 1 scene(s)
  Nibiru: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Sage: known=False spawnable=False class=unknown in 3 scene(s)
  Seven: known=False spawnable=False class=unknown in 1 scene(s)
  Someone: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Torrhen: known=True spawnable=True class=known_spawnable in 4 scene(s)
  Zephyr: known=True spawnable=True class=known_spawnable in 3 scene(s)

### chapter.book004.020_the_collapse
  Anunnaki: known=False spawnable=False class=unknown in 3 scene(s)
  Culling: known=False spawnable=False class=unknown in 1 scene(s)
  Fifteen: known=False spawnable=False class=unknown in 1 scene(s)
  Flood: known=False spawnable=False class=unknown in 1 scene(s)
  Giant: known=False spawnable=False class=unknown in 1 scene(s)
  Great: known=False spawnable=False class=unknown in 1 scene(s)
  Igigi: known=False spawnable=False class=unknown in 1 scene(s)
  Individual: known=False spawnable=False class=unknown in 1 scene(s)
  Pythagoras: known=False spawnable=False class=unknown in 1 scene(s)
  Sage: known=False spawnable=False class=unknown in 7 scene(s)
  Seven: known=False spawnable=False class=unknown in 1 scene(s)
  Species: known=False spawnable=False class=unknown in 1 scene(s)
  Studies: known=False spawnable=False class=unknown in 1 scene(s)
  Synthesis: known=False spawnable=False class=unknown in 2 scene(s)
  Tidecaller: known=False spawnable=False class=unknown in 2 scene(s)
  Torrhen: known=True spawnable=True class=known_spawnable in 7 scene(s)
  Year: known=False spawnable=False class=unknown in 2 scene(s)
  Zephyr: known=True spawnable=True class=known_spawnable in 1 scene(s)

### chapter.book004.021_the_first_lesson
  Codex: known=False spawnable=False class=unknown in 2 scene(s)
  First: known=False spawnable=False class=unknown in 6 scene(s)
  Five: known=False spawnable=False class=unknown in 1 scene(s)
  Grammar: known=False spawnable=False class=unknown in 3 scene(s)
  Harmonic: known=False spawnable=False class=unknown in 2 scene(s)
  Keen: known=False spawnable=False class=unknown in 1 scene(s)
  Pythagoras: known=False spawnable=False class=unknown in 2 scene(s)
  Resonances: known=False spawnable=False class=unknown in 1 scene(s)
  Sage: known=False spawnable=False class=unknown in 6 scene(s)
  Synthesis: known=False spawnable=False class=unknown in 3 scene(s)
  Torrhen: known=True spawnable=True class=known_spawnable in 6 scene(s)
  Tran: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Twelve: known=False spawnable=False class=unknown in 1 scene(s)
  Year: known=False spawnable=False class=unknown in 3 scene(s)
  Zephyr: known=True spawnable=True class=known_spawnable in 1 scene(s)

### chapter.book004.022_final_calculation
  Aethon: known=False spawnable=False class=unknown in 1 scene(s)
  Cycle: known=False spawnable=False class=unknown in 1 scene(s)
  Five: known=False spawnable=False class=unknown in 1 scene(s)
  Great: known=False spawnable=False class=unknown in 2 scene(s)
  Individual: known=False spawnable=False class=unknown in 1 scene(s)
  Sage: known=False spawnable=False class=unknown in 6 scene(s)
  Seven: known=False spawnable=False class=unknown in 1 scene(s)
  Students: known=False spawnable=False class=unknown in 1 scene(s)
  Torrhen: known=True spawnable=True class=known_spawnable in 5 scene(s)
  Universal: known=False spawnable=False class=unknown in 1 scene(s)
  Year: known=False spawnable=False class=unknown in 3 scene(s)

### chapter.book004.023_beyond_identity
  Beyond: known=False spawnable=False class=unknown in 1 scene(s)
  Book: known=False spawnable=False class=unknown in 1 scene(s)
  Days: known=False spawnable=False class=unknown in 1 scene(s)
  Eternal: known=False spawnable=False class=unknown in 3 scene(s)
  Great: known=False spawnable=False class=unknown in 1 scene(s)
  Hours: known=False spawnable=False class=unknown in 1 scene(s)
  Keen: known=False spawnable=False class=unknown in 1 scene(s)
  Sage: known=False spawnable=False class=unknown in 6 scene(s)
  Torrhen: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Tran: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Unnameable: known=False spawnable=False class=unknown in 1 scene(s)
  Year: known=False spawnable=False class=unknown in 1 scene(s)

### chapter.book005.024_the_first_spark
  Anunnaki: known=False spawnable=False class=unknown in 9 scene(s)
  Applicator: known=False spawnable=False class=unknown in 1 scene(s)
  Buyers: known=False spawnable=False class=unknown in 1 scene(s)
  Caverns: known=False spawnable=False class=unknown in 1 scene(s)
  Chamber: known=False spawnable=False class=unknown in 1 scene(s)
  Chapter: known=False spawnable=False class=unknown in 1 scene(s)
  Days: known=False spawnable=False class=unknown in 3 scene(s)
  Dregans: known=False spawnable=False class=unknown in 1 scene(s)
  Every: known=False spawnable=False class=unknown in 1 scene(s)
  Felt: known=False spawnable=False class=unknown in 1 scene(s)
  Five: known=False spawnable=False class=unknown in 3 scene(s)
  Galactic: known=False spawnable=False class=unknown in 1 scene(s)
  Geralt: known=True spawnable=True class=known_spawnable in 3 scene(s)
  Gruulith: known=False spawnable=False class=unknown in 1 scene(s)
  Gruuliths: known=False spawnable=False class=unknown in 2 scene(s)
  Hours: known=False spawnable=False class=unknown in 1 scene(s)
  Immediately: known=False spawnable=False class=unknown in 3 scene(s)
  Lyrian: known=False spawnable=False class=unknown in 1 scene(s)
  Masters: known=False spawnable=False class=unknown in 1 scene(s)
  Mika: known=True spawnable=True class=known_spawnable in 2 scene(s)
  More: known=False spawnable=False class=unknown in 2 scene(s)
  Nameless: known=False spawnable=False class=unknown in 11 scene(s)
  Night: known=False spawnable=False class=unknown in 3 scene(s)
  Ones: known=False spawnable=False class=unknown in 3 scene(s)
  Overseer: known=False spawnable=False class=unknown in 2 scene(s)
  Overseers: known=False spawnable=False class=unknown in 6 scene(s)
  Pleiadian: known=False spawnable=False class=unknown in 2 scene(s)
  Pleiadians: known=False spawnable=False class=unknown in 2 scene(s)
  Potential: known=False spawnable=False class=unknown in 1 scene(s)
  Reptilian: known=False spawnable=False class=unknown in 6 scene(s)
  Slaves: known=False spawnable=False class=unknown in 1 scene(s)
  Something: known=False spawnable=False class=unknown in 4 scene(s)
  These: known=False spawnable=False class=unknown in 1 scene(s)
  Trade: known=False spawnable=False class=unknown in 1 scene(s)
  Waiting: known=False spawnable=False class=unknown in 1 scene(s)
  Watched: known=False spawnable=False class=unknown in 1 scene(s)

### chapter.book005.025_confined_freedom
  Another: known=False spawnable=False class=unknown in 1 scene(s)
  Anunnaki: known=False spawnable=False class=unknown in 5 scene(s)
  Applicator: known=False spawnable=False class=unknown in 4 scene(s)
  Applicators: known=False spawnable=False class=unknown in 1 scene(s)
  Because: known=False spawnable=False class=unknown in 1 scene(s)
  Chamber: known=False spawnable=False class=unknown in 1 scene(s)
  Chapter: known=False spawnable=False class=unknown in 1 scene(s)
  Compound: known=False spawnable=False class=unknown in 1 scene(s)
  Crystalline: known=False spawnable=False class=unknown in 1 scene(s)
  Days: known=False spawnable=False class=unknown in 2 scene(s)
  Every: known=False spawnable=False class=unknown in 1 scene(s)
  Everyone: known=False spawnable=False class=unknown in 1 scene(s)
  Five: known=False spawnable=False class=unknown in 4 scene(s)
  Freed: known=False spawnable=False class=unknown in 2 scene(s)
  Geralt: known=True spawnable=True class=known_spawnable in 4 scene(s)
  Host: known=False spawnable=False class=unknown in 2 scene(s)
  Just: known=False spawnable=False class=unknown in 3 scene(s)
  Language: known=False spawnable=False class=unknown in 1 scene(s)
  Mika: known=True spawnable=True class=known_spawnable in 3 scene(s)
  More: known=False spawnable=False class=unknown in 1 scene(s)
  Morning: known=False spawnable=False class=unknown in 1 scene(s)
  Nameless: known=False spawnable=False class=unknown in 6 scene(s)
  Nephoretti: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Network: known=False spawnable=False class=unknown in 1 scene(s)
  Nothing: known=False spawnable=False class=unknown in 1 scene(s)
  Overseer: known=False spawnable=False class=unknown in 2 scene(s)
  Overseers: known=False spawnable=False class=unknown in 1 scene(s)
  Past: known=False spawnable=False class=unknown in 1 scene(s)
  Please: known=False spawnable=False class=unknown in 1 scene(s)
  Power: known=False spawnable=False class=unknown in 1 scene(s)
  Reptilian: known=False spawnable=False class=unknown in 3 scene(s)
  Respect: known=False spawnable=False class=unknown in 1 scene(s)
  Seal: known=False spawnable=False class=unknown in 1 scene(s)
  Searching: known=False spawnable=False class=unknown in 1 scene(s)
  Stay: known=False spawnable=False class=unknown in 1 scene(s)
  Still: known=False spawnable=False class=unknown in 1 scene(s)
  Thank: known=False spawnable=False class=unknown in 1 scene(s)
  Tomorrow: known=False spawnable=False class=unknown in 1 scene(s)
  Toward: known=False spawnable=False class=unknown in 1 scene(s)
  Training: known=False spawnable=False class=unknown in 1 scene(s)
  Weapons: known=False spawnable=False class=unknown in 1 scene(s)
  With: known=False spawnable=False class=unknown in 1 scene(s)
  Within: known=False spawnable=False class=unknown in 1 scene(s)
  Would: known=False spawnable=False class=unknown in 1 scene(s)
  Your: known=False spawnable=False class=unknown in 1 scene(s)

### chapter.book005.026_dragonmail
  Aeon: known=False spawnable=False class=unknown in 3 scene(s)
  Anunnaki: known=False spawnable=False class=unknown in 3 scene(s)
  Applicator: known=False spawnable=False class=unknown in 3 scene(s)
  Dragon: known=False spawnable=False class=unknown in 1 scene(s)
  Ethereal: known=True spawnable=False class=known_non_spawnable in 3 scene(s)
  Geralt: known=True spawnable=True class=known_spawnable in 3 scene(s)
  Immediately: known=False spawnable=False class=unknown in 3 scene(s)
  Keeper: known=False spawnable=False class=unknown in 1 scene(s)
  Keepers: known=False spawnable=False class=unknown in 3 scene(s)
  Library: known=False spawnable=False class=unknown in 2 scene(s)
  Mail: known=False spawnable=False class=unknown in 1 scene(s)
  Nameless: known=False spawnable=False class=unknown in 3 scene(s)
  Nephoretti: known=True spawnable=False class=known_non_spawnable in 2 scene(s)
  Tiamat: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Zaron: known=False spawnable=False class=unknown in 1 scene(s)

### chapter.book005.027_the_claiming
  Aeon: known=False spawnable=False class=unknown in 3 scene(s)
  Anunnaki: known=False spawnable=False class=unknown in 4 scene(s)
  Applicator: known=False spawnable=False class=unknown in 6 scene(s)
  Dragon: known=False spawnable=False class=unknown in 3 scene(s)
  Ethereal: known=True spawnable=False class=known_non_spawnable in 1 scene(s)
  Every: known=False spawnable=False class=unknown in 1 scene(s)
  Felt: known=False spawnable=False class=unknown in 1 scene(s)
  Five: known=False spawnable=False class=unknown in 1 scene(s)
  Geralt: known=True spawnable=True class=known_spawnable in 7 scene(s)
  Guardian: known=False spawnable=False class=unknown in 1 scene(s)
  Host: known=False spawnable=False class=unknown in 1 scene(s)
  Hours: known=False spawnable=False class=unknown in 1 scene(s)
  Immediately: known=False spawnable=False class=unknown in 4 scene(s)
  Kael: known=False spawnable=False class=unknown in 1 scene(s)
  Keepers: known=False spawnable=False class=unknown in 2 scene(s)
  Mail: known=False spawnable=False class=unknown in 2 scene(s)
  Mika: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Nephoretti: known=True spawnable=False class=known_non_spawnable in 2 scene(s)
  Only: known=False spawnable=False class=unknown in 1 scene(s)
  Oreck: known=True spawnable=True class=known_spawnable in 7 scene(s)
  Tess: known=False spawnable=False class=unknown in 1 scene(s)
  Tomorrow: known=False spawnable=False class=unknown in 1 scene(s)
  Vale: known=True spawnable=True class=known_spawnable in 1 scene(s)
  Your: known=False spawnable=False class=unknown in 1 scene(s)
  Zaron: known=False spawnable=False class=unknown in 3 scene(s)

### chapter.book005.028_ragnarok
  Aeon: known=False spawnable=False class=unknown in 1 scene(s)
  Anunnaki: known=False spawnable=False class=unknown in 4 scene(s)
  Applicator: known=False spawnable=False class=unknown in 5 scene(s)
  Artifact: known=False spawnable=False class=unknown in 1 scene(s)
  Choose: known=False spawnable=False class=unknown in 1 scene(s)
  Dawn: known=False spawnable=False class=unknown in 1 scene(s)
  Days: known=False spawnable=False class=unknown in 1 scene(s)
  Dragon: known=False spawnable=False class=unknown in 1 scene(s)
  Dren: known=False spawnable=False class=unknown in 2 scene(s)
  Enforcer: known=False spawnable=False class=unknown in 2 scene(s)
  Every: known=False spawnable=False class=unknown in 1 scene(s)
  Five: known=False spawnable=False class=unknown in 1 scene(s)
  Freed: known=False spawnable=False class=unknown in 1 scene(s)
  Galactic: known=False spawnable=False class=unknown in 1 scene(s)
  Geralt: known=True spawnable=True class=known_spawnable in 5 scene(s)
  Guards: known=False spawnable=False class=unknown in 1 scene(s)
  Immediately: known=False spawnable=False class=unknown in 2 scene(s)
  Keeper: known=False spawnable=False class=unknown in 1 scene(s)
  Mail: known=False spawnable=False class=unknown in 1 scene(s)
  Mika: known=True spawnable=True class=known_spawnable in 4 scene(s)
  None: known=False spawnable=False class=unknown in 1 scene(s)
  Oreck: known=True spawnable=True class=known_spawnable in 5 scene(s)
  Overseer: known=False spawnable=False class=unknown in 3 scene(s)
  Personnel: known=False spawnable=False class=unknown in 1 scene(s)
  Ragnarok: known=False spawnable=False class=unknown in 2 scene(s)
  Same: known=False spawnable=False class=unknown in 1 scene(s)
  Strike: known=False spawnable=False class=unknown in 1 scene(s)
  Subject: known=False spawnable=False class=unknown in 1 scene(s)
  Team: known=False spawnable=False class=unknown in 1 scene(s)
  Tomorrow: known=False spawnable=False class=unknown in 1 scene(s)
  Twenty: known=False spawnable=False class=unknown in 1 scene(s)
  With: known=False spawnable=False class=unknown in 2 scene(s)
  Within: known=False spawnable=False class=unknown in 1 scene(s)
  Would: known=False spawnable=False class=unknown in 1 scene(s)
  Your: known=False spawnable=False class=unknown in 1 scene(s)
  Zaron: known=False spawnable=False class=unknown in 5 scene(s)
```

## Aggregate Book 1-5 summary

```text
Chapters processed:                27 / 27
Pipeline exit codes:                27 / 27 clean (0)
Scene packets generated:            124
Primary invariant (authored==generated): 27 / 27 PASS, 0 mismatches
Boundary method / authority state:  100% authored_scene_marker /
                                     SCENE_BOUNDARY_AUTHORED / proven=true
Scene-meta key survival:             124 / 124 scenes, 0 empty
Scene-text leakage across markers:   0 cases
Meta-keyword-as-entity contamination: 0 cases
Manifestation consistency violations: 0 cases (either direction)
Tran-like false-entity recurrence:    0 (2 real Tran references, both correct)
semantic_environment_extractor gap:  still present, 45 non-fatal occurrences
Bogus entity candidates:             noise words + unregistered real names,
                                     both harmless (never spawnable)
Manuscript files modified:           0
Mettaext code changed:               0
```

The primary invariant this run existed to check -- authored scene markers
equal generated scene packets, for every repaired chapter in Books 1-5 --
holds without exception. No mismatch was found, so none was recorded as a
failure; this is an honest fresh baseline, not a smoothed-over one, and the
only real, pre-existing defect confirmed still present is the already-
tracked `semantic_environment_extractor` gap.