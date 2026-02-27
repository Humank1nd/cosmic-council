"""
Phase 14 hunk-level mirror triage.

Builds a compact JSON report for high-risk file pairs so later merges can be
executed as small, reviewable hunks.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
MIRROR_ROOT = PROJECT_ROOT / "frontend" / "think-tank" / "src"

DEFAULT_FILES = [
    "cosmic_council/core/api.py",
    "cosmic_council/core/workflow_engine.py",
]


HUNK_HEADER_RE = re.compile(r"^@@ -(?P<src_start>\d+)(?:,(?P<src_count>\d+))? \+(?P<mirror_start>\d+)(?:,(?P<mirror_count>\d+))? @@")


def classify_hunk(added: list[str], removed: list[str]) -> str:
    changed = added + removed
    if not changed:
        return "empty"

    import_only = all(line.lstrip().startswith(("import ", "from ")) for line in changed if line.strip())
    comment_only = all(
        (not line.strip())
        or line.lstrip().startswith("#")
        or line.lstrip().startswith('"""')
        or line.lstrip().startswith("'''")
        for line in changed
    )
    signature_change = any(line.lstrip().startswith(("def ", "async def ", "class ")) for line in changed)

    if comment_only:
        return "safe_comment_only"
    if import_only and len(changed) <= 8:
        return "safe_import_only"
    if signature_change:
        return "high_signature_change"
    if len(changed) <= 12:
        return "review_small_logic_change"
    return "high_logic_change"


def hunk_symbol(lines: list[str], start_line: int) -> str:
    for index in range(start_line - 1, -1, -1):
        line = lines[index].strip()
        if line.startswith(("def ", "async def ", "class ")):
            return line
    return "<module>"


def triage_file(rel_path: str) -> dict[str, Any]:
    src_path = SRC_ROOT / rel_path
    mirror_path = MIRROR_ROOT / rel_path
    src_lines = src_path.read_text(encoding="utf-8", errors="replace").splitlines()
    mirror_lines = mirror_path.read_text(encoding="utf-8", errors="replace").splitlines()

    diff_lines = list(
        difflib.unified_diff(
            src_lines,
            mirror_lines,
            fromfile=str(src_path),
            tofile=str(mirror_path),
            n=3,
            lineterm="",
        )
    )

    hunks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in diff_lines:
        if line.startswith("@@ "):
            if current is not None:
                current["classification"] = classify_hunk(current["added"], current["removed"])
                current["symbol"] = hunk_symbol(src_lines, current["src_start"])
                current["changed_lines"] = len(current["added"]) + len(current["removed"])
                hunks.append(current)
            match = HUNK_HEADER_RE.match(line)
            if not match:
                continue
            current = {
                "header": line,
                "src_start": int(match.group("src_start")),
                "src_count": int(match.group("src_count") or "1"),
                "mirror_start": int(match.group("mirror_start")),
                "mirror_count": int(match.group("mirror_count") or "1"),
                "added": [],
                "removed": [],
            }
            continue
        if current is None:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            current["added"].append(line[1:])
        elif line.startswith("-") and not line.startswith("---"):
            current["removed"].append(line[1:])

    if current is not None:
        current["classification"] = classify_hunk(current["added"], current["removed"])
        current["symbol"] = hunk_symbol(src_lines, current["src_start"])
        current["changed_lines"] = len(current["added"]) + len(current["removed"])
        hunks.append(current)

    return {
        "rel_path": rel_path,
        "src_path": str(src_path),
        "mirror_path": str(mirror_path),
        "hunk_count": len(hunks),
        "hunks": hunks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 14 hunk-level mirror triage")
    parser.add_argument(
        "--json-out",
        default="recovery/phase14_hunk_triage.json",
        help="Path for JSON report output",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default=DEFAULT_FILES,
        help="Relative paths under src/",
    )
    args = parser.parse_args()

    reports = [triage_file(rel_path) for rel_path in args.files]
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": reports,
        "file_count": len(reports),
        "total_hunks": sum(report["hunk_count"] for report in reports),
    }

    out_path = Path(args.json_out)
    if not out_path.is_absolute():
        out_path = (PROJECT_ROOT / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"PHASE14_HUNK_TRIAGE={out_path}")
    print(f"FILES={summary['file_count']}")
    print(f"HUNKS={summary['total_hunks']}")
    print("STATUS=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
