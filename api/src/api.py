"""Cosmic Council REST API."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from .models import Enterprise, ENTERPRISE_INFO
from .council import council

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CosmicCouncil.API")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown."""
    logger.info("Cosmic Council API starting...")
    yield
    await council.close()
    logger.info("Cosmic Council API shutdown")


app = FastAPI(
    title="Cosmic Council API",
    description="The Six Enterprises solving problems through collective wisdom",
    version="1.0.0",
    lifespan=lifespan
)


# ============== Request/Response Models ==============

class CreateProblemRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None


class ProblemResponse(BaseModel):
    id: str
    title: str
    description: str
    context: Dict[str, Any]
    status: str
    created_at: datetime


class EnterpriseResponseModel(BaseModel):
    enterprise: str
    name: str
    question: str
    analysis: str
    recommendations: List[str]
    confidence: float


class CycleResponse(BaseModel):
    id: str
    problem_id: str
    responses: List[EnterpriseResponseModel]
    synthesis: str
    action_items: List[str]
    status: str


class SolutionResponse(BaseModel):
    id: str
    problem_id: str
    cycle_id: str
    title: str
    description: str
    action_items: List[str]
    confidence: float
    created_at: datetime


class RunCycleRequest(BaseModel):
    problem_id: str


class EnterpriseQueryRequest(BaseModel):
    enterprise: str = Field(..., description="Enterprise ID (red, orange, yellow, green, blue, purple)")
    question: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None


# ============== Endpoints ==============

@app.get("/")
async def root():
    """API root."""
    return {
        "name": "Cosmic Council API",
        "version": "1.0.0",
        "description": "Six enterprises solving problems through collective wisdom",
        "enterprises": [
            f"{info['name']} ({info['question']})"
            for info in ENTERPRISE_INFO.values()
        ],
        "flow": "Red Owl -> Orange Orangutan -> Yellow Honeybee -> Green Tortoise -> Blue Dolphin -> Purple Elephant"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "cosmic-council-api",
        "timestamp": datetime.utcnow().isoformat(),
        "problems_count": len(council.problems),
        "cycles_count": len(council.cycles),
        "solutions_count": len(council.solutions)
    }


# ---------- Enterprises ----------

@app.get("/api/v1/supra-enterprise")
async def list_enterprises():
    """List all six enterprises."""
    return {
        "enterprises": [
            {
                "id": ent.value,
                **info
            }
            for ent, info in ENTERPRISE_INFO.items()
        ],
        "flow": "ROYGBV (Red -> Orange -> Yellow -> Green -> Blue -> Purple)"
    }


@app.get("/api/v1/supra-enterprise/{enterprise_id}")
async def get_enterprise(enterprise_id: str):
    """Get details about a specific enterprise."""
    try:
        enterprise = Enterprise(enterprise_id)
        info = ENTERPRISE_INFO[enterprise]
        return {"id": enterprise_id, **info}
    except ValueError:
        raise HTTPException(404, f"Enterprise '{enterprise_id}' not found")


@app.post("/api/v1/supra-enterprise/query")
async def query_enterprise(request: EnterpriseQueryRequest):
    """Query a single enterprise for advice."""
    try:
        enterprise = Enterprise(request.enterprise)
    except ValueError:
        raise HTTPException(400, f"Invalid enterprise: {request.enterprise}")

    # Create temporary problem
    problem = await council.create_problem(
        title=f"Query: {request.question[:50]}...",
        description=request.question,
        context=request.context
    )

    # Run single enterprise
    response = await council.run_enterprise(enterprise, problem)
    info = ENTERPRISE_INFO[enterprise]

    return {
        "enterprise": request.enterprise,
        "name": info["name"],
        "question": info["question"],
        "analysis": response.analysis,
        "recommendations": response.recommendations,
        "confidence": response.confidence
    }


# ---------- Problems ----------

@app.post("/api/v1/problems", response_model=ProblemResponse)
async def create_problem(request: CreateProblemRequest):
    """Create a new problem for the council."""
    problem = await council.create_problem(
        title=request.title,
        description=request.description,
        context=request.context
    )
    return ProblemResponse(
        id=problem.id,
        title=problem.title,
        description=problem.description,
        context=problem.context,
        status=problem.status,
        created_at=problem.created_at
    )


@app.get("/api/v1/problems")
async def list_problems():
    """List all problems."""
    problems = council.list_problems()
    return {
        "problems": [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status,
                "created_at": p.created_at.isoformat()
            }
            for p in problems
        ],
        "count": len(problems)
    }


@app.get("/api/v1/problems/{problem_id}")
async def get_problem(problem_id: str):
    """Get a specific problem."""
    problem = council.get_problem(problem_id)
    if not problem:
        raise HTTPException(404, f"Problem {problem_id} not found")

    return {
        "id": problem.id,
        "title": problem.title,
        "description": problem.description,
        "context": problem.context,
        "status": problem.status,
        "created_at": problem.created_at.isoformat()
    }


# ---------- Cycles ----------

@app.post("/api/v1/cycles")
async def run_cycle(request: RunCycleRequest, background_tasks: BackgroundTasks):
    """Run a full ROYGBV cycle on a problem."""
    problem = council.get_problem(request.problem_id)
    if not problem:
        raise HTTPException(404, f"Problem {request.problem_id} not found")

    # Run cycle (this can take a while with LLM calls)
    cycle = await council.run_cycle(request.problem_id)

    return {
        "id": cycle.id,
        "problem_id": cycle.problem_id,
        "status": cycle.status,
        "responses_count": len(cycle.responses),
        "action_items": cycle.action_items,
        "message": "Cycle completed successfully"
    }


@app.get("/api/v1/cycles")
async def list_cycles():
    """List all cycles."""
    cycles = council.list_cycles()
    return {
        "cycles": [
            {
                "id": c.id,
                "problem_id": c.problem_id,
                "status": c.status,
                "responses_count": len(c.responses)
            }
            for c in cycles
        ],
        "count": len(cycles)
    }


@app.get("/api/v1/cycles/{cycle_id}")
async def get_cycle(cycle_id: str):
    """Get a specific cycle with all responses."""
    cycle = council.get_cycle(cycle_id)
    if not cycle:
        raise HTTPException(404, f"Cycle {cycle_id} not found")

    return {
        "id": cycle.id,
        "problem_id": cycle.problem_id,
        "status": cycle.status,
        "responses": [
            {
                "enterprise": r.enterprise.value,
                "name": ENTERPRISE_INFO[r.enterprise]["name"],
                "question": r.question,
                "analysis": r.analysis,
                "recommendations": r.recommendations,
                "confidence": r.confidence
            }
            for r in cycle.responses
        ],
        "synthesis": cycle.synthesis,
        "action_items": cycle.action_items
    }


# ---------- Solutions ----------

@app.get("/api/v1/solutions")
async def list_solutions(problem_id: Optional[str] = None):
    """List solutions, optionally filtered by problem."""
    solutions = council.get_solutions(problem_id)
    return {
        "solutions": [
            {
                "id": s.id,
                "problem_id": s.problem_id,
                "title": s.title,
                "confidence": s.confidence,
                "created_at": s.created_at.isoformat()
            }
            for s in solutions
        ],
        "count": len(solutions)
    }


@app.get("/api/v1/solutions/{solution_id}")
async def get_solution(solution_id: str):
    """Get a specific solution."""
    for solution in council.solutions.values():
        if solution.id == solution_id:
            return {
                "id": solution.id,
                "problem_id": solution.problem_id,
                "cycle_id": solution.cycle_id,
                "title": solution.title,
                "description": solution.description,
                "action_items": solution.action_items,
                "confidence": solution.confidence,
                "created_at": solution.created_at.isoformat()
            }
    raise HTTPException(404, f"Solution {solution_id} not found")


# ---------- Quick Actions ----------

@app.post("/api/v1/solve")
async def quick_solve(request: CreateProblemRequest):
    """Quick solve: Create problem and run full cycle in one call."""
    # Create problem
    problem = await council.create_problem(
        title=request.title,
        description=request.description,
        context=request.context
    )

    # Run cycle
    cycle = await council.run_cycle(problem.id)

    # Get solution
    solutions = council.get_solutions(problem.id)
    solution = solutions[0] if solutions else None

    return {
        "problem_id": problem.id,
        "cycle_id": cycle.id,
        "synthesis": cycle.synthesis,
        "action_items": cycle.action_items,
        "solution": {
            "id": solution.id,
            "confidence": solution.confidence
        } if solution else None,
        "enterprise_summaries": [
            {
                "enterprise": ENTERPRISE_INFO[r.enterprise]["name"],
                "question": r.question,
                "key_insight": r.analysis[:200] + "..." if len(r.analysis) > 200 else r.analysis
            }
            for r in cycle.responses
        ]
    }
