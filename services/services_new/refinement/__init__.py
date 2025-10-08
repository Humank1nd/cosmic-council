"""
Cosmic Council Refinement Engine
A problem-refinement ladder system with Deci → Quecto layers and ROYGBV cycles.

This package implements the Cosmic Council's fractal problem-solving approach where:
1. Problems start at the Deci layer (broad framing)
2. Complete ROYGBV cycles are executed at each layer
3. The escalator decides whether to stay, refine deeper, or resolve
4. Refinement continues until the problem is solved or reaches Quecto

Key Components:
- layers.py: Defines the 12 refinement layers and their capabilities
- escalator.py: Decision engine for refinement vs resolution
- sector_engine.py: ROYGBV sector execution with handoffs
- layer_orchestration.py: Manages complete cycles per layer
- refinement_tracker.py: Tracks genealogy and audit trails
- api.py: REST API endpoints for problem submission and tracking
- governance_tests.py: Tests for system integrity and invariants
"""

from .layers import (
    LayerDefinitions,
    LayerType,
    LayerCapability,
    LayerRefinementEngine
)

from .escalator import (
    EscalatorEngine,
    EscalatorAction,
    EscalatorDecision,
    SolutionCandidate,
    EscalatorMetrics
)

from .sector_engine import (
    SectorEngine,
    SectorType,
    SectorExecutor,
    SectorResult,
    HandoffData,
    RedSectorExecutor,
    OrangeSectorExecutor,
    YellowSectorExecutor,
    GreenSectorExecutor,
    BlueSectorExecutor,
    PurpleSectorExecutor
)

from .layer_orchestration import (
    LayerOrchestrator,
    LayerRun,
    LayerRunStatus,
    ProblemContext
)

from .refinement_tracker import (
    RefinementTracker,
    RefinementNode,
    RefinementPath,
    TrackingEvent,
    TrackingEventType
)

from .governance_tests import (
    GovernanceTests,
    GovernanceInvariants
)

# Version information
__version__ = "1.0.0"
__author__ = "Cosmic Council"
__description__ = "Problem refinement system with Deci → Quecto layers and ROYGBV cycles"

# Main exports
__all__ = [
    # Core classes
    "LayerOrchestrator",
    "EscalatorEngine", 
    "SectorEngine",
    "RefinementTracker",
    "GovernanceTests",
    
    # Data models
    "LayerCapability",
    "SolutionCandidate",
    "EscalatorDecision",
    "SectorResult",
    "HandoffData",
    "LayerRun",
    "ProblemContext",
    "RefinementNode",
    "TrackingEvent",
    
    # Enums
    "LayerType",
    "EscalatorAction",
    "SectorType",
    "LayerRunStatus",
    "TrackingEventType",
    
    # Utilities
    "LayerDefinitions",
    "LayerRefinementEngine",
    "EscalatorMetrics",
    "GovernanceInvariants"
]

# Quick start function
def create_refinement_engine(config: dict = None):
    """
    Create a complete refinement engine with all components.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Tuple of (orchestrator, tracker, escalator, sector_engine)
    """
    from .layer_orchestration import LayerOrchestrator
    from .refinement_tracker import RefinementTracker
    from .escalator import EscalatorEngine
    from .sector_engine import SectorEngine
    
    orchestrator = LayerOrchestrator(config)
    tracker = RefinementTracker()
    escalator = EscalatorEngine(config)
    sector_engine = SectorEngine()
    
    return orchestrator, tracker, escalator, sector_engine


# Example usage
if __name__ == "__main__":
    print("Cosmic Council Refinement Engine")
    print(f"Version: {__version__}")
    print(f"Description: {__description__}")
    print("\nAvailable layers:")
    for layer_name in LayerDefinitions.get_layer_order():
        layer = LayerDefinitions.get_layer(layer_name)
        print(f"  {layer_name}: {layer.description}")
    
    print("\nQuick start:")
    print("  from refinement_engine import create_refinement_engine")
    print("  orchestrator, tracker, escalator, sector_engine = create_refinement_engine()")
