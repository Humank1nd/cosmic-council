"""
Materialize Dream Caesar core operational tables into the local DB.

This copies the normalized core tables from the legacy root database:
  D:/dream-caesar/cosmic_council.db

Into the local canonical database:
  D:/dream-caesar/data/dream_caesar.db

The local DB currently contains JSON-row `cc_*` tables plus read-through views
like `problems -> cc_problems`. This script replaces those views with the
normalized tables Dream Caesar expects at runtime.
"""

from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


SOURCE_DB = Path(r"D:\dream-caesar\cosmic_council.db")
TARGET_DB = Path(r"D:\dream-caesar\data\dream_caesar.db")
RECOVERY_DIR = Path(r"D:\dream-caesar\recovery")

CORE_TABLES = [
    "users",
    "problems",
    "cycles",
    "solutions",
    "workflow_sessions",
    "workflow_steps",
    "audit_logs",
]


def backup_databases() -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = RECOVERY_DIR / f"local_core_materialize_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE_DB, out_dir / SOURCE_DB.name)
    shutil.copy2(TARGET_DB, out_dir / TARGET_DB.name)
    return out_dir


def object_sql(conn: sqlite3.Connection, obj_type: str, name: str) -> str | None:
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type=? AND name=?",
        (obj_type, name),
    ).fetchone()
    return row[0] if row and row[0] else None


def object_type(conn: sqlite3.Connection, name: str) -> str | None:
    row = conn.execute(
        "SELECT type FROM sqlite_master WHERE name=?",
        (name,),
    ).fetchone()
    return row[0] if row else None


def index_definitions(conn: sqlite3.Connection, table: str) -> list[tuple[str, str]]:
    return conn.execute(
        """
        SELECT name, sql
        FROM sqlite_master
        WHERE type='index'
          AND tbl_name=?
          AND sql IS NOT NULL
        ORDER BY name
        """,
        (table,),
    ).fetchall()


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])


def main() -> int:
    if not SOURCE_DB.exists():
        print(f"FAIL: missing source DB: {SOURCE_DB}")
        return 2
    if not TARGET_DB.exists():
        print(f"FAIL: missing target DB: {TARGET_DB}")
        return 2

    backup_dir = backup_databases()
    print(f"BACKUP={backup_dir}")

    src = sqlite3.connect(str(SOURCE_DB))
    dst = sqlite3.connect(str(TARGET_DB))
    try:
        dst.execute("PRAGMA foreign_keys=OFF")
        dst.execute(f"ATTACH DATABASE '{SOURCE_DB.as_posix()}' AS legacy")
        for table in CORE_TABLES:
            src_sql = object_sql(src, "table", table)
            if not src_sql:
                print(f"SKIP: source table missing: {table}")
                continue

            existing_type = object_type(dst, table)
            if existing_type == "view":
                dst.execute(f'DROP VIEW "{table}"')
                print(f"DROP_VIEW={table}")
            elif existing_type == "table":
                dst.execute(f'DROP TABLE "{table}"')
                print(f"DROP_TABLE={table}")

            dst.execute(src_sql)
            dst.execute(f'INSERT INTO "{table}" SELECT * FROM legacy."{table}"')
            print(f"CREATE_TABLE={table}")
            print(f"ROW_COUNT={table}:{table_count(src, table)}")

            for index_name, index_sql in index_definitions(src, table):
                dst.execute(index_sql)
                print(f"CREATE_INDEX={index_name}")

        dst.commit()
        dst.execute("DETACH DATABASE legacy")
    finally:
        dst.close()
        src.close()

    print("STATUS=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
