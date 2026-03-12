"""
Outcome Evaluator
=================

Normalizes outcome signals into scoring metrics for strategy learning.

Outcome Signals:
- Success/failure status
- Rework count (iterations needed)
- Human intervention (required/not)
- Time to resolution
- User feedback (explicit ratings)
- Error patterns
"""

import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .registry import AgentRole

logger = logging.getLogger(__name__)


class OutcomeType(str, Enum):
    """Types of cycle outcomes."""
    SUCCESS = "success"              # Completed successfully
    PARTIAL_SUCCESS = "partial"      # Completed with caveats
    FAILURE = "failure"              # Failed to complete
    TIMEOUT = "timeout"              # Exceeded time limit
    REJECTED = "rejected"            # User rejected output
    REWORK = "rework"                # Required rework iterations


@dataclass
class OutcomeSignal:
    """
    A single outcome signal from a cycle or interaction.

    Signals are collected from various sources and normalized
    into comparable metrics.
    """
    signal_type: str  # "success", "feedback", "rework", "intervention", "latency", "error"
    value: Any
    weight: float = 1.0
    source: str = "system"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_type": self.signal_type,
            "value": self.value,
            "weight": self.weight,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class CycleOutcome:
    """
    Complete outcome record for a triangle cycle.

    Captures all signals and metrics for a cycle's execution.
    """
    cycle_id: str
    problem_id: str
    role: AgentRole
    outcome_type: OutcomeType

    # Timing
    started_at: datetime
    completed_at: datetime
    duration_ms: float

    # Quality metrics
    success: bool
    confidence_reported: float  # What the agent claimed
    confidence_actual: Optional[float] = None  # Calibrated post-hoc

    # Iteration metrics
    iteration_count: int = 1
    rework_count: int = 0

    # Intervention metrics
    human_intervention: bool = False
    intervention_type: Optional[str] = None

    # Feedback
    user_rating: Optional[float] = None  # 1-5 scale
    user_feedback: Optional[str] = None

    # Error tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Raw signals
    signals: List[OutcomeSignal] = field(default_factory=list)

    # Tool usage
    tools_used: List[str] = field(default_factory=list)
    tool_success_rates: Dict[str, float] = field(default_factory=dict)

    # Memory metrics
    memory_queries: int = 0
    memory_hit_rate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "problem_id": self.problem_id,
            "role": self.role.value,
            "outcome_type": self.outcome_type.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "duration_ms": self.duration_ms,
            "success": self.success,
            "confidence_reported": self.confidence_reported,
            "confidence_actual": self.confidence_actual,
            "iteration_count": self.iteration_count,
            "rework_count": self.rework_count,
            "human_intervention": self.human_intervention,
            "intervention_type": self.intervention_type,
            "user_rating": self.user_rating,
            "user_feedback": self.user_feedback,
            "errors": self.errors,
            "warnings": self.warnings,
            "signals": [s.to_dict() for s in self.signals],
            "tools_used": self.tools_used,
            "tool_success_rates": self.tool_success_rates,
            "memory_queries": self.memory_queries,
            "memory_hit_rate": self.memory_hit_rate,
        }


@dataclass
class OutcomeMetrics:
    """
    Aggregated metrics computed from outcome signals.

    Used for strategy evaluation and calibration.
    """
    # Overall success
    success_rate: float
    partial_rate: float
    failure_rate: float

    # Timing
    avg_duration_ms: float
    p50_duration_ms: float
    p95_duration_ms: float

    # Iteration quality
    avg_iterations: float
    avg_rework: float
    first_time_success_rate: float

    # Intervention
    intervention_rate: float

    # Confidence calibration
    avg_confidence: float
    confidence_accuracy: float  # How well confidence predicts success

    # User satisfaction
    avg_rating: Optional[float]
    rating_count: int

    # Sample info
    sample_size: int
    period_start: datetime
    period_end: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success_rate": self.success_rate,
            "partial_rate": self.partial_rate,
            "failure_rate": self.failure_rate,
            "avg_duration_ms": self.avg_duration_ms,
            "p50_duration_ms": self.p50_duration_ms,
            "p95_duration_ms": self.p95_duration_ms,
            "avg_iterations": self.avg_iterations,
            "avg_rework": self.avg_rework,
            "first_time_success_rate": self.first_time_success_rate,
            "intervention_rate": self.intervention_rate,
            "avg_confidence": self.avg_confidence,
            "confidence_accuracy": self.confidence_accuracy,
            "avg_rating": self.avg_rating,
            "rating_count": self.rating_count,
            "sample_size": self.sample_size,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
        }


@dataclass
class RoleScorecard:
    """
    Performance scorecard for a role.

    Aggregates outcome metrics with role-specific scoring.
    """
    role: AgentRole
    metrics: OutcomeMetrics
    computed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Computed scores (0-100)
    accuracy_score: float = 0.0
    speed_score: float = 0.0
    thoroughness_score: float = 0.0
    efficiency_score: float = 0.0
    overall_score: float = 0.0

    # Trends (vs previous period)
    accuracy_trend: float = 0.0  # Positive = improving
    speed_trend: float = 0.0
    overall_trend: float = 0.0

    # Recommendations
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "metrics": self.metrics.to_dict(),
            "computed_at": self.computed_at.isoformat(),
            "scores": {
                "accuracy": self.accuracy_score,
                "speed": self.speed_score,
                "thoroughness": self.thoroughness_score,
                "efficiency": self.efficiency_score,
                "overall": self.overall_score,
            },
            "trends": {
                "accuracy": self.accuracy_trend,
                "speed": self.speed_trend,
                "overall": self.overall_trend,
            },
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
        }


class OutcomeEvaluator:
    """
    Evaluates cycle outcomes and computes metrics.

    Features:
    - Signal normalization
    - Role-specific scoring
    - Confidence calibration computation
    - Trend analysis
    """

    # Role-specific scoring weights
    ROLE_WEIGHTS = {
        AgentRole.WHY: {
            "accuracy": 0.4,
            "speed": 0.1,
            "thoroughness": 0.35,
            "efficiency": 0.15,
        },
        AgentRole.HOW: {
            "accuracy": 0.3,
            "speed": 0.2,
            "thoroughness": 0.25,
            "efficiency": 0.25,
        },
        AgentRole.WHAT: {
            "accuracy": 0.35,
            "speed": 0.15,
            "thoroughness": 0.35,
            "efficiency": 0.15,
        },
        AgentRole.WHEN: {
            "accuracy": 0.4,  # Timeline accuracy is critical
            "speed": 0.25,
            "thoroughness": 0.2,
            "efficiency": 0.15,
        },
        AgentRole.WHERE: {
            "accuracy": 0.3,
            "speed": 0.25,
            "thoroughness": 0.2,
            "efficiency": 0.25,
        },
        AgentRole.WHO: {
            "accuracy": 0.35,
            "speed": 0.2,
            "thoroughness": 0.25,
            "efficiency": 0.2,
        },
    }

    # Baseline thresholds for scoring
    BASELINES = {
        "duration_good_ms": 5000,
        "duration_acceptable_ms": 15000,
        "iterations_good": 1,
        "iterations_acceptable": 3,
        "rework_good": 0,
        "rework_acceptable": 1,
        "confidence_threshold": 0.8,
    }

    def __init__(self):
        self._outcomes: Dict[str, List[CycleOutcome]] = {}  # role -> outcomes

    def record_outcome(self, outcome: CycleOutcome) -> None:
        """Record a cycle outcome."""
        role_key = outcome.role.value
        if role_key not in self._outcomes:
            self._outcomes[role_key] = []
        self._outcomes[role_key].append(outcome)
        logger.debug(f"Recorded outcome for {role_key}: {outcome.outcome_type.value}")

    def get_outcomes(
        self,
        role: AgentRole,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[CycleOutcome]:
        """Get outcomes for a role."""
        outcomes = self._outcomes.get(role.value, [])

        if since:
            outcomes = [o for o in outcomes if o.completed_at >= since]

        outcomes = sorted(outcomes, key=lambda o: o.completed_at, reverse=True)

        if limit:
            outcomes = outcomes[:limit]

        return outcomes

    def compute_metrics(
        self,
        role: AgentRole,
        period_days: int = 30,
    ) -> OutcomeMetrics:
        """Compute aggregated metrics for a role over a period."""
        period_start = datetime.now(timezone.utc) - timedelta(days=period_days)
        outcomes = self.get_outcomes(role, since=period_start)

        if not outcomes:
            return self._empty_metrics(period_start)

        # Success rates
        total = len(outcomes)
        successes = sum(1 for o in outcomes if o.outcome_type == OutcomeType.SUCCESS)
        partials = sum(1 for o in outcomes if o.outcome_type == OutcomeType.PARTIAL_SUCCESS)
        failures = total - successes - partials

        # Timing
        durations = [o.duration_ms for o in outcomes]
        sorted_durations = sorted(durations)

        # Iterations
        iterations = [o.iteration_count for o in outcomes]
        reworks = [o.rework_count for o in outcomes]
        first_time = sum(1 for o in outcomes if o.iteration_count == 1 and o.success)

        # Intervention
        interventions = sum(1 for o in outcomes if o.human_intervention)

        # Confidence
        confidences = [o.confidence_reported for o in outcomes if o.confidence_reported]
        confidence_accuracy = self._compute_confidence_accuracy(outcomes)

        # Ratings
        ratings = [o.user_rating for o in outcomes if o.user_rating is not None]

        return OutcomeMetrics(
            success_rate=successes / total,
            partial_rate=partials / total,
            failure_rate=failures / total,
            avg_duration_ms=statistics.mean(durations),
            p50_duration_ms=sorted_durations[len(sorted_durations) // 2],
            p95_duration_ms=sorted_durations[int(len(sorted_durations) * 0.95)] if len(sorted_durations) > 1 else sorted_durations[0],
            avg_iterations=statistics.mean(iterations),
            avg_rework=statistics.mean(reworks),
            first_time_success_rate=first_time / total if total > 0 else 0,
            intervention_rate=interventions / total,
            avg_confidence=statistics.mean(confidences) if confidences else 0.5,
            confidence_accuracy=confidence_accuracy,
            avg_rating=statistics.mean(ratings) if ratings else None,
            rating_count=len(ratings),
            sample_size=total,
            period_start=period_start,
            period_end=datetime.now(timezone.utc),
        )

    def _compute_confidence_accuracy(self, outcomes: List[CycleOutcome]) -> float:
        """
        Compute how well reported confidence predicts actual success.

        Returns a value between 0 and 1 where 1 means perfect calibration.
        """
        if not outcomes:
            return 0.5

        # Bucket outcomes by confidence level
        buckets: Dict[str, List[bool]] = {
            "low": [],      # < 0.4
            "medium": [],   # 0.4 - 0.7
            "high": [],     # > 0.7
        }

        for o in outcomes:
            if o.confidence_reported < 0.4:
                buckets["low"].append(o.success)
            elif o.confidence_reported < 0.7:
                buckets["medium"].append(o.success)
            else:
                buckets["high"].append(o.success)

        # Calculate calibration error
        # Well-calibrated: low confidence -> low success, high confidence -> high success
        errors = []

        for bucket_name, expected_rate in [("low", 0.3), ("medium", 0.55), ("high", 0.8)]:
            bucket = buckets[bucket_name]
            if bucket:
                actual_rate = sum(bucket) / len(bucket)
                errors.append(abs(actual_rate - expected_rate))

        if not errors:
            return 0.5

        # Convert error to accuracy (lower error = higher accuracy)
        avg_error = statistics.mean(errors)
        return max(0, 1 - avg_error)

    def _empty_metrics(self, period_start: datetime) -> OutcomeMetrics:
        """Return empty metrics when no data available."""
        return OutcomeMetrics(
            success_rate=0,
            partial_rate=0,
            failure_rate=0,
            avg_duration_ms=0,
            p50_duration_ms=0,
            p95_duration_ms=0,
            avg_iterations=0,
            avg_rework=0,
            first_time_success_rate=0,
            intervention_rate=0,
            avg_confidence=0.5,
            confidence_accuracy=0.5,
            avg_rating=None,
            rating_count=0,
            sample_size=0,
            period_start=period_start,
            period_end=datetime.now(timezone.utc),
        )

    def compute_scorecard(
        self,
        role: AgentRole,
        period_days: int = 30,
        previous_scorecard: Optional[RoleScorecard] = None,
    ) -> RoleScorecard:
        """
        Compute a full scorecard for a role.

        Includes scores, trends, and recommendations.
        """
        metrics = self.compute_metrics(role, period_days)
        weights = self.ROLE_WEIGHTS.get(role, self.ROLE_WEIGHTS[AgentRole.WHY])

        # Compute individual scores
        accuracy_score = self._score_accuracy(metrics)
        speed_score = self._score_speed(metrics)
        thoroughness_score = self._score_thoroughness(metrics)
        efficiency_score = self._score_efficiency(metrics)

        # Weighted overall score
        overall_score = (
            accuracy_score * weights["accuracy"] +
            speed_score * weights["speed"] +
            thoroughness_score * weights["thoroughness"] +
            efficiency_score * weights["efficiency"]
        )

        # Compute trends
        accuracy_trend = 0.0
        speed_trend = 0.0
        overall_trend = 0.0

        if previous_scorecard:
            accuracy_trend = accuracy_score - previous_scorecard.accuracy_score
            speed_trend = speed_score - previous_scorecard.speed_score
            overall_trend = overall_score - previous_scorecard.overall_score

        # Generate recommendations
        strengths, weaknesses, recommendations = self._generate_recommendations(
            role, accuracy_score, speed_score, thoroughness_score, efficiency_score, metrics
        )

        return RoleScorecard(
            role=role,
            metrics=metrics,
            accuracy_score=accuracy_score,
            speed_score=speed_score,
            thoroughness_score=thoroughness_score,
            efficiency_score=efficiency_score,
            overall_score=overall_score,
            accuracy_trend=accuracy_trend,
            speed_trend=speed_trend,
            overall_trend=overall_trend,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
        )

    def _score_accuracy(self, metrics: OutcomeMetrics) -> float:
        """Score accuracy (0-100) based on success rates and confidence calibration."""
        if metrics.sample_size == 0:
            return 50.0

        base_score = metrics.success_rate * 100

        # Bonus/penalty for confidence calibration
        calibration_factor = (metrics.confidence_accuracy - 0.5) * 20

        # Penalty for high rework
        rework_penalty = min(metrics.avg_rework * 5, 20)

        return max(0, min(100, base_score + calibration_factor - rework_penalty))

    def _score_speed(self, metrics: OutcomeMetrics) -> float:
        """Score speed (0-100) based on duration."""
        if metrics.sample_size == 0 or metrics.avg_duration_ms == 0:
            return 50.0

        baselines = self.BASELINES

        if metrics.avg_duration_ms <= baselines["duration_good_ms"]:
            return 100.0
        elif metrics.avg_duration_ms <= baselines["duration_acceptable_ms"]:
            # Linear interpolation
            ratio = (metrics.avg_duration_ms - baselines["duration_good_ms"]) / \
                    (baselines["duration_acceptable_ms"] - baselines["duration_good_ms"])
            return 100 - (ratio * 30)  # 70-100 range
        else:
            # Exponential decay for slow responses
            excess = metrics.avg_duration_ms / baselines["duration_acceptable_ms"]
            return max(0, 70 - (excess - 1) * 20)

    def _score_thoroughness(self, metrics: OutcomeMetrics) -> float:
        """Score thoroughness based on completeness and quality."""
        if metrics.sample_size == 0:
            return 50.0

        # Based on first-time success and low intervention
        base_score = metrics.first_time_success_rate * 100

        # Bonus for low intervention
        intervention_bonus = (1 - metrics.intervention_rate) * 15

        # Bonus for good ratings
        rating_bonus = 0
        if metrics.avg_rating:
            rating_bonus = (metrics.avg_rating - 3) * 10  # -20 to +20

        return max(0, min(100, base_score + intervention_bonus + rating_bonus))

    def _score_efficiency(self, metrics: OutcomeMetrics) -> float:
        """Score efficiency based on iterations and resource usage."""
        if metrics.sample_size == 0:
            return 50.0

        baselines = self.BASELINES

        # Based on iteration count
        if metrics.avg_iterations <= baselines["iterations_good"]:
            iteration_score = 100
        elif metrics.avg_iterations <= baselines["iterations_acceptable"]:
            iteration_score = 100 - ((metrics.avg_iterations - 1) * 15)
        else:
            iteration_score = max(0, 55 - (metrics.avg_iterations - 3) * 10)

        # Based on rework
        if metrics.avg_rework <= baselines["rework_good"]:
            rework_score = 100
        elif metrics.avg_rework <= baselines["rework_acceptable"]:
            rework_score = 80
        else:
            rework_score = max(0, 60 - metrics.avg_rework * 10)

        return (iteration_score + rework_score) / 2

    def _generate_recommendations(
        self,
        role: AgentRole,
        accuracy: float,
        speed: float,
        thoroughness: float,
        efficiency: float,
        metrics: OutcomeMetrics,
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate strengths, weaknesses, and recommendations."""
        strengths = []
        weaknesses = []
        recommendations = []

        # Analyze each dimension
        if accuracy >= 80:
            strengths.append("High accuracy in outputs")
        elif accuracy < 60:
            weaknesses.append("Low accuracy rate")
            recommendations.append("Increase evidence requirements before conclusions")

        if speed >= 80:
            strengths.append("Fast response times")
        elif speed < 60:
            weaknesses.append("Slow response times")
            recommendations.append("Consider caching common patterns or simplifying approach")

        if thoroughness >= 80:
            strengths.append("Thorough and complete outputs")
        elif thoroughness < 60:
            weaknesses.append("Outputs often incomplete or require follow-up")
            recommendations.append("Add completeness checks before finalizing")

        if efficiency >= 80:
            strengths.append("Efficient use of iterations")
        elif efficiency < 60:
            weaknesses.append("High iteration/rework count")
            recommendations.append("Improve initial analysis to reduce rework")

        # Role-specific recommendations
        if role == AgentRole.WHY:
            if metrics.confidence_accuracy < 0.6:
                recommendations.append("Calibrate confidence levels - predictions are poorly calibrated")
            if metrics.avg_rework > 1:
                recommendations.append("Strengthen evidence requirements before stating root causes")

        elif role == AgentRole.HOW:
            if metrics.intervention_rate > 0.3:
                recommendations.append("Improve feasibility checks - high human intervention rate")

        elif role == AgentRole.WHAT:
            if metrics.first_time_success_rate < 0.7:
                recommendations.append("Improve requirement analysis to reduce spec revisions")

        elif role == AgentRole.WHEN:
            if metrics.success_rate < 0.7:
                recommendations.append("Add buffer time to estimates - timeline accuracy is low")

        return strengths, weaknesses, recommendations

    def get_role_comparison(self) -> Dict[str, Any]:
        """Compare performance across all roles."""
        comparison = {}

        for role in AgentRole:
            scorecard = self.compute_scorecard(role)
            comparison[role.value] = {
                "overall_score": scorecard.overall_score,
                "success_rate": scorecard.metrics.success_rate,
                "sample_size": scorecard.metrics.sample_size,
                "top_strength": scorecard.strengths[0] if scorecard.strengths else None,
                "top_weakness": scorecard.weaknesses[0] if scorecard.weaknesses else None,
            }

        return comparison
