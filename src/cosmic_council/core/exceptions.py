"""
Standardized Service Exceptions for Agent Orchestrator.
Fortune 500 Level Error Handling with unique error codes and unified formatting.
"""

from enum import Enum
from typing import Any, Dict, Optional

class ErrorCode(Enum):
    """Unique error codes for enterprise-grade debugging."""
    # General Errors
    INTERNAL_SERVER_ERROR = "CC-1000"
    NOT_FOUND = "CC-1001"
    INVALID_INPUT = "CC-1002"
    UNAUTHORIZED = "CC-1003"
    FORBIDDEN = "CC-1004"
    
    # Workflow Errors
    WORKFLOW_INITIALIZATION_FAILED = "CC-2000"
    STAGE_EXECUTION_ERROR = "CC-2001"
    LOOP_CLOSURE_FAILED = "CC-2002"
    RECURSION_LIMIT_EXCEEDED = "CC-2003"
    
    # AI & Knowledge Base Errors
    AI_GENERATION_FAILED = "CC-3000"
    KNOWLEDGE_BASE_UNAVAILABLE = "CC-3001"
    LLM_RATE_LIMIT_EXCEEDED = "CC-3002"
    
    # Resource & Priority Errors
    INSUFFICIENT_RESOURCES = "CC-4000"
    PRIORITY_SCORING_ERROR = "CC-4001"
    QUANTUM_ALLOCATION_FAILED = "CC-4002"

class ServiceError(Exception):
    """Base exception for all Cosmic Council services."""
    def __init__(
        self, 
        message: str, 
        error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "success": False,
            "error": {
                "code": self.error_code.value,
                "type": self.error_code.name,
                "message": self.message,
                "details": self.details
            }
        }

class WorkflowError(ServiceError):
    """Errors occurring during workflow orchestration."""
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.STAGE_EXECUTION_ERROR, **kwargs):
        super().__init__(message, error_code, status_code=400, **kwargs)

class AIError(ServiceError):
    """Errors occurring during AI interaction or narrative generation."""
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.AI_GENERATION_FAILED, **kwargs):
        super().__init__(message, error_code, status_code=502, **kwargs)

class ResourceError(ServiceError):
    """Errors occurring during resource allocation or priority matrix calculation."""
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.INSUFFICIENT_RESOURCES, **kwargs):
        super().__init__(message, error_code, status_code=422, **kwargs)

class NotFoundError(ServiceError):
    """Errors when a resource is not found."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCode.NOT_FOUND, status_code=404, **kwargs)
