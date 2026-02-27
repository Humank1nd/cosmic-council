"""
Extract selected hunks from the phase14 hunk triage report.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract hunks from phase14 triage report")
    parser.add_argument("--report", default="recovery/phase14_hunk_triage.json")
    parser.add_argument("--rel-path", required=True)
    parser.add_argument("--classification")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = (PROJECT_ROOT / report_path).resolve()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    file_report = next((item for item in report["files"] if item["rel_path"] == args.rel_path), None)
    if file_report is None:
        print("STATUS=missing_file")
        return 1

    hunks = file_report["hunks"]
    if args.classification:
        hunks = [h for h in hunks if h["classification"] == args.classification]

    for idx, hunk in enumerate(hunks[: args.limit], start=1):
        print(f"HUNK={idx}")
        print(f"HEADER={hunk['header']}")
        print(f"CLASSIFICATION={hunk['classification']}")
        print(f"SYMBOL={hunk['symbol']}")
        print(f"CHANGED_LINES={hunk['changed_lines']}")
        print("---")

    print(f"TOTAL={len(hunks)}")
    print("STATUS=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
