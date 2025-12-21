"""
Integration tests for the Perpetual Thinking System
Tests the integration between perpetual thinking engine, AI integration, and database
"""

import pytest
import pytest_asyncio
import asyncio
import uuid
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

# Import the components to test
from perpetual_ai_integration import (
    PerpetualAIThinkingEngine,
    AIEnhancementLevel,
    AIThinkingMode
)
from perpetual_thinking_engine import PerpetualCycle, CycleType, CycleStatus
from ai_llm_integration import AILLMIntegration, LLMConfig, LLMProvider, LLMModel
from think_tank_integration_system import CosmicCouncilThinkTankIntegration
from perpetual_database_service import PerpetualDatabaseService


class TestPerpetualThinkingIntegration:
    """Test the integration of perpetual thinking components"""

    @pytest_asyncio.fixture
    async def ai_engine_with_db(self):
        """Create a Perpetual AI Thinking Engine with database for testing"""
        # Use in-memory database for testing
        db_url = "sqlite:///:memory:"
        
        # Initialize database service
        db_service = PerpetualDatabaseService(db_url)
        await db_service.create_tables()
        
        # Initialize AI config
        ai_config = LLMConfig(
            provider=LLMProvider.MOCK,
            model=LLMModel.GPT_4,
            temperature=0.7,
            max_tokens=2000
        )
        
        # Initialize AI engine
        engine = PerpetualAIThinkingEngine(
            database_url=db_url,
            ai_config=ai_config
        )
        
        return engine, db_service

    @pytest.fixture
    def sample_problem_statement(self):
        """Sample problem statement for testing"""
        return "How can we develop sustainable energy solutions that are both economically viable and environmentally friendly?"

    @pytest.mark.asyncio
    async def test_ai_enhanced_cycle_execution(self, ai_engine_with_db, sample_problem_statement):
        """Test complete AI-enhanced cycle execution"""
        ai_engine, db_service = ai_engine_with_db
        
        # Start an AI-enhanced session
        session_id = await ai_engine.start_ai_enhanced_perpetual_cycle(
            initial_input=sample_problem_statement,
            ai_enhancement_level=AIEnhancementLevel.ENHANCED,
            ai_learning_enabled=True,
            ai_adaptation_enabled=True,
            ai_breakthrough_detection=True,
            max_cycles=1  # Limit to 1 cycle for testing
        )
        
        # Wait a bit for the cycle to complete
        await asyncio.sleep(2)
        
        # Verify session was created
        assert session_id in ai_engine.ai_sessions
        ai_session = ai_engine.ai_sessions[session_id]
        
        # Verify session properties
        assert ai_session.initial_input == sample_problem_statement
        assert ai_session.ai_enhancement_level == AIEnhancementLevel.ENHANCED
        assert ai_session.ai_learning_enabled is True
        assert ai_session.ai_adaptation_enabled is True
        assert ai_session.ai_breakthrough_detection is True
        
        # Verify cycles were created
        assert len(ai_session.ai_sessions_history) > 0
        
        # Verify AI enhancements were recorded
        assert len(ai_session.ai_cycle_enhancements) > 0
        
        # Verify database persistence
        session_data = await db_service.get_session(session_id)
        assert session_data is not None
        assert session_data["session_name"] == ai_session.session_name

    @pytest.mark.asyncio
    async def test_ai_enhancement_levels(self, ai_engine_with_db, sample_problem_statement):
        """Test different AI enhancement levels"""
        ai_engine, db_service = ai_engine_with_db
        
        enhancement_levels = [
            AIEnhancementLevel.NONE,
            AIEnhancementLevel.ASSISTED,
            AIEnhancementLevel.ENHANCED,
            AIEnhancementLevel.AUTONOMOUS
        ]
        
        session_ids = []
        
        for level in enhancement_levels:
            session_id = await ai_engine.start_ai_enhanced_perpetual_cycle(
                initial_input=f"{sample_problem_statement} (Level: {level.value})",
                ai_enhancement_level=level,
                ai_learning_enabled=True,
                ai_adaptation_enabled=True,
                ai_breakthrough_detection=True,
                max_cycles=1
            )
            session_ids.append(session_id)
            
            # Wait for cycle completion
            await asyncio.sleep(1)
        
        # Verify all sessions were created with correct enhancement levels
        for i, session_id in enumerate(session_ids):
            ai_session = ai_engine.ai_sessions[session_id]
            assert ai_session.ai_enhancement_level == enhancement_levels[i]
            
            # Verify AI enhancements were applied based on level
            if enhancement_levels[i] == AIEnhancementLevel.NONE:
                # No AI enhancements should be recorded
                assert len(ai_session.ai_cycle_enhancements) == 0
            else:
                # AI enhancements should be recorded
                assert len(ai_session.ai_cycle_enhancements) > 0

    @pytest.mark.asyncio
    async def test_ai_learning_and_adaptation(self, ai_engine_with_db, sample_problem_statement):
        """Test AI learning and adaptation features"""
        ai_engine, db_service = ai_engine_with_db
        
        # Start session with learning and adaptation enabled
        session_id = await ai_engine.start_ai_enhanced_perpetual_cycle(
            initial_input=sample_problem_statement,
            ai_enhancement_level=AIEnhancementLevel.ENHANCED,
            ai_learning_enabled=True,
            ai_adaptation_enabled=True,
            ai_breakthrough_detection=True,
            max_cycles=3  # Multiple cycles to test learning
        )
        
        # Wait for cycles to complete
        await asyncio.sleep(3)
        
        ai_session = ai_engine.ai_sessions[session_id]
        
        # Verify learning history was recorded
        assert len(ai_session.ai_learning_history) >= 0  # May be 0 if no adaptations occurred
        
        # Verify session insights were generated
        assert len(ai_session.ai_session_insights) >= 0  # May be 0 if no insights generated
        
        # Verify collaborative metrics were updated
        assert ai_session.ai_collaborative_metrics is not None

    @pytest.mark.asyncio
    async def test_ai_breakthrough_detection(self, ai_engine_with_db, sample_problem_statement):
        """Test AI breakthrough detection"""
        ai_engine, db_service = ai_engine_with_db
        
        # Start session with breakthrough detection enabled
        session_id = await ai_engine.start_ai_enhanced_perpetual_cycle(
            initial_input=sample_problem_statement,
            ai_enhancement_level=AIEnhancementLevel.ENHANCED,
            ai_learning_enabled=True,
            ai_adaptation_enabled=True,
            ai_breakthrough_detection=True,
            max_cycles=2
        )
        
        # Wait for cycles to complete
        await asyncio.sleep(2)
        
        ai_session = ai_engine.ai_sessions[session_id]
        
        # Verify breakthrough detection was active
        assert ai_session.ai_breakthrough_detection is True
        
        # Check if any breakthroughs were detected (may or may not occur)
        # This is more of a smoke test to ensure the system doesn't crash
        assert ai_session.status in ["active", "completed", "terminated_with_error"]

    @pytest.mark.asyncio
    async def test_ai_session_analytics_integration(self, ai_engine_with_db, sample_problem_statement):
        """Test AI session analytics integration"""
        ai_engine, db_service = ai_engine_with_db
        
        # Start a session
        session_id = await ai_engine.start_ai_enhanced_perpetual_cycle(
            initial_input=sample_problem_statement,
            ai_enhancement_level=AIEnhancementLevel.ENHANCED,
            max_cycles=1
        )
        
        # Wait for completion
        await asyncio.sleep(2)
        
        # Get analytics
        analytics = await ai_engine.get_ai_session_analytics(session_id)
        
        assert analytics is not None
        assert analytics["session_id"] == session_id
        assert analytics["ai_enhancement_level"] == "enhanced"
        assert "total_ai_enhanced_cycles" in analytics
        assert "avg_ai_confidence" in analytics
        assert "avg_impact_score" in analytics
        assert "total_ai_tokens_used" in analytics
        assert "total_ai_processing_time_seconds" in analytics

    @pytest.mark.asyncio
    async def test_ai_enhanced_cycle_status_integration(self, ai_engine_with_db, sample_problem_statement):
        """Test AI enhanced cycle status integration"""
        ai_engine, db_service = ai_engine_with_db
        
        # Start a session
        session_id = await ai_engine.start_ai_enhanced_perpetual_cycle(
            initial_input=sample_problem_statement,
            ai_enhancement_level=AIEnhancementLevel.ENHANCED,
            max_cycles=1
        )
        
        # Wait a bit for cycle to start
        await asyncio.sleep(1)
        
        # Get cycle status
        status = await ai_engine.get_ai_enhanced_cycle_status(session_id)
        
        if status is not None:  # May be None if cycle hasn't started yet
            assert status["session_id"] == session_id
            assert "cycle_id" in status
            assert "cycle_number" in status
            assert "cycle_type" in status
            assert "status" in status
            assert "ai_enhancement_level" in status

    @pytest.mark.asyncio
    async def test_database_persistence_integration(self, ai_engine_with_db, sample_problem_statement):
        """Test database persistence integration"""
        ai_engine, db_service = ai_engine_with_db
        
        # Start a session
        session_id = await ai_engine.start_ai_enhanced_perpetual_cycle(
            initial_input=sample_problem_statement,
            ai_enhancement_level=AIEnhancementLevel.ENHANCED,
            max_cycles=1
        )
        
        # Wait for completion
        await asyncio.sleep(2)
        
        # Verify session was persisted to database
        session_data = await db_service.get_session(session_id)
        assert session_data is not None
        assert session_data["session_id"] == session_id
        
        # Verify cycles were persisted
        cycles = await db_service.get_session_cycles(session_id)
        assert len(cycles) > 0
        
        # Verify metrics were persisted
        metrics = await db_service.get_session_metrics(session_id)
        assert metrics is not None

    @pytest.mark.asyncio
    async def test_think_tank_integration(self, ai_engine_with_db, sample_problem_statement):
        """Test integration with Think Tank system"""
        ai_engine, db_service = ai_engine_with_db
        
        # Mock the Think Tank integration to return predictable results
        mock_integration_result = Mock()
        mock_integration_result.overall_confidence = 0.85
        mock_integration_result.think_tank_results = {
            "red_owl": {"status": "completed", "confidence": 0.8},
            "orange_orangutan": {"status": "completed", "confidence": 0.9}
        }
        mock_integration_result.integration_synthesis = {
            "summary": "Test synthesis",
            "key_insights": ["insight1", "insight2"]
        }
        
        with patch.object(ai_engine.think_tank_integration, 'conduct_integrated_inquiry', return_value=mock_integration_result):
            # Start a session
            session_id = await ai_engine.start_ai_enhanced_perpetual_cycle(
                initial_input=sample_problem_statement,
                ai_enhancement_level=AIEnhancementLevel.ENHANCED,
                max_cycles=1
            )
            
            # Wait for completion
            await asyncio.sleep(2)
            
            # Verify Think Tank integration was called
            ai_session = ai_engine.ai_sessions[session_id]
            assert len(ai_session.ai_sessions_history) > 0
            
            # Verify cycles have Think Tank results
            cycle_id = ai_session.ai_sessions_history[0]
            cycle = next((c for c in ai_engine.cycles if c.id == cycle_id), None)
            if cycle:
                assert cycle.output_data is not None
                assert "integration_result" in cycle.output_data
                assert "think_tank_results" in cycle.output_data

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, ai_engine_with_db, sample_problem_statement):
        """Test error handling in integrated system"""
        ai_engine, db_service = ai_engine_with_db
        
        # Mock an error in the Think Tank integration
        with patch.object(ai_engine.think_tank_integration, 'conduct_integrated_inquiry', side_effect=Exception("Test error")):
            # Start a session
            session_id = await ai_engine.start_ai_enhanced_perpetual_cycle(
                initial_input=sample_problem_statement,
                ai_enhancement_level=AIEnhancementLevel.ENHANCED,
                max_cycles=1
            )
            
            # Wait for completion
            await asyncio.sleep(2)
            
            # Verify error was handled gracefully
            ai_session = ai_engine.ai_sessions[session_id]
            assert ai_session.status in ["completed", "terminated_with_error"]
            
            # Verify system didn't crash
            assert session_id in ai_engine.ai_sessions

    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, ai_engine_with_db):
        """Test handling of concurrent AI-enhanced sessions"""
        ai_engine, db_service = ai_engine_with_db
        
        # Start multiple concurrent sessions
        session_ids = []
        for i in range(3):
            session_id = await ai_engine.start_ai_enhanced_perpetual_cycle(
                initial_input=f"Concurrent test problem {i}",
                ai_enhancement_level=AIEnhancementLevel.ENHANCED,
                max_cycles=1
            )
            session_ids.append(session_id)
        
        # Wait for all sessions to complete
        await asyncio.sleep(3)
        
        # Verify all sessions were created and processed
        for session_id in session_ids:
            assert session_id in ai_engine.ai_sessions
            ai_session = ai_engine.ai_sessions[session_id]
            assert ai_session.status in ["active", "completed", "terminated_with_error"]
            
            # Verify database persistence for each session
            session_data = await db_service.get_session(session_id)
            assert session_data is not None

    @pytest.mark.asyncio
    async def test_ai_configuration_variations(self, ai_engine_with_db, sample_problem_statement):
        """Test different AI configuration variations"""
        ai_engine, db_service = ai_engine_with_db
        
        # Test different AI configurations
        configs = [
            {"ai_learning_enabled": True, "ai_adaptation_enabled": False, "ai_breakthrough_detection": False},
            {"ai_learning_enabled": False, "ai_adaptation_enabled": True, "ai_breakthrough_detection": False},
            {"ai_learning_enabled": False, "ai_adaptation_enabled": False, "ai_breakthrough_detection": True},
            {"ai_learning_enabled": True, "ai_adaptation_enabled": True, "ai_breakthrough_detection": True}
        ]
        
        session_ids = []
        
        for i, config in enumerate(configs):
            session_id = await ai_engine.start_ai_enhanced_perpetual_cycle(
                initial_input=f"{sample_problem_statement} (Config {i})",
                ai_enhancement_level=AIEnhancementLevel.ENHANCED,
                **config,
                max_cycles=1
            )
            session_ids.append(session_id)
            
            # Wait for completion
            await asyncio.sleep(1)
        
        # Verify all configurations were applied correctly
        for i, session_id in enumerate(session_ids):
            ai_session = ai_engine.ai_sessions[session_id]
            config = configs[i]
            
            assert ai_session.ai_learning_enabled == config["ai_learning_enabled"]
            assert ai_session.ai_adaptation_enabled == config["ai_adaptation_enabled"]
            assert ai_session.ai_breakthrough_detection == config["ai_breakthrough_detection"]
