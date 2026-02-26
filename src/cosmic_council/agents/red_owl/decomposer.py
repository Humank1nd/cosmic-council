"""
RED OWL - Problem Decomposer.

Breaks a problem statement into its constituent components:
- Symptoms (what's observed)
- Context (environmental factors)
- Constraints (limitations and requirements)
- Stakeholders (who's affected)
- Timeline (when things happened)

This is the first step in genuine root cause analysis.
The quality of decomposition determines the quality of everything that follows.
"""

import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import structlog

from .models import ProblemComponent

logger = structlog.get_logger(__name__)


@dataclass
class DecompositionResult:
    """Result of decomposing a problem."""
    components: List[ProblemComponent] = field(default_factory=list)
    raw_entities: Dict[str, List[str]] = field(default_factory=dict)
    problem_type: str = "unknown"
    complexity_score: float = 0.5
    decomposition_confidence: float = 0.5
    duration_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "components": [c.to_dict() for c in self.components],
            "raw_entities": self.raw_entities,
            "problem_type": self.problem_type,
            "complexity_score": self.complexity_score,
            "decomposition_confidence": self.decomposition_confidence,
            "duration_ms": self.duration_ms,
        }


class ProblemDecomposer:
    """
    Decomposes problem statements into structured components.

    Uses a combination of:
    - Pattern matching for common problem structures
    - Entity extraction for key elements
    - LLM analysis for deeper decomposition (when available)
    """

    # Problem type patterns
    PROBLEM_PATTERNS = {
        "performance": [
            r"slow", r"latency", r"timeout", r"delay", r"lag",
            r"high cpu", r"high memory", r"resource", r"bottleneck",
        ],
        "availability": [
            r"down", r"unavailable", r"outage", r"crash", r"fail",
            r"unreachable", r"offline", r"error rate",
        ],
        "security": [
            r"breach", r"attack", r"unauthorized", r"vulnerability",
            r"exploit", r"intrusion", r"suspicious", r"malicious",
        ],
        "data": [
            r"corrupt", r"inconsistent", r"missing", r"duplicate",
            r"wrong", r"incorrect", r"data loss", r"integrity",
        ],
        "integration": [
            r"api", r"connection", r"sync", r"webhook",
            r"authentication", r"authorization", r"rate limit",
        ],
        "configuration": [
            r"config", r"setting", r"environment", r"deploy",
            r"misconfigur", r"wrong value", r"invalid",
        ],
        "logic": [
            r"bug", r"incorrect behavior", r"unexpected", r"wrong result",
            r"edge case", r"race condition", r"deadlock",
        ],
        "scaling": [
            r"capacity", r"overload", r"throttl", r"limit",
            r"scale", r"growth", r"traffic spike",
        ],
    }

    # Entity extraction patterns
    ENTITY_PATTERNS = {
        "service": r"\b([A-Z][a-z]+(?:Service|API|Server|Client|Worker|Handler|Manager))\b",
        "error_code": r"\b((?:HTTP\s*)?[45]\d{2}|ERR[_-]?\w+|E\d{4,})\b",
        "time_reference": r"\b(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?|\d+\s*(?:seconds?|minutes?|hours?|days?)\s*ago|yesterday|today|since\s+\w+)\b",
        "metric": r"\b(\d+(?:\.\d+)?(?:\s*)?(?:%|ms|s|MB|GB|KB|req/s|ops/s|QPS|TPS|rps))\b",
        "user_count": r"\b(\d+)\s*(?:users?|customers?|clients?|requests?)\b",
        "component": r"\b(database|cache|queue|load\s*balancer|proxy|gateway|cluster|node|pod|container|redis|postgres|mysql|kafka|rabbitmq)\b",
        "environment": r"\b(prod(?:uction)?|stag(?:ing)?|dev(?:elopment)?|test(?:ing)?|qa|uat)\b",
    }

    # Severity indicators
    SEVERITY_INDICATORS = {
        "critical": (["critical", "severe", "emergency", "p0", "sev1", "all users", "complete outage", "total failure"], 1.0),
        "high": (["high", "major", "significant", "p1", "sev2", "many users", "partial outage", "widespread"], 0.8),
        "medium": (["medium", "moderate", "p2", "sev3", "some users", "degraded", "intermittent"], 0.5),
        "low": (["low", "minor", "p3", "sev4", "few users", "occasional", "rare"], 0.3),
    }

    def __init__(self, llm_provider: Optional[Any] = None):
        """
        Initialize the decomposer.

        Args:
            llm_provider: Optional LLM provider for deeper analysis
        """
        self.llm_provider = llm_provider
        logger.info("problem_decomposer_initialized", has_llm=llm_provider is not None)

    async def decompose(
        self,
        problem_statement: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> DecompositionResult:
        """
        Decompose a problem statement into components.

        Args:
            problem_statement: The problem to analyze
            context: Optional additional context

        Returns:
            DecompositionResult with structured components
        """
        start_time = time.time()
        context = context or {}
        result = DecompositionResult()

        normalized = problem_statement.lower().strip()

        # 1. Identify problem type
        result.problem_type = self._identify_problem_type(normalized)

        # 2. Extract entities
        result.raw_entities = self._extract_entities(problem_statement)

        # 3. Extract severity
        severity = self._extract_severity(normalized)

        # 4. Build components
        components = []

        # Add symptom components
        symptoms = self._extract_symptoms(problem_statement)
        for i, symptom in enumerate(symptoms):
            components.append(ProblemComponent(
                name=f"symptom_{i+1}",
                description=symptom,
                category="symptom",
                severity=severity,
            ))

        # Add entity-based components
        for entity_type, entities in result.raw_entities.items():
            for entity in entities:
                components.append(ProblemComponent(
                    name=entity_type,
                    description=entity,
                    category=self._map_entity_to_category(entity_type),
                    severity=0.5,
                    metadata={"entity_type": entity_type},
                ))

        # Add context components
        if context:
            for key, value in context.items():
                if isinstance(value, str) and value:
                    components.append(ProblemComponent(
                        name=key,
                        description=str(value),
                        category="context",
                        severity=0.5,
                        metadata={"source": "provided_context"},
                    ))

        # 5. Build relationships
        components = self._build_relationships(components)

        # 6. Calculate complexity
        result.complexity_score = self._calculate_complexity(components, problem_statement)

        # 7. LLM enhancement if available
        if self.llm_provider:
            components = await self._enhance_with_llm(problem_statement, components)
            result.decomposition_confidence = 0.85
        else:
            result.decomposition_confidence = 0.65

        result.components = components
        result.duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "problem_decomposed",
            problem_type=result.problem_type,
            component_count=len(components),
            complexity=result.complexity_score,
            confidence=result.decomposition_confidence,
            duration_ms=result.duration_ms,
        )

        return result

    def _identify_problem_type(self, normalized: str) -> str:
        """Identify the type of problem based on patterns."""
        type_scores: Dict[str, int] = {}

        for problem_type, patterns in self.PROBLEM_PATTERNS.items():
            score = sum(1 for p in patterns if re.search(p, normalized))
            if score > 0:
                type_scores[problem_type] = score

        if not type_scores:
            return "unknown"

        return max(type_scores, key=type_scores.get)

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from the problem statement."""
        entities: Dict[str, List[str]] = {}

        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                unique_matches = list(dict.fromkeys(matches))
                entities[entity_type] = unique_matches

        return entities

    def _extract_severity(self, normalized: str) -> float:
        """Extract severity level from the problem statement."""
        for severity_level, (indicators, score) in self.SEVERITY_INDICATORS.items():
            for indicator in indicators:
                if indicator in normalized:
                    return score
        return 0.5

    def _extract_symptoms(self, text: str) -> List[str]:
        """Extract symptom descriptions from the text."""
        symptoms = []
        sentences = re.split(r'[.;]|\band\b|\bbut\b', text)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:
                symptom_indicators = [
                    "is", "are", "was", "were", "not working", "failing",
                    "error", "issue", "problem", "unable", "cannot", "can't",
                    "slow", "high", "low", "increased", "decreased",
                    "returning", "showing", "displaying", "causing",
                ]
                if any(ind in sentence.lower() for ind in symptom_indicators):
                    symptoms.append(sentence)

        if not symptoms:
            symptoms = [text.strip()]

        return symptoms[:5]

    def _map_entity_to_category(self, entity_type: str) -> str:
        """Map entity type to component category."""
        category_map = {
            "service": "component",
            "error_code": "symptom",
            "time_reference": "timeline",
            "metric": "symptom",
            "user_count": "impact",
            "component": "component",
            "environment": "context",
        }
        return category_map.get(entity_type, "context")

    def _build_relationships(self, components: List[ProblemComponent]) -> List[ProblemComponent]:
        """Build relationships between components."""
        by_category: Dict[str, List[ProblemComponent]] = {}
        for comp in components:
            by_category.setdefault(comp.category, []).append(comp)

        symptoms = by_category.get("symptom", [])
        comp_components = by_category.get("component", [])

        for symptom in symptoms:
            for comp in comp_components:
                if comp.description.lower() in symptom.description.lower():
                    symptom.relationships.append(comp.id)
                    comp.relationships.append(symptom.id)

        return components

    def _calculate_complexity(self, components: List[ProblemComponent], text: str) -> float:
        """Calculate problem complexity score."""
        factors = [
            len(components) / 10,
            len(text) / 500,
            len(set(c.category for c in components)) / 5,
            sum(1 for c in components if c.relationships) / max(len(components), 1),
        ]

        complexity = sum(factors) / len(factors)
        return min(max(complexity, 0.1), 1.0)

    async def _enhance_with_llm(
        self,
        problem_statement: str,
        components: List[ProblemComponent],
    ) -> List[ProblemComponent]:
        """Enhance decomposition using LLM analysis."""
        if not self.llm_provider:
            return components

        try:
            from ..hierarchical_enterprise import LLMRequest, LLMMessage

            prompt = f"""Analyze this problem and identify additional components not yet captured.

Problem: {problem_statement}

Already identified:
{chr(10).join(f'- [{c.category}] {c.description}' for c in components)}

Identify any missing:
1. Hidden symptoms
2. Affected systems
3. Timeline details
4. Stakeholder impacts
5. Environmental factors

Format: One component per line as "CATEGORY: description"
Categories: symptom, component, timeline, impact, context"""

            request = LLMRequest(
                messages=[
                    LLMMessage(role="system", content="You are a problem decomposition specialist."),
                    LLMMessage(role="user", content=prompt),
                ],
                temperature=0.3,
            )

            response = await self.llm_provider.generate(request)

            # Parse response and add components
            for line in response.content.split("\n"):
                line = line.strip()
                if ":" in line and len(line) > 5:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        category = parts[0].strip().lower()
                        description = parts[1].strip()
                        if category in ["symptom", "component", "timeline", "impact", "context"]:
                            components.append(ProblemComponent(
                                name=f"llm_{category}",
                                description=description,
                                category=category,
                                severity=0.5,
                                metadata={"source": "llm_enhancement"},
                            ))

            logger.info("llm_enhancement_complete", added_components=len([c for c in components if c.metadata.get("source") == "llm_enhancement"]))

        except Exception as e:
            logger.warning("llm_enhancement_failed", error=str(e))

        return components


# Factory function
def create_decomposer(llm_provider: Optional[Any] = None) -> ProblemDecomposer:
    """Create a problem decomposer instance."""
    return ProblemDecomposer(llm_provider=llm_provider)
