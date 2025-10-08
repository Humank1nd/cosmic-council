"""
Unit tests for Yellow Honeybee agent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.enterprises.yellow_honeybee import YellowHoneybeeAgent


class TestYellowHoneybeeAgent:
    """Test YellowHoneybeeAgent class."""
    
    def test_agent_initialization(self):
        """Test Yellow Honeybee agent initialization."""
        agent = YellowHoneybeeAgent()
        assert agent is not None
        assert agent.enterprise_type == "yellow_honeybee"
    
    def test_agent_name(self):
        """Test agent name."""
        agent = YellowHoneybeeAgent()
        assert agent.name == "Yellow Honeybee"
    
    @pytest.mark.asyncio
    async def test_develop_method(self):
        """Test development method."""
        agent = YellowHoneybeeAgent()
        
        with patch.object(agent, 'develop') as mock_develop:
            mock_develop.return_value = {"result": "development_complete"}
            result = await agent.develop("test_problem")
            assert result["result"] == "development_complete"
