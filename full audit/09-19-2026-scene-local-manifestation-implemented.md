# Scene-local manifestation implemented per the approved plan — plus an unrelated source-drift discovery found during live validation

Implements the 10-step plan approved after `405d1b7`'s correction.
Committed to `EngAIn`. All unit/regression tests pass. A live full-
pipeline rerun surfaced a genuine, unrelated discovery about the
current vault content that limits what this rerun could demonstrate —
reported here in full rather than glossed over.

## What was implemented, exactly per plan

**`tier3/mettaext/passroom/pass2_enhanced.py`**
- `Character` gains `presence`, `presence_confidence`, `physicality`,
  `physicality_confidence` — four new optional fields, `known`/
  `spawnable`/`classification` untouched.
- `infer_presence_enhanced(segments, characters)`: priority 1, an
  authored `participants:` scene-meta line (highest confidence, 1.0);
  priority 2, prose evidence naming the entity as the *object* of
  remote detection (`resonance of X essence`, `X's energy/life
  signature`, `signature of X`, `detected X`, `sensed X` — deliberately
  object-position patterns, so "Lyaris sensed something" never
  misclassifies Lyaris as remote); priority 3, `unknown` — fail closed,
  never inventing locality.
- `infer_physicality_enhanced(segments, characters)`: only evaluated
  when `presence == "local"`; keyword evidence for physical
  (body-formation/action verbs) vs. nonphysical (consciousness/
  awareness/ethereal framing); `unknown` when neither or when not
  local. On conflicting evidence, concrete physical evidence outranks
  a generic consciousness mention (a physically embodied character can
  still "sense" something without that undoing embodiment).
- Both wired into `main()`, after entity filtering and before
  `write_metta()`; the `.metta` entity atom now always carries all four
  new fields.

**`tier3/mettaext/passroom/pass3_merge.py`**
- `_handle_entity()` parses the four new tokens, left as `None` (not
  defaulted) when absent — this is what lets an old `.metta` file
  predating this feature be told apart from one that computed
  manifestation and got `"unknown"`.
- `merge_to_zonj()`: `@entities_manifested` is written whenever any
  entity in the scene carries manifestation data at all (even if the
  resulting list is empty) — the opposite convention from `@entities`'s
  own omit-if-empty rule, because an empty manifested list is a real,
  confirmed answer, not a "not computed yet" gap. Membership rule:
  `spawnable AND presence == "local" AND physicality == "physical"`.

**`tier3/mettaext/passroom/pass4_zon_bridge.py`**
- Pure passthrough of `@entities_manifested` in both `convert_to_zonj()`
  branches, keyed on presence (`"@entities_manifested" in scene`), not
  truthiness — no re-derivation, no second classifier, per the plan's
  "transport/normalization, not a second manifestation classifier."
  The word-boundary narration fallback from the earlier handoff fix is
  untouched.

**`tier2/godotsim/bridge_integration.py`**
- `bridge_entities_for_scene()`'s entity-source selection now prefers
  `@entities_manifested`/`entities_manifested` when the key is present
  — even empty — falling back to today's `entities`/`@entities`
  behavior only when the key is entirely absent. Confirmed (by reading
  `declared_entity_ids()`/`filter_bridge_entities_by_declared_ids()`
  again) that no further change is needed there: that filter only ever
  *removes* entities not in the union of `entities`/`@entities`/
  `spawn_commands`, never adds any back, and `@entities_manifested` is
  by construction always a subset of `@entities` — so it cannot
  reintroduce an excluded entity.
- Noted, not acted on: `bridge_integration.py` already uses the word
  `presence` for a different, existing per-entity-instance runtime
  concept (`result["presence"] = ent.get("presence", "visible")`,
  forwarded game-mechanics visibility state). No actual data collision
  — `@entities_manifested` is a bare name-string list, never an
  enriched dict, so it never reaches that line — but the name overlap
  is worth knowing about if this code is touched again.

## Tests

New: `tier3/mettaext/tests/test_scene_local_manifestation.py` (15
tests) and `tier2/godotsim/test_bridge_entities_manifestation.py` (4
tests), covering every case in the plan's step 9 using fixtures built
directly from the real evidence found earlier this session:

```text
Vaelith  -- local, nonphysical, NOT in @entities_manifested
Pelagor  -- remote, physicality forced unknown, NOT manifested
Senareth -- local, physical, IN @entities_manifested (positive control)
Giants   -- local, physical, but spawnable:false -- excluded from
            @entities_manifested for a DIFFERENT reason than
            Vaelith/Pelagor (orthogonality proof)
Vairis   -- no participants/remote evidence -- fails closed to
            unknown, stays in @entities, excluded from manifested
```

Updated: `test_pass3_pass4_entity_handoff.py`'s
`test_entities_observed_unchanged_by_this_fix` — the key-set pin now
includes the four new keys, as flagged as a required update in
`82b061b` before this was implemented.

```text
tier3/mettaext/tests/:  56 passed (41 pre-existing/from bcdad29 + 15 new)
tier2/godotsim/:         4 passed (new file, no prior test infra existed here)
```

## Live validation: what worked, and a genuine discovery about what didn't

Reran the full pipeline (`pipeline_runner.py`) against all four Book 1
chapter files under `tier1/mrlore/raw/chapters/`. All four completed
with no errors.

**Confirmed working, on real fresh chapter-1/2 text:**
- Pelagor: `presence: "remote"` — the resonance/essence/signature
  detection still fired correctly on real prose.
- `@entities_manifested` correctly written as an empty list (present,
  not absent) wherever no local-physical entity qualified.
- Fail-closed `"unknown"` correctly applied wherever no participants
  line or remote evidence existed — no invented locality anywhere.

**Could not reproduce on this rerun, for a reason unrelated to the
code**: Vaelith ending up `presence: "local"`, and Senareth reaching
`@entities_manifested`. Investigated why — this is the discovery:

The actual current content of `tier1/mrlore/raw/chapters/
book_01_book_of_genesis_001_the_ethereal_vigil.md` (and chapter 2's
equivalent) does **not** contain a `participants:` scene-meta line at
all. Its real header is a completely different, simpler format:

```text
BOOK: 01_garden_genisis
CHAPTER: 001_the_ethereal_vigil
THREADS INCLUDED: Pelagor Evolution, Nephoretti Manifestation, ...
ARC: Aaon Keepers
REGION: Akashic Library, Ethereal Realm
TIME PERIOD: Post-Shattering, 3,417 Years After Marduk-Tiamat Collision
POV / FOCUS: Aaon Keepers
STATUS: Complete:
```

No `day N`/`scene N.M`/`scene meta:`/`participants:`/`focus:`/
`continuity:` block anywhere in it. This is a genuinely different, far
less structured format than the one actually present in the
`scene.book001.001_the_ethereal_vigil.scene001.zonj.json` artifact this
whole design was grounded on and quoted directly in `405d1b7` — that
artifact's `participants: Lyaris, Theron, Vaelith, Mordain, Syreth,
Korath` line is real, not fabricated.

Checked precisely, rather than left as speculation:

- `git diff HEAD -- tier1/mrlore/raw/chapters/book_01_book_of_genesis_001_the_ethereal_vigil.md`
  is empty — the raw chapter file on disk is byte-identical to its last
  commit (`c0b6bc6`, 2026-06-24). **It has not been edited during this
  session, or since.** The sparse format is not drift; it is this raw
  file's genuine, long-standing content.
- `grep -rl "^participants:" --include="*.md" .` (repo-wide, excluding
  the legacy corpus) returns **zero files**. No `.md` source anywhere
  in this repo currently contains a `participants:` line in any format.
- The one other candidate location that looked promising (`out of
  root/scratch/mettaext_speaker_test/multi_chapter/...`) produces the
  same sparse, no-participants structure as the raw chapter file when
  inspected directly — ruled out.

Conclusion, stated as confirmed rather than guessed: the rich
`scene.book001.*` artifact was not produced by feeding this raw
chapter `.md` file to `pipeline_runner.py` the way today's live
validation just did. Its own header says
`"@contract": "engain.scene_text_packet.v1"` — a distinct, richer
input *format* (day/scene/participants/focus/continuity), not just a
richer chapter file. Whatever step actually produces a
`scene_text_packet` from the raw chapter (an enrichment/compilation
stage the earlier session's authorized `engain_door.py ingest` work
apparently went through) was not invoked by today's direct
`pipeline_runner.py <raw.md>` call, and its location was not found
during this session. This is the same category of finding as `772b26b`
(stale/divergent source copies) and `3d317a5`/`3f58af9` (multiple
corpora, different schemas) earlier this session — a real, now-verified
environment fact about there being (at least) two distinct valid input
formats into this pipeline, not a defect in today's code — and
explicitly not chased further here, since locating the
`scene_text_packet` compilation step is its own investigation, not
part of the approved manifestation patch.

**What this means, concretely**: on today's actual on-disk chapter 1/2
content, the presence axis's `participants:`-based "local" path will
essentially never fire, and everything will fail closed to `unknown` —
which is safe and correct behavior, but means `@entities_manifested`
will currently come out empty for most scenes rather than usefully
distinguishing local-physical entities, until either the richer source
format is located/restored, or a second local-presence evidence source
(e.g., dialogue-speaker-attribution proximity, which reliably implies
co-presence in most prose) is added as a second priority tier below
the participants line. Not done here — an open decision, not scope
creep on this patch.

The unit tests are unaffected by this and remain the authoritative
proof the logic itself is correct: they use fixtures built directly
from the real evidence patterns this session already captured and
verified (the actual `participants:` line and prose from the artifact
quoted above), independent of whatever the raw chapter file's current
on-disk content happens to be.

## What stayed exactly as scoped

- `world_rules.json` / `spawnable` — untouched.
- `@entities` — untouched in meaning; still the spawnable-safe
  projection from `bcdad29`.
- `entities_observed` — additive only; `known`/`spawnable`/
  `classification`/`mentions` unchanged.
- Scene segmentation, provenance-as-narration contamination, and the
  missing `semantic_environment_extractor` module — not touched.
- Director/adaptation override — not represented anywhere in
  `tier3/mettaext`; still entirely a runtime-layer concern.

## Net

```text
Presence/physicality inference (Pass 2):       implemented, tested
entities_observed carries both (Pass 3):       implemented, tested
@entities_manifested derivation (Pass 3):      implemented, tested
Pass 4 passthrough:                            implemented, tested
GodotSim preference-with-fallback:             implemented, tested
Director override:                             confirmed still outside Mettaext
Live pipeline rerun:                           succeeded, no errors, 4/4 chapters
Live positive-control reproduction:            blocked by unrelated source-content
                                                drift, not a code defect -- flagged,
                                                not resolved
```
