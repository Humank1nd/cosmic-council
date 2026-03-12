"""Bridge script to run Cronus and emit a JSON response."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from typing import Any, Dict, Optional


def _build_prompt(task: str, totem: str, context: Optional[str]) -> str:
    prompt_parts = [f"Totem: {totem}", f"Task: {task}"]
    if context:
        prompt_parts.append(f"Context:\n{context}")
    return "\n".join(prompt_parts)


def _emit(payload: Dict[str, Any], exit_code: int) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=True))
    sys.exit(exit_code)


def _inherit_llm_env() -> None:
    if not os.getenv("CRONUS_LLM_API_KEY"):
        value = os.getenv("OPENAI_API_KEY")
        if value:
            os.environ["CRONUS_LLM_API_KEY"] = value


async def _run(prompt: str, repo_path: str) -> Dict[str, Any]:
    if not repo_path:
        return {"error": "CRONUS_REPO_PATH is not set."}

    _inherit_llm_env()
    sys.path.insert(0, repo_path)
    try:
        from app.agent.cronus import Cronus
    except Exception as exc:
        return {
            "error": (
                "Failed to import Cronus: "
                f"{exc.__class__.__name__}: {exc}"
            )
        }

    max_steps_env = os.getenv("CRONUS_MAX_STEPS", "1")
    try:
        max_steps = max(1, int(max_steps_env))
    except ValueError:
        max_steps = 1

    try:
        agent = await Cronus.create(max_steps=max_steps)
    except Exception as exc:
        return {
            "error": (
                "Failed to initialize Cronus: "
                f"{exc.__class__.__name__}: {exc}"
            )
        }

    try:
        await agent.run(prompt)
    except Exception as exc:
        return {
            "error": (
                "Cronus execution failed: "
                f"{exc.__class__.__name__}: {exc}"
            )
        }

    last_assistant = ""
    for message in reversed(agent.memory.messages):
        if getattr(message, "role", None) != "assistant":
            continue
        content = getattr(message, "content", None)
        if content:
            last_assistant = content
            break

    return {
        "result": last_assistant,
        "messages_total": len(agent.memory.messages),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Cronus and return the last assistant message as JSON."
    )
    parser.add_argument("--prompt", type=str, help="Full prompt to run")
    parser.add_argument("--task", type=str, help="Task text to build a prompt")
    parser.add_argument("--totem", type=str, default="purple")
    parser.add_argument("--context", type=str)
    args = parser.parse_args()

    prompt = args.prompt
    if not prompt:
        if not args.task:
            _emit({"error": "Provide --prompt or --task."}, 2)
        prompt = _build_prompt(args.task, args.totem, args.context)

    repo_path = os.getenv("CRONUS_REPO_PATH") or ""
    payload = asyncio.run(_run(prompt, repo_path))
    exit_code = 0 if not payload.get("error") else 1
    _emit(payload, exit_code)


if __name__ == "__main__":
    main()
