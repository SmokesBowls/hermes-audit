#!/usr/bin/env python3
"""Canonical provider-free verifier for Stage 8 Ticket 1 plus Amendment 1."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sys
import unicodedata


ROOT = Path(__file__).resolve().parent
CONTRACT_NAME = "ENGAV3D-STAGE8-TICKET-1-PERSISTENT-WORKER-ROUTING-BOUNDARY.md"
AMENDMENT_NAME = "ENGAV3D-STAGE8-TICKET-1-AMENDMENT-1-EXPLICIT-NO-CURRENT-IMAGE.md"
CONTRACT_SHA256 = "8d569dac608f268405630b36816cb5d8514fd6d74dc784840c4110218f2a880a"
AMENDMENT_SHA256 = "5bbc93fd4ed308f69722417be63f12b6db91e9012112776132b1baf394e0eeaf"
POLICY = "engav3d.routing.stage8.ticket1.v1 + amendment-1"

RULE0 = (
    "without using any current image",
    "without a current image",
    "do not use any current image",
    "do not use a current image",
    "don't use any current image",
    "don't use a current image",
    "no current image",
    "text only",
)
RULE1 = (
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
DIRECT_VIEW = {"what do you see", "what can you see"}
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
VISUAL = (
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

MEMORY_FIXTURE = (
    "Without using any current image, describe what you remember about the previous "
    "Dragon and the room/environment you saw before this latest scene."
)

CASES = (
    ("What do you see?", "current_perception"),
    ("Where is the Dragon right now?", "current_perception"),
    ("What color is the object in front of me?", "current_perception"),
    ("What is on the left side of the screen?", "current_perception"),
    ("Describe the current room.", "current_perception"),
    ("What do you remember about the previous Dragon and room?", "text_only"),
    ("How is this Dragon different from the one you remember?", "current_perception"),
    ("What did we discuss earlier?", "text_only"),
    ("Help me plan the next ticket.", "text_only"),
    ("What did you see in the previous scene?", "text_only"),
    ("Explain this plan.", "text_only"),
    ("Do you remember this Dragon on the screen?", "current_perception"),
    (MEMORY_FIXTURE, "text_only"),
    ("Text-only: what is visible right now?", "text_only"),
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_identity(name: str, expected: str) -> str:
    path = ROOT / name
    if digest(path) != expected:
        raise AssertionError(f"hash mismatch: {name}")
    sidecar = ROOT / f"{name}.sha256"
    if sidecar.read_text(encoding="utf-8") != f"{expected}  {name}\n":
        raise AssertionError(f"sidecar mismatch: {name}")
    return path.read_text(encoding="utf-8")


def normalize(message: str) -> str:
    value = unicodedata.normalize("NFKC", message).casefold()
    characters: list[str] = []
    for index, character in enumerate(value):
        if character.isspace():
            characters.append(" ")
        elif unicodedata.category(character).startswith("P"):
            internal_apostrophe = (
                character in {"'", "’"}
                and index > 0
                and index + 1 < len(value)
                and value[index - 1].isalnum()
                and value[index + 1].isalnum()
            )
            characters.append(character if internal_apostrophe else " ")
        else:
            characters.append(character)
    return " ".join("".join(characters).split())


def contains(value: str, phrase: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", value) is not None


def route(message: str) -> str:
    value = normalize(message)
    if any(contains(value, phrase) for phrase in RULE0):
        return "text_only"

    explicit = {phrase for phrase in RULE1 if contains(value, phrase)}
    if explicit:
        direct_history_exception = (
            explicit.issubset(DIRECT_VIEW)
            and any(contains(value, phrase) for phrase in HISTORY_SCOPES)
        )
        if not direct_history_exception:
            return "current_perception"

    if (
        any(contains(value, phrase) for phrase in ANCHORS)
        and any(contains(value, phrase) for phrase in VISUAL)
    ):
        return "current_perception"
    return "text_only"


def verify_authorities() -> None:
    contract = require_identity(CONTRACT_NAME, CONTRACT_SHA256)
    amendment = require_identity(AMENDMENT_NAME, AMENDMENT_SHA256)
    required_contract = (
        "At most one authoritative worker may own the project mailbox at a time.",
        "An admitted `text_only` submission receives no `capture_id`.",
        "No provider interpretation is needed to answer any of the six questions.",
        "text-only wire representation:        BLOCKED ON FOLLOW-UP SCHEMA AUTHORITY",
        "runtime wiring:                       NOT AUTHORIZED",
    )
    required_amendment = (
        POLICY,
        "0. explicit no-current-image instruction -> text_only",
        "Rule 0 is an explicit evidence constraint.",
        "capture_permitted=false",
        "image_attachment_permitted=false",
        "worker_remains_alive=true",
    )
    if not all(item in contract for item in required_contract):
        raise AssertionError("upstream contract boundary missing")
    if not all(item in amendment for item in required_amendment):
        raise AssertionError("amendment boundary missing")


def verify_routes() -> None:
    for message, expected in CASES:
        observed = [route(message) for _ in range(3)]
        if observed != [expected, expected, expected]:
            raise AssertionError(
                f"non-deterministic or wrong route for {message!r}: {observed!r}"
            )


def verify_admission_questions() -> None:
    selected = route(MEMORY_FIXTURE)
    answers = {
        "route": selected,
        "capture_permitted": selected == "current_perception",
        "image_attachment_permitted": selected == "current_perception",
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
    if len(answers) != 6 or answers != expected:
        raise AssertionError(f"admission answers differ: {answers!r}")


def main() -> int:
    verify_authorities()
    verify_routes()
    verify_admission_questions()
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
