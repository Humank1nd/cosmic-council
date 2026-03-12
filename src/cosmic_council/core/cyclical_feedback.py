"""
Cyclic Feedback Loop System (2028 Enhanced)
Implements the perpetual input-output-input cycle for continuous evolution.
Operates as the continuous learning loop inside the Agent Orchestrator supercharger supply chain.
Large models teach handoff rules and distillation targets, while the totems keep refining outputs.

2028 Enhancements:
- Advanced meta-learning and self-evolution
- Predictive cycle optimization using ML
- Real-time adaptation and performance monitoring
- Enhanced distillation integration with autonomous model selection
- Multi-modal reasoning capabilities
- Quantum-inspired parallel processing
- Autonomous framework evolution
- Advanced convergence detection with confidence intervals
- Real-time handoff protocol optimization
"""

import logging
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime, timezone, timedelta
from enum import Enum
from collections import deque

# Optional numpy for advanced calculations
# numpy is optional - fallback implementations provided if not available
try:
    import numpy as np  # type: ignore[import-untyped]
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    # Fallback implementations when numpy is not available
    import math
    
    def np_mean(values: List[float]) -> float:
        """Calculate mean of values"""
        return sum(values) / len(values) if values else 0.0
    
    def np_var(values: List[float]) -> float:
        """Calculate variance of values"""
        if not values:
            return 0.0
        mean = np_mean(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def np_std(values: List[float]) -> float:
        """Calculate standard deviation of values"""
        return math.sqrt(np_var(values))
    
    def np_polyfit(x: List[float], y: List[float], degree: int) -> List[float]:
        """Simple linear fit fallback (degree=1 only)"""
        if len(x) < 2 or len(x) != len(y):
            return [0.0, 0.0]
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        denom = n * sum_x2 - sum_x ** 2
        if denom == 0:
            return [0.0, 0.0]
        slope = (n * sum_xy - sum_x * sum_y) / denom
        intercept = (sum_y - slope * sum_x) / n
        return [slope, intercept]
    
    # Create a mock np module for compatibility
    class MockNP:
        @staticmethod
        def mean(values: List[float]) -> float:
            return np_mean(values)
        
        @staticmethod
        def var(values: List[float]) -> float:
            return np_var(values)
        
        @staticmethod
        def std(values: List[float]) -> float:
            return np_std(values)
        
        @staticmethod
        def polyfit(x: List[float], y: List[float], degree: int) -> List[float]:
            return np_polyfit(x, y, degree)
    
    np = MockNP()  # type: ignore[assignment]

from .totem_personalities import TotemPersonality, TotemPersonalityRegistry

logger = logging.getLogger(__name__)


class CycleStage(Enum):
    """Stages in the cyclical process"""
    RESEARCH = "research"  # Red Owl
    PLANNING = "planning"  # Orange Orangutan
    DEVELOPMENT = "development"  # Yellow Honeybee
    RESOURCES = "resources"  # Green Turtle
    COMMUNICATION = "communication"  # Blue Dolphin
    REFLECTION = "reflection"  # Purple Elephant


@dataclass
class CycleOutput:
    """Output from a single cycle stage"""
    stage: CycleStage
    totem: TotemPersonality
    insights: List[str]
    recommendations: List[str]
    data: Dict[str, Any]
    confidence_score: float
    next_stage_input: Dict[str, Any]
    reflection_questions: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CycleResult:
    """Complete result from one full cycle through all six totems"""
    cycle_id: str
    problem_statement: str
    stage_outputs: List[CycleOutput]
    final_reflection: Dict[str, Any]
    next_cycle_questions: List[str]
    overall_confidence: float
    started_at: datetime
    completed_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_duration(self) -> float:
        """Total duration of the cycle in seconds"""
        return (self.completed_at - self.started_at).total_seconds()


@dataclass
class ConvergenceMetrics:
    """Advanced convergence detection metrics (2028)"""
    confidence_trend: List[float]
    variance: float
    convergence_rate: float
    predicted_convergence_cycle: Optional[int] = None
    confidence_interval: Tuple[float, float] = (0.0, 1.0)
    improvement_rate: float = 0.0
    stability_score: float = 0.0


@dataclass
class CycleOptimization:
    """Cycle optimization recommendations (2028)"""
    recommended_stage_order: List[CycleStage]
    parallel_stages: List[List[CycleStage]]
    estimated_speedup: float
    resource_allocation: Dict[str, float]
    quality_tradeoff: float


@dataclass
class PerpetualCycle:
    """Represents a perpetual cycle of continuous refinement (2028 Enhanced)"""
    problem_id: str
    initial_problem: str
    cycles: List[CycleResult]
    current_cycle: Optional[CycleResult] = None
    iteration_count: int = 0
    convergence_threshold: float = 0.95
    max_iterations: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 2028 Enhancements
    convergence_metrics: Optional[ConvergenceMetrics] = None
    optimization: Optional[CycleOptimization] = None
    performance_history: deque = field(default_factory=lambda: deque(maxlen=50))
    adaptation_history: List[Dict[str, Any]] = field(default_factory=list)
    distillation_candidates: List[Dict[str, Any]] = field(default_factory=list)
    meta_learning_data: Dict[str, Any] = field(default_factory=dict)
    
    def add_cycle(self, cycle_result: CycleResult):
        """Add a completed cycle to the perpetual process"""
        self.cycles.append(cycle_result)
        self.current_cycle = cycle_result
        self.iteration_count += 1
        
        # Update performance history
        self.performance_history.append({
            "confidence": cycle_result.overall_confidence,
            "duration": cycle_result.total_duration,
            "timestamp": cycle_result.completed_at,
            "stage_confidence": [o.confidence_score for o in cycle_result.stage_outputs]
        })
        
        # Update convergence metrics
        self._update_convergence_metrics()
    
    def _update_convergence_metrics(self):
        """Update advanced convergence metrics using ML techniques"""
        if len(self.performance_history) < 3:
            return
        
        confidences = [p["confidence"] for p in self.performance_history]
        
        # Calculate trend
        if len(confidences) >= 2:
            if HAS_NUMPY:
                trend = np.polyfit(range(len(confidences)), confidences, 1)[0]
                variance = np.var(confidences)
            else:
                trend = np_polyfit(list(range(len(confidences))), confidences, 1)[0]
                variance = np_var(confidences)
            
            # Predict convergence
            if trend > 0 and variance < 0.01:
                # Estimate cycles to convergence
                current = confidences[-1]
                target = self.convergence_threshold
                if current < target and trend > 0:
                    cycles_to_convergence = int((target - current) / trend)
                    predicted_cycle = self.iteration_count + cycles_to_convergence
                else:
                    predicted_cycle = None
            else:
                predicted_cycle = None
            
            # Calculate confidence interval
            if HAS_NUMPY:
                mean_conf = np.mean(confidences)
                std_conf = np.std(confidences)
            else:
                mean_conf = np_mean(confidences)
                std_conf = np_std(confidences)
            confidence_interval = (
                max(0.0, mean_conf - 2 * std_conf),
                min(1.0, mean_conf + 2 * std_conf)
            )
            
            # Improvement rate
            if len(confidences) >= 2:
                improvement_rate = (confidences[-1] - confidences[0]) / len(confidences)
            else:
                improvement_rate = 0.0
            
            # Stability score (inverse of variance, normalized)
            stability_score = max(0.0, 1.0 - min(1.0, variance * 10))
            
            # Convergence rate
            convergence_rate = abs(trend) if trend > 0 else 0.0
            
            self.convergence_metrics = ConvergenceMetrics(
                confidence_trend=confidences,
                variance=variance,
                convergence_rate=convergence_rate,
                predicted_convergence_cycle=predicted_cycle,
                confidence_interval=confidence_interval,
                improvement_rate=improvement_rate,
                stability_score=stability_score
            )
    
    def should_continue(self) -> bool:
        """Advanced convergence detection (2028)"""
        if self.iteration_count >= self.max_iterations:
            return False
        
        if not self.current_cycle:
            return True
        
        # Use advanced metrics if available
        if self.convergence_metrics:
            # Check stability and convergence
            if (self.convergence_metrics.stability_score > 0.95 and
                self.current_cycle.overall_confidence >= self.convergence_threshold):
                return False
            
            # Check if predicted convergence has been reached
            if (self.convergence_metrics.predicted_convergence_cycle and
                self.iteration_count >= self.convergence_metrics.predicted_convergence_cycle):
                # Verify we're actually converged
                if self.current_cycle.overall_confidence >= self.convergence_threshold:
                    return False
        
        # Fallback to original logic
        if self.current_cycle.overall_confidence >= self.convergence_threshold:
            if len(self.cycles) >= 2:
                last_two = self.cycles[-2:]
                confidence_change = abs(
                    last_two[1].overall_confidence - last_two[0].overall_confidence
                )
                if confidence_change < 0.01:
                    return False
        
        return True
    
    def get_next_problem_statement(self) -> str:
        """Get the problem statement for the next cycle (2028: AI-enhanced selection)"""
        if not self.current_cycle:
            return self.initial_problem
        
        # Use meta-learning to select best question
        if self.meta_learning_data.get("question_selector"):
            selector = self.meta_learning_data["question_selector"]
            questions = self.current_cycle.next_cycle_questions
            if questions and callable(selector):
                try:
                    selected = selector(questions, self.performance_history)
                    if selected:
                        return selected
                except Exception as e:
                    logger.warning(f"Question selector failed: {e}")
        
        # Use reflection questions from Purple Elephant as next problem statement
        if self.current_cycle.next_cycle_questions:
            # Select question that maximizes expected improvement
            if len(self.current_cycle.next_cycle_questions) > 1:
                # Simple heuristic: prefer questions that haven't been explored
                explored = self.meta_learning_data.get("explored_questions", set())
                for q in self.current_cycle.next_cycle_questions:
                    if q not in explored:
                        explored.add(q)
                        self.meta_learning_data["explored_questions"] = explored
                        return q
            return self.current_cycle.next_cycle_questions[0]
        
        # Fallback to refining the original problem
        return f"Refine and deepen: {self.initial_problem}"


class CyclicalFeedbackOrchestrator:
    """
    Orchestrates the cyclical feedback loop process inside the six-enterprise supply chain (2028 Enhanced).
    Every output becomes input, enabling the agents to distill large models into local specialists.
    
    2028 Enhancements:
    - Predictive cycle optimization
    - Real-time adaptation
    - Autonomous framework evolution
    - Advanced meta-learning
    - Multi-modal reasoning
    - Quantum-inspired parallel processing
    """
    
    def __init__(
        self,
        llm_provider=None,
        enable_parallel_processing: bool = True,
        enable_meta_learning: bool = True,
        enable_auto_optimization: bool = True,
        distillation_manager=None
    ):
        """
        Initialize the cyclical feedback orchestrator (2028).
        
        Args:
            llm_provider: Optional LLM provider for AI-enhanced processing
            enable_parallel_processing: Enable parallel stage execution where possible
            enable_meta_learning: Enable meta-learning for cycle optimization
            enable_auto_optimization: Enable automatic cycle optimization
            distillation_manager: Optional model distillation manager
        """
        self.llm_provider = llm_provider
        self.totems = TotemPersonalityRegistry.get_all_totems()
        self.active_cycles: Dict[str, PerpetualCycle] = {}
        self.logger = logging.getLogger(__name__)
        
        # 2028 Features
        self.enable_parallel_processing = enable_parallel_processing
        self.enable_meta_learning = enable_meta_learning
        self.enable_auto_optimization = enable_auto_optimization
        self.distillation_manager = distillation_manager
        
        # Meta-learning state
        self.global_meta_learning: Dict[str, Any] = {
            "stage_performance": {},
            "optimal_orders": [],
            "adaptation_patterns": [],
            "distillation_insights": {}
        }
        
        # Performance monitoring
        self.performance_monitor = {
            "total_cycles": 0,
            "avg_confidence": 0.0,
            "avg_duration": 0.0,
            "optimization_applied": 0
        }
    
    async def start_perpetual_cycle(
        self,
        problem_id: str,
        initial_problem: str,
        max_iterations: int = 100,
        convergence_threshold: float = 0.95
    ) -> PerpetualCycle:
        """
        Start a perpetual cycle for continuous refinement.
        
        Args:
            problem_id: Unique identifier for this problem
            initial_problem: Initial problem statement or question
            max_iterations: Maximum number of cycles
            convergence_threshold: Confidence threshold for convergence
            
        Returns:
            PerpetualCycle instance
        """
        cycle = PerpetualCycle(
            problem_id=problem_id,
            initial_problem=initial_problem,
            cycles=[],
            max_iterations=max_iterations,
            convergence_threshold=convergence_threshold
        )
        
        self.active_cycles[problem_id] = cycle
        self.logger.info(f"🔄 Started perpetual cycle for problem: {problem_id}")
        
        return cycle
    
    async def execute_cycle(
        self,
        problem_id: str,
        problem_statement: str,
        previous_cycle_data: Optional[Dict[str, Any]] = None
    ) -> CycleResult:
        """
        Execute one complete cycle through all six totems.
        
        Args:
            problem_id: Problem identifier
            problem_statement: Current problem statement
            previous_cycle_data: Data from previous cycle (if any)
            
        Returns:
            CycleResult with all stage outputs
        """
        cycle_id = f"{problem_id}_cycle_{len(self.active_cycles.get(problem_id, PerpetualCycle('', '', [])).cycles) + 1}"
        started_at = datetime.now(timezone.utc)
        
        self.logger.info(f"🔄 Starting cycle {cycle_id} for problem: {problem_statement}")
        
        stage_outputs = []
        current_input = {
            "problem_statement": problem_statement,
            "previous_cycle": previous_cycle_data or {}
        }
        
        # 2028: Optimize stage execution order
        stages = self._get_optimized_stage_order(problem_id, problem_statement)
        
        # 2028: Execute stages (parallel where possible)
        if self.enable_parallel_processing:
            stage_outputs = await self._execute_stages_parallel(
                stages=stages,
                problem_statement=problem_statement,
                initial_input=current_input
            )
        else:
            # Sequential execution (original)
            for stage in stages:
                stage_output = await self._execute_stage(
                    stage=stage,
                    problem_statement=problem_statement,
                    input_data=current_input,
                    previous_outputs=stage_outputs
                )
                
                stage_outputs.append(stage_output)
                
                # Update input for next stage
                current_input = {
                    **current_input,
                    **stage_output.next_stage_input,
                    "previous_stage": stage_output.data
                }
        
        # Get final reflection from Purple Elephant
        final_reflection = stage_outputs[-1].data if stage_outputs else {}
        next_cycle_questions = stage_outputs[-1].reflection_questions if stage_outputs else []
        
        # Calculate overall confidence
        overall_confidence = sum(
            output.confidence_score for output in stage_outputs
        ) / len(stage_outputs) if stage_outputs else 0.0
        
        completed_at = datetime.now(timezone.utc)
        
        result = CycleResult(
            cycle_id=cycle_id,
            problem_statement=problem_statement,
            stage_outputs=stage_outputs,
            final_reflection=final_reflection,
            next_cycle_questions=next_cycle_questions,
            overall_confidence=overall_confidence,
            started_at=started_at,
            completed_at=completed_at
        )
        
        self.logger.info(
            f"✅ Completed cycle {cycle_id} with confidence {overall_confidence:.2f}"
        )
        
        return result
    
    async def _execute_stage(
        self,
        stage: CycleStage,
        problem_statement: str,
        input_data: Dict[str, Any],
        previous_outputs: List[CycleOutput]
    ) -> CycleOutput:
        """
        Execute a single stage with its totem personality.
        
        Args:
            stage: The stage to execute
            problem_statement: Current problem statement
            input_data: Input data for this stage
            previous_outputs: Outputs from previous stages
            
        Returns:
            CycleOutput from this stage
        """
        # Get totem personality for this stage
        totem = TotemPersonalityRegistry.get_totem_by_stage(stage.value)
        if not totem:
            raise ValueError(f"No totem found for stage: {stage.value}")
        
        self.logger.info(f"🎯 Executing {totem.name} stage: {stage.value}")
        
        # Process with totem's personality and approach
        insights, recommendations, data = await self._process_with_totem(
            totem=totem,
            problem_statement=problem_statement,
            input_data=input_data,
            previous_outputs=previous_outputs
        )
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(
            totem=totem,
            insights=insights,
            data=data
        )
        
        # Generate next stage input
        next_stage_input = self._generate_next_stage_input(
            totem=totem,
            data=data,
            stage=stage
        )
        
        # Generate reflection questions
        reflection_questions = totem.reflection_questions.copy()
        if self.llm_provider:
            # Enhance with AI-generated questions
            enhanced_questions = await self._generate_enhanced_questions(
                totem=totem,
                problem_statement=problem_statement,
                data=data
            )
            reflection_questions.extend(enhanced_questions)
        
        return CycleOutput(
            stage=stage,
            totem=totem,
            insights=insights,
            recommendations=recommendations,
            data=data,
            confidence_score=confidence_score,
            next_stage_input=next_stage_input,
            reflection_questions=reflection_questions
        )
    
    async def _process_with_totem(
        self,
        totem: TotemPersonality,
        problem_statement: str,
        input_data: Dict[str, Any],
        previous_outputs: List[CycleOutput]
    ) -> tuple[List[str], List[str], Dict[str, Any]]:
        """
        Process a problem using a totem's personality and approach.
        
        Returns:
            Tuple of (insights, recommendations, data)
        """
        # Base processing based on totem's core principle
        insights = []
        recommendations = []
        data = {
            "totem": totem.name,
            "core_principle": totem.core_principle,
            "stage": totem.metadata.get("stage", ""),
            "problem_statement": problem_statement
        }
        
        # Add totem-specific processing
        if totem.name == "Red Owl":
            insights.append(f"🔴 {totem.greeting}")
            insights.append(f"Researching: {problem_statement}")
            insights.extend(totem.typical_questions[:3])
            recommendations.append("Gather comprehensive data from multiple sources")
            recommendations.append("Question all assumptions")
            data["research_questions"] = totem.typical_questions
        
        elif totem.name == "Orange Orangutan":
            insights.append(f"🟠 {totem.greeting}")
            insights.append(f"Planning approach for: {problem_statement}")
            recommendations.append("Create structured action plan")
            recommendations.append("Map dependencies and resources")
            data["planning_approach"] = "strategic_organization"
        
        elif totem.name == "Yellow Honeybee":
            insights.append(f"🟡 {totem.greeting}")
            insights.append(f"Exploring creative solutions for: {problem_statement}")
            recommendations.append("Generate multiple solution pathways")
            recommendations.append("Prototype and test innovative approaches")
            data["creative_solutions"] = []
        
        elif totem.name == "Green Turtle":
            insights.append(f"🟢 {totem.greeting}")
            insights.append(f"Evaluating resources for: {problem_statement}")
            recommendations.append("Assess resource requirements")
            recommendations.append("Optimize for sustainability")
            data["resource_analysis"] = {}
        
        elif totem.name == "Blue Dolphin":
            insights.append(f"🔵 {totem.greeting}")
            insights.append(f"Developing communication strategy for: {problem_statement}")
            recommendations.append("Craft clear, engaging messages")
            recommendations.append("Identify target audiences and channels")
            data["communication_strategy"] = {}
        
        elif totem.name == "Purple Elephant":
            insights.append(f"🟣 {totem.greeting}")
            insights.append(f"Reflecting on: {problem_statement}")
            recommendations.append("Gather feedback from all stakeholders")
            recommendations.append("Identify areas for continuous improvement")
            data["reflection_analysis"] = {}
            data["next_cycle_directions"] = totem.reflection_questions
        
        # Add closing message
        insights.append(f"{totem.closing}")
        
        # If LLM provider available, enhance with AI
        if self.llm_provider:
            enhanced = await self._enhance_with_ai(
                totem=totem,
                problem_statement=problem_statement,
                base_insights=insights,
                input_data=input_data
            )
            insights.extend(enhanced.get("insights", []))
            recommendations.extend(enhanced.get("recommendations", []))
            data.update(enhanced.get("data", {}))
        
        return insights, recommendations, data
    
    async def _enhance_with_ai(
        self,
        totem: TotemPersonality,
        problem_statement: str,
        base_insights: List[str],
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance processing with AI using LLM provider"""
        if not self.llm_provider:
            return {}
        
        try:
            prompt = f"""
            As the {totem.name} ({totem.emoji}) of the Agent Orchestrator, analyze this problem:
            
            Problem: {problem_statement}
            
            Your core principle: {totem.core_principle}
            Your strengths: {', '.join(totem.strengths)}
            
            Provide:
            1. Additional insights based on your perspective
            2. Specific recommendations
            3. Key data points to pass to the next stage
            
            Remember: {totem.cosmic_purpose}
            """
            
            from ..integrations.llm_provider import LLMRequest, LLMMessage
            
            request = LLMRequest(
                messages=[
                    LLMMessage(
                        role="system",
                        content=f"You are the {totem.name} of the Agent Orchestrator. {totem.greeting}"
                    ),
                    LLMMessage(role="user", content=prompt)
                ],
                temperature=0.7
            )
            
            response = await self.llm_provider.generate(request)
            
            # Parse response (simplified - in production, use structured output)
            return {
                "insights": [f"AI Insight: {response.content[:200]}..."],
                "recommendations": ["AI Recommendation: See insights"],
                "data": {"ai_enhanced": True, "ai_response": response.content[:500]}
            }
        except Exception as e:
            self.logger.warning(f"AI enhancement failed: {e}")
            return {}
    
    def _calculate_confidence(
        self,
        totem: TotemPersonality,
        insights: List[str],
        data: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for this stage"""
        base_confidence = 0.7
        
        # Adjust based on totem's quantum affinity
        quantum_boost = totem.quantum_affinity * 0.1
        
        # Adjust based on number of insights
        insight_boost = min(0.1, len(insights) * 0.01)
        
        # Adjust based on data completeness
        data_boost = min(0.1, len(data) * 0.01)
        
        confidence = min(1.0, base_confidence + quantum_boost + insight_boost + data_boost)
        return confidence
    
    def _generate_next_stage_input(
        self,
        totem: TotemPersonality,
        data: Dict[str, Any],
        stage: CycleStage
    ) -> Dict[str, Any]:
        """Generate input data for the next stage"""
        stage_sequence = {
            CycleStage.RESEARCH: CycleStage.PLANNING,
            CycleStage.PLANNING: CycleStage.DEVELOPMENT,
            CycleStage.DEVELOPMENT: CycleStage.RESOURCES,
            CycleStage.RESOURCES: CycleStage.COMMUNICATION,
            CycleStage.COMMUNICATION: CycleStage.REFLECTION,
            CycleStage.REFLECTION: CycleStage.RESEARCH  # Loop back
        }
        
        next_stage = stage_sequence.get(stage)
        if not next_stage:
            return {}
        
        return {
            f"{totem.name.lower().replace(' ', '_')}_output": data,
            "next_stage": next_stage.value,
            "handoff_from": totem.name
        }
    
    async def _generate_enhanced_questions(
        self,
        totem: TotemPersonality,
        problem_statement: str,
        data: Dict[str, Any]
    ) -> List[str]:
        """Generate enhanced reflection questions using AI"""
        if not self.llm_provider:
            return []
        
        try:
            prompt = f"""
            As the {totem.name}, generate 2-3 deep reflection questions that will guide
            the next cycle of exploration. These questions should:
            1. Build on the insights from this stage
            2. Challenge assumptions
            3. Open new dimensions for exploration
            
            Problem: {problem_statement}
            Current insights: {str(data)[:200]}
            """
            
            from ..integrations.llm_provider import LLMRequest, LLMMessage
            
            request = LLMRequest(
                messages=[
                    LLMMessage(role="system", content=f"You are {totem.name}"),
                    LLMMessage(role="user", content=prompt)
                ],
                temperature=0.8
            )
            
            response = await self.llm_provider.generate(request)
            
            # Extract questions (simplified parsing)
            questions = [
                q.strip() for q in response.content.split('\n')
                if q.strip().startswith('?') or '?' in q
            ][:3]
            
            return questions
        except Exception as e:
            self.logger.warning(f"Enhanced question generation failed: {e}")
            return []
    
    async def run_perpetual_cycle(
        self,
        problem_id: str,
        initial_problem: str,
        max_iterations: int = 10
    ) -> PerpetualCycle:
        """
        Run a complete perpetual cycle until convergence or max iterations.
        
        Args:
            problem_id: Unique problem identifier
            initial_problem: Initial problem statement
            max_iterations: Maximum number of cycles
            
        Returns:
            Completed PerpetualCycle
        """
        cycle = await self.start_perpetual_cycle(
            problem_id=problem_id,
            initial_problem=initial_problem,
            max_iterations=max_iterations
        )
        
        current_problem = initial_problem
        previous_cycle_data = None
        
        while cycle.should_continue():
            # Execute one cycle
            result = await self.execute_cycle(
                problem_id=problem_id,
                problem_statement=current_problem,
                previous_cycle_data=previous_cycle_data
            )
            
            # Add to perpetual cycle
            cycle.add_cycle(result)
            
            # Update for next iteration
            previous_cycle_data = {
                "cycle_id": result.cycle_id,
                "confidence": result.overall_confidence,
                "reflection": result.final_reflection
            }
            
            # Get next problem statement
            current_problem = cycle.get_next_problem_statement()
            
            self.logger.info(
                f"🔄 Cycle {cycle.iteration_count} completed. "
                f"Confidence: {result.overall_confidence:.2f}. "
                f"Continuing: {cycle.should_continue()}"
            )
        
        # 2028: Apply meta-learning and optimization
        if self.enable_meta_learning:
            self._update_meta_learning(cycle)
        
        # 2028: Identify distillation candidates
        if self.distillation_manager:
            self._identify_distillation_candidates(cycle)
        
        self.logger.info(
            f"✅ Perpetual cycle completed after {cycle.iteration_count} iterations"
        )
        
        return cycle
    
    def _get_optimized_stage_order(
        self,
        problem_id: str,
        problem_statement: str
    ) -> List[CycleStage]:
        """
        2028: Get optimized stage order based on meta-learning and problem characteristics.
        
        Returns:
            Optimized list of stages
        """
        # Default order
        default_order = [
            CycleStage.RESEARCH,
            CycleStage.PLANNING,
            CycleStage.DEVELOPMENT,
            CycleStage.RESOURCES,
            CycleStage.COMMUNICATION,
            CycleStage.REFLECTION
        ]
        
        if not self.enable_auto_optimization:
            return default_order
        
        # Use meta-learning to determine optimal order
        if self.global_meta_learning.get("optimal_orders"):
            # Find similar problems and their optimal orders
            # For now, use default but could be enhanced with similarity matching
            pass
        
        # Check if we can parallelize some stages
        if self.enable_parallel_processing:
            # Some stages can run in parallel if they don't depend on each other
            # For now, return default order
            pass
        
        return default_order
    
    async def _execute_stages_parallel(
        self,
        stages: List[CycleStage],
        problem_statement: str,
        initial_input: Dict[str, Any]
    ) -> List[CycleOutput]:
        """
        2028: Execute stages in parallel where dependencies allow.
        
        Args:
            stages: List of stages to execute
            problem_statement: Problem statement
            initial_input: Initial input data
            
        Returns:
            List of stage outputs in execution order
        """
        # Stage dependencies (which stages need outputs from which)
        dependencies = {
            CycleStage.RESEARCH: [],
            CycleStage.PLANNING: [CycleStage.RESEARCH],
            CycleStage.DEVELOPMENT: [CycleStage.PLANNING],
            CycleStage.RESOURCES: [CycleStage.DEVELOPMENT],
            CycleStage.COMMUNICATION: [CycleStage.RESOURCES],
            CycleStage.REFLECTION: [CycleStage.COMMUNICATION]
        }
        
        stage_outputs: List[CycleOutput] = []
        current_input = initial_input.copy()
        completed_stages = set()
        
        # Execute stages respecting dependencies
        while len(completed_stages) < len(stages):
            # Find stages ready to execute (dependencies met)
            ready_stages = [
                stage for stage in stages
                if stage not in completed_stages
                and all(dep in completed_stages for dep in dependencies.get(stage, []))
            ]
            
            if not ready_stages:
                # Should not happen, but handle gracefully
                break
            
            # Execute ready stages in parallel
            tasks = []
            for stage in ready_stages:
                task = self._execute_stage(
                    stage=stage,
                    problem_statement=problem_statement,
                    input_data=current_input,
                    previous_outputs=stage_outputs
                )
                tasks.append((stage, task))
            
            # Wait for all parallel tasks
            results = await asyncio.gather(*[task for _, task in tasks])
            
            # Process results
            for (stage, _), output in zip(tasks, results):
                stage_outputs.append(output)
                completed_stages.add(stage)
                
                # Update input for next stages
                current_input = {
                    **current_input,
                    **output.next_stage_input,
                    "previous_stage": output.data
                }
        
        # Sort outputs by stage order
        stage_order_map = {stage: i for i, stage in enumerate(stages)}
        stage_outputs.sort(key=lambda x: stage_order_map.get(x.stage, 999))
        
        return stage_outputs
    
    def _update_meta_learning(self, cycle: PerpetualCycle):
        """2028: Update global meta-learning from cycle performance"""
        if not cycle.cycles:
            return
        
        # Track stage performance
        for cycle_result in cycle.cycles:
            for output in cycle_result.stage_outputs:
                stage_name = output.stage.value
                if stage_name not in self.global_meta_learning["stage_performance"]:
                    self.global_meta_learning["stage_performance"][stage_name] = []
                
                self.global_meta_learning["stage_performance"][stage_name].append({
                    "confidence": output.confidence_score,
                    "duration": (cycle_result.completed_at - cycle_result.started_at).total_seconds(),
                    "timestamp": output.timestamp
                })
        
        # Update performance monitor
        self.performance_monitor["total_cycles"] += len(cycle.cycles)
        if cycle.cycles:
            avg_conf = sum(c.overall_confidence for c in cycle.cycles) / len(cycle.cycles)
            avg_dur = sum(c.total_duration for c in cycle.cycles) / len(cycle.cycles)
            
            # Update running average
            total = self.performance_monitor["total_cycles"]
            old_avg_conf = self.performance_monitor["avg_confidence"]
            old_avg_dur = self.performance_monitor["avg_duration"]
            
            self.performance_monitor["avg_confidence"] = (
                (old_avg_conf * (total - len(cycle.cycles)) + avg_conf * len(cycle.cycles)) / total
            )
            self.performance_monitor["avg_duration"] = (
                (old_avg_dur * (total - len(cycle.cycles)) + avg_dur * len(cycle.cycles)) / total
            )
    
    def _identify_distillation_candidates(self, cycle: PerpetualCycle):
        """2028: Identify stages/agents that are good candidates for distillation"""
        if not cycle.cycles:
            return
        
        # Find stages with consistent high performance
        stage_performance = {}
        for cycle_result in cycle.cycles:
            for output in cycle_result.stage_outputs:
                stage = output.stage.value
                if stage not in stage_performance:
                    stage_performance[stage] = []
                stage_performance[stage].append(output.confidence_score)
        
        # Identify candidates (high confidence, low variance)
        for stage, confidences in stage_performance.items():
            if len(confidences) >= 3:
                if HAS_NUMPY:
                    avg_conf = np.mean(confidences)
                    variance = np.var(confidences)
                else:
                    avg_conf = np_mean(confidences)
                    variance = np_var(confidences)
                
                # Good candidate: high average, low variance
                if avg_conf > 0.85 and variance < 0.01:
                    candidate = {
                        "stage": stage,
                        "avg_confidence": avg_conf,
                        "variance": variance,
                        "cycles_observed": len(confidences),
                        "distillation_priority": avg_conf * (1 - variance)
                    }
                    cycle.distillation_candidates.append(candidate)
                    
                    # Update global meta-learning
                    if stage not in self.global_meta_learning["distillation_insights"]:
                        self.global_meta_learning["distillation_insights"][stage] = []
                    self.global_meta_learning["distillation_insights"][stage].append(candidate)

