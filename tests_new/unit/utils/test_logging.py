"""
Unit tests for logging utilities.
"""

import pytest
import logging
from src.utils.logging import setup_logging, get_logger


class TestLogging:
    """Test logging utilities."""
    
    def test_setup_logging(self):
        """Test logging setup."""
        setup_logging()
        logger = logging.getLogger("test")
        assert logger is not None
    
    def test_get_logger(self):
        """Test get logger function."""
        logger = get_logger("test_module")
        assert logger is not None
        assert logger.name == "test_module"
    
    def test_logger_levels(self):
        """Test logger levels."""
        logger = get_logger("test")
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        # These should not raise exceptions
        assert True
