# Assembly stage: `[EDITOR_REQUEST]` + asset table → candidate `.osp` (design v1, spec only, no code)

The last undesigned link in the chain from `09-17-2026-dragon-to-osp-
scene-build-design-v1.md`. Traced against the same real
`[EDITOR_REQUEST]` frozen in `09-17-2026-editor-request-contract-v1.md`
(Falcon Ridge, `chapter.book008.047_mika` scene002). Nothing implemented.

## 0. This isn't new invention — it finishes a wiring ob-scene-workspace already scoped

Read `ob-scene-workspace/manifests/kenney-mini-arena-capability-
manifest.v0.1.yaml` (not read before this design pass) to check this
design against the original authors' own intent before locking anything.
It independently names, back in July, exactly the two components this
design reuses: **`Topologist: candidate_for placement and spatial
relationships`**, **`Cartographer: candidate_for dimensions, units, and
scene metrics`** — both listed under `ownership_summary.prospective`,
never wired in. `ownership_summary.unresolved` separately lists
`"exact asset-resolver boundary"` as a named, acknowledged gap. This
design closes both: it's finishing a connection the original workspace
already identified as needed, not proposing a new architecture.

One correction this manifest forces: `CAP-PHYSICS-001` records the
donor scene's floor as Godot's `CSGBox3D`, but OSP's own doctrine
(`contracts/osp-v0.1/README.md`) explicitly forbids that as canonical
vocabulary — the real `osp_loader.gd` already normalizes this correctly
to `primitive: box` realized as `BoxMesh` + `MeshInstance3D`. This
design follows the loader's real behavior, not the donor manifest's
raw observation.

## 1. Pipeline, existing components unmodified, two new steps only

```text
[EDITOR_REQUEST]
     ↓
STEP A (new): asset resolution
     structures[] × asset table → resolved instances + unmapped_concepts[]
     ↓
STEP B (new): relation eligibility filter
     spatial_relations[] → eligible (structure↔structure, both resolved)
                          → deferred (structure↔terrain_feature, or
                            either endpoint unmapped) — reported, not guessed
     ↓
STEP C (existing, reused unmodified): Topologist
     eligible relations → convert_spatial_signals_to_artifact-equivalent
     → TopologyValidator → gate_accept_proposed_topology_artifact.py
     → accepted_spatial_truth_packet
     ↓
STEP D (existing, reused unmodified): Cartographer
     accepted packet + per-instance envelope (from asset table)
     → topology_metric_layout_solver.py → real x/y/z positions
     ↓
STEP E (new): OSP assembly
     resolved instances + positions + fixed default scaffold
     (floor/camera/light/environment) → candidate .osp
     ↓
STEP F (existing, reused unmodified): gates/validate_osp_v0_1.py
     candidate .osp → validated .osp (or rejected, with reasons)
```

## 2. Step A — asset table format (fields only; contents mostly TBD)

```json
{
  "match_key": "dwelling",
  "resource_id": "asset.<placeholder>",
  "kind": "model",
  "uri": "fixture://<placeholder>",
  "material_binding_id": "material.colormap",
  "envelope": { "h": null, "w": null, "d": null }
}
```

Matched only against `structures[].role`, exact string match — no
fuzzy/semantic matching at this stage. A structure with no `role`, or a
`role` with no table entry, is `unmapped_concepts`, reported by
`structure_id` and `description`, never guessed toward the nearest
available asset. Same doctrine as `worldfield`'s `TERRAIN_TO_RECIPE`.

**Real, named gap**: the only 5 proven assets (banner/column/tree/
bricks/statue) have no verified `envelope` (h/w/d) dimensions anywhere
in this session's evidence — the capability manifest records positions
and rotations for the donor scene's instances, never bounding-box size.
Cartographer's solver requires `pgt_envelope` per entity (verified in
`topology_metric_layout_solver.py`). Without real dimensions, Step D
cannot run correctly for any of these 5 assets today. Not fabricating
placeholder numbers here — flagged as the actual next blocker for a
non-empty run, separate from this design.

## 3. Step B — why terrain-touching relations can't reach Cartographer yet

Topologist's own entities (`TopologyEntity`) don't need an envelope —
`TopologyValidator` only checks referential integrity, not geometry — so
a relation like `struct.hut_geralt_mika near terrain.stream` *could* be
converted and validated as a topology artifact. But Cartographer's
metric solver needs an envelope for every entity in the accepted packet,
and terrain features have none — they're not discrete objects, they're
`tier2/worldfield`'s domain (elevation/grid, no bounding box). Passing a
terrain feature through with an invented placeholder envelope would be
exactly the kind of guess this whole pipeline is built to avoid.

**v1 rule**: only structure↔structure relations where both sides
resolved to a real asset (Step A) are eligible for Topologist/
Cartographer. Everything else — structure↔terrain_feature relations,
relations touching an unmapped structure — is `deferred`, named in the
assembly report with its reason, not silently dropped and not forced
through with invented geometry.

## 4. Step E — default scaffold (a door-owned choice, stated not hidden)

Every candidate `.osp` gets a fixed baseline scaffold — one root, one
generated floor primitive, one camera, one directional light, one
environment binding — mirroring the Kenney fixture's own baseline
(`CAP-SCENE-002`'s five direct children: WorldEnvironment, Floor, View/
Camera, Sun, Sample), so a scene is always inspectable in Godot even
when zero structures resolve. This is a deliberate default, not an
inferred requirement — flagged as a choice for confirmation, not slipped
in silently. Resolved `asset_instance` nodes (if any) go under a
`group.sample`-equivalent node, same pattern as the fixture.

## 5. Worked trace against the real Falcon Ridge `[EDITOR_REQUEST]`

Running the actual frozen request from `09-17-2026-editor-request-
contract-v1.md`:

**Step A** — all six `structures[]` entries: none carry a `role` value
matching any of the (currently near-empty) asset table's keys. Result:
`unmapped_concepts = [hut_geralt_mika, barracks, fields,
irrigation_ditches, storage_cache, perimeter_wall]` — 6 of 6.

**Step B** — of the five `spatial_relations[]` entries: `hut near
terrain.stream`, `irrigation_ditches within terrain.valley`,
`perimeter_wall within terrain.valley` are terrain-touching → deferred
under §3's rule regardless of asset resolution. `barracks near hut` and
`archive near central_fire` are structure↔structure in shape, but both
endpoints are already `unmapped_concepts` from Step A → also blocked,
reported as "relation dropped: endpoint unresolved." **0 of 5 relations
reach Topologist.**

**Steps C+D** — nothing to process; skipped, not run on empty input.

**Step E** — candidate `.osp` contains only the fixed default scaffold
(floor, camera, light, environment) — zero `asset_instance` nodes.

**Step F** — this candidate validates cleanly against `validate_osp_
v0_1.py`'s mechanical checks (it's structurally a legal, if empty,
package) — mechanical validity is not the same as narrative
completeness, exactly the distinction OSP's own README already draws.

**Reading this result**: the pipeline did its job correctly. Given
today's actual asset table (effectively empty) and today's actual
envelope data (none), a real scene about a hut, a barracks, an archive,
and a perimeter wall produces an honest, empty, inspectable stage — not
a fabricated approximation. Every one of the 6 structures and 5
relations is individually accounted for in the assembly report with a
specific, named reason. That's the fail-closed behavior this whole
project's doctrine has demanded everywhere else today; this is not a
different outcome, it's the same discipline reaching its first
end-to-end real trace.

## 6. Non-negotiable rules

- Deterministic throughout. No LLM call anywhere in Steps A–F — Dragon's
  reasoning already happened, upstream, in producing `[EDITOR_REQUEST]`.
- Every dropped/deferred/unmapped item is named with a reason in the
  assembly report. Silence is not an allowed outcome for anything in the
  input.
- No invented envelope dimensions, no invented asset substitutions, no
  invented terrain placement.
- Reuses `TopologyValidator`, `gate_accept_proposed_topology_artifact.py`,
  `topology_metric_layout_solver.py`, and `gates/validate_osp_v0_1.py`
  exactly as they exist today — no modification proposed to any of them.
- Does not touch canon, MrLore's identity authority, AP, or runtime —
  same stop line as every other design this session.

## 7. Open items, not resolved here

1. Real envelope (h/w/d) dimensions for the 5 proven Kenney assets —
   blocks Cartographer for any non-empty future run.
2. Rotation for placed instances: Cartographer's solver produces
   position only (verified in `topology_metric_layout_solver.py`); no
   orientation logic exists anywhere in this chain yet. Needs its own
   decision before a placed instance can face a sensible direction.
3. The asset table itself is still schema-only — populating it beyond
   the 5 Kenney entries (or beyond `role: "dwelling"` even for those) is
   separate, substantial work, not attempted here.
4. Whether `struct.fields` and `struct.irrigation_ditches` belong in
   `structures[]` at all (flagged already in the contract doc, §7) bears
   directly on this design too — if reclassified as terrain, they'd
   route to worldfield instead of ever reaching asset resolution.

## Status

Pipeline and both new steps designed, traced against real content end
to end, zero fields invented. No code written. The chain from raw scene
text to a validated (if currently empty) `.osp` is now fully specified,
door to door — what was missing at the start of today's conversation.
