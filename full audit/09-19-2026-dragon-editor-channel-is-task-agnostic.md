# The Dragon↔Editor coordination channel already exists and is task-agnostic

Read-only architecture trace, per instruction: identify the mechanism
Dragon already uses for a known-successful artifact request (the
"Dragon Sight" F1-rig build), and determine whether that same channel
can carry a read-only investigative request instead. `delegate_task`
was explicitly excluded from this trace (see the separate, parked
finding in `85a54b5`/`d0366b7` receipts). Nothing changed. Nothing rerun.

## Grounding example

Real, observed instance in Hermes `state.db`, session
`20260731_065008_63a62d`:

- `id=50046` (assistant): Dragon's narrative response contains a
  `[EDITOR_REQUEST]...[/EDITOR_REQUEST]` block with a full natural-
  language build spec (create `DragonSightRig13.tscn`, wire an F1
  toggle, etc.) — otherwise ordinary spoken text around it ("Let's give
  the dragon a second pair of eyes.").
- `id=50047` (user, but not player-authored — injected):
  *"EngAIn's Editor has a coordination report for you (not something
  the player said): status: applied, summary: Created 2 file(s),
  modified 1 file(s), deleted 0 file(s)."*
- `id=50048` (assistant): Dragon continues the conversation using that
  report, unprompted by the player in between.

## The verified mechanism, end to end

```text
Dragon
  |  emits a [EDITOR_REQUEST]...[/EDITOR_REQUEST] block inside its own
  |  ordinary spoken narrative_response -- no special tool call, no
  |  structured function, just plain text markup
  v
hermes_session_adapter.py: EDITOR_DIRECTIVE_PATTERN / _extract_editor_directive()
  |  regex-extracts the block AFTER the normal response is already
  |  built and validated; strips it from what the player hears
  v
_publish_dragon_directive() writes one engain.dragon_request.v1 JSON
file (message_id, parent_message_id=client_request_id, source:
"dragon3d", destination: "editor", body: <the free-text block content>,
created_at) into coordination_outbox_dir -- a shared filesystem
directory. Per the code's own comment: "the two Godot projects only
ever communicate through this filesystem seam" -- no direct call of
any kind into Editor code.
  v
addons/hermes_editor/hermes_bridge.gd (a Godot EDITOR PLUGIN, a
separate process from the player-facing runtime) independently polls
that same outbox directory (list_pending_dragon_requests()) and, for
each pending file, spawns its OWN fresh CLI session:
  `hermes chat -Q --source tool --pass-session-id ...`
No --profile/-p flag is passed -- unlike the player-facing "hermes_b"
companion session, which is pinned to the frozen "default" profile.
This Editor-side session gets Hermes's ordinary default tool surface:
terminal, file read/write, search, etc. -- the same general toolset
every other Hermes session on this machine has used throughout this
audit to call engain_door.py and mrlore_query.py via `terminal`.
  v
build_editor_report() packages whatever that session produced into one
engain.editor_report.v1 JSON file, written to coordination_inbox_dir.
  v
hermes_session_adapter.py's _read_coordination_report() picks it up on
Dragon's *next* turn and injects it as a synthetic "EngAIn's Editor has
a coordination report for you" user-role message -- Dragon continues
the conversation from there, not synchronously within the same turn.
```

## What Dragon emits

Nothing structural. A literal `[EDITOR_REQUEST]` / `[/EDITOR_REQUEST]`
text block inside its own ordinary spoken response. No tool call, no
special protocol.

## What component receives it

`hermes_session_adapter.py`'s `_extract_editor_directive()`, running
strictly after the player-facing response is already validated —
transport-side code, not Dragon-side.

## How the Tool session/process is started or addressed

Not addressed directly at all. `hermes_editor`'s Godot plugin polls the
shared outbox on its own schedule and, for each request, launches a
brand-new, unrestricted `hermes chat` session per request. There is no
persistent "Tool session" Dragon talks to — each dragon_request gets a
fresh Editor-side Hermes invocation.

## What request format the Tool receives

`engain.dragon_request.v1`: `schema`, `message_id`, `parent_message_id`,
`source`, `destination`, `body` (free text, verbatim from inside the
`[EDITOR_REQUEST]` block), `created_at`. Nothing in this envelope
distinguishes a build request from an investigative one — `body` is
opaque natural language either way.

## How Tool results return to Dragon

`engain.editor_report.v1`, written to `coordination_inbox_dir`, claimed
and injected as a synthetic message on Dragon's next turn. Structurally
this is exactly the same "task in, report out" shape a delegate_task
subagent uses — just filesystem-based instead of in-process, and
critically (see below) actually reaching the parent.

## What distinguishes build/edit requests from informational ones — the real finding

**Nothing on the request or transport side.** The gap is entirely on
the Editor's own report-construction step. Read `build_editor_report()`
in full (`addons/hermes_editor/hermes_bridge.gd:954-1050`):

```gdscript
var execution_summary := ""
if succeeded:
    execution_summary = "Created %d file(s), modified %d file(s), deleted %d file(s)." % [
        files_created.size(), files_modified.size(), files_deleted.size(),
    ]
...
var body := execution_summary
```

`edit_result.get("response", "")` — the Editor-side Hermes session's
actual free-text output — is read only by `extract_task_disposition()`
to classify completed vs. not-completed. **Its content is never copied
into the outgoing report.** `execution_summary` and `body` are both
hardcoded to a file-mutation-count template. For a genuinely read-only
request (zero files created/modified/deleted), this template still
fires and produces something like *"Created 0 file(s), modified 0
file(s), deleted 0 file(s)."* — a technically valid, correctly-
correlated report that discards whatever the Editor session actually
found before it ever reaches Dragon.

## Classification, as instructed

```text
Dragon->Tool task handoff:            WORKING
  (plain-text EDITOR_REQUEST block -> dragon_request.v1 file; verified
  against a real historical example)

Tool task format:                     TASK-AGNOSTIC
  (body is opaque free text; nothing marks build vs. informational)

Tool authority access:                AVAILABLE
  (Editor-side hermes chat session runs with no profile restriction --
  the same general tool surface, including terminal, that every other
  session on this machine has used to call engain_door.py/mrlore_query.py)

Tool->Dragon result transport:        WORKING structurally
  (editor_report.v1 -> coordination_inbox_dir -> claimed and injected
  on Dragon's next turn; verified against the same real example)

Informational result preservation:    BROKEN
  (build_editor_report() only ever emits a hardcoded mutation-count
  sentence; the Editor session's actual free-text findings are read
  only for completion-disposition, never copied into the report)
```

## Root cause, stated narrowly

`build_editor_report()` was written assuming every dragon_request
results in a file mutation, and reduces the Editor's real response to
mutation counts plus a completed/not-completed disposition. It has no
field carrying the Editor's actual textual output for a request that
legitimately produces zero file changes.

## Explicitly not touched by this finding

`delegate_task` (separately parked, per `85a54b5`), Dragon's emission
format, the outbox/inbox filesystem transport itself, how the Editor's
Hermes session is started, and the EngAIn doors. This trace confirms
none of those need to change — the fix belongs entirely to the report-
building step described above.

## What was not done, per instruction

No code changed. Nothing rerun. The coordination architecture is
recorded exactly as found, not redesigned.
