# Yes — Mettaext's extraction logic changed substantially after the legacy corpus was generated

Direct answer to "didn't we change a few things in Mettaext recently...
that old results should be wiped and rerun." Checked EngAIn's own git
history for `tier3/mettaext/`. The answer is yes, and it's more than a
schema change — real extraction *behavior* changed, on a date well
after the legacy corpus (`legacy_pipeline_work/`, dated 2026-05-27
through 2026-06-24) was produced.

## The commit history

```text
2026-06-25  41957e3  add chapterroom bridge for game proof 003
2026-06-25  9c1515f  fix passroom bridge tagged-line parser
2026-06-25  49be3a1  add game proof 005 passroom to topologist seam
2026-07-03  36c8240  godotmanifext
2026-09-15  174ff0e  mettaext refactor
2026-09-15  f58edff  mettaext number 7
2026-09-16  d01c8f2  working on it
```

All seven postdate the legacy corpus's latest file
(`out_pass2_001_the_ethereal_vigil.metta`, 2026-06-24). The two that
matter most for "should old results be trusted as-is" are the pair on
**2026-09-15** — four days before this week's live tests, and roughly
three months after the legacy corpus was generated.

## The entity-filtering behavior actually changed, not just the schema around it

`174ff0e` ("mettaext refactor") touched
`tier3/mettaext/passroom/pass2_entity_filter.py` directly. The diff,
in full for the relevant section:

```diff
         if world_rules_loader.is_known(clean):
+            char.known = True
             if _is_runtime_renderable(clean):
-                filtered[clean] = char
+                char.spawnable = True
+                char.classification = "known_spawnable"
+            else:
+                char.spawnable = False
+                char.classification = "known_non_spawnable"
+            filtered[clean] = char
             continue

         ...
-        # Weak frequency filter stays. This is noise suppression, not ontology.
-        if char.mentions < 3:
-            continue
+        # Unknown entity candidate passing noise checks: preserve evidence as UNKNOWN
+        char.known = False
+        char.spawnable = False
+        char.classification = "unknown"
+        filtered[clean] = char

         print(
-            f"[pass2_entity_filter] UNKNOWN ENTITY BLOCKED: '{clean}' "
+            f"[pass2_entity_filter] UNKNOWN ENTITY PRESERVED: '{clean}' "
             f"(mentions={char.mentions}). Classified as unknown (non-spawnable)."
         )
```

**Before this commit:** any unrecognized entity mentioned fewer than 3
times was silently dropped entirely (`if char.mentions < 3: continue` —
never added to the output at all, logged as "UNKNOWN ENTITY BLOCKED").

**After this commit:** that frequency threshold was removed. Every
entity candidate that passes basic noise checks is now preserved and
explicitly classified (`known`/`spawnable`/`classification`), regardless
of mention count.

**This means the `known`/`spawnable`/`classification` fields found only
in current output (per the chapter-1 comparison, `e2a6964`) are not
just new metadata bolted onto the same underlying extraction — they
replaced a real exclusion rule.** The legacy corpus was produced by a
version of Mettaext that actively threw away low-mention entities
before they ever reached the output file. That is very likely part of
why entity lists in the legacy corpus look sparse — it's not only
incomplete extraction, it's *designed* to omit anything below a
frequency floor that no longer exists in the current code.

## A genuinely new extraction capability was also added the same day

`f58edff` ("mettaext number 7") added an entirely new
`extract_scene_objects()` function and `SCENE_OBJECT_PATTERNS` table to
`pass2_enhanced.py` — pattern-based detection of non-character scene
content (settlements, landmarks, structures, terrain features:
"Falcon Ridge," "Star Needle Spire," "perimeter wall," "storage cache,"
"stream," "waterfall," "plateau," etc.). **This capability did not
exist in any form when the legacy corpus was generated.** It's a
plausible part of why this week's live chapter-1 evidence packet came
back with rich environmental detail (crystalline lattice, temporal
archives, vrill infrastructure) that a comparably-aged legacy chapter
would have no mechanism to produce.

## Net answer

**Yes, and it's a stronger case than "the schema moved."** Two
independent, dated, real logic changes on 2026-09-15 mean the legacy
corpus reflects entity-filtering and scene-content-extraction behavior
that Mettaext no longer has. Even a perfect schema/location adapter
that successfully read `legacy_pipeline_work/`'s old files would still
be serving output produced by superseded extraction logic, not a
faithful stand-in for what the current pipeline would produce if
pointed at the same 110 chapters today.

This sharpens (without contradicting) the prior two receipts:

- `3d317a5` established the corpus exists and the door can't see it.
- `e2a6964` established the current schema carries information
  (`known`/`spawnable`) the legacy schema has no field for at all.
- **This receipt establishes why**: that field's absence in legacy
  isn't just a missing column — it's the visible trace of an entity-
  filtering rule that got removed. The two other passes touched the
  same day (`pass3_merge.py`, `pass4_zon_bridge.py`, `pass5_game_bridge.py`,
  plus `master_pipeline.py`/`engain_ingest.py`/`narrative_to_game.py`
  orchestration) were not individually diffed here — flagged as likely
  containing more of the same class of change, not confirmed line by
  line.

## What this means for "wipe and rerun" as a question, not a decision

This investigation does not decide whether to wipe and rerun the full
110-chapter legacy corpus, migrate it as-is, or something else — that
remains the user's call, per the same discipline as the prior two
receipts. What it does establish is that **"migrate the old files"** and
**"rerun extraction with the current pipeline"** are not equivalent
options producing the same content in different shapes — the second
one uses meaningfully different logic than what produced the first
one. Whichever recovery path is chosen, it should be chosen knowing
that, not discovered afterward.

## What was not done

No file was ingested, rebuilt, migrated, or modified. `pass3_merge.py`,
`pass4_zon_bridge.py`, `pass5_game_bridge.py`,
`chapterroom_index_runner.py`, and `passB5_environment_detector.py`'s
own diffs were not individually read in full — named as likely relevant,
not verified line by line, to keep this investigation to the specific
question asked.
