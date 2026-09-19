# Fix plan: adapter error-response correlation + inner timeout policy

Spec only. No code in this repo, `godot_engain_3d_avatar`, `engain_door.py`,
`mrlore_query.py`, or Dragon routing has been touched. This addresses
exactly the two defects confirmed in
`09-18-2026-hermes-adapter-timeout-trace.md` (committed `32087d6`) and
nothing else — door behavior, Mettaext, MrLore, and Dragon's own
authority-selection logic are out of scope and stay as they already
proved themselves in the live test.

## Defect A — error-response correlation contract

**File:** `hermes_session_adapter.py`
**Function:** `_error_response()` (`:3327-3358`)

**Current behavior:** takes an optional `call_id: str | None = None`
keyword, defaulting to `None`; only adds the `"call_id"` key to the
result dict when a caller explicitly passes one. Every existing call
site (`:2241`, `:2277`, `:2299`, `:2318`, `:2465`, `:2474`, `:2483`)
omits it, so every error response this function produces is missing
the key outright. Meanwhile the two success-path builders,
`_engain_continuity_response()` (`:3271-3272`) and `_sanitize_response()`
(`:3316-3317`), already do this correctly:
```python
if validated.has_call_contract:
    result["call_id"] = validated.call_id
```
`_validate_request()` (`:2640-2641`) already enforces `call_id ==
request_id` as a hard invariant on every incoming payload — the two
are never allowed to differ. So `call_id` is always derivable from
`request_id` the moment a request is known at all, legacy schema or
not.

**Proposed behavior:** give `_error_response()` the same two pieces of
information the success builders already use — `has_call_contract:
bool` and `call_id: str | None` — instead of a single optional
`call_id` that most callers skip, and apply the identical conditional:
```python
def _error_response(
    self,
    narrative: str,
    request_id: str = "malformed_request",
    client_request_id: str = "",
    *,
    has_call_contract: bool = False,
    call_id: str | None = None,
    perception: ValidatedPerception | None = None,
    failure_code: str | None = None,
) -> dict[str, Any]:
    ...
    if has_call_contract:
        result["call_id"] = call_id
```
Then update each call site:
- `:2465, :2474, :2483` (inside the dispatch `try`, after
  `validated = self._validate_request(payload)` succeeded): pass
  `has_call_contract=validated.has_call_contract, call_id=validated.call_id`
  — `validated` is already in scope at all three.
- `:2277` (`PerceptionValidationError`) and `:2299` (decode/JSON
  error): these run on a partial, manual parse *before* full
  validation succeeds (`:2255-2267`). Extend that manual parse to also
  read `call_id = payload.get("call_id", request_id)` and
  `has_call_contract = isinstance(payload, dict) and set(payload) in
  (legacy_keys, current_keys)` (mirroring `:2624-2630`), then thread
  both through.
- `:2318` (reserved-request replay block): `validated` is not yet
  bound at this point in the function (it's assigned at `:2271`,
  *after* this check) — reorder so the reservation check runs after
  `validated` exists, or extract `has_call_contract`/`call_id` the same
  manual way as the two branches above. Either is acceptable; reordering
  is simpler and removes a second manual-parse duplicate.
- `:2241` (`OSError` reading the raw request bytes): no payload was
  ever parsed, so no `call_id` can be known — this one stays as it is.
  Flagged explicitly as a residual, structurally unavoidable gap: if
  the request's own bytes can't be read, there is no request_id/call_id
  to correlate against, and GDScript will still (correctly) report this
  one as uncorrelated. Not part of this fix.

**Regression tests (adapter side, no live Hermes/subprocess needed —
these only need a fake payload and `HermesTimeoutError`/exception
injection):**
1. `test_timeout_error_response_contains_exact_call_id` — force
   `HermesTimeoutError` out of `_run_bounded()` (or stub the director
   bridge to raise it directly) for a request built with the current
   (`call_id`-bearing) schema; assert the written response's `call_id`
   equals the request's `call_id`/`request_id`.
2. `test_schema_invalid_error_response_contains_exact_call_id` — feed a
   request that fails `_validate_request()` partway through (e.g. bad
   `additional_context`) but still has a syntactically valid
   `request_id`/`call_id`; assert the resulting `_error_response()`
   still carries the right `call_id`.
3. `test_generic_provider_failure_response_contains_exact_call_id` —
   force the catch-all `except Exception` branch (`:2482`); same
   assertion.
4. `test_legacy_schema_error_response_omits_call_id_key` — a
   legacy-shape request (no `call_id`/`expires_at` keys at all) hitting
   any error branch must still produce a response *without* a `call_id`
   key at all (not `null`) — this is the existing, already-correct
   legacy behavior and must not regress.

**Regression test (GDScript side, exercising the real contract, not
just the Python dict shape):**
5. `test_dragon_accepts_correlated_error_response` — feed
   `_validate_correlated_response()` a dict matching what fix #1 above
   now produces (real `call_id` present, real `request_id`/
   `client_request_id` matching `_active_*`, valid `narrative_response`
   text, `action_type == "OBSERVATION"`, etc.); assert it now returns
   `true` and the narrative ("Hermes timed out. The dragon is still
   here; please try again.") reaches `_emit_dragon()` instead of
   `_emit_err()`.

**Risk:** low. This only adds a key that was structurally always
knowable and always required; it does not relax any existing check,
change the success path, or touch `RESPONSE_SCHEMA` itself. The one
thing to verify carefully in review is the reordering at `:2318`
(moving the reservation check after `_validate_request()`), since that
changes when a replay gets rejected relative to full payload
validation — worth an explicit test that a reserved/replayed request
with an otherwise-invalid payload still fails for the *right* reason.

## Defect B — inner timeout policy, not just its size

**Files:** `hermes_session_adapter.py:76` (constant),
`EngAInBridge3D.gd:30-44,210-221,234,240` (outer watchdog + its message)

**Current behavior:** `MAX_HERMES_TIMEOUT_SECONDS = 180.0` is an
independently-chosen module constant for the *local* (non-continuity)
path — not derived from anything else in the codebase. Separately, the
continuity-dispatch path already has its own, explicitly-widened policy
value for "how long may a provider legitimately take":
`ENGAIN_CONTINUITY_PROVIDER_TIMEOUT_S` (default `240.0`) +
`ENGAIN_CONTINUITY_TIMEOUT_MARGIN_S` (default `15.0`). That widening
happened for a documented reason (`EngAInBridge3D.gd:30-40`): 180s
was found, by live incident, to be too short for a real turn. The
local path's own inner subprocess timeout was never reconciled with
that finding — it still hardcodes the pre-incident number. This live
test is a second, independent demonstration of the same class of
problem: a real, in-scope, multi-door turn used the entire 180s budget
and was SIGKILLed mid-flight, one tool-call short of its answer.

Separately, `EngAInBridge3D.gd:234` and `:240` unconditionally print
the literal string `"Mailbox timeout after 180.0 seconds."` regardless
of what `WAIT_TIMEOUT_SEC` (dynamically computed, `:210-221`, currently
defaulting to `270.0`) actually is.

**Proposed behavior:**
1. Do not give the local path a second, larger, independently-chosen
   literal. Instead, make its default *equal to* the policy value the
   codebase already established as "how long a provider may legitimately
   run," rather than maintaining a second, smaller, unreconciled number:
   ```python
   MAX_HERMES_TIMEOUT_SECONDS = float(
       os.environ.get(
           "ENGAIN_HERMES_TIMEOUT",
           os.environ.get("ENGAIN_CONTINUITY_PROVIDER_TIMEOUT_S", "240.0"),
       )
   )
   ```
   This keeps `ENGAIN_HERMES_TIMEOUT` as the explicit per-path override
   it already is (unchanged for anyone currently setting it), but
   changes what happens when *nothing* is set: the local path now
   inherits the same 240.0s policy value the continuity path already
   uses, instead of falling back to the smaller, pre-incident 180.0.
   `EngAInBridge3D.gd`'s own `_compute_wait_timeout_sec()` needs no
   change at all — it already takes `max(local_timeout,
   continuity_client_timeout) + timeout_margin`, so raising the local
   default to 240.0 automatically keeps the outer/inner ordering
   correct (`max(240, 255) + 15 = 270`, same outer result as today,
   for a different, no-longer-arbitrary reason) while giving the local
   path 60 more real seconds before a hard kill.
2. Fix the stale diagnostic text at `:234` and `:240`:
   ```gdscript
   _emit_err("Mailbox timeout after %.1f seconds." % WAIT_TIMEOUT_SEC)
   ```
   so the message always reflects the value actually enforced, not a
   number left over from before `_compute_wait_timeout_sec()` existed.

**Regression tests:**
6. `test_local_hermes_timeout_defaults_to_provider_timeout_policy` —
   with neither `ENGAIN_HERMES_TIMEOUT` nor
   `ENGAIN_CONTINUITY_PROVIDER_TIMEOUT_S` set, assert
   `MAX_HERMES_TIMEOUT_SECONDS`-equivalent resolves to `240.0`, not
   `180.0`.
7. `test_explicit_hermes_timeout_override_still_wins` — with
   `ENGAIN_HERMES_TIMEOUT` set, assert it still takes priority over the
   provider-timeout-derived default (no regression to the existing,
   already-documented override behavior).
8. `test_inner_timeout_never_exceeds_outer_budget` — for a matrix of
   env-var combinations (defaults; `ENGAIN_HERMES_TIMEOUT` only;
   `ENGAIN_CONTINUITY_PROVIDER_TIMEOUT_S` only; both), assert
   `_compute_wait_timeout_sec()`'s result is always strictly greater
   than the adapter's resolved `MAX_HERMES_TIMEOUT_SECONDS`-equivalent
   by at least `timeout_margin` — this is the invariant the 2026-09-13
   fix established for the continuity path; this test makes it hold
   for the local path too, and catches future drift between the two
   files.
9. `test_timeout_diagnostic_reports_actual_effective_value` — set
   `ENGAIN_HERMES_TIMEOUT`/provider env vars to a non-default value,
   force the outer watchdog to fire, assert the emitted `[ERR]` string
   contains that actual computed `WAIT_TIMEOUT_SEC`, not the literal
   `"180.0"`.

**Risk:** low-moderate. Raising the local path's real timeout from
180s to 240s is a behavior change a live player could notice (a stuck
request now visibly hangs 60s longer before any error surfaces) — but
it directly targets the mechanism that killed this exact live turn
before it could answer, and the outer watchdog's already-correct
`max(...)+margin` formula absorbs it without needing its own edit.
The one thing worth confirming in review before merging: whether
anything downstream assumes `MAX_HERMES_TIMEOUT_SECONDS` is a
compile-time-constant `180.0` rather than an environment-resolved
value (a quick grep of both files for direct references to the literal
`180` beyond the two spots already identified here is worth doing at
implementation time, not assumed clean from this read-only pass).

## Explicitly out of scope for this fix

No change to `engain_door.py`, `mrlore_query.py`, the (still-absent)
formal `mrlore_door.py`, `_dispatch_via_engain_continuity`, or any
authority-selection/routing logic. The live test already proved Dragon
picks the right authority on its own; these two defects are why its
answer never arrived, not why it chose what it chose.

## Suggested validation after implementation

Once A and B land, re-run the *exact* original prompt from the
2026-09-18 live test unchanged (not a new one) — the same request text,
same session — as a clean before/after comparison rather than moving
the target. Not run as part of this plan; this document stops at the
proposal per instruction.
