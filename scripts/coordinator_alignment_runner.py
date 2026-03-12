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

for candidate in (SRC_ROOT, SCRIPT_ROOT):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

from cronus.app.council.canon_adapter import next_outer_seat, seat_title
from desktop_runtime import ACTIVE_CANON_PATH, RUNTIME_ROOT, ensure_runtime_dirs
from internal_mail import send_mail
from mail_routing import COORDINATOR_SEAT, COORDINATOR_THREAD, load_active_seats
from seat_mailbox_consumer import run_once as consume_coordinator_mail


AUDIT_JSON_PATH = RUNTIME_ROOT / "coordinator-alignment-audit.json"
AUDIT_MD_PATH = RUNTIME_ROOT / "coordinator-alignment-audit.md"
MAIL_ROOT = RUNTIME_ROOT / "mail"
ALIGNMENT_PATH = RUNTIME_ROOT / "canon-seat-alignment.json"
WATCHDOG_PATH = RUNTIME_ROOT / "artifacts" / "desktop-council-watchdog-status.json"
CANON_PATH = SRC_ROOT / "cosmic_council" / "canon" / "cosmic_canon.py"
ADAPTER_PATH = SRC_ROOT / "cronus" / "app" / "council" / "canon_adapter.py"


SEAT_INTERVIEW_PROMPTS = {
    "red": "Include: 1. your purpose in the ROYGBV cycle, 2. two deep responsibility areas, 3. two expanded guiding questions, 4. one example in action, 5. how your output should shape Orange Orangutan next in the current runtime, 6. what runtime fact shows you are grounded in root-truth instead of symptoms.",
    "orange": "Include: 1. your purpose in the ROYGBV cycle, 2. two deep responsibility areas, 3. two expanded guiding questions, 4. one example in action, 5. how Red Owl input should shape your plan right now, 6. how your output should shape Yellow Honeybee next in the current runtime, 7. what runtime fact shows your plan is grounded instead of speculative.",
    "yellow": "Include: 1. your purpose in the ROYGBV cycle, 2. two deep responsibility areas, 3. two expanded guiding questions, 4. one example in action, 5. how Orange Orangutan input should shape your build right now, 6. how your output should shape Green Tortoise next in the current runtime, 7. what runtime fact shows your work is grounded instead of premature.",
    "green": "Include: 1. your purpose in the ROYGBV cycle, 2. two deep responsibility areas, 3. two expanded guiding questions, 4. one example in action, 5. how Yellow Honeybee output should shape your stewardship right now, 6. how your output should shape Blue Dolphin next in the current runtime, 7. what runtime fact shows your stewardship is grounded instead of wasteful.",
    "blue": "Include: 1. your purpose in the ROYGBV cycle, 2. two deep responsibility areas, 3. two expanded guiding questions, 4. one example in action, 5. how Green Tortoise output should shape your messaging right now, 6. how your output should shape Purple Elephant next in the current runtime, 7. what runtime fact shows your communication is grounded instead of empty.",
    "purple": "Include: 1. your purpose in the ROYGBV cycle, 2. two deep responsibility areas, 3. two expanded guiding questions, 4. one example in action, 5. how Blue Dolphin output should shape your reflection right now, 6. how your output should shape Red Owl next in the current runtime, 7. what runtime fact shows your reflection is grounded instead of detached.",
}


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _send_interview(seat: str, stamp: str) -> str:
    subject = f"alignment-audit-{seat}-{stamp}"
    body = (
        f"Dream Caesar coordinator alignment audit for {seat_title(seat)}. "
        "Answer from canon plus current runtime state. "
        f"{SEAT_INTERVIEW_PROMPTS[seat]} "
        "Keep scope on Dream Caesar runtime and exact repo paths only."
    )
    args = Namespace(
        sender=COORDINATOR_SEAT,
        to=seat,
        subject=subject,
        body=body,
        thread=COORDINATOR_THREAD,
        priority="high",
        attachments=[
            str(ALIGNMENT_PATH),
            str(CANON_PATH),
            str(ADAPTER_PATH),
            str(WATCHDOG_PATH),
        ],
    )
    send_mail(args)
    mailbox = MAIL_ROOT / seat
    latest = max(mailbox.glob("*.md"), key=lambda item: item.stat().st_mtime, default=None)
    return str(latest) if latest else ""


def _extract_field(text: str, key: str) -> str | None:
    needle = f"{key}: "
    for line in text.splitlines():
        if line.startswith(needle):
            return line[len(needle) :].strip()
    return None


def _extract_next_shape(text: str) -> tuple[str | None, str | None]:
    match = re.search(r"^For\s+([A-Za-z-]+)\s+next:\s*(.+)$", text, flags=re.MULTILINE)
    if not match:
        return None, None
    return match.group(1).strip().lower(), match.group(2).strip()


def _extract_exact_paths(text: str) -> list[str]:
    match = re.search(r"## Exact Paths\s+(.+?)(?:\n## |\Z)", text, flags=re.DOTALL)
    if not match:
        return []
    paths: list[str] = []
    for line in match.group(1).splitlines():
        line = line.strip()
        if line.startswith("- "):
            paths.append(line[2:].strip())
    return paths


def _latest_reply_for_subject_fragment(fragment: str) -> Path | None:
    mailbox = MAIL_ROOT / COORDINATOR_SEAT
    candidates = sorted(mailbox.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True)
    for path in candidates:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if fragment in text:
            return path
    return None


def _summarize_reply(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    seat = _extract_field(text, "SEAT")
    next_shape_target, next_shape_text = _extract_next_shape(text)
    expected_next = next_outer_seat(seat) if seat else None
    return {
        "path": str(path),
        "seat": seat,
        "role": _extract_field(text, "ROLE"),
        "purpose": _extract_field(text, "PURPOSE"),
        "guiding_question": _extract_field(text, "GUIDING_QUESTION"),
        "current_responsibility": _extract_field(text, "CURRENT_RESPONSIBILITY"),
        "queue_state": _extract_field(text, "QUEUE_STATE"),
        "latest_handoff": _extract_field(text, "LATEST_HANDOFF"),
        "next_shape_target": next_shape_target,
        "next_shape": next_shape_text,
        "expected_next_seat": expected_next,
        "next_shape_aligned": bool(next_shape_target and expected_next and next_shape_target == expected_next),
        "exact_paths": _extract_exact_paths(text),
        "body": text,
    }


def _write_markdown(record: dict) -> None:
    findings = record.get("findings") or ["none"]
    lines = [
        "# Dream Caesar Coordinator Alignment Audit",
        "",
        f"Timestamp: {record['timestamp']}",
        f"Active seats: {', '.join(record['active_seats'])}",
        f"Aligned seats: {record.get('aligned_seat_count', 0)} / {len(record.get('active_seats', []))}",
        f"All next-seat shaping aligned: {record.get('all_next_shape_aligned')}",
        "",
        "## Findings",
        "",
        *[f"- {finding}" for finding in findings],
        "",
    ]
    for seat_record in record["seats"]:
        lines.extend(
            [
                f"## {seat_record['seat']}",
                "",
                f"- reply_path: {seat_record['reply_path']}",
                f"- role: {seat_record.get('role')}",
                f"- purpose: {seat_record.get('purpose')}",
                f"- guiding_question: {seat_record.get('guiding_question')}",
                f"- current_responsibility: {seat_record.get('current_responsibility')}",
                f"- queue_state: {seat_record.get('queue_state')}",
                f"- latest_handoff: {seat_record.get('latest_handoff')}",
                f"- expected_next_seat: {seat_record.get('expected_next_seat')}",
                f"- next_shape_target: {seat_record.get('next_shape_target')}",
                f"- next_shape_aligned: {seat_record.get('next_shape_aligned')}",
                f"- next_shape: {seat_record.get('next_shape')}",
                f"- exact_paths: {', '.join(seat_record.get('exact_paths') or [])}",
                "",
            ]
        )
    AUDIT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def run_once() -> dict:
    ensure_runtime_dirs()
    active_seats = load_active_seats() or []
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    sent: list[dict] = []
    for seat in active_seats:
        sent.append({"seat": seat, "mail_path": _send_interview(seat, stamp)})

    processed = consume_coordinator_mail()
    time.sleep(1)

    replies: list[dict] = []
    for seat in active_seats:
        fragment = f"alignment-audit-{seat}-{stamp}"
        reply_path = _latest_reply_for_subject_fragment(fragment)
        seat_record = {"seat": seat, "sent_path": next(item["mail_path"] for item in sent if item["seat"] == seat), "reply_path": str(reply_path) if reply_path else None}
        if reply_path is not None:
            seat_record.update(_summarize_reply(reply_path))
        replies.append(seat_record)

    misaligned_seats = [
        seat_record["seat"]
        for seat_record in replies
        if seat_record.get("reply_path") and not seat_record.get("next_shape_aligned")
    ]
    missing_replies = [seat_record["seat"] for seat_record in replies if not seat_record.get("reply_path")]
    findings: list[str] = []
    if missing_replies:
        findings.append(f"Missing coordinator replies: {', '.join(missing_replies)}")
    if misaligned_seats:
        findings.append(f"Next-seat shaping misaligned for: {', '.join(misaligned_seats)}")
    if not findings:
        findings.append("All active seats replied on DC-COORDINATOR and matched their canonical next-seat shaping.")

    record = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "stamp": stamp,
        "active_seats": active_seats,
        "sent": sent,
        "consumer_processed_count": processed.get("processed_count"),
        "aligned_seat_count": sum(1 for seat_record in replies if seat_record.get("next_shape_aligned")),
        "all_next_shape_aligned": not misaligned_seats and not missing_replies,
        "misaligned_seats": misaligned_seats,
        "missing_replies": missing_replies,
        "findings": findings,
        "seats": replies,
        "active_canon_path": str(ACTIVE_CANON_PATH),
    }
    AUDIT_JSON_PATH.write_text(json.dumps(record, indent=2), encoding="utf-8")
    _write_markdown(record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Dream Caesar coordinator alignment interviews across all active seats.")
    parser.add_argument("--interval-seconds", type=int, default=300)
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
