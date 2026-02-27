"""
Phase 13 endpoint contract snapshot.

Captures response-key contracts for critical API routes against a live server.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


PROCESS_RESPONSE_REQUIRED_KEYS = {
    "enterprise",
    "status",
    "confidence_score",
    "processing_time",
    "insights",
    "recommendations",
    "next_actions",
    "dependencies",
    "personality_response",
    "applied_rules",
    "wisdom_insights",
    "questions_for_next_cycle",
    "timestamp",
}


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


def collect_key_paths(obj: Any, prefix: str = "") -> set[str]:
    paths: set[str] = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else key
            paths.add(path)
            paths.update(collect_key_paths(value, path))
    elif isinstance(obj, list):
        if obj:
            paths.update(collect_key_paths(obj[0], f"{prefix}[]"))
        else:
            paths.add(f"{prefix}[]")
    return paths


def fingerprint_paths(paths: set[str]) -> str:
    text = "\n".join(sorted(paths))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 13 endpoint contract snapshot")
    parser.add_argument("--base-url", default="http://127.0.0.1:8012")
    parser.add_argument("--json-out", default="recovery/phase13_endpoint_contract_snapshot.json")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    process_payload = {
        "title": "Contract snapshot",
        "description": "Schema snapshot payload",
        "domain": "ops",
        "complexity": "moderate",
        "stakeholders": ["andre"],
        "constraints": {},
        "success_criteria": ["200 response"],
        "context": {},
        "analysis_depth": "quick",
    }

    endpoints: list[tuple[str, str, str, dict[str, Any] | None]] = [
        ("root", "GET", f"{base}/", None),
        ("health", "GET", f"{base}/health", None),
        ("perpetual_status", "GET", f"{base}/api/v1/perpetual/status", None),
        ("agents_list", "GET", f"{base}/api/v1/agents/", None),
    ]
    for enterprise in [
        "red_owl",
        "orange_orangutan",
        "yellow_honeybee",
        "green_tortoise",
        "blue_dolphin",
        "purple_elephant",
    ]:
        endpoints.append(
            (
                f"agent_process_{enterprise}",
                "POST",
                f"{base}/api/v1/agents/{enterprise}/process",
                process_payload,
            )
        )

    checks: dict[str, dict[str, Any]] = {}
    failed_contracts: list[str] = []

    for name, method, url, payload in endpoints:
        result = request_json(method, url, payload)
        body = result.get("body")
        paths = collect_key_paths(body) if isinstance(body, (dict, list)) else set()
        entry = {
            "ok": result.get("ok"),
            "status_code": result.get("status_code"),
            "latency_ms": result.get("latency_ms"),
            "top_level_keys": sorted(body.keys()) if isinstance(body, dict) else [],
            "data_keys": sorted((body.get("data") or {}).keys()) if isinstance(body, dict) and isinstance(body.get("data"), dict) else [],
            "path_count": len(paths),
            "schema_fingerprint_sha256": fingerprint_paths(paths) if paths else None,
        }

        # Minimal contract assertions for strict mode.
        if name.startswith("agent_process_"):
            if result.get("status_code") != 200:
                failed_contracts.append(f"{name}:status={result.get('status_code')}")
            elif not PROCESS_RESPONSE_REQUIRED_KEYS.issubset(set(entry["top_level_keys"])):
                failed_contracts.append(f"{name}:missing_process_keys")
        else:
            wrapper_required = {"success", "message", "data", "timestamp"}
            if result.get("status_code") != 200:
                failed_contracts.append(f"{name}:status={result.get('status_code')}")
            elif not wrapper_required.issubset(set(entry["top_level_keys"])):
                failed_contracts.append(f"{name}:missing_wrapper_keys")

        checks[name] = entry

    summary = {
        "total_checks": len(checks),
        "ok_status_checks": sum(1 for c in checks.values() if c.get("status_code") == 200),
        "failed_contract_checks": len(failed_contracts),
        "failed_contract_ids": failed_contracts,
        "all_contracts_ok": len(failed_contracts) == 0,
    }

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

    print(f"PHASE13_CONTRACT_REPORT={out_path}")
    print(f"CHECKS_OK={summary['ok_status_checks']}/{summary['total_checks']}")
    print(f"CONTRACT_FAILURES={summary['failed_contract_checks']}")
    print(f"STATUS={'fail' if (args.strict and not summary['all_contracts_ok']) else 'ok'}")
    return 1 if args.strict and not summary["all_contracts_ok"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

