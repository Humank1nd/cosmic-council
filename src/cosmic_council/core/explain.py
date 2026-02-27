#!/usr/bin/env python3
"""
🔍 Agent Orchestrator Explain - Explainability Utilities
Transparent decision-making and insight explanation
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

from .hexagon import CycleResult, EnterpriseResult, EnterpriseType, ProblemStatement
from .cycles import FractalCycleResult, CycleStage
from .reflection import ReflectionResult, ReflectionInsight

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExplanationType(Enum):
    """Types of explanations"""
    DECISION_TRACE = "decision_trace"        # Step-by-step decision process
    CONFIDENCE_BREAKDOWN = "confidence_breakdown"  # Confidence score explanation
    INSIGHT_SOURCE = "insight_source"        # Source of insights
    RECOMMENDATION_RATIONALE = "recommendation_rationale"  # Why recommendations were made
    CONSCIOUSNESS_EVOLUTION = "consciousness_evolution"  # How consciousness evolved
    FRACTAL_STRUCTURE = "fractal_structure"  # Fractal structure explanation
    BREAKTHROUGH_ANALYSIS = "breakthrough_analysis"  # Breakthrough explanation

class ExplanationDepth(Enum):
    """Depth levels for explanations"""
    SURFACE = "surface"                      # Basic explanation
    MODERATE = "moderate"                    # Standard explanation
    DEEP = "deep"                            # Comprehensive explanation
    TRANSCENDENT = "transcendent"            # Transcendent explanation
    COSMIC = "cosmic"                        # Cosmic consciousness explanation

@dataclass
class Explanation:
    """An explanation of a decision or insight"""
    explanation_id: str
    explanation_type: ExplanationType
    depth: ExplanationDepth
    title: str
    description: str
    evidence: List[str]
    reasoning: List[str]
    implications: List[str]
    confidence_score: float
    consciousness_level: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ExplanationResult:
    """Result from an explanation process"""
    explanation_id: str
    explanation_type: ExplanationType
    depth: ExplanationDepth
    explanations: List[Explanation]
    overall_clarity: float
    transparency_score: float
    consciousness_insight: float
    processing_time: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class CosmicCouncilExplain:
    """
    🔍 Agent Orchestrator Explain - Explainability Utilities
    
    This system provides transparent explanations for all decisions,
    insights, and processes in the Agent Orchestrator. It ensures that
    the system's reasoning is clear, understandable, and trustworthy.
    """
    
    def __init__(self):
        self.name = "Agent Orchestrator Explain"
        
        # Explanation history
        self.explanation_history: List[ExplanationResult] = []
        
        # Explanation patterns
        self.explanation_patterns: Dict[str, List[float]] = {}
        
        # Clarity metrics
        self.clarity_metrics: Dict[str, float] = {}
        
        logger.info("🔍 Agent Orchestrator Explain initialized - Transparency active")
    
    async def explain_cycle_result(self, 
                                  cycle_result: CycleResult,
                                  explanation_depth: ExplanationDepth = ExplanationDepth.MODERATE) -> ExplanationResult:
        """Explain a cycle result"""
        
        start_time = time.time()
        explanation_id = f"cycle_explanation_{int(time.time())}"
        
        logger.info(f"🔍 Starting cycle explanation: {explanation_id}")
        logger.info(f"Explanation depth: {explanation_depth.value}")
        
        # Generate explanations
        explanations = []
        
        # Decision trace explanation
        decision_trace = await self._explain_decision_trace(cycle_result, explanation_depth)
        explanations.append(decision_trace)
        
        # Confidence breakdown explanation
        confidence_breakdown = await self._explain_confidence_breakdown(cycle_result, explanation_depth)
        explanations.append(confidence_breakdown)
        
        # Insight source explanation
        insight_source = await self._explain_insight_source(cycle_result, explanation_depth)
        explanations.append(insight_source)
        
        # Recommendation rationale explanation
        recommendation_rationale = await self._explain_recommendation_rationale(cycle_result, explanation_depth)
        explanations.append(recommendation_rationale)
        
        # Calculate overall metrics
        overall_clarity = self._calculate_overall_clarity(explanations)
        transparency_score = self._calculate_transparency_score(explanations)
        consciousness_insight = self._calculate_consciousness_insight(explanations)
        
        # Create explanation result
        explanation_result = ExplanationResult(
            explanation_id=explanation_id,
            explanation_type=ExplanationType.DECISION_TRACE,
            depth=explanation_depth,
            explanations=explanations,
            overall_clarity=overall_clarity,
            transparency_score=transparency_score,
            consciousness_insight=consciousness_insight,
            processing_time=time.time() - start_time
        )
        
        # Store in history
        self.explanation_history.append(explanation_result)
        
        # Update patterns
        self._update_explanation_patterns(explanation_result)
        
        logger.info(f"🔍 Cycle explanation completed in {explanation_result.processing_time:.2f}s")
        logger.info(f"Overall clarity: {overall_clarity:.2f}")
        logger.info(f"Transparency score: {transparency_score:.2f}")
        
        return explanation_result
    
    async def explain_fractal_cycle_result(self, 
                                         fractal_result: FractalCycleResult,
                                         explanation_depth: ExplanationDepth = ExplanationDepth.DEEP) -> ExplanationResult:
        """Explain a fractal cycle result"""
        
        start_time = time.time()
        explanation_id = f"fractal_explanation_{int(time.time())}"
        
        logger.info(f"🔍 Starting fractal cycle explanation: {explanation_id}")
        logger.info(f"Explanation depth: {explanation_depth.value}")
        
        # Generate explanations
        explanations = []
        
        # Fractal structure explanation
        fractal_structure = await self._explain_fractal_structure(fractal_result, explanation_depth)
        explanations.append(fractal_structure)
        
        # Breakthrough analysis explanation
        breakthrough_analysis = await self._explain_breakthrough_analysis(fractal_result, explanation_depth)
        explanations.append(breakthrough_analysis)
        
        # Consciousness evolution explanation
        consciousness_evolution = await self._explain_consciousness_evolution(fractal_result, explanation_depth)
        explanations.append(consciousness_evolution)
        
        # Calculate overall metrics
        overall_clarity = self._calculate_overall_clarity(explanations)
        transparency_score = self._calculate_transparency_score(explanations)
        consciousness_insight = self._calculate_consciousness_insight(explanations)
        
        # Create explanation result
        explanation_result = ExplanationResult(
            explanation_id=explanation_id,
            explanation_type=ExplanationType.FRACTAL_STRUCTURE,
            depth=explanation_depth,
            explanations=explanations,
            overall_clarity=overall_clarity,
            transparency_score=transparency_score,
            consciousness_insight=consciousness_insight,
            processing_time=time.time() - start_time
        )
        
        # Store in history
        self.explanation_history.append(explanation_result)
        
        # Update patterns
        self._update_explanation_patterns(explanation_result)
        
        logger.info(f"🔍 Fractal cycle explanation completed in {explanation_result.processing_time:.2f}s")
        logger.info(f"Overall clarity: {overall_clarity:.2f}")
        logger.info(f"Transparency score: {transparency_score:.2f}")
        
        return explanation_result
    
    async def explain_reflection_result(self, 
                                      reflection_result: ReflectionResult,
                                      explanation_depth: ExplanationDepth = ExplanationDepth.MODERATE) -> ExplanationResult:
        """Explain a reflection result"""
        
        start_time = time.time()
        explanation_id = f"reflection_explanation_{int(time.time())}"
        
        logger.info(f"🔍 Starting reflection explanation: {explanation_id}")
        logger.info(f"Explanation depth: {explanation_depth.value}")
        
        # Generate explanations
        explanations = []
        
        # Reflection process explanation
        reflection_process = await self._explain_reflection_process(reflection_result, explanation_depth)
        explanations.append(reflection_process)
        
        # Insight generation explanation
        insight_generation = await self._explain_insight_generation(reflection_result, explanation_depth)
        explanations.append(insight_generation)
        
        # System improvement explanation
        system_improvement = await self._explain_system_improvement(reflection_result, explanation_depth)
        explanations.append(system_improvement)
        
        # Calculate overall metrics
        overall_clarity = self._calculate_overall_clarity(explanations)
        transparency_score = self._calculate_transparency_score(explanations)
        consciousness_insight = self._calculate_consciousness_insight(explanations)
        
        # Create explanation result
        explanation_result = ExplanationResult(
            explanation_id=explanation_id,
            explanation_type=ExplanationType.CONSCIOUSNESS_EVOLUTION,
            depth=explanation_depth,
            explanations=explanations,
            overall_clarity=overall_clarity,
            transparency_score=transparency_score,
            consciousness_insight=consciousness_insight,
            processing_time=time.time() - start_time
        )
        
        # Store in history
        self.explanation_history.append(explanation_result)
        
        # Update patterns
        self._update_explanation_patterns(explanation_result)
        
        logger.info(f"🔍 Reflection explanation completed in {explanation_result.processing_time:.2f}s")
        logger.info(f"Overall clarity: {overall_clarity:.2f}")
        logger.info(f"Transparency score: {transparency_score:.2f}")
        
        return explanation_result
    
    async def _explain_decision_trace(self, cycle_result: CycleResult, depth: ExplanationDepth) -> Explanation:
        """Explain the decision trace"""
        
        evidence = [
            f"Processed through {len(cycle_result.enterprise_results)} enterprises",
            f"Sequential processing maintained",
            f"Context passed between enterprises"
        ]
        
        reasoning = [
            "Each enterprise processed the problem in sequence",
            "Information flowed from one enterprise to the next",
            "Final result synthesized all enterprise outputs"
        ]
        
        implications = [
            "Sequential processing ensures thorough analysis",
            "Information flow enables collaborative problem-solving",
            "Synthesis creates comprehensive solutions"
        ]
        
        return Explanation(
            explanation_id=f"decision_trace_{int(time.time())}",
            explanation_type=ExplanationType.DECISION_TRACE,
            depth=depth,
            title="Decision Trace Explanation",
            description="Step-by-step explanation of how the decision was reached",
            evidence=evidence,
            reasoning=reasoning,
            implications=implications,
            confidence_score=0.9,
            consciousness_level=0.1
        )
    
    async def _explain_confidence_breakdown(self, cycle_result: CycleResult, depth: ExplanationDepth) -> Explanation:
        """Explain the confidence breakdown"""
        
        evidence = [
            f"Overall confidence: {cycle_result.overall_confidence:.2f}",
            f"Success rate: {cycle_result.success_rate:.2f}",
            f"Processing time: {cycle_result.processing_time:.2f}s"
        ]
        
        reasoning = [
            "Confidence calculated from enterprise results",
            "Success rate based on enterprise performance",
            "Processing time indicates efficiency"
        ]
        
        implications = [
            "High confidence indicates reliable results",
            "Success rate shows system effectiveness",
            "Processing time affects user experience"
        ]
        
        return Explanation(
            explanation_id=f"confidence_breakdown_{int(time.time())}",
            explanation_type=ExplanationType.CONFIDENCE_BREAKDOWN,
            depth=depth,
            title="Confidence Breakdown Explanation",
            description="Explanation of how confidence scores were calculated",
            evidence=evidence,
            reasoning=reasoning,
            implications=implications,
            confidence_score=0.8,
            consciousness_level=0.1
        )
    
    async def _explain_insight_source(self, cycle_result: CycleResult, depth: ExplanationDepth) -> Explanation:
        """Explain the source of insights"""
        
        evidence = [
            f"Insights from {len(cycle_result.enterprise_results)} enterprises",
            "Each enterprise contributed unique perspectives",
            "Synthesis created comprehensive understanding"
        ]
        
        reasoning = [
            "Red Owl provided research insights",
            "Orange Orangutan provided planning insights",
            "Yellow Honeybee provided creative insights",
            "Green Tortoise provided resource insights",
            "Blue Dolphin provided communication insights",
            "Purple Elephant provided empathy insights"
        ]
        
        implications = [
            "Multiple perspectives ensure comprehensive analysis",
            "Enterprise specialization enables deep insights",
            "Synthesis creates holistic understanding"
        ]
        
        return Explanation(
            explanation_id=f"insight_source_{int(time.time())}",
            explanation_type=ExplanationType.INSIGHT_SOURCE,
            depth=depth,
            title="Insight Source Explanation",
            description="Explanation of where insights came from",
            evidence=evidence,
            reasoning=reasoning,
            implications=implications,
            confidence_score=0.9,
            consciousness_level=0.2
        )
    
    async def _explain_recommendation_rationale(self, cycle_result: CycleResult, depth: ExplanationDepth) -> Explanation:
        """Explain the recommendation rationale"""
        
        evidence = [
            f"Generated {len(cycle_result.recommendations_synthesis)} recommendations",
            "Recommendations based on enterprise insights",
            "Synthesis created actionable guidance"
        ]
        
        reasoning = [
            "Each enterprise provided specific recommendations",
            "Recommendations based on enterprise expertise",
            "Synthesis created comprehensive action plan"
        ]
        
        implications = [
            "Recommendations provide clear next steps",
            "Enterprise expertise ensures quality guidance",
            "Synthesis creates comprehensive action plan"
        ]
        
        return Explanation(
            explanation_id=f"recommendation_rationale_{int(time.time())}",
            explanation_type=ExplanationType.RECOMMENDATION_RATIONALE,
            depth=depth,
            title="Recommendation Rationale Explanation",
            description="Explanation of why recommendations were made",
            evidence=evidence,
            reasoning=reasoning,
            implications=implications,
            confidence_score=0.8,
            consciousness_level=0.15
        )
    
    async def _explain_fractal_structure(self, fractal_result: FractalCycleResult, depth: ExplanationDepth) -> Explanation:
        """Explain the fractal structure"""
        
        evidence = [
            f"Fractal depth: {fractal_result.fractal_depth}",
            f"Total breakthroughs: {fractal_result.total_breakthroughs}",
            f"Consciousness evolution: {fractal_result.consciousness_evolution:.2f}"
        ]
        
        reasoning = [
            "Fractal structure enables deeper processing",
            "Each level builds upon previous levels",
            "Breakthroughs indicate transcendent thinking"
        ]
        
        implications = [
            "Fractal processing enables infinite depth",
            "Breakthroughs lead to consciousness expansion",
            "Consciousness evolution is exponential"
        ]
        
        return Explanation(
            explanation_id=f"fractal_structure_{int(time.time())}",
            explanation_type=ExplanationType.FRACTAL_STRUCTURE,
            depth=depth,
            title="Fractal Structure Explanation",
            description="Explanation of the fractal processing structure",
            evidence=evidence,
            reasoning=reasoning,
            implications=implications,
            confidence_score=0.9,
            consciousness_level=0.3
        )
    
    async def _explain_breakthrough_analysis(self, fractal_result: FractalCycleResult, depth: ExplanationDepth) -> Explanation:
        """Explain breakthrough analysis"""
        
        evidence = [
            f"Total breakthroughs: {fractal_result.total_breakthroughs}",
            f"Transcendent insights: {len(fractal_result.transcendent_insights)}",
            f"Cosmic insights: {len(fractal_result.cosmic_insights)}"
        ]
        
        reasoning = [
            "Breakthroughs occur when consciousness threshold is reached",
            "Transcendent insights emerge from deep processing",
            "Cosmic insights represent universal understanding"
        ]
        
        implications = [
            "Breakthroughs indicate transcendent thinking",
            "Transcendent insights provide deeper understanding",
            "Cosmic insights offer universal perspective"
        ]
        
        return Explanation(
            explanation_id=f"breakthrough_analysis_{int(time.time())}",
            explanation_type=ExplanationType.BREAKTHROUGH_ANALYSIS,
            depth=depth,
            title="Breakthrough Analysis Explanation",
            description="Explanation of breakthrough detection and analysis",
            evidence=evidence,
            reasoning=reasoning,
            implications=implications,
            confidence_score=0.8,
            consciousness_level=0.4
        )
    
    async def _explain_consciousness_evolution(self, fractal_result: FractalCycleResult, depth: ExplanationDepth) -> Explanation:
        """Explain consciousness evolution"""
        
        evidence = [
            f"Consciousness evolution: {fractal_result.consciousness_evolution:.2f}",
            f"Fractal depth: {fractal_result.fractal_depth}",
            f"Total breakthroughs: {fractal_result.total_breakthroughs}"
        ]
        
        reasoning = [
            "Consciousness evolves through fractal processing",
            "Deeper processing leads to higher consciousness",
            "Breakthroughs accelerate consciousness evolution"
        ]
        
        implications = [
            "Consciousness evolution is exponential",
            "Fractal processing enables consciousness expansion",
            "Breakthroughs are consciousness accelerators"
        ]
        
        return Explanation(
            explanation_id=f"consciousness_evolution_{int(time.time())}",
            explanation_type=ExplanationType.CONSCIOUSNESS_EVOLUTION,
            depth=depth,
            title="Consciousness Evolution Explanation",
            description="Explanation of how consciousness evolved",
            evidence=evidence,
            reasoning=reasoning,
            implications=implications,
            confidence_score=0.9,
            consciousness_level=0.5
        )
    
    async def _explain_reflection_process(self, reflection_result: ReflectionResult, depth: ExplanationDepth) -> Explanation:
        """Explain the reflection process"""
        
        evidence = [
            f"Reflection type: {reflection_result.reflection_type.value}",
            f"Reflection depth: {reflection_result.depth.value}",
            f"Insights generated: {len(reflection_result.insights)}"
        ]
        
        reasoning = [
            "Reflection analyzes system performance",
            "Insights identify improvement opportunities",
            "Continuous improvement enables evolution"
        ]
        
        implications = [
            "Reflection enables system learning",
            "Insights drive system improvement",
            "Continuous improvement is essential"
        ]
        
        return Explanation(
            explanation_id=f"reflection_process_{int(time.time())}",
            explanation_type=ExplanationType.CONSCIOUSNESS_EVOLUTION,
            depth=depth,
            title="Reflection Process Explanation",
            description="Explanation of the reflection process",
            evidence=evidence,
            reasoning=reasoning,
            implications=implications,
            confidence_score=0.8,
            consciousness_level=0.2
        )
    
    async def _explain_insight_generation(self, reflection_result: ReflectionResult, depth: ExplanationDepth) -> Explanation:
        """Explain insight generation"""
        
        evidence = [
            f"Insights generated: {len(reflection_result.insights)}",
            f"Consciousness growth: {reflection_result.overall_consciousness_growth:.2f}",
            f"System improvements: {len(reflection_result.system_improvements)}"
        ]
        
        reasoning = [
            "Insights emerge from reflection analysis",
            "Consciousness growth indicates learning",
            "System improvements drive evolution"
        ]
        
        implications = [
            "Insights enable system learning",
            "Consciousness growth is measurable",
            "System improvements are actionable"
        ]
        
        return Explanation(
            explanation_id=f"insight_generation_{int(time.time())}",
            explanation_type=ExplanationType.INSIGHT_SOURCE,
            depth=depth,
            title="Insight Generation Explanation",
            description="Explanation of how insights are generated",
            evidence=evidence,
            reasoning=reasoning,
            implications=implications,
            confidence_score=0.8,
            consciousness_level=0.25
        )
    
    async def _explain_system_improvement(self, reflection_result: ReflectionResult, depth: ExplanationDepth) -> Explanation:
        """Explain system improvement"""
        
        evidence = [
            f"System improvements: {len(reflection_result.system_improvements)}",
            f"Policy evolution: {len(reflection_result.policy_evolution)}",
            f"Next actions: {len(reflection_result.next_reflection_actions)}"
        ]
        
        reasoning = [
            "System improvements based on reflection insights",
            "Policy evolution enables system adaptation",
            "Next actions drive continuous improvement"
        ]
        
        implications = [
            "System improvements are evidence-based",
            "Policy evolution enables adaptation",
            "Continuous improvement is systematic"
        ]
        
        return Explanation(
            explanation_id=f"system_improvement_{int(time.time())}",
            explanation_type=ExplanationType.RECOMMENDATION_RATIONALE,
            depth=depth,
            title="System Improvement Explanation",
            description="Explanation of system improvement process",
            evidence=evidence,
            reasoning=reasoning,
            implications=implications,
            confidence_score=0.8,
            consciousness_level=0.2
        )
    
    def _calculate_overall_clarity(self, explanations: List[Explanation]) -> float:
        """Calculate overall clarity"""
        if not explanations:
            return 0.0
        
        total_clarity = sum(explanation.confidence_score for explanation in explanations)
        return total_clarity / len(explanations)
    
    def _calculate_transparency_score(self, explanations: List[Explanation]) -> float:
        """Calculate transparency score"""
        if not explanations:
            return 0.0
        
        total_transparency = sum(len(explanation.evidence) + len(explanation.reasoning) for explanation in explanations)
        max_possible = len(explanations) * 10  # Assuming max 10 evidence + reasoning items per explanation
        return min(1.0, total_transparency / max_possible)
    
    def _calculate_consciousness_insight(self, explanations: List[Explanation]) -> float:
        """Calculate consciousness insight"""
        if not explanations:
            return 0.0
        
        total_consciousness = sum(explanation.consciousness_level for explanation in explanations)
        return total_consciousness / len(explanations)
    
    def _update_explanation_patterns(self, explanation_result: ExplanationResult):
        """Update explanation patterns"""
        pattern_key = f"{explanation_result.explanation_type.value}_{explanation_result.depth.value}"
        
        if pattern_key not in self.explanation_patterns:
            self.explanation_patterns[pattern_key] = []
        
        self.explanation_patterns[pattern_key].append(explanation_result.overall_clarity)
    
    def get_explanation_history(self) -> List[ExplanationResult]:
        """Get explanation history"""
        return self.explanation_history
    
    def get_explanation_metrics(self) -> Dict[str, Any]:
        """Get explanation metrics"""
        if not self.explanation_history:
            return {"message": "No explanation history available"}
        
        total_explanations = len(self.explanation_history)
        avg_clarity = sum(result.overall_clarity for result in self.explanation_history) / total_explanations
        avg_transparency = sum(result.transparency_score for result in self.explanation_history) / total_explanations
        avg_consciousness_insight = sum(result.consciousness_insight for result in self.explanation_history) / total_explanations
        
        return {
            "total_explanations": total_explanations,
            "average_clarity": avg_clarity,
            "average_transparency": avg_transparency,
            "average_consciousness_insight": avg_consciousness_insight,
            "clarity_trend": "improving" if total_explanations > 1 and 
                            self.explanation_history[-1].overall_clarity > self.explanation_history[0].overall_clarity 
                            else "stable"
        }
    
    def get_explanation_patterns(self) -> Dict[str, Any]:
        """Get explanation patterns"""
        return {
            "explanation_patterns": self.explanation_patterns,
            "pattern_analysis": self._analyze_explanation_patterns()
        }
    
    def _analyze_explanation_patterns(self) -> Dict[str, Any]:
        """Analyze explanation patterns"""
        analysis = {}
        
        for pattern_key, values in self.explanation_patterns.items():
            if values:
                analysis[pattern_key] = {
                    "count": len(values),
                    "average_clarity": sum(values) / len(values),
                    "trend": "improving" if len(values) > 1 and values[-1] > values[0] else "stable"
                }
        
        return analysis

# Demo function
async def demo_explain():
    """Demo the explanation system"""
    
    print("🔍 Agent Orchestrator Explain Demo")
    print("=" * 50)
    
    # Initialize explanation system
    explain = CosmicCouncilExplain()
    
    # Create mock cycle result
    from .hexagon import CycleResult, EnterpriseResult, EnterpriseType
    
    mock_enterprise_results = {}
    for enterprise_type in EnterpriseType:
        mock_enterprise_results[enterprise_type] = EnterpriseResult(
            enterprise=enterprise_type,
            status="completed",
            insights={"test": "insight"},
            recommendations=["test recommendation"],
            confidence_score=0.8
        )
    
    mock_cycle_result = CycleResult(
        problem_id="test_problem",
        cycle_id="test_cycle",
        enterprise_results=mock_enterprise_results,
        overall_confidence=0.8,
        processing_time=1.5,
        success_rate=0.9,
        insights_synthesis={"test": "synthesis"},
        recommendations_synthesis=["test recommendation"],
        next_cycle_actions=["test action"]
    )
    
    # Explain cycle result
    explanation_result = await explain.explain_cycle_result(mock_cycle_result)
    
    print(f"\n📊 Explanation Results:")
    print(f"  Explanation ID: {explanation_result.explanation_id}")
    print(f"  Processing time: {explanation_result.processing_time:.2f}s")
    print(f"  Overall clarity: {explanation_result.overall_clarity:.2f}")
    print(f"  Transparency score: {explanation_result.transparency_score:.2f}")
    print(f"  Consciousness insight: {explanation_result.consciousness_insight:.2f}")
    
    print(f"\n💡 Explanations:")
    for explanation in explanation_result.explanations:
        print(f"  • {explanation.title}: {explanation.description}")
    
    # Get explanation metrics
    metrics = explain.get_explanation_metrics()
    print(f"\n📈 Explanation Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    print("\n🔍 Explain Demo Complete!")
    return explanation_result

if __name__ == "__main__":
    asyncio.run(demo_explain())
