"""
YELLOW HONEYBEE - Implementation Specification Agent.

Yellow Honeybee is the YELLOW Enterprise (Level 4) in the Cosmic Council ROYGBV hierarchy.
It answers the fundamental question: WHAT exactly needs to be done?

This module implements genuine implementation specification with:
- Specification completeness (every action gets detailed specs)
- Validation rules (pre/post conditions for each step)
- Resource identification (specific resources identified)

The Three Falsifiable Criteria:
1. Specification completeness - every action gets detailed specs
2. Validation rules - pre/post conditions for each step
3. Resource identification - specific resources/endpoints/configs identified

Usage:
    from cosmic_council.agents.yellow_honeybee import YellowHoneybeeEngine, specify_implementation

    # Quick specification
    result = await specify_implementation(actions)
    print(result.plan.specifications)

    # Full control
    engine = YellowHoneybeeEngine(
        default_namespace="production",
    )
    result = await engine.specify(
        action_plan_id="plan-123",
        actions=actions,
    )

    # As a Cosmic Council Agent
    agent = create_yellow_honeybee_agent()
    result = await agent.process_task(context)
"""

# Core models
from .models import (
    # Enums
    SpecificationType,
    ResourceType,
    ValidationStatus,
    # Data classes
    Resource,
    ValidationRule,
    PreCondition,
    PostCondition,
    CommandSpec,
    ApiCallSpec,
    ConfigChangeSpec,
    DatabaseQuerySpec,
    KubernetesSpec,
    TaskSpecification,
    ImplementationPlan,
    # Configuration
    YellowHoneybeeConfig,
)

# Components
from .specification_generator import (
    SpecificationGenerator,
    SpecificationResult,
    create_specification_generator,
)

from .resource_identifier import (
    ResourceIdentifier,
    ResourceDiscoveryResult,
    create_resource_identifier,
)

from .validation_builder import (
    ValidationBuilder,
    ValidationResult,
    create_validation_builder,
)

# Main engine
from .engine import (
    YellowHoneybeeEngine,
    YellowHoneybeeResult,
    create_yellow_honeybee,
    get_yellow_honeybee,
    specify_implementation,
)

# Cosmic Council Agent Integration
from .agent import (
    YellowHoneybeeAgent,
    create_yellow_honeybee_agent,
    get_specification_agent,
)

__all__ = [
    # Enums
    "SpecificationType",
    "ResourceType",
    "ValidationStatus",
    # Core data classes
    "Resource",
    "ValidationRule",
    "PreCondition",
    "PostCondition",
    "CommandSpec",
    "ApiCallSpec",
    "ConfigChangeSpec",
    "DatabaseQuerySpec",
    "KubernetesSpec",
    "TaskSpecification",
    "ImplementationPlan",
    # Configuration
    "YellowHoneybeeConfig",
    # Component classes
    "SpecificationGenerator",
    "SpecificationResult",
    "ResourceIdentifier",
    "ResourceDiscoveryResult",
    "ValidationBuilder",
    "ValidationResult",
    # Engine
    "YellowHoneybeeEngine",
    "YellowHoneybeeResult",
    # Factory functions
    "create_specification_generator",
    "create_resource_identifier",
    "create_validation_builder",
    "create_yellow_honeybee",
    "get_yellow_honeybee",
    # Convenience functions
    "specify_implementation",
    # Cosmic Council Agent
    "YellowHoneybeeAgent",
    "create_yellow_honeybee_agent",
    "get_specification_agent",
]

__version__ = "0.1.0"
