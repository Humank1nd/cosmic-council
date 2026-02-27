"""
Phase 14 validation bundle runner.

Executes the current core validation gates in sequence and writes a summary JSON
report for recovery bookkeeping.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_command(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    stdout_lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    stderr_lines = [line.strip() for line in completed.stderr.splitlines() if line.strip()]
    return {
        "command": " ".join(args),
        "returncode": completed.returncode,
        "stdout_lines": stdout_lines,
        "stderr_lines": stderr_lines,
    }


def extract_status(lines: list[str]) -> str:
    for line in reversed(lines):
        if line.startswith("STATUS="):
            return line.split("=", 1)[1]
    return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 14 validation bundle")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8012",
        help="Base URL for live runtime/API validation probes",
    )
    parser.add_argument(
        "--json-out",
        default="recovery/phase14_validation_bundle.json",
        help="Path for summary JSON report",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=300,
        help="Timeout for phase7 core suite audit",
    )
    args = parser.parse_args()

    commands = [
        [
            sys.executable,
            "scripts/phase7_tests_artifacts_audit.py",
            "--run-core-suites",
            "--timeout-seconds",
            str(args.timeout_seconds),
        ],
        [
            sys.executable,
            "scripts/phase11_api_runtime_probe.py",
            "--base-url",
            args.base_url,
            "--strict",
        ],
        [
            sys.executable,
            "scripts/phase13_endpoint_contract_snapshot.py",
            "--base-url",
            args.base_url,
            "--strict",
        ],
    ]

    results = [run_command(command) for command in commands]
    all_ok = all(result["returncode"] == 0 and extract_status(result["stdout_lines"]) == "ok" for result in results)

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_url": args.base_url,
        "all_ok": all_ok,
        "results": [
            {
                **result,
                "status": extract_status(result["stdout_lines"]),
            }
            for result in results
        ],
    }

    out_path = Path(args.json_out)
    if not out_path.is_absolute():
        out_path = (PROJECT_ROOT / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"PHASE14_VALIDATION_BUNDLE={out_path}")
    print(f"COMMANDS_RUN={len(results)}")
    print(f"ALL_OK={'yes' if all_ok else 'no'}")
    for index, result in enumerate(report["results"], start=1):
        print(f"STEP_{index}_RC={result['returncode']}")
        print(f"STEP_{index}_STATUS={result['status']}")
    print(f"STATUS={'ok' if all_ok else 'fail'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
