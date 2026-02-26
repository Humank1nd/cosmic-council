"""
BLUE DOLPHIN - Location Agent.

Blue Dolphin is the BLUE Enterprise (Level 6) in the Cosmic Council ROYGBV hierarchy.
It answers the fundamental question: WHERE should each action execute?

This module implements genuine location resolution with:
- Location resolution (every action has a specific target)
- Environment matching (actions matched to appropriate environments)
- Connectivity validation (all targets are reachable)

The Three Falsifiable Criteria:
1. Location resolution - every action has a resolved execution target
2. Environment matching - actions matched to appropriate environments
3. Connectivity validation - all targets are validated as reachable

Usage:
    from cosmic_council.agents.blue_dolphin import BlueDolphinEngine, locate_execution

    # Quick location
    result = await locate_execution(schedule_id, slots)
    print(result.location_plan.targets)

    # Full control
    engine = BlueDolphinEngine(
        config=BlueDolphinConfig(require_connectivity_check=True),
    )
    result = await engine.locate(
        schedule_id="schedule-123",
        slots=slots,
    )

    # As a Cosmic Council Agent
    agent = create_blue_dolphin_agent()
    result = await agent.process_task(context)
"""

# Core models
from .models import (
    # Enums
    EnvironmentType,
    LocationType,
    CloudProvider,
    ConnectivityStatus,
    TargetStatus,
    # Data classes
    NetworkEndpoint,
    Location,
    Environment,
    ExecutionTarget,
    RoutingRule,
    LocationPlan,
    # Configuration
    BlueDolphinConfig,
    # Constants
    STANDARD_ENVIRONMENTS,
    STANDARD_LOCATIONS,
)

# Components
from .location_resolver import (
    LocationResolver,
    ResolutionResult,
    BatchResolutionResult,
    create_location_resolver,
)

from .environment_analyzer import (
    EnvironmentAnalyzer,
    EnvironmentRequirement,
    EnvironmentMatch,
    EnvironmentAnalysisResult,
    create_environment_analyzer,
)

from .routing_engine import (
    RoutingEngine,
    ConnectivityCheck,
    RoutingDecision,
    RoutingResult,
    create_routing_engine,
)

# Main engine
from .engine import (
    BlueDolphinEngine,
    BlueDolphinResult,
    create_blue_dolphin,
    get_blue_dolphin,
    locate_execution,
)

# Cosmic Council Agent Integration
from .agent import (
    BlueDolphinAgent,
    create_blue_dolphin_agent,
    get_location_agent,
)

__all__ = [
    # Enums
    "EnvironmentType",
    "LocationType",
    "CloudProvider",
    "ConnectivityStatus",
    "TargetStatus",
    # Core data classes
    "NetworkEndpoint",
    "Location",
    "Environment",
    "ExecutionTarget",
    "RoutingRule",
    "LocationPlan",
    # Configuration
    "BlueDolphinConfig",
    # Constants
    "STANDARD_ENVIRONMENTS",
    "STANDARD_LOCATIONS",
    # Component classes
    "LocationResolver",
    "ResolutionResult",
    "BatchResolutionResult",
    "EnvironmentAnalyzer",
    "EnvironmentRequirement",
    "EnvironmentMatch",
    "EnvironmentAnalysisResult",
    "RoutingEngine",
    "ConnectivityCheck",
    "RoutingDecision",
    "RoutingResult",
    # Engine
    "BlueDolphinEngine",
    "BlueDolphinResult",
    # Factory functions
    "create_location_resolver",
    "create_environment_analyzer",
    "create_routing_engine",
    "create_blue_dolphin",
    "get_blue_dolphin",
    # Convenience functions
    "locate_execution",
    # Cosmic Council Agent
    "BlueDolphinAgent",
    "create_blue_dolphin_agent",
    "get_location_agent",
]

__version__ = "0.1.0"
