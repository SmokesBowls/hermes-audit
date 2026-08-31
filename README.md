# Godot 3D Avatar — Progress

Session close: 2026-08-31

Not yet committed. Everything below is real, verified working-tree state in
`/mnt/data-drive/godot_engain_3d_avatar` (last commit `244fa9b revrt button`,
predates all four builds described here) — commit only on explicit
instruction, per this project's own standing discipline.

## Current gate

Phase 1C-1 — the Dragon ↔ Editor structured coordination report contract —
is implemented and verified. Four bounded builds this session, each proven
live or by real executed test before the next began:

1. Mechanical per-edit revert (edit receipts)
2. `.godot` exclusion fix (fingerprint/receipt boundary correction)
3. Phase 1 — sideband coordination lane (Dragon → Editor → Dragon message routing)
4. Phase 1C-1 — structured `engain.editor_report.v1` contract + headless validation

Implemented in exactly:

- `addons/hermes_editor/edit_receipt_store.gd` (new)
- `addons/hermes_editor/coordination_report_validator.gd` (new)
- `addons/hermes_editor/hermes_bridge.gd`
- `addons/hermes_editor/hermes_dock.gd`
- `addons/hermes_editor/test_hermes_bridge_logic.gd`
- `hermes_session_adapter.py`
- `tests/test_hermes_session_adapter.py`

## Proven implementation

### 1. Mechanical per-edit revert

Every `DIRECT_WRITE` turn that touches the live tree gets a one-time
`[Revert this edit]` button in the dock. No LLM involvement in the revert
path — pure filesystem mechanics: before-bytes snapshotted under Godot's
`user://` (structurally outside the fingerprint boundary, not by an
exclusion rule), verify-all-then-commit-all against the recorded AFTER
state, swap-based transactional apply with rollback on partial failure.
Refuses mechanically (touches nothing) if a later edit touched any covered
path. See `edit_receipt_store.gd`'s own top-of-file doc for the full
verify → prepare → commit → rollback shape.

### 2. `.godot` exclusion fix

A real receipt from Pass 4 exposed `.godot/editor/filesystem_cache10` —
Godot's own editor housekeeping, not anything Hermes or the user did —
riding along in a fingerprint diff. Excluded now, same rationale and same
list shape as the existing `.git` exclusion, in both
`hermes_bridge.gd`'s `_FINGERPRINT_EXCLUDED_DIR_NAMES` and
`edit_receipt_store.gd`'s `_EXCLUDED_DIR_NAMES`. Without this, a
perfectly legitimate AVAILABLE receipt could get refused later purely from
ordinary editor activity, not from anything the user or Dragon changed.

### 3. Phase 1 — sideband coordination lane

Dragon's frozen `REQUEST_SCHEMA`/`RESPONSE_SCHEMA` and its
`OBSERVATION`/empty-`state_changes`/zero-`entropy_impact` invariants are
completely untouched. Coordination travels as a separate labeled prompt
section instead:

```text
pending_perception      -> <CURRENT_RUNTIME_PERCEPTION>   (pre-existing)
pending_coordination    -> <COORDINATION_REPORT>          (new, same pattern)
```

- **Editor → Dragon**: `coordination/inbox/` → adapter claims atomically →
  labeled, provenance-tagged, base64 context on the director's next turn.
  3-attempt retry cap, immutable payload, attempt tracked in the filename
  (`editor_report.<id>.attemptN.json`), routes to `coordination/failed/`
  after the third failure — never replayed indefinitely.
- **Dragon → Editor**: a `[EDITOR_REQUEST]...[/EDITOR_REQUEST]` block
  inside `narrative_response`, extracted *after* `_sanitize_response()`
  already produced a valid response (never changes what Godot's own
  `_validate_correlated_response` accepts), published to
  `coordination/outbox/`. Directive-only turns fall back to the fixed
  acknowledgement `"Editor request sent."` rather than ever leaving the
  narrative empty or leaking transport markup into what Dragon says.
  Dragon's director system prompt (`LocalObservationDirector.build_messages`)
  now explains this convention — without it, a real model would never
  spontaneously produce that exact bracket syntax.
- **Editor execution**: human-confirm only, deliberately, for this first
  proof. `[Execute (DIRECT_WRITE)]` in the dock; mode is a caller-supplied
  argument the dock hardcodes — a Dragon request can never select or
  escalate its own authority mode. Reusable
  `_process_dragon_coordination_request(request, path, mode)` — a future
  auto-run path calls exactly this same function with no human click in
  between. Row-level feedback (`⏳ WORKING — ...` / `Running...`) added
  after the first live proof showed a merely-disabled button was too easy
  to miss under the runtime debug window.
- Continuity-dispatch conflict handled explicitly:
  `ENGAIN_CONTINUITY_DISPATCH=1` + a pending coordination report refuses
  with `COORDINATION_CONTEXT_UNSUPPORTED_ON_CONTINUITY_DISPATCH` (that
  path bypasses the prompt-formatting seam entirely) rather than silently
  dropping the report.

### 4. Phase 1C-1 — structured report contract

`engain.editor_report.v1` carries facts as fields now, not prose Dragon
has to re-parse:

```text
status                                  "applied" | "failed"
files_created / files_modified / files_deleted     res:// paths
execution_summary                       deterministic fact string
errors / warnings                       structured lists
validation_result                       real, mechanical, disk-level
runtime_result                          {"status": "not_checked"} — honest placeholder
body                                    human-readable summary ONLY
```

`validation_result` is produced by a genuinely separate headless Godot
process (`coordination_report_validator.gd`) — `.gd` files reloaded via a
fresh `GDScript` instance (trusting the real `Error` return, not `load()`'s
return value — see the bug note below), `.tscn` files loaded as
`PackedScene` and actually instantiated, then freed. Deliberately distinct
from `runtime_result`: disk-level parse/load proof is not proof the
composed runtime actually started or behaved correctly, and the report
never claims otherwise.

**A real bug caught before shipping**: the first validator implementation
used plain `load(path)` for scripts. Tested against a deliberately broken
`.gd` file first — Godot printed a real parse error to console, but
`load()` still returned a non-null `GDScript` that passed an `is GDScript`
check, so the check reported "passed" on a file that doesn't parse.
Rewrote to read source directly and trust `GDScript.reload()`'s actual
`Error` return; re-verified against broken/working scripts and a missing
scene, all cases now correct.

## Live proof

The full loop ran for real during this session, not only in tests:

```text
Dragon (real turn, real model) proposed a landmark tower
  → [EDITOR_REQUEST] extracted, published to outbox
  → human clicked Execute (DIRECT_WRITE)
  → real edit landed: scenes/FirstLightTower.tscn (+ script, + test),
    scenes/Main.tscn modified — receipt 20260830_203753_73d1
  → structured engain.editor_report.v1 written to inbox
  → claimed and consumed by a real Dragon turn (confirmed independently:
    the report moved inbox/ → consumed/ between two checks, with no
    action from this session in between)
```

That is the transport half of the Phase 1C loop closed for real. Dragon
has not yet been taught to *evaluate* what it received (see TODO below) —
this proved delivery, not comprehension.

## Evidence

```text
GDScript suite (test_hermes_bridge_logic.gd):     71 real assertions, ALL CHECKS PASSED
                                                    (includes a real headless validator
                                                    spawn against real project files)
Python suite (tests/test_hermes_session_adapter.py): 47 passed, 1 pre-existing failure
                                                    (test_current_scene_bytes_freeze_...
                                                    — confirmed via git stash to fail
                                                    identically with none of this
                                                    session's changes present; unrelated
                                                    scene-content drift from earlier work)
godot --headless --check-only:                     exit 0 on every touched .gd file
python3 -m py_compile hermes_session_adapter.py:   clean
```

No live editor/runtime process was ever left disturbed by any verification
step this session — checked before and after each headless spawn.

## Continuation TODO — next steps for future development

Settled sequencing (do not reorder without re-deciding deliberately — the
whole point was not letting the report schema depend on whichever autonomy
mode got built first):

1. **Phase 1C-2 — Dragon evaluation.** Teach the director to read a
   `<COORDINATION_REPORT>` and respond with one of:
   - `FIX` — result exists, something about it should be corrected
   - `NEXT` — result acceptable, propose the next useful construction
   - `NO_ACTION` — objective needs no further edit

   Introduce `[EDITOR_PROPOSAL]...[/EDITOR_PROPOSAL]` as an explicitly
   **inert** tag — never enters the outbox, never executes, just carries
   Dragon's current design thought forward in conversation. Critically:
   spontaneous FIX/NEXT evaluation must use `[EDITOR_PROPOSAL]`, never
   `[EDITOR_REQUEST]` — the latter already means "route through Editor
   now," and blurring the two destroys the conversational approval
   boundary.

2. **Mode 1 — Conversational World Building.** Human talks with Dragon;
   Dragon evaluates reports and proposes via `[EDITOR_PROPOSAL]`; Dragon
   *stops* after proposing. Only an explicit human "send it through"
   converts the current proposal into a real `[EDITOR_REQUEST]`.

3. **Mode 2 — Continuous World Building.** Same evaluation machinery as
   Mode 1, different authorization: `[EDITOR_PROPOSAL]` becomes
   `[EDITOR_REQUEST]` automatically inside a bounded loop. Explicit stop
   conditions required from day one, not added later: objective
   satisfied, `NO_ACTION`, human pause/redirect/cancel, editor report
   requiring a human decision, safety/authority boundary refusal,
   iteration/budget limit reached.

4. **`runtime_result`.** Currently an honest `{"status": "not_checked"}`
   placeholder. Real content requires an actual
   write → load-from-disk → restart-composed-runtime → health-check
   pipeline — not yet built, not to be faked by relabeling
   `validation_result`.

5. **Auto-run authorization.** `_process_dragon_coordination_request()`
   is already written to be reusable without a human click — Mode 2 is
   the natural point to actually call it that way. Until then it stays
   human-confirm only, unconditionally.

Smaller open items, lower priority, not blocking the above:

- **CASE 2** (the Aug 23 SIGSEGV cluster during the original direct-write
  maturity experiment) remains decoupled and unexplained. Its coredump
  has since rotated out of `/var/lib/systemd/coredump/` — reproduction
  would be required if this is ever pursued.
- `ENGAIN_AVATAR_DRAGON_BRIDGE_CONTRACT_v1.md` (in the EngAIn checkout,
  `docs/contracts/SUPPORT_LANE_DISTRIBUTION/engain_avatar_4thlane_dragon_bridge/`)
  is stale for this 3D body specifically — it describes the 2D avatar's
  file-polling handshake through an Ollama/Dolphin director, predating
  the tier system and this body's real `EngAInBridge3D.gd` mechanics.
  Worth a real rewrite once the 3D message contract is mature enough to
  formalize; its Amendment 1 (shared-session continuity) is current and
  should be preserved.
- Standing sequencing rule, reaffirmed, not yet due: do not hook EngAIn's
  own tier1/tier2 coordination/authority layer into this Dragon↔Editor
  pair until the pair has proven itself as a stable two-system team on
  its own (Phase 1C-2 through Mode 2, above). EngAIn's own migration
  (tier authority map, Trixel 3.2d as an external peer, Cartographer/
  Topologist, the proposed Mettaext bridge) continues independently and
  is documented separately in the EngAIn checkout's own
  `docs/Canonical authority map — current local checkout august 30 2026.md`.

## History

### Stage 7 (closed 2026-08-10)

Live current-perception production code, implemented in exactly:

- `scripts/PerceptionCapture3D.gd`
- `scripts/EngAInBridge3D.gd`
- `scripts/ControlHUD.gd`
- `hermes_session_adapter.py`

The frozen Stage 7 gate was GREEN at the application-contract level:

- protected Stage 4–7 tests: `178 passed`
- Godot 4.6.1 headless editor parse: exit `0`
- Python compilation: passed
- `git diff --check`: passed
- final independent Amendment 5 review: `PASS`
- provider executions during Stage 7 RED/GREEN: `0`
- live HUD submissions during Stage 7 RED/GREEN: `0`

Frozen Stage 7 tests (unchanged since):

```text
7d4387695af71ac937742266f185a68b2b82e695d34943b8764801b2eb14ea66
tests/test_stage7_live_perception_capture.py

28f06f4e7db140964b8dfa19bc3587e15c20c2ba3c4d0a48c550e8579d355aec
tests/test_stage7_live_perception_adapter.py
```

Proven at the time:

- The capture producer accepts the bridge-owned `client_request_id`, owns
  `capture_id`, records `captured_at` before fallible work, and reuses the
  Stage 5A PNG/JSON persistence and hashing path.
- The bridge reserves capture state before its first await, suppresses
  response polling during capture, publishes exactly once, and emits
  `submission_committed` only after publication.
- The HUD clears unchanged submitted text only after the correlated
  commit and preserves newer or unrelated text.
- Full adapter requests pass through `prepare_image_dispatch` before the
  director/provider boundary. The admitted argv, image path, and SHA-256
  are retained one-shot; `chat()` executes the admitted argv and rehashes
  the image immediately before `_run_bounded`.
- Unavailable perception does not prepare or attach an image.

Two architecture questions were left open at Stage 7 close and were never
revisited before this session's work superseded that closure boundary:

1. A bridge timeout invalidates late publication, but Godot cannot cancel
   the already-running capture coroutine — a replacement lifecycle could
   overlap producer work unless a producer-level lock or cancellation
   contract is added.
2. The frozen pathname-based `--image` interface proves the admitted
   command/path/pre-launch hash under application-level immutable-evidence
   rules, but cannot exclude a hostile same-user pathname replacement
   between the last hash and Hermes opening the file.

Neither has been acted on since; they remain open if Stage 7's own
perception path is revisited.

### Audit authorities and evidence (Stage 7 era)

- `ENGAV3D-0001-IDENTITY-MAILBOX-PERCEPTION-FREEZE.md`
- `ENGAV3D-0001-AMENDMENT-1-STAGE5B-PREPARATION-BOUNDARY.md`
- `ENGAV3D-0001-AMENDMENT-5-STAGE7-LIVE-PERCEPTION-LIFECYCLE.md`
- `ENGAV3D-0012-STAGE7-LIVE-PERCEPTION-RED.log`
- `ENGAV3D-0012-STAGE7-LIVE-PERCEPTION-TESTS.sha256`

### Pass 1–4, Phase 1, Phase 1C-1 (2026-08-28 through 2026-08-31)

No numbered `ENGAV3D-*` authority documents were produced for this
session's work — tracked instead through this file and the live
conversation record. If this project returns to the numbered-authority
convention, Pass 1–4 (direct-write maturity ladder), Phase 1 (sideband
coordination lane), and Phase 1C-1 (structured report contract) are the
three closure boundaries that would need their own formal documents.
