"""
GREEN TURTLE - Constraint Resolver.

Resolves and validates scheduling constraints:
- Time window constraints
- Dependency constraints
- Resource constraints
- Rate limiting
- SLA requirements

This implements Criterion 3: All constraints must be satisfied.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

import structlog

from .models import (
    SchedulingConstraint,
    ConstraintType,
    TemporalDependency,
    ExecutionSlot,
    ScheduleStatus,
    TimeWindow,
)

logger = structlog.get_logger(__name__)


@dataclass
class ConstraintViolation:
    """A constraint violation."""
    constraint_id: str
    constraint_type: ConstraintType
    slot_id: str
    violation_type: str
    message: str
    severity: str = "error"  # error, warning
    can_reschedule: bool = True


@dataclass
class ConstraintResolutionResult:
    """Result of constraint resolution."""
    is_satisfied: bool = False
    violations: List[ConstraintViolation] = field(default_factory=list)
    resolved_constraints: List[SchedulingConstraint] = field(default_factory=list)
    suggested_adjustments: Dict[str, datetime] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    duration_ms: int = 0


class ConstraintResolver:
    """
    Resolves scheduling constraints.

    Criterion 3: All scheduling constraints must be met.
    """

    def __init__(
        self,
        max_concurrent_actions: int = 5,
        default_cooldown_seconds: int = 60,
        respect_sla: bool = True,
    ):
        """
        Initialize the constraint resolver.

        Args:
            max_concurrent_actions: Maximum concurrent actions
            default_cooldown_seconds: Default cooldown between actions
            respect_sla: Whether to respect SLA constraints
        """
        self.max_concurrent = max_concurrent_actions
        self.default_cooldown = default_cooldown_seconds
        self.respect_sla = respect_sla

        # Track state
        self._active_slots: Dict[str, ExecutionSlot] = {}
        self._completed_slots: Dict[str, ExecutionSlot] = {}
        self._resource_usage: Dict[str, List[str]] = {}  # resource -> slot_ids

        logger.info(
            "constraint_resolver_initialized",
            max_concurrent=max_concurrent_actions,
            default_cooldown=default_cooldown_seconds,
        )

    def resolve(
        self,
        slot: ExecutionSlot,
        all_slots: List[ExecutionSlot],
        time_windows: List[TimeWindow],
        context: Optional[Dict[str, Any]] = None,
    ) -> ConstraintResolutionResult:
        """
        Resolve constraints for a slot.

        Args:
            slot: The slot to resolve constraints for
            all_slots: All slots in the schedule
            time_windows: Available time windows
            context: Additional context

        Returns:
            ConstraintResolutionResult
        """
        import time
        start_time = time.time()
        context = context or {}

        violations: List[ConstraintViolation] = []
        resolved: List[SchedulingConstraint] = []
        adjustments: Dict[str, datetime] = {}
        warnings: List[str] = []

        # Check each constraint
        for constraint in slot.constraints:
            is_valid, violation = self._check_constraint(
                constraint, slot, all_slots, time_windows, context
            )

            if is_valid:
                constraint.is_satisfied = True
                resolved.append(constraint)
            else:
                constraint.is_satisfied = False
                if violation:
                    violations.append(violation)

                # Try to suggest adjustment
                adjustment = self._suggest_adjustment(
                    constraint, slot, all_slots, time_windows
                )
                if adjustment:
                    adjustments[slot.id] = adjustment

        # Check dependencies
        for dep in slot.dependencies:
            is_valid, violation = self._check_dependency(dep, slot, all_slots)
            if not is_valid and violation:
                violations.append(violation)
            dep.is_satisfied = is_valid

        # Check concurrency
        concurrency_ok, concurrency_violation = self._check_concurrency(slot, all_slots)
        if not concurrency_ok and concurrency_violation:
            violations.append(concurrency_violation)

        # Check cooldown
        cooldown_ok, cooldown_violation = self._check_cooldown(slot, all_slots)
        if not cooldown_ok and cooldown_violation:
            violations.append(cooldown_violation)

        # Determine overall satisfaction
        hard_violations = [
            v for v in violations
            if v.severity == "error"
        ]
        is_satisfied = len(hard_violations) == 0

        duration_ms = int((time.time() - start_time) * 1000)

        logger.debug(
            "constraints_resolved",
            slot_id=slot.id,
            is_satisfied=is_satisfied,
            violations=len(violations),
            resolved=len(resolved),
            duration_ms=duration_ms,
        )

        return ConstraintResolutionResult(
            is_satisfied=is_satisfied,
            violations=violations,
            resolved_constraints=resolved,
            suggested_adjustments=adjustments,
            warnings=warnings,
            duration_ms=duration_ms,
        )

    def _check_constraint(
        self,
        constraint: SchedulingConstraint,
        slot: ExecutionSlot,
        all_slots: List[ExecutionSlot],
        time_windows: List[TimeWindow],
        context: Dict[str, Any],
    ) -> Tuple[bool, Optional[ConstraintViolation]]:
        """Check a single constraint."""
        if constraint.type == ConstraintType.TIME_WINDOW:
            return self._check_time_window_constraint(constraint, slot, time_windows)

        elif constraint.type == ConstraintType.DEPENDENCY:
            return self._check_dependency_constraint(constraint, slot, all_slots)

        elif constraint.type == ConstraintType.RESOURCE:
            return self._check_resource_constraint(constraint, slot, context)

        elif constraint.type == ConstraintType.RATE_LIMIT:
            return self._check_rate_limit_constraint(constraint, slot, all_slots)

        elif constraint.type == ConstraintType.COOLDOWN:
            return self._check_cooldown_constraint(constraint, slot, all_slots)

        elif constraint.type == ConstraintType.BLACKOUT:
            return self._check_blackout_constraint(constraint, slot)

        elif constraint.type == ConstraintType.SLA:
            return self._check_sla_constraint(constraint, slot)

        elif constraint.type == ConstraintType.CONCURRENCY:
            return self._check_concurrency_constraint(constraint, slot, all_slots)

        return True, None  # Unknown constraint type passes

    def _check_time_window_constraint(
        self,
        constraint: SchedulingConstraint,
        slot: ExecutionSlot,
        time_windows: List[TimeWindow],
    ) -> Tuple[bool, Optional[ConstraintViolation]]:
        """Check time window constraint."""
        if not slot.scheduled_start:
            return False, ConstraintViolation(
                constraint_id=constraint.id,
                constraint_type=constraint.type,
                slot_id=slot.id,
                violation_type="no_schedule",
                message="Slot has no scheduled time",
            )

        # Find the window
        window = None
        for w in time_windows:
            if w.id == constraint.target_id:
                window = w
                break

        if not window:
            return True, None  # No specific window required

        if not window.contains(slot.scheduled_start):
            return False, ConstraintViolation(
                constraint_id=constraint.id,
                constraint_type=constraint.type,
                slot_id=slot.id,
                violation_type="outside_window",
                message=f"Scheduled time {slot.scheduled_start} is outside window {window.name}",
                can_reschedule=True,
            )

        return True, None

    def _check_dependency_constraint(
        self,
        constraint: SchedulingConstraint,
        slot: ExecutionSlot,
        all_slots: List[ExecutionSlot],
    ) -> Tuple[bool, Optional[ConstraintViolation]]:
        """Check dependency constraint."""
        prereq_id = constraint.target_id
        if not prereq_id:
            return True, None

        # Find prerequisite slot
        prereq_slot = None
        for s in all_slots:
            if s.action_id == prereq_id:
                prereq_slot = s
                break

        if not prereq_slot:
            return False, ConstraintViolation(
                constraint_id=constraint.id,
                constraint_type=constraint.type,
                slot_id=slot.id,
                violation_type="missing_prerequisite",
                message=f"Prerequisite action {prereq_id} not found in schedule",
            )

        if not prereq_slot.scheduled_start or not slot.scheduled_start:
            return True, None  # Can't check without schedules

        prereq_end = prereq_slot.scheduled_end or (
            prereq_slot.scheduled_start +
            timedelta(seconds=prereq_slot.estimated_duration_seconds)
        )

        if slot.scheduled_start < prereq_end:
            return False, ConstraintViolation(
                constraint_id=constraint.id,
                constraint_type=constraint.type,
                slot_id=slot.id,
                violation_type="dependency_order",
                message=f"Slot scheduled before prerequisite {prereq_id} completes",
                can_reschedule=True,
            )

        return True, None

    def _check_resource_constraint(
        self,
        constraint: SchedulingConstraint,
        slot: ExecutionSlot,
        context: Dict[str, Any],
    ) -> Tuple[bool, Optional[ConstraintViolation]]:
        """Check resource availability constraint."""
        resource_id = constraint.target_id
        if not resource_id:
            return True, None

        # Check if resource is available (from context)
        available_resources = context.get("available_resources", set())
        if resource_id in available_resources:
            return True, None

        # Check if resource is in use
        if resource_id in self._resource_usage:
            active_slots = self._resource_usage[resource_id]
            if active_slots:
                return False, ConstraintViolation(
                    constraint_id=constraint.id,
                    constraint_type=constraint.type,
                    slot_id=slot.id,
                    violation_type="resource_busy",
                    message=f"Resource {resource_id} is in use by other slots",
                    can_reschedule=True,
                )

        return True, None

    def _check_rate_limit_constraint(
        self,
        constraint: SchedulingConstraint,
        slot: ExecutionSlot,
        all_slots: List[ExecutionSlot],
    ) -> Tuple[bool, Optional[ConstraintViolation]]:
        """Check rate limiting constraint."""
        max_per_period = constraint.max_value or 10
        period_seconds = constraint.duration_seconds or 3600

        if not slot.scheduled_start:
            return True, None

        period_start = slot.scheduled_start - timedelta(seconds=period_seconds)
        period_end = slot.scheduled_start

        # Count slots in period
        count = 0
        for s in all_slots:
            if s.id == slot.id:
                continue
            if s.scheduled_start and period_start <= s.scheduled_start <= period_end:
                count += 1

        if count >= max_per_period:
            return False, ConstraintViolation(
                constraint_id=constraint.id,
                constraint_type=constraint.type,
                slot_id=slot.id,
                violation_type="rate_limit_exceeded",
                message=f"Rate limit of {max_per_period} per {period_seconds}s exceeded",
                can_reschedule=True,
            )

        return True, None

    def _check_cooldown_constraint(
        self,
        constraint: SchedulingConstraint,
        slot: ExecutionSlot,
        all_slots: List[ExecutionSlot],
    ) -> Tuple[bool, Optional[ConstraintViolation]]:
        """Check cooldown constraint."""
        cooldown = constraint.cooldown_seconds or self.default_cooldown

        if not slot.scheduled_start:
            return True, None

        # Check for any slot ending within cooldown period
        for s in all_slots:
            if s.id == slot.id:
                continue
            if not s.scheduled_end:
                continue

            gap = (slot.scheduled_start - s.scheduled_end).total_seconds()
            if 0 < gap < cooldown:
                return False, ConstraintViolation(
                    constraint_id=constraint.id,
                    constraint_type=constraint.type,
                    slot_id=slot.id,
                    violation_type="cooldown_violated",
                    message=f"Only {gap}s gap, need {cooldown}s cooldown",
                    can_reschedule=True,
                )

        return True, None

    def _check_blackout_constraint(
        self,
        constraint: SchedulingConstraint,
        slot: ExecutionSlot,
    ) -> Tuple[bool, Optional[ConstraintViolation]]:
        """Check blackout period constraint."""
        if not slot.scheduled_start:
            return True, None

        blackout_start = constraint.value.get("start") if isinstance(constraint.value, dict) else None
        blackout_end = constraint.value.get("end") if isinstance(constraint.value, dict) else None

        if blackout_start and blackout_end:
            if blackout_start <= slot.scheduled_start <= blackout_end:
                return False, ConstraintViolation(
                    constraint_id=constraint.id,
                    constraint_type=constraint.type,
                    slot_id=slot.id,
                    violation_type="blackout_period",
                    message=f"Slot scheduled during blackout period",
                    can_reschedule=True,
                )

        return True, None

    def _check_sla_constraint(
        self,
        constraint: SchedulingConstraint,
        slot: ExecutionSlot,
    ) -> Tuple[bool, Optional[ConstraintViolation]]:
        """Check SLA constraint."""
        if not self.respect_sla:
            return True, None

        deadline = constraint.value if isinstance(constraint.value, datetime) else None
        if deadline and slot.scheduled_end:
            if slot.scheduled_end > deadline:
                return False, ConstraintViolation(
                    constraint_id=constraint.id,
                    constraint_type=constraint.type,
                    slot_id=slot.id,
                    violation_type="sla_violation",
                    message=f"Slot completion exceeds SLA deadline",
                    severity="error" if constraint.is_hard else "warning",
                    can_reschedule=True,
                )

        return True, None

    def _check_concurrency_constraint(
        self,
        constraint: SchedulingConstraint,
        slot: ExecutionSlot,
        all_slots: List[ExecutionSlot],
    ) -> Tuple[bool, Optional[ConstraintViolation]]:
        """Check concurrency constraint."""
        max_concurrent = constraint.max_value or self.max_concurrent

        if not slot.scheduled_start:
            return True, None

        slot_end = slot.scheduled_end or (
            slot.scheduled_start + timedelta(seconds=slot.estimated_duration_seconds)
        )

        # Count overlapping slots
        concurrent = 0
        for s in all_slots:
            if s.id == slot.id:
                continue
            if not s.scheduled_start:
                continue

            s_end = s.scheduled_end or (
                s.scheduled_start + timedelta(seconds=s.estimated_duration_seconds)
            )

            # Check for overlap
            if s.scheduled_start < slot_end and s_end > slot.scheduled_start:
                concurrent += 1

        if concurrent >= max_concurrent:
            return False, ConstraintViolation(
                constraint_id=constraint.id,
                constraint_type=constraint.type,
                slot_id=slot.id,
                violation_type="concurrency_exceeded",
                message=f"Would exceed max concurrent ({max_concurrent})",
                can_reschedule=True,
            )

        return True, None

    def _check_dependency(
        self,
        dep: TemporalDependency,
        slot: ExecutionSlot,
        all_slots: List[ExecutionSlot],
    ) -> Tuple[bool, Optional[ConstraintViolation]]:
        """Check a temporal dependency."""
        # Find prerequisite slot
        prereq_slot = None
        for s in all_slots:
            if s.action_id == dep.prerequisite_action_id:
                prereq_slot = s
                break

        if not prereq_slot:
            return False, ConstraintViolation(
                constraint_id=dep.id,
                constraint_type=ConstraintType.DEPENDENCY,
                slot_id=slot.id,
                violation_type="missing_prerequisite",
                message=f"Prerequisite {dep.prerequisite_action_id} not found",
            )

        if not slot.scheduled_start or not prereq_slot.scheduled_start:
            return True, None

        prereq_end = prereq_slot.scheduled_end or (
            prereq_slot.scheduled_start +
            timedelta(seconds=prereq_slot.estimated_duration_seconds)
        )

        # Check min delay
        actual_delay = (slot.scheduled_start - prereq_end).total_seconds()
        if actual_delay < dep.min_delay_seconds:
            return False, ConstraintViolation(
                constraint_id=dep.id,
                constraint_type=ConstraintType.DEPENDENCY,
                slot_id=slot.id,
                violation_type="min_delay_violated",
                message=f"Need {dep.min_delay_seconds}s delay, only {actual_delay}s",
                can_reschedule=True,
            )

        # Check max delay
        if dep.max_delay_seconds and actual_delay > dep.max_delay_seconds:
            return False, ConstraintViolation(
                constraint_id=dep.id,
                constraint_type=ConstraintType.DEPENDENCY,
                slot_id=slot.id,
                violation_type="max_delay_exceeded",
                message=f"Max delay {dep.max_delay_seconds}s exceeded",
                can_reschedule=True,
            )

        return True, None

    def _check_concurrency(
        self,
        slot: ExecutionSlot,
        all_slots: List[ExecutionSlot],
    ) -> Tuple[bool, Optional[ConstraintViolation]]:
        """Check overall concurrency limit."""
        if not slot.scheduled_start:
            return True, None

        concurrent = sum(
            1 for s in all_slots
            if s.id != slot.id and s.status == ScheduleStatus.IN_PROGRESS
        )

        if concurrent >= self.max_concurrent:
            return False, ConstraintViolation(
                constraint_id="global_concurrency",
                constraint_type=ConstraintType.CONCURRENCY,
                slot_id=slot.id,
                violation_type="global_concurrency",
                message=f"Max concurrent actions ({self.max_concurrent}) reached",
                can_reschedule=True,
            )

        return True, None

    def _check_cooldown(
        self,
        slot: ExecutionSlot,
        all_slots: List[ExecutionSlot],
    ) -> Tuple[bool, Optional[ConstraintViolation]]:
        """Check global cooldown."""
        if not slot.scheduled_start:
            return True, None

        for s in all_slots:
            if s.id == slot.id or not s.scheduled_end:
                continue

            gap = (slot.scheduled_start - s.scheduled_end).total_seconds()
            if 0 < gap < self.default_cooldown:
                return False, ConstraintViolation(
                    constraint_id="global_cooldown",
                    constraint_type=ConstraintType.COOLDOWN,
                    slot_id=slot.id,
                    violation_type="global_cooldown",
                    message=f"Need {self.default_cooldown}s gap between actions",
                    can_reschedule=True,
                )

        return True, None

    def _suggest_adjustment(
        self,
        constraint: SchedulingConstraint,
        slot: ExecutionSlot,
        all_slots: List[ExecutionSlot],
        time_windows: List[TimeWindow],
    ) -> Optional[datetime]:
        """Suggest a time adjustment to satisfy constraint."""
        if not slot.scheduled_start:
            return None

        # For dependency violations, suggest after prerequisite
        if constraint.type == ConstraintType.DEPENDENCY:
            for s in all_slots:
                if s.action_id == constraint.target_id and s.scheduled_end:
                    return s.scheduled_end + timedelta(seconds=self.default_cooldown)

        # For cooldown violations, suggest after cooldown
        if constraint.type == ConstraintType.COOLDOWN:
            cooldown = constraint.cooldown_seconds or self.default_cooldown
            for s in all_slots:
                if s.id != slot.id and s.scheduled_end:
                    potential = s.scheduled_end + timedelta(seconds=cooldown)
                    if potential > slot.scheduled_start:
                        return potential

        return None


def create_constraint_resolver(
    max_concurrent_actions: int = 5,
    default_cooldown_seconds: int = 60,
    respect_sla: bool = True,
) -> ConstraintResolver:
    """Factory function to create a ConstraintResolver."""
    return ConstraintResolver(
        max_concurrent_actions=max_concurrent_actions,
        default_cooldown_seconds=default_cooldown_seconds,
        respect_sla=respect_sla,
    )
