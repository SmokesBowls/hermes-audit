# Continuity Identity Boundary Correction: Native Session, Not Actor Label

Written 2026-08-17, same day as the `ContinuityContextBuilder`/mailbox
work this corrects. Caught in review before anything was pushed: the
recap-trigger decision compared `agent_id`/actor labels, which is not the
same thing as "does this native session actually have this memory," and
four concrete cases show why the difference matters:

- Same actor, replaced native session (expiry, failure) → the old check
  would skip the recap; the fresh session has seen nothing.
- Different door/actor, same still-current native session → the old check
  would inject a redundant recap into a session that already has it.
- A provider switch could reuse an agent-facing label, hiding a needed
  recap the same way.
- More generally: actor is a policy/presence-facing label, not a claim
  about what any particular native transcript contains.

## The corrected identity

`(provider_id, provider_session_id)` — the exact pair
`ProviderSessionBinding` already carries — names the actual native memory
container. `continuity_cursor_tracker.py`'s new `ContinuityCursorTracker`
records, per that pair, the newest Ledger `turn_id` known to have reached
it via a *successful* dispatch round trip. `-1` means never dispatched to.
`advance()` is monotonic — never regresses.

`continuity_context_builder.py`'s `build()` no longer takes or compares
any actor/agent identity at all. It takes `last_seen_turn_id` and recaps
exactly the Ledger turns with `turn_id` greater than it — not "all of
context" once triggered, the genuinely missing suffix only, which is what
makes "recap only what was missed" possible instead of always recapping
from the beginning.

`shared_session_bridge.py`'s step 5 now looks up
`cursor.last_seen_turn_id(binding.provider_id, binding.provider_session_id)`
before building the dispatch input, and `cursor.advance(...)` is called
only after step 7's successful, validated Ledger append — never inside a
failure path, never speculatively before dispatch. A rejected or failed
turn can therefore never be mistaken, later, for one a native session
actually received.

**Consequence for callers:** `ContinuityCursorTracker` must be
constructed once and explicitly shared across every `SharedSessionBridge`
instance touching the same session — exactly the same explicit-sharing
discipline already required of `PresenceRegistry`/`SessionLedger`. Both
proof scripts (`live_cross_provider_portability_proof.py`,
`live_cross_provider_mailbox_portability_proof.py`) construct three
separate bridge instances (one per `provider_dispatch`) and were updated
to pass one shared tracker to all three — without that, each bridge would
silently fall back to its own fresh tracker and every dispatch would look
like "never seen," recapping unconditionally and defeating the fix.

## Tests added, one per required scenario

`test_continuity_cursor_tracker.py` — 4 tests on the tracker in isolation:
unknown pair reads `-1`, advance-then-read, independent tracking per
`(provider_id, provider_session_id)` pair (not `agent_id` alone, not
`provider_id` alone), and monotonic advance never regressing.

`test_continuity_context_builder.py` — rewritten for the `last_seen_turn_id`
signature: no-context passthrough, cursor-covers-context skips the recap,
cursor-behind-context recaps, and recap includes only the strictly-missing
suffix (not the full context) once triggered.

`test_continuity_identity_boundary.py` — the six bridge-level scenarios
from review, each exercised through real `SharedSessionBridge.handle_turn()`
calls with a shared tracker and a recording fake dispatcher:

1. Same actor, different provider session → recap.
2. Same provider and actor, replacement native session → recap
   (mechanically identical to 1 — the fix does not distinguish *why* the
   native session changed).
3. Different body, same native session → no duplicate recap.
4. Switch away and back to an older native session → recap contains only
   the missed turn, not the session's own earlier turn it already
   produced.
5. Newly created native session → recap contains everything currently
   available.
6. Failed dispatch (response actor mismatch, standing in for any dispatch
   failure) → cursor stays at `-1`; confirmed a subsequent successful call
   to the same native session still recaps the turn that was appended but
   never actually acknowledged.

One test-fixture bug caught and fixed during this pass, not a logic bug:
the first version of the recording fake dispatcher echoed its own
`dispatch_input` back inside its canned response text, which meant a
later recap of *that* response would incidentally re-contain whatever the
dispatcher itself had just been recapped with — making "is X excluded"
assertions meaningless regardless of whether the real logic was correct.
Fixed to return a response with no dependency on its own input.

Full suite: 208/208.

## Both live proofs re-run with the corrected boundary

Both scripts were also simplified in the same pass: the first cross-
provider proof previously hand-wrote its own recap prose (meaning it could
never have caught this bug — a hand-written recap doesn't exercise
`ContinuityCursorTracker` at all). Both now submit bare `player_input`
throughout, matching the mailbox proof's existing discipline, and both add
an explicit assertion on `cursor.last_seen_turn_id(...)` confirming the
original Hermes native session's cursor advanced exactly once, at the
final step, never bumped by the intervening Claude Code turn.

Direct call proof (`live_cross_provider_portability_proof.py`), phrase
`amber compass`:

```
shared_session_id:            shared-586d2bc6190f4c3ab43c4ccea4068593
hermes_provider_session_id_1: 20260817_012114_7ba318
claude_provider_session_id:   76ea207a-0d1e-455a-9e78-bc508674448b

hermes:      "remember: amber compass" -> "noted."
claude_code: [cursor-driven recap]     -> "amber compass"
hermes (same original native session, cursor-driven recap) -> "amber compass"

cursor.last_seen_turn_id("hermes", hermes_provider_session_id_1)
    == the step-8 response's own turn_id, exactly — confirmed, not assumed
```

Mailbox proof (`live_cross_provider_mailbox_portability_proof.py`), phrase
`granite lantern`, three real request/response file pairs under
`runtime/mailboxes/cross_provider_proof/`, re-confirmed bare on this run
too:

```
02_claude_recall.request.json:
  "player_input": "What phrase did I just ask you to remember? Reply with only the phrase, nothing else."

03_hermes_recover.request.json:
  "player_input": "What did the other assistant just tell me? Reply with only the phrase, nothing else."
```

Both proofs: all checks passed, first re-run after the correction.

## Scope, restated per review

This — both proof scripts, both days' worth of work — is a file-mailbox
integration proof for `mailbox_request_handler.py`, the translation layer
built inside `tier1/engainos`. It is not integration with the existing
`engain_avatar`/`godot_engain_3d_avatar` avatar-body mailboxes
(`dragon2d`/`dragon3d`, `hermes_session_adapter.py`'s own protocol) — those
remain exactly as the earlier full audit described them, separate and
unconnected. `08-17-2026-continuity-context-builder-mailbox-proof.md` has
been amended in place with the same clarification.

## Unchanged, deliberately

`agent_gateway.py`, `SessionClaimRegistry`/presence authority server,
`PresenceRegistry`'s data model, `ProviderSessionBinding` itself — none
touched by this correction. This was entirely about which identity a
recap decision keys on, not about presence, claims, or the binding shape.
