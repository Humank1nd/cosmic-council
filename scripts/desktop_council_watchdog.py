import argparse
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

from mail_routing import ACTIVE_CANON_THREAD, CANONICAL_SEATS, normalize_thread, resolve_allowed_recipient
from desktop_runtime import ACTIVE_CANON_PATH, ARTIFACT_ROOT, HANDOFF_DIR, MAIL_ROOT, REPO_ROOT, ensure_runtime_dirs


OUTPUT_DIR = ARTIFACT_ROOT
RUNNER = REPO_ROOT / "scripts" / "desktop_handoff_runner.py"
OUTER_SEATS = CANONICAL_SEATS
MAIL_LOG_PATH = MAIL_ROOT / "mail-log.jsonl"


def read_handoff_text(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def handoff_metadata(path: Path | None, content: str | None = None) -> dict:
    if path is None:
        return {
            "task_id": None,
            "from_seat": None,
            "to_seat": None,
            "is_dream_caesar": False,
            "filename_seat": None,
        }

    text = content if content is not None else read_handoff_text(path)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    fields: dict[str, str] = {}
    task_id = None
    for line in lines[:4]:
        if line.lower().startswith("# handoff "):
            task_id = line[len("# Handoff ") :].strip()
            break
        if line.upper().startswith("TASK "):
            task_id = line.split(None, 2)[1].strip()
            break
    for line in lines[:12]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip().upper()] = value.strip()

    task_id = task_id or fields.get("TASK") or fields.get("# HANDOFF")
    from_seat = fields.get("FROM")
    to_seat = fields.get("TO")
    lowered_name = path.name.lower()
    lowered_text = text.lower()
    filename_seat = infer_seat_from_handoff(path)
    is_dream_caesar = (
        (task_id or "").upper().startswith("DC-")
        or "-dc-" in lowered_name
        or "dream caesar" in lowered_text
    )

    return {
        "task_id": task_id,
        "from_seat": from_seat.lower() if from_seat else None,
        "to_seat": to_seat.lower() if to_seat else None,
        "is_dream_caesar": is_dream_caesar,
        "filename_seat": filename_seat,
    }


def infer_seat_from_handoff(path: Path | None) -> str | None:
    if path is None:
        return None
    lowered = path.name.lower()
    for seat in OUTER_SEATS:
        if seat in lowered:
            return seat
    if "center" in lowered:
        return "center"
    return None


def candidate_handoffs() -> list[Path]:
    if not HANDOFF_DIR.exists():
        return []
    return [
        path
        for path in HANDOFF_DIR.glob("*")
        if path.is_file()
        and not path.name.upper().startswith("JB-MAIL-")
        and "hold" not in path.name.lower()
    ]


def latest_handoff(active_canon: dict | None = None) -> Path | None:
    candidates = candidate_handoffs()
    if not candidates:
        return None

    if active_canon:
        active = set(active_seats(active_canon))
        for path in sorted(candidates, key=lambda candidate: candidate.stat().st_mtime, reverse=True):
            metadata = handoff_metadata(path)
            participants = {
                participant
                for participant in (metadata.get("from_seat"), metadata.get("to_seat"))
                if participant
            }
            if "center" in participants or participants.intersection(active):
                return path
            if metadata.get("is_dream_caesar") and not participants:
                return path
            filename_seat = metadata.get("filename_seat")
            if filename_seat == "center" or filename_seat in active:
                return path

    return max(candidates, key=lambda path: path.stat().st_mtime, default=None)


def latest_active_handoff(active_canon: dict | None = None) -> Path | None:
    candidates = candidate_handoffs()
    if not candidates or not active_canon:
        return None

    active_list = active_seats(active_canon)
    active = set(active_list)
    for path in sorted(candidates, key=lambda candidate: candidate.stat().st_mtime, reverse=True):
        metadata = handoff_metadata(path)
        sender = metadata.get("from_seat")
        recipient = metadata.get("to_seat")
        if sender not in active or recipient not in active:
            continue
        expected_recipient = resolve_allowed_recipient(
            sender,
            thread=ACTIVE_CANON_THREAD,
            active_seats=active_list,
        )
        if expected_recipient == recipient:
            return path
    return None


def latest_mail_record(active_canon: dict | None = None) -> dict | None:
    if not MAIL_LOG_PATH.exists():
        return None
    active_list = active_seats(active_canon) if active_canon else []
    active = set(active_list)
    records: list[dict] = []
    with MAIL_LOG_PATH.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if active:
                sender = str(record.get("from", "")).lower()
                recipient = str(record.get("to", "")).lower()
                thread = normalize_thread(record.get("thread"))
                if thread != ACTIVE_CANON_THREAD:
                    continue
                if sender not in active or recipient not in active:
                    continue
                expected_recipient = resolve_allowed_recipient(
                    sender,
                    thread=thread,
                    active_seats=active_list,
                )
                if expected_recipient is None or recipient != expected_recipient:
                    continue
            records.append(record)
    return records[-1] if records else None


def load_active_canon() -> dict | None:
    if not ACTIVE_CANON_PATH.exists():
        return None
    return json.loads(ACTIVE_CANON_PATH.read_text(encoding="utf-8"))


def active_seats(active_canon: dict | None) -> list[str]:
    if not active_canon:
        return OUTER_SEATS
    seats = active_canon.get("active_seats")
    if isinstance(seats, list) and seats:
        return [seat for seat in seats if seat in OUTER_SEATS]
    return OUTER_SEATS


def detect_drift(latest: Path | None, active_canon: dict | None) -> dict:
    if latest is None or active_canon is None:
        return {"detected": False}

    content_text = read_handoff_text(latest)
    metadata = handoff_metadata(latest, content=content_text)
    content = content_text.lower()
    task_id = str(metadata.get("task_id") or "").upper()
    if metadata.get("is_dream_caesar") or task_id.startswith("DC-"):
        return {
            "detected": False,
            "reason": None,
            "skipped": True,
            "note_type": "dream-caesar-operations",
            "required_path_hits": [],
            "required_keyword_hits": [],
            "drift_hint_hits": [],
        }

    required_paths = [path.lower() for path in active_canon.get("required_paths", [])]
    required_keywords = [keyword.lower() for keyword in active_canon.get("required_keywords", [])]
    drift_hints = [hint.lower() for hint in active_canon.get("drift_hints", [])]

    required_path_hits = [path for path in required_paths if path in content]
    required_keyword_hits = [keyword for keyword in required_keywords if keyword in content]
    drift_hint_hits = [hint for hint in drift_hints if hint in content]

    detected = False
    reason = None
    if not required_path_hits and len(required_keyword_hits) < 2:
        detected = True
        reason = "latest handoff is not grounded in the active canon paths or keywords"
    elif len(drift_hint_hits) >= 2 and len(required_path_hits) < 2:
        detected = True
        reason = "latest handoff matches out-of-scope drift hints more strongly than the active canon"

    return {
        "detected": detected,
        "reason": reason,
        "skipped": False,
        "note_type": "implementation",
        "required_path_hits": required_path_hits,
        "required_keyword_hits": required_keyword_hits,
        "drift_hint_hits": drift_hint_hits,
    }


def validate_active_canon(active_canon: dict | None) -> dict:
    if active_canon is None:
        return {
            "valid": False,
            "reason": f"active canon file missing: {ACTIVE_CANON_PATH}",
            "missing_paths": [],
        }

    missing_paths: list[str] = []
    for raw_path in active_canon.get("required_paths", []):
        candidate = Path(str(raw_path))
        resolved = candidate if candidate.is_absolute() else REPO_ROOT / candidate
        if not resolved.exists():
            missing_paths.append(str(raw_path))

    if missing_paths:
        return {
            "valid": False,
            "reason": "active canon required paths are missing from the Dream Caesar workspace",
            "missing_paths": missing_paths,
        }

    return {
        "valid": True,
        "reason": None,
        "missing_paths": [],
    }


def send_desktop_message(seat: str, message: str) -> dict:
    result = subprocess.run(
        [
            "python",
            str(RUNNER),
            "--seat",
            seat,
            "--message",
            message,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "seat": seat,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def write_record(record: dict, log_path: Path, status_path: Path) -> None:
    ensure_runtime_dirs()
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    status_path.write_text(json.dumps(record, indent=2), encoding="utf-8")


def build_center_poke(latest_path: str | None, age_seconds: int) -> str:
    latest_text = latest_path or "NO_HANDOFF_FILE"
    return (
        f"LATEST: {latest_text} AGE: {age_seconds}s. "
        "NEXT: reassert the active queue now. "
        "If blocked, delegate unblock work. "
        "OUTPUT: next handoff task with exact path first."
    )


def build_outer_poke(seat_name: str, latest_path: str | None, age_seconds: int) -> str:
    latest_text = latest_path or "NO_HANDOFF_FILE"
    return (
        f"SEAT: {seat_name.upper()} LATEST: {latest_text} AGE: {age_seconds}s. "
        "NEXT: send your next handoff now, or state blocker path + missing input. "
        "FINAL: path-only last line."
    )


def build_mail_poke(seat_name: str, age_seconds: int) -> str:
    return (
        f"SEAT: {seat_name.upper()} MAIL_AGE: {age_seconds}s. "
        "SEND: one next-seat-only mail with exact paths. "
        "Use internal mail. Scope: active canon only."
    )


def build_blocked_poke(seat_name: str, reason: str, missing_paths: list[str]) -> str:
    path_text = " | ".join(missing_paths[:3]) if missing_paths else "NO_PATHS"
    return (
        f"SEAT: {seat_name.upper()} STATUS: BLOCKED. "
        f"REASON: {reason}. "
        f"MISSING: {path_text}. "
        "NEXT: delegate unblock work or repair canon scope with exact Dream Caesar paths."
    )


def build_center_blocked_poke(reason: str, missing_paths: list[str]) -> str:
    path_text = " | ".join(missing_paths[:3]) if missing_paths else "NO_PATHS"
    return (
        "QUEUE: BLOCKED. "
        f"REASON: {reason}. "
        f"MISSING: {path_text}. "
        "NEXT: repair canon scope or delegate unblock work with exact Dream Caesar paths first."
    )


def build_drift_poke(seat_name: str, canonical_task_file: str, objective: str, reason: str) -> str:
    return (
        f"SEAT: {seat_name.upper()} CANON_FILE: {canonical_task_file}. "
        f"DRIFT: {reason}. OBJECTIVE: {objective}. "
        "NEXT: re-anchor and send a handoff grounded only in canon paths."
    )


def build_park_poke(seat_name: str, objective: str) -> str:
    return (
        f"SEAT: {seat_name.upper()} STATUS: PARKED. "
        f"OBJECTIVE: {objective}. "
        "Hold unless assigned a supporting proof task."
    )


def build_center_drift_poke(canonical_task_file: str, objective: str, latest_path: str, reason: str) -> str:
    return (
        f"CANON_FILE: {canonical_task_file} LATEST: {latest_path}. "
        f"DRIFT: {reason}. OBJECTIVE: {objective}. "
        "NEXT: reassert the canon task now."
    )


def queue_state_summary(
    canon_validity: dict,
    active_handoff_stalled: bool,
    mail_stalled: bool,
) -> tuple[str, list[str]]:
    if not canon_validity["valid"]:
        return "blocked", ["canon_invalid"]

    reasons: list[str] = []
    if mail_stalled:
        reasons.append("mail_stalled")
    elif active_handoff_stalled:
        reasons.append("active_handoff_stalled_advisory")

    if mail_stalled:
        return "stalled", reasons
    return "moving", reasons


def main() -> int:
    parser = argparse.ArgumentParser(description="Poke Dream Caesar council seats when handoff activity stalls.")
    parser.add_argument("--interval-seconds", type=int, default=60)
    parser.add_argument("--stall-after-seconds", type=int, default=420)
    parser.add_argument("--poke-cooldown-seconds", type=int, default=300)
    parser.add_argument("--observe-only", action="store_true")
    parser.add_argument(
        "--status-path",
        default=str(OUTPUT_DIR / "desktop-council-watchdog-status.json"),
    )
    parser.add_argument(
        "--log-path",
        default=str(OUTPUT_DIR / "desktop-council-watchdog.jsonl"),
    )
    args = parser.parse_args()
    status_path = Path(args.status_path)
    log_path = Path(args.log_path)

    last_poke_at = 0.0
    last_poked_handoff = ""
    last_drift_path = ""
    last_mail_poke_at = 0.0

    while True:
        now = datetime.now().astimezone()
        active_canon = load_active_canon()
        canon_active_seats = active_seats(active_canon)
        canon_validity = validate_active_canon(active_canon)
        latest = latest_handoff(active_canon)
        latest_path = str(latest) if latest else None
        latest_metadata = handoff_metadata(latest)
        latest_mtime = latest.stat().st_mtime if latest else None
        age_seconds = int(max(0, time.time() - latest_mtime)) if latest_mtime else None
        latest_active = latest_active_handoff(active_canon)
        latest_active_path = str(latest_active) if latest_active else None
        latest_active_metadata = handoff_metadata(latest_active)
        latest_active_mtime = latest_active.stat().st_mtime if latest_active else None
        active_handoff_age_seconds = int(max(0, time.time() - latest_active_mtime)) if latest_active_mtime else None
        latest_mail = latest_mail_record(active_canon)
        latest_mail_mtime = None
        if latest_mail:
            latest_mail_mtime = datetime.fromisoformat(latest_mail["timestamp"]).timestamp()
        mail_age_seconds = int(max(0, time.time() - latest_mail_mtime)) if latest_mail_mtime else None
        handoff_stalled = age_seconds is None or age_seconds >= args.stall_after_seconds
        active_handoff_stalled = active_handoff_age_seconds is None or active_handoff_age_seconds >= args.stall_after_seconds
        mail_stalled = mail_age_seconds is None or mail_age_seconds >= args.stall_after_seconds
        queue_state, queue_reasons = queue_state_summary(
            canon_validity,
            active_handoff_stalled,
            mail_stalled,
        )
        stalled = queue_state == "stalled"
        drift = detect_drift(latest_active or latest, active_canon)

        poked = []
        if queue_state == "blocked":
            if time.time() - last_poke_at >= args.poke_cooldown_seconds:
                if not args.observe_only:
                    poked.append(
                        send_desktop_message(
                            "center",
                            build_center_blocked_poke(
                                canon_validity["reason"],
                                canon_validity["missing_paths"],
                            ),
                        )
                    )
                    for seat in canon_active_seats:
                        poked.append(
                            send_desktop_message(
                                seat,
                                build_blocked_poke(
                                    seat,
                                    canon_validity["reason"],
                                    canon_validity["missing_paths"],
                                ),
                            )
                        )
                last_poke_at = time.time()
        elif stalled:
            should_poke = (
                time.time() - last_poke_at >= args.poke_cooldown_seconds
                or latest_active_path != last_poked_handoff
            )
            if should_poke:
                if not args.observe_only:
                    poked.append(
                        send_desktop_message(
                            "center",
                            build_center_poke(
                                latest_active_path or latest_path,
                                active_handoff_age_seconds or age_seconds or -1,
                            ),
                        )
                    )
                    for seat in canon_active_seats:
                        poked.append(
                            send_desktop_message(
                                seat,
                                build_outer_poke(seat, latest_active_path, active_handoff_age_seconds or -1),
                            )
                        )
                last_poke_at = time.time()
                last_poked_handoff = latest_active_path or ""

        if drift.get("detected") and latest_active_path and latest_active_path != last_drift_path and active_canon:
            canonical_task_file = active_canon["canonical_task_file"]
            objective = active_canon["objective"]
            reason = drift["reason"]
            drifting_seat = infer_seat_from_handoff(latest_active)
            if drifting_seat:
                if not args.observe_only:
                    if drifting_seat in canon_active_seats:
                        poked.append(
                            send_desktop_message(
                                drifting_seat,
                                build_drift_poke(drifting_seat, canonical_task_file, objective, reason),
                            )
                        )
                    else:
                        poked.append(send_desktop_message(drifting_seat, build_park_poke(drifting_seat, objective)))
            last_drift_path = latest_path

        if mail_age_seconds is not None and mail_age_seconds >= args.stall_after_seconds:
            if time.time() - last_mail_poke_at >= args.poke_cooldown_seconds:
                if not args.observe_only:
                    for seat in canon_active_seats:
                        poked.append(send_desktop_message(seat, build_mail_poke(seat, mail_age_seconds)))
                last_mail_poke_at = time.time()

        record = {
            "timestamp": now.isoformat(),
            "queue_state": queue_state,
            "queue_reasons": queue_reasons,
            "canon_validity": canon_validity,
            "latest_handoff": latest_path,
            "latest_handoff_metadata": latest_metadata,
            "handoff_age_seconds": age_seconds,
            "handoff_stalled": handoff_stalled,
            "latest_active_handoff": latest_active_path,
            "latest_active_handoff_metadata": latest_active_metadata,
            "active_handoff_age_seconds": active_handoff_age_seconds,
            "active_handoff_stalled": active_handoff_stalled,
            "latest_mail_log_path": str(MAIL_LOG_PATH) if MAIL_LOG_PATH.exists() else None,
            "latest_mail_record": latest_mail,
            "mail_age_seconds": mail_age_seconds,
            "mail_stalled": mail_stalled,
            "stalled": stalled,
            "stall_after_seconds": args.stall_after_seconds,
            "poke_cooldown_seconds": args.poke_cooldown_seconds,
            "active_canon_path": str(ACTIVE_CANON_PATH) if active_canon else None,
            "active_seats": canon_active_seats,
            "drift": drift,
            "poked_count": len(poked),
            "poked": poked,
            "observe_only": args.observe_only,
        }
        write_record(record, log_path=log_path, status_path=status_path)
        print(json.dumps(record))
        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
