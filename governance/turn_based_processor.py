"""
Cosmic Council Turn-Based Processor
Implements the strict linear flow and fractal recursion mechanics
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class TurnStatus(Enum):
    """Turn status for each stage"""
    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"

class VictoryCondition(Enum):
    """Victory conditions for cycle completion"""
    SOLVED = "solved"
    EVOLVED = "evolved"
    ESCALATED = "escalated"

class ActionType(Enum):
    """Action types for each stage"""
    QUERY = "query"           # Red Owl
    PLAN = "plan"             # Orange Orangutan
    PROTOTYPE = "prototype"   # Yellow Honeybee
    ALLOCATE = "allocate"     # Green Tortoise
    COMMUNICATE = "communicate" # Blue Dolphin
    REFLECT = "reflect"       # Violet Elephant

@dataclass
class ActionPoint:
    """Represents an action point for a stage"""
    action_type: ActionType
    stage: str
    description: str
    energy_cost: int
    max_uses: int
    current_uses: int = 0

@dataclass
class Turn:
    """Represents a turn in the Cosmic Council process"""
    turn_id: str
    cycle_id: str
    stage: str
    status: TurnStatus
    action_points: List[ActionPoint]
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    energy_budget: int
    energy_used: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    feedback_score: Optional[float] = None
    notes: str = ""

@dataclass
class Cycle:
    """Represents a complete Cosmic Council cycle"""
    cycle_id: str
    problem_statement: str
    turns: List[Turn]
    current_turn_index: int
    victory_condition: Optional[VictoryCondition]
    feedback_for_next_cycle: str
    is_sub_council: bool
    parent_cycle_id: Optional[str]
    sub_councils: List[str]
    created_at: datetime
    completed_at: Optional[datetime] = None

class CosmicCouncilTurnBasedProcessor:
    """
    Turn-based processor that enforces strict linear flow and fractal recursion
    """
    
    def __init__(self):
        self.active_cycles: Dict[str, Cycle] = {}
        self.completed_cycles: Dict[str, Cycle] = {}
        self.sub_council_registry: Dict[str, List[str]] = {}  # parent_cycle_id -> sub_council_ids
        
        # Define action points for each stage
        self.stage_action_points = {
            "research": [
                ActionPoint(ActionType.QUERY, "research", "Query external sources", 2, 5),
                ActionPoint(ActionType.QUERY, "research", "Analyze data patterns", 3, 3),
                ActionPoint(ActionType.QUERY, "research", "Define problem scope", 1, 1)
            ],
            "planning": [
                ActionPoint(ActionType.PLAN, "planning", "Create action plan", 2, 1),
                ActionPoint(ActionType.PLAN, "planning", "Identify dependencies", 1, 3),
                ActionPoint(ActionType.PLAN, "planning", "Set timelines", 1, 2)
            ],
            "development": [
                ActionPoint(ActionType.PROTOTYPE, "development", "Create prototype", 4, 2),
                ActionPoint(ActionType.PROTOTYPE, "development", "Test solution", 2, 3),
                ActionPoint(ActionType.PROTOTYPE, "development", "Iterate design", 3, 2)
            ],
            "budget": [
                ActionPoint(ActionType.ALLOCATE, "budget", "Allocate resources", 2, 1),
                ActionPoint(ActionType.ALLOCATE, "budget", "Calculate costs", 1, 2),
                ActionPoint(ActionType.ALLOCATE, "budget", "Optimize budget", 2, 1)
            ],
            "market": [
                ActionPoint(ActionType.COMMUNICATE, "market", "Develop strategy", 2, 1),
                ActionPoint(ActionType.COMMUNICATE, "market", "Create messaging", 1, 2),
                ActionPoint(ActionType.COMMUNICATE, "market", "Engage audience", 3, 2)
            ],
            "support": [
                ActionPoint(ActionType.REFLECT, "support", "Collect feedback", 2, 2),
                ActionPoint(ActionType.REFLECT, "support", "Assess performance", 1, 1),
                ActionPoint(ActionType.REFLECT, "support", "Generate improvements", 2, 1)
            ]
        }
        
        # ROYGBV sequence
        self.roygbv_sequence = ["research", "planning", "development", "budget", "market", "support"]
        
        logger.info("Cosmic Council Turn-Based Processor initialized")

    async def start_new_cycle(self, 
                            problem_statement: str,
                            energy_budget: int = 100,
                            is_sub_council: bool = False,
                            parent_cycle_id: Optional[str] = None) -> str:
        """
        Start a new Cosmic Council cycle
        
        Args:
            problem_statement: The problem to be solved
            energy_budget: Total energy budget for the cycle
            is_sub_council: Whether this is a sub-council
            parent_cycle_id: ID of parent cycle if this is a sub-council
            
        Returns:
            cycle_id: UUID of the created cycle
        """
        cycle_id = str(uuid.uuid4())
        
        # Create initial turn for Red Owl (Research)
        initial_turn = Turn(
            turn_id=str(uuid.uuid4()),
            cycle_id=cycle_id,
            stage="research",
            status=TurnStatus.ACTIVE,
            action_points=self.stage_action_points["research"].copy(),
            input_data={"problem_statement": problem_statement},
            output_data={},
            energy_budget=energy_budget,
            energy_used=0,
            started_at=datetime.now(timezone.utc)
        )
        
        # Create cycle
        cycle = Cycle(
            cycle_id=cycle_id,
            problem_statement=problem_statement,
            turns=[initial_turn],
            current_turn_index=0,
            victory_condition=None,
            feedback_for_next_cycle="",
            is_sub_council=is_sub_council,
            parent_cycle_id=parent_cycle_id,
            sub_councils=[],
            created_at=datetime.now(timezone.utc)
        )
        
        self.active_cycles[cycle_id] = cycle
        
        # Register sub-council if applicable
        if is_sub_council and parent_cycle_id:
            if parent_cycle_id not in self.sub_council_registry:
                self.sub_council_registry[parent_cycle_id] = []
            self.sub_council_registry[parent_cycle_id].append(cycle_id)
        
        logger.info(f"Started new cycle {cycle_id}: {problem_statement}")
        return cycle_id

    async def execute_turn(self, 
                         cycle_id: str,
                         action_type: ActionType,
                         action_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a turn in the current cycle
        
        Args:
            cycle_id: ID of the cycle
            action_type: Type of action to execute
            action_data: Data for the action
            
        Returns:
            Result of the turn execution
        """
        if cycle_id not in self.active_cycles:
            raise ValueError(f"Cycle {cycle_id} not found or not active")
        
        cycle = self.active_cycles[cycle_id]
        current_turn = cycle.turns[cycle.current_turn_index]
        
        # Validate turn is active
        if current_turn.status != TurnStatus.ACTIVE:
            raise ValueError(f"Turn {current_turn.turn_id} is not active")
        
        # Find the action point
        action_point = None
        for ap in current_turn.action_points:
            if ap.action_type == action_type and ap.current_uses < ap.max_uses:
                action_point = ap
                break
        
        if not action_point:
            raise ValueError(f"Action {action_type.value} not available or exhausted")
        
        # Check energy budget
        if current_turn.energy_used + action_point.energy_cost > current_turn.energy_budget:
            raise ValueError(f"Insufficient energy budget for action {action_type.value}")
        
        # Execute the action
        try:
            result = await self._execute_action(action_type, action_data, current_turn)
            
            # Update action point usage
            action_point.current_uses += 1
            current_turn.energy_used += action_point.energy_cost
            
            # Update turn output data
            current_turn.output_data.update(result)
            
            # Check if turn is complete
            if await self._is_turn_complete(current_turn):
                await self._complete_turn(cycle, current_turn)
            
            return {
                'success': True,
                'result': result,
                'energy_remaining': current_turn.energy_budget - current_turn.energy_used,
                'action_points_remaining': sum(ap.max_uses - ap.current_uses for ap in current_turn.action_points)
            }
            
        except Exception as e:
            logger.error(f"Error executing action {action_type.value}: {e}")
            current_turn.status = TurnStatus.FAILED
            return {
                'success': False,
                'error': str(e),
                'turn_status': current_turn.status.value
            }

    async def _execute_action(self, 
                            action_type: ActionType,
                            action_data: Dict[str, Any],
                            turn: Turn) -> Dict[str, Any]:
        """Execute a specific action type"""
        
        if action_type == ActionType.QUERY:
            return await self._execute_query_action(action_data, turn)
        elif action_type == ActionType.PLAN:
            return await self._execute_plan_action(action_data, turn)
        elif action_type == ActionType.PROTOTYPE:
            return await self._execute_prototype_action(action_data, turn)
        elif action_type == ActionType.ALLOCATE:
            return await self._execute_allocate_action(action_data, turn)
        elif action_type == ActionType.COMMUNICATE:
            return await self._execute_communicate_action(action_data, turn)
        elif action_type == ActionType.REFLECT:
            return await self._execute_reflect_action(action_data, turn)
        else:
            raise ValueError(f"Unknown action type: {action_type}")

    async def _execute_query_action(self, action_data: Dict[str, Any], turn: Turn) -> Dict[str, Any]:
        """Execute query action for Red Owl"""
        query_type = action_data.get('query_type', 'general')
        query_data = action_data.get('query_data', {})
        
        # Simulate query execution
        result = {
            'query_type': query_type,
            'findings': f"Research findings for {query_type}",
            'confidence': 0.85,
            'sources': ['source1', 'source2', 'source3'],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return result

    async def _execute_plan_action(self, action_data: Dict[str, Any], turn: Turn) -> Dict[str, Any]:
        """Execute plan action for Orange Orangutan"""
        plan_type = action_data.get('plan_type', 'general')
        plan_data = action_data.get('plan_data', {})
        
        # Simulate planning execution
        result = {
            'plan_type': plan_type,
            'action_plan': f"Action plan for {plan_type}",
            'timeline': '30 days',
            'dependencies': ['dep1', 'dep2'],
            'resources_needed': ['resource1', 'resource2'],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return result

    async def _execute_prototype_action(self, action_data: Dict[str, Any], turn: Turn) -> Dict[str, Any]:
        """Execute prototype action for Yellow Honeybee"""
        prototype_type = action_data.get('prototype_type', 'general')
        prototype_data = action_data.get('prototype_data', {})
        
        # Simulate prototyping execution
        result = {
            'prototype_type': prototype_type,
            'prototype_description': f"Prototype for {prototype_type}",
            'test_results': {'performance': 0.9, 'usability': 0.8},
            'iterations': 3,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return result

    async def _execute_allocate_action(self, action_data: Dict[str, Any], turn: Turn) -> Dict[str, Any]:
        """Execute allocate action for Green Tortoise"""
        allocation_type = action_data.get('allocation_type', 'general')
        allocation_data = action_data.get('allocation_data', {})
        
        # Simulate allocation execution
        result = {
            'allocation_type': allocation_type,
            'budget_allocation': {'development': 40, 'testing': 30, 'deployment': 30},
            'resource_plan': f"Resource plan for {allocation_type}",
            'cost_analysis': {'total_cost': 10000, 'cost_per_unit': 100},
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return result

    async def _execute_communicate_action(self, action_data: Dict[str, Any], turn: Turn) -> Dict[str, Any]:
        """Execute communicate action for Blue Dolphin"""
        communication_type = action_data.get('communication_type', 'general')
        communication_data = action_data.get('communication_data', {})
        
        # Simulate communication execution
        result = {
            'communication_type': communication_type,
            'strategy': f"Communication strategy for {communication_type}",
            'target_audience': 'stakeholders',
            'channels': ['email', 'meeting', 'documentation'],
            'metrics': {'reach': 100, 'engagement': 0.75},
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return result

    async def _execute_reflect_action(self, action_data: Dict[str, Any], turn: Turn) -> Dict[str, Any]:
        """Execute reflect action for Violet Elephant"""
        reflection_type = action_data.get('reflection_type', 'general')
        reflection_data = action_data.get('reflection_data', {})
        
        # Simulate reflection execution
        result = {
            'reflection_type': reflection_type,
            'feedback_summary': f"Feedback summary for {reflection_type}",
            'performance_score': 0.85,
            'improvements': ['improvement1', 'improvement2'],
            'next_cycle_focus': 'Focus on user experience',
            'victory_condition': 'solved',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return result

    async def _is_turn_complete(self, turn: Turn) -> bool:
        """Check if a turn is complete"""
        # Check if all action points are exhausted
        all_exhausted = all(ap.current_uses >= ap.max_uses for ap in turn.action_points)
        
        # Check if energy budget is exhausted
        energy_exhausted = turn.energy_used >= turn.energy_budget
        
        # Check if output data indicates completion
        output_complete = 'victory_condition' in turn.output_data
        
        return all_exhausted or energy_exhausted or output_complete

    async def _complete_turn(self, cycle: Cycle, turn: Turn):
        """Complete a turn and advance to the next stage"""
        turn.status = TurnStatus.COMPLETED
        turn.completed_at = datetime.now(timezone.utc)
        
        # Calculate feedback score
        turn.feedback_score = await self._calculate_feedback_score(turn)
        
        # Check if cycle is complete (reached Purple Elephant)
        if turn.stage == "support":
            await self._complete_cycle(cycle, turn)
        else:
            # Advance to next stage
            await self._advance_to_next_stage(cycle, turn)

    async def _advance_to_next_stage(self, cycle: Cycle, completed_turn: Turn):
        """Advance to the next stage in ROYGBV sequence"""
        current_index = self.roygbv_sequence.index(completed_turn.stage)
        next_index = (current_index + 1) % len(self.roygbv_sequence)
        next_stage = self.roygbv_sequence[next_index]
        
        # Create new turn for next stage
        next_turn = Turn(
            turn_id=str(uuid.uuid4()),
            cycle_id=cycle.cycle_id,
            stage=next_stage,
            status=TurnStatus.ACTIVE,
            action_points=self.stage_action_points[next_stage].copy(),
            input_data=completed_turn.output_data,  # Pass output as input
            output_data={},
            energy_budget=completed_turn.energy_budget - completed_turn.energy_used,
            energy_used=0,
            started_at=datetime.now(timezone.utc)
        )
        
        cycle.turns.append(next_turn)
        cycle.current_turn_index += 1
        
        logger.info(f"Advanced cycle {cycle.cycle_id} to {next_stage} stage")

    async def _complete_cycle(self, cycle: Cycle, final_turn: Turn):
        """Complete a cycle and determine victory condition"""
        cycle.completed_at = datetime.now(timezone.utc)
        
        # Determine victory condition from final turn
        victory_condition = VictoryCondition(final_turn.output_data.get('victory_condition', 'solved'))
        cycle.victory_condition = victory_condition
        
        # Generate feedback for next cycle
        cycle.feedback_for_next_cycle = final_turn.output_data.get('next_cycle_focus', 'Continue improvement')
        
        # Move to completed cycles
        self.completed_cycles[cycle.cycle_id] = cycle
        del self.active_cycles[cycle.cycle_id]
        
        logger.info(f"Completed cycle {cycle.cycle_id} with victory condition: {victory_condition.value}")

    async def _calculate_feedback_score(self, turn: Turn) -> float:
        """Calculate feedback score for a turn"""
        # Simple scoring based on energy efficiency and output quality
        energy_efficiency = 1.0 - (turn.energy_used / turn.energy_budget)
        output_quality = len(turn.output_data) / 10.0  # Normalize output data
        
        return min(1.0, (energy_efficiency + output_quality) / 2.0)

    async def create_sub_council(self, 
                               parent_cycle_id: str,
                               sub_problem: str,
                               energy_budget: int = 50) -> str:
        """Create a sub-council to handle a sub-problem"""
        
        if parent_cycle_id not in self.active_cycles:
            raise ValueError(f"Parent cycle {parent_cycle_id} not found")
        
        # Create sub-council cycle
        sub_cycle_id = await self.start_new_cycle(
            problem_statement=sub_problem,
            energy_budget=energy_budget,
            is_sub_council=True,
            parent_cycle_id=parent_cycle_id
        )
        
        # Register with parent cycle
        parent_cycle = self.active_cycles[parent_cycle_id]
        parent_cycle.sub_councils.append(sub_cycle_id)
        
        logger.info(f"Created sub-council {sub_cycle_id} for parent cycle {parent_cycle_id}")
        return sub_cycle_id

    async def escalate_cycle(self, cycle_id: str, escalation_reason: str) -> str:
        """Escalate a cycle to a higher-order council"""
        
        if cycle_id not in self.active_cycles:
            raise ValueError(f"Cycle {cycle_id} not found")
        
        cycle = self.active_cycles[cycle_id]
        
        # Mark current turn as escalated
        current_turn = cycle.turns[cycle.current_turn_index]
        current_turn.status = TurnStatus.ESCALATED
        current_turn.notes = f"Escalated: {escalation_reason}"
        
        # Complete cycle with escalation victory condition
        cycle.victory_condition = VictoryCondition.ESCALATED
        cycle.completed_at = datetime.now(timezone.utc)
        cycle.feedback_for_next_cycle = f"Escalated due to: {escalation_reason}"
        
        # Move to completed cycles
        self.completed_cycles[cycle_id] = cycle
        del self.active_cycles[cycle_id]
        
        logger.info(f"Escalated cycle {cycle_id}: {escalation_reason}")
        return cycle_id

    async def get_cycle_status(self, cycle_id: str) -> Dict[str, Any]:
        """Get status of a cycle"""
        
        # Check active cycles first
        if cycle_id in self.active_cycles:
            cycle = self.active_cycles[cycle_id]
            current_turn = cycle.turns[cycle.current_turn_index]
            
            return {
                'cycle_id': cycle_id,
                'status': 'active',
                'current_stage': current_turn.stage,
                'turn_status': current_turn.status.value,
                'energy_remaining': current_turn.energy_budget - current_turn.energy_used,
                'turns_completed': len([t for t in cycle.turns if t.status == TurnStatus.COMPLETED]),
                'total_turns': len(cycle.turns),
                'is_sub_council': cycle.is_sub_council,
                'parent_cycle_id': cycle.parent_cycle_id,
                'sub_councils': cycle.sub_councils
            }
        
        # Check completed cycles
        elif cycle_id in self.completed_cycles:
            cycle = self.completed_cycles[cycle_id]
            
            return {
                'cycle_id': cycle_id,
                'status': 'completed',
                'victory_condition': cycle.victory_condition.value if cycle.victory_condition else None,
                'feedback_for_next_cycle': cycle.feedback_for_next_cycle,
                'total_turns': len(cycle.turns),
                'is_sub_council': cycle.is_sub_council,
                'parent_cycle_id': cycle.parent_cycle_id,
                'sub_councils': cycle.sub_councils,
                'completed_at': cycle.completed_at.isoformat() if cycle.completed_at else None
            }
        
        else:
            raise ValueError(f"Cycle {cycle_id} not found")

    async def get_processor_statistics(self) -> Dict[str, Any]:
        """Get processor statistics"""
        active_count = len(self.active_cycles)
        completed_count = len(self.completed_cycles)
        
        # Count victory conditions
        victory_conditions = {}
        for cycle in self.completed_cycles.values():
            if cycle.victory_condition:
                condition = cycle.victory_condition.value
                victory_conditions[condition] = victory_conditions.get(condition, 0) + 1
        
        # Count sub-councils
        total_sub_councils = sum(len(cycle.sub_councils) for cycle in self.active_cycles.values())
        total_sub_councils += sum(len(cycle.sub_councils) for cycle in self.completed_cycles.values())
        
        return {
            'active_cycles': active_count,
            'completed_cycles': completed_count,
            'total_cycles': active_count + completed_count,
            'victory_conditions': victory_conditions,
            'total_sub_councils': total_sub_councils,
            'sub_council_registry': len(self.sub_council_registry)
        }

# Example usage
async def main():
    """Example usage of the turn-based processor"""
    
    processor = CosmicCouncilTurnBasedProcessor()
    
    # Start a new cycle
    cycle_id = await processor.start_new_cycle(
        "How can we improve customer satisfaction in our e-commerce platform?",
        energy_budget=100
    )
    
    print(f"Started cycle: {cycle_id}")
    
    # Execute some turns
    result1 = await processor.execute_turn(cycle_id, ActionType.QUERY, {
        'query_type': 'customer_feedback',
        'query_data': {'source': 'surveys'}
    })
    print(f"Query result: {result1}")
    
    result2 = await processor.execute_turn(cycle_id, ActionType.QUERY, {
        'query_type': 'competitor_analysis',
        'query_data': {'competitors': ['competitor1', 'competitor2']}
    })
    print(f"Query result: {result2}")
    
    # Get cycle status
    status = await processor.get_cycle_status(cycle_id)
    print(f"Cycle status: {status}")
    
    # Get processor statistics
    stats = await processor.get_processor_statistics()
    print(f"Processor statistics: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
