# ContinuityContextBuilder: Real Runtime Recap, Real Mailbox Requests

Written 2026-08-17, continuing directly from the prior day's
`ProviderSessionBinding` work. That proof was real but not production:
the recap text sent to Claude Code and back to Hermes was hand-written
inside the proof script itself. Nothing about a real mailbox request would
ever arrive pre-annotated with "here is what the other provider said." This
closes that gap on both stated fronts: the builder moved into the real
dispatch path, and the proof repeated through actual request/response
files with no manually constructed recap anywhere in this session.

## ContinuityContextBuilder

`tier1/engainos/core/continuity_context_builder.py`. One rule: a recap is
built only when the actor about to answer differs from whoever produced
the most recent Ledger response — i.e. exactly at a provider switch, never
otherwise. A provider resuming its own prior turn already has that memory
natively via `--resume`; injecting a recap regardless would be the "second,
competing memory" both provider adapters' own docstrings already forbid.
Stateless — every call is a pure function of the context and input handed
to it.

Wired into `shared_session_bridge.py`'s `handle_turn()` at exactly one
point, step 5: `dispatch_input = self._continuity.build(context,
player_input, binding.agent_id)`, dispatched instead of the raw
`player_input`. Step 2's Ledger append — the bare, unmodified thing the
player actually said — happens earlier and is untouched by this; what gets
*recorded* never depends on who ends up answering, only what gets
*dispatched* does.

5 new tests: no-context passthrough, same-provider-continuing gets no
recap, a genuine switch gets a recap containing the full prior exchange
(not just the last pair), and — mirroring the live proof's own decisive
step — switching back to a provider used two turns ago still recaps the
intervening switch, since what matters is the *most recent* responder, not
provider history further back.

## mailbox_request_handler.py

The real file-based request/response layer this was missing entirely.
`engain.mailbox_request.v1` in (`shared_session_id`, `origin_body`,
`player_input`, optional `snapshot`), `handle_turn()`'s own return shape
out, unmodified. Deliberately not a persistent polling daemon — that's a
separate, larger decision the same-day-earlier full audit already flagged
as needing its own review; this is the translation layer only, callable
once per request the same way the existing avatar repos'
`hermes_session_adapter.py --publish-request`/`--claim-response` are also
invoked per request rather than as a service.

5 new tests, including the one that matters most here: a bare request file
with ordinary human-shaped `player_input`, and after processing, the
Ledger's own recorded request turn is verified to equal that bare text
exactly — proving no recap leaked into what gets recorded, symmetric with
`ContinuityContextBuilder`'s own guarantee about what gets dispatched.

## Regression

199/199 (189 prior + 5 `ContinuityContextBuilder` tests + 5 mailbox handler
tests). One pre-existing structural test
(`test_bridge_holds_no_conversation_state_of_its_own`)
needed updating: `SharedSessionBridge` now legitimately holds a fourth
attribute, `_continuity` — the stateless builder — alongside presence,
ledger, and dispatcher. Both single-provider live-proof tools' identical
structural checks updated the same way.

## The mailbox proof — real, first run, no manually constructed recap

`live_cross_provider_mailbox_portability_proof.py`. Same Hermes -> Claude
Code -> Hermes scenario as the prior day's proof, but every `player_input`
written to a request file is bare:

```
01_hermes_remember.request.json:
  "player_input": "Remember the phrase: granite lantern. Reply with exactly: noted."

02_claude_recall.request.json:
  "player_input": "What phrase did I just ask you to remember? Reply with only the phrase, nothing else."

03_hermes_recover.request.json:
  "player_input": "What did the other assistant just tell me? Reply with only the phrase, nothing else."
```

No provider names, no prior-turn text, no recap prose anywhere in any
request file — confirmed by reading the files directly off disk after the
run, not just trusting the script's own claim. All three real request
files and three real response files are preserved at
`runtime/mailboxes/cross_provider_proof/` as evidence, not written to a
temp directory and discarded.

Outcome, identical shape to the prior day's proof, produced through a
materially different mechanism this time:

```
shared_session_id:            shared-11fe9a0fe05c4e7da1ed81363113d4c7
hermes_provider_session_id_1: (real, minted, reused unchanged in step 8)
claude_provider_session_id:   (real, minted)

turn 0-1: hermes,   via mailbox file 01  -> "noted."
turn 2-3: claude_code, via mailbox file 02 -> "granite lantern"
turn 4-5: hermes (same stale native session), via mailbox file 03 -> "granite lantern"
```

Hermes's second answer, exactly as before, could only have come from the
Ledger — its native transcript still only ever contained the "remember
granite lantern"/"noted." exchange — but this time the mechanism that
supplied it was the production dispatch path (`ContinuityContextBuilder`
inside `handle_turn()`), triggered automatically by an ordinary file on
disk, not by anything this proof script wrote into the request itself.

## Unchanged, deliberately

`agent_gateway.py`, `SessionClaimRegistry`/presence authority server,
`PresenceRegistry`'s data model — none touched. No persistent mailbox
polling worker was built; this remains the translation layer only, exactly
as scoped.
