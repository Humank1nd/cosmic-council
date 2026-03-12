#!/usr/bin/env python3
"""
Autonomous Task Daemon for Spider-Qwen

Monitors a task queue and executes tasks 24/7 via the CRONUS execution engine.
Tasks can be submitted via:
  - JSON file queue (repo-local runtime path)
  - Telegram via OpenClaw
  - Direct API calls to CRONUS

Usage:
    python autonomous_daemon.py --watch
    python autonomous_daemon.py --submit "Build the login page component"
"""

import argparse
import asyncio
import json
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx

CRONUS_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = Path(os.getenv("CRONUS_RUNTIME_ROOT", CRONUS_ROOT / "runtime"))
TASK_QUEUE_PATH = Path(os.getenv("CRONUS_TASK_QUEUE", RUNTIME_ROOT / "task_queue.json"))
RESULTS_PATH = Path(os.getenv("CRONUS_TASK_RESULTS", RUNTIME_ROOT / "task_results.json"))
CRONUS_API_URL = os.getenv("CRONUS_API_URL", "http://localhost:8010")
POLL_INTERVAL = int(os.getenv("CRONUS_POLL_INTERVAL", "5"))  # seconds
MAX_CONCURRENT = int(os.getenv("CRONUS_MAX_CONCURRENT", "2"))


def load_queue() -> list:
    """Load the task queue from disk."""
    if not TASK_QUEUE_PATH.exists():
        return []
    try:
        with open(TASK_QUEUE_PATH, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def save_queue(queue: list):
    """Save the task queue to disk."""
    TASK_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TASK_QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2, default=str)


def load_results() -> list:
    """Load task results from disk."""
    if not RESULTS_PATH.exists():
        return []
    try:
        with open(RESULTS_PATH, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def save_results(results: list):
    """Save task results to disk."""
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(results[-100:], f, indent=2, default=str)  # Keep last 100


def submit_task(
    task: str,
    totem: str = "yellow",  # Yellow = Creative/Build agent
    priority: int = 3,
    context: Optional[str] = None,
) -> dict:
    """Submit a new task to the queue."""
    task_obj = {
        "id": str(uuid.uuid4())[:8],
        "task": task,
        "totem": totem,
        "priority": priority,
        "context": context,
        "status": "pending",
        "submitted_at": datetime.now().isoformat(),
        "submitted_by": "autonomous_daemon",
    }
    queue = load_queue()
    queue.append(task_obj)
    # Sort by priority (higher = more urgent)
    queue.sort(key=lambda x: (-x.get("priority", 1), x.get("submitted_at", "")))
    save_queue(queue)
    print(f"[QUEUE] Task {task_obj['id']} submitted: {task[:50]}...")
    return task_obj


async def execute_task(task_obj: dict) -> dict:
    """Execute a task via the CRONUS API."""
    task_id = task_obj.get("id", "unknown")
    print(f"[EXEC] Starting task {task_id}: {task_obj.get('task', '')[:50]}...")

    payload = {
        "task": task_obj.get("task"),
        "totem": task_obj.get("totem", "yellow"),
        "context": task_obj.get("context"),
        "priority": task_obj.get("priority", 1),
        "session_id": f"daemon-{task_id}",
    }

    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(f"{CRONUS_API_URL}/execute", json=payload)
            response.raise_for_status()
            result = response.json()

        elapsed = (time.time() - start_time) * 1000

        return {
            "task_id": task_id,
            "success": result.get("success", False),
            "result": result.get("result"),
            "agent_used": result.get("agent_used"),
            "totem": result.get("totem"),
            "execution_time_ms": elapsed,
            "steps_taken": result.get("steps_taken", []),
            "error": result.get("error"),
            "completed_at": datetime.now().isoformat(),
        }

    except httpx.HTTPError as e:
        return {
            "task_id": task_id,
            "success": False,
            "result": None,
            "error": f"HTTP error: {str(e)}",
            "execution_time_ms": (time.time() - start_time) * 1000,
            "completed_at": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "task_id": task_id,
            "success": False,
            "result": None,
            "error": f"Unexpected error: {str(e)}",
            "execution_time_ms": (time.time() - start_time) * 1000,
            "completed_at": datetime.now().isoformat(),
        }


async def process_queue():
    """Process pending tasks from the queue."""
    queue = load_queue()
    pending = [t for t in queue if t.get("status") == "pending"]

    if not pending:
        return

    # Take up to MAX_CONCURRENT tasks
    to_process = pending[:MAX_CONCURRENT]

    # Mark as running
    for task_obj in to_process:
        task_obj["status"] = "running"
        task_obj["started_at"] = datetime.now().isoformat()
    save_queue(queue)

    # Execute concurrently
    results = await asyncio.gather(*[execute_task(t) for t in to_process])

    # Update queue with results
    queue = load_queue()
    all_results = load_results()

    for task_obj, result in zip(to_process, results):
        for q_task in queue:
            if q_task.get("id") == task_obj.get("id"):
                q_task["status"] = "completed" if result.get("success") else "failed"
                q_task["result"] = result
                break
        all_results.append(result)

        status = "SUCCESS" if result.get("success") else "FAILED"
        print(f"[{status}] Task {task_obj.get('id')}: {result.get('result', result.get('error', ''))[:100]}")

    save_queue(queue)
    save_results(all_results)


async def daemon_loop():
    """Main daemon loop - runs forever."""
    print("=" * 60)
    print("AUTONOMOUS TASK DAEMON - Spider-Qwen 24/7 Worker")
    print("=" * 60)
    print(f"Queue file: {TASK_QUEUE_PATH}")
    print(f"Results file: {RESULTS_PATH}")
    print(f"CRONUS API: {CRONUS_API_URL}")
    print(f"Poll interval: {POLL_INTERVAL}s")
    print(f"Max concurrent: {MAX_CONCURRENT}")
    print("=" * 60)
    print("Watching for tasks... (Ctrl+C to stop)")
    print()

    # Check CRONUS health first
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{CRONUS_API_URL}/health")
            health = resp.json()
            print(f"[CRONUS] Status: {health.get('status')}")
            print(f"[CRONUS] Agents: {health.get('agents_available', [])}")
    except Exception as e:
        print(f"[WARNING] CRONUS not reachable: {e}")
        print(f"[WARNING] Start CRONUS with: python {CRONUS_ROOT / 'run_cronus.py'}")

    print()

    while True:
        try:
            await process_queue()
        except Exception as e:
            print(f"[ERROR] Queue processing failed: {e}")

        await asyncio.sleep(POLL_INTERVAL)


def show_status():
    """Show current queue status."""
    queue = load_queue()
    results = load_results()

    pending = [t for t in queue if t.get("status") == "pending"]
    running = [t for t in queue if t.get("status") == "running"]
    completed = [t for t in queue if t.get("status") == "completed"]
    failed = [t for t in queue if t.get("status") == "failed"]

    print("=" * 60)
    print("TASK QUEUE STATUS")
    print("=" * 60)
    print(f"Pending:   {len(pending)}")
    print(f"Running:   {len(running)}")
    print(f"Completed: {len(completed)}")
    print(f"Failed:    {len(failed)}")
    print(f"Total Results: {len(results)}")
    print("=" * 60)

    if pending:
        print("\nPending Tasks:")
        for t in pending[:5]:
            print(f"  [{t.get('id')}] P{t.get('priority', 1)} - {t.get('task', '')[:50]}...")

    if running:
        print("\nRunning Tasks:")
        for t in running:
            print(f"  [{t.get('id')}] Started: {t.get('started_at', 'unknown')}")


def main():
    parser = argparse.ArgumentParser(description="Autonomous Task Daemon for Spider-Qwen")
    parser.add_argument("--watch", action="store_true", help="Start the daemon to watch for tasks")
    parser.add_argument("--submit", type=str, help="Submit a new task")
    parser.add_argument("--totem", type=str, default="yellow", choices=["red", "orange", "yellow", "green", "blue", "purple"], help="Target totem/agent")
    parser.add_argument("--priority", type=int, default=3, help="Task priority (1-5, higher = more urgent)")
    parser.add_argument("--context", type=str, help="Additional context for the task")
    parser.add_argument("--status", action="store_true", help="Show queue status")
    parser.add_argument("--clear", action="store_true", help="Clear completed/failed tasks from queue")

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.clear:
        queue = load_queue()
        queue = [t for t in queue if t.get("status") in ("pending", "running")]
        save_queue(queue)
        print("Cleared completed/failed tasks from queue.")
        return

    if args.submit:
        submit_task(args.submit, args.totem, args.priority, args.context)
        return

    if args.watch:
        try:
            asyncio.run(daemon_loop())
        except KeyboardInterrupt:
            print("\n[DAEMON] Shutting down...")
            return

    parser.print_help()


if __name__ == "__main__":
    main()
