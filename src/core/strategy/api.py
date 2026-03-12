"""
Strategy API Endpoints
======================

REST API for managing agent strategies, calibration, and optimization.

Endpoints:
- GET/PUT /api/v1/strategy/{role} - Strategy profile management
- GET /api/v1/strategy/{role}/history - Version history
- GET /api/v1/strategy/recommendations - Optimization recommendations
- POST /api/v1/strategy/{role}/outcomes - Record cycle outcomes
- GET /api/v1/strategy/{role}/calibration - Get calibration status
- POST /api/v1/strategy/{role}/calibration/run - Trigger calibration
- GET /api/v1/strategy/{role}/scorecard - Get performance scorecard
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field, ConfigDict

from .registry import (
    AgentRole,
    RiskTolerance,
    EvidenceStandard,
    StrategyProfile,
    StrategyVersion,
    StrategyRegistry,
    ToolPreference,
)
from .outcomes import (
    CycleOutcome,
    OutcomeType,
    OutcomeEvaluator,
    RoleScorecard,
)
from .calibration import (
    CalibrationConfig,
    CalibrationResult,
    CalibrationEngine,
)
from .optimizer import (
    AdaptivePolicyEngine,
    StrategyUpdate,
    UpdateDecision,
)
from .store import StrategyStore, SQLiteStrategyStore
from .crystallization import CrystallizationEngine, TruthCandidate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/strategy", tags=["strategy"])


# -----------------------------------------------------------------------------
# Pydantic Models for API
# -----------------------------------------------------------------------------

class ToolPreferenceModel(BaseModel):
    """Tool preference configuration."""
    tool_name: str
    priority: int = 5
    success_rate: float = 0.5
    usage_count: int = 0
    enabled: bool = True

    model_config = ConfigDict(extra="forbid")


class StrategyProfileModel(BaseModel):
    """Strategy profile request/response model."""
    role: str
    version: int = 1
    risk_tolerance: str = "moderate"
    evidence_standard: str = "standard"
    min_confidence_to_act: float = Field(0.6, ge=0.0, le=1.0)
    min_confidence_to_recommend: float = Field(0.4, ge=0.0, le=1.0)
    tool_preferences: List[ToolPreferenceModel] = Field(default_factory=list)
    max_iterations: int = Field(3, ge=1, le=10)
    max_retry_attempts: int = Field(2, ge=0, le=5)
    weight_accuracy: float = Field(0.3, ge=0.0, le=1.0)
    weight_speed: float = Field(0.2, ge=0.0, le=1.0)
    weight_thoroughness: float = Field(0.3, ge=0.0, le=1.0)
    weight_clarity: float = Field(0.2, ge=0.0, le=1.0)
    update_reason: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class OutcomeRecordModel(BaseModel):
    """Cycle outcome recording model."""
    cycle_id: str
    problem_id: str
    outcome_type: str
    started_at: str
    completed_at: str
    success: bool
    confidence_reported: float = Field(ge=0.0, le=1.0)
    confidence_actual: Optional[float] = Field(None, ge=0.0, le=1.0)
    iteration_count: int = Field(1, ge=1)
    rework_count: int = Field(0, ge=0)
    human_intervention: bool = False
    intervention_type: Optional[str] = None
    user_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    user_feedback: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    tool_success_rates: Dict[str, float] = Field(default_factory=dict)
    memory_queries: int = 0
    memory_hit_rate: float = 0.0

    model_config = ConfigDict(extra="forbid")


class CalibrationTriggerModel(BaseModel):
    """Request to trigger calibration."""
    period_days: int = Field(30, ge=7, le=365)
    apply_recommendations: bool = False

    model_config = ConfigDict(extra="forbid")


class UpdateApprovalModel(BaseModel):
    """Request to approve/reject a pending update."""
    approved: bool
    approved_by: str
    reason: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class RecommendationQueryModel(BaseModel):
    """Query parameters for recommendations."""
    roles: Optional[List[str]] = None
    include_pending: bool = True
    min_confidence: float = Field(0.5, ge=0.0, le=1.0)

    model_config = ConfigDict(extra="forbid")


# -----------------------------------------------------------------------------
# Dependency Injection
# -----------------------------------------------------------------------------

_registry: Optional[StrategyRegistry] = None
_evaluator: Optional[OutcomeEvaluator] = None
_calibration_engine: Optional[CalibrationEngine] = None
_optimizer: Optional[AdaptivePolicyEngine] = None
_store: Optional[StrategyStore] = None
_crystallization_engine: Optional[CrystallizationEngine] = None


async def get_registry() -> StrategyRegistry:
    """Get strategy registry instance."""
    global _registry
    if _registry is None:
        _registry = StrategyRegistry()
    return _registry


async def get_evaluator() -> OutcomeEvaluator:
    """Get outcome evaluator instance."""
    global _evaluator
    if _evaluator is None:
        _evaluator = OutcomeEvaluator()
    return _evaluator


async def get_calibration_engine(
    evaluator: OutcomeEvaluator = Depends(get_evaluator),
) -> CalibrationEngine:
    """Get calibration engine instance."""
    global _calibration_engine
    if _calibration_engine is None:
        _calibration_engine = CalibrationEngine(evaluator)
    return _calibration_engine


async def get_optimizer(
    registry: StrategyRegistry = Depends(get_registry),
    evaluator: OutcomeEvaluator = Depends(get_evaluator),
    calibration_engine: CalibrationEngine = Depends(get_calibration_engine),
) -> AdaptivePolicyEngine:
    """Get optimizer instance."""
    global _optimizer
    if _optimizer is None:
        _optimizer = AdaptivePolicyEngine(registry, evaluator, calibration_engine)
    return _optimizer


async def get_store() -> StrategyStore:
    """Get persistence store instance."""
    global _store
    if _store is None:
        _store = SQLiteStrategyStore()
        await _store.initialize()
    return _store


async def get_crystallization_engine(
    store: StrategyStore = Depends(get_store),
) -> CrystallizationEngine:
    """Get crystallization engine instance."""
    global _crystallization_engine
    if _crystallization_engine is None:
        _crystallization_engine = CrystallizationEngine(store)
    return _crystallization_engine


def parse_role(role_str: str) -> AgentRole:
    """Parse role string to AgentRole enum."""
    try:
        return AgentRole(role_str.lower())
    except ValueError:
        valid_roles = [r.value for r in AgentRole]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role: {role_str}. Valid roles: {valid_roles}",
        )


# -----------------------------------------------------------------------------
# Static Endpoints
# -----------------------------------------------------------------------------

@router.get("/summary", response_model=Dict[str, Any])
async def get_strategy_summary(
    registry: StrategyRegistry = Depends(get_registry),
    store: StrategyStore = Depends(get_store),
):
    """
    Get summary of all role strategies.
    """
    summaries = []

    for role in AgentRole:
        profile = await store.get_profile(role)
        if profile is None:
            profile = registry.get_profile(role)

        stats = await store.get_outcome_stats(role, days=30)

        summaries.append({
            "role": role.value,
            "version": profile.version,
            "risk_tolerance": profile.risk_tolerance.value,
            "min_confidence_to_act": profile.min_confidence_to_act,
            "tool_count": len(profile.tool_preferences),
            "stats": stats,
        })

    return {
        "status": "success",
        "role_count": len(summaries),
        "roles": summaries,
    }


@router.get("/health", response_model=Dict[str, Any])
async def health_check(
    store: StrategyStore = Depends(get_store),
):
    """
    Health check for strategy service.
    """
    try:
        # Check store connectivity
        profiles = await store.get_all_profiles()

        return {
            "status": "healthy",
            "store": "connected",
            "profiles_loaded": len(profiles),
        }
    except Exception as e:
        logger.error(f"Strategy health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }

# -----------------------------------------------------------------------------
# Optimization Endpoints
# -----------------------------------------------------------------------------

@router.get("/recommendations", response_model=Dict[str, Any])
async def get_optimization_recommendations(
    registry: StrategyRegistry = Depends(get_registry),
    evaluator: OutcomeEvaluator = Depends(get_evaluator),
    calibration_engine: CalibrationEngine = Depends(get_calibration_engine),
):
    """
    Get optimization recommendations for all roles.
    """
    optimizer = AdaptivePolicyEngine(registry, evaluator, calibration_engine)
    decisions = {}

    for role in AgentRole:
        decision = optimizer.analyze_role(role)
        decisions[role.value] = [u.to_dict() for u in decision]

    return {
        "status": "success",
        "recommendations": decisions,
    }

@router.get("/truths/pending", response_model=Dict[str, Any])
async def get_pending_truths(
    engine: CrystallizationEngine = Depends(get_crystallization_engine)
):
    candidates = await engine.get_pending_candidates()
    return {
        "status": "success",
        "count": len(candidates),
        "candidates": [c.to_dict() for c in candidates]
    }

# -----------------------------------------------------------------------------
# History Endpoints
# -----------------------------------------------------------------------------

@router.get("/{role}", response_model=Dict[str, Any])
async def get_strategy_profile(
    role: str,
    registry: StrategyRegistry = Depends(get_registry),
    store: StrategyStore = Depends(get_store),
):
    """
    Get the current strategy profile for a role.

    Returns the active profile with all configuration settings.
    """
    agent_role = parse_role(role)

    # Try store first, fall back to registry
    profile = await store.get_profile(agent_role)
    if profile is None:
        profile = registry.get_profile(agent_role)

    return {
        "status": "success",
        "profile": profile.to_dict(),
    }


@router.put("/{role}", response_model=Dict[str, Any])
async def update_strategy_profile(
    role: str,
    profile_data: StrategyProfileModel,
    registry: StrategyRegistry = Depends(get_registry),
    store: StrategyStore = Depends(get_store),
):
    """
    Update the strategy profile for a role.

    Creates a new version and persists the changes.
    """
    agent_role = parse_role(role)

    # Get current profile
    current = await store.get_profile(agent_role)
    if current is None:
        current = registry.get_profile(agent_role)

    # Build updated profile
    try:
        tool_prefs = [
            ToolPreference(
                tool_name=tp.tool_name,
                priority=tp.priority,
                success_rate=tp.success_rate,
                usage_count=tp.usage_count,
                enabled=tp.enabled,
            )
            for tp in profile_data.tool_preferences
        ]

        updated = StrategyProfile(
            role=agent_role,
            version=current.version + 1,
            risk_tolerance=RiskTolerance(profile_data.risk_tolerance),
            evidence_standard=EvidenceStandard(profile_data.evidence_standard),
            min_confidence_to_act=profile_data.min_confidence_to_act,
            min_confidence_to_recommend=profile_data.min_confidence_to_recommend,
            tool_preferences=tool_prefs if tool_prefs else current.tool_preferences,
            constraints=current.constraints,
            max_iterations=profile_data.max_iterations,
            max_retry_attempts=profile_data.max_retry_attempts,
            weight_accuracy=profile_data.weight_accuracy,
            weight_speed=profile_data.weight_speed,
            weight_thoroughness=profile_data.weight_thoroughness,
            weight_clarity=profile_data.weight_clarity,
            updated_at=datetime.now(timezone.utc),
            update_reason=profile_data.update_reason or "Manual update via API",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Update registry and persist
    registry.update_profile(updated)
    await store.save_profile(updated)

    # Save version history
    version_record = StrategyVersion(
        role=agent_role,
        version=updated.version,
        profile=updated,
        created_by="api",
        update_reason=updated.update_reason,
        parent_version=current.version,
    )
    await store.save_version(version_record)

    logger.info(f"Updated strategy profile for {role} to version {updated.version}")

    return {
        "status": "success",
        "message": f"Profile updated to version {updated.version}",
        "profile": updated.to_dict(),
    }


@router.get("/{role}/history", response_model=Dict[str, Any])
async def get_strategy_history(
    role: str,
    limit: int = Query(10, ge=1, le=100),
    store: StrategyStore = Depends(get_store),
):
    """
    Get version history for a role's strategy profile.

    Returns past versions with metadata about changes.
    """
    agent_role = parse_role(role)

    versions = await store.get_version_history(agent_role, limit=limit)

    return {
        "status": "success",
        "role": role,
        "version_count": len(versions),
        "versions": [
            {
                "version": v.version,
                "created_at": v.created_at.isoformat(),
                "created_by": v.created_by,
                "update_reason": v.update_reason,
                "parent_version": v.parent_version,
                "success_rate": v.success_rate,
                "avg_score": v.avg_score,
                "sample_size": v.sample_size,
                "content_hash": v.content_hash[:16] + "...",
            }
            for v in versions
        ],
    }


@router.get("/{role}/version/{version_num}", response_model=Dict[str, Any])
async def get_strategy_version(
    role: str,
    version_num: int,
    store: StrategyStore = Depends(get_store),
):
    """
    Get a specific version of a role's strategy profile.
    """
    agent_role = parse_role(role)

    version = await store.get_version(agent_role, version_num)
    if version is None:
        raise HTTPException(
            status_code=404,
            detail=f"Version {version_num} not found for role {role}",
        )

    return {
        "status": "success",
        "version": {
            "version": version.version,
            "profile": version.profile.to_dict(),
            "created_at": version.created_at.isoformat(),
            "created_by": version.created_by,
            "update_reason": version.update_reason,
            "parent_version": version.parent_version,
            "success_rate": version.success_rate,
            "avg_score": version.avg_score,
            "sample_size": version.sample_size,
            "content_hash": version.content_hash,
        },
    }


# -----------------------------------------------------------------------------
# Outcome Endpoints
# -----------------------------------------------------------------------------

@router.post("/{role}/outcomes", response_model=Dict[str, Any])
async def record_outcome(
    role: str,
    outcome_data: OutcomeRecordModel,
    evaluator: OutcomeEvaluator = Depends(get_evaluator),
    store: StrategyStore = Depends(get_store),
):
    """
    Record a cycle outcome for a role.

    Used to track performance and feed the learning loop.
    """
    agent_role = parse_role(role)

    try:
        outcome = CycleOutcome(
            cycle_id=outcome_data.cycle_id,
            problem_id=outcome_data.problem_id,
            role=agent_role,
            outcome_type=OutcomeType(outcome_data.outcome_type),
            started_at=datetime.fromisoformat(outcome_data.started_at),
            completed_at=datetime.fromisoformat(outcome_data.completed_at),
            success=outcome_data.success,
            confidence_reported=outcome_data.confidence_reported,
            confidence_actual=outcome_data.confidence_actual,
            iteration_count=outcome_data.iteration_count,
            rework_count=outcome_data.rework_count,
            human_intervention=outcome_data.human_intervention,
            intervention_type=outcome_data.intervention_type,
            user_rating=outcome_data.user_rating,
            user_feedback=outcome_data.user_feedback,
            errors=outcome_data.errors,
            warnings=outcome_data.warnings,
            tools_used=outcome_data.tools_used,
            tool_success_rates=outcome_data.tool_success_rates,
            memory_queries=outcome_data.memory_queries,
            memory_hit_rate=outcome_data.memory_hit_rate,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Record in evaluator
    evaluator.record_outcome(outcome)

    # Persist
    await store.save_outcome(outcome)

    # Compute score
    from .registry import StrategyRegistry
    registry = await get_registry()
    profile = registry.get_profile(agent_role)
    score = evaluator.compute_score(outcome, profile)

    logger.info(
        f"Recorded outcome for {role}: cycle={outcome_data.cycle_id}, "
        f"success={outcome_data.success}, score={score:.3f}"
    )

    return {
        "status": "success",
        "message": "Outcome recorded",
        "outcome_id": outcome.cycle_id,
        "computed_score": score,
    }


@router.get("/{role}/outcomes", response_model=Dict[str, Any])
async def get_outcomes(
    role: str,
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(100, ge=1, le=1000),
    store: StrategyStore = Depends(get_store),
):
    """
    Get recorded outcomes for a role.
    """
    agent_role = parse_role(role)
    since = datetime.now(timezone.utc) - timedelta(days=days)

    outcomes = await store.get_outcomes(agent_role, since=since, limit=limit)

    return {
        "status": "success",
        "role": role,
        "period_days": days,
        "outcome_count": len(outcomes),
        "outcomes": [o.to_dict() for o in outcomes],
    }


@router.get("/{role}/scorecard", response_model=Dict[str, Any])
async def get_scorecard(
    role: str,
    days: int = Query(30, ge=1, le=365),
    evaluator: OutcomeEvaluator = Depends(get_evaluator),
    store: StrategyStore = Depends(get_store),
):
    """
    Get performance scorecard for a role.

    Aggregates metrics over the specified period.
    """
    agent_role = parse_role(role)

    # Get stats from store
    stats = await store.get_outcome_stats(agent_role, days=days)

    if stats.get("sample_size", 0) == 0:
        return {
            "status": "success",
            "role": role,
            "period_days": days,
            "scorecard": None,
            "message": "Insufficient data for scorecard",
        }

    # Build scorecard from evaluator
    scorecard = evaluator.get_scorecard(agent_role)
    if scorecard:
        return {
            "status": "success",
            "role": role,
            "period_days": days,
            "scorecard": scorecard.to_dict(),
            "stats": stats,
        }

    return {
        "status": "success",
        "role": role,
        "period_days": days,
        "scorecard": None,
        "stats": stats,
    }


# -----------------------------------------------------------------------------
# Calibration Endpoints
# -----------------------------------------------------------------------------

@router.get("/{role}/calibration", response_model=Dict[str, Any])
async def get_calibration_status(
    role: str,
    calibration_engine: CalibrationEngine = Depends(get_calibration_engine),
):
    """
    Get current calibration status for a role.

    Shows if confidence levels are well-calibrated.
    """
    agent_role = parse_role(role)

    history = calibration_engine.get_calibration_history(agent_role, limit=1)
    trend = calibration_engine.get_calibration_trend(agent_role)

    if not history:
        return {
            "status": "success",
            "role": role,
            "calibration": None,
            "message": "No calibration data available. Run calibration first.",
        }

    latest = history[0]
    return {
        "status": "success",
        "role": role,
        "calibration": latest.to_dict(),
        "trend": trend,
    }


@router.post("/{role}/calibration/run", response_model=Dict[str, Any])
async def run_calibration(
    role: str,
    request: CalibrationTriggerModel = Body(default=CalibrationTriggerModel()),
    registry: StrategyRegistry = Depends(get_registry),
    calibration_engine: CalibrationEngine = Depends(get_calibration_engine),
    store: StrategyStore = Depends(get_store),
):
    """
    Trigger calibration analysis for a role.

    Analyzes historical outcomes and optionally applies recommendations.
    """
    agent_role = parse_role(role)

    # Get current profile
    profile = await store.get_profile(agent_role)
    if profile is None:
        profile = registry.get_profile(agent_role)

    # Run calibration
    result = calibration_engine.analyze_calibration(
        agent_role,
        profile,
        period_days=request.period_days,
    )

    response = {
        "status": "success",
        "role": role,
        "calibration_result": result.to_dict(),
        "applied": False,
    }

    # Apply recommendations if requested
    if request.apply_recommendations and result.needs_recalibration:
        updated_profile = calibration_engine.apply_calibration(profile, result)
        registry.update_profile(updated_profile)
        await store.save_profile(updated_profile)

        # Save version
        version_record = StrategyVersion(
            role=agent_role,
            version=updated_profile.version,
            profile=updated_profile,
            created_by="calibration",
            update_reason=f"Calibration adjustment: {result.status.value}",
            parent_version=profile.version,
        )
        await store.save_version(version_record)

        response["applied"] = True
        response["updated_profile"] = updated_profile.to_dict()
        logger.info(f"Applied calibration for {role}: {result.status.value}")

    return response


# -----------------------------------------------------------------------------
# Optimization Endpoints
# -----------------------------------------------------------------------------

@router.get("/recommendations", response_model=Dict[str, Any])
async def get_recommendations(
    roles: Optional[str] = Query(None, description="Comma-separated roles"),
    include_pending: bool = Query(True),
    min_confidence: float = Query(0.5, ge=0.0, le=1.0),
    optimizer: AdaptivePolicyEngine = Depends(get_optimizer),
    store: StrategyStore = Depends(get_store),
):
    """
    Get optimization recommendations across roles.

    Returns pending updates and suggested improvements.
    """
    # Parse roles
    if roles:
        role_list = [parse_role(r.strip()) for r in roles.split(",")]
    else:
        role_list = list(AgentRole)

    recommendations = []

    for role in role_list:
        # Get pending updates
        if include_pending:
            pending = await store.get_updates(role=role, status="pending")
            for update in pending:
                recommendations.append({
                    "role": role.value,
                    "type": "pending_update",
                    "update": {
                        "id": update.id,
                        "update_type": update.update_type.value,
                        "risk": update.risk.value,
                        "field_name": update.field_name,
                        "delta": update.delta,
                        "reason": update.reason,
                        "created_at": update.created_at.isoformat(),
                    },
                })

        # Get optimization decision
        decision = await optimizer.evaluate_role(role)
        if decision.should_update and decision.confidence >= min_confidence:
            recommendations.append({
                "role": role.value,
                "type": "optimization_suggestion",
                "decision": {
                    "should_update": decision.should_update,
                    "confidence": decision.confidence,
                    "reason": decision.reason,
                    "updates_count": len(decision.updates),
                    "updates": [
                        {
                            "update_type": u.update_type.value,
                            "field_name": u.field_name,
                            "risk": u.risk.value,
                            "delta": u.delta,
                        }
                        for u in decision.updates[:5]  # Limit to top 5
                    ],
                    "blocked_reason": decision.blocked_reason,
                },
            })

    return {
        "status": "success",
        "recommendation_count": len(recommendations),
        "recommendations": recommendations,
    }


@router.post("/{role}/optimize", response_model=Dict[str, Any])
async def trigger_optimization(
    role: str,
    dry_run: bool = Query(True, description="If true, don't apply changes"),
    optimizer: AdaptivePolicyEngine = Depends(get_optimizer),
    store: StrategyStore = Depends(get_store),
):
    """
    Trigger optimization evaluation for a role.

    Evaluates current performance and suggests/applies updates.
    """
    agent_role = parse_role(role)

    # Get decision
    decision = await optimizer.evaluate_role(agent_role)

    response = {
        "status": "success",
        "role": role,
        "decision": {
            "should_update": decision.should_update,
            "confidence": decision.confidence,
            "reason": decision.reason,
            "updates_count": len(decision.updates),
            "blocked_reason": decision.blocked_reason,
        },
        "updates": [u.to_dict() for u in decision.updates],
        "applied": False,
    }

    # Apply if not dry run and updates available
    if not dry_run and decision.should_update and decision.updates:
        # Save pending updates
        for update in decision.updates:
            await store.save_update(update)

        # For low-risk auto-approved updates, apply immediately
        applied_count = 0
        for update in decision.updates:
            if update.status == "approved":
                await optimizer.apply_update(update)
                applied_count += 1

        response["applied"] = True
        response["applied_count"] = applied_count
        response["pending_count"] = len(decision.updates) - applied_count

        logger.info(
            f"Optimization for {role}: {applied_count} applied, "
            f"{len(decision.updates) - applied_count} pending approval"
        )

    return response


@router.get("/{role}/updates", response_model=Dict[str, Any])
async def get_updates(
    role: str,
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    store: StrategyStore = Depends(get_store),
):
    """
    Get update history for a role.
    """
    agent_role = parse_role(role)

    updates = await store.get_updates(role=agent_role, status=status, limit=limit)

    return {
        "status": "success",
        "role": role,
        "update_count": len(updates),
        "updates": [u.to_dict() for u in updates],
    }


@router.post("/updates/{update_id}/approve", response_model=Dict[str, Any])
async def approve_update(
    update_id: str,
    approval: UpdateApprovalModel,
    optimizer: AdaptivePolicyEngine = Depends(get_optimizer),
    store: StrategyStore = Depends(get_store),
):
    """
    Approve or reject a pending update.

    High-risk updates require human approval before application.
    """
    # Find the update
    all_updates = await store.get_updates(status="pending")
    update = next((u for u in all_updates if u.id == update_id), None)

    if update is None:
        raise HTTPException(
            status_code=404,
            detail=f"Update {update_id} not found or not pending",
        )

    if approval.approved:
        # Apply the update
        update.status = "approved"
        update.approved_by = approval.approved_by
        update.applied_at = datetime.now(timezone.utc)

        await optimizer.apply_update(update)
        await store.save_update(update)

        logger.info(f"Update {update_id} approved by {approval.approved_by}")

        return {
            "status": "success",
            "message": "Update approved and applied",
            "update_id": update_id,
        }
    else:
        # Reject the update
        update.status = "rejected"
        update.approved_by = approval.approved_by
        update.reason = f"Rejected: {approval.reason}" if approval.reason else "Rejected"

        await store.save_update(update)

        logger.info(f"Update {update_id} rejected by {approval.approved_by}")

        return {
            "status": "success",
            "message": "Update rejected",
            "update_id": update_id,
        }


@router.post("/{role}/rollback/{version_num}", response_model=Dict[str, Any])
async def rollback_to_version(
    role: str,
    version_num: int,
    registry: StrategyRegistry = Depends(get_registry),
    store: StrategyStore = Depends(get_store),
):
    """
    Rollback a role's strategy to a previous version.
    """
    agent_role = parse_role(role)

    # Get target version
    target_version = await store.get_version(agent_role, version_num)
    if target_version is None:
        raise HTTPException(
            status_code=404,
            detail=f"Version {version_num} not found for role {role}",
        )

    # Get current version
    current = await store.get_profile(agent_role)
    current_version = current.version if current else 0

    # Create new version with rollback content
    rollback_profile = StrategyProfile.from_dict(target_version.profile.to_dict())
    rollback_profile.version = current_version + 1
    rollback_profile.updated_at = datetime.now(timezone.utc)
    rollback_profile.update_reason = f"Rollback to version {version_num}"

    # Update registry and persist
    registry.update_profile(rollback_profile)
    await store.save_profile(rollback_profile)

    # Save version record
    version_record = StrategyVersion(
        role=agent_role,
        version=rollback_profile.version,
        profile=rollback_profile,
        created_by="rollback",
        update_reason=f"Rollback to version {version_num}",
        parent_version=current_version,
    )
    await store.save_version(version_record)

    logger.info(f"Rolled back {role} from v{current_version} to v{version_num}")

    return {
        "status": "success",
        "message": f"Rolled back to version {version_num}",
        "previous_version": current_version,
        "new_version": rollback_profile.version,
        "profile": rollback_profile.to_dict(),
    }


    return {
        "status": "success",
        "message": "Strategy rolled back",
        "version": version_record.version,
    }

# -----------------------------------------------------------------------------
# Truth/Crystallization Endpoints
# -----------------------------------------------------------------------------

@router.post("/truths/{truth_id}/approve", response_model=Dict[str, Any])
async def approve_truth(
    truth_id: str,
    approved_by: str = Body(..., embed=True),
    reason: Optional[str] = Body(None, embed=True),
    engine: CrystallizationEngine = Depends(get_crystallization_engine)
):
    success = await engine.approve_candidate(truth_id, approved_by, reason)
    if not success:
        raise HTTPException(status_code=404, detail="Truth candidate not found or not pending")
    
    return {"status": "success", "message": "Truth approved"}

@router.post("/truths/{truth_id}/reject", response_model=Dict[str, Any])
async def reject_truth(
    truth_id: str,
    rejected_by: str = Body(..., embed=True),
    reason: Optional[str] = Body(None, embed=True),
    engine: CrystallizationEngine = Depends(get_crystallization_engine)
):
    success = await engine.reject_candidate(truth_id, rejected_by, reason)
    if not success:
        raise HTTPException(status_code=404, detail="Truth candidate not found")
        
    return {"status": "success", "message": "Truth rejected"}
