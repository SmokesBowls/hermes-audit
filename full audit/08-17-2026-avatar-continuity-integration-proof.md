# Avatar Continuity Integration: dragon2d/dragon3d Through EngAIn's Sole Authority

Written 2026-08-17, same day as the identity-boundary correction this
builds on directly. This is the integration the identity-boundary fix was
for: the real `dragon2d`/`dragon3d` avatar mailbox workers now share
EngAIn's own continuity — without either avatar repository importing or
vendoring `SharedSessionBridge`, `ContinuityCursorTracker`, or
`ContinuityContextBuilder`. EngAIn is the sole continuity authority,
reached over HTTP; both avatar repos gained only a small stateless client.

## What "sole authority" means concretely

`tier1/engainos/server/presence_authority_server.py` — the same process
already serving `/presence/*` and `/claim`/`/release` — gained one new
endpoint, `POST /dispatch`. It now also owns a `SessionLedger` and a
`ContinuityCursorTracker` (previously only owned by proof scripts and,
implicitly, by whatever process constructed a `SharedSessionBridge`
directly). A `/dispatch` call:

1. Requires the caller's own `ProviderSessionBinding` fields
   (`provider_id`, `model_id`, `provider_session_id`, optional
   `agent_id`/`instance_id`/`launch_options`) alongside the bare
   `shared_session_id`/`origin_body`/`player_input` — "the worker submits
   the request plus its ProviderSessionBinding to EngAIn," literally.
2. REGISTERs that binding into the server's own `PresenceRegistry`
   (most-recent-REGISTER-for-a-session_id-wins, `PresenceRegistry`'s own
   already-documented rule) — this is how "the active provider" is
   decided, with no second, competing notion of "active" invented here.
3. Picks the matching dispatcher (`dispatch_via_hermes_cli` /
   `dispatch_via_claude_code_cli`) and calls the real, unmodified
   `SharedSessionBridge.handle_turn()` — the exact same class every
   in-repo proof already used, now reachable from a different process.
4. Returns `handle_turn()`'s own shape unmodified: 200 on success, 404
   `PROVIDER_NOT_REGISTERED`, 409 `RESPONSE_ACTOR_MISMATCH`, 502
   `PROVIDER_DISPATCH_FAILED`.

`engain_continuity_client.py` — vendored, byte-identical, into both
`engain_avatar` and `godot_engain_3d_avatar` (same discipline as
`presence_authority_client.py`: a stateless HTTP client, never the
stateful classes themselves). One function, `dispatch(...)`, one exception
type, `EngAinContinuityError`, carrying the server's own `error` code.

## The avatar worker side — additive, opt-in, nothing removed

`hermes_session_adapter.py` in both repos gained:

- `ENGAIN_CONTINUITY_DISPATCH` — unset (default) leaves
  `_process_claimed_request` byte-for-byte what it always was:
  `director_bridge.process_player_input()` straight to this worker's own
  frozen native Hermes session, `_sanitize_response()`'s existing
  single-use provider-receipt binding unchanged. Set to `"1"`, dispatch
  goes through `engain_continuity_client.dispatch()` instead.
- `_engain_continuity_binding_fields()` — defaults to this worker's own
  frozen identity (`provider_id="hermes"`, `model_id=self.client.model`,
  `provider_session_id=self.client.session_id`,
  `launch_options={"provider": self.client.provider}`), every field
  independently overridable by an `ENGAIN_CONTINUITY_*` env var — this is
  how the proof drives one worker as "answering via Claude Code" without
  the adapter ever hard-coding Claude Code's existence.
- `_engain_continuity_response()` — a new response-builder, not a
  modification of `_sanitize_response()`. `_sanitize_response()` sources
  `narrative_response` from `self.client.take_provider_receipt()` — a
  receipt proving *this exact process's own Hermes CLI client* made the
  call — which is simply the wrong invariant to check when the true
  answering actor may be a different provider entirely. The new path
  sources the narrative from EngAIn's own answer and records the *true*
  actor/turn_id honestly in `director_analysis`. `provider_session_ref`
  (via the existing `_provenance_fields`) still reports this worker's own
  frozen identity, unchanged — the response.json schema itself is frozen
  and Godot's parser depends on that shape, so `director_analysis` is
  where truth lives instead, not a schema change. **Named limitation**:
  `provider_session_ref` in a response.json can therefore read as Hermes
  even when Claude Code truly answered; anything reading `provider`/
  `model`/`session_id` from that field alone, rather than
  `director_analysis`, would be misled. No consumer does that today.
- `_register_with_presence_authority()`, `_acquire_dispatch_claim()`,
  `_release_dispatch_claim()` — **untouched**. That claim mechanism
  serializes concurrent access to this worker's own frozen native Hermes
  session between dragon2d and dragon3d, keyed by that frozen session_id —
  a different concern than /dispatch's own routing, still runs
  unconditionally in both dispatch modes, and still protects what it
  always protected.

## A gap this pass does not close, named rather than hidden

`/dispatch`'s own internal dispatch call has no mutex of its own. Today,
protection against two *concurrent* `/dispatch` calls racing the same
native provider session relies entirely on the pre-existing worker-level
claim (which only exists for the frozen-Hermes default binding, keyed on
`self.client.session_id`). A caller that submits an explicitly-overridden
binding — as the proof does for its Claude Code leg — has no equivalent
guard. This proof's own steps are strictly sequential and never exercise
that race; it is not proven safe here, and is not claimed to be.

## Cursor/Ledger durability — still process-lifetime only, and what that turned out to mean

Both live inside `presence_authority_server.py`'s own process memory, same
as `PresenceRegistry` already did. A restart empties both. The prior
receipt asked for this to be handled "conservatively" before restart
durability is claimed — this pass still does not persist or reconstruct
from receipts; it stays honestly in-memory-only, and the decisive proof
below tests that boundary directly, including one discovery not written
down before this run:

**A cursor-driven recap, once dispatched, becomes a genuine, permanent
part of the receiving native session's own transcript** — not something
EngAIn continues to "own" or that a later EngAIn restart can retract. The
first two attempts at the proof's restart leg asked the *same* native
Hermes session (the one that had *already* received, pre-restart, a recap
containing the Claude Code exchange) about that exchange again, post-
restart, and it answered correctly both times — not via any leak, but
because that recap had already become the same kind of native fact as
anything else ever said to that session via `--resume`. Confirmed directly
and cheaply: a brand-new, never-used Hermes session asked cold said "No"
to knowing an invented test word; the frozen session, resumed directly
outside this proof's own code, correctly attributed that same word to "a
different assistant earlier in this conversation" — its own real,
unprompted memory, not a coincidence. The corrected proof (below) instead
asks a **freshly-minted, never-recapped** native Hermes session about the
Claude exchange post-restart, which correctly does not know it — isolating
the actual claim ("EngAIn's Ledger, once lost, cannot supply what only it
held") from a session that had separately, legitimately learned it before
the loss.

## Test suites, offline, all green

- EngAIn (`tier1/engainos/tests/`): 215/215 — 208 prior + 7 new
  (`test_presence_authority_dispatch.py`, real HTTP against a real
  ephemeral-port server with fake dispatchers, covering missing-field/
  unknown-provider 400s, the basic 200 shape, same-native-session-no-recap,
  switch-then-switch-back recaps exactly the missed turn, dispatch-failure
  502, response-actor-mismatch 409).
- `engain_avatar` (`tests/`): 86/86 — 77 prior + 9 new
  (`test_engain_continuity_dispatch.py`: the client against a small local
  fake `/dispatch`, binding-field defaults/overrides, the
  `ENGAIN_CONTINUITY_SHARED_SESSION_ID`-required guard, the response-shape
  builder, and both a default-path regression pin and an enabled-path
  end-to-end test through `_process_claimed_request`/`process_once()`).
- `godot_engain_3d_avatar` (`tests/`): 260/263 — 251 prior + 9 new
  (identical shape to `engain_avatar`'s), 3 pre-existing unrelated `RED`
  failures (`test_stage8_ticket3b_worker_ownership_red.py`), confirmed
  unrelated to this change by the same failure signature the last full
  audit already recorded.

## The decisive live proof

`tier1/engainos/tools/live_avatar_continuity_integration_proof.py`. Real,
unmodified `hermes_session_adapter.py` in both repos, run as real
persistent subprocesses against the real production file mailboxes at
`/mnt/data-drive/engain-runtime-mailboxes/{dragon2d,dragon3d}/`, driven
exactly the way Godot itself would (`--publish-request`, poll for
`response.json`, `--claim-response`) — never a direct Python call into
either adapter. Neither avatar worker constructs recap text anywhere in
this run; every `player_input` submitted is a plain instruction.

Sequence and real results, this run's shared_session_id
`shared-8f6f00ed38e44caeb41b4c27f62c7c2a`:

```
1. dragon2d, default binding (hermes, native session 20260731_065008_63a62d):
   "Remember the phrase: opal thicket. Reply with exactly: noted."
   -> "noted."                              actor=hermes    turn_id=1

2. dragon3d, explicit Claude Code binding (freshly minted session
   f670227d-f628-4cdf-833b-24c29c885bfb):
   "...extract the phrase... also invent one unrelated made-up word..."
   -> "opal thicket|flembrix"               actor=claude_code turn_id=3
   (cursor-driven recap supplied "opal thicket" — claude_code's own native
   session never saw it any other way)

3. dragon2d, default binding again (same frozen native session):
   "...extract ONLY the exact phrase from what the other assistant replied..."
   -> "opal thicket"                        actor=hermes    turn_id=5
   (cursor-driven recap of turn 2/3 supplied this — that native session's
   own transcript never independently had it)

--- restart presence_authority_server.py: fresh, empty Ledger + cursor ---

4. dragon2d, default binding, SAME frozen native session as steps 1/3:
   "Earlier you said 'noted.'... output ONLY that exact phrase..."
   -> "opal thicket"                        actor=hermes    turn_id=1
   (dispatch_input was bare — empty Ledger, nothing to recap; this answer
   is provably native Hermes memory, not EngAIn's Ledger)

5. dragon2d, binding overridden to a FRESH, never-recapped native Hermes
   session (20260817_065745_818f32), same shared_session_id:
   "A different assistant invented an arbitrary made-up word... what was it?"
   -> "I don't know."                       actor=hermes    turn_id=3
   (correctly cannot recover "flembrix" — neither this session's own
   native memory nor the now-empty Ledger has it)
```

All five went through real request/response mailbox files at the real
production paths (consumed via the real `--claim-response` protocol, same
as Godot would — not preserved as separate artifacts the way the
brand-new file-mailbox translation layer's own proof preserved its files,
since this protocol is pre-existing and already documented). The full
structured result — every `request_id`, every `director_analysis`, every
`provider_session_ref`, every `perception_result` — is preserved at
`runtime/logs/AVATAR_CONTINUITY_INTEGRATION_PROOF_V1.report.json` in the
EngAIn checkout.

Confirmed directly from that receipt, not merely asserted by the proof
script: `director_analysis` for step 2 reads
`"EngAIn shared continuity (actor='claude_code', turn_id=3)"` — the true
answering actor, honestly recorded, while `provider_session_ref` in that
same response.json still names Hermes's frozen identity (the named,
accepted schema limitation above, confirmed in practice, not just in
theory).

Five real Hermes CLI calls, two real Claude Code CLI calls (one bootstrap,
one dispatch) this run.

## Housekeeping note, unrelated to this change but caught during it

A `hermes_session_adapter.py` worker process for `dragon2d` was found
still running (PID alive, listener lease actively renewing) from earlier
work in this same multi-day session, orphaned rather than cleanly shut
down. Confirmed it was mine (exact invocation match, parent a bare shell,
no Godot process alongside it, nothing else consuming it) before stopping
it with `SIGINT` — the same graceful path `hermes_session_adapter.py`'s
own `main()` already handles, confirmed clean (PID lock released, process
exited) — so the new proof could acquire its `PidFileLock`.

## Unchanged, deliberately

`agent_gateway.py`, `SessionClaimRegistry`'s own logic, `PresenceRegistry`'s
data model, `ProviderSessionBinding` itself, `ContinuityCursorTracker`,
`ContinuityContextBuilder`, `SharedSessionBridge` — none touched. This was
entirely about giving two existing, separate-repo workers a way to reach
the one place those already live, without copying them.

## Still open, not attempted here

- No mutex around concurrent `/dispatch` calls carrying an overridden
  (non-default) binding — named above, not solved.
- No Ledger/cursor persistence or receipt-based reconstruction across a
  real restart — this pass proves the honest, safe-direction consequence
  of not having it (lost cross-provider context, never a wrong answer),
  not a fix for the loss itself.
- Real Godot was not launched for this proof (unlike the earlier
  SESSION_OCCUPIED live proof) — both workers ran as real, persistent,
  file-mailbox-driven subprocesses, without the Godot engine layer.
