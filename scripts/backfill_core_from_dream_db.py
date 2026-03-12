"""
Backfill core API tables from the legacy JSON-row database into the
normalized operational database.

Source (legacy JSON rows):
  D:/dream-caesar/cosmic_council.db

Target (normalized ORM schema):
  D:/dream-caesar/data/dream_caesar.db
"""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


SOURCE_DB = Path(r"D:\dream-caesar\cosmic_council.db")
TARGET_DB = Path(r"D:\dream-caesar\data\dream_caesar.db")
RECOVERY_DIR = Path(r"D:\dream-caesar\recovery")


@dataclass
class Stats:
    seen: int = 0
    inserted: int = 0
    skipped: int = 0
    errors: int = 0


def to_uuid_hex(value: Any) -> Optional[str]:
    if value in (None, "", "anonymous"):
        return None
    try:
        return uuid.UUID(str(value)).hex
    except Exception:
        return None


def to_json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, default=str)


def backup_databases() -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = RECOVERY_DIR / f"db_unify_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE_DB, out_dir / SOURCE_DB.name)
    shutil.copy2(TARGET_DB, out_dir / TARGET_DB.name)
    return out_dir


def backfill_problems(src: sqlite3.Connection, dst: sqlite3.Connection) -> Stats:
    stats = Stats()
    rows = src.execute(
        "SELECT id, data, created_at, updated_at FROM problems ORDER BY created_at ASC"
    ).fetchall()
    for row_id, data_raw, created_at, updated_at in rows:
        stats.seen += 1
        try:
            payload = json.loads(data_raw or "{}")
            problem_id = to_uuid_hex(payload.get("id") or row_id)
            if not problem_id:
                stats.skipped += 1
                continue
            dst.execute(
                """
                INSERT OR IGNORE INTO problems
                (id, title, description, domain, complexity, status, priority,
                 created_by, created_at, updated_at, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    problem_id,
                    str(payload.get("title") or "Recovered Problem"),
                    str(payload.get("description") or ""),
                    str(payload.get("domain") or "general"),
                    str(payload.get("complexity") or "moderate"),
                    str(payload.get("status") or "active"),
                    str(payload.get("priority") or "medium"),
                    None,
                    created_at or datetime.utcnow().isoformat(),
                    updated_at or created_at or datetime.utcnow().isoformat(),
                    payload.get("due_date"),
                ),
            )
            if dst.total_changes > stats.inserted:
                stats.inserted += 1
            else:
                stats.skipped += 1
        except Exception:
            stats.errors += 1
    return stats


def backfill_cycles(src: sqlite3.Connection, dst: sqlite3.Connection) -> Stats:
    stats = Stats()
    rows = src.execute(
        "SELECT id, data, created_at, updated_at FROM cycles ORDER BY created_at ASC"
    ).fetchall()
    for row_id, data_raw, created_at, updated_at in rows:
        stats.seen += 1
        try:
            payload = json.loads(data_raw or "{}")
            cycle_id = to_uuid_hex(payload.get("id") or row_id)
            problem_id = to_uuid_hex(payload.get("problem_id"))
            if not cycle_id or not problem_id:
                stats.skipped += 1
                continue

            problem_exists = dst.execute(
                "SELECT 1 FROM problems WHERE id = ? LIMIT 1", (problem_id,)
            ).fetchone()
            if not problem_exists:
                stats.skipped += 1
                continue

            dst.execute(
                """
                INSERT OR IGNORE INTO cycles
                (id, problem_id, cycle_number, status, started_at, completed_at,
                 total_duration, overall_confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cycle_id,
                    problem_id,
                    int(payload.get("cycle_number") or 1),
                    str(payload.get("status") or "pending"),
                    payload.get("started_at") or created_at or datetime.utcnow().isoformat(),
                    payload.get("completed_at"),
                    float(payload.get("total_duration") or 0.0),
                    float(payload.get("overall_confidence") or 0.0),
                ),
            )
            if dst.total_changes > stats.inserted:
                stats.inserted += 1
            else:
                stats.skipped += 1
        except Exception:
            stats.errors += 1
    return stats


def backfill_audit_logs(src: sqlite3.Connection, dst: sqlite3.Connection) -> Stats:
    stats = Stats()
    rows = src.execute(
        "SELECT id, data, created_at, updated_at FROM audit_logs ORDER BY created_at ASC"
    ).fetchall()
    for row_id, data_raw, created_at, updated_at in rows:
        stats.seen += 1
        try:
            payload: Dict[str, Any] = json.loads(data_raw or "{}")
            log_id = to_uuid_hex(payload.get("id") or row_id)
            if not log_id:
                stats.skipped += 1
                continue

            raw_user = payload.get("user_id")
            raw_resource = payload.get("resource_id")
            user_uuid = to_uuid_hex(raw_user)
            resource_uuid = to_uuid_hex(raw_resource)

            details = payload.get("details") or {}
            if not isinstance(details, dict):
                details = {"details_raw": details}
            if raw_user and not user_uuid:
                details.setdefault("user_identifier", str(raw_user))
            if raw_resource and not resource_uuid:
                details.setdefault("resource_identifier", str(raw_resource))

            dst.execute(
                """
                INSERT OR IGNORE INTO audit_logs
                (id, user_id, action, resource_type, resource_id, details, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    log_id,
                    user_uuid,
                    str(payload.get("action") or "unknown"),
                    str(payload.get("resource_type") or "unknown"),
                    resource_uuid,
                    to_json_text(details),
                    created_at or updated_at or datetime.utcnow().isoformat(),
                ),
            )
            if dst.total_changes > stats.inserted:
                stats.inserted += 1
            else:
                stats.skipped += 1
        except Exception:
            stats.errors += 1
    return stats


def count_rows(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def main() -> int:
    if not SOURCE_DB.exists():
        print(f"ERROR: missing source DB: {SOURCE_DB}")
        return 2
    if not TARGET_DB.exists():
        print(f"ERROR: missing target DB: {TARGET_DB}")
        return 2

    backup_path = backup_databases()
    print(f"BACKUP: {backup_path}")

    src = sqlite3.connect(str(SOURCE_DB))
    dst = sqlite3.connect(str(TARGET_DB))

    try:
        dst.execute("PRAGMA foreign_keys = OFF")
        before = {
            "problems": count_rows(dst, "problems"),
            "cycles": count_rows(dst, "cycles"),
            "audit_logs": count_rows(dst, "audit_logs"),
        }

        p_stats = backfill_problems(src, dst)
        c_stats = backfill_cycles(src, dst)
        a_stats = backfill_audit_logs(src, dst)

        dst.commit()

        after = {
            "problems": count_rows(dst, "problems"),
            "cycles": count_rows(dst, "cycles"),
            "audit_logs": count_rows(dst, "audit_logs"),
        }

        print("SUMMARY")
        print(f"problems: seen={p_stats.seen} inserted={p_stats.inserted} skipped={p_stats.skipped} errors={p_stats.errors}")
        print(f"cycles: seen={c_stats.seen} inserted={c_stats.inserted} skipped={c_stats.skipped} errors={c_stats.errors}")
        print(f"audit_logs: seen={a_stats.seen} inserted={a_stats.inserted} skipped={a_stats.skipped} errors={a_stats.errors}")
        print("COUNTS_BEFORE", before)
        print("COUNTS_AFTER", after)
        return 0
    finally:
        src.close()
        dst.close()


if __name__ == "__main__":
    raise SystemExit(main())
