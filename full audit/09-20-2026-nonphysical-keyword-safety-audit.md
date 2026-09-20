# Nonphysical keyword safety audit: all five flips are false classifications, and the root cause is systemic

Read-only, per instruction. No code changed. Uses only the fresh
Books 1-5 corpus generated after `5514843`. Answers two questions:
whether the five physical→nonphysical flips are real, and how safe
each current `NONPHYSICAL_MANIFESTATION_KEYWORDS` entry actually is.

## Headline finding

**All five flips are false nonphysical classifications**, and this
isn't confined to those five scenes — the same root cause (`consciousness`/
`awareness` treated as proof of bodilessness rather than a mode of
mental activity) misclassifies the same characters **repeatedly, across
other scenes in the corpus**, most severely for Zephyr, this book's own
protagonist.

## The five flips, examined individually

**Pazuzu & Torhh**, `book002.008_queens_assessment.scene003`:

```text
"Torhh worked alongside Pazuzu in the late afternoon light, their
consciousness-touches cooperating to shape stone for the Needle's
foundation despite the fundamental wrongness of what they built."
```

This sentence describes them **doing physical construction labor**
("shape stone for the Needle's foundation") using a magical
communication technique ("consciousness-touches") as their *method* of
cooperating — not a claim that either lacks a body. "Torhh rumbled
acknowledgment" (a vocal, embodied sound) and "Torhh's consciousness
was already processing implications" (mental activity, not entity
state) round out the scene's evidence. **False.**

**Zephyr**, `book004.016_the_choice_third_coming.scene001`:

```text
"Zephyr closed his eyes, letting his consciousness expand into the
mathematical space where pure logic dwelt."
"Zephyr's mathematical consciousness interfaced directly with the
device, processing information streams..."
```

"Zephyr closed **his eyes**" is direct, explicit body-part evidence in
the *same sentence* as the nonphysical trigger — the current physical
lexicon simply doesn't have "eyes" in it (confirmed gap from
`6e403d5`'s vocabulary audit), so this sentence's own physical evidence
was invisible to the classifier while its nonphysical evidence wasn't.
**False, and unambiguously so.**

**Igigi**, same scene: `"the soft glow of Igigi consciousness pulsed..."`,
`"Igigi consciousness-forms began initiating emergency scatter
protocols"`. Counter-evidence in the same scene: `"Elder Pazuzu
declared, his ancient FORM beginning to GLOW with the accumulated power
of eons"` — Igigi appear to have physical forms that glow, not an
absence of form. **Likely false**, held with slightly less confidence
than the two individually-named cases above since Igigi is a
species-level reference and this book's own worldbuilding for the
species isn't fully pinned down by this scene alone.

**Anunnaki**, same scene: `"their advanced consciousness siphoned to
power Anunnaki technology"`. Corpus-wide, Anunnaki are established as
physically embodied throughout Books 1-5 (Overseers who review reports,
a Queen who "descends" in a vessel, "Anunnaki battle-forms"). "Consciousness
siphoned" describes their mental capacity being exploited as a resource,
not a claim about their bodies. **Likely false**, same confidence
caveat as Igigi.

## This is systemic, not five isolated scenes

Checked each of the five names' classification across every scene in
the corpus, not just the flipped one:

```text
Pazuzu:    7 physical, 7 nonphysical, 2 unknown
Torhh:     6 physical, 6 nonphysical, 6 unknown
Zephyr:    2 physical, 11 nonphysical, 4 unknown
Igigi:     4 physical, 5 nonphysical, 2 unknown
Anunnaki:  4 physical, 2 nonphysical, 9 unknown
```

**Zephyr is the starkest case**: nonphysical in 11 of 17 classified
scenes (65%) despite being this book's protagonist, established
elsewhere as unambiguously embodied. Sampled four of those 11 scenes'
actual triggering evidence directly:

```text
"Zephyr closed his eyes, letting his consciousness expand..."
"Zephyr felt the change before he saw it... his consciousness recoil..."
"Zephyr learned to reshape his mathematical consciousness into
  survival algorithms, calculating optimal energy expenditure for
  each movement, each breath, each heartbeat."
"Zephyr followed, his consciousness burning through energy reserves
  at unsustainable rates just to maintain thermal equilibrium..."
"For three days, Zephyr survived in that impossible cave while his
  consciousness struggled to process what he had witnessed."
```

"Each breath, each heartbeat," "maintain thermal equilibrium," and
"survived... for three days" are unambiguous evidence of a living,
metabolizing body — sitting in the immediate vicinity of the exact
same "consciousness" language currently coded as proof of the opposite.
Pazuzu and Torhh's even three-way splits (physical/nonphysical/unknown)
point at the same mechanism operating less severely but just as really.

## Keyword-by-keyword audit of `NONPHYSICAL_MANIFESTATION_KEYWORDS`

```text
"no body"                        STRONG
"without a body"                 STRONG
  Direct, explicit entity-state claims. No corpus evidence found of
  either misfiring.

"distributed awareness"          CONTEXTUAL
  Stronger than bare "awareness" alone -- "distributed" specifically
  implies existence spread without a singular bodily locus (Lyaris's
  original description: "existed as distributed awareness across
  probability matrices"). Trustworthy in an "existed as X" construction;
  not verified safe in other constructions since none appeared in this
  corpus.

"ethereal"                       CONTEXTUAL, weaker than assumed
  Confirmed real corpus example where "ethereal" describes an OBJECT
  the entity physically interacts with, not the entity itself, while
  the entity is clearly embodied in the same sentence:
    "Oreck—recovered enough to move—grabbed the spectral chain and
    tore it free with claws that left furrows in ethereal matter."
  Oreck has claws, grabs, and tears -- unambiguously physical -- but
  "ethereal" (describing the matter he's tearing, not him) still counts
  as nonphysical evidence for Oreck under the current same-sentence
  rule. Safe only when the construction ties "ethereal" to the
  entity's own described nature ("existed as an ethereal being," "her
  ethereal form"); unsafe when it modifies some other noun that
  happens to share the sentence.

"consciousness"                  UNSAFE STANDALONE
"awareness"                      UNSAFE STANDALONE
  Confirmed extensively: describes a MODE OF MENTAL ACTIVITY or
  communication technique by an entity that may be, and in every
  checked case here actually is, otherwise embodied. Same-sentence
  scoping (5514843) correctly ties the word to the right entity, but
  does not establish that the word means what the keyword list assumes
  it means.

"projected her awareness"        UNSAFE
"projected his awareness"        UNSAFE
"projected their awareness"      UNSAFE
  These directly contradict the design principle they were supposedly
  built to encode. 405d1b7 explicitly established "Vaelith projected
  her awareness through the Veil" describes her ACTION, not her
  location or state -- yet the implemented keyword list (fc3e3d1) added
  the literal phrase as POSITIVE nonphysical evidence anyway. This is
  the same conflation as bare "consciousness"/"awareness," just
  phrased as a specific compound: projecting awareness somewhere is
  compatible with having a body exactly as much as it's compatible
  with not having one. Did not fire for any of this session's five
  flip cases, but is confirmed unsafe by the same reasoning and the
  same rule the user just restated: "projects awareness ≠ is
  nonphysical."
```

## The rule, confirmed against real evidence rather than asserted

```text
uses consciousness       ≠ is nonphysical    -- confirmed (Zephyr, Pazuzu, Torhh, Anunnaki)
has awareness             ≠ is nonphysical    -- same keyword family, same evidence
projects awareness        ≠ is nonphysical    -- confirmed by design history (405d1b7 vs. fc3e3d1)
                                                  even though it didn't fire here
explicitly exists without a body,
  or is explicitly manifested as
  consciousness/ethereal PRESENCE
  (not merely uses consciousness
  as a verb/faculty)              → nonphysical  -- "no body"/"without a body" hold up;
                                                     "distributed awareness" holds up in its
                                                     one verified construction; "ethereal"
                                                     holds up only when it modifies the
                                                     entity itself, not a nearby noun
```

## What this means for the vocabulary-expansion patch

Confirms the concern that prompted this audit precisely: adding
physical-vocabulary families (`bodily_description`, `physical_sensation`,
etc.) *before* fixing this would very likely have "corrected" Zephyr's
case the moment "eyes" or "breath" entered the physical lexicon — not
because the nonphysical inference became sound, but because it would
have been outvoted by a coincidentally-present physical keyword
elsewhere in the same evidence window. That would leave the underlying
conflation intact and undetected for any future scene where the
character happens not to have a competing physical keyword nearby —
exactly the failure mode the user flagged before it could hide inside
a passing test case.

## What was not done

No code changed. `NONPHYSICAL_MANIFESTATION_KEYWORDS` was audited, not
edited. No fix implemented for any of the "unsafe"/"contextual"
findings above. The five flipped classifications were not corrected in
the corpus. Physical vocabulary expansion remains on hold pending a
decision on how to handle `consciousness`/`awareness`/the `projected
...awareness` compounds.
