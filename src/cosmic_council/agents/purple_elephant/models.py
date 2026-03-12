"""
PURPLE ELEPHANT (WHO) - Responsibility Models.

Purple Elephant is the PURPLE/VIOLET Enterprise in the ROYGBV hierarchy.
The Wise Guardian - Supports, remembers, and continuously improves.

═══════════════════════════════════════════════════════════════════════════════
COSMIC IDENTITY
═══════════════════════════════════════════════════════════════════════════════

Chakra: Ajna (Third Eye) - Intuition, Memory, Continuous Learning
Gemstone: Amethyst - Spiritual Wisdom, Memory, Learning, Protection, Awareness
Quantum Principle: Quantum Field Theory
Element: Spirit/Ether
Frequency: 963Hz
Color: Purple/Violet (#8B00FF)

Core Energy: Intuition, Memory, Continuous Learning

    The Third Eye Chakra governs higher perception and accumulated wisdom.
    Purple Elephant embodies this energy through deep memory and ethical
    reflection. Continuous learning is not passive absorption—it is the
    active integration of experience into ever-deepening understanding.

    Energy Flow:
    - Intuition: Perceives patterns and consequences beyond surface data
    - Memory: Preserves institutional knowledge across cycles
    - Continuous Learning: Evolves understanding through reflection on outcomes

───────────────────────────────────────────────────────────────────────────────
QUANTUM FIELD THEORY - "Everything exists within a vast, interconnected field."
───────────────────────────────────────────────────────────────────────────────

Quantum Meaning:
    In physics, empty space is not truly empty—it is filled with fluctuating
    quantum fields that shape everything. Every particle and force emerges
    from the quantum field, meaning all things are interconnected and
    influence each other.

Application to Cosmic Council:
    - All decisions, technologies, and innovations exist within a larger
      ethical and societal field.
    - No action is isolated—every choice creates ripple effects in the world.
    - Long-term reflection and wisdom are crucial to prevent harmful
      unintended consequences.

Examples:
    - An AI system trained on biased data can reinforce inequality, even if
      designed with good intentions.
    - Economic and environmental policies must be seen as part of an
      interconnected system—a win for one sector can harm another.

Cycle Position: 6️⃣ Ensuring long-term wisdom and ethical alignment.
    ← Receives from Wave-Particle Duality (Blue Dolphin)
    → Feeds back into Quantum Entanglement (Red Owl) ♾️

───────────────────────────────────────────────────────────────────────────────
SPIRIT ANIMAL ARCHETYPE - The Elephant 🐘
───────────────────────────────────────────────────────────────────────────────

Totem: The Sage & Ethical Guardian
Natural Strength: Deep Memory, Compassion, Ethical Judgment

Why the Elephant?
    - Elephants remember everything, carrying the wisdom of generations.
    - They act with empathy and fairness, ensuring moral and ethical
      responsibility.
    - They balance strength with gentleness, ensuring power is used
      responsibly.

How the Elephant Guides the Council:
    - Reflects on long-term consequences, preventing short-sighted mistakes
      (Quantum Field Theory).
    - Ensures actions align with ethical values and emotional intelligence.
    - Preserves knowledge and wisdom for future generations.

Example:
    An AI ethics researcher ensuring machine learning models remain fair,
    unbiased, and human-centered.

Guiding Thought: "Wisdom is not just knowing—it is understanding and applying knowledge ethically."

═══════════════════════════════════════════════════════════════════════════════
ROLE & PURPOSE
═══════════════════════════════════════════════════════════════════════════════

Role: Support & Continuous Improvement
Guiding Question: "Who needs support, and how can we continuously improve our
                   service?"

Function:
- Provides ongoing support and troubleshooting
- Maintains institutional memory and best practices
- Focuses on iterative improvement based on feedback
- Assigns responsibilities to appropriate executors
- Identifies all relevant stakeholders for each action
- Routes notifications to all parties

Core Principle: Guard wisdom and nurture continuous growth.

═══════════════════════════════════════════════════════════════════════════════
THREE FALSIFIABLE CRITERIA
═══════════════════════════════════════════════════════════════════════════════

1. Responsibility assignment - every action has a designated executor
2. Stakeholder identification - all relevant stakeholders identified
3. Notification routing - all parties properly notified
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


class ResponsibilityType(Enum):
    """Type of responsibility."""
    EXECUTOR = "executor"           # Performs the action
    APPROVER = "approver"           # Approves the action
    REVIEWER = "reviewer"           # Reviews results
    OBSERVER = "observer"           # Notified but no action required
    ESCALATION = "escalation"       # Escalation contact
    OWNER = "owner"                 # Service/resource owner


class StakeholderType(Enum):
    """Type of stakeholder."""
    INDIVIDUAL = "individual"
    TEAM = "team"
    SERVICE_ACCOUNT = "service_account"
    AUTOMATION = "automation"
    ON_CALL = "on_call"
    DISTRIBUTION_LIST = "distribution_list"


class NotificationChannel(Enum):
    """Notification delivery channel."""
    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"
    SMS = "sms"
    IN_APP = "in_app"
    NONE = "none"


class NotificationPriority(Enum):
    """Notification priority level."""
    CRITICAL = "critical"   # Immediate, all channels
    HIGH = "high"           # Within minutes
    MEDIUM = "medium"       # Within hours
    LOW = "low"             # Best effort
    INFO = "info"           # FYI only


class AssignmentStatus(Enum):
    """Status of a responsibility assignment."""
    PENDING = auto()
    ASSIGNED = auto()
    ACKNOWLEDGED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    ESCALATED = auto()
    REASSIGNED = auto()


@dataclass
class ContactInfo:
    """Contact information for a stakeholder."""
    email: str = ""
    slack_id: str = ""
    slack_channel: str = ""
    phone: str = ""
    pagerduty_id: str = ""
    webhook_url: str = ""
    preferred_channel: NotificationChannel = NotificationChannel.EMAIL


@dataclass
class Stakeholder:
    """
    A person, team, or system that has stake in an action.

    Criterion 2: All relevant stakeholders are identified.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    type: StakeholderType = StakeholderType.INDIVIDUAL

    # Contact
    contact: ContactInfo = field(default_factory=ContactInfo)

    # Organizational
    team: str = ""
    department: str = ""
    role: str = ""
    timezone: str = "UTC"

    # Availability
    is_available: bool = True
    on_call: bool = False
    vacation_until: Optional[datetime] = None

    # Capabilities
    capabilities: Set[str] = field(default_factory=set)
    services_owned: List[str] = field(default_factory=list)
    escalation_level: int = 0  # 0 = primary, 1 = first escalation, etc.

    # Preferences
    notification_preferences: Dict[str, NotificationChannel] = field(default_factory=dict)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponsibilityAssignment:
    """
    Assignment of responsibility to a stakeholder.

    Criterion 1: Every action has a designated executor.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # References
    action_id: str = ""
    target_id: str = ""  # From Blue Dolphin
    slot_id: str = ""    # From Green Turtle

    # Assignment
    stakeholder: Optional[Stakeholder] = None
    responsibility_type: ResponsibilityType = ResponsibilityType.EXECUTOR
    status: AssignmentStatus = AssignmentStatus.PENDING

    # Timing
    assigned_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    due_by: Optional[datetime] = None

    # Escalation
    escalation_chain: List[str] = field(default_factory=list)  # Stakeholder IDs
    escalation_timeout_minutes: int = 30
    current_escalation_level: int = 0

    # Notification tracking
    notifications_sent: List[str] = field(default_factory=list)
    last_notification_at: Optional[datetime] = None

    # Metadata
    reason: str = ""
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_assigned(self) -> bool:
        """Check if responsibility is assigned."""
        return self.stakeholder is not None and self.status != AssignmentStatus.PENDING


@dataclass
class NotificationRecord:
    """
    Record of a notification sent.

    Criterion 3: All parties are properly notified.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # References
    assignment_id: str = ""
    stakeholder_id: str = ""
    action_id: str = ""

    # Notification details
    channel: NotificationChannel = NotificationChannel.EMAIL
    priority: NotificationPriority = NotificationPriority.MEDIUM
    subject: str = ""
    message: str = ""

    # Delivery
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None

    # Status
    is_sent: bool = False
    is_delivered: bool = False
    is_read: bool = False
    delivery_error: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EscalationRule:
    """Rule for escalating unacknowledged assignments."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""

    # Trigger conditions
    timeout_minutes: int = 30
    unacknowledged_only: bool = True
    risk_levels: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)

    # Escalation target
    escalation_stakeholder_id: Optional[str] = None
    escalation_team: Optional[str] = None
    notification_priority: NotificationPriority = NotificationPriority.HIGH

    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponsibilityPlan:
    """
    Complete responsibility plan for located actions.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # Source references
    location_plan_id: str = ""
    schedule_id: str = ""

    # Assignments
    assignments: List[ResponsibilityAssignment] = field(default_factory=list)
    stakeholders: List[Stakeholder] = field(default_factory=list)

    # Notifications
    notifications: List[NotificationRecord] = field(default_factory=list)
    escalation_rules: List[EscalationRule] = field(default_factory=list)

    # Metrics
    assignments_made: int = 0
    assignments_pending: int = 0
    stakeholders_identified: int = 0
    notifications_sent: int = 0

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
        """Compute plan metrics."""
        if not self.assignments:
            return

        self.assignments_made = sum(1 for a in self.assignments if a.is_assigned)
        self.assignments_pending = len(self.assignments) - self.assignments_made
        self.stakeholders_identified = len(set(
            a.stakeholder.id for a in self.assignments if a.stakeholder
        ))
        self.notifications_sent = sum(1 for n in self.notifications if n.is_sent)

    def get_assignment(self, assignment_id: str) -> Optional[ResponsibilityAssignment]:
        """Get an assignment by ID."""
        for assignment in self.assignments:
            if assignment.id == assignment_id:
                return assignment
        return None

    def get_assignments_for_action(self, action_id: str) -> List[ResponsibilityAssignment]:
        """Get all assignments for an action."""
        return [a for a in self.assignments if a.action_id == action_id]

    def get_stakeholder(self, stakeholder_id: str) -> Optional[Stakeholder]:
        """Get a stakeholder by ID."""
        for stakeholder in self.stakeholders:
            if stakeholder.id == stakeholder_id:
                return stakeholder
        return None


@dataclass
class PurpleElephantConfig:
    """Configuration for Purple Elephant responsibility assignment."""

    # Assignment settings
    require_executor: bool = True
    require_approver_for_high_risk: bool = True
    auto_assign_service_owners: bool = True

    # Notification settings
    send_notifications: bool = True
    default_notification_channel: NotificationChannel = NotificationChannel.SLACK
    notification_timeout_minutes: int = 30

    # Escalation settings
    enable_escalation: bool = True
    default_escalation_timeout_minutes: int = 30
    max_escalation_levels: int = 3

    # Fallback settings
    fallback_to_on_call: bool = True
    fallback_to_team: bool = True


# Pre-defined stakeholders (examples)
STANDARD_STAKEHOLDERS: Dict[str, Stakeholder] = {
    "platform-team": Stakeholder(
        name="Platform Team",
        type=StakeholderType.TEAM,
        team="platform",
        contact=ContactInfo(
            email="platform@example.com",
            slack_channel="#platform-ops",
            preferred_channel=NotificationChannel.SLACK,
        ),
        capabilities={"kubernetes", "deployment", "scaling", "monitoring"},
        services_owned=["api-gateway", "service-mesh"],
    ),
    "database-team": Stakeholder(
        name="Database Team",
        type=StakeholderType.TEAM,
        team="database",
        contact=ContactInfo(
            email="dba@example.com",
            slack_channel="#database-ops",
            preferred_channel=NotificationChannel.SLACK,
        ),
        capabilities={"database", "backup", "migration", "replication"},
        services_owned=["primary-db", "read-replicas"],
    ),
    "on-call-primary": Stakeholder(
        name="Primary On-Call",
        type=StakeholderType.ON_CALL,
        on_call=True,
        contact=ContactInfo(
            pagerduty_id="on-call-primary",
            preferred_channel=NotificationChannel.PAGERDUTY,
        ),
        escalation_level=0,
    ),
    "on-call-secondary": Stakeholder(
        name="Secondary On-Call",
        type=StakeholderType.ON_CALL,
        on_call=True,
        contact=ContactInfo(
            pagerduty_id="on-call-secondary",
            preferred_channel=NotificationChannel.PAGERDUTY,
        ),
        escalation_level=1,
    ),
    "automation-service": Stakeholder(
        name="Automation Service",
        type=StakeholderType.AUTOMATION,
        contact=ContactInfo(
            webhook_url="http://automation.internal/webhook",
            preferred_channel=NotificationChannel.WEBHOOK,
        ),
        capabilities={"notification", "restart", "scaling"},
        is_available=True,
    ),
}


# Default escalation rules
DEFAULT_ESCALATION_RULES: List[EscalationRule] = [
    EscalationRule(
        name="high_risk_escalation",
        description="Escalate high-risk actions quickly",
        timeout_minutes=15,
        risk_levels=["HIGH", "CRITICAL"],
        notification_priority=NotificationPriority.CRITICAL,
    ),
    EscalationRule(
        name="standard_escalation",
        description="Standard escalation for unacknowledged actions",
        timeout_minutes=30,
        notification_priority=NotificationPriority.HIGH,
    ),
]
