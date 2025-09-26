"""
Cosmic Council Refinement Engine - REST API Endpoints
Provides REST API endpoints for problem submission, status tracking, and explanations.
"""

from typing import Dict, Any, Optional, List
import json
import logging
from datetime import datetime
import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import asyncio

try:
    from .layer_orchestration import LayerOrchestrator, ProblemContext
    from .refinement_tracker import RefinementTracker, TrackingEventType
    from .layers import LayerDefinitions
    from .escalator import EscalatorAction
except ImportError:
    # For testing
    from layer_orchestration import LayerOrchestrator, ProblemContext
    from refinement_tracker import RefinementTracker, TrackingEventType
    from layers import LayerDefinitions
    from escalator import EscalatorAction


# Pydantic models for API requests and responses
class ProblemSubmissionRequest(BaseModel):
    """Request model for problem submission."""
    title: str = Field(..., description="Problem title")
    description: str = Field(..., description="Problem description")
    initial_layer: str = Field(default="deci", description="Initial layer to start processing")
    max_iterations: int = Field(default=100, description="Maximum number of iterations")


class ProblemSubmissionResponse(BaseModel):
    """Response model for problem submission."""
    problem_id: str
    status: str
    message: str
    estimated_completion_time: Optional[str] = None


class ProblemStatusResponse(BaseModel):
    """Response model for problem status."""
    problem_id: str
    title: str
    current_layer: str
    status: str
    layer_runs_count: int
    refinements_count: int
    answers_count: int
    latest_layer_run: Optional[Dict[str, Any]] = None


class ProblemGenealogyResponse(BaseModel):
    """Response model for problem genealogy."""
    problem_id: str
    title: str
    original_question: str
    refinements: List[Dict[str, Any]]
    layer_runs: List[Dict[str, Any]]
    answers: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class LayerRunResponse(BaseModel):
    """Response model for layer run details."""
    layer_run_id: str
    problem_id: str
    layer: str
    revolution: int
    status: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    total_cost_usd: float
    total_latency_ms: int
    metrics: Dict[str, Any]
    sector_results: List[Dict[str, Any]]


class RefinementAnalyticsResponse(BaseModel):
    """Response model for refinement analytics."""
    problem_id: str
    total_processing_time: int
    total_cost: float
    total_latency: int
    layers_visited: List[str]
    revolutions_per_layer: Dict[str, int]
    success_rate: float
    refinement_efficiency: float
    performance_trends: Dict[str, List[float]]


class AuditTrailResponse(BaseModel):
    """Response model for audit trail."""
    problem_id: str
    events: List[Dict[str, Any]]


class LayerInfoResponse(BaseModel):
    """Response model for layer information."""
    name: str
    description: str
    toolchain_type: str
    confidence_threshold: float
    completeness_threshold: float
    max_revolutions: int
    budget_usd: float
    p95_latency_ms: int
    example_reframing: str
    tools: List[str]
    techniques: List[str]
    scale_exponent: int
    order_index: int


# Global instances
app = FastAPI(
    title="Cosmic Council Refinement Engine API",
    description="API for the Cosmic Council problem refinement system with Deci → Quecto layers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
orchestrator = LayerOrchestrator()
tracker = RefinementTracker()

# Dependency to get the orchestrator
def get_orchestrator() -> LayerOrchestrator:
    return orchestrator

# Dependency to get the tracker
def get_tracker() -> RefinementTracker:
    return tracker


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Cosmic Council Refinement Engine API",
        "version": "1.0.0",
        "description": "Problem refinement system with Deci → Quecto layers and ROYGBV cycles"
    }


@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/problems", response_model=ProblemSubmissionResponse)
async def submit_problem(
    request: ProblemSubmissionRequest,
    background_tasks: BackgroundTasks,
    orchestrator: LayerOrchestrator = Depends(get_orchestrator),
    tracker: RefinementTracker = Depends(get_tracker)
):
    """
    Submit a new problem for processing.
    
    The problem will be processed continuously in the background until resolution
    or maximum iterations are reached.
    """
    try:
        # Generate problem ID
        problem_id = str(uuid.uuid4())
        
        # Track problem creation
        tracker.track_event(
            TrackingEventType.PROBLEM_CREATED,
            problem_id,
            {
                "title": request.title,
                "description": request.description,
                "initial_layer": request.initial_layer,
                "max_iterations": request.max_iterations
            }
        )
        
        # Start background processing
        background_tasks.add_task(
            process_problem_background,
            problem_id,
            request.title,
            request.description,
            request.initial_layer,
            request.max_iterations,
            orchestrator,
            tracker
        )
        
        return ProblemSubmissionResponse(
            problem_id=problem_id,
            status="accepted",
            message="Problem submitted successfully and processing started",
            estimated_completion_time="Variable based on complexity"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting problem: {str(e)}")


async def process_problem_background(
    problem_id: str,
    title: str,
    description: str,
    initial_layer: str,
    max_iterations: int,
    orchestrator: LayerOrchestrator,
    tracker: RefinementTracker
):
    """Background task to process a problem."""
    try:
        # Process the problem continuously
        problem_context = await orchestrator.process_problem_continuously(
            problem_id=problem_id,
            title=title,
            description=description,
            max_iterations=max_iterations
        )
        
        # Track completion
        tracker.track_event(
            TrackingEventType.PROBLEM_RESOLVED,
            problem_id,
            {
                "final_status": problem_context.metadata.get("status", "unknown"),
                "total_layer_runs": len(problem_context.layer_runs),
                "total_refinements": len(problem_context.refinements),
                "total_answers": len(problem_context.answers)
            }
        )
        
    except Exception as e:
        logging.error(f"Error processing problem {problem_id}: {str(e)}")
        tracker.track_event(
            TrackingEventType.PROBLEM_RESOLVED,
            problem_id,
            {
                "final_status": "error",
                "error_message": str(e)
            }
        )


@app.get("/problems/{problem_id}/status", response_model=ProblemStatusResponse)
async def get_problem_status(
    problem_id: str,
    orchestrator: LayerOrchestrator = Depends(get_orchestrator)
):
    """Get the current status of a problem."""
    try:
        status = orchestrator.get_problem_status(problem_id)
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return ProblemStatusResponse(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting problem status: {str(e)}")


@app.get("/problems/{problem_id}/genealogy", response_model=ProblemGenealogyResponse)
async def get_problem_genealogy(
    problem_id: str,
    orchestrator: LayerOrchestrator = Depends(get_orchestrator)
):
    """Get the complete genealogy of a problem."""
    try:
        genealogy = orchestrator.get_problem_genealogy(problem_id)
        
        if "error" in genealogy:
            raise HTTPException(status_code=404, detail=genealogy["error"])
        
        return ProblemGenealogyResponse(**genealogy)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting problem genealogy: {str(e)}")


@app.get("/problems/{problem_id}/analytics", response_model=RefinementAnalyticsResponse)
async def get_problem_analytics(
    problem_id: str,
    tracker: RefinementTracker = Depends(get_tracker)
):
    """Get analytics for a problem's refinement process."""
    try:
        analytics = tracker.get_refinement_analytics(problem_id)
        
        if "error" in analytics:
            raise HTTPException(status_code=404, detail=analytics["error"])
        
        return RefinementAnalyticsResponse(**analytics)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting problem analytics: {str(e)}")


@app.get("/problems/{problem_id}/audit-trail", response_model=AuditTrailResponse)
async def get_problem_audit_trail(
    problem_id: str,
    tracker: RefinementTracker = Depends(get_tracker)
):
    """Get the complete audit trail for a problem."""
    try:
        audit_trail = tracker.get_audit_trail(problem_id)
        
        return AuditTrailResponse(
            problem_id=problem_id,
            events=audit_trail
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting audit trail: {str(e)}")


@app.get("/problems/{problem_id}/layer-runs/{layer_run_id}", response_model=LayerRunResponse)
async def get_layer_run_details(
    problem_id: str,
    layer_run_id: str,
    orchestrator: LayerOrchestrator = Depends(get_orchestrator)
):
    """Get detailed information about a specific layer run."""
    try:
        # Get problem context
        problem_context = orchestrator.active_problems.get(problem_id)
        if not problem_context:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Find the layer run
        layer_run = next(
            (run for run in problem_context.layer_runs if run.layer_run_id == layer_run_id),
            None
        )
        
        if not layer_run:
            raise HTTPException(status_code=404, detail="Layer run not found")
        
        # Convert sector results to dict format
        sector_results = [
            {
                "sector": result.sector.value,
                "status": result.status,
                "output": result.output,
                "metrics": result.metrics,
                "execution_time_ms": result.execution_time_ms,
                "cost_usd": result.cost_usd,
                "error_message": result.error_message
            }
            for result in layer_run.sector_results
        ]
        
        return LayerRunResponse(
            layer_run_id=layer_run.layer_run_id,
            problem_id=layer_run.problem_id,
            layer=layer_run.layer,
            revolution=layer_run.revolution,
            status=layer_run.status.value,
            started_at=layer_run.started_at.isoformat() if layer_run.started_at else None,
            finished_at=layer_run.finished_at.isoformat() if layer_run.finished_at else None,
            total_cost_usd=layer_run.total_cost_usd,
            total_latency_ms=layer_run.total_latency_ms,
            metrics=layer_run.metrics,
            sector_results=sector_results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting layer run details: {str(e)}")


@app.get("/layers", response_model=List[LayerInfoResponse])
async def get_all_layers():
    """Get information about all available layers."""
    try:
        layers = []
        for layer_name in LayerDefinitions.get_layer_order():
            layer_info = LayerDefinitions.get_layer_summary(layer_name)
            layers.append(LayerInfoResponse(**layer_info))
        
        return layers
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting layers: {str(e)}")


@app.get("/layers/{layer_name}", response_model=LayerInfoResponse)
async def get_layer_info(layer_name: str):
    """Get information about a specific layer."""
    try:
        if not LayerDefinitions.is_valid_layer(layer_name):
            raise HTTPException(status_code=404, detail=f"Invalid layer: {layer_name}")
        
        layer_info = LayerDefinitions.get_layer_summary(layer_name)
        return LayerInfoResponse(**layer_info)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting layer info: {str(e)}")


@app.get("/problems", response_model=List[ProblemStatusResponse])
async def list_problems(
    orchestrator: LayerOrchestrator = Depends(get_orchestrator)
):
    """List all problems and their current status."""
    try:
        problems = []
        for problem_id, problem_context in orchestrator.active_problems.items():
            status = orchestrator.get_problem_status(problem_id)
            problems.append(ProblemStatusResponse(**status))
        
        return problems
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing problems: {str(e)}")


@app.get("/problems/{problem_id}/explain", response_model=Dict[str, Any])
async def explain_problem_solution(
    problem_id: str,
    orchestrator: LayerOrchestrator = Depends(get_orchestrator),
    tracker: RefinementTracker = Depends(get_tracker)
):
    """
    Get a human-readable explanation of how a problem was solved.
    
    This endpoint provides a narrative explanation of the problem-solving process,
    including the refinement path, key decisions, and final solution.
    """
    try:
        # Get problem context
        problem_context = orchestrator.active_problems.get(problem_id)
        if not problem_context:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Get genealogy and analytics
        genealogy = tracker.get_problem_genealogy(problem_id)
        analytics = tracker.get_refinement_analytics(problem_id)
        
        # Build explanation
        explanation = {
            "problem_id": problem_id,
            "title": problem_context.title,
            "original_question": problem_context.original_question,
            "solution_summary": _build_solution_summary(problem_context, genealogy, analytics),
            "refinement_path": _build_refinement_path_explanation(genealogy),
            "key_decisions": _build_key_decisions_explanation(genealogy),
            "performance_insights": _build_performance_insights(analytics),
            "final_solution": _build_final_solution_explanation(problem_context)
        }
        
        return explanation
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining problem solution: {str(e)}")


def _build_solution_summary(problem_context: ProblemContext, genealogy: Dict[str, Any], analytics: Dict[str, Any]) -> str:
    """Build a summary of the solution process."""
    status = problem_context.metadata.get("status", "in_progress")
    layers_visited = genealogy.get("layers_visited", [])
    total_cost = analytics.get("total_cost", 0.0)
    success_rate = analytics.get("success_rate", 0.0)
    
    summary = f"Problem '{problem_context.title}' was processed through {len(layers_visited)} layers: {', '.join(layers_visited)}. "
    summary += f"The solution process achieved a {success_rate:.1%} success rate with a total cost of ${total_cost:.2f}. "
    
    if status == "resolved":
        summary += "The problem was successfully resolved with a high-quality solution."
    elif status == "max_iterations_reached":
        summary += "The problem reached the maximum number of iterations but may still have a viable solution."
    else:
        summary += "The problem is still being processed."
    
    return summary


def _build_refinement_path_explanation(genealogy: Dict[str, Any]) -> str:
    """Build an explanation of the refinement path."""
    refinements = genealogy.get("refinements", [])
    max_depth = genealogy.get("max_depth", 0)
    
    if not refinements:
        return "The problem was solved at the initial layer without requiring refinement."
    
    explanation = f"The problem was refined {len(refinements)} times, reaching a maximum depth of {max_depth} layers. "
    explanation += "The refinement path was: "
    
    path_parts = []
    for refinement in refinements:
        from_layer = refinement.get("from_layer", "unknown")
        to_layer = refinement.get("to_layer", "unknown")
        rationale = refinement.get("rationale", "No rationale provided")
        path_parts.append(f"{from_layer} → {to_layer} (because {rationale})")
    
    explanation += " → ".join(path_parts) + "."
    
    return explanation


def _build_key_decisions_explanation(genealogy: Dict[str, Any]) -> List[str]:
    """Build explanations of key decisions made during the process."""
    decisions = []
    
    # Analyze refinements
    refinements = genealogy.get("refinements", [])
    for refinement in refinements:
        from_layer = refinement.get("from_layer", "unknown")
        to_layer = refinement.get("to_layer", "unknown")
        rationale = refinement.get("rationale", "No rationale provided")
        decisions.append(f"Refined from {from_layer} to {to_layer}: {rationale}")
    
    # Analyze layer runs
    layer_runs = genealogy.get("layer_runs", [])
    for run in layer_runs:
        if run.get("status") == "completed":
            layer = run.get("layer", "unknown")
            revolution = run.get("revolution", 0)
            confidence = run.get("metrics", {}).get("confidence_score", 0.0)
            decisions.append(f"Completed {layer} layer (revolution {revolution}) with {confidence:.1%} confidence")
    
    return decisions


def _build_performance_insights(analytics: Dict[str, Any]) -> Dict[str, Any]:
    """Build performance insights from analytics."""
    return {
        "total_processing_time_ms": analytics.get("total_processing_time", 0),
        "total_cost_usd": analytics.get("total_cost", 0.0),
        "success_rate": analytics.get("success_rate", 0.0),
        "refinement_efficiency": analytics.get("refinement_efficiency", 0.0),
        "layers_visited": analytics.get("layers_visited", []),
        "revolutions_per_layer": analytics.get("revolutions_per_layer", {})
    }


def _build_final_solution_explanation(problem_context: ProblemContext) -> Dict[str, Any]:
    """Build explanation of the final solution."""
    answers = problem_context.answers
    
    if not answers:
        return {
            "status": "no_solution_yet",
            "message": "No solution has been generated yet. The problem is still being processed."
        }
    
    # Get the latest answer
    latest_answer = answers[-1]
    
    return {
        "status": "solution_available",
        "layer": latest_answer.get("layer", "unknown"),
        "confidence_score": latest_answer.get("confidence_score", 0.0),
        "completeness_score": latest_answer.get("completeness_score", 0.0),
        "solution_summary": f"Solution generated at {latest_answer.get('layer', 'unknown')} layer with {latest_answer.get('confidence_score', 0.0):.1%} confidence and {latest_answer.get('completeness_score', 0.0):.1%} completeness",
        "created_at": latest_answer.get("created_at", "unknown")
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Resource not found", "detail": str(exc)}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc)}


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the API on startup."""
    logging.info("Cosmic Council Refinement Engine API started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logging.info("Cosmic Council Refinement Engine API shutting down")


# Example usage and testing
if __name__ == "__main__":
    import uvicorn
    
    # Run the API server
    uvicorn.run(
        "refinement_engine.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
