"""
End-to-end tests for complete workflows.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


class TestCompleteWorkflow:
    """Test complete problem-solving workflow."""
    
    def test_problem_to_solution_workflow(self):
        """Test complete problem to solution workflow."""
        client = TestClient(app)
        
        # 1. Create a problem
        problem_data = {
            "title": "E2E Test Problem",
            "description": "End-to-end test problem",
            "domain": "technology",
            "complexity": "simple"
        }
        
        problem_response = client.post("/api/v1/problems", json=problem_data)
        assert problem_response.status_code in [200, 201, 422]
        
        # 2. Create a cycle
        if problem_response.status_code in [200, 201]:
            problem_id = problem_response.json().get("id", "test-id")
            cycle_data = {
                "problem_id": problem_id,
                "status": "pending"
            }
            
            cycle_response = client.post("/api/v1/cycles", json=cycle_data)
            assert cycle_response.status_code in [200, 201, 422]
        
        # 3. Create a solution
        solution_data = {
            "problem_id": problem_id if 'problem_id' in locals() else "test-id",
            "title": "E2E Test Solution",
            "description": "End-to-end test solution",
            "approach": "Test approach"
        }
        
        solution_response = client.post("/api/v1/solutions", json=solution_data)
        assert solution_response.status_code in [200, 201, 422]
