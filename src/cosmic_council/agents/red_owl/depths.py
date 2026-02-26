"""
RED OWL - Depth Analysis System.

Coordinates the depth-level analysis cycle:
SURFACE → CAUSAL → COUNTERFACTUAL → ADVERSARIAL → SYNTHESIS

The key insight: this is not retry logic. Each depth level asks a
DIFFERENT question and produces DIFFERENT outputs. This is genuine
deepening of understanding.

The "7th step" recursion: if synthesis doesn't reach confidence threshold,
we recurse - but the NEXT iteration starts with the outputs of this
iteration, creating genuine compounding.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

from .models import (
    AnalysisDepth,
    DepthAnalysis,
    Evidence,
    Hypothesis,
    HypothesisStatus,
    ProblemComponent,
    RedOwlConfig,
)
from .decomposer import ProblemDecomposer, DecompositionResult
from .hypothesizer import HypothesisGenerator, HypothesisGenerationResult
from .evidence import EvidenceGatherer, EvidenceGatheringResult
from .weigher import HypothesisWeigher, WeighingResult

logger = structlog.get_logger(__name__)


@dataclass
class DepthCycleResult:
    """Result of a complete depth cycle (SURFACE through SYNTHESIS)."""
    depth_analyses: List[DepthAnalysis] = field(default_factory=list)
    final_hypotheses: List[Hypothesis] = field(default_factory=list)
    final_confidence: float = 0.0
    reached_synthesis: bool = False
    recursion_count: int = 0
    total_duration_ms: int = 0
    crystallization_hits: int = 0
    total_evidence: int = 0
    total_hypotheses: int = 0
    should_recurse: bool = False
    reasoning: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DepthAnalysisSystem:
    """
    Orchestrates the depth-level analysis cycle.

    The cycle:
    1. SURFACE: What symptoms are present?
    2. CAUSAL: What mechanisms explain them?
    3. COUNTERFACTUAL: What conditions were necessary?
    4. ADVERSARIAL: How could we be wrong?
    5. SYNTHESIS: What's the unified model?

    If synthesis confidence is below threshold, we recurse (7th step).
    Each recursion builds on the previous, creating genuine deepening.
    """

    DEPTH_ORDER = [
        AnalysisDepth.SURFACE,
        AnalysisDepth.CAUSAL,
        AnalysisDepth.COUNTERFACTUAL,
        AnalysisDepth.ADVERSARIAL,
        AnalysisDepth.SYNTHESIS,
    ]

    def __init__(
        self,
        decomposer: ProblemDecomposer,
        hypothesizer: HypothesisGenerator,
        evidence_gatherer: EvidenceGatherer,
        weigher: HypothesisWeigher,
        config: Optional[RedOwlConfig] = None,
    ):
        """
        Initialize the depth analysis system.

        Args:
            decomposer: Problem decomposer
            hypothesizer: Hypothesis generator
            evidence_gatherer: Evidence gatherer
            weigher: Hypothesis weigher
            config: Red Owl configuration
        """
        self.decomposer = decomposer
        self.hypothesizer = hypothesizer
        self.evidence_gatherer = evidence_gatherer
        self.weigher = weigher
        self.config = config or RedOwlConfig()

        logger.info(
            "depth_analysis_system_initialized",
            min_depth=self.config.min_depth.name,
            max_depth=self.config.max_depth.name,
            confidence_threshold=self.config.confidence_threshold,
            max_recursions=self.config.max_recursions,
        )

    async def analyze_at_depth(
        self,
        depth: AnalysisDepth,
        components: List[ProblemComponent],
        problem_type: str,
        problem_statement: str,
        previous_analysis: Optional[DepthAnalysis] = None,
        crystallized_hints: Optional[List[Dict[str, Any]]] = None,
    ) -> DepthAnalysis:
        """
        Perform analysis at a specific depth level.

        Args:
            depth: The depth level to analyze at
            components: Problem components
            problem_type: Type of problem
            problem_statement: Original problem statement
            previous_analysis: Analysis from previous depth
            crystallized_hints: Hints from crystallized truths

        Returns:
            DepthAnalysis for this depth level
        """
        start_time = time.time()
        analysis = DepthAnalysis(depth=depth)

        if previous_analysis:
            analysis.builds_on_id = previous_analysis.id

        # 1. Generate hypotheses for this depth
        gen_result: HypothesisGenerationResult = await self.hypothesizer.generate(
            depth=depth,
            components=components,
            problem_type=problem_type,
            previous_analysis=previous_analysis,
            crystallized_hints=crystallized_hints,
            max_hypotheses=self.config.max_hypotheses_per_depth,
        )
        analysis.hypotheses = gen_result.hypotheses
        analysis.llm_calls = gen_result.llm_calls

        analysis.reasoning_chain.append(
            f"Generated {len(gen_result.hypotheses)} hypotheses at {depth.name} depth"
        )

        # 2. Gather evidence for these hypotheses
        ev_result: EvidenceGatheringResult = await self.evidence_gatherer.gather(
            hypotheses=gen_result.hypotheses,
            problem_type=problem_type,
            problem_statement=problem_statement,
            depth=depth,
            max_evidence_per_hypothesis=self.config.max_evidence_per_hypothesis,
            search_crystallized=True,
        )
        analysis.evidence = ev_result.evidence
        analysis.crystallization_hits = ev_result.crystallization_hits

        analysis.reasoning_chain.append(
            f"Gathered {len(ev_result.evidence)} evidence items "
            f"({ev_result.crystallization_hits} from crystallized truths)"
        )

        # 3. Weigh hypotheses against evidence
        weigh_result: WeighingResult = self.weigher.weigh(
            hypotheses=analysis.hypotheses,
            evidence=analysis.evidence,
            depth=depth,
        )
        analysis.hypotheses = weigh_result.hypotheses

        analysis.reasoning_chain.append(
            f"Weighed hypotheses: {len(weigh_result.accepted)} accepted, "
            f"{len(weigh_result.rejected)} rejected, "
            f"{len(weigh_result.needs_investigation)} need investigation"
        )

        # 4. Extract key insights
        analysis.key_insights = self._extract_insights(analysis)

        # 5. Calculate overall confidence for this depth
        if weigh_result.accepted:
            analysis.confidence = max(h.confidence for h in weigh_result.accepted)
        elif analysis.hypotheses:
            analysis.confidence = sum(h.confidence for h in analysis.hypotheses) / len(analysis.hypotheses)
        else:
            analysis.confidence = 0.0

        analysis.duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "depth_analysis_complete",
            depth=depth.name,
            hypotheses=len(analysis.hypotheses),
            evidence=len(analysis.evidence),
            crystallization_hits=analysis.crystallization_hits,
            confidence=analysis.confidence,
            duration_ms=analysis.duration_ms,
        )

        return analysis

    async def run_depth_cycle(
        self,
        problem_statement: str,
        context: Optional[Dict[str, Any]] = None,
        previous_cycle: Optional[DepthCycleResult] = None,
    ) -> DepthCycleResult:
        """
        Run a complete depth cycle from SURFACE to SYNTHESIS.

        Args:
            problem_statement: The problem to analyze
            context: Optional additional context
            previous_cycle: Previous cycle result (for recursion)

        Returns:
            DepthCycleResult with all depth analyses
        """
        start_time = time.time()
        result = DepthCycleResult()

        if previous_cycle:
            result.recursion_count = previous_cycle.recursion_count + 1
            result.reasoning.append(
                f"Recursion {result.recursion_count}: Building on previous cycle "
                f"(confidence was {previous_cycle.final_confidence:.2f})"
            )

        # 1. Decompose the problem
        decomp_result: DecompositionResult = await self.decomposer.decompose(
            problem_statement=problem_statement,
            context=context,
        )

        result.reasoning.append(
            f"Decomposed problem into {len(decomp_result.components)} components "
            f"(type: {decomp_result.problem_type})"
        )

        # 2. Get crystallized hints upfront
        crystallized_hints = await self._get_crystallized_hints(
            problem_statement, decomp_result.problem_type
        )
        if crystallized_hints:
            result.reasoning.append(
                f"Found {len(crystallized_hints)} crystallized hints from past problems"
            )

        # 3. Run through depth levels
        previous_analysis: Optional[DepthAnalysis] = None

        # If recursing, start with previous cycle's synthesis insights
        if previous_cycle and previous_cycle.depth_analyses:
            # Use the previous synthesis as our starting point
            previous_analysis = previous_cycle.depth_analyses[-1]

        for depth in self.DEPTH_ORDER:
            # Skip depths below minimum
            if depth.value < self.config.min_depth.value:
                continue

            # Skip depths above maximum
            if depth.value > self.config.max_depth.value:
                break

            analysis = await self.analyze_at_depth(
                depth=depth,
                components=decomp_result.components,
                problem_type=decomp_result.problem_type,
                problem_statement=problem_statement,
                previous_analysis=previous_analysis,
                crystallized_hints=crystallized_hints,
            )

            result.depth_analyses.append(analysis)
            result.crystallization_hits += analysis.crystallization_hits
            result.total_evidence += len(analysis.evidence)
            result.total_hypotheses += len(analysis.hypotheses)

            previous_analysis = analysis

            # Check if we should continue to next depth
            if depth == AnalysisDepth.SYNTHESIS:
                result.reached_synthesis = True

        # 4. Determine final state
        if result.depth_analyses:
            final_analysis = result.depth_analyses[-1]
            result.final_hypotheses = [
                h for h in final_analysis.hypotheses
                if h.status == HypothesisStatus.ACCEPTED
            ]
            result.final_confidence = final_analysis.confidence

            # Should we recurse?
            result.should_recurse = (
                result.final_confidence < self.config.confidence_threshold
                and result.recursion_count < self.config.max_recursions
            )

            if result.should_recurse:
                result.reasoning.append(
                    f"Confidence {result.final_confidence:.2f} < threshold "
                    f"{self.config.confidence_threshold:.2f}, recommending recursion"
                )
            else:
                result.reasoning.append(
                    f"Analysis complete at confidence {result.final_confidence:.2f}"
                )

        result.total_duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "depth_cycle_complete",
            recursion=result.recursion_count,
            depths_analyzed=len(result.depth_analyses),
            final_confidence=result.final_confidence,
            reached_synthesis=result.reached_synthesis,
            should_recurse=result.should_recurse,
            crystallization_hits=result.crystallization_hits,
            total_duration_ms=result.total_duration_ms,
        )

        return result

    async def run_recursive_analysis(
        self,
        problem_statement: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> DepthCycleResult:
        """
        Run analysis with recursive deepening until confidence threshold or max recursions.

        This is the "7th step" - if synthesis doesn't reach threshold,
        we recurse, but each recursion BUILDS ON the previous.

        Args:
            problem_statement: The problem to analyze
            context: Optional additional context

        Returns:
            Final DepthCycleResult after recursions
        """
        current_result: Optional[DepthCycleResult] = None
        all_reasoning: List[str] = []

        while True:
            result = await self.run_depth_cycle(
                problem_statement=problem_statement,
                context=context,
                previous_cycle=current_result,
            )

            all_reasoning.extend(result.reasoning)

            if not result.should_recurse:
                # We're done - combine all reasoning
                result.reasoning = all_reasoning
                logger.info(
                    "recursive_analysis_complete",
                    total_recursions=result.recursion_count,
                    final_confidence=result.final_confidence,
                )
                return result

            # Prepare for recursion
            current_result = result

    async def _get_crystallized_hints(
        self,
        problem_statement: str,
        problem_type: str,
    ) -> List[Dict[str, Any]]:
        """Get hints from crystallized truths for this problem."""
        hints = []

        if self.evidence_gatherer.crystallization_store:
            try:
                results = await self.evidence_gatherer.crystallization_store.search(
                    query=problem_statement,
                    limit=self.config.crystallization_search_limit,
                    filters={"problem_type": problem_type},
                )
                hints = results
            except Exception as e:
                logger.warning("crystallization_hint_fetch_failed", error=str(e))

        return hints

    def _extract_insights(self, analysis: DepthAnalysis) -> List[str]:
        """Extract key insights from a depth analysis."""
        insights = []

        # Insight from accepted hypotheses
        accepted = [h for h in analysis.hypotheses if h.status == HypothesisStatus.ACCEPTED]
        for h in accepted[:3]:  # Top 3
            insights.append(f"[{analysis.depth.name}] Accepted: {h.statement[:100]}")

        # Insight from crystallized evidence
        crystallized = [e for e in analysis.evidence if e.is_crystallized]
        if crystallized:
            insights.append(
                f"[{analysis.depth.name}] Found {len(crystallized)} similar past cases"
            )

        # Insight from high-confidence hypotheses
        high_conf = [h for h in analysis.hypotheses if h.confidence > 0.8]
        if high_conf and high_conf[0] not in accepted:
            insights.append(
                f"[{analysis.depth.name}] High confidence candidate: {high_conf[0].statement[:100]}"
            )

        return insights


# Factory function
def create_depth_system(
    decomposer: Optional[ProblemDecomposer] = None,
    hypothesizer: Optional[HypothesisGenerator] = None,
    evidence_gatherer: Optional[EvidenceGatherer] = None,
    weigher: Optional[HypothesisWeigher] = None,
    config: Optional[RedOwlConfig] = None,
    llm_provider: Optional[Any] = None,
) -> DepthAnalysisSystem:
    """Create a depth analysis system with defaults."""
    from .decomposer import create_decomposer
    from .hypothesizer import create_hypothesizer
    from .evidence import create_evidence_gatherer
    from .weigher import create_weigher

    return DepthAnalysisSystem(
        decomposer=decomposer or create_decomposer(llm_provider),
        hypothesizer=hypothesizer or create_hypothesizer(llm_provider),
        evidence_gatherer=evidence_gatherer or create_evidence_gatherer(),
        weigher=weigher or create_weigher(),
        config=config or RedOwlConfig(),
    )
