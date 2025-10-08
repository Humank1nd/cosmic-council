"""
Unit tests for core services.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.core.services.problem_service import ProblemService
from src.core.services.solution_service import SolutionService
from src.core.services.cycle_service import CycleService


class TestProblemService:
    """Test ProblemService class."""
    
    def test_problem_service_initialization(self):
        """Test problem service initialization."""
        service = ProblemService()
        assert service is not None
    
    @pytest.mark.asyncio
    async def test_create_problem(self):
        """Test problem creation."""
        service = ProblemService()
        problem_data = {
            "title": "Test Problem",
            "description": "Test description",
            "domain": "technology",
            "complexity": "simple"
        }
        
        with patch.object(service, 'repository') as mock_repo:
            mock_repo.create.return_value = Mock(id="test-id")
            result = await service.create_problem(problem_data)
            assert result == "test-id"


class TestSolutionService:
    """Test SolutionService class."""
    
    def test_solution_service_initialization(self):
        """Test solution service initialization."""
        service = SolutionService()
        assert service is not None
    
    @pytest.mark.asyncio
    async def test_create_solution(self):
        """Test solution creation."""
        service = SolutionService()
        solution_data = {
            "problem_id": "test-problem-id",
            "title": "Test Solution",
            "description": "Test solution description",
            "approach": "Test approach"
        }
        
        with patch.object(service, 'repository') as mock_repo:
            mock_repo.create.return_value = Mock(id="test-solution-id")
            result = await service.create_solution(solution_data)
            assert result == "test-solution-id"


class TestCycleService:
    """Test CycleService class."""
    
    def test_cycle_service_initialization(self):
        """Test cycle service initialization."""
        service = CycleService()
        assert service is not None
    
    @pytest.mark.asyncio
    async def test_create_cycle(self):
        """Test cycle creation."""
        service = CycleService()
        cycle_data = {
            "problem_id": "test-problem-id",
            "status": "pending"
        }
        
        with patch.object(service, 'repository') as mock_repo:
            mock_repo.create.return_value = Mock(id="test-cycle-id")
            result = await service.create_cycle(cycle_data)
            assert result == "test-cycle-id"
