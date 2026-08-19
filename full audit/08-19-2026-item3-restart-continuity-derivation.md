# Item 3 Design Investigation — What Restart Continuity Actually Requires

Written 2026-08-19. **Design/re-derivation only — no runtime code
touched, no persistence implemented.** Per explicit instruction: the
original TODO framing ("ledger/cursor persistence across a restart")
was written before this session discovered that a dispatched recap
becomes permanent native-side state regardless of what EngAIn's own
process does — persisting every Python object without accounting for
that would solve the wrong problem. Re-opening the question rather than
carrying the old framing forward:

> After an EngAIn restart, what continuity state is actually lost, which
> of it can already be reconstructed from native/provider state or
> receipts, and which state genuinely requires EngAIn persistence?

## Method

Traced, component by component, whether each one (a) has any disk I/O
at all today, (b) is lost on a `presence_authority_server.py` restart,
and (c) if lost, whether anything else in the system already makes that
loss survivable. Confirmed by grep, not assumed: `presence_authority_server.py`
and all four of its core modules (`PresenceRegistry`, `SessionLedger`,
`ContinuityCursorTracker`, `SessionClaimRegistry`) have **zero** disk
I/O anywhere — the entire authority is 100% in-memory today, full stop.
Everything it owns is lost on restart; the real question is which losses
matter and why.

## Component by component

### `SessionLedger` — genuinely lost, no reconstruction path found

No persistence, no load path (confirmed in item 2's own verification:
every `SessionLedger()` construction site starts empty). On restart,
every `shared_session_id`'s turn history is gone — a fresh dispatch for
a previously-active `shared_session_id` starts a brand-new list at
`turn_id=0` again, with no relationship to what existed before.

**But the functional impact is narrower than "everything is lost."**
Traced concretely: immediately after a restart, `handle_turn()` step 4
(`context = [... if t.turn_id < request_turn.turn_id]`) is necessarily
`[]` for the first post-restart turn on any `shared_session_id`, since
the fresh Ledger has nothing in it yet — so no recap gets built,
regardless of what the (also-reset) cursor says. The dispatched provider
call carries only the bare `player_input`.

For the **same native provider session that was already active** before
the restart, this doesn't actually break continuity — see the next
section: the vendor's own transcript survived the restart untouched, and
`--resume <provider_session_id>` picks it back up exactly where it left
off, EngAIn's own Ledger loss notwithstanding. The genuine, substantive
loss is narrower and sharper: **any provider/door that would need to be
caught up on pre-restart history via EngAIn's own Ledger cannot be,
after a restart, because the Ledger has nothing to catch it up with.**
Cross-provider continuity of pre-restart history is what's actually at
risk — not same-provider continuation.

### `ContinuityCursorTracker` — lost, but consistently so with the Ledger

Also unpersisted, resets every `(provider_id, provider_session_id)` to
"never seen anything" (`-1`) on restart. Checked whether this creates a
*new* inconsistency on its own: it doesn't, as long as it resets
*together* with the Ledger — recapping "everything currently in the
Ledger" onto a Ledger that currently has nothing in it is a no-op,
consistent with the cursor's own reset. The danger would only appear if
a future design persisted one of these two without the other (e.g.
cursor survives but Ledger doesn't → cursor wrongly claims knowledge of
turns that no longer exist; Ledger survives but cursor doesn't → every
native session gets redundantly re-recapped the entire persisted
history on its next turn). **Constraint for any future persistence
design: Ledger and Cursor must be persisted and restored as one
consistent pair, never independently.**

### `shared_session_id` relationships — not EngAIn-owned state at all

Checked whether EngAIn persists, anywhere, which body/door "belongs to"
which `shared_session_id`. It doesn't, and there's no evidence it needs
to: `ENGAIN_CONTINUITY_SHARED_SESSION_ID` is read fresh from the
environment by each avatar worker at dispatch time (confirmed in both
avatar repos' `hermes_session_adapter.py`) — supplied by whatever
launches the worker, not remembered by EngAIn. Every `/dispatch` request
body already carries its own `shared_session_id` explicitly, every
single call. There is nothing here for EngAIn's own restart to lose.

### Provider-session bindings (`PresenceRegistry`, `SessionClaimRegistry`) — ephemeral by design, already self-healing

Also unpersisted, also reset on restart. But both are deliberately
short-lived by their own stated contracts — Presence is a renewable
lease ("is X reachable *right now*"), and the claim registry is
"a mutex held only for the duration of one dispatch call." Both
self-heal on the very next real call (`register()`/`claim()` runs fresh)
with no special handling needed. This matches the original 2026-08-17
receipt's own framing, and nothing found here contradicts it — no
persistence need here, then or now.

### Native provider transcript/state — already durable, already outside EngAIn's boundary

This is the piece that changes the shape of the whole question. Each
native provider (Hermes, Claude Code) maintains its **own**, vendor-side,
durable session transcript — entirely outside EngAIn's process, outside
either avatar repo's own persistence, unaffected by an EngAIn restart.
`--resume <provider_session_id>` is exactly how every dispatch already
reaches it. This is *why* same-provider continuation survives an EngAIn
restart even with zero EngAIn-side persistence today: the provider
itself remembers, independent of anything EngAIn does.

Checked what the avatar repos' own on-disk state actually holds, since
it sounds adjacent: `.godot/engain_hermes_session.json` (both avatar
repos, identical shape) persists exactly five fields — `profile`,
`companion_ref`, `provider`, `model`, `session_id` (validated against
the frozen constant, not "learned") — and `processed_request_ids`, a
capped (`MAX_PROCESSED_REQUEST_IDS = 256`) replay-protection list. **This
is not a continuity/history store** — it's narrow identity-consistency
plus idempotency, nothing that records what was actually said. Worth
being precise about this so it isn't mistaken for a partial continuity
persistence layer that already exists; it isn't one.

### ZW/ZON/AP representations — no active consumer, checked again specifically for this

Re-confirmed (same grep item 2 already ran, re-run here specifically in
the persistence context in case a different angle surfaced something):
zero references to `SessionLedger`, `Turn`, `turn_id`, or
`ContinuityCursorTracker` anywhere outside `tier1/engainos/`, including
Trixel32d. Nothing here to persist through, retrofit, or check
compatibility against — consistent with [[zw-native-language]]'s own
recorded caveat that a "ZW"/"ZON"/"AP" name appearing somewhere is not
evidence of an active implementation behind it.

### Existing receipts/transcripts on disk — real, but not a viable reconstruction source

Every live-proof script (`tier1/engainos/tools/live_*.py`) writes to a
**fixed**, script-specific path under `runtime/logs/` — e.g.
`LIVE_DISPATCH_MUTEX_CONTENTION_PROOF_V1.report.json` — overwritten on
every run of that script, not appended. These are proof-run artifacts,
not a production dispatch journal; they capture "did this specific proof
pass, most recently," not "everything that was ever said." Mailbox
request/response files (`request.json`/`response.json`, both avatar
repos and `mailbox_request_handler.py`) are actively claimed, processed,
and unlinked as part of normal operation — transient by design, not
accumulated. **No existing on-disk artifact today could reconstruct
production Ledger history if asked to.**

## What this reframes

The original item 3 framing treated "ledger/cursor persistence" as one
obvious missing feature to build. Traced against what's actually true
today, the real shape is narrower and more specific:

- Same-provider conversational continuity across a restart **already
  survives**, today, with zero EngAIn-side persistence — because the
  vendor's own native transcript is the thing actually carrying it.
- What's genuinely lost is EngAIn's own cross-provider catch-up
  capability for **pre-restart** history specifically — a provider that
  wasn't already active before the restart, brought in afterward, gets
  no recap of anything that happened before the process came back up.
- Presence/claim ephemerality was already correctly identified as fine
  as-is; nothing here changes that.
- `shared_session_id` itself was never EngAIn's state to lose.
- Any future persistence design must treat Ledger+Cursor as one
  consistent unit, never independently.

## Open question this note deliberately does not resolve

Whether the narrower, real gap — **cross-provider catch-up of
pre-restart history** — is common or valuable enough in actual usage to
justify building and maintaining a persistence mechanism for it, versus
documenting it as an accepted, honest limitation (same shape as the
already-accepted Presence/claim ephemerality). This is a product-weight
judgment, not something this trace can settle on its own — named
explicitly so it isn't silently assumed either way, same discipline as
item 2's own open question about simultaneous multi-body requests.

If persistence *is* judged worth building, this trace narrows what it
would actually need to cover (Ledger+Cursor, as a pair, per
`shared_session_id`) and rules out several things that would otherwise
be tempting but aren't load-bearing: no need to persist Presence or
claims, no need to persist or reconstruct anything from ZW/ZON/AP, no
existing on-disk artifact to build on top of — any such mechanism would
be new, not an extension of something already partially there. A
different-shaped alternative was also considered, not designed: rather
than EngAIn persisting its own copy of history, asking the still-durable
native provider transcript itself to supply a summary on reconnect —
not pursued further here since no dispatcher adapter currently exposes
any read-back capability against a native transcript (today's adapters
only ever write via `--resume`), which would itself be new, non-trivial
work, and a different kind of change than "persist a Python dict."

## Recommendation

Not yet — this note is diagnosis, not a proposal. Before any
implementation: get a decision on the open product question above. If
the answer is "yes, worth building," the next design pass should treat
Ledger+Cursor persistence as one paired mechanism scoped specifically to
restoring cross-provider catch-up capability, not a general "make
everything durable" effort — and should re-check, at implementation
time, whether the vendor-transcript-summary alternative named above has
become more feasible before committing to a from-scratch persistence
format.
