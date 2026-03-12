#!/usr/bin/env python3
"""Cut over Dream Caesar database identity from cosmic_council to dream_caesar.

Supports:
- PostgreSQL in-cluster rename or clone via `psql`
- SQLite file copy
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse, urlunparse


DEFAULT_SOURCE_DB = "cosmic_council"
DEFAULT_TARGET_DB = "dream_caesar"
DEFAULT_TARGET_ROLE = "dream_caesar"
DEFAULT_TARGET_PASSWORD = "dream_caesar"


def _sql_ident(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _replace_db_name(url: str, db_name: str) -> str:
    parsed = urlparse(url)
    path = "/" + db_name
    return urlunparse(parsed._replace(path=path, params="", query="", fragment=""))


def _require_binary(name: str) -> None:
    if shutil.which(name):
        return
    raise SystemExit(f"Missing required binary: {name}")


def _run(cmd: list[str], env: dict[str, str] | None = None) -> None:
    subprocess.run(cmd, check=True, env=env)


def _run_psql(admin_url: str, sql: str) -> None:
    _run(["psql", admin_url, "-v", "ON_ERROR_STOP=1", "-c", sql])


def _postgres_database_exists(admin_url: str, db_name: str) -> bool:
    result = subprocess.run(
        [
            "psql",
            admin_url,
            "-t",
            "-A",
            "-c",
            f"SELECT 1 FROM pg_database WHERE datname = {_sql_literal(db_name)}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() == "1"


def _terminate_db_connections(admin_url: str, db_name: str) -> None:
    sql = f"""
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE datname = {_sql_literal(db_name)}
      AND pid <> pg_backend_pid();
    """
    _run_psql(admin_url, sql)


def _ensure_role(admin_url: str, role: str, password: str) -> None:
    sql = f"""
    DO $$
    BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = {_sql_literal(role)}) THEN
        EXECUTE 'CREATE ROLE {_sql_ident(role)} LOGIN PASSWORD ' || quote_literal({_sql_literal(password)});
      ELSE
        EXECUTE 'ALTER ROLE {_sql_ident(role)} WITH LOGIN PASSWORD ' || quote_literal({_sql_literal(password)});
      END IF;
    END
    $$;
    """
    _run_psql(admin_url, sql)


def _grant_database_access(target_db_url: str, db_name: str, role: str) -> None:
    sql = f"""
    ALTER DATABASE {_sql_ident(db_name)} OWNER TO {_sql_ident(role)};
    GRANT ALL PRIVILEGES ON DATABASE {_sql_ident(db_name)} TO {_sql_ident(role)};
    GRANT ALL PRIVILEGES ON SCHEMA public TO {_sql_ident(role)};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {_sql_ident(role)};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {_sql_ident(role)};
    GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO {_sql_ident(role)};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {_sql_ident(role)};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {_sql_ident(role)};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO {_sql_ident(role)};
    """
    _run(["psql", target_db_url, "-v", "ON_ERROR_STOP=1", "-c", sql])


def migrate_postgres(args: argparse.Namespace) -> None:
    _require_binary("psql")

    admin_url = args.admin_url
    target_db_url = _replace_db_name(admin_url, args.target_db)

    _ensure_role(admin_url, args.target_role, args.target_password)

    if args.mode == "rename":
        if not _postgres_database_exists(admin_url, args.source_db):
            raise SystemExit(f"Source database does not exist: {args.source_db}")
        if _postgres_database_exists(admin_url, args.target_db):
            raise SystemExit(f"Target database already exists: {args.target_db}")

        _terminate_db_connections(admin_url, args.source_db)
        _run_psql(
            admin_url,
            f"ALTER DATABASE {_sql_ident(args.source_db)} RENAME TO {_sql_ident(args.target_db)};",
        )
    else:
        if not _postgres_database_exists(admin_url, args.source_db):
            raise SystemExit(f"Source database does not exist: {args.source_db}")
        if _postgres_database_exists(admin_url, args.target_db):
            if not args.replace_target:
                raise SystemExit(
                    f"Target database already exists: {args.target_db}. Use --replace-target to recreate it."
                )
            _terminate_db_connections(admin_url, args.target_db)
            _run_psql(admin_url, f"DROP DATABASE {_sql_ident(args.target_db)};")

        _terminate_db_connections(admin_url, args.source_db)
        _run_psql(
            admin_url,
            (
                f"CREATE DATABASE {_sql_ident(args.target_db)} "
                f"WITH TEMPLATE {_sql_ident(args.source_db)} OWNER {_sql_ident(args.target_role)};"
            ),
        )

    _grant_database_access(target_db_url, args.target_db, args.target_role)


def migrate_sqlite(args: argparse.Namespace) -> None:
    source = Path(args.source_path)
    target = Path(args.target_path)
    if not source.exists():
        raise SystemExit(f"Source SQLite file does not exist: {source}")
    if target.exists() and not args.replace_target:
        raise SystemExit(f"Target SQLite file already exists: {target}. Use --replace-target to overwrite it.")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="backend", required=True)

    postgres = subparsers.add_parser("postgres", help="Rename or clone a PostgreSQL database")
    postgres.add_argument(
        "--admin-url",
        default=os.getenv(
            "POSTGRES_ADMIN_URL",
            "postgresql://postgres:postgres@localhost:5432/postgres",
        ),
        help="Admin connection URL pointed at a maintenance database such as postgres",
    )
    postgres.add_argument("--mode", choices=("rename", "clone"), default="rename")
    postgres.add_argument("--source-db", default=DEFAULT_SOURCE_DB)
    postgres.add_argument("--target-db", default=DEFAULT_TARGET_DB)
    postgres.add_argument("--target-role", default=DEFAULT_TARGET_ROLE)
    postgres.add_argument(
        "--target-password",
        default=os.getenv("DREAM_CAESAR_DB_PASSWORD", DEFAULT_TARGET_PASSWORD),
    )
    postgres.add_argument("--replace-target", action="store_true")
    postgres.set_defaults(func=migrate_postgres)

    sqlite = subparsers.add_parser("sqlite", help="Copy a SQLite database file")
    sqlite.add_argument("--source-path", default="./cosmic_council.db")
    sqlite.add_argument("--target-path", default="./dream_caesar.db")
    sqlite.add_argument("--replace-target", action="store_true")
    sqlite.set_defaults(func=migrate_sqlite)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    print("migration_complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
