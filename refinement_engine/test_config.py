"""
Cosmic Council Refinement Engine - Test Configuration
Configuration and utilities for integration testing.
"""

import os
import asyncio
import tempfile
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import pytest
import pytest_asyncio


@dataclass
class TestConfig:
    """Test configuration class."""
    
    # Database settings
    test_database_url: str
    use_in_memory_db: bool
    
    # AI service settings
    mock_ai_services: bool
    openai_api_key: Optional[str]
    anthropic_api_key: Optional[str]
    
    # Security settings
    test_jwt_secret: str
    test_user_password: str
    
    # Monitoring settings
    enable_metrics_server: bool
    metrics_port: int
    enable_sentry: bool
    
    # Test settings
    test_timeout: int
    max_concurrent_tests: int
    cleanup_after_tests: bool
    
    # Performance settings
    performance_test_iterations: int
    load_test_concurrency: int


def get_test_config() -> TestConfig:
    """Get test configuration from environment variables."""
    return TestConfig(
        # Database settings
        test_database_url=os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:"),
        use_in_memory_db=os.getenv("USE_IN_MEMORY_DB", "true").lower() == "true",
        
        # AI service settings
        mock_ai_services=os.getenv("MOCK_AI_SERVICES", "true").lower() == "true",
        openai_api_key=os.getenv("TEST_OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("TEST_ANTHROPIC_API_KEY"),
        
        # Security settings
        test_jwt_secret=os.getenv("TEST_JWT_SECRET", "test-secret-key-for-testing-only"),
        test_user_password=os.getenv("TEST_USER_PASSWORD", "TestPassword123!"),
        
        # Monitoring settings
        enable_metrics_server=os.getenv("ENABLE_METRICS_SERVER", "false").lower() == "true",
        metrics_port=int(os.getenv("TEST_METRICS_PORT", "9091")),
        enable_sentry=os.getenv("ENABLE_SENTRY", "false").lower() == "true",
        
        # Test settings
        test_timeout=int(os.getenv("TEST_TIMEOUT", "300")),  # 5 minutes
        max_concurrent_tests=int(os.getenv("MAX_CONCURRENT_TESTS", "5")),
        cleanup_after_tests=os.getenv("CLEANUP_AFTER_TESTS", "true").lower() == "true",
        
        # Performance settings
        performance_test_iterations=int(os.getenv("PERFORMANCE_TEST_ITERATIONS", "10")),
        load_test_concurrency=int(os.getenv("LOAD_TEST_CONCURRENCY", "5"))
    )


class TestDatabaseManager:
    """Test database manager for integration tests."""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.temp_dir = None
        self.db_path = None
    
    async def setup(self):
        """Set up test database."""
        if self.config.use_in_memory_db:
            # Use in-memory SQLite
            self.db_path = "sqlite:///:memory:"
        else:
            # Use temporary file
            self.temp_dir = tempfile.mkdtemp()
            self.db_path = f"sqlite:///{self.temp_dir}/test.db"
        
        return self.db_path
    
    async def teardown(self):
        """Tear down test database."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)


class TestAIManager:
    """Test AI manager for integration tests."""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.mocked_responses = {}
    
    def setup_mocks(self):
        """Set up mocked AI responses."""
        if not self.config.mock_ai_services:
            return
        
        # Mock OpenAI responses
        self.mocked_responses["openai"] = {
            "research": {
                "content": "Research shows that renewable energy sources like solar and wind can significantly reduce carbon emissions.",
                "confidence": 0.85,
                "cost_usd": 0.01,
                "latency_ms": 1000
            },
            "planning": {
                "content": "A comprehensive plan should include: 1) Solar energy deployment, 2) Wind energy expansion, 3) Energy storage systems.",
                "confidence": 0.88,
                "cost_usd": 0.015,
                "latency_ms": 1200
            },
            "development": {
                "content": "Develop solar panel installation protocols, wind turbine maintenance procedures, and grid integration systems.",
                "confidence": 0.82,
                "cost_usd": 0.012,
                "latency_ms": 1100
            },
            "budget": {
                "content": "Estimated budget: $50M for solar, $30M for wind, $20M for storage systems. ROI: 15% over 10 years.",
                "confidence": 0.90,
                "cost_usd": 0.008,
                "latency_ms": 800
            },
            "market": {
                "content": "Market analysis shows strong demand for renewable energy solutions. Competition is moderate but growing.",
                "confidence": 0.87,
                "cost_usd": 0.009,
                "latency_ms": 900
            },
            "validation": {
                "content": "Solution validation: High confidence in technical feasibility, moderate confidence in market adoption.",
                "confidence": 0.83,
                "cost_usd": 0.007,
                "latency_ms": 700
            }
        }
        
        # Mock Anthropic responses
        self.mocked_responses["anthropic"] = {
            "research": {
                "content": "Claude analysis indicates that carbon capture technology combined with renewable energy offers the most promising path forward.",
                "confidence": 0.88,
                "cost_usd": 0.005,
                "latency_ms": 800
            },
            "planning": {
                "content": "Strategic plan: Phase 1 - Deploy solar/wind, Phase 2 - Implement carbon capture, Phase 3 - Scale globally.",
                "confidence": 0.91,
                "cost_usd": 0.007,
                "latency_ms": 900
            },
            "development": {
                "content": "Development roadmap: 1) Pilot projects, 2) Technology refinement, 3) Mass deployment, 4) Global scaling.",
                "confidence": 0.86,
                "cost_usd": 0.006,
                "latency_ms": 850
            },
            "budget": {
                "content": "Budget analysis: $100M total investment, $20M annual operating costs, 20% ROI projected.",
                "confidence": 0.92,
                "cost_usd": 0.004,
                "latency_ms": 600
            },
            "market": {
                "content": "Market assessment: High growth potential, regulatory support increasing, consumer demand rising.",
                "confidence": 0.89,
                "cost_usd": 0.005,
                "latency_ms": 700
            },
            "validation": {
                "content": "Validation results: Strong technical foundation, positive market indicators, regulatory alignment confirmed.",
                "confidence": 0.87,
                "cost_usd": 0.003,
                "latency_ms": 500
            }
        }
    
    def get_mock_response(self, provider: str, sector: str) -> Dict[str, Any]:
        """Get mock response for a provider and sector."""
        if not self.config.mock_ai_services:
            return None
        
        return self.mocked_responses.get(provider, {}).get(sector, {
            "content": f"Mock response for {provider} {sector}",
            "confidence": 0.8,
            "cost_usd": 0.01,
            "latency_ms": 1000
        })


class TestDataGenerator:
    """Generate test data for integration tests."""
    
    @staticmethod
    def generate_problem_data(problem_type: str = "carbon_emissions") -> Dict[str, Any]:
        """Generate test problem data."""
        problems = {
            "carbon_emissions": {
                "title": "How can we reduce global carbon emissions?",
                "description": "We need to develop a comprehensive strategy to reduce global carbon emissions by 50% over the next decade while maintaining economic growth and energy security.",
                "initial_layer": "deci",
                "max_iterations": 100
            },
            "renewable_energy": {
                "title": "How can we accelerate renewable energy adoption?",
                "description": "Develop a plan to increase renewable energy adoption from 20% to 80% of total energy production within 15 years.",
                "initial_layer": "deci",
                "max_iterations": 80
            },
            "sustainable_transport": {
                "title": "How can we make transportation more sustainable?",
                "description": "Create a strategy to transition from fossil fuel vehicles to electric and other sustainable transportation options.",
                "initial_layer": "deci",
                "max_iterations": 60
            },
            "carbon_capture": {
                "title": "How can we implement carbon capture technology?",
                "description": "Design a system for capturing and storing carbon dioxide from industrial processes and power plants.",
                "initial_layer": "deci",
                "max_iterations": 120
            },
            "energy_storage": {
                "title": "How can we improve energy storage systems?",
                "description": "Develop better energy storage solutions to support renewable energy integration and grid stability.",
                "initial_layer": "deci",
                "max_iterations": 90
            }
        }
        
        return problems.get(problem_type, problems["carbon_emissions"])
    
    @staticmethod
    def generate_user_data(user_type: str = "regular") -> Dict[str, Any]:
        """Generate test user data."""
        users = {
            "regular": {
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPassword123!",
                "role": "user"
            },
            "admin": {
                "username": "testadmin",
                "email": "admin@example.com",
                "password": "AdminPassword123!",
                "role": "admin"
            },
            "readonly": {
                "username": "testreadonly",
                "email": "readonly@example.com",
                "password": "ReadOnlyPassword123!",
                "role": "readonly"
            }
        }
        
        return users.get(user_type, users["regular"])
    
    @staticmethod
    def generate_layer_metrics(layer: str = "deci") -> Dict[str, Any]:
        """Generate test layer metrics."""
        base_metrics = {
            "revolutions_at_layer": 1,
            "total_cost_usd": 25.0,
            "total_latency_ms": 15000,
            "confidence_score": 0.8,
            "completeness_score": 0.75,
            "novelty_score": 0.2,
            "alignment_score": 0.9,
            "net_benefit_score": 0.7
        }
        
        # Adjust metrics based on layer
        layer_adjustments = {
            "deci": {"confidence_score": 0.8, "completeness_score": 0.75},
            "centi": {"confidence_score": 0.85, "completeness_score": 0.80},
            "milli": {"confidence_score": 0.90, "completeness_score": 0.85},
            "micro": {"confidence_score": 0.95, "completeness_score": 0.90},
            "nano": {"confidence_score": 0.98, "completeness_score": 0.95},
            "pico": {"confidence_score": 0.99, "completeness_score": 0.98},
            "femto": {"confidence_score": 0.995, "completeness_score": 0.99},
            "atto": {"confidence_score": 0.998, "completeness_score": 0.995},
            "zepto": {"confidence_score": 0.999, "completeness_score": 0.998},
            "yocto": {"confidence_score": 0.9995, "completeness_score": 0.999},
            "ronto": {"confidence_score": 0.9998, "completeness_score": 0.9995},
            "quecto": {"confidence_score": 0.9999, "completeness_score": 0.9998}
        }
        
        if layer in layer_adjustments:
            base_metrics.update(layer_adjustments[layer])
        
        return base_metrics


class TestAssertions:
    """Custom assertions for integration tests."""
    
    @staticmethod
    def assert_problem_context_valid(problem_context) -> None:
        """Assert that a problem context is valid."""
        assert problem_context is not None
        assert hasattr(problem_context, 'problem_id')
        assert hasattr(problem_context, 'title')
        assert hasattr(problem_context, 'description')
        assert hasattr(problem_context, 'layer_runs')
        assert hasattr(problem_context, 'refinements')
        assert hasattr(problem_context, 'answers')
        assert hasattr(problem_context, 'metadata')
        
        assert problem_context.problem_id is not None
        assert problem_context.title is not None
        assert problem_context.description is not None
        assert isinstance(problem_context.layer_runs, list)
        assert isinstance(problem_context.refinements, list)
        assert isinstance(problem_context.answers, list)
        assert isinstance(problem_context.metadata, dict)
    
    @staticmethod
    def assert_sector_result_valid(sector_result) -> None:
        """Assert that a sector result is valid."""
        assert sector_result is not None
        assert hasattr(sector_result, 'sector')
        assert hasattr(sector_result, 'status')
        assert hasattr(sector_result, 'output')
        assert hasattr(sector_result, 'metrics')
        assert hasattr(sector_result, 'handoff_data')
        assert hasattr(sector_result, 'cost_usd')
        
        assert sector_result.sector is not None
        assert sector_result.status in ["completed", "error", "pending"]
        assert isinstance(sector_result.metrics, dict)
        assert "confidence" in sector_result.metrics
        assert "completeness" in sector_result.metrics
        assert "novelty" in sector_result.metrics
        assert isinstance(sector_result.cost_usd, (int, float))
        assert sector_result.cost_usd >= 0
    
    @staticmethod
    def assert_escalator_decision_valid(decision) -> None:
        """Assert that an escalator decision is valid."""
        assert decision is not None
        assert hasattr(decision, 'action')
        assert hasattr(decision, 'reason')
        assert hasattr(decision, 'from_layer')
        assert hasattr(decision, 'confidence')
        
        assert decision.action is not None
        assert decision.reason is not None
        assert decision.from_layer is not None
        assert 0.0 <= decision.confidence <= 1.0
    
    @staticmethod
    def assert_health_check_valid(health_check) -> None:
        """Assert that a health check is valid."""
        assert health_check is not None
        assert hasattr(health_check, 'name')
        assert hasattr(health_check, 'status')
        assert hasattr(health_check, 'message')
        assert hasattr(health_check, 'response_time_ms')
        assert hasattr(health_check, 'timestamp')
        
        assert health_check.name is not None
        assert health_check.status is not None
        assert health_check.message is not None
        assert health_check.response_time_ms >= 0
        assert health_check.timestamp is not None


# Pytest configuration
def pytest_configure(config):
    """Configure pytest for integration tests."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection for integration tests."""
    for item in items:
        # Add integration marker to all tests in this file
        if "integration_tests" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker to end-to-end tests
        if "test_complete_problem_solving_workflow" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Add performance marker to performance tests
        if "performance" in item.name or "load" in item.name:
            item.add_marker(pytest.mark.performance)
        
        # Add security marker to security tests
        if "security" in item.name or "auth" in item.name:
            item.add_marker(pytest.mark.security)


# Test fixtures
@pytest.fixture(scope="session")
def test_config():
    """Get test configuration."""
    return get_test_config()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db_manager(test_config):
    """Set up test database manager."""
    db_manager = TestDatabaseManager(test_config)
    db_path = await db_manager.setup()
    yield db_manager, db_path
    await db_manager.teardown()


@pytest.fixture(scope="session")
def test_ai_manager(test_config):
    """Set up test AI manager."""
    ai_manager = TestAIManager(test_config)
    ai_manager.setup_mocks()
    return ai_manager


# Example usage
if __name__ == "__main__":
    # Test configuration
    config = get_test_config()
    print(f"Test configuration: {config}")
    
    # Test data generation
    problem_data = TestDataGenerator.generate_problem_data("carbon_emissions")
    print(f"Problem data: {problem_data}")
    
    user_data = TestDataGenerator.generate_user_data("admin")
    print(f"User data: {user_data}")
    
    layer_metrics = TestDataGenerator.generate_layer_metrics("deci")
    print(f"Layer metrics: {layer_metrics}")
    
    # Test AI manager
    ai_manager = TestAIManager(config)
    ai_manager.setup_mocks()
    
    openai_response = ai_manager.get_mock_response("openai", "research")
    print(f"OpenAI response: {openai_response}")
    
    anthropic_response = ai_manager.get_mock_response("anthropic", "planning")
    print(f"Anthropic response: {anthropic_response}")
