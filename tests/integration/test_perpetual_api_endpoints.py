"""
Integration tests for Perpetual Thinking API endpoints
Tests the API endpoints for the perpetual thinking system
"""

import pytest
import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from typing import Dict, Any

# Import the API application
from cosmic_council_api import app
from perpetual_ai_integration import AIEnhancementLevel


class TestPerpetualAPIEndpoints:
    """Test the perpetual thinking API endpoints"""

    @pytest.fixture
    def client(self):
        """Create a test client for the API"""
        return TestClient(app)

    @pytest.fixture
    def sample_session_data(self):
        """Sample session creation data"""
        return {
            "session_name": "Test Perpetual Session",
            "initial_input": "How can we solve global climate change through innovative technology?",
            "mode": "collaborative",
            "goals": ["sustainability", "economic_viability"],
            "success_criteria": ["20% carbon reduction", "cost effective"],
            "ai_enhancement_level": "enhanced",
            "ai_learning_enabled": True,
            "ai_adaptation_enabled": True,
            "ai_breakthrough_detection": True
        }

    @pytest.mark.asyncio
    async def test_create_perpetual_session(self, client, sample_session_data):
        """Test creating a perpetual thinking session"""
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine:
            mock_session_id = "test-session-id-123"
            mock_engine.start_ai_enhanced_perpetual_cycle.return_value = mock_session_id
            
            response = client.post("/api/v1/perpetual/sessions", json=sample_session_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["session_id"] == mock_session_id
            assert data["data"]["session_name"] == sample_session_data["session_name"]
            assert data["data"]["ai_enhancement_level"] == sample_session_data["ai_enhancement_level"]
            assert data["data"]["ai_learning_enabled"] == sample_session_data["ai_learning_enabled"]
            assert data["data"]["ai_adaptation_enabled"] == sample_session_data["ai_adaptation_enabled"]
            assert data["data"]["ai_breakthrough_detection"] == sample_session_data["ai_breakthrough_detection"]

    @pytest.mark.asyncio
    async def test_create_perpetual_session_validation(self, client):
        """Test session creation with validation errors"""
        # Test missing required fields
        invalid_data = {
            "session_name": "Test Session"
            # Missing initial_input
        }
        
        response = client.post("/api/v1/perpetual/sessions", json=invalid_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_perpetual_sessions(self, client):
        """Test getting all perpetual sessions"""
        with patch('cosmic_council_api.perpetual_db_service') as mock_db:
            mock_sessions = [
                {
                    "session_id": "session-1",
                    "session_name": "Session 1",
                    "status": "active",
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "session_id": "session-2",
                    "session_name": "Session 2",
                    "status": "completed",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            ]
            mock_db.get_all_sessions.return_value = mock_sessions
            
            response = client.get("/api/v1/perpetual/sessions")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]["sessions"]) == 2
            assert data["data"]["sessions"][0]["session_id"] == "session-1"
            assert data["data"]["sessions"][1]["session_id"] == "session-2"

    @pytest.mark.asyncio
    async def test_get_perpetual_session(self, client):
        """Test getting a specific perpetual session"""
        session_id = "test-session-id"
        
        with patch('cosmic_council_api.perpetual_db_service') as mock_db:
            mock_session = {
                "session_id": session_id,
                "session_name": "Test Session",
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "ai_enhancement_level": "enhanced",
                "ai_learning_enabled": True,
                "ai_adaptation_enabled": True,
                "ai_breakthrough_detection": True
            }
            mock_db.get_session.return_value = mock_session
            
            response = client.get(f"/api/v1/perpetual/sessions/{session_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["session_id"] == session_id
            assert data["data"]["session_name"] == "Test Session"

    @pytest.mark.asyncio
    async def test_get_perpetual_session_not_found(self, client):
        """Test getting a non-existent perpetual session"""
        session_id = "non-existent-session"
        
        with patch('cosmic_council_api.perpetual_db_service') as mock_db:
            mock_db.get_session.return_value = None
            
            response = client.get(f"/api/v1/perpetual/sessions/{session_id}")
            
            assert response.status_code == 404
            data = response.json()
            assert data["success"] is False
            assert "not found" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_pause_perpetual_session(self, client):
        """Test pausing a perpetual session"""
        session_id = "test-session-id"
        
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine:
            mock_engine.ai_sessions = {session_id: Mock()}
            
            response = client.post(f"/api/v1/perpetual/sessions/{session_id}/pause")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "paused" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_stop_perpetual_session(self, client):
        """Test stopping a perpetual session"""
        session_id = "test-session-id"
        
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine:
            mock_engine.ai_sessions = {session_id: Mock()}
            
            response = client.post(f"/api/v1/perpetual/sessions/{session_id}/stop")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "stopped" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_get_perpetual_system_status(self, client):
        """Test getting perpetual system status"""
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine, \
             patch('cosmic_council_api.perpetual_db_service') as mock_db:
            
            mock_engine.ai_sessions = {
                "session-1": Mock(status="active"),
                "session-2": Mock(status="active")
            }
            mock_db.get_all_sessions.return_value = [
                {"session_id": "session-1", "status": "active"},
                {"session_id": "session-2", "status": "active"}
            ]
            
            response = client.get("/api/v1/perpetual/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["active_sessions"] == 2
            assert data["data"]["active_ai_sessions"] == 2
            assert data["data"]["perpetual_ai_engine_available"] is True

    @pytest.mark.asyncio
    async def test_get_ai_sessions(self, client):
        """Test getting AI-enhanced sessions"""
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine:
            mock_ai_sessions = {
                "session-1": Mock(
                    session_id="session-1",
                    session_name="AI Session 1",
                    ai_enhancement_level=AIEnhancementLevel.ENHANCED,
                    status="active"
                ),
                "session-2": Mock(
                    session_id="session-2",
                    session_name="AI Session 2",
                    ai_enhancement_level=AIEnhancementLevel.AUTONOMOUS,
                    status="completed"
                )
            }
            mock_engine.ai_sessions = mock_ai_sessions
            
            response = client.get("/api/v1/perpetual/ai/sessions")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]["sessions"]) == 2

    @pytest.mark.asyncio
    async def test_get_ai_sessions_with_filter(self, client):
        """Test getting AI-enhanced sessions with enhancement level filter"""
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine:
            mock_ai_sessions = {
                "session-1": Mock(
                    session_id="session-1",
                    session_name="AI Session 1",
                    ai_enhancement_level=AIEnhancementLevel.ENHANCED,
                    status="active"
                ),
                "session-2": Mock(
                    session_id="session-2",
                    session_name="AI Session 2",
                    ai_enhancement_level=AIEnhancementLevel.AUTONOMOUS,
                    status="completed"
                )
            }
            mock_engine.ai_sessions = mock_ai_sessions
            
            response = client.get("/api/v1/perpetual/ai/sessions?ai_enhancement_level=enhanced")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            # Should only return enhanced sessions
            assert len(data["data"]["sessions"]) == 1
            assert data["data"]["sessions"][0]["ai_enhancement_level"] == "enhanced"

    @pytest.mark.asyncio
    async def test_get_ai_session_analytics(self, client):
        """Test getting AI session analytics"""
        session_id = "test-session-id"
        
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine:
            mock_analytics = {
                "session_id": session_id,
                "session_name": "Test Session",
                "ai_enhancement_level": "enhanced",
                "total_ai_enhanced_cycles": 5,
                "avg_ai_confidence": 0.85,
                "avg_impact_score": 0.78,
                "total_ai_tokens_used": 1500,
                "total_ai_processing_time_seconds": 12.5
            }
            mock_engine.get_ai_session_analytics.return_value = mock_analytics
            
            response = client.get(f"/api/v1/perpetual/ai/sessions/{session_id}/analytics")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["session_id"] == session_id
            assert data["data"]["total_ai_enhanced_cycles"] == 5
            assert data["data"]["avg_ai_confidence"] == 0.85

    @pytest.mark.asyncio
    async def test_get_ai_session_analytics_not_found(self, client):
        """Test getting analytics for non-existent AI session"""
        session_id = "non-existent-session"
        
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine:
            mock_engine.get_ai_session_analytics.return_value = None
            
            response = client.get(f"/api/v1/perpetual/ai/sessions/{session_id}/analytics")
            
            assert response.status_code == 404
            data = response.json()
            assert data["success"] is False
            assert "not found" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_get_ai_enhanced_cycle_status(self, client):
        """Test getting AI enhanced cycle status"""
        session_id = "test-session-id"
        
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine:
            mock_status = {
                "session_id": session_id,
                "cycle_id": "cycle-123",
                "cycle_number": 3,
                "cycle_type": "exploration",
                "status": "running",
                "confidence_score": 0.82,
                "creativity_score": 0.75,
                "wisdom_density": 0.68,
                "ai_enhancement_level": "enhanced"
            }
            mock_engine.get_ai_enhanced_cycle_status.return_value = mock_status
            
            response = client.get(f"/api/v1/perpetual/ai/sessions/{session_id}/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["session_id"] == session_id
            assert data["data"]["cycle_number"] == 3
            assert data["data"]["status"] == "running"

    @pytest.mark.asyncio
    async def test_get_ai_enhanced_cycle_status_not_found(self, client):
        """Test getting cycle status for non-existent session"""
        session_id = "non-existent-session"
        
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine:
            mock_engine.get_ai_enhanced_cycle_status.return_value = None
            
            response = client.get(f"/api/v1/perpetual/ai/sessions/{session_id}/status")
            
            assert response.status_code == 404
            data = response.json()
            assert data["success"] is False
            assert "not found" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_perpetual_system_not_available(self, client):
        """Test API behavior when perpetual system is not available"""
        with patch('cosmic_council_api.perpetual_ai_engine', None):
            response = client.post("/api/v1/perpetual/sessions", json={
                "session_name": "Test Session",
                "initial_input": "Test input"
            })
            
            assert response.status_code == 503
            data = response.json()
            assert data["success"] is False
            assert "not available" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_health_check_with_perpetual_system(self, client):
        """Test health check includes perpetual system status"""
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine:
            mock_engine.ai_sessions = {"session-1": Mock()}
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "perpetual_ai_engine" in data["components"]
            assert data["components"]["perpetual_ai_engine"] == "available"

    @pytest.mark.asyncio
    async def test_api_info_includes_perpetual_endpoints(self, client):
        """Test API info includes perpetual thinking endpoints"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "perpetual" in data["endpoints"]
        
        perpetual_endpoints = data["endpoints"]["perpetual"]
        assert "sessions" in perpetual_endpoints
        assert "ai" in perpetual_endpoints
        assert "status" in perpetual_endpoints

    @pytest.mark.asyncio
    async def test_error_handling_in_api_endpoints(self, client):
        """Test error handling in API endpoints"""
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine:
            # Test with engine that raises an exception
            mock_engine.start_ai_enhanced_perpetual_cycle.side_effect = Exception("Test error")
            
            response = client.post("/api/v1/perpetual/sessions", json={
                "session_name": "Test Session",
                "initial_input": "Test input"
            })
            
            assert response.status_code == 500
            data = response.json()
            assert data["success"] is False
            assert "error" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_concurrent_api_requests(self, client, sample_session_data):
        """Test handling concurrent API requests"""
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine:
            mock_engine.start_ai_enhanced_perpetual_cycle.return_value = "test-session-id"
            
            # Make multiple concurrent requests
            responses = []
            for i in range(5):
                data = sample_session_data.copy()
                data["session_name"] = f"Concurrent Session {i}"
                response = client.post("/api/v1/perpetual/sessions", json=data)
                responses.append(response)
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
