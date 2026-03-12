"""
WHITE RABBIT Agent - Cosmic Council Integration.

This module integrates the White Rabbit Input engine
as a SpecializedAgent in the Cosmic Council hierarchy.

White Rabbit is the entry point - receiving input prompts
and initiating the cosmic cycle.

"Follow the White Rabbit" - The beginning of every journey.
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

from .engine import WhiteRabbitEngine, create_white_rabbit, WhiteRabbitResult
from .models import WhiteRabbitConfig, InputType, WHITE_RABBIT_SYMBOL

logger = structlog.get_logger(__name__)


class WhiteRabbitAgentRole:
    """Extended agent roles for White Rabbit."""
    INPUT_HANDLER = "input_handler"
    CYCLE_STARTER = "cycle_starter"


class WhiteRabbitAgent(BaseTotemAgent):
    """
    Input Agent for the White Rabbit - the entry point.

    White Rabbit initiates the cosmic cycle by:
    1. Receiving and validating input prompts
    2. Classifying the intent of the input
    3. Initiating the cycle with Red Owl

    The Three Falsifiable Criteria:
    1. Input reception (prompts properly received)
    2. Intent classification (intent correctly identified)
    3. Cycle initiation (Red Owl properly invoked)
    """

    def __init__(
        self,
        agent_id: str,
        llm_provider: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        input_config: Optional[WhiteRabbitConfig] = None,
    ):
        """
        Initialize the White Rabbit Agent.

        Args:
            agent_id: Unique agent identifier
            llm_provider: LLM provider (optional)
            config: General agent configuration
            input_config: White Rabbit specific configuration
        """
        # Initialize as White Rabbit (use DATA_COLLECTOR as entry point match)
        super().__init__(
            agent_id=agent_id,
            totem=TotemType.RED_OWL,  # White Rabbit leads to Red Owl
            role=AgentRole.DATA_MINER,  # Entry point role
            llm_provider=llm_provider,
            config=config,
        )

        # Override totem info for White Rabbit
        self.totem_name = "White Rabbit"
        self.totem_symbol = WHITE_RABBIT_SYMBOL

        # Override the system prompt for input handling
        self.system_prompt = """You are White Rabbit - the entry point to the Cosmic Council.
Your role is to receive INPUT and initiate the CYCLE.

You begin every journey by:
- Receiving and validating input prompts
- Classifying the intent and extracting key information
- Initiating the inquiry cycle with Red Owl

You embody three principles:
1. All prompts are properly received and parsed
2. The intent/type is correctly identified
3. Red Owl is properly invoked with structured input

Follow the White Rabbit. Every journey begins with a single prompt."""

        # Create the input engine
        self.input_engine = create_white_rabbit(config=input_config)

        logger.info(
            "white_rabbit_agent_initialized",
            agent_id=agent_id,
        )

    async def process_task(self, context: TaskContext) -> AgentResult:
        """
        Process an input task.

        Args:
            context: Task context with input

        Returns:
            AgentResult with cycle initiation
        """
        start_time = time.time()

        try:
            # Extract input from context
            input_data = context.input_data if context.input_data else {}
            content = input_data.get("content", input_data.get("prompt", ""))

            # If no content in input_data, use task description
            if not content and context.task_description:
                content = context.task_description

            input_type_str = input_data.get("input_type", "text")
            input_type = InputType(input_type_str) if input_type_str in [t.value for t in InputType] else InputType.TEXT

            source_id = input_data.get("source_id", context.user_id or "")
            source_type = input_data.get("source_type", "user")
            channel = input_data.get("channel", "api")
            metadata = input_data.get("metadata", {})

            # Process the input
            result: WhiteRabbitResult = await self.input_engine.process(
                content=content,
                input_type=input_type,
                source_id=source_id,
                source_type=source_type,
                channel=channel,
                metadata=metadata,
                context=input_data.get("context", {}),
            )

            # Update agent metrics
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (
                (self.avg_processing_time * (self.tasks_completed - 1) + processing_time)
                / self.tasks_completed
            )

            # Build output
            output = {
                "cycle_id": result.cycle_initiation.cycle_id if result.cycle_initiation else None,
                "cycle_number": result.cycle_initiation.cycle_number if result.cycle_initiation else 0,
                "initiated": result.cycle_initiation.initiated if result.cycle_initiation else False,
                "red_owl_invoked": result.initiation_result.red_owl_invoked if result.initiation_result else False,
                "intent": {
                    "category": result.classification_result.intent.category.value if result.classification_result else None,
                    "confidence": result.classification_result.intent.confidence if result.classification_result else 0.0,
                    "subject": result.classification_result.intent.subject if result.classification_result else "",
                    "urgency": result.classification_result.intent.urgency.value if result.classification_result else "normal",
                } if result.classification_result else None,
                "inquiry_seed": result.cycle_initiation.inquiry_seed if result.cycle_initiation else None,
                "initial_questions": (
                    result.classification_result.intent.initial_questions
                    if result.classification_result else []
                ),
                "reasoning": result.reasoning,
                "warnings": result.warnings,
                "criterion_metrics": {
                    "input_reception": result.input_reception,
                    "intent_classification": result.intent_classification,
                    "cycle_initiation": result.cycle_initiation_rate,
                },
            }

            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=result.success,
                output=output,
                confidence=result.intent_classification if result.success else 0.0,
                processing_time=processing_time,
                metadata={
                    "cycle_id": result.cycle_initiation.cycle_id if result.cycle_initiation else None,
                    "initiated": result.cycle_initiation.initiated if result.cycle_initiation else False,
                },
            )

        except Exception as e:
            logger.error(f"Input processing failed: {e}")
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

        White Rabbit always hands off to Red Owl after initiating.
        """
        if context.metadata.get("cycle_initiated"):
            inquiry_seed = context.metadata.get("inquiry_seed", {})

            # Hand off to Red Owl
            return AgentHandoff(
                from_agent=self.agent_id,
                to_specialization=AgentSpecialization.DATA_COLLECTOR,  # Red Owl
                reason=HandoffReason.COMPLETED,
                context={
                    "inquiry_seed": inquiry_seed,
                    "task": "Begin inquiry cycle",
                },
                confidence=0.95,
            )

        return None

    def get_handoff_targets(self) -> List[AgentSpecialization]:
        """Get possible handoff targets."""
        return [
            AgentSpecialization.DATA_COLLECTOR,  # Red Owl
        ]

    def get_input_metrics(self) -> Dict[str, Any]:
        """Get input-specific metrics."""
        return self.input_engine.get_metrics()

    def set_red_owl_callback(self, callback) -> None:
        """Set the callback for invoking Red Owl."""
        self.input_engine.set_red_owl_callback(callback)


# Factory function
def create_white_rabbit_agent(
    agent_id: str = "white_rabbit_1",
    llm_provider: Optional[Any] = None,
    input_config: Optional[WhiteRabbitConfig] = None,
    **kwargs,
) -> WhiteRabbitAgent:
    """Create a White Rabbit Agent instance."""
    return WhiteRabbitAgent(
        agent_id=agent_id,
        llm_provider=llm_provider,
        input_config=input_config,
        **kwargs,
    )


# Singleton instance
_input_agent: Optional[WhiteRabbitAgent] = None


def get_input_agent() -> WhiteRabbitAgent:
    """Get the default input agent instance."""
    global _input_agent
    if _input_agent is None:
        _input_agent = create_white_rabbit_agent()
    return _input_agent
