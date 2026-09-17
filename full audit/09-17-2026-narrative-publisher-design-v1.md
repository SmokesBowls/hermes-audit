# Narrative Publisher — locked architecture (design v1, spec only, no code)

Answers the gap surfaced once `[EDITOR_REQUEST]` and the assembly stage
were both frozen: giving Dragon a whole scene (let alone a whole
chapter) doesn't scale, and Mettaext's own scene boundaries are already
admittedly mechanical. Refined across two rounds with the user into its
final shape: **not a new parser, a shared coordinate system** — Mettaext
and MrLore keep doing whole-book analysis exactly as they do today; the
Publisher gives every result from every system, and every bounded read
Dragon does, the same address space. Grounded against the same real
scene used all day (`chapter.book008.047_mika` scene002, Falcon Ridge).
Nothing implemented.

## 0. What already exists that this builds on or must reconcile with

Checked before locking anything, same discipline as every design today:

1. **Mettaext already has a chapter-original line anchor, separate from
   its own internal numbering.** The `out_pass1_<scene_id>.txt` header
   (read today, real file) carries `@boundary_start_line: 56` /
   `@boundary_end_line: 131` — confirmed, per the already-frozen Mettaext
   door contract (§4 of `09-15-2026-engain-door-contract-v1.md`), to be
   the **original chapter's own line numbers**, a different space from
   `artifact_line` (which is local to that one `out_pass1_*.txt` file
   and includes front-matter). So Mettaext isn't fully disconnected from
   a canonical line-numbering scheme — it already tracks one — but that
   scheme is scene-level and admittedly mechanical
   (`@boundary_method: mechanical_word_chunk`,
   `@authored_scene_boundaries_proven: false`), not passage-level or
   narratively validated. The Publisher does not need to invent
   chapter-line tracking from nothing; it needs its own independent,
   finer-grained, narratively-aware pass, and a crosswalk to what
   Mettaext already emits.
2. **Mettaext's own line-tagged format already marks paragraph
   boundaries.** Every `out_pass1_*.txt` line carries `{type:narration}`,
   `{type:dialogue, speaker:X}`, or `{type:blank}` (verified, real file).
   `{type:blank}` lines already function as paragraph/beat separators in
   the existing pipeline — a real, reusable structural signal, not
   something the Publisher has to detect from raw prose itself if it
   reads Mettaext's tagged output rather than the bare vault `.md`.
   (Open question, not resolved here: does the Publisher read the raw
   vault file directly, or Mettaext's tagged pass1 output? See §6.)
3. **The Mettaext door's frozen `artifact_line` field does not survive
   this unchanged.** Any existing evidence citing `artifact_line` is
   scoped to one Mettaext-internal file, not Publisher coordinates. This
   design does not retroactively renumber that contract — it names a
   real crosswalk/backfill obligation for later, not solved here.

## 1. What the Publisher is and is not

```text
Publisher:  "Where in the story is this?"
Mettaext:   "What is explicitly there?"
MrLore:     "What is this thing across the story?"
Dragon:     "Show me the amount I can work with right now."
```

The Publisher is **dumb about interpretation** — it does not decide
identity, canon, or scene meaning. Its job, exactly as specified: preserve,
segment, number, hash, and serve. Mettaext and MrLore are not
constrained to passage-sized inputs — they keep their whole-book
analysis; every result they produce simply gets tagged with Publisher
coordinates so it's addressable at passage granularity when needed. The
Publisher never does content search ("give me the passage where Falcon
Ridge is introduced" is answered in two steps: Mettaext/MrLore resolve
*which* passage by content, then the Publisher serves that passage *by
coordinate* — the Publisher itself only ever takes an ID, a range, or
`next`/`previous`, never a search term).

## 2. Coordinate schema (locked)

```json
{
  "passage_id": "book_008.chapter_047.passage_0009",
  "source_file": "book_08_the_vigil_of_the_anchor/047_mika.md",
  "chapter_id": "chapter.book008.047_mika",
  "byte_start": 0, "byte_end": 0,
  "line_start": 88, "line_end": 92,
  "word_start": 0, "word_end": 0,
  "content_hash": "sha256:...",
  "previous_passage_id": "book_008.chapter_047.passage_0008",
  "next_passage_id": "book_008.chapter_047.passage_0010",
  "context_before": { "word_start": 0, "word_end": 0 },
  "context_after": { "word_start": 0, "word_end": 0 }
}
```

Byte range is the strongest replay anchor (exact, encoding-proof); line
range is for human/tool cross-reference against Mettaext's existing
`boundary_start_line`/`boundary_end_line`; word range is "the common
ruler" for synchronization, per the user's framing. `context_before`/
`context_after` are explicitly **not part of the passage's authoritative
range** — envelope only, never counted as passage content, so overlap
never corrupts the numbering. (Real word offsets left as `0` above —
computing them requires the one canonical segmenter, §3, which isn't
built yet; not fabricated here.)

## 3. One canonical segmenter — the load-bearing constraint

Per the user's explicit correction: **no per-tool word counting.** One
shared library/executable every consumer calls, because "Moon-heart"
counted as one word by one tool and two by another silently breaks
every downstream coordinate. This needs an explicit, frozen tokenization
rule before any passage numbering can be trusted — not designed here,
flagged as the single highest-priority open item (§7).

## 4. Boundary priority (locked, in this order)

```text
1. scene break
2. paragraph boundary
3. dialogue/action block
4. sentence boundary
5. hard size limit — last resort only
```

Applies to both the **primary passage range** and the **context
envelope** — the envelope should also snap to structural boundaries
(never cut mid-sentence), not just be a raw word-count window. This
extends the user's own priority order to the envelope rather than
leaving it as a separate, unprincipled cut.

## 5. Worked example against real text (Falcon Ridge, scene002, "ACT 3: EARLY DAYS")

Using `{type:blank}` boundaries already present in the real
`out_pass1_scene.book008.047_mika.scene002.txt` (lines 86–117 — the same
Act 3 span `[EDITOR_REQUEST]`'s `structures[]` was grounded against),
paragraph-boundary splitting produces five natural passages, not one
undifferentiated block:

| Passage | Content (real) | Source lines |
|---|---|---|
| A | "Month 1 was raw survival... The second was a long barracks... basic, drafty, and home." | 88–92 |
| B | "Month 2 brought order... A storage cache was dug into a cool hillside." | 94–99 |
| C | "Month 3 saw the valley become a settlement... A low perimeter wall began to snake..." | 101–104 |
| D | "The valley's strategic perfection was undeniable... two-mile sightline..." | 106–109 |
| E | "One morning, as Mika inspected the growing wall... 'Perimeter's good'... Then he was gone..." | 111–117 (includes one dialogue/action block, rule 3) |

Each of these is well under any plausible hard size limit (a few
sentences each) — the scene-break/paragraph rules alone resolve this
whole span cleanly, the hard-limit fallback never triggers here. This is
real evidence the priority order works as intended on real prose, not
an assumption.

Passage B, if it were Dragon's current read position, would carry:

```text
primary: passage B, lines 94-99 ("Month 2 brought order..." through "...cool hillside.")
context_before: end of passage A (line 92, "...basic, drafty, and home.")
context_after: start of passage C (line 101, "Month 3 saw the valley become a settlement.")
```

matching the "old MrLore problem" the user named directly — a name or
event examined without enough surrounding narrative to mean anything —
the exact failure this envelope exists to prevent.

## 6. Open question, not resolved here: reads the raw vault, or Mettaext's tagged output?

Two real options, each with a real cost:

- **Read the bare vault `.md`/`.txt` directly.** Fully independent of
  Mettaext; matches "preserve the original untouched" cleanly. But
  re-derives paragraph/dialogue-block detection from scratch — duplicate
  work Mettaext's `{type:...}` tagging already does.
- **Read Mettaext's `out_pass1_*.txt`.** Reuses the existing narration/
  dialogue/blank tagging (§0.2) instead of re-deriving it, but makes the
  Publisher depend on Mettaext having already run `ingest` for that
  chapter, and inherits Mettaext's own line-numbering quirks (§0.1,
  0.3) as something to crosswalk rather than avoid.

Not decided in this document. Whichever is chosen, the Publisher's own
segmentation (§4) stays independent of Mettaext's mechanical scene
boundaries — it does not defer to `@boundary_method: mechanical_word_
chunk` as authoritative, it only optionally reuses the tagging.

## 7. Non-negotiable rules

- Original book files are never modified. Published output lives beside
  them (`published/book_11.index.json`, `published/chapter_001.
  passages.jsonl`), matching the user's proposed layout exactly.
- The Publisher never interprets — no identity, no canon, no scene
  meaning, no content search. Coordinate resolution only.
- One canonical segmenter/tokenizer, shared, not reimplemented per
  consumer. This is the single highest-priority open item before any
  passage numbering can be trusted across Mettaext, MrLore, and Dragon.
- Context envelopes are never counted as part of a passage's
  authoritative range.
- Deterministic and hash-verified throughout — same discipline as every
  other artifact in this ecosystem today.

## 8. What this doesn't solve, stated plainly

- Existing Mettaext/MrLore evidence (anything citing `artifact_line` or
  entity records without passage coordinates) needs a real backfill/
  crosswalk pass to become addressable in this scheme — not automatic,
  not attempted here.
- The Mettaext door's frozen v1 raw-text lane (`out_pass1_<scene_id>.
  txt`, substring search, 200-hit cap) is not superseded by this
  document. A future door v2 reading published passages instead is a
  natural next step, not this one.
- Tokenization rule (§3), and the raw-vault-vs-tagged-output choice
  (§6), are both named but not decided.

## Status

Architecture and coordinate schema locked, validated against real text
with real paragraph boundaries, nothing invented. No code, no
tokenization rule, no crosswalk mechanism yet. This is now the fifth and
last piece of today's chain: Publisher (this doc) → Mettaext/MrLore
evidence, addressable → Dragon reads bounded passages → `[EDITOR_
REQUEST]` → assembly → `.osp` → Godot. Every link in that chain has a
locked design as of today; none has code yet.
