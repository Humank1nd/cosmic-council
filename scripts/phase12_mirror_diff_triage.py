"""
Phase 12 mirror diff triage.

Analyzes src/ vs frontend/think-tank/src diff set and ranks merge risk so
recovery batches can proceed safely.
"""

from __future__ import annotations

import argparse
import difflib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BRANDING_TOKENS = [
    ("Cosmic Council", "Agent Orchestrator"),
    ("cosmic council", "agent orchestrator"),
    ("CosmicCouncil", "AgentOrchestrator"),
]


@dataclass
class FileTriage:
    rel_path: str
    added_lines: int
    removed_lines: int
    total_changed_lines: int
    has_signature_change: bool
    has_import_change: bool
    only_comment_or_docstring: bool
    branding_only: bool
    risk: str


def normalize_branding(text: str) -> str:
    out = text
    for old, new in BRANDING_TOKENS:
        out = out.replace(old, "{PROJECT_NAME}")
        out = out.replace(new, "{PROJECT_NAME}")
    return out


def is_comment_or_doc_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if s.startswith("#"):
        return True
    if s.startswith('"""') or s.startswith("'''"):
        return True
    if s.startswith("*") or s.startswith("- "):
        return True
    return False


def triage_file(rel_path: str) -> FileTriage | None:
    src_path = PROJECT_ROOT / "src" / rel_path
    mirror_path = PROJECT_ROOT / "frontend" / "think-tank" / "src" / rel_path
    if not (src_path.exists() and mirror_path.exists()):
        return None

    src_lines = src_path.read_text(encoding="utf-8", errors="replace").splitlines()
    mirror_lines = mirror_path.read_text(encoding="utf-8", errors="replace").splitlines()

    diff = list(difflib.unified_diff(src_lines, mirror_lines, n=0))
    removed = [l[1:] for l in diff if l.startswith("-") and not l.startswith("---")]
    added = [l[1:] for l in diff if l.startswith("+") and not l.startswith("+++")]

    total = len(added) + len(removed)
    has_signature = any(
        l.lstrip().startswith(("def ", "async def ", "class "))
        for l in added + removed
    )
    has_import = any(
        l.lstrip().startswith(("import ", "from "))
        for l in added + removed
    )
    only_comment_doc = all(is_comment_or_doc_line(l) for l in added + removed)

    norm_removed = [normalize_branding(l.strip()) for l in removed if l.strip()]
    norm_added = [normalize_branding(l.strip()) for l in added if l.strip()]
    branding_only = (
        bool(norm_removed or norm_added)
        and sorted(norm_removed) == sorted(norm_added)
        and not has_signature
        and not has_import
    )

    risk = "high"
    if only_comment_doc and total <= 30:
        risk = "low"
    elif branding_only and total <= 30:
        risk = "low"
    elif not has_signature and not has_import and total <= 20:
        risk = "medium"
    elif has_signature and total <= 12:
        risk = "medium"

    return FileTriage(
        rel_path=rel_path,
        added_lines=len(added),
        removed_lines=len(removed),
        total_changed_lines=total,
        has_signature_change=has_signature,
        has_import_change=has_import,
        only_comment_or_docstring=only_comment_doc,
        branding_only=branding_only,
        risk=risk,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 12 mirror diff risk triage")
    parser.add_argument(
        "--input-report",
        default="recovery/phase9_mirror_restore_plan.json",
        help="Path to phase9 mirror restore report",
    )
    parser.add_argument(
        "--json-out",
        default="recovery/phase12_mirror_diff_triage.json",
    )
    args = parser.parse_args()

    input_path = Path(args.input_report)
    if not input_path.is_absolute():
        input_path = (PROJECT_ROOT / input_path).resolve()
    if not input_path.exists():
        print(f"ERROR=missing_input_report path={input_path}")
        print("STATUS=fail")
        return 1

    report = json.loads(input_path.read_text(encoding="utf-8"))
    rel_paths = report["restore_candidates"]["merge_review_required"]

    triage: list[FileTriage] = []
    missing = 0
    for rel in rel_paths:
        row = triage_file(rel)
        if row is None:
            missing += 1
            continue
        triage.append(row)

    triage_sorted = sorted(
        triage, key=lambda r: ({"low": 0, "medium": 1, "high": 2}[r.risk], r.total_changed_lines, r.rel_path)
    )

    by_risk = {
        "low": sum(1 for r in triage_sorted if r.risk == "low"),
        "medium": sum(1 for r in triage_sorted if r.risk == "medium"),
        "high": sum(1 for r in triage_sorted if r.risk == "high"),
    }

    low_candidates = [asdict(r) for r in triage_sorted if r.risk == "low"][:50]
    medium_candidates = [asdict(r) for r in triage_sorted if r.risk == "medium"][:50]

    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "input_report": str(input_path),
        "summary": {
            "files_considered": len(triage_sorted),
            "files_missing": missing,
            "risk_counts": by_risk,
        },
        "low_risk_candidates": low_candidates,
        "medium_risk_candidates": medium_candidates,
        "triage": [asdict(r) for r in triage_sorted],
    }

    out_path = Path(args.json_out)
    if not out_path.is_absolute():
        out_path = (PROJECT_ROOT / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"PHASE12_REPORT={out_path}")
    print(f"FILES_CONSIDERED={out['summary']['files_considered']}")
    print(f"LOW_RISK={by_risk['low']}")
    print(f"MEDIUM_RISK={by_risk['medium']}")
    print(f"HIGH_RISK={by_risk['high']}")
    print("STATUS=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
