"""
BLUE DOLPHIN (WHERE) - Location Models.

Blue Dolphin is the BLUE Enterprise in the ROYGBV hierarchy.
The Harmonious Communicator - Bridges gaps and ensures clear messaging.

═══════════════════════════════════════════════════════════════════════════════
COSMIC IDENTITY
═══════════════════════════════════════════════════════════════════════════════

Chakra: Vishuddha (Throat) - Communication, Connection, Expression
Gemstone: Sapphire - Communication, Truth, Connection, Wisdom, Insight
Quantum Principle: Wave-Particle Duality
Element: Water
Frequency: 852Hz
Color: Blue (#0000FF)

Core Energy: Communication, Connection, Expression

    The Throat Chakra governs authentic expression and clear communication.
    Blue Dolphin channels this energy by bridging gaps between systems,
    teams, and stakeholders. Connection is not mere transmission—it is the
    art of ensuring the message resonates with its intended audience.

    Energy Flow:
    - Communication: Translates complex information into clear messaging
    - Connection: Bridges diverse systems and stakeholders
    - Expression: Adapts the form of delivery to match the context

───────────────────────────────────────────────────────────────────────────────
WAVE-PARTICLE DUALITY - "How something is perceived depends on how it is observed."
───────────────────────────────────────────────────────────────────────────────

Quantum Meaning:
    Light and matter act both as particles (solid objects) and waves (fluid
    energy). Whether something is a wave or a particle depends on how you
    measure it.

Application to Cosmic Council:
    - Communication changes based on the audience. A message should shift
      depending on context and perception.
    - Marketing, storytelling, and leadership require flexibility—words,
      symbols, and ideas must be adaptable.
    - Reality is shaped by perception—leaders must understand both the
      "hard facts" and the "emotional wave" behind them.

Examples:
    - A scientific discovery needs different explanations for different
      audiences (technical for experts, simple for the public).
    - Public perception of technology shifts depending on how it's presented—
      a "surveillance system" vs. a "safety network."

Cycle Position: 5️⃣ Adapting messaging and perception.
    ← Receives from Quantum Teleportation (Green Turtle)
    → Feeds into Quantum Field Theory (Purple Elephant)

───────────────────────────────────────────────────────────────────────────────
SPIRIT ANIMAL ARCHETYPE - The Dolphin 🐬
───────────────────────────────────────────────────────────────────────────────

Totem: The Messenger & Storyteller
Natural Strength: Communication, Adaptability, Social Intelligence

Why the Dolphin?
    - Dolphins are masters of communication, using echolocation and social
      intelligence.
    - They translate complex signals into meaningful messages, mirroring
      effective communication strategies.
    - They balance logic with playfulness, ensuring that communication is
      both effective and engaging.

How the Dolphin Guides the Council:
    - Crafts persuasive messages that resonate deeply (Wave-Particle Duality).
    - Adapts communication styles based on audience perception.
    - Turns data into compelling stories, ensuring clarity and engagement.

Example:
    A public speaker transforming complex scientific research into
    accessible, inspiring talks.

Guiding Thought: "A message unshared is a message unheard—speak with clarity and purpose."

═══════════════════════════════════════════════════════════════════════════════
ROLE & PURPOSE
═══════════════════════════════════════════════════════════════════════════════

Role: Communication & Marketing
Guiding Question: "Where should our message be seen, and how will it best reach
                   our audience?"

Function:
- Crafts clear and compelling messaging
- Bridges gaps between teams, stakeholders, and the public
- Ensures alignment between internal goals and external perception
- Resolves execution locations for actions
- Validates connectivity to all targets

Core Principle: Communicate with clarity and bridge all divides.

═══════════════════════════════════════════════════════════════════════════════
THREE FALSIFIABLE CRITERIA
═══════════════════════════════════════════════════════════════════════════════

1. Location resolution - every action has a specific execution target
2. Environment matching - actions matched to appropriate environments
3. Connectivity validation - all targets are reachable
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


class EnvironmentType(Enum):
    """Type of execution environment."""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TESTING = "testing"
    SANDBOX = "sandbox"
    DR = "disaster_recovery"
    EDGE = "edge"


class LocationType(Enum):
    """Type of execution location."""
    KUBERNETES_CLUSTER = "kubernetes"
    VM = "virtual_machine"
    CONTAINER = "container"
    SERVERLESS = "serverless"
    BARE_METAL = "bare_metal"
    CLOUD_FUNCTION = "cloud_function"
    EDGE_NODE = "edge"
    LOCAL = "local"


class CloudProvider(Enum):
    """Cloud provider."""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ON_PREM = "on_prem"
    HYBRID = "hybrid"
    MULTI_CLOUD = "multi_cloud"


class ConnectivityStatus(Enum):
    """Connectivity status."""
    CONNECTED = auto()
    DISCONNECTED = auto()
    DEGRADED = auto()
    UNKNOWN = auto()


class TargetStatus(Enum):
    """Execution target status."""
    AVAILABLE = auto()
    BUSY = auto()
    MAINTENANCE = auto()
    UNAVAILABLE = auto()
    RESERVED = auto()


@dataclass
class NetworkEndpoint:
    """A network endpoint for connectivity."""
    address: str = ""
    port: int = 0
    protocol: str = "tcp"
    is_internal: bool = True
    requires_vpn: bool = False
    requires_mtls: bool = False


@dataclass
class Location:
    """
    A physical or logical location for execution.

    Criterion 1: Every action must have a resolved location.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    type: LocationType = LocationType.KUBERNETES_CLUSTER

    # Cloud/infrastructure details
    provider: CloudProvider = CloudProvider.ON_PREM
    region: str = ""
    zone: str = ""
    datacenter: str = ""

    # Kubernetes details (if applicable)
    cluster_name: str = ""
    namespace: str = "default"
    node_selector: Dict[str, str] = field(default_factory=dict)

    # Network
    endpoints: List[NetworkEndpoint] = field(default_factory=list)
    vpc_id: Optional[str] = None
    subnet_id: Optional[str] = None

    # Capacity
    cpu_available: float = 0.0
    memory_available_gb: float = 0.0
    storage_available_gb: float = 0.0

    # Status
    status: TargetStatus = TargetStatus.AVAILABLE
    connectivity: ConnectivityStatus = ConnectivityStatus.UNKNOWN
    last_health_check: Optional[datetime] = None

    # Metadata
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_available(self) -> bool:
        """Check if location is available for execution."""
        return (
            self.status == TargetStatus.AVAILABLE and
            self.connectivity in [ConnectivityStatus.CONNECTED, ConnectivityStatus.UNKNOWN]
        )


@dataclass
class Environment:
    """
    An execution environment.

    Criterion 2: Actions must be matched to appropriate environments.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    type: EnvironmentType = EnvironmentType.PRODUCTION

    # Locations in this environment
    locations: List[Location] = field(default_factory=list)
    primary_location_id: Optional[str] = None

    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    secrets_provider: str = ""  # e.g., "vault", "aws-secrets-manager"

    # Access control
    requires_approval: bool = False
    allowed_actions: List[str] = field(default_factory=list)
    blocked_actions: List[str] = field(default_factory=list)

    # Risk settings
    is_production: bool = False
    change_freeze: bool = False
    maintenance_window_only: bool = False

    # Metadata
    owner: str = ""
    team: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def primary_location(self) -> Optional[Location]:
        """Get the primary location."""
        if self.primary_location_id:
            for loc in self.locations:
                if loc.id == self.primary_location_id:
                    return loc
        return self.locations[0] if self.locations else None


@dataclass
class ExecutionTarget:
    """
    A specific target for action execution.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # References
    action_id: str = ""
    spec_id: str = ""
    slot_id: str = ""

    # Target details
    location: Optional[Location] = None
    environment: Optional[Environment] = None

    # Execution context
    namespace: str = "default"
    service_account: str = ""
    run_as_user: Optional[str] = None

    # Resource requirements
    cpu_request: float = 0.1
    cpu_limit: float = 1.0
    memory_request_mb: int = 128
    memory_limit_mb: int = 512

    # Networking
    endpoints: List[NetworkEndpoint] = field(default_factory=list)
    ingress_required: bool = False
    egress_allowed: bool = True

    # Status
    is_resolved: bool = False
    is_reachable: bool = False
    resolution_error: Optional[str] = None

    # Fallback
    fallback_location_id: Optional[str] = None
    retry_on_different_location: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoutingRule:
    """
    A rule for routing actions to locations.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""

    # Matching criteria
    action_patterns: List[str] = field(default_factory=list)  # Glob patterns
    spec_types: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    risk_levels: List[str] = field(default_factory=list)

    # Target
    target_environment: Optional[str] = None
    target_location: Optional[str] = None
    target_region: Optional[str] = None

    # Priority and conditions
    priority: int = 100
    enabled: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LocationPlan:
    """
    Complete location plan for scheduled actions.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # Source references
    schedule_id: str = ""
    implementation_plan_id: str = ""

    # Targets
    targets: List[ExecutionTarget] = field(default_factory=list)
    routing_rules_applied: List[str] = field(default_factory=list)

    # Environments used
    environments: List[Environment] = field(default_factory=list)
    locations: List[Location] = field(default_factory=list)

    # Metrics
    targets_resolved: int = 0
    targets_unresolved: int = 0
    targets_reachable: int = 0
    targets_unreachable: int = 0

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
        if not self.targets:
            return

        self.targets_resolved = sum(1 for t in self.targets if t.is_resolved)
        self.targets_unresolved = len(self.targets) - self.targets_resolved
        self.targets_reachable = sum(1 for t in self.targets if t.is_reachable)
        self.targets_unreachable = sum(
            1 for t in self.targets if t.is_resolved and not t.is_reachable
        )

    def get_target(self, target_id: str) -> Optional[ExecutionTarget]:
        """Get a target by ID."""
        for target in self.targets:
            if target.id == target_id:
                return target
        return None

    def get_target_for_action(self, action_id: str) -> Optional[ExecutionTarget]:
        """Get target for an action."""
        for target in self.targets:
            if target.action_id == action_id:
                return target
        return None


@dataclass
class BlueDolphinConfig:
    """Configuration for Blue Dolphin location resolution."""

    # Environment selection
    default_environment: EnvironmentType = EnvironmentType.PRODUCTION
    allow_cross_environment: bool = False
    prefer_same_region: bool = True

    # Connectivity
    require_connectivity_check: bool = True
    connectivity_timeout_seconds: int = 10
    retry_unreachable: bool = True

    # Routing
    apply_routing_rules: bool = True
    fallback_enabled: bool = True

    # Safety
    block_production_for_risky: bool = True
    require_staging_first: bool = False


# Pre-defined environments
STANDARD_ENVIRONMENTS: Dict[str, Environment] = {
    "production": Environment(
        name="Production",
        type=EnvironmentType.PRODUCTION,
        is_production=True,
        requires_approval=True,
        maintenance_window_only=True,
    ),
    "staging": Environment(
        name="Staging",
        type=EnvironmentType.STAGING,
        is_production=False,
        requires_approval=False,
    ),
    "development": Environment(
        name="Development",
        type=EnvironmentType.DEVELOPMENT,
        is_production=False,
        requires_approval=False,
    ),
}

# Pre-defined locations
STANDARD_LOCATIONS: Dict[str, Location] = {
    "prod-us-east": Location(
        name="Production US East",
        type=LocationType.KUBERNETES_CLUSTER,
        provider=CloudProvider.AWS,
        region="us-east-1",
        cluster_name="prod-cluster-east",
        namespace="production",
        status=TargetStatus.AVAILABLE,
        connectivity=ConnectivityStatus.CONNECTED,
    ),
    "prod-us-west": Location(
        name="Production US West",
        type=LocationType.KUBERNETES_CLUSTER,
        provider=CloudProvider.AWS,
        region="us-west-2",
        cluster_name="prod-cluster-west",
        namespace="production",
        status=TargetStatus.AVAILABLE,
        connectivity=ConnectivityStatus.CONNECTED,
    ),
    "staging-us-east": Location(
        name="Staging US East",
        type=LocationType.KUBERNETES_CLUSTER,
        provider=CloudProvider.AWS,
        region="us-east-1",
        cluster_name="staging-cluster",
        namespace="staging",
        status=TargetStatus.AVAILABLE,
        connectivity=ConnectivityStatus.CONNECTED,
    ),
    "dev-local": Location(
        name="Development Local",
        type=LocationType.LOCAL,
        provider=CloudProvider.ON_PREM,
        status=TargetStatus.AVAILABLE,
        connectivity=ConnectivityStatus.CONNECTED,
    ),
}
