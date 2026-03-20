from __future__ import annotations

from importlib import import_module

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..api.compat_council import CompatProblemCreateRequest, solve_problem
from ..integrations.e8_bridge import get_e8_bridge_status
from ..integrations.twin_earth_bridge import twin_earth_artifact_dir


router = APIRouter(prefix="/api/v1/integration", tags=["Integration Spine"])

# ROYGBV order — matches cosmic_canon.ROYGBV_ORDER
_SEAT_ORDER = ["red", "orange", "yellow", "green", "blue", "purple"]

# Canonical seat identities aligned to cosmic_canon.py
_SEAT_CANON: dict = {
    "red":    {"totem": "Red Owl",         "role": "Inquiry & Research",              "quantum": "Entanglement",        "chakra": "Muladhara"},
    "orange": {"totem": "Orange Orangutan","role": "Strategy & Planning",             "quantum": "Tunneling",           "chakra": "Svadisthana"},
    "yellow": {"totem": "Yellow Honeybee", "role": "Creation & Innovation",           "quantum": "Superposition",       "chakra": "Manipura"},
    "green":  {"totem": "Green Tortoise",  "role": "Resource Management",             "quantum": "Teleportation",       "chakra": "Anahata"},
    "blue":   {"totem": "Blue Dolphin",    "role": "Communication & Influence",       "quantum": "Wave-Particle Duality","chakra": "Vishuddha"},
    "purple": {"totem": "Purple Elephant", "role": "Reflection & Ethics",             "quantum": "Field Theory",        "chakra": "Ajna"},
}


def _projects_hub_module():
    return import_module("cosmic_council.integrations.project_implementation_hub")


def _projects_hub_status(*, fast: bool) -> dict:
    module = _projects_hub_module()
    if fast and hasattr(module, "projects_implementation_status_fast"):
        return module.projects_implementation_status_fast()
    return module.projects_implementation_status()


class VerticalSliceRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    twin_earth_domain: str = "npc_behavior"


@router.get("/status")
async def integration_status() -> dict:
    """
    Unified status surface for the full Dream Caesar integration spine.

    Reports:
    - compat_council: DB availability + path
    - e8_bridge: loaded / error state
    - twin_earth: artifact dir, count, latest artifact path
    - projects_hub: operator summary, active binding, record counts, execution readiness
    """
    # --- compat council / storage DB ---
    hub_module = _projects_hub_module()
    _db = hub_module.db_path()
    db_available = _db.exists()

    # --- E8 bridge ---
    e8_status = get_e8_bridge_status()

    # --- Twin Earth artifacts ---
    artifact_dir = twin_earth_artifact_dir()
    artifacts = sorted(artifact_dir.glob("*.json"))
    latest_artifact = str(artifacts[-1]) if artifacts else None

    # --- projects hub (active binding + counts) ---
    try:
        hub = _projects_hub_status(fast=False)
        hub_data = {
            "db_path": hub.get("db_path"),
            "truth_source": hub.get("truth_source"),
            "reconciliation_status": hub.get("reconciliation_status"),
            "reconciliation_warning": hub.get("reconciliation_warning"),
            "alignment_state": hub.get("alignment_state", {}),
            "alignment_alert": hub.get("alignment_alert", {}),
            "alignment_timeline": hub.get("alignment_timeline", {}),
            "operator_summary": hub.get("operator_summary", {}),
            "counts": hub.get("counts", {}),
            "active_binding": hub.get("active_binding", {}),
            "execution_readiness": hub.get("execution_readiness", {}),
        }
        hub_error = None
    except Exception as exc:
        hub_data = {}
        hub_error = str(exc)

    data: dict = {
        "compat_council": {
            "available": db_available,
            "db_path": str(_db),
        },
        "e8_bridge": e8_status,
        "twin_earth": {
            "artifact_dir": str(artifact_dir),
            "artifact_count": len(artifacts),
            "latest_artifact": latest_artifact,
        },
        "projects_hub": hub_data,
    }
    if hub_error:
        data["projects_hub_error"] = hub_error

    return {"success": True, "data": data}


@router.get("/operator")
async def integration_operator_status() -> dict:
    """
    Compact operator-facing integration view.

    Mirrors the terminal compact projects-hub output so HTTP callers see the
    same live canon state: current seat, current step, last completed outcome,
    counts, and readiness.
    """
    try:
        hub = _projects_hub_status(fast=True)
    except Exception as exc:
        return {
            "success": False,
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
            },
        }

    return {
        "success": True,
        "data": {
            "operator_summary": hub.get("operator_summary", {}),
            "counts": hub.get("counts", {}),
            "execution_readiness": hub.get("execution_readiness", {}),
            "truth_source": hub.get("truth_source"),
            "reconciliation_status": hub.get("reconciliation_status"),
            "reconciliation_warning": hub.get("reconciliation_warning"),
            "alignment_state": hub.get("alignment_state", {}),
            "alignment_alert": hub.get("alignment_alert", {}),
            "alignment_timeline": hub.get("alignment_timeline", {}),
            "workflow_session_id": hub.get("active_binding", {}).get("workflow_session_id"),
            "problem_id": hub.get("active_binding", {}).get("problem_id"),
            "resolution_assessment": hub.get("active_binding", {}).get("latest_resolution_assessment"),
            "resolution_reason": hub.get("active_binding", {}).get("latest_resolution_reason"),
            "sentry_recovery_attempt": hub.get("active_binding", {}).get("latest_sentry_recovery_attempt", {}),
            "sentry_recovery": hub.get("active_binding", {}).get("latest_sentry_recovery", {}),
            "last_completed_sentry_recovery_attempt": hub.get("active_binding", {}).get("last_completed_sentry_recovery_attempt", {}),
            "last_completed_sentry_recovery": hub.get("active_binding", {}).get("last_completed_sentry_recovery", {}),
            "previous_cycle": hub.get("active_binding", {}).get("previous_cycle", {}),
            "loopback_context": hub.get("active_binding", {}).get("loopback_context", {}),
        },
    }


@router.get("/canon")
async def integration_canon() -> dict:
    """
    Canon ring alignment view.

    Exposes the six canonical seats in ROYGBV order with their totem
    identities, quantum principles, and the current active-canon binding
    (problem_id, workflow_session_id, current step) pulled from the
    projects hub.  Gives Codex and operators a single call to see
    whether the ring is canon-aligned and which seat is currently active.
    """
    try:
        hub = _projects_hub_status(fast=True)
        active = hub.get("active_binding", {})
        operator_summary = hub.get("operator_summary", {})
    except Exception:
        active = {}
        operator_summary = {}

    try:
        from cronus.app.council.canon_adapter import WORKFLOW_STEP_BY_SEAT, outer_seats
        live_seats = list(outer_seats())
        step_map: dict = dict(WORKFLOW_STEP_BY_SEAT)
    except Exception:
        live_seats = _SEAT_ORDER[:]
        step_map = {s: f"{s}_step" for s in _SEAT_ORDER}

    active_seat = (
        active.get("latest_iteration_seat")
        or active.get("latest_workflow_step_type")
        or active.get("latest_fractal_address")
    )

    seats = []
    for seat in _SEAT_ORDER:
        entry = dict(_SEAT_CANON.get(seat, {}))
        entry["seat"] = seat
        entry["workflow_step"] = step_map.get(seat, f"{seat}_step")
        entry["in_live_ring"] = seat in live_seats
        entry["is_active"] = seat == active_seat
        seats.append(entry)

    return {
        "success": True,
        "data": {
            "ring": "ROYGBV",
            "center": "Dream Caesar",
            "truth_source": hub.get("truth_source"),
            "reconciliation_status": hub.get("reconciliation_status"),
            "reconciliation_warning": hub.get("reconciliation_warning"),
            "alignment_state": hub.get("alignment_state", {}),
            "alignment_alert": hub.get("alignment_alert", {}),
            "alignment_timeline": hub.get("alignment_timeline", {}),
            "operator_summary": operator_summary,
            "seats": seats,
            "active_binding": {
                "problem_id": active.get("problem_id"),
                "problem_title": active.get("problem_title"),
                "workflow_session_id": active.get("workflow_session_id"),
                "current_step": active.get("workflow_current_step"),
                "latest_seat": active_seat,
                "latest_fractal_address": active.get("latest_fractal_address"),
                "last_completed_seat": active.get("last_completed_seat"),
                "last_completed_outcome": active.get("last_completed_outcome"),
                "last_completed_next_seat": active.get("last_completed_next_seat"),
                "last_completed_resolution_assessment": active.get("last_completed_resolution_assessment"),
                "last_completed_resolution_reason": active.get("last_completed_resolution_reason"),
                "latest_sentry_recovery_attempt": active.get("latest_sentry_recovery_attempt", {}),
                "latest_sentry_recovery": active.get("latest_sentry_recovery", {}),
                "last_completed_sentry_recovery_attempt": active.get("last_completed_sentry_recovery_attempt", {}),
                "last_completed_sentry_recovery": active.get("last_completed_sentry_recovery", {}),
                "resolution_assessment": operator_summary.get("resolution_assessment"),
                "resolution_reason": operator_summary.get("resolution_reason"),
                "previous_cycle": active.get("previous_cycle", {}),
                "alignment_state": active.get("alignment_state", {}),
                "alignment_timeline": active.get("alignment_timeline", {}),
                "loopback_context": active.get("loopback_context", {}),
                "loopback_reason": operator_summary.get("loopback_reason"),
                "loopback_trigger_seat": operator_summary.get("loopback_trigger_seat"),
                "loopback_trigger_outcome": operator_summary.get("loopback_trigger_outcome"),
            },
        },
    }


@router.post("/vertical-slice")
async def integration_vertical_slice(request: VerticalSliceRequest) -> dict:
    """
    Run the full integration vertical slice end-to-end:
    creates a problem + cycle, then exports a Twin Earth proposal artifact.
    Returns IDs and artifact path so the caller can track what was created.
    """
    try:
        result = await solve_problem(
            CompatProblemCreateRequest(
                title=request.title,
                description=request.description,
                export_twin_earth=True,
                twin_earth_domain=request.twin_earth_domain,
            )
        )
    except Exception as exc:
        return {
            "success": False,
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
            },
        }

    problem = result.get("problem", {})
    cycle = result.get("cycle", {})
    twin_earth = result.get("twin_earth_proposal", {})

    return {
        "success": True,
        "data": result,
        "summary": {
            "problem_id": problem.get("problem_id"),
            "workflow_session_id": problem.get("binding", {}).get("workflow_session_id"),
            "cycle_id": cycle.get("cycle_id"),
            "twin_earth_artifact_path": twin_earth.get("artifact_path"),
            "twin_earth_proposal_id": twin_earth.get("proposal_id"),
        },
    }
