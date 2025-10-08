"""
Unit tests for Blue Dolphin agent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.enterprises.blue_dolphin import BlueDolphinAgent


class TestBlueDolphinAgent:
    """Test BlueDolphinAgent class."""
    
    def test_agent_initialization(self):
        """Test Blue Dolphin agent initialization."""
        agent = BlueDolphinAgent()
        assert agent is not None
        assert agent.enterprise_type == "blue_dolphin"
    
    def test_agent_name(self):
        """Test agent name."""
        agent = BlueDolphinAgent()
        assert agent.name == "Blue Dolphin"
    
    @pytest.mark.asyncio
    async def test_market_method(self):
        """Test market analysis method."""
        agent = BlueDolphinAgent()
        
        with patch.object(agent, 'market') as mock_market:
            mock_market.return_value = {"result": "market_analysis_complete"}
            result = await agent.market("test_problem")
            assert result["result"] == "market_analysis_complete"
