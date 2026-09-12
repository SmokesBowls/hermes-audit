# 09-12-2026 — Where a coordination_report/event belongs in EngAIn's /dispatch path (discovery only, no implementation)

## Trigger

Screenshot confirmed the ChatGPT "avatar dragon" persona reports no
configured Action/tool (`Tool name: none. Operation name: none.`) — the
existing authorization gate is the Hermes Editor dock's own Execute
button, not a ChatGPT Action-confirmation dialog. That question is
settled; not revisited here. This note is a separate, narrower task the
user asked for next: trace EngAIn's real `/dispatch` handler and
`SharedSessionBridge.handle_turn()` (in
`/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn`) to find the
correct authoritative place to add a `coordination_report`/event input,
kept structurally separate from `player_input`. **Discovery only — no
code changed in this repo or EngAIn as part of this note.**

## Files read directly

- `tier1/engainos/server/presence_authority_server.py` — `_handle_dispatch()`
- `tier1/engainos/bridgeroom/shared_session_bridge.py` — `SharedSessionBridge.handle_turn()`
- `tier1/engainos/core/continuity_context_builder.py` — `ContinuityContextBuilder.build()`
- `tier1/engainos/core/session_ledger.py` — `Turn` dataclass, `SessionLedger.append()`
- `tier1/engainos/tests/test_shared_session_continuity_proof.py`,
  `tier1/engainos/core/continuity_cursor_tracker.py` (checked for any
  existing `direction` branching or coordination sketch — none found;
  this is genuinely greenfield)

## The real data flow, as it exists today

```
POST /dispatch  (presence_authority_server.py:_handle_dispatch)
  required body fields: shared_session_id, origin_body, player_input,
                        provider_id, model_id, provider_session_id
  optional: agent_id, instance_id, launch_options, requested_lease, snapshot
       |
       v
SharedSessionBridge.handle_turn(session_id, origin_body, player_input,
                                 binding, snapshot=None)
  step 2: self._ledger.append(..., direction="request", actor="player",
                               payload=player_input, snapshot=snapshot)
          -- player_input becomes Turn.payload, VERBATIM. This append is
             the historical record of "what the player said" and the
             module docstring is explicit that nothing may modify it.
  step 4: context = prior Turns (direction "request"/"response" only)
  step 5: dispatch_input = ContinuityContextBuilder.build(
              context, player_input, last_seen_turn_id)
          result = self._dispatch(binding, context, dispatch_input)
       |
       v
ContinuityContextBuilder.build(context, player_input, last_seen_turn_id) -> str
  pure function. Returns player_input UNCHANGED if the target native
  session has already seen everything in context; otherwise wraps it in
  a "here is what you're missing" recap block ending in
  "Now: {player_input}". player_input's own text is never altered either
  way -- only what surrounds it.
```

Two hard invariants the existing docstrings state explicitly and that
any addition must respect:
1. **Ledger step 2 (`payload=player_input`) is "historical fact" and may
   never be modified** — a player request is recorded even when nobody
   is ACTIVE to answer it. A coordination_report is not something the
   player said; folding it into `payload` would corrupt this record.
2. **`Turn.direction` is `"request" | "response"` only**, everywhere —
   `ContinuityContextBuilder.build()`'s own turn-labeling logic branches
   on exactly `if turn.direction == "request": ... else: ... "A different
   assistant replied"`. Confirmed via the two real tests that assert
   `preserved.direction == "request"` — nothing anywhere currently
   handles or expects a third direction value. Introducing one (e.g.
   `"event"`) would silently mis-label it as an assistant reply wherever
   this branch runs, unless every one of those call sites were also
   updated — a materially larger, riskier change than the alternative
   below.

## The existing precedent for exactly this kind of side-channel

`Turn.snapshot: Optional[dict] = None` and `handle_turn(..., snapshot:
Optional[dict] = None)` are already **exactly** this shape: a piece of
per-turn data that is NOT the player's words, carried alongside
`payload` as its own field rather than concatenated into it, optional,
and passed through the `/dispatch` body as a distinct top-level key. This
is the load-bearing existing pattern to follow, not a new one to invent.

There is also a real, already-built precedent for keeping a coordination
report out of the dispatched text's "voice" specifically: the local
(non-continuity) `hermes_session_adapter.py` path already carries
`pending_coordination` into `_format_messages()` as its own labeled
block, separate from the player's message — and explicitly **refuses**
to combine with continuity dispatch today
(`COORDINATION_UNSUPPORTED_ON_CONTINUITY_DISPATCH`, seen in this
session's earlier trace of `hermes_session_adapter.py:2177`). Whatever
gets added to the continuity path is the thing that would eventually let
that refusal be lifted — but lifting it is a separate call-site change,
not part of this discovery note.

## Answer: the correct authoritative injection point

Three coordinated additions, mirroring the `snapshot` precedent exactly,
each additive (no existing field/signature removed or repurposed):

1. **`/dispatch` HTTP body** (`presence_authority_server.py:_handle_dispatch`):
   add an optional top-level key, e.g. `"coordination_report"` (dict or
   absent) — read via `body.get("coordination_report")`, never merged
   into `body["player_input"]`.

2. **`SharedSessionBridge.handle_turn()`**: add
   `coordination_report: Optional[dict] = None`, threaded exactly like
   `snapshot` is today:
   - Step 2: pass it into `self._ledger.append(...)` as its own new
     `Turn` field (e.g. `Turn.coordination_report`, sibling to
     `Turn.snapshot`) — attached to the request turn as metadata, never
     folded into `payload`. This keeps the "player request is historical
     fact, unmodified" invariant intact while still durably recording
     that a report accompanied this turn (this project's own "leave
     proof trail" convention).
   - Step 5: pass the same value into `ContinuityContextBuilder.build()`
     as a new explicit parameter — see next point.

3. **`ContinuityContextBuilder.build(context, player_input,
   last_seen_turn_id, coordination_report=None)`**: when present, prepend
   a clearly labeled block (structurally parallel to the existing
   "here is what you're missing" recap, textually distinct from it) —
   e.g. "EngAIn's Editor has a report for you: ..." — followed by
   `player_input` exactly as it is today (still just `"Now: {player_input}"`
   or the bare string). `player_input`'s own text is never touched either
   way — the requirement "without mixing it into player_input" is
   satisfied by construction, not by convention.

No new `Turn.direction` value, no change to `read_since()`/cursor
branching, no journal/frame-shape change (item 3's crash-consistency
design is untouched) — everything above is additive fields plus one new
optional function parameter at each of the three layers.

## Explicitly not done here (discovery only, per instruction)

- No code changed in EngAIn or any other repo.
- Did not decide whether/how to lift `hermes_session_adapter.py`'s
  existing `COORDINATION_UNSUPPORTED_ON_CONTINUITY_DISPATCH` refusal —
  that's a real call-site decision for whoever wires a caller to this,
  separate from where EngAIn itself should accept the input.
- Did not address the browser ChatGPT Dragon connection at all — this
  question was purely about EngAIn's own internal plumbing; the two
  remain unrelated until a separate decision connects them.
