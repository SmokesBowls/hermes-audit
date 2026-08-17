#!/usr/bin/env python3
"""Canonical provider-free Ticket 2B response compatibility verifier."""

from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent
CONTRACT_NAME = (
    "ENGAV3D-STAGE8-TICKET-2B-TEXT-ONLY-RESPONSE-WIRE-COMPATIBILITY-CONTRACT.md"
)
CONTRACT_SHA256 = "861e4835b3df3e92e1605d41611895dd3d2455169d509bdbd7d75a44c62676d7"
FIXTURE_A_SHA256 = "5953bce251e8a8f684a175d5b43f13a82dcdf9d9c926f9aded127414472f35ad"
FIXTURE_B_SHA256 = "5a5f856dcc157f885343c8d08bcfd9ebbf826a404bbab5fcf91c2a87fa69c4db"
FIXTURE_C_SHA256 = "a85c9dad2078fda1637b4972516349bbb3892482876d3c6c3e096d7f97a26588"

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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def bridge_accepts(
    response: Any,
    *,
    active_request_id: str,
    active_client_request_id: str,
    active_capture_id: str,
) -> bool:
    if not isinstance(response, dict) or set(response) != RESPONSE_KEYS:
        return False
    if response.get("request_id") != active_request_id:
        return False
    if response.get("client_request_id") != active_client_request_id:
        return False
    if not isinstance(response.get("narrative_response"), str):
        return False
    if not response["narrative_response"].strip():
        return False
    if not isinstance(response.get("director_analysis"), str):
        return False
    if not isinstance(response.get("reasoning"), str):
        return False
    if response.get("action_type") != "OBSERVATION":
        return False
    if response.get("state_changes") != {}:
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
    if result.get("requested_state") not in {"full", "structured_only", "unavailable"}:
        return False
    if result.get("effective_state") not in {
        "full",
        "structured_only",
        "unavailable",
        "rejected",
    }:
        return False
    if not isinstance(result.get("structured_snapshot_supplied"), bool):
        return False
    if not isinstance(result.get("viewport_image_attached"), bool):
        return False
    if result.get("effective_state") == "rejected":
        return True
    return (
        result.get("capture_id") == active_capture_id
        and result.get("capture_event") == "message_received"
        and result.get("capture_phase") == "pre_dispatch_player_view.v1"
    )


def exact_text_request(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    context = value.get("additional_context")
    return (
        isinstance(context, dict)
        and set(context) == {"client_request_id", "companion_ref", "routing_mode"}
        and context.get("routing_mode") == "text_only"
        and "perception" not in context
    )


def main() -> int:
    contract = ROOT / CONTRACT_NAME
    if digest(contract) != CONTRACT_SHA256:
        raise AssertionError("contract hash differs")
    sidecar = ROOT / f"{CONTRACT_NAME}.sha256"
    if sidecar.read_text(encoding="utf-8") != f"{CONTRACT_SHA256}  {CONTRACT_NAME}\n":
        raise AssertionError("contract sidecar differs")

    fixture_a_path = ROOT / "fixture-a-stage7-response-unchanged.json"
    fixture_b_path = ROOT / "fixture-b-text-only-request.json"
    fixture_c_path = ROOT / "fixture-c-existing-schema-text-response.json"
    if digest(fixture_a_path) != FIXTURE_A_SHA256:
        raise AssertionError("Fixture A bytes differ from sealed 0021 response")
    if digest(fixture_b_path) != FIXTURE_B_SHA256:
        raise AssertionError("Fixture B differs from admitted text-only request")
    if digest(fixture_c_path) != FIXTURE_C_SHA256:
        raise AssertionError("Fixture C bytes differ")
    fixture_c_sidecar = ROOT / (
        "ENGAV3D-STAGE8-TICKET-2B-FIXTURE-C-EXISTING-SCHEMA-TEXT-RESPONSE.json.sha256"
    )
    expected_fixture_c_sidecar = (
        f"{FIXTURE_C_SHA256}  "
        "ENGAV3D-STAGE8-TICKET-2B-FIXTURE-C-EXISTING-SCHEMA-TEXT-RESPONSE.json\n"
    )
    if fixture_c_sidecar.read_text(encoding="utf-8") != expected_fixture_c_sidecar:
        raise AssertionError("Fixture C source sidecar differs")

    fixture_a = json.loads(fixture_a_path.read_bytes())
    fixture_b = json.loads(fixture_b_path.read_bytes())
    fixture_c = json.loads(fixture_c_path.read_bytes())

    if set(fixture_a) != RESPONSE_KEYS:
        raise AssertionError("Stage 7 response top-level keys differ")
    if set(fixture_a["provider_session_ref"]) != PROVIDER_KEYS:
        raise AssertionError("Stage 7 provider-session keys differ")
    if set(fixture_a["perception_result"]) != PERCEPTION_RESULT_KEYS:
        raise AssertionError("Stage 7 perception-result keys differ")
    if not bridge_accepts(
        fixture_a,
        active_request_id=fixture_a["request_id"],
        active_client_request_id=fixture_a["client_request_id"],
        active_capture_id=fixture_a["perception_result"]["capture_id"],
    ):
        raise AssertionError("sealed Stage 7 response no longer validates")

    if not exact_text_request(fixture_b):
        raise AssertionError("Fixture B is not the admitted text-only request")
    text_request_id = fixture_b["request_id"]
    text_client_id = fixture_b["additional_context"]["client_request_id"]

    if set(fixture_c) != RESPONSE_KEYS:
        raise AssertionError("Fixture C does not use exact existing response keys")
    if fixture_c["request_id"] != text_request_id:
        raise AssertionError("Fixture C request_id is not correlated")
    if fixture_c["client_request_id"] != text_client_id:
        raise AssertionError("Fixture C client_request_id is not correlated")
    if "routing_mode" in fixture_c:
        raise AssertionError("Fixture C added routing_mode")
    if not bridge_accepts(
        fixture_c,
        active_request_id=text_request_id,
        active_client_request_id=text_client_id,
        active_capture_id="",
    ):
        raise AssertionError("existing rejected/no-capture shape was not admitted")

    perception = fixture_c["perception_result"]
    if not (
        perception["requested_state"] == "unavailable"
        and perception["effective_state"] == "rejected"
        and perception["capture_id"] is None
        and perception["image_sha256"] is None
    ):
        raise AssertionError("Fixture C does not expose rejected perception semantics")

    proposed_success = copy.deepcopy(fixture_c)
    proposed_success["perception_result"]["effective_state"] = "unavailable"
    if bridge_accepts(
        proposed_success,
        active_request_id=text_request_id,
        active_client_request_id=text_client_id,
        active_capture_id="",
    ):
        raise AssertionError("non-rejected text-only result passed without capture identity")

    if bridge_accepts(
        fixture_c,
        active_request_id="req_ffffffffffffffffffffffffffffffff",
        active_client_request_id=text_client_id,
        active_capture_id="",
    ):
        raise AssertionError("request_id mismatch was accepted")
    if bridge_accepts(
        fixture_c,
        active_request_id=text_request_id,
        active_client_request_id="dragon3d_ffffffffffffffffffffffffffffffff_9",
        active_capture_id="",
    ):
        raise AssertionError("client_request_id mismatch was accepted")

    response_fields = set(fixture_c["perception_result"])
    if "capture_id" not in response_fields or "image_sha256" not in response_fields:
        raise AssertionError("perception-specific mandatory keys were not observed")
    if {"image_path", "perception_state", "routing_mode"} & set(fixture_c):
        raise AssertionError("unexpected top-level route/image fields observed")

    contract_text = contract.read_text(encoding="utf-8")
    required_contract_markers = (
        "STAGE8_TEXT_ONLY_RESPONSE_WIRE_CONTRACT_GAP",
        "SUCCESSFUL NO-PERCEPTION RESULT BRANCH",
        "Response correlation:                         SUFFICIENT",
        "Successful text-only response:                 NOT HONESTLY REPRESENTABLE",
    )
    if not all(marker in contract_text for marker in required_contract_markers):
        raise AssertionError("contract gap markers differ")

    print("STAGE8_TEXT_ONLY_RESPONSE_WIRE_CONTRACT_GAP")
    print("RESPONSE_QUESTIONS=10/10_ANSWERED")
    print("RESPONSE_TOP_LEVEL_KEYS=11")
    print("REQUEST_CORRELATION=request_id+client_request_id")
    print("REQUEST_CORRELATION=DETERMINISTIC_NOT_ORDER_ONLY")
    print("RESPONSE_ROUTING_MODE=NOT_REQUIRED_FOR_CORRELATION")
    print("PERCEPTION_RESULT=MANDATORY")
    print("TEXT_ONLY_SUCCESS_NO_CAPTURE=NOT_REPRESENTABLE")
    print("EXACT_MISSING_SEMANTIC=SUCCESSFUL_NO_PERCEPTION_RESULT_BRANCH")
    print("FIXTURE_C=EXISTING_SCHEMA_BUT_UNAVAILABLE_REJECTED")
    print("STAGE7_RESPONSE_BYTES=UNCHANGED")
    print("PROVIDER_EXECUTIONS=0")
    print("RUNTIME_IMPLEMENTATION=NOT_AUTHORIZED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError) as exc:
        print(f"STAGE8_TICKET2B_VERIFIER_REJECTED: {exc}", file=sys.stderr)
        raise SystemExit(1)
