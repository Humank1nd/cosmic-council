"""
GREEN TURTLE - Scheduling Agent.

Green Turtle is the GREEN Enterprise (Level 5) in the Cosmic Council ROYGBV hierarchy.
It answers the fundamental question: WHEN should each action execute?

This module implements genuine scheduling with:
- Time window compliance (actions within valid windows)
- Dependency sequencing (topological ordering)
- Constraint satisfaction (all constraints met)

The Three Falsifiable Criteria:
1. Time window compliance - actions scheduled within valid time windows
2. Dependency sequencing - actions respect temporal dependencies
3. Constraint satisfaction - all scheduling constraints are met

Usage:
    from cosmic_council.agents.green_turtle import GreenTurtleEngine, schedule_execution

    # Quick scheduling
    result = await schedule_execution(specifications)
    print(result.schedule.execution_order)

    # Full control
    engine = GreenTurtleEngine(
        config=GreenTurtleConfig(prefer_off_peak=True),
    )
    result = await engine.schedule(
        implementation_plan_id="plan-123",
        specifications=specifications,
    )

    # As a Cosmic Council Agent
    agent = create_green_turtle_agent()
    result = await agent.process_task(context)
"""

# Core models
from .models import (
    # Enums
    SchedulePriority,
    TimeWindowType,
    ConstraintType,
    ScheduleStatus,
    # Data classes
    TimeWindow,
    SchedulingConstraint,
    TemporalDependency,
    ExecutionSlot,
    ExecutionSchedule,
    # Configuration
    GreenTurtleConfig,
    # Constants
    STANDARD_TIME_WINDOWS,
)

# Components
from .time_analyzer import (
    TimeAnalyzer,
    TimeSlot,
    TimeAnalysisResult,
    create_time_analyzer,
)

from .constraint_resolver import (
    ConstraintResolver,
    ConstraintViolation,
    ConstraintResolutionResult,
    create_constraint_resolver,
)

from .schedule_optimizer import (
    ScheduleOptimizer,
    OptimizationResult,
    create_schedule_optimizer,
)

# Main engine
from .engine import (
    GreenTurtleEngine,
    GreenTurtleResult,
    create_green_turtle,
    get_green_turtle,
    schedule_execution,
)

# Cosmic Council Agent Integration
from .agent import (
    GreenTurtleAgent,
    create_green_turtle_agent,
    get_scheduling_agent,
)

__all__ = [
    # Enums
    "SchedulePriority",
    "TimeWindowType",
    "ConstraintType",
    "ScheduleStatus",
    # Core data classes
    "TimeWindow",
    "SchedulingConstraint",
    "TemporalDependency",
    "ExecutionSlot",
    "ExecutionSchedule",
    # Configuration
    "GreenTurtleConfig",
    # Constants
    "STANDARD_TIME_WINDOWS",
    # Component classes
    "TimeAnalyzer",
    "TimeSlot",
    "TimeAnalysisResult",
    "ConstraintResolver",
    "ConstraintViolation",
    "ConstraintResolutionResult",
    "ScheduleOptimizer",
    "OptimizationResult",
    # Engine
    "GreenTurtleEngine",
    "GreenTurtleResult",
    # Factory functions
    "create_time_analyzer",
    "create_constraint_resolver",
    "create_schedule_optimizer",
    "create_green_turtle",
    "get_green_turtle",
    # Convenience functions
    "schedule_execution",
    # Cosmic Council Agent
    "GreenTurtleAgent",
    "create_green_turtle_agent",
    "get_scheduling_agent",
]

__version__ = "0.1.0"
