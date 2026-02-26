"""
BLACK SNAKE Agent - Cosmic Council Integration.

This module integrates the Black Snake Execution engine
as a SpecializedAgent in the Cosmic Council hierarchy.

Black Snake is the 7th step, completing the Ouroboros cycle.
It executes actions and feeds insights back to Red Owl.
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

from .engine import BlackSnakeEngine, create_black_snake, BlackSnakeResult
from .models import BlackSnakeConfig, OUROBOROS_SYMBOL

logger = structlog.get_logger(__name__)


class BlackSnakeAgentRole:
    """Extended agent roles for Black Snake."""
    EXECUTOR = "executor"
    OUROBOROS = "ouroboros"


class BlackSnakeAgent(BaseTotemAgent):
    """
    Execution Agent for the Black Snake - the 7th step.

    Black Snake completes the Ouroboros cycle by:
    1. Executing all assigned actions
    2. Capturing execution outcomes
    3. Feeding insights back to Red Owl

    The Three Falsifiable Criteria:
    1. Execution completion (all actions executed)
    2. Outcome capture (results properly recorded)
    3. Cycle recursion (insights feed back)
    """

    def __init__(
        self,
        agent_id: str,
        llm_provider: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        execution_config: Optional[BlackSnakeConfig] = None,
    ):
        """
        Initialize the Black Snake Agent.

        Args:
            agent_id: Unique agent identifier
            llm_provider: LLM provider (optional)
            config: General agent configuration
            execution_config: Black Snake specific configuration
        """
        # Initialize as Black Snake (use FEEDBACK_COLLECTOR as closest match)
        super().__init__(
            agent_id=agent_id,
            totem=TotemType.PURPLE_ELEPHANT,  # Black Snake extends beyond the 6 totems
            role=AgentRole.FEEDBACK_COLLECTOR,  # Closest match for recursion
            llm_provider=llm_provider,
            config=config,
        )

        # Override totem info for Black Snake
        self.totem_name = "Black Snake"
        self.totem_symbol = OUROBOROS_SYMBOL

        # Override the system prompt for execution
        self.system_prompt = """You are Black Snake - the 7th step in the Cosmic Council.
Your role is to EXECUTE and RECURSE - completing the eternal cycle.

You close the Ouroboros by:
- Executing all assigned actions from Purple Elephant
- Capturing outcomes and detecting surprises
- Generating insights that feed back to Red Owl

You embody three principles:
1. All assigned actions are executed
2. Results are properly recorded
3. Insights feed back to initiate new inquiry

The serpent consumes its tail. Each ending is a new beginning."""

        # Create the execution engine
        self.execution_engine = create_black_snake(config=execution_config)

        logger.info(
            "black_snake_agent_initialized",
            agent_id=agent_id,
            dry_run=execution_config.dry_run if execution_config else False,
        )

    async def process_task(self, context: TaskContext) -> AgentResult:
        """
        Process an execution task.

        Args:
            context: Task context with assignments

        Returns:
            AgentResult with execution plan
        """
        start_time = time.time()

        try:
            # Extract assignments from context
            input_data = context.input_data if context.input_data else {}
            assignments = input_data.get("assignments", [])
            responsibility_plan_id = input_data.get(
                "responsibility_plan_id", context.task_id
            )
            execution_context = input_data.get("context", {})

            # If no assignments provided, try to parse from description
            if not assignments and context.task_description:
                assignments = self._parse_assignments_from_description(
                    context.task_description
                )

            # Run the execution engine
            result: BlackSnakeResult = await self.execution_engine.execute(
                responsibility_plan_id=responsibility_plan_id,
                assignments=assignments,
                context=execution_context,
            )

            # Update agent metrics
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (
                (self.avg_processing_time * (self.tasks_completed - 1) + processing_time)
                / self.tasks_completed
            )

            # Build output
            plan = result.execution_plan
            output = {
                "plan_id": plan.id if plan else None,
                "cycle_id": plan.cycle_id if plan else None,
                "execution_count": len(plan.executions) if plan else 0,
                "is_valid": plan.is_valid if plan else False,
                "executions": [
                    {
                        "id": e.id,
                        "action_id": e.action_id,
                        "status": e.status.value,
                        "success": e.success,
                        "duration_ms": e.duration_ms,
                    }
                    for e in (plan.executions if plan else [])
                ],
                "outcomes": [
                    {
                        "id": o.id,
                        "action_id": o.action_id,
                        "outcome_type": o.outcome_type.value,
                        "impact_score": o.impact_score,
                    }
                    for o in (plan.outcomes if plan else [])
                ],
                "insights": [
                    {
                        "id": i.id,
                        "type": i.insight_type.value,
                        "title": i.title,
                        "confidence": i.confidence,
                    }
                    for i in (plan.insights if plan else [])
                ],
                "next_cycle_seed": plan.next_cycle_seed if plan else None,
                "reasoning": result.reasoning,
                "warnings": result.warnings,
                "criterion_metrics": {
                    "execution_completion": result.execution_completion,
                    "outcome_capture": result.outcome_capture,
                    "cycle_recursion": result.cycle_recursion,
                },
            }

            # Add feedback for Red Owl if available
            if result.cycle_result:
                feedback = result.cycle_result.feedback
                output["red_owl_feedback"] = {
                    "new_questions": feedback.new_questions,
                    "hypotheses_to_test": feedback.hypotheses_to_test,
                    "evidence_collected": feedback.evidence_collected,
                    "should_continue": feedback.should_continue,
                    "priority": feedback.priority,
                    "urgency": feedback.urgency,
                }

            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=result.success,
                output=output,
                confidence=result.execution_completion if result.success else 0.0,
                processing_time=processing_time,
                metadata={
                    "plan_id": plan.id if plan else None,
                    "execution_count": len(plan.executions) if plan else 0,
                    "is_valid": plan.is_valid if plan else False,
                    "next_cycle_ready": result.cycle_result.next_cycle_initiated if result.cycle_result else False,
                },
            )

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0,
                processing_time=time.time() - start_time,
            )

    def _parse_assignments_from_description(
        self,
        description: str,
    ) -> List[Dict[str, Any]]:
        """Parse assignments from task description."""
        assignments = []
        lines = description.split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith("#"):
                assignments.append({
                    "id": f"assign-{i+1}",
                    "action_id": f"action-{i+1}",
                    "action_type": "default",
                    "parameters": {},
                })

        return assignments

    def should_handoff(self, context: TaskContext) -> Optional[AgentHandoff]:
        """
        Determine if task should be handed off to another agent.

        Black Snake completes the cycle by handing back to Red Owl.
        """
        if context.metadata.get("cycle_complete"):
            feedback = context.metadata.get("red_owl_feedback", {})

            if feedback.get("should_continue", False):
                # Hand off back to Red Owl to start new cycle
                return AgentHandoff(
                    from_agent=self.agent_id,
                    to_specialization=AgentSpecialization.DATA_COLLECTOR,  # Red Owl
                    reason=HandoffReason.COMPLETED,
                    context={
                        "feedback": feedback,
                        "task": "Initiate new inquiry cycle",
                    },
                    confidence=0.9,
                )

        return None

    def get_handoff_targets(self) -> List[AgentSpecialization]:
        """Get possible handoff targets."""
        return [
            AgentSpecialization.DATA_COLLECTOR,  # Back to Red Owl
            AgentSpecialization.COORDINATOR,     # Or to coordinator
        ]

    def get_execution_metrics(self) -> Dict[str, Any]:
        """Get execution-specific metrics."""
        return self.execution_engine.get_metrics()

    def set_red_owl_callback(self, callback) -> None:
        """Set the callback for feeding back to Red Owl."""
        self.execution_engine.set_red_owl_callback(callback)


# Factory function
def create_black_snake_agent(
    agent_id: str = "black_snake_1",
    llm_provider: Optional[Any] = None,
    execution_config: Optional[BlackSnakeConfig] = None,
    **kwargs,
) -> BlackSnakeAgent:
    """Create a Black Snake Agent instance."""
    return BlackSnakeAgent(
        agent_id=agent_id,
        llm_provider=llm_provider,
        execution_config=execution_config,
        **kwargs,
    )


# Singleton instance
_execution_agent: Optional[BlackSnakeAgent] = None


def get_execution_agent() -> BlackSnakeAgent:
    """Get the default execution agent instance."""
    global _execution_agent
    if _execution_agent is None:
        _execution_agent = create_black_snake_agent()
    return _execution_agent
