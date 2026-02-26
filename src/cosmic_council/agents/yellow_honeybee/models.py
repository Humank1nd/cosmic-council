"""
YELLOW HONEYBEE (WHAT) - Implementation Specification Models.

Yellow Honeybee is the YELLOW Enterprise in the ROYGBV hierarchy.
The Creator & Experimenter - Transforms plans into tangible solutions.

═══════════════════════════════════════════════════════════════════════════════
COSMIC IDENTITY
═══════════════════════════════════════════════════════════════════════════════

Chakra: Manipura (Solar Plexus) - Power, Manifestation, Creative Drive
Gemstone: Citrine - Creativity, Vision, Transformation, Abundance
Quantum Principle: Quantum Superposition
Element: Fire
Frequency: 639Hz
Color: Yellow (#FFFF00)

Core Energy: Power, Manifestation, Creative Drive

    The Solar Plexus Chakra is the seat of personal power and manifestation.
    Yellow Honeybee embodies this energy through relentless creation and
    experimentation. Creative drive is not aimless activity—it is the focused
    power to bring ideas into tangible reality.

    Energy Flow:
    - Power: Commands the energy to transform thought into action
    - Manifestation: Brings abstract possibilities into concrete specifications
    - Creative Drive: Sustains the momentum of continuous innovation

───────────────────────────────────────────────────────────────────────────────
QUANTUM SUPERPOSITION - "Something can exist in multiple states until a choice is made."
───────────────────────────────────────────────────────────────────────────────

Quantum Meaning:
    A quantum system can exist in multiple states at the same time—until
    observed, when it "collapses" into one reality. In Schrödinger's famous
    thought experiment, a cat in a box is both alive and dead simultaneously—
    until someone looks inside.

Application to Cosmic Council:
    - Creativity flourishes when multiple possibilities are explored at once.
    - Innovation requires considering multiple ideas before selecting the best.
    - Rigid, binary thinking limits creativity—quantum superposition encourages
      embracing uncertainty and holding multiple truths at once.

Examples:
    - An entrepreneur brainstorming multiple product ideas before committing to one.
    - Scientists running simulations of multiple possible futures before
      determining the optimal path.

Cycle Position: 3️⃣ Exploring all possible ideas before choosing one.
    ← Receives from Quantum Tunneling (Orange Orangutan)
    → Feeds into Quantum Teleportation (Green Turtle)

───────────────────────────────────────────────────────────────────────────────
SPIRIT ANIMAL ARCHETYPE - The Honeybee 🐝
───────────────────────────────────────────────────────────────────────────────

Totem: The Creator & Experimenter
Natural Strength: Industriousness, Collaboration, Rapid Experimentation

Why the Honeybee?
    - Honeybees create, adapt, and refine—always innovating within their
      environments.
    - They work in collective intelligence, mirroring how creative solutions
      emerge from collaboration.
    - Their hive structure represents interconnected problem-solving and
      agile experimentation.

How the Honeybee Guides the Council:
    - Explores multiple possibilities before choosing a direction (Quantum Superposition).
    - Builds and refines creative solutions through rapid iteration.
    - Embraces both structure and spontaneity—balancing logic with bold innovation.

Example:
    A scientist experimenting with new AI models, rapidly testing and
    iterating to find the most effective solution.

Guiding Thought: "Everything that exists was once just an idea—make yours a reality."

═══════════════════════════════════════════════════════════════════════════════
ROLE & PURPOSE
═══════════════════════════════════════════════════════════════════════════════

Role: Development & Innovation
Guiding Question: "What new solutions or innovations can we bring into reality?"

Function:
- Develops prototypes and experimental models
- Iterates rapidly, testing multiple possibilities before committing
- Encourages risk-taking and bold, innovative solutions
- Generates multiple solutions for each problem
- Blends creativity with functionality for real-world applicability

Core Principle: Manifest creativity through divine inspiration.

═══════════════════════════════════════════════════════════════════════════════
THREE FALSIFIABLE CRITERIA
═══════════════════════════════════════════════════════════════════════════════

1. Specification completeness - every action gets detailed specs
2. Validation rules - pre/post conditions for each step
3. Resource identification - specific resources/endpoints/configs identified
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


class SpecificationType(Enum):
    """Type of specification."""
    COMMAND = "command"           # Shell/CLI command
    API_CALL = "api_call"         # REST/GraphQL API call
    CONFIG_CHANGE = "config"      # Configuration modification
    DATABASE_QUERY = "database"   # Database operation
    SCRIPT = "script"             # Script execution
    MANUAL = "manual"             # Manual human action
    KUBERNETES = "kubernetes"     # K8s resource change
    TERRAFORM = "terraform"       # Infrastructure as code
    ANSIBLE = "ansible"           # Ansible playbook
    CUSTOM = "custom"             # Custom implementation


class ResourceType(Enum):
    """Type of resource involved."""
    SERVICE = "service"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    STORAGE = "storage"
    NETWORK = "network"
    CONFIG = "config"
    SECRET = "secret"
    ENDPOINT = "endpoint"
    CONTAINER = "container"
    POD = "pod"
    DEPLOYMENT = "deployment"
    CUSTOM = "custom"


class ValidationStatus(Enum):
    """Status of a validation check."""
    PENDING = auto()
    PASSED = auto()
    FAILED = auto()
    SKIPPED = auto()
    WARNING = auto()


@dataclass
class Resource:
    """
    A specific resource involved in an implementation.

    Criterion 3: Every resource must be specifically identified.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    type: ResourceType = ResourceType.CUSTOM
    identifier: str = ""  # e.g., "prod-db-01", "api.example.com/v1"
    namespace: Optional[str] = None  # K8s namespace, AWS region, etc.

    # Access details
    endpoint: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None

    # Authentication
    requires_auth: bool = False
    auth_method: Optional[str] = None  # "token", "mtls", "basic", etc.
    credential_ref: Optional[str] = None  # Reference to secret

    # State
    current_state: Optional[Dict[str, Any]] = None
    desired_state: Optional[Dict[str, Any]] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationRule:
    """
    A validation rule for pre/post conditions.

    Criterion 2: Every step has validation rules.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""

    # What to check
    check_type: str = "assertion"  # assertion, query, command, api_call
    check_expression: str = ""     # The actual check

    # Expected result
    expected_value: Optional[Any] = None
    comparison: str = "equals"  # equals, contains, matches, greater_than, etc.

    # Timing
    timeout_seconds: int = 30
    retry_count: int = 3
    retry_delay_seconds: int = 5

    # Result
    status: ValidationStatus = ValidationStatus.PENDING
    actual_value: Optional[Any] = None
    error_message: Optional[str] = None

    # Severity
    is_blocking: bool = True  # Fail the step if this fails

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PreCondition(ValidationRule):
    """Pre-condition that must be true before execution."""
    pass


@dataclass
class PostCondition(ValidationRule):
    """Post-condition that must be true after execution."""
    pass


@dataclass
class CommandSpec:
    """Specification for a command-based implementation."""
    command: str = ""
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    working_dir: Optional[str] = None
    shell: str = "bash"
    timeout_seconds: int = 300
    capture_output: bool = True
    expected_exit_code: int = 0


@dataclass
class ApiCallSpec:
    """Specification for an API call implementation."""
    method: str = "GET"
    url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    timeout_seconds: int = 30
    expected_status_codes: List[int] = field(default_factory=lambda: [200])
    retry_count: int = 3
    auth_header: Optional[str] = None


@dataclass
class ConfigChangeSpec:
    """Specification for a configuration change."""
    config_path: str = ""
    config_format: str = "yaml"  # yaml, json, toml, ini, env
    changes: Dict[str, Any] = field(default_factory=dict)
    backup_before: bool = True
    validate_after: bool = True
    reload_command: Optional[str] = None


@dataclass
class DatabaseQuerySpec:
    """Specification for a database operation."""
    connection_string_ref: str = ""  # Reference to secret
    query: str = ""
    query_type: str = "select"  # select, update, insert, delete, ddl
    parameters: Dict[str, Any] = field(default_factory=dict)
    transaction: bool = True
    timeout_seconds: int = 60
    expected_affected_rows: Optional[int] = None


@dataclass
class KubernetesSpec:
    """Specification for a Kubernetes operation."""
    action: str = "apply"  # apply, delete, patch, rollout
    resource_type: str = ""  # deployment, service, configmap, etc.
    resource_name: str = ""
    namespace: str = "default"
    manifest: Optional[Dict[str, Any]] = None
    patch: Optional[Dict[str, Any]] = None
    wait_for_ready: bool = True
    timeout_seconds: int = 300


@dataclass
class TaskSpecification:
    """
    Complete specification for implementing an action.

    Criterion 1: Every action gets a detailed specification.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # Reference to source action
    action_id: str = ""
    action_title: str = ""

    # Specification type
    spec_type: SpecificationType = SpecificationType.CUSTOM

    # The actual specification (one of these will be populated)
    command_spec: Optional[CommandSpec] = None
    api_spec: Optional[ApiCallSpec] = None
    config_spec: Optional[ConfigChangeSpec] = None
    database_spec: Optional[DatabaseQuerySpec] = None
    kubernetes_spec: Optional[KubernetesSpec] = None
    custom_spec: Optional[Dict[str, Any]] = None

    # Resources involved (Criterion 3)
    resources: List[Resource] = field(default_factory=list)

    # Validation (Criterion 2)
    pre_conditions: List[PreCondition] = field(default_factory=list)
    post_conditions: List[PostCondition] = field(default_factory=list)

    # Human-readable
    description: str = ""
    steps: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Execution details
    estimated_duration_seconds: int = 60
    idempotent: bool = False
    dry_run_supported: bool = False

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_complete(self) -> bool:
        """Is this specification complete enough to execute?"""
        has_spec = any([
            self.command_spec,
            self.api_spec,
            self.config_spec,
            self.database_spec,
            self.kubernetes_spec,
            self.custom_spec,
        ])
        has_resources = len(self.resources) > 0 or self.spec_type == SpecificationType.MANUAL
        return has_spec and has_resources

    @property
    def has_validation(self) -> bool:
        """Does this spec have validation rules?"""
        return len(self.pre_conditions) > 0 or len(self.post_conditions) > 0


@dataclass
class ImplementationPlan:
    """
    Complete implementation plan for all actions.

    Contains detailed specifications for every action in the plan.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # Source plan reference
    action_plan_id: str = ""
    root_cause: str = ""

    # Specifications
    specifications: List[TaskSpecification] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)  # Spec IDs

    # Resources summary
    all_resources: List[Resource] = field(default_factory=list)
    resource_dependencies: Dict[str, List[str]] = field(default_factory=dict)

    # Validation summary
    total_pre_conditions: int = 0
    total_post_conditions: int = 0

    # Completeness (Criterion 1)
    specs_complete: int = 0
    specs_incomplete: int = 0
    completeness_ratio: float = 0.0

    # Timing
    estimated_total_duration_seconds: int = 0

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Compute derived fields."""
        self._compute_metrics()

    def _compute_metrics(self):
        """Compute metrics about the plan."""
        if not self.specifications:
            return

        self.specs_complete = sum(1 for s in self.specifications if s.is_complete)
        self.specs_incomplete = len(self.specifications) - self.specs_complete
        self.completeness_ratio = self.specs_complete / len(self.specifications)

        self.total_pre_conditions = sum(
            len(s.pre_conditions) for s in self.specifications
        )
        self.total_post_conditions = sum(
            len(s.post_conditions) for s in self.specifications
        )

        self.estimated_total_duration_seconds = sum(
            s.estimated_duration_seconds for s in self.specifications
        )

        # Collect all resources
        seen_resources: Set[str] = set()
        for spec in self.specifications:
            for resource in spec.resources:
                if resource.id not in seen_resources:
                    self.all_resources.append(resource)
                    seen_resources.add(resource.id)

    def get_specification(self, spec_id: str) -> Optional[TaskSpecification]:
        """Get a specification by ID."""
        for spec in self.specifications:
            if spec.id == spec_id:
                return spec
        return None


@dataclass
class YellowHoneybeeConfig:
    """Configuration for Yellow Honeybee implementation planning."""

    # Specification generation
    require_complete_specs: bool = True
    require_validation_rules: bool = True
    require_resource_identification: bool = True

    # Validation
    min_pre_conditions_per_action: int = 1
    min_post_conditions_per_action: int = 1

    # Resource discovery
    auto_discover_resources: bool = True
    resource_discovery_timeout_seconds: int = 30

    # Execution
    default_timeout_seconds: int = 300
    enable_dry_run: bool = True
