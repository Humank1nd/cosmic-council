"""Think Tank runtime primitives for recursive node identity and sentry gating."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from cronus.app.council.canon_adapter import get_full_totem_profile, outer_seats

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sentry_tribunal import SentryA, SentryB, SentryC, SentryTribunal  # noqa: E402


def build_node_identity(address: str, *, node_kind: str, parent_address: str | None = None) -> dict[str, Any]:
    clean_address = str(address or "").strip().lower()
    segments = [segment for segment in clean_address.split(".") if segment]
    root_seat = segments[0] if segments else None
    current_focus = segments[-1] if segments else None
    resolved_parent = parent_address
    if resolved_parent is None and len(segments) > 1:
        resolved_parent = ".".join(segments[:-1])
    return {
        "node_kind": node_kind,
        "node_address": clean_address or "unbound",
        "parent_address": resolved_parent,
        "depth": len(segments),
        "root_seat": root_seat,
        "current_focus": current_focus,
        "segments": segments,
    }


def _red_inner_contribution(seat: str, problem_title: str, problem_description: str, loopback_reason: str | None) -> str:
    prompt = {
        "red": f"Clarify why '{problem_title}' matters now and what core cause still drives the problem.",
        "orange": f"Identify how research on '{problem_title}' should be structured before planning advances.",
        "yellow": f"Identify what concrete evidence or artifact would prove the research is sufficient.",
        "green": f"Identify when the research should stop expanding and become actionable.",
        "blue": f"Identify where the research should surface clearly for the next seat handoff.",
        "purple": f"Identify who or what memory should be preserved so the next cycle does not forget the lesson.",
    }
    if loopback_reason:
        return (
            f"{prompt[seat]} Recursive constraint: {loopback_reason} "
            f"Use the existing description '{problem_description}' as the active research boundary."
        )
    return f"{prompt[seat]} Use the description '{problem_description}' as the active research boundary."


def build_red_inner_council_payload(
    *,
    problem_title: str,
    problem_description: str,
    workflow_session_id: str,
    loopback_context: dict[str, Any] | None = None,
    source: str,
) -> dict[str, Any]:
    root_identity = build_node_identity("red", node_kind="outer_seat")
    loopback_reason = None
    if isinstance(loopback_context, dict):
        loopback_reason = str(loopback_context.get("reason") or "").strip() or None

    inner_seats: list[dict[str, Any]] = []
    research_focus: list[str] = []
    for seat in outer_seats():
        profile = get_full_totem_profile(seat)
        child_identity = build_node_identity(f"red.{seat}", node_kind="inner_seat", parent_address="red")
        contribution = _red_inner_contribution(seat, problem_title, problem_description, loopback_reason)
        inner_seats.append(
            {
                "seat": seat,
                "identity": profile.get("identity"),
                "guiding_question": profile.get("guiding_question"),
                "canonical_role": profile.get("canonical_role"),
                "node_identity": child_identity,
                "contribution": contribution,
            }
        )
        research_focus.append(contribution)

    research_summary = (
        f"Red reopened '{problem_title}' through its inner council after a recursive adjustment request."
        if loopback_reason
        else f"Red decomposed '{problem_title}' through its inner council to build a fuller research brief."
    )
    return {
        "seat": "red",
        "research_summary": research_summary,
        "research_focus": research_focus,
        "required_outputs": ["Research brief", "Clarified assumptions", "Next-seat handoff rationale"],
        "recommended_next_seat": "orange",
        "decision_outcome": "sufficient_data",
        "source": source,
        "problem_context": {
            "title": problem_title,
            "description": problem_description,
            "workflow_session_id": workflow_session_id,
        },
        "node_identity": root_identity,
        "think_tank": {
            "node_identity": build_node_identity("red", node_kind="inner_hexagon_shell"),
            "inner_council": inner_seats,
            "synthesis": {
                "child_count": len(inner_seats),
                "recursive_mode": bool(loopback_reason),
                "loopback_reason": loopback_reason,
            },
        },
        "loopback_context": loopback_context if isinstance(loopback_context, dict) and loopback_context else None,
    }


def build_orange_inner_council_payload(
    *,
    problem_title: str,
    problem_description: str,
    workflow_session_id: str,
    upstream_payload: dict[str, Any] | None,
    source: str,
) -> dict[str, Any]:
    upstream_payload = dict(upstream_payload or {})
    loopback_context = upstream_payload.get("loopback_context") if isinstance(upstream_payload, dict) else None
    research_summary = str(upstream_payload.get("research_summary") or "").strip()
    red_inner_council = ((upstream_payload.get("think_tank") or {}).get("inner_council") or []) if isinstance(upstream_payload, dict) else []
    root_identity = build_node_identity("orange", node_kind="outer_seat")

    planning_threads: list[dict[str, Any]] = []
    prioritized_tasks: list[str] = []
    for child in red_inner_council:
        if not isinstance(child, dict):
            continue
        seat = str(child.get("seat") or "").strip().lower()
        if not seat:
            continue
        profile = get_full_totem_profile(seat)
        node_identity = build_node_identity(f"orange.{seat}", node_kind="inner_seat", parent_address="orange")
        inherited = str(child.get("contribution") or "").strip()
        planning_focus = (
            f"Plan how Orange should use the Red {seat} thread: {inherited}"
            if inherited
            else f"Plan how Orange should use the {seat} research thread for execution."
        )
        planning_threads.append(
            {
                "seat": seat,
                "identity": profile.get("identity"),
                "guiding_question": profile.get("guiding_question"),
                "canonical_role": profile.get("canonical_role"),
                "node_identity": node_identity,
                "planning_focus": planning_focus,
            }
        )
        prioritized_tasks.append(planning_focus)

    sentry_observation_summary = (
        (((upstream_payload.get("sentry_tribunal") or {}).get("sentry_recursion") or {}).get("sentry_a") or {}).get("observation_summary")
        if isinstance(upstream_payload.get("sentry_tribunal"), dict)
        else None
    )
    strategy_summary = (
        f"Refine the recursive Red research for '{problem_title}' into a bounded implementation plan."
        if isinstance(loopback_context, dict) and loopback_context
        else f"Translate Red's inner-council research for '{problem_title}' into a bounded plan that can hand off to Yellow."
    )
    return {
        "seat": "orange",
        "strategy_summary": strategy_summary,
        "prioritized_tasks": prioritized_tasks or [
            f"Turn the Red research for '{problem_title}' into an actionable Yellow-ready plan."
        ],
        "contingency_plans": [
            "Loop back to Red if the plan exposes unresolved research gaps.",
            "Escalate to Green early if constraints imply a sustainability bottleneck.",
        ],
        "dependencies": [
            f"Workflow session id: {workflow_session_id}",
            f"Problem: {problem_title}",
            *([f"Red research summary: {research_summary}"] if research_summary else []),
            *([f"Sentry observation: {sentry_observation_summary}"] if sentry_observation_summary else []),
        ],
        "constraints": [
            "Stay on the Dream Caesar integration spine.",
            "Preserve the recursive provenance of the Red inner council.",
        ],
        "required_outputs": ["Roadmap", "Prioritized tasks", "Contingency plans"],
        "recommended_next_seat": "yellow",
        "decision_outcome": "feasible_plan",
        "source": source,
        "problem_context": {
            "title": problem_title,
            "description": problem_description,
            "workflow_session_id": workflow_session_id,
        },
        "upstream_research_summary": research_summary or None,
        "research_threads": [
            {
                "seat": child.get("seat"),
                "node_address": ((child.get("node_identity") or {}).get("node_address")),
                "contribution": child.get("contribution"),
            }
            for child in red_inner_council
            if isinstance(child, dict)
        ],
        "inner_council_addresses": [
            ((child.get("node_identity") or {}).get("node_address"))
            for child in red_inner_council
            if isinstance(child, dict) and ((child.get("node_identity") or {}).get("node_address"))
        ],
        "sentry_observation_summary": sentry_observation_summary,
        "node_identity": root_identity,
        "think_tank": {
            "node_identity": build_node_identity("orange", node_kind="inner_hexagon_shell"),
            "inner_council": planning_threads,
            "synthesis": {
                "child_count": len(planning_threads),
                "recursive_mode": bool(loopback_context),
                "loopback_reason": (loopback_context or {}).get("reason") if isinstance(loopback_context, dict) else None,
            },
        },
        "loopback_context": loopback_context if isinstance(loopback_context, dict) and loopback_context else None,
    }


def build_yellow_inner_council_payload(
    *,
    problem_title: str,
    problem_description: str,
    workflow_session_id: str,
    upstream_payload: dict[str, Any] | None,
    source: str,
) -> dict[str, Any]:
    upstream_payload = dict(upstream_payload or {})
    loopback_context = upstream_payload.get("loopback_context") if isinstance(upstream_payload, dict) else None
    strategy_summary = str(upstream_payload.get("strategy_summary") or "").strip()
    planning_threads = ((upstream_payload.get("think_tank") or {}).get("inner_council") or []) if isinstance(upstream_payload, dict) else []
    root_identity = build_node_identity("yellow", node_kind="outer_seat")

    development_threads: list[dict[str, Any]] = []
    prototype_artifacts: list[str] = []
    for child in planning_threads:
        if not isinstance(child, dict):
            continue
        seat = str(child.get("seat") or "").strip().lower()
        if not seat:
            continue
        profile = get_full_totem_profile(seat)
        node_identity = build_node_identity(f"yellow.{seat}", node_kind="inner_seat", parent_address="yellow")
        planning_focus = str(child.get("planning_focus") or "").strip()
        development_focus = (
            f"Turn the Orange {seat} planning thread into a concrete prototype move: {planning_focus}"
            if planning_focus
            else f"Turn the {seat} planning thread into a concrete prototype move."
        )
        development_threads.append(
            {
                "seat": seat,
                "identity": profile.get("identity"),
                "guiding_question": profile.get("guiding_question"),
                "canonical_role": profile.get("canonical_role"),
                "node_identity": node_identity,
                "development_focus": development_focus,
            }
        )
        prototype_artifacts.append(development_focus)

    sentry_observation_summary = (
        (((upstream_payload.get("sentry_tribunal") or {}).get("sentry_recursion") or {}).get("sentry_a") or {}).get("observation_summary")
        if isinstance(upstream_payload.get("sentry_tribunal"), dict)
        else None
    )
    prototype_brief = (
        f"Use Orange's recursive plan for '{problem_title}' to produce a bounded development pass that preserves the Think Tank trace."
        if isinstance(loopback_context, dict) and loopback_context
        else f"Use Orange's Think Tank plan for '{problem_title}' to produce a bounded development pass."
    )
    return {
        "seat": "yellow",
        "strategy_summary": strategy_summary,
        "prototype_brief": prototype_brief,
        "prototype_artifacts": prototype_artifacts or [
            f"Translate the Orange plan for '{problem_title}' into the first bounded implementation artifact."
        ],
        "solution_hypotheses": [
            "A prototype grounded in Orange's full planning hexagon should be strong enough for Green review.",
            "Preserving sentry observations in the development pass should reduce handoff ambiguity.",
        ],
        "implementation_notes": [
            f"Workflow session id: {workflow_session_id}",
            "Preserve canon alignment and recursive provenance.",
            *([f"Sentry observation: {sentry_observation_summary}"] if sentry_observation_summary else []),
        ],
        "recommended_next_seat": "green",
        "decision_outcome": "viable_solution",
        "source": source,
        "problem_context": {
            "title": problem_title,
            "description": problem_description,
            "workflow_session_id": workflow_session_id,
        },
        "upstream_decision_outcome": str(upstream_payload.get("decision_outcome") or ""),
        "upstream_research_summary": upstream_payload.get("upstream_research_summary"),
        "planning_threads": [
            {
                "seat": child.get("seat"),
                "node_address": ((child.get("node_identity") or {}).get("node_address")),
                "planning_focus": child.get("planning_focus"),
            }
            for child in planning_threads
            if isinstance(child, dict)
        ],
        "sentry_observation_summary": sentry_observation_summary,
        "node_identity": root_identity,
        "think_tank": {
            "node_identity": build_node_identity("yellow", node_kind="inner_hexagon_shell"),
            "inner_council": development_threads,
            "synthesis": {
                "child_count": len(development_threads),
                "recursive_mode": bool(loopback_context),
                "loopback_reason": (loopback_context or {}).get("reason") if isinstance(loopback_context, dict) else None,
            },
        },
        "loopback_context": loopback_context if isinstance(loopback_context, dict) and loopback_context else None,
    }


def build_green_inner_council_payload(
    *,
    problem_title: str,
    problem_description: str,
    workflow_session_id: str,
    upstream_payload: dict[str, Any] | None,
    source: str,
) -> dict[str, Any]:
    upstream_payload = dict(upstream_payload or {})
    loopback_context = upstream_payload.get("loopback_context") if isinstance(upstream_payload, dict) else None
    prototype_brief = str(upstream_payload.get("prototype_brief") or "").strip()
    development_threads = ((upstream_payload.get("think_tank") or {}).get("inner_council") or []) if isinstance(upstream_payload, dict) else []
    root_identity = build_node_identity("green", node_kind="outer_seat")

    resource_threads: list[dict[str, Any]] = []
    budget_focus: list[str] = []
    for child in development_threads:
        if not isinstance(child, dict):
            continue
        seat = str(child.get("seat") or "").strip().lower()
        if not seat:
            continue
        profile = get_full_totem_profile(seat)
        node_identity = build_node_identity(f"green.{seat}", node_kind="inner_seat", parent_address="green")
        development_focus = str(child.get("development_focus") or "").strip()
        resource_focus = (
            f"Evaluate the resource cost and sustainability of the Yellow {seat} development thread: {development_focus}"
            if development_focus
            else f"Evaluate the resource cost and sustainability of the {seat} development thread."
        )
        resource_threads.append(
            {
                "seat": seat,
                "identity": profile.get("identity"),
                "guiding_question": profile.get("guiding_question"),
                "canonical_role": profile.get("canonical_role"),
                "node_identity": node_identity,
                "resource_focus": resource_focus,
            }
        )
        budget_focus.append(resource_focus)

    sentry_observation_summary = (
        (((upstream_payload.get("sentry_tribunal") or {}).get("sentry_recursion") or {}).get("sentry_a") or {}).get("observation_summary")
        if isinstance(upstream_payload.get("sentry_tribunal"), dict)
        else None
    )
    return {
        "seat": "green",
        "resource_summary": (
            f"Review Yellow's Think Tank development pass for '{problem_title}' against sustainability, effort, and timing constraints."
        ),
        "budget_focus": budget_focus or [
            f"Evaluate whether the Yellow prototype for '{problem_title}' is sustainable enough to move into Blue."
        ],
        "timeline_assumptions": [
            f"Workflow session id: {workflow_session_id}",
            "The current prototype slice should be small enough for immediate communication review if resources align.",
            *([f"Sentry observation: {sentry_observation_summary}"] if sentry_observation_summary else []),
        ],
        "recommended_next_seat": "blue",
        "decision_outcome": "resources_aligned",
        "source": source,
        "problem_context": {
            "title": problem_title,
            "description": problem_description,
            "workflow_session_id": workflow_session_id,
        },
        "upstream_decision_outcome": str(upstream_payload.get("decision_outcome") or ""),
        "prototype_brief": prototype_brief or None,
        "upstream_research_summary": upstream_payload.get("upstream_research_summary"),
        "development_threads": [
            {
                "seat": child.get("seat"),
                "node_address": ((child.get("node_identity") or {}).get("node_address")),
                "development_focus": child.get("development_focus"),
            }
            for child in development_threads
            if isinstance(child, dict)
        ],
        "sentry_observation_summary": sentry_observation_summary,
        "node_identity": root_identity,
        "think_tank": {
            "node_identity": build_node_identity("green", node_kind="inner_hexagon_shell"),
            "inner_council": resource_threads,
            "synthesis": {
                "child_count": len(resource_threads),
                "recursive_mode": bool(loopback_context),
                "loopback_reason": (loopback_context or {}).get("reason") if isinstance(loopback_context, dict) else None,
            },
        },
        "loopback_context": loopback_context if isinstance(loopback_context, dict) and loopback_context else None,
    }


def build_blue_inner_council_payload(
    *,
    problem_title: str,
    problem_description: str,
    workflow_session_id: str,
    upstream_payload: dict[str, Any] | None,
    source: str,
) -> dict[str, Any]:
    upstream_payload = dict(upstream_payload or {})
    loopback_context = upstream_payload.get("loopback_context") if isinstance(upstream_payload, dict) else None
    resource_summary = str(upstream_payload.get("resource_summary") or "").strip()
    resource_threads = ((upstream_payload.get("think_tank") or {}).get("inner_council") or []) if isinstance(upstream_payload, dict) else []
    root_identity = build_node_identity("blue", node_kind="outer_seat")

    communication_threads: list[dict[str, Any]] = []
    delivery_assets: list[str] = []
    for child in resource_threads:
        if not isinstance(child, dict):
            continue
        seat = str(child.get("seat") or "").strip().lower()
        if not seat:
            continue
        profile = get_full_totem_profile(seat)
        node_identity = build_node_identity(f"blue.{seat}", node_kind="inner_seat", parent_address="blue")
        resource_focus = str(child.get("resource_focus") or "").strip()
        communication_focus = (
            f"Translate the Green {seat} resource thread into a clear communication move: {resource_focus}"
            if resource_focus
            else f"Translate the {seat} resource thread into a clear communication move."
        )
        communication_threads.append(
            {
                "seat": seat,
                "identity": profile.get("identity"),
                "guiding_question": profile.get("guiding_question"),
                "canonical_role": profile.get("canonical_role"),
                "node_identity": node_identity,
                "communication_focus": communication_focus,
            }
        )
        delivery_assets.append(communication_focus)

    sentry_observation_summary = (
        (((upstream_payload.get("sentry_tribunal") or {}).get("sentry_recursion") or {}).get("sentry_a") or {}).get("observation_summary")
        if isinstance(upstream_payload.get("sentry_tribunal"), dict)
        else None
    )
    return {
        "seat": "blue",
        "message_summary": f"Translate Green's resource-aligned path for '{problem_title}' into a clear operator-facing communication package.",
        "audience_targets": [
            "Operator",
            "Dream Caesar runtime surfaces",
            "Purple reflection as downstream validator",
        ],
        "delivery_assets": delivery_assets or [
            f"Summarize why the resource-aligned path for '{problem_title}' is ready for reflection."
        ],
        "recommended_next_seat": "purple",
        "decision_outcome": "communication_effective",
        "source": source,
        "problem_context": {
            "title": problem_title,
            "description": problem_description,
            "workflow_session_id": workflow_session_id,
        },
        "upstream_decision_outcome": str(upstream_payload.get("decision_outcome") or ""),
        "resource_summary": resource_summary or None,
        "upstream_research_summary": upstream_payload.get("upstream_research_summary"),
        "resource_threads": [
            {
                "seat": child.get("seat"),
                "node_address": ((child.get("node_identity") or {}).get("node_address")),
                "resource_focus": child.get("resource_focus"),
            }
            for child in resource_threads
            if isinstance(child, dict)
        ],
        "sentry_observation_summary": sentry_observation_summary,
        "node_identity": root_identity,
        "think_tank": {
            "node_identity": build_node_identity("blue", node_kind="inner_hexagon_shell"),
            "inner_council": communication_threads,
            "synthesis": {
                "child_count": len(communication_threads),
                "recursive_mode": bool(loopback_context),
                "loopback_reason": (loopback_context or {}).get("reason") if isinstance(loopback_context, dict) else None,
            },
        },
        "loopback_context": loopback_context if isinstance(loopback_context, dict) and loopback_context else None,
    }


def build_purple_inner_council_payload(
    *,
    problem_title: str,
    problem_description: str,
    workflow_session_id: str,
    upstream_payload: dict[str, Any] | None,
    source: str,
) -> dict[str, Any]:
    upstream_payload = dict(upstream_payload or {})
    loopback_context = upstream_payload.get("loopback_context") if isinstance(upstream_payload, dict) else None
    message_summary = str(upstream_payload.get("message_summary") or "").strip()
    communication_threads = ((upstream_payload.get("think_tank") or {}).get("inner_council") or []) if isinstance(upstream_payload, dict) else []
    root_identity = build_node_identity("purple", node_kind="outer_seat")

    reflection_threads: list[dict[str, Any]] = []
    lessons_learned: list[str] = []
    adjustment_vectors: list[str] = []
    for child in communication_threads:
        if not isinstance(child, dict):
            continue
        seat = str(child.get("seat") or "").strip().lower()
        if not seat:
            continue
        profile = get_full_totem_profile(seat)
        node_identity = build_node_identity(f"purple.{seat}", node_kind="inner_seat", parent_address="purple")
        communication_focus = str(child.get("communication_focus") or "").strip()
        reflection_focus = (
            f"Reflect on the Blue {seat} communication thread and judge whether it resolves the cycle: {communication_focus}"
            if communication_focus
            else f"Reflect on the {seat} communication thread and judge whether it resolves the cycle."
        )
        reflection_threads.append(
            {
                "seat": seat,
                "identity": profile.get("identity"),
                "guiding_question": profile.get("guiding_question"),
                "canonical_role": profile.get("canonical_role"),
                "node_identity": node_identity,
                "reflection_focus": reflection_focus,
            }
        )
        lessons_learned.append(reflection_focus)
        adjustment_vectors.append(
            f"Reopen {seat} only if Purple finds that this communication thread still leaves unresolved impact."
        )

    sentry_observation_summary = (
        (((upstream_payload.get("sentry_tribunal") or {}).get("sentry_recursion") or {}).get("sentry_a") or {}).get("observation_summary")
        if isinstance(upstream_payload.get("sentry_tribunal"), dict)
        else None
    )
    return {
        "seat": "purple",
        "reflection_summary": (
            f"Generate a WHO impact report for '{problem_title}': identify every living being affected by the full cycle — "
            "humans, animals, plants, fungi, characters — surface positive impacts, negative consequences, and new problems that emerge."
        ),
        "lessons_learned": lessons_learned or [
            f"Purple witnessed the full cycle for '{problem_title}' and delivered a WHO impact report. Cycle fate is determined by the sentry tribunal."
        ],
        "adjustment_vectors": adjustment_vectors or [
            "Surface any new problems that emerge from consequences — these will feed back into DreamFS for future cycles."
        ],
        "recommended_next_seat": "red",
        "decision_outcome": "effective_solution",
        "source": source,
        "problem_context": {
            "title": problem_title,
            "description": problem_description,
            "workflow_session_id": workflow_session_id,
        },
        "upstream_decision_outcome": str(upstream_payload.get("decision_outcome") or ""),
        "message_summary": message_summary or None,
        "upstream_research_summary": upstream_payload.get("upstream_research_summary"),
        "communication_threads": [
            {
                "seat": child.get("seat"),
                "node_address": ((child.get("node_identity") or {}).get("node_address")),
                "communication_focus": child.get("communication_focus"),
            }
            for child in communication_threads
            if isinstance(child, dict)
        ],
        "sentry_observation_summary": sentry_observation_summary,
        "node_identity": root_identity,
        "think_tank": {
            "node_identity": build_node_identity("purple", node_kind="inner_hexagon_shell"),
            "inner_council": reflection_threads,
            "synthesis": {
                "child_count": len(reflection_threads),
                "recursive_mode": bool(loopback_context),
                "loopback_reason": (loopback_context or {}).get("reason") if isinstance(loopback_context, dict) else None,
            },
        },
        "loopback_context": loopback_context if isinstance(loopback_context, dict) and loopback_context else None,
    }


def run_outer_sentry_gate(
    *,
    seat: str,
    output_payload: dict[str, Any],
    mission: str,
    workflow_session_id: str,
    expected_keys: list[str] | None = None,
    auto_recover_sentry_a: bool = True,
    auto_recover_sentry_b: bool = True,
    auto_recover_sentry_c: bool = True,
) -> dict[str, Any]:
    runtime_root = Path(
        os.environ.get(
            "DREAM_CAESAR_DESKTOP_COUNCIL_ROOT",
            REPO_ROOT / "docs" / "runtime" / "desktop-council",
        )
    ).resolve()
    state_dir = runtime_root / "artifacts" / "sentry-tribunal"
    state_dir.mkdir(parents=True, exist_ok=True)
    tribunal = SentryTribunal(state_path=state_dir / f"{workflow_session_id}.json")
    expected_form = {"required_keys": expected_keys or ["research_summary", "research_focus", "think_tank", "node_identity"]}
    verdict = tribunal.validate_level(seat=seat, level=1, output=output_payload, mission=mission, expected_form=expected_form)
    verdict_dict = verdict.to_dict()
    final_verdict = str(verdict_dict.get("final_verdict") or "").lower()
    inner_council = ((output_payload.get("think_tank") or {}).get("inner_council") or []) if isinstance(output_payload, dict) else []
    sentry_a = SentryA()
    sentry_b = SentryB()
    sentry_c = SentryC()
    sacred_question = SentryTribunal.SEAT_QUESTIONS.get(seat, "")
    max_level = SentryTribunal.SEAT_LEVELS.get(seat, 1)
    sentry_a_recursive_results = []
    sentry_b_recursive_results = []
    sentry_c_recursive_results = []
    for child in inner_council:
        if not isinstance(child, dict) or not child.get("seat"):
            continue
        child_focus = (
            child.get("contribution")
            or child.get("planning_focus")
            or child.get("development_focus")
            or child.get("resource_focus")
            or child.get("communication_focus")
            or child.get("reflection_focus")
        )
        focus_keys = [
            key
            for key in (
                "contribution",
                "planning_focus",
                "development_focus",
                "resource_focus",
                "communication_focus",
                "reflection_focus",
            )
            if child.get(key) is not None
        ]
        child_expected_keys = ["seat", "node_identity", *(focus_keys[:1] or ["contribution"])]
        child_result = sentry_a.observe(
            child,
            expected_form={"required_keys": child_expected_keys},
            mission=f"{mission} Inner sentry observation focus: {child_focus or child.get('seat')}",
        )
        analysis_result = sentry_b.analyze(
            child,
            sacred_question=sacred_question,
            mission=f"{mission} Inner sentry analysis focus: {child_focus or child.get('seat')}",
            observation_result=child_result,
        )
        conclusion_result = sentry_c.conclude(
            child_result,
            analysis_result,
            level=1,
            max_level=max_level,
        )
        sentry_a_recursive_results.append(
            {
                "seat": child.get("seat"),
                "node_identity": child.get("node_identity"),
                "verdict": child_result.verdict.value.lower(),
                "observations": child_result.observations,
                "realignment_vector": child_result.realignment_vector,
            }
        )
        sentry_b_recursive_results.append(
            {
                "seat": child.get("seat"),
                "node_identity": child.get("node_identity"),
                "verdict": analysis_result.verdict.value.lower(),
                "observations": analysis_result.observations,
                "realignment_vector": analysis_result.realignment_vector,
            }
        )
        sentry_c_recursive_results.append(
            {
                "seat": child.get("seat"),
                "node_identity": child.get("node_identity"),
                "verdict": conclusion_result.verdict.value.lower(),
                "observations": conclusion_result.observations,
                "realignment_vector": conclusion_result.realignment_vector,
            }
        )
    recursive_pass_count = sum(1 for result in sentry_a_recursive_results if result["verdict"] == "pass")
    recursive_analysis_pass_count = sum(1 for result in sentry_b_recursive_results if result["verdict"] == "pass")
    recursive_conclusion_pass_count = sum(1 for result in sentry_c_recursive_results if result["verdict"] == "pass")
    sentry_a_fail_count = len(sentry_a_recursive_results) - recursive_pass_count
    sentry_b_fail_count = len(sentry_b_recursive_results) - recursive_analysis_pass_count
    sentry_c_fail_count = len(sentry_c_recursive_results) - recursive_conclusion_pass_count
    sentry_a_recursion = {
        "node_identity": build_node_identity(f"{seat}.sentry_a", node_kind="sentry_triangle", parent_address=seat),
        "inner_hexagon": [
            {
                "node_identity": build_node_identity(f"{seat}.sentry_a.{child.get('seat')}", node_kind="sentry_inner_seat", parent_address=f"{seat}.sentry_a"),
                "seat": child.get("seat"),
                "observation_focus": (
                    child.get("contribution")
                    or child.get("planning_focus")
                    or child.get("development_focus")
                    or child.get("resource_focus")
                    or child.get("communication_focus")
                    or child.get("reflection_focus")
                ),
            }
            for child in inner_council
            if isinstance(child, dict) and child.get("seat")
        ],
        "recursive_validation": sentry_a_recursive_results,
        "observation_pass_count": recursive_pass_count,
        "observation_fail_count": sentry_a_fail_count,
        "observation_summary": (
            f"Sentry A recursively observed {len(inner_council)} inner-council contributions and passed {recursive_pass_count} before authorizing {seat.title()} level 1."
        ),
    }
    sentry_b_recursion = {
        "node_identity": build_node_identity(f"{seat}.sentry_b", node_kind="sentry_triangle", parent_address=seat),
        "recursive_validation": sentry_b_recursive_results,
        "analysis_pass_count": recursive_analysis_pass_count,
        "analysis_fail_count": sentry_b_fail_count,
        "analysis_summary": (
            f"Sentry B recursively analyzed {len(inner_council)} inner-council contributions and passed {recursive_analysis_pass_count} at {seat.title()} level 1."
        ),
    }
    sentry_c_recursion = {
        "node_identity": build_node_identity(f"{seat}.sentry_c", node_kind="sentry_triangle", parent_address=seat),
        "recursive_validation": sentry_c_recursive_results,
        "conclusion_pass_count": recursive_conclusion_pass_count,
        "conclusion_fail_count": sentry_c_fail_count,
        "conclusion_summary": (
            f"Sentry C recursively concluded {len(inner_council)} inner-council contributions and passed {recursive_conclusion_pass_count} at {seat.title()} level 1."
        ),
    }
    recursive_redirect_address = None
    recursive_realignment_vector = None
    recursive_recovery_plan = None
    if sentry_a_fail_count:
        recursive_redirect_address = f"{seat}.sentry_a"
        recursive_realignment_vector = "Resolve sentry A recursive observation failures before level advancement."
        failing_results = [result for result in sentry_a_recursive_results if result["verdict"] == "fail"]
        recursive_recovery_plan = {
            "owner": recursive_redirect_address,
            "mode": "recursive_observation_repair",
            "steps": [
                {
                    "seat": result["seat"],
                    "node_address": ((result.get("node_identity") or {}).get("node_address")),
                    "action": "Restore the missing or malformed child output so Sentry A can observe it cleanly.",
                    "observations": result["observations"],
                    "realignment_vector": result["realignment_vector"],
                }
                for result in failing_results
            ],
        }
    elif sentry_b_fail_count:
        recursive_redirect_address = f"{seat}.sentry_b"
        recursive_realignment_vector = "Resolve sentry B recursive analysis failures before level advancement."
        failing_results = [result for result in sentry_b_recursive_results if result["verdict"] == "fail"]
        recursive_recovery_plan = {
            "owner": recursive_redirect_address,
            "mode": "recursive_analysis_repair",
            "steps": [
                {
                    "seat": result["seat"],
                    "node_address": ((result.get("node_identity") or {}).get("node_address")),
                    "action": "Realign the child output to the seat mission and sacred question before retrying.",
                    "observations": result["observations"],
                    "realignment_vector": result["realignment_vector"],
                }
                for result in failing_results
            ],
        }
    elif sentry_c_fail_count:
        recursive_redirect_address = f"{seat}.sentry_c"
        recursive_realignment_vector = "Resolve sentry C recursive conclusion failures before level advancement."
        failing_results = [result for result in sentry_c_recursive_results if result["verdict"] == "fail"]
        recursive_recovery_plan = {
            "owner": recursive_redirect_address,
            "mode": "recursive_conclusion_repair",
            "steps": [
                {
                    "seat": result["seat"],
                    "node_address": ((result.get("node_identity") or {}).get("node_address")),
                    "action": "Resolve the blocking observation/analysis issues so Sentry C can authorize advancement.",
                    "observations": result["observations"],
                    "realignment_vector": result["realignment_vector"],
                }
                for result in failing_results
            ],
        }
    effective_verdict = "pass" if final_verdict == "pass" else "fail" if final_verdict == "fail" else "pending"
    if recursive_redirect_address:
        effective_verdict = "fail"
    gate_payload = {
        "overall_verdict": effective_verdict,
        "express_eligible": bool(verdict_dict.get("express_eligible")) and not recursive_redirect_address,
        "redirect_address": recursive_redirect_address or (None if final_verdict == "pass" else f"{seat}.sentry_c"),
        "realignment_vector": recursive_realignment_vector or tribunal.get_realignment_vector(),
        "sequence_info": {
            "validated_level": 1,
            "max_level": SentryTribunal.SEAT_LEVELS.get(seat),
            "total_depth": 1,
        },
        "recursive_gate": {
            "passed": recursive_redirect_address is None,
            "redirect_address": recursive_redirect_address,
            "realignment_vector": recursive_realignment_vector,
            "recovery_plan": recursive_recovery_plan,
        },
        "sentry_recursion": {
            "sentry_a": sentry_a_recursion,
            "sentry_b": sentry_b_recursion,
            "sentry_c": sentry_c_recursion,
        },
        "verdict": verdict_dict,
    }
    if auto_recover_sentry_a and recursive_redirect_address == f"{seat}.sentry_a" and recursive_recovery_plan:
        recovery_attempt = run_sentry_a_recovery(
            seat=seat,
            output_payload=output_payload,
            mission=mission,
            workflow_session_id=workflow_session_id,
            expected_keys=expected_keys,
        )
        recovered_gate = dict(recovery_attempt["recovery_verdict"])
        recovered_gate["recovery_attempt"] = {
            "owner": recursive_redirect_address,
            "triggered": True,
            "mode": "auto_sentry_a_recovery",
            "result": "recovered" if recovered_gate.get("overall_verdict") == "pass" else "still_blocked",
        }
        recovered_gate["repaired_payload"] = recovery_attempt["repaired_payload"]
        return recovered_gate
    if auto_recover_sentry_b and recursive_redirect_address == f"{seat}.sentry_b" and recursive_recovery_plan:
        recovery_attempt = run_sentry_b_recovery(
            seat=seat,
            output_payload=output_payload,
            mission=mission,
            workflow_session_id=workflow_session_id,
            expected_keys=expected_keys,
        )
        recovered_gate = dict(recovery_attempt["recovery_verdict"])
        recovered_gate["recovery_attempt"] = {
            "owner": recursive_redirect_address,
            "triggered": True,
            "mode": "auto_sentry_b_recovery",
            "result": "recovered" if recovered_gate.get("overall_verdict") == "pass" else "still_blocked",
        }
        recovered_gate["repaired_payload"] = recovery_attempt["repaired_payload"]
        return recovered_gate
    if auto_recover_sentry_c and recursive_redirect_address == f"{seat}.sentry_c" and recursive_recovery_plan:
        recovery_attempt = run_sentry_c_recovery(
            seat=seat,
            output_payload=output_payload,
            mission=mission,
            workflow_session_id=workflow_session_id,
            expected_keys=expected_keys,
        )
        recovered_gate = dict(recovery_attempt["recovery_verdict"])
        recovered_gate["recovery_attempt"] = {
            "owner": recursive_redirect_address,
            "triggered": True,
            "mode": "auto_sentry_c_recovery",
            "result": "recovered" if recovered_gate.get("overall_verdict") == "pass" else "still_blocked",
        }
        recovered_gate["repaired_payload"] = recovery_attempt["repaired_payload"]
        return recovered_gate
    return gate_payload


def run_sentry_a_recovery(
    *,
    seat: str,
    output_payload: dict[str, Any],
    mission: str,
    workflow_session_id: str,
    expected_keys: list[str] | None = None,
) -> dict[str, Any]:
    repaired_payload = dict(output_payload or {})
    think_tank = dict((repaired_payload.get("think_tank") or {}))
    inner_council = [dict(child) for child in ((think_tank.get("inner_council") or [])) if isinstance(child, dict)]
    for child in inner_council:
        focus_keys = (
            "contribution",
            "planning_focus",
            "development_focus",
            "resource_focus",
            "communication_focus",
            "reflection_focus",
        )
        if any(child.get(key) is not None for key in focus_keys):
            continue
        child_seat = str(child.get("seat") or "unknown").strip().lower() or "unknown"
        node_address = ((child.get("node_identity") or {}).get("node_address")) or f"{seat}.{child_seat}"
        child["contribution"] = (
            f"Sentry A recovery restored the missing child output for {node_address} so recursive observation can proceed."
        )
    think_tank["inner_council"] = inner_council
    repaired_payload["think_tank"] = think_tank
    repaired_payload.setdefault("sentry_recovery", {})
    repaired_payload["sentry_recovery"]["sentry_a"] = {
        "repaired": True,
        "repaired_children": [child.get("seat") for child in inner_council],
        "source": "run_sentry_a_recovery",
    }
    recovery_verdict = run_outer_sentry_gate(
        seat=seat,
        output_payload=repaired_payload,
        mission=mission,
        workflow_session_id=workflow_session_id,
        expected_keys=expected_keys,
    )
    return {
        "repaired_payload": repaired_payload,
        "recovery_verdict": recovery_verdict,
    }


def run_sentry_b_recovery(
    *,
    seat: str,
    output_payload: dict[str, Any],
    mission: str,
    workflow_session_id: str,
    expected_keys: list[str] | None = None,
) -> dict[str, Any]:
    repaired_payload = dict(output_payload or {})
    think_tank = dict((repaired_payload.get("think_tank") or {}))
    inner_council = [dict(child) for child in ((think_tank.get("inner_council") or [])) if isinstance(child, dict)]
    sacred_question = SentryTribunal.SEAT_QUESTIONS.get(seat, "")
    sacred_hint_map = {
        "WHY": "reason",
        "HOW": "strategy",
        "WHAT": "create",
        "WHEN": "timing",
        "WHERE": "channel",
        "WHO": "owner",
    }
    sacred_hint = sacred_hint_map.get(str(sacred_question or "").upper(), "mission")
    for child in inner_council:
        focus_key = next(
            (
                key
                for key in (
                    "contribution",
                    "planning_focus",
                    "development_focus",
                    "resource_focus",
                    "communication_focus",
                    "reflection_focus",
                )
                if child.get(key) is not None
            ),
            None,
        )
        if not focus_key:
            continue
        focus_value = str(child.get(focus_key) or "").strip()
        normalized_focus = focus_value
        for term in SentryB.QUANTUM_EXPLICIT_TERMS:
            normalized_focus = normalized_focus.replace(term, "implicit-pattern")
            normalized_focus = normalized_focus.replace(term.title(), "implicit-pattern")
        if sacred_hint in focus_value.lower():
            child[focus_key] = normalized_focus
            continue
        child[focus_key] = (
            f"{normalized_focus} Explicit {sacred_question} alignment: clarify the {sacred_hint} before advancement."
        )
    think_tank["inner_council"] = inner_council
    repaired_payload["think_tank"] = think_tank
    repaired_payload.setdefault("sentry_recovery", {})
    repaired_payload["sentry_recovery"]["sentry_b"] = {
        "repaired": True,
        "repaired_children": [child.get("seat") for child in inner_council],
        "source": "run_sentry_b_recovery",
        "sacred_question": sacred_question,
    }
    recovery_verdict = run_outer_sentry_gate(
        seat=seat,
        output_payload=repaired_payload,
        mission=mission,
        workflow_session_id=workflow_session_id,
        expected_keys=expected_keys,
        auto_recover_sentry_b=False,
    )
    return {
        "repaired_payload": repaired_payload,
        "recovery_verdict": recovery_verdict,
    }


def run_sentry_c_recovery(
    *,
    seat: str,
    output_payload: dict[str, Any],
    mission: str,
    workflow_session_id: str,
    expected_keys: list[str] | None = None,
) -> dict[str, Any]:
    repaired_payload = dict(output_payload or {})
    think_tank = dict((repaired_payload.get("think_tank") or {}))
    inner_council = [dict(child) for child in ((think_tank.get("inner_council") or [])) if isinstance(child, dict)]
    for child in inner_council:
        focus_key = next(
            (
                key
                for key in (
                    "contribution",
                    "planning_focus",
                    "development_focus",
                    "resource_focus",
                    "communication_focus",
                    "reflection_focus",
                )
                if child.get(key) is not None
            ),
            None,
        )
        if not focus_key:
            continue
        focus_value = str(child.get(focus_key) or "").strip()
        if "level advancement authorized after repair" in focus_value.lower():
            continue
        child[focus_key] = f"{focus_value} Level advancement authorized after repair."
    think_tank["inner_council"] = inner_council
    repaired_payload["think_tank"] = think_tank
    repaired_payload.setdefault("sentry_recovery", {})
    repaired_payload["sentry_recovery"]["sentry_c"] = {
        "repaired": True,
        "repaired_children": [child.get("seat") for child in inner_council],
        "source": "run_sentry_c_recovery",
    }
    recovery_verdict = run_outer_sentry_gate(
        seat=seat,
        output_payload=repaired_payload,
        mission=mission,
        workflow_session_id=workflow_session_id,
        expected_keys=expected_keys,
        auto_recover_sentry_c=False,
    )
    return {
        "repaired_payload": repaired_payload,
        "recovery_verdict": recovery_verdict,
    }


class ThinkTankRuntime:
    """Minimal runtime orchestrator for canon-faithful Think Tank seat execution."""

    def __init__(self, *, source: str) -> None:
        self.source = source

    def run_seat(
        self,
        *,
        seat: str,
        problem_title: str,
        problem_description: str,
        workflow_session_id: str,
        loopback_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_seat = str(seat or "").strip().lower()
        if normalized_seat == "red":
            payload = build_red_inner_council_payload(
                problem_title=problem_title,
                problem_description=problem_description,
                workflow_session_id=workflow_session_id,
                loopback_context=loopback_context,
                source=self.source,
            )
            mission = (
                f"Research why '{problem_title}' exists in its current form and produce a canon-aligned handoff "
                "to Orange only when sufficient data exists."
            )
            expected_keys = ["research_summary", "research_focus", "think_tank", "node_identity"]
        elif normalized_seat == "orange":
            payload = build_orange_inner_council_payload(
                problem_title=problem_title,
                problem_description=problem_description,
                workflow_session_id=workflow_session_id,
                upstream_payload=loopback_context,
                source=self.source,
            )
            mission = (
                f"Plan how '{problem_title}' should move from research into execution and hand off to Yellow only "
                "when the roadmap, tasks, and contingencies are coherent."
            )
            expected_keys = ["strategy_summary", "prioritized_tasks", "contingency_plans", "think_tank", "node_identity"]
        elif normalized_seat == "yellow":
            payload = build_yellow_inner_council_payload(
                problem_title=problem_title,
                problem_description=problem_description,
                workflow_session_id=workflow_session_id,
                upstream_payload=loopback_context,
                source=self.source,
            )
            mission = (
                f"Develop how '{problem_title}' should move from plan into prototype and hand off to Green only "
                "when the implementation brief and artifacts are coherent."
            )
            expected_keys = ["prototype_brief", "prototype_artifacts", "solution_hypotheses", "think_tank", "node_identity"]
        elif normalized_seat == "green":
            payload = build_green_inner_council_payload(
                problem_title=problem_title,
                problem_description=problem_description,
                workflow_session_id=workflow_session_id,
                upstream_payload=loopback_context,
                source=self.source,
            )
            mission = (
                f"Review whether '{problem_title}' is resourced and sustainable enough to move from development into communication."
            )
            expected_keys = ["resource_summary", "budget_focus", "timeline_assumptions", "think_tank", "node_identity"]
        elif normalized_seat == "blue":
            payload = build_blue_inner_council_payload(
                problem_title=problem_title,
                problem_description=problem_description,
                workflow_session_id=workflow_session_id,
                upstream_payload=loopback_context,
                source=self.source,
            )
            mission = (
                f"Communicate whether '{problem_title}' is clear and coherent enough to move from resource review into reflection."
            )
            expected_keys = ["message_summary", "audience_targets", "delivery_assets", "think_tank", "node_identity"]
        elif normalized_seat == "purple":
            payload = build_purple_inner_council_payload(
                problem_title=problem_title,
                problem_description=problem_description,
                workflow_session_id=workflow_session_id,
                upstream_payload=loopback_context,
                source=self.source,
            )
            mission = (
                f"Reflect on whether '{problem_title}' is coherent and complete enough to close, or whether it must recurse."
            )
            expected_keys = ["reflection_summary", "lessons_learned", "adjustment_vectors", "think_tank", "node_identity"]
        else:
            raise NotImplementedError(f"ThinkTankRuntime currently supports only Red, Orange, Yellow, Green, Blue, and Purple, not {normalized_seat!r}.")

        payload["orchestrator"] = {
            "runtime": "ThinkTankRuntime",
            "seat": normalized_seat,
            "mode": "inner_council_plus_outer_sentry",
        }
        payload["sentry_tribunal"] = run_outer_sentry_gate(
            seat=normalized_seat,
            output_payload=payload,
            mission=mission,
            workflow_session_id=workflow_session_id,
            expected_keys=expected_keys,
        )
        return payload
