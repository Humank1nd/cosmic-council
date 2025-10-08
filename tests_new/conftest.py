"""
Pytest configuration and shared fixtures for the new modular test structure.
"""

import asyncio
import pytest
import tempfile
import os
import sys
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import new modular components
from src.core.types import EnterpriseType, ProblemComplexity, CycleStatus, CosmicCouncilRule
from src.database.connection import get_database_connection, DatabaseConnection
from src.database.models import Problem, Solution, Cycle, Enterprise
from src.agents.orchestration.coordinator import AgentCoordinator
from src.utils.logging import setup_logging, get_logger

# Configure pytest
pytest_plugins = ["pytest_asyncio"]

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    # Set up temporary database
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
async def database_connection(temp_db):
    """Create a database connection for testing."""
    connection = DatabaseConnection(f'sqlite:///{temp_db}')
    connection.initialize()
    await connection.create_tables()
    
    yield connection
    
    await connection.close()

@pytest.fixture
def sample_problem_data():
    """Sample problem data for testing."""
    return {
        "title": "Test Problem",
        "description": "Test problem description",
        "domain": "technology",
        "complexity": ProblemComplexity.SIMPLE,
        "priority": "medium"
    }

@pytest.fixture
def sample_solution_data():
    """Sample solution data for testing."""
    return {
        "title": "Test Solution",
        "description": "Test solution description",
        "approach": "Test approach",
        "status": "draft"
    }

@pytest.fixture
def sample_cycle_data():
    """Sample cycle data for testing."""
    return {
        "status": CycleStatus.PENDING,
        "current_enterprise": EnterpriseType.RED_OWL
    }

@pytest.fixture
def mock_agent_coordinator():
    """Mock agent coordinator for testing."""
    coordinator = Mock(spec=AgentCoordinator)
    coordinator.coordinate_agents = AsyncMock(return_value={"status": "success"})
    return coordinator

@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return Mock(spec=get_logger("test"))

# Markers for different test types
pytestmark = [
    pytest.mark.asyncio,
]
