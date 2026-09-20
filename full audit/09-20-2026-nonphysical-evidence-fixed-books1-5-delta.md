# Nonphysical evidence corrected and live-verified — from 141 to 1 across Books 1-5

Implements the correction specified after `c7c08b8`'s audit. Code +
tests committed to `EngAIn` as `f0f0698`. Scoped exactly as instructed:
`infer_physicality_enhanced()` and its nonphysical evidence
definitions only — no physical vocabulary touched.

## What changed

`NONPHYSICAL_MANIFESTATION_KEYWORDS` (bare `consciousness`, `awareness`,
`ethereal`, `projected <pronoun> awareness`) is removed entirely,
replaced by `_NONPHYSICAL_ENTITY_STATE_PATTERNS` — phrases that
actually predicate a bodiless state, not describe a mode of mental
activity:

```text
KEPT (already existed):        no body, without a body
ADDED, sound but unobserved:   no physical form, bodiless, disembodied,
                                noncorporeal, incorporeal
ADDED, grounded in real text:  had no physical (source|mass|substance|
                                  form|body)  -- "a weight... that had
                                  no physical mass"
                                existed (solely|only|purely) as (pure|
                                  distributed) (consciousness|awareness|
                                  energy|an ethereal X) -- Lyaris:
                                  "existed as distributed awareness
                                  across probability matrices"
ADDED, from the spec's own example:
                                <'s/his/her/their> form was (ethereal|
                                  incorporeal|nonphysical)
REMOVED: bare consciousness, awareness, ethereal, projected <pronoun>
  awareness -- confirmed these describe cognition/ability/action, not
  entity state (c7c08b8)
```

Evidence is now ranked, not tie-broken: an explicit entity-state claim
wins outright over ordinary physical-action evidence in the same
sentence — the opposite of the old "physical wins on conflict" rule,
because a direct "had no physical body"-class claim is a stronger fact
than an action verb. Bare mental-life vocabulary without a qualifying
construction now casts no vote at all in either direction.

## Live delta: fresh Books 1-5 rerun

```text
Primary invariant:                27/27, unchanged
Manifest consistency violations:  0, unchanged

Local-presence physicality distribution:
                before    after
  physical         187       187   (unchanged -- physical evidence
                                     detection untouched)
  nonphysical      141         1
  unknown          236       376
```

## The six named entities, as requested

```text
              before (c7c08b8)              after
Pazuzu        7 physical, 7 nonphysical,     7 physical, 9 unknown
                2 unknown
Torhh         6 physical, 6 nonphysical,     6 physical, 12 unknown
                6 unknown
Zephyr        2 physical, 11 nonphysical,    2 physical, 15 unknown
                4 unknown
Igigi         4 physical, 5 nonphysical,     4 physical, 7 unknown
                2 unknown
Anunnaki      4 physical, 2 nonphysical,     4 physical, 11 unknown
                9 unknown
Vaelith       (nonphysical, the original     1 unknown
                design case)
```

**Every one of the six now has zero `nonphysical` classifications
anywhere in the corpus.** None flipped to `physical` either — they
correctly landed on `unknown`, exactly the "no evidence of a body is
not evidence of no body" outcome the correction was built to produce.

## Every remaining nonphysical classification, corpus-wide, with its evidence

Exactly **one** survives across all 124 scenes:

```text
chapter.book004.023_beyond_identity, scene.book004.023_beyond_identity.scene004
  entity: "Sage" (mentions=10, known=false, spawnable=false)
  evidence: "The Sage existed as consciousness recognizing itself
    through every form it encountered while maintaining distinctiveness
    that served such recognition rather than limiting it."
```

This matches the `existed (solely|only|purely) as ... consciousness`
pattern precisely, and reads as a genuine, deliberate narrative beat —
Book 4's climactic "beyond identity" chapter describing the Sage's own
transcendence into a consciousness-only state at the story's end, not
an incidental mental-activity description like the 140 that were
removed. Worth noting: this is tracked under the separate name "Sage",
not "Zephyr" — the same underlying character split across two untied
names is the pre-existing alias-resolution gap flagged in earlier
sessions (Pattern 2 territory), not something this patch addresses.
`spawnable: false` either way, so it doesn't reach `@entities`.

## Regression coverage

Updated 4 existing tests whose fixtures depended on now-invalidated
bare evidence — most notably `test_vaelith_is_nonphysical` (renamed
`test_vaelith_physicality_is_unknown_not_forced_nonphysical`), since
Vaelith's original "projected her awareness" fixture is the exact case
`405d1b7` used to establish the "projects awareness != is nonphysical"
principle in the first place; the implemented keyword list had quietly
contradicted that principle until this patch. Added dedicated tests
for: bare vocabulary casting no vote (including the confirmed real
"ethereal matter" object-not-entity case, and a plain "ethereal blade"
case matching the correction spec's own example); every new pattern
firing correctly; and the ranking rule (entity-state evidence beats
physical action in the same sentence). Full `tier3/mettaext` suite:
**97 passed**.

## What was deliberately not done

No physical vocabulary added anywhere — `PHYSICAL_MANIFESTATION_KEYWORDS`
is byte-for-byte unchanged from `5514843`. The Sage/Zephyr alias split
is noted, not resolved. Metadata exclusion and sentence-scoping from
`5514843` are unchanged; this patch only redefined what counts as
nonphysical evidence within that already-corrected scope.

## Next

The corpus is now in the state the user described wanting before
vocabulary work begins: `unknown` (376) is doing almost all the work
outside a scene's own strong evidence, `physical` (187) is untouched
and was never the problem, and `nonphysical` (1) is down to a single,
well-evidenced case instead of 141 mostly-false ones. The physical-
vocabulary expansion (`bodily_description`, `physical_sensation`,
`touched_carried_struck`, `touch_manipulate`, and the smaller
locomotion/body-formation gaps from `6e403d5`) can now proceed without
competing against an overbroad negative classifier.
