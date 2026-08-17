#!/usr/bin/env python3
"""Canonical provider-free admission verifier for Stage 8 Ticket 2C RED."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = Path("/mnt/data-drive/godot_engain_3d_avatar")
BASE_HEAD = "77593c205851c97a1b0b46ebdb6ade270309f81a"
TESTS = (
    "tests/test_stage8_ticket2c_text_only_adapter_red.py",
    "tests/test_stage8_ticket2c_text_only_bridge_red.py",
)
EXPECTED = {
    "hermes_session_adapter.py": "f3add4a3011b09c9f88c489b436e4fc5e4751fd18ccb080810cac6ad06869e39",
    "scripts/EngAInBridge3D.gd": "64abb2a0770973cf8519449b918eb84fca6e87c2e5c298df5086c67a5ad18683",
    "scripts/ControlHUD.gd": "acc0b0e075f788b96cf146a9376a56ec94943b661585570f8c1cecaa23c0c2f1",
    "scripts/PerceptionCapture3D.gd": "9ed05917067e799ee0b8de35e6bb68158c838a7eb1effb5d16137c6a3d213da7",
    "scripts/DragonAvatar3D.gd": "ef667b7eb63c4689f23888cf28ff25891fb459f2ccc6e6f99c4febc75dbbcf38",
    "tests/test_stage7_live_perception_capture.py": "7d4387695af71ac937742266f185a68b2b82e695d34943b8764801b2eb14ea66",
    "tests/test_stage7_live_perception_adapter.py": "28f06f4e7db140964b8dfa19bc3587e15c20c2ba3c4d0a48c550e8579d355aec",
    TESTS[0]: "452097c103ab9d38fd7aed0ae0ab5196836b3d75d7582ef91407d2cd185c7377",
    TESTS[1]: "fc70cfc985a42428768c9c144da3f7fd3655defe766d80bc99912113cfbca465",
    "snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.json": "c5588884a45c6ab6ab7be7df1a102d3411431d488a25cca01c8dc240f26028aa",
    "snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png": "ddbca6833ba8f8a44c733e2a2feceabbac96d5a238b1a360ae2da690268fc858",
    "snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png.import": "12ce78ab051d67ce9200edd6a0f46cc067b10cce548bcc41cc6c24fbdf8b75b8",
}
EXPECTED_STATUS = {
    " M scripts/DragonAvatar3D.gd",
    "?? snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.json",
    "?? snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png",
    "?? snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.png.import",
    "?? tests/test_stage8_ticket2c_text_only_adapter_red.py",
    "?? tests/test_stage8_ticket2c_text_only_bridge_red.py",
}
EXPECTED_FAILURES = (
    "test_ticket2c_adapter_admits_exact_text_only_request",
    "test_ticket2c_text_only_dispatch_has_no_capture_preparation_or_image_argument",
    "test_ticket2c_bridge_admits_correlated_text_only_success",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    print(f"STAGE8_TICKET2C_RED_REJECTED: {message}")
    raise SystemExit(1)


head = subprocess.check_output(
    ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
).strip()
if head != BASE_HEAD:
    fail("repository HEAD differs from base authority")

for relative, expected in EXPECTED.items():
    path = REPO / relative
    if not path.is_file() or sha256(path) != expected:
        fail(f"identity mismatch: {relative}")

for test in TESTS:
    if (REPO / test).read_bytes() != (ROOT / Path(test).name).read_bytes():
        fail(f"evidence test copy differs: {test}")

status = set(
    subprocess.check_output(
        ["git", "status", "--porcelain=v1"], cwd=REPO, text=True
    ).splitlines()
)
if status != EXPECTED_STATUS:
    fail("repository status differs from frozen Ticket 2C boundary")

completed = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", *TESTS],
    cwd=REPO,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    timeout=120,
    check=False,
)
output = completed.stdout
if completed.returncode != 1:
    fail(f"focused pytest exit was {completed.returncode}, expected intentional RED exit 1")
if "3 failed, 8 passed" not in output:
    fail("focused pytest did not produce exact 3-fail/8-pass RED matrix")
if output.count("FAILED tests/") != 3:
    fail("focused pytest failure count is not exactly three")
for name in EXPECTED_FAILURES:
    if output.count(name) < 2:
        fail(f"expected RED failure missing: {name}")
for forbidden in (
    "test_ticket2c_stage7_request_fixture_bytes_and_admission_are_preserved",
    "test_ticket2c_bridge_preserves_stage7_full_and_unavailable_responses",
    "test_ticket2c_bridge_rejects_route_coupled_response_toxics",
):
    if f"FAILED tests/" in output and f"FAILED tests/" + forbidden in output:
        fail(f"preservation/toxic test failed: {forbidden}")

preserved_log = ROOT / "focused-pytest-red.log"
if not preserved_log.is_file():
    fail("preserved focused RED log is missing")
preserved_output = preserved_log.read_text()
if "3 failed, 8 passed" not in preserved_output:
    fail("preserved focused RED log does not contain the admitted outcome")
for name in EXPECTED_FAILURES:
    if preserved_output.count(name) < 2:
        fail(f"preserved RED failure missing: {name}")

print("STAGE8_TICKET2C_IMPLEMENTATION_RED")
print("TEXT_ONLY_REQUEST_ADMISSION=FAIL_EXPECTED")
print("TEXT_ONLY_IMAGE_SUPPRESSION=FAIL_EXPECTED")
print("TEXT_ONLY_SUCCESS_RESPONSE_ADMISSION=FAIL_EXPECTED")
print("STAGE7_FULL_REQUEST=PRESERVED")
print("STAGE7_UNAVAILABLE_REQUEST=PRESERVED")
print("STAGE7_FULL_RESPONSE=PRESERVED")
print("STAGE7_UNAVAILABLE_RESPONSE=PRESERVED")
print("ROUTE_COUPLED_TOXICS=DEFINED_AND_PASSING")
print("FOCUSED_TESTS=3_FAILED_8_PASSED")
print("CANONICAL_RED_REPLAY=SEMANTIC_EXACT")
print("PROVIDER_EXECUTIONS=0")
print("PRODUCTION_FILES_CHANGED=0")
print("PRE_EXISTING_DIRTY_STATE=BYTE_IDENTICAL")
print("IMPLEMENTATION_GAPS=3")
print("ADAPTER_TEXT_ONLY_BRANCH=MISSING")
print("ADAPTER_ZERO_IMAGE_TEXT_ONLY_BRANCH=MISSING")
print("BRIDGE_NOT_REQUESTED_SUCCESS_BRANCH=MISSING")
print("PERSISTENT_WORKER=OUT_OF_SCOPE")
print("PRODUCTION_IMPLEMENTATION=NOT_AUTHORIZED")
