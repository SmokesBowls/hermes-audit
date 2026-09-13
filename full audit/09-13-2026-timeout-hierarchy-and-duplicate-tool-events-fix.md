# 09-13-2026 — Timeout hierarchy fix + duplicate [TOOL] event fix

## Trigger

Live symptom: the automatic Editor→coordination-report→/dispatch→Hermes
return path reached `dispatch_via_hermes_cli()` and a real
`hermes chat --resume 20260731_065008_63a62d` call, but never returned
within 90 seconds — client-side "unreachable: timed out", server-side a
502 `PROVIDER_DISPATCH_FAILED` sent to an already-disconnected client
(BrokenPipeError, correctly identified as downstream noise, not root
cause). Separately, the ControlHUD showed identical `[TOOL]` lines
repeating for the same request ids. User asked for discovery only,
first — see the prior turn's report — then accepted the findings and
asked for exactly two corrections, no more.

## A — timeout hierarchy

**Root cause, live-reproduced, not inferred**: `hermes_provider_adapter
.DEFAULT_TIMEOUT_S` (EngAIn) and `engain_continuity_client.py`'s own
HTTP `timeout` default (dragon3d) were independently hardcoded to the
same `90.0` in two different repos. Reproduced the exact call live,
system idle:

```
hermes chat -Q --pass-session-id --ignore-rules --source tool \
  --provider openai-codex -m gpt-5.6-sol --resume 20260731_065008_63a62d \
  -q "Diagnostic ping..."
↻ Resumed session 20260731_065008_63a62d (101 user messages, 202 total messages)
session_id: 20260731_065008_63a62d
real 2m32.090s  (152.09s)
```

A real, successful call — not a hang. 152.09s vs. a shared 90s budget on
both sides, with the client's own clock starting earlier in the chain
(HTTP connect + claim/register + Ledger reads, all before the server's
`subprocess.run()` even begins) — guaranteed the client would give up at
or before the server's own inner timeout could resolve cleanly, every
time this session was dispatched to.

**Fix**:
- `hermes_provider_adapter.py` (EngAIn): `DEFAULT_TIMEOUT_S` is now
  `240.0` (152.09s + real headroom, not a round-number guess),
  configurable via `ENGAIN_CONTINUITY_PROVIDER_TIMEOUT_S`. Still the one
  source `_dispatch_claim_lease_seconds()` reads — that lease grows to
  255s automatically, no separate change needed.
- `engain_continuity_client.py` (dragon3d, cannot import the above
  directly — deliberately vendored): derives its own `DEFAULT_TIMEOUT_S`
  as `provider_timeout + margin` (240.0 + 15.0 = 255.0), tracking the
  EngAIn value via the *same env var name* rather than a shared import,
  plus `ENGAIN_CONTINUITY_TIMEOUT_MARGIN_S` for the margin.
- No new queue/transport/retry system. `claude_code_provider_adapter.py`
  untouched — out of scope, no evidence of a problem there.

**Tests**: `test_hermes_provider_adapter_timeout.py` (EngAIn, new, 6
tests) proves the mechanism with a fake `hermes` executable at
test-friendly scale (seconds, not real minutes) — a call killed by a
narrow timeout survives a wider one; the real configured default
exceeds the real 152.09s observation; session-drift detection
unaffected. `test_engain_continuity_dispatch.py` (dragon3d, +2 tests)
proves the client's derived value and its env-var overrides. 49/49 and
89/90 respectively across the full targeted sweeps (the one dragon3d
failure is the same pre-existing, unrelated scene-freeze test).

## B — duplicate [TOOL] events

**Root cause, confirmed from real mailbox artifacts, not inferred**: 6
files in `tool_events_handled/`, 3 identical per request id, ~90.2s
apart — matching 3 retry attempts (`attempt0`→`attempt1`→`attempt2`)
before landing in `failed/`. A report's `message_id` is stable across
retries (only the filename's `attempt` suffix changes), but
`_publish_tool_event("tool", ...)` fired unconditionally on every read —
including every retry of the same underlying report.

**Fix**: gate the "tool" publish on `coord_attempt == 0` at both call
sites (`_process_pending_coordination_report_without_player_turn()` and
the player-turn coordination-disposal path in
`_process_claimed_request()`), including the malformed-report branch.
Dispatch retry mechanics (claim/dispose/attempt-increment/failed-ceiling)
are completely unchanged. The "dragon" event needed no gate — it only
ever fires on a successful attempt, which ends the retry loop by
definition, so it was never duplicable this way.

**Tests**: `test_one_report_retried_three_times_produces_exactly_one_tool_event`
(three real HTTP attempts + real `failed/` landing, exactly one tool
event) and `test_two_different_report_message_ids_each_publish_their_own_tool_event`
(dedup doesn't over-fire).

## Relationship between A and B

Related but distinct, as instructed: B's triplication was *triggered*
by A (repeated failed retries), but is a separate, real defect on its
own — any future retry-after-failure, for any reason, would have
produced the same triplication without B's fix. Fixing A alone would
not have fixed B; fixing B alone would not have fixed A.

## Explicitly not touched, per instruction

Godot live-reload/SIGABRT, status wording/semantics, authority model,
session rotation/compaction. The live session's own growth (101 user
messages / 202 total since July 31) is noted as a real, separate future
concern — if provider latency keeps growing with session size, even
240s may eventually be insufficient — but is a session-lifecycle/
compaction problem, not mixed into this fix.
