# Chapter 1's Metta evidence is confirmed stale — direct hash comparison

Direct answer to the requested check: compare the current chapter-1
vault file's hash against the hash the ingestion was authorized
against. Read-only. Confirms the user's revised diagnosis precisely,
and surfaces one more structural gap in the process.

## The comparison

```text
Current file:  /home/mytruelove/Downloads/obsidianburdenNov25/
               book_01_book_of_genesis/001_the_ethereal_vigil.md
Current SHA-256:    1b8ee585ba2c4b5c97cedebdf226b49d6161ec218b492dacdc6d219c32367caa
Current mtime:      2026-09-19 10:50:36

Ingestion-authorized SHA-256 (from id=50397's authorization contract,
re-verified post-execution per id=50533):
                     7e75a99dd44bc261d25109f6dd9b0eec5ede4697740b8393eb6a1413f9135f60
```

**The hashes differ. The vault file was edited after this morning's
controlled ingestion** (ingestion completed ~08:41; current file mtime
10:50, about two hours later).

## What actually changed, confirmed directly

The vault file, right now, contains exactly one scene marker:

```text
$ grep -n "scene 001\." 001_the_ethereal_vigil.md
6:scene 001.1 — the ethereal vigil
```

The evidence captured *at ingestion time* — still sitting in
`out_passA_001_the_ethereal_vigil.json`'s own `raw_text` field — shows
the pre-edit structure, exactly as the user described: duplicated beat
labels formatted as if they were scene boundaries:

```text
scene 001.1 — ethereal watch / planetary stabilization
scene 001.2 — discovery of transformed Pelagor
scene 001.2 — discovery of transformed Pelagor      (duplicate)
scene 001.3 — decision to manifest Nephoretti
scene 001.3 — decision to manifest Nephoretti       (duplicate)
scene 001.4 — manifestation launch
```

This confirms the corrected diagnosis exactly: those `001.2`/`001.3`
markers were not valid authored scene boundaries Mettaext ignored —
they were bad source structure (duplicated beat labels) that has since
been cleaned up in the vault. The prior finding in `e2a6964` ("neither
pipeline uses the author's own inline scene headings") is now qualified,
not reversed: at the time of ingestion, the only heading structure
present was this duplicated, unreliable one — there was no clean
authored boundary for either pipeline to have used yet.

## The generated evidence has no durable hash of its own

Checked `out_passA_001_the_ethereal_vigil.json` for any field recording
the source hash it was built from: none exists (`{}` — empty). The
*only* record of the source hash anywhere is the conversation-level
authorization/completion exchange (Hermes `state.db`, ids `50397`/
`50533`) — not a structured field on the artifact itself.

**This means today's hash comparison could only be done by going back
to a chat transcript, not by reading the evidence file.** For any
future automatic staleness check (`vault file hash changes -> notice
-> invalidate -> rerun -> replace`) to work at all, the generated
`out_passA`/`out_passB` artifacts need to durably record the exact
source hash they were built from, as a real field, not something that
only exists in an authorization request's prose. This is a concrete,
independent gap worth fixing alongside the five defects already listed
in the recovery-decision receipt (`4c7bf79`) — not a sixth content
defect, but a missing precondition for the vault-integration lifecycle
the decision receipt already committed to.

## Net

```text
Chapter 1's current Metta evidence:  CONFIRMED STALE
                                      (hash mismatch, source edited
                                      post-ingestion)
Cause of the earlier "boundary"
  finding:                           source-side (duplicated beat
                                      labels), not a Mettaext defect
Durable hash tracking on artifacts:  ABSENT -- comparison required the
                                      conversation transcript, not the
                                      file
```

This is exactly the demonstration the user was after: a real,
concrete, dated case of vault drift invalidating existing evidence,
found by comparison rather than assumed. Per the plan already recorded
in `4c7bf79`, the scene splitter should not be tuned against this
now-stale Chapter 1 evidence. The test pair going forward, once the
five defects are fixed and a fresh rerun happens: **Chapter 1 should
resolve to 1 scene** (matching its current, cleaned single-marker
structure) and **Chapter 3 should resolve to 7 scenes** (seven
genuine, day-separated scenes, per the user's own description) — a
real pass/fail check for whether the fixed boundary logic is doing
what's actually needed, not a synthetic one.

## What was not done

No rerun, no ingestion, no fix to the scene splitter or any of the five
listed defects. No file was modified. This is a read-only hash/content
comparison, exactly as requested.
