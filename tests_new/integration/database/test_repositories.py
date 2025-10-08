"""
Integration tests for database repositories.
"""

import pytest
from src.database.connection import get_database_connection
from src.database.repositories import (
    ProblemRepository, SolutionRepository, CycleRepository
)


class TestRepositoryIntegration:
    """Test repository integration with database."""
    
    @pytest.fixture
    async def db_connection(self):
        """Create test database connection."""
        connection = get_database_connection()
        await connection.create_tables()
        yield connection
        await connection.drop_tables()
    
    @pytest.mark.asyncio
    async def test_problem_repository_integration(self, db_connection):
        """Test problem repository with real database."""
        async with db_connection.get_async_session() as session:
            repository = ProblemRepository(session)
            
            # Create a problem
            problem_data = {
                "title": "Integration Test Problem",
                "description": "Test problem for integration testing",
                "domain": "testing",
                "complexity": "simple"
            }
            
            problem = await repository.create(problem_data)
            assert problem is not None
            assert problem.title == "Integration Test Problem"
            
            # Retrieve the problem
            retrieved = await repository.get_by_id(str(problem.id))
            assert retrieved is not None
            assert retrieved.title == "Integration Test Problem"
    
    @pytest.mark.asyncio
    async def test_solution_repository_integration(self, db_connection):
        """Test solution repository with real database."""
        async with db_connection.get_async_session() as session:
            repository = SolutionRepository(session)
            
            # Create a solution
            solution_data = {
                "problem_id": "test-problem-id",
                "title": "Integration Test Solution",
                "description": "Test solution for integration testing",
                "approach": "Test approach"
            }
            
            solution = await repository.create(solution_data)
            assert solution is not None
            assert solution.title == "Integration Test Solution"
    
    @pytest.mark.asyncio
    async def test_cycle_repository_integration(self, db_connection):
        """Test cycle repository with real database."""
        async with db_connection.get_async_session() as session:
            repository = CycleRepository(session)
            
            # Create a cycle
            cycle_data = {
                "problem_id": "test-problem-id",
                "status": "pending"
            }
            
            cycle = await repository.create(cycle_data)
            assert cycle is not None
            assert cycle.status == "pending"
