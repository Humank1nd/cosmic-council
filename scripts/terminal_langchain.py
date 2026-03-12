import argparse
import json
import shutil
import subprocess
import sys
import time
from argparse import Namespace
from datetime import datetime
from pathlib import Path
from typing import Any

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
SRC_ROOT = REPO_ROOT / "src"
CRONUS_ROOT = REPO_ROOT / "CRONUS"

for candidate in (SRC_ROOT, SCRIPT_ROOT):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

from langchain_core.runnables import RunnableLambda

from desktop_runtime import ACTIVE_CANON_PATH, HANDOFF_DIR, MAIL_ROOT, RUNTIME_ROOT, ensure_runtime_dirs
from cronus.app.council.canon_adapter import (
    outer_seats,
    resolve_seat_window,
    seat_guiding_question,
    seat_mission_pillar,
    seat_role,
    seat_title,
    window_selector_for_seat,
)
from cronus.app.tools.desktop import handle_list_windows, handle_send_handoff
from internal_mail import send_mail
from mail_routing import ACTIVE_CANON_THREAD, load_active_seats, resolve_allowed_recipient

STATUS_PATH = RUNTIME_ROOT / "terminal-langchain-status.json"
LOG_PATH = RUNTIME_ROOT / "terminal-langchain.jsonl"
ALIGNMENT_PATH = RUNTIME_ROOT / "canon-seat-alignment.json"
ACTIVE_TERMINAL_WORKER_STATUS_PATH = RUNTIME_ROOT / "active-canon-terminal-worker-status.json"
MAIL_LOG_PATH = MAIL_ROOT / "mail-log.jsonl"
OPENCLAW_CHANNEL = "telegram"
OPENCLAW_GROUP_TARGET = "-5102968528"

PATH_TARGETS = [
    str(SCRIPT_ROOT / "internal_mail.py"),
    str(SCRIPT_ROOT / "mail_routing.py"),
    str(SCRIPT_ROOT / "active_canon_terminal_worker.py"),
    str(SCRIPT_ROOT / "desktop_council_watchdog.py"),
    str(SCRIPT_ROOT / "desktop_handoff_runner.py"),
    str(SRC_ROOT / "cronus" / "app" / "tools" / "desktop.py"),
    str(CRONUS_ROOT / "api" / "main.py"),
    str(CRONUS_ROOT / "app" / "agents" / "runtime.py"),
    str(CRONUS_ROOT / "config" / "config.toml"),
    str(CRONUS_ROOT / "run_cronus.py"),
]


def _resolve_openclaw_command() -> list[str]:
    wsl = shutil.which("wsl")
    if wsl:
        return [wsl, "-d", "Ubuntu", "--", "openclaw"]
    resolved_cmd = shutil.which("openclaw.cmd")
    if resolved_cmd:
        return ["cmd", "/c", resolved_cmd]
    resolved_exe = shutil.which("openclaw")
    if resolved_exe:
        return [resolved_exe]
    return ["openclaw"]


def _active_seats() -> list[str]:
    return load_active_seats() or ["blue", "purple"]


def _slug(stamp: str) -> str:
    return f"{stamp}-dc-active-queue-mail-reassert.md"


def _seat_summary(seat: str) -> str:
    return f"{seat}: {seat_title(seat)} | {seat_role(seat)} | {seat_guiding_question(seat)}"


def _seat_alignment(active_seats: list[str]) -> dict[str, Any]:
    active = set(active_seats)
    seats: list[dict[str, Any]] = []
    for seat in outer_seats():
        seats.append(
            {
                "seat": seat,
                "title": seat_title(seat),
                "role": seat_role(seat),
                "mission_pillar": seat_mission_pillar(seat),
                "guiding_question": seat_guiding_question(seat),
                "status": "active" if seat in active else "parked",
            }
        )
    return {
        "generated_at": datetime.now().astimezone().isoformat(),
        "active_seats": active_seats,
        "parked_seats": [seat for seat in outer_seats() if seat not in active],
        "seats": seats,
    }


def _note_content(note_path: Path, active_seats: list[str], submit_mode: str, alignment_path: Path) -> str:
    path_lines = "\n".join(f"- {path}" for path in PATH_TARGETS)
    active_line = " -> ".join(active_seats)
    role_lines = "\n".join(f"- {_seat_summary(seat)}" for seat in active_seats)
    return (
        "# Handoff DC-ACTIVE-QUEUE\n\n"
        f"{PATH_TARGETS[0]}\n\n"
        "ISSUE: The active queue needs fresh next-seat-only internal mail between the live seats.\n"
        f"EXACT PATH: {PATH_TARGETS[0]}\n"
        "FIX: Check your mail now. Send one next-seat-only active-canon mail with exact Dream Caesar paths first. If blocked, delegate unblock work to the next seat. Keep the queue moving.\n\n"
        f"THREAD: {ACTIVE_CANON_THREAD}\n"
        f"ACTIVE: {', '.join(active_seats)}\n"
        f"RING: {active_line}\n"
        f"SUBMIT: {submit_mode}\n"
        f"NOTE_PATH: {note_path}\n\n"
        "## Active Seat Alignment\n\n"
        f"{role_lines}\n\n"
        "## Alignment Artifact\n\n"
        f"- {alignment_path}\n\n"
        "## Paths\n\n"
        f"{path_lines}\n"
    )


def _build_state(args: argparse.Namespace) -> dict[str, Any]:
    timestamp = datetime.now().astimezone()
    stamp = timestamp.strftime("%Y%m%d-%H%M%S")
    active_seats = _active_seats()
    note_path = HANDOFF_DIR / _slug(stamp)
    return {
        "timestamp": timestamp.isoformat(),
        "timestamp_epoch": timestamp.timestamp(),
        "stamp": stamp,
        "active_seats": active_seats,
        "submit_mode": args.submit_mode,
        "delivery_mode": args.delivery_mode,
        "interval_seconds": args.interval_seconds,
        "note_path": str(note_path),
    }


def _render_note(state: dict[str, Any]) -> dict[str, Any]:
    note_path = Path(state["note_path"])
    state["alignment_path"] = str(ALIGNMENT_PATH)
    state["alignment"] = _seat_alignment(state["active_seats"])
    state["note_content"] = _note_content(
        note_path,
        state["active_seats"],
        state["submit_mode"],
        ALIGNMENT_PATH,
    )
    return state


def _write_alignment(state: dict[str, Any]) -> dict[str, Any]:
    ALIGNMENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ALIGNMENT_PATH.write_text(json.dumps(state["alignment"], indent=2), encoding="utf-8")
    return state


def _write_note(state: dict[str, Any]) -> dict[str, Any]:
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    Path(state["note_path"]).write_text(state["note_content"], encoding="utf-8")
    return state


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _latest_mail_record() -> dict[str, Any] | None:
    if not MAIL_LOG_PATH.exists():
        return None
    latest: dict[str, Any] | None = None
    with MAIL_LOG_PATH.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                latest = json.loads(line)
            except json.JSONDecodeError:
                continue
    return latest


def _terminal_work_is_flowing(state: dict[str, Any]) -> dict[str, Any]:
    worker_status = _read_json(ACTIVE_TERMINAL_WORKER_STATUS_PATH) or {}
    latest_record = _latest_mail_record() or {}
    latest_subject = str(latest_record.get("subject") or "")
    latest_thread = str(latest_record.get("thread") or "")
    latest_timestamp = str(latest_record.get("timestamp") or "")

    latest_age_seconds: int | None = None
    if latest_timestamp:
        try:
            latest_age_seconds = max(
                0,
                int(
                    state["timestamp_epoch"]
                    - datetime.fromisoformat(latest_timestamp).timestamp()
                ),
            )
        except ValueError:
            latest_age_seconds = None

    recent_terminal_mail = (
        latest_thread == ACTIVE_CANON_THREAD
        and latest_subject.startswith("active-canon-terminal-work-")
        and latest_age_seconds is not None
        and latest_age_seconds <= max(state["interval_seconds"] * 3, 240)
    )

    worker_has_history = bool(worker_status.get("processed_count")) or bool(worker_status.get("processed"))
    worker_running = bool(worker_status.get("running"))
    recent_worker_run = False
    worker_timestamp = worker_status.get("timestamp")
    if worker_timestamp:
        try:
            worker_age_seconds = max(
                0,
                int(
                    state["timestamp_epoch"]
                    - datetime.fromisoformat(str(worker_timestamp)).timestamp()
                ),
            )
            recent_worker_run = worker_age_seconds <= max(state["interval_seconds"] * 4, 300)
        except ValueError:
            recent_worker_run = False

    state["active_terminal_worker_status_path"] = str(ACTIVE_TERMINAL_WORKER_STATUS_PATH)
    state["seed_suppressed"] = worker_running or worker_has_history or (recent_terminal_mail and recent_worker_run)
    state["seed_suppression_reason"] = (
        "active terminal worker owns the live active-canon loop"
        if state["seed_suppressed"]
        else None
    )
    return state


def _dispatch_openclaw(note_path: str) -> dict[str, Any]:
    command = _resolve_openclaw_command()
    result = subprocess.run(
        [
            *command,
            "message",
            "send",
            "--channel",
            OPENCLAW_CHANNEL,
            "--target",
            OPENCLAW_GROUP_TARGET,
            "--message",
            note_path,
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    parsed = None
    stdout = result.stdout.strip()
    if stdout:
        try:
            parsed = json.loads(stdout)
        except json.JSONDecodeError:
            parsed = None
    return {
        "transport": "openclaw",
        "command": command,
        "channel": OPENCLAW_CHANNEL,
        "target": OPENCLAW_GROUP_TARGET,
        "returncode": result.returncode,
        "stdout": stdout,
        "stderr": result.stderr.strip(),
        "response": parsed,
        "success": result.returncode == 0,
    }


def _mail_body(note_path: str, sender: str, recipient: str, alignment_path: str) -> str:
    return (
        f"{note_path}\n\n"
        f"SENDER ROLE: {seat_title(sender)} | {seat_role(sender)}\n"
        f"SENDER QUESTION: {seat_guiding_question(sender)}\n"
        f"RECIPIENT ROLE: {seat_title(recipient)} | {seat_role(recipient)}\n"
        f"RECIPIENT QUESTION: {seat_guiding_question(recipient)}\n"
        f"ALIGNMENT ARTIFACT: {alignment_path}\n\n"
        "Check your mail now. Reassert the active queue with next-seat-only internal mail. "
        "Keep scope on Dream Caesar runtime paths only and stay inside your canon role. "
        "If blocked, delegate unblock work to the next seat."
    )


def _dispatch_internal_mail(state: dict[str, Any]) -> list[dict[str, Any]]:
    deliveries = []
    for seat in state["active_seats"]:
        recipient = resolve_allowed_recipient(
            seat,
            thread=ACTIVE_CANON_THREAD,
            active_seats=state["active_seats"],
        )
        if recipient is None:
            deliveries.append(
                {
                    "transport": "internal_mail",
                    "sender": seat,
                    "recipient": None,
                    "success": False,
                    "error": "no_allowed_recipient",
                }
            )
            continue
        subject = f"next-seat-live-terminal-relay-exact-paths-keepalive-{seat}"
        args = Namespace(
            sender=seat,
            to=recipient,
            subject=subject,
            body=_mail_body(state["note_path"], seat, recipient, state["alignment_path"]),
            thread=ACTIVE_CANON_THREAD,
            priority="high",
            attachments=[state["note_path"], state["alignment_path"], *PATH_TARGETS],
        )
        try:
            send_mail(args)
            mailbox = MAIL_ROOT / recipient
            latest = max(mailbox.glob("*.md"), key=lambda path: path.stat().st_mtime, default=None)
            deliveries.append(
                {
                    "transport": "internal_mail",
                    "sender": seat,
                    "recipient": recipient,
                    "thread": ACTIVE_CANON_THREAD,
                    "success": True,
                    "mail_path": str(latest) if latest else None,
                }
            )
        except SystemExit as exc:
            deliveries.append(
                {
                    "transport": "internal_mail",
                    "sender": seat,
                    "recipient": recipient,
                    "thread": ACTIVE_CANON_THREAD,
                    "success": False,
                    "error": str(exc),
                }
            )
    return deliveries


def _dispatch_desktop(state: dict[str, Any]) -> list[dict[str, Any]]:
    windows = handle_list_windows({}).get("windows", [])
    deliveries = []
    for seat in state["active_seats"]:
        resolved = resolve_seat_window(windows, seat)
        selector = window_selector_for_seat(seat, resolved)
        typed = handle_send_handoff(
            {
                **selector,
                "message": state["note_path"],
                "submit": True,
                "submit_mode": state["submit_mode"],
                "confirm": True,
                "text_entry_method": "paste",
            }
        )
        deliveries.append(
            {
                "seat": seat,
                "resolved_title": resolved.get("title"),
                "dispatch": typed,
                "transport": "desktop",
            }
        )
    return deliveries


def _dispatch(state: dict[str, Any]) -> dict[str, Any]:
    deliveries = []
    if state.get("seed_suppressed"):
        deliveries.append(
            {
                "transport": "internal_mail",
                "success": True,
                "skipped": True,
                "reason": state.get("seed_suppression_reason"),
            }
        )
    elif state["delivery_mode"] == "internal-mail":
        deliveries.extend(_dispatch_internal_mail(state))
    else:
        primary = _dispatch_openclaw(state["note_path"])
        deliveries.append(primary)
    if state["delivery_mode"] == "desktop":
        deliveries.extend(_dispatch_desktop(state))
    elif state["delivery_mode"] == "openclaw-fallback-desktop" and not deliveries[0].get("success"):
        deliveries.extend(_dispatch_desktop(state))
    state["deliveries"] = deliveries
    return state


def _record(state: dict[str, Any]) -> dict[str, Any]:
    ensure_runtime_dirs()
    record = {
        "timestamp": state["timestamp"],
        "note_path": state["note_path"],
        "active_seats": state["active_seats"],
        "submit_mode": state["submit_mode"],
        "delivery_mode": state["delivery_mode"],
        "active_canon_path": str(ACTIVE_CANON_PATH),
        "alignment_path": state["alignment_path"],
        "active_terminal_worker_status_path": state.get("active_terminal_worker_status_path"),
        "seed_suppressed": state.get("seed_suppressed", False),
        "seed_suppression_reason": state.get("seed_suppression_reason"),
        "deliveries": state["deliveries"],
    }
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    STATUS_PATH.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


CHAIN = (
    RunnableLambda(_build_state)
    | RunnableLambda(_render_note)
    | RunnableLambda(_write_alignment)
    | RunnableLambda(_write_note)
    | RunnableLambda(_terminal_work_is_flowing)
    | RunnableLambda(_dispatch)
    | RunnableLambda(_record)
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a Dream Caesar terminal LangChain relay loop.")
    parser.add_argument("--interval-seconds", type=int, default=90)
    parser.add_argument("--submit-mode", choices=["enter", "ctrl-enter", "both"], default="enter")
    parser.add_argument(
        "--delivery-mode",
        choices=["internal-mail", "openclaw", "openclaw-fallback-desktop", "desktop"],
        default="internal-mail",
    )
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    while True:
        record = CHAIN.invoke(args)
        print(json.dumps(record))
        if args.once:
            return 0
        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
