"""
GREEN TURTLE - Time Analyzer.

Analyzes optimal execution times based on:
- Risk levels
- Time windows
- Historical patterns
- Current system state

This implements Criterion 1: Time window compliance.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, time as time_obj
from typing import Any, Dict, List, Optional, Tuple

import structlog

from .models import (
    TimeWindow,
    TimeWindowType,
    SchedulePriority,
    STANDARD_TIME_WINDOWS,
)

logger = structlog.get_logger(__name__)


# Risk level to preferred window mapping
RISK_WINDOW_MAPPING: Dict[str, List[TimeWindowType]] = {
    "CRITICAL": [TimeWindowType.EMERGENCY],
    "HIGH": [TimeWindowType.MAINTENANCE, TimeWindowType.OFF_PEAK],
    "MEDIUM": [TimeWindowType.OFF_PEAK, TimeWindowType.MAINTENANCE],
    "LOW": [TimeWindowType.BUSINESS_HOURS, TimeWindowType.OFF_PEAK],
    "NEGLIGIBLE": [TimeWindowType.BUSINESS_HOURS],
}

# Category to preferred window mapping
CATEGORY_WINDOW_MAPPING: Dict[str, List[TimeWindowType]] = {
    "database": [TimeWindowType.MAINTENANCE],
    "deployment": [TimeWindowType.MAINTENANCE, TimeWindowType.OFF_PEAK],
    "scaling": [TimeWindowType.BUSINESS_HOURS, TimeWindowType.OFF_PEAK],
    "restart": [TimeWindowType.MAINTENANCE, TimeWindowType.OFF_PEAK],
    "configuration": [TimeWindowType.MAINTENANCE],
    "network": [TimeWindowType.MAINTENANCE],
    "security": [TimeWindowType.MAINTENANCE],
    "monitoring": [TimeWindowType.BUSINESS_HOURS],
    "communication": [TimeWindowType.BUSINESS_HOURS],
    "investigation": [TimeWindowType.BUSINESS_HOURS],
}


@dataclass
class TimeSlot:
    """A potential time slot for execution."""
    start: datetime
    end: datetime
    window: TimeWindow
    score: float = 0.0
    reasons: List[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> int:
        return int((self.end - self.start).total_seconds())


@dataclass
class TimeAnalysisResult:
    """Result of time analysis."""
    recommended_slots: List[TimeSlot] = field(default_factory=list)
    earliest_possible: Optional[datetime] = None
    latest_deadline: Optional[datetime] = None
    preferred_window: Optional[TimeWindow] = None
    warnings: List[str] = field(default_factory=list)
    duration_ms: int = 0


class TimeAnalyzer:
    """
    Analyzes optimal execution times.

    Criterion 1: Actions must be scheduled within valid time windows.
    """

    def __init__(
        self,
        time_windows: Optional[Dict[str, TimeWindow]] = None,
        scheduling_horizon_hours: int = 24,
        prefer_off_peak: bool = True,
    ):
        """
        Initialize the time analyzer.

        Args:
            time_windows: Available time windows
            scheduling_horizon_hours: How far ahead to look
            prefer_off_peak: Prefer off-peak windows
        """
        self.time_windows = time_windows or STANDARD_TIME_WINDOWS
        self.scheduling_horizon = timedelta(hours=scheduling_horizon_hours)
        self.prefer_off_peak = prefer_off_peak

        logger.info(
            "time_analyzer_initialized",
            window_count=len(self.time_windows),
            horizon_hours=scheduling_horizon_hours,
        )

    def analyze(
        self,
        action_id: str,
        estimated_duration_seconds: int,
        risk_level: str = "MEDIUM",
        category: str = "investigation",
        priority: SchedulePriority = SchedulePriority.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
    ) -> TimeAnalysisResult:
        """
        Analyze optimal execution time for an action.

        Args:
            action_id: Action identifier
            estimated_duration_seconds: How long the action takes
            risk_level: Risk level (CRITICAL, HIGH, MEDIUM, LOW, NEGLIGIBLE)
            category: Action category
            priority: Scheduling priority
            context: Additional context

        Returns:
            TimeAnalysisResult with recommended slots
        """
        import time
        start_time = time.time()
        context = context or {}
        warnings: List[str] = []

        now = datetime.utcnow()
        horizon_end = now + self.scheduling_horizon

        # Find applicable windows
        applicable_windows = self._find_applicable_windows(
            risk_level, category, priority
        )

        if not applicable_windows:
            warnings.append("No applicable time windows found, using emergency window")
            applicable_windows = [self.time_windows.get("emergency", STANDARD_TIME_WINDOWS["emergency"])]

        # Generate candidate slots
        candidate_slots: List[TimeSlot] = []
        for window in applicable_windows:
            slots = self._generate_slots_in_window(
                window, now, horizon_end, estimated_duration_seconds
            )
            candidate_slots.extend(slots)

        # Score and rank slots
        scored_slots = self._score_slots(
            candidate_slots, risk_level, category, priority, context
        )

        # Sort by score (highest first)
        scored_slots.sort(key=lambda s: s.score, reverse=True)

        # Determine earliest and latest
        earliest = min(s.start for s in scored_slots) if scored_slots else now
        latest = max(s.end for s in scored_slots) if scored_slots else horizon_end

        # Get preferred window
        preferred = applicable_windows[0] if applicable_windows else None

        duration_ms = int((time.time() - start_time) * 1000)

        logger.debug(
            "time_analysis_complete",
            action_id=action_id,
            candidate_slots=len(scored_slots),
            preferred_window=preferred.name if preferred else None,
            duration_ms=duration_ms,
        )

        return TimeAnalysisResult(
            recommended_slots=scored_slots[:5],  # Top 5 slots
            earliest_possible=earliest,
            latest_deadline=latest,
            preferred_window=preferred,
            warnings=warnings,
            duration_ms=duration_ms,
        )

    def _find_applicable_windows(
        self,
        risk_level: str,
        category: str,
        priority: SchedulePriority,
    ) -> List[TimeWindow]:
        """Find windows applicable for the given parameters."""
        windows: List[TimeWindow] = []

        # Emergency priority can use any window
        if priority == SchedulePriority.CRITICAL:
            if "emergency" in self.time_windows:
                windows.append(self.time_windows["emergency"])
            return windows

        # Get windows by risk level
        risk_types = RISK_WINDOW_MAPPING.get(risk_level, [TimeWindowType.OFF_PEAK])

        # Get windows by category
        category_types = CATEGORY_WINDOW_MAPPING.get(
            category.lower(),
            [TimeWindowType.OFF_PEAK]
        )

        # Find intersection
        preferred_types = set(risk_types) & set(category_types)
        if not preferred_types:
            preferred_types = set(risk_types)

        # Get actual windows
        for window in self.time_windows.values():
            if window.type in preferred_types:
                windows.append(window)

        # Fall back to off-peak if nothing found
        if not windows and "off_peak" in self.time_windows:
            windows.append(self.time_windows["off_peak"])

        return windows

    def _generate_slots_in_window(
        self,
        window: TimeWindow,
        start: datetime,
        end: datetime,
        duration_seconds: int,
    ) -> List[TimeSlot]:
        """Generate potential slots within a window."""
        slots: List[TimeSlot] = []
        current = start
        duration = timedelta(seconds=duration_seconds)

        # Step through time in 15-minute increments
        step = timedelta(minutes=15)

        while current + duration <= end:
            if window.contains(current) and window.contains(current + duration):
                slots.append(TimeSlot(
                    start=current,
                    end=current + duration,
                    window=window,
                ))
            current += step

        return slots

    def _score_slots(
        self,
        slots: List[TimeSlot],
        risk_level: str,
        category: str,
        priority: SchedulePriority,
        context: Dict[str, Any],
    ) -> List[TimeSlot]:
        """Score slots based on various factors."""
        now = datetime.utcnow()

        for slot in slots:
            score = 100.0
            reasons: List[str] = []

            # Factor 1: Window preference
            if slot.window.is_preferred:
                score += 20
                reasons.append("Preferred window")
            else:
                score -= 10

            # Factor 2: Risk multiplier (lower = better)
            risk_adjustment = (1.0 - slot.window.risk_multiplier) * 30
            score += risk_adjustment
            if slot.window.risk_multiplier < 1.0:
                reasons.append(f"Low risk window ({slot.window.risk_multiplier})")

            # Factor 3: Time until slot (sooner better for high priority)
            hours_until = (slot.start - now).total_seconds() / 3600
            if priority in [SchedulePriority.CRITICAL, SchedulePriority.HIGH]:
                # Prefer sooner slots
                score -= hours_until * 2
                if hours_until < 1:
                    reasons.append("Executes within 1 hour")
            else:
                # Slight preference for not-too-soon
                if 2 <= hours_until <= 8:
                    score += 10
                    reasons.append("Good lead time")

            # Factor 4: Off-peak bonus
            if self.prefer_off_peak and slot.window.type == TimeWindowType.OFF_PEAK:
                score += 15
                reasons.append("Off-peak hours")

            # Factor 5: Maintenance window bonus for risky operations
            if risk_level in ["HIGH", "CRITICAL"]:
                if slot.window.type == TimeWindowType.MAINTENANCE:
                    score += 25
                    reasons.append("Maintenance window for high-risk action")

            # Factor 6: Business hours penalty for disruptive actions
            if category in ["restart", "deployment", "database"]:
                if slot.window.type == TimeWindowType.BUSINESS_HOURS:
                    score -= 20
                    reasons.append("Business hours penalty for disruptive action")

            slot.score = max(0, score)
            slot.reasons = reasons

        return slots

    def get_next_window(
        self,
        window_type: TimeWindowType,
        after: Optional[datetime] = None,
    ) -> Optional[Tuple[datetime, datetime]]:
        """Get the next occurrence of a window type."""
        after = after or datetime.utcnow()

        for window in self.time_windows.values():
            if window.type == window_type:
                # Find next occurrence
                return self._find_next_occurrence(window, after)

        return None

    def _find_next_occurrence(
        self,
        window: TimeWindow,
        after: datetime,
    ) -> Optional[Tuple[datetime, datetime]]:
        """Find the next occurrence of a window."""
        current = after

        # Look up to 7 days ahead
        for _ in range(7 * 24):  # Check every hour for a week
            if window.contains(current):
                # Find when this window ends
                end = self._find_window_end(window, current)
                return (current, end)
            current += timedelta(hours=1)

        return None

    def _find_window_end(
        self,
        window: TimeWindow,
        start: datetime,
    ) -> datetime:
        """Find when a window ends."""
        current = start
        max_duration = timedelta(hours=12)

        while current - start < max_duration:
            current += timedelta(minutes=15)
            if not window.contains(current):
                return current

        return start + max_duration

    def is_within_window(
        self,
        dt: datetime,
        window_types: Optional[List[TimeWindowType]] = None,
    ) -> Tuple[bool, Optional[TimeWindow]]:
        """Check if datetime is within any specified window."""
        for window in self.time_windows.values():
            if window_types and window.type not in window_types:
                continue
            if window.contains(dt):
                return True, window
        return False, None


def create_time_analyzer(
    time_windows: Optional[Dict[str, TimeWindow]] = None,
    scheduling_horizon_hours: int = 24,
    prefer_off_peak: bool = True,
) -> TimeAnalyzer:
    """Factory function to create a TimeAnalyzer."""
    return TimeAnalyzer(
        time_windows=time_windows,
        scheduling_horizon_hours=scheduling_horizon_hours,
        prefer_off_peak=prefer_off_peak,
    )
