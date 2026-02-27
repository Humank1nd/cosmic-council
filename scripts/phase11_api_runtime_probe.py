"""
Phase 11 API runtime probe.

Runs non-destructive HTTP checks against a live API instance and writes a JSON
report for troubleshooting and regression tracking.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def request_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    body: bytes | None = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url=url, data=body, method=method, headers=headers)
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            latency_ms = (time.perf_counter() - started) * 1000.0
            parsed: Any
            try:
                parsed = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                parsed = {"_raw": raw}
            return {
                "ok": True,
                "status_code": resp.status,
                "latency_ms": round(latency_ms, 3),
                "body": parsed,
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        latency_ms = (time.perf_counter() - started) * 1000.0
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = {"_raw": raw}
        return {
            "ok": False,
            "status_code": exc.code,
            "latency_ms": round(latency_ms, 3),
            "body": parsed,
        }
    except Exception as exc:  # pragma: no cover
        latency_ms = (time.perf_counter() - started) * 1000.0
        return {
            "ok": False,
            "status_code": None,
            "latency_ms": round(latency_ms, 3),
            "error": f"{type(exc).__name__}: {exc}",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 11 runtime API probe")
    parser.add_argument("--base-url", default="http://127.0.0.1:8012")
    parser.add_argument("--json-out", default="recovery/phase11_runtime_probe.json")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    checks: dict[str, dict[str, Any]] = {}

    checks["health"] = request_json("GET", f"{base}/health")
    checks["perpetual_status"] = request_json("GET", f"{base}/api/v1/perpetual/status")
    checks["perpetual_sessions"] = request_json("GET", f"{base}/api/v1/perpetual/sessions")
    checks["agents_list"] = request_json("GET", f"{base}/api/v1/agents/")

    process_payload = {
        "title": "Runtime probe",
        "description": "Smoke process call from phase11 probe",
        "domain": "ops",
        "complexity": "moderate",
        "stakeholders": ["andre"],
        "constraints": {},
        "success_criteria": ["200 response"],
        "context": {},
        "analysis_depth": "quick",
    }
    checks["agent_process_red_owl"] = request_json(
        "POST", f"{base}/api/v1/agents/red_owl/process", process_payload
    )
    checks["agent_process_yellow_honeybee"] = request_json(
        "POST", f"{base}/api/v1/agents/yellow_honeybee/process", process_payload
    )

    summary = {
        "total_checks": len(checks),
        "ok_checks": sum(1 for c in checks.values() if c.get("ok")),
        "failed_checks": sum(1 for c in checks.values() if not c.get("ok")),
    }
    summary["all_ok"] = summary["failed_checks"] == 0

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_url": base,
        "summary": summary,
        "checks": checks,
    }

    out_path = Path(args.json_out)
    if not out_path.is_absolute():
        out_path = (PROJECT_ROOT / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"PHASE11_REPORT={out_path}")
    print(f"CHECKS_OK={summary['ok_checks']}/{summary['total_checks']}")
    print(f"CHECKS_FAILED={summary['failed_checks']}")
    print(f"STATUS={'fail' if (args.strict and not summary['all_ok']) else 'ok'}")
    return 1 if args.strict and not summary["all_ok"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
