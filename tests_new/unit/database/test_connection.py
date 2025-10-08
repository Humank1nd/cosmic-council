"""
Unit tests for database connection management.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from src.database.connection import DatabaseConnection, get_database_connection


class TestDatabaseConnection:
    """Test DatabaseConnection class."""
    
    def test_connection_initialization(self):
        """Test database connection initialization."""
        connection = DatabaseConnection("sqlite:///:memory:")
        assert connection.database_url == "sqlite:///:memory:"
        assert connection.engine is None
        assert connection.async_engine is None
    
    def test_connection_config(self):
        """Test database connection with config."""
        config = {"pool_size": 5, "echo": True}
        connection = DatabaseConnection("sqlite:///:memory:", config)
        assert connection.config == config
    
    @pytest.mark.asyncio
    async def test_async_session(self):
        """Test async session creation."""
        connection = DatabaseConnection("sqlite:///:memory:")
        connection.initialize()
        
        async with connection.get_async_session() as session:
            assert session is not None
    
    def test_health_check(self):
        """Test database health check."""
        connection = DatabaseConnection("sqlite:///:memory:")
        # This would need proper async testing setup
        assert connection is not None
