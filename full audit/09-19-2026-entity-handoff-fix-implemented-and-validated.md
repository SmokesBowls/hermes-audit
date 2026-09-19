# Entity handoff fix implemented, tested, and live-validated against book 1

Implements and validates the plan from `787970f`, resolved with the
spawnable-safe interpretation of `@entities` confirmed after the
consumer trace (`04d8abe`). Committed to `EngAIn` as `bcdad29`.

## What changed

**PRIMARY — `tier3/mettaext/passroom/pass3_merge.py`,
`merge_to_zonj()`:** now projects the spawnable-true subset of
`entities_observed` into `@entities`, alongside the existing (byte-
for-byte unchanged) `entities_observed` assignment. Only assigned when
at least one spawnable entity exists, so Pass 4's own "not populated"
fallback still applies correctly when Pass 2 found nothing spawnable.

**DEFENSIVE — `tier3/mettaext/passroom/pass4_zon_bridge.py`,
`ZONBridge.extract_entities()`:** the narration-scan fallback's
`cn.lower() in all_text` substring check is now a word-boundary regex
match (`re.search(rf"\b{re.escape(cn.lower())}\b", all_text)`). Kept
as a fallback for malformed/legacy/partial input, not removed.

`@entities`'s meaning was **not** redefined globally — it keeps
meaning "spawnable-safe," matching what `tier2/godotsim`'s
`bridge_entities_for_scene()` already assumes with no changes needed
there, per the consumer trace's finding that this live runtime
consumer has no independent spawnable check of its own.

## Regression coverage

7 new tests in `tier3/mettaext/tests/test_pass3_pass4_entity_handoff.py`,
using real `world_rules.json` fixtures (Lyaris: known/non-spawnable;
Vairis: known/spawnable; Tran: known/spawnable,
`chapter_102`/`mars_convergence`) — matching the revised acceptance
checklist exactly:

```text
1. Lyaris present in entities_observed                    PASS
2. Lyaris absent from @entities (spawnable: false)         PASS
3. A genuinely spawnable entity (Vairis) reaches @entities  PASS
4. False "Tran" from "transformed"/"transformation" gone   PASS
5. A genuine standalone "Tran" still matches                PASS
6. entities_observed's shape unchanged (regression pin)     PASS
7. Normal pipeline input never reaches the fallback scan     PASS
```

Full existing `tier3/mettaext/tests/` suite: 34 pre-existing + 7 new =
**41 passed**, no regressions.

## Live validation: book 1, chapters 1-4, fresh rerun

Cleared all four chapters' current-schema artifacts (never touching
`legacy_pipeline_work/`) and re-ran `engain_door.py ingest` directly
for all four, same as the pre-fix baseline (`dce6854`), for a clean
before/after comparison on the same source text.

```text
                          Before (dce6854)         After (this fix)
Chapter 1 @entities:      Mordain, Pelagor,        Pelagor, Vaelith
                           Syreth, Theron,           (spawnable only)
                           Tran, Vaelith
Chapter 1 Lyaris:          absent everywhere         present in
                                                      entities_observed
                                                      (known: true,
                                                      spawnable: false)
"Tran" anywhere in         present, every chapter    absent, every
chapters 1-4:               (1, 2, 3, 4)              chapter (swept
                                                       all @entities
                                                       and
                                                       entities_observed
                                                       across all
                                                       scenes, zero hits)
Scene counts:               4, 4, 3, 4                4, 4, 3, 4
                                                       (unchanged --
                                                       scene-boundary
                                                       defect untouched,
                                                       as scoped)
```

Direct confirmation for chapter 1, scene 1 (the exact case traced in
`f1bf22a`):

```json
"@entities": ["Pelagor", "Vaelith"]

"=entities_observed": [
  {"name": "Aeon", "known": false, "spawnable": false, ...},
  {"name": "Ethereal", "known": true, "spawnable": false, ...},
  {"name": "Keepers", "known": false, "spawnable": false, ...},
  {"name": "Korath", "known": true, "spawnable": false, ...},
  {"name": "Lyaris", "known": true, "spawnable": false, ...},
  {"name": "Pelagor", "known": true, "spawnable": true, ...},
  {"name": "Tiamat", "known": true, "spawnable": false, ...},
  {"name": "Vaelith", "known": true, "spawnable": true, ...}
]
```

This is exactly the behavior described as the goal from the start of
this investigation: Dragon can now correctly say *"Lyaris is present
in the scene, but current evidence does not justify physically
spawning Lyaris"* — the data to support that sentence exists in the
generated evidence for the first time.

## What remains explicitly untouched, per the scoping instruction

The scene-boundary/`mechanical_word_chunk` defect (chapter 3 still
mechanically split into 3 scenes instead of its real 7 authored days),
the provenance-as-fake-narration-segment contamination, and the
missing `semantic_environment_extractor` module all reproduce
identically in this fresh rerun, exactly as before. None were touched
by this fix, as instructed — each remains its own independent, not-
yet-addressed defect from the original five-item list (`4c7bf79`).

## Net

```text
Entity handoff defect (Tran/Lyaris):  FIXED, tested, live-validated
Consumer risk (bridge_integration.py): AVOIDED -- @entities semantics
                                        left exactly as that consumer
                                        already assumes
Scope discipline:                      HELD -- no other defect touched
```
