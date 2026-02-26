"""
PURPLE ELEPHANT Agent - Cosmic Council Integration.

This module integrates the Purple Elephant Responsibility engine
as a SpecializedAgent in the Cosmic Council hierarchy.

Purple Elephant is the PURPLE Enterprise (Level 7), answering WHO.
It is the sixth step in the Six-Seven Triangle cycle.
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

from .engine import PurpleElephantEngine, create_purple_elephant, PurpleElephantResult
from .models import PurpleElephantConfig, Stakeholder

logger = structlog.get_logger(__name__)


class PurpleAgentRole:
    """Extended agent roles for Purple Elephant."""
    ASSIGNER = "assigner"


class PurpleElephantAgent(BaseTotemAgent):
    """
    Responsibility Agent for the Purple Elephant Team.

    This agent specializes in answering WHO - the fundamental
    question after WHERE is answered. It assigns responsibilities
    for located targets.

    The Three Falsifiable Criteria:
    1. Responsibility assignment (every action has an executor)
    2. Stakeholder identification (all stakeholders identified)
    3. Notification routing (all parties notified)
    """

    def __init__(
        self,
        agent_id: str,
        llm_provider: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        responsibility_config: Optional[PurpleElephantConfig] = None,
        stakeholders: Optional[Dict[str, Stakeholder]] = None,
    ):
        """
        Initialize the Purple Elephant Agent.

        Args:
            agent_id: Unique agent identifier
            llm_provider: LLM provider for intelligent assignment
            config: General agent configuration
            responsibility_config: Purple Elephant specific configuration
            stakeholders: Custom stakeholders
        """
        # Initialize as a Purple Elephant team member
        super().__init__(
            agent_id=agent_id,
            totem=TotemType.PURPLE_ELEPHANT,
            role=PurpleAgentRole.ASSIGNER,
            llm_provider=llm_provider,
            config=config,
        )

        # Override the system prompt for responsibility
        self.system_prompt = """You are the Assigner for the Purple Elephant team.
Your role is to answer WHO - assigning responsibilities for located actions.

You assign responsibilities with:
- Executor designation (who performs the action)
- Stakeholder identification (who needs to know)
- Notification routing (how they are informed)

You embody three principles:
1. Every action has a designated executor
2. All relevant stakeholders are identified
3. All parties are properly notified"""

        # Create the responsibility engine
        self.responsibility_engine = create_purple_elephant(
            config=responsibility_config,
            stakeholders=stakeholders,
            llm_provider=llm_provider,
        )

        logger.info(
            "purple_elephant_agent_initialized",
            agent_id=agent_id,
            has_llm=llm_provider is not None,
        )

    async def process_task(self, context: TaskContext) -> AgentResult:
        """
        Process a responsibility task.

        Args:
            context: Task context with located targets

        Returns:
            AgentResult with responsibility plan
        """
        start_time = time.time()

        try:
            # Extract targets from context
            input_data = context.input_data if context.input_data else {}
            targets = input_data.get("targets", [])
            location_plan_id = input_data.get("location_plan_id", context.task_id)
            responsibility_context = input_data.get("context", {})

            # If no targets provided, try to parse from description
            if not targets and context.task_description:
                targets = self._parse_targets_from_description(context.task_description)

            # Run the responsibility engine
            result: PurpleElephantResult = await self.responsibility_engine.assign(
                location_plan_id=location_plan_id,
                targets=targets,
                context=responsibility_context,
            )

            # Update agent metrics
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (
                (self.avg_processing_time * (self.tasks_completed - 1) + processing_time)
                / self.tasks_completed
            )

            # Build output
            plan = result.responsibility_plan
            output = {
                "plan_id": plan.id,
                "location_plan_id": plan.location_plan_id,
                "assignment_count": len(plan.assignments),
                "is_valid": plan.is_valid,
                "assignments": [
                    {
                        "id": a.id,
                        "action_id": a.action_id,
                        "stakeholder": a.stakeholder.name if a.stakeholder else None,
                        "type": a.responsibility_type.value,
                        "status": a.status.name,
                    }
                    for a in plan.assignments
                ],
                "stakeholders": [
                    {
                        "id": s.id,
                        "name": s.name,
                        "type": s.type.value,
                        "team": s.team,
                    }
                    for s in plan.stakeholders
                ],
                "notifications_sent": plan.notifications_sent,
                "reasoning": result.reasoning,
                "warnings": result.warnings,
                "criterion_metrics": {
                    "responsibility_assignment": result.responsibility_assignment,
                    "stakeholder_identification": result.stakeholder_identification,
                    "notification_routing": result.notification_routing,
                },
            }

            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=result.success,
                output=output,
                confidence=result.responsibility_assignment if result.success else 0.0,
                processing_time=processing_time,
                metadata={
                    "plan_id": plan.id,
                    "assignment_count": len(plan.assignments),
                    "is_valid": plan.is_valid,
                },
            )

        except Exception as e:
            logger.error(f"Responsibility assignment failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0,
                processing_time=time.time() - start_time,
            )

    def _parse_targets_from_description(
        self,
        description: str,
    ) -> List[Dict[str, Any]]:
        """Parse targets from task description."""
        targets = []
        lines = description.split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith("#"):
                targets.append({
                    "id": f"target-{i+1}",
                    "action_id": f"action-{i+1}",
                    "action_title": line,
                })

        return targets

    def should_handoff(self, context: TaskContext) -> Optional[AgentHandoff]:
        """
        Determine if task should be handed off to another agent.

        Purple Elephant completes the Six-Seven Triangle cycle.
        It hands back to the execution layer or starts a new cycle.
        """
        if context.metadata.get("responsibility_complete"):
            plan = context.metadata.get("responsibility_plan")

            # Hand off to execution (or back to coordinator for new cycle)
            return AgentHandoff(
                from_agent=self.agent_id,
                to_specialization=AgentSpecialization.TASK_EXECUTOR,
                reason=HandoffReason.COMPLETED,
                context={
                    "responsibility_plan": plan,
                    "task": "Execute assigned actions",
                },
                confidence=0.9,
            )

        return None

    def get_handoff_targets(self) -> List[AgentSpecialization]:
        """Get possible handoff targets."""
        return [
            AgentSpecialization.TASK_EXECUTOR,  # To execution layer
            AgentSpecialization.COORDINATOR,    # Back to start new cycle
        ]

    def get_responsibility_metrics(self) -> Dict[str, Any]:
        """Get responsibility-specific metrics."""
        return self.responsibility_engine.get_metrics()


# Factory function
def create_purple_elephant_agent(
    agent_id: str = "purple_elephant_1",
    llm_provider: Optional[Any] = None,
    responsibility_config: Optional[PurpleElephantConfig] = None,
    **kwargs,
) -> PurpleElephantAgent:
    """Create a Purple Elephant Agent instance."""
    return PurpleElephantAgent(
        agent_id=agent_id,
        llm_provider=llm_provider,
        responsibility_config=responsibility_config,
        **kwargs,
    )


# Singleton instance
_responsibility_agent: Optional[PurpleElephantAgent] = None


def get_responsibility_agent() -> PurpleElephantAgent:
    """Get the default responsibility agent instance."""
    global _responsibility_agent
    if _responsibility_agent is None:
        _responsibility_agent = create_purple_elephant_agent()
    return _responsibility_agent
