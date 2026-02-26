"""
ORANGE ORANGUTAN - Action Planning Agent.

Orange Orangutan is the ORANGE Enterprise (Level 3) in the Cosmic Council ROYGBV hierarchy.
It answers the fundamental question: HOW do we fix this?

This module implements genuine action planning with:
- Dependency ordering (topological sort of actions)
- Rollback reversibility (each action has a rollback procedure)
- Risk gates (high-risk actions require approval)

The Three Falsifiable Criteria:
1. Dependency ordering - actions are topologically sorted by dependencies
2. Rollback reversibility - every action has a defined rollback procedure
3. Risk gates - high-risk actions require human approval

Usage:
    from cosmic_council.agents.orange_orangutan import OrangeOrangutanEngine, plan_actions

    # Quick planning
    result = await plan_actions("Database connection pool exhausted")
    print(result.plan.execution_order)

    # Full control
    engine = OrangeOrangutanEngine(
        critical_services=["payment-service", "auth-service"],
    )
    result = await engine.plan("Service X returning 500 errors")

    # As a Cosmic Council Agent
    agent = create_orange_orangutan_agent()
    result = await agent.process_task(context)
"""

# Core models
from .models import (
    # Enums
    RiskLevel,
    ActionStatus,
    ActionCategory,
    # Data classes
    RollbackProcedure,
    Dependency,
    ActionStep,
    ActionPlan,
    # Configuration
    OrangeOrangutanConfig,
    # Benchmark types
    OrangeOrangutanBenchmarkCase,
    OrangeOrangutanEvalResult,
)

# Components
from .action_decomposer import (
    ActionDecomposer,
    DecompositionResult,
    create_action_decomposer,
)

from .dependency_resolver import (
    DependencyResolver,
    DependencyResolutionResult,
    create_dependency_resolver,
)

from .risk_assessor import (
    RiskAssessor,
    RiskAssessment,
    PlanRiskAssessment,
    create_risk_assessor,
)

from .rollback_planner import (
    RollbackPlanner,
    RollbackPlan,
    create_rollback_planner,
)

# Main engine
from .engine import (
    OrangeOrangutanEngine,
    OrangeOrangutanResult,
    create_orange_orangutan,
    get_orange_orangutan,
    plan_actions,
)

# Cosmic Council Agent Integration
from .agent import (
    OrangeOrangutanAgent,
    create_orange_orangutan_agent,
    get_planning_agent,
)

__all__ = [
    # Enums
    "RiskLevel",
    "ActionStatus",
    "ActionCategory",
    # Core data classes
    "RollbackProcedure",
    "Dependency",
    "ActionStep",
    "ActionPlan",
    # Configuration
    "OrangeOrangutanConfig",
    # Benchmark types
    "OrangeOrangutanBenchmarkCase",
    "OrangeOrangutanEvalResult",
    # Component classes
    "ActionDecomposer",
    "DecompositionResult",
    "DependencyResolver",
    "DependencyResolutionResult",
    "RiskAssessor",
    "RiskAssessment",
    "PlanRiskAssessment",
    "RollbackPlanner",
    "RollbackPlan",
    # Engine
    "OrangeOrangutanEngine",
    "OrangeOrangutanResult",
    # Factory functions
    "create_action_decomposer",
    "create_dependency_resolver",
    "create_risk_assessor",
    "create_rollback_planner",
    "create_orange_orangutan",
    "get_orange_orangutan",
    # Convenience functions
    "plan_actions",
    # Cosmic Council Agent
    "OrangeOrangutanAgent",
    "create_orange_orangutan_agent",
    "get_planning_agent",
]

__version__ = "0.1.0"
