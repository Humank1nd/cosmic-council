"""Local filesystem tools for Spider-Qwen."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

CRONUS_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_WORKSPACE = CRONUS_ROOT
DEFAULT_SCRATCH = CRONUS_ROOT / ".scratch"

# Allowed base paths for file operations (security boundary)
ALLOWED_PATHS = [
    Path(os.getenv("CRONUS_WORKSPACE", str(DEFAULT_WORKSPACE))),
    Path(os.getenv("CRONUS_SCRATCH", str(DEFAULT_SCRATCH))),
]


def _is_path_allowed(path: Path) -> bool:
    """Check if path is within allowed directories."""
    resolved = path.resolve()
    return any(
        resolved == allowed or allowed in resolved.parents
        for allowed in ALLOWED_PATHS
    )


def _normalize_path(path_str: str) -> Path:
    """Normalize and validate path."""
    path = Path(path_str).resolve()
    if not _is_path_allowed(path):
        raise PermissionError(f"Path not allowed: {path}")
    return path


def handle_read_file(params: Dict[str, Any]) -> Dict[str, Any]:
    """Read a file's contents."""
    file_path = params.get("path")
    if not file_path:
        return {"error": "path is required", "exit_code": 2}

    try:
        path = _normalize_path(file_path)
        if not path.exists():
            return {"error": f"File not found: {path}", "exit_code": 1}
        if not path.is_file():
            return {"error": f"Not a file: {path}", "exit_code": 1}

        # Limit file size
        max_size = int(os.getenv("CRONUS_MAX_FILE_SIZE", str(1024 * 1024)))  # 1MB default
        if path.stat().st_size > max_size:
            return {"error": f"File too large (max {max_size} bytes)", "exit_code": 1}

        content = path.read_text(encoding="utf-8", errors="replace")
        return {
            "content": content,
            "path": str(path),
            "size": len(content),
            "exit_code": 0,
        }
    except PermissionError as e:
        return {"error": str(e), "exit_code": 3}
    except Exception as e:
        return {"error": f"Read failed: {e}", "exit_code": 1}


def handle_write_file(params: Dict[str, Any]) -> Dict[str, Any]:
    """Write content to a file."""
    file_path = params.get("path")
    content = params.get("content")

    if not file_path:
        return {"error": "path is required", "exit_code": 2}
    if content is None:
        return {"error": "content is required", "exit_code": 2}

    try:
        path = _normalize_path(file_path)

        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content, encoding="utf-8")
        return {
            "message": f"Written {len(content)} bytes to {path}",
            "path": str(path),
            "size": len(content),
            "exit_code": 0,
        }
    except PermissionError as e:
        return {"error": str(e), "exit_code": 3}
    except Exception as e:
        return {"error": f"Write failed: {e}", "exit_code": 1}


def handle_list_directory(params: Dict[str, Any]) -> Dict[str, Any]:
    """List contents of a directory."""
    dir_path = params.get("path", ".")

    try:
        path = _normalize_path(dir_path)
        if not path.exists():
            return {"error": f"Directory not found: {path}", "exit_code": 1}
        if not path.is_dir():
            return {"error": f"Not a directory: {path}", "exit_code": 1}

        entries: List[Dict[str, Any]] = []
        for entry in sorted(path.iterdir()):
            try:
                stat = entry.stat()
                entries.append({
                    "name": entry.name,
                    "type": "dir" if entry.is_dir() else "file",
                    "size": stat.st_size if entry.is_file() else None,
                })
            except (OSError, PermissionError):
                entries.append({
                    "name": entry.name,
                    "type": "unknown",
                    "error": "access denied",
                })

        return {
            "path": str(path),
            "entries": entries,
            "count": len(entries),
            "exit_code": 0,
        }
    except PermissionError as e:
        return {"error": str(e), "exit_code": 3}
    except Exception as e:
        return {"error": f"List failed: {e}", "exit_code": 1}


def handle_file_exists(params: Dict[str, Any]) -> Dict[str, Any]:
    """Check if a file or directory exists."""
    file_path = params.get("path")
    if not file_path:
        return {"error": "path is required", "exit_code": 2}

    try:
        path = _normalize_path(file_path)
        exists = path.exists()
        return {
            "exists": exists,
            "is_file": path.is_file() if exists else False,
            "is_dir": path.is_dir() if exists else False,
            "path": str(path),
            "exit_code": 0,
        }
    except PermissionError as e:
        return {"error": str(e), "exit_code": 3}
    except Exception as e:
        return {"error": f"Check failed: {e}", "exit_code": 1}
