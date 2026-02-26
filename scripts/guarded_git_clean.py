"""
Safe wrapper around `git clean` to prevent accidental local data loss.

Examples:
  python scripts/guarded_git_clean.py -fd --yes
  python scripts/guarded_git_clean.py -fdx --yes --allow-protected
"""

from __future__ import annotations

import argparse
import fnmatch
import subprocess
import sys
from pathlib import Path


PROTECTED_PATTERNS = [
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "*.db-wal",
    "*.db-shm",
    "*.db-journal",
    "*.sqlite-wal",
    "*.sqlite-shm",
    "*.sqlite-journal",
    "recovery/*",
    "data/*",
]


def parse_paths(dry_run_output: str) -> list[str]:
    paths: list[str] = []
    for raw in dry_run_output.splitlines():
        line = raw.strip()
        prefix = "Would remove "
        if line.startswith(prefix):
            paths.append(line[len(prefix) :].strip())
    return paths


def is_protected(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(
        fnmatch.fnmatch(normalized, pat) or fnmatch.fnmatch(Path(normalized).name, pat)
        for pat in PROTECTED_PATTERNS
    )


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Guarded git clean")
    parser.add_argument(
        "clean_args",
        nargs="*",
        help="Arguments forwarded to git clean (example: -fd, -fdx)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Actually execute clean. Without this, script only previews.",
    )
    parser.add_argument(
        "--allow-protected",
        action="store_true",
        help="Allow removal of protected files/paths.",
    )
    args, unknown = parser.parse_known_args()

    forwarded = [*args.clean_args, *unknown] or ["-fd"]
    dry_cmd = ["git", "clean", "-n", *forwarded]
    dry = run(dry_cmd)
    if dry.returncode != 0:
        sys.stderr.write(dry.stderr or dry.stdout)
        return dry.returncode

    print("PREVIEW")
    print(dry.stdout.strip() or "(nothing to remove)")

    candidate_paths = parse_paths(dry.stdout)
    protected_hits = [p for p in candidate_paths if is_protected(p)]
    if protected_hits and not args.allow_protected:
        print("\nBLOCKED: protected paths detected")
        for p in protected_hits:
            print(f"  - {p}")
        print("Re-run with --allow-protected only if you are absolutely sure.")
        return 1

    if not args.yes:
        print("\nDRY RUN ONLY. Re-run with --yes to execute.")
        return 0

    real_cmd = ["git", "clean", *forwarded]
    real = run(real_cmd)
    if real.stdout:
        print(real.stdout.strip())
    if real.returncode != 0 and real.stderr:
        sys.stderr.write(real.stderr)
    return real.returncode


if __name__ == "__main__":
    raise SystemExit(main())
