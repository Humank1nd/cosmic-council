import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
SRC_ROOT = REPO_ROOT / "src"

src_root_str = str(SRC_ROOT)
if src_root_str not in sys.path:
    sys.path.insert(0, src_root_str)

from desktop_runtime import ARTIFACT_ROOT, SEAT_MAP_PATH, ensure_runtime_dirs
from cronus.app.tools.desktop import handle_list_windows  # noqa: E402
from cronus.app.tools.vision import handle_screenshot  # noqa: E402
from cronus.app.council.canon_adapter import (  # noqa: E402
    CENTER_SEAT,
    SeatResolutionError,
    all_seats,
    normalize_title,
    resolve_seat_window,
    seat_title,
    title_matches_seat,
    window_selector_for_seat,
)

OUTPUT_DIR = ARTIFACT_ROOT
SCREENSHOT_PATH = OUTPUT_DIR / "desktop-fractal-council-latest.png"
MAP_PATH = OUTPUT_DIR / "desktop-fractal-council-map.json"

def _selector(seat: str, window):
    return window_selector_for_seat(seat, window)


def _seat_entry(seat: str, window):
    return {
        "title": window["title"],
        "bounds": {
            "left": window["left"],
            "top": window["top"],
            "width": window["width"],
            "height": window["height"],
        },
        "selector": _selector(seat, window),
        "handoff_defaults": {
            "input_ratio_x": 0.5,
            "input_offset_y": 42,
        },
    }


def _load_previous_seats() -> dict[str, dict]:
    if not SEAT_MAP_PATH.exists():
        return {}
    return json.loads(SEAT_MAP_PATH.read_text(encoding="utf-8")).get("seats", {})


def _find_named_seat(windows: list[dict], seat: str, previous: dict | None = None) -> dict:
    selector = dict((previous or {}).get("selector", {}))
    bounds = dict((previous or {}).get("bounds", {}))
    return resolve_seat_window(
        windows,
        seat,
        exact_title=selector.get("exact_title") or (previous or {}).get("title"),
        target_left=selector.get("target_left", bounds.get("left")),
        target_top=selector.get("target_top", bounds.get("top")),
    )


def _pick_windows():
    result = handle_list_windows({})
    windows = result["windows"]
    previous_seats = _load_previous_seats()

    named_seats = {}
    resolution_errors = {}
    for seat in all_seats():
        try:
            named_seats[seat] = _find_named_seat(windows, seat, previous=previous_seats.get(seat))
        except SeatResolutionError as exc:
            resolution_errors[seat] = str(exc)

    if resolution_errors:
        raise RuntimeError(json.dumps({"seat_resolution_errors": resolution_errors}, indent=2))

    claudes = [w for w in windows if "Claude Code" in w["title"]]
    geminis = [w for w in windows if "cmd.exe" in w["title"]]
    codexes = [
        w
        for w in windows
        if normalize_title(w["title"]) == "Windows PowerShell" or title_matches_seat(w["title"], CENTER_SEAT)
    ]

    codexes_sorted = sorted(codexes, key=lambda w: (w["top"], w["left"]))
    geminis_sorted = sorted(geminis, key=lambda w: (w["top"], w["left"]))
    claudes_sorted = sorted(claudes, key=lambda w: (w["top"], w["left"]))

    return {
        "named_seats": named_seats,
        "center_codex": named_seats.get(CENTER_SEAT) or next((w for w in codexes if w["is_active"]), codexes_sorted[0] if codexes_sorted else None),
        "codex": codexes_sorted,
        "gemini": geminis_sorted,
        "claude": claudes_sorted,
    }


def main() -> int:
    ensure_runtime_dirs()
    screenshot_result = handle_screenshot({"save_path": str(SCREENSHOT_PATH)})
    layout = _pick_windows()

    artifact = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "screenshot_path": str(SCREENSHOT_PATH),
        "screenshot_success": screenshot_result.get("success", False),
        "layout": {
            "center_codex": layout["center_codex"],
            "codex": layout["codex"],
            "gemini": layout["gemini"],
            "claude": layout["claude"],
        },
        "notes": [
            "This file is an observed layout artifact, not a permanent seat assignment.",
            "Re-run after the human rearranges the windows around the hexaclock.",
        ],
    }
    seat_map = {
        "timestamp": artifact["timestamp"],
        "screenshot_path": str(SCREENSHOT_PATH),
        "seats": {
            seat: _seat_entry(seat, window)
            for seat, window in layout["named_seats"].items()
            if window is not None
        },
        "notes": [
            "Selectors prefer canon-backed title_contains with normalized exact title and live top-left coordinates.",
            "handoff_defaults are conservative defaults for CRONUS send_handoff.",
        ],
    }
    MAP_PATH.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    SEAT_MAP_PATH.write_text(json.dumps(seat_map, indent=2), encoding="utf-8")
    print(str(MAP_PATH))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
