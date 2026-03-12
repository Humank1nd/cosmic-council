"""
GREEN TURTLE - Scheduling Engine.

Main engine that orchestrates:
- Time analysis (Criterion 1)
- Dependency sequencing (Criterion 2)
- Constraint satisfaction (Criterion 3)

Takes implementation specs from Yellow Honeybee and produces
execution schedules.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog

from .models import (
    ExecutionSlot,
    ExecutionSchedule,
    ScheduleStatus,
    SchedulePriority,
    TemporalDependency,
    SchedulingConstraint,
    ConstraintType,
    TimeWindow,
    GreenTurtleConfig,
    STANDARD_TIME_WINDOWS,
)
from .time_analyzer import (
    TimeAnalyzer,
    create_time_analyzer,
)
from .constraint_resolver import (
    ConstraintResolver,
    create_constraint_resolver,
)
from .schedule_optimizer import (
    ScheduleOptimizer,
    create_schedule_optimizer,
)

logger = structlog.get_logger(__name__)


@dataclass
class GreenTurtleResult:
    """Result of Green Turtle scheduling."""
    success: bool
    schedule: ExecutionSchedule
    reasoning: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None
    duration_ms: int = 0

    # Criterion metrics
    time_window_compliance: float = 0.0
    dependency_sequencing: float = 0.0
    constraint_satisfaction: float = 0.0


class GreenTurtleEngine:
    """
    Green Turtle Scheduling Engine.

    Answers the WHEN question: When should each action execute?

    Three Falsifiable Criteria:
    1. Time window compliance - actions within valid windows
    2. Dependency sequencing - actions respect temporal dependencies
    3. Constraint satisfaction - all constraints are met
    """

    def __init__(
        self,
        config: Optional[GreenTurtleConfig] = None,
        llm_provider: Optional[Any] = None,
        time_windows: Optional[Dict[str, TimeWindow]] = None,
    ):
        """
        Initialize the Green Turtle engine.

        Args:
            config: Engine configuration
            llm_provider: Optional LLM provider
            time_windows: Custom time windows
        """
        self.config = config or GreenTurtleConfig()
        self.llm_provider = llm_provider
        self.time_windows = time_windows or STANDARD_TIME_WINDOWS

        # Initialize components
        self.time_analyzer = create_time_analyzer(
            time_windows=self.time_windows,
            scheduling_horizon_hours=self.config.scheduling_horizon_hours,
            prefer_off_peak=self.config.prefer_off_peak,
        )
        self.constraint_resolver = create_constraint_resolver(
            max_concurrent_actions=self.config.max_concurrent_actions,
            default_cooldown_seconds=self.config.default_cooldown_seconds,
            respect_sla=self.config.respect_sla_constraints,
        )
        self.optimizer = create_schedule_optimizer(
            time_analyzer=self.time_analyzer,
            min_slot_gap_seconds=self.config.min_slot_gap_seconds,
            max_concurrent=self.config.max_concurrent_actions,
            optimize_for_speed=self.config.optimize_for_speed,
        )

        logger.info(
            "green_turtle_engine_initialized",
            has_llm=llm_provider is not None,
            window_count=len(self.time_windows),
        )

    async def schedule(
        self,
        implementation_plan_id: str,
        specifications: List[Dict[str, Any]],
        dependencies: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> GreenTurtleResult:
        """
        Create an execution schedule for specifications.

        Args:
            implementation_plan_id: ID of source implementation plan
            specifications: Specs from Yellow Honeybee
            dependencies: Temporal dependencies between specs
            context: Additional context

        Returns:
            GreenTurtleResult with execution schedule
        """
        start_time = time.time()
        context = context or {}
        dependencies = dependencies or []
        reasoning: List[str] = []
        warnings: List[str] = []

        try:
            reasoning.append(f"Scheduling {len(specifications)} specifications")

            # Step 1: Create execution slots from specs
            slots = self._create_slots(specifications, context)
            reasoning.append(f"Created {len(slots)} execution slots")

            # Step 2: Create temporal dependencies
            temporal_deps = self._create_dependencies(dependencies, specifications)
            reasoning.append(f"Identified {len(temporal_deps)} dependencies")

            # Step 3: Create constraints
            constraints = self._create_constraints(slots, context)
            reasoning.append(f"Created {len(constraints)} scheduling constraints")

            # Step 4: Analyze optimal times (Criterion 1)
            for slot in slots:
                analysis = self.time_analyzer.analyze(
                    action_id=slot.action_id,
                    estimated_duration_seconds=slot.estimated_duration_seconds,
                    risk_level=context.get("risk_level", "MEDIUM"),
                    category=context.get("category", "investigation"),
                    priority=slot.priority,
                    context=context,
                )
                if analysis.recommended_slots:
                    best = analysis.recommended_slots[0]
                    slot.scheduled_start = best.start
                    slot.scheduled_end = best.end
                    slot.time_window_id = best.window.id
                    slot.time_window_name = best.window.name
                    slot.status = ScheduleStatus.SCHEDULED
                warnings.extend(analysis.warnings)

            # Step 5: Create initial schedule
            schedule = ExecutionSchedule(
                implementation_plan_id=implementation_plan_id,
                slots=slots,
                execution_order=[s.id for s in slots],
                time_windows=list(self.time_windows.values()),
                all_constraints=constraints,
                dependencies=temporal_deps,
            )

            # Step 6: Optimize schedule (Criterion 2)
            opt_result = self.optimizer.optimize(schedule, context)
            schedule = opt_result.schedule
            reasoning.extend(opt_result.improvements)
            warnings.extend(opt_result.warnings)

            # Step 7: Resolve constraints (Criterion 3)
            for slot in schedule.slots:
                slot.constraints = [c for c in constraints if c.target_id == slot.id]
                slot.dependencies = [d for d in temporal_deps if d.dependent_action_id == slot.action_id]

                resolution = self.constraint_resolver.resolve(
                    slot, schedule.slots, schedule.time_windows, context
                )
                if not resolution.is_satisfied:
                    for violation in resolution.violations:
                        warnings.append(f"{slot.action_id}: {violation.message}")

            # Step 8: Validate schedule
            is_valid, validation_errors = self._validate_schedule(schedule)
            schedule.is_valid = is_valid
            schedule.validation_errors = validation_errors

            if not is_valid:
                warnings.extend(validation_errors)

            # Calculate criterion metrics
            time_compliance = self._calculate_time_compliance(schedule)
            dep_sequencing = self._calculate_dependency_sequencing(schedule)
            constraint_sat = self._calculate_constraint_satisfaction(schedule)

            reasoning.append(
                f"Criteria: time={time_compliance:.1%}, "
                f"deps={dep_sequencing:.1%}, "
                f"constraints={constraint_sat:.1%}"
            )

            duration_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "green_turtle_scheduling_complete",
                schedule_id=schedule.id,
                slot_count=len(slots),
                is_valid=is_valid,
                duration_ms=duration_ms,
            )

            return GreenTurtleResult(
                success=True,
                schedule=schedule,
                reasoning=reasoning,
                warnings=warnings,
                duration_ms=duration_ms,
                time_window_compliance=time_compliance,
                dependency_sequencing=dep_sequencing,
                constraint_satisfaction=constraint_sat,
            )

        except Exception as e:
            logger.error("green_turtle_scheduling_failed", error=str(e))
            return GreenTurtleResult(
                success=False,
                schedule=ExecutionSchedule(),
                reasoning=reasoning,
                warnings=warnings,
                error=str(e),
                duration_ms=int((time.time() - start_time) * 1000),
            )

    def _create_slots(
        self,
        specifications: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[ExecutionSlot]:
        """Create execution slots from specifications."""
        slots: List[ExecutionSlot] = []

        for spec in specifications:
            # Determine priority
            risk = spec.get("risk_level", "MEDIUM")
            if risk == "CRITICAL":
                priority = SchedulePriority.CRITICAL
            elif risk == "HIGH":
                priority = SchedulePriority.HIGH
            elif risk == "LOW":
                priority = SchedulePriority.LOW
            else:
                priority = SchedulePriority.MEDIUM

            slot = ExecutionSlot(
                action_id=spec.get("action_id", spec.get("id", "")),
                spec_id=spec.get("id", ""),
                estimated_duration_seconds=spec.get("estimated_duration_seconds", 60),
                priority=priority,
                status=ScheduleStatus.PENDING,
                metadata={
                    "action_title": spec.get("action_title", ""),
                    "spec_type": spec.get("spec_type", ""),
                },
            )
            slots.append(slot)

        return slots

    def _create_dependencies(
        self,
        dependencies: List[Dict[str, Any]],
        specifications: List[Dict[str, Any]],
    ) -> List[TemporalDependency]:
        """Create temporal dependencies."""
        temporal_deps: List[TemporalDependency] = []

        # From explicit dependencies
        for dep in dependencies:
            temporal_deps.append(TemporalDependency(
                dependent_action_id=dep.get("dependent_id", ""),
                prerequisite_action_id=dep.get("prerequisite_id", ""),
                min_delay_seconds=dep.get("min_delay", 0),
                max_delay_seconds=dep.get("max_delay"),
            ))

        # Infer from specification order (if execution_order provided)
        spec_order = [s.get("action_id", s.get("id")) for s in specifications]
        for i in range(1, len(spec_order)):
            # Each spec depends on the previous one by default
            temporal_deps.append(TemporalDependency(
                dependent_action_id=spec_order[i],
                prerequisite_action_id=spec_order[i-1],
                min_delay_seconds=0,
            ))

        return temporal_deps

    def _create_constraints(
        self,
        slots: List[ExecutionSlot],
        context: Dict[str, Any],
    ) -> List[SchedulingConstraint]:
        """Create scheduling constraints."""
        constraints: List[SchedulingConstraint] = []

        # Concurrency constraint
        constraints.append(SchedulingConstraint(
            type=ConstraintType.CONCURRENCY,
            name="max_concurrency",
            description=f"Max {self.config.max_concurrent_actions} concurrent actions",
            max_value=self.config.max_concurrent_actions,
            is_hard=True,
        ))

        # Cooldown constraint
        constraints.append(SchedulingConstraint(
            type=ConstraintType.COOLDOWN,
            name="default_cooldown",
            description=f"Min {self.config.default_cooldown_seconds}s between actions",
            cooldown_seconds=self.config.default_cooldown_seconds,
            is_hard=False,
        ))

        # Per-slot constraints
        for slot in slots:
            # Time window constraint
            constraints.append(SchedulingConstraint(
                type=ConstraintType.TIME_WINDOW,
                name=f"window_{slot.id}",
                description=f"Time window for {slot.action_id}",
                target_id=slot.id,
                is_hard=slot.priority != SchedulePriority.CRITICAL,
            ))

        return constraints

    def _validate_schedule(
        self,
        schedule: ExecutionSchedule,
    ) -> tuple[bool, List[str]]:
        """Validate the complete schedule."""
        errors: List[str] = []

        # Check all slots are scheduled
        unscheduled = [
            s for s in schedule.slots
            if s.status == ScheduleStatus.PENDING or not s.scheduled_start
        ]
        if unscheduled:
            errors.append(f"{len(unscheduled)} slots are not scheduled")

        # Check no overlapping with concurrency limit
        for i, slot1 in enumerate(schedule.slots):
            if not slot1.scheduled_start:
                continue
            concurrent = 0
            for slot2 in schedule.slots:
                if slot2.id == slot1.id or not slot2.scheduled_start:
                    continue
                # Check overlap
                s2_end = slot2.scheduled_end or (
                    slot2.scheduled_start + timedelta(seconds=slot2.estimated_duration_seconds)
                )
                s1_end = slot1.scheduled_end or (
                    slot1.scheduled_start + timedelta(seconds=slot1.estimated_duration_seconds)
                )
                if slot2.scheduled_start < s1_end and s2_end > slot1.scheduled_start:
                    concurrent += 1
            if concurrent >= self.config.max_concurrent_actions:
                errors.append(f"Slot {slot1.id} exceeds concurrency limit")

        # Check dependencies satisfied
        for dep in schedule.dependencies:
            dep_slot = None
            prereq_slot = None
            for s in schedule.slots:
                if s.action_id == dep.dependent_action_id:
                    dep_slot = s
                if s.action_id == dep.prerequisite_action_id:
                    prereq_slot = s

            if dep_slot and prereq_slot:
                if dep_slot.scheduled_start and prereq_slot.scheduled_end:
                    if dep_slot.scheduled_start < prereq_slot.scheduled_end:
                        errors.append(
                            f"Dependency violated: {dep.dependent_action_id} "
                            f"before {dep.prerequisite_action_id}"
                        )

        return len(errors) == 0, errors

    def _calculate_time_compliance(self, schedule: ExecutionSchedule) -> float:
        """Calculate time window compliance ratio."""
        if not schedule.slots:
            return 0.0

        compliant = 0
        for slot in schedule.slots:
            if slot.time_window_id:
                compliant += 1
            elif slot.status == ScheduleStatus.SCHEDULED:
                # Scheduled but no specific window
                compliant += 0.5

        return compliant / len(schedule.slots)

    def _calculate_dependency_sequencing(self, schedule: ExecutionSchedule) -> float:
        """Calculate dependency sequencing accuracy."""
        if not schedule.dependencies:
            return 1.0  # No dependencies to violate

        satisfied = sum(1 for d in schedule.dependencies if d.is_satisfied)
        return satisfied / len(schedule.dependencies)

    def _calculate_constraint_satisfaction(self, schedule: ExecutionSchedule) -> float:
        """Calculate constraint satisfaction ratio."""
        if not schedule.all_constraints:
            return 1.0

        satisfied = sum(1 for c in schedule.all_constraints if c.is_satisfied)
        return satisfied / len(schedule.all_constraints)

    async def quick_schedule(
        self,
        specifications: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Quick scheduling returning essentials."""
        result = await self.schedule(
            implementation_plan_id="quick",
            specifications=specifications,
            context=context,
        )

        return {
            "success": result.success,
            "slot_count": len(result.schedule.slots),
            "scheduled_count": result.schedule.slots_scheduled,
            "earliest_start": result.schedule.earliest_start.isoformat() if result.schedule.earliest_start else None,
            "latest_end": result.schedule.latest_end.isoformat() if result.schedule.latest_end else None,
            "total_duration_seconds": result.schedule.total_duration_seconds,
            "is_valid": result.schedule.is_valid,
            "duration_ms": result.duration_ms,
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get engine metrics."""
        return {
            "config": {
                "scheduling_horizon_hours": self.config.scheduling_horizon_hours,
                "max_concurrent_actions": self.config.max_concurrent_actions,
                "default_cooldown_seconds": self.config.default_cooldown_seconds,
                "prefer_off_peak": self.config.prefer_off_peak,
                "optimize_for_speed": self.config.optimize_for_speed,
            },
            "capabilities": {
                "has_llm": self.llm_provider is not None,
                "respect_sla": self.config.respect_sla_constraints,
                "batch_similar": self.config.batch_similar_actions,
            },
            "time_windows": list(self.time_windows.keys()),
        }


# Singleton instance
_engine: Optional[GreenTurtleEngine] = None


def create_green_turtle(
    config: Optional[GreenTurtleConfig] = None,
    llm_provider: Optional[Any] = None,
    time_windows: Optional[Dict[str, TimeWindow]] = None,
) -> GreenTurtleEngine:
    """Create a Green Turtle engine instance."""
    return GreenTurtleEngine(
        config=config,
        llm_provider=llm_provider,
        time_windows=time_windows,
    )


def get_green_turtle() -> GreenTurtleEngine:
    """Get the default Green Turtle engine instance."""
    global _engine
    if _engine is None:
        _engine = create_green_turtle()
    return _engine


async def schedule_execution(
    specifications: List[Dict[str, Any]],
    implementation_plan_id: str = "",
    dependencies: Optional[List[Dict[str, Any]]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> GreenTurtleResult:
    """Convenience function for quick scheduling."""
    engine = get_green_turtle()
    return await engine.schedule(
        implementation_plan_id=implementation_plan_id,
        specifications=specifications,
        dependencies=dependencies,
        context=context,
    )
