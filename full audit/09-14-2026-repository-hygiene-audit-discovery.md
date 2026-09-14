# Repository hygiene audit — discovery only

## Scope and method

Target: `godot_engain_3d_avatar` (the repo with `.engain_request.req_*.tmp`
in its root). Checked against its actual current state — `git status
--porcelain=2 --ignored=matching`, `du`, `find`, and direct code reading
— not assumed from memory. Baseline was git-clean at the start (0
untracked-and-not-ignored files); a live game session (editor + composed
runtime, PIDs 2968093/2968094/2968110) turned out to be running,
started independently at 05:42, three minutes before this pass began —
noted where it changed a number, since the repo is not static during
this audit.

No files were deleted or moved. Findings only.

## 1. `.engain_request.req_*.tmp` — the file the user asked to be traced specifically

**What creates it:** `scripts/EngAInBridge3D.gd:319-331`. Every single
player message that reaches a live-capture turn allocates a random
`req_<32hex>` ID and writes
`<PROJECT_ROOT>/.engain_request.<id>.tmp` directly in the **project
root** via `FileAccess.open(..., FileAccess.WRITE)` — not under
`.godot/`, not under any mailbox/temp directory. This is deliberate
project-root placement, not a mistake: `hermes_session_adapter.py`'s
`publish_request()` requires the temp file's parent to equal the frozen
project root (line ~561) as an identity/security check.

**Why old ones survive — the actual defect:** immediately after writing
the temp file, `EngAInBridge3D.gd:333` shells out to
`hermes_session_adapter.py --publish-request <path>`, which internally
calls `publish_request()` — and *that* function reliably deletes its
exact temp file on every path, success or validation failure (its own
`try/except/finally` calls `cleanup_exact_temporary()` unconditionally).
**But if that subprocess call itself fails to complete** — non-zero
exit, timeout, the game process dying, or any other failure before
`publish_request()` ever got to run — `EngAInBridge3D.gd:334-337` just
logs the error and returns. **Nothing in the GDScript path deletes the
temp file it just wrote when the downstream publish step doesn't
succeed.** Confirmed by reading the whole branch: there is no `catch`-
equivalent cleanup, no retry-then-delete, nothing.

**Does the runtime still depend on them?** No. They are single-use,
named by a random per-turn ID that's never reused. Once abandoned they
are inert — nothing reads them again, they're just failed turns'
wreckage.

**Count / size right now:** 12 files, 48 KB total, timestamped Aug 17
through Aug 30 (`.engain_request.req_073b95...` through
`...faa8509...`) — spanning exactly the period this project's own
receipts document real crashes and clobbers (Editor reload crashes,
`Main.tscn` autosave clobber, timeout/duplicate-event bugs). None from
September — consistent with those specific failure modes having since
been fixed, not with the leak itself being fixed.

**Intended lifetime:** milliseconds — write, publish, delete, all
within one `_execute_adapter()` call.

**Why in the repo root:** structural requirement of
`publish_request()`'s own identity check (temp file's parent must be
the frozen project root) — not a placement mistake, but nothing about
that check requires the *stale* ones to stay there forever once
abandoned.

**Should they live elsewhere?** The live, in-flight ones can't move
without a matching change to `publish_request()`'s frozen-root check —
out of scope here (would touch proven code). The **stale, abandoned**
ones have no reason to stay; they're accumulated failure debris, not
functional state.

**Is existing cleanup failing?** No — there is no existing cleanup for
this specific case. `publish_request()`'s cleanup is real and correct
for every path that reaches it. The gap is upstream: the GDScript
writer has no fallback delete when its own publish call doesn't
succeed. Grepped the whole adapter for any startup/orphan sweep
(`orphan`, `cleanup`, `sweep`) — none exists for this file class at
all, only per-call "delete the exact one I'm holding" logic.

## 2. Stale response/claim/temp files (other than the above)

- `engain_request.json` (the canonical, non-temp mailbox file, single
  slot, atomically hardlinked into place by `publish_request()`):
  present, 261 bytes, last written Aug 13. Ignored via `.gitignore`.
  Single-slot by design — does not accumulate. Not a hygiene problem.
- `engain_response.json`: does not currently exist on disk. Also
  single-slot/ignored; nothing to report.
- `.godot/engain_hermes_replay/<request_id>.reserved` — a genuine
  crash-safety replay-dedup lock
  (`_reserve_request()`/`_release_request_reservation()`,
  `hermes_session_adapter.py:2542-2600`), created before processing a
  claimed request and deleted right after. Watched one appear and
  disappear live during this audit (`req_a87fe9e1...reserved`, created
  and released within the same second) as the running session actually
  processed a real turn — proof the release path works correctly on
  the success path. No stale ones found at rest. Not a hygiene problem,
  but worth knowing it exists next to the `.tmp` mailbox files for
  anyone tracing this family of artifacts later.

## 3. Capture/snapshot artifacts

**What creates them:** every perception capture writes a PNG +
metadata JSON pair (plus Godot's own `.import` sidecar once the editor
indexes the PNG) into `snapshots/`, per `_publish_snapshot_pair()` /
the `perception_cap_<hash>_<n>` naming convention.

**Runtime dependency:** none after the fact — each snapshot is read
back only for the correlated turn it was captured for
(`CURRENT_RUNTIME_PERCEPTION` freshness checks). Nothing re-reads an
old one later.

**Count/size:** **177 files tracked in git** (59 PNG + 59 JSON + 59
`.import`, ~2.9 MB), spanning Aug 8 → Sep 13 across 7 separate commits
— this has been growing steadily, monotonically, for over a month.
While auditing, the currently-live session added **3 more full
triplets (9 files) as untracked working-tree changes** in real time —
concrete proof this keeps growing with ordinary play, not just formal
test runs.

**Intended lifetime:** effectively one turn (freshness-checked against
the current request only) — but nothing ever removes the file
afterward.

**Why in the repo, and is that appropriate:** this is evidentiary/
diagnostic material (a screenshot record of what the game looked like
at a moment in the past), **committed into the code repository** —
which runs directly against this project's own stated discipline (code
repos hold only what's meant to be committed; evidentiary/diagnostic
material belongs in the audit repo). Every clone of this repo now
carries 2.9 MB of unversioned-in-spirit capture history that grows
without bound and will never shrink under git's normal model.

**Should it move?** Yes in principle — this is the single largest,
fastest-growing hygiene issue found. It doesn't belong committed to the
game repo at all; if kept, it belongs either git-ignored (local-only,
like `.hermes_scratch/`) or physically relocated to the audit repo's
evidence area. Moving/untracking 177 already-committed files is a real
history-shape decision, explicitly not done here.

## 4. Generated logs

None found. `find . -iname "*.log"` (excluding `.git/`) returned
nothing, and `.gitignore` already covers `*.log` / `crash*.txt`. No
issue.

## 5. Test leftovers

- **`.pytest_cache/`** — 64 KB, standard, ignored, regenerated every
  `pytest` run. Not a problem.
- **`.hermes_scratch/scenes/Main.tscn`** — a **genuinely stale
  SAFE/REVIEW-mode proposal**, last written 2026-08-23, predating the
  `Main.tscn`/`WorldComposition.tscn` split entirely (diffed against
  the live `Main.tscn`: missing the `WorldComposition` instance node
  entirely, missing the current HUD anchor layout, different
  `DragonAvatar3D` transform). Nobody ever reviewed, applied, or
  discarded it — it has just been sitting in the ignored scratch
  directory for three weeks. `.hermes_scratch/tests/
  test_beacon_gate_proposal.py` is the same kind of leftover — an
  unreviewed proposal, not a real test in `tests/`.
- **`tests/`** itself is clean — every tracked file is a real
  `.py`/`.gd`/`.uid`, no generated output checked in.

## 6. Obsolete probe artifacts

- **`scenes/AzureCubeProbe09.tscn`** and **`scenes/EmeraldCubeProbe10.tscn`**
  — tracked, tiny (~530 bytes each), last touched by the Sept 13 "hot
  reload" commit, but **referenced by nothing** — not by
  `WorldComposition.tscn`, not by `Main.tscn`, not by any script. These
  are exactly the two probes the ownership-split receipt documents as
  lost to the `Main.tscn` autosave-clobber bug before
  `WorldComposition.tscn` existed; every other probe from that same
  sequence (Amber/Diamond/Violet/etc.) is live-instanced in
  `WorldComposition.tscn` today. These two are the only orphans.
- **`evidence/stage8_ticket3f_green.txt`** — a single tracked
  stage-gate proof artifact from Aug 16. Same category problem as
  §3: evidentiary material committed into the code repo rather than
  the audit repo, just a single small file rather than a growing
  directory.
- **`engain_probe/engain_visibility_probe.py`** — tracked, but not
  imported or invoked anywhere else in the repo (checked: zero
  references outside its own file). Could be a still-useful standalone
  manual diagnostic tool or a dead one-off; nothing here proves either
  way — flagged, not classified.

## 7. Caches/build output

- **`.godot/`** — 12 MB, ignored, Godot's own editor-managed cache
  (`shader_cache/` 11 MB, `imported/` 1.7 MB). Standard and expected
  for a Godot project; regenerates itself. Not a hygiene issue on its
  own, though it's also where the real per-project state
  (`engain_hermes_session.json`, the `.pid` file, the replay-reservation
  dir) lives, mixed in with pure editor cache — a minor organizational
  note, not a defect.
- No `__pycache__/`, no `.mypy_cache/`, no `.ruff_cache/` found anywhere
  in the tree.

## Summary table

| Class | Tracked in git? | Count now | Size now | Accumulating? | Belongs in repo root? |
|---|---|---|---|---|---|
| `.engain_request.req_*.tmp` (stale) | No (ignored) | 12 | 48 KB | Only on the crash path (dormant since Aug) | No — cleanup gap, not intended state |
| `snapshots/` capture pairs | **Yes** | 177 (+9 untracked, live) | 2.9 MB, growing | **Yes, unbounded** | No — evidentiary, belongs in audit repo |
| `.hermes_scratch/` stale proposal | No (ignored) | 2 files | 20 KB | No (one-off, just never cleared) | Debatable — scratch dir is fine, contents are stale |
| `AzureCubeProbe09.tscn` / `EmeraldCubeProbe10.tscn` | **Yes** | 2 | ~1 KB | No | No — orphaned, referenced nowhere |
| `evidence/stage8_ticket3f_green.txt` | **Yes** | 1 | tiny | No | No — evidentiary, belongs in audit repo |
| `.pytest_cache/` | No (ignored) | — | 64 KB | Regenerates per run | Fine as-is |
| `.godot/` cache | No (ignored) | — | 12 MB | Slowly, normal Godot behavior | Fine as-is |
| `engain_request.json` / `engain_response.json` | No (ignored) | 0-1 | ~4 KB | No, single slot | Fine as-is (structural requirement) |
| `.godot/engain_hermes_replay/*.reserved` | No (ignored) | 0 at rest | 0 | No — self-cleans on success | Fine as-is |

## Proposed smallest cleanup/migration plan (not yet implemented)

Ordered by risk, smallest/safest first. None of this touches
`RuntimeSceneSync3D.gd`, `Main.tscn`/`WorldComposition.tscn` runtime
wiring, or anything the hotload/continuity proofs depend on — every
item below is either dormant debris or a repo-shape decision, not
active state.

1. **Delete the 12 stale `.engain_request.req_*.tmp` files.** Zero
   risk: already proven inert (ignored, un-referenced, from resolved
   incidents). Pure disk cleanup, no code change.
2. **Delete `.hermes_scratch/`'s stale proposal** (`scenes/Main.tscn`,
   `tests/test_beacon_gate_proposal.py`) — an unreviewed, three-week-old
   SAFE/REVIEW artifact from before the ownership split, already
   confirmed to not match current `Main.tscn`. Zero runtime risk
   (ignored, never read by anything except a human reviewing it).
3. **Remove the two orphaned probe scenes**
   (`AzureCubeProbe09.tscn`, `EmeraldCubeProbe10.tscn`) from git.
   Low risk — confirmed zero references — but this is a real tracked-
   file removal, so it's a git change, not just disk cleanup.
4. **Fix the actual leak, narrowly**: give
   `EngAInBridge3D.gd`'s publish-failure branch
   (`scripts/EngAInBridge3D.gd:334-337`) a cleanup call for its own
   `temporary_path` before it returns, mirroring exactly what
   `publish_request()` already does on its own failure path. This is a
   real code change (small, one failure branch) — separate from pure
   hygiene, and should be its own reviewed step, not bundled into a
   disk-cleanup pass.
5. **Relocate `evidence/stage8_ticket3f_green.txt`** to the audit repo,
   removing it from the code repo, per this project's own stated
   discipline. Small, low risk, but changes tracked history.
6. **`snapshots/` — the one that needs a real decision, not just a
   sweep.** Two real options, not a hygiene tweak:
   - (a) git-ignore `snapshots/` going forward (like
     `.hermes_scratch/`) and let captures live locally/untracked, only
     promoting a specific one to the audit repo when it's actually
     needed as evidence; or
   - (b) keep committing them, accept the repo grows a few files per
     played turn indefinitely.
   Either way, the *already-committed* 177 files are a separate
   question (rewrite history to shrink the repo, vs. leave the past
   alone and only fix behavior going forward) — that decision belongs
   to you, not something to default on.
7. **`engain_probe/engain_visibility_probe.py`** — no action proposed;
   flagged only. Needs a answer to "is this still a tool you use," not
   a hygiene classification.

Nothing above has been executed. Stopping here per instruction.
