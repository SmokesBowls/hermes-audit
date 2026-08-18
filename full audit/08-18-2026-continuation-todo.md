# Continuation TODO — 2026-08-18, Post-Item-1

Written 2026-08-18, end of the session that closed item 1 and produced
item 2's design note. This supersedes `08-17-2026-continuation-todo.md`
as the resumption pointer — read this file first, not that one; that
file and every other dated document stay exactly as written (this
project's standing discipline: amend via new documents, never rewrite
history).

## State as of this writing

| Repo | Branch | HEAD | vs. `origin/main` |
|---|---|---|---|
| EngAIn (`/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn`) | main | `2142d90` | pushed, in sync |
| `engain_avatar` (dragon2d, `/mnt/data-drive/engain_avatar`) | main | `1b2c111` | **1 ahead, not pushed** |
| `godot_engain_3d_avatar` (dragon3d, `/mnt/data-drive/godot_engain_3d_avatar`) | main | `90fc568` | pushed, in sync |
| `engain-avatar-audit` (this repo) | main | `1700da2` | **1 ahead, not pushed** |

`engain_avatar`'s unpushed commit (`1b2c111`, "Route dispatch through
EngAIn's shared continuity authority (opt-in)") predates this session —
carried forward from the 2026-08-17 avatar-continuity-integration work,
still deliberately unpushed, same standing rule (never push without
explicit instruction). `engain-avatar-audit`'s unpushed commit
(`1700da2`) is this session's item-2 design note — see below.

`engain-avatar-audit` also still carries the same pre-existing, unrelated
dirty files noted in every receipt since 2026-08-17
(`claude hermes 3d.md` modified, `claude hermes 3d2.md` untracked) —
still untouched, still not part of any of this work.

`ENGAIN_CONTINUITY_DISPATCH` remains opt-in/unset by default in both
avatar repos — the new `/dispatch` path (and its item-1 mutex) is proven
live but inert unless a worker explicitly turns it on. The
default/direct-Hermes avatar path is what real Godot sessions exercise
today, and item 1's live proof confirmed it still works unmodified,
double-locked (old client-side claim + new server-side claim, both real,
harmless, redundant — see item 3 below).

## Closed since the last continuation TODO

- **Continuation-TODO item 4** (real Godot launch through the composed
  runtime) — closed 2026-08-17, two phases:
  `08-17-2026-dragon3d-launch-wrapper-phase1-proof.md` (the
  `launch_dragon3d.sh` fix) and
  `08-17-2026-listener-absent-structured-diagnostic-phase2-proof.md`
  (structured `LISTENER_ABSENT` diagnostics). Both live-proven, both
  pushed.
- **Continuation-TODO item 1** (concurrent-`/dispatch` mutex) — closed
  2026-08-18. Full chain: `fef2a00` (design) → `23c6215` (design,
  amended after a reviewer traced a binding-sourcing race that
  invalidated the first draft) → `2142d90` in EngAIn (implementation) →
  `ff8d8ff` (proof receipt) → `a9b016a` (closure). All pushed, all
  remotely verified. Full narrative: `08-18-2026-item1-closed.md`.

## In progress — item 2, design done, implementation not started

**`SessionLedger.append()`'s `turn_id` race** (discovered while
re-deriving item 1; recorded as its own item in
`08-18-2026-continuation-todo-amendment-ledger-turn-id-race.md`).

Design note written and committed (`1700da2`, **not yet pushed**):
`08-18-2026-item2-session-ledger-semantic-derivation.md`. Conclusion,
derived from the actual contract (`SHARED_SESSION_CONTINUITY_CONTRACT_v1.md`)
and every real (non-test, non-proof-script) caller, not assumed:

- The contract promises `turn_id` is unique + monotonic per
  `session_id` only — nothing about physical list position, nothing
  about request/response transactional adjacency.
- All five real production callers (inside `SharedSessionBridge.
  handle_turn()` and its two collaborators) use `turn_id` purely as a
  `<`/`>` comparison key — never a list index, never a paired
  request/response identifier.
- A concrete interleaved trace (`A-req, B-req, B-resp, A-resp`, same
  `shared_session_id`, two different native providers) produces correct
  results at every one of those five readers, given only that `turn_id`
  assignment is atomic and unique. No existing caller requires or
  assumes strict transactional (non-interleaved) ordering instead.
- **Recommended minimal fix**: atomic/unique/monotonic `turn_id`
  assignment inside `append()` alone, decoupled from physical list
  position. No lock spanning `handle_turn()`'s provider-dispatch call.
  Explicitly must not grow to also serialize `shared_session_id`
  operations end-to-end — that would silently re-eat the concurrency
  item 1 just proved correct, for a guarantee no caller needs.

**Not yet implemented — awaiting review of the design note before any
code changes**, same discipline as item 1's own design→review→implement
sequence. When resuming: get sign-off on
`08-18-2026-item2-session-ledger-semantic-derivation.md`'s conclusion
first (or a correction to it, the way item 1's first design draft got
corrected before implementation), then implement, add a deterministic
concurrency regression test (real threads, no sleep-based timing — same
standard item 1's own regression test set), run all three repos' offline
suites, and write the implementation receipt — mirroring item 1's own
`fef2a00`→`23c6215`→`2142d90`→`ff8d8ff`→`a9b016a` shape.

## Full open-items order

1. ~~Concurrent-`/dispatch` mutex~~ — **done**, `08-18-2026-item1-closed.md`.
2. **`SessionLedger.append()` `turn_id` race** — design done, awaiting
   review, implementation next. *(current position)*
3. Ledger/cursor persistence across a restart — blocked behind item 2
   (persisting an already-possibly-inconsistent ledger would be
   backwards; also worth re-deriving from first principles once item 2
   lands, since a dispatched recap becoming permanent native-side state
   already changes what's actually still missing here — see the
   original 2026-08-17 continuation TODO's own note on this).
4. Production cutover decision — not made. Includes, now, whether/when
   to retire the client-side/default-path claim in `hermes_session_adapter.py`
   given item 1's server-side claim makes it redundant for any caller
   that goes through `/dispatch` — not decided, not urgent, no regression
   risk either way today.
5. ~~Real Godot launch through this integration~~ — **done**,
   2026-08-17 (two-phase receipt above).
6. `provider_session_ref`'s frozen-identity limitation — not fixed,
   still just named.

## Where to look first when resuming

- **Item 2 (current)**: `08-18-2026-item2-session-ledger-semantic-derivation.md`
  for the full design reasoning; `tier1/engainos/core/session_ledger.py`
  (`SessionLedger.append()`, the actual `turn_id=len(turns)` bug) and
  `tier1/engainos/bridgeroom/shared_session_bridge.py` (the five real
  callers traced) are where to look first once implementation starts.
- **Working discipline, unchanged, apply without being re-told**: every
  claim backed by a real, live-executed proof; receipts written
  honestly including corrections when something was found wrong (item
  1's own §8a correction is the model for this); ratified/committed
  docs amended via new documents, never rewritten in place; commit
  per-repo with detailed messages; **never push without explicit
  instruction** (`engain_avatar`'s `1b2c111` and this repo's `1700da2`
  are both currently held exactly per this rule); design reviewed and
  approved before implementation for anything touching a shared
  contract (item 1's own process, repeated for item 2).
- Chronological `full audit/08-1{5,6,7,8}-2026-*.md` files hold the
  complete history if more depth than this summary is needed.
