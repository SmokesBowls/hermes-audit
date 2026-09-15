# engain_door.py error-contract tests — isolated, no live Mettaext damage

Closes the gap named in the last checkpoint: `INGEST_FAILED`,
`MANIFEST_INVALID`, `EVIDENCE_NOT_FOUND`, `QUERY_FAILED` were
implemented per the frozen contract but not exercised live, since
forcing them for real would mean deliberately breaking part of a real
Mettaext run. Added `tests/test_engain_door.py` in the dragon3d repo
instead (`f8a2efb`): a fake `$ENGAIN_ROOT` built fresh under `tmp_path`
per test, minimal fixture artifacts matching the real verified schemas
(`out_passA_*.json`, `scene_packets_index.json`, `out_pass1_*.txt`,
`<scene_id>.zonj.json`), and `subprocess.run` monkeypatched where a
Mettaext subprocess call needs to be simulated. The real EngAIn
checkout is never touched.

## Coverage, 10/10 passing

- **`INGEST_FAILED`** — three angles: non-zero exit from the mocked
  subprocess; a mocked `TimeoutExpired`; and the specific case the
  contract calls out explicitly — subprocess reports exit 0 but the
  door's own post-run check finds no Pass A artifact actually landed.
  All three raise `INGEST_FAILED`, confirming the door never trusts a
  reported success on its own.
- **`MANIFEST_INVALID`** — two angles, both simulating "Pass A/scene
  index landed for real, but the manifest step specifically broke":
  manifest file missing entirely, and manifest file present but not
  valid JSON. Both distinguish correctly from the broader
  `INGEST_FAILED` (evidence did land; only the manifest is the
  problem).
- **`EVIDENCE_NOT_FOUND`** — a chapter with a valid Pass A and scene
  index but zero scenes carrying an `out_pass1_*.txt`. Also tested the
  adjacent, deliberately-different case: one scene present, one
  missing — confirmed that's a **warning inside a successful
  response**, not a hard failure, exactly as the contract specifies
  (partial evidence loss ≠ total evidence loss).
- **`QUERY_FAILED`** — empty/whitespace-only `--query` string (the
  argument-validation path), and a malformed `<scene_id>.zonj.json`
  that a valid `out_pass1_*.txt` search successfully reaches before
  hitting the corrupt file.
- A sanity test (fixtures producing an ordinary successful two-lane
  query) confirms the fixture helpers themselves are correct — a
  failure in the tests above is attributable to the specific fault
  injected, not to a broken test harness.

## Regression check

Ran the full `tests/` suite alongside: 293 passed, 6 failed. All six
failures pre-exist this change and are unrelated —
`test_stage8_ticket3b_worker_ownership_red.py` is intentionally
red/TDD by its own filename, plus two unrelated failures in
`test_hermes_session_adapter.py` and `test_stage6a_godot_mailbox_bridge.py`.
No regression introduced.

## Status

All four previously-unexercised error contracts now have real,
isolated proof. `engain_door.py`'s full error surface (all 8 codes) is
now verified — 4 live against real chapters
(`09-15-2026-engain-door-implementation-proof.md`), 4 via isolated
fixtures here. Ready for the next, explicitly scoped step: wiring only
the `query` path into Dragon's bridge as a subprocess call, JSON as
the sole contract, no module import, no automatic ingest, no
conversational orchestration yet.
