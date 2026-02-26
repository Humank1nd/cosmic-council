"""
Synthesis Engine for Agent Orchestrator
Finds common threads across all perspectives, detects contradictions, and generates novel connections.

This implements the core innovation: "Approach a problem from multiple angles SIMULTANEOUSLY 
and interpolate the data finding COMMON THREADS amongst the iterations in order to create 
new ARTIFICIAL SYNAPSES and find uncharted AI NEUROPATHWAYS."
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import json
import hashlib

from ..integrations.llm_provider import BaseLLMProvider, LLMRequest, LLMMessage
from .models import (
    ResearchCoreProblem, ResearchFinding, ResearchPrioritizedQuestion,
    PlanningRelatedQuestion, PlanningActionPlan, PlanningDependency,
    DevelopmentPrototype, DevelopmentInternalTesting, DevelopmentCreativeNote,
    BudgetResourceInventory, BudgetAllocation, BudgetTimeCostAnalysis,
    MarketInsight, MarketCommunicationStrategy, MarketPerformanceMetric,
    SupportUserFeedback, SupportPerformanceAssessment, SupportContinuousImprovement
)

logger = logging.getLogger(__name__)


class SynthesisLevel(Enum):
    """Level of synthesis depth"""
    SURFACE = "surface"           # Basic pattern matching
    DEEP = "deep"                 # Semantic analysis
    QUANTUM = "quantum"           # Quantum-inspired superposition analysis
    TRANSCENDENT = "transcendent" # Novel connection generation


@dataclass
class PerspectiveOutput:
    """Output from a single perspective (totem)"""
    totem: str                    # "red_owl", "orange_orangutan", etc.
    cycle_number: int
    agent_outputs: Dict[str, Any]  # Outputs from all 6 agents in this totem
    key_insights: List[str]
    recommendations: List[str]
    questions_raised: List[str]
    confidence: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CommonThread:
    """A common thread found across multiple perspectives"""
    thread_id: str
    description: str
    supporting_perspectives: List[str]  # Which totems support this thread
    strength: float                      # 0.0-1.0, how strong the connection is
    evidence: List[str]                  # Supporting evidence from outputs
    relevance_score: float               # How relevant to the core problem
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Contradiction:
    """A contradiction detected between perspectives"""
    contradiction_id: str
    description: str
    conflicting_perspectives: List[str]  # Which totems contradict
    conflict_type: str                   # "logical", "resource", "timeline", "philosophical"
    severity: float                      # 0.0-1.0
    resolution_suggestions: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class NovelConnection:
    """A novel connection (artificial synapse) discovered"""
    connection_id: str
    description: str
    connecting_perspectives: List[str]   # Which perspectives connect
    novelty_score: float                 # How novel this connection is
    potential_impact: float              # Potential impact if explored
    exploration_path: str                # Suggested path for exploration
    neuropathway: str                    # The uncharted AI neuropathway identified
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SynthesisResult:
    """Complete synthesis result"""
    synthesis_id: str
    cycle_number: int
    problem_ref: Optional[str]
    
    # Input perspectives
    perspective_outputs: Dict[str, PerspectiveOutput]  # Keyed by totem
    
    # Synthesis findings
    common_threads: List[CommonThread]
    contradictions: List[Contradiction]
    novel_connections: List[NovelConnection]
    
    # Meta-analysis
    synthesis_level: SynthesisLevel
    overall_coherence: float            # How coherent the perspectives are
    synthesis_confidence: float         # Confidence in synthesis quality
    
    # Recommendations
    recommended_actions: List[str]
    next_questions: List[str]            # Questions for next cycle (Ouroboros)
    evolution_suggestions: List[str]      # Suggestions for system evolution
    
    # Metadata
    processing_time: float
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SynthesisEngine:
    """
    Synthesis Engine that finds common threads, detects contradictions,
    and generates novel connections across all perspectives.
    """
    
    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        synthesis_level: SynthesisLevel = SynthesisLevel.DEEP,
        min_thread_strength: float = 0.6,
        min_novelty_score: float = 0.7
    ):
        """
        Initialize the synthesis engine
        
        Args:
            llm_provider: LLM provider for semantic analysis
            synthesis_level: Depth of synthesis analysis
            min_thread_strength: Minimum strength for common threads
            min_novelty_score: Minimum novelty score for novel connections
        """
        self.llm_provider = llm_provider
        self.synthesis_level = synthesis_level
        self.min_thread_strength = min_thread_strength
        self.min_novelty_score = min_novelty_score
        self.logger = logging.getLogger(__name__)
    
    async def synthesize(
        self,
        perspective_outputs: Dict[str, PerspectiveOutput],
        cycle_number: int,
        problem_ref: Optional[str] = None
    ) -> SynthesisResult:
        """
        Synthesize outputs from all perspectives
        
        Args:
            perspective_outputs: Dictionary of perspective outputs keyed by totem
            cycle_number: Current cycle number
            problem_ref: Reference to the problem being solved
            
        Returns:
            Complete synthesis result
        """
        start_time = datetime.now(timezone.utc)
        synthesis_id = f"synthesis_{cycle_number}_{int(start_time.timestamp())}"
        
        self.logger.info(f"🔄 Starting synthesis for cycle {cycle_number} with {len(perspective_outputs)} perspectives")
        
        # Step 1: Extract key information from all perspectives
        all_insights = []
        all_recommendations = []
        all_questions = []
        
        for totem, output in perspective_outputs.items():
            all_insights.extend(output.key_insights)
            all_recommendations.extend(output.recommendations)
            all_questions.extend(output.questions_raised)
        
        # Step 2: Find common threads
        common_threads = await self._find_common_threads(
            perspective_outputs, all_insights, all_recommendations
        )
        
        # Step 3: Detect contradictions
        contradictions = await self._detect_contradictions(perspective_outputs)
        
        # Step 4: Generate novel connections (artificial synapses)
        novel_connections = await self._generate_novel_connections(
            perspective_outputs, common_threads
        )
        
        # Step 5: Calculate overall coherence
        overall_coherence = self._calculate_coherence(
            common_threads, contradictions, perspective_outputs
        )
        
        # Step 6: Generate recommendations and next questions
        recommended_actions = await self._generate_recommendations(
            common_threads, contradictions, novel_connections
        )
        
        next_questions = await self._generate_next_questions(
            common_threads, contradictions, novel_connections, all_questions
        )
        
        evolution_suggestions = await self._generate_evolution_suggestions(
            novel_connections, common_threads
        )
        
        # Step 7: Calculate synthesis confidence
        synthesis_confidence = self._calculate_synthesis_confidence(
            common_threads, contradictions, novel_connections, overall_coherence
        )
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        result = SynthesisResult(
            synthesis_id=synthesis_id,
            cycle_number=cycle_number,
            problem_ref=problem_ref,
            perspective_outputs=perspective_outputs,
            common_threads=common_threads,
            contradictions=contradictions,
            novel_connections=novel_connections,
            synthesis_level=self.synthesis_level,
            overall_coherence=overall_coherence,
            synthesis_confidence=synthesis_confidence,
            recommended_actions=recommended_actions,
            next_questions=next_questions,
            evolution_suggestions=evolution_suggestions,
            processing_time=processing_time
        )
        
        self.logger.info(
            f"✅ Synthesis complete: {len(common_threads)} threads, "
            f"{len(contradictions)} contradictions, {len(novel_connections)} novel connections "
            f"(coherence: {overall_coherence:.2f}, confidence: {synthesis_confidence:.2f})"
        )
        
        return result
    
    async def _find_common_threads(
        self,
        perspective_outputs: Dict[str, PerspectiveOutput],
        all_insights: List[str],
        all_recommendations: List[str]
    ) -> List[CommonThread]:
        """Find common threads across perspectives"""
        threads = []
        
        if not self.llm_provider:
            # Fallback: Simple keyword-based matching
            return self._find_common_threads_keyword_based(
                perspective_outputs, all_insights, all_recommendations
            )
        
        # Use LLM for semantic analysis
        prompt = f"""
        Analyze the following insights and recommendations from 6 different perspectives 
        (Research, Planning, Development, Budget, Market, Support) and identify common threads.
        
        Insights from all perspectives:
        {json.dumps(all_insights, indent=2)}
        
        Recommendations from all perspectives:
        {json.dumps(all_recommendations, indent=2)}
        
        For each common thread, provide:
        1. A clear description of the thread
        2. Which perspectives support it
        3. Evidence from the outputs
        4. Relevance to the core problem
        
        Return as JSON array with structure:
        [
            {{
                "description": "thread description",
                "supporting_perspectives": ["red_owl", "orange_orangutan"],
                "evidence": ["evidence 1", "evidence 2"],
                "relevance": 0.85
            }}
        ]
        """
        
        try:
            request = LLMRequest(
                messages=[
                    LLMMessage(role="system", content="You are a synthesis expert that finds patterns across multiple perspectives."),
                    LLMMessage(role="user", content=prompt)
                ],
                temperature=0.5
            )
            
            response = await self.llm_provider.generate(request)
            
            # Parse JSON response
            threads_data = json.loads(response.content)
            
            for i, thread_data in enumerate(threads_data):
                thread_id = f"thread_{hashlib.md5(thread_data['description'].encode()).hexdigest()[:8]}"
                
                # Calculate strength based on number of supporting perspectives
                num_supporters = len(thread_data.get('supporting_perspectives', []))
                strength = min(1.0, num_supporters / 6.0 + 0.3)  # At least 0.3, up to 1.0
                
                thread = CommonThread(
                    thread_id=thread_id,
                    description=thread_data['description'],
                    supporting_perspectives=thread_data.get('supporting_perspectives', []),
                    strength=strength,
                    evidence=thread_data.get('evidence', []),
                    relevance_score=thread_data.get('relevance', 0.5)
                )
                
                if thread.strength >= self.min_thread_strength:
                    threads.append(thread)
        
        except Exception as e:
            self.logger.error(f"Error finding common threads with LLM: {e}")
            # Fallback to keyword-based
            threads = self._find_common_threads_keyword_based(
                perspective_outputs, all_insights, all_recommendations
            )
        
        return sorted(threads, key=lambda t: t.strength * t.relevance_score, reverse=True)
    
    def _find_common_threads_keyword_based(
        self,
        perspective_outputs: Dict[str, PerspectiveOutput],
        all_insights: List[str],
        all_recommendations: List[str]
    ) -> List[CommonThread]:
        """Fallback keyword-based common thread detection"""
        # Simple implementation: find words that appear in multiple perspectives
        word_counts: Dict[str, List[str]] = {}
        
        all_text = " ".join(all_insights + all_recommendations).lower()
        words = all_text.split()
        
        for word in set(words):
            if len(word) > 4:  # Only meaningful words
                perspectives_with_word = []
                for totem, output in perspective_outputs.items():
                    totem_text = " ".join(output.key_insights + output.recommendations).lower()
                    if word in totem_text:
                        perspectives_with_word.append(totem)
                
                if len(perspectives_with_word) >= 2:
                    word_counts[word] = perspectives_with_word
        
        threads = []
        for word, perspectives in word_counts.items():
            thread_id = f"thread_{hashlib.md5(word.encode()).hexdigest()[:8]}"
            strength = len(perspectives) / 6.0
            
            thread = CommonThread(
                thread_id=thread_id,
                description=f"Common theme: {word}",
                supporting_perspectives=perspectives,
                strength=strength,
                evidence=[f"Found in {len(perspectives)} perspectives"],
                relevance_score=0.6
            )
            
            if thread.strength >= self.min_thread_strength:
                threads.append(thread)
        
        return threads
    
    async def _detect_contradictions(
        self,
        perspective_outputs: Dict[str, PerspectiveOutput]
    ) -> List[Contradiction]:
        """Detect contradictions between perspectives"""
        contradictions = []
        
        if not self.llm_provider:
            return contradictions  # Skip if no LLM
        
        # Compare each pair of perspectives
        totems = list(perspective_outputs.keys())
        
        for i, totem1 in enumerate(totems):
            for totem2 in totems[i+1:]:
                output1 = perspective_outputs[totem1]
                output2 = perspective_outputs[totem2]
                
                prompt = f"""
                Compare these two perspectives and identify any contradictions:
                
                {totem1} perspective:
                Insights: {json.dumps(output1.key_insights, indent=2)}
                Recommendations: {json.dumps(output1.recommendations, indent=2)}
                
                {totem2} perspective:
                Insights: {json.dumps(output2.key_insights, indent=2)}
                Recommendations: {json.dumps(output2.recommendations, indent=2)}
                
                Identify contradictions (logical conflicts, resource conflicts, timeline conflicts, 
                or philosophical differences). Return as JSON:
                {{
                    "has_contradiction": true/false,
                    "description": "description of contradiction",
                    "conflict_type": "logical|resource|timeline|philosophical",
                    "severity": 0.0-1.0,
                    "resolution_suggestions": ["suggestion1", "suggestion2"]
                }}
                """
                
                try:
                    request = LLMRequest(
                        messages=[
                            LLMMessage(role="system", content="You are an expert at detecting logical contradictions."),
                            LLMMessage(role="user", content=prompt)
                        ],
                        temperature=0.3
                    )
                    
                    response = await self.llm_provider.generate(request)
                    contradiction_data = json.loads(response.content)
                    
                    if contradiction_data.get('has_contradiction', False):
                        contradiction_id = f"contradiction_{hashlib.md5(contradiction_data['description'].encode()).hexdigest()[:8]}"
                        
                        contradiction = Contradiction(
                            contradiction_id=contradiction_id,
                            description=contradiction_data['description'],
                            conflicting_perspectives=[totem1, totem2],
                            conflict_type=contradiction_data.get('conflict_type', 'logical'),
                            severity=contradiction_data.get('severity', 0.5),
                            resolution_suggestions=contradiction_data.get('resolution_suggestions', [])
                        )
                        
                        contradictions.append(contradiction)
                
                except Exception as e:
                    self.logger.warning(f"Error detecting contradiction between {totem1} and {totem2}: {e}")
                    continue
        
        return sorted(contradictions, key=lambda c: c.severity, reverse=True)
    
    async def _generate_novel_connections(
        self,
        perspective_outputs: Dict[str, PerspectiveOutput],
        common_threads: List[CommonThread]
    ) -> List[NovelConnection]:
        """Generate novel connections (artificial synapses)"""
        connections = []
        
        if not self.llm_provider:
            return connections
        
        prompt = f"""
        Analyze these perspective outputs and identify NOVEL CONNECTIONS that create 
        "artificial synapses" - unexpected links between perspectives that reveal 
        uncharted AI neuropathways.
        
        Perspective outputs:
        {json.dumps({k: {"insights": v.key_insights, "recommendations": v.recommendations} 
                     for k, v in perspective_outputs.items()}, indent=2)}
        
        Common threads already identified:
        {json.dumps([t.description for t in common_threads], indent=2)}
        
        Find connections that are:
        1. Novel (not obvious)
        2. Potentially transformative
        3. Create new pathways for exploration
        
        Return as JSON array:
        [
            {{
                "description": "novel connection description",
                "connecting_perspectives": ["red_owl", "yellow_honeybee"],
                "novelty_score": 0.0-1.0,
                "potential_impact": 0.0-1.0,
                "exploration_path": "suggested path",
                "neuropathway": "description of the uncharted pathway"
            }}
        ]
        """
        
        try:
            request = LLMRequest(
                messages=[
                    LLMMessage(role="system", content="You are a creative synthesis expert that finds novel connections."),
                    LLMMessage(role="user", content=prompt)
                ],
                temperature=0.9  # High temperature for creativity
            )
            
            response = await self.llm_provider.generate(request)
            connections_data = json.loads(response.content)
            
            for conn_data in connections_data:
                if conn_data.get('novelty_score', 0) >= self.min_novelty_score:
                    connection_id = f"connection_{hashlib.md5(conn_data['description'].encode()).hexdigest()[:8]}"
                    
                    connection = NovelConnection(
                        connection_id=connection_id,
                        description=conn_data['description'],
                        connecting_perspectives=conn_data.get('connecting_perspectives', []),
                        novelty_score=conn_data.get('novelty_score', 0.5),
                        potential_impact=conn_data.get('potential_impact', 0.5),
                        exploration_path=conn_data.get('exploration_path', ''),
                        neuropathway=conn_data.get('neuropathway', '')
                    )
                    
                    connections.append(connection)
        
        except Exception as e:
            self.logger.error(f"Error generating novel connections: {e}")
        
        return sorted(connections, key=lambda c: c.novelty_score * c.potential_impact, reverse=True)
    
    def _calculate_coherence(
        self,
        common_threads: List[CommonThread],
        contradictions: List[Contradiction],
        perspective_outputs: Dict[str, PerspectiveOutput]
    ) -> float:
        """Calculate overall coherence score"""
        # Base coherence from common threads
        thread_coherence = sum(t.strength * t.relevance_score for t in common_threads) / max(len(common_threads), 1)
        
        # Penalty for contradictions
        contradiction_penalty = sum(c.severity for c in contradictions) / max(len(contradictions), 1) * 0.3
        
        # Perspective alignment (how well perspectives align)
        avg_confidence = sum(p.confidence for p in perspective_outputs.values()) / len(perspective_outputs)
        
        coherence = (thread_coherence * 0.5 + avg_confidence * 0.3) - contradiction_penalty
        return max(0.0, min(1.0, coherence))
    
    async def _generate_recommendations(
        self,
        common_threads: List[CommonThread],
        contradictions: List[Contradiction],
        novel_connections: List[NovelConnection]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Recommendations from common threads
        for thread in common_threads[:3]:  # Top 3 threads
            recommendations.append(f"Focus on: {thread.description} (supported by {len(thread.supporting_perspectives)} perspectives)")
        
        # Recommendations for resolving contradictions
        for contradiction in contradictions[:2]:  # Top 2 contradictions
            if contradiction.resolution_suggestions:
                recommendations.append(f"Resolve contradiction: {contradiction.resolution_suggestions[0]}")
        
        # Recommendations from novel connections
        for connection in novel_connections[:2]:  # Top 2 connections
            recommendations.append(f"Explore novel pathway: {connection.exploration_path}")
        
        return recommendations
    
    async def _generate_next_questions(
        self,
        common_threads: List[CommonThread],
        contradictions: List[Contradiction],
        novel_connections: List[NovelConnection],
        existing_questions: List[str]
    ) -> List[str]:
        """Generate questions for next cycle (Ouroboros)"""
        questions = []
        
        # Questions from contradictions
        for contradiction in contradictions:
            questions.append(f"How can we resolve the contradiction: {contradiction.description}?")
        
        # Questions from novel connections
        for connection in novel_connections:
            questions.append(f"What happens if we explore: {connection.neuropathway}?")
        
        # Questions from common threads that need deeper exploration
        for thread in common_threads:
            if thread.strength < 0.8:  # Threads that could be stronger
                questions.append(f"How can we strengthen the thread: {thread.description}?")
        
        # Add some existing questions if they're still relevant
        questions.extend(existing_questions[:2])
        
        return questions[:5]  # Top 5 questions
    
    async def _generate_evolution_suggestions(
        self,
        novel_connections: List[NovelConnection],
        common_threads: List[CommonThread]
    ) -> List[str]:
        """Generate suggestions for system evolution"""
        suggestions = []
        
        if novel_connections:
            suggestions.append(f"Explore {len(novel_connections)} novel neuropathways identified")
        
        if len(common_threads) > 5:
            suggestions.append("Strong pattern alignment detected - consider optimizing for these patterns")
        
        if not novel_connections:
            suggestions.append("No novel connections found - consider more divergent thinking")
        
        return suggestions
    
    def _calculate_synthesis_confidence(
        self,
        common_threads: List[CommonThread],
        contradictions: List[Contradiction],
        novel_connections: List[NovelConnection],
        coherence: float
    ) -> float:
        """Calculate confidence in synthesis quality"""
        # Base confidence from coherence
        confidence = coherence
        
        # Boost from strong common threads
        if common_threads:
            avg_thread_strength = sum(t.strength for t in common_threads) / len(common_threads)
            confidence += avg_thread_strength * 0.2
        
        # Boost from novel connections
        if novel_connections:
            confidence += 0.1
        
        # Penalty for severe contradictions
        if contradictions:
            max_severity = max(c.severity for c in contradictions)
            confidence -= max_severity * 0.2
        
        return max(0.0, min(1.0, confidence))

