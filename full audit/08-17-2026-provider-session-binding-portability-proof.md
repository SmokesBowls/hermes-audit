# Provider-Neutral Dispatch Boundary: ProviderSessionBinding + Portability Proof

Written 2026-08-16/17, continuing directly from the same day's Godot-orphan
fix. This is the architectural correction the operator specified: the
original dispatch design conflated two identifiers that must never be
treated as interchangeable, and this closes that gap with a real,
live, cross-provider proof — not just two configurable provider names.

## The conflation, and the fix

`PresenceRecord.session_id` was previously used both as EngAIn's own
Ledger/Presence key *and* handed directly to a provider CLI as its native
`--resume` target. That's two different identifier spaces, owned by two
different parties, silently collapsed into one field. It never surfaced as
a bug in the single-provider-per-session proofs from earlier the same
day, because nothing ever switched providers mid-session — the conflation
was there, just invisible.

`tier1/engainos/core/provider_session_binding.py` defines
`ProviderSessionBinding`, exactly as specified:

```
provider_id / model_id / provider_session_id / agent_id / instance_id /
shared_session_id / launch_options
```

`ProviderSessionBinding.from_presence_record()` is the only place a
binding gets constructed — it combines a resolved `PresenceRecord`'s own
`agent_id`/`instance_id`/`session_id` (which *is* `shared_session_id`,
unchanged in meaning) with provider-specific detail now carried in
`PresenceRecord.endpoint`, re-encoded via `encode_endpoint()`. It raises,
rather than guessing, if the endpoint is missing or incomplete — an
adapter must never be handed something to guess a provider/model/session
from.

## The adapter changed, not the bridge's orchestration

`shared_session_bridge.py`'s `handle_turn()` gained exactly one new line
at step 5: construct the binding from the just-resolved record, then
dispatch with the binding instead of the raw record. Steps 1–4 and 6–8
are untouched — this was a boundary correction, not a redesign.

Both provider adapters now take `ProviderSessionBinding` instead of
`PresenceRecord`. `--resume` now uses `binding.provider_session_id`
(vendor-native), never `binding.shared_session_id` (EngAIn's own) — the
exact line that was previously wrong. Hermes's own internal `--provider`
flag (e.g. `openai-codex`, distinct from EngAIn's `provider_id="hermes"`)
moved into `launch_options`, since it's Hermes-specific plumbing, not a
universal binding concept.

## Regression and new coverage

6 new tests (`test_provider_session_binding.py`): round-trip through a
real `PresenceRecord`, the two identifiers never being the same field,
provider switching preserving `shared_session_id` while changing
`provider_id`/`provider_session_id`, missing/incomplete endpoint raising
by name rather than guessing, and `launch_options` defaulting to empty.
Full suite: 189/189 (183 prior + 6 new), no regressions. The five existing
tests in `test_shared_session_continuity_proof.py` that register presence
without an endpoint needed a shared `TEST_ENDPOINT` fixture added — they
were exercising orchestration logic unrelated to provider dispatch and
had never needed a real binding before this change made one mandatory at
dispatch time.

The two existing single-provider live-proof tools
(`live_hermes_continuity_proof.py`, `live_claude_code_continuity_proof.py`)
had the exact conflation this whole change fixes — each minted a vendor
session and used it as both the shared and native session id. Both
corrected to mint a separate `shared_session_id` via `uuid.uuid4()`,
deliberately never equal to the vendor-native id.

## The real proof — all 8 steps, live, first run, no retries

`live_cross_provider_portability_proof.py`. Real Hermes, real Claude Code,
real Ledger, real Presence, one process, no mocks. Full transcript
(`runtime/logs/CROSS_PROVIDER_PORTABILITY_PROOF_V1.report.json`):

```
shared_session_id:            shared-563353f363614e2d8a24e0edd4388129
hermes_provider_session_id_1: 20260816_234740_dbd92e
claude_provider_session_id:   c7d12651-fe05-407f-ab5c-84c87b4a864c

turn 0  dragon_2d  request   player        "Remember the phrase: obsidian ferry..."
turn 1  dragon_2d  response  hermes        "noted."
turn 2  dragon_3d  request   player        <recap of turns 0-1, supplied by the proof
                                             script from the Ledger, asking Claude Code
                                             to recall the phrase from a provider it has
                                             no memory of>
turn 3  dragon_3d  response  claude_code   "obsidian ferry"
turn 4  dragon_2d  request   player        <recap of turn 3, supplied from the Ledger,
                                             asking Hermes — resumed on its ORIGINAL,
                                             unchanged provider_session_id — to recall
                                             the phrase Claude Code reported>
turn 5  dragon_2d  response  hermes        "obsidian ferry"
```

The decisive step is turn 4/5: Hermes was re-registered against the exact
same `provider_session_id` from turn 1 — the identical native transcript,
which only ever contained "remember obsidian ferry" / "noted." and was
never told anything about a Claude Code exchange. It answered correctly
about the Claude turn only because turn 4's prompt — built by reading the
Ledger, not by asking either vendor for its memory — supplied it directly.
If either provider adapter secretly injected Ledger context into every
prompt on its own (which neither does — see both adapters' docstrings),
this test would not have distinguished that from genuine portability.
Because they don't, and the recap was assembled explicitly by the proof
script from `ledger.read_since()`/`read_last()` before dispatch, this is a
real demonstration that EngAIn's Ledger — not either vendor's session
state — is what makes continuity portable across a provider switch.

One Ledger, six turns, three separate registration events (two Hermes, one
Claude Code — the second Hermes registration reusing the first's
`provider_session_id` on purpose), one `shared_session_id` throughout.

## Unchanged, deliberately

`agent_gateway.py` policy — not touched, not consulted from the bridge, as
before. `SessionClaimRegistry`/presence authority server from the earlier
same-day work — untouched; this proof ran without a shared authority
process, single-process, matching how the original two single-provider
proofs also ran (the presence authority's cross-process mutex is a
separate concern from provider portability and wasn't exercised here).
`PresenceRegistry`'s own data model — unchanged; `session_id` already
meant `shared_session_id` correctly, the bug was entirely in how the
adapters used it, not in what Presence stored.
