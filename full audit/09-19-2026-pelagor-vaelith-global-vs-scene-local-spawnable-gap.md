# Pelagor and Vaelith: `spawnable:true` is global identity capability, not scene-local manifestation — and `bridge_integration.py` cannot tell the difference

Read-only investigation, per instruction. No code changed. Traces
exactly why fresh chapter 1 produces `@entities = [Pelagor, Vaelith]`
and what the live Godot bridge would actually do with that.

## 1. Why Pass 2 classifies both `spawnable: true` — checked at the source

`world_rules.json`, both entries in full:

```json
"Pelagor": {
  "canonical_name": "Pelagor", "entity_type": "character",
  "cardinality": "individual", "spawnable": true,
  "render_as": "physical_actor", "runtime_projection": "physical"
},
"Vaelith": {
  "canonical_name": "Vaelith", "entity_type": "character",
  "cardinality": "individual", "spawnable": true,
  "render_as": "physical_actor", "runtime_projection": "physical"
}
```

No scene, chapter, or book scoping on either entry. Confirmed by
reading `pass2_entity_filter.py`'s `_is_runtime_renderable()` — the
exact function that sets `spawnable: True` — its own docstring states
it outright: *"Runtime render permission comes only from
world_rules.json."* The function's only input is the entity's bare
name; it never receives scene text, segments, or any per-scene
context:

```python
def _is_runtime_renderable(clean: str) -> bool:
    if not world_rules_loader.is_known(clean):
        return False
    if not world_rules_loader.is_spawnable(clean):
        return False
    if world_rules_loader.get_render_as(clean) == "none":
        return False
    return True
```

**Direct answer: this is entirely global identity capability, not scene-
local manifestation evidence.** "Pelagor: spawnable:true" means exactly
the same thing in this scene as it would in any other scene in the
entire novel that happens to mention the name "Pelagor" — the pipeline
has no mechanism anywhere to ask "is Pelagor actually, physically here,
right now, in this specific scene" as a separate question from "is
Pelagor a character the registry says may ever be rendered as a
physical actor."

Compare `Lyaris`'s entry, for contrast — same `render_as:
"physical_actor"` value, but `spawnable: false, runtime_projection:
"excluded"`, with a human-authored note: *"Keeper-type character. Name
ends in s — explicit individual override."* This confirms the registry
is manually curated per-name (Aeon Keepers generally excluded, with
individual overrides), not derived from any scene evidence either —
it's a different global default, still global.

## 2. What the scene's own evidence already established about these two

Already on record from this session's earlier scene-representation
trace (`9205232`, Dragon's own proposal for this exact scene):

```text
Vaelith: "Represent nonphysically -- Projects awareness through
          the Veil; no body established."
Pelagor: "Represent nonphysically -- The Keepers detect Pelagor
          essence remotely; physical co-location and exact bodily
          appearance are not established."
```

**Neither entity is depicted as physically/locally present in this
scene, per the narrative evidence already extracted.** Vaelith is one
of the six ethereal Aeon Keeper consciousnesses — the same category as
Lyaris — and Pelagor is only ever detected remotely as an energy
signature. The only reason Vaelith ends up in `@entities` while her five
fellow Keepers (including Lyaris) don't is that her *name* happens to
carry a global `spawnable: true` flag in the registry, for reasons
unrelated to this scene.

## 3. Traced `bridge_integration.py` precisely: yes, it would spawn both, unconditionally

Read `bridge_entities_for_scene()` to its end. The core loop:

```python
for i, ent in enumerate(raw_entities):
    ...
    zon_position, placement_source = _resolve_position_with_source(ent, i, len(raw_entities))
    zon_entity = {"id": eid, "type": concept_type, "position": zon_position}
    entity3d = zon_to_entity3d(zon_entity, registry)
    result = entity3d.to_dict()
    ...
    results.append(result)
```

**No presence/manifestation check exists anywhere in this loop.** Every
entry in `raw_entities` (sourced from `@entities`) gets a computed
position — via `_resolve_position_with_source(ent, i, len(raw_entities))`,
which spaces entities out algorithmically by list index/count, not by
any real spatial evidence — and an `Entity3D` object with a transform,
unconditionally.

The one filter that runs afterward, `filter_bridge_entities_by_declared_ids()`,
is **circular, not a presence check**: its `allowed_ids` comes from
`declared_entity_ids(scene_doc)`, which itself just reads
`scene_doc.get("entities")` / `scene_doc.get("@entities")` — the same
field the loop already consumed. It exists to guard against the
registry-resolution step injecting something *not* in the original
list (e.g. from `spawn_commands`), not to verify that a declared entity
is actually, locally embodied in this scene.

**Direct answer: yes, `bridge_integration.py` would create physical
`Entity3D` representations — with a position, a transform, and
whatever placeholder mesh/color the registry assigns — for both
Vaelith and Pelagor in this scene, exactly as it would for any
genuinely embodied character, with nothing distinguishing "detected as
a remote energy signature" from "standing in the room."**

## The five distinctions, mapped against what actually exists in the pipeline today

```text
1. entity is present/referenced
   EXISTS: entities_observed (Pass 2/3, correct, this session's fix)

2. entity is known
   EXISTS: entities_observed[].known (Pass 2, matched against world_rules.json)

3. entity has an avatar / can ever be spawned
   EXISTS: entities_observed[].spawnable, and now @entities (this
   session's fix) -- but this is GLOBAL, PER-NAME, STATIC. It answers
   "can this character ever be a physical actor, in any scene," never
   "should it be one here."

4. entity is physically/locally manifested in THIS scene
   DOES NOT EXIST ANYWHERE IN THE CURRENT PIPELINE. No field, no
   check, no data source. This is exactly what distinguishes Vaelith
   (globally spawnable, but ethereal/unembodied in this scene) from a
   hypothetical scene where she's actually described walking into a
   room. Today's fix could not have added this -- it wasn't in scope
   and doesn't have a natural home in world_rules.json's static schema.

5. Dragon/director chooses to instantiate it anyway
   DOES NOT EXIST AS A WIRED MECHANISM. bridge_integration.py has no
   concept of a director override at all -- it just spawns whatever
   @entities contains. The conceptual layer this session established
   early on (9205232: "spawn them here anyway" as an adaptation
   decision layered on source evidence) has no code path into this
   consumer today.
```

## Why this is not a regression from today's fix, and not something it should have tried to solve

The entity handoff fix (`bcdad29`) did exactly what it was scoped to
do: it made `@entities` correctly reflect `entities_observed`'s
existing `spawnable` classification, instead of being independently
(and buggily) reconstructed by Pass 4's narration scan. **Both Pelagor
and Vaelith were *already* globally `spawnable: true` in
`world_rules.json` before today's fix — that fact is untouched by
anything changed today.** The fix correctly stopped an unrelated bug
(the Tran substring match) from adding noise to `@entities`, and it
correctly kept Lyaris out (since her global flag is `false`). It never
had, and was never asked to have, any way to know that *this specific
scene* doesn't actually show Pelagor or Vaelith with a body — that
information isn't captured by Pass 2's extraction at all right now.

## What this means, stated as an open question, not a decision

If gap #4 (scene-local manifestation) is ever worth closing, it would
need new evidence Pass 2/Pass 3 don't currently produce — something
like "is this entity's presence in this scene described as embodied/
physical, or as remote/ethereal/referenced" — which is a real
extraction task (arguably harder than the entity-name matching already
fixed today), not a metadata plumbing fix like this session's other
changes. Whether that's worth building now, later, or handled instead
by a director-level review step (a human or Dragon looking at each
scene's spawnable-but-maybe-not-manifested entities before a build)
is not decided here.

## What was not done

No code changed anywhere. This is a read-only trace of exactly why
these two names appear in fresh `@entities`, and exactly what the live
Godot bridge would do with them.
