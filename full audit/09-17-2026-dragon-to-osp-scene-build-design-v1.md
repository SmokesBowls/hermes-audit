# Dragon → OSP: narrative comprehension to a buildable scene (design v1, spec only, no code)

Answers the question raised this session once the Mettaext door, MrLore
door, and the whole tier2/tier1 inventory were mapped: **what does
Dragon actually hand to "the tool" once it has understood a scene?**
Per the user's own framing: "the dragon is not asking, it is
understanding... anyone can load any book/story/event/history and the
dragon hears it and the tool builds it." This locks the architecture for
that missing piece. Nothing here is implemented. All facts about
existing systems are re-verified today, not assumed from memory.

## 0. What already exists and gets reused, not rebuilt

Four real, independently-verified pieces chain together for this, none
of them new:

1. **Mettaext raw-text evidence** — `engain_door.py`'s lane A (frozen
   contract, `09-15-2026-engain-door-contract-v1.md`) or a direct read of
   `output/passroom/<scene_id>/out_pass1_<scene_id>.txt`. Gives Dragon
   provenance-tagged narration/dialogue lines for a scene.
2. **Topologist** (`EngAIn/tier2/topologist`) — converts qualitative
   spatial relations (near/behind/beside/within/approach/enter/etc.,
   RCC-8-style QSLINK/OLINK/MOVELINK) into a validated
   `ProseTopologyArtifact`. Proven on a toy fixture, not yet on real
   content (see [[engain-tier2-module-inventory]]).
3. **Cartographer** (`EngAIn/tier2/cartographer`) — takes an *accepted*
   topology artifact and deterministically solves real meter-space
   positions (`world_cell_y_up`). Same proof maturity as Topologist.
4. **OSP v0.1 + the Godot 4 adapter** (`/mnt/data-drive/
   ob-scene-workspace`) — a real, working scene-package format
   (`ob_scene_package.v0.1.schema.json`) and a real Godot loader
   (`adapters/godot-4/osp_loader.gd`) that builds an actual scene tree
   from `.osp` JSON: groups, asset instances (GLB models by resource
   ID), primitives, cameras, lights, environment bindings, explicit
   transforms, hash-verified package integrity, material-binding
   verification. Proven today on a real fixture (Kenney "Mini Arena":
   statue, tree, banner, column, bricks — 5 model identities, 6
   instances). This is the only fully-working "declarative scene
   description → real engine output" proof found anywhere in this
   ecosystem this session.

OSP's own doctrine (`contracts/osp-v0.1/README.md`) already states the
right shape of the missing piece without knowing it: every package field
must trace to one origin class — `vault_authored` (human-authored intent
from the source vault), `authority_resolved` (identity/placement/metrics
resolved by governed authorities), `workspace_derived` (deterministic
compiler products), `osp_emitted` (the final package),
`adapter_derived` (engine realization). **A conforming `.osp` proves
mechanical conformance only — never canon approval, runtime admission,
or that the scene is narratively correct.** That boundary is exactly
where Dragon's output needs to land: Dragon proposes, it does not emit
`.osp` directly.

## 1. What's missing — one bridge, not a rebuild

`ob-scene-workspace`'s own plan for connecting narrative evidence to
`.osp` (a six-ticket "Codex" evidence ladder, T1 exact witnesses through
T6 scope-bound canon acceptance, then a "Physical Scene Projection
Contract" turning accepted assertions into `.osp`) is real, well-designed
on paper, and stalled: only T1+T2 have code (80 witnesses, 28 surface
groups), T3 is contract-closed but has zero code and is blocked on an
unsealed prerequisite, T4-T6 never left "architecture bounded." That
ladder exists to let many independent, non-LLM extraction stages agree
before anything is trusted — valuable if the producer is a dumb pattern
matcher, but Dragon isn't one. **Per this session's own reframing, Dragon
(the LLM) can read raw scene prose and reason about "what should exist"
directly** — it doesn't need six tickets of proposal/acceptance ceremony
to do what a human reading the same chapter would do instinctively. The
missing piece is narrower than the stalled ladder: a way to get Dragon's
own understanding into the same shape Topologist/Cartographer/OSP
already expect, without reinventing evidence-laddering.

Two things need designing, not six:

1. **A semantic scene-build proposal Dragon emits** — reusing "the
   door.md"'s own original term from months ago: `[EDITOR_REQUEST]`.
   Not `.osp` (Dragon can't ground real asset IDs or final transforms
   from reading prose alone), not raw prose either — a structured
   middle layer naming what Dragon concluded should exist and how
   things relate spatially, in terms Topologist/Cartographer and an
   asset resolver can consume.
2. **An asset-resolution table** — turning Dragon's semantic concepts
   ("a hut," "a stone archive," "a perimeter wall") into concrete OSP
   `resource_id`s, using the exact same doctrine already proven in this
   codebase for exactly this kind of mapping: `tier2/worldfield`'s
   `TERRAIN_TO_RECIPE` table (`grid_facts_emitter.py`) — explicit
   entries only, unmapped concepts emit `null` and get surfaced in an
   `unmapped_concepts` list, never guessed or invented. Fail-closed, not
   fail-silent, matching every other authority boundary in this project.

## 2. Proposed flow, end to end

```text
BOOK / STORY
     ↓ (existing: raw vault ingest)
Mettaext
     ↓ (existing: door lane A, or direct pass1 read)
scene raw text + provenance
     ↓ (Dragon reads directly — no query needed, no lookup)
DRAGON comprehension
     ↓ (NEW — this design)
[EDITOR_REQUEST] — semantic scene-build proposal
     ↓ splits two ways
     ├─→ spatial relations → Topologist → Cartographer → real transforms
     └─→ named entities/structures → asset-resolution table → resource_id
              (or: unmapped_concepts, surfaced, not guessed)
     ↓ (NEW — assembly step, deterministic, no LLM)
assembled candidate .osp
     ↓ (existing: OSP's own mechanical validator, `gates/validate_osp_v0_1.py`)
validated .osp
     ↓ (existing: `osp_loader.gd`)
Godot realization
```

Only the two `NEW` steps are undesigned. Everything else in this chain
is real, already-built code, re-verified today.

## 3. `[EDITOR_REQUEST]` — what it needs to carry (design-only, fields not frozen)

Door-owned choices to make when this gets a real contract pass (not
decided here, flagged for the next design session):

- **Entities named, with a semantic type, not a resource_id.** Dragon
  writes `"a stone archive with a vaulted ceiling"`, not a model path.
  Grounding to a real asset happens later, deterministically, never by
  Dragon guessing a `.glb` filename.
- **Spatial relations in the same relation vocabulary Topologist
  already accepts** (near/behind/beside/within/approach/enter/etc.) —
  reusing the existing `_TO_OLINK`/`_TO_QSLINK`/`_TO_MOVELINK` tables in
  `passroom_signal_converter.py` rather than inventing a second
  vocabulary Topologist would then need to learn.
- **Provenance back to the source scene** — which `scene_id`,
  `chapter_id`, and (if door-sourced) which `artifact_line`s grounded
  each claim. Matches every other artifact in this ecosystem: nothing
  here is ever presented without a line back to source.
- **Explicit `confidence`/`authority` posture of `proposal_only`** — same
  zero-lock discipline `ob-scene-workspace`'s own Ticket 3 design
  insists on ("every valid child proposal remains confidence_basis_
  points = 0, promotion_state = proposal_only"). `[EDITOR_REQUEST]` is
  Dragon's read of the text, not accepted canon — MrLore (whichever
  implementation eventually clears its RED gates) remains the identity/
  canon authority, Dragon does not self-certify.
- **What it must NOT contain**: real transforms (Cartographer's job),
  real resource IDs (the asset table's job), anything read as accepted
  canon (MrLore's job, not reachable from this design).

## 4. Asset-resolution table — the real, current limitation

The honest constraint, stated plainly: **today, the only real,
`.osp`-realizable assets proven in this pipeline are Kenney's five Mini
Arena models (statue, tree, banner, column, bricks).** None of them are
a hut, a barracks, a perimeter wall, or a stone archive — the exact
vocabulary the Falcon Ridge scene (this session's running example) would
need. Running `[EDITOR_REQUEST]` against that scene today would produce
mostly `unmapped_concepts`, honestly reported, not a populated scene.
This isn't a flaw in the design — surfacing the gap instead of inventing
placeholder geometry is the same fail-closed discipline as everywhere
else — but it means **this pipeline's near-term ceiling is asset-library
breadth, not narrative comprehension.** Growing the asset table (more
Kenney packs, Trixel-authored assets once ready, procedural primitives
per `worldfield`'s own primitive-generation pattern) is separate, real,
substantial work, out of scope for this design.

## 5. Non-negotiable rules

- Dragon's `[EDITOR_REQUEST]` is never treated as an accepted `.osp`.
  The compilation boundary OSP's own README already declares stays
  intact: proposal → deterministic resolution → mechanical validation →
  realization. No step is allowed to skip forward.
- The asset-resolution table and the spatial pipeline are both
  deterministic, table/solver-driven, non-LLM — same as every other
  "authority" boundary found this session. Dragon proposes meaning; it
  does not resolve its own asset IDs or coordinates.
- Unmapped concepts are surfaced, never guessed, never silently dropped.
- This design does not touch canon, does not touch MrLore's identity
  authority, does not invoke AP, does not wire runtime. It ends at a
  validated `.osp` ready for passive Godot realization — the same stop
  line `ob-scene-workspace`'s own doctrine already draws.

## 6. Status

Architecture sketched at this document. Not designed yet: the exact
`[EDITOR_REQUEST]` JSON schema, the initial (necessarily small) asset
table, and the deterministic assembly step that merges Topologist/
Cartographer output with asset resolution into a candidate `.osp`. No
code written. Next step, when authorized: freeze `[EDITOR_REQUEST]`'s
schema the same way the Mettaext and MrLore door contracts were frozen —
field by field, against a real scene (Falcon Ridge is the natural choice
given how much of today's audit already grounds there) — before any
code, and with the asset-table gap stated up front rather than discovered
after the fact.
