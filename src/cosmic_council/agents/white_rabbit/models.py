"""
WHITE RABBIT - Input & Initiation Models.

Core data structures for the entry point to the Cosmic Council.
White Rabbit receives the input prompt and initiates the inquiry cycle.

"Follow the White Rabbit" - The beginning of every journey.

Three Falsifiable Criteria:
1. Input reception - all prompts are properly received and parsed
2. Intent classification - the intent/type of inquiry is correctly identified
3. Cycle initiation - Red Owl is properly invoked with structured input

Chakra: Bindu (The Point) - Origin, Potential, The Source
Gemstone: Clear Quartz - Clarity, Amplification, Programming
Quantum Concept: Quantum Vacuum - The source from which all possibilities emerge
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


class InputType(Enum):
    """Type of input received."""
    TEXT = "text"
    STRUCTURED = "structured"
    EVENT = "event"
    FEEDBACK = "feedback"  # From Black Snake
    COMMAND = "command"
    QUERY = "query"


class IntentCategory(Enum):
    """High-level intent categories."""
    INQUIRY = "inquiry"          # Asking questions, seeking understanding
    ACTION = "action"            # Requesting something be done
    ANALYSIS = "analysis"        # Requesting analysis of data/situation
    CREATION = "creation"        # Requesting something be created
    OPTIMIZATION = "optimization"  # Requesting improvement
    RESOLUTION = "resolution"    # Requesting problem resolution
    MONITORING = "monitoring"    # Requesting observation/tracking
    FEEDBACK = "feedback"        # Providing feedback from previous cycle


class UrgencyLevel(Enum):
    """Urgency of the input."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    IMMEDIATE = "immediate"


class InputStatus(Enum):
    """Status of input processing."""
    RECEIVED = "received"
    VALIDATED = "validated"
    CLASSIFIED = "classified"
    INITIATED = "initiated"
    REJECTED = "rejected"
    QUEUED = "queued"


@dataclass
class InputPrompt:
    """
    The raw input that initiates a cycle.

    Criterion 1: All prompts are properly received and parsed.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # The input content
    content: str = ""
    input_type: InputType = InputType.TEXT

    # Source information
    source_id: str = ""
    source_type: str = ""  # user, system, black_snake, external
    channel: str = ""      # api, cli, webhook, internal

    # Context
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    parent_cycle_id: Optional[str] = None  # If from Black Snake feedback

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)

    # Timing
    received_at: datetime = field(default_factory=datetime.utcnow)

    # Status
    status: InputStatus = InputStatus.RECEIVED
    validation_errors: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Check if input is valid."""
        return len(self.validation_errors) == 0 and bool(self.content.strip())

    @property
    def is_feedback_loop(self) -> bool:
        """Check if this is feedback from a previous cycle."""
        return self.parent_cycle_id is not None or self.source_type == "black_snake"


@dataclass
class Intent:
    """
    Classified intent of the input.

    Criterion 2: The intent/type of inquiry is correctly identified.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # Reference
    prompt_id: str = ""

    # Classification
    category: IntentCategory = IntentCategory.INQUIRY
    subcategory: str = ""
    confidence: float = 0.0  # 0-1

    # Extracted information
    subject: str = ""           # What the input is about
    action_requested: str = ""  # What action is being requested
    entities: List[str] = field(default_factory=list)  # Extracted entities
    keywords: List[str] = field(default_factory=list)  # Key terms

    # Context indicators
    urgency: UrgencyLevel = UrgencyLevel.NORMAL
    complexity: str = "medium"  # simple, medium, complex
    domain: str = ""           # Detected domain/area

    # For Red Owl
    initial_questions: List[str] = field(default_factory=list)
    suggested_hypotheses: List[str] = field(default_factory=list)

    # Timing
    classified_at: datetime = field(default_factory=datetime.utcnow)

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CycleInitiation:
    """
    Initiation of a new cosmic cycle.

    Criterion 3: Red Owl is properly invoked with structured input.
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # References
    prompt_id: str = ""
    intent_id: str = ""

    # Cycle information
    cycle_id: str = field(default_factory=lambda: str(uuid4()))
    cycle_number: int = 1

    # For Red Owl
    inquiry_seed: Dict[str, Any] = field(default_factory=dict)
    initial_context: Dict[str, Any] = field(default_factory=dict)

    # From previous cycle (if feedback loop)
    previous_cycle_id: Optional[str] = None
    previous_insights: List[Dict[str, Any]] = field(default_factory=list)
    continuity_context: Dict[str, Any] = field(default_factory=dict)

    # Configuration
    urgency: UrgencyLevel = UrgencyLevel.NORMAL
    timeout_seconds: int = 300
    max_depth: int = 5  # Max recursive cycles

    # Status
    initiated: bool = False
    initiated_at: Optional[datetime] = None
    red_owl_invoked: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InputValidation:
    """Result of input validation."""
    prompt_id: str = ""
    is_valid: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    sanitized_content: str = ""
    detected_language: str = "en"
    content_length: int = 0
    has_attachments: bool = False


@dataclass
class WhiteRabbitConfig:
    """Configuration for White Rabbit input handling."""

    # Validation
    max_input_length: int = 10000
    min_input_length: int = 1
    allowed_input_types: List[InputType] = field(
        default_factory=lambda: list(InputType)
    )

    # Classification
    default_intent_category: IntentCategory = IntentCategory.INQUIRY
    min_confidence_threshold: float = 0.5

    # Cycle initiation
    auto_initiate: bool = True
    require_validation: bool = True
    max_concurrent_cycles: int = 10

    # Feedback loop
    accept_feedback: bool = True
    max_cycle_depth: int = 10

    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_source: int = 10


# The White Rabbit Symbol - the guide into the journey
WHITE_RABBIT_SYMBOL = """
       (\\(\\
       ( -.-)
       o_(")(")

    Follow the White Rabbit.
    Every journey begins with a single prompt.
    The input that awakens the inquiry.
"""
