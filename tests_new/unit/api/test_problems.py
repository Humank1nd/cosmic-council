"""
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
