"""
ORANGE ORANGUTAN - API Endpoints.

FastAPI router for Orange Orangutan action planning endpoints.
"""

from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from .engine import OrangeOrangutanEngine, create_orange_orangutan, OrangeOrangutanResult
from .models import OrangeOrangutanConfig, RiskLevel, ActionCategory

logger = structlog.get_logger(__name__)

# Create router
router = APIRouter(prefix="/orange-orangutan", tags=["Orange Orangutan - Action Planning"])

# Global engine instance
_engine: Optional[OrangeOrangutanEngine] = None


def get_engine() -> OrangeOrangutanEngine:
    """Get or create the Orange Orangutan engine."""
    global _engine
    if _engine is None:
        _engine = create_orange_orangutan()
    return _engine


def set_engine(engine: OrangeOrangutanEngine) -> None:
    """Set a custom engine instance."""
    global _engine
    _engine = engine


# Request/Response models
class PlanRequest(BaseModel):
    """Request to create an action plan."""
    root_cause: str = Field(..., description="The root cause to address")
    confidence: float = Field(0.7, description="Confidence in the root cause (0-1)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    problem_id: Optional[str] = Field(None, description="Optional ID for tracking")


class QuickPlanRequest(BaseModel):
    """Request for quick planning."""
    root_cause: str = Field(..., description="The root cause to address")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ActionResponse(BaseModel):
    """Response for a single action."""
    id: str
    title: str
    category: str
    risk_level: str
    depends_on: List[str]
    has_rollback: bool
    estimated_duration_seconds: int


class PlanResponse(BaseModel):
    """Full planning response."""
    plan_id: str
    root_cause: str
    action_count: int
    overall_risk: str
    requires_approval: bool
    approval_gates: List[str]
    execution_order: List[str]
    actions: List[ActionResponse]
    rollback_order: List[str]
    estimated_duration_seconds: int
    reasoning: List[str]
    warnings: List[str]
    success: bool
    error: Optional[str] = None
    duration_ms: int


class QuickPlanResponse(BaseModel):
    """Quick planning response."""
    success: bool
    action_count: int
    overall_risk: str
    approval_needed: bool
    approval_gates: int
    estimated_duration_seconds: int
    first_actions: List[str]
    duration_ms: int


class EngineMetricsResponse(BaseModel):
    """Engine metrics response."""
    config: Dict[str, Any]
    capabilities: Dict[str, bool]


# Endpoints
@router.post("/plan", response_model=PlanResponse)
async def create_plan(request: PlanRequest) -> PlanResponse:
    """
    Create a complete action plan for a root cause.

    Takes a root cause (typically from Red Owl) and generates
    a full action plan with:
    - Ordered action steps
    - Dependency resolution
    - Risk assessment
    - Rollback procedures
    """
    engine = get_engine()

    try:
        result: OrangeOrangutanResult = await engine.plan(
            root_cause=request.root_cause,
            confidence=request.confidence,
            context=request.context,
            problem_id=request.problem_id,
        )

        plan = result.plan

        return PlanResponse(
            plan_id=plan.id,
            root_cause=plan.root_cause,
            action_count=len(plan.actions),
            overall_risk=plan.overall_risk.name,
            requires_approval=plan.requires_approval,
            approval_gates=plan.approval_gates,
            execution_order=plan.execution_order,
            actions=[
                ActionResponse(
                    id=a.id,
                    title=a.title,
                    category=a.category.value,
                    risk_level=a.risk_level.name,
                    depends_on=a.depends_on,
                    has_rollback=a.rollback is not None and a.rollback.is_reversible,
                    estimated_duration_seconds=a.estimated_duration_seconds,
                )
                for a in plan.actions
            ],
            rollback_order=plan.rollback_order,
            estimated_duration_seconds=plan.estimated_total_duration_seconds,
            reasoning=result.reasoning,
            warnings=result.warnings,
            success=result.success,
            error=result.error,
            duration_ms=result.duration_ms,
        )

    except Exception as e:
        logger.error("plan_endpoint_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-plan", response_model=QuickPlanResponse)
async def quick_plan(request: QuickPlanRequest) -> QuickPlanResponse:
    """
    Create a quick plan returning just the essentials.

    Faster than full planning, suitable for integrations
    that just need the overview.
    """
    engine = get_engine()

    try:
        result = await engine.quick_plan(
            root_cause=request.root_cause,
            context=request.context,
        )

        return QuickPlanResponse(
            success=result["success"],
            action_count=result["action_count"],
            overall_risk=result["overall_risk"],
            approval_needed=result["approval_needed"],
            approval_gates=result["approval_gates"],
            estimated_duration_seconds=result["estimated_duration_seconds"],
            first_actions=result["execution_order"],
            duration_ms=result["duration_ms"],
        )

    except Exception as e:
        logger.error("quick_plan_endpoint_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=EngineMetricsResponse)
async def get_metrics() -> EngineMetricsResponse:
    """Get Orange Orangutan engine metrics and capabilities."""
    engine = get_engine()
    metrics = engine.get_metrics()

    return EngineMetricsResponse(
        config=metrics["config"],
        capabilities=metrics["capabilities"],
    )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "agent": "orange_orangutan"}


@router.get("/categories")
async def list_categories() -> List[Dict[str, str]]:
    """List all action categories."""
    return [
        {"name": cat.name, "value": cat.value}
        for cat in ActionCategory
    ]


@router.get("/risk-levels")
async def list_risk_levels() -> List[Dict[str, Any]]:
    """List all risk levels with their properties."""
    return [
        {
            "name": level.name,
            "value": level.value,
            "requires_approval": level.requires_approval,
            "requires_confirmation": level.requires_confirmation,
            "can_auto_execute": level.can_auto_execute,
        }
        for level in RiskLevel
    ]


# Background planning for complex problems
_planning_results: Dict[str, OrangeOrangutanResult] = {}


class BackgroundPlanRequest(BaseModel):
    """Request for background planning."""
    root_cause: str
    confidence: float = 0.7
    context: Optional[Dict[str, Any]] = None


class BackgroundPlanResponse(BaseModel):
    """Response for starting background planning."""
    plan_id: str
    status: str


@router.post("/plan/background", response_model=BackgroundPlanResponse)
async def start_background_plan(
    request: BackgroundPlanRequest,
    background_tasks: BackgroundTasks,
) -> BackgroundPlanResponse:
    """
    Start a background planning session.

    Returns a plan ID that can be used to poll for results.
    """
    from uuid import uuid4

    plan_id = str(uuid4())

    async def run_planning():
        engine = get_engine()
        result = await engine.plan(
            root_cause=request.root_cause,
            confidence=request.confidence,
            context=request.context,
            problem_id=plan_id,
        )
        _planning_results[plan_id] = result

    background_tasks.add_task(run_planning)

    return BackgroundPlanResponse(
        plan_id=plan_id,
        status="started",
    )


@router.get("/plan/background/{plan_id}")
async def get_background_plan(plan_id: str) -> Dict[str, Any]:
    """Get the result of a background planning session."""
    if plan_id not in _planning_results:
        return {"status": "pending", "plan_id": plan_id}

    result = _planning_results[plan_id]

    return {
        "status": "complete",
        "plan_id": plan_id,
        "action_count": len(result.plan.actions),
        "overall_risk": result.plan.overall_risk.name,
        "success": result.success,
    }
