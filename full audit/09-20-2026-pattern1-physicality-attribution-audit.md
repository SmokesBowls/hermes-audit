# Pattern 1 read-only audit: physicality vocabulary vs. attribution scope, Books 1-5

Read-only, per instruction. No code changed. Uses only the freshly
regenerated Books 1-5 corpus (post `e4c3d54`) — the vault was not
consulted. Every `entities_observed` entry with `presence: local` was
partitioned and, for physical/nonphysical calls, checked for whether
the triggering keyword actually shares a sentence with the entity's
name, or only the same segment/metadata line.

## Headline answer

**Both, as expected — but not in equal measure, and not in the order
that matters most.** Attribution/proximity is the smaller-count but
higher-priority problem: it silently corrupts calls the lexicon
*already* thinks it can make correctly, including some that are
currently reported as confident and clean. Vocabulary coverage is the
larger-count problem, but it fails safely (to `unknown`) and won't get
worse by itself.

```text
Local-presence entities with a physical/nonphysical call: 359
  Metadata-segment trigger present (at risk regardless of
    sentence-level logic):                                  72  (20%)
  Prose-only, sentence-confirmed (likely correct):          282  (79%)
  Prose-only, cross-sentence within the same paragraph
    (genuine attribution-radius failure in real narrative):    5  (1%)

Local-presence entities with physicality: unknown:          205
  Zero prose text mentioning the name at all (pure
    participant-line seed, nothing to classify from):        130  (63%)
  Real prose text exists, clustered into recurring
    evidence families below:                                  75  (37%)
```

## Partition, as requested (exact counts)

```text
correctly physical (prose-only, sentence-confirmed):          183
correctly nonphysical (prose-only, sentence-confirmed):        99
physicality unknown:                                          205
likely false / at-risk physical
  (metadata-trigger present):                                  14
  (prose-only but cross-sentence):                               3
likely false / at-risk nonphysical
  (metadata-trigger present):                                  58
  (prose-only but cross-sentence):                               2
```

Notably, the metadata-trigger risk skews heavily toward `nonphysical`
(58 of 72, vs. 14 `physical`) — because the current
`NONPHYSICAL_MANIFESTATION_KEYWORDS` list is dominated by
`consciousness`/`awareness`, exactly the vocabulary that authored
`participants:` lines use constantly to describe *other* entities'
natures parenthetically (`"Torrhen (embedded consciousness)"`,
`"Aeon Keepers (consciousness contact)"`) — so the nonphysical lexicon
is far more exposed to metadata-line cross-contamination than the
physical one is.

**Important caveat, stated precisely rather than glossed over**: "72
have a metadata-segment trigger" does not mean all 72 are wrong. Many
of these names (Torrhen, Zephyr, Torhh, Pazuzu, Sage, Geralt) are real,
heavily-narrated characters who *also* have solid, independent prose
evidence elsewhere in the same scene — for them, the classification is
very likely still correct, just resting on an evidentiary foundation
that includes an illegitimate input alongside the legitimate one. The
audit did not attempt to determine, name by name, whether the metadata
trigger was load-bearing or redundant — only that it is present and
should not be. The concrete, load-bearing failures found were where
metadata was the *only* signal:

```text
Saresh, chapter.book003.012_nephilim_summoning.scene002 -- the
  confirmed control case. Zero prose mentions. Classified
  physicality: nonphysical, confidence 0.85, purely because the
  scene's own participants line reads "...Saresh, Giant tribes,
  Pazuzu, allied Igigi, Torrhen (embedded consciousness), Aeon
  Keepers (consciousness contact)" -- "consciousness" describes
  Torrhen and the Aeon Keepers, not Saresh, but sits in the same
  segment as his name.
```

## The attribution question: what's the smallest safe evidence scope?

Tested three candidate scopes directly against the corpus:

**"Same segment" (current behavior)**: too broad. Causes all 72
metadata-trigger cases, because a comma-separated `participants:` line
naming six entities and describing two of them parenthetically is one
segment, and the check only asks "does this segment contain the name
anywhere AND the keyword anywhere."

**"Same sentence" (naive, period-delimited)**: fixes ordinary prose
cross-sentence misattribution (all 5 genuine cases below), but
**does not fix Saresh, or any other metadata-line case**. Checked this
directly rather than assuming it would help: a `participants:` line is
a comma-separated list with no sentence-terminating punctuation at
all, so a period-based sentence splitter treats the entire line as one
"sentence" — Saresh and "consciousness" still land in the same
"sentence" under this scope. Same-sentence scoping is necessary but
not sufficient on its own.

**Recommended combination, validated against the data (not
implemented — this audit is read-only)**:

```text
1. Exclude metadata segments from physicality evidence scanning
   entirely -- the exact same exclusion pattern already established
   for frequency counting in the Pattern 4 fix (e4c3d54), applied to
   infer_physicality_enhanced() instead of extract_characters(). This
   is not a new mechanism to design; it's reusing
   _metadata_segment_indices()-style detection in the one other place
   physicality inference currently ignores it. This alone would
   eliminate all 72 metadata-trigger cases, including Saresh, cleanly.

2. Narrow prose-only evidence scope from "same segment" to "same
   sentence" for non-dialogue segments. This would eliminate the 5
   genuine cross-sentence-within-paragraph cases below, at negligible
   cost -- 282 of 287 prose-triggered cases already satisfy this
   scope, so almost nothing that's currently correct would be lost.
```

The five genuine cross-sentence cases, for concreteness:

```text
Elyraen, book002.005.scene007 (physical, kw="falling") -- "falling"
  describes thought-seeds cast generations ago in a rhetorical
  question, several clauses removed from Elyraen's own name.

Genesis, book003.010.scene002 (physical, kw="stood") -- ambiguous
  whether "Genesis" is even a distinct named character here rather
  than a descriptor ("the genesis AI"); flagged, not resolved.

Igigi, book004.016.scene001 (physical, kw="stand") -- "will stand
  with me" is dialogue attributed to Pazuzu, referring to a group
  ("we"); Igigi is a species/collective reference in an adjacent
  sentence, not the one standing.

Zaron, book005.026.scene004 (nonphysical, kw="consciousness") --
  Zaron's own dialogue ("Three consciousness sharing single host")
  is genuinely about himself, but the sentence split separates the
  "Zaron mused." attribution from the quoted content. Same-sentence
  scoping alone would make this WORSE, not better, by unlinking a
  correct attribution -- worth naming explicitly, since it argues for
  the "speaker/action linkage already produced elsewhere in Pass 2"
  option too: dialogue segments already carry resolved speaker
  attribution (infer_speakers_enhanced()) that a sentence-only rule
  would ignore. A dialogue segment's speaker should probably count as
  "same clause" for its own quoted content, as a documented exception
  to plain sentence-splitting.

Freed, book005.028.scene005 (nonphysical, kw="consciousness") --
  "Freed" is very likely a fragment of "Freed Slaves"/"Newly Freed
  Slaves" (Pattern 3 territory, not a distinct character), so this
  case is arguably not a scope failure at all but a noise-extraction
  failure wearing a physicality-audit costume.
```

## Vocabulary families in the true "unknown, has evidence" bucket (75 of 205)

Only the 75 entities that have real prose text (excluding the 130 with
none at all) are counted here; an entity can match more than one
family.

```text
Family                        Count   Current lexicon coverage
bodily_description               32   NONE -- "eyes/hands/face/skin/
                                        limbs/arms/legs/voice/body" are
                                        not in PHYSICAL_MANIFESTATION_
                                        KEYWORDS at all
locomotion_posture                21   Partial -- "stood/walked/
                                        stepped" covered; "approached/
                                        ventured/positioned themselves"
                                        are not
physical_sensation                17   NONE -- "felt the X" pattern
                                        entirely absent from the lexicon
enter_exit_emerge                 11   Partial -- "emerged" covered;
                                        "entered/arrived/departed" not
touched_carried_struck            11   NONE -- "held/carried/gripped"
                                        entirely absent
body_formation_embodiment         10   Partial -- "humanoid form/
                                        muscles/organs" covered;
                                        "solidified/stone-flesh/
                                        manifested" not
touch_manipulate                   7   NONE
transformation_shapeshift          4   NONE -- "transformed" is
                                        currently only used defensively
                                        against false Tran matches
                                        (word-boundary), never as
                                        positive physicality evidence
dialogue_only_no_body               3   Correctly stays unknown --
                                        speech alone doesn't establish
                                        a body; this is fail-closed
                                        working as intended, not a gap
consciousness_ethereal               3   Ambiguous/overlapping cases
                                        (e.g. Geralt, elsewhere clearly
                                        physical) -- likely a
                                        family-matching artifact of
                                        combining multiple segments'
                                        text, not a real signal; not
                                        conclusive
```

Representative snippets (full set saved in this session's scratch
directory, available on request):

```text
bodily_description: "Got within twenty yards of the tree line before
  the same burnt-red Giant appeared and drove them back with
  threatening gestures—massive arms swinging, fists pounding ground."

physical_sensation: "Saresh of the Oasis Clans felt the scream in the
  marrow of its stone."

body_formation_embodiment: "Korrhan's stone-flesh had solidified
  unevenly—half-molten scars marking where the ritual's heat had
  exceeded survivable thresholds..."

touched_carried_struck / touch_manipulate: "Ishara held her newborn
  and tried not to calculate the probability that this child would
  live to adulthood in freedom."
```

**Desired classification vs. current, by family**: every family above
except `dialogue_only_no_body` and the ambiguous `consciousness_ethereal`
cluster represents real, concrete physical-embodiment evidence that a
human reader would call `physical` without hesitation. Current
classification for all of them is `unknown` — a pure vocabulary gap,
not an attribution failure (these entities aren't being misattributed
someone else's evidence; they simply have no matching keyword for
their own, real evidence).

## The 130 zero-evidence "unknown" cases

Nothing to cluster — these are participants seeded by `e4c3d54`'s fix
whose names literally never appear in that scene's narrative prose at
all, only in the `participants:` line. No classifier, however good,
can determine physicality from zero text. Correctly `unknown`, and
expected to stay that way unless the manuscripts themselves are
expanded — this is not a Mettaext gap.

## Answer to the framing question

```text
Is the next fix mainly better vocabulary, or better attribution?

By RAW COUNT: vocabulary. 75 real-evidence unknowns need new keyword
  families (bodily_description, physical_sensation, touched/carried,
  touch/manipulate chief among them) that the current lexicon,
  hand-built from Chapter 1/2, simply never anticipated.

By RISK TO ALREADY-MADE CLASSIFICATIONS: attribution. 72 of 359
  current physical/nonphysical calls (20%) rest partly or wholly on
  evidence that doesn't actually belong to that entity, confirmed via
  the Saresh control case and quantified corpus-wide, not merely
  inferred from one example.

Sequencing recommendation this audit's data supports: fix attribution
  first, specifically (1) excluding metadata segments from physicality
  scanning (reuses the Pattern 4 precedent exactly, narrow, high
  confidence) and (2) narrowing prose scope from segment to sentence
  (eliminates the 5 genuine cross-sentence cases, near-zero cost since
  282/287 already satisfy it) -- BEFORE adding the new vocabulary
  families. Confirmed concretely why order matters: every new keyword
  added to either lexicon is a new opportunity for a same-segment
  metadata line (which frequently lists several entities with rich
  descriptive parentheticals) to misfire the same way "consciousness"
  did for Saresh. Fixing scope first means new vocabulary added next
  inherits a narrow, already-correct evidence window instead of the
  current wide, leaky one.
```

## What was not done

No code changed. No keyword lists touched. No attribution-scope change
implemented. Pattern 3 title-fragment noise, remote inference, and
world_rules/alias work remain untouched and out of scope for this
audit. The vault was not consulted.
