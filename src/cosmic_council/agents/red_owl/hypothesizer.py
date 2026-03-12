"""
RED OWL - Hypothesis Generator.

Generates candidate root cause hypotheses based on:
- Decomposed problem components
- Current analysis depth
- Previous depth's accepted hypotheses (for deepening)
- Retrieved crystallized truths (for compounding)

The key insight: hypothesis generation at each depth level is DIFFERENT.
- SURFACE: What could cause these symptoms?
- CAUSAL: What mechanisms explain the immediate causes?
- COUNTERFACTUAL: What conditions were necessary?
- ADVERSARIAL: What might we be missing?
- SYNTHESIS: How do all the pieces fit together?
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import structlog

from .models import (
    AnalysisDepth,
    Hypothesis,
    HypothesisStatus,
    ProblemComponent,
    DepthAnalysis,
)

logger = structlog.get_logger(__name__)


@dataclass
class HypothesisGenerationResult:
    """Result of hypothesis generation."""
    hypotheses: List[Hypothesis] = field(default_factory=list)
    reasoning: List[str] = field(default_factory=list)
    duration_ms: int = 0
    llm_calls: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


# Depth-specific prompt templates
DEPTH_PROMPTS = {
    AnalysisDepth.SURFACE: """Based on these observed symptoms:
{symptoms}

Generate hypotheses about what could be causing these symptoms.
Focus on: What is the most likely immediate cause?

For each hypothesis, provide:
1. A clear statement of the potential cause
2. Which symptoms it would explain
3. Initial confidence (0.0-1.0)""",

    AnalysisDepth.CAUSAL: """Based on these symptoms and their likely immediate causes:

Symptoms: {symptoms}
Previous hypotheses: {previous_hypotheses}

Go deeper: What MECHANISMS or PROCESSES could explain these causes?
Focus on: WHY would this cause lead to these symptoms?

For each hypothesis, provide:
1. The causal mechanism
2. The chain of causation
3. Confidence (0.0-1.0)""",

    AnalysisDepth.COUNTERFACTUAL: """Based on this causal analysis:

Symptoms: {symptoms}
Causal mechanisms: {previous_hypotheses}

Consider: What conditions were NECESSARY for this to happen?
Focus on: What would have PREVENTED this from occurring?

For each hypothesis, provide:
1. The necessary condition
2. What prevention would look like
3. Confidence (0.0-1.0)""",

    AnalysisDepth.ADVERSARIAL: """Based on this analysis so far:

Symptoms: {symptoms}
Causal chain: {previous_hypotheses}
Necessary conditions: {counterfactual}

Challenge this analysis: What might we be WRONG about?
Focus on: Alternative explanations, hidden assumptions, blind spots.

For each hypothesis, provide:
1. The alternative explanation or challenge
2. What evidence would support/refute it
3. Confidence (0.0-1.0)""",

    AnalysisDepth.SYNTHESIS: """Based on the complete analysis:

Symptoms: {symptoms}
Causal mechanisms: {causal}
Necessary conditions: {counterfactual}
Challenges considered: {adversarial}

Synthesize: What is the UNIFIED ROOT CAUSE MODEL?
Focus on: Integrating all insights into a coherent explanation.

Provide:
1. The integrated root cause statement
2. How it explains all observations
3. Final confidence (0.0-1.0)
4. Key supporting reasoning""",
}


class HypothesisGenerator:
    """
    Generates hypotheses at each depth level of analysis.

    The generator uses different strategies for each depth:
    - SURFACE: Pattern matching + LLM inference from symptoms
    - CAUSAL: Mechanism reasoning from immediate causes
    - COUNTERFACTUAL: Necessity analysis
    - ADVERSARIAL: Devil's advocate / red team
    - SYNTHESIS: Integration and unification
    """

    # Common causal patterns by problem type
    CAUSAL_PATTERNS = {
        "performance": [
            "Resource exhaustion (CPU/memory/disk)",
            "Network latency or congestion",
            "Database query inefficiency",
            "Lock contention or deadlock",
            "Garbage collection pressure",
            "Connection pool exhaustion",
        ],
        "availability": [
            "Service crash or OOM",
            "Dependency failure",
            "Network partition",
            "Configuration error",
            "Deployment failure",
            "Resource limits exceeded",
        ],
        "security": [
            "Authentication bypass",
            "Authorization misconfiguration",
            "Credential exposure",
            "Injection vulnerability",
            "Missing input validation",
            "Insecure default settings",
        ],
        "data": [
            "Race condition in write path",
            "Replication lag",
            "Schema mismatch",
            "Encoding/parsing error",
            "Transaction isolation issue",
            "Backup/restore failure",
        ],
        "integration": [
            "API contract violation",
            "Rate limiting triggered",
            "Authentication token expiry",
            "Network timeout",
            "Serialization mismatch",
            "Version incompatibility",
        ],
    }

    def __init__(self, llm_provider: Optional[Any] = None):
        """
        Initialize the hypothesis generator.

        Args:
            llm_provider: Optional LLM provider for sophisticated generation
        """
        self.llm_provider = llm_provider
        logger.info("hypothesis_generator_initialized", has_llm=llm_provider is not None)

    async def generate(
        self,
        depth: AnalysisDepth,
        components: List[ProblemComponent],
        problem_type: str,
        previous_analysis: Optional[DepthAnalysis] = None,
        crystallized_hints: Optional[List[Dict[str, Any]]] = None,
        max_hypotheses: int = 5,
    ) -> HypothesisGenerationResult:
        """
        Generate hypotheses for the given depth level.

        Args:
            depth: The analysis depth to generate for
            components: Problem components from decomposition
            problem_type: Type of problem (performance, security, etc.)
            previous_analysis: Analysis from previous depth (for building on)
            crystallized_hints: Retrieved similar past solutions
            max_hypotheses: Maximum number of hypotheses to generate

        Returns:
            HypothesisGenerationResult with candidate hypotheses
        """
        start_time = time.time()
        result = HypothesisGenerationResult()

        # Extract symptom descriptions
        symptoms = [c.description for c in components if c.category == "symptom"]
        symptoms_str = "\n".join(f"- {s}" for s in symptoms)

        # Build context from previous analysis
        prev_hypotheses_str = ""
        if previous_analysis and previous_analysis.accepted_hypotheses:
            prev_hypotheses_str = "\n".join(
                f"- {h.statement} (confidence: {h.confidence:.2f})"
                for h in previous_analysis.accepted_hypotheses
            )

        # Generate based on depth
        if self.llm_provider:
            hypotheses = await self._generate_with_llm(
                depth=depth,
                symptoms_str=symptoms_str,
                prev_hypotheses_str=prev_hypotheses_str,
                problem_type=problem_type,
                crystallized_hints=crystallized_hints,
                max_hypotheses=max_hypotheses,
            )
            result.llm_calls = 1
        else:
            hypotheses = self._generate_with_patterns(
                depth=depth,
                components=components,
                problem_type=problem_type,
                previous_analysis=previous_analysis,
                crystallized_hints=crystallized_hints,
                max_hypotheses=max_hypotheses,
            )

        # Mark depth and add reasoning
        for h in hypotheses:
            h.depth = depth
            h.components_addressed = [c.id for c in components if c.category == "symptom"]

        result.hypotheses = hypotheses[:max_hypotheses]
        result.reasoning = [
            f"Generated {len(result.hypotheses)} hypotheses at depth {depth.name}",
            f"Problem type: {problem_type}",
            f"Based on {len(symptoms)} symptoms",
        ]
        if previous_analysis:
            result.reasoning.append(f"Building on {len(previous_analysis.accepted_hypotheses)} previous hypotheses")

        result.duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "hypotheses_generated",
            depth=depth.name,
            count=len(result.hypotheses),
            problem_type=problem_type,
            duration_ms=result.duration_ms,
        )

        return result

    async def _generate_with_llm(
        self,
        depth: AnalysisDepth,
        symptoms_str: str,
        prev_hypotheses_str: str,
        problem_type: str,
        crystallized_hints: Optional[List[Dict[str, Any]]],
        max_hypotheses: int,
    ) -> List[Hypothesis]:
        """Generate hypotheses using LLM."""
        hypotheses = []

        try:
            from ..hierarchical_enterprise import LLMRequest, LLMMessage

            # Build prompt based on depth
            template = DEPTH_PROMPTS[depth]
            prompt = template.format(
                symptoms=symptoms_str,
                previous_hypotheses=prev_hypotheses_str or "None yet",
                counterfactual=prev_hypotheses_str or "None yet",
                causal=prev_hypotheses_str or "None yet",
                adversarial=prev_hypotheses_str or "None yet",
            )

            # Add crystallized hints if available
            if crystallized_hints:
                hint_str = "\n".join(
                    f"- Past case: {h.get('problem', 'Unknown')} -> Root cause: {h.get('root_cause', 'Unknown')}"
                    for h in crystallized_hints[:3]
                )
                prompt += f"\n\nSimilar past cases for reference:\n{hint_str}"

            prompt += f"\n\nGenerate up to {max_hypotheses} hypotheses."

            request = LLMRequest(
                messages=[
                    LLMMessage(
                        role="system",
                        content=f"You are Red Owl, the root cause analysis specialist at depth level {depth.name}. "
                        f"Your focus is: {depth.focus}. Question you're answering: {depth.question}",
                    ),
                    LLMMessage(role="user", content=prompt),
                ],
                temperature=0.4,
            )

            response = await self.llm_provider.generate(request)

            # Parse response into hypotheses
            hypotheses = self._parse_llm_response(response.content, depth)

        except Exception as e:
            logger.warning("llm_generation_failed", error=str(e))
            # Fall back to pattern-based
            hypotheses = self._generate_with_patterns(
                depth=depth,
                components=[],
                problem_type=problem_type,
                previous_analysis=None,
                crystallized_hints=crystallized_hints,
                max_hypotheses=max_hypotheses,
            )

        return hypotheses

    def _generate_with_patterns(
        self,
        depth: AnalysisDepth,
        components: List[ProblemComponent],
        problem_type: str,
        previous_analysis: Optional[DepthAnalysis],
        crystallized_hints: Optional[List[Dict[str, Any]]],
        max_hypotheses: int,
    ) -> List[Hypothesis]:
        """Generate hypotheses using pattern matching (fallback when no LLM)."""
        hypotheses = []

        # Get patterns for this problem type
        patterns = self.CAUSAL_PATTERNS.get(problem_type, self.CAUSAL_PATTERNS.get("performance", []))

        if depth == AnalysisDepth.SURFACE:
            # For surface level, generate from patterns
            for i, pattern in enumerate(patterns[:max_hypotheses]):
                hypotheses.append(Hypothesis(
                    statement=f"Potential cause: {pattern}",
                    depth=depth,
                    status=HypothesisStatus.PROPOSED,
                    confidence=0.5 - (i * 0.05),  # Decreasing confidence
                    reasoning_chain=[f"Pattern matched for {problem_type} problems"],
                ))

        elif depth == AnalysisDepth.CAUSAL:
            # Build on previous hypotheses
            if previous_analysis and previous_analysis.accepted_hypotheses:
                for prev_h in previous_analysis.accepted_hypotheses[:max_hypotheses]:
                    hypotheses.append(Hypothesis(
                        statement=f"Mechanism: The cause '{prev_h.statement}' leads to symptoms via cascading failure",
                        depth=depth,
                        status=HypothesisStatus.PROPOSED,
                        confidence=prev_h.confidence * 0.9,
                        parent_hypothesis_id=prev_h.id,
                        reasoning_chain=[f"Building on: {prev_h.statement}"],
                    ))
            else:
                for pattern in patterns[:max_hypotheses]:
                    hypotheses.append(Hypothesis(
                        statement=f"Causal mechanism: {pattern}",
                        depth=depth,
                        status=HypothesisStatus.PROPOSED,
                        confidence=0.4,
                        reasoning_chain=["Generated without previous depth context"],
                    ))

        elif depth == AnalysisDepth.COUNTERFACTUAL:
            if previous_analysis and previous_analysis.accepted_hypotheses:
                for prev_h in previous_analysis.accepted_hypotheses[:max_hypotheses]:
                    hypotheses.append(Hypothesis(
                        statement=f"Prevention: If we had monitored/prevented '{prev_h.statement}', the issue would not have occurred",
                        depth=depth,
                        status=HypothesisStatus.PROPOSED,
                        confidence=prev_h.confidence * 0.85,
                        parent_hypothesis_id=prev_h.id,
                        reasoning_chain=[f"Counterfactual of: {prev_h.statement}"],
                    ))

        elif depth == AnalysisDepth.ADVERSARIAL:
            # Challenge existing hypotheses
            if previous_analysis and previous_analysis.accepted_hypotheses:
                for prev_h in previous_analysis.accepted_hypotheses[:max_hypotheses]:
                    hypotheses.append(Hypothesis(
                        statement=f"Alternative: What if '{prev_h.statement}' is a symptom, not a cause?",
                        depth=depth,
                        status=HypothesisStatus.PROPOSED,
                        confidence=0.3,  # Low confidence for challenges
                        parent_hypothesis_id=prev_h.id,
                        reasoning_chain=["Adversarial challenge to accepted hypothesis"],
                    ))

        elif depth == AnalysisDepth.SYNTHESIS:
            # Combine all insights
            if previous_analysis and previous_analysis.accepted_hypotheses:
                combined = " AND ".join(h.statement for h in previous_analysis.accepted_hypotheses[:3])
                hypotheses.append(Hypothesis(
                    statement=f"Unified root cause: {combined}",
                    depth=depth,
                    status=HypothesisStatus.PROPOSED,
                    confidence=0.7,
                    reasoning_chain=["Synthesis of all accepted hypotheses"],
                ))

        # Add crystallized hints as hypotheses if available
        if crystallized_hints and len(hypotheses) < max_hypotheses:
            for hint in crystallized_hints[:max_hypotheses - len(hypotheses)]:
                hypotheses.append(Hypothesis(
                    statement=f"Similar past case: {hint.get('root_cause', 'Unknown root cause')}",
                    depth=depth,
                    status=HypothesisStatus.PROPOSED,
                    confidence=0.6,
                    reasoning_chain=[f"Based on similar problem: {hint.get('problem', 'Unknown')}"],
                    metadata={"crystallized": True, "source_id": hint.get("id")},
                ))

        return hypotheses

    def _parse_llm_response(self, content: str, depth: AnalysisDepth) -> List[Hypothesis]:
        """Parse LLM response into structured hypotheses."""
        hypotheses = []
        lines = content.strip().split("\n")

        current_statement = None
        current_confidence = 0.5

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for hypothesis statements
            if line.startswith(("1.", "2.", "3.", "4.", "5.", "-", "*")):
                if current_statement:
                    hypotheses.append(Hypothesis(
                        statement=current_statement,
                        depth=depth,
                        status=HypothesisStatus.PROPOSED,
                        confidence=current_confidence,
                        reasoning_chain=[f"LLM generated at {depth.name} depth"],
                    ))
                current_statement = line.lstrip("0123456789.-* ").strip()
                current_confidence = 0.5

            # Look for confidence values
            if "confidence" in line.lower():
                import re
                match = re.search(r"(\d+\.?\d*)", line)
                if match:
                    conf = float(match.group(1))
                    current_confidence = conf if conf <= 1 else conf / 100

        # Add last hypothesis
        if current_statement:
            hypotheses.append(Hypothesis(
                statement=current_statement,
                depth=depth,
                status=HypothesisStatus.PROPOSED,
                confidence=current_confidence,
                reasoning_chain=[f"LLM generated at {depth.name} depth"],
            ))

        return hypotheses


# Factory function
def create_hypothesizer(llm_provider: Optional[Any] = None) -> HypothesisGenerator:
    """Create a hypothesis generator instance."""
    return HypothesisGenerator(llm_provider=llm_provider)
