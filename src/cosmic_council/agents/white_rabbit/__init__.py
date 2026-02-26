"""
WHITE RABBIT - Input & Initiation Agent.

White Rabbit is the entry point to the Cosmic Council.
It receives input prompts and initiates the inquiry cycle
by invoking Red Owl.

"Follow the White Rabbit" - Every journey begins here.

This module implements genuine input handling with:
- Input reception (all prompts properly received)
- Intent classification (intent correctly identified)
- Cycle initiation (Red Owl properly invoked)

The Three Falsifiable Criteria:
1. Input reception - all prompts are properly received and parsed
2. Intent classification - the intent/type is correctly identified
3. Cycle initiation - Red Owl is properly invoked with structured input

Usage:
    from cosmic_council.agents.white_rabbit import WhiteRabbitEngine, follow_the_rabbit

    # Quick start
    result = await follow_the_rabbit("Why is the database slow?")
    print(result.cycle_initiation.cycle_id)

    # Full control
    engine = WhiteRabbitEngine(
        config=WhiteRabbitConfig(auto_initiate=True),
    )
    result = await engine.process(
        content="Analyze the performance issue",
    )

    # As a Cosmic Council Agent
    agent = create_white_rabbit_agent()
    result = await agent.process_task(context)
"""

# Core models
from .models import (
    # Enums
    InputType,
    IntentCategory,
    UrgencyLevel,
    InputStatus,
    # Data classes
    InputPrompt,
    Intent,
    CycleInitiation,
    InputValidation,
    # Configuration
    WhiteRabbitConfig,
    # Constants
    WHITE_RABBIT_SYMBOL,
)

# Input Receiver (Criterion 1)
from .input_receiver import (
    InputReceiver,
    ReceivedInput,
    BatchReceiveResult,
    create_input_receiver,
)

# Intent Classifier (Criterion 2)
from .intent_classifier import (
    IntentClassifier,
    ClassificationResult,
    BatchClassificationResult,
    create_intent_classifier,
)

# Cycle Initiator (Criterion 3)
from .cycle_initiator import (
    CycleInitiator,
    InitiationResult,
    BatchInitiationResult,
    create_cycle_initiator,
)

# Main engine
from .engine import (
    WhiteRabbitEngine,
    WhiteRabbitResult,
    create_white_rabbit,
    get_white_rabbit,
    follow_the_rabbit,
)

# Note: Agent integration requires additional dependencies from the parent package
# Import explicitly when needed:
# from .agent import WhiteRabbitAgent, create_white_rabbit_agent, get_input_agent

__all__ = [
    # Enums
    "InputType",
    "IntentCategory",
    "UrgencyLevel",
    "InputStatus",
    # Core data classes
    "InputPrompt",
    "Intent",
    "CycleInitiation",
    "InputValidation",
    # Configuration
    "WhiteRabbitConfig",
    # Constants
    "WHITE_RABBIT_SYMBOL",
    # Input Receiver
    "InputReceiver",
    "ReceivedInput",
    "BatchReceiveResult",
    "create_input_receiver",
    # Intent Classifier
    "IntentClassifier",
    "ClassificationResult",
    "BatchClassificationResult",
    "create_intent_classifier",
    # Cycle Initiator
    "CycleInitiator",
    "InitiationResult",
    "BatchInitiationResult",
    "create_cycle_initiator",
    # Engine
    "WhiteRabbitEngine",
    "WhiteRabbitResult",
    "create_white_rabbit",
    "get_white_rabbit",
    # Convenience functions
    "follow_the_rabbit",
]

__version__ = "0.1.0"
