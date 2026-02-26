"""
BLACK SNAKE - Outcome Collector.

Captures and analyzes execution outcomes.
This implements Criterion 2: Outcome capture.

All results must be properly recorded.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

import structlog

from .models import (
    ExecutionRecord,
    ExecutionStatus,
    ExecutionOutcome,
    OutcomeType,
    BlackSnakeConfig,
)
from .executor import ExecutionResult

logger = structlog.get_logger(__name__)


@dataclass
class OutcomeAnalysis:
    """Analysis of an execution outcome."""
    outcome: ExecutionOutcome
    patterns_detected: List[str] = field(default_factory=list)
    anomalies: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class BatchOutcomeResult:
    """Result of collecting outcomes for multiple executions."""
    outcomes: List[ExecutionOutcome] = field(default_factory=list)
    analyses: List[OutcomeAnalysis] = field(default_factory=list)
    total_captured: int = 0
    success_count: int = 0
    failure_count: int = 0
    surprises_detected: int = 0
    duration_ms: int = 0


class OutcomeCollector:
    """
    Collects and analyzes execution outcomes.

    Criterion 2: Results are properly recorded.
    """

    def __init__(
        self,
        config: Optional[BlackSnakeConfig] = None,
    ):
        """
        Initialize the outcome collector.

        Args:
            config: Configuration
        """
        self.config = config or BlackSnakeConfig()

        # Outcome storage
        self._outcomes: List[ExecutionOutcome] = []
        self._analyses: List[OutcomeAnalysis] = []

        # Pattern tracking
        self._known_patterns: Dict[str, int] = {}
        self._failure_patterns: Dict[str, List[str]] = {}

        logger.info("outcome_collector_initialized")

    def collect(
        self,
        result: ExecutionResult,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionOutcome:
        """
        Collect outcome from an execution result.

        Args:
            result: Execution result
            context: Additional context

        Returns:
            ExecutionOutcome
        """
        context = context or {}
        record = result.record

        # Determine outcome type
        outcome_type = self._classify_outcome(result)

        # Calculate impact
        impact_score = self._calculate_impact(result, context)

        # Detect surprises
        surprises = self._detect_surprises(result, context)

        # Build outcome
        outcome = ExecutionOutcome(
            execution_id=record.id,
            action_id=record.action_id,
            outcome_type=outcome_type,
            severity=self._determine_severity(result),
            summary=self._generate_summary(result),
            details=self._generate_details(result),
            metrics=self._extract_metrics(result),
            observations=self._extract_observations(result),
            surprises=surprises,
            impact_score=impact_score,
            affected_services=record.resources_affected.copy(),
        )

        # Store outcome
        self._outcomes.append(outcome)

        # Update pattern tracking
        self._update_patterns(outcome)

        logger.debug(
            "outcome_collected",
            action_id=record.action_id,
            outcome_type=outcome_type.value,
            impact_score=impact_score,
            surprises=len(surprises),
        )

        return outcome

    def _classify_outcome(self, result: ExecutionResult) -> OutcomeType:
        """Classify the outcome type."""
        if result.success:
            # Check for partial success
            if result.error:
                return OutcomeType.PARTIAL_SUCCESS
            return OutcomeType.SUCCESS
        else:
            # Check if unexpected
            if result.record.error_code == "UNEXPECTED":
                return OutcomeType.UNEXPECTED
            return OutcomeType.FAILURE

    def _calculate_impact(
        self,
        result: ExecutionResult,
        context: Dict[str, Any],
    ) -> float:
        """Calculate impact score (0-1)."""
        score = 0.0

        # Base on success/failure
        if not result.success:
            score += 0.3

        # Changes made impact
        changes = len(result.changes_made)
        score += min(changes * 0.1, 0.3)

        # Resources affected
        resources = len(result.record.resources_affected)
        score += min(resources * 0.05, 0.2)

        # Duration impact (longer = more significant)
        if result.record.duration_ms > 5000:
            score += 0.1
        elif result.record.duration_ms > 1000:
            score += 0.05

        # Risk level from context
        risk = context.get("risk_level", "MEDIUM").upper()
        if risk == "CRITICAL":
            score += 0.3
        elif risk == "HIGH":
            score += 0.2
        elif risk == "MEDIUM":
            score += 0.1

        return min(score, 1.0)

    def _detect_surprises(
        self,
        result: ExecutionResult,
        context: Dict[str, Any],
    ) -> List[str]:
        """Detect unexpected outcomes."""
        surprises = []

        # Unexpected success
        expected_failure = context.get("expected_failure", False)
        if result.success and expected_failure:
            surprises.append("Action succeeded when failure was expected")

        # Unexpected failure
        expected_success = context.get("expected_success", True)
        if not result.success and expected_success:
            surprises.append(f"Action failed unexpectedly: {result.error}")

        # Duration surprise
        expected_duration = context.get("expected_duration_ms", 0)
        if expected_duration > 0:
            actual = result.record.duration_ms
            if actual > expected_duration * 2:
                surprises.append(
                    f"Duration {actual}ms was much longer than expected {expected_duration}ms"
                )
            elif actual < expected_duration * 0.1:
                surprises.append(
                    f"Duration {actual}ms was much shorter than expected {expected_duration}ms"
                )

        # Output surprises
        if result.output:
            for key, value in result.output.items():
                expected = context.get(f"expected_{key}")
                if expected is not None and value != expected:
                    surprises.append(
                        f"Output {key}={value} differs from expected {expected}"
                    )

        return surprises

    def _determine_severity(self, result: ExecutionResult) -> str:
        """Determine severity of outcome."""
        if result.success:
            return "info"
        elif result.record.error_code == "TIMEOUT":
            return "warning"
        elif result.record.error_code == "CRITICAL":
            return "critical"
        else:
            return "error"

    def _generate_summary(self, result: ExecutionResult) -> str:
        """Generate outcome summary."""
        record = result.record
        if result.success:
            changes = len(result.changes_made)
            return f"Successfully executed {record.action_id} with {changes} changes"
        else:
            return f"Failed to execute {record.action_id}: {result.error}"

    def _generate_details(self, result: ExecutionResult) -> str:
        """Generate detailed description."""
        lines = []
        record = result.record

        lines.append(f"Action: {record.action_id}")
        lines.append(f"Status: {record.status.value}")
        lines.append(f"Duration: {record.duration_ms}ms")

        if result.changes_made:
            lines.append("Changes:")
            for change in result.changes_made:
                lines.append(f"  - {change}")

        if result.output:
            lines.append("Output:")
            for key, value in list(result.output.items())[:5]:
                lines.append(f"  {key}: {value}")

        if result.error:
            lines.append(f"Error: {result.error}")

        return "\n".join(lines)

    def _extract_metrics(self, result: ExecutionResult) -> Dict[str, float]:
        """Extract numeric metrics from result."""
        metrics = {}

        metrics["duration_ms"] = float(result.record.duration_ms)
        metrics["success"] = 1.0 if result.success else 0.0
        metrics["changes_count"] = float(len(result.changes_made))

        # Extract numeric values from output
        if result.output:
            for key, value in result.output.items():
                if isinstance(value, (int, float)):
                    metrics[key] = float(value)

        return metrics

    def _extract_observations(self, result: ExecutionResult) -> List[str]:
        """Extract observations from result."""
        observations = []

        record = result.record

        if result.success:
            observations.append(f"Action {record.action_id} completed successfully")
        else:
            observations.append(f"Action {record.action_id} failed: {result.error}")

        if result.changes_made:
            observations.append(f"Made {len(result.changes_made)} changes")

        if record.rollback_available:
            observations.append("Rollback is available if needed")

        if record.duration_ms > 5000:
            observations.append("Execution took longer than 5 seconds")

        return observations

    def _update_patterns(self, outcome: ExecutionOutcome) -> None:
        """Update pattern tracking with new outcome."""
        # Track by action
        action_pattern = f"action:{outcome.action_id}"
        self._known_patterns[action_pattern] = (
            self._known_patterns.get(action_pattern, 0) + 1
        )

        # Track failures
        if outcome.outcome_type in [OutcomeType.FAILURE, OutcomeType.UNEXPECTED]:
            if outcome.action_id not in self._failure_patterns:
                self._failure_patterns[outcome.action_id] = []
            self._failure_patterns[outcome.action_id].append(outcome.summary)

    def analyze(
        self,
        outcome: ExecutionOutcome,
    ) -> OutcomeAnalysis:
        """
        Analyze an outcome for patterns and anomalies.

        Args:
            outcome: Outcome to analyze

        Returns:
            OutcomeAnalysis
        """
        patterns: List[str] = []
        anomalies: List[str] = []
        recommendations: List[str] = []

        # Check for repeated patterns
        action_pattern = f"action:{outcome.action_id}"
        count = self._known_patterns.get(action_pattern, 0)
        if count > 3:
            patterns.append(f"Action {outcome.action_id} has been executed {count} times")

        # Check failure patterns
        if outcome.action_id in self._failure_patterns:
            failures = self._failure_patterns[outcome.action_id]
            if len(failures) >= 2:
                patterns.append(f"Action has failed {len(failures)} times previously")
                recommendations.append("Consider investigating root cause of repeated failures")

        # Detect anomalies
        if outcome.surprises:
            for surprise in outcome.surprises:
                anomalies.append(surprise)

        if outcome.impact_score > 0.7:
            anomalies.append(f"High impact score: {outcome.impact_score:.2f}")
            recommendations.append("Review high-impact action results carefully")

        # Generate recommendations
        if outcome.outcome_type == OutcomeType.FAILURE:
            recommendations.append("Investigate failure cause")
            if "TIMEOUT" in outcome.summary.upper():
                recommendations.append("Consider increasing timeout or optimizing action")

        analysis = OutcomeAnalysis(
            outcome=outcome,
            patterns_detected=patterns,
            anomalies=anomalies,
            recommendations=recommendations,
        )

        self._analyses.append(analysis)

        logger.debug(
            "outcome_analyzed",
            action_id=outcome.action_id,
            patterns=len(patterns),
            anomalies=len(anomalies),
        )

        return analysis

    def collect_batch(
        self,
        results: List[ExecutionResult],
        context: Optional[Dict[str, Any]] = None,
    ) -> BatchOutcomeResult:
        """
        Collect outcomes for multiple executions.

        Args:
            results: List of execution results
            context: Shared context

        Returns:
            BatchOutcomeResult
        """
        import time
        start_time = time.time()
        context = context or {}

        outcomes: List[ExecutionOutcome] = []
        analyses: List[OutcomeAnalysis] = []
        success_count = 0
        failure_count = 0
        surprises_count = 0

        for result in results:
            outcome = self.collect(result, context)
            outcomes.append(outcome)

            analysis = self.analyze(outcome)
            analyses.append(analysis)

            if outcome.outcome_type == OutcomeType.SUCCESS:
                success_count += 1
            elif outcome.outcome_type in [OutcomeType.FAILURE, OutcomeType.UNEXPECTED]:
                failure_count += 1

            surprises_count += len(outcome.surprises)

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "batch_outcomes_collected",
            total=len(results),
            success=success_count,
            failure=failure_count,
            surprises=surprises_count,
            duration_ms=duration_ms,
        )

        return BatchOutcomeResult(
            outcomes=outcomes,
            analyses=analyses,
            total_captured=len(outcomes),
            success_count=success_count,
            failure_count=failure_count,
            surprises_detected=surprises_count,
            duration_ms=duration_ms,
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get collector metrics."""
        total = len(self._outcomes)
        successes = sum(
            1 for o in self._outcomes
            if o.outcome_type == OutcomeType.SUCCESS
        )
        failures = sum(
            1 for o in self._outcomes
            if o.outcome_type in [OutcomeType.FAILURE, OutcomeType.UNEXPECTED]
        )
        surprises = sum(len(o.surprises) for o in self._outcomes)

        avg_impact = 0.0
        if total > 0:
            avg_impact = sum(o.impact_score for o in self._outcomes) / total

        return {
            "total_outcomes": total,
            "successes": successes,
            "failures": failures,
            "surprises_detected": surprises,
            "average_impact_score": avg_impact,
            "patterns_tracked": len(self._known_patterns),
            "failure_patterns": len(self._failure_patterns),
        }


def create_outcome_collector(
    config: Optional[BlackSnakeConfig] = None,
) -> OutcomeCollector:
    """Factory function to create an OutcomeCollector."""
    return OutcomeCollector(config=config)
