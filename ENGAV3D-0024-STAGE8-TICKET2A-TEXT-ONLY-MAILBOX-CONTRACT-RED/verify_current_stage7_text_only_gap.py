#!/usr/bin/env python3
"""Provider-free RED verifier for the current Stage 7 text-only wire gap."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
PROJECT = Path("/mnt/data-drive/godot_engain_3d_avatar")
ADAPTER_PATH = PROJECT / "hermes_session_adapter.py"
BRIDGE_PATH = PROJECT / "scripts/EngAInBridge3D.gd"
CONTRACT_NAME = (
    "ENGAV3D-STAGE8-TICKET-2A-TEXT-ONLY-MAILBOX-REPRESENTATION-CONTRACT.md"
)
CONTRACT_SHA256 = "8c811933a9d9d6e882db7b9917e8b086a886d0423af7a0483ddd989a1a55d989"
ADAPTER_SHA256 = "f3add4a3011b09c9f88c489b436e4fc5e4751fd18ccb080810cac6ad06869e39"
BRIDGE_SHA256 = "64abb2a0770973cf8519449b918eb84fca6e87c2e5c298df5086c67a5ad18683"

REQUEST_ID = "req_11111111111111111111111111111111"
CLIENT_REQUEST_ID = "dragon3d_22222222222222222222222222222222_1"
CAPTURE_ID = "cap_33333333333333333333333333333333_1"
FIXTURE = (
    "Without using any current image, describe what you remember about the previous "
    "Dragon and the room/environment you saw before this latest scene."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("stage8_ticket2a_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("adapter module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return module


def unavailable_perception() -> dict[str, Any]:
    return {
        "schema": "engain.runtime_perception.v1",
        "perception_state": "unavailable",
        "capture_id": CAPTURE_ID,
        "capture_event": "message_received",
        "capture_phase": "pre_dispatch_player_view.v1",
        "captured_at": 1.0,
        "project_id": "godot_3d_avatar",
        "scene_path": "res://scenes/Main.tscn",
        "snapshot": None,
        "viewport": {
            "availability": "unavailable",
            "image_path": None,
            "image_sha256": None,
            "media_type": None,
            "width": None,
            "height": None,
            "reason": "capture_failed",
        },
        "unavailable_reason": "capture_failed",
    }


def request(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "player_input": FIXTURE,
        "game_state": {},
        "additional_context": context,
        "timestamp": 1.0,
        "request_id": REQUEST_ID,
    }


def base_context() -> dict[str, Any]:
    return {
        "client_request_id": CLIENT_REQUEST_ID,
        "companion_ref": "hermes_b",
    }


def reject(adapter: Any, payload: dict[str, Any], label: str) -> str:
    try:
        adapter._validate_request(payload, validation_time=1.0)
    except Exception as exc:
        return f"{label}=REJECTED:{type(exc).__name__}:{exc}"
    raise AssertionError(f"{label} unexpectedly validated")


def main() -> int:
    if sha256(ROOT / CONTRACT_NAME) != CONTRACT_SHA256:
        raise AssertionError("Ticket 2A contract hash differs")
    sidecar = (ROOT / f"{CONTRACT_NAME}.sha256").read_text(encoding="utf-8")
    if sidecar != f"{CONTRACT_SHA256}  {CONTRACT_NAME}\n":
        raise AssertionError("Ticket 2A contract sidecar differs")
    if sha256(ADAPTER_PATH) != ADAPTER_SHA256:
        raise AssertionError("adapter source hash differs")
    if sha256(BRIDGE_PATH) != BRIDGE_SHA256:
        raise AssertionError("bridge source hash differs")

    module = load_adapter()
    provider_calls: list[str] = []

    def forbidden(name: str) -> Callable[..., Any]:
        def fail(*args: Any, **kwargs: Any) -> Any:
            provider_calls.append(name)
            raise AssertionError(f"forbidden provider execution: {name}")

        return fail

    module.HermesCLIClient._run_bounded = forbidden("HermesCLIClient._run_bounded")
    module.HermesCLIClient.chat = forbidden("HermesCLIClient.chat")
    module.subprocess.Popen = forbidden("subprocess.Popen")

    with tempfile.TemporaryDirectory(prefix="engav3d-ticket2a-red-") as temporary:
        adapter = module.HermesSessionAdapter(
            module.AdapterConfig(project_dir=Path(temporary)),
            director_bridge=object(),
        )

        omitted_context = base_context()
        omitted = reject(adapter, request(omitted_context), "perception_omitted")

        null_context = base_context()
        null_context["perception"] = None
        null_value = reject(adapter, request(null_context), "perception_null")

        text_state = unavailable_perception()
        text_state["perception_state"] = "text_only"
        text_context = base_context()
        text_context["perception"] = text_state
        unknown_state = reject(adapter, request(text_context), "text_only_state")

        context_discriminator = base_context()
        context_discriminator["perception"] = unavailable_perception()
        context_discriminator["routing_mode"] = "text_only"
        unknown_context_key = reject(
            adapter,
            request(context_discriminator),
            "context_routing_mode",
        )

        top_level = request(
            {
                **base_context(),
                "perception": unavailable_perception(),
            }
        )
        top_level["routing_mode"] = "text_only"
        unknown_request_key = reject(adapter, top_level, "request_routing_mode")

        unavailable_payload = request(
            {
                **base_context(),
                "perception": unavailable_perception(),
            }
        )
        validated = adapter._validate_request(unavailable_payload, validation_time=1.0)

    if validated.perception.requested_state != "unavailable":
        raise AssertionError("unavailable control did not validate as unavailable")
    if validated.perception.capture_id != CAPTURE_ID:
        raise AssertionError("unavailable control did not retain capture identity")
    if provider_calls:
        raise AssertionError(f"provider execution observed: {provider_calls}")

    bridge = BRIDGE_PATH.read_text(encoding="utf-8")
    required_bridge_literals = (
        '"client_request_id",\n\t"companion_ref",\n\t"perception",',
        '"perception": perception',
        '"capture_id",',
        '"captured_at",',
        '"viewport",',
    )
    if not all(literal in bridge for literal in required_bridge_literals):
        raise AssertionError("bridge exact-key evidence differs")
    if '"routing_mode"' in bridge:
        raise AssertionError("bridge unexpectedly contains routing_mode")

    observations = {
        "perception_omitted": omitted,
        "perception_null": null_value,
        "text_only_state": unknown_state,
        "context_routing_mode": unknown_context_key,
        "request_routing_mode": unknown_request_key,
        "unavailable_control": "ACCEPTED_WITH_CAPTURE_ID_AND_CAPTURE_FAILURE_SEMANTICS",
        "provider_executions": 0,
    }
    print(json.dumps(observations, indent=2, sort_keys=True))
    print()
    print("STAGE8_TEXT_ONLY_MAILBOX_CONTRACT_GAP")
    print("route=text_only")
    print("capture_attempted=false")
    print("capture_id=FORBIDDEN_BY_TICKET1_BUT_REQUIRED_BY_CURRENT_SCHEMA")
    print("image_attachment_permitted=false")
    print("intentional_absence_distinct_from_capture_failure=NOT_REPRESENTABLE")
    print("stage7_current_perception_representation=UNCHANGED")
    print("provider_executions=0")
    print("runtime_implementation=NOT_AUTHORIZED")
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"STAGE8_TICKET2A_VERIFIER_INTEGRITY_FAILURE: {exc}", file=sys.stderr)
        raise SystemExit(2)
