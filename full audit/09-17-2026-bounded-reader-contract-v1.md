# Bounded Reader — frozen contract v1 (spec only, not implemented)

Freezes the interface that existed only by implication in
`09-17-2026-dragon-to-osp-scene-build-design-v1.md` ("Dragon reads
bounded passages") and `09-17-2026-narrative-publisher-design-v1.md`
("Dragon can ask: give me the next passage"). Depends only on the
Publisher (per `09-17-2026-publisher-input-authority-amendment.md`,
the Publisher is the sole coordinate authority) — does not depend on
the crosswalk layer. Grounded against the same five real Falcon Ridge
Act 3 passages (A–E) already hand-verified in the Publisher design §5.
Nothing implemented.

## 0. Non-negotiable rules (recap, tightened for this contract)

- **No narrative interpretation.** The reader returns text and
  coordinates. It does not decide what a passage means, who is present,
  or what is canonical — same "dumb" doctrine as the Publisher itself.
- **Read-only.** Never writes to the Publisher's index, never mutates a
  passage, never creates new passages.
- Every returned passage carries its `content_hash` (from the
  Publisher's own schema) — the reader does not compute or alter it,
  only passes it through.
- Context envelopes are always returned as a separate field from the
  authoritative range, never merged into it — same rule as the
  Publisher design's own §2.

## 1. Operations (frozen, four only)

```text
read_passage(passage_id, include_context: bool = true)
next(passage_id)
previous(passage_id)
read_range(start_passage_id, end_passage_id, overlap: int = 1)
```

No fifth operation (e.g. content search) is in scope. "Give me the
passage where Falcon Ridge is introduced" is explicitly **not** this
contract's job — that's a two-step process (semantic lookup elsewhere,
then a `read_passage` call by the ID that lookup returns), per the
Publisher design's own §1 ("the Publisher never does content search").

## 2. `read_passage` — response shape

```json
{
  "ok": true,
  "passage_id": "book_008.chapter_047.passage_C",
  "chapter_id": "chapter.book008.047_mika",
  "source_file": "book_08_the_vigil_of_the_anchor/047_mika.md",
  "primary": {
    "text": "Month 3 saw the valley become a settlement. More veterans arrived from Ironspire, their war ended, seeking the quiet company of their commanders. Oreck took charge of construction, his methodical, powerful presence perfect for lifting stone beams and plotting defensive lines. A low perimeter wall began to snake around the valley's most accessible approaches.",
    "line_start": 101, "line_end": 104,
    "word_start": 0, "word_end": 0,
    "byte_start": 0, "byte_end": 0
  },
  "context_before": {
    "text": "It was basic, drafty, and home.",
    "line_start": 92, "line_end": 92
  },
  "context_after": {
    "text": "Month 3 saw the valley become a settlement.",
    "line_start": 101, "line_end": 101
  },
  "content_hash": "sha256:...",
  "previous_passage_id": "book_008.chapter_047.passage_B",
  "next_passage_id": "book_008.chapter_047.passage_D"
}
```

Real text above is passage C from the Publisher design's own worked
example (§5) — word/byte offsets left `0` since the tokenizer rule's
reference implementation doesn't exist yet (same honesty rule as every
other placeholder this session: not fabricated). `context_before`/
`context_after` here are the immediately adjacent passages' own tail/
head text — the simplest, most defensible default; whether the envelope
should ever be wider than one adjacent passage is an open item (§5).

## 3. `next` / `previous` — deterministic end-of-book behavior

```json
// next() called on the book's last passage
{ "ok": false, "error": "END_OF_BOOK", "passage_id": "book_008.chapter_047.passage_E" }

// previous() called on the book's first passage
{ "ok": false, "error": "START_OF_BOOK", "passage_id": "book_008.chapter_001.passage_A" }

// next()/previous() called on an ID the Publisher hasn't indexed
{ "ok": false, "error": "PASSAGE_NOT_FOUND", "passage_id": "<given id>" }

// any operation on a chapter the Publisher hasn't segmented yet
{ "ok": false, "error": "CHAPTER_NOT_PUBLISHED", "chapter_id": "<given id>" }
```

`CHAPTER_NOT_PUBLISHED` reuses the exact error vocabulary the crosswalk
design already uses for the same condition
(`chapter_not_yet_published`) — one shared error name across both
contracts for the same real situation, not two spellings of the same
thing.

## 4. `read_range` — overlap semantics

```text
read_range("passage_A", "passage_C", overlap=1)
```

returns passages A, B, C **plus** the one passage immediately before A
and the one immediately after C as context-only entries (not
authoritative), matching the `overlap` count exactly — `overlap=1`
means one full passage of surrounding context on each side, not one
extra sentence. Each returned passage still carries its own `primary`/
`context_before`/`context_after` split (§2) — `read_range` does not
collapse the whole span into one undifferentiated block of text.

## 5. Open items, not resolved here

1. Whether `context_before`/`context_after` should ever span more than
   one adjacent passage (e.g. for a very short passage) — not decided,
   defaulted to exactly one adjacent passage for now.
2. Real word/byte offsets depend on the tokenizer reference
   implementation existing (still not built, per the tokenizer
   contract's own §7 item 3).
3. Whether `read_passage` should accept a raw word/byte position instead
   of only a `passage_id` — not requested by any consumer so far,
   flagged rather than speculatively added.

## Status

Interface frozen at this document, response shapes grounded in the same
real Falcon Ridge passages already hand-verified elsewhere in this
session. No code written. Depends only on the Publisher (§0 of the
input-authority amendment) — does not require the crosswalk layer to
exist first, correcting the ordering caught in the dependency-audit
report before this contract was written.
