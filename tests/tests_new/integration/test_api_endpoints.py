"""
Integration tests for API endpoints
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.api.main import app


class TestAPIEndpoints:
    """Test API endpoints integration."""
    
    @pytest.fixture
    def client(self):
        """Provide a test client."""
        return TestClient(app)
    
    @pytest.fixture
    async def async_client(self):
        """Provide an async test client."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_create_problem(self, client):
        """Test problem creation endpoint."""
        problem_data = {
            "title": "API Test Problem",
            "description": "A problem for API testing",
            "complexity": "moderate",
            "domain": "Test",
            "stakeholders": ["Test Stakeholder"],
            "constraints": {"budget": "$5K"},
            "success_criteria": ["Test criteria"]
        }
        
        response = client.post("/api/v1/problems", json=problem_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "API Test Problem"
        assert "problem_id" in data
        assert data["status"] == "pending"
        assert data["complexity"] == "moderate"
        assert data["domain"] == "Test"
    
    def test_get_problem(self, client):
        """Test problem retrieval endpoint."""
        # First create a problem
        problem_data = {
            "title": "Get Test Problem",
            "description": "A problem for get testing",
            "complexity": "simple",
            "domain": "Test"
        }
        
        create_response = client.post("/api/v1/problems", json=problem_data)
        problem_id = create_response.json()["problem_id"]
        
        # Then retrieve it
        response = client.get(f"/api/v1/problems/{problem_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["problem_id"] == problem_id
        assert data["title"] == "Get Test Problem"
        assert data["description"] == "A problem for get testing"
        assert data["complexity"] == "simple"
        assert data["domain"] == "Test"
    
    def test_list_problems(self, client):
        """Test problem listing endpoint."""
        # Create multiple problems
        for i in range(3):
            problem_data = {
                "title": f"List Test Problem {i}",
                "description": f"A problem for list testing {i}",
                "complexity": "simple",
                "domain": "Test"
            }
            client.post("/api/v1/problems", json=problem_data)
        
        # List problems
        response = client.get("/api/v1/problems?limit=10&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert "problems" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert len(data["problems"]) >= 3
        assert data["total"] >= 3
    
    def test_update_problem(self, client):
        """Test problem update endpoint."""
        # Create a problem
        problem_data = {
            "title": "Update Test Problem",
            "description": "A problem for update testing",
            "complexity": "simple",
            "domain": "Test"
        }
        
        create_response = client.post("/api/v1/problems", json=problem_data)
        problem_id = create_response.json()["problem_id"]
        
        # Update the problem
        update_data = {
            "title": "Updated Test Problem",
            "description": "Updated description"
        }
        
        response = client.put(f"/api/v1/problems/{problem_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Test Problem"
        assert data["description"] == "Updated description"
        assert data["problem_id"] == problem_id
    
    def test_delete_problem(self, client):
        """Test problem deletion endpoint."""
        # Create a problem
        problem_data = {
            "title": "Delete Test Problem",
            "description": "A problem for delete testing",
            "complexity": "simple",
            "domain": "Test"
        }
        
        create_response = client.post("/api/v1/problems", json=problem_data)
        problem_id = create_response.json()["problem_id"]
        
        # Delete the problem
        response = client.delete(f"/api/v1/problems/{problem_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Problem deleted successfully"
        
        # Verify problem is deleted
        get_response = client.get(f"/api/v1/problems/{problem_id}")
        assert get_response.status_code == 404
    
    def test_create_cycle(self, client):
        """Test cycle creation endpoint."""
        # First create a problem
        problem_data = {
            "title": "Cycle Test Problem",
            "description": "A problem for cycle testing",
            "complexity": "moderate",
            "domain": "Test"
        }
        
        problem_response = client.post("/api/v1/problems", json=problem_data)
        problem_id = problem_response.json()["problem_id"]
        
        # Create a cycle
        cycle_data = {
            "problem_id": problem_id,
            "objective": "Test cycle objective",
            "priority": 3,
            "ai_enhanced": False
        }
        
        response = client.post("/api/v1/cycles", json=cycle_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["problem_id"] == problem_id
        assert data["objective"] == "Test cycle objective"
        assert data["priority"] == 3
        assert data["status"] == "pending"
        assert "cycle_id" in data
    
    def test_execute_cycle(self, client):
        """Test cycle execution endpoint."""
        # Create a problem and cycle
        problem_data = {
            "title": "Execute Test Problem",
            "description": "A problem for execute testing",
            "complexity": "simple",
            "domain": "Test"
        }
        
        problem_response = client.post("/api/v1/problems", json=problem_data)
        problem_id = problem_response.json()["problem_id"]
        
        cycle_data = {
            "problem_id": problem_id,
            "objective": "Test execute objective",
            "priority": 3
        }
        
        cycle_response = client.post("/api/v1/cycles", json=cycle_data)
        cycle_id = cycle_response.json()["cycle_id"]
        
        # Execute the cycle
        response = client.post(f"/api/v1/cycles/{cycle_id}/execute")
        
        assert response.status_code == 200
        data = response.json()
        assert data["cycle_id"] == cycle_id
        assert data["status"] in ["running", "completed"]
        assert "started_at" in data
    
    def test_get_cycle_status(self, client):
        """Test cycle status retrieval endpoint."""
        # Create a problem and cycle
        problem_data = {
            "title": "Status Test Problem",
            "description": "A problem for status testing",
            "complexity": "simple",
            "domain": "Test"
        }
        
        problem_response = client.post("/api/v1/problems", json=problem_data)
        problem_id = problem_response.json()["problem_id"]
        
        cycle_data = {
            "problem_id": problem_id,
            "objective": "Test status objective",
            "priority": 3
        }
        
        cycle_response = client.post("/api/v1/cycles", json=cycle_data)
        cycle_id = cycle_response.json()["cycle_id"]
        
        # Get cycle status
        response = client.get(f"/api/v1/cycles/{cycle_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["cycle_id"] == cycle_id
        assert data["problem_id"] == problem_id
        assert data["objective"] == "Test status objective"
        assert data["priority"] == 3
        assert "status" in data
        assert "created_at" in data
    
    def test_list_cycles(self, client):
        """Test cycle listing endpoint."""
        # Create a problem and multiple cycles
        problem_data = {
            "title": "List Cycle Test Problem",
            "description": "A problem for list cycle testing",
            "complexity": "simple",
            "domain": "Test"
        }
        
        problem_response = client.post("/api/v1/problems", json=problem_data)
        problem_id = problem_response.json()["problem_id"]
        
        for i in range(3):
            cycle_data = {
                "problem_id": problem_id,
                "objective": f"Test list cycle objective {i}",
                "priority": 3
            }
            client.post("/api/v1/cycles", json=cycle_data)
        
        # List cycles
        response = client.get(f"/api/v1/cycles?problem_id={problem_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "cycles" in data
        assert "total" in data
        assert len(data["cycles"]) >= 3
        assert data["total"] >= 3
    
    def test_get_solutions(self, client):
        """Test solution retrieval endpoint."""
        # Create a problem and cycle
        problem_data = {
            "title": "Solution Test Problem",
            "description": "A problem for solution testing",
            "complexity": "simple",
            "domain": "Test"
        }
        
        problem_response = client.post("/api/v1/problems", json=problem_data)
        problem_id = problem_response.json()["problem_id"]
        
        cycle_data = {
            "problem_id": problem_id,
            "objective": "Test solution objective",
            "priority": 3
        }
        
        cycle_response = client.post("/api/v1/cycles", json=cycle_data)
        cycle_id = cycle_response.json()["cycle_id"]
        
        # Get solutions
        response = client.get(f"/api/v1/solutions?cycle_id={cycle_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "solutions" in data
        assert "total" in data
        assert isinstance(data["solutions"], list)
    
    def test_create_solution(self, client):
        """Test solution creation endpoint."""
        # Create a problem and cycle
        problem_data = {
            "title": "Create Solution Test Problem",
            "description": "A problem for create solution testing",
            "complexity": "simple",
            "domain": "Test"
        }
        
        problem_response = client.post("/api/v1/problems", json=problem_data)
        problem_id = problem_response.json()["problem_id"]
        
        cycle_data = {
            "problem_id": problem_id,
            "objective": "Test create solution objective",
            "priority": 3
        }
        
        cycle_response = client.post("/api/v1/cycles", json=cycle_data)
        cycle_id = cycle_response.json()["cycle_id"]
        
        # Create a solution
        solution_data = {
            "cycle_id": cycle_id,
            "title": "Test Solution",
            "description": "A test solution",
            "components": [
                {
                    "name": "Component 1",
                    "description": "First component",
                    "priority": 1,
                    "estimated_effort": "1 week"
                }
            ]
        }
        
        response = client.post("/api/v1/solutions", json=solution_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["cycle_id"] == cycle_id
        assert data["title"] == "Test Solution"
        assert data["description"] == "A test solution"
        assert "solution_id" in data
        assert len(data["components"]) == 1
    
    def test_get_analytics(self, client):
        """Test analytics endpoints."""
        # Test problem analytics
        response = client.get("/api/v1/analytics/problems")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_problems" in data
        assert "by_complexity" in data
        assert "by_domain" in data
        assert "by_status" in data
        assert "success_rate" in data
        
        # Test cycle analytics
        response = client.get("/api/v1/analytics/cycles")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_cycles" in data
        assert "by_status" in data
        assert "average_duration" in data
        assert "average_confidence" in data
        
        # Test solution analytics
        response = client.get("/api/v1/analytics/solutions")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_solutions" in data
        assert "by_status" in data
        assert "average_confidence" in data
        assert "average_feasibility" in data
    
    def test_get_enterprises(self, client):
        """Test enterprise information endpoint."""
        response = client.get("/api/v1/enterprises")
        
        assert response.status_code == 200
        data = response.json()
        assert "enterprises" in data
        assert len(data["enterprises"]) == 6
        
        # Check enterprise structure
        for enterprise in data["enterprises"]:
            assert "enterprise_id" in enterprise
            assert "name" in enterprise
            assert "role" in enterprise
            assert "description" in enterprise
            assert "color" in enterprise
            assert "status" in enterprise
            assert "capabilities" in enterprise
    
    def test_get_enterprise_performance(self, client):
        """Test enterprise performance endpoint."""
        response = client.get("/api/v1/enterprises/red_owl/performance")
        
        assert response.status_code == 200
        data = response.json()
        assert "enterprise_id" in data
        assert "name" in data
        assert "performance_metrics" in data
        assert "recent_activity" in data
        
        # Check performance metrics structure
        metrics = data["performance_metrics"]
        assert "cycles_processed" in metrics
        assert "success_rate" in metrics
        assert "average_confidence" in metrics
        assert "average_processing_time" in metrics
        assert "specialization_score" in metrics
        assert "collaboration_score" in metrics
    
    def test_api_error_handling(self, client):
        """Test API error handling."""
        # Test 404 for non-existent problem
        response = client.get("/api/v1/problems/non-existent-id")
        assert response.status_code == 404
        
        # Test 400 for invalid problem data
        invalid_data = {
            "title": "",  # Empty title should be invalid
            "description": "Test description",
            "complexity": "invalid_complexity",
            "domain": "Test"
        }
        
        response = client.post("/api/v1/problems", json=invalid_data)
        assert response.status_code == 400
        
        # Test 404 for non-existent cycle
        response = client.get("/api/v1/cycles/non-existent-id")
        assert response.status_code == 404
    
    def test_api_validation(self, client):
        """Test API input validation."""
        # Test missing required fields
        incomplete_data = {
            "title": "Test Problem"
            # Missing required fields
        }
        
        response = client.post("/api/v1/problems", json=incomplete_data)
        assert response.status_code == 422  # Validation error
        
        # Test invalid data types
        invalid_types_data = {
            "title": "Test Problem",
            "description": "Test description",
            "complexity": "moderate",
            "domain": "Test",
            "stakeholders": "not_a_list",  # Should be a list
            "constraints": "not_a_dict",   # Should be a dict
            "success_criteria": "not_a_list"  # Should be a list
        }
        
        response = client.post("/api/v1/problems", json=invalid_types_data)
        assert response.status_code == 422  # Validation error
    
    def test_api_pagination(self, client):
        """Test API pagination."""
        # Create multiple problems
        for i in range(15):
            problem_data = {
                "title": f"Pagination Test Problem {i}",
                "description": f"A problem for pagination testing {i}",
                "complexity": "simple",
                "domain": "Test"
            }
            client.post("/api/v1/problems", json=problem_data)
        
        # Test pagination
        response = client.get("/api/v1/problems?limit=5&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["problems"]) == 5
        assert data["limit"] == 5
        assert data["offset"] == 0
        assert data["total"] >= 15
        
        # Test second page
        response = client.get("/api/v1/problems?limit=5&offset=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["problems"]) == 5
        assert data["limit"] == 5
        assert data["offset"] == 5
    
    def test_api_filtering(self, client):
        """Test API filtering."""
        # Create problems with different complexities
        complexities = ["simple", "moderate", "complex"]
        for complexity in complexities:
            for i in range(3):
                problem_data = {
                    "title": f"Filter Test Problem {complexity} {i}",
                    "description": f"A {complexity} problem for filter testing {i}",
                    "complexity": complexity,
                    "domain": "Test"
                }
                client.post("/api/v1/problems", json=problem_data)
        
        # Test filtering by complexity
        response = client.get("/api/v1/problems?complexity=moderate")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["problems"]) >= 3
        for problem in data["problems"]:
            assert problem["complexity"] == "moderate"
        
        # Test filtering by domain
        response = client.get("/api/v1/problems?domain=Test")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["problems"]) >= 9
        for problem in data["problems"]:
            assert problem["domain"] == "Test"
    
    def test_api_sorting(self, client):
        """Test API sorting."""
        # Create problems with different titles
        titles = ["Alpha Problem", "Beta Problem", "Gamma Problem"]
        for title in titles:
            problem_data = {
                "title": title,
                "description": f"A problem with title {title}",
                "complexity": "simple",
                "domain": "Test"
            }
            client.post("/api/v1/problems", json=problem_data)
        
        # Test sorting by title
        response = client.get("/api/v1/problems?sort_by=title&sort_order=asc")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["problems"]) >= 3
        
        # Check that problems are sorted
        problem_titles = [p["title"] for p in data["problems"]]
        assert problem_titles == sorted(problem_titles)
    
    @pytest.mark.asyncio
    async def test_async_endpoints(self, async_client):
        """Test async endpoint functionality."""
        # Test async problem creation
        problem_data = {
            "title": "Async Test Problem",
            "description": "A problem for async testing",
            "complexity": "simple",
            "domain": "Test"
        }
        
        response = await async_client.post("/api/v1/problems", json=problem_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Async Test Problem"
        assert "problem_id" in data
    
    def test_api_rate_limiting(self, client):
        """Test API rate limiting."""
        # Make many requests quickly
        for i in range(100):
            response = client.get("/api/v1/problems")
            if response.status_code == 429:
                break
        
        # Should eventually hit rate limit
        assert response.status_code == 429
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
    
    def test_api_cors(self, client):
        """Test API CORS headers."""
        response = client.options("/api/v1/problems")
        
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers
    
    def test_api_content_type(self, client):
        """Test API content type handling."""
        # Test JSON content type
        problem_data = {
            "title": "Content Type Test Problem",
            "description": "A problem for content type testing",
            "complexity": "simple",
            "domain": "Test"
        }
        
        response = client.post(
            "/api/v1/problems",
            json=problem_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201
        assert response.headers["content-type"] == "application/json"
        
        # Test invalid content type
        response = client.post(
            "/api/v1/problems",
            data=problem_data,
            headers={"Content-Type": "text/plain"}
        )
        
        assert response.status_code == 422  # Validation error
