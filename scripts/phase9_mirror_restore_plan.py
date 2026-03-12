"""
Phase 9 mirror restore plan generator.

Builds a non-destructive merge plan between:
- src/
- frontend/think-tank/src/
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
MIRROR_ROOT = PROJECT_ROOT / "frontend" / "think-tank" / "src"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def rel_path(base: Path, path: Path) -> str:
    return str(path.relative_to(base)).replace("\\", "/")


def list_py_relative(base: Path) -> list[str]:
    if not base.exists() or not base.is_dir():
        return []
    return sorted(rel_path(base, p) for p in base.rglob("*.py") if p.is_file())


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)


def write_patch_file(out_dir: Path, rel_file: str) -> str:
    src_file = SRC_ROOT / rel_file
    mirror_file = MIRROR_ROOT / rel_file
    diff = difflib.unified_diff(
        read_lines(src_file),
        read_lines(mirror_file),
        fromfile=f"a/src/{rel_file}",
        tofile=f"b/frontend/think-tank/src/{rel_file}",
        n=3,
    )

    patch_path = out_dir / (rel_file.replace("/", "__") + ".patch")
    patch_path.parent.mkdir(parents=True, exist_ok=True)
    patch_path.write_text("".join(diff), encoding="utf-8")
    return str(patch_path.relative_to(PROJECT_ROOT)).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 9 mirror restore plan")
    parser.add_argument("--json-out", default="recovery/phase9_mirror_restore_plan.json")
    parser.add_argument(
        "--emit-diffs-dir",
        help="Optional directory to write unified diff patch files for differing paths",
    )
    parser.add_argument("--max-list", type=int, default=200)
    parser.add_argument("--strict", action="store_true", help="Fail if mirror is missing")
    args = parser.parse_args()

    if not MIRROR_ROOT.exists():
        print(f"MIRROR_ROOT_MISSING={MIRROR_ROOT}")
        print("STATUS=fail" if args.strict else "STATUS=ok")
        return 1 if args.strict else 0

    src_files = list_py_relative(SRC_ROOT)
    mirror_files = list_py_relative(MIRROR_ROOT)
    src_set = set(src_files)
    mirror_set = set(mirror_files)

    common = sorted(src_set.intersection(mirror_set))
    unique_in_mirror = sorted(mirror_set - src_set)
    unique_in_src = sorted(src_set - mirror_set)

    same_count = 0
    diff_paths: list[str] = []
    for rel_file in common:
        if sha256(SRC_ROOT / rel_file) == sha256(MIRROR_ROOT / rel_file):
            same_count += 1
        else:
            diff_paths.append(rel_file)

    patch_index: list[str] = []
    if args.emit_diffs_dir:
        out_dir = Path(args.emit_diffs_dir)
        if not out_dir.is_absolute():
            out_dir = (PROJECT_ROOT / out_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        for rel_file in diff_paths:
            patch_index.append(write_patch_file(out_dir, rel_file))

    report: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "src_root": str(SRC_ROOT),
        "mirror_root": str(MIRROR_ROOT),
        "summary": {
            "src_py_count": len(src_files),
            "mirror_py_count": len(mirror_files),
            "common_relative_paths": len(common),
            "same_content_count": same_count,
            "different_content_count": len(diff_paths),
            "unique_in_mirror_count": len(unique_in_mirror),
            "unique_in_src_count": len(unique_in_src),
        },
        "restore_candidates": {
            "add_from_mirror": unique_in_mirror[: args.max_list],
            "merge_review_required": diff_paths[: args.max_list],
            "add_from_mirror_truncated": len(unique_in_mirror) > args.max_list,
            "merge_review_truncated": len(diff_paths) > args.max_list,
        },
        "optional_patch_index": patch_index[: args.max_list],
        "optional_patch_index_truncated": len(patch_index) > args.max_list,
    }

    out_path = Path(args.json_out)
    if not out_path.is_absolute():
        out_path = (PROJECT_ROOT / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary = report["summary"]
    print(f"PHASE9_REPORT={out_path}")
    print(f"SRC_PY={summary['src_py_count']}")
    print(f"MIRROR_PY={summary['mirror_py_count']}")
    print(f"COMMON={summary['common_relative_paths']}")
    print(f"SAME={summary['same_content_count']}")
    print(f"DIFF={summary['different_content_count']}")
    print(f"UNIQUE_IN_MIRROR={summary['unique_in_mirror_count']}")
    print(f"UNIQUE_IN_SRC={summary['unique_in_src_count']}")
    if args.emit_diffs_dir:
        print(f"PATCHES_WRITTEN={len(patch_index)}")
    print("STATUS=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
