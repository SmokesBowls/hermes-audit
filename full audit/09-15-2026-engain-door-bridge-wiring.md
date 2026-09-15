# Dragon bridge wiring — query only, subprocess boundary, tiny by design

Closes the instruction: "wire only the query path into Dragon's
bridge using engain_door.py as a subprocess and JSON as the sole
contract. Do not import the door module directly. Do not add automatic
ingest or source discovery." Comes after
`09-15-2026-engain-door-error-contract-tests.md` closed the last error
coverage gap.

## What was built

`engain_door_client.py` (dragon3d repo root, `f68e481`) — the one
place in this repo allowed to cross the door's CLI/JSON boundary.
`query_engain_door(source, query)` shells out to `python3
engain_door.py query --source ... --query ...`, relays the
subprocess's stderr, and returns the parsed stdout JSON **completely
unmodified** — no filtering, no summarizing, no interpretation. A
door-reported `ok:false` (e.g. `INGEST_REQUIRED`) comes back as
ordinary data for the caller to read, exactly like an `ok:true`
response; the client only raises `EngainDoorClientError` for a
plumbing failure on its own side of the boundary (subprocess wouldn't
launch, timed out, or didn't emit valid JSON).

`ENGAIN_ROOT` resolution is deliberately not this module's concern —
it must already be set in the calling process's environment, same as
the door's own contract requires, inherited into the subprocess
automatically.

## Explicit exclusions honored

- No module import of `engain_door.py` anywhere — verified by reading
  `engain_door_client.py`'s own source: the only reference to
  `engain_door.py` is as a `Path` used to build a subprocess command
  line.
- No automatic ingest — `query_engain_door` only ever calls the
  `query` operation. Calling `ingest` remains a separate, explicit
  decision left entirely to whatever calls this client.
- No source discovery — `source` is a required parameter, always
  caller-supplied, same as the door's own contract.
- No conversational orchestration — `engain_door_client.py` is not
  called from `hermes_session_adapter.py` or any live per-turn
  dispatch path. Deliberately left for a later, separate step. This
  pass proves the pipe works; it doesn't yet decide when Dragon should
  turn the handle.

## Live proof

`tests/test_engain_door_client.py::test_live_dragon_can_knock_door_answers_dragon_can_read_it`
— real, unmocked, run against the live EngAIn checkout: calls
`query_engain_door` for "Igigi" against the already-ingested
`book_04_sage_saga/016_the_choice_third_coming.md`, gets back
`ok:true`, both evidence lanes present (`raw_text` and
`entity_observation`), and confirms the entity observation correctly
carries `known:false, spawnable:false` end to end through the client,
not just at the door's own CLI. Skips automatically (rather than
failing) when `ENGAIN_ROOT` or the test chapter aren't present on the
machine running the suite, keeping it portable.

Alongside: 4 mocked-subprocess tests for the client's own plumbing
failures (timeout, launch failure, non-JSON stdout), and one test
confirming a well-formed `ok:false` door response is returned as data,
never raised. All 6 pass; full repo suite re-run at 299 passed, same 6
pre-existing unrelated failures as every prior check this session, no
regression.

## Status

```text
Dragon request (not yet wired to a real trigger)
   -> engain_door_client.query_engain_door()   [built, tested, proven live]
   -> engain_door.py query, subprocess          [built, tested, proven live]
   -> stable/repaired Mettaext                  [checkpointed at 105c9dd]
```

The door and its one bridge-side crossing both exist and are proven.
What remains, and was intentionally not done in this pass: actually
calling `engain_door_client.query_engain_door` from somewhere in
Dragon's live conversation loop — deciding when a turn should knock on
the door at all. That's the conversational-orchestration step, a
separate decision from "does the pipe work."
