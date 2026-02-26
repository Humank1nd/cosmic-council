"""
7th Step Loop Closure Handler for Agent Orchestrator.

Manages the recursion decision from Purple Elephant (WHO) back to
Red Owl (WHY) based on problem resolution status and confidence.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from prometheus_client import Counter, Gauge, Histogram

from .cycle_context import (
    CycleContext,
    create_cycle_context,
    get_current_cycle,
    get_current_cycle_optional,
    set_cycle_context,
)
from .confidence_calibrator import (
    ConfidenceCalibrator,
    ConfidenceDecision,
    ConfidenceThresholds,
    get_calibrator,
)

logger = logging.getLogger(__name__)


# ============== Prometheus Metrics ==============

LOOP_DECISIONS = Counter(
    "loop_closure_decisions_total",
    "Total loop closure decisions",
    ["decision"],
)

RECURSION_DEPTH = Gauge(
    "loop_closure_recursion_depth",
    "Current recursion depth",
    ["cycle_id"],
)

LOOP_LATENCY = Histogram(
    "loop_closure_latency_seconds",
    "Loop closure decision latency",
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0],
)


# ============== Enums ==============

class LoopDecision(Enum):
    """Decisions for 7th step loop closure."""
    COMPLETE = "complete"        # Problem solved, crystallize truth
    RECURSE = "recurse"          # Loop back to Red Owl
    HUMAN_REVIEW = "human_review"  # Escalate to human
    TIMEOUT = "timeout"          # Max recursions reached
    ERROR = "error"              # Error during evaluation


class LoopState(Enum):
    """State of the loop closure process."""
    PENDING = "pending"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    RECURSING = "recursing"
    ESCALATED = "escalated"
    FAILED = "failed"


# ============== Loop Context ==============

@dataclass
class LoopEvaluationContext:
    """Context for loop closure evaluation."""
    cycle_id: str
    problem_id: str
    recursion_depth: int
    stage_confidences: Dict[str, float]
    is_solved: bool
    resolution: Optional[str] = None
    recursion_reason: Optional[str] = None
    emergent_issues: List[str] = field(default_factory=list) # Phase 23: New emergent challenges
    accumulated_insights: Dict[str, Any] = field(default_factory=dict)
    previous_cycles: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoopDecisionResult:
    """Result of loop closure decision."""
    decision: LoopDecision
    reason: str
    new_cycle_id: Optional[str] = None
    enriched_context: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    requires_approval: bool = False
    escalation_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to dict."""
        return {
            "decision": self.decision.value,
            "reason": self.reason,
            "new_cycle_id": self.new_cycle_id,
            "confidence": self.confidence,
            "requires_approval": self.requires_approval,
            "timestamp": self.timestamp.isoformat(),
        }


# ============== Event Callbacks ==============

RecursionCallback = Callable[[str, str, Dict[str, Any]], None]
CompletionCallback = Callable[[str, Dict[str, Any]], None]
EscalationCallback = Callable[[str, Dict[str, Any]], None]


# ============== Loop Closure Handler ==============

class LoopClosureHandler:
    """
    Manages the 7th step recursion from Purple Elephant to Red Owl.

    Features:
    - Evaluates cycle completion based on solution status and confidence
    - Triggers recursion with enriched context
    - Handles max recursion limits
    - Supports approval workflows for deep recursion
    - Emits events for external integration
    """

    def __init__(
        self,
        calibrator: Optional[ConfidenceCalibrator] = None,
        max_recursions: int = 5,
        approval_threshold: int = 3,
        ai_agent: Optional[Any] = None,
    ):
        self._calibrator = calibrator
        self.max_recursions = max_recursions
        self.approval_threshold = approval_threshold
        self.ai_agent = ai_agent

        # Event callbacks
        self._on_recursion: List[RecursionCallback] = []
        self._on_completion: List[CompletionCallback] = []
        self._on_escalation: List[EscalationCallback] = []

        # State tracking
        self._loop_states: Dict[str, LoopState] = {}

    def _get_calibrator(self) -> ConfidenceCalibrator:
        """Get or create confidence calibrator."""
        if self._calibrator is None:
            self._calibrator = get_calibrator()
        return self._calibrator

    # ============== AI Enhancement ==============

    async def generate_recursion_guidance(
        self,
        context: LoopEvaluationContext,
    ) -> Dict[str, Any]:
        """
        Generate AI-powered guidance for the next recursion cycle.
        Phase 23 enhancement: Summarizes feedback into research queries.
        """
        if not self.ai_agent:
            return {
                "summary": "No AI guidance available.",
                "research_queries": [context.recursion_reason or "Investigate previous cycle failures."]
            }

        try:
            # Prepare context for LLM
            prompt_context = {
                "problem_id": context.problem_id,
                "recursion_depth": context.recursion_depth,
                "is_solved": context.is_solved,
                "recursion_reason": context.recursion_reason,
                "accumulated_insights": context.accumulated_insights,
                "previous_resolution_attempt": context.resolution,
                "emergent_issues": context.emergent_issues
            }

            # Generate summary and new research queries using the agent
            # Instruct the agent to specifically look for self-updating logic 
            # and emergent problems.
            ai_response = await self.ai_agent.generate_response(
                "loop_recursion_guidance",
                {
                    **prompt_context,
                    "instruction": (
                        "Analyze the feedback loop results. Identify core bottlenecks and "
                        "emergent issues. Generate a list of prioritized research queries "
                        "for the next Red Owl stage to automate the refinement process."
                    )
                }
            )

            # Extract research queries from AI content
            content = ai_response.content
            queries = self._parse_research_queries(content)
            extracted_emergent = self._extract_emergent_issues(content)

            return {
                "summary": content,
                "research_queries": queries,
                "identified_emergent_issues": extracted_emergent,
                "ai_confidence": ai_response.confidence_score,
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to generate recursion guidance: {e}")
            return {
                "summary": f"Error generating guidance: {str(e)}",
                "research_queries": [context.recursion_reason or "Manual review required."]
            }

    def _parse_research_queries(self, content: str) -> List[str]:
        """Extract research queries from AI-generated content."""
        queries = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            # Look for lines that look like questions or numbered lists
            if line.endswith('?') or (line and line[0].isdigit() and '.' in line[:3]):
                clean_query = line.lstrip('0123456789. ').strip()
                if clean_query:
                    queries.append(clean_query)
        
        # Fallback if no structured queries found
        if not queries:
            queries = [content[:200] + "..."]
        
        return queries

    def _extract_emergent_issues(self, content: str) -> List[str]:
        """Extract emergent issues from AI-generated content."""
        issues = []
        if "EMERGENT:" in content:
            section = content.split("EMERGENT:")[1].split("\n\n")[0]
            for line in section.split('\n'):
                line = line.strip().lstrip('-•* ')
                if line:
                    issues.append(line)
        return issues

    # ============== Event Registration ==============

    def on_recursion(self, callback: RecursionCallback) -> None:
        """Register callback for recursion events."""
        self._on_recursion.append(callback)

    def on_completion(self, callback: CompletionCallback) -> None:
        """Register callback for completion events."""
        self._on_completion.append(callback)

    def on_escalation(self, callback: EscalationCallback) -> None:
        """Register callback for escalation events."""
        self._on_escalation.append(callback)

    # ============== Main Evaluation ==============

    async def evaluate_closure(
        self,
        context: LoopEvaluationContext,
    ) -> LoopDecisionResult:
        """
        Evaluate whether the cycle should close or recurse.

        This is the main entry point called after Purple Elephant completes.

        Args:
            context: Loop evaluation context with all cycle data

        Returns:
            LoopDecisionResult with decision and any new cycle info
        """
        with LOOP_LATENCY.time():
            self._loop_states[context.cycle_id] = LoopState.EVALUATING
            RECURSION_DEPTH.labels(cycle_id=context.cycle_id).set(context.recursion_depth)

            try:
                result = await self._evaluate_internal(context)

                # Update state based on decision
                if result.decision == LoopDecision.COMPLETE:
                    self._loop_states[context.cycle_id] = LoopState.COMPLETED
                    await self._emit_completion(context.cycle_id, context.stage_confidences)

                elif result.decision == LoopDecision.RECURSE:
                    self._loop_states[context.cycle_id] = LoopState.RECURSING
                    
                    # Generate AI-powered guidance for the next cycle
                    ai_guidance = await self.generate_recursion_guidance(context)
                    if result.enriched_context:
                        result.enriched_context["ai_guidance"] = ai_guidance
                        # Automatically inject new research queries for Red Owl
                        result.enriched_context["next_cycle_queries"] = ai_guidance.get("research_queries", [])

                    await self._emit_recursion(
                        context.cycle_id,
                        result.new_cycle_id or "",
                        result.enriched_context or {},
                    )

                elif result.decision in (LoopDecision.HUMAN_REVIEW, LoopDecision.TIMEOUT):
                    self._loop_states[context.cycle_id] = LoopState.ESCALATED
                    await self._emit_escalation(context.cycle_id, {
                        "decision": result.decision.value,
                        "reason": result.reason,
                        "recursion_depth": context.recursion_depth,
                        "stage_confidences": context.stage_confidences,
                    })

                LOOP_DECISIONS.labels(decision=result.decision.value).inc()
                return result

            except Exception as e:
                logger.error(f"Loop evaluation failed: {e}")
                self._loop_states[context.cycle_id] = LoopState.FAILED
                LOOP_DECISIONS.labels(decision="error").inc()
                return LoopDecisionResult(
                    decision=LoopDecision.ERROR,
                    reason=str(e),
                )

    async def _evaluate_internal(
        self,
        context: LoopEvaluationContext,
    ) -> LoopDecisionResult:
        """Internal evaluation logic."""
        calibrator = self._get_calibrator()

        # Get calibrator's cycle completion decision
        decision, reason = calibrator.evaluate_cycle_completion(
            stage_confidences=context.stage_confidences,
            is_solved=context.is_solved,
            recursion_depth=context.recursion_depth,
        )

        # Check max recursions
        if context.recursion_depth >= self.max_recursions:
            return LoopDecisionResult(
                decision=LoopDecision.TIMEOUT,
                reason=f"Max recursions ({self.max_recursions}) reached. {reason}",
                confidence=self._calculate_overall_confidence(context.stage_confidences),
                requires_approval=True,
                escalation_data={
                    "recursion_depth": context.recursion_depth,
                    "previous_cycles": context.previous_cycles,
                },
            )

        # Map calibrator decision to loop decision
        if decision == ConfidenceDecision.PROCEED:
            return LoopDecisionResult(
                decision=LoopDecision.COMPLETE,
                reason=reason,
                confidence=self._calculate_overall_confidence(context.stage_confidences),
            )

        elif decision == ConfidenceDecision.RECURSE:
            # Check if we need approval for deep recursion
            requires_approval = context.recursion_depth >= self.approval_threshold

            # Create enriched context for new cycle
            enriched_context = self._build_enriched_context(context)

            # Generate new cycle ID
            new_cycle_id = str(uuid4())

            return LoopDecisionResult(
                decision=LoopDecision.RECURSE,
                reason=context.recursion_reason or reason,
                new_cycle_id=new_cycle_id,
                enriched_context=enriched_context,
                confidence=self._calculate_overall_confidence(context.stage_confidences),
                requires_approval=requires_approval,
            )

        else:  # HUMAN_REVIEW
            return LoopDecisionResult(
                decision=LoopDecision.HUMAN_REVIEW,
                reason=reason,
                confidence=self._calculate_overall_confidence(context.stage_confidences),
                requires_approval=True,
                escalation_data={
                    "stage_confidences": context.stage_confidences,
                    "accumulated_insights": context.accumulated_insights,
                },
            )

    def _calculate_overall_confidence(
        self,
        stage_confidences: Dict[str, float],
    ) -> float:
        """Calculate weighted overall confidence."""
        if not stage_confidences:
            return 0.0

        # WHO (Purple Elephant) has higher weight for final decision
        weights = {
            "why": 1.0,
            "how": 1.0,
            "what": 1.0,
            "when": 0.8,
            "where": 0.8,
            "who": 1.5,  # Higher weight for final decision
        }

        total_weight = 0.0
        weighted_sum = 0.0

        for stage, confidence in stage_confidences.items():
            stage_lower = stage.lower()
            weight = weights.get(stage_lower, 1.0)
            weighted_sum += confidence * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _build_enriched_context(
        self,
        context: LoopEvaluationContext,
    ) -> Dict[str, Any]:
        """Build enriched context for recursion."""
        return {
            "previous_cycle_id": context.cycle_id,
            "recursion_depth": context.recursion_depth + 1,
            "previous_confidences": context.stage_confidences.copy(),
            "accumulated_insights": context.accumulated_insights,
            "previous_resolution_attempt": context.resolution,
            "recursion_reason": context.recursion_reason,
            "previous_cycles": [
                *context.previous_cycles,
                context.cycle_id,
            ],
            "metadata": context.metadata,
        }

    # ============== Recursion Trigger ==============

    async def trigger_recursion(
        self,
        current_context: CycleContext,
        reason: str,
        accumulated_insights: Optional[Dict[str, Any]] = None,
    ) -> CycleContext:
        """
        Trigger recursion and create new cycle context.

        Args:
            current_context: Current cycle context
            reason: Reason for recursion
            accumulated_insights: Insights to carry forward

        Returns:
            New CycleContext for recursed cycle
        """
        # Create recursion context
        new_context = current_context.create_recursion_context(reason)

        # Add accumulated insights to metadata
        if accumulated_insights:
            new_context.metadata["accumulated_insights"] = accumulated_insights

        logger.info(
            f"Triggered recursion: {current_context.cycle_id} -> {new_context.cycle_id} "
            f"(depth {new_context.recursion_depth})"
        )

        # Emit recursion event
        await self._emit_recursion(
            current_context.cycle_id,
            new_context.cycle_id,
            {"reason": reason, "depth": new_context.recursion_depth},
        )

        return new_context

    # ============== Event Emission ==============

    async def _emit_recursion(
        self,
        old_cycle_id: str,
        new_cycle_id: str,
        context: Dict[str, Any],
    ) -> None:
        """Emit recursion event to callbacks."""
        for callback in self._on_recursion:
            try:
                callback(old_cycle_id, new_cycle_id, context)
            except Exception as e:
                logger.error(f"Recursion callback error: {e}")

    async def _emit_completion(
        self,
        cycle_id: str,
        confidences: Dict[str, float],
    ) -> None:
        """Emit completion event to callbacks."""
        for callback in self._on_completion:
            try:
                callback(cycle_id, confidences)
            except Exception as e:
                logger.error(f"Completion callback error: {e}")

    async def _emit_escalation(
        self,
        cycle_id: str,
        data: Dict[str, Any],
    ) -> None:
        """Emit escalation event to callbacks."""
        for callback in self._on_escalation:
            try:
                callback(cycle_id, data)
            except Exception as e:
                logger.error(f"Escalation callback error: {e}")

    # ============== State Queries ==============

    def get_loop_state(self, cycle_id: str) -> Optional[LoopState]:
        """Get current loop state for a cycle."""
        return self._loop_states.get(cycle_id)

    def clear_state(self, cycle_id: str) -> None:
        """Clear loop state for a cycle."""
        self._loop_states.pop(cycle_id, None)
        RECURSION_DEPTH.remove(cycle_id)


# ============== Factory Functions ==============

_default_handler: Optional[LoopClosureHandler] = None


def get_loop_handler() -> LoopClosureHandler:
    """Get the global loop closure handler."""
    global _default_handler
    if _default_handler is None:
        _default_handler = LoopClosureHandler()
    return _default_handler


def set_loop_handler(handler: LoopClosureHandler) -> None:
    """Set the global loop closure handler."""
    global _default_handler
    _default_handler = handler


def create_loop_handler(
    max_recursions: int = 5,
    approval_threshold: int = 3,
    calibrator: Optional[ConfidenceCalibrator] = None,
) -> LoopClosureHandler:
    """
    Create a new loop closure handler.

    Args:
        max_recursions: Maximum allowed recursions
        approval_threshold: Recursion depth requiring approval
        calibrator: Optional pre-configured calibrator

    Returns:
        Configured LoopClosureHandler
    """
    return LoopClosureHandler(
        calibrator=calibrator,
        max_recursions=max_recursions,
        approval_threshold=approval_threshold,
    )


# ============== Convenience Functions ==============

async def evaluate_and_decide(
    cycle_id: str,
    problem_id: str,
    stage_confidences: Dict[str, float],
    is_solved: bool,
    recursion_depth: int = 0,
    resolution: Optional[str] = None,
    recursion_reason: Optional[str] = None,
) -> LoopDecisionResult:
    """
    Convenience function to evaluate loop closure.

    Args:
        cycle_id: Current cycle ID
        problem_id: Problem ID
        stage_confidences: Confidence scores from all stages
        is_solved: Whether agent determined problem is solved
        recursion_depth: Current recursion depth
        resolution: Optional resolution text
        recursion_reason: Optional reason for potential recursion

    Returns:
        LoopDecisionResult with decision
    """
    handler = get_loop_handler()
    context = LoopEvaluationContext(
        cycle_id=cycle_id,
        problem_id=problem_id,
        recursion_depth=recursion_depth,
        stage_confidences=stage_confidences,
        is_solved=is_solved,
        resolution=resolution,
        recursion_reason=recursion_reason,
    )
    return await handler.evaluate_closure(context)
