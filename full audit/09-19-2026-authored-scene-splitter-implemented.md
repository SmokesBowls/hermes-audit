# Authored-scene splitter implemented — Book 1 acceptance met, manifestation confirmed working end-to-end for real

Implements the corrected design from `d96cea7`
(no `day N` special rule; `time:` opaque). Committed to `EngAIn` as
`d138fc8`. Chapters 005+ were not processed or modified.

## What changed

**`tier3/mettaext/chapterroom/passB_scene_boundary_provider.py`** — new
`split_by_authored_scene_markers()`, checked first, ahead of all four
existing methods. `scene NNN.x — <title>` (space-em-dash-space,
distinct from the chapter title line's bare hyphen) starts exactly one
scene running to the next marker or end of chapter. Its immediately
following `scene meta:` block is parsed generically — any `key: value`
line, no hardcoded key list — into a `scene_meta` dict, additive to the
existing raw text (never replacing it, so Pass 2 keeps finding
`participants:` by scanning segment text directly). `choose_boundaries()`
sets `authority_state: "SCENE_BOUNDARY_AUTHORED"` and
`authored_scene_boundaries_proven: true` only for scenes produced this
way; the existing fallback chain is untouched. Per the corrected design,
there is **no `day N` handling of any kind** — those lines get no
recognition and just fall wherever plain marker-to-marker chunking
puts them.

**`tier3/mettaext/chapterroom/passC_scene_packet_writer.py`** — carries
`scene_meta` into the actual `.txt` packet (as generic
`@scene_meta_<key>: value` header lines — e.g. `@scene_meta_cutscene_purpose`
for `cutscene purpose`) and into each packet's index entry. This was a
necessary addition beyond Pass B alone: Pass B's own JSON output isn't
what Pass 1 reads — Pass C's `.txt` packet is — so without this change
the parsed metadata would have been computed and then silently dropped
at the Pass B → Pass C boundary.

## Tests

13 new tests in `test_authored_scene_boundary_splitter.py`:

```text
Marker/meta parser unit tests: generic-key capture (presentation,
  cutscene purpose -- absent from Book 1), opaque time: preservation
  (including compound "year N (X years after...)" annotations),
  chapter-title-hyphen vs marker-dash disambiguation, day-N-line
  harmlessness (present but never specially recognized), multi-marker
  chunking, no-markers-returns-empty.

choose_boundaries() integration: authored path sets state/proven
  correctly; no-markers path is byte-for-byte the same fallback
  behavior as before this change (regression pin).

Pass C passthrough: scene_meta reaches both the packet file's header
  lines and the index entry.

Real-vault acceptance (skipped gracefully if the vault path isn't
  present in a given environment):
    Book 1 chapters 1-4 -> exactly 1, 1, 7, 1 authored scenes.
    Chapter 2's parsed participants matches the real text verbatim.
    End-to-end through Pass 1/2: Vaelith -> local/nonphysical,
    Pelagor -> remote/unknown -- fc3e3d1's manifestation regression
    cases, now proven through the corrected splitter, not just
    through synthetic fixtures.
```

Full `tier3/mettaext` suite: **69 passed** (56 previous + 13 new).

## Live validation: real pipeline, real vault, chapters 1-4 only

Reran `pipeline_runner.py` against
`/home/mytruelove/Downloads/obsidianburdenNov25/book_01_book_of_genesis/00{1,2,3,4}_*.md`
— the real, canonical vault Dragon's own live request resolved
yesterday (`4d1b622`) — and only those four files.

```text
Chapter 1: SCENE_COUNT = 1, BOUNDARY_METHOD = authored_scene_marker
Chapter 2: SCENE_COUNT = 1, BOUNDARY_METHOD = authored_scene_marker
Chapter 3: SCENE_COUNT = 7, BOUNDARY_METHOD = authored_scene_marker
Chapter 4: SCENE_COUNT = 1, BOUNDARY_METHOD = authored_scene_marker
```

Exact acceptance criteria met.

**This also resolves the gap flagged in `a5c75a7`.** That session's live
rerun used the wrong source (`tier1/mrlore/raw/chapters/`, which never
had a `participants:` line), so the manifestation feature's positive
control (Vaelith local) couldn't be demonstrated end-to-end at the time
— only via synthetic fixtures. Rerunning against the real vault with
the new splitter, chapter 1's fresh output now shows, for real:

```json
"@entities": ["Mordain", "Pelagor", "Syreth", "Theron", "Vaelith"],
"@entities_manifested": [],
"=entities_observed": [
  {"name": "Vaelith", "known": true, "spawnable": true,
   "presence": "local", "presence_confidence": 1.0,
   "physicality": "nonphysical", "physicality_confidence": 0.85},
  {"name": "Pelagor", "known": true, "spawnable": true,
   "presence": "remote", "presence_confidence": 0.85,
   "physicality": "unknown", "physicality_confidence": 0.0}
]
```

`@entities_manifested` present and empty, exactly as designed. The
`@scene_meta_*` header lines confirmed flowing through into the final
zonj's segments as plain narration text, alongside the structured dict
captured earlier in the pipeline.

## What was deliberately not done

`scene_meta` is not propagated any further than Pass C's packet (header
lines + index entry). It was not added as a new structured field on
Pass 3/4's ZONJ output — that would be a separate scope decision (akin
to `entities_observed`/`@entities`/`@entities_manifested`) that wasn't
asked for here; the instruction was to preserve it "in the scene
packet," which this does. Chapters 005+ were not read, processed, or
modified. `tools/passB_fix/passB_day_boundary_runner.py` (a separate,
one-off repair tool for an unrelated italic/bold `*Day N*` markdown
convention in other books) was not touched.

## Net

```text
Authored scene-marker splitter:        implemented, tested
Generic scene_meta parsing:            implemented, tested (no hardcoded keys)
time: opacity / no day N rule:         implemented per corrected design
Pass C metadata passthrough:           implemented, tested
Book 1 acceptance (1/1/7/1):           met, live-verified against real vault
Manifestation still works post-change: confirmed, live, real text
Chapters 005+:                         untouched
```
