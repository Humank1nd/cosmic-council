import argparse
import asyncio
import json
import os
import re
import sys
import time
import tomllib
from argparse import Namespace
from datetime import datetime
from pathlib import Path
from typing import Any

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
SRC_ROOT = REPO_ROOT / "src"
CRONUS_ROOT = REPO_ROOT / "CRONUS"

for candidate in (CRONUS_ROOT, SCRIPT_ROOT, SRC_ROOT):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

from app.agents.runtime import run_task
from cronus.app.council.canon_adapter import seat_role, seat_title
from desktop_runtime import ACTIVE_CANON_PATH, HANDOFF_DIR, MAIL_ROOT, RUNTIME_ROOT, ensure_runtime_dirs
from internal_mail import send_mail
from mail_routing import ACTIVE_CANON_THREAD, load_active_seats, resolve_allowed_recipient


STATUS_PATH = RUNTIME_ROOT / "active-canon-terminal-worker-status.json"
STATE_PATH = RUNTIME_ROOT / "active-canon-terminal-worker-state.json"
LOG_PATH = RUNTIME_ROOT / "active-canon-terminal-worker.jsonl"
CRONUS_CONFIG_PATH = CRONUS_ROOT / "config" / "config.toml"


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _load_state() -> dict[str, Any]:
    return _load_json(STATE_PATH, {"processed_paths": []})


def _save_state(state: dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _write_status(record: dict[str, Any]) -> None:
    STATUS_PATH.write_text(json.dumps(record, indent=2), encoding="utf-8")


def _load_active_canon() -> dict[str, Any]:
    return _load_json(ACTIVE_CANON_PATH, {})


def _load_cronus_config() -> dict[str, Any]:
    if not CRONUS_CONFIG_PATH.exists():
        return {}
    return tomllib.loads(CRONUS_CONFIG_PATH.read_text(encoding="utf-8"))


def _truncate_text(text: str, max_chars: int) -> str:
    compact = text.strip()
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3].rstrip() + "..."


def _read_mail(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    subject = ""
    sender = ""
    recipient = ""
    thread = ""
    body_lines: list[str] = []
    attachments: list[str] = []
    in_body = False
    in_attachments = False
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
            in_attachments = False
            continue
        elif line == "## Attachments":
            in_body = False
            in_attachments = True
            continue
        elif in_body:
            body_lines.append(line)
        elif in_attachments and line.strip().startswith("- "):
            attachments.append(line.strip()[2:].strip())
    return {
        "path": str(path),
        "subject": subject,
        "from": sender,
        "to": recipient,
        "thread": thread,
        "body": "\n".join(body_lines).strip(),
        "attachments": attachments,
    }


def _latest_active_mail_for_seat(seat: str, processed_paths: set[str]) -> dict[str, Any] | None:
    mailbox = MAIL_ROOT / seat
    if not mailbox.exists():
        return None
    candidates = sorted(mailbox.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True)
    for path in candidates:
        if str(path) in processed_paths:
            continue
        parsed = _read_mail(path)
        if parsed["thread"] != ACTIVE_CANON_THREAD:
            continue
        if parsed["to"] != seat:
            continue
        return parsed
    return None


def _extract_note_path(source_mail: dict[str, Any]) -> str | None:
    body = source_mail.get("body", "")
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.lower().endswith(".md") and (":\\" in stripped or stripped.startswith("D:/")):
            return stripped
    attachments = source_mail.get("attachments") or []
    for attachment in attachments:
        if attachment.lower().endswith(".md"):
            return attachment
    return None


def _note_excerpt(note_path: str | None, max_chars: int = 2000) -> str:
    if not note_path:
        return "NO_NOTE_PATH"
    candidate = Path(note_path)
    if not candidate.exists():
        return note_path
    try:
        return _truncate_text(candidate.read_text(encoding="utf-8", errors="ignore"), max_chars)
    except OSError:
        return note_path


def _build_task_prompt(seat: str, source_mail: dict[str, Any], active_canon: dict[str, Any]) -> tuple[str, str]:
    note_path = _extract_note_path(source_mail)
    required_path_lines = "\n".join(f"- {path}" for path in active_canon.get("required_paths", [])[:10]) or "- none"
    note_line = note_path or "NO_NOTE_PATH"
    task = (
        f"You are {seat_title(seat)}. Continue the Dream Caesar active-canon task in your terminal role.\n"
        f"Use read_file on NOTE_PATH first: {note_line}\n"
        "Then inspect only the exact Dream Caesar or CRONUS paths you need.\n"
        "Produce a concise handoff for the next seat.\n"
        "Do not impersonate Dream Caesar. Do not route outside the canon ring.\n"
        "Output sections named exactly: SUMMARY, EXACT_PATHS, NEXT_HANDOFF."
    )
    context = (
        f"ACTIVE OBJECTIVE:\n{active_canon.get('objective')}\n\n"
        f"SEAT ROLE:\n{seat_role(seat)}\n\n"
        f"SOURCE MAIL PATH:\n{source_mail['path']}\n\n"
        f"SOURCE MAIL FROM:\n{source_mail['from']}\n\n"
        f"SOURCE NOTE PATH:\n{note_line}\n\n"
        "REQUIRED RUNTIME PATHS:\n"
        f"{required_path_lines}\n"
    )
    return task, context


def _build_fallback_task_prompt(seat: str, source_mail: dict[str, Any], active_canon: dict[str, Any]) -> tuple[str, str]:
    note_path = _extract_note_path(source_mail) or "NO_NOTE_PATH"
    task = (
        f"You are {seat_title(seat)}. Read NOTE_PATH and continue the Dream Caesar active-canon task.\n"
        f"NOTE_PATH: {note_path}\n"
        "Return only SUMMARY, EXACT_PATHS, NEXT_HANDOFF."
    )
    context = (
        f"OBJECTIVE: {active_canon.get('objective')}\n"
        f"SOURCE_MAIL: {source_mail['path']}\n"
        f"ROLE: {seat_role(seat)}\n"
    )
    return task, context


def _summarize_result_text(text: str) -> str:
    compact = " ".join(line.strip() for line in text.splitlines() if line.strip())
    return _truncate_text(compact, 500)


def _write_handoff(
    seat: str,
    recipient: str,
    source_mail: dict[str, Any],
    result_text: str,
    active_canon: dict[str, Any],
) -> str:
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    path = HANDOFF_DIR / f"{stamp}-dc-{seat}-terminal-work-to-{recipient}.md"
    note_path = _extract_note_path(source_mail) or "NO_NOTE_PATH"
    path.write_text(
        (
            "# Handoff DC-ACTIVE-CANON-WORK\n\n"
            f"FROM: {seat}\n"
            f"TO: {recipient}\n"
            f"THREAD: {ACTIVE_CANON_THREAD}\n"
            f"SOURCE_MAIL: {source_mail['path']}\n"
            f"NOTE_PATH: {note_path}\n\n"
            f"{note_path}\n\n"
            f"OBJECTIVE: {active_canon.get('objective')}\n"
            f"ROLE: {seat_role(seat)}\n\n"
            "## Work Output\n\n"
            f"{result_text.strip()}\n"
        ),
        encoding="utf-8",
    )
    return str(path)


def _send_next_mail(
    seat: str,
    recipient: str,
    source_mail: dict[str, Any],
    handoff_path: str,
    result_text: str,
) -> str:
    summary = _summarize_result_text(result_text)
    args = Namespace(
        sender=seat,
        to=recipient,
        subject=f"active-canon-terminal-work-{seat}",
        body=(
            f"{handoff_path}\n\n"
            f"SOURCE_MAIL: {source_mail['path']}\n"
            f"SOURCE_SUBJECT: {source_mail['subject']}\n\n"
            "TERMINAL WORK SUMMARY:\n"
            f"{summary}\n\n"
            "Check this handoff and continue the canon ring in terminal."
        ),
        thread=ACTIVE_CANON_THREAD,
        priority="high",
        attachments=[handoff_path, source_mail["path"]],
    )
    send_mail(args)
    mailbox = MAIL_ROOT / recipient
    latest = max(mailbox.glob("*.md"), key=lambda item: item.stat().st_mtime, default=None)
    return str(latest) if latest else ""


async def _execute_seat_task(seat: str, source_mail: dict[str, Any], active_canon: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    task, context = _build_task_prompt(seat, source_mail, active_canon)
    try:
        return await run_task(task=task, totem=seat, context=context, config=config, use_tools=False)
    except Exception as exc:
        if "Context size has been exceeded" not in str(exc):
            raise
    fallback_task, fallback_context = _build_fallback_task_prompt(seat, source_mail, active_canon)
    result = await run_task(task=fallback_task, totem=seat, context=fallback_context, config=config, use_tools=False)
    result["fallback_used"] = True
    return result


def run_once() -> dict[str, Any]:
    ensure_runtime_dirs()
    state = _load_state()
    processed_paths = set(state.get("processed_paths", []))
    config = _load_cronus_config()
    active_canon = _load_active_canon()
    active_seats = load_active_seats() or []
    records: list[dict[str, Any]] = []
    _write_status(
        {
            "timestamp": datetime.now().astimezone().isoformat(),
            "active_seats": active_seats,
            "processed": records,
            "processed_count": 0,
            "state_path": str(STATE_PATH),
            "running": True,
        }
    )

    for seat in active_seats:
        source_mail = _latest_active_mail_for_seat(seat, processed_paths)
        if source_mail is None:
            continue
        recipient = resolve_allowed_recipient(seat, thread=ACTIVE_CANON_THREAD, active_seats=active_seats)
        if recipient is None:
            continue

        result = asyncio.run(_execute_seat_task(seat, source_mail, active_canon, config))
        result_text = str(result.get("result") or "").strip()
        handoff_path = _write_handoff(seat, recipient, source_mail, result_text, active_canon)
        forwarded_mail_path = _send_next_mail(seat, recipient, source_mail, handoff_path, result_text)

        processed_paths.add(source_mail["path"])
        records.append(
            {
                "seat": seat,
                "source_mail": source_mail["path"],
                "recipient": recipient,
                "handoff_path": handoff_path,
                "forwarded_mail_path": forwarded_mail_path,
                "provider": result.get("provider"),
                "model": result.get("model"),
                "steps": result.get("steps"),
                "error": result.get("error"),
                "elapsed_ms": result.get("elapsed_ms"),
            }
        )
        _write_status(
            {
                "timestamp": datetime.now().astimezone().isoformat(),
                "active_seats": active_seats,
                "processed": records,
                "processed_count": len(records),
                "state_path": str(STATE_PATH),
                "running": True,
            }
        )

    new_state = {"processed_paths": sorted(processed_paths)}
    _save_state(new_state)
    record = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "active_seats": active_seats,
        "processed": records,
        "processed_count": len(records),
        "state_path": str(STATE_PATH),
        "running": False,
    }
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    _write_status(record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Consume active-canon seat mail and run CRONUS terminal work per seat.")
    parser.add_argument("--interval-seconds", type=int, default=120)
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
