"""VirtualBox host control helpers."""

from __future__ import annotations

import os
import subprocess
from typing import Any, Dict, List


def _resolve_vboxmanage() -> str:
    override = os.getenv("VBOXMANAGE_PATH")
    if override:
        return override
    if os.name == "nt":
        windows_path = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
        if os.path.exists(windows_path):
            return windows_path
    return "VBoxManage"


def _run_vboxmanage(args: List[str]) -> Dict[str, Any]:
    cmd = [_resolve_vboxmanage(), *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "exit_code": result.returncode,
        "command": " ".join(cmd),
    }


def _parse_vm_state(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("VMState="):
            return line.split("=", 1)[1].strip().strip('"')
    return "unknown"


def handle_vm_control(params: Dict[str, Any]) -> Dict[str, Any]:
    action = (params.get("action") or "").lower()
    vm_name = params.get("vm_name") or os.getenv("CRONUS_VM_NAME")
    if action in {"list_vms", "list_running"}:
        args = ["list", "runningvms" if action == "list_running" else "vms"]
        return _run_vboxmanage(args)

    if not vm_name:
        return {
            "error": "vm_name is required for this action.",
            "exit_code": 2,
        }

    if action == "status":
        result = _run_vboxmanage(["showvminfo", vm_name, "--machinereadable"])
        result["state"] = _parse_vm_state(result.get("stdout", ""))
        return result

    if action == "start":
        vm_type = params.get("type") or "headless"
        return _run_vboxmanage(["startvm", vm_name, "--type", str(vm_type)])

    if action == "stop":
        return _run_vboxmanage(["controlvm", vm_name, "acpipowerbutton"])

    if action == "poweroff":
        return _run_vboxmanage(["controlvm", vm_name, "poweroff"])

    if action == "savestate":
        return _run_vboxmanage(["controlvm", vm_name, "savestate"])

    if action == "snapshot_take":
        snapshot = params.get("snapshot_name") or "cronus-snapshot"
        return _run_vboxmanage(["snapshot", vm_name, "take", snapshot])

    if action == "snapshot_restore":
        snapshot = params.get("snapshot_name")
        if not snapshot:
            return {"error": "snapshot_name is required.", "exit_code": 2}
        return _run_vboxmanage(["snapshot", vm_name, "restore", snapshot])

    if action == "snapshot_delete":
        snapshot = params.get("snapshot_name")
        if not snapshot:
            return {"error": "snapshot_name is required.", "exit_code": 2}
        return _run_vboxmanage(["snapshot", vm_name, "delete", snapshot])

    if action == "snapshot_list":
        return _run_vboxmanage(["snapshot", vm_name, "list", "--machinereadable"])

    if action == "port_forward":
        rule_name = params.get("rule_name") or "cronus-ssh"
        protocol = (params.get("protocol") or "tcp").lower()
        host_ip = params.get("host_ip") or ""
        host_port = params.get("host_port")
        guest_ip = params.get("guest_ip") or ""
        guest_port = params.get("guest_port")
        if host_port is None or guest_port is None:
            return {"error": "host_port and guest_port are required.", "exit_code": 2}
        rule = f"{rule_name},{protocol},{host_ip},{host_port},{guest_ip},{guest_port}"
        return _run_vboxmanage(["modifyvm", vm_name, "--natpf1", rule])

    return {"error": f"Unknown action: {action}", "exit_code": 2}
