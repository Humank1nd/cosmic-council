"""
BLACK SNAKE - Execution & Recursion Agent.

Black Snake is the 7th step in the Cosmic Council hierarchy.
It closes the eternal cycle - executing actions from Purple Elephant
and feeding insights back to Red Owl for the next iteration.

The Ouroboros - the serpent consuming its tail.

This module implements genuine execution with:
- Execution completion (all assigned actions executed)
- Outcome capture (results properly recorded)
- Cycle recursion (insights feed back to initiate new inquiry)

The Three Falsifiable Criteria:
1. Execution completion - all assigned actions are executed
2. Outcome capture - results are properly recorded
3. Cycle recursion - insights feed back to initiate new inquiry

Usage:
    from cosmic_council.agents.black_snake import BlackSnakeEngine, execute_and_recurse

    # Quick execution
    result = await execute_and_recurse(responsibility_plan_id, assignments)
    print(result.execution_plan.insights)

    # Full control
    engine = BlackSnakeEngine(
        config=BlackSnakeConfig(auto_feed_forward=True),
    )
    result = await engine.execute(
        responsibility_plan_id="resp-123",
        assignments=assignments,
    )

    # As a Cosmic Council Agent
    agent = create_black_snake_agent()
    result = await agent.process_task(context)
"""

# Core models
from .models import (
    # Enums
    ExecutionStatus,
    OutcomeType,
    InsightType,
    CyclePhase,
    # Data classes
    ExecutionRecord,
    ExecutionOutcome,
    CycleInsight,
    CycleState,
    ExecutionPlan,
    # Configuration
    BlackSnakeConfig,
    # Constants
    OUROBOROS_SYMBOL,
)

# Executor (Criterion 1)
from .executor import (
    ActionExecutor,
    ExecutionContext,
    ExecutionResult,
    create_action_executor,
)

# Outcome Collector (Criterion 2)
from .outcome_collector import (
    OutcomeCollector,
    OutcomeAnalysis,
    BatchOutcomeResult,
    create_outcome_collector,
)

# Cycle Manager (Criterion 3)
from .cycle_manager import (
    CycleManager,
    InsightSeed,
    CycleFeedback,
    CycleCompletionResult,
    create_cycle_manager,
)

# Main engine
from .engine import (
    BlackSnakeEngine,
    BlackSnakeResult,
    create_black_snake,
    get_black_snake,
    execute_and_recurse,
)

# Note: Agent integration requires additional dependencies from the parent package
# Import explicitly when needed:
# from .agent import BlackSnakeAgent, create_black_snake_agent, get_execution_agent

__all__ = [
    # Enums
    "ExecutionStatus",
    "OutcomeType",
    "InsightType",
    "CyclePhase",
    # Core data classes
    "ExecutionRecord",
    "ExecutionOutcome",
    "CycleInsight",
    "CycleState",
    "ExecutionPlan",
    # Configuration
    "BlackSnakeConfig",
    # Constants
    "OUROBOROS_SYMBOL",
    # Executor
    "ActionExecutor",
    "ExecutionContext",
    "ExecutionResult",
    "create_action_executor",
    # Outcome Collector
    "OutcomeCollector",
    "OutcomeAnalysis",
    "BatchOutcomeResult",
    "create_outcome_collector",
    # Cycle Manager
    "CycleManager",
    "InsightSeed",
    "CycleFeedback",
    "CycleCompletionResult",
    "create_cycle_manager",
    # Engine
    "BlackSnakeEngine",
    "BlackSnakeResult",
    "create_black_snake",
    "get_black_snake",
    # Convenience functions
    "execute_and_recurse",
]

__version__ = "0.1.0"
