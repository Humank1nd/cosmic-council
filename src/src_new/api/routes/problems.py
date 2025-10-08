"""
Problem management API routes.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional
import logging

from ...core.services.problem_service import ProblemService
from ...core.models.problem import Problem, ProblemStatement
from ...core.types import ProblemComplexity
from ..main import get_problem_service
from ..schemas.requests import CreateProblemRequest, UpdateProblemRequest
from ..schemas.responses import ProblemResponse, ProblemListResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED)
async def create_problem(
    request: CreateProblemRequest,
    problem_service: ProblemService = Depends(get_problem_service)
):
    """Create a new problem"""
    try:
        problem_data = request.dict()
        problem = await problem_service.create_problem(problem_data)
        return ProblemResponse.from_model(problem)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating problem: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(
    problem_id: str,
    problem_service: ProblemService = Depends(get_problem_service)
):
    """Get a problem by ID"""
    try:
        problem = await problem_service.get_problem(problem_id)
        if not problem:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
        
        return ProblemResponse.from_model(problem)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting problem {problem_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/{problem_id}", response_model=ProblemResponse)
async def update_problem(
    problem_id: str,
    request: UpdateProblemRequest,
    problem_service: ProblemService = Depends(get_problem_service)
):
    """Update a problem"""
    try:
        updates = request.dict(exclude_unset=True)
        problem = await problem_service.update_problem(problem_id, updates)
        if not problem:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
        
        return ProblemResponse.from_model(problem)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating problem {problem_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_problem(
    problem_id: str,
    problem_service: ProblemService = Depends(get_problem_service)
):
    """Delete a problem"""
    try:
        success = await problem_service.delete_problem(problem_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting problem {problem_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/", response_model=ProblemListResponse)
async def list_problems(
    domain: Optional[str] = None,
    complexity: Optional[ProblemComplexity] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    problem_service: ProblemService = Depends(get_problem_service)
):
    """List problems with optional filters"""
    try:
        filters = {}
        if domain:
            filters['domain'] = domain
        if complexity:
            filters['complexity'] = complexity
        if status:
            filters['status'] = status
        
        problems = await problem_service.list_problems(filters)
        
        # Apply pagination
        total = len(problems)
        problems = problems[offset:offset + limit]
        
        return ProblemListResponse(
            problems=[ProblemResponse.from_model(p) for p in problems],
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error listing problems: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{problem_id}/statements", response_model=Dict[str, Any])
async def create_problem_statement(
    problem_id: str,
    statement_data: Dict[str, Any],
    problem_service: ProblemService = Depends(get_problem_service)
):
    """Create a problem statement for analysis"""
    try:
        statement_data['problem_id'] = problem_id
        statement = await problem_service.create_problem_statement(statement_data)
        return statement.to_dict()
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating problem statement: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{problem_id}/analyze-complexity", response_model=Dict[str, Any])
async def analyze_problem_complexity(
    problem_id: str,
    problem_service: ProblemService = Depends(get_problem_service)
):
    """Analyze problem complexity"""
    try:
        problem = await problem_service.get_problem(problem_id)
        if not problem:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
        
        complexity = await problem_service.analyze_problem_complexity(problem)
        
        return {
            'problem_id': problem_id,
            'analyzed_complexity': complexity.value,
            'current_complexity': problem.complexity.value,
            'analysis_timestamp': problem.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing problem complexity: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
