"""
Logging configuration and utilities for the Cosmic Council system.
Provides structured logging with multiple handlers and formatters.
"""

import logging
import logging.config
import sys
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import json
from ..config import get_settings

class LoggerConfig:
    """Configuration for the logging system."""
    
    def __init__(self):
        self.settings = get_settings()
        self.log_level = self.settings.log_level.upper()
        self.log_format = self.settings.log_format
        self.log_file = self.settings.log_file
        self.log_json = self.settings.log_json
    
    def get_config(self) -> Dict[str, Any]:
        """Get the logging configuration dictionary."""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'detailed': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'json': {
                    '()': 'shared.logging.formatters.JSONFormatter',
                    'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': self.log_level,
                    'formatter': 'json' if self.log_json else 'standard',
                    'stream': sys.stdout
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': self.log_level,
                    'formatter': 'detailed',
                    'filename': self.log_file,
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5
                }
            },
            'loggers': {
                'cosmic_council': {
                    'level': self.log_level,
                    'handlers': ['console', 'file'],
                    'propagate': False
                },
                'shared': {
                    'level': self.log_level,
                    'handlers': ['console', 'file'],
                    'propagate': False
                },
                'services': {
                    'level': self.log_level,
                    'handlers': ['console', 'file'],
                    'propagate': False
                },
                'enterprises': {
                    'level': self.log_level,
                    'handlers': ['console', 'file'],
                    'propagate': False
                }
            },
            'root': {
                'level': self.log_level,
                'handlers': ['console']
            }
        }

def setup_logging() -> None:
    """Set up the logging configuration."""
    config = LoggerConfig()
    logging.config.dictConfig(config.get_config())
    
    # Create log directory if it doesn't exist
    log_file_path = Path(config.log_file)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger('cosmic_council')
    logger.info("Logging system initialized successfully")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)

class CosmicCouncilLogger:
    """Enhanced logger with Cosmic Council specific functionality."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs) -> None:
        """Set logging context for structured logging."""
        self.context.update(kwargs)
    
    def clear_context(self) -> None:
        """Clear the logging context."""
        self.context.clear()
    
    def _log_with_context(self, level: int, message: str, **kwargs) -> None:
        """Log a message with context information."""
        if self.context:
            message = f"{message} | Context: {json.dumps(self.context)}"
        self.logger.log(level, message, **kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message."""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log an info message."""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message."""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log an error message."""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log a critical message."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def log_cycle_start(self, cycle_id: str, objective: str) -> None:
        """Log the start of a cycle."""
        self.set_context(cycle_id=cycle_id, objective=objective, event="cycle_start")
        self.info(f"Cycle {cycle_id} started with objective: {objective}")
    
    def log_cycle_complete(self, cycle_id: str, duration: float) -> None:
        """Log the completion of a cycle."""
        self.set_context(cycle_id=cycle_id, duration=duration, event="cycle_complete")
        self.info(f"Cycle {cycle_id} completed in {duration:.2f} seconds")
    
    def log_stage_start(self, cycle_id: str, stage: str) -> None:
        """Log the start of a stage."""
        self.set_context(cycle_id=cycle_id, stage=stage, event="stage_start")
        self.info(f"Stage {stage} started for cycle {cycle_id}")
    
    def log_stage_complete(self, cycle_id: str, stage: str, duration: float) -> None:
        """Log the completion of a stage."""
        self.set_context(cycle_id=cycle_id, stage=stage, duration=duration, event="stage_complete")
        self.info(f"Stage {stage} completed for cycle {cycle_id} in {duration:.2f} seconds")
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Log an error with context."""
        if context:
            self.set_context(**context)
        self.set_context(error_type=type(error).__name__, error_message=str(error))
        self.error(f"Error occurred: {error}")

# Global logger instance
_cosmic_logger: Optional[CosmicCouncilLogger] = None

def get_cosmic_logger(name: str = "cosmic_council") -> CosmicCouncilLogger:
    """Get the global Cosmic Council logger instance."""
    global _cosmic_logger
    if _cosmic_logger is None:
        _cosmic_logger = CosmicCouncilLogger(name)
    return _cosmic_logger