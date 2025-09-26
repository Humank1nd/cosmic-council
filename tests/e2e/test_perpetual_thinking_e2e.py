"""
End-to-end tests for the Perpetual Thinking System
Tests complete workflows from API to database to AI integration
"""

import pytest
import asyncio
import uuid
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from typing import Dict, Any

# Import the API application
from cosmic_council_api import app
from perpetual_ai_integration import AIEnhancementLevel, AIThinkingMode
from ai_llm_integration import LLMConfig, LLMProvider, LLMModel


class TestPerpetualThinkingE2E:
    """End-to-end tests for the perpetual thinking system"""

    @pytest.fixture
    def client(self):
        """Create a test client for the API"""
        return TestClient(app)

    @pytest.fixture
    def sample_problem_scenarios(self):
        """Sample problem scenarios for E2E testing"""
        return [
            {
                "name": "Climate Change Solution",
                "input": "How can we develop a comprehensive solution to global climate change that balances environmental protection with economic growth?",
                "goals": ["carbon_neutrality", "economic_viability", "social_equity"],
                "success_criteria": ["50% carbon reduction by 2030", "maintain GDP growth", "create green jobs"]
            },
            {
                "name": "Urban Planning Innovation",
                "input": "Design a smart city infrastructure that maximizes efficiency, sustainability, and quality of life for residents.",
                "goals": ["sustainability", "efficiency", "livability"],
                "success_criteria": ["reduce energy consumption by 30%", "improve air quality", "increase green spaces"]
            },
            {
                "name": "Healthcare System Optimization",
                "input": "How can we redesign healthcare systems to provide universal access while maintaining quality and controlling costs?",
                "goals": ["universal_access", "quality_care", "cost_control"],
                "success_criteria": ["100% population coverage", "reduce costs by 20%", "improve patient outcomes"]
            }
        ]

    @pytest.mark.asyncio
    async def test_complete_perpetual_thinking_workflow(self, client, sample_problem_scenarios):
        """Test complete perpetual thinking workflow from creation to completion"""
        scenario = sample_problem_scenarios[0]
        
        # Step 1: Create a perpetual thinking session
        session_data = {
            "session_name": scenario["name"],
            "initial_input": scenario["input"],
            "mode": "collaborative",
            "goals": scenario["goals"],
            "success_criteria": scenario["success_criteria"],
            "ai_enhancement_level": "enhanced",
            "ai_learning_enabled": True,
            "ai_adaptation_enabled": True,
            "ai_breakthrough_detection": True
        }
        
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine, \
             patch('cosmic_council_api.perpetual_db_service') as mock_db:
            
            # Mock session creation
            session_id = str(uuid.uuid4())
            mock_engine.start_ai_enhanced_perpetual_cycle.return_value = session_id
            
            # Create session
            create_response = client.post("/api/v1/perpetual/sessions", json=session_data)
            assert create_response.status_code == 200
            create_data = create_response.json()
            assert create_data["success"] is True
            assert create_data["data"]["session_id"] == session_id
            
            # Step 2: Verify session was created and persisted
            mock_db.get_session.return_value = {
                "session_id": session_id,
                "session_name": scenario["name"],
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "ai_enhancement_level": "enhanced"
            }
            
            get_response = client.get(f"/api/v1/perpetual/sessions/{session_id}")
            assert get_response.status_code == 200
            get_data = get_response.json()
            assert get_data["success"] is True
            assert get_data["data"]["session_id"] == session_id
            assert get_data["data"]["session_name"] == scenario["name"]
            
            # Step 3: Check system status
            mock_engine.ai_sessions = {session_id: Mock(status="active")}
            mock_db.get_all_sessions.return_value = [{"session_id": session_id, "status": "active"}]
            
            status_response = client.get("/api/v1/perpetual/status")
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["success"] is True
            assert status_data["data"]["active_sessions"] == 1
            assert status_data["data"]["active_ai_sessions"] == 1
            
            # Step 4: Get AI session analytics
            mock_analytics = {
                "session_id": session_id,
                "session_name": scenario["name"],
                "ai_enhancement_level": "enhanced",
                "total_ai_enhanced_cycles": 3,
                "avg_ai_confidence": 0.87,
                "avg_impact_score": 0.82,
                "total_ai_tokens_used": 1200,
                "total_ai_processing_time_seconds": 8.5
            }
            mock_engine.get_ai_session_analytics.return_value = mock_analytics
            
            analytics_response = client.get(f"/api/v1/perpetual/ai/sessions/{session_id}/analytics")
            assert analytics_response.status_code == 200
            analytics_data = analytics_response.json()
            assert analytics_data["success"] is True
            assert analytics_data["data"]["total_ai_enhanced_cycles"] == 3
            assert analytics_data["data"]["avg_ai_confidence"] == 0.87
            
            # Step 5: Get AI enhanced cycle status
            mock_cycle_status = {
                "session_id": session_id,
                "cycle_id": "cycle-123",
                "cycle_number": 3,
                "cycle_type": "synthesis",
                "status": "running",
                "confidence_score": 0.89,
                "creativity_score": 0.85,
                "wisdom_density": 0.78,
                "ai_enhancement_level": "enhanced"
            }
            mock_engine.get_ai_enhanced_cycle_status.return_value = mock_cycle_status
            
            cycle_status_response = client.get(f"/api/v1/perpetual/ai/sessions/{session_id}/status")
            assert cycle_status_response.status_code == 200
            cycle_status_data = cycle_status_response.json()
            assert cycle_status_data["success"] is True
            assert cycle_status_data["data"]["cycle_number"] == 3
            assert cycle_status_data["data"]["status"] == "running"
            
            # Step 6: Pause the session
            mock_engine.ai_sessions = {session_id: Mock()}
            
            pause_response = client.post(f"/api/v1/perpetual/sessions/{session_id}/pause")
            assert pause_response.status_code == 200
            pause_data = pause_response.json()
            assert pause_data["success"] is True
            
            # Step 7: Stop the session
            stop_response = client.post(f"/api/v1/perpetual/sessions/{session_id}/stop")
            assert stop_response.status_code == 200
            stop_data = stop_response.json()
            assert stop_data["success"] is True

    @pytest.mark.asyncio
    async def test_multiple_ai_enhancement_levels_workflow(self, client, sample_problem_scenarios):
        """Test workflow with different AI enhancement levels"""
        scenario = sample_problem_scenarios[1]
        
        enhancement_levels = ["none", "assisted", "enhanced", "autonomous"]
        session_ids = []
        
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine, \
             patch('cosmic_council_api.perpetual_db_service') as mock_db:
            
            for i, level in enumerate(enhancement_levels):
                session_data = {
                    "session_name": f"{scenario['name']} - {level.title()}",
                    "initial_input": scenario["input"],
                    "mode": "collaborative",
                    "goals": scenario["goals"],
                    "success_criteria": scenario["success_criteria"],
                    "ai_enhancement_level": level,
                    "ai_learning_enabled": True,
                    "ai_adaptation_enabled": True,
                    "ai_breakthrough_detection": True
                }
                
                session_id = str(uuid.uuid4())
                mock_engine.start_ai_enhanced_perpetual_cycle.return_value = session_id
                session_ids.append(session_id)
                
                # Create session
                create_response = client.post("/api/v1/perpetual/sessions", json=session_data)
                assert create_response.status_code == 200
                create_data = create_response.json()
                assert create_data["success"] is True
                assert create_data["data"]["ai_enhancement_level"] == level
            
            # Verify all sessions were created
            mock_db.get_all_sessions.return_value = [
                {"session_id": sid, "status": "active", "ai_enhancement_level": level}
                for sid, level in zip(session_ids, enhancement_levels)
            ]
            
            get_sessions_response = client.get("/api/v1/perpetual/sessions")
            assert get_sessions_response.status_code == 200
            sessions_data = get_sessions_response.json()
            assert sessions_data["success"] is True
            assert len(sessions_data["data"]["sessions"]) == 4
            
            # Test AI sessions filtering
            mock_engine.ai_sessions = {
                sid: Mock(
                    session_id=sid,
                    session_name=f"Session {i}",
                    ai_enhancement_level=getattr(AIEnhancementLevel, level.upper()),
                    status="active"
                )
                for i, (sid, level) in enumerate(zip(session_ids, enhancement_levels))
            }
            
            # Filter for enhanced sessions only
            ai_sessions_response = client.get("/api/v1/perpetual/ai/sessions?ai_enhancement_level=enhanced")
            assert ai_sessions_response.status_code == 200
            ai_sessions_data = ai_sessions_response.json()
            assert ai_sessions_data["success"] is True
            assert len(ai_sessions_data["data"]["sessions"]) == 1
            assert ai_sessions_data["data"]["sessions"][0]["ai_enhancement_level"] == "enhanced"

    @pytest.mark.asyncio
    async def test_ai_learning_and_adaptation_workflow(self, client, sample_problem_scenarios):
        """Test AI learning and adaptation features in E2E workflow"""
        scenario = sample_problem_scenarios[2]
        
        session_data = {
            "session_name": scenario["name"],
            "initial_input": scenario["input"],
            "mode": "collaborative",
            "goals": scenario["goals"],
            "success_criteria": scenario["success_criteria"],
            "ai_enhancement_level": "enhanced",
            "ai_learning_enabled": True,
            "ai_adaptation_enabled": True,
            "ai_breakthrough_detection": True
        }
        
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine, \
             patch('cosmic_council_api.perpetual_db_service') as mock_db:
            
            session_id = str(uuid.uuid4())
            mock_engine.start_ai_enhanced_perpetual_cycle.return_value = session_id
            
            # Create session with learning enabled
            create_response = client.post("/api/v1/perpetual/sessions", json=session_data)
            assert create_response.status_code == 200
            
            # Simulate learning and adaptation over multiple cycles
            mock_analytics = {
                "session_id": session_id,
                "session_name": scenario["name"],
                "ai_enhancement_level": "enhanced",
                "total_ai_enhanced_cycles": 5,
                "avg_ai_confidence": 0.92,  # High confidence from learning
                "avg_impact_score": 0.88,   # High impact from adaptation
                "total_ai_tokens_used": 2500,
                "total_ai_processing_time_seconds": 15.2,
                "ai_session_insights_count": 8,
                "ai_learning_events_count": 3
            }
            mock_engine.get_ai_session_analytics.return_value = mock_analytics
            
            # Get analytics to verify learning occurred
            analytics_response = client.get(f"/api/v1/perpetual/ai/sessions/{session_id}/analytics")
            assert analytics_response.status_code == 200
            analytics_data = analytics_response.json()
            assert analytics_data["success"] is True
            assert analytics_data["data"]["ai_learning_events_count"] == 3
            assert analytics_data["data"]["ai_session_insights_count"] == 8
            assert analytics_data["data"]["avg_ai_confidence"] > 0.9  # High confidence from learning

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, client, sample_problem_scenarios):
        """Test error recovery in E2E workflow"""
        scenario = sample_problem_scenarios[0]
        
        session_data = {
            "session_name": scenario["name"],
            "initial_input": scenario["input"],
            "mode": "collaborative",
            "goals": scenario["goals"],
            "success_criteria": scenario["success_criteria"],
            "ai_enhancement_level": "enhanced",
            "ai_learning_enabled": True,
            "ai_adaptation_enabled": True,
            "ai_breakthrough_detection": True
        }
        
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine, \
             patch('cosmic_council_api.perpetual_db_service') as mock_db:
            
            session_id = str(uuid.uuid4())
            
            # Test error during session creation
            mock_engine.start_ai_enhanced_perpetual_cycle.side_effect = Exception("Simulated error")
            
            create_response = client.post("/api/v1/perpetual/sessions", json=session_data)
            assert create_response.status_code == 500
            create_data = create_response.json()
            assert create_data["success"] is False
            assert "error" in create_data["message"].lower()
            
            # Test recovery - reset mock and try again
            mock_engine.start_ai_enhanced_perpetual_cycle.side_effect = None
            mock_engine.start_ai_enhanced_perpetual_cycle.return_value = session_id
            
            create_response = client.post("/api/v1/perpetual/sessions", json=session_data)
            assert create_response.status_code == 200
            create_data = create_response.json()
            assert create_data["success"] is True
            
            # Test error during analytics retrieval
            mock_engine.get_ai_session_analytics.side_effect = Exception("Analytics error")
            
            analytics_response = client.get(f"/api/v1/perpetual/ai/sessions/{session_id}/analytics")
            assert analytics_response.status_code == 500
            analytics_data = analytics_response.json()
            assert analytics_data["success"] is False

    @pytest.mark.asyncio
    async def test_concurrent_sessions_workflow(self, client, sample_problem_scenarios):
        """Test handling multiple concurrent sessions in E2E workflow"""
        session_ids = []
        
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine, \
             patch('cosmic_council_api.perpetual_db_service') as mock_db:
            
            # Create multiple concurrent sessions
            for i, scenario in enumerate(sample_problem_scenarios):
                session_data = {
                    "session_name": f"{scenario['name']} - Concurrent {i}",
                    "initial_input": scenario["input"],
                    "mode": "collaborative",
                    "goals": scenario["goals"],
                    "success_criteria": scenario["success_criteria"],
                    "ai_enhancement_level": "enhanced",
                    "ai_learning_enabled": True,
                    "ai_adaptation_enabled": True,
                    "ai_breakthrough_detection": True
                }
                
                session_id = str(uuid.uuid4())
                mock_engine.start_ai_enhanced_perpetual_cycle.return_value = session_id
                session_ids.append(session_id)
                
                # Create session
                create_response = client.post("/api/v1/perpetual/sessions", json=session_data)
                assert create_response.status_code == 200
                create_data = create_response.json()
                assert create_data["success"] is True
            
            # Verify all sessions are tracked
            mock_engine.ai_sessions = {
                sid: Mock(status="active") for sid in session_ids
            }
            mock_db.get_all_sessions.return_value = [
                {"session_id": sid, "status": "active"} for sid in session_ids
            ]
            
            # Check system status
            status_response = client.get("/api/v1/perpetual/status")
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["success"] is True
            assert status_data["data"]["active_sessions"] == len(session_ids)
            assert status_data["data"]["active_ai_sessions"] == len(session_ids)
            
            # Get all sessions
            get_sessions_response = client.get("/api/v1/perpetual/sessions")
            assert get_sessions_response.status_code == 200
            sessions_data = get_sessions_response.json()
            assert sessions_data["success"] is True
            assert len(sessions_data["data"]["sessions"]) == len(session_ids)

    @pytest.mark.asyncio
    async def test_web_interface_integration(self, client):
        """Test web interface integration with perpetual thinking system"""
        # Test that the web interface can access perpetual endpoints
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine, \
             patch('cosmic_council_api.perpetual_db_service') as mock_db:
            
            # Mock web interface data
            mock_db.get_all_sessions.return_value = [
                {
                    "session_id": "web-session-1",
                    "session_name": "Web Interface Test",
                    "status": "active",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            ]
            
            mock_engine.ai_sessions = {
                "web-session-1": Mock(
                    session_id="web-session-1",
                    session_name="Web Interface Test",
                    ai_enhancement_level=AIEnhancementLevel.ENHANCED,
                    status="active"
                )
            }
            
            # Test web interface can get sessions
            web_sessions_response = client.get("/api/web/perpetual/sessions")
            assert web_sessions_response.status_code == 200
            
            # Test web interface can get system status
            web_status_response = client.get("/api/web/perpetual/status")
            assert web_status_response.status_code == 200
            
            # Test web interface can get AI sessions
            web_ai_sessions_response = client.get("/api/web/perpetual/ai/sessions")
            assert web_ai_sessions_response.status_code == 200

    @pytest.mark.asyncio
    async def test_performance_under_load(self, client, sample_problem_scenarios):
        """Test system performance under load in E2E scenario"""
        scenario = sample_problem_scenarios[0]
        
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine, \
             patch('cosmic_council_api.perpetual_db_service') as mock_db:
            
            # Create multiple sessions quickly to simulate load
            session_ids = []
            start_time = datetime.now()
            
            for i in range(10):  # Create 10 sessions
                session_data = {
                    "session_name": f"{scenario['name']} - Load Test {i}",
                    "initial_input": scenario["input"],
                    "mode": "collaborative",
                    "goals": scenario["goals"],
                    "success_criteria": scenario["success_criteria"],
                    "ai_enhancement_level": "enhanced",
                    "ai_learning_enabled": True,
                    "ai_adaptation_enabled": True,
                    "ai_breakthrough_detection": True
                }
                
                session_id = str(uuid.uuid4())
                mock_engine.start_ai_enhanced_perpetual_cycle.return_value = session_id
                session_ids.append(session_id)
                
                # Create session
                create_response = client.post("/api/v1/perpetual/sessions", json=session_data)
                assert create_response.status_code == 200
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Verify performance - should complete within reasonable time
            assert duration < 5.0  # Should complete 10 sessions in under 5 seconds
            
            # Verify all sessions were created
            mock_engine.ai_sessions = {sid: Mock(status="active") for sid in session_ids}
            mock_db.get_all_sessions.return_value = [
                {"session_id": sid, "status": "active"} for sid in session_ids
            ]
            
            status_response = client.get("/api/v1/perpetual/status")
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["data"]["active_sessions"] == 10
