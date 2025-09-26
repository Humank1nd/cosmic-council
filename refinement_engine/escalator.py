"""
Cosmic Council Refinement Engine - Escalator Function
Decides whether to stay at current layer, refine to deeper layer, or resolve the problem.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
import logging
from datetime import datetime

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
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class EscalatorEngine:
    """
    The escalator function that decides whether to stay, refine, or resolve.
    
    This is the core decision-making engine that determines the next step
    in the problem-solving process based on solution quality and layer policies.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the escalator engine.
        
        Args:
            config: Configuration dictionary with thresholds and policies
        """
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the escalator."""
        return {
            "confidence_threshold": 0.85,
            "completeness_threshold": 0.80,
            "novelty_threshold": 0.20,
            "alignment_threshold": 0.90,
            "net_benefit_threshold": 0.0,
            "max_revolutions_per_layer": 3,
            "improvement_threshold": 0.05,  # Minimum improvement to stay
            "cost_threshold_multiplier": 1.5,  # Max cost before forcing refinement
            "latency_threshold_multiplier": 2.0  # Max latency before forcing refinement
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
        
        Args:
            problem_id: Unique identifier for the problem
            current_layer: Current layer name (deci, centi, etc.)
            solution_candidate: The solution candidate to evaluate
            layer_metrics: Metrics from the current layer run
            problem_context: Additional context about the problem
            
        Returns:
            EscalatorDecision with the chosen action and reasoning
        """
        self.logger.info(f"Making escalator decision for problem {problem_id} at layer {current_layer}")
        
        # Get layer-specific policies
        layer_capability = LayerDefinitions.get_layer(current_layer)
        if not layer_capability:
            return EscalatorDecision(
                action=EscalatorAction.RESOLVE,
                reason=f"Invalid layer: {current_layer}",
                from_layer=current_layer
            )
        
        # Check if solution meets exit criteria
        if self._meets_resolution_criteria(solution_candidate, layer_capability):
            return EscalatorDecision(
                action=EscalatorAction.RESOLVE,
                reason="Solution meets confidence and completeness thresholds",
                from_layer=current_layer,
                metrics=layer_metrics
            )
        
        # Check if we should refine to a deeper layer
        if self._should_refine(solution_candidate, layer_metrics, layer_capability):
            next_layer = LayerDefinitions.get_next_layer(current_layer)
            if next_layer:
                refined_question = LayerRefinementEngine.refine_question(
                    problem_context.get('original_question', '') if problem_context else '',
                    next_layer
                )
                
                rationale = LayerRefinementEngine.get_refinement_rationale(
                    current_layer, next_layer, layer_metrics
                )
                
                return EscalatorDecision(
                    action=EscalatorAction.REFINE,
                    reason=rationale,
                    from_layer=current_layer,
                    to_layer=next_layer,
                    refined_question=refined_question,
                    metrics=layer_metrics
                )
            else:
                # We're at the bottom layer (quecto)
                return EscalatorDecision(
                    action=EscalatorAction.RESOLVE,
                    reason="Reached quecto layer - no deeper refinement possible. Returning best available solution.",
                    from_layer=current_layer,
                    metrics=layer_metrics
                )
        
        # Check if we should stay at the current layer
        if self._should_stay(solution_candidate, layer_metrics, layer_capability):
            return EscalatorDecision(
                action=EscalatorAction.STAY,
                reason="Re-run current layer with alternative framing or new data",
                from_layer=current_layer,
                metrics=layer_metrics
            )
        
        # Default: force resolution if we can't make progress
        return EscalatorDecision(
            action=EscalatorAction.RESOLVE,
            reason="Unable to make progress - forcing resolution with best available solution",
            from_layer=current_layer,
            metrics=layer_metrics
        )
    
    def _meets_resolution_criteria(
        self, 
        solution_candidate: SolutionCandidate, 
        layer_capability
    ) -> bool:
        """Check if the solution meets the criteria for resolution."""
        confidence_ok = solution_candidate.confidence_score >= layer_capability.confidence_threshold
        completeness_ok = solution_candidate.completeness_score >= layer_capability.completeness_threshold
        alignment_ok = solution_candidate.alignment_score >= self.config["alignment_threshold"]
        net_benefit_ok = solution_candidate.net_benefit_score >= self.config["net_benefit_threshold"]
        
        return confidence_ok and completeness_ok and alignment_ok and net_benefit_ok
    
    def _should_refine(
        self,
        solution_candidate: SolutionCandidate,
        layer_metrics: Dict[str, Any],
        layer_capability
    ) -> bool:
        """Determine if we should refine to a deeper layer."""
        # Check if we've exceeded max revolutions
        revolutions = layer_metrics.get('revolutions_at_layer', 1)
        if revolutions >= layer_capability.max_revolutions:
            self.logger.info(f"Max revolutions ({revolutions}) reached for layer {layer_capability.name}")
            return True
        
        # Check if confidence or completeness is too low
        confidence_low = solution_candidate.confidence_score < layer_capability.confidence_threshold
        completeness_low = solution_candidate.completeness_score < layer_capability.completeness_threshold
        
        if confidence_low or completeness_low:
            self.logger.info(f"Quality thresholds not met: confidence={solution_candidate.confidence_score:.2f}, completeness={solution_candidate.completeness_score:.2f}")
            return True
        
        # Check if we're not making progress (stagnation)
        improvement_trend = layer_metrics.get('improvement_trend', 0.0)
        if improvement_trend < self.config["improvement_threshold"] and revolutions > 1:
            self.logger.info(f"Stagnation detected: improvement_trend={improvement_trend:.3f}")
            return True
        
        # Check cost and latency thresholds
        total_cost = layer_metrics.get('total_cost_usd', 0.0)
        if total_cost > layer_capability.budget_usd * self.config["cost_threshold_multiplier"]:
            self.logger.info(f"Cost threshold exceeded: {total_cost:.2f} > {layer_capability.budget_usd * self.config['cost_threshold_multiplier']:.2f}")
            return True
        
        total_latency = layer_metrics.get('total_latency_ms', 0)
        if total_latency > layer_capability.p95_latency_ms * self.config["latency_threshold_multiplier"]:
            self.logger.info(f"Latency threshold exceeded: {total_latency} > {layer_capability.p95_latency_ms * self.config['latency_threshold_multiplier']}")
            return True
        
        return False
    
    def _should_stay(
        self,
        solution_candidate: SolutionCandidate,
        layer_metrics: Dict[str, Any],
        layer_capability
    ) -> bool:
        """Determine if we should stay at the current layer for another revolution."""
        revolutions = layer_metrics.get('revolutions_at_layer', 1)
        
        # Don't stay if we've exceeded max revolutions
        if revolutions >= layer_capability.max_revolutions:
            return False
        
        # Don't stay if quality is too low (should refine instead)
        confidence_low = solution_candidate.confidence_score < layer_capability.confidence_threshold
        completeness_low = solution_candidate.completeness_score < layer_capability.completeness_threshold
        
        if confidence_low or completeness_low:
            return False
        
        # Stay if we're making progress
        improvement_trend = layer_metrics.get('improvement_trend', 0.0)
        if improvement_trend >= self.config["improvement_threshold"]:
            self.logger.info(f"Making progress: improvement_trend={improvement_trend:.3f}")
            return True
        
        # Stay if we have budget and time remaining
        total_cost = layer_metrics.get('total_cost_usd', 0.0)
        total_latency = layer_metrics.get('total_latency_ms', 0)
        
        budget_remaining = layer_capability.budget_usd - total_cost > 0
        time_remaining = total_latency < layer_capability.p95_latency_ms
        
        if budget_remaining and time_remaining:
            self.logger.info("Budget and time remaining - staying for another revolution")
            return True
        
        return False
    
    def get_decision_summary(self, decision: EscalatorDecision) -> Dict[str, Any]:
        """Get a summary of the escalator decision."""
        return {
            "action": decision.action.value,
            "reason": decision.reason,
            "from_layer": decision.from_layer,
            "to_layer": decision.to_layer,
            "refined_question": decision.refined_question,
            "timestamp": decision.timestamp.isoformat(),
            "metrics": decision.metrics
        }
    
    def validate_decision(self, decision: EscalatorDecision) -> List[str]:
        """
        Validate an escalator decision and return any issues.
        
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        
        if decision.action == EscalatorAction.REFINE:
            if not decision.to_layer:
                issues.append("Refine action requires to_layer")
            if not decision.refined_question:
                issues.append("Refine action requires refined_question")
            if decision.from_layer == decision.to_layer:
                issues.append("Cannot refine to the same layer")
        
        if decision.action == EscalatorAction.STAY:
            if not decision.from_layer:
                issues.append("Stay action requires from_layer")
        
        if decision.action == EscalatorAction.RESOLVE:
            if not decision.from_layer:
                issues.append("Resolve action requires from_layer")
        
        return issues


class EscalatorMetrics:
    """Helper class for calculating and tracking escalator metrics."""
    
    @staticmethod
    def calculate_improvement_trend(confidence_history: List[float], completeness_history: List[float]) -> float:
        """
        Calculate the improvement trend from historical metrics.
        
        Args:
            confidence_history: List of confidence scores over time
            completeness_history: List of completeness scores over time
            
        Returns:
            Improvement trend score (positive = improving, negative = declining)
        """
        if len(confidence_history) < 2 or len(completeness_history) < 2:
            return 0.0
        
        # Calculate weighted improvement (confidence and completeness equally weighted)
        confidence_improvement = (confidence_history[-1] - confidence_history[0]) / len(confidence_history)
        completeness_improvement = (completeness_history[-1] - completeness_history[0]) / len(completeness_history)
        
        return (confidence_improvement + completeness_improvement) / 2.0
    
    @staticmethod
    def calculate_layer_efficiency(metrics: Dict[str, Any]) -> float:
        """
        Calculate the efficiency of a layer run.
        
        Args:
            metrics: Layer run metrics
            
        Returns:
            Efficiency score (0.0 to 1.0)
        """
        confidence = metrics.get('confidence_score', 0.0)
        completeness = metrics.get('completeness_score', 0.0)
        cost = metrics.get('total_cost_usd', 0.0)
        latency = metrics.get('total_latency_ms', 0)
        
        # Quality score (weighted average of confidence and completeness)
        quality_score = (confidence + completeness) / 2.0
        
        # Efficiency penalty for high cost and latency
        cost_penalty = min(cost / 100.0, 1.0)  # Normalize cost penalty
        latency_penalty = min(latency / 60000.0, 1.0)  # Normalize latency penalty (60s = 1.0)
        
        efficiency = quality_score * (1.0 - (cost_penalty + latency_penalty) / 2.0)
        return max(0.0, min(1.0, efficiency))


# Example usage and testing
if __name__ == "__main__":
    # Test escalator engine
    print("=== Escalator Engine Test ===")
    
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
        "improvement_trend": 0.02,
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
    if decision.to_layer:
        print(f"Refining to: {decision.to_layer}")
        print(f"Refined question: {decision.refined_question}")
    
    # Test metrics calculation
    confidence_history = [0.60, 0.65, 0.70, 0.75]
    completeness_history = [0.55, 0.60, 0.65, 0.70]
    improvement = EscalatorMetrics.calculate_improvement_trend(confidence_history, completeness_history)
    print(f"\nImprovement trend: {improvement:.3f}")
    
    efficiency = EscalatorMetrics.calculate_layer_efficiency(layer_metrics)
    print(f"Layer efficiency: {efficiency:.3f}")
