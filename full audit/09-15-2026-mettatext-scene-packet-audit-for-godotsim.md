# Mettaext → GodotSim scene-packet audit: no existing artifact is a clean match

Answers the question posed directly: "Which existing artifact most
closely represents: Scene 1 contains a town, three buildings and a
farm?" Audits Pass C's scene packet, the final Pass 4 `.zonj.json`,
and the Pass 5 `game_scenes/*.json` against real, rich settlement
content — nothing invented, nothing proposed to build. Verdict up
front: **none of the three cleanly represents it.** The gap is real,
specific, and traceable to three distinct extraction limits, not one.

## Test material

Found by searching the vault (restricted, as before, to `book*`-prefixed
folders only) for literal architectural language rather than
metaphorical "building." `book_08_the_vigil_of_the_anchor/047_mika.md`
(17KB) contains "ACT 2: THE FALCON RIDGE FOUNDING" — a settlement
founded, grown, and described in concrete physical terms across three
in-story years: a hut, a barracks, irrigated fields, a storage cache, a
perimeter wall, and "the archive... a solid stone building with a
vaulted ceiling." (Notable, unprompted: the settlement is even named
**Falcon Ridge** — the same name used as a hypothetical example in "the
door.md" months ago, and now sitting in real source material.)

Ingested for real via `engain_door.py ingest`
(`chapter_id: chapter.book008.047_mika`, 4 scenes). Used `engain_door.py
query` to locate the founding content precisely: **scene002**
(`@boundary_start_line: 56` – `131` of the original chapter).

## Pass C — the scene packet (chapterroom level)

`output/chapterroom/scene_packets/chapter.book008.047_mika/scene.book008.047_mika.scene002.txt`

A `@key:value` header block, then the **verbatim original prose**,
unmodified, unsegmented beyond scene boundaries. No interpretation at
all — this is pure witness text, one step removed from the source
file. Confirmed identical in kind to the toy-chapter audit's earlier
finding about `out_pass1_*.txt`; Pass C is upstream of even that.

**Not a candidate.** It was never meant to be — Mettaext's own doctrine
already says Pass C provides scene packets for passroom to compile, not
a structured product in its own right.

## Final Pass 4 `.zonj.json` — adds people, nothing else

`output/passroom/scene.book008.047_mika.scene002/scene.book008.047_mika.scene002.zonj.json`

- `=segments`: the same prose, now line-numbered JSON objects
  (`{"line": 90, "type": "narration", "text": "The first structure was
  a simple hut of stone and timber—Geralt and Mika's."}`,
  `{"line": 104, ..., "text": "A low perimeter wall began to snake
  around the valley's most accessible approaches."}`,
  `{"line": 124, ..., "text": "The archive was Mika's pride—a solid
  stone building with a vaulted ceiling..."}`). Real content, but
  **exactly as unstructured as Pass C** — a reader (human or GodotSim)
  still has to read full sentences and infer "there is a hut here" for
  itself. No semantic lift over the raw witness text for structures or
  places.
- `@entities` / `=entities_observed`: `["Geralt", "Mika", "Oreck",
  "Zephyr"]` (plus a false positive, "Month," from "Month 1/2/3" section
  headers misread as a proper noun). **Zero structures, zero places.**
  Confirms, on real content, what the toy-chapter audit already
  suspected: Mettaext's entity pipeline has no concept of "building" or
  "place" as an entity type — it is a **character-name extractor**,
  full stop. "Falcon Ridge," "the archive," "the perimeter wall," "the
  barracks" never appear in this field, despite being named or
  described explicitly and repeatedly in the same scene's own prose.
- `region: "Unknown"`, `terrain_family: "wasteland"`,
  `environment: "wasteland"`, confidence `0.49`. **Actively wrong.**
  The scene describes a lush, green, irrigated valley — "a clear
  stream," "a waterfall," "ancient, gnarled trees," "rich, dark soil,"
  "a bowl of life" — the opposite of wasteland. Traced to its own
  `environment_inference.evidence`: `["kw:desert", "kw:scrap", ...]` —
  "desert" comes from a *metaphorical* description of the wider
  surrounding landscape ("carved into the stone desert"), and "scrap"
  comes from "a **scrap** of fabric," a piece of cloth, matched purely
  as a keyword with zero regard for its sentence's actual meaning. Same
  failure mode as the toy-chapter audit's hardcoded-Beach finding, but
  this time it's not a hardcoded default — it's the content-based
  keyword voter itself producing a confidently wrong answer.

**Not a match.** It adds a (people-only, occasionally noisy) entity
index and a demonstrably unreliable environment guess. The actual
"what exists" content is still sitting in unstructured prose.

## Pass 5 `game_scenes/*.json` — attempts the most, delivers the least reliably

`output/passroom/scene.book008.047_mika.scene002/game_scenes/scene.book008.047_mika.scene002.json`

This is the artifact structurally closest in *intent* to "Scene 1: a
town, three buildings, a farm" — it has a `locations` array, a
`level_design` block (`landmarks`, `boundaries`, `hazards`,
`points_of_interest`), and a `layout_proof`. On this real scene, every
one of them fails:

- `locations`: `[{"id": "unknown", "name": "Unknown", "description":
  "Location: Realm/Physical/Unknown", ...}]` — one generic stub,
  inherited straight from the broken `region:"Unknown"` above it. Not
  "Falcon Ridge," not "the valley," not "the archive."
- `level_design.landmarks`: `["They reached the plateau"]` — a raw
  sentence fragment, not "hut," "barracks," "perimeter wall," or
  "archive."
- `level_design.boundaries`: two **truncated mid-word substrings** —
  `"d stone between two ridges—but both Geralt and Mika sto"` and
  `"ed from the eastern cliff."` — not usable data by any measure.
- `level_design.hazards`: `["I collapsed right here.\""]` — a quoted
  line of dialogue, misclassified as a hazard.
- `layout_proof`: **0 of 12** detected spatial relations were
  successfully consumed (`consumed_relation_count: 0,
  unresolved_relation_count: 12`) — every single one fell back to
  `"reason": "subject_not_resolved"`. All 4 characters were placed by
  `fallback_linear` (evenly spaced along a line, `x = 0, 5, 10, 15`,
  `y = z = 0` for all) — not derived from the text at all, a pure
  placeholder arrangement.
- `entities`: same 4 characters as the `.zonj.json`, with synthetic
  positions and `health: 100.0` fields that have no source in a scene
  containing no combat.

Traced the failure further, into `out_pass1_spatial_*.json` (Pass 1
Spatial's own raw signal list, the input `layout_proof` tried and
failed to consume): 15 signals, all triggered by **prepositions**
(between/above/behind/below/in_front_of). The scene's actual structural
sentences — *"The first structure was a simple hut..."*, *"A low
perimeter wall began to snake..."*, *"The archive was... a solid stone
building..."* — are all plain declarative **"X was a Y"** sentences
with no spatial preposition in them at all, so the signal extractor
never even attempts them. It isn't that these relations were detected
and failed to resolve — they were never detected in the first place.
Confirms the `subject_hint`/`object_hint` quality problem the earlier
toy-chapter audit already flagged ("stone"/"both geralt",
"space"/"suddenly charged" — grammatical neighbors, not real nouns) on
real, higher-stakes content, and adds a new, more specific finding:
**the extractor's trigger set (prepositions) structurally cannot see
declarative "there is a building" sentences**, which is exactly the
sentence shape authors actually use to describe architecture.

**Closest in intent, but currently unusable as a handoff.** A GodotSim
consuming this file today would receive one "Unknown" location, three
garbage `level_design` lists, and four characters standing in a
straight line — nothing resembling "town, three buildings, a farm."

## Verdict

None of the three artifacts is today's answer to "Scene 1 contains a
town, three buildings and a farm." Ranked by how close they get:

1. **`=segments` in the final `.zonj.json`** (or equivalently, Pass
   C's raw text) — the *only* place all the real structural content
   survives at all, but entirely as unstructured prose a downstream
   system would have to re-read and re-interpret itself, gaining
   nothing over reading the book directly.
2. **`game_scenes/*.json`** — the right *shape* (locations,
   level_design, layout_proof all exist as fields), but on real content
   every one of those fields is either an empty stub or extraction
   noise. The intent is correct; the extraction underneath it isn't
   there yet.
3. **`@entities`** — actively unhelpful for this question; it's a
   people-only index and will never contain "Falcon Ridge" or "the
   archive," structurally, not as a bug to patch but as what the field
   currently *is*.

## Root cause, three distinct gaps (not one)

1. **No place/structure entity type.** Character extraction exists;
   structure/place extraction does not. "Falcon Ridge," "the archive,"
   "the barracks" are never candidates for anything, the way "Igigi" at
   least was a candidate *character* even before it was known to
   `world_rules.json`.
2. **Landmark/boundary/hazard extraction produces sentence fragments,
   not entities** — confirmed on two independent real chapters now
   (the toy-chapter audit's "of the stone gate" / "front of the stone
   gate", and this scene's truncated mid-word substrings).
3. **Spatial-relation detection is preposition-triggered only** and
   structurally misses the declarative "X was a Y" sentence shape that
   architectural description actually uses in this corpus. This is new
   to this audit — not previously observed, because no prior real
   chapter tested here described actual buildings.

## Implication, stated plainly and no further than the question asked

If GodotSim (or whatever comes next) needs "what exists in this
scene," there is currently no Mettaext artifact that hands it that
cleanly. The honest starting point for that system, today, is the same
raw narration sentences the door's own raw-text query lane already
reads — not a further-upstream structured product, because that
product doesn't exist yet. This is not a recommendation to build
anything; it's the answer the audit was asked to produce.
