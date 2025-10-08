"""
Unit tests for Orange Orangutan agent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.enterprises.orange_orangutan import OrangeOrangutanAgent


class TestOrangeOrangutanAgent:
    """Test OrangeOrangutanAgent class."""
    
    def test_agent_initialization(self):
        """Test Orange Orangutan agent initialization."""
        agent = OrangeOrangutanAgent()
        assert agent is not None
        assert agent.enterprise_type == "orange_orangutan"
    
    def test_agent_name(self):
        """Test agent name."""
        agent = OrangeOrangutanAgent()
        assert agent.name == "Orange Orangutan"
    
    @pytest.mark.asyncio
    async def test_plan_method(self):
        """Test planning method."""
        agent = OrangeOrangutanAgent()
        
        with patch.object(agent, 'plan') as mock_plan:
            mock_plan.return_value = {"result": "plan_complete"}
            result = await agent.plan("test_problem")
            assert result["result"] == "plan_complete"
