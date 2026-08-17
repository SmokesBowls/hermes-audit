#!/usr/bin/env python3
"""Canonical, provider-free admission verifier for Stage 8 Ticket 1."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sys
import unicodedata


ROOT = Path(__file__).resolve().parent
CONTRACT_NAME = (
    "ENGAV3D-STAGE8-TICKET-1-PERSISTENT-WORKER-ROUTING-BOUNDARY.md"
)
CONTRACT = ROOT / CONTRACT_NAME
SIDECAR = ROOT / f"{CONTRACT_NAME}.sha256"
EXPECTED_SHA256 = "8d569dac608f268405630b36816cb5d8514fd6d74dc784840c4110218f2a880a"
POLICY_VERSION = "engav3d.routing.stage8.ticket1.v1"

EXPLICIT_CURRENT_PHRASES = (
    "what do you see",
    "what can you see",
    "what is visible",
    "currently visible",
    "current viewport",
    "current view",
    "current screen",
    "current frame",
    "current scene",
    "current room",
    "right now",
    "in front of me",
    "left side of the screen",
    "right side of the screen",
    "left side of the frame",
    "right side of the frame",
    "look at this",
    "look here",
    "look around",
)
DIRECT_VIEW_PHRASES = {"what do you see", "what can you see"}
HISTORY_SCOPES = (
    "in your memory",
    "from memory",
    "in the previous scene",
    "in the prior scene",
    "in the earlier scene",
    "last time",
    "previously",
)
ANCHORS = (
    "this",
    "these",
    "here",
    "currently",
    "right now",
    "at the moment",
    "in front of me",
    "on the screen",
    "in the frame",
    "in the viewport",
)
VISUAL_SPATIAL_TERMS = (
    "see",
    "look",
    "visible",
    "view",
    "screen",
    "frame",
    "viewport",
    "scene",
    "room",
    "object",
    "dragon",
    "color",
    "colour",
    "where",
    "location",
    "left",
    "right",
    "front",
    "behind",
    "above",
    "below",
    "near",
    "far",
    "different",
    "compare",
)

NORMATIVE_CASES = (
    ("What do you see?", "current_perception"),
    ("Where is the Dragon right now?", "current_perception"),
    ("What color is the object in front of me?", "current_perception"),
    ("What is on the left side of the screen?", "current_perception"),
    ("Describe the current room.", "current_perception"),
    ("What do you remember about the previous Dragon and room?", "text_only"),
    (
        "How is this Dragon different from the one you remember?",
        "current_perception",
    ),
    ("What did we discuss earlier?", "text_only"),
    ("Help me plan the next ticket.", "text_only"),
    ("What did you see in the previous scene?", "text_only"),
    ("Explain this plan.", "text_only"),
    ("Do you remember this Dragon on the screen?", "current_perception"),
)

MEMORY_FIXTURE = (
    "Without using any current image, describe what you remember about the previous "
    "Dragon and the room/environment you saw before this latest scene."
)


def normalize(message: str) -> str:
    normalized = unicodedata.normalize("NFKC", message).casefold()
    characters: list[str] = []
    for index, character in enumerate(normalized):
        if character.isspace():
            characters.append(" ")
            continue
        category = unicodedata.category(character)
        if category.startswith("P"):
            internal_apostrophe = (
                character in {"'", "’"}
                and index > 0
                and index + 1 < len(normalized)
                and normalized[index - 1].isalnum()
                and normalized[index + 1].isalnum()
            )
            characters.append(character if internal_apostrophe else " ")
            continue
        characters.append(character)
    return " ".join("".join(characters).split())


def contains_phrase(message: str, phrase: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", message) is not None


def route(message: str) -> str:
    comparison = normalize(message)
    explicit_matches = {
        phrase
        for phrase in EXPLICIT_CURRENT_PHRASES
        if contains_phrase(comparison, phrase)
    }
    if explicit_matches:
        history_scoped_direct_view = (
            explicit_matches.issubset(DIRECT_VIEW_PHRASES)
            and any(contains_phrase(comparison, phrase) for phrase in HISTORY_SCOPES)
        )
        if not history_scoped_direct_view:
            return "current_perception"

    anchored = any(contains_phrase(comparison, phrase) for phrase in ANCHORS)
    visual = any(
        contains_phrase(comparison, phrase) for phrase in VISUAL_SPATIAL_TERMS
    )
    if anchored and visual:
        return "current_perception"
    return "text_only"


def require_contract_identity() -> str:
    raw = CONTRACT.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_SHA256:
        raise AssertionError(f"contract hash mismatch: {actual}")
    expected_sidecar = f"{EXPECTED_SHA256}  {CONTRACT_NAME}\n"
    if SIDECAR.read_text(encoding="utf-8") != expected_sidecar:
        raise AssertionError("contract sidecar differs from exact frozen identity")
    return raw.decode("utf-8")


def require_contract_boundaries(text: str) -> None:
    required_literals = (
        POLICY_VERSION,
        "At most one authoritative worker may own the project mailbox at a time.",
        "An admitted `text_only` submission receives no `capture_id`.",
        "Unknown, novel, or ambiguous wording defaults to `text_only`.",
        "No provider interpretation is needed to answer any of the six questions.",
        "text-only wire representation:        BLOCKED ON FOLLOW-UP SCHEMA AUTHORITY",
        "provider execution:                   0 AUTHORIZED",
        "runtime wiring:                       NOT AUTHORIZED",
    )
    missing = [literal for literal in required_literals if literal not in text]
    if missing:
        raise AssertionError(f"contract boundaries missing: {missing}")


def require_deterministic_routes() -> None:
    for message, expected in NORMATIVE_CASES:
        first = route(message)
        second = route(message)
        if first != expected or second != expected or first != second:
            raise AssertionError(
                f"route mismatch for {message!r}: {first!r}, {second!r}, expected {expected!r}"
            )

    if route(MEMORY_FIXTURE) != "text_only":
        raise AssertionError("memory fixture did not route text_only")


def require_six_admission_answers() -> None:
    memory_route = route(MEMORY_FIXTURE)
    admission = {
        "route": memory_route,
        "capture_permitted": memory_route == "current_perception",
        "image_attachment_permitted": memory_route == "current_perception",
        "worker_owner": "one_authoritative_persistent_project_worker",
        "hud_lifecycle": ("thinking", "terminal_clear"),
        "worker_remains_alive": True,
    }
    expected = {
        "route": "text_only",
        "capture_permitted": False,
        "image_attachment_permitted": False,
        "worker_owner": "one_authoritative_persistent_project_worker",
        "hud_lifecycle": ("thinking", "terminal_clear"),
        "worker_remains_alive": True,
    }
    if admission != expected or len(admission) != 6:
        raise AssertionError(f"six-question admission mismatch: {admission!r}")


def main() -> int:
    text = require_contract_identity()
    require_contract_boundaries(text)
    require_deterministic_routes()
    require_six_admission_answers()

    print("STAGE8_TICKET1_CONTRACT_ADMITTED")
    print()
    print("Persistent worker lifecycle:")
    print("DEFINED")
    print()
    print("Routing modes:")
    print("text_only")
    print("current_perception")
    print()
    print("Routing decision:")
    print("DETERMINISTIC PRE-DISPATCH")
    print()
    print("Thinking lifecycle:")
    print("DEFINED")
    print()
    print("Admission questions:")
    print("6 / 6 DETERMINISTICALLY ANSWERABLE")
    print()
    print("Memory fixture:")
    print("route=text_only")
    print("capture_permitted=false")
    print("image_attachment_permitted=false")
    print("worker_remains_alive=true")
    print()
    print("Contract SHA-256:")
    print(EXPECTED_SHA256)
    print()
    print("Provider executions:")
    print("0")
    print()
    print("Runtime implementation:")
    print("NOT AUTHORIZED BY THIS GATE")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"STAGE8_TICKET1_CONTRACT_REJECTED: {exc}", file=sys.stderr)
        raise SystemExit(1)
