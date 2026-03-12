import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
SRC_ROOT = REPO_ROOT / "src"

src_root_str = str(SRC_ROOT)
if src_root_str not in sys.path:
    sys.path.insert(0, src_root_str)

from desktop_runtime import ARTIFACT_ROOT, HANDOFF_DIR, ensure_runtime_dirs

OUTPUT_DIR = ARTIFACT_ROOT
LOG_PATH = OUTPUT_DIR / "openclaw-desktop-monitor.jsonl"
STATUS_PATH = OUTPUT_DIR / "openclaw-desktop-monitor-status.json"
VISION_FEED_PATH = OUTPUT_DIR / "desktop-vision-feed.json"
OPENCLAW_CMD = ["wsl", "openclaw"]
AJNA_CMD = ["python", str(SCRIPT_ROOT / "ajna_monitor.py"), "--once"]


def _latest_handoff() -> dict | None:
    if not HANDOFF_DIR.exists():
        return None

    latest = max(HANDOFF_DIR.glob("*"), key=lambda path: path.stat().st_mtime, default=None)
    if latest is None:
        return None

    stat = latest.stat()
    return {
        "path": str(latest),
        "name": latest.name,
        "modified_ts": stat.st_mtime,
        "modified_iso": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(),
        "size_bytes": stat.st_size,
    }


def _run_ajna() -> dict:
    result = subprocess.run(
        AJNA_CMD,
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
        "returncode": result.returncode,
        "stdout": stdout,
        "stderr": result.stderr.strip(),
        "record": parsed,
    }


def tick(note: str, stall_after_seconds: int, emit_event: bool) -> dict:
    ensure_runtime_dirs()
    timestamp = datetime.now().astimezone()
    latest_handoff = _latest_handoff()
    handoff_age_seconds = None
    if latest_handoff is not None:
        handoff_age_seconds = max(0, int(timestamp.timestamp() - latest_handoff["modified_ts"]))

    note_text = note
    if latest_handoff is not None:
        note_text = (
            f"{note} Latest handoff: {latest_handoff['name']} ({handoff_age_seconds}s old)."
        )
    else:
        note_text = f"{note} No handoff files detected yet."

    if handoff_age_seconds is not None and handoff_age_seconds >= stall_after_seconds:
        note_text += " Activity appears stalled; inspect council state and unblock the next relay."

    ajna = _run_ajna()
    ajna_record = ajna.get("record") or {}
    screenshot_path = ajna_record.get("screenshot_path")
    ajna_summary = ajna_record.get("summary")
    if ajna_summary:
        note_text += f" Ajna: {ajna_summary}."

    if emit_event:
        event = subprocess.run(
            [
                *OPENCLAW_CMD,
                "system",
                "event",
                "--mode",
                "next-heartbeat",
                "--text",
                note_text,
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        event_returncode = event.returncode
        event_stdout = event.stdout.strip()
        event_stderr = event.stderr.strip()
    else:
        event_returncode = None
        event_stdout = ""
        event_stderr = "skipped: emit_event disabled"

    record = {
        "timestamp": timestamp.isoformat(),
        "note": note_text,
        "event_returncode": event_returncode,
        "event_stdout": event_stdout,
        "event_stderr": event_stderr,
        "screenshot_path": screenshot_path,
        "screenshot_success": bool(ajna_record.get("screenshot_success")),
        "latest_handoff": latest_handoff,
        "handoff_age_seconds": handoff_age_seconds,
        "stall_after_seconds": stall_after_seconds,
        "stalled": handoff_age_seconds is not None and handoff_age_seconds >= stall_after_seconds,
        "ajna": {
            "returncode": ajna["returncode"],
            "stderr": ajna["stderr"],
            "summary": ajna_summary,
            "missing_active_seats": ajna_record.get("missing_active_seats"),
            "ambiguous_seats": ajna_record.get("ambiguous_seats"),
            "overall_state": (ajna_record.get("vision") or {}).get("overall_state"),
            "status_path": str(OUTPUT_DIR / "ajna-monitor-status.json"),
        },
    }
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    STATUS_PATH.write_text(json.dumps(record, indent=2), encoding="utf-8")
    VISION_FEED_PATH.write_text(
        json.dumps(
            {
                "timestamp": timestamp.isoformat(),
                "screenshot_path": screenshot_path,
                "note": note_text,
                "latest_handoff_path": latest_handoff["path"] if latest_handoff else None,
                "ajna_summary": ajna_summary,
                "ajna_missing_active_seats": ajna_record.get("missing_active_seats"),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit OpenClaw heartbeat events and capture council screenshots.")
    parser.add_argument("--interval-seconds", type=int, default=300)
    parser.add_argument("--note", default="Dream Caesar council monitor tick: keep desktop agents aligned, path-based, and visually verified.")
    parser.add_argument("--stall-after-seconds", type=int, default=900)
    parser.add_argument("--emit-event", action="store_true")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    while True:
        record = tick(args.note, args.stall_after_seconds, args.emit_event)
        print(json.dumps(record))
        if args.once:
            return 0
        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
