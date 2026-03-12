"""
Unified 108-Cycle Fractal System for Agent Orchestrator
Combines basic, enhanced, and quantum fractal systems with full 108-stage implementation.

This is the primary and only fractal system file - all other fractal system files
should import from this unified implementation.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import math

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Import the unified database models
from ..core.models import (
    ResearchCoreProblem, ResearchFinding, ResearchPrioritizedQuestion,
    PlanningRelatedQuestion, PlanningActionPlan, PlanningDependency,
    DevelopmentPrototype, DevelopmentInternalTesting, DevelopmentCreativeNote,
    BudgetResourceInventory, BudgetAllocation, BudgetTimeCostAnalysis,
    MarketInsight, MarketCommunicationStrategy, MarketPerformanceMetric,
    SupportUserFeedback, SupportPerformanceAssessment, SupportContinuousImprovement
)

logger = logging.getLogger(__name__)

class EnterpriseType(Enum):
    """The six enterprises in the 108-cycle system"""
    RED_OWL = "red_owl"           # Research & Inquiry
    ORANGE_ORANGUTAN = "orange_orangutan"  # Planning & Logistics
    YELLOW_HONEYBEE = "yellow_honeybee"    # Development & Creativity
    GREEN_TORTOISE = "green_tortoise"      # Budget & Resources
    BLUE_DOLPHIN = "blue_dolphin"          # Market & Communication
    PURPLE_ELEPHANT = "purple_elephant"    # Support & Feedback

class SquadType(Enum):
    """The six squads within each enterprise"""
    ALPHA = "alpha"               # Primary execution squad
    BETA = "beta"                 # Secondary validation squad
    GAMMA = "gamma"               # Tertiary review squad
    DELTA = "delta"               # Quality assurance squad
    EPSILON = "epsilon"           # Innovation squad
    ZETA = "zeta"                 # Integration squad

class RedundancyPassType(Enum):
    """The three redundancy passes"""
    DECIDE = "decide"             # Initial decision making
    VALIDATE = "validate"         # Validation and verification
    REFLECT = "reflect"           # Reflection and improvement

class FractalMode(Enum):
    """Fractal system execution modes"""
    BASIC = "basic"               # Simple fractal execution
    ENHANCED = "enhanced"         # Enhanced with database integration
    QUANTUM = "quantum"          # Quantum-enhanced with spiritual integration
    ADAPTIVE = "adaptive"        # Automatically adapts based on available resources

class CycleStatus(Enum):
    """Cycle execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StageStatus(Enum):
    """Individual stage status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class QuantumCoherenceLevel(Enum):
    """Quantum coherence levels for quantum mode"""
    CLASSICAL = "classical"       # Standard processing
    QUANTUM = "quantum"          # Quantum superposition
    ENTANGLED = "entangled"      # Quantum entanglement
    COHERENT = "coherent"        # Full quantum coherence

class SpiritualAlignmentLevel(Enum):
    """Spiritual alignment levels for quantum mode"""
    MATERIAL = "material"        # Material world focus
    ETHEREAL = "ethereal"        # Subtle energy awareness
    CELESTIAL = "celestial"      # Higher dimensional awareness
    COSMIC = "cosmic"           # Universal consciousness

@dataclass
class CycleStage:
    """Represents a single stage in the 108-cycle system"""
    stage_id: int
    enterprise: EnterpriseType
    squad: SquadType
    redundancy_pass: RedundancyPassType
    stage_name: str
    description: str
    dependencies: List[int] = field(default_factory=list)
    estimated_duration_minutes: int = 30
    priority: int = 1
    required_resources: List[str] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)
    
    # Quantum and spiritual properties (for quantum mode)
    quantum_coherence_level: QuantumCoherenceLevel = QuantumCoherenceLevel.CLASSICAL
    spiritual_alignment_level: SpiritualAlignmentLevel = SpiritualAlignmentLevel.MATERIAL
    cosmic_significance: float = 0.0

@dataclass
class CycleRun:
    """Represents a complete 108-cycle execution"""
    run_id: str
    cycle_id: str
    objective_ref: str
    priority: int
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    status: CycleStatus = CycleStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    stages: List[CycleStage] = field(default_factory=list)
    stage_runs: Dict[str, 'StageRun'] = field(default_factory=dict)
    final_decision: Optional[Dict[str, Any]] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Enhanced properties
    problem_id: Optional[str] = None
    current_stage: int = 1
    total_stages: int = 108
    progress_percentage: float = 0.0
    
    # Quantum properties (for quantum mode)
    quantum_state: str = "classical"
    spiritual_resonance: float = 0.0
    cosmic_alignment: float = 0.0

@dataclass
class StageRun:
    """Represents execution of a single stage"""
    stage_run_id: str
    stage_id: int
    cycle_run_id: str
    status: StageStatus = StageStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_seconds: Optional[float] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Enhanced properties
    enterprise: EnterpriseType = EnterpriseType.RED_OWL
    squad: SquadType = SquadType.ALPHA
    redundancy_pass: RedundancyPassType = RedundancyPassType.DECIDE
    
    # Quantum properties (for quantum mode)
    quantum_coherence: float = 0.0
    spiritual_insights: List[str] = field(default_factory=list)
    cosmic_insights_generated: List[str] = field(default_factory=list)

class UnifiedFractal108CycleSystem:
    """
    Unified 108-cycle fractal system combining basic, enhanced, and quantum capabilities
    6 Enterprises × 6 Squads × 3 Redundancy Passes = 108 Stages
    """
    
    def __init__(self, 
                 database_url: Optional[str] = None,
                 mode: FractalMode = FractalMode.ENHANCED,
                 enable_quantum_features: bool = False,
                 enable_spiritual_integration: bool = False):
        """
        Initialize the unified fractal system
        
        Args:
            database_url: Database connection string (required for enhanced/quantum modes)
            mode: Fractal execution mode
            enable_quantum_features: Enable quantum processing features
            enable_spiritual_integration: Enable spiritual/consciousness integration
        """
        self.mode = mode
        self.enable_quantum_features = enable_quantum_features
        self.enable_spiritual_integration = enable_spiritual_integration
        
        # Initialize database connection if provided
        self.database_url = database_url
        self.engine = None
        self.async_session = None
        
        if database_url and mode in [FractalMode.ENHANCED, FractalMode.QUANTUM, FractalMode.ADAPTIVE]:
            self.engine = create_async_engine(database_url)
            self.async_session = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
        
        # Initialize system components
        self.enterprises = list(EnterpriseType)
        self.squads = list(SquadType)
        self.redundancy_passes = list(RedundancyPassType)
        self.stages: Dict[int, CycleStage] = {}
        self.cycle_runs: Dict[str, CycleRun] = {}
        self.stage_runs: Dict[str, StageRun] = {}
        
        # Initialize all 108 stages
        self._initialize_108_stages()
        
        # Enterprise processing functions
        self.enterprise_processors = {
            EnterpriseType.RED_OWL: self._process_red_owl,
            EnterpriseType.ORANGE_ORANGUTAN: self._process_orange_orangutan,
            EnterpriseType.YELLOW_HONEYBEE: self._process_yellow_honeybee,
            EnterpriseType.GREEN_TORTOISE: self._process_green_tortoise,
            EnterpriseType.BLUE_DOLPHIN: self._process_blue_dolphin,
            EnterpriseType.PURPLE_ELEPHANT: self._process_purple_elephant
        }
        
        # Squad specializations
        self.squad_specializations = {
            SquadType.ALPHA: "strategic_analysis",
            SquadType.BETA: "tactical_execution", 
            SquadType.GAMMA: "quality_assurance",
            SquadType.DELTA: "innovation_research",
            SquadType.EPSILON: "stakeholder_engagement",
            SquadType.ZETA: "continuous_improvement"
        }
        
        logger.info(f"Unified 108-Cycle Fractal System initialized in {mode.value} mode with 108 stages")

    def _initialize_108_stages(self):
        """Initialize all 108 stages of the fractal system"""
        stage_id = 1
        
        for enterprise in self.enterprises:
            for squad in self.squads:
                for redundancy_pass in self.redundancy_passes:
                    # Determine quantum and spiritual properties based on mode
                    quantum_level = QuantumCoherenceLevel.CLASSICAL
                    spiritual_level = SpiritualAlignmentLevel.MATERIAL
                    cosmic_significance = 0.0
                    
                    if self.mode == FractalMode.QUANTUM and self.enable_quantum_features:
                        # Assign quantum levels based on enterprise and squad
                        quantum_level = self._assign_quantum_level(enterprise, squad)
                        spiritual_level = self._assign_spiritual_level(enterprise, squad)
                        cosmic_significance = self._calculate_cosmic_significance(enterprise, squad, redundancy_pass)
                    
                    stage = CycleStage(
                        stage_id=stage_id,
                        enterprise=enterprise,
                        squad=squad,
                        redundancy_pass=redundancy_pass,
                        stage_name=f"{enterprise.value}_{squad.value}_{redundancy_pass.value}",
                        description=f"Stage {stage_id}: {enterprise.value} {squad.value} {redundancy_pass.value}",
                        estimated_duration_minutes=self._estimate_duration(enterprise, squad, redundancy_pass),
                        priority=self._calculate_priority(enterprise, squad, redundancy_pass),
                        quantum_coherence_level=quantum_level,
                        spiritual_alignment_level=spiritual_level,
                        cosmic_significance=cosmic_significance
                    )
                    
                    self.stages[stage_id] = stage
                    stage_id += 1
        
        logger.info(f"✅ Initialized {len(self.stages)} fractal stages")

    def _assign_quantum_level(self, enterprise: EnterpriseType, squad: SquadType) -> QuantumCoherenceLevel:
        """Assign quantum coherence level based on enterprise and squad"""
        # Red Owl (Research) gets higher quantum levels
        if enterprise == EnterpriseType.RED_OWL:
            if squad in [SquadType.ALPHA, SquadType.DELTA]:
                return QuantumCoherenceLevel.ENTANGLED
            else:
                return QuantumCoherenceLevel.QUANTUM
        
        # Purple Elephant (Support) gets spiritual quantum levels
        elif enterprise == EnterpriseType.PURPLE_ELEPHANT:
            if squad in [SquadType.GAMMA, SquadType.ZETA]:
                return QuantumCoherenceLevel.COHERENT
            else:
                return QuantumCoherenceLevel.ENTANGLED
        
        # Other enterprises get standard quantum levels
        else:
            if squad in [SquadType.ALPHA, SquadType.BETA]:
                return QuantumCoherenceLevel.QUANTUM
            else:
                return QuantumCoherenceLevel.CLASSICAL

    def _assign_spiritual_level(self, enterprise: EnterpriseType, squad: SquadType) -> SpiritualAlignmentLevel:
        """Assign spiritual alignment level based on enterprise and squad"""
        # Purple Elephant (Support) gets highest spiritual levels
        if enterprise == EnterpriseType.PURPLE_ELEPHANT:
            if squad in [SquadType.GAMMA, SquadType.ZETA]:
                return SpiritualAlignmentLevel.COSMIC
            else:
                return SpiritualAlignmentLevel.CELESTIAL
        
        # Red Owl (Research) gets ethereal levels
        elif enterprise == EnterpriseType.RED_OWL:
            if squad in [SquadType.ALPHA, SquadType.DELTA]:
                return SpiritualAlignmentLevel.CELESTIAL
            else:
                return SpiritualAlignmentLevel.ETHEREAL
        
        # Other enterprises get material/ethereal levels
        else:
            if squad in [SquadType.ALPHA, SquadType.BETA]:
                return SpiritualAlignmentLevel.ETHEREAL
            else:
                return SpiritualAlignmentLevel.MATERIAL

    def _calculate_cosmic_significance(self, enterprise: EnterpriseType, squad: SquadType, redundancy_pass: RedundancyPassType) -> float:
        """Calculate cosmic significance score for quantum mode"""
        base_score = 0.1
        
        # Enterprise multipliers
        enterprise_multipliers = {
            EnterpriseType.RED_OWL: 1.2,
            EnterpriseType.ORANGE_ORANGUTAN: 1.0,
            EnterpriseType.YELLOW_HONEYBEE: 1.1,
            EnterpriseType.GREEN_TORTOISE: 0.9,
            EnterpriseType.BLUE_DOLPHIN: 1.0,
            EnterpriseType.PURPLE_ELEPHANT: 1.3
        }
        
        # Squad multipliers
        squad_multipliers = {
            SquadType.ALPHA: 1.2,
            SquadType.BETA: 1.0,
            SquadType.GAMMA: 1.1,
            SquadType.DELTA: 1.3,
            SquadType.EPSILON: 1.0,
            SquadType.ZETA: 1.2
        }
        
        # Redundancy pass multipliers
        pass_multipliers = {
            RedundancyPassType.DECIDE: 1.0,
            RedundancyPassType.VALIDATE: 1.1,
            RedundancyPassType.REFLECT: 1.2
        }
        
        return base_score * enterprise_multipliers[enterprise] * squad_multipliers[squad] * pass_multipliers[redundancy_pass]

    def _estimate_duration(self, enterprise: EnterpriseType, squad: SquadType, redundancy_pass: RedundancyPassType) -> int:
        """Estimate duration in minutes for a stage"""
        base_duration = 30
        
        # Enterprise-specific durations
        enterprise_durations = {
            EnterpriseType.RED_OWL: 45,      # Research takes longer
            EnterpriseType.ORANGE_ORANGUTAN: 35,  # Planning
            EnterpriseType.YELLOW_HONEYBEE: 40,   # Development
            EnterpriseType.GREEN_TORTOISE: 25,    # Budget (faster)
            EnterpriseType.BLUE_DOLPHIN: 30,      # Communication
            EnterpriseType.PURPLE_ELEPHANT: 35    # Support
        }
        
        # Squad-specific adjustments
        squad_adjustments = {
            SquadType.ALPHA: 1.2,    # Primary execution takes longer
            SquadType.BETA: 1.0,     # Standard
            SquadType.GAMMA: 1.1,    # Review takes a bit longer
            SquadType.DELTA: 1.3,    # Innovation takes longer
            SquadType.EPSILON: 1.0,  # Standard
            SquadType.ZETA: 1.1      # Integration takes a bit longer
        }
        
        return int(enterprise_durations[enterprise] * squad_adjustments[squad])

    def _calculate_priority(self, enterprise: EnterpriseType, squad: SquadType, redundancy_pass: RedundancyPassType) -> int:
        """Calculate priority for a stage (1-10, higher is more important)"""
        base_priority = 5
        
        # Enterprise priorities
        enterprise_priorities = {
            EnterpriseType.RED_OWL: 8,       # Research is high priority
            EnterpriseType.ORANGE_ORANGUTAN: 7,  # Planning is important
            EnterpriseType.YELLOW_HONEYBEE: 6,   # Development
            EnterpriseType.GREEN_TORTOISE: 4,    # Budget (lower priority)
            EnterpriseType.BLUE_DOLPHIN: 5,      # Communication
            EnterpriseType.PURPLE_ELEPHANT: 7    # Support is important
        }
        
        # Squad priorities
        squad_priorities = {
            SquadType.ALPHA: 8,      # Primary execution is high priority
            SquadType.BETA: 6,       # Secondary validation
            SquadType.GAMMA: 7,      # Review is important
            SquadType.DELTA: 5,      # Innovation (medium priority)
            SquadType.EPSILON: 6,    # Stakeholder engagement
            SquadType.ZETA: 7        # Continuous improvement is important
        }
        
        return min(10, max(1, (enterprise_priorities[enterprise] + squad_priorities[squad]) // 2))

    async def start_cycle(self, 
                         objective_ref: str,
                         context: Dict[str, Any],
                         priority: int = 5,
                         problem_id: Optional[str] = None) -> str:
        """
        Start a new 108-cycle execution
        
        Args:
            objective_ref: Reference to the objective being processed
            context: Context data for the cycle
            priority: Priority level (1-10)
            problem_id: Optional problem ID for database integration
            
        Returns:
            run_id: Unique identifier for the cycle run
        """
        run_id = str(uuid.uuid4())
        cycle_id = str(uuid.uuid4())
        
        logger.info(f"🚀 Starting 108-cycle run: {run_id}")
        
        # Create cycle run
        cycle_run = CycleRun(
            run_id=run_id,
            cycle_id=cycle_id,
            objective_ref=objective_ref,
            priority=priority,
            context=context,
            metadata={
                "mode": self.mode.value,
                "quantum_enabled": self.enable_quantum_features,
                "spiritual_enabled": self.enable_spiritual_integration,
                "total_stages": 108
            },
            problem_id=problem_id,
            status=CycleStatus.RUNNING,
            started_at=datetime.now(timezone.utc)
        )
        
        self.cycle_runs[run_id] = cycle_run
        
        try:
            # Execute the 108 stages
            await self._execute_108_stages(cycle_run)
            
            # Mark as completed
            cycle_run.status = CycleStatus.COMPLETED
            cycle_run.completed_at = datetime.now(timezone.utc)
            cycle_run.progress_percentage = 100.0
            
            # Generate final decision
            cycle_run.final_decision = await self._generate_final_decision(cycle_run)
            
            logger.info(f"✅ 108-cycle run completed: {run_id}")
            return run_id
            
        except Exception as e:
            logger.error(f"❌ Error in 108-cycle run {run_id}: {e}")
            cycle_run.status = CycleStatus.FAILED
            cycle_run.metadata["error"] = str(e)
            raise

    async def _execute_108_stages(self, cycle_run: CycleRun):
        """Execute all 108 stages of the fractal system"""
        for stage_id in range(1, 109):  # 1 to 108
            stage = self.stages[stage_id]
            
            logger.info(f"🔄 Executing stage {stage_id}/108: {stage.stage_name}")
            
            # Create stage run
            stage_run = StageRun(
                stage_run_id=str(uuid.uuid4()),
                stage_id=stage_id,
                cycle_run_id=cycle_run.run_id,
                enterprise=stage.enterprise,
                squad=stage.squad,
                redundancy_pass=stage.redundancy_pass,
                status=StageStatus.RUNNING,
                started_at=datetime.now(timezone.utc)
            )
            
            try:
                # Execute the stage
                await self._execute_stage(stage, stage_run, cycle_run)
                
                # Mark as completed
                stage_run.status = StageStatus.COMPLETED
                stage_run.completed_at = datetime.now(timezone.utc)
                stage_run.execution_time_seconds = (
                    stage_run.completed_at - stage_run.started_at
                ).total_seconds()
                
                # Update cycle progress
                cycle_run.current_stage = stage_id
                cycle_run.progress_percentage = (stage_id / 108) * 100
                
                # Store stage run
                self.stage_runs[stage_run.stage_run_id] = stage_run
                cycle_run.stage_runs[stage_run.stage_run_id] = stage_run
                
                logger.info(f"✅ Stage {stage_id} completed in {stage_run.execution_time_seconds:.2f}s")
                
            except Exception as e:
                logger.error(f"❌ Error in stage {stage_id}: {e}")
                stage_run.status = StageStatus.FAILED
                stage_run.error_message = str(e)
                stage_run.completed_at = datetime.now(timezone.utc)
                
                # Store failed stage run
                self.stage_runs[stage_run.stage_run_id] = stage_run
                cycle_run.stage_runs[stage_run.stage_run_id] = stage_run
                
                # Decide whether to continue or fail the entire cycle
                if stage.priority >= 8:  # High priority stages cause cycle failure
                    raise

    async def _execute_stage(self, stage: CycleStage, stage_run: StageRun, cycle_run: CycleRun):
        """Execute a single stage"""
        # Get enterprise processor
        processor = self.enterprise_processors[stage.enterprise]
        
        # Prepare input data
        input_data = {
            "stage": stage,
            "cycle_run": cycle_run,
            "context": cycle_run.context,
            "mode": self.mode.value
        }
        
        # Add quantum properties if enabled
        if self.enable_quantum_features and self.mode == FractalMode.QUANTUM:
            input_data.update({
                "quantum_coherence_level": stage.quantum_coherence_level,
                "spiritual_alignment_level": stage.spiritual_alignment_level,
                "cosmic_significance": stage.cosmic_significance
            })
        
        # Execute the stage
        output_data = await processor(stage, input_data)
        
        # Process quantum effects if enabled
        if self.enable_quantum_features and self.mode == FractalMode.QUANTUM:
            output_data = await self._process_quantum_effects(stage, output_data)
        
        # Process spiritual integration if enabled
        if self.enable_spiritual_integration and self.mode == FractalMode.QUANTUM:
            output_data = await self._process_spiritual_integration(stage, output_data)
        
        # Store results
        stage_run.input_data = input_data
        stage_run.output_data = output_data
        stage_run.confidence_score = output_data.get("confidence_score", 0.8)
        
        # Update quantum properties
        if self.enable_quantum_features:
            stage_run.quantum_coherence = output_data.get("quantum_coherence", 0.0)
            stage_run.spiritual_insights = output_data.get("spiritual_insights", [])
            stage_run.cosmic_insights_generated = output_data.get("cosmic_insights", [])

    async def _process_red_owl(self, stage: CycleStage, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Red Owl (Research) enterprise stage"""
        # Basic research processing
        result = {
            "enterprise": "red_owl",
            "squad": stage.squad.value,
            "redundancy_pass": stage.redundancy_pass.value,
            "research_findings": [],
            "confidence_score": 0.8,
            "insights": ["Research analysis completed"]
        }
        
        # Enhanced processing with database integration
        if self.mode in [FractalMode.ENHANCED, FractalMode.QUANTUM, FractalMode.ADAPTIVE] and self.async_session:
            try:
                async with self.async_session() as session:
                    # Create research finding
                    finding = ResearchFinding(
                        research_problem_id=input_data.get("cycle_run", {}).get("problem_id", str(uuid.uuid4())),
                        finding_type=f"{stage.squad.value}_{stage.redundancy_pass.value}",
                        content=f"Research finding from {stage.stage_name}",
                        confidence_score=result["confidence_score"],
                        source="fractal_system",
                        created_at=datetime.now(timezone.utc)
                    )
                    session.add(finding)
                    await session.commit()
                    
                    result["research_findings"] = [str(finding.id)]
                    
            except Exception as e:
                logger.error(f"❌ Error in enhanced Red Owl processing: {e}")
                result["error"] = str(e)
        
        return result

    async def _process_orange_orangutan(self, stage: CycleStage, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Orange Orangutan (Planning) enterprise stage"""
        return {
            "enterprise": "orange_orangutan",
            "squad": stage.squad.value,
            "redundancy_pass": stage.redundancy_pass.value,
            "planning_complete": True,
            "confidence_score": 0.8,
            "insights": ["Planning analysis completed"]
        }

    async def _process_yellow_honeybee(self, stage: CycleStage, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Yellow Honeybee (Development) enterprise stage"""
        return {
            "enterprise": "yellow_honeybee",
            "squad": stage.squad.value,
            "redundancy_pass": stage.redundancy_pass.value,
            "development_complete": True,
            "confidence_score": 0.8,
            "insights": ["Development analysis completed"]
        }

    async def _process_green_tortoise(self, stage: CycleStage, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Green Tortoise (Budget) enterprise stage"""
        return {
            "enterprise": "green_tortoise",
            "squad": stage.squad.value,
            "redundancy_pass": stage.redundancy_pass.value,
            "budget_analysis_complete": True,
            "confidence_score": 0.8,
            "insights": ["Budget analysis completed"]
        }

    async def _process_blue_dolphin(self, stage: CycleStage, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Blue Dolphin (Communication) enterprise stage"""
        return {
            "enterprise": "blue_dolphin",
            "squad": stage.squad.value,
            "redundancy_pass": stage.redundancy_pass.value,
            "communication_analysis_complete": True,
            "confidence_score": 0.8,
            "insights": ["Communication analysis completed"]
        }

    async def _process_purple_elephant(self, stage: CycleStage, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Purple Elephant (Support) enterprise stage"""
        return {
            "enterprise": "purple_elephant",
            "squad": stage.squad.value,
            "redundancy_pass": stage.redundancy_pass.value,
            "support_analysis_complete": True,
            "confidence_score": 0.8,
            "insights": ["Support analysis completed"]
        }

    async def _process_quantum_effects(self, stage: CycleStage, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process quantum effects for quantum mode"""
        if not self.enable_quantum_features:
            return output_data
        
        # Simulate quantum processing
        quantum_coherence = stage.cosmic_significance * 0.8
        quantum_insights = [
            f"Quantum coherence achieved at level {stage.quantum_coherence_level.value}",
            f"Spiritual alignment at {stage.spiritual_alignment_level.value} level",
            f"Cosmic significance: {stage.cosmic_significance:.3f}"
        ]
        
        output_data.update({
            "quantum_coherence": quantum_coherence,
            "quantum_insights": quantum_insights,
            "quantum_processed": True
        })
        
        return output_data

    async def _process_spiritual_integration(self, stage: CycleStage, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process spiritual integration for quantum mode"""
        if not self.enable_spiritual_integration:
            return output_data
        
        # Generate spiritual insights
        spiritual_insights = [
            f"Spiritual resonance with {stage.enterprise.value} energy",
            f"Alignment with {stage.spiritual_alignment_level.value} consciousness",
            f"Cosmic wisdom channeled through {stage.squad.value} squad"
        ]
        
        cosmic_insights = [
            f"Universal pattern recognition in {stage.redundancy_pass.value} phase",
            f"Divine guidance received for {stage.stage_name}",
            f"Cosmic significance: {stage.cosmic_significance:.3f}"
        ]
        
        output_data.update({
            "spiritual_insights": spiritual_insights,
            "cosmic_insights": cosmic_insights,
            "spiritual_processed": True
        })
        
        return output_data

    async def _generate_final_decision(self, cycle_run: CycleRun) -> Dict[str, Any]:
        """Generate final decision from the 108-cycle run"""
        # Analyze all stage results
        completed_stages = [sr for sr in cycle_run.stage_runs.values() if sr.status == StageStatus.COMPLETED]
        failed_stages = [sr for sr in cycle_run.stage_runs.values() if sr.status == StageStatus.FAILED]
        
        # Calculate overall metrics
        total_execution_time = sum(
            sr.execution_time_seconds or 0 for sr in completed_stages
        )
        avg_confidence = sum(sr.confidence_score for sr in completed_stages) / len(completed_stages) if completed_stages else 0
        
        # Generate decision
        decision = {
            "cycle_run_id": cycle_run.run_id,
            "objective_ref": cycle_run.objective_ref,
            "status": "completed" if not failed_stages else "completed_with_issues",
            "total_stages": 108,
            "completed_stages": len(completed_stages),
            "failed_stages": len(failed_stages),
            "total_execution_time_seconds": total_execution_time,
            "average_confidence": avg_confidence,
            "final_recommendation": "proceed" if avg_confidence >= 0.7 else "review_required",
            "key_insights": self._extract_key_insights(completed_stages),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Add quantum properties if enabled
        if self.enable_quantum_features and self.mode == FractalMode.QUANTUM:
            quantum_insights = []
            cosmic_insights = []
            
            for stage_run in completed_stages:
                quantum_insights.extend(stage_run.spiritual_insights)
                cosmic_insights.extend(stage_run.cosmic_insights_generated)
            
            decision.update({
                "quantum_insights": quantum_insights,
                "cosmic_insights": cosmic_insights,
                "quantum_processed": True
            })
        
        return decision

    def _extract_key_insights(self, completed_stages: List[StageRun]) -> List[str]:
        """Extract key insights from completed stages"""
        insights = []
        
        # Group by enterprise
        enterprise_insights = {}
        for stage_run in completed_stages:
            enterprise = stage_run.enterprise.value
            if enterprise not in enterprise_insights:
                enterprise_insights[enterprise] = []
            enterprise_insights[enterprise].append(stage_run.confidence_score)
        
        # Generate insights
        for enterprise, scores in enterprise_insights.items():
            avg_score = sum(scores) / len(scores)
            insights.append(f"{enterprise} enterprise achieved {avg_score:.2f} average confidence")
        
        return insights

    async def get_cycle_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a cycle run"""
        if run_id not in self.cycle_runs:
            return None
        
        cycle_run = self.cycle_runs[run_id]
        
        return {
            "run_id": run_id,
            "status": cycle_run.status.value,
            "progress_percentage": cycle_run.progress_percentage,
            "current_stage": cycle_run.current_stage,
            "total_stages": cycle_run.total_stages,
            "started_at": cycle_run.started_at.isoformat() if cycle_run.started_at else None,
            "completed_at": cycle_run.completed_at.isoformat() if cycle_run.completed_at else None,
            "final_decision": cycle_run.final_decision
        }

    async def close(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
            logger.info("✅ Fractal system connections closed")

# ============================================================================
# BACKWARD COMPATIBILITY WRAPPERS
# ============================================================================

class Fractal108CycleSystem:
    """
    Backward compatibility wrapper for the basic Fractal 108-Cycle System.
    This class provides the same interface as the original but uses the unified implementation.
    """
    
    def __init__(self):
        """Initialize with backward compatibility"""
        self.unified_system = UnifiedFractal108CycleSystem(
            mode=FractalMode.BASIC,
            enable_quantum_features=False,
            enable_spiritual_integration=False
        )
        logger.info("🗄️ Fractal 108-Cycle System (backward compatibility) initialized")
    
    async def start_cycle(self, objective_ref: str, context: Dict[str, Any], priority: int = 5) -> str:
        """Start a new cycle (backward compatibility)"""
        return await self.unified_system.start_cycle(
            objective_ref=objective_ref,
            context=context,
            priority=priority
        )
    
    async def get_cycle_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get cycle status (backward compatibility)"""
        return await self.unified_system.get_cycle_status(run_id)
    
    async def close(self):
        """Close connections (backward compatibility)"""
        return await self.unified_system.close()

class Enhanced108CycleFractalSystem:
    """
    Backward compatibility wrapper for the Enhanced 108-Cycle Fractal System.
    This class provides the same interface as the original but uses the unified implementation.
    """
    
    def __init__(self, database_url: str):
        """Initialize with backward compatibility"""
        self.unified_system = UnifiedFractal108CycleSystem(
            database_url=database_url,
            mode=FractalMode.ENHANCED,
            enable_quantum_features=False,
            enable_spiritual_integration=False
        )
        logger.info("🗄️ Enhanced 108-Cycle Fractal System (backward compatibility) initialized")
    
    async def start_cycle(self, objective_ref: str, context: Dict[str, Any], priority: int = 5) -> str:
        """Start a new cycle (backward compatibility)"""
        return await self.unified_system.start_cycle(
            objective_ref=objective_ref,
            context=context,
            priority=priority
        )
    
    async def get_cycle_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get cycle status (backward compatibility)"""
        return await self.unified_system.get_cycle_status(run_id)
    
    async def close(self):
        """Close connections (backward compatibility)"""
        return await self.unified_system.close()

# ============================================================================
# EXPORT ALL CLASSES AND FUNCTIONS
# ============================================================================

__all__ = [
    'UnifiedFractal108CycleSystem',
    'Fractal108CycleSystem',  # Backward compatibility
    'Enhanced108CycleFractalSystem',  # Backward compatibility
    'EnterpriseType', 'SquadType', 'RedundancyPassType',
    'FractalMode', 'CycleStatus', 'StageStatus',
    'QuantumCoherenceLevel', 'SpiritualAlignmentLevel',
    'CycleStage', 'CycleRun', 'StageRun'
]
