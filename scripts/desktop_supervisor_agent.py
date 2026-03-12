#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent

script_root_str = str(SCRIPT_ROOT)
if script_root_str not in sys.path:
    sys.path.insert(0, script_root_str)

from desktop_runtime import ARTIFACT_ROOT, RUNTIME_ROOT, ensure_runtime_dirs


STATUS_PATH = ARTIFACT_ROOT / "desktop-supervisor-status.json"
LOG_PATH = ARTIFACT_ROOT / "desktop-supervisor.jsonl"
PROCESS_LOG_DIR = ARTIFACT_ROOT / "supervisor-logs"

PYTHON = sys.executable


@dataclass(frozen=True)
class WorkerSpec:
    name: str
    command: list[str]
    status_path: Path
    stdout_path: Path
    stderr_path: Path
    max_status_age_seconds: int


def _worker_specs(args: argparse.Namespace) -> list[WorkerSpec]:
    openclaw_monitor = str(SCRIPT_ROOT / "openclaw_desktop_council_monitor.py")
    relay_script = str(SCRIPT_ROOT / "terminal_langchain.py")
    mail_consumer = str(SCRIPT_ROOT / "seat_mailbox_consumer.py")
    active_terminal_worker = str(SCRIPT_ROOT / "active_canon_terminal_worker.py")
    alignment_audit = str(SCRIPT_ROOT / "coordinator_alignment_runner.py")
    watchdog = str(SCRIPT_ROOT / "desktop_council_watchdog.py")
    return [
        WorkerSpec(
            name="heartbeat",
            command=[
                PYTHON,
                openclaw_monitor,
                "--interval-seconds",
                str(args.heartbeat_interval_seconds),
                "--stall-after-seconds",
                str(args.stall_after_seconds),
                "--emit-event" if args.heartbeat_emit_event else "",
                "--note",
                "Dream Caesar heartbeat: keep desktop agents alive, check mail, relay next-seat-only, and never stop.",
            ],
            status_path=ARTIFACT_ROOT / "openclaw-desktop-monitor-status.json",
            stdout_path=PROCESS_LOG_DIR / "heartbeat.stdout.log",
            stderr_path=PROCESS_LOG_DIR / "heartbeat.stderr.log",
            max_status_age_seconds=max(args.heartbeat_interval_seconds * 3, 180),
        ),
        WorkerSpec(
            name="relay",
            command=[
                PYTHON,
                relay_script,
                "--interval-seconds",
                str(args.relay_interval_seconds),
                "--submit-mode",
                args.submit_mode,
                "--delivery-mode",
                args.delivery_mode,
            ],
            status_path=RUNTIME_ROOT / "terminal-langchain-status.json",
            stdout_path=PROCESS_LOG_DIR / "relay.stdout.log",
            stderr_path=PROCESS_LOG_DIR / "relay.stderr.log",
            max_status_age_seconds=max(args.relay_interval_seconds * 3, 180),
        ),
        WorkerSpec(
            name="mail_consumer",
            command=[
                PYTHON,
                mail_consumer,
                "--interval-seconds",
                str(args.mail_consumer_interval_seconds),
            ],
            status_path=RUNTIME_ROOT / "seat-mailbox-consumer-status.json",
            stdout_path=PROCESS_LOG_DIR / "mail_consumer.stdout.log",
            stderr_path=PROCESS_LOG_DIR / "mail_consumer.stderr.log",
            max_status_age_seconds=max(args.mail_consumer_interval_seconds * 3, 60),
        ),
        WorkerSpec(
            name="active_terminal_worker",
            command=[
                PYTHON,
                active_terminal_worker,
                "--interval-seconds",
                str(args.active_terminal_worker_interval_seconds),
            ],
            status_path=RUNTIME_ROOT / "active-canon-terminal-worker-status.json",
            stdout_path=PROCESS_LOG_DIR / "active_terminal_worker.stdout.log",
            stderr_path=PROCESS_LOG_DIR / "active_terminal_worker.stderr.log",
            max_status_age_seconds=max(args.active_terminal_worker_interval_seconds * 8, 900),
        ),
        WorkerSpec(
            name="alignment_audit",
            command=[
                PYTHON,
                alignment_audit,
                "--interval-seconds",
                str(args.alignment_audit_interval_seconds),
            ],
            status_path=RUNTIME_ROOT / "coordinator-alignment-audit.json",
            stdout_path=PROCESS_LOG_DIR / "alignment_audit.stdout.log",
            stderr_path=PROCESS_LOG_DIR / "alignment_audit.stderr.log",
            max_status_age_seconds=max(args.alignment_audit_interval_seconds * 3, 180),
        ),
        WorkerSpec(
            name="watchdog",
            command=[
                PYTHON,
                watchdog,
                "--observe-only",
                "--interval-seconds",
                str(args.watchdog_interval_seconds),
                "--stall-after-seconds",
                str(args.stall_after_seconds),
                "--poke-cooldown-seconds",
                str(args.poke_cooldown_seconds),
            ],
            status_path=ARTIFACT_ROOT / "desktop-council-watchdog-status.json",
            stdout_path=PROCESS_LOG_DIR / "watchdog.stdout.log",
            stderr_path=PROCESS_LOG_DIR / "watchdog.stderr.log",
            max_status_age_seconds=max(args.watchdog_interval_seconds * 3, 180),
        ),
    ]


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _status_age_seconds(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        return max(0, int(time.time() - path.stat().st_mtime))
    except OSError:
        return None


def _spawn(spec: WorkerSpec) -> subprocess.Popen[str]:
    spec.stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_handle = open(spec.stdout_path, "a", encoding="utf-8")
    stderr_handle = open(spec.stderr_path, "a", encoding="utf-8")
    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
    return subprocess.Popen(
        [part for part in spec.command if part],
        stdout=stdout_handle,
        stderr=stderr_handle,
        text=True,
        cwd=str(REPO_ROOT),
        creationflags=creationflags,
    )


def _stop_process(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            proc.send_signal(signal.CTRL_BREAK_EVENT)
            proc.wait(timeout=5)
        else:
            proc.terminate()
            proc.wait(timeout=5)
    except Exception:
        proc.kill()
        proc.wait(timeout=5)


def _record(status: dict[str, Any]) -> None:
    ensure_runtime_dirs()
    PROCESS_LOG_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(status) + "\n")
    STATUS_PATH.write_text(json.dumps(status, indent=2), encoding="utf-8")


def _summarize_worker(spec: WorkerSpec, proc: subprocess.Popen[str]) -> dict[str, Any]:
    status_record = _read_json(spec.status_path)
    status_age = _status_age_seconds(spec.status_path)
    healthy = proc.poll() is None and status_age is not None and status_age <= spec.max_status_age_seconds
    return {
        "name": spec.name,
        "pid": proc.pid,
        "running": proc.poll() is None,
        "returncode": proc.poll(),
        "status_path": str(spec.status_path),
        "status_age_seconds": status_age,
        "max_status_age_seconds": spec.max_status_age_seconds,
        "healthy": healthy,
        "status_record": status_record,
    }


def run_supervisor(args: argparse.Namespace) -> int:
    ensure_runtime_dirs()
    PROCESS_LOG_DIR.mkdir(parents=True, exist_ok=True)

    specs = _worker_specs(args)
    procs: dict[str, subprocess.Popen[str]] = {}
    restart_counts: dict[str, int] = {spec.name: 0 for spec in specs}
    start_times: dict[str, str] = {}

    try:
        while True:
            for spec in specs:
                proc = procs.get(spec.name)
                status_age = _status_age_seconds(spec.status_path)
                stale = status_age is None or status_age > spec.max_status_age_seconds
                dead = proc is None or proc.poll() is not None
                if dead or stale:
                    if proc is not None and proc.poll() is None:
                        _stop_process(proc)
                    procs[spec.name] = _spawn(spec)
                    restart_counts[spec.name] += 1
                    start_times[spec.name] = _now_iso()

            workers = [_summarize_worker(spec, procs[spec.name]) for spec in specs]
            watchdog_record = _read_json(ARTIFACT_ROOT / "desktop-council-watchdog-status.json") or {}
            supervisor_status = {
                "timestamp": _now_iso(),
                "supervisor_pid": os.getpid(),
                "workers": workers,
                "restart_counts": restart_counts,
                "started_at": start_times,
                "queue_state": watchdog_record.get("queue_state"),
                "mail_age_seconds": watchdog_record.get("mail_age_seconds"),
                "active_handoff_age_seconds": watchdog_record.get("active_handoff_age_seconds"),
                "latest_active_handoff": watchdog_record.get("latest_active_handoff"),
                "all_healthy": all(worker["healthy"] for worker in workers),
            }
            _record(supervisor_status)
            print(json.dumps(supervisor_status), flush=True)

            if args.once:
                return 0
            time.sleep(args.interval_seconds)
    finally:
        if args.leave_children_running:
            return 0
        for proc in procs.values():
            _stop_process(proc)


def main() -> int:
    parser = argparse.ArgumentParser(description="Keep Dream Caesar desktop workers alive.")
    parser.add_argument("--interval-seconds", type=int, default=30)
    parser.add_argument("--heartbeat-interval-seconds", type=int, default=300)
    parser.add_argument("--relay-interval-seconds", type=int, default=90)
    parser.add_argument("--mail-consumer-interval-seconds", type=int, default=15)
    parser.add_argument("--active-terminal-worker-interval-seconds", type=int, default=120)
    parser.add_argument("--alignment-audit-interval-seconds", type=int, default=300)
    parser.add_argument("--watchdog-interval-seconds", type=int, default=60)
    parser.add_argument("--stall-after-seconds", type=int, default=420)
    parser.add_argument("--poke-cooldown-seconds", type=int, default=300)
    parser.add_argument("--heartbeat-emit-event", action="store_true")
    parser.add_argument("--submit-mode", choices=["enter", "ctrl-enter", "both"], default="both")
    parser.add_argument(
        "--delivery-mode",
        choices=["internal-mail", "openclaw", "openclaw-fallback-desktop", "desktop"],
        default="internal-mail",
    )
    parser.add_argument("--leave-children-running", action="store_true")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    return run_supervisor(args)


if __name__ == "__main__":
    raise SystemExit(main())
