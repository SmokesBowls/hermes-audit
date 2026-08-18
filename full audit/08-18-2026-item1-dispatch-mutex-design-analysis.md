# Item 1 Design Analysis — Concurrent-`/dispatch` Mutex for the Native Provider Session

Written 2026-08-18. This is a **design note only** — no runtime code is
touched by this document. It re-derives continuation-TODO item 1 from the
actual code (`presence_authority_server.py`, `shared_session_bridge.py`,
`session_ledger.py`, `continuity_cursor_tracker.py`, `presence_registry.py`,
`session_claim_registry.py`, and both avatar repos' `hermes_session_adapter.py`)
rather than from the original TODO note's prose, per explicit instruction
not to recommend a primitive until a trace proves what it has to protect.
Do not implement any of this until it has been reviewed.

> **Revision 1 (same day)**: §8a's original conclusion — "no refactor of
> `handle_turn()`'s internal binding resolution is needed" — is **wrong**.
> A second reviewer traced an interleaving where that conclusion fails to
> hold: two dispatches acquiring two different, correctly-non-contending
> mutex keys can still end up both operating on the *same* native
> transcript, because `handle_turn()` re-derives its actual dispatch
> binding from mutable, shared `PresenceRegistry` state rather than from
> the immutable request that was validated and claimed against. §8a below
> is left in place, unedited, so the record is honest about what was
> wrong and why — **do not implement §8a as originally written**. The
> correction is §9, appended after the original recommendation; §9's
> conclusion supersedes §8a and the final Recommendation.

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

> **This classification is wrong — see §9.** It is not a pre-existing,
> out-of-scope Presence characteristic once a provider-session mutex
> exists: that same overwrite is what lets the *other* caller's dispatch
> silently steer *this* caller into invoking a native session different
> from the one its own claim protects, defeating the mutex's actual
> guarantee. §9 works the interleaving in full.

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

> **Superseded by §9 below — do not implement the above as written.**
> §9 replaces "no `handle_turn()` refactor needed" with an explicit,
> required signature change, and folds that into the final recommendation
> at the end of §9.

---

## 9. Revision — the binding must be a frozen input, not a re-derived read

### 9.1 The interleaving that breaks §8a

§8a's claim rested on: *"holding the new claim prevents any other dispatch
to the same native pair from running concurrently."* That's true of the
**claim registry** — but §8a implicitly assumed it was also true of
**Presence**, which it isn't. The claim is keyed on
`(provider_id, provider_session_id)`; `PresenceRegistry` is keyed on
`shared_session_id`. Two dispatches naming *different* native pairs but
the *same* `shared_session_id` acquire two different, non-contending
claims — and then both freely read and write the *same* Presence slot.

```
request A: shared S -> provider A / session 123
request B: shared S -> provider B / session 456

T1  A: claims.claim(key=(A,123))              -> success (uncontended)
T2  B: claims.claim(key=(B,456))              -> success (uncontended, different key)
T3  A: presence.register(session_id=S, endpoint=encode(A,123,...))
        presence._by_session[S] now = (A,123)
T4  B: presence.register(session_id=S, endpoint=encode(B,456,...))
        presence._by_session[S] now = (B,456)   -- overwrites A, "most-recent-wins"
T5  A: bridge.handle_turn(session_id=S, ...)
        step3: record = presence.resolve(S)      -> returns (B,456), NOT what A registered
        step5: binding = ProviderSessionBinding.from_presence_record(record)
               binding = (B,456)
        A calls self._dispatch(binding=(B,456), ...)   -- A invokes the provider
        using B's target, while A's own claim is on key (A,123)
T6  B: bridge.handle_turn(session_id=S, ...)
        step3/step5: resolve(S) -> (B,456) (nothing overwrote it again) -> binding=(B,456)
        B calls self._dispatch(binding=(B,456), ...)   -- B invokes the provider
        using its own, correctly-claimed target
```

At T5–T6, **A and B are both concurrently invoking the native transcript
`(B,456)`** — A while holding a claim on the wrong key `(A,123)`, which
protects nothing relevant; B while holding the *correct* claim on
`(B,456)`, which A's presence-sourced binding silently bypassed entirely.
This is exactly the failure item 1 exists to prevent, reproduced *with*
the mutex from §§1–8 in place. Verified against
`ProviderSessionBinding.from_presence_record()` directly — it performs no
cross-check against who registered the record, which claim the caller
holds, or which call is invoking it; it trusts `record.endpoint` exactly
as currently stored, unconditionally.

The precise property that failed: `§8a` showed *"the claim key and what
gets registered are identical within one call"* — true, but irrelevant.
The property item 1 actually needs is:

```
claimed_provider_session_key == actual_provider_session_invoked
```

held for the *entire* protected operation, not just at the moment of
registration. `handle_turn()` re-reading Presence at step 5 (and step 3)
means the *invoked* side of that equation is decided by whichever
register() happened to land last, globally, across every in-flight
`shared_session_id`-sharing caller — not by what the claim-holder itself
requested.

### 9.2 Why the Presence round-trip is unsafe regardless of sequencing

The register()-then-resolve() pattern is unsafe **no matter when it
happens relative to claim acquisition**, because the claim never protects
`PresenceRegistry`'s `_by_session[shared_session_id]` slot — it's keyed on
a different identity entirely. Moving the register()/resolve() pair
earlier, later, or wrapping it in the claim doesn't help: the claim for
key `(A,123)` provides zero exclusion over writes to `presence._by_session[S]`,
which any caller naming *any* other native pair, under the *same*
`shared_session_id`, can freely perform. The bug isn't in the ordering;
it's in using a globally-shared, coarsely-keyed store as the channel for
a value that needs to stay scoped to one already-in-flight, specifically-
claimed call.

### 9.3 Option comparison

**Option 1 — pass the validated request binding directly into
`handle_turn()`; never re-derive it from Presence for dispatch.**
`_handle_dispatch` already has every field needed
(`provider_id`, `model_id`, `provider_session_id`, `agent_id`,
`instance_id`, `shared_session_id`, `launch_options` — the same fields
§8a already identified as available, side-effect-free, at function entry)
to construct a `ProviderSessionBinding` directly, with no read of
`PresenceRegistry` in the path at all. `handle_turn()` takes this as an
explicit, required parameter and uses it, unmodified, at step 5 (dispatch)
and step 8 (cursor advance) instead of calling
`ProviderSessionBinding.from_presence_record(record)`. Because the same
Python value is used to acquire the claim *and* to dispatch, with no
intervening read of mutable shared state, `claimed_key ==
actual_invoked` holds by construction — there is no step left where they
*could* diverge, for any interleaving. This is the only option below that
makes the invariant **structurally true** rather than **usually true**.

**Option 2 — resolve/snapshot an authoritative binding once before
claiming, carry the snapshot through the turn.** On inspection this
degenerates to Option 1 or fails, depending on how "resolve" is read. If
"resolve" means *read it back from `PresenceRegistry`* (even once, even
before the claim, even under the claim), it inherits exactly the same
vulnerability §9.1 traces — the claim doesn't protect that read no matter
where it sits in the sequence, and another caller's concurrent register()
for the same `shared_session_id` can still land before this call's
"snapshot" read. The *only* way to make a "snapshot" genuinely safe is
for it to never touch `PresenceRegistry` for this purpose at all — at
which point it is Option 1, not a distinct alternative. Not recommended
as a separate design; recorded to show it was considered and why it
collapses into Option 1 rather than competing with it.

**Option 3 — additionally serialize mutation/resolution of
`shared_session_id`.** Would close the race (only one in-flight
`/dispatch` per `shared_session_id` at a time), but at real cost: it
requires a *second*, independent lock with its own key
(`shared_session_id`), its own TTL/lifetime/failure-semantics design (all
of §§4/6/8b redone for a second primitive), and it re-conflates dispatch
ownership with Presence exactly as the original TODO's caution against
extending `PresenceRegistry` warned against — just moved one layer over.
It's also insufficient *alone*: it does nothing for two *different*
`shared_session_id`s that happen to target the *same*
`(provider_id, provider_session_id)` — the exact case the
`(provider_id, provider_session_id)` claim exists for — so it would have
to be layered on top of, not instead of, everything in §§1–8, roughly
doubling the design surface for a result Option 1 achieves with no lock
at all. There is also a legitimacy question worth naming: the continuity
model already treats "the active provider for a `shared_session_id`" as
strictly single-valued at any moment (most-recent-register-wins) — so two
concurrent dispatches to *different* providers for the *same*
`shared_session_id` are arguably never a "legitimate concurrency" case
this system wants to support in parallel in the first place, independent
of the mutex question. Not recommended: more design surface for a
narrower fix than Option 1, layered on top of Option 1 rather than
replacing any part of it.

**Option 4 — detect-and-reject: keep `handle_turn()`'s resolve-based
binding, but compare it against the claimed key immediately before
dispatch and raise instead of proceeding on mismatch.** Smaller diff than
Option 1 — no new `handle_turn()` parameter. But it only *detects* the
drift after it has already happened, rather than preventing the read
that causes it, and it fails the "impossible," not merely "checked,"
bar: it still requires the Presence round-trip and its associated
register()-then-resolve() footgun to exist at all, decorated with a
guard rather than removed. It's also strictly worse for the *caller*: in
the §9.1 trace, A's own request — for the uncontended, correctly-claimed
target `(A,123)` — would be spuriously failed purely because of B's
unrelated, concurrent activity on the same `shared_session_id`, even
though nothing was ever actually wrong with `(A,123)` itself. Option 1
lets A succeed on its own merits, unaffected by B, which is strictly
better on correctness, availability, and simplicity (no new error code,
no new comparison, no continued reliance on the pattern that caused the
bug). Not recommended, named explicitly because it was the "smaller
diff" temptation and rejected on principle, not size.

**Decision: Option 1.**

### 9.4 What Presence is being asked to be — two meanings, conflated

Asked directly: why does `_handle_dispatch` write the caller-supplied
binding into `PresenceRegistry` at all? Two genuinely different things
are happening under one `register()` call today:

1. **Persistent/dynamic body presence** — `PresenceRegistry`'s own
   documented purpose: "is a specific instance of an already-authorized
   agent reachable right now, under which session?" Real, load-bearing,
   used independently of any one in-flight dispatch — `/presence/resolve`
   as a standalone query, `/presence/renew`/`/presence/deregister`
   lifecycle, and `handle_turn()`'s own step 6 (re-resolve Presence,
   validate the *response*'s claimed actor against whoever Presence
   *currently* reports active — a legitimate, independent authorization
   check on the response side, unaffected by anything in this revision).
2. **Temporary per-call routing state** — using `register()`+later
   `resolve()` purely as a side-channel to carry *this specific call's*
   already-known binding from `_handle_dispatch` into `handle_turn()`,
   because `handle_turn()`'s signature doesn't accept it directly. This
   has nothing to do with reachability; it's argument-passing that
   happens to reuse Presence's data shape.

Meaning 2 is what's unsafe, precisely because it's being stored in a
structure whose entire design (meaning 1) requires it to be freely,
immediately overwritable by any other caller's own liveness update
("most-recent-register-wins" is *correct* for meaning 1, and is exactly
what makes it *wrong* for meaning 2). The fix is not to stop calling
`presence.register()` — meaning 1 remains real and needed — it's to stop
reading meaning 2 back out of it for dispatch routing.

### 9.5 The corrected design

- `_handle_dispatch` constructs `binding = ProviderSessionBinding(...)`
  directly from `body`'s own required fields, first — pure, no side
  effects, no Presence read.
- Acquire the claim on `(binding.provider_id, binding.provider_session_id)`
  next (cheaper to fail fast here than to also perform a `presence.register()`
  that's about to be wasted on a `DISPATCH_BUSY` rejection — a small,
  free simplification Option 1 enables that wasn't available in §8a's
  ordering).
- `presence.register(...)` unchanged — still real, still meaning 1, now
  clearly decoupled from routing.
- `SharedSessionBridge.handle_turn()` gains a new **required** parameter,
  `binding: ProviderSessionBinding` (no default — see below for why not
  optional). Step 5 and step 8 use it directly; `from_presence_record()`
  is no longer called for dispatch purposes anywhere in this path.
- Step 3's `presence.resolve(session_id)` **stays exactly as it is
  today** — its role was always "does presence exist at all for this
  session" (`PROVIDER_NOT_REGISTERED` if not), which is a legitimate,
  independent gate; it simply stops being *also* the binding source.
  Explicitly not adding a check that the resolved record matches the
  passed-in `binding` — that would reintroduce a Presence-race-sensitive
  comparison and reproduce Option 4's spurious-failure problem for no
  benefit.
- Step 6 (re-resolve Presence, validate the response actor) is unchanged
  and remains meaningful — it's now unambiguously a pure
  response-authorization check, decoupled from dispatch routing, which is
  arguably a clearer statement of what Gate 11 always intended.
- **Required, not optional, with no presence-derived fallback.** An
  `Optional[ProviderSessionBinding] = None` parameter that falls back to
  today's `from_presence_record()` behavior when omitted would leave the
  vulnerable path reachable by any caller (existing proof scripts, tests)
  that simply doesn't pass one — "avoidable if you remember to," not
  "impossible," failing the bar this revision was asked to meet. Making
  it required is a call-site-breaking change: every existing caller of
  `handle_turn()` (proof scripts under `tier1/engainos/tools/`, the test
  suite) needs updating to construct and pass its own binding explicitly.
  Recorded here as necessary follow-on implementation work, not a
  deferred risk.

This gives the architectural split you'd expect once the two Presence
meanings are named separately: **the dispatch binding becomes a frozen
property of the turn** (constructed once, from the validated request,
never re-read), while **Presence remains purely dynamic system state**
(liveness/reachability, freely overwritable, exactly as
`PresenceRegistry`'s own documentation already says it should be) — no
longer asked to also serve as a mid-flight routing channel for a value
the caller already had.

### 9.6 Updated recommendation (supersedes §8a and the original Recommendation)

Same as the original Recommendation for everything in §§1–8b (mutex key,
critical-section lifetime, `SessionClaimRegistry` extension,
`DISPATCH_BUSY` semantics, fresh per-request `instance_id`, TTL formula,
single-authority-process precondition) — **except** §8a's binding-sourcing
conclusion, replaced by §9.5: `_handle_dispatch` builds the
`ProviderSessionBinding` directly from the request body before touching
Presence or the claim registry; `SharedSessionBridge.handle_turn()` takes
that binding as a new required parameter and uses it for dispatch and
cursor-advance instead of re-deriving it from `PresenceRegistry`; all
existing `handle_turn()` call sites (proof scripts, tests) need updating
to pass their own binding explicitly, with no presence-derived fallback
path left reachable.

Not yet implemented. `SessionLedger.append()`'s `turn_id` race remains a
separate, recorded, not-fixed-here item (companion document).
