# Fix plan: preserve informational Editor results (spec only)

Addresses exactly the one gap found in
`09-19-2026-dragon-editor-channel-is-task-agnostic.md` (`2d4da65`):
`build_editor_report()` discards the Editor-side Hermes session's real
free-text response, replacing it with a hardcoded mutation-count
template regardless of what kind of request was actually made. No code
in this repo has been changed to write this plan. Scope is held to
exactly the report-construction/validation step — nothing else.

## Explicitly out of scope (per instruction)

Dragon's `[EDITOR_REQUEST]` emission format, the outbox/inbox
filesystem transport itself, how `hermes_editor` starts its own
`hermes chat` session, and the EngAIn doors. `delegate_task` remains
separately parked (`85a54b5`). None of these are touched by this plan.

## The change, in one sentence

Add one new, always-present, nullable field to the
`engain.editor_report.v1` contract — `result_text` — populated with the
Editor session's actual free-text response whenever one exists, leaving
every existing mutation-report field and consumer untouched.

## Per-file change

### 1. `addons/hermes_editor/hermes_bridge.gd` — `build_editor_report()` (`:954-1050`)

**Current behavior:** `execution_summary`/`body` are built purely from
`files_created.size()`/`files_modified.size()`/`files_deleted.size()`
counts. `edit_result.get("response", "")` (the Editor session's actual
output) is read only by `extract_task_disposition()` to classify
completed vs. not-completed; its text is never placed anywhere in the
outgoing report dict.

**Proposed behavior:** add one line building a new field from the same
`edit_result.get("response", "")` value already in scope at this point
in the function, and include it in the returned dict:

```gdscript
var raw_response := String(edit_result.get("response", "")).strip_edges()
var result_text: Variant = raw_response if not raw_response.is_empty() else null
...
var report := {
    "schema": EDITOR_REPORT_SCHEMA_ID,
    ...
    "body": body,
    "result_text": result_text,
}
```

No change to `execution_summary`, `body`, `files_created/modified/deleted`,
`status`, or disposition logic — existing mutation-flow behavior is
byte-for-byte unchanged except for the one new key.

**Risk:** low. Purely additive; the existing fields and their
semantics are untouched.

### 2. `hermes_session_adapter.py` — `EDITOR_REPORT_KEYS` (`:133-...`)

**Current behavior:** a fixed `frozenset` of accepted keys, checked via
exact-match (`set(payload.keys()) != EDITOR_REPORT_KEYS`) in
`_read_coordination_report()`. Adding a key to the GDScript side alone,
without this change, would make every report — mutation or
informational — fail this check outright and be silently treated as
malformed (matches the same architectural pattern already fixed for
`RESPONSE_SCHEMA`/`call_id` in the prior timeout/correlation fix).

**Proposed behavior:** add `"result_text"` to the frozenset.

**Risk:** none on its own; must land in the same change as #1 and #3,
or every report of either kind starts failing validation.

### 3. `hermes_session_adapter.py` — `_read_coordination_report()` (`:1981-2023`)

**Current behavior:** type-checks every field explicitly (`body` must
be `str`, `execution_summary` must be `str`, list/dict fields checked,
etc.) — no wildcard/pass-through validation.

**Proposed behavior:** add one check alongside the existing `body`
check:

```python
result_text = payload.get("result_text")
if result_text is not None and not isinstance(result_text, str):
    return None
```

(`None`/absent-but-present-as-null is valid; any non-string, non-null
value is rejected, matching the strict-typing convention already used
for every other field here.)

**Risk:** low. Same validation style already used for the other ten-odd
fields in this function.

### 4. `_format_messages()` (`:1294-1392`) — no change needed

Confirmed by reading the function: the entire validated report dict
(`self.pending_coordination`) is serialized to JSON and base64-encoded
into the `<COORDINATION_REPORT>` block verbatim. Once `result_text`
survives validation, it automatically reaches Dragon's prompt with no
further wiring — this function does not enumerate fields individually.

## Test-fixture updates required (both sides use exact-key-set literals)

- `tests/test_hermes_session_adapter.py`'s `_write_editor_report()`
  helper (`:778`) builds a report dict against the *current* key set
  for its own fixtures; it needs the new key added (with a `None`
  default parameter) so existing tests using it keep constructing
  valid, exact-key-matching payloads.
- `addons/hermes_editor/test_hermes_bridge_logic.gd`'s existing
  `build_editor_report()`-based tests (`:539-691`) assert against
  specific fields (`execution_summary`, etc.) and don't currently
  assert an exact key count themselves — should still pass unmodified,
  but worth a read-through at implementation time to confirm none of
  them independently enumerate expected keys elsewhere in the file.

## Required regression tests

**GDScript side** (extending `test_hermes_bridge_logic.gd`'s existing
`build_editor_report()` coverage):

1. `informational_report_carries_editor_response_in_result_text` — call
   `build_editor_report()` with an `edit_result` that has
   `live_tree_changes` empty (zero created/modified/deleted) and a
   real, non-empty `response` string containing findings text; assert
   `result_text` equals that (stripped) text, `execution_summary` still
   reads "Created 0 file(s), modified 0 file(s), deleted 0 file(s).",
   and `status` is unaffected.
2. `mutation_report_result_text_is_null_when_response_is_empty` — the
   existing mutation-flow fixture pattern (files actually created),
   with an empty/whitespace-only `response`; assert `result_text` is
   `null`, and every existing assertion in the current mutation tests
   (`:574-691`) still passes unchanged.
3. `mutation_report_still_carries_result_text_when_response_nonempty` —
   a mutation flow where the Editor session's response also contained
   narrative text alongside making real file changes; assert
   `result_text` is populated AND `files_created`/`execution_summary`
   are unaffected — confirms the two fields are independent, not
   mutually exclusive.

**Python side** (extending `test_hermes_session_adapter.py`):

4. `test_coordination_report_with_result_text_is_claimed_and_read_back_intact`
   — mirrors the existing `test_coordination_report_is_claimed_and_read_back_intact`
   (`:809`) but with `result_text` set to a real string in the fixture;
   assert `_read_coordination_report()` returns it unchanged.
5. `test_coordination_report_null_result_text_is_accepted` — existing-
   shape mutation report with `result_text: null`; assert acceptance
   (no regression to the pre-existing, still-most-common report shape).
6. `test_coordination_report_non_string_result_text_is_rejected` —
   `result_text` set to a number/list/dict; assert
   `_read_coordination_report()` returns `None` (rejected), matching
   the strict-typing convention already enforced for every other field.
7. `test_format_messages_coordination_report_json_includes_result_text`
   — extends `test_format_messages_includes_labeled_coordination_report_when_pending`
   (`:934`) to decode the base64 payload embedded in the
   `<COORDINATION_REPORT>` block and assert `result_text` is present
   and matches the fixture value — confirms #4's claim about
   `_format_messages()` needing no direct change.

## Suggested validation after implementation

Once implemented, resend the exact scene-1 chapter-001 investigative
request already used in the fourth/fifth live tests (unchanged, for a
clean before/after) and confirm the resulting `editor_report`'s
`result_text` field actually carries Mettaext/MrLore door findings
through to Dragon's next turn. Not run as part of this plan — this
document stops at the proposal, per instruction.
