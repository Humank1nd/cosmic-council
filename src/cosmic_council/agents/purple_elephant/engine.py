"""
PURPLE ELEPHANT - Responsibility Engine.

Main orchestrator for the Purple Elephant Responsibility Agent.
Coordinates responsibility resolution, stakeholder analysis, and notifications.

Three Falsifiable Criteria:
1. Responsibility assignment - every action has a designated executor
2. Stakeholder identification - all relevant stakeholders identified
3. Notification routing - all parties properly notified
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

import structlog

from .models import (
    Stakeholder,
    ResponsibilityAssignment,
    ResponsibilityPlan,
    NotificationRecord,
    PurpleElephantConfig,
    STANDARD_STAKEHOLDERS,
)
from .responsibility_resolver import (
    ResponsibilityResolver,
    ResolutionResult,
    AssignmentRule,
    create_responsibility_resolver,
)
from .stakeholder_analyzer import (
    StakeholderAnalyzer,
    StakeholderAnalysisResult,
    create_stakeholder_analyzer,
)
from .notification_engine import (
    NotificationEngine,
    BatchNotificationResult,
    create_notification_engine,
)

logger = structlog.get_logger(__name__)


@dataclass
class PurpleElephantResult:
    """Result of Purple Elephant responsibility processing."""
    responsibility_plan: ResponsibilityPlan = field(default_factory=ResponsibilityPlan)
    success: bool = False
    duration_ms: int = 0

    # Criterion metrics
    responsibility_assignment: float = 0.0  # % of actions with executors
    stakeholder_identification: float = 0.0  # % of actions with stakeholders
    notification_routing: float = 0.0  # % of notifications sent

    # Details
    resolution_results: List[ResolutionResult] = field(default_factory=list)
    stakeholder_results: List[StakeholderAnalysisResult] = field(default_factory=list)
    notification_result: Optional[BatchNotificationResult] = None

    reasoning: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class PurpleElephantEngine:
    """
    Main engine for Purple Elephant responsibility agent.

    Orchestrates the three criteria:
    1. Responsibility assignment (ResponsibilityResolver)
    2. Stakeholder identification (StakeholderAnalyzer)
    3. Notification routing (NotificationEngine)
    """

    def __init__(
        self,
        config: Optional[PurpleElephantConfig] = None,
        stakeholders: Optional[Dict[str, Stakeholder]] = None,
        assignment_rules: Optional[List[AssignmentRule]] = None,
        llm_provider: Optional[Any] = None,
    ):
        """
        Initialize the Purple Elephant engine.

        Args:
            config: Configuration
            stakeholders: Available stakeholders
            assignment_rules: Assignment rules
            llm_provider: Optional LLM for intelligent assignment
        """
        self.config = config or PurpleElephantConfig()
        self.stakeholders = stakeholders or STANDARD_STAKEHOLDERS
        self.llm_provider = llm_provider

        # Initialize components
        self.responsibility_resolver = create_responsibility_resolver(
            stakeholders=self.stakeholders,
            assignment_rules=assignment_rules,
            config=self.config,
        )

        self.stakeholder_analyzer = create_stakeholder_analyzer(
            stakeholders=self.stakeholders,
            config=self.config,
        )

        self.notification_engine = create_notification_engine(
            config=self.config,
        )

        # Metrics
        self._plans_created = 0
        self._total_assignments = 0
        self._total_notifications = 0

        logger.info(
            "purple_elephant_engine_initialized",
            stakeholder_count=len(self.stakeholders),
            has_llm=llm_provider is not None,
        )

    async def assign(
        self,
        location_plan_id: str,
        targets: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> PurpleElephantResult:
        """
        Assign responsibilities for located targets.

        This is the main entry point that coordinates all three criteria.

        Args:
            location_plan_id: ID of the location plan from Blue Dolphin
            targets: Located execution targets
            context: Additional context

        Returns:
            PurpleElephantResult with responsibility plan
        """
        start_time = time.time()
        context = context or {}

        reasoning: List[str] = []
        warnings: List[str] = []

        # Create responsibility plan
        plan = ResponsibilityPlan(
            location_plan_id=location_plan_id,
        )

        reasoning.append(f"Processing {len(targets)} located targets")

        # ====================================================================
        # CRITERION 1: Responsibility Assignment
        # ====================================================================
        resolution_results: List[ResolutionResult] = []
        assignments: List[ResponsibilityAssignment] = []

        for target in targets:
            result = self.responsibility_resolver.resolve(
                action_id=target.get("action_id", ""),
                target_id=target.get("id", target.get("target_id", "")),
                slot_id=target.get("slot_id", ""),
                category=target.get("category", ""),
                risk_level=target.get("risk_level", "MEDIUM"),
                service_name=target.get("service_name", ""),
                context=context,
            )

            resolution_results.append(result)
            assignments.append(result.assignment)
            warnings.extend(result.warnings)

        # Calculate assignment rate
        assigned_count = sum(1 for r in resolution_results if r.success)
        assignment_rate = assigned_count / len(targets) if targets else 0.0

        plan.assignments = assignments
        plan.assignments_made = assigned_count
        plan.assignments_pending = len(targets) - assigned_count

        reasoning.append(
            f"Responsibility assignment: {assigned_count}/{len(targets)} ({assignment_rate:.0%})"
        )

        # ====================================================================
        # CRITERION 2: Stakeholder Identification
        # ====================================================================
        stakeholder_results = self.stakeholder_analyzer.analyze_batch(
            targets, context
        )

        # Count unique stakeholders
        all_stakeholders: Dict[str, Stakeholder] = {}
        for result in stakeholder_results:
            for match in result.identified_stakeholders:
                all_stakeholders[match.stakeholder.id] = match.stakeholder

        plan.stakeholders = list(all_stakeholders.values())
        plan.stakeholders_identified = len(all_stakeholders)

        stakeholder_rate = (
            sum(1 for r in stakeholder_results if r.success) / len(targets)
            if targets else 0.0
        )

        reasoning.append(
            f"Stakeholder identification: {len(all_stakeholders)} unique stakeholders"
        )
        reasoning.append(
            f"Stakeholder success rate: {stakeholder_rate:.0%}"
        )

        # ====================================================================
        # CRITERION 3: Notification Routing
        # ====================================================================
        notification_result = None
        notification_rate = 0.0

        if self.config.send_notifications:
            # Only notify assigned stakeholders
            assignments_to_notify = [a for a in assignments if a.is_assigned]

            notification_result = await self.notification_engine.notify_all(
                assignments_to_notify,
                context=context,
            )

            plan.notifications = notification_result.records
            plan.notifications_sent = notification_result.sent_count

            notification_rate = (
                notification_result.sent_count / len(assignments_to_notify)
                if assignments_to_notify else 1.0
            )

            reasoning.append(
                f"Notification routing: {notification_result.sent_count}/{len(assignments_to_notify)} sent"
            )

            if notification_result.failed_count > 0:
                warnings.append(
                    f"{notification_result.failed_count} notifications failed"
                )
        else:
            reasoning.append("Notifications disabled")
            notification_rate = 1.0  # Not applicable

        # ====================================================================
        # Finalize plan
        # ====================================================================
        plan.is_valid = (
            assignment_rate >= 0.8 and
            stakeholder_rate >= 0.8 and
            notification_rate >= 0.8
        )

        if not plan.is_valid:
            if assignment_rate < 0.8:
                plan.validation_errors.append(
                    f"Responsibility assignment too low: {assignment_rate:.0%}"
                )
            if stakeholder_rate < 0.8:
                plan.validation_errors.append(
                    f"Stakeholder identification too low: {stakeholder_rate:.0%}"
                )
            if notification_rate < 0.8:
                plan.validation_errors.append(
                    f"Notification routing too low: {notification_rate:.0%}"
                )

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Update metrics
        self._plans_created += 1
        self._total_assignments += assigned_count
        self._total_notifications += (notification_result.sent_count if notification_result else 0)

        logger.info(
            "responsibility_plan_created",
            location_plan_id=location_plan_id,
            targets=len(targets),
            assigned=assigned_count,
            stakeholders=len(all_stakeholders),
            notifications=notification_result.sent_count if notification_result else 0,
            is_valid=plan.is_valid,
            duration_ms=duration_ms,
        )

        return PurpleElephantResult(
            responsibility_plan=plan,
            success=plan.is_valid,
            duration_ms=duration_ms,
            responsibility_assignment=assignment_rate,
            stakeholder_identification=stakeholder_rate,
            notification_routing=notification_rate,
            resolution_results=resolution_results,
            stakeholder_results=stakeholder_results,
            notification_result=notification_result,
            reasoning=reasoning,
            warnings=warnings,
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get engine metrics."""
        notification_metrics = self.notification_engine.get_notification_metrics()
        stakeholder_summary = self.stakeholder_analyzer.get_stakeholder_summary()

        return {
            "plans_created": self._plans_created,
            "total_assignments": self._total_assignments,
            "total_notifications": self._total_notifications,
            "stakeholder_count": len(self.stakeholders),
            "notifications": notification_metrics,
            "stakeholders": stakeholder_summary,
        }


# Singleton instance
_purple_elephant_engine: Optional[PurpleElephantEngine] = None


def create_purple_elephant(
    config: Optional[PurpleElephantConfig] = None,
    stakeholders: Optional[Dict[str, Stakeholder]] = None,
    assignment_rules: Optional[List[AssignmentRule]] = None,
    llm_provider: Optional[Any] = None,
) -> PurpleElephantEngine:
    """Factory function to create a PurpleElephantEngine."""
    return PurpleElephantEngine(
        config=config,
        stakeholders=stakeholders,
        assignment_rules=assignment_rules,
        llm_provider=llm_provider,
    )


def get_purple_elephant() -> PurpleElephantEngine:
    """Get the default Purple Elephant engine instance."""
    global _purple_elephant_engine
    if _purple_elephant_engine is None:
        _purple_elephant_engine = create_purple_elephant()
    return _purple_elephant_engine


async def assign_responsibilities(
    location_plan_id: str,
    targets: List[Dict[str, Any]],
    context: Optional[Dict[str, Any]] = None,
) -> PurpleElephantResult:
    """
    Convenience function to assign responsibilities.

    Args:
        location_plan_id: Location plan ID from Blue Dolphin
        targets: Located targets to assign
        context: Additional context

    Returns:
        PurpleElephantResult with responsibility plan
    """
    engine = get_purple_elephant()
    return await engine.assign(location_plan_id, targets, context)
