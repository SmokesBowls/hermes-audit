# MrLore door — locked architecture (design v1, spec only, no code)

Companion door to `engain_door.py` (Dragon → Mettaext). This document
locks the architecture for a symmetric door into MrLore (live checkout:
`/home/mytruelove/Downloads/_mrlore`, git remote `SmokesBowls/unclelore`,
frozen today at commit `a9ec5ff` per its own
`FREEZE_NARRATIVE_IDENTITY_CHECKPOINT.md`), per user instruction: build
a door for MrLore, and make sure **both doors swing both ways** —
Mettaext and MrLore should each be able to supply what the other
cannot, in both directions. Nothing below is implemented yet. All
facts are verified against the live checkout as of today; nothing is
invented.

## 0. Why this door, stated in the same terms as the Mettaext one

The Mettaext scene-packet audit (`09-15-2026-mettatext-scene-packet-
audit-for-godotsim.md`) found three real gaps: no place/structure
entity type, landmark extraction producing sentence fragments, and
spatial-relation detection blind to declarative "X was a Y" sentences.
MrLore does not fix any of those — it has no scene/spatial concept at
all (confirmed: no code path in `tools/` touches spatial layout,
`MRLORE_SCHEMA.md` §1 explicitly states MrLore "is not a runtime
engine, not a Godot service").

What MrLore has that Mettaext doesn't: a real identity/canon authority
layer. Verified in `wiki/registry/entities.yaml` (111 structured
entities) — `entity_id`, `aliases`, `incarnation_chain` (an entity
tracked across in-story identity changes, e.g. Geralt's own chain:
`The Nameless One → Geralt → Ragnarok → Man Who Flew Into The Sun → Mr
GPT`), `status`/`canon_state` (`candidate`/`provisional`, not yet
`approved`), cross-book/chapter appearance tracking, and deterministic,
explainable authority scoring (`schema/authority_scoring_rules.md`:
canon decisions +100, continuity findings ±20/-30/-10, source summaries
+5, registry existence +1 — a point system, not a confidence-vote
black box). `tools/continuity_audit.py` runs five deterministic
detectors (alias drift, timeline order violations, character presence,
location contradictions, world-state descriptor drift) and writes
real, reviewable `wiki/continuity/CONT-NNNN-*.yaml` conflict records.
This is exactly the "which of two contradictory descriptions is
authoritative" capability flagged as missing back when Mettaext-only
was in play (see "the door.md": "Or it retrieves two contradictory
descriptions and Dragon needs to know which is authoritative. Now we
have a real reason to bring in MrLore.") That moment has arrived.

## 1. Verified facts about the live checkout that change the design

These are load-bearing; skipping them would produce a door that
doesn't work against the real repo.

1. **Two-tier registry, not one.** `wiki/registry.md` (2,346 rows) is
   a flat index of *every* wiki stub page ever created —
   verified 100% of its rows are `canon_state: wiki_only` (checked:
   `awk` over the full file, zero exceptions). `wiki/registry/
   entities.yaml` (111 entries) is a smaller, separately-maintained
   *structured* symbol table (`REGISTRY_SYMBOL_TABLE_SCHEMA.md`:
   "the registry is the symbol table... the wiki is the readable
   output") with real identity machinery (aliases, incarnation chains,
   signal stats). These are not the same thing and a door must not
   conflate them.
2. **The structured registry has no location/faction entities at all.**
   `entities.yaml`'s 111 entries break down as 100 `character`, 6
   `concept`, 2 `unknown`, 2 `artifact`, 1 `species` — **zero**
   `location`, despite `ENTITY_STATE_SCHEMA.md` listing `location` as a
   valid `entity_type`. Meanwhile `wiki/locations/` alone has 493
   markdown stub pages (verified: `type: location`, `canon_state:
   provisional`, body is template placeholder text — "Stub: Pending
   behavioral/worldbuilding definition"). So the same asymmetry
   Mettaext has (people get structured treatment, places don't) exists
   inside MrLore too, one layer up: places exist as wiki stubs, not
   yet as registry-grade identity records. A MrLore door's location
   answers will be shallower than its character answers, verifiably,
   not just by assumption.
3. **Most of MrLore's own tooling is currently unrunnable from this
   checkout.** 15 scripts (`build_registry.py`, `promotion_eligibility_
   gate.py`, `authority_score_calculator.py`, `populate_registry.py`,
   `stb_scanner.py`, others — grepped exhaustively) hardcode
   `BASE_DIR = "/home/mytruelove/Downloads/obsidianburdenNov25/_mrlore"`,
   a path that **does not exist** (confirmed: `obsidianburdenNov25`
   exists, has no `_mrlore` child — the checkout now lives standalone
   at `/home/mytruelove/Downloads/_mrlore`). Only `mrlore_query.py` and
   `continuity_audit.py` resolve paths via `Path(__file__).resolve()`
   and are therefore portable regardless of checkout location. This is
   a pre-existing MrLore-side bug, not something the door introduces or
   should try to fix — but it hard-constrains the door design: **the
   door must never subprocess-invoke any BASE_DIR-hardcoded tool**,
   only read files directly or call the two portable, path-safe
   scripts. Flagging this to you as a separate, real defect worth a
   fix of its own at some point — not doing that fix now, out of scope
   for a door design.
4. **`mrlore_query.py` has no JSON mode.** It's `print()`-only, formatted
   for a human terminal (verified: reading its full 342 lines). Unlike
   Mettaext's door, which reads Mettaext's own on-disk JSON artifacts
   directly, a MrLore door should **not** shell out to `mrlore_query.py`
   and scrape its text output — that's fragile parsing of a display
   format never meant to be a contract. It should do exactly what
   `mrlore_query.py` itself does internally: read `entities.yaml`
   (`load_entities()`'s own segment-split/YAML-per-block parse,
   verified working) and `raw/math/identity_signal_stats.jsonl`
   directly. This mirrors the Mettaext door's own discipline of reading
   artifacts, not parsing another tool's stdout.
5. **No single MrLore "ingest" step exists.** Mettaext has one
   `pipeline_runner.py` the door can subprocess-invoke end to end.
   MrLore's equivalent is a multi-phase, partly human-reviewed chain
   (`ollama_ingest_cockpit.py` → `extract_candidates.py` →
   `identity_reviewer.py`/human review queue → `promotion_eligibility_
   gate.py` → `build_registry.py`), several steps of which write to a
   human review queue (`review/identity_review_queue.jsonl`) rather
   than completing unattended. **Door-owned decision: v1 of the MrLore
   door is query-only, no `ingest` operation.** This isn't a gap
   relative to the Mettaext door's design — it's the correct
   reflection of how MrLore actually works (deliberately
   human-in-the-loop for identity promotion, per its own schema docs).

## 2. What each door gives that the other structurally cannot

This is the "swing both ways" requirement, made concrete rather than
aspirational:

```text
                    Mettaext door (exists)      MrLore door (this design)
scene/spatial text        yes (raw prose,             no
                           scene boundaries)
place/structure           no (character-only          partial (wiki-stub
  as a concept              entity extractor)           locations exist,
                                                         not yet registry-grade)
identity across            no (per-scene only,          yes (incarnation
  in-story changes           no cross-chapter            chains, e.g. one
                             identity concept)            character across
                                                          5 aliases)
contradiction /            no                            yes (continuity_audit's
  authority resolution                                    5 deterministic
                                                          detectors + explainable
                                                          scoring)
raw witness text            yes (out_pass1_*.txt,         yes (wiki page
  with provenance            artifact_line)                Source Notes /
                                                           artifact snippets)
```

Concretely: Dragon asking "what does Falcon Ridge look like" goes to
Mettaext (scene prose, spatial attempt). Dragon asking "have we called
this character something else before, and which name is canonical"
goes to MrLore. Dragon asking "these two chapters disagree about
whether the archive collapsed — which one wins" is a question neither
door can answer alone today: Mettaext doesn't detect the contradiction
at all (no cross-chapter concept); MrLore's `continuity_audit.py` can
detect it as a `CONT-NNNN` record **if that audit has been run against
the relevant sources**, which is a real, separate, human-triggered step
— the door can only surface a conflict that already exists as a
recorded finding, it cannot run the audit on demand (see §1.5, no
ingest in v1).

## 3. "Both ways" — three distinct meanings, not one

The user's instruction covers more than "add a query door for MrLore
symmetric to the Mettaext one." Three separable things are in scope,
at three different levels of readiness:

1. **The new door itself, query-only, both directions of *use*.**
   Dragon can ask MrLore identity/authority questions the same way it
   asks Mettaext scene questions. This is what gets a frozen contract
   next (§4).
2. **Enhancement Mettaext could receive from MrLore** (not part of the
   door's v1 scope, a future integration): Mettaext's Gap 1 (no place/
   structure entity type) could be partially mitigated by having
   Mettaext's entity-normalization step consult MrLore's known
   place/faction/species names (from `wiki/locations/`, `wiki/
   factions/`, etc., or eventually a promoted registry) as a lookup
   dictionary — the same "known/spawnable" pattern `world_rules.json`
   already gives Mettaext for characters, extended via MrLore's wider
   canon. This is a real, plausible future improvement, not proposed
   for implementation now.
3. **Enhancement MrLore could receive from Mettaext** (also future,
   also not in v1 scope): MrLore's location entities currently sit as
   493 unstructured stub pages because nothing feeds them
   scene-grounded, provenance-tagged descriptions to compile from.
   Mettaext's raw scene prose (or, if it ever lands, its `=segments`/
   `scene_content_observed` channel) is a plausible additional *source*
   for MrLore's own extraction pipeline to ingest from — today MrLore
   only ingests directly from the vault's raw chapter text
   (`raw/chapters/`), the same original source Mettaext also reads
   independently. Feeding MrLore Mettaext's scene-segmented output
   instead of (or alongside) raw chapters could give MrLore's location
   compiler a running start. Flagged as a real, sound idea; not
   designed or scoped here — it is pipeline-internal work on MrLore's
   side, analogous to the Mettaext-internal fixes discussed for Gaps
   1–3, and shouldn't be conflated with the door itself, per the same
   discipline that kept the Mettaext door's contract separate from
   Mettaext's own pipeline improvements.

Items 2 and 3 are the "systems may need some work to enhance each
other" half of your instruction — captured here as scoped, named future
work, not attempted now. The door (item 1) is what gets built next and
is deliverable without either.

## 4. Non-negotiable rules for the MrLore door (v1)

Mirroring the Mettaext door's discipline, adapted to verified MrLore
reality:

- Standalone CLI/subprocess, same as `engain_door.py`. Caller supplies
  an explicit query; the door never scans or chooses what to look up.
- **Query-only. No `ingest`, no `promote`, no write path of any kind.**
  MrLore's own promotion pipeline stays human-gated, untouched.
- Reads `entities.yaml` and `identity_signal_stats.jsonl` directly
  (same files `mrlore_query.py` itself reads), never subprocess-invokes
  `mrlore_query.py` or any BASE_DIR-hardcoded tool (§1.3–1.4).
- Root resolution: env-var only, matching the `ENGAIN_ROOT` convention
  — a `MRLORE_ROOT` pointing at the `_mrlore` checkout root. Door-owned,
  not a CLI flag, same reasoning as the Mettaext door's frozen surface.
- stdout carries exactly one JSON document. No print-formatted human
  display — that's what `mrlore_query.py` is already for.
- Fail-closed on the two-tier registry ambiguity (§1.1): a query result
  must say plainly whether it's answering from the structured registry
  (`entities.yaml`, identity-grade) or the wiki-stub layer
  (`wiki/registry.md` + the entity's markdown page, `wiki_only`/stub
  grade) — never blend them into one undifferentiated answer, the same
  way the Mettaext door keeps `known`/`spawnable` visible rather than
  silently resolving them.

## 5. Status

Architecture locked at this document. Next step: freeze the exact
CLI/JSON contract (field-by-field, against `entities.yaml`'s real
schema and a real wiki-stub page's real frontmatter, the same way
`09-15-2026-engain-door-contract-v1.md` was built from three real-
chapter audits) — not yet written. No code written.
