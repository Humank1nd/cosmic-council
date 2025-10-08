"""
Agent coordinator for orchestrating enterprise agents in the Cosmic Council system.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import logging

from ..base.agent import BaseAgent
from ..base.communication import AgentCommunicationHub, AgentCollaboration
from ..enterprises import (
    RedOwlAgent, OrangeOrangutanAgent, YellowHoneybeeAgent,
    GreenTortoiseAgent, BlueDolphinAgent, PurpleElephantAgent
)
from ...core.types import EnterpriseType, CycleStatus
from ...core.models.cycle import Cycle

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Coordinates the execution of enterprise agents"""
    
    def __init__(self):
        self.agents: Dict[EnterpriseType, BaseAgent] = {}
        self.communication_hub = AgentCommunicationHub()
        self.collaboration = AgentCollaboration(self.communication_hub)
        self.active_cycles: Dict[str, Cycle] = {}
        self.logger = logger
        
        # Initialize enterprise agents
        self._initialize_agents()
    
    def _initialize_agents(self) -> None:
        """Initialize all enterprise agents"""
        try:
            # Create enterprise agents
            self.agents[EnterpriseType.RED_OWL] = RedOwlAgent()
            self.agents[EnterpriseType.ORANGE_ORANGUTAN] = OrangeOrangutanAgent()
            self.agents[EnterpriseType.YELLOW_HONEYBEE] = YellowHoneybeeAgent()
            self.agents[EnterpriseType.GREEN_TORTOISE] = GreenTortoiseAgent()
            self.agents[EnterpriseType.BLUE_DOLPHIN] = BlueDolphinAgent()
            self.agents[EnterpriseType.PURPLE_ELEPHANT] = PurpleElephantAgent()
            
            # Register agents with communication hub
            for agent in self.agents.values():
                self.communication_hub.register_agent(agent)
            
            self.logger.info("All enterprise agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing agents: {e}")
            raise
    
    async def execute_cycle(self, cycle: Cycle) -> Dict[str, Any]:
        """Execute a complete problem-solving cycle"""
        try:
            self.logger.info(f"Starting cycle execution: {cycle.id}")
            
            # Store active cycle
            self.active_cycles[cycle.id] = cycle
            
            # Start the cycle
            cycle.start()
            
            # Execute each enterprise in sequence
            cycle_results = {}
            for enterprise_type in cycle.enterprises:
                try:
                    self.logger.info(f"Executing enterprise: {enterprise_type.value}")
                    
                    # Update current enterprise
                    cycle.current_enterprise = enterprise_type
                    
                    # Execute enterprise
                    result = await self._execute_enterprise(cycle, enterprise_type)
                    cycle_results[enterprise_type.value] = result
                    
                    # Update cycle results
                    cycle.results[enterprise_type.value] = result
                    
                except Exception as e:
                    self.logger.error(f"Error executing enterprise {enterprise_type}: {e}")
                    cycle.fail(f"Enterprise {enterprise_type} failed: {str(e)}")
                    return {
                        'cycle_id': cycle.id,
                        'status': 'failed',
                        'error': str(e),
                        'results': cycle_results
                    }
            
            # Complete the cycle
            cycle.complete()
            
            # Remove from active cycles
            if cycle.id in self.active_cycles:
                del self.active_cycles[cycle.id]
            
            self.logger.info(f"Cycle completed successfully: {cycle.id}")
            
            return {
                'cycle_id': cycle.id,
                'status': 'completed',
                'results': cycle_results,
                'completed_at': cycle.completed_at.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error executing cycle {cycle.id}: {e}")
            cycle.fail(str(e))
            return {
                'cycle_id': cycle.id,
                'status': 'failed',
                'error': str(e)
            }
    
    async def _execute_enterprise(self, cycle: Cycle, enterprise_type: EnterpriseType) -> Dict[str, Any]:
        """Execute a specific enterprise"""
        try:
            agent = self.agents.get(enterprise_type)
            if not agent:
                raise ValueError(f"Agent not found for enterprise: {enterprise_type}")
            
            # Prepare input data for the enterprise
            input_data = self._prepare_enterprise_input(cycle, enterprise_type)
            
            # Execute the agent
            result = await agent.execute(input_data)
            
            return {
                'enterprise_type': enterprise_type.value,
                'agent_id': agent.agent_id,
                'result': result,
                'execution_time': 1.0,  # Placeholder
                'success': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error executing enterprise {enterprise_type}: {e}")
            return {
                'enterprise_type': enterprise_type.value,
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _prepare_enterprise_input(self, cycle: Cycle, enterprise_type: EnterpriseType) -> Dict[str, Any]:
        """Prepare input data for a specific enterprise"""
        base_input = {
            'cycle_id': cycle.id,
            'problem_id': cycle.problem_id,
            'enterprise_type': enterprise_type.value,
            'previous_results': cycle.results
        }
        
        # Add enterprise-specific input based on type
        if enterprise_type == EnterpriseType.RED_OWL:
            base_input.update({
                'problem_description': 'Problem to be researched',
                'research_scope': 'Comprehensive analysis required'
            })
        elif enterprise_type == EnterpriseType.ORANGE_ORANGUTAN:
            base_input.update({
                'research_findings': cycle.results.get('red_owl', {}).get('result', {}),
                'objectives': ['Create comprehensive plan', 'Identify dependencies']
            })
        elif enterprise_type == EnterpriseType.YELLOW_HONEYBEE:
            base_input.update({
                'action_plan': cycle.results.get('orange_orangutan', {}).get('result', {}),
                'requirements': ['Implement solution', 'Ensure quality']
            })
        elif enterprise_type == EnterpriseType.GREEN_TORTOISE:
            base_input.update({
                'project_scope': cycle.results.get('yellow_honeybee', {}).get('result', {}),
                'budget_constraints': {'max_budget': 100000}
            })
        elif enterprise_type == EnterpriseType.BLUE_DOLPHIN:
            base_input.update({
                'solution_description': cycle.results.get('yellow_honeybee', {}).get('result', {}),
                'target_audience': 'End users and stakeholders'
            })
        elif enterprise_type == EnterpriseType.PURPLE_ELEPHANT:
            base_input.update({
                'solution_output': cycle.results.get('yellow_honeybee', {}).get('result', {}),
                'user_feedback': ['Positive feedback', 'Some improvement suggestions']
            })
        
        return base_input
    
    async def start_collaboration(self, collaboration_id: str, enterprise_types: List[EnterpriseType], goal: str) -> bool:
        """Start a collaboration between specific enterprises"""
        try:
            # Get agent IDs for the enterprises
            agent_ids = [self.agents[et].agent_id for et in enterprise_types if et in self.agents]
            
            if not agent_ids:
                self.logger.error("No valid agents found for collaboration")
                return False
            
            # Start collaboration
            success = await self.collaboration.start_collaboration(collaboration_id, agent_ids, goal)
            
            if success:
                self.logger.info(f"Started collaboration {collaboration_id} with {len(agent_ids)} agents")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error starting collaboration: {e}")
            return False
    
    async def end_collaboration(self, collaboration_id: str, results: Dict[str, Any]) -> bool:
        """End a collaboration"""
        try:
            success = await self.collaboration.end_collaboration(collaboration_id, results)
            
            if success:
                self.logger.info(f"Ended collaboration {collaboration_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error ending collaboration: {e}")
            return False
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            'agents': self.communication_hub.get_agent_status(),
            'active_cycles': len(self.active_cycles),
            'collaborations': len(self.collaboration.get_all_collaborations())
        }
    
    def get_cycle_status(self, cycle_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific cycle"""
        cycle = self.active_cycles.get(cycle_id)
        if cycle:
            return {
                'cycle_id': cycle.id,
                'status': cycle.status.value,
                'current_enterprise': cycle.current_enterprise.value if cycle.current_enterprise else None,
                'enterprises': [e.value for e in cycle.enterprises],
                'results': cycle.results,
                'started_at': cycle.started_at.isoformat() if cycle.started_at else None,
                'updated_at': cycle.updated_at.isoformat()
            }
        return None
    
    async def pause_cycle(self, cycle_id: str) -> bool:
        """Pause a running cycle"""
        try:
            cycle = self.active_cycles.get(cycle_id)
            if not cycle:
                self.logger.error(f"Cycle not found: {cycle_id}")
                return False
            
            if cycle.status != CycleStatus.RUNNING:
                self.logger.error(f"Cannot pause cycle in status: {cycle.status}")
                return False
            
            cycle.status = CycleStatus.PAUSED
            cycle.updated_at = datetime.utcnow()
            
            self.logger.info(f"Paused cycle: {cycle_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error pausing cycle {cycle_id}: {e}")
            return False
    
    async def resume_cycle(self, cycle_id: str) -> bool:
        """Resume a paused cycle"""
        try:
            cycle = self.active_cycles.get(cycle_id)
            if not cycle:
                self.logger.error(f"Cycle not found: {cycle_id}")
                return False
            
            if cycle.status != CycleStatus.PAUSED:
                self.logger.error(f"Cannot resume cycle in status: {cycle.status}")
                return False
            
            cycle.status = CycleStatus.RUNNING
            cycle.updated_at = datetime.utcnow()
            
            self.logger.info(f"Resumed cycle: {cycle_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resuming cycle {cycle_id}: {e}")
            return False
    
    async def cancel_cycle(self, cycle_id: str) -> bool:
        """Cancel a cycle"""
        try:
            cycle = self.active_cycles.get(cycle_id)
            if not cycle:
                self.logger.error(f"Cycle not found: {cycle_id}")
                return False
            
            if cycle.status in [CycleStatus.COMPLETED, CycleStatus.FAILED]:
                self.logger.error(f"Cannot cancel cycle in status: {cycle.status}")
                return False
            
            cycle.status = CycleStatus.FAILED
            cycle.completed_at = datetime.utcnow()
            cycle.update_metadata('cancelled', True)
            
            # Remove from active cycles
            if cycle_id in self.active_cycles:
                del self.active_cycles[cycle_id]
            
            self.logger.info(f"Cancelled cycle: {cycle_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling cycle {cycle_id}: {e}")
            return False
