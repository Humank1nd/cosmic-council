"""
Cosmic Council Refinement Engine - Integration Tests
Comprehensive integration tests that test actual functionality end-to-end.
"""

import pytest
import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, AsyncMock
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import all the components we need to test
try:
    from .database import (
        DatabaseManager, ProblemModel, LayerRunModel, SectorRunModel,
        RefinementModel, AnswerModel, LayerModel, initialize_database
    )
except ImportError:
    from database import (
        DatabaseManager, ProblemModel, LayerRunModel, SectorRunModel,
        RefinementModel, AnswerModel, LayerModel, initialize_database
    )
try:
    from .ai_integrations import (
        AIIntegrationManager, OpenAIProvider, AnthropicProvider,
        RAGProvider, GraphAnalysisProvider, OptimizationProvider,
        initialize_ai_integrations
    )
except ImportError:
    from ai_integrations import (
        AIIntegrationManager, OpenAIProvider, AnthropicProvider,
        RAGProvider, GraphAnalysisProvider, OptimizationProvider,
        initialize_ai_integrations
    )
try:
    from .security import (
        SecurityManager, User, APIKey, Permission, UserRole,
        LoginRequest, ProblemSubmissionRequest, UserCreateRequest,
        initialize_security
    )
except ImportError:
    from security import (
        SecurityManager, User, APIKey, Permission, UserRole,
        LoginRequest, ProblemSubmissionRequest, UserCreateRequest,
        initialize_security
    )
try:
    from .escalator_fixed import EscalatorEngine, SolutionCandidate, EscalatorAction
    from .layer_orchestration import LayerOrchestrator, ProblemContext
    from .sector_engine import SectorEngine, SectorType, SectorResult
    from .refinement_tracker import RefinementTracker, TrackingEventType
    from .monitoring import MetricsCollector, initialize_monitoring
    from .health_checks import HealthChecker, initialize_health_checks
    from .error_handling import ErrorHandler, initialize_error_handling
    from .secure_api import app as secure_app
    from .monitoring_api import app as monitoring_app
except ImportError:
    from escalator_fixed import EscalatorEngine, SolutionCandidate, EscalatorAction
    from layer_orchestration import LayerOrchestrator, ProblemContext
    from sector_engine import SectorEngine, SectorType, SectorResult
    from refinement_tracker import RefinementTracker, TrackingEventType
    from monitoring import MetricsCollector, initialize_monitoring
    from health_checks import HealthChecker, initialize_health_checks
    from error_handling import ErrorHandler, initialize_error_handling
    from secure_api import app as secure_app
    from monitoring_api import app as monitoring_app


class IntegrationTestBase:
    """Base class for integration tests with common setup and teardown."""
    
    @pytest.fixture(scope="class")
    async def test_database(self):
        """Set up test database."""
        # Use in-memory SQLite for testing
        engine = create_engine("sqlite:///:memory:", echo=False)
        
        # Create tables
        from .database import Base
        Base.metadata.create_all(engine)
        
        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create database manager
        db_manager = DatabaseManager("sqlite:///:memory:")
        
        yield db_manager
        
        # Cleanup
        await db_manager.close()
    
    @pytest.fixture(scope="class")
    async def test_ai_manager(self):
        """Set up test AI manager with mocked providers."""
        # Mock AI providers for testing
        with patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test-key',
            'ANTHROPIC_API_KEY': 'test-key'
        }):
            ai_manager = initialize_ai_integrations()
            
            # Mock the actual AI calls
            ai_manager.providers["openai"] = Mock()
            ai_manager.providers["openai"].generate_response = AsyncMock(return_value=Mock(
                content="Test AI response",
                confidence=0.85,
                cost_usd=0.01,
                latency_ms=1000,
                metadata={"model": "gpt-4", "tokens": 100}
            ))
            
            ai_manager.providers["anthropic"] = Mock()
            ai_manager.providers["anthropic"].generate_response = AsyncMock(return_value=Mock(
                content="Test Claude response",
                confidence=0.88,
                cost_usd=0.005,
                latency_ms=800,
                metadata={"model": "claude-3", "tokens": 80}
            ))
            
            yield ai_manager
    
    @pytest.fixture(scope="class")
    async def test_security_manager(self):
        """Set up test security manager."""
        security_manager = initialize_security()
        
        # Create test user
        user_data = UserCreateRequest(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
            role="user"
        )
        
        user = await security_manager.create_user(user_data)
        
        yield security_manager, user
    
    @pytest.fixture(scope="class")
    async def test_monitoring(self):
        """Set up test monitoring."""
        metrics_collector, sentry = initialize_monitoring({
            "enable_metrics_server": False,
            "enable_sentry": False
        })
        
        health_checker = initialize_health_checks({
            "enable_continuous_monitoring": False
        })
        
        yield metrics_collector, sentry, health_checker
    
    @pytest.fixture(scope="class")
    async def test_error_handler(self):
        """Set up test error handler."""
        error_handler = initialize_error_handling()
        yield error_handler


class TestDatabaseIntegration(IntegrationTestBase):
    """Test database integration functionality."""
    
    @pytest.mark.asyncio
    async def test_problem_lifecycle(self, test_database):
        """Test complete problem lifecycle in database."""
        db_manager = test_database
        
        # Create problem
        problem_id = await db_manager.create_problem(
            title="Test Problem",
            description="How can we reduce carbon emissions?",
            initial_layer="deci"
        )
        
        assert problem_id is not None
        
        # Get problem
        problem = await db_manager.get_problem(problem_id)
        assert problem is not None
        assert problem["title"] == "Test Problem"
        assert problem["description"] == "How can we reduce carbon emissions?"
        assert problem["status"] == "open"
        
        # Create layer run
        layer_run_id = await db_manager.create_layer_run(problem_id, "deci", 1)
        assert layer_run_id is not None
        
        # Update layer run
        await db_manager.update_layer_run(
            layer_run_id,
            status="completed",
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            total_cost_usd=50.0,
            total_latency_ms=30000
        )
        
        # Create sector run
        sector_run_id = await db_manager.create_sector_run(
            layer_run_id,
            "red",
            1,
            output_json={"confidence": 0.8, "content": "Test output"},
            metrics={"latency_ms": 1000, "cost_usd": 5.0}
        )
        assert sector_run_id is not None
        
        # Create refinement
        refinement_id = await db_manager.create_refinement(
            problem_id,
            "deci",
            "centi",
            "Need deeper analysis",
            "How can we reduce carbon emissions at the centi level?",
            {"decision": "refine", "confidence": 0.7}
        )
        assert refinement_id is not None
        
        # Create answer
        answer_id = await db_manager.create_answer(
            problem_id,
            "centi",
            {"solution": "Implement renewable energy"},
            confidence_score=0.9,
            completeness_score=0.85,
            novelty_score=0.3,
            alignment_score=0.95,
            net_benefit_score=0.8
        )
        assert answer_id is not None
        
        # Get problem genealogy
        genealogy = await db_manager.get_problem_genealogy(problem_id)
        assert genealogy is not None
        assert genealogy["problem_id"] == problem_id
        assert len(genealogy["layer_runs"]) == 1
        assert len(genealogy["refinements"]) == 1
        assert len(genealogy["answers"]) == 1
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, test_database):
        """Test concurrent database operations."""
        db_manager = test_database
        
        # Create multiple problems concurrently
        tasks = []
        for i in range(10):
            task = db_manager.create_problem(
                title=f"Test Problem {i}",
                description=f"Test description {i}",
                initial_layer="deci"
            )
            tasks.append(task)
        
        problem_ids = await asyncio.gather(*tasks)
        
        # Verify all problems were created
        assert len(problem_ids) == 10
        assert all(pid is not None for pid in problem_ids)
        
        # Verify all problems exist
        for problem_id in problem_ids:
            problem = await db_manager.get_problem(problem_id)
            assert problem is not None
            assert problem["status"] == "open"


class TestAIIntegration(IntegrationTestBase):
    """Test AI integration functionality."""
    
    @pytest.mark.asyncio
    async def test_ai_provider_integration(self, test_ai_manager):
        """Test AI provider integration."""
        ai_manager = test_ai_manager
        
        # Test OpenAI provider
        response = await ai_manager.process_with_llm(
            "What are the key factors in reducing carbon emissions?",
            provider="openai"
        )
        
        assert response is not None
        assert response.content == "Test AI response"
        assert response.confidence == 0.85
        assert response.cost_usd == 0.01
        assert response.latency_ms == 1000
        
        # Test Anthropic provider
        response = await ai_manager.process_with_llm(
            "What are the key factors in reducing carbon emissions?",
            provider="anthropic"
        )
        
        assert response is not None
        assert response.content == "Test Claude response"
        assert response.confidence == 0.88
        assert response.cost_usd == 0.005
        assert response.latency_ms == 800
    
    @pytest.mark.asyncio
    async def test_rag_integration(self, test_ai_manager):
        """Test RAG system integration."""
        ai_manager = test_ai_manager
        
        # Mock RAG response
        ai_manager.providers["rag"].query = AsyncMock(return_value=Mock(
            content="RAG response based on retrieved documents",
            confidence=0.80,
            cost_usd=0.001,
            latency_ms=500,
            metadata={"retrieved_docs": 3, "vector_store_type": "chroma"}
        ))
        
        response = await ai_manager.process_with_rag(
            "What are the latest developments in carbon capture technology?"
        )
        
        assert response is not None
        assert response.content == "RAG response based on retrieved documents"
        assert response.confidence == 0.80
        assert response.metadata["retrieved_docs"] == 3
    
    @pytest.mark.asyncio
    async def test_graph_analysis_integration(self, test_ai_manager):
        """Test graph analysis integration."""
        ai_manager = test_ai_manager
        
        # Mock graph analysis response
        ai_manager.providers["graph"].analyze_dependencies = AsyncMock(return_value=Mock(
            content="Graph analysis shows critical dependencies between energy and transportation sectors",
            confidence=0.85,
            cost_usd=0.0,
            latency_ms=200,
            metadata={
                "nodes": 4,
                "edges": 3,
                "density": 0.5,
                "critical_paths": [["energy", "transportation", "industry"]],
                "bottlenecks": ["energy"]
            }
        ))
        
        entities = ["energy", "transportation", "industry", "agriculture"]
        relationships = [
            ("energy", "transportation", "powers"),
            ("energy", "industry", "powers"),
            ("transportation", "industry", "transports")
        ]
        
        response = await ai_manager.process_with_graph_analysis(
            "Carbon emission reduction dependencies",
            entities,
            relationships
        )
        
        assert response is not None
        assert response.content == "Graph analysis shows critical dependencies between energy and transportation sectors"
        assert response.metadata["nodes"] == 4
        assert response.metadata["edges"] == 3
        assert "energy" in response.metadata["bottlenecks"]
    
    @pytest.mark.asyncio
    async def test_optimization_integration(self, test_ai_manager):
        """Test optimization integration."""
        ai_manager = test_ai_manager
        
        # Mock optimization response
        ai_manager.providers["optimization"].optimize_solution = AsyncMock(return_value=Mock(
            content="Optimization completed. Optimal solution: 60% solar, 30% wind, 10% nuclear",
            confidence=0.90,
            cost_usd=0.0,
            latency_ms=300,
            metadata={
                "status": "optimal",
                "objective_value": 0.85,
                "variables": {"solar": 0.6, "wind": 0.3, "nuclear": 0.1}
            }
        ))
        
        response = await ai_manager.process_with_optimization(
            objective="minimize carbon emissions",
            constraints=["budget limit", "time constraint"],
            variables=["solar", "wind", "nuclear"],
            problem_type="linear"
        )
        
        assert response is not None
        assert response.content == "Optimization completed. Optimal solution: 60% solar, 30% wind, 10% nuclear"
        assert response.confidence == 0.90
        assert response.metadata["status"] == "optimal"
        assert response.metadata["variables"]["solar"] == 0.6


class TestSecurityIntegration(IntegrationTestBase):
    """Test security integration functionality."""
    
    @pytest.mark.asyncio
    async def test_authentication_flow(self, test_security_manager):
        """Test complete authentication flow."""
        security_manager, user = test_security_manager
        
        # Test user authentication
        authenticated_user = await security_manager.authenticate_user(
            "testuser",
            "TestPassword123!"
        )
        
        assert authenticated_user is not None
        assert authenticated_user.username == "testuser"
        assert authenticated_user.is_active is True
        
        # Test token creation
        token = security_manager.create_access_token(
            authenticated_user.user_id,
            authenticated_user.permissions
        )
        
        assert token is not None
        assert len(token) > 0
        
        # Test token verification
        payload = security_manager.verify_access_token(token)
        assert payload["sub"] == authenticated_user.user_id
        assert "permissions" in payload
        
        # Test API key creation
        api_key = await security_manager.create_api_key(
            "test-key",
            authenticated_user.user_id,
            {Permission.CREATE_PROBLEM, Permission.READ_PROBLEM}
        )
        
        assert api_key is not None
        assert len(api_key) > 0
        
        # Test API key authentication
        api_key_record = await security_manager.authenticate_api_key(api_key)
        assert api_key_record is not None
        assert api_key_record.name == "test-key"
        assert api_key_record.user_id == authenticated_user.user_id
    
    @pytest.mark.asyncio
    async def test_authorization_flow(self, test_security_manager):
        """Test authorization flow."""
        security_manager, user = test_security_manager
        
        # Test permission checking
        assert security_manager.check_permission(
            user.permissions,
            Permission.CREATE_PROBLEM
        )
        
        assert security_manager.check_permission(
            user.permissions,
            Permission.READ_PROBLEM
        )
        
        # Test multiple permissions
        required_permissions = {Permission.CREATE_PROBLEM, Permission.READ_PROBLEM}
        assert security_manager.check_permissions(
            user.permissions,
            required_permissions
        )
        
        # Test insufficient permissions
        assert not security_manager.check_permission(
            user.permissions,
            Permission.SYSTEM_ADMIN
        )
    
    @pytest.mark.asyncio
    async def test_input_validation(self, test_security_manager):
        """Test input validation and sanitization."""
        security_manager, user = test_security_manager
        
        # Test valid input
        valid_data = {
            "title": "Test Problem",
            "description": "This is a test problem description",
            "initial_layer": "deci",
            "max_iterations": 100
        }
        
        validated_data = security_manager.validate_problem_input(valid_data)
        assert validated_data["title"] == "Test Problem"
        assert validated_data["description"] == "This is a test problem description"
        assert validated_data["initial_layer"] == "deci"
        assert validated_data["max_iterations"] == 100
        
        # Test input sanitization
        malicious_input = "'; DROP TABLE users; --"
        sanitized = security_manager.sanitize_input(malicious_input)
        assert "DROP TABLE" not in sanitized
        
        # Test XSS prevention
        xss_input = "<script>alert('XSS')</script>"
        sanitized = security_manager.sanitize_input(xss_input)
        assert "<script>" not in sanitized


class TestEscalatorIntegration(IntegrationTestBase):
    """Test escalator integration functionality."""
    
    @pytest.mark.asyncio
    async def test_escalator_decision_flow(self):
        """Test escalator decision flow."""
        escalator = EscalatorEngine()
        
        # Test solution that meets resolution criteria
        solution = SolutionCandidate(
            solution_text="Implement renewable energy sources",
            confidence_score=0.9,
            completeness_score=0.85,
            novelty_score=0.3,
            alignment_score=0.95,
            net_benefit_score=0.8
        )
        
        layer_metrics = {
            "revolutions_at_layer": 1,
            "total_cost_usd": 25.0,
            "total_latency_ms": 15000,
            "confidence_score": 0.9,
            "completeness_score": 0.85
        }
        
        problem_context = {
            "original_question": "How can we reduce global carbon emissions?",
            "problem_id": "test-problem-001"
        }
        
        decision = escalator.decide(
            problem_id="test-problem-001",
            current_layer="deci",
            solution_candidate=solution,
            layer_metrics=layer_metrics,
            problem_context=problem_context
        )
        
        assert decision is not None
        assert decision.action in [EscalatorAction.STAY, EscalatorAction.REFINE, EscalatorAction.RESOLVE]
        assert decision.from_layer == "deci"
        assert decision.confidence > 0.0
        
        # Test solution that needs refinement
        poor_solution = SolutionCandidate(
            solution_text="Use renewable energy",
            confidence_score=0.6,
            completeness_score=0.5,
            novelty_score=0.1,
            alignment_score=0.8,
            net_benefit_score=0.3
        )
        
        decision = escalator.decide(
            problem_id="test-problem-002",
            current_layer="deci",
            solution_candidate=poor_solution,
            layer_metrics=layer_metrics,
            problem_context=problem_context
        )
        
        assert decision is not None
        # Should either refine or stay, not resolve
        assert decision.action in [EscalatorAction.STAY, EscalatorAction.REFINE]
    
    @pytest.mark.asyncio
    async def test_escalator_learning(self):
        """Test escalator learning from previous decisions."""
        escalator = EscalatorEngine()
        
        # Make multiple decisions to test learning
        for i in range(5):
            solution = SolutionCandidate(
                solution_text=f"Solution {i}",
                confidence_score=0.7 + (i * 0.05),
                completeness_score=0.6 + (i * 0.05),
                novelty_score=0.2,
                alignment_score=0.9,
                net_benefit_score=0.7
            )
            
            layer_metrics = {
                "revolutions_at_layer": 1,
                "total_cost_usd": 20.0 + (i * 5.0),
                "total_latency_ms": 10000 + (i * 1000),
                "confidence_score": 0.7 + (i * 0.05),
                "completeness_score": 0.6 + (i * 0.05)
            }
            
            decision = escalator.decide(
                problem_id=f"test-problem-{i}",
                current_layer="deci",
                solution_candidate=solution,
                layer_metrics=layer_metrics,
                problem_context={"original_question": "Test question"}
            )
            
            assert decision is not None
        
        # Test performance analytics
        analytics = escalator.get_performance_analytics()
        assert analytics is not None
        assert "total_decisions" in analytics
        assert analytics["total_decisions"] == 5


class TestSectorEngineIntegration(IntegrationTestBase):
    """Test sector engine integration functionality."""
    
    @pytest.mark.asyncio
    async def test_sector_execution_flow(self, test_ai_manager):
        """Test sector execution flow."""
        # Mock AI manager
        ai_manager = test_ai_manager
        
        # Create sector engine
        sector_engine = SectorEngine("deci", ai_manager)
        
        # Test Red sector (Research)
        result = await sector_engine.execute_red_sector(
            problem_statement="How can we reduce carbon emissions?",
            evidence_refs=[],
            assumptions=[],
            constraints={}
        )
        
        assert result is not None
        assert result.sector == SectorType.RED
        assert result.status == "completed"
        assert result.metrics is not None
        assert "confidence" in result.metrics
        assert "completeness" in result.metrics
        assert "novelty" in result.metrics
        
        # Test Orange sector (Planning)
        handoff_data = result.handoff_data
        result = await sector_engine.execute_orange_sector(
            problem_statement="How can we reduce carbon emissions?",
            evidence_refs=handoff_data.evidence_refs,
            assumptions=handoff_data.assumptions,
            constraints=handoff_data.constraints
        )
        
        assert result is not None
        assert result.sector == SectorType.ORANGE
        assert result.status == "completed"
        assert result.handoff_data is not None
        
        # Test Yellow sector (Development)
        handoff_data = result.handoff_data
        result = await sector_engine.execute_yellow_sector(
            problem_statement="How can we reduce carbon emissions?",
            evidence_refs=handoff_data.evidence_refs,
            assumptions=handoff_data.assumptions,
            constraints=handoff_data.constraints
        )
        
        assert result is not None
        assert result.sector == SectorType.YELLOW
        assert result.status == "completed"
    
    @pytest.mark.asyncio
    async def test_sector_error_handling(self, test_ai_manager):
        """Test sector error handling."""
        # Mock AI manager to raise errors
        ai_manager = test_ai_manager
        ai_manager.providers["openai"].generate_response = AsyncMock(
            side_effect=Exception("AI service error")
        )
        
        sector_engine = SectorEngine("deci", ai_manager)
        
        # Test error handling in Red sector
        result = await sector_engine.execute_red_sector(
            problem_statement="How can we reduce carbon emissions?",
            evidence_refs=[],
            assumptions=[],
            constraints={}
        )
        
        # Should handle error gracefully
        assert result is not None
        assert result.status in ["completed", "error"]
        if result.status == "error":
            assert result.error_message is not None


class TestLayerOrchestrationIntegration(IntegrationTestBase):
    """Test layer orchestration integration functionality."""
    
    @pytest.mark.asyncio
    async def test_problem_processing_flow(self, test_database, test_ai_manager):
        """Test complete problem processing flow."""
        db_manager = test_database
        ai_manager = test_ai_manager
        
        # Create orchestrator
        orchestrator = LayerOrchestrator()
        
        # Create problem
        problem_id = await db_manager.create_problem(
            title="Integration Test Problem",
            description="How can we reduce carbon emissions?",
            initial_layer="deci"
        )
        
        # Process problem
        problem_context = await orchestrator.process_problem_continuously(
            problem_id=problem_id,
            title="Integration Test Problem",
            description="How can we reduce carbon emissions?",
            max_iterations=10
        )
        
        assert problem_context is not None
        assert problem_context.problem_id == problem_id
        assert problem_context.title == "Integration Test Problem"
        assert problem_context.description == "How can we reduce carbon emissions?"
        
        # Verify problem was processed
        assert len(problem_context.layer_runs) > 0
        assert problem_context.metadata is not None
        assert "status" in problem_context.metadata
    
    @pytest.mark.asyncio
    async def test_layer_refinement_flow(self, test_database, test_ai_manager):
        """Test layer refinement flow."""
        db_manager = test_database
        ai_manager = test_ai_manager
        
        # Create orchestrator
        orchestrator = LayerOrchestrator()
        
        # Create problem
        problem_id = await db_manager.create_problem(
            title="Refinement Test Problem",
            description="How can we reduce carbon emissions?",
            initial_layer="deci"
        )
        
        # Process problem with refinement
        problem_context = await orchestrator.process_problem_continuously(
            problem_id=problem_id,
            title="Refinement Test Problem",
            description="How can we reduce carbon emissions?",
            max_iterations=20
        )
        
        assert problem_context is not None
        
        # Check if refinement occurred
        if len(problem_context.refinements) > 0:
            refinement = problem_context.refinements[0]
            assert refinement.from_layer is not None
            assert refinement.to_layer is not None
            assert refinement.rationale is not None
            assert refinement.refined_question is not None


class TestAPIIntegration(IntegrationTestBase):
    """Test API integration functionality."""
    
    @pytest.fixture
    def test_client(self):
        """Create test client for API testing."""
        return TestClient(secure_app)
    
    @pytest.fixture
    def test_monitoring_client(self):
        """Create test client for monitoring API testing."""
        return TestClient(monitoring_app)
    
    @pytest.mark.asyncio
    async def test_secure_api_flow(self, test_client, test_security_manager):
        """Test secure API flow."""
        security_manager, user = test_security_manager
        
        # Test user registration
        user_data = {
            "username": "apitestuser",
            "email": "apitest@example.com",
            "password": "ApiTestPassword123!",
            "role": "user"
        }
        
        response = test_client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "apitestuser"
        assert data["email"] == "apitest@example.com"
        assert data["role"] == "user"
        
        # Test user login
        login_data = {
            "username": "apitestuser",
            "password": "ApiTestPassword123!"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        
        token = data["access_token"]
        
        # Test protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/problems", headers=headers)
        assert response.status_code == 200
        
        # Test problem submission
        problem_data = {
            "title": "API Test Problem",
            "description": "This is a test problem for API integration testing",
            "initial_layer": "deci",
            "max_iterations": 50
        }
        
        response = test_client.post("/problems", json=problem_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "problem_id" in data
        assert data["status"] == "accepted"
        
        problem_id = data["problem_id"]
        
        # Test problem status
        response = test_client.get(f"/problems/{problem_id}/status", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["problem_id"] == problem_id
        assert "status" in data
    
    @pytest.mark.asyncio
    async def test_monitoring_api_flow(self, test_monitoring_client):
        """Test monitoring API flow."""
        # Test health check
        response = test_monitoring_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "uptime_seconds" in data
        
        # Test metrics endpoint
        response = test_monitoring_client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        
        # Test system info (requires authentication)
        response = test_monitoring_client.get("/system/info")
        assert response.status_code == 401  # Unauthorized


class TestEndToEndIntegration(IntegrationTestBase):
    """Test end-to-end integration functionality."""
    
    @pytest.mark.asyncio
    async def test_complete_problem_solving_workflow(
        self, 
        test_database, 
        test_ai_manager, 
        test_security_manager,
        test_monitoring
    ):
        """Test complete problem solving workflow from submission to resolution."""
        db_manager = test_database
        ai_manager = test_ai_manager
        security_manager, user = test_security_manager
        metrics_collector, sentry, health_checker = test_monitoring
        
        # Step 1: User authentication
        authenticated_user = await security_manager.authenticate_user(
            "testuser",
            "TestPassword123!"
        )
        assert authenticated_user is not None
        
        # Step 2: Problem submission
        problem_id = await db_manager.create_problem(
            title="End-to-End Test Problem",
            description="How can we reduce global carbon emissions?",
            initial_layer="deci"
        )
        assert problem_id is not None
        
        # Step 3: Problem processing
        orchestrator = LayerOrchestrator()
        problem_context = await orchestrator.process_problem_continuously(
            problem_id=problem_id,
            title="End-to-End Test Problem",
            description="How can we reduce global carbon emissions?",
            max_iterations=5
        )
        
        assert problem_context is not None
        assert problem_context.problem_id == problem_id
        
        # Step 4: Verify processing results
        assert len(problem_context.layer_runs) > 0
        assert problem_context.metadata is not None
        
        # Step 5: Check database persistence
        problem = await db_manager.get_problem(problem_id)
        assert problem is not None
        
        genealogy = await db_manager.get_problem_genealogy(problem_id)
        assert genealogy is not None
        assert len(genealogy["layer_runs"]) > 0
        
        # Step 6: Verify monitoring
        system_health = await health_checker.run_all_checks()
        assert system_health is not None
        assert system_health.status is not None
        
        # Step 7: Check metrics
        metrics_summary = metrics_collector.get_metrics_summary()
        assert metrics_summary is not None
        assert "performance_metrics" in metrics_summary
        
        # Step 8: Verify error handling
        error_analytics = metrics_collector.get_metrics_summary()
        assert error_analytics is not None
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(
        self, 
        test_database, 
        test_ai_manager, 
        test_security_manager,
        test_error_handler
    ):
        """Test error recovery workflow."""
        db_manager = test_database
        ai_manager = test_ai_manager
        security_manager, user = test_security_manager
        error_handler = test_error_handler
        
        # Simulate AI service failure
        ai_manager.providers["openai"].generate_response = AsyncMock(
            side_effect=Exception("AI service temporarily unavailable")
        )
        
        # Create problem
        problem_id = await db_manager.create_problem(
            title="Error Recovery Test Problem",
            description="How can we reduce carbon emissions?",
            initial_layer="deci"
        )
        
        # Process problem with error handling
        orchestrator = LayerOrchestrator()
        problem_context = await orchestrator.process_problem_continuously(
            problem_id=problem_id,
            title="Error Recovery Test Problem",
            description="How can we reduce carbon emissions?",
            max_iterations=3
        )
        
        # Should handle errors gracefully
        assert problem_context is not None
        assert problem_context.metadata is not None
        
        # Check error handling
        error_analytics = error_handler.get_error_analytics()
        assert error_analytics is not None
        assert "total_errors" in error_analytics
    
    @pytest.mark.asyncio
    async def test_performance_under_load(
        self, 
        test_database, 
        test_ai_manager, 
        test_security_manager
    ):
        """Test performance under load."""
        db_manager = test_database
        ai_manager = test_ai_manager
        security_manager, user = test_security_manager
        
        # Create multiple problems concurrently
        tasks = []
        for i in range(5):
            task = db_manager.create_problem(
                title=f"Load Test Problem {i}",
                description=f"Load test description {i}",
                initial_layer="deci"
            )
            tasks.append(task)
        
        problem_ids = await asyncio.gather(*tasks)
        assert len(problem_ids) == 5
        
        # Process problems concurrently
        orchestrator = LayerOrchestrator()
        processing_tasks = []
        
        for problem_id in problem_ids:
            task = orchestrator.process_problem_continuously(
                problem_id=problem_id,
                title=f"Load Test Problem",
                description="Load test description",
                max_iterations=2
            )
            processing_tasks.append(task)
        
        # Wait for all processing to complete
        results = await asyncio.gather(*processing_tasks, return_exceptions=True)
        
        # Verify all problems were processed
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) > 0
        
        # Check that errors were handled gracefully
        error_count = len([r for r in results if isinstance(r, Exception)])
        assert error_count < len(results)  # Some should succeed


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
