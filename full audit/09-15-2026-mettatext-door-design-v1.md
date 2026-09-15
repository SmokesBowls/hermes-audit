# The door: Dragon <-> Mettaext contract, v1 — design only, nothing implemented

Captures the design decided in conversation on 2026-09-15, following on
from "the door.md" (untracked transcript, dropped at the audit repo
root, not yet filed). **Nothing below has been implemented.** This is a
design document, not a receipt.

## Where this picks up from

MettaText was chosen as the first EngAIn component to bring into
service, because it sits upstream of the whole working construction
loop (Dragon -> [EDITOR_REQUEST] -> Builder -> WorldComposition ->
hotload) and doesn't require touching any of it. See "the door.md" for
the original reasoning and the `ENGAIN_ROOT` env var convention
(`/home/mytruelove/Desktop/burdens_of_a_forgotten_past/EngAIn`,
Mettaext at `$ENGAIN_ROOT/tier3/mettaext`).

Before designing the contract, the actual Mettaext surface was read
directly (not assumed from the transcript):

- **One entrypoint**: `python3 -m tier3.mettaext.pipeline_runner
  <chapter.txt>`, run with `cwd=ENGAIN_ROOT`. It ingests **a whole
  chapter file**, not a targeted question — there is no "tell me about
  Falcon Ridge" API on the Mettaext side. It chains chapterroom
  ingestion (Pass A/B/C) then passroom compilation (Pass 1-5), then
  writes `tier3/mettaext/stageroom/mettaext_done_manifest.json`
  (`stageroom_manifest.py`).
- **Doctrine is explicit** (`stageroom/STAGEROOM_AUTHORITY_NOTE.md`):
  "Mettaext does not dispatch... Consumers pull from stageroom...
  Presence in stageroom is evidence only... not canon... not runtime
  truth." Confirmed in code: `pipeline_runner.py` and
  `stageroom_manifest.py` never call out anywhere; they only write
  files and stop.
- **Per-scene evidence shape**, verified against a live sample
  (`scene.999_abc_smoke.scene001`): `out_pass1_<scene_id>.txt`
  (line-numbered exact source prose — the witness),
  `<scene_id>.zonj.json` (structured `=segments` with `line`/`type`/
  `text`, plus an `=inferred` block for emotions/actions — the
  semantic-proposal layer), and `game_scenes/<scene_id>.json` (Pass 5
  runtime-shaped output). Scene ids are canonicalized via
  `scene_identity.py` (`scene.NNN_slug`).
- **Not idempotent by itself** — `chapterroom_runner.py` has no
  "already processed" guard. Reprocessing an already-ingested chapter
  is safe (deterministic overwrite of the same output paths) but
  wasteful and not free (it shells out through 5+ subprocesses per
  scene), so the caller must guard against redundant reruns, not
  Mettaext.
- **No retrieval API exists yet.** Mettaext's one operation is
  "ingest a whole chapter." Because of that, the door isn't just a
  pipe — it has to *be* the retrieval layer, since nothing upstream
  provides one.

## Decisions made

**Invocation shape: standalone CLI/subprocess.** The door is a small
standalone script/executable that Dragon's bridge shells out to (the
same pattern Mettaext itself uses internally for its own passes),
rather than a module imported in-process into the bridge. Cleaner
isolation, testable alone, doesn't couple the door's dependencies or
crashes to the bridge process.

**Source selection: Dragon always passes an explicit source path.**
The door never scans a directory or guesses which chapter is
relevant — that judgment (which book/chapter matters right now) stays
upstream of the door, with Dragon. Give the door a source path; the
door determines whether that source is already represented in
stageroom, using Mettaext-specific identity/layout knowledge Dragon
should never need to know.

**Two operations, strictly separated — `query` never triggers
`ingest`:**

```text
ingest:
  Explicitly process the exact source chapter requested by the caller.
  Never invoked implicitly by query.

query:
  Read existing stageroom evidence only.
  Never triggers ingestion as a side effect.
  If no completed ingestion is found for the requested source:
    -> return INGEST_REQUIRED, let the caller (Dragon) decide whether
       to issue an explicit ingest request.
```

**Response contracts:**

```text
ingest response:
  ingestion_status = "created" | "existing" | "failed"

query response:
  ingestion_status = "existing"
  OR error = "INGEST_REQUIRED"
  ("created" is not a valid query response — query cannot create.)
```

**Door ownership boundary:**

```text
Door owns:
  - ENGAIN_ROOT resolution
  - Mettaext invocation details (pipeline_runner subprocess call,
    argument shape, cwd)
  - source_text_id / chapter_id / scene_id derivation and lookup
  - stageroom manifest/layout knowledge (where evidence actually lives)
  - evidence normalization (packaging pass1 text + zonj segments +
    game_scenes JSON, with provenance, into one payload for Dragon)

Door does not own:
  - canon decisions (that's MrLore's job, per Mettaext's own doctrine)
  - source discovery (that's Dragon's / upstream's job)
  - runtime mutation (matches "everything below here already works" —
    Builder/WorldComposition/hotload are untouched)
  - automatic ingestion during query (explicit-only, see above)
```

## Open items (not yet decided)

- Exact CLI argument/output shape for `ingest` and `query` (flags,
  JSON-on-stdout schema for the evidence payload, exit codes).
- Where the door's own code should live: a new directory in the
  dragon3d avatar repo, versus a location it can be invoked from
  without duplicating ENGAIN_ROOT-resolution logic if a second avatar
  body (dragon2d) ever needs the same door.
- What "query" actually matches on — the transcript's example was a
  free-text term ("Falcon Ridge"); the real Mettaext evidence has no
  built-in keyword index, so the door's query implementation will need
  to do its own text/segment search across `out_pass1_*.txt` and
  `*.zonj.json` for the requested source. Matching strategy (exact
  substring vs. something smarter) not yet decided.
- Timeout / failure handling for the `pipeline_runner` subprocess call
  (it chains 5+ subprocesses per scene; no timeout exists today).

## Next step

Write the door's CLI contract and evidence-payload schema concretely,
then implement, following the working discipline established across
this project: real live-executed proof before anything is called
closed.
