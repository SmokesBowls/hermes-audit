# Hermes adapter timeout trace — read-only follow-up to the first live door-test baseline

Follows `09-18-2026-first-live-door-test-diagnosis.md` (committed
`536cce7`, left unmodified — this is an additive trace, not a
correction of that file). Scope held to exactly what was asked: confirm
or falsify the 180s-cutoff hypothesis by reading
`hermes_session_adapter.py` and the surrounding timeout path, no code
changed, nothing rerun. Two mechanisms turned out to be involved, and
the second one is a real, independently-reproducible bug rather than a
timing coincidence — reported plainly rather than folded into "probably
a timeout."

## Is there one shared 180s timeout, or several independent ones?

**Two distinct mechanisms, not one shared constant — and they are no
longer numerically equal in current code, though the observed error
text falsely implies they are.**

**1. The inner limit — real, still literally 180.0s, and it is a hard
kill, not an idle/abandoned process.**
`hermes_session_adapter.py:76`: `MAX_HERMES_TIMEOUT_SECONDS = 180.0`
(overridable via `ENGAIN_HERMES_TIMEOUT`). Enforced in `_run_bounded()`
(`:1174-1237`): a single `subprocess.Popen(command, start_new_session=
True, ...)` launches `hermes` once per adapter invocation; a selector
loop reads its stdout/stderr incrementally against `deadline =
time.monotonic() + self.timeout_seconds`; on expiry it calls
`_terminate_process()` (`:1263-1274`), which does:

```python
os.killpg(process.pid, signal.SIGKILL)   # whole process group, not just the child
```

with a 5s grace wait and a fallback `process.kill()` if that doesn't
land. **This directly answers the "killed, abandoned, or just stops
producing output" question: it is genuinely, forcibly killed.** Nothing
about this path leaves the process running detached or waits for it to
finish on its own.

**2. The outer limit — GDScript's per-turn watchdog — is *not* actually
180.0s any more, and the printed message is stale/hardcoded text
independent of the real value.**
`EngAInBridge3D.gd:30-44` carries its own dated comment describing
almost exactly this incident, from **2026-09-13**, already fixed once:
originally the outer watchdog was an independent hardcoded `180.0`,
numerically equal to the adapter's inner timeout by coincidence; when
the continuity-dispatch path's inner budget was later widened to
240s+15s=255s, the outer 180s watchdog became *shorter* than a
legitimate in-flight turn and fired first, live-caught back then as
"Mailbox timeout after 180.0 seconds." immediately followed by "stale
response claimed and discarded." The recorded fix
(`_compute_wait_timeout_sec()`, `:210-221`) makes the outer timeout
dynamic:

```gdscript
var local_timeout := 180.0            # ENGAIN_HERMES_TIMEOUT override
var provider_timeout := 240.0         # ENGAIN_CONTINUITY_PROVIDER_TIMEOUT_S override
var timeout_margin := 15.0            # ENGAIN_CONTINUITY_TIMEOUT_MARGIN_S override
var continuity_client_timeout := provider_timeout + timeout_margin   # 255.0
return max(local_timeout, continuity_client_timeout) + timeout_margin  # 270.0 by default
```

With no env overrides (the ordinary case), `WAIT_TIMEOUT_SEC` computes
to **270.0 seconds**, not 180. **But the two places that actually fire
this watchdog (`:234` and `:240`) print the literal string `"Mailbox
timeout after 180.0 seconds."` regardless of what `WAIT_TIMEOUT_SEC`
actually is.** That string was never updated when the timeout became
dynamic. This is a real, currently-live bug in its own right — the
diagnostic text cannot be trusted to reflect the enforced duration —
and it is exactly the kind of thing that could mislead a future
diagnosis into treating 180s as load-bearing for the outer watchdog when
it is not.

**Net answer to "one shared timeout or several independent ones":**
historically two independent-but-numerically-identical ones (a known,
already-partially-fixed defect); currently one real 180.0s inner limit
that actually governs the Hermes subprocess, and one dynamically-sized
outer limit (270.0s by default) that no longer matches 180.0 in value
but still *prints* 180.0 when it fires.

## Does the inner 180s kill explain the "malformed, mismatched, or stale" rejection?

**Partially, and there is a second, independent, deterministic bug
underneath it that would reproduce on any error path, not just a
timeout.**

Full causal chain, traced end to end:

1. `_run_bounded()` times out at 180.0s → raises `HermesTimeoutError`.
2. Caught at `hermes_session_adapter.py:2464-2472`:
   ```python
   except HermesTimeoutError as exc:
       safe_response = self._error_response(
           "Hermes timed out. The dragon is still here; please try again.",
           request_id,
           client_request_id,
           perception=validated.perception,
           failure_code="PROVIDER_TIMEOUT",
       )
   ```
   Note: **no `call_id=` keyword argument is passed.**
3. `_error_response()` (`:3327-3358`) only ever adds a `"call_id"` key
   to the returned dict *conditionally*:
   ```python
   if call_id is not None:
       result["call_id"] = call_id
   ```
   Since the timeout branch never passes `call_id`, the resulting
   dict has **no `call_id` key at all** — not `null`, absent entirely.
4. This dict reaches the mailbox unchanged: `self._write_response(
   safe_response)` at `:2536` is the one path that serializes a
   response to `response.json`, in both the success and every error
   branch.
5. On the GDScript side, `_validate_correlated_response()`
   (`EngAInBridge3D.gd:567-605`) builds its required key set from
   `RESPONSE_SCHEMA` and only *drops* the `call_id` requirement if
   `_active_call_id == ""` (`:568-570`). But `_active_call_id` is set
   to the generated `request_id` unconditionally at submission time
   (`:340`, `_active_call_id = request_id`) — it is never empty in the
   normal flow. So `call_id` stays a required key.
6. `_has_exact_keys()` (`:659-666`) requires the response dict's key
   **count** to exactly equal the schema's key count, in addition to
   every key being a member of the schema:
   ```gdscript
   if keys.size() != schema.size():
       return false
   ```
   A response missing `call_id` fails this on the very first line, for
   size alone — before any of the semantic checks (narrative content,
   action_type, entropy_impact, etc.) are ever reached.
7. This is exactly `_validate_correlated_response()` returning `false`,
   which produces the line-536 message: `"Response rejected as
   malformed, mismatched, or stale; waiting continues."` And per
   `_poll_response_mailbox()` (`:535-537`), a `false` result does
   **not** end the busy lifecycle — it just returns and keeps waiting.
   So the request stays "busy" until the outer watchdog eventually
   fires (per above, ~270.0s by default, not 180.0, despite what its
   own message claims).

**This bug is not specific to timeouts.** Every other `_error_response()`
call site in the file — schema-invalid requests (`:2241`, `:2299`),
perception-validation failures (`:2277`), reserved-request replay
blocks (`:2318`), and the generic `except Exception` catch-all
(`:2483`) — likewise never passes `call_id`. **Any adapter-side error
response, regardless of cause, is currently guaranteed to fail
`_validate_correlated_response()`'s key-count check and be rejected as
"malformed, mismatched, or stale," even when its `narrative_response`
text is perfectly good** (e.g. "Hermes timed out. The dragon is still
here; please try again." never reaches the player — it's discarded by
the exact-key-count check before `narrative_response` is even read).

## Revised understanding of the original incident, given this

The original baseline's Q7/Q8 answers are not wrong, but this narrows
them:

- The **180s coincidence** in the baseline report (179.847s from
  request to last Hermes message) is real and still explains *why no
  genuine narrative answer was ever produced* — the inner subprocess
  really was SIGKILLed at that boundary.
- But the **"malformed, mismatched, or stale" rejection** the player
  actually saw is not really a timing race at all — it is a
  deterministic contract mismatch (`_error_response()` omitting
  `call_id`) that would fire the exact same way even for a fast, clean
  error response with no timeout involved.
- The **second ControlHUD message** (whatever its exact wording was in
  the original test — not independently re-derivable now, see the
  baseline's own §5 gap) most likely reflects the *outer* GDScript
  watchdog firing after its own (dynamically computed, ~270s-by-default)
  budget elapsed while `_busy` stayed true waiting for a response that
  would never validate — not a second independent 180s clock, and not
  literally at the 180s mark, regardless of what its hardcoded message
  text says.

## What was not done, per instruction

No timeout value, retry behavior, mailbox validation, `_error_response()`
call site, or watchdog message string was changed. Nothing was rerun.
This is a read trace only, extending the already-committed baseline
without altering it.
