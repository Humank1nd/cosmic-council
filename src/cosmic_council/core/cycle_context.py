"""
Cycle Context Management for Agent Orchestrator.

Provides async-safe cycle ID propagation through the entire agent pipeline
using Python's contextvars for proper async context isolation.
"""

import logging
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


# ============== Context Data Classes ==============

@dataclass
class CycleContext:
    """
    Context object carrying cycle information through async operations.

    Attributes:
        cycle_id: Unique identifier for the current cycle
        problem_id: Problem being solved in this cycle
        recursion_depth: Current recursion level (0 = first attempt)
        parent_cycle_id: ID of parent cycle if this is a recursion
        correlation_id: Request correlation ID for distributed tracing
        started_at: When the cycle began
        metadata: Additional context data
    """
    cycle_id: str
    problem_id: str
    recursion_depth: int = 0
    parent_cycle_id: Optional[str] = None
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Track which stages have completed
    completed_stages: List[str] = field(default_factory=list)

    # Accumulated confidence scores per stage
    stage_confidences: Dict[str, float] = field(default_factory=dict)

    # Phase 23: Quantum Resource Allocation (Instant insight movement)
    # A shared dictionary for insights that bypass sequential flow
    instant_insights: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize context for logging/transmission."""
        return {
            "cycle_id": self.cycle_id,
            "problem_id": self.problem_id,
            "recursion_depth": self.recursion_depth,
            "parent_cycle_id": self.parent_cycle_id,
            "correlation_id": self.correlation_id,
            "started_at": self.started_at.isoformat(),
            "completed_stages": self.completed_stages,
            "stage_confidences": self.stage_confidences,
            "instant_insights": self.instant_insights,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CycleContext":
        """Deserialize context from dict."""
        started_at = data.get("started_at")
        if isinstance(started_at, str):
            started_at = datetime.fromisoformat(started_at)
        elif started_at is None:
            started_at = datetime.utcnow()

        return cls(
            cycle_id=data["cycle_id"],
            problem_id=data["problem_id"],
            recursion_depth=data.get("recursion_depth", 0),
            parent_cycle_id=data.get("parent_cycle_id"),
            correlation_id=data.get("correlation_id", str(uuid4())),
            started_at=started_at,
            completed_stages=data.get("completed_stages", []),
            stage_confidences=data.get("stage_confidences", {}),
            instant_insights=data.get("instant_insights", {}),
            metadata=data.get("metadata", {}),
        )

    def mark_stage_complete(self, stage: str, confidence: float) -> None:
        """Record stage completion with confidence score."""
        if stage not in self.completed_stages:
            self.completed_stages.append(stage)
        self.stage_confidences[stage] = confidence
        logger.debug(f"Stage {stage} completed with confidence {confidence:.2f}")

    def get_overall_confidence(self) -> float:
        """Calculate weighted average confidence across completed stages."""
        if not self.stage_confidences:
            return 0.0
        return sum(self.stage_confidences.values()) / len(self.stage_confidences)

    def create_recursion_context(self, reason: str) -> "CycleContext":
        """Create new context for recursion back to Red Owl."""
        new_context = CycleContext(
            cycle_id=str(uuid4()),
            problem_id=self.problem_id,
            recursion_depth=self.recursion_depth + 1,
            parent_cycle_id=self.cycle_id,
            correlation_id=self.correlation_id,  # Preserve correlation
            metadata={
                **self.metadata,
                "recursion_reason": reason,
                "previous_confidences": self.stage_confidences.copy(),
            }
        )
        logger.info(
            f"Created recursion context: {new_context.cycle_id} "
            f"(depth {new_context.recursion_depth}) from {self.cycle_id}"
        )
        return new_context


# ============== Context Variable ==============

_cycle_context: ContextVar[Optional[CycleContext]] = ContextVar(
    'cycle_context',
    default=None
)


# ============== Context Accessors ==============

def get_current_cycle() -> CycleContext:
    """
    Get the current cycle context.

    Raises:
        RuntimeError: If no cycle context is set
    """
    ctx = _cycle_context.get()
    if ctx is None:
        raise RuntimeError("No cycle context available. Ensure operation is within a cycle.")
    return ctx


def get_current_cycle_optional() -> Optional[CycleContext]:
    """Get the current cycle context, or None if not set."""
    return _cycle_context.get()


def get_cycle_id() -> str:
    """Get the current cycle ID, or empty string if not in a cycle."""
    ctx = _cycle_context.get()
    return ctx.cycle_id if ctx else ""


def get_correlation_id() -> str:
    """Get the current correlation ID for distributed tracing."""
    ctx = _cycle_context.get()
    return ctx.correlation_id if ctx else str(uuid4())


# ============== Context Managers ==============

class CycleContextManager:
    """
    Context manager for setting cycle context during async operations.

    Usage:
        async with CycleContextManager(context):
            # All operations here have access to context
            await process_stage(...)
    """

    def __init__(self, context: CycleContext):
        self.context = context
        self._token = None

    def __enter__(self) -> CycleContext:
        self._token = _cycle_context.set(self.context)
        logger.debug(f"Entered cycle context: {self.context.cycle_id}")
        return self.context

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._token is not None:
            _cycle_context.reset(self._token)
            logger.debug(f"Exited cycle context: {self.context.cycle_id}")
        return False

    async def __aenter__(self) -> CycleContext:
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.__exit__(exc_type, exc_val, exc_tb)


def set_cycle_context(context: CycleContext) -> CycleContextManager:
    """
    Set the cycle context for the current async context.

    Usage:
        with set_cycle_context(context):
            await process_stage(...)
    """
    return CycleContextManager(context)


# ============== Factory Functions ==============

def create_cycle_context(
    problem_id: str,
    cycle_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> CycleContext:
    """
    Create a new cycle context for a fresh problem-solving cycle.

    Args:
        problem_id: The problem being solved
        cycle_id: Optional explicit cycle ID (auto-generated if not provided)
        correlation_id: Optional correlation ID for tracing
        metadata: Optional additional context data

    Returns:
        New CycleContext instance
    """
    context = CycleContext(
        cycle_id=cycle_id or str(uuid4()),
        problem_id=problem_id,
        correlation_id=correlation_id or str(uuid4()),
        metadata=metadata or {},
    )
    logger.info(f"Created cycle context: {context.cycle_id} for problem {problem_id}")
    return context


def create_recursion_context_from_current(reason: str) -> CycleContext:
    """
    Create a recursion context from the current context.

    Args:
        reason: Why recursion is needed

    Returns:
        New CycleContext for the recursion

    Raises:
        RuntimeError: If no current context exists
    """
    current = get_current_cycle()
    return current.create_recursion_context(reason)


# ============== Logging Integration ==============

def get_logging_context() -> Dict[str, str]:
    """
    Get cycle context fields for structured logging.

    Returns dict suitable for use with logging extra parameter.
    """
    ctx = _cycle_context.get()
    if ctx is None:
        return {}

    return {
        "cycle_id": ctx.cycle_id,
        "problem_id": ctx.problem_id,
        "correlation_id": ctx.correlation_id,
        "recursion_depth": str(ctx.recursion_depth),
    }


class CycleContextFilter(logging.Filter):
    """
    Logging filter that adds cycle context to log records.

    Usage:
        handler.addFilter(CycleContextFilter())
    """

    def filter(self, record: logging.LogRecord) -> bool:
        ctx = _cycle_context.get()
        if ctx:
            record.cycle_id = ctx.cycle_id
            record.problem_id = ctx.problem_id
            record.correlation_id = ctx.correlation_id
            record.recursion_depth = ctx.recursion_depth
        else:
            record.cycle_id = ""
            record.problem_id = ""
            record.correlation_id = ""
            record.recursion_depth = 0
        return True
