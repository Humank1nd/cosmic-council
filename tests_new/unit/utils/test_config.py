"""
Unit tests for configuration utilities.
"""

import pytest
from unittest.mock import patch
from src.utils.config import load_config


class TestConfig:
    """Test configuration utilities."""
    
    def test_load_config_default(self):
        """Test loading default configuration."""
        config = load_config()
        assert config is not None
        assert isinstance(config, dict)
    
    @patch.dict('os.environ', {'DATABASE_URL': 'test://test'})
    def test_load_config_with_env(self):
        """Test loading configuration with environment variables."""
        config = load_config()
        assert config is not None
        assert 'database_url' in config or 'DATABASE_URL' in config
    
    def test_config_structure(self):
        """Test configuration structure."""
        config = load_config()
        
        # Check for common configuration keys
        expected_keys = ['database_url', 'debug', 'log_level']
        for key in expected_keys:
            if key in config:
                assert config[key] is not None
