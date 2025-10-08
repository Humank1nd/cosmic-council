"""
Main FastAPI application for the Cosmic Council system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging

from .routes import problems, solutions, cycles, analytics, health
from .middleware.auth import AuthMiddleware
from .middleware.logging import LoggingMiddleware
from ..core.services import (
    ProblemService, SolutionService, CycleService, 
    EnterpriseService, AnalyticsService
)

logger = logging.getLogger(__name__)

# Global service instances
problem_service: ProblemService = None
solution_service: SolutionService = None
cycle_service: CycleService = None
enterprise_service: EnterpriseService = None
analytics_service: AnalyticsService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global problem_service, solution_service, cycle_service, enterprise_service, analytics_service
    
    # Startup
    logger.info("Starting Cosmic Council API Server...")
    
    try:
        # Initialize services (with mock repositories for now)
        problem_service = ProblemService()
        solution_service = SolutionService()
        cycle_service = CycleService()
        enterprise_service = EnterpriseService()
        analytics_service = AnalyticsService()
        
        logger.info("Services initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    # Shutdown
    logger.info("Shutting down Cosmic Council API Server...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title="Cosmic Council API",
        description="AI-Powered Problem Solving System",
        version="2.0.0",
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
    
    app.add_middleware(AuthMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # Include routers
    app.include_router(problems.router, prefix="/api/v1/problems", tags=["problems"])
    app.include_router(solutions.router, prefix="/api/v1/solutions", tags=["solutions"])
    app.include_router(cycles.router, prefix="/api/v1/cycles", tags=["cycles"])
    app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
    app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
    
    return app


def get_problem_service() -> ProblemService:
    """Get the global problem service instance"""
    return problem_service


def get_solution_service() -> SolutionService:
    """Get the global solution service instance"""
    return solution_service


def get_cycle_service() -> CycleService:
    """Get the global cycle service instance"""
    return cycle_service


def get_enterprise_service() -> EnterpriseService:
    """Get the global enterprise service instance"""
    return enterprise_service


def get_analytics_service() -> AnalyticsService:
    """Get the global analytics service instance"""
    return analytics_service
