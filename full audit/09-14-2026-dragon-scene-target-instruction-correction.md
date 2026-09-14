# Dragon's persistent world-content scene-target instruction corrected

## What this closes

The loose end flagged in `09-13-2026-main-worldcomposition-ownership-split.md`:
"Dragon's own operating instructions still say 'Instance ... into
`res://scenes/Main.tscn`.'" That phrasing lived in the accumulated
conversation history of the real, resumed Hermes Editor session — not
in this repo, not in any config file, not in `~/.hermes/memories/MEMORY.md`
or a project `AGENTS.md` (checked; none exists for this project) — so
the fix is a direct chat correction into that same session, exactly the
mechanism the prior receipt named, not a code change.

## Scope, as instructed

- Smallest change necessary: one instruction correction, no code touched,
  no scene files touched, no edit/delete/move reconciliation design
  started.
- Responsibility boundary preserved exactly as specified: Hermes mutates
  and saves the requested scene file(s) itself and reports the exact
  changed paths and any blockers; the outer bridge (existing
  `run_coordination_validation()`) does validation; no runtime/reload/
  viewport/GUI validation ask was added inside `[EDITOR_REQUEST]`.

## How the correction actually reached Dragon

Not a new mechanism — the exact same invocation shape
`hermes_bridge.gd`'s `build_wrapper_script()` already produces for every
real dock turn:

```
cd /mnt/data-drive/godot_engain_3d_avatar
hermes chat -Q --source tool --pass-session-id \
  --resume 20260731_065008_63a62d \
  -q "<message>"
```

`20260731_065008_63a62d` is the live session_id currently recorded in
`.godot/engain_hermes_session.json` (companion_ref `hermes_b`), the same
one the Editor dock resumes on every turn — confirmed by its mtime
(2026-09-13 23:15, i.e. during the hotload proof session) and by the
CLI's own `↻ Resumed session 20260731_065008_63a62d (55 user messages,
110 total messages)` banner on the call below, which matched the file
before either correction turn.

Two turns were sent, cwd = the project root, no model/provider override
(so the session's own existing model stays in force):

1. The standing correction itself — states the new WorldComposition.tscn
   boundary, explicitly supersedes any earlier Main.tscn instruction,
   states it applies "to this turn and every future turn in this
   session, regardless of what was said earlier" (same persistence
   framing this project's own `build_safe_mode_preamble()` already uses
   for its analogous claim), restates the responsibility boundary
   verbatim, and asks for a one-sentence confirmation.
2. A separate, differently-worded follow-up query in the same session,
   sent after the first turn completed, asking Dragon to restate the
   rule in its own words — a check for independent recall, not an echo
   of turn 1's exact wording.

## Independent verification — read from Hermes's own persisted session store, not the CLI's own summary

The CLI's own `-Q` final line was unhelpfully terse for both turns
(`No tool call is required: the standing correction was recorded...` /
`No action or tool call is required; the requested restatement is
complete.`) — see "Reporting artifact" below for why. Verification
instead came from querying `~/.hermes/state.db` directly for this
session's actual message rows:

**Turn 1's real assistant reply (id 49603):**
> I will instance normal world-content only into
> res://scenes/WorldComposition.tscn, mutate and save the requested
> scene files while reporting exact changed paths and blockers, and will
> not modify res://scenes/Main.tscn or perform runtime, reload,
> viewport, GUI, or other validation myself.

**Turn 2's real assistant reply (id 49607), independently phrased, sent
after turn 1 had already completed:**
> I will instance normal world-content only into
> `res://scenes/WorldComposition.tscn`, never
> `res://scenes/Main.tscn`. I will mutate and save the requested project
> files and report exact changed paths or blockers, but I will not
> perform runtime, reload, viewport, GUI, or visual validation; the
> outer layer handles those checks.

Both replies name the correct target file, the correct exclusion, and
the correct validation boundary, independently derived twice rather than
a single echoed sentence — this is the evidence that the correction is
now part of the session's effective, standing instructions, not a
one-off acknowledgment.

## Reporting artifact (not a defect in the correction itself)

Both real answers above (49603, 49607) were immediately followed in the
transcript by an auto-injected `[System: Continue now. Execute the
required tool calls and only send your final answer after completing
the task.]` message from Hermes's own agent loop, and Dragon's reply to
*that* nudge (`No tool call is required...` / `No action or tool call is
required...`) is what `hermes chat -Q`'s "only the final response" mode
actually printed to stdout — because it genuinely is the last message in
the turn. The substantive content was real and correctly recorded either
way; it just wasn't the line `-Q` surfaces when a turn ends in a
no-op continuation exchange. Worth knowing for any future scripted
verification against this session: check `~/.hermes/state.db` directly,
don't trust `-Q`'s tail line alone, when a turn asks Dragon a question
rather than a mutation.

## What this does not do

- Does not touch `RuntimeSceneSync3D.gd`, `Main.tscn`, or
  `WorldComposition.tscn`.
- Does not begin edit/delete/move reconciliation design (explicitly
  deferred, per instruction).
- Does not re-run a live probe to confirm Dragon's *next real*
  `[EDITOR_REQUEST]` actually targets `WorldComposition.tscn` in
  practice — this receipt closes the instruction correction and its
  in-session verification only. The next live world-content probe is
  the natural place that gets exercised for real.

## Status

Local chat correction only; no repository files were modified. This
receipt is the only new file, committed to the audit repo, not pushed.
