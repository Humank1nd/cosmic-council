"""
WHITE RABBIT - Cycle Initiator.

Initiates the cosmic cycle by invoking Red Owl.
This implements Criterion 3: Cycle initiation.

Red Owl must be properly invoked with structured input.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from uuid import uuid4

import structlog

from .models import (
    InputPrompt,
    Intent,
    IntentCategory,
    CycleInitiation,
    UrgencyLevel,
    WhiteRabbitConfig,
)

logger = structlog.get_logger(__name__)


@dataclass
class InitiationResult:
    """Result of cycle initiation."""
    initiation: CycleInitiation
    red_owl_invoked: bool = False
    red_owl_response: Optional[Dict[str, Any]] = None
    processing_time_ms: int = 0


@dataclass
class BatchInitiationResult:
    """Result of multiple cycle initiations."""
    results: List[InitiationResult] = field(default_factory=list)
    total_initiated: int = 0
    total_invoked: int = 0
    duration_ms: int = 0


# Type for Red Owl callback
RedOwlCallback = Callable[[Dict[str, Any]], "asyncio.Future[Dict[str, Any]]"]


class CycleInitiator:
    """
    Initiates cosmic cycles by invoking Red Owl.

    Criterion 3: Red Owl is properly invoked with structured input.
    """

    def __init__(
        self,
        config: Optional[WhiteRabbitConfig] = None,
        red_owl_callback: Optional[RedOwlCallback] = None,
    ):
        """
        Initialize the cycle initiator.

        Args:
            config: Configuration
            red_owl_callback: Callback to invoke Red Owl
        """
        self.config = config or WhiteRabbitConfig()
        self._red_owl_callback = red_owl_callback

        # Track initiations
        self._initiated_count: int = 0
        self._invoked_count: int = 0
        self._active_cycles: Dict[str, CycleInitiation] = {}
        self._cycle_history: List[CycleInitiation] = []

        # Cycle number tracking
        self._global_cycle_number: int = 0

        logger.info(
            "cycle_initiator_initialized",
            auto_initiate=self.config.auto_initiate,
        )

    async def initiate(
        self,
        prompt: InputPrompt,
        intent: Intent,
        context: Optional[Dict[str, Any]] = None,
    ) -> InitiationResult:
        """
        Initiate a cosmic cycle.

        Args:
            prompt: The input prompt
            intent: Classified intent
            context: Additional context

        Returns:
            InitiationResult
        """
        start_time = time.time()
        context = context or {}

        # Check concurrent cycle limit
        if len(self._active_cycles) >= self.config.max_concurrent_cycles:
            logger.warning(
                "max_concurrent_cycles_reached",
                active=len(self._active_cycles),
                max=self.config.max_concurrent_cycles,
            )
            # Return without invoking
            initiation = CycleInitiation(
                prompt_id=prompt.id,
                intent_id=intent.id,
                initiated=False,
            )
            return InitiationResult(
                initiation=initiation,
                red_owl_invoked=False,
            )

        # Increment global cycle number
        self._global_cycle_number += 1

        # Determine cycle number for this chain
        cycle_number = 1
        if prompt.parent_cycle_id:
            # Find parent cycle
            for cycle in self._cycle_history:
                if cycle.cycle_id == prompt.parent_cycle_id:
                    cycle_number = cycle.cycle_number + 1
                    break

        # Check max depth
        if cycle_number > self.config.max_cycle_depth:
            logger.warning(
                "max_cycle_depth_reached",
                cycle_number=cycle_number,
                max_depth=self.config.max_cycle_depth,
            )
            initiation = CycleInitiation(
                prompt_id=prompt.id,
                intent_id=intent.id,
                cycle_number=cycle_number,
                previous_cycle_id=prompt.parent_cycle_id,
                initiated=False,
            )
            return InitiationResult(
                initiation=initiation,
                red_owl_invoked=False,
            )

        # Build inquiry seed for Red Owl
        inquiry_seed = self._build_inquiry_seed(prompt, intent, context)

        # Build initial context
        initial_context = self._build_initial_context(prompt, intent, context)

        # Handle continuity from previous cycle
        previous_insights = []
        continuity_context = {}
        if prompt.parent_cycle_id and prompt.metadata.get("feedback"):
            feedback = prompt.metadata["feedback"]
            previous_insights = feedback.get("insights", [])
            continuity_context = {
                "previous_questions": feedback.get("new_questions", []),
                "previous_hypotheses": feedback.get("hypotheses_to_test", []),
                "evidence_collected": feedback.get("evidence_collected", []),
            }

        # Map urgency to timeout
        timeout_map = {
            UrgencyLevel.IMMEDIATE: 60,
            UrgencyLevel.CRITICAL: 120,
            UrgencyLevel.HIGH: 180,
            UrgencyLevel.NORMAL: 300,
            UrgencyLevel.LOW: 600,
        }
        timeout = timeout_map.get(intent.urgency, 300)

        # Create the initiation
        initiation = CycleInitiation(
            prompt_id=prompt.id,
            intent_id=intent.id,
            cycle_number=cycle_number,
            inquiry_seed=inquiry_seed,
            initial_context=initial_context,
            previous_cycle_id=prompt.parent_cycle_id,
            previous_insights=previous_insights,
            continuity_context=continuity_context,
            urgency=intent.urgency,
            timeout_seconds=timeout,
            max_depth=self.config.max_cycle_depth,
        )

        # Track active cycle
        self._active_cycles[initiation.cycle_id] = initiation
        self._initiated_count += 1

        # Invoke Red Owl if callback is set and auto-initiate is enabled
        red_owl_response = None
        if self.config.auto_initiate and self._red_owl_callback:
            try:
                red_owl_payload = self._prepare_red_owl_payload(initiation)
                red_owl_response = await self._red_owl_callback(red_owl_payload)
                initiation.red_owl_invoked = True
                self._invoked_count += 1

                logger.info(
                    "red_owl_invoked",
                    cycle_id=initiation.cycle_id,
                    cycle_number=cycle_number,
                )
            except Exception as e:
                logger.error(
                    "red_owl_invocation_failed",
                    cycle_id=initiation.cycle_id,
                    error=str(e),
                )

        initiation.initiated = True
        initiation.initiated_at = datetime.utcnow()

        # Move to history
        self._active_cycles.pop(initiation.cycle_id, None)
        self._cycle_history.append(initiation)

        processing_time = int((time.time() - start_time) * 1000)

        logger.debug(
            "cycle_initiated",
            cycle_id=initiation.cycle_id,
            cycle_number=cycle_number,
            red_owl_invoked=initiation.red_owl_invoked,
            is_feedback_loop=prompt.is_feedback_loop,
        )

        return InitiationResult(
            initiation=initiation,
            red_owl_invoked=initiation.red_owl_invoked,
            red_owl_response=red_owl_response,
            processing_time_ms=processing_time,
        )

    async def initiate_batch(
        self,
        prompts_and_intents: List[tuple],
        context: Optional[Dict[str, Any]] = None,
    ) -> BatchInitiationResult:
        """
        Initiate multiple cycles.

        Args:
            prompts_and_intents: List of (prompt, intent) tuples
            context: Shared context

        Returns:
            BatchInitiationResult
        """
        start_time = time.time()

        results: List[InitiationResult] = []
        invoked_count = 0

        for prompt, intent in prompts_and_intents:
            result = await self.initiate(prompt, intent, context)
            results.append(result)
            if result.red_owl_invoked:
                invoked_count += 1

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "batch_initiation_complete",
            total=len(results),
            invoked=invoked_count,
            duration_ms=duration_ms,
        )

        return BatchInitiationResult(
            results=results,
            total_initiated=len(results),
            total_invoked=invoked_count,
            duration_ms=duration_ms,
        )

    def _build_inquiry_seed(
        self,
        prompt: InputPrompt,
        intent: Intent,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build the inquiry seed for Red Owl."""
        return {
            "prompt": prompt.content,
            "prompt_id": prompt.id,
            "input_type": prompt.input_type.value,
            "intent_category": intent.category.value,
            "subject": intent.subject,
            "action_requested": intent.action_requested,
            "entities": intent.entities,
            "keywords": intent.keywords,
            "initial_questions": intent.initial_questions,
            "suggested_hypotheses": intent.suggested_hypotheses,
            "urgency": intent.urgency.value,
            "complexity": intent.complexity,
            "is_feedback_loop": prompt.is_feedback_loop,
        }

    def _build_initial_context(
        self,
        prompt: InputPrompt,
        intent: Intent,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build initial context for the cycle."""
        return {
            "source_id": prompt.source_id,
            "source_type": prompt.source_type,
            "channel": prompt.channel,
            "session_id": prompt.session_id,
            "conversation_id": prompt.conversation_id,
            "domain": intent.domain,
            "metadata": prompt.metadata,
            **context,
        }

    def _prepare_red_owl_payload(
        self,
        initiation: CycleInitiation,
    ) -> Dict[str, Any]:
        """Prepare the payload for Red Owl invocation."""
        return {
            "cycle_id": initiation.cycle_id,
            "cycle_number": initiation.cycle_number,
            "inquiry_seed": initiation.inquiry_seed,
            "initial_context": initiation.initial_context,
            "previous_cycle_id": initiation.previous_cycle_id,
            "previous_insights": initiation.previous_insights,
            "continuity_context": initiation.continuity_context,
            "urgency": initiation.urgency.value,
            "timeout_seconds": initiation.timeout_seconds,
            "max_depth": initiation.max_depth,
        }

    def set_red_owl_callback(self, callback: RedOwlCallback) -> None:
        """Set the callback for invoking Red Owl."""
        self._red_owl_callback = callback

    def get_active_cycles(self) -> List[CycleInitiation]:
        """Get list of active cycles."""
        return list(self._active_cycles.values())

    def get_cycle(self, cycle_id: str) -> Optional[CycleInitiation]:
        """Get a specific cycle by ID."""
        if cycle_id in self._active_cycles:
            return self._active_cycles[cycle_id]
        for cycle in self._cycle_history:
            if cycle.cycle_id == cycle_id:
                return cycle
        return None

    def get_metrics(self) -> Dict[str, Any]:
        """Get initiator metrics."""
        return {
            "total_initiated": self._initiated_count,
            "total_invoked": self._invoked_count,
            "invocation_rate": (
                self._invoked_count / self._initiated_count
                if self._initiated_count > 0 else 0.0
            ),
            "active_cycles": len(self._active_cycles),
            "global_cycle_number": self._global_cycle_number,
        }


def create_cycle_initiator(
    config: Optional[WhiteRabbitConfig] = None,
    red_owl_callback: Optional[RedOwlCallback] = None,
) -> CycleInitiator:
    """Factory function to create a CycleInitiator."""
    return CycleInitiator(
        config=config,
        red_owl_callback=red_owl_callback,
    )
