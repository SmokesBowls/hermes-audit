# Fix plan: Pass2→Pass3→Pass4 entity handoff (spec only)

Implements the two-change plan confirmed after `e5ca7f2`. Spec only —
no code changed yet. Surfaces one real design decision the primary fix
depends on before proposing exact code, per the same discipline used
throughout this line of work.

## The one thing that needs deciding first: what does `@entities` mean?

Checked `pass4_zon_bridge.py`'s `_normalise_and_filter()` — the
function that runs whenever `@entities` *is* already populated. It
does more than dedupe/canonicalize:

```python
def _normalise_and_filter(self, names: List) -> List[str]:
    result: set = set()
    for raw in names:
        name = str(raw).strip()
        if not name or name.lower() in _SPEAKER_STOPWORDS:
            continue
        resolved = self._resolve_to_canonical(name)
        candidate = resolved if resolved else name
        if self.world_rules and not self._is_spawnable(candidate):
            continue          # <-- drops non-spawnable entities
        result.add(candidate)
    return sorted(result)
```

It drops anything not `spawnable`. Scene 1's real Pass 2 candidates
include **Lyaris, classified `known: true, spawnable: false`** —
exactly like Ethereal, Korath, and Tiamat. **If the primary fix simply
projects Pass 2's known entities into `@entities` and lets this
existing function run unchanged, Lyaris would still be filtered out
of the final `@entities`** — same outcome as today, for a different
reason.

This is the same distinction the very first design conversation in
this session established (`9205232`): *"entity exists in the story ≠
entity must physically instantiate in the game scene."* `@entities`
answering "who/what is present" and `spawnable` (already correctly
preserved in `entities_observed`) answering "should this be rendered
physically" are two different questions. Filtering `@entities` down to
spawnable-only would quietly re-introduce that same flattening error
one level down in the pipeline.

**Recommendation, to satisfy the stated acceptance criteria directly:**
`@entities` should be projected from Pass 2's **known** entities
(`known: true`), regardless of `spawnable`, and should bypass
`_normalise_and_filter()`'s spawnable-drop when the source is this new
upstream projection. `entities_observed` remains the place spawnable/
classification detail lives — `@entities` becomes "who Pass 2 confirmed
is actually present," matching what the acceptance checklist actually
asks for. This is stated here as the plan's working assumption, not
decided unilaterally past the point of flagging it — worth a beat of
confirmation before implementation, since it's a real semantic choice
about what `@entities` is for, not just a code path.

## PRIMARY fix — `pass3_merge.py`

**Function:** `merge_to_zonj()` (`:585-634`)

**Current behavior:** builds `scene["entities_observed"]` from
`p2.entities` (already correctly parsed, known/spawnable/classification
intact). Never assigns `scene["@entities"]` under any condition.

**Proposed behavior:** add, alongside the existing
`entities_observed` assignment:

```python
if p2.entities:
    scene["entities_observed"] = [
        dict(info) for name, info in sorted(p2.entities.items())
    ]
    known_names = sorted(
        name for name, info in p2.entities.items() if info.get("known")
    )
    if known_names:
        scene["@entities"] = known_names
```

Only assigns `@entities` when at least one known entity exists —
leaving it absent (not an empty list) when Pass 2 found nothing known,
so Pass 4's existing "not populated" branch still applies correctly to
that case rather than silently producing an empty result.

**Risk:** low, additive. Doesn't touch `entities_observed`'s existing
construction or any other field `merge_to_zonj()` produces.

## Companion change needed in `pass4_zon_bridge.py` for the primary fix to actually work

Per the design-tension section above, `extract_entities()`'s existing
branch —

```python
existing = obj.get("@entities")
if isinstance(existing, list) and existing:
    return self._normalise_and_filter(existing)
```

— would still apply `_normalise_and_filter()`'s spawnable-drop to the
new field, filtering Lyaris back out. **This needs its own small,
separate change**, not folded into the "defensive" narration-scan
fix below: when `@entities` arrives already-known-filtered from Pass 3
(the new, intended path), skip the spawnable-drop and just
canonicalize/dedupe. Simplest shape: a new, narrower helper (e.g.
`_canonicalize_known(names)`) that resolves-to-canonical and dedupes
without the `_is_spawnable` check, used for this path instead of
`_normalise_and_filter()`. Exact implementation left to the actual
edit, not fully specified here — flagged now so it isn't discovered as
a surprise after the primary fix "doesn't work."

## DEFENSIVE fix — `pass4_zon_bridge.py`

**Function:** `extract_entities()`, the "Narration scan" block
(~`:445-452`)

**Current behavior:** `if cn.lower() in all_text: canonical.add(cn)` —
substring containment against the full scene text, for every
`spawnable` entity in `world_rules.json`.

**Proposed behavior:** replace the substring check with a
word-boundary-respecting match — e.g.
`re.search(rf"\b{re.escape(cn.lower())}\b", all_text)` — so "tran"
only matches the standalone word "tran," never as a prefix of
"transformed." Kept as a defensive hardening of this fallback path,
not removed entirely, per the instruction to treat it as a legacy/
partial-input safety net rather than delete it outright.

**Risk:** low for this exact change; the fallback's overall
*frequency* of firing should already drop sharply once the primary fix
lands (per the design-tension section, it now only fires when Pass 2
found zero known entities for a scene), so this narrows blast radius
further rather than changing behavior for the common case.

## Required regression coverage, matching the stated acceptance checklist

```text
1. pass3_merge.py: p2.entities with a known:true, spawnable:false
   entity (Lyaris-shaped) -> scene["@entities"] includes it.
2. pass3_merge.py: p2.entities with only known:false entities (Aeon/
   Keepers-shaped) -> scene["@entities"] is absent, not an empty list.
3. pass3_merge.py: entities_observed's own construction is byte-for-
   byte unchanged by this addition (regression pin).
4. pass4_zon_bridge.py: extract_entities() given a pre-populated
   @entities containing a known:true/spawnable:false name -> survives
   into the final list (proves the companion change works, not just
   the primary fix in isolation).
5. pass4_zon_bridge.py: narration-scan fallback given text containing
   "transformed"/"transformation" and world_rules' real "Tran" entry
   -> does NOT add "Tran" (word-boundary fix verified directly against
   the exact false-positive case found in f1bf22a).
6. pass4_zon_bridge.py: narration-scan fallback given text containing
   the real standalone word "tran" (constructed fixture, since it
   doesn't occur in current chapters 1-4) -> DOES still add "Tran" --
   proves the defensive fix doesn't disable real detection, only the
   substring false-positive class.
7. End-to-end (book 1, chapters 1-4, current vault): rerun and diff
   against the fresh baseline (dce6854) -- Lyaris present in chapter
   1 scene 1's @entities; "Tran" absent from all four chapters'
   @entities; entities_observed's content is otherwise unchanged from
   baseline (proves Pass 2 itself was never the defect, per the user's
   own stated check).
```

## Explicitly out of scope, per instruction

The scene-boundary/`mechanical_word_chunk` defect, the provenance-as-
fake-narration-segment contamination, and the missing
`semantic_environment_extractor` module are **not** touched by this
plan. This fix is scoped to the entity handoff only, to be proven
independently before any of the others are addressed.

## What was not done

No code changed. This is a plan only, including the one open
design-semantics question (what `@entities` means) flagged for
confirmation before implementation, per the same discipline as every
prior fix in this line of work.
