# 09-11-2026 — ChatGPT "avatar dragon" status relay, Phase 0

## Trigger

User shared a screenshot of the ChatGPT custom-GPT project "avatar dragon"
(browser tab, `chatgpt.com/g/.../avatar-dragon`), overlaid with a
`ControlHUD`/`engain_parser (DEBUG)` in-scene chat log. The in-character
`[DRAGON]` dialogue described wanting replies "tied to a request ID with
accepted/in-progress/completed/refused/failed status plus changed files,
validation, and any blocker," then, when asked how that should reach it
mechanically, described a "durable session mailbox" / `engain.editor_status.v1`
event / gateway-injects-into-context design.

## Two "Dragon" surfaces — kept distinct per explicit user instruction

- **A. dragon3d runtime Dragon** — `director_bridge.process_player_input()`
  in `godot_engain_3d_avatar`, backed by a real local `hermes` CLI
  subprocess call per turn (see `hermes_session_adapter.py`). This is a
  fully separate implementation from either the `engain_avatar` (2D)
  mailbox or the ChatGPT custom GPT.
- **B. ChatGPT custom-GPT "avatar dragon"** — the actual persona in the
  screenshot. Runs in the browser ChatGPT UI, not the API. This is the
  agent the user wants receiving editor status.

These are NOT the same agent and must not be treated as interchangeable —
user's explicit correction, recorded verbatim in this session.

## What was found already built (traced directly, not taken on claim)

Confirmed by reading `godot_engain_3d_avatar/hermes_session_adapter.py`
and `addons/hermes_editor/{hermes_bridge.gd,hermes_dock.gd}` line-by-line,
and by re-running the real headless test suite (all passing before any
change here):

```
runtime Dragon (director_bridge, Hermes-CLI-backed)
  -> narrative_response may contain [EDITOR_REQUEST]...[/EDITOR_REQUEST]
  -> _extract_editor_directive() (hermes_session_adapter.py:1874) strips it
  -> _publish_dragon_directive() writes engain.dragon_request.v1 to
     COORDINATION_OUTBOX_DIR, atomically, filesystem-only seam
  -> hermes_dock.gd polls the outbox every 1s, lists under "Pending Dragon
     requests (human-confirm, DIRECT_WRITE)"
  -> human clicks Execute -> runs the existing DIRECT_WRITE path (request
     body can never select/escalate its own authority mode)
  -> _on_turn_finished() calls write_editor_report() regardless of
     success/failure -> engain.editor_report.v1 written to
     COORDINATION_INBOX_DIR
  -> _claim_coordination_report() (hermes_session_adapter.py:1713) claims
     the oldest pending report OPPORTUNISTICALLY on the next real player
     turn — "no separate poll loop is needed" per its own comment. This is
     exactly why the screenshot's DRAGON could truthfully say "no report
     has reached me": nothing had triggered a new dragon3d turn yet.
```

Real executed tests already covering this, unchanged by this session's
work: `test_extract_editor_directive_publishes_and_strips_block`,
`test_coordination_report_is_claimed_and_read_back_intact`,
`test_coordination_report_moves_to_failed_after_max_attempts`, and the
`_check_coordination_lane()` end-to-end outbox/inbox round trip in
`test_hermes_bridge_logic.gd`.

**Correction to this session's own earlier statement**: an initial claim
that "nothing in any of the repos shows an existing automated channel"
was wrong for lane A — it had only checked `engain_avatar` (2D) and this
audit repo, not `godot_engain_3d_avatar`. User caught this by tracing the
actual code and named the exact functions; verified directly before
acting on it, per this project's own no-simulated-claims discipline.

**What is still NOT wired anywhere** (checked via repo-wide grep across
all four repos for `openapi|gpt action|custom gpt|ai-plugin|actions\.(json|yaml)|webhook|gateway`):
no code anywhere calls out to OpenAI, no Actions/OpenAPI config exists for
the "avatar dragon" custom GPT, no webhook receiver exists. Lane A and the
ChatGPT persona (lane B) are two structurally separate brains that have
never been connected.

## Decision (user, explicit)

Extend lane A's *reports* to reach the ChatGPT Dragon as an **additional
recipient**, without touching lane A's proven mechanics in any way. Do
**not** replace the local Hermes-CLI director with the ChatGPT GPT (that
would be a much larger, separate architecture change). Reverse direction
(ChatGPT Dragon -> Editor requests, user-authorized) is explicitly
deferred to a later, separate step once this return-awareness half is
proven.

Mechanism for this half: since no Action/webhook exists for the custom
GPT (browser-based custom GPTs have no push/webhook capability at all —
they can only call an Action during an active turn), and since every
existing step in this project's Editor lane is already human-confirmed,
the lowest-risk Phase 0 is a **human-relayed copy-paste handoff** of the
exact same verified report, not a new transport.

## Implementation (`godot_engain_3d_avatar`)

`addons/hermes_editor/hermes_bridge.gd`:
- Split `write_editor_report(dragon_request, edit_result) -> Error` into
  `build_editor_report(...) -> Dictionary` (pure) + a new
  `write_report_dict(report) -> Error` (pure I/O). `write_editor_report()`
  itself is unchanged in signature/behavior — it now just composes the
  two — so lane A and every existing test are untouched.
- Added `format_report_for_chatgpt_dragon(report: Dictionary) -> String`
  — a pure, read-only formatter over the exact same report dict lane A
  already produces. Field vocabulary mirrors what the ChatGPT persona
  itself proposed (`event_id`/`status`/`summary`/`changed_files`/
  `validation`/`blockers`) wherever this project has a real fact behind
  that name; fields it doesn't actually produce (`sequence`,
  `acknowledgments`, `replay_protection`) are deliberately NOT invented —
  those belong to a future real transport, not a formatter.

`addons/hermes_editor/hermes_dock.gd`:
- `_on_turn_finished()` now builds the report once (`build_editor_report`),
  writes it to the existing inbox (`write_report_dict`) — identical bytes
  to before — and additionally formats+appends the ChatGPT-relay block to
  the transcript. One computation feeds both consumers, so
  `run_coordination_validation()`'s real headless Godot spawn never runs
  twice per edit.
- Added a "Copy last report for ChatGPT Dragon" button
  (`DisplayServer.clipboard_set()`), disabled until a coordinated edit has
  actually produced a report. Tooltip states plainly that no automated
  channel to that conversation exists yet.

## Proof

Extended `addons/hermes_editor/test_hermes_bridge_logic.gd`'s existing
`_check_coordination_lane()` (real outbox/inbox round trip, real headless
validation spawn against real project files — not mocked) with:
- the ChatGPT-relay block is built from the *same* `report_payload` this
  test already read back off disk, and asserted to carry the identical
  `event_id`, `status`, `changed_files`, and `validation`/`blockers` facts;
- a second `build_editor_report()` call for a failed edit_result, asserting
  the relay block surfaces the real failure as a blocker rather than
  hiding it.

Ran `godot --headless -s addons/hermes_editor/test_hermes_bridge_logic.gd`:
**ALL CHECKS PASSED**, including every pre-existing assertion (coordination
lane, fingerprint safety regressions, wrapper-script injection tests) —
nothing in lane A regressed. Also `godot --headless --check-only --script
addons/hermes_editor/hermes_dock.gd` parses clean.

## What this does NOT prove / explicitly out of scope

- Does not prove the ChatGPT Dragon actually reads or understands a pasted
  block — that requires a human to actually paste one and observe the
  reply, not yet done this session.
- Does not build any Action/webhook/HTTP transport — deferred until/unless
  the manual relay proves insufficient, per the user's own instruction not
  to design a replacement transport prematurely.
- Does not touch the reverse direction (ChatGPT Dragon -> Editor,
  user-authorized) at all — that is the explicitly-deferred next step once
  this return-awareness half is proven in real use.

## Working discipline followed

Per this project's established rule: verified the existing-code claim by
reading the actual functions before acting on it (not accepted on
narrative alone), kept the two "Dragon" identities distinct per user
correction, additive-only change to a proven/tested lane, real executed
test added (not asserted-without-proof), receipt written same-day.
