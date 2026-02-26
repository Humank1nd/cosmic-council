"""
Phase 3 preflight guard:
1) Validate canonical DB integrity.
2) Validate presence of critical tables.
3) Create a timestamped recovery snapshot with checksums.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


CANONICAL_DB = Path(r"D:\dream-caesar\cosmic_council.db")
LEGACY_DB = Path(r"D:\dream-caesar\data\dream_caesar.db")
RECOVERY_ROOT = Path(r"D:\dream-caesar\recovery")

CRITICAL_TABLES = [
    "problems",
    "cycles",
    "audit_logs",
    "workflow_sessions",
    "workflow_steps",
    "dreamfs_dreams",
    "knowledge_documents",
    "cc_stage_results",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_integrity(path: Path) -> tuple[bool, str]:
    conn = sqlite3.connect(str(path))
    try:
        result = conn.execute("PRAGMA integrity_check").fetchone()[0]
        return result == "ok", str(result)
    finally:
        conn.close()


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (table,)
    ).fetchone()
    return row is not None


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])


def snapshot(paths: list[Path]) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = RECOVERY_ROOT / f"preflight_snapshot_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_lines = []
    for p in paths:
        if not p.exists():
            manifest_lines.append(f"MISSING\t{p}")
            continue
        dst = out_dir / p.name
        shutil.copy2(p, dst)
        manifest_lines.append(
            f"OK\t{p}\t{dst}\t{os.path.getsize(dst)}\t{sha256(dst)}"
        )
    (out_dir / "manifest.tsv").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    return out_dir


def main() -> int:
    if not CANONICAL_DB.exists():
        print(f"FAIL: Missing canonical DB: {CANONICAL_DB}")
        return 2

    ok, detail = check_integrity(CANONICAL_DB)
    print(f"INTEGRITY={detail}")
    if not ok:
        print("FAIL: integrity_check failed")
        return 1

    conn = sqlite3.connect(str(CANONICAL_DB))
    try:
        missing = [t for t in CRITICAL_TABLES if not table_exists(conn, t)]
        if missing:
            print("FAIL: missing critical tables")
            for t in missing:
                print(f"  - {t}")
            return 1

        print("CRITICAL_COUNTS")
        for t in CRITICAL_TABLES:
            print(f"{t}={table_count(conn, t)}")
    finally:
        conn.close()

    snapshot_paths = [CANONICAL_DB]
    if LEGACY_DB.exists():
        snapshot_paths.append(LEGACY_DB)
    out_dir = snapshot(snapshot_paths)
    print(f"SNAPSHOT={out_dir}")
    print("STATUS=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
