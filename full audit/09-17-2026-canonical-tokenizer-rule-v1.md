# Canonical tokenizer/word-counter rule v1 (frozen spec, no code)

Settles the single highest-priority open item from `09-17-2026-
narrative-publisher-design-v1.md` §3/§7: one shared word-counting rule,
used identically by the Publisher, Mettaext, MrLore, and Dragon, so a
word offset means the same thing to all four. Grounded against real
text from the same chapter this whole session keeps returning to
(`book_08_the_vigil_of_the_anchor_047_mika.md`, real file, checked
directly today — not the Mettaext-processed output, the actual source
`.md`).

## 0. Why this needed real evidence, not a guessed rule

Grepped the real chapter file before writing any rule. Two concrete,
quantified problems exist in this one file already, not hypothetically:

1. **Apostrophe drift is real, in-corpus, today.** The file mixes
   curly (`’`, U+2019) and straight (`'`, U+0027) apostrophes for the
   same grammatical construction: `he’d`, `she’d`, `they’d` appear with
   the curly form (4 occurrences) while `they'd`, `didn't`, `Geralt's`,
   `Zephyr's`, `Needle's`, `mountain's` appear with the straight form
   (57 occurrences) — **in the same file**. This is exactly the
   `Moon-heart`-style drift risk flagged when this item was raised,
   confirmed present, not assumed.
2. **Em-dashes attach directly to words with no surrounding whitespace**
   in this author's style (18 occurrences in this one chapter) — e.g.
   line 13: `unremarkable—just`, `ridges—but`; line 46: `—and the
   valley`. A whitespace-only splitter (`wc -w`, or any naive tokenizer)
   silently merges these into single tokens. Quantified below.
3. **Hyphenated compounds are common and real**, not a one-off edge
   case: `blood-stained, brick-dust, cloth-wrapped, dragon-shaped,
   fist-sized, genetically-modified, late-blooming, metal-reinforced,
   now-familiar, now-visible, rust-colored, sixty-three, south-facing,
   Spire-town, sun-faded, two-mile, wind-scoured` — 17 distinct forms in
   one chapter.
4. **Double quotes are 100% straight in this file** (118 straight, 0
   curly) — no drift risk observed here, but the canonicalization table
   below still covers curly double quotes since other chapters in the
   corpus haven't all been checked and the rule needs to hold corpus-wide,
   not just for this one file.

## 1. Two separate layers — do not conflate them

**Source bytes are never altered.** `byte_start`/`byte_end` (the
Publisher's strongest anchor, per its own design doc) always index into
the original, untouched file exactly as written — curly apostrophe,
straight apostrophe, whatever the author typed. Canonicalization (§3)
exists **only** for a derived comparison/matching layer — deciding
whether two occurrences are "the same word" for cross-referencing,
search, or word-count numbering — never for rewriting what gets served
back as source text. Conflating these would silently violate the
Publisher's own "preserve, never modify" rule.

## 2. Word boundary rule (locked)

A word is a maximal run of characters between boundary points, where a
boundary point is any of:

```text
whitespace (space, tab, newline, any run of these)
em-dash (—), en-dash (–)
```

Leading and trailing punctuation attached to a token (`.` `,` `"` `;`
`:` `!` `?` `(` `)`) is stripped before the token is counted, but does
**not** itself create a boundary beyond where it already sits — i.e.
`struck.` counts as one word, `struck`.

**Internal hyphens do not break a word.** `wind-scoured`, `sixty-three`,
`south-facing` each count as one word — chosen because they function as
single modifiers in this corpus, and because the alternative (splitting
every hyphenated compound) would make `two-mile` count as two words
where the author clearly means one concept. This is a naming choice, not
a discovered fact — recorded as a decision, not derived.

**Internal apostrophes do not break a word**, after canonicalization
(§3) — `Geralt's`, `didn't`, `they'd` each count as one word regardless
of which apostrophe glyph the source file used.

## 3. Canonicalization table (matching layer only, per §1)

```text
U+2019 (’ right single quote)  ->  U+0027 (' apostrophe)
U+2018 (‘ left single quote)   ->  U+0027 (' apostrophe)
U+201C (“ left double quote)   ->  U+0022 (" quote)
U+201D (” right double quote)  ->  U+0022 (" quote)
```

Applied only when deciding word identity/matching. Never applied to
`byte_start`/`byte_end` ranges or to any text actually served back to a
consumer.

## 4. Numbering scope (locked): book-wide, not per-chapter

`word_start`/`word_end` are a **continuous count across the whole book**,
not reset at each chapter boundary. This follows directly from the
user's own worked example in the Publisher design round (`words
48,291–48,972` — a number far larger than any single ~3,000-word
chapter, only sensible as a book-wide running count). `line_start`/
`line_end` stay chapter-file-scoped (matching Mettaext's existing
`boundary_start_line`/`boundary_end_line` convention, already chapter-
local); only the word ruler is book-wide.

## 5. Worked example, hand-traced against real text

Line 13 of the real chapter file:

> The place was unremarkable—just a flat stretch of wind-scoured stone
> between two ridges—but both Geralt and Mika stopped as if struck.

Tokenized under this rule (boundary = whitespace or em-dash; internal
hyphens/apostrophes preserved; trailing punctuation stripped):

```text
1.The  2.place  3.was  4.unremarkable | 5.just  6.a  7.flat  8.stretch
9.of  10.wind-scoured  11.stone  12.between  13.two  14.ridges | 15.but
16.both  17.Geralt  18.and  19.Mika  20.stopped  21.as  22.if  23.struck
```

**23 words.** A naive whitespace-only splitter (`wc -w`, or any tool
that doesn't treat em-dash as a boundary) merges `unremarkable—just`
and `ridges—but` into single tokens each, undercounting this same
sentence at **21** — a 2-word, ~9% discrepancy on one sentence alone,
from a single stylistic choice (unspaced em-dashes) this author uses 18
times in one chapter. This is the concrete, quantified version of the
drift risk the Publisher design named abstractly — confirmed here, not
asserted.

## 6. Non-negotiable rules

- Canonicalization (§3) never touches source bytes, only the matching
  layer. `byte_start`/`byte_end` always refer to the original file.
- One implementation, shared by Publisher/Mettaext/MrLore/Dragon —
  no per-tool reimplementation of §2–§4, per the standing instruction
  that raised this item in the first place.
- Word numbering is book-wide and continuous; line numbering stays
  chapter-local, matching what Mettaext already does.
- This rule is corpus-wide, not chapter-specific — evidence came from
  one chapter, but the rule must hold for every chapter without
  per-chapter exceptions, or it stops being a canonical ruler.

## 7. Open items, not resolved here

1. **Numbers and mixed tokens** — `"1,435"`, `"Month 1"`, `"sixty-three"`
   vs `"63"` — not specified beyond the general boundary rule; no
   evidence gathered yet on how these actually appear across the corpus
   at scale.
2. **En-dash vs em-dash vs hyphen disambiguation in source encoding** —
   this file's em-dashes were consistently U+2014; not checked whether
   other chapters use `--` (double hyphen) as an ASCII em-dash
   substitute, which would need its own boundary rule if found.
3. **Reference implementation** — this document specifies the rule;
   it does not provide code. The Publisher design's own next step
   (§3 of that doc) still needs an actual shared library/executable
   built to this spec.

## Status

Tokenizer rule frozen at this document, validated against real text
with a hand-traced, quantified example — not asserted abstractly. No
code written. This was the top-priority blocker named in the Narrative
Publisher design; it's now specified enough to implement against,
though implementation itself is separate, later work.
