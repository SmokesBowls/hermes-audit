#!/usr/bin/env python3
"""Admit the exact semantic Stage 8 Ticket 3B intentional RED."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = Path("/mnt/data-drive/godot_engain_3d_avatar")
AUDIT = ROOT.parent
BASE_HEAD = "77593c205851c97a1b0b46ebdb6ade270309f81a"
TESTS = (
    "tests/test_stage8_ticket3b_godot_routing_red.py",
    "tests/test_stage8_ticket3b_hud_lifecycle_red.py",
    "tests/test_stage8_ticket3b_worker_ownership_red.py",
)
EXPECTED_TEST_HASHES = {
    TESTS[0]: "08c0cb1d346a41c4fab16c8abb64de96f768b4bc6ea279a01a5496b35425485f",
    TESTS[1]: "bef933b4a833fffac7796e393756574bcca17b0d7cbd002ab76ab8b8c87da77e",
    TESTS[2]: "7868afe8cd4fc09a839de746f28f9bd2e9fcbeb42fdc78a0bb8b5fc542b29787",
}
EXPECTED_FAILURES = {
    "test_ticket3b_text_only_fixture_selects_text_wire_without_capture",
    "test_ticket3b_internal_looking_is_observable",
    "test_ticket3b_thinking_begins_only_after_successful_request_commit",
    "test_ticket3b_runtime_shutdown_clears_transient_status",
    "test_ticket3b_runtime_boundary_makes_exactly_one_persistent_worker_available",
    "test_ticket3b_multiple_submissions_share_one_observed_worker_identity",
    "test_ticket3b_runtime_shutdown_requests_ticket2f_explicit_stop",
}
PRESERVED = {
    "hermes_session_adapter.py": "fc7969f9be6f992570821d96ed9a46b62959f5cc60780d4d89d9a04cc79f7542",
    "scripts/EngAInBridge3D.gd": "814c25c3c784b880992ec9725232dc0de2dac3662b180409a3709911c14cd6eb",
    "scripts/ControlHUD.gd": "acc0b0e075f788b96cf146a9376a56ec94943b661585570f8c1cecaa23c0c2f1",
    "scripts/PerceptionCapture3D.gd": "9ed05917067e799ee0b8de35e6bb68158c838a7eb1effb5d16137c6a3d213da7",
    "scripts/Main.gd": "0dea446757d1cf0941a364f0524d3a08fe859c816c48c7063e195f72be9191cf",
    "scripts/DragonAvatar3D.gd": "ef667b7eb63c4689f23888cf28ff25891fb459f2ccc6e6f99c4febc75dbbcf38",
    "tests/test_stage7_live_perception_capture.py": "7d4387695af71ac937742266f185a68b2b82e695d34943b8764801b2eb14ea66",
    "tests/test_stage7_live_perception_adapter.py": "28f06f4e7db140964b8dfa19bc3587e15c20c2ba3c4d0a48c550e8579d355aec",
    "tests/test_stage8_ticket2e_persistent_worker_red.py": "db705f501187709b55f927faa589bafad93a3cb6e72368387b0a4dcc5914d068",
    "snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.json": "c5588884a45c6ab6ab7be7df1a102d3411431d488a25cca01c8dc240f26028aa",
    "snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png": "ddbca6833ba8f8a44c733e2a2feceabbac96d5a238b1a360ae2da690268fc858",
    "snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png.import": "12ce78ab051d67ce9200edd6a0f46cc067b10cce548bcc41cc6c24fbdf8b75b8",
}
EXPECTED_STATUS = {
    " M hermes_session_adapter.py",
    " M scripts/DragonAvatar3D.gd",
    " M scripts/EngAInBridge3D.gd",
    "?? snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.json",
    "?? snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png",
    "?? snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png.import",
    "?? tests/test_stage8_ticket2c_text_only_adapter_red.py",
    "?? tests/test_stage8_ticket2c_text_only_bridge_red.py",
    "?? tests/test_stage8_ticket2e_persistent_worker_red.py",
    "?? tests/test_stage8_ticket3b_godot_routing_red.py",
    "?? tests/test_stage8_ticket3b_hud_lifecycle_red.py",
    "?? tests/test_stage8_ticket3b_worker_ownership_red.py",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reject(detail: str) -> None:
    print(f"STAGE8_TICKET3B_RED_REJECTED: {detail}")
    raise SystemExit(1)


if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip() != BASE_HEAD:
    reject("base HEAD differs")
for relative, expected in EXPECTED_TEST_HASHES.items():
    if sha256(REPO / relative) != expected:
        reject(f"test identity differs: {relative}")
    if (REPO / relative).read_bytes() != (ROOT / Path(relative).name).read_bytes():
        reject(f"evidence test copy differs: {relative}")
for relative, expected in PRESERVED.items():
    if sha256(REPO / relative) != expected:
        reject(f"preserved identity differs: {relative}")
status = set(subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=REPO, text=True).splitlines())
if status != EXPECTED_STATUS:
    reject("repository status differs")
base_sidecar = subprocess.run(
    ["sha256sum", "-c", "ENGAV3D-0032-STAGE8-TICKET3A-HUD-CAPTURE-ORDER-ADMITTED.sha256"],
    cwd=AUDIT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
)
if base_sidecar.returncode != 0:
    reject("Ticket 3A base authority failed")

focused = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", *TESTS], cwd=REPO,
    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    timeout=180, check=False,
)
if focused.returncode == 0:
    reject("focused process unexpectedly exited zero")
failed = set(re.findall(r"^FAILED .*::([^\s]+)", focused.stdout, re.MULTILINE))
if failed != EXPECTED_FAILURES:
    reject(f"failure identities differ: {sorted(failed)}")
if not re.search(r"7 failed, 7 passed", focused.stdout):
    reject("focused count differs")
for forbidden in (
    "ERROR collecting",
    "fixture '" ,
    "ERROR at setup",
    "SyntaxError",
    "INTERNALERROR",
):
    if forbidden in focused.stdout:
        reject(f"invalid RED failure class: {forbidden}")

print("STAGE8_TICKET3B_GODOT_LIFECYCLE_RED")
print("TEXT_ONLY_ROUTE_SELECTION=FAIL_EXPECTED")
print("CURRENT_PERCEPTION_ROUTE_SELECTION=PASS_ALREADY_PRESENT")
print("TEXT_ONLY_CAPTURE_SUPPRESSION=FAIL_EXPECTED")
print("CURRENT_PERCEPTION_CAPTURE_PRESERVATION=PASS_ALREADY_PRESENT")
print("INTERNAL_LOOKING_STATE=FAIL_EXPECTED")
print("VISIBLE_PRE_CAPTURE_MUTATION_FORBIDDEN=PASS_ALREADY_PRESENT")
print("THINKING_AFTER_COMMIT=FAIL_EXPECTED")
print("CORRELATED_STATUS_CLEAR_GATE=PASS_ALREADY_PRESENT")
print("STALE_RESPONSE_CANNOT_CLEAR_GATE=PASS_ALREADY_PRESENT")
print("TERMINAL_FAILURE_RELEASE=PASS_ALREADY_PRESENT")
print("RUNTIME_SHUTDOWN_STATUS_CLEAR=FAIL_EXPECTED")
print("PERSISTENT_WORKER_AVAILABLE_TO_RUNTIME=FAIL_EXPECTED")
print("SAME_WORKER_ACROSS_SUBMISSIONS=FAIL_EXPECTED")
print("RUNTIME_SHUTDOWN_REQUESTS_EXPLICIT_STOP=FAIL_EXPECTED")
print("WORKER_OWNERSHIP_IMPLEMENTATION_CHOICE=OPEN")
print("FOCUSED_TESTS=7_FAILED_7_PASSED")
print("STAGE7_CAPTURE_ORDER=PRESERVED")
print("TICKET2D_TEXT_ONLY_WIRE=PRESERVED")
print("TICKET2F_WORKER_LIFECYCLE=PRESERVED")
print("PROVIDER_EXECUTIONS=0")
print("PRODUCTION_FILES_CHANGED=0")
print("RUNTIME_IMPLEMENTATION=NOT_AUTHORIZED")
