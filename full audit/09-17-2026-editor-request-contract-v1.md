# `[EDITOR_REQUEST]` v1 — frozen schema (spec only, not implemented)

Freezes the exact shape of the one new artifact identified in
`09-17-2026-dragon-to-osp-scene-build-design-v1.md`: what Dragon emits
after reading a scene, before anything deterministic (Topologist,
Cartographer, asset resolution) touches it. Grounded against a real
scene, same discipline as both door contracts: `chapter.book008.047_mika`
scene002 (Falcon Ridge founding, months 1–3 — `ACT 3: EARLY DAYS`,
`out_pass1_scene.book008.047_mika.scene002.txt`, lines 86–117), the same
scene the Mettaext scene-packet audit used. Nothing below is invented
without a line in that real text backing it.

## 0. Non-negotiable rules (recap from the design doc)

- `[EDITOR_REQUEST]` is Dragon's read of the text. It is never treated
  as accepted canon, never an `.osp`, never carries a real transform or
  a real `resource_id`.
- `authority` is always `proposal_only`. No confidence score beyond a
  bare `grounded` flag (does this claim trace to source text or not) —
  no invented numeric certainty, matching every other proposal-stage
  artifact found this session (Mettaext's `known:false/spawnable:false`,
  Ob-Scene's `confidence_basis_points = 0`).
- Every entity and relation carries `source_lines` back to the exact
  `out_pass1_<scene_id>.txt` this request was read from. No claim
  without a line citation — same rule the Mettaext door already enforces
  on its own hits.
- **Structures and terrain are kept in separate arrays**, not one
  undifferentiated `entities` list. They resolve through different
  downstream pipelines: structures become OSP `asset_instance` nodes
  (need a `resource_id`); terrain features (valley, stream, ridges,
  cliffs) are `tier2/worldfield`'s domain (elevation/terrain painting,
  not discrete asset placement). Conflating them would send terrain
  descriptions into the asset-resolution table where they can only ever
  come back `unmapped`.
- Dragon does not resolve its own asset IDs or coordinates. It names
  what it read and how those things relate; resolution is deterministic
  and happens after this document, per the design doc's flow.

## 1. Top-level shape

```json
{
  "editor_request_version": "0.1",
  "request_id": "req.book008.047_mika.scene002.0001",
  "source": {
    "scene_id": "scene.book008.047_mika.scene002",
    "chapter_id": "chapter.book008.047_mika",
    "artifact": "output/passroom/scene.book008.047_mika.scene002/out_pass1_scene.book008.047_mika.scene002.txt"
  },
  "generated_by": "dragon",
  "authority": "proposal_only",
  "structures": [ /* §2 */ ],
  "terrain_features": [ /* §3 */ ],
  "spatial_relations": [ /* §4 */ ],
  "unresolved_notes": [ /* §5 */ ]
}
```

`source.artifact` uses the exact stable, `stageroom_root`-relative path
convention the Mettaext door contract already locked (§4 of
`09-15-2026-engain-door-contract-v1.md`) — not repeated here, reused.

## 2. `structures[]` — discrete, placeable things

```json
{
  "structure_id": "struct.hut_geralt_mika",
  "kind": "structure",
  "description": "a simple hut of stone and timber",
  "role": "dwelling",
  "owner_note": "Geralt and Mika's",
  "source_lines": [90],
  "grounded": true
}
```

Real entries this scene actually supports (all with a direct source
line, nothing invented):

| `structure_id` | `description` | `source_lines` |
|---|---|---|
| `struct.hut_geralt_mika` | "a simple hut of stone and timber" | [90] |
| `struct.barracks` | "a long barracks for the soldiers" | [91] |
| `struct.fields` | first planted fields on the south-facing slope | [95, 97] |
| `struct.irrigation_ditches` | irrigation ditches channeled from the stream | [98] |
| `struct.storage_cache` | "dug into a cool hillside" | [99] |
| `struct.perimeter_wall` | "began to snake around the valley's most accessible approaches" | [104] |

`role` is a free-text hint for the asset-resolution table (§ below), not
a closed enum yet — v1 doesn't have enough real vocabulary across more
than one scene to freeze an enum responsibly.

## 3. `terrain_features[]` — not asset instances, worldfield's domain

```json
{
  "feature_id": "terrain.valley",
  "kind": "valley",
  "description": "hidden, perfectly sheltered by the surrounding ridges",
  "source_lines": [46, 48]
}
```

Real entries: `terrain.valley` [46,48], `terrain.stream` (cuts through
center, fed by a waterfall) [49], `terrain.waterfall` [49],
`terrain.eastern_cliff` [49], `terrain.ridges` [48], `terrain.plateau`
(the original meeting place, scene001-adjacent) [11]. These do not get a
`resource_id` in this design — they're named so a future worldfield/
Trixel bridge has something to consume, out of scope for this contract
to resolve.

## 4. `spatial_relations[]` — reusing Topologist's existing vocabulary, not a new one

```json
{
  "relation_id": "rel.0001",
  "subject": "struct.perimeter_wall",
  "relation": "within",
  "object": "terrain.valley",
  "source_lines": [104],
  "grounded": true
}
```

Relation values are drawn only from what `passroom_signal_converter.py`
already accepts (`_TO_OLINK`/`_TO_QSLINK`/`_TO_MOVELINK` keys:
`in_front_of, behind, beside, above, below, near, within, approach,
enter, retreat, withdraw`, plus `blocks_path`/`closed_boundary` from the
obstruction table) — not a second vocabulary Topologist would need to
learn. Real entries this scene supports:

| subject | relation | object | source_lines |
|---|---|---|---|
| `struct.hut_geralt_mika` | `near` | `terrain.stream` | [89, 90] |
| `struct.barracks` | `near` | `struct.hut_geralt_mika` | [90, 91] |
| `struct.irrigation_ditches` | `within` | `terrain.valley` | [98] |
| `struct.perimeter_wall` | `within` | `terrain.valley` | [104] |
| `struct.archive` | `near` | `struct.central_fire` | [124, 126] (Act 4, adjacent scene boundary — flagged, see §5) |

Several real spatial statements in this scene **cannot** honestly be
placed in this table yet: "a low perimeter wall began to snake around
the valley's most accessible approaches" (line 104) is a shape/path
description, not a point relation — Topologist's `_TO_QSLINK`/`_TO_OLINK`
tables have no representation for "traces a boundary along terrain,"
only point-to-point relations. That gap is named, not papered over, in
§5.

## 5. `unresolved_notes[]` — required, not optional

Anything Dragon read and judged narratively significant but that this
schema cannot honestly represent yet goes here, plainly, instead of
being forced into a relation it doesn't fit:

```json
{
  "note": "perimeter wall follows a path along the valley's accessible approaches, not a point relation to one object; Topologist's relation vocabulary has no path/boundary-following relation type",
  "source_lines": [104]
}
```

Real entries for this scene: the wall's path-following shape (above);
"a two-mile sightline" strategic/visibility fact (line 109) — not a
placement relation at all; the archive's boundary — it's described in
the scene immediately following (Act 4, line 124) rather than cleanly
inside this scene's own `boundary_start_line`/`boundary_end_line`
window (56–131 per this file's own header, though the text file's
content extends to line 145 — a real, observed inconsistency in the
source artifact itself, flagged here rather than silently resolved
either way).

## 6. What asset resolution actually returns against this scene, today

Stated plainly, not deferred: running this request's six `structures[]`
entries against the only real asset table proven in this pipeline
(Kenney Mini Arena — statue, tree, banner, column, bricks) returns:

```text
struct.hut_geralt_mika       -> unmapped
struct.barracks               -> unmapped
struct.fields                 -> unmapped (terrain-adjacent, arguably belongs in §3 not §2 — open question)
struct.irrigation_ditches     -> unmapped
struct.storage_cache          -> unmapped
struct.perimeter_wall         -> unmapped (also a path-shape gap, see §5)
```

Zero of six resolve. This is the honest result this design doc predicted
and it's confirmed here against real content, not asserted abstractly.
The schema and the flow are sound; the asset table is the actual near-
term blocker, exactly as stated in the design doc §4.

## 7. Open item surfaced while freezing this, not resolved here

`struct.fields` sits ambiguously between "placeable structure" and
"terrain feature" — a planted field is closer to a ground-texture change
(worldfield's domain) than a discrete object (OSP's domain). This
contract does not resolve that classification; flagged for the next
design pass rather than guessed at here.

## Status

Schema frozen at this document, validated against one real scene's real
text, zero fields invented without a source line. No code written. Next
step: the deterministic assembly step (`structures[]` + `spatial_
relations[]` + asset table → candidate `.osp`) — not designed yet.
