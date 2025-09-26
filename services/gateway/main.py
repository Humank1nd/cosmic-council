#!/usr/bin/env python3
"""
🚪 Cosmic Council Gateway Service
FastAPI Guardrail Gateway with OPA/Rego policy enforcement
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Import shared utilities
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.utils.database import get_database_manager, DatabaseManager
from shared.logging.logger import setup_logging, get_enterprise_logger
from src.cosmic_council.core.core import ProblemStatement, ProblemComplexity, EnterpriseType
from src.cosmic_council.core.hexagon import CosmicCouncilHexagon

# Configure logging
logger = setup_logging(enterprise="gateway")
gateway_logger = get_enterprise_logger("gateway", "main")

# Pydantic models
class CycleRequest(BaseModel):
    """Request model for starting a new cycle"""
    objective_ref: str = Field(..., description="Objective reference for the cycle")
    problem_title: str = Field(..., description="Title of the problem to solve")
    problem_description: str = Field(..., description="Detailed problem description")
    complexity: ProblemComplexity = Field(default=ProblemComplexity.MODERATE, description="Problem complexity level")
    parent_cycle_id: Optional[str] = Field(None, description="Parent cycle ID for fractal recursion")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CycleResponse(BaseModel):
    """Response model for cycle operations"""
    cycle_id: str
    status: str
    message: str
    started_at: datetime
    next_stage: Optional[str] = None

class PolicyEvaluationRequest(BaseModel):
    """Request model for policy evaluation"""
    action: str = Field(..., description="Action to evaluate")
    resource: str = Field(..., description="Resource being accessed")
    subject: str = Field(..., description="Subject performing the action")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")

class PolicyEvaluationResponse(BaseModel):
    """Response model for policy evaluation"""
    allowed: bool
    reason: str
    conditions: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    services: Dict[str, str]
    version: str = "1.0.0"

# Global variables
hexagon: Optional[CosmicCouncilHexagon] = None
db_manager: Optional[DatabaseManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global hexagon, db_manager
    
    # Startup
    gateway_logger.info("🚪 Starting Cosmic Council Gateway Service")
    
    try:
        # Initialize database manager
        db_manager = await get_database_manager()
        gateway_logger.info("✅ Database manager initialized")
        
        # Initialize hexagon
        hexagon = CosmicCouncilHexagon()
        gateway_logger.info("✅ Cosmic Council Hexagon initialized")
        
        # Register enterprise stubs
        await register_enterprise_stubs()
        gateway_logger.info("✅ Enterprise stubs registered")
        
        gateway_logger.info("🚪 Gateway service startup complete")
        
    except Exception as e:
        gateway_logger.error(f"❌ Gateway startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    gateway_logger.info("🚪 Shutting down Gateway service")
    if db_manager:
        await db_manager.close_pool()
    gateway_logger.info("🚪 Gateway service shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Cosmic Council Gateway",
    description="FastAPI Guardrail Gateway with OPA/Rego policy enforcement",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Dependency injection
async def get_hexagon() -> CosmicCouncilHexagon:
    """Get hexagon instance"""
    if hexagon is None:
        raise HTTPException(status_code=503, detail="Hexagon not initialized")
    return hexagon

async def get_db_manager() -> DatabaseManager:
    """Get database manager instance"""
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    return db_manager

async def register_enterprise_stubs():
    """Register enterprise service stubs"""
    try:
        from enterprises.red_owl.services.stub import RedOwlService
        from enterprises.orange_orangutan.services.stub import OrangeOrangutanService
        from enterprises.yellow_honeybee.services.stub import YellowHoneybeeService
        from enterprises.green_tortoise.services.stub import GreenTortoiseService
        from enterprises.blue_dolphin.services.stub import BlueDolphinService
        from enterprises.purple_elephant.services.stub import PurpleElephantService

        hexagon.register_enterprise(EnterpriseType.RED_OWL, RedOwlService())
        hexagon.register_enterprise(EnterpriseType.ORANGE_ORANGUTAN, OrangeOrangutanService())
        hexagon.register_enterprise(EnterpriseType.YELLOW_HONEYBEE, YellowHoneybeeService())
        hexagon.register_enterprise(EnterpriseType.GREEN_TORTOISE, GreenTortoiseService())
        hexagon.register_enterprise(EnterpriseType.BLUE_DOLPHIN, BlueDolphinService())
        hexagon.register_enterprise(EnterpriseType.PURPLE_ELEPHANT, PurpleElephantService())
        
        gateway_logger.info("✅ All enterprise stubs registered")
    except Exception as e:
        gateway_logger.warning(f"⚠️ Enterprise stub registration warning: {e}")

# Routes
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    services = {
        "gateway": "healthy",
        "database": "healthy" if db_manager else "unhealthy",
        "hexagon": "healthy" if hexagon else "unhealthy"
    }
    
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        services=services
    )

@app.post("/v1/cycles", response_model=CycleResponse)
async def start_cycle(
    request: CycleRequest,
    background_tasks: BackgroundTasks,
    hexagon_instance: CosmicCouncilHexagon = Depends(get_hexagon),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Start a new Cosmic Council cycle"""
    try:
        # Create problem statement
        problem = ProblemStatement(
            title=request.problem_title,
            description=request.problem_description,
            complexity=request.complexity,
            metadata=request.metadata
        )
        
        # Start cycle
        result = await hexagon_instance.process_cycle(problem)
        
        # Log cycle start in database
        background_tasks.add_task(log_cycle_start, db, result.cycle_id, request.objective_ref)
        
        return CycleResponse(
            cycle_id=result.cycle_id,
            status=result.status,
            message="Cycle started successfully",
            started_at=result.timestamp,
            next_stage="red_research"
        )
        
    except Exception as e:
        gateway_logger.error(f"❌ Cycle start failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start cycle: {str(e)}")

@app.get("/v1/cycles/{cycle_id}")
async def get_cycle_status(
    cycle_id: str,
    hexagon_instance: CosmicCouncilHexagon = Depends(get_hexagon),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get cycle status and results"""
    try:
        # Query cycle from database
        query = """
        SELECT c.*, se.stage_code, se.status as stage_status, se.completed_at
        FROM cycles c
        LEFT JOIN stage_executions se ON c.id = se.cycle_id
        WHERE c.id = $1
        ORDER BY se.execution_order
        """
        
        results = await db.execute_query(query, (cycle_id,))
        
        if not results:
            raise HTTPException(status_code=404, detail="Cycle not found")
        
        # Process results
        cycle_data = results[0]
        stages = []
        
        for row in results:
            if row['stage_code']:
                stages.append({
                    "stage": row['stage_code'],
                    "status": row['stage_status'],
                    "completed_at": row['completed_at']
                })
        
        return {
            "cycle_id": cycle_id,
            "objective_ref": cycle_data['objective_ref'],
            "status": cycle_data['status'],
            "started_at": cycle_data['started_at'],
            "completed_at": cycle_data['completed_at'],
            "stages": stages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        gateway_logger.error(f"❌ Get cycle status failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cycle status: {str(e)}")

@app.post("/v1/policies/evaluate", response_model=PolicyEvaluationResponse)
async def evaluate_policy(
    request: PolicyEvaluationRequest,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Evaluate policy using OPA/Rego rules"""
    try:
        # For now, implement basic policy evaluation
        # In production, this would integrate with OPA (Open Policy Agent)
        
        allowed = True
        reason = "Policy evaluation passed"
        conditions = []
        
        # Basic policy rules
        if request.action == "start_cycle" and request.resource == "cycles":
            allowed = True
            reason = "Cycle start allowed"
            conditions.append("user_authenticated")
        elif request.action == "read" and request.resource.startswith("cycles/"):
            allowed = True
            reason = "Cycle read allowed"
            conditions.append("user_authenticated")
        else:
            allowed = False
            reason = "Action not permitted"
            conditions.append("insufficient_permissions")
        
        # Log policy evaluation
        await log_policy_evaluation(db, request, allowed, reason)
        
        return PolicyEvaluationResponse(
            allowed=allowed,
            reason=reason,
            conditions=conditions
        )
        
    except Exception as e:
        gateway_logger.error(f"❌ Policy evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Policy evaluation failed: {str(e)}")

@app.get("/v1/explain/{entity_id}")
async def explain_entity(
    entity_id: str,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get explainability chain for an entity"""
    try:
        # Query audit log for entity
        query = """
        SELECT al.*, c.objective_ref, se.stage_code
        FROM audit_log al
        LEFT JOIN cycles c ON al.cycle_id = c.id
        LEFT JOIN stage_executions se ON al.stage_execution_id = se.id
        WHERE al.entity_id = $1
        ORDER BY al.timestamp ASC
        """
        
        results = await db.execute_query(query, (entity_id,))
        
        if not results:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Build explanation chain
        explanation = {
            "entity_id": entity_id,
            "entity_type": results[0]['entity_type'],
            "chain": []
        }
        
        for row in results:
            explanation["chain"].append({
                "action": row['action'],
                "actor": row['actor'],
                "timestamp": row['timestamp'],
                "details": row['details_json'],
                "cycle_id": row['cycle_id'],
                "stage": row['stage_code']
            })
        
        return explanation
        
    except HTTPException:
        raise
    except Exception as e:
        gateway_logger.error(f"❌ Explain entity failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to explain entity: {str(e)}")

# Background tasks
async def log_cycle_start(db: DatabaseManager, cycle_id: str, objective_ref: str):
    """Log cycle start in audit log"""
    try:
        query = """
        INSERT INTO audit_log (entity_type, entity_id, action, actor, details_json, cycle_id)
        VALUES ('cycle', $1, 'create', 'gateway', $2, $1)
        """
        
        details = {"objective_ref": objective_ref, "source": "gateway"}
        await db.execute_command(query, (cycle_id, details))
        
    except Exception as e:
        gateway_logger.error(f"❌ Failed to log cycle start: {e}")

async def log_policy_evaluation(
    db: DatabaseManager, 
    request: PolicyEvaluationRequest, 
    allowed: bool, 
    reason: str
):
    """Log policy evaluation in audit log"""
    try:
        query = """
        INSERT INTO audit_log (entity_type, entity_id, action, actor, details_json)
        VALUES ('policy', $1, 'evaluate', 'gateway', $2)
        """
        
        details = {
            "action": request.action,
            "resource": request.resource,
            "subject": request.subject,
            "context": request.context,
            "result": {"allowed": allowed, "reason": reason}
        }
        
        await db.execute_command(query, (request.resource, details))
        
    except Exception as e:
        gateway_logger.error(f"❌ Failed to log policy evaluation: {e}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    gateway_logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
