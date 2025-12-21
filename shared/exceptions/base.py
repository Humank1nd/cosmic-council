"""
Base exception classes for the Cosmic Council system.
Provides structured error handling with context and logging.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone

class CosmicCouncilException(Exception):
    """Base exception class for all Cosmic Council exceptions."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.cause = cause
        self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "cause": str(self.cause) if self.cause else None
        }
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"

class ValidationError(CosmicCouncilException):
    """Exception raised for validation errors."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if field:
            context['field'] = field
        if value is not None:
            context['value'] = value
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            context=context,
            **kwargs
        )

class DatabaseError(CosmicCouncilException):
    """Exception raised for database-related errors."""
    
    def __init__(
        self,
        message: str,
        query: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if query:
            context['query'] = query
        if table:
            context['table'] = table
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            context=context,
            **kwargs
        )

class AuthenticationError(CosmicCouncilException):
    """Exception raised for authentication errors."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        user_id: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if user_id:
            context['user_id'] = user_id
        
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            context=context,
            **kwargs
        )

class AuthorizationError(CosmicCouncilException):
    """Exception raised for authorization errors."""
    
    def __init__(
        self,
        message: str = "Access denied",
        user_id: Optional[str] = None,
        permission: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if user_id:
            context['user_id'] = user_id
        if permission:
            context['permission'] = permission
        
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            context=context,
            **kwargs
        )

class ConfigurationError(CosmicCouncilException):
    """Exception raised for configuration errors."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if config_key:
            context['config_key'] = config_key
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            context=context,
            **kwargs
        )

class ServiceError(CosmicCouncilException):
    """Exception raised for service-related errors."""
    
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        endpoint: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if service_name:
            context['service_name'] = service_name
        if endpoint:
            context['endpoint'] = endpoint
        
        super().__init__(
            message=message,
            error_code="SERVICE_ERROR",
            context=context,
            **kwargs
        )

class NetworkError(CosmicCouncilException):
    """Exception raised for network-related errors."""
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if url:
            context['url'] = url
        if status_code:
            context['status_code'] = status_code
        
        super().__init__(
            message=message,
            error_code="NETWORK_ERROR",
            context=context,
            **kwargs
        )

class TimeoutError(CosmicCouncilException):
    """Exception raised for timeout errors."""
    
    def __init__(
        self,
        message: str = "Operation timed out",
        timeout_seconds: Optional[float] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if timeout_seconds:
            context['timeout_seconds'] = timeout_seconds
        
        super().__init__(
            message=message,
            error_code="TIMEOUT_ERROR",
            context=context,
            **kwargs
        )

class ResourceNotFoundError(CosmicCouncilException):
    """Exception raised when a resource is not found."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if resource_type:
            context['resource_type'] = resource_type
        if resource_id:
            context['resource_id'] = resource_id
        
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            context=context,
            **kwargs
        )

class BusinessLogicError(CosmicCouncilException):
    """Exception raised for business logic violations."""
    
    def __init__(
        self,
        message: str,
        rule: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if rule:
            context['rule'] = rule
        
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            context=context,
            **kwargs
        )
