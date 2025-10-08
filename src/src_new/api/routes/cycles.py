"""
Cycle management API routes.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional
import logging

from ...core.services.cycle_service import CycleService
from ...core.models.cycle import Cycle
from ...core.types import CycleStatus, EnterpriseType
from ..main import get_cycle_service
from ..schemas.requests import CreateCycleRequest, UpdateCycleRequest
from ..schemas.responses import CycleResponse, CycleListResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=CycleResponse, status_code=status.HTTP_201_CREATED)
async def create_cycle(
    request: CreateCycleRequest,
    cycle_service: CycleService = Depends(get_cycle_service)
):
    """Create a new problem-solving cycle"""
    try:
        cycle_data = request.dict()
        cycle = await cycle_service.create_cycle(cycle_data)
        return CycleResponse.from_model(cycle)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating cycle: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{cycle_id}", response_model=CycleResponse)
async def get_cycle(
    cycle_id: str,
    cycle_service: CycleService = Depends(get_cycle_service)
):
    """Get a cycle by ID"""
    try:
        cycle = await cycle_service.get_cycle(cycle_id)
        if not cycle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
        
        return CycleResponse.from_model(cycle)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cycle {cycle_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{cycle_id}/start", response_model=CycleResponse)
async def start_cycle(
    cycle_id: str,
    cycle_service: CycleService = Depends(get_cycle_service)
):
    """Start a cycle execution"""
    try:
        cycle = await cycle_service.start_cycle(cycle_id)
        if not cycle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
        
        return CycleResponse.from_model(cycle)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting cycle {cycle_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{cycle_id}/execute", response_model=CycleResponse)
async def execute_cycle(
    cycle_id: str,
    cycle_service: CycleService = Depends(get_cycle_service)
):
    """Execute a complete cycle"""
    try:
        cycle = await cycle_service.execute_cycle(cycle_id)
        if not cycle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
        
        return CycleResponse.from_model(cycle)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing cycle {cycle_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{cycle_id}/pause", response_model=CycleResponse)
async def pause_cycle(
    cycle_id: str,
    cycle_service: CycleService = Depends(get_cycle_service)
):
    """Pause a running cycle"""
    try:
        cycle = await cycle_service.pause_cycle(cycle_id)
        if not cycle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
        
        return CycleResponse.from_model(cycle)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error pausing cycle {cycle_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{cycle_id}/resume", response_model=CycleResponse)
async def resume_cycle(
    cycle_id: str,
    cycle_service: CycleService = Depends(get_cycle_service)
):
    """Resume a paused cycle"""
    try:
        cycle = await cycle_service.resume_cycle(cycle_id)
        if not cycle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
        
        return CycleResponse.from_model(cycle)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error resuming cycle {cycle_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{cycle_id}/cancel", response_model=CycleResponse)
async def cancel_cycle(
    cycle_id: str,
    cycle_service: CycleService = Depends(get_cycle_service)
):
    """Cancel a cycle"""
    try:
        cycle = await cycle_service.cancel_cycle(cycle_id)
        if not cycle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
        
        return CycleResponse.from_model(cycle)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error cancelling cycle {cycle_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/", response_model=CycleListResponse)
async def list_cycles(
    problem_id: Optional[str] = None,
    status: Optional[CycleStatus] = None,
    limit: int = 100,
    offset: int = 0,
    cycle_service: CycleService = Depends(get_cycle_service)
):
    """List cycles with optional filters"""
    try:
        filters = {}
        if problem_id:
            filters['problem_id'] = problem_id
        if status:
            filters['status'] = status
        
        # This would need to be implemented in the service
        cycles = []  # await cycle_service.list_cycles(filters)
        
        # Apply pagination
        total = len(cycles)
        cycles = cycles[offset:offset + limit]
        
        return CycleListResponse(
            cycles=[CycleResponse.from_model(c) for c in cycles],
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error listing cycles: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{cycle_id}/results", response_model=List[Dict[str, Any]])
async def get_cycle_results(
    cycle_id: str,
    cycle_service: CycleService = Depends(get_cycle_service)
):
    """Get all results for a cycle"""
    try:
        results = await cycle_service.get_cycle_results(cycle_id)
        return [result.to_dict() for result in results]
        
    except Exception as e:
        logger.error(f"Error getting cycle results: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
