# Third live Dragon-door test — a genuinely new question, post-fix

Follows the before/after pair (`09-18-2026-second-live-door-test-before-after.md`,
`d0366b7`). That receipt flagged a real concern: when re-asked the
*same* question a second time, Dragon's final answer presented old,
remembered door results as if they were this turn's own calls. This
test is a different prompt entirely (chapter `059_eyes_of_eternity`,
entity Kyh, not the earlier Geralt/Mika chapter 047 question), sent
fresh by the user with no prior answer already in context — a clean
opportunity to see whether that concern was specific to re-asking a
settled question, or a general pattern.

**Request received:** `id=50125`, `2026-09-18 18:40:48.333`.
**Final answer delivered:** `id=50148`, `2026-09-18 18:42:49.951`,
`finish_reason: stop`.
**Elapsed: ~121.6 seconds.** Still well inside the new 240.0s inner
budget and the outer ~270s watchdog; did not need the larger budget to
succeed, but is closer to it than the second test's 62s.

## This time, the door ledger matches the actual tool-call trace

Full observed tool-call record, ids 50126–50147:

```text
todo (plan)
search_files x4  (locate chapter 059 source + Kyh registry hits)
terminal: engain_door.py query --source .../059_eyes_of_eternity.md --query Kyh
  -> {"ok": false, "error": "INGEST_REQUIRED", "message": "Source has not
      been ingested. Call `ingest` before `query`."}, exit code 1
terminal: mrlore_door.py query --name Kyh
  -> FileNotFoundError, exit code 2
terminal: mrlore_query.py Kyh                 -> entity record, real
terminal: mrlore_query.py --incarnation Kyh   -> "no incarnation chain recorded"
terminal: mrlore_query.py --appearances Kyh   -> book 9 ch51, book 10 ch59, both low confidence
search_files / read_file x5  (direct read of the un-ingested source + registry stub pages)
todo (marked complete)
```

Every door result cited in the final answer's "Authority ledger" section
traces to one of these exact calls, made in this turn, with matching
values (the `INGEST_REQUIRED` payload, the `mrlore_door.py` ENOENT text,
the "no incarnation chain recorded" line, the appearances list) — unlike
the second test, nothing here is a recycled result from an earlier
exchange. This is consistent with the theory in the prior receipt: the
earlier discrepancy was specific to re-asking a question Dragon already
had a committed answer for in context, not a general failure to call
doors when asked to.

## A new, real failure mode surfaced cleanly: `INGEST_REQUIRED`

This is a different door failure than anything seen in the first two
tests (which only ever saw `ok: true` from Mettaext, or the `mrlore_door.py`
absence). Here, Mettaext's own door refused outright because this
particular chapter file has never been ingested into it. Per the user's
explicit instruction ("If an authority is unavailable, show that failure
as-is"), the final answer:

- Quoted the exact `INGEST_REQUIRED` JSON payload, unmodified
- Explained *why* it didn't just call `ingest` itself (treating the
  EngAIn install as an immutable, read-only donor — a boundary decision,
  not a missing capability)
- Fell back to reading the source file directly instead of silently
  producing an answer with no source citation at all
- Separately surfaced a second, unrelated identifier inconsistency
  (filename says chapter 059, the file's own heading and closing line
  say "Chapter 57", MrLore's registry says `ch059`) without resolving or
  hiding it

This is the same honest, non-repairing posture as the first live test's
handling of the `047_mika`/`chapter.045_the_homecoming` mismatch — the
runtime fix has not changed Dragon's own failure-reporting discipline,
only whether a response makes it back to the player at all.

## Net read across all three live tests

1. **First test** (original incident): real door calls made, correct
   authority selection, process killed by the inner timeout before
   answering, response rejected on the correlation defect. Runtime
   failure.
2. **Second test** (exact repeat of test 1's question, post-fix): fast,
   clean completion — but the door ledger reported test 1's old results
   rather than fresh calls. Not a runtime failure; a prompt-fidelity
   question against re-asked material.
3. **Third test** (fresh question, post-fix): fast, clean completion,
   with a door ledger that matches this turn's own tool-call trace
   exactly, including a new and correctly-surfaced `INGEST_REQUIRED`
   failure.

The runtime fix (`cb8456c`) is holding up across two different live
turns now, including one that hit a door failure it had never
previously produced. The one open item from the prior receipt (whether
Dragon re-invokes doors on request) looks, on this second data point,
specific to already-answered questions rather than a general pattern —
worth keeping in mind rather than treating as fully closed on an n of 2.
