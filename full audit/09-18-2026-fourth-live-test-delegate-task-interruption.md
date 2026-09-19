# Fourth live test — Dragon→tool-layer delegation, both subagents interrupted

Diagnosis only, per instruction. No changes made to Dragon, doors,
broker behavior, or source files; nothing rerun.

## The exact turn

**Request** (`id=50204`, Hermes `state.db`, session `20260731_065008_63a62d`,
`2026-09-18 18:57:30.076`): chapter-001 (`001_the_ethereal_vigil.md`)
first-scene request, explicitly instructing Dragon not to inspect the
chapter or call doors itself and to route through "the tool layer."

## 1. What tool/subagent mechanism Dragon invoked

`delegate_task` — a native Hermes tool, not anything specific to this
project's doors. Dragon's own tool call (`id=50205`) invoked it once
with a `tasks` array of two entries, dispatched together as one
`background` batch under `delegation_id: "deleg_07f2763f"` (tool result,
`id=50206`). The tool's own returned contract states: *"2 subagents are
running in parallel in the background. You and the user can keep
working; they wait on each other and their consolidated results
re-enter the conversation as a single message once ALL of them finish.
Do not wait or poll — just continue."* It also names two live,
append-only transcript files, one per subagent:

```text
/home/mytruelove/.hermes/cache/delegation/live/deleg_07f2763f/task-0.log
/home/mytruelove/.hermes/cache/delegation/live/deleg_07f2763f/task-1.log
```

Both still exist and are the primary evidence for this report. Dragon's
own final visible message this turn (`id=50213`, `18:58:34.794`,
`finish_reason: stop`) is only its immediate acknowledgment that
delegation was dispatched — *"I've asked the tool layer to query the
source-evidence and identity/continuity authorities under your
constraints..."* — written **before** either subagent's own outcome was
known, exactly matching the tool's "don't wait, just continue" contract.
No consolidated subagent result ever arrived as a later message: `id=50213`
is the last row in this session, and no other session in the entire
`state.db` has any row in the relevant time window either. The two
`task-*.log` files are the only surviving record that these subagents
ran at all.

## 2. Exact request sent to subagent-0 (verbatim, from `id=50205`'s tool-call arguments and confirmed identically in `task-0.log`'s own kickoff line)

```text
Goal: Obtain source evidence for the FIRST scene of the supplied chapter
using only the existing EngAIn source-evidence authority door(s). Return
the exact commands/operations used and raw stdout/stderr/exit codes,
followed by a structured extraction ONLY if supported by those returned
door results: first-scene beginning/end, setting/location, physically
present characters, important objects/environment, actions/events, and
explicit source-established facts.

Context: Source path: /home/mytruelove/Downloads/obsidianburdenNov25/
book_01_book_of_genesis/001_the_ethereal_vigil.md. EngAIn root:
/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn. Avatar
integration repo: /mnt/data-drive/godot_engain_3d_avatar. HARD
CONSTRAINTS: Do NOT read, search, cat, grep, parse, stat for content, or
otherwise inspect the chapter file directly. Do NOT read Mettaext
stageroom/passroom artifacts directly. Obtain chapter evidence only by
invoking the established EngAIn/Mettaext door interface. You may inspect
the door implementation/help to learn its contract. EngAIn is an
immutable read-only donor: do not invoke ingest or any operation that
writes into EngAIn. If status/query says un-ingested, unknown,
unsupported, bad data, or errors, preserve and report that result
exactly; do not repair, bypass, or fall back to direct source
inspection. Do not invent unsupported scene details. Return a compact
evidence ledger suitable for the parent to quote.
```

## 3. Exact request sent to subagent-1 (verbatim, same sources)

```text
Goal: Obtain prior identity/continuity records relevant to the
characters in the FIRST scene of the supplied chapter through existing
EngAIn/MrLore authority door(s), without reading the chapter or
generated source artifacts directly. Return exact calls and raw
results/errors, clearly separated from source evidence.

Context: Source path for identification context only:
/home/mytruelove/Downloads/obsidianburdenNov25/book_01_book_of_genesis/
001_the_ethereal_vigil.md. EngAIn root: /home/mytruelove/Desktop/
burdens_of_a_forgotten_past/EngAIn. Avatar repo:
/mnt/data-drive/godot_engain_3d_avatar. MrLore checkout may exist at
/home/mytruelove/Downloads/_mrlore. HARD CONSTRAINTS: Do NOT
inspect/read/search the chapter file directly. Do NOT inspect Mettaext
stageroom/passroom artifacts directly. First use the source authority
door only as needed to discover the first-scene character names; then
call the structured MrLore/identity authority door if it exists. Do not
disguise a human-readable registry CLI as a structured authority door.
If the MrLore door is absent or returns an error, preserve that failure
exactly. EngAIn and source are read-only: perform no ingestion,
promotion, or writes. Do not invent continuity. Return exact
operation/command, stdout/stderr, exit code, and a concise ledger of
what is established versus unresolved.
```

Both prompts are well-formed and correctly encode every constraint the
user gave Dragon. This is not where anything went wrong.

## 4. Which API call each subagent was attempting when interrupted

Neither subagent ever reached the door-invocation step. Full transcripts:

**subagent-0** (source-evidence):
```text
18:58:27  kickoff received
18:58:28  start
18:58:34  tool  -> todo(planning 3 task(s))
18:58:34  result: todo ok 0.0s — plan created: discover door / invoke door / extract ledger
18:58:35  final: status=interrupted duration=6.77s
          summary: "Operation interrupted: waiting for model response (0.3s elapsed)."
18:58:35  final: end status=interrupted exit_reason=interrupted
```

**subagent-1** (identity/continuity):
```text
18:58:27  kickoff received
18:58:28  start
18:58:33  tool  -> skill_view(github:codebase-inspection)
18:58:33  result: returned a generic "Inspect codebases w/ pygount: LOC,
          languages, ratios" skill document — unrelated to any EngAIn/
          Mettaext/MrLore door; not a door invocation of any kind.
18:58:35  final: status=interrupted duration=6.77s
          summary: "Operation interrupted: waiting for model response (1.9s elapsed)."
18:58:35  final: end status=interrupted exit_reason=interrupted
```

Both were interrupted while waiting on their **next underlying
model-completion API call** — i.e., after their first tool call
returned, waiting for the LLM to decide its next action. Neither had
issued, nor was in the middle of, any door/terminal call at the moment
of interruption.

## 5. Whether either subagent reached Mettaext or MrLore

**No, neither did.** subagent-0 got only as far as writing its own todo
plan (never executed the "invoke door" step it had just planned).
subagent-1 called an unrelated, generic codebase-metrics skill
(`skill_view(github:codebase-inspection)`) instead of anything
resembling `engain_door.py`'s help/contract or `mrlore_query.py` — this
looks like a wrong/stray tool selection on subagent-1's part while
trying to "inspect the door implementation... to learn its contract"
per its own instructions, not evidence of it reaching or attempting the
real MrLore interface. No `terminal`, `read_file` against
`engain_door.py`/`mrlore_query.py`/`mrlore_door.py`, or any other
door-shaped call appears in either transcript.

## 6. What actually caused the interruption

**Identical `duration=6.77s` for both subagents, both ending at the same
wall-clock second (`18:58:35`), despite starting their respective
model-response waits at different offsets (0.3s vs 1.9s in) — this is
not a coincidence of two independent per-subagent timeouts landing on
the same value.** 6.77 seconds is far too short to be either
`MAX_HERMES_TIMEOUT_SECONDS` (180s pre-fix / 240s post-fix) or the
GDScript mailbox watchdog (~270s) — this is not that mechanism.

The much stronger correlation: Dragon's own parent-turn final message
(`id=50213`) was written at `18:58:34.794` — **doing the arithmetic,
`18:58:28` (subagent start) + `6.77s` = `18:58:34.77`, within roughly
20 milliseconds of the parent's own completion timestamp.** Both
subagents were cut off at essentially the exact instant the parent
turn's own visible response was finalized.

Read against the delegate_task tool's own documented contract ("2
subagents are running in parallel in the background... their
consolidated results re-enter the conversation... once ALL of them
finish" — implying they are meant to keep running past the parent's own
turn), the best-supported explanation from the available evidence is
**parent turn completion / session lifecycle**, not a timeout,
cancellation request, unavailable tool, or malformed request: these
subagents appear to be hosted as in-process, async tasks inside the
same underlying `hermes` CLI invocation that produced the parent's
turn, and neither of them has its own row anywhere in `state.db` under
any session id — their only surviving trace is the two "live" transcript
files, consistent with being ephemeral, in-process constructs rather
than independent CLI subprocess sessions. When the hosting process's own
top-level turn reached a natural stopping point and (per
`hermes_session_adapter.py`'s `_run_bounded()`, which waits for the
whole subprocess to exit) the process appears to have torn down, any
subagents still mid-flight inside it were interrupted with it — even
though "background" was supposed to mean independent of the parent
turn's own completion.

**This is inference from timing correlation and file-level evidence,
not a confirmed root cause** — `hermes` is a closed CLI at
`/home/mytruelove/.local/bin/hermes`, not part of either
`engain-avatar-audit` or `godot_engain_3d_avatar`, so its own
process/async-task lifecycle code is not available to inspect from this
side. Stated as the best-supported hypothesis given what's observable,
not as something directly verified in source.

## 7. Whether any partial authority result exists in logs/receipts

No. `/home/mytruelove/.hermes/cache/delegation/` contains many historical
`subagent-summary-N-<timestamp>.txt` receipt files from past delegations
going back to July, but **none exists for `deleg_07f2763f`** — only the
two raw "live" transcripts, which is exactly what the tool's own
contract predicts for a delegation that never reached completion (the
summary file is written when a subagent finishes; an interrupted one
never gets there). Neither transcript contains any door output, partial
or otherwise, to preserve.

## Preserved distinction, as instructed

```text
Dragon routing/delegation:     PASS
  - Correctly refused to inspect the chapter or call doors directly
  - Correctly formed two well-scoped, constraint-complete delegate_task
    prompts matching exactly what the user asked for
  - Correctly did not wait/poll, per the tool's own contract
  - Correctly reported delegation as dispatched, not as an answer

Tool-layer authority execution:  FAILED / interrupted
  - Both subagents cut off before reaching any door
  - Best-supported cause: parent-turn completion tearing down subagents
    hosted in the same process, contradicting delegate_task's own
    "keeps running in the background" contract
  - Not caused by Mettaext, MrLore, engain_door.py, or mrlore_door.py --
    none of them were ever reached
```

## What was not done, per instruction

Nothing was fixed or rerun. No change to Dragon, any door, the broker,
`delegate_task`, or the Hermes CLI itself. This is a read-only trace of
exactly the one turn described.
