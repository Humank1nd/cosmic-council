"""
Integration tests for API endpoints
"""

import pytest
import asyncio
import json
import uuid
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import pytest_asyncio

from src.api.main import app


def _response_data(payload):
    if isinstance(payload, dict) and "data" in payload:
        return payload.get("data") or {}
    return payload if isinstance(payload, dict) else {}


class TestAPIEndpoints:
    """Test API endpoints integration."""
    
    @pytest.fixture
    def client(self):
        """Provide a test client."""
        return TestClient(app)
    
    @pytest_asyncio.fixture
    async def async_client(self):
        """Provide an async test client."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        payload = response.json()
        assert "timestamp" in payload
        if "success" in payload:
            assert payload["success"] in [True, False]
        data = _response_data(payload)
        assert data.get("overall_status") in ["healthy", "unhealthy"]
    
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

        assert response.status_code == 200
        payload = response.json()
        assert payload.get("success") is True
        data = _response_data(payload)
        assert data["title"] == "API Test Problem"
        assert "problem_id" in data
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
        problem_id = _response_data(create_response.json())["problem_id"]
        
        # Then retrieve it
        response = client.get(f"/api/v1/problems/{problem_id}")

        assert response.status_code == 200
        payload = response.json()
        data = _response_data(payload)
        problem = data.get("problem") or {}
        assert problem.get("id") == problem_id
        assert problem.get("title") == "Get Test Problem"
        assert problem.get("description") == "A problem for get testing"
        assert problem.get("complexity") == "simple"
        assert problem.get("domain") == "Test"
    
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
        payload = response.json()
        data = _response_data(payload)
        assert "problems" in data
        assert "total_count" in data
        assert "limit" in data
        assert "offset" in data
        assert len(data["problems"]) >= 3
        assert data["total_count"] >= 3
    
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
        problem_id = _response_data(create_response.json())["problem_id"]
        
        # Update the problem
        update_data = {
            "title": "Updated Test Problem",
            "description": "Updated description"
        }
        
        response = client.put(f"/api/v1/problems/{problem_id}", json=update_data)
        
        assert response.status_code == 200
        payload = response.json()
        data = _response_data(payload)
        assert data["title"] == "Updated Test Problem"
        assert data["problem_id"] == problem_id
    
    def test_delete_problem(self, client):
        """Test problem deletion endpoint."""
        pytest.skip("Delete endpoint is not implemented in core API")
    
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
        problem_id = _response_data(problem_response.json())["problem_id"]

        # Create a cycle
        cycle_data = {
            "problem_id": problem_id,
            "cycle_number": 1,
            "max_iterations": 2
        }

        response = client.post("/api/v1/cycles", json=cycle_data)

        assert response.status_code == 200
        payload = response.json()
        data = _response_data(payload)
        assert data["problem_id"] == problem_id
        assert data["cycle_number"] == 1
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
        problem_id = _response_data(problem_response.json())["problem_id"]
        
        cycle_data = {
            "problem_id": problem_id,
            "cycle_number": 1,
            "max_iterations": 1
        }
        
        cycle_response = client.post("/api/v1/cycles", json=cycle_data)
        cycle_id = _response_data(cycle_response.json())["cycle_id"]
        
        # Execute the cycle
        response = client.post(f"/api/v1/cycles/{cycle_id}/execute")
        
        assert response.status_code == 200
        payload = response.json()
        data = _response_data(payload)
        assert data["cycle_id"] == cycle_id
        assert data["status"] == "in_progress"
    
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
        problem_id = _response_data(problem_response.json())["problem_id"]

        cycle_data = {
            "problem_id": problem_id,
            "cycle_number": 1,
            "max_iterations": 1
        }

        cycle_response = client.post("/api/v1/cycles", json=cycle_data)
        cycle_id = _response_data(cycle_response.json())["cycle_id"]

        # Get cycle status
        response = client.get(f"/api/v1/cycles/{cycle_id}")

        assert response.status_code == 200
        payload = response.json()
        data = _response_data(payload)
        cycle = data.get("cycle") or {}
        assert cycle.get("id") == cycle_id
        assert cycle.get("problem_id") == problem_id
        assert "status" in cycle
    
    def test_list_cycles(self, client):
        """Test cycle listing endpoint."""
        pytest.skip("Cycle listing endpoint is not implemented in core API")
    
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
        problem_id = _response_data(problem_response.json())["problem_id"]

        cycle_data = {
            "problem_id": problem_id,
            "cycle_number": 1,
            "max_iterations": 1
        }

        cycle_response = client.post("/api/v1/cycles", json=cycle_data)
        cycle_id = _response_data(cycle_response.json())["cycle_id"]

        # Get solutions
        response = client.get(f"/api/v1/solutions?problem_id={problem_id}")

        assert response.status_code == 200
        payload = response.json()
        data = _response_data(payload)
        assert "solutions" in data
        assert "total_count" in data
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
        problem_id = _response_data(problem_response.json())["problem_id"]

        cycle_data = {
            "problem_id": problem_id,
            "cycle_number": 1,
            "max_iterations": 1
        }

        cycle_response = client.post("/api/v1/cycles", json=cycle_data)
        cycle_id = _response_data(cycle_response.json())["cycle_id"]

        # Create a solution
        solution_data = {
            "problem_id": problem_id,
            "cycle_id": cycle_id,
            "title": "Test Solution",
            "description": "A test solution",
            "approach": "Componentized delivery"
        }

        response = client.post("/api/v1/solutions", json=solution_data)

        assert response.status_code == 200
        payload = response.json()
        data = _response_data(payload)
        assert data["title"] == "Test Solution"
        assert "solution_id" in data

    def test_create_solution_with_cycle(self, client):
        """Test create-with-cycle solution endpoint."""
        problem_data = {
            "title": "Create With Cycle Test Problem",
            "description": "A problem for create-with-cycle testing",
            "complexity": "simple",
            "domain": "Test"
        }

        problem_response = client.post("/api/v1/problems", json=problem_data)
        problem_id = _response_data(problem_response.json())["problem_id"]

        request_data = {
            "problem_id": problem_id,
            "title": "Create With Cycle Solution",
            "description": "Solution created with automatic cycle",
            "approach": "Automated cycle execution",
            "max_iterations": 1
        }

        response = client.post("/api/v1/solutions/create-with-cycle", json=request_data)

        assert response.status_code == 200
        payload = response.json()
        assert payload.get("success") is True
        data = _response_data(payload)
        assert data.get("problem_id") == problem_id
        assert "solution_id" in data
        assert "cycle_id" in data
        assert data.get("status") == "draft"
        assert data.get("cycle_status") == "in_progress"
    
    def test_get_analytics(self, client):
        """Test analytics endpoints."""
        # Test problem analytics
        response = client.get("/api/v1/analytics/problems")
        
        assert response.status_code == 200
        payload = response.json()
        data = _response_data(payload)
        assert "total_problems" in data
        assert "by_complexity" in data
        assert "by_domain" in data
        assert "by_status" in data
        assert "success_rate" in data
        
        # Test cycle analytics
        response = client.get("/api/v1/analytics/cycles")
        
        assert response.status_code == 200
        payload = response.json()
        data = _response_data(payload)
        assert "total_cycles" in data
        assert "by_status" in data
        assert "average_duration" in data
        assert "average_confidence" in data
        
        # Test solution analytics
        response = client.get("/api/v1/analytics/solutions")
        
        assert response.status_code == 200
        payload = response.json()
        data = _response_data(payload)
        assert "total_solutions" in data
        assert "by_status" in data
        assert "average_confidence" in data
        assert "average_feasibility" in data

    def test_analytics_payload_structure(self, client):
        """Ensure analytics endpoints expose the expected data shape."""
        endpoints = {
            "/api/v1/analytics/problems": ["total_problems", "by_status", "by_domain", "success_rate"],
            "/api/v1/analytics/cycles": ["total_cycles", "by_status", "average_duration", "average_confidence", "success_rate"],
            "/api/v1/analytics/solutions": ["total_solutions", "by_status", "average_scores", "high_confidence_solutions"]
        }

        for path, required_keys in endpoints.items():
            response = client.get(path)
            assert response.status_code == 200, f"Expected 200 from {path}"
            payload = response.json()
            data = _response_data(payload)
            for key in required_keys:
                assert key in data, f"{key} missing from {path}"
    
    def test_get_enterprises(self, client):
        """Test enterprise information endpoint."""
        response = client.get("/api/v1/supra_enterprise")

        assert response.status_code == 200
        payload = response.json()
        data = _response_data(payload)
        assert "enterprises" in data
        assert len(data["enterprises"]) == 6

        # Check enterprise structure
        for enterprise in data["enterprises"]:
            assert "id" in enterprise
            assert "name" in enterprise
            assert "type" in enterprise
            assert "description" in enterprise
            assert "color" in enterprise
            assert "symbol" in enterprise
            assert "core_principle" in enterprise
            assert "expertise_areas" in enterprise
            assert "processing_order" in enterprise
            assert "is_active" in enterprise

    def test_get_enterprise_performance(self, client):
        """Test enterprise performance endpoint."""
        pytest.skip("Enterprise performance endpoint is not implemented in core API")
    
    def test_api_error_handling(self, client):
        """Test API error handling."""
        # Test 404 for non-existent problem
        missing_problem_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/problems/{missing_problem_id}")
        assert response.status_code == 404

        # Test 422 for invalid problem data
        invalid_data = {
            "title": "",  # Empty title should be invalid
            "description": "Test description",
            "complexity": "invalid_complexity",
            "domain": "Test"
        }

        response = client.post("/api/v1/problems", json=invalid_data)
        assert response.status_code == 422

        # Test 404 for non-existent cycle
        missing_cycle_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/cycles/{missing_cycle_id}")
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
        payload = response.json()
        data = _response_data(payload)
        assert len(data["problems"]) == 5
        assert data["limit"] == 5
        assert data["offset"] == 0
        assert data["total_count"] >= 15
        
        # Test second page
        response = client.get("/api/v1/problems?limit=5&offset=5")

        assert response.status_code == 200
        payload = response.json()
        data = _response_data(payload)
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
        payload = response.json()
        data = _response_data(payload)
        assert len(data["problems"]) >= 3
        for problem in data["problems"]:
            assert problem["complexity"] == "moderate"
        
        # Test filtering by domain
        response = client.get("/api/v1/problems?domain=Test")

        assert response.status_code == 200
        payload = response.json()
        data = _response_data(payload)
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
        payload = response.json()
        data = _response_data(payload)
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

        assert response.status_code == 200
        payload = response.json()
        data = _response_data(payload)
        assert data["title"] == "Async Test Problem"
        assert "problem_id" in data
    
    def test_api_rate_limiting(self, client):
        """Test API rate limiting."""
        pytest.skip("Rate limiting is not enabled on core API endpoints")
    
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
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        
        # Test invalid content type
        response = client.post(
            "/api/v1/problems",
            data=problem_data,
            headers={"Content-Type": "text/plain"}
        )
        
        assert response.status_code == 422  # Validation error
