# Mettaext refactor re-verification — same chapter, post-fix code

EngAIn commit `174ff0e` ("mettaext refactor") landed changes to
`pipeline_runner.py`, `pass2_entity_filter.py`, `pass2_enhanced.py`,
`pass3_merge.py`, `pass4_zon_bridge.py`, `pass5_game_bridge.py`. Ran
the exact same chapter as
`09-15-2026-mettatext-real-chapter-ingest-proof.md`
(`book_04_sage_saga/016_the_choice_third_coming.md`) again, live, to
check which of that document's findings the refactor actually
addresses. Two of three are fixed; the third is fixed at the wrong
layer — real for the door's purposes, nothing changed.

## Fixed — Correction 4 (chapter_id mismatch)

`pipeline_runner.py` now passes the real `chapter_id` variable
straight to `stageroom_manifest --source-text-id`, instead of
re-deriving from `chapter_path.stem`. Confirmed live:

```
[CHAPTERROOM] CHAPTER_ID = chapter.book004.016_the_choice_third_coming
...
SOURCE_TEXT_ID=chapter.book004.016_the_choice_third_coming
```

Matches on this run. The done manifest's `source_text_id` is now
trustworthy for this id-derivation path — though the door should still
prefer reading `passA`'s own output directly rather than depending on
the manifest, since the manifest remains a single global file that
only reflects the most recent run (see the original audit's Finding 7,
untouched by this refactor).

## Fixed differently than expected — Correction 3 (hardcoded era/location)

`pipeline_runner.py` no longer hardcodes `--era FirstAge --location
Beach`. Now: `era = passA_data.get("era_hint") or "Unknown"`,
`location = "Unknown"` (unconditionally). Confirmed live: `Era: Unknown
/ Location: Unknown`, `@where: "Realm/Physical/Unknown"`.

This resolves the actual problem (a specific *wrong* place was being
asserted as fact) but doesn't add real location extraction — every
chapter's `region`/`@where` will now read "Unknown" rather than a false
"Beach." Correct behavior for the door: still don't treat `region`/
`@where` as content, same conclusion as before, just for a more honest
reason now (it's absent, not fabricated).

`environment`/`terrain_family` are unaffected by this change (they
were never wired to the `--location` arg) and still vote correctly
off real content — confirmed unchanged: `"cosmic"`, same
`environment_inference` block, same keyword evidence, same metadata-line
noise in the evidence list as the pre-refactor run.

## Partially fixed, not where it matters yet — Correction 2 (world_rules entity gating)

`pass2_entity_filter.py` no longer deletes unknown entities outright.
Confirmed live — the log line itself changed:

```
[pass2_entity_filter] UNKNOWN ENTITY PRESERVED: 'Igigi' (mentions=6). Classified as unknown (non-spawnable).
[pass2_entity_filter] UNKNOWN ENTITY PRESERVED: 'Anunnaki' (mentions=4). Classified as unknown (non-spawnable).
```

(Previously: `UNKNOWN ENTITY BLOCKED`.) And `Igigi`/`Anunnaki` do now
survive into the `.metta` file's plain-text comment block:

```
; ---- Discovered Characters ----
; Anunnaki: 4 mentions, traits: none
; Igigi: 6 mentions, traits: none
; Zephyr: 7 mentions, traits: none
```

**But `@entities` in the final `.zonj.json` and `entities` in
`game_scenes/*.json` are unchanged: still exactly `["Pazuzu", "Tran",
"Zephyr"]`, same three names as the pre-refactor run.** The
`known`/`spawnable`/`classification` fields added to the `Character`
dataclass in `pass2_entity_filter.py` are never serialized anywhere —
not into the `.metta` output (which only prints a name + mention count
comment, no classification tag), not into `zonj_*.json` (pass3's
intermediate output — checked, no `characters` key at all), and not
into the final `.zonj.json`/`game_scenes` JSON. The classification
exists only as an in-memory Python attribute for the duration of one
process.

**Consequence for the door, unchanged from before:** any JSON- or
`@entities`-based lookup still cannot see "Igigi" or "Anunnaki," same
as pre-refactor. The only place they're recoverable at all right now
is the `.metta` file's free-text comment section (not meant for
machine parsing) or raw narration text (`out_pass1_*.txt`,
`out_pass1_spatial_*.json`'s `source_text`) — which is where the
door's search was already going to have to look, per the original
audit. This refactor is real progress (nothing is silently deleted
anymore, and a future pass could serialize the preserved classification
into JSON cheaply since the data already exists in-memory) but it does
not yet change what the door can rely on.

## Net effect on the door design

No change to the v1 query design's conclusion: search raw narration
text and `pass1_spatial` `source_text`, not structured `@entities`.
Two things did get strictly better and should be taken advantage of
once the door is built: `source_text_id`/`chapter_id` derivation is
now reliable from the manifest for a freshly-run chapter (Correction 4
fixed), and `region`/`@where` no longer lies with a specific wrong
place (Correction 3 fixed, if less informatively).
