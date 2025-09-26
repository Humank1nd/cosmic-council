"""
🔄 Cosmic Council Think Tank Integration System
Seamless Integration of All Six Think Tanks

This system creates seamless integration where each Think Tank's takeaway feeds into 
the next, ensuring a cyclical process that addresses every aspect of inquiry from 
foundational principles to societal implications. It embodies the eternal dance of 
knowledge and wisdom.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import math

# Import all Think Tank modules
from think_tank_red_owl_genesis import RedOwlGenesisThinkTank, GenesisResult, InquiryDepth, CulturalDomain
from think_tank_orange_orangutan_logistics import OrangeOrangutanLogisticsThinkTank, LogisticsResult, PlanningDepth, PlanningMethodology
from think_tank_yellow_honeybee_innovation import YellowHoneybeeInnovationThinkTank, InnovationResult, InnovationDepth, CreativeDomain
from think_tank_green_tortoise_resources import GreenTortoiseResourceThinkTank, ResourceResult, ResourceType, RiskLevel, SustainabilityLevel
from think_tank_blue_dolphin_communication import BlueDolphinCommunicationThinkTank, CommunicationResult, CommunicationChannel, AudienceSegment, EmotionalResonance
from think_tank_purple_elephant_reflection import PurpleElephantReflectionThinkTank, ReflectionResult, ReflectionDepth, EmpathyLevel, EthicalAlignment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationPhase(Enum):
    """Phases of the integrated Think Tank process"""
    GENESIS = "genesis"           # Red Owl: Why
    LOGISTICS = "logistics"       # Orange Orangutan: How
    INNOVATION = "innovation"     # Yellow Honeybee: What
    RESOURCES = "resources"       # Green Tortoise: When
    COMMUNICATION = "communication" # Blue Dolphin: Where/Interpersonal
    REFLECTION = "reflection"     # Purple Elephant: Who
    SYNTHESIS = "synthesis"       # Integration and Wisdom Synthesis

class IntegrationStatus(Enum):
    """Status of the integration process"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SYNTHESIZED = "synthesized"

@dataclass
class ThinkTankResult:
    """Result from a single Think Tank"""
    phase: IntegrationPhase
    result: Union[GenesisResult, LogisticsResult, InnovationResult, ResourceResult, CommunicationResult, ReflectionResult]
    status: IntegrationStatus
    processing_time: float
    confidence_score: float
    key_insights: List[str]
    next_phase_inputs: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class IntegrationCycle:
    """Represents a complete integration cycle through all Think Tanks"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    problem_statement: str = ""
    cycle_number: int = 1
    think_tank_results: Dict[IntegrationPhase, ThinkTankResult] = field(default_factory=dict)
    integration_synthesis: Dict[str, Any] = field(default_factory=dict)
    overall_confidence: float = 0.0
    total_processing_time: float = 0.0
    status: IntegrationStatus = IntegrationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

@dataclass
class WisdomSynthesis:
    """Represents the final wisdom synthesis from all Think Tanks"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cycle_id: str = ""
    synthesis_text: str = ""
    key_insights: List[str] = field(default_factory=list)
    actionable_recommendations: List[str] = field(default_factory=list)
    next_cycle_questions: List[str] = field(default_factory=list)
    wisdom_principles: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

class CosmicCouncilThinkTankIntegration:
    """🔄 Cosmic Council Think Tank Integration System
    
    Creates seamless integration where each Think Tank's takeaway feeds into the next, 
    ensuring a cyclical process that addresses every aspect of inquiry from foundational 
    principles to societal implications.
    """
    
    def __init__(self):
        self.name = "Cosmic Council Think Tank Integration System"
        self.think_tanks = {
            IntegrationPhase.GENESIS: RedOwlGenesisThinkTank(),
            IntegrationPhase.LOGISTICS: OrangeOrangutanLogisticsThinkTank(),
            IntegrationPhase.INNOVATION: YellowHoneybeeInnovationThinkTank(),
            IntegrationPhase.RESOURCES: GreenTortoiseResourceThinkTank(),
            IntegrationPhase.COMMUNICATION: BlueDolphinCommunicationThinkTank(),
            IntegrationPhase.REFLECTION: PurpleElephantReflectionThinkTank()
        }
        self.integration_history: List[IntegrationCycle] = []
        
    async def conduct_integrated_inquiry(self, problem_statement: str, 
                                       initial_context: Dict[str, Any] = None,
                                       cycle_number: int = 1) -> IntegrationCycle:
        """Conduct a complete integrated inquiry through all Think Tanks"""
        start_time = datetime.utcnow()
        
        logger.info(f"🔄 Beginning Integrated Cosmic Council Inquiry - Cycle {cycle_number}")
        logger.info(f"Problem: {problem_statement}")
        
        # Initialize integration cycle
        cycle = IntegrationCycle(
            problem_statement=problem_statement,
            cycle_number=cycle_number,
            status=IntegrationStatus.IN_PROGRESS
        )
        
        # Phase 1: Genesis Plane (Red Owl) - Why
        logger.info("🔴🦉 Phase 1: Genesis Plane - Red Owl")
        genesis_result = await self._conduct_genesis_phase(problem_statement, initial_context or {})
        cycle.think_tank_results[IntegrationPhase.GENESIS] = genesis_result
        
        # Phase 2: Logistics Nexus (Orange Orangutan) - How
        logger.info("🟠🦧 Phase 2: Logistics Nexus - Orange Orangutan")
        logistics_result = await self._conduct_logistics_phase(genesis_result)
        cycle.think_tank_results[IntegrationPhase.LOGISTICS] = logistics_result
        
        # Phase 3: Innovation Sphere (Yellow Honeybee) - What
        logger.info("🟡🐝 Phase 3: Innovation Sphere - Yellow Honeybee")
        innovation_result = await self._conduct_innovation_phase(logistics_result)
        cycle.think_tank_results[IntegrationPhase.INNOVATION] = innovation_result
        
        # Phase 4: Verdant Expanse (Green Tortoise) - When
        logger.info("🟢🐢 Phase 4: Verdant Expanse - Green Tortoise")
        resource_result = await self._conduct_resource_phase(innovation_result)
        cycle.think_tank_results[IntegrationPhase.RESOURCES] = resource_result
        
        # Phase 5: Market of Echoes (Blue Dolphin) - Where/Interpersonal
        logger.info("🔵🐬 Phase 5: Market of Echoes - Blue Dolphin")
        communication_result = await self._conduct_communication_phase(resource_result)
        cycle.think_tank_results[IntegrationPhase.COMMUNICATION] = communication_result
        
        # Phase 6: Third Eye (Purple Elephant) - Who
        logger.info("🟣🐘 Phase 6: Third Eye - Purple Elephant")
        reflection_result = await self._conduct_reflection_phase(communication_result)
        cycle.think_tank_results[IntegrationPhase.REFLECTION] = reflection_result
        
        # Phase 7: Integration Synthesis
        logger.info("🔄 Phase 7: Integration Synthesis")
        integration_synthesis = await self._conduct_integration_synthesis(cycle)
        cycle.integration_synthesis = integration_synthesis
        
        # Calculate overall metrics
        cycle.overall_confidence = self._calculate_overall_confidence(cycle.think_tank_results)
        cycle.total_processing_time = (datetime.utcnow() - start_time).total_seconds()
        cycle.status = IntegrationStatus.COMPLETED
        cycle.completed_at = datetime.utcnow()
        
        # Add to history
        self.integration_history.append(cycle)
        
        logger.info(f"🔄 Integrated Cosmic Council Inquiry completed in {cycle.total_processing_time:.2f}s")
        logger.info(f"Overall Confidence: {cycle.overall_confidence:.2f}")
        
        return cycle
    
    async def _conduct_genesis_phase(self, problem_statement: str, 
                                   initial_context: Dict[str, Any]) -> ThinkTankResult:
        """Conduct the Genesis Plane phase (Red Owl)"""
        start_time = datetime.utcnow()
        
        think_tank = self.think_tanks[IntegrationPhase.GENESIS]
        
        # Conduct genesis inquiry
        result = await think_tank.conduct_genesis_inquiry(
            problem_statement=problem_statement,
            inquiry_depth=InquiryDepth.FOUNDATIONAL,
            cultural_domains=[
                CulturalDomain.WESTERN_PHILOSOPHY,
                CulturalDomain.EASTERN_WISDOM,
                CulturalDomain.INDIGENOUS_KNOWLEDGE,
                CulturalDomain.MODERN_THOUGHT
            ]
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Extract key insights and prepare inputs for next phase
        key_insights = [
            f"Core principles identified: {len(result.core_principles)}",
            f"Philosophical foundations established: {len(result.philosophical_foundations)}",
            f"Cultural insights gathered: {len(result.cultural_insights)}",
            f"Motivation analysis completed: {len(result.motivation_analysis)}"
        ]
        
        next_phase_inputs = {
            "core_principles": result.core_principles,
            "philosophical_foundations": result.philosophical_foundations,
            "cultural_insights": result.cultural_insights,
            "motivation_analysis": result.motivation_analysis,
            "wisdom_synthesis": result.wisdom_synthesis
        }
        
        return ThinkTankResult(
            phase=IntegrationPhase.GENESIS,
            result=result,
            status=IntegrationStatus.COMPLETED,
            processing_time=processing_time,
            confidence_score=result.confidence_score,
            key_insights=key_insights,
            next_phase_inputs=next_phase_inputs
        )
    
    async def _conduct_logistics_phase(self, genesis_result: ThinkTankResult) -> ThinkTankResult:
        """Conduct the Logistics Nexus phase (Orange Orangutan)"""
        start_time = datetime.utcnow()
        
        think_tank = self.think_tanks[IntegrationPhase.LOGISTICS]
        
        # Extract inputs from genesis phase
        core_principles = genesis_result.next_phase_inputs["core_principles"]
        philosophical_foundations = genesis_result.next_phase_inputs["philosophical_foundations"]
        
        # Conduct logistics inquiry
        result = await think_tank.conduct_logistics_inquiry(
            problem_statement=genesis_result.result.problem_statement,
            core_principles=core_principles,
            planning_depth=PlanningDepth.STRATEGIC,
            methodologies=[
                PlanningMethodology.SUN_TZU_STRATEGY,
                PlanningMethodology.LOVELACE_ALGORITHMIC,
                PlanningMethodology.SYSTEMS_THINKING
            ],
            constraints={"budget": "moderate", "timeline": "18 months"},
            resources_available={"team_size": "8-12 people", "expertise": "multi-disciplinary"}
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Extract key insights and prepare inputs for next phase
        key_insights = [
            f"Strategic analysis completed: {len(result.strategic_analysis)}",
            f"Planning frameworks developed: {len(result.planning_frameworks)}",
            f"Actionable strategies created: {len(result.actionable_strategies)}",
            f"Resource plan established: {len(result.resource_plan)}"
        ]
        
        next_phase_inputs = {
            "core_principles": core_principles,
            "strategic_frameworks": result.planning_frameworks,
            "actionable_strategies": result.actionable_strategies,
            "resource_plan": result.resource_plan,
            "timeline_framework": result.timeline_framework
        }
        
        return ThinkTankResult(
            phase=IntegrationPhase.LOGISTICS,
            result=result,
            status=IntegrationStatus.COMPLETED,
            processing_time=processing_time,
            confidence_score=result.confidence_score,
            key_insights=key_insights,
            next_phase_inputs=next_phase_inputs
        )
    
    async def _conduct_innovation_phase(self, logistics_result: ThinkTankResult) -> ThinkTankResult:
        """Conduct the Innovation Sphere phase (Yellow Honeybee)"""
        start_time = datetime.utcnow()
        
        think_tank = self.think_tanks[IntegrationPhase.INNOVATION]
        
        # Extract inputs from logistics phase
        core_principles = logistics_result.next_phase_inputs["core_principles"]
        strategic_frameworks = logistics_result.next_phase_inputs["strategic_frameworks"]
        actionable_strategies = logistics_result.next_phase_inputs["actionable_strategies"]
        
        # Conduct innovation inquiry
        result = await think_tank.conduct_innovation_inquiry(
            problem_statement=logistics_result.result.problem_statement,
            core_principles=core_principles,
            strategic_frameworks=strategic_frameworks,
            innovation_depth=InnovationDepth.DISRUPTIVE,
            creative_domains=[
                CreativeDomain.INTERDISCIPLINARY,
                CreativeDomain.TECHNOLOGICAL,
                CreativeDomain.SOCIAL
            ],
            constraints={"budget": "moderate", "timeline": "18 months"},
            opportunities={"technology": "AI and collaboration tools", "community": "global network"}
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Extract key insights and prepare inputs for next phase
        key_insights = [
            f"Innovation analysis completed: {len(result.innovation_analysis)}",
            f"Creative solutions developed: {len(result.creative_solutions)}",
            f"Design frameworks created: {len(result.design_frameworks)}",
            f"Implementation roadmap established: {len(result.implementation_roadmap)}"
        ]
        
        next_phase_inputs = {
            "core_principles": core_principles,
            "strategic_frameworks": strategic_frameworks,
            "creative_solutions": result.creative_solutions,
            "design_frameworks": result.design_frameworks,
            "implementation_roadmap": result.implementation_roadmap
        }
        
        return ThinkTankResult(
            phase=IntegrationPhase.INNOVATION,
            result=result,
            status=IntegrationStatus.COMPLETED,
            processing_time=processing_time,
            confidence_score=result.confidence_score,
            key_insights=key_insights,
            next_phase_inputs=next_phase_inputs
        )
    
    async def _conduct_resource_phase(self, innovation_result: ThinkTankResult) -> ThinkTankResult:
        """Conduct the Verdant Expanse phase (Green Tortoise)"""
        start_time = datetime.utcnow()
        
        think_tank = self.think_tanks[IntegrationPhase.RESOURCES]
        
        # Extract inputs from innovation phase
        core_principles = innovation_result.next_phase_inputs["core_principles"]
        strategic_frameworks = innovation_result.next_phase_inputs["strategic_frameworks"]
        creative_solutions = innovation_result.next_phase_inputs["creative_solutions"]
        
        # Define available resources
        available_resources = {
            ResourceType.HUMAN_CAPITAL: 100,
            ResourceType.FINANCIAL: 1000000,
            ResourceType.TECHNOLOGICAL: 100,
            ResourceType.TIME: 18
        }
        
        # Conduct resource inquiry
        result = await think_tank.conduct_resource_inquiry(
            problem_statement=innovation_result.result.problem_statement,
            core_principles=core_principles,
            strategic_frameworks=strategic_frameworks,
            creative_solutions=creative_solutions,
            available_resources=available_resources,
            constraints={"budget": "moderate", "timeline": "18 months"},
            timeline_requirements={"launch": "12 months", "scaling": "18 months"}
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Extract key insights and prepare inputs for next phase
        key_insights = [
            f"Resource analysis completed: {len(result.resource_analysis)}",
            f"Allocation plan created: {len(result.allocation_plan)}",
            f"Timeline framework established: {len(result.timeline_framework)}",
            f"Monte Carlo simulations run: {len(result.monte_carlo_simulations)}"
        ]
        
        next_phase_inputs = {
            "core_principles": core_principles,
            "strategic_frameworks": strategic_frameworks,
            "creative_solutions": creative_solutions,
            "resource_allocations": result.allocation_plan,
            "timeline_framework": result.timeline_framework
        }
        
        return ThinkTankResult(
            phase=IntegrationPhase.RESOURCES,
            result=result,
            status=IntegrationStatus.COMPLETED,
            processing_time=processing_time,
            confidence_score=result.confidence_score,
            key_insights=key_insights,
            next_phase_inputs=next_phase_inputs
        )
    
    async def _conduct_communication_phase(self, resource_result: ThinkTankResult) -> ThinkTankResult:
        """Conduct the Market of Echoes phase (Blue Dolphin)"""
        start_time = datetime.utcnow()
        
        think_tank = self.think_tanks[IntegrationPhase.COMMUNICATION]
        
        # Extract inputs from resource phase
        core_principles = resource_result.next_phase_inputs["core_principles"]
        strategic_frameworks = resource_result.next_phase_inputs["strategic_frameworks"]
        creative_solutions = resource_result.next_phase_inputs["creative_solutions"]
        resource_allocations = resource_result.next_phase_inputs["resource_allocations"]
        
        # Conduct communication inquiry
        result = await think_tank.conduct_communication_inquiry(
            problem_statement=resource_result.result.problem_statement,
            core_principles=core_principles,
            strategic_frameworks=strategic_frameworks,
            creative_solutions=creative_solutions,
            resource_allocations=resource_allocations,
            target_markets=["early adopters", "mainstream", "enterprise"],
            stakeholder_groups=["end users", "decision makers", "influencers", "partners"]
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Extract key insights and prepare inputs for next phase
        key_insights = [
            f"Communication analysis completed: {len(result.communication_analysis)}",
            f"Market engagement strategies developed: {len(result.market_engagement_strategies)}",
            f"Audience analysis completed: {len(result.audience_analysis)}",
            f"Message frameworks created: {len(result.message_frameworks)}"
        ]
        
        next_phase_inputs = {
            "core_principles": core_principles,
            "strategic_frameworks": strategic_frameworks,
            "creative_solutions": creative_solutions,
            "resource_allocations": resource_allocations,
            "communication_strategies": result.market_engagement_strategies,
            "audience_analysis": result.audience_analysis
        }
        
        return ThinkTankResult(
            phase=IntegrationPhase.COMMUNICATION,
            result=result,
            status=IntegrationStatus.COMPLETED,
            processing_time=processing_time,
            confidence_score=result.confidence_score,
            key_insights=key_insights,
            next_phase_inputs=next_phase_inputs
        )
    
    async def _conduct_reflection_phase(self, communication_result: ThinkTankResult) -> ThinkTankResult:
        """Conduct the Third Eye phase (Purple Elephant)"""
        start_time = datetime.utcnow()
        
        think_tank = self.think_tanks[IntegrationPhase.REFLECTION]
        
        # Extract inputs from communication phase
        core_principles = communication_result.next_phase_inputs["core_principles"]
        strategic_frameworks = communication_result.next_phase_inputs["strategic_frameworks"]
        creative_solutions = communication_result.next_phase_inputs["creative_solutions"]
        resource_allocations = communication_result.next_phase_inputs["resource_allocations"]
        communication_strategies = communication_result.next_phase_inputs["communication_strategies"]
        
        # Simulate stakeholder feedback
        stakeholder_feedback = {
            "end_users": {"satisfaction": 0.85, "feedback": "Very positive"},
            "decision_makers": {"satisfaction": 0.80, "feedback": "Good progress"},
            "partners": {"satisfaction": 0.90, "feedback": "Excellent collaboration"}
        }
        
        # Conduct reflection inquiry
        result = await think_tank.conduct_reflection_inquiry(
            problem_statement=communication_result.result.problem_statement,
            core_principles=core_principles,
            strategic_frameworks=strategic_frameworks,
            creative_solutions=creative_solutions,
            resource_allocations=resource_allocations,
            communication_strategies=communication_strategies,
            stakeholder_feedback=stakeholder_feedback,
            reflection_depth=ReflectionDepth.DEEP
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Extract key insights and prepare inputs for synthesis
        key_insights = [
            f"Reflection analysis completed: {len(result.reflection_analysis)}",
            f"Empathy assessment completed: {len(result.empathy_assessment)}",
            f"Ethical alignment evaluated: {len(result.ethical_alignment)}",
            f"Feedback systems created: {len(result.feedback_systems)}"
        ]
        
        next_phase_inputs = {
            "core_principles": core_principles,
            "reflection_analysis": result.reflection_analysis,
            "empathy_assessment": result.empathy_assessment,
            "ethical_alignment": result.ethical_alignment,
            "wisdom_synthesis": result.wisdom_synthesis
        }
        
        return ThinkTankResult(
            phase=IntegrationPhase.REFLECTION,
            result=result,
            status=IntegrationStatus.COMPLETED,
            processing_time=processing_time,
            confidence_score=result.confidence_score,
            key_insights=key_insights,
            next_phase_inputs=next_phase_inputs
        )
    
    async def _conduct_integration_synthesis(self, cycle: IntegrationCycle) -> Dict[str, Any]:
        """Conduct the final integration synthesis"""
        synthesis = {
            "cycle_summary": {
                "cycle_id": cycle.id,
                "cycle_number": cycle.cycle_number,
                "problem_statement": cycle.problem_statement,
                "total_processing_time": cycle.total_processing_time,
                "overall_confidence": cycle.overall_confidence
            },
            
            "phase_summaries": {},
            "integrated_insights": [],
            "actionable_recommendations": [],
            "next_cycle_questions": [],
            "wisdom_principles": []
        }
        
        # Summarize each phase
        for phase, result in cycle.think_tank_results.items():
            synthesis["phase_summaries"][phase.value] = {
                "status": result.status.value,
                "processing_time": result.processing_time,
                "confidence_score": result.confidence_score,
                "key_insights": result.key_insights
            }
        
        # Extract integrated insights from all phases
        for phase, result in cycle.think_tank_results.items():
            synthesis["integrated_insights"].extend(result.key_insights)
        
        # Generate actionable recommendations
        synthesis["actionable_recommendations"] = [
            "Implement the strategic frameworks developed by the Orange Orangutan",
            "Deploy the creative solutions designed by the Yellow Honeybee",
            "Execute the resource allocation plan created by the Green Tortoise",
            "Launch the communication strategies developed by the Blue Dolphin",
            "Establish the feedback systems recommended by the Purple Elephant"
        ]
        
        # Generate next cycle questions
        synthesis["next_cycle_questions"] = [
            "How can we measure the effectiveness of our integrated approach?",
            "What adaptations are needed based on initial implementation results?",
            "How can we scale our solutions to reach broader impact?",
            "What new challenges and opportunities have emerged?",
            "How can we deepen our wisdom and understanding through continued cycles?"
        ]
        
        # Extract wisdom principles
        synthesis["wisdom_principles"] = [
            "Seek truth through multiple perspectives and cultural wisdom",
            "Translate principles into actionable strategies and plans",
            "Innovate through creative design and interdisciplinary thinking",
            "Allocate resources wisely with sustainability and efficiency",
            "Communicate with clarity, empathy, and emotional resonance",
            "Reflect continuously with empathy and ethical alignment"
        ]
        
        return synthesis
    
    def _calculate_overall_confidence(self, think_tank_results: Dict[IntegrationPhase, ThinkTankResult]) -> float:
        """Calculate overall confidence score from all Think Tank results"""
        if not think_tank_results:
            return 0.0
        
        total_confidence = sum(result.confidence_score for result in think_tank_results.values())
        return total_confidence / len(think_tank_results)
    
    async def conduct_multiple_cycles(self, problem_statement: str, 
                                    num_cycles: int = 3,
                                    initial_context: Dict[str, Any] = None) -> List[IntegrationCycle]:
        """Conduct multiple integration cycles for deeper understanding"""
        cycles = []
        
        for cycle_num in range(1, num_cycles + 1):
            logger.info(f"🔄 Starting Integration Cycle {cycle_num} of {num_cycles}")
            
            # Use insights from previous cycle as context for next cycle
            context = initial_context or {}
            if cycles:
                previous_cycle = cycles[-1]
                context["previous_insights"] = previous_cycle.integration_synthesis.get("integrated_insights", [])
                context["previous_recommendations"] = previous_cycle.integration_synthesis.get("actionable_recommendations", [])
            
            cycle = await self.conduct_integrated_inquiry(
                problem_statement=problem_statement,
                initial_context=context,
                cycle_number=cycle_num
            )
            
            cycles.append(cycle)
            
            logger.info(f"🔄 Completed Integration Cycle {cycle_num}")
            logger.info(f"Overall Confidence: {cycle.overall_confidence:.2f}")
        
        return cycles
    
    def get_integration_history(self) -> List[IntegrationCycle]:
        """Get the history of all integration cycles"""
        return self.integration_history
    
    def get_cycle_summary(self, cycle_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a specific integration cycle"""
        for cycle in self.integration_history:
            if cycle.id == cycle_id:
                return {
                    "cycle_id": cycle.id,
                    "cycle_number": cycle.cycle_number,
                    "problem_statement": cycle.problem_statement,
                    "status": cycle.status.value,
                    "overall_confidence": cycle.overall_confidence,
                    "total_processing_time": cycle.total_processing_time,
                    "phase_count": len(cycle.think_tank_results),
                    "created_at": cycle.created_at.isoformat(),
                    "completed_at": cycle.completed_at.isoformat() if cycle.completed_at else None
                }
        return None

# Example usage and testing
async def demo_think_tank_integration():
    """Demonstrate the Cosmic Council Think Tank Integration System"""
    print("🔄 Cosmic Council Think Tank Integration System Demo")
    print("=" * 70)
    
    integration_system = CosmicCouncilThinkTankIntegration()
    
    # Example problem
    problem = "How can we create a more sustainable and equitable economic system?"
    
    # Conduct single integration cycle
    print(f"\n🔄 Conducting Single Integration Cycle")
    print(f"Problem: {problem}")
    
    cycle = await integration_system.conduct_integrated_inquiry(
        problem_statement=problem,
        initial_context={"domain": "economic_systems", "complexity": "systemic"},
        cycle_number=1
    )
    
    print(f"\n🔄 Integration Cycle Results:")
    print(f"Cycle ID: {cycle.id}")
    print(f"Status: {cycle.status.value}")
    print(f"Overall Confidence: {cycle.overall_confidence:.2f}")
    print(f"Total Processing Time: {cycle.total_processing_time:.2f}s")
    
    print(f"\n📊 Phase Results:")
    for phase, result in cycle.think_tank_results.items():
        print(f"  {phase.value}: {result.status.value} ({result.confidence_score:.2f})")
    
    print(f"\n🎯 Key Insights:")
    for insight in cycle.integration_synthesis["integrated_insights"][:5]:
        print(f"  • {insight}")
    
    print(f"\n📋 Actionable Recommendations:")
    for recommendation in cycle.integration_synthesis["actionable_recommendations"]:
        print(f"  • {recommendation}")
    
    print(f"\n❓ Next Cycle Questions:")
    for question in cycle.integration_synthesis["next_cycle_questions"]:
        print(f"  • {question}")
    
    # Conduct multiple cycles
    print(f"\n🔄 Conducting Multiple Integration Cycles")
    cycles = await integration_system.conduct_multiple_cycles(
        problem_statement=problem,
        num_cycles=2,
        initial_context={"domain": "economic_systems", "complexity": "systemic"}
    )
    
    print(f"\n📈 Multiple Cycles Summary:")
    for i, cycle in enumerate(cycles, 1):
        print(f"  Cycle {i}: Confidence {cycle.overall_confidence:.2f}, Time {cycle.total_processing_time:.2f}s")
    
    print(f"\n🔄 Integration System Demo Completed")

if __name__ == "__main__":
    asyncio.run(demo_think_tank_integration())
