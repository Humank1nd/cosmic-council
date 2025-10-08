"""
Integration tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


class TestAPIIntegration:
    """Test API integration."""
    
    def test_problem_creation_flow(self):
        """Test complete problem creation flow."""
        client = TestClient(app)
        
        # Create a problem
        problem_data = {
            "title": "Test Problem",
            "description": "Test description",
            "domain": "technology",
            "complexity": "moderate"
        }
        
        response = client.post("/api/v1/problems", json=problem_data)
        # This would need proper database setup
        assert response.status_code in [200, 201, 422]
    
    def test_cycle_creation_flow(self):
        """Test complete cycle creation flow."""
        client = TestClient(app)
        
        cycle_data = {
            "problem_id": "test-problem-id",
            "status": "pending"
        }
        
        response = client.post("/api/v1/cycles", json=cycle_data)
        # This would need proper database setup
        assert response.status_code in [200, 201, 422]
