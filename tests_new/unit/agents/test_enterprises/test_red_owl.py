"""
Unit tests for Red Owl agent.
"""

import pytest
from unittest.mock import Mock, patch
from src.agents.enterprises.red_owl import RedOwlAgent


class TestRedOwlAgent:
    """Test RedOwlAgent class."""
    
    def test_agent_initialization(self):
        """Test Red Owl agent initialization."""
        agent = RedOwlAgent()
        assert agent is not None
        assert agent.enterprise_type == "red_owl"
    
    def test_agent_name(self):
        """Test agent name."""
        agent = RedOwlAgent()
        assert agent.name == "Red Owl"
    
    @pytest.mark.asyncio
    async def test_research_method(self):
        """Test research method."""
        agent = RedOwlAgent()
        # Mock the research implementation
        with patch.object(agent, 'research') as mock_research:
            mock_research.return_value = {"result": "research_complete"}
            result = await agent.research("test_problem")
            assert result["result"] == "research_complete"
