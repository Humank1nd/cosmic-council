"""
Cosmic Council Production API
FastAPI-based REST API with proper validation, error handling, and documentation.
"""

import asyncio
import time
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn

from .core import CosmicCouncilMVP
from .database_improved import ProductionDatabase, DatabaseConfig
from .config import CosmicCouncilConfig, get_config
from .logging_config import get_logger, RequestLogger, LogContext


# Pydantic models for API
class ProblemRequest(BaseModel):
    """Request model for problem solving."""
    problem: str = Field(..., min_length=1, max_length=10000, description="The problem to solve")
    domain: Optional[str] = Field(None, description="Problem domain (e.g., 'business', 'technical')")
    complexity: Optional[str] = Field("medium", pattern="^(low|medium|high)$", description="Problem complexity level")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the problem")
    
    @validator('problem')
    def validate_problem(cls, v):
        """Validate problem text."""
        if not v or not v.strip():
            raise ValueError("Problem cannot be empty")
        return v.strip()


class SolutionResponse(BaseModel):
    """Response model for individual enterprise solutions."""
    enterprise: str = Field(..., description="Enterprise name")
    solution: str = Field(..., description="Enterprise solution")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    processing_time: float = Field(..., description="Processing time in seconds")
    sources: List[str] = Field(default_factory=list, description="Source references")


class ProblemResponse(BaseModel):
    """Response model for complete problem solving."""
    problem_id: int = Field(..., description="Unique problem ID")
    session_id: str = Field(..., description="Unique session ID")
    problem: str = Field(..., description="Original problem text")
    solutions: List[SolutionResponse] = Field(..., description="Enterprise solutions")
    total_processing_time: float = Field(..., description="Total processing time in seconds")
    total_confidence: float = Field(..., ge=0.0, le=1.0, description="Average confidence score")
    created_at: datetime = Field(..., description="Creation timestamp")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(..., description="Current timestamp")
    database_connected: bool = Field(..., description="Database connection status")
    ai_provider: str = Field(..., description="AI provider being used")


class StatsResponse(BaseModel):
    """Database statistics response."""
    problems: int = Field(..., description="Total number of problems")
    solutions: int = Field(..., description="Total number of solutions")
    sessions: int = Field(..., description="Total number of sessions")
    average_confidence: float = Field(..., description="Average confidence score")
    total_cost: float = Field(..., description="Total cost in USD")
    total_tokens: int = Field(..., description="Total tokens used")


# Global instances
app = FastAPI(
    title="Cosmic Council MVP API",
    description="AI-Powered Problem Solving Framework",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

council: Optional[CosmicCouncilMVP] = None
database: Optional[ProductionDatabase] = None
logger = get_logger("cosmic_council.api")


# Dependency injection
async def get_council() -> CosmicCouncilMVP:
    """Get the Cosmic Council instance."""
    global council
    if council is None:
        council = CosmicCouncilMVP()
    return council


async def get_database() -> ProductionDatabase:
    """Get the database instance."""
    global database
    if database is None:
        config = get_config()
        db_config = DatabaseConfig(
            db_path=config.database.db_path,
            pool_size=config.database.pool_size,
            timeout=config.database.timeout
        )
        database = ProductionDatabase(db_config)
    return database


# Middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests and responses."""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    with RequestLogger(logger, request_id, request.method, request.url.path):
        response = await call_next(request)
        
        duration_ms = (time.time() - start_time) * 1000
        logger.log_response(
            request_id,
            response.status_code,
            duration_ms
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        return response


@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    """Simple rate limiting middleware."""
    # This is a basic implementation - in production, use Redis or similar
    config = get_config()
    if config.security.rate_limit_requests_per_minute > 0:
        # TODO: Implement proper rate limiting
        pass
    
    return await call_next(request)


# CORS configuration
config = get_config()
if config.security.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.security.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly for production
)


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.error(
        f"HTTP error: {exc.status_code} - {exc.detail}",
        context=LogContext.ERROR,
        status_code=exc.status_code,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "path": request.url.path,
                "timestamp": datetime.now().isoformat()
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(
        f"Unhandled error: {exc}",
        context=LogContext.ERROR,
        error_code=type(exc).__name__,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "path": request.url.path,
                "timestamp": datetime.now().isoformat()
            }
        }
    )


# API Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Cosmic Council MVP API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(db: ProductionDatabase = Depends(get_database)):
    """Health check endpoint."""
    config = get_config()
    
    # Check database connection
    try:
        stats = db.get_database_stats()
        database_connected = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        database_connected = False
    
    return HealthResponse(
        status="healthy" if database_connected else "degraded",
        version=config.app_version,
        timestamp=datetime.now(),
        database_connected=database_connected,
        ai_provider=config.ai.provider.value
    )


@app.post("/solve", response_model=ProblemResponse)
async def solve_problem(
    request: ProblemRequest,
    council: CosmicCouncilMVP = Depends(get_council),
    db: ProductionDatabase = Depends(get_database)
):
    """Solve a problem using the Cosmic Council framework."""
    start_time = time.time()
    session_id = str(uuid.uuid4())
    
    try:
        # Save problem to database
        problem_id = db.save_problem(
            request.problem,
            request.domain,
            request.complexity
        )
        
        # Solve the problem
        logger.info(
            f"Solving problem {problem_id}: {request.problem[:100]}...",
            context=LogContext.REQUEST,
            problem_id=str(problem_id),
            session_id=session_id
        )
        
        results = await council.solve_problem(request.problem, request.context)
        
        # Process results and save to database
        solutions = []
        total_confidence = 0.0
        session_metrics = {
            "total_confidence": 0.0,
            "total_processing_time": 0.0,
            "total_tokens_used": 0,
            "total_cost": 0.0
        }
        
        for enterprise_name, solution_text in results.items():
            # Extract metrics from solution (if available)
            confidence = 0.8  # Default confidence
            processing_time = 0.1  # Default processing time
            
            # Save solution to database
            solution_id = db.save_solution(
                problem_id,
                enterprise_name,
                solution_text,
                confidence=confidence,
                processing_time=processing_time
            )
            
            # Create response object
            solution_response = SolutionResponse(
                enterprise=enterprise_name,
                solution=solution_text,
                confidence=confidence,
                processing_time=processing_time,
                sources=[]  # TODO: Extract sources from solution
            )
            
            solutions.append(solution_response)
            total_confidence += confidence
            session_metrics["total_confidence"] += confidence
            session_metrics["total_processing_time"] += processing_time
        
        # Calculate averages
        avg_confidence = total_confidence / len(solutions) if solutions else 0.0
        session_metrics["total_confidence"] = avg_confidence
        
        # Save problem session
        db.save_problem_session(problem_id, results, session_metrics)
        
        total_processing_time = time.time() - start_time
        
        logger.info(
            f"Problem {problem_id} solved successfully",
            context=LogContext.RESPONSE,
            problem_id=str(problem_id),
            session_id=session_id,
            duration_ms=total_processing_time * 1000
        )
        
        return ProblemResponse(
            problem_id=problem_id,
            session_id=session_id,
            problem=request.problem,
            solutions=solutions,
            total_processing_time=total_processing_time,
            total_confidence=avg_confidence,
            created_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(
            f"Error solving problem: {e}",
            context=LogContext.ERROR,
            problem_id=str(problem_id) if 'problem_id' in locals() else None,
            session_id=session_id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to solve problem: {str(e)}"
        )


@app.get("/problems/{problem_id}", response_model=Dict[str, Any])
async def get_problem(
    problem_id: int,
    db: ProductionDatabase = Depends(get_database)
):
    """Get a specific problem and its solutions."""
    try:
        problem = db.get_problem(problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        solutions = db.get_solutions_for_problem(problem_id)
        
        return {
            "problem": problem,
            "solutions": solutions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving problem {problem_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve problem")


@app.get("/stats", response_model=StatsResponse)
async def get_stats(db: ProductionDatabase = Depends(get_database)):
    """Get database statistics."""
    try:
        stats = db.get_database_stats()
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


@app.get("/supra_enterprise", response_model=List[Dict[str, str]])
async def get_enterprises():
    """Get list of available enterprises."""
    return [
        {"name": "Red Owl", "type": "research", "emoji": "🔴🦉"},
        {"name": "Orange Orangutan", "type": "planning", "emoji": "🟠🦧"},
        {"name": "Yellow Honeybee", "type": "development", "emoji": "🟡🐝"},
        {"name": "Green Tortoise", "type": "budget", "emoji": "🟢🐢"},
        {"name": "Blue Dolphin", "type": "communication", "emoji": "🔵🐬"},
        {"name": "Purple Elephant", "type": "support", "emoji": "🟣🐘"}
    ]


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("🚀 Cosmic Council API starting up...")
    
    # Initialize configuration
    config = get_config()
    logger.info(f"Configuration loaded: {config.environment} mode")
    
    # Initialize database
    try:
        db = await get_database()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Initialize council
    try:
        council = await get_council()
        logger.info("✅ Cosmic Council initialized successfully")
    except Exception as e:
        logger.error(f"❌ Cosmic Council initialization failed: {e}")
        raise
    
    logger.info("🎉 Cosmic Council API ready to serve requests!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Cosmic Council API shutting down...")
    
    # Close database connections
    if database:
        database.close()
        logger.info("✅ Database connections closed")
    
    logger.info("👋 Cosmic Council API shutdown complete")


# CLI runner
def run_api(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the API server."""
    config = get_config()
    
    uvicorn.run(
        "cosmic_council.api:app",
        host=host,
        port=port,
        reload=reload and config.debug_mode,
        log_level=config.logging.level.value.lower()
    )


if __name__ == "__main__":
    run_api()
