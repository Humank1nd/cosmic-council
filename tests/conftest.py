"""
Pytest configuration and shared fixtures for the Cosmic Council Framework testing suite
Updated to import directly from the current package layout.
"""

import atexit
import asyncio
import pytest
import tempfile
import os
import sys
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone
from pathlib import Path

# Add the project root and src paths to the Python path
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "applications"
CONFIG_DIR = ROOT_DIR / "config"
for p in [ROOT_DIR, SRC_DIR, APPS_DIR, CONFIG_DIR]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Isolate database writes to a temp SQLite file per process and allow anonymous access.
# Process-scoped paths avoid create_all race collisions when multiple pytest sessions run.
def _cleanup_sqlite_files(db_path: Path) -> None:
    for suffix in ("", "-journal", "-wal", "-shm"):
        candidate = Path(f"{db_path}{suffix}")
        try:
            candidate.unlink()
        except FileNotFoundError:
            pass
        except PermissionError:
            # Another process may still hold a transient handle; ignore during startup cleanup.
            pass


if "DATABASE_URL" in os.environ:
    TEMP_DB_PATH = None
else:
    TEMP_DB_PATH = Path(tempfile.gettempdir()) / f"cosmic_council_test_{os.getpid()}.db"
    _cleanup_sqlite_files(TEMP_DB_PATH)
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEMP_DB_PATH}"

os.environ.setdefault("ALLOW_ANONYMOUS", "true")

if TEMP_DB_PATH is not None:
    atexit.register(_cleanup_sqlite_files, TEMP_DB_PATH)

# Ensure tables are created once for the temp DB
import asyncio  # noqa: E402
from cosmic_council.database.unified_database_manager import get_database_manager  # noqa: E402

_db_manager = get_database_manager()
# Run table creation synchronously for tests
asyncio.run(_db_manager.create_tables())

# Import core components directly from current package structure
from cosmic_council.core.core import CosmicCouncil, EnhancedRedOwlAgent, EnhancedOrangeOrangutanAgent  # noqa: E402
from cosmic_council.core.types import ProblemStatement, ProblemComplexity  # noqa: E402
from cosmic_council.agents.unified_ai_agent_system import (  # noqa: E402
    UnifiedCosmicCouncilAgent,
    AgentType,
    AgentContext,
    AgentResult,
    LLMConfig,
    LLMProvider,
    LLMModel,
)
from cosmic_council.workflows.problem_solving_workflow import ProblemSolvingWorkflow, WorkflowStep  # noqa: E402
from cosmic_council.core.models import Problem as DBProblem, Cycle, Solution  # noqa: E402
from cosmic_council.database.unified_database_manager import get_session_context  # noqa: E402
from cosmic_council.utils.analytics_dashboard import AnalyticsDashboard, TimeRange, DashboardView  # noqa: E402
from applications.enterprise_policy_engine import EnterprisePolicyEngine, PolicyRule, PolicyType  # noqa: E402
from applications.purple_elephant_feedback_system import PurpleElephantFeedbackSystem, FeedbackType  # noqa: E402
from cosmic_council.integrations.unified_perpetual_thinking_system import (  # noqa: E402
    UnifiedPerpetualThinkingEngine,
    PerpetualAIThinkingEngine,
    AIEnhancementLevel,
    AIThinkingMode,
    PerpetualCycle,
    CycleType,
    CycleStatus,
    PatternType,
)
from cosmic_council.database.unified_database_service import PerpetualDatabaseService  # noqa: E402

# Local testing stub for missing AI LLM integration
class AILLMIntegration:  # type: ignore
    def __init__(self, *args, **kwargs):
        self.config = kwargs.get("config")

    async def enhance(self, *args, **kwargs):
        return {"status": "ok", "enhanced": True}


# Configure pytest
pytest_plugins = ["pytest_asyncio"]

# Ignore tests with missing module dependencies
collect_ignore = [
    "tests_new",
    "e2e/test_complete_workflow.py",
    "integration/test_red_to_orange_handoff.py",
    "performance/test_load_performance.py",
    "unit/test_enhanced_enterprise_agents.py",
    "unit/test_problem_solving_workflow.py",
]


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
async def cosmic_council() -> AsyncGenerator[CosmicCouncil, None]:
    """Provide a Cosmic Council instance for testing."""
    council = CosmicCouncil()
    yield council


@pytest.fixture
async def enhanced_red_owl_agent() -> AsyncGenerator[EnhancedRedOwlAgent, None]:
    """Provide an enhanced Red Owl agent for testing."""
    agent = EnhancedRedOwlAgent()
    yield agent


@pytest.fixture
async def enhanced_orange_orangutan_agent() -> AsyncGenerator[EnhancedOrangeOrangutanAgent, None]:
    """Provide an enhanced Orange Orangutan agent for testing."""
    agent = EnhancedOrangeOrangutanAgent()
    yield agent


@pytest.fixture
async def problem_solving_workflow() -> AsyncGenerator[ProblemSolvingWorkflow, None]:
    """Provide a problem-solving workflow for testing."""
    workflow = ProblemSolvingWorkflow()
    yield workflow


@pytest.fixture
async def ai_llm_integration() -> AsyncGenerator[AILLMIntegration, None]:
    """Provide an AI/LLM integration for testing."""
    integration = AILLMIntegration()
    yield integration


@pytest.fixture
async def analytics_dashboard() -> AsyncGenerator[AnalyticsDashboard, None]:
    """Provide an analytics dashboard for testing."""
    dashboard = AnalyticsDashboard()
    yield dashboard


@pytest.fixture
async def policy_engine() -> AsyncGenerator[EnterprisePolicyEngine, None]:
    """Provide a policy engine for testing."""
    engine = EnterprisePolicyEngine()
    yield engine


@pytest.fixture
async def feedback_system() -> AsyncGenerator[PurpleElephantFeedbackSystem, None]:
    """Provide a feedback system for testing."""
    system = PurpleElephantFeedbackSystem()
    yield system


@pytest.fixture
async def perpetual_ai_engine() -> AsyncGenerator[PerpetualAIThinkingEngine, None]:
    """Provide a perpetual AI thinking engine for testing."""
    ai_config = LLMConfig(
        provider=LLMProvider.MOCK,
        model=LLMModel.GPT_4,
        temperature=0.7,
        max_tokens=2000
    )
    engine = PerpetualAIThinkingEngine(
        database_url="sqlite:///:memory:",
        ai_config=ai_config
    )
    yield engine


@pytest.fixture
async def perpetual_database_service() -> AsyncGenerator[PerpetualDatabaseService, None]:
    """Provide a perpetual database service for testing."""
    service = PerpetualDatabaseService("sqlite:///:memory:")
    await service.create_tables()
    yield service


@pytest.fixture
def sample_problem() -> ProblemStatement:
    """Provide a sample problem for testing."""
    return ProblemStatement(
        title="Test Problem",
        description="A test problem for unit testing",
        complexity=ProblemComplexity.MODERATE,
        domain="Testing",
        stakeholders=["Test Stakeholder"],
        constraints={"budget": "$5K", "timeline": "1 week"},
        success_criteria=["Test criteria 1", "Test criteria 2"]
    )


@pytest.fixture
def sample_complex_problem() -> ProblemStatement:
    """Provide a complex sample problem for testing."""
    return ProblemStatement(
        title="Complex Test Problem",
        description="A complex test problem with multiple facets and stakeholders",
        complexity=ProblemComplexity.COMPLEX,
        domain="Complex Testing",
        stakeholders=["Stakeholder 1", "Stakeholder 2", "Stakeholder 3"],
        constraints={"budget": "$50K", "timeline": "3 months", "team_size": "10 people"},
        success_criteria=["Complex criteria 1", "Complex criteria 2", "Complex criteria 3"]
    )


@pytest.fixture
def sample_simple_problem() -> ProblemStatement:
    """Provide a simple sample problem for testing."""
    return ProblemStatement(
        title="Simple Test Problem",
        description="A simple test problem for basic testing",
        complexity=ProblemComplexity.SIMPLE,
        domain="Simple Testing",
        stakeholders=["Simple Stakeholder"],
        constraints={"budget": "$1K"},
        success_criteria=["Simple criteria"]
    )


@pytest.fixture
def sample_systemic_problem() -> ProblemStatement:
    """Provide a systemic sample problem for testing."""
    return ProblemStatement(
        title="Systemic Test Problem",
        description="A systemic test problem affecting multiple systems",
        complexity=ProblemComplexity.SYSTEMIC,
        domain="Systemic Testing",
        stakeholders=["System Stakeholder 1", "System Stakeholder 2", "System Stakeholder 3", "System Stakeholder 4"],
        constraints={"budget": "$100K", "timeline": "6 months", "regulatory": "strict"},
        success_criteria=["Systemic criteria 1", "Systemic criteria 2", "Systemic criteria 3", "Systemic criteria 4"]
    )


@pytest.fixture
def sample_problem_data() -> dict:
    """Provide sample problem data for testing."""
    return {
        "title": "Test Problem Data",
        "description": "Test problem data for testing",
        "complexity": "moderate",
        "domain": "Test Domain",
        "stakeholders": ["Test Stakeholder"],
        "constraints": {"budget": "$5K"},
        "success_criteria": ["Test criteria"]
    }


@pytest.fixture
def sample_cycle_data() -> dict:
    """Provide sample cycle data for testing."""
    return {
        "objective": "Test cycle objective",
        "priority": 3,
        "ai_enhanced": False,
        "config": {
            "max_iterations": 3,
            "confidence_threshold": 0.8
        }
    }


@pytest.fixture
def sample_solution_data() -> dict:
    """Provide sample solution data for testing."""
    return {
        "title": "Test Solution",
        "description": "A test solution for testing",
        "components": [
            {
                "name": "Component 1",
                "description": "First component",
                "priority": 1,
                "estimated_effort": "1 week"
            },
            {
                "name": "Component 2",
                "description": "Second component",
                "priority": 2,
                "estimated_effort": "2 weeks"
            }
        ]
    }


@pytest.fixture
def mock_llm_response() -> dict:
    """Provide a mock LLM response for testing."""
    return {
        "status": "completed",
        "confidence": 0.85,
        "insights": ["Mock insight 1", "Mock insight 2"],
        "recommendations": ["Mock recommendation 1", "Mock recommendation 2"],
        "analysis_depth": "moderate",
        "framework_applied": "mock_framework"
    }


@pytest.fixture
def mock_enterprise_result() -> dict:
    """Provide a mock enterprise result for testing."""
    return {
        "status": "completed",
        "confidence": 0.9,
        "insights": ["Enterprise insight 1", "Enterprise insight 2"],
        "recommendations": ["Enterprise recommendation 1", "Enterprise recommendation 2"],
        "processing_time": 2.5,
        "metadata": {
            "enterprise": "test_enterprise",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@pytest.fixture
def mock_workflow_result() -> dict:
    """Provide a mock workflow result for testing."""
    return {
        "status": "completed",
        "overall_confidence": 0.88,
        "total_processing_time": 15.5,
        "step_results": {
            "problem_definition": {"status": "completed", "confidence": 0.9},
            "stakeholder_analysis": {"status": "completed", "confidence": 0.85},
            "constraint_analysis": {"status": "completed", "confidence": 0.9},
            "red_owl_research": {"status": "completed", "confidence": 0.88},
            "orange_orangutan_planning": {"status": "completed", "confidence": 0.87},
            "yellow_honeybee_development": {"status": "completed", "confidence": 0.89},
            "green_tortoise_resources": {"status": "completed", "confidence": 0.86},
            "blue_dolphin_communication": {"status": "completed", "confidence": 0.88},
            "purple_elephant_support": {"status": "completed", "confidence": 0.91},
            "final_synthesis": {"status": "completed", "confidence": 0.88}
        },
        "enterprise_results": {
            "red_owl": {"status": "completed", "confidence": 0.88},
            "orange_orangutan": {"status": "completed", "confidence": 0.87},
            "yellow_honeybee": {"status": "completed", "confidence": 0.89},
            "green_tortoise": {"status": "completed", "confidence": 0.86},
            "blue_dolphin": {"status": "completed", "confidence": 0.88},
            "purple_elephant": {"status": "completed", "confidence": 0.91}
        }
    }


@pytest.fixture
def mock_analytics_data() -> dict:
    """Provide mock analytics data for testing."""
    return {
        "system_uptime": 99.95,
        "total_requests": 125000,
        "average_response_time": 245.5,
        "error_rate": 0.02,
        "throughput": 1250.0,
        "total_problems": 150,
        "problems_resolved": 142,
        "success_rate": 94.67,
        "total_cycles": 108,
        "cycles_completed": 102,
        "average_cycle_duration": 2400.0,
        "total_solutions": 142,
        "solutions_implemented": 128,
        "average_quality_score": 0.87,
        "innovation_index": 0.84
    }


@pytest.fixture
def mock_policy_rule() -> PolicyRule:
    """Provide a mock policy rule for testing."""
    return PolicyRule(
        rule_id="test_rule_1",
        name="Test Policy Rule",
        description="A test policy rule for testing",
        policy_type=PolicyType.ACCESS_CONTROL,
        condition="user.role == 'admin'",
        action="allow",
        priority=1,
        is_active=True
    )


@pytest.fixture
def mock_feedback_cycle() -> dict:
    """Provide mock feedback cycle data for testing."""
    return {
        "cycle_id": "test_cycle_1",
        "feedback_type": FeedbackType.SYSTEM_REFLECTION,
        "scope": "enterprise_level",
        "metrics": {
            "performance_score": 0.85,
            "efficiency_score": 0.88,
            "satisfaction_score": 0.92
        },
        "insights": ["Test insight 1", "Test insight 2"],
        "recommendations": ["Test recommendation 1", "Test recommendation 2"]
    }


@pytest.fixture
def mock_database_session():
    """Provide a mock database session for testing."""
    session = Mock()
    session.query.return_value = Mock()
    session.add.return_value = None
    session.commit.return_value = None
    session.rollback.return_value = None
    session.close.return_value = None
    return session


@pytest.fixture
def mock_redis_client():
    """Provide a mock Redis client for testing."""
    client = Mock()
    client.get.return_value = None
    client.set.return_value = True
    client.delete.return_value = True
    client.exists.return_value = False
    client.expire.return_value = True
    return client


@pytest.fixture
def mock_http_client():
    """Provide a mock HTTP client for testing."""
    client = Mock()
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"status": "success"}
    client.get.return_value = response
    client.post.return_value = response
    client.put.return_value = response
    client.delete.return_value = response
    return client


@pytest.fixture
def mock_websocket():
    """Provide a mock WebSocket for testing."""
    websocket = AsyncMock()
    websocket.accept.return_value = None
    websocket.send_text.return_value = None
    websocket.receive_text.return_value = "test message"
    websocket.close.return_value = None
    return websocket


@pytest.fixture
def mock_file_system():
    """Provide a mock file system for testing."""
    fs = Mock()
    fs.exists.return_value = True
    fs.read_text.return_value = "test content"
    fs.write_text.return_value = None
    fs.mkdir.return_value = None
    fs.rmdir.return_value = None
    return fs


@pytest.fixture
def mock_logger():
    """Provide a mock logger for testing."""
    logger = Mock()
    logger.info.return_value = None
    logger.warning.return_value = None
    logger.error.return_value = None
    logger.debug.return_value = None
    return logger


@pytest.fixture
def mock_config():
    """Provide a mock configuration for testing."""
    config = Mock()
    config.database_url = "sqlite:///:memory:"
    config.redis_url = "redis://localhost:6379/0"
    config.log_level = "INFO"
    config.debug = False
    config.secret_key = "test-secret-key"
    config.api_key = "test-api-key"
    return config


@pytest.fixture
def mock_environment():
    """Provide a mock environment for testing."""
    env = {
        "DATABASE_URL": "sqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/0",
        "LOG_LEVEL": "INFO",
        "DEBUG": "False",
        "SECRET_KEY": "test-secret-key",
        "API_KEY": "test-api-key",
        "OPENAI_API_KEY": "test-openai-key",
        "ANTHROPIC_API_KEY": "test-anthropic-key"
    }
    return env


@pytest.fixture
def sample_perpetual_session_data():
    """Provide sample perpetual session data for testing."""
    return {
        "session_name": "Test Perpetual Session",
        "initial_input": "How can we solve global climate change through innovative technology and policy?",
        "mode": "collaborative",
        "goals": ["sustainability", "economic_viability", "social_equity"],
        "success_criteria": ["50% carbon reduction", "maintain GDP growth", "create green jobs"],
        "ai_enhancement_level": "enhanced",
        "ai_learning_enabled": True,
        "ai_adaptation_enabled": True,
        "ai_breakthrough_detection": True
    }


@pytest.fixture
def sample_ai_enhancement_data():
    """Provide sample AI enhancement data for testing."""
    return {
        "cycle_id": "test-cycle-123",
        "ai_enhancement_level": AIEnhancementLevel.ENHANCED,
        "ai_thinking_mode": AIThinkingMode.CREATIVE,
        "ai_prompt_used": "test prompt for enhancement",
        "ai_response_summary": "AI enhanced the input with creative insights",
        "ai_confidence": 0.85,
        "ai_reasoning": "AI reasoning for enhancement decision",
        "ai_tokens_used": 150,
        "ai_processing_time": 1.2,
        "impact_score": 0.78
    }


@pytest.fixture
def sample_perpetual_cycle():
    """Provide a sample perpetual cycle for testing."""
    return PerpetualCycle(
        id="test-cycle-123",
        cycle_number=1,
        cycle_type=CycleType.EXPLORATION,
        status=CycleStatus.RUNNING,
        input_data="Test input for perpetual cycle",
        output_data={"synthesis": {"summary": "Test synthesis"}},
        confidence_score=0.8,
        creativity_score=0.75,
        wisdom_density=0.7,
        pattern_type=PatternType.CONVERGENCE,
        processing_time=2.5
    )


@pytest.fixture
def mock_perpetual_analytics():
    """Provide mock perpetual analytics data for testing."""
    return {
        "session_id": "test-session-123",
        "session_name": "Test Perpetual Session",
        "ai_enhancement_level": "enhanced",
        "status": "active",
        "total_ai_enhanced_cycles": 5,
        "avg_ai_confidence": 0.87,
        "avg_impact_score": 0.82,
        "total_ai_tokens_used": 1200,
        "total_ai_processing_time_seconds": 8.5,
        "ai_session_insights_count": 6,
        "ai_learning_events_count": 2,
        "collaborative_metrics": {
            "total_cycles": 5,
            "avg_confidence": 0.87,
            "avg_creativity": 0.75,
            "avg_wisdom_density": 0.7
        }
    }


# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.performance = pytest.mark.performance
pytest.mark.security = pytest.mark.security
pytest.mark.slow = pytest.mark.slow


# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add unit marker to tests in unit/ directory
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        # Add integration marker to tests in integration/ directory
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        # Add e2e marker to tests in e2e/ directory
        elif "e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        # Add performance marker to tests in performance/ directory
        elif "performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        # Add security marker to tests in security/ directory
        elif "security" in item.nodeid:
            item.add_marker(pytest.mark.security)
        # Add slow marker to tests that take longer than 5 seconds
        if "slow" in item.name or "load" in item.name or "stress" in item.name:
            item.add_marker(pytest.mark.slow)
