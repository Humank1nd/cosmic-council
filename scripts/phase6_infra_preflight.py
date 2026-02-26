"""
Phase 6 infrastructure and DevOps preflight checks.

This script performs static validations only (no deploy actions).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Finding:
    severity: str  # error | warning | info
    code: str
    message: str
    path: str | None = None


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def parse_dockerfile_stages(path: Path) -> set[str]:
    stage_re = re.compile(r"^\s*FROM\s+\S+\s+AS\s+([A-Za-z0-9_.-]+)\s*$", re.IGNORECASE)
    stages: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = stage_re.match(line)
        if match:
            stages.add(match.group(1).lower())
    return stages


def extract_bind_source(volume_spec: str) -> str | None:
    if ":" not in volume_spec:
        return None
    source = volume_spec.split(":", 1)[0].strip()
    if not source:
        return None
    if source.startswith(".") or source.startswith("/") or source.startswith("\\"):
        return source
    return None


def check_required_paths(findings: list[Finding]) -> None:
    required_files = [
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.dev.yml",
        "infrastructure/README.md",
        "infrastructure/deploy.sh",
        "infrastructure/deploy.ps1",
        ".github/workflows/ci.yml",
        ".github/workflows/ci-cd.yml",
    ]
    for entry in required_files:
        path = PROJECT_ROOT / entry
        if not path.exists():
            findings.append(Finding("error", "missing_required_file", f"Missing required file: {entry}", entry))

    required_dirs = {
        "infrastructure/k8s": 1,
        "infrastructure/kubernetes": 1,
        "infrastructure/monitoring": 1,
        ".github/workflows": 1,
    }
    for entry, min_files in required_dirs.items():
        path = PROJECT_ROOT / entry
        if not path.exists():
            findings.append(Finding("error", "missing_required_dir", f"Missing required directory: {entry}", entry))
            continue
        count = sum(1 for p in path.rglob("*") if p.is_file())
        if count < min_files:
            findings.append(
                Finding("error", "insufficient_files", f"Directory has too few files ({count} < {min_files})", entry)
            )


def check_compose_and_dockerfile(findings: list[Finding]) -> None:
    dockerfile_path = PROJECT_ROOT / "Dockerfile"
    if not dockerfile_path.exists():
        return

    stages = parse_dockerfile_stages(dockerfile_path)
    for required_stage in ("development", "production"):
        if required_stage not in stages:
            findings.append(
                Finding(
                    "error",
                    "dockerfile_stage_missing",
                    f"Dockerfile missing '{required_stage}' stage required by compose/workflows",
                    "Dockerfile",
                )
            )

    compose_expectations = {
        "docker-compose.yml": {"postgres", "n8n", "gateway", "analytics", "reflection"},
        "docker-compose.dev.yml": {
            "postgres-dev",
            "postgres-perpetual-dev",
            "redis-dev",
            "api-dev",
            "web-dev",
            "nginx-dev",
            "prometheus-dev",
            "grafana-dev",
        },
    }

    for compose_name, expected_services in compose_expectations.items():
        compose_path = PROJECT_ROOT / compose_name
        if not compose_path.exists():
            continue
        try:
            doc = load_yaml(compose_path)
        except Exception as exc:  # pragma: no cover
            findings.append(
                Finding("error", "yaml_parse_error", f"Failed to parse compose file: {exc}", compose_name)
            )
            continue

        services = doc.get("services") if isinstance(doc, dict) else None
        if not isinstance(services, dict) or not services:
            findings.append(
                Finding("error", "compose_services_missing", "Compose file missing non-empty services map", compose_name)
            )
            continue

        missing = sorted(expected_services - set(services.keys()))
        if missing:
            findings.append(
                Finding("error", "compose_expected_service_missing", f"Missing expected services: {', '.join(missing)}", compose_name)
            )

        for service_name, service in services.items():
            if not isinstance(service, dict):
                continue

            build = service.get("build")
            if isinstance(build, dict):
                target = build.get("target")
                if target and str(target).lower() not in stages:
                    findings.append(
                        Finding(
                            "error",
                            "compose_build_target_missing",
                            f"Service '{service_name}' targets missing Dockerfile stage '{target}'",
                            compose_name,
                        )
                    )

            for volume in service.get("volumes", []) or []:
                if not isinstance(volume, str):
                    continue
                source = extract_bind_source(volume)
                if source is None:
                    continue
                source_path = (PROJECT_ROOT / source).resolve() if source.startswith(".") else Path(source)
                if source.startswith(".") and not source_path.exists():
                    findings.append(
                        Finding(
                            "error",
                            "compose_bind_source_missing",
                            f"Service '{service_name}' bind source does not exist: {source}",
                            compose_name,
                        )
                    )


def check_workflows(findings: list[Finding]) -> None:
    workflows_dir = PROJECT_ROOT / ".github" / "workflows"
    if not workflows_dir.exists():
        return

    workflow_paths = sorted(workflows_dir.glob("*.yml"))
    if not workflow_paths:
        findings.append(Finding("error", "workflows_missing", "No workflow files found", rel(workflows_dir)))
        return

    uses_master_re = re.compile(r"@master\b", re.IGNORECASE)
    curated_refs: dict[str, list[str]] = {
        "ci-cd.yml": ["requirements-test.txt"],
        "enhanced-ci-cd.yml": [
            "requirements-test.txt",
            "requirements.in",
            "requirements-test.in",
            "mkdocs.yml",
            "tests/smoke/staging_smoke_tests.py",
            "tests/health/production_health_checks.py",
            "tests/performance/locustfile.py",
            "tests/performance/k6_script.js",
        ],
        "release.yml": ["mkdocs.yml"],
    }

    for workflow_path in workflow_paths:
        try:
            doc = load_yaml(workflow_path)
        except Exception as exc:  # pragma: no cover
            findings.append(
                Finding("error", "yaml_parse_error", f"Failed to parse workflow: {exc}", rel(workflow_path))
            )
            continue

        if not isinstance(doc, dict):
            findings.append(
                Finding("error", "workflow_invalid_root", "Workflow YAML root is not a mapping", rel(workflow_path))
            )
            continue

        jobs = doc.get("jobs")
        if not isinstance(jobs, dict) or not jobs:
            findings.append(Finding("error", "workflow_jobs_missing", "Workflow has no jobs", rel(workflow_path)))

        content = workflow_path.read_text(encoding="utf-8")
        if uses_master_re.search(content):
            findings.append(
                Finding(
                    "warning",
                    "workflow_unpinned_master",
                    "Workflow uses @master action references; pin to a version/tag or commit SHA",
                    rel(workflow_path),
                )
            )

        for ref in curated_refs.get(workflow_path.name, []):
            if not (PROJECT_ROOT / ref).exists():
                findings.append(
                    Finding(
                        "warning",
                        "workflow_ref_missing",
                        f"Workflow references file not found locally: {ref}",
                        rel(workflow_path),
                    )
                )


def check_tooling(findings: list[Finding]) -> None:
    for tool in ("docker", "kubectl", "gh"):
        if shutil.which(tool):
            findings.append(Finding("info", "tool_available", f"Tool available: {tool}"))
        else:
            findings.append(Finding("warning", "tool_missing", f"Tool not found in PATH: {tool}"))


def optional_compose_config_validation(findings: list[Finding]) -> None:
    if not shutil.which("docker"):
        findings.append(
            Finding("warning", "compose_validation_skipped", "Skipped docker compose config validation (docker missing)")
        )
        return

    for compose_name in ("docker-compose.yml", "docker-compose.dev.yml"):
        compose_path = PROJECT_ROOT / compose_name
        if not compose_path.exists():
            continue
        result = subprocess.run(
            ["docker", "compose", "-f", str(compose_path), "config"],
            cwd=str(PROJECT_ROOT),
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or "unknown docker compose error"
            findings.append(
                Finding(
                    "warning",
                    "compose_config_failed",
                    f"`docker compose config` failed: {message}",
                    compose_name,
                )
            )
        else:
            findings.append(Finding("info", "compose_config_ok", "`docker compose config` succeeded", compose_name))


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 6 infrastructure preflight checks")
    parser.add_argument("--json-out", help="Optional JSON report output path")
    parser.add_argument("--strict", action="store_true", help="Fail on errors")
    parser.add_argument("--fail-on-warn", action="store_true", help="Fail on warnings as well")
    parser.add_argument(
        "--validate-compose-with-docker",
        action="store_true",
        help="Run `docker compose config` checks when docker is available",
    )
    args = parser.parse_args()

    findings: list[Finding] = []
    check_required_paths(findings)
    check_compose_and_dockerfile(findings)
    check_workflows(findings)
    check_tooling(findings)
    if args.validate_compose_with_docker:
        optional_compose_config_validation(findings)

    severity_counts = {
        "error": sum(1 for f in findings if f.severity == "error"),
        "warning": sum(1 for f in findings if f.severity == "warning"),
        "info": sum(1 for f in findings if f.severity == "info"),
    }

    print(f"PHASE6_PREFLIGHT_AT={datetime.now(timezone.utc).isoformat()}")
    print(f"ERRORS={severity_counts['error']}")
    print(f"WARNINGS={severity_counts['warning']}")
    print(f"INFO={severity_counts['info']}")
    for finding in findings:
        path_suffix = f" path={finding.path}" if finding.path else ""
        print(f"[{finding.severity.upper()}] {finding.code}: {finding.message}{path_suffix}")

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "severity_counts": severity_counts,
        "findings": [asdict(f) for f in findings],
    }
    if args.json_out:
        out_path = Path(args.json_out)
        if not out_path.is_absolute():
            out_path = (PROJECT_ROOT / out_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"JSON_REPORT={out_path}")

    failed = False
    if args.fail_on_warn and severity_counts["warning"] > 0:
        failed = True
    elif args.strict and severity_counts["error"] > 0:
        failed = True

    print(f"STATUS={'fail' if failed else 'ok'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
