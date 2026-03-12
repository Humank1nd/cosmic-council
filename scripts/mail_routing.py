import json
import sys

sys.path.insert(0, r"D:\dream-caesar\src")

from cronus.app.council.canon_adapter import next_outer_seat, outer_seats  # noqa: E402
from desktop_runtime import ACTIVE_CANON_PATH  # noqa: E402


ACTIVE_CANON_THREAD = "DC-ACTIVE-CANON"
COORDINATOR_THREAD = "DC-COORDINATOR"
COORDINATOR_SEAT = "dream-caesar"
ACTIVE_CANON_THREAD_ALIASES = {
    "",
    "ACTIVE-CANON",
    "JB-ACTIVE-CANON",
    ACTIVE_CANON_THREAD,
}
COORDINATOR_THREAD_ALIASES = {
    "COORDINATOR",
    "DC-CONTROL",
    COORDINATOR_THREAD,
}
CANONICAL_SEATS = outer_seats()


def normalize_thread(thread: str | None) -> str:
    normalized = (thread or "").strip().upper()
    if normalized in ACTIVE_CANON_THREAD_ALIASES:
        return ACTIVE_CANON_THREAD if normalized else ""
    if normalized in COORDINATOR_THREAD_ALIASES:
        return COORDINATOR_THREAD
    return normalized


def load_active_seats() -> list[str] | None:
    if not ACTIVE_CANON_PATH.exists():
        return None
    try:
        data = json.loads(ACTIVE_CANON_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    seats = data.get("active_seats")
    if not isinstance(seats, list):
        return None
    normalized = [
        str(seat).lower()
        for seat in seats
        if isinstance(seat, str) and str(seat).lower() in CANONICAL_SEATS
    ]
    return normalized or None


def resolve_ring_recipient(sender: str, seat_ring: list[str]) -> str | None:
    normalized_sender = sender.lower()
    if normalized_sender not in seat_ring or not seat_ring:
        return None
    sender_index = seat_ring.index(normalized_sender)
    return seat_ring[(sender_index + 1) % len(seat_ring)]


def resolve_canonical_recipient(sender: str) -> str | None:
    normalized_sender = sender.lower()
    if normalized_sender not in CANONICAL_SEATS:
        return None
    return next_outer_seat(normalized_sender)


def resolve_allowed_recipient(
    sender: str,
    thread: str | None = None,
    active_seats: list[str] | None = None,
) -> str | None:
    normalized_sender = sender.lower()
    normalized_thread = normalize_thread(thread)
    if normalized_thread == COORDINATOR_THREAD:
        if normalized_sender == COORDINATOR_SEAT:
            return None
        if normalized_sender in CANONICAL_SEATS:
            return COORDINATOR_SEAT
        return None
    if normalized_thread == ACTIVE_CANON_THREAD:
        return resolve_ring_recipient(sender, active_seats or [])
    return resolve_canonical_recipient(sender)
