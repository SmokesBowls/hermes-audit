# Dragon Orchestration — frozen contract v1 (spec only, not implemented)

Freezes the component flagged as a real gap in the dependency audit:
nothing in any of the six original designs specified how Dragon combines
a bounded passage read with Mettaext and MrLore evidence into whatever
it reasons over before producing an `[EDITOR_REQUEST]`. This is that
specification — combination and authority-labeling only. **It does not
implement identity resolution, canon decisions, or interpretation.**
Dragon does the reasoning; this contract only governs what gets handed
to Dragon and how it's labeled. Not implemented.

## 0. What this combines, and from where

```text
bounded_reader.read_passage(passage_id)
    -> primary passage + context envelope        [09-17-2026-bounded-reader-contract-v1.md]

crosswalk.mettaext_lookup(passage_id)
    -> Mettaext evidence intersecting this passage's coordinates
       (entity_observation hits, spatial signals — whatever the
       crosswalk resolved for this range)

crosswalk.mrlore_lookup(passage_id)
    -> MrLore evidence/identity state intersecting this passage's
       coordinates, from whichever MrLore source is currently gated in
       (§2)
```

Orchestration's job is exactly: fetch all three, tag each item with
where it came from and what authority it actually has, and hand Dragon
one structured bundle. Nothing here decides what any of it *means*.

## 1. Output shape — the bundle Dragon actually reasons over

```json
{
  "passage": { /* bounded reader's own response shape, unchanged */ },
  "evidence": [
    {
      "producer": "mettaext",
      "producer_artifact_id": "entity_observation:Zephyr:scene.book008.047_mika.scene002",
      "authority": "observed_only",
      "content": { "name": "Zephyr", "known": false, "spawnable": false, "mentions": 6 }
    },
    {
      "producer": "unclelore",
      "producer_artifact_id": "art_132894a92d37",
      "authority": "legacy_proposal",
      "content": { "surface_form": "THREADS INCLUDED", "surrounding_quote": "..." }
    },
    {
      "producer": "tier1_mrlore",
      "producer_artifact_id": "claim.000997272d5bc07426410e2a",
      "authority": "unavailable_pending_integrity_repair",
      "content": null
    }
  ]
}
```

Every evidence item keeps its `producer` and its own `authority` label.
**Nothing gets flattened into one undifferentiated context blob** —
Dragon sees "Mettaext observed X," "unclelore proposes Y (legacy,
unverified)," and, currently, "Tier1 MrLore has nothing available"
as three distinctly labeled things, not one merged paragraph of
"facts."

## 2. Authority labeling rules (locked)

```text
authority values, in this system, mean exactly this and nothing more:

observed_only
    Mettaext's own evidence lane — a witnessed occurrence, never a
    canon claim. Matches Mettaext's own known:false/spawnable:false
    discipline already in force.

legacy_proposal
    unclelore-sourced evidence. Never auto-accepted as Tier1 authority,
    per explicit instruction. This label does not change once Tier1
    MrLore's integrity gates close — unclelore was never staged as the
    Tier1 canon-memory authority candidate (tier1/mrlore was, per its
    own MRLORE_TIER1_STAGING_LOCK.md); it simply becomes less necessary
    to lean on once Tier1 is ready, not promoted in place.

unavailable_pending_integrity_repair
    Tier1 MrLore evidence, while its known integrity defects remain
    open (17 duplicate scene IDs, 482 duplicate claim records, a
    16/16 health check that doesn't catch either — real findings from
    the 2026-09-16 Hermes side-by-side run). Orchestration returns
    this label instead of the evidence content itself; it does not
    silently pass through a claim that sits on a duplicate ID.

tier1_authority
    Reserved for Tier1 MrLore evidence once its RED gates close. Not a
    label this contract is authorized to emit today — named here so the
    schema doesn't need to change later, not because it's usable yet.
```

## 3. The gate, stated as a checkable condition, not a hardcoded date

```text
tier1_mrlore_gate_status: OPEN | CLOSED

While OPEN (today's real state):
    tier1_mrlore_lookup() results are labeled
    unavailable_pending_integrity_repair, content withheld.

Once CLOSED (requires, at minimum, the RED gates already named in the
2026-09-16 side-by-side report: zero duplicate chapter/scene/claim IDs,
temporal enrichment blocked by errors_count > 0, explicit accounting
for every deferred chapter):
    tier1_mrlore_lookup() results may carry authority: tier1_authority.
```

This is a real, checkable status this contract depends on — not a
permanent hardcoded branch and not something orchestration decides for
itself. Whoever closes those gates flips the status; orchestration only
reads it.

## 4. Non-negotiable rules

- No identity resolution, no canon decision, no contradiction
  resolution happens in orchestration. It combines and labels; Dragon
  reasons.
- Producer and authority are carried on every single evidence item,
  never summarized away.
- `unclelore` evidence is never labeled anything but `legacy_proposal`.
- `tier1_mrlore` evidence is never labeled `tier1_authority` while
  `tier1_mrlore_gate_status` is `OPEN`.
- Orchestration is read-only against the bounded reader and the
  crosswalk layer — same standing rule as everything upstream of it.

## 5. Open items, not resolved here

1. What happens when Mettaext and MrLore evidence for the same passage
   genuinely conflict — not addressed; that's downstream, Dragon's
   reasoning problem, or eventually a contradiction-detection system's
   (MrLore's own `continuity_audit.py`, or Paradox Machine for temporal
   conflicts) — not this contract's job to resolve.
2. Whether evidence outside the passage's own coordinate range but
   causally relevant (e.g. an earlier chapter establishing who Zephyr
   is) ever gets included — not scoped here; this contract only
   combines what intersects the *current* passage.

## Status

Contract frozen at this document. No code written. Depends on the
bounded reader (`09-17-2026-bounded-reader-contract-v1.md`) and the
crosswalk layer (`09-17-2026-crosswalk-layer-design-v1.md`) both
existing and populated for the target passage; does not require Tier1
MrLore's integrity repair to be *complete*, only its gate status to be
checkable and honestly reported.
