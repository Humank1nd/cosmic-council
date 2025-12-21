"""
Unit tests for the Perpetual AI Integration system
Tests the AI-enhanced perpetual thinking engine and related components
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
    AIThinkingMode,
    AICycleEnhancement,
    PerpetualAISession
)
from perpetual_thinking_engine import PerpetualCycle, CycleType, CycleStatus, PatternType
from ai_llm_integration import AILLMIntegration, LLMConfig, LLMProvider, LLMModel


class TestPerpetualAIThinkingEngine:
    """Test the Perpetual AI Thinking Engine"""

    @pytest_asyncio.fixture
    async def ai_engine(self):
        """Create a Perpetual AI Thinking Engine for testing"""
        ai_config = LLMConfig(
            provider=LLMProvider.MOCK,
            model=LLMModel.GPT_4,
            temperature=0.7,
            max_tokens=2000
        )
        engine = PerpetualAIThinkingEngine(
            database_url="sqlite:///:memory:",
            ai_config=ai_config
        )
        return engine

    @pytest.fixture
    def sample_initial_input(self):
        """Sample initial input for testing"""
        return "How can we solve global climate change through innovative technology and policy?"

    @pytest.fixture
    def mock_ai_response(self):
        """Mock AI response for testing"""
        return Mock(
            content="Enhanced problem statement with AI insights",
            confidence_score=0.85,
            reasoning="AI reasoning for enhancement",
            tokens_used=150,
            processing_time=1.2,
            metadata={"prompt": "test_prompt"}
        )

    @pytest.mark.asyncio
    async def test_initialization(self, ai_engine):
        """Test AI engine initialization"""
        assert ai_engine.name == "Perpetual AI Thinking Engine"
        assert ai_engine.ai_integration is not None
        assert isinstance(ai_engine.ai_sessions, dict)
        assert len(ai_engine.ai_sessions) == 0

    @pytest.mark.asyncio
    async def test_start_ai_enhanced_perpetual_cycle(self, ai_engine, sample_initial_input):
        """Test starting an AI-enhanced perpetual cycle"""
        session_id = await ai_engine.start_ai_enhanced_perpetual_cycle(
            initial_input=sample_initial_input,
            ai_enhancement_level=AIEnhancementLevel.ENHANCED,
            ai_learning_enabled=True,
            ai_adaptation_enabled=True,
            ai_breakthrough_detection=True
        )
        
        assert session_id is not None
        assert session_id in ai_engine.ai_sessions
        
        ai_session = ai_engine.ai_sessions[session_id]
        assert ai_session.session_name.startswith("AI-Enhanced Session")
        assert ai_session.initial_input == sample_initial_input
        assert ai_session.ai_enhancement_level == AIEnhancementLevel.ENHANCED
        assert ai_session.ai_learning_enabled is True
        assert ai_session.ai_adaptation_enabled is True
        assert ai_session.ai_breakthrough_detection is True

    @pytest.mark.asyncio
    async def test_determine_ai_thinking_mode(self, ai_engine):
        """Test AI thinking mode determination"""
        # Test different cycle types
        assert ai_engine._determine_ai_thinking_mode(CycleType.EXPLORATION, AIEnhancementLevel.ENHANCED) == AIThinkingMode.CREATIVE
        assert ai_engine._determine_ai_thinking_mode(CycleType.CONVERGENCE, AIEnhancementLevel.ENHANCED) == AIThinkingMode.LOGICAL
        assert ai_engine._determine_ai_thinking_mode(CycleType.SYNTHESIS, AIEnhancementLevel.ENHANCED) == AIThinkingMode.CRITICAL
        assert ai_engine._determine_ai_thinking_mode(CycleType.META_REFLECTION, AIEnhancementLevel.ENHANCED) == AIThinkingMode.EMPATHIC
        assert ai_engine._determine_ai_thinking_mode(CycleType.BREAKTHROUGH, AIEnhancementLevel.ENHANCED) == AIThinkingMode.CREATIVE
        assert ai_engine._determine_ai_thinking_mode(CycleType.ADAPTATION, AIEnhancementLevel.ENHANCED) == AIThinkingMode.STRATEGIC
        
        # Test with no enhancement
        assert ai_engine._determine_ai_thinking_mode(CycleType.EXPLORATION, AIEnhancementLevel.NONE) == AIThinkingMode.LOGICAL

    @pytest.mark.asyncio
    async def test_get_ai_enhanced_input(self, ai_engine, sample_initial_input, mock_ai_response):
        """Test AI input enhancement"""
        ai_session = PerpetualAISession(
            session_id=str(uuid.uuid4()),
            session_name="Test Session",
            initial_input=sample_initial_input,
            ai_enhancement_level=AIEnhancementLevel.ENHANCED
        )
        
        ai_context = {
            "problem_statement": sample_initial_input,
            "cycle_number": 1,
            "cycle_type": "exploration",
            "ai_enhancement_level": "enhanced"
        }
        
        with patch.object(ai_engine.ai_integration, 'generate_response', return_value=mock_ai_response):
            enhanced_input, ai_response = await ai_engine._get_ai_enhanced_input(
                ai_session, sample_initial_input, ai_context, AIThinkingMode.CREATIVE
            )
            
            assert enhanced_input == mock_ai_response.content
            assert ai_response == mock_ai_response

    @pytest.mark.asyncio
    async def test_get_ai_enhanced_input_no_enhancement(self, ai_engine, sample_initial_input):
        """Test AI input enhancement with no enhancement level"""
        ai_session = PerpetualAISession(
            session_id=str(uuid.uuid4()),
            session_name="Test Session",
            initial_input=sample_initial_input,
            ai_enhancement_level=AIEnhancementLevel.NONE
        )
        
        ai_context = {"problem_statement": sample_initial_input}
        
        enhanced_input, ai_response = await ai_engine._get_ai_enhanced_input(
            ai_session, sample_initial_input, ai_context, AIThinkingMode.LOGICAL
        )
        
        assert enhanced_input == sample_initial_input
        assert ai_response is None

    @pytest.mark.asyncio
    async def test_adjust_metric_with_ai(self, ai_engine):
        """Test metric adjustment with AI confidence"""
        original_score = 0.7
        ai_confidence = 0.9
        
        # Test different enhancement levels
        assisted_score = ai_engine._adjust_metric_with_ai(original_score, ai_confidence, AIEnhancementLevel.ASSISTED)
        enhanced_score = ai_engine._adjust_metric_with_ai(original_score, ai_confidence, AIEnhancementLevel.ENHANCED)
        autonomous_score = ai_engine._adjust_metric_with_ai(original_score, ai_confidence, AIEnhancementLevel.AUTONOMOUS)
        none_score = ai_engine._adjust_metric_with_ai(original_score, ai_confidence, AIEnhancementLevel.NONE)
        
        assert none_score == original_score
        assert assisted_score == (original_score + ai_confidence) / 2
        assert enhanced_score == (original_score * 0.6 + ai_confidence * 0.4)
        assert autonomous_score == (original_score * 0.4 + ai_confidence * 0.6)

    @pytest.mark.asyncio
    async def test_should_ai_adapt(self, ai_engine):
        """Test AI adaptation decision logic"""
        ai_session = PerpetualAISession(
            session_id=str(uuid.uuid4()),
            session_name="Test Session",
            initial_input="Test input",
            ai_enhancement_level=AIEnhancementLevel.ENHANCED
        )
        
        # Test stagnation scenario
        cycle = PerpetualCycle(
            id=str(uuid.uuid4()),
            cycle_number=1,
            cycle_type=CycleType.EXPLORATION,
            status=CycleStatus.RUNNING,
            input_data="Test input"
        )
        cycle.pattern_type = PatternType.STAGNATION
        cycle.confidence_score = 0.3  # Below threshold
        
        should_adapt = await ai_engine._should_ai_adapt(ai_session, cycle)
        assert should_adapt is True
        
        # Test breakthrough scenario
        cycle.confidence_score = 0.95
        cycle.creativity_score = 0.95
        
        should_adapt = await ai_engine._should_ai_adapt(ai_session, cycle)
        assert should_adapt is True
        
        # Test no adaptation needed
        cycle.confidence_score = 0.7
        cycle.creativity_score = 0.6
        
        should_adapt = await ai_engine._should_ai_adapt(ai_session, cycle)
        assert should_adapt is False

    @pytest.mark.asyncio
    async def test_should_ai_adapt_no_enhancement(self, ai_engine):
        """Test AI adaptation with no enhancement level"""
        ai_session = PerpetualAISession(
            session_id=str(uuid.uuid4()),
            session_name="Test Session",
            initial_input="Test input",
            ai_enhancement_level=AIEnhancementLevel.NONE
        )
        
        cycle = PerpetualCycle(
            id=str(uuid.uuid4()),
            cycle_number=1,
            cycle_type=CycleType.EXPLORATION,
            status=CycleStatus.RUNNING,
            input_data="Test input"
        )
        
        should_adapt = await ai_engine._should_ai_adapt(ai_session, cycle)
        assert should_adapt is False

    @pytest.mark.asyncio
    async def test_get_ai_session_analytics(self, ai_engine):
        """Test AI session analytics retrieval"""
        session_id = str(uuid.uuid4())
        ai_session = PerpetualAISession(
            session_id=session_id,
            session_name="Test Session",
            initial_input="Test input",
            ai_enhancement_level=AIEnhancementLevel.ENHANCED
        )
        
        # Add some mock enhancements
        enhancement1 = AICycleEnhancement(
            cycle_id=str(uuid.uuid4()),
            ai_enhancement_level=AIEnhancementLevel.ENHANCED,
            ai_thinking_mode=AIThinkingMode.CREATIVE,
            ai_prompt_used="test_prompt",
            ai_response_summary="test response",
            ai_confidence=0.8,
            ai_reasoning="test reasoning",
            ai_tokens_used=100,
            ai_processing_time=1.0,
            impact_score=0.75
        )
        
        enhancement2 = AICycleEnhancement(
            cycle_id=str(uuid.uuid4()),
            ai_enhancement_level=AIEnhancementLevel.ENHANCED,
            ai_thinking_mode=AIThinkingMode.LOGICAL,
            ai_prompt_used="test_prompt2",
            ai_response_summary="test response2",
            ai_confidence=0.9,
            ai_reasoning="test reasoning2",
            ai_tokens_used=120,
            ai_processing_time=1.2,
            impact_score=0.85
        )
        
        ai_session.ai_cycle_enhancements = [enhancement1, enhancement2]
        ai_session.ai_session_insights = ["insight1", "insight2"]
        ai_session.ai_learning_history = [{"type": "adaptation", "timestamp": "2024-01-01"}]
        
        ai_engine.ai_sessions[session_id] = ai_session
        
        analytics = await ai_engine.get_ai_session_analytics(session_id)
        
        assert analytics is not None
        assert analytics["session_id"] == session_id
        assert analytics["session_name"] == "Test Session"
        assert analytics["ai_enhancement_level"] == "enhanced"
        assert analytics["total_ai_enhanced_cycles"] == 2
        assert analytics["avg_ai_confidence"] == 0.85  # (0.8 + 0.9) / 2
        assert analytics["avg_impact_score"] == 0.8  # (0.75 + 0.85) / 2
        assert analytics["total_ai_tokens_used"] == 220  # 100 + 120
        assert analytics["total_ai_processing_time_seconds"] == 2.2  # 1.0 + 1.2
        assert analytics["ai_session_insights_count"] == 2
        assert analytics["ai_learning_events_count"] == 1

    @pytest.mark.asyncio
    async def test_get_ai_session_analytics_not_found(self, ai_engine):
        """Test AI session analytics for non-existent session"""
        analytics = await ai_engine.get_ai_session_analytics("non-existent-session")
        assert analytics is None

    @pytest.mark.asyncio
    async def test_get_ai_enhanced_cycle_status(self, ai_engine):
        """Test AI enhanced cycle status retrieval"""
        session_id = str(uuid.uuid4())
        cycle_id = str(uuid.uuid4())
        
        ai_session = PerpetualAISession(
            session_id=session_id,
            session_name="Test Session",
            initial_input="Test input",
            ai_enhancement_level=AIEnhancementLevel.ENHANCED
        )
        ai_session.ai_sessions_history = [cycle_id]
        
        cycle = PerpetualCycle(
            id=cycle_id,
            cycle_number=1,
            cycle_type=CycleType.EXPLORATION,
            status=CycleStatus.RUNNING,
            input_data="Test input"
        )
        cycle.confidence_score = 0.8
        cycle.creativity_score = 0.7
        cycle.wisdom_density = 0.6
        cycle.pattern_type = PatternType.CONVERGENCE
        cycle.processing_time = 2.5
        
        ai_engine.ai_sessions[session_id] = ai_session
        ai_engine.cycles = [cycle]
        
        status = await ai_engine.get_ai_enhanced_cycle_status(session_id)
        
        assert status is not None
        assert status["session_id"] == session_id
        assert status["cycle_id"] == cycle_id
        assert status["cycle_number"] == 1
        assert status["cycle_type"] == "exploration"
        assert status["status"] == "running"
        assert status["confidence_score"] == 0.8
        assert status["creativity_score"] == 0.7
        assert status["wisdom_density"] == 0.6
        assert status["pattern_type"] == "convergence"
        assert status["processing_time"] == 2.5
        assert status["ai_enhancement_level"] == "enhanced"

    @pytest.mark.asyncio
    async def test_get_ai_enhanced_cycle_status_not_found(self, ai_engine):
        """Test AI enhanced cycle status for non-existent session"""
        status = await ai_engine.get_ai_enhanced_cycle_status("non-existent-session")
        assert status is None


class TestAICycleEnhancement:
    """Test the AICycleEnhancement dataclass"""

    def test_ai_cycle_enhancement_creation(self):
        """Test AICycleEnhancement creation"""
        enhancement = AICycleEnhancement(
            cycle_id="test-cycle-id",
            ai_enhancement_level=AIEnhancementLevel.ENHANCED,
            ai_thinking_mode=AIThinkingMode.CREATIVE,
            ai_prompt_used="test prompt",
            ai_response_summary="test response",
            ai_confidence=0.85,
            ai_reasoning="test reasoning",
            ai_tokens_used=150,
            ai_processing_time=1.5
        )
        
        assert enhancement.cycle_id == "test-cycle-id"
        assert enhancement.ai_enhancement_level == AIEnhancementLevel.ENHANCED
        assert enhancement.ai_thinking_mode == AIThinkingMode.CREATIVE
        assert enhancement.ai_prompt_used == "test prompt"
        assert enhancement.ai_response_summary == "test response"
        assert enhancement.ai_confidence == 0.85
        assert enhancement.ai_reasoning == "test reasoning"
        assert enhancement.ai_tokens_used == 150
        assert enhancement.ai_processing_time == 1.5
        assert enhancement.impact_score == 0.0  # Default value
        assert enhancement.learning_feedback is None  # Default value
        assert enhancement.enhancement_id is not None  # Auto-generated


class TestPerpetualAISession:
    """Test the PerpetualAISession dataclass"""

    def test_perpetual_ai_session_creation(self):
        """Test PerpetualAISession creation"""
        session = PerpetualAISession(
            session_id="test-session-id",
            session_name="Test Session",
            initial_input="Test input",
            ai_enhancement_level=AIEnhancementLevel.ENHANCED,
            ai_learning_enabled=True,
            ai_adaptation_enabled=True,
            ai_breakthrough_detection=True
        )
        
        assert session.session_id == "test-session-id"
        assert session.session_name == "Test Session"
        assert session.initial_input == "Test input"
        assert session.ai_enhancement_level == AIEnhancementLevel.ENHANCED
        assert session.ai_learning_enabled is True
        assert session.ai_adaptation_enabled is True
        assert session.ai_breakthrough_detection is True
        assert session.status == "active"  # Default value
        assert isinstance(session.ai_sessions_history, list)
        assert isinstance(session.ai_cycle_enhancements, list)
        assert isinstance(session.ai_session_insights, list)
        assert isinstance(session.ai_learning_history, list)
        assert session.created_at is not None
        assert session.updated_at is not None


class TestAIEnhancementLevel:
    """Test the AIEnhancementLevel enum"""

    def test_ai_enhancement_level_values(self):
        """Test AIEnhancementLevel enum values"""
        assert AIEnhancementLevel.NONE.value == "none"
        assert AIEnhancementLevel.ASSISTED.value == "assisted"
        assert AIEnhancementLevel.ENHANCED.value == "enhanced"
        assert AIEnhancementLevel.AUTONOMOUS.value == "autonomous"


class TestAIThinkingMode:
    """Test the AIThinkingMode enum"""

    def test_ai_thinking_mode_values(self):
        """Test AIThinkingMode enum values"""
        assert AIThinkingMode.CREATIVE.value == "creative"
        assert AIThinkingMode.LOGICAL.value == "logical"
        assert AIThinkingMode.CRITICAL.value == "critical"
        assert AIThinkingMode.EMPATHIC.value == "empathic"
        assert AIThinkingMode.STRATEGIC.value == "strategic"
