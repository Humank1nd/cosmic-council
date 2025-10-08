"""
Unit tests for Green Tortoise agent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.enterprises.green_tortoise import GreenTortoiseAgent


class TestGreenTortoiseAgent:
    """Test GreenTortoiseAgent class."""
    
    def test_agent_initialization(self):
        """Test Green Tortoise agent initialization."""
        agent = GreenTortoiseAgent()
        assert agent is not None
        assert agent.enterprise_type == "green_tortoise"
    
    def test_agent_name(self):
        """Test agent name."""
        agent = GreenTortoiseAgent()
        assert agent.name == "Green Tortoise"
    
    @pytest.mark.asyncio
    async def test_budget_method(self):
        """Test budgeting method."""
        agent = GreenTortoiseAgent()
        
        with patch.object(agent, 'budget') as mock_budget:
            mock_budget.return_value = {"result": "budget_complete"}
            result = await agent.budget("test_problem")
            assert result["result"] == "budget_complete"
