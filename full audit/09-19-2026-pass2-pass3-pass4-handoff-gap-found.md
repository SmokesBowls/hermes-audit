# The architectural question, answered: Pass 3 is where the handoff actually breaks

Direct answer to: *"Why does Pass 4 independently reconstruct canonical
entities instead of consuming the entity candidates/classifications
already produced by Pass 2?"* Read-only, per instruction — no fix
applied. The answer changes where the real repair belongs.

## Pass 2's output format, checked directly

`pass2_enhanced.py` writes **only a human-readable `.metta` text file**
— no JSON. Its entity data is serialized as S-expression-style comment
blocks:

```text
(entity Lyaris :known true :spawnable false :classification "known_non_spawnable" :mentions 3)
```

This is not a rejected or bypassed format — it's the intended
interchange format for this stage (the file's own docstring says
*"Compatible with pass3_merge.py output format"*), meant to be
re-parsed downstream, not consumed as structured JSON directly.

## Pass 3 *does* correctly parse Pass 2's entities — confirmed by reading the parser

`pass3_merge.py` has a real, working `_handle_entity()` function that
correctly parses every field from the `(entity ...)` s-expression —
`known`, `spawnable`, `classification`, `mentions` all round-trip
correctly. **Pass 2's classification is not lost or ignored at the
parsing stage.**

## The actual gap: `merge_to_zonj()` never writes `@entities`

Read `merge_to_zonj()` in full (`pass3_merge.py:585-634`, the function
that builds the final per-scene zonj dict). The entity-related lines,
verbatim:

```python
if p2.entities:
    scene["entities_observed"] = [
        dict(info) for name, info in sorted(p2.entities.items())
    ]
```

**That's the only place Pass 2's parsed entities go.** There is no
corresponding line anywhere in this function that derives or copies a
value into `scene["@entities"]`. Confirmed by reading the entire
function body — `@entities` is never assigned, under any condition.
This is exactly why pass3's own zonj file for chapter 1 scene 1 showed
`@entities: null` while `entities_observed` correctly contained
Pass 2's real, classified candidates (Aeon, Ethereal, Keepers, Korath,
Lyaris, Pelagor, Tiamat, Vaelith).

## What this means for Pass 4's behavior

Pass 4's own `extract_entities()` docstring states its intended
priority order explicitly: *"1. If @entities already populated:
normalise + filter spawnable. 2. Otherwise: collect from segment
speakers/inferred, then enrich via narration text scan and scene_tags
injection."* **This reads as a deliberately-designed fallback for
cases where some upstream stage hasn't populated `@entities` yet** —
not code written to deliberately override or second-guess Pass 2.
Given that Pass 3 *never* populates `@entities` (not "sometimes," per
the code just read — never, unconditionally), **Pass 4's fallback path
is not an edge case; it is the only path that ever executes, on every
scene, every chapter, every run.** The narration-scan substring bug
traced in `f1bf22a` only matters because this fallback is always
active — if `@entities` were populated upstream, `_normalise_and_filter()`
would run instead, and the substring-matching code would never be
reached at all for entity purposes.

## Direct answer to the architectural question

**Pass 4 does not "bypass" Pass 2's newer classification logic by
design or by oversight of Pass 2's authority — it was never given
Pass 2's result in the form it needs.** Pass 2's real work
(known/spawnable/classification per entity) correctly survives all the
way to `entities_observed` in Pass 3's output. It simply never gets
projected into the separate `@entities` field Pass 4 (and apparently
other consumers) expect to find already populated. Pass 3 is the
missing link, not Pass 2 or Pass 4 individually.

## This reframes the two candidate fixes from the prior receipt

```text
A. Patch Pass 4's narration-scan match (substring -> word-boundary)
   Still worth doing on its own merits if that scan has any real
   independent purpose beyond "no @entities was found upstream" (e.g.
   catching an entity that's present in prose but never became a
   pass2 candidate for some reason) -- but per this trace, it is
   currently ALWAYS exercised as a fallback, not as a supplementary
   check on top of good pass2 data, because nothing ever supplies
   that data.

B. Carry Pass 2's classified result forward into @entities
   Now identified precisely: add one thing to pass3_merge.py's
   merge_to_zonj() -- populate scene["@entities"] from the already-
   correctly-parsed p2.entities (e.g. the known: true subset,
   canonical-name deduplicated), the same data entities_observed
   already carries. This would make pass4's existing
   "if @entities already populated" branch actually fire, routing
   through _normalise_and_filter() instead of the narration scan for
   every scene going forward -- eliminating the "Tran" trigger
   condition at its source rather than hardening the fallback that
   currently substitutes for it.
```

**B looks like the real architectural repair, not just the cleaner
one.** Fixing pass3's gap doesn't just avoid the Tran-class substring
bug — it also means Lyaris (and any other pass2-classified candidate)
would finally reach `@entities` too, since `entities_observed` already
has her. A alone would still leave every scene's `@entities` being
independently reconstructed from raw text, discarding pass2's careful
work every time, just with a less buggy reconstruction method.

Not decided here: whether A is still warranted *in addition* to B (as
a safety net, or because narration-scan genuinely catches something
pass2's regex-based candidate extraction sometimes misses) — that's
a real design question for whoever implements this, not resolved by
this trace.

## What was not done

No fix applied to `pass3_merge.py`, `pass4_zon_bridge.py`, or anywhere
else. This is a read-only trace of the Pass 2 → Pass 3 → Pass 4
handoff, exactly as requested, preserved for the fix-planning step that
follows.
