"""
Concrete implementations of specialized agents for each department.
Each agent is trained to do ONE specific task extremely well and participates
in the Agent Orchestrator supercharger supply chain that hands work off
from one specialist to the next. Large foundational models teach these
departments the patterns and behaviors they need; the agents then distill
that knowledge into leaner personas that can run locally when needed.
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from .hierarchical_enterprise import (
    SpecializedAgent, AgentSpecialization, TaskContext, AgentResult,
    AgentHandoff, HandoffReason
)
from ..integrations.llm_provider import BaseLLMProvider, LLMRequest, LLMMessage

logger = logging.getLogger(__name__)


class DataCollectorAgent(SpecializedAgent):
    """Specialized agent for collecting and gathering data"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, AgentSpecialization.DATA_COLLECTOR, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        """Collect data based on task requirements"""
        start_time = time.time()
        
        try:
            if self.llm_provider:
                prompt = f"""
                As a data collector, identify what data needs to be gathered for:
                Task: {context.task_description}
                Context: {context.input_data}
                
                Provide:
                1. Data sources to query
                2. Key information to collect
                3. Data collection strategy
                """
                
                request = LLMRequest(
                    messages=[
                        LLMMessage(role="system", content="You are a specialized data collection agent."),
                        LLMMessage(role="user", content=prompt)
                    ],
                    temperature=0.5
                )
                
                response = await self.llm_provider.generate(request)
                collected_data = {"strategy": response.content, "sources": []}
            else:
                collected_data = {"strategy": "Basic data collection", "sources": []}
            
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=True,
                output=collected_data,
                confidence=0.85,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Data collection failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0,
                handoff=self.should_handoff(context)
            )
    
    def should_handoff(self, context: TaskContext) -> Optional[AgentHandoff]:
        """Hand off if data validation is needed"""
        if "validate" in context.task_description.lower():
            return AgentHandoff(
                from_agent=self.agent_id,
                to_agent="validation_specialist",
                reason=HandoffReason.REQUIRES_SPECIALIST,
                context=context,
                handoff_data={"task_description": "Validate collected data", "input_data": context.input_data}
            )
        return None
    
    def get_handoff_targets(self) -> List[AgentSpecialization]:
        return [AgentSpecialization.VALIDATION_SPECIALIST, AgentSpecialization.LITERATURE_REVIEWER]


class TaskDecomposerAgent(SpecializedAgent):
    """Specialized agent for breaking down complex tasks into subtasks"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, AgentSpecialization.TASK_DECOMPOSER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        """Decompose task into subtasks"""
        start_time = time.time()
        
        try:
            if self.llm_provider:
                prompt = f"""
                Decompose this task into clear, actionable subtasks:
                Task: {context.task_description}
                
                Provide:
                1. List of subtasks in order
                2. Dependencies between subtasks
                3. Estimated effort for each
                """
                
                request = LLMRequest(
                    messages=[
                        LLMMessage(role="system", content="You are a specialized task decomposition agent."),
                        LLMMessage(role="user", content=prompt)
                    ],
                    temperature=0.4
                )
                
                response = await self.llm_provider.generate(request)
                decomposition = {"subtasks": response.content, "dependencies": []}
            else:
                decomposition = {"subtasks": ["Subtask 1", "Subtask 2"], "dependencies": []}
            
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=True,
                output=decomposition,
                confidence=0.9,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Task decomposition failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0
            )
    
    def should_handoff(self, context: TaskContext) -> Optional[AgentHandoff]:
        """Hand off to dependency mapper if dependencies need analysis"""
        if "dependency" in context.task_description.lower() or "dependency" in str(context.input_data).lower():
            return AgentHandoff(
                from_agent=self.agent_id,
                to_agent="dependency_mapper",
                reason=HandoffReason.REQUIRES_SPECIALIST,
                context=context,
                handoff_data={"task_description": "Map task dependencies", "input_data": context.input_data}
            )
        return None
    
    def get_handoff_targets(self) -> List[AgentSpecialization]:
        return [AgentSpecialization.DEPENDENCY_MAPPER, AgentSpecialization.TIMELINE_OPTIMIZER]


class PrototypeBuilderAgent(SpecializedAgent):
    """Specialized agent for building prototypes"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, AgentSpecialization.PROTOTYPE_BUILDER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        """Build a prototype based on requirements"""
        start_time = time.time()
        
        try:
            if self.llm_provider:
                prompt = f"""
                Build a prototype for:
                Requirements: {context.task_description}
                Input: {context.input_data}
                
                Provide:
                1. Prototype design
                2. Implementation approach
                3. Key features
                """
                
                request = LLMRequest(
                    messages=[
                        LLMMessage(role="system", content="You are a specialized prototype building agent."),
                        LLMMessage(role="user", content=prompt)
                    ],
                    temperature=0.7
                )
                
                response = await self.llm_provider.generate(request)
                prototype = {"design": response.content, "features": []}
            else:
                prototype = {"design": "Basic prototype", "features": ["Feature 1", "Feature 2"]}
            
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=True,
                output=prototype,
                confidence=0.8,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Prototype building failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0,
                handoff=self.should_handoff(context)
            )
    
    def should_handoff(self, context: TaskContext) -> Optional[AgentHandoff]:
        """Hand off to code generator if code is needed"""
        if "code" in context.task_description.lower() or "implement" in context.task_description.lower():
            return AgentHandoff(
                from_agent=self.agent_id,
                to_agent="code_generator",
                reason=HandoffReason.REQUIRES_SPECIALIST,
                context=context,
                handoff_data={"task_description": "Generate code for prototype", "input_data": context.input_data}
            )
        return None
    
    def get_handoff_targets(self) -> List[AgentSpecialization]:
        return [AgentSpecialization.CODE_GENERATOR, AgentSpecialization.TEST_WRITER]


class CostEstimatorAgent(SpecializedAgent):
    """Specialized agent for estimating costs"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, AgentSpecialization.COST_ESTIMATOR, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        """Estimate costs for a project or task"""
        start_time = time.time()
        
        try:
            if self.llm_provider:
                prompt = f"""
                Estimate costs for:
                Task: {context.task_description}
                Requirements: {context.input_data}
                
                Provide:
                1. Cost breakdown by category
                2. Estimated total cost
                3. Cost assumptions and risks
                """
                
                request = LLMRequest(
                    messages=[
                        LLMMessage(role="system", content="You are a specialized cost estimation agent."),
                        LLMMessage(role="user", content=prompt)
                    ],
                    temperature=0.3
                )
                
                response = await self.llm_provider.generate(request)
                estimate = {"breakdown": response.content, "total": 0}
            else:
                estimate = {"breakdown": "Basic cost estimate", "total": 10000}
            
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=True,
                output=estimate,
                confidence=0.75,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Cost estimation failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0
            )
    
    def should_handoff(self, context: TaskContext) -> Optional[AgentHandoff]:
        """Hand off to budget analyzer for detailed budget work"""
        if "budget" in context.task_description.lower():
            return AgentHandoff(
                from_agent=self.agent_id,
                to_agent="budget_analyzer",
                reason=HandoffReason.REQUIRES_SPECIALIST,
                context=context,
                handoff_data={"task_description": "Analyze budget", "input_data": context.input_data}
            )
        return None
    
    def get_handoff_targets(self) -> List[AgentSpecialization]:
        return [AgentSpecialization.BUDGET_ANALYZER, AgentSpecialization.ROI_CALCULATOR]


class MessageCrafterAgent(SpecializedAgent):
    """Specialized agent for crafting messages and communications"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, AgentSpecialization.MESSAGE_CRAFTER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        """Craft a message for communication"""
        start_time = time.time()
        
        try:
            if self.llm_provider:
                prompt = f"""
                Craft a message for:
                Purpose: {context.task_description}
                Audience: {context.input_data.get('audience', 'general')}
                Key points: {context.input_data.get('key_points', [])}
                
                Provide:
                1. Main message
                2. Supporting points
                3. Call to action
                """
                
                request = LLMRequest(
                    messages=[
                        LLMMessage(role="system", content="You are a specialized message crafting agent."),
                        LLMMessage(role="user", content=prompt)
                    ],
                    temperature=0.8
                )
                
                response = await self.llm_provider.generate(request)
                message = {"content": response.content, "tone": "professional"}
            else:
                message = {"content": "Sample message", "tone": "professional"}
            
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=True,
                output=message,
                confidence=0.85,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Message crafting failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0
            )
    
    def should_handoff(self, context: TaskContext) -> Optional[AgentHandoff]:
        """Hand off to channel optimizer for distribution"""
        if "channel" in context.task_description.lower() or "distribute" in context.task_description.lower():
            return AgentHandoff(
                from_agent=self.agent_id,
                to_agent="channel_optimizer",
                reason=HandoffReason.REQUIRES_SPECIALIST,
                context=context,
                handoff_data={"task_description": "Optimize message channels", "input_data": context.input_data}
            )
        return None
    
    def get_handoff_targets(self) -> List[AgentSpecialization]:
        return [AgentSpecialization.CHANNEL_OPTIMIZER, AgentSpecialization.AUDIENCE_ANALYZER]


class FeedbackCollectorAgent(SpecializedAgent):
    """Specialized agent for collecting and analyzing feedback"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, AgentSpecialization.FEEDBACK_COLLECTOR, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        """Collect and analyze feedback"""
        start_time = time.time()
        
        try:
            if self.llm_provider:
                prompt = f"""
                Collect and analyze feedback for:
                Topic: {context.task_description}
                Current feedback: {context.input_data.get('feedback', [])}
                
                Provide:
                1. Feedback summary
                2. Key themes
                3. Action items
                """
                
                request = LLMRequest(
                    messages=[
                        LLMMessage(role="system", content="You are a specialized feedback collection agent."),
                        LLMMessage(role="user", content=prompt)
                    ],
                    temperature=0.5
                )
                
                response = await self.llm_provider.generate(request)
                feedback_analysis = {"summary": response.content, "themes": []}
            else:
                feedback_analysis = {"summary": "Feedback collected", "themes": ["Theme 1", "Theme 2"]}
            
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=True,
                output=feedback_analysis,
                confidence=0.8,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Feedback collection failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0,
                handoff=self.should_handoff(context)
            )
    
    def should_handoff(self, context: TaskContext) -> Optional[AgentHandoff]:
        """Hand off to improvement analyzer for action planning"""
        if "improve" in context.task_description.lower() or "action" in context.task_description.lower():
            return AgentHandoff(
                from_agent=self.agent_id,
                to_agent="improvement_analyzer",
                reason=HandoffReason.REQUIRES_SPECIALIST,
                context=context,
                handoff_data={"task_description": "Analyze improvements", "input_data": context.input_data}
            )
        return None
    
    def get_handoff_targets(self) -> List[AgentSpecialization]:
        return [AgentSpecialization.IMPROVEMENT_ANALYZER, AgentSpecialization.ISSUE_TRIAGER]


def create_specialized_agent(
    specialization: AgentSpecialization,
    agent_id: str,
    llm_provider: Optional[BaseLLMProvider] = None,
    config: Optional[Dict[str, Any]] = None
) -> SpecializedAgent:
    """
    Factory function to create specialized agents.
    
    Args:
        specialization: The agent specialization type
        agent_id: Unique agent identifier
        llm_provider: Optional LLM provider for AI capabilities
        config: Agent configuration
        
    Returns:
        SpecializedAgent instance
    """
    agent_classes = {
        AgentSpecialization.DATA_COLLECTOR: DataCollectorAgent,
        AgentSpecialization.TASK_DECOMPOSER: TaskDecomposerAgent,
        AgentSpecialization.PROTOTYPE_BUILDER: PrototypeBuilderAgent,
        AgentSpecialization.COST_ESTIMATOR: CostEstimatorAgent,
        AgentSpecialization.MESSAGE_CRAFTER: MessageCrafterAgent,
        AgentSpecialization.FEEDBACK_COLLECTOR: FeedbackCollectorAgent,
    }
    
    agent_class = agent_classes.get(specialization)
    if not agent_class:
        raise ValueError(f"No implementation for specialization: {specialization.value}")
    
    return agent_class(agent_id, llm_provider, config)

