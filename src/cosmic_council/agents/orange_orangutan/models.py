"""
ORANGE ORANGUTAN (HOW) - Action Planning Models.

Orange Orangutan is the ORANGE Enterprise in the ROYGBV hierarchy.
The Architect of Strategy - Transforms knowledge into structured action.

═══════════════════════════════════════════════════════════════════════════════
COSMIC IDENTITY
═══════════════════════════════════════════════════════════════════════════════

Chakra: Svadisthana (Sacral) - Flow, Structure, Strategy
Gemstone: Topaz - Focus, Logic, Organization, Courage, Motivation
Quantum Principle: Quantum Tunneling
Element: Earth
Frequency: 528Hz
Color: Orange (#FFA500)

Core Energy: Creativity, Planning, Bold Action

    The Sacral Chakra governs creative flow and structural planning. Orange
    Orangutan channels this energy by transforming raw insights into executable
    strategies. Bold action is not recklessness—it is the courage to commit to
    a plan while remaining adaptable to change.

    Energy Flow:
    - Creativity: Generates innovative approaches to obstacles
    - Planning: Structures chaos into ordered, executable steps
    - Bold Action: Commits decisively while maintaining flexibility

───────────────────────────────────────────────────────────────────────────────
QUANTUM TUNNELING - "Some barriers are not as solid as they appear."
───────────────────────────────────────────────────────────────────────────────

Quantum Meaning:
    In quantum mechanics, particles can "tunnel" through barriers without
    having enough energy to do so classically. Instead of stopping at a wall,
    a particle finds a hidden route through it.

Application to Cosmic Council:
    - Challenges that seem impossible or blocked often have unseen solutions.
    - Strategy and planning should look for alternative routes, shortcuts,
      and workarounds.
    - Rigidity in thinking creates artificial barriers—sometimes the best
      way forward is outside conventional methods.

Examples:
    - A startup struggling with funding may find alternative financing through
      partnerships or decentralized networks instead of traditional VC.
    - Ancient civilizations "tunneled" around technological limitations through
      ingenious engineering solutions.

Cycle Position: 2️⃣ Finding hidden pathways through challenges.
    ← Receives from Quantum Entanglement (Red Owl)
    → Feeds into Quantum Superposition (Yellow Honeybee)

───────────────────────────────────────────────────────────────────────────────
SPIRIT ANIMAL ARCHETYPE - The Orangutan 🦧
───────────────────────────────────────────────────────────────────────────────

Totem: The Architect of Strategy
Natural Strength: Problem-Solving, Dexterity, Tactical Thinking

Why the Orangutan?
    - Orangutans are brilliant problem-solvers, using tools and logic to
      overcome obstacles.
    - They plan their actions strategically, ensuring efficiency and precision.
    - Their ability to navigate complex environments mirrors structured
      thinking in logistics and planning.

How the Orangutan Guides the Council:
    - Develops execution plans to turn knowledge into action.
    - Finds the smartest pathways through challenges (Quantum Tunneling).
    - Creates adaptable strategies, adjusting when necessary.

Example:
    A business leader orchestrating a complex project launch, ensuring
    efficiency and smooth execution.

Guiding Thought: "Every great vision is only as strong as the plan behind it."

═══════════════════════════════════════════════════════════════════════════════
ROLE & PURPOSE
═══════════════════════════════════════════════════════════════════════════════

Role: Logistics & Strategic Planning
Guiding Question: "How do we get from where we are to where we want to be?"

Function:
- Creates roadmaps and action plans
- Structures efficient workflows to eliminate waste
- Anticipates obstacles and finds alternative routes
- Transforms root cause insights into structured action
- Ensures outputs are actionable and tied to practical strategies

Core Principle: Create order through strategic planning.

═══════════════════════════════════════════════════════════════════════════════
THREE FALSIFIABLE CRITERIA
═══════════════════════════════════════════════════════════════════════════════

1. Dependency ordering - actions are topologically sorted
2. Rollback reversibility - each action has a defined rollback
3. Risk gates - high-risk actions require approval
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


class RiskLevel(Enum):
    """Risk level for an action."""
    NEGLIGIBLE = 1  # Can be auto-executed
    LOW = 2         # Can be auto-executed with logging
    MEDIUM = 3      # Requires confirmation
    HIGH = 4        # Requires approval
    CRITICAL = 5    # Requires multi-party approval

    @property
    def requires_approval(self) -> bool:
        """Does this risk level require human approval?"""
        return self.value >= 4

    @property
    def requires_confirmation(self) -> bool:
        """Does this risk level require confirmation?"""
        return self.value >= 3

    @property
    def can_auto_execute(self) -> bool:
        """Can this action be auto-executed?"""
        return self.value <= 2


class ActionStatus(Enum):
    """Status of an action in the plan."""
    PLANNED = auto()      # Not yet started
    READY = auto()        # Dependencies met, ready to execute
    BLOCKED = auto()      # Waiting on dependencies
    PENDING_APPROVAL = auto()  # Waiting for human approval
    APPROVED = auto()     # Approved, ready to execute
    EXECUTING = auto()    # Currently running
    COMPLETED = auto()    # Successfully completed
    FAILED = auto()       # Execution failed
    ROLLED_BACK = auto()  # Was rolled back
    SKIPPED = auto()      # Skipped due to conditions


class ActionCategory(Enum):
    """Category of action for routing and risk assessment."""
    CONFIGURATION = "configuration"  # Config changes
    DEPLOYMENT = "deployment"        # Deploy/rollback
    SCALING = "scaling"              # Scale up/down
    RESTART = "restart"              # Restart services
    DATABASE = "database"            # DB operations
    NETWORK = "network"              # Network changes
    SECURITY = "security"            # Security changes
    MONITORING = "monitoring"        # Monitoring/alerting
    COMMUNICATION = "communication"  # Notify stakeholders
    INVESTIGATION = "investigation"  # Gather more info
    CUSTOM = "custom"                # Custom action


@dataclass
class RollbackProcedure:
    """
    How to undo an action.

    Every action MUST have a rollback procedure (Criterion 2).
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    steps: List[str] = field(default_factory=list)
    estimated_duration_seconds: int = 60
    risk_level: RiskLevel = RiskLevel.LOW
    requires_data_backup: bool = False
    backup_location: Optional[str] = None
    automation_script: Optional[str] = None
    manual_steps: List[str] = field(default_factory=list)

    @property
    def is_automated(self) -> bool:
        """Can this rollback be automated?"""
        return self.automation_script is not None

    @property
    def is_reversible(self) -> bool:
        """Is this rollback actually reversible?"""
        return len(self.steps) > 0 or self.automation_script is not None


@dataclass
class Dependency:
    """
    Dependency between actions.

    Actions are topologically sorted by dependencies (Criterion 1).
    """
    from_action_id: str  # This action...
    to_action_id: str    # ...must complete before this one
    dependency_type: str = "requires"  # requires, recommends, conflicts
    reason: str = ""

    @property
    def is_hard_dependency(self) -> bool:
        """Is this a blocking dependency?"""
        return self.dependency_type in ("requires", "conflicts")


@dataclass
class ActionStep:
    """
    A single action step in the plan.

    Each action has:
    - Clear description of what to do
    - Risk assessment
    - Dependencies on other actions
    - Rollback procedure
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # What to do
    title: str = ""
    description: str = ""
    category: ActionCategory = ActionCategory.CUSTOM
    target_service: Optional[str] = None
    target_resource: Optional[str] = None

    # Parameters for execution
    parameters: Dict[str, Any] = field(default_factory=dict)

    # Risk assessment (Criterion 3)
    risk_level: RiskLevel = RiskLevel.LOW
    risk_factors: List[str] = field(default_factory=list)
    risk_mitigations: List[str] = field(default_factory=list)

    # Dependencies (Criterion 1)
    depends_on: List[str] = field(default_factory=list)  # Action IDs
    blocks: List[str] = field(default_factory=list)      # Action IDs this blocks

    # Rollback (Criterion 2)
    rollback: Optional[RollbackProcedure] = None

    # Execution
    status: ActionStatus = ActionStatus.PLANNED
    estimated_duration_seconds: int = 60
    actual_duration_seconds: Optional[int] = None

    # Approval tracking
    requires_approval: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None

    # Results
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Ensure rollback exists and approval is set correctly."""
        if self.rollback is None:
            self.rollback = RollbackProcedure(
                description=f"Rollback: {self.title}",
                steps=["Manual intervention required"],
            )
        self.requires_approval = self.risk_level.requires_approval

    @property
    def is_ready(self) -> bool:
        """Is this action ready to execute?"""
        if self.requires_approval and self.status != ActionStatus.APPROVED:
            return False
        return self.status in (ActionStatus.READY, ActionStatus.APPROVED)

    @property
    def is_complete(self) -> bool:
        """Has this action completed (success or failure)?"""
        return self.status in (
            ActionStatus.COMPLETED,
            ActionStatus.FAILED,
            ActionStatus.ROLLED_BACK,
            ActionStatus.SKIPPED,
        )

    @property
    def can_rollback(self) -> bool:
        """Can this action be rolled back?"""
        return (
            self.rollback is not None
            and self.rollback.is_reversible
            and self.status == ActionStatus.COMPLETED
        )


@dataclass
class ActionPlan:
    """
    A complete action plan to resolve a root cause.

    The plan is a DAG of actions with:
    - Topological ordering by dependencies
    - Risk assessment for the overall plan
    - Rollback strategy for the entire plan
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # What this plan addresses
    root_cause: str = ""
    root_cause_confidence: float = 0.0
    problem_id: Optional[str] = None

    # The plan
    title: str = ""
    description: str = ""
    actions: List[ActionStep] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)  # Topologically sorted action IDs

    # Dependencies (computed)
    dependencies: List[Dependency] = field(default_factory=list)

    # Overall risk
    overall_risk: RiskLevel = RiskLevel.LOW
    risk_summary: str = ""

    # Approval requirements
    requires_approval: bool = False
    approval_gates: List[str] = field(default_factory=list)  # Action IDs that need approval

    # Execution tracking
    status: ActionStatus = ActionStatus.PLANNED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Rollback strategy
    rollback_strategy: str = "sequential"  # sequential, parallel, selective
    rollback_order: List[str] = field(default_factory=list)  # Reverse of execution_order

    # Metrics
    estimated_total_duration_seconds: int = 0
    actual_total_duration_seconds: Optional[int] = None
    actions_completed: int = 0
    actions_failed: int = 0

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "orange_orangutan"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Compute derived fields."""
        self._compute_execution_order()
        self._compute_risk()
        self._compute_duration()

    def _compute_execution_order(self):
        """Topologically sort actions by dependencies."""
        if not self.actions:
            return

        # Build dependency graph
        action_map = {a.id: a for a in self.actions}
        in_degree = {a.id: 0 for a in self.actions}
        graph: Dict[str, List[str]] = {a.id: [] for a in self.actions}

        for action in self.actions:
            for dep_id in action.depends_on:
                if dep_id in action_map:
                    graph[dep_id].append(action.id)
                    in_degree[action.id] += 1

        # Kahn's algorithm for topological sort
        queue = [aid for aid, deg in in_degree.items() if deg == 0]
        result = []

        while queue:
            # Sort by risk (lower risk first) for deterministic ordering
            queue.sort(key=lambda x: action_map[x].risk_level.value)
            current = queue.pop(0)
            result.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self.actions):
            # Cycle detected - fall back to original order
            self.execution_order = [a.id for a in self.actions]
            self.metadata["cycle_detected"] = True
        else:
            self.execution_order = result
            self.rollback_order = list(reversed(result))

    def _compute_risk(self):
        """Compute overall risk from individual actions."""
        if not self.actions:
            return

        max_risk = max(a.risk_level.value for a in self.actions)
        self.overall_risk = RiskLevel(max_risk)

        # Count high-risk actions
        high_risk_count = sum(1 for a in self.actions if a.risk_level.value >= 4)
        medium_risk_count = sum(1 for a in self.actions if a.risk_level.value == 3)

        self.risk_summary = (
            f"{len(self.actions)} actions: "
            f"{high_risk_count} high-risk, {medium_risk_count} medium-risk"
        )

        self.requires_approval = any(a.requires_approval for a in self.actions)
        self.approval_gates = [a.id for a in self.actions if a.requires_approval]

    def _compute_duration(self):
        """Compute estimated total duration."""
        # Simple sum (could be smarter with parallel execution)
        self.estimated_total_duration_seconds = sum(
            a.estimated_duration_seconds for a in self.actions
        )

    def get_action(self, action_id: str) -> Optional[ActionStep]:
        """Get an action by ID."""
        for action in self.actions:
            if action.id == action_id:
                return action
        return None

    def get_ready_actions(self) -> List[ActionStep]:
        """Get actions that are ready to execute."""
        completed_ids = {a.id for a in self.actions if a.is_complete}
        ready = []

        for action in self.actions:
            if action.is_complete:
                continue
            if action.requires_approval and action.status != ActionStatus.APPROVED:
                continue
            # Check all dependencies are complete
            if all(dep_id in completed_ids for dep_id in action.depends_on):
                ready.append(action)

        return ready

    def get_blocked_actions(self) -> List[ActionStep]:
        """Get actions that are blocked on dependencies."""
        completed_ids = {a.id for a in self.actions if a.is_complete}
        blocked = []

        for action in self.actions:
            if action.is_complete:
                continue
            # Has incomplete dependencies
            if not all(dep_id in completed_ids for dep_id in action.depends_on):
                blocked.append(action)

        return blocked

    @property
    def progress(self) -> float:
        """Get plan progress as a percentage."""
        if not self.actions:
            return 0.0
        completed = sum(1 for a in self.actions if a.is_complete)
        return completed / len(self.actions)

    @property
    def is_complete(self) -> bool:
        """Is the entire plan complete?"""
        return all(a.is_complete for a in self.actions)


@dataclass
class OrangeOrangutanConfig:
    """Configuration for Orange Orangutan action planning."""

    # Risk thresholds
    auto_execute_max_risk: RiskLevel = RiskLevel.LOW
    require_approval_min_risk: RiskLevel = RiskLevel.HIGH

    # Planning parameters
    max_actions_per_plan: int = 20
    max_parallel_actions: int = 3

    # Timeouts
    default_action_timeout_seconds: int = 300
    max_action_timeout_seconds: int = 3600

    # Rollback
    auto_rollback_on_failure: bool = True
    rollback_timeout_seconds: int = 600

    # Approval
    approval_timeout_seconds: int = 86400  # 24 hours
    escalation_timeout_seconds: int = 3600  # 1 hour

    # Safety
    require_rollback_for_all_actions: bool = True
    dry_run_by_default: bool = False


# Benchmark types for testing
@dataclass
class OrangeOrangutanBenchmarkCase:
    """A benchmark case for testing action planning."""
    id: str
    root_cause: str
    expected_action_count: int
    expected_categories: List[ActionCategory]
    expected_max_risk: RiskLevel
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrangeOrangutanEvalResult:
    """Result of evaluating a benchmark case."""
    case_id: str
    success: bool
    plan: Optional[ActionPlan] = None
    action_count_match: bool = False
    categories_match: bool = False
    risk_appropriate: bool = False
    all_have_rollback: bool = False
    valid_ordering: bool = False
    error: Optional[str] = None
