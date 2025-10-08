"""
Error handling utilities for the Cosmic Council system.
"""

import logging
import traceback
from typing import Any, Dict, Optional
from datetime import datetime
import uuid


class CosmicCouncilError(Exception):
    """Base exception for Cosmic Council system"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        self.error_id = str(uuid.uuid4())


class ValidationError(CosmicCouncilError):
    """Validation error"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value


class AuthenticationError(CosmicCouncilError):
    """Authentication error"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(CosmicCouncilError):
    """Authorization error"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, "AUTHORIZATION_ERROR")


class NotFoundError(CosmicCouncilError):
    """Resource not found error"""
    
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message, "NOT_FOUND_ERROR")
        self.resource_type = resource_type
        self.resource_id = resource_id


class DatabaseError(CosmicCouncilError):
    """Database operation error"""
    
    def __init__(self, message: str, operation: str = None):
        super().__init__(message, "DATABASE_ERROR")
        self.operation = operation


class ExternalServiceError(CosmicCouncilError):
    """External service error"""
    
    def __init__(self, service_name: str, message: str):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR")
        self.service_name = service_name


def handle_error(error: Exception, logger: logging.Logger = None) -> Dict[str, Any]:
    """Handle and format error for API response"""
    if logger is None:
        logger = logging.getLogger(__name__)
    
    # Log the error
    log_error(error, logger)
    
    # Create error response
    if isinstance(error, CosmicCouncilError):
        return create_error_response(
            error_code=error.error_code,
            message=error.message,
            details=error.details,
            error_id=error.error_id
        )
    else:
        return create_error_response(
            error_code="INTERNAL_ERROR",
            message="An internal error occurred",
            details={"type": type(error).__name__}
        )


def log_error(error: Exception, logger: logging.Logger) -> None:
    """Log error with context"""
    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if isinstance(error, CosmicCouncilError):
        error_context.update({
            "error_code": error.error_code,
            "error_id": error.error_id,
            "details": error.details
        })
    
    logger.error(f"Error occurred: {error_context}", exc_info=True)


def create_error_response(
    error_code: str,
    message: str,
    details: Dict[str, Any] = None,
    error_id: str = None
) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
            "error_id": error_id or str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat()
        }
    }


def safe_execute(func, *args, **kwargs):
    """Safely execute a function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger = logging.getLogger(__name__)
        log_error(e, logger)
        raise


async def safe_execute_async(func, *args, **kwargs):
    """Safely execute an async function with error handling"""
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger = logging.getLogger(__name__)
        log_error(e, logger)
        raise


def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Decorator to retry function on error"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        import time
                        time.sleep(delay * (backoff_factor ** attempt))
                    else:
                        raise last_exception
            
            return None
        
        return wrapper
    return decorator


def validate_error_response(response: Dict[str, Any]) -> bool:
    """Validate error response format"""
    if not isinstance(response, dict):
        return False
    
    if "error" not in response:
        return False
    
    error = response["error"]
    required_fields = ["code", "message", "timestamp"]
    
    return all(field in error for field in required_fields)
