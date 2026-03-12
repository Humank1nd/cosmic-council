"""
Thin adapter between Cosmic Council canon and desktop council routing.

The six outer seats come from cosmic_council.canon. The desktop-only
"center" seat stays local to the desktop orchestration layer.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List

from cosmic_council.canon import COSMIC_COUNCIL_CANON, ROYGBV_ORDER, TotemCanon, TotemColor, get_next_totem


CENTER_SEAT = "center"
CENTER_TITLE = "Dream Caesar"
OUTER_SEAT_ORDER = [color.value for color in ROYGBV_ORDER]
COMPATIBILITY_ALIASES: Dict[str, List[str]] = {
    "green": ["Green Turtle"],
}


class SeatResolutionError(ValueError):
    pass


def normalize_title(title: str | None) -> str:
    return re.sub(r"\s+", " ", (title or "")).strip()


def outer_seats() -> list[str]:
    return list(OUTER_SEAT_ORDER)


def all_seats(include_center: bool = True) -> list[str]:
    if include_center:
        return [CENTER_SEAT, *OUTER_SEAT_ORDER]
    return outer_seats()


def seat_color(seat: str) -> TotemColor | None:
    normalized = seat.lower()
    for color in ROYGBV_ORDER:
        if color.value == normalized:
            return color
    return None


def seat_canon(seat: str) -> TotemCanon | None:
    color = seat_color(seat)
    if color is None:
        return None
    return COSMIC_COUNCIL_CANON[color]


def seat_title(seat: str) -> str:
    normalized = seat.lower()
    if normalized == CENTER_SEAT:
        return CENTER_TITLE
    canon = seat_canon(normalized)
    if canon is None:
        return seat.title()
    return canon.name


def seat_aliases(seat: str) -> list[str]:
    normalized = seat.lower()
    if normalized == CENTER_SEAT:
        return [CENTER_TITLE, "Center"]

    title = seat_title(normalized)
    aliases = [title, normalized.title()]
    aliases.extend(COMPATIBILITY_ALIASES.get(normalized, []))

    seen: set[str] = set()
    ordered: list[str] = []
    for alias in aliases:
        if alias not in seen:
            seen.add(alias)
            ordered.append(alias)
    return ordered


def title_matches_seat(title: str | None, seat: str) -> bool:
    normalized_title = normalize_title(title).lower()
    if not normalized_title:
        return False
    return any(normalize_title(alias).lower() in normalized_title for alias in seat_aliases(seat))


def window_selector_for_seat(seat: str, window: dict[str, Any]) -> dict[str, Any]:
    return {
        "title_contains": seat_title(seat),
        "exact_title": normalize_title(window.get("title", "")),
        "target_left": window.get("left"),
        "target_top": window.get("top"),
    }


def _distance(window: dict[str, Any], target_left: int | None, target_top: int | None) -> int:
    left = int(window.get("left", 0) or 0)
    top = int(window.get("top", 0) or 0)
    expected_left = int(target_left if target_left is not None else left)
    expected_top = int(target_top if target_top is not None else top)
    return abs(left - expected_left) + abs(top - expected_top)


def _pick_unique_window(
    candidates: Iterable[dict[str, Any]],
    *,
    seat: str,
    target_left: int | None = None,
    target_top: int | None = None,
    label: str,
) -> dict[str, Any]:
    items = list(candidates)
    if len(items) == 1:
        return items[0]

    if (target_left is not None or target_top is not None) and items:
        ranked = sorted(items, key=lambda window: (_distance(window, target_left, target_top), normalize_title(window.get("title", "")).lower()))
        if len(ranked) == 1 or _distance(ranked[0], target_left, target_top) < _distance(ranked[1], target_left, target_top):
            return ranked[0]

    titles = ", ".join(normalize_title(item.get("title", "")) or "<untitled>" for item in items[:4])
    if len(items) > 4:
        titles += ", ..."
    raise SeatResolutionError(f"{label} for seat {seat}: {titles}")


def resolve_seat_window(
    windows: Iterable[dict[str, Any]],
    seat: str,
    *,
    exact_title: str | None = None,
    target_left: int | None = None,
    target_top: int | None = None,
) -> dict[str, Any]:
    items = [window for window in windows if normalize_title(window.get("title", ""))]
    normalized_exact = normalize_title(exact_title).lower()
    canonical_lower = normalize_title(seat_title(seat)).lower()
    alias_lowers = [normalize_title(alias).lower() for alias in seat_aliases(seat)]

    if normalized_exact:
        exact_matches = [
            window for window in items if normalize_title(window.get("title", "")).lower() == normalized_exact
        ]
        seat_exact_matches = [window for window in exact_matches if title_matches_seat(window.get("title", ""), seat)]
        if seat_exact_matches:
            return _pick_unique_window(
                seat_exact_matches,
                seat=seat,
                target_left=target_left,
                target_top=target_top,
                label="Ambiguous saved exact-title match",
            )

    exact_canonical = [
        window for window in items if normalize_title(window.get("title", "")).lower() == canonical_lower
    ]
    if exact_canonical:
        return _pick_unique_window(
            exact_canonical,
            seat=seat,
            target_left=target_left,
            target_top=target_top,
            label="Ambiguous canonical exact-title match",
        )

    exact_alias = [
        window for window in items if normalize_title(window.get("title", "")).lower() in alias_lowers
    ]
    if exact_alias:
        return _pick_unique_window(
            exact_alias,
            seat=seat,
            target_left=target_left,
            target_top=target_top,
            label="Ambiguous alias exact-title match",
        )

    contains_canonical = [
        window for window in items if canonical_lower in normalize_title(window.get("title", "")).lower()
    ]
    if contains_canonical:
        return _pick_unique_window(
            contains_canonical,
            seat=seat,
            target_left=target_left,
            target_top=target_top,
            label="Ambiguous canonical title match",
        )

    contains_alias = [
        window
        for window in items
        if any(alias in normalize_title(window.get("title", "")).lower() for alias in alias_lowers)
    ]
    if contains_alias:
        return _pick_unique_window(
            contains_alias,
            seat=seat,
            target_left=target_left,
            target_top=target_top,
            label="Ambiguous alias title match",
        )

    raise SeatResolutionError(f"No live window matched seat {seat}")


def seat_role(seat: str) -> str | None:
    canon = seat_canon(seat)
    return canon.role if canon else None


def seat_purpose(seat: str) -> str | None:
    canon = seat_canon(seat)
    return canon.purpose if canon else None


def seat_guiding_question(seat: str) -> str | None:
    canon = seat_canon(seat)
    return canon.guiding_question if canon else None


def seat_mission_pillar(seat: str) -> str | None:
    canon = seat_canon(seat)
    return canon.mission_pillar if canon else None


def seat_guiding_thought(seat: str) -> str | None:
    canon = seat_canon(seat)
    return canon.guiding_thought if canon else None


def seat_key_responsibilities(seat: str) -> list[str]:
    canon = seat_canon(seat)
    return list(canon.key_responsibilities) if canon else []


def next_outer_seat(seat: str) -> str | None:
    color = seat_color(seat)
    if color is None:
        return None
    return get_next_totem(color).value
