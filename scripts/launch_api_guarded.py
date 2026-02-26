"""
Phase 4 guarded API launcher.

Usage examples:
  python scripts/launch_api_guarded.py --smoke
  python scripts/launch_api_guarded.py
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DB = (PROJECT_ROOT / "cosmic_council.db").resolve()
PRECHECK_SCRIPT = PROJECT_ROOT / "scripts" / "preflight_db_guard.py"


def sqlite_db_path_from_url(url: str) -> Path | None:
    if url.startswith("sqlite+aiosqlite:///"):
        raw_path = url[len("sqlite+aiosqlite:///"):]
    elif url.startswith("sqlite:///"):
        raw_path = url[len("sqlite:///"):]
    else:
        return None

    if raw_path == ":memory:":
        return None

    path = Path(raw_path)
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    return path.resolve()


def run_preflight() -> int:
    if not PRECHECK_SCRIPT.exists():
        print(f"FAIL: missing preflight script: {PRECHECK_SCRIPT}")
        return 2

    result = subprocess.run(
        [sys.executable, str(PRECHECK_SCRIPT)],
        cwd=str(PROJECT_ROOT),
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return int(result.returncode)


def wait_for_health(url: str, timeout_seconds: int, process: subprocess.Popen | None = None) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if process and process.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                if 200 <= response.status < 300:
                    return True
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(1)
    return False


def health_ready(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return 200 <= response.status < 300
    except (urllib.error.URLError, TimeoutError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Guarded launcher for Cosmic Council API")
    parser.add_argument("--host", default="127.0.0.1", help="Host bind address")
    parser.add_argument("--port", type=int, default=8009, help="API port")
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip scripts/preflight_db_guard.py",
    )
    parser.add_argument(
        "--allow-db-mismatch",
        action="store_true",
        help="Allow DATABASE_URL to point to a DB other than cosmic_council.db",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Launch API, wait for /health, then stop process",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=45,
        help="Health wait timeout for smoke mode",
    )
    args = parser.parse_args()

    env = os.environ.copy()
    env.setdefault("ALLOW_ANONYMOUS", "true")
    env["API_PORT"] = str(args.port)
    env.setdefault("DREAM_CAESAR_DB_PATH", CANONICAL_DB.as_posix())
    py_path_entries = [
        str(PROJECT_ROOT),
        str(PROJECT_ROOT / "src"),
        str(PROJECT_ROOT / "config"),
    ]
    existing_py_path = env.get("PYTHONPATH", "").strip()
    if existing_py_path:
        py_path_entries.append(existing_py_path)
    env["PYTHONPATH"] = os.pathsep.join(py_path_entries)

    canonical_url = f"sqlite+aiosqlite:///{CANONICAL_DB.as_posix()}"
    db_url = env.get("DATABASE_URL", "").strip()
    if not db_url:
        env["DATABASE_URL"] = canonical_url
        print(f"DATABASE_URL=defaulted_to:{canonical_url}")
    else:
        resolved = sqlite_db_path_from_url(db_url)
        if resolved is not None:
            print(f"DATABASE_URL=resolved:{resolved}")
            if resolved != CANONICAL_DB and not args.allow_db_mismatch:
                print("FAIL: DATABASE_URL does not point to canonical DB")
                print(f"  canonical={CANONICAL_DB}")
                print(f"  actual={resolved}")
                print("  rerun with --allow-db-mismatch only if intentional")
                return 1
        else:
            print("DATABASE_URL=non-sqlite-or-memory (skip canonical path check)")

    if not args.skip_preflight:
        preflight_rc = run_preflight()
        if preflight_rc != 0:
            print(f"FAIL: preflight_db_guard.py returned {preflight_rc}")
            return preflight_rc

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "src.cosmic_council.core.api:app",
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--log-level",
        "info",
    ]

    health_url = f"http://{args.host}:{args.port}/health"

    if args.smoke:
        if health_ready(health_url):
            print(f"FAIL: target already healthy before launch: {health_url}")
            print("  choose a different --port for smoke validation")
            return 1

        print(f"Launching smoke server: {' '.join(command)}")
        process = subprocess.Popen(command, cwd=str(PROJECT_ROOT), env=env)
        try:
            healthy = wait_for_health(health_url, args.timeout_seconds, process=process)
            if not healthy:
                print(f"FAIL: health endpoint not ready within {args.timeout_seconds}s: {health_url}")
                if process.poll() is not None:
                    print(f"PROCESS_EXIT_CODE={process.returncode}")
                return 1
            print(f"SMOKE=ok ({health_url})")
            return 0
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
    else:
        print(f"Launching API: {' '.join(command)}")
        return subprocess.call(command, cwd=str(PROJECT_ROOT), env=env)


if __name__ == "__main__":
    raise SystemExit(main())
