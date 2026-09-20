# Traced why Mettaext ignores authored `scene NNN.x —` markers — root cause found, narrowest fix designed, no code changed

Read-only trace, per instruction. Locates the exact splitter, shows
precisely why each of its four methods misses the authored markers
against the real vault text, and designs the narrowest change —
without implementing it.

## The module

`tier3/mettaext/chapterroom/passB_scene_boundary_provider.py`,
`choose_boundaries()` (line 115), tries four methods in a fixed
priority chain, first non-empty result wins:

```text
1. split_by_scene_tags        -- literal line == "@scene"
2. split_by_markdown_headings -- line starts with "##" (not "###")
3. split_by_double_blank      -- 2+ consecutive blank lines
4. split_mechanical_words     -- ~900-word chunks (the fallback of last resort)
```

## Root cause, checked directly against the real authored source

Read the actual vault files Dragon's own request today resolved as
canonical (`/home/mytruelove/Downloads/obsidianburdenNov25/
book_01_book_of_genesis/00{1,2,3,4}_*.md`). Chapter 2's real structure:

```text
1: book 1
2: chapter 002-molten descent
3: (blank)
4: day 0
5: (blank)
6: scene 002.1 — molten descent
7: (blank)
8: scene meta:
9: location: ...
10: time: ...
11: participants: ...
12: focus: ...
13: continuity: ...
14: (blank)
15: [prose begins, single blank line between every paragraph]
...
151: end of chapter 002-molten descent
```

None of the four existing methods recognize any part of this:

```text
1. No line anywhere reads exactly "@scene" -- zero matches, not
   attempted-and-rejected, just never present in this convention.
2. No line starts with "##" -- "scene 002.1 — molten descent" is
   plain text, not a markdown heading. Zero matches.
3. split_by_double_blank requires blank_count >= 2. Every separator
   in this file -- between the marker and scene meta:, between scene
   meta: fields' trailing blank and prose, and between every prose
   paragraph -- is exactly ONE blank line. The whole file collapses
   into a single candidate chunk, and the function explicitly rejects
   single-chunk results (`return chunks if len(chunks) > 1 else []`,
   line 88). This is not a near-miss -- it is structurally guaranteed
   to reject every chapter written with consistent single-blank-line
   paragraph spacing, which is the norm across all of Book 1.
4. split_mechanical_words is therefore the one that always fires for
   these chapters -- chunking by raw word count with zero awareness
   of where "scene NNN.x —" or "scene meta:" fall. This is the
   direct, confirmed mechanism producing 4 mechanical chunks for
   chapters that are authored as 1 scene (Ch1, Ch2, Ch4), and 3 for
   a chapter authored as 7 (Ch3) -- pure coincidence of word count,
   unrelated to the real scene boundaries.
```

Confirmed the same for chapters 1, 3, and 4 directly (not inferred):
each opens with exactly one `book 1` / `chapter NNN-...` header pair,
followed by `day N`, blank, `scene NNN.x — <title>`, blank, `scene
meta:`, then fields, matching chapter 2's shape exactly. Chapter 3
has this pattern seven times, once per authored scene, each preceded
by its own incrementing `day N` line (`day 1` through `day 7`) --
confirming `day N` is scene-scoped, not chapter-scoped, since it
changes with every scene rather than appearing once at the top.

```text
Ch1: 1 marker (day 0)              Ch2: 1 marker (day 0)
Ch3: 7 markers (day 1 through 7)   Ch4: 1 marker (day 9)
```

Exactly matching the validation corpus already established:
`Ch1=1, Ch2=1, Ch3=7, Ch4=1`.

## The schema already anticipated this fix

Every scene entry `choose_boundaries()` produces already carries
`"authority_state"` (`"SCENE_BOUNDARY_MECHANICAL"` or
`"SCENE_BOUNDARY_PROPOSED"`) and `"authored_scene_boundaries_proven"`,
hardcoded `False` today because no existing method ever sets it
`True`. **This field exists specifically for the case this
investigation is about** — it's a placeholder for a proof tier that
was designed in, never implemented.

## Narrowest change: one new method, given top priority

Add `split_by_authored_scene_markers(lines)` and check it **first**,
ahead of all four existing methods (none of them can ever coexist with
it in the same file in practice, so ordering relative to `@scene`/`##`
specifically doesn't matter beyond "before the four heuristics that
exist only because this signal wasn't recognized yet"):

```python
_SCENE_MARKER_RE = re.compile(
    r'^scene\s+(?P<num>\d+)\.(?P<sub>\d+)\s+[—-]\s+(?P<title>.+)$',
    re.IGNORECASE,
)
_SCENE_META_HEADER_RE = re.compile(r'^scene meta:\s*$', re.IGNORECASE)
_SCENE_META_FIELD_RE = re.compile(r'^([A-Za-z][A-Za-z _]*):\s*(.*)$')
_DAY_HEADER_RE = re.compile(r'^day\s+\d+\s*$', re.IGNORECASE)
```

The em-dash-with-surrounding-spaces requirement (`\s+[—-]\s+`) is
deliberate: it's what distinguishes `scene 002.1 — molten descent`
from the chapter title line's own hyphen convention,
`chapter 002-molten descent` (no surrounding spaces) -- these must
never be confused.

**Five design decisions, stated explicitly rather than left implicit:**

1. **Chunk start includes the preceding `day N` line, not just the
   marker.** Confirmed each `day N` line sits exactly one blank line
   before its scene marker and changes per scene (chapter 3). If a
   scene marker is immediately preceded by (marker's index - 2) being
   a `day N` line, the chunk starts there instead of at the marker
   itself, so the day information is preserved in-band rather than
   silently dropped. `day N` should also be parsed into the scene's
   structured metadata (see below) as a `day` field, since it's
   scene-scoped evidence, not chapter-scoped.

2. **`scene meta:` parsing is generic key:value, not a fixed field
   list.** Chapters 1-4 show `location/time/participants/focus/
   continuity`; the user's Chapter 18 example adds `presentation` and
   `cutscene purpose` that don't appear in Book 1 at all. The parser
   must accept any `key: value` line (mirroring `pass1_explicit`'s
   already-generic `_parse_header_attrs()` -- same tolerant-by-design
   principle already used elsewhere in this codebase) and stop at the
   first blank line, not hardcode which keys exist.

3. **Scene meta fields become a new structured field on the scene
   packet, additive to the existing raw text.** Something like
   `scene["scene_meta"] = {"location": ..., "participants": ..., ...}`
   alongside the existing `text`. Critically, **the raw `scene meta:`
   lines must still flow into `text` unchanged, exactly as they do
   today** — this session's just-shipped manifestation feature
   (`fc3e3d1`) depends on it: `pass2_enhanced.py`'s
   `infer_presence_enhanced()` finds the `participants:` line by
   scanning Pass 1 segment text directly. If Pass B started stripping
   these lines out of `text` once it also captured them structurally,
   the presence-inference feature shipped today would silently stop
   working. This is a real interface dependency between today's two
   pieces of work, not a hypothetical one.

4. **New authority state for genuinely authored, non-inferred
   boundaries.** Reusing `"SCENE_BOUNDARY_PROPOSED"` would understate
   what this is — every other method that produces that state is
   still guessing. Set `authority_state: "SCENE_BOUNDARY_AUTHORED"`
   (a new value) and `authored_scene_boundaries_proven: True` only for
   scenes produced by this method, leaving the other four methods'
   states exactly as they are today.

5. **Fallback chain order otherwise unchanged.** If no authored
   markers are found in a chapter, the existing four-method chain
   runs exactly as it does today — this is additive, not a
   replacement, matching the plan's own "mechanical fallback used
   only when no authored scene markers exist."

Sketch of the only change to `choose_boundaries()` itself:

```python
method = "authored_scene_marker"
chunks = split_by_authored_scene_markers(lines)   # returns (start, end, text, scene_meta, day)

if not chunks:
    method = "scene_tag"
    chunks = split_by_scene_tags(lines)
# ... existing chain unchanged from here
```

## Validation corpus for this fix, once implemented

```text
Ch1 -> 1 scene packet   (currently 4, mechanical)
Ch2 -> 1 scene packet   (currently 4, mechanical -- or 2/3 depending
                          on which source copy/target-words setting
                          produced a given run; irrelevant once this
                          fires, since authored markers make word
                          count moot)
Ch3 -> 7 scene packets  (currently 3, mechanical)
Ch4 -> 1 scene packet   (currently 4, mechanical)
Ch18 -> 2 scene packets (2 authored headers observed in the pasted
                          example -- a good later regression case
                          precisely because it introduces scene_meta
                          keys (presentation, cutscene purpose) not
                          present anywhere in Book 1, exercising the
                          generic-parsing requirement from decision 2)
```

## What was not done

No code changed. This is the trace and the narrowest-change design
only, per instruction. Downstream Pass 2-5 behavior was not
re-examined beyond confirming the one real dependency named above
(decision 3); a full consumer trace of the new `scene_meta` structured
field, if one is wanted before implementation, has not been done.
