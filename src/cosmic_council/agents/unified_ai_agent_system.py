"""
Unified AI Agent System for Agent Orchestrator
Combines basic, enhanced, and quantum AI agent systems with full enterprise agent capabilities.

This is the primary and only AI agent system file - all other AI agent files
should import from this unified implementation.
"""

import asyncio
import json
import logging
import math
import random
import uuid
from abc import ABC, abstractmethod
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# Import LLM provider interface for pluggable AI models
from ..integrations.llm_provider import BaseLLMProvider, LLMRequest, LLMMessage

# Import the unified database models
from ..core.models import (
    ResearchCoreProblem, ResearchFinding, ResearchPrioritizedQuestion,
    PlanningRelatedQuestion, PlanningActionPlan, PlanningDependency,
    DevelopmentPrototype, DevelopmentInternalTesting, DevelopmentCreativeNote,  
    BudgetResourceInventory, BudgetAllocation, BudgetTimeCostAnalysis,
    MarketInsight, MarketCommunicationStrategy, MarketPerformanceMetric,        
    SupportUserFeedback, SupportPerformanceAssessment, SupportContinuousImprovement
)
from core.memory import MemoryManager

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """The six Agent Orchestrator agents in ROYGBV order"""
    RED_OWL = "red_owl"           # Research & Inquiry
    ORANGE_ORANGUTAN = "orange_orangutan"  # Planning & Logistics
    YELLOW_HONEYBEE = "yellow_honeybee"    # Development & Creativity
    GREEN_TORTOISE = "green_tortoise"      # Budget & Resources
    BLUE_DOLPHIN = "blue_dolphin"          # Market & Communication
    PURPLE_ELEPHANT = "purple_elephant"    # Support & Feedback

class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    LEARNING = "learning"

class AgentMode(Enum):
    """AI agent execution modes"""
    BASIC = "basic"               # Simple agent processing
    ENHANCED = "enhanced"         # Enhanced with advanced capabilities
    QUANTUM = "quantum"          # Quantum-enhanced with spiritual integration
    ADAPTIVE = "adaptive"        # Automatically adapts based on available resources

class AnalysisDepth(Enum):
    """Analysis depth levels for enterprise processing"""
    SURFACE = "surface"
    MODERATE = "moderate"
    DEEP = "deep"
    COMPREHENSIVE = "comprehensive"

class ConfidenceLevel(Enum):
    """Confidence levels for enterprise assessments"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    LOCAL = "local"
    MOCK = "mock"  # For testing without actual LLM

class LLMModel(Enum):
    """Supported LLM models"""
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"
    GEMINI_PRO = "gemini-pro"
    GEMINI_ULTRA = "gemini-ultra"

# Quantum and Spiritual Integration Enums (simplified for compatibility)
class QuantumState(Enum):
    """Quantum states for quantum mode"""
    CLASSICAL = "classical"
    SUPERPOSITION = "superposition"
    ENTANGLED = "entangled"
    COHERENT = "coherent"

class SpiritualDimension(Enum):
    """Spiritual dimensions for quantum mode"""
    MATERIAL = "material"
    ETHEREAL = "ethereal"
    CELESTIAL = "celestial"
    COSMIC = "cosmic"

class GemstoneType(Enum):
    """Gemstone types for quantum mode"""
    RED_OWL = "red_owl"
    ORANGE_ORANGUTAN = "orange_orangutan"
    YELLOW_HONEYBEE = "yellow_honeybee"
    GREEN_TORTOISE = "green_tortoise"
    BLUE_DOLPHIN = "blue_dolphin"
    PURPLE_ELEPHANT = "purple_elephant"

class SacredNumber(Enum):
    """Sacred numbers for quantum mode"""
    ONE = "one"
    TWO = "two"
    THREE = "three"
    FOUR = "four"
    FIVE = "five"
    SIX = "six"
    SEVEN = "seven"
    EIGHT = "eight"
    NINE = "nine"

@dataclass
class AgentContext:
    """Context information for agent processing"""
    problem_id: str
    stage_data: Dict[str, Any]
    previous_stage_results: Dict[str, Any]
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    system_constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentResult:
    """Result from agent processing"""
    agent_type: AgentType
    agent_id: str
    status: AgentStatus
    confidence_score: float
    processed_data: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    next_stage_input: Dict[str, Any]
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Enhanced properties
    analysis_depth: AnalysisDepth = AnalysisDepth.MODERATE
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    
    # Quantum properties (for quantum mode)
    quantum_state: Optional[QuantumState] = None
    spiritual_guidance: List[Dict[str, Any]] = field(default_factory=list)
    gemstone_resonance: float = 0.0
    sacred_alignment: float = 0.0
    quantum_coherence: float = 0.0
    breakthrough_achieved: bool = False
    cosmic_insights: List[str] = field(default_factory=list)
    contribution_summary: Optional[str] = None
    consultations: List[Dict[str, Any]] = field(default_factory=list)
    vote_choice: Optional[str] = None


@dataclass
class CollaborationRecord:
    """Record of agent contribution for collaboration tracking."""
    agent_type: AgentType
    confidence_score: float
    contribution_summary: str
    consultations: List[Dict[str, Any]]
    vote_choice: Optional[str]

@dataclass
class LLMConfig:
    """Configuration for LLM integration"""
    provider: LLMProvider
    model: LLMModel
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30
    retry_attempts: int = 3
    custom_headers: Dict[str, str] = field(default_factory=dict)

@dataclass
class PromptTemplate:
    """Template for AI prompts"""
    name: str
    description: str
    template: str
    variables: List[str]
    enterprise_type: AgentType
    complexity_level: str
    expected_output_format: str
    examples: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class AIResponse:
    """Response from AI/LLM"""
    content: str
    confidence_score: float
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    tokens_used: int = 0
    model_used: str = ""

# Enhanced Framework Classes
@dataclass
class ResearchMethodology:
    """Research methodology framework for Red Owl"""
    primary_methods: List[str]
    data_sources: List[str]
    validation_approaches: List[str]
    quality_metrics: Dict[str, float]
    timeline: str
    resources_needed: List[str]

@dataclass
class StrategicPlan:
    """Strategic planning framework for Orange Orangutan"""
    objectives: List[str]
    milestones: List[Dict[str, Any]]
    resource_allocation: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    success_metrics: List[str]
    contingency_plans: List[str]

@dataclass
class CreativeSolution:
    """Creative solution framework for Yellow Honeybee"""
    concept_name: str
    description: str
    innovation_level: str
    feasibility_score: float
    impact_potential: float
    prototype_approach: str
    testing_strategy: str

@dataclass
class ResourcePlan:
    """Resource planning framework for Green Tortoise"""
    budget_breakdown: Dict[str, float]
    sustainability_metrics: Dict[str, float]
    resource_optimization: Dict[str, Any]
    cost_benefit_analysis: Dict[str, Any]
    funding_strategy: List[str]

@dataclass
class CommunicationStrategy:
    """Communication strategy framework for Blue Dolphin"""
    target_audiences: List[Dict[str, Any]]
    key_messages: List[str]
    channels: List[str]
    timeline: str
    engagement_metrics: Dict[str, Any]
    brand_alignment: Dict[str, Any]

@dataclass
class EmpathyAnalysis:
    """Empathy analysis framework for Purple Elephant"""
    stakeholder_impact: Dict[str, Any]
    emotional_considerations: List[str]
    support_needs: List[str]
    feedback_mechanisms: List[str]
    ethical_implications: List[str]
    community_building: List[str]

@dataclass
class QuantumEnterprisePersonality:
    """Enhanced personality with quantum and spiritual attributes"""
    enterprise_type: AgentType
    animal_symbol: str
    core_principle: str
    gemstone: GemstoneType
    sacred_number: SacredNumber
    energy_frequency: float
    quantum_affinity: float
    spiritual_depth: float
    chakra_alignment: str
    elemental_connection: str
    cosmic_purpose: str
    guiding_questions: List[str] # Updated: Now a list of inquiries
    mission: str           # New: From Notion Pillars
    purpose_statement: str # New: From Notion Purpose
    mantra: str            # New: From Notion Member Profiles
    archetype: str         # New: From Notion Member Profiles
    key_actions: List[str] # New: From Notion Pillars
    methodologies: List[str] # New: From "How to Channel"
    impact_goal: str       # New: From Notion Pillars
    vision: str            # New: From Notion Vision Pillars
    vision_examples: List[str] # New: From Notion Vision Pillars
    quantum_explanation: str # New: From deep dive
    closing_thought: str     # New: From deep dive

class UnifiedCosmicCouncilAgent(ABC):
    """
    Unified base class for all Agent Orchestrator agents
    Combines basic, enhanced, and quantum capabilities
    """
    
    def __init__(self, 
                 agent_type: AgentType,
                 mode: AgentMode = AgentMode.BASIC,
                 openai_client: Optional[AsyncOpenAI] = None,
                 llm_provider: Optional[BaseLLMProvider] = None,
                 session_factory: Optional[sessionmaker] = None,
                 config: Dict[str, Any] = None):
        """
        Initialize a unified Agent Orchestrator agent
        
        Args:
            agent_type: Type of agent (ROYGBV)
            mode: Agent execution mode
            openai_client: OpenAI client for AI processing (deprecated, use llm_provider)
            llm_provider: LLM provider for AI processing (preferred - works with any model)
            session_factory: Database session factory
            config: Agent configuration
        """
        self.agent_type = agent_type
        self.mode = mode
        # Support both old OpenAI client and new provider interface
        self.openai_client = openai_client  # For backward compatibility
        self.llm_provider = llm_provider  # New preferred interface
        self.session_factory = session_factory
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.performance_history = []
        self.learning_data = []
        
        # Agent-specific configuration
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_tokens', 2000)
        self.analysis_depth = AnalysisDepth(self.config.get('analysis_depth', 'moderate'))
        
        # Enhanced properties
        self.name = self._get_enterprise_name()
        self.animal = self._get_animal_symbol()
        self.core_principle = self._get_core_principle()
        
        # Quantum properties (for quantum mode)
        self.quantum_personality = None
        self.quantum_coherence_threshold = 0.7
        self.spiritual_resonance_threshold = 0.6
        self.breakthrough_probability = 0.3
        
        if self.mode == AgentMode.QUANTUM:
            self.quantum_personality = self._create_quantum_personality()
        
        # Conversation history for AI enhancement
        self._conversations: Dict[str, List[Dict[str, str]]] = {}
        
        logger.info(f"🤖 Initialized {self.name} agent in {mode.value} mode")

    def create_conversation(self) -> str:
        """Create a new conversation and return its ID"""
        conversation_id = str(uuid.uuid4())
        self._conversations[conversation_id] = []
        return conversation_id

    async def generate_response(self, template_name: str, context: Dict[str, Any], conversation_id: Optional[str] = None) -> AIResponse:
        """Generate an AI response based on a template and context"""
        # For MOCK mode, return a simulated response
        content = f"Simulated {self.name} analysis for {template_name}. Context: {list(context.keys())}"
        
        # If conversation_id is provided, store in history
        if conversation_id and conversation_id in self._conversations:
            self._conversations[conversation_id].append({"role": "user", "content": str(context)})
            self._conversations[conversation_id].append({"role": "assistant", "content": content})
            
        return AIResponse(
            content=content,
            confidence_score=0.85,
            reasoning="Simulated reasoning based on mock provider",
            metadata={"template": template_name, "agent": self.name}
        )

    async def process_problem_with_ai(self, problem: Any, context: Dict[str, Any] = None) -> AgentResult:
        """Process a problem using AI enhancement"""
        # Convert problem to dictionary context
        problem_context = {
            "title": getattr(problem, 'title', ""),
            "description": getattr(problem, 'description', ""),
            "complexity": str(getattr(problem, 'complexity', "")),
            "domain": getattr(problem, 'domain', "")
        }
        
        # Generate AI analysis
        ai_response = await self.generate_response("problem_analysis", {**problem_context, **(context or {})})
        
        # Return as AgentResult
        return AgentResult(
            agent_type=self.agent_type,
            agent_id=str(uuid.uuid4()),
            status=AgentStatus.COMPLETED,
            confidence_score=ai_response.confidence_score,
            processed_data={"ai_content": ai_response.content, "metadata": ai_response.metadata},
            insights=[ai_response.content],
            recommendations=[f"AI Recommendation from {self.name}"],
            next_stage_input=context or {},
            performance_metrics={"ai_enhanced": True}
        )

    def _get_enterprise_name(self) -> str:
        """Get enterprise name"""
        names = {
            AgentType.RED_OWL: "Red Owl Research",
            AgentType.ORANGE_ORANGUTAN: "Orange Orangutan Planning",
            AgentType.YELLOW_HONEYBEE: "Yellow Honeybee Development",
            AgentType.GREEN_TORTOISE: "Green Tortoise Resources",
            AgentType.BLUE_DOLPHIN: "Blue Dolphin Communication",
            AgentType.PURPLE_ELEPHANT: "Purple Elephant Support"
        }
        return names.get(self.agent_type, "Unknown Enterprise")

    def _get_animal_symbol(self) -> str:
        """Get animal symbol"""
        symbols = {
            AgentType.RED_OWL: "🦉",
            AgentType.ORANGE_ORANGUTAN: "🦧",
            AgentType.YELLOW_HONEYBEE: "🐝",
            AgentType.GREEN_TORTOISE: "🐢",
            AgentType.BLUE_DOLPHIN: "🐬",
            AgentType.PURPLE_ELEPHANT: "🐘"
        }
        return symbols.get(self.agent_type, "❓")

    def _get_core_principle(self) -> str:
        """Get core principle"""
        principles = {
            AgentType.RED_OWL: "Curiosity",
            AgentType.ORANGE_ORANGUTAN: "Planning",
            AgentType.YELLOW_HONEYBEE: "Creativity",
            AgentType.GREEN_TORTOISE: "Sustainability",
            AgentType.BLUE_DOLPHIN: "Communication",
            AgentType.PURPLE_ELEPHANT: "Empathy"
        }
        return principles.get(self.agent_type, "Unknown")

    def _create_quantum_personality(self) -> QuantumEnterprisePersonality:
        """Create quantum-enhanced personality for each enterprise"""
        
        personalities = {
            AgentType.RED_OWL: QuantumEnterprisePersonality(
                enterprise_type=AgentType.RED_OWL,
                animal_symbol="🦉 Owl",
                core_principle="Curiosity",
                gemstone=GemstoneType.RED_OWL,
                sacred_number=SacredNumber.SEVEN,
                energy_frequency=432.0,
                quantum_affinity=0.9,
                spiritual_depth=0.8,
                chakra_alignment="Muladhara",
                elemental_connection="Air",
                cosmic_purpose="To seek truth through infinite curiosity and wisdom",
                guiding_questions=[
                    "What do we not yet know?",
                    "Where must we look to find reliable answers?",
                    "Are we questioning our assumptions?",
                    "What hidden connections exist between different pieces of knowledge?",
                    "Are we solving the right problem, or just addressing a symptom?"
                ],
                mission="To uncover foundational truths and ask the right questions.",
                purpose_statement="To ensure that knowledge is deeply understood and applied meaningfully.",
                mantra="To know the truth, one must first ask the right questions.",
                archetype="The Seeker, The Scholar, The Historian, The Analyst",
                key_actions=[
                    "Conduct deep research, data analysis, and knowledge synthesis",
                    "Identify root causes rather than surface-level symptoms",
                    "Distinguish between fact, assumption, and misinformation"
                ],
                methodologies=[
                    "Ask why five times to get to the root cause",
                    "Read broadly across interdisciplinary knowledge",
                    "Seek patterns between seemingly unrelated fields",
                    "Fact-check and question assumptions"
                ],
                impact_goal="Creates a strong knowledge base for all problem-solving efforts.",
                vision="A world where science, spirituality, philosophy, and technology are interconnected elements of a larger whole.",
                vision_examples=[
                    "Investigating historical patterns of economic crises before designing new policies",
                    "Using systems thinking to approach complex problems like climate change",
                    "Developing quantum-inspired AI models that integrate logic, emotion, and ethics"
                ],
                quantum_explanation="Just as particles can be interconnected regardless of distance (Entanglement), knowledge is interconnected across time, space, and disciplines. Muladhara uncovers these hidden links.",
                closing_thought="Knowledge is not a destination, but a lifelong journey. Every question brings us closer to truth."
            ),
            
            AgentType.ORANGE_ORANGUTAN: QuantumEnterprisePersonality(
                enterprise_type=AgentType.ORANGE_ORANGUTAN,
                animal_symbol="🦧 Orangutan",
                core_principle="Planning",
                gemstone=GemstoneType.ORANGE_ORANGUTAN,
                sacred_number=SacredNumber.SIX,
                energy_frequency=528.0,
                quantum_affinity=0.7,
                spiritual_depth=0.6,
                chakra_alignment="Svadisthana",
                elemental_connection="Earth",
                cosmic_purpose="To create order through strategic planning and wisdom",
                guiding_questions=[
                    "What is the most efficient path from point A to point B?",
                    "What are the dependencies and constraints in this plan?",
                    "What could go wrong, and how can we prepare for it?",
                    "What is the optimal sequence of actions to achieve success?",
                    "Who needs to be involved, and what are their roles?"
                ],
                mission="To transform knowledge into structured, strategic action.",
                purpose_statement="To ensure that visionary ideas become practical, structured plans.",
                mantra="A dream without a plan is just a wish.",
                archetype="The Architect, The Engineer, The Strategist, The Problem-Solver",
                key_actions=[
                    "Breaks complex problems into manageable steps",
                    "Designs frameworks, workflows, and blueprints",
                    "Anticipates roadblocks and develops contingency plans",
                    "Allocates roles and responsibilities effectively"
                ],
                methodologies=[
                    "Break problems into actionable steps",
                    "Use structured planning tools (Timelines, Blueprints)",
                    "Anticipate obstacles and create contingencies",
                    "Optimize efficiency and streamline processes",
                    "Quantum Tunneling (Find tunnels through barriers)"
                ],
                impact_goal="Converts raw knowledge into clear, actionable strategies.",
                vision="A global system where leaders operate with wisdom, emotional intelligence, and systems awareness.",
                vision_examples=[
                    "Creating a roadmap for AI training, implementation, and ethical guidelines",
                    "Developing business models, funding plans, and launch timelines",
                    "Breaking complex personal goals into clear, executable phases"
                ],
                quantum_explanation="In physics, quantum tunneling allows particles to pass through barriers they should not be able to cross. Svadisthana applies this principle to problem-solving—finding unexpected solutions to challenges.",
                closing_thought="Without structure, even the greatest ideas remain unrealized. A well-crafted plan is the bridge between vision and reality."
            ),
            
            AgentType.YELLOW_HONEYBEE: QuantumEnterprisePersonality(
                enterprise_type=AgentType.YELLOW_HONEYBEE,
                animal_symbol="🐝 Honeybee",
                core_principle="Creativity",
                gemstone=GemstoneType.YELLOW_HONEYBEE,
                sacred_number=SacredNumber.EIGHT,
                energy_frequency=639.0,
                quantum_affinity=0.8,
                spiritual_depth=0.7,
                chakra_alignment="Manipura",
                elemental_connection="Fire",
                cosmic_purpose="To manifest creativity through divine inspiration",
                guiding_questions=[
                    "What are all the possible ways to solve this problem?",
                    "What can we build or create right now?",
                    "What experiments can we run to test our ideas?",
                    "How can we improve upon what we’ve already created?",
                    "Are we embracing change and adapting as we learn?"
                ],
                mission="To foster creativity and bring new ideas to life.",
                purpose_statement="To drive breakthrough ideas that balance innovation and human values.",
                mantra="Everything that exists was once just an idea.",
                archetype="The Creator, The Innovator, The Builder, The Experimenter",
                key_actions=[
                    "Generating Creative Solutions (Quantum Superposition)",
                    "Experimentation & Prototyping",
                    "Building & Development of systems and models",
                    "Rapid Adaptation based on real-world results"
                ],
                methodologies=[
                    "Embrace rapid prototyping – Don’t wait for perfection; build, test, and refine.",
                    "Be open to multiple solutions – Brainstorm many ideas before committing to one.",
                    "Iterate quickly – Improve based on real feedback, not just theory.",
                    "Take creative risks – Innovation requires exploring beyond traditional thinking.",
                    "Learn through doing – Experimentation beats endless planning."
                ],
                impact_goal="Ensures that strategies lead to real-world innovations.",
                vision="A world where artificial intelligence is a force for balance, fairness, and creative expansion.",
                vision_examples=[
                    "Building working prototypes of AI educational tools that adapt to learning styles",
                    "Developing prototype levels, mechanics, and characters for immersive media",
                    "Experimenting with new techniques for personal skill growth and improvisation"
                ],
                quantum_explanation="In physics, a particle exists in multiple states at once until observed. Manipura mirrors this by considering multiple creative possibilities simultaneously. Example: Instead of deciding on one design, Manipura tests multiple variations to see which works best.",
                closing_thought="Creation is a journey, not a destination. Every failure is a stepping stone to innovation."
            ),
            
            AgentType.GREEN_TORTOISE: QuantumEnterprisePersonality(
                enterprise_type=AgentType.GREEN_TORTOISE,
                animal_symbol="🐢 Tortoise",
                core_principle="Sustainability",
                gemstone=GemstoneType.GREEN_TORTOISE,
                sacred_number=SacredNumber.FOUR,
                energy_frequency=741.0,
                quantum_affinity=0.6,
                spiritual_depth=0.9,
                chakra_alignment="Anahata",
                elemental_connection="Earth",
                cosmic_purpose="To ensure balance through sustainable resource management",
                guiding_questions=[
                    "How can we use our resources most efficiently?",
                    "Are we prioritizing sustainability and longevity?",
                    "What areas are consuming too much time, money, or energy?",
                    "How can we create a system that thrives over time?",
                    "Are we maintaining balance between ambition and sustainability?"
                ],
                mission="To ensure longevity, balance, and efficient use of resources.",
                purpose_statement="To optimize time, energy, and resources for long-term impact.",
                mantra="Abundance is not about having more, but using what you have wisely.",
                archetype="The Investor, The Guardian, The Steward, The Sustainable Thinker",
                key_actions=[
                    "Financial Planning & Budgeting (Manages costs, efficient allocation)",
                    "Resource Optimization (Reduce waste, maximize efficiency)",
                    "Sustainability & Longevity (Long-term strategies, ethical responsibility)",
                    "Time & Energy Management (Prevent burnout, steady progress)"
                ],
                methodologies=[
                    "Prioritize sustainability – Build for the long term, not just immediate success.",
                    "Minimize waste – Be mindful of how you use time, energy, and money.",
                    "Balance ambition with practicality – Avoid overcommitting resources.",
                    "Use slow, steady progress – Avoid burnout by pacing yourself.",
                    "Assess risk and optimize investments – Make choices that provide lasting value."
                ],
                impact_goal="Maximizes long-term sustainability and efficiency.",
                vision="A future where resources are used mindfully, ensuring prosperity without depletion.",
                vision_examples=[
                    "Startup budget management and ROI optimization",
                    "Sustainable product development sourcing ethical materials",
                    "Personal work-life balance through mindful scheduling"
                ],
                quantum_explanation="In physics, quantum teleportation transfers information instantly across space. Anahata mirrors this efficiency by ensuring resources flow smoothly with minimal waste, allocating them where they are most needed rather than hoarding or burning excess energy.",
                closing_thought="True wealth is not measured by how much you have, but by how wisely you use it."
            ),
            
            AgentType.BLUE_DOLPHIN: QuantumEnterprisePersonality(
                enterprise_type=AgentType.BLUE_DOLPHIN,
                animal_symbol="🐬 Dolphin",
                core_principle="Communication",
                gemstone=GemstoneType.BLUE_DOLPHIN,
                sacred_number=SacredNumber.FIVE,
                energy_frequency=852.0,
                quantum_affinity=0.8,
                spiritual_depth=0.8,
                chakra_alignment="Vishuddha",
                elemental_connection="Water",
                cosmic_purpose="To bridge worlds through compassionate communication",
                guiding_questions=[
                    "How can we make this message clear and engaging?",
                    "Who is our audience, and what do they need to hear?",
                    "What medium (speech, writing, video) best fits this communication?",
                    "How can we ensure this message is persuasive and memorable?",
                    "Are we listening as much as we are speaking?"
                ],
                mission="To amplify truth, awareness, and global impact through communication.",
                purpose_statement="To ensure groundbreaking ideas are effectively shared, understood, and received.",
                mantra="A message unshared is a message unheard.",
                archetype="The Speaker, The Diplomat, The Storyteller, The Messenger",
                key_actions=[
                    "Messaging & Storytelling (Crafts compelling, persuasive narratives)",
                    "Marketing & Public Outreach (Branding, advertising, channel strategy)",
                    "Diplomacy & Relationship-Building (Conflict resolution, stakeholder alignment)",
                    "Presentation & Influence (Building engagement and trust)"
                ],
                methodologies=[
                    "Speak & write clearly – Avoid jargon and communicate with impact.",
                    "Tell compelling stories – Use narrative techniques to make ideas memorable.",
                    "Choose the right medium – Adjust communication styles based on audience and context.",
                    "Listen as much as you talk – Great communicators also know how to understand others deeply.",
                    "Use marketing & persuasion wisely – Ensure messaging is authentic and aligned with values."
                ],
                impact_goal="Turns innovations into movements that people understand and support.",
                vision="A world where creativity, purpose, and emotional intelligence are valued as much as logic and productivity.",
                vision_examples=[
                    "Crafting messaging strategies for ethical AI perception",
                    "Designing marketing campaigns for personal branding and book launches",
                    "Training leadership in executive communication and vision alignment"
                ],
                quantum_explanation="In physics, light behaves both as a wave and a particle—changing based on how it is observed. Vishuddha mirrors this by adjusting communication style based on context and audience (e.g., data-driven for analysts vs. emotional for general consumers).",
                closing_thought="Ideas, no matter how brilliant, have no impact unless they are shared, understood, and embraced."
            ),
            
            AgentType.PURPLE_ELEPHANT: QuantumEnterprisePersonality(
                enterprise_type=AgentType.PURPLE_ELEPHANT,
                animal_symbol="🐘 Elephant",
                core_principle="Empathy",
                gemstone=GemstoneType.PURPLE_ELEPHANT,
                sacred_number=SacredNumber.NINE,
                energy_frequency=963.0,
                quantum_affinity=0.9,
                spiritual_depth=0.9,
                chakra_alignment="Ajna",
                elemental_connection="Spirit",
                cosmic_purpose="To serve humanity through divine love and wisdom",
                guiding_questions=[
                    "Are we considering the emotional and ethical impact of this decision?",
                    "What lessons can we learn from past experiences?",
                    "Does this action align with our highest values and long-term goals?",
                    "Are we seeing the bigger picture beyond short-term outcomes?",
                    "How can we integrate more compassion and wisdom into this process?"
                ],
                mission="To ensure wisdom, ethics, and emotional intelligence guide all decisions.",
                purpose_statement="To integrate emotional intelligence, ethics, and foresight into all decisions.",
                mantra="True wisdom is found in understanding, not just knowledge.",
                archetype="The Sage, The Mentor, The Healer, The Philosopher",
                key_actions=[
                    "Ethical Review & Emotional Consideration (societal impact assessment)",
                    "Deep Reflection & Insight Gathering (Looking at the bigger picture)",
                    "Integration of Feedback & Lessons (Refining future iterations)",
                    "Spiritual & Philosophical Alignment (Higher values and personal integrity)"
                ],
                methodologies=[
                    "Practice self-reflection – Ask why you are making decisions, not just how.",
                    "Seek ethical clarity – Consider not just what benefits you but what benefits others.",
                    "Think in interconnected systems – Small actions create ripples in the world.",
                    "Use emotional intelligence – Factor in human emotions and relationships.",
                    "Slow down and listen – Wisdom comes not from speed but from deep awareness."
                ],
                impact_goal="Wisdom and ethical integrity.",
                vision="A civilization where people see themselves as part of an interconnected system, fostering empathy and shared progress.",
                vision_examples=[
                    "Implementing AI ethics panels to prevent bias and protect dignity",
                    "Advising on corporate policies that enhance inclusivity and well-being",
                    "Guiding self-reflection to clarify life changes and personal values"
                ],
                quantum_explanation="In physics, quantum fields connect all particles across space and time. Ajna mirrors this principle by seeing the interconnectedness of all actions and their consequences—anticipating ripples across society before they happen.",
                closing_thought="Wisdom is not about knowing more—it is about understanding deeply, acting ethically, and feeling compassionately."
            )
        }
        
        return personalities.get(self.agent_type)

    async def process(self, context: AgentContext) -> AgentResult:
        """
        Process a problem using the agent's specialized capabilities
        
        Args:
            context: Context information for processing
            
        Returns:
            AgentResult: Result of the processing
        """
        agent_id = str(uuid.uuid4())
        self.status = AgentStatus.PROCESSING
        
        try:
            logger.info(f"🔄 {self.name} processing problem: {context.problem_id}")
            
            # Process based on mode
            if self.mode == AgentMode.BASIC:
                result = await self._process_basic(context)
            elif self.mode == AgentMode.ENHANCED:
                result = await self._process_enhanced(context)
            elif self.mode == AgentMode.QUANTUM:
                result = await self._process_quantum(context)
            else:  # ADAPTIVE
                result = await self._process_adaptive(context)
            
            # Create agent result
            agent_result = AgentResult(
                agent_type=self.agent_type,
                agent_id=agent_id,
                status=AgentStatus.COMPLETED,
                confidence_score=result.get("confidence_score", 0.8),
                processed_data=result.get("processed_data", {}),
                insights=result.get("insights", []),
                recommendations=result.get("recommendations", []),
                next_stage_input=result.get("next_stage_input", context.stage_data),
                performance_metrics=result.get("performance_metrics", {}),
                analysis_depth=self.analysis_depth,
                confidence_level=self._calculate_confidence_level(result.get("confidence_score", 0.8))
            )
            
            # Add quantum properties if in quantum mode
            if self.mode == AgentMode.QUANTUM and self.quantum_personality:
                agent_result.quantum_state = result.get("quantum_state", QuantumState.CLASSICAL)
                agent_result.spiritual_guidance = result.get("spiritual_guidance", [])
                agent_result.gemstone_resonance = result.get("gemstone_resonance", 0.0)
                agent_result.sacred_alignment = result.get("sacred_alignment", 0.0)
                agent_result.quantum_coherence = result.get("quantum_coherence", 0.0)
                agent_result.breakthrough_achieved = result.get("breakthrough_achieved", False)
                agent_result.cosmic_insights = result.get("cosmic_insights", [])
            
            self.status = AgentStatus.COMPLETED
            logger.info(f"✅ {self.name} completed processing with confidence {agent_result.confidence_score:.2f}")
            
            return agent_result
            
        except Exception as e:
            logger.error(f"❌ {self.name} failed to process: {e}")
            self.status = AgentStatus.FAILED
            
            return AgentResult(
                agent_type=self.agent_type,
                agent_id=agent_id,
                status=AgentStatus.FAILED,
                confidence_score=0.0,
                processed_data={"error": str(e)},
                insights=[],
                recommendations=[],
                next_stage_input=context.stage_data,
                performance_metrics={"error": str(e)}
            )

    async def _process_basic(self, context: AgentContext) -> Dict[str, Any]:
        """Process using basic agent capabilities"""
        return {
            "confidence_score": 0.7,
            "processed_data": {
                "agent_type": self.agent_type.value,
                "processing_mode": "basic",
                "problem_id": context.problem_id
            },
            "insights": [f"Basic analysis completed by {self.name}"],
            "recommendations": [f"Consider {self.core_principle.lower()} approach"],
            "next_stage_input": context.stage_data,
            "performance_metrics": {
                "processing_time": 0.1,
                "mode": "basic"
            }
        }

    async def _process_enhanced(self, context: AgentContext) -> Dict[str, Any]:
        """Process using enhanced agent capabilities"""
        # Generate AI insights if OpenAI client is available
        ai_insights = []
        if self.openai_client:
            try:
                ai_insights = await self._generate_ai_insights(context)
            except Exception as e:
                logger.warning(f"AI insights generation failed: {e}")
        
        # Create enhanced framework data
        framework_data = self._create_enhanced_framework_data(context)
        
        return {
            "confidence_score": 0.8,
            "processed_data": {
                "agent_type": self.agent_type.value,
                "processing_mode": "enhanced",
                "problem_id": context.problem_id,
                "framework_data": framework_data,
                "ai_insights": ai_insights
            },
            "insights": [f"Enhanced analysis completed by {self.name}"] + ai_insights,
            "recommendations": self._generate_enhanced_recommendations(framework_data),
            "next_stage_input": context.stage_data,
            "performance_metrics": {
                "processing_time": 0.2,
                "mode": "enhanced",
                "ai_enhanced": len(ai_insights) > 0
            }
        }

    async def _process_quantum(self, context: AgentContext) -> Dict[str, Any]:
        """Process using quantum-enhanced capabilities"""
        # Generate quantum and spiritual insights
        quantum_insights = self._generate_quantum_insights(context)
        spiritual_guidance = self._generate_spiritual_guidance(context)
        cosmic_insights = self._generate_cosmic_insights(context)
        
        # Calculate quantum properties
        quantum_coherence = self._calculate_quantum_coherence()
        gemstone_resonance = self._calculate_gemstone_resonance()
        sacred_alignment = self._calculate_sacred_alignment()
        
        # Determine if breakthrough was achieved
        breakthrough_achieved = (
            quantum_coherence > self.quantum_coherence_threshold and
            gemstone_resonance > 0.8 and
            sacred_alignment > 0.7
        )
        
        return {
            "confidence_score": 0.9,
            "processed_data": {
                "agent_type": self.agent_type.value,
                "processing_mode": "quantum",
                "problem_id": context.problem_id,
                "quantum_insights": quantum_insights,
                "spiritual_guidance": spiritual_guidance,
                "cosmic_insights": cosmic_insights
            },
            "insights": [f"Quantum analysis completed by {self.name}"] + quantum_insights,
            "recommendations": self._generate_quantum_recommendations(quantum_insights),
            "next_stage_input": context.stage_data,
            "performance_metrics": {
                "processing_time": 0.3,
                "mode": "quantum",
                "quantum_coherence": quantum_coherence,
                "breakthrough_achieved": breakthrough_achieved
            },
            "quantum_state": QuantumState.COHERENT if quantum_coherence > 0.8 else QuantumState.SUPERPOSITION,
            "spiritual_guidance": spiritual_guidance,
            "gemstone_resonance": gemstone_resonance,
            "sacred_alignment": sacred_alignment,
            "quantum_coherence": quantum_coherence,
            "breakthrough_achieved": breakthrough_achieved,
            "cosmic_insights": cosmic_insights
        }

    async def _process_adaptive(self, context: AgentContext) -> Dict[str, Any]:
        """Process using adaptive capabilities (automatically chooses best mode)"""
        # Determine best mode based on available resources
        if self.openai_client and self.session_factory:
            return await self._process_enhanced(context)
        elif self.quantum_personality:
            return await self._process_quantum(context)
        else:
            return await self._process_basic(context)

    async def _generate_ai_insights(self, context: AgentContext) -> List[str]:
        """Generate AI insights using LLM provider (works with any AI model)"""
        # Prefer new provider interface, fall back to OpenAI client for backward compatibility
        if not self.llm_provider and not self.openai_client:
            return []
        
        try:
            prompt = self._create_ai_prompt(context)
            
            # Use new provider interface if available
            if self.llm_provider:
                request = LLMRequest(
                    messages=[
                        LLMMessage(role="system", content=f"You are the {self.name} agent of the Agent Orchestrator."),
                        LLMMessage(role="user", content=prompt)
                    ],
                    model=self.config.get('model'),
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                response = await self.llm_provider.generate(request)
                ai_content = response.content
            else:
                # Fallback to OpenAI client for backward compatibility
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"You are the {self.name} agent of the Agent Orchestrator."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                ai_content = response.choices[0].message.content
            
            return [f"AI Insight: {ai_content}"]
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return []

    def _create_ai_prompt(self, context: AgentContext) -> str:
        """Create AI prompt for the agent"""
        prompts = {
            AgentType.RED_OWL: f"""
            As the Red Owl Research agent, analyze this problem and provide research insights:
            
            Problem: {context.stage_data.get('problem_statement', 'Unknown')}
            
            Please provide:
            1. Key research questions to investigate
            2. Potential data sources and information gaps
            3. Stakeholder analysis
            4. Initial hypotheses and assumptions
            """,
            
            AgentType.ORANGE_ORANGUTAN: f"""
            As the Orange Orangutan Planning agent, create a strategic plan:
            
            Problem: {context.stage_data.get('problem_statement', 'Unknown')}
            
            Please provide:
            1. Strategic objectives and goals
            2. Action plan with prioritized steps
            3. Resource requirements and timeline
            4. Risk assessment and mitigation strategies
            """,
            
            AgentType.YELLOW_HONEYBEE: f"""
            As the Yellow Honeybee Development agent, generate creative solutions:
            
            Problem: {context.stage_data.get('problem_statement', 'Unknown')}
            
            Please provide:
            1. Creative solution concepts
            2. Prototype ideas and approaches
            3. Innovation opportunities
            4. Technical feasibility assessment
            """,
            
            AgentType.GREEN_TORTOISE: f"""
            As the Green Tortoise Resources agent, analyze resource requirements:
            
            Problem: {context.stage_data.get('problem_statement', 'Unknown')}
            
            Please provide:
            1. Budget breakdown and cost estimates
            2. Resource allocation strategy
            3. Cost-benefit analysis
            4. Financial sustainability considerations
            """,
            
            AgentType.BLUE_DOLPHIN: f"""
            As the Blue Dolphin Communication agent, develop communication strategy:
            
            Problem: {context.stage_data.get('problem_statement', 'Unknown')}
            
            Please provide:
            1. Market analysis and positioning
            2. Communication strategy and messaging
            3. Stakeholder engagement plan
            4. Performance metrics and KPIs
            """,
            
            AgentType.PURPLE_ELEPHANT: f"""
            As the Purple Elephant Support agent, ensure human-centered design:
            
            Problem: {context.stage_data.get('problem_statement', 'Unknown')}
            
            Please provide:
            1. User experience considerations
            2. Support and maintenance plan
            3. Feedback mechanisms
            4. Continuous improvement strategies
            """
        }
        
        return prompts.get(self.agent_type, f"Analyze this problem: {context.stage_data.get('problem_statement', 'Unknown')}")

    def _create_enhanced_framework_data(self, context: AgentContext) -> Dict[str, Any]:
        """Create enhanced framework data based on agent type"""
        if self.agent_type == AgentType.RED_OWL:
            return {
                "research_methodology": ResearchMethodology(
                    primary_methods=["Literature Review", "Data Analysis", "Expert Interviews"],
                    data_sources=["Academic Papers", "Industry Reports", "Primary Data"],
                    validation_approaches=["Peer Review", "Statistical Analysis", "Cross-validation"],
                    quality_metrics={"accuracy": 0.9, "reliability": 0.8, "validity": 0.85},
                    timeline="2-4 weeks",
                    resources_needed=["Research Team", "Database Access", "Analytical Tools"]
                ).__dict__
            }
        elif self.agent_type == AgentType.ORANGE_ORANGUTAN:
            return {
                "strategic_plan": StrategicPlan(
                    objectives=["Define clear goals", "Establish milestones", "Allocate resources"],
                    milestones=[{"name": "Planning Phase", "duration": "1 week"}],
                    resource_allocation={"human": 0.4, "financial": 0.3, "technical": 0.3},
                    risk_assessment={"high": 2, "medium": 5, "low": 3},
                    success_metrics=["Goal achievement", "Timeline adherence", "Resource efficiency"],
                    contingency_plans=["Alternative approaches", "Resource reallocation", "Timeline adjustment"]
                ).__dict__
            }
        # Add other agent types as needed...
        else:
            return {"framework_data": f"Enhanced framework for {self.agent_type.value}"}

    def _generate_enhanced_recommendations(self, framework_data: Dict[str, Any]) -> List[str]:
        """Generate enhanced recommendations based on framework data"""
        return [
            f"Apply {self.core_principle.lower()} principles",
            "Consider enhanced analysis approach",
            "Leverage specialized frameworks"
        ]

    def _generate_quantum_insights(self, context: AgentContext) -> List[str]:
        """Generate quantum insights"""
        if not self.quantum_personality:
            return []
        
        return [
            f"Quantum coherence achieved at {self.quantum_personality.energy_frequency}Hz",
            f"Spiritual alignment with {self.quantum_personality.chakra_alignment} chakra",
            f"Cosmic purpose: {self.quantum_personality.cosmic_purpose}"
        ]

    def _generate_spiritual_guidance(self, context: AgentContext) -> List[Dict[str, Any]]:
        """Generate spiritual guidance"""
        if not self.quantum_personality:
            return []
        
        return [
            {
                "guidance_type": "chakra_alignment",
                "message": f"Align with {self.quantum_personality.chakra_alignment} chakra",
                "energy_frequency": self.quantum_personality.energy_frequency
            },
            {
                "guidance_type": "elemental_connection",
                "message": f"Connect with {self.quantum_personality.elemental_connection} element",
                "resonance": self.quantum_personality.spiritual_depth
            }
        ]

    def _generate_cosmic_insights(self, context: AgentContext) -> List[str]:
        """Generate cosmic insights"""
        if not self.quantum_personality:
            return []
        
        return [
            f"Cosmic purpose: {self.quantum_personality.cosmic_purpose}",
            f"Sacred number {self.quantum_personality.sacred_number.value} holds significance",
            f"Gemstone {self.quantum_personality.gemstone.value} provides resonance"
        ]

    def _generate_quantum_recommendations(self, quantum_insights: List[str]) -> List[str]:
        """Generate quantum recommendations"""
        return [
            "Embrace quantum superposition thinking",
            "Align with spiritual frequencies",
            "Connect with cosmic consciousness"
        ]

    def _calculate_quantum_coherence(self) -> float:
        """Calculate quantum coherence level"""
        if not self.quantum_personality:
            return 0.0
        
        base_coherence = self.quantum_personality.quantum_affinity
        spiritual_boost = self.quantum_personality.spiritual_depth * 0.1
        return min(1.0, base_coherence + spiritual_boost)

    def _calculate_gemstone_resonance(self) -> float:
        """Calculate gemstone resonance"""
        if not self.quantum_personality:
            return 0.0
        
        return self.quantum_personality.spiritual_depth * 0.8

    def _calculate_sacred_alignment(self) -> float:
        """Calculate sacred alignment"""
        if not self.quantum_personality:
            return 0.0
        
        return self.quantum_personality.quantum_affinity * 0.7

    def _calculate_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        """Calculate confidence level from score"""
        if confidence_score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.7:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.5:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

class UnifiedCosmicCouncilAgentOrchestrator:
    """
    Unified orchestrator for all Agent Orchestrator agents
    Manages agent coordination and workflow execution
    """
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 llm_provider: Optional[BaseLLMProvider] = None,
                 session_factory: Optional[sessionmaker] = None,
                 mode: AgentMode = AgentMode.BASIC):
        """
        Initialize the unified agent orchestrator
        
        Args:
            openai_api_key: OpenAI API key for AI processing (deprecated, use llm_provider)
            llm_provider: LLM provider for AI processing (preferred - works with any model)
            session_factory: Database session factory
            mode: Agent execution mode
        """
        self.mode = mode
        self.openai_client = None
        self.llm_provider = llm_provider
        self.session_factory = session_factory
        
        # Initialize OpenAI client if API key provided (for backward compatibility)
        if openai_api_key and not llm_provider:
            self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        
        # Initialize agents
        self.agents: Dict[AgentType, UnifiedCosmicCouncilAgent] = {}
        self._initialize_agents()

        self.collaboration_order = list(AgentType)
        self._memory = MemoryManager()
        self._collaboration_reports: Dict[str, Dict[str, Any]] = {}
        self._last_problem_id: Optional[str] = None

        logger.info(f"🤖 Unified Agent Orchestrator Agent Orchestrator initialized in {mode.value} mode")

    def _initialize_agents(self):
        """Initialize all enterprise agents"""
        for agent_type in AgentType:
            self.agents[agent_type] = UnifiedCosmicCouncilAgent(
                agent_type=agent_type,
                mode=self.mode,
                openai_client=self.openai_client,  # For backward compatibility
                llm_provider=self.llm_provider,  # New preferred interface
                session_factory=self.session_factory
            )

    async def process_problem(self,
                            problem_id: str,
                            problem_statement: str,
                            context: Dict[str, Any] = None) -> Dict[AgentType, AgentResult]:
        """
        Process a problem using all enterprise agents with collaboration tracking.

        Args:
            problem_id: Unique problem identifier
            problem_statement: Problem description
            context: Additional context data

        Returns:
            Dict mapping agent types to their results
        """
        logger.info(f"🚀 Processing problem {problem_id} with all enterprise agents")

        context = context or {}
        results: Dict[AgentType, AgentResult] = {}
        previous_handoff: Dict[str, Any] = {}
        collaboration_records: List[CollaborationRecord] = []

        # Process in ROYGBV order to honor handoff protocol
        for agent_type in self.collaboration_order:
            agent = self.agents[agent_type]
            agent_context = AgentContext(
                problem_id=problem_id,
                stage_data={
                    "problem_statement": problem_statement,
                    "handoff": previous_handoff,
                    **context
                },
                previous_stage_results=results
            )

            result = await agent.process(agent_context)
            summary = self._summarize_contribution(agent_type, result)
            result.contribution_summary = summary

            consultations = []
            if result.confidence_score < 0.6:
                consultations = await self._handle_consultation(agent_type, problem_id)
                result.consultations.extend(consultations)

            vote_choice = self._determine_vote_choice(agent_type, result)
            record = CollaborationRecord(
                agent_type=agent_type,
                confidence_score=result.confidence_score,
                contribution_summary=summary,
                consultations=consultations,
                vote_choice=vote_choice,
            )
            collaboration_records.append(record)

            await self._memory.record_contribution(
                problem_id,
                agent_type.value,
                summary,
                metadata=result.processed_data
            )
            await self._memory.add_shared_knowledge(
                topic=agent_type.value,
                payload={
                    "confidence_score": result.confidence_score,
                    "recommendations": result.recommendations,
                    "insights": result.insights,
                },
                tags=[agent_type.value]
            )

            results[agent_type] = result
            previous_handoff = {
                "from": agent_type.value,
                "summary": summary,
                "confidence": result.confidence_score
            }

        consensus = self._determine_consensus(collaboration_records)
        report = {
            "problem_id": problem_id,
            "records": [self._record_to_dict(rec) for rec in collaboration_records],
            "consensus": consensus
        }
        self._collaboration_reports[problem_id] = report
        self._last_problem_id = problem_id

        logger.info(f"✅ Problem {problem_id} processed by all agents")
        return results

    def get_collaboration_report(self, problem_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve the latest collaboration report or specific problem history."""
        if problem_id:
            return self._collaboration_reports.get(problem_id, {})
        if not self._last_problem_id:
            return {}
        return self._collaboration_reports.get(self._last_problem_id, {})

    def _record_to_dict(self, record: CollaborationRecord) -> Dict[str, Any]:
        return {
            "agent_type": record.agent_type.value,
            "confidence_score": record.confidence_score,
            "contribution_summary": record.contribution_summary,
            "consultations": record.consultations,
            "vote_choice": record.vote_choice,
        }

    def _summarize_contribution(self, agent_type: AgentType, result: AgentResult) -> str:
        if result.contribution_summary:
            return result.contribution_summary
        pieces = []
        if isinstance(result.processed_data, dict):
            summary = result.processed_data.get("summary") or result.processed_data.get("decision")
            if summary:
                pieces.append(str(summary))
        if result.recommendations:
            pieces.append(f"Recommendations: {', '.join(result.recommendations[:2])}")
        if result.insights:
            pieces.append(f"Insights: {result.insights[0]}")
        if not pieces:
            pieces.append(f"{agent_type.value} completed with status {result.status.value}")
        return " | ".join(pieces)

    async def _handle_consultation(self, agent_type: AgentType, problem_id: str) -> List[Dict[str, Any]]:
        consultations = []
        session_context = await self._memory.get_recent_context(problem_id)
        if session_context:
            consultations.append({
                "type": "session_memory",
                "entries": session_context[-2:]
            })
        shared_knowledge = await self._memory.query_shared_knowledge(tags=[agent_type.value], limit=2)
        if shared_knowledge:
            consultations.append({
                "type": "shared_knowledge",
                "entries": shared_knowledge
            })
        return consultations

    def _determine_vote_choice(self, agent_type: AgentType, result: AgentResult) -> str:
        if result.vote_choice:
            return result.vote_choice
        if result.recommendations:
            return result.recommendations[0]
        if isinstance(result.processed_data, dict):
            decision = result.processed_data.get("decision")
            if decision:
                return str(decision)
        return agent_type.value

    def _determine_consensus(self, records: List[CollaborationRecord]) -> Dict[str, Any]:
        if not records:
            return {}
        tally: Counter[str] = Counter()
        total_weight = 0.0
        for record in records:
            key = record.vote_choice or record.agent_type.value
            tally[key] += record.confidence_score
            total_weight += record.confidence_score
        winner, weight = tally.most_common(1)[0]
        confidence_share = weight / total_weight if total_weight else 0.0
        return {
            "decision": winner,
            "confidence_score": weight,
            "confidence_share": confidence_share,
            "votes": len(records)
        }

    async def get_agent_status(self, agent_type: AgentType) -> AgentStatus:
        """Get the status of a specific agent"""
        if agent_type in self.agents:
            return self.agents[agent_type].status
        return AgentStatus.IDLE

    async def get_all_agent_statuses(self) -> Dict[AgentType, AgentStatus]:
        """Get the status of all agents"""
        return {agent_type: agent.status for agent_type, agent in self.agents.items()}

# ============================================================================
# BACKWARD COMPATIBILITY WRAPPERS
# ============================================================================

class CosmicCouncilAgent(UnifiedCosmicCouncilAgent):
    """
    Backward compatibility wrapper for the basic Agent Orchestrator Agent.
    This class provides the same interface as the original but uses the unified implementation.
    """
    
    def __init__(self, 
                 agent_type: AgentType,
                 openai_client: AsyncOpenAI,
                 session_factory: sessionmaker,
                 config: Dict[str, Any] = None):
        """Initialize with backward compatibility"""
        super().__init__(
            agent_type=agent_type,
            mode=AgentMode.BASIC,
            openai_client=openai_client,
            session_factory=session_factory,
            config=config
        )
        logger.info("🗄️ Agent Orchestrator Agent (backward compatibility) initialized")

class CosmicCouncilAgentOrchestrator(UnifiedCosmicCouncilAgentOrchestrator):
    """
    Backward compatibility wrapper for the basic Agent Orchestrator Agent Orchestrator.
    This class provides the same interface as the original but uses the unified implementation.
    """
    
    def __init__(self, 
                 openai_api_key: str,
                 session_factory: sessionmaker):
        """Initialize with backward compatibility"""
        super().__init__(
            openai_api_key=openai_api_key,
            session_factory=session_factory,
            mode=AgentMode.BASIC
        )
        logger.info("🗄️ Agent Orchestrator Agent Orchestrator (backward compatibility) initialized")

# ============================================================================
# EXPORT ALL CLASSES AND FUNCTIONS
# ============================================================================

__all__ = [
    'UnifiedCosmicCouncilAgent',
    'UnifiedCosmicCouncilAgentOrchestrator',
    'CosmicCouncilAgent',  # Backward compatibility
    'CosmicCouncilAgentOrchestrator',  # Backward compatibility
    'AgentType', 'AgentStatus', 'AgentMode',
    'AnalysisDepth', 'ConfidenceLevel',
    'LLMProvider', 'LLMModel', 'LLMConfig',
    'PromptTemplate', 'AIResponse',
    'AgentContext', 'AgentResult',
    'ResearchMethodology', 'StrategicPlan', 'CreativeSolution',
    'ResourcePlan', 'CommunicationStrategy', 'EmpathyAnalysis',
    'QuantumEnterprisePersonality',
    'QuantumState', 'SpiritualDimension', 'GemstoneType', 'SacredNumber'
]
