# Seventh live test — result_text fix proven correct; live deployment gap found

Follows the sixth-test receipt (`4ff936f`). This time the request was
worded to name the mechanism directly: *"The same way you send the
Editor a build request, send the Editor a read-only request for this
task... Send this through the Editor Tool as an [EDITOR_REQUEST]."*

## Dragon emitted a correct, well-formed [EDITOR_REQUEST] this time

`id=50235`/`50236` (frozen session, `2026-09-19 05:52:15`–`05:52:29`,
`finish_reason: stop`). Dragon's entire response was the block itself:
a request ID, explicit read-only constraints (no build/edit/ingest/
mutate, no direct chapter inspection, no artifact bypass, no
Godot/runtime validation), and an explicit ask for exact door calls,
raw results, a structured findings section, and confirmation that zero
files changed. Naming the mechanism directly worked where "ask the
tool" (fifth/sixth tests) did not.

## The full chain ran, for real

```text
dragonreq_20260919_125230_a8cd163d.json   (outbox_handled/)
  parent_message_id: dragon3d_73cd53247c6c4f12ef59cffb356a4266_4
  body: <the exact EDITOR_REQUEST text above>

  -> Editor's own hermes chat session (resumed 20260918_184736_847694)
  -> engain_door.py status --source .../001_the_ethereal_vigil.md
       -> {"ok": true, "ingestion_status": "not_ingested", ...}
  -> engain_door.py query --source .../001_the_ethereal_vigil.md --query scene
       -> {"ok": false, "error": "INGEST_REQUIRED", ...}, exit code 1

editor_report.20260919_055321_c3de.attempt2.json   (failed/)
  status: "applied"
  execution_summary/body: "Created 0 file(s), modified 0 file(s), deleted 0 file(s)."
  result_text: <full findings, quoted below>
```

`result_text`, in full:

```text
Terminal status: BLOCKED
- status call: exit code 0
- query call: exit code 1
- No mutating operation was invoked.

[... exact commands, exact arguments, both raw JSON results ...]

Structured findings
1. First scene's returned scene ID: Unavailable (chapter_id: null, scene_count: null)
2-6. Unavailable (no scene evidence returned)
7. What the scene explicitly establishes: source path exists;
   ingestion_status is exactly "not_ingested"; no chapter ID; no scene
   count; the evidence query failed with "INGEST_REQUIRED".
8. All requested content fields were unavailable.

Mutation confirmation: Zero files were created, modified, or deleted.
I invoked only the read-only status and query door operations. I did
not invoke ingest or inspect the source chapter or Mettaext artifacts
directly.

Blocker: INGEST_REQUIRED -- Source has not been ingested. Call ingest
before query. Because ingestion and all other mutations were explicitly
prohibited, no complete first-scene answer could be obtained through
the established authority door.
```

**This is exactly the fix's target behavior.** An honest, complete,
zero-mutation investigation result, correctly distinguishing what the
authority returned from what it could not determine, preserved intact
in `result_text` — while `execution_summary`/`body` keep their exact
prior mutation-count meaning, unaffected.

## But it never reached Dragon — a live deployment gap, not a code bug

The report is sitting in `coordination/failed/`, not `consumed/`,
`attempt2` (the third and final try before `_dispose_coordination_report()`
gives up). Root cause, confirmed directly:

```text
runtime_composition.py (the persistent supervisor) process start: 2026-09-18 18:46:42
hermes_session_adapter.py on-disk fix (bc995d1) written:           2026-09-19 05:18:19
                                                    committed:      2026-09-19 05:18:45
```

The supervisor, and whatever persistent worker it launched, has been
running continuously since **before the fix existed on disk**. Python
does not hot-reload a running process's already-imported source — the
live adapter process is still executing the pre-fix `EDITOR_REPORT_KEYS`
(without `result_text`), so every report the Editor produced with the
new field failed `_read_coordination_report()`'s exact-key-set check,
was treated as malformed, retried twice, and filed to `failed/` after
the third attempt. The GDScript (`hermes_bridge.gd`) side clearly *did*
pick up the fix — it correctly built and sent `result_text` — because
Godot's editor plugin re-reads/re-executes that script per invocation,
unlike a long-lived Python process.

## Verified: 20/20 keys otherwise match exactly

Cross-checked the failed report's actual key set against the intended
(fixed) `EDITOR_REPORT_KEYS` frozenset — identical, 20 keys each,
`result_text` included. The report is fully valid under the *fixed*
code; it was only ever rejected because the running process hadn't
loaded that code yet.

## Conclusion

```text
result_text fix (bc995d1):        CORRECT -- proven by a real live
                                   Editor session producing exactly the
                                   intended content
Live deployment:                  STALE -- persistent worker process
                                   predates the fix; needs a restart to
                                   pick up the new code
Dragon's [EDITOR_REQUEST] usage:  now working, once the mechanism was
                                   named explicitly in the request
```

Restarting the live persistent worker/runtime is a real action against
a currently-running system and was not taken as part of this receipt —
flagged for the user to authorize separately.
