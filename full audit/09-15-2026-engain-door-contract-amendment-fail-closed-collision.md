# Amendment: fail-closed stem-collision handling for engain_door.py v1

Amends `09-15-2026-engain-door-contract-v1.md` (committed `d6ce833`).
Does not rewrite that document in place, per established discipline.
One correction only: how the door handles a Pass A filename-stem
collision. Everything else in the frozen contract stands unchanged —
captured stdout on `ingest`, the manifest treated as a receipt not a
registry, Pass 1 Spatial staying out of V1, the two clean evidence
lanes, no invented entity fields.

## The problem with the original design

The original contract (§10) detected a real collision correctly —
`out_passA_<stem>.json` is named from the bare input filename only, no
folder context, so two different sources sharing a stem (e.g.
`book_01/.../016_the_choice.md` and `book_04/.../016_the_choice.md`,
both producing `out_passA_016_the_choice.json`) collide at that path.

But the original contract then let `ingest` **proceed anyway** on a
detected collision, just with a `warning` field noting the overwrite.
That's backwards: the door correctly identified the danger and then
walked into it. If `ingest` proceeds, Mettaext genuinely overwrites the
other chapter's Pass A artifact at that path — a real, destructive,
silent-to-the-caller-unless-they-read-the-warning-field data loss.

## The fix: fail closed, per operation

```text
status:
  stem collision detected
  -> ok:true, ingestion_status:"stem_collision", collision details exposed
  -> never implies "safe to proceed"

query:
  stem collision detected
  -> ok:false, error:"SOURCE_STEM_COLLISION"
  -> never falls through to INGEST_REQUIRED (that would wrongly imply
     "just call ingest and this resolves itself" -- it would not,
     ingest refuses too)
  -> never reads or returns evidence from the artifact at that path

ingest:
  stem collision detected
  -> ok:false, error:"SOURCE_STEM_COLLISION"
  -> pipeline_runner is NEVER invoked
  -> no artifact is overwritten
```

One error code, `SOURCE_STEM_COLLISION`, used identically by both
`ingest` and `query` (not two near-synonymous codes) — a single
vocabulary for "this source cannot be resolved unambiguously against
what's on disk," resolvable only by a human or a future Mettaext-side
fix (folder-qualified Pass A filenames), never by retrying the door.

## Amended `status` schema (§2 supersession)

Adds a `collision` object exposing which other source is blocking,
read directly from the conflicting `out_passA_<stem>.json`'s own
verified `source_file` field — no new Mettaext read required, just
surfacing what was already being read:

```json
{
  "ok": true,
  "operation": "status",
  "authority": "evidence_only",
  "source": { "path": "/abs/path/given", "exists": true },
  "ingestion_status": "stem_collision",
  "chapter_id": null,
  "scene_count": null,
  "collision": {
    "expected_artifact": "output/chapterroom/out_passA_016_the_choice_third_coming.json",
    "conflicting_source": "/home/mytruelove/Downloads/obsidianburdenNov25/book_01_.../016_the_choice_third_coming.md"
  },
  "warning": "A different source with the same filename stem occupies the expected Pass A artifact path. This source has not been ingested and ingest will refuse until the collision is resolved."
}
```

`collision` is `null` whenever `ingestion_status` is not
`"stem_collision"`. `status` remains `ok:true` in every case — it's a
neutral fact-reporter and never fails, consistent with the original
contract.

## Amended `query` error (§4/§5 supersession)

Collision now short-circuits directly to its own error, before
`INGEST_REQUIRED` is even considered:

```json
{
  "ok": false,
  "operation": "query",
  "authority": "evidence_only",
  "error": "SOURCE_STEM_COLLISION",
  "message": "A different source occupies this chapter's expected Pass A artifact. Query refused; no evidence was read.",
  "detail": {
    "expected_artifact": "output/chapterroom/out_passA_016_the_choice_third_coming.json",
    "conflicting_source": "/home/mytruelove/Downloads/obsidianburdenNov25/book_01_.../016_the_choice_third_coming.md"
  },
  "source": { "path": "/abs/path/given" }
}
```

## Amended `ingest` error (§3/§5 supersession)

```json
{
  "ok": false,
  "operation": "ingest",
  "authority": "evidence_only",
  "error": "SOURCE_STEM_COLLISION",
  "message": "Refusing to ingest: a different source already occupies this chapter's expected Pass A artifact path. pipeline_runner was not invoked.",
  "detail": {
    "expected_artifact": "output/chapterroom/out_passA_016_the_choice_third_coming.json",
    "conflicting_source": "/home/mytruelove/Downloads/obsidianburdenNov25/book_01_.../016_the_choice_third_coming.md"
  },
  "source": { "path": "/abs/path/given" }
}
```

The `ingest` success schema's `warning` field (originally documented
for "proceeded despite collision, previous artifact overwritten") is
**removed** — that path no longer exists. `warning` in a successful
`ingest` response is now always `null`; a collision never reaches the
success schema at all.

## Amended error table (§5 supersession)

| Code | Ops | Meaning |
|---|---|---|
| `SOURCE_STEM_COLLISION` | ingest, query | `out_passA_<stem>.json` exists but its `source_file` does not exactly match `--source`. Fail-closed: `ingest` never invokes `pipeline_runner`; `query` never reads evidence. Resolvable only by a human (rename/relocate one of the colliding sources) or a future Mettaext fix (folder-qualified Pass A filenames) — never by retrying the door. |

All other rows from the original error table (`SOURCE_REQUIRED`,
`SOURCE_NOT_FOUND`, `METTAEXT_NOT_FOUND`, `INGEST_REQUIRED`,
`INGEST_FAILED`, `MANIFEST_INVALID`, `EVIDENCE_NOT_FOUND`,
`QUERY_FAILED`) are unchanged. `INGEST_REQUIRED` now strictly means
"genuinely not ingested yet, calling `ingest` will resolve it" —
collision is no longer folded into it, since for a collision calling
`ingest` will *not* resolve it.

## Amended exit-code contract (§9 supersession)

`SOURCE_STEM_COLLISION` is bucketed under exit code **1** (general
caller error), not **2** (`INGEST_FAILED`'s dedicated code). Exit 2 is
reserved specifically for "the subprocess itself broke, a retry might
help" — a stem collision is the opposite of that: retrying the door
changes nothing, only resolving the underlying naming ambiguity does.
Keeping it out of the retry-suggesting exit code preserves that
signal's meaning.

## What this does not require

No Mettaext repair today. This is entirely a door-side refusal around
a known, verified, still-present Mettaext limitation (Pass A's
filename doesn't carry folder context, even though its `chapter_id`
content does). The door protects both sides of the doorway: it won't
let an ambiguous request through, and it won't let Mettaext silently
overwrite a different chapter's evidence on the door's behalf.

## Status

Contract amended. Implementation of `engain_door.py` may now proceed,
against `09-15-2026-engain-door-contract-v1.md` as amended by this
document.
