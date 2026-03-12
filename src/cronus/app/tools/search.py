"""
CRONUS Search Tool — Grep/search file contents and find files.

Used primarily by Curiosity (C) totem for:
- Searching codebases for patterns
- Finding files by name/glob
- Understanding project structure
"""

from __future__ import annotations

import fnmatch
import os
import re
from pathlib import Path
from typing import Any, Dict, List


# Safety limits
MAX_RESULTS = 100
MAX_LINE_LENGTH = 500
MAX_FILE_SIZE = 5_000_000  # 5MB


def handle_grep(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search file contents for a regex pattern.

    Args (in arguments dict):
        pattern: str — regex pattern to search for
        path: str — directory or file to search in
        glob: optional str — file glob filter (e.g. "*.py", "*.ts")
        case_insensitive: optional bool — default False
        max_results: optional int — default 100
    """
    pattern = arguments.get("pattern")
    search_path = arguments.get("path")
    if not pattern or not search_path:
        return {"error": "Both 'pattern' and 'path' are required"}

    file_glob = arguments.get("glob", "*")
    case_insensitive = arguments.get("case_insensitive", False)
    max_results = min(arguments.get("max_results", MAX_RESULTS), MAX_RESULTS)

    flags = re.IGNORECASE if case_insensitive else 0
    try:
        compiled = re.compile(pattern, flags)
    except re.error as e:
        return {"error": f"Invalid regex: {e}"}

    matches: List[Dict[str, Any]] = []
    search_root = Path(search_path)

    try:
        if search_root.is_file():
            files = [search_root]
        else:
            files = sorted(search_root.rglob(file_glob))

        for fpath in files:
            if len(matches) >= max_results:
                break
            if not fpath.is_file():
                continue
            if fpath.stat().st_size > MAX_FILE_SIZE:
                continue
            # Skip common non-text dirs
            parts = fpath.parts
            if any(p in (".git", "node_modules", ".venv", "__pycache__", ".next") for p in parts):
                continue

            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        if compiled.search(line):
                            matches.append({
                                "file": str(fpath),
                                "line": line_num,
                                "content": line.rstrip()[:MAX_LINE_LENGTH],
                            })
                            if len(matches) >= max_results:
                                break
            except (PermissionError, OSError):
                continue

        return {
            "success": True,
            "matches": matches,
            "count": len(matches),
            "truncated": len(matches) >= max_results,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_find_files(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Find files matching a glob pattern.

    Args (in arguments dict):
        pattern: str — glob pattern (e.g. "**/*.py", "*.config.ts")
        path: str — root directory to search from
        max_results: optional int — default 100
    """
    pattern = arguments.get("pattern")
    search_path = arguments.get("path")
    if not pattern or not search_path:
        return {"error": "Both 'pattern' and 'path' are required"}

    max_results = min(arguments.get("max_results", MAX_RESULTS), MAX_RESULTS)
    search_root = Path(search_path)

    try:
        files = []
        for fpath in sorted(search_root.rglob(pattern)):
            if not fpath.is_file():
                continue
            parts = fpath.parts
            if any(p in (".git", "node_modules", ".venv", "__pycache__", ".next") for p in parts):
                continue
            files.append(str(fpath))
            if len(files) >= max_results:
                break

        return {
            "success": True,
            "files": files,
            "count": len(files),
            "truncated": len(files) >= max_results,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
