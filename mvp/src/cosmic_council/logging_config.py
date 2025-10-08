"""
Cosmic Council Logging Framework
Production-grade structured logging with proper formatting and handlers.
"""

import logging
import logging.handlers
import sys
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from .config import LoggingConfig, LogLevel


class LogContext(Enum):
    """Logging context types."""
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DATABASE = "database"
    AI = "ai"
    RESEARCH = "research"


@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: str
    level: str
    logger: str
    message: str
    context: Optional[str] = None
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    enterprise: Optional[str] = None
    problem_id: Optional[str] = None
    session_id: Optional[str] = None
    duration_ms: Optional[float] = None
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def __init__(self, include_stack_trace: bool = True):
        """Initialize the structured formatter."""
        super().__init__()
        self.include_stack_trace = include_stack_trace
    
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as structured JSON."""
        # Extract custom attributes
        log_entry = LogEntry(
            timestamp=datetime.fromtimestamp(record.created).isoformat(),
            level=record.levelname,
            logger=record.name,
            message=record.getMessage(),
            context=getattr(record, 'context', None),
            request_id=getattr(record, 'request_id', None),
            user_id=getattr(record, 'user_id', None),
            enterprise=getattr(record, 'enterprise', None),
            problem_id=getattr(record, 'problem_id', None),
            session_id=getattr(record, 'session_id', None),
            duration_ms=getattr(record, 'duration_ms', None),
            error_code=getattr(record, 'error_code', None),
            stack_trace=traceback.format_exc() if self.include_stack_trace and record.exc_info else None,
            metadata=getattr(record, 'metadata', None)
        )
        
        # Convert to dict and remove None values
        log_dict = {k: v for k, v in asdict(log_entry).items() if v is not None}
        
        return json.dumps(log_dict, default=str)


class HumanReadableFormatter(logging.Formatter):
    """Human-readable formatter for console output."""
    
    def __init__(self):
        """Initialize the human-readable formatter."""
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record for human reading."""
        # Add emoji based on level
        level_emojis = {
            'DEBUG': '🔍',
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }
        
        emoji = level_emojis.get(record.levelname, '📝')
        formatted = super().format(record)
        
        # Add emoji and context if available
        if hasattr(record, 'context'):
            formatted = f"{emoji} [{record.context}] {formatted}"
        else:
            formatted = f"{emoji} {formatted}"
        
        # Add enterprise info if available
        if hasattr(record, 'enterprise'):
            formatted = formatted.replace('|', f"| {record.enterprise} |", 1)
        
        return formatted


class CosmicCouncilLogger:
    """Enhanced logger with structured logging capabilities."""
    
    def __init__(self, name: str, config: LoggingConfig):
        """Initialize the logger."""
        self.name = name
        self.config = config
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.level.value))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Add console handler
        if config.enable_console:
            self._add_console_handler()
        
        # Add file handler
        if config.enable_file and config.file_path:
            self._add_file_handler()
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _add_console_handler(self):
        """Add console handler with human-readable formatting."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.config.level.value))
        console_handler.setFormatter(HumanReadableFormatter())
        self.logger.addHandler(console_handler)
    
    def _add_file_handler(self):
        """Add rotating file handler with structured formatting."""
        log_file = Path(self.config.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.config.max_file_size_mb * 1024 * 1024,
            backupCount=self.config.backup_count
        )
        file_handler.setLevel(getattr(logging, self.config.level.value))
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)
    
    def _log_with_context(self, level: int, message: str, context: LogContext = None, 
                         **kwargs):
        """Log with additional context."""
        extra = {k: v for k, v in kwargs.items() if v is not None}
        if context:
            extra['context'] = context.value
        
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, context: LogContext = None, **kwargs):
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, context, **kwargs)
    
    def info(self, message: str, context: LogContext = None, **kwargs):
        """Log info message."""
        self._log_with_context(logging.INFO, message, context, **kwargs)
    
    def warning(self, message: str, context: LogContext = None, **kwargs):
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, context, **kwargs)
    
    def error(self, message: str, context: LogContext = None, **kwargs):
        """Log error message."""
        self._log_with_context(logging.ERROR, message, context, **kwargs)
    
    def critical(self, message: str, context: LogContext = None, **kwargs):
        """Log critical message."""
        self._log_with_context(logging.CRITICAL, message, context, **kwargs)
    
    def log_request(self, request_id: str, method: str, path: str, 
                   user_id: str = None, **kwargs):
        """Log an incoming request."""
        self.info(
            f"Request: {method} {path}",
            context=LogContext.REQUEST,
            request_id=request_id,
            user_id=user_id,
            method=method,
            path=path,
            **kwargs
        )
    
    def log_response(self, request_id: str, status_code: int, duration_ms: float,
                    **kwargs):
        """Log a response."""
        level = logging.INFO if status_code < 400 else logging.WARNING
        self.logger.log(
            level,
            f"Response: {status_code} ({duration_ms:.2f}ms)",
            extra={
                'context': LogContext.RESPONSE.value,
                'request_id': request_id,
                'status_code': status_code,
                'duration_ms': duration_ms,
                **kwargs
            }
        )
    
    def log_enterprise_processing(self, enterprise: str, problem_id: str, 
                                session_id: str = None, **kwargs):
        """Log enterprise processing."""
        self.info(
            f"Enterprise processing: {enterprise}",
            context=LogContext.AI,
            enterprise=enterprise,
            problem_id=problem_id,
            session_id=session_id,
            **kwargs
        )
    
    def log_performance_metric(self, metric_name: str, metric_value: float,
                             metric_unit: str = None, **kwargs):
        """Log a performance metric."""
        self.info(
            f"Performance: {metric_name} = {metric_value}{metric_unit or ''}",
            context=LogContext.PERFORMANCE,
            metric_name=metric_name,
            metric_value=metric_value,
            metric_unit=metric_unit,
            **kwargs
        )
    
    def log_database_operation(self, operation: str, table: str, duration_ms: float = None,
                             **kwargs):
        """Log a database operation."""
        self.debug(
            f"Database: {operation} on {table}",
            context=LogContext.DATABASE,
            operation=operation,
            table=table,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_security_event(self, event_type: str, severity: str = "medium", **kwargs):
        """Log a security event."""
        level = logging.CRITICAL if severity == "high" else logging.WARNING
        self.logger.log(
            level,
            f"Security: {event_type}",
            extra={
                'context': LogContext.SECURITY.value,
                'event_type': event_type,
                'severity': severity,
                **kwargs
            }
        )


def setup_logging(config: LoggingConfig) -> Dict[str, CosmicCouncilLogger]:
    """Set up logging for the entire application."""
    loggers = {}
    
    # Main application logger
    loggers['app'] = CosmicCouncilLogger('cosmic_council', config)
    
    # Component-specific loggers
    components = [
        'cosmic_council.core',
        'cosmic_council.enterprises',
        'cosmic_council.database',
        'cosmic_council.ai_service',
        'cosmic_council.research_service',
        'cosmic_council.api',
        'cosmic_council.security'
    ]
    
    for component in components:
        loggers[component] = CosmicCouncilLogger(component, config)
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.level.value))
    
    # Add a handler to catch any unhandled logs
    if config.enable_console:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(HumanReadableFormatter())
        root_logger.addHandler(handler)
    
    loggers['app'].info("🚀 Logging system initialized", context=LogContext.REQUEST)
    
    return loggers


def get_logger(name: str) -> CosmicCouncilLogger:
    """Get a logger instance."""
    # This would typically be managed by a dependency injection system
    # For now, we'll create a simple logger
    from .config import get_config
    config = get_config()
    return CosmicCouncilLogger(name, config.logging)


# Performance monitoring decorator
def log_performance(logger: CosmicCouncilLogger, operation_name: str):
    """Decorator to log performance metrics."""
    def decorator(func):
        import time
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.log_performance_metric(
                    f"{operation_name}_duration",
                    duration_ms,
                    "ms"
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"Error in {operation_name}: {e}",
                    context=LogContext.ERROR,
                    duration_ms=duration_ms,
                    error_code=type(e).__name__
                )
                raise
        
        return wrapper
    return decorator


# Context manager for request logging
class RequestLogger:
    """Context manager for logging requests."""
    
    def __init__(self, logger: CosmicCouncilLogger, request_id: str, 
                 method: str, path: str, user_id: str = None):
        """Initialize request logger."""
        self.logger = logger
        self.request_id = request_id
        self.method = method
        self.path = path
        self.user_id = user_id
        self.start_time = None
    
    def __enter__(self):
        """Start request logging."""
        import time
        self.start_time = time.time()
        self.logger.log_request(
            self.request_id,
            self.method,
            self.path,
            self.user_id
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End request logging."""
        import time
        duration_ms = (time.time() - self.start_time) * 1000
        
        if exc_type:
            self.logger.log_response(
                self.request_id,
                500,
                duration_ms,
                error=exc_val
            )
        else:
            self.logger.log_response(
                self.request_id,
                200,
                duration_ms
            )
