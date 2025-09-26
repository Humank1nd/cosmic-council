"""
Enhanced Perpetual Thinking Integration for Cosmic Council
Integrates the perpetual thinking engine with the workflow system for continuous learning
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

# Import the unified perpetual thinking system
from .unified_perpetual_thinking_system import (
    UnifiedPerpetualThinkingEngine, 
    PerpetualCycle, 
    CycleType, 
    CycleStatus, 
    PatternType, 
    PatternAnalysis,
    CollaborativeMetrics
)

# Import the unified workflow engine
# TODO: Fix this import - module may have been moved or renamed
# from unified_workflow_engine import UnifiedCosmicCouncilWorkflowEngine

# Import the unified AI agent system
from unified_ai_agent_system import UnifiedCosmicCouncilAgent, AgentType, AgentContext, AgentResult

logger = logging.getLogger(__name__)

class LearningMode(Enum):
    """Modes of continuous learning"""
    EXPLORATORY = "exploratory"           # Broad exploration and discovery
    FOCUSED = "focused"                   # Focused learning on specific areas
    SYNTHETIC = "synthetic"               # Synthesis and integration
    ADAPTIVE = "adaptive"                 # Adaptive learning based on feedback
    BREAKTHROUGH = "breakthrough"         # Breakthrough and paradigm shifts
    META_LEARNING = "meta_learning"       # Learning about learning itself

class IntegrationLevel(Enum):
    """Levels of integration with workflow system"""
    SURFACE = "surface"                   # Basic integration
    DEEP = "deep"                         # Deep integration with workflow
    PERPETUAL = "perpetual"               # Full perpetual integration
    TRANSCENDENT = "transcendent"         # Transcendent integration

@dataclass
class LearningInsight:
    """A learning insight from the perpetual thinking engine"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    insight_type: str = ""
    content: str = ""
    confidence_score: float = 0.0
    relevance_score: float = 0.0
    source_cycle_id: str = ""
    source_agent_type: Optional[AgentType] = None
    learning_mode: LearningMode = LearningMode.EXPLORATORY
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowLearningIntegration:
    """Integration between workflow and perpetual thinking"""
    workflow_stage: str
    cycle_type: CycleType
    learning_mode: LearningMode
    integration_level: IntegrationLevel
    feedback_loop_enabled: bool = True
    continuous_learning_enabled: bool = True
    adaptation_threshold: float = 0.7

@dataclass
class PerpetualLearningMetrics:
    """Metrics for perpetual learning system"""
    total_cycles: int = 0
    total_insights: int = 0
    learning_velocity: float = 0.0
    adaptation_rate: float = 0.0
    breakthrough_frequency: float = 0.0
    wisdom_accumulation: float = 0.0
    synergy_score: float = 0.0
    continuous_improvement_score: float = 0.0

class EnhancedPerpetualThinkingIntegration:
    """
    Enhanced Perpetual Thinking Integration
    Integrates the perpetual thinking engine with the workflow system for continuous learning
    """
    
    def __init__(self, 
                 database_url: str,
                 openai_api_key: str,
                 session_factory: sessionmaker,
                 integration_config: Dict[str, Any] = None):
        """
        Initialize the perpetual thinking integration
        
        Args:
            database_url: Database connection string
            openai_api_key: OpenAI API key
            session_factory: Database session factory
            integration_config: Integration configuration
        """
        self.database_url = database_url
        self.openai_api_key = openai_api_key
        self.session_factory = session_factory
        self.integration_config = integration_config or {}
        
        # Create database engine
        self.engine = create_async_engine(database_url)
        
        # Initialize perpetual thinking engine
        self.perpetual_engine = PerpetualThinkingEngine(database_url)
        
        # Initialize workflow engine
        self.workflow_engine = EnhancedCosmicCouncilWorkflowEngine(
            database_url=database_url,
            openai_api_key=openai_api_key,
            session_factory=session_factory
        )
        
        # Learning insights storage
        self.learning_insights: List[LearningInsight] = []
        self.workflow_integrations: Dict[str, WorkflowLearningIntegration] = {}
        
        # Learning metrics
        self.learning_metrics = PerpetualLearningMetrics()
        
        # Integration settings
        self.continuous_learning_enabled = self.integration_config.get('continuous_learning_enabled', True)
        self.adaptation_threshold = self.integration_config.get('adaptation_threshold', 0.7)
        self.learning_velocity_target = self.integration_config.get('learning_velocity_target', 0.5)
        self.breakthrough_threshold = self.integration_config.get('breakthrough_threshold', 0.9)
        
        # Initialize workflow integrations
        self._initialize_workflow_integrations()
        
        logger.info("Enhanced Perpetual Thinking Integration initialized")

    def _initialize_workflow_integrations(self):
        """Initialize integrations between workflow stages and perpetual thinking"""
        # Red Stage - Research & Inquiry
        self.workflow_integrations['research'] = WorkflowLearningIntegration(
            workflow_stage='research',
            cycle_type=CycleType.EXPLORATION,
            learning_mode=LearningMode.EXPLORATORY,
            integration_level=IntegrationLevel.DEEP,
            feedback_loop_enabled=True,
            continuous_learning_enabled=True,
            adaptation_threshold=0.6
        )
        
        # Orange Stage - Planning & Logistics
        self.workflow_integrations['planning'] = WorkflowLearningIntegration(
            workflow_stage='planning',
            cycle_type=CycleType.CONVERGENCE,
            learning_mode=LearningMode.FOCUSED,
            integration_level=IntegrationLevel.DEEP,
            feedback_loop_enabled=True,
            continuous_learning_enabled=True,
            adaptation_threshold=0.7
        )
        
        # Yellow Stage - Development & Creativity
        self.workflow_integrations['development'] = WorkflowLearningIntegration(
            workflow_stage='development',
            cycle_type=CycleType.EXPLORATION,
            learning_mode=LearningMode.EXPLORATORY,
            integration_level=IntegrationLevel.PERPETUAL,
            feedback_loop_enabled=True,
            continuous_learning_enabled=True,
            adaptation_threshold=0.8
        )
        
        # Green Stage - Budget & Resources
        self.workflow_integrations['budget'] = WorkflowLearningIntegration(
            workflow_stage='budget',
            cycle_type=CycleType.CONVERGENCE,
            learning_mode=LearningMode.FOCUSED,
            integration_level=IntegrationLevel.DEEP,
            feedback_loop_enabled=True,
            continuous_learning_enabled=True,
            adaptation_threshold=0.7
        )
        
        # Blue Stage - Market & Communication
        self.workflow_integrations['market'] = WorkflowLearningIntegration(
            workflow_stage='market',
            cycle_type=CycleType.SYNTHESIS,
            learning_mode=LearningMode.SYNTHETIC,
            integration_level=IntegrationLevel.DEEP,
            feedback_loop_enabled=True,
            continuous_learning_enabled=True,
            adaptation_threshold=0.7
        )
        
        # Purple Stage - Support & Feedback
        self.workflow_integrations['support'] = WorkflowLearningIntegration(
            workflow_stage='support',
            cycle_type=CycleType.META_REFLECTION,
            learning_mode=LearningMode.META_LEARNING,
            integration_level=IntegrationLevel.TRANSCENDENT,
            feedback_loop_enabled=True,
            continuous_learning_enabled=True,
            adaptation_threshold=0.8
        )

    async def start_perpetual_workflow_learning(self, 
                                              problem_id: str,
                                              initial_context: Dict[str, Any] = None) -> str:
        """
        Start perpetual learning integrated with workflow system
        
        Args:
            problem_id: UUID of the problem to process
            initial_context: Initial context for learning
            
        Returns:
            Learning session ID
        """
        try:
            # Create learning session
            session_id = str(uuid.uuid4())
            
            # Initialize learning context
            learning_context = {
                'session_id': session_id,
                'problem_id': problem_id,
                'initial_context': initial_context or {},
                'started_at': datetime.now(timezone.utc),
                'learning_modes': [mode.value for mode in LearningMode],
                'integration_levels': [level.value for level in IntegrationLevel]
            }
            
            # Start perpetual thinking cycle
            initial_input = f"Begin perpetual learning for problem {problem_id}: {initial_context.get('problem_statement', 'No statement provided')}"
            cycle_id = await self.perpetual_engine.start_perpetual_cycle(
                initial_input=initial_input,
                cycle_type=CycleType.EXPLORATION,
                max_cycles=None  # Unlimited for perpetual learning
            )
            
            # Start workflow learning integration
            await self._start_workflow_learning_integration(session_id, problem_id, cycle_id)
            
            logger.info(f"Started perpetual workflow learning session {session_id} with cycle {cycle_id}")
            
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start perpetual workflow learning: {e}")
            raise

    async def _start_workflow_learning_integration(self, 
                                                 session_id: str, 
                                                 problem_id: str, 
                                                 cycle_id: str):
        """Start integration between workflow and perpetual thinking"""
        try:
            # Process through all workflow stages with perpetual learning
            for stage_name, integration in self.workflow_integrations.items():
                await self._process_stage_with_perpetual_learning(
                    session_id=session_id,
                    problem_id=problem_id,
                    cycle_id=cycle_id,
                    stage_name=stage_name,
                    integration=integration
                )
                
        except Exception as e:
            logger.error(f"Failed to start workflow learning integration: {e}")
            raise

    async def _process_stage_with_perpetual_learning(self, 
                                                   session_id: str,
                                                   problem_id: str,
                                                   cycle_id: str,
                                                   stage_name: str,
                                                   integration: WorkflowLearningIntegration):
        """Process a workflow stage with perpetual learning integration"""
        try:
            # Get current cycle status
            cycle_status = await self.perpetual_engine.get_cycle_status(cycle_id)
            if not cycle_status:
                logger.warning(f"No cycle status for {cycle_id}")
                return
            
            # Create stage context
            stage_context = {
                'session_id': session_id,
                'problem_id': problem_id,
                'cycle_id': cycle_id,
                'stage_name': stage_name,
                'cycle_status': cycle_status,
                'integration': integration.__dict__
            }
            
            # Process stage with workflow engine
            stage_result = await self.workflow_engine.process_stage(
                problem_id=problem_id,
                stage_name=stage_name,
                context=stage_context
            )
            
            # Extract learning insights from stage result
            insights = await self._extract_learning_insights(stage_result, stage_name, cycle_id)
            self.learning_insights.extend(insights)
            
            # Update learning metrics
            await self._update_learning_metrics(insights, stage_result)
            
            # Check for adaptation needs
            if await self._should_adapt_learning(integration, stage_result):
                await self._adapt_learning_process(integration, stage_result)
            
            # Generate feedback for perpetual thinking
            feedback = await self._generate_learning_feedback(stage_result, insights)
            if feedback:
                await self._feed_back_to_perpetual_engine(cycle_id, feedback)
            
            logger.info(f"Processed stage {stage_name} with perpetual learning integration")
            
        except Exception as e:
            logger.error(f"Failed to process stage {stage_name} with perpetual learning: {e}")
            raise

    async def _extract_learning_insights(self, 
                                       stage_result: Dict[str, Any], 
                                       stage_name: str, 
                                       cycle_id: str) -> List[LearningInsight]:
        """Extract learning insights from stage result"""
        insights = []
        
        try:
            # Extract insights from stage result
            if 'insights' in stage_result:
                for insight_data in stage_result['insights']:
                    insight = LearningInsight(
                        insight_type=f"{stage_name}_insight",
                        content=insight_data.get('content', ''),
                        confidence_score=insight_data.get('confidence_score', 0.0),
                        relevance_score=insight_data.get('relevance_score', 0.0),
                        source_cycle_id=cycle_id,
                        learning_mode=LearningMode.EXPLORATORY,  # Default, will be updated
                        metadata={
                            'stage_name': stage_name,
                            'stage_result': stage_result,
                            'extraction_timestamp': datetime.now(timezone.utc).isoformat()
                        }
                    )
                    insights.append(insight)
            
            # Extract recommendations as insights
            if 'recommendations' in stage_result:
                for rec_data in stage_result['recommendations']:
                    insight = LearningInsight(
                        insight_type=f"{stage_name}_recommendation",
                        content=rec_data.get('content', ''),
                        confidence_score=rec_data.get('confidence_score', 0.0),
                        relevance_score=rec_data.get('relevance_score', 0.0),
                        source_cycle_id=cycle_id,
                        learning_mode=LearningMode.FOCUSED,
                        metadata={
                            'stage_name': stage_name,
                            'stage_result': stage_result,
                            'extraction_timestamp': datetime.now(timezone.utc).isoformat()
                        }
                    )
                    insights.append(insight)
            
            # Extract patterns as insights
            if 'patterns' in stage_result:
                for pattern_data in stage_result['patterns']:
                    insight = LearningInsight(
                        insight_type=f"{stage_name}_pattern",
                        content=pattern_data.get('description', ''),
                        confidence_score=pattern_data.get('confidence', 0.0),
                        relevance_score=pattern_data.get('significance_score', 0.0),
                        source_cycle_id=cycle_id,
                        learning_mode=LearningMode.SYNTHETIC,
                        metadata={
                            'stage_name': stage_name,
                            'pattern_type': pattern_data.get('pattern_type'),
                            'stage_result': stage_result,
                            'extraction_timestamp': datetime.now(timezone.utc).isoformat()
                        }
                    )
                    insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to extract learning insights: {e}")
            return []

    async def _update_learning_metrics(self, insights: List[LearningInsight], stage_result: Dict[str, Any]):
        """Update learning metrics based on insights and stage results"""
        try:
            # Update basic metrics
            self.learning_metrics.total_insights += len(insights)
            
            # Calculate learning velocity
            if insights:
                avg_confidence = sum(insight.confidence_score for insight in insights) / len(insights)
                avg_relevance = sum(insight.relevance_score for insight in insights) / len(insights)
                self.learning_metrics.learning_velocity = (avg_confidence + avg_relevance) / 2
            
            # Calculate adaptation rate
            adaptation_indicators = 0
            total_indicators = 0
            
            for insight in insights:
                if insight.learning_mode in [LearningMode.ADAPTIVE, LearningMode.BREAKTHROUGH]:
                    adaptation_indicators += 1
                total_indicators += 1
            
            if total_indicators > 0:
                self.learning_metrics.adaptation_rate = adaptation_indicators / total_indicators
            
            # Calculate breakthrough frequency
            breakthrough_insights = [i for i in insights if i.learning_mode == LearningMode.BREAKTHROUGH]
            if insights:
                self.learning_metrics.breakthrough_frequency = len(breakthrough_insights) / len(insights)
            
            # Calculate wisdom accumulation
            wisdom_insights = [i for i in insights if i.learning_mode == LearningMode.META_LEARNING]
            if insights:
                self.learning_metrics.wisdom_accumulation = len(wisdom_insights) / len(insights)
            
            # Calculate synergy score
            synergy_indicators = 0
            for insight in insights:
                if insight.confidence_score > 0.7 and insight.relevance_score > 0.7:
                    synergy_indicators += 1
            
            if insights:
                self.learning_metrics.synergy_score = synergy_indicators / len(insights)
            
            # Calculate continuous improvement score
            improvement_insights = [i for i in insights if i.learning_mode == LearningMode.ADAPTIVE]
            if insights:
                self.learning_metrics.continuous_improvement_score = len(improvement_insights) / len(insights)
            
        except Exception as e:
            logger.error(f"Failed to update learning metrics: {e}")

    async def _should_adapt_learning(self, 
                                   integration: WorkflowLearningIntegration, 
                                   stage_result: Dict[str, Any]) -> bool:
        """Determine if learning process should adapt"""
        try:
            # Check adaptation threshold
            if stage_result.get('confidence_score', 0.0) < integration.adaptation_threshold:
                return True
            
            # Check for stagnation indicators
            if stage_result.get('stagnation_detected', False):
                return True
            
            # Check for breakthrough opportunities
            if stage_result.get('breakthrough_potential', 0.0) > self.breakthrough_threshold:
                return True
            
            # Check learning velocity
            if self.learning_metrics.learning_velocity < self.learning_velocity_target:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check adaptation needs: {e}")
            return False

    async def _adapt_learning_process(self, 
                                    integration: WorkflowLearningIntegration, 
                                    stage_result: Dict[str, Any]):
        """Adapt the learning process based on performance"""
        try:
            # Adjust learning mode based on performance
            if stage_result.get('confidence_score', 0.0) < integration.adaptation_threshold:
                # Switch to more exploratory mode
                integration.learning_mode = LearningMode.EXPLORATORY
                integration.cycle_type = CycleType.EXPLORATION
            elif stage_result.get('breakthrough_potential', 0.0) > self.breakthrough_threshold:
                # Switch to breakthrough mode
                integration.learning_mode = LearningMode.BREAKTHROUGH
                integration.cycle_type = CycleType.BREAKTHROUGH
            
            # Adjust integration level
            if self.learning_metrics.synergy_score > 0.8:
                # Increase integration level
                if integration.integration_level == IntegrationLevel.SURFACE:
                    integration.integration_level = IntegrationLevel.DEEP
                elif integration.integration_level == IntegrationLevel.DEEP:
                    integration.integration_level = IntegrationLevel.PERPETUAL
                elif integration.integration_level == IntegrationLevel.PERPETUAL:
                    integration.integration_level = IntegrationLevel.TRANSCENDENT
            
            # Adjust adaptation threshold
            if self.learning_metrics.adaptation_rate > 0.5:
                integration.adaptation_threshold *= 0.9  # Lower threshold for more adaptation
            else:
                integration.adaptation_threshold *= 1.1  # Raise threshold for less adaptation
            
            logger.info(f"Adapted learning process for {integration.workflow_stage}")
            
        except Exception as e:
            logger.error(f"Failed to adapt learning process: {e}")

    async def _generate_learning_feedback(self, 
                                        stage_result: Dict[str, Any], 
                                        insights: List[LearningInsight]) -> Optional[str]:
        """Generate feedback for the perpetual thinking engine"""
        try:
            if not insights:
                return None
            
            # Generate feedback based on insights
            feedback_parts = []
            
            # Add stage result summary
            if 'summary' in stage_result:
                feedback_parts.append(f"Stage Summary: {stage_result['summary']}")
            
            # Add key insights
            key_insights = [i for i in insights if i.relevance_score > 0.7]
            if key_insights:
                feedback_parts.append(f"Key Insights: {len(key_insights)} high-relevance insights generated")
                for insight in key_insights[:3]:  # Top 3 insights
                    feedback_parts.append(f"- {insight.content[:100]}...")
            
            # Add learning metrics
            feedback_parts.append(f"Learning Metrics: Velocity={self.learning_metrics.learning_velocity:.2f}, "
                                f"Adaptation={self.learning_metrics.adaptation_rate:.2f}, "
                                f"Breakthrough={self.learning_metrics.breakthrough_frequency:.2f}")
            
            # Add recommendations for next cycle
            if stage_result.get('next_cycle_recommendations'):
                feedback_parts.append(f"Next Cycle Recommendations: {stage_result['next_cycle_recommendations']}")
            
            return "\n".join(feedback_parts)
            
        except Exception as e:
            logger.error(f"Failed to generate learning feedback: {e}")
            return None

    async def _feed_back_to_perpetual_engine(self, cycle_id: str, feedback: str):
        """Feed learning feedback back to the perpetual thinking engine"""
        try:
            # This would integrate with the perpetual thinking engine's feedback mechanism
            # For now, we'll log the feedback
            logger.info(f"Feeding back to perpetual engine cycle {cycle_id}: {feedback[:200]}...")
            
            # In a full implementation, this would:
            # 1. Update the perpetual engine's learning parameters
            # 2. Influence the next cycle's input generation
            # 3. Adjust the engine's adaptation mechanisms
            
        except Exception as e:
            logger.error(f"Failed to feed back to perpetual engine: {e}")

    async def get_perpetual_learning_analytics(self, days_back: int = 30) -> Dict[str, Any]:
        """Get analytics for the perpetual learning system"""
        try:
            start_time = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            # Filter insights by time
            recent_insights = [i for i in self.learning_insights if i.created_at >= start_time]
            
            # Calculate analytics
            analytics = {
                'period_days': days_back,
                'learning_metrics': {
                    'total_insights': len(recent_insights),
                    'learning_velocity': self.learning_metrics.learning_velocity,
                    'adaptation_rate': self.learning_metrics.adaptation_rate,
                    'breakthrough_frequency': self.learning_metrics.breakthrough_frequency,
                    'wisdom_accumulation': self.learning_metrics.wisdom_accumulation,
                    'synergy_score': self.learning_metrics.synergy_score,
                    'continuous_improvement_score': self.learning_metrics.continuous_improvement_score
                },
                'insights_by_type': {},
                'insights_by_stage': {},
                'insights_by_learning_mode': {},
                'workflow_integrations': {
                    stage: integration.__dict__ 
                    for stage, integration in self.workflow_integrations.items()
                }
            }
            
            # Analyze insights by type
            for insight in recent_insights:
                insight_type = insight.insight_type
                if insight_type not in analytics['insights_by_type']:
                    analytics['insights_by_type'][insight_type] = 0
                analytics['insights_by_type'][insight_type] += 1
            
            # Analyze insights by stage
            for insight in recent_insights:
                stage = insight.metadata.get('stage_name', 'unknown')
                if stage not in analytics['insights_by_stage']:
                    analytics['insights_by_stage'][stage] = 0
                analytics['insights_by_stage'][stage] += 1
            
            # Analyze insights by learning mode
            for insight in recent_insights:
                mode = insight.learning_mode.value
                if mode not in analytics['insights_by_learning_mode']:
                    analytics['insights_by_learning_mode'][mode] = 0
                analytics['insights_by_learning_mode'][mode] += 1
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get perpetual learning analytics: {e}")
            return {"error": str(e)}

    async def stop_perpetual_learning(self, session_id: str):
        """Stop perpetual learning for a session"""
        try:
            # Stop perpetual thinking cycles
            # This would need to be implemented based on the perpetual engine's API
            
            # Clear session data
            self.learning_insights = [i for i in self.learning_insights if i.metadata.get('session_id') != session_id]
            
            logger.info(f"Stopped perpetual learning for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to stop perpetual learning: {e}")

    async def close(self):
        """Close database connections"""
        await self.engine.dispose()
        logger.info("Enhanced Perpetual Thinking Integration closed")

# Example usage
async def main():
    """Example usage of the enhanced perpetual thinking integration"""
    
    integration = EnhancedPerpetualThinkingIntegration(
        database_url="postgresql+asyncpg://user:password@localhost/cosmic_council",
        openai_api_key="your-openai-api-key",
        session_factory=None,  # Would be your actual session factory
        integration_config={
            'continuous_learning_enabled': True,
            'adaptation_threshold': 0.7,
            'learning_velocity_target': 0.5,
            'breakthrough_threshold': 0.9
        }
    )
    
    try:
        # Start perpetual workflow learning
        session_id = await integration.start_perpetual_workflow_learning(
            problem_id="test-problem-id",
            initial_context={
                'problem_statement': 'How can we improve the efficiency of our workflow system?',
                'priority': 'high',
                'complexity': 'medium'
            }
        )
        
        print(f"Started perpetual learning session: {session_id}")
        
        # Wait for some learning to occur
        await asyncio.sleep(10)
        
        # Get learning analytics
        analytics = await integration.get_perpetual_learning_analytics(30)
        print(f"Learning Analytics: {json.dumps(analytics, indent=2, default=str)}")
        
        # Stop learning
        await integration.stop_perpetual_learning(session_id)
        
    finally:
        await integration.close()

if __name__ == "__main__":
    asyncio.run(main())
