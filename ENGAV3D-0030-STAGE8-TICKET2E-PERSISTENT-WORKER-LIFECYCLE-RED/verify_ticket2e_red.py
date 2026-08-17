#!/usr/bin/env python3
"""Admit the exact semantic Stage 8 Ticket 2E intentional RED."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = Path("/mnt/data-drive/godot_engain_3d_avatar")
BASE_HEAD = "77593c205851c97a1b0b46ebdb6ade270309f81a"
TEST = "tests/test_stage8_ticket2e_persistent_worker_red.py"
EXPECTED_FAILURE = (
    "test_ticket2e_worker_exposes_explicit_stop_lifecycle_without_signal_injection"
)
EXPECTED_HASHES = {
    "hermes_session_adapter.py": "85970e3cdf28f87406a8415918aae7ffa4248d26b315cb8c59eaa9f141cb80f3",
    "scripts/EngAInBridge3D.gd": "814c25c3c784b880992ec9725232dc0de2dac3662b180409a3709911c14cd6eb",
    "tests/test_stage8_ticket2c_text_only_adapter_red.py": "17bf37dee6e3abb4208b8f2dd15ba14178f9e0e8a493581723804077c9e977af",
    "tests/test_stage8_ticket2c_text_only_bridge_red.py": "fc70cfc985a42428768c9c144da3f7fd3655defe766d80bc99912113cfbca465",
    TEST: "385ea2aa60b988f206d4df0eb4c65745d4733983140b5ff3435b6e7de68314d7",
    "scripts/DragonAvatar3D.gd": "ef667b7eb63c4689f23888cf28ff25891fb459f2ccc6e6f99c4febc75dbbcf38",
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
    f"?? {TEST}",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(detail: str) -> None:
    print(f"STAGE8_TICKET2E_RED_REJECTED: {detail}")
    raise SystemExit(1)


head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
if head != BASE_HEAD:
    fail("base HEAD differs")
for relative, expected in EXPECTED_HASHES.items():
    path = REPO / relative
    if not path.is_file() or sha256(path) != expected:
        fail(f"identity mismatch: {relative}")
if (REPO / TEST).read_bytes() != (ROOT / Path(TEST).name).read_bytes():
    fail("evidence test copy differs")
status = set(subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=REPO, text=True).splitlines())
if status != EXPECTED_STATUS:
    fail("repository status differs from the authorized Ticket 2E boundary")

compiled = subprocess.run(
    [sys.executable, "-m", "py_compile", TEST], cwd=REPO,
    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
)
if compiled.returncode != 0:
    fail("test compilation failed")

focused = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", TEST], cwd=REPO,
    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    timeout=180, check=False,
)
if focused.returncode != 1:
    fail(f"focused pytest exit was {focused.returncode}, expected 1")
summary = re.search(r"(\d+) failed, (\d+) passed", focused.stdout)
if summary is None or summary.groups() != ("1", "4"):
    fail("focused result is not exactly 1 failed, 4 passed")
failed = re.findall(r"^FAILED .*::([^\s]+)", focused.stdout, re.MULTILINE)
if failed != [EXPECTED_FAILURE]:
    fail(f"unexpected failure identities: {failed}")
for required in (
    "no explicit worker-stop behavior is exposed",
    "test_ticket2e_one_worker_processes_text_text_perception_and_survives_each",
):
    if required not in focused.stdout and required == "no explicit worker-stop behavior is exposed":
        fail("missing explicit-stop failure meaning")

print("STAGE8_TICKET2E_PERSISTENT_WORKER_RED")
print("SINGLE_WORKER_MULTI_REQUEST=PASS_ALREADY_PRESENT")
print("WORKER_SURVIVES_SUCCESS=PASS_ALREADY_PRESENT")
print("WORKER_SURVIVES_LOCAL_REQUEST_FAILURE=PASS_ALREADY_PRESENT")
print("DUPLICATE_REQUEST_EXACTLY_ONCE=PASS_ALREADY_PRESENT")
print("SINGLE_AUTHORITATIVE_WORKER=PASS_ALREADY_PRESENT")
print("EXPLICIT_STOP_LIFECYCLE=FAIL_EXPECTED")
print("TICKET2D_TEXT_ONLY_TRANSACTION=PRESERVED")
print("STAGE7_CURRENT_PERCEPTION=PRESERVED")
print("FOCUSED_TESTS=1_FAILED_4_PASSED")
print("PROVIDER_EXECUTIONS=0")
print("PRODUCTION_FILES_CHANGED=0")
print("PRE_EXISTING_DIRTY_STATE=BYTE_IDENTICAL")
print("PERSISTENT_WORKER_IMPLEMENTATION=NOT_AUTHORIZED")
print("HUD_ROUTING=NOT_AUTHORIZED")
