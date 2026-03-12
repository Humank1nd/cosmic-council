"""
Comprehensive logging configuration for Agent Orchestrator API
Provides structured logging with request/response tracking, performance monitoring, and error context
"""

import logging
import logging.handlers
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        def json_serializer(obj):
            """Custom JSON serializer for datetime and other objects"""
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, '__dict__'):
                return str(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields (serialize any datetime objects)
        if hasattr(record, "extra_data"):
            extra = record.extra_data
            # Convert any datetime objects in extra_data to strings
            if isinstance(extra, dict):
                extra = {k: v.isoformat() if isinstance(v, datetime) else v for k, v in extra.items()}
            log_data["extra"] = extra
        
        return json.dumps(log_data, default=json_serializer)


class StructuredFormatter(logging.Formatter):
    """Human-readable structured formatter"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record in human-readable format"""
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        level = record.levelname.ljust(8)
        logger_name = record.name
        message = record.getMessage()
        
        formatted = f"{timestamp} [{level}] {logger_name}: {message}"
        
        # Add extra context if present
        if hasattr(record, "extra_data"):
            extra = json.dumps(record.extra_data, default=str)
            formatted += f" | {extra}"
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    use_json: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Setup comprehensive logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        use_json: Whether to use JSON format for file logs
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
    """
    # Create logs directory if log file is specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler (always human-readable)
    # Use an error-tolerant stream for the console to prevent UnicodeEncodeError on Windows
    import io
    try:
        # Wrap the buffer to handle encoding errors gracefully
        safe_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=sys.stdout.encoding, errors='replace', newline='\n', line_buffering=True)
        console_handler = logging.StreamHandler(safe_stdout)
    except (AttributeError, io.UnsupportedOperation):
        # Fallback for environments where stdout.buffer is not available
        console_handler = logging.StreamHandler(sys.stdout)
        
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler (JSON or structured format)
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        if use_json:
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(StructuredFormatter())
        
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    logging.info(f"Logging configured: level={log_level}, file={log_file}, json={use_json}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)


def log_request(logger: logging.Logger, method: str, path: str, **kwargs) -> None:
    """Log HTTP request"""
    logger.info(
        f"Request: {method} {path}",
        extra={"extra_data": {"type": "request", "method": method, "path": path, **kwargs}}
    )


def log_response(logger: logging.Logger, method: str, path: str, status_code: int, duration: float, **kwargs) -> None:
    """Log HTTP response"""
    level = logging.WARNING if status_code >= 400 else logging.INFO
    logger.log(
        level,
        f"Response: {method} {path} -> {status_code} ({duration:.3f}s)",
        extra={"extra_data": {"type": "response", "method": method, "path": path, "status_code": status_code, "duration": duration, **kwargs}}
    )


def log_performance(logger: logging.Logger, operation: str, duration: float, **kwargs) -> None:
    """Log performance metrics"""
    level = logging.WARNING if duration > 1.0 else (logging.INFO if duration > 0.5 else logging.DEBUG)
    logger.log(
        level,
        f"Performance: {operation} took {duration:.3f}s",
        extra={"extra_data": {"type": "performance", "operation": operation, "duration": duration, **kwargs}}
    )


def log_error(logger: logging.Logger, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log error with context"""
    logger.error(
        f"Error: {type(error).__name__}: {str(error)}",
        exc_info=True,
        extra={"extra_data": {"type": "error", "error_type": type(error).__name__, "context": context or {}}}
    )


def log_audit(logger: logging.Logger, action: str, user: str, resource: str, **kwargs) -> None:
    """Log audit event"""
    logger.info(
        f"Audit: {user} performed {action} on {resource}",
        extra={"extra_data": {"type": "audit", "action": action, "user": user, "resource": resource, **kwargs}}
    )

