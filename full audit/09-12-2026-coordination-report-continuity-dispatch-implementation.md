# 09-12-2026 — coordination_report wired into /dispatch (bounded implementation)

## Scope (per explicit instruction)

Implements exactly the chain accepted from the prior discovery note:
`/dispatch -> SharedSessionBridge.handle_turn() -> ContinuityContextBuilder
.build()`, with `coordination_report` carried separately from
`player_input`. No new mailbox, no new Dragon path, no new authority
system, no redesign of the existing Phase 1 coordination lane. The
existing dragon3d<->Editor path (outbox/inbox, human-confirm DIRECT_WRITE)
is untouched.

## Changes — EngAIn (`/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn`)

- `tier1/engainos/core/continuity_context_builder.py`: `build()` gained
  `coordination_report: Optional[dict] = None`. When present, a new
  `_format_coordination_report()` block is prepended, structurally
  parallel to the existing missing-context recap. `player_input`'s own
  text is untouched either way — verified by test, not just by
  construction.
- `tier1/engainos/bridgeroom/shared_session_bridge.py`: `handle_turn()`
  gained the same optional parameter, passed through to `build()` at
  step 5 only. **Scoping decision, stated plainly**: it is NOT added to
  `Turn`/`SessionLedger.append()`/the durable journal — it is a
  dispatch-time-only input for this one turn, not persisted as part of
  the Ledger's own history. `Turn.direction` (`"request"|"response"`)
  and the journal's crash-consistency frame shape (item 3's own
  carefully-reviewed design) are both untouched. Consequence: a native
  session that only catches up via a later recap will not learn a
  coordination_report accompanied an earlier turn — acceptable for this
  bounded change; broadening to durable storage is future work if ever
  needed, not done here.
- `tier1/engainos/server/presence_authority_server.py`: `_handle_dispatch()`
  passes `body.get("coordination_report")` through — absent by default,
  so every existing caller that never sends this field is unaffected.

## Changes — dragon3d (`/mnt/data-drive/godot_engain_3d_avatar`)

- `engain_continuity_client.py`: `dispatch()` gained the same optional
  `coordination_report` parameter, sent as its own body field (mirrors
  `snapshot`'s existing treatment exactly).
- `hermes_session_adapter.py`:
  - `_dispatch_via_engain_continuity()` gained `coordination_report`,
    passed straight through to the client.
  - The `coordination_report is not None and _engain_continuity_dispatch_enabled()`
    branch that used to hard-refuse with
    `COORDINATION_UNSUPPORTED_ON_CONTINUITY_DISPATCH` is removed —
    that combination is now supported, so it folds into the ordinary
    continuity-dispatch branch (`coordination_report` is passed whether
    it's a real report or `None`; `None` is indistinguishable from never
    sending the field).
  - `dragon_turn_succeeded = True` is now set on a successful
    continuity-dispatch turn (previously only set in the local/non-
    continuity branch) — necessary correctness fix: without it,
    `report_delivered = coordination_report is not None and
    dragon_turn_succeeded` would always be `False` on this path even on
    genuine success, so a delivered report would be endlessly
    re-attempted instead of being marked consumed.
  - The now-permanently-unreachable `coordination_structural_refusal`
    local variable and the `COORDINATION_UNSUPPORTED_ON_CONTINUITY_DISPATCH`
    constant are removed (confirmed via repo-wide grep, including `.gd`
    files, that nothing else referenced the constant — no Godot-side
    error-code handling keyed on it).
  - `engain_avatar` (2D)'s own separate copy of these files was
    deliberately NOT touched — out of scope; the coordination lane this
    task concerns is dragon3d-only.

## Tests added (all real, executed — not asserted-without-proof)

EngAIn (`python3 -m pytest tier1/engainos/tests/test_continuity_context_builder.py
tier1/engainos/tests/test_continuity_identity_boundary.py
tier1/engainos/tests/test_presence_authority_dispatch.py
tier1/engainos/tests/test_shared_session_continuity_proof.py`):
- 3 new pure `ContinuityContextBuilder.build()` cases: labeled block
  present and `player_input` byte-for-byte preserved; omitted
  `coordination_report` matches old behavior exactly; report + missing-
  context recap combine without dropping either.
- 2 new real-HTTP `/dispatch` cases: the report reaches the fake
  dispatcher's actual dispatched text while the Ledger's own recorded
  request-turn `payload` stays exactly `player_input` (the direct proof
  of "never mixed into player_input," not just an inference from the
  builder's own logic); an ordinary call with no `coordination_report`
  is unaffected (regression pin).
- **Result: 43 passed** (38 pre-existing + 5 new).

dragon3d (`python3 -m pytest tests/test_engain_continuity_dispatch.py
tests/test_hermes_session_adapter.py`):
- 1 new end-to-end case: writes a real `editor_report.v1` into the
  coordination inbox (reusing the existing `_write_editor_report()` test
  helper), runs a real continuity-dispatch turn against a fake `/dispatch`
  server, and asserts (a) the wire body's `player_input` is verbatim,
  (b) `coordination_report` arrives as its own field with the right
  `message_id`/`status`, (c) the report file is moved to `consumed/`
  (proving the `dragon_turn_succeeded` fix actually takes effect, not
  just that it compiles).
- **Result: 57 passed, 1 pre-existing unrelated failure**
  (`test_current_scene_bytes_freeze_actual_root_and_dragon_node_path` — a
  frozen-scene-bytes check against `scenes/Main.tscn`; confirmed via
  `git stash` that it fails identically with none of this session's
  changes applied, so it predates this work).

## The question asked after implementation

**What exact connection, if any, is still missing between an Editor edit
completing and that `coordination_report` being delivered into `/dispatch`
so Dragon can receive it without waiting for another player turn?**

Traced directly: `HermesSessionAdapter.process_once()`
(`hermes_session_adapter.py:1656`) is the entire trigger surface. Its
very first substantive step is:

```python
claimed_path = self._claim_request_file()
if claimed_path is None:
    return False
```

`_claim_coordination_report()` — the call that actually notices a report
sitting in the inbox — is reached only *after* this, deep inside
`_process_claimed_request()`, which only runs when a **player** request
file was successfully claimed. The worker's own run loop (`run()`:
`while True: self.process_once(); time.sleep(self.config.poll_seconds)`)
does poll on a fixed interval, but every one of those polls is a
no-op — it returns `False` at the line above — whenever no player
message is currently pending. There is no separate poll, file-watch, or
callback on the coordination inbox itself, and nothing on the Editor
side (`write_editor_report()`/`hermes_dock.gd`) signals the dragon3d
worker process when it finishes writing a report.

**So: the missing connection is a trigger independent of a player
turn** — something that makes `_claim_coordination_report()` (or an
equivalent dispatch) run when the Editor's report actually lands, not
only the next time a player happens to type something. Nothing in this
session's implementation added such a trigger, and per instruction,
nothing further is implemented here until this is reviewed.

## Follow-up (same day): the trigger itself, closing the ticket

User held the ticket open pending five conditions and specified the
exact integration test to add. Implemented in
`godot_engain_3d_avatar/hermes_session_adapter.py`:

- `process_once()`: when no player request is claimable, it now calls a
  new `_process_pending_coordination_report_without_player_turn()`
  instead of unconditionally returning `False`. The existing poll loop
  (`run(): while True: process_once(); sleep(poll_seconds)`) becomes the
  delivery mechanism — no new thread, file-watcher, or process.
- The new method fires only when continuity dispatch is enabled (local/
  non-continuity path untouched — a report still just waits for a
  player turn there). It acquires the same presence-authority dispatch
  claim a real player turn already takes, in the same order (claim
  first, then claim the report from the inbox), so a contended or
  unreachable claim costs the report no retry attempt. It claims via the
  same atomic-rename `_claim_coordination_report()`/
  `_dispose_coordination_report()` pair the player-turn path already
  uses. It dispatches with `player_input=""` (no player said anything;
  the coordination_report block alone carries content) and deliberately
  does **not** write `config.response_file` — doing so would wedge every
  subsequent real player request behind a file nothing would ever
  correlate to and claim, since `process_once()` itself refuses to claim
  a new request while that file exists.
- `_dispatch_via_engain_continuity()` now takes a plain `player_input:
  str` instead of a `ValidatedRequest`, so the real-player-turn call site
  and this new one can share it.

**Verification against the five held-open conditions:**
1. Editor completion causes dispatch with no external trigger — proven:
   `test_pending_coordination_report_dispatches_without_a_player_turn`
   writes a report and calls `process_once()` with **no request file at
   all**; the fake `/dispatch` server receives it.
2. `coordination_report` still carried separately from `player_input` —
   asserted directly on the wire body (`player_input == ""`,
   `coordination_report` present as its own key).
3. Success → moved to `consumed/`, not retried — asserted directly.
4. Failure → exactly one HTTP attempt per poll, back to `inbox/` at
   `attempt+1`, and a second poll proves it's genuinely retryable, not
   stuck — new `test_pending_coordination_report_stays_retryable_on_dispatch_failure`.
5. `COORDINATION_UNSUPPORTED_ON_CONTINUITY_DISPATCH` — grep-confirmed
   absent from the file and every test.

**Test results:** targeted files 59/60 passed (2 new + 57 prior); the
one failure is the same pre-existing, unrelated scene-freeze test
already confirmed via `git stash` to predate any of this session's
changes. Additionally ran every other test file in the repo that calls
`process_once()` (presence-authority integration/supervision, stage8
runtime-composition/persistent-worker): 21/21 passed, no regressions.

**Known, stated limitation, not one of the five conditions**: the
resulting narrative response from a coordination-only dispatch is
absorbed into EngAIn's own Ledger (visible to a future real turn's
recap) but is not surfaced to the player directly — no in-game "the
dragon speaks" effect from this delivery yet. Also unresolved:
`handle_turn()`'s step 2 still unconditionally records this turn's empty
`player_input` as an `actor="player"` Ledger entry — a minor imprecision
in Ledger history for a turn no player initiated, left as-is since it's
an EngAIn-side Ledger-schema question outside this ticket's scope.

**Known gap (closure note, user-added)**: the dispatch reply from the
report-only path is not captured by the dragon3d worker itself —
`_process_pending_coordination_report_without_player_turn()` calls
`_dispatch_via_engain_continuity()` and checks only for success/failure,
never binding or logging the returned `engain_result`. This receipt does
not currently specify whether that reply should be persisted (e.g.
logged locally, or surfaced some other way) or is fine to discard
locally as it is now — that decision is open, not made here.

## Follow-up: surfacing [TOOL]/[DRAGON] in the live HUD, then correcting the text

Before the live restart, the "known gap" above (reply not captured) was
closed: `AdapterConfig.tool_events_dir` + `_publish_tool_event()` (dragon3d)
write small display-only events; `EngAInBridge3D.gd` polls them and
re-emits through the existing `log_line` signal; `ControlHUD.gd` renders
`kind="tool"` as `[TOOL]`. Deliberately NOT routed through `response.json`
— `_validate_correlated_response()` requires an active player-initiated
lifecycle that a coordination-only delivery never has.

**Live-test review caught a real defect before restart**: the first
version's `[TOOL]` text was a canned `"Proposal complete — <summary>"` /
`"Proposal failed — <summary>"` string — exactly the generic status
language this project's own honesty conventions reject. Fixed with
`_format_tool_completion_text(coordination_report)`, a pure function
built entirely from real report fields (request id via
`parent_message_id`, real changed-file basenames, real
`validation_result.status`, DONE/FAILED from the report's own `status`,
first real error message on failure) — no canned strings. 2 new pure
unit tests plus corrected assertions on the 2 existing end-to-end
tool-event tests (exact text, not `startswith()`).

Also caught and fixed in the same pass: a real filename-ordering bug —
`_publish_tool_event()` used second-resolution `strftime` timestamps,
and a "tool" event followed by its "dragon" reaction routinely publish
within the same wall-clock second, so they could sort out of order in
both a test and the actual live HUD. Fixed to zero-padded
`time.time_ns()`. Caught by a real, reproducible test failure, not
reasoned about in the abstract.

**Git-state correction**: a claim that "push ended at 27a5113" was
checked directly (`git log`, `git status`, `git show --stat`) —
`27a5113 "reload"` is the user's own commit on top of this session's
`ebd6137`/`dda1057`/etc., capturing their saved `Main.tscn`/
`FirstLightTower.tscn` scene edits plus two new snapshot captures.
Working tree clean; nothing was pushed to `origin` by this session at
any point.

**Live restart, still pending as of this writing**: `ENGAIN_CONTINUITY_DISPATCH=1
ENGAIN_CONTINUITY_SHARED_SESSION_ID=dragon3d_main ./launch_dragon3d.sh`,
after saving editor state. Expected first observable effect: the
already-completed `first_light_tower_revision_02` report still sitting
in `coordination/inbox/` should flush automatically on the worker's
first poll, producing a real `[TOOL] Request dragonreq_...: DONE — ...`
line with no player input at all — the free proof-of-return-lane the
live test was designed to give before any new interactive turn.

## Closure

Ticket closed. The five held-open conditions are proven, not merely
asserted — in particular #4 (retry semantics: exactly one HTTP attempt
per poll, requeued at `attempt+1`, a second poll proving genuine
retryability) and the shared dispatch-claim ordering with the real
player-turn path (claim first, then claim the report, so a contended or
unreachable claim costs no retry attempt). The two stated follow-ups
above (in-game surfacing of a report-only reply, and the `actor="player"`
Ledger imprecision) are correctly out of this ticket's scope and remain
open questions for whenever they're picked up next.
