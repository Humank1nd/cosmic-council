import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
SRC_ROOT = REPO_ROOT / "src"

src_root_str = str(SRC_ROOT)
if src_root_str not in sys.path:
    sys.path.insert(0, src_root_str)

from desktop_runtime import ACTIVE_CANON_PATH, AJNA_DIR, ARTIFACT_ROOT, SEAT_MAP_PATH, ensure_runtime_dirs
from cosmic_council.canon import COSMIC_COUNCIL_CANON, ROYGBV_ORDER, TotemColor  # noqa: E402
from cronus.app.tools.desktop import handle_list_windows  # noqa: E402
from cronus.app.tools.vision import handle_screenshot, handle_vision_analyze  # noqa: E402


OUTPUT_DIR = ARTIFACT_ROOT
SCREENSHOT_DIR = AJNA_DIR
STATUS_PATH = OUTPUT_DIR / "ajna-monitor-status.json"
LOG_PATH = OUTPUT_DIR / "ajna-monitor.jsonl"
VISION_FEED_PATH = OUTPUT_DIR / "ajna-vision-feed.json"

CENTER_SEAT = "center"
CENTER_TITLES = ["Dream Caesar", "Center"]


def _normalize_title(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def _canonical_seats() -> list[str]:
    return [color.value for color in ROYGBV_ORDER]


def _seat_display_title(seat: str) -> str:
    if seat == CENTER_SEAT:
        return CENTER_TITLES[0]
    return COSMIC_COUNCIL_CANON[TotemColor(seat)].name


def _seat_aliases(seat: str) -> list[str]:
    if seat == CENTER_SEAT:
        return list(CENTER_TITLES)
    display = _seat_display_title(seat)
    color = seat.title()
    return [display, color]


def _load_active_canon() -> dict[str, Any] | None:
    if not ACTIVE_CANON_PATH.exists():
        return None
    try:
        return json.loads(ACTIVE_CANON_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _active_seats(active_canon: dict[str, Any] | None) -> list[str]:
    if not active_canon:
        return _canonical_seats()
    seats = active_canon.get("active_seats")
    if isinstance(seats, list) and seats:
        return [seat for seat in seats if seat in _canonical_seats()]
    return _canonical_seats()


def _load_seat_map() -> dict[str, Any]:
    if not SEAT_MAP_PATH.exists():
        return {}
    try:
        return json.loads(SEAT_MAP_PATH.read_text(encoding="utf-8")).get("seats", {})
    except (OSError, json.JSONDecodeError):
        return {}


def _seat_expected_titles(seat: str, seat_map: dict[str, Any]) -> list[str]:
    expected = []
    seat_entry = seat_map.get(seat, {})
    title = seat_entry.get("title")
    if isinstance(title, str) and title.strip():
        expected.append(title.strip())
    for alias in _seat_aliases(seat):
        if alias not in expected:
            expected.append(alias)
    return expected


def _match_score(window: dict[str, Any], seat: str, seat_map: dict[str, Any]) -> tuple[int, int, int, int]:
    title = _normalize_title(window.get("title", ""))
    seat_entry = seat_map.get(seat, {})
    saved_title = _normalize_title(str(seat_entry.get("title", "")))
    aliases = [_normalize_title(alias) for alias in _seat_aliases(seat)]
    exact_display = _normalize_title(_seat_display_title(seat))
    alias_hit = any(alias and alias in title for alias in aliases)
    exact_saved = int(bool(saved_title) and title == saved_title)
    exact_display_hit = int(bool(exact_display) and title == exact_display)
    active_hit = int(bool(window.get("is_active")))
    return (
        exact_saved,
        exact_display_hit,
        int(alias_hit),
        active_hit,
    )


def _matching_windows_for_seat(
    windows: list[dict[str, Any]],
    seat: str,
    seat_map: dict[str, Any],
) -> list[dict[str, Any]]:
    expected_titles = [_normalize_title(title) for title in _seat_expected_titles(seat, seat_map)]
    matches = []
    for window in windows:
        normalized = _normalize_title(window.get("title", ""))
        if not normalized:
            continue
        if any(expected == normalized for expected in expected_titles):
            matches.append(window)
            continue
        if any(expected and expected in normalized for expected in expected_titles):
            matches.append(window)
    return sorted(
        matches,
        key=lambda window: _match_score(window, seat, seat_map),
        reverse=True,
    )


def _seat_window_state(
    seat: str,
    windows: list[dict[str, Any]],
    seat_map: dict[str, Any],
) -> dict[str, Any]:
    matches = _matching_windows_for_seat(windows, seat, seat_map)
    selected = matches[0] if matches else None
    return {
        "seat": seat,
        "display_title": _seat_display_title(seat),
        "expected_titles": _seat_expected_titles(seat, seat_map),
        "present": selected is not None,
        "ambiguous": len(matches) > 1,
        "match_count": len(matches),
        "selected_window": selected,
        "matching_titles": [window["title"] for window in matches[:5]],
        "is_active": bool(selected and selected.get("is_active")),
        "is_minimized": bool(selected and selected.get("is_minimized")),
    }


def _extract_json_block(raw: str) -> dict[str, Any] | None:
    if not raw:
        return None
    candidate = raw.strip()
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", candidate, re.DOTALL)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _build_vision_prompt(active_seats: list[str]) -> str:
    seat_list = ", ".join([CENTER_SEAT, *_canonical_seats()])
    active_list = ", ".join(active_seats)
    return (
        "You are Ajna, the passive Dream Caesar computer-vision layer. "
        "Inspect this desktop council screenshot and respond with JSON only. "
        "Use this exact schema: "
        '{"overall_state":"ok|warning|blocked|unknown",'
        '"summary":"short string",'
        '"blockers":["..."],'
        '"seat_observations":{"center":{"visible":true,"blocked":false,"note":"..."},'
        '"red":{"visible":true,"blocked":false,"note":"..."},'
        '"orange":{"visible":true,"blocked":false,"note":"..."},'
        '"yellow":{"visible":true,"blocked":false,"note":"..."},'
        '"green":{"visible":true,"blocked":false,"note":"..."},'
        '"blue":{"visible":true,"blocked":false,"note":"..."},'
        '"purple":{"visible":true,"blocked":false,"note":"..."}},'
        '"recommendations":["..."]}. '
        f"Known seats: {seat_list}. Active seats now: {active_list}. "
        "Base the answer only on what is visible in the screenshot. If a seat is not visible, mark it visible=false."
    )


def _build_local_summary(
    seat_states: dict[str, dict[str, Any]],
    active_seats: list[str],
    vision_state: dict[str, Any],
) -> str:
    missing = [seat for seat in active_seats if not seat_states.get(seat, {}).get("present")]
    ambiguous = [seat for seat, state in seat_states.items() if state.get("ambiguous")]
    blocked = vision_state.get("blockers", []) if isinstance(vision_state, dict) else []
    parts = []
    if missing:
        parts.append(f"missing active seats: {', '.join(missing)}")
    if ambiguous:
        parts.append(f"ambiguous seat matches: {', '.join(ambiguous)}")
    if blocked:
        parts.append(f"vision blockers: {', '.join(blocked[:2])}")
    if not parts:
        parts.append("desktop looks routable")
    return "; ".join(parts)


def tick(include_vision_analysis: bool = True, monitor: int = 0) -> dict[str, Any]:
    ensure_runtime_dirs()
    timestamp = datetime.now().astimezone()
    stamp = timestamp.strftime("%Y%m%d-%H%M%S")
    screenshot_path = SCREENSHOT_DIR / f"ajna-{stamp}.png"

    active_canon = _load_active_canon()
    active_seats = _active_seats(active_canon)
    seat_map = _load_seat_map()

    screenshot = handle_screenshot({"monitor": monitor, "save_path": str(screenshot_path)})
    windows_result = handle_list_windows({})
    windows = windows_result.get("windows", []) if windows_result.get("success") else []

    seat_states = {
        seat: _seat_window_state(seat, windows, seat_map)
        for seat in [CENTER_SEAT, *_canonical_seats()]
    }

    raw_analysis = None
    parsed_analysis = None
    vision_error = None
    if include_vision_analysis and screenshot.get("success") and (
        os.getenv("CRONUS_VISION_API_KEY") or os.getenv("OPENAI_API_KEY")
    ):
        vision_result = handle_vision_analyze(
            {
                "prompt": _build_vision_prompt(active_seats),
                "image_base64": screenshot["image_base64"],
            }
        )
        if vision_result.get("success"):
            raw_analysis = vision_result.get("analysis")
            parsed_analysis = _extract_json_block(raw_analysis or "")
        else:
            vision_error = vision_result.get("error")
    elif include_vision_analysis:
        vision_error = "Vision analysis skipped because no API key is configured."

    vision_state = parsed_analysis or {
        "overall_state": "unknown" if vision_error else "ok",
        "summary": "No structured vision analysis available.",
        "blockers": [],
        "seat_observations": {},
        "recommendations": [],
    }

    record = {
        "timestamp": timestamp.isoformat(),
        "ajna": True,
        "active_canon_path": str(ACTIVE_CANON_PATH) if active_canon else None,
        "active_seats": active_seats,
        "screenshot_path": str(screenshot_path) if screenshot.get("success") else None,
        "screenshot_success": screenshot.get("success", False),
        "windows_success": windows_result.get("success", False),
        "window_count": len(windows),
        "seat_states": seat_states,
        "missing_active_seats": [seat for seat in active_seats if not seat_states[seat]["present"]],
        "ambiguous_seats": [seat for seat, state in seat_states.items() if state["ambiguous"]],
        "vision_analysis_enabled": include_vision_analysis,
        "vision_error": vision_error,
        "vision_raw": raw_analysis,
        "vision": vision_state,
    }
    record["summary"] = _build_local_summary(seat_states, active_seats, vision_state)

    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    STATUS_PATH.write_text(json.dumps(record, indent=2), encoding="utf-8")
    VISION_FEED_PATH.write_text(
        json.dumps(
            {
                "timestamp": record["timestamp"],
                "summary": record["summary"],
                "screenshot_path": record["screenshot_path"],
                "active_seats": active_seats,
                "missing_active_seats": record["missing_active_seats"],
                "ambiguous_seats": record["ambiguous_seats"],
                "overall_state": vision_state.get("overall_state"),
                "recommendations": vision_state.get("recommendations", []),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Ajna monitor for Dream Caesar desktop state.")
    parser.add_argument("--interval-seconds", type=int, default=300)
    parser.add_argument("--monitor", type=int, default=0)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--no-vision-analysis", action="store_true")
    args = parser.parse_args()

    while True:
        record = tick(include_vision_analysis=not args.no_vision_analysis, monitor=args.monitor)
        print(json.dumps(record))
        if args.once:
            return 0
        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
