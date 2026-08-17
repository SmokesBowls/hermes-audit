#!/usr/bin/env python3
"""Admit the expected fail-closed Ticket 2A RED result as evidence."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
RED_VERIFIER = ROOT / "verify_current_stage7_text_only_gap.py"
RED_LOG = ROOT / "current-stage7-text-only-red.log"

EXPECTED_MARKERS = (
    "STAGE8_TEXT_ONLY_MAILBOX_CONTRACT_GAP",
    "perception_omitted=REJECTED",
    "perception_null=REJECTED",
    "text_only_state=REJECTED",
    "context_routing_mode=REJECTED",
    "request_routing_mode=REJECTED",
    "ACCEPTED_WITH_CAPTURE_ID_AND_CAPTURE_FAILURE_SEMANTICS",
    "capture_attempted=false",
    "capture_id=FORBIDDEN_BY_TICKET1_BUT_REQUIRED_BY_CURRENT_SCHEMA",
    "image_attachment_permitted=false",
    "intentional_absence_distinct_from_capture_failure=NOT_REPRESENTABLE",
    "stage7_current_perception_representation=UNCHANGED",
    "provider_executions=0",
    "runtime_implementation=NOT_AUTHORIZED",
)


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(RED_VERIFIER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 1:
        raise AssertionError(f"RED verifier exit was {result.returncode}, expected 1")
    replay = result.stdout + result.stderr + "VERIFIER_EXIT=1\n"
    frozen_log = RED_LOG.read_text(encoding="utf-8")
    if replay != frozen_log:
        raise AssertionError("RED verifier replay differs from frozen RED log")
    missing = [marker for marker in EXPECTED_MARKERS if marker not in replay]
    if missing:
        raise AssertionError(f"RED evidence markers missing: {missing}")

    print("STAGE8_TICKET2A_CONTRACT_GAP_RED_ADMITTED")
    print("REPRESENTATION_QUESTIONS=10/10_ANSWERED")
    print("EXACT_TEXT_ONLY_JSON=NOT_CONSTRUCTIBLE_UNDER_CURRENT_SCHEMA")
    print("INTENTIONAL_TEXT_ONLY_VS_CAPTURE_FAILURE=NOT_STRUCTURALLY_DISTINGUISHABLE")
    print("STAGE7_CURRENT_PERCEPTION=UNCHANGED")
    print("PROVIDER_EXECUTIONS=0")
    print("RUNTIME_IMPLEMENTATION=NOT_AUTHORIZED")
    print("FOLLOW_UP_SCHEMA_AMENDMENT=REQUIRED_BUT_NOT_DEFINED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"STAGE8_TICKET2A_RED_EVIDENCE_REJECTED: {exc}", file=sys.stderr)
        raise SystemExit(1)
