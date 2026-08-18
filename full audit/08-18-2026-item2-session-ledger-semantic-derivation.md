# Item 2 Design Analysis — What `SessionLedger` Actually Promises

Written 2026-08-18, immediately after item 1's closure. This is a
**design note only** — no runtime code is touched. Per explicit
instruction: derive `SessionLedger`'s actual semantic contract from
`SHARED_SESSION_CONTINUITY_CONTRACT_v1.md`, the implementation, and every
real caller before proposing a lock, counter, queue, or transaction
primitive. Keep `shared_session_id` synchronization (this item)
completely separate from the already-closed `(provider_id,
provider_session_id)` dispatch mutex (item 1) — nothing here may reduce
the provider-dispatch concurrency item 1 just proved correct.

## 1. What `Turn.turn_id` means

The contract (`SHARED_SESSION_CONTINUITY_CONTRACT_v1.md` §5, §8) is
explicit and narrower than the current implementation:

> "`turn_id` — assigned by the Ledger at accept time, **monotonically
> increasing per session_id**. Never client-supplied."
>
> §8: "Concurrent-write resolution beyond 'turn_id is assigned by the
> Ledger, not the caller' — what happens if two bodies APPEND at nearly
> the same instant is an implementation detail of turn_id assignment,
> **not specified here beyond monotonic-per-session ordering**."

Two things follow directly from the contract text, not from inspecting
code:

- `turn_id` is **identity + total order**, per `session_id` — unique,
  and comparable with `<`/`>` to mean "happened no later than." That is
  the entire promise.
- The contract explicitly declines to specify anything stronger about
  concurrent-write interleaving. It does not promise transactional
  request/response adjacency. It does not promise `turn_id` corresponds
  to a "conversational turn number" (one shared number per request+
  response pair) — direction is a separate field; a request and its own
  response get two different, independently-assigned `turn_id`s, same as
  any other two turns.

The current implementation (`session_ledger.py`) additionally makes
`turn_id` equal to **physical list position** at append time
(`turn_id=len(turns)`), and readers additionally receive turns in
**physical append order** (list iteration order). Neither of those two
extra properties is contractually promised — they are implementation
artifacts of the simplest possible data structure (Stage 4's own
"tiny-implementation proof" scope note says as much: storage mechanism
and concurrent-write ordering are both named as open). The bug this item
is about is exactly that `turn_id=len(turns)` conflates *identity*
(what the contract promises) with *storage position* (what nothing
promises) — and that conflation is what a race can break, since reading
`len(turns)` and appending are two separate steps with no atomicity
between them.

**Answer to question 1**: `turn_id` contractually means *identity +
total order per session_id*. It does not mean physical list position
(implementation detail), and it does not mean conversational turn number
(request/response pairing is not part of its contract).

## 2. What every real reader assumes

Grepped every call site in `tier1/engainos/` outside `tests/`/`tools/`
(the only ones with a live, concurrent, production-shaped caller — the
proof scripts under `tools/` inspect the Ledger read-only, single-
threaded, after the fact, and exercise no interleaving at all). There
are exactly five, all inside `SharedSessionBridge.handle_turn()` and its
two collaborators:

1. **`shared_session_bridge.py` step 2** — `ledger.append(session_id, ...,
   direction="request", ...)`. Assumes only: gets back a `turn_id` that
   is unique and higher than anything already in the session. Does not
   read anything back.
2. **`shared_session_bridge.py` step 4** — `context = [t for t in
   ledger.read_since(session_id, since_turn_id=-1) if t.turn_id <
   request_turn.turn_id]`. Assumes `turn_id` is a valid comparison key:
   "everything with a strictly smaller `turn_id` than my own just-
   appended request happened no later than mine, so it's fair game as
   prior context." Never indexes by `turn_id`, never assumes list
   position, never assumes anything about the *other* turns' direction
   or origin_body.
3. **`continuity_context_builder.py::build()`** — `missing = [t for t in
   context if t.turn_id > last_seen_turn_id]`. Same shape: a pure
   numeric-comparison filter, deciding what a given native session
   "hasn't seen yet." This is the highest-stakes reader — its output
   becomes literal text sent to a real provider — but its assumption
   about `turn_id` is identical to step 4's: total order, nothing more.
4. **`shared_session_bridge.py` step 7** — `ledger.append(..., direction=
   "response", ...)`. Same as (1).
5. **`continuity_cursor_tracker.py::advance()`** — `if turn_id >
   self._cursors.get(key, -1): self._cursors[key] = turn_id`. Monotonic-
   max bookkeeping keyed by `(provider_id, provider_session_id)` — again,
   pure numeric comparison against `turn_id`, nothing about position or
   pairing.

**Answer to question 2**: every real reader uses `turn_id` exclusively
as a **comparison key for total order** — never as a list index, never
as a paired request/response identifier, never as a per-origin_body
counter. Nothing anywhere reads `turns[turn_id]` or assumes adjacency
between a request and its own response. This matters directly for
question 4: it means every real reader is *already* written in a shape
that is interleaving-agnostic, provided the numbers themselves are
trustworthy (unique, and consistent with true accept-time order).

## 3. Which interleavings are valid — traced concretely

Two callers, A (origin_body `dragon_2d`, dispatching to native session
`P_A`) and B (origin_body `dragon_3d`, dispatching to native session
`P_B`), both calling `handle_turn()` for the **same** `shared_session_id`
S, genuinely concurrently — assuming, for this trace, that `turn_id`
assignment has *already* been made atomic/unique/monotonic (i.e., item
2's minimal fix, whatever its exact mechanism, is in place). The
question is whether *interleaving itself*, independent of the raw
duplicate-ID bug, produces an incorrect result for any of the five real
readers above.

```
t0  A step2 append request  -> turn_id=0
t1  B step2 append request  -> turn_id=1
t2  A step4 read_since(-1) -> [turn0, turn1] (both already in the Ledger by now)
       filter t.turn_id < 0 (A's own request_turn.turn_id)
       -> context_A = []                     -- correct: turn 1 (B's request)
                                                 did not exist before A's own
                                                 request was accepted, so it is
                                                 rightly excluded regardless of
                                                 when step 4 happens to run
t3  B step4 read_since(-1) -> [turn0, turn1]
       filter t.turn_id < 1 (B's own request_turn.turn_id)
       -> context_B = [turn0]                -- correct: A's request DID
                                                 happen before B's, so it IS
                                                 legitimate prior context for B
t4  B's real dispatch is fast; completes.
       step7 append response -> turn_id=2
       cursor.advance(P_B, 2)
t5  A's real dispatch is slow; still in flight — was built from context_A=[]
       at t2, using last_seen_turn_id for P_A at that time. B's response
       (turn 2) did not exist yet when A's dispatch_input was built, so
       A's own provider call correctly never saw it.
t6  A's dispatch finally completes.
       step7 append response -> turn_id=3
       cursor.advance(P_A, 3)
```

Final Ledger order: `[A-req(0), B-req(1), B-resp(2), A-resp(3)]` — the
"A request / B request / B response / A response" interleaving the
review question named directly.

Checking every one of the five real readers against this trace: all
five behave exactly as documented, using nothing but `<`/`>` comparisons
against unique, correctly-ordered `turn_id`s. **Nothing is incorrect.**
`read_last(S, direction="response")` would now return B's response
(turn 2) or A's response (turn 3) depending on when it's called — both
answers are *correct* under the contract's own definition of recency
("the single most recent matching turn," §6), even though a reader
unfamiliar with the timing might find "B's whole exchange nested inside
A's slower one" surprising. That surprise is not a violation of the
contract; §2's own framing ("three doors into the same room," one page
everyone reads and writes) already commits to exactly this: turns
interleave by real submission/completion order, not partitioned or
paired by door.

**The strict-transactional model** ("must always be A-req, A-resp,
B-req, B-resp — never interleaved") was checked against the same five
readers for a caller that would become *incorrect* without it, and none
was found. No caller anywhere in the codebase — production or test —
currently assumes or requires transactional request/response adjacency.
Enforcing it would require a *new* constraint nothing today asks for:
serializing the *entire* `handle_turn()` span (Ledger append through
real provider dispatch through Ledger append) per `shared_session_id`,
which is a categorically heavier lock than anything either item touches
today — effectively re-introducing a full per-shared-session mutex
spanning a real, possibly-slow network/subprocess call, exactly the
shape of primitive item 1's design explicitly avoided for the *narrower*
`(provider_id, provider_session_id)` case, now proposed for the *wider*
`shared_session_id` case with no reader that needs it.

## 4. The smallest required invariant

Given §1's contract text and §2's/§3's callers, the required invariant
is squarely **(A) atomic, unique, monotonic append IDs** — not (B)
"consistent reads/writes" beyond what unique IDs already guarantee (no
reader was found that needs a stronger read/write consistency property;
Python's own list/GIL semantics already prevent a torn *read* of
existing elements during a concurrent append, so the actual defect is
confined to `append()`'s own internal read-modify-write, not to
`read_since`/`read_last`), and not (C) whole-`handle_turn()`-transaction
serialization (§3 found no caller that needs it, and imposing it would
cost real, currently-legitimate concurrency for no discovered benefit).

This directly and narrowly fixes the bug as originally found (§2 of the
item-1 design note): two concurrent `append()` calls for the same
`session_id` racing `len(turns)` and minting a duplicate `turn_id`. The
natural implementation shape (not proposed as code here, per
instruction) is the same category `SessionClaimRegistry` already uses —
one lock around the read-then-write inside `append()` itself, or an
atomic counter decoupled from list length entirely (the contract, per
§1, does not require `turn_id == list index`, so decoupling them is not
a compatibility risk with anything that currently reads the Ledger).

## 5. Boundary with item 1 — explicitly preserved

Item 1's claim is keyed on `(provider_id, provider_session_id)` — the
native provider transcript. This item's fix is keyed on `session_id` —
Ledger append-identity. These protect two different resources and must
stay two different mechanisms:

```
shared session S
A -> Hermes / native session 123
B -> Claude Code / native session 456
```

Item 1 already correctly proved these two native dispatches must run
concurrently — different keys, no shared resource, no reason to
serialize. §3's trace above shows the Ledger-identity fix does not
change that: `append()`'s own internal critical section (assigning one
`turn_id` and inserting one `Turn`) is measured in microseconds, pure
in-memory, with no provider call inside it — nothing like item 1's
minutes-scale, subprocess-bound critical section. A's and B's real
provider dispatches remain fully concurrent under this fix; only the
instant of "mint my request's `turn_id`" (and, separately, "mint my
response's `turn_id`") becomes atomic, each on the order of a single
Python statement. This item's fix must never grow to also serialize the
dispatch span itself — that would be silently reintroducing the
transactional model §3 found no caller needs, at the cost of exactly the
concurrency item 1 was built to preserve.

## 6. A previously-established safety argument this reopens

Worth naming, not resolving here: this project's prior design history
(the 2026-08-17 avatar-integration receipt, cited in
`presence_authority_server.py`'s own module docstring) argues "a lost
cursor can only cause MORE recap being attempted, never less" — an
argument for why `ContinuityCursorTracker` losing state across a restart
is the conservative, safe direction. That argument implicitly assumes
`turn_id` values it advances against are trustworthy. Under the
*current*, unfixed duplicate-ID bug, a corrupted `response_turn.turn_id`
passed to `cursor.advance()` could in principle push a cursor to a value
inconsistent with what a native session actually received — in the
dangerous direction (cursor advances further than truly justified,
causing genuinely-missing content to be silently skipped in a future
recap), not just the previously-accepted-safe direction (extra,
redundant recap). This is a second, independent reason (beyond the raw
duplicate-`turn_id` corruption itself) the fix in §4 is worth prioritizing
before restart persistence, as already recorded — persisting cursor
state built on top of a currently-fixable corruption would durably
encode it.

## Answer to the question this review posed

> Can EngAIn legitimately remember: A request, B request, B response, A
> response — or must it always remember: A request, A response, B
> request, B response?

**The first.** The contract only promises a total, unique order per
`session_id` (§1); every real reader is already written against exactly
that promise and nothing more (§2); tracing the interleaved case against
all five real readers with correctly-unique IDs produces no incorrect
result anywhere (§3); and no existing caller, production or test, was
found to require or assume the transactional alternative (§3). The
minimal fix is atomic/unique/monotonic ID assignment inside `append()`
alone (§4), kept entirely separate from and without reducing item 1's
already-proven provider-dispatch concurrency (§5).

## Open, unresolved by this note

Whether the *product* ever wants two bodies submitting genuinely
simultaneous requests against one `shared_session_id` in the first place
is a different question from whether the *Ledger* must forbid or endure
it — `PresenceRegistry`'s own "one ACTIVE agent at a time" model
suggests a "one conversation, one active speaker" mental model that may
mean this scenario is rare-to-nonexistent in real usage (a human
generally speaks through one door at a time) even though nothing
structurally prevents it and item 1 already builds real, tested
machinery for exactly this case. Not resolved here — noted so it isn't
silently assumed either way.

## Recommendation (for review, not yet implemented)

Fix `SessionLedger.append()`'s `turn_id` assignment to be atomic,
unique, and monotonic per `session_id`, decoupled from physical list
position. Do not add any lock or serialization spanning
`handle_turn()`'s dispatch call. Do not touch item 1's claim mechanism.
No code changes proposed or made in this note.
