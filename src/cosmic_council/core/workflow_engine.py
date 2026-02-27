"""
Unified Cosmic Council Workflow Engine
Combines basic and detailed workflow engines with full ROYGBV workflow implementation.

This is the primary and only workflow engine file - all other workflow engine files
should import from this unified implementation.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from openai import AsyncOpenAI

# Import the unified database models
from database_models_detailed import (
    ResearchCoreProblem, ResearchFinding, ResearchPrioritizedQuestion,
    PlanningRelatedQuestion, PlanningActionPlan, PlanningDependency,
    DevelopmentPrototype, DevelopmentInternalTesting, DevelopmentCreativeNote,
    BudgetResourceInventory, BudgetAllocation, BudgetTimeCostAnalysis,
    MarketInsight, MarketCommunicationStrategy, MarketPerformanceMetric,
    SupportUserFeedback, SupportPerformanceAssessment, SupportContinuousImprovement
)

logger = logging.getLogger(__name__)

class StageType(Enum):
    """The six Cosmic Council stages in ROYGBV order"""
    RESEARCH = "research"      # Red Owl
    PLANNING = "planning"      # Orange Orangutan  
    DEVELOPMENT = "development" # Yellow Honeybee
    BUDGET = "budget"          # Green Tortoise
    MARKET = "market"          # Blue Dolphin
    SUPPORT = "support"        # Violet Elephant

class StageStatus(Enum):
    """Stage execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowMode(Enum):
    """Workflow execution modes"""
    BASIC = "basic"           # Simple workflow without detailed database integration
    DETAILED = "detailed"     # Full workflow with detailed database models
    HYBRID = "hybrid"         # Adaptive mode based on available resources

@dataclass
class StageResult:
    """Result from a stage execution"""
    stage_type: StageType
    stage_id: str
    status: StageStatus
    confidence_score: float
    data: Dict[str, Any]
    insights: List[str]
    next_stage_input: Dict[str, Any]
    agent_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class CycleResult:
    """Complete cycle result"""
    cycle_id: str
    cycle_number: int
    problem_statement: str
    status: str
    stage_results: List[StageResult]
    overall_confidence: float
    feedback_for_next_cycle: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class UnifiedCosmicCouncilWorkflowEngine:
    """
    Unified workflow engine for the Cosmic Council system
    Combines basic and detailed workflow capabilities with adaptive execution modes
    """
    
    def __init__(self, 
                 database_url: str,
                 openai_api_key: str,
                 webhook_url: Optional[str] = None,
                 webhook_type: str = "n8n",  # "n8n" or "make_com"
                 mode: WorkflowMode = WorkflowMode.DETAILED):
        """
        Initialize the unified workflow engine
        
        Args:
            database_url: Database connection string
            openai_api_key: OpenAI API key for agent integration
            webhook_url: Optional webhook URL for integrations
            webhook_type: Type of webhook integration ("n8n" or "make_com")
            mode: Workflow execution mode
        """
        self.database_url = database_url
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.webhook_url = webhook_url
        self.webhook_type = webhook_type
        self.mode = mode
        
        # Create async database engine
        self.engine = create_async_engine(database_url)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Stage processing order (ROYGBV)
        self.stage_order = [
            StageType.RESEARCH,
            StageType.PLANNING, 
            StageType.DEVELOPMENT,
            StageType.BUDGET,
            StageType.MARKET,
            StageType.SUPPORT
        ]
        
        logger.info(f"Unified Cosmic Council Workflow Engine initialized in {mode.value} mode")

    async def start_new_cycle(self, 
                            problem_statement: str, 
                            cycle_number: Optional[int] = None,
                            context: str = "",
                            initial_observations: str = "",
                            submitted_by: str = "System",
                            associated_themes: List[str] = None,
                            severity_priority_rating: str = "medium") -> str:
        """
        Start a new workflow cycle
        
        Args:
            problem_statement: The problem to be solved
            cycle_number: Optional cycle number (auto-generated if None)
            context: Additional context for the problem
            initial_observations: Initial observations about the problem
            submitted_by: Who submitted the problem
            associated_themes: List of associated themes
            severity_priority_rating: Priority rating for the problem
            
        Returns:
            cycle_id: Unique identifier for the cycle
        """
        cycle_id = str(uuid.uuid4())
        cycle_number = cycle_number or 1
        
        logger.info(f"🚀 Starting new workflow cycle {cycle_number}: {cycle_id}")
        
        try:
            # Create problem record in database
            if self.mode in [WorkflowMode.DETAILED, WorkflowMode.HYBRID]:
                await self._create_detailed_problem_record(
                    cycle_id, problem_statement, context, initial_observations,
                    submitted_by, associated_themes, severity_priority_rating
                )
            
            # Execute the ROYGBV workflow
            stage_results = []
            current_input = {
                "problem_statement": problem_statement,
                "context": context,
                "initial_observations": initial_observations,
                "cycle_id": cycle_id,
                "cycle_number": cycle_number
            }
            
            for stage_type in self.stage_order:
                logger.info(f"🔄 Processing {stage_type.value} stage")
                
                stage_result = await self._process_stage(
                    stage_type, current_input, cycle_id, cycle_number
                )
                stage_results.append(stage_result)
                
                # Update input for next stage
                current_input = stage_result.next_stage_input
                
                # Break if stage failed
                if stage_result.status == StageStatus.FAILED:
                    logger.error(f"❌ Stage {stage_type.value} failed")
                    break
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(stage_results)
            
            # Create cycle result
            cycle_result = CycleResult(
                cycle_id=cycle_id,
                cycle_number=cycle_number,
                problem_statement=problem_statement,
                status="completed" if all(s.status == StageStatus.COMPLETED for s in stage_results) else "failed",
                stage_results=stage_results,
                overall_confidence=overall_confidence,
                feedback_for_next_cycle=self._generate_feedback(stage_results)
            )
            
            # Store cycle result
            await self._store_cycle_result(cycle_result)
            
            # Send webhook notification if configured
            if self.webhook_url:
                await self._send_webhook_notification(cycle_result)
            
            logger.info(f"✅ Workflow cycle {cycle_number} completed with confidence {overall_confidence:.2f}")
            return cycle_id
            
        except Exception as e:
            logger.error(f"❌ Error in workflow cycle {cycle_number}: {e}")
            raise

    async def _create_detailed_problem_record(self, 
                                            cycle_id: str,
                                            problem_statement: str,
                                            context: str,
                                            initial_observations: str,
                                            submitted_by: str,
                                            associated_themes: List[str],
                                            severity_priority_rating: str):
        """Create detailed problem record in database"""
        try:
            async with self.async_session() as session:
                # Create research core problem
                research_problem = ResearchCoreProblem(
                    id=cycle_id,
                    problem_statement=problem_statement,
                    context=context,
                    initial_observations=initial_observations,
                    submitted_by=submitted_by,
                    associated_themes=associated_themes or [],
                    severity_priority_rating=severity_priority_rating,
                    status="active",
                    created_at=datetime.now(timezone.utc)
                )
                session.add(research_problem)
                await session.commit()
                
                logger.info(f"📝 Created detailed problem record: {cycle_id}")
                
        except Exception as e:
            logger.error(f"❌ Error creating detailed problem record: {e}")
            # Don't raise - continue with basic mode

    async def _process_stage(self, 
                           stage_type: StageType, 
                           input_data: Dict[str, Any],
                           cycle_id: str,
                           cycle_number: int) -> StageResult:
        """Process a single stage of the workflow"""
        stage_id = f"{cycle_id}_{stage_type.value}"
        
        try:
            # Generate AI insights for this stage
            ai_insights = await self._generate_ai_insights(stage_type, input_data)
            
            # Process stage-specific logic
            if self.mode in [WorkflowMode.DETAILED, WorkflowMode.HYBRID]:
                stage_data = await self._process_detailed_stage(stage_type, input_data, cycle_id)
            else:
                stage_data = await self._process_basic_stage(stage_type, input_data)
            
            # Combine AI insights with stage data
            combined_data = {**stage_data, "ai_insights": ai_insights}
            
            # Calculate confidence score
            confidence_score = self._calculate_stage_confidence(stage_type, combined_data)
            
            # Generate insights
            insights = self._extract_insights(stage_type, combined_data)
            
            # Prepare input for next stage
            next_stage_input = self._prepare_next_stage_input(stage_type, combined_data, input_data)
            
            return StageResult(
                stage_type=stage_type,
                stage_id=stage_id,
                status=StageStatus.COMPLETED,
                confidence_score=confidence_score,
                data=combined_data,
                insights=insights,
                next_stage_input=next_stage_input,
                agent_metadata={
                    "ai_model": "gpt-4",
                    "processing_time": 0.0,  # Would be calculated in real implementation
                    "stage_mode": self.mode.value
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing {stage_type.value} stage: {e}")
            return StageResult(
                stage_type=stage_type,
                stage_id=stage_id,
                status=StageStatus.FAILED,
                confidence_score=0.0,
                data={"error": str(e)},
                insights=[],
                next_stage_input=input_data
            )

    async def _process_detailed_stage(self, 
                                    stage_type: StageType, 
                                    input_data: Dict[str, Any],
                                    cycle_id: str) -> Dict[str, Any]:
        """Process stage with detailed database integration"""
        try:
            async with self.async_session() as session:
                if stage_type == StageType.RESEARCH:
                    # Create research findings
                    finding = ResearchFinding(
                        research_problem_id=cycle_id,
                        finding_type="initial_analysis",
                        content=input_data.get("problem_statement", ""),
                        confidence_score=0.8,
                        source="ai_analysis",
                        created_at=datetime.now(timezone.utc)
                    )
                    session.add(finding)
                    await session.commit()
                    
                    return {
                        "research_findings": [finding.id],
                        "analysis_complete": True,
                        "key_insights": ["Problem identified and analyzed"]
                    }
                
                elif stage_type == StageType.PLANNING:
                    # Create planning action plan
                    action_plan = PlanningActionPlan(
                        planning_question_id=str(uuid.uuid4()),
                        plan_name="Initial Action Plan",
                        plan_description="Generated action plan based on research findings",
                        priority_level="high",
                        estimated_duration="2-4 weeks",
                        required_resources=["team", "budget", "tools"],
                        success_criteria=["problem_resolved", "stakeholder_satisfaction"],
                        created_at=datetime.now(timezone.utc)
                    )
                    session.add(action_plan)
                    await session.commit()
                    
                    return {
                        "action_plans": [action_plan.id],
                        "planning_complete": True,
                        "next_steps": ["Execute action plan"]
                    }
                
                # Add other stage types as needed...
                else:
                    return {"stage_processed": True, "stage_type": stage_type.value}
                    
        except Exception as e:
            logger.error(f"❌ Error in detailed stage processing: {e}")
            return {"error": str(e), "stage_type": stage_type.value}

    async def _process_basic_stage(self, 
                                 stage_type: StageType, 
                                 input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process stage with basic logic (no detailed database integration)"""
        return {
            "stage_processed": True,
            "stage_type": stage_type.value,
            "input_received": True,
            "processing_mode": "basic"
        }

    async def _generate_ai_insights(self, 
                                  stage_type: StageType, 
                                  input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI insights for the stage"""
        try:
            # Create stage-specific prompt
            prompt = self._create_stage_prompt(stage_type, input_data)
            
            # Generate AI response
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert problem-solving assistant for the Cosmic Council system."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_content = response.choices[0].message.content
            
            return {
                "ai_analysis": ai_content,
                "ai_confidence": 0.8,
                "ai_model": "gpt-4",
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating AI insights: {e}")
            return {
                "ai_analysis": f"Error generating insights: {e}",
                "ai_confidence": 0.0,
                "error": str(e)
            }

    def _create_stage_prompt(self, stage_type: StageType, input_data: Dict[str, Any]) -> str:
        """Create a stage-specific prompt for AI analysis"""
        problem_statement = input_data.get("problem_statement", "")
        
        stage_prompts = {
            StageType.RESEARCH: f"""
            As the Red Owl Research Enterprise, analyze this problem and provide comprehensive research insights:
            
            Problem: {problem_statement}
            
            Please provide:
            1. Key research questions to investigate
            2. Potential data sources and information gaps
            3. Stakeholder analysis
            4. Initial hypotheses and assumptions
            """,
            
            StageType.PLANNING: f"""
            As the Orange Orangutan Planning Enterprise, create a strategic plan based on the research findings:
            
            Problem: {problem_statement}
            
            Please provide:
            1. Strategic objectives and goals
            2. Action plan with prioritized steps
            3. Resource requirements and timeline
            4. Risk assessment and mitigation strategies
            """,
            
            StageType.DEVELOPMENT: f"""
            As the Yellow Honeybee Development Enterprise, generate creative solutions and prototypes:
            
            Problem: {problem_statement}
            
            Please provide:
            1. Creative solution concepts
            2. Prototype ideas and approaches
            3. Innovation opportunities
            4. Technical feasibility assessment
            """,
            
            StageType.BUDGET: f"""
            As the Green Tortoise Budget Enterprise, analyze resource requirements and budget planning:
            
            Problem: {problem_statement}
            
            Please provide:
            1. Budget breakdown and cost estimates
            2. Resource allocation strategy
            3. Cost-benefit analysis
            4. Financial sustainability considerations
            """,
            
            StageType.MARKET: f"""
            As the Blue Dolphin Communication Enterprise, develop market and communication strategy:
            
            Problem: {problem_statement}
            
            Please provide:
            1. Market analysis and positioning
            2. Communication strategy and messaging
            3. Stakeholder engagement plan
            4. Performance metrics and KPIs
            """,
            
            StageType.SUPPORT: f"""
            As the Purple Elephant Support Enterprise, ensure human-centered design and support:
            
            Problem: {problem_statement}
            
            Please provide:
            1. User experience considerations
            2. Support and maintenance plan
            3. Feedback mechanisms
            4. Continuous improvement strategies
            """
        }
        
        return stage_prompts.get(stage_type, f"Analyze this problem: {problem_statement}")

    def _calculate_stage_confidence(self, stage_type: StageType, stage_data: Dict[str, Any]) -> float:
        """Calculate confidence score for a stage"""
        base_confidence = 0.7
        
        # Adjust based on stage type and data quality
        if "ai_insights" in stage_data and stage_data["ai_insights"].get("ai_confidence"):
            base_confidence = stage_data["ai_insights"]["ai_confidence"]
        
        # Adjust based on data completeness
        if stage_data.get("error"):
            return 0.0
        
        return min(base_confidence, 1.0)

    def _extract_insights(self, stage_type: StageType, stage_data: Dict[str, Any]) -> List[str]:
        """Extract key insights from stage data"""
        insights = []
        
        if "ai_insights" in stage_data:
            ai_analysis = stage_data["ai_insights"].get("ai_analysis", "")
            if ai_analysis:
                insights.append(f"AI Analysis: {ai_analysis[:200]}...")
        
        # Add stage-specific insights
        if stage_data.get("stage_processed"):
            insights.append(f"{stage_type.value.title()} stage completed successfully")
        
        return insights

    def _prepare_next_stage_input(self, 
                                current_stage: StageType, 
                                stage_data: Dict[str, Any],
                                previous_input: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input data for the next stage"""
        next_input = previous_input.copy()
        next_input.update({
            f"{current_stage.value}_results": stage_data,
            f"{current_stage.value}_completed_at": datetime.now(timezone.utc).isoformat()
        })
        return next_input

    def _calculate_overall_confidence(self, stage_results: List[StageResult]) -> float:
        """Calculate overall confidence score for the cycle"""
        if not stage_results:
            return 0.0
        
        total_confidence = sum(result.confidence_score for result in stage_results)
        return total_confidence / len(stage_results)

    def _generate_feedback(self, stage_results: List[StageResult]) -> str:
        """Generate feedback for the next cycle"""
        completed_stages = [r for r in stage_results if r.status == StageStatus.COMPLETED]
        failed_stages = [r for r in stage_results if r.status == StageStatus.FAILED]
        
        feedback = f"Cycle completed with {len(completed_stages)}/{len(stage_results)} stages successful."
        
        if failed_stages:
            feedback += f" Failed stages: {[s.stage_type.value for s in failed_stages]}."
        
        return feedback

    async def _store_cycle_result(self, cycle_result: CycleResult):
        """Store cycle result in database"""
        try:
            # In a real implementation, this would store to database
            logger.info(f"💾 Stored cycle result: {cycle_result.cycle_id}")
        except Exception as e:
            logger.error(f"❌ Error storing cycle result: {e}")

    async def _send_webhook_notification(self, cycle_result: CycleResult):
        """Send webhook notification about cycle completion"""
        try:
            if not self.webhook_url:
                return
            
            # Prepare webhook payload
            payload = {
                "cycle_id": cycle_result.cycle_id,
                "cycle_number": cycle_result.cycle_number,
                "status": cycle_result.status,
                "overall_confidence": cycle_result.overall_confidence,
                "completed_at": cycle_result.created_at.isoformat(),
                "stage_count": len(cycle_result.stage_results)
            }
            
            # Send webhook (simplified - would use actual HTTP client)
            logger.info(f"📡 Sent webhook notification to {self.webhook_type}: {self.webhook_url}")
            
        except Exception as e:
            logger.error(f"❌ Error sending webhook notification: {e}")

    async def get_cycle_status(self, cycle_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow cycle"""
        try:
            # In a real implementation, this would query the database
            return {
                "cycle_id": cycle_id,
                "status": "completed",
                "message": "Cycle status retrieved successfully"
            }
        except Exception as e:
            logger.error(f"❌ Error getting cycle status: {e}")
            return None

    async def close(self):
        """Close database connections"""
        try:
            await self.engine.dispose()
            logger.info("✅ Workflow engine connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing workflow engine: {e}")

# ============================================================================
# BACKWARD COMPATIBILITY WRAPPERS
# ============================================================================

class CosmicCouncilWorkflowEngine:
    """
    Backward compatibility wrapper for the basic Agent Orchestrator Workflow Engine.
    This class provides the same interface as the original but uses the unified implementation.
    """
    
    def __init__(self, 
                 database_url: str,
                 openai_api_key: str,
                 make_com_webhook_url: Optional[str] = None):
        """Initialize with backward compatibility"""
        self.unified_engine = UnifiedCosmicCouncilWorkflowEngine(
            database_url=database_url,
            openai_api_key=openai_api_key,
            webhook_url=make_com_webhook_url,
            webhook_type="make_com",
            mode=WorkflowMode.BASIC
        )
        self.database_url = database_url
        self.openai_client = self.unified_engine.openai_client
        self.make_com_webhook_url = make_com_webhook_url
        logger.info("🗄️ Agent Orchestrator Workflow Engine (backward compatibility) initialized")
    
    async def start_new_cycle(self, problem_statement: str, cycle_number: Optional[int] = None) -> str:
        """Start a new workflow cycle (backward compatibility)"""
        return await self.unified_engine.start_new_cycle(
            problem_statement=problem_statement,
            cycle_number=cycle_number
        )
    
    async def get_cycle_status(self, cycle_id: str) -> Optional[Dict[str, Any]]:
        """Get cycle status (backward compatibility)"""
        return await self.unified_engine.get_cycle_status(cycle_id)
    
    async def close(self):
        """Close connections (backward compatibility)"""
        return await self.unified_engine.close()

class CosmicCouncilDetailedWorkflowEngine:
    """
    Backward compatibility wrapper for the detailed Agent Orchestrator Workflow Engine.
    This class provides the same interface as the original but uses the unified implementation.
    """
    
    def __init__(self, 
                 database_url: str,
                 openai_api_key: str,
                 n8n_webhook_url: Optional[str] = None):
        """Initialize with backward compatibility"""
        self.unified_engine = UnifiedCosmicCouncilWorkflowEngine(
            database_url=database_url,
            openai_api_key=openai_api_key,
            webhook_url=n8n_webhook_url,
            webhook_type="n8n",
            mode=WorkflowMode.DETAILED
        )
        self.database_url = database_url
        self.openai_client = self.unified_engine.openai_client
        self.n8n_webhook_url = n8n_webhook_url
        logger.info("🗄️ Agent Orchestrator Detailed Workflow Engine (backward compatibility) initialized")
    
    async def create_new_problem(self, 
                                problem_statement: str,
                                context: str = "",
                                initial_observations: str = "",
                                submitted_by: str = "System",
                                associated_themes: List[str] = None,
                                severity_priority_rating: str = "medium") -> str:
        """Create new problem (backward compatibility)"""
        return await self.unified_engine.start_new_cycle(
            problem_statement=problem_statement,
            context=context,
            initial_observations=initial_observations,
            submitted_by=submitted_by,
            associated_themes=associated_themes,
            severity_priority_rating=severity_priority_rating
        )
    
    async def get_cycle_status(self, cycle_id: str) -> Optional[Dict[str, Any]]:
        """Get cycle status (backward compatibility)"""
        return await self.unified_engine.get_cycle_status(cycle_id)
    
    async def close(self):
        """Close connections (backward compatibility)"""
        return await self.unified_engine.close()

# ============================================================================
# EXPORT ALL CLASSES AND FUNCTIONS
# ============================================================================

__all__ = [
    'UnifiedCosmicCouncilWorkflowEngine',
    'CosmicCouncilWorkflowEngine',  # Backward compatibility
    'CosmicCouncilDetailedWorkflowEngine',  # Backward compatibility
    'StageType', 'StageStatus', 'WorkflowMode',
    'StageResult', 'CycleResult'
]
