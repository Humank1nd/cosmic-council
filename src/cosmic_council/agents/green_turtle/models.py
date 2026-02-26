"""
GREEN TURTLE (WHEN) - Scheduling Models.

Green Turtle is the GREEN Enterprise in the ROYGBV hierarchy.
The Patient Steward - Manages resources with wisdom and foresight.

═══════════════════════════════════════════════════════════════════════════════
COSMIC IDENTITY
═══════════════════════════════════════════════════════════════════════════════

Chakra: Anahata (Heart) - Love, Balance, Resource Harmony
Gemstone: Emerald - Prosperity, Patience, Balance, Harmony, Wisdom
Quantum Principle: Quantum Teleportation
Element: Water
Frequency: 741Hz
Color: Green (#00FF00)

Core Energy: Love, Balance, Resource Harmony

    The Heart Chakra bridges the lower and upper energy centers, governing
    balance and harmony. Green Turtle embodies this energy through patient
    resource stewardship. Love in this context is care for the system's
    long-term health—ensuring no part is depleted or overextended.

    Energy Flow:
    - Love: Cares for sustainable system health and longevity
    - Balance: Maintains equilibrium between competing demands
    - Resource Harmony: Orchestrates optimal allocation across time and space

───────────────────────────────────────────────────────────────────────────────
QUANTUM TELEPORTATION - "Resources and information can be transferred efficiently."
───────────────────────────────────────────────────────────────────────────────

Quantum Meaning:
    Quantum teleportation allows instantaneous transfer of quantum states over
    vast distances. Instead of moving physical particles, only information is
    transmitted, making the process highly efficient.

Application to Cosmic Council:
    - Efficiency in resource management is key—things don't need to move
      physically if their essence can be transferred.
    - Digital solutions, decentralized finance, and AI-driven optimizations
      allow for smarter, more efficient allocation of time, energy, and resources.
    - Sustainability is about optimal transfer—waste happens when systems fail
      to move information or energy effectively.

Examples:
    - Remote work and AI collaboration allow skills to be used without needing
      physical presence.
    - Cloud computing transfers computational resources instantly to where needed.

Cycle Position: 4️⃣ Optimizing efficiency and sustainability.
    ← Receives from Quantum Superposition (Yellow Honeybee)
    → Feeds into Wave-Particle Duality (Blue Dolphin)

───────────────────────────────────────────────────────────────────────────────
SPIRIT ANIMAL ARCHETYPE - The Turtle 🐢
───────────────────────────────────────────────────────────────────────────────

Totem: The Guardian of Longevity
Natural Strength: Patience, Longevity, Conservation

Why the Turtle?
    - Turtles live for centuries, symbolizing wisdom, sustainability, and
      long-term thinking.
    - They navigate land and sea, mastering the balance between stability
      and adaptability.
    - Their slow, methodical movement ensures steady progress, avoiding
      wasteful efforts.

How the Turtle Guides the Council:
    - Allocates resources wisely, preventing unnecessary waste (Quantum Teleportation).
    - Balances short-term execution with long-term sustainability.
    - Protects energy and prevents burnout, ensuring sustainable progress.

Example:
    An environmentalist developing a circular economy model, ensuring
    zero waste and long-term efficiency.

Guiding Thought: "Sustainability is not just a choice—it is the foundation of all success."

═══════════════════════════════════════════════════════════════════════════════
ROLE & PURPOSE
═══════════════════════════════════════════════════════════════════════════════

Role: Budget & Resource Management
Guiding Question: "When is the right time to act, and what resources do we need?"

Function:
- Manages timelines and resource allocation
- Tracks costs and ensures efficient distribution of resources
- Handles long-term sustainability planning
- Schedules actions within valid time windows
- Respects temporal dependencies between tasks

Core Principle: Steward resources with patience and foresight.

═══════════════════════════════════════════════════════════════════════════════
THREE FALSIFIABLE CRITERIA
═══════════════════════════════════════════════════════════════════════════════

1. Time window compliance - actions scheduled within valid time windows
2. Dependency sequencing - actions respect temporal dependencies
3. Constraint satisfaction - all scheduling constraints are met
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, time as time_obj
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


class SchedulePriority(Enum):
    """Priority level for scheduled actions."""
    CRITICAL = 1      # Must execute immediately
    HIGH = 2          # Execute as soon as possible
    MEDIUM = 3        # Normal priority
    LOW = 4           # Can be deferred
    BACKGROUND = 5    # Execute when resources available


class TimeWindowType(Enum):
    """Type of time window."""
    MAINTENANCE = "maintenance"       # Scheduled maintenance window
    BUSINESS_HOURS = "business_hours" # Normal business hours
    OFF_PEAK = "off_peak"            # Low traffic period
    PEAK = "peak"                     # High traffic period
    EMERGENCY = "emergency"           # Emergency window (any time)
    CUSTOM = "custom"                 # Custom defined window


class ConstraintType(Enum):
    """Type of scheduling constraint."""
    TIME_WINDOW = "time_window"       # Must execute within window
    DEPENDENCY = "dependency"          # Must execute after dependency
    RESOURCE = "resource"              # Resource availability
    RATE_LIMIT = "rate_limit"         # Rate limiting
    COOLDOWN = "cooldown"             # Minimum time between executions
    BLACKOUT = "blackout"             # Cannot execute during period
    SLA = "sla"                       # SLA compliance requirement
    CONCURRENCY = "concurrency"       # Max concurrent executions


class ScheduleStatus(Enum):
    """Status of a scheduled item."""
    PENDING = auto()
    SCHEDULED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    DEFERRED = auto()
    BLOCKED = auto()


@dataclass
class TimeWindow:
    """
    A time window for scheduling.

    Criterion 1: Actions must be scheduled within valid windows.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    type: TimeWindowType = TimeWindowType.CUSTOM

    # Window boundaries
    start_time: Optional[time_obj] = None  # Daily start time
    end_time: Optional[time_obj] = None    # Daily end time

    # Specific datetime range (for one-time windows)
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None

    # Recurrence
    days_of_week: List[int] = field(default_factory=list)  # 0=Monday, 6=Sunday
    timezone: str = "UTC"

    # Metadata
    description: str = ""
    is_preferred: bool = False
    risk_multiplier: float = 1.0  # Higher = riskier window

    metadata: Dict[str, Any] = field(default_factory=dict)

    def contains(self, dt: datetime) -> bool:
        """Check if datetime falls within this window."""
        # Check day of week
        if self.days_of_week and dt.weekday() not in self.days_of_week:
            return False

        # Check specific datetime range
        if self.start_datetime and self.end_datetime:
            return self.start_datetime <= dt <= self.end_datetime

        # Check daily time range
        if self.start_time and self.end_time:
            current_time = dt.time()
            if self.start_time <= self.end_time:
                return self.start_time <= current_time <= self.end_time
            else:  # Window crosses midnight
                return current_time >= self.start_time or current_time <= self.end_time

        return True  # No restrictions


@dataclass
class SchedulingConstraint:
    """
    A constraint on scheduling.

    Criterion 3: All constraints must be satisfied.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    type: ConstraintType = ConstraintType.TIME_WINDOW
    name: str = ""
    description: str = ""

    # Constraint parameters
    target_id: Optional[str] = None      # ID of related entity
    value: Optional[Any] = None          # Constraint value
    min_value: Optional[Any] = None      # Minimum value
    max_value: Optional[Any] = None      # Maximum value

    # Time-based constraints
    duration_seconds: Optional[int] = None
    cooldown_seconds: Optional[int] = None

    # Enforcement
    is_hard: bool = True      # Hard constraint must be satisfied
    priority: int = 100       # Higher = more important
    violation_penalty: float = 1.0  # Penalty for soft constraint violation

    # Status
    is_satisfied: bool = False
    violation_reason: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TemporalDependency:
    """
    A temporal dependency between actions.

    Criterion 2: Actions must respect temporal dependencies.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # The action that must wait
    dependent_action_id: str = ""

    # The action that must complete first
    prerequisite_action_id: str = ""

    # Timing requirements
    min_delay_seconds: int = 0       # Minimum delay after prerequisite
    max_delay_seconds: Optional[int] = None  # Maximum delay (deadline)

    # Type
    dependency_type: str = "finish_to_start"  # finish_to_start, start_to_start, etc.

    # Status
    is_satisfied: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionSlot:
    """
    A scheduled execution slot for an action.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # What is being scheduled
    action_id: str = ""
    spec_id: str = ""

    # When
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    estimated_duration_seconds: int = 60

    # Window
    time_window_id: Optional[str] = None
    time_window_name: str = ""

    # Priority and status
    priority: SchedulePriority = SchedulePriority.MEDIUM
    status: ScheduleStatus = ScheduleStatus.PENDING

    # Constraints
    constraints: List[SchedulingConstraint] = field(default_factory=list)
    dependencies: List[TemporalDependency] = field(default_factory=list)

    # Execution tracking
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3

    # Results
    success: Optional[bool] = None
    error_message: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_overdue(self) -> bool:
        """Check if slot is past its scheduled time."""
        if self.scheduled_start and self.status == ScheduleStatus.PENDING:
            return datetime.utcnow() > self.scheduled_start
        return False

    @property
    def can_execute(self) -> bool:
        """Check if slot can be executed now."""
        if self.status != ScheduleStatus.PENDING:
            return False
        if not all(c.is_satisfied for c in self.constraints if c.is_hard):
            return False
        if not all(d.is_satisfied for d in self.dependencies):
            return False
        return True


@dataclass
class ExecutionSchedule:
    """
    Complete execution schedule for a plan.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # Source references
    implementation_plan_id: str = ""
    action_plan_id: str = ""

    # Slots
    slots: List[ExecutionSlot] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)  # Slot IDs

    # Time windows used
    time_windows: List[TimeWindow] = field(default_factory=list)

    # Constraints
    all_constraints: List[SchedulingConstraint] = field(default_factory=list)
    dependencies: List[TemporalDependency] = field(default_factory=list)

    # Schedule boundaries
    earliest_start: Optional[datetime] = None
    latest_end: Optional[datetime] = None
    total_duration_seconds: int = 0

    # Metrics
    slots_scheduled: int = 0
    slots_pending: int = 0
    constraints_satisfied: int = 0
    constraints_violated: int = 0

    # Validity
    is_valid: bool = False
    validation_errors: List[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Compute derived fields."""
        self._compute_metrics()

    def _compute_metrics(self):
        """Compute schedule metrics."""
        if not self.slots:
            return

        self.slots_scheduled = sum(
            1 for s in self.slots
            if s.status == ScheduleStatus.SCHEDULED
        )
        self.slots_pending = sum(
            1 for s in self.slots
            if s.status == ScheduleStatus.PENDING
        )

        self.constraints_satisfied = sum(
            1 for c in self.all_constraints if c.is_satisfied
        )
        self.constraints_violated = sum(
            1 for c in self.all_constraints if not c.is_satisfied
        )

        # Calculate total duration
        self.total_duration_seconds = sum(
            s.estimated_duration_seconds for s in self.slots
        )

        # Find boundaries
        scheduled_slots = [s for s in self.slots if s.scheduled_start]
        if scheduled_slots:
            self.earliest_start = min(s.scheduled_start for s in scheduled_slots)
            ends = [
                s.scheduled_end or (s.scheduled_start + timedelta(seconds=s.estimated_duration_seconds))
                for s in scheduled_slots
            ]
            self.latest_end = max(ends)

    def get_slot(self, slot_id: str) -> Optional[ExecutionSlot]:
        """Get a slot by ID."""
        for slot in self.slots:
            if slot.id == slot_id:
                return slot
        return None

    def get_next_slot(self) -> Optional[ExecutionSlot]:
        """Get the next slot ready for execution."""
        for slot_id in self.execution_order:
            slot = self.get_slot(slot_id)
            if slot and slot.can_execute:
                return slot
        return None


@dataclass
class GreenTurtleConfig:
    """Configuration for Green Turtle scheduling."""

    # Time windows
    default_time_window: TimeWindowType = TimeWindowType.MAINTENANCE
    allow_emergency_override: bool = True

    # Constraints
    respect_sla_constraints: bool = True
    max_concurrent_actions: int = 5
    default_cooldown_seconds: int = 60

    # Scheduling
    scheduling_horizon_hours: int = 24
    min_slot_gap_seconds: int = 30
    prefer_off_peak: bool = True

    # Retries
    max_retries: int = 3
    retry_delay_seconds: int = 300

    # Optimization
    optimize_for_speed: bool = False  # True = ASAP, False = optimal windows
    batch_similar_actions: bool = True


# Pre-defined time windows
STANDARD_TIME_WINDOWS: Dict[str, TimeWindow] = {
    "maintenance": TimeWindow(
        name="Maintenance Window",
        type=TimeWindowType.MAINTENANCE,
        start_time=time_obj(2, 0),   # 2 AM
        end_time=time_obj(6, 0),     # 6 AM
        days_of_week=[0, 1, 2, 3, 4],  # Mon-Fri
        is_preferred=True,
        risk_multiplier=0.5,
        description="Low-traffic maintenance window",
    ),
    "business_hours": TimeWindow(
        name="Business Hours",
        type=TimeWindowType.BUSINESS_HOURS,
        start_time=time_obj(9, 0),   # 9 AM
        end_time=time_obj(17, 0),    # 5 PM
        days_of_week=[0, 1, 2, 3, 4],  # Mon-Fri
        is_preferred=False,
        risk_multiplier=2.0,
        description="Normal business hours - high traffic",
    ),
    "off_peak": TimeWindow(
        name="Off-Peak Hours",
        type=TimeWindowType.OFF_PEAK,
        start_time=time_obj(22, 0),  # 10 PM
        end_time=time_obj(6, 0),     # 6 AM
        days_of_week=[0, 1, 2, 3, 4, 5, 6],  # All days
        is_preferred=True,
        risk_multiplier=0.7,
        description="Low traffic period",
    ),
    "weekend": TimeWindow(
        name="Weekend",
        type=TimeWindowType.OFF_PEAK,
        days_of_week=[5, 6],  # Sat-Sun
        is_preferred=True,
        risk_multiplier=0.6,
        description="Weekend - typically lower traffic",
    ),
    "emergency": TimeWindow(
        name="Emergency Window",
        type=TimeWindowType.EMERGENCY,
        is_preferred=False,
        risk_multiplier=1.5,
        description="Emergency execution - any time",
    ),
}
