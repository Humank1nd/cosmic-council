"""
Research & Inquiry Hub - Muladhara (Red Owl) Knowledge Repository.

"The pursuit of knowledge is the foundation of all wisdom."

This module provides the Knowledge Repository for the Red Owl agent,
enabling structured research storage, quantum-inspired knowledge mapping,
and interdisciplinary inquiry frameworks.

===============================================================================
MULADHARA - THE SEEKER OF TRUTH
===============================================================================

Chakra: Muladhara (Root) - Foundation, Stability, Grounding
Spirit Animal: Red Owl - Deep Perception, Hidden Knowledge, Truth Seeking
Quantum Principle: Quantum Entanglement - All knowledge is connected

Core Functions:
- Gather foundational knowledge
- Explore complex problems
- Uncover hidden connections
- Map interdisciplinary insights

===============================================================================
KNOWLEDGE REPOSITORY STRUCTURE
===============================================================================

    +-----------------------------------------------------------------+
    |                    RESEARCH & INQUIRY HUB                        |
    +-----------------------------------------------------------------+
    |                                                                  |
    |   +-------------------+    +-------------------+                |
    |   | Research Findings |    | Quantum Concepts  |                |
    |   | (Firebase)        |    | & Metaphors       |                |
    |   +-------------------+    +-------------------+                |
    |           |                        |                            |
    |   +-------------------+    +-------------------+                |
    |   | Past Iterations   |    | Guiding Questions |                |
    |   | & Key Insights    |    | & Problem Mapping |                |
    |   +-------------------+    +-------------------+                |
    |           |                        |                            |
    |   +-------+------------------------+-------+                    |
    |   |          References & Literature       |                    |
    |   +----------------------------------------+                    |
    |                                                                  |
    +-----------------------------------------------------------------+

===============================================================================
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from .firebase_automation import (
    FirebaseClient,
    MockFirebaseClient,
    ResearchRecord,
    TotemDatabaseManager,
)

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS & TYPES
# =============================================================================

class ResearchDomain(Enum):
    """Core research domains for the Knowledge Repository."""
    AI_ETHICS = "ai_ethics_governance"
    QUANTUM_SYSTEMS = "quantum_systems_thinking"
    COGNITIVE_SCIENCE = "cognitive_decision_making"
    ANCIENT_WISDOM = "ancient_wisdom_integration"
    INTELLIGENCE_NATURE = "nature_of_intelligence"
    CONSCIOUSNESS = "consciousness_studies"
    METAPHYSICS = "metaphysics_philosophy"
    TECHNOLOGY = "technology_innovation"
    SUSTAINABILITY = "sustainability_ecology"
    GOVERNANCE = "governance_policy"


class QuantumPrinciple(Enum):
    """Quantum principles applied to knowledge mapping."""
    ENTANGLEMENT = "entanglement"          # All knowledge is connected
    TUNNELING = "tunneling"                # Barriers can be bypassed
    SUPERPOSITION = "superposition"        # Multiple truths coexist
    WAVE_PARTICLE = "wave_particle"        # Truth depends on observation
    UNCERTAINTY = "uncertainty"            # Limits of knowability
    COHERENCE = "coherence"                # Aligned understanding
    DECOHERENCE = "decoherence"           # Loss of context
    INTERFERENCE = "interference"          # Constructive/destructive patterns


class SourceType(Enum):
    """Types of research sources."""
    ACADEMIC_PAPER = "academic_paper"
    BOOK = "book"
    ARTICLE = "article"
    REPORT = "report"
    DATA_SET = "data_set"
    EXPERIMENT = "experiment"
    INSIGHT = "insight"
    ITERATION = "iteration"
    BREAKTHROUGH = "breakthrough"
    FAILURE_LESSON = "failure_lesson"


class InquiryStatus(Enum):
    """Status of a research inquiry."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    BLOCKED = "blocked"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class QuantumConcept:
    """A quantum concept applied to knowledge understanding."""
    concept_id: str = field(default_factory=lambda: str(uuid4()))
    principle: QuantumPrinciple = QuantumPrinciple.ENTANGLEMENT
    title: str = ""
    description: str = ""
    application: str = ""  # How this applies to problem-solving
    examples: List[str] = field(default_factory=list)
    related_domains: List[ResearchDomain] = field(default_factory=list)
    metaphors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept_id": self.concept_id,
            "principle": self.principle.value,
            "title": self.title,
            "description": self.description,
            "application": self.application,
            "examples": self.examples,
            "related_domains": [d.value for d in self.related_domains],
            "metaphors": self.metaphors,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class GuidingQuestion:
    """A guiding question for deep inquiry."""
    question_id: str = field(default_factory=lambda: str(uuid4()))
    question: str = ""
    domain: ResearchDomain = ResearchDomain.COGNITIVE_SCIENCE
    inquiry_type: str = ""  # foundational, intersectional, overlooked, historical
    sub_questions: List[str] = field(default_factory=list)
    related_research: List[str] = field(default_factory=list)  # Research record IDs
    insights_generated: List[str] = field(default_factory=list)
    status: InquiryStatus = InquiryStatus.OPEN
    priority: int = 1  # 1-5, 5 being highest
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    answered_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "question": self.question,
            "domain": self.domain.value,
            "inquiry_type": self.inquiry_type,
            "sub_questions": self.sub_questions,
            "related_research": self.related_research,
            "insights_generated": self.insights_generated,
            "status": self.status.value,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "answered_at": self.answered_at.isoformat() if self.answered_at else None,
        }


@dataclass
class ResearchIteration:
    """A record of past research iteration or key insight."""
    iteration_id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    iteration_type: str = ""  # breakthrough, refinement, failure, pivot
    domain: ResearchDomain = ResearchDomain.TECHNOLOGY
    key_insights: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    related_questions: List[str] = field(default_factory=list)
    outcome: str = ""  # success, partial, failure
    impact_score: float = 0.0  # 0.0 to 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "iteration_id": self.iteration_id,
            "title": self.title,
            "description": self.description,
            "iteration_type": self.iteration_type,
            "domain": self.domain.value,
            "key_insights": self.key_insights,
            "lessons_learned": self.lessons_learned,
            "related_questions": self.related_questions,
            "outcome": self.outcome,
            "impact_score": self.impact_score,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class LiteratureReference:
    """A reference to external literature or resource."""
    reference_id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    authors: List[str] = field(default_factory=list)
    source_type: SourceType = SourceType.ACADEMIC_PAPER
    domain: ResearchDomain = ResearchDomain.TECHNOLOGY
    publication_date: Optional[datetime] = None
    url: str = ""
    doi: str = ""
    abstract: str = ""
    key_findings: List[str] = field(default_factory=list)
    relevance_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    citations: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference_id": self.reference_id,
            "title": self.title,
            "authors": self.authors,
            "source_type": self.source_type.value,
            "domain": self.domain.value,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "url": self.url,
            "doi": self.doi,
            "abstract": self.abstract,
            "key_findings": self.key_findings,
            "relevance_score": self.relevance_score,
            "tags": self.tags,
            "citations": self.citations,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class KnowledgeNode:
    """A node in the knowledge graph representing a concept or finding."""
    node_id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    node_type: str = ""  # concept, finding, question, insight
    domain: ResearchDomain = ResearchDomain.TECHNOLOGY
    connections: List[str] = field(default_factory=list)  # Other node IDs
    quantum_principles: List[QuantumPrinciple] = field(default_factory=list)
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "title": self.title,
            "description": self.description,
            "node_type": self.node_type,
            "domain": self.domain.value,
            "connections": self.connections,
            "quantum_principles": [q.value for q in self.quantum_principles],
            "confidence": self.confidence,
            "evidence": self.evidence,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ResearchTopic:
    """An active research topic being investigated."""
    topic_id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    domain: ResearchDomain = ResearchDomain.TECHNOLOGY
    status: InquiryStatus = InquiryStatus.OPEN
    priority: int = 1
    year: int = 2025
    guiding_questions: List[str] = field(default_factory=list)
    research_records: List[str] = field(default_factory=list)
    iterations: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    team_members: List[str] = field(default_factory=list)
    progress_percent: float = 0.0
    insights: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic_id": self.topic_id,
            "title": self.title,
            "description": self.description,
            "domain": self.domain.value,
            "status": self.status.value,
            "priority": self.priority,
            "year": self.year,
            "guiding_questions": self.guiding_questions,
            "research_records": self.research_records,
            "iterations": self.iterations,
            "references": self.references,
            "team_members": self.team_members,
            "progress_percent": self.progress_percent,
            "insights": self.insights,
            "next_steps": self.next_steps,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# =============================================================================
# FIREBASE COLLECTIONS
# =============================================================================

class ResearchCollections:
    """Firebase collection names for the Research Hub."""
    RESEARCH_FINDINGS = "research_findings"
    QUANTUM_CONCEPTS = "quantum_concepts"
    GUIDING_QUESTIONS = "guiding_questions"
    ITERATIONS = "research_iterations"
    LITERATURE = "literature_references"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    RESEARCH_TOPICS = "research_topics"


# =============================================================================
# RESEARCH HUB
# =============================================================================

class ResearchInquiryHub:
    """
    The Research & Inquiry Hub for Muladhara (Red Owl).

    Provides:
    - Centralized research storage and retrieval
    - Quantum-inspired knowledge mapping
    - Guiding questions framework
    - Literature management
    - Knowledge graph building
    """

    def __init__(
        self,
        firebase_client: Optional[FirebaseClient] = None,
    ):
        """Initialize the Research Hub."""
        self.firebase = firebase_client or MockFirebaseClient()

        # Initialize with pre-built quantum concepts
        self._quantum_concepts: Dict[str, QuantumConcept] = {}
        self._initialize_quantum_concepts()

        # Initialize default guiding questions
        self._guiding_questions: Dict[str, GuidingQuestion] = {}
        self._initialize_guiding_questions()

        logger.info("ResearchInquiryHub initialized - Muladhara Knowledge Repository active")

    def _initialize_quantum_concepts(self) -> None:
        """Initialize core quantum concepts and metaphors."""
        concepts = [
            QuantumConcept(
                principle=QuantumPrinciple.ENTANGLEMENT,
                title="Quantum Entanglement of Knowledge",
                description="All knowledge is connected—understanding one area unlocks insights in another.",
                application="When studying any topic, actively seek connections to unrelated fields. "
                           "Breakthroughs often come from unexpected intersections.",
                examples=[
                    "Biology principles applied to computer network design",
                    "Ancient philosophy informing AI ethics",
                    "Music theory enhancing mathematical understanding",
                ],
                related_domains=[ResearchDomain.COGNITIVE_SCIENCE, ResearchDomain.ANCIENT_WISDOM],
                metaphors=[
                    "Knowledge nodes are like entangled particles—touch one, affect all",
                    "The web of understanding spans all disciplines",
                ],
            ),
            QuantumConcept(
                principle=QuantumPrinciple.TUNNELING,
                title="Quantum Tunneling Through Barriers",
                description="Barriers in knowledge can be bypassed by finding alternative routes.",
                application="When blocked by complexity or missing information, look for "
                           "indirect paths—analogies, simulations, or cross-domain insights.",
                examples=[
                    "Using game theory to understand evolutionary biology",
                    "Applying fluid dynamics to traffic flow optimization",
                    "Learning foreign concepts through native language metaphors",
                ],
                related_domains=[ResearchDomain.QUANTUM_SYSTEMS, ResearchDomain.TECHNOLOGY],
                metaphors=[
                    "The shortest path is not always visible—tunnel through the barrier",
                    "Knowledge finds a way, even through walls of complexity",
                ],
            ),
            QuantumConcept(
                principle=QuantumPrinciple.WAVE_PARTICLE,
                title="Wave-Particle Duality of Truth",
                description="Truth changes depending on how we observe and measure it.",
                application="Recognize that different methodologies reveal different truths. "
                           "Combine qualitative and quantitative approaches for fuller understanding.",
                examples=[
                    "Statistical analysis vs. case study depth",
                    "Objective measurement vs. subjective experience",
                    "Reductionist vs. holistic perspectives",
                ],
                related_domains=[ResearchDomain.METAPHYSICS, ResearchDomain.CONSCIOUSNESS],
                metaphors=[
                    "The observed becomes the observer's truth",
                    "Reality shifts with the lens of perception",
                ],
            ),
            QuantumConcept(
                principle=QuantumPrinciple.SUPERPOSITION,
                title="Superposition of Possibilities",
                description="Multiple truths and possibilities coexist until collapsed by decision.",
                application="Hold multiple hypotheses simultaneously. Resist premature conclusion. "
                           "Let evidence gradually collapse the superposition of possibilities.",
                examples=[
                    "Maintaining competing theories until data discriminates",
                    "Exploring parallel solution paths before committing",
                    "Balancing optimism and skepticism in research",
                ],
                related_domains=[ResearchDomain.COGNITIVE_SCIENCE, ResearchDomain.AI_ETHICS],
                metaphors=[
                    "All paths exist until one is chosen",
                    "The answer is everywhere and nowhere until measured",
                ],
            ),
            QuantumConcept(
                principle=QuantumPrinciple.UNCERTAINTY,
                title="Heisenberg Uncertainty of Knowledge",
                description="The more precisely we measure one aspect, the less we know about others.",
                application="Recognize trade-offs in research depth vs. breadth. "
                           "Deep expertise in one area may obscure broader patterns.",
                examples=[
                    "Specialization vs. generalization tension",
                    "Detail-oriented analysis missing system-level insights",
                    "Technical accuracy vs. intuitive understanding",
                ],
                related_domains=[ResearchDomain.QUANTUM_SYSTEMS, ResearchDomain.INTELLIGENCE_NATURE],
                metaphors=[
                    "The more you know about the tree, the less you see the forest",
                    "Precision and breadth dance in eternal trade-off",
                ],
            ),
            QuantumConcept(
                principle=QuantumPrinciple.COHERENCE,
                title="Quantum Coherence of Understanding",
                description="Aligned knowledge amplifies insight; misaligned knowledge creates noise.",
                application="Seek conceptual alignment across sources. Build coherent mental models "
                           "that harmonize disparate findings into unified understanding.",
                examples=[
                    "Synthesizing contradictory research into higher-order truth",
                    "Building mental models that accommodate exceptions",
                    "Integrating Eastern and Western philosophical frameworks",
                ],
                related_domains=[ResearchDomain.ANCIENT_WISDOM, ResearchDomain.CONSCIOUSNESS],
                metaphors=[
                    "Coherent knowledge rings like a bell; noise cancels itself",
                    "Truth amplifies when understandings align",
                ],
            ),
        ]

        for concept in concepts:
            self._quantum_concepts[concept.concept_id] = concept

    async def initialize_2025_research_topics(self) -> List[ResearchTopic]:
        """
        Initialize the 2025 Active Research Topics.

        Active Research Topics (2025):
        - AI & Superintelligence Alignment
        - Quantum Ethics & Consciousness
        - Predictive Analytics for Global Trends
        - Collaboration Requests & Open Research Calls
        """
        topics = []

        # Topic 1: AI & Superintelligence Alignment
        topic1 = await self.create_research_topic(
            title="AI & Superintelligence Alignment",
            description=(
                "Research focused on ensuring advanced AI systems remain aligned with "
                "human values, intentions, and well-being. Explores technical alignment "
                "approaches, value learning, interpretability, and governance frameworks "
                "for superintelligent systems."
            ),
            domain=ResearchDomain.AI_ETHICS,
            priority=5,
            year=2025,
            guiding_questions=[
                "How can we formally specify human values for AI systems?",
                "What interpretability methods reveal AI decision-making?",
                "How do we prevent instrumental convergence toward harmful goals?",
                "What governance structures can safely oversee superintelligent systems?",
                "How can we test alignment before deploying advanced AI?",
            ],
        )
        topics.append(topic1)

        # Topic 2: Quantum Ethics & Consciousness
        topic2 = await self.create_research_topic(
            title="Quantum Ethics & Consciousness",
            description=(
                "Exploring the intersection of quantum mechanics, ethics, and consciousness. "
                "Investigates quantum approaches to understanding consciousness, ethical "
                "implications of quantum technologies, and metaphysical questions about "
                "the nature of reality and moral agency in a quantum universe."
            ),
            domain=ResearchDomain.CONSCIOUSNESS,
            priority=4,
            year=2025,
            guiding_questions=[
                "Does quantum mechanics play a role in consciousness?",
                "What are the ethical implications of quantum computing on privacy?",
                "How do quantum principles inform our understanding of free will?",
                "Can quantum entanglement provide insights into interconnected ethics?",
                "What moral framework applies to quantum technology development?",
            ],
        )
        topics.append(topic2)

        # Topic 3: Predictive Analytics for Global Trends
        topic3 = await self.create_research_topic(
            title="Predictive Analytics for Global Trends",
            description=(
                "Leveraging advanced analytics, AI, and systems thinking to forecast "
                "global trends in technology, society, economics, and environment. "
                "Focuses on developing robust models that account for uncertainty, "
                "complex system dynamics, and emergent phenomena."
            ),
            domain=ResearchDomain.TECHNOLOGY,
            priority=4,
            year=2025,
            guiding_questions=[
                "What methods best predict technological disruption timelines?",
                "How can we model complex system interactions for trend forecasting?",
                "What signals indicate impending societal phase transitions?",
                "How do we account for black swan events in predictive models?",
                "What role does collective intelligence play in trend emergence?",
            ],
        )
        topics.append(topic3)

        # Topic 4: Collaboration Requests & Open Research Calls
        topic4 = await self.create_research_topic(
            title="Collaboration Requests & Open Research Calls",
            description=(
                "Meta-research topic for tracking collaboration opportunities, "
                "open research calls, cross-institutional partnerships, and "
                "community-driven inquiry initiatives. Serves as a hub for "
                "connecting researchers across domains."
            ),
            domain=ResearchDomain.GOVERNANCE,
            priority=3,
            year=2025,
            guiding_questions=[
                "What interdisciplinary collaborations would accelerate breakthrough?",
                "How can distributed research teams maintain coherence?",
                "What incentive structures promote open knowledge sharing?",
                "How do we bridge academic, industry, and community research?",
                "What collaboration patterns lead to the most impactful discoveries?",
            ],
        )
        topics.append(topic4)

        logger.info(f"Initialized {len(topics)} 2025 Active Research Topics")
        return topics

    def _initialize_guiding_questions(self) -> None:
        """Initialize core guiding questions for deep inquiry."""
        questions = [
            GuidingQuestion(
                question="What foundational knowledge is required to understand this problem fully?",
                domain=ResearchDomain.COGNITIVE_SCIENCE,
                inquiry_type="foundational",
                sub_questions=[
                    "What are the first principles underlying this domain?",
                    "What prerequisite concepts must be mastered?",
                    "Where are the knowledge gaps in current understanding?",
                ],
                priority=5,
            ),
            GuidingQuestion(
                question="How do different fields of study intersect on this issue?",
                domain=ResearchDomain.QUANTUM_SYSTEMS,
                inquiry_type="intersectional",
                sub_questions=[
                    "What disciplines have studied this phenomenon?",
                    "Where do their conclusions align or conflict?",
                    "What novel insights emerge from cross-pollination?",
                ],
                priority=4,
            ),
            GuidingQuestion(
                question="What are the most overlooked variables influencing this topic?",
                domain=ResearchDomain.COGNITIVE_SCIENCE,
                inquiry_type="overlooked",
                sub_questions=[
                    "What assumptions are being made unconsciously?",
                    "What second and third-order effects are being ignored?",
                    "Who benefits from the current framing of the problem?",
                ],
                priority=4,
            ),
            GuidingQuestion(
                question="Are there historical patterns or cyclical events that offer insights?",
                domain=ResearchDomain.ANCIENT_WISDOM,
                inquiry_type="historical",
                sub_questions=[
                    "Has this problem been solved before in different contexts?",
                    "What can be learned from past failures in this domain?",
                    "Are there recurring cycles that predict future developments?",
                ],
                priority=3,
            ),
            GuidingQuestion(
                question="What ethical considerations must inform this inquiry?",
                domain=ResearchDomain.AI_ETHICS,
                inquiry_type="ethical",
                sub_questions=[
                    "Who could be harmed by this research or its applications?",
                    "What values are embedded in the methodology?",
                    "How do power dynamics affect knowledge production?",
                ],
                priority=5,
            ),
            GuidingQuestion(
                question="What would a completely different intelligence conclude about this?",
                domain=ResearchDomain.INTELLIGENCE_NATURE,
                inquiry_type="perspective",
                sub_questions=[
                    "How would an alien civilization approach this problem?",
                    "What would an AI system without human biases conclude?",
                    "How might future generations view our current understanding?",
                ],
                priority=3,
            ),
        ]

        for question in questions:
            self._guiding_questions[question.question_id] = question

    # -------------------------------------------------------------------------
    # Research Findings Management
    # -------------------------------------------------------------------------

    async def save_research_finding(
        self,
        title: str,
        source_type: SourceType,
        domain: ResearchDomain,
        abstract: str = "",
        key_insights: Optional[List[str]] = None,
        patterns_detected: Optional[List[str]] = None,
        authors: Optional[List[str]] = None,
        relevance_score: float = 0.0,
        tags: Optional[List[str]] = None,
    ) -> ResearchRecord:
        """Save a new research finding to Firebase."""
        record = ResearchRecord(
            title=title,
            source_type=source_type.value,
            domain=domain.value,
            abstract=abstract,
            key_insights=key_insights or [],
            patterns_detected=patterns_detected or [],
            authors=authors or [],
            relevance_score=relevance_score,
            tags=tags or [],
        )

        await self.firebase.set_document(
            ResearchCollections.RESEARCH_FINDINGS,
            record.record_id,
            record.to_dict(),
        )

        logger.info(f"Saved research finding: {title} ({record.record_id})")
        return record

    async def get_research_finding(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a research finding by ID."""
        return await self.firebase.get_document(
            ResearchCollections.RESEARCH_FINDINGS,
            record_id,
        )

    async def search_research(
        self,
        domain: Optional[ResearchDomain] = None,
        source_type: Optional[SourceType] = None,
        min_relevance: float = 0.0,
        tags: Optional[List[str]] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search research findings with filters."""
        filters = []

        if domain:
            filters.append({"field": "domain", "op": "==", "value": domain.value})
        if source_type:
            filters.append({"field": "source_type", "op": "==", "value": source_type.value})
        if min_relevance > 0:
            filters.append({"field": "relevance_score", "op": ">=", "value": min_relevance})

        results = await self.firebase.query_documents(
            ResearchCollections.RESEARCH_FINDINGS,
            filters,
            "-relevance_score",
            limit,
        )

        # Filter by tags if specified
        if tags:
            results = [
                r for r in results
                if any(tag in r.get("tags", []) for tag in tags)
            ]

        return results

    async def get_research_by_domain(
        self,
        domain: ResearchDomain,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get all research in a specific domain."""
        return await self.search_research(domain=domain, limit=limit)

    # -------------------------------------------------------------------------
    # Quantum Concepts
    # -------------------------------------------------------------------------

    def get_quantum_concepts(self) -> List[QuantumConcept]:
        """Get all quantum concepts."""
        return list(self._quantum_concepts.values())

    def get_quantum_concept_by_principle(
        self,
        principle: QuantumPrinciple,
    ) -> Optional[QuantumConcept]:
        """Get quantum concept by principle."""
        for concept in self._quantum_concepts.values():
            if concept.principle == principle:
                return concept
        return None

    async def save_quantum_concept(self, concept: QuantumConcept) -> bool:
        """Save a quantum concept to Firebase."""
        self._quantum_concepts[concept.concept_id] = concept

        success = await self.firebase.set_document(
            ResearchCollections.QUANTUM_CONCEPTS,
            concept.concept_id,
            concept.to_dict(),
        )

        return success

    def apply_quantum_lens(
        self,
        problem: str,
        principle: QuantumPrinciple,
    ) -> Dict[str, Any]:
        """Apply a quantum lens to analyze a problem."""
        concept = self.get_quantum_concept_by_principle(principle)
        if not concept:
            return {"error": f"No concept found for principle: {principle.value}"}

        return {
            "problem": problem,
            "quantum_lens": concept.title,
            "principle": principle.value,
            "application": concept.application,
            "metaphors": concept.metaphors,
            "suggested_approaches": concept.examples,
            "insights": [
                f"Through {principle.value}: {concept.description}",
                f"Consider: {concept.application}",
            ],
        }

    # -------------------------------------------------------------------------
    # Guiding Questions
    # -------------------------------------------------------------------------

    def get_guiding_questions(
        self,
        domain: Optional[ResearchDomain] = None,
        status: Optional[InquiryStatus] = None,
    ) -> List[GuidingQuestion]:
        """Get guiding questions with optional filters."""
        questions = list(self._guiding_questions.values())

        if domain:
            questions = [q for q in questions if q.domain == domain]
        if status:
            questions = [q for q in questions if q.status == status]

        return sorted(questions, key=lambda q: -q.priority)

    async def add_guiding_question(
        self,
        question: str,
        domain: ResearchDomain,
        inquiry_type: str,
        sub_questions: Optional[List[str]] = None,
        priority: int = 3,
    ) -> GuidingQuestion:
        """Add a new guiding question."""
        gq = GuidingQuestion(
            question=question,
            domain=domain,
            inquiry_type=inquiry_type,
            sub_questions=sub_questions or [],
            priority=priority,
        )

        self._guiding_questions[gq.question_id] = gq

        await self.firebase.set_document(
            ResearchCollections.GUIDING_QUESTIONS,
            gq.question_id,
            gq.to_dict(),
        )

        return gq

    async def answer_question(
        self,
        question_id: str,
        insights: List[str],
        related_research: Optional[List[str]] = None,
    ) -> bool:
        """Record insights that answer a guiding question."""
        if question_id not in self._guiding_questions:
            return False

        question = self._guiding_questions[question_id]
        question.insights_generated.extend(insights)
        if related_research:
            question.related_research.extend(related_research)
        question.status = InquiryStatus.RESOLVED
        question.answered_at = datetime.now(timezone.utc)

        await self.firebase.set_document(
            ResearchCollections.GUIDING_QUESTIONS,
            question_id,
            question.to_dict(),
        )

        return True

    # -------------------------------------------------------------------------
    # Research Iterations
    # -------------------------------------------------------------------------

    async def record_iteration(
        self,
        title: str,
        description: str,
        iteration_type: str,
        domain: ResearchDomain,
        key_insights: List[str],
        lessons_learned: Optional[List[str]] = None,
        outcome: str = "partial",
        impact_score: float = 0.5,
    ) -> ResearchIteration:
        """Record a research iteration or key insight."""
        iteration = ResearchIteration(
            title=title,
            description=description,
            iteration_type=iteration_type,
            domain=domain,
            key_insights=key_insights,
            lessons_learned=lessons_learned or [],
            outcome=outcome,
            impact_score=impact_score,
        )

        await self.firebase.set_document(
            ResearchCollections.ITERATIONS,
            iteration.iteration_id,
            iteration.to_dict(),
        )

        logger.info(f"Recorded iteration: {title} ({iteration_type})")
        return iteration

    async def get_iterations(
        self,
        domain: Optional[ResearchDomain] = None,
        iteration_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get research iterations with optional filters."""
        filters = []

        if domain:
            filters.append({"field": "domain", "op": "==", "value": domain.value})
        if iteration_type:
            filters.append({"field": "iteration_type", "op": "==", "value": iteration_type})

        return await self.firebase.query_documents(
            ResearchCollections.ITERATIONS,
            filters,
            "-impact_score",
            limit,
        )

    async def get_breakthroughs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get breakthrough iterations."""
        return await self.get_iterations(iteration_type="breakthrough", limit=limit)

    async def get_failure_lessons(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get lessons from failures."""
        return await self.get_iterations(iteration_type="failure", limit=limit)

    # -------------------------------------------------------------------------
    # Literature References
    # -------------------------------------------------------------------------

    async def add_reference(
        self,
        title: str,
        authors: List[str],
        source_type: SourceType,
        domain: ResearchDomain,
        url: str = "",
        doi: str = "",
        abstract: str = "",
        key_findings: Optional[List[str]] = None,
        relevance_score: float = 0.5,
        tags: Optional[List[str]] = None,
    ) -> LiteratureReference:
        """Add a literature reference."""
        ref = LiteratureReference(
            title=title,
            authors=authors,
            source_type=source_type,
            domain=domain,
            url=url,
            doi=doi,
            abstract=abstract,
            key_findings=key_findings or [],
            relevance_score=relevance_score,
            tags=tags or [],
        )

        await self.firebase.set_document(
            ResearchCollections.LITERATURE,
            ref.reference_id,
            ref.to_dict(),
        )

        logger.info(f"Added reference: {title}")
        return ref

    async def search_literature(
        self,
        domain: Optional[ResearchDomain] = None,
        source_type: Optional[SourceType] = None,
        min_relevance: float = 0.0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search literature references."""
        filters = []

        if domain:
            filters.append({"field": "domain", "op": "==", "value": domain.value})
        if source_type:
            filters.append({"field": "source_type", "op": "==", "value": source_type.value})
        if min_relevance > 0:
            filters.append({"field": "relevance_score", "op": ">=", "value": min_relevance})

        return await self.firebase.query_documents(
            ResearchCollections.LITERATURE,
            filters,
            "-relevance_score",
            limit,
        )

    # -------------------------------------------------------------------------
    # Research Topics (Active 2025)
    # -------------------------------------------------------------------------

    async def create_research_topic(
        self,
        title: str,
        description: str,
        domain: ResearchDomain,
        priority: int = 3,
        year: int = 2025,
        guiding_questions: Optional[List[str]] = None,
    ) -> ResearchTopic:
        """Create a new research topic."""
        topic = ResearchTopic(
            title=title,
            description=description,
            domain=domain,
            priority=priority,
            year=year,
            guiding_questions=guiding_questions or [],
        )

        await self.firebase.set_document(
            ResearchCollections.RESEARCH_TOPICS,
            topic.topic_id,
            topic.to_dict(),
        )

        logger.info(f"Created research topic: {title}")
        return topic

    async def get_active_topics(
        self,
        year: int = 2025,
        domain: Optional[ResearchDomain] = None,
    ) -> List[Dict[str, Any]]:
        """Get active research topics."""
        filters = [
            {"field": "year", "op": "==", "value": year},
            {"field": "status", "op": "!=", "value": InquiryStatus.ARCHIVED.value},
        ]

        if domain:
            filters.append({"field": "domain", "op": "==", "value": domain.value})

        return await self.firebase.query_documents(
            ResearchCollections.RESEARCH_TOPICS,
            filters,
            "-priority",
            100,
        )

    async def update_topic_progress(
        self,
        topic_id: str,
        progress_percent: float,
        insights: Optional[List[str]] = None,
        next_steps: Optional[List[str]] = None,
    ) -> bool:
        """Update progress on a research topic."""
        update_data = {
            "progress_percent": progress_percent,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if insights:
            topic = await self.firebase.get_document(
                ResearchCollections.RESEARCH_TOPICS,
                topic_id,
            )
            if topic:
                existing_insights = topic.get("insights", [])
                update_data["insights"] = existing_insights + insights

        if next_steps:
            update_data["next_steps"] = next_steps

        return await self.firebase.update_document(
            ResearchCollections.RESEARCH_TOPICS,
            topic_id,
            update_data,
        )

    # -------------------------------------------------------------------------
    # Knowledge Graph
    # -------------------------------------------------------------------------

    async def add_knowledge_node(
        self,
        title: str,
        description: str,
        node_type: str,
        domain: ResearchDomain,
        connections: Optional[List[str]] = None,
        quantum_principles: Optional[List[QuantumPrinciple]] = None,
        confidence: float = 0.5,
        evidence: Optional[List[str]] = None,
    ) -> KnowledgeNode:
        """Add a node to the knowledge graph."""
        node = KnowledgeNode(
            title=title,
            description=description,
            node_type=node_type,
            domain=domain,
            connections=connections or [],
            quantum_principles=quantum_principles or [],
            confidence=confidence,
            evidence=evidence or [],
        )

        await self.firebase.set_document(
            ResearchCollections.KNOWLEDGE_GRAPH,
            node.node_id,
            node.to_dict(),
        )

        return node

    async def connect_nodes(
        self,
        node_id_1: str,
        node_id_2: str,
    ) -> bool:
        """Connect two knowledge nodes (bidirectional)."""
        # Update node 1
        node1 = await self.firebase.get_document(
            ResearchCollections.KNOWLEDGE_GRAPH,
            node_id_1,
        )
        if node1:
            connections = node1.get("connections", [])
            if node_id_2 not in connections:
                connections.append(node_id_2)
                await self.firebase.update_document(
                    ResearchCollections.KNOWLEDGE_GRAPH,
                    node_id_1,
                    {"connections": connections},
                )

        # Update node 2
        node2 = await self.firebase.get_document(
            ResearchCollections.KNOWLEDGE_GRAPH,
            node_id_2,
        )
        if node2:
            connections = node2.get("connections", [])
            if node_id_1 not in connections:
                connections.append(node_id_1)
                await self.firebase.update_document(
                    ResearchCollections.KNOWLEDGE_GRAPH,
                    node_id_2,
                    {"connections": connections},
                )

        return True

    async def get_connected_knowledge(
        self,
        node_id: str,
        depth: int = 1,
    ) -> List[Dict[str, Any]]:
        """Get connected knowledge nodes up to specified depth."""
        visited = set()
        results = []

        async def traverse(nid: str, current_depth: int):
            if current_depth > depth or nid in visited:
                return
            visited.add(nid)

            node = await self.firebase.get_document(
                ResearchCollections.KNOWLEDGE_GRAPH,
                nid,
            )
            if node:
                results.append(node)
                for conn_id in node.get("connections", []):
                    await traverse(conn_id, current_depth + 1)

        await traverse(node_id, 0)
        return results

    # -------------------------------------------------------------------------
    # Hub Summary
    # -------------------------------------------------------------------------

    async def get_hub_summary(self) -> Dict[str, Any]:
        """Get a summary of the Research Hub contents."""
        research = await self.firebase.query_documents(
            ResearchCollections.RESEARCH_FINDINGS, [], limit=1000
        )
        iterations = await self.firebase.query_documents(
            ResearchCollections.ITERATIONS, [], limit=1000
        )
        literature = await self.firebase.query_documents(
            ResearchCollections.LITERATURE, [], limit=1000
        )
        topics = await self.get_active_topics()
        nodes = await self.firebase.query_documents(
            ResearchCollections.KNOWLEDGE_GRAPH, [], limit=1000
        )

        return {
            "muladhara_status": "active",
            "research_findings_count": len(research),
            "quantum_concepts_count": len(self._quantum_concepts),
            "guiding_questions_count": len(self._guiding_questions),
            "iterations_count": len(iterations),
            "literature_count": len(literature),
            "active_topics_count": len(topics),
            "knowledge_nodes_count": len(nodes),
            "domains_covered": list(ResearchDomain.__members__.keys()),
            "quantum_principles": list(QuantumPrinciple.__members__.keys()),
        }


# =============================================================================
# FACTORY & SINGLETON
# =============================================================================

_research_hub_instance: Optional[ResearchInquiryHub] = None


def get_research_hub() -> ResearchInquiryHub:
    """Get the global Research Hub instance."""
    global _research_hub_instance
    if _research_hub_instance is None:
        _research_hub_instance = ResearchInquiryHub()
    return _research_hub_instance


def create_research_hub(
    firebase_client: Optional[FirebaseClient] = None,
) -> ResearchInquiryHub:
    """Create a new Research Hub instance."""
    return ResearchInquiryHub(firebase_client)
