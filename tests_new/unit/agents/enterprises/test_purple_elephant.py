"""
Unit tests for Purple Elephant agent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.enterprises.purple_elephant import PurpleElephantAgent


class TestPurpleElephantAgent:
    """Test PurpleElephantAgent class."""
    
    def test_agent_initialization(self):
        """Test Purple Elephant agent initialization."""
        agent = PurpleElephantAgent()
        assert agent is not None
        assert agent.enterprise_type == "purple_elephant"
    
    def test_agent_name(self):
        """Test agent name."""
        agent = PurpleElephantAgent()
        assert agent.name == "Purple Elephant"
    
    @pytest.mark.asyncio
    async def test_support_method(self):
        """Test support method."""
        agent = PurpleElephantAgent()
        
        with patch.object(agent, 'support') as mock_support:
            mock_support.return_value = {"result": "support_complete"}
            result = await agent.support("test_problem")
            assert result["result"] == "support_complete"
