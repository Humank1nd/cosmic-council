"""
Cosmic Council Refinement Engine - Comprehensive Error Handling
Implements robust error handling, retry mechanisms, and graceful degradation.
"""

import asyncio
import logging
import traceback
from typing import Dict, Any, Optional, List, Callable, Type, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import functools
import json
import time


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""
    NETWORK = "network"
    DATABASE = "database"
    AI_SERVICE = "ai_service"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context information for errors."""
    error_id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    component: str
    operation: str
    error_message: str
    stack_trace: str
    metadata: Dict[str, Any]
    retry_count: int = 0
    max_retries: int = 3
    is_recoverable: bool = True


class ErrorHandler:
    """
    Centralized error handling system with retry mechanisms and graceful degradation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize error handler.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        
        # Error tracking
        self.error_history: List[ErrorContext] = []
        self.error_counts: Dict[str, int] = {}
        
        # Circuit breaker state
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Retry policies
        self.retry_policies = self._initialize_retry_policies()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default error handling configuration."""
        return {
            "max_error_history": 1000,
            "circuit_breaker_threshold": 5,
            "circuit_breaker_timeout": 300,  # 5 minutes
            "default_retry_delay": 1.0,
            "max_retry_delay": 60.0,
            "retry_backoff_multiplier": 2.0,
            "enable_graceful_degradation": True,
            "log_all_errors": True,
            "alert_on_critical_errors": True
        }
    
    def _initialize_retry_policies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize retry policies for different error types."""
        return {
            "network": {
                "max_retries": 3,
                "base_delay": 1.0,
                "max_delay": 10.0,
                "backoff_multiplier": 2.0,
                "retryable_exceptions": [
                    "ConnectionError",
                    "TimeoutError",
                    "requests.exceptions.RequestException"
                ]
            },
            "database": {
                "max_retries": 2,
                "base_delay": 0.5,
                "max_delay": 5.0,
                "backoff_multiplier": 1.5,
                "retryable_exceptions": [
                    "asyncpg.exceptions.ConnectionDoesNotExistError",
                    "sqlalchemy.exc.OperationalError"
                ]
            },
            "ai_service": {
                "max_retries": 2,
                "base_delay": 2.0,
                "max_delay": 30.0,
                "backoff_multiplier": 2.0,
                "retryable_exceptions": [
                    "openai.RateLimitError",
                    "anthropic.RateLimitError",
                    "openai.APITimeoutError"
                ]
            },
            "default": {
                "max_retries": 1,
                "base_delay": 1.0,
                "max_delay": 5.0,
                "backoff_multiplier": 1.5,
                "retryable_exceptions": []
            }
        }
    
    def handle_error(
        self,
        error: Exception,
        component: str,
        operation: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        metadata: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorContext:
        """
        Handle an error and return error context.
        
        Args:
            error: The exception that occurred
            component: Component where error occurred
            operation: Operation being performed
            severity: Error severity level
            category: Error category
            metadata: Additional metadata
            context: Additional context
            
        Returns:
            ErrorContext object
        """
        error_id = f"err_{int(time.time() * 1000)}"
        
        # Create error context
        error_context = ErrorContext(
            error_id=error_id,
            timestamp=datetime.utcnow(),
            severity=severity,
            category=category,
            component=component,
            operation=operation,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            metadata=metadata or {},
            is_recoverable=self._is_recoverable_error(error, category)
        )
        
        # Update error counts
        error_key = f"{component}:{operation}:{category.value}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Add to history
        self.error_history.append(error_context)
        
        # Keep history size manageable
        if len(self.error_history) > self.config["max_error_history"]:
            self.error_history = self.error_history[-self.config["max_error_history"]:]
        
        # Log error
        if self.config["log_all_errors"]:
            self._log_error(error_context)
        
        # Check circuit breaker
        if self._should_trip_circuit_breaker(component, operation):
            self._trip_circuit_breaker(component, operation)
        
        # Alert on critical errors
        if severity == ErrorSeverity.CRITICAL and self.config["alert_on_critical_errors"]:
            self._send_alert(error_context)
        
        return error_context
    
    def _is_recoverable_error(self, error: Exception, category: ErrorCategory) -> bool:
        """Determine if an error is recoverable."""
        error_type = type(error).__name__
        
        # Check retry policies
        policy = self.retry_policies.get(category.value, self.retry_policies["default"])
        retryable_exceptions = policy.get("retryable_exceptions", [])
        
        return error_type in retryable_exceptions
    
    def _should_trip_circuit_breaker(self, component: str, operation: str) -> bool:
        """Check if circuit breaker should be tripped."""
        error_key = f"{component}:{operation}"
        error_count = self.error_counts.get(error_key, 0)
        
        return error_count >= self.config["circuit_breaker_threshold"]
    
    def _trip_circuit_breaker(self, component: str, operation: str):
        """Trip circuit breaker for a component/operation."""
        circuit_key = f"{component}:{operation}"
        self.circuit_breakers[circuit_key] = {
            "tripped_at": datetime.utcnow(),
            "error_count": self.error_counts.get(circuit_key, 0)
        }
        
        self.logger.warning(f"Circuit breaker tripped for {circuit_key}")
    
    def is_circuit_breaker_open(self, component: str, operation: str) -> bool:
        """Check if circuit breaker is open."""
        circuit_key = f"{component}:{operation}"
        
        if circuit_key not in self.circuit_breakers:
            return False
        
        circuit = self.circuit_breakers[circuit_key]
        timeout = timedelta(seconds=self.config["circuit_breaker_timeout"])
        
        # Check if timeout has passed
        if datetime.utcnow() - circuit["tripped_at"] > timeout:
            # Reset circuit breaker
            del self.circuit_breakers[circuit_key]
            return False
        
        return True
    
    def _log_error(self, error_context: ErrorContext):
        """Log error with appropriate level."""
        log_message = f"Error in {error_context.component}.{error_context.operation}: {error_context.error_message}"
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message, extra={"error_context": error_context})
        elif error_context.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message, extra={"error_context": error_context})
        elif error_context.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message, extra={"error_context": error_context})
        else:
            self.logger.info(log_message, extra={"error_context": error_context})
    
    def _send_alert(self, error_context: ErrorContext):
        """Send alert for critical errors."""
        # In a real implementation, this would send alerts via email, Slack, etc.
        alert_message = f"CRITICAL ERROR: {error_context.component}.{error_context.operation} - {error_context.error_message}"
        self.logger.critical(f"ALERT: {alert_message}")
    
    async def retry_with_backoff(
        self,
        func: Callable,
        *args,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        max_retries: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Retry a function with exponential backoff.
        
        Args:
            func: Function to retry
            *args: Function arguments
            category: Error category for retry policy
            max_retries: Maximum number of retries
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: Last exception if all retries fail
        """
        policy = self.retry_policies.get(category.value, self.retry_policies["default"])
        
        max_retries = max_retries or policy["max_retries"]
        base_delay = policy["base_delay"]
        max_delay = policy["max_delay"]
        backoff_multiplier = policy["backoff_multiplier"]
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
                    
            except Exception as e:
                last_exception = e
                
                # Check if error is retryable
                if not self._is_recoverable_error(e, category):
                    raise e
                
                # Don't retry on last attempt
                if attempt == max_retries:
                    break
                
                # Calculate delay
                delay = min(base_delay * (backoff_multiplier ** attempt), max_delay)
                
                # Log retry attempt
                self.logger.warning(f"Retrying {func.__name__} in {delay:.2f}s (attempt {attempt + 1}/{max_retries + 1})")
                
                # Wait before retry
                await asyncio.sleep(delay)
        
        # All retries failed
        raise last_exception
    
    def get_error_analytics(self) -> Dict[str, Any]:
        """Get error analytics and statistics."""
        if not self.error_history:
            return {"error": "No error history available"}
        
        # Calculate statistics
        total_errors = len(self.error_history)
        errors_by_severity = {}
        errors_by_category = {}
        errors_by_component = {}
        
        for error in self.error_history:
            # By severity
            severity = error.severity.value
            errors_by_severity[severity] = errors_by_severity.get(severity, 0) + 1
            
            # By category
            category = error.category.value
            errors_by_category[category] = errors_by_category.get(category, 0) + 1
            
            # By component
            component = error.component
            errors_by_component[component] = errors_by_component.get(component, 0) + 1
        
        # Recent errors (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_errors = [e for e in self.error_history if e.timestamp > recent_cutoff]
        
        return {
            "total_errors": total_errors,
            "recent_errors_24h": len(recent_errors),
            "errors_by_severity": errors_by_severity,
            "errors_by_category": errors_by_category,
            "errors_by_component": errors_by_component,
            "circuit_breakers": list(self.circuit_breakers.keys()),
            "error_rate": total_errors / max(1, (datetime.utcnow() - self.error_history[0].timestamp).total_seconds() / 3600)
        }


def error_handler(
    component: str,
    operation: str,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    retry_category: Optional[ErrorCategory] = None
):
    """
    Decorator for automatic error handling.
    
    Args:
        component: Component name
        operation: Operation name
        severity: Error severity
        category: Error category
        retry_category: Category for retry policy (defaults to category)
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            error_handler_instance = get_error_handler()
            
            try:
                return await error_handler_instance.retry_with_backoff(
                    func,
                    *args,
                    category=retry_category or category,
                    **kwargs
                )
            except Exception as e:
                error_context = error_handler_instance.handle_error(
                    error=e,
                    component=component,
                    operation=operation,
                    severity=severity,
                    category=category,
                    metadata={"function": func.__name__, "args": str(args), "kwargs": str(kwargs)}
                )
                
                # Re-raise with error context
                raise Exception(f"Error in {component}.{operation}: {str(e)}") from e
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            error_handler_instance = get_error_handler()
            
            try:
                return error_handler_instance.retry_with_backoff(
                    func,
                    *args,
                    category=retry_category or category,
                    **kwargs
                )
            except Exception as e:
                error_context = error_handler_instance.handle_error(
                    error=e,
                    component=component,
                    operation=operation,
                    severity=severity,
                    category=category,
                    metadata={"function": func.__name__, "args": str(args), "kwargs": str(kwargs)}
                )
                
                # Re-raise with error context
                raise Exception(f"Error in {component}.{operation}: {str(e)}") from e
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class GracefulDegradation:
    """
    Implements graceful degradation for system components.
    """
    
    def __init__(self, error_handler: ErrorHandler):
        """
        Initialize graceful degradation.
        
        Args:
            error_handler: Error handler instance
        """
        self.error_handler = error_handler
        self.logger = logging.getLogger(__name__)
        self.fallback_handlers: Dict[str, Callable] = {}
    
    def register_fallback(self, component: str, fallback_func: Callable):
        """
        Register a fallback function for a component.
        
        Args:
            component: Component name
            fallback_func: Fallback function to call
        """
        self.fallback_handlers[component] = fallback_func
        self.logger.info(f"Registered fallback for component: {component}")
    
    async def execute_with_fallback(
        self,
        component: str,
        operation: str,
        primary_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with fallback if primary fails.
        
        Args:
            component: Component name
            operation: Operation name
            primary_func: Primary function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or fallback result
        """
        try:
            if asyncio.iscoroutinefunction(primary_func):
                return await primary_func(*args, **kwargs)
            else:
                return primary_func(*args, **kwargs)
                
        except Exception as e:
            self.logger.warning(f"Primary function failed for {component}.{operation}, trying fallback")
            
            # Handle error
            self.error_handler.handle_error(
                error=e,
                component=component,
                operation=operation,
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.UNKNOWN
            )
            
            # Try fallback
            if component in self.fallback_handlers:
                try:
                    fallback_func = self.fallback_handlers[component]
                    if asyncio.iscoroutinefunction(fallback_func):
                        return await fallback_func(*args, **kwargs)
                    else:
                        return fallback_func(*args, **kwargs)
                except Exception as fallback_error:
                    self.logger.error(f"Fallback also failed for {component}.{operation}")
                    self.error_handler.handle_error(
                        error=fallback_error,
                        component=component,
                        operation=f"{operation}_fallback",
                        severity=ErrorSeverity.HIGH,
                        category=ErrorCategory.UNKNOWN
                    )
                    raise fallback_error
            else:
                self.logger.error(f"No fallback available for {component}.{operation}")
                raise e


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def initialize_error_handling(config: Optional[Dict[str, Any]] = None) -> ErrorHandler:
    """
    Initialize error handling system.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Error handler instance
    """
    global _error_handler
    _error_handler = ErrorHandler(config)
    return _error_handler


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_error_handling():
        print("=== Error Handling Test ===")
        
        # Initialize error handler
        error_handler = initialize_error_handling()
        
        # Test error handling
        try:
            raise ValueError("Test error")
        except Exception as e:
            error_context = error_handler.handle_error(
                error=e,
                component="test_component",
                operation="test_operation",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.VALIDATION
            )
            print(f"Error handled: {error_context.error_id}")
        
        # Test retry mechanism
        @error_handler(
            component="test_component",
            operation="retry_test",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.NETWORK
        )
        async def failing_function():
            raise ConnectionError("Simulated network error")
        
        try:
            await failing_function()
        except Exception as e:
            print(f"Retry failed: {e}")
        
        # Test graceful degradation
        graceful_degradation = GracefulDegradation(error_handler)
        
        def fallback_func():
            return "Fallback result"
        
        graceful_degradation.register_fallback("test_component", fallback_func)
        
        async def primary_func():
            raise RuntimeError("Primary function failed")
        
        try:
            result = await graceful_degradation.execute_with_fallback(
                "test_component",
                "graceful_test",
                primary_func
            )
            print(f"Graceful degradation result: {result}")
        except Exception as e:
            print(f"Graceful degradation failed: {e}")
        
        # Get error analytics
        analytics = error_handler.get_error_analytics()
        print(f"Error analytics: {analytics}")
    
    # Run the test
    asyncio.run(test_error_handling())
