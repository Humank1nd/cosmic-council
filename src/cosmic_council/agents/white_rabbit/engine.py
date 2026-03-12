"""
WHITE RABBIT - Input Engine.

The main orchestration engine for White Rabbit.
Coordinates input reception, intent classification, and cycle initiation.

"Follow the White Rabbit" - The beginning of every journey.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime

import structlog

from .models import (
    InputPrompt,
    InputType,
    Intent,
    CycleInitiation,
    WhiteRabbitConfig,
)
from .input_receiver import (
    InputReceiver,
    ReceivedInput,
    create_input_receiver,
)
from .intent_classifier import (
    IntentClassifier,
    ClassificationResult,
    create_intent_classifier,
)
from .cycle_initiator import (
    CycleInitiator,
    InitiationResult,
    create_cycle_initiator,
)

logger = structlog.get_logger(__name__)


@dataclass
class WhiteRabbitResult:
    """Result of White Rabbit processing."""
    success: bool = False
    cycle_initiation: Optional[CycleInitiation] = None

    # Criterion metrics (0-1)
    input_reception: float = 0.0     # Criterion 1
    intent_classification: float = 0.0  # Criterion 2
    cycle_initiation_rate: float = 0.0   # Criterion 3

    # Component results
    received_input: Optional[ReceivedInput] = None
    classification_result: Optional[ClassificationResult] = None
    initiation_result: Optional[InitiationResult] = None

    # Timing
    duration_ms: int = 0

    # Diagnostics
    reasoning: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class WhiteRabbitEngine:
    """
    White Rabbit Input Engine.

    The entry point to the Cosmic Council cycle.
    Receives input, classifies intent, and initiates the inquiry cycle
    by invoking Red Owl.

    Three Falsifiable Criteria:
    1. Input reception - all prompts are properly received and parsed
    2. Intent classification - the intent/type is correctly identified
    3. Cycle initiation - Red Owl is properly invoked with structured input
    """

    def __init__(
        self,
        config: Optional[WhiteRabbitConfig] = None,
        input_receiver: Optional[InputReceiver] = None,
        intent_classifier: Optional[IntentClassifier] = None,
        cycle_initiator: Optional[CycleInitiator] = None,
    ):
        """
        Initialize the White Rabbit engine.

        Args:
            config: Configuration
            input_receiver: Input receiver component
            intent_classifier: Intent classifier component
            cycle_initiator: Cycle initiator component
        """
        self.config = config or WhiteRabbitConfig()
        self.input_receiver = input_receiver or create_input_receiver(self.config)
        self.intent_classifier = intent_classifier or create_intent_classifier(self.config)
        self.cycle_initiator = cycle_initiator or create_cycle_initiator(self.config)

        logger.info(
            "white_rabbit_engine_initialized",
            auto_initiate=self.config.auto_initiate,
        )

    async def process(
        self,
        content: str,
        input_type: InputType = InputType.TEXT,
        source_id: str = "",
        source_type: str = "user",
        channel: str = "api",
        metadata: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> WhiteRabbitResult:
        """
        Process an input and initiate a cosmic cycle.

        Args:
            content: The input content
            input_type: Type of input
            source_id: Source identifier
            source_type: Type of source
            channel: Input channel
            metadata: Additional metadata
            context: Processing context

        Returns:
            WhiteRabbitResult
        """
        start_time = time.time()
        context = context or {}
        reasoning: List[str] = []
        warnings: List[str] = []

        try:
            # Phase 1: Receive and validate input (Criterion 1)
            received = self.input_receiver.receive(
                content=content,
                input_type=input_type,
                source_id=source_id,
                source_type=source_type,
                channel=channel,
                metadata=metadata,
            )

            # Calculate input reception rate
            input_reception = 1.0 if received.validation.is_valid else 0.0

            if not received.validation.is_valid:
                reasoning.append(f"Input validation failed: {received.validation.errors}")
                duration_ms = int((time.time() - start_time) * 1000)
                return WhiteRabbitResult(
                    success=False,
                    input_reception=input_reception,
                    received_input=received,
                    duration_ms=duration_ms,
                    reasoning=reasoning,
                    warnings=warnings,
                )

            reasoning.append(
                f"Input received and validated: {len(content)} chars, "
                f"type={input_type.value}"
            )

            # Phase 2: Classify intent (Criterion 2)
            classification = self.intent_classifier.classify(
                prompt=received.prompt,
                context=context,
            )

            # Calculate classification rate based on confidence
            intent_classification = classification.classification_confidence

            reasoning.append(
                f"Intent classified: {classification.intent.category.value} "
                f"(confidence: {classification.classification_confidence:.1%})"
            )

            if classification.alternative_intents:
                alt_cats = [i.category.value for i in classification.alternative_intents]
                reasoning.append(f"Alternative interpretations: {', '.join(alt_cats)}")

            # Phase 3: Initiate cycle (Criterion 3)
            initiation = await self.cycle_initiator.initiate(
                prompt=received.prompt,
                intent=classification.intent,
                context=context,
            )

            # Calculate cycle initiation rate
            cycle_initiation_rate = 1.0 if initiation.initiation.initiated else 0.0
            if initiation.red_owl_invoked:
                cycle_initiation_rate = 1.0
            elif initiation.initiation.initiated:
                cycle_initiation_rate = 0.8  # Initiated but not invoked

            reasoning.append(
                f"Cycle initiated: {initiation.initiation.cycle_id} "
                f"(number: {initiation.initiation.cycle_number})"
            )

            if initiation.red_owl_invoked:
                reasoning.append("Red Owl invoked successfully")
            else:
                warnings.append("Red Owl not invoked (no callback set or auto-initiate disabled)")

            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Overall success
            success = (
                input_reception >= 0.8 and
                intent_classification >= 0.5 and
                cycle_initiation_rate >= 0.8
            )

            logger.info(
                "white_rabbit_processing_complete",
                cycle_id=initiation.initiation.cycle_id,
                success=success,
                input_reception=input_reception,
                intent_classification=intent_classification,
                cycle_initiation_rate=cycle_initiation_rate,
                duration_ms=duration_ms,
            )

            return WhiteRabbitResult(
                success=success,
                cycle_initiation=initiation.initiation,
                input_reception=input_reception,
                intent_classification=intent_classification,
                cycle_initiation_rate=cycle_initiation_rate,
                received_input=received,
                classification_result=classification,
                initiation_result=initiation,
                duration_ms=duration_ms,
                reasoning=reasoning,
                warnings=warnings,
            )

        except Exception as e:
            logger.error(
                "white_rabbit_processing_failed",
                error=str(e),
            )

            duration_ms = int((time.time() - start_time) * 1000)
            warnings.append(f"Processing failed: {str(e)}")

            return WhiteRabbitResult(
                success=False,
                duration_ms=duration_ms,
                reasoning=reasoning,
                warnings=warnings,
            )

    async def process_feedback(
        self,
        feedback: Dict[str, Any],
        cycle_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> WhiteRabbitResult:
        """
        Process feedback from Black Snake to continue the cycle.

        Args:
            feedback: Feedback from Black Snake
            cycle_id: The cycle that generated the feedback
            context: Additional context

        Returns:
            WhiteRabbitResult
        """
        # Receive feedback as structured input
        received = self.input_receiver.receive_feedback(
            feedback=feedback,
            cycle_id=cycle_id,
        )

        if not received.validation.is_valid:
            return WhiteRabbitResult(
                success=False,
                input_reception=0.0,
                received_input=received,
                reasoning=["Feedback validation failed"],
                warnings=received.validation.errors,
            )

        # Process the feedback prompt
        return await self.process(
            content=received.prompt.content,
            input_type=InputType.FEEDBACK,
            source_id="black_snake",
            source_type="black_snake",
            channel="internal",
            metadata={
                "feedback": feedback,
                "parent_cycle_id": cycle_id,
            },
            context=context,
        )

    def set_red_owl_callback(self, callback: Callable) -> None:
        """Set the callback for invoking Red Owl."""
        self.cycle_initiator.set_red_owl_callback(callback)

    def get_metrics(self) -> Dict[str, Any]:
        """Get combined metrics from all components."""
        return {
            "input_receiver": self.input_receiver.get_metrics(),
            "intent_classifier": self.intent_classifier.get_metrics(),
            "cycle_initiator": self.cycle_initiator.get_metrics(),
        }


# Global instance
_white_rabbit_instance: Optional[WhiteRabbitEngine] = None


def create_white_rabbit(
    config: Optional[WhiteRabbitConfig] = None,
) -> WhiteRabbitEngine:
    """Factory function to create a WhiteRabbitEngine."""
    return WhiteRabbitEngine(config=config)


def get_white_rabbit() -> WhiteRabbitEngine:
    """Get or create the global WhiteRabbitEngine instance."""
    global _white_rabbit_instance
    if _white_rabbit_instance is None:
        _white_rabbit_instance = create_white_rabbit()
    return _white_rabbit_instance


async def follow_the_rabbit(
    content: str,
    input_type: InputType = InputType.TEXT,
    context: Optional[Dict[str, Any]] = None,
) -> WhiteRabbitResult:
    """
    Convenience function to process input and start a cycle.

    "Follow the White Rabbit" - every journey begins here.

    Args:
        content: The input content
        input_type: Type of input
        context: Processing context

    Returns:
        WhiteRabbitResult
    """
    engine = get_white_rabbit()
    return await engine.process(
        content=content,
        input_type=input_type,
        context=context,
    )
