"""
RED OWL - API Endpoints.

FastAPI router for Red Owl root cause analysis endpoints.
"""

from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from .engine import RedOwlEngine, create_red_owl, RedOwlResult
from .models import RedOwlConfig, AnalysisDepth

logger = structlog.get_logger(__name__)

# Create router
router = APIRouter(prefix="/red-owl", tags=["Red Owl - Root Cause Analysis"])

# Global engine instance
_engine: Optional[RedOwlEngine] = None


def get_engine() -> RedOwlEngine:
    """Get or create the Red Owl engine."""
    global _engine
    if _engine is None:
        _engine = create_red_owl()
    return _engine


def set_engine(engine: RedOwlEngine) -> None:
    """Set a custom engine instance."""
    global _engine
    _engine = engine


# Request/Response models
class AnalyzeRequest(BaseModel):
    """Request to analyze a problem."""
    problem_statement: str = Field(..., description="The problem to analyze")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    problem_id: Optional[str] = Field(None, description="Optional ID for tracking")


class QuickAnalyzeRequest(BaseModel):
    """Request for quick analysis."""
    problem_statement: str = Field(..., description="The problem to analyze")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class DepthAnalysisResponse(BaseModel):
    """Response for a single depth analysis."""
    depth: str
    depth_value: int
    hypotheses_count: int
    evidence_count: int
    crystallization_hits: int
    confidence: float
    key_insights: List[str]
    duration_ms: int


class AnalyzeResponse(BaseModel):
    """Full analysis response."""
    problem_id: str
    problem_statement: str
    final_root_cause: Optional[str]
    final_confidence: float
    depth_reached: str
    recursion_count: int
    crystallization_hits: int
    retrieval_rate: float
    total_evidence: int
    total_hypotheses: int
    accepted_hypotheses: int
    depth_analyses: List[DepthAnalysisResponse]
    reasoning_summary: List[str]
    duration_ms: int
    success: bool
    error: Optional[str] = None


class QuickAnalyzeResponse(BaseModel):
    """Quick analysis response."""
    root_cause: Optional[str]
    confidence: float
    depth_reached: str
    crystallization_hits: int
    insights: List[str]
    success: bool
    duration_ms: int


class EngineMetricsResponse(BaseModel):
    """Engine metrics response."""
    config: Dict[str, Any]
    capabilities: Dict[str, bool]


# Endpoints
@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_problem(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Perform full root cause analysis on a problem.

    This runs the complete depth cycle (SURFACE → SYNTHESIS)
    with recursive deepening if needed.
    """
    engine = get_engine()

    try:
        result: RedOwlResult = await engine.analyze(
            problem_statement=request.problem_statement,
            context=request.context,
            problem_id=request.problem_id,
        )

        analysis = result.analysis

        return AnalyzeResponse(
            problem_id=analysis.problem_id,
            problem_statement=analysis.problem_statement,
            final_root_cause=analysis.final_root_cause,
            final_confidence=analysis.final_confidence,
            depth_reached=analysis.max_depth_reached.name,
            recursion_count=analysis.recursion_count,
            crystallization_hits=analysis.crystallization_hits,
            retrieval_rate=analysis.retrieval_rate,
            total_evidence=analysis.total_evidence_gathered,
            total_hypotheses=analysis.total_hypotheses_generated,
            accepted_hypotheses=analysis.total_hypotheses_accepted,
            depth_analyses=[
                DepthAnalysisResponse(
                    depth=da.depth.name,
                    depth_value=da.depth.value,
                    hypotheses_count=len(da.hypotheses),
                    evidence_count=len(da.evidence),
                    crystallization_hits=da.crystallization_hits,
                    confidence=da.confidence,
                    key_insights=da.key_insights,
                    duration_ms=da.duration_ms,
                )
                for da in analysis.depth_analyses
            ],
            reasoning_summary=result.reasoning_summary,
            duration_ms=analysis.total_duration_ms,
            success=result.success,
            error=result.error,
        )

    except Exception as e:
        logger.error("analyze_endpoint_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-analyze", response_model=QuickAnalyzeResponse)
async def quick_analyze(request: QuickAnalyzeRequest) -> QuickAnalyzeResponse:
    """
    Perform quick analysis returning just the essentials.

    Faster than full analysis, suitable for integrations
    that just need the root cause.
    """
    engine = get_engine()

    try:
        result = await engine.quick_analyze(
            problem_statement=request.problem_statement,
            context=request.context,
        )

        return QuickAnalyzeResponse(
            root_cause=result.get("root_cause"),
            confidence=result.get("confidence", 0.0),
            depth_reached=result.get("depth_reached", "SURFACE"),
            crystallization_hits=result.get("crystallization_hits", 0),
            insights=result.get("insights", []),
            success=result.get("success", False),
            duration_ms=result.get("duration_ms", 0),
        )

    except Exception as e:
        logger.error("quick_analyze_endpoint_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=EngineMetricsResponse)
async def get_metrics() -> EngineMetricsResponse:
    """Get Red Owl engine metrics and capabilities."""
    engine = get_engine()
    metrics = engine.get_metrics()

    return EngineMetricsResponse(
        config=metrics["config"],
        capabilities=metrics["capabilities"],
    )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "agent": "red_owl"}


@router.get("/depths")
async def list_depths() -> List[Dict[str, Any]]:
    """List all analysis depth levels."""
    return [
        {
            "name": depth.name,
            "value": depth.value,
            "question": depth.question,
            "focus": depth.focus,
        }
        for depth in AnalysisDepth
    ]


# Background analysis for long-running problems
_analysis_results: Dict[str, RedOwlResult] = {}


class BackgroundAnalyzeRequest(BaseModel):
    """Request for background analysis."""
    problem_statement: str
    context: Optional[Dict[str, Any]] = None


class BackgroundAnalyzeResponse(BaseModel):
    """Response for starting background analysis."""
    analysis_id: str
    status: str


@router.post("/analyze/background", response_model=BackgroundAnalyzeResponse)
async def start_background_analysis(
    request: BackgroundAnalyzeRequest,
    background_tasks: BackgroundTasks,
) -> BackgroundAnalyzeResponse:
    """
    Start a background analysis for long-running problems.

    Returns an analysis ID that can be used to poll for results.
    """
    from uuid import uuid4

    analysis_id = str(uuid4())

    async def run_analysis():
        engine = get_engine()
        result = await engine.analyze(
            problem_statement=request.problem_statement,
            context=request.context,
            problem_id=analysis_id,
        )
        _analysis_results[analysis_id] = result

    background_tasks.add_task(run_analysis)

    return BackgroundAnalyzeResponse(
        analysis_id=analysis_id,
        status="started",
    )


@router.get("/analyze/background/{analysis_id}")
async def get_background_analysis(analysis_id: str) -> Dict[str, Any]:
    """Get the result of a background analysis."""
    if analysis_id not in _analysis_results:
        return {"status": "pending", "analysis_id": analysis_id}

    result = _analysis_results[analysis_id]

    return {
        "status": "complete",
        "analysis_id": analysis_id,
        "root_cause": result.analysis.final_root_cause,
        "confidence": result.analysis.final_confidence,
        "success": result.success,
    }
