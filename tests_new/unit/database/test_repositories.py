"""
Unit tests for database repositories.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from src.database.repositories.problem_repository import ProblemRepository
from src.database.repositories.solution_repository import SolutionRepository
from src.database.repositories.cycle_repository import CycleRepository


class TestProblemRepository:
    """Test ProblemRepository class."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def problem_repository(self, mock_session):
        """Create problem repository with mock session."""
        return ProblemRepository(mock_session)
    
    @pytest.mark.asyncio
    async def test_create_problem(self, problem_repository, mock_session):
        """Test problem creation."""
        problem_data = {
            "title": "Test Problem",
            "description": "Test description",
            "domain": "technology",
            "complexity": "simple"
        }
        
        mock_problem = Mock()
        mock_problem.id = "test-id"
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None
        
        result = await problem_repository.create(problem_data)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_get_by_domain(self, problem_repository, mock_session):
        """Test getting problems by domain."""
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        
        result = await problem_repository.get_by_domain("technology")
        assert result == []


class TestSolutionRepository:
    """Test SolutionRepository class."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def solution_repository(self, mock_session):
        """Create solution repository with mock session."""
        return SolutionRepository(mock_session)
    
    @pytest.mark.asyncio
    async def test_create_solution(self, solution_repository, mock_session):
        """Test solution creation."""
        solution_data = {
            "problem_id": "test-problem-id",
            "title": "Test Solution",
            "description": "Test description",
            "approach": "Test approach"
        }
        
        mock_solution = Mock()
        mock_solution.id = "test-solution-id"
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None
        
        result = await solution_repository.create(solution_data)
        assert result is not None


class TestCycleRepository:
    """Test CycleRepository class."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def cycle_repository(self, mock_session):
        """Create cycle repository with mock session."""
        return CycleRepository(mock_session)
    
    @pytest.mark.asyncio
    async def test_create_cycle(self, cycle_repository, mock_session):
        """Test cycle creation."""
        cycle_data = {
            "problem_id": "test-problem-id",
            "status": "pending"
        }
        
        mock_cycle = Mock()
        mock_cycle.id = "test-cycle-id"
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None
        
        result = await cycle_repository.create(cycle_data)
        assert result is not None
