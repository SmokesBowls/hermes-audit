# Mettaext Boundary 6 checkpoint — real-chapter proof, all 9 checks pass

Final re-run of the same real chapter
(`book_04_sage_saga/016_the_choice_third_coming.md`) against the
Boundary 6 code (uncommitted working-tree state in EngAIn at time of
this run — `pass2_enhanced.py`, `pass3_merge.py`, `pass4_zon_bridge.py`,
`pass5_game_bridge.py` all changed since `174ff0e`). This closes the
Mettaext-repair side of the work; the door's original task resumes
from here.

## What changed since the last checkpoint

Confirmed by reading the diffs, not assumed:

- `pass2_enhanced.py`'s `.metta` writer now emits a structured Metta
  atom per candidate character, not just a free-text comment:
  `(entity Igigi :known false :spawnable false :classification "unknown" :mentions 6)`.
- `pass3_merge.py` gained a real parser for that atom
  (`_handle_entity`) and threads the result into
  `scene["entities_observed"]` as a proper list of dicts.
- `pass4_zon_bridge.py` propagates it into `=entities_observed` (both
  the current-format and legacy-rebuild code paths) and mirrors it
  into `=inferred.entities`. **Its `_is_spawnable()` default flipped
  from `return True # unknown entity: don't filter` to `return False
  # unknown entity: non-spawnable by default`** — this is the actual
  authority-hole fix, not merely additive.
- `pass5_game_bridge.py`'s `_is_spawnable()` got the identical default
  flip, and `entities_observed` now flows into both
  `metadata.entities_observed` and top-level `entities_observed` in
  `game_scenes/*.json`.
- (Found while checking the manifest-scope item below, not new to this
  session but not previously re-verified: `stageroom_manifest.py` was
  already rewritten in `174ff0e` to scope by matching `chapter_id`/
  `scene_id` against the requested `source_text_id`, replacing the old
  blind `rglob` over the whole output tree. This retroactively fixes
  the original audit's Finding 7 — the manifest is no longer a
  contaminated global receipt. Confirmed live below.)

## Live proof, all 9 checklist items

Ran `python3 -m tier3.mettaext.pipeline_runner
book_04_sage_saga/016_the_choice_third_coming.md`, then read the real
output files directly (not the console log alone):

| # | Check | Result |
|---|---|---|
| 1 | Igigi in structured `entities_observed` | **Pass** — `=entities_observed` in the final `.zonj.json`: `{"name": "Igigi", "known": false, "spawnable": false, "classification": "unknown", "mentions": 6}` |
| 2 | Anunnaki in `entities_observed` if detected | **Pass** — same list: `{"name": "Anunnaki", ..., "mentions": 4}` |
| 3 | Igigi NOT in `@entities` | **Pass** — `@entities: ["Pazuzu", "Tran", "Zephyr"]`, no Igigi |
| 4 | Anunnaki NOT in `@entities` unless authorized | **Pass** — not present, not in the 36-entity `world_rules.json` allowlist |
| 5 | Igigi NOT in `game_scene["entities"]` | **Pass** — `game_scenes/*.json` `entities`: `["Pazuzu", "Tran", "Zephyr"]` only |
| 6 | Pazuzu/Tran/Zephyr unchanged | **Pass** — identical 3 names, same as the pre-Boundary-6 run; `entities_observed` also independently lists `Zephyr` as `known: true, spawnable: true, classification: "known_spawnable"`, consistent with `@entities` |
| 7 | `chapter_id` still correct | **Pass** — `chapter.book004.016_the_choice_third_coming` throughout: `[CHAPTERROOM] CHAPTER_ID`, `@chapter_id`, `metadata.chapter_id`, manifest `source_text_id` |
| 8 | No false Beach/FirstAge | **Pass** — `Era: Unknown`, `Location: Unknown`, `region: "Unknown"`, `@where: "Realm/Physical/Unknown"` |
| 9 | Manifest scoped to this chapter | **Pass** — `mettaext_done_manifest.json`'s `artifacts.chapterroom`/`artifacts.passroom` contain exactly 5 + 16 entries, all `book004`/`016_the_choice_third_coming`-tagged. Zero entries from the still-on-disk `chapter.999_abc_smoke`, `engain_spatial_smoke_chapter`, `088_silent_tower`, `101`-`104` test chapters — confirmed those files still physically exist (`ls` checked directly) and are correctly excluded now, not merely absent |

Also noted: the key the door will actually need to read is
`=entities_observed` (equals-prefixed), not `entities_observed` — the
bare key from `pass3_merge.py`'s intermediate output does not survive
into the final `.zonj.json`; only the `=`-prefixed mirror does. Also
present redundantly at `=inferred.entities` (same content) and, in
`game_scenes/*.json`, at both `metadata.entities_observed` and
top-level `entities_observed`.

## Authority separation, as designed

For "Igigi," end to end on this real chapter:

```text
observed in source       -> entities_observed        YES (mentions=6)
known to world_rules      -> known                    false
runtime-spawnable         -> spawnable                false
reaches ZON projection     -> @entities               NO
reaches game scene actors -> game_scene["entities"]   NO
```

Three previously-collapsed truths (observed vs. approved-for-ZON vs.
runtime-actor) are now distinct fields instead of one boolean gate
that either kept or discarded a name. The dangerous prior default
(`unknown -> assume spawnable`, in both `pass4_zon_bridge.py` and
`pass5_game_bridge.py`) is gone, confirmed by reading both diffs
directly, not inferred from behavior alone.

## Status: Mettaext repair work closed here

All 9 checks pass on a real chapter. Per the standing plan, repair
work on Mettaext itself stops at this checkpoint. Door design resumes
with one upgrade available that didn't exist this morning: v1 can
still fall back to raw-text search as the general-purpose path
(unregistered names will never appear in `@entities`, by design — that
gate is intentional now, not a bug), but where `=entities_observed`
exists for a scene, the door can surface it too, clearly labeled as
*observed, not canon, not runtime-authorized* — never conflated with
`@entities`.
