from __future__ import annotations

from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BRIDGE_PATH = PROJECT_ROOT / "scripts" / "EngAInBridge3D.gd"
SOURCE = BRIDGE_PATH.read_text(encoding="utf-8")
TEXT_ONLY_FIXTURE = (
    "Without using any current image, describe what you remember about the previous "
    "Dragon and the room/environment you saw before this latest scene."
)
CURRENT_FIXTURE = "What color is the Dragon right now?"


def _function(source: str, name: str) -> str:
    match = re.search(rf"(?m)^func\s+{re.escape(name)}\s*\(", source)
    assert match is not None, f"Ticket 3B prerequisite function is absent: {name}"
    following = re.search(r"(?m)^func\s+", source[match.end() :])
    end = len(source) if following is None else match.end() + following.start()
    return source[match.start() : end]


def _text_only_submission_surface(body: str) -> bool:
    capture = body.find("capture_for_submission")
    if capture < 0:
        return False
    before_capture = body[:capture]
    route_is_locally_selected = (
        '"text_only"' in before_capture
        and ("routing_mode" in before_capture or "route" in before_capture)
        and ("current image" in SOURCE.lower() or "no-current-image" in SOURCE.lower())
    )
    capture_is_route_guarded = bool(
        re.search(
            r"(?s)if[^\n]*(current_perception|routing_mode|route)[^:]*:.*capture_for_submission",
            body,
        )
    )
    text_wire_is_reachable = (
        '"routing_mode"' in body
        and '"text_only"' in body
        and '"perception": perception' in SOURCE
    )
    return route_is_locally_selected and capture_is_route_guarded and text_wire_is_reachable


def test_ticket3b_text_only_fixture_selects_text_wire_without_capture() -> None:
    """The explicit no-current-image fixture must bypass capture before publication."""
    assert "Without using any current image" in TEXT_ONLY_FIXTURE
    assert _text_only_submission_surface(_function(SOURCE, "submit")), (
        "Godot submission has no reachable local text-only route that suppresses "
        "capture and publishes the admitted text-only mailbox representation"
    )


def test_ticket3b_current_perception_fixture_preserves_one_stage7_capture() -> None:
    """The current-view fixture retains the sealed single-capture publication order."""
    body = _function(SOURCE, "submit")
    assert "right now" in CURRENT_FIXTURE
    assert body.count("capture_for_submission(client_request_id)") == 1
    capture = body.find("capture_for_submission(client_request_id)")
    publication = body.find('PackedStringArray(["--publish-request", temporary_path])')
    assert 0 <= capture < publication
    builder = _function(SOURCE, "_build_mailbox_request")
    assert '"perception": perception' in builder
    assert '"capture_id": capture_id' not in builder


def test_ticket3b_routing_probe_has_no_provider_execution_surface() -> None:
    forbidden = ("--resume", "--image", "HermesCLIClient", "_run_bounded", "hermes chat")
    assert [token for token in forbidden if token in SOURCE] == []
