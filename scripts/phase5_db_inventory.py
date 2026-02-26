"""
Phase 5 database and data inventory (read-only).

This script does not modify database contents.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class DbTarget:
    relative_path: str
    purpose: str
    required: bool = False


DB_TARGETS = [
    DbTarget("cosmic_council.db", "Main council DB", required=True),
    DbTarget("perpetual_thinking.db", "Perpetual thinking DB", required=True),
    DbTarget("data/dream_caesar.db", "Primary Dream Caesar DB", required=True),
    DbTarget("data/strategy_store.db", "Strategy store DB", required=True),
    DbTarget("test_cosmic_council.db", "Test DB (commonly empty)", required=False),
    DbTarget("test_perpetual.db", "Test perpetual DB", required=False),
]


def format_bytes(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(num_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)}{unit}"
            return f"{value:.1f}{unit}"
        value /= 1024.0
    return f"{num_bytes}B"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sqlite_ro_conn(path: Path) -> sqlite3.Connection:
    uri = f"file:{path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def inspect_sqlite(path: Path, full_integrity: bool = False) -> dict[str, Any]:
    with sqlite_ro_conn(path) as conn:
        integrity_pragma = "PRAGMA integrity_check" if full_integrity else "PRAGMA quick_check"
        integrity = str(conn.execute(integrity_pragma).fetchone()[0])

        table_count = int(
            conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ).fetchone()[0]
        )
        index_count = int(
            conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
            ).fetchone()[0]
        )
        view_count = int(
            conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='view'").fetchone()[0]
        )
        trigger_count = int(
            conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='trigger'").fetchone()[0]
        )

        sample_tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                "ORDER BY name LIMIT 8"
            ).fetchall()
        ]

    return {
        "integrity": integrity,
        "table_count": table_count,
        "index_count": index_count,
        "view_count": view_count,
        "trigger_count": trigger_count,
        "sample_tables": sample_tables,
    }


def sorted_files(path: Path, pattern: str) -> list[str]:
    return sorted(
        str(p.relative_to(PROJECT_ROOT)).replace("\\", "/")
        for p in path.glob(pattern)
        if p.is_file()
    )


def build_inventory(full_integrity: bool, include_hash: bool) -> dict[str, Any]:
    inventory: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "databases": [],
        "artifacts": {},
    }

    for target in DB_TARGETS:
        absolute = (PROJECT_ROOT / target.relative_path).resolve()
        entry: dict[str, Any] = {
            "path": target.relative_path,
            "absolute_path": str(absolute),
            "purpose": target.purpose,
            "required": target.required,
            "exists": absolute.exists(),
        }

        if absolute.exists():
            stat = absolute.stat()
            entry["size_bytes"] = stat.st_size
            entry["size_human"] = format_bytes(stat.st_size)
            entry["modified_utc"] = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            if include_hash:
                entry["sha256"] = sha256(absolute)
            if stat.st_size > 0:
                entry["sqlite"] = inspect_sqlite(absolute, full_integrity=full_integrity)
            else:
                entry["sqlite"] = {"status": "empty_file"}
        inventory["databases"].append(entry)

    database_root = PROJECT_ROOT / "database"
    src_database_root = PROJECT_ROOT / "src" / "database"
    inventory["artifacts"] = {
        "master_schemas": sorted_files(database_root / "schemas", "*.sql"),
        "migrations": sorted_files(src_database_root / "migrations", "*.sql"),
        "models": sorted_files(src_database_root / "models", "*.py"),
        "repositories": sorted_files(src_database_root / "repositories", "*.py"),
        "seed_csvs": sorted_files(src_database_root / "seeds", "*.csv")
        + sorted_files(database_root / "seeds" / "cosmic_council_airtable_csv", "*.csv"),
    }

    return inventory


def status_from_inventory(inventory: dict[str, Any]) -> tuple[bool, list[str]]:
    issues: list[str] = []
    ok = True
    for db in inventory["databases"]:
        if db["required"] and not db["exists"]:
            ok = False
            issues.append(f"missing required DB: {db['path']}")
            continue
        sqlite_info = db.get("sqlite")
        if not sqlite_info:
            continue
        integrity = sqlite_info.get("integrity")
        if integrity and integrity != "ok":
            ok = False
            issues.append(f"integrity check failed for {db['path']}: {integrity}")
    return ok, issues


def print_inventory(inventory: dict[str, Any]) -> None:
    print(f"PHASE5_INVENTORY_AT={inventory['generated_at_utc']}")
    print("DATABASE_FILES")
    for db in inventory["databases"]:
        print(f"- path={db['path']} exists={db['exists']} required={db['required']}")
        if not db["exists"]:
            continue
        print(f"  size={db['size_human']} ({db['size_bytes']} bytes)")
        print(f"  modified_utc={db['modified_utc']}")
        sqlite_info = db.get("sqlite", {})
        if "status" in sqlite_info:
            print(f"  sqlite={sqlite_info['status']}")
        else:
            print(
                "  sqlite="
                f"integrity={sqlite_info['integrity']} "
                f"tables={sqlite_info['table_count']} "
                f"indexes={sqlite_info['index_count']} "
                f"views={sqlite_info['view_count']} "
                f"triggers={sqlite_info['trigger_count']}"
            )

    print("ARTIFACT_COUNTS")
    artifacts = inventory["artifacts"]
    print(f"- master_schemas={len(artifacts['master_schemas'])}")
    print(f"- migrations={len(artifacts['migrations'])}")
    print(f"- models={len(artifacts['models'])}")
    print(f"- repositories={len(artifacts['repositories'])}")
    print(f"- seed_csvs={len(artifacts['seed_csvs'])}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 5 DB inventory (read-only)")
    parser.add_argument(
        "--full-integrity",
        action="store_true",
        help="Use PRAGMA integrity_check instead of quick_check",
    )
    parser.add_argument(
        "--include-hash",
        action="store_true",
        help="Include SHA-256 for each existing DB file",
    )
    parser.add_argument(
        "--json-out",
        help="Optional output path for JSON report",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero on missing required DB or failed integrity",
    )
    args = parser.parse_args()

    inventory = build_inventory(full_integrity=args.full_integrity, include_hash=args.include_hash)
    print_inventory(inventory)

    ok, issues = status_from_inventory(inventory)
    if issues:
        print("ISSUES")
        for issue in issues:
            print(f"- {issue}")

    if args.json_out:
        out_path = Path(args.json_out)
        if not out_path.is_absolute():
            out_path = (PROJECT_ROOT / out_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
        print(f"JSON_REPORT={out_path}")

    print(f"STATUS={'ok' if ok else 'fail'}")
    if args.strict and not ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
