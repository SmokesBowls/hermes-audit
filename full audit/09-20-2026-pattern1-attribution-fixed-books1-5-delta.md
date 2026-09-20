# Pattern 1 attribution scope fixed and live-verified — delta from `6e403d5`

Implements the fix specified after `6e403d5`'s audit. Scoped exactly as
instructed: `infer_physicality_enhanced()` only. No vocabulary changed
anywhere.

## What changed

Two evidence-scope narrowings, applied in this order:

```text
1. ALL scene-metadata segments excluded from physicality keyword
   scanning entirely (new _all_metadata_segment_indices() -- broader
   than the participants-only exclusion Pattern 4 uses for frequency
   counting, and deliberately so: metadata establishes scene facts,
   never narrative evidence of any one entity's physical state).

2. Ordinary prose evidence must share a SENTENCE with the entity's
   name, not merely a segment/paragraph.
```

Narrow exception, reusing existing infrastructure rather than inventing
new vocabulary: when a segment opens with `<Name> <speech-verb>` or
`<speech-verb> <Name>` (this file's own `_CONT_NAME_VERB_RE` /
`_CONT_VERB_NAME_RE`, already used by `infer_speakers_enhanced()` for a
different purpose), and `Name` is the entity being evaluated, the whole
segment counts as that entity's evidence — so a quote following the
attribution isn't lost to sentence-splitting.

## Honest limit, not silently patched

The exception only fires for verbs already in `_SPEECH_VERBS`. The
audit's own concrete example — "Zaron mused." — uses "mused," which
isn't in that list. This case is **not** rescued by the exception and
correctly falls back to plain sentence scoping, landing on `unknown`.
Confirmed directly with a test (`test_verb_outside_speech_verb_list_is_
not_covered_by_the_exception`) rather than either silently expanding
`_SPEECH_VERBS` to make the demo case pass, or claiming success without
checking. Widening `_SPEECH_VERBS` is a small, separate, defensible
follow-up if wanted — not done here, since it would be a vocabulary
change and this patch was scoped to attribution only.

## Live delta: fresh Books 1-5 rerun vs. `6e403d5`'s baseline

```text
Primary invariant:                    27/27, unchanged
Manifest consistency violations:      0, unchanged

Saresh (the control case):
  before: nonphysical, confidence 0.85, mentions=0
  after:  unknown,     confidence 0.0,  mentions=0        FIXED

Local-presence physicality distribution:
                    before    after
  physical            200       187
  nonphysical         159       141
  unknown             205       236

31 classifications dropped from physical/nonphysical to unknown --
  the metadata-only-supported calls that lost their sole evidence
  source, exactly as intended. (Not the full 72 flagged "at risk" in
  the audit -- most of those also had independent, valid prose
  evidence that survived untouched, confirming the audit's own caveat
  that many at-risk cases were still probably correct.)

5 classifications changed VALUE (all physical -> nonphysical):
  Pazuzu & Torhh, book002.008.scene003 -- their own sentences in this
    scene emphasize "consciousness-touches" as their described mode
    of interaction; the prior "physical" label came from elsewhere in
    the old segment-wide scan. A defensible, evidence-consistent
    result for what this specific passage's text actually says, not
    a confident "was wrong, now right" claim -- worldbuilding context
    elsewhere establishes both as embodied Giants, but that context
    isn't in this scene's own text.
  Zephyr, Igigi, Anunnaki, book004.016.scene001 -- Zephyr's own
    sentences ("Zephyr's mathematical consciousness interfaced
    directly with the device", "letting his consciousness expand into
    the mathematical space") are genuine same-sentence nonphysical
    evidence; the prior "physical" label was very likely borrowed
    from an unrelated sentence elsewhere in the old segment-wide scan.
    Igigi/Anunnaki are collective/species terms already excluded from
    @entities on other grounds -- their individual physicality label
    is conceptually questionable regardless of this fix (a collective
    noun having "a" physicality is its own separate, unresolved
    question), noted but not addressed here.
```

323 of 359 original physical/nonphysical calls (90%) are completely
unchanged — the large majority of existing correct classifications
survived exactly as the acceptance criteria required.

## Acceptance criteria, checked one by one

```text
Saresh no longer receives false nonphysical.              CONFIRMED
72 metadata-trigger classifications disappear unless
  independently supported by narrative evidence.          CONFIRMED --
  31 disappeared (no independent support); the remainder
  kept their classification because independent prose
  evidence existed all along, exactly as the audit predicted
  some would.
Existing correct sentence-supported classifications
  remain unchanged.                                        CONFIRMED --
  323 of 359 (90%) identical before/after.
Zaron-style speaker/action-linked cases remain
  classifiable through existing association, not broad
  segment scanning.                                        PARTIALLY --
  the general mechanism (name+speech-verb attribution)
  works and is tested; Zaron's own literal example uses a
  verb ("mused") outside the existing verb list and is
  honestly reported as not covered, not force-fit.
unknown preferred over borrowing physicality evidence
  from another entity.                                     CONFIRMED --
  direct test with two names in one segment, keyword only
  in the sentence naming the other one.
```

## Regression coverage

9 new tests in `test_pattern1_physicality_attribution.py`: the Saresh
control case; metadata exclusion working symmetrically (doesn't
manufacture a false classification either direction) while leaving
real prose evidence intact; same-sentence classifications unchanged;
cross-sentence-within-segment no longer borrows evidence; both
speech-verb attribution orderings extending evidence correctly; and
the honest, explicit test confirming the verb-list limit is a known
boundary, not an oversight. Full `tier3/mettaext` suite: **85 passed**
(76 previous + 9 new).

## What was deliberately not done

No vocabulary added to either keyword lexicon, anywhere. `_SPEECH_VERBS`
left unchanged, including not adding "mused" to rescue the one demo
case. The Igigi/Anunnaki collective-noun-physicality question is noted,
not resolved. Pattern 3 title-fragment noise, remote inference, and
world_rules/alias work remain untouched.

## Next

Per the agreed sequencing, vocabulary expansion (`bodily_description`,
`physical_sensation`, `touched_carried_struck`, `touch_manipulate`, and
the smaller locomotion/body-formation gaps from `6e403d5`) can now
proceed against a corpus where the evidence window is no longer leaking
between entities.
