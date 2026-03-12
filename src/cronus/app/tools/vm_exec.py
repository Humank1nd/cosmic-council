"""Execute commands inside a VM using SSH or VirtualBox guestcontrol."""

from __future__ import annotations

import os
import subprocess
import time
from typing import Any, Dict, List, Tuple

from cronus.app.tools.vbox import _parse_vm_state, _resolve_vboxmanage, _run_vboxmanage


def _build_ssh_command(command: str) -> List[str]:
    host = os.getenv("CRONUS_VM_SSH_HOST", "127.0.0.1")
    port = os.getenv("CRONUS_VM_SSH_PORT", "2222")
    user = os.getenv("CRONUS_VM_SSH_USER")
    key_path = os.getenv("CRONUS_VM_SSH_KEY")

    if not user:
        raise ValueError("CRONUS_VM_SSH_USER is required for SSH execution.")

    null_device = "NUL" if os.name == "nt" else "/dev/null"
    cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        f"UserKnownHostsFile={null_device}",
        "-p",
        str(port),
    ]
    if key_path:
        cmd.extend(["-i", key_path])
    cmd.append(f"{user}@{host}")
    cmd.append(command)
    return cmd


def _build_guestcontrol_command(command: str, vm_name: str) -> List[str]:
    user = os.getenv("CRONUS_VM_GUEST_USER")
    password = os.getenv("CRONUS_VM_GUEST_PASS")
    if not user or not password:
        raise ValueError("CRONUS_VM_GUEST_USER and CRONUS_VM_GUEST_PASS are required.")

    shell = os.getenv("CRONUS_VM_GUEST_SHELL", "/bin/sh")
    shell_args = os.getenv("CRONUS_VM_GUEST_SHELL_ARGS", "-lc").split()
    cmd = [
        _resolve_vboxmanage(),
        "guestcontrol",
        vm_name,
        "run",
        "--username",
        user,
        "--password",
        password,
        "--exe",
        shell,
        "--",
        shell,
        *shell_args,
        command,
    ]
    return cmd


def _run_command(cmd: List[str]) -> Dict[str, Any]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "exit_code": result.returncode,
        "command": " ".join(cmd),
    }


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _param_or_env_flag(params: Dict[str, Any], key: str, env_name: str, default: bool) -> bool:
    if key in params:
        return bool(params[key])
    return _env_flag(env_name, default)


def _get_vm_state(vm_name: str) -> Tuple[str, Dict[str, Any]]:
    result = _run_vboxmanage(["showvminfo", vm_name, "--machinereadable"])
    state = _parse_vm_state(result.get("stdout", ""))
    return state, result


def _snapshot_exists(vm_name: str, snapshot_name: str) -> bool:
    result = _run_vboxmanage(["snapshot", vm_name, "list", "--machinereadable"])
    return f'SnapshotName="{snapshot_name}"' in result.get("stdout", "")


def _ensure_vm_powered_off(vm_name: str, stop_mode: str, actions: List[str]) -> None:
    state, _ = _get_vm_state(vm_name)
    if state != "running":
        return
    if stop_mode == "poweroff":
        _run_vboxmanage(["controlvm", vm_name, "poweroff"])
        actions.append("vm_poweroff")
    elif stop_mode == "savestate":
        _run_vboxmanage(["controlvm", vm_name, "savestate"])
        actions.append("vm_savestate")
    else:
        _run_vboxmanage(["controlvm", vm_name, "acpipowerbutton"])
        actions.append("vm_acpi_stop")


def _start_vm(vm_name: str, start_type: str, actions: List[str]) -> bool:
    state, _ = _get_vm_state(vm_name)
    if state == "running":
        return False
    _run_vboxmanage(["startvm", vm_name, "--type", start_type])
    actions.append("vm_start")
    return True


def _maybe_wait_for_boot(actions: List[str]) -> None:
    wait_s = float(os.getenv("CRONUS_VM_BOOT_WAIT_S", "10"))
    if wait_s > 0:
        actions.append(f"vm_boot_wait_{int(wait_s)}s")
        time.sleep(wait_s)


def _run_with_retries(cmd: List[str], retries: int, delay_s: float) -> Dict[str, Any]:
    last_result: Dict[str, Any] = {}
    for attempt in range(retries + 1):
        last_result = _run_command(cmd)
        if last_result.get("exit_code", 1) == 0:
            return last_result
        if attempt < retries:
            time.sleep(delay_s)
    return last_result


def handle_vm_exec(params: Dict[str, Any]) -> Dict[str, Any]:
    command = params.get("command")
    if not command:
        return {"error": "command is required.", "exit_code": 2}

    method = (params.get("method") or os.getenv("CRONUS_VM_EXEC_METHOD") or "ssh").lower()
    auto_start = _param_or_env_flag(params, "auto_start", "CRONUS_VM_AUTO_START", False)
    auto_stop = _param_or_env_flag(params, "auto_stop", "CRONUS_VM_AUTO_STOP", False)
    auto_snapshot = _param_or_env_flag(params, "auto_snapshot", "CRONUS_VM_AUTO_SNAPSHOT", False)
    auto_restore = _param_or_env_flag(params, "auto_restore", "CRONUS_VM_AUTO_RESTORE", False)
    actions: List[str] = []
    vm_name = params.get("vm_name") or os.getenv("CRONUS_VM_NAME")

    if (auto_start or auto_stop or auto_snapshot or auto_restore) and not vm_name:
        return {"error": "vm_name is required for auto start/stop/snapshot.", "exit_code": 2}

    snapshot_name = params.get("snapshot_name") or os.getenv("CRONUS_VM_SNAPSHOT_NAME", "cronus-auto")
    stop_mode = (params.get("stop_mode") or os.getenv("CRONUS_VM_AUTO_STOP_MODE") or "acpi").lower()
    start_type = params.get("start_type") or os.getenv("CRONUS_VM_START_TYPE", "headless")
    overwrite_snapshot = _param_or_env_flag(
        params, "snapshot_overwrite", "CRONUS_VM_SNAPSHOT_OVERWRITE", False
    )

    if method == "guestcontrol":
        if not vm_name:
            return {"error": "vm_name is required for guestcontrol.", "exit_code": 2}
        try:
            if auto_restore:
                if not _snapshot_exists(vm_name, snapshot_name):
                    return {"error": "snapshot not found for restore.", "exit_code": 2}
                _ensure_vm_powered_off(vm_name, stop_mode, actions)
                _run_vboxmanage(["snapshot", vm_name, "restore", snapshot_name])
                actions.append("snapshot_restore")

            started = False
            if auto_start:
                started = _start_vm(vm_name, start_type, actions)
            if started:
                _maybe_wait_for_boot(actions)

            if auto_snapshot:
                if _snapshot_exists(vm_name, snapshot_name):
                    if overwrite_snapshot:
                        _run_vboxmanage(["snapshot", vm_name, "delete", snapshot_name])
                        actions.append("snapshot_delete")
                    else:
                        actions.append("snapshot_exists")
                if not _snapshot_exists(vm_name, snapshot_name):
                    _run_vboxmanage(["snapshot", vm_name, "take", snapshot_name])
                    actions.append("snapshot_take")

            cmd = _build_guestcontrol_command(command, vm_name)
            retries = int(os.getenv("CRONUS_VM_GUESTCONTROL_RETRIES", "3"))
            delay_s = float(os.getenv("CRONUS_VM_GUESTCONTROL_RETRY_DELAY_S", "5"))
            result = _run_with_retries(cmd, retries, delay_s)
            result["method"] = "guestcontrol"
            if actions:
                result["vm_actions"] = actions

            if auto_restore:
                _ensure_vm_powered_off(vm_name, stop_mode, actions)
                _run_vboxmanage(["snapshot", vm_name, "restore", snapshot_name])
                actions.append("snapshot_restore_after")

            if auto_stop:
                _ensure_vm_powered_off(vm_name, stop_mode, actions)

            if actions:
                result["vm_actions"] = actions
            return result
        except ValueError as exc:
            return {"error": str(exc), "exit_code": 2}

    try:
        if auto_start and vm_name:
            started = _start_vm(vm_name, start_type, actions)
            if started:
                _maybe_wait_for_boot(actions)
        if auto_snapshot and vm_name:
            if _snapshot_exists(vm_name, snapshot_name):
                if overwrite_snapshot:
                    _run_vboxmanage(["snapshot", vm_name, "delete", snapshot_name])
                    actions.append("snapshot_delete")
                else:
                    actions.append("snapshot_exists")
            if not _snapshot_exists(vm_name, snapshot_name):
                _run_vboxmanage(["snapshot", vm_name, "take", snapshot_name])
                actions.append("snapshot_take")

        cmd = _build_ssh_command(command)
        result = _run_command(cmd)
        result["method"] = "ssh"
        if actions:
            result["vm_actions"] = actions

        if auto_restore and vm_name:
            _ensure_vm_powered_off(vm_name, stop_mode, actions)
            _run_vboxmanage(["snapshot", vm_name, "restore", snapshot_name])
            actions.append("snapshot_restore_after")

        if auto_stop and vm_name:
            _ensure_vm_powered_off(vm_name, stop_mode, actions)

        if actions:
            result["vm_actions"] = actions
        return result
    except ValueError as exc:
        return {"error": str(exc), "exit_code": 2}
