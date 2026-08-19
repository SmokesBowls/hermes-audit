# Item 3 Amendment — Crash-Consistency Model for `SessionLedger` + `ContinuityCursorTracker` Persistence

Written 2026-08-19, after the product decision on
`08-19-2026-item3-restart-continuity-derivation.md`: the cross-provider
restart gap is **not** accepted as a permanent limitation; persistence
is worth building, scoped to EngAIn-owned continuity state only. This
document is the required crash-consistency design pass before any of
that gets implemented. **Design only — no runtime code, no encoding
selected.**

## 1. The failure windows, traced against the actual code

`handle_turn()`'s real step order (unchanged by items 1/2, both already
proven correct against it) is what every window below is measured
against: step 2 (request append) → step 4/5 (context read, dispatch) →
step 6 (re-validate) → step 7 (response append) → step 8 (cursor
advance). The in-memory ordering already enforces request-before-dispatch
and response-before-cursor-advance; the question is what happens when a
crash lands between durability points that don't yet exist.

| # | Window | Reconstructed state after restart | Consequence |
|---|---|---|---|
| 1 | Crash after request turn durable, before dispatch | Ledger has the request; no response exists; cursor unaffected | **Orphan request** — but this is not a new failure mode. Gate 2 (§7 of the contract) already requires exactly this to be a valid, tolerated state: "a request may be appended even while nobody is currently on the other side." No special recovery needed beyond what the system already does for any unanswered request. |
| 2 | Crash after provider returns, before response turn durable | Ledger has only the request; the *native* provider's own transcript already contains the exchange (durable, vendor-side, per item 3's own derivation) — but EngAIn's Ledger does not | **Missing recap**, bounded and inherent — not eliminable by any journal-ordering design, only by making the request-durable→dispatch→response-durable path as short as possible. See §4: no design can make "provider call succeeded but our own write hadn't landed yet" impossible when the provider call is an external, non-transactional, possibly-multi-second subprocess. This is the one honestly-irreducible risk window; it is bounded (one exchange, one shared_session_id, one crash), not open-ended. |
| 3 | Crash after response turn durable, before cursor advance durable | Ledger correctly has the response; cursor for that `(provider_id, provider_session_id)` is stale — still shows the pre-exchange value | **Safe duplicate recap.** The next dispatch to that same native session recaps a turn it already actually produced. This is exactly the pre-existing, already-endorsed safety argument ("a lost cursor can only cause more recap, never less") — now trustworthy again specifically because item 2 closed the `turn_id` corruption that had put that argument at risk. |
| 4 | Crash after cursor advance durable, before the HTTP response reaches the caller | Ledger and cursor are both **fully, correctly durable** | **Not a Ledger/Cursor consistency issue at all** — this is a caller-notification ambiguity (the caller doesn't know its request succeeded), identical in shape to what any HTTP service has whenever a response is lost after the server-side effect committed. Out of scope for this journal design; would need an idempotency key on the *caller's* retry to fix, which is separate, unbuilt, unscoped-here machinery. |
| 5 | Process kill mid-write of a single event record (torn write) | Whatever the storage mechanism leaves behind — a partial/unparseable record, *unless* the mechanism guarantees atomic, all-or-nothing appends | **Unrecoverable corruption is possible** unless the eventual storage choice provides: an event either lands whole or not at all, and a torn tail is *detectable*, never silently accepted as valid. This is a required property of whatever encoding gets chosen later (§3) — not resolved here, but the requirement is non-negotiable regardless of which encoding is picked. |
| 6 | Restart finds a partially-written tail | If window 5's property holds: the torn record is detected and discarded; replay proceeds as if the crash had happened one event earlier (reduces to window 1, 2, or 3, whichever event was mid-flight) | **Safe, by construction** — provided detection is real. A corrupt tail must never be treated as valid data, and discarding it must never discard anything *before* it. This is the recovery-time enforcement of window 5's requirement. |

**Structural constraint that rules out an entire failure category by
design**: replay must be pure, read-only reconstruction of Ledger+Cursor
state from durable events — it must never re-invoke a provider. As long
as this is honored, **duplicate native provider invocation** from
restart/replay itself is not merely unlikely, it's architecturally
impossible, and doesn't need a runtime guard to prevent — only a design
rule to not violate. Likewise, **orphan response** (a response with no
matching request) is impossible by construction as long as the request's
durability write completes before dispatch begins (see §4) — a response
event can never be journaled without its request already present earlier
in the same ordered stream.

## 2. Single durable ordering source, not two independently-authoritative files

Confirmed, not merely asserted: table row 3 shows the *only* survivable
divergence between Ledger and Cursor durability is "response durable,
cursor stale" (safe). The reverse — cursor claiming knowledge of a turn
whose response was never actually durably recorded — is the one state
that must be **structurally unreachable**, not just avoided by careful
sequencing. Two independently-written files/records (`ledger.json` +
`cursor.json`, or two separately-updated database rows) require an
*extra*, explicit cross-file transaction guarantee to prevent that
reverse case — the exact same care a single ordered stream gives for
free, plus more moving parts. A single, strictly-ordered durable event
stream — `TURN_APPENDED` / `CURSOR_ADVANCED`, one writer, replayed in
order — makes "cursor ahead of its own turn" unreachable by
construction: a `CURSOR_ADVANCED` event can only be written (and can
only be replayed) after its corresponding `TURN_APPENDED(response)`
already exists earlier in the same stream. **Recommendation: one
ordered durable event stream, not two independently-authoritative
persistence files.** This holds regardless of which storage mechanism
eventually implements it (§3) — a single-writer append-only file and a
single ACID transaction per commit point both satisfy this; two
separate files/tables updated independently do not, without rebuilding
the same guarantee by hand.

**Commit points within that one stream are still per-step, not one
giant transaction spanning a whole turn.** Per Gate 2's own asymmetry
(request is real regardless of whether anyone answers) and items 1/2's
already-established rule (never lock or hold a transaction across a
provider dispatch), there are exactly two commit points per turn, both
inside the one stream:
1. `TURN_APPENDED(request)` — committed before dispatch begins.
2. `TURN_APPENDED(response)` + `CURSOR_ADVANCED` — committed together,
   as one atomic unit, after dispatch and Gate 11 validation both
   succeed.

**On the cursor event's meaning** (this review's own correction, worth
stating explicitly since it's easy to get subtly wrong): `CURSOR_ADVANCED`
must mean "EngAIn has durable evidence this native provider actually
incorporated history through turn N" — never "we attempted to send it."
The existing in-memory code already gets this right by construction:
`cursor.advance()` is only ever called after step 6's validation and
step 7's successful append, never right after step 5's raw dispatch
return. The persisted event must be written at that exact same logical
point, not earlier — preserving the existing semantic, not changing it.

## 3. Encoding: not selected — the required properties are

Per instruction, no storage mechanism is chosen here. What's established
is the semantic record and the properties any candidate mechanism must
provide:
- Atomic, all-or-nothing event append (§1, window 5).
- Detectable torn tail on read, distinguishable from valid data (§1,
  window 6).
- One writer per `shared_session_id` (naturally matches item 2's own
  per-session_id lock — see §5 for why per-session, not global).
- Strict write-order preservation matching program order (request before
  dispatch; response+cursor-advance together, after validation).

SQLite, a plain append-only file with length-prefixed/checksummed
records, or any other mechanism providing those four properties are all
still open — that choice belongs to a later, separate pass, once this
semantic record is agreed.

## 4. The durability point of `/dispatch`

> At what exact moment may EngAIn truthfully consider a request turn,
> response turn, and cursor advance committed?

- **Request turn**: the instant `TURN_APPENDED(request)`'s durable write
  is flushed — which must happen **before** dispatch (step 5) begins.
  This is both a correctness requirement (rules out orphan responses,
  §1) and an honesty requirement (the player's words are asserted real
  the moment they're accepted, per Gate 2, not held hostage to a slow,
  external provider call that might take up to 90–120 seconds per
  item 1's own measured timeouts).
- **Response turn**: the instant `TURN_APPENDED(response)`'s durable
  write is flushed — necessarily after the provider call returns *and*
  after Gate 11's actor-mismatch check passes (a response that fails
  that check is never appended at all today, unmodified by this design).
- **Cursor advance**: the instant `CURSOR_ADVANCED`'s durable write is
  flushed — logically bound to the response turn's own commit (§2's
  atomic pairing), never separately or earlier.
- **The HTTP `200` to the caller must be the last thing that happens**,
  strictly after the response+cursor-advance durable write completes.
  Sending `200` before that write is flushed would be exactly the
  dishonest claim this question warns against — a state that exists only
  in RAM, asserted to the caller as if it survived a kill it wouldn't
  have.

## 5. Retention / recovery scope

- **One journal per `shared_session_id`, not one global journal.** This
  inherits, for free, items 1 and 2's already-proven principle that
  different sessions must never contend — a per-session journal never
  blocks or interferes with a different session's journal, the same way
  the per-session `SessionLedger` lock and the `(provider_id,
  provider_session_id)` dispatch claim already don't. A single global
  journal would either need a global write lock (reintroducing exactly
  the cross-session contention items 1/2 worked to eliminate) or
  session-tagged interleaving-tolerant replay logic — more machinery for
  no discovered benefit.
- **No ordering requirement across different `shared_session_id`s** —
  re-confirmed directly from the contract, which never claims any
  relationship between sessions; each is its own independent "page"
  (§2 of `SHARED_SESSION_CONTINUITY_CONTRACT_v1.md`).
- **Compaction: not yet safe to design.** A turn could only be provably
  safe to discard once every `(provider_id, provider_session_id)` that
  could ever ask for a recap of it has already caught up past it — but
  nothing in the current architecture tracks "every native session that
  has ever been active for this `shared_session_id`," only the
  *currently* active one (Presence). Building that tracking is new
  scope beyond this journal's job. Until it exists, the honest default
  is **no automatic compaction**, matching the contract's own explicit
  deferral (§8: "retention or pruning policy... is not decided here").
- **What evidence allows discard, today**: none that can be proven
  permanent. Provider-neutral dispatch means any `provider_id` could in
  principle be introduced to a `shared_session_id` at any future time —
  there is no closed set of "consumers" to wait out. A real discard
  policy would need an operational decision (e.g., "a session is
  considered closed after N days of inactivity") layered on top — a
  policy call, not a technical derivation, and out of scope here.
- **Clean tail vs. corruption at startup**: per §1 window 6 — detect via
  whatever atomicity/boundary mechanism §3's eventual encoding choice
  provides; discard a detected torn tail and nothing before it; never
  treat an undetectable-but-actually-torn record as valid (this is why
  §3's properties are non-negotiable, not a nice-to-have).

## 6. ZW/ZON/AP, inspected specifically for this role — negative result, reported honestly

Checked whether the project's own established ZW/ZON/AP material already
has a project-specific shape that fits a continuity journal, per
instruction, rather than assuming either way. Finding: **no established,
project-specific shape exists for this role.** Nothing in the `markor/zw/`
archive defines an event-log/journal block type, and — re-confirmed
directly, not assumed — there is no existing cross-reference anywhere
between ZW/ZON/AP and `SessionLedger`/`turn_id`/`ContinuityCursorTracker`
(same grep item 2 ran, and item 3's derivation re-ran specifically in
this context; both came back empty).

What *is* true, worth naming without overselling it: ZW's own generic
definition (`zw primer V0.1 gpt5.0.txt` — schema-agnostic, block-based,
each block self-contained with `id`/`type`/`payload`, tolerant of
unknown fields) is structurally not unlike what a `TURN_APPENDED`/
`CURSOR_ADVANCED` event record wants to look like in the abstract. That
is a resemblance to ZW's *generic* pattern, not a discovered,
already-established fit — adopting it here would be a new design
decision at encoding-selection time (§3), not something this trace found
already built and waiting. Per instruction, not proposing it as "the"
answer, and not fabricating a "ZW persistence format" to claim
compliance with something the project never actually defined for this
purpose. If the eventual encoding pass wants to consider it, that's a
real, honestly-available option — reported here as exactly that and
nothing more.

## Explicitly out of scope (unchanged from instruction)

Persisting `PresenceRegistry`; persisting `SessionClaimRegistry`;
persisting `shared_session_id` ownership; copying native Hermes/Claude
transcripts into EngAIn; production cutover; ZW/ZON/AP redesign. None
touched by this document.

## Summary for review

- Six failure windows traced against the real code; five are safe or
  already-tolerated by existing contract gates; one (window 2, provider
  succeeded but the write hadn't landed) is an honestly bounded,
  irreducible risk inherent to any design where durability follows an
  external, non-transactional provider call — named, not hidden.
- One durable, strictly-ordered event stream per `shared_session_id`,
  not two independently-authoritative files — proven necessary, not
  merely preferred, by the asymmetry in table row 3 vs. its reverse.
- Two commit points per turn within that one stream (request-before-
  dispatch; response+cursor-advance together, after validation) — never
  one transaction spanning the provider call itself.
- The durability point for the HTTP `200` is strictly after
  response+cursor durability, never before.
- Encoding deliberately not chosen; four required properties named
  instead.
- ZW/ZON/AP: checked specifically for this role, genuinely nothing
  established found — reported as a negative result, not filled in with
  an invented one.

Not yet implemented. Encoding selection and the actual persistence
implementation are the next two passes, in that order, each wanting its
own review before code — same sequence as items 1 and 2.
