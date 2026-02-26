"""
BLACK SNAKE - Execution Engine.

The main orchestration engine for Black Snake.
Coordinates execution, outcome capture, and cycle recursion.

The Ouroboros - completing the eternal cycle of inquiry.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from uuid import uuid4

import structlog

from .models import (
    ExecutionRecord,
    ExecutionOutcome,
    CycleInsight,
    CycleState,
    CyclePhase,
    ExecutionPlan,
    ExecutionStatus,
    OutcomeType,
    BlackSnakeConfig,
)
from .executor import (
    ActionExecutor,
    ExecutionContext,
    ExecutionResult,
    create_action_executor,
)
from .outcome_collector import (
    OutcomeCollector,
    OutcomeAnalysis,
    BatchOutcomeResult,
    create_outcome_collector,
)
from .cycle_manager import (
    CycleManager,
    CycleFeedback,
    CycleCompletionResult,
    create_cycle_manager,
)

logger = structlog.get_logger(__name__)


@dataclass
class BlackSnakeResult:
    """Result of Black Snake execution."""
    success: bool = False
    execution_plan: Optional[ExecutionPlan] = None

    # Criterion metrics (0-1)
    execution_completion: float = 0.0  # Criterion 1
    outcome_capture: float = 0.0       # Criterion 2
    cycle_recursion: float = 0.0       # Criterion 3

    # Execution results
    execution_results: List[ExecutionResult] = field(default_factory=list)
    outcome_result: Optional[BatchOutcomeResult] = None
    cycle_result: Optional[CycleCompletionResult] = None

    # Timing
    duration_ms: int = 0

    # Diagnostics
    reasoning: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class BlackSnakeEngine:
    """
    Black Snake Execution Engine.

    The 7th step in the Cosmic Council - closing the eternal cycle.
    Executes actions, captures outcomes, and feeds insights back to Red Owl.

    Three Falsifiable Criteria:
    1. Execution completion - all assigned actions are executed
    2. Outcome capture - results are properly recorded
    3. Cycle recursion - insights feed back to initiate new inquiry
    """

    def __init__(
        self,
        config: Optional[BlackSnakeConfig] = None,
        executor: Optional[ActionExecutor] = None,
        outcome_collector: Optional[OutcomeCollector] = None,
        cycle_manager: Optional[CycleManager] = None,
    ):
        """
        Initialize the Black Snake engine.

        Args:
            config: Configuration
            executor: Action executor
            outcome_collector: Outcome collector
            cycle_manager: Cycle manager
        """
        self.config = config or BlackSnakeConfig()
        self.executor = executor or create_action_executor(self.config)
        self.outcome_collector = outcome_collector or create_outcome_collector(self.config)
        self.cycle_manager = cycle_manager or create_cycle_manager(self.config)

        logger.info(
            "black_snake_engine_initialized",
            dry_run=self.config.dry_run,
            parallel=self.config.parallel_execution,
        )

    async def execute(
        self,
        responsibility_plan_id: str,
        assignments: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> BlackSnakeResult:
        """
        Execute assigned actions and complete the cycle.

        Args:
            responsibility_plan_id: ID from Purple Elephant
            assignments: List of assignments to execute
            context: Execution context

        Returns:
            BlackSnakeResult
        """
        start_time = time.time()
        context = context or {}
        reasoning: List[str] = []
        warnings: List[str] = []

        # Generate cycle ID
        cycle_id = context.get("cycle_id", str(uuid4()))

        # Start cycle tracking
        cycle_state = self.cycle_manager.start_cycle(
            cycle_id=cycle_id,
            inquiry_id=context.get("inquiry_id"),
            metadata={"responsibility_plan_id": responsibility_plan_id},
        )

        reasoning.append(f"Started cycle {cycle_id} for responsibility plan {responsibility_plan_id}")

        # Create execution plan
        execution_plan = ExecutionPlan(
            cycle_id=cycle_id,
            responsibility_plan_id=responsibility_plan_id,
        )

        try:
            # Phase 1: Execute all actions (Criterion 1)
            execution_contexts = self._create_execution_contexts(assignments, context)
            execution_results = await self.executor.execute_batch(execution_contexts)

            execution_plan.executions = [r.record for r in execution_results]
            execution_plan.execution_order = [r.record.id for r in execution_results]

            # Calculate execution completion rate
            total_actions = len(assignments)
            executed_actions = len(execution_results)
            successful_actions = sum(1 for r in execution_results if r.success)

            execution_completion = executed_actions / total_actions if total_actions > 0 else 0.0

            reasoning.append(
                f"Executed {executed_actions}/{total_actions} actions, "
                f"{successful_actions} successful"
            )

            # Phase 2: Capture outcomes (Criterion 2)
            self.cycle_manager.update_phase(cycle_id, CyclePhase.EXECUTION)

            outcome_result = self.outcome_collector.collect_batch(
                results=execution_results,
                context=context,
            )

            execution_plan.outcomes = outcome_result.outcomes

            # Calculate outcome capture rate
            outcomes_captured = outcome_result.total_captured
            outcome_capture = outcomes_captured / executed_actions if executed_actions > 0 else 0.0

            reasoning.append(
                f"Captured {outcomes_captured} outcomes, "
                f"{outcome_result.surprises_detected} surprises detected"
            )

            # Record executions in cycle state
            self.cycle_manager.record_executions(
                cycle_id=cycle_id,
                executions=[r.record for r in execution_results],
                outcomes=outcome_result.outcomes,
            )

            # Phase 3: Generate insights and complete cycle (Criterion 3)
            insights = self.cycle_manager.generate_insights(
                outcomes=outcome_result.outcomes,
                analyses=outcome_result.analyses,
                context=context,
            )

            execution_plan.insights = insights
            execution_plan.insights_generated = len(insights)

            # Complete the cycle
            cycle_result = await self.cycle_manager.complete_cycle(
                cycle_id=cycle_id,
                insights=insights,
            )

            # Calculate cycle recursion rate
            # Recursion is successful if we generated insights and fed forward (or are ready to)
            has_insights = len(insights) > 0
            has_questions = len(cycle_result.feedback.new_questions) > 0
            fed_forward = cycle_result.next_cycle_initiated

            if self.config.auto_feed_forward:
                cycle_recursion = 1.0 if fed_forward else (0.5 if has_questions else 0.0)
            else:
                # If not auto-feeding, we just need to have prepared feedback
                cycle_recursion = 1.0 if has_questions else (0.5 if has_insights else 0.0)

            reasoning.append(
                f"Generated {len(insights)} insights, "
                f"{len(cycle_result.feedback.new_questions)} new questions"
            )

            if fed_forward:
                reasoning.append(f"Initiated next cycle: {cycle_result.next_cycle_id}")

            # Prepare next cycle seed
            if cycle_result.feedback.should_continue:
                execution_plan.next_cycle_seed = {
                    "questions": cycle_result.feedback.new_questions,
                    "hypotheses": cycle_result.feedback.hypotheses_to_test,
                    "evidence": cycle_result.feedback.evidence_collected,
                    "priority": cycle_result.feedback.priority,
                    "urgency": cycle_result.feedback.urgency,
                }

            # Validate execution plan
            self._validate_plan(execution_plan, warnings)

            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Update plan metrics
            execution_plan.executions_completed = successful_actions
            execution_plan.executions_failed = executed_actions - successful_actions
            execution_plan.outcomes_captured = outcomes_captured
            execution_plan.completed_at = datetime.utcnow()

            # Overall success
            success = (
                execution_completion >= 0.8 and
                outcome_capture >= 0.8 and
                execution_plan.is_valid
            )

            logger.info(
                "black_snake_execution_complete",
                cycle_id=cycle_id,
                success=success,
                execution_completion=execution_completion,
                outcome_capture=outcome_capture,
                cycle_recursion=cycle_recursion,
                duration_ms=duration_ms,
            )

            return BlackSnakeResult(
                success=success,
                execution_plan=execution_plan,
                execution_completion=execution_completion,
                outcome_capture=outcome_capture,
                cycle_recursion=cycle_recursion,
                execution_results=execution_results,
                outcome_result=outcome_result,
                cycle_result=cycle_result,
                duration_ms=duration_ms,
                reasoning=reasoning,
                warnings=warnings,
            )

        except Exception as e:
            logger.error(
                "black_snake_execution_failed",
                cycle_id=cycle_id,
                error=str(e),
            )

            duration_ms = int((time.time() - start_time) * 1000)
            warnings.append(f"Execution failed: {str(e)}")

            return BlackSnakeResult(
                success=False,
                execution_plan=execution_plan,
                duration_ms=duration_ms,
                reasoning=reasoning,
                warnings=warnings,
            )

    def _create_execution_contexts(
        self,
        assignments: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[ExecutionContext]:
        """Create execution contexts from assignments."""
        contexts = []

        for assignment in assignments:
            exec_context = ExecutionContext(
                execution_id=str(uuid4()),
                action_id=assignment.get("action_id", ""),
                assignment_id=assignment.get("id", ""),
                target_id=assignment.get("target_id", ""),
                action_type=assignment.get("action_type", assignment.get("category", "")),
                parameters=assignment.get("parameters", {}),
                location=assignment.get("location", ""),
                namespace=assignment.get("namespace", ""),
                environment=assignment.get("environment", ""),
                executor_id=assignment.get("executor_id", "automation"),
                executor_type=assignment.get("executor_type", "automation"),
                timeout_seconds=assignment.get("timeout_seconds", self.config.execution_timeout_seconds),
                dry_run=self.config.dry_run,
                metadata=assignment.get("metadata", {}),
            )
            contexts.append(exec_context)

        return contexts

    def _validate_plan(self, plan: ExecutionPlan, warnings: List[str]) -> None:
        """Validate the execution plan."""
        errors = []

        # Check all executions have outcomes
        exec_ids = {e.id for e in plan.executions}
        outcome_exec_ids = {o.execution_id for o in plan.outcomes}

        missing_outcomes = exec_ids - outcome_exec_ids
        if missing_outcomes:
            errors.append(f"Missing outcomes for executions: {missing_outcomes}")

        # Check for high failure rate
        if plan.executions:
            failure_rate = plan.executions_failed / len(plan.executions)
            if failure_rate > 0.5:
                warnings.append(f"High failure rate: {failure_rate:.1%}")

        # Check for insights if there were failures
        if plan.executions_failed > 0 and not plan.insights:
            warnings.append("No insights generated despite failures")

        plan.validation_errors = errors
        plan.is_valid = len(errors) == 0

    def set_red_owl_callback(self, callback: Callable) -> None:
        """Set the callback for feeding back to Red Owl."""
        self.cycle_manager.set_red_owl_callback(callback)

    def get_metrics(self) -> Dict[str, Any]:
        """Get combined metrics from all components."""
        return {
            "executor": self.executor.get_metrics(),
            "outcome_collector": self.outcome_collector.get_metrics(),
            "cycle_manager": self.cycle_manager.get_metrics(),
        }


# Global instance
_black_snake_instance: Optional[BlackSnakeEngine] = None


def create_black_snake(
    config: Optional[BlackSnakeConfig] = None,
) -> BlackSnakeEngine:
    """Factory function to create a BlackSnakeEngine."""
    return BlackSnakeEngine(config=config)


def get_black_snake() -> BlackSnakeEngine:
    """Get or create the global BlackSnakeEngine instance."""
    global _black_snake_instance
    if _black_snake_instance is None:
        _black_snake_instance = create_black_snake()
    return _black_snake_instance


async def execute_and_recurse(
    responsibility_plan_id: str,
    assignments: List[Dict[str, Any]],
    context: Optional[Dict[str, Any]] = None,
) -> BlackSnakeResult:
    """
    Convenience function for execution and cycle recursion.

    Args:
        responsibility_plan_id: ID from Purple Elephant
        assignments: List of assignments to execute
        context: Execution context

    Returns:
        BlackSnakeResult
    """
    engine = get_black_snake()
    return await engine.execute(
        responsibility_plan_id=responsibility_plan_id,
        assignments=assignments,
        context=context,
    )
