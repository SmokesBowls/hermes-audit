# ENGAV-0001 — Hermes Embodiment Proof: Final Preservation Record

Preservation date: 2026-07-31

Repository: `/mnt/data-drive/engain_avatar`

Baseline commit: `22b0ffdf16c014da8aaf7760a031c5ae6788e9cd`

## Sealed Git identity

- Commit: `f00ff0424f714726f024c0d763b741f61dfc8178`
- Tree: `2e8d83408d435e06277b38b2e0925bbf90915d3e`
- Parent: `22b0ffdf16c014da8aaf7760a031c5ae6788e9cd`
- Commit subject: `ENGAV-0001: seal Hermes embodiment proof`
- Annotated tag: `engav-0001-hermes-embodiment-proof`
- Tag object: `025a76728e64504a8a66aa883cfd8d43336d2c42`
- Peeled tag commit: `f00ff0424f714726f024c0d763b741f61dfc8178`

The commit contains exactly these two paths:

```text
M addons/zwengain/scripts/EngAInDragon.gd
A hermes_session_adapter.py
```

The five pre-existing Godot `.import` modifications were not staged or committed.

## Source SHA-256

```text
34d84f4536671b6e0b8118ee91e756142f9c31c02f8598775f98e838f7289bc9  addons/zwengain/scripts/EngAInDragon.gd
7828bdf556f2b16748dc1b11cf32bf64bba16f5c70908b7b5a05387dafac2355  hermes_session_adapter.py
```

## Final Hermes session

```text
session_id: 20260730_211403_f1204d
```

The persisted session state is preserved at:

```text
/mnt/data-drive/engain-avatar-audit/logs/engav-0001-hermes-session-state.json
```

SHA-256:

```text
cb74ebd634b365b1869aed17edb76d5a8ea1d2c9112317d4fb93658c6c742a02
```

## Final real provider / Godot proof

Adapter command:

```bash
python -u hermes_session_adapter.py \
  --project-dir /mnt/data-drive/engain_avatar \
  --provider openai-codex \
  --model gpt-5.6-sol \
  --timeout 30 \
  --state-file /tmp/engav0001-final6-state.json \
  --pid-file /tmp/engav0001-final6-adapter.pid
```

Godot proof command:

```bash
set -o pipefail
set +e
timeout --signal=TERM --kill-after=5s 240s \
  godot --headless \
  --path /mnt/data-drive/engain_avatar \
  --script /tmp/engav0001_tests/godot_two_turn_proof.gd \
  2>&1 | tee /tmp/engav0001_tests/godot-two-turn-final6.log
status=${PIPESTATUS[0]}
printf 'GODOT_FINAL6_PROOF_EXIT=%s\n' "$status"
exit "$status"
```

Observed result:

```text
ENGAV_PROOF_TURN1=TOKEN STORED
ENGAV_PROOF_TURN2=DRAGON-NONCE-7F31
ENGAV_PROOF=PASS
GODOT_FINAL6_PROOF_EXIT=0
```

The complete proof log is preserved at:

```text
/mnt/data-drive/engain-avatar-audit/logs/engav-0001-godot-two-turn-final.log
```

SHA-256:

```text
38e80dab63af97e3c2f970f06042d28c7b6d618fa91b6faeb80ea3f9c6760e43
```

The headless run emitted the known pre-existing SnapshotManager viewport-capture error on the second response. The exact visible response and proof completed with exit status 0. SnapshotManager was outside ENGAV-0001 scope.

## Restart continuity proof

Restart command:

```bash
python -u hermes_session_adapter.py \
  --project-dir /mnt/data-drive/engain_avatar \
  --provider openai-codex \
  --model gpt-5.6-sol \
  --timeout 30 \
  --state-file /tmp/engav0001-final6-state.json \
  --pid-file /tmp/engav0001-final6-adapter.pid \
  --once
```

Observed response after worker restart:

```json
{
  "request_id": "engav_restart_final6_1",
  "client_request_id": "dragon_restart_final6_1",
  "narrative_response": "DRAGON-NONCE-7F31",
  "action_type": "OBSERVATION",
  "state_changes": {},
  "entropy_impact": 0.0
}
```

The same persisted session ID, `20260730_211403_f1204d`, was reused.

## Final focused test gate

Command:

```bash
cd /tmp/engav0001_tests
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_engav0001
python -B -m py_compile /mnt/data-drive/engain_avatar/hermes_session_adapter.py
git -C /mnt/data-drive/engain_avatar diff --check
```

Result:

```text
Ran 20 tests in 0.355s
OK
py_compile: PASS
git diff --check: PASS
```

Additional ad-hoc verification exhaustively enumerated all 63 disallowed Unicode category `Cc` code points and proved prefix/suffix ingress rejection, visible-egress stripping, and newline/tab preservation. Separate real Godot ad-hoc verification proved the speech-generation guard prevents an older delayed coroutine from clearing newer correlated text. These temporary `hermes-verify-*` scripts were explicitly ad hoc, were stored under `/mnt/data-drive/EngAIn_Recovery/07_TMP`, and were deleted after successful execution.

## Independent closure review

Final current-byte review `deleg_5bad6f79` returned:

```json
{
  "passed": true,
  "security_concerns": [],
  "logic_errors": [],
  "suggestions": []
}
```

## Preserved authority boundary

The restored active path is:

```text
Godot LineEdit
→ existing EngAInBridge
→ hermes_session_adapter.py
→ existing EngAIn director responsibilities
→ persisted Hermes session
→ existing EngAInBridge response signal
→ EngAInDragon.dragon_speak()
→ visible response
```

Provider output is constrained to observation-only text:

```json
{
  "action_type": "OBSERVATION",
  "state_changes": {},
  "entropy_impact": 0.0
}
```

`EngAInBridge.gd` remains immutable. Consequently, local repository filesystem writers remain a trusted boundary; model/provider/player inputs are untrusted and bounded, filtered, correlated, tool-less, and denied mutation authority.

## Deferred work

- ENGAV-0002: extract Agent Portal and Hermes Driver responsibilities without Godot or external-schema changes, preserving all ENGAV-0001 tests and live proofs.
- SnapshotManager headless viewport capture: separate pre-existing ticket.

## Final repository state

The proof commit and annotated tag are local. They were not pushed because no push was requested.

The worktree intentionally remains modified only by the five pre-existing `.import` drift files. No ENGAV-0001 runtime request, response, or database artifact remains in the repository.
