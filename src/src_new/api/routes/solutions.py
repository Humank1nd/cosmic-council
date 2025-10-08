"""
Solution management API routes.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional
import logging

from ...core.services.solution_service import SolutionService
from ...core.models.solution import Solution, SolutionComponent
from ..main import get_solution_service
from ..schemas.requests import CreateSolutionRequest, UpdateSolutionRequest, CreateSolutionComponentRequest
from ..schemas.responses import SolutionResponse, SolutionListResponse, SolutionComponentResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=SolutionResponse, status_code=status.HTTP_201_CREATED)
async def create_solution(
    request: CreateSolutionRequest,
    solution_service: SolutionService = Depends(get_solution_service)
):
    """Create a new solution"""
    try:
        solution_data = request.dict()
        solution = await solution_service.create_solution(solution_data)
        return SolutionResponse.from_model(solution)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating solution: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{solution_id}", response_model=SolutionResponse)
async def get_solution(
    solution_id: str,
    solution_service: SolutionService = Depends(get_solution_service)
):
    """Get a solution by ID"""
    try:
        solution = await solution_service.get_solution(solution_id)
        if not solution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")
        
        return SolutionResponse.from_model(solution)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting solution {solution_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/{solution_id}", response_model=SolutionResponse)
async def update_solution(
    solution_id: str,
    request: UpdateSolutionRequest,
    solution_service: SolutionService = Depends(get_solution_service)
):
    """Update a solution"""
    try:
        updates = request.dict(exclude_unset=True)
        solution = await solution_service.update_solution(solution_id, updates)
        if not solution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")
        
        return SolutionResponse.from_model(solution)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating solution {solution_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{solution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_solution(
    solution_id: str,
    solution_service: SolutionService = Depends(get_solution_service)
):
    """Delete a solution"""
    try:
        success = await solution_service.delete_solution(solution_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting solution {solution_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/", response_model=SolutionListResponse)
async def list_solutions(
    problem_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    solution_service: SolutionService = Depends(get_solution_service)
):
    """List solutions with optional filters"""
    try:
        if problem_id:
            solutions = await solution_service.get_solutions_for_problem(problem_id)
        else:
            solutions = []  # Would need to implement list_solutions in service
        
        # Apply status filter
        if status:
            solutions = [s for s in solutions if s.status == status]
        
        # Apply pagination
        total = len(solutions)
        solutions = solutions[offset:offset + limit]
        
        return SolutionListResponse(
            solutions=[SolutionResponse.from_model(s) for s in solutions],
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error listing solutions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{solution_id}/components", response_model=SolutionComponentResponse, status_code=status.HTTP_201_CREATED)
async def add_solution_component(
    solution_id: str,
    request: CreateSolutionComponentRequest,
    solution_service: SolutionService = Depends(get_solution_service)
):
    """Add a component to a solution"""
    try:
        component_data = request.dict()
        component = await solution_service.add_solution_component(solution_id, component_data)
        return SolutionComponentResponse.from_model(component)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding solution component: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{solution_id}/components", response_model=List[SolutionComponentResponse])
async def get_solution_components(
    solution_id: str,
    solution_service: SolutionService = Depends(get_solution_service)
):
    """Get all components for a solution"""
    try:
        components = await solution_service.get_solution_components(solution_id)
        return [SolutionComponentResponse.from_model(c) for c in components]
        
    except Exception as e:
        logger.error(f"Error getting solution components: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{solution_id}/evaluate", response_model=Dict[str, Any])
async def evaluate_solution(
    solution_id: str,
    problem_id: str,
    solution_service: SolutionService = Depends(get_solution_service)
):
    """Evaluate a solution against a problem"""
    try:
        solution = await solution_service.get_solution(solution_id)
        if not solution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")
        
        # This would need to get the problem from the problem service
        # For now, create a mock problem
        from ...core.models.problem import Problem
        problem = Problem(problem_id=problem_id, title="Mock Problem", description="Mock Description")
        
        evaluation = await solution_service.evaluate_solution(solution, problem)
        return evaluation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating solution: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
