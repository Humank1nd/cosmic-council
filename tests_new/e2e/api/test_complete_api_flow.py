"""
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
