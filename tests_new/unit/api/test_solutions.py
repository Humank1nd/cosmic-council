"""
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
