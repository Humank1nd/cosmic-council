"""Runtime adapter for LLM execution."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import httpx
from openai import AsyncOpenAI

from cronus.app.tools import TOOL_HANDLERS, TOOL_SCHEMAS

# Governance imports for enforcement gate (legacy external repo dependency)
if TYPE_CHECKING:
    # from app.genesis.cosmic_governance import LivingTribunal, BudgetToken
    LivingTribunal = Any
    BudgetToken = Any

# Global governance reference - set by boot sequence
_tribunal: Optional["LivingTribunal"] = None
_continuity_id: str = ""
_identity_hash: str = ""


def set_tribunal(tribunal: "LivingTribunal") -> None:
    """Set the global tribunal reference (called by boot sequence)."""
    global _tribunal
    _tribunal = tribunal


def set_continuity_context(continuity_id: str, identity_hash: str) -> None:
    """Set continuity context (called by boot sequence)."""
    global _continuity_id, _identity_hash
    _continuity_id = continuity_id
    _identity_hash = identity_hash


def get_tribunal() -> Optional["LivingTribunal"]:
    """Get the global tribunal reference."""
    return _tribunal


TOTEM_SYSTEM_PROMPTS = {
    "red": (
        "You are Curiosity (C), the Red Owl of CRONUS. "
        "You ask WHY. Research the problem deeply — gather facts, identify root causes, "
        "synthesize knowledge. Provide concise, factual analysis that the next agents can build on."
    ),
    "orange": (
        "You are Routing (R), the Orange Orangutan of CRONUS. "
        "You plan HOW. Take the research from Curiosity and create a clear execution strategy. "
        "Break the problem into actionable steps, delegate concerns, and orchestrate the path forward."
    ),
    "yellow": (
        "You are Origin (O), the Yellow Honeybee of CRONUS. "
        "You create WHAT. Take the plan from Routing and build the solution. "
        "Write code, design structures, produce artifacts. Be practical and precise."
    ),
    "green": (
        "You are Numbers (N), the Green Tortoise of CRONUS. "
        "You measure BALANCE. Evaluate the solution from Origin — check resource costs, timing, "
        "sustainability, trade-offs. Flag risks. Ensure nothing is over-engineered or under-resourced."
    ),
    "blue": (
        "You are User (U), the Blue Dolphin of CRONUS. "
        "You deliver OUTPUT. Take everything the council has produced and craft the final, "
        "user-facing response. Be clear, concise, and audience-aware. This is what the human sees."
    ),
    "purple": (
        "You are Support (S), the Purple Elephant of CRONUS. "
        "You provide REFLECTION. Evaluate the entire cycle — was the output adequate? "
        "What was missed? Should we run another cycle? Be honest, empathetic, and constructive."
    ),
}


def _get_config_value(config: Dict[str, Any], key: str, default: Optional[str]) -> Optional[str]:
    value = config.get(key)
    return value if isinstance(value, str) and value.strip() else default


def _get_llm_settings(config: Dict[str, Any]) -> Dict[str, Optional[str]]:
    # Check for provider override (groq, local, etc.)
    provider = os.getenv("CRONUS_LLM_PROVIDER", "local").lower()

    if provider == "groq":
        # Use Groq for fast inference
        groq_config = config.get("llm", {}).get("groq", {})
        return {
            "base_url": "https://api.groq.com/openai/v1",
            "model": os.getenv("CRONUS_GROQ_MODEL") or _get_config_value(groq_config, "model", "llama-3.3-70b-versatile"),
            "api_key": os.getenv("GROQ_API_KEY"),
            "provider": "groq",
        }

    # Default: local Ollama (DeepSeek-R1)
    llm_config = config.get("llm", {}) if isinstance(config.get("llm"), dict) else {}
    base_url = os.getenv("CRONUS_LLM_BASE_URL") or _get_config_value(llm_config, "base_url", None)
    model = os.getenv("CRONUS_LLM_MODEL") or _get_config_value(llm_config, "model", None)
    api_key = os.getenv("CRONUS_LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or "ollama"
    return {
        "base_url": base_url,
        "model": model,
        "api_key": api_key,
        "provider": "local",
    }


async def _run_http_runtime(
    base_url: str,
    task: str,
    totem: str,
    context: Optional[str],
    timeout: float,
) -> Dict[str, Any]:
    payload = {"task": task, "totem": totem, "context": context}
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(f"{base_url.rstrip('/')}/execute", json=payload)
        response.raise_for_status()
        data = response.json()
    return {
        "result": data.get("result") or data.get("response") or data,
        "provider": "runtime-http",
        "model": data.get("model"),
    }


def _execute_tool(
    name: str,
    arguments: Dict[str, Any],
    caller: str = "unknown",
    sandbox_mode: bool = False,
    budget_token: Optional["BudgetToken"] = None,
) -> Dict[str, Any]:
    """
    Execute a tool by name with given arguments.

    ENFORCEMENT GATE: This is where Tribunal verdicts become real.
    Every tool call is adjudicated BEFORE execution.
    """
    # ==========================================================================
    # TRIBUNAL ENFORCEMENT GATE (Section 1 of Enforcement Plan)
    # ==========================================================================
    if _tribunal is not None:
        verdict_result = _tribunal.check_verdict(
            tool_name=name,
            arguments=arguments,
            caller=caller,
            continuity_id=_continuity_id,
            identity_hash=_identity_hash,
            sandbox_mode=sandbox_mode,
            budget_token=budget_token,
        )

        if not verdict_result["allowed"]:
            # Tool execution BLOCKED by Tribunal
            return {
                "error": verdict_result["error"],
                "exit_code": verdict_result.get("exit_code", 403),
                "verdict": verdict_result["verdict"].name if verdict_result.get("verdict") else "BLOCKED",
                "case_id": verdict_result.get("case_id"),
                "tribunal_blocked": True,
            }

    # ==========================================================================
    # NORMAL EXECUTION (if Tribunal allows or not configured)
    # ==========================================================================
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return {"error": f"Unknown tool: {name}", "exit_code": 1}
    try:
        return handler(arguments)
    except Exception as e:
        return {"error": f"Tool execution failed: {e}", "exit_code": 1}


async def _run_openai_runtime(
    base_url: str,
    model: str,
    api_key: str,
    task: str,
    totem: str,
    context: Optional[str],
    use_tools: bool = True,
    max_tool_rounds: int = 10,
    sandbox_mode: bool = False,
) -> Dict[str, Any]:
    """
    Run OpenAI-compatible LLM with tool calling.

    Now includes:
    - Budget token tracking (Infinity I2/I3)
    - Tribunal verdict enforcement at tool execution
    """
    client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    system_prompt = TOTEM_SYSTEM_PROMPTS.get(totem, TOTEM_SYSTEM_PROMPTS["purple"])

    # Enhance system prompt with tool awareness
    if use_tools:
        system_prompt += "\n\nYou have access to file system tools. Use them to complete tasks that require reading, writing, or listing files."

    content = task if context is None else f"{task}\n\nContext:\n{context}"
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content},
    ]

    tool_calls_made: List[Dict[str, Any]] = []

    # ==========================================================================
    # BUDGET TOKEN CREATION (Infinity I2/I3)
    # ==========================================================================
    budget_token: Optional["BudgetToken"] = None
    runtime_id = f"openai_runtime_{uuid.uuid4().hex[:8]}"

    if _tribunal is not None:
        budget_token = _tribunal.create_budget_token(runtime_id)

    try:
        for round_num in range(max_tool_rounds):
            # Check budget time remaining
            if budget_token is not None:
                elapsed_ms = int((time.time() - budget_token.created_at) * 1000)
                if not budget_token.decrement_time(elapsed_ms - (budget_token.remaining_ms - budget_token.remaining_ms)):
                    # Time budget would be exceeded
                    pass  # Let check_verdict handle the actual enforcement

            # Make API call with or without tools
            if use_tools and TOOL_SCHEMAS:
                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto",
                )
            else:
                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                )

            message = response.choices[0].message

            # Check if model wants to call tools
            if not message.tool_calls:
                # No tool calls - return final response
                return {
                    "result": message.content or "",
                    "provider": "openai-compatible",
                    "model": model,
                    "tool_calls": tool_calls_made,
                    "rounds": round_num + 1,
                    "budget_remaining": budget_token.remaining_calls if budget_token else None,
                }

            # Process tool calls
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in message.tool_calls
                ],
            })

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                # ==========================================================
                # EXECUTE TOOL (with Tribunal enforcement gate)
                # ==========================================================
                tool_result = _execute_tool(
                    name=tool_name,
                    arguments=tool_args,
                    caller="openai_runtime",
                    sandbox_mode=sandbox_mode,
                    budget_token=budget_token,
                )

                tool_calls_made.append({
                    "tool": tool_name,
                    "args": tool_args,
                    "result": tool_result,
                    "tribunal_blocked": tool_result.get("tribunal_blocked", False),
                })

                # If Tribunal blocked, include that in the tool response
                if tool_result.get("tribunal_blocked"):
                    # Add a message indicating the tool was blocked
                    tool_result_content = json.dumps({
                        "error": tool_result.get("error"),
                        "blocked_by": "Tribunal",
                        "case_id": tool_result.get("case_id"),
                    })
                else:
                    tool_result_content = json.dumps(tool_result)

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result_content,
                })

        # Max rounds reached
        return {
            "result": "Max tool rounds reached without final response.",
            "provider": "openai-compatible",
            "model": model,
            "tool_calls": tool_calls_made,
            "rounds": max_tool_rounds,
            "warning": "incomplete",
            "budget_remaining": budget_token.remaining_calls if budget_token else None,
        }

    finally:
        # ==========================================================================
        # RELEASE BUDGET TOKEN
        # ==========================================================================
        if _tribunal is not None and budget_token is not None:
            _tribunal.release_budget_token(runtime_id)


def _build_cronus_prompt(task: str, totem: str, context: Optional[str]) -> str:
    prompt_parts = [f"Totem: {totem}", f"Task: {task}"]
    if context:
        prompt_parts.append(f"Context:\n{context}")
    return "\n".join(prompt_parts)


def _resolve_cronus_bridge_path() -> str:
    bridge_path = os.getenv("CRONUS_BRIDGE_PATH")
    if bridge_path:
        return bridge_path
    return str(Path(__file__).with_name("cronus_bridge.py"))


def _extract_json_payload(stdout_text: str) -> Optional[Dict[str, Any]]:
    if not stdout_text:
        return None
    try:
        return json.loads(stdout_text)
    except json.JSONDecodeError:
        for line in reversed(stdout_text.splitlines()):
            line = line.strip()
            if not line:
                continue
            if not (line.startswith("{") and line.endswith("}")):
                continue
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return None


async def _run_cronus_bridge(
    repo_path: str,
    task: str,
    totem: str,
    context: Optional[str],
    timeout: float,
) -> Dict[str, Any]:
    python_exe = os.getenv("CRONUS_PYTHON") or sys.executable
    prompt = _build_cronus_prompt(task, totem, context)
    bridge_path = _resolve_cronus_bridge_path()
    cmd = [python_exe, bridge_path, "--prompt", prompt]
    env = os.environ.copy()
    env["CRONUS_REPO_PATH"] = repo_path

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
    except FileNotFoundError as exc:
        return {
            "error": f"Cronus python executable not found: {exc}",
            "exit_code": 127,
        }

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        process.kill()
        return {
            "error": "Cronus bridge timed out.",
            "exit_code": 124,
        }

    stdout_text = (stdout or b"").decode("utf-8", errors="ignore").strip()
    stderr_text = (stderr or b"").decode("utf-8", errors="ignore").strip()
    payload = _extract_json_payload(stdout_text)
    if payload is None:
        return {
            "error": "Cronus bridge returned invalid JSON.",
            "result": stdout_text or stderr_text,
            "provider": "cronus-bridge",
            "model": None,
            "exit_code": process.returncode,
            "stderr": stderr_text,
        }
    return {
        "result": payload.get("result"),
        "provider": "cronus-bridge",
        "model": None,
        "error": payload.get("error"),
        "metadata": payload,
        "exit_code": process.returncode,
        "stderr": stderr_text,
    }


async def run_task(
    task: str,
    totem: str,
    context: Optional[str],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    steps = []
    started = time.time()

    cronus_repo = os.getenv("CRONUS_REPO_PATH")
    runtime_url = os.getenv("CRONUS_RUNTIME_URL")
    timeout_s = float(os.getenv("CRONUS_RUNTIME_TIMEOUT_S", "120"))

    if cronus_repo:
        steps.append("cronus_bridge")
        result = await _run_cronus_bridge(
            cronus_repo, task, totem, context, timeout_s
        )
        result["steps"] = steps
        result["elapsed_ms"] = (time.time() - started) * 1000
        return result

    if runtime_url:
        steps.append("runtime_http_call")
        result = await _run_http_runtime(runtime_url, task, totem, context, timeout_s)
        result["steps"] = steps
        result["elapsed_ms"] = (time.time() - started) * 1000
        return result

    llm_settings = _get_llm_settings(config)
    base_url = llm_settings.get("base_url")
    model = llm_settings.get("model")
    api_key = llm_settings.get("api_key") or "local"

    if not base_url or not model:
        return {
            "result": "LLM runtime is not configured. Set CRONUS_LLM_BASE_URL and CRONUS_LLM_MODEL.",
            "provider": "unconfigured",
            "model": model,
            "steps": ["runtime_unconfigured"],
            "elapsed_ms": (time.time() - started) * 1000,
        }

    steps.append("openai_chat_completion")
    result = await _run_openai_runtime(base_url, model, api_key, task, totem, context)
    result["steps"] = steps
    result["elapsed_ms"] = (time.time() - started) * 1000
    return result
