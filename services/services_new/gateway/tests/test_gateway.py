#!/usr/bin/env python3
"""
🧪 Gateway Service Tests
Test the Cosmic Council Gateway Service functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone
import uuid

# Import the modules to test
from services.gateway.main import app, CycleRequest, CycleResponse
from services.gateway.routes.cycle import CycleStartRequest, CycleStartResponse
from services.gateway.routes.evaluate import PolicyEvaluationRequest, PolicyEvaluationResponse
from services.gateway.routes.simulate import SimulationRequest, SimulationResponse
from services.gateway.routes.explain import ExplanationRequest, ExplanationResponse

class TestGatewayService:
    """Test Gateway Service functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        return TestClient(app)
    
    @pytest.fixture
    def sample_cycle_request(self):
        """Create sample cycle request"""
        return CycleStartRequest(
            objective_ref="test_objective_001",
            problem_title="Test Problem",
            problem_description="A test problem for unit testing",
            complexity="moderate",
            metadata={"test": True}
        )
    
    @pytest.fixture
    def sample_policy_request(self):
        """Create sample policy evaluation request"""
        return PolicyEvaluationRequest(
            action="start_cycle",
            resource="cycles",
            subject="test_user",
            context={"test": True}
        )
    
    @pytest.fixture
    def sample_simulation_request(self):
        """Create sample simulation request"""
        return SimulationRequest(
            objective_ref="test_simulation_001",
            problem_title="Test Simulation Problem",
            problem_description="A test problem for simulation",
            complexity="moderate",
            simulation_type="full",
            dry_run=True
        )
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data
    
    @pytest.mark.asyncio
    async def test_start_cycle_success(self, client, sample_cycle_request):
        """Test successful cycle start"""
        with patch('services.gateway.main.get_hexagon') as mock_hexagon, \
             patch('services.gateway.main.get_db_manager') as mock_db:
            
            # Mock hexagon response
            mock_hexagon.return_value.process_cycle = AsyncMock(return_value=Mock(
                cycle_id="test_cycle_123",
                status="active",
                timestamp=datetime.now(timezone.utc)
            ))
            
            # Mock database
            mock_db.return_value.execute_query = AsyncMock()
            mock_db.return_value.execute_command = AsyncMock()
            
            response = client.post("/v1/cycles", json=sample_cycle_request.dict())
            
            assert response.status_code == 200
            data = response.json()
            assert data["cycle_id"] == "test_cycle_123"
            assert data["status"] == "active"
            assert data["next_stage"] == "red_research"
    
    @pytest.mark.asyncio
    async def test_start_cycle_failure(self, client, sample_cycle_request):
        """Test cycle start failure"""
        with patch('services.gateway.main.get_hexagon') as mock_hexagon:
            # Mock hexagon failure
            mock_hexagon.return_value.process_cycle = AsyncMock(side_effect=Exception("Hexagon error"))
            
            response = client.post("/v1/cycles", json=sample_cycle_request.dict())
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
            assert "Failed to start cycle" in data["error"]
    
    @pytest.mark.asyncio
    async def test_get_cycle_status_success(self, client):
        """Test successful cycle status retrieval"""
        cycle_id = "test_cycle_123"
        
        with patch('services.gateway.main.get_hexagon') as mock_hexagon, \
             patch('services.gateway.main.get_db_manager') as mock_db:
            
            # Mock database response
            mock_db.return_value.execute_query = AsyncMock(return_value=[
                {
                    "id": cycle_id,
                    "objective_ref": "test_objective",
                    "status": "active",
                    "started_at": datetime.now(timezone.utc),
                    "completed_at": None,
                    "total_stages": 6,
                    "completed_stages": 2
                }
            ])
            
            response = client.get(f"/v1/cycles/{cycle_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["cycle_id"] == cycle_id
            assert data["status"] == "active"
            assert data["progress_percentage"] == 33.33  # 2/6 * 100
    
    def test_get_cycle_status_not_found(self, client):
        """Test cycle status retrieval for non-existent cycle"""
        cycle_id = "non_existent_cycle"
        
        with patch('services.gateway.main.get_db_manager') as mock_db:
            # Mock empty database response
            mock_db.return_value.execute_query = AsyncMock(return_value=[])
            
            response = client.get(f"/v1/cycles/{cycle_id}")
            
            assert response.status_code == 404
            data = response.json()
            assert "Cycle not found" in data["error"]
    
    @pytest.mark.asyncio
    async def test_policy_evaluation_success(self, client, sample_policy_request):
        """Test successful policy evaluation"""
        with patch('services.gateway.main.get_db_manager') as mock_db:
            # Mock database
            mock_db.return_value.execute_command = AsyncMock()
            
            response = client.post("/v1/policies/evaluate", json=sample_policy_request.dict())
            
            assert response.status_code == 200
            data = response.json()
            assert data["allowed"] is True
            assert "Policy evaluation passed" in data["reason"]
            assert "user_authenticated" in data["conditions"]
    
    @pytest.mark.asyncio
    async def test_policy_evaluation_denied(self, client):
        """Test policy evaluation denial"""
        policy_request = PolicyEvaluationRequest(
            action="unauthorized_action",
            resource="sensitive_resource",
            subject="regular_user",
            context={}
        )
        
        with patch('services.gateway.main.get_db_manager') as mock_db:
            # Mock database
            mock_db.return_value.execute_command = AsyncMock()
            
            response = client.post("/v1/policies/evaluate", json=policy_request.dict())
            
            assert response.status_code == 200
            data = response.json()
            assert data["allowed"] is False
            assert "Action not permitted" in data["reason"]
    
    @pytest.mark.asyncio
    async def test_simulation_success(self, client, sample_simulation_request):
        """Test successful simulation"""
        with patch('services.gateway.main.get_hexagon') as mock_hexagon, \
             patch('services.gateway.main.get_db_manager') as mock_db:
            
            # Mock hexagon
            mock_hexagon.return_value = Mock()
            
            # Mock database
            mock_db.return_value.execute_query = AsyncMock()
            mock_db.return_value.execute_command = AsyncMock()
            
            response = client.post("/v1/simulate/cycle", json=sample_simulation_request.dict())
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"  # Dry run should complete immediately
            assert data["simulation_type"] == "full"
            assert "results" in data
    
    @pytest.mark.asyncio
    async def test_explain_entity_success(self, client):
        """Test successful entity explanation"""
        entity_id = "test_entity_123"
        
        with patch('services.gateway.main.get_db_manager') as mock_db:
            # Mock database response
            mock_db.return_value.execute_query = AsyncMock(return_value=[
                {
                    "id": entity_id,
                    "objective_ref": "test_objective",
                    "status": "completed",
                    "started_at": datetime.now(timezone.utc),
                    "completed_at": datetime.now(timezone.utc)
                }
            ])
            
            response = client.get(f"/v1/explain/{entity_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["entity_id"] == entity_id
            assert data["entity_type"] == "cycle"
            assert "summary" in data
            assert "reasoning_chain" in data
    
    def test_explain_entity_not_found(self, client):
        """Test entity explanation for non-existent entity"""
        entity_id = "non_existent_entity"
        
        with patch('services.gateway.main.get_db_manager') as mock_db:
            # Mock empty database response
            mock_db.return_value.execute_query = AsyncMock(return_value=[])
            
            response = client.get(f"/v1/explain/{entity_id}")
            
            assert response.status_code == 404
            data = response.json()
            assert "not found" in data["error"]


class TestCycleRoutes:
    """Test Cycle Management Routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client for cycle routes"""
        from fastapi.testclient import TestClient
        from services.gateway.routes.cycle import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    def test_estimate_cycle_duration(self):
        """Test cycle duration estimation"""
        from services.gateway.routes.cycle import estimate_cycle_duration
        from src.core.types import ProblemComplexity
        
        # Test different complexity levels
        assert estimate_cycle_duration(ProblemComplexity.SIMPLE) == 30
        assert estimate_cycle_duration(ProblemComplexity.MODERATE) == 60
        assert estimate_cycle_duration(ProblemComplexity.COMPLEX) == 120
        assert estimate_cycle_duration(ProblemComplexity.SYSTEMIC) == 240
    
    @pytest.mark.asyncio
    async def test_cancel_cycle_success(self, client):
        """Test successful cycle cancellation"""
        cycle_id = "test_cycle_123"
        cancel_request = {
            "reason": "Test cancellation",
            "force": False
        }
        
        with patch('services.gateway.routes.cycle.get_hexagon') as mock_hexagon, \
             patch('services.gateway.routes.cycle.get_database_manager') as mock_db:
            
            # Mock database responses
            mock_db.return_value.execute_query = AsyncMock(return_value=[
                {"status": "active"}
            ])
            mock_db.return_value.execute_command = AsyncMock(return_value="UPDATE 1")
            
            response = client.post(f"/v1/cycles/{cycle_id}/cancel", json=cancel_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["cycle_id"] == cycle_id
            assert data["status"] == "cancelled"
            assert data["reason"] == "Test cancellation"
    
    @pytest.mark.asyncio
    async def test_pause_cycle_success(self, client):
        """Test successful cycle pause"""
        cycle_id = "test_cycle_123"
        pause_request = {
            "reason": "Test pause",
            "estimated_resume_time": None
        }
        
        with patch('services.gateway.routes.cycle.get_database_manager') as mock_db:
            # Mock database responses
            mock_db.return_value.execute_query = AsyncMock(return_value=[
                {"status": "active"}
            ])
            mock_db.return_value.execute_command = AsyncMock(return_value="UPDATE 1")
            
            response = client.post(f"/v1/cycles/{cycle_id}/pause", json=pause_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["cycle_id"] == cycle_id
            assert data["status"] == "paused"
            assert data["reason"] == "Test pause"


class TestPolicyRoutes:
    """Test Policy Evaluation Routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client for policy routes"""
        from fastapi.testclient import TestClient
        from services.gateway.routes.evaluate import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_get_policy_rules(self, client):
        """Test getting policy rules"""
        with patch('services.gateway.routes.evaluate.get_database_manager') as mock_db:
            # Mock database response
            mock_db.return_value.execute_query = AsyncMock(return_value=[
                {
                    "id": "rule_1",
                    "name": "Test Rule",
                    "description": "A test policy rule",
                    "action": "start_cycle",
                    "resource_pattern": "*",
                    "conditions": ["user_authenticated"],
                    "priority": 1,
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc)
                }
            ])
            
            response = client.get("/v1/policies/rules")
            
            assert response.status_code == 200
            data = response.json()
            assert "rules" in data
            assert len(data["rules"]) == 1
            assert data["rules"][0]["name"] == "Test Rule"
    
    @pytest.mark.asyncio
    async def test_create_policy_rule(self, client):
        """Test creating a policy rule"""
        rule_request = {
            "name": "New Test Rule",
            "description": "A new test policy rule",
            "conditions": ["user_authenticated", "admin_only"],
            "action": "create_cycle",
            "priority": 5
        }
        
        with patch('services.gateway.routes.evaluate.get_database_manager') as mock_db:
            # Mock database response
            mock_db.return_value.execute_query = AsyncMock(return_value=[
                {"id": "new_rule_123"}
            ])
            mock_db.return_value.execute_command = AsyncMock()
            
            response = client.post("/v1/policies/rules", json=rule_request)
            
            assert response.status_code == 200
            data = response.json()
            assert "rule_id" in data
            assert data["rule_id"] == "new_rule_123"


class TestSimulationRoutes:
    """Test Simulation Routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client for simulation routes"""
        from fastapi.testclient import TestClient
        from services.gateway.routes.simulate import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    def test_simulate_stage_duration(self):
        """Test stage duration simulation"""
        from services.gateway.routes.simulate import simulate_stage_duration
        from src.core.types import ProblemComplexity
        
        # Test different stages and complexities
        duration = simulate_stage_duration("red_research", ProblemComplexity.MODERATE)
        assert duration == 30.0  # 30 * 1.0
        
        duration = simulate_stage_duration("yellow_development", ProblemComplexity.COMPLEX)
        assert duration == 52.5  # 35 * 1.5
    
    def test_simulate_confidence_score(self):
        """Test confidence score simulation"""
        from services.gateway.routes.simulate import simulate_confidence_score
        
        # Test different stages
        confidence = simulate_confidence_score("red_research")
        assert confidence == 0.75
        
        confidence = simulate_confidence_score("purple_support")
        assert confidence == 0.82
    
    @pytest.mark.asyncio
    async def test_load_test_success(self, client):
        """Test successful load test"""
        load_test_request = {
            "concurrent_cycles": 10,
            "cycle_duration": 120,
            "test_duration": 300,
            "complexity_distribution": {
                "simple": 0.3,
                "moderate": 0.4,
                "complex": 0.2,
                "systemic": 0.1
            }
        }
        
        with patch('services.gateway.routes.simulate.get_hexagon') as mock_hexagon, \
             patch('services.gateway.routes.simulate.get_database_manager') as mock_db:
            
            # Mock hexagon and database
            mock_hexagon.return_value = Mock()
            mock_db.return_value.execute_command = AsyncMock()
            
            response = client.post("/v1/simulate/load-test", json=load_test_request)
            
            assert response.status_code == 200
            data = response.json()
            assert "test_id" in data
            assert data["concurrent_cycles"] == 10
            assert data["test_duration"] == 300


class TestExplainabilityRoutes:
    """Test Explainability Routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client for explainability routes"""
        from fastapi.testclient import TestClient
        from services.gateway.routes.explain import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_get_decision_trace(self, client):
        """Test getting decision trace"""
        entity_id = "test_entity_123"
        
        with patch('services.gateway.routes.explain.get_database_manager') as mock_db:
            # Mock database response
            mock_db.return_value.execute_query = AsyncMock(return_value=[
                {
                    "id": "decision_1",
                    "timestamp": datetime.now(timezone.utc),
                    "action": "create",
                    "details_json": {
                        "criteria": ["user_authenticated"],
                        "rationale": "User has proper permissions",
                        "confidence_score": 0.85
                    },
                    "cycle_id": "cycle_123",
                    "stage_code": "red_research",
                    "objective_ref": "test_objective"
                }
            ])
            
            response = client.get(f"/v1/explain/{entity_id}/decisions")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["decision_id"] == "decision_1"
            assert data[0]["decision_type"] == "create"
            assert data[0]["confidence_score"] == 0.85
    
    @pytest.mark.asyncio
    async def test_generate_transparency_report(self, client):
        """Test generating transparency report"""
        with patch('services.gateway.routes.explain.get_database_manager') as mock_db:
            # Mock database
            mock_db.return_value.execute_query = AsyncMock(return_value=[])
            
            response = client.post(
                "/v1/explain/transparency-report",
                params={
                    "scope": "cycle",
                    "scope_id": "test_cycle_123",
                    "period_days": 30
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "report_id" in data
            assert data["scope"] == "cycle"
            assert data["scope_id"] == "test_cycle_123"
            assert data["total_decisions"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
