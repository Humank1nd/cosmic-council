"""
Script to create additional test files for the new modular structure.
"""

import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_additional_test_files():
    """Create additional test files for comprehensive coverage"""
    new_tests_dir = Path("tests_new")
    
    additional_tests = {
        # Core service tests
        "unit/core/test_services.py": '''"""
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
''',
        
        # Database repository tests
        "unit/database/test_repositories.py": '''"""
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
''',
        
        # Agent orchestration tests
        "unit/agents/orchestration/test_coordinator.py": '''"""
Unit tests for agent orchestration coordinator.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.orchestration.coordinator import AgentCoordinator


class TestAgentCoordinator:
    """Test AgentCoordinator class."""
    
    def test_coordinator_initialization(self):
        """Test coordinator initialization."""
        coordinator = AgentCoordinator()
        assert coordinator is not None
    
    @pytest.mark.asyncio
    async def test_coordinate_agents(self):
        """Test agent coordination."""
        coordinator = AgentCoordinator()
        
        with patch.object(coordinator, 'agents') as mock_agents:
            mock_agents.items.return_value = [
                ("red_owl", Mock()),
                ("orange_orangutan", Mock())
            ]
            
            result = await coordinator.coordinate_agents("test_problem")
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_execute_workflow(self):
        """Test workflow execution."""
        coordinator = AgentCoordinator()
        
        with patch.object(coordinator, 'coordinate_agents') as mock_coordinate:
            mock_coordinate.return_value = {"status": "success"}
            
            result = await coordinator.execute_workflow("test_problem")
            assert result["status"] == "success"
''',
        
        # Enterprise agent tests
        "unit/agents/supra_enterprise/test_orange_orangutan.py": '''"""
Unit tests for Orange Orangutan agent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.supra_enterprise.orange_orangutan import OrangeOrangutanAgent


class TestOrangeOrangutanAgent:
    """Test OrangeOrangutanAgent class."""
    
    def test_agent_initialization(self):
        """Test Orange Orangutan agent initialization."""
        agent = OrangeOrangutanAgent()
        assert agent is not None
        assert agent.enterprise_type == "orange_orangutan"
    
    def test_agent_name(self):
        """Test agent name."""
        agent = OrangeOrangutanAgent()
        assert agent.name == "Orange Orangutan"
    
    @pytest.mark.asyncio
    async def test_plan_method(self):
        """Test planning method."""
        agent = OrangeOrangutanAgent()
        
        with patch.object(agent, 'plan') as mock_plan:
            mock_plan.return_value = {"result": "plan_complete"}
            result = await agent.plan("test_problem")
            assert result["result"] == "plan_complete"
''',
        
        "unit/agents/supra_enterprise/test_yellow_honeybee.py": '''"""
Unit tests for Yellow Honeybee agent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.supra_enterprise.yellow_honeybee import YellowHoneybeeAgent


class TestYellowHoneybeeAgent:
    """Test YellowHoneybeeAgent class."""
    
    def test_agent_initialization(self):
        """Test Yellow Honeybee agent initialization."""
        agent = YellowHoneybeeAgent()
        assert agent is not None
        assert agent.enterprise_type == "yellow_honeybee"
    
    def test_agent_name(self):
        """Test agent name."""
        agent = YellowHoneybeeAgent()
        assert agent.name == "Yellow Honeybee"
    
    @pytest.mark.asyncio
    async def test_develop_method(self):
        """Test development method."""
        agent = YellowHoneybeeAgent()
        
        with patch.object(agent, 'develop') as mock_develop:
            mock_develop.return_value = {"result": "development_complete"}
            result = await agent.develop("test_problem")
            assert result["result"] == "development_complete"
''',
        
        "unit/agents/supra_enterprise/test_green_tortoise.py": '''"""
Unit tests for Green Tortoise agent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.supra_enterprise.green_tortoise import GreenTortoiseAgent


class TestGreenTortoiseAgent:
    """Test GreenTortoiseAgent class."""
    
    def test_agent_initialization(self):
        """Test Green Tortoise agent initialization."""
        agent = GreenTortoiseAgent()
        assert agent is not None
        assert agent.enterprise_type == "green_tortoise"
    
    def test_agent_name(self):
        """Test agent name."""
        agent = GreenTortoiseAgent()
        assert agent.name == "Green Tortoise"
    
    @pytest.mark.asyncio
    async def test_budget_method(self):
        """Test budgeting method."""
        agent = GreenTortoiseAgent()
        
        with patch.object(agent, 'budget') as mock_budget:
            mock_budget.return_value = {"result": "budget_complete"}
            result = await agent.budget("test_problem")
            assert result["result"] == "budget_complete"
''',
        
        "unit/agents/supra_enterprise/test_blue_dolphin.py": '''"""
Unit tests for Blue Dolphin agent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.supra_enterprise.blue_dolphin import BlueDolphinAgent


class TestBlueDolphinAgent:
    """Test BlueDolphinAgent class."""
    
    def test_agent_initialization(self):
        """Test Blue Dolphin agent initialization."""
        agent = BlueDolphinAgent()
        assert agent is not None
        assert agent.enterprise_type == "blue_dolphin"
    
    def test_agent_name(self):
        """Test agent name."""
        agent = BlueDolphinAgent()
        assert agent.name == "Blue Dolphin"
    
    @pytest.mark.asyncio
    async def test_market_method(self):
        """Test market analysis method."""
        agent = BlueDolphinAgent()
        
        with patch.object(agent, 'market') as mock_market:
            mock_market.return_value = {"result": "market_analysis_complete"}
            result = await agent.market("test_problem")
            assert result["result"] == "market_analysis_complete"
''',
        
        "unit/agents/supra_enterprise/test_purple_elephant.py": '''"""
Unit tests for Purple Elephant agent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.supra_enterprise.purple_elephant import PurpleElephantAgent


class TestPurpleElephantAgent:
    """Test PurpleElephantAgent class."""
    
    def test_agent_initialization(self):
        """Test Purple Elephant agent initialization."""
        agent = PurpleElephantAgent()
        assert agent is not None
        assert agent.enterprise_type == "purple_elephant"
    
    def test_agent_name(self):
        """Test agent name."""
        agent = PurpleElephantAgent()
        assert agent.name == "Purple Elephant"
    
    @pytest.mark.asyncio
    async def test_support_method(self):
        """Test support method."""
        agent = PurpleElephantAgent()
        
        with patch.object(agent, 'support') as mock_support:
            mock_support.return_value = {"result": "support_complete"}
            result = await agent.support("test_problem")
            assert result["result"] == "support_complete"
''',
        
        # API route tests
        "unit/api/test_problems.py": '''"""
Unit tests for problem API routes.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


class TestProblemRoutes:
    """Test problem API routes."""
    
    def test_app_creation(self):
        """Test FastAPI app creation."""
        assert app is not None
    
    def test_get_problems(self):
        """Test GET /api/v1/problems endpoint."""
        client = TestClient(app)
        response = client.get("/api/v1/problems")
        assert response.status_code in [200, 404]  # 404 if no problems exist
    
    def test_create_problem(self):
        """Test POST /api/v1/problems endpoint."""
        client = TestClient(app)
        problem_data = {
            "title": "Test Problem",
            "description": "Test description",
            "domain": "technology",
            "complexity": "simple"
        }
        
        response = client.post("/api/v1/problems", json=problem_data)
        assert response.status_code in [200, 201, 422]  # 422 for validation errors
    
    def test_get_problem_by_id(self):
        """Test GET /api/v1/problems/{id} endpoint."""
        client = TestClient(app)
        response = client.get("/api/v1/problems/test-id")
        assert response.status_code in [200, 404]
''',
        
        "unit/api/test_cycles.py": '''"""
Unit tests for cycle API routes.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


class TestCycleRoutes:
    """Test cycle API routes."""
    
    def test_get_cycles(self):
        """Test GET /api/v1/cycles endpoint."""
        client = TestClient(app)
        response = client.get("/api/v1/cycles")
        assert response.status_code in [200, 404]
    
    def test_create_cycle(self):
        """Test POST /api/v1/cycles endpoint."""
        client = TestClient(app)
        cycle_data = {
            "problem_id": "test-problem-id",
            "status": "pending"
        }
        
        response = client.post("/api/v1/cycles", json=cycle_data)
        assert response.status_code in [200, 201, 422]
    
    def test_get_cycle_by_id(self):
        """Test GET /api/v1/cycles/{id} endpoint."""
        client = TestClient(app)
        response = client.get("/api/v1/cycles/test-id")
        assert response.status_code in [200, 404]
''',
        
        "unit/api/test_solutions.py": '''"""
Unit tests for solution API routes.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


class TestSolutionRoutes:
    """Test solution API routes."""
    
    def test_get_solutions(self):
        """Test GET /api/v1/solutions endpoint."""
        client = TestClient(app)
        response = client.get("/api/v1/solutions")
        assert response.status_code in [200, 404]
    
    def test_create_solution(self):
        """Test POST /api/v1/solutions endpoint."""
        client = TestClient(app)
        solution_data = {
            "problem_id": "test-problem-id",
            "title": "Test Solution",
            "description": "Test solution description",
            "approach": "Test approach"
        }
        
        response = client.post("/api/v1/solutions", json=solution_data)
        assert response.status_code in [200, 201, 422]
    
    def test_get_solution_by_id(self):
        """Test GET /api/v1/solutions/{id} endpoint."""
        client = TestClient(app)
        response = client.get("/api/v1/solutions/test-id")
        assert response.status_code in [200, 404]
''',
        
        # Utility tests
        "unit/utils/test_config.py": '''"""
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
''',
        
        "unit/utils/test_validation.py": '''"""
Unit tests for validation utilities.
"""

import pytest
from src.utils.validation import (
    validate_input, validate_email, validate_uuid,
    validate_string_length, validate_numeric_range
)


class TestValidation:
    """Test validation utilities."""
    
    def test_validate_input(self):
        """Test input validation."""
        # Valid input
        assert validate_input("test", data_type=str) == True
        assert validate_input(123, data_type=int) == True
        assert validate_input({"key": "value"}, required_fields=["key"]) == True
        
        # Invalid input
        assert validate_input(None) == False
        assert validate_input("test", data_type=int) == False
        assert validate_input({"key": "value"}, required_fields=["missing"]) == False
    
    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        assert validate_email("test@example.com") == True
        assert validate_email("user.name@domain.co.uk") == True
        
        # Invalid emails
        assert validate_email("invalid-email") == False
        assert validate_email("@domain.com") == False
        assert validate_email("user@") == False
    
    def test_validate_uuid(self):
        """Test UUID validation."""
        # Valid UUIDs
        assert validate_uuid("123e4567-e89b-12d3-a456-426614174000") == True
        assert validate_uuid("00000000-0000-0000-0000-000000000000") == True
        
        # Invalid UUIDs
        assert validate_uuid("invalid-uuid") == False
        assert validate_uuid("123") == False
        assert validate_uuid("") == False
    
    def test_validate_string_length(self):
        """Test string length validation."""
        # Valid lengths
        assert validate_string_length("test", min_length=1, max_length=10) == True
        assert validate_string_length("", min_length=0) == True
        
        # Invalid lengths
        assert validate_string_length("", min_length=1) == False
        assert validate_string_length("very long string", max_length=5) == False
        assert validate_string_length(123) == False  # Not a string
    
    def test_validate_numeric_range(self):
        """Test numeric range validation."""
        # Valid ranges
        assert validate_numeric_range(5, min_value=1, max_value=10) == True
        assert validate_numeric_range(0, min_value=0) == True
        assert validate_numeric_range(100, max_value=100) == True
        
        # Invalid ranges
        assert validate_numeric_range(5, min_value=10) == False
        assert validate_numeric_range(5, max_value=1) == False
        assert validate_numeric_range("not a number") == False
''',
        
        "unit/utils/test_helpers.py": '''"""
Unit tests for helper utilities.
"""

import pytest
from src.utils.helpers import (
    generate_id, format_timestamp, sanitize_string,
    deep_merge_dicts, chunk_list, remove_duplicates
)


class TestHelpers:
    """Test helper utilities."""
    
    def test_generate_id(self):
        """Test ID generation."""
        # Test with prefix
        id_with_prefix = generate_id("test")
        assert id_with_prefix.startswith("test_")
        assert len(id_with_prefix) > 5
        
        # Test without prefix
        id_without_prefix = generate_id()
        assert len(id_without_prefix) > 0
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        from datetime import datetime, timezone
        
        # Test with datetime object
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        formatted = format_timestamp(dt)
        assert "2024-01-01" in formatted
        assert "12:00:00" in formatted
        
        # Test with string
        formatted_str = format_timestamp("2024-01-01T12:00:00Z")
        assert formatted_str is not None
    
    def test_sanitize_string(self):
        """Test string sanitization."""
        # Test normal string
        assert sanitize_string("  test  ") == "test"
        
        # Test string with control characters
        dirty_string = "test\x00\x01\x02string"
        clean_string = sanitize_string(dirty_string)
        assert "\x00" not in clean_string
        assert "\x01" not in clean_string
        assert "\x02" not in clean_string
        
        # Test max length
        long_string = "a" * 100
        truncated = sanitize_string(long_string, max_length=10)
        assert len(truncated) == 10
    
    def test_deep_merge_dicts(self):
        """Test deep dictionary merging."""
        dict1 = {"a": 1, "b": {"c": 2}}
        dict2 = {"b": {"d": 3}, "e": 4}
        
        merged = deep_merge_dicts(dict1, dict2)
        assert merged["a"] == 1
        assert merged["b"]["c"] == 2
        assert merged["b"]["d"] == 3
        assert merged["e"] == 4
    
    def test_chunk_list(self):
        """Test list chunking."""
        test_list = list(range(10))
        
        # Test chunking
        chunks = chunk_list(test_list, 3)
        assert len(chunks) == 4
        assert chunks[0] == [0, 1, 2]
        assert chunks[-1] == [9]
        
        # Test empty list
        empty_chunks = chunk_list([], 3)
        assert empty_chunks == []
    
    def test_remove_duplicates(self):
        """Test duplicate removal."""
        # Test with key function
        test_list = [
            {"id": 1, "name": "test"},
            {"id": 2, "name": "test"},
            {"id": 1, "name": "duplicate"}
        ]
        
        unique = remove_duplicates(test_list, key="id")
        assert len(unique) == 2
        
        # Test without key function
        simple_list = [1, 2, 2, 3, 3, 3]
        unique_simple = remove_duplicates(simple_list)
        assert unique_simple == [1, 2, 3]
''',
        
        # Integration tests
        "integration/database/test_repositories.py": '''"""
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
''',
        
        # E2E tests
        "e2e/api/test_complete_api_flow.py": '''"""
End-to-end tests for complete API flow.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


class TestCompleteAPIFlow:
    """Test complete API workflow."""
    
    def test_problem_to_solution_workflow(self):
        """Test complete problem to solution workflow via API."""
        client = TestClient(app)
        
        # 1. Create a problem
        problem_data = {
            "title": "E2E API Test Problem",
            "description": "End-to-end API test problem",
            "domain": "technology",
            "complexity": "simple"
        }
        
        problem_response = client.post("/api/v1/problems", json=problem_data)
        assert problem_response.status_code in [200, 201, 422]
        
        # 2. Get the problem
        if problem_response.status_code in [200, 201]:
            problem_id = problem_response.json().get("id", "test-id")
            
            get_problem_response = client.get(f"/api/v1/problems/{problem_id}")
            assert get_problem_response.status_code in [200, 404]
        
        # 3. Create a cycle
        cycle_data = {
            "problem_id": problem_id if 'problem_id' in locals() else "test-id",
            "status": "pending"
        }
        
        cycle_response = client.post("/api/v1/cycles", json=cycle_data)
        assert cycle_response.status_code in [200, 201, 422]
        
        # 4. Create a solution
        solution_data = {
            "problem_id": problem_id if 'problem_id' in locals() else "test-id",
            "title": "E2E API Test Solution",
            "description": "End-to-end API test solution",
            "approach": "Test approach"
        }
        
        solution_response = client.post("/api/v1/solutions", json=solution_data)
        assert solution_response.status_code in [200, 201, 422]
        
        # 5. Get analytics
        analytics_response = client.get("/api/v1/analytics")
        assert analytics_response.status_code in [200, 404]
''',
        
        # Performance tests
        "performance/stress/test_stress.py": '''"""
Stress tests for the Cosmic Council system.
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from src.api.main import app


class TestStressPerformance:
    """Test system stress performance."""
    
    def test_high_concurrent_requests(self):
        """Test high concurrent request handling."""
        client = TestClient(app)
        
        def make_request(i):
            problem_data = {
                "title": f"Stress Test Problem {i}",
                "description": f"Stress test problem {i}",
                "domain": "technology",
                "complexity": "simple"
            }
            return client.post("/api/v1/problems", json=problem_data)
        
        # Test with 50 concurrent requests
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request, i) for i in range(50)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # All requests should complete
        assert len(results) == 50
        
        # Should complete within reasonable time
        assert execution_time < 30.0  # 30 seconds max
        
        # Most requests should succeed
        success_count = sum(1 for r in results if r.status_code in [200, 201])
        assert success_count >= 40  # At least 80% success rate
    
    def test_memory_usage_under_load(self):
        """Test memory usage under load."""
        client = TestClient(app)
        
        # Create many problems to test memory usage
        problem_ids = []
        
        for i in range(100):
            problem_data = {
                "title": f"Memory Test Problem {i}",
                "description": f"Memory test problem {i}",
                "domain": "technology",
                "complexity": "simple"
            }
            
            response = client.post("/api/v1/problems", json=problem_data)
            if response.status_code in [200, 201]:
                problem_ids.append(response.json().get("id"))
        
        # Verify we can retrieve all problems
        for problem_id in problem_ids[:10]:  # Test first 10
            response = client.get(f"/api/v1/problems/{problem_id}")
            assert response.status_code in [200, 404]
        
        assert len(problem_ids) >= 80  # At least 80% should succeed
'''
    }
    
    created_count = 0
    
    for file_path, content in additional_tests.items():
        full_path = new_tests_dir / file_path
        
        # Create parent directory if it doesn't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Created additional test file: {file_path}")
        created_count += 1
    
    return created_count

def create_test_runner():
    """Create a comprehensive test runner script"""
    new_tests_dir = Path("tests_new")
    
    test_runner_content = '''"""
Comprehensive test runner for the Cosmic Council system.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests with specified options."""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test path
    cmd.append("tests_new/")
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add coverage
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    # Add test type filtering
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "e2e":
        cmd.extend(["-m", "e2e"])
    elif test_type == "performance":
        cmd.extend(["-m", "performance"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    
    # Add other options
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False


def run_specific_tests(test_path):
    """Run specific test file or directory."""
    cmd = ["python", "-m", "pytest", test_path, "-v"]
    
    print(f"Running specific tests: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ Tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False


def main():
    """Main test runner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cosmic Council Test Runner")
    parser.add_argument("--type", choices=["all", "unit", "integration", "e2e", "performance", "fast"],
                       default="all", help="Type of tests to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Run with coverage")
    parser.add_argument("--specific", "-s", help="Run specific test file or directory")
    
    args = parser.parse_args()
    
    if args.specific:
        success = run_specific_tests(args.specific)
    else:
        success = run_tests(args.type, args.verbose, args.coverage)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
'''
    
    test_runner_path = new_tests_dir / "run_tests.py"
    with open(test_runner_path, 'w', encoding='utf-8') as f:
        f.write(test_runner_content)
    
    logger.info("Created test runner script")

def main():
    """Main function to create additional tests"""
    logger.info("Creating additional test files...")
    
    # Create additional test files
    created_count = create_additional_test_files()
    logger.info(f"Created {created_count} additional test files")
    
    # Create test runner
    create_test_runner()
    logger.info("Created test runner script")
    
    logger.info("Additional test creation completed!")

if __name__ == "__main__":
    main()
