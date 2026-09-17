# Crosswalk layer: existing Mettaext/MrLore evidence → Publisher coordinates (design v1, spec only, no code)

Maps existing evidence onto the book-wide token coordinates locked in
`09-17-2026-narrative-publisher-design-v1.md` and `09-17-2026-canonical-
tokenizer-rule-v1.md`, **without changing any source artifact or any
system's underlying reasoning** — additive only, per the standing
instruction. Grounded against three real, distinct provenance shapes
pulled from disk today, not assumed to be uniform.

## 0. Real evidence: three provenance shapes, not one

Pulled one real record from each system before designing anything.

**`unclelore`** (`raw/artifacts/batch_20260518_214757.jsonl`, real file):

```json
{
  "artifact_id": "art_132894a92d37",
  "surface_form": "THREADS INCLUDED",
  "source_line": 3,
  "source_span": "3-3",
  "chapter": "book_01_book_of_genesis_ch001",
  "source_file": "/home/mytruelove/Downloads/obsidianburdenNov25/_mrlore/raw/chapters/book_01_book_of_genesis_001_the_ethereal_vigil.md",
  "source_hash": "39a5e85c50d7dbb533cf87d1fa9db8aa2cde0c2ce232b180ef909c379086aca7"
}
```

`source_line` refers to the **original chapter `.md` file directly**
(`source_file` points at `raw/chapters/*.md`, not a derived
intermediate), and carries its own `source_hash`. This is the cleanest
of the three cases.

**Mettaext** (`out_pass1_scene.book008.047_mika.scene002.txt`, read
earlier today): hits carry `artifact_line`, scoped to that one
scene-packet text file, which starts with ~10 lines of header/preamble
before real prose — verified: artifact_line 11 is the scene's first
prose line, while the header's own `@boundary_start_line: 56` claims
that same line is chapter-original line 56. **Not a fixed arithmetic
offset**: this session already caught `@boundary_end_line: 131` while
the same file's actual content runs to line 145 — a real, observed
inconsistency, not a hypothetical one. Scene-local, indirect.

**`tier1/mrlore`** (`/tmp/mrlore_side_by_side/tier1_review/mrlore/
claims/proposed_claims.jsonl`, real output from the Hermes side-by-side
run, still on disk):

```json
{
  "claim_id": "claim.000997272d5bc07426410e2a",
  "source_scene": "scene.book018.096_violet_convergence.scene002",
  "source_line": 86,
  "source_span": {"start": 86, "end": 86},
  "subject": "Violet",
  "predicate": "present_in"
}
```

`source_line` here is **scene-packet-scoped** (`SOURCE_SCENE`/
`source_scene`, same `scene.book0XX.0YY_name.sceneNNN` naming
convention Mettaext uses) — same indirection problem as Mettaext, not
a direct chapter-file line number.

## 1. Core mechanism: crosswalk via the Publisher's own line index, not re-derivation

Once the Publisher has segmented a chapter (per its own design), it
already knows, for every line of the **original chapter file**, which
word range that line falls in (word_start/word_end per §2 of the
tokenizer rule). The crosswalk's job for each existing citation is
therefore: **resolve the citation's line reference to a chapter-
original line number, then look that number up in the Publisher's
already-built index.** No new segmentation logic — this reuses the
Publisher's index as the single source of truth, exactly the
"one canonical ruler" principle the tokenizer rule exists to protect.

## 2. Per-system resolution, three different confidence levels

**`unclelore` — direct lookup, high confidence.** `source_line`
already indexes the original chapter file (confirmed by `source_file`
+ matching `source_hash`). Crosswalk = look up that line number
directly in the Publisher's index for that file. No text matching
needed. Tag: `exact_line_match`.

**Mettaext and `tier1/mrlore` — content-matched, medium confidence.**
Both are scene-packet-scoped, and Mettaext's own `boundary_start_line`
anchor is demonstrably not arithmetic-safe (§0). The reliable mechanism
is **content matching, not arithmetic**: take the exact text of the
cited scene-packet line (Mettaext's `out_pass1_*.txt` line text, or
tier1/mrlore's equivalent scene-packet text), and locate that exact
string within the Publisher's already-segmented original chapter file.
A unique exact match resolves the citation with tag `content_matched`.
No match, or more than one match, is **not guessed at** — tagged
`unresolved`, reported by citation ID, with the attempted search text
included so a human or a later pass can resolve it, never silently
dropped and never silently assigned to the wrong location.

## 3. Output shape — additive, never touches the source

```json
{
  "crosswalk_id": "xw.unclelore.art_132894a92d37",
  "source_system": "unclelore",
  "source_citation_id": "art_132894a92d37",
  "resolution": "exact_line_match",
  "chapter_original_line": 3,
  "passage_id": "book_001.chapter_001.passage_0001",
  "word_start": 12, "word_end": 15
}
```

Written to a new, separate file per chapter
(`published/crosswalk/<chapter_id>.crosswalk.jsonl`, one line per
existing citation) — never edits `raw/artifacts/*.jsonl`, never edits
any Mettaext `out_pass1_*`/`.zonj.json` file, never edits any
`tier1/mrlore` claim file. MrLore's and Mettaext's own reasoning,
registries, and claim records are read-only inputs to this process,
exactly as instructed.

## 4. Non-negotiable rules

- Read-only against every existing artifact from every system. This
  process only ever writes new `crosswalk/*.jsonl` files.
- No arithmetic-only resolution for scene-scoped citations (Mettaext,
  tier1/mrlore) — content matching only, given the demonstrated
  unreliability of the boundary-line anchor alone.
- Every citation gets a `resolution` tag (`exact_line_match`,
  `content_matched`, or `unresolved`) — never silently treated as
  equally precise, and `unresolved` is a valid, expected, reported
  outcome, not a failure to hide.
- The crosswalk depends on the Publisher having already segmented the
  relevant chapter. A citation for an unpublished chapter is
  `unresolved: chapter_not_yet_published`, not blocked/errored.

## 5. Open items, not resolved here

1. Exact content-matching algorithm (byte-exact substring vs. whitespace-
   normalized) isn't specified — needs its own small design pass once
   real per-line Mettaext/tier1-mrlore text is compared against real
   original chapter text at scale, not just the one line traced today.
2. Volume: `unclelore` alone has tens of thousands of artifact records
   (see `09-16-2026` side-by-side evidence, 35,449 observations) — this
   design doesn't estimate how many will land in each resolution
   category at that scale, only establishes the mechanism.
3. Whether `tier1/mrlore`'s scene-packet text is byte-identical to
   Mettaext's `out_pass1_*.txt` for the same scene (both ultimately
   derive from the same source chapters) isn't checked — if they match,
   one content-matching pass could serve both systems; if not, each
   needs its own.

## Status

Mechanism designed and grounded against three real provenance examples
pulled from disk, not assumed uniform. No code written. This closes the
gap the Publisher design named at §8 ("existing evidence needs a real
backfill/crosswalk pass... not attempted there") — now specified enough
to implement against.
