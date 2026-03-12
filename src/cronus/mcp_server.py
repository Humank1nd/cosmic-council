"""
CRONUS MCP Server - Bridges CRONUS HTTP API to MCP stdio protocol.

This wrapper allows Claude Code to call CRONUS tools directly via MCP.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional

import httpx

# CRONUS API base URL
CRONUS_API_URL = "http://127.0.0.1:8010"


async def call_cronus_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Call a CRONUS tool via HTTP API."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{CRONUS_API_URL}/tool",
            json={"tool_name": tool_name, "parameters": parameters}
        )
        return response.json()


async def call_cronus_execute(task: str, totem: Optional[str] = None, context: Optional[str] = None) -> Dict[str, Any]:
    """Execute a task via CRONUS agent."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        payload = {"task": task}
        if totem:
            payload["totem"] = totem
        if context:
            payload["context"] = context
        response = await client.post(f"{CRONUS_API_URL}/execute", json=payload)
        return response.json()


async def get_cronus_health() -> Dict[str, Any]:
    """Get CRONUS health status."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{CRONUS_API_URL}/health")
        return response.json()


# MCP Tool definitions
TOOLS = [
    {
        "name": "cronus_vm_control",
        "description": "Control VirtualBox VMs: start, stop, snapshot, status. Actions: list_vms, list_running, start, stop, poweroff, savestate, status, snapshot_take, snapshot_restore, snapshot_delete, snapshot_list",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "VM action: list_vms, list_running, start, stop, poweroff, savestate, status, snapshot_take, snapshot_restore, snapshot_delete, snapshot_list"
                },
                "vm_name": {
                    "type": "string",
                    "description": "Name of the VM (required for most actions)"
                },
                "snapshot_name": {
                    "type": "string",
                    "description": "Snapshot name (for snapshot operations)"
                },
                "type": {
                    "type": "string",
                    "description": "Start type: headless, gui, sdl (default: headless)"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "cronus_vm_exec",
        "description": "Execute commands inside a VirtualBox VM via SSH or guestcontrol. Supports auto-start, auto-stop, and snapshot restore.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command to execute inside the VM"
                },
                "vm_name": {
                    "type": "string",
                    "description": "VM name (uses CRONUS_VM_NAME env if not specified)"
                },
                "method": {
                    "type": "string",
                    "description": "Execution method: ssh (default) or guestcontrol"
                },
                "auto_start": {
                    "type": "boolean",
                    "description": "Auto-start VM if not running"
                },
                "auto_stop": {
                    "type": "boolean",
                    "description": "Auto-stop VM after command"
                },
                "auto_restore": {
                    "type": "boolean",
                    "description": "Restore snapshot before and after execution"
                },
                "snapshot_name": {
                    "type": "string",
                    "description": "Snapshot to restore (default: cronus-auto)"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "cronus_execute",
        "description": "Execute a task through CRONUS agent totems. Totems: red (research), orange (orchestration), yellow (building), green (scheduling), blue (communications), purple (reflection)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Task description to execute"
                },
                "totem": {
                    "type": "string",
                    "description": "Agent totem: red, orange, yellow, green, blue, purple"
                },
                "context": {
                    "type": "string",
                    "description": "Additional context for the task"
                }
            },
            "required": ["task"]
        }
    },
    {
        "name": "cronus_health",
        "description": "Check CRONUS API health and available agents",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Any:
    """Handle an MCP tool call."""
    try:
        if name == "cronus_vm_control":
            return await call_cronus_tool("vm_control", arguments)
        elif name == "cronus_vm_exec":
            return await call_cronus_tool("vm_exec", arguments)
        elif name == "cronus_execute":
            return await call_cronus_execute(
                task=arguments.get("task", ""),
                totem=arguments.get("totem"),
                context=arguments.get("context")
            )
        elif name == "cronus_health":
            return await get_cronus_health()
        else:
            return {"error": f"Unknown tool: {name}"}
    except httpx.ConnectError:
        local_entry = Path(__file__).resolve().parents[2] / "CRONUS" / "run_cronus.py"
        return {"error": f"CRONUS API not reachable. Start it with: python {local_entry}"}
    except Exception as e:
        return {"error": str(e)}


def write_response(response: Dict[str, Any]) -> None:
    """Write JSON-RPC response to stdout."""
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()


async def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle an MCP JSON-RPC request."""
    method = request.get("method", "")
    params = request.get("params", {})
    request_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "cronus",
                    "version": "1.0.0"
                }
            }
        }

    elif method == "notifications/initialized":
        # No response needed for notifications
        return None

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": TOOLS
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        result = await handle_tool_call(tool_name, arguments)

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        }

    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }


async def main():
    """Main MCP server loop - reads from stdin, writes to stdout."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            request = json.loads(line.strip())
            response = await handle_request(request)

            if response is not None:
                write_response(response)

        except json.JSONDecodeError as e:
            write_response({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {e}"
                }
            })
        except Exception as e:
            write_response({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {e}"
                }
            })


if __name__ == "__main__":
    asyncio.run(main())
