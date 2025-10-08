"""
Cosmic Council Refinement Engine - Secure REST API
Provides secure REST API endpoints with authentication, authorization, and input validation.
"""

from typing import Dict, Any, Optional, List
import json
import logging
import hashlib
import os
from datetime import datetime
import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
import asyncio
import structlog

try:
    from .layer_orchestration import LayerOrchestrator, ProblemContext
    from .refinement_tracker import RefinementTracker, TrackingEventType
    from .layers import LayerDefinitions
    from .escalator import EscalatorAction
    from .security import (
        SecurityManager, User, APIKey, Permission, UserRole,
        LoginRequest, ProblemSubmissionRequest, UserCreateRequest,
        get_current_user, get_current_api_key, require_permission,
        require_permissions, rate_limit_dependency, get_security_manager
    )
    from .error_handling import ErrorHandler, ErrorSeverity, ErrorCategory, get_error_handler
except ImportError:
    # For testing
    from layer_orchestration import LayerOrchestrator, ProblemContext
    from refinement_tracker import RefinementTracker, TrackingEventType
    from layers import LayerDefinitions
    from escalator import EscalatorAction
    from security import (
        SecurityManager, User, APIKey, Permission, UserRole,
        LoginRequest, ProblemSubmissionRequest, UserCreateRequest,
        get_current_user, get_current_api_key, require_permission,
        require_permissions, rate_limit_dependency, get_security_manager
    )
    from error_handling import ErrorHandler, ErrorSeverity, ErrorCategory, get_error_handler
try:
    from .database import get_database_connection
except ImportError:
    # For testing
    from database import get_database_connection


# Response models
class LoginResponse(BaseModel):
    """Response model for login."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class UserResponse(BaseModel):
    """Response model for user information."""
    user_id: str
    username: str
    email: str
    role: str
    permissions: List[str]
    is_active: bool
    created_at: str
    last_login: Optional[str] = None


class APIKeyResponse(BaseModel):
    """Response model for API key creation."""
    api_key: str
    key_id: str
    name: str
    permissions: List[str]
    expires_at: str


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


class SecurityMetricsResponse(BaseModel):
    """Response model for security metrics."""
    total_users: int
    active_sessions: int
    failed_login_attempts: int
    rate_limit_violations: int
    api_key_usage: Dict[str, int]


# Initialize FastAPI app with security
app = FastAPI(
    title="Cosmic Council Refinement Engine - Secure API",
    description="Secure API for the Cosmic Council problem refinement system",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENABLE_DOCS", "true").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("ENABLE_DOCS", "true").lower() == "true" else None
)

# Security middleware
security = HTTPBearer()

# Configure CORS with security
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
)

# Initialize components
orchestrator = LayerOrchestrator()
tracker = RefinementTracker()
security_manager = get_security_manager()
error_handler = get_error_handler()

# Structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


# Middleware for request logging and security
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Security middleware for request processing."""
    start_time = datetime.utcnow()
    request_id = str(uuid.uuid4())
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    # Log request
    logger.info(
        "Request started",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host,
        user_agent=request.headers.get("user-agent", "")
    )
    
    try:
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            "Request completed",
            request_id=request_id,
            status_code=response.status_code,
            process_time=process_time
        )
        
        # Add security headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
        
    except Exception as e:
        # Log error
        process_time = (datetime.utcnow() - start_time).total_seconds()
        logger.error(
            "Request failed",
            request_id=request_id,
            error=str(e),
            process_time=process_time
        )
        
        # Handle error
        error_context = error_handler.handle_error(
            error=e,
            component="api",
            operation="request_processing",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.UNKNOWN,
            metadata={"request_id": request_id, "url": str(request.url)}
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Health check endpoint (no authentication required)
@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# Authentication endpoints
@app.post("/auth/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    _: None = Depends(rate_limit_dependency)
):
    """
    Authenticate user and return access token.
    """
    try:
        # Authenticate user
        user = await security_manager.authenticate_user(
            login_data.username,
            login_data.password
        )
        
        if not user:
            # Log failed login attempt
            logger.warning(
                "Failed login attempt",
                username=login_data.username,
                client_ip=request.client.host
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Create access token
        access_token = security_manager.create_access_token(
            user.user_id,
            user.permissions
        )
        
        # Log successful login
        logger.info(
            "User logged in",
            user_id=user.user_id,
            username=user.username,
            client_ip=request.client.host
        )
        
        return LoginResponse(
            access_token=access_token,
            expires_in=security_manager.access_token_expire_minutes * 60,
            user={
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "permissions": [p.value for p in user.permissions]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@app.post("/auth/register", response_model=UserResponse)
async def register(
    user_data: UserCreateRequest,
    request: Request,
    _: None = Depends(rate_limit_dependency)
):
    """
    Register a new user.
    """
    try:
        # Create user
        user = await security_manager.create_user(user_data)
        
        # Log user creation
        logger.info(
            "User registered",
            user_id=user.user_id,
            username=user.username,
            client_ip=request.client.host
        )
        
        return UserResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            permissions=[p.value for p in user.permissions],
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@app.post("/auth/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    name: str,
    permissions: List[str],
    current_user: User = Depends(get_current_user)
):
    """
    Create a new API key for the current user.
    """
    try:
        # Validate permissions
        valid_permissions = set()
        for perm_str in permissions:
            try:
                valid_permissions.add(Permission(perm_str))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid permission: {perm_str}"
                )
        
        # Create API key
        api_key = await security_manager.create_api_key(
            name=name,
            user_id=current_user.user_id,
            permissions=valid_permissions
        )
        
        # Log API key creation
        logger.info(
            "API key created",
            user_id=current_user.user_id,
            key_name=name,
            permissions=[p.value for p in valid_permissions]
        )
        
        return APIKeyResponse(
            api_key=api_key,
            key_id=security_manager.api_keys[hashlib.sha256(api_key.encode()).hexdigest()].key_id,
            name=name,
            permissions=[p.value for p in valid_permissions],
            expires_at=security_manager.api_keys[hashlib.sha256(api_key.encode()).hexdigest()].expires_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("API key creation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key creation failed"
        )


# Problem management endpoints
@app.post("/problems", response_model=ProblemSubmissionResponse)
async def submit_problem(
    request_data: ProblemSubmissionRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: User = Depends(get_current_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    Submit a new problem for processing.
    """
    try:
        # Validate and sanitize input
        validated_data = security_manager.validate_problem_input(request_data.dict())
        
        # Generate problem ID
        problem_id = str(uuid.uuid4())
        
        # Log problem submission
        logger.info(
            "Problem submitted",
            problem_id=problem_id,
            user_id=current_user.user_id,
            title=validated_data["title"],
            initial_layer=validated_data["initial_layer"]
        )
        
        # Track problem creation
        tracker.track_event(
            TrackingEventType.PROBLEM_CREATED,
            problem_id,
            {
                "title": validated_data["title"],
                "description": validated_data["description"],
                "initial_layer": validated_data["initial_layer"],
                "max_iterations": validated_data["max_iterations"],
                "user_id": current_user.user_id
            }
        )
        
        # Start background processing
        background_tasks.add_task(
            process_problem_background,
            problem_id,
            validated_data["title"],
            validated_data["description"],
            validated_data["initial_layer"],
            validated_data["max_iterations"],
            current_user.user_id
        )
        
        return ProblemSubmissionResponse(
            problem_id=problem_id,
            status="accepted",
            message="Problem submitted successfully and processing started",
            estimated_completion_time="Variable based on complexity"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Problem submission error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Problem submission failed"
        )


@app.get("/problems/{problem_id}/status", response_model=ProblemStatusResponse)
async def get_problem_status(
    problem_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the current status of a problem.
    """
    try:
        # Validate problem ID format
        try:
            uuid.UUID(problem_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid problem ID format"
            )
        
        # Get problem status
        status = orchestrator.get_problem_status(problem_id)
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return ProblemStatusResponse(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Problem status error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get problem status"
        )


@app.get("/problems", response_model=List[ProblemStatusResponse])
async def list_problems(
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    List problems for the current user.
    """
    try:
        # Get problems (in a real implementation, this would be filtered by user)
        problems = []
        for problem_id, problem_context in orchestrator.active_problems.items():
            status = orchestrator.get_problem_status(problem_id)
            problems.append(ProblemStatusResponse(**status))
        
        # Apply pagination
        start = offset
        end = offset + limit
        paginated_problems = problems[start:end]
        
        return paginated_problems
        
    except Exception as e:
        logger.error("List problems error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list problems"
        )


# Analytics endpoints (admin only)
@app.get("/analytics/security", response_model=SecurityMetricsResponse)
@require_permission(Permission.SYSTEM_ADMIN)
async def get_security_metrics(
    current_user: User = Depends(get_current_user)
):
    """
    Get security metrics (admin only).
    """
    try:
        # Get security metrics
        total_users = len(security_manager.users)
        active_sessions = len(security_manager.sessions)
        failed_login_attempts = sum(
            user.failed_login_attempts for user in security_manager.users.values()
        )
        rate_limit_violations = len(security_manager.rate_limits)
        
        # Get API key usage
        api_key_usage = {}
        for api_key in security_manager.api_keys.values():
            if api_key.last_used:
                api_key_usage[api_key.name] = 1
        
        return SecurityMetricsResponse(
            total_users=total_users,
            active_sessions=active_sessions,
            failed_login_attempts=failed_login_attempts,
            rate_limit_violations=rate_limit_violations,
            api_key_usage=api_key_usage
        )
        
    except Exception as e:
        logger.error("Security metrics error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get security metrics"
        )


# User management endpoints (admin only)
@app.get("/users", response_model=List[UserResponse])
@require_permission(Permission.MANAGE_USERS)
async def list_users(
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    List all users (admin only).
    """
    try:
        users = []
        for user in security_manager.users.values():
            users.append(UserResponse(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                role=user.role.value,
                permissions=[p.value for p in user.permissions],
                is_active=user.is_active,
                created_at=user.created_at.isoformat(),
                last_login=user.last_login.isoformat() if user.last_login else None
            ))
        
        # Apply pagination
        start = offset
        end = offset + limit
        paginated_users = users[start:end]
        
        return paginated_users
        
    except Exception as e:
        logger.error("List users error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )


# Background task for problem processing
async def process_problem_background(
    problem_id: str,
    title: str,
    description: str,
    initial_layer: str,
    max_iterations: int,
    user_id: str
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
                "total_answers": len(problem_context.answers),
                "user_id": user_id
            }
        )
        
        logger.info(
            "Problem processing completed",
            problem_id=problem_id,
            user_id=user_id,
            status=problem_context.metadata.get("status", "unknown")
        )
        
    except Exception as e:
        logger.error(
            "Problem processing failed",
            problem_id=problem_id,
            user_id=user_id,
            error=str(e)
        )
        
        tracker.track_event(
            TrackingEventType.PROBLEM_RESOLVED,
            problem_id,
            {
                "final_status": "error",
                "error_message": str(e),
                "user_id": user_id
            }
        )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the API on startup."""
    logger.info("Cosmic Council Refinement Engine Secure API started")
    
    # Initialize Redis for session management
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    await security_manager.initialize_redis(redis_url)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Cosmic Council Refinement Engine Secure API shutting down")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.warning("Resource not found", url=str(request.url), error=str(exc))
    return {"error": "Resource not found", "detail": str(exc)}


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error("Internal server error", url=str(request.url), error=str(exc))
    return {"error": "Internal server error", "detail": str(exc)}


# Example usage and testing
if __name__ == "__main__":
    import uvicorn
    import os
    
    # Set environment variables for testing
    os.environ["JWT_SECRET_KEY"] = "test-secret-key"
    os.environ["ENABLE_DOCS"] = "true"
    os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000,http://localhost:8080"
    
    # Run the API server
    uvicorn.run(
        "refinement_engine.secure_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
