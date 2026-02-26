"""
Confidence Calibration for Agent Orchestrator Triangle Decisions.

Provides configurable thresholds per triangle role with optional
dynamic calibration based on historical performance.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============== Enums ==============

class TriangleRole(Enum):
    """Triangle roles corresponding to ROYGBV agents."""
    WHY = "why"       # Red Owl
    HOW = "how"       # Orange Orangutan
    WHAT = "what"     # Yellow Honeybee
    WHEN = "when"     # Green Tortoise
    WHERE = "where"   # Blue Dolphin
    WHO = "who"       # Purple Elephant


class ConfidenceDecision(Enum):
    """Decisions based on confidence evaluation."""
    PROCEED = "proceed"           # Continue to next stage
    RECURSE = "recurse"           # Loop back to Red Owl
    HUMAN_REVIEW = "human_review" # Escalate to human
    REJECT = "reject"             # Reject with error


# ============== Threshold Configuration ==============

@dataclass
class RoleThresholds:
    """Confidence thresholds for a specific role."""
    min_confidence: float       # Below this -> human review
    recursion_threshold: float  # Below this -> suggest recursion
    proceed_threshold: float    # Above this -> proceed confidently

    def evaluate(self, confidence: float) -> ConfidenceDecision:
        """Evaluate confidence against thresholds."""
        if confidence >= self.proceed_threshold:
            return ConfidenceDecision.PROCEED
        elif confidence >= self.min_confidence:
            return ConfidenceDecision.PROCEED  # Marginal but acceptable
        elif confidence >= self.recursion_threshold:
            return ConfidenceDecision.RECURSE
        else:
            return ConfidenceDecision.HUMAN_REVIEW


@dataclass
class ConfidenceThresholds:
    """Complete threshold configuration for all roles."""

    # Per-role thresholds (min_confidence, recursion_threshold, proceed_threshold)
    why: RoleThresholds = field(default_factory=lambda: RoleThresholds(0.30, 0.50, 0.70))
    how: RoleThresholds = field(default_factory=lambda: RoleThresholds(0.30, 0.50, 0.65))
    what: RoleThresholds = field(default_factory=lambda: RoleThresholds(0.30, 0.50, 0.70))
    when: RoleThresholds = field(default_factory=lambda: RoleThresholds(0.30, 0.50, 0.60))
    where: RoleThresholds = field(default_factory=lambda: RoleThresholds(0.30, 0.50, 0.65))
    who: RoleThresholds = field(default_factory=lambda: RoleThresholds(0.30, 0.50, 0.75))

    # Global settings
    max_recursions: int = 5
    recursion_approval_threshold: int = 3  # Require approval above this

    def get_role_thresholds(self, role: TriangleRole) -> RoleThresholds:
        """Get thresholds for a specific role."""
        role_map = {
            TriangleRole.WHY: self.why,
            TriangleRole.HOW: self.how,
            TriangleRole.WHAT: self.what,
            TriangleRole.WHEN: self.when,
            TriangleRole.WHERE: self.where,
            TriangleRole.WHO: self.who,
        }
        return role_map[role]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize thresholds to dict."""
        return {
            "why": {"min": self.why.min_confidence, "recurse": self.why.recursion_threshold, "proceed": self.why.proceed_threshold},
            "how": {"min": self.how.min_confidence, "recurse": self.how.recursion_threshold, "proceed": self.how.proceed_threshold},
            "what": {"min": self.what.min_confidence, "recurse": self.what.recursion_threshold, "proceed": self.what.proceed_threshold},
            "when": {"min": self.when.min_confidence, "recurse": self.when.recursion_threshold, "proceed": self.when.proceed_threshold},
            "where": {"min": self.where.min_confidence, "recurse": self.where.recursion_threshold, "proceed": self.where.proceed_threshold},
            "who": {"min": self.who.min_confidence, "recurse": self.who.recursion_threshold, "proceed": self.who.proceed_threshold},
            "max_recursions": self.max_recursions,
            "recursion_approval_threshold": self.recursion_approval_threshold,
        }


# ============== Calibration Result ==============

@dataclass
class CalibrationResult:
    """Result of confidence evaluation."""
    decision: ConfidenceDecision
    raw_confidence: float
    calibrated_confidence: float
    role: TriangleRole
    thresholds: RoleThresholds
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to dict."""
        return {
            "decision": self.decision.value,
            "raw_confidence": self.raw_confidence,
            "calibrated_confidence": self.calibrated_confidence,
            "role": self.role.value,
            "reason": self.reason,
            "metadata": self.metadata,
        }


# ============== Historical Performance ==============

@dataclass
class HistoricalMetrics:
    """Historical performance metrics for calibration."""
    total_cycles: int = 0
    successful_cycles: int = 0
    recursion_count: int = 0
    human_review_count: int = 0
    avg_confidence_by_role: Dict[str, float] = field(default_factory=dict)
    success_rate_by_role: Dict[str, float] = field(default_factory=dict)


# ============== Confidence Calibrator ==============

class ConfidenceCalibrator:
    """
    Calibrates confidence thresholds based on historical performance.

    Features:
    - Per-role threshold configuration
    - Dynamic calibration from history
    - Context-aware adjustments
    - Recursion depth consideration
    """

    def __init__(
        self,
        thresholds: Optional[ConfidenceThresholds] = None,
        enable_dynamic_calibration: bool = False,
    ):
        self.thresholds = thresholds or ConfidenceThresholds()
        self.enable_dynamic_calibration = enable_dynamic_calibration
        self._historical_metrics: Optional[HistoricalMetrics] = None
        self._calibration_adjustments: Dict[TriangleRole, float] = {}

    def evaluate_confidence(
        self,
        role: TriangleRole,
        raw_confidence: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> CalibrationResult:
        """
        Evaluate confidence for a triangle role.

        Args:
            role: The triangle role being evaluated
            raw_confidence: Raw confidence score from agent (0.0-1.0)
            context: Optional context for calibration adjustments

        Returns:
            CalibrationResult with decision and calibrated confidence
        """
        context = context or {}
        role_thresholds = self.thresholds.get_role_thresholds(role)

        # Apply calibration adjustments if enabled
        calibrated = self._apply_calibration(role, raw_confidence, context)

        # Get base decision from thresholds
        decision = role_thresholds.evaluate(calibrated)

        # Check recursion depth constraints
        recursion_depth = context.get("recursion_depth", 0)
        if recursion_depth >= self.thresholds.max_recursions:
            if decision == ConfidenceDecision.RECURSE:
                decision = ConfidenceDecision.HUMAN_REVIEW
                reason = f"Max recursions ({self.thresholds.max_recursions}) reached"
            else:
                reason = self._get_decision_reason(decision, calibrated, role_thresholds)
        else:
            reason = self._get_decision_reason(decision, calibrated, role_thresholds)

        result = CalibrationResult(
            decision=decision,
            raw_confidence=raw_confidence,
            calibrated_confidence=calibrated,
            role=role,
            thresholds=role_thresholds,
            reason=reason,
            metadata={
                "recursion_depth": recursion_depth,
                "max_recursions": self.thresholds.max_recursions,
                "dynamic_calibration": self.enable_dynamic_calibration,
            }
        )

        logger.info(
            f"Confidence evaluation for {role.value}: "
            f"{raw_confidence:.2f} -> {calibrated:.2f} = {decision.value}"
        )

        return result

    def evaluate_cycle_completion(
        self,
        stage_confidences: Dict[str, float],
        is_solved: bool,
        recursion_depth: int,
    ) -> Tuple[ConfidenceDecision, str]:
        """
        Evaluate whether a cycle should complete, recurse, or escalate.

        This is called after Purple Elephant (WHO) stage to determine
        the 7th step decision.

        Args:
            stage_confidences: Confidence scores from all stages
            is_solved: Whether the agent determined problem is solved
            recursion_depth: Current recursion depth

        Returns:
            Tuple of (decision, reason)
        """
        # Calculate overall confidence
        if not stage_confidences:
            return (
                ConfidenceDecision.HUMAN_REVIEW,
                "No stage confidences available"
            )

        overall_confidence = sum(stage_confidences.values()) / len(stage_confidences)

        # Get WHO (Purple Elephant) confidence - critical for final decision
        who_confidence = stage_confidences.get("who", stage_confidences.get("WHO", 0.0))
        who_thresholds = self.thresholds.get_role_thresholds(TriangleRole.WHO)

        # Check if max recursions reached
        if recursion_depth >= self.thresholds.max_recursions:
            return (
                ConfidenceDecision.HUMAN_REVIEW,
                f"Max recursions ({self.thresholds.max_recursions}) reached with "
                f"confidence {overall_confidence:.2f}"
            )

        # If agent says solved and confidence is good, complete
        if is_solved and who_confidence >= who_thresholds.min_confidence:
            return (
                ConfidenceDecision.PROCEED,
                f"Problem solved with confidence {who_confidence:.2f}"
            )

        # If not solved, check if we should recurse or escalate
        if overall_confidence < who_thresholds.recursion_threshold:
            return (
                ConfidenceDecision.HUMAN_REVIEW,
                f"Overall confidence {overall_confidence:.2f} below recursion threshold"
            )

        # Recurse if we haven't hit approval threshold
        if recursion_depth < self.thresholds.recursion_approval_threshold:
            return (
                ConfidenceDecision.RECURSE,
                f"Recursion suggested (depth {recursion_depth}) - not solved"
            )

        # Need approval for deep recursion
        return (
            ConfidenceDecision.HUMAN_REVIEW,
            f"Deep recursion (depth {recursion_depth}) requires approval"
        )

    def _apply_calibration(
        self,
        role: TriangleRole,
        raw_confidence: float,
        context: Dict[str, Any],
    ) -> float:
        """Apply calibration adjustments to raw confidence."""
        calibrated = raw_confidence

        if not self.enable_dynamic_calibration:
            return calibrated

        # Apply role-specific adjustment from history
        if role in self._calibration_adjustments:
            calibrated += self._calibration_adjustments[role]

        # Apply recursion depth penalty (deeper = more conservative)
        recursion_depth = context.get("recursion_depth", 0)
        if recursion_depth > 0:
            # Slight penalty for each recursion level
            penalty = 0.02 * recursion_depth
            calibrated -= penalty

        # Clamp to valid range
        return max(0.0, min(1.0, calibrated))

    def _get_decision_reason(
        self,
        decision: ConfidenceDecision,
        confidence: float,
        thresholds: RoleThresholds,
    ) -> str:
        """Generate human-readable reason for decision."""
        if decision == ConfidenceDecision.PROCEED:
            if confidence >= thresholds.proceed_threshold:
                return f"Confidence {confidence:.2f} >= proceed threshold {thresholds.proceed_threshold}"
            else:
                return f"Confidence {confidence:.2f} >= min threshold {thresholds.min_confidence} (marginal)"
        elif decision == ConfidenceDecision.RECURSE:
            return f"Confidence {confidence:.2f} in recursion range [{thresholds.recursion_threshold}, {thresholds.min_confidence})"
        elif decision == ConfidenceDecision.HUMAN_REVIEW:
            return f"Confidence {confidence:.2f} < recursion threshold {thresholds.recursion_threshold}"
        else:
            return f"Confidence {confidence:.2f} rejected"

    async def calibrate_from_history(
        self,
        lookback_days: int = 30,
        analytics_repository=None,
    ) -> ConfidenceThresholds:
        """
        Adjust thresholds based on historical cycle performance.

        Args:
            lookback_days: Number of days to analyze
            analytics_repository: Repository for querying historical data

        Returns:
            Updated ConfidenceThresholds
        """
        if analytics_repository is None:
            logger.warning("No analytics repository provided for calibration")
            return self.thresholds

        try:
            # Query historical metrics
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=lookback_days)

            metrics = await analytics_repository.get_calibration_metrics(
                start_time=start_time,
                end_time=end_time,
            )

            self._historical_metrics = HistoricalMetrics(
                total_cycles=metrics.get("total_cycles", 0),
                successful_cycles=metrics.get("successful_cycles", 0),
                recursion_count=metrics.get("recursion_count", 0),
                human_review_count=metrics.get("human_review_count", 0),
                avg_confidence_by_role=metrics.get("avg_confidence_by_role", {}),
                success_rate_by_role=metrics.get("success_rate_by_role", {}),
            )

            # Calculate adjustments based on success rates
            self._calculate_adjustments()

            logger.info(
                f"Calibration complete: {self._historical_metrics.total_cycles} cycles, "
                f"{self._historical_metrics.successful_cycles} successful"
            )

        except Exception as e:
            logger.error(f"Calibration failed: {e}")

        return self.thresholds

    def _calculate_adjustments(self) -> None:
        """Calculate calibration adjustments from historical metrics."""
        if not self._historical_metrics:
            return

        for role in TriangleRole:
            role_name = role.value.lower()
            success_rate = self._historical_metrics.success_rate_by_role.get(role_name, 0.5)

            # If success rate is high, we can be more lenient
            # If success rate is low, be more conservative
            if success_rate > 0.8:
                self._calibration_adjustments[role] = 0.05  # Boost confidence
            elif success_rate < 0.5:
                self._calibration_adjustments[role] = -0.05  # Reduce confidence
            else:
                self._calibration_adjustments[role] = 0.0

    def update_thresholds(
        self,
        role: TriangleRole,
        min_confidence: Optional[float] = None,
        recursion_threshold: Optional[float] = None,
        proceed_threshold: Optional[float] = None,
    ) -> None:
        """
        Update thresholds for a specific role.

        Args:
            role: Role to update
            min_confidence: New minimum confidence threshold
            recursion_threshold: New recursion threshold
            proceed_threshold: New proceed threshold
        """
        current = self.thresholds.get_role_thresholds(role)

        new_thresholds = RoleThresholds(
            min_confidence=min_confidence if min_confidence is not None else current.min_confidence,
            recursion_threshold=recursion_threshold if recursion_threshold is not None else current.recursion_threshold,
            proceed_threshold=proceed_threshold if proceed_threshold is not None else current.proceed_threshold,
        )

        # Update in thresholds object
        role_attr = role.value.lower()
        setattr(self.thresholds, role_attr, new_thresholds)

        logger.info(f"Updated thresholds for {role.value}: {new_thresholds}")


# ============== Factory Functions ==============

def create_calibrator(
    config: Optional[Dict[str, Any]] = None,
    enable_dynamic: bool = False,
) -> ConfidenceCalibrator:
    """
    Create a confidence calibrator with optional configuration.

    Args:
        config: Optional threshold configuration dict
        enable_dynamic: Enable dynamic calibration from history

    Returns:
        Configured ConfidenceCalibrator
    """
    thresholds = ConfidenceThresholds()

    if config:
        # Apply custom thresholds from config
        for role_name in ["why", "how", "what", "when", "where", "who"]:
            if role_name in config:
                role_config = config[role_name]
                role_thresholds = RoleThresholds(
                    min_confidence=role_config.get("min", 0.30),
                    recursion_threshold=role_config.get("recurse", 0.50),
                    proceed_threshold=role_config.get("proceed", 0.70),
                )
                setattr(thresholds, role_name, role_thresholds)

        if "max_recursions" in config:
            thresholds.max_recursions = config["max_recursions"]
        if "recursion_approval_threshold" in config:
            thresholds.recursion_approval_threshold = config["recursion_approval_threshold"]

    return ConfidenceCalibrator(
        thresholds=thresholds,
        enable_dynamic_calibration=enable_dynamic,
    )


# ============== Global Instance ==============

_default_calibrator: Optional[ConfidenceCalibrator] = None


def get_calibrator() -> ConfidenceCalibrator:
    """Get the global calibrator instance."""
    global _default_calibrator
    if _default_calibrator is None:
        _default_calibrator = ConfidenceCalibrator()
    return _default_calibrator


def set_calibrator(calibrator: ConfidenceCalibrator) -> None:
    """Set the global calibrator instance."""
    global _default_calibrator
    _default_calibrator = calibrator
