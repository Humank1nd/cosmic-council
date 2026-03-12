"""
Enterprise Observability Configuration for Agent Orchestrator.
Configures structlog for JSON-standardized logging and integrated tracing.
"""

import logging
import sys
import structlog
from typing import Any, Dict

def setup_observability(log_level: str = "INFO"):
    """
    Configure structlog for high-performance, structured logging.
    """
    
    # Processors for structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    # If terminal is interactive, use colorful rendering, else JSON
    if sys.stderr.isatty():
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Bridge standard logging to structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    logger = structlog.get_logger(__name__)
    logger.info("Enterprise observability initialized", standard="Fortune 500")

def get_enterprise_logger(name: str):
    """Returns a structlog logger instance."""
    return structlog.get_logger(name)
