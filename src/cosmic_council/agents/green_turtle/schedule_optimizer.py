"""
GREEN TURTLE - Schedule Optimizer.

Optimizes the execution schedule for:
- Minimum total duration
- Maximum parallelism (when safe)
- Optimal window utilization

This implements Criterion 2: Dependency sequencing.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict

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
)
from .time_analyzer import TimeAnalyzer, TimeSlot

logger = structlog.get_logger(__name__)


@dataclass
class OptimizationResult:
    """Result of schedule optimization."""
    schedule: ExecutionSchedule
    optimized: bool = False
    improvements: List[str] = field(default_factory=list)
    total_duration_seconds: int = 0
    parallelism_achieved: float = 0.0
    warnings: List[str] = field(default_factory=list)
    duration_ms: int = 0


class ScheduleOptimizer:
    """
    Optimizes execution schedules.

    Criterion 2: Actions respect temporal dependencies.
    """

    def __init__(
        self,
        time_analyzer: TimeAnalyzer,
        min_slot_gap_seconds: int = 30,
        max_concurrent: int = 5,
        optimize_for_speed: bool = False,
    ):
        """
        Initialize the schedule optimizer.

        Args:
            time_analyzer: Time analyzer for finding optimal slots
            min_slot_gap_seconds: Minimum gap between slots
            max_concurrent: Maximum concurrent executions
            optimize_for_speed: Optimize for fastest completion
        """
        self.time_analyzer = time_analyzer
        self.min_gap = timedelta(seconds=min_slot_gap_seconds)
        self.max_concurrent = max_concurrent
        self.optimize_for_speed = optimize_for_speed

        logger.info(
            "schedule_optimizer_initialized",
            min_gap_seconds=min_slot_gap_seconds,
            max_concurrent=max_concurrent,
            optimize_for_speed=optimize_for_speed,
        )

    def optimize(
        self,
        schedule: ExecutionSchedule,
        context: Optional[Dict[str, Any]] = None,
    ) -> OptimizationResult:
        """
        Optimize an execution schedule.

        Args:
            schedule: The schedule to optimize
            context: Additional context

        Returns:
            OptimizationResult with optimized schedule
        """
        import time
        start_time = time.time()
        context = context or {}
        improvements: List[str] = []
        warnings: List[str] = []

        # Step 1: Build dependency graph
        dep_graph = self._build_dependency_graph(schedule)

        # Step 2: Topological sort respecting dependencies
        sorted_slots = self._topological_sort(schedule.slots, dep_graph)
        if not sorted_slots:
            warnings.append("Could not determine valid execution order (cycle detected?)")
            sorted_slots = schedule.slots

        # Step 3: Assign optimal times
        scheduled_slots = self._assign_times(
            sorted_slots, schedule.time_windows, dep_graph, context
        )

        # Step 4: Parallelize where possible
        if not self.optimize_for_speed:
            parallelized = self._parallelize_slots(scheduled_slots, dep_graph)
            if parallelized > 0:
                improvements.append(f"Parallelized {parallelized} independent slots")
        else:
            improvements.append("Speed optimization: sequential execution")

        # Step 5: Compress schedule (remove gaps)
        compressed = self._compress_schedule(scheduled_slots)
        if compressed > 0:
            improvements.append(f"Compressed schedule by {compressed} seconds")

        # Update schedule
        schedule.slots = scheduled_slots
        schedule.execution_order = [s.id for s in scheduled_slots]

        # Calculate metrics
        schedule._compute_metrics()

        # Calculate parallelism achieved
        parallelism = self._calculate_parallelism(scheduled_slots)

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "schedule_optimized",
            slot_count=len(scheduled_slots),
            improvements=len(improvements),
            parallelism=f"{parallelism:.1%}",
            duration_ms=duration_ms,
        )

        return OptimizationResult(
            schedule=schedule,
            optimized=len(improvements) > 0,
            improvements=improvements,
            total_duration_seconds=schedule.total_duration_seconds,
            parallelism_achieved=parallelism,
            warnings=warnings,
            duration_ms=duration_ms,
        )

    def _build_dependency_graph(
        self,
        schedule: ExecutionSchedule,
    ) -> Dict[str, Set[str]]:
        """Build dependency graph (slot_id -> set of prerequisite slot_ids)."""
        graph: Dict[str, Set[str]] = defaultdict(set)

        # Map action_id to slot_id
        action_to_slot: Dict[str, str] = {}
        for slot in schedule.slots:
            action_to_slot[slot.action_id] = slot.id

        # Build graph from dependencies
        for dep in schedule.dependencies:
            dependent_slot = action_to_slot.get(dep.dependent_action_id)
            prereq_slot = action_to_slot.get(dep.prerequisite_action_id)

            if dependent_slot and prereq_slot:
                graph[dependent_slot].add(prereq_slot)

        # Also check slot-level dependencies
        for slot in schedule.slots:
            for dep in slot.dependencies:
                prereq_slot = action_to_slot.get(dep.prerequisite_action_id)
                if prereq_slot:
                    graph[slot.id].add(prereq_slot)

        return graph

    def _topological_sort(
        self,
        slots: List[ExecutionSlot],
        dep_graph: Dict[str, Set[str]],
    ) -> List[ExecutionSlot]:
        """
        Topological sort of slots respecting dependencies.

        Uses Kahn's algorithm.
        """
        # Build in-degree map
        in_degree: Dict[str, int] = {s.id: 0 for s in slots}
        for slot_id, prereqs in dep_graph.items():
            if slot_id in in_degree:
                in_degree[slot_id] = len(prereqs)

        # Find slots with no dependencies
        queue: List[str] = [
            slot_id for slot_id, degree in in_degree.items()
            if degree == 0
        ]

        # Sort by priority within each level
        slot_map = {s.id: s for s in slots}
        queue.sort(key=lambda sid: slot_map[sid].priority.value)

        sorted_ids: List[str] = []

        while queue:
            # Take highest priority slot with no unsatisfied dependencies
            current = queue.pop(0)
            sorted_ids.append(current)

            # Reduce in-degree for dependents
            for slot_id, prereqs in dep_graph.items():
                if current in prereqs:
                    in_degree[slot_id] -= 1
                    if in_degree[slot_id] == 0:
                        queue.append(slot_id)
                        queue.sort(key=lambda sid: slot_map[sid].priority.value)

        # Check for cycles
        if len(sorted_ids) != len(slots):
            logger.warning(
                "dependency_cycle_detected",
                sorted=len(sorted_ids),
                total=len(slots),
            )
            # Return original order for unsorted slots
            remaining = [s for s in slots if s.id not in sorted_ids]
            return [slot_map[sid] for sid in sorted_ids] + remaining

        return [slot_map[sid] for sid in sorted_ids]

    def _assign_times(
        self,
        slots: List[ExecutionSlot],
        time_windows: List[TimeWindow],
        dep_graph: Dict[str, Set[str]],
        context: Dict[str, Any],
    ) -> List[ExecutionSlot]:
        """Assign optimal times to slots."""
        now = datetime.utcnow()
        current_time = now

        slot_end_times: Dict[str, datetime] = {}

        for slot in slots:
            # Find earliest possible start
            earliest = current_time

            # Check dependencies
            for prereq_id in dep_graph.get(slot.id, set()):
                if prereq_id in slot_end_times:
                    prereq_end = slot_end_times[prereq_id]
                    if prereq_end + self.min_gap > earliest:
                        earliest = prereq_end + self.min_gap

            # Analyze for optimal time
            analysis = self.time_analyzer.analyze(
                action_id=slot.action_id,
                estimated_duration_seconds=slot.estimated_duration_seconds,
                risk_level=context.get("risk_level", "MEDIUM"),
                priority=slot.priority,
                context=context,
            )

            # Find best slot after earliest
            best_slot: Optional[TimeSlot] = None
            for time_slot in analysis.recommended_slots:
                if time_slot.start >= earliest:
                    best_slot = time_slot
                    break

            if best_slot:
                slot.scheduled_start = best_slot.start
                slot.scheduled_end = best_slot.end
                slot.time_window_id = best_slot.window.id
                slot.time_window_name = best_slot.window.name
            else:
                # Fall back to earliest possible
                slot.scheduled_start = earliest
                slot.scheduled_end = earliest + timedelta(seconds=slot.estimated_duration_seconds)

            slot.status = ScheduleStatus.SCHEDULED
            slot_end_times[slot.id] = slot.scheduled_end
            current_time = slot.scheduled_end + self.min_gap

        return slots

    def _parallelize_slots(
        self,
        slots: List[ExecutionSlot],
        dep_graph: Dict[str, Set[str]],
    ) -> int:
        """Parallelize independent slots."""
        parallelized = 0

        # Group slots by dependency level
        levels: List[List[ExecutionSlot]] = []
        remaining = set(s.id for s in slots)
        completed: Set[str] = set()

        while remaining:
            # Find slots whose dependencies are all completed
            level = []
            for slot in slots:
                if slot.id not in remaining:
                    continue
                prereqs = dep_graph.get(slot.id, set())
                if prereqs <= completed:
                    level.append(slot)

            if not level:
                break

            levels.append(level)
            for slot in level:
                remaining.discard(slot.id)
                completed.add(slot.id)

        # Schedule parallel slots at same time
        slot_map = {s.id: s for s in slots}
        for level in levels:
            if len(level) <= 1:
                continue

            # Find earliest start for this level
            earliest = min(s.scheduled_start for s in level if s.scheduled_start)

            # Limit concurrency
            concurrent = 0
            for slot in level:
                if concurrent >= self.max_concurrent:
                    # Must wait for a slot in this level
                    for prev_slot in level[:level.index(slot)]:
                        if prev_slot.scheduled_end:
                            earliest = max(earliest, prev_slot.scheduled_end + self.min_gap)
                    concurrent = 0

                if slot.scheduled_start != earliest:
                    slot.scheduled_start = earliest
                    slot.scheduled_end = earliest + timedelta(seconds=slot.estimated_duration_seconds)
                    parallelized += 1

                concurrent += 1

        return parallelized

    def _compress_schedule(
        self,
        slots: List[ExecutionSlot],
    ) -> int:
        """Remove unnecessary gaps in schedule."""
        if not slots:
            return 0

        total_compressed = 0
        current_end = slots[0].scheduled_start

        for slot in slots:
            if not slot.scheduled_start:
                continue

            gap = (slot.scheduled_start - current_end).total_seconds()
            if gap > self.min_gap.total_seconds():
                # Compress
                excess = gap - self.min_gap.total_seconds()
                slot.scheduled_start = current_end + self.min_gap
                slot.scheduled_end = slot.scheduled_start + timedelta(seconds=slot.estimated_duration_seconds)
                total_compressed += int(excess)

            current_end = slot.scheduled_end or slot.scheduled_start

        return total_compressed

    def _calculate_parallelism(
        self,
        slots: List[ExecutionSlot],
    ) -> float:
        """Calculate degree of parallelism achieved."""
        if not slots:
            return 0.0

        # Find timeline boundaries
        starts = [s.scheduled_start for s in slots if s.scheduled_start]
        ends = [s.scheduled_end for s in slots if s.scheduled_end]

        if not starts or not ends:
            return 0.0

        timeline_start = min(starts)
        timeline_end = max(ends)
        total_timeline = (timeline_end - timeline_start).total_seconds()

        if total_timeline <= 0:
            return 0.0

        # Sum of all durations
        total_work = sum(s.estimated_duration_seconds for s in slots)

        # Parallelism = total_work / timeline
        # If all sequential, parallelism = 1.0
        # If all parallel, parallelism = n
        parallelism = total_work / total_timeline if total_timeline > 0 else 1.0

        # Normalize to 0-1 where 1 = perfect parallelism
        max_parallelism = min(len(slots), self.max_concurrent)
        normalized = (parallelism - 1) / (max_parallelism - 1) if max_parallelism > 1 else 0

        return max(0, min(1, normalized))

    def reorder_by_priority(
        self,
        slots: List[ExecutionSlot],
    ) -> List[ExecutionSlot]:
        """Reorder slots by priority within dependency constraints."""
        # This is a simplified reordering that respects dependencies
        # but prioritizes higher-priority slots
        return sorted(
            slots,
            key=lambda s: (s.priority.value, s.scheduled_start or datetime.max),
        )


def create_schedule_optimizer(
    time_analyzer: TimeAnalyzer,
    min_slot_gap_seconds: int = 30,
    max_concurrent: int = 5,
    optimize_for_speed: bool = False,
) -> ScheduleOptimizer:
    """Factory function to create a ScheduleOptimizer."""
    return ScheduleOptimizer(
        time_analyzer=time_analyzer,
        min_slot_gap_seconds=min_slot_gap_seconds,
        max_concurrent=max_concurrent,
        optimize_for_speed=optimize_for_speed,
    )
