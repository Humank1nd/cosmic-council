#!/usr/bin/env python3
"""
Error Handling and Logging System for Cosmic Council Framework
"""

import logging
import traceback
import sys
from typing import Any, Dict, Optional, Union
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import json

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories"""
    VALIDATION = "validation"
    DATABASE = "database"
    API = "api"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    SYSTEM = "system"
    SECURITY = "security"

@dataclass
class ErrorContext:
    """Context information for errors"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    component: Optional[str] = None
    operation: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ErrorInfo:
    """Structured error information"""
    error_id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    exception_type: str
    exception_message: str
    traceback: str
    context: ErrorContext
    resolved: bool = False
    resolution_notes: Optional[str] = None

class CosmicCouncilError(Exception):
    """Base exception for Cosmic Council framework"""
    
    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        context: Optional[ErrorContext] = None,
        original_exception: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.category = category
        self.context = context or ErrorContext()
        self.original_exception = original_exception
        self.timestamp = datetime.now(timezone.utc)

class ValidationError(CosmicCouncilError):
    """Validation error"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(message, ErrorSeverity.MEDIUM, ErrorCategory.VALIDATION, context)

class DatabaseError(CosmicCouncilError):
    """Database error"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None, original_exception: Optional[Exception] = None):
        super().__init__(message, ErrorSeverity.HIGH, ErrorCategory.DATABASE, context, original_exception)

class APIError(CosmicCouncilError):
    """API error"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None, original_exception: Optional[Exception] = None):
        super().__init__(message, ErrorSeverity.MEDIUM, ErrorCategory.API, context, original_exception)

class BusinessLogicError(CosmicCouncilError):
    """Business logic error"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(message, ErrorSeverity.MEDIUM, ErrorCategory.BUSINESS_LOGIC, context)

class ExternalServiceError(CosmicCouncilError):
    """External service error"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None, original_exception: Optional[Exception] = None):
        super().__init__(message, ErrorSeverity.HIGH, ErrorCategory.EXTERNAL_SERVICE, context, original_exception)

class SecurityError(CosmicCouncilError):
    """Security error"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(message, ErrorSeverity.CRITICAL, ErrorCategory.SECURITY, context)

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, logger_name: str = "cosmic_council"):
        self.logger = logging.getLogger(logger_name)
        self.error_history: list[ErrorInfo] = []
        self.max_history_size = 1000
    
    def handle_error(
        self,
        error: Union[Exception, CosmicCouncilError],
        context: Optional[ErrorContext] = None,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[ErrorCategory] = None
    ) -> ErrorInfo:
        """Handle and log an error"""
        
        # Convert regular exceptions to CosmicCouncilError
        if not isinstance(error, CosmicCouncilError):
            if severity is None:
                severity = ErrorSeverity.MEDIUM
            if category is None:
                category = ErrorCategory.SYSTEM
            
            error = CosmicCouncilError(
                message=str(error),
                severity=severity,
                category=category,
                context=context,
                original_exception=error
            )
        
        # Create error info
        error_info = ErrorInfo(
            error_id=f"err_{datetime.now(timezone.utc).timestamp()}",
            timestamp=error.timestamp,
            severity=error.severity,
            category=error.category,
            message=error.message,
            exception_type=type(error).__name__,
            exception_message=str(error),
            traceback=traceback.format_exc(),
            context=error.context
        )
        
        # Log the error
        self._log_error(error_info)
        
        # Store in history
        self._store_error(error_info)
        
        return error_info
    
    def _log_error(self, error_info: ErrorInfo) -> None:
        """Log error information"""
        log_data = {
            "error_id": error_info.error_id,
            "timestamp": error_info.timestamp.isoformat(),
            "severity": error_info.severity.value,
            "category": error_info.category.value,
            "message": error_info.message,
            "exception_type": error_info.exception_type,
            "context": asdict(error_info.context)
        }
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"CRITICAL ERROR: {json.dumps(log_data)}")
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(f"HIGH SEVERITY ERROR: {json.dumps(log_data)}")
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"MEDIUM SEVERITY ERROR: {json.dumps(log_data)}")
        else:
            self.logger.info(f"LOW SEVERITY ERROR: {json.dumps(log_data)}")
    
    def _store_error(self, error_info: ErrorInfo) -> None:
        """Store error in history"""
        self.error_history.append(error_info)
        
        # Maintain max history size
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    def get_error_history(self, limit: Optional[int] = None) -> list[ErrorInfo]:
        """Get error history"""
        if limit is None:
            return self.error_history.copy()
        return self.error_history[-limit:]
    
    def get_errors_by_severity(self, severity: ErrorSeverity) -> list[ErrorInfo]:
        """Get errors by severity"""
        return [error for error in self.error_history if error.severity == severity]
    
    def get_errors_by_category(self, category: ErrorCategory) -> list[ErrorInfo]:
        """Get errors by category"""
        return [error for error in self.error_history if error.category == category]
    
    def resolve_error(self, error_id: str, resolution_notes: str) -> bool:
        """Mark an error as resolved"""
        for error in self.error_history:
            if error.error_id == error_id:
                error.resolved = True
                error.resolution_notes = resolution_notes
                return True
        return False

# Global error handler instance
error_handler = ErrorHandler()

def handle_error(
    error: Union[Exception, CosmicCouncilError],
    context: Optional[ErrorContext] = None,
    severity: Optional[ErrorSeverity] = None,
    category: Optional[ErrorCategory] = None
) -> ErrorInfo:
    """Global error handling function"""
    return error_handler.handle_error(error, context, severity, category)

def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    return error_handler

# Decorator for automatic error handling
def error_handler_decorator(
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.SYSTEM
):
    """Decorator for automatic error handling"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    component=func.__module__,
                    operation=func.__name__
                )
                handle_error(e, context, severity, category)
                raise
        return wrapper
    return decorator

# Async version of the decorator
def async_error_handler_decorator(
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.SYSTEM
):
    """Async decorator for automatic error handling"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    component=func.__module__,
                    operation=func.__name__
                )
                handle_error(e, context, severity, category)
                raise
        return wrapper
    return decorator
