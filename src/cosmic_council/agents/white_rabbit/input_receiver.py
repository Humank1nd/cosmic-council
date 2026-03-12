"""
WHITE RABBIT - Input Receiver.

Receives and validates input prompts.
This implements Criterion 1: Input reception.

All prompts must be properly received and parsed.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

import structlog

from .models import (
    InputPrompt,
    InputType,
    InputStatus,
    InputValidation,
    WhiteRabbitConfig,
)

logger = structlog.get_logger(__name__)


@dataclass
class ReceivedInput:
    """Result of receiving an input."""
    prompt: InputPrompt
    validation: InputValidation
    received: bool = True
    processing_time_ms: int = 0


@dataclass
class BatchReceiveResult:
    """Result of receiving multiple inputs."""
    inputs: List[ReceivedInput] = field(default_factory=list)
    total_received: int = 0
    total_valid: int = 0
    total_invalid: int = 0
    duration_ms: int = 0


class InputReceiver:
    """
    Receives and validates input prompts.

    Criterion 1: All prompts are properly received and parsed.
    """

    def __init__(
        self,
        config: Optional[WhiteRabbitConfig] = None,
    ):
        """
        Initialize the input receiver.

        Args:
            config: Configuration
        """
        self.config = config or WhiteRabbitConfig()

        # Track received inputs
        self._received_count: int = 0
        self._valid_count: int = 0
        self._invalid_count: int = 0

        # Rate limiting (simple in-memory)
        self._rate_tracker: Dict[str, List[datetime]] = {}

        logger.info("input_receiver_initialized")

    def receive(
        self,
        content: str,
        input_type: InputType = InputType.TEXT,
        source_id: str = "",
        source_type: str = "user",
        channel: str = "api",
        metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        parent_cycle_id: Optional[str] = None,
    ) -> ReceivedInput:
        """
        Receive a single input prompt.

        Args:
            content: The input content
            input_type: Type of input
            source_id: Source identifier
            source_type: Type of source
            channel: Input channel
            metadata: Additional metadata
            session_id: Session identifier
            parent_cycle_id: Parent cycle if feedback

        Returns:
            ReceivedInput
        """
        import time
        start_time = time.time()

        # Create the prompt
        prompt = InputPrompt(
            content=content,
            input_type=input_type,
            source_id=source_id,
            source_type=source_type,
            channel=channel,
            metadata=metadata or {},
            session_id=session_id,
            parent_cycle_id=parent_cycle_id,
        )

        # Validate
        validation = self._validate(prompt)

        # Update prompt status
        if validation.is_valid:
            prompt.status = InputStatus.VALIDATED
            prompt.content = validation.sanitized_content
            self._valid_count += 1
        else:
            prompt.status = InputStatus.REJECTED
            prompt.validation_errors = validation.errors
            self._invalid_count += 1

        self._received_count += 1
        processing_time = int((time.time() - start_time) * 1000)

        logger.debug(
            "input_received",
            prompt_id=prompt.id,
            input_type=input_type.value,
            is_valid=validation.is_valid,
            length=len(content),
        )

        return ReceivedInput(
            prompt=prompt,
            validation=validation,
            received=True,
            processing_time_ms=processing_time,
        )

    def receive_structured(
        self,
        data: Dict[str, Any],
        source_id: str = "",
        source_type: str = "system",
        channel: str = "internal",
    ) -> ReceivedInput:
        """
        Receive structured input (e.g., from API or Black Snake).

        Args:
            data: Structured data dictionary
            source_id: Source identifier
            source_type: Type of source
            channel: Input channel

        Returns:
            ReceivedInput
        """
        # Extract content from structured data
        content = data.get("content", data.get("message", data.get("prompt", "")))
        if not content and "questions" in data:
            # From Black Snake feedback
            content = "; ".join(data.get("questions", []))

        input_type = InputType.STRUCTURED
        if data.get("type") == "feedback":
            input_type = InputType.FEEDBACK
        elif data.get("type") == "event":
            input_type = InputType.EVENT
        elif data.get("type") == "command":
            input_type = InputType.COMMAND

        return self.receive(
            content=content,
            input_type=input_type,
            source_id=source_id,
            source_type=source_type,
            channel=channel,
            metadata=data.get("metadata", {}),
            session_id=data.get("session_id"),
            parent_cycle_id=data.get("cycle_id") or data.get("parent_cycle_id"),
        )

    def receive_feedback(
        self,
        feedback: Dict[str, Any],
        cycle_id: str,
    ) -> ReceivedInput:
        """
        Receive feedback from Black Snake (completing the loop).

        Args:
            feedback: Feedback from Black Snake
            cycle_id: The cycle that generated the feedback

        Returns:
            ReceivedInput
        """
        # Build content from feedback
        questions = feedback.get("new_questions", [])
        hypotheses = feedback.get("hypotheses_to_test", [])

        content_parts = []
        if questions:
            content_parts.append("Questions: " + "; ".join(questions))
        if hypotheses:
            content_parts.append("Hypotheses: " + "; ".join(hypotheses))

        content = " | ".join(content_parts) if content_parts else "Continue cycle"

        return self.receive(
            content=content,
            input_type=InputType.FEEDBACK,
            source_id="black_snake",
            source_type="black_snake",
            channel="internal",
            metadata={
                "feedback": feedback,
                "priority": feedback.get("priority", "medium"),
                "urgency": feedback.get("urgency", "normal"),
            },
            parent_cycle_id=cycle_id,
        )

    def receive_batch(
        self,
        inputs: List[Dict[str, Any]],
    ) -> BatchReceiveResult:
        """
        Receive multiple inputs.

        Args:
            inputs: List of input dictionaries

        Returns:
            BatchReceiveResult
        """
        import time
        start_time = time.time()

        results: List[ReceivedInput] = []
        valid_count = 0
        invalid_count = 0

        for input_data in inputs:
            if isinstance(input_data, str):
                result = self.receive(content=input_data)
            else:
                result = self.receive_structured(input_data)

            results.append(result)
            if result.validation.is_valid:
                valid_count += 1
            else:
                invalid_count += 1

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "batch_inputs_received",
            total=len(inputs),
            valid=valid_count,
            invalid=invalid_count,
            duration_ms=duration_ms,
        )

        return BatchReceiveResult(
            inputs=results,
            total_received=len(results),
            total_valid=valid_count,
            total_invalid=invalid_count,
            duration_ms=duration_ms,
        )

    def _validate(self, prompt: InputPrompt) -> InputValidation:
        """Validate an input prompt."""
        errors: List[str] = []
        warnings: List[str] = []

        content = prompt.content
        sanitized = content

        # Check input type is allowed
        if prompt.input_type not in self.config.allowed_input_types:
            errors.append(f"Input type {prompt.input_type.value} not allowed")

        # Check length
        if len(content) < self.config.min_input_length:
            errors.append(f"Input too short (min {self.config.min_input_length} chars)")

        if len(content) > self.config.max_input_length:
            errors.append(f"Input too long (max {self.config.max_input_length} chars)")
            sanitized = content[:self.config.max_input_length]

        # Sanitize content
        sanitized = self._sanitize(sanitized)

        # Check for empty after sanitization
        if not sanitized.strip():
            errors.append("Input is empty after sanitization")

        # Rate limiting check
        if not self._check_rate_limit(prompt.source_id):
            errors.append("Rate limit exceeded")

        # Detect language (simple heuristic)
        detected_language = self._detect_language(sanitized)

        # Check for feedback loop validity
        if prompt.is_feedback_loop and not self.config.accept_feedback:
            errors.append("Feedback loop not enabled")

        return InputValidation(
            prompt_id=prompt.id,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_content=sanitized,
            detected_language=detected_language,
            content_length=len(sanitized),
            has_attachments=len(prompt.attachments) > 0,
        )

    def _sanitize(self, content: str) -> str:
        """Sanitize input content."""
        # Strip whitespace
        content = content.strip()

        # Remove null bytes
        content = content.replace("\x00", "")

        # Normalize whitespace
        content = re.sub(r"\s+", " ", content)

        # Remove control characters (except newlines and tabs)
        content = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", content)

        return content

    def _detect_language(self, content: str) -> str:
        """Simple language detection heuristic."""
        # Very basic - just check for common patterns
        # In production, use a proper language detection library

        # Check for CJK characters
        if re.search(r"[\u4e00-\u9fff]", content):
            return "zh"
        if re.search(r"[\u3040-\u309f\u30a0-\u30ff]", content):
            return "ja"
        if re.search(r"[\uac00-\ud7af]", content):
            return "ko"

        # Default to English
        return "en"

    def _check_rate_limit(self, source_id: str) -> bool:
        """Check if source is within rate limit."""
        if not source_id:
            return True

        now = datetime.utcnow()
        minute_ago = datetime(
            now.year, now.month, now.day,
            now.hour, now.minute, 0
        )

        # Get requests from this source in the last minute
        if source_id not in self._rate_tracker:
            self._rate_tracker[source_id] = []

        # Clean old entries
        self._rate_tracker[source_id] = [
            t for t in self._rate_tracker[source_id]
            if t > minute_ago
        ]

        # Check limit
        if len(self._rate_tracker[source_id]) >= self.config.rate_limit_per_source:
            return False

        # Record this request
        self._rate_tracker[source_id].append(now)
        return True

    def get_metrics(self) -> Dict[str, Any]:
        """Get receiver metrics."""
        return {
            "total_received": self._received_count,
            "total_valid": self._valid_count,
            "total_invalid": self._invalid_count,
            "validation_rate": (
                self._valid_count / self._received_count
                if self._received_count > 0 else 0.0
            ),
        }


def create_input_receiver(
    config: Optional[WhiteRabbitConfig] = None,
) -> InputReceiver:
    """Factory function to create an InputReceiver."""
    return InputReceiver(config=config)
