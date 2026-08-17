#!/usr/bin/env python3
"""Canonical provider-free verifier for Ticket 2A Amendment 1."""

from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent
AMENDMENT_NAME = (
    "ENGAV3D-STAGE8-TICKET-2A-AMENDMENT-1-EXPLICIT-TEXT-ONLY-MAILBOX-BRANCH.md"
)
TEXT_FIXTURE_NAME = (
    "ENGAV3D-STAGE8-TICKET-2A-AMENDMENT-1-MANDATORY-TEXT-ONLY-REQUEST.json"
)
AMENDMENT_SHA256 = "01b14eb7eb0c0c693fc63f590e01748bab645e16cce4a36e13dcd476a0c94f03"
TEXT_FIXTURE_SHA256 = "5a5f856dcc157f885343c8d08bcfd9ebbf826a404bbab5fcf91c2a87fa69c4db"
STAGE7_FULL_SHA256 = "5701b7d0d1e11c1e9307ccb54ad85752166ec7a6e51bb3017180c7c26da511b7"

REQUEST_KEYS = {
    "additional_context",
    "game_state",
    "player_input",
    "request_id",
    "timestamp",
}
CURRENT_CONTEXT_KEYS = {"client_request_id", "companion_ref", "perception"}
TEXT_CONTEXT_KEYS = {"client_request_id", "companion_ref", "routing_mode"}
PERCEPTION_KEYS = {
    "schema",
    "perception_state",
    "capture_id",
    "capture_event",
    "capture_phase",
    "captured_at",
    "project_id",
    "scene_path",
    "snapshot",
    "viewport",
    "unavailable_reason",
}
VIEWPORT_KEYS = {
    "availability",
    "image_path",
    "image_sha256",
    "media_type",
    "width",
    "height",
    "reason",
}
TEXT_FORBIDDEN_KEYS = {
    "perception",
    "capture_id",
    "captured_at",
    "snapshot",
    "viewport",
    "image_path",
    "image_sha256",
}
REQUEST_ID = re.compile(r"req_[0-9a-f]{32}")
CLIENT_ID = re.compile(r"dragon3d_[0-9a-f]{32}_[1-9][0-9]*")
CAPTURE_ID = re.compile(r"cap_[0-9a-f]{32}_[1-9][0-9]*")
SHA256 = re.compile(r"[0-9a-f]{64}")


class ContractReject(ValueError):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_sidecar(name: str, expected: str) -> None:
    sidecar = ROOT / f"{name}.sha256"
    if sidecar.read_text(encoding="utf-8") != f"{expected}  {name}\n":
        raise AssertionError(f"sidecar mismatch: {name}")


def finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def forbidden_keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key in TEXT_FORBIDDEN_KEYS:
                found.add(key)
            found.update(forbidden_keys(child))
    elif isinstance(value, list):
        for child in value:
            found.update(forbidden_keys(child))
    return found


def validate_viewport(viewport: Any, state: str) -> None:
    if not isinstance(viewport, dict) or set(viewport) != VIEWPORT_KEYS:
        raise ContractReject("viewport exact keys differ")
    if state == "full":
        if viewport["availability"] != "available":
            raise ContractReject("full viewport is not available")
        if not isinstance(viewport["image_path"], str) or not viewport["image_path"]:
            raise ContractReject("full image_path missing")
        if not isinstance(viewport["image_sha256"], str) or not SHA256.fullmatch(
            viewport["image_sha256"]
        ):
            raise ContractReject("full image_sha256 invalid")
        if viewport["media_type"] != "image/png":
            raise ContractReject("full media type differs")
        if not isinstance(viewport["width"], int) or viewport["width"] <= 0:
            raise ContractReject("full width invalid")
        if not isinstance(viewport["height"], int) or viewport["height"] <= 0:
            raise ContractReject("full height invalid")
        if viewport["reason"] is not None:
            raise ContractReject("full reason must be null")
    else:
        if viewport["availability"] != "unavailable":
            raise ContractReject("unavailable viewport availability differs")
        for key in ("image_path", "image_sha256", "media_type", "width", "height"):
            if viewport[key] is not None:
                raise ContractReject(f"unavailable {key} must be null")
        if viewport["reason"] != "capture_failed":
            raise ContractReject("unavailable reason differs")


def validate_stage7_perception(value: Any) -> str:
    if not isinstance(value, dict) or set(value) != PERCEPTION_KEYS:
        raise ContractReject("perception exact keys differ")
    if value["schema"] != "engain.runtime_perception.v1":
        raise ContractReject("perception schema differs")
    state = value["perception_state"]
    if state not in {"full", "unavailable"}:
        raise ContractReject("Stage 7 state is not full or unavailable")
    if not isinstance(value["capture_id"], str) or not CAPTURE_ID.fullmatch(
        value["capture_id"]
    ):
        raise ContractReject("capture_id invalid")
    if value["capture_event"] != "message_received":
        raise ContractReject("capture_event differs")
    if value["capture_phase"] != "pre_dispatch_player_view.v1":
        raise ContractReject("capture_phase differs")
    if not finite_number(value["captured_at"]) or float(value["captured_at"]) <= 0:
        raise ContractReject("captured_at invalid")
    if value["project_id"] != "godot_3d_avatar":
        raise ContractReject("project differs")
    if value["scene_path"] != "res://scenes/Main.tscn":
        raise ContractReject("scene differs")
    validate_viewport(value["viewport"], state)
    if state == "full":
        if value["unavailable_reason"] is not None:
            raise ContractReject("full unavailable_reason must be null")
        if not isinstance(value["snapshot"], dict):
            raise ContractReject("full snapshot missing")
    else:
        if value["snapshot"] is not None:
            raise ContractReject("unavailable snapshot must be null")
        if value["unavailable_reason"] != "capture_failed":
            raise ContractReject("unavailable failure semantics differ")
    return state


def validate_request(payload: Any) -> tuple[str, str | None]:
    if not isinstance(payload, dict) or set(payload) != REQUEST_KEYS:
        raise ContractReject("request exact keys differ")
    if not isinstance(payload["request_id"], str) or not REQUEST_ID.fullmatch(
        payload["request_id"]
    ):
        raise ContractReject("request_id invalid")
    if not isinstance(payload["player_input"], str) or not payload["player_input"].strip():
        raise ContractReject("player_input invalid")
    if not isinstance(payload["game_state"], dict):
        raise ContractReject("game_state invalid")
    if not finite_number(payload["timestamp"]):
        raise ContractReject("timestamp invalid")
    context = payload["additional_context"]
    if not isinstance(context, dict):
        raise ContractReject("additional_context invalid")
    if context.get("companion_ref") != "hermes_b":
        raise ContractReject("companion_ref differs")
    client_id = context.get("client_request_id")
    if not isinstance(client_id, str) or not CLIENT_ID.fullmatch(client_id):
        raise ContractReject("client_request_id invalid")

    keys = set(context)
    if keys == CURRENT_CONTEXT_KEYS:
        state = validate_stage7_perception(context["perception"])
        return "current_perception", state
    if keys == TEXT_CONTEXT_KEYS:
        if context["routing_mode"] != "text_only":
            raise ContractReject("unknown routing_mode")
        forbidden = forbidden_keys(payload)
        if forbidden:
            raise ContractReject(f"text-only forbidden keys present: {sorted(forbidden)}")
        return "text_only", None
    raise ContractReject("no admitted branch matches additional_context")


def must_reject(payload: dict[str, Any], label: str) -> None:
    try:
        validate_request(payload)
    except ContractReject:
        return
    raise AssertionError(f"{label} unexpectedly validated")


def main() -> int:
    amendment = ROOT / AMENDMENT_NAME
    text_fixture_path = ROOT / TEXT_FIXTURE_NAME
    if digest(amendment) != AMENDMENT_SHA256:
        raise AssertionError("amendment hash differs")
    require_sidecar(AMENDMENT_NAME, AMENDMENT_SHA256)
    if digest(text_fixture_path) != TEXT_FIXTURE_SHA256:
        raise AssertionError("text-only fixture hash differs")
    require_sidecar(TEXT_FIXTURE_NAME, TEXT_FIXTURE_SHA256)

    raw_text = text_fixture_path.read_bytes()
    text_request = json.loads(raw_text)
    canonical = (
        json.dumps(text_request, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")
    if raw_text != canonical:
        raise AssertionError("text-only fixture is not exact canonical JSON")
    if validate_request(text_request) != ("text_only", None):
        raise AssertionError("text-only fixture branch differs")

    text_context = text_request["additional_context"]
    if set(text_context) != TEXT_CONTEXT_KEYS:
        raise AssertionError("text-only exact context differs")
    if forbidden_keys(text_request):
        raise AssertionError("text-only fixture contains forbidden fields")

    full_path = ROOT / "stage7-full-request-unchanged.json"
    if digest(full_path) != STAGE7_FULL_SHA256:
        raise AssertionError("sealed Stage 7 full request bytes changed")
    full_request = json.loads(full_path.read_bytes())
    if validate_request(full_request) != ("current_perception", "full"):
        raise AssertionError("Stage 7 full request did not validate unchanged")
    if "routing_mode" in full_request["additional_context"]:
        raise AssertionError("Stage 7 full request gained routing_mode")

    unavailable_path = ROOT / "stage7-unavailable-request-unchanged.json"
    unavailable_request = json.loads(unavailable_path.read_bytes())
    if validate_request(unavailable_request) != ("current_perception", "unavailable"):
        raise AssertionError("Stage 7 unavailable request did not validate")
    if "routing_mode" in unavailable_request["additional_context"]:
        raise AssertionError("Stage 7 unavailable request gained routing_mode")

    mixed = copy.deepcopy(text_request)
    mixed["additional_context"]["perception"] = copy.deepcopy(
        unavailable_request["additional_context"]["perception"]
    )
    must_reject(mixed, "text_only_and_perception")

    untagged = copy.deepcopy(text_request)
    del untagged["additional_context"]["routing_mode"]
    must_reject(untagged, "untagged_no_perception")

    unknown = copy.deepcopy(text_request)
    unknown["additional_context"]["routing_mode"] = "unknown"
    must_reject(unknown, "unknown_routing_mode")

    current_tag = copy.deepcopy(text_request)
    current_tag["additional_context"]["routing_mode"] = "current_perception"
    must_reject(current_tag, "routing_mode_current_perception")

    image_key = copy.deepcopy(text_request)
    image_key["game_state"]["image_path"] = "snapshots/forbidden.png"
    must_reject(image_key, "text_only_image_path")

    structured = copy.deepcopy(unavailable_request)
    structured["additional_context"]["perception"]["perception_state"] = "structured_only"
    must_reject(structured, "non_stage7_structured_only_state")

    if text_context.get("routing_mode") != "text_only":
        raise AssertionError("text-only tag is not explicit")
    if "perception" in text_context:
        raise AssertionError("text-only perception is present")

    print("STAGE8_TICKET2A_AMENDMENT1_ADMITTED")
    print("TEXT_ONLY_EXACT_JSON=CONSTRUCTIBLE")
    print("TEXT_ONLY_TAG=EXPLICIT")
    print("TEXT_ONLY_PERCEPTION=ABSENT")
    print("TEXT_ONLY_CAPTURE_ID=ABSENT")
    print("TEXT_ONLY_IMAGE_FIELDS=FORBIDDEN")
    print("TEXT_ONLY_AND_PERCEPTION=REJECTED")
    print("UNTAGGED_NO_PERCEPTION=REJECTED")
    print("UNKNOWN_ROUTING_MODE=REJECTED")
    print("STAGE7_FULL_FIXTURE=ACCEPTED_UNCHANGED")
    print("STAGE7_UNAVAILABLE_FIXTURE=ACCEPTED_UNCHANGED")
    print("INTENTIONAL_TEXT_ONLY_VS_CAPTURE_FAILURE=DISTINCT")
    print("PROVIDER_EXECUTIONS=0")
    print("RUNTIME_IMPLEMENTATION=NOT_AUTHORIZED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, ContractReject, json.JSONDecodeError) as exc:
        print(f"STAGE8_TICKET2A_AMENDMENT1_REJECTED: {exc}", file=sys.stderr)
        raise SystemExit(1)
