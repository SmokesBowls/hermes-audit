# Semantic quality audit: Books 1-5's 124 authored scenes

Structure is proven (`bee9cc5`): 27/27 chapters, 124/124 authored scenes,
zero segmentation mismatches. This audit asks the next question —
**given Metta now reliably finds the scenes, how reliably does it
understand what's in them?** — using only the already-generated
Mettaext evidence corpus from that run (`entities_observed`,
`@entities`, `@entities_manifested`, `scene_meta`, and the raw
`out_pass1_*.txt` segment text Mettaext itself produced). The vault was
not re-consulted as an alternate authority anywhere in this audit — every
finding below is checked against Mettaext's own output, not against the
original manuscript. No code changed, nothing rerun, nothing fixed.

Findings are grouped by repeated pattern, not one scene at a time, per
instruction.

## Pattern 1 — physicality coverage gap: the biggest single finding

**152 instances** (across 22 of 27 chapters) of an entity correctly
classified `presence: local` — via the authored `participants:` line,
which remains 100% reliable (see the zero-count check below) — that
then gets `physicality: unknown` because neither the physical nor
nonphysical keyword lexicon fires anywhere in that entity's mentions.

```text
chapter.book001.003_first_contact           21
chapter.book005.024_the_first_spark         20
chapter.book005.028_ragnarok                19
chapter.book002.005_the_garden_blooms       14
chapter.book002.006_the_first_coming         9
chapter.book005.025_confined_freedom         9
chapter.book005.027_the_claiming             8
chapter.book004.017_niburu_shadow            7
chapter.book003.011_escalation_and_desperation 7
chapter.book002.007_the_needle_construction  6
chapter.book003.015_betrayal                 6
chapter.book005.026_dragonmail               6
... (18 more chapters, 1-5 each)
```

This confirms directly what `bee9cc5` already flagged about the remote
lexicon: **both manifestation keyword lexicons (`PHYSICAL_MANIFESTATION_KEYWORDS`/
`NONPHYSICAL_MANIFESTATION_KEYWORDS`) were hand-built from Chapter 1/2's
specific phrasing and have weak recall everywhere else.** A locally
present entity in Books 2-5 whose scene doesn't happen to use one of the
~20 tuned keywords (`stood`, `consciousness`, `humanoid form`, etc.)
correctly, safely falls to `unknown` rather than being guessed — but
that means `@entities_manifested` systematically **under-manifests**
across most of the corpus, not because the manifestation logic is wrong,
but because its evidence vocabulary is too narrow. This is the practical
answer to "is this ready for Dragon to auto-build content from": not
yet, on physicality specifically — most locally-present characters in
Books 2-5 currently produce no physicality signal at all.

## Pattern 2 — character alias mismatch: participants uses a title, prose uses a name

A clean, well-evidenced, reproducible case. Book 5's protagonist is
narrated throughout as **"Geralt"**, but early `participants:` lines
name him only as **"The Nameless One"** (the book's own title). Since
presence detection is pure literal substring matching against the
`participants:` string, "Geralt" cannot resolve to local when only
"The Nameless One" appears there — and does not, for a specific,
traceable stretch:

```text
chapter.book005.024_the_first_spark.scene001  participants: "The Nameless One (Geralt)"   -> Geralt: local (parenthetical saved it)
chapter.book005.024_the_first_spark.scene004  participants: "Anunnaki Elders / Observers"  -> Geralt: presence unknown (4 mentions)
chapter.book005.024_the_first_spark.scene009  participants: "The Nameless One, ..."         -> Geralt: presence unknown (4 mentions)
chapter.book005.025_confined_freedom.scene001-004  participants: "The Nameless One, ..."    -> Geralt: presence unknown every time
                                                                                                (6, 4, 6, 4 mentions -- clearly the
                                                                                                 scene's own protagonist, per the
                                                                                                 scene's own focus: "Geralt awakens...
                                                                                                 Geralt commands the Five...")
chapter.book005.026_dragonmail.scene001       participants: "The Nameless One (Geralt)"    -> Geralt: local again (parenthetical present)
chapter.book005.026_dragonmail.scene003+      participants: "Geralt (spirit-form)"          -> Geralt: local from here on, reliably
chapter.book005.027_the_claiming onward       participants: "Geralt, Oreck, ..."            -> Geralt: local + physical, reliably,
                                                                                                for the rest of the book
```

The pattern resolves itself once the author's own naming converges
(book 5, chapter 27 onward uses "Geralt" consistently) — this is not a
permanent defect, but it produced roughly 6 scenes where the book's own
protagonist, actively performing physical actions per the scene's own
`focus:` text, was invisible to presence detection. Worth generalizing:
**any character whose canonical prose name differs from the name or
epithet used in that scene's `participants:` line will silently fail to
resolve to local**, with no error, no warning — it just falls to
`unknown` like any other absent evidence.

## Pattern 3 — title/epithet fragments extracted as spurious separate "entities"

Confirmed recurring, not a one-off: multi-word titles produce a
free-floating single-word fragment candidate that then receives full
presence/physicality inference as if it were its own character.

```text
"Aeon Keepers"      -> "Aeon" extracted separately (seen since Book 1;
                        recurs in book002.005, book003.012/014, book005.026/027/028)
"The Nameless One"  -> "Nameless" extracted separately (book005.024/025/026),
                        reaching mentions as high as 32 in a single scene,
                        and flip-flopping physicality scene to scene:
                        physical (0.85) in some scenes, nonphysical (0.85)
                        in others, unknown in others -- for what is not a
                        character at all, just a title fragment.
```

Harmless for `@entities`/`@entities_manifested` specifically — both
fragments are correctly `known: false, spawnable: false` and never
reach either field (confirmed: zero manifestation-consistency
violations corpus-wide, `bee9cc5`) — but they pollute
`entities_observed`'s presence/physicality evidence with a
non-existent "character" whose classification is essentially noise,
and would mislead any consumer treating `entities_observed` as a
reliable per-name cast list rather than raw candidate evidence.

## Pattern 4 — real named participants silently absent from `entities_observed`, not just misclassified

Distinct from pattern 2 (misclassified) — these never became a
candidate at all, because `extract_characters()`'s fixed 3+-mention (or
explicit-speaker) threshold wasn't met in that specific scene's own
prose, even though the author explicitly listed the character in
`participants:`.

```text
Mika    -- named in participants for chapter.book005.024's scenes
           005/010/011 and chapter.book005.025's scene003 -- absent
           from entities_observed in all four, despite being a
           recurring, clearly-real character elsewhere in the same book.
Zephyr  -- named in participants for book004.019.scene004,
           book004.022.scene001, book004.023.scene001 -- absent from
           entities_observed in those three specific scenes, despite
           being correctly extracted as local+physical/nonphysical in
           every other scene of the same chapters.
Saresh  -- named in participants for book003.012.scene002 and
           book003.014.scene001 -- never appears in entities_observed
           at all.
Torhh   -- one isolated miss, book002.007.scene002, despite being
           well-represented everywhere else in Books 1-2.
```

This is a quieter failure mode than a wrong classification: there is no
`unknown` entry to audit, no evidence trail at all — the name is simply
absent, and only comparing against the scene's own authored
`participants:` string surfaces it.

## Pattern 5 — remote-presence detection: confirmed effectively nonexistent outside Chapter 1

Only **1 of 124 scenes** produced a `remote` classification anywhere in
the corpus (Pelagor, chapter 1). Consistent with `bee9cc5`'s flag, now
with the concrete counter-example that shows the cost: Chapter 4's
Pelagor (7 mentions, entirely historical/ancestral — "the Pelagor who
had once ventured onto Tiamat's shores... had been chased away", "ten
thousand years later, the Pelagor's descendants") and Book 4's Torrhen
post-dissolution (7 mentions, entirely about his absence — "One month
after Torrhen's dissolution", "since Torrhen's dissolution") both
correctly avoid being marked `local`, but land on `unknown` rather than
anything resembling `remote` or `referenced_only`. This is the exact
gap `405d1b7`'s design already named as open and unimplemented
(`referenced_only` "is not actively inferred by any rule here yet") —
this audit is the first quantified evidence of how often that gap is
actually hit: entities discussed only in memory/history/backstory are
common across Books 2-5, and all of them currently collapse into the
same generic `unknown` bucket as entities with no evidence at all,
losing the "this is explicitly a historical/absent reference" signal
the raw text actually supports.

## Pattern 6 — registry coverage gap (reaffirmed, not re-audited in depth)

Same finding as `bee9cc5`: `Sage`, `Keen`, `Kael`, `Tess`, `Dren`, and
similar real, recurring names across Books 2-5 remain `known: false`
because `world_rules.json` has no entries for them. Not re-investigated
further here since it was already fully characterized in the prior
receipt and is lore/registry work, not an extraction defect.

## `@entities_manifested` itself: mechanically consistent, evidentially incomplete

No new violations found beyond what `bee9cc5` already confirmed (zero
in either direction, corpus-wide). The suspicious-looking cases this
audit turned up are all consequences of Pattern 1/2/4 above feeding
into it, not new logic bugs in the manifestation projection itself:
scenes that are clearly action-heavy per their own `focus:` text (e.g.
book005.024.scene002's "Nameless" showing `physicality: nonphysical`
at 24 mentions in what the scene's own focus describes as physical
labor/excavation) end up with thin or empty `@entities_manifested` not
because the projection rule is wrong, but because the underlying
`entities_observed` record it reads from is incomplete or mislabeled
for the reasons above.

## Separate inventory: `semantic_environment_extractor` occurrences (not fixed)

45 occurrences total, confined to 14 of 27 chapters — notably **zero**
in Book 1 this run, concentrated in Books 2-5:

```text
book002.007_the_needle_construction            1
book003.009_stalemate_departure_the_first_coming 1
book004.017_niburu_shadow                      1
book004.018_the_wandering                      6
book004.019_the_sacrafice                      1
book004.020_the_collapse                       4
book004.021_the_first_lesson                   5
book004.022_final_calculation                  6
book004.023_beyond_identity                    4
book005.024_the_first_spark                    7
book005.025_confined_freedom                   4
book005.026_dragonmail                         1
book005.027_the_claiming                       2
book005.028_ragnarok                           2
```

All non-fatal (caught exceptions; all 27 chapters still completed with
exit 0). The uneven per-scene distribution (45 occurrences across 124
scenes, not one-per-scene) was not investigated further — out of scope
for this audit per instruction, and the module is still simply absent,
same as `4c7bf79`'s original finding.

## Answer to the question this audit was for

```text
Metta now reliably knows WHERE THE SCENES ARE.        -- proven, bee9cc5
Metta reliably knows WHO IS LOCALLY PRESENT.           -- strong: 0 false
                                                           positives found
                                                           in the
                                                           participants-
                                                           line matcher
                                                           itself
Metta unreliably knows WHETHER THAT PRESENCE IS         -- weak: 152
  PHYSICAL OR NONPHYSICAL outside Book 1/2's               unknowns,
  specific phrasing.                                       narrow lexicon
Metta does not yet distinguish "referenced/historical"  -- not
  from "no evidence at all" -- both are "unknown".        implemented,
                                                            confirmed
                                                            costly at scale
Metta can silently miss a real, authored participant    -- confirmed,
  in a specific scene if the frequency threshold isn't    4 named
  met there, even though the author listed them.          instances found
Metta can silently misclassify a real character as       -- confirmed,
  presence:unknown for several scenes if the author's      1 clean case
  own naming in participants: doesn't match the prose.     (Geralt), self-
                                                            resolving
Metta can extract a title fragment as a fake entity      -- confirmed,
  and apply full (flip-flopping) presence/physicality      2 recurring
  inference to it -- harmless for @entities, noisy for     cases (Aeon,
  entities_observed.                                       Nameless)
```

**Before Dragon automatically turns these 124 scenes into game
content, the physicality coverage gap (Pattern 1) is the one that
matters most at scale** — it's not wrong, it's just silent on most of
Books 2-5's cast, which would leave `@entities_manifested` sparse
almost everywhere outside the two chapters its keyword lexicon was
built from.

## What was not done

No Mettaext code changed. Nothing rerun. No fixes proposed as
implementation — patterns are reported for a future scoping decision,
not applied here. The vault was not consulted as an independent
authority anywhere in this audit; every claim above is sourced from the
Mettaext evidence corpus generated in `bee9cc5`'s run (`entities_observed`,
`scene_meta`, and the raw `out_pass1_*.txt` text Mettaext itself produced).
