"""
Phase 8 orphan source audit.

Non-destructive inventory for breadcrumb cleanup targets:
- frontend/think-tank/src
- *_new directories
- database_backup directories
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "think-tank" / "src"
ROOT_SRC = PROJECT_ROOT / "src"


@dataclass
class DirInventory:
    path: str
    file_count: int
    py_count: int


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def list_py_relative(base: Path) -> list[str]:
    if not base.exists() or not base.is_dir():
        return []
    return sorted(rel_path(base, p) for p in base.rglob("*.py") if p.is_file())


def rel_path(base: Path, path: Path) -> str:
    return str(path.relative_to(base)).replace("\\", "/")


def list_root_untracked() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"],
            cwd=str(PROJECT_ROOT),
            check=False,
            capture_output=True,
        )
    except Exception:
        return []

    if result.returncode != 0:
        return []
    raw = result.stdout.decode("utf-8", errors="replace")
    entries = [e for e in raw.split("\x00") if e]
    return sorted(entries)


def inventory_new_dirs() -> list[DirInventory]:
    out: list[DirInventory] = []
    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_dir():
            continue
        if ".git" in path.parts:
            continue
        name = path.name
        if not (name.endswith("_new") or name in {"tests_new", "docs_new"}):
            continue
        files = [p for p in path.rglob("*") if p.is_file() and ".git" not in p.parts]
        py_files = [p for p in files if p.suffix == ".py"]
        out.append(
            DirInventory(
                path=rel(path),
                file_count=len(files),
                py_count=len(py_files),
            )
        )
    return sorted(out, key=lambda d: d.path)


def inventory_database_backup_dirs() -> list[DirInventory]:
    out: list[DirInventory] = []
    for path in PROJECT_ROOT.rglob("database_backup"):
        if not path.is_dir():
            continue
        if ".git" in path.parts:
            continue
        files = [p for p in path.rglob("*") if p.is_file() and ".git" not in p.parts]
        py_files = [p for p in files if p.suffix == ".py"]
        out.append(
            DirInventory(
                path=rel(path),
                file_count=len(files),
                py_count=len(py_files),
            )
        )
    return sorted(out, key=lambda d: d.path)


def compare_src_mirror(max_diff_list: int) -> dict[str, Any]:
    src_files = list_py_relative(ROOT_SRC)
    mirror_files = list_py_relative(FRONTEND_SRC)
    src_set = set(src_files)
    mirror_set = set(mirror_files)

    common = sorted(src_set.intersection(mirror_set))
    unique_in_mirror = sorted(mirror_set - src_set)
    unique_in_src = sorted(src_set - mirror_set)

    same_count = 0
    diff_paths: list[str] = []
    for rel_file in common:
        src_hash = sha256(ROOT_SRC / rel_file)
        mirror_hash = sha256(FRONTEND_SRC / rel_file)
        if src_hash == mirror_hash:
            same_count += 1
        else:
            diff_paths.append(rel_file)

    return {
        "src_py_count": len(src_files),
        "mirror_py_count": len(mirror_files),
        "common_relative_paths": len(common),
        "same_content_count": same_count,
        "different_content_count": len(diff_paths),
        "different_content_paths": diff_paths[:max_diff_list],
        "different_content_paths_truncated": len(diff_paths) > max_diff_list,
        "unique_in_mirror_count": len(unique_in_mirror),
        "unique_in_mirror_paths": unique_in_mirror[:max_diff_list],
        "unique_in_mirror_paths_truncated": len(unique_in_mirror) > max_diff_list,
        "unique_in_src_count": len(unique_in_src),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 8 orphan source audit")
    parser.add_argument("--json-out", default="recovery/phase8_orphan_source_report.json")
    parser.add_argument("--max-diff-list", type=int, default=200)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero if orphan/drift indicators are present",
    )
    args = parser.parse_args()

    untracked = list_root_untracked()
    untracked_py = sorted(p for p in untracked if p.endswith(".py"))
    untracked_nonpy_count = len(untracked) - len(untracked_py)

    new_dirs = inventory_new_dirs()
    db_backup_dirs = inventory_database_backup_dirs()
    mirror = compare_src_mirror(max_diff_list=args.max_diff_list)

    top_level_untracked_py_counts: dict[str, int] = {}
    for path in untracked_py:
        top = path.split("/", 1)[0]
        top_level_untracked_py_counts[top] = top_level_untracked_py_counts.get(top, 0) + 1

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "summary": {
            "root_untracked_total": len(untracked),
            "root_untracked_py": len(untracked_py),
            "root_untracked_nonpy": untracked_nonpy_count,
            "frontend_src_exists": FRONTEND_SRC.exists(),
            "new_dirs_found": len(new_dirs),
            "new_dir_file_total": sum(d.file_count for d in new_dirs),
            "new_dir_py_total": sum(d.py_count for d in new_dirs),
            "database_backup_dirs_found": len(db_backup_dirs),
            "database_backup_file_total": sum(d.file_count for d in db_backup_dirs),
            "database_backup_py_total": sum(d.py_count for d in db_backup_dirs),
            "src_mirror_common": mirror["common_relative_paths"],
            "src_mirror_diff": mirror["different_content_count"],
            "src_mirror_unique_in_mirror": mirror["unique_in_mirror_count"],
        },
        "root_untracked_py_top_levels": dict(sorted(top_level_untracked_py_counts.items())),
        "root_untracked_py_paths": untracked_py,
        "new_dir_inventory": [asdict(d) for d in new_dirs],
        "database_backup_inventory": [asdict(d) for d in db_backup_dirs],
        "src_frontend_mirror": mirror,
    }

    out_path = Path(args.json_out)
    if not out_path.is_absolute():
        out_path = (PROJECT_ROOT / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary = report["summary"]
    print(f"PHASE8_REPORT={out_path}")
    print(f"ROOT_UNTRACKED_TOTAL={summary['root_untracked_total']}")
    print(f"ROOT_UNTRACKED_PY={summary['root_untracked_py']}")
    print(f"FRONTEND_THINK_TANK_SRC_EXISTS={1 if summary['frontend_src_exists'] else 0}")
    print(f"SRC_MIRROR_COMMON={summary['src_mirror_common']}")
    print(f"SRC_MIRROR_DIFF={summary['src_mirror_diff']}")
    print(f"SRC_MIRROR_UNIQUE_IN_MIRROR={summary['src_mirror_unique_in_mirror']}")
    print(f"NEW_DIRS_FOUND={summary['new_dirs_found']}")
    print(f"NEW_DIR_FILES={summary['new_dir_file_total']}")
    print(f"NEW_DIR_PY={summary['new_dir_py_total']}")
    print(f"DATABASE_BACKUP_DIRS={summary['database_backup_dirs_found']}")
    print(f"DATABASE_BACKUP_FILES={summary['database_backup_file_total']}")
    print(f"DATABASE_BACKUP_PY={summary['database_backup_py_total']}")

    has_orphan_signals = any(
        [
            summary["root_untracked_py"] > 0,
            summary["src_mirror_diff"] > 0,
            summary["src_mirror_unique_in_mirror"] > 0,
            summary["database_backup_dirs_found"] > 0,
        ]
    )
    failed = bool(args.strict and has_orphan_signals)
    print(f"STATUS={'fail' if failed else 'ok'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
