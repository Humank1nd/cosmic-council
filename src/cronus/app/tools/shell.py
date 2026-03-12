"""
CRONUS Shell Tool — Execute shell commands.

Used primarily by Origin (O) totem for:
- Running build commands (pnpm build, npm test)
- Git operations
- Code execution
- System inspection

Tribunal-enforced: every call goes through the enforcement gate.
"""

from __future__ import annotations

import asyncio
import os
import subprocess
from typing import Any, Dict


# Safety: max output size to prevent memory issues
MAX_OUTPUT_BYTES = 100_000
# Safety: default timeout
DEFAULT_TIMEOUT_S = 60


def handle_shell_exec(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a shell command and return stdout/stderr.

    Args (in arguments dict):
        command: str — the command to run
        cwd: optional str — working directory (default: CRONUS_WORKSPACE or D:/)
        timeout: optional int — seconds before kill (default: 60)
        shell: optional bool — use shell mode (default: True)
    """
    command = arguments.get("command")
    if not command:
        return {"error": "No command provided", "exit_code": 1}

    cwd = arguments.get("cwd") or os.getenv("CRONUS_WORKSPACE") or "D:/"
    timeout = arguments.get("timeout", DEFAULT_TIMEOUT_S)
    use_shell = arguments.get("shell", True)

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=use_shell,
            capture_output=True,
            timeout=timeout,
            text=True,
        )

        stdout = result.stdout[:MAX_OUTPUT_BYTES] if result.stdout else ""
        stderr = result.stderr[:MAX_OUTPUT_BYTES] if result.stderr else ""

        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "truncated": len(result.stdout or "") > MAX_OUTPUT_BYTES,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout}s",
            "exit_code": 124,
        }
    except FileNotFoundError as e:
        return {
            "success": False,
            "error": f"Command not found: {e}",
            "exit_code": 127,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "exit_code": 1,
        }
