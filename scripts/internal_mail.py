import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from mail_routing import (
    ACTIVE_CANON_PATH,
    ACTIVE_CANON_THREAD,
    CANONICAL_SEATS,
    COORDINATOR_SEAT,
    COORDINATOR_THREAD,
    load_active_seats,
    normalize_thread,
    resolve_allowed_recipient,
)
from desktop_runtime import MAIL_ROOT, ensure_runtime_dirs


LOG_PATH = MAIL_ROOT / "mail-log.jsonl"


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def ensure_mailbox(seat: str) -> Path:
    ensure_runtime_dirs()
    mailbox = MAIL_ROOT / seat.lower()
    mailbox.mkdir(parents=True, exist_ok=True)
    return mailbox


def write_log(record: dict) -> None:
    ensure_runtime_dirs()
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def validate_route(sender: str, recipient: str, thread: str | None) -> None:
    normalized_sender = sender.lower()
    normalized_recipient = recipient.lower()
    thread_name = normalize_thread(thread)

    if thread_name == COORDINATOR_THREAD:
        if normalized_sender == COORDINATOR_SEAT and normalized_recipient in CANONICAL_SEATS:
            return
        if normalized_sender in CANONICAL_SEATS and normalized_recipient == COORDINATOR_SEAT:
            return
        raise SystemExit(
            f"Coordinator mail blocked: {normalized_sender} may only communicate between Dream Caesar and canonical seats on {COORDINATOR_THREAD}."
        )

    if thread_name == ACTIVE_CANON_THREAD:
        active_seats = load_active_seats()
        if not active_seats:
            raise SystemExit(
                f"Active-canon mail blocked: unable to load active seats from {ACTIVE_CANON_PATH}."
            )
        if normalized_sender not in active_seats:
            raise SystemExit(
                f"Out-of-scope active-canon mail blocked: {normalized_sender} is not in active seats {active_seats}."
            )
        expected_recipient = resolve_allowed_recipient(
            normalized_sender,
            thread=thread_name,
            active_seats=active_seats,
        )
        if expected_recipient is None or normalized_recipient != expected_recipient:
            raise SystemExit(
                f"Out-of-sequence active-canon mail blocked: {normalized_sender} may only message {expected_recipient}, not {normalized_recipient}."
            )
        return

    expected_recipient = resolve_allowed_recipient(normalized_sender, thread=thread_name)
    if expected_recipient and normalized_recipient != expected_recipient:
        raise SystemExit(
            f"Out-of-sequence mail blocked: {normalized_sender} may only message {expected_recipient}, not {normalized_recipient}."
        )


def send_mail(args: argparse.Namespace) -> int:
    thread_name = normalize_thread(args.thread)
    validate_route(args.sender, args.to, thread_name)
    mailbox = ensure_mailbox(args.to)
    timestamp = datetime.now().astimezone()
    stamp = timestamp.strftime("%Y%m%d-%H%M%S")
    subject_slug = slugify(args.subject) or "message"
    mail_path = mailbox / f"{stamp}-{subject_slug}.md"

    attachments = args.attachments or []
    attachment_lines = "\n".join(f"- {path}" for path in attachments) or "- none"
    body = (
        f"# Mail {args.subject}\n\n"
        f"FROM: {args.sender}\n"
        f"TO: {args.to}\n"
        f"THREAD: {thread_name or 'none'}\n"
        f"PRIORITY: {args.priority}\n"
        f"TIMESTAMP: {timestamp.isoformat()}\n\n"
        f"## Body\n\n"
        f"{args.body}\n\n"
        f"## Attachments\n\n"
        f"{attachment_lines}\n"
    )
    mail_path.write_text(body, encoding="utf-8")

    write_log(
        {
            "timestamp": timestamp.isoformat(),
            "from": args.sender,
            "to": args.to,
            "subject": args.subject,
            "thread": thread_name or None,
            "priority": args.priority,
            "path": str(mail_path),
            "attachments": attachments,
        }
    )
    print(str(mail_path))
    return 0


def list_mail(args: argparse.Namespace) -> int:
    mailbox = ensure_mailbox(args.seat)
    messages = sorted(mailbox.glob("*.md"), key=lambda path: path.stat().st_mtime, reverse=True)
    for path in messages[: args.limit]:
        print(str(path))
    return 0


def latest_mail(args: argparse.Namespace) -> int:
    mailbox = ensure_mailbox(args.seat)
    latest = max(mailbox.glob("*.md"), key=lambda path: path.stat().st_mtime, default=None)
    if latest is None:
        return 1
    print(str(latest))
    return 0


def next_seat(args: argparse.Namespace) -> int:
    thread_name = normalize_thread(getattr(args, "thread", None))
    active_seats = load_active_seats() if thread_name == ACTIVE_CANON_THREAD else None
    if thread_name == ACTIVE_CANON_THREAD and not active_seats:
        raise SystemExit(
            f"Active-canon next seat unavailable: unable to load active seats from {ACTIVE_CANON_PATH}."
        )
    recipient = resolve_allowed_recipient(args.seat, thread=thread_name, active_seats=active_seats)
    if recipient is None:
        return 1
    print(recipient)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Local internal maildrop for Dream Caesar desktop seats.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    send_parser = subparsers.add_parser("send")
    send_parser.add_argument("--from", dest="sender", required=True)
    send_parser.add_argument("--to", required=True)
    send_parser.add_argument("--subject", required=True)
    send_parser.add_argument("--body", required=True)
    send_parser.add_argument("--thread")
    send_parser.add_argument("--priority", default="normal")
    send_parser.add_argument("--attachments", nargs="*")
    send_parser.set_defaults(func=send_mail)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--seat", required=True)
    list_parser.add_argument("--limit", type=int, default=10)
    list_parser.set_defaults(func=list_mail)

    latest_parser = subparsers.add_parser("latest")
    latest_parser.add_argument("--seat", required=True)
    latest_parser.set_defaults(func=latest_mail)

    next_parser = subparsers.add_parser("next")
    next_parser.add_argument("--seat", required=True)
    next_parser.add_argument("--thread")
    next_parser.set_defaults(func=next_seat)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
