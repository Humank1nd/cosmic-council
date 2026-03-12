"""
RED OWL - Hypothesis Weigher.

Evaluates hypotheses against gathered evidence to determine:
- Which hypotheses are supported
- Which hypotheses are refuted
- Which hypotheses need more investigation

The weigher updates hypothesis confidence based on evidence,
moving hypotheses through states: PROPOSED → EVIDENCED/CHALLENGED → ACCEPTED/REJECTED

The key insight: crystallized evidence gets bonus weight because it represents
proven solutions - this is how the system compounds knowledge.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import structlog

from .models import (
    AnalysisDepth,
    Evidence,
    EvidenceType,
    EvidenceWeight,
    Hypothesis,
    HypothesisStatus,
)

logger = structlog.get_logger(__name__)


@dataclass
class WeighingResult:
    """Result of weighing hypotheses against evidence."""
    hypotheses: List[Hypothesis] = field(default_factory=list)
    accepted: List[Hypothesis] = field(default_factory=list)
    rejected: List[Hypothesis] = field(default_factory=list)
    needs_investigation: List[Hypothesis] = field(default_factory=list)
    reasoning: List[str] = field(default_factory=list)
    duration_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class HypothesisWeigher:
    """
    Weighs hypotheses against evidence to determine acceptance/rejection.

    The weighing algorithm:
    1. Calculate support score from supporting evidence
    2. Calculate refutation score from refuting evidence
    3. Apply crystallization bonus (compounding mechanism)
    4. Determine final confidence and status

    Status transitions:
    - PROPOSED + strong support → EVIDENCED → ACCEPTED
    - PROPOSED + strong refutation → CHALLENGED → REJECTED
    - PROPOSED + mixed evidence → needs more investigation
    """

    # Confidence thresholds
    ACCEPTANCE_THRESHOLD = 0.7  # Minimum confidence to accept
    REJECTION_THRESHOLD = 0.3   # Maximum confidence before rejection
    CRYSTALLIZATION_BONUS = 0.15  # Bonus for crystallized evidence

    # Evidence weight multipliers
    WEIGHT_MULTIPLIERS = {
        EvidenceWeight.STRONG_SUPPORT: 1.0,
        EvidenceWeight.MODERATE_SUPPORT: 0.6,
        EvidenceWeight.WEAK_SUPPORT: 0.3,
        EvidenceWeight.NEUTRAL: 0.0,
        EvidenceWeight.WEAK_REFUTE: -0.3,
        EvidenceWeight.MODERATE_REFUTE: -0.6,
        EvidenceWeight.STRONG_REFUTE: -1.0,
    }

    def __init__(
        self,
        acceptance_threshold: float = 0.7,
        rejection_threshold: float = 0.3,
        crystallization_bonus: float = 0.15,
    ):
        """
        Initialize the hypothesis weigher.

        Args:
            acceptance_threshold: Minimum confidence to accept hypothesis
            rejection_threshold: Maximum confidence before rejection
            crystallization_bonus: Bonus weight for crystallized evidence
        """
        self.acceptance_threshold = acceptance_threshold
        self.rejection_threshold = rejection_threshold
        self.crystallization_bonus = crystallization_bonus
        logger.info(
            "hypothesis_weigher_initialized",
            acceptance_threshold=acceptance_threshold,
            rejection_threshold=rejection_threshold,
            crystallization_bonus=crystallization_bonus,
        )

    def weigh(
        self,
        hypotheses: List[Hypothesis],
        evidence: List[Evidence],
        depth: AnalysisDepth,
    ) -> WeighingResult:
        """
        Weigh hypotheses against evidence.

        Args:
            hypotheses: Hypotheses to evaluate
            evidence: Evidence to weigh against
            depth: Current analysis depth

        Returns:
            WeighingResult with evaluated hypotheses
        """
        start_time = time.time()
        result = WeighingResult()

        # Group evidence by hypothesis
        evidence_by_hypothesis = self._group_evidence_by_hypothesis(evidence)

        for hypothesis in hypotheses:
            # Get evidence for this hypothesis
            hyp_evidence = evidence_by_hypothesis.get(hypothesis.id, [])

            # Calculate scores
            support_score, refute_score = self._calculate_scores(hyp_evidence)

            # Apply crystallization bonus
            crystallized_bonus = self._calculate_crystallization_bonus(hyp_evidence)

            # Update hypothesis
            hypothesis.supporting_score = support_score + crystallized_bonus
            hypothesis.refuting_score = refute_score
            hypothesis.evidence_ids = [e.id for e in hyp_evidence]

            # Calculate net confidence
            net_score = hypothesis.supporting_score - hypothesis.refuting_score
            base_confidence = hypothesis.confidence

            # Update confidence based on evidence
            # Scale net_score to a confidence adjustment (-0.5 to +0.5)
            confidence_adjustment = max(-0.5, min(0.5, net_score * 0.2))
            new_confidence = max(0.0, min(1.0, base_confidence + confidence_adjustment))
            hypothesis.confidence = new_confidence

            # Determine status
            self._update_status(hypothesis, hyp_evidence, depth)

            # Add reasoning
            hypothesis.reasoning_chain.append(
                f"Depth {depth.name}: {len(hyp_evidence)} evidence items, "
                f"support={hypothesis.supporting_score:.2f}, "
                f"refute={hypothesis.refuting_score:.2f}, "
                f"crystallized_bonus={crystallized_bonus:.2f}, "
                f"confidence={hypothesis.confidence:.2f} → {hypothesis.status.value}"
            )

            result.hypotheses.append(hypothesis)

            # Categorize
            if hypothesis.status == HypothesisStatus.ACCEPTED:
                result.accepted.append(hypothesis)
                result.reasoning.append(
                    f"ACCEPTED: '{hypothesis.statement[:50]}...' "
                    f"(confidence={hypothesis.confidence:.2f})"
                )
            elif hypothesis.status == HypothesisStatus.REJECTED:
                result.rejected.append(hypothesis)
                result.reasoning.append(
                    f"REJECTED: '{hypothesis.statement[:50]}...' "
                    f"(confidence={hypothesis.confidence:.2f})"
                )
            else:
                result.needs_investigation.append(hypothesis)

        result.duration_ms = int((time.time() - start_time) * 1000)
        result.metadata = {
            "total_hypotheses": len(hypotheses),
            "total_evidence": len(evidence),
            "accepted_count": len(result.accepted),
            "rejected_count": len(result.rejected),
            "needs_investigation_count": len(result.needs_investigation),
        }

        logger.info(
            "hypotheses_weighed",
            depth=depth.name,
            total=len(hypotheses),
            accepted=len(result.accepted),
            rejected=len(result.rejected),
            needs_investigation=len(result.needs_investigation),
            duration_ms=result.duration_ms,
        )

        return result

    def _group_evidence_by_hypothesis(
        self,
        evidence: List[Evidence],
    ) -> Dict[str, List[Evidence]]:
        """Group evidence by the hypotheses they relate to."""
        grouped: Dict[str, List[Evidence]] = {}

        for ev in evidence:
            for hyp_id in ev.hypothesis_ids:
                if hyp_id not in grouped:
                    grouped[hyp_id] = []
                grouped[hyp_id].append(ev)

        return grouped

    def _calculate_scores(
        self,
        evidence: List[Evidence],
    ) -> Tuple[float, float]:
        """Calculate support and refutation scores from evidence."""
        support_score = 0.0
        refute_score = 0.0

        for ev in evidence:
            weight_multiplier = self.WEIGHT_MULTIPLIERS.get(ev.weight, 0.0)
            relevance_factor = ev.relevance

            contribution = abs(weight_multiplier) * relevance_factor

            if weight_multiplier > 0:
                support_score += contribution
            elif weight_multiplier < 0:
                refute_score += contribution

        return support_score, refute_score

    def _calculate_crystallization_bonus(
        self,
        evidence: List[Evidence],
    ) -> float:
        """
        Calculate bonus from crystallized evidence.

        This is THE mechanism for compounding - crystallized truths
        from past problem solving get extra weight.
        """
        bonus = 0.0

        for ev in evidence:
            if ev.is_crystallized and ev.weight.value > 0:
                # Crystallized evidence gets a bonus proportional to its relevance
                bonus += self.crystallization_bonus * ev.relevance

        return bonus

    def _update_status(
        self,
        hypothesis: Hypothesis,
        evidence: List[Evidence],
        depth: AnalysisDepth,
    ) -> None:
        """Update hypothesis status based on evidence and confidence."""
        has_supporting = any(e.weight.value > 0 for e in evidence)
        has_refuting = any(e.weight.value < 0 for e in evidence)

        # High confidence + supporting evidence → ACCEPTED
        if hypothesis.confidence >= self.acceptance_threshold and has_supporting:
            hypothesis.status = HypothesisStatus.ACCEPTED

        # Low confidence + refuting evidence → REJECTED
        elif hypothesis.confidence <= self.rejection_threshold and has_refuting:
            hypothesis.status = HypothesisStatus.REJECTED

        # Has both supporting and refuting → CHALLENGED (needs more investigation)
        elif has_supporting and has_refuting:
            hypothesis.status = HypothesisStatus.CHALLENGED

        # Has only supporting evidence but not enough confidence → EVIDENCED
        elif has_supporting:
            hypothesis.status = HypothesisStatus.EVIDENCED

        # Has only refuting evidence but not low enough confidence → CHALLENGED
        elif has_refuting:
            hypothesis.status = HypothesisStatus.CHALLENGED

        # No strong evidence either way → stays PROPOSED
        else:
            hypothesis.status = HypothesisStatus.PROPOSED

    def rank_hypotheses(
        self,
        hypotheses: List[Hypothesis],
        prefer_crystallized: bool = True,
    ) -> List[Hypothesis]:
        """
        Rank hypotheses by likelihood of being the root cause.

        Args:
            hypotheses: Hypotheses to rank
            prefer_crystallized: Whether to prefer crystallized-backed hypotheses

        Returns:
            Sorted list of hypotheses (best first)
        """
        def score_hypothesis(h: Hypothesis) -> float:
            base_score = h.confidence

            # Bonus for having evidence
            if h.evidence_ids:
                base_score += 0.1

            # Bonus for crystallized evidence
            if prefer_crystallized and h.metadata.get("has_crystallized_evidence"):
                base_score += 0.1

            # Penalty for being challenged or rejected
            if h.status == HypothesisStatus.CHALLENGED:
                base_score -= 0.1
            elif h.status == HypothesisStatus.REJECTED:
                base_score -= 0.5

            # Net evidence score
            base_score += h.net_evidence_score * 0.1

            return base_score

        return sorted(hypotheses, key=score_hypothesis, reverse=True)

    def should_deepen(
        self,
        result: WeighingResult,
        current_depth: AnalysisDepth,
        min_confidence: float = 0.8,
    ) -> bool:
        """
        Determine if analysis should go deeper.

        Args:
            result: Current weighing result
            current_depth: Current analysis depth
            min_confidence: Minimum confidence to stop deepening

        Returns:
            True if should deepen analysis, False if sufficient
        """
        # If we've reached synthesis, no need to deepen
        if current_depth == AnalysisDepth.SYNTHESIS:
            return False

        # If we have high-confidence accepted hypotheses, might not need to deepen
        if result.accepted:
            max_confidence = max(h.confidence for h in result.accepted)
            if max_confidence >= min_confidence:
                logger.info(
                    "deepening_not_needed",
                    reason="high_confidence_hypothesis",
                    max_confidence=max_confidence,
                )
                return False

        # If everything is rejected, might need fresh approach
        if result.rejected and not result.accepted and not result.needs_investigation:
            logger.info(
                "deepening_recommended",
                reason="all_rejected",
            )
            return True

        # If there are hypotheses needing investigation, deepen
        if result.needs_investigation:
            logger.info(
                "deepening_recommended",
                reason="needs_investigation",
                count=len(result.needs_investigation),
            )
            return True

        # Default: deepen if not at high confidence
        return True


# Factory function
def create_weigher(
    acceptance_threshold: float = 0.7,
    rejection_threshold: float = 0.3,
    crystallization_bonus: float = 0.15,
) -> HypothesisWeigher:
    """Create a hypothesis weigher instance."""
    return HypothesisWeigher(
        acceptance_threshold=acceptance_threshold,
        rejection_threshold=rejection_threshold,
        crystallization_bonus=crystallization_bonus,
    )
