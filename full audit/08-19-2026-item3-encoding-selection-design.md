# Item 3 Amendment — Encoding/Storage Selection for the Continuity Journal

Written 2026-08-19, following approval of the crash-consistency model
(`ff9e558`, wording-corrected `46c51aa`). **Design only — no runtime
code, no final encoding decision.** Semantic record derived first, per
instruction, before any syntax/storage comparison.

## 1. Minimum durable event vocabulary

Two event types, not more — derived from the approved crash-consistency
model's own two commit points (§2 of the crash-consistency design), not
assumed:

### `TURN_APPENDED` — request turns only

The standalone commit point (before dispatch begins). A request never
carries provider identity — nothing is dispatched to yet.

### `RESPONSE_COMMITTED` — response turns, **and** cursor evidence, as one record

This collapses what the crash-consistency design called "response-append
+ cursor-advance, committed together as one atomic unit" into a single
*physical* record, not two records inside one transaction. Derived, not
assumed — see §2's reasoning for why this is both correct and strictly
simpler than keeping a separate `CURSOR_ADVANCED` event.

No third event type is needed. `PresenceRegistry`/`SessionClaimRegistry`
have no persisted representation at all (out of scope, unchanged).

## 2. Field derivation — authoritative vs. reconstructible, traced per field

Went through every field the review listed, against the actual code
(`Turn` dataclass, `handle_turn()`'s real call sites, `ContinuityCursorTracker`),
not the dataclass's shape by default.

| Field | Needed on `TURN_APPENDED`? | Needed on `RESPONSE_COMMITTED`? | Why |
|---|---|---|---|
| `shared_session_id` | Optional, defensive only | Optional, defensive only | The per-session journal's own identity (§5 of the crash-consistency design: one journal per `shared_session_id`) already encodes this — redundant as a *functional* requirement, but cheap to include as a self-check that a record hasn't been misfiled into the wrong journal. Not authoritative on its own. |
| `turn_id` | **Authoritative, required** | **Authoritative, required** | The whole ordering identity (item 2). |
| direction (request/response) | Implicit in event type | Implicit in event type | Using two distinctly-named event types makes a separate `direction` field redundant — it's encoded by *which* event this is, not a value inside it. `Turn.direction` exists on the in-memory dataclass because one class serves both; the journal doesn't need that unification. |
| `actor` | **Not required — derivable constant** | **Authoritative, required** | Traced the only real call site (`handle_turn()` step 2): `actor="player"` is hardcoded, never parameterized, for every request turn — and the contract itself (§5: "actor... the player, for a request") makes this a stable, contract-level invariant, not a code accident. Safe to omit and reconstruct as the fixed value "player" for every `TURN_APPENDED`. For `RESPONSE_COMMITTED`, actor is genuinely variable (`result["actor"]`, e.g. "hermes"/"claude_code") — must be persisted. |
| `origin_body` | **Authoritative, required** | **Authoritative, required** | Genuine per-call provenance (§3 of the contract), not derivable from anything else. |
| `payload` | **Authoritative, required** | **Authoritative, required** | The actual content. See §4 for the constraint on how it must be stored. |
| `timestamp` | Non-authoritative, optional | Non-authoritative, optional | Re-confirmed against item 2's own five-reader trace: nothing in `context` filtering, recap building, or cursor advancement ever reads `.timestamp`. Not required for reconstruction *correctness*. Worth keeping anyway as audit/debug metadata, but explicitly labeled as not load-bearing — don't let its presence imply it's part of the replay contract. |
| `snapshot` | Authoritative when present, else absent | Authoritative when present, else absent | Genuinely irrecoverable after the fact (captured image/metadata reference at that exact turn) — contract's own "optional on request, present-if-available on response" (§5). Persist verbatim when present, nothing invented when absent. |
| `provider_id` / `provider_session_id` | N/A — a request has no provider yet | **Authoritative, required — and NOT currently on `Turn` at all** | The one genuinely new field this journal needs beyond what the in-memory dataclass has today. See §2a — required specifically to make cursor state reconstructible from `RESPONSE_COMMITTED` events alone. |
| `model_id` / `launch_options` | Not needed | Not needed | Pure dispatch-time routing parameters (needed to *invoke* a provider), not used by any of item 2's five real readers and not part of `ContinuityCursorTracker`'s own key shape (`(provider_id, provider_session_id)` only, confirmed against its source). Not part of Ledger/Cursor reconstruction. |
| cursor target (as its own field/event) | N/A | **Not persisted as a separate fact — derived** | See §2a. |
| `dispatch_input` (the recap-prefixed text actually sent) | Not persisted | Not persisted | A pure, deterministic function of already-persisted context + cursor state (`ContinuityContextBuilder.build()` takes only `context`, `player_input`, `last_seen_turn_id` — all reconstructible). Persisting it would be exactly the cache-as-authoritative-state mistake the review's own instruction warns against. |
| `prior_context_turns` (adapter audit field) | Not persisted | Not persisted | Trivially `len(context)`, already reconstructible. |

### 2a. Why `RESPONSE_COMMITTED` alone is sufficient for cursor reconstruction — the actual derivation

Checked the *only* production call site of `ContinuityCursorTracker.advance()`
(`shared_session_bridge.py` step 8):

```python
self._cursor.advance(binding.provider_id, binding.provider_session_id, response_turn.turn_id)
```

Every single call advances the cursor to **exactly** the response turn's
own `turn_id` — no other call site, no other value, anywhere in the
codebase. That means cursor state is fully derivable, at replay time,
purely by processing `RESPONSE_COMMITTED` events in order and computing:

```
cursor[(provider_id, provider_session_id)] = max(existing, turn_id)
```

for each one — **provided** each `RESPONSE_COMMITTED` record itself
carries `provider_id`/`provider_session_id` (it doesn't come from
anywhere else; today's `Turn` dataclass has no such fields, since that
information currently only exists transiently in the `binding` object at
dispatch time). This is the one field genuinely *new* relative to
today's in-memory shape — added because it's required for correctness,
not copied in because the dataclass happens to have neighbors.

Consequence: **no separate `CURSOR_ADVANCED` event/record is needed at
all.** This is a real refinement of the approved crash-consistency
model, not a reversal of it — the model called for "response-append and
cursor-advance committed together, atomically, as one unit"; collapsing
them into one *physical* record satisfies that exactly (there is no
possible state where one lands and the other doesn't, because there is
only one write), and is strictly simpler than "two records in one
transaction." Flagged explicitly as a discovered simplification, for
review rather than assumed approved.

## 3. Event identity/idempotency — is `turn_id` sufficient?

Checked directly rather than adding an identifier by default, per
instruction.

**What actually needs distinguishing**: "this exact durable event
already exists" vs. "this is a genuinely new turn" — matters at two
possible moments: (a) during replay itself, or (b) if some upstream
mechanism could cause the same logical write to be attempted twice.

- **(a) Replay**: structurally read-only by design (crash-consistency
  doc's own constraint: replay reconstructs state, never re-invokes a
  provider, and — established here — never re-writes the journal
  either). Reading the same durable file twice always reconstructs the
  same state; replay is idempotent by construction, with no separate ID
  needed to detect "have I processed this already."
- **(b) Duplicate write attempts**: checked whether `/dispatch`/
  `handle_turn()` has, or is expected to gain, its own deduplication
  layer. It doesn't, and traced why that's already handled *upstream*:
  both avatar repos' `hermes_session_adapter.py` already maintain
  `processed_request_ids` (a capped, persisted replay-protection list —
  see item 3's own restart-continuity derivation) specifically to stop
  the *same* mailbox request from ever reaching `/dispatch` twice.
  Idempotency against duplicate submission is already solved one layer
  above this journal, out of scope for it, same as `shared_session_id`
  ownership was already found to be (previous item-3 document).

Given both, **`turn_id` (scoped by its owning per-`shared_session_id`
journal, per §5 of the crash-consistency design) is sufficient** — it
already uniquely and totally orders every turn within its session
(item 2's own proven invariant), which is everything this journal is
actually asked to guarantee. No separate record/event ID is added.

**The one legitimate future trigger, named without acting on it**: a
future compaction, repair, or cross-journal migration tool might want a
stable identity independent of `turn_id`'s per-session meaning (e.g., to
track "which physical bytes correspond to which logical event" across a
rewrite). Compaction is already deferred as its own undesigned problem
(crash-consistency design §5) — this is the same deferral, not a new
one. Revisit if and when that tooling is actually designed, not before.

## 4. Payload durability — the actual constraint, not a premature encoding choice

`Turn.payload` is `str` today — already narrower than "arbitrary JSON."
The concern raised isn't "persist richer types today," it's: don't let
whichever storage mechanism gets picked make plain-JSON-compatible text
the permanent ceiling of what a future `payload` (or `snapshot`) could
ever hold.

**Concrete requirement, independent of which candidate wins below**: the
chosen mechanism must store `payload`/`snapshot` as an **opaque,
length-delimited byte/text blob it returns unmodified** — never a value
it type-constrains, re-encodes, or interprets. A framed file's raw
record segment and a SQLite `TEXT`/`BLOB` column both satisfy this
already; a design that assumed payload was always a JSON scalar and
built that assumption into the framing itself would not. This is listed
as its own row in the comparison below rather than left implicit.

## 5. Candidate comparison

One clarification before the table: the three candidates named aren't
three parallel, mutually-exclusive choices at every layer. **"ZW-shaped
records inside a durable framing mechanism" is a record-*encoding*
choice, not a competing *framing* mechanism** — it can only ever sit on
top of either candidate 1 or candidate 2's own framing (a SQLite
`TEXT`/`BLOB` column full of ZW-shaped text, or a framed file whose
record body is ZW-shaped bytes instead of JSON-ish ones). The table
below reflects that: column 3 inherits every framing-layer property from
column 2 identically (they're the same framing, different record
content), and differs only on the rows that are actually about content
shape, not durability mechanics.

|  | SQLite (1 file/`shared_session_id`) | Framed append-only file | ZW-shaped records + framing (= col. 2's framing, ZW-shaped body) |
|---|---|---|---|
| Atomic compound commit | Native (transaction/WAL) — but moot here, since §2a already collapsed the response+cursor pair into one physical record for *any* candidate | Achievable — single `write()` of one whole framed record + `fsync()`; same "one physical record" property applies | Same as framed file — identical framing |
| Torn-tail detection | Handled by SQLite's own engine — we trust it, don't implement it | Must be self-implemented: length-prefix + checksum, detect on read | Same as framed file |
| Ordered replay | Natural (`ORDER BY turn_id` or insertion order) | Natural — file byte order *is* the order | Same as framed file |
| Human inspectability | Moderate — needs `sqlite3`/a tool, not a text editor | Moderate — text-encoded records are grep-able around the framing bytes; framing itself is a small, fixed-format cost | Potentially better — ZW's own stated design goal is intent-first, human-readable text, if the project's own established ZW conventions are used for the record body |
| Append-only semantics | **Not native** — a general-purpose mutable engine; append-only would be *our own discipline*, not something the engine enforces | **Native** — the format offers no in-place-mutation primitive at all | Same as framed file |
| Stdlib dependencies | `sqlite3` — in stdlib, zero extra dependency | `struct`/`hashlib` or `zlib.crc32`/`os` — all stdlib; **direct precedent already in this codebase** (`hermes_session_adapter.py`'s own `_atomic_write_no_replace` already uses this exact descriptor-based, no-clobber, durable-write style) | Same as framed file, plus whatever ZW-encoding code the project already has (unverified — see §6) |
| Recovery complexity | Low *for us* — SQLite's engine does the hard part; correctness argument becomes "trust SQLite's own crash recovery" | Low-to-moderate, entirely *our* code — no engine to trust, but must be "deliberately tiny and heavily tested" per the review's own explicit caution | Same as framed file |
| Future schema evolution | Good — `ALTER TABLE`/versioned tables, well-trodden | Achievable — needs a `schema_version` field designed in from the start; not automatic | Arguably better *for content shape* specifically — ZW's own schema-agnostic, extra-fields-tolerant, gracefully-degrading design (per the primer) is suited to this by definition, independent of the framing layer's own versioning |
| Project-native semantics | None natively — SQLite's own relational/typed-column model | Neutral — framing carries no opinion about what's inside it | High, by construction — this *is* the point of this column |
| ZW/ZON future compatibility | Possible but awkward (ZW text inside a BLOB column defeats using SQL structure directly) | Fully open — payload segment could be anything | Structurally open — **but not actually built or required today**: confirmed (twice now, item 2 and item 3's own re-check) there is no active ZW→ZON compiler/runtime on this continuity path. "Compatible with" ≠ "already provided by." |
| Cross-session contention | None — one file per `shared_session_id`, matches the approved per-session-journal architecture | None — same, one file per session | Same |
| Compaction path | Mechanically easy (`DELETE`+`VACUUM`) — but policy for *when* it's safe is still undesigned (crash-consistency §5), so this is a future convenience, not a current factor | Requires self-implemented rewrite-and-atomic-rename — more manual, not fundamentally hard, same policy gap applies | Same as framed file |

## 6. Direct answer to the SQLite-specific question

> whether one SQLite file per `shared_session_id` fits the chosen
> per-session-journal architecture, and whether SQLite starts becoming
> an unnecessarily opaque database around what is conceptually an
> append-only continuity stream

It fits mechanically (one file per session, no cross-session locking,
real transactional guarantees). The concern in the question's own
second half is legitimate, though: SQLite is a general-purpose mutable
engine being asked to emulate an append-only stream by *our own
discipline* (never issuing `UPDATE`/`DELETE` in the hot path), not by
anything the engine itself enforces — the exact same "discipline vs.
structural guarantee" distinction that made a single ordered event
stream provably better than two independently-maintained files in the
crash-consistency pass itself (§2 of that document). SQLite genuinely
removes an entire class of self-implemented-correctness risk (we don't
have to prove our own torn-write/checksum logic correct); the framed
file genuinely matches the model's own shape more directly, and has a
working precedent already in this codebase. Neither is wrong; this is a
real tradeoff, not a one-sided call — see §7.

## 7. ZW/ZON/AP — inspected specifically for this role, again

Per instruction: not choosing ZON merely because it's downstream of ZW.
Re-confirmed there is no active ZW→ZON compiler/runtime anywhere on this
continuity path (same negative result as the crash-consistency pass, now
checked a third time from the encoding angle specifically) — making
persistence depend on one would turn item 3 into building that compiler/
runtime first, a categorically larger, unscoped project. Not
recommended. AP is an execution/logic layer for a different problem
(game-logic/strategy) — this journal is not an AP execution problem, and
nothing traced here suggests otherwise. Not pursued.

ZW itself, as a **record-encoding** choice (not framing), remains a
real, legitimate option per [[zw-native-language]]'s own corrected
hierarchy — "the project gives ZW its concrete shape" — meaning if this
journal's record body is ever expressed in ZW, its shape would need to
be *defined here, for this exact role*, not borrowed from an existing
canonical form (none exists, confirmed). Not designing that shape in
this pass — that's an encoding-content decision that follows *after* a
framing mechanism is chosen, not before.

## Current status (matches the review's own framing)

- Crash model: **GREEN** (approved, wording-corrected).
- Persistence scope: **GREEN** (approved).
- Per-session journal: **GREEN** (approved, and independently
  re-confirmed here — both framing candidates satisfy it identically).
- Semantic record: derived — two event types, one field table, one
  concrete simplification found (`RESPONSE_COMMITTED` absorbs cursor
  evidence, no separate `CURSOR_ADVANCED` record) — **flagged for
  review, not assumed approved.**
- Event identity: `turn_id` proven sufficient; no new identifier added.
- Payload durability: named as a concrete constraint on any candidate,
  not deferred to "figure it out later."
- Encoding: **still undecided.** Leaning stated, not chosen: the framed
  append-only file has a direct precedent already in this codebase and
  matches the model's own append-only shape structurally rather than by
  discipline; SQLite trades that structural match for a real, working
  transactional/recovery engine we wouldn't have to prove correct
  ourselves. Both are legitimate; this document does not pick a winner.
- ZW as record content: real, open, explicitly not designed in this
  pass, and explicitly not faked to claim compliance with something
  the project hasn't actually established for this role.

Not yet implemented. Next steps, in order, each wanting its own review:
final framing choice, then the actual record-encoding shape (including
whether ZW is used), then implementation.
