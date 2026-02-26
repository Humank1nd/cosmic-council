"""
RED OWL - Root Cause Analysis Engine.

The main orchestrator for Red Owl root cause analysis.
This is the RED Enterprise (Level 2) in the ROYGBV hierarchy,
answering the fundamental question: WHY did this happen?

The engine coordinates:
1. Problem decomposition
2. Multi-depth hypothesis generation
3. Evidence gathering (including crystallized truths)
4. Hypothesis weighing and acceptance
5. Recursive deepening (the "7th step")
6. Final root cause synthesis

Three falsifiable criteria this engine embodies:
1. Recursion deepens (not retries) - each depth produces different analysis
2. Crystallization compounds - past solutions boost future analyses
3. E8 constraint - analysis follows the triangle cycle properly
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

import structlog

from .models import (
    AnalysisDepth,
    DepthAnalysis,
    Evidence,
    Hypothesis,
    HypothesisStatus,
    ProblemComponent,
    RedOwlConfig,
    RootCauseAnalysis,
)
from .decomposer import ProblemDecomposer, create_decomposer
from .hypothesizer import HypothesisGenerator, create_hypothesizer
from .evidence import EvidenceGatherer, create_evidence_gatherer
from .weigher import HypothesisWeigher, create_weigher
from .depths import DepthAnalysisSystem, create_depth_system

logger = structlog.get_logger(__name__)


@dataclass
class RedOwlResult:
    """Complete result from Red Owl analysis."""
    analysis: RootCauseAnalysis
    success: bool = True
    error: Optional[str] = None
    reasoning_summary: List[str] = field(default_factory=list)


class RedOwlEngine:
    """
    The Red Owl Root Cause Analysis Engine.

    Red Owl is the RED Enterprise agent in the Cosmic Council.
    It specializes in answering WHY - the first question in
    the Six-Seven Triangle cycle.

    Usage:
        engine = RedOwlEngine()
        result = await engine.analyze("Service X is returning 500 errors")
        print(result.analysis.final_root_cause)
    """

    def __init__(
        self,
        config: Optional[RedOwlConfig] = None,
        llm_provider: Optional[Any] = None,
        kb_client: Optional[Any] = None,
        log_client: Optional[Any] = None,
        metrics_client: Optional[Any] = None,
        crystallization_store: Optional[Any] = None,
    ):
        """
        Initialize the Red Owl engine.

        Args:
            config: Configuration for analysis behavior
            llm_provider: LLM provider for intelligent generation
            kb_client: Knowledge base client
            log_client: Log search client
            metrics_client: Metrics query client
            crystallization_store: Store for crystallized truths
        """
        self.config = config or RedOwlConfig()
        self.llm_provider = llm_provider

        # Initialize components
        self.decomposer = create_decomposer(llm_provider)
        self.hypothesizer = create_hypothesizer(llm_provider)
        self.evidence_gatherer = create_evidence_gatherer(
            kb_client=kb_client,
            log_client=log_client,
            metrics_client=metrics_client,
            crystallization_store=crystallization_store,
        )
        self.weigher = create_weigher(
            acceptance_threshold=self.config.confidence_threshold,
            rejection_threshold=self.config.hypothesis_pruning_threshold,
        )

        # Create the depth analysis system
        self.depth_system = create_depth_system(
            decomposer=self.decomposer,
            hypothesizer=self.hypothesizer,
            evidence_gatherer=self.evidence_gatherer,
            weigher=self.weigher,
            config=self.config,
            llm_provider=llm_provider,
        )

        logger.info(
            "red_owl_engine_initialized",
            has_llm=llm_provider is not None,
            has_kb=kb_client is not None,
            has_logs=log_client is not None,
            has_metrics=metrics_client is not None,
            has_crystallization=crystallization_store is not None,
            confidence_threshold=self.config.confidence_threshold,
            max_recursions=self.config.max_recursions,
        )

    async def analyze(
        self,
        problem_statement: str,
        context: Optional[Dict[str, Any]] = None,
        problem_id: Optional[str] = None,
    ) -> RedOwlResult:
        """
        Perform root cause analysis on a problem.

        This is the main entry point for Red Owl analysis.

        Args:
            problem_statement: Description of the problem to analyze
            context: Optional additional context (logs, metrics, etc.)
            problem_id: Optional ID for tracking

        Returns:
            RedOwlResult containing the complete analysis
        """
        start_time = time.time()
        problem_id = problem_id or str(uuid4())

        # Initialize the analysis result
        analysis = RootCauseAnalysis(
            problem_id=problem_id,
            problem_statement=problem_statement,
        )

        try:
            logger.info(
                "red_owl_analysis_started",
                problem_id=problem_id,
                statement_length=len(problem_statement),
            )

            # Run recursive depth analysis
            cycle_result = await self.depth_system.run_recursive_analysis(
                problem_statement=problem_statement,
                context=context,
            )

            # Populate the analysis result
            analysis.depth_analyses = cycle_result.depth_analyses
            analysis.crystallization_hits = cycle_result.crystallization_hits
            analysis.total_evidence_gathered = cycle_result.total_evidence
            analysis.total_hypotheses_generated = cycle_result.total_hypotheses
            analysis.recursion_count = cycle_result.recursion_count

            # Extract components from first depth analysis
            if cycle_result.depth_analyses:
                first_analysis = cycle_result.depth_analyses[0]
                # Components were stored during decomposition
                # We'll reconstruct from the depth analysis metadata
                pass

            # Determine final root cause
            if cycle_result.final_hypotheses:
                # Take the highest confidence accepted hypothesis
                best_hypothesis = max(
                    cycle_result.final_hypotheses,
                    key=lambda h: h.confidence
                )
                analysis.final_root_cause = best_hypothesis.statement
                analysis.final_confidence = best_hypothesis.confidence
                analysis.final_reasoning = best_hypothesis.reasoning_chain

                analysis.total_hypotheses_accepted = len(cycle_result.final_hypotheses)
            else:
                # No accepted hypothesis - report the best candidate
                all_hypotheses = []
                for da in cycle_result.depth_analyses:
                    all_hypotheses.extend(da.hypotheses)

                if all_hypotheses:
                    best = max(all_hypotheses, key=lambda h: h.confidence)
                    analysis.final_root_cause = f"[CANDIDATE] {best.statement}"
                    analysis.final_confidence = best.confidence * 0.7  # Penalty for not accepted
                    analysis.final_reasoning = best.reasoning_chain

            # Track max depth reached
            if cycle_result.depth_analyses:
                analysis.max_depth_reached = max(
                    (da.depth for da in cycle_result.depth_analyses),
                    key=lambda d: d.value
                )

            # Calculate total LLM calls
            analysis.total_llm_calls = sum(
                da.llm_calls for da in cycle_result.depth_analyses
            )

            # Finalize
            analysis.total_duration_ms = int((time.time() - start_time) * 1000)
            analysis.completed_at = datetime.utcnow()

            logger.info(
                "red_owl_analysis_complete",
                problem_id=problem_id,
                final_confidence=analysis.final_confidence,
                depth_reached=analysis.max_depth_reached.name,
                recursion_count=analysis.recursion_count,
                crystallization_hits=analysis.crystallization_hits,
                retrieval_rate=analysis.retrieval_rate,
                duration_ms=analysis.total_duration_ms,
            )

            return RedOwlResult(
                analysis=analysis,
                success=True,
                reasoning_summary=cycle_result.reasoning,
            )

        except Exception as e:
            logger.error(
                "red_owl_analysis_failed",
                problem_id=problem_id,
                error=str(e),
            )

            analysis.total_duration_ms = int((time.time() - start_time) * 1000)
            analysis.metadata["error"] = str(e)

            return RedOwlResult(
                analysis=analysis,
                success=False,
                error=str(e),
            )

    async def quick_analyze(
        self,
        problem_statement: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform a quick analysis returning just the essentials.

        Useful for integrations that just need the root cause.

        Args:
            problem_statement: Description of the problem
            context: Optional additional context

        Returns:
            Dict with root_cause, confidence, and key insights
        """
        result = await self.analyze(problem_statement, context)

        return {
            "root_cause": result.analysis.final_root_cause,
            "confidence": result.analysis.final_confidence,
            "depth_reached": result.analysis.max_depth_reached.name,
            "crystallization_hits": result.analysis.crystallization_hits,
            "insights": [
                insight
                for da in result.analysis.depth_analyses
                for insight in da.key_insights
            ][:5],  # Top 5 insights
            "success": result.success,
            "duration_ms": result.analysis.total_duration_ms,
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics about engine usage."""
        return {
            "config": {
                "min_depth": self.config.min_depth.name,
                "max_depth": self.config.max_depth.name,
                "confidence_threshold": self.config.confidence_threshold,
                "max_recursions": self.config.max_recursions,
            },
            "capabilities": {
                "has_llm": self.llm_provider is not None,
                "has_kb": self.evidence_gatherer.kb_client is not None,
                "has_logs": self.evidence_gatherer.log_client is not None,
                "has_metrics": self.evidence_gatherer.metrics_client is not None,
                "has_crystallization": self.evidence_gatherer.crystallization_store is not None,
            },
        }


# Factory function
def create_red_owl(
    config: Optional[RedOwlConfig] = None,
    llm_provider: Optional[Any] = None,
    kb_client: Optional[Any] = None,
    log_client: Optional[Any] = None,
    metrics_client: Optional[Any] = None,
    crystallization_store: Optional[Any] = None,
) -> RedOwlEngine:
    """Create a Red Owl engine instance."""
    return RedOwlEngine(
        config=config,
        llm_provider=llm_provider,
        kb_client=kb_client,
        log_client=log_client,
        metrics_client=metrics_client,
        crystallization_store=crystallization_store,
    )


# Global instance for simple usage
_default_engine: Optional[RedOwlEngine] = None


def get_red_owl() -> RedOwlEngine:
    """Get the default Red Owl engine instance."""
    global _default_engine
    if _default_engine is None:
        _default_engine = create_red_owl()
    return _default_engine


async def analyze_problem(
    problem_statement: str,
    context: Optional[Dict[str, Any]] = None,
) -> RedOwlResult:
    """
    Convenience function to analyze a problem.

    Usage:
        result = await analyze_problem("Database queries are slow")
        print(result.analysis.final_root_cause)
    """
    engine = get_red_owl()
    return await engine.analyze(problem_statement, context)
