#!/usr/bin/env python3
"""Canonical provider-free verifier for Ticket 2B Amendment 1."""

from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent
AMENDMENT_NAME = (
    "ENGAV3D-STAGE8-TICKET-2B-AMENDMENT-1-"
    "SUCCESSFUL-NO-PERCEPTION-RESULT-BRANCH.md"
)
TEXT_RESPONSE_NAME = (
    "ENGAV3D-STAGE8-TICKET-2B-AMENDMENT-1-SUCCESSFUL-TEXT-ONLY-RESPONSE.json"
)
AMENDMENT_SHA256 = "1a70715ff351818d63e0f507214d459e4bda154d0405952dadf1e9f28ab25d41"
TEXT_RESPONSE_SHA256 = "63fb4d28cdf03c0f4f6f8c39bc29ce59005a9de42ffde0ed2a94fc0150738d2b"
TEXT_REQUEST_SHA256 = "5a5f856dcc157f885343c8d08bcfd9ebbf826a404bbab5fcf91c2a87fa69c4db"
FULL_REQUEST_SHA256 = "5701b7d0d1e11c1e9307ccb54ad85752166ec7a6e51bb3017180c7c26da511b7"
FULL_RESPONSE_SHA256 = "5953bce251e8a8f684a175d5b43f13a82dcdf9d9c926f9aded127414472f35ad"
UNAVAILABLE_REQUEST_SHA256 = "b739f1658018611791c770eb869e8d116dbc112c2965d9219853f38d1753dd34"
UNAVAILABLE_RESPONSE_SHA256 = "dc1a9a8e4b847f9531c0343b9e93b5e5ce470971498bc5f735c8a3c570ad3c00"

REQUEST_KEYS = {
    "request_id",
    "player_input",
    "game_state",
    "timestamp",
    "additional_context",
}
RESPONSE_KEYS = {
    "request_id",
    "client_request_id",
    "narrative_response",
    "action_type",
    "state_changes",
    "director_analysis",
    "reasoning",
    "entropy_impact",
    "timestamp",
    "provider_session_ref",
    "perception_result",
}
PROVIDER_KEYS = {"companion_ref", "provider", "model", "session_id"}
PERCEPTION_RESULT_KEYS = {
    "schema",
    "requested_state",
    "effective_state",
    "capture_id",
    "capture_event",
    "capture_phase",
    "captured_at",
    "metadata_sha256",
    "image_sha256",
    "structured_snapshot_supplied",
    "viewport_image_attached",
    "failure_code",
}
PROVIDER_REF = {
    "companion_ref": "hermes_b",
    "provider": "openai-codex",
    "model": "gpt-5.6-sol",
    "session_id": "20260731_065008_63a62d",
}
NULL_IDENTITY_FIELDS = {
    "capture_id",
    "capture_event",
    "capture_phase",
    "captured_at",
    "metadata_sha256",
    "image_sha256",
    "failure_code",
}
FORBIDDEN_IDENTITY_KEYS = {
    "capture_id",
    "captured_at",
    "snapshot",
    "viewport",
    "image_path",
    "image_sha256",
    "metadata_sha256",
    "capture_event",
    "capture_phase",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_bytes())


def finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def request_route(request: Any) -> str | None:
    if not isinstance(request, dict) or set(request) != REQUEST_KEYS:
        return None
    context = request.get("additional_context")
    if not isinstance(context, dict):
        return None
    if set(context) == {"client_request_id", "companion_ref", "perception"}:
        if context.get("companion_ref") != "hermes_b":
            return None
        return "current_perception"
    if set(context) == {"client_request_id", "companion_ref", "routing_mode"}:
        if (
            context.get("companion_ref") == "hermes_b"
            and context.get("routing_mode") == "text_only"
        ):
            return "text_only"
    return None


def valid_common_response(response: Any, request: Any) -> bool:
    if not isinstance(response, dict) or set(response) != RESPONSE_KEYS:
        return False
    if request_route(request) is None:
        return False
    if response.get("request_id") != request.get("request_id"):
        return False
    context = request["additional_context"]
    if response.get("client_request_id") != context.get("client_request_id"):
        return False
    if not isinstance(response.get("narrative_response"), str):
        return False
    if not response["narrative_response"].strip():
        return False
    if response.get("action_type") != "OBSERVATION":
        return False
    if response.get("state_changes") != {}:
        return False
    if not isinstance(response.get("director_analysis"), str):
        return False
    if not isinstance(response.get("reasoning"), str):
        return False
    if not finite_number(response.get("entropy_impact")):
        return False
    if float(response["entropy_impact"]) != 0.0:
        return False
    if not finite_number(response.get("timestamp")):
        return False
    provider = response.get("provider_session_ref")
    if not isinstance(provider, dict) or set(provider) != PROVIDER_KEYS:
        return False
    if provider != PROVIDER_REF:
        return False
    result = response.get("perception_result")
    if not isinstance(result, dict) or set(result) != PERCEPTION_RESULT_KEYS:
        return False
    if result.get("schema") != "engain.runtime_perception_result.v1":
        return False
    if not isinstance(result.get("structured_snapshot_supplied"), bool):
        return False
    if not isinstance(result.get("viewport_image_attached"), bool):
        return False
    return True


def valid_current_perception_result(request: dict[str, Any], result: dict[str, Any]) -> bool:
    perception = request["additional_context"]["perception"]
    requested_state = result.get("requested_state")
    effective_state = result.get("effective_state")
    if requested_state not in {"full", "structured_only", "unavailable"}:
        return False
    if effective_state not in {"full", "structured_only", "unavailable", "rejected"}:
        return False
    if "not_requested" in {requested_state, effective_state}:
        return False

    if effective_state == "rejected":
        return (
            requested_state == "unavailable"
            and all(result.get(key) is None for key in NULL_IDENTITY_FIELDS)
            and result.get("structured_snapshot_supplied") is False
            and result.get("viewport_image_attached") is False
        )

    if result.get("capture_id") != perception.get("capture_id"):
        return False
    if result.get("capture_event") != "message_received":
        return False
    if result.get("capture_phase") != "pre_dispatch_player_view.v1":
        return False

    if requested_state == "full" and effective_state == "full":
        return (
            isinstance(result.get("captured_at"), (int, float))
            and not isinstance(result.get("captured_at"), bool)
            and isinstance(result.get("metadata_sha256"), str)
            and isinstance(result.get("image_sha256"), str)
            and result.get("structured_snapshot_supplied") is True
            and result.get("viewport_image_attached") is True
            and result.get("failure_code") is None
        )

    if requested_state == "unavailable" and effective_state == "unavailable":
        return (
            result.get("captured_at") == perception.get("captured_at")
            and result.get("metadata_sha256") is None
            and result.get("image_sha256") is None
            and result.get("structured_snapshot_supplied") is False
            and result.get("viewport_image_attached") is False
            and result.get("failure_code") is None
        )
    return False


def hidden_identity_present(response: dict[str, Any]) -> bool:
    def visit(value: Any, *, in_result: bool = False) -> bool:
        if isinstance(value, dict):
            for key, child in value.items():
                child_in_result = in_result or key == "perception_result"
                if key in FORBIDDEN_IDENTITY_KEYS and not child_in_result:
                    return True
                if visit(child, in_result=child_in_result):
                    return True
        elif isinstance(value, list):
            return any(visit(child, in_result=in_result) for child in value)
        return False

    return visit(response)


def valid_text_only_result(response: dict[str, Any], result: dict[str, Any]) -> bool:
    if result.get("requested_state") != "not_requested":
        return False
    if result.get("effective_state") != "not_requested":
        return False
    if not all(result.get(key) is None for key in NULL_IDENTITY_FIELDS):
        return False
    if result.get("structured_snapshot_supplied") is not False:
        return False
    if result.get("viewport_image_attached") is not False:
        return False
    if hidden_identity_present(response):
        return False
    return True


def admitted(request: Any, response: Any) -> bool:
    if not valid_common_response(response, request):
        return False
    route = request_route(request)
    result = response["perception_result"]
    if route == "text_only":
        return valid_text_only_result(response, result)
    if route == "current_perception":
        return valid_current_perception_result(request, result)
    return False


def mutate_result(response: dict[str, Any], **changes: Any) -> dict[str, Any]:
    changed = copy.deepcopy(response)
    changed["perception_result"].update(changes)
    return changed


def main() -> int:
    amendment = ROOT / AMENDMENT_NAME
    text_response_path = ROOT / TEXT_RESPONSE_NAME
    if digest(amendment) != AMENDMENT_SHA256:
        raise AssertionError("amendment hash differs")
    if digest(text_response_path) != TEXT_RESPONSE_SHA256:
        raise AssertionError("text response fixture hash differs")
    if (ROOT / f"{AMENDMENT_NAME}.sha256").read_text(encoding="utf-8") != (
        f"{AMENDMENT_SHA256}  {AMENDMENT_NAME}\n"
    ):
        raise AssertionError("amendment sidecar differs")
    if (ROOT / f"{TEXT_RESPONSE_NAME}.sha256").read_text(encoding="utf-8") != (
        f"{TEXT_RESPONSE_SHA256}  {TEXT_RESPONSE_NAME}\n"
    ):
        raise AssertionError("text response sidecar differs")

    paths = {
        "text_request": ROOT / "fixture-text-only-request.json",
        "full_request": ROOT / "fixture-stage7-full-request-unchanged.json",
        "full_response": ROOT / "fixture-stage7-full-response-unchanged.json",
        "unavailable_request": ROOT / "fixture-current-perception-unavailable-request-unchanged.json",
        "unavailable_response": ROOT / "fixture-current-perception-unavailable-response-unchanged.json",
    }
    expected_hashes = {
        "text_request": TEXT_REQUEST_SHA256,
        "full_request": FULL_REQUEST_SHA256,
        "full_response": FULL_RESPONSE_SHA256,
        "unavailable_request": UNAVAILABLE_REQUEST_SHA256,
        "unavailable_response": UNAVAILABLE_RESPONSE_SHA256,
    }
    for name, path in paths.items():
        if digest(path) != expected_hashes[name]:
            raise AssertionError(f"{name} fixture bytes differ")

    text_request = load(paths["text_request"])
    text_response = load(text_response_path)
    full_request = load(paths["full_request"])
    full_response = load(paths["full_response"])
    unavailable_request = load(paths["unavailable_request"])
    unavailable_response = load(paths["unavailable_response"])

    if request_route(text_request) != "text_only":
        raise AssertionError("text request route differs")
    if request_route(full_request) != "current_perception":
        raise AssertionError("full request route differs")
    if request_route(unavailable_request) != "current_perception":
        raise AssertionError("unavailable request route differs")

    if not admitted(text_request, text_response):
        raise AssertionError("successful text-only response was not admitted")
    if not admitted(full_request, full_response):
        raise AssertionError("sealed Stage 7 full pair was not admitted")
    if not admitted(unavailable_request, unavailable_response):
        raise AssertionError("existing current-perception unavailable pair was not admitted")

    if admitted(text_request, full_response):
        raise AssertionError("text-only request admitted full perception result")
    correlated_full = copy.deepcopy(full_response)
    correlated_full["request_id"] = text_request["request_id"]
    correlated_full["client_request_id"] = text_request["additional_context"]["client_request_id"]
    if admitted(text_request, correlated_full):
        raise AssertionError("correlated text-only request admitted full perception result")

    correlated_unavailable = copy.deepcopy(unavailable_response)
    correlated_unavailable["request_id"] = text_request["request_id"]
    correlated_unavailable["client_request_id"] = text_request["additional_context"]["client_request_id"]
    if admitted(text_request, correlated_unavailable):
        raise AssertionError("text-only request admitted unavailable result")

    correlated_text_for_full = copy.deepcopy(text_response)
    correlated_text_for_full["request_id"] = full_request["request_id"]
    correlated_text_for_full["client_request_id"] = full_request["additional_context"]["client_request_id"]
    if admitted(full_request, correlated_text_for_full):
        raise AssertionError("current-perception request admitted not_requested result")

    toxics = (
        mutate_result(text_response, capture_id="cap_ffffffffffffffffffffffffffffffff_1"),
        mutate_result(text_response, image_sha256="f" * 64),
        mutate_result(text_response, requested_state="not_requested", effective_state="full"),
        mutate_result(text_response, requested_state="full", effective_state="not_requested"),
        mutate_result(text_response, requested_state="unknown"),
        mutate_result(text_response, effective_state="unknown"),
        mutate_result(text_response, capture_event="message_received"),
        mutate_result(text_response, captured_at=1.0),
        mutate_result(text_response, metadata_sha256="e" * 64),
        mutate_result(text_response, structured_snapshot_supplied=True),
        mutate_result(text_response, viewport_image_attached=True),
        mutate_result(text_response, failure_code="PROVIDER_FAILURE"),
    )
    for index, toxic in enumerate(toxics, start=1):
        if admitted(text_request, toxic):
            raise AssertionError(f"text-only toxic result {index} was admitted")

    hidden_top = copy.deepcopy(text_response)
    hidden_top["image_path"] = "/tmp/forbidden.png"
    if admitted(text_request, hidden_top):
        raise AssertionError("hidden top-level image identity was admitted")
    hidden_provider = copy.deepcopy(text_response)
    hidden_provider["provider_session_ref"]["capture_id"] = "cap_hidden"
    if admitted(text_request, hidden_provider):
        raise AssertionError("hidden provider capture identity was admitted")

    routing_tagged = copy.deepcopy(text_response)
    routing_tagged["routing_mode"] = "text_only"
    if admitted(text_request, routing_tagged):
        raise AssertionError("response routing tag was admitted")

    wrong_request_id = copy.deepcopy(text_response)
    wrong_request_id["request_id"] = "req_ffffffffffffffffffffffffffffffff"
    if admitted(text_request, wrong_request_id):
        raise AssertionError("request_id mismatch was admitted")
    wrong_client_id = copy.deepcopy(text_response)
    wrong_client_id["client_request_id"] = "dragon3d_ffffffffffffffffffffffffffffffff_9"
    if admitted(text_request, wrong_client_id):
        raise AssertionError("client_request_id mismatch was admitted")

    if set(text_response) != set(full_response):
        raise AssertionError("top-level response key set changed")
    if set(text_response["perception_result"]) != set(full_response["perception_result"]):
        raise AssertionError("perception-result key set changed")
    if "routing_mode" in text_response:
        raise AssertionError("routing_mode was added to text response")

    required_markers = (
        "STAGE8_TICKET2B_AMENDMENT1_ADMITTED",
        "TEXT_ONLY_SUCCESS_RESULT=REPRESENTABLE",
        "CURRENT_PERCEPTION_FULL=UNCHANGED",
        "CURRENT_PERCEPTION_UNAVAILABLE=UNCHANGED",
        "RESPONSE_ROUTING_MODE=NOT_ADDED",
    )
    amendment_text = amendment.read_text(encoding="utf-8")
    if not all(marker in amendment_text for marker in required_markers):
        raise AssertionError("amendment admission requirements differ")

    print("STAGE8_TICKET2B_AMENDMENT1_ADMITTED")
    print("TEXT_ONLY_SUCCESS_RESULT=REPRESENTABLE")
    print("TEXT_ONLY_REQUEST_CORRELATION=DETERMINISTIC")
    print("TEXT_ONLY_REQUESTED_STATE=not_requested")
    print("TEXT_ONLY_EFFECTIVE_STATE=not_requested")
    print("TEXT_ONLY_CAPTURE_ID=null")
    print("TEXT_ONLY_IMAGE_SHA256=null")
    print("CURRENT_PERCEPTION_FULL=UNCHANGED")
    print("CURRENT_PERCEPTION_UNAVAILABLE=UNCHANGED")
    print("STAGE7_0021_RESPONSE_BYTES=UNCHANGED")
    print("TEXT_ONLY_PLUS_FULL_RESULT=REJECTED")
    print("TEXT_ONLY_PLUS_UNAVAILABLE_RESULT=REJECTED")
    print("CURRENT_PERCEPTION_PLUS_NOT_REQUESTED=REJECTED")
    print("NOT_REQUESTED_PLUS_CAPTURE_ID=REJECTED")
    print("NOT_REQUESTED_PLUS_IMAGE=REJECTED")
    print("NOT_REQUESTED_MIXED_STATE=REJECTED")
    print("UNKNOWN_REQUESTED_STATE=REJECTED")
    print("UNKNOWN_EFFECTIVE_STATE=REJECTED")
    print("HIDDEN_CAPTURE_IMAGE_IDENTITY=REJECTED")
    print("RESPONSE_TOP_LEVEL_KEYS=UNCHANGED")
    print("PERCEPTION_RESULT_KEYS=UNCHANGED")
    print("RESPONSE_ROUTING_MODE=NOT_ADDED")
    print("PROVIDER_EXECUTIONS=0")
    print("RUNTIME_IMPLEMENTATION=NOT_AUTHORIZED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError) as exc:
        print(f"STAGE8_TICKET2B_AMENDMENT1_REJECTED: {exc}", file=sys.stderr)
        raise SystemExit(1)
