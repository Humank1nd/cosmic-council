"""
Strategy Observability Metrics
==============================

Prometheus metrics for strategy performance, calibration, and optimization.

Metrics exported:
- strategy_profile_version: Current version per role
- strategy_outcome_total: Outcome counts by type
- strategy_success_rate: Rolling success rate per role
- strategy_confidence_calibration: Calibration error per role
- strategy_update_total: Update counts by type and status
- strategy_optimization_duration: Time to run optimization
- strategy_learning_loop_total: Learning loop iterations
"""

import logging
from typing import Dict, Optional

try:
    from prometheus_client import Counter, Gauge, Histogram, Summary, Info
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Provide stub implementations
    class StubMetric:
        def labels(self, *args, **kwargs):
            return self
        def inc(self, *args, **kwargs):
            pass
        def dec(self, *args, **kwargs):
            pass
        def set(self, *args, **kwargs):
            pass
        def observe(self, *args, **kwargs):
            pass
        def info(self, *args, **kwargs):
            pass
    Counter = Gauge = Histogram = Summary = Info = lambda *args, **kwargs: StubMetric()

from .registry import AgentRole

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Profile Metrics
# -----------------------------------------------------------------------------

STRATEGY_PROFILE_VERSION = Gauge(
    "strategy_profile_version",
    "Current strategy profile version",
    ["role"],
)

STRATEGY_PROFILE_RISK_TOLERANCE = Gauge(
    "strategy_profile_risk_tolerance",
    "Risk tolerance level (0=very_low, 4=very_high)",
    ["role"],
)

STRATEGY_PROFILE_CONFIDENCE_THRESHOLD = Gauge(
    "strategy_profile_confidence_threshold",
    "Minimum confidence threshold to act",
    ["role"],
)

STRATEGY_TOOL_PREFERENCE_COUNT = Gauge(
    "strategy_tool_preference_count",
    "Number of configured tool preferences",
    ["role"],
)


# -----------------------------------------------------------------------------
# Outcome Metrics
# -----------------------------------------------------------------------------

STRATEGY_OUTCOME_TOTAL = Counter(
    "strategy_outcome_total",
    "Total outcomes recorded",
    ["role", "outcome_type", "success"],
)

STRATEGY_OUTCOME_DURATION = Histogram(
    "strategy_outcome_duration_seconds",
    "Outcome duration in seconds",
    ["role", "outcome_type"],
    buckets=[0.5, 1, 2, 5, 10, 30, 60, 120, 300, 600],
)

STRATEGY_OUTCOME_CONFIDENCE = Histogram(
    "strategy_outcome_confidence",
    "Reported confidence distribution",
    ["role", "success"],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)

STRATEGY_OUTCOME_ITERATIONS = Histogram(
    "strategy_outcome_iterations",
    "Number of iterations per outcome",
    ["role"],
    buckets=[1, 2, 3, 4, 5, 7, 10],
)

STRATEGY_OUTCOME_REWORK = Counter(
    "strategy_outcome_rework_total",
    "Total rework count",
    ["role"],
)

STRATEGY_OUTCOME_INTERVENTION = Counter(
    "strategy_outcome_intervention_total",
    "Total human interventions",
    ["role", "intervention_type"],
)

STRATEGY_SUCCESS_RATE = Gauge(
    "strategy_success_rate",
    "Rolling success rate (last 100 outcomes)",
    ["role"],
)

STRATEGY_AVG_SCORE = Gauge(
    "strategy_avg_score",
    "Average performance score (0-1)",
    ["role"],
)

STRATEGY_USER_RATING = Summary(
    "strategy_user_rating",
    "User rating distribution",
    ["role"],
)


# -----------------------------------------------------------------------------
# Calibration Metrics
# -----------------------------------------------------------------------------

STRATEGY_CALIBRATION_ERROR = Gauge(
    "strategy_calibration_error",
    "Calibration error (actual - expected success rate)",
    ["role", "bucket"],
)

STRATEGY_CALIBRATION_STATUS = Gauge(
    "strategy_calibration_status",
    "Calibration status (0=insufficient, 1=well_calibrated, 2=over, 3=under)",
    ["role"],
)

STRATEGY_CALIBRATION_SCALING_FACTOR = Gauge(
    "strategy_calibration_scaling_factor",
    "Recommended confidence scaling factor",
    ["role"],
)

STRATEGY_CALIBRATION_RUNS = Counter(
    "strategy_calibration_runs_total",
    "Total calibration runs",
    ["role", "status"],
)

STRATEGY_CALIBRATION_DURATION = Histogram(
    "strategy_calibration_duration_seconds",
    "Time to run calibration",
    ["role"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)


# -----------------------------------------------------------------------------
# Optimization Metrics
# -----------------------------------------------------------------------------

STRATEGY_UPDATE_TOTAL = Counter(
    "strategy_update_total",
    "Total strategy updates",
    ["role", "update_type", "risk", "status"],
)

STRATEGY_UPDATE_PENDING = Gauge(
    "strategy_update_pending",
    "Number of pending updates awaiting approval",
    ["role"],
)

STRATEGY_OPTIMIZATION_RUNS = Counter(
    "strategy_optimization_runs_total",
    "Total optimization runs",
    ["role"],
)

STRATEGY_OPTIMIZATION_DURATION = Histogram(
    "strategy_optimization_duration_seconds",
    "Time to run optimization evaluation",
    ["role"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

STRATEGY_OPTIMIZATION_CONFIDENCE = Histogram(
    "strategy_optimization_confidence",
    "Confidence in optimization decisions",
    ["role", "should_update"],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)

STRATEGY_ROLLBACK_TOTAL = Counter(
    "strategy_rollback_total",
    "Total rollbacks performed",
    ["role", "reason"],
)


# -----------------------------------------------------------------------------
# Learning Loop Metrics
# -----------------------------------------------------------------------------

STRATEGY_LEARNING_LOOP_TOTAL = Counter(
    "strategy_learning_loop_total",
    "Total learning loop iterations",
    ["role", "phase"],
)

STRATEGY_LEARNING_LOOP_DURATION = Histogram(
    "strategy_learning_loop_duration_seconds",
    "Full learning loop duration",
    ["role"],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
)

STRATEGY_RULE_TRIGGERED = Counter(
    "strategy_rule_triggered_total",
    "Adaptation rules triggered",
    ["role", "rule_name"],
)

STRATEGY_BUDGET_REMAINING = Gauge(
    "strategy_budget_remaining",
    "Remaining change budget for today",
    ["role"],
)

STRATEGY_COOLDOWN_ACTIVE = Gauge(
    "strategy_cooldown_active",
    "Whether role is in cooldown (1=yes, 0=no)",
    ["role"],
)


# -----------------------------------------------------------------------------
# Tool Performance Metrics
# -----------------------------------------------------------------------------

STRATEGY_TOOL_SUCCESS_RATE = Gauge(
    "strategy_tool_success_rate",
    "Tool success rate",
    ["role", "tool_name"],
)

STRATEGY_TOOL_USAGE = Counter(
    "strategy_tool_usage_total",
    "Tool usage count",
    ["role", "tool_name"],
)

STRATEGY_TOOL_PRIORITY = Gauge(
    "strategy_tool_priority",
    "Tool priority (1-10)",
    ["role", "tool_name"],
)


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

CALIBRATION_STATUS_MAP = {
    "insufficient_data": 0,
    "well_calibrated": 1,
    "over_confident": 2,
    "under_confident": 3,
}

RISK_TOLERANCE_MAP = {
    "very_low": 0,
    "low": 1,
    "moderate": 2,
    "high": 3,
    "very_high": 4,
}


def record_profile_metrics(profile) -> None:
    """Record metrics for a strategy profile."""
    role = profile.role.value

    STRATEGY_PROFILE_VERSION.labels(role=role).set(profile.version)
    STRATEGY_PROFILE_RISK_TOLERANCE.labels(role=role).set(
        RISK_TOLERANCE_MAP.get(profile.risk_tolerance.value, 2)
    )
    STRATEGY_PROFILE_CONFIDENCE_THRESHOLD.labels(role=role).set(
        profile.min_confidence_to_act
    )
    STRATEGY_TOOL_PREFERENCE_COUNT.labels(role=role).set(
        len(profile.tool_preferences)
    )

    # Record tool metrics
    for tool in profile.tool_preferences:
        STRATEGY_TOOL_SUCCESS_RATE.labels(role=role, tool_name=tool.tool_name).set(
            tool.success_rate
        )
        STRATEGY_TOOL_PRIORITY.labels(role=role, tool_name=tool.tool_name).set(
            tool.priority
        )


def record_outcome_metrics(outcome, score: float) -> None:
    """Record metrics for a cycle outcome."""
    role = outcome.role.value
    outcome_type = outcome.outcome_type.value
    success = "true" if outcome.success else "false"

    STRATEGY_OUTCOME_TOTAL.labels(
        role=role,
        outcome_type=outcome_type,
        success=success,
    ).inc()

    STRATEGY_OUTCOME_DURATION.labels(
        role=role,
        outcome_type=outcome_type,
    ).observe(outcome.duration_ms / 1000.0)

    STRATEGY_OUTCOME_CONFIDENCE.labels(
        role=role,
        success=success,
    ).observe(outcome.confidence_reported)

    STRATEGY_OUTCOME_ITERATIONS.labels(role=role).observe(outcome.iteration_count)

    if outcome.rework_count > 0:
        STRATEGY_OUTCOME_REWORK.labels(role=role).inc(outcome.rework_count)

    if outcome.human_intervention:
        STRATEGY_OUTCOME_INTERVENTION.labels(
            role=role,
            intervention_type=outcome.intervention_type or "unknown",
        ).inc()

    if outcome.user_rating is not None:
        STRATEGY_USER_RATING.labels(role=role).observe(outcome.user_rating)

    # Update avg score (this is a simplification - real impl would use sliding window)
    STRATEGY_AVG_SCORE.labels(role=role).set(score)


def record_calibration_metrics(result) -> None:
    """Record metrics for a calibration result."""
    role = result.role.value

    STRATEGY_CALIBRATION_STATUS.labels(role=role).set(
        CALIBRATION_STATUS_MAP.get(result.status.value, 0)
    )

    STRATEGY_CALIBRATION_SCALING_FACTOR.labels(role=role).set(
        result.confidence_scaling_factor
    )

    STRATEGY_CALIBRATION_RUNS.labels(
        role=role,
        status=result.status.value,
    ).inc()

    # Record per-bucket errors
    for bucket in result.buckets:
        STRATEGY_CALIBRATION_ERROR.labels(
            role=role,
            bucket=bucket.bucket_name,
        ).set(bucket.calibration_error)


def record_update_metrics(update) -> None:
    """Record metrics for a strategy update."""
    role = update.role.value

    STRATEGY_UPDATE_TOTAL.labels(
        role=role,
        update_type=update.update_type.value,
        risk=update.risk.value,
        status=update.status,
    ).inc()


def record_optimization_metrics(
    role: AgentRole,
    decision,
    duration_seconds: float,
) -> None:
    """Record metrics for an optimization run."""
    role_value = role.value

    STRATEGY_OPTIMIZATION_RUNS.labels(role=role_value).inc()

    STRATEGY_OPTIMIZATION_DURATION.labels(role=role_value).observe(duration_seconds)

    STRATEGY_OPTIMIZATION_CONFIDENCE.labels(
        role=role_value,
        should_update="true" if decision.should_update else "false",
    ).observe(decision.confidence)

    # Update pending count
    pending_count = len([u for u in decision.updates if u.status == "pending"])
    STRATEGY_UPDATE_PENDING.labels(role=role_value).set(pending_count)


def record_learning_loop_metrics(
    role: AgentRole = None,
    phase: str = "iteration",
    duration_seconds: Optional[float] = None,
    proposed: int = 0,
    applied: int = 0
) -> None:
    """Record metrics for learning loop phases."""
    role_value = role.value if role else "all"

    STRATEGY_LEARNING_LOOP_TOTAL.labels(role=role_value, phase=phase).inc()

    if duration_seconds is not None:
        STRATEGY_LEARNING_LOOP_DURATION.labels(role=role_value).observe(duration_seconds)
        
    # We could add more metrics for proposed/applied if needed
    if proposed > 0:
        logger.debug(f"Learning loop proposed {proposed} updates for {role_value}")
    if applied > 0:
        logger.debug(f"Learning loop applied {applied} updates for {role_value}")


def record_rule_triggered(role: AgentRole, rule_name: str) -> None:
    """Record when an adaptation rule is triggered."""
    STRATEGY_RULE_TRIGGERED.labels(role=role.value, rule_name=rule_name).inc()


def record_rollback(role: AgentRole, reason: str) -> None:
    """Record a rollback event."""
    STRATEGY_ROLLBACK_TOTAL.labels(role=role.value, reason=reason).inc()


def update_budget_metrics(role: AgentRole, remaining: int) -> None:
    """Update change budget metrics."""
    STRATEGY_BUDGET_REMAINING.labels(role=role.value).set(remaining)


def update_cooldown_metrics(role: AgentRole, in_cooldown: bool) -> None:
    """Update cooldown status metrics."""
    STRATEGY_COOLDOWN_ACTIVE.labels(role=role.value).set(1 if in_cooldown else 0)


def update_success_rate_metrics(role: AgentRole, success_rate: float) -> None:
    """Update rolling success rate metric."""
    STRATEGY_SUCCESS_RATE.labels(role=role.value).set(success_rate)


def record_tool_usage(role: AgentRole, tool_name: str) -> None:
    """Record tool usage."""
    STRATEGY_TOOL_USAGE.labels(role=role.value, tool_name=tool_name).inc()


# -----------------------------------------------------------------------------
# Metrics Registry Export
# -----------------------------------------------------------------------------

def get_all_metrics() -> Dict[str, str]:
    """Get all registered metrics with descriptions."""
    return {
        "strategy_profile_version": "Current strategy profile version per role",
        "strategy_profile_risk_tolerance": "Risk tolerance level per role",
        "strategy_profile_confidence_threshold": "Confidence threshold to act",
        "strategy_outcome_total": "Total outcomes by role, type, and success",
        "strategy_outcome_duration_seconds": "Outcome duration distribution",
        "strategy_outcome_confidence": "Reported confidence distribution",
        "strategy_outcome_iterations": "Iteration count distribution",
        "strategy_outcome_rework_total": "Total rework count",
        "strategy_outcome_intervention_total": "Human intervention count",
        "strategy_success_rate": "Rolling success rate per role",
        "strategy_avg_score": "Average performance score",
        "strategy_user_rating": "User rating distribution",
        "strategy_calibration_error": "Calibration error per bucket",
        "strategy_calibration_status": "Calibration status code",
        "strategy_calibration_runs_total": "Total calibration runs",
        "strategy_calibration_duration_seconds": "Calibration duration",
        "strategy_update_total": "Total strategy updates",
        "strategy_update_pending": "Pending updates count",
        "strategy_optimization_runs_total": "Total optimization runs",
        "strategy_optimization_duration_seconds": "Optimization duration",
        "strategy_optimization_confidence": "Decision confidence distribution",
        "strategy_rollback_total": "Total rollbacks",
        "strategy_learning_loop_total": "Learning loop iterations",
        "strategy_learning_loop_duration_seconds": "Full loop duration",
        "strategy_rule_triggered_total": "Rules triggered count",
        "strategy_budget_remaining": "Change budget remaining",
        "strategy_cooldown_active": "Cooldown status",
        "strategy_tool_success_rate": "Tool success rate",
        "strategy_tool_usage_total": "Tool usage count",
        "strategy_tool_priority": "Tool priority value",
    }


# -----------------------------------------------------------------------------
# Truth Metrics
# -----------------------------------------------------------------------------

TRUTH_PROMOTED_TOTAL = Counter(
    "truth_promoted_total",
    "Total truths crystallized",
    ["status", "confidence_level"],
)

TRUTH_REJECTED_TOTAL = Counter(
    "truth_rejected_total",
    "Total truths rejected",
    ["reason"],
)

def record_truth_metrics(status: str, confidence: str = None, reason: str = None):
    if not PROMETHEUS_AVAILABLE:
        return
    
    if status in ["approved", "auto_approved"]:
        TRUTH_PROMOTED_TOTAL.labels(status=status, confidence_level=confidence).inc()
    elif status == "rejected":
        TRUTH_REJECTED_TOTAL.labels(reason=reason or "unknown").inc()
