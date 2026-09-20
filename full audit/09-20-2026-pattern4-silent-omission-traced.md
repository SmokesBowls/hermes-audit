# Pattern 4 traced to its exact cause — and the semantic audit's own wording corrected

Read-only trace, per instruction. Reconciles `e9a3075`'s "fixed 3-mention
threshold" claim against `3f58af9`'s confirmed removal of the old
`mentions < 3` exclusion in `pass2_entity_filter.py`. Verified against
the real, fresh Books 1-5 artifacts from `bee9cc5`, not re-derived from
memory of the code. **No code changed.**

## The reconciliation: two different thresholds, in two different files

`3f58af9` (2026-09-15) is correct and unaffected by this trace: the old
`if char.mentions < 3: continue` exclusion rule inside
`pass2_entity_filter.py` really was removed, and stays removed —
confirmed by re-reading that file's current `filter_entities()` (no
mention-count check anywhere in it; known entities are kept
unconditionally, unknown candidates are kept unless they fail the
noise-word/length/suffix checks).

But `e9a3075`'s explanation was imprecise about *where* the threshold
that actually causes Pattern 4 lives. It is not in
`pass2_entity_filter.py` at all. It is a separate, earlier, still-present
gate in **`pass2_enhanced.py`'s `extract_characters()`** (line 425-454)
— the function that builds the initial candidate list *before* the
filter ever runs:

```python
# First pass: count potential names
for seg in segments:
    ...
    for match in NAME_PATTERN.finditer(text):
        word = match.group()
        if word not in {"The", "They", ...}:
            name_counts[word] += 1

# Second pass: names that appear 3+ times are probably characters
for name, count in name_counts.items():
    if count >= 3:
        characters[name] = Character(name=name, mentions=count)

# Add explicit speakers
for seg in segments:
    if seg.speaker and seg.speaker != "unknown":
        ...
```

This threshold was never touched by `3f58af9` and was never part of
that fix's scope. It's a different mechanism, doing a different job
(deciding whether a capitalized word is *worth considering* as a name
candidate at all), one full stage upstream of the known/unknown
classification `3f58af9` fixed.

## Exact stage-by-stage trace, verified against real artifacts

Checked all 10 flagged scene-instances from `e9a3075` (Mika x4, Zephyr
x3, Saresh x2, Torhh x1) directly against the fresh `out_pass1_*.txt`
files. **Every single one shows exactly the same mechanism, with
identical numbers:**

```text
scene.book005.024_the_first_spark.scene005    Mika    occurrences=2  speaker_lines=0
scene.book005.024_the_first_spark.scene010    Mika    occurrences=2  speaker_lines=0
scene.book005.024_the_first_spark.scene011    Mika    occurrences=2  speaker_lines=0
scene.book005.025_confined_freedom.scene003   Mika    occurrences=2  speaker_lines=0
scene.book004.019_the_sacrafice.scene004      Zephyr  occurrences=2  speaker_lines=0
scene.book004.022_final_calculation.scene001  Zephyr  occurrences=2  speaker_lines=0
scene.book004.023_beyond_identity.scene001    Zephyr  occurrences=2  speaker_lines=0
scene.book003.012_nephilim_summoning.scene002 Saresh  occurrences=2  speaker_lines=0
scene.book003.014_convergence.scene001        Saresh  occurrences=2  speaker_lines=0
scene.book002.007_the_needle_construction.scene002 Torhh occurrences=2 speaker_lines=0
```

Never 3. Never an explicit speaker attribution. And checking *where*
those exactly-2 occurrences fall (not just how many) adds a sharper,
more precise finding than `e9a3075` stated:

```text
$ grep -n "Mika" .../out_pass1_scene.book005.024_the_first_spark.scene005.txt
11:{type:narration} @scene_meta_participants: The Nameless One, The Five, Mika
23:{type:narration} participants: The Nameless One, The Five, Mika
```

**Both occurrences, in every one of the 10 cases, are the participants
metadata line itself — once as the structured `@scene_meta_participants:`
header line (`d138fc8`'s Pass C passthrough) and once as the original
raw `participants:` line that was already part of the scene's text.
None of the 10 names appear anywhere in that scene's actual narrative
prose at all.** This is a more precise statement than "one mention
short of the threshold" — the real prose-mention count is zero; the
count of 2 is entirely a metadata artifact, and `extract_characters()`'s
`NAME_PATTERN` scan has no concept of "this segment is a metadata
header, not narration" — it scans every segment's text identically
regardless of provenance.

Full stage-by-stage path, confirmed:

```text
scene_meta.participants (authored, contains "Mika")
    v   [Pass B: split_by_authored_scene_markers -- text unchanged, verbatim]
    v   [Pass C: packet_text() -- adds @scene_meta_participants: header, ADDITIVE]
Pass 1 segments: "Mika" appears twice, both from the participants line
  (once as structured header, once as original raw text) -- zero
  appearances in narrative prose.
    v   [pass2_enhanced.extract_characters(), NAME_PATTERN scan -- line 437]
    Both occurrences count identically. Total = 2.
    v   [line 446: `if count >= 3`]
    2 < 3 -- Mika is NEVER added to the `characters` dict. Stops here.
    v   [pass2_entity_filter.filter_entities()]
    NEVER REACHED. This function only classifies names already in the
    `characters` dict it's handed -- Mika was never in it, so
    3f58af9's fix (real, correct, unrelated) has nothing to act on.
    v   Pass 2 .metta
    No (entity Mika ...) atom -- nothing to write.
    v   Pass 3 entities_observed
    No Mika record. Matches e9a3075's observed symptom exactly, now
    with the exact mechanism identified instead of the wrong file named.
```

## Direct answers to the three questions asked

```text
Is there another threshold?
  Yes -- pass2_enhanced.py's extract_characters(), line 446,
  `if count >= 3`, untouched by 3f58af9 and in a different file/function
  entirely from the one that fix changed.

Does participant metadata ever seed the candidate set independently?
  No. Nothing in the current pipeline treats scene_meta.participants
  as its own candidate source. A participant only becomes a Character
  candidate by accumulating 3+ raw NAME_PATTERN hits across ALL of a
  scene's segment text (metadata lines counted identically to prose),
  or by being an explicit dialogue speaker tag. There is no code path
  that reads scene_meta.participants and unconditionally seeds
  entries from it.

Is some other filter responsible?
  No. pass2_entity_filter.py was checked in full and is not involved
  in any of the 10 traced cases -- they never reach it.
```

## The design invariant, restated precisely against what exists today

The proposed invariant —

```text
authored participant -> must have an entities_observed record
  even if known=false, spawnable=false, physicality=unknown
```

— is not satisfied today because `extract_characters()` builds its
candidate set purely from frequency-in-text-that-happens-to-include-the-
metadata-line, with no direct, unconditional seed from
`scene_meta.participants` itself. The fix location this trace points to
(not implemented here): `extract_characters()` (or a caller wrapping
it) would need to independently parse `scene_meta.participants` into
name tokens and guarantee each becomes a `Character` candidate
regardless of raw mention count -- separate from, not a replacement
for, the existing frequency-based extraction that still needs to catch
named characters who aren't listed in `participants:` at all (background
figures, historically-referenced characters, etc.).

## What was not done

No code changed. `pass2_enhanced.py` and `pass2_entity_filter.py` were
read, not edited. No fix was written or proposed as an implementation --
this trace exists to correctly locate the mechanism before any change
is made, per instruction.
