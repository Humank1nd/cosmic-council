"""
Unit tests for agent orchestration coordinator.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agents.orchestration.coordinator import AgentCoordinator


class TestAgentCoordinator:
    """Test AgentCoordinator class."""
    
    def test_coordinator_initialization(self):
        """Test coordinator initialization."""
        coordinator = AgentCoordinator()
        assert coordinator is not None
    
    @pytest.mark.asyncio
    async def test_coordinate_agents(self):
        """Test agent coordination."""
        coordinator = AgentCoordinator()
        
        with patch.object(coordinator, 'agents') as mock_agents:
            mock_agents.items.return_value = [
                ("red_owl", Mock()),
                ("orange_orangutan", Mock())
            ]
            
            result = await coordinator.coordinate_agents("test_problem")
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_execute_workflow(self):
        """Test workflow execution."""
        coordinator = AgentCoordinator()
        
        with patch.object(coordinator, 'coordinate_agents') as mock_coordinate:
            mock_coordinate.return_value = {"status": "success"}
            
            result = await coordinator.execute_workflow("test_problem")
            assert result["status"] == "success"
