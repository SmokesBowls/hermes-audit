# Every active consumer of `@entities`, traced — read-only, no code changed

Direct answer to: hold implementation, search every active consumer of
`@entities`, and determine what each assumes it means before deciding
how to fix the Pass2→3→4 entity handoff. This changes the answer —
there is a real, live consumer with no independent spawnable check.

## All consumers found (8 files, active code only; one additional file confirmed inactive)

```text
tier3/mettaext/passroom/pass4_zon_bridge.py    WRITER + reader (traced already, e5ca7f2)
tier3/mettaext/passroom/pass5_game_bridge.py   reader
tier3/mettaext/zw_compiler.py                  writer -- CONFIRMED INACTIVE (below)
tier2/godotsim/bridge_integration.py           reader -- spawns physical Godot entities
tier2/godotsim/scene_manager.py                reader/relay -- feeds bridge_integration
tier2/godotsim/scene_extractor.py              reader -- builds reference "EntityCard"s
tier2/godotsim/http_handlers.py                reader -- search/scoring only
tier2/godotsim/vault_linker.py                 writer -- separate ingestion path (below)
```

## Confirmed inactive: `zw_compiler.py`

Not imported by `pipeline_runner.py` or any file in the active
`engain_door.py ingest` chain; no other active file references it.
Its `extract_canon_entities()` (line 411) already does correct
word-boundary matching (`re.search(r'\b' + re.escape(canon) + r'\b', ...,
re.IGNORECASE)`) — worth knowing as precedent that word-boundary
matching is an established, already-used pattern in this codebase, but
this file itself is not part of what actually ran for this session's
ingestions and is excluded from the rest of this trace.

## The critical finding: one active, wired-in consumer has no independent spawnable check

**`tier2/godotsim/bridge_integration.py`'s `bridge_entities_for_scene()`**
— confirmed genuinely active and reachable: called directly from
`scene_manager.py:346` (`_bridge_entities_for_scene()`) and
`sim_runtime.py:415,563` — the actual Godot simulation runtime.

Its own docstring: *"Resolve all entities in a scene through the
semantic bridge. Returns a list of serialized Entity3D dicts ready for
Godot. Each dict contains: entity_id, placeholder_mesh, color,
transform, ap_profile, etc."*

Grepped the entire file for `spawnable`/`render_as`/`is_spawnable`:
**zero matches.** This function reads `@entities` (falling back from
`entities`), treats every entry as something to build a physical
`Entity3D` for, and has **no filtering step of its own** to exclude a
non-spawnable or purely-ethereal entity. If `@entities` ever contained
an entry like Lyaris (known, non-embodied, explicitly described as
"distributed awareness" with no physical form), **this function would
attempt to give her a placeholder mesh and a 3D transform anyway.**

This is exactly the risk the user flagged before approving anything.

## The other active consumers, by contrast, are safe either way

**`pass5_game_bridge.py`** (`_create_characters()`, docstring:
*"Create character entries, filtering non-spawnable and using
canonical names"*) — has its **own independent** `_is_spawnable()`
check (`:651-664`) applied to every entity before creating a character,
regardless of what `@entities` contains. Also separately reads
`entities_observed`/`=entities_observed` and passes it through as its
own metadata field (`:776-781`, `:809-810`) — it does not rely on
`@entities` alone at all. **Safe under either semantic.**

**`scene_extractor.py`** (`_discover_entities`-style phase) — uses
`@entities` only to seed lightweight "EntityCard" reference objects,
filtered by stopwords/length only, no spawn implication. **Safe under
either semantic** — this is a presence/reference use, not a spawn use.

**`http_handlers.py`** — uses `@entities` only for full-text search
relevance scoring (does the query string match an entity name). No
spawn implication whatsoever. **Safe under either semantic.**

**`scene_manager.py`** (`load_scene`) — mostly a pass-through/relay:
copies `@entities` into a "normalized view" dict for storage, and
separately is the caller that invokes `bridge_integration.py`'s
spawn-semantics function later (`:346`). It doesn't interpret
`@entities` itself at the point traced; its risk is entirely inherited
from `bridge_integration.py` downstream.

**`vault_linker.py`** — a **separate, independent ingestion path**,
not part of the `pipeline_runner.py`/pass1-5 chain at all. Its own
docstring admits `@entities` there is populated by a *"names detected
in text (capitalized words heuristic)"* — i.e., it's already a raw,
unfiltered presence-style list at the point it's written, by a
completely different tool than Mettaext's own pipeline. Not
consumed by anything traced in this pass beyond its own writer role;
flagged for completeness, not analyzed further since it doesn't touch
`pass3`/`pass4`'s handoff.

## None of the reader consumers (except pass5) currently reach for `entities_observed`/`known`/`spawnable`/`classification` on their own

Only `pass5_game_bridge.py` reads `entities_observed` independently.
`bridge_integration.py`, `scene_manager.py`, `scene_extractor.py`, and
`http_handlers.py` never reference it at all — they only ever look at
`@entities`/`entities`. So today, if a consumer wants spawnable-safety
information, `@entities` (pre-filtered by Pass 4's existing
`_normalise_and_filter()`) is the *only* place three of these four
readers currently get it from.

## Direct answer to "what does `@entities` currently mean"

**Today, in practice, `@entities` means "spawnable" for at least one
real, live consumer (`bridge_integration.py`), by omission rather than
by anyone deciding it should — that consumer simply never got its own
safety check the way `pass5_game_bridge.py` did.** It is not
consistently "canonical" or "presence" anywhere; the only place that
concept is actually preserved correctly today is `entities_observed`,
which most consumers never look at.

## What this means for the fix, stated as a choice rather than decided here

```text
Option 1 — keep @entities meaning "spawnable-safe," add presence
  elsewhere:
    Leave @entities as pre-filtered/spawnable (matching what
    bridge_integration.py already assumes with no changes needed
    there). Give Pass 3 a genuinely separate field for "who Pass 2
    says is present" (entities_observed already exists and already
    carries this -- the actual gap becomes "make bridge_integration.py
    and scene_extractor.py/http_handlers.py aware of
    entities_observed too, if presence-level completeness ever matters
    to them" -- a separate, later concern, not required to fix Tran/Lyaris).
    Lyaris then correctly lives in entities_observed, not @entities,
    and nothing downstream needs to change to stay safe.

Option 2 — redefine @entities as "presence," fix every consumer:
    Change @entities to mean known-present (per the user's own stated
    intent), and ALSO add an independent spawnable check into
    bridge_integration.py (mirroring pass5's own _is_spawnable()
    pattern) so it stops trusting @entities for spawn-safety. This
    achieves the cleaner single-field semantic the user described, but
    is strictly more work and touches a second file
    (tier2/godotsim/bridge_integration.py, a different, more
    consequential runtime-facing subsystem than tier3/mettaext) in
    the same change.
```

Both options fix the Tran/Lyaris defect at the Pass2→3→4 level either
way, since both keep `entities_observed` correct and either leave
`@entities` alone (Option 1) or fix its one unsafe consumer alongside
it (Option 2). The difference is entirely about whether `@entities`'s
meaning changes globally or a new/existing field absorbs the
"presence" concept while `@entities` keeps its de facto current
meaning. Not decided here, per instruction — this is the fork the user
asked to see before approving anything.

## What was not done

No code changed anywhere. This is the requested consumer trace only.
