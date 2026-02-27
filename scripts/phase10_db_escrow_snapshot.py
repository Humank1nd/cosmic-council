"""
Phase 10 database escrow snapshot.

Creates a timestamped recovery bundle containing:
- raw SQLite DB copy
- optional WAL/SHM sidecars
- schema SQL
- full data SQL dump
- table row counts + checksum manifest
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
from sqlite3 import dump as sqlite_dump
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = PROJECT_ROOT / "cosmic_council.db"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def sqlite_integrity(db_path: Path) -> str:
    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute("PRAGMA quick_check;").fetchone()
        return str(row[0]) if row else "unknown"
    finally:
        conn.close()


def table_counts(db_path: Path) -> list[tuple[str, int]]:
    conn = sqlite3.connect(str(db_path))
    try:
        table_rows = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()
        out: list[tuple[str, int]] = []
        for (name,) in table_rows:
            count = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            out.append((str(name), int(count)))
        return out
    finally:
        conn.close()


def export_schema(db_path: Path, out_file: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(
            """
            SELECT type, name, sql
            FROM sqlite_master
            WHERE sql IS NOT NULL
            ORDER BY type, name
            """
        ).fetchall()
    finally:
        conn.close()

    lines: list[str] = []
    for obj_type, name, sql in rows:
        lines.append(f"-- {obj_type} {name}\n")
        lines.append(f"{sql};\n\n")
    out_file.write_text("".join(lines), encoding="utf-8")


def _iterdump_best_effort(connection: sqlite3.Connection) -> list[str]:
    """
    Best-effort SQL dump for DBs with broken FK metadata.

    Python 3.13's sqlite3.iterdump() runs PRAGMA foreign_key_check first;
    malformed FK definitions can raise OperationalError before any output.
    This fallback skips the pre-check and emits the transaction anyway.
    """
    writeable_schema = False
    cu = connection.cursor()
    cu.row_factory = None

    lines: list[str] = []
    lines.append("PRAGMA foreign_keys=OFF;")
    lines.append("BEGIN TRANSACTION;")

    q_tables = """
        SELECT "name", "type", "sql"
        FROM "sqlite_master"
        WHERE "sql" NOT NULL AND "type" == 'table'
        ORDER BY "name"
    """
    schema_res = cu.execute(q_tables)
    sqlite_sequence: list[str] = []
    for table_name, _type, sql in schema_res.fetchall():
        if table_name == "sqlite_sequence":
            rows = cu.execute('SELECT * FROM "sqlite_sequence";')
            sqlite_sequence = ['DELETE FROM "sqlite_sequence"']
            sqlite_sequence += [
                f'INSERT INTO "sqlite_sequence" VALUES({sqlite_dump._quote_value(seq_name)},{seq_value})'
                for seq_name, seq_value in rows.fetchall()
            ]
            continue
        if table_name == "sqlite_stat1":
            lines.append('ANALYZE "sqlite_master";')
        elif table_name.startswith("sqlite_"):
            continue
        elif sql.startswith("CREATE VIRTUAL TABLE"):
            if not writeable_schema:
                writeable_schema = True
                lines.append("PRAGMA writable_schema=ON;")
            lines.append(
                "INSERT INTO sqlite_master(type,name,tbl_name,rootpage,sql)"
                f"VALUES('table',{sqlite_dump._quote_value(table_name)},{sqlite_dump._quote_value(table_name)},0,{sqlite_dump._quote_value(sql)});"
            )
        else:
            lines.append(f"{sql};")

        table_name_ident = sqlite_dump._quote_name(table_name)
        res = cu.execute(f"PRAGMA table_info({table_name_ident})")
        column_names = [str(table_info[1]) for table_info in res.fetchall()]
        q_rows = "SELECT 'INSERT INTO {0} VALUES('{1}')' FROM {0};".format(
            table_name_ident,
            "','".join(
                "||quote({0})||".format(sqlite_dump._quote_name(col))
                for col in column_names
            ),
        )
        query_res = cu.execute(q_rows)
        for row in query_res:
            lines.append(f"{row[0]};")

    q_other = """
        SELECT "name", "type", "sql"
        FROM "sqlite_master"
        WHERE "sql" NOT NULL AND "type" IN ('index', 'trigger', 'view')
    """
    schema_res = cu.execute(q_other)
    for _name, _type, sql in schema_res.fetchall():
        lines.append(f"{sql};")

    if writeable_schema:
        lines.append("PRAGMA writable_schema=OFF;")

    for row in sqlite_sequence:
        lines.append(f"{row};")
    lines.append("COMMIT;")
    return lines


def export_dump(db_path: Path, out_file: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    try:
        try:
            lines = list(conn.iterdump())
        except sqlite3.OperationalError as exc:
            if "foreign key mismatch" not in str(exc).lower():
                raise
            lines = _iterdump_best_effort(conn)
    finally:
        conn.close()
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 10 DB escrow snapshot")
    parser.add_argument("--db-path", default=str(DEFAULT_DB))
    parser.add_argument("--out-dir", default="recovery")
    parser.add_argument("--skip-dump", action="store_true", help="Skip full SQL data dump")
    args = parser.parse_args()

    db_path = Path(args.db_path)
    if not db_path.is_absolute():
        db_path = (PROJECT_ROOT / db_path).resolve()
    if not db_path.exists():
        print(f"ERROR=missing_db path={db_path}")
        print("STATUS=fail")
        return 1

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_root = Path(args.out_dir)
    if not out_root.is_absolute():
        out_root = (PROJECT_ROOT / out_root).resolve()
    bundle_dir = out_root / f"phase10_db_escrow_{stamp}"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    copied: list[Path] = []
    db_copy = bundle_dir / db_path.name
    shutil.copy2(db_path, db_copy)
    copied.append(db_copy)

    for suffix in ("-wal", "-shm", "-journal"):
        sidecar = Path(str(db_path) + suffix)
        if sidecar.exists():
            target = bundle_dir / sidecar.name
            shutil.copy2(sidecar, target)
            copied.append(target)

    schema_file = bundle_dir / f"{db_path.stem}.schema.sql"
    export_schema(db_copy, schema_file)
    copied.append(schema_file)

    dump_file: Path | None = None
    dump_error: str | None = None
    if not args.skip_dump:
        dump_file = bundle_dir / f"{db_path.stem}.dump.sql"
        try:
            export_dump(db_copy, dump_file)
            copied.append(dump_file)
        except Exception as exc:  # pragma: no cover
            dump_error = f"{type(exc).__name__}: {exc}"
            err_file = bundle_dir / "dump_error.txt"
            err_file.write_text(dump_error + "\n", encoding="utf-8")
            copied.append(err_file)
            dump_file = None

    counts = table_counts(db_copy)
    counts_file = bundle_dir / f"{db_path.stem}.table_counts.tsv"
    counts_file.write_text(
        "table\trows\n" + "\n".join(f"{name}\t{count}" for name, count in counts) + "\n",
        encoding="utf-8",
    )
    copied.append(counts_file)

    manifest: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_db": str(db_path),
        "integrity_quick_check": sqlite_integrity(db_copy),
        "bundle_dir": str(bundle_dir),
        "dump_error": dump_error,
        "files": [],
        "table_count_total": len(counts),
        "row_total": sum(c for _, c in counts),
    }
    for item in copied:
        manifest["files"].append(
            {
                "path": rel(item),
                "size_bytes": item.stat().st_size,
                "sha256": sha256(item),
            }
        )

    manifest_file = bundle_dir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"BUNDLE_DIR={bundle_dir}")
    print(f"SOURCE_DB={db_path}")
    print(f"INTEGRITY={manifest['integrity_quick_check']}")
    print(f"TABLES={manifest['table_count_total']}")
    print(f"ROWS={manifest['row_total']}")
    print(f"SCHEMA_FILE={schema_file}")
    if dump_file:
        print(f"DUMP_FILE={dump_file}")
    elif dump_error:
        print(f"DUMP_ERROR={dump_error}")
    print(f"MANIFEST={manifest_file}")
    print("STATUS=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
