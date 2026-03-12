"""
Phase 7 tests and artifacts audit/runner.

Validates expected Phase 7 files and directories, inventories artifact paths,
and can execute core pytest suite commands with bounded failure output.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class PathCheck:
    path: str
    kind: str  # file | dir
    exists: bool
    size_bytes: int | None = None
    file_count: int | None = None
    required: bool = True
    notes: str | None = None


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


PHASE7_EXPECTED_FILES = [
    # 7A
    "pytest.ini",
    "tests/__init__.py",
    "tests/conftest.py",
    "tests/fixtures/prom_registry.py",
    "tests/reason_code_registry.py",
    # 7B unit
    "tests/unit/conftest.py",
    "tests/unit/test_cosmic_council_core.py",
    "tests/unit/test_memory_store.py",
    "tests/unit/test_memory_retrieval.py",
    "tests/unit/test_memory_schemas.py",
    "tests/unit/test_enhanced_enterprise_agents.py",
    "tests/unit/test_problem_solving_workflow.py",
    "tests/unit/test_perpetual_ai_integration.py",
    "tests/unit/test_red_research.py",
    "tests/unit/test_totem_registry_aliases.py",
    "tests/unit/test_collaboration.py",
    "tests/unit/test_handshake_contracts.py",
    "tests/unit/test_council_envelope.py",
    "tests/unit/test_policy_governance.py",
    "tests/unit/test_core_api_perpetual.py",
    "tests/unit/test_ledger.py",
    "tests/unit/test_hive_bridge.py",
    "tests/unit/test_stewardship_sanity.py",
    "tests/unit/test_symbiote_skeleton.py",
    "tests/unit/test_knowledge_base_client.py",
    # 7C contract
    "tests/contract/conftest.py",
    "tests/contract/test_standalone_agents_contract.py",
    "tests/contract/test_mcp_tools_contract.py",
    # 7D + 7E + 7F + 7G integration
    "tests/integration/test_council_golden_path.py",
    "tests/integration/test_council_scenarios.py",
    "tests/integration/test_council_contracts.py",
    "tests/integration/test_api_endpoints.py",
    "tests/integration/test_standalone_agents_api.py",
    "tests/integration/test_cycle_flow_api.py",
    "tests/integration/test_workflow_sessions.py",
    "tests/integration/test_red_owl_os.py",
    "tests/integration/test_orange_orangutan_os.py",
    "tests/integration/test_yellow_honeybee_os.py",
    "tests/integration/test_green_tortoise_os.py",
    "tests/integration/test_green_tortoise_state_regression.py",
    "tests/integration/test_blue_dolphin_os.py",
    "tests/integration/test_purple_elephant_os.py",
    "tests/integration/test_red_to_orange_handoff.py",
    "tests/integration/test_symbiote_council_integration.py",
    "tests/integration/test_symbiote_gold.py",
    "tests/integration/test_phase2_governance.py",
    "tests/integration/test_phase3_tripwires.py",
    "tests/integration/test_phase4_symbiote.py",
    "tests/integration/test_phase5_cli.py",
    "tests/integration/test_policy_tripwires.py",
    "tests/integration/test_perpetual_thinking_integration.py",
    "tests/integration/test_perpetual_api_endpoints.py",
    "tests/integration/test_agent_api_hardening.py",
    "tests/integration/test_cli_commands.py",
    "tests/integration/test_ledger_persistence.py",
    "tests/integration/test_milestone3_multihost.py",
    # 7H e2e
    "tests/e2e/test_complete_workflow.py",
    "tests/e2e/test_sacred_pipeline_comprehensive.py",
    "tests/e2e/test_standalone_agents_live.py",
    "tests/e2e/test_perpetual_thinking_e2e.py",
    # 7I performance
    "tests/performance/test_load_performance.py",
    "tests/performance/test_perpetual_thinking_performance.py",
    # 7K + 7L
    "tests/test_graduation_report.py",
    "tests/test_graduation_alert_digest.py",
    "tests/test_graduation_snapshot_sync.py",
    "tests/test_ops_report_graduation.py",
    "tests/test_ops_alert_digest_graduation.py",
    "tests/test_ops_snapshot_sync_graduation.py",
    "tests/test_evidence_integrity.py",
    "tests/test_time_injection_security.py",
    "tests/test_os_regression_tripwire.py",
    "tests/test_readonly_mode.py",
    "tests/test_reason_code_coverage.py",
    "tests/test_reason_codes_compliant.py",
    "tests/test_reason_code_fixture_safety.py",
    "tests/test_scheduler_tick_signature.py",
    # 7M
    "tests/tools/gen_missing_reason_code_fixtures.py",
    # 7N
    "comprehensive_test_results.json",
    "scenarios_9_13_results.json",
    "test_execution_results.json",
    # 7P tests_new
    "tests_new/conftest.py",
    "tests_new/pytest.ini",
    "tests_new/run_tests.py",
]

PHASE7_EXPECTED_DIRS = [
    "tests/unit",
    "tests/contract",
    "tests/integration",
    "tests/e2e",
    "tests/performance",
    "tests/tools",
    "artifacts/evidence",
    "artifacts/symbiote",
    "artifacts/symbiote/mirrors",
    "artifacts/symbiote/raw_vault",
    "artifacts/blue_dolphin",
    "artifacts/yellow_honeybee",
    "artifacts/ops_reports",
    "artifacts/ops_alerts",
    "artifacts/ops_snapshots",
    "artifacts/ops_scheduler",
    "tests_new/unit",
    "tests_new/integration",
    "tests_new/e2e",
    "tests_new/performance",
    "tests_new/mocks",
    "tests_new/fixtures",
]

CORE_PYTEST_COMMANDS = [
    ("unit", ["python", "-m", "pytest", "tests/unit", "-q", "--maxfail=1"]),
    ("integration", ["python", "-m", "pytest", "tests/integration", "-q", "--maxfail=1"]),
    ("e2e", ["python", "-m", "pytest", "tests/e2e", "-q", "--maxfail=1"]),
]


def check_file(path_str: str) -> PathCheck:
    path = (PROJECT_ROOT / path_str).resolve()
    exists = path.exists() and path.is_file()
    size = path.stat().st_size if exists else None
    return PathCheck(path=path_str, kind="file", exists=exists, size_bytes=size)


def check_dir(path_str: str) -> PathCheck:
    path = (PROJECT_ROOT / path_str).resolve()
    exists = path.exists() and path.is_dir()
    count = sum(1 for p in path.rglob("*") if p.is_file()) if exists else None
    return PathCheck(path=path_str, kind="dir", exists=exists, file_count=count)


def run_cmd(command: list[str], timeout_seconds: int) -> dict[str, Any]:
    started = datetime.now(timezone.utc)
    try:
        result = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
        return {
            "command": command,
            "returncode": result.returncode,
            "started_at_utc": started.isoformat(),
            "ended_at_utc": datetime.now(timezone.utc).isoformat(),
            "stdout_tail": "\n".join(result.stdout.splitlines()[-120:]),
            "stderr_tail": "\n".join(result.stderr.splitlines()[-120:]),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": None,
            "timeout": True,
            "started_at_utc": started.isoformat(),
            "ended_at_utc": datetime.now(timezone.utc).isoformat(),
            "stdout_tail": (exc.stdout or "")[-8000:],
            "stderr_tail": (exc.stderr or "")[-8000:],
        }


def summarize_checks(file_checks: list[PathCheck], dir_checks: list[PathCheck]) -> dict[str, Any]:
    missing_files = [c.path for c in file_checks if not c.exists]
    missing_dirs = [c.path for c in dir_checks if not c.exists]
    existing_tests = sorted(
        rel(p)
        for p in (PROJECT_ROOT / "tests").rglob("test_*.py")
        if p.is_file()
    )
    existing_tests_new = sorted(
        rel(p)
        for p in (PROJECT_ROOT / "tests_new").rglob("test_*.py")
        if p.is_file()
    ) if (PROJECT_ROOT / "tests_new").exists() else []

    return {
        "expected_files_total": len(file_checks),
        "expected_files_present": len(file_checks) - len(missing_files),
        "expected_files_missing": len(missing_files),
        "expected_dirs_total": len(dir_checks),
        "expected_dirs_present": len(dir_checks) - len(missing_dirs),
        "expected_dirs_missing": len(missing_dirs),
        "missing_files": missing_files,
        "missing_dirs": missing_dirs,
        "discovered_tests": {
            "tests_count": len(existing_tests),
            "tests_new_count": len(existing_tests_new),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 7 tests/artifacts audit and runner")
    parser.add_argument("--json-out", default="recovery/phase7_tests_artifacts_report.json")
    parser.add_argument("--run-core-suites", action="store_true", help="Run pytest unit/integration/e2e commands")
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--strict", action="store_true", help="Fail when expected files/dirs are missing")
    args = parser.parse_args()

    file_checks = [check_file(path) for path in PHASE7_EXPECTED_FILES]
    dir_checks = [check_dir(path) for path in PHASE7_EXPECTED_DIRS]
    summary = summarize_checks(file_checks, dir_checks)

    command_results: list[dict[str, Any]] = []
    if args.run_core_suites:
        for _, cmd in CORE_PYTEST_COMMANDS:
            command_results.append(run_cmd(cmd, timeout_seconds=args.timeout_seconds))

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "summary": summary,
        "file_checks": [asdict(c) for c in file_checks],
        "dir_checks": [asdict(c) for c in dir_checks],
        "core_suite_runs": command_results,
    }

    out_path = Path(args.json_out)
    if not out_path.is_absolute():
        out_path = (PROJECT_ROOT / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"PHASE7_REPORT={out_path}")
    print(f"EXPECTED_FILES_PRESENT={summary['expected_files_present']}/{summary['expected_files_total']}")
    print(f"EXPECTED_DIRS_PRESENT={summary['expected_dirs_present']}/{summary['expected_dirs_total']}")
    print(f"MISSING_FILES={summary['expected_files_missing']}")
    print(f"MISSING_DIRS={summary['expected_dirs_missing']}")
    print(f"DISCOVERED_TESTS={summary['discovered_tests']['tests_count']}")
    print(f"DISCOVERED_TESTS_NEW={summary['discovered_tests']['tests_new_count']}")

    for run in command_results:
        label = " ".join(run["command"])
        rc = run.get("returncode")
        timeout = run.get("timeout", False)
        if timeout:
            print(f"CORE_SUITE=timeout command={label}")
        else:
            print(f"CORE_SUITE=rc:{rc} command={label}")

    failed = False
    if args.strict and (summary["expected_files_missing"] > 0 or summary["expected_dirs_missing"] > 0):
        failed = True
    if args.run_core_suites:
        for run in command_results:
            if run.get("timeout", False):
                failed = True
            elif run.get("returncode", 1) != 0:
                failed = True

    print(f"STATUS={'fail' if failed else 'ok'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
