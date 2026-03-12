"""
CRONUS Tool Registry

All tools available to the C→R→O→N→U→S pipeline.
Each tool goes through the Tribunal enforcement gate before execution.
"""

from cronus.app.tools.vbox import handle_vm_control
from cronus.app.tools.vm_exec import handle_vm_exec
from cronus.app.tools.local_fs import (
    handle_read_file,
    handle_write_file,
    handle_list_directory,
    handle_file_exists,
)
from cronus.app.tools.vision import handle_screenshot, handle_vision_analyze
from cronus.app.tools.desktop import (
    handle_list_windows,
    handle_focus_window,
    handle_desktop_input,
    handle_send_handoff,
)
from cronus.app.tools.shell import handle_shell_exec
from cronus.app.tools.search import handle_grep, handle_find_files

TOOL_HANDLERS = {
    # Filesystem (all totems)
    "read_file": handle_read_file,
    "write_file": handle_write_file,
    "list_directory": handle_list_directory,
    "file_exists": handle_file_exists,
    # Vision — Curiosity (C) & User (U)
    "screenshot": handle_screenshot,
    "vision_analyze": handle_vision_analyze,
    # Desktop control — User (U) / Routing (R)
    "list_windows": handle_list_windows,
    "focus_window": handle_focus_window,
    "desktop_input": handle_desktop_input,
    "send_handoff": handle_send_handoff,
    # Shell — Origin (O)
    "shell_exec": handle_shell_exec,
    # Search — Curiosity (C)
    "grep": handle_grep,
    "find_files": handle_find_files,
    # VM — all totems
    "vm_control": handle_vm_control,
    "vm_exec": handle_vm_exec,
}

# OpenAI function calling schemas (what the LLM sees)
TOOL_SCHEMAS = [
    # -- Filesystem --
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file to read"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to write the file"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List contents of a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the directory"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "file_exists",
            "description": "Check if a file or directory exists",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to check"}
                },
                "required": ["path"],
            },
        },
    },
    # -- Vision --
    {
        "type": "function",
        "function": {
            "name": "screenshot",
            "description": "Capture the screen (or a region) and return a base64 PNG image. Use this to see what is currently displayed on the monitor.",
            "parameters": {
                "type": "object",
                "properties": {
                    "monitor": {
                        "type": "integer",
                        "description": "Monitor index (0=all monitors, 1=primary). Default 0.",
                    },
                    "region": {
                        "type": "object",
                        "description": "Optional sub-region to capture",
                        "properties": {
                            "left": {"type": "integer"},
                            "top": {"type": "integer"},
                            "width": {"type": "integer"},
                            "height": {"type": "integer"},
                        },
                    },
                    "save_path": {
                        "type": "string",
                        "description": "Optional file path to save the PNG to disk",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "vision_analyze",
            "description": "Capture the screen and analyze it with a vision model (GPT-4o). Describe what you want to find or verify on screen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "What to look for or analyze on screen (e.g. 'Is the login page showing correctly?', 'What errors are visible?')",
                    },
                    "monitor": {
                        "type": "integer",
                        "description": "Monitor index (0=all, 1=primary). Default 0.",
                    },
                    "region": {
                        "type": "object",
                        "description": "Optional sub-region to capture",
                        "properties": {
                            "left": {"type": "integer"},
                            "top": {"type": "integer"},
                            "width": {"type": "integer"},
                            "height": {"type": "integer"},
                        },
                    },
                },
                "required": ["prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_windows",
            "description": "List visible desktop windows with title and bounds. Use this before desktop control so the council knows who is who.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title_contains": {
                        "type": "string",
                        "description": "Optional substring filter for window titles.",
                    },
                    "exact_title": {
                        "type": "string",
                        "description": "Optional exact title match.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "focus_window",
            "description": "Focus a desktop window by title so later mouse/keyboard input lands in the right place.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title_contains": {"type": "string"},
                    "exact_title": {"type": "string"},
                    "index": {
                        "type": "integer",
                        "description": "If multiple windows match, choose by zero-based index.",
                    },
                    "target_left": {
                        "type": "integer",
                        "description": "Optional expected left coordinate used to disambiguate duplicate titles.",
                    },
                    "target_top": {
                        "type": "integer",
                        "description": "Optional expected top coordinate used to disambiguate duplicate titles.",
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Report the chosen window without focusing it.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "desktop_input",
            "description": "Execute one desktop mouse or keyboard action. Requires confirm=true for real execution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "One of: move, click, double_click, right_click, type_text, press, hotkey, scroll",
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Must be true to execute the action. Otherwise this is a dry run.",
                    },
                    "focus_first": {
                        "type": "boolean",
                        "description": "Focus a matching window before sending input.",
                    },
                    "title_contains": {"type": "string"},
                    "exact_title": {"type": "string"},
                    "index": {"type": "integer"},
                    "target_left": {"type": "integer"},
                    "target_top": {"type": "integer"},
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                    "button": {"type": "string"},
                    "text": {"type": "string"},
                    "key": {"type": "string"},
                    "keys": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "presses": {"type": "integer"},
                    "amount": {"type": "integer"},
                    "interval": {"type": "number"},
                    "duration": {"type": "number"},
                    "pause_seconds": {"type": "number"},
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_handoff",
            "description": "Focus a desktop LLM window, click its prompt area, type a message, and optionally submit it. Requires confirm=true for real execution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title_contains": {"type": "string"},
                    "exact_title": {"type": "string"},
                    "index": {"type": "integer"},
                    "target_left": {"type": "integer"},
                    "target_top": {"type": "integer"},
                    "message": {"type": "string"},
                    "submit": {"type": "boolean"},
                    "confirm": {"type": "boolean"},
                    "input_offset_y": {"type": "integer"},
                    "input_ratio_x": {"type": "number"},
                    "input_x": {"type": "integer"},
                    "input_y": {"type": "integer"},
                    "input_band_min_offset_y": {"type": "integer"},
                    "input_band_max_offset_y": {"type": "integer"},
                    "input_padding_x": {"type": "integer"},
                    "focus_pause_seconds": {"type": "number"},
                    "focus_retries": {"type": "integer"},
                    "focus_delay_seconds": {"type": "number"},
                    "clear_input": {"type": "boolean"},
                    "clear_hotkey": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "clear_key": {"type": "string"},
                    "clear_key_presses": {"type": "integer"},
                    "clear_pause_seconds": {"type": "number"},
                    "text_entry_method": {"type": "string"},
                    "paste_threshold": {"type": "integer"},
                    "interval": {"type": "number"},
                },
                "required": ["message"],
            },
        },
    },
    # -- Shell --
    {
        "type": "function",
        "function": {
            "name": "shell_exec",
            "description": "Execute a shell command and return stdout/stderr. Use for builds, git, tests, and system commands.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute",
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Working directory (default: CRONUS_WORKSPACE)",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 60)",
                    },
                },
                "required": ["command"],
            },
        },
    },
    # -- Search --
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search file contents for a regex pattern. Returns matching lines with file paths and line numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regex pattern to search for",
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory or file to search in",
                    },
                    "glob": {
                        "type": "string",
                        "description": "File glob filter (e.g. '*.py', '*.ts'). Default '*'.",
                    },
                    "case_insensitive": {
                        "type": "boolean",
                        "description": "Case insensitive search. Default false.",
                    },
                },
                "required": ["pattern", "path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_files",
            "description": "Find files matching a glob pattern in a directory tree.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern (e.g. '**/*.py', '*.config.ts')",
                    },
                    "path": {
                        "type": "string",
                        "description": "Root directory to search from",
                    },
                },
                "required": ["pattern", "path"],
            },
        },
    },
]
