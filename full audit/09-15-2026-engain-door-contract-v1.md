# engain_door.py — frozen interface contract v1 (spec only, not implemented)

Freezes the CLI/JSON interface Dragon will depend on, before any code
is written. Builds on the locked architecture in
`09-15-2026-mettatext-door-design-v1.md` and every verified fact from
the three real-chapter audit passes (`09-15-2026-mettatext-*-proof.md`,
`...-refactor-reverify.md`, `...-boundary6-checkpoint.md`), current as
of Mettaext commit `105c9dd`'s checkpoint. **No field below is
invented without a verified source; where a value is a door-owned
design choice rather than a Mettaext fact, it's marked "door-owned."**

## 0. Non-negotiable rules (recap, not new)

- Standalone CLI/subprocess. Dragon/caller always supplies an explicit
  `--source` path. The door never scans or chooses chapters.
- `ingest` is explicit only, never triggered by `query`.
- `query` is read-only; an unprocessed source returns `INGEST_REQUIRED`,
  never an implicit ingest.
- **stdout carries exactly one JSON document, and nothing else.**
  Mettaext's own subprocess chain is chatty (`pipeline_runner.py`'s
  children print `[PASS1] Done...`, `[PASS1_SPATIAL] signal_count...`,
  etc., directly to inherited stdout) — the door's `ingest` operation
  MUST invoke it with captured output (`subprocess.run(..., capture_output=True)`)
  and relay that captured text to the door's own **stderr**, never let
  it leak to stdout. This is an implementation requirement, not
  optional.
- ENGAIN_ROOT resolution is env-var only in V1 (`ENGAIN_ROOT` process
  env var), matching the established launch convention in "the
  door.md". No `--engain-root` CLI flag in V1 — keeps the frozen CLI
  surface exactly as specified below, nothing added.

## 1. Exact CLI arguments (frozen, nothing beyond this in V1)

```bash
python3 engain_door.py status --source /absolute/path/to/chapter.md
python3 engain_door.py ingest --source /absolute/path/to/chapter.md
python3 engain_door.py query  --source /absolute/path/to/chapter.md --query "Igigi"
```

- `--source` — required for all three operations. Absolute path.
  Door does not resolve relative paths, does not search, does not
  guess.
- `--query` — required for `query` only. Non-empty string. Case
  sensitivity is not configurable in V1 (always case-insensitive
  substring match, per the locked v1 design) — no `--case-sensitive`
  flag.
- No `--timeout`, `--max-hits`, or `--engain-root` flags in V1. These
  exist as **door-internal constants** (documented in §6/§9), not
  exposed on the CLI, to keep the frozen surface identical to what's
  specified here. Revisit in a later version if a real need appears.

## 2. `status` — stdout JSON schema

Read-only, cheap, never runs ingestion, never fails on "not ingested"
(that's a valid, reportable state, not an error).

```json
{
  "ok": true,
  "operation": "status",
  "authority": "evidence_only",
  "source": { "path": "/abs/path/given", "exists": true },
  "ingestion_status": "not_ingested",
  "chapter_id": null,
  "scene_count": null,
  "warning": null
}
```

When already ingested:

```json
{
  "ok": true,
  "operation": "status",
  "authority": "evidence_only",
  "source": { "path": "/abs/path/given", "exists": true },
  "ingestion_status": "existing",
  "chapter_id": "chapter.book004.016_the_choice_third_coming",
  "scene_count": 2,
  "warning": null
}
```

When a filename-stem collision is detected (see §10 for the
verified mechanism):

```json
{
  "ok": true,
  "operation": "status",
  "authority": "evidence_only",
  "source": { "path": "/abs/path/given", "exists": true },
  "ingestion_status": "stem_collision",
  "chapter_id": null,
  "scene_count": null,
  "warning": "A different source with the same filename stem was previously ingested at the expected passA path. This source has not been ingested."
}
```

`chapter_id` — from passA's own `chapter_id` field (verified:
`chapter.book004.016_the_choice_third_coming`, folder-context-aware,
door-owned derivation). `scene_count` — from `scene_packets_index.json`'s
`scene_count` field (verified field name).

## 3. `ingest` — stdout JSON schema

```json
{
  "ok": true,
  "operation": "ingest",
  "authority": "evidence_only",
  "source": { "path": "/abs/path/given", "exists": true },
  "ingestion_status": "created",
  "chapter_id": "chapter.book004.016_the_choice_third_coming",
  "scene_count": 2,
  "warning": null
}
```

- `ingestion_status: "existing"` — the door detected this exact source
  was already ingested (passA's `source_file` field matches
  `--source` exactly) and **skipped calling `pipeline_runner`
  entirely** — idempotent short-circuit, avoids the 5+ subprocess
  chain for no reason. This is a door-owned optimization; Mettaext
  itself has no such guard (verified — `chapterroom_runner.py` has no
  "already processed" check).
- `ingestion_status: "created"` — the door ran `pipeline_runner`,
  it exited 0, and the door independently re-read `out_passA_*.json` +
  `scene_packets_index.json` afterward to confirm the artifacts
  actually landed before reporting success. A reported success is
  never taken on the subprocess's exit code alone.
- `warning` — non-null only when ingest proceeded despite a detected
  stem collision (§10), noting that a previously-ingested, *different*
  source's `out_passA_<stem>.json` was overwritten.
- **`"failed"` never appears as an `ingestion_status` value in this
  success schema.** A failed ingest is always reported through the
  error schema (§5, `ok:false`, `error:"INGEST_FAILED"`). "failed" is
  listed as one of three conceptual outcomes of calling `ingest` only
  to be complete about what can happen when you call it — it is
  realized as an error object, never as `ok:true` with a failed status
  string.

## 4. `query` — stdout JSON schema (success)

```json
{
  "ok": true,
  "operation": "query",
  "authority": "evidence_only",
  "source": {
    "path": "/abs/path/given",
    "chapter_id": "chapter.book004.016_the_choice_third_coming"
  },
  "ingestion_status": "existing",
  "query": "Igigi",
  "hit_count": 2,
  "truncated": false,
  "hits": [
    {
      "kind": "raw_text",
      "scene_id": "scene.book004.016_the_choice_third_coming.scene001",
      "chapter_id": "chapter.book004.016_the_choice_third_coming",
      "artifact": "output/passroom/scene.book004.016_the_choice_third_coming.scene001/out_pass1_scene.book004.016_the_choice_third_coming.scene001.txt",
      "artifact_line": 13,
      "segment_type": "dialogue",
      "text": "\"The orbital mechanics are conclusive,\" he whispered to the assembled Igigi council, his voice carrying the weight of cosmic certainty."
    },
    {
      "kind": "entity_observation",
      "scene_id": "scene.book004.016_the_choice_third_coming.scene001",
      "chapter_id": "chapter.book004.016_the_choice_third_coming",
      "artifact": "output/passroom/scene.book004.016_the_choice_third_coming.scene001/scene.book004.016_the_choice_third_coming.scene001.zonj.json",
      "name": "Igigi",
      "known": false,
      "spawnable": false,
      "classification": "unknown",
      "mentions": 6
    }
  ]
}
```

Field notes, all grounded in verified structure:

- `"ingestion_status"` for `query` is **only ever `"existing"`** in a
  success payload. `"created"` is invalid here (query never ingests);
  an unprocessed source never reaches a success payload at all — it
  returns the `INGEST_REQUIRED` error instead (§5).
- `artifact` — path relative to `stageroom_root`, matching the
  convention `mettaext_done_manifest.json` itself already uses
  (verified: `"output/passroom/..."`, not absolute) — stays stable
  across machines/ENGAIN_ROOT locations.
- `artifact_line` — the 1-indexed line number **within that specific
  `out_pass1_<scene_id>.txt` file**. Deliberately NOT called
  `source_line` or `chapter_line`: verified that this numbering space
  does not match the original source chapter's own line numbers
  (pass1's internal numbering includes the metadata/front-matter
  preamble; passB's `boundary_start_line`/`boundary_end_line` are the
  chapter-original numbers and are a different space entirely). Naming
  it `artifact_line` keeps that distinction visible in the schema
  itself rather than relying on a comment someone might not read.
- `segment_type` — `"narration"` or `"dialogue"`, taken directly from
  the verified `{type:...}` tag on that line.
- Entity-observation fields (`name`, `known`, `spawnable`,
  `classification`, `mentions`) are exactly and only the fields
  verified present in a real `=entities_observed` entry — no
  `confidence`, `line`, or `canon_status` invented; those do not exist
  in this structure.
- `hit_count` / `truncated` — door-owned. See §6 for the cap.

## 5. Error schema (uniform shape, all operations)

```json
{
  "ok": false,
  "operation": "query",
  "authority": "evidence_only",
  "error": "INGEST_REQUIRED",
  "message": "Source has not been ingested. Call `ingest` before `query`.",
  "detail": null,
  "source": { "path": "/abs/path/given" }
}
```

| Code | Ops | Meaning |
|---|---|---|
| `SOURCE_REQUIRED` | all | `--source` missing or empty. Checked before touching the filesystem. `source.path` is `null`. |
| `SOURCE_NOT_FOUND` | all | `--source` given but does not exist on disk. |
| `METTAEXT_NOT_FOUND` | all | `ENGAIN_ROOT` unset, or `$ENGAIN_ROOT/tier3/mettaext/pipeline_runner.py` doesn't exist. |
| `INGEST_REQUIRED` | query | Source status resolved to `not_ingested` **or** `stem_collision` (§10) — for this source, no valid ingestion exists. `detail` explains which of the two, when it's a collision. |
| `INGEST_FAILED` | ingest | `pipeline_runner` subprocess exited non-zero, or timed out, or exited 0 but the door's post-run verification (re-reading `out_passA_*.json`) still found nothing. `detail` carries a bounded (few-KB) tail of captured stderr for diagnosis — never the full log. |
| `MANIFEST_INVALID` | ingest (fatal); status/query (degraded, see below) | For `ingest`: after a subprocess-reported success, the door's own post-run manifest read (`mettaext_done_manifest.json`) was missing or not parseable as JSON — a more specific diagnosis than the general `INGEST_FAILED`. For `status`/`query`: the manifest is read only as *optional informational context* (never as the authoritative ingestion signal, see §10) — if it's broken there, the operation does **not** fail; the informational field is simply omitted/null. `MANIFEST_INVALID` as a hard error is `ingest`-only. |
| `EVIDENCE_NOT_FOUND` | query | Chapter resolves to `existing` and `scene_packets_index.json` lists scenes, but **none** of them have a readable `out_pass1_<scene_id>.txt`. Total evidence loss for an apparently-ingested chapter. (Partial loss — some scenes readable, others not — is not an error: query proceeds over what's readable and adds a non-fatal `warning` naming the skipped scene_ids.) |
| `QUERY_FAILED` | query | Catch-all for the matching phase itself: an expected artifact exists but isn't parseable (malformed JSON/encoding), or `--query` is present but empty after trimming. |

## 6. Raw-text matching rules (lane A)

1. Enumerate scenes for the resolved `chapter_id` via
   `scene_packets_index.json`'s `packets[].scene_id` (verified field).
2. For each scene, read
   `output/passroom/<scene_id>/out_pass1_<scene_id>.txt` (verified
   naming pattern, confirmed on the real chapter).
3. Each line has the verified form `{type:TAG[, key:value]} REST` —
   verified tags present: `narration`, `dialogue` (with a
   `speaker:NAME` sub-field), `blank`, `scene_header`. Treat this as
   an **allowlist** — only `narration` and `dialogue` lines are ever
   eligible; an unrecognized future tag is excluded by default, not
   included.
4. Find the **last** line tagged `scene_header` in the file (verified:
   there can be two or more — the engine `@key:value` preamble's
   closing marker, then possibly authored front matter, then a second
   marker before real prose). Every line at or before that index is
   excluded unconditionally, regardless of tag.
5. Match: case-insensitive substring match of `--query` against the
   REST text of each remaining eligible line — plain `.lower() in
   .lower()`, no regex, no tokenization, no word-boundary logic. A
   query for "Ig" matching inside "Igigi" is accepted V1 behavior, not
   a bug — matches the locked "no fuzzy search, no embeddings" v1
   decision exactly.
6. One hit per matching **line**, not per occurrence within a line.
7. Cap: **200 raw_text hits per query call** (door-owned constant),
   applied deterministically in scene-order then line-order. If hit,
   set `"truncated": true`.
8. **Explicitly out of scope for V1**: `out_pass1_spatial_<scene_id>.json`
   is not searched. Its `source_text` entries are a content-filtered
   subset of the same sentences already in `out_pass1_*.txt` — indexing
   both would violate the dedup rules in §8 by surfacing the same
   sentence twice under different provenance framings. This is a
   deliberate scope line, not an oversight, and the best candidate for
   a future V2 lane (it carries `relation`/`subject_hint`/`object_hint`
   that plain text search doesn't).

## 7. Structured `=entities_observed` normalization rules (lane B)

1. Same per-scene enumeration as lane A.
2. Read exactly one file per scene:
   `output/passroom/<scene_id>/<scene_id>.zonj.json` — the **final
   Pass 4 artifact** (verified naming: literally `<scene_id>.zonj.json`,
   confirmed against the real chapter's on-disk filename). This is
   deliberately not `zonj_<scene_id>.json` (the Pass 3 *intermediate*
   file, different prefix convention, verified to exist alongside it
   as a distinct, earlier-stage file).
3. Read the `=entities_observed` key (verified: equals-prefixed; the
   bare `entities_observed` key from Pass 3's intermediate output does
   not survive into this final artifact). Absent/empty is not an
   error — many scenes have no candidate entities at all (verified on
   both toy smoke chapters).
4. Match: case-insensitive substring match of `--query` against each
   entry's `name` field.
5. Emit exactly the four verified per-entity fields
   (`name`, `known`, `spawnable`, `classification`, `mentions`) plus
   door-added provenance (`scene_id`, `chapter_id`, `artifact`). Never
   backfill fields the structure doesn't have.

## 8. Evidence deduplication rules

1. **Never** read `=inferred.entities` in addition to
   `=entities_observed` — verified identical mirror, same file, same
   content. Lane B reads `=entities_observed` only.
2. **Never** read `game_scenes/<scene_id>.json`'s `entities_observed`
   or `metadata.entities_observed` — verified Pass 5 mirrors of the
   same Pass 4 data, unchanged in transit. Reading the Pass 4
   `.zonj.json` once is sufficient and authoritative.
3. **Never** search `out_pass1_spatial_*.json` in addition to
   `out_pass1_*.txt` — §6 rule 8.
4. Within lane A, one hit per matching line, never per occurrence
   (§6 rule 6).
5. **No cross-lane deduplication.** A term appearing in both a
   narration sentence and `=entities_observed` legitimately produces
   one `raw_text` hit and one `entity_observation` hit in the same
   response — these are different evidence types (verbatim quote vs.
   structured classification), not duplicates, and both are wanted.
6. No cross-call state. Each `query` invocation is independent and
   stateless — no caching, no memoization across separate CLI
   invocations, consistent with "standalone CLI/subprocess."

## 9. Exit-code contract

| Code | Meaning |
|---|---|
| `0` | `ok: true`. Includes `status` reporting `not_ingested`, `ingest` reporting `existing` (idempotent skip), and `query` returning zero hits — all valid, successful outcomes. |
| `1` | `ok: false`, everything except `INGEST_FAILED` — `SOURCE_REQUIRED`, `SOURCE_NOT_FOUND`, `METTAEXT_NOT_FOUND`, `INGEST_REQUIRED`, `MANIFEST_INVALID`, `EVIDENCE_NOT_FOUND`, `QUERY_FAILED`. The JSON `error` field is the authoritative discriminator; this exit code just means "did not complete, see stdout." |
| `2` | `ok: false`, `error: "INGEST_FAILED"` specifically — the one case involving an actual subprocess failure or timeout, distinct enough that a caller might branch on exit code alone (e.g., "maybe retry") without parsing JSON first. |

`ingest`'s internal timeout: **180 seconds** (door-owned constant, not
a CLI flag in V1 — see §1). `pipeline_runner` chains 5+ subprocesses
per scene with no timeout of its own (verified, original design doc's
open item); the door supplies the bound Mettaext doesn't.

## 10. Which concrete artifacts each operation reads

**`status`** (no subprocess, no writes):
- `output/chapterroom/out_passA_<source.stem>.json` — existence +
  parse. `chapter_id` for identity; `source_file` field for
  stem-collision detection (see below).
- `output/chapterroom/scene_packets/<chapter_id>/scene_packets_index.json`
  — only if passA exists; `scene_count` field.

**Idempotency/collision mechanism (door-owned, built from two verified
facts):** Pass A's output filename is `out_passA_<input_filename_stem>.json`
— named from the raw input stem only, **no folder/book context in the
filename itself** (verified: real run produced
`out_passA_016_the_choice_third_coming.json`, even though the real
`chapter_id` inside it is folder-aware —
`chapter.book004.016_the_choice_third_coming`). Two different source
files sharing a stem (plausible across different `book_NN_*` folders,
not yet proven to occur but not ruled out either) would collide at this
path. The door's guard: after finding `out_passA_<stem>.json`, read its
`source_file` field (verified present, absolute path) and require an
**exact match** against `--source`. Match → `existing`. No match →
`stem_collision`, treated as not-ingested-for-this-source, with a
warning surfaced.

**`ingest`**:
- Same two reads as `status` first, to decide skip vs. run.
- If running: subprocess `python3 -m tier3.mettaext.pipeline_runner
  <source>` (`cwd=$ENGAIN_ROOT`), stdout+stderr captured, bounded by
  the 180s internal timeout.
- Post-run: re-reads the same two files as `status` to confirm the
  artifacts actually landed and extract `chapter_id`/`scene_count` —
  never trusts the subprocess exit code alone.
- Does **not** use `mettaext_done_manifest.json` for the
  success/failure determination (it's a single file, global,
  overwritten on every run — verified, and still true after the
  Boundary 6 checkpoint: it correctly *scopes* to whichever chapter
  was ingested most recently, but still only reflects the most recent
  one, not a registry of everything ever ingested). May read it only
  for the optional post-run cross-check that can raise
  `MANIFEST_INVALID` (§5).

**`query`**:
- Same two `status` reads first — must resolve to `existing`, else
  `INGEST_REQUIRED`.
- `scene_packets_index.json`'s `packets[].scene_id` to enumerate
  scenes.
- Per scene, lane A: `output/passroom/<scene_id>/out_pass1_<scene_id>.txt`.
- Per scene, lane B: `output/passroom/<scene_id>/<scene_id>.zonj.json`,
  `=entities_observed` key only.
- Never reads: `out_pass1_spatial_*.json`, `zonj_<scene_id>.json`
  (Pass 3 intermediate), `*.zon` (human-readable mirror),
  `game_scenes/*.json`, `=inferred.entities`.

## Status

Interface frozen at this document. No code written. Next step, when
authorized: implement `engain_door.py` in the dragon3d avatar repo
against exactly this contract, then prove it live against
`book_04_sage_saga/016_the_choice_third_coming.md` for all three
operations before calling it done.
