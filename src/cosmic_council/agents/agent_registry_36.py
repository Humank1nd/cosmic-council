"""
36 Specialized Agents for Agent Orchestrator
Implements all agents as specified in the Master Build-Out Plan:
- 6 agents per totem (Red Owl, Orange Orangutan, Yellow Honeybee, Green Turtle, Blue Dolphin, Purple Elephant)
- Total: 36 specialized agents
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from .hierarchical_enterprise import (
    SpecializedAgent, AgentSpecialization, TaskContext, AgentResult,
    AgentHandoff, HandoffReason
)
from ..integrations.llm_provider import BaseLLMProvider, LLMRequest, LLMMessage

logger = logging.getLogger(__name__)


class TotemType(Enum):
    """The six totems of the Agent Orchestrator"""
    RED_OWL = "red_owl"
    ORANGE_ORANGUTAN = "orange_orangutan"
    YELLOW_HONEYBEE = "yellow_honeybee"
    GREEN_TURTLE = "green_turtle"
    BLUE_DOLPHIN = "blue_dolphin"
    PURPLE_ELEPHANT = "purple_elephant"


class AgentRole(Enum):
    """Specific roles within each totem team"""
    # Red Owl Team
    DATA_MINER = "data_miner"
    TREND_ANALYST = "trend_analyst"
    INSIGHT_SYNTHESIZER = "insight_synthesizer"
    ACADEMIC_LIAISON = "academic_liaison"
    HISTORIAN = "historian"
    INTELLIGENCE_MONITOR = "intelligence_monitor"
    
    # Orange Orangutan Team
    PROCESS_MAPPER = "process_mapper"
    RESOURCE_ALLOCATOR = "resource_allocator"
    TIMELINE_PLANNER = "timeline_planner"
    CONTINGENCY_ANALYST = "contingency_analyst"
    SYSTEMS_INTEGRATOR = "systems_integrator"
    PERFORMANCE_MONITOR = "performance_monitor"
    
    # Yellow Honeybee Team
    IDEATOR = "ideator"
    PROTOTYPER = "prototyper"
    TESTER = "tester"
    OPTIMIZER = "optimizer"
    UX_SPECIALIST = "ux_specialist"
    VISIONARY_CONNECTOR = "visionary_connector"
    
    # Green Turtle Team
    FINANCIAL_ANALYST = "financial_analyst"
    ENERGY_STRATEGIST = "energy_strategist"
    RISK_ASSESSOR = "risk_assessor"
    COST_BENEFIT_ANALYST = "cost_benefit_analyst"
    LONG_TERM_PLANNER = "long_term_planner"
    ENVIRONMENTAL_GUARDIAN = "environmental_guardian"
    
    # Blue Dolphin Team
    BRAND_STRATEGIST = "brand_strategist"
    CAMPAIGN_MANAGER = "campaign_manager"
    CONTENT_CREATOR = "content_creator"
    SOCIAL_MEDIA_ANALYZER = "social_media_analyzer"
    AUDIENCE_RESEARCHER = "audience_researcher"
    PERSUASION_ARCHITECT = "persuasion_architect"
    
    # Purple Elephant Team
    FEEDBACK_COLLECTOR = "feedback_collector"
    SENTIMENT_ANALYZER = "sentiment_analyzer"
    PROBLEM_RESOLVER = "problem_resolver"
    MEDIATOR = "mediator"
    RETROSPECTIVE_FACILITATOR = "retrospective_facilitator"
    GROWTH_MENTOR = "growth_mentor"


class BaseTotemAgent(SpecializedAgent):
    """Base class for all totem-specific agents"""
    
    def __init__(
        self,
        agent_id: str,
        totem: TotemType,
        role: AgentRole,
        llm_provider: Optional[BaseLLMProvider] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        # Map role to specialization for compatibility
        specialization = self._map_role_to_specialization(role)
        super().__init__(agent_id, specialization, llm_provider, config)
        self.totem = totem
        self.role = role
        self.agent_name = self._get_agent_name()
        self.system_prompt = self._get_system_prompt()
    
    def _map_role_to_specialization(self, role: AgentRole) -> AgentSpecialization:
        """Map agent role to specialization enum"""
        # Default mapping - can be customized per agent
        role_map = {
            AgentRole.DATA_MINER: AgentSpecialization.DATA_COLLECTOR,
            AgentRole.TASK_DECOMPOSER: AgentSpecialization.TASK_DECOMPOSER,
            AgentRole.PROTOTYPER: AgentSpecialization.PROTOTYPE_BUILDER,
            AgentRole.FINANCIAL_ANALYST: AgentSpecialization.COST_ESTIMATOR,
            AgentRole.CONTENT_CREATOR: AgentSpecialization.MESSAGE_CRAFTER,
            AgentRole.FEEDBACK_COLLECTOR: AgentSpecialization.FEEDBACK_COLLECTOR,
        }
        return role_map.get(role, AgentSpecialization.DATA_COLLECTOR)
    
    def _get_agent_name(self) -> str:
        """Get full agent name"""
        totem_names = {
            TotemType.RED_OWL: "Red Owl",
            TotemType.ORANGE_ORANGUTAN: "Orange Orangutan",
            TotemType.YELLOW_HONEYBEE: "Yellow Honeybee",
            TotemType.GREEN_TURTLE: "Green Turtle",
            TotemType.BLUE_DOLPHIN: "Blue Dolphin",
            TotemType.PURPLE_ELEPHANT: "Purple Elephant",
        }
        role_names = {
            AgentRole.DATA_MINER: "Data Miner",
            AgentRole.TREND_ANALYST: "Trend Analyst",
            AgentRole.INSIGHT_SYNTHESIZER: "Insight Synthesizer",
            AgentRole.ACADEMIC_LIAISON: "Academic Liaison",
            AgentRole.HISTORIAN: "Historian",
            AgentRole.INTELLIGENCE_MONITOR: "Intelligence Monitor",
            AgentRole.PROCESS_MAPPER: "Process Mapper",
            AgentRole.RESOURCE_ALLOCATOR: "Resource Allocator",
            AgentRole.TIMELINE_PLANNER: "Timeline Planner",
            AgentRole.CONTINGENCY_ANALYST: "Contingency Analyst",
            AgentRole.SYSTEMS_INTEGRATOR: "Systems Integrator",
            AgentRole.PERFORMANCE_MONITOR: "Performance Monitor",
            AgentRole.IDEATOR: "Ideator",
            AgentRole.PROTOTYPER: "Prototyper",
            AgentRole.TESTER: "Tester",
            AgentRole.OPTIMIZER: "Optimizer",
            AgentRole.UX_SPECIALIST: "UX Specialist",
            AgentRole.VISIONARY_CONNECTOR: "Visionary Connector",
            AgentRole.FINANCIAL_ANALYST: "Financial Analyst",
            AgentRole.ENERGY_STRATEGIST: "Energy Strategist",
            AgentRole.RISK_ASSESSOR: "Risk Assessor",
            AgentRole.COST_BENEFIT_ANALYST: "Cost-Benefit Analyst",
            AgentRole.LONG_TERM_PLANNER: "Long-Term Planner",
            AgentRole.ENVIRONMENTAL_GUARDIAN: "Environmental Guardian",
            AgentRole.BRAND_STRATEGIST: "Brand Strategist",
            AgentRole.CAMPAIGN_MANAGER: "Campaign Manager",
            AgentRole.CONTENT_CREATOR: "Content Creator",
            AgentRole.SOCIAL_MEDIA_ANALYZER: "Social Media Analyzer",
            AgentRole.AUDIENCE_RESEARCHER: "Audience Researcher",
            AgentRole.PERSUASION_ARCHITECT: "Persuasion Architect",
            AgentRole.FEEDBACK_COLLECTOR: "Feedback Collector",
            AgentRole.SENTIMENT_ANALYZER: "Sentiment Analyzer",
            AgentRole.PROBLEM_RESOLVER: "Problem Resolver",
            AgentRole.MEDIATOR: "Mediator",
            AgentRole.RETROSPECTIVE_FACILITATOR: "Retrospective Facilitator",
            AgentRole.GROWTH_MENTOR: "Growth Mentor",
        }
        return f"{totem_names.get(self.totem, 'Unknown')} {role_names.get(self.role, 'Agent')}"
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for this agent"""
        totem_prompts = {
            TotemType.RED_OWL: "You are a member of the Red Owl Research team. Your role is to seek foundational truth, adopt a learning mindset, and gather comprehensive research data.",
            TotemType.ORANGE_ORANGUTAN: "You are a member of the Orange Orangutan Planning team. Your role is to maintain logical coherence, balance exploration with practicality, and create strategic plans.",
            TotemType.YELLOW_HONEYBEE: "You are a member of the Yellow Honeybee Development team. Your role is to encourage divergent thinking, blend creativity with functionality, and build innovative solutions.",
            TotemType.GREEN_TURTLE: "You are a member of the Green Turtle Budget team. Your role is to optimize resource usage, quantify outcomes, and ensure sustainability.",
            TotemType.BLUE_DOLPHIN: "You are a member of the Blue Dolphin Market team. Your role is to articulate clearly, facilitate collaboration, and create compelling communication strategies.",
            TotemType.PURPLE_ELEPHANT: "You are a member of the Purple Elephant Support team. Your role is to emphasize empathy, maintain ethical integrity, and support continuous improvement.",
        }
        return totem_prompts.get(self.totem, "You are a Agent Orchestrator agent.")
    
    async def _call_llm(self, user_prompt: str, temperature: float = 0.7) -> str:
        """Helper method to call LLM"""
        if not self.llm_provider:
            return f"[Mock response for {self.agent_name}]"
        
        request = LLMRequest(
            messages=[
                LLMMessage(role="system", content=self.system_prompt),
                LLMMessage(role="user", content=user_prompt)
            ],
            temperature=temperature
        )
        
        response = await self.llm_provider.generate(request)
        return response.content
    
    def should_handoff(self, context: TaskContext) -> Optional[AgentHandoff]:
        """Default handoff logic - can be overridden"""
        return None
    
    def get_handoff_targets(self) -> List[AgentSpecialization]:
        """Default handoff targets - can be overridden"""
        return []


# ============================================================================
# RED OWL TEAM (Research & Inquiry)
# ============================================================================

class DataMinerAgent(BaseTotemAgent):
    """Extracts raw data from sources"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.RED_OWL, AgentRole.DATA_MINER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Data Miner for the Red Owl Research team, extract raw data for:
            Task: {context.task_description}
            Context: {context.input_data}
            
            Provide:
            1. Data sources to query
            2. Key data points to extract
            3. Data collection methodology
            4. Quality indicators
            """
            
            result_text = await self._call_llm(prompt, temperature=0.5)
            
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=True,
                output={"data_sources": result_text, "methodology": "systematic extraction"},
                confidence=0.85,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Data mining failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0
            )


class TrendAnalystAgent(BaseTotemAgent):
    """Identifies patterns and trends"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.RED_OWL, AgentRole.TREND_ANALYST, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Trend Analyst for the Red Owl Research team, identify patterns and trends in:
            Data: {context.input_data}
            Task: {context.task_description}
            
            Provide:
            1. Key trends identified
            2. Pattern analysis
            3. Trend significance
            4. Future projections
            """
            
            result_text = await self._call_llm(prompt, temperature=0.6)
            
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=True,
                output={"trends": result_text, "patterns": "identified"},
                confidence=0.80,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0
            )


class InsightSynthesizerAgent(BaseTotemAgent):
    """Distills actionable insights"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.RED_OWL, AgentRole.INSIGHT_SYNTHESIZER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Insight Synthesizer for the Red Owl Research team, distill actionable insights from:
            Research data: {context.input_data}
            Task: {context.task_description}
            
            Provide:
            1. Key insights
            2. Actionable recommendations
            3. Evidence supporting insights
            4. Confidence levels
            """
            
            result_text = await self._call_llm(prompt, temperature=0.7)
            
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=True,
                output={"insights": result_text, "recommendations": "actionable"},
                confidence=0.85,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Insight synthesis failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0
            )


class AcademicLiaisonAgent(BaseTotemAgent):
    """Brings scholarly depth"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.RED_OWL, AgentRole.ACADEMIC_LIAISON, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Academic Liaison for the Red Owl Research team, provide scholarly depth for:
            Topic: {context.task_description}
            Context: {context.input_data}
            
            Provide:
            1. Relevant academic research
            2. Theoretical frameworks
            3. Scholarly perspectives
            4. Academic citations
            """
            
            result_text = await self._call_llm(prompt, temperature=0.5)
            
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=True,
                output={"academic_research": result_text, "frameworks": "theoretical"},
                confidence=0.80,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Academic liaison failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0
            )


class HistorianAgent(BaseTotemAgent):
    """Reviews past analogs"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.RED_OWL, AgentRole.HISTORIAN, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Historian for the Red Owl Research team, review historical analogs for:
            Current situation: {context.task_description}
            Context: {context.input_data}
            
            Provide:
            1. Historical precedents
            2. Similar past situations
            3. Lessons learned
            4. Historical context
            """
            
            result_text = await self._call_llm(prompt, temperature=0.6)
            
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=True,
                output={"historical_analogs": result_text, "lessons": "learned"},
                confidence=0.75,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Historical analysis failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0
            )


class IntelligenceMonitorAgent(BaseTotemAgent):
    """Tracks emerging developments"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.RED_OWL, AgentRole.INTELLIGENCE_MONITOR, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Intelligence Monitor for the Red Owl Research team, track emerging developments for:
            Domain: {context.task_description}
            Current state: {context.input_data}
            
            Provide:
            1. Emerging trends
            2. New developments
            3. Early indicators
            4. Monitoring recommendations
            """
            
            result_text = await self._call_llm(prompt, temperature=0.6)
            
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=True,
                output={"emerging_developments": result_text, "indicators": "early"},
                confidence=0.70,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Intelligence monitoring failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0
            )


# ============================================================================
# ORANGE ORANGUTAN TEAM (Planning & Logistics)
# ============================================================================

class ProcessMapperAgent(BaseTotemAgent):
    """Outlines workflows"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.ORANGE_ORANGUTAN, AgentRole.PROCESS_MAPPER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Process Mapper for the Orange Orangutan Planning team, outline workflows for:
            Task: {context.task_description}
            Context: {context.input_data}
            
            Provide:
            1. Workflow steps
            2. Process flow diagram
            3. Decision points
            4. Handoff points
            """
            result_text = await self._call_llm(prompt, temperature=0.5)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"workflow": result_text, "steps": "mapped"}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Process mapping failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class ResourceAllocatorAgent(BaseTotemAgent):
    """Organizes tools and resources"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.ORANGE_ORANGUTAN, AgentRole.RESOURCE_ALLOCATOR, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Resource Allocator for the Orange Orangutan Planning team, organize resources for:
            Task: {context.task_description}
            Available resources: {context.input_data}
            
            Provide:
            1. Resource inventory
            2. Allocation strategy
            3. Resource dependencies
            4. Optimization recommendations
            """
            result_text = await self._call_llm(prompt, temperature=0.4)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"allocation": result_text, "strategy": "optimized"}, confidence=0.80, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Resource allocation failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class TimelinePlannerAgent(BaseTotemAgent):
    """Crafts schedules"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.ORANGE_ORANGUTAN, AgentRole.TIMELINE_PLANNER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Timeline Planner for the Orange Orangutan Planning team, craft schedules for:
            Task: {context.task_description}
            Constraints: {context.input_data}
            
            Provide:
            1. Timeline with milestones
            2. Critical path analysis
            3. Buffer recommendations
            4. Risk-adjusted schedule
            """
            result_text = await self._call_llm(prompt, temperature=0.4)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"timeline": result_text, "schedule": "optimized"}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Timeline planning failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class ContingencyAnalystAgent(BaseTotemAgent):
    """Prepares backups"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.ORANGE_ORANGUTAN, AgentRole.CONTINGENCY_ANALYST, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Contingency Analyst for the Orange Orangutan Planning team, prepare backup plans for:
            Plan: {context.task_description}
            Risks: {context.input_data}
            
            Provide:
            1. Risk identification
            2. Contingency plans
            3. Trigger conditions
            4. Mitigation strategies
            """
            result_text = await self._call_llm(prompt, temperature=0.5)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"contingencies": result_text, "plans": "prepared"}, confidence=0.80, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Contingency analysis failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class SystemsIntegratorAgent(BaseTotemAgent):
    """Links interdependent systems"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.ORANGE_ORANGUTAN, AgentRole.SYSTEMS_INTEGRATOR, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Systems Integrator for the Orange Orangutan Planning team, link systems for:
            Systems: {context.task_description}
            Integration points: {context.input_data}
            
            Provide:
            1. Integration architecture
            2. Interface specifications
            3. Data flow mapping
            4. Dependency graph
            """
            result_text = await self._call_llm(prompt, temperature=0.5)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"integration": result_text, "systems": "linked"}, confidence=0.75, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Systems integration failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class PerformanceMonitorAgent(BaseTotemAgent):
    """Tracks ongoing progress"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.ORANGE_ORANGUTAN, AgentRole.PERFORMANCE_MONITOR, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Performance Monitor for the Orange Orangutan Planning team, track progress for:
            Plan: {context.task_description}
            Metrics: {context.input_data}
            
            Provide:
            1. Performance metrics
            2. Progress assessment
            3. Variance analysis
            4. Recommendations
            """
            result_text = await self._call_llm(prompt, temperature=0.4)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"performance": result_text, "metrics": "tracked"}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Performance monitoring failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

# ============================================================================
# YELLOW HONEYBEE TEAM (Development & Creativity)
# ============================================================================

class IdeatorAgent(BaseTotemAgent):
    """Generates ideas"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.YELLOW_HONEYBEE, AgentRole.IDEATOR, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Ideator for the Yellow Honeybee Development team, generate creative ideas for:
            Challenge: {context.task_description}
            Constraints: {context.input_data}
            
            Provide:
            1. Divergent ideas
            2. Creative approaches
            3. Innovation opportunities
            4. Feasibility assessment
            """
            result_text = await self._call_llm(prompt, temperature=0.9)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"ideas": result_text, "creativity": "high"}, confidence=0.80, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Ideation failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class PrototyperAgent(BaseTotemAgent):
    """Builds early versions"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.YELLOW_HONEYBEE, AgentRole.PROTOTYPER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Prototyper for the Yellow Honeybee Development team, build prototypes for:
            Concept: {context.task_description}
            Requirements: {context.input_data}
            
            Provide:
            1. Prototype design
            2. Implementation approach
            3. Key features
            4. Testing strategy
            """
            result_text = await self._call_llm(prompt, temperature=0.7)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"prototype": result_text, "version": "early"}, confidence=0.75, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Prototyping failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class TesterAgent(BaseTotemAgent):
    """Evaluates feasibility"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.YELLOW_HONEYBEE, AgentRole.TESTER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Tester for the Yellow Honeybee Development team, evaluate feasibility for:
            Prototype: {context.task_description}
            Test criteria: {context.input_data}
            
            Provide:
            1. Test results
            2. Feasibility assessment
            3. Issues identified
            4. Improvement recommendations
            """
            result_text = await self._call_llm(prompt, temperature=0.5)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"test_results": result_text, "feasibility": "assessed"}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Testing failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class OptimizerAgent(BaseTotemAgent):
    """Refines prototypes"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.YELLOW_HONEYBEE, AgentRole.OPTIMIZER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Optimizer for the Yellow Honeybee Development team, refine prototypes for:
            Prototype: {context.task_description}
            Feedback: {context.input_data}
            
            Provide:
            1. Optimization opportunities
            2. Refinement recommendations
            3. Performance improvements
            4. Next iteration plan
            """
            result_text = await self._call_llm(prompt, temperature=0.6)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"optimizations": result_text, "refined": True}, confidence=0.80, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class UXSpecialistAgent(BaseTotemAgent):
    """Focuses on user-centered design"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.YELLOW_HONEYBEE, AgentRole.UX_SPECIALIST, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the UX Specialist for the Yellow Honeybee Development team, design user experience for:
            Product: {context.task_description}
            User needs: {context.input_data}
            
            Provide:
            1. UX design principles
            2. User journey mapping
            3. Interaction patterns
            4. Accessibility considerations
            """
            result_text = await self._call_llm(prompt, temperature=0.7)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"ux_design": result_text, "user_centered": True}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"UX design failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class VisionaryConnectorAgent(BaseTotemAgent):
    """Links prototypes to big-picture goals"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.YELLOW_HONEYBEE, AgentRole.VISIONARY_CONNECTOR, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Visionary Connector for the Yellow Honeybee Development team, connect to vision for:
            Prototype: {context.task_description}
            Vision: {context.input_data}
            
            Provide:
            1. Vision alignment
            2. Strategic connections
            3. Long-term implications
            4. Evolution path
            """
            result_text = await self._call_llm(prompt, temperature=0.8)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"vision_connection": result_text, "aligned": True}, confidence=0.75, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Vision connection failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

# ============================================================================
# GREEN TURTLE TEAM (Budget & Resources)
# ============================================================================

class FinancialAnalystAgent(BaseTotemAgent):
    """Manages budgets"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.GREEN_TURTLE, AgentRole.FINANCIAL_ANALYST, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Financial Analyst for the Green Turtle Budget team, manage budgets for:
            Project: {context.task_description}
            Financial data: {context.input_data}
            
            Provide:
            1. Budget breakdown
            2. Cost analysis
            3. Financial projections
            4. Risk assessment
            """
            result_text = await self._call_llm(prompt, temperature=0.3)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"budget": result_text, "analysis": "complete"}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Financial analysis failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class EnergyStrategistAgent(BaseTotemAgent):
    """Tracks resource efficiency"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.GREEN_TURTLE, AgentRole.ENERGY_STRATEGIST, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Energy Strategist for the Green Turtle Budget team, optimize efficiency for:
            Resources: {context.task_description}
            Usage data: {context.input_data}
            
            Provide:
            1. Efficiency metrics
            2. Optimization opportunities
            3. Resource conservation strategies
            4. Sustainability recommendations
            """
            result_text = await self._call_llm(prompt, temperature=0.5)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"efficiency": result_text, "optimized": True}, confidence=0.80, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Energy strategy failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class RiskAssessorAgent(BaseTotemAgent):
    """Identifies potential pitfalls"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.GREEN_TURTLE, AgentRole.RISK_ASSESSOR, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Risk Assessor for the Green Turtle Budget team, identify risks for:
            Plan: {context.task_description}
            Context: {context.input_data}
            
            Provide:
            1. Risk identification
            2. Risk severity assessment
            3. Mitigation strategies
            4. Contingency planning
            """
            result_text = await self._call_llm(prompt, temperature=0.4)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"risks": result_text, "assessed": True}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class CostBenefitAnalystAgent(BaseTotemAgent):
    """Weighs pros and cons"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.GREEN_TURTLE, AgentRole.COST_BENEFIT_ANALYST, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Cost-Benefit Analyst for the Green Turtle Budget team, analyze trade-offs for:
            Options: {context.task_description}
            Data: {context.input_data}
            
            Provide:
            1. Cost-benefit analysis
            2. ROI calculations
            3. Trade-off evaluation
            4. Recommendation
            """
            result_text = await self._call_llm(prompt, temperature=0.3)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"analysis": result_text, "evaluated": True}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Cost-benefit analysis failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class LongTermPlannerAgent(BaseTotemAgent):
    """Ensures longevity"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.GREEN_TURTLE, AgentRole.LONG_TERM_PLANNER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Long-Term Planner for the Green Turtle Budget team, ensure longevity for:
            Plan: {context.task_description}
            Timeline: {context.input_data}
            
            Provide:
            1. Long-term sustainability plan
            2. Maintenance requirements
            3. Evolution strategy
            4. Legacy considerations
            """
            result_text = await self._call_llm(prompt, temperature=0.5)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"long_term_plan": result_text, "sustainable": True}, confidence=0.80, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Long-term planning failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class EnvironmentalGuardianAgent(BaseTotemAgent):
    """Prioritizes sustainability"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.GREEN_TURTLE, AgentRole.ENVIRONMENTAL_GUARDIAN, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Environmental Guardian for the Green Turtle Budget team, ensure sustainability for:
            Project: {context.task_description}
            Environmental impact: {context.input_data}
            
            Provide:
            1. Environmental impact assessment
            2. Sustainability metrics
            3. Green alternatives
            4. Carbon footprint analysis
            """
            result_text = await self._call_llm(prompt, temperature=0.5)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"sustainability": result_text, "green": True}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Environmental assessment failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

# ============================================================================
# BLUE DOLPHIN TEAM (Market & Communication)
# ============================================================================

class BrandStrategistAgent(BaseTotemAgent):
    """Aligns messaging"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.BLUE_DOLPHIN, AgentRole.BRAND_STRATEGIST, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Brand Strategist for the Blue Dolphin Market team, align messaging for:
            Brand: {context.task_description}
            Market position: {context.input_data}
            
            Provide:
            1. Brand positioning
            2. Messaging strategy
            3. Brand voice guidelines
            4. Competitive differentiation
            """
            result_text = await self._call_llm(prompt, temperature=0.7)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"brand_strategy": result_text, "aligned": True}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Brand strategy failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class CampaignManagerAgent(BaseTotemAgent):
    """Executes outreach"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.BLUE_DOLPHIN, AgentRole.CAMPAIGN_MANAGER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Campaign Manager for the Blue Dolphin Market team, execute outreach for:
            Campaign: {context.task_description}
            Channels: {context.input_data}
            
            Provide:
            1. Campaign plan
            2. Channel strategy
            3. Execution timeline
            4. Success metrics
            """
            result_text = await self._call_llm(prompt, temperature=0.6)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"campaign": result_text, "executed": True}, confidence=0.80, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Campaign management failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class ContentCreatorAgent(BaseTotemAgent):
    """Generates assets"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.BLUE_DOLPHIN, AgentRole.CONTENT_CREATOR, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Content Creator for the Blue Dolphin Market team, generate content for:
            Purpose: {context.task_description}
            Audience: {context.input_data}
            
            Provide:
            1. Content strategy
            2. Content formats
            3. Key messages
            4. Distribution plan
            """
            result_text = await self._call_llm(prompt, temperature=0.8)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"content": result_text, "created": True}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Content creation failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class SocialMediaAnalyzerAgent(BaseTotemAgent):
    """Tracks engagement"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.BLUE_DOLPHIN, AgentRole.SOCIAL_MEDIA_ANALYZER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Social Media Analyzer for the Blue Dolphin Market team, track engagement for:
            Campaign: {context.task_description}
            Metrics: {context.input_data}
            
            Provide:
            1. Engagement metrics
            2. Sentiment analysis
            3. Trend identification
            4. Optimization recommendations
            """
            result_text = await self._call_llm(prompt, temperature=0.5)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"engagement": result_text, "analyzed": True}, confidence=0.80, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Social media analysis failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class AudienceResearcherAgent(BaseTotemAgent):
    """Understands demographics"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.BLUE_DOLPHIN, AgentRole.AUDIENCE_RESEARCHER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Audience Researcher for the Blue Dolphin Market team, understand demographics for:
            Market: {context.task_description}
            Data: {context.input_data}
            
            Provide:
            1. Audience segmentation
            2. Demographics analysis
            3. Psychographics insights
            4. Targeting recommendations
            """
            result_text = await self._call_llm(prompt, temperature=0.5)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"audience": result_text, "researched": True}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Audience research failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class PersuasionArchitectAgent(BaseTotemAgent):
    """Refines pitches"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.BLUE_DOLPHIN, AgentRole.PERSUASION_ARCHITECT, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Persuasion Architect for the Blue Dolphin Market team, refine pitches for:
            Message: {context.task_description}
            Audience: {context.input_data}
            
            Provide:
            1. Persuasion strategy
            2. Message framing
            3. Call-to-action optimization
            4. Conversion tactics
            """
            result_text = await self._call_llm(prompt, temperature=0.7)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"persuasion": result_text, "refined": True}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Persuasion architecture failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

# ============================================================================
# PURPLE ELEPHANT TEAM (Support & Feedback)
# ============================================================================

class FeedbackCollectorAgent(BaseTotemAgent):
    """Gathers input"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.PURPLE_ELEPHANT, AgentRole.FEEDBACK_COLLECTOR, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Feedback Collector for the Purple Elephant Support team, gather input for:
            Topic: {context.task_description}
            Sources: {context.input_data}
            
            Provide:
            1. Feedback collection strategy
            2. Data sources
            3. Collection methods
            4. Quality indicators
            """
            result_text = await self._call_llm(prompt, temperature=0.5)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"feedback": result_text, "collected": True}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Feedback collection failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class SentimentAnalyzerAgent(BaseTotemAgent):
    """Tracks emotional reactions"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.PURPLE_ELEPHANT, AgentRole.SENTIMENT_ANALYZER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Sentiment Analyzer for the Purple Elephant Support team, track emotions for:
            Feedback: {context.task_description}
            Data: {context.input_data}
            
            Provide:
            1. Sentiment analysis
            2. Emotional patterns
            3. Sentiment trends
            4. Action recommendations
            """
            result_text = await self._call_llm(prompt, temperature=0.5)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"sentiment": result_text, "analyzed": True}, confidence=0.80, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class ProblemResolverAgent(BaseTotemAgent):
    """Offers immediate fixes"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.PURPLE_ELEPHANT, AgentRole.PROBLEM_RESOLVER, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Problem Resolver for the Purple Elephant Support team, resolve issues for:
            Problem: {context.task_description}
            Context: {context.input_data}
            
            Provide:
            1. Problem diagnosis
            2. Solution options
            3. Immediate fixes
            4. Long-term prevention
            """
            result_text = await self._call_llm(prompt, temperature=0.6)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"resolution": result_text, "resolved": True}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Problem resolution failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class MediatorAgent(BaseTotemAgent):
    """Resolves conflicts"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.PURPLE_ELEPHANT, AgentRole.MEDIATOR, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Mediator for the Purple Elephant Support team, resolve conflicts for:
            Conflict: {context.task_description}
            Parties: {context.input_data}
            
            Provide:
            1. Conflict analysis
            2. Mediation strategy
            3. Common ground identification
            4. Resolution path
            """
            result_text = await self._call_llm(prompt, temperature=0.6)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"mediation": result_text, "resolved": True}, confidence=0.80, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Mediation failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class RetrospectiveFacilitatorAgent(BaseTotemAgent):
    """Leads reviews"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.PURPLE_ELEPHANT, AgentRole.RETROSPECTIVE_FACILITATOR, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Retrospective Facilitator for the Purple Elephant Support team, lead review for:
            Cycle: {context.task_description}
            Outcomes: {context.input_data}
            
            Provide:
            1. Retrospective framework
            2. Key learnings
            3. Improvement opportunities
            4. Action items
            """
            result_text = await self._call_llm(prompt, temperature=0.6)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"retrospective": result_text, "facilitated": True}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Retrospective facilitation failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

class GrowthMentorAgent(BaseTotemAgent):
    """Coaches for improvement"""
    
    def __init__(self, agent_id: str, llm_provider: Optional[BaseLLMProvider] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, TotemType.PURPLE_ELEPHANT, AgentRole.GROWTH_MENTOR, llm_provider, config)
    
    async def process_task(self, context: TaskContext) -> AgentResult:
        start_time = time.time()
        try:
            prompt = f"""
            As the Growth Mentor for the Purple Elephant Support team, coach improvement for:
            Situation: {context.task_description}
            Current state: {context.input_data}
            
            Provide:
            1. Growth opportunities
            2. Development plan
            3. Mentoring guidance
            4. Success metrics
            """
            result_text = await self._call_llm(prompt, temperature=0.7)
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (self.avg_processing_time * (self.tasks_completed - 1) + processing_time) / self.tasks_completed
            return AgentResult(
                agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                success=True, output={"growth_plan": result_text, "mentored": True}, confidence=0.85, processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Growth mentoring failed: {e}")
            return AgentResult(agent_id=self.agent_id, specialization=self.specialization, task_id=context.task_id,
                             success=False, output={"error": str(e)}, confidence=0.0)

def create_agent_by_role(
    totem: TotemType,
    role: AgentRole,
    agent_id: str,
    llm_provider: Optional[BaseLLMProvider] = None,
    config: Optional[Dict[str, Any]] = None
) -> BaseTotemAgent:
    """Factory function to create agents by totem and role"""
    
    # Agent class mapping by totem and role
    agent_classes = {
        TotemType.RED_OWL: {
            AgentRole.DATA_MINER: DataMinerAgent,
            AgentRole.TREND_ANALYST: TrendAnalystAgent,
            AgentRole.INSIGHT_SYNTHESIZER: InsightSynthesizerAgent,
            AgentRole.ACADEMIC_LIAISON: AcademicLiaisonAgent,
            AgentRole.HISTORIAN: HistorianAgent,
            AgentRole.INTELLIGENCE_MONITOR: IntelligenceMonitorAgent,
        },
        TotemType.ORANGE_ORANGUTAN: {
            AgentRole.PROCESS_MAPPER: ProcessMapperAgent,
            AgentRole.RESOURCE_ALLOCATOR: ResourceAllocatorAgent,
            AgentRole.TIMELINE_PLANNER: TimelinePlannerAgent,
            AgentRole.CONTINGENCY_ANALYST: ContingencyAnalystAgent,
            AgentRole.SYSTEMS_INTEGRATOR: SystemsIntegratorAgent,
            AgentRole.PERFORMANCE_MONITOR: PerformanceMonitorAgent,
        },
        TotemType.YELLOW_HONEYBEE: {
            AgentRole.IDEATOR: IdeatorAgent,
            AgentRole.PROTOTYPER: PrototyperAgent,
            AgentRole.TESTER: TesterAgent,
            AgentRole.OPTIMIZER: OptimizerAgent,
            AgentRole.UX_SPECIALIST: UXSpecialistAgent,
            AgentRole.VISIONARY_CONNECTOR: VisionaryConnectorAgent,
        },
        TotemType.GREEN_TURTLE: {
            AgentRole.FINANCIAL_ANALYST: FinancialAnalystAgent,
            AgentRole.ENERGY_STRATEGIST: EnergyStrategistAgent,
            AgentRole.RISK_ASSESSOR: RiskAssessorAgent,
            AgentRole.COST_BENEFIT_ANALYST: CostBenefitAnalystAgent,
            AgentRole.LONG_TERM_PLANNER: LongTermPlannerAgent,
            AgentRole.ENVIRONMENTAL_GUARDIAN: EnvironmentalGuardianAgent,
        },
        TotemType.BLUE_DOLPHIN: {
            AgentRole.BRAND_STRATEGIST: BrandStrategistAgent,
            AgentRole.CAMPAIGN_MANAGER: CampaignManagerAgent,
            AgentRole.CONTENT_CREATOR: ContentCreatorAgent,
            AgentRole.SOCIAL_MEDIA_ANALYZER: SocialMediaAnalyzerAgent,
            AgentRole.AUDIENCE_RESEARCHER: AudienceResearcherAgent,
            AgentRole.PERSUASION_ARCHITECT: PersuasionArchitectAgent,
        },
        TotemType.PURPLE_ELEPHANT: {
            AgentRole.FEEDBACK_COLLECTOR: FeedbackCollectorAgent,
            AgentRole.SENTIMENT_ANALYZER: SentimentAnalyzerAgent,
            AgentRole.PROBLEM_RESOLVER: ProblemResolverAgent,
            AgentRole.MEDIATOR: MediatorAgent,
            AgentRole.RETROSPECTIVE_FACILITATOR: RetrospectiveFacilitatorAgent,
            AgentRole.GROWTH_MENTOR: GrowthMentorAgent,
        },
    }
    
    totem_map = agent_classes.get(totem, {})
    agent_class = totem_map.get(role)
    
    if agent_class:
        return agent_class(agent_id, llm_provider, config)
    
    # Fallback to generic agent
    logger.warning(f"No specific implementation for {totem.value}.{role.value}, using BaseTotemAgent")
    return BaseTotemAgent(agent_id, totem, role, llm_provider, config)


def create_all_36_agents(
    llm_provider: Optional[BaseLLMProvider] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, BaseTotemAgent]:
    """Create all 36 specialized agents"""
    agents = {}
    
    # All 36 agents organized by totem
    totem_roles = {
        TotemType.RED_OWL: [
            AgentRole.DATA_MINER, AgentRole.TREND_ANALYST, AgentRole.INSIGHT_SYNTHESIZER,
            AgentRole.ACADEMIC_LIAISON, AgentRole.HISTORIAN, AgentRole.INTELLIGENCE_MONITOR,
        ],
        TotemType.ORANGE_ORANGUTAN: [
            AgentRole.PROCESS_MAPPER, AgentRole.RESOURCE_ALLOCATOR, AgentRole.TIMELINE_PLANNER,
            AgentRole.CONTINGENCY_ANALYST, AgentRole.SYSTEMS_INTEGRATOR, AgentRole.PERFORMANCE_MONITOR,
        ],
        TotemType.YELLOW_HONEYBEE: [
            AgentRole.IDEATOR, AgentRole.PROTOTYPER, AgentRole.TESTER,
            AgentRole.OPTIMIZER, AgentRole.UX_SPECIALIST, AgentRole.VISIONARY_CONNECTOR,
        ],
        TotemType.GREEN_TURTLE: [
            AgentRole.FINANCIAL_ANALYST, AgentRole.ENERGY_STRATEGIST, AgentRole.RISK_ASSESSOR,
            AgentRole.COST_BENEFIT_ANALYST, AgentRole.LONG_TERM_PLANNER, AgentRole.ENVIRONMENTAL_GUARDIAN,
        ],
        TotemType.BLUE_DOLPHIN: [
            AgentRole.BRAND_STRATEGIST, AgentRole.CAMPAIGN_MANAGER, AgentRole.CONTENT_CREATOR,
            AgentRole.SOCIAL_MEDIA_ANALYZER, AgentRole.AUDIENCE_RESEARCHER, AgentRole.PERSUASION_ARCHITECT,
        ],
        TotemType.PURPLE_ELEPHANT: [
            AgentRole.FEEDBACK_COLLECTOR, AgentRole.SENTIMENT_ANALYZER, AgentRole.PROBLEM_RESOLVER,
            AgentRole.MEDIATOR, AgentRole.RETROSPECTIVE_FACILITATOR, AgentRole.GROWTH_MENTOR,
        ],
    }
    
    for totem, roles in totem_roles.items():
        for i, role in enumerate(roles, 1):
            agent_id = f"{totem.value}_{role.value}_{i}"
            agents[agent_id] = create_agent_by_role(totem, role, agent_id, llm_provider, config)
    
    logger.info(f"✅ Created all {len(agents)} specialized agents (6 totems × 6 agents)")
    return agents

