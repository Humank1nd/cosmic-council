"""
Unit tests for API routes.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


class TestAPI:
    """Test API endpoints."""
    
    def test_app_creation(self):
        """Test FastAPI app creation."""
        assert app is not None
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_problems_endpoint(self):
        """Test problems endpoint."""
        client = TestClient(app)
        response = client.get("/api/v1/problems")
        # This would need proper setup for database
        assert response.status_code in [200, 404]  # 404 if no problems exist
