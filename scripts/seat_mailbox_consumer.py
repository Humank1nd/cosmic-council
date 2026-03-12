import argparse
import json
import re
import sys
import time
from argparse import Namespace
from datetime import datetime
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
SRC_ROOT = REPO_ROOT / "src"
CRONUS_ROOT = REPO_ROOT / "CRONUS"

for candidate in (SRC_ROOT, SCRIPT_ROOT):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

from cosmic_council.canon.cosmic_canon import COSMIC_COUNCIL_CANON, TOTEM_DEEP_PROFILES
from cronus.app.council.canon_adapter import next_outer_seat, seat_color, seat_guiding_question, seat_mission_pillar, seat_role, seat_title
from desktop_runtime import ACTIVE_CANON_PATH, ARTIFACT_ROOT, HANDOFF_DIR, MAIL_ROOT, RUNTIME_ROOT, ensure_runtime_dirs
from internal_mail import send_mail
from mail_routing import CANONICAL_SEATS, COORDINATOR_SEAT, COORDINATOR_THREAD, load_active_seats


STATUS_PATH = RUNTIME_ROOT / "seat-mailbox-consumer-status.json"
STATE_PATH = RUNTIME_ROOT / "seat-mailbox-consumer-state.json"
LOG_PATH = RUNTIME_ROOT / "seat-mailbox-consumer.jsonl"
ALIGNMENT_PATH = RUNTIME_ROOT / "canon-seat-alignment.json"
WATCHDOG_STATUS_PATH = ARTIFACT_ROOT / "desktop-council-watchdog-status.json"
RELAY_STATUS_PATH = RUNTIME_ROOT / "terminal-langchain-status.json"
CANON_PATH = SRC_ROOT / "cosmic_council" / "canon" / "cosmic_canon.py"
ADAPTER_PATH = SRC_ROOT / "cronus" / "app" / "council" / "canon_adapter.py"

ROLE_OWNERSHIP = {
    "red": [
        str(SCRIPT_ROOT / "internal_mail.py"),
        str(SCRIPT_ROOT / "mail_routing.py"),
        str(CRONUS_ROOT / "app" / "agents" / "runtime.py"),
    ],
    "orange": [
        str(SCRIPT_ROOT / "desktop_council_watchdog.py"),
        str(RUNTIME_ROOT / "plans" / "20260311-1305-alignment-plan.md"),
        str(CRONUS_ROOT / "api" / "main.py"),
    ],
    "yellow": [
        str(SCRIPT_ROOT / "desktop_handoff_runner.py"),
        str(SCRIPT_ROOT / "desktop_fractal_council_probe.py"),
        str(SCRIPT_ROOT / "active_canon_terminal_worker.py"),
        str(CRONUS_ROOT / "run_cronus.py"),
    ],
    "green": [
        str(SRC_ROOT / "cronus" / "app" / "tools" / "desktop.py"),
        str(SCRIPT_ROOT / "desktop_runtime.py"),
        str(CRONUS_ROOT / "config" / "config.toml"),
    ],
    "blue": [
        str(RUNTIME_ROOT / "canon-seat-alignment.json"),
        str(RUNTIME_ROOT / "terminal-langchain-status.json"),
        str(CRONUS_ROOT / "mcp_server.py"),
    ],
    "purple": [
        str(RUNTIME_ROOT / "active-canon.json"),
        str(ARTIFACT_ROOT / "desktop-council-watchdog-status.json"),
        str(CRONUS_ROOT / "autonomous_daemon.py"),
    ],
}

ROLE_AVOIDS = {
    "red": "Do not drift into direct strategy, implementation, or coordinator spoofing.",
    "orange": "Do not replace validated truth with speculation or skip sequencing.",
    "yellow": "Do not treat unverified prototypes as production truth.",
    "green": "Do not ignore runtime sustainability, reliability, or operator load.",
    "blue": "Do not collapse communication into canon-breaking shortcuts or stale prompts.",
    "purple": "Do not override the ring with self-routing or bypass ethics review.",
}


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _canon_bundle(seat: str) -> dict:
    color = seat_color(seat)
    canon = COSMIC_COUNCIL_CANON[color] if color else None
    deep = TOTEM_DEEP_PROFILES.get(color, {}) if color else {}
    return {"canon": canon, "deep": deep}


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {"processed_paths": []}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"processed_paths": []}


def _save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _read_mail(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    subject = ""
    sender = ""
    recipient = ""
    thread = ""
    body_lines: list[str] = []
    in_body = False
    for line in lines:
        if line.startswith("# Mail "):
            subject = line[len("# Mail ") :].strip()
        elif line.startswith("FROM: "):
            sender = line[len("FROM: ") :].strip().lower()
        elif line.startswith("TO: "):
            recipient = line[len("TO: ") :].strip().lower()
        elif line.startswith("THREAD: "):
            thread = line[len("THREAD: ") :].strip().upper()
        elif line == "## Body":
            in_body = True
            continue
        elif line == "## Attachments":
            in_body = False
        elif in_body:
            body_lines.append(line)
    return {
        "path": str(path),
        "subject": subject,
        "from": sender,
        "to": recipient,
        "thread": thread,
        "body": "\n".join(body_lines).strip(),
    }


def _active_owned_paths(seat: str) -> list[str]:
    return ROLE_OWNERSHIP.get(seat, [])


def _format_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) or "- none"


def _responsibility_area_lines(deep: dict) -> list[str]:
    areas = deep.get("responsibility_areas") or {}
    lines: list[str] = []
    for area, bullets in areas.items():
        title = area.replace("_", " ")
        lines.append(f"- {title}:")
        for bullet in bullets[:2]:
            lines.append(f"  - {bullet}")
    return lines


def _example_lines(deep: dict) -> list[str]:
    examples = deep.get("examples_in_action") or []
    lines: list[str] = []
    for example in examples[:2]:
        context = example.get("context")
        problem = example.get("problem")
        actions = example.get("actions") or []
        lines.append(f"- {context}: {problem}")
        for action in actions[:2]:
            lines.append(f"  - {action}")
    return lines


def _relationship_lines(deep: dict) -> list[str]:
    relationships = deep.get("relationships") or {}
    lines: list[str] = []
    for seat, value in relationships.items():
        label = seat.value if hasattr(seat, "value") else str(seat)
        lines.append(f"- {label}: {value}")
    return lines


def _channel_lines(deep: dict) -> list[str]:
    return [f"- {line}" for line in (deep.get("how_to_channel") or [])[:5]]


def _next_seat_shaping(seat: str, deep: dict) -> str:
    relationships = deep.get("relationships") or {}
    if not relationships:
        return "Use my canon relationships to prepare the next seat with validated truth, not assumptions."
    by_name = {
        (key.value if hasattr(key, "value") else str(key)).lower(): value
        for key, value in relationships.items()
    }
    canonical_next = next_outer_seat(seat)
    if canonical_next and canonical_next in by_name:
        return f"For {canonical_next.title()} next: {by_name[canonical_next]}"
    first_key = next(iter(by_name), None)
    if first_key:
        return f"For {first_key.title()} next: {by_name[first_key]}"
    return "Use my canon relationships to prepare the next seat with validated truth, not assumptions."


def _latest_seat_mail(seat: str) -> str | None:
    mailbox = MAIL_ROOT / seat
    latest = max(mailbox.glob("*.md"), key=lambda item: item.stat().st_mtime, default=None)
    return str(latest) if latest else None


def _latest_handoff() -> str | None:
    latest = max(HANDOFF_DIR.glob("*.md"), key=lambda item: item.stat().st_mtime, default=None)
    return str(latest) if latest else None


def _runtime_bundle(seat: str) -> dict:
    watchdog = _read_json(WATCHDOG_STATUS_PATH)
    relay = _read_json(RELAY_STATUS_PATH)
    active_canon = _read_json(ACTIVE_CANON_PATH)
    latest_mail_record = watchdog.get("latest_mail_record") or {}
    return {
        "objective": active_canon.get("objective"),
        "active_seats": active_canon.get("active_seats") or [],
        "required_paths": active_canon.get("required_paths") or [],
        "queue_state": watchdog.get("queue_state"),
        "queue_reasons": watchdog.get("queue_reasons") or [],
        "mail_age_seconds": watchdog.get("mail_age_seconds"),
        "latest_handoff": watchdog.get("latest_handoff") or relay.get("note_path") or _latest_handoff(),
        "latest_mail_record": latest_mail_record,
        "latest_mail_for_seat": _latest_seat_mail(seat),
    }


def _response_body(seat: str, source_mail: dict) -> str:
    bundle = _canon_bundle(seat)
    canon = bundle["canon"]
    deep = bundle["deep"]
    owned_paths = _active_owned_paths(seat)
    owned_lines = _format_bullets(owned_paths)
    key_responsibilities = _format_bullets(list(canon.key_responsibilities[:3]) if canon else [])
    expanded_questions = _format_bullets(list((deep.get("expanded_guiding_questions") or [])[:5]))
    responsibility_area_lines = "\n".join(_responsibility_area_lines(deep)) or "- none"
    example_lines = "\n".join(_example_lines(deep)) or "- none"
    downstream_lines = "\n".join(_relationship_lines(deep)) or "- none"
    channel_lines = "\n".join(_channel_lines(deep)) or "- none"
    runtime = _runtime_bundle(seat)
    runtime_paths = _format_bullets(list(runtime.get("required_paths", [])[:12]))
    queue_reasons = _format_bullets(list(runtime.get("queue_reasons", [])))
    next_shape = _next_seat_shaping(seat, deep)
    root_failure = (
        "A canon error occurs when I jump to planning or implementation before proving the root cause, "
        "which means I am solving a symptom instead of the actual problem."
    )
    return (
        f"SOURCE_MAIL: {source_mail['path']}\n"
        f"SEAT: {seat}\n"
        f"TITLE: {seat_title(seat)}\n"
        f"ROLE: {seat_role(seat)}\n"
        f"POSITION_IN_CYCLE: {deep.get('position_in_cycle', '')}\n"
        f"PURPOSE: {canon.purpose if canon else ''}\n"
        f"MISSION_PILLAR: {seat_mission_pillar(seat)}\n"
        f"GUIDING_THOUGHT: {canon.guiding_thought if canon else ''}\n"
        f"GUIDING_QUESTION: {seat_guiding_question(seat)}\n"
        f"CURRENT_RESPONSIBILITY: Own the truth and maintenance of {owned_paths[0] if owned_paths else 'canon-aligned runtime scope'} right now.\n"
        f"AVOID: {ROLE_AVOIDS.get(seat, 'Do not drift outside canon.')}\n\n"
        "## Key Responsibilities\n\n"
        f"{key_responsibilities}\n\n"
        "## Deep Responsibility Areas\n\n"
        f"{responsibility_area_lines}\n\n"
        "## Expanded Guiding Questions\n\n"
        f"{expanded_questions}\n\n"
        "## Examples In Action\n\n"
        f"{example_lines}\n\n"
        "## How To Channel This Seat\n\n"
        f"{channel_lines}\n\n"
        "## Downstream Impact On The Ring\n\n"
        f"{downstream_lines}\n\n"
        "## Live Runtime State\n\n"
        f"OBJECTIVE: {runtime.get('objective')}\n"
        f"ACTIVE_SEATS: {', '.join(runtime.get('active_seats', []))}\n"
        f"QUEUE_STATE: {runtime.get('queue_state')}\n"
        f"QUEUE_REASONS:\n{queue_reasons}\n"
        f"MAIL_AGE_SECONDS: {runtime.get('mail_age_seconds')}\n"
        f"LATEST_HANDOFF: {runtime.get('latest_handoff')}\n"
        f"LATEST_MAIL_FOR_SEAT: {runtime.get('latest_mail_for_seat')}\n"
        f"LATEST_MAIL_RECORD_PATH: {(runtime.get('latest_mail_record') or {}).get('path')}\n\n"
        "## Required Runtime Paths In Scope\n\n"
        f"{runtime_paths}\n\n"
        "## Next Seat Shaping\n\n"
        f"{next_shape}\n\n"
        "## Root Problem Guardrail\n\n"
        f"{root_failure}\n\n"
        "## Exact Paths\n\n"
        f"{owned_lines}\n\n"
        "## Canon Alignment\n\n"
        "I am responding on the coordinator thread as my canonical seat, not as Dream Caesar and not as another totem.\n"
    )


def _coordinator_mail(seat: str, state: dict) -> list[dict]:
    mailbox = MAIL_ROOT / seat
    if not mailbox.exists():
        return []
    processed = set(state.get("processed_paths", []))
    messages = []
    for path in sorted(mailbox.glob("*.md"), key=lambda item: item.stat().st_mtime):
        if str(path) in processed:
            continue
        parsed = _read_mail(path)
        if parsed["thread"] != COORDINATOR_THREAD:
            continue
        if parsed["from"] != COORDINATOR_SEAT or parsed["to"] != seat:
            continue
        messages.append(parsed)
    return messages


def _reply_to_coordinator(seat: str, source_mail: dict) -> str:
    subject = f"coordinator-reply-{seat}-{_slugify(source_mail['subject'])}"
    args = Namespace(
        sender=seat,
        to=COORDINATOR_SEAT,
        subject=subject,
        body=_response_body(seat, source_mail),
        thread=COORDINATOR_THREAD,
        priority="high",
        attachments=[
            source_mail["path"],
            str(ALIGNMENT_PATH),
            str(CANON_PATH),
            str(ADAPTER_PATH),
            *ROLE_OWNERSHIP.get(seat, []),
        ],
    )
    send_mail(args)
    mailbox = MAIL_ROOT / COORDINATOR_SEAT
    latest = max(mailbox.glob("*.md"), key=lambda item: item.stat().st_mtime, default=None)
    return str(latest) if latest else ""


def run_once() -> dict:
    ensure_runtime_dirs()
    state = _load_state()
    active_seats = load_active_seats() or list(CANONICAL_SEATS)
    processed_now: list[dict] = []

    for seat in active_seats:
        for source_mail in _coordinator_mail(seat, state):
            reply_path = _reply_to_coordinator(seat, source_mail)
            processed_now.append(
                {
                    "seat": seat,
                    "source_mail": source_mail["path"],
                    "reply_mail": reply_path,
                    "thread": COORDINATOR_THREAD,
                }
            )
            state.setdefault("processed_paths", []).append(source_mail["path"])

    _save_state(state)
    record = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "active_seats": active_seats,
        "processed": processed_now,
        "processed_count": len(processed_now),
        "state_path": str(STATE_PATH),
    }
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    STATUS_PATH.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Consume Dream Caesar coordinator mail and emit canonical seat replies.")
    parser.add_argument("--interval-seconds", type=int, default=15)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    while True:
        record = run_once()
        print(json.dumps(record))
        if args.once:
            return 0
        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
