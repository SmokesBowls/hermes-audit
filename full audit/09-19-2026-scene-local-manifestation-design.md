# Where scene-local manifestation should be derived and carried: a design, not a patch

Answers the follow-up to `7fae863`: define where scene-local
manifestation evidence should be derived and carried through Mettaext
-> Pass3 -> Pass4 -> GodotSim, using Chapter 1's Vaelith and Pelagor as
the acceptance cases. `world_rules.spawnable` stays the global render-
capability gate, untouched. Director/adaptation override stays outside
Mettaext entirely. **No code changed in this step.**

## Ground truth this design is built against

Read the real, current, post-handoff-fix artifact for the exact scene
in question:
`tier3/mettaext/stageroom/output/passroom/scene.book001.001_the_ethereal_vigil.scene001/scene.book001.001_the_ethereal_vigil.scene001.zonj.json`

The textual evidence already sitting in `=segments` is decisive and
specific, not vague:

```text
line 166 (Vaelith): "Vaelith, the most pragmatic of their assembly,
  projected her awareness through the Veil—that friction-space
  between ethereal and physical..."

line 89-92 (Pelagor): "Vaelith, 'Pelagor,'" ... "buried deep within
  those massive forms was the unmistakable resonance of Pelagor
  essence."

line 311 / 347 (Pelagor, supporting): "life signatures" / "analyzing
  the energy signatures"
```

This is exactly the kind of textual signal Pass 2 already keys other
inferences off of (`infer_emotions_enhanced`, `infer_actions_enhanced`
scan segment text for keyword evidence near a character name) — the
same extraction *pattern* used for emotion/action/thought applies
directly to manifestation. This is not a new paradigm for this
codebase, just a new evidence category.

## What stays fixed, per instruction

- `world_rules.json`'s `spawnable` flag remains the sole, global,
  static "can this identity ever be rendered as a physical actor"
  capability gate. Nothing proposed here adds scene-awareness to it,
  changes its values, or makes it conditional.
- `@entities` (Pass 3's spawnable-safe projection, fixed in `bcdad29`)
  keeps meaning exactly what it means today. It is **not** redefined.
  `tier2/godotsim`'s existing assumption about it is undisturbed.
- Director/adaptation override — "spawn Vaelith anyway, as a
  translucent effect" — is never computed, stored, or represented
  anywhere inside `tier3/mettaext`. It is a decision that consumes
  Mettaext's evidence; Mettaext never encodes it.

## Where it's derived: Pass 2, alongside the other per-segment inferences

`tier3/mettaext/passroom/pass2_enhanced.py` already runs a family of
structurally identical passes over the same `List[Segment]` +
`Dict[str, Character]` — `infer_emotions_enhanced`,
`infer_actions_enhanced`, `infer_thoughts_enhanced`,
`infer_relationships`. Manifestation classification belongs in this
same family: `infer_manifestation_enhanced(segments, characters)`.

Two keyword lexicons, evidenced directly against this scene's own
text, mirroring the existing `EMOTION_KEYWORDS`/`ACTION_KEYWORDS` dict
style:

```python
REMOTE_MANIFESTATION_KEYWORDS = {
    "projected her awareness", "projected his awareness",
    "extended her awareness", "extended his awareness",
    "resonance of", "essence", "energy signature", "life signature",
    "consciousness", "through the veil", "distributed awareness",
    "sensed", "detected",
}

EMBODIED_MANIFESTATION_KEYWORDS = {
    # direct physical contact/motion verbs attributed to the named
    # entity in the same or adjacent segment -- overlaps deliberately
    # with the existing physical subset of ACTION_KEYWORDS (knelt,
    # approached, retreated, huddled) rather than duplicating a
    # second, competing verb list.
}
```

Classification per character, per scene: `"embodied"` if embodied-
keyword evidence found in a segment naming the character;
`"remote"` if remote-keyword evidence found and no embodied evidence
found; `"unestablished"` if neither — the conservative default,
matching this codebase's existing philosophy of preserving an honest
"we don't know" state rather than guessing (the same spirit as
`pass2_entity_filter.py` preserving `known:false` entities instead of
discarding them). **Absence of embodiment evidence must never be
treated as embodiment** — this is the entire point of the exercise.

Output: extend `Character` (line ~140) with
`manifestation: Optional[str] = None` and
`manifestation_confidence: Optional[float] = None`, and extend
`write_metta()`'s entity atom (line ~621) to emit them when set:

```text
(entity Vaelith :known true :spawnable true :classification "known_spawnable"
  :mentions 1 :manifestation "remote" :manifestation_confidence 0.85)
```

## Where it's carried: Pass 3, as new keys on `entities_observed`, plus a new derived field

`pass3_merge.py`'s `_handle_entity()` (line 424) parses the two new
tokens the same tolerant way it already parses `:known`/`:spawnable`.
**Critical distinction, stated explicitly because it changes the
default logic**: a token that is *absent* (old `.metta` file, feature
didn't exist yet) is not the same thing as Pass 2 *evaluating* the
entity and finding no evidence. Only the latter is `"unestablished"`.
The former means this scene has no manifestation data at all.

`entities_observed[]` entries (already a generic `dict(info)` dump,
`merge_to_zonj()` line 627) gain `manifestation` and
`manifestation_confidence` automatically once Pass 2 populates them —
this is additive to the record, not a schema break, but it **does**
invalidate the exact key-set assertion pinned in
`test_pass3_pass4_entity_handoff.py:136-138`
(`test_entities_observed_unchanged_by_this_fix`, asserting
`{"name", "known", "spawnable", "classification", "mentions"}`) —
flagging this now so it isn't a silent surprise at implementation
time; that test's key-set will need updating as part of the same
patch, not treated as a regression.

New derived field, alongside the existing `@entities` projection
(`merge_to_zonj()`, right after line 646):

```python
scene_has_manifestation_data = any(
    "manifestation" in info for info in p2.entities.values()
)
if scene_has_manifestation_data:
    manifested_names = sorted(
        name for name, info in p2.entities.items()
        if info.get("spawnable") and info.get("manifestation") == "embodied"
    )
    scene["@entities_manifested"] = manifested_names   # may be []
```

**This deliberately does not follow `@entities`'s own "omit the key if
empty" convention (line 645: `if spawnable_names:`).** `@entities`
omits itself when empty so Pass 4's segment-scan fallback can still
run — there is always a legitimate reason to keep looking. But an
empty `@entities_manifested` when manifestation data exists is not "no
data yet," it's a real, confirmed answer: *nothing in this scene is
embodied*. Conflating "we checked and found nothing" with "we never
checked" here would silently defeat the entire feature for scenes just
like chapter 1 scene 1, where the correct list genuinely is empty.
Key-presence, not list-length, is the signal a scene has manifestation
data at all — the same presence-vs-content distinction Pass 4 already
relies on elsewhere (`existing_id and isinstance(existing_segments,
list) and existing_segments` at `pass4_zon_bridge.py:679`, and
`entities_obs = scene.get(...) or scene.get(...)` at line 688, though
that second one uses truthiness rather than presence and would need
the same tightening if this pattern is extended there too).

## Where it's carried further: Pass 4 passthrough

Confirmed against the real artifact above that current-pipeline scenes
(`id`/`segments`, no `@id`/`=segments`) always take
`pass4_zon_bridge.py`'s **"Legacy path: rebuild from a raw ZONJ
narrative object"** branch (line 698+) — the one that already
passes `entities_observed` through unchanged (line 713, 736-738). Add
the identical treatment, keyed on presence not truthiness:

```python
if "@entities_manifested" in scene:
    zon_canonical["@entities_manifested"] = scene.get("@entities_manifested")
```

placed beside the existing `entities_obs` passthrough. The other
branch (`existing_id and ... "=segments"`, line 677-696 — currently
unreached by any current-pipeline data, per this session's earlier
trace) should get the same line for symmetry, since nothing prevents
some future producer from emitting canonical-shaped ZONJ directly.

`extract_entities()`/`_normalise_and_filter()` do **not** need a
manifestation-aware counterpart: `@entities_manifested` is by
construction always a subset of `@entities` using names Pass 3 already
canonicalized, so it is pure passthrough data, never re-derived in
Pass 4.

## Where it's consumed: GodotSim, as a preference, not a replacement

`tier2/godotsim/bridge_integration.py`'s `bridge_entities_for_scene()`
currently does:

```python
raw_entities = scene_doc.get("entities", [])
if not raw_entities:
    raw_entities = scene_doc.get("@entities", [])
```

Proposed replacement logic (not implemented):

```python
if "@entities_manifested" in scene_doc or "entities_manifested" in scene_doc:
    raw_entities = scene_doc.get("@entities_manifested",
                                  scene_doc.get("entities_manifested", []))
else:
    raw_entities = scene_doc.get("entities", [])
    if not raw_entities:
        raw_entities = scene_doc.get("@entities", [])
```

This is a **preference with a compatibility fallback**, not a
replacement of `@entities`'s meaning: scenes regenerated with the new
Pass 2 inference get the tighter, scene-accurate list; scenes not yet
regenerated keep behaving exactly as they do today (spawn everything
globally spawnable) until they are. `filter_bridge_entities_by_declared_ids()`
downstream of this needs no change — it was already confirmed
(`7fae863`) to key off the same `("entities", "@entities")` pair, so it
naturally continues to be a no-op scope guard either way, not a
manifestation check itself; it does not need to learn about the new
field for this design to work.

## Where director/adaptation override lives instead

Not in `tier3/mettaext` at all, by design. It is a decision made
*after* `bridge_entities_for_scene()` (or by a wrapper around it) that
takes a completely separate input — an explicit list from Dragon or a
scene-authoring override config — and unions it with whatever
`bridge_entities_for_scene()` already decided to spawn:

```text
final_spawn_list = bridge_entities_for_scene(scene_doc, ...) 
                    ∪ director_override_entities
```

`director_override_entities` never comes from a Mettaext artifact, and
a director's choice to spawn Vaelith anyway must never be written back
into `world_rules.json`, `@entities`, or `@entities_manifested` — those
three stay pure evidence/capability records. This preserves the
three-authority separation already established this session: MrLore =
identity, Mettaext = scene-local evidence, Dragon = director decision.

## Acceptance cases: Chapter 1, scene 1, Vaelith and Pelagor

```text
entities_observed (after Pass 2 gets the new inference, fresh rerun):
  Vaelith: known:true, spawnable:true,
           manifestation:"remote", manifestation_confidence:~0.8-0.9
           (evidence: "projected her awareness through the Veil")
  Pelagor: known:true, spawnable:true,
           manifestation:"remote", manifestation_confidence:~0.8-0.9
           (evidence: "resonance of Pelagor essence", "energy signatures")

@entities (unchanged, world_rules.spawnable-derived, global):
  ["Pelagor", "Vaelith"]   <- must NOT shrink; proves world_rules.spawnable
                              was not touched

@entities_manifested (new field, this scene):
  []                        <- key PRESENT (manifestation data exists for
                              this scene), list EMPTY (neither entity is
                              embodied here) -- this is the field doing
                              its job, not a bug

bridge_entities_for_scene() result for this scene, once GodotSim is
updated to prefer @entities_manifested when present:
  zero Entity3D objects for Vaelith or Pelagor
```

## What's still open, not decided here

- The exact keyword lexicons above are a starting proposal grounded in
  this one scene's text; they need validation against the rest of book
  1 before implementation, the same way `EMOTION_KEYWORDS`/
  `ACTION_KEYWORDS` were clearly hand-tuned against real prose over
  time.
- **No positive control exists in this scene** — all six Aeon Keepers
  are ethereal and Pelagor is remote-sensed, so chapter 1 scene 1 has
  zero embodied spawnable entities by design. A genuinely embodied,
  known-spawnable character elsewhere in book 1 must be located and
  used as a regression case before implementation, to prove the
  classifier isn't degenerately always-remote. Not yet located or
  verified in this session.
- Confidence thresholds, and what (if anything) should happen with a
  low-confidence "embodied" call, are not decided.
- Whether `filter_bridge_entities_by_declared_ids()`'s truthiness-based
  reads elsewhere in `pass4_zon_bridge.py` (the `entities_obs = ... or
  ...` pattern) should also be tightened to presence-based checks is
  noted but out of scope for this feature specifically.

## What was not done

No code changed anywhere in this step, per instruction. This is a
design for a future patch, not a patch.
