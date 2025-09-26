#!/usr/bin/env python3
"""
🔄 Cycle Management Routes
Cycle lifecycle management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from shared.utils.database import DatabaseManager, get_database_manager
from shared.logging.logger import get_enterprise_logger
from src.cosmic_council.core.hexagon import CosmicCouncilHexagon
from src.cosmic_council.core.core import ProblemStatement, ProblemComplexity

router = APIRouter(prefix="/v1/cycles", tags=["cycles"])
logger = get_enterprise_logger("gateway", "cycle")

class CycleStartRequest(BaseModel):
    """Request model for starting a cycle"""
    objective_ref: str = Field(..., description="Objective reference for the cycle")
    problem_title: str = Field(..., description="Title of the problem to solve")
    problem_description: str = Field(..., description="Detailed problem description")
    complexity: ProblemComplexity = Field(default=ProblemComplexity.MODERATE, description="Problem complexity level")
    parent_cycle_id: Optional[str] = Field(None, description="Parent cycle ID for fractal recursion")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CycleStartResponse(BaseModel):
    """Response model for cycle start"""
    cycle_id: str
    status: str
    message: str
    started_at: datetime
    next_stage: Optional[str] = None
    estimated_duration: Optional[int] = None  # minutes

class CycleStatusResponse(BaseModel):
    """Response model for cycle status"""
    cycle_id: str
    objective_ref: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_stage: Optional[str] = None
    progress_percentage: float
    stages: List[Dict[str, Any]]
    overall_confidence: Optional[float] = None
    success_rate: Optional[float] = None

class CycleCancelRequest(BaseModel):
    """Request model for canceling a cycle"""
    reason: str = Field(..., description="Reason for cancellation")
    force: bool = Field(default=False, description="Force cancellation even if in progress")

class CyclePauseRequest(BaseModel):
    """Request model for pausing a cycle"""
    reason: str = Field(..., description="Reason for pausing")
    estimated_resume_time: Optional[datetime] = Field(None, description="Estimated time to resume")

@router.post("/", response_model=CycleStartResponse)
async def start_cycle(
    request: CycleStartRequest,
    background_tasks: BackgroundTasks,
    hexagon: CosmicCouncilHexagon = Depends(),
    db: DatabaseManager = Depends(get_database_manager)
):
    """Start a new Cosmic Council cycle"""
    try:
        logger.info(f"Starting new cycle: {request.objective_ref}")
        
        # Create problem statement
        problem = ProblemStatement(
            title=request.problem_title,
            description=request.problem_description,
            complexity=request.complexity,
            metadata=request.metadata
        )
        
        # Start cycle using hexagon
        result = await hexagon.process_cycle(problem)
        
        # Log cycle start in database
        background_tasks.add_task(log_cycle_start, db, result.cycle_id, request)
        
        # Estimate duration based on complexity
        estimated_duration = estimate_cycle_duration(request.complexity)
        
        return CycleStartResponse(
            cycle_id=result.cycle_id,
            status=result.status,
            message="Cycle started successfully",
            started_at=result.timestamp,
            next_stage="red_research",
            estimated_duration=estimated_duration
        )
        
    except Exception as e:
        logger.error(f"❌ Cycle start failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start cycle: {str(e)}")

@router.get("/{cycle_id}", response_model=CycleStatusResponse)
async def get_cycle_status(
    cycle_id: str,
    hexagon: CosmicCouncilHexagon = Depends(),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get detailed cycle status and progress"""
    try:
        logger.info(f"Getting cycle status: {cycle_id}")
        
        # Get cycle information
        cycle_query = """
        SELECT c.*, 
               COUNT(se.id) as total_stages,
               COUNT(CASE WHEN se.status = 'completed' THEN 1 END) as completed_stages
        FROM cycles c
        LEFT JOIN stage_executions se ON c.id = se.cycle_id
        WHERE c.id = $1
        GROUP BY c.id
        """
        
        cycle_result = await db.execute_query(cycle_query, (cycle_id,))
        
        if not cycle_result:
            raise HTTPException(status_code=404, detail="Cycle not found")
        
        cycle_data = cycle_result[0]
        
        # Get stage executions
        stages_query = """
        SELECT se.*, 
               CASE WHEN se.completed_at IS NOT NULL 
                    THEN EXTRACT(EPOCH FROM (se.completed_at - se.started_at))
                    ELSE NULL END as duration_seconds
        FROM stage_executions se
        WHERE se.cycle_id = $1
        ORDER BY se.execution_order
        """
        
        stages_result = await db.execute_query(stages_query, (cycle_id,))
        
        # Process stages
        stages = []
        current_stage = None
        for stage in stages_result:
            stage_info = {
                "stage": stage['stage_code'],
                "status": stage['status'],
                "started_at": stage['started_at'],
                "completed_at": stage['completed_at'],
                "duration_seconds": stage['duration_seconds'],
                "execution_order": stage['execution_order']
            }
            stages.append(stage_info)
            
            if stage['status'] == 'active':
                current_stage = stage['stage_code']
        
        # Calculate progress
        total_stages = len(stages)
        completed_stages = len([s for s in stages if s['status'] == 'completed'])
        progress_percentage = (completed_stages / total_stages * 100) if total_stages > 0 else 0
        
        # Get overall confidence and success rate from hexagon result
        overall_confidence = None
        success_rate = None
        
        # Try to get from hexagon if available
        try:
            # This would need to be implemented in hexagon
            # overall_confidence = await hexagon.get_cycle_confidence(cycle_id)
            # success_rate = await hexagon.get_cycle_success_rate(cycle_id)
            pass
        except:
            pass
        
        return CycleStatusResponse(
            cycle_id=cycle_id,
            objective_ref=cycle_data['objective_ref'],
            status=cycle_data['status'],
            started_at=cycle_data['started_at'],
            completed_at=cycle_data['completed_at'],
            current_stage=current_stage,
            progress_percentage=progress_percentage,
            stages=stages,
            overall_confidence=overall_confidence,
            success_rate=success_rate
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get cycle status failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cycle status: {str(e)}")

@router.get("/", response_model=List[Dict[str, Any]])
async def list_cycles(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of cycles to return"),
    offset: int = Query(0, ge=0, description="Number of cycles to skip"),
    db: DatabaseManager = Depends(get_db_manager)
):
    """List cycles with optional filtering"""
    try:
        logger.info(f"Listing cycles: status={status}, limit={limit}, offset={offset}")
        
        # Build query
        query = """
        SELECT c.*, 
               COUNT(se.id) as total_stages,
               COUNT(CASE WHEN se.status = 'completed' THEN 1 END) as completed_stages,
               EXTRACT(EPOCH FROM (c.completed_at - c.started_at)) as total_duration
        FROM cycles c
        LEFT JOIN stage_executions se ON c.id = se.cycle_id
        WHERE 1=1
        """
        
        params = []
        param_count = 0
        
        if status:
            param_count += 1
            query += f" AND c.status = ${param_count}"
            params.append(status)
        
        query += f" GROUP BY c.id ORDER BY c.started_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        params.extend([limit, offset])
        
        # Execute query
        results = await db.execute_query(query, tuple(params))
        
        # Process results
        cycles = []
        for row in results:
            progress_percentage = 0
            if row['total_stages'] > 0:
                progress_percentage = (row['completed_stages'] / row['total_stages']) * 100
            
            cycles.append({
                "cycle_id": row['id'],
                "objective_ref": row['objective_ref'],
                "status": row['status'],
                "started_at": row['started_at'],
                "completed_at": row['completed_at'],
                "total_duration": row['total_duration'],
                "progress_percentage": progress_percentage,
                "total_stages": row['total_stages'],
                "completed_stages": row['completed_stages'],
                "parent_cycle_id": row['parent_cycle_id'],
                "cycle_depth": row['cycle_depth']
            })
        
        return cycles
        
    except Exception as e:
        logger.error(f"❌ List cycles failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list cycles: {str(e)}")

@router.post("/{cycle_id}/cancel")
async def cancel_cycle(
    cycle_id: str,
    request: CycleCancelRequest,
    background_tasks: BackgroundTasks,
    hexagon: CosmicCouncilHexagon = Depends(),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Cancel a running cycle"""
    try:
        logger.info(f"Canceling cycle: {cycle_id}, reason: {request.reason}")
        
        # Check if cycle exists and is cancellable
        cycle_query = "SELECT status FROM cycles WHERE id = $1"
        cycle_result = await db.execute_query(cycle_query, (cycle_id,))
        
        if not cycle_result:
            raise HTTPException(status_code=404, detail="Cycle not found")
        
        current_status = cycle_result[0]['status']
        
        if current_status == 'completed':
            raise HTTPException(status_code=400, detail="Cannot cancel completed cycle")
        
        if current_status == 'failed':
            raise HTTPException(status_code=400, detail="Cycle already failed")
        
        if not request.force and current_status == 'active':
            # Check if any stages are currently running
            active_stages_query = """
            SELECT COUNT(*) as active_count 
            FROM stage_executions 
            WHERE cycle_id = $1 AND status = 'active'
            """
            active_result = await db.execute_query(active_stages_query, (cycle_id,))
            active_count = active_result[0]['active_count']
            
            if active_count > 0:
                raise HTTPException(
                    status_code=400, 
                    detail="Cycle has active stages. Use force=true to cancel anyway."
                )
        
        # Update cycle status
        update_query = """
        UPDATE cycles 
        SET status = 'failed', completed_at = NOW(), updated_at = NOW()
        WHERE id = $1
        """
        
        await db.execute_command(update_query, (cycle_id,))
        
        # Cancel active stages
        cancel_stages_query = """
        UPDATE stage_executions 
        SET status = 'failed', completed_at = NOW()
        WHERE cycle_id = $1 AND status = 'active'
        """
        
        await db.execute_command(cancel_stages_query, (cycle_id,))
        
        # Log cancellation
        background_tasks.add_task(log_cycle_cancellation, db, cycle_id, request)
        
        return {
            "cycle_id": cycle_id,
            "status": "cancelled",
            "message": "Cycle cancelled successfully",
            "cancelled_at": datetime.now(timezone.utc),
            "reason": request.reason
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Cancel cycle failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel cycle: {str(e)}")

@router.post("/{cycle_id}/pause")
async def pause_cycle(
    cycle_id: str,
    request: CyclePauseRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Pause a running cycle"""
    try:
        logger.info(f"Pausing cycle: {cycle_id}, reason: {request.reason}")
        
        # Check if cycle exists and is pausable
        cycle_query = "SELECT status FROM cycles WHERE id = $1"
        cycle_result = await db.execute_query(cycle_query, (cycle_id,))
        
        if not cycle_result:
            raise HTTPException(status_code=404, detail="Cycle not found")
        
        current_status = cycle_result[0]['status']
        
        if current_status != 'active':
            raise HTTPException(status_code=400, detail="Can only pause active cycles")
        
        # Update cycle status
        update_query = """
        UPDATE cycles 
        SET status = 'paused', updated_at = NOW()
        WHERE id = $1
        """
        
        await db.execute_command(update_query, (cycle_id,))
        
        # Pause active stages
        pause_stages_query = """
        UPDATE stage_executions 
        SET status = 'paused'
        WHERE cycle_id = $1 AND status = 'active'
        """
        
        await db.execute_command(pause_stages_query, (cycle_id,))
        
        # Log pause
        background_tasks.add_task(log_cycle_pause, db, cycle_id, request)
        
        return {
            "cycle_id": cycle_id,
            "status": "paused",
            "message": "Cycle paused successfully",
            "paused_at": datetime.now(timezone.utc),
            "reason": request.reason,
            "estimated_resume_time": request.estimated_resume_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Pause cycle failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to pause cycle: {str(e)}")

@router.post("/{cycle_id}/resume")
async def resume_cycle(
    cycle_id: str,
    background_tasks: BackgroundTasks,
    hexagon: CosmicCouncilHexagon = Depends(),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Resume a paused cycle"""
    try:
        logger.info(f"Resuming cycle: {cycle_id}")
        
        # Check if cycle exists and is resumable
        cycle_query = "SELECT status FROM cycles WHERE id = $1"
        cycle_result = await db.execute_query(cycle_query, (cycle_id,))
        
        if not cycle_result:
            raise HTTPException(status_code=404, detail="Cycle not found")
        
        current_status = cycle_result[0]['status']
        
        if current_status != 'paused':
            raise HTTPException(status_code=400, detail="Can only resume paused cycles")
        
        # Update cycle status
        update_query = """
        UPDATE cycles 
        SET status = 'active', updated_at = NOW()
        WHERE id = $1
        """
        
        await db.execute_command(update_query, (cycle_id,))
        
        # Resume paused stages
        resume_stages_query = """
        UPDATE stage_executions 
        SET status = 'active', started_at = NOW()
        WHERE cycle_id = $1 AND status = 'paused'
        """
        
        await db.execute_command(resume_stages_query, (cycle_id,))
        
        # Log resume
        background_tasks.add_task(log_cycle_resume, db, cycle_id)
        
        return {
            "cycle_id": cycle_id,
            "status": "active",
            "message": "Cycle resumed successfully",
            "resumed_at": datetime.now(timezone.utc)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Resume cycle failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resume cycle: {str(e)}")

# Helper functions
def estimate_cycle_duration(complexity: ProblemComplexity) -> int:
    """Estimate cycle duration in minutes based on complexity"""
    duration_map = {
        ProblemComplexity.SIMPLE: 30,
        ProblemComplexity.MODERATE: 60,
        ProblemComplexity.COMPLEX: 120,
        ProblemComplexity.SYSTEMIC: 240
    }
    return duration_map.get(complexity, 60)

async def log_cycle_start(db: DatabaseManager, cycle_id: str, request: CycleStartRequest):
    """Log cycle start in audit log"""
    try:
        query = """
        INSERT INTO audit_log (entity_type, entity_id, action, actor, details_json, cycle_id)
        VALUES ('cycle', $1, 'create', 'gateway', $2, $1)
        """
        
        details = {
            "objective_ref": request.objective_ref,
            "problem_title": request.problem_title,
            "complexity": request.complexity.value,
            "parent_cycle_id": request.parent_cycle_id,
            "metadata": request.metadata,
            "source": "gateway"
        }
        
        await db.execute_command(query, (cycle_id, details))
        
    except Exception as e:
        logger.error(f"Failed to log cycle start: {e}")

async def log_cycle_cancellation(db: DatabaseManager, cycle_id: str, request: CycleCancelRequest):
    """Log cycle cancellation in audit log"""
    try:
        query = """
        INSERT INTO audit_log (entity_type, entity_id, action, actor, details_json, cycle_id)
        VALUES ('cycle', $1, 'cancel', 'gateway', $2, $1)
        """
        
        details = {
            "reason": request.reason,
            "force": request.force,
            "source": "gateway"
        }
        
        await db.execute_command(query, (cycle_id, details))
        
    except Exception as e:
        logger.error(f"Failed to log cycle cancellation: {e}")

async def log_cycle_pause(db: DatabaseManager, cycle_id: str, request: CyclePauseRequest):
    """Log cycle pause in audit log"""
    try:
        query = """
        INSERT INTO audit_log (entity_type, entity_id, action, actor, details_json, cycle_id)
        VALUES ('cycle', $1, 'pause', 'gateway', $2, $1)
        """
        
        details = {
            "reason": request.reason,
            "estimated_resume_time": request.estimated_resume_time.isoformat() if request.estimated_resume_time else None,
            "source": "gateway"
        }
        
        await db.execute_command(query, (cycle_id, details))
        
    except Exception as e:
        logger.error(f"Failed to log cycle pause: {e}")

async def log_cycle_resume(db: DatabaseManager, cycle_id: str):
    """Log cycle resume in audit log"""
    try:
        query = """
        INSERT INTO audit_log (entity_type, entity_id, action, actor, details_json, cycle_id)
        VALUES ('cycle', $1, 'resume', 'gateway', $2, $1)
        """
        
        details = {
            "source": "gateway"
        }
        
        await db.execute_command(query, (cycle_id, details))
        
    except Exception as e:
        logger.error(f"Failed to log cycle resume: {e}")
