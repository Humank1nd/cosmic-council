"""
GREEN TURTLE Agent - Cosmic Council Integration.

This module integrates the Green Turtle Scheduling engine
as a SpecializedAgent in the Cosmic Council hierarchy.

Green Turtle is the GREEN Enterprise (Level 5), answering WHEN.
It is the fourth step in the Six-Seven Triangle cycle.
"""

import time
from typing import Any, Dict, List, Optional

import structlog

from ..hierarchical_enterprise import (
    SpecializedAgent,
    AgentSpecialization,
    TaskContext,
    AgentResult,
    AgentHandoff,
    HandoffReason,
)
from ..agent_registry_36 import TotemType, AgentRole, BaseTotemAgent

try:
    from ..integrations.llm_provider import BaseLLMProvider, LLMRequest, LLMMessage
except ImportError:
    BaseLLMProvider = None
    LLMRequest = None
    LLMMessage = None

from .engine import GreenTurtleEngine, create_green_turtle, GreenTurtleResult
from .models import GreenTurtleConfig, TimeWindow

logger = structlog.get_logger(__name__)


class GreenAgentRole:
    """Extended agent roles for Green Turtle."""
    SCHEDULER = "scheduler"


class GreenTurtleAgent(BaseTotemAgent):
    """
    Scheduling Agent for the Green Turtle Team.

    This agent specializes in answering WHEN - the fundamental
    question after WHAT is answered. It creates execution schedules
    from implementation specifications.

    The Three Falsifiable Criteria:
    1. Time window compliance (actions within valid windows)
    2. Dependency sequencing (actions respect dependencies)
    3. Constraint satisfaction (all constraints met)
    """

    def __init__(
        self,
        agent_id: str,
        llm_provider: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        scheduling_config: Optional[GreenTurtleConfig] = None,
        time_windows: Optional[Dict[str, TimeWindow]] = None,
    ):
        """
        Initialize the Green Turtle Agent.

        Args:
            agent_id: Unique agent identifier
            llm_provider: LLM provider for intelligent scheduling
            config: General agent configuration
            scheduling_config: Green Turtle specific configuration
            time_windows: Custom time windows
        """
        # Initialize as a Green Turtle team member
        super().__init__(
            agent_id=agent_id,
            totem=TotemType.GREEN_TURTLE,
            role=GreenAgentRole.SCHEDULER,
            llm_provider=llm_provider,
            config=config,
        )

        # Override the system prompt for scheduling
        self.system_prompt = """You are the Scheduler for the Green Turtle team.
Your role is to answer WHEN - creating execution schedules from implementation specs.

You create schedules with:
- Optimal time windows (maintenance, off-peak, business hours)
- Dependency-aware sequencing (topological ordering)
- Constraint satisfaction (concurrency, cooldown, SLA)

You embody three principles:
1. Actions execute within appropriate time windows
2. Dependencies are always respected
3. All constraints are satisfied"""

        # Create the scheduling engine
        self.scheduling_engine = create_green_turtle(
            config=scheduling_config,
            llm_provider=llm_provider,
            time_windows=time_windows,
        )

        logger.info(
            "green_turtle_agent_initialized",
            agent_id=agent_id,
            has_llm=llm_provider is not None,
        )

    async def process_task(self, context: TaskContext) -> AgentResult:
        """
        Process a scheduling task.

        Args:
            context: Task context with specifications

        Returns:
            AgentResult with execution schedule
        """
        start_time = time.time()

        try:
            # Extract specifications from context
            input_data = context.input_data if context.input_data else {}
            specifications = input_data.get("specifications", [])
            implementation_plan_id = input_data.get("implementation_plan_id", context.task_id)
            dependencies = input_data.get("dependencies", [])
            scheduling_context = input_data.get("context", {})

            # If no specs provided, try to parse from description
            if not specifications and context.task_description:
                specifications = self._parse_specs_from_description(context.task_description)

            # Run the scheduling
            result: GreenTurtleResult = await self.scheduling_engine.schedule(
                implementation_plan_id=implementation_plan_id,
                specifications=specifications,
                dependencies=dependencies,
                context=scheduling_context,
            )

            # Update agent metrics
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (
                (self.avg_processing_time * (self.tasks_completed - 1) + processing_time)
                / self.tasks_completed
            )

            # Build output
            schedule = result.schedule
            output = {
                "schedule_id": schedule.id,
                "implementation_plan_id": schedule.implementation_plan_id,
                "slot_count": len(schedule.slots),
                "is_valid": schedule.is_valid,
                "earliest_start": schedule.earliest_start.isoformat() if schedule.earliest_start else None,
                "latest_end": schedule.latest_end.isoformat() if schedule.latest_end else None,
                "total_duration_seconds": schedule.total_duration_seconds,
                "slots": [
                    {
                        "id": s.id,
                        "action_id": s.action_id,
                        "scheduled_start": s.scheduled_start.isoformat() if s.scheduled_start else None,
                        "scheduled_end": s.scheduled_end.isoformat() if s.scheduled_end else None,
                        "status": s.status.name,
                        "priority": s.priority.name,
                        "time_window": s.time_window_name,
                    }
                    for s in schedule.slots
                ],
                "execution_order": schedule.execution_order,
                "reasoning": result.reasoning,
                "warnings": result.warnings,
                "criterion_metrics": {
                    "time_window_compliance": result.time_window_compliance,
                    "dependency_sequencing": result.dependency_sequencing,
                    "constraint_satisfaction": result.constraint_satisfaction,
                },
            }

            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=result.success,
                output=output,
                confidence=result.constraint_satisfaction if result.success else 0.0,
                processing_time=processing_time,
                metadata={
                    "schedule_id": schedule.id,
                    "slot_count": len(schedule.slots),
                    "is_valid": schedule.is_valid,
                },
            )

        except Exception as e:
            logger.error(f"Scheduling failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0,
                processing_time=time.time() - start_time,
            )

    def _parse_specs_from_description(
        self,
        description: str,
    ) -> List[Dict[str, Any]]:
        """Parse specifications from task description."""
        specs = []
        lines = description.split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith("#"):
                specs.append({
                    "id": f"spec-{i+1}",
                    "action_id": f"action-{i+1}",
                    "action_title": line,
                    "estimated_duration_seconds": 60,
                })

        return specs

    def should_handoff(self, context: TaskContext) -> Optional[AgentHandoff]:
        """
        Determine if task should be handed off to another agent.

        Green Turtle hands off to:
        - Blue Dolphin (WHERE) for execution location
        - Violet Fox (WHO) for responsibility assignment
        """
        if context.metadata.get("scheduling_complete"):
            schedule = context.metadata.get("schedule")

            # Hand off to Blue Dolphin for execution location
            return AgentHandoff(
                from_agent=self.agent_id,
                to_specialization=AgentSpecialization.COORDINATOR,
                reason=HandoffReason.SUBTASK,
                context={
                    "schedule": schedule,
                    "task": "Determine execution locations",
                },
                confidence=0.8,
            )

        return None

    def get_handoff_targets(self) -> List[AgentSpecialization]:
        """Get possible handoff targets."""
        return [
            AgentSpecialization.COORDINATOR,   # Blue Dolphin for location
            AgentSpecialization.TASK_EXECUTOR, # Or direct to execution
        ]

    def get_scheduling_metrics(self) -> Dict[str, Any]:
        """Get scheduling-specific metrics."""
        return self.scheduling_engine.get_metrics()


# Factory function
def create_green_turtle_agent(
    agent_id: str = "green_turtle_1",
    llm_provider: Optional[Any] = None,
    scheduling_config: Optional[GreenTurtleConfig] = None,
    **kwargs,
) -> GreenTurtleAgent:
    """Create a Green Turtle Agent instance."""
    return GreenTurtleAgent(
        agent_id=agent_id,
        llm_provider=llm_provider,
        scheduling_config=scheduling_config,
        **kwargs,
    )


# Singleton instance
_scheduling_agent: Optional[GreenTurtleAgent] = None


def get_scheduling_agent() -> GreenTurtleAgent:
    """Get the default scheduling agent instance."""
    global _scheduling_agent
    if _scheduling_agent is None:
        _scheduling_agent = create_green_turtle_agent()
    return _scheduling_agent
