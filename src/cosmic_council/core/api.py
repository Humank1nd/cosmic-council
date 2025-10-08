"""
Cosmic Council REST API Server
Comprehensive API endpoints for problem submission, cycle execution, and result retrieval
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import uvicorn

# Import our existing components
from .core import ProblemStatement, ProblemComplexity, EnterpriseType
from ..workflows.problem_solving_workflow import ProblemSolvingWorkflow, WorkflowStep
from ..agents.unified_ai_agent_system import LLMConfig, LLMProvider, LLMModel, UnifiedCosmicCouncilAgent, AgentType
from ..workflows.ai_enhanced_workflow import AIEnhancedProblemSolvingWorkflow, AIWorkflowConfig
from ..database.unified_database_service import (
    UnifiedDatabaseService,
    Problem, Solution, Cycle, Enterprise, EnterpriseResult, User, Stakeholder,
    Constraint, SuccessCriterion, SolutionComponent, ImplementationTracking,
    CycleAnalytics, SystemMetrics, AuditLog,
    # ROYGBV workflow models (detailed)
    ResearchCoreProblem, ResearchFinding, ResearchPrioritizedQuestion,
    PlanningRelatedQuestion, PlanningActionPlan, PlanningDependency,
    DevelopmentPrototype, DevelopmentInternalTesting, DevelopmentCreativeNote,
    BudgetResourceInventory, BudgetAllocation, BudgetTimeCostAnalysis,
    MarketInsight, MarketCommunicationStrategy, MarketPerformanceMetric,
    SupportUserFeedback, SupportPerformanceAssessment, SupportContinuousImprovement
)
from ..database.unified_database_manager import get_database_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Global variables for application state
workflow_engine: Optional[ProblemSolvingWorkflow] = None
ai_workflow_engine: Optional[AIEnhancedProblemSolvingWorkflow] = None
ai_integration: Optional[UnifiedCosmicCouncilAgent] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global workflow_engine, ai_workflow_engine, ai_integration
    global perpetual_engine, orchestration_system, perpetual_db_service
    global perpetual_guardrail_integration, perpetual_policy_enforcer
    global fractal_108_cycle_system, perpetual_108_cycle_integration
    
    # Startup
    logger.info("Starting Cosmic Council API Server...")
    
    try:
        # Initialize database
        db_manager = get_database_manager()
        logger.info("Database initialized successfully")
        
        # Initialize workflow engine
        workflow_engine = ProblemSolvingWorkflow()
        logger.info("Workflow engine initialized")
        
        # Initialize AI integration (simplified for now)
        ai_integration = None
        ai_workflow_engine = None
        logger.info("AI integration disabled for simplified API")
        
        # Initialize perpetual thinking system
        try:
            # Initialize database service for perpetual system
            perpetual_db_service = PerpetualDatabaseService("sqlite:///perpetual_thinking.db")
            await perpetual_db_service.create_tables()
            
            # Initialize base perpetual thinking engine
            perpetual_engine = PerpetualThinkingEngine(
                database_url="sqlite:///perpetual_thinking.db"
            )
            
            # Initialize AI-enhanced perpetual thinking engine
            from ai_llm_integration import LLMConfig, LLMProvider, LLMModel
            ai_config = LLMConfig(
                provider=LLMProvider.MOCK,  # Use mock for demo
                model=LLMModel.GPT_4,
                temperature=0.7,
                max_tokens=2000
            )
            perpetual_ai_engine = PerpetualAIThinkingEngine(
                database_url="sqlite:///perpetual_thinking.db",
                ai_config=ai_config
            )
            
            # Initialize meta-cyclical architecture
            meta_architecture = MetaCyclicalArchitecture()
            
            # Initialize master orchestration system
            orchestration_system = MasterOrchestrationSystem(
                perpetual_engine=perpetual_ai_engine,  # Use AI-enhanced engine
                meta_architecture=meta_architecture,
                database_service=perpetual_db_service
            )
            
            # Initialize Guardrail Gateway integration
            perpetual_guardrail_integration = PerpetualGuardrailIntegration(
                enable_audit_logging=True,
                enable_simulation_mode=False
            )
            
            # Initialize policy enforcer
            perpetual_policy_enforcer = PerpetualPolicyEnforcer(
                perpetual_engine=perpetual_ai_engine,  # Use AI-enhanced engine
                guardrail_integration=perpetual_guardrail_integration
            )
            
            # Initialize 108-cycle fractal system
            fractal_108_cycle_system = Fractal108CycleSystem()
            
            # Initialize perpetual-108-cycle integration
            perpetual_108_cycle_integration = Perpetual108CycleIntegration(
                fractal_system=fractal_108_cycle_system,
                perpetual_engine=perpetual_ai_engine,  # Use AI-enhanced engine
                meta_architecture=meta_architecture,
                orchestration_system=orchestration_system,
                guardrail_integration=perpetual_guardrail_integration
            )
            
            logger.info("AI-enhanced perpetual thinking system initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize perpetual thinking system: {e}")
            # Set to None to indicate system is not available
            perpetual_engine = None
            perpetual_ai_engine = None
            orchestration_system = None
            perpetual_db_service = None
            perpetual_guardrail_integration = None
            perpetual_policy_enforcer = None
            fractal_108_cycle_system = None
            perpetual_108_cycle_integration = None
        
        logger.info("AI integration and enhanced workflow initialized")
        logger.info("Cosmic Council API Server started successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize API server: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Cosmic Council API Server...")

# Create FastAPI application
app = FastAPI(
    title="Cosmic Council API",
    description="REST API for the Cosmic Council problem-solving framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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

# Pydantic Models for API

class ProblemCreateRequest(BaseModel):
    """Request model for creating a problem"""
    title: str = Field(..., min_length=1, max_length=500, description="Problem title")
    description: str = Field(..., min_length=1, description="Problem description")
    domain: str = Field(..., min_length=1, max_length=200, description="Problem domain")
    complexity: str = Field(..., description="Problem complexity level")
    priority: str = Field(default="medium", description="Problem priority")
    stakeholders: List[str] = Field(default=[], description="List of stakeholders")
    constraints: Dict[str, Any] = Field(default={}, description="Problem constraints")
    success_criteria: List[str] = Field(default=[], description="Success criteria")
    due_date: Optional[datetime] = Field(default=None, description="Due date")
    
    @validator('complexity')
    def validate_complexity(cls, v):
        valid_complexities = ['simple', 'moderate', 'complex', 'systemic']
        if v not in valid_complexities:
            raise ValueError(f'Complexity must be one of: {valid_complexities}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v

class ProblemUpdateRequest(BaseModel):
    """Request model for updating a problem"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=1)
    domain: Optional[str] = Field(None, min_length=1, max_length=200)
    complexity: Optional[str] = Field(None)
    priority: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
    due_date: Optional[datetime] = Field(None)
    
    @validator('complexity')
    def validate_complexity(cls, v):
        if v is not None:
            valid_complexities = ['simple', 'moderate', 'complex', 'systemic']
            if v not in valid_complexities:
                raise ValueError(f'Complexity must be one of: {valid_complexities}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v is not None:
            valid_priorities = ['low', 'medium', 'high', 'critical']
            if v not in valid_priorities:
                raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['active', 'in_progress', 'completed', 'archived']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {valid_statuses}')
        return v

class CycleCreateRequest(BaseModel):
    """Request model for creating a cycle"""
    problem_id: str = Field(..., description="Problem ID")
    cycle_number: int = Field(..., ge=1, description="Cycle number")
    max_iterations: int = Field(default=3, ge=1, le=10, description="Maximum iterations")

class WorkflowStepRequest(BaseModel):
    """Request model for workflow step execution"""
    step_name: str = Field(..., description="Step name")
    user_inputs: Dict[str, Any] = Field(default={}, description="User inputs for the step")

class SolutionCreateRequest(BaseModel):
    """Request model for creating a solution"""
    problem_id: str = Field(..., description="Problem ID")
    cycle_id: str = Field(..., description="Cycle ID")
    title: str = Field(..., min_length=1, max_length=500, description="Solution title")
    description: str = Field(..., min_length=1, description="Solution description")
    approach: Optional[str] = Field(None, description="Solution approach")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    feasibility_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Feasibility score")
    impact_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Impact score")
    estimated_cost: Optional[float] = Field(None, ge=0.0, description="Estimated cost")
    estimated_duration: Optional[int] = Field(None, ge=1, description="Estimated duration in days")
    risk_level: Optional[str] = Field(None, description="Risk level")
    
    @validator('risk_level')
    def validate_risk_level(cls, v):
        if v is not None:
            valid_risk_levels = ['low', 'medium', 'high', 'critical']
            if v not in valid_risk_levels:
                raise ValueError(f'Risk level must be one of: {valid_risk_levels}')
        return v

class ResponseModel(BaseModel):
    """Standard response model"""
    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProblemResponse(BaseModel):
    """Problem response model"""
    id: str
    title: str
    description: str
    domain: str
    complexity: str
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]
    stakeholder_count: int
    constraint_count: int
    success_criteria_count: int
    cycle_count: int
    solution_count: int

class CycleResponse(BaseModel):
    """Cycle response model"""
    id: str
    problem_id: str
    cycle_number: int
    status: str
    phase: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    total_duration: Optional[int]
    confidence_score: Optional[float]
    max_iterations: int
    current_iteration: int
    enterprise_results_count: int

class SolutionResponse(BaseModel):
    """Solution response model"""
    id: str
    problem_id: str
    cycle_id: str
    title: str
    description: str
    status: str
    confidence_score: Optional[float]
    feasibility_score: Optional[float]
    impact_score: Optional[float]
    estimated_cost: Optional[float]
    estimated_duration: Optional[int]
    risk_level: Optional[str]
    created_at: datetime
    updated_at: datetime

# Dependency functions

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user from authorization token"""
    # In a real implementation, this would validate the JWT token
    # For demo purposes, we'll just return a mock user ID
    return "demo_user"

async def get_workflow_engine() -> ProblemSolvingWorkflow:
    """Get the workflow engine instance"""
    if workflow_engine is None:
        raise HTTPException(status_code=500, detail="Workflow engine not initialized")
    return workflow_engine

async def get_ai_workflow_engine() -> AIEnhancedProblemSolvingWorkflow:
    """Get the AI-enhanced workflow engine instance"""
    if ai_workflow_engine is None:
        raise HTTPException(status_code=500, detail="AI workflow engine not initialized")
    return ai_workflow_engine

# API Endpoints

@app.get("/", response_model=ResponseModel)
async def root():
    """Root endpoint with API information"""
    return ResponseModel(
        success=True,
        message="Cosmic Council API is running",
        data={
            "version": "1.0.0",
            "description": "REST API for the Cosmic Council problem-solving framework",
            "endpoints": {
                "problems": "/api/v1/problems",
                "cycles": "/api/v1/cycles",
                "solutions": "/api/v1/solutions",
                "workflows": "/api/v1/workflows",
                "analytics": "/api/v1/analytics",
                "enterprises": "/api/v1/enterprises",
                "perpetual_sessions": "/api/v1/perpetual/sessions",
                "perpetual_metrics": "/api/v1/perpetual/metrics",
                "perpetual_status": "/api/v1/perpetual/status",
                "perpetual_audit_logs": "/api/v1/perpetual/audit/logs",
                "perpetual_violations": "/api/v1/perpetual/audit/violations",
                "perpetual_risk_summary": "/api/v1/perpetual/audit/risk-summary",
                "perpetual_policy_evaluate": "/api/v1/perpetual/policy/evaluate",
                "ai_session_analytics": "/api/v1/perpetual/ai/sessions/{session_id}/analytics",
                "ai_enhanced_cycle_status": "/api/v1/perpetual/ai/sessions/{session_id}/status",
                "ai_sessions_list": "/api/v1/perpetual/ai/sessions",
                "fractal_perpetual_sessions": "/api/v1/fractal-perpetual/sessions",
                "fractal_perpetual_analytics": "/api/v1/fractal-perpetual/analytics",
                "fractal_perpetual_insights": "/api/v1/fractal-perpetual/insights",
                "fractal_perpetual_status": "/api/v1/fractal-perpetual/status"
            }
        }
    )

@app.get("/health", response_model=ResponseModel)
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_manager = get_database_manager()
        db_healthy = db_manager.check_connection()
        
        # Check workflow engine
        workflow_healthy = workflow_engine is not None
        
        # Check AI integration
        ai_healthy = ai_integration is not None
        
        # Check perpetual thinking system
        perpetual_healthy = (perpetual_engine is not None and 
                           perpetual_ai_engine is not None and
                           orchestration_system is not None and
                           perpetual_guardrail_integration is not None and
                           fractal_108_cycle_system is not None and
                           perpetual_108_cycle_integration is not None)
        
        overall_health = db_healthy and workflow_healthy and ai_healthy
        
        return ResponseModel(
            success=overall_health,
            message="Health check completed",
            data={
                "database": db_healthy,
                "workflow_engine": workflow_healthy,
                "ai_integration": ai_healthy,
                "perpetual_thinking_system": perpetual_healthy,
                "ai_enhanced_perpetual_system": perpetual_ai_engine is not None,
                "overall_status": "healthy" if overall_health else "unhealthy"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return ResponseModel(
            success=False,
            message="Health check failed",
            data={"error": str(e)}
        )

# Problem Management Endpoints

@app.post("/api/v1/problems", response_model=ResponseModel)
async def create_problem(
    request: ProblemCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Create a new problem"""
    try:
        # Convert to ProblemStatement
        problem_statement = ProblemStatement(
            title=request.title,
            description=request.description,
            domain=request.domain,
            complexity=ProblemComplexity(request.complexity),
            stakeholders=request.stakeholders,
            constraints=request.constraints,
            success_criteria=request.success_criteria
        )
        
        # Create problem in database
        problem = ProblemRepository.create_problem(
            title=request.title,
            description=request.description,
            domain=request.domain,
            complexity=request.complexity,
            priority=request.priority,
            due_date=request.due_date
        )
        
        # Log audit action
        background_tasks.add_task(
            AuditLogRepository.log_action,
            action="create",
            resource_type="problem",
            resource_id=problem.id,
            user_id=current_user,
            new_values=request.dict()
        )
        
        # Record system metric
        background_tasks.add_task(
            SystemMetricsRepository.record_metric,
            metric_name="problems_created",
            metric_type="counter",
            metric_value=1.0,
            tags=["api", "problem"]
        )
        
        return ResponseModel(
            success=True,
            message="Problem created successfully",
            data={
                "problem_id": str(problem.id),
                "title": problem.title,
                "domain": problem.domain,
                "complexity": problem.complexity
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to create problem: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create problem: {str(e)}")

@app.get("/api/v1/problems", response_model=ResponseModel)
async def get_problems(
    domain: Optional[str] = None,
    complexity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: str = Depends(get_current_user)
):
    """Get problems with filtering"""
    try:
        problems = ProblemRepository.get_problems(
            domain=domain,
            complexity=complexity,
            status=status,
            limit=limit,
            offset=offset
        )
        
        problem_responses = []
        for problem in problems:
            problem_responses.append(ProblemResponse(
                id=str(problem.id),
                title=problem.title,
                description=problem.description,
                domain=problem.domain,
                complexity=problem.complexity,
                priority=problem.priority,
                status=problem.status,
                created_at=problem.created_at,
                updated_at=problem.updated_at,
                due_date=problem.due_date,
                stakeholder_count=len(problem.stakeholders),
                constraint_count=len(problem.constraints),
                success_criteria_count=len(problem.success_criteria),
                cycle_count=len(problem.cycles),
                solution_count=len(problem.solutions)
            ))
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(problem_responses)} problems",
            data={
                "problems": [p.dict() for p in problem_responses],
                "total_count": len(problem_responses),
                "limit": limit,
                "offset": offset
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get problems: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get problems: {str(e)}")

@app.get("/api/v1/problems/{problem_id}", response_model=ResponseModel)
async def get_problem(
    problem_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get a specific problem by ID"""
    try:
        problem_uuid = uuid.UUID(problem_id)
        problem = ProblemRepository.get_problem(problem_uuid)
        
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        return ResponseModel(
            success=True,
            message="Problem retrieved successfully",
            data={
                "problem": ProblemResponse(
                    id=str(problem.id),
                    title=problem.title,
                    description=problem.description,
                    domain=problem.domain,
                    complexity=problem.complexity,
                    priority=problem.priority,
                    status=problem.status,
                    created_at=problem.created_at,
                    updated_at=problem.updated_at,
                    due_date=problem.due_date,
                    stakeholder_count=len(problem.stakeholders),
                    constraint_count=len(problem.constraints),
                    success_criteria_count=len(problem.success_criteria),
                    cycle_count=len(problem.cycles),
                    solution_count=len(problem.solutions)
                ).dict()
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid problem ID format")
    except Exception as e:
        logger.error(f"Failed to get problem {problem_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get problem: {str(e)}")

@app.put("/api/v1/problems/{problem_id}", response_model=ResponseModel)
async def update_problem(
    problem_id: str,
    request: ProblemUpdateRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Update a problem"""
    try:
        problem_uuid = uuid.UUID(problem_id)
        
        # Get current problem for audit
        current_problem = ProblemRepository.get_problem(problem_uuid)
        if not current_problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Update problem
        updated_problem = ProblemRepository.update_problem(
            problem_uuid,
            **request.dict(exclude_unset=True)
        )
        
        if not updated_problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Log audit action
        background_tasks.add_task(
            AuditLogRepository.log_action,
            action="update",
            resource_type="problem",
            resource_id=problem_uuid,
            user_id=current_user,
            old_values={
                "title": current_problem.title,
                "status": current_problem.status,
                "priority": current_problem.priority
            },
            new_values=request.dict(exclude_unset=True)
        )
        
        return ResponseModel(
            success=True,
            message="Problem updated successfully",
            data={
                "problem_id": str(updated_problem.id),
                "title": updated_problem.title,
                "status": updated_problem.status,
                "updated_at": updated_problem.updated_at
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid problem ID format")
    except Exception as e:
        logger.error(f"Failed to update problem {problem_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update problem: {str(e)}")

# Cycle Management Endpoints

@app.post("/api/v1/cycles", response_model=ResponseModel)
async def create_cycle(
    request: CycleCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Create a new cycle for a problem"""
    try:
        problem_uuid = uuid.UUID(request.problem_id)
        
        # Verify problem exists
        problem = ProblemRepository.get_problem(problem_uuid)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Create cycle
        cycle = CycleRepository.create_cycle(
            problem_id=problem_uuid,
            cycle_number=request.cycle_number,
            max_iterations=request.max_iterations,
            status="pending"
        )
        
        # Log audit action
        background_tasks.add_task(
            AuditLogRepository.log_action,
            action="create",
            resource_type="cycle",
            resource_id=cycle.id,
            user_id=current_user,
            new_values=request.dict()
        )
        
        return ResponseModel(
            success=True,
            message="Cycle created successfully",
            data={
                "cycle_id": str(cycle.id),
                "problem_id": str(cycle.problem_id),
                "cycle_number": cycle.cycle_number,
                "status": cycle.status
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid problem ID format")
    except Exception as e:
        logger.error(f"Failed to create cycle: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create cycle: {str(e)}")

@app.get("/api/v1/cycles/{cycle_id}", response_model=ResponseModel)
async def get_cycle(
    cycle_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get a specific cycle by ID"""
    try:
        cycle_uuid = uuid.UUID(cycle_id)
        cycle = CycleRepository.get_cycle(cycle_uuid)
        
        if not cycle:
            raise HTTPException(status_code=404, detail="Cycle not found")
        
        return ResponseModel(
            success=True,
            message="Cycle retrieved successfully",
            data={
                "cycle": CycleResponse(
                    id=str(cycle.id),
                    problem_id=str(cycle.problem_id),
                    cycle_number=cycle.cycle_number,
                    status=cycle.status,
                    phase=cycle.phase,
                    started_at=cycle.started_at,
                    completed_at=cycle.completed_at,
                    total_duration=cycle.total_duration,
                    confidence_score=cycle.confidence_score,
                    max_iterations=cycle.max_iterations,
                    current_iteration=cycle.current_iteration,
                    enterprise_results_count=len(cycle.enterprise_results)
                ).dict()
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid cycle ID format")
    except Exception as e:
        logger.error(f"Failed to get cycle {cycle_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cycle: {str(e)}")

@app.post("/api/v1/cycles/{cycle_id}/execute", response_model=ResponseModel)
async def execute_cycle(
    cycle_id: str,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Execute a cycle (start the problem-solving process)"""
    try:
        cycle_uuid = uuid.UUID(cycle_id)
        cycle = CycleRepository.get_cycle(cycle_uuid)
        
        if not cycle:
            raise HTTPException(status_code=404, detail="Cycle not found")
        
        if cycle.status != "pending":
            raise HTTPException(status_code=400, detail="Cycle is not in pending status")
        
        # Update cycle status to in_progress
        CycleRepository.update_cycle_status(cycle_uuid, "in_progress")
        
        # Start cycle execution in background
        background_tasks.add_task(execute_cycle_background, cycle_uuid, current_user)
        
        return ResponseModel(
            success=True,
            message="Cycle execution started",
            data={
                "cycle_id": str(cycle_uuid),
                "status": "in_progress",
                "message": "Cycle execution is running in the background"
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid cycle ID format")
    except Exception as e:
        logger.error(f"Failed to execute cycle {cycle_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute cycle: {str(e)}")

async def execute_cycle_background(cycle_id: uuid.UUID, user_id: str):
    """Background task to execute a cycle"""
    try:
        logger.info(f"Starting background execution of cycle {cycle_id}")
        
        # Get cycle and problem
        cycle = CycleRepository.get_cycle(cycle_id)
        if not cycle:
            logger.error(f"Cycle {cycle_id} not found")
            return
        
        problem = ProblemRepository.get_problem(cycle.problem_id)
        if not problem:
            logger.error(f"Problem {cycle.problem_id} not found")
            return
        
        # Convert to ProblemStatement
        problem_statement = ProblemStatement(
            title=problem.title,
            description=problem.description,
            domain=problem.domain,
            complexity=ProblemComplexity(problem.complexity),
            stakeholders=[s.name for s in problem.stakeholders],
            constraints=problem.constraints,
            success_criteria=[c.name for c in problem.success_criteria]
        )
        
        # Execute cycle using AI-enhanced workflow
        session = await ai_workflow_engine.start_ai_enhanced_session(problem_statement, user_id)
        
        # Process through all enterprises
        enterprises = EnterpriseRepository.get_all_enterprises()
        for enterprise in enterprises:
            # Create enterprise result
            result = EnterpriseResultRepository.create_enterprise_result(
                cycle_id=cycle_id,
                enterprise_id=enterprise.id,
                status="in_progress",
                started_at=datetime.utcnow()
            )
            
            # Simulate enterprise processing (in real implementation, this would call the actual enterprise)
            await asyncio.sleep(1)  # Simulate processing time
            
            # Update result
            EnterpriseResultRepository.update_enterprise_result(
                result.id,
                status="completed",
                confidence_score=0.85,
                processing_time=1.0,
                specialized_analysis={"approach": f"{enterprise.name} analysis"},
                recommendations=[f"Recommendation from {enterprise.name}"],
                reasoning=f"Analysis reasoning from {enterprise.name}",
                key_insights=[f"Key insight from {enterprise.name}"],
                ai_enhanced=True,
                ai_model_used="gpt-4",
                ai_tokens_used=500,
                ai_processing_time=0.8
            )
        
        # Complete the cycle
        CycleRepository.update_cycle_status(cycle_id, "completed")
        
        logger.info(f"Cycle {cycle_id} execution completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to execute cycle {cycle_id} in background: {str(e)}")
        CycleRepository.update_cycle_status(cycle_id, "failed")

# Solution Management Endpoints

@app.post("/api/v1/solutions", response_model=ResponseModel)
async def create_solution(
    request: SolutionCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Create a new solution"""
    try:
        problem_uuid = uuid.UUID(request.problem_id)
        cycle_uuid = uuid.UUID(request.cycle_id)
        
        # Verify problem and cycle exist
        problem = ProblemRepository.get_problem(problem_uuid)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        cycle = CycleRepository.get_cycle(cycle_uuid)
        if not cycle:
            raise HTTPException(status_code=404, detail="Cycle not found")
        
        # Create solution
        solution = SolutionRepository.create_solution(
            problem_id=problem_uuid,
            cycle_id=cycle_uuid,
            title=request.title,
            description=request.description,
            created_by=current_user,
            approach=request.approach,
            confidence_score=request.confidence_score,
            feasibility_score=request.feasibility_score,
            impact_score=request.impact_score,
            estimated_cost=request.estimated_cost,
            estimated_duration=request.estimated_duration,
            risk_level=request.risk_level
        )
        
        # Log audit action
        background_tasks.add_task(
            AuditLogRepository.log_action,
            action="create",
            resource_type="solution",
            resource_id=solution.id,
            user_id=current_user,
            new_values=request.dict()
        )
        
        return ResponseModel(
            success=True,
            message="Solution created successfully",
            data={
                "solution_id": str(solution.id),
                "title": solution.title,
                "confidence_score": solution.confidence_score,
                "feasibility_score": solution.feasibility_score
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except Exception as e:
        logger.error(f"Failed to create solution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create solution: {str(e)}")

@app.get("/api/v1/solutions", response_model=ResponseModel)
async def get_solutions(
    problem_id: Optional[str] = None,
    cycle_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: str = Depends(get_current_user)
):
    """Get solutions with filtering"""
    try:
        if problem_id:
            problem_uuid = uuid.UUID(problem_id)
            solutions = SolutionRepository.get_solutions_for_problem(problem_uuid)
        else:
            # Get all solutions (implement this in repository if needed)
            solutions = []
        
        solution_responses = []
        for solution in solutions[offset:offset+limit]:
            solution_responses.append(SolutionResponse(
                id=str(solution.id),
                problem_id=str(solution.problem_id),
                cycle_id=str(solution.cycle_id),
                title=solution.title,
                description=solution.description,
                status=solution.status,
                confidence_score=solution.confidence_score,
                feasibility_score=solution.feasibility_score,
                impact_score=solution.impact_score,
                estimated_cost=solution.estimated_cost,
                estimated_duration=solution.estimated_duration,
                risk_level=solution.risk_level,
                created_at=solution.created_at,
                updated_at=solution.updated_at
            ))
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(solution_responses)} solutions",
            data={
                "solutions": [s.dict() for s in solution_responses],
                "total_count": len(solution_responses),
                "limit": limit,
                "offset": offset
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except Exception as e:
        logger.error(f"Failed to get solutions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get solutions: {str(e)}")

# Analytics Endpoints

@app.get("/api/v1/analytics/problems", response_model=ResponseModel)
async def get_problem_analytics(current_user: str = Depends(get_current_user)):
    """Get problem analytics and statistics"""
    try:
        stats = AnalyticsRepository.get_problem_statistics()
        
        return ResponseModel(
            success=True,
            message="Problem analytics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Failed to get problem analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get problem analytics: {str(e)}")

@app.get("/api/v1/analytics/cycles", response_model=ResponseModel)
async def get_cycle_analytics(current_user: str = Depends(get_current_user)):
    """Get cycle analytics and statistics"""
    try:
        stats = AnalyticsRepository.get_cycle_statistics()
        
        return ResponseModel(
            success=True,
            message="Cycle analytics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Failed to get cycle analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cycle analytics: {str(e)}")

@app.get("/api/v1/analytics/solutions", response_model=ResponseModel)
async def get_solution_analytics(current_user: str = Depends(get_current_user)):
    """Get solution analytics and statistics"""
    try:
        stats = AnalyticsRepository.get_solution_statistics()
        
        return ResponseModel(
            success=True,
            message="Solution analytics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Failed to get solution analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get solution analytics: {str(e)}")

# Enterprise Endpoints

@app.get("/api/v1/enterprises", response_model=ResponseModel)
async def get_enterprises(current_user: str = Depends(get_current_user)):
    """Get all enterprises"""
    try:
        enterprises = EnterpriseRepository.get_all_enterprises()
        
        enterprise_data = []
        for enterprise in enterprises:
            enterprise_data.append({
                "id": str(enterprise.id),
                "name": enterprise.name,
                "type": enterprise.type,
                "description": enterprise.description,
                "color": enterprise.color,
                "symbol": enterprise.symbol,
                "core_principle": enterprise.core_principle,
                "expertise_areas": enterprise.expertise_areas,
                "processing_order": enterprise.processing_order,
                "is_active": enterprise.is_active
            })
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(enterprise_data)} enterprises",
            data={
                "enterprises": enterprise_data
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get enterprises: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get enterprises: {str(e)}")

# ============================================================================
# PERPETUAL THINKING SYSTEM API ENDPOINTS
# ============================================================================

# Import perpetual thinking system components
try:
    from ..integrations.unified_perpetual_thinking_system import (
        UnifiedPerpetualThinkingEngine, CycleType, PatternType,
        PerpetualAIThinkingEngine, AIEnhancementLevel, AIThinkingMode,
        AICycleEnhancement
    )
    from ..integrations.meta_cyclical_architecture import MetaCyclicalArchitecture, MetaCycleType
    from ...applications.enhanced_master_orchestration_system import EnhancedMasterOrchestrationSystem, OrchestrationMode
    from ..database.unified_database_service import DatabaseService, PerpetualDatabaseService
    from ..integrations.perpetual_guardrail_integration import (
        PerpetualGuardrailIntegration, PerpetualPolicyEnforcer,
        PerpetualPolicyType, PerpetualActionType, PerpetualPolicyContext
    )
    from ..integrations.perpetual_108_cycle_integration import (
        Perpetual108CycleIntegration, PerpetualFractalMode, FractalPerpetualMapping,
        FractalPerpetualContext, FractalPerpetualResult
    )
    from ..integrations.unified_fractal_system import (
        UnifiedFractal108CycleSystem, EnterpriseType, SquadType, RedundancyPassType
    )
    PERPETUAL_SYSTEM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Perpetual thinking system not available: {e}")
    PERPETUAL_SYSTEM_AVAILABLE = False

# Global perpetual system components
perpetual_engine = None
perpetual_ai_engine = None
orchestration_system = None
perpetual_db_service = None
perpetual_guardrail_integration = None
perpetual_policy_enforcer = None
fractal_108_cycle_system = None
perpetual_108_cycle_integration = None

# Pydantic models for perpetual thinking system
class PerpetualSessionCreateRequest(BaseModel):
    """Request model for creating a perpetual thinking session"""
    session_name: str = Field(..., min_length=1, max_length=255, description="Session name")
    initial_input: str = Field(..., min_length=1, description="Initial input for the session")
    mode: str = Field(default="collaborative", description="Orchestration mode")
    goals: List[str] = Field(default=[], description="Session goals")
    success_criteria: List[str] = Field(default=[], description="Success criteria")
    ai_enhancement_level: str = Field(default="enhanced", description="AI enhancement level")
    ai_learning_enabled: bool = Field(default=True, description="Enable AI learning")
    ai_adaptation_enabled: bool = Field(default=True, description="Enable AI adaptation")
    ai_breakthrough_detection: bool = Field(default=True, description="Enable AI breakthrough detection")

class PerpetualSessionResponse(BaseModel):
    """Response model for perpetual thinking session"""
    session_id: str
    session_name: str
    initial_input: str
    current_input: str
    current_cycle_number: int
    status: str
    mode: str
    goals: List[str]
    success_criteria: List[str]
    created_at: datetime
    updated_at: datetime
    summary_metrics: Optional[Dict[str, Any]] = None

class PerpetualCycleResponse(BaseModel):
    """Response model for perpetual cycle"""
    cycle_id: str
    session_id: str
    cycle_number: int
    cycle_type: str
    status: str
    input_text: str
    output_text: Optional[str] = None
    confidence_score: float
    effectiveness_score: float
    relevance_score: float
    pattern_detected: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None

class BreakthroughResponse(BaseModel):
    """Response model for breakthrough moments"""
    breakthrough_id: str
    session_id: str
    cycle_id: str
    breakthrough_type: str
    insight_description: str
    impact_score: float
    occurred_at: datetime

class MetaCycleResponse(BaseModel):
    """Response model for meta-cycles"""
    meta_cycle_id: str
    session_id: str
    meta_cycle_type: str
    target_metric: str
    initial_value: float
    final_value: float
    improvement: float
    confidence_in_changes: float
    started_at: datetime
    completed_at: Optional[datetime] = None

# Perpetual Thinking System Endpoints

@app.post("/api/v1/perpetual/sessions", response_model=ResponseModel)
async def create_perpetual_session(
    request: PerpetualSessionCreateRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new AI-enhanced perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_ai_engine:
        raise HTTPException(status_code=503, detail="AI-enhanced perpetual thinking system not available")
    
    try:
        # Convert AI enhancement level string to enum
        try:
            ai_enhancement_level = AIEnhancementLevel(request.ai_enhancement_level)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid AI enhancement level: {request.ai_enhancement_level}")
        
        # Use policy enforcer to create session with policy enforcement
        if perpetual_policy_enforcer:
            allow, session_id, policy_meta = await perpetual_policy_enforcer.create_session_with_policy(
                session_name=request.session_name,
                initial_input=request.initial_input,
                user_id=credentials.credentials  # Use token as user ID for demo
            )
            
            if not allow:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Session creation denied by policy: {policy_meta}"
                )
        else:
            # Fallback to direct AI-enhanced perpetual cycle creation
            session_id = await perpetual_ai_engine.start_ai_enhanced_perpetual_cycle(
                initial_input=request.initial_input,
                ai_enhancement_level=ai_enhancement_level,
                cycle_type=CycleType.EXPLORATION,
                max_cycles=None  # No limit for perpetual sessions
            )
        
        # Save to database
        if perpetual_db_service:
            session_data = {
                'session_id': session_id,
                'session_name': request.session_name,
                'initial_input': request.initial_input,
                'current_input': request.initial_input,
                'current_cycle_number': 0,
                'status': 'active',
                'mode': request.mode,
                'goals': request.goals,
                'success_criteria': request.success_criteria,
                'ai_enhancement_level': request.ai_enhancement_level,
                'ai_learning_enabled': request.ai_learning_enabled,
                'ai_adaptation_enabled': request.ai_adaptation_enabled,
                'ai_breakthrough_detection': request.ai_breakthrough_detection,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
                'ended_at': None,
                'session_data': {},
                'summary_metrics': {}
            }
            await perpetual_db_service.save_perpetual_session(session_data)
        
        return ResponseModel(
            success=True,
            message=f"AI-enhanced perpetual thinking session '{request.session_name}' created successfully",
            data={
                "session_id": session_id,
                "session_name": request.session_name,
                "status": "active",
                "ai_enhancement_level": request.ai_enhancement_level,
                "ai_learning_enabled": request.ai_learning_enabled,
                "ai_adaptation_enabled": request.ai_adaptation_enabled,
                "ai_breakthrough_detection": request.ai_breakthrough_detection
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to create AI-enhanced perpetual session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create AI-enhanced perpetual session: {str(e)}")

@app.get("/api/v1/perpetual/sessions/{session_id}", response_model=ResponseModel)
async def get_perpetual_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        # Get from orchestration system
        orchestration_session = orchestration_system.get_orchestration_session_status(session_id)
        
        if not orchestration_session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get from database if available
        db_session = None
        if perpetual_db_service:
            db_session = await perpetual_db_service.get_perpetual_session(session_id)
        
        session_data = {
            "session_id": session_id,
            "session_name": orchestration_session.session_name,
            "initial_input": orchestration_session.initial_input,
            "current_input": orchestration_session.current_input,
            "current_cycle_number": orchestration_session.current_cycle_number,
            "status": orchestration_session.status,
            "mode": orchestration_session.mode.value if hasattr(orchestration_session.mode, 'value') else str(orchestration_session.mode),
            "goals": orchestration_session.goals,
            "success_criteria": orchestration_session.success_criteria,
            "created_at": orchestration_session.created_at,
            "updated_at": orchestration_session.updated_at,
            "summary_metrics": orchestration_session.summary_metrics
        }
        
        return ResponseModel(
            success=True,
            message="Perpetual session retrieved successfully",
            data=session_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get perpetual session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get perpetual session: {str(e)}")

@app.get("/api/v1/perpetual/sessions", response_model=ResponseModel)
async def list_perpetual_sessions(
    status: Optional[str] = None,
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """List perpetual thinking sessions"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        # Get active sessions from orchestration system
        active_sessions = list(orchestration_system.orchestration_sessions.values())
        
        # Filter by status if provided
        if status:
            active_sessions = [s for s in active_sessions if s.status == status]
        
        # Limit results
        active_sessions = active_sessions[:limit]
        
        sessions_data = []
        for session in active_sessions:
            sessions_data.append({
                "session_id": session.session_id,
                "session_name": session.session_name,
                "status": session.status,
                "mode": session.mode.value if hasattr(session.mode, 'value') else str(session.mode),
                "current_cycle_number": session.current_cycle_number,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "summary_metrics": session.summary_metrics
            })
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(sessions_data)} perpetual sessions",
            data={
                "sessions": sessions_data,
                "total_count": len(sessions_data)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to list perpetual sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list perpetual sessions: {str(e)}")

@app.get("/api/v1/perpetual/sessions/{session_id}/cycles", response_model=ResponseModel)
async def get_perpetual_session_cycles(
    session_id: str,
    limit: int = 100,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get cycles for a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        # Get cycles from database
        if perpetual_db_service:
            cycles = await perpetual_db_service.get_session_cycles(session_id, limit)
        else:
            cycles = []
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(cycles)} cycles for session {session_id}",
            data={
                "session_id": session_id,
                "cycles": cycles,
                "total_count": len(cycles)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get session cycles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session cycles: {str(e)}")

@app.get("/api/v1/perpetual/sessions/{session_id}/breakthroughs", response_model=ResponseModel)
async def get_perpetual_session_breakthroughs(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get breakthrough moments for a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        # Get breakthroughs from orchestration system
        orchestration_session = orchestration_system.get_orchestration_session_status(session_id)
        
        if not orchestration_session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get breakthroughs from perpetual engine
        perpetual_session = perpetual_engine.get_session_status(orchestration_session.current_perpetual_session_id)
        
        breakthroughs = []
        if perpetual_session:
            breakthroughs = perpetual_session.breakthrough_moments
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(breakthroughs)} breakthrough moments",
            data={
                "session_id": session_id,
                "breakthroughs": breakthroughs,
                "total_count": len(breakthroughs)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session breakthroughs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session breakthroughs: {str(e)}")

@app.post("/api/v1/perpetual/sessions/{session_id}/pause", response_model=ResponseModel)
async def pause_perpetual_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Pause a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        await orchestration_system.pause_orchestration_session(session_id)
        
        return ResponseModel(
            success=True,
            message=f"Perpetual session {session_id} paused successfully",
            data={"session_id": session_id, "status": "paused"}
        )
        
    except Exception as e:
        logger.error(f"Failed to pause perpetual session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to pause perpetual session: {str(e)}")

@app.post("/api/v1/perpetual/sessions/{session_id}/resume", response_model=ResponseModel)
async def resume_perpetual_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Resume a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        await orchestration_system.resume_orchestration_session(session_id)
        
        return ResponseModel(
            success=True,
            message=f"Perpetual session {session_id} resumed successfully",
            data={"session_id": session_id, "status": "active"}
        )
        
    except Exception as e:
        logger.error(f"Failed to resume perpetual session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resume perpetual session: {str(e)}")

@app.post("/api/v1/perpetual/sessions/{session_id}/stop", response_model=ResponseModel)
async def stop_perpetual_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Stop a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        await orchestration_system.stop_orchestration_session(session_id)
        
        return ResponseModel(
            success=True,
            message=f"Perpetual session {session_id} stopped successfully",
            data={"session_id": session_id, "status": "completed"}
        )
        
    except Exception as e:
        logger.error(f"Failed to stop perpetual session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop perpetual session: {str(e)}")

@app.get("/api/v1/perpetual/metrics", response_model=ResponseModel)
async def get_perpetual_system_metrics(
    metric_name: Optional[str] = None,
    limit: int = 100,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get perpetual thinking system metrics"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        # Get metrics from database
        if perpetual_db_service:
            metrics = await perpetual_db_service.get_system_metrics(metric_name, limit)
        else:
            metrics = []
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(metrics)} system metrics",
            data={
                "metrics": metrics,
                "total_count": len(metrics)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")

@app.get("/api/v1/perpetual/status", response_model=ResponseModel)
async def get_perpetual_system_status(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get AI-enhanced perpetual thinking system status"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        # Get system status
        active_sessions = len(orchestration_system.orchestration_sessions) if orchestration_system else 0
        total_sessions = len(orchestration_system.session_history) if orchestration_system else 0
        active_ai_sessions = len(perpetual_ai_engine.ai_sessions) if perpetual_ai_engine else 0
        
        status_data = {
            "system_available": True,
            "active_sessions": active_sessions,
            "total_sessions": total_sessions,
            "active_ai_sessions": active_ai_sessions,
            "database_available": perpetual_db_service is not None,
            "perpetual_engine_available": perpetual_engine is not None,
            "perpetual_ai_engine_available": perpetual_ai_engine is not None,
            "orchestration_system_available": orchestration_system is not None,
            "guardrail_integration_available": perpetual_guardrail_integration is not None,
            "policy_enforcer_available": perpetual_policy_enforcer is not None,
            "ai_enhancement_available": perpetual_ai_engine is not None
        }
        
        return ResponseModel(
            success=True,
            message="AI-enhanced perpetual thinking system status retrieved successfully",
            data=status_data
        )
        
    except Exception as e:
        logger.error(f"Failed to get system status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

# AI-Enhanced Perpetual Thinking Endpoints

@app.get("/api/v1/perpetual/ai/sessions/{session_id}/analytics", response_model=ResponseModel)
async def get_ai_session_analytics(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get AI session analytics for a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_ai_engine:
        raise HTTPException(status_code=503, detail="AI-enhanced perpetual thinking system not available")
    
    try:
        analytics = await perpetual_ai_engine.get_ai_session_analytics(session_id)
        
        if analytics is None:
            raise HTTPException(status_code=404, detail="AI session not found")
        
        return ResponseModel(
            success=True,
            message="AI session analytics retrieved successfully",
            data=analytics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get AI session analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI session analytics: {str(e)}")

@app.get("/api/v1/perpetual/ai/sessions/{session_id}/status", response_model=ResponseModel)
async def get_ai_enhanced_cycle_status(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get AI-enhanced cycle status for a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_ai_engine:
        raise HTTPException(status_code=503, detail="AI-enhanced perpetual thinking system not available")
    
    try:
        # Get AI-enhanced cycle status
        status = await perpetual_ai_engine.get_ai_enhanced_cycle_status(session_id)
        
        if status is None:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return ResponseModel(
            success=True,
            message="AI-enhanced cycle status retrieved successfully",
            data=status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get AI-enhanced cycle status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI-enhanced cycle status: {str(e)}")

@app.get("/api/v1/perpetual/ai/sessions", response_model=ResponseModel)
async def list_ai_sessions(
    ai_enhancement_level: Optional[str] = None,
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """List AI-enhanced perpetual thinking sessions"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_ai_engine:
        raise HTTPException(status_code=503, detail="AI-enhanced perpetual thinking system not available")
    
    try:
        # Get AI sessions
        ai_sessions = list(perpetual_ai_engine.ai_sessions.values())
        
        # Filter by AI enhancement level if provided
        if ai_enhancement_level:
            try:
                enhancement_level = AIEnhancementLevel(ai_enhancement_level)
                ai_sessions = [s for s in ai_sessions if s.ai_enhancement_level == enhancement_level]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid AI enhancement level: {ai_enhancement_level}")
        
        # Limit results
        ai_sessions = ai_sessions[:limit]
        
        sessions_data = []
        for session in ai_sessions:
            sessions_data.append({
                "session_id": session.session_id,
                "ai_enhancement_level": session.ai_enhancement_level.value,
                "ai_learning_enabled": session.ai_learning_enabled,
                "ai_adaptation_enabled": session.ai_adaptation_enabled,
                "ai_breakthrough_detection": session.ai_breakthrough_detection,
                "ai_cycle_enhancements_count": len(session.ai_cycle_enhancements),
                "ai_session_insights_count": len(session.ai_session_insights),
                "ai_learning_history_count": len(session.ai_learning_history),
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "ai_collaborative_metrics": {
                    "ai_contribution_score": session.ai_collaborative_metrics.ai_contribution_score,
                    "human_contribution_score": session.ai_collaborative_metrics.human_contribution_score,
                    "synergy_score": session.ai_collaborative_metrics.synergy_score,
                    "wisdom_density": session.ai_collaborative_metrics.wisdom_density,
                    "creative_potential": session.ai_collaborative_metrics.creative_potential,
                    "learning_velocity": session.ai_collaborative_metrics.learning_velocity,
                    "adaptation_rate": session.ai_collaborative_metrics.adaptation_rate
                }
            })
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(sessions_data)} AI-enhanced sessions",
            data={
                "sessions": sessions_data,
                "total_count": len(sessions_data),
                "filters": {
                    "ai_enhancement_level": ai_enhancement_level,
                    "limit": limit
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list AI sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list AI sessions: {str(e)}")

# Policy Enforcement and Audit Logging Endpoints

@app.get("/api/v1/perpetual/audit/logs", response_model=ResponseModel)
async def get_perpetual_audit_logs(
    session_id: Optional[str] = None,
    operation_type: Optional[str] = None,
    limit: int = 100,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get audit logs for perpetual thinking operations"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_guardrail_integration:
        raise HTTPException(status_code=503, detail="Perpetual guardrail integration not available")
    
    try:
        logs = perpetual_guardrail_integration.get_audit_logs(
            session_id=session_id,
            operation_type=operation_type,
            limit=limit
        )
        
        # Convert logs to dict format for JSON serialization
        logs_data = []
        for log in logs:
            logs_data.append({
                "log_id": log.log_id,
                "timestamp": log.timestamp.isoformat(),
                "operation_type": log.operation_type,
                "agent_id": log.agent_id,
                "resource_service": log.resource_service,
                "resource_action": log.resource_action,
                "policy_decision": log.policy_decision,
                "policy_packages": log.policy_packages,
                "obligations": log.obligations,
                "context": log.context,
                "explanation": log.explanation,
                "latency_ms": log.latency_ms,
                "session_id": log.session_id,
                "cycle_id": log.cycle_id,
                "user_id": log.user_id,
                "violations": log.violations,
                "risk_score": log.risk_score
            })
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(logs_data)} audit logs",
            data={
                "logs": logs_data,
                "total_count": len(logs_data),
                "filters": {
                    "session_id": session_id,
                    "operation_type": operation_type,
                    "limit": limit
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get audit logs: {str(e)}")

@app.get("/api/v1/perpetual/audit/violations", response_model=ResponseModel)
async def get_perpetual_policy_violations(
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get policy violations (denied operations)"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_guardrail_integration:
        raise HTTPException(status_code=503, detail="Perpetual guardrail integration not available")
    
    try:
        violations = perpetual_guardrail_integration.get_policy_violations(limit=limit)
        
        # Convert violations to dict format
        violations_data = []
        for violation in violations:
            violations_data.append({
                "log_id": violation.log_id,
                "timestamp": violation.timestamp.isoformat(),
                "operation_type": violation.operation_type,
                "agent_id": violation.agent_id,
                "resource_service": violation.resource_service,
                "resource_action": violation.resource_action,
                "policy_packages": violation.policy_packages,
                "obligations": violation.obligations,
                "context": violation.context,
                "explanation": violation.explanation,
                "session_id": violation.session_id,
                "cycle_id": violation.cycle_id,
                "user_id": violation.user_id,
                "violations": violation.violations,
                "risk_score": violation.risk_score
            })
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(violations_data)} policy violations",
            data={
                "violations": violations_data,
                "total_count": len(violations_data),
                "limit": limit
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get policy violations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get policy violations: {str(e)}")

@app.get("/api/v1/perpetual/audit/risk-summary", response_model=ResponseModel)
async def get_perpetual_risk_summary(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get risk summary for perpetual thinking operations"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_guardrail_integration:
        raise HTTPException(status_code=503, detail="Perpetual guardrail integration not available")
    
    try:
        risk_summary = perpetual_guardrail_integration.get_risk_summary()
        
        return ResponseModel(
            success=True,
            message="Risk summary retrieved successfully",
            data=risk_summary
        )
        
    except Exception as e:
        logger.error(f"Failed to get risk summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get risk summary: {str(e)}")

@app.post("/api/v1/perpetual/policy/evaluate", response_model=ResponseModel)
async def evaluate_perpetual_policy(
    operation_type: str,
    action_type: str,
    agent_id: str,
    context: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Evaluate a perpetual thinking operation against policies"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_guardrail_integration:
        raise HTTPException(status_code=503, detail="Perpetual guardrail integration not available")
    
    try:
        # Convert string enums to enum objects
        try:
            op_type = PerpetualPolicyType(operation_type)
            act_type = PerpetualActionType(action_type)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid operation or action type: {e}")
        
        # Create policy context
        policy_context = PerpetualPolicyContext(**context)
        
        # Evaluate policy
        allow, meta = await perpetual_guardrail_integration.evaluate_perpetual_operation(
            operation_type=op_type,
            action_type=act_type,
            agent_id=agent_id,
            context=policy_context
        )
        
        return ResponseModel(
            success=True,
            message="Policy evaluation completed",
            data={
                "allow": allow,
                "metadata": meta,
                "operation_type": operation_type,
                "action_type": action_type,
                "agent_id": agent_id
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to evaluate policy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate policy: {str(e)}")

# 108-Cycle Fractal Integration Endpoints

class FractalPerpetualSessionRequest(BaseModel):
    """Request model for creating a fractal-perpetual integrated session"""
    session_name: str = Field(..., min_length=1, max_length=255, description="Session name")
    initial_input: str = Field(..., min_length=1, description="Initial input for the session")
    integration_mode: str = Field(default="integrated", description="Integration mode")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")

class FractalPerpetualSessionResponse(BaseModel):
    """Response model for fractal-perpetual integrated session"""
    session_id: str
    session_name: str
    integration_mode: str
    fractal_result: Dict[str, Any]
    perpetual_result: Dict[str, Any]
    integration_insights: Dict[str, Any]
    cross_system_patterns: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    execution_time: float
    success: bool
    errors: List[str] = []

@app.post("/api/v1/fractal-perpetual/sessions", response_model=ResponseModel)
async def create_fractal_perpetual_session(
    request: FractalPerpetualSessionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new fractal-perpetual integrated session"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_108_cycle_integration:
        raise HTTPException(status_code=503, detail="Fractal-perpetual integration not available")
    
    try:
        # Convert integration mode string to enum
        try:
            integration_mode = PerpetualFractalMode(request.integration_mode)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid integration mode: {request.integration_mode}")
        
        # Execute integrated session
        result = await perpetual_108_cycle_integration.execute_integrated_session(
            session_name=request.session_name,
            initial_input=request.initial_input,
            integration_mode=integration_mode,
            context=request.context
        )
        
        return ResponseModel(
            success=result.success,
            message=f"Fractal-perpetual session '{request.session_name}' executed successfully",
            data={
                "session_id": str(uuid.uuid4()),
                "session_name": request.session_name,
                "integration_mode": request.integration_mode,
                "fractal_result": result.fractal_result,
                "perpetual_result": result.perpetual_result,
                "integration_insights": result.integration_insights,
                "cross_system_patterns": result.cross_system_patterns,
                "performance_metrics": result.performance_metrics,
                "execution_time": result.execution_time,
                "success": result.success,
                "errors": result.errors
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to create fractal-perpetual session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create fractal-perpetual session: {str(e)}")

@app.get("/api/v1/fractal-perpetual/analytics", response_model=ResponseModel)
async def get_fractal_perpetual_analytics(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get analytics for fractal-perpetual integration"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_108_cycle_integration:
        raise HTTPException(status_code=503, detail="Fractal-perpetual integration not available")
    
    try:
        analytics = perpetual_108_cycle_integration.get_integration_analytics()
        
        return ResponseModel(
            success=True,
            message="Fractal-perpetual analytics retrieved successfully",
            data=analytics
        )
        
    except Exception as e:
        logger.error(f"Failed to get fractal-perpetual analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get fractal-perpetual analytics: {str(e)}")

@app.get("/api/v1/fractal-perpetual/insights/{session_id}", response_model=ResponseModel)
async def get_fractal_perpetual_insights(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get cross-system insights for a fractal-perpetual session"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_108_cycle_integration:
        raise HTTPException(status_code=503, detail="Fractal-perpetual integration not available")
    
    try:
        insights = perpetual_108_cycle_integration.get_cross_system_insights(session_id)
        
        if insights is None:
            raise HTTPException(status_code=404, detail="Session insights not found")
        
        return ResponseModel(
            success=True,
            message="Cross-system insights retrieved successfully",
            data={
                "session_id": session_id,
                "insights": insights
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cross-system insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cross-system insights: {str(e)}")

@app.get("/api/v1/fractal-perpetual/status/{session_id}", response_model=ResponseModel)
async def get_fractal_perpetual_status(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get status of a fractal-perpetual integration session"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_108_cycle_integration:
        raise HTTPException(status_code=503, detail="Fractal-perpetual integration not available")
    
    try:
        status = perpetual_108_cycle_integration.get_integration_status(session_id)
        
        if status is None:
            raise HTTPException(status_code=404, detail="Session status not found")
        
        return ResponseModel(
            success=True,
            message="Integration session status retrieved successfully",
            data=status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get integration status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get integration status: {str(e)}")

# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseModel(
            success=False,
            message=exc.detail,
            data={"status_code": exc.status_code}
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ResponseModel(
            success=False,
            message="Internal server error",
            data={"error": str(exc)}
        ).dict()
    )

# Main execution
def main():
    """Main function to start the API server"""
    uvicorn.run(
        "src.cosmic_council.core.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
