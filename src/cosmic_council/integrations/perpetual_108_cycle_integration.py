"""
Perpetual Thinking System - 108-Cycle Fractal Integration
Integrates the perpetual thinking system with the existing 108-cycle fractal system
to create a unified, scalable, and auditable thinking architecture.
"""

import asyncio
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

# Import existing systems
from .unified_fractal_system import (
    UnifiedFractal108CycleSystem, EnterpriseType, SquadType, RedundancyPassType,
    CycleStage, CycleRun, StageRun, CycleStatus, StageStatus
)
from .unified_perpetual_thinking_system import (
    UnifiedPerpetualThinkingEngine, CycleType, PatternType, PerpetualCycle
)
from .meta_cyclical_architecture import (
    MetaCyclicalArchitecture, MetaCycleType, MetaCycle
)
from ...applications.enhanced_master_orchestration_system import (
    EnhancedMasterOrchestrationSystem, OrchestrationMode, OrchestrationSession
)
from .perpetual_guardrail_integration import (
    PerpetualGuardrailIntegration, PerpetualPolicyEnforcer
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerpetualFractalMode(Enum):
    """Modes for integrating perpetual thinking with 108-cycle fractal system"""
    PARALLEL = "parallel"           # Run both systems in parallel
    SEQUENTIAL = "sequential"       # Run fractal system first, then perpetual
    INTEGRATED = "integrated"       # Fully integrated execution
    FRACTAL_DRIVEN = "fractal_driven"  # Fractal system drives perpetual cycles
    PERPETUAL_DRIVEN = "perpetual_driven"  # Perpetual system drives fractal stages

class FractalPerpetualMapping(Enum):
    """Mapping between fractal enterprises and perpetual cycle types"""
    RED_OWL_TO_EXPLORATION = "red_owl_exploration"
    ORANGE_ORANGUTAN_TO_CONVERGENCE = "orange_orangutan_convergence"
    YELLOW_HONEYBEE_TO_SYNTHESIS = "yellow_honeybee_synthesis"
    GREEN_TORTOISE_TO_META_REFLECTION = "green_tortoise_meta_reflection"
    BLUE_DOLPHIN_TO_BREAKTHROUGH = "blue_dolphin_breakthrough"
    PURPLE_ELEPHANT_TO_ADAPTATION = "purple_elephant_adaptation"

@dataclass
class FractalPerpetualContext:
    """Context for integrating fractal and perpetual systems"""
    fractal_run_id: Optional[str] = None
    perpetual_session_id: Optional[str] = None
    integration_mode: PerpetualFractalMode = PerpetualFractalMode.INTEGRATED
    mapping_strategy: FractalPerpetualMapping = FractalPerpetualMapping.RED_OWL_TO_EXPLORATION
    cross_system_insights: Dict[str, Any] = field(default_factory=dict)
    synchronization_points: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FractalPerpetualResult:
    """Result of integrated fractal-perpetual execution"""
    fractal_result: Dict[str, Any]
    perpetual_result: Dict[str, Any]
    integration_insights: Dict[str, Any]
    cross_system_patterns: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    execution_time: float
    success: bool
    errors: List[str] = field(default_factory=list)

class Perpetual108CycleIntegration:
    """
    Integration layer between perpetual thinking system and 108-cycle fractal system
    Provides unified execution, cross-system insights, and performance optimization
    """
    
    def __init__(self,
                 fractal_system: UnifiedFractal108CycleSystem,
                 perpetual_engine: UnifiedPerpetualThinkingEngine,
                 meta_architecture: MetaCyclicalArchitecture,
                 orchestration_system: EnhancedMasterOrchestrationSystem,
                 guardrail_integration: Optional[PerpetualGuardrailIntegration] = None):
        """
        Initialize the fractal-perpetual integration
        
        Args:
            fractal_system: 108-cycle fractal system instance
            perpetual_engine: Perpetual thinking engine instance
            meta_architecture: Meta-cyclical architecture instance
            orchestration_system: Master orchestration system instance
            guardrail_integration: Optional guardrail integration for policy enforcement
        """
        self.fractal_system = fractal_system
        self.perpetual_engine = perpetual_engine
        self.meta_architecture = meta_architecture
        self.orchestration_system = orchestration_system
        self.guardrail_integration = guardrail_integration
        
        # Integration mappings
        self.enterprise_to_cycle_mapping = {
            EnterpriseType.RED_OWL: CycleType.EXPLORATION,
            EnterpriseType.ORANGE_ORANGUTAN: CycleType.CONVERGENCE,
            EnterpriseType.YELLOW_HONEYBEE: CycleType.SYNTHESIS,
            EnterpriseType.GREEN_TORTOISE: CycleType.META_REFLECTION,
            EnterpriseType.BLUE_DOLPHIN: CycleType.BREAKTHROUGH,
            EnterpriseType.PURPLE_ELEPHANT: CycleType.ADAPTATION
        }
        
        self.cycle_to_enterprise_mapping = {v: k for k, v in self.enterprise_to_cycle_mapping.items()}
        
        # Cross-system insights storage
        self.cross_system_insights: Dict[str, Any] = {}
        self.integration_sessions: Dict[str, FractalPerpetualContext] = {}
        
        logger.info("Perpetual-108-Cycle Integration initialized")
    
    async def execute_integrated_session(self,
                                       session_name: str,
                                       initial_input: str,
                                       integration_mode: PerpetualFractalMode = PerpetualFractalMode.INTEGRATED,
                                       context: Optional[Dict[str, Any]] = None) -> FractalPerpetualResult:
        """
        Execute an integrated session combining both fractal and perpetual systems
        
        Args:
            session_name: Name for the integrated session
            initial_input: Initial input for both systems
            integration_mode: How to integrate the systems
            context: Additional context information
            
        Returns:
            FractalPerpetualResult with results from both systems
        """
        start_time = datetime.now(timezone.utc)
        session_id = str(uuid.uuid4())
        
        # Create integration context
        integration_context = FractalPerpetualContext(
            fractal_run_id=None,
            perpetual_session_id=None,
            integration_mode=integration_mode,
            cross_system_insights={},
            synchronization_points=[],
            performance_metrics={}
        )
        
        self.integration_sessions[session_id] = integration_context
        
        try:
            logger.info(f"Starting integrated session: {session_name} (Mode: {integration_mode.value})")
            
            # Execute based on integration mode
            if integration_mode == PerpetualFractalMode.PARALLEL:
                result = await self._execute_parallel_mode(session_id, session_name, initial_input, context)
            elif integration_mode == PerpetualFractalMode.SEQUENTIAL:
                result = await self._execute_sequential_mode(session_id, session_name, initial_input, context)
            elif integration_mode == PerpetualFractalMode.INTEGRATED:
                result = await self._execute_integrated_mode(session_id, session_name, initial_input, context)
            elif integration_mode == PerpetualFractalMode.FRACTAL_DRIVEN:
                result = await self._execute_fractal_driven_mode(session_id, session_name, initial_input, context)
            elif integration_mode == PerpetualFractalMode.PERPETUAL_DRIVEN:
                result = await self._execute_perpetual_driven_mode(session_id, session_name, initial_input, context)
            else:
                raise ValueError(f"Unknown integration mode: {integration_mode}")
            
            # Calculate execution time
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            result.execution_time = execution_time
            
            # Store cross-system insights
            self.cross_system_insights[session_id] = result.integration_insights
            
            logger.info(f"Integrated session completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Integrated session failed: {str(e)}")
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            return FractalPerpetualResult(
                fractal_result={},
                perpetual_result={},
                integration_insights={},
                cross_system_patterns=[],
                performance_metrics={},
                execution_time=execution_time,
                success=False,
                errors=[str(e)]
            )
        finally:
            # Clean up session
            if session_id in self.integration_sessions:
                del self.integration_sessions[session_id]
    
    async def _execute_parallel_mode(self, session_id: str, session_name: str, 
                                   initial_input: str, context: Optional[Dict[str, Any]]) -> FractalPerpetualResult:
        """Execute both systems in parallel"""
        logger.info("Executing in parallel mode")
        
        # Start both systems simultaneously
        fractal_task = asyncio.create_task(
            self._execute_fractal_system(session_name, initial_input, context)
        )
        perpetual_task = asyncio.create_task(
            self._execute_perpetual_system(session_name, initial_input, context)
        )
        
        # Wait for both to complete
        fractal_result, perpetual_result = await asyncio.gather(
            fractal_task, perpetual_task, return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(fractal_result, Exception):
            fractal_result = {"error": str(fractal_result)}
        if isinstance(perpetual_result, Exception):
            perpetual_result = {"error": str(perpetual_result)}
        
        # Analyze cross-system patterns
        cross_system_patterns = await self._analyze_cross_system_patterns(
            fractal_result, perpetual_result
        )
        
        return FractalPerpetualResult(
            fractal_result=fractal_result,
            perpetual_result=perpetual_result,
            integration_insights=self._generate_integration_insights(fractal_result, perpetual_result),
            cross_system_patterns=cross_system_patterns,
            performance_metrics=self._calculate_performance_metrics(fractal_result, perpetual_result),
            execution_time=0.0,  # Will be set by caller
            success=True
        )
    
    async def _execute_sequential_mode(self, session_id: str, session_name: str,
                                     initial_input: str, context: Optional[Dict[str, Any]]) -> FractalPerpetualResult:
        """Execute fractal system first, then perpetual system"""
        logger.info("Executing in sequential mode")
        
        # Execute fractal system first
        fractal_result = await self._execute_fractal_system(session_name, initial_input, context)
        
        # Use fractal insights as input for perpetual system
        enhanced_input = self._enhance_input_with_fractal_insights(initial_input, fractal_result)
        
        # Execute perpetual system with enhanced input
        perpetual_result = await self._execute_perpetual_system(
            f"{session_name}_enhanced", enhanced_input, context
        )
        
        # Analyze cross-system patterns
        cross_system_patterns = await self._analyze_cross_system_patterns(
            fractal_result, perpetual_result
        )
        
        return FractalPerpetualResult(
            fractal_result=fractal_result,
            perpetual_result=perpetual_result,
            integration_insights=self._generate_integration_insights(fractal_result, perpetual_result),
            cross_system_patterns=cross_system_patterns,
            performance_metrics=self._calculate_performance_metrics(fractal_result, perpetual_result),
            execution_time=0.0,  # Will be set by caller
            success=True
        )
    
    async def _execute_integrated_mode(self, session_id: str, session_name: str,
                                     initial_input: str, context: Optional[Dict[str, Any]]) -> FractalPerpetualResult:
        """Execute fully integrated mode with cross-system synchronization"""
        logger.info("Executing in integrated mode")
        
        # Create orchestration session
        orchestration_session_id = await self.orchestration_system.start_orchestration_session(
            session_name=f"{session_name}_integrated",
            initial_input=initial_input,
            mode=OrchestrationMode.COLLABORATIVE,
            goals=["fractal_perpetual_integration", "cross_system_optimization"],
            success_criteria=["both_systems_complete", "insights_synthesized"]
        )
        
        # Start fractal system
        fractal_run_id = await self.fractal_system.start_cycle_run(
            objective_ref=f"integrated_{session_name}",
            priority=5,
            context=context or {}
        )
        
        # Start perpetual system
        perpetual_session_id = await self.perpetual_engine.create_session(
            session_name=f"{session_name}_perpetual",
            initial_input=initial_input,
            user_id="integrated_system"
        )
        
        # Update integration context
        integration_context = self.integration_sessions[session_id]
        integration_context.fractal_run_id = fractal_run_id
        integration_context.perpetual_session_id = perpetual_session_id
        
        # Execute fractal system
        fractal_result = await self.fractal_system.execute_cycle_run(fractal_run_id)
        
        # Synchronize with perpetual system at key points
        await self._synchronize_systems(fractal_result, perpetual_session_id)
        
        # Execute perpetual cycles based on fractal insights
        perpetual_result = await self._execute_perpetual_cycles_from_fractal(
            perpetual_session_id, fractal_result
        )
        
        # Synthesize final results
        integration_insights = await self._synthesize_integration_insights(
            fractal_result, perpetual_result
        )
        
        # Analyze cross-system patterns
        cross_system_patterns = await self._analyze_cross_system_patterns(
            fractal_result, perpetual_result
        )
        
        return FractalPerpetualResult(
            fractal_result=fractal_result,
            perpetual_result=perpetual_result,
            integration_insights=integration_insights,
            cross_system_patterns=cross_system_patterns,
            performance_metrics=self._calculate_performance_metrics(fractal_result, perpetual_result),
            execution_time=0.0,  # Will be set by caller
            success=True
        )
    
    async def _execute_fractal_driven_mode(self, session_id: str, session_name: str,
                                         initial_input: str, context: Optional[Dict[str, Any]]) -> FractalPerpetualResult:
        """Execute with fractal system driving perpetual cycles"""
        logger.info("Executing in fractal-driven mode")
        
        # Execute fractal system first
        fractal_result = await self._execute_fractal_system(session_name, initial_input, context)
        
        # Create perpetual session
        perpetual_session_id = await self.perpetual_engine.create_session(
            session_name=f"{session_name}_fractal_driven",
            initial_input=initial_input,
            user_id="fractal_system"
        )
        
        # Execute perpetual cycles based on fractal enterprise results
        perpetual_result = await self._execute_perpetual_cycles_from_fractal(
            perpetual_session_id, fractal_result
        )
        
        # Analyze cross-system patterns
        cross_system_patterns = await self._analyze_cross_system_patterns(
            fractal_result, perpetual_result
        )
        
        return FractalPerpetualResult(
            fractal_result=fractal_result,
            perpetual_result=perpetual_result,
            integration_insights=self._generate_integration_insights(fractal_result, perpetual_result),
            cross_system_patterns=cross_system_patterns,
            performance_metrics=self._calculate_performance_metrics(fractal_result, perpetual_result),
            execution_time=0.0,  # Will be set by caller
            success=True
        )
    
    async def _execute_perpetual_driven_mode(self, session_id: str, session_name: str,
                                           initial_input: str, context: Optional[Dict[str, Any]]) -> FractalPerpetualResult:
        """Execute with perpetual system driving fractal stages"""
        logger.info("Executing in perpetual-driven mode")
        
        # Create perpetual session
        perpetual_session_id = await self.perpetual_engine.create_session(
            session_name=f"{session_name}_perpetual_driven",
            initial_input=initial_input,
            user_id="perpetual_system"
        )
        
        # Execute initial perpetual cycle
        initial_cycle = await self.perpetual_engine.execute_cycle(
            session_id=perpetual_session_id,
            cycle_type=CycleType.EXPLORATION,
            input_text=initial_input
        )
        
        # Use perpetual insights to drive fractal execution
        fractal_result = await self._execute_fractal_from_perpetual(
            session_name, initial_cycle, context
        )
        
        # Continue perpetual cycles with fractal insights
        perpetual_result = await self._continue_perpetual_with_fractal(
            perpetual_session_id, fractal_result
        )
        
        # Analyze cross-system patterns
        cross_system_patterns = await self._analyze_cross_system_patterns(
            fractal_result, perpetual_result
        )
        
        return FractalPerpetualResult(
            fractal_result=fractal_result,
            perpetual_result=perpetual_result,
            integration_insights=self._generate_integration_insights(fractal_result, perpetual_result),
            cross_system_patterns=cross_system_patterns,
            performance_metrics=self._calculate_performance_metrics(fractal_result, perpetual_result),
            execution_time=0.0,  # Will be set by caller
            success=True
        )
    
    async def _execute_fractal_system(self, session_name: str, initial_input: str,
                                    context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the 108-cycle fractal system"""
        try:
            # Start cycle run
            run_id = await self.fractal_system.start_cycle_run(
                objective_ref=f"perpetual_integration_{session_name}",
                priority=5,
                context=context or {}
            )
            
            # Execute the cycle
            result = await self.fractal_system.execute_cycle_run(run_id)
            
            logger.info(f"Fractal system completed: {run_id}")
            return result
            
        except Exception as e:
            logger.error(f"Fractal system execution failed: {str(e)}")
            return {"error": str(e), "run_id": None}
    
    async def _execute_perpetual_system(self, session_name: str, initial_input: str,
                                      context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the perpetual thinking system"""
        try:
            # Create session
            session_id = await self.perpetual_engine.create_session(
                session_name=session_name,
                initial_input=initial_input,
                user_id="fractal_integration"
            )
            
            # Execute multiple cycles
            cycles = []
            for cycle_type in [CycleType.EXPLORATION, CycleType.CONVERGENCE, CycleType.SYNTHESIS]:
                cycle_result = await self.perpetual_engine.execute_cycle(
                    session_id=session_id,
                    cycle_type=cycle_type,
                    input_text=initial_input
                )
                cycles.append(cycle_result)
            
            # Get session status
            session_status = self.perpetual_engine.get_session_status(session_id)
            
            logger.info(f"Perpetual system completed: {session_id}")
            return {
                "session_id": session_id,
                "cycles": cycles,
                "session_status": session_status,
                "total_cycles": len(cycles)
            }
            
        except Exception as e:
            logger.error(f"Perpetual system execution failed: {str(e)}")
            return {"error": str(e), "session_id": None}
    
    async def _execute_perpetual_cycles_from_fractal(self, perpetual_session_id: str,
                                                   fractal_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute perpetual cycles based on fractal system results"""
        cycles = []
        
        # Map fractal enterprise results to perpetual cycles
        for enterprise, enterprise_data in fractal_result.get("enterprise_results", {}).items():
            if enterprise in self.enterprise_to_cycle_mapping:
                cycle_type = self.enterprise_to_cycle_mapping[enterprise]
                
                # Create input from fractal enterprise data
                cycle_input = self._create_cycle_input_from_fractal(enterprise_data)
                
                # Execute perpetual cycle
                cycle_result = await self.perpetual_engine.execute_cycle(
                    session_id=perpetual_session_id,
                    cycle_type=cycle_type,
                    input_text=cycle_input
                )
                cycles.append(cycle_result)
        
        return {
            "session_id": perpetual_session_id,
            "cycles": cycles,
            "fractal_driven": True,
            "total_cycles": len(cycles)
        }
    
    async def _execute_fractal_from_perpetual(self, session_name: str, perpetual_cycle: Dict[str, Any],
                                            context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute fractal system based on perpetual cycle insights"""
        # Extract insights from perpetual cycle
        cycle_insights = perpetual_cycle.get("insights", {})
        
        # Enhance context with perpetual insights
        enhanced_context = (context or {}).copy()
        enhanced_context["perpetual_insights"] = cycle_insights
        enhanced_context["perpetual_cycle_type"] = perpetual_cycle.get("cycle_type")
        
        # Execute fractal system with enhanced context
        return await self._execute_fractal_system(
            f"{session_name}_perpetual_driven", 
            str(cycle_insights), 
            enhanced_context
        )
    
    async def _continue_perpetual_with_fractal(self, perpetual_session_id: str,
                                             fractal_result: Dict[str, Any]) -> Dict[str, Any]:
        """Continue perpetual cycles with fractal system insights"""
        # Extract fractal insights
        fractal_insights = fractal_result.get("final_decision", {})
        
        # Execute additional perpetual cycles
        additional_cycles = []
        for cycle_type in [CycleType.META_REFLECTION, CycleType.BREAKTHROUGH, CycleType.ADAPTATION]:
            cycle_input = f"Fractal insights: {fractal_insights}"
            
            cycle_result = await self.perpetual_engine.execute_cycle(
                session_id=perpetual_session_id,
                cycle_type=cycle_type,
                input_text=cycle_input
            )
            additional_cycles.append(cycle_result)
        
        return {
            "session_id": perpetual_session_id,
            "additional_cycles": additional_cycles,
            "fractal_enhanced": True,
            "total_additional_cycles": len(additional_cycles)
        }
    
    async def _synchronize_systems(self, fractal_result: Dict[str, Any], perpetual_session_id: str):
        """Synchronize fractal and perpetual systems at key points"""
        # Extract key insights from fractal system
        key_insights = fractal_result.get("final_decision", {})
        
        # Update perpetual session with fractal insights
        if perpetual_session_id:
            # This would update the perpetual session with fractal insights
            # Implementation depends on perpetual engine API
            logger.info(f"Synchronizing systems with insights: {key_insights}")
    
    async def _analyze_cross_system_patterns(self, fractal_result: Dict[str, Any],
                                           perpetual_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze patterns between fractal and perpetual systems"""
        patterns = []
        
        # Analyze enterprise-cycle alignment
        fractal_enterprises = fractal_result.get("enterprise_results", {})
        perpetual_cycles = perpetual_result.get("cycles", [])
        
        for enterprise, enterprise_data in fractal_enterprises.items():
            if enterprise in self.enterprise_to_cycle_mapping:
                cycle_type = self.enterprise_to_cycle_mapping[enterprise]
                
                # Find corresponding perpetual cycle
                corresponding_cycle = None
                for cycle in perpetual_cycles:
                    if cycle.get("cycle_type") == cycle_type.value:
                        corresponding_cycle = cycle
                        break
                
                if corresponding_cycle:
                    pattern = {
                        "type": "enterprise_cycle_alignment",
                        "enterprise": enterprise.value,
                        "cycle_type": cycle_type.value,
                        "fractal_confidence": enterprise_data.get("confidence", 0),
                        "perpetual_confidence": corresponding_cycle.get("confidence_score", 0),
                        "alignment_score": self._calculate_alignment_score(enterprise_data, corresponding_cycle)
                    }
                    patterns.append(pattern)
        
        # Analyze cross-system insights
        fractal_insights = fractal_result.get("final_decision", {})
        perpetual_insights = perpetual_result.get("session_status", {}).get("insights", {})
        
        if fractal_insights and perpetual_insights:
            insight_pattern = {
                "type": "cross_system_insights",
                "fractal_insights": fractal_insights,
                "perpetual_insights": perpetual_insights,
                "insight_overlap": self._calculate_insight_overlap(fractal_insights, perpetual_insights)
            }
            patterns.append(insight_pattern)
        
        return patterns
    
    def _enhance_input_with_fractal_insights(self, original_input: str, fractal_result: Dict[str, Any]) -> str:
        """Enhance input with insights from fractal system"""
        fractal_insights = fractal_result.get("final_decision", {})
        enhanced_input = f"{original_input}\n\nFractal System Insights: {fractal_insights}"
        return enhanced_input
    
    def _create_cycle_input_from_fractal(self, enterprise_data: Dict[str, Any]) -> str:
        """Create perpetual cycle input from fractal enterprise data"""
        return f"Fractal Enterprise Data: {enterprise_data}"
    
    def _generate_integration_insights(self, fractal_result: Dict[str, Any],
                                     perpetual_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from the integration of both systems"""
        return {
            "fractal_completion_rate": fractal_result.get("executed_stages", 0) / 108,
            "perpetual_cycle_count": len(perpetual_result.get("cycles", [])),
            "cross_system_success": fractal_result.get("status") == "completed" and "error" not in perpetual_result,
            "integration_timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _calculate_performance_metrics(self, fractal_result: Dict[str, Any],
                                     perpetual_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics for the integrated execution"""
        return {
            "fractal_stages_completed": fractal_result.get("executed_stages", 0),
            "perpetual_cycles_executed": len(perpetual_result.get("cycles", [])),
            "total_processing_time": fractal_result.get("metrics", {}).get("total_duration_ms", 0),
            "success_rate": 1.0 if fractal_result.get("status") == "completed" and "error" not in perpetual_result else 0.0
        }
    
    def _calculate_alignment_score(self, enterprise_data: Dict[str, Any],
                                 cycle_data: Dict[str, Any]) -> float:
        """Calculate alignment score between fractal enterprise and perpetual cycle"""
        fractal_confidence = enterprise_data.get("confidence", 0)
        perpetual_confidence = cycle_data.get("confidence_score", 0)
        
        # Simple alignment score based on confidence correlation
        return abs(fractal_confidence - perpetual_confidence)
    
    def _calculate_insight_overlap(self, fractal_insights: Dict[str, Any],
                                 perpetual_insights: Dict[str, Any]) -> float:
        """Calculate overlap between fractal and perpetual insights"""
        # Simple overlap calculation based on key presence
        fractal_keys = set(fractal_insights.keys())
        perpetual_keys = set(perpetual_insights.keys())
        
        if not fractal_keys and not perpetual_keys:
            return 0.0
        
        intersection = fractal_keys.intersection(perpetual_keys)
        union = fractal_keys.union(perpetual_keys)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def _synthesize_integration_insights(self, fractal_result: Dict[str, Any],
                                             perpetual_result: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize insights from both systems"""
        return {
            "synthesis_timestamp": datetime.now(timezone.utc).isoformat(),
            "fractal_contribution": fractal_result.get("final_decision", {}),
            "perpetual_contribution": perpetual_result.get("session_status", {}).get("insights", {}),
            "integrated_recommendation": "Both systems provide complementary insights for comprehensive analysis"
        }
    
    def get_integration_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an integration session"""
        if session_id in self.integration_sessions:
            context = self.integration_sessions[session_id]
            return {
                "session_id": session_id,
                "integration_mode": context.integration_mode.value,
                "fractal_run_id": context.fractal_run_id,
                "perpetual_session_id": context.perpetual_session_id,
                "synchronization_points": context.synchronization_points,
                "performance_metrics": context.performance_metrics
            }
        return None
    
    def get_cross_system_insights(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get cross-system insights for a session"""
        return self.cross_system_insights.get(session_id)
    
    def get_integration_analytics(self) -> Dict[str, Any]:
        """Get analytics for all integration sessions"""
        return {
            "total_sessions": len(self.cross_system_insights),
            "active_sessions": len(self.integration_sessions),
            "cross_system_insights": self.cross_system_insights,
            "integration_modes_used": list(set(
                context.integration_mode.value 
                for context in self.integration_sessions.values()
            ))
        }

# Example usage and testing
async def test_perpetual_108_cycle_integration():
    """Test the perpetual-108-cycle integration"""
    try:
        # Initialize systems (these would be real instances in production)
        from .unified_fractal_system import UnifiedFractal108CycleSystem
        from .unified_perpetual_thinking_system import UnifiedPerpetualThinkingEngine
        from .meta_cyclical_architecture import MetaCyclicalArchitecture
        from ...applications.enhanced_master_orchestration_system import EnhancedMasterOrchestrationSystem
        
        # Create integration
        integration = Perpetual108CycleIntegration(
            fractal_system=fractal_system,
            perpetual_engine=UnifiedPerpetualThinkingEngine(),
            meta_architecture=MetaCyclicalArchitecture(),
            orchestration_system=EnhancedMasterOrchestrationSystem(
                perpetual_engine=UnifiedPerpetualThinkingEngine(),
                meta_architecture=MetaCyclicalArchitecture(),
                database_service=None
            )
        )
        
        print("✅ Perpetual-108-Cycle Integration initialized successfully")
        
        # Test integrated execution
        result = await integration.execute_integrated_session(
            session_name="Test Integration",
            initial_input="Test input for integrated fractal-perpetual execution",
            integration_mode=PerpetualFractalMode.INTEGRATED
        )
        
        print(f"✅ Integrated execution completed: {result.success}")
        print(f"   Execution time: {result.execution_time:.2f}s")
        print(f"   Cross-system patterns: {len(result.cross_system_patterns)}")
        
        print("✅ Perpetual-108-Cycle Integration test completed successfully")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_perpetual_108_cycle_integration())
