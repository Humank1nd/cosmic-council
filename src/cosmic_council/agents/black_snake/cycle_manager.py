"""
BLACK SNAKE - Cycle Manager.

Manages the recursive cycle, feeding insights back to Red Owl.
This implements Criterion 3: Cycle recursion.

The Ouroboros completes - each ending is a new beginning.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime

import structlog

from .models import (
    ExecutionRecord,
    ExecutionOutcome,
    CycleInsight,
    CycleState,
    CyclePhase,
    ExecutionPlan,
    InsightType,
    OutcomeType,
    BlackSnakeConfig,
)
from .outcome_collector import OutcomeAnalysis

logger = structlog.get_logger(__name__)


@dataclass
class InsightSeed:
    """Seed for generating new cycle insights."""
    outcome: ExecutionOutcome
    analysis: OutcomeAnalysis
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CycleFeedback:
    """Feedback prepared for Red Owl."""
    cycle_id: str
    insights: List[CycleInsight]
    new_questions: List[str]
    hypotheses_to_test: List[str]
    evidence_collected: List[str]
    priority: str = "medium"
    urgency: str = "normal"
    should_continue: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CycleCompletionResult:
    """Result of completing a cycle."""
    cycle_state: CycleState
    feedback: CycleFeedback
    next_cycle_initiated: bool = False
    next_cycle_id: Optional[str] = None
    duration_ms: int = 0


# Type for Red Owl callback
RedOwlCallback = Callable[[CycleFeedback], "asyncio.Future[str]"]


class CycleManager:
    """
    Manages the recursive cycle and feeds insights back to Red Owl.

    Criterion 3: Insights feed back to initiate new inquiry.

    The Ouroboros - the serpent consuming its tail.
    Each ending is a new beginning.
    """

    def __init__(
        self,
        config: Optional[BlackSnakeConfig] = None,
        red_owl_callback: Optional[RedOwlCallback] = None,
    ):
        """
        Initialize the cycle manager.

        Args:
            config: Configuration
            red_owl_callback: Callback to initiate new Red Owl inquiry
        """
        self.config = config or BlackSnakeConfig()
        self._red_owl_callback = red_owl_callback

        # Cycle tracking
        self._active_cycles: Dict[str, CycleState] = {}
        self._completed_cycles: List[CycleState] = []

        # Insight generation
        self._insight_generators: List[Callable[[InsightSeed], Optional[CycleInsight]]] = []
        self._register_default_generators()

        logger.info(
            "cycle_manager_initialized",
            auto_feed_forward=self.config.auto_feed_forward,
        )

    def _register_default_generators(self):
        """Register default insight generators."""
        self._insight_generators.extend([
            self._generate_root_cause_insight,
            self._generate_pattern_insight,
            self._generate_anomaly_insight,
            self._generate_improvement_insight,
        ])

    def start_cycle(
        self,
        cycle_id: str,
        inquiry_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CycleState:
        """
        Start tracking a new cycle.

        Args:
            cycle_id: Unique cycle identifier
            inquiry_id: Red Owl inquiry that initiated this cycle
            metadata: Additional metadata

        Returns:
            CycleState
        """
        cycle_number = len(self._completed_cycles) + len(self._active_cycles) + 1

        state = CycleState(
            id=cycle_id,
            cycle_number=cycle_number,
            current_phase=CyclePhase.INQUIRY,
            inquiry_id=inquiry_id,
            started_at=datetime.utcnow(),
            metadata=metadata or {},
        )

        self._active_cycles[cycle_id] = state

        logger.info(
            "cycle_started",
            cycle_id=cycle_id,
            cycle_number=cycle_number,
        )

        return state

    def update_phase(
        self,
        cycle_id: str,
        phase: CyclePhase,
        artifact_id: Optional[str] = None,
    ) -> CycleState:
        """
        Update the current phase of a cycle.

        Args:
            cycle_id: Cycle identifier
            phase: New phase
            artifact_id: ID of artifact produced in this phase

        Returns:
            Updated CycleState
        """
        state = self._active_cycles.get(cycle_id)
        if not state:
            raise ValueError(f"Cycle not found: {cycle_id}")

        # Record phase transition
        state.phase_history.append({
            "from_phase": state.current_phase.value,
            "to_phase": phase.value,
            "timestamp": datetime.utcnow().isoformat(),
            "artifact_id": artifact_id,
        })

        state.current_phase = phase

        # Store artifact reference
        if artifact_id:
            if phase == CyclePhase.PLANNING:
                state.plan_id = artifact_id
            elif phase == CyclePhase.CREATION:
                state.specification_id = artifact_id
            elif phase == CyclePhase.SCHEDULING:
                state.schedule_id = artifact_id
            elif phase == CyclePhase.LOCATION:
                state.location_plan_id = artifact_id
            elif phase == CyclePhase.ASSIGNMENT:
                state.responsibility_plan_id = artifact_id

        logger.debug(
            "cycle_phase_updated",
            cycle_id=cycle_id,
            phase=phase.value,
        )

        return state

    def record_executions(
        self,
        cycle_id: str,
        executions: List[ExecutionRecord],
        outcomes: List[ExecutionOutcome],
    ) -> CycleState:
        """
        Record execution results for a cycle.

        Args:
            cycle_id: Cycle identifier
            executions: Execution records
            outcomes: Execution outcomes

        Returns:
            Updated CycleState
        """
        state = self._active_cycles.get(cycle_id)
        if not state:
            raise ValueError(f"Cycle not found: {cycle_id}")

        state.executions.extend(executions)
        state.outcomes.extend(outcomes)

        # Update metrics
        state.actions_executed += len(executions)
        state.actions_succeeded += sum(1 for e in executions if e.success)
        state.actions_failed += sum(1 for e in executions if not e.success)

        state.current_phase = CyclePhase.EXECUTION

        logger.info(
            "executions_recorded",
            cycle_id=cycle_id,
            count=len(executions),
            succeeded=state.actions_succeeded,
            failed=state.actions_failed,
        )

        return state

    def generate_insights(
        self,
        outcomes: List[ExecutionOutcome],
        analyses: List[OutcomeAnalysis],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[CycleInsight]:
        """
        Generate insights from execution outcomes.

        Args:
            outcomes: Execution outcomes
            analyses: Outcome analyses
            context: Additional context

        Returns:
            List of generated insights
        """
        context = context or {}
        insights: List[CycleInsight] = []

        # Create seeds for insight generation
        for outcome, analysis in zip(outcomes, analyses):
            seed = InsightSeed(
                outcome=outcome,
                analysis=analysis,
                context=context,
            )

            # Run through all generators
            for generator in self._insight_generators:
                try:
                    insight = generator(seed)
                    if insight and insight.confidence >= self.config.min_confidence_threshold:
                        insights.append(insight)
                except Exception as e:
                    logger.warning(
                        "insight_generation_failed",
                        generator=generator.__name__,
                        error=str(e),
                    )

        # Limit insights
        if len(insights) > self.config.max_insights_per_cycle:
            # Sort by confidence and take top N
            insights.sort(key=lambda i: i.confidence, reverse=True)
            insights = insights[:self.config.max_insights_per_cycle]

        logger.info(
            "insights_generated",
            count=len(insights),
        )

        return insights

    def _generate_root_cause_insight(self, seed: InsightSeed) -> Optional[CycleInsight]:
        """Generate root cause insights."""
        outcome = seed.outcome
        analysis = seed.analysis

        if outcome.outcome_type == OutcomeType.SUCCESS:
            # Successful execution may confirm root cause
            if "root_cause" in seed.context:
                return CycleInsight(
                    execution_ids=[outcome.execution_id],
                    insight_type=InsightType.ROOT_CAUSE_CONFIRMED,
                    title=f"Root cause confirmed for {outcome.action_id}",
                    description=f"Action succeeded, confirming hypothesis: {seed.context.get('root_cause')}",
                    confidence=0.8,
                    new_questions=[],
                    hypotheses_to_test=[],
                    evidence_needed=[],
                    priority="high",
                )

        elif outcome.outcome_type == OutcomeType.FAILURE:
            # Failure may invalidate root cause or reveal new one
            if "root_cause" in seed.context:
                return CycleInsight(
                    execution_ids=[outcome.execution_id],
                    insight_type=InsightType.ROOT_CAUSE_INVALIDATED,
                    title=f"Root cause invalidated for {outcome.action_id}",
                    description=f"Action failed: {outcome.summary}. Hypothesis may be incorrect.",
                    confidence=0.7,
                    new_questions=[
                        f"Why did {outcome.action_id} fail despite addressing the hypothesized root cause?",
                        "Are there other contributing factors we haven't considered?",
                    ],
                    hypotheses_to_test=[
                        "The root cause may be more complex than initially thought",
                        "There may be multiple interacting root causes",
                    ],
                    evidence_needed=[
                        "Additional diagnostic data from failed execution",
                        "Comparison with successful executions of similar actions",
                    ],
                    priority="high",
                    urgency="soon",
                )

        return None

    def _generate_pattern_insight(self, seed: InsightSeed) -> Optional[CycleInsight]:
        """Generate pattern insights."""
        analysis = seed.analysis

        if analysis.patterns_detected:
            # Repeated patterns warrant investigation
            pattern_str = "; ".join(analysis.patterns_detected[:3])
            return CycleInsight(
                execution_ids=[seed.outcome.execution_id],
                insight_type=InsightType.PATTERN_DETECTED,
                title=f"Pattern detected in {seed.outcome.action_id}",
                description=f"Patterns: {pattern_str}",
                confidence=0.6,
                new_questions=[
                    f"Why is this pattern recurring?",
                    "Is this pattern indicative of a systemic issue?",
                ],
                hypotheses_to_test=[
                    "The pattern reflects a structural characteristic of the system",
                    "The pattern is caused by external factors",
                ],
                evidence_needed=[
                    "Historical data on similar patterns",
                    "Correlation with system changes or events",
                ],
                priority="medium",
                related_patterns=analysis.patterns_detected,
            )

        return None

    def _generate_anomaly_insight(self, seed: InsightSeed) -> Optional[CycleInsight]:
        """Generate anomaly insights."""
        analysis = seed.analysis
        outcome = seed.outcome

        if analysis.anomalies or outcome.surprises:
            anomalies = analysis.anomalies + outcome.surprises
            anomaly_str = "; ".join(anomalies[:3])

            return CycleInsight(
                execution_ids=[outcome.execution_id],
                insight_type=InsightType.ANOMALY_DISCOVERED,
                title=f"Anomaly discovered in {outcome.action_id}",
                description=f"Unexpected observations: {anomaly_str}",
                confidence=0.7,
                new_questions=[
                    "What caused this unexpected behavior?",
                    "Does this anomaly indicate a larger issue?",
                ],
                hypotheses_to_test=[
                    "The anomaly is a symptom of an unidentified problem",
                    "The anomaly is a one-time occurrence due to transient conditions",
                ],
                evidence_needed=[
                    "Logs and metrics from the time of anomaly",
                    "Comparison with baseline behavior",
                ],
                priority="high" if outcome.impact_score > 0.5 else "medium",
                urgency="soon" if outcome.impact_score > 0.7 else "normal",
            )

        return None

    def _generate_improvement_insight(self, seed: InsightSeed) -> Optional[CycleInsight]:
        """Generate process improvement insights."""
        analysis = seed.analysis

        if analysis.recommendations:
            rec_str = "; ".join(analysis.recommendations[:3])

            return CycleInsight(
                execution_ids=[seed.outcome.execution_id],
                insight_type=InsightType.PROCESS_IMPROVEMENT,
                title=f"Improvement opportunity for {seed.outcome.action_id}",
                description=f"Recommendations: {rec_str}",
                confidence=0.5,
                new_questions=[
                    "How can we implement these improvements?",
                    "What resources are needed?",
                ],
                hypotheses_to_test=[
                    "Implementing these changes will improve outcomes",
                ],
                evidence_needed=[
                    "Baseline metrics before improvement",
                    "Success criteria for improvement",
                ],
                priority="low",
            )

        return None

    def prepare_feedback(
        self,
        cycle_id: str,
        insights: List[CycleInsight],
    ) -> CycleFeedback:
        """
        Prepare feedback for Red Owl.

        Args:
            cycle_id: Cycle identifier
            insights: Generated insights

        Returns:
            CycleFeedback ready for Red Owl
        """
        state = self._active_cycles.get(cycle_id)

        # Aggregate questions and hypotheses
        all_questions: List[str] = []
        all_hypotheses: List[str] = []
        all_evidence: List[str] = []

        highest_priority = "low"
        highest_urgency = "normal"

        priority_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        urgency_order = {"normal": 0, "soon": 1, "immediate": 2}

        for insight in insights:
            all_questions.extend(insight.new_questions)
            all_hypotheses.extend(insight.hypotheses_to_test)
            all_evidence.extend(insight.evidence_needed)

            if priority_order.get(insight.priority, 0) > priority_order.get(highest_priority, 0):
                highest_priority = insight.priority
            if urgency_order.get(insight.urgency, 0) > urgency_order.get(highest_urgency, 0):
                highest_urgency = insight.urgency

        # Deduplicate
        all_questions = list(dict.fromkeys(all_questions))
        all_hypotheses = list(dict.fromkeys(all_hypotheses))
        all_evidence = list(dict.fromkeys(all_evidence))

        # Determine if cycle should continue
        should_continue = True
        if state:
            success_rate = state.success_rate
            should_continue = success_rate >= self.config.min_success_rate_for_recursion

        feedback = CycleFeedback(
            cycle_id=cycle_id,
            insights=insights,
            new_questions=all_questions[:10],  # Limit
            hypotheses_to_test=all_hypotheses[:5],
            evidence_collected=all_evidence[:10],
            priority=highest_priority,
            urgency=highest_urgency,
            should_continue=should_continue and bool(all_questions),
            metadata={
                "success_rate": state.success_rate if state else 0.0,
                "total_insights": len(insights),
                "cycle_number": state.cycle_number if state else 0,
            },
        )

        logger.info(
            "feedback_prepared",
            cycle_id=cycle_id,
            questions=len(all_questions),
            hypotheses=len(all_hypotheses),
            should_continue=should_continue,
        )

        return feedback

    async def complete_cycle(
        self,
        cycle_id: str,
        insights: List[CycleInsight],
    ) -> CycleCompletionResult:
        """
        Complete a cycle and optionally initiate the next one.

        Args:
            cycle_id: Cycle identifier
            insights: Generated insights

        Returns:
            CycleCompletionResult
        """
        start_time = time.time()

        state = self._active_cycles.get(cycle_id)
        if not state:
            raise ValueError(f"Cycle not found: {cycle_id}")

        # Store insights
        state.insights.extend(insights)

        # Prepare feedback for Red Owl
        feedback = self.prepare_feedback(cycle_id, insights)

        # Update state
        state.current_phase = CyclePhase.RECURSION
        state.completed_at = datetime.utcnow()
        state.duration_ms = int(
            (state.completed_at - state.started_at).total_seconds() * 1000
        ) if state.started_at else 0

        # Check if we should feed forward
        next_cycle_initiated = False
        next_cycle_id = None

        if (
            self.config.auto_feed_forward
            and feedback.should_continue
            and self._red_owl_callback
            and not self.config.require_human_review
        ):
            try:
                next_cycle_id = await self._red_owl_callback(feedback)
                next_cycle_initiated = True
                state.next_cycle_id = next_cycle_id
                state.feeds_forward = True

                logger.info(
                    "cycle_fed_forward",
                    cycle_id=cycle_id,
                    next_cycle_id=next_cycle_id,
                )
            except Exception as e:
                logger.error(
                    "cycle_feed_forward_failed",
                    cycle_id=cycle_id,
                    error=str(e),
                )

        # Move to completed
        self._active_cycles.pop(cycle_id, None)
        self._completed_cycles.append(state)

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "cycle_completed",
            cycle_id=cycle_id,
            cycle_number=state.cycle_number,
            success_rate=state.success_rate,
            insights=len(insights),
            feeds_forward=state.feeds_forward,
        )

        return CycleCompletionResult(
            cycle_state=state,
            feedback=feedback,
            next_cycle_initiated=next_cycle_initiated,
            next_cycle_id=next_cycle_id,
            duration_ms=duration_ms,
        )

    def set_red_owl_callback(self, callback: RedOwlCallback) -> None:
        """Set the callback for initiating new Red Owl inquiries."""
        self._red_owl_callback = callback

    def add_insight_generator(
        self,
        generator: Callable[[InsightSeed], Optional[CycleInsight]],
    ) -> None:
        """Add a custom insight generator."""
        self._insight_generators.append(generator)

    def get_cycle_state(self, cycle_id: str) -> Optional[CycleState]:
        """Get current state of a cycle."""
        return self._active_cycles.get(cycle_id)

    def get_metrics(self) -> Dict[str, Any]:
        """Get cycle manager metrics."""
        total_cycles = len(self._completed_cycles)
        fed_forward = sum(1 for c in self._completed_cycles if c.feeds_forward)

        avg_success_rate = 0.0
        avg_insights = 0.0
        if total_cycles > 0:
            avg_success_rate = sum(c.success_rate for c in self._completed_cycles) / total_cycles
            avg_insights = sum(len(c.insights) for c in self._completed_cycles) / total_cycles

        return {
            "total_cycles_completed": total_cycles,
            "active_cycles": len(self._active_cycles),
            "cycles_fed_forward": fed_forward,
            "feed_forward_rate": fed_forward / total_cycles if total_cycles > 0 else 0.0,
            "average_success_rate": avg_success_rate,
            "average_insights_per_cycle": avg_insights,
        }


def create_cycle_manager(
    config: Optional[BlackSnakeConfig] = None,
    red_owl_callback: Optional[RedOwlCallback] = None,
) -> CycleManager:
    """Factory function to create a CycleManager."""
    return CycleManager(
        config=config,
        red_owl_callback=red_owl_callback,
    )
