"""
Post-recovery data integrity checks for Dream Caesar.

Default behavior:
1) Validates canonical DB exists and passes PRAGMA integrity_check.
2) Verifies critical tables are present.
3) Prints row counts for key tables.
4) If legacy DB exists, compares row counts across shared tables.

Exit codes:
  0 = checks passed
  1 = integrity/table/count mismatch failure
  2 = invalid usage / missing canonical DB
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from typing import Iterable, List, Set, Tuple


DEFAULT_CANONICAL = Path(r"D:\dream-caesar\cosmic_council.db")
DEFAULT_LEGACY = Path(r"D:\dream-caesar\data\dream_caesar.db")

CRITICAL_TABLES = [
    "problems",
    "cycles",
    "solutions",
    "workflow_sessions",
    "workflow_steps",
    "audit_logs",
    "dreamfs_dreams",
    "knowledge_documents",
    "cc_stage_results",
    "hive_messages",
    "standalone_totem_outputs",
]

COUNT_TABLES = [
    "problems",
    "cycles",
    "audit_logs",
    "workflow_sessions",
    "workflow_steps",
    "dreamfs_dreams",
    "knowledge_documents",
    "cc_stage_results",
    "hive_messages",
    "standalone_totem_outputs",
]


def table_names(conn: sqlite3.Connection) -> Set[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return {r[0] for r in rows}


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])


def compare_counts(
    legacy: sqlite3.Connection, canonical: sqlite3.Connection, tables: Iterable[str]
) -> List[Tuple[str, int, int]]:
    mismatches: List[Tuple[str, int, int]] = []
    for t in sorted(tables):
        l_count = table_count(legacy, t)
        c_count = table_count(canonical, t)
        if l_count != c_count:
            mismatches.append((t, l_count, c_count))
    return mismatches


def main() -> int:
    parser = argparse.ArgumentParser(description="Dream Caesar DB integrity checker")
    parser.add_argument(
        "--canonical",
        default=str(DEFAULT_CANONICAL),
        help="Path to canonical DB (default: D:/dream-caesar/cosmic_council.db)",
    )
    parser.add_argument(
        "--legacy",
        default=str(DEFAULT_LEGACY),
        help="Path to legacy DB for row-count comparison (default: D:/dream-caesar/data/dream_caesar.db)",
    )
    parser.add_argument(
        "--skip-legacy-compare",
        action="store_true",
        help="Skip row-count comparison against legacy DB",
    )
    args = parser.parse_args()

    canonical_path = Path(args.canonical)
    legacy_path = Path(args.legacy)

    if not canonical_path.exists():
        print(f"FAIL: Canonical DB not found: {canonical_path}")
        return 2

    canonical = sqlite3.connect(str(canonical_path))
    try:
        integrity = canonical.execute("PRAGMA integrity_check").fetchone()[0]
        print(f"CANONICAL_DB={canonical_path}")
        print(f"INTEGRITY_CHECK={integrity}")
        if integrity != "ok":
            print("FAIL: Canonical DB failed integrity_check")
            return 1

        names = table_names(canonical)
        missing_critical = [t for t in CRITICAL_TABLES if t not in names]
        if missing_critical:
            print("FAIL: Missing critical tables:")
            for t in missing_critical:
                print(f"  - {t}")
            return 1

        print("KEY_TABLE_COUNTS")
        for t in COUNT_TABLES:
            print(f"{t}={table_count(canonical, t)}")

        if args.skip_legacy_compare:
            print("LEGACY_COMPARE=skipped")
            return 0

        if not legacy_path.exists():
            print(f"LEGACY_COMPARE=skipped (legacy DB missing: {legacy_path})")
            return 0

        legacy = sqlite3.connect(str(legacy_path))
        try:
            legacy_names = table_names(legacy)
            common = legacy_names & names
            mismatches = compare_counts(legacy, canonical, common)
            print(f"LEGACY_COMPARE_TABLES={len(common)}")
            if mismatches:
                print(f"FAIL: count mismatches={len(mismatches)}")
                for t, l_count, c_count in mismatches[:100]:
                    print(f"{t}: legacy={l_count} canonical={c_count}")
                return 1
            print("LEGACY_COMPARE=ok")
        finally:
            legacy.close()
    finally:
        canonical.close()

    print("STATUS=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
