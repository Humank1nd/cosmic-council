"""
BLUE DOLPHIN Agent - Cosmic Council Integration.

This module integrates the Blue Dolphin Location engine
as a SpecializedAgent in the Cosmic Council hierarchy.

Blue Dolphin is the BLUE Enterprise (Level 6), answering WHERE.
It is the fifth step in the Six-Seven Triangle cycle.
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

from .engine import BlueDolphinEngine, create_blue_dolphin, BlueDolphinResult
from .models import BlueDolphinConfig, Location, Environment

logger = structlog.get_logger(__name__)


class BlueAgentRole:
    """Extended agent roles for Blue Dolphin."""
    LOCATOR = "locator"


class BlueDolphinAgent(BaseTotemAgent):
    """
    Location Agent for the Blue Dolphin Team.

    This agent specializes in answering WHERE - the fundamental
    question after WHEN is answered. It determines execution locations
    from scheduled slots.

    The Three Falsifiable Criteria:
    1. Location resolution (every action has a target)
    2. Environment matching (actions matched to environments)
    3. Connectivity validation (all targets reachable)
    """

    def __init__(
        self,
        agent_id: str,
        llm_provider: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        location_config: Optional[BlueDolphinConfig] = None,
        locations: Optional[Dict[str, Location]] = None,
        environments: Optional[Dict[str, Environment]] = None,
    ):
        """
        Initialize the Blue Dolphin Agent.

        Args:
            agent_id: Unique agent identifier
            llm_provider: LLM provider for intelligent routing
            config: General agent configuration
            location_config: Blue Dolphin specific configuration
            locations: Custom locations
            environments: Custom environments
        """
        # Initialize as a Blue Dolphin team member
        super().__init__(
            agent_id=agent_id,
            totem=TotemType.BLUE_DOLPHIN,
            role=BlueAgentRole.LOCATOR,
            llm_provider=llm_provider,
            config=config,
        )

        # Override the system prompt for location
        self.system_prompt = """You are the Locator for the Blue Dolphin team.
Your role is to answer WHERE - determining execution locations for scheduled actions.

You determine locations with:
- Environment selection (production, staging, development)
- Geographic routing (regions, zones, clusters)
- Connectivity validation (reachability checks)

You embody three principles:
1. Every action has a specific execution target
2. Actions are matched to appropriate environments
3. All targets are validated as reachable"""

        # Create the location engine
        self.location_engine = create_blue_dolphin(
            config=location_config,
            locations=locations,
            environments=environments,
            llm_provider=llm_provider,
        )

        logger.info(
            "blue_dolphin_agent_initialized",
            agent_id=agent_id,
            has_llm=llm_provider is not None,
        )

    async def process_task(self, context: TaskContext) -> AgentResult:
        """
        Process a location task.

        Args:
            context: Task context with scheduled slots

        Returns:
            AgentResult with location plan
        """
        start_time = time.time()

        try:
            # Extract slots from context
            input_data = context.input_data if context.input_data else {}
            slots = input_data.get("slots", [])
            schedule_id = input_data.get("schedule_id", context.task_id)
            location_context = input_data.get("context", {})

            # If no slots provided, try to parse from description
            if not slots and context.task_description:
                slots = self._parse_slots_from_description(context.task_description)

            # Run the location engine
            result: BlueDolphinResult = await self.location_engine.locate(
                schedule_id=schedule_id,
                slots=slots,
                context=location_context,
            )

            # Update agent metrics
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (
                (self.avg_processing_time * (self.tasks_completed - 1) + processing_time)
                / self.tasks_completed
            )

            # Build output
            plan = result.location_plan
            output = {
                "plan_id": plan.id,
                "schedule_id": plan.schedule_id,
                "target_count": len(plan.targets),
                "is_valid": plan.is_valid,
                "targets": [
                    {
                        "id": t.id,
                        "action_id": t.action_id,
                        "location": t.location.name if t.location else None,
                        "environment": t.environment.name if t.environment else None,
                        "namespace": t.namespace,
                        "is_resolved": t.is_resolved,
                        "is_reachable": t.is_reachable,
                    }
                    for t in plan.targets
                ],
                "environments": [
                    {
                        "id": e.id,
                        "name": e.name,
                        "type": e.type.value,
                        "is_production": e.is_production,
                    }
                    for e in plan.environments
                ],
                "locations": [
                    {
                        "id": l.id,
                        "name": l.name,
                        "region": l.region,
                        "cluster": l.cluster_name,
                    }
                    for l in plan.locations
                ],
                "reasoning": result.reasoning,
                "warnings": result.warnings,
                "criterion_metrics": {
                    "location_resolution": result.location_resolution,
                    "environment_matching": result.environment_matching,
                    "connectivity_validation": result.connectivity_validation,
                },
            }

            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=result.success,
                output=output,
                confidence=result.connectivity_validation if result.success else 0.0,
                processing_time=processing_time,
                metadata={
                    "plan_id": plan.id,
                    "target_count": len(plan.targets),
                    "is_valid": plan.is_valid,
                },
            )

        except Exception as e:
            logger.error(f"Location failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0,
                processing_time=time.time() - start_time,
            )

    def _parse_slots_from_description(
        self,
        description: str,
    ) -> List[Dict[str, Any]]:
        """Parse slots from task description."""
        slots = []
        lines = description.split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith("#"):
                slots.append({
                    "id": f"slot-{i+1}",
                    "action_id": f"action-{i+1}",
                    "action_title": line,
                })

        return slots

    def should_handoff(self, context: TaskContext) -> Optional[AgentHandoff]:
        """
        Determine if task should be handed off to another agent.

        Blue Dolphin hands off to:
        - Violet Fox (WHO) for responsibility assignment
        - Back to execution layer for actual execution
        """
        if context.metadata.get("location_complete"):
            plan = context.metadata.get("location_plan")

            # Hand off to Violet Fox for responsibility assignment
            return AgentHandoff(
                from_agent=self.agent_id,
                to_specialization=AgentSpecialization.TASK_EXECUTOR,
                reason=HandoffReason.SUBTASK,
                context={
                    "location_plan": plan,
                    "task": "Assign execution responsibilities",
                },
                confidence=0.8,
            )

        return None

    def get_handoff_targets(self) -> List[AgentSpecialization]:
        """Get possible handoff targets."""
        return [
            AgentSpecialization.TASK_EXECUTOR,  # Violet Fox for responsibility
            AgentSpecialization.COORDINATOR,    # Or back to coordinator
        ]

    def get_location_metrics(self) -> Dict[str, Any]:
        """Get location-specific metrics."""
        return self.location_engine.get_metrics()


# Factory function
def create_blue_dolphin_agent(
    agent_id: str = "blue_dolphin_1",
    llm_provider: Optional[Any] = None,
    location_config: Optional[BlueDolphinConfig] = None,
    **kwargs,
) -> BlueDolphinAgent:
    """Create a Blue Dolphin Agent instance."""
    return BlueDolphinAgent(
        agent_id=agent_id,
        llm_provider=llm_provider,
        location_config=location_config,
        **kwargs,
    )


# Singleton instance
_location_agent: Optional[BlueDolphinAgent] = None


def get_location_agent() -> BlueDolphinAgent:
    """Get the default location agent instance."""
    global _location_agent
    if _location_agent is None:
        _location_agent = create_blue_dolphin_agent()
    return _location_agent
