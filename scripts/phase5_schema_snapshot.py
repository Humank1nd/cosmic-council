"""
Phase 5 schema snapshot exporter for SQLite databases (read-only).
"""

from __future__ import annotations

import argparse
import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DBS = [
    PROJECT_ROOT / "cosmic_council.db",
    PROJECT_ROOT / "perpetual_thinking.db",
    PROJECT_ROOT / "data" / "dream_caesar.db",
    PROJECT_ROOT / "data" / "strategy_store.db",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ro_conn(path: Path) -> sqlite3.Connection:
    uri = f"file:{path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def safe_table_count(conn: sqlite3.Connection, table_name: str) -> int:
    escaped = table_name.replace('"', '""')
    return int(conn.execute(f'SELECT COUNT(*) FROM "{escaped}"').fetchone()[0])


def export_schema(db_path: Path, out_dir: Path) -> tuple[Path, Path, int]:
    schema_out = out_dir / f"{db_path.stem}.schema.sql"
    counts_out = out_dir / f"{db_path.stem}.table_counts.tsv"

    with ro_conn(db_path) as conn:
        objects = conn.execute(
            "SELECT type, name, tbl_name, sql FROM sqlite_master "
            "WHERE sql IS NOT NULL AND type IN ('table','index','trigger','view') "
            "ORDER BY CASE type "
            "WHEN 'table' THEN 0 "
            "WHEN 'index' THEN 1 "
            "WHEN 'trigger' THEN 2 "
            "ELSE 3 END, name"
        ).fetchall()

        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                "ORDER BY name"
            ).fetchall()
        ]

        schema_lines = [
            f"-- Source: {db_path}",
            f"-- Exported UTC: {datetime.now(timezone.utc).isoformat()}",
            "",
        ]
        for obj_type, name, tbl_name, sql in objects:
            statement = sql.strip()
            if statement and not statement.endswith(";"):
                statement += ";"
            schema_lines.append(f"-- {obj_type.upper()}: {name} (table: {tbl_name})")
            schema_lines.append(statement)
            schema_lines.append("")
        schema_out.write_text("\n".join(schema_lines), encoding="utf-8")

        count_lines = ["table\tcount"]
        for table_name in tables:
            count_lines.append(f"{table_name}\t{safe_table_count(conn, table_name)}")
        counts_out.write_text("\n".join(count_lines) + "\n", encoding="utf-8")

    return schema_out, counts_out, len(tables)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export read-only SQLite schema snapshots")
    parser.add_argument(
        "--db",
        action="append",
        help="Relative or absolute DB path (repeatable). Defaults to canonical DB set.",
    )
    parser.add_argument(
        "--output-root",
        default="recovery",
        help="Root directory for snapshot output (default: recovery)",
    )
    parser.add_argument(
        "--include-empty",
        action="store_true",
        help="Attempt export for zero-byte DB files",
    )
    args = parser.parse_args()

    output_root = Path(args.output_root)
    if not output_root.is_absolute():
        output_root = (PROJECT_ROOT / output_root).resolve()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = output_root / f"phase5_schema_snapshot_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    db_paths = []
    if args.db:
        for raw in args.db:
            path = Path(raw)
            if not path.is_absolute():
                path = (PROJECT_ROOT / path).resolve()
            db_paths.append(path)
    else:
        db_paths = [p.resolve() for p in DEFAULT_DBS]

    manifest_lines = ["status\tdb_path\tsize_bytes\tdb_sha256\tschema_file\tcounts_file\ttable_count\terror"]
    exported = 0
    errors = 0
    skipped = 0

    for db_path in db_paths:
        if not db_path.exists():
            manifest_lines.append(f"MISSING\t{db_path}\t\t\t\t\t\t")
            continue

        size_bytes = db_path.stat().st_size
        if size_bytes == 0 and not args.include_empty:
            skipped += 1
            manifest_lines.append(f"SKIPPED_EMPTY\t{db_path}\t0\t\t\t\t\t")
            continue

        try:
            schema_file, counts_file, table_count = export_schema(db_path, out_dir)
            db_hash = sha256(db_path)
            exported += 1
            manifest_lines.append(
                "OK\t"
                f"{db_path}\t{size_bytes}\t{db_hash}\t"
                f"{schema_file.name}\t{counts_file.name}\t{table_count}\t"
            )
        except Exception as exc:  # pragma: no cover
            errors += 1
            manifest_lines.append(
                f"ERROR\t{db_path}\t{size_bytes}\t\t\t\t\t{type(exc).__name__}: {exc}"
            )

    manifest_path = out_dir / "manifest.tsv"
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    print(f"SCHEMA_SNAPSHOT={out_dir}")
    print(f"EXPORTED={exported}")
    print(f"SKIPPED={skipped}")
    print(f"ERRORS={errors}")
    print(f"MANIFEST={manifest_path}")

    if errors > 0 or exported == 0:
        print("STATUS=fail")
        return 1
    print("STATUS=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
