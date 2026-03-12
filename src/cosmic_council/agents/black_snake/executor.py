"""
BLACK SNAKE - Action Executor.

Executes assigned actions from Purple Elephant.
This implements Criterion 1: Execution completion.

All assigned actions must be executed.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime

import structlog

from .models import (
    ExecutionRecord,
    ExecutionStatus,
    BlackSnakeConfig,
)

logger = structlog.get_logger(__name__)


@dataclass
class ExecutionContext:
    """Context for action execution."""
    execution_id: str = ""
    action_id: str = ""
    assignment_id: str = ""
    target_id: str = ""

    # What to do
    action_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)

    # Where to do it
    location: str = ""
    namespace: str = ""
    environment: str = ""

    # Who is doing it
    executor_id: str = ""
    executor_type: str = "automation"

    # Constraints
    timeout_seconds: int = 300
    dry_run: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of executing an action."""
    record: ExecutionRecord
    success: bool = False
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    changes_made: List[str] = field(default_factory=list)
    rollback_data: Dict[str, Any] = field(default_factory=dict)


# Action handler type
ActionHandler = Callable[[ExecutionContext], "asyncio.Future[ExecutionResult]"]


class ActionExecutor:
    """
    Executes actions based on assignments.

    Criterion 1: All assigned actions are executed.
    """

    def __init__(
        self,
        config: Optional[BlackSnakeConfig] = None,
        handlers: Optional[Dict[str, ActionHandler]] = None,
    ):
        """
        Initialize the action executor.

        Args:
            config: Configuration
            handlers: Custom action handlers
        """
        self.config = config or BlackSnakeConfig()
        self.handlers: Dict[str, ActionHandler] = handlers or {}

        # Register default handlers
        self._register_default_handlers()

        # Track executions
        self._active_executions: Dict[str, ExecutionContext] = {}
        self._execution_history: List[ExecutionRecord] = []

        logger.info(
            "action_executor_initialized",
            handler_count=len(self.handlers),
            parallel=self.config.parallel_execution,
        )

    def _register_default_handlers(self):
        """Register default action handlers."""
        # These simulate common operations
        self.handlers["database"] = self._handle_database_action
        self.handlers["scaling"] = self._handle_scaling_action
        self.handlers["deployment"] = self._handle_deployment_action
        self.handlers["restart"] = self._handle_restart_action
        self.handlers["monitoring"] = self._handle_monitoring_action
        self.handlers["notification"] = self._handle_notification_action
        self.handlers["backup"] = self._handle_backup_action
        self.handlers["default"] = self._handle_default_action

    async def execute(
        self,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Execute a single action.

        Args:
            context: Execution context

        Returns:
            ExecutionResult
        """
        # Create execution record
        record = ExecutionRecord(
            id=context.execution_id or str(time.time()),
            action_id=context.action_id,
            assignment_id=context.assignment_id,
            target_id=context.target_id,
            executor_id=context.executor_id,
            executor_type=context.executor_type,
            scheduled_at=datetime.utcnow(),
        )

        # Track active execution
        self._active_executions[record.id] = context

        try:
            # Check dry run
            if self.config.dry_run or context.dry_run:
                logger.info(
                    "dry_run_execution",
                    action_id=context.action_id,
                )
                record.status = ExecutionStatus.COMPLETED
                record.success = True
                record.completed_at = datetime.utcnow()
                return ExecutionResult(
                    record=record,
                    success=True,
                    output={"dry_run": True},
                )

            # Find handler
            handler = self._get_handler(context.action_type)

            # Execute with timeout
            record.started_at = datetime.utcnow()
            record.status = ExecutionStatus.IN_PROGRESS

            result = await asyncio.wait_for(
                handler(context),
                timeout=context.timeout_seconds,
            )

            # Update record from result
            record.status = ExecutionStatus.COMPLETED if result.success else ExecutionStatus.FAILED
            record.success = result.success
            record.output = result.output
            record.error = result.error
            record.changes_made = result.changes_made
            record.rollback_data = result.rollback_data
            record.rollback_available = bool(result.rollback_data)
            record.completed_at = datetime.utcnow()
            record.duration_ms = int(
                (record.completed_at - record.started_at).total_seconds() * 1000
            )

            logger.info(
                "action_executed",
                action_id=context.action_id,
                success=result.success,
                duration_ms=record.duration_ms,
            )

            return ExecutionResult(
                record=record,
                success=result.success,
                output=result.output,
                error=result.error,
                changes_made=result.changes_made,
                rollback_data=result.rollback_data,
            )

        except asyncio.TimeoutError:
            record.status = ExecutionStatus.FAILED
            record.error = f"Execution timed out after {context.timeout_seconds}s"
            record.error_code = "TIMEOUT"
            record.completed_at = datetime.utcnow()

            logger.error(
                "execution_timeout",
                action_id=context.action_id,
                timeout=context.timeout_seconds,
            )

            return ExecutionResult(
                record=record,
                success=False,
                error=record.error,
            )

        except Exception as e:
            record.status = ExecutionStatus.FAILED
            record.error = str(e)
            record.error_code = "EXCEPTION"
            record.completed_at = datetime.utcnow()

            logger.error(
                "execution_failed",
                action_id=context.action_id,
                error=str(e),
            )

            return ExecutionResult(
                record=record,
                success=False,
                error=str(e),
            )

        finally:
            # Remove from active
            self._active_executions.pop(record.id, None)
            # Add to history
            self._execution_history.append(record)

    async def execute_batch(
        self,
        contexts: List[ExecutionContext],
    ) -> List[ExecutionResult]:
        """
        Execute multiple actions.

        Args:
            contexts: List of execution contexts

        Returns:
            List of ExecutionResult
        """
        if self.config.parallel_execution:
            # Execute in parallel with limit
            semaphore = asyncio.Semaphore(self.config.max_parallel)

            async def limited_execute(ctx: ExecutionContext) -> ExecutionResult:
                async with semaphore:
                    return await self.execute(ctx)

            results = await asyncio.gather(
                *[limited_execute(ctx) for ctx in contexts],
                return_exceptions=True,
            )

            # Handle any exceptions
            final_results = []
            for ctx, result in zip(contexts, results):
                if isinstance(result, Exception):
                    record = ExecutionRecord(
                        action_id=ctx.action_id,
                        status=ExecutionStatus.FAILED,
                        error=str(result),
                    )
                    final_results.append(ExecutionResult(
                        record=record,
                        success=False,
                        error=str(result),
                    ))
                else:
                    final_results.append(result)

            return final_results
        else:
            # Execute sequentially
            results = []
            for ctx in contexts:
                result = await self.execute(ctx)
                results.append(result)

                # Retry if configured
                if not result.success and self.config.retry_failed:
                    for attempt in range(self.config.max_retries):
                        logger.info(
                            "retrying_execution",
                            action_id=ctx.action_id,
                            attempt=attempt + 1,
                        )
                        result = await self.execute(ctx)
                        if result.success:
                            results[-1] = result
                            break

            return results

    def _get_handler(self, action_type: str) -> ActionHandler:
        """Get handler for action type."""
        # Try exact match
        if action_type in self.handlers:
            return self.handlers[action_type]

        # Try category match
        action_lower = action_type.lower()
        for key in self.handlers:
            if key in action_lower:
                return self.handlers[key]

        # Default handler
        return self.handlers["default"]

    # Default handlers (simulated)
    async def _handle_database_action(self, ctx: ExecutionContext) -> ExecutionResult:
        """Handle database actions."""
        await asyncio.sleep(0.1)  # Simulate work
        return ExecutionResult(
            record=ExecutionRecord(action_id=ctx.action_id),
            success=True,
            output={"tables_affected": 3, "rows_modified": 150},
            changes_made=["Updated database configuration"],
            rollback_data={"previous_config": "..."},
        )

    async def _handle_scaling_action(self, ctx: ExecutionContext) -> ExecutionResult:
        """Handle scaling actions."""
        await asyncio.sleep(0.1)
        return ExecutionResult(
            record=ExecutionRecord(action_id=ctx.action_id),
            success=True,
            output={"replicas_before": 3, "replicas_after": 5},
            changes_made=["Scaled deployment to 5 replicas"],
            rollback_data={"previous_replicas": 3},
        )

    async def _handle_deployment_action(self, ctx: ExecutionContext) -> ExecutionResult:
        """Handle deployment actions."""
        await asyncio.sleep(0.15)
        return ExecutionResult(
            record=ExecutionRecord(action_id=ctx.action_id),
            success=True,
            output={"pods_updated": 5, "rollout_complete": True},
            changes_made=["Deployed new version", "Updated 5 pods"],
            rollback_data={"previous_version": "v1.2.3"},
        )

    async def _handle_restart_action(self, ctx: ExecutionContext) -> ExecutionResult:
        """Handle restart actions."""
        await asyncio.sleep(0.1)
        return ExecutionResult(
            record=ExecutionRecord(action_id=ctx.action_id),
            success=True,
            output={"pods_restarted": 3, "downtime_ms": 500},
            changes_made=["Restarted 3 pods"],
        )

    async def _handle_monitoring_action(self, ctx: ExecutionContext) -> ExecutionResult:
        """Handle monitoring actions."""
        await asyncio.sleep(0.05)
        return ExecutionResult(
            record=ExecutionRecord(action_id=ctx.action_id),
            success=True,
            output={"metrics_collected": 25, "alerts_checked": 10},
            changes_made=[],
        )

    async def _handle_notification_action(self, ctx: ExecutionContext) -> ExecutionResult:
        """Handle notification actions."""
        await asyncio.sleep(0.02)
        return ExecutionResult(
            record=ExecutionRecord(action_id=ctx.action_id),
            success=True,
            output={"notifications_sent": 3, "channels_used": ["slack", "email"]},
            changes_made=[],
        )

    async def _handle_backup_action(self, ctx: ExecutionContext) -> ExecutionResult:
        """Handle backup actions."""
        await asyncio.sleep(0.1)
        return ExecutionResult(
            record=ExecutionRecord(action_id=ctx.action_id),
            success=True,
            output={"backup_size_mb": 256, "backup_location": "s3://backups/..."},
            changes_made=["Created backup snapshot"],
            rollback_data={"backup_id": "backup-12345"},
        )

    async def _handle_default_action(self, ctx: ExecutionContext) -> ExecutionResult:
        """Default handler for unknown actions."""
        await asyncio.sleep(0.05)
        return ExecutionResult(
            record=ExecutionRecord(action_id=ctx.action_id),
            success=True,
            output={"action_type": ctx.action_type, "handled_by": "default"},
            changes_made=[f"Executed {ctx.action_type}"],
        )

    async def rollback(
        self,
        execution_id: str,
    ) -> ExecutionResult:
        """
        Rollback a previous execution.

        Args:
            execution_id: ID of execution to rollback

        Returns:
            ExecutionResult of rollback
        """
        # Find original execution
        original = None
        for record in self._execution_history:
            if record.id == execution_id:
                original = record
                break

        if not original:
            return ExecutionResult(
                record=ExecutionRecord(
                    action_id=f"rollback-{execution_id}",
                    status=ExecutionStatus.FAILED,
                    error="Original execution not found",
                ),
                success=False,
                error="Original execution not found",
            )

        if not original.rollback_available:
            return ExecutionResult(
                record=ExecutionRecord(
                    action_id=f"rollback-{execution_id}",
                    status=ExecutionStatus.FAILED,
                    error="Rollback not available",
                ),
                success=False,
                error="Rollback not available for this execution",
            )

        # Simulate rollback
        await asyncio.sleep(0.1)

        original.rollback_executed = True

        logger.info(
            "rollback_executed",
            execution_id=execution_id,
            action_id=original.action_id,
        )

        return ExecutionResult(
            record=ExecutionRecord(
                action_id=f"rollback-{original.action_id}",
                status=ExecutionStatus.COMPLETED,
                success=True,
            ),
            success=True,
            output={"rolled_back": execution_id},
            changes_made=[f"Rolled back {original.action_id}"],
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get executor metrics."""
        total = len(self._execution_history)
        succeeded = sum(1 for e in self._execution_history if e.success)
        failed = sum(1 for e in self._execution_history if not e.success)

        return {
            "total_executions": total,
            "succeeded": succeeded,
            "failed": failed,
            "success_rate": succeeded / total if total > 0 else 0.0,
            "active_executions": len(self._active_executions),
        }


def create_action_executor(
    config: Optional[BlackSnakeConfig] = None,
    handlers: Optional[Dict[str, ActionHandler]] = None,
) -> ActionExecutor:
    """Factory function to create an ActionExecutor."""
    return ActionExecutor(
        config=config,
        handlers=handlers,
    )
