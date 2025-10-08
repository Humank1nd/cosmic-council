"""
Database test fixtures.
"""

import pytest
from src.database.connection import get_database_connection
from src.database.models import Problem, Solution, Cycle


@pytest.fixture
async def test_database():
    """Create test database with sample data."""
    connection = get_database_connection()
    await connection.create_tables()
    
    # Add sample data
    async with connection.get_async_session() as session:
        # Create test problems
        problems = [
            Problem(
                title="Test Problem 1",
                description="Test description 1",
                domain="technology",
                complexity="simple"
            ),
            Problem(
                title="Test Problem 2", 
                description="Test description 2",
                domain="business",
                complexity="moderate"
            )
        ]
        
        for problem in problems:
            session.add(problem)
        
        await session.commit()
    
    yield connection
    
    # Cleanup
    await connection.drop_tables()


@pytest.fixture
def sample_problem_data():
    """Sample problem data for testing."""
    return {
        "title": "Fixture Test Problem",
        "description": "Problem created from fixture",
        "domain": "testing",
        "complexity": "simple",
        "priority": "medium"
    }


@pytest.fixture
def sample_solution_data():
    """Sample solution data for testing."""
    return {
        "title": "Fixture Test Solution",
        "description": "Solution created from fixture",
        "approach": "Fixture approach",
        "status": "draft"
    }
