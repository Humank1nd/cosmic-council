#!/usr/bin/env python3
"""
🏛️ Cosmic Council Hexagon - The Brainstem
Core linear cycle logic (ROYGBV) - strictly linear, clockwise-only processing
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnterpriseType(Enum):
    """The six enterprises of the Cosmic Council"""
    RED_OWL = "red_owl"                    # Research & Inquiry
    ORANGE_ORANGUTAN = "orange_orangutan"  # Planning & Logistics
    YELLOW_HONEYBEE = "yellow_honeybee"    # Development & Creativity
    GREEN_TORTOISE = "green_tortoise"      # Budget & Resources
    BLUE_DOLPHIN = "blue_dolphin"          # Communication & Marketing
    PURPLE_ELEPHANT = "purple_elephant"    # Reflection & Empathy

class ProblemComplexity(Enum):
    """Problem complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    SYSTEMIC = "systemic"

@dataclass
class ProblemStatement:
    """Represents a problem to be solved by the Cosmic Council"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    complexity: ProblemComplexity = ProblemComplexity.MODERATE
    domain: str = ""
    stakeholders: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EnterpriseResult:
    """Result from an enterprise's processing"""
    enterprise: EnterpriseType
    status: str
    insights: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    processing_time: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class CycleResult:
    """Result from a complete ROYGBV cycle"""
    problem_id: str
    cycle_id: str
    enterprise_results: Dict[EnterpriseType, EnterpriseResult]
    overall_confidence: float
    processing_time: float
    success_rate: float
    insights_synthesis: Dict[str, Any]
    recommendations_synthesis: List[str]
    next_cycle_actions: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class CosmicCouncilHexagon:
    """
    🏛️ Cosmic Council Hexagon - The Brainstem
    
    This is the core nervous system of the Cosmic Council.
    Strictly linear, clockwise-only processing through ROYGBV sequence.
    If deeper recursion is needed → handled via cycles.py (fractal branching).
    """
    
    def __init__(self):
        self.name = "Cosmic Council Hexagon"
        self.processing_order = [
            EnterpriseType.RED_OWL,
            EnterpriseType.ORANGE_ORANGUTAN,
            EnterpriseType.YELLOW_HONEYBEE,
            EnterpriseType.GREEN_TORTOISE,
            EnterpriseType.BLUE_DOLPHIN,
            EnterpriseType.PURPLE_ELEPHANT
        ]
        
        # Enterprise registry (will be populated by enterprise services)
        self.enterprises: Dict[EnterpriseType, Any] = {}
        
        # Processing history
        self.cycle_history: List[CycleResult] = []
        
        logger.info("🏛️ Cosmic Council Hexagon initialized - Brainstem active")
    
    def register_enterprise(self, enterprise_type: EnterpriseType, enterprise_service: Any):
        """Register an enterprise service"""
        self.enterprises[enterprise_type] = enterprise_service
        logger.info(f"🔗 Registered {enterprise_type.value} enterprise")
    
    async def process_problem_linear(self, 
                                   problem: ProblemStatement,
                                   context: Dict[str, Any] = None) -> CycleResult:
        """
        Process a problem through the linear ROYGBV sequence
        
        This is the brainstem - strictly linear, clockwise-only processing.
        No parallel processing, no skipping, no backtracking.
        Each enterprise processes in sequence, building upon previous results.
        """
        
        start_time = time.time()
        cycle_id = f"cycle_{int(time.time())}"
        
        logger.info(f"🏛️ Starting linear ROYGBV cycle for: {problem.title}")
        logger.info(f"Cycle ID: {cycle_id}")
        
        # Initialize context
        if context is None:
            context = {}
        
        # Process through each enterprise in strict ROYGBV order
        enterprise_results = {}
        accumulated_insights = {}
        accumulated_recommendations = []
        
        for enterprise_type in self.processing_order:
            logger.info(f"🔄 Processing {enterprise_type.value}...")
            
            # Get enterprise service
            enterprise = self.enterprises.get(enterprise_type)
            if not enterprise:
                logger.warning(f"⚠️ Enterprise {enterprise_type.value} not registered")
                # Create a default result
                enterprise_results[enterprise_type] = EnterpriseResult(
                    enterprise=enterprise_type,
                    status="not_registered",
                    insights={"error": "Enterprise not registered"},
                    recommendations=["Register enterprise service"],
                    confidence_score=0.0
                )
                continue
            
            # Build context from previous results
            processing_context = {
                **context,
                "previous_results": {
                    ent.value: result.insights 
                    for ent, result in enterprise_results.items()
                },
                "accumulated_insights": accumulated_insights,
                "accumulated_recommendations": accumulated_recommendations
            }
            
            # Process through enterprise
            try:
                result = await enterprise.process_problem(problem, processing_context)
                enterprise_results[enterprise_type] = result
                
                # Accumulate insights and recommendations
                accumulated_insights.update(result.insights)
                accumulated_recommendations.extend(result.recommendations)
                
                logger.info(f"✅ {enterprise_type.value} completed (confidence: {result.confidence_score:.2f})")
                
            except Exception as e:
                logger.error(f"❌ Error processing {enterprise_type.value}: {e}")
                # Create error result
                enterprise_results[enterprise_type] = EnterpriseResult(
                    enterprise=enterprise_type,
                    status="error",
                    insights={"error": str(e)},
                    recommendations=["Review and retry"],
                    confidence_score=0.0
                )
        
        # Calculate overall metrics
        processing_time = time.time() - start_time
        overall_confidence = self._calculate_overall_confidence(enterprise_results)
        success_rate = self._calculate_success_rate(enterprise_results)
        
        # Synthesize insights and recommendations
        insights_synthesis = self._synthesize_insights(enterprise_results)
        recommendations_synthesis = self._synthesize_recommendations(enterprise_results)
        next_cycle_actions = self._identify_next_cycle_actions(enterprise_results)
        
        # Create cycle result
        cycle_result = CycleResult(
            problem_id=problem.id,
            cycle_id=cycle_id,
            enterprise_results=enterprise_results,
            overall_confidence=overall_confidence,
            processing_time=processing_time,
            success_rate=success_rate,
            insights_synthesis=insights_synthesis,
            recommendations_synthesis=recommendations_synthesis,
            next_cycle_actions=next_cycle_actions
        )
        
        # Store in history
        self.cycle_history.append(cycle_result)
        
        logger.info(f"🏛️ Linear ROYGBV cycle completed in {processing_time:.2f}s")
        logger.info(f"Overall confidence: {overall_confidence:.2f}")
        logger.info(f"Success rate: {success_rate:.2f}")
        
        return cycle_result
    
    def _calculate_overall_confidence(self, enterprise_results: Dict[EnterpriseType, EnterpriseResult]) -> float:
        """Calculate overall confidence from enterprise results"""
        if not enterprise_results:
            return 0.0
        
        total_confidence = sum(result.confidence_score for result in enterprise_results.values())
        return total_confidence / len(enterprise_results)
    
    def _calculate_success_rate(self, enterprise_results: Dict[EnterpriseType, EnterpriseResult]) -> float:
        """Calculate success rate from enterprise results"""
        if not enterprise_results:
            return 0.0
        
        successful = sum(1 for result in enterprise_results.values() if result.confidence_score > 0.5)
        return successful / len(enterprise_results)
    
    def _synthesize_insights(self, enterprise_results: Dict[EnterpriseType, EnterpriseResult]) -> Dict[str, Any]:
        """Synthesize insights from all enterprise results"""
        synthesis = {}
        
        for enterprise_type, result in enterprise_results.items():
            synthesis[f"{enterprise_type.value}_insights"] = result.insights
        
        return synthesis
    
    def _synthesize_recommendations(self, enterprise_results: Dict[EnterpriseType, EnterpriseResult]) -> List[str]:
        """Synthesize recommendations from all enterprise results"""
        recommendations = []
        
        for enterprise_type, result in enterprise_results.items():
            for rec in result.recommendations:
                recommendations.append(f"[{enterprise_type.value}] {rec}")
        
        return recommendations
    
    def _identify_next_cycle_actions(self, enterprise_results: Dict[EnterpriseType, EnterpriseResult]) -> List[str]:
        """Identify actions for the next cycle"""
        actions = []
        
        for enterprise_type, result in enterprise_results.items():
            actions.extend(result.next_actions)
        
        return actions
    
    def get_cycle_history(self) -> List[CycleResult]:
        """Get processing history"""
        return self.cycle_history
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        if not self.cycle_history:
            return {"message": "No cycle history available"}
        
        total_cycles = len(self.cycle_history)
        avg_confidence = sum(cycle.overall_confidence for cycle in self.cycle_history) / total_cycles
        avg_success_rate = sum(cycle.success_rate for cycle in self.cycle_history) / total_cycles
        avg_processing_time = sum(cycle.processing_time for cycle in self.cycle_history) / total_cycles
        
        return {
            "total_cycles": total_cycles,
            "average_confidence": avg_confidence,
            "average_success_rate": avg_success_rate,
            "average_processing_time": avg_processing_time,
            "performance_trend": "improving" if total_cycles > 1 and 
                                self.cycle_history[-1].overall_confidence > self.cycle_history[0].overall_confidence 
                                else "stable"
        }

# Demo function
async def demo_hexagon():
    """Demo the hexagon processing"""
    
    print("🏛️ Cosmic Council Hexagon Demo")
    print("=" * 50)
    
    # Initialize hexagon
    hexagon = CosmicCouncilHexagon()
    
    # Register enterprise stubs
    try:
        from enterprises.red_owl.services.stub import RedOwlService
        from enterprises.orange_orangutan.services.stub import OrangeOrangutanService
        from enterprises.yellow_honeybee.services.stub import YellowHoneybeeService
        from enterprises.green_tortoise.services.stub import GreenTortoiseService
        from enterprises.blue_dolphin.services.stub import BlueDolphinService
        from enterprises.purple_elephant.services.stub import PurpleElephantService

        hexagon.register_enterprise(EnterpriseType.RED_OWL, RedOwlService())
        hexagon.register_enterprise(EnterpriseType.ORANGE_ORANGUTAN, OrangeOrangutanService())
        hexagon.register_enterprise(EnterpriseType.YELLOW_HONEYBEE, YellowHoneybeeService())
        hexagon.register_enterprise(EnterpriseType.GREEN_TORTOISE, GreenTortoiseService())
        hexagon.register_enterprise(EnterpriseType.BLUE_DOLPHIN, BlueDolphinService())
        hexagon.register_enterprise(EnterpriseType.PURPLE_ELEPHANT, PurpleElephantService())
    except Exception as e:
        logger.warning(f"Stub registration warning: {e}")
    
    # Create test problem
    problem = ProblemStatement(
        title="Hexagon Processing Test",
        description="Test problem for linear ROYGBV processing",
        complexity=ProblemComplexity.MODERATE,
        metadata={"test": True}
    )
    
    # Process problem
    result = await hexagon.process_problem_linear(problem)
    
    print(f"\n📊 Cycle Results:")
    print(f"  Cycle ID: {result.cycle_id}")
    print(f"  Processing time: {result.processing_time:.2f}s")
    print(f"  Overall confidence: {result.overall_confidence:.2f}")
    print(f"  Success rate: {result.success_rate:.2f}")
    
    print(f"\n🔍 Enterprise Results:")
    for enterprise_type, enterprise_result in result.enterprise_results.items():
        print(f"  {enterprise_type.value}: {enterprise_result.status} (confidence: {enterprise_result.confidence_score:.2f})")
    
    print(f"\n💡 Recommendations:")
    for rec in result.recommendations_synthesis[:3]:  # Show first 3
        print(f"  • {rec}")
    
    print("\n🏛️ Hexagon Demo Complete!")
    return result

if __name__ == "__main__":
    import uuid
    asyncio.run(demo_hexagon())
