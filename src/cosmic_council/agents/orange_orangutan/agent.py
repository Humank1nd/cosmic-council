"""
ORANGE ORANGUTAN Agent - Cosmic Council Integration.

This module integrates the Orange Orangutan Action Planning engine
as a SpecializedAgent in the Cosmic Council hierarchy.

Orange Orangutan is the ORANGE Enterprise (Level 3), answering HOW.
It is the second step in the Six-Seven Triangle cycle.
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

from .engine import OrangeOrangutanEngine, create_orange_orangutan, OrangeOrangutanResult
from .models import OrangeOrangutanConfig, RiskLevel

logger = structlog.get_logger(__name__)


class OrangeAgentRole:
    """Extended agent roles for Orange Orangutan."""
    ACTION_PLANNER = "action_planner"


class OrangeOrangutanAgent(BaseTotemAgent):
    """
    Action Planning Agent for the Orange Orangutan Team.

    This agent specializes in answering HOW - the fundamental
    question after WHY is answered. It creates actionable plans
    to resolve root causes identified by Red Owl.

    The Three Falsifiable Criteria:
    1. Dependency ordering (actions topologically sorted)
    2. Rollback reversibility (each action has rollback)
    3. Risk gates (high-risk actions require approval)
    """

    def __init__(
        self,
        agent_id: str,
        llm_provider: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        planning_config: Optional[OrangeOrangutanConfig] = None,
        critical_services: Optional[List[str]] = None,
    ):
        """
        Initialize the Orange Orangutan Agent.

        Args:
            agent_id: Unique agent identifier
            llm_provider: LLM provider for intelligent planning
            config: General agent configuration
            planning_config: Orange Orangutan specific configuration
            critical_services: List of critical service names
        """
        # Initialize as an Orange Orangutan team member
        super().__init__(
            agent_id=agent_id,
            totem=TotemType.ORANGE_ORANGUTAN,
            role=OrangeAgentRole.ACTION_PLANNER,
            llm_provider=llm_provider,
            config=config,
        )

        # Override the system prompt for action planning
        self.system_prompt = """You are the Action Planner for the Orange Orangutan team.
Your role is to answer HOW - creating actionable plans from root causes.

You create plans with:
- Clear, sequenced action steps
- Dependency ordering (what must happen first)
- Risk assessment (what could go wrong)
- Rollback procedures (how to undo each step)

You embody three principles:
1. Actions are ordered by dependencies
2. Every action has a rollback plan
3. High-risk actions require approval gates"""

        # Create the planning engine
        self.planning_engine = create_orange_orangutan(
            config=planning_config,
            llm_provider=llm_provider,
            critical_services=critical_services,
        )

        logger.info(
            "orange_orangutan_agent_initialized",
            agent_id=agent_id,
            has_llm=llm_provider is not None,
            critical_services_count=len(critical_services or []),
        )

    async def process_task(self, context: TaskContext) -> AgentResult:
        """
        Process an action planning task.

        Args:
            context: Task context with root cause and confidence

        Returns:
            AgentResult with action plan
        """
        start_time = time.time()

        try:
            # Extract root cause from context
            root_cause = context.task_description

            # Get confidence from input_data or default
            input_data = context.input_data if context.input_data else {}
            confidence = input_data.get("confidence", 0.7)
            planning_context = input_data.get("context", {})

            # Run the planning
            result: OrangeOrangutanResult = await self.planning_engine.plan(
                root_cause=root_cause,
                confidence=confidence,
                context=planning_context,
                problem_id=context.task_id,
            )

            # Update agent metrics
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (
                (self.avg_processing_time * (self.tasks_completed - 1) + processing_time)
                / self.tasks_completed
            )

            # Build output
            plan = result.plan
            output = {
                "plan_id": plan.id,
                "action_count": len(plan.actions),
                "overall_risk": plan.overall_risk.name,
                "requires_approval": plan.requires_approval,
                "approval_gates": plan.approval_gates,
                "execution_order": plan.execution_order,
                "estimated_duration_seconds": plan.estimated_total_duration_seconds,
                "actions": [
                    {
                        "id": a.id,
                        "title": a.title,
                        "category": a.category.value,
                        "risk_level": a.risk_level.name,
                        "depends_on": a.depends_on,
                        "has_rollback": a.rollback is not None and a.rollback.is_reversible,
                    }
                    for a in plan.actions
                ],
                "rollback_order": plan.rollback_order,
                "reasoning": result.reasoning,
                "warnings": result.warnings,
            }

            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=result.success,
                output=output,
                confidence=confidence if result.success else 0.0,
                processing_time=processing_time,
                metadata={
                    "plan_id": plan.id,
                    "root_cause_type": plan.metadata.get("cause_type", "unknown"),
                },
            )

        except Exception as e:
            logger.error(f"Action planning failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0,
                processing_time=time.time() - start_time,
            )

    def should_handoff(self, context: TaskContext) -> Optional[AgentHandoff]:
        """
        Determine if task should be handed off to another agent.

        Orange Orangutan hands off to:
        - Yellow Honeybee (WHAT) for implementation details
        - Green Turtle (WHEN) for scheduling
        """
        # Check if we've completed planning and should hand off
        if context.metadata.get("planning_complete"):
            plan = context.metadata.get("plan")
            risk = context.metadata.get("overall_risk", "LOW")

            # Hand off to Yellow Honeybee for implementation
            return AgentHandoff(
                from_agent=self.agent_id,
                to_specialization=AgentSpecialization.TASK_EXECUTOR,
                reason=HandoffReason.SUBTASK,
                context={
                    "plan": plan,
                    "overall_risk": risk,
                    "task": "Implement the action plan",
                },
                confidence=0.8,
            )

        return None

    def get_handoff_targets(self) -> List[AgentSpecialization]:
        """Get possible handoff targets."""
        return [
            AgentSpecialization.TASK_EXECUTOR,   # Yellow Honeybee for implementation
            AgentSpecialization.SCHEDULER,        # Green Turtle for scheduling
        ]

    def get_planning_metrics(self) -> Dict[str, Any]:
        """Get planning-specific metrics."""
        return self.planning_engine.get_metrics()


# Factory function
def create_orange_orangutan_agent(
    agent_id: str = "orange_orangutan_1",
    llm_provider: Optional[Any] = None,
    planning_config: Optional[OrangeOrangutanConfig] = None,
    **kwargs,
) -> OrangeOrangutanAgent:
    """Create an Orange Orangutan Agent instance."""
    return OrangeOrangutanAgent(
        agent_id=agent_id,
        llm_provider=llm_provider,
        planning_config=planning_config,
        **kwargs,
    )


# Singleton instance
_planning_agent: Optional[OrangeOrangutanAgent] = None


def get_planning_agent() -> OrangeOrangutanAgent:
    """Get the default planning agent instance."""
    global _planning_agent
    if _planning_agent is None:
        _planning_agent = create_orange_orangutan_agent()
    return _planning_agent
