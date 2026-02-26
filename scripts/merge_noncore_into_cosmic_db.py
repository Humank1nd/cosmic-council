"""
Phase 2: Merge non-core tables into the operational DB.

Copies all tables that exist in:
  D:/dream-caesar/data/dream_caesar.db
but not in:
  D:/dream-caesar/cosmic_council.db

Also copies related indexes, triggers, and views.
Creates timestamped backups before making changes.
"""

from __future__ import annotations

import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Set, Tuple


SOURCE_DB = Path(r"D:\dream-caesar\data\dream_caesar.db")
TARGET_DB = Path(r"D:\dream-caesar\cosmic_council.db")
RECOVERY_DIR = Path(r"D:\dream-caesar\recovery")


@dataclass
class MergeStats:
    tables_created: int = 0
    tables_failed: int = 0
    table_rows_copied: int = 0
    data_copy_failures: int = 0
    indexes_created: int = 0
    index_failures: int = 0
    triggers_created: int = 0
    trigger_failures: int = 0
    views_created: int = 0
    view_failures: int = 0


def backup_databases() -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = RECOVERY_DIR / f"phase2_merge_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE_DB, out_dir / SOURCE_DB.name)
    shutil.copy2(TARGET_DB, out_dir / TARGET_DB.name)
    return out_dir


def fetch_table_names(conn: sqlite3.Connection, db_schema: str) -> Set[str]:
    rows = conn.execute(
        f"""
        SELECT name
        FROM {db_schema}.sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """
    ).fetchall()
    return {r[0] for r in rows}


def fetch_objects(
    conn: sqlite3.Connection, db_schema: str, obj_type: str, table_names: Set[str] | None = None
) -> List[Tuple[str, str, str]]:
    """
    Returns tuples: (name, tbl_name, sql)
    """
    base_sql = f"""
        SELECT name, tbl_name, sql
        FROM {db_schema}.sqlite_master
        WHERE type=?
          AND name NOT LIKE 'sqlite_%'
          AND sql IS NOT NULL
    """
    params: List[object] = [obj_type]
    if table_names is not None:
        placeholders = ",".join("?" for _ in table_names)
        base_sql += f" AND tbl_name IN ({placeholders})"
        params.extend(sorted(table_names))
    base_sql += " ORDER BY name"
    rows = conn.execute(base_sql, params).fetchall()
    return [(r[0], r[1], r[2]) for r in rows]


def qident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def count_rows(conn: sqlite3.Connection, schema: str, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {schema}.{qident(table)}").fetchone()[0])


def main() -> int:
    if not SOURCE_DB.exists():
        print(f"ERROR: Missing source DB: {SOURCE_DB}")
        return 2
    if not TARGET_DB.exists():
        print(f"ERROR: Missing target DB: {TARGET_DB}")
        return 2

    backup_dir = backup_databases()
    print(f"BACKUP={backup_dir}")

    conn = sqlite3.connect(str(TARGET_DB))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("ATTACH DATABASE ? AS srcdb", (str(SOURCE_DB),))

    stats = MergeStats()
    try:
        src_tables = fetch_table_names(conn, "srcdb")
        dst_tables = fetch_table_names(conn, "main")
        missing_tables = sorted(src_tables - dst_tables)
        print(f"MISSING_TABLES={len(missing_tables)}")

        # 1) Create missing tables.
        for table in missing_tables:
            row = conn.execute(
                "SELECT sql FROM srcdb.sqlite_master WHERE type='table' AND name=?",
                (table,),
            ).fetchone()
            create_sql = row[0] if row else None
            if not create_sql:
                # Some internal/shadow entries can lack SQL; skip safely.
                continue
            try:
                conn.execute(create_sql)
                stats.tables_created += 1
            except sqlite3.Error as exc:
                stats.tables_failed += 1
                print(f"TABLE_CREATE_FAIL\t{table}\t{exc}")

        # 2) Copy table data for all missing tables now present in target.
        created_or_available = sorted(
            t for t in missing_tables if t in fetch_table_names(conn, "main")
        )
        for table in created_or_available:
            try:
                before = count_rows(conn, "main", table)
                conn.execute(
                    f"INSERT INTO main.{qident(table)} SELECT * FROM srcdb.{qident(table)}"
                )
                after = count_rows(conn, "main", table)
                copied = max(0, after - before)
                stats.table_rows_copied += copied
            except sqlite3.Error as exc:
                stats.data_copy_failures += 1
                print(f"DATA_COPY_FAIL\t{table}\t{exc}")

        # 3) Create related indexes/triggers/views for migrated tables.
        migrated_set = set(created_or_available)

        for name, tbl_name, sql in fetch_objects(conn, "srcdb", "index", migrated_set):
            try:
                conn.execute(sql)
                stats.indexes_created += 1
            except sqlite3.Error as exc:
                stats.index_failures += 1
                print(f"INDEX_CREATE_FAIL\t{name}\t{exc}")

        for name, tbl_name, sql in fetch_objects(conn, "srcdb", "trigger", migrated_set):
            try:
                conn.execute(sql)
                stats.triggers_created += 1
            except sqlite3.Error as exc:
                stats.trigger_failures += 1
                print(f"TRIGGER_CREATE_FAIL\t{name}\t{exc}")

        # Views may not have tbl_name linkage; copy all source views that target lacks.
        src_views = fetch_objects(conn, "srcdb", "view", None)
        dst_view_names = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM main.sqlite_master WHERE type='view' AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
        }
        for name, _tbl, sql in src_views:
            if name in dst_view_names:
                continue
            try:
                conn.execute(sql)
                stats.views_created += 1
            except sqlite3.Error as exc:
                stats.view_failures += 1
                print(f"VIEW_CREATE_FAIL\t{name}\t{exc}")

        conn.commit()

        # 4) Verification summary.
        print("SUMMARY")
        print(f"tables_created={stats.tables_created}")
        print(f"tables_failed={stats.tables_failed}")
        print(f"table_rows_copied={stats.table_rows_copied}")
        print(f"data_copy_failures={stats.data_copy_failures}")
        print(f"indexes_created={stats.indexes_created}")
        print(f"index_failures={stats.index_failures}")
        print(f"triggers_created={stats.triggers_created}")
        print(f"trigger_failures={stats.trigger_failures}")
        print(f"views_created={stats.views_created}")
        print(f"view_failures={stats.view_failures}")

        # Show key-domain table counts after merge.
        key_prefixes = ["dreamfs_", "knowledge_", "cc_", "hive_", "standalone_"]
        dst_all_tables = sorted(fetch_table_names(conn, "main"))
        for prefix in key_prefixes:
            tables = [t for t in dst_all_tables if t.startswith(prefix)]
            print(f"{prefix}TABLES={len(tables)}")
            total_rows = 0
            for t in tables:
                try:
                    total_rows += count_rows(conn, "main", t)
                except sqlite3.Error:
                    pass
            print(f"{prefix}ROWS={total_rows}")

        return 0
    finally:
        try:
            conn.execute("DETACH DATABASE srcdb")
        except Exception:
            pass
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
