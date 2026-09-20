# Correction: drop the `day N` folding rule — `time:` is just another scene_meta key

Supersedes decision 1 ("chunk start includes the preceding `day N`
line") from `7120eef`
(`09-19-2026-scene-boundary-splitter-traced.md`). Rejected before
implementation. Decisions 2-5 from that receipt are unchanged and not
re-derived here. **Still no code changed**, and this does not touch
`book_04_sage_saga` — that editing work belongs to whatever tool
produced the Chapter 019/020 transcript pasted alongside this
correction, not to this trace/design work.

## Why decision 1 was wrong to build

It special-cased a transitional artifact. Book 1's `day N` lines exist
only because those chapters haven't been migrated to full authored
timestamps yet. The Chapter 020 scene-meta blocks just proposed for
`book_04_sage_saga` already show the durable form directly:

```text
time: year 14,032 (fifteen years after the Great Flood in scene 019.2)
```

`time:` sitting as an ordinary key inside `scene meta:`, not a separate
structural line the splitter has to notice and reach backward for. A
splitter rule built around `day N` would already be wrong for this
newer content, and would become dead weight the moment Book 1 finishes
the same migration — exactly the "obsolete rule" risk flagged.

## The corrected, durable contract

```text
scene NNN.x — <title>      <- defines the authored boundary, nothing else
    scene meta:            <- the immediately following block belongs to it
        location: ...
        time: ...          <- opaque authored value, preserved exactly
        participants: ...
        focus: ...
        continuity: ...
        presentation: ...
        <any future key>   <- accepted without splitter changes
    <prose, until the next authored scene marker or end of chapter>
```

`time:` gets no special parsing at all in the splitter or in the
generic `scene_meta` key:value parser from `7120eef`'s decision 2 — it
is stored as a plain string, same as `location`/`focus`/`continuity`.
If a structured `time` breakdown is ever wanted, that is a separate,
later concern (a timeline/calendar interpreter reading `scene_meta.time`
after the fact), never something the splitter or its metadata parser
needs to understand. Splitter recognizes scenes; metadata parser reads
key:value pairs generically; a timeline system — if and when one
exists — interprets what `time:` means. Three separate concerns, kept
separate, matching the plan's own reasoning.

## What happens to Book 1's existing `day N` lines without a special rule

Not ignored, not erased — just not specially recognized. Chunk
boundaries are now purely marker-to-marker (`start = marker's own
line`, `end = next marker's line, or end of chapter`). A `day N` line
that currently sits *before* a scene marker (all of Book 1's cases)
falls into whichever span it's physically inside:

```text
Chapter opening (day 0 before scene 001.1 in Ch1/Ch2, day 9 before
  scene 004.1 in Ch4): excluded from every scene chunk, same bucket as
  the chapter's "book 1" / "chapter NNN-title" header lines above it --
  chapter-level material that was never scene prose to begin with.

Between two scenes (Ch3's "day 2" through "day 7", each sitting after
  one scene's prose and before the next scene's marker): lands as a
  trailing, orphaned line at the END of the PRECEDING scene's prose
  text -- e.g. scene 003.1's chunk ends with a stray "day 2" sentence
  tacked on after its real content, and scene 003.2 begins clean at
  its own marker.
```

Neither case corrupts anything or requires the splitter to know what a
`day N` line even is. This is exactly the "tolerated for compatibility,
not defining the format" behavior asked for — Book 1 gets slightly
untidy trailing text on 6 of its 7 chapter-3 scenes until those
chapters are migrated to authored `time:` fields, and nothing more.

## Updated splitter contract, restated in full

```text
1. scene NNN.x — ... defines the authored boundary.
2. The immediately following scene meta: block belongs to that scene.
3. time: is an opaque authored value, preserved exactly as written --
   no parsing, no special structural role. (Corrected here.)
4. Metadata parsing accepts any key: value line generically -- new
   keys (presentation, cutscene purpose, and whatever comes later)
   require no splitter change. (Unchanged from 7120eef.)
5. Scene prose continues until the next authored scene marker or end
   of chapter. (Unchanged.)
6. Mechanical/heuristic fallback applies only when no authored scene
   markers exist in the chapter at all. (Unchanged.)
7. authority_state: "SCENE_BOUNDARY_AUTHORED" /
   authored_scene_boundaries_proven: true for markers produced this
   way. (Unchanged.)
8. The raw scene meta: lines still flow into segment text unchanged,
   alongside the new structured scene_meta field -- still required so
   this session's manifestation feature (fc3e3d1) keeps finding
   participants: by scanning segment text directly. (Unchanged.)
```

## What was not done

No code changed. `book_04_sage_saga/019_the_sacrafice.md` and
`020_the_collapse.md` were not read or touched by this session — the
Chapter 019/020 edit log and Chapter 020 breakdown proposal quoted
alongside this correction came from a different tool/session's work,
relayed here only as evidence that `time:`-inside-`scene-meta` is
already the real, live direction new chapters are being written in.
