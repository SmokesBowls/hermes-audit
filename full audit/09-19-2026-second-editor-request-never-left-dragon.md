# The second [EDITOR_REQUEST] never left Dragon — a distinct, real bug

Diagnosis only, per instruction. Nothing in `EngAIn`,
`godot_engain_3d_avatar`, or `engain-avatar-audit` was modified.

## Direct answers

**Exact Dragon request/report IDs.**

```text
First post-restart round trip:
  dragon_request:  dragonreq_20260919_125810_54c2a386
  editor_report:   20260919_060024_11f0  (consumed/, attempt0)

Second ("_report" follow-up) request:
  Dragon's own label inside the text: read_first_scene_ethereal_vigil_01_report
  dragon_request file: NONE EVER CREATED
  editor_report:       NONE EVER CREATED
```

**Did the second request reach `outbox_handled`?** No. `outbox/`
contains only three stale files from 2026-09-13; `outbox_handled/` has
nothing newer than the first request's `06:00` file. No file matching
this second request exists anywhere in the coordination tree.

**Did a fresh Editor Hermes session run?** No. `list_pending_dragon_
requests()` (the function `hermes_dock.gd`/the runtime's own dragon-
request processing loop polls) only ever discovers files that exist in
the outbox — since none was ever written for this request, nothing
triggered a new Editor-side `hermes chat` invocation.

**Exact EngAIn door calls/results for the second request.** None.
No Editor session ran, so no door was ever invoked.

**Was `result_text` populated again?** Not applicable — no report of
any kind was generated for this request, so there is no `result_text`
to check.

**Did the report land in `consumed/`?** No. There is no second report.

**What did `ContinuityContextBuilder` deliver to Dragon in response to
this second request?** Nothing, because nothing ever came back for it
to deliver. `hermes_session_adapter.py`'s own `messages` history for
this session has zero rows after `id=50272` (Dragon's second
`[EDITOR_REQUEST]` turn) — confirmed directly by querying `state.db`.

**Dragon's response after "receiving" it.** There was nothing to
receive, and no further Dragon message exists. Dragon has not spoken
again since emitting the second request.

**Did Dragon emit a third request, indicating a repeat loop?** No —
and structurally it had no occasion to, since nothing ever returned to
prompt a further turn. This is not a retry loop; it's a dead end.

## Root cause: a second, distinct, real bug — this time inside `godot_engain_3d_avatar`, not `EngAIn`

`_process_pending_coordination_report_without_player_turn()`
(`hermes_session_adapter.py:1762-1914` — the same function whose
docstring explained the `EngAIn`-side truncation traced in the eighth-
test receipt) dispatches Dragon's reaction like this, in full:

```python
engain_result = self._dispatch_via_engain_continuity(
    "", coordination_report=coordination_report
)
delivered = True
reply = str(engain_result.get("response", "")).strip()
if reply:
    self._publish_tool_event("dragon", reply)
```

`_extract_editor_directive()` — the one function anywhere in this file
that turns a `[EDITOR_REQUEST]...[/EDITOR_REQUEST]` block into a real
`dragon_request.v1` file via `_publish_dragon_directive()` — is called
from exactly two places in the whole file (`:2497`, `:2506`), both
inside the ordinary per-player-turn dispatch flow in `_process_claimed_
request()`. Verified by grep: it is never called anywhere in
`_process_pending_coordination_report_without_player_turn()`.

So when Dragon's reaction to *this specific kind* of turn (a
coordination-report delivery with no player message attached) contains
its own `[EDITOR_REQUEST]` block, that text is published only to
`_publish_tool_event("dragon", reply)` — the same display-only channel
described in `EngAInBridge3D.gd`'s own comments as carrying "no
authority: nothing here ever sets `_busy`, claims a dispatch lock, or
feeds `_validate_correlated_response()`... It only ever adds a line to
the transcript." The block is shown as text and then structurally
discarded — there is no code path from there to `_publish_dragon_
directive()`.

## Comparison: first round trip vs. second

```text
                          First (dragonreq_...54c2a386)   Second ("_report" follow-up)
dragon_request published?      YES                             NO
reached outbox_handled?        YES                             NO
fresh Editor session ran?      YES                             NO
door calls made?               YES (status, query x2)          NO
result_text populated?         YES, rich and complete          N/A -- no report exists
report reached consumed/?      YES, attempt0                   N/A
ContinuityContextBuilder
  delivered to Dragon:         status + summary only           nothing (no report to relay)
Dragon's follow-up:            correctly identified the gap,    none -- turn is a dead end
                                re-issued a second request
```

The first request worked all the way through the `godot_engain_3d_
avatar` side of the pipeline and was only truncated by `EngAIn`'s
`ContinuityContextBuilder` (per the eighth-test receipt). The second
request never got that far — it failed at the very first step,
inside `godot_engain_3d_avatar` itself, before ever reaching the
outbox.

## Two independent, now-confirmed defects, not one

```text
Defect 1 (EngAIn, third repo, per the eighth-test receipt):
  ContinuityContextBuilder._format_coordination_report() only reads
  status/execution_summary -- result_text never reaches Dragon on a
  SUCCESSFULLY delivered report.

Defect 2 (godot_engain_3d_avatar, this receipt):
  _process_pending_coordination_report_without_player_turn() never
  calls _extract_editor_directive() -- an [EDITOR_REQUEST] Dragon
  emits DURING a coordination-only turn can never reach the outbox at
  all, regardless of what EngAIn does with the report content.
```

Both defects sit on the same "no-player-turn coordination delivery"
code path, but they are independent: fixing #1 alone would let
`result_text` reach Dragon, but any follow-up `[EDITOR_REQUEST]` Dragon
then writes in reaction would still vanish per #2. Fixing #2 alone
would let a follow-up request reach the outbox, but its own eventual
report would still be truncated by #1 before Dragon could read it.
Both need fixing for the full "ask again if the first answer was
incomplete" loop to actually work.

## What was not done, per instruction

No change to `EngAIn`, `godot_engain_3d_avatar`, or `engain-avatar-
audit`. Diagnosis only.
