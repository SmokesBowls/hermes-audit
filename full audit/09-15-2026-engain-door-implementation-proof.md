# engain_door.py implemented and proven live against real chapters

Implements the frozen contract (`09-15-2026-engain-door-contract-v1.md`,
amended by `09-15-2026-engain-door-contract-amendment-fail-closed-collision.md`).
Lives at the dragon3d avatar repo root
(`/mnt/data-drive/godot_engain_3d_avatar/engain_door.py`, matching the
placement convention of every existing standalone Python module there
— `engain_continuity_client.py`, `hermes_session_adapter.py`, etc., all
at repo root, not nested), committed there as `cb13c54`.

Every path below was run for real, not simulated, with `ENGAIN_ROOT`
pointed at the checked-out EngAIn tree.

## Happy paths

- `status` on the already-ingested `book_04_sage_saga/016_the_choice_third_coming.md`
  → `ok:true, ingestion_status:"existing", chapter_id:"chapter.book004.016_the_choice_third_coming", scene_count:2`.
- `ingest` on that same already-ingested source → idempotent skip:
  `ingestion_status:"existing"`, empty stderr, confirming `pipeline_runner`
  was never invoked for a source already known-good.
- `query --query "Igigi"` on it → 8 hits: 7 `raw_text` (6 in scene001,
  1 in scene002, matching the verified mention counts from the
  Boundary 6 checkpoint) + 1 `entity_observation`
  (`known:false, spawnable:false, classification:"unknown", mentions:6`).
  Both lanes working together, no duplication.
- `status` on a genuinely never-touched real chapter
  (`book_18_inquisition_of_yourself/096_violet_convergence.md`) →
  `ingestion_status:"not_ingested"`.
- `query` on that same untouched source → `ok:false,
  error:"INGEST_REQUIRED"`, exit 1 — refused before reading anything.
- `ingest` on it → **real subprocess execution**, not a skip: 166 lines
  of Mettaext's own chatter landed on stderr (`[PASS1] Done...`,
  `[PASS1_SPATIAL] signal_count...`, etc.), stdout was exactly one line
  of JSON, `ingestion_status:"created"`, real folder-aware
  `chapter_id:"chapter.book018.096_violet_convergence"`, `scene_count:3`.
- `query --query "Violet"` on the freshly-ingested chapter → 17 hits
  immediately available, no re-ingestion needed.

## Error paths

- No `--source` → `SOURCE_REQUIRED`, exit 1.
- Nonexistent `--source` path → `SOURCE_NOT_FOUND`, exit 1.
- `ENGAIN_ROOT` pointed at a bogus directory → `METTAEXT_NOT_FOUND`,
  exit 1.

## Fail-closed stem-collision guard — the specific correction from this session

Constructed a real decoy file at a scratch path, deliberately given the
exact same filename stem as the already-ingested book004 chapter
(`016_the_choice_third_coming.md`, different absolute path, unrelated
one-line content):

- `status` on the decoy → `ok:true, ingestion_status:"stem_collision"`,
  with `collision.conflicting_source` correctly naming the *real*
  book004 source path — informational, never implies safe-to-proceed.
- `ingest` on the decoy → `ok:false, error:"SOURCE_STEM_COLLISION"`,
  exit 1, **stderr was completely empty** — direct proof
  `pipeline_runner` was never invoked, so nothing was overwritten.
- `query` on the decoy → `ok:false, error:"SOURCE_STEM_COLLISION"`,
  refused before reading any evidence.
- Confirmed afterward, directly: the real book004
  `out_passA_016_the_choice_third_coming.json` still reads
  `chapter_id: "chapter.book004.016_the_choice_third_coming"` and
  `source_file` pointing at the real book004 path — untouched. The
  amendment's core promise (refuse rather than overwrite) holds under
  a real, deliberately-provoked collision, not just in the spec.

## Not exercised live (implemented per spec, not forced)

`INGEST_FAILED`, `MANIFEST_INVALID`, `EVIDENCE_NOT_FOUND`, and
`QUERY_FAILED` all exist in the code exactly as specified in the
contract, but weren't forced live in this pass — doing so would mean
deliberately corrupting or crashing part of a real Mettaext run, which
wasn't worth the side effects for this verification. Worth a targeted
check before this is trusted as the actual Dragon-facing path, not
before.

## Status

`engain_door.py` exists, matches the frozen (and amended) contract
field-for-field, and both the general happy paths and the specific
collision correction from this session are proven against real chapter
data. Not yet wired into Dragon's bridge itself — that's the next
integration step, not done here.
