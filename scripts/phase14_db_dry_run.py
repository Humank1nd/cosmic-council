"""
Phase 14 DB dry-run contract check.

Runs database manager lifecycle operations against an isolated temporary
SQLite database and emits a JSON report for recovery gating.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

import sys

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from cosmic_council.database.unified_database_manager import UnifiedDatabaseManager


def _cleanup_sqlite_files(db_path: Path) -> None:
    for suffix in ("", "-journal", "-wal", "-shm"):
        candidate = Path(f"{db_path}{suffix}")
        try:
            candidate.unlink()
        except FileNotFoundError:
            pass
        except PermissionError:
            pass


async def _table_count(manager: UnifiedDatabaseManager) -> int:
    with manager.get_session() as session:
        result = session.execute(
            text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        )
        return int(result.scalar() or 0)


async def run_checks(database_url: str) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add_check(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    manager: UnifiedDatabaseManager | None = None
    try:
        manager = UnifiedDatabaseManager(database_url=database_url)
        add_check("manager_init", True, "initialized")
    except Exception as exc:
        add_check("manager_init", False, f"{type(exc).__name__}: {exc}")
        return {"checks": checks}

    try:
        await manager.create_tables()
        add_check("create_tables_first", True, "ok")
    except Exception as exc:
        add_check("create_tables_first", False, f"{type(exc).__name__}: {exc}")

    try:
        await manager.create_tables()
        add_check("create_tables_idempotent", True, "ok")
    except Exception as exc:
        add_check("create_tables_idempotent", False, f"{type(exc).__name__}: {exc}")

    try:
        health = await manager.health_check()
        healthy = bool(health.get("healthy", False) or health.get("status") == "healthy")
        add_check("health_check", healthy, json.dumps(health, sort_keys=True))
    except Exception as exc:
        add_check("health_check", False, f"{type(exc).__name__}: {exc}")

    try:
        table_count = await _table_count(manager)
        add_check("table_count_positive", table_count > 0, f"count={table_count}")
    except Exception as exc:
        add_check("table_count_positive", False, f"{type(exc).__name__}: {exc}")

    try:
        with manager.get_session() as session:
            scalar = session.execute(text("SELECT 1")).scalar()
            add_check("session_select_1", int(scalar or 0) == 1, f"value={scalar}")
    except Exception as exc:
        add_check("session_select_1", False, f"{type(exc).__name__}: {exc}")

    try:
        await manager.drop_tables()
        add_check("drop_tables", True, "ok")
    except Exception as exc:
        add_check("drop_tables", False, f"{type(exc).__name__}: {exc}")

    try:
        await manager.create_tables()
        add_check("create_after_drop", True, "ok")
    except Exception as exc:
        add_check("create_after_drop", False, f"{type(exc).__name__}: {exc}")

    try:
        await manager.close()
        add_check("close", True, "ok")
    except Exception as exc:
        add_check("close", False, f"{type(exc).__name__}: {exc}")

    return {"checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 14 DB dry-run checker")
    parser.add_argument(
        "--json-out",
        default="recovery/phase14_db_dry_run.json",
        help="Path for JSON report output",
    )
    parser.add_argument(
        "--db-url",
        default="",
        help="Optional explicit DB URL (defaults to a temp sqlite file)",
    )
    parser.add_argument(
        "--keep-db",
        action="store_true",
        help="Keep temp DB files after run",
    )
    args = parser.parse_args()

    temp_db_path: Path | None = None
    if args.db_url:
        database_url = args.db_url
    else:
        temp_db_path = (
            Path(tempfile.gettempdir())
            / f"cosmic_council_phase14_dry_run_{os.getpid()}.db"
        )
        _cleanup_sqlite_files(temp_db_path)
        database_url = f"sqlite+aiosqlite:///{temp_db_path}"

    result = asyncio.run(run_checks(database_url))
    checks = result["checks"]
    ok = [c for c in checks if c["ok"]]
    failed = [c for c in checks if not c["ok"]]

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "database_url": database_url,
        "temp_db_path": str(temp_db_path) if temp_db_path else None,
        "checks_ok": len(ok),
        "checks_failed": len(failed),
        "checks_total": len(checks),
        "checks": checks,
        "status": "ok" if not failed else "fail",
    }

    out_path = Path(args.json_out)
    if not out_path.is_absolute():
        out_path = (PROJECT_ROOT / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"PHASE14_DB_DRY_RUN_REPORT={out_path}")
    print(f"CHECKS_OK={len(ok)}/{len(checks)}")
    print(f"CHECKS_FAILED={len(failed)}")
    if failed:
        print("FAILED_CHECKS=" + ",".join(c["name"] for c in failed))
    print(f"STATUS={report['status']}")

    if temp_db_path and not args.keep_db:
        _cleanup_sqlite_files(temp_db_path)

    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
