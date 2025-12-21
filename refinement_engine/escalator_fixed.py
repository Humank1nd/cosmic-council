"""
Cosmic Council Refinement Engine - Fixed Escalator Function
Properly implements the decision logic for staying, refining, or resolving.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
import logging
from datetime import datetime, timezone
import math

try:
    from .layers import LayerDefinitions, LayerRefinementEngine
except ImportError:
    # For testing
    from layers import LayerDefinitions, LayerRefinementEngine


class EscalatorAction(Enum):
    """Possible actions the escalator can take."""
    STAY = "stay"
    REFINE = "refine"
    RESOLVE = "resolve"


@dataclass
class SolutionCandidate:
    """Represents a solution candidate with evaluation metrics."""
    solution_text: str
    confidence_score: float
    completeness_score: float
    novelty_score: float = 0.0
    alignment_score: float = 1.0
    net_benefit_score: float = 0.0
    evaluation: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class EscalatorDecision:
    """Represents the escalator's decision."""
    action: EscalatorAction
    reason: str
    from_layer: Optional[str] = None
    to_layer: Optional[str] = None
    refined_question: Optional[str] = None
    metrics: Dict[str, Any] = None
    timestamp: datetime = None
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class EscalatorEngine:
    """
    Fixed escalator function with proper decision logic.
    
    This implementation addresses the critical flaws in the original:
    1. Proper cost-benefit analysis
    2. Learning from previous attempts
    3. Time and resource constraints
    4. Quality improvement tracking
    5. Fallback mechanisms
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the escalator engine.
        
        Args:
            config: Configuration dictionary with thresholds and policies
        """
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        
        # Track decision history for learning
        self.decision_history: List[Dict[str, Any]] = []
        
        # Track performance trends
        self.performance_trends: Dict[str, List[float]] = {
            "confidence": [],
            "completeness": [],
            "cost": [],
            "latency": []
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the escalator."""
        return {
            # Quality thresholds
            "confidence_threshold": 0.85,
            "completeness_threshold": 0.80,
            "novelty_threshold": 0.20,
            "alignment_threshold": 0.90,
            "net_benefit_threshold": 0.0,
            
            # Resource limits
            "max_revolutions_per_layer": 3,
            "max_total_cost_usd": 1000.0,
            "max_total_latency_ms": 300000,  # 5 minutes
            "max_total_iterations": 50,
            
            # Learning parameters
            "improvement_threshold": 0.05,  # Minimum improvement to continue
            "stagnation_threshold": 3,  # Max iterations without improvement
            "cost_benefit_ratio_threshold": 0.1,  # Min benefit per dollar spent
            
            # Escalation parameters
            "force_refine_after_revolutions": 2,
            "force_resolve_after_cost": 500.0,
            "force_resolve_after_time": 180000,  # 3 minutes
            
            # Quality gates
            "min_confidence_for_resolution": 0.70,
            "min_completeness_for_resolution": 0.65,
            "min_alignment_for_resolution": 0.80
        }
    
    def decide(
        self,
        problem_id: str,
        current_layer: str,
        solution_candidate: SolutionCandidate,
        layer_metrics: Dict[str, Any],
        problem_context: Optional[Dict[str, Any]] = None
    ) -> EscalatorDecision:
        """
        Make a decision about the next step for a problem.
        
        This is the core decision-making engine that determines the next step
        in the problem-solving process based on solution quality and constraints.
        """
        self.logger.info(f"Making escalator decision for problem {problem_id} at layer {current_layer}")
        
        # Get layer-specific policies
        layer_capability = LayerDefinitions.get_layer(current_layer)
        if not layer_capability:
            return EscalatorDecision(
                action=EscalatorAction.RESOLVE,
                reason=f"Invalid layer: {current_layer}",
                from_layer=current_layer,
                confidence=0.0
            )
        
        # Calculate decision confidence
        decision_confidence = self._calculate_decision_confidence(
            solution_candidate, layer_metrics, layer_capability
        )
        
        # Check hard constraints first
        hard_constraint_decision = self._check_hard_constraints(
            problem_id, current_layer, layer_metrics, problem_context
        )
        if hard_constraint_decision:
            hard_constraint_decision.confidence = decision_confidence
            return hard_constraint_decision
        
        # Check if solution meets resolution criteria
        if self._meets_resolution_criteria(solution_candidate, layer_capability):
            decision = EscalatorDecision(
                action=EscalatorAction.RESOLVE,
                reason="Solution meets all quality thresholds and constraints",
                from_layer=current_layer,
                metrics=layer_metrics,
                confidence=decision_confidence
            )
            self._record_decision(problem_id, decision, layer_metrics)
            return decision
        
        # Check if we should refine to a deeper layer
        refine_decision = self._should_refine(
            problem_id, current_layer, solution_candidate, layer_metrics, layer_capability
        )
        if refine_decision:
            refine_decision.confidence = decision_confidence
            self._record_decision(problem_id, refine_decision, layer_metrics)
            return refine_decision
        
        # Check if we should stay at the current layer
        stay_decision = self._should_stay(
            problem_id, current_layer, solution_candidate, layer_metrics, layer_capability
        )
        if stay_decision:
            stay_decision.confidence = decision_confidence
            self._record_decision(problem_id, stay_decision, layer_metrics)
            return stay_decision
        
        # Default: force resolution with best available solution
        decision = EscalatorDecision(
            action=EscalatorAction.RESOLVE,
            reason="Unable to make progress - forcing resolution with best available solution",
            from_layer=current_layer,
            metrics=layer_metrics,
            confidence=decision_confidence
        )
        self._record_decision(problem_id, decision, layer_metrics)
        return decision
    
    def _check_hard_constraints(
        self,
        problem_id: str,
        current_layer: str,
        layer_metrics: Dict[str, Any],
        problem_context: Optional[Dict[str, Any]]
    ) -> Optional[EscalatorDecision]:
        """
        Check hard constraints that force specific decisions.
        
        Returns:
            EscalatorDecision if a hard constraint is violated, None otherwise
        """
        # Check if we're at the bottom layer (quecto)
        if current_layer == "quecto":
            return EscalatorDecision(
                action=EscalatorAction.RESOLVE,
                reason="Reached quecto layer - no deeper refinement possible",
                from_layer=current_layer,
                metrics=layer_metrics
            )
        
        # Check total cost constraint
        total_cost = layer_metrics.get('total_cost_usd', 0.0)
        if total_cost >= self.config["force_resolve_after_cost"]:
            return EscalatorDecision(
                action=EscalatorAction.RESOLVE,
                reason=f"Cost limit exceeded: ${total_cost:.2f} >= ${self.config['force_resolve_after_cost']:.2f}",
                from_layer=current_layer,
                metrics=layer_metrics
            )
        
        # Check total time constraint
        total_latency = layer_metrics.get('total_latency_ms', 0)
        if total_latency >= self.config["force_resolve_after_time"]:
            return EscalatorDecision(
                action=EscalatorAction.RESOLVE,
                reason=f"Time limit exceeded: {total_latency}ms >= {self.config['force_resolve_after_time']}ms",
                from_layer=current_layer,
                metrics=layer_metrics
            )
        
        # Check total iterations constraint
        total_iterations = len(self.decision_history)
        if total_iterations >= self.config["max_total_iterations"]:
            return EscalatorDecision(
                action=EscalatorAction.RESOLVE,
                reason=f"Maximum iterations reached: {total_iterations}",
                from_layer=current_layer,
                metrics=layer_metrics
            )
        
        return None
    
    def _meets_resolution_criteria(
        self, 
        solution_candidate: SolutionCandidate, 
        layer_capability
    ) -> bool:
        """
        Check if the solution meets the criteria for resolution.
        
        This includes both quality thresholds and minimum acceptable levels.
        """
        # Check quality thresholds
        confidence_ok = solution_candidate.confidence_score >= layer_capability.confidence_threshold
        completeness_ok = solution_candidate.completeness_score >= layer_capability.completeness_threshold
        
        # Check minimum acceptable levels
        min_confidence_ok = solution_candidate.confidence_score >= self.config["min_confidence_for_resolution"]
        min_completeness_ok = solution_candidate.completeness_score >= self.config["min_completeness_for_resolution"]
        alignment_ok = solution_candidate.alignment_score >= self.config["min_alignment_for_resolution"]
        net_benefit_ok = solution_candidate.net_benefit_score >= self.config["net_benefit_threshold"]
        
        # Must meet minimum levels AND either quality thresholds OR be at bottom layer
        return (min_confidence_ok and min_completeness_ok and alignment_ok and net_benefit_ok) and \
               (confidence_ok and completeness_ok)
    
    def _should_refine(
        self,
        problem_id: str,
        current_layer: str,
        solution_candidate: SolutionCandidate,
        layer_metrics: Dict[str, Any],
        layer_capability
    ) -> Optional[EscalatorDecision]:
        """
        Determine if we should refine to a deeper layer.
        
        Returns:
            EscalatorDecision to refine if conditions are met, None otherwise
        """
        # Check if we've exceeded max revolutions at this layer
        revolutions = layer_metrics.get('revolutions_at_layer', 1)
        if revolutions >= layer_capability.max_revolutions:
            next_layer = LayerDefinitions.get_next_layer(current_layer)
            if next_layer:
                refined_question = LayerRefinementEngine.refine_question(
                    problem_context.get('original_question', '') if problem_context else '',
                    next_layer
                )
                
                return EscalatorDecision(
                    action=EscalatorAction.REFINE,
                    reason=f"Maximum revolutions ({revolutions}) reached at {current_layer} layer",
                    from_layer=current_layer,
                    to_layer=next_layer,
                    refined_question=refined_question,
                    metrics=layer_metrics
                )
        
        # Check if quality is insufficient for resolution
        confidence_low = solution_candidate.confidence_score < layer_capability.confidence_threshold
        completeness_low = solution_candidate.completeness_score < layer_capability.completeness_threshold
        
        if confidence_low or completeness_low:
            # Check if we're making progress
            improvement_trend = self._calculate_improvement_trend(problem_id, current_layer)
            
            # If not making progress and quality is low, refine
            if improvement_trend < self.config["improvement_threshold"]:
                next_layer = LayerDefinitions.get_next_layer(current_layer)
                if next_layer:
                    refined_question = LayerRefinementEngine.refine_question(
                        problem_context.get('original_question', '') if problem_context else '',
                        next_layer
                    )
                    
                    return EscalatorDecision(
                        action=EscalatorAction.REFINE,
                        reason=f"Quality insufficient (confidence: {solution_candidate.confidence_score:.2f}, completeness: {solution_candidate.completeness_score:.2f}) and no improvement trend",
                        from_layer=current_layer,
                        to_layer=next_layer,
                        refined_question=refined_question,
                        metrics=layer_metrics
                    )
        
        # Check cost-benefit ratio
        cost_benefit_ratio = self._calculate_cost_benefit_ratio(solution_candidate, layer_metrics)
        if cost_benefit_ratio < self.config["cost_benefit_ratio_threshold"]:
            next_layer = LayerDefinitions.get_next_layer(current_layer)
            if next_layer:
                refined_question = LayerRefinementEngine.refine_question(
                    problem_context.get('original_question', '') if problem_context else '',
                    next_layer
                )
                
                return EscalatorDecision(
                    action=EscalatorAction.REFINE,
                    reason=f"Poor cost-benefit ratio: {cost_benefit_ratio:.3f} < {self.config['cost_benefit_ratio_threshold']:.3f}",
                    from_layer=current_layer,
                    to_layer=next_layer,
                    refined_question=refined_question,
                    metrics=layer_metrics
                )
        
        return None
    
    def _should_stay(
        self,
        problem_id: str,
        current_layer: str,
        solution_candidate: SolutionCandidate,
        layer_metrics: Dict[str, Any],
        layer_capability
    ) -> Optional[EscalatorDecision]:
        """
        Determine if we should stay at the current layer for another revolution.
        
        Returns:
            EscalatorDecision to stay if conditions are met, None otherwise
        """
        revolutions = layer_metrics.get('revolutions_at_layer', 1)
        
        # Don't stay if we've exceeded max revolutions
        if revolutions >= layer_capability.max_revolutions:
            return None
        
        # Don't stay if quality is too low (should refine instead)
        confidence_low = solution_candidate.confidence_score < layer_capability.confidence_threshold
        completeness_low = solution_candidate.completeness_score < layer_capability.completeness_threshold
        
        if confidence_low or completeness_low:
            return None
        
        # Check if we're making progress
        improvement_trend = self._calculate_improvement_trend(problem_id, current_layer)
        if improvement_trend >= self.config["improvement_threshold"]:
            return EscalatorDecision(
                action=EscalatorAction.STAY,
                reason=f"Making progress: improvement trend = {improvement_trend:.3f}",
                from_layer=current_layer,
                metrics=layer_metrics
            )
        
        # Check if we have budget and time remaining
        total_cost = layer_metrics.get('total_cost_usd', 0.0)
        total_latency = layer_metrics.get('total_latency_ms', 0)
        
        budget_remaining = total_cost < layer_capability.budget_usd
        time_remaining = total_latency < layer_capability.p95_latency_ms
        
        if budget_remaining and time_remaining:
            return EscalatorDecision(
                action=EscalatorAction.STAY,
                reason="Budget and time remaining for another revolution",
                from_layer=current_layer,
                metrics=layer_metrics
            )
        
        return None
    
    def _calculate_decision_confidence(
        self,
        solution_candidate: SolutionCandidate,
        layer_metrics: Dict[str, Any],
        layer_capability
    ) -> float:
        """
        Calculate confidence in the escalator decision.
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence on solution quality
        quality_score = (solution_candidate.confidence_score + solution_candidate.completeness_score) / 2.0
        
        # Adjust based on layer depth (deeper layers are more certain)
        depth_factor = 1.0 + (layer_capability.order_idx - 1) * 0.05
        
        # Adjust based on cost-benefit ratio
        cost_benefit_ratio = self._calculate_cost_benefit_ratio(solution_candidate, layer_metrics)
        cost_benefit_factor = min(1.0, cost_benefit_ratio / self.config["cost_benefit_ratio_threshold"])
        
        # Combine factors
        confidence = quality_score * depth_factor * cost_benefit_factor
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_improvement_trend(
        self,
        problem_id: str,
        current_layer: str
    ) -> float:
        """
        Calculate improvement trend for the current layer.
        
        Returns:
            Improvement trend score (positive = improving, negative = declining)
        """
        # Get recent decisions for this problem and layer
        recent_decisions = [
            d for d in self.decision_history
            if d.get('problem_id') == problem_id and d.get('from_layer') == current_layer
        ]
        
        if len(recent_decisions) < 2:
            return 0.0
        
        # Calculate trend in confidence and completeness
        confidences = [d.get('metrics', {}).get('confidence_score', 0.0) for d in recent_decisions]
        completenesses = [d.get('metrics', {}).get('completeness_score', 0.0) for d in recent_decisions]
        
        if len(confidences) < 2:
            return 0.0
        
        # Calculate linear trend
        confidence_trend = (confidences[-1] - confidences[0]) / len(confidences)
        completeness_trend = (completenesses[-1] - completenesses[0]) / len(completenesses)
        
        return (confidence_trend + completeness_trend) / 2.0
    
    def _calculate_cost_benefit_ratio(
        self,
        solution_candidate: SolutionCandidate,
        layer_metrics: Dict[str, Any]
    ) -> float:
        """
        Calculate cost-benefit ratio for the solution.
        
        Returns:
            Benefit per dollar spent
        """
        total_cost = layer_metrics.get('total_cost_usd', 0.0)
        if total_cost <= 0:
            return float('inf')
        
        # Calculate benefit as weighted combination of quality metrics
        benefit = (
            solution_candidate.confidence_score * 0.4 +
            solution_candidate.completeness_score * 0.4 +
            solution_candidate.novelty_score * 0.1 +
            solution_candidate.alignment_score * 0.1
        )
        
        return benefit / total_cost
    
    def _record_decision(
        self,
        problem_id: str,
        decision: EscalatorDecision,
        layer_metrics: Dict[str, Any]
    ):
        """
        Record decision for learning and analysis.
        
        Args:
            problem_id: Problem ID
            decision: Escalator decision
            layer_metrics: Layer metrics
        """
        decision_record = {
            "problem_id": problem_id,
            "timestamp": decision.timestamp.isoformat(),
            "action": decision.action.value,
            "from_layer": decision.from_layer,
            "to_layer": decision.to_layer,
            "reason": decision.reason,
            "confidence": decision.confidence,
            "metrics": layer_metrics
        }
        
        self.decision_history.append(decision_record)
        
        # Update performance trends
        if "confidence_score" in layer_metrics:
            self.performance_trends["confidence"].append(layer_metrics["confidence_score"])
        if "completeness_score" in layer_metrics:
            self.performance_trends["completeness"].append(layer_metrics["completeness_score"])
        if "total_cost_usd" in layer_metrics:
            self.performance_trends["cost"].append(layer_metrics["total_cost_usd"])
        if "total_latency_ms" in layer_metrics:
            self.performance_trends["latency"].append(layer_metrics["total_latency_ms"])
        
        # Keep only recent history to prevent memory bloat
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-500:]
        
        for trend in self.performance_trends.values():
            if len(trend) > 1000:
                trend[:] = trend[-500:]
    
    def get_decision_summary(self, decision: EscalatorDecision) -> Dict[str, Any]:
        """Get a summary of the escalator decision."""
        return {
            "action": decision.action.value,
            "reason": decision.reason,
            "from_layer": decision.from_layer,
            "to_layer": decision.to_layer,
            "refined_question": decision.refined_question,
            "timestamp": decision.timestamp.isoformat(),
            "confidence": decision.confidence,
            "metrics": decision.metrics
        }
    
    def get_performance_analytics(self) -> Dict[str, Any]:
        """
        Get performance analytics for the escalator.
        
        Returns:
            Performance analytics data
        """
        if not self.performance_trends["confidence"]:
            return {"error": "No performance data available"}
        
        analytics = {
            "total_decisions": len(self.decision_history),
            "average_confidence": sum(self.performance_trends["confidence"]) / len(self.performance_trends["confidence"]),
            "average_completeness": sum(self.performance_trends["completeness"]) / len(self.performance_trends["completeness"]),
            "total_cost": sum(self.performance_trends["cost"]),
            "total_latency": sum(self.performance_trends["latency"]),
            "decision_distribution": self._get_decision_distribution(),
            "performance_trends": self.performance_trends
        }
        
        return analytics
    
    def _get_decision_distribution(self) -> Dict[str, int]:
        """Get distribution of decision types."""
        distribution = {"stay": 0, "refine": 0, "resolve": 0}
        
        for decision in self.decision_history:
            action = decision.get("action", "unknown")
            if action in distribution:
                distribution[action] += 1
        
        return distribution


# Example usage and testing
if __name__ == "__main__":
    # Test fixed escalator engine
    print("=== Fixed Escalator Engine Test ===")
    
    # Create test solution candidate
    solution = SolutionCandidate(
        solution_text="Implement carbon capture technology in steel plants",
        confidence_score=0.75,
        completeness_score=0.70,
        novelty_score=0.3,
        alignment_score=0.95,
        net_benefit_score=0.8
    )
    
    # Create test layer metrics
    layer_metrics = {
        "revolutions_at_layer": 2,
        "total_cost_usd": 50.0,
        "total_latency_ms": 15000,
        "confidence_score": 0.75,
        "completeness_score": 0.70
    }
    
    # Create problem context
    problem_context = {
        "original_question": "How can we reduce global carbon emissions?",
        "problem_id": "test-problem-001"
    }
    
    # Test escalator decision
    escalator = EscalatorEngine()
    decision = escalator.decide(
        problem_id="test-problem-001",
        current_layer="deci",
        solution_candidate=solution,
        layer_metrics=layer_metrics,
        problem_context=problem_context
    )
    
    print(f"Decision: {decision.action.value}")
    print(f"Reason: {decision.reason}")
    print(f"Confidence: {decision.confidence:.3f}")
    if decision.to_layer:
        print(f"Refining to: {decision.to_layer}")
        print(f"Refined question: {decision.refined_question}")
    
    # Test performance analytics
    analytics = escalator.get_performance_analytics()
    print(f"\nPerformance Analytics:")
    print(f"Total decisions: {analytics['total_decisions']}")
    print(f"Decision distribution: {analytics['decision_distribution']}")
