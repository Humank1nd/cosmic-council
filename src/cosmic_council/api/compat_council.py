"""Compatibility council facade over the live Dream Caesar runtime."""

from __future__ import annotations

import asyncio
import json
import os
import pathlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from types import SimpleNamespace

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from cronus.app.council.canon_adapter import (
    WORKFLOW_STEP_BY_SEAT,
    canonical_validation_stage_for_seat,
    canonical_success_outcome_for_seat,
    full_totem_profile_table,
    get_full_totem_profile,
    outer_seats,
    required_outputs_for_seat,
    resolve_decision_tree_transition,
)
from ..integrations.council_transition_models import (
    validate_blue_payload,
    validate_green_payload,
    validate_orange_payload,
    validate_yellow_payload,
)
from ..integrations.project_implementation_hub import db_path as projects_hub_db_path
from ..integrations.think_tank_runtime import (
    ThinkTankRuntime,
)
from ..integrations.twin_earth_bridge import export_twin_earth_proposal
from ..integrations.distillation_seed_writer import write_seed_async as _write_distillation_seed
from ..core.models import Cycle, Problem, WorkflowSession, WorkflowStep
from ..database.unified_database_manager import UnifiedDatabaseManager

_PROJECTS_HUB_DB_PATH = projects_hub_db_path()
_RUNTIME_ROOT = _PROJECTS_HUB_DB_PATH.parent.parent
_DESKTOP_COUNCIL_ROOT = _RUNTIME_ROOT / "desktop-council"
os.environ.setdefault("DREAM_CAESAR_RUNTIME_ROOT", str(_RUNTIME_ROOT))
os.environ.setdefault("DREAM_CAESAR_DESKTOP_COUNCIL_ROOT", str(_DESKTOP_COUNCIL_ROOT))
os.environ.setdefault("DREAM_CAESAR_ARTIFACTS", str(_DESKTOP_COUNCIL_ROOT / "artifacts"))
os.environ.setdefault("DREAM_CAESAR_ARTIFACT_ROOT", str(_DESKTOP_COUNCIL_ROOT / "artifacts"))
os.environ.setdefault("DREAM_CAESAR_HANDOFF_DIR", str(_DESKTOP_COUNCIL_ROOT / "handoffs"))
os.environ.setdefault("DREAM_CAESAR_HANDOFF_ROOT", str(_DESKTOP_COUNCIL_ROOT / "handoffs"))
os.environ.setdefault("DREAM_CAESAR_MAIL_ROOT", str(_DESKTOP_COUNCIL_ROOT / "mail"))
os.environ.setdefault("DREAM_CAESAR_ACTIVE_CANON_PATH", str(_DESKTOP_COUNCIL_ROOT / "active-canon.json"))
os.environ.setdefault("DREAM_CAESAR_DB_DIR", str(_RUNTIME_ROOT / "data"))
os.environ.setdefault("DREAM_CAESAR_DB_PATH", str(_PROJECTS_HUB_DB_PATH))

import sys as _sys
_SCRIPTS_DIR = str(
    __import__("pathlib").Path(__file__).resolve().parents[3] / "scripts"
)
if _SCRIPTS_DIR not in _sys.path:
    _sys.path.insert(0, _SCRIPTS_DIR)

try:
    from desktop_runtime import (
        bind_active_problem,
        record_cycle_iteration_artifact,
        record_workflow_step_artifact,
        resolve_fractal_address,
    )
    _DESKTOP_RUNTIME_AVAILABLE = True
except Exception as _drt_exc:
    import logging as _logging
    _logging.getLogger(__name__).warning(
        "desktop_runtime not available (%s); active-canon binding disabled.", _drt_exc
    )
    _DESKTOP_RUNTIME_AVAILABLE = False

    def bind_active_problem(*_a, **_kw) -> dict:  # type: ignore[misc]
        return {}

    def record_cycle_iteration_artifact(*_a, **_kw) -> dict:  # type: ignore[misc]
        return {}

    def record_workflow_step_artifact(*_a, **_kw) -> dict:  # type: ignore[misc]
        return {}

    def resolve_fractal_address(address: str = "", **_kw) -> dict:  # type: ignore[misc]
        return {"address": address or "unbound"}


router = APIRouter(prefix="/api/v1/compat/council", tags=["compat-council"])
_COMPAT_DB_MANAGER: UnifiedDatabaseManager | None = None

_SEAT_GATE_ERROR = {
    "red": "RedSentryGateFailure",
    "orange": "OrangeSentryGateFailure",
    "yellow": "YellowSentryGateFailure",
    "green": "GreenSentryGateFailure",
    "blue": "BlueSentryGateFailure",
    "purple": "PurpleSentryGateFailure",
}

_SEAT_GATE_MESSAGE = {
    "red": "Red completion did not pass the outer sentry gate.",
    "orange": "Orange completion did not pass the outer sentry gate.",
    "yellow": "Yellow completion did not pass the outer sentry gate.",
    "green": "Green completion did not pass the outer sentry gate.",
    "blue": "Blue completion did not pass the outer sentry gate.",
    "purple": "Purple completion did not pass the outer sentry gate.",
}

_SEAT_COMPLETION_NOTE = {
    "red": "Red inquiry completed via compat bootstrap handoff.",
    "orange": "Orange planning completed via compat bootstrap handoff.",
    "yellow": "Yellow development completed via compat bootstrap handoff.",
    "green": "Green sustainability review completed via compat bootstrap handoff.",
    "blue": "Blue communication completed via compat bootstrap handoff.",
}

_SEAT_NEXT_STEP_NOTE = {
    "red": (
        "Orange planning activated after Red inquiry handoff. "
        "Deterministic Orange planning payload created and validated for Yellow handoff readiness."
    ),
    "orange": "Yellow development activated after Orange produced a feasible canon-aligned plan.",
    "yellow": "Green sustainability review activated after Yellow produced a viable canon-aligned solution path.",
    "green": "Blue communication activated after Green aligned the resources and sustainability path.",
    "blue": "Purple reflection activated after Blue produced an effective communication path.",
}

_NONTERMINAL_SEAT_DECISION_FALLBACK = {
    "red": "sufficient_data",
    "orange": "feasible_plan",
    "yellow": "viable_solution",
    "green": "resources_aligned",
    "blue": "communication_effective",
}


def _structured_error(exc: Exception, context: str = "") -> Dict[str, Any]:
    """Return a structured failure payload instead of leaking a raw traceback."""
    return {
        "success": False,
        "error": {
            "type": type(exc).__name__,
            "message": str(exc),
            **({"context": context} if context else {}),
        },
    }


# ---------------------------------------------------------------------------
# CRONUS seat-agent integration
# ---------------------------------------------------------------------------

_CRONUS_CONFIG: Dict[str, Any] | None = None
_CRONUS_CONFIG_PATH = (
    pathlib.Path(__file__).resolve().parents[3] / "CRONUS" / "config" / "config.toml"
)

# Human-readable seat names for context headers (mirrors pipeline._build_pipeline_context)
_SEAT_LETTER: Dict[str, str] = {
    "red": "C", "orange": "R", "yellow": "O",
    "green": "N", "blue": "U", "purple": "S",
}
_SEAT_NAME: Dict[str, str] = {
    "red": "Red Owl", "orange": "Orange Orangutan", "yellow": "Yellow Honeybee",
    "green": "Green Tortoise", "blue": "Blue Dolphin", "purple": "Purple Elephant",
}


def _load_cronus_config() -> Dict[str, Any]:
    global _CRONUS_CONFIG
    if _CRONUS_CONFIG is not None:
        return _CRONUS_CONFIG
    try:
        import toml  # type: ignore[import]
        if _CRONUS_CONFIG_PATH.exists():
            _CRONUS_CONFIG = toml.load(_CRONUS_CONFIG_PATH)
        else:
            _CRONUS_CONFIG = {}
    except Exception:
        _CRONUS_CONFIG = {}
    return _CRONUS_CONFIG


def _get_prior_step_text(session: Any, workflow_session_id: str, seat: str) -> str:
    """
    Return the prior seat's actual LLM output as formatted context text,
    mirroring how pipeline._build_pipeline_context passes prior outputs.
    JSON blobs are not passed — only the human-readable agent_response or result_text.
    """
    step = (
        session.query(WorkflowStep)
        .filter(
            WorkflowStep.session_id == uuid.UUID(workflow_session_id),
            WorkflowStep.step_name == WORKFLOW_STEP_BY_SEAT.get(seat, f"{seat}_step"),
        )
        .first()
    )
    if not step or not step.output_data:
        return ""
    od = step.output_data
    text = od.get("agent_response") or od.get("result_text") or ""
    if not text:
        return ""
    letter = _SEAT_LETTER.get(seat, seat.upper()[0])
    name = _SEAT_NAME.get(seat, seat.title())
    return f"[{letter}] {name} ({seat}):\n{text}"


def _get_full_cascade_text(session: Any, workflow_session_id: str) -> str:
    """
    Return the full cascade — all prior seat outputs formatted as a complete council briefing.
    Used by Purple, who must see the entire cycle to generate WHO impact report.
    """
    seats_in_order = ["red", "orange", "yellow", "green", "blue"]
    parts = []
    for seat in seats_in_order:
        text = _get_prior_step_text(session, workflow_session_id, seat)
        if text:
            parts.append(text)
    return "\n\n".join(parts)


def _write_agent_result_to_step(
    session: Any, workflow_session_id: str, step_name: str, agent_result: Dict[str, Any]
) -> None:
    """
    Write the LLM result into the seat's WorkflowStep.output_data BEFORE the advance
    function reads it. This ensures advance_*_handoff commits real LLM content, not bootstrap.
    """
    agent_text = agent_result.get("result") or ""
    if not agent_text:
        return
    step = (
        session.query(WorkflowStep)
        .filter(
            WorkflowStep.session_id == uuid.UUID(workflow_session_id),
            WorkflowStep.step_name == step_name,
        )
        .first()
    )
    if step:
        data = dict(step.output_data or {})
        data["agent_response"] = agent_text
        data["agent_model"] = agent_result.get("model")
        data["agent_completed_at"] = datetime.now(timezone.utc).isoformat()
        step.output_data = data


async def _run_seat_agent(
    seat: str,
    problem_task: str,
    prior_context: str,
) -> Dict[str, Any]:
    """
    Call CRONUS run_task for the seat. Blocks until the LLM finishes — this IS the
    computation. The system prompt is built from locked canon by _build_system_prompt.
    `problem_task` is the problem statement (user turn only — not role definition).
    `prior_context` is formatted prior-seat LLM text (mirrors pipeline context).
    Falls back gracefully if Ollama is unreachable.
    """
    try:
        from cronus.app.agents.runtime import run_task  # noqa: PLC0415
    except Exception as exc:
        return {"result": None, "error": str(exc)}

    config = _load_cronus_config()
    try:
        return await run_task(problem_task, seat, prior_context or None, config, use_tools=True)
    except Exception as exc:
        return {"result": None, "error": str(exc)}


# ---------------------------------------------------------------------------

class EnterpriseQueryRequest(BaseModel):
    seat: str = Field(..., description="Outer council seat id")
    question: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None


class CompatProblemCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None
    export_twin_earth: bool = False
    twin_earth_domain: str = "npc_behavior"
    fractal_address: Optional[str] = None


class CompatCycleCreateRequest(BaseModel):
    problem_id: str
    mode: str = "ouroboros"
    autonomous: bool = True
    fractal_address: Optional[str] = None


class AdvanceSeatRequest(BaseModel):
    problem_id: str
    seat: str


class PurpleDecisionRequest(BaseModel):
    problem_id: str
    decision_outcome: str = Field(..., pattern="^(effective_solution|adjustments_needed)$")


def _compat_database_url() -> str:
    return f"sqlite+aiosqlite:///{_PROJECTS_HUB_DB_PATH}"


def _db_manager() -> UnifiedDatabaseManager:
    global _COMPAT_DB_MANAGER
    if _COMPAT_DB_MANAGER is None:
        os.environ.setdefault("DATABASE_URL", _compat_database_url())
        _COMPAT_DB_MANAGER = UnifiedDatabaseManager(database_url=_compat_database_url())
    return _COMPAT_DB_MANAGER


def _problem_payload(problem: Problem, workflow_session_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
    return {
        "problem_id": str(problem.id),
        "title": problem.title,
        "description": problem.description,
        "status": problem.status,
        "created_at": problem.created_at.isoformat() if problem.created_at else None,
        "binding": {
            "workflow_session_id": str(workflow_session_id) if workflow_session_id else None,
            "db_problem_id": str(problem.id),
        },
    }


def _cycle_payload(cycle: Cycle, workflow_session_id: Optional[uuid.UUID]) -> Dict[str, Any]:
    return {
        "cycle_id": str(cycle.id),
        "problem_id": str(cycle.problem_id),
        "status": cycle.status,
        "responses": [],
        "synthesis": None,
        "action_items": [],
        "binding": {
            "workflow_session_id": str(workflow_session_id) if workflow_session_id else None,
            "db_cycle_id": str(cycle.id),
        },
    }


def _seat_query_payload(seat: str, result: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    analysis = result.get("result")
    if not isinstance(analysis, str) or not analysis.strip():
        analysis = "Live runtime returned no structured analysis."
    confidence = 0.0 if result.get("error") else 0.7
    return {
        "seat": seat,
        "identity": profile.get("identity"),
        "guiding_question": profile.get("guiding_question"),
        "analysis": analysis,
        "recommendations": profile.get("responsibilities", [])[:3],
        "confidence": confidence,
        "source": {
            "runtime": "live",
            "canon": "live",
        },
        "runtime": {
            "steps": result.get("steps", []),
            "error": result.get("error"),
            "provider": result.get("provider"),
            "model": result.get("model"),
        },
    }


def _create_workflow_binding(session, problem_id: uuid.UUID) -> WorkflowSession:
    first_seat = outer_seats()[0]
    first_step_name = WORKFLOW_STEP_BY_SEAT.get(first_seat, f"{first_seat}_step")
    workflow_session = WorkflowSession(
        id=uuid.uuid4(),
        problem_id=problem_id,
        session_type="compat_council",
        status="active",
        current_step=first_step_name,
        started_at=datetime.now(timezone.utc),
        session_data={"source": "compat_council"},
        user_preferences={},
        session_notes=[],
    )
    session.add(workflow_session)

    for order, seat in enumerate(outer_seats(), start=1):
        step_name = WORKFLOW_STEP_BY_SEAT.get(seat, f"{seat}_step")
        session.add(
            WorkflowStep(
                id=uuid.uuid4(),
                session_id=workflow_session.id,
                step_name=step_name,
                step_type=seat,
                step_order=order,
                status="active" if seat == first_seat else "pending",
                input_data={},
                output_data={},
                ai_enhanced=True,
            )
        )

    return workflow_session


def build_bootstrap_orange_payload(
    problem: Problem,
    workflow_session: WorkflowSession,
    upstream_payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    required_outputs = required_outputs_for_seat("orange")
    decision_outcome = canonical_success_outcome_for_seat("orange") or "feasible_plan"
    upstream_payload = dict(upstream_payload or {})
    loopback_context = upstream_payload.get("loopback_context") if isinstance(upstream_payload, dict) else None
    research_summary = str(upstream_payload.get("research_summary") or "").strip()
    inner_council = ((upstream_payload.get("think_tank") or {}).get("inner_council") or []) if isinstance(upstream_payload, dict) else []
    sentry_tribunal = upstream_payload.get("sentry_tribunal") if isinstance(upstream_payload, dict) else None
    research_threads = [
        {
            "seat": child.get("seat"),
            "node_address": ((child.get("node_identity") or {}).get("node_address")),
            "contribution": child.get("contribution"),
        }
        for child in inner_council
        if isinstance(child, dict) and child.get("seat")
    ]
    inner_council_addresses = [thread.get("node_address") for thread in research_threads if thread.get("node_address")]
    sentry_observation_summary = (
        (((sentry_tribunal or {}).get("sentry_recursion") or {}).get("sentry_a") or {}).get("observation_summary")
        if isinstance(sentry_tribunal, dict)
        else None
    )
    strategy_summary = (
        f"Refine the recursive Red research for '{problem.title}' into a bounded implementation plan "
        "that resolves the Purple-triggered adjustment vector before handing off to Yellow."
        if isinstance(loopback_context, dict) and loopback_context
        else f"Translate Red's inner-council research for '{problem.title}' into a bounded implementation plan "
        "that uses the six research threads and the sentry observations to hand off cleanly to Yellow."
        if research_threads
        else f"Translate the Red inquiry for '{problem.title}' into a bounded implementation plan "
        "that can hand off cleanly to Yellow."
    )
    prioritized_tasks = (
        [
            "Resolve the specific adjustment vector returned by Purple reflection.",
            "Turn Red's restarted research focus into a sharper planning sequence for Yellow.",
            "Preserve recursive continuity so the next implementation pass addresses the known weakness directly.",
        ]
        if isinstance(loopback_context, dict) and loopback_context
        else [
            "Consolidate the six Red inner-council research threads into one executable plan.",
            "Use the sentry observation summary to protect the plan against weak handoff assumptions.",
            "Define the proof point that will show the plan is ready for Yellow development.",
        ]
        if research_threads
        else [
            "Define the next bounded implementation move.",
            "Sequence the immediate execution steps for the Yellow prototype pass.",
            "Identify the proof point that will show the plan is ready for development.",
        ]
    )
    contingency_plans = (
        [
            "Loop back to Red again if the refined plan still fails to address Purple's stated adjustment vector.",
            "Escalate to Green early if the recursive adjustment implies a sustainability or resource bottleneck.",
        ]
        if isinstance(loopback_context, dict) and loopback_context
        else [
            "Loop back to Red if a critical unknown or missing dependency breaks the plan.",
        ]
    )
    dependencies = [
        "A live compat workflow session exists.",
        "The canon-aligned seat transition path is available.",
        f"Workflow session id: {workflow_session.id}",
    ]
    if research_summary:
        dependencies.append(f"Red research summary: {research_summary}")
    payload = {
        "strategy_summary": strategy_summary,
        "prioritized_tasks": prioritized_tasks,
        "contingency_plans": contingency_plans,
        "dependencies": dependencies,
        "constraints": [
            "Stay on the Dream Caesar integration spine.",
            "Avoid broad refactors while the multiagent session is active.",
        ],
        "required_outputs": required_outputs,
        "recommended_next_seat": "yellow",
        "decision_outcome": decision_outcome,
        "source": "compat_council.bootstrap_orange_payload",
        "problem_context": {
            "title": problem.title,
            "description": problem.description,
            "domain": problem.domain,
        },
        "upstream_research_summary": research_summary or None,
        "research_threads": research_threads,
        "inner_council_addresses": inner_council_addresses,
        "sentry_observation_summary": sentry_observation_summary,
        "loopback_context": loopback_context if isinstance(loopback_context, dict) and loopback_context else None,
    }
    validation = validate_orange_payload(payload)
    if not validation["valid"]:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "type": "OrangePayloadValidationError",
                    "message": "Bootstrap Orange payload failed validation.",
                    "errors": validation["errors"],
                },
            },
        )
    normalized = dict(validation["normalized"])
    normalized["required_outputs"] = required_outputs
    normalized["source"] = payload["source"]
    normalized["problem_context"] = payload["problem_context"]
    normalized["upstream_research_summary"] = payload["upstream_research_summary"]
    normalized["research_threads"] = payload["research_threads"]
    normalized["inner_council_addresses"] = payload["inner_council_addresses"]
    normalized["sentry_observation_summary"] = payload["sentry_observation_summary"]
    if payload.get("loopback_context"):
        normalized["loopback_context"] = payload["loopback_context"]
    return normalized


def build_bootstrap_yellow_payload(
    problem: Problem,
    workflow_session: WorkflowSession,
    upstream_payload: Dict[str, Any] | None,
) -> Dict[str, Any]:
    upstream_payload = dict(upstream_payload or {})
    loopback_context = upstream_payload.get("loopback_context") if isinstance(upstream_payload, dict) else None
    strategy_summary = str((upstream_payload or {}).get("strategy_summary") or "")
    recursive_mode = isinstance(loopback_context, dict) and loopback_context
    payload = {
        "strategy_summary": strategy_summary,
        "prototype_brief": (
            f"Use the recursive Orange plan for '{problem.title}' to create a development pass that directly resolves Purple's adjustment vector."
            if recursive_mode
            else f"Use the Orange plan for '{problem.title}' to create the first bounded implementation or prototype pass."
        ),
        "prototype_artifacts": (
            [
                "A refinement-oriented prototype brief that answers Purple's recursive concern.",
                "A development slice explicitly shaped by Red's restarted research and Orange's recursive planning.",
            ]
            if recursive_mode
            else [
                "A bounded implementation-ready prototype brief.",
                "A validated Orange plan translated into a Yellow development starting point.",
            ]
        ),
        "solution_hypotheses": (
            [
                "The next prototype should directly resolve the loopback reason before advancing.",
                "A clearer development response to Purple's adjustment vector should reduce unnecessary future recursion.",
            ]
            if recursive_mode
            else [
                "The first prototype pass should be strong enough to enter Green resource review.",
            ]
        ),
        "implementation_notes": (
            [
                "Preserve canon alignment and recursive traceability.",
                "Use the inherited loopback context as a design constraint, not just operator metadata.",
                f"Workflow session id: {workflow_session.id}",
            ]
            if recursive_mode
            else [
                "Preserve canon alignment and transition traceability.",
                f"Workflow session id: {workflow_session.id}",
            ]
        ),
        "recommended_next_seat": "green",
        "decision_outcome": "viable_solution",
        "upstream_decision_outcome": str((upstream_payload or {}).get("decision_outcome") or ""),
        "source": "compat_council.bootstrap_yellow_payload",
        "problem_context": {
            "title": problem.title,
            "description": problem.description,
            "domain": problem.domain,
            "workflow_session_id": str(workflow_session.id),
        },
        "upstream_research_summary": upstream_payload.get("upstream_research_summary"),
        "loopback_context": loopback_context if recursive_mode else None,
    }
    validation = validate_yellow_payload(payload)
    if not validation["valid"]:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "type": "YellowPayloadValidationError",
                    "message": "Bootstrap Yellow payload failed validation.",
                    "errors": validation["errors"],
                },
            },
        )
    normalized = dict(validation["normalized"])
    normalized["strategy_summary"] = payload["strategy_summary"]
    normalized["upstream_decision_outcome"] = payload["upstream_decision_outcome"]
    normalized["source"] = payload["source"]
    normalized["problem_context"] = payload["problem_context"]
    normalized["upstream_research_summary"] = payload["upstream_research_summary"]
    if payload.get("loopback_context"):
        normalized["loopback_context"] = payload["loopback_context"]
    return normalized


def build_bootstrap_green_payload(
    problem: Problem,
    workflow_session: WorkflowSession,
    upstream_payload: Dict[str, Any] | None,
) -> Dict[str, Any]:
    upstream_payload = dict(upstream_payload or {})
    loopback_context = upstream_payload.get("loopback_context") if isinstance(upstream_payload, dict) else None
    prototype_brief = str(upstream_payload.get("prototype_brief") or "").strip()
    upstream_research_summary = str(upstream_payload.get("upstream_research_summary") or "").strip()
    recursive_mode = isinstance(loopback_context, dict) and loopback_context
    payload = {
        "resource_summary": (
            f"Review the recursive Yellow prototype path for '{problem.title}' against time, effort, and sustainability constraints before communication."
            if recursive_mode
            else f"Review the Yellow prototype path for '{problem.title}' against time, effort, and sustainability constraints."
        ),
        "budget_focus": (
            [
                "Keep the recursive refinement bounded to the adjustment vector raised by Purple.",
                "Preserve reversible changes while the loop is still converging on a stable answer.",
                "Only spend effort on prototype work that directly resolves the inherited recursive weakness.",
            ]
            if recursive_mode
            else [
                "Keep the next implementation move bounded.",
                "Prefer reversible changes while the integrated loop is still proving itself.",
            ]
        ),
        "timeline_assumptions": (
            [
                "The recursive Yellow prototype can be reviewed immediately in the current runtime session.",
                "Resource review should preserve continuity from Purple's loopback without reopening solved scope.",
            ]
            if recursive_mode
            else [
                "The Yellow prototype can be reviewed immediately in the current runtime session.",
            ]
        ),
        "recommended_next_seat": "blue",
        "decision_outcome": "resources_aligned",
        "source": "compat_council.bootstrap_green_payload",
        "problem_context": {
            "title": problem.title,
            "description": problem.description,
            "domain": problem.domain,
            "workflow_session_id": str(workflow_session.id),
        },
        "upstream_decision_outcome": str((upstream_payload or {}).get("decision_outcome") or ""),
        "prototype_brief": prototype_brief or None,
        "upstream_research_summary": upstream_research_summary or None,
        "loopback_context": loopback_context if recursive_mode else None,
    }
    validation = validate_green_payload(payload)
    if not validation["valid"]:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "type": "GreenPayloadValidationError",
                    "message": "Bootstrap Green payload failed validation.",
                    "errors": validation["errors"],
                },
            },
        )
    normalized = dict(validation["normalized"])
    normalized["source"] = payload["source"]
    normalized["problem_context"] = payload["problem_context"]
    normalized["upstream_decision_outcome"] = payload["upstream_decision_outcome"]
    normalized["prototype_brief"] = payload["prototype_brief"]
    normalized["upstream_research_summary"] = payload["upstream_research_summary"]
    if payload.get("loopback_context"):
        normalized["loopback_context"] = payload["loopback_context"]
    return normalized


def build_bootstrap_blue_payload(
    problem: Problem,
    workflow_session: WorkflowSession,
    upstream_payload: Dict[str, Any] | None,
) -> Dict[str, Any]:
    upstream_payload = dict(upstream_payload or {})
    loopback_context = upstream_payload.get("loopback_context") if isinstance(upstream_payload, dict) else None
    resource_summary = str(upstream_payload.get("resource_summary") or "").strip()
    upstream_research_summary = str(upstream_payload.get("upstream_research_summary") or "").strip()
    recursive_mode = isinstance(loopback_context, dict) and loopback_context
    payload = {
        "message_summary": (
            f"Translate the recursive Green-reviewed solution path for '{problem.title}' into a clear communication and rollout message that reflects Purple's adjustment vector."
            if recursive_mode
            else f"Translate the Green-reviewed solution path for '{problem.title}' into a clear communication and rollout message."
        ),
        "audience_targets": (
            [
                "Operator",
                "Dream Caesar runtime surfaces",
                "Purple reflection as the immediate downstream validator",
            ]
            if recursive_mode
            else [
                "Operator",
                "Dream Caesar runtime surfaces",
            ]
        ),
        "delivery_assets": (
            [
                "A recursive operator-facing summary that explains what changed after the loopback.",
                "A clear handoff note for Purple showing how the adjustment vector was addressed.",
            ]
            if recursive_mode
            else [
                "Clear operator-facing summary.",
                "Readable next-step communication for downstream reflection.",
            ]
        ),
        "recommended_next_seat": "purple",
        "decision_outcome": "communication_effective",
        "source": "compat_council.bootstrap_blue_payload",
        "problem_context": {
            "title": problem.title,
            "description": problem.description,
            "domain": problem.domain,
            "workflow_session_id": str(workflow_session.id),
        },
        "upstream_decision_outcome": str((upstream_payload or {}).get("decision_outcome") or ""),
        "resource_summary": resource_summary or None,
        "upstream_research_summary": upstream_research_summary or None,
        "loopback_context": loopback_context if recursive_mode else None,
    }
    validation = validate_blue_payload(payload)
    if not validation["valid"]:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "type": "BluePayloadValidationError",
                    "message": "Bootstrap Blue payload failed validation.",
                    "errors": validation["errors"],
                },
            },
        )
    normalized = dict(validation["normalized"])
    normalized["source"] = payload["source"]
    normalized["problem_context"] = payload["problem_context"]
    normalized["upstream_decision_outcome"] = payload["upstream_decision_outcome"]
    normalized["resource_summary"] = payload["resource_summary"]
    normalized["upstream_research_summary"] = payload["upstream_research_summary"]
    if payload.get("loopback_context"):
        normalized["loopback_context"] = payload["loopback_context"]
    return normalized


def build_bootstrap_purple_payload(
    problem: Problem,
    workflow_session: WorkflowSession,
    upstream_payload: Dict[str, Any] | None,
) -> Dict[str, Any]:
    upstream_payload = dict(upstream_payload or {})
    loopback_context = upstream_payload.get("loopback_context") if isinstance(upstream_payload, dict) else None
    upstream_research_summary = str(upstream_payload.get("upstream_research_summary") or "").strip()
    message_summary = str(upstream_payload.get("message_summary") or "").strip()
    recursive_mode = isinstance(loopback_context, dict) and loopback_context
    return {
        "reflection_summary": (
            f"Review whether the recursively adjusted communication for '{problem.title}' now resolves the prior loopback condition or still requires another refinement pass."
            if recursive_mode
            else f"Review whether the communicated solution for '{problem.title}' is coherent, complete, and ready to close or recurse."
        ),
        "lessons_learned": (
            [
                "The cycle preserved recursive continuity from Purple back through Red, Orange, Yellow, Green, and Blue.",
                "Reflection can now judge whether the prior adjustment vector was actually addressed."
            ]
            if recursive_mode
            else [
                "The canon-aligned handoff path now reaches the reflection seat.",
            ]
        ),
        "adjustment_vectors": (
            list(loopback_context.get("adjustment_vectors") or []) + ["If the recursive communication still misses the mark, loop back with a sharper research brief."]
            if recursive_mode
            else [
                "If communication is weak, route back into Yellow or Green.",
            ]
        ),
        "recommended_next_seat": "red",
        "decision_outcome": "effective_solution",
        "source": "compat_council.bootstrap_purple_payload",
        "problem_context": {
            "title": problem.title,
            "description": problem.description,
            "domain": problem.domain,
            "workflow_session_id": str(workflow_session.id),
        },
        "upstream_decision_outcome": str((upstream_payload or {}).get("decision_outcome") or ""),
        "message_summary": message_summary or None,
        "upstream_research_summary": upstream_research_summary or None,
        "loopback_context": loopback_context if recursive_mode else None,
    }


def _resolve_purple_decision_payload(
    purple_payload: Dict[str, Any],
    *,
    decision_outcome: str,
) -> Dict[str, Any]:
    resolved = dict(purple_payload)
    loopback_context = resolved.get("loopback_context")
    recursive_mode = isinstance(loopback_context, dict) and loopback_context

    resolved["decision_outcome"] = decision_outcome
    resolved["recommended_next_seat"] = None if decision_outcome == "effective_solution" else "red"
    resolved["resolution_mode"] = "terminal_close" if decision_outcome == "effective_solution" else "recursive_loopback"
    resolved["resolution_assessment"] = (
        "recursive_reflection_resolved"
        if decision_outcome == "effective_solution"
        else "recursive_reflection_requires_adjustment"
    ) if recursive_mode else (
        "reflection_resolved"
        if decision_outcome == "effective_solution"
        else "reflection_requires_adjustment"
    )
    resolved["resolution_reason"] = (
        "Sentry tribunal closed the recursively adjusted cycle after reviewing Purple's WHO impact report."
        if recursive_mode and decision_outcome == "effective_solution"
        else "Sentry tribunal continued the recursively adjusted cycle — Purple's WHO report surfaced unresolved consequences."
        if recursive_mode
        else "Sentry tribunal closed the cycle after reviewing Purple's WHO impact report."
        if decision_outcome == "effective_solution"
        else "Sentry tribunal continued the cycle — Purple's WHO report surfaced consequences requiring further processing."
    )

    lessons_learned = list(resolved.get("lessons_learned") or [])
    if decision_outcome == "effective_solution":
        lessons_learned.append(
            "Sentry tribunal closed the loop after Purple's WHO report on the recursive adjustment path."
            if recursive_mode
            else "Sentry tribunal closed the loop after Purple's WHO impact report."
        )
    else:
        lessons_learned.append(
            "Sentry tribunal kept the cycle open — Purple's WHO report on the recursive path identified unresolved impacts."
            if recursive_mode
            else "Sentry tribunal kept the cycle open — Purple's WHO report identified unresolved impacts."
        )
    resolved["lessons_learned"] = lessons_learned
    return resolved


def _seed_runtime_binding_artifact(
    *,
    problem: Problem,
    workflow_session: WorkflowSession,
    source: str,
) -> None:
    first_seat = outer_seats()[0]
    first_step_name = WORKFLOW_STEP_BY_SEAT.get(first_seat, f"{first_seat}_step")
    first_stage = canonical_validation_stage_for_seat(first_seat)
    record_workflow_step_artifact(
        problem_id=str(problem.id),
        workflow_session_id=str(workflow_session.id),
        step_id=None,
        step_name=first_step_name,
        step_type=first_seat,
        step_order=1,
        status=workflow_session.status,
        started_at=workflow_session.started_at.isoformat() if workflow_session.started_at else None,
        completed_at=workflow_session.completed_at.isoformat() if workflow_session.completed_at else None,
        duration=workflow_session.total_duration,
        input_data={
            "problem_title": problem.title,
            "problem_description": problem.description,
            "problem_domain": problem.domain,
        },
        output_data={
            "binding_kind": "compat_council",
            "workflow_session_id": str(workflow_session.id),
        },
        step_notes="Compat council session initialized at the Red inquiry seat.",
        source=source,
    )
    record_cycle_iteration_artifact(
        problem_id=str(problem.id),
        workflow_session_id=str(workflow_session.id),
        seat=first_seat,
        step_name=first_step_name,
        event_type="step_started",
        status="in_progress",
        source=source,
        fractal_address=first_seat,
        council_address_kind="outer_hexagon",
        validation_stage=first_stage,
        sentry_shell_state="active",
        metadata={
            "binding_kind": "compat_council",
            "workflow_session_id": str(workflow_session.id),
            "problem_title": problem.title,
        },
    )


def advance_workflow_seat_transition(
    *,
    workflow_session_id: str,
    problem_id: str,
    from_seat: str,
    decision_outcome: str,
    output_payload: Dict[str, Any],
    source: str,
    completion_note: str,
    next_step_note: str,
) -> dict[str, Any]:
    db_manager = _db_manager()
    normalized_from_seat = from_seat.lower()
    from_step_name = WORKFLOW_STEP_BY_SEAT.get(normalized_from_seat, f"{normalized_from_seat}_step")
    from_stage = canonical_validation_stage_for_seat(normalized_from_seat)
    completed_at = datetime.now(timezone.utc)
    completed_at_iso = completed_at.isoformat()
    started_at_iso = completed_at_iso
    decision = resolve_decision_tree_transition(normalized_from_seat, decision_outcome)
    next_seat = decision.get("next_seat")
    if not isinstance(next_seat, str) or not next_seat.strip():
        raise HTTPException(status_code=400, detail=f"No canonical next seat for {normalized_from_seat}:{decision_outcome}")
    normalized_next_seat = next_seat.lower()
    next_step_name = WORKFLOW_STEP_BY_SEAT.get(normalized_next_seat, f"{normalized_next_seat}_step")
    next_stage = canonical_validation_stage_for_seat(normalized_next_seat)
    is_loopback = bool(decision.get("terminal")) is False and (
        normalized_next_seat == normalized_from_seat
        or normalized_next_seat in outer_seats()[: outer_seats().index(normalized_from_seat) + 1]
        or bool(decision.get("alternate_next_seats"))
    )
    sentry_tribunal = output_payload.get("sentry_tribunal") if isinstance(output_payload, dict) else None
    sentry_recovery_attempt = (
        sentry_tribunal.get("recovery_attempt")
        if isinstance(sentry_tribunal, dict)
        else None
    )
    repaired_payload = (
        sentry_tribunal.get("repaired_payload")
        if isinstance(sentry_tribunal, dict)
        else None
    )
    sentry_recovery = (
        repaired_payload.get("sentry_recovery")
        if isinstance(repaired_payload, dict)
        else None
    )
    node_identity = output_payload.get("node_identity") if isinstance(output_payload, dict) else None
    think_tank = output_payload.get("think_tank") if isinstance(output_payload, dict) else None
    inherited_loopback_context = output_payload.get("loopback_context") if isinstance(output_payload, dict) else None
    loopback_context = {
        "trigger_seat": normalized_from_seat,
        "trigger_step": from_step_name,
        "trigger_outcome": decision_outcome,
        "target_seat": normalized_next_seat,
        "reason": decision.get("reason"),
        "alternate_next_seats": decision.get("alternate_next_seats") or [],
        "reflection_summary": output_payload.get("reflection_summary"),
        "adjustment_vectors": output_payload.get("adjustment_vectors") or [],
        "source": source,
    } if is_loopback else None

    with db_manager.get_session() as session:
        workflow_session = session.query(WorkflowSession).filter(WorkflowSession.id == uuid.UUID(workflow_session_id)).first()
        if workflow_session is None:
            raise HTTPException(status_code=404, detail=f"Workflow session not found: {workflow_session_id}")

        from_step = (
            session.query(WorkflowStep)
            .filter(WorkflowStep.session_id == workflow_session.id, WorkflowStep.step_name == from_step_name)
            .first()
        )
        next_step = (
            session.query(WorkflowStep)
            .filter(WorkflowStep.session_id == workflow_session.id, WorkflowStep.step_name == next_step_name)
            .first()
        )
        problem = session.query(Problem).filter(Problem.id == uuid.UUID(problem_id)).first()
        if from_step is None or next_step is None or problem is None:
            raise HTTPException(status_code=404, detail="Required compat workflow rows are missing.")

        from_step.status = "completed"
        from_step.started_at = from_step.started_at or completed_at
        from_step.completed_at = completed_at
        from_step.duration = 0
        from_step.output_data = output_payload
        from_step.step_notes = completion_note

        next_step.status = "active"
        next_step.started_at = next_step.started_at or completed_at
        next_step_input_data: Dict[str, Any] = {
            "upstream_payload": output_payload,
            "from_seat": normalized_from_seat,
        }
        if loopback_context:
            next_step_input_data["loopback_context"] = loopback_context
        next_step.input_data = next_step_input_data
        if normalized_next_seat == "orange":
            next_step.output_data = build_bootstrap_orange_payload(problem, workflow_session, output_payload)
        elif normalized_next_seat == "yellow":
            next_step.output_data = build_bootstrap_yellow_payload(problem, workflow_session, output_payload)
        elif normalized_next_seat == "green":
            next_step.output_data = build_bootstrap_green_payload(problem, workflow_session, output_payload)
        elif normalized_next_seat == "blue":
            next_step.output_data = build_bootstrap_blue_payload(problem, workflow_session, output_payload)
        elif normalized_next_seat == "purple":
            next_step.output_data = build_bootstrap_purple_payload(problem, workflow_session, output_payload)
        next_step.step_notes = next_step_note

        workflow_session.current_step = next_step_name
        workflow_session.status = "active"
        session.commit()

        bind_active_problem(
            problem_id=problem_id,
            workflow_session_id=workflow_session_id,
            problem_title=problem.title,
            problem_status=problem.status,
            workflow_session_status=workflow_session.status,
            workflow_current_step=next_step_name,
            source=source,
            fractal_address=normalized_next_seat,
            validation_stage=next_stage,
        )

        from_artifact = record_workflow_step_artifact(
            problem_id=problem_id,
            workflow_session_id=workflow_session_id,
            step_id=str(from_step.id),
            step_name=from_step_name,
            step_type=normalized_from_seat,
            step_order=from_step.step_order,
            status="completed",
            started_at=(from_step.started_at.isoformat() if from_step.started_at else started_at_iso),
            completed_at=completed_at_iso,
            duration=0,
            input_data=from_step.input_data or {},
            output_data=output_payload,
            step_notes=from_step.step_notes,
            source=source,
        )
        from_iteration = record_cycle_iteration_artifact(
            problem_id=problem_id,
            workflow_session_id=workflow_session_id,
            seat=normalized_from_seat,
            step_name=from_step_name,
            event_type="step_completed",
            status="completed",
            decision_outcome=decision_outcome,
            next_seat=decision.get("next_seat"),
            alternate_next_seats=decision.get("alternate_next_seats"),
            terminal=bool(decision.get("terminal")),
            reason=decision.get("reason"),
            source=source,
            fractal_address=normalized_from_seat,
            council_address_kind="outer_hexagon",
            validation_stage=from_stage,
            sentry_shell_state="active",
            tribunal_verdict=sentry_tribunal if isinstance(sentry_tribunal, dict) else None,
            metadata={
                "workflow_step_artifact_path": from_artifact["artifact_path"],
                "transition_kind": "seat_handoff",
                "resolution_assessment": output_payload.get("resolution_assessment"),
                "resolution_reason": output_payload.get("resolution_reason"),
                "resolution_mode": output_payload.get("resolution_mode"),
                **({"node_identity": node_identity} if isinstance(node_identity, dict) and node_identity else {}),
                **({"think_tank": think_tank} if isinstance(think_tank, dict) and think_tank else {}),
                **({"sentry_tribunal": sentry_tribunal} if isinstance(sentry_tribunal, dict) and sentry_tribunal else {}),
                **({"sentry_recovery_attempt": sentry_recovery_attempt} if isinstance(sentry_recovery_attempt, dict) and sentry_recovery_attempt else {}),
                **({"sentry_recovery": sentry_recovery} if isinstance(sentry_recovery, dict) and sentry_recovery else {}),
                **({"inherited_loopback_context": inherited_loopback_context} if isinstance(inherited_loopback_context, dict) and inherited_loopback_context else {}),
                **({"loopback_context": loopback_context} if loopback_context else {}),
            },
        )
        next_artifact = record_workflow_step_artifact(
            problem_id=problem_id,
            workflow_session_id=workflow_session_id,
            step_id=str(next_step.id),
            step_name=next_step_name,
            step_type=normalized_next_seat,
            step_order=next_step.step_order,
            status="active",
            started_at=(next_step.started_at.isoformat() if next_step.started_at else completed_at_iso),
            completed_at=None,
            duration=None,
            input_data=next_step.input_data or {},
            output_data=next_step.output_data or {},
            step_notes=next_step.step_notes,
            source=source,
        )
        next_iteration = record_cycle_iteration_artifact(
            problem_id=problem_id,
            workflow_session_id=workflow_session_id,
            seat=normalized_next_seat,
            step_name=next_step_name,
            event_type="step_started",
            status="in_progress",
            source=source,
            fractal_address=normalized_next_seat,
            council_address_kind="outer_hexagon",
            validation_stage=next_stage,
            sentry_shell_state="active",
            metadata={
                "workflow_step_artifact_path": next_artifact["artifact_path"],
                "transition_kind": "seat_handoff",
                "handoff_from": normalized_from_seat,
                "handoff_outcome": decision_outcome,
                "loopback": is_loopback,
                **({"sentry_recovery_attempt": sentry_recovery_attempt} if isinstance(sentry_recovery_attempt, dict) and sentry_recovery_attempt else {}),
                **({"sentry_recovery": sentry_recovery} if isinstance(sentry_recovery, dict) and sentry_recovery else {}),
                **({"loopback_context": loopback_context} if loopback_context else {}),
            },
        )

    return {
        "workflow_session_id": workflow_session_id,
        "problem_id": problem_id,
        "completed_step": from_step_name,
        "activated_step": next_step_name,
        "decision_next_seat": decision.get("next_seat"),
        "completed_artifact_path": from_artifact["artifact_path"],
        "completed_iteration_path": from_iteration["artifact_path"],
        "activated_artifact_path": next_artifact["artifact_path"],
        "activated_iteration_path": next_iteration["artifact_path"],
    }


def close_workflow_seat_terminal(
    *,
    workflow_session_id: str,
    problem_id: str,
    seat: str,
    decision_outcome: str,
    output_payload: Dict[str, Any],
    source: str,
    completion_note: str,
) -> dict[str, Any]:
    db_manager = _db_manager()
    normalized_seat = seat.lower()
    step_name = WORKFLOW_STEP_BY_SEAT.get(normalized_seat, f"{normalized_seat}_step")
    stage = canonical_validation_stage_for_seat(normalized_seat)
    completed_at = datetime.now(timezone.utc)
    completed_at_iso = completed_at.isoformat()
    decision = resolve_decision_tree_transition(normalized_seat, decision_outcome)

    with db_manager.get_session() as session:
        workflow_session = session.query(WorkflowSession).filter(WorkflowSession.id == uuid.UUID(workflow_session_id)).first()
        problem = session.query(Problem).filter(Problem.id == uuid.UUID(problem_id)).first()
        step = (
            session.query(WorkflowStep)
            .filter(WorkflowStep.session_id == uuid.UUID(workflow_session_id), WorkflowStep.step_name == step_name)
            .first()
        )
        if workflow_session is None or problem is None or step is None:
            raise HTTPException(status_code=404, detail="Required terminal workflow rows are missing.")

        step.status = "completed"
        step.started_at = step.started_at or completed_at
        step.completed_at = completed_at
        step.duration = 0
        step.output_data = output_payload
        step.step_notes = completion_note

        workflow_session.status = "completed"
        workflow_session.completed_at = completed_at

        # Mark the corresponding Cycle completed — find by problem_id ordered to match cycle_number
        all_cycles = (
            session.query(Cycle)
            .filter(Cycle.problem_id == problem.id, Cycle.status == "running")
            .order_by(Cycle.started_at.desc())
            .all()
        )
        if all_cycles:
            all_cycles[0].status = "completed"
            all_cycles[0].completed_at = completed_at

        session.commit()

        bind_active_problem(
            problem_id=problem_id,
            workflow_session_id=workflow_session_id,
            problem_title=problem.title,
            problem_status=problem.status,
            workflow_session_status=workflow_session.status,
            workflow_current_step=step_name,
            source=source,
            fractal_address=normalized_seat,
            validation_stage=stage,
        )

        step_artifact = record_workflow_step_artifact(
            problem_id=problem_id,
            workflow_session_id=workflow_session_id,
            step_id=str(step.id),
            step_name=step_name,
            step_type=normalized_seat,
            step_order=step.step_order,
            status="completed",
            started_at=(step.started_at.isoformat() if step.started_at else completed_at_iso),
            completed_at=completed_at_iso,
            duration=0,
            input_data=step.input_data or {},
            output_data=output_payload,
            step_notes=step.step_notes,
            source=source,
        )
        iteration = record_cycle_iteration_artifact(
            problem_id=problem_id,
            workflow_session_id=workflow_session_id,
            seat=normalized_seat,
            step_name=step_name,
            event_type="step_completed",
            status="completed",
            decision_outcome=decision_outcome,
            next_seat=decision.get("next_seat"),
            alternate_next_seats=decision.get("alternate_next_seats"),
            terminal=bool(decision.get("terminal")),
            reason=decision.get("reason"),
            source=source,
            fractal_address=normalized_seat,
            council_address_kind="outer_hexagon",
            validation_stage=stage,
            sentry_shell_state="active",
            metadata={
                "workflow_step_artifact_path": step_artifact["artifact_path"],
                "transition_kind": "terminal_close",
                "resolution_assessment": output_payload.get("resolution_assessment"),
                "resolution_reason": output_payload.get("resolution_reason"),
                "resolution_mode": output_payload.get("resolution_mode"),
            },
        )

    return {
        "workflow_session_id": workflow_session_id,
        "problem_id": problem_id,
        "completed_step": step_name,
        "decision_outcome": decision_outcome,
        "terminal": True,
        "completed_artifact_path": step_artifact["artifact_path"],
        "completed_iteration_path": iteration["artifact_path"],
    }


def _raise_sentry_gate_failure(seat: str, tribunal: Any) -> None:
    normalized_seat = str(seat or "").strip().lower()
    raise HTTPException(
        status_code=409,
        detail={
            "success": False,
            "error": {
                "type": _SEAT_GATE_ERROR.get(normalized_seat, "SentryGateFailure"),
                "message": _SEAT_GATE_MESSAGE.get(normalized_seat, "Seat completion did not pass the outer sentry gate."),
                "tribunal": tribunal,
            },
        },
    )


def _build_bootstrap_payload_for_seat(
    seat: str,
    problem: Problem,
    workflow_session: WorkflowSession,
    upstream_payload: Dict[str, Any],
) -> Dict[str, Any]:
    normalized_seat = str(seat or "").strip().lower()
    if normalized_seat == "orange":
        return build_bootstrap_orange_payload(problem, workflow_session, upstream_payload)
    if normalized_seat == "yellow":
        return build_bootstrap_yellow_payload(problem, workflow_session, upstream_payload)
    if normalized_seat == "green":
        return build_bootstrap_green_payload(problem, workflow_session, upstream_payload)
    if normalized_seat == "blue":
        return build_bootstrap_blue_payload(problem, workflow_session, upstream_payload)
    if normalized_seat == "purple":
        return build_bootstrap_purple_payload(problem, workflow_session, upstream_payload)
    return {}


def _load_active_seat_context(
    *,
    workflow_session_id: str,
    problem_id: str,
    seat: str,
) -> tuple[Any, Any, Dict[str, Any], Dict[str, Any]]:
    db_manager = _db_manager()
    step_name = WORKFLOW_STEP_BY_SEAT.get(seat, f"{seat}_step")
    with db_manager.get_session() as session:
        workflow_session = session.query(WorkflowSession).filter(WorkflowSession.id == uuid.UUID(workflow_session_id)).first()
        problem = session.query(Problem).filter(Problem.id == uuid.UUID(problem_id)).first()
        step = (
            session.query(WorkflowStep)
            .filter(WorkflowStep.session_id == uuid.UUID(workflow_session_id), WorkflowStep.step_name == step_name)
            .first()
        )
        if workflow_session is None or problem is None or step is None:
            raise HTTPException(status_code=404, detail=f"Required {seat.title()} workflow rows are missing.")
        upstream_payload = ((step.input_data or {}).get("upstream_payload") or {})
        workflow_session_data = SimpleNamespace(id=workflow_session.id)
        problem_data = SimpleNamespace(
            id=problem.id,
            title=problem.title,
            description=problem.description,
            domain=problem.domain,
        )
        step_data = {
            "input_data": dict(step.input_data or {}),
            "output_data": dict(step.output_data or {}),
        }
        return workflow_session_data, problem_data, step_data, upstream_payload if isinstance(upstream_payload, dict) else {}


def _run_orchestrated_seat_payload(
    *,
    workflow_session_id: str,
    problem_id: str,
    seat: str,
    source: str,
    base_payload: Dict[str, Any] | None = None,
    loopback_context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    normalized_seat = str(seat or "").strip().lower()
    workflow_session, problem, step_data, upstream_payload = _load_active_seat_context(
        workflow_session_id=workflow_session_id,
        problem_id=problem_id,
        seat=normalized_seat,
    )
    runtime = ThinkTankRuntime(source=source)
    payload = dict(
        base_payload
        or step_data["output_data"]
        or _build_bootstrap_payload_for_seat(normalized_seat, problem, workflow_session, upstream_payload)
    )
    runtime_context = loopback_context if isinstance(loopback_context, dict) else upstream_payload
    payload.update(
        runtime.run_seat(
            seat=normalized_seat,
            problem_title=problem.title,
            problem_description=problem.description,
            workflow_session_id=str(workflow_session.id),
            loopback_context=runtime_context if isinstance(runtime_context, dict) and runtime_context else None,
        )
    )
    tribunal = payload.get("sentry_tribunal", {})
    if tribunal.get("overall_verdict") != "pass":
        _raise_sentry_gate_failure(normalized_seat, tribunal)
    return payload


def _advance_orchestrated_seat_handoff(
    *,
    workflow_session_id: str,
    problem_id: str,
    seat: str,
    source: str,
    decision_outcome_fallback: str,
) -> dict[str, Any]:
    payload = _run_orchestrated_seat_payload(
        workflow_session_id=workflow_session_id,
        problem_id=problem_id,
        seat=seat,
        source=source,
    )
    normalized_seat = str(seat or "").strip().lower()
    return advance_workflow_seat_transition(
        workflow_session_id=workflow_session_id,
        problem_id=problem_id,
        from_seat=normalized_seat,
        decision_outcome=str(payload.get("decision_outcome") or decision_outcome_fallback),
        output_payload=dict(payload),
        source=source,
        completion_note=_SEAT_COMPLETION_NOTE[normalized_seat],
        next_step_note=_SEAT_NEXT_STEP_NOTE[normalized_seat],
    )


def _resolve_purple_runtime_payload(
    *,
    workflow_session_id: str,
    problem_id: str,
    source: str,
    decision_outcome: str,
) -> Dict[str, Any]:
    payload = _run_orchestrated_seat_payload(
        workflow_session_id=workflow_session_id,
        problem_id=problem_id,
        seat="purple",
        source=source,
    )
    return _resolve_purple_decision_payload(payload, decision_outcome=decision_outcome)


def advance_initial_seat_handoff(
    *,
    workflow_session_id: str,
    problem_id: str,
    seat: str,
    result_text: str = "Compat council bootstrap completed seat handoff.",
) -> dict[str, Any]:
    normalized_seat = str(seat or "").strip().lower()
    if normalized_seat == "purple":
        raise HTTPException(status_code=400, detail="Use the Purple decision entrypoint for terminal close or loopback.")
    if normalized_seat not in _NONTERMINAL_SEAT_DECISION_FALLBACK:
        raise HTTPException(status_code=400, detail=f"Unsupported seat for generic handoff: {seat}")
    if normalized_seat == "red":
        red_output_payload: Dict[str, Any] = {
            "seat": "red",
            "result_text": result_text,
            "source": "compat_council.advance_initial_red_handoff",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        _, _, step_data, _ = _load_active_seat_context(
            workflow_session_id=workflow_session_id,
            problem_id=problem_id,
            seat="red",
        )
        loopback_context = ((step_data.get("input_data") or {}).get("loopback_context") or {})
        red_output_payload = _run_orchestrated_seat_payload(
            workflow_session_id=workflow_session_id,
            problem_id=problem_id,
            seat="red",
            source="compat_council.advance_initial_red_handoff",
            base_payload=red_output_payload,
            loopback_context=loopback_context if isinstance(loopback_context, dict) and loopback_context else None,
        )
        if isinstance(loopback_context, dict) and loopback_context:
            red_output_payload["reflection_summary"] = loopback_context.get("reflection_summary")
            red_output_payload["adjustment_vectors"] = loopback_context.get("adjustment_vectors") or []
        return advance_workflow_seat_transition(
            workflow_session_id=workflow_session_id,
            problem_id=problem_id,
            from_seat="red",
            decision_outcome="sufficient_data",
            output_payload=red_output_payload,
            source="compat_council.advance_initial_red_handoff",
            completion_note=_SEAT_COMPLETION_NOTE["red"],
            next_step_note=_SEAT_NEXT_STEP_NOTE["red"],
        )

    return _advance_orchestrated_seat_handoff(
        workflow_session_id=workflow_session_id,
        problem_id=problem_id,
        seat=normalized_seat,
        source=f"compat_council.advance_initial_{normalized_seat}_handoff",
        decision_outcome_fallback=_NONTERMINAL_SEAT_DECISION_FALLBACK[normalized_seat],
    )


def advance_initial_purple_decision(
    *,
    workflow_session_id: str,
    problem_id: str,
    decision_outcome: str,
) -> dict[str, Any]:
    normalized_outcome = str(decision_outcome or "").strip().lower()
    if normalized_outcome not in {"effective_solution", "adjustments_needed"}:
        raise HTTPException(status_code=400, detail=f"Unsupported Purple decision outcome: {decision_outcome}")
    purple_payload = _resolve_purple_runtime_payload(
        workflow_session_id=workflow_session_id,
        problem_id=problem_id,
        source=(
            "compat_council.complete_initial_purple_effective_solution"
            if normalized_outcome == "effective_solution"
            else "compat_council.advance_initial_purple_loopback"
        ),
        decision_outcome=normalized_outcome,
    )
    if normalized_outcome == "effective_solution":
        return close_workflow_seat_terminal(
            workflow_session_id=workflow_session_id,
            problem_id=problem_id,
            seat="purple",
            decision_outcome=str(purple_payload.get("decision_outcome") or "effective_solution"),
            output_payload=dict(purple_payload),
            source="compat_council.complete_initial_purple_effective_solution",
            completion_note="Purple WHO report delivered. Sentry tribunal closed the cycle with an effective solution.",
        )
    return advance_workflow_seat_transition(
        workflow_session_id=workflow_session_id,
        problem_id=problem_id,
        from_seat="purple",
        decision_outcome="adjustments_needed",
        output_payload=purple_payload,
        source="compat_council.advance_initial_purple_loopback",
        completion_note="Purple WHO report delivered. Sentry tribunal determined another refinement cycle is needed.",
        next_step_note="Red inquiry reactivated after sentry tribunal identified unresolved impacts in Purple's WHO report.",
    )


def advance_initial_red_handoff(
    *,
    workflow_session_id: str,
    problem_id: str,
    result_text: str = "Compat council bootstrap completed Red inquiry handoff.",
) -> dict[str, Any]:
    return advance_initial_seat_handoff(
        workflow_session_id=workflow_session_id,
        problem_id=problem_id,
        seat="red",
        result_text=result_text,
    )


def advance_initial_orange_handoff(
    *,
    workflow_session_id: str,
    problem_id: str,
) -> dict[str, Any]:
    return advance_initial_seat_handoff(
        workflow_session_id=workflow_session_id,
        problem_id=problem_id,
        seat="orange",
    )


def advance_initial_yellow_handoff(
    *,
    workflow_session_id: str,
    problem_id: str,
) -> dict[str, Any]:
    return advance_initial_seat_handoff(
        workflow_session_id=workflow_session_id,
        problem_id=problem_id,
        seat="yellow",
    )


def advance_initial_green_handoff(
    *,
    workflow_session_id: str,
    problem_id: str,
) -> dict[str, Any]:
    return advance_initial_seat_handoff(
        workflow_session_id=workflow_session_id,
        problem_id=problem_id,
        seat="green",
    )


def advance_initial_blue_handoff(
    *,
    workflow_session_id: str,
    problem_id: str,
) -> dict[str, Any]:
    return advance_initial_seat_handoff(
        workflow_session_id=workflow_session_id,
        problem_id=problem_id,
        seat="blue",
    )


def complete_initial_purple_effective_solution(
    *,
    workflow_session_id: str,
    problem_id: str,
) -> dict[str, Any]:
    return advance_initial_purple_decision(
        workflow_session_id=workflow_session_id,
        problem_id=problem_id,
        decision_outcome="effective_solution",
    )


def advance_initial_purple_loopback(
    *,
    workflow_session_id: str,
    problem_id: str,
) -> dict[str, Any]:
    return advance_initial_purple_decision(
        workflow_session_id=workflow_session_id,
        problem_id=problem_id,
        decision_outcome="adjustments_needed",
    )


@router.get("/enterprises")
async def list_enterprises() -> Dict[str, Any]:
    profiles = full_totem_profile_table()
    enterprises = []
    for seat in outer_seats():
        profile = profiles[seat]
        enterprises.append(
            {
                "seat": seat,
                "identity": profile.get("identity"),
                "guiding_question": profile.get("guiding_question"),
                "canonical_role": profile.get("canonical_role"),
                "next_seat": profile.get("next_seat"),
            }
        )
    return {"enterprises": enterprises}


@router.get("/enterprises/{seat}")
async def get_enterprise(seat: str) -> Dict[str, Any]:
    normalized = seat.lower()
    if normalized not in outer_seats():
        raise HTTPException(status_code=404, detail=f"Unknown seat: {seat}")
    return get_full_totem_profile(normalized)


@router.get("/fractal/{address}")
async def get_fractal_resolution(address: str) -> Dict[str, Any]:
    """Resolve a fractal address and return its components."""
    try:
        return resolve_fractal_address(address)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "resolve_fractal")) from exc


@router.get("/press-the-glass")
async def press_the_glass() -> Dict[str, Any]:
    """
    Summon Dream Caesar at the axis to synthesize current state.
    Provides 'computer vision + dream vision' meta-analysis.
    """
    try:
        from ...scripts.dream_caesar_axis import invoke_axis
        from ...scripts.desktop_runtime import append_to_alignment_log
        
        result = invoke_axis(trigger="user_request")
        
        # TASK B3: Log Axis Synthesis
        if result.get("invoked") and result.get("revelation"):
            log_entry = (
                f"**Oracle Invocation (The Glass Pressed)**\n\n"
                f"> \"{result['revelation']}\"\n\n"
                f"*Dream Caesar observes the axis.*"
            )
            append_to_alignment_log(log_entry)
            
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "press_the_glass")) from exc


@router.post("/ritual")
async def ritual_invocation(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect exact ritual phrases and route to the appropriate council seat.
    Example: "WHY do we begin?" -> Red Owl
    """
    phrase = request.get("phrase", "").strip().upper()
    
    # Canonical Ritual Mapping
    rituals = {
        "WHY DO WE BEGIN?": "red",
        "HOW SHALL WE PROCEED?": "orange",
        "WHAT SHALL WE CREATE?": "yellow",
        "WHEN IS THE HARVEST?": "green",
        "WHERE IS THE VOICE?": "blue",
        "WHO REMEMBERS ALL?": "purple"
    }
    
    seat = rituals.get(phrase)
    if not seat:
        return {
            "success": False, 
            "error": "Ritual unrecognized. The Council remains silent.",
            "available_rituals": list(rituals.keys())
        }
        
    from ...scripts.desktop_runtime import append_to_alignment_log
    append_to_alignment_log(f"**Ritual Invoked:** \"{phrase}\"\n\nThe **{seat}** seat has been summoned via ritual.")
    
    return {
        "success": True,
        "seat": seat,
        "phrase": phrase,
        "message": f"The {seat} totem stirs in response to the ritual."
    }


@router.post("/enterprises/query")
async def query_enterprise(request: EnterpriseQueryRequest) -> Dict[str, Any]:
    seat = request.seat.lower()
    if seat not in outer_seats():
        raise HTTPException(status_code=400, detail=f"Invalid seat: {request.seat}")
    profile = get_full_totem_profile(seat)
    context = json.dumps(request.context or {}, default=str)
    try:
        from cronus.app.agents.runtime import run_task

        result = await run_task(request.question, seat, context, {})
    except Exception as exc:
        result = {
            "result": f"Live runtime unavailable: {exc}",
            "error": str(exc),
            "steps": ["runtime_import_failed"],
            "provider": "compat_fallback",
        }
    return _seat_query_payload(seat, result, profile)


@router.post("/problems")
async def create_problem(request: CompatProblemCreateRequest) -> Dict[str, Any]:
    try:
        db_manager = _db_manager()
        with db_manager.get_session() as session:
            problem = Problem(
                id=uuid.uuid4(),
                title=request.title,
                description=request.description,
                domain="compat_council",
                complexity="moderate",
                status="active",
                priority="medium",
                impact="medium",
                urgency="cyclical",
                priority_score=0.0,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(problem)
            session.commit()
            session.refresh(problem)
            return _problem_payload(problem)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "create_problem")) from exc


@router.get("/problems")
async def list_problems(limit: int = 20) -> Dict[str, Any]:
    try:
        db_manager = _db_manager()
        with db_manager.get_session() as session:
            problems = (
                session.query(Problem)
                .filter(Problem.domain == "compat_council")
                .order_by(Problem.created_at.desc())
                .limit(limit)
                .all()
            )
            return {"problems": [_problem_payload(problem) for problem in problems]}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "list_problems")) from exc


@router.get("/problems/{problem_id}")
async def get_problem(problem_id: str) -> Dict[str, Any]:
    try:
        db_manager = _db_manager()
        with db_manager.get_session() as session:
            problem = session.query(Problem).filter(Problem.id == uuid.UUID(problem_id)).first()
            if not problem:
                raise HTTPException(status_code=404, detail=f"Problem not found: {problem_id}")
            workflow_session = (
                session.query(WorkflowSession)
                .filter(WorkflowSession.problem_id == problem.id)
                .order_by(WorkflowSession.started_at.desc())
                .first()
            )
            return _problem_payload(problem, workflow_session.id if workflow_session else None)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "get_problem")) from exc


@router.post("/cycles")
async def create_cycle(request: CompatCycleCreateRequest) -> Dict[str, Any]:
    try:
        db_manager = _db_manager()
        with db_manager.get_session() as session:
            problem = session.query(Problem).filter(Problem.id == uuid.UUID(request.problem_id)).first()
            if not problem:
                raise HTTPException(status_code=404, detail=f"Problem not found: {request.problem_id}")

            next_cycle_number = (
                session.query(Cycle).filter(Cycle.problem_id == problem.id).count() + 1
            )
            cycle = Cycle(
                id=uuid.uuid4(),
                problem_id=problem.id,
                cycle_number=next_cycle_number,
                status="running" if request.autonomous else "pending",
                started_at=datetime.now(timezone.utc),
                overall_confidence=0.0,
            )
            session.add(cycle)
            workflow_session = _create_workflow_binding(session, problem.id)
            problem.status = "in_progress"
            problem.updated_at = datetime.now(timezone.utc)
            session.commit()
            session.refresh(cycle)
            session.refresh(workflow_session)
            bind_active_problem(
                problem_id=str(problem.id),
                workflow_session_id=str(workflow_session.id),
                problem_title=problem.title,
                problem_status=problem.status,
                workflow_session_status=workflow_session.status,
                workflow_current_step=workflow_session.current_step,
                source="compat_council.create_cycle",
                fractal_address=request.fractal_address,
            )
            _seed_runtime_binding_artifact(
                problem=problem,
                workflow_session=workflow_session,
                source="compat_council.create_cycle",
            )
            return _cycle_payload(cycle, workflow_session.id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "create_cycle")) from exc


@router.get("/cycles")
async def list_cycles(limit: int = 20) -> Dict[str, Any]:
    try:
        db_manager = _db_manager()
        with db_manager.get_session() as session:
            cycles = (
                session.query(Cycle)
                .join(Problem, Problem.id == Cycle.problem_id)
                .filter(Problem.domain == "compat_council")
                .order_by(Cycle.started_at.desc())
                .limit(limit)
                .all()
            )
            payloads = []
            for cycle in cycles:
                workflow_session = (
                    session.query(WorkflowSession)
                    .filter(WorkflowSession.problem_id == cycle.problem_id)
                    .order_by(WorkflowSession.started_at.desc())
                    .first()
                )
                payloads.append(_cycle_payload(cycle, workflow_session.id if workflow_session else None))
            return {"cycles": payloads}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "list_cycles")) from exc


@router.post("/workflows/{workflow_session_id}/advance")
async def advance_workflow_seat(
    workflow_session_id: str,
    request: AdvanceSeatRequest,
) -> Dict[str, Any]:
    try:
        return advance_initial_seat_handoff(
            workflow_session_id=workflow_session_id,
            problem_id=request.problem_id,
            seat=request.seat,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "advance_workflow_seat")) from exc


@router.post("/workflows/{workflow_session_id}/purple-decision")
async def advance_workflow_purple_decision(
    workflow_session_id: str,
    request: PurpleDecisionRequest,
) -> Dict[str, Any]:
    try:
        return advance_initial_purple_decision(
            workflow_session_id=workflow_session_id,
            problem_id=request.problem_id,
            decision_outcome=request.decision_outcome,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "advance_workflow_purple_decision")) from exc


@router.get("/problems/{problem_id}/ring-history")
async def get_problem_ring_history(problem_id: str) -> Dict[str, Any]:
    """
    Full ring history for a problem — all cycles with per-step statuses.

    Returns cycles in chronological order so operators can trace how the
    ring has evolved across multiple passes for a given problem.
    """
    try:
        db_manager = _db_manager()
        with db_manager.get_session() as session:
            problem = session.query(Problem).filter(Problem.id == uuid.UUID(problem_id)).first()
            if not problem:
                raise HTTPException(status_code=404, detail=f"Problem not found: {problem_id}")

            cycles = (
                session.query(Cycle)
                .filter(Cycle.problem_id == problem.id)
                .order_by(Cycle.cycle_number.asc())
                .all()
            )
            all_ws = (
                session.query(WorkflowSession)
                .filter(WorkflowSession.problem_id == problem.id)
                .order_by(WorkflowSession.started_at.asc())
                .all()
            )

            def _match_ws_for_cycle(cycle: Cycle, ws_list: list) -> "WorkflowSession | None":
                """Find the WS started closest to the cycle's started_at."""
                if not ws_list:
                    return None
                if not cycle.started_at:
                    return ws_list[0]
                best, best_delta = None, float("inf")
                for ws in ws_list:
                    if ws.started_at:
                        delta = abs((ws.started_at - cycle.started_at).total_seconds())
                        if delta < best_delta:
                            best, best_delta = ws, delta
                # Only accept if within 5 seconds — avoids cross-cycle false matches
                return best if best_delta < 5.0 else None

            cycle_history = []
            for cycle in cycles:
                ws = _match_ws_for_cycle(cycle, all_ws)
                steps = []
                if ws:
                    steps = [
                        {
                            "seat": s.step_type,
                            "step_name": s.step_name,
                            "step_order": s.step_order,
                            "status": s.status,
                        }
                        for s in session.query(WorkflowStep)
                        .filter(WorkflowStep.session_id == ws.id)
                        .order_by(WorkflowStep.step_order.asc())
                        .all()
                    ]
                cycle_history.append({
                    "cycle_number": cycle.cycle_number,
                    "cycle_id": str(cycle.id),
                    "status": cycle.status,
                    "started_at": cycle.started_at.isoformat() if cycle.started_at else None,
                    "completed_at": cycle.completed_at.isoformat() if cycle.completed_at else None,
                    "workflow_session_id": str(ws.id) if ws else None,
                    "workflow_session_status": ws.status if ws else None,
                    "steps": steps,
                })

            completed_count = sum(1 for c in cycle_history if c["status"] == "completed")
            return {
                "problem_id": problem_id,
                "problem_title": problem.title,
                "problem_status": problem.status,
                "total_cycles": len(cycle_history),
                "completed_cycles": completed_count,
                "cycles": cycle_history,
            }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "get_problem_ring_history")) from exc


@router.get("/cycles/{cycle_id}")
async def get_cycle(cycle_id: str) -> Dict[str, Any]:
    try:
        db_manager = _db_manager()
        with db_manager.get_session() as session:
            cycle = session.query(Cycle).filter(Cycle.id == uuid.UUID(cycle_id)).first()
            if not cycle:
                raise HTTPException(status_code=404, detail=f"Cycle not found: {cycle_id}")
            # Find the WS started closest in time to this cycle (within 5s).
            all_ws = (
                session.query(WorkflowSession)
                .filter(WorkflowSession.problem_id == cycle.problem_id)
                .order_by(WorkflowSession.started_at.asc())
                .all()
            )
            workflow_session = None
            if all_ws and cycle.started_at:
                best_delta = float("inf")
                for ws in all_ws:
                    if ws.started_at:
                        delta = abs((ws.started_at - cycle.started_at).total_seconds())
                        if delta < best_delta:
                            best_delta, workflow_session = delta, ws
                if best_delta >= 5.0:
                    workflow_session = None
            elif all_ws:
                workflow_session = all_ws[-1]
            payload = _cycle_payload(cycle, workflow_session.id if workflow_session else None)
            if workflow_session:
                steps = (
                    session.query(WorkflowStep)
                    .filter(WorkflowStep.session_id == workflow_session.id)
                    .order_by(WorkflowStep.step_order.asc())
                    .all()
                )
                payload["responses"] = [
                    {
                        "seat": step.step_type,
                        "step_name": step.step_name,
                        "status": step.status,
                        "output_data": step.output_data or {},
                    }
                    for step in steps
                ]
                payload["workflow_session_status"] = workflow_session.status
                payload["cycle_number"] = cycle.cycle_number
            return payload
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "get_cycle")) from exc


class AdvanceRequest(BaseModel):
    workflow_session_id: str
    problem_id: str


class RedAdvanceRequest(AdvanceRequest):
    result_text: str = "Compat council bootstrap completed Red inquiry handoff."


def _get_prior_step_ctx(session: Any, workflow_session_id: str, seat: str) -> str:
    """Fetch the prior seat's output_data as a JSON string for agent context."""
    step = (
        session.query(WorkflowStep)
        .filter(
            WorkflowStep.session_id == uuid.UUID(workflow_session_id),
            WorkflowStep.step_name == WORKFLOW_STEP_BY_SEAT.get(seat, f"{seat}_step"),
        )
        .first()
    )
    return json.dumps(step.output_data or {}) if step else ""


@router.post("/advance/red-handoff")
async def http_advance_red_handoff(request: RedAdvanceRequest) -> Dict[str, Any]:
    """Red Owl runs its inquiry, then the ring advances to Orange."""
    try:
        db_manager = _db_manager()
        with db_manager.get_session() as _s:
            _prob = _s.query(Problem).filter(Problem.id == uuid.UUID(request.problem_id)).first()
            _title = _prob.title if _prob else request.problem_id

        agent = await _run_seat_agent("red", _title, "")
        result_text = agent.get("result") or request.result_text

        with db_manager.get_session() as _s:
            _write_agent_result_to_step(_s, request.workflow_session_id, WORKFLOW_STEP_BY_SEAT["red"], agent)

        advance_result = advance_initial_red_handoff(
            workflow_session_id=request.workflow_session_id,
            problem_id=request.problem_id,
            result_text=result_text,
        )
        advance_result["agent_model"] = agent.get("model")
        # Sentry passed — crystallise this output as a distillation seed
        await _write_distillation_seed(
            seat="red",
            problem_id=request.problem_id,
            workflow_session_id=request.workflow_session_id,
            prompt=_title,
            response=result_text or "",
            model_used=agent.get("model") or "unknown",
        )
        return advance_result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "advance_red_handoff")) from exc


@router.post("/advance/orange-handoff")
async def http_advance_orange_handoff(request: AdvanceRequest) -> Dict[str, Any]:
    """Orange Orangutan runs its planning on Red's output, then advances to Yellow."""
    try:
        db_manager = _db_manager()
        with db_manager.get_session() as _s:
            _prob = _s.query(Problem).filter(Problem.id == uuid.UUID(request.problem_id)).first()
            _title = _prob.title if _prob else request.problem_id
            _prior_ctx = _get_prior_step_text(_s, request.workflow_session_id, "red")

        agent = await _run_seat_agent("orange", _title, _prior_ctx)

        with db_manager.get_session() as _s:
            _write_agent_result_to_step(_s, request.workflow_session_id, WORKFLOW_STEP_BY_SEAT["orange"], agent)

        advance_result = advance_initial_orange_handoff(
            workflow_session_id=request.workflow_session_id,
            problem_id=request.problem_id,
        )
        advance_result["agent_response"] = agent.get("result")
        advance_result["agent_model"] = agent.get("model")
        await _write_distillation_seed(
            seat="orange",
            problem_id=request.problem_id,
            workflow_session_id=request.workflow_session_id,
            prompt=f"{_title}\n\n{_prior_ctx}".strip(),
            response=agent.get("result") or "",
            model_used=agent.get("model") or "unknown",
        )
        return advance_result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "advance_orange_handoff")) from exc


@router.post("/advance/yellow-handoff")
async def http_advance_yellow_handoff(request: AdvanceRequest) -> Dict[str, Any]:
    """Yellow Honeybee runs its creation on Orange's plan, then advances to Green."""
    try:
        db_manager = _db_manager()
        with db_manager.get_session() as _s:
            _prob = _s.query(Problem).filter(Problem.id == uuid.UUID(request.problem_id)).first()
            _title = _prob.title if _prob else request.problem_id
            _prior_ctx = _get_prior_step_text(_s, request.workflow_session_id, "orange")

        agent = await _run_seat_agent("yellow", _title, _prior_ctx)

        with db_manager.get_session() as _s:
            _write_agent_result_to_step(_s, request.workflow_session_id, WORKFLOW_STEP_BY_SEAT["yellow"], agent)

        advance_result = advance_initial_yellow_handoff(
            workflow_session_id=request.workflow_session_id,
            problem_id=request.problem_id,
        )
        advance_result["agent_response"] = agent.get("result")
        advance_result["agent_model"] = agent.get("model")
        await _write_distillation_seed(
            seat="yellow",
            problem_id=request.problem_id,
            workflow_session_id=request.workflow_session_id,
            prompt=f"{_title}\n\n{_prior_ctx}".strip(),
            response=agent.get("result") or "",
            model_used=agent.get("model") or "unknown",
        )
        return advance_result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "advance_yellow_handoff")) from exc


@router.post("/advance/green-handoff")
async def http_advance_green_handoff(request: AdvanceRequest) -> Dict[str, Any]:
    """Green Tortoise reviews resources on Yellow's output, then advances to Blue."""
    try:
        db_manager = _db_manager()
        with db_manager.get_session() as _s:
            _prob = _s.query(Problem).filter(Problem.id == uuid.UUID(request.problem_id)).first()
            _title = _prob.title if _prob else request.problem_id
            _prior_ctx = _get_prior_step_text(_s, request.workflow_session_id, "yellow")

        agent = await _run_seat_agent("green", _title, _prior_ctx)

        with db_manager.get_session() as _s:
            _write_agent_result_to_step(_s, request.workflow_session_id, WORKFLOW_STEP_BY_SEAT["green"], agent)

        advance_result = advance_initial_green_handoff(
            workflow_session_id=request.workflow_session_id,
            problem_id=request.problem_id,
        )
        advance_result["agent_response"] = agent.get("result")
        advance_result["agent_model"] = agent.get("model")
        await _write_distillation_seed(
            seat="green",
            problem_id=request.problem_id,
            workflow_session_id=request.workflow_session_id,
            prompt=f"{_title}\n\n{_prior_ctx}".strip(),
            response=agent.get("result") or "",
            model_used=agent.get("model") or "unknown",
        )
        return advance_result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "advance_green_handoff")) from exc


@router.post("/advance/blue-handoff")
async def http_advance_blue_handoff(request: AdvanceRequest) -> Dict[str, Any]:
    """Blue Dolphin synthesises communication on Green's output, then advances to Purple."""
    try:
        db_manager = _db_manager()
        with db_manager.get_session() as _s:
            _prob = _s.query(Problem).filter(Problem.id == uuid.UUID(request.problem_id)).first()
            _title = _prob.title if _prob else request.problem_id
            _prior_ctx = _get_prior_step_text(_s, request.workflow_session_id, "green")

        agent = await _run_seat_agent("blue", _title, _prior_ctx)

        with db_manager.get_session() as _s:
            _write_agent_result_to_step(_s, request.workflow_session_id, WORKFLOW_STEP_BY_SEAT["blue"], agent)

        advance_result = advance_initial_blue_handoff(
            workflow_session_id=request.workflow_session_id,
            problem_id=request.problem_id,
        )
        advance_result["agent_response"] = agent.get("result")
        advance_result["agent_model"] = agent.get("model")
        await _write_distillation_seed(
            seat="blue",
            problem_id=request.problem_id,
            workflow_session_id=request.workflow_session_id,
            prompt=f"{_title}\n\n{_prior_ctx}".strip(),
            response=agent.get("result") or "",
            model_used=agent.get("model") or "unknown",
        )
        return advance_result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "advance_blue_handoff")) from exc


@router.post("/advance/purple-complete")
async def http_complete_purple(request: AdvanceRequest) -> Dict[str, Any]:
    """Purple Elephant witnesses the full cycle and generates WHO impact report, then closes."""
    try:
        db_manager = _db_manager()
        with db_manager.get_session() as _s:
            _prob = _s.query(Problem).filter(Problem.id == uuid.UUID(request.problem_id)).first()
            _title = _prob.title if _prob else request.problem_id
            _prior_ctx = _get_full_cascade_text(_s, request.workflow_session_id)

        agent = await _run_seat_agent("purple", _title, _prior_ctx)

        with db_manager.get_session() as _s:
            _write_agent_result_to_step(_s, request.workflow_session_id, WORKFLOW_STEP_BY_SEAT["purple"], agent)

        advance_result = complete_initial_purple_effective_solution(
            workflow_session_id=request.workflow_session_id,
            problem_id=request.problem_id,
        )
        advance_result["agent_response"] = agent.get("result")
        advance_result["agent_model"] = agent.get("model")
        # Purple completion = full ring validated — mark as gold seed
        await _write_distillation_seed(
            seat="purple",
            problem_id=request.problem_id,
            workflow_session_id=request.workflow_session_id,
            prompt=f"{_title}\n\n{_prior_ctx}".strip(),
            response=agent.get("result") or "",
            model_used=agent.get("model") or "unknown",
            is_gold=True,
        )
        return advance_result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "complete_purple")) from exc


@router.post("/advance/purple-loopback")
async def http_advance_purple_loopback(request: AdvanceRequest) -> Dict[str, Any]:
    """Purple Elephant witnesses the full cycle and generates WHO impact report, then loops back."""
    try:
        db_manager = _db_manager()
        with db_manager.get_session() as _s:
            _prob = _s.query(Problem).filter(Problem.id == uuid.UUID(request.problem_id)).first()
            _title = _prob.title if _prob else request.problem_id
            _prior_ctx = _get_full_cascade_text(_s, request.workflow_session_id)

        agent = await _run_seat_agent("purple", _title, _prior_ctx)

        with db_manager.get_session() as _s:
            _write_agent_result_to_step(_s, request.workflow_session_id, WORKFLOW_STEP_BY_SEAT["purple"], agent)

        advance_result = advance_initial_purple_loopback(
            workflow_session_id=request.workflow_session_id,
            problem_id=request.problem_id,
        )
        advance_result["agent_response"] = agent.get("result")
        advance_result["agent_model"] = agent.get("model")
        return advance_result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "advance_purple_loopback")) from exc


@router.get("/ring-status")
async def ring_status() -> Dict[str, Any]:
    """
    Single-call operator view of the active ring state.

    Reads from the active-canon binding to report:
    - Which problem/session is active
    - Current seat position
    - Per-seat step statuses for the active workflow session
    - Cycle count for the active problem
    """
    try:
        from scripts.desktop_runtime import load_active_canon
        canon = load_active_canon()
    except Exception:
        canon = {}

    problem_id = canon.get("problem_id")
    workflow_session_id = canon.get("workflow_session_id")
    current_seat = (
        canon.get("latest_iteration_seat")
        or canon.get("latest_workflow_step_type")
        or canon.get("latest_fractal_address")
    )

    seat_steps: List[Dict[str, Any]] = []
    cycle_count = 0
    problem_title = canon.get("problem_title")

    if problem_id and workflow_session_id:
        try:
            db_manager = _db_manager()
            with db_manager.get_session() as session:
                cycle_count = session.query(Cycle).filter(
                    Cycle.problem_id == uuid.UUID(problem_id)
                ).count()

                ws = session.query(WorkflowSession).filter(
                    WorkflowSession.id == uuid.UUID(workflow_session_id)
                ).first()
                if ws:
                    steps = (
                        session.query(WorkflowStep)
                        .filter(WorkflowStep.session_id == ws.id)
                        .order_by(WorkflowStep.step_order.asc())
                        .all()
                    )
                    seat_steps = [
                        {
                            "seat": s.step_type,
                            "step_name": s.step_name,
                            "step_order": s.step_order,
                            "status": s.status,
                            "is_current": s.step_type == current_seat,
                        }
                        for s in steps
                    ]
        except Exception:
            pass

    # CRONUS geometry for the current seat
    current_seat_geometry: Dict[str, Any] = {}
    if current_seat:
        try:
            from cronus.api.geometry_support import calculate_vertex_coordinates
            seat_order = ["red", "orange", "yellow", "green", "blue", "purple"]
            if current_seat in seat_order:
                seat_idx = seat_order.index(current_seat)
                level_id = seat_idx * 18 + 1
                coords = calculate_vertex_coordinates(level_id)
                current_seat_geometry = {"cronus_coords": coords, "level_id": level_id}
        except Exception:
            pass

    return {
        "success": True,
        "data": {
            "problem_id": problem_id,
            "problem_title": problem_title,
            "workflow_session_id": workflow_session_id,
            "current_seat": current_seat,
            "current_step": canon.get("latest_workflow_step_name"),
            "latest_fractal_address": canon.get("latest_fractal_address"),
            "latest_validation_stage": canon.get("latest_validation_stage"),
            "cycle_count": cycle_count,
            "seat_steps": seat_steps,
            "current_seat_geometry": current_seat_geometry,
            "binding_updated_at": canon.get("binding_updated_at"),
        },
    }


@router.post("/solve")
async def solve_problem(request: CompatProblemCreateRequest) -> Dict[str, Any]:
    try:
        db_manager = _db_manager()
        with db_manager.get_session() as session:
            problem = Problem(
                id=uuid.uuid4(),
                title=request.title,
                description=request.description,
                domain="compat_council",
                complexity="moderate",
                status="in_progress",
                priority="medium",
                impact="medium",
                urgency="cyclical",
                priority_score=0.0,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(problem)
            cycle = Cycle(
                id=uuid.uuid4(),
                problem_id=problem.id,
                cycle_number=1,
                status="running",
                started_at=datetime.now(timezone.utc),
                overall_confidence=0.0,
            )
            session.add(cycle)
            workflow_session = _create_workflow_binding(session, problem.id)
            session.commit()
            session.refresh(problem)
            session.refresh(cycle)
            session.refresh(workflow_session)
            bind_active_problem(
                problem_id=str(problem.id),
                workflow_session_id=str(workflow_session.id),
                problem_title=problem.title,
                problem_status=problem.status,
                workflow_session_status=workflow_session.status,
                workflow_current_step=workflow_session.current_step,
                source="compat_council.solve_problem",
                fractal_address=request.fractal_address,
            )
            _seed_runtime_binding_artifact(
                problem=problem,
                workflow_session=workflow_session,
                source="compat_council.solve_problem",
            )
            response = {
                "problem": _problem_payload(problem, workflow_session.id),
                "cycle": _cycle_payload(cycle, workflow_session.id),
                "source": {"runtime": "live", "storage": "db"},
            }
            if request.export_twin_earth:
                response["twin_earth_proposal"] = export_twin_earth_proposal(
                    domain=request.twin_earth_domain,  # type: ignore[arg-type]
                    intent=(
                        f"Export compat-council solve for '{request.title}' "
                        f"as a Twin Earth proposal package."
                    ),
                )
            return response
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_structured_error(exc, "solve_problem")) from exc
