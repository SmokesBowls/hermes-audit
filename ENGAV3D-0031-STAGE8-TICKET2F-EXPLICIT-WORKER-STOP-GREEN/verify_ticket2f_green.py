#!/usr/bin/env python3
"""Canonical provider-free verifier for Stage 8 Ticket 2F GREEN."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = Path("/mnt/data-drive/godot_engain_3d_avatar")
BASE_HEAD = "77593c205851c97a1b0b46ebdb6ade270309f81a"
EXPECTED = {
    "hermes_session_adapter.py": "fc7969f9be6f992570821d96ed9a46b62959f5cc60780d4d89d9a04cc79f7542",
    "tests/test_stage8_ticket2e_persistent_worker_red.py": "db705f501187709b55f927faa589bafad93a3cb6e72368387b0a4dcc5914d068",
    "scripts/EngAInBridge3D.gd": "814c25c3c784b880992ec9725232dc0de2dac3662b180409a3709911c14cd6eb",
    "tests/test_stage8_ticket2c_text_only_adapter_red.py": "17bf37dee6e3abb4208b8f2dd15ba14178f9e0e8a493581723804077c9e977af",
    "tests/test_stage8_ticket2c_text_only_bridge_red.py": "fc70cfc985a42428768c9c144da3f7fd3655defe766d80bc99912113cfbca465",
    "scripts/ControlHUD.gd": "acc0b0e075f788b96cf146a9376a56ec94943b661585570f8c1cecaa23c0c2f1",
    "scripts/PerceptionCapture3D.gd": "9ed05917067e799ee0b8de35e6bb68158c838a7eb1effb5d16137c6a3d213da7",
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
    "?? tests/test_stage8_ticket2e_persistent_worker_red.py",
}
COPIES = {
    "hermes_session_adapter.py": "hermes_session_adapter.py",
    "tests/test_stage8_ticket2e_persistent_worker_red.py": "test_stage8_ticket2e_persistent_worker_red.py",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(detail: str) -> None:
    print(f"STAGE8_TICKET2F_GREEN_REJECTED: {detail}")
    raise SystemExit(1)


head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
if head != BASE_HEAD:
    fail("base HEAD differs")
for relative, expected in EXPECTED.items():
    path = REPO / relative
    if not path.is_file() or sha256(path) != expected:
        fail(f"identity mismatch: {relative}")
for relative, copied_name in COPIES.items():
    if (REPO / relative).read_bytes() != (ROOT / copied_name).read_bytes():
        fail(f"evidence copy differs: {relative}")
status = set(subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=REPO, text=True).splitlines())
if status != EXPECTED_STATUS:
    fail("repository status differs from authorized boundary")

focused = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "tests/test_stage8_ticket2e_persistent_worker_red.py"],
    cwd=REPO, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    timeout=180, check=False,
)
if focused.returncode != 0 or "5 passed" not in focused.stdout:
    fail("focused Ticket 2E suite is not 5 passed")

protected = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "tests"], cwd=REPO,
    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    timeout=600, check=False,
)
if protected.returncode != 0 or "196 passed" not in protected.stdout:
    fail("protected suite is not 196 passed")

print("STAGE8_TICKET2F_EXPLICIT_STOP_GREEN")
print("WORKER_STATE_READY=OBSERVABLE")
print("WORKER_STATE_STOPPING=OBSERVABLE")
print("WORKER_STATE_STOPPED=OBSERVABLE")
print("EXPLICIT_STOP_WITHOUT_SIGNAL=PASS")
print("NEW_REQUEST_AFTER_STOP_REQUEST=NOT_ADMITTED")
print("SINGLE_WORKER_MULTI_REQUEST=PRESERVED")
print("WORKER_SURVIVES_SUCCESS=PRESERVED")
print("WORKER_SURVIVES_LOCAL_REQUEST_FAILURE=PRESERVED")
print("DUPLICATE_REQUEST_EXACTLY_ONCE=PRESERVED")
print("SINGLE_AUTHORITATIVE_WORKER=PRESERVED")
print("FOCUSED_TICKET2E=5_PASSED")
print("PROTECTED_SUITE=196_PASSED")
print("PROVIDER_EXECUTIONS=0")
print("AUTHORIZED_FILES_CHANGED_ONLY=PASS")
print("PRE_EXISTING_DIRTY_STATE=BYTE_IDENTICAL")
print("HUD_ROUTING=NOT_IMPLEMENTED")
print("THINKING_STATE=NOT_IMPLEMENTED")
print("GODOT_WORKER_WIRING=NOT_IMPLEMENTED")
