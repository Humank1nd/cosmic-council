"""
BLACK SNAKE - Execution & Recursion Models.

Core data structures for the 7th step in the Cosmic Council.
Black Snake closes the cycle - executing actions and feeding
outcomes back to Red Owl for the next iteration.

The Ouroboros - the serpent consuming its tail.

Three Falsifiable Criteria:
1. Execution completion - all assigned actions are executed
2. Outcome capture - results are properly recorded
3. Cycle recursion - insights feed back to initiate new inquiry

Chakra: Sahasrara (Crown) - Transcendence, Unity, Completion
Gemstone: Obsidian - Transformation, Protection, Truth
Quantum Concept: Quantum Measurement - Observation collapses possibility into reality
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


class ExecutionStatus(Enum):
    """Status of action execution."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    SKIPPED = "skipped"


class OutcomeType(Enum):
    """Type of execution outcome."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    UNEXPECTED = "unexpected"
    LEARNING = "learning"


class InsightType(Enum):
    """Type of insight generated from execution."""
    ROOT_CAUSE_CONFIRMED = "root_cause_confirmed"
    ROOT_CAUSE_INVALIDATED = "root_cause_invalidated"
    NEW_HYPOTHESIS = "new_hypothesis"
    PATTERN_DETECTED = "pattern_detected"
    ANOMALY_DISCOVERED = "anomaly_discovered"
    PROCESS_IMPROVEMENT = "process_improvement"
    KNOWLEDGE_GAP = "knowledge_gap"
    LEARNING = "learning"


class CyclePhase(Enum):
    """Phase of the cosmic cycle."""
    INQUIRY = "inquiry"           # Red Owl
    PLANNING = "planning"         # Orange Orangutan
    CREATION = "creation"         # Yellow Honeybee
    SCHEDULING = "scheduling"     # Green Turtle
    LOCATION = "location"         # Blue Dolphin
    ASSIGNMENT = "assignment"     # Purple Elephant
    EXECUTION = "execution"       # Black Snake
    RECURSION = "recursion"       # Return to Red Owl


@dataclass
class ExecutionRecord:
    """
    Record of a single action execution.

    Criterion 1: All assigned actions are executed.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # References from previous agents
    action_id: str = ""
    assignment_id: str = ""
    target_id: str = ""
    slot_id: str = ""

    # Execution details
    status: ExecutionStatus = ExecutionStatus.PENDING
    executor_id: str = ""
    executor_type: str = ""  # human, automation, service

    # Timing
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: int = 0

    # Results
    success: bool = False
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    error_code: Optional[str] = None

    # Rollback
    rollback_available: bool = False
    rollback_executed: bool = False
    rollback_data: Dict[str, Any] = field(default_factory=dict)

    # Audit
    audit_event_id: Optional[str] = None
    changes_made: List[str] = field(default_factory=list)
    resources_affected: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionOutcome:
    """
    Captured outcome of an execution.

    Criterion 2: Results are properly recorded.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # Reference
    execution_id: str = ""
    action_id: str = ""

    # Outcome classification
    outcome_type: OutcomeType = OutcomeType.SUCCESS
    severity: str = "info"  # info, warning, error, critical

    # What happened
    summary: str = ""
    details: str = ""
    metrics: Dict[str, float] = field(default_factory=dict)

    # What we learned
    observations: List[str] = field(default_factory=list)
    surprises: List[str] = field(default_factory=list)  # Unexpected results

    # Impact
    impact_score: float = 0.0  # 0-1, how significant
    affected_services: List[str] = field(default_factory=list)
    affected_users: int = 0

    # Timing
    captured_at: datetime = field(default_factory=datetime.utcnow)

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CycleInsight:
    """
    Insight generated for the next cycle.

    Criterion 3: Insights feed back to initiate new inquiry.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # Source
    cycle_id: str = ""
    execution_ids: List[str] = field(default_factory=list)

    # Insight details
    insight_type: InsightType = InsightType.LEARNING
    title: str = ""
    description: str = ""
    confidence: float = 0.0  # 0-1

    # For Red Owl
    new_questions: List[str] = field(default_factory=list)
    hypotheses_to_test: List[str] = field(default_factory=list)
    evidence_needed: List[str] = field(default_factory=list)

    # Priority for next cycle
    priority: str = "medium"  # low, medium, high, critical
    urgency: str = "normal"  # normal, soon, immediate

    # Context
    related_patterns: List[str] = field(default_factory=list)
    similar_past_insights: List[str] = field(default_factory=list)

    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CycleState:
    """
    State of a complete cosmic cycle.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    cycle_number: int = 1

    # Phase tracking
    current_phase: CyclePhase = CyclePhase.INQUIRY
    phase_history: List[Dict[str, Any]] = field(default_factory=list)

    # Artifacts from each phase
    inquiry_id: Optional[str] = None          # Red Owl output
    plan_id: Optional[str] = None             # Orange Orangutan output
    specification_id: Optional[str] = None    # Yellow Honeybee output
    schedule_id: Optional[str] = None         # Green Turtle output
    location_plan_id: Optional[str] = None    # Blue Dolphin output
    responsibility_plan_id: Optional[str] = None  # Purple Elephant output

    # Black Snake outputs
    executions: List[ExecutionRecord] = field(default_factory=list)
    outcomes: List[ExecutionOutcome] = field(default_factory=list)
    insights: List[CycleInsight] = field(default_factory=list)

    # Cycle metrics
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: int = 0

    # Success metrics
    actions_planned: int = 0
    actions_executed: int = 0
    actions_succeeded: int = 0
    actions_failed: int = 0

    # Next cycle
    next_cycle_id: Optional[str] = None
    feeds_forward: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_complete(self) -> bool:
        """Check if cycle is complete."""
        return self.current_phase == CyclePhase.RECURSION and self.feeds_forward

    @property
    def success_rate(self) -> float:
        """Calculate execution success rate."""
        if self.actions_executed == 0:
            return 0.0
        return self.actions_succeeded / self.actions_executed


@dataclass
class ExecutionPlan:
    """
    Complete execution plan from Black Snake.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # Source
    cycle_id: str = ""
    responsibility_plan_id: str = ""

    # Executions
    executions: List[ExecutionRecord] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)

    # Outcomes
    outcomes: List[ExecutionOutcome] = field(default_factory=list)

    # Insights for next cycle
    insights: List[CycleInsight] = field(default_factory=list)
    next_cycle_seed: Optional[Dict[str, Any]] = None

    # Metrics
    executions_completed: int = 0
    executions_failed: int = 0
    outcomes_captured: int = 0
    insights_generated: int = 0

    # Validity
    is_valid: bool = False
    validation_errors: List[str] = field(default_factory=list)

    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Compute derived fields."""
        self._compute_metrics()

    def _compute_metrics(self):
        """Compute plan metrics."""
        if not self.executions:
            return

        self.executions_completed = sum(
            1 for e in self.executions
            if e.status == ExecutionStatus.COMPLETED
        )
        self.executions_failed = sum(
            1 for e in self.executions
            if e.status == ExecutionStatus.FAILED
        )
        self.outcomes_captured = len(self.outcomes)
        self.insights_generated = len(self.insights)


@dataclass
class BlackSnakeConfig:
    """Configuration for Black Snake execution."""

    # Execution settings
    parallel_execution: bool = False
    max_parallel: int = 3
    execution_timeout_seconds: int = 300
    retry_failed: bool = True
    max_retries: int = 2

    # Outcome capture
    capture_all_outputs: bool = True
    capture_metrics: bool = True
    capture_surprises: bool = True

    # Insight generation
    generate_insights: bool = True
    min_confidence_threshold: float = 0.5
    max_insights_per_cycle: int = 10

    # Recursion
    auto_feed_forward: bool = True
    require_human_review: bool = False
    min_success_rate_for_recursion: float = 0.5

    # Safety
    enable_rollback: bool = True
    dry_run: bool = False


# The Ouroboros - representing the eternal cycle
OUROBOROS_SYMBOL = """
        ___
      /     \\
     |  ♾️   |
      \\_____/
    🐍 ─────► 🔴

    The Snake consumes its tail.
    Each ending is a new beginning.
    Execution feeds Inquiry.
"""
