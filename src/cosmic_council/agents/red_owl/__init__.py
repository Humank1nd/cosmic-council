"""
RED OWL - Root Cause Analysis Agent.

Red Owl is the RED Enterprise (Level 2) in the Cosmic Council ROYGBV hierarchy.
It answers the fundamental question: WHY did this happen?

This module implements genuine root cause analysis with:
- Multi-depth analysis (SURFACE → CAUSAL → COUNTERFACTUAL → ADVERSARIAL → SYNTHESIS)
- Recursive deepening (the "7th step" in the Six-Seven Triangle)
- Crystallization compounding (learning from past solved problems)
- Evidence-based hypothesis weighing

The Three Falsifiable Criteria:
1. Recursion deepens (not retries) - each depth produces different analysis
2. Crystallization compounds - past solutions boost future analyses
3. E8 constraint - analysis follows the triangle cycle properly

Usage:
    from cosmic_council.agents.red_owl import RedOwlEngine, analyze_problem

    # Quick analysis
    result = await analyze_problem("Database queries are slow")
    print(result.analysis.final_root_cause)

    # Full control
    engine = RedOwlEngine(
        llm_provider=my_llm,
        crystallization_store=my_vector_db,
    )
    result = await engine.analyze("Service X returning 500 errors")

    # As a Cosmic Council Agent
    agent = create_red_owl_rca_agent()
    result = await agent.process_task(context)
"""

# Core models
from .models import (
    # Enums
    AnalysisDepth,
    HypothesisStatus,
    EvidenceType,
    EvidenceWeight,
    # Data classes
    ProblemComponent,
    Hypothesis,
    Evidence,
    DepthAnalysis,
    RootCauseAnalysis,
    # Configuration
    RedOwlConfig,
    # Benchmark types
    RedOwlBenchmarkCase,
    RedOwlEvalResult,
)

# Components
from .decomposer import (
    ProblemDecomposer,
    DecompositionResult,
    create_decomposer,
)

from .hypothesizer import (
    HypothesisGenerator,
    HypothesisGenerationResult,
    create_hypothesizer,
)

from .evidence import (
    EvidenceGatherer,
    EvidenceGatheringResult,
    CrystallizedTruth,
    create_evidence_gatherer,
)

from .weigher import (
    HypothesisWeigher,
    WeighingResult,
    create_weigher,
)

from .depths import (
    DepthAnalysisSystem,
    DepthCycleResult,
    create_depth_system,
)

# Main engine
from .engine import (
    RedOwlEngine,
    RedOwlResult,
    create_red_owl,
    get_red_owl,
    analyze_problem,
)

# Cosmic Council Agent Integration
from .agent import (
    RedOwlRCAAgent,
    create_red_owl_rca_agent,
    get_rca_agent,
)

__all__ = [
    # Enums
    "AnalysisDepth",
    "HypothesisStatus",
    "EvidenceType",
    "EvidenceWeight",
    # Core data classes
    "ProblemComponent",
    "Hypothesis",
    "Evidence",
    "DepthAnalysis",
    "RootCauseAnalysis",
    # Configuration
    "RedOwlConfig",
    # Benchmark types
    "RedOwlBenchmarkCase",
    "RedOwlEvalResult",
    # Component classes
    "ProblemDecomposer",
    "DecompositionResult",
    "HypothesisGenerator",
    "HypothesisGenerationResult",
    "EvidenceGatherer",
    "EvidenceGatheringResult",
    "CrystallizedTruth",
    "HypothesisWeigher",
    "WeighingResult",
    "DepthAnalysisSystem",
    "DepthCycleResult",
    # Engine
    "RedOwlEngine",
    "RedOwlResult",
    # Factory functions
    "create_decomposer",
    "create_hypothesizer",
    "create_evidence_gatherer",
    "create_weigher",
    "create_depth_system",
    "create_red_owl",
    "get_red_owl",
    # Convenience functions
    "analyze_problem",
    # Cosmic Council Agent
    "RedOwlRCAAgent",
    "create_red_owl_rca_agent",
    "get_rca_agent",
]

__version__ = "0.1.0"
