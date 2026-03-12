import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib import error, request


API_URL = os.environ.get("DREAM_CAESAR_API_URL", "http://127.0.0.1:8012/api/v1/agents/sequence")
OUTPUT_DIR = Path(
    os.environ.get(
        "JOKEBOOK_DREAM_CAESAR_OUTPUT_DIR",
        r"D:\dream-caesar\docs\runtime\integrations\jokebook\overnight",
    )
)
JOKEBOOK_REPO_PATH = os.environ.get(
    "JOKEBOOK_REPO_PATH",
    r"D:\dream-caesar\integrations\jokebook",
)
SUMMARY_PATH = OUTPUT_DIR / "LATEST_SUMMARY.md"


@dataclass(frozen=True)
class OvernightPrompt:
    slug: str
    title: str
    description: str
    stakeholders: list[str]
    success_criteria: list[str]
    key_routes: list[str]


PROMPTS = [
    OvernightPrompt(
        slug="dashboard-inbox",
        title="Jokebook dashboard and inbox",
        description=(
            "Review the logged-in launch path from dashboard to booking inbox. "
            "Focus on operator clarity, response urgency, and keeping comedians moving toward real bookings."
        ),
        stakeholders=["comedians", "operators"],
        success_criteria=["Clear dashboard next action", "Inbox remains operator center of gravity"],
        key_routes=["/dashboard", "/bookings"],
    ),
    OvernightPrompt(
        slug="booking-detail-response",
        title="Jokebook booking detail and response",
        description=(
            "Review the launch-critical booking detail and response flow. "
            "Focus on single-decision UX, clear status copy, and avoiding dead-end pages after a request is opened."
        ),
        stakeholders=["venues", "comedians", "operators"],
        success_criteria=["Booking detail stays operational", "Respond flow closes loop cleanly"],
        key_routes=["/bookings/[id]", "/bookings/[id]/respond"],
    ),
    OvernightPrompt(
        slug="payment-lane",
        title="Jokebook venue payment lane",
        description=(
            "Review the venue-side approval and payment closeout path. "
            "Focus on compensation clarity, Stripe handoff clarity, and returning the venue to booking status without confusion."
        ),
        stakeholders=["venues", "operators"],
        success_criteria=["Payment lane is explicit", "Venue returns to booking detail after payment starts"],
        key_routes=["/venues/dashboard/bookings/[id]/approve", "/bookings/[id]"],
    ),
    OvernightPrompt(
        slug="venue-browse-request",
        title="Jokebook venue browse and request",
        description=(
            "Review the browse-to-request flow from the venue side. "
            "Focus on comedian selection, request form momentum, and handoff from browse into the booking loop."
        ),
        stakeholders=["venues"],
        success_criteria=["Selected comedian context persists", "Venue request moves directly into booking loop"],
        key_routes=["/book", "/bookings/[id]"],
    ),
]


def _post_json(url: str, payload: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat()


def _build_payload(prompt: OvernightPrompt) -> dict[str, Any]:
    return {
        "problem": {
            "title": prompt.title,
            "description": prompt.description,
            "domain": "product engineering",
            "complexity": "simple",
            "stakeholders": prompt.stakeholders,
            "constraints": {
                "repo": JOKEBOOK_REPO_PATH,
                "scope": "web launch only",
                "mode": "overnight council pass",
            },
            "success_criteria": prompt.success_criteria,
            "context": {
                "repo_path": JOKEBOOK_REPO_PATH,
                "key_routes": prompt.key_routes,
                "launch_date": "2026-04-01",
            },
            "analysis_depth": "surface",
        },
        "agent_sequence": ["red_owl", "orange_orangutan"],
        "parallel": False,
        "synthesize": True,
    }


def _extract_summary(result: dict[str, Any]) -> dict[str, Any]:
    synthesis = result.get("synthesis") or {}
    insights = synthesis.get("insights_synthesis") or {}
    red = insights.get("red_owl_insights") or {}
    orange = insights.get("orange_orangutan_insights") or {}

    actions = []
    for action in orange.get("actions") or []:
        title = action.get("title")
        category = action.get("category")
        if title:
            actions.append(f"{title} [{category}]")

    return {
        "overall_confidence": result.get("overall_confidence"),
        "red_root_cause": red.get("root_cause"),
        "red_depth": red.get("depth_reached"),
        "orange_actions": actions,
        "orange_risk": orange.get("overall_risk"),
        "next_recommended_agent": result.get("next_recommended_agent"),
    }


def _write_summary(entries: list[dict[str, Any]]) -> None:
    lines = [
        "# Dream Caesar Overnight Jokebook Summary",
        "",
        f"Updated: {_iso_now()}",
        "",
        "This file is regenerated by `overnight_jokebook_loop.py`.",
        "",
    ]

    for entry in entries[-20:]:
        lines.extend(
            [
                f"## {entry['timestamp']} - {entry['slug']}",
                "",
                f"- Sequence ID: `{entry['sequence_id']}`",
                f"- Overall confidence: `{entry['summary'].get('overall_confidence')}`",
                f"- Red Owl depth: `{entry['summary'].get('red_depth')}`",
                f"- Red Owl root cause: `{entry['summary'].get('red_root_cause')}`",
                f"- Orange risk: `{entry['summary'].get('orange_risk')}`",
                f"- Next recommended agent: `{entry['summary'].get('next_recommended_agent')}`",
                "- Orange actions:",
            ]
        )
        actions = entry["summary"].get("orange_actions") or []
        if actions:
            for action in actions[:4]:
                lines.append(f"  - {action}")
        else:
            lines.append("  - none")
        lines.extend(
            [
                f"- Artifact: `{entry['artifact_path']}`",
                "",
            ]
        )

    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def _default_stop_time() -> datetime:
    now = datetime.now().astimezone()
    stop = now.replace(hour=8, minute=0, second=0, microsecond=0)
    if stop <= now:
        stop = stop + timedelta(days=1)
    return stop


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Dream Caesar overnight against Jokebook.")
    parser.add_argument("--sleep-seconds", type=int, default=900)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--cycles", type=int, default=0, help="0 means run until stop time.")
    parser.add_argument("--stop-at", type=str, default="", help="ISO timestamp with timezone.")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    history: list[dict[str, Any]] = []

    if args.stop_at:
        stop_at = datetime.fromisoformat(args.stop_at)
    else:
        stop_at = _default_stop_time()

    cycle = 0
    while True:
        cycle += 1
        cycle_started = _iso_now()
        for prompt in PROMPTS:
            payload = _build_payload(prompt)
            artifact_name = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{prompt.slug}.json"
            artifact_path = OUTPUT_DIR / artifact_name

            record: dict[str, Any] = {
                "timestamp": cycle_started,
                "cycle": cycle,
                "slug": prompt.slug,
                "payload": payload,
            }

            try:
                result = _post_json(API_URL, payload, timeout_seconds=args.timeout_seconds)
                record["result"] = result
                record["sequence_id"] = result.get("sequence_id")
                record["summary"] = _extract_summary(result)
                record["status"] = "ok"
            except error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                record["status"] = "http_error"
                record["error"] = {"code": exc.code, "body": body}
            except Exception as exc:  # noqa: BLE001
                record["status"] = "error"
                record["error"] = str(exc)

            artifact_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
            history.append(
                {
                    "timestamp": cycle_started,
                    "slug": prompt.slug,
                    "sequence_id": record.get("sequence_id", "n/a"),
                    "summary": record.get("summary", {}),
                    "artifact_path": str(artifact_path),
                }
            )
            _write_summary(history)
            print(f"[{cycle_started}] {prompt.slug}: {record['status']} -> {artifact_path}", flush=True)

        if args.cycles and cycle >= args.cycles:
            break

        now = datetime.now().astimezone()
        if now >= stop_at:
            print(f"Reached stop time {stop_at.isoformat()}", flush=True)
            break

        time.sleep(args.sleep_seconds)

    return 0


if __name__ == "__main__":
    sys.exit(main())
