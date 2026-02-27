"""
Enhanced error handling utilities for Agent Orchestrator API
Provides standardized error responses with actionable messages, error codes, and troubleshooting hints
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from enum import Enum


class ErrorCode(str, Enum):
    """Standard error codes for the Agent Orchestrator API"""
    # Authentication & Authorization
    AUTH_REQUIRED = "AUTH_001"
    AUTH_INVALID = "AUTH_002"
    AUTH_EXPIRED = "AUTH_003"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_004"
    
    # Validation
    VALIDATION_ERROR = "VAL_001"
    VALIDATION_INVALID_FORMAT = "VAL_002"
    VALIDATION_MISSING_FIELD = "VAL_003"
    VALIDATION_INVALID_VALUE = "VAL_004"
    
    # Resources
    RESOURCE_NOT_FOUND = "RES_001"
    RESOURCE_ALREADY_EXISTS = "RES_002"
    RESOURCE_CONFLICT = "RES_003"
    RESOURCE_LOCKED = "RES_004"
    
    # Business Logic
    BUSINESS_RULE_VIOLATION = "BIZ_001"
    BUSINESS_INVALID_STATE = "BIZ_002"
    BUSINESS_OPERATION_FAILED = "BIZ_003"
    
    # System
    SYSTEM_UNAVAILABLE = "SYS_001"
    SYSTEM_TIMEOUT = "SYS_002"
    SYSTEM_RATE_LIMIT = "SYS_003"
    SYSTEM_MAINTENANCE = "SYS_004"
    
    # External Services
    EXTERNAL_SERVICE_UNAVAILABLE = "EXT_001"
    EXTERNAL_SERVICE_ERROR = "EXT_002"
    
    # Generic
    INTERNAL_ERROR = "INT_001"
    UNKNOWN_ERROR = "UNK_001"


class ErrorResponse:
    """Standardized error response structure"""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[str] = None,
        troubleshooting: Optional[list] = None,
        reference: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details
        self.troubleshooting = troubleshooting or []
        self.reference = reference
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error response to dictionary"""
        result = {
            "error_code": self.error_code.value,
            "message": self.message
        }
        
        if self.details:
            result["details"] = self.details
        
        if self.troubleshooting:
            result["troubleshooting"] = self.troubleshooting
        
        if self.reference:
            result["reference"] = self.reference
        
        if self.context:
            result["context"] = self.context
        
        return result


def create_http_exception(
    status_code: int,
    error_code: ErrorCode,
    message: str,
    details: Optional[str] = None,
    troubleshooting: Optional[list] = None,
    reference: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Create a standardized HTTPException with enhanced error information
    
    Args:
        status_code: HTTP status code
        error_code: Standard error code
        message: User-friendly error message
        details: Additional error details
        troubleshooting: List of troubleshooting hints
        reference: Reference to documentation or support
        context: Additional context information
    
    Returns:
        HTTPException with standardized error format
    """
    error_response = ErrorResponse(
        error_code=error_code,
        message=message,
        details=details,
        troubleshooting=troubleshooting,
        reference=reference,
        context=context
    )
    
    return HTTPException(
        status_code=status_code,
        detail=error_response.to_dict()
    )


# Common error factories
def not_found_error(
    resource_type: str,
    resource_id: str,
    reference: Optional[str] = None
) -> HTTPException:
    """Create a 404 Not Found error"""
    return create_http_exception(
        status_code=status.HTTP_404_NOT_FOUND,
        error_code=ErrorCode.RESOURCE_NOT_FOUND,
        message=f"{resource_type} not found",
        details=f"The {resource_type} with ID '{resource_id}' does not exist or has been deleted.",
        troubleshooting=[
            f"Verify that the {resource_type} ID is correct",
            f"Check if the {resource_type} has been deleted",
            "Ensure you have permission to access this resource"
        ],
        reference=reference,
        context={"resource_type": resource_type, "resource_id": resource_id}
    )


def validation_error(
    field: str,
    message: str,
    valid_values: Optional[list] = None,
    reference: Optional[str] = None
) -> HTTPException:
    """Create a 400 Validation Error"""
    troubleshooting = [
        f"Check that the '{field}' field is correctly formatted",
        "Review the API documentation for expected field formats"
    ]
    
    if valid_values:
        troubleshooting.append(f"Valid values for '{field}' are: {', '.join(map(str, valid_values))}")
    
    return create_http_exception(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code=ErrorCode.VALIDATION_ERROR,
        message=f"Validation error: {message}",
        details=f"The field '{field}' failed validation: {message}",
        troubleshooting=troubleshooting,
        reference=reference,
        context={"field": field, "valid_values": valid_values}
    )


def authentication_error(
    reason: str = "Authentication required",
    reference: Optional[str] = None
) -> HTTPException:
    """Create a 401 Authentication Error"""
    return create_http_exception(
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_code=ErrorCode.AUTH_REQUIRED,
        message="Authentication required",
        details=reason,
        troubleshooting=[
            "Include a valid authentication token in the Authorization header",
            "Check that your token has not expired",
            "Verify the token format: 'Bearer <token>'"
        ],
        reference=reference
    )


def permission_error(
    action: str,
    resource: str,
    reference: Optional[str] = None
) -> HTTPException:
    """Create a 403 Permission Error"""
    return create_http_exception(
        status_code=status.HTTP_403_FORBIDDEN,
        error_code=ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
        message="Insufficient permissions",
        details=f"You do not have permission to {action} {resource}",
        troubleshooting=[
            "Check your user permissions",
            "Contact your administrator if you believe you should have access",
            "Verify that you are using the correct authentication token"
        ],
        reference=reference,
        context={"action": action, "resource": resource}
    )


def system_unavailable_error(
    service: str,
    reference: Optional[str] = None
) -> HTTPException:
    """Create a 503 Service Unavailable Error"""
    return create_http_exception(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        error_code=ErrorCode.SYSTEM_UNAVAILABLE,
        message=f"{service} is currently unavailable",
        details=f"The {service} service is not available at this time. Please try again later.",
        troubleshooting=[
            "Check the system status page",
            "Wait a few moments and try again",
            "Contact support if the issue persists"
        ],
        reference=reference,
        context={"service": service}
    )


def internal_error(
    operation: str,
    reference: Optional[str] = None
) -> HTTPException:
    """Create a 500 Internal Server Error"""
    return create_http_exception(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code=ErrorCode.INTERNAL_ERROR,
        message="An internal error occurred",
        details=f"An error occurred while processing your request: {operation}",
        troubleshooting=[
            "Try the request again",
            "If the problem persists, contact support with the error code",
            "Check the API status page for known issues"
        ],
        reference=reference,
        context={"operation": operation}
    )
