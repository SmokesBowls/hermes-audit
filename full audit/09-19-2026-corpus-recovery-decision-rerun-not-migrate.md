# Decision: rerun Mettaext from the vault, don't migrate the legacy corpus

Records the decision made after `3d317a5`, `e2a6964`, and `3f58af9`
(the corpus-discovery, chapter-1-comparison, and logic-change
receipts). No code changed as part of this receipt — decision and plan
only.

## The decision

**Do not build a legacy-corpus adapter.** The disqualifying reason is
not schema drift, it's semantics: `pass2_entity_filter.py`'s
pre-`174ff0e` behavior *deliberately discarded* unknown entities
mentioned fewer than 3 times, and the legacy corpus predates
`extract_scene_objects()` entirely (per `3f58af9`). Adapting the old
files forward would carry those superseded decisions into current use,
not just old formatting.

**`legacy_pipeline_work/` is retained as audit/reference only:**

```text
legacy_pipeline_work/
  -> preserve (already git-tracked; not touched by this decision)
  -> never used as current Dragon evidence
  -> retained as a regression/history comparison oracle
```

## The plan, in order

**1. Fix five known current-pipeline defects first**, before any
full-corpus regeneration:

```text
1. Authored scene headings ("scene 001.1 —" / "scene 001.2 —",
   already present in the raw source text) are currently ignored by
   both the legacy (no split) and current (mechanical_word_chunk)
   boundary methods -- per e2a6964.
2. Provenance/header text (@scene_id, @boundary_method, etc.) is
   embedded as fake "narration" segments, confirmed to contaminate
   scene1's own environment_inference evidence -- per e2a6964.
3. A "Tran" false positive is persisted into scene1's own generated
   @entities array, not just a live-query artifact -- per e2a6964.
4. Lyaris -- explicitly named speaking in the chapter's opening
   dialogue setup -- is missing from every entity list checked, both
   eras -- per e2a6964.
5. Pass 5 reported "No module named 'semantic_environment_extractor'"
   for two of chapter 1's four generated scenes during this week's
   ingestion, caught but silently substituted -- per the design-
   principle receipt, 9205232.
```

**2. Once Chapter 1 passes cleanly against those five fixes**, wipe
only the *current* generated Mettaext outputs (`chapterroom/`,
`passroom/` -- never `legacy_pipeline_work/`) and regenerate the full
corpus from the present vault under the fixed pipeline:

```text
current vault -> current (fixed) Mettaext logic -> fresh, complete
evidence corpus -> Dragon / MrLore / downstream systems
```

**3. From then on, the intended lifecycle governs incremental
updates**, not full reruns:

```text
vault chapter unchanged  -> do nothing
vault chapter changed    -> rerun that chapter only
new chapter added        -> extract it
chapter removed          -> invalidate its evidence
```

**4. After the rebuild**, use the legacy corpus as a **test oracle**:
compare old vs. new chapter coverage and flag suspicious losses (an
entity, scene, or event present in the old extraction but absent from
the new one) — without ever treating the old output as authoritative
over the new one. This is a comparison/regression tool, not a fallback
data source.

## What was not decided here

Which specific implementation approach fixes each of the five defects
(e.g., exact heading-detection regex, where provenance metadata should
live instead, how to harden exact-name matching against substring
hits, why Lyaris specifically is missed, what actually broke
`semantic_environment_extractor`'s import) — that's the next planning
step, not decided in this receipt.

## What was not done, per the read-only discipline maintained throughout this investigation

No code changed. `legacy_pipeline_work/` was not touched. No wipe or
regeneration was performed. This receipt records the decision and
sequencing only.
