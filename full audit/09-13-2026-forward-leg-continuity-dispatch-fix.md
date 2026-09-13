# 09-13-2026 — Forward Dragon→Editor leg was dead under continuity dispatch

## Trigger

Live test screenshot: Dragon (routed through `ENGAIN_CONTINUITY_DISPATCH=1
ENGAIN_CONTINUITY_SHARED_SESSION_ID=dragon3d_main`) visibly emitted a real
`[EDITOR_REQUEST]` block for `return_landing_sigil_01` in its
`narrative_response`, but the Hermes Editor dock's "Pending Dragon
requests (human-confirm, DIRECT_WRITE)" list stayed empty. User correctly
diagnosed the likely cause before I touched any code: continuity dispatch
might be returning Dragon's response through a path that bypasses
`_extract_editor_directive()`, and asked for that to be traced and fixed
narrowly — no auto-reload, no completion-semantics redesign, nothing else.

## Root cause, confirmed not assumed

`git log --follow -p -- hermes_session_adapter.py` shows the
continuity-dispatch branch of `_process_claimed_request()` has never
called `_extract_editor_directive()` — not since continuity dispatch was
first introduced (2026-08-17), which predates Phase 1's
`[EDITOR_REQUEST]` extraction machinery entirely. The local
(non-continuity) branch already called it correctly from the start. This
session's own earlier work touched this exact `if` branch (removing the
old `COORDINATION_UNSUPPORTED_ON_CONTINUITY_DISPATCH` refusal) but did
not remove or break an existing call — there was never one there to
remove. Confirmed by reading every version of this block back through
history, not inferred.

## Fix

One line: `safe_response = self._extract_editor_directive(safe_response)`
added to the continuity branch, immediately after
`_engain_continuity_response()` builds `safe_response` — identical to
what the local branch already does. No other change.

## Proof

- `git stash` the fix, ran the new test first: **0 outbox files** where 1
  was expected — the exact failure from the screenshot, reproduced as a
  real RED, not just described.
- Restored the fix: outbox gets a real `engain.dragon_request.v1` with
  the correct body, `source`/`destination`, and the player-facing
  `narrative_response` has the `[EDITOR_REQUEST]` block stripped (same
  as the local path).
- Full targeted sweep (`test_engain_continuity_dispatch.py` +
  `test_hermes_session_adapter.py`): 64/65 passed; the 1 failure is the
  same pre-existing, unrelated scene-freeze test already confirmed
  unrelated in an earlier receipt.

## What this does NOT prove yet

This proves the fix at the Python/unit level against a fake `/dispatch`
server. It does **not** yet prove the live Hermes Editor dock actually
renders the row and the Execute button works end-to-end against the real
running system — that requires physically re-running
`return_landing_sigil_01` (or an equivalent harmless request) live, per
the user's own acceptance test:

1. Dragon emits `[EDITOR_REQUEST]` in `narrative_response` — already
   true, unaffected by this fix.
2. Existing extraction logic sees it — fixed, proven at unit level.
3. `engain.dragon_request.v1` is published — fixed, proven at unit level.
4. Hermes Editor sees it in "Pending Dragon requests" — **not yet proven
   live**, requires a real re-run.
5. User can click the existing Execute control — **not yet proven live**,
   unaffected by this fix but not exercised by it either.

## Explicitly deferred, per instruction

No auto-reload, no runtime-consumption verification, no
COMPLETED/REFUSED/FAILED redesign — Dragon's own stricter acceptance
criteria from the `return_landing_sigil_01` request remain a recorded
future design target, not implemented here.
