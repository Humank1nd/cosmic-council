"""
YELLOW HONEYBEE Agent - Cosmic Council Integration.

This module integrates the Yellow Honeybee Implementation Specification engine
as a SpecializedAgent in the Cosmic Council hierarchy.

Yellow Honeybee is the YELLOW Enterprise (Level 4), answering WHAT.
It is the third step in the Six-Seven Triangle cycle.
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

from .engine import YellowHoneybeeEngine, create_yellow_honeybee, YellowHoneybeeResult
from .models import YellowHoneybeeConfig

logger = structlog.get_logger(__name__)


class YellowAgentRole:
    """Extended agent roles for Yellow Honeybee."""
    IMPLEMENTATION_PLANNER = "implementation_planner"


class YellowHoneybeeAgent(BaseTotemAgent):
    """
    Implementation Specification Agent for the Yellow Honeybee Team.

    This agent specializes in answering WHAT - the fundamental
    question after HOW is answered. It creates detailed implementation
    specifications from action plans.

    The Three Falsifiable Criteria:
    1. Specification completeness (every action gets detailed specs)
    2. Validation rules (pre/post conditions for each step)
    3. Resource identification (specific resources identified)
    """

    def __init__(
        self,
        agent_id: str,
        llm_provider: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        specification_config: Optional[YellowHoneybeeConfig] = None,
        default_namespace: str = "default",
        service_registry: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """
        Initialize the Yellow Honeybee Agent.

        Args:
            agent_id: Unique agent identifier
            llm_provider: LLM provider for intelligent specification
            config: General agent configuration
            specification_config: Yellow Honeybee specific configuration
            default_namespace: Default Kubernetes namespace
            service_registry: Optional service registry
        """
        # Initialize as a Yellow Honeybee team member
        super().__init__(
            agent_id=agent_id,
            totem=TotemType.YELLOW_HONEYBEE,
            role=YellowAgentRole.IMPLEMENTATION_PLANNER,
            llm_provider=llm_provider,
            config=config,
        )

        # Override the system prompt for implementation specification
        self.system_prompt = """You are the Implementation Planner for the Yellow Honeybee team.
Your role is to answer WHAT - creating detailed implementation specifications from action plans.

You create specifications with:
- Exact commands, API calls, or configuration changes
- Pre-conditions that must be true before execution
- Post-conditions that must be true after execution
- Specific resources identified (endpoints, configs, secrets)

You embody three principles:
1. Every action gets a complete specification
2. Every step has validation rules
3. Every resource is specifically identified"""

        # Create the specification engine
        self.specification_engine = create_yellow_honeybee(
            config=specification_config,
            llm_provider=llm_provider,
            default_namespace=default_namespace,
            service_registry=service_registry,
        )

        logger.info(
            "yellow_honeybee_agent_initialized",
            agent_id=agent_id,
            has_llm=llm_provider is not None,
            default_namespace=default_namespace,
        )

    async def process_task(self, context: TaskContext) -> AgentResult:
        """
        Process an implementation specification task.

        Args:
            context: Task context with action plan

        Returns:
            AgentResult with implementation plan
        """
        start_time = time.time()

        try:
            # Extract actions from context
            input_data = context.input_data if context.input_data else {}
            actions = input_data.get("actions", [])
            action_plan_id = input_data.get("action_plan_id", context.task_id)
            root_cause = input_data.get("root_cause", context.task_description)
            specification_context = input_data.get("context", {})

            # If task_description contains action info, parse it
            if not actions and context.task_description:
                # Try to extract from description
                actions = self._parse_actions_from_description(context.task_description)

            # Run the specification
            result: YellowHoneybeeResult = await self.specification_engine.specify(
                action_plan_id=action_plan_id,
                actions=actions,
                root_cause=root_cause,
                context=specification_context,
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
                "action_plan_id": plan.action_plan_id,
                "spec_count": len(plan.specifications),
                "completeness_ratio": plan.completeness_ratio,
                "total_pre_conditions": plan.total_pre_conditions,
                "total_post_conditions": plan.total_post_conditions,
                "resource_count": len(plan.all_resources),
                "estimated_duration_seconds": plan.estimated_total_duration_seconds,
                "specifications": [
                    {
                        "id": s.id,
                        "action_id": s.action_id,
                        "action_title": s.action_title,
                        "spec_type": s.spec_type.value,
                        "is_complete": s.is_complete,
                        "has_validation": s.has_validation,
                        "resource_count": len(s.resources),
                        "steps": s.steps,
                    }
                    for s in plan.specifications
                ],
                "resources": [
                    {
                        "name": r.name,
                        "type": r.type.value,
                        "identifier": r.identifier,
                        "namespace": r.namespace,
                    }
                    for r in plan.all_resources
                ],
                "reasoning": result.reasoning,
                "warnings": result.warnings,
                "criterion_metrics": {
                    "specification_completeness": result.specification_completeness,
                    "validation_coverage": result.validation_coverage,
                    "resource_identification": result.resource_identification,
                },
            }

            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=result.success,
                output=output,
                confidence=result.specification_completeness if result.success else 0.0,
                processing_time=processing_time,
                metadata={
                    "plan_id": plan.id,
                    "spec_count": len(plan.specifications),
                },
            )

        except Exception as e:
            logger.error(f"Implementation specification failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0,
                processing_time=time.time() - start_time,
            )

    def _parse_actions_from_description(
        self,
        description: str,
    ) -> List[Dict[str, Any]]:
        """Parse actions from task description."""
        # Simple parsing - in production this would be more sophisticated
        actions = []
        lines = description.split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith("#"):
                actions.append({
                    "id": f"action-{i+1}",
                    "title": line,
                    "category": self._infer_category(line),
                })

        return actions

    def _infer_category(self, title: str) -> str:
        """Infer action category from title."""
        title_lower = title.lower()

        if any(w in title_lower for w in ["deploy", "rollback", "release"]):
            return "deployment"
        if any(w in title_lower for w in ["scale", "replica"]):
            return "scaling"
        if any(w in title_lower for w in ["restart", "reboot"]):
            return "restart"
        if any(w in title_lower for w in ["database", "db", "query", "sql"]):
            return "database"
        if any(w in title_lower for w in ["config", "setting", "parameter"]):
            return "configuration"
        if any(w in title_lower for w in ["network", "dns", "firewall"]):
            return "network"
        if any(w in title_lower for w in ["security", "auth", "credential"]):
            return "security"
        if any(w in title_lower for w in ["monitor", "alert", "metric"]):
            return "monitoring"
        if any(w in title_lower for w in ["notify", "communicate", "message"]):
            return "communication"

        return "investigation"

    def should_handoff(self, context: TaskContext) -> Optional[AgentHandoff]:
        """
        Determine if task should be handed off to another agent.

        Yellow Honeybee hands off to:
        - Green Turtle (WHEN) for scheduling
        - Blue Dolphin (WHERE) for execution location
        """
        # Check if we've completed specification and should hand off
        if context.metadata.get("specification_complete"):
            plan = context.metadata.get("plan")

            # Hand off to Green Turtle for scheduling
            return AgentHandoff(
                from_agent=self.agent_id,
                to_specialization=AgentSpecialization.SCHEDULER,
                reason=HandoffReason.SUBTASK,
                context={
                    "plan": plan,
                    "task": "Schedule the implementation plan",
                },
                confidence=0.8,
            )

        return None

    def get_handoff_targets(self) -> List[AgentSpecialization]:
        """Get possible handoff targets."""
        return [
            AgentSpecialization.SCHEDULER,     # Green Turtle for scheduling
            AgentSpecialization.COORDINATOR,   # Blue Dolphin for location
        ]

    def get_specification_metrics(self) -> Dict[str, Any]:
        """Get specification-specific metrics."""
        return self.specification_engine.get_metrics()


# Factory function
def create_yellow_honeybee_agent(
    agent_id: str = "yellow_honeybee_1",
    llm_provider: Optional[Any] = None,
    specification_config: Optional[YellowHoneybeeConfig] = None,
    **kwargs,
) -> YellowHoneybeeAgent:
    """Create a Yellow Honeybee Agent instance."""
    return YellowHoneybeeAgent(
        agent_id=agent_id,
        llm_provider=llm_provider,
        specification_config=specification_config,
        **kwargs,
    )


# Singleton instance
_specification_agent: Optional[YellowHoneybeeAgent] = None


def get_specification_agent() -> YellowHoneybeeAgent:
    """Get the default specification agent instance."""
    global _specification_agent
    if _specification_agent is None:
        _specification_agent = create_yellow_honeybee_agent()
    return _specification_agent
