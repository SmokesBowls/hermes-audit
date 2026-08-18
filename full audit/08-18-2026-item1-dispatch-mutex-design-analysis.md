# Item 1 Design Analysis — Concurrent-`/dispatch` Mutex for the Native Provider Session

Written 2026-08-18. This is a **design note only** — no runtime code is
touched by this document. It re-derives continuation-TODO item 1 from the
actual code (`presence_authority_server.py`, `shared_session_bridge.py`,
`session_ledger.py`, `continuity_cursor_tracker.py`, `presence_registry.py`,
`session_claim_registry.py`, and both avatar repos' `hermes_session_adapter.py`)
rather than from the original TODO note's prose, per explicit instruction
not to recommend a primitive until a trace proves what it has to protect.
Do not implement any of this until it has been reviewed.

## 0. What the re-derivation overturned

The original TODO note framed this as: "protection exists for the default
frozen-Hermes binding ... a caller submitting an explicit override has no
equivalent guard." Tracing the actual code shows that framing understates
the gap. `_handle_dispatch` in `presence_authority_server.py` calls
`claims.claim()`/`claims.release()` **nowhere** — confirmed by grep; those
calls exist only inside the standalone `/claim`/`/release` HTTP handlers,
which only `hermes_session_adapter.py`'s own client-side
`_acquire_dispatch_claim()` wrapper calls. `/dispatch` itself has **no**
serialization of its own, for **any** caller, override or not.

`dragon_2d` and `dragon_3d` are only protected against *each other*
because both repos hardcode the byte-identical frozen string
`PERSISTED_HERMES_B_SESSION_ID = "20260731_065008_63a62d"` (confirmed via
`grep` in both `hermes_session_adapter.py` files) as the key their local
claim wrapper happens to use — an accident of both bodies sharing one
frozen companion identity, not a property of what they're dispatching to.
Any other caller reaching `/dispatch` directly — the integration proof's
Claude-Code leg, a `tool` origin_body, a future third avatar body, a bare
`curl` — gets zero exclusion today, under any binding.

## 1. The exact concurrent operation

Two simultaneous `POST /dispatch` calls, both handled inline in a
`ThreadingHTTPServer` request thread (one OS process, one GIL, real OS
threads — no async, no queueing), both eventually reaching
`SharedSessionBridge.handle_turn()`'s 8 steps:

```
Thread A (/dispatch)                    Thread B (/dispatch)
──────────────────────                  ──────────────────────
presence.register(shared_session_id)    presence.register(shared_session_id)
handle_turn():
  step2 ledger.append(request)  ←────── step2 ledger.append(request)   [race #2, below]
  step3 presence.resolve()               step3 presence.resolve()
  step4 read Ledger context              step4 read Ledger context
  step5 binding = from_presence_record() step5 binding = from_presence_record()  [same target]
        cursor.last_seen_turn_id(P,S)          cursor.last_seen_turn_id(P,S)     [both read stale]
        dispatch(binding, ctx, input)  ←──────  dispatch(binding, ctx, input)    [BOTH hit the provider CLI on session S at once]
  step6 presence.resolve() (re-check)    step6 presence.resolve()
  step7 ledger.append(response) ←──────── step7 ledger.append(response)  [race #2, below]
  step8 cursor.advance(P,S,turn_id)       step8 cursor.advance(P,S,turn_id)  [monotonic-max wins, order not preserved]
```

Nothing in this path serializes today.

## 2. The protected resource — two distinct ones, not one

**Resource A — the native provider transcript**, identified by
`(provider_id, provider_session_id)`. This is `session_claim_registry.py`'s
own stated reason for existing: concurrent `hermes chat --resume
<session_id>` (or Claude Code's equivalent) "could interleave or corrupt
one live transcript." External to EngAIn, unrecoverable after the fact —
prevention is the only real defense. This is what item 1 is actually
about, and what this note designs a fix for.

**Resource B — `SessionLedger`'s own turn ordering**, keyed on EngAIn's
`shared_session_id`, not `(provider_id, provider_session_id)`. A real,
independently-discovered bug, not hypothetical:

```python
turns = self._turns.setdefault(session_id, [])
turn = Turn(turn_id=len(turns), ...)   # read
turns.append(turn)                      # write — not atomic with the read
```

Two threads racing `append()` for the same `shared_session_id` can read
the same `len(turns)`, mint two turns claiming the same `turn_id`, and
leave the Ledger's stored order out of sync with the `turn_id` field
everything else trusts. This can happen even between two dispatches
targeting **different** native provider sessions, as long as they share a
`shared_session_id` — so a `(provider_id, provider_session_id)` mutex does
**not** protect it. Recorded as a separate, new TODO item — see the
companion document, not fixed here.

## 3. The lock key — proved from the three comparison cases

```
dragon_2d -> provider A / session 123
dragon_3d -> provider A / session 123        SAME native transcript. Must serialize.

dragon_2d -> provider A / session 123
tool      -> provider A / session 456        Different sessions, same provider.
                                              provider_id alone is too coarse — would
                                              force false contention between unrelated
                                              transcripts.

dragon_2d -> provider A / session 123
dragon_3d -> provider B / session 123        session_id "123" collides as a bare string
                                              but names two unrelated native memory
                                              containers under different providers.
                                              session_id alone is too coarse — would
                                              force a false conflict between unrelated
                                              resources that happen to share a number.
```

Only the composite `(provider_id, provider_session_id)` gets all three
right. This is the same identity `ContinuityCursorTracker` already keys
on, for a different reason (recap correctness, not mutual exclusion) —
two independent parts of the system converging on the same composite key
from different angles is a strong signal it's the correct identity, not
an arbitrary choice.

## 4. Critical-section lifetime

Locking only around `self._dispatch(...)` (step 5's actual provider call)
is insufficient. In the trace above, both threads read
`cursor.last_seen_turn_id(P, S)` and build their recap from it **before**
either has dispatched or advanced anything. A lock scoped to only the
provider call would still let thread B block, wake holding an already-
stale recap, and send it the instant the lock opens — the exact "second
request builds context from stale cursor state" failure being guarded
against. The claim must be held from before the Ledger-context read and
the cursor read (steps 4–5) through the cursor advance (step 8) — in
practice, the entire `handle_turn()` call, acquired immediately at the
top of `_handle_dispatch` and released in a `finally` after `handle_turn()`
returns or raises.

## 5. Registry choice: extend `SessionClaimRegistry`

Its own docstring already states, verbatim, what item 1 needs: *"who,
right now, holds the right to actually send the next message to this
session's provider — a short-lived mutex held only for the duration of
one dispatch call."* Not a coincidental resemblance — the same problem.

The only mismatch is key shape (`str` today; needs
`(provider_id, provider_session_id)`). The implementation
(`Dict[key, SessionClaim]` behind one `threading.Lock`) only needs
hashability — this is a type generalization, not a semantic change.

**The public `/claim`/`/release` HTTP endpoints and their JSON contract
are untouched by this design** — they stay exactly `session_id: str`,
exactly as today's client-side worker-level claim already uses them.
`_handle_dispatch`'s new behavior is a direct, in-process Python call into
the same `claims` singleton with a composite key — never a new or changed
HTTP surface.

A separate `DispatchClaimRegistry` would duplicate the same lock+dict+
lease-expiry code for no semantic daylight — `SessionClaimRegistry` was
already deliberately split off from `PresenceRegistry` for exactly the
readiness/ownership-conflation reason that would make a forced reuse
wrong; extending it doesn't re-introduce that, because nothing about
what the class *means* changes, only what a caller's key looks like.

Known, accepted redundancy this creates: once `_handle_dispatch` claims
`(provider_id, provider_session_id)` server-side, the default
(non-override) path becomes double-locked — the existing client-side
claim on the frozen string, plus the new server-side claim on the tuple.
Both real, harmless, redundant rather than conflicting. Retiring the
client-side claim is production-cutover territory (item 3), not this.

## 6. Failure semantics

- **Contending caller**: reject immediately — new `DISPATCH_BUSY`
  (409), shaped like the existing `ClaimRejected`/`SESSION_OCCUPIED`.
  Not queued or blocked. Matches the only existing precedent in this
  codebase (`SESSION_OCCUPIED`), which avatar workers already handle as
  a retryable, non-fatal, user-safe error. Queueing inside an HTTP
  handler thread is a materially larger commitment (queue depth,
  thread-pool exhaustion under contention, its own timeout policy) with
  zero precedent here — not proposed.
- **Crash/hang recovery**: the existing `lease_seconds`/
  `claim_expires_at` self-expiry, unchanged — no new mechanism invented.
  See §8 for how the TTL itself is derived.
- **Stale claim survival**: bounded by that same lease.
- **Fairness**: none, today or after — `claim()` is immediate
  accept/reject with no queue. Pre-existing limitation, not introduced
  or fixed here; stated so it isn't silently inherited as if it were new.
- **Self-reacquisition**: a real trap, not hypothetical. `claim()`'s
  reentrancy rule — same `instance_id` re-claiming its own unexpired
  claim succeeds as a refresh, not a rejection — means two genuinely
  concurrent `/dispatch` calls that happen to derive the *same*
  `instance_id` (e.g. today's fallback `f"{provider_id}-dispatch"` when
  the caller supplies none) would silently "refresh" each other's claim
  instead of correctly contending, defeating the mutex entirely. The new
  claim must use an `instance_id` freshly minted per `/dispatch` call
  (e.g. a UUID generated inside `_handle_dispatch` itself), never the
  caller-supplied `agent_id`/`instance_id` body field — so two overlapping
  requests, even from the same declared caller, correctly contend rather
  than co-owning the lock.

## 7. Single-authority-process invariant

`presence_authority_server.py`'s own module docstring states the reason
it exists: "exactly one `PresenceRegistry` and exactly one
`SessionClaimRegistry` in the whole system." It is a `ThreadingHTTPServer`
— one process, one GIL, threads only. The Phase 1 launcher work
(`SupervisedPresenceAuthority` in `runtime_composition.py`) confirmed this
further: exactly one authority process is spawned per composed runtime
generation; nothing in this codebase anticipates multiple authority
processes. An in-process `threading.Lock`-backed registry is therefore
correct **as long as that invariant holds** — which is assumed, not
enforced, anywhere today. If it is ever violated (a second authority
process on another port, horizontal scaling for availability), an
in-process mutex becomes false safety: each process would own a
different lock over a different dict, and two processes could both
"successfully" claim the same native session. Flagging this as a
documented precondition of the whole design, not a silent assumption.

---

## 8. Closing the two remaining holes

### 8a. Where `(provider_id, provider_session_id)` comes from, before `handle_turn()`

**No refactor of `handle_turn()`'s internal binding resolution is
needed.** The request body already carries `provider_id` and
`provider_session_id` as required, validated fields — checked at the very
top of `_handle_dispatch`:

```python
required = (
    "shared_session_id", "origin_body", "player_input",
    "provider_id", "model_id", "provider_session_id",
)
missing = [key for key in required if key not in body]
```

These two fields are available as plain dict lookups — `body["provider_id"]`,
`body["provider_session_id"]` — with no side effects, before
`presence.register()` is called, before `SharedSessionBridge` is even
constructed. They are, in fact, the *same* values already used moments
later to build the `endpoint` string passed into that `presence.register()`
call (`ProviderSessionBinding.encode_endpoint(provider_id=provider_id, ...,
provider_session_id=body["provider_session_id"], ...)`) — so the claim key
and what gets registered are, by construction, identical within one
`_handle_dispatch` invocation. `handle_turn()`'s own step-5 re-derivation
(`binding = ProviderSessionBinding.from_presence_record(record)`) reads
back whatever Presence currently reports for `shared_session_id` — under
normal operation that is exactly what this same call just registered,
since holding the new claim prevents any *other* dispatch to the *same*
native pair from running concurrently.

One boundary worth naming, not fixing here: the claim is keyed on
`(provider_id, provider_session_id)`, not `shared_session_id`. It does
**not** prevent a *different* concurrent `/dispatch` call for the *same*
`shared_session_id` but a *different* provider from overwriting Presence's
registration for that `shared_session_id` between this call's `register()`
and `handle_turn()`'s step-3 `resolve()`. That is `presence.register()`'s
existing, already-documented "most-recent-REGISTER-wins" semantic — a
pre-existing characteristic of `PresenceRegistry`, unrelated to and not
introduced by this mutex, out of scope for item 1.

**Recommended acquisition point**: at the very top of `_handle_dispatch`,
immediately after the `required`-fields check and the `provider_id`→
dispatcher lookup (so a request naming an unknown provider still gets its
existing 400 without ever touching the claim registry), and *before*
`presence.register()` is called. Released in a `finally` wrapping
everything from that point through `bridge.handle_turn()` returning or
raising.

### 8b. The claim-lifetime invariant

**Invariant**: the claim's TTL must exceed the maximum possible duration
of the entire protected critical section — from acquisition (top of
`_handle_dispatch`) through release (`finally`, after `handle_turn()`
returns or raises) — so that a legitimate, still-running dispatch can
never have its claim expire out from under it while a second caller
acquires the same key.

**What bounds that duration, traced through the actual code**:

- `presence.register()`, `handle_turn()` steps 2–4 and 6–8 (Ledger
  append ×2, Presence resolve ×2, Ledger read, cursor read/advance,
  `ContinuityContextBuilder.build()`) are all pure in-memory Python
  operations — no I/O, no subprocess. Bounded in practice to low
  single-digit milliseconds even under a handful of concurrent threads
  contending for the GIL. Not literally provably instantaneous, so the
  margin below treats this generously rather than as zero.
- Step 5, `self._dispatch(...)`, is the dominant and only unbounded-
  looking cost — the actual provider CLI subprocess call. It is **not**
  actually unbounded: both registered dispatchers enforce a hard
  `subprocess.run(..., timeout=timeout_s)` ceiling —
  `dispatch_via_hermes_cli`'s default `timeout_s=90.0`,
  `dispatch_via_claude_code_cli`'s default `timeout_s=120.0` (both
  confirmed by reading `hermes_provider_adapter.py` /
  `claude_code_provider_adapter.py` directly). A timeout firing raises
  `subprocess.TimeoutExpired`, translated to `HermesDispatchError`/
  `ClaudeCodeDispatchError`, which propagates up through `handle_turn()`
  uncaught and is caught by `_handle_dispatch`'s existing
  `_DISPATCH_FAILURE_EXCEPTIONS` handler (502) — the `finally` still
  releases the claim on this path.
- `subprocess.run`'s own post-timeout teardown (killing and reaping the
  child) adds a small, bounded amount beyond `timeout_s` itself — not
  zero, but not open-ended either.

**Concrete formula**:

```
claim_lease_seconds(provider_id) = dispatch_timeout_s(provider_id) + margin_s
```

where `dispatch_timeout_s` is looked up per `provider_id` (mirroring
`_PROVIDER_DISPATCHERS`'s own existing per-provider mapping — a small
sibling table, e.g. `_PROVIDER_DISPATCH_TIMEOUTS = {"hermes": 90.0,
"claude_code": 120.0}`, kept next to it in the same file so the two stay
visibly in sync; the simpler, less precise fallback is one fixed
`margin_s` added to `max()` of every registered timeout, applied
uniformly regardless of provider), and `margin_s` covers the in-memory
step overhead plus subprocess teardown — recommend `10.0`–`20.0`,
matching the existing worker-level claim's own precedent
(`MAX_HERMES_TIMEOUT_SECONDS + 20.0` in `hermes_session_adapter.py`).

**Renewal is not required** under this design, specifically *because* the
TTL is derived to exceed the critical section's proven maximum duration —
a well-behaved dispatch provably cannot outlive its own claim. Renewal
would only become necessary if a future change made the critical section
open-ended (e.g. a dispatcher call with no enforced timeout, or a new step
added that can block indefinitely) — naming this condition explicitly so
any future change that adds an unbounded step to the critical section is
forced to reconsider this invariant rather than silently invalidate it.

**Residual, named limitation**: this invariant assumes `subprocess.run`'s
own timeout enforcement is itself reliable. That is a reasonable but not
absolute assumption — pathological OS-level states (e.g. a grandchild
process holding an inherited pipe open in a way that delays
`Popen.communicate()`'s internal wait) are a known-hard general problem
in UNIX process management, not fully closed by any subprocess library
in every edge case. Not treated as solved here; a defensive additional
ceiling (a hard cap on `lease_seconds` regardless of provider, and/or a
periodic sweep) could be considered later if this residual risk proves
material in practice. Not proposed as part of this design.

---

## Recommendation (for review, not yet implemented)

Extend `SessionClaimRegistry` to accept a `(provider_id,
provider_session_id)` key for `_handle_dispatch`'s own internal,
direct-object use (public `/claim`/`/release` HTTP contract untouched).
Acquire at the top of `_handle_dispatch`, before `presence.register()`,
using `body["provider_id"]`/`body["provider_session_id"]` directly — no
`handle_turn()` refactor needed. Release in a `finally` around the whole
call. TTL per provider = that provider's own enforced dispatch timeout
plus a fixed margin (10–20s), no renewal needed given that bound. Reject
a contending caller immediately with a new `DISPATCH_BUSY` (409). Use a
freshly-minted, per-request `instance_id` for the claim, never
caller-supplied. Document the single-authority-process precondition
explicitly in code, since nothing enforces it today.

`SessionLedger.append()`'s `turn_id` race is a separate, real bug,
recorded as a new continuation-TODO item in the companion document —
not part of this design, not fixed by it.
