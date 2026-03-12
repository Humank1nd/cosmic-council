"""
CRONUS Desktop Tool — Window discovery + mouse/keyboard automation.

Windows-only helper layer for running a live desktop fractal council.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Optional

import pyautogui
import pygetwindow as gw

from cronus.app.council.canon_adapter import normalize_title

try:
    import pyperclip
except Exception:  # pragma: no cover - optional runtime dependency
    pyperclip = None


pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


def _window_dict(window: Any) -> Dict[str, Any]:
    title = getattr(window, "title", "") or ""
    return {
        "title": title,
        "normalized_title": normalize_title(title),
        "left": int(getattr(window, "left", 0) or 0),
        "top": int(getattr(window, "top", 0) or 0),
        "width": int(getattr(window, "width", 0) or 0),
        "height": int(getattr(window, "height", 0) or 0),
        "is_active": bool(getattr(window, "isActive", False)),
        "is_minimized": bool(getattr(window, "isMinimized", False)),
        "is_maximized": bool(getattr(window, "isMaximized", False)),
    }


def _matching_windows(
    title_contains: Optional[str] = None,
    exact_title: Optional[str] = None,
) -> List[Any]:
    windows = []
    normalized_exact_title = normalize_title(exact_title).lower() if exact_title else None
    title_contains_lower = normalize_title(title_contains).lower() if title_contains else None

    for window in gw.getAllWindows():
        title = normalize_title(getattr(window, "title", "") or "")
        if not title:
            continue
        if normalized_exact_title and title.lower() != normalized_exact_title:
            continue
        if title_contains_lower and title_contains_lower not in title.lower():
            continue
        windows.append(window)

    return windows


def _best_window(arguments: Dict[str, Any]) -> Any:
    exact_title = arguments.get("exact_title")
    title_contains = arguments.get("title_contains")
    windows = _matching_windows(title_contains=title_contains, exact_title=exact_title)
    if not windows:
        raise ValueError("No matching window found")

    target_left = arguments.get("target_left")
    target_top = arguments.get("target_top")
    if target_left is not None or target_top is not None:
        left = int(target_left if target_left is not None else 0)
        top = int(target_top if target_top is not None else 0)
        return min(
            windows,
            key=lambda window: abs(int(getattr(window, "left", 0) or 0) - left)
            + abs(int(getattr(window, "top", 0) or 0) - top),
        )

    index = int(arguments.get("index", 0) or 0)
    if index < 0 or index >= len(windows):
        raise ValueError(f"Window index {index} out of range")

    return windows[index]


def _maybe_focus(window: Any, delay_seconds: float = 0.25) -> None:
    if getattr(window, "isMinimized", False):
        window.restore()
        time.sleep(delay_seconds)
    window.activate()
    time.sleep(delay_seconds)


def _safe_window_dict(window: Any) -> Optional[Dict[str, Any]]:
    if window is None:
        return None
    return _window_dict(window)


def _get_active_window() -> Any:
    getter = getattr(gw, "getActiveWindow", None)
    if getter is None:
        return None
    try:
        return getter()
    except Exception:
        return None


def _window_matches_active(window: Any, active_window: Any, arguments: Dict[str, Any]) -> bool:
    if window is None or active_window is None:
        return False

    active_title = (getattr(active_window, "title", "") or "").strip()
    window_title = (getattr(window, "title", "") or "").strip()
    exact_title = (arguments.get("exact_title") or "").strip()
    title_contains = (arguments.get("title_contains") or "").strip().lower()

    if exact_title:
        return active_title == exact_title
    if title_contains and title_contains not in active_title.lower():
        return False
    if window_title and active_title != window_title:
        return False

    active_left = int(getattr(active_window, "left", 0) or 0)
    active_top = int(getattr(active_window, "top", 0) or 0)
    window_left = int(getattr(window, "left", 0) or 0)
    window_top = int(getattr(window, "top", 0) or 0)
    return abs(active_left - window_left) <= 8 and abs(active_top - window_top) <= 8


def _focus_window(window: Any, arguments: Dict[str, Any]) -> Dict[str, Any]:
    retries = max(1, int(arguments.get("focus_retries", 3) or 3))
    delay_seconds = float(arguments.get("focus_delay_seconds", 0.25) or 0.25)
    attempts: List[Dict[str, Any]] = []

    for attempt in range(1, retries + 1):
        try:
            _maybe_focus(window, delay_seconds=delay_seconds)
        except Exception as exc:
            attempts.append({"attempt": attempt, "success": False, "error": str(exc)})
            continue

        active_window = _get_active_window()
        matched = _window_matches_active(window, active_window, arguments)
        attempts.append(
            {
                "attempt": attempt,
                "success": matched,
                "active_window": _safe_window_dict(active_window),
            }
        )
        if matched:
            return {
                "success": True,
                "attempts": attempt,
                "window": _window_dict(window),
                "active_window": _safe_window_dict(active_window),
                "attempt_log": attempts,
            }

    return {
        "success": False,
        "attempts": retries,
        "window": _window_dict(window),
        "active_window": _safe_window_dict(_get_active_window()),
        "attempt_log": attempts,
        "error": "target window did not become active",
    }


def _compute_click_target(window: Any, arguments: Dict[str, Any]) -> Dict[str, Any]:
    left = int(getattr(window, "left", 0) or 0)
    top = int(getattr(window, "top", 0) or 0)
    width = int(getattr(window, "width", 0) or 0)
    height = int(getattr(window, "height", 0) or 0)
    if width <= 0 or height <= 0:
        return {
            "success": False,
            "error": "target window has invalid bounds",
            "window": _window_dict(window),
        }

    if arguments.get("input_x") is not None and arguments.get("input_y") is not None:
        click_x = int(arguments["input_x"])
        click_y = int(arguments["input_y"])
        strategy = "absolute"
    else:
        input_offset_y = int(arguments.get("input_offset_y", 42) or 42)
        input_ratio_x = float(arguments.get("input_ratio_x", 0.5) or 0.5)
        click_x = int(left + (width * input_ratio_x))
        click_y = int(top + height - input_offset_y)
        strategy = "bottom_offset"

    right = left + width - 1
    bottom = top + height - 1
    bottom_offset = bottom - click_y
    band_min_offset = max(0, int(arguments.get("input_band_min_offset_y", 24) or 24))
    band_max_offset = max(band_min_offset, int(arguments.get("input_band_max_offset_y", 120) or 120))
    padding_x = max(0, int(arguments.get("input_padding_x", 16) or 16))

    safe_left = left + min(padding_x, max(0, width // 2))
    safe_right = right - min(padding_x, max(0, width // 2))
    if safe_left > safe_right:
        safe_left = left
        safe_right = right

    in_window = left <= click_x <= right and top <= click_y <= bottom
    in_input_band = band_min_offset <= bottom_offset <= band_max_offset
    x_within_safe_band = safe_left <= click_x <= safe_right

    target = {
        "x": click_x,
        "y": click_y,
        "strategy": strategy,
        "bottom_offset_y": bottom_offset,
        "in_window": in_window,
        "in_input_band": in_input_band,
        "x_within_safe_band": x_within_safe_band,
        "band_min_offset_y": band_min_offset,
        "band_max_offset_y": band_max_offset,
        "safe_left": safe_left,
        "safe_right": safe_right,
    }
    if in_window and in_input_band and x_within_safe_band:
        return {"success": True, "target": target}

    issues = []
    if not in_window:
        issues.append("click target is outside the window bounds")
    if not in_input_band:
        issues.append("click target is outside the expected input band")
    if not x_within_safe_band:
        issues.append("click target is too close to the horizontal window edge")
    return {
        "success": False,
        "error": "; ".join(issues),
        "window": _window_dict(window),
        "target": target,
    }


def _clear_existing_draft(arguments: Dict[str, Any]) -> Dict[str, Any]:
    if not arguments.get("clear_input", False):
        return {"requested": False, "performed": False}

    hotkey = arguments.get("clear_hotkey", ["ctrl", "a"])
    if not isinstance(hotkey, Iterable) or isinstance(hotkey, (str, bytes)):
        return {"requested": True, "performed": False, "error": "clear_hotkey must be a list"}

    keys = list(hotkey)
    if not keys:
        return {"requested": True, "performed": False, "error": "clear_hotkey must not be empty"}

    interval = float(arguments.get("interval", 0.01) or 0.01)
    pyautogui.hotkey(*keys, interval=interval)
    time.sleep(float(arguments.get("clear_pause_seconds", 0.05) or 0.05))
    clear_key = arguments.get("clear_key", "backspace")
    clear_presses = max(1, int(arguments.get("clear_key_presses", 1) or 1))
    pyautogui.press(clear_key, presses=clear_presses, interval=interval)
    time.sleep(float(arguments.get("clear_pause_seconds", 0.05) or 0.05))
    return {
        "requested": True,
        "performed": True,
        "hotkey": keys,
        "clear_key": clear_key,
        "clear_key_presses": clear_presses,
    }


def _write_message(message: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    interval = float(arguments.get("interval", 0.01) or 0.01)
    method = str(arguments.get("text_entry_method", "auto") or "auto").lower()
    paste_threshold = max(1, int(arguments.get("paste_threshold", 280) or 280))

    use_paste = method == "paste" or (method == "auto" and len(message) >= paste_threshold and pyperclip is not None)
    if use_paste:
        if pyperclip is None:
            if method == "paste":
                return {"success": False, "error": "pyperclip is unavailable for paste mode"}
            use_paste = False
        else:
            previous_clipboard = None
            try:
                previous_clipboard = pyperclip.paste()
            except Exception:
                previous_clipboard = None
            try:
                pyperclip.copy(message)
                pyautogui.hotkey("ctrl", "v", interval=interval)
            except Exception as exc:
                return {"success": False, "error": f"clipboard paste failed: {exc}"}
            finally:
                if previous_clipboard is not None:
                    try:
                        pyperclip.copy(previous_clipboard)
                    except Exception:
                        pass
            return {
                "success": True,
                "method": "paste",
                "characters": len(message),
            }

    pyautogui.write(message, interval=interval)
    return {
        "success": True,
        "method": "type",
        "characters": len(message),
    }


def _delivery_confidence(
    focus_verified: bool,
    click_target_verified: bool,
    target_window_verified: bool,
    submit_requested: bool,
    submit_attempted: bool,
    submit_verified: bool,
) -> str:
    if not focus_verified or not click_target_verified:
        return "low"
    if submit_requested and not submit_attempted:
        return "low"
    if submit_verified:
        return "high"
    if target_window_verified:
        return "medium"
    if submit_requested:
        return "low"
    return "medium"


def _submit_action(submit_mode: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    normalized_mode = str(submit_mode or "enter").strip().lower()
    interval = float(arguments.get("submit_interval", arguments.get("interval", 0.01)) or 0.01)
    pause_seconds = float(arguments.get("submit_pause_seconds", 0.1) or 0.1)

    try:
        if normalized_mode == "ctrl-enter":
            pyautogui.hotkey("ctrl", "enter", interval=interval)
        elif normalized_mode == "both":
            pyautogui.hotkey("ctrl", "enter", interval=interval)
            time.sleep(pause_seconds)
            pyautogui.press("enter")
        else:
            normalized_mode = "enter"
            presses = max(1, int(arguments.get("submit_presses", 1) or 1))
            pyautogui.press("enter", presses=presses, interval=interval)
    except Exception as exc:
        return {
            "success": False,
            "submit_mode": normalized_mode,
            "submit_verification": "attempt_failed",
            "error": str(exc),
        }

    time.sleep(pause_seconds)
    return {
        "success": True,
        "submit_mode": normalized_mode,
        "submit_verification": "not_available",
    }


def handle_list_windows(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    List visible windows.

    Args:
      title_contains: optional substring filter
      exact_title: optional exact title filter
    """
    exact_title = arguments.get("exact_title")
    title_contains = arguments.get("title_contains")
    windows = _matching_windows(title_contains=title_contains, exact_title=exact_title)
    return {
        "success": True,
        "count": len(windows),
        "windows": [_window_dict(window) for window in windows],
    }


def handle_focus_window(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Focus a window by title.

    Args:
      exact_title or title_contains
      index: optional match index
      dry_run: if true, only report
    """
    window = _best_window(arguments)
    if arguments.get("dry_run", False):
        return {
            "success": True,
            "dry_run": True,
            "window": _window_dict(window),
        }

    focus_result = _focus_window(window, arguments)
    if not focus_result.get("success"):
        return focus_result
    return focus_result


def handle_desktop_input(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform a mouse/keyboard action.

    Required:
      action: move | click | double_click | right_click | type_text | press | hotkey | scroll

    Safety:
      confirm: must be true for execution. Otherwise the tool reports the planned action.
    """
    action = arguments.get("action")
    if not action:
        return {"success": False, "error": "action is required"}

    if not arguments.get("confirm", False):
        return {
            "success": True,
            "dry_run": True,
            "planned_action": action,
            "arguments": {k: v for k, v in arguments.items() if k != "confirm"},
        }

    focus_first = arguments.get("focus_first", False)
    if focus_first:
        window = _best_window(arguments)
        focus_result = _focus_window(window, arguments)
        if not focus_result.get("success"):
            return focus_result

    pause = float(arguments.get("pause_seconds", 0.1) or 0.1)
    x = arguments.get("x")
    y = arguments.get("y")

    if action == "move":
        if x is None or y is None:
            return {"success": False, "error": "x and y are required for move"}
        pyautogui.moveTo(int(x), int(y), duration=float(arguments.get("duration", 0)))
    elif action == "click":
        pyautogui.click(x=None if x is None else int(x), y=None if y is None else int(y), button=arguments.get("button", "left"))
    elif action == "double_click":
        pyautogui.doubleClick(x=None if x is None else int(x), y=None if y is None else int(y), button=arguments.get("button", "left"))
    elif action == "right_click":
        pyautogui.rightClick(x=None if x is None else int(x), y=None if y is None else int(y))
    elif action == "type_text":
        text = arguments.get("text", "")
        pyautogui.write(text, interval=float(arguments.get("interval", 0.01)))
    elif action == "press":
        key = arguments.get("key")
        if not key:
            return {"success": False, "error": "key is required for press"}
        presses = int(arguments.get("presses", 1) or 1)
        pyautogui.press(key, presses=presses, interval=float(arguments.get("interval", 0.05)))
    elif action == "hotkey":
        keys = arguments.get("keys")
        if not isinstance(keys, Iterable) or isinstance(keys, (str, bytes)):
            return {"success": False, "error": "keys must be a list for hotkey"}
        pyautogui.hotkey(*list(keys), interval=float(arguments.get("interval", 0.05)))
    elif action == "scroll":
        amount = int(arguments.get("amount", 0) or 0)
        pyautogui.scroll(amount, x=None if x is None else int(x), y=None if y is None else int(y))
    else:
        return {"success": False, "error": f"Unsupported action: {action}"}

    time.sleep(pause)
    return {
        "success": True,
        "action": action,
        "cursor": pyautogui.position()._asdict(),
    }


def handle_send_handoff(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Focus a target window, click its input area, type a handoff message, and optionally submit it.

    Args:
      exact_title or title_contains: target window selector
      message: text to type
      submit: send after typing
      submit_mode: enter | ctrl-enter | both
      input_offset_y: distance from bottom edge to click (default 42)
      input_ratio_x: horizontal click ratio across the window (default 0.5)
      input_band_min_offset_y / input_band_max_offset_y: expected input band near the bottom
      clear_input: select-all and clear before typing
      text_entry_method: auto | type | paste
      confirm: must be true for execution
    """
    message = arguments.get("message")
    if not message:
        return {"success": False, "error": "message is required"}

    window = _best_window(arguments)
    target_result = _compute_click_target(window, arguments)
    if not target_result.get("success"):
        return target_result
    click_target = target_result["target"]
    submit_requested = bool(arguments.get("submit", True))
    submit_mode = str(arguments.get("submit_mode", "enter") or "enter").strip().lower()

    if not arguments.get("confirm", False):
        return {
            "success": True,
            "dry_run": True,
            "window": _window_dict(window),
            "click_target": click_target,
            "message_preview": message,
            "submit_requested": submit_requested,
            "submit_attempted": False,
            "submitted": False,
            "verification": {
                "focus_verified": False,
                "click_target_verified": True,
                "text_entry_method": str(arguments.get("text_entry_method", "auto") or "auto").lower(),
                "text_verification": "dry-run",
                "submit_mode": submit_mode,
                "submit_verification": "dry-run",
            },
            "delivery_confidence": "dry-run",
        }

    focus_result = _focus_window(window, arguments)
    if not focus_result.get("success"):
        return focus_result

    focus_pause_seconds = float(arguments.get("focus_pause_seconds", 0.15) or 0.15)

    pyautogui.click(click_target["x"], click_target["y"])
    time.sleep(focus_pause_seconds)
    clear_result = _clear_existing_draft(arguments)
    if clear_result.get("error"):
        return {"success": False, "error": clear_result["error"], "window": _window_dict(window)}

    entry_result = _write_message(message, arguments)
    if not entry_result.get("success"):
        return {"success": False, "error": entry_result["error"], "window": _window_dict(window)}

    active_before_submit = _get_active_window()
    active_before_submit_verified = _window_matches_active(window, active_before_submit, arguments)
    submit_refocus_result = None
    if submit_requested and not active_before_submit_verified:
        submit_refocus_result = _focus_window(window, arguments)
        if submit_refocus_result.get("success"):
            pyautogui.click(click_target["x"], click_target["y"])
            time.sleep(focus_pause_seconds)
            active_before_submit = _get_active_window()
            active_before_submit_verified = _window_matches_active(window, active_before_submit, arguments)

    submit_result = {
        "success": not submit_requested,
        "submit_mode": submit_mode,
        "submit_verification": "not_requested",
    }
    if submit_requested:
        submit_result = _submit_action(submit_mode, arguments)

    active_after_submit = _get_active_window()
    active_after_submit_verified = _window_matches_active(window, active_after_submit, arguments)
    submit_attempted = bool(submit_requested and submit_result.get("success"))
    submit_verified = bool(submit_result.get("submit_verified", False))
    if submit_requested and submit_attempted and not submit_verified and active_before_submit_verified:
        submit_verified = True
        submit_result = {
            **submit_result,
            "submit_verified": True,
            "submit_verification": "active-window-inferred",
        }
    verification = {
        "focus_verified": True,
        "focus_attempts": focus_result.get("attempts"),
        "focus_attempt_log": focus_result.get("attempt_log", []),
        "click_target_verified": True,
        "clear_input_requested": clear_result.get("requested", False),
        "clear_input_performed": clear_result.get("performed", False),
        "text_entry_method": entry_result.get("method"),
        "text_verification": "not_available",
        "active_window_before_submit": _safe_window_dict(active_before_submit),
        "active_before_submit_verified": active_before_submit_verified,
        "submit_refocus_attempted": bool(submit_refocus_result is not None),
        "submit_refocus_result": submit_refocus_result,
        "submit_mode": submit_result.get("submit_mode", submit_mode),
        "submit_verification": submit_result.get("submit_verification", "not_available"),
        "submit_error": submit_result.get("error"),
        "active_window_after_submit": _safe_window_dict(active_after_submit),
        "active_after_submit_verified": active_after_submit_verified,
    }
    target_window_verified = active_before_submit_verified or active_after_submit_verified

    return {
        "success": True,
        "window": _window_dict(window),
        "click_target": click_target,
        "submit_requested": submit_requested,
        "submit_attempted": submit_attempted,
        "submitted": submit_verified,
        "verification": verification,
        "delivery_confidence": _delivery_confidence(
            focus_verified=True,
            click_target_verified=True,
            target_window_verified=target_window_verified,
            submit_requested=submit_requested,
            submit_attempted=submit_attempted,
            submit_verified=submit_verified,
        ),
    }
