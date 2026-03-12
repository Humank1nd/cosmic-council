"""
RED OWL (WHY) - Core Data Models.

Red Owl is the RED Enterprise in the ROYGBV hierarchy.
The Seeker of Truth - Gathers foundational knowledge and asks the right questions.

═══════════════════════════════════════════════════════════════════════════════
COSMIC IDENTITY
═══════════════════════════════════════════════════════════════════════════════

Chakra: Muladhara (Root) - Stability, Foundation, Deep Understanding
Gemstone: Ruby - Wisdom, Protection, Clarity, Intelligence, Awareness
Quantum Principle: Quantum Entanglement
Element: Air
Frequency: 432Hz
Color: Red (#FF0000)

Core Energy: Grounding, Stability, Truth-Seeking

    The Root Chakra grounds the entire system. Red Owl embodies this grounding
    energy by establishing stable foundations of knowledge before any action
    is taken. Truth-seeking is not mere curiosity—it is the stabilizing force
    that prevents the system from building on false premises.

    Energy Flow:
    - Grounding: Anchors all analysis in verifiable reality
    - Stability: Provides consistent, reliable knowledge foundations
    - Truth-Seeking: Drives the relentless pursuit of accurate information

───────────────────────────────────────────────────────────────────────────────
QUANTUM ENTANGLEMENT - "Everything is interconnected, even across vast distances."
───────────────────────────────────────────────────────────────────────────────

Quantum Meaning:
    In quantum physics, entangled particles remain instantaneously connected,
    no matter how far apart they are. A change in one particle immediately
    affects the other, suggesting a hidden network of interdependence.

Application to Cosmic Council:
    - Knowledge is never isolated—everything is interconnected.
    - Researching one aspect of a problem reveals hidden connections to other fields.
    - Ideas, people, and technologies are entangled, so insights from one
      discipline can transform another.

Examples:
    - Studying ancient philosophy might unlock insights for modern AI ethics.
    - Social, economic, and technological systems are deeply interwoven—
      one shift can ripple through the rest.

Cycle Position: 1️⃣ The starting point of inquiry and deep connections.
    → Feeds into Quantum Tunneling (Orange Orangutan)

───────────────────────────────────────────────────────────────────────────────
SPIRIT ANIMAL ARCHETYPE - The Owl 🦉
───────────────────────────────────────────────────────────────────────────────

Totem: The Seeker of Truth
Natural Strength: Observation, Insight, Awareness

Why the Owl?
    - Owls symbolize deep wisdom and perception—seeing what others overlook.
    - They operate in the dark, uncovering hidden truths in silence.
    - Their 360° vision represents holistic awareness, mirroring how knowledge
      must be comprehensive and unbiased.

How the Owl Guides the Council:
    - Asks the right questions—peeling back layers of misinformation.
    - Sees connections others miss, uncovering hidden relationships in knowledge.
    - Works in stillness, absorbing and processing information deeply.

Example:
    A researcher investigating patterns in ancient civilizations to uncover
    new breakthroughs in sustainable architecture.

Guiding Thought: "Knowledge is power, but only if you seek beyond the obvious."

═══════════════════════════════════════════════════════════════════════════════
ROLE & PURPOSE
═══════════════════════════════════════════════════════════════════════════════

Role: Research & Knowledge Gathering
Guiding Question: "What do we not yet know, and where must we look to find it?"

Function:
- Researches the root causes of problems
- Ensures information is unbiased, factual, and well-sourced
- Cross-references multiple disciplines to reveal hidden insights
- Questions validity of all assumptions
- Explores multiple perspectives to reduce biases

Core Principle: Seek foundational truth through comprehensive research.

═══════════════════════════════════════════════════════════════════════════════
THREE FALSIFIABLE CRITERIA
═══════════════════════════════════════════════════════════════════════════════

1. Hypothesis generation - testable hypotheses are produced
2. Evidence gathering - relevant evidence is collected
3. Root cause identification - genuine root causes are identified

═══════════════════════════════════════════════════════════════════════════════
DEPTH MODEL
═══════════════════════════════════════════════════════════════════════════════

The key insight: root cause analysis isn't a single step - it's a deepening spiral.
Each depth level builds on the previous, creating genuine understanding rather
than retries. This is where shallow systems go to die, and where real systems
start to look different.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class AnalysisDepth(Enum):
    """
    The five levels of root cause analysis depth.

    This is the core innovation: each level answers a different question,
    and each level BUILDS ON the previous level's output.

    This maps to the recursive "7th step" in the Six-Seven Triangle:
    - First pass through depths 1-5 may not reach synthesis
    - If confidence is low, we recurse - but each recursion goes DEEPER
    - Depth is not retry; it's genuine deepening of understanding
    """
    SURFACE = 1       # What happened? (symptoms, observations)
    CAUSAL = 2        # Why did it happen? (immediate causes)
    COUNTERFACTUAL = 3  # What would prevent it? (necessary conditions)
    ADVERSARIAL = 4   # How could this analysis be wrong? (challenge assumptions)
    SYNTHESIS = 5     # Integrated model (unified root cause theory)

    @property
    def question(self) -> str:
        """The core question this depth level answers."""
        questions = {
            AnalysisDepth.SURFACE: "What symptoms and observations are present?",
            AnalysisDepth.CAUSAL: "What immediate causes led to these symptoms?",
            AnalysisDepth.COUNTERFACTUAL: "What conditions were necessary? What would have prevented this?",
            AnalysisDepth.ADVERSARIAL: "How could this analysis be wrong? What are we missing?",
            AnalysisDepth.SYNTHESIS: "What is the unified root cause model?",
        }
        return questions[self]

    @property
    def focus(self) -> str:
        """What this depth level focuses on."""
        focuses = {
            AnalysisDepth.SURFACE: "observation",
            AnalysisDepth.CAUSAL: "mechanism",
            AnalysisDepth.COUNTERFACTUAL: "prevention",
            AnalysisDepth.ADVERSARIAL: "validation",
            AnalysisDepth.SYNTHESIS: "integration",
        }
        return focuses[self]

    @property
    def builds_on(self) -> Optional['AnalysisDepth']:
        """What previous depth this level builds on."""
        if self == AnalysisDepth.SURFACE:
            return None
        return AnalysisDepth(self.value - 1)


class HypothesisStatus(Enum):
    """Status of a hypothesis through the analysis process."""
    PROPOSED = "proposed"      # Initially generated
    EVIDENCED = "evidenced"    # Has supporting evidence
    CHALLENGED = "challenged"  # Has contradicting evidence
    REFINED = "refined"        # Modified based on evidence
    ACCEPTED = "accepted"      # Final accepted hypothesis
    REJECTED = "rejected"      # Ruled out by evidence


class EvidenceType(Enum):
    """Types of evidence that can support or refute hypotheses."""
    LOG_ENTRY = "log_entry"
    METRIC = "metric"
    CRYSTALLIZED_TRUTH = "crystallized_truth"  # Past solved problems - key for compounding
    KB_DOCUMENT = "kb_document"
    USER_REPORT = "user_report"
    PATTERN_MATCH = "pattern_match"
    CORRELATION = "correlation"
    CAUSAL_CHAIN = "causal_chain"
    EXPERT_JUDGMENT = "expert_judgment"


class EvidenceWeight(Enum):
    """How strongly evidence supports or refutes a hypothesis."""
    STRONG_SUPPORT = 3
    MODERATE_SUPPORT = 2
    WEAK_SUPPORT = 1
    NEUTRAL = 0
    WEAK_REFUTE = -1
    MODERATE_REFUTE = -2
    STRONG_REFUTE = -3


@dataclass
class ProblemComponent:
    """A decomposed component of the original problem."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    category: str = ""  # symptom, context, constraint, stakeholder, timeline
    severity: float = 0.5
    relationships: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "severity": self.severity,
            "relationships": self.relationships,
            "metadata": self.metadata,
        }


@dataclass
class Hypothesis:
    """A candidate root cause hypothesis."""
    id: str = field(default_factory=lambda: str(uuid4()))
    statement: str = ""
    depth: AnalysisDepth = AnalysisDepth.SURFACE
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    confidence: float = 0.5
    evidence_ids: List[str] = field(default_factory=list)
    supporting_score: float = 0.0
    refuting_score: float = 0.0
    reasoning_chain: List[str] = field(default_factory=list)
    parent_hypothesis_id: Optional[str] = None
    components_addressed: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def net_evidence_score(self) -> float:
        """Net score from evidence."""
        return self.supporting_score - self.refuting_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "statement": self.statement,
            "depth": self.depth.name,
            "depth_value": self.depth.value,
            "status": self.status.value,
            "confidence": self.confidence,
            "evidence_ids": self.evidence_ids,
            "supporting_score": self.supporting_score,
            "refuting_score": self.refuting_score,
            "net_evidence_score": self.net_evidence_score,
            "reasoning_chain": self.reasoning_chain,
            "parent_hypothesis_id": self.parent_hypothesis_id,
            "components_addressed": self.components_addressed,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Evidence:
    """A piece of evidence that supports or refutes hypotheses."""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: EvidenceType = EvidenceType.LOG_ENTRY
    source: str = ""
    content: str = ""
    summary: str = ""
    weight: EvidenceWeight = EvidenceWeight.NEUTRAL
    relevance: float = 0.5
    hypothesis_ids: List[str] = field(default_factory=list)
    retrieved_at: datetime = field(default_factory=datetime.utcnow)
    is_crystallized: bool = False  # True if from past crystallized truths
    crystallization_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "source": self.source,
            "content": self.content,
            "summary": self.summary,
            "weight": self.weight.name,
            "weight_value": self.weight.value,
            "relevance": self.relevance,
            "hypothesis_ids": self.hypothesis_ids,
            "retrieved_at": self.retrieved_at.isoformat(),
            "is_crystallized": self.is_crystallized,
            "crystallization_id": self.crystallization_id,
        }


@dataclass
class DepthAnalysis:
    """The analysis produced at a specific depth level."""
    id: str = field(default_factory=lambda: str(uuid4()))
    depth: AnalysisDepth = AnalysisDepth.SURFACE
    hypotheses: List[Hypothesis] = field(default_factory=list)
    evidence: List[Evidence] = field(default_factory=list)
    reasoning_chain: List[str] = field(default_factory=list)
    key_insights: List[str] = field(default_factory=list)
    confidence: float = 0.5
    builds_on_id: Optional[str] = None
    duration_ms: int = 0
    llm_calls: int = 0
    crystallization_hits: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def accepted_hypotheses(self) -> List[Hypothesis]:
        """Get hypotheses that were accepted at this depth."""
        return [h for h in self.hypotheses if h.status == HypothesisStatus.ACCEPTED]

    @property
    def top_hypothesis(self) -> Optional[Hypothesis]:
        """Get the highest confidence hypothesis."""
        if not self.hypotheses:
            return None
        return max(self.hypotheses, key=lambda h: h.confidence)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "depth": self.depth.name,
            "depth_value": self.depth.value,
            "depth_question": self.depth.question,
            "depth_focus": self.depth.focus,
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "evidence": [e.to_dict() for e in self.evidence],
            "reasoning_chain": self.reasoning_chain,
            "key_insights": self.key_insights,
            "confidence": self.confidence,
            "builds_on_id": self.builds_on_id,
            "duration_ms": self.duration_ms,
            "llm_calls": self.llm_calls,
            "crystallization_hits": self.crystallization_hits,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class RootCauseAnalysis:
    """
    Complete root cause analysis across all depth levels.

    This is the primary output of Red Owl - a structured, auditable
    analysis that shows HOW we arrived at the root cause, not just
    what we think it is.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    problem_id: str = ""
    problem_statement: str = ""
    components: List[ProblemComponent] = field(default_factory=list)
    depth_analyses: List[DepthAnalysis] = field(default_factory=list)

    # Final outputs
    final_root_cause: Optional[str] = None
    final_confidence: float = 0.0
    final_reasoning: List[str] = field(default_factory=list)

    # Metrics for the three falsifiable criteria
    crystallization_hits: int = 0  # Retrieval from past solutions
    total_evidence_gathered: int = 0
    total_hypotheses_generated: int = 0
    total_hypotheses_accepted: int = 0
    max_depth_reached: AnalysisDepth = AnalysisDepth.SURFACE
    recursion_count: int = 0  # How many times we recursed through depths

    # Timing
    total_duration_ms: int = 0
    total_llm_calls: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def retrieval_rate(self) -> float:
        """Rate of crystallization hits vs total evidence - key metric for compounding."""
        if self.total_evidence_gathered == 0:
            return 0.0
        return self.crystallization_hits / self.total_evidence_gathered

    @property
    def hypothesis_acceptance_rate(self) -> float:
        """Rate of accepted vs generated hypotheses."""
        if self.total_hypotheses_generated == 0:
            return 0.0
        return self.total_hypotheses_accepted / self.total_hypotheses_generated

    @property
    def depth_progression(self) -> List[str]:
        """Show how analysis deepened across recursions."""
        return [f"Depth {da.depth.value}: {da.depth.name}" for da in self.depth_analyses]

    def get_depth_analysis(self, depth: AnalysisDepth) -> Optional[DepthAnalysis]:
        """Get analysis for a specific depth level."""
        for da in self.depth_analyses:
            if da.depth == depth:
                return da
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "problem_id": self.problem_id,
            "problem_statement": self.problem_statement,
            "components": [c.to_dict() for c in self.components],
            "depth_analyses": [da.to_dict() for da in self.depth_analyses],
            "final_root_cause": self.final_root_cause,
            "final_confidence": self.final_confidence,
            "final_reasoning": self.final_reasoning,
            "crystallization_hits": self.crystallization_hits,
            "total_evidence_gathered": self.total_evidence_gathered,
            "total_hypotheses_generated": self.total_hypotheses_generated,
            "total_hypotheses_accepted": self.total_hypotheses_accepted,
            "max_depth_reached": self.max_depth_reached.name,
            "recursion_count": self.recursion_count,
            "retrieval_rate": self.retrieval_rate,
            "hypothesis_acceptance_rate": self.hypothesis_acceptance_rate,
            "depth_progression": self.depth_progression,
            "total_duration_ms": self.total_duration_ms,
            "total_llm_calls": self.total_llm_calls,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class RedOwlConfig:
    """Configuration for Red Owl analysis."""
    # Depth control
    min_depth: AnalysisDepth = AnalysisDepth.CAUSAL
    max_depth: AnalysisDepth = AnalysisDepth.SYNTHESIS
    confidence_threshold: float = 0.7  # Minimum confidence to accept

    # Recursion control (the "7th step")
    max_recursions: int = 3
    recursion_confidence_boost: float = 0.1  # Required improvement per recursion

    # Evidence gathering
    max_evidence_per_hypothesis: int = 10
    crystallization_search_limit: int = 20

    # Hypothesis generation
    max_hypotheses_per_depth: int = 5
    hypothesis_pruning_threshold: float = 0.3

    # LLM settings
    llm_temperature: float = 0.4
    llm_max_tokens: int = 2000

    # Timeouts
    depth_timeout_seconds: float = 30.0
    total_timeout_seconds: float = 120.0


@dataclass
class RedOwlBenchmarkCase:
    """A benchmark case for testing Red Owl accuracy."""
    id: str = field(default_factory=lambda: str(uuid4()))
    problem: str = ""
    known_root_cause: str = ""
    difficulty: str = "medium"  # easy, medium, hard
    domain: str = ""
    expected_depth: AnalysisDepth = AnalysisDepth.CAUSAL
    tags: List[str] = field(default_factory=list)


@dataclass
class RedOwlEvalResult:
    """Evaluation result for a Red Owl analysis."""
    benchmark_id: str = ""
    analysis_id: str = ""
    accuracy: float = 0.0
    depth_reached: AnalysisDepth = AnalysisDepth.SURFACE
    reasoning_quality: float = 0.0
    retrieval_rate: float = 0.0
    time_to_insight_ms: int = 0
    passed: bool = False
    feedback: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "analysis_id": self.analysis_id,
            "accuracy": self.accuracy,
            "depth_reached": self.depth_reached.name,
            "reasoning_quality": self.reasoning_quality,
            "retrieval_rate": self.retrieval_rate,
            "time_to_insight_ms": self.time_to_insight_ms,
            "passed": self.passed,
            "feedback": self.feedback,
        }
