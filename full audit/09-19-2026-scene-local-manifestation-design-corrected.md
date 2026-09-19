# Correction: manifestation must separate presence from remote action/observation

Supersedes the category model proposed in `82b061b`
(`09-19-2026-scene-local-manifestation-design.md`). That design's
`embodied / remote / unestablished` enum is rejected before
implementation — it conflates two different questions. This document
replaces the category model only; everything else in `82b061b`
(spawnable stays global, `@entities_manifested` key-presence-not-
emptiness semantics, Pass 4 passthrough, GodotSim preference-with-
fallback, director override outside Mettaext) still stands and is not
re-derived here. **Still no code changed.**

## The mistake, stated plainly

`82b061b` classified Vaelith as `"remote"` because her segment says she
"projected her awareness through the Veil." That sentence describes
**where her attention/action is directed**, not **where she herself
is**. Checked directly against the scene's own authored structure —
line 21 of `scene.book001.001_the_ethereal_vigil.scene001.zonj.json`:

```text
participants: Lyaris, Theron, Vaelith, Mordain, Syreth, Korath
```

Vaelith is explicitly authored as a participant *in this scene* (the
Akashic Records). She is locally present, as a nonphysical
consciousness, while her awareness reaches somewhere else. Pelagor, by
contrast, is **absent** from that same participants line — confirming
Pelagor is not a participant in this scene at all, only detected
remotely. The two entities that shared a category in `82b061b` are
evidenced as opposite cases once presence and action are told apart.

## The corrected model: two orthogonal axes, not one enum

This mirrors a pattern already established in this exact codebase:
`known` and `spawnable` are two independent booleans on `Character`,
not one combined flag, specifically so a "known but not spawnable"
state (Lyaris) can exist without being force-fit into a single
lattice. Manifestation needs the same treatment:

```text
presence:      "local" | "remote" | "referenced_only" | "unknown"
physicality:   "physical" | "nonphysical" | null   (meaningful only when presence == "local")
```

Not locking exact string values yet, per instruction, but the axis
split itself is the load-bearing decision. Combined, these reproduce
the five states from the correction:

```text
presence=local,    physicality=physical     <- Senareth, Giants
presence=local,    physicality=nonphysical  <- Vaelith, Lyaris, the other Keepers
presence=remote                             <- Pelagor (ch1)
presence=referenced_only                    <- Tiamat
presence=unknown                            <- default when neither participants
                                                data nor text evidence resolves it
```

`@entities_manifested` (from `82b061b`) becomes: `spawnable AND
presence == "local" AND physicality == "physical"`.

## The strongest available evidence source: the authored `participants:` line

Every scene-meta block already contains a human-authored participants
list (`scene1 line 21` above; `scene.book001.002_molten_descent.scene001`
line 21: `"participants: Senareth, Elyraen, Vairis, Olythae, Nephoretti
assembly, Mordain, transformed Pelagor (Giants)"`). This is direct,
explicit, author-intended ground truth for the **presence** axis — who
is actually in the scene — independent of any keyword heuristic over
prose.

This is not a new pattern for this pipeline. `pass4_zon_bridge.py`'s
`_resolve_scene_terrain_meta()` already treats an explicit `REGION:`
annotation as the top-priority, `confidence: 1.0`,
`source: "explicit_annotation"` evidence tier, only falling back to
weighted keyword voting when no explicit annotation exists (lines
215-232). The `participants:` line deserves the identical treatment
for the presence axis: parse it first, as authoritative; fall back to
prose-based inference only for entities the participants line doesn't
mention or resolve.

**This needs care, not hand-waving, when implemented**: the line is
free text, not a clean canonical list — `"Nephoretti assembly"` and
`"transformed Pelagor (Giants)"` both mix a canonical name with
modifiers/aliases/parentheticals. Resolving these to world_rules
canonical names will need something like `pass4_zon_bridge.py`'s
existing `_resolve_to_canonical()` last-word/substring matching
heuristic, not exact string comparison. Flagged as a real
implementation risk, not assumed solved.

Physicality (the second axis) still needs prose-based inference where
`presence == "local"` — the participants line doesn't say who has a
body. Entity-type hints from `world_rules.json` (e.g.
`entity_type: "aeon_keeper"`) can seed a prior, but should not
override direct textual evidence when it exists (Senareth's `entity_type`
is presumably plain `"character"` with no inherent physicality
default — her physicality has to come from the body-formation
narration itself).

## Chapter 1 negative controls (confirmed against real text)

```text
Vaelith
  participants line: present            -> presence = local
  text: "projected her awareness through the Veil" describes her
        ACTION, not her location; no body/embodiment language anywhere
        for her                          -> physicality = nonphysical
  world_rules: spawnable = true (global capability, untouched)
  Expected @entities_manifested membership: EXCLUDED
    (local, but not physical)

Pelagor (chapter 1 only -- see chapter 2 below for the same identity
after transformation)
  participants line: ABSENT
  text: "unmistakable resonance of Pelagor essence," "energy
        signatures," "life signatures" -- all detection-at-a-distance
        language, never placed in the room
                                         -> presence = remote
  world_rules: spawnable = true (global capability, untouched)
  Expected @entities_manifested membership: EXCLUDED
    (not local at all)
```

## Chapter 2 positive controls (confirmed against real text)

```text
Senareth -- scene.book001.002_molten_descent.scene001 + scene002
  participants line (scene001): present
  text: "Senareth's consciousness-pattern became a framework
        first... The body began forming... Muscles... Organs...
        Neural networks that connected thought to matter"
        (scene001, lines 69-79) -- direct, real-time embodiment
        narration, not exposition
  text: "Senareth tried to stand and immediately fell" / "The sand
        was rough against their palms" / "Senareth forced themselves
        to stand" (scene002, lines 25, 28, 92) -- ongoing physical
        interaction with the local environment
                                         -> presence = local,
                                            physicality = physical
  world_rules: spawnable = true
  Expected @entities_manifested membership: INCLUDED
    -- the clean positive control this model needed.

Giants / transformed Pelagor -- scene.book001.002_molten_descent.scene002
  participants line (scene001): "transformed Pelagor (Giants)" listed
  text: "took several steps backward," "emerged from the forest,"
        "stood among the charcoal-grey" (lines 62, 66, 114) -- direct
        local physical action
                                         -> presence = local,
                                            physicality = physical
  world_rules: "Giants" entity_type "collective", cardinality
        "species", spawnable = FALSE (non-spawnable by cardinality,
        independent of manifestation)
  Expected @entities_manifested membership: EXCLUDED
    -- but for a DIFFERENT reason than Vaelith/Pelagor (not spawnable
    at all, not a manifestation failure). This is the important
    proof that manifestation and spawnable are genuinely orthogonal:
    a physically-local entity can still be correctly excluded from
    the spawn list on spawnable grounds alone, and the two gates must
    stay independent, evaluated in either order, not folded together.
```

This also means manifestation inference must run over **every** known
entity in `entities_observed`, not only ones already `spawnable:true`
— otherwise Giants would never get audited presence/physicality data
at all, and `entities_observed`'s role as the complete presence-and-
classification record (established in `04d8abe`/`08fb992`) would
regress back to being spawnable-filtered.

## A referenced-only example, for completeness of the taxonomy

```text
Tiamat -- chapter 1
  participants line: absent
  text: only past-tense exposition ("since Marduk's collision
        shattered Tiamat"), never sensed/detected/observed in the
        scene's present moment
  world_rules: entity_type "celestial_body", cardinality "abstract",
        spawnable = false, render_as = "none"
                                         -> presence = referenced_only
```

Not acceptance-critical (already excluded on spawnable/render_as
grounds regardless), but useful for keeping `referenced_only`
distinguishable from `remote` in the model: Pelagor is being actively
sensed *right now* from a distance; Tiamat is only being talked about
as history. Collapsing these two would be a smaller version of the
same mistake this correction is fixing.

## One more thing the registry already half-anticipated

`world_rules.json`'s `Nephoretti`/`Giants` entries already carry
`runtime_projection: "conditional"` (vs. `"physical"` or `"excluded"`
for individual characters) and a note: *"Not a single physical actor.
Requires multi-agent or ambient presence logic."* Confirmed via the
earlier consumer trace (`7fae863`) that nothing in `bridge_integration.py`
currently reads `runtime_projection` at all. This isn't something to
act on now, but it's worth naming: the global registry already has a
placeholder for graduated, non-binary projection modes; this
manifestation gap and that placeholder are likely related and should
probably be reconciled at implementation time rather than designed
twice, independently.

## Still open, not decided

- Exact string values for `presence`/`physicality` are illustrative,
  not final.
- The `participants:` line parser's handling of multi-word/aliased/
  modified entries (`"transformed Pelagor (Giants)"`,
  `"Nephoretti assembly"`) needs a concrete resolution strategy before
  implementation, not just a plan to "use `_resolve_to_canonical`."
- What happens when the participants line and prose evidence conflict
  (e.g., an entity is listed as a participant but the prose never
  otherwise mentions them) is not decided.
- Whether `unknown` should ever be treated differently from
  `referenced_only` by any downstream consumer, or whether that
  distinction matters only for audit/inspection, is open.
- `runtime_projection: "conditional"` reconciliation, noted above, is
  flagged but not scoped.

## What was not done

No code changed. This corrects the category model from `82b061b`
before any implementation begins; the rest of that design (schema
plumbing, key-presence semantics, GodotSim preference/fallback,
director override outside Mettaext) is unchanged and still pending
the same "hold implementation" instruction.
