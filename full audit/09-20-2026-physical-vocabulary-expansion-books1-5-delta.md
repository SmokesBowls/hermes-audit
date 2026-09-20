# Physical vocabulary expansion, corpus-backed — delta from `f0f0698`

Implements the expansion requested after `f0f0698`. Code + tests
committed to `EngAIn` as (see commit below). Scoped exactly as
instructed: only the positive/physical side of
`infer_physicality_enhanced()`. Nonphysical entity-state rules,
presence inference, participant seeding, remote/reference inference,
world_rules/aliases, `@entities_manifested` projection, and
`semantic_environment_extractor` are all untouched.

## What was added, all grounded directly in real Books 1-5 phrasing

```text
Locomotion extension:
  "approached", "ventured", "entered", "arrived", "backed away"
  -- "Pazuzu approached Torhh slowly", "closer than any Giant had
  ventured since the landing"

Body-formation extension:
  "solidified", "stone-flesh"
  -- "Korrhan's stone-flesh had solidified unevenly"

Body-part evidence (NEW: a construction, not bare nouns):
  (possessive) + (up to 3 descriptive words) + eye(s)/hand(s)/
  finger(s)/arm(s)/leg(s)/skin/face
  -- "Zephyr closed his eyes", "Torhh's ocean-deep eyes carried grief",
  "his elongated fingers" -- a bare "eyes"/"hands" was deliberately
  rejected (would also match "eyes of the storm"/"hands of fate"
  idiom); requiring the possessive ties it to whichever entity's name
  shares the sentence.

Physical-sensation evidence (NEW: a construction, not bare "felt"):
  "felt ... against/beneath/on (his/her/their/its) skin/palms/feet/
  chest/body" -- grounded in "Felt it warm against their skin". Bare
  "felt" was rejected outright: this corpus uses it constantly for
  emotional/mental states ("felt gratitude", "felt violated", "felt
  something twist in his consciousness").

Contact/manipulation verbs (NEW, guarded):
  gripped, grabbed, lifted, pushed, pulled, pressed -- but ONLY when
  the sentence does not also contain consciousness/awareness/mind
  language, because this exact corpus uses several of these verbs as
  metaphors for mental/psychic effect ("the glacial cold that still
  gripped its consciousness") -- the same idiom family as
  "consciousness-touch".
```

## Deliberately not added, despite appearing in the corpus

```text
"touch"/"touched" -- this corpus's own recurring compound term
  "consciousness-touch" means telepathic communication between
  Giants/Igigi, far more common here than any literal touch. Adding
  the bare word would misfire constantly.

"carried" -- overwhelmingly abstract/emotional in this corpus
  ("carried grief", "carried weight that transcended the moment",
  "carried enough truth") rather than literal carrying.

"struck" -- appears as simile for mental impact at least as often as
  literal contact ("Understanding struck Zephyr like a physical
  force"). Excluded rather than risk misfiring on figurative language.
```

Each exclusion has a dedicated regression test confirming the excluded
word does NOT fire in exactly the contaminating construction found in
the corpus.

## Live delta: fresh Books 1-5 rerun vs. `f0f0698`

```text
Primary invariant:                27/27, unchanged
Manifest consistency violations:  0, unchanged

Local-presence physicality distribution:
              before    after
  physical       187       266   (+79)
  nonphysical      1         1   (unchanged, exactly as required)
  unknown        376       297   (-79, matches exactly)

Physical -> unknown/nonphysical regressions: 0
```

## The 79 newly-physical instances, grouped by evidence family

```text
body_part_possessive        42   (eyes/hands/fingers/arms/legs, possessive)
locomotion_extension        21   (approached/ventured/entered/arrived/backed away)
body_formation_extension     8   (solidified/stone-flesh)
contact_manipulation         6   (gripped/grabbed/lifted/pushed/pulled/pressed, unguarded)
physical_sensation           1   (felt ... against ... skin)
unattributed                 1   (resolved via the existing speech-verb
                                   whole-segment exception from 5514843,
                                   not a plain sentence match)
```

`body_part_possessive` alone accounts for more than half — confirming
the audit's own ranking of `bodily_description` as the single largest
family (32 of 75 "unknown-with-evidence" cases in `6e403d5`'s original
clustering).

## The seven spot-check entities

```text
              before (f0f0698)          after
Zephyr        2 physical, 15 unknown    6 physical, 11 unknown
Torhh         6 physical, 12 unknown    10 physical, 8 unknown
Pazuzu        7 physical, 9 unknown     10 physical, 6 unknown
Senareth      (not previously flagged)  5 physical, 8 unknown
Giants        (not previously flagged)  10 physical, 6 unknown
Giant         (not previously flagged)  13 physical, 11 unknown
Igigi         4 physical, 7 unknown     4 physical, 7 unknown (unchanged --
                                          no new construction matched any
                                          Igigi sentence)
Anunnaki      4 physical, 11 unknown    9 physical, 6 unknown
```

Every one improved except Igigi, which is unchanged — an honest result,
not a gap papered over: Igigi's own textual evidence in this corpus
leans on collective/consciousness-form language this patch correctly
continues to treat as inconclusive, not on any of the newly-added
constructions.

## The Sage regression control

**Confirmed intact.** `book004.023_beyond_identity.scene004`'s Sage is
still, and only, `nonphysical` — the ranking rule from `f0f0698`
(explicit entity-state evidence outranks physical action evidence in
the same sentence) held exactly as designed, verified with a dedicated
test using a constructed worst-case sentence combining both kinds of
evidence for Sage in one clause.

## New `@entities_manifested` entries: 21, all explained

```text
Mordain    -- ch1 scene1, possessive body-part evidence, known_spawnable
Elyraen    -- ch2 scene1, possessive body-part / locomotion evidence
Senareth   -- book002.005.scene005, locomotion/body-part evidence
Torhh      -- 4 scenes (book002.005/007, book003.009/015), mixed
              locomotion and body-part evidence
Pazuzu     -- 3 scenes (book002.006, book003.009x2), mixed contact and
              body-part evidence
Zephyr     -- 4 scenes (book004.016/018/019x2), mixed body-part and
              contact evidence
Torrhen    -- book004.020.scene001, body-part/locomotion evidence
Oreck      -- 5 scenes (book005.027x4, book005.028x1), contact/body-part
              evidence (including the "grabbed...furrows" case this
              audit examined directly)
Mika       -- 2 scenes (book005.028.scene002/005), body-part or
              locomotion evidence
```

Every one is `known_spawnable` in `world_rules.json` (already confirmed
`@entities`-eligible before this patch) and now also correctly
`presence: local, physicality: physical` from real, specific textual
evidence — not a single one is a name flagged elsewhere as noise or
newly seeded without support.

## Regression coverage

14 new tests in `test_pattern1_physicality_attribution.py`'s new
`TestPhysicalVocabularyExpansion` class: each new family firing
correctly, the bare-body-part-noun-alone rejection, bare-"felt"-for-
emotion rejection, the mental-metaphor guard for ambiguous contact
verbs, and dedicated tests confirming each of the three deliberate
exclusions (`touch`, `carried`, `struck`) does not fire in its
confirmed contaminating construction. Plus the Sage regression control.
Full `tier3/mettaext` suite: **111 passed** (97 previous + 14 new,
one existing test's expected value corrected from `unknown` to
`physical` since the new vocabulary genuinely and correctly resolves
that case now — documented in the test itself, not silently changed).

## What this tells us about the remaining `unknown` population

297 of 583 local-presence entities remain `unknown` after both fixes.
Some, like the 130 originally identified in `6e403d5` with zero prose
mentions at all (pure participant-line seeds), are genuinely
unknowable from the text as written — no vocabulary work can help
there. Others, like Igigi's unchanged count, reflect real textual
ambiguity this patch correctly declined to resolve rather than guess
at. Distinguishing the rest — genuinely unknowable vs. still a
coverage gap — would need another clustering pass over what's left,
not assumed here.

## What was deliberately not done

Nonphysical entity-state rules, presence inference, participant
seeding, remote/reference inference, world_rules/aliases,
`@entities_manifested`'s own projection logic, and
`semantic_environment_extractor` are all untouched. No unrelated
findings were fixed during this patch.
