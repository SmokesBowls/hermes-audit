# Scope narrowed: book 1 (chapters 1-4 only) stands in for "the whole thing" for now

Records a scoping instruction, not a technical finding. No code
changed.

## What was confirmed

`book_01_book_of_genesis/` currently contains exactly four files, no
more:

```text
001_the_ethereal_vigil.md   22220 bytes, mtime 2026-09-19 10:50
002_molten_descent.md       19328 bytes, mtime 2026-09-19 11:02
003_first_contact.md        16595 bytes, mtime 2026-09-19 11:12
004_the_convergence.md      22499 bytes, mtime 2026-09-19 11:15
```

Only these four chapters have been through the user's manual cleanup
pass (removing duplicated beat-label markers per `772b26b`) so far.
Non-chapter files that previously lived in this directory have been
removed by the user directly.

## The instruction

For all work until further notice: **treat book 1 (these four
chapters) as the entire scope**, not a sample of a ~140-chapter novel.
The rest of the books have not yet been through the same cleanup pass
and are explicitly out of scope for now. A full-novel scan remains a
later, separate step the user will initiate once the rest of the vault
has been reviewed the same way book 1 was.

## Why this matters for the plan already recorded

This directly narrows `4c7bf79`'s "wipe current generated outputs and
regenerate the full corpus from the present vault" step: for now, that
means chapters 1-4 of book 1 only, not the 110-chapter legacy scope
discovered in `3d317a5`. The test pair from `772b26b` (chapter 1 -> 1
scene, chapter 3 -> 7 scenes) still applies directly and is now the
right-sized target — both chapters are inside this narrowed scope.

## What was not done

No code changed, no rerun performed. This is a scope confirmation only.
