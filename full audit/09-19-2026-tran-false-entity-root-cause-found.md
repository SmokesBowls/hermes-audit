# Root cause of the "Tran" false entity, found precisely — read-only trace, no fix applied

Full provenance trace, per instruction. No code changed. Answers every
sub-question asked, in order, plus corrects an error in my own earlier
reporting that the requested negative control exposed.

## 1. Confirmed: no standalone "Tran" in current source, chapters 1-4

```bash
grep -nio '\btran\b' 001_the_ethereal_vigil.md   # no matches
grep -nio '\btran\b' 002_molten_descent.md        # no matches
grep -nio '\btran\b' 003_first_contact.md         # no matches
grep -nio '\btran\b' 004_the_convergence.md       # no matches
```

Confirmed absent, whole-word, case-insensitive, in all four current
chapter files.

## 2-3. Searched runtime code/registries; distinguished active from inactive

Searched `world_rules_loader.py`, `pass2_entity_filter.py`,
`pass4_zon_bridge.py`, `pass5_game_bridge.py`, `pipeline_runner.py`,
`zw_world_rules_compiler.py` (the only files referencing
`world_rules`/`is_known` at all — no test/fixture/comment-only hits).
Found the exact token:

```json
"Tran": {
  "canonical_name": "Tran",
  "entity_type": "character",
  "cardinality": "individual",
  "spawnable": true,
  "render_as": "physical_actor",
  "zw_tags": ["chapter_102", "mars_convergence", "resilience"]
}
```

in `/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn/tier1/engainos/assets/world_rules.json`
— **a real, registered, spawnable character, tagged to chapter 102
("mars_convergence"), a completely different, much later part of the
novel with no relation to book 1.** This is not inactive material — the
run logs from this session confirm `world_rules.json` is loaded fresh
on every single chapter/scene pass (`[world_rules] loaded 36 entities
from .../world_rules.json`), so this registry is live and reachable by
the current pipeline for every chapter, not a stale fixture.

## 4. Earliest artifact where "Tran" appears — checked stage by stage, not assumed

Checked every intermediate file for chapter 1, scene 1, in pipeline
order:

```text
out_pass1_...scene001.txt              (raw scene text)     -- no Tran
out_pass1_spatial_...scene001.json     (spatial signals)     -- no Tran
out_pass2_...scene001.metta            (ENTITY CANDIDATES)   -- no Tran
  Real candidates: Aeon, Ethereal, Keepers, Korath, Lyaris,
                   Pelagor, Tiamat, Vaelith  (8 total)
zonj_scene001.json                     (pass3 canonical)     -- @entities: null
scene001.zon / scene001.zonj.json      (PASS 4 OUTPUT)       -- Tran FIRST APPEARS HERE
  @entities: [Mordain, Pelagor, Syreth, Theron, Tran, Vaelith]
```

**Pass 2's own candidate extraction is correct and does not contain
"Tran" at all.** It also correctly identifies **Lyaris** as a known
candidate (`known: true, spawnable: false, mentions: 3`) — this
corrects my own prior finding in `e2a6964` that Lyaris was "missing
from every entity list examined." She is present at the pass2 stage;
she simply never survives into the `@entities` field, because (per
below) `@entities` is not derived from pass2's output at all.

Pass 3's own zonj file has `@entities: null` — empty, not yet populated.

**"Tran" is introduced entirely inside Pass 4**
(`tier3/mettaext/passroom/pass4_zon_bridge.py`, class `ZonBridge`,
method `extract_entities()`), which — because the upstream `@entities`
is empty — falls through to its own independent detection logic that
never consults pass2's candidate list at all.

## 5. Traced to the exact mechanism — confirmed, not assumed

`extract_entities()`'s "Narration scan" block, in full:

```python
# Narration scan: find canonical names that appear verbatim in text
if self.world_rules:
    all_text = " ".join(
        (s.get("text", "") or "") for s in segments
    ).lower()
    for key, entry in self._wr_entities().items():
        if not entry.get("spawnable", True):
            continue
        if entry.get("cardinality") in ("species", "collective", "abstract"):
            continue
        cn = entry.get("canonical_name", key)
        if cn.lower() in all_text:
            canonical.add(cn)
```

`if cn.lower() in all_text:` is a **plain Python substring containment
check** — not a word-boundary-respecting match (`\bTran\b` or
equivalent). Verified directly against the exact segment text this
function operates on for scene 1:

```python
segs = json.load(open(".../zonj_scene.book001.001_the_ethereal_vigil.scene001.json"))["segments"]
all_text = " ".join(s.get("text","") or "" for s in segs).lower()
"tran" in all_text  # -> True
re.findall(r"tran[a-z]*", all_text)  # -> ['transformed', 'transformation']
```

**Confirmed, not assumed: scene 1's own text contains "transformed" and
"transformation."** `"tran"` (world_rules' `canonical_name` for the
real character Tran, lowercased) is a substring of both, so the check
fires and adds "Tran" to the scene's entity set — regardless of the
fact that the actual character Tran, from a chapter-102 storyline, has
no connection to this scene whatsoever. My own initial case-sensitive
grep (`grep -c "Tran"`) missed this on the first pass because it didn't
match lowercase "transformed" — corrected here by re-checking
case-insensitively against the exact same text the function itself
uses.

## 6. Is a global known-character list being supplied to every chapter?

**Yes, and that part is working as designed** — `world_rules.json`
(36 entities) is deliberately a shared, global registry, loaded fresh
for every chapter (confirmed: identical "loaded 36 entities" log line
for chapters 1-4 this session, no caching between chapters). **The bug
is not that a global list gets applied globally — that's intentional.
The bug is that the per-entity match against each chapter's text is a
substring check instead of a word-boundary check.** Any of the other
35 registered entities with a name that happens to be a substring of a
common word would trigger the same failure mode; "Tran" is simply the
one that happened to collide with "trans-"-prefixed vocabulary that is
common across this book's prose (transformed, transformation,
transcended, etc.).

## 7. Cross-chapter/shared-state contamination — checked and ruled out

No mutable global state, cache, or module-level accumulator is
involved. `ZonBridge` is instantiated fresh per scene (confirmed:
`self.known_entities = set()`, `self.world_rules = {}` in `__init__`,
and `world_rules.json` is re-read from disk on each instantiation, not
cached across calls). The bug is fully deterministic and
scene-local: given the same scene text and the same `world_rules.json`,
it reproduces identically every time, with no dependency on processing
order, prior chapters, or run history. This rules out run-state/cache/
global-dict leakage as the mechanism, even though the effect (the same
false entity appearing in unrelated chapters) superficially resembles
contamination.

## 8. Exact origin, classified as requested

```text
File:        tier3/mettaext/passroom/pass4_zon_bridge.py
Class:       ZonBridge
Method:      extract_entities()
Block:       "Narration scan: find canonical names that appear verbatim in text"
Mechanism:   substring-derived (cn.lower() in all_text), against a
             correctly-global, correctly-fresh-loaded registry
             (world_rules.json) -- NOT hardcoded, NOT seeded with a
             per-chapter default, NOT leaked from shared/cross-run state.
```

## 9. The negative control — corrects my own earlier reporting

The requested check (does chapter 4 lack both `Tran` and
`transformed`-like words, which would strengthen the substring
explanation) surfaced an error in my own prior summary. Re-checked
directly: **chapter 4's source contains multiple `trans-` words**
(transcended, transformation, transformed, transforming, translation,
translate — six distinct forms) and **chapter 4's fresh ingestion did
in fact produce the "Tran" entity too**, in at least four of its
scenes — I simply had not reported chapter 4's entity list in the
prior baseline receipt (`dce6854`), and my summary to the user
described that omission as if it meant absence. It didn't. There is no
real negative control chapter in this four-chapter set — every chapter
that contains any `trans-`-prefixed word produces the false "Tran"
entity, which is exactly what the confirmed substring mechanism
predicts and requires no further explanation beyond what's already
found.

## Net

```text
Origin:        pass4_zon_bridge.py, ZonBridge.extract_entities(),
               narration-scan substring check
Nature:        substring-derived match against a legitimate, correctly-
               shared global registry (world_rules.json) -- not
               hardcoded, not seeded, not cross-run state leakage
Scope:         reproduces on every chapter containing any word starting
               with a registered entity's (lowercased) canonical name --
               "Tran" is the specific collision found here; there is no
               general guard against this class of false positive for
               any of the other 35 registered entities either
Corrected:     chapter 4 also exhibits this bug; my earlier report's
               silence on chapter 4 was an omission, not a finding
Bonus finding: pass2's own candidate extraction is correct (includes
               Lyaris, correctly classified) but is never consulted by
               pass4's @entities derivation when pass3's own @entities
               is empty -- two independent, disconnected entity-
               extraction paths exist in this pipeline, and the one
               that actually reaches the final evidence is the buggier
               of the two
```

## What was not done

No fix applied to `pass4_zon_bridge.py` or anywhere else. Nothing
ingested or rebuilt. This is a read-only trace, exactly as requested.
