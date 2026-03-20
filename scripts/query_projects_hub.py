#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from cosmic_council.integrations.project_implementation_hub import (
    list_project_execution_gaps,
    projects_implementation_status,
    projects_implementation_status_fast,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Query Dream Caesar's Projects & Implementation Hub.")
    parser.add_argument("--gaps", action="store_true", help="Print only execution gaps.")
    parser.add_argument("--compact", action="store_true", help="Print only the operator summary and key counts.")
    parser.add_argument("--fast", action="store_true", help="Use the fast projection path without heavy count/recent queries.")
    args = parser.parse_args()

    if args.gaps:
        print(json.dumps(list_project_execution_gaps(), indent=2))
        return 0

    status = projects_implementation_status_fast() if args.fast else projects_implementation_status()
    if args.compact:
        print(
            json.dumps(
                {
                    "truth_source": status.get("truth_source"),
                    "reconciliation_status": status.get("reconciliation_status"),
                    "reconciliation_warning": status.get("reconciliation_warning"),
                    "alignment_state": status.get("alignment_state", {}),
                    "alignment_alert": status.get("alignment_alert", {}),
                    "alignment_timeline": status.get("alignment_timeline", {}),
                    "operator_summary": status.get("operator_summary", {}),
                    "counts": status.get("counts", {}),
                    "execution_readiness": status.get("execution_readiness", {}),
                },
                indent=2,
            )
        )
        return 0

    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
