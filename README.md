# Godot 3D Avatar — Progress

Session close: 2026-08-10

## Current gate

Stage 7 live current-perception production code is implemented in exactly:

- `scripts/PerceptionCapture3D.gd`
- `scripts/EngAInBridge3D.gd`
- `scripts/ControlHUD.gd`
- `hermes_session_adapter.py`

The frozen Stage 7 gate is GREEN at the application-contract level:

- protected Stage 4–7 tests: `178 passed`
- Godot 4.6.1 headless editor parse: exit `0`
- Python compilation: passed
- `git diff --check`: passed
- final independent Amendment 5 review: `PASS`
- provider executions during Stage 7 RED/GREEN: `0`
- live HUD submissions during Stage 7 RED/GREEN: `0`

Frozen Stage 7 tests remain unchanged:

```text
7d4387695af71ac937742266f185a68b2b82e695d34943b8764801b2eb14ea66
tests/test_stage7_live_perception_capture.py

28f06f4e7db140964b8dfa19bc3587e15c20c2ba3c4d0a48c550e8579d355aec
tests/test_stage7_live_perception_adapter.py
```

## Proven implementation

- The capture producer accepts the bridge-owned `client_request_id`, owns
  `capture_id`, records `captured_at` before fallible work, and reuses the
  Stage 5A PNG/JSON persistence and hashing path.
- The bridge reserves capture state before its first await, suppresses response
  polling during capture, publishes exactly once, and emits
  `submission_committed` only after publication.
- The HUD clears unchanged submitted text only after the correlated commit and
  preserves newer or unrelated text.
- Full adapter requests pass through `prepare_image_dispatch` before the
  director/provider boundary. The admitted argv, image path, and SHA-256 are
  retained one-shot; `chat()` executes the admitted argv and rehashes the image
  immediately before `_run_bounded`.
- Unavailable perception does not prepare or attach an image.

## Closure status

Do not call Stage 7 finally sealed yet. Two architecture questions remain for
explicit authority:

1. A bridge timeout invalidates late publication, but Godot cannot cancel the
   already-running capture coroutine. A replacement lifecycle could therefore
   overlap producer work unless a producer-level lock or cancellation contract
   is added.
2. The frozen pathname-based `--image` interface proves the admitted command,
   path, and pre-launch hash under application-level immutable-evidence rules.
   It cannot exclude a hostile same-user pathname replacement between the last
   hash and Hermes opening the file. Descriptor-bound or OS-enforced evidence
   would require an amended architecture/test authority.

Until those questions are resolved, the accurate status is:

```text
Frozen Stage 7 test gate:                 GREEN
Application-level Amendment 5 review:    PASS
Adversarial filesystem/cancellation seal: BLOCKED ON AUTHORITY
Provider authorization remaining:        unchanged; no execution authorized
```

## Audit authorities and evidence

- `ENGAV3D-0001-IDENTITY-MAILBOX-PERCEPTION-FREEZE.md`
- `ENGAV3D-0001-AMENDMENT-1-STAGE5B-PREPARATION-BOUNDARY.md`
- `ENGAV3D-0001-AMENDMENT-5-STAGE7-LIVE-PERCEPTION-LIFECYCLE.md`
- `ENGAV3D-0012-STAGE7-LIVE-PERCEPTION-RED.log`
- `ENGAV3D-0012-STAGE7-LIVE-PERCEPTION-TESTS.sha256`
