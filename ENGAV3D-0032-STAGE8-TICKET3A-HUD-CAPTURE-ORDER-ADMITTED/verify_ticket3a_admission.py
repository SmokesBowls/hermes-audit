#!/usr/bin/env python3
"""Canonical admission verifier for Stage 8 Ticket 3A.

This verifier executes the normative route/order/correlation matrix independently of
runtime implementation and fails closed if the frozen authorities or contract drift.
"""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIT = ROOT.parent
REPO = Path("/mnt/data-drive/godot_engain_3d_avatar")
CONTRACT_NAME = "ENGAV3D-STAGE8-TICKET-3A-HUD-STATUS-CAPTURE-ORDER-RECONCILIATION.md"
CONTRACT_SHA256 = "ff5ef62f696ab0361f49edf61e856b2acc1ee029a5f570ac7624fcd22c868eb3"
TICKET1_SHA256 = "8d569dac608f268405630b36816cb5d8514fd6d74dc784840c4110218f2a880a"
STAGE7_SHA256 = "277a957c99c9c3ae231bcf4964141a5f736580e165e285e077f8cee0de352d74"
TICKET2F_SIDECAR_SHA256 = "7f7fe8b649c4516006a7fc50860c1f015943a09ca761c1782b9ffd446cb90425"
BASE_HEAD = "77593c205851c97a1b0b46ebdb6ade270309f81a"

PRESERVED = {
    "hermes_session_adapter.py": "fc7969f9be6f992570821d96ed9a46b62959f5cc60780d4d89d9a04cc79f7542",
    "scripts/EngAInBridge3D.gd": "814c25c3c784b880992ec9725232dc0de2dac3662b180409a3709911c14cd6eb",
    "scripts/ControlHUD.gd": "acc0b0e075f788b96cf146a9376a56ec94943b661585570f8c1cecaa23c0c2f1",
    "scripts/PerceptionCapture3D.gd": "9ed05917067e799ee0b8de35e6bb68158c838a7eb1effb5d16137c6a3d213da7",
    "scripts/DragonAvatar3D.gd": "ef667b7eb63c4689f23888cf28ff25891fb459f2ccc6e6f99c4febc75dbbcf38",
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
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reject(detail: str) -> None:
    print(f"STAGE8_TICKET3A_ADMISSION_REJECTED: {detail}")
    raise SystemExit(1)


def require(condition: bool, detail: str) -> None:
    if not condition:
        reject(detail)


@dataclass(frozen=True)
class Scenario:
    name: str
    route: str
    internal_looking: bool = False
    visible_before_capture: bool = False
    capture_attempted: bool = False
    capture_identity: bool = False
    capture_valid: bool = True
    capture_excluded_surface: bool = False
    publication_committed: bool = False
    thinking_visible: bool = False
    active_request_id: str = "req_active"
    active_client_request_id: str = "client_active"
    response_request_id: str | None = None
    response_client_request_id: str | None = None
    terminal: bool = False
    status_cleared: bool = False


def admitted(s: Scenario) -> bool:
    if s.route not in {"current_perception", "text_only"}:
        return False
    if s.route == "text_only":
        if s.internal_looking or s.capture_attempted or s.capture_identity:
            return False
    else:
        if not s.capture_attempted or not s.capture_identity or not s.capture_valid:
            return False
        if s.visible_before_capture and not s.capture_excluded_surface:
            return False
    if s.thinking_visible and not s.publication_committed:
        return False
    response_present = s.response_request_id is not None or s.response_client_request_id is not None
    correlated = (
        response_present
        and s.response_request_id == s.active_request_id
        and s.response_client_request_id == s.active_client_request_id
    )
    if s.status_cleared and not (correlated or s.terminal):
        return False
    if s.terminal and s.thinking_visible and not s.status_cleared:
        return False
    return True


contract = ROOT / CONTRACT_NAME
require(contract.is_file() and digest(contract) == CONTRACT_SHA256, "contract identity differs")
require((AUDIT / CONTRACT_NAME).read_bytes() == contract.read_bytes(), "root contract copy differs")
require(digest(AUDIT / "ENGAV3D-STAGE8-TICKET-1-PERSISTENT-WORKER-ROUTING-BOUNDARY.md") == TICKET1_SHA256, "Ticket 1 authority differs")
require(digest(AUDIT / "ENGAV3D-0001-AMENDMENT-5-STAGE7-LIVE-PERCEPTION-LIFECYCLE.md") == STAGE7_SHA256, "Stage 7 authority differs")
require(digest(AUDIT / "ENGAV3D-0031-STAGE8-TICKET2F-EXPLICIT-WORKER-STOP-GREEN.sha256") == TICKET2F_SIDECAR_SHA256, "Ticket 2F authority differs")
require(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip() == BASE_HEAD, "repository HEAD differs")
for relative, expected in PRESERVED.items():
    require(digest(REPO / relative) == expected, f"runtime identity differs: {relative}")
status = set(subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=REPO, text=True).splitlines())
require(status == EXPECTED_STATUS, "repository status differs")

matrix = {
    "current_internal_looking": (
        Scenario("current_internal_looking", "current_perception", True, False, True, True, publication_committed=True), True
    ),
    "visible_hud_before_capture": (
        Scenario("visible_hud_before_capture", "current_perception", True, True, True, True), False
    ),
    "thinking_before_capture": (
        Scenario("thinking_before_capture", "current_perception", True, True, True, True, thinking_visible=True), False
    ),
    "capture_excluded_future_surface": (
        Scenario("capture_excluded_future_surface", "current_perception", True, True, True, True, True, True, True), True
    ),
    "current_capture_commit_thinking": (
        Scenario("current_capture_commit_thinking", "current_perception", True, False, True, True, publication_committed=True, thinking_visible=True), True
    ),
    "current_skips_capture": (
        Scenario("current_skips_capture", "current_perception", True, False, False, False), False
    ),
    "valid_unavailable_commit": (
        Scenario("valid_unavailable_commit", "current_perception", True, False, True, True, publication_committed=True, thinking_visible=True), True
    ),
    "text_only_invokes_capture": (
        Scenario("text_only_invokes_capture", "text_only", capture_attempted=True, capture_identity=True), False
    ),
    "text_only_allocates_capture_identity": (
        Scenario("text_only_allocates_capture_identity", "text_only", capture_identity=True), False
    ),
    "text_only_commit_thinking": (
        Scenario("text_only_commit_thinking", "text_only", publication_committed=True, thinking_visible=True), True
    ),
    "capture_failure_thinking": (
        Scenario("capture_failure_thinking", "current_perception", True, False, True, True, False, publication_committed=False, thinking_visible=True, terminal=True), False
    ),
    "publication_failure_thinking": (
        Scenario("publication_failure_thinking", "text_only", publication_committed=False, thinking_visible=True, terminal=True), False
    ),
    "wrong_request_clears": (
        Scenario("wrong_request_clears", "text_only", publication_committed=True, thinking_visible=True, response_request_id="req_wrong", response_client_request_id="client_active", status_cleared=True), False
    ),
    "wrong_client_clears": (
        Scenario("wrong_client_clears", "text_only", publication_committed=True, thinking_visible=True, response_request_id="req_active", response_client_request_id="client_wrong", status_cleared=True), False
    ),
    "old_response_clears_newer": (
        Scenario("old_response_clears_newer", "text_only", publication_committed=True, thinking_visible=True, active_request_id="req_new", active_client_request_id="client_new", response_request_id="req_old", response_client_request_id="client_old", status_cleared=True), False
    ),
    "correlated_response_clears": (
        Scenario("correlated_response_clears", "text_only", publication_committed=True, thinking_visible=True, response_request_id="req_active", response_client_request_id="client_active", terminal=True, status_cleared=True), True
    ),
    "timeout_leaves_status": (
        Scenario("timeout_leaves_status", "text_only", publication_committed=True, thinking_visible=True, terminal=True, status_cleared=False), False
    ),
    "shutdown_leaves_status": (
        Scenario("shutdown_leaves_status", "text_only", publication_committed=True, thinking_visible=True, terminal=True, status_cleared=False), False
    ),
}
for name, (scenario, expected) in matrix.items():
    require(admitted(scenario) is expected, f"matrix contradiction: {name}")

required_contract_tokens = (
    "LOOKING_INTERNAL=ALLOWED_BEFORE_CAPTURE",
    "LOOKING_VISIBLE_IN_CAPTURED_VIEWPORT=FORBIDDEN_BEFORE_CAPTURE",
    "THINKING_BEGINS_AFTER_REQUEST_COMMIT=DEFINED",
    "response for wrong request_id",
    "response for wrong client_request_id",
    "old response after a newer committed submission",
    "Ticket 3A changes no runtime file",
)
contract_text = contract.read_text(encoding="utf-8")
for token in required_contract_tokens:
    require(token in contract_text, f"required contract token absent: {token}")

print("STAGE8_TICKET3A_HUD_CAPTURE_ORDER_ADMITTED")
print("CURRENT_PERCEPTION_INTERNAL_LOOKING=DEFINED")
print("VISIBLE_LOOKING_BEFORE_CAPTURE=FORBIDDEN")
print("CAPTURE_PRECEDES_VISIBLE_HUD_MUTATION=PRESERVED")
print("THINKING_BEGINS_AFTER_REQUEST_COMMIT=DEFINED")
print("TEXT_ONLY_CAPTURE=FORBIDDEN")
print("TEXT_ONLY_THINKING_AFTER_COMMIT=DEFINED")
print("CORRELATED_RESPONSE_CLEARS_STATUS=DEFINED")
print("UNRELATED_RESPONSE_CANNOT_CLEAR_STATUS=DEFINED")
print("TERMINAL_FAILURE_CLEARS_STATUS=DEFINED")
print("FAIL_CLOSED_MATRIX=18_CASES_PASS")
print("STAGE7_CAPTURE_ORDER=UNCHANGED")
print("TICKET1_ROUTING=UNCHANGED")
print("PROVIDER_EXECUTIONS=0")
print("RUNTIME_IMPLEMENTATION=NOT_AUTHORIZED")
