# Mettaext "number 7" re-verified: scene-object gap addressed, two gaps untouched

EngAIn commit `f58edff` ("mettaext number 7") landed after the
Mettaext→GodotSim scene-packet audit
(`09-15-2026-mettatext-scene-packet-audit-for-godotsim.md`). Re-ran
the exact same real chapter/scene the audit used
(`book_08_the_vigil_of_the_anchor/047_mika.md`, scene002 — the "Falcon
Ridge Founding" scene) against the new code to check what actually
changed. One of the three gaps found is substantially addressed; the
other two are untouched, confirmed byte-for-byte identical to before.

## What changed

`pass2_enhanced.py` gained a new, parallel extraction channel to
character detection: `extract_scene_objects()`, driven by a hardcoded
list of ~26 phrase patterns (`SCENE_OBJECT_PATTERNS`) explicitly
including `"falcon ridge"`, `"star needle spire"`, `"perimeter wall"`,
`"solid stone building"`, `"hut"`, `"barracks"`, `"archive"`,
`"fields"`, `"irrigation ditches"`, `"storage cache"`, plus generic
terrain words (`stream`, `waterfall`, `plateau`, `valley`, `ridge`).
Longest-phrase-wins span suppression prevents double-counting overlaps
(e.g. "solid stone building" claims its span before the standalone
"building"-shaped patterns could). Threaded through exactly the same
three-stage pipeline as `entities_observed` before it: a new
`(scene_object "Name" :category "..." :normalized_type "..." :mentions N)`
Metta atom (pass2) → parsed into `scene["scene_content_observed"]`
(pass3) → propagated to `=scene_content_observed` in the final
`.zonj.json` (pass4, mirrored at `=inferred.scene_objects`) →
`scene_inventory` in `game_scenes/*.json` (pass5, both
`metadata.scene_inventory` and top-level).

## Gap 1 (no place/structure entity type) — substantially addressed

Confirmed live. Re-running the pipeline on scene002 now produces 16
scene-content observations, including exactly the content the audit
named as missing:

```json
{"name": "Falcon Ridge", "category": "settlement", "normalized_type": "settlement", "mentions": 2}
{"name": "Star Needle Spire", "category": "landmark", "normalized_type": "spire", "mentions": 1}
{"name": "archive", "category": "structure", "normalized_type": "archive", "mentions": 1}
{"name": "barracks", "category": "structure", "normalized_type": "barracks", "mentions": 1}
{"name": "hut", "category": "structure", "normalized_type": "hut", "mentions": 2}
{"name": "perimeter wall", "category": "boundary", "normalized_type": "wall", "mentions": 1}
{"name": "solid stone building", "category": "structure", "normalized_type": "building", "mentions": 1}
{"name": "fields", "category": "settlement_feature", "normalized_type": "fields", "mentions": 2}
{"name": "irrigation ditches", "category": "settlement_feature", "normalized_type": "ditches", "mentions": 1}
{"name": "storage cache", "category": "settlement_feature", "normalized_type": "cache", "mentions": 1}
```

This is genuinely the shape the audit was looking for — a settlement,
three structures, farm-adjacent features, correctly separated by
category. `@entities` remains unchanged (`["Geralt", "Mika", "Oreck",
"Zephyr"]`, people only) — the new channel is additive and kept
separate, same authority discipline as `entities_observed`: this is
*observed content*, not folded into canon entities.

**Caveat, stated plainly:** this is a hardcoded phrase list, not a
general capability. It works here because the patterns were evidently
written with this exact chapter's vocabulary in mind (`"falcon ridge"`
appears verbatim in the pattern list). A different chapter describing
a "tavern," "temple," "bridge," or "farmhouse" — none of which are in
the list — would still produce nothing for those, the same gap as
before, just not visible on this particular test. Unlike
`entities_observed`'s people-detection (which generalizes via NLP-ish
character-mention counting, then gates against `world_rules.json`),
this is pattern-matching against a fixed vocabulary. It also has no
`known`/`spawnable`-style gate yet — every matched object is reported
as an unconditional observation, none of the three-tier authority
separation (observed / approved / runtime) built for characters.

## Gap 2 (environment/terrain misclassification) — unchanged, confirmed identical

```json
"region": "Unknown", "environment": "wasteland", "terrain_family": "wasteland"
"environment_inference": {
  "profile": "wasteland", "confidence": 0.49,
  "evidence": ["kw:desert", "kw:scrap", "segments:1 narration @scene_id: ...", ...]
}
```

Byte-for-byte the same as before this commit. The lush, irrigated,
waterfall-fed valley this scene actually describes is still classified
"wasteland" off the same "kw:desert" (metaphor about the surrounding
landscape) and "kw:scrap" (a scrap of fabric) votes the audit already
flagged as wrong. This commit did not touch `environment_inference` or
its keyword-voting logic at all.

## Gap 3 (landmark/boundary/hazard noise, 0/12 spatial relations) — unchanged, confirmed identical

```json
"locations": [{"id": "unknown", "name": "Unknown", ...}]
"level_design.landmarks": ["They reached the plateau"]
"level_design.boundaries": ["d stone between two ridges—but both Geralt and Mika sto", "ed from the eastern cliff."]
"level_design.hazards": ["I collapsed right here.\""]
"layout_proof": {"mode": "fallback_linear", "consumed_relation_count": 0, "unresolved_relation_count": 12}
```

Also byte-for-byte identical. `locations` is still the single
"Unknown" stub inherited from the still-broken `region` field;
`level_design`'s three lists are still the same noisy/truncated
fragments; `layout_proof` still resolves 0 of the 12 detected spatial
relations, still falls back to lining characters up on an axis. This
commit did not touch `pass1_spatial.py` or the layout-resolution code
in `pass5_game_bridge.py` at all — the preposition-only trigger
problem the audit traced (declarative "X was a Y" architecture
sentences never even attempted) still applies exactly as documented.

## Net effect

One of three named gaps meaningfully closed, with an honest caveat
about how far it generalizes; the other two stand exactly as
documented in the prior audit, not regressed, not improved. The
`=scene_content_observed`/`scene_inventory` channel is real, new,
useful evidence — the best candidate yet for "what does this scene
contain" — but `locations`/`level_design`/`layout_proof` (the fields
that would actually place that content spatially, which is what a
GodotSim-style consumer needs next) remain unusable on real content,
same as before.
