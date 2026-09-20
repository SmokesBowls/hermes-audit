# Pattern 4 fixed and live-verified — delta from the `e9a3075` semantic baseline

Implements the fix traced in `e9cd2c0`. Code + tests committed to
`EngAIn` as `e4c3d54`. Scoped exactly as instructed: `pass2_enhanced.py`
candidate construction only; physicality inference, remote inference,
world_rules, aliases, and Pattern 3 noise untouched.

## What changed

`extract_characters()` now keeps two things distinct that were
previously conflated:

```text
1. Frequency-based prose discovery (unchanged in spirit) -- but the
   participants: line's own metadata representations
   (@scene_meta_participants: and the raw participants: line) are
   excluded from the count, so authored presence and prose mention
   count stop being the same number.

2. New: every name token in the participants: line is seeded as a
   Character candidate unconditionally, regardless of prose mention
   count.
```

## A real correction made mid-implementation, reported plainly

The first version of the metadata exclusion was broader than what was
asked — it also excluded `focus:`, `continuity:`, `location:`, `time:`,
`presentation:`, and `cutscene purpose:` lines (both `@scene_meta_*`
and raw forms), not just `participants:`. A full fresh Books 1-5 rerun
against that version caught a real regression before it shipped: **Tran
(x2 scenes), Geralt (x6 scenes), and Torrhen (x2 scenes)** — all
previously `known_spawnable` with real `presence: unknown` records —
**disappeared from `entities_observed` entirely**, because their only
mentions in those specific scenes were inside `focus:`/`cutscene
purpose:` prose (discussing them prospectively or historically), never
in `participants:`, and excluding those fields dropped them below the
frequency threshold with no participant-seeding to catch them. That is
a worse outcome than the `unknown` they started at — exactly Pattern
4's own failure mode, recreated via a different field, and exactly why
the instruction to keep it scoped mattered.

Narrowed the exclusion to `participants:` specifically (both
representations, nothing else), reran clean, confirmed all ten
disappearances restored. This is now flagged as its own, separate,
real finding for later, deferred work — see below — not folded into
this patch.

## Live delta: fresh Books 1-5 rerun, narrow fix, vs. `e9a3075`'s baseline

```text
Primary invariant (authored markers == generated packets): 27/27, unchanged
Manifest consistency violations (either direction):         0, unchanged
entities_observed rows:                                     944 -> 1021 (+77, purely additive)
Disappeared entities_observed rows:                          0
New false @entities entries:                                 0 -- all 7 new
  @entities additions (Pelagor x3 in book1 ch3, Torhh, Zephyr x2, Mika)
  are genuine known_spawnable participants Pattern 4 was supposed to surface
New false @entities_manifested entries:                       0
```

## All ten named Pattern 4 acceptance cases confirmed fixed

```text
scene.book005.024_the_first_spark.scene005    Mika    present, mentions=0
scene.book005.024_the_first_spark.scene010    Mika    present, mentions=0
scene.book005.024_the_first_spark.scene011    Mika    present, mentions=0
scene.book005.025_confined_freedom.scene003   Mika    present, mentions=0
scene.book004.019_the_sacrafice.scene004      Zephyr  present, mentions=0
scene.book004.022_final_calculation.scene001  Zephyr  present, mentions=0
scene.book004.023_beyond_identity.scene001    Zephyr  present, mentions=0
scene.book003.012_nephilim_summoning.scene002 Saresh  present, mentions=0
scene.book003.014_convergence.scene001        Saresh  present, mentions=0
scene.book002.007_the_needle_construction.scene002 Torhh present, mentions=0
```

`mentions=0` in every case, not inflated — confirming requirement 4
(metadata establishes participation, not mention count) held precisely.
All still `physicality: unknown` except where noted below — this patch
did not invent physicality anywhere.

## One pre-existing wrinkle this fix exposed, not caused, not fixed

`scene.book003.012_nephilim_summoning.scene002`'s Saresh — now
correctly present via participant-seeding — comes out
`physicality: nonphysical, confidence: 0.85` despite zero prose
mentions. Traced: the scene's participants line itself is
`"...Torrhen (embedded consciousness), Aeon Keepers (consciousness
contact)"` — the word "consciousness" sits in the *same segment* as
"Saresh", and `infer_physicality_enhanced()`'s same-segment scan has no
per-name proximity check finer than "does this segment contain the
name anywhere," so it misattributes evidence about Torrhen/the Aeon
Keepers to Saresh. This is a pre-existing flaw in physicality
inference, not something this patch's code touches or introduces — it
was simply invisible before because Saresh never reached the
`presence: local` branch at all. Flagged for whoever does Pattern 1's
work next, since it lives in the same function; not fixed here.

## Regression coverage

5 new tests in `test_pattern4_participant_seeding.py`: zero-prose-
mention participant survives; metadata duplication doesn't inflate
`mentions`; a real non-participant character with 3+ genuine prose
mentions is still discovered by the unchanged frequency path;
participant seeding never implies `known`/`spawnable`/physicality;
and a direct test locking in the narrow scope of the exclusion helper
(participants only, not `focus:`/etc.) so the reverted broader version
doesn't quietly return. `test_scene_local_manifestation.py`'s existing
`@entities` assertion updated — Mordain now correctly included, the
fix working as intended. Full `tier3/mettaext` suite: **76 passed**.

## What was deliberately not done

Physicality inference untouched (Saresh's misattribution stands,
flagged not fixed). Remote inference, world_rules, alias resolution,
and Pattern 3's title-fragment noise (`Aeon`, `Nameless`) untouched.
The broader focus:/continuity:/etc. metadata-as-noise finding is
reported, not resolved — a real, separate candidate for future work,
distinct from both this patch and Pattern 1's physicality-lexicon
generalization.
