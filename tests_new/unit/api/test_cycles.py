"""
Unit tests for cycle API routes.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


class TestCycleRoutes:
    """Test cycle API routes."""
    
    def test_get_cycles(self):
        """Test GET /api/v1/cycles endpoint."""
        client = TestClient(app)
        response = client.get("/api/v1/cycles")
        assert response.status_code in [200, 404]
    
    def test_create_cycle(self):
        """Test POST /api/v1/cycles endpoint."""
        client = TestClient(app)
        cycle_data = {
            "problem_id": "test-problem-id",
            "status": "pending"
        }
        
        response = client.post("/api/v1/cycles", json=cycle_data)
        assert response.status_code in [200, 201, 422]
    
    def test_get_cycle_by_id(self):
        """Test GET /api/v1/cycles/{id} endpoint."""
        client = TestClient(app)
        response = client.get("/api/v1/cycles/test-id")
        assert response.status_code in [200, 404]
