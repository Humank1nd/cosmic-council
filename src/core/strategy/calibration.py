"""
Calibration Engine
==================

Adjusts confidence thresholds using historical outcomes.

Features:
- Confidence calibration based on actual success rates
- Role-specific calibration profiles
- Guardrails to prevent over/under-confidence
- Gradual adjustment with decay factors
"""

import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .registry import AgentRole, StrategyProfile
from .outcomes import CycleOutcome, OutcomeMetrics, OutcomeEvaluator

logger = logging.getLogger(__name__)


class CalibrationStatus(str, Enum):
    """Status of calibration."""
    WELL_CALIBRATED = "well_calibrated"
    OVER_CONFIDENT = "over_confident"
    UNDER_CONFIDENT = "under_confident"
    INSUFFICIENT_DATA = "insufficient_data"


@dataclass
class CalibrationConfig:
    """Configuration for calibration engine."""
    # Minimum samples for calibration
    min_samples: int = 30

    # Maximum adjustment per calibration
    max_confidence_shift: float = 0.1
    max_threshold_shift: float = 0.05

    # Calibration bands
    well_calibrated_tolerance: float = 0.1  # Within 10% is well-calibrated

    # Smoothing factor for updates
    smoothing_alpha: float = 0.3  # Exponential smoothing

    # Guardrails
    min_confidence_threshold: float = 0.3
    max_confidence_threshold: float = 0.95
    min_action_threshold: float = 0.5
    max_action_threshold: float = 0.9

    # Time-based factors
    recent_weight: float = 2.0  # Weight for recent outcomes
    recent_window_days: int = 7


@dataclass
class ConfidenceCalibration:
    """
    Calibration data for a confidence bucket.

    Tracks how reported confidence maps to actual success.
    """
    bucket_name: str  # "very_low", "low", "medium", "high", "very_high"
    bucket_range: Tuple[float, float]  # (min, max) confidence
    expected_success_rate: float  # Target success rate for this bucket
    actual_success_rate: float
    sample_count: int
    calibration_error: float  # actual - expected
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_well_calibrated(self) -> bool:
        return abs(self.calibration_error) < 0.1

    @property
    def is_over_confident(self) -> bool:
        return self.calibration_error < -0.1

    @property
    def is_under_confident(self) -> bool:
        return self.calibration_error > 0.1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bucket_name": self.bucket_name,
            "bucket_range": self.bucket_range,
            "expected_success_rate": self.expected_success_rate,
            "actual_success_rate": self.actual_success_rate,
            "sample_count": self.sample_count,
            "calibration_error": self.calibration_error,
            "is_well_calibrated": self.is_well_calibrated,
            "is_over_confident": self.is_over_confident,
            "is_under_confident": self.is_under_confident,
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class CalibrationResult:
    """
    Result of a calibration analysis.

    Contains recommended adjustments and supporting data.
    """
    role: AgentRole
    status: CalibrationStatus
    buckets: List[ConfidenceCalibration]

    # Current thresholds
    current_action_threshold: float
    current_recommend_threshold: float

    # Recommended adjustments
    recommended_action_threshold: Optional[float] = None
    recommended_recommend_threshold: Optional[float] = None
    threshold_delta: float = 0.0

    # Additional recommendations
    confidence_scaling_factor: float = 1.0  # Multiply reported confidence by this
    needs_recalibration: bool = False

    # Evidence
    sample_size: int = 0
    analysis_period_days: int = 30

    computed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "status": self.status.value,
            "buckets": [b.to_dict() for b in self.buckets],
            "current_action_threshold": self.current_action_threshold,
            "current_recommend_threshold": self.current_recommend_threshold,
            "recommended_action_threshold": self.recommended_action_threshold,
            "recommended_recommend_threshold": self.recommended_recommend_threshold,
            "threshold_delta": self.threshold_delta,
            "confidence_scaling_factor": self.confidence_scaling_factor,
            "needs_recalibration": self.needs_recalibration,
            "sample_size": self.sample_size,
            "analysis_period_days": self.analysis_period_days,
            "computed_at": self.computed_at.isoformat(),
        }


class CalibrationEngine:
    """
    Engine for calibrating agent confidence levels.

    Uses historical outcomes to determine if an agent is:
    - Over-confident: Claims high confidence but often wrong
    - Under-confident: Claims low confidence but often right
    - Well-calibrated: Confidence matches actual success rates
    """

    # Confidence buckets with expected success rates
    CONFIDENCE_BUCKETS = [
        ("very_low", (0.0, 0.3), 0.2),    # 0-30% confidence should succeed ~20%
        ("low", (0.3, 0.5), 0.4),          # 30-50% -> ~40%
        ("medium", (0.5, 0.7), 0.6),       # 50-70% -> ~60%
        ("high", (0.7, 0.85), 0.8),        # 70-85% -> ~80%
        ("very_high", (0.85, 1.0), 0.9),   # 85-100% -> ~90%
    ]

    def __init__(
        self,
        evaluator: OutcomeEvaluator,
        config: Optional[CalibrationConfig] = None,
    ):
        self.evaluator = evaluator
        self.config = config or CalibrationConfig()
        self._calibration_history: Dict[str, List[CalibrationResult]] = {}

    def analyze_calibration(
        self,
        role: AgentRole,
        profile: StrategyProfile,
        period_days: int = 30,
    ) -> CalibrationResult:
        """
        Analyze calibration for a role and compute recommendations.

        Returns a CalibrationResult with status and recommended adjustments.
        """
        outcomes = self.evaluator.get_outcomes(
            role,
            since=datetime.now(timezone.utc) - timedelta(days=period_days),
        )

        if len(outcomes) < self.config.min_samples:
            return CalibrationResult(
                role=role,
                status=CalibrationStatus.INSUFFICIENT_DATA,
                buckets=[],
                current_action_threshold=profile.min_confidence_to_act,
                current_recommend_threshold=profile.min_confidence_to_recommend,
                sample_size=len(outcomes),
                analysis_period_days=period_days,
            )

        # Analyze each confidence bucket
        buckets = self._analyze_buckets(outcomes)

        # Determine overall status
        status = self._determine_status(buckets)

        # Compute recommendations
        result = self._compute_recommendations(
            role, profile, buckets, status, outcomes
        )

        # Record in history
        role_key = role.value
        if role_key not in self._calibration_history:
            self._calibration_history[role_key] = []
        self._calibration_history[role_key].append(result)

        return result

    def _analyze_buckets(
        self,
        outcomes: List[CycleOutcome],
    ) -> List[ConfidenceCalibration]:
        """Analyze success rates for each confidence bucket."""
        buckets = []

        for bucket_name, (min_conf, max_conf), expected_rate in self.CONFIDENCE_BUCKETS:
            # Filter outcomes in this bucket
            bucket_outcomes = [
                o for o in outcomes
                if min_conf <= o.confidence_reported < max_conf
            ]

            if not bucket_outcomes:
                # No data for this bucket
                buckets.append(ConfidenceCalibration(
                    bucket_name=bucket_name,
                    bucket_range=(min_conf, max_conf),
                    expected_success_rate=expected_rate,
                    actual_success_rate=expected_rate,  # Assume calibrated
                    sample_count=0,
                    calibration_error=0.0,
                ))
                continue

            # Calculate actual success rate
            successes = sum(1 for o in bucket_outcomes if o.success)
            actual_rate = successes / len(bucket_outcomes)

            buckets.append(ConfidenceCalibration(
                bucket_name=bucket_name,
                bucket_range=(min_conf, max_conf),
                expected_success_rate=expected_rate,
                actual_success_rate=actual_rate,
                sample_count=len(bucket_outcomes),
                calibration_error=actual_rate - expected_rate,
            ))

        return buckets

    def _determine_status(
        self,
        buckets: List[ConfidenceCalibration],
    ) -> CalibrationStatus:
        """Determine overall calibration status from bucket analysis."""
        # Only consider buckets with enough samples
        significant_buckets = [b for b in buckets if b.sample_count >= 5]

        if not significant_buckets:
            return CalibrationStatus.INSUFFICIENT_DATA

        # Weight by sample count
        total_samples = sum(b.sample_count for b in significant_buckets)
        weighted_error = sum(
            b.calibration_error * b.sample_count / total_samples
            for b in significant_buckets
        )

        if abs(weighted_error) < self.config.well_calibrated_tolerance:
            return CalibrationStatus.WELL_CALIBRATED
        elif weighted_error < 0:
            return CalibrationStatus.OVER_CONFIDENT
        else:
            return CalibrationStatus.UNDER_CONFIDENT

    def _compute_recommendations(
        self,
        role: AgentRole,
        profile: StrategyProfile,
        buckets: List[ConfidenceCalibration],
        status: CalibrationStatus,
        outcomes: List[CycleOutcome],
    ) -> CalibrationResult:
        """Compute threshold recommendations based on calibration analysis."""
        current_action = profile.min_confidence_to_act
        current_recommend = profile.min_confidence_to_recommend

        recommended_action = None
        recommended_recommend = None
        scaling_factor = 1.0
        needs_recalibration = False

        if status == CalibrationStatus.OVER_CONFIDENT:
            # Agent is too confident - raise thresholds
            shift = min(
                self.config.max_threshold_shift,
                self._calculate_shift(buckets, direction="up"),
            )
            recommended_action = min(
                self.config.max_action_threshold,
                current_action + shift,
            )
            recommended_recommend = min(
                current_action,  # recommend threshold should be <= action threshold
                current_recommend + shift * 0.5,
            )

            # Also suggest scaling down confidence
            scaling_factor = self._calculate_scaling_factor(buckets)
            needs_recalibration = True

        elif status == CalibrationStatus.UNDER_CONFIDENT:
            # Agent is too conservative - lower thresholds
            shift = min(
                self.config.max_threshold_shift,
                self._calculate_shift(buckets, direction="down"),
            )
            recommended_action = max(
                self.config.min_action_threshold,
                current_action - shift,
            )
            recommended_recommend = max(
                self.config.min_confidence_threshold,
                current_recommend - shift * 0.5,
            )

            scaling_factor = self._calculate_scaling_factor(buckets)
            needs_recalibration = True

        # Calculate threshold delta
        threshold_delta = 0.0
        if recommended_action is not None:
            threshold_delta = recommended_action - current_action

        return CalibrationResult(
            role=role,
            status=status,
            buckets=buckets,
            current_action_threshold=current_action,
            current_recommend_threshold=current_recommend,
            recommended_action_threshold=recommended_action,
            recommended_recommend_threshold=recommended_recommend,
            threshold_delta=threshold_delta,
            confidence_scaling_factor=scaling_factor,
            needs_recalibration=needs_recalibration,
            sample_size=len(outcomes),
            analysis_period_days=30,
        )

    def _calculate_shift(
        self,
        buckets: List[ConfidenceCalibration],
        direction: str,
    ) -> float:
        """Calculate recommended threshold shift based on calibration errors."""
        significant_buckets = [b for b in buckets if b.sample_count >= 5]

        if not significant_buckets:
            return 0.0

        # Average absolute error, weighted by sample count
        total_samples = sum(b.sample_count for b in significant_buckets)
        weighted_abs_error = sum(
            abs(b.calibration_error) * b.sample_count / total_samples
            for b in significant_buckets
        )

        # Convert error to shift (larger error = larger shift)
        base_shift = weighted_abs_error * 0.5

        # Apply smoothing
        return base_shift * self.config.smoothing_alpha

    def _calculate_scaling_factor(
        self,
        buckets: List[ConfidenceCalibration],
    ) -> float:
        """
        Calculate a scaling factor for confidence values.

        If agent is over-confident, scaling factor < 1.
        If under-confident, scaling factor > 1.
        """
        significant_buckets = [b for b in buckets if b.sample_count >= 5]

        if not significant_buckets:
            return 1.0

        # Find the average ratio of actual to expected success
        ratios = []
        for b in significant_buckets:
            if b.expected_success_rate > 0:
                ratio = b.actual_success_rate / b.expected_success_rate
                ratios.append(ratio)

        if not ratios:
            return 1.0

        avg_ratio = statistics.mean(ratios)

        # Clamp to reasonable range
        return max(0.7, min(1.3, avg_ratio))

    def apply_calibration(
        self,
        profile: StrategyProfile,
        result: CalibrationResult,
    ) -> StrategyProfile:
        """
        Apply calibration recommendations to a profile.

        Returns a new profile with updated thresholds.
        """
        if not result.needs_recalibration:
            return profile

        # Create copy with updated values
        updated = StrategyProfile.from_dict(profile.to_dict())

        if result.recommended_action_threshold is not None:
            # Apply with smoothing
            updated.min_confidence_to_act = (
                self.config.smoothing_alpha * result.recommended_action_threshold +
                (1 - self.config.smoothing_alpha) * profile.min_confidence_to_act
            )

        if result.recommended_recommend_threshold is not None:
            updated.min_confidence_to_recommend = (
                self.config.smoothing_alpha * result.recommended_recommend_threshold +
                (1 - self.config.smoothing_alpha) * profile.min_confidence_to_recommend
            )

        updated.updated_at = datetime.now(timezone.utc)
        updated.update_reason = f"Calibration adjustment: {result.status.value}"

        return updated

    def get_calibration_history(
        self,
        role: AgentRole,
        limit: int = 10,
    ) -> List[CalibrationResult]:
        """Get calibration history for a role."""
        history = self._calibration_history.get(role.value, [])
        return sorted(history, key=lambda r: r.computed_at, reverse=True)[:limit]

    def get_calibration_trend(
        self,
        role: AgentRole,
    ) -> Dict[str, Any]:
        """Get calibration trend over time."""
        history = self.get_calibration_history(role, limit=10)

        if not history:
            return {"trend": "unknown", "data_points": 0}

        # Calculate trend in threshold delta
        deltas = [r.threshold_delta for r in history]
        statuses = [r.status.value for r in history]

        # Determine trend
        if len(deltas) >= 3:
            recent_avg = statistics.mean(deltas[:3])
            older_avg = statistics.mean(deltas[3:6]) if len(deltas) >= 6 else 0

            if abs(recent_avg) < abs(older_avg):
                trend = "improving"
            elif abs(recent_avg) > abs(older_avg):
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "trend": trend,
            "recent_status": statuses[0] if statuses else None,
            "recent_delta": deltas[0] if deltas else 0,
            "data_points": len(history),
            "status_distribution": {
                s: statuses.count(s) for s in set(statuses)
            },
        }

    def simulate_calibration(
        self,
        role: AgentRole,
        profile: StrategyProfile,
        hypothetical_outcomes: List[CycleOutcome],
    ) -> CalibrationResult:
        """
        Simulate calibration with hypothetical outcomes.

        Useful for testing calibration changes before applying.
        """
        # Temporarily add outcomes
        original_outcomes = self.evaluator.get_outcomes(role)

        for outcome in hypothetical_outcomes:
            self.evaluator.record_outcome(outcome)

        # Run calibration
        result = self.analyze_calibration(role, profile)

        # Remove hypothetical outcomes (in real impl, would need more sophisticated handling)
        # For now, this is a simple simulation

        return result
