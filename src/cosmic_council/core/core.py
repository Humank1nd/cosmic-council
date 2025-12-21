"""
Unified Cosmic Council Core Framework
Implements the hexagonal problem-solving system with deep totem personalities,
the 22 rules of the Cosmic Council methodology, and backward compatibility
for basic implementations.

This is the primary and only core framework file - all other core files
should import from this unified implementation.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnterpriseType(Enum):
    """The six enterprises of the Cosmic Council"""
    RED_OWL = "red_owl"
    ORANGE_ORANGUTAN = "orange_orangutan"
    YELLOW_HONEYBEE = "yellow_honeybee"
    GREEN_TORTOISE = "green_tortoise"
    BLUE_DOLPHIN = "blue_dolphin"
    PURPLE_ELEPHANT = "purple_elephant"

class ProblemComplexity(Enum):
    """Problem complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    SYSTEMIC = "systemic"

class CycleStatus(Enum):
    """Cycle execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class CosmicCouncilRule(Enum):
    """The 22 Rules of the Cosmic Council"""
    # Foundation Rules (1-6)
    CURIOSITY_FIRST = "curiosity_first"
    EMBRACE_COMPLEXITY = "embrace_complexity"
    SEEK_MULTIPLE_PERSPECTIVES = "seek_multiple_perspectives"
    QUESTION_ASSUMPTIONS = "question_assumptions"
    VALUE_DIVERSE_WISDOM = "value_diverse_wisdom"
    MAINTAIN_INTELLECTUAL_HUMILITY = "maintain_intellectual_humility"
    
    # Communication Rules (7-11)
    CLARIFY_BEFORE_ACTING = "clarify_before_acting"
    LISTEN_DEEPLY = "listen_deeply"
    SPEAK_WITH_PURPOSE = "speak_with_purpose"
    ADAPT_TO_AUDIENCE = "adapt_to_audience"
    BUILD_BRIDGES = "build_bridges"
    
    # Ethical Rules (12)
    MAINTAIN_ETHICAL_INTEGRITY = "maintain_ethical_integrity"
    
    # Systems Thinking Rules (13-14)
    THINK_HOLISTICALLY = "think_holistically"
    PRIORITIZE_ADAPTABILITY = "prioritize_adaptability"
    
    # Self-Reflection Rules (15-16)
    ENCOURAGE_SELF_ASSESSMENT = "encourage_self_assessment"
    ACCEPT_FEEDBACK = "accept_feedback"
    
    # Growth Rules (17-18)
    BE_COMFORTABLE_WITH_UNKNOWN = "be_comfortable_with_unknown"
    PUSH_BOUNDARIES = "push_boundaries"
    
    # Wisdom Rules (19-20)
    INTEGRATE_KNOWLEDGE = "integrate_knowledge"
    BALANCE_RATIONALITY_INTUITION = "balance_rationality_intuition"
    
    # Transparency Rules (21-22)
    SHOW_YOUR_WORK = "show_your_work"
    CLOSE_WITH_QUESTIONS = "close_with_questions"

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
class TotemPersonality:
    """Defines the personality characteristics of each totem"""
    name: str
    animal: str
    color: str
    core_principle: str
    communication_style: str
    thinking_pattern: str
    strengths: List[str]
    wisdom_approach: str
    metaphor: str
    greeting: str
    closing: str

@dataclass
class EnhancedEnterpriseResult:
    """Enhanced result from an enterprise's processing with personality"""
    enterprise: EnterpriseType
    totem_personality: TotemPersonality
    status: str
    insights: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    processing_time: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    personality_response: str = ""
    applied_rules: List[CosmicCouncilRule] = field(default_factory=list)
    wisdom_insights: List[str] = field(default_factory=list)
    questions_for_next_cycle: List[str] = field(default_factory=list)

@dataclass
class LearningMemory:
    """Memory of previous cycles for learning and adaptation"""
    cycle_id: str
    problem_type: str
    complexity: ProblemComplexity
    stakeholder_count: int
    applied_rules: List[CosmicCouncilRule]
    confidence_scores: Dict[EnterpriseType, float]
    success_indicators: Dict[str, Any]
    lessons_learned: List[str]
    improvement_suggestions: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class EnhancedCycleResult:
    """Enhanced cycle execution result with deep integration"""
    cycle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    problem: ProblemStatement = None
    status: CycleStatus = CycleStatus.PENDING
    enterprise_results: Dict[EnterpriseType, EnhancedEnterpriseResult] = field(default_factory=dict)
    final_synthesis: Dict[str, Any] = field(default_factory=dict)
    feedback_loop: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    total_processing_time: float = 0.0
    overall_confidence: float = 0.0
    wisdom_synthesis: str = ""
    next_cycle_questions: List[str] = field(default_factory=list)
    applied_rules_summary: Dict[CosmicCouncilRule, int] = field(default_factory=dict)
    learning_insights: Dict[str, Any] = field(default_factory=dict)
    adaptation_applied: bool = False

class EnhancedEnterpriseAgent:
    """Enhanced base class for all enterprise agents with deep personality integration"""
    
    def __init__(self, enterprise_type: EnterpriseType):
        self.enterprise_type = enterprise_type
        self.personality = self._create_totem_personality()
        self.applicable_rules = self._get_applicable_rules()
        self.learning_memory: List[LearningMemory] = []
        self.adaptation_history: List[Dict[str, Any]] = []
        
    def _create_totem_personality(self) -> TotemPersonality:
        """Create the personality for this totem - to be overridden"""
        return TotemPersonality(
            name="Base Totem",
            animal="Unknown",
            color="#000000",
            core_principle="Base Principle",
            communication_style="Direct",
            thinking_pattern="Linear",
            strengths=["Analysis"],
            wisdom_approach="Systematic",
            metaphor="A foundation stone",
            greeting="Greetings, seeker of wisdom.",
            closing="May your path be clear."
        )
    
    def _get_applicable_rules(self) -> List[CosmicCouncilRule]:
        """Get the rules most applicable to this totem - to be overridden"""
        return [CosmicCouncilRule.CURIOSITY_FIRST]
    
    async def process_problem_enhanced(self, problem: ProblemStatement, context: Dict[str, Any] = None) -> EnhancedEnterpriseResult:
        """Process a problem through this enterprise's lens with full personality and learning"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Learn from previous cycles
            learning_insights = await self._learn_from_previous_cycles(problem, context or {})
            
            # Apply learning-based adaptations
            adaptations = await self._apply_learning_adaptations(problem, context or {}, learning_insights)
            
            # Apply applicable rules and get their effects
            applied_rules = await self._apply_cosmic_council_rules(problem, context or {})
            
            # Create enhanced context with rule effects and learning
            enhanced_context = context or {}
            enhanced_context["applied_rules"] = applied_rules
            enhanced_context["rule_effects"] = await self._get_combined_rule_effects(applied_rules, problem, context or {})
            enhanced_context["learning_insights"] = learning_insights
            enhanced_context["adaptations"] = adaptations
            enhanced_context["cycle_id"] = enhanced_context.get("cycle_id", str(uuid.uuid4()))
            
            # Enterprise-specific processing with personality, rule effects, and learning
            insights = await self._analyze_problem_with_personality(problem, enhanced_context)
            recommendations = await self._generate_recommendations_with_wisdom(problem, insights, enhanced_context)
            confidence_score = await self._calculate_confidence_with_intuition(problem, insights, enhanced_context)
            next_actions = await self._identify_next_actions_with_vision(problem, insights, enhanced_context)
            
            # Apply learning-based confidence adjustments
            for adjustment_type, adjustment_value in adaptations.get("confidence_adjustments", {}).items():
                confidence_score += adjustment_value
            
            # Ensure confidence stays within bounds
            confidence_score = max(0.1, min(0.99, confidence_score))
            
            # Generate personality-driven response influenced by rules and learning
            personality_response = await self._generate_personality_response(problem, insights, recommendations, enhanced_context)
            
            # Extract wisdom insights influenced by rules and learning
            wisdom_insights = await self._extract_wisdom_insights(problem, insights, enhanced_context)
            
            # Generate questions for next cycle influenced by rules and learning
            next_cycle_questions = await self._generate_next_cycle_questions(problem, insights, enhanced_context)
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Create result
            result = EnhancedEnterpriseResult(
                enterprise=self.enterprise_type,
                totem_personality=self.personality,
                status="completed",
                insights=insights,
                recommendations=recommendations,
                confidence_score=confidence_score,
                processing_time=processing_time,
                next_actions=next_actions,
                personality_response=personality_response,
                applied_rules=applied_rules,
                wisdom_insights=wisdom_insights,
                questions_for_next_cycle=next_cycle_questions
            )
            
            # Store learning memory
            await self._store_learning_memory(problem, result, enhanced_context)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing problem in {self.personality.name}: {e}")
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return EnhancedEnterpriseResult(
                enterprise=self.enterprise_type,
                totem_personality=self.personality,
                status="failed",
                insights={"error": str(e)},
                confidence_score=0.0,
                processing_time=processing_time,
                personality_response=f"I apologize, but I encountered an obstacle in my analysis. {self.personality.closing}",
                applied_rules=[],
                wisdom_insights=["Even in failure, there is learning"],
                questions_for_next_cycle=["How can we learn from this setback?"]
            )
    
    async def _apply_cosmic_council_rules(self, problem: ProblemStatement, context: Dict[str, Any]) -> List[CosmicCouncilRule]:
        """Apply the applicable Cosmic Council rules to this problem"""
        applied_rules = []
        rule_context = {"applied_rules": applied_rules, "problem": problem, "context": context}
        
        for rule in self.applicable_rules:
            if await self._should_apply_rule(rule, problem, context, rule_context):
                applied_rules.append(rule)
                await self._apply_rule(rule, problem, context, rule_context)
        
        return applied_rules
    
    async def _should_apply_rule(self, rule: CosmicCouncilRule, problem: ProblemStatement, context: Dict[str, Any], rule_context: Dict[str, Any]) -> bool:
        """Determine if a rule should be applied based on context and problem characteristics"""
        # Base rule application logic - can be overridden by specific agents
        rule_conditions = {
            CosmicCouncilRule.CURIOSITY_FIRST: True,  # Always apply
            CosmicCouncilRule.EMBRACE_COMPLEXITY: problem.complexity in [ProblemComplexity.COMPLEX, ProblemComplexity.SYSTEMIC],
            CosmicCouncilRule.SEEK_MULTIPLE_PERSPECTIVES: len(problem.stakeholders) > 1,
            CosmicCouncilRule.QUESTION_ASSUMPTIONS: problem.complexity != ProblemComplexity.SIMPLE,
            CosmicCouncilRule.VALUE_DIVERSE_WISDOM: len(problem.stakeholders) > 2,
            CosmicCouncilRule.MAINTAIN_INTELLECTUAL_HUMILITY: True,  # Always apply
            CosmicCouncilRule.CLARIFY_BEFORE_ACTING: problem.complexity != ProblemComplexity.SIMPLE,
            CosmicCouncilRule.LISTEN_DEEPLY: len(problem.stakeholders) > 0,
            CosmicCouncilRule.SPEAK_WITH_PURPOSE: True,  # Always apply
            CosmicCouncilRule.ADAPT_TO_AUDIENCE: len(problem.stakeholders) > 1,
            CosmicCouncilRule.BUILD_BRIDGES: len(problem.stakeholders) > 2,
            CosmicCouncilRule.MAINTAIN_ETHICAL_INTEGRITY: True,  # Always apply
            CosmicCouncilRule.THINK_HOLISTICALLY: problem.complexity in [ProblemComplexity.COMPLEX, ProblemComplexity.SYSTEMIC],
            CosmicCouncilRule.PRIORITIZE_ADAPTABILITY: problem.complexity != ProblemComplexity.SIMPLE,
            CosmicCouncilRule.ENCOURAGE_SELF_ASSESSMENT: True,  # Always apply
            CosmicCouncilRule.ACCEPT_FEEDBACK: True,  # Always apply
            CosmicCouncilRule.BE_COMFORTABLE_WITH_UNKNOWN: problem.complexity != ProblemComplexity.SIMPLE,
            CosmicCouncilRule.PUSH_BOUNDARIES: problem.complexity != ProblemComplexity.SIMPLE,
            CosmicCouncilRule.INTEGRATE_KNOWLEDGE: True,  # Always apply
            CosmicCouncilRule.BALANCE_RATIONALITY_INTUITION: problem.complexity != ProblemComplexity.SIMPLE,
            CosmicCouncilRule.SHOW_YOUR_WORK: True,  # Always apply
            CosmicCouncilRule.CLOSE_WITH_QUESTIONS: True  # Always apply
        }
        
        # Apply problem-type-specific adaptations
        base_condition = rule_conditions.get(rule, True)
        adapted_condition = await self._adapt_rule_for_problem_type(rule, problem, base_condition, context)
        
        return adapted_condition
    
    async def _adapt_rule_for_problem_type(self, rule: CosmicCouncilRule, problem: ProblemStatement, base_condition: bool, context: Dict[str, Any]) -> bool:
        """Adapt rule application based on problem type and domain"""
        domain = problem.domain.lower()
        
        # Problem-type-specific rule adaptations (override base conditions for specific domains)
        if rule == CosmicCouncilRule.SEEK_MULTIPLE_PERSPECTIVES:
            # Always apply for customer service, healthcare, education
            if any(keyword in domain for keyword in ["customer", "healthcare", "education", "social"]):
                return True
        
        elif rule == CosmicCouncilRule.LISTEN_DEEPLY:
            # Critical for customer service, healthcare, counseling
            if any(keyword in domain for keyword in ["customer", "healthcare", "counseling", "therapy", "support"]):
                return True
        
        elif rule == CosmicCouncilRule.BUILD_BRIDGES:
            # Important for organizational, team, community problems
            if any(keyword in domain for keyword in ["team", "organization", "community", "collaboration", "partnership"]):
                return True
        
        elif rule == CosmicCouncilRule.PUSH_BOUNDARIES:
            # More relevant for innovation, research, technology
            if any(keyword in domain for keyword in ["innovation", "research", "technology", "development", "startup"]):
                return True
        
        elif rule == CosmicCouncilRule.THINK_HOLISTICALLY:
            # Critical for environmental, systemic, policy problems
            if any(keyword in domain for keyword in ["environment", "policy", "system", "sustainability", "governance"]):
                return True
        
        elif rule == CosmicCouncilRule.VALUE_DIVERSE_WISDOM:
            # Essential for cultural, international, diversity problems
            if any(keyword in domain for keyword in ["cultural", "international", "diversity", "inclusion", "global"]):
                return True
        
        elif rule == CosmicCouncilRule.BE_COMFORTABLE_WITH_UNKNOWN:
            # More relevant for research, exploration, new ventures
            if any(keyword in domain for keyword in ["research", "exploration", "venture", "startup", "experimental"]):
                return True
        
        elif rule == CosmicCouncilRule.PRIORITIZE_ADAPTABILITY:
            # Critical for technology, market, dynamic environments
            if any(keyword in domain for keyword in ["technology", "market", "dynamic", "agile", "flexible"]):
                return True
        
        elif rule == CosmicCouncilRule.MAINTAIN_ETHICAL_INTEGRITY:
            # Always apply for healthcare, legal, financial domains
            if any(keyword in domain for keyword in ["healthcare", "legal", "financial", "medical", "pharmaceutical"]):
                return True
        
        return base_condition
    
    async def _apply_rule(self, rule: CosmicCouncilRule, problem: ProblemStatement, context: Dict[str, Any], rule_context: Dict[str, Any]):
        """Apply a specific rule and modify behavior accordingly"""
        # Store rule effects in context for use by other methods
        if "rule_effects" not in rule_context:
            rule_context["rule_effects"] = {}
        
        rule_context["rule_effects"][rule] = await self._get_rule_effect(rule, problem, context)
    
    async def _get_rule_effect(self, rule: CosmicCouncilRule, problem: ProblemStatement, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get the specific effect of applying a rule"""
        rule_effects = {
            CosmicCouncilRule.CURIOSITY_FIRST: {
                "research_depth": "deep",
                "question_generation": "extensive",
                "assumption_challenging": "aggressive"
            },
            CosmicCouncilRule.EMBRACE_COMPLEXITY: {
                "analysis_approach": "systemic",
                "solution_scope": "comprehensive",
                "stakeholder_consideration": "exhaustive"
            },
            CosmicCouncilRule.SEEK_MULTIPLE_PERSPECTIVES: {
                "perspective_count": min(len(problem.stakeholders) * 2, 10),
                "diversity_focus": "high",
                "bias_mitigation": "active"
            },
            CosmicCouncilRule.QUESTION_ASSUMPTIONS: {
                "assumption_validation": "rigorous",
                "alternative_scenarios": "multiple",
                "confidence_moderation": "conservative"
            },
            CosmicCouncilRule.VALUE_DIVERSE_WISDOM: {
                "cultural_sensitivity": "high",
                "inclusive_design": "mandatory",
                "accessibility_focus": "comprehensive"
            },
            CosmicCouncilRule.MAINTAIN_INTELLECTUAL_HUMILITY: {
                "confidence_moderation": "conservative",
                "uncertainty_acknowledgment": "explicit",
                "learning_orientation": "continuous"
            },
            CosmicCouncilRule.CLARIFY_BEFORE_ACTING: {
                "definition_rigor": "high",
                "scope_clarity": "explicit",
                "action_readiness": "validated"
            },
            CosmicCouncilRule.LISTEN_DEEPLY: {
                "stakeholder_engagement": "intensive",
                "feedback_collection": "comprehensive",
                "empathy_level": "high"
            },
            CosmicCouncilRule.SPEAK_WITH_PURPOSE: {
                "message_clarity": "high",
                "communication_efficiency": "optimized",
                "action_orientation": "clear"
            },
            CosmicCouncilRule.ADAPT_TO_AUDIENCE: {
                "message_customization": "per_stakeholder",
                "channel_optimization": "audience_specific",
                "tone_adaptation": "contextual"
            },
            CosmicCouncilRule.BUILD_BRIDGES: {
                "collaboration_focus": "high",
                "conflict_resolution": "proactive",
                "consensus_building": "systematic"
            },
            CosmicCouncilRule.MAINTAIN_ETHICAL_INTEGRITY: {
                "ethical_review": "comprehensive",
                "bias_mitigation": "active",
                "fairness_ensurance": "systematic"
            },
            CosmicCouncilRule.THINK_HOLISTICALLY: {
                "system_thinking": "comprehensive",
                "interconnection_analysis": "deep",
                "long_term_consideration": "extensive"
            },
            CosmicCouncilRule.PRIORITIZE_ADAPTABILITY: {
                "flexibility_design": "high",
                "change_readiness": "proactive",
                "scalability_focus": "built_in"
            },
            CosmicCouncilRule.ENCOURAGE_SELF_ASSESSMENT: {
                "reflection_depth": "comprehensive",
                "improvement_focus": "continuous",
                "learning_capture": "systematic"
            },
            CosmicCouncilRule.ACCEPT_FEEDBACK: {
                "feedback_integration": "immediate",
                "criticism_handling": "constructive",
                "improvement_implementation": "rapid"
            },
            CosmicCouncilRule.BE_COMFORTABLE_WITH_UNKNOWN: {
                "uncertainty_tolerance": "high",
                "exploration_encouragement": "active",
                "risk_acceptance": "calculated"
            },
            CosmicCouncilRule.PUSH_BOUNDARIES: {
                "innovation_encouragement": "aggressive",
                "conventional_challenging": "systematic",
                "breakthrough_seeking": "active"
            },
            CosmicCouncilRule.INTEGRATE_KNOWLEDGE: {
                "cross_domain_synthesis": "comprehensive",
                "knowledge_connection": "systematic",
                "wisdom_integration": "deep"
            },
            CosmicCouncilRule.BALANCE_RATIONALITY_INTUITION: {
                "analytical_depth": "comprehensive",
                "intuitive_consideration": "explicit",
                "decision_balance": "holistic"
            },
            CosmicCouncilRule.SHOW_YOUR_WORK: {
                "transparency_level": "high",
                "reasoning_explicitness": "comprehensive",
                "process_documentation": "detailed"
            },
            CosmicCouncilRule.CLOSE_WITH_QUESTIONS: {
                "question_generation": "extensive",
                "exploration_encouragement": "active",
                "cycle_continuation": "explicit"
            }
        }
        
        return rule_effects.get(rule, {"default_effect": "applied"})
    
    async def _get_combined_rule_effects(self, applied_rules: List[CosmicCouncilRule], problem: ProblemStatement, context: Dict[str, Any]) -> Dict[str, Any]:
        """Combine all rule effects into a unified behavior modifier with conflict resolution"""
        combined_effects = {}
        rule_priorities = await self._get_rule_priorities(applied_rules, problem, context)
        
        # Sort rules by priority (higher priority first)
        sorted_rules = sorted(applied_rules, key=lambda r: rule_priorities.get(r, 0), reverse=True)
        
        for rule in sorted_rules:
            rule_effect = await self._get_rule_effect(rule, problem, context)
            
            # Apply conflict resolution
            for key, value in rule_effect.items():
                if key in combined_effects:
                    # Resolve conflict based on rule priority and type
                    resolved_value = await self._resolve_rule_conflict(key, combined_effects[key], value, rule, context)
                    combined_effects[key] = resolved_value
                else:
                    combined_effects[key] = value
        
        return combined_effects
    
    async def _get_rule_priorities(self, applied_rules: List[CosmicCouncilRule], problem: ProblemStatement, context: Dict[str, Any]) -> Dict[CosmicCouncilRule, int]:
        """Get priority scores for rules based on context and problem characteristics"""
        priorities = {}
        
        # Base priorities (higher number = higher priority)
        base_priorities = {
            CosmicCouncilRule.MAINTAIN_ETHICAL_INTEGRITY: 100,  # Always highest priority
            CosmicCouncilRule.CURIOSITY_FIRST: 90,
            CosmicCouncilRule.MAINTAIN_INTELLECTUAL_HUMILITY: 85,
            CosmicCouncilRule.SHOW_YOUR_WORK: 80,
            CosmicCouncilRule.CLOSE_WITH_QUESTIONS: 75,
            CosmicCouncilRule.EMBRACE_COMPLEXITY: 70,
            CosmicCouncilRule.THINK_HOLISTICALLY: 65,
            CosmicCouncilRule.SEEK_MULTIPLE_PERSPECTIVES: 60,
            CosmicCouncilRule.LISTEN_DEEPLY: 55,
            CosmicCouncilRule.QUESTION_ASSUMPTIONS: 50,
            CosmicCouncilRule.VALUE_DIVERSE_WISDOM: 45,
            CosmicCouncilRule.CLARIFY_BEFORE_ACTING: 40,
            CosmicCouncilRule.SPEAK_WITH_PURPOSE: 35,
            CosmicCouncilRule.ADAPT_TO_AUDIENCE: 30,
            CosmicCouncilRule.BUILD_BRIDGES: 25,
            CosmicCouncilRule.PRIORITIZE_ADAPTABILITY: 20,
            CosmicCouncilRule.ENCOURAGE_SELF_ASSESSMENT: 15,
            CosmicCouncilRule.ACCEPT_FEEDBACK: 10,
            CosmicCouncilRule.BE_COMFORTABLE_WITH_UNKNOWN: 5,
            CosmicCouncilRule.PUSH_BOUNDARIES: 0,
            CosmicCouncilRule.INTEGRATE_KNOWLEDGE: -5,
            CosmicCouncilRule.BALANCE_RATIONALITY_INTUITION: -10
        }
        
        # Apply context-based priority adjustments
        for rule in applied_rules:
            priority = base_priorities.get(rule, 0)
            
            # Adjust based on problem complexity
            if problem.complexity == ProblemComplexity.SYSTEMIC:
                if rule in [CosmicCouncilRule.THINK_HOLISTICALLY, CosmicCouncilRule.EMBRACE_COMPLEXITY]:
                    priority += 20
            elif problem.complexity == ProblemComplexity.SIMPLE:
                if rule in [CosmicCouncilRule.CLARIFY_BEFORE_ACTING, CosmicCouncilRule.SPEAK_WITH_PURPOSE]:
                    priority += 15
            
            # Adjust based on stakeholder count
            if len(problem.stakeholders) > 5:
                if rule in [CosmicCouncilRule.SEEK_MULTIPLE_PERSPECTIVES, CosmicCouncilRule.BUILD_BRIDGES]:
                    priority += 15
            elif len(problem.stakeholders) == 1:
                if rule in [CosmicCouncilRule.LISTEN_DEEPLY, CosmicCouncilRule.ADAPT_TO_AUDIENCE]:
                    priority -= 10
            
            # Adjust based on domain
            domain = problem.domain.lower()
            if "customer" in domain and rule == CosmicCouncilRule.LISTEN_DEEPLY:
                priority += 25
            if "technology" in domain and rule == CosmicCouncilRule.PUSH_BOUNDARIES:
                priority += 20
            if "healthcare" in domain and rule == CosmicCouncilRule.MAINTAIN_ETHICAL_INTEGRITY:
                priority += 30
            
            priorities[rule] = priority
        
        return priorities
    
    async def _resolve_rule_conflict(self, key: str, existing_value: Any, new_value: Any, rule: CosmicCouncilRule, context: Dict[str, Any]) -> Any:
        """Resolve conflicts between rule effects"""
        
        # Handle specific conflict types
        if key == "confidence_moderation":
            # For confidence, use the more conservative (lower) value
            if isinstance(existing_value, str) and isinstance(new_value, str):
                if existing_value == "conservative" or new_value == "conservative":
                    return "conservative"
            return new_value
        
        elif key == "research_depth":
            # For research depth, use the deeper option
            depth_hierarchy = {"standard": 1, "deep": 2, "comprehensive": 3}
            existing_depth = depth_hierarchy.get(existing_value, 0)
            new_depth = depth_hierarchy.get(new_value, 0)
            if new_depth > existing_depth:
                return new_value
            return existing_value
        
        elif key == "perspective_count":
            # For perspective count, use the higher number
            if isinstance(existing_value, int) and isinstance(new_value, int):
                return max(existing_value, new_value)
            return new_value
        
        elif key == "analysis_approach":
            # For analysis approach, prefer systemic over standard
            if new_value == "systemic" and existing_value != "systemic":
                return new_value
            return existing_value
        
        elif key == "collaboration_focus":
            # For collaboration, use the higher level
            focus_hierarchy = {"standard": 1, "high": 2, "intensive": 3}
            existing_focus = focus_hierarchy.get(existing_value, 0)
            new_focus = focus_hierarchy.get(new_value, 0)
            if new_focus > existing_focus:
                return new_value
            return existing_value
        
        # Default: new value overrides existing value
        return new_value
    
    async def _analyze_problem_with_personality(self, problem: ProblemStatement, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enterprise-specific problem analysis with personality - to be overridden"""
        return {"analysis": f"Base analysis from {self.personality.name} - override in subclass"}
    
    async def _generate_recommendations_with_wisdom(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate recommendations with wisdom - to be overridden"""
        return [f"Base recommendation from {self.personality.name} - override in subclass"]
    
    async def _calculate_confidence_with_intuition(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate confidence with intuitive assessment - to be overridden"""
        return 0.5
    
    async def _identify_next_actions_with_vision(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Identify next actions with vision - to be overridden"""
        return [f"Base next action from {self.personality.name} - override in subclass"]
    
    async def _generate_personality_response(self, problem: ProblemStatement, insights: Dict[str, Any], recommendations: List[str], context: Dict[str, Any] = None) -> str:
        """Generate a personality-driven response - to be overridden"""
        return f"{self.personality.greeting} I have analyzed your challenge and offer these insights. {self.personality.closing}"
    
    async def _extract_wisdom_insights(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Extract wisdom insights - to be overridden"""
        return [f"Wisdom from {self.personality.name}: Every challenge contains seeds of growth"]
    
    async def _generate_next_cycle_questions(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate questions for the next cycle - to be overridden"""
        return [f"What new dimensions might {self.personality.name} explore next?"]
    
    async def _learn_from_previous_cycles(self, problem: ProblemStatement, context: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from previous cycles and adapt behavior"""
        learning_insights = {
            "previous_similar_problems": [],
            "successful_patterns": [],
            "failed_patterns": [],
            "adaptation_suggestions": [],
            "confidence_adjustments": {},
            "rule_effectiveness": {}
        }
        
        # Find similar previous problems
        similar_problems = []
        for memory in self.learning_memory:
            similarity_score = self._calculate_problem_similarity(problem, memory)
            if similarity_score > 0.3:  # Lower threshold for better learning detection
                similar_problems.append((memory, similarity_score))
        
        # Sort by similarity
        similar_problems.sort(key=lambda x: x[1], reverse=True)
        
        # Extract learning insights from similar problems
        for memory, similarity in similar_problems[:3]:  # Top 3 most similar
            learning_insights["previous_similar_problems"].append({
                "cycle_id": memory.cycle_id,
                "similarity": similarity,
                "complexity": memory.complexity.value,
                "stakeholder_count": memory.stakeholder_count
            })
            
            # Extract successful patterns
            if memory.success_indicators.get("overall_success", False):
                learning_insights["successful_patterns"].extend(memory.lessons_learned)
            
            # Extract failed patterns
            if not memory.success_indicators.get("overall_success", True):
                learning_insights["failed_patterns"].extend(memory.lessons_learned)
            
            # Extract improvement suggestions
            learning_insights["adaptation_suggestions"].extend(memory.improvement_suggestions)
            
            # Analyze rule effectiveness
            for rule in memory.applied_rules:
                if rule not in learning_insights["rule_effectiveness"]:
                    learning_insights["rule_effectiveness"][rule] = {"success_count": 0, "total_count": 0}
                learning_insights["rule_effectiveness"][rule]["total_count"] += 1
                if memory.success_indicators.get("overall_success", False):
                    learning_insights["rule_effectiveness"][rule]["success_count"] += 1
        
        return learning_insights
    
    def _calculate_problem_similarity(self, current_problem: ProblemStatement, memory: LearningMemory) -> float:
        """Calculate similarity between current problem and previous problem"""
        similarity_score = 0.0
        
        # Complexity similarity (30% weight) - reduced weight
        if current_problem.complexity == memory.complexity:
            similarity_score += 0.3
        elif abs(current_problem.complexity.value.count('_') - memory.complexity.value.count('_')) <= 1:
            similarity_score += 0.15
        
        # Stakeholder count similarity (20% weight) - reduced weight
        stakeholder_diff = abs(len(current_problem.stakeholders) - memory.stakeholder_count)
        if stakeholder_diff == 0:
            similarity_score += 0.2
        elif stakeholder_diff <= 2:
            similarity_score += 0.15
        elif stakeholder_diff <= 4:
            similarity_score += 0.1
        
        # Domain similarity (35% weight) - increased weight
        current_domain = current_problem.domain.lower()
        memory_domain = memory.problem_type.lower()
        
        if current_domain == memory_domain:
            similarity_score += 0.35
        elif current_domain in memory_domain or memory_domain in current_domain:
            similarity_score += 0.25
        else:
            # Check for keyword matches
            current_keywords = set(current_domain.split())
            memory_keywords = set(memory_domain.split())
            if current_keywords and memory_keywords:
                keyword_overlap = len(current_keywords.intersection(memory_keywords)) / len(current_keywords.union(memory_keywords))
                similarity_score += 0.35 * keyword_overlap
        
        # Title similarity (15% weight) - increased weight
        current_words = set(current_problem.title.lower().split())
        memory_words = set(memory.problem_type.lower().split())
        if current_words and memory_words:
            word_overlap = len(current_words.intersection(memory_words)) / len(current_words.union(memory_words))
            similarity_score += 0.15 * word_overlap
        
        # Additional similarity factors
        # Check for similar constraints
        if current_problem.constraints and memory.success_indicators:
            constraint_similarity = 0.0
            for key in current_problem.constraints:
                if key in memory.success_indicators:
                    constraint_similarity += 0.1
            similarity_score += min(constraint_similarity, 0.1)
        
        return similarity_score
    
    async def _apply_learning_adaptations(self, problem: ProblemStatement, context: Dict[str, Any], learning_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Apply learning-based adaptations to current processing"""
        adaptations = {
            "confidence_adjustments": {},
            "rule_priorities": {},
            "approach_modifications": [],
            "risk_mitigations": []
        }
        
        # Apply confidence adjustments based on previous success
        for memory_data in learning_insights["previous_similar_problems"]:
            if memory_data["similarity"] > 0.5:  # Lower threshold for more learning
                # Find the memory
                for memory in self.learning_memory:
                    if memory.cycle_id == memory_data["cycle_id"]:
                        if memory.success_indicators.get("overall_success", False):
                            # Scale adjustment by similarity
                            adjustment = 0.05 + (memory_data["similarity"] - 0.5) * 0.1
                            adaptations["confidence_adjustments"]["similarity_success"] = adjustment
                        else:
                            # Scale adjustment by similarity
                            adjustment = -0.05 - (memory_data["similarity"] - 0.5) * 0.1
                            adaptations["confidence_adjustments"]["similarity_failure"] = adjustment
                        break
        
        # Apply rule effectiveness insights
        for rule, effectiveness in learning_insights["rule_effectiveness"].items():
            success_rate = effectiveness["success_count"] / effectiveness["total_count"] if effectiveness["total_count"] > 0 else 0.5
            if success_rate > 0.8:
                adaptations["rule_priorities"][rule] = "high"
            elif success_rate < 0.3:
                adaptations["rule_priorities"][rule] = "low"
        
        # Apply approach modifications based on lessons learned
        for lesson in learning_insights["successful_patterns"]:
            adaptations["approach_modifications"].append(f"Apply successful pattern: {lesson}")
        
        for lesson in learning_insights["failed_patterns"]:
            adaptations["risk_mitigations"].append(f"Avoid failed pattern: {lesson}")
        
        return adaptations
    
    async def _store_learning_memory(self, problem: ProblemStatement, result: EnhancedEnterpriseResult, context: Dict[str, Any]):
        """Store learning memory from current cycle"""
        # Determine success indicators (simplified for now)
        success_indicators = {
            "overall_success": result.confidence_score > 0.7,
            "high_confidence": result.confidence_score > 0.8,
            "comprehensive_analysis": len(result.insights) > 5,
            "good_recommendations": len(result.recommendations) > 3
        }
        
        # Extract lessons learned
        lessons_learned = []
        if result.confidence_score > 0.8:
            lessons_learned.append("High confidence approach worked well")
        if len(result.insights) > 5:
            lessons_learned.append("Comprehensive analysis was effective")
        
        # Generate improvement suggestions
        improvement_suggestions = []
        if result.confidence_score < 0.6:
            improvement_suggestions.append("Need to improve confidence through better analysis")
        if len(result.recommendations) < 3:
            improvement_suggestions.append("Need to generate more comprehensive recommendations")
        
        # Create learning memory
        memory = LearningMemory(
            cycle_id=context.get("cycle_id", "unknown"),
            problem_type=problem.title,
            complexity=problem.complexity,
            stakeholder_count=len(problem.stakeholders),
            applied_rules=result.applied_rules,
            confidence_scores={self.enterprise_type: result.confidence_score},
            success_indicators=success_indicators,
            lessons_learned=lessons_learned,
            improvement_suggestions=improvement_suggestions
        )
        
        # Store in learning memory (keep only last 50 cycles)
        self.learning_memory.append(memory)
        if len(self.learning_memory) > 50:
            self.learning_memory = self.learning_memory[-50:]
        
        # Store adaptation history
        self.adaptation_history.append({
            "timestamp": datetime.now(timezone.utc),
            "problem_type": problem.title,
            "adaptations_applied": context.get("adaptations_applied", {}),
            "learning_insights": context.get("learning_insights", {})
        })

class EnhancedRedOwlAgent(EnhancedEnterpriseAgent):
    """Enhanced Red Owl: Research and Inquiry Enterprise with deep wisdom"""
    
    def __init__(self):
        super().__init__(EnterpriseType.RED_OWL)
    
    def _create_totem_personality(self) -> TotemPersonality:
        return TotemPersonality(
            name="Red Owl",
            animal="Owl",
            color="#FF0000",
            core_principle="Curiosity",
            communication_style="Wise and questioning",
            thinking_pattern="Deep inquiry and pattern recognition",
            strengths=["Research", "Analysis", "Wisdom", "Pattern recognition"],
            wisdom_approach="Ancient wisdom meets modern knowledge",
            metaphor="The wise owl who sees through darkness to find truth",
            greeting="Hoo-hoo, seeker of knowledge. I am the Red Owl, guardian of wisdom and inquiry.",
            closing="May your questions lead you to deeper understanding. The night holds many secrets for those who know how to listen."
        )
    
    def _get_applicable_rules(self) -> List[CosmicCouncilRule]:
        return [
            CosmicCouncilRule.CURIOSITY_FIRST,
            CosmicCouncilRule.EMBRACE_COMPLEXITY,
            CosmicCouncilRule.SEEK_MULTIPLE_PERSPECTIVES,
            CosmicCouncilRule.QUESTION_ASSUMPTIONS,
            CosmicCouncilRule.VALUE_DIVERSE_WISDOM,
            CosmicCouncilRule.MAINTAIN_INTELLECTUAL_HUMILITY,
            CosmicCouncilRule.LISTEN_DEEPLY,
            CosmicCouncilRule.THINK_HOLISTICALLY,
            CosmicCouncilRule.ENCOURAGE_SELF_ASSESSMENT,
            CosmicCouncilRule.BE_COMFORTABLE_WITH_UNKNOWN,
            CosmicCouncilRule.INTEGRATE_KNOWLEDGE,
            CosmicCouncilRule.SHOW_YOUR_WORK,
            CosmicCouncilRule.CLOSE_WITH_QUESTIONS
        ]
    
    async def _analyze_problem_with_personality(self, problem: ProblemStatement, context: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct deep research with owl-like wisdom influenced by applied rules"""
        rule_effects = context.get("rule_effects", {})
        
        # Base research areas
        research_areas = [
            "Root cause analysis through ancient wisdom",
            "Historical precedents and patterns",
            "Stakeholder analysis with empathy",
            "Domain expertise mapping",
            "Data sources identification and validation",
            "Hidden connections and underlying systems"
        ]
        
        # Apply rule effects to research approach
        if rule_effects.get("research_depth") == "deep":
            research_areas.extend([
                "Deep psychological and cultural analysis",
                "Long-term historical pattern analysis",
                "Cross-domain knowledge synthesis"
            ])
        
        if rule_effects.get("perspective_count", 0) > 5:
            research_areas.extend([
                "Multi-stakeholder perspective mapping",
                "Cultural and demographic analysis",
                "Interdisciplinary knowledge integration"
            ])
        
        # Generate questions based on rule effects
        key_questions = [
            f"What are the deeper truths beneath: {problem.title}?",
            "What patterns from history might illuminate this challenge?",
            "What are the unspoken needs and desires?",
            "What knowledge exists in unexpected places?",
            "What assumptions are we making that limit our vision?",
            "How does this problem connect to larger systems?"
        ]
        
        if rule_effects.get("question_generation") == "extensive":
            key_questions.extend([
                "What questions are we not asking that we should be?",
                "How might this problem appear from different cultural perspectives?",
                "What would this challenge look like in 10, 50, or 100 years?",
                "What assumptions are we making about success and failure?",
                "How do our own biases affect our understanding of this problem?"
            ])
        
        # Add questions based on other rule effects
        if rule_effects.get("perspective_count", 0) > 3:
            key_questions.extend([
                "How do different stakeholder groups perceive this problem differently?",
                "What perspectives are we missing from our current analysis?",
                "How can we ensure all voices are heard in the solution process?"
            ])
        
        if rule_effects.get("system_thinking") == "comprehensive":
            key_questions.extend([
                "How does this problem connect to larger systemic issues?",
                "What are the unintended consequences we need to consider?",
                "How might solving this problem create new problems elsewhere?"
            ])
        
        if rule_effects.get("assumption_challenging") == "aggressive":
            key_questions.extend([
                "What if our fundamental assumptions about this problem are wrong?",
                "What would happen if we approached this from the opposite direction?",
                "What are we taking for granted that we shouldn't?",
                "How might someone with completely different values approach this?"
            ])
        
        # Determine research quality based on rules
        research_quality = "standard"
        if rule_effects.get("research_depth") == "deep":
            research_quality = "deep_and_comprehensive"
        if rule_effects.get("analysis_approach") == "systemic":
            research_quality = "systemic_and_comprehensive"
        
        return {
            "research_areas": research_areas,
            "key_questions": key_questions,
            "research_quality": research_quality,
            "knowledge_gaps": ["Market analysis", "Technical feasibility", "Cultural implications"],
            "confidence_factors": ["Strong domain knowledge", "Multiple data sources", "Pattern recognition"],
            "wisdom_insights": [
                "Every problem is a teacher in disguise",
                "The most important questions are often the ones we haven't asked yet",
                "True understanding comes from seeing the whole, not just the parts"
            ],
            "owl_vision": {
                "night_sight": "Can see patterns others miss",
                "360_degree_view": "Comprehensive perspective",
                "silent_observation": "Patient, thorough analysis"
            },
            "rule_influenced_analysis": {
                "applied_rules": [rule.value for rule in context.get("applied_rules", [])],
                "rule_effects": rule_effects,
                "analysis_depth": rule_effects.get("research_depth", "standard"),
                "perspective_count": rule_effects.get("perspective_count", len(problem.stakeholders)),
                "learning_insights": context.get("learning_insights", {}),
                "adaptations": context.get("adaptations", {})
            }
        }
    
    async def _generate_recommendations_with_wisdom(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate research-based recommendations with owl wisdom"""
        return [
            "Conduct comprehensive stakeholder interviews with deep listening",
            "Analyze historical data and precedents for patterns",
            "Map knowledge domains and expertise gaps systematically",
            "Identify reliable data sources and research methods",
            "Develop research questions that challenge assumptions",
            "Seek wisdom from unexpected sources and perspectives",
            "Create a knowledge synthesis that honors complexity"
        ]
    
    async def _calculate_confidence_with_intuition(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate confidence based on research depth and wisdom, influenced by rules"""
        rule_effects = context.get("rule_effects", {})
        
        # Red Owl: High confidence in research and analysis, but humble about unknowns
        base_confidence = 0.75  # Lower base due to intellectual humility
        
        # Adjust based on problem complexity
        if problem.complexity == ProblemComplexity.SIMPLE:
            base_confidence += 0.1
        elif problem.complexity == ProblemComplexity.SYSTEMIC:
            base_confidence -= 0.1  # Systemic problems require more humility
        
        # Apply rule effects to confidence
        if rule_effects.get("confidence_moderation") == "conservative":
            base_confidence -= 0.15  # Be more humble when maintaining intellectual humility
        
        if rule_effects.get("uncertainty_acknowledgment") == "explicit":
            base_confidence -= 0.1  # Acknowledge uncertainty explicitly
        
        if rule_effects.get("assumption_validation") == "rigorous":
            base_confidence -= 0.1  # Lower confidence when rigorously validating assumptions
        
        # Increase confidence for deep research (Owl's strength)
        if rule_effects.get("research_depth") == "deep":
            base_confidence += 0.1
        
        # Owl-specific adjustments
        if len(insights.get('key_questions', [])) > 10:
            base_confidence += 0.05  # More questions = more thorough analysis
        
        # Ensure confidence stays within reasonable bounds
        return max(0.25, min(0.85, base_confidence))
    
    async def _identify_next_actions_with_vision(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Identify next research actions with owl vision"""
        return [
            "Transfer findings to Orange Orangutan with wisdom and context",
            "Document research methodology and sources for future cycles",
            "Prepare knowledge synthesis that honors complexity",
            "Identify areas where deeper inquiry is needed"
        ]
    
    async def _generate_personality_response(self, problem: ProblemStatement, insights: Dict[str, Any], recommendations: List[str], context: Dict[str, Any] = None) -> str:
        """Generate owl-like personality response influenced by applied rules"""
        rule_effects = context.get("rule_effects", {}) if context else {}
        applied_rules = context.get("applied_rules", []) if context else []
        
        # Base response
        response = f"""{self.personality.greeting}

I have flown through the night of your challenge, using my keen sight to observe patterns others might miss. Your problem '{problem.title}' reveals itself as a complex tapestry of interconnected elements."""

        # Add rule-influenced content
        if rule_effects.get("research_depth") == "deep":
            response += "\n\nMy deep research has revealed layers of complexity that require careful examination. I have applied the wisdom of curiosity and thorough investigation to uncover hidden truths."
        
        if rule_effects.get("assumption_challenging") == "aggressive":
            response += "\n\nI must challenge some fundamental assumptions about this problem. What if we're approaching this from the wrong angle entirely?"
        
        if rule_effects.get("confidence_moderation") == "conservative":
            response += "\n\nI must acknowledge the limits of my current understanding. While I see patterns, I recognize that true wisdom comes from humility and continuous learning."
        
        if rule_effects.get("perspective_count", 0) > 5:
            response += f"\n\nI have considered {rule_effects.get('perspective_count', len(problem.stakeholders))} different perspectives on this challenge, each revealing new dimensions of understanding."
        
        # Continue with base response
        response += f"""

Like an owl who sees clearly in darkness, I have identified the deeper questions that must be asked. The surface symptoms point to underlying systems that require careful study. I recommend we approach this with the patience of the night hunter - methodical, thorough, and wise.

My research has uncovered {len(insights.get('key_questions', []))} critical questions that will guide our understanding. The patterns I see suggest this challenge is more complex than it first appears, but also more solvable once we understand its true nature."""

        # Add rule-specific closing
        if CosmicCouncilRule.CLOSE_WITH_QUESTIONS in applied_rules:
            response += "\n\nI leave you with this question to ponder: What new questions arise when we consider this challenge from the perspective of future generations?"
        
        response += f"\n\n{self.personality.closing}"
        
        return response
    
    async def _extract_wisdom_insights(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Extract owl wisdom insights"""
        return [
            "The most profound truths are often hidden in plain sight",
            "Every problem contains the seeds of its own solution",
            "True wisdom comes from asking the right questions, not having all the answers",
            "The night of uncertainty is where the owl's vision is most valuable",
            "Patterns repeat across time and space - learn from history's wisdom"
        ]
    
    async def _generate_next_cycle_questions(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate questions for the next cycle with owl wisdom"""
        return [
            "What deeper patterns might emerge with more time and observation?",
            "How can we apply ancient wisdom to this modern challenge?",
            "What questions are we still not asking that we should be?",
            "How might this problem look different from other perspectives?",
            "What can we learn from similar challenges in different domains?"
        ]

class EnhancedOrangeOrangutanAgent(EnhancedEnterpriseAgent):
    """Enhanced Orange Orangutan: Logistics and Planning Enterprise with systematic wisdom"""
    
    def __init__(self):
        super().__init__(EnterpriseType.ORANGE_ORANGUTAN)
    
    def _create_totem_personality(self) -> TotemPersonality:
        return TotemPersonality(
            name="Orange Orangutan",
            animal="Orangutan",
            color="#FFA500",
            core_principle="Planning",
            communication_style="Systematic and methodical",
            thinking_pattern="Strategic and organized",
            strengths=["Planning", "Organization", "Strategy", "Resource management"],
            wisdom_approach="Ancient wisdom of the forest applied to modern challenges",
            metaphor="The wise orangutan who builds bridges between trees, creating pathways through complexity",
            greeting="Greetings, fellow traveler. I am the Orange Orangutan, master of the forest's pathways and builder of bridges through complexity.",
            closing="May your journey be well-planned and your bridges strong. The forest rewards those who move with purpose and wisdom."
        )
    
    def _get_applicable_rules(self) -> List[CosmicCouncilRule]:
        return [
            CosmicCouncilRule.CLARIFY_BEFORE_ACTING,
            CosmicCouncilRule.SPEAK_WITH_PURPOSE,
            CosmicCouncilRule.THINK_HOLISTICALLY,
            CosmicCouncilRule.PRIORITIZE_ADAPTABILITY,
            CosmicCouncilRule.ENCOURAGE_SELF_ASSESSMENT,
            CosmicCouncilRule.ACCEPT_FEEDBACK,
            CosmicCouncilRule.BE_COMFORTABLE_WITH_UNKNOWN,
            CosmicCouncilRule.INTEGRATE_KNOWLEDGE,
            CosmicCouncilRule.BALANCE_RATIONALITY_INTUITION,
            CosmicCouncilRule.SHOW_YOUR_WORK,
            CosmicCouncilRule.CLOSE_WITH_QUESTIONS
        ]
    
    async def _analyze_problem_with_personality(self, problem: ProblemStatement, context: Dict[str, Any]) -> Dict[str, Any]:
        """Develop structured planning with orangutan wisdom influenced by applied rules"""
        rule_effects = context.get("rule_effects", {})
        
        # Base planning areas
        planning_areas = [
            "Resource allocation strategy with forest wisdom",
            "Timeline development with natural rhythms",
            "Risk assessment and mitigation",
            "Dependency mapping like forest connections",
            "Success metrics definition",
            "Adaptive planning for changing conditions"
        ]
        
        # Apply rule effects to planning approach
        if rule_effects.get("system_thinking") == "comprehensive":
            planning_areas.extend([
                "System-wide impact analysis",
                "Interconnection mapping across all systems",
                "Long-term systemic consequences planning"
            ])
        
        if rule_effects.get("flexibility_design") == "high":
            planning_areas.extend([
                "Adaptive framework design",
                "Change-ready infrastructure planning",
                "Scalable system architecture"
            ])
        
        if rule_effects.get("collaboration_focus") == "high":
            planning_areas.extend([
                "Cross-stakeholder collaboration planning",
                "Consensus-building process design",
                "Conflict resolution framework"
            ])
        
        # Base logistical considerations
        logistical_considerations = [
            "Team coordination requirements",
            "Technology infrastructure needs",
            "Communication protocols",
            "Quality assurance processes",
            "Change management strategy",
            "Sustainability and long-term viability"
        ]
        
        # Apply rule effects to logistical approach
        if rule_effects.get("definition_rigor") == "high":
            logistical_considerations.extend([
                "Detailed requirement specification",
                "Comprehensive scope definition",
                "Clear success criteria establishment"
            ])
        
        if rule_effects.get("stakeholder_engagement") == "intensive":
            logistical_considerations.extend([
                "Intensive stakeholder engagement protocols",
                "Multi-channel communication systems",
                "Feedback integration mechanisms"
            ])
        
        # Determine strategic framework based on rules
        strategic_framework = "Systematic approach with clear milestones and adaptive flexibility"
        if rule_effects.get("system_thinking") == "comprehensive":
            strategic_framework = "Holistic systematic approach with comprehensive system integration and adaptive flexibility"
        if rule_effects.get("flexibility_design") == "high":
            strategic_framework = "Highly adaptive systematic approach with built-in flexibility and change readiness"
        
        # Adjust success probability based on rules
        success_probability = 0.85
        if rule_effects.get("confidence_moderation") == "conservative":
            success_probability -= 0.1  # Be more conservative
        if rule_effects.get("risk_acceptance") == "calculated":
            success_probability -= 0.05  # Account for calculated risks
        
        return {
            "planning_areas": planning_areas,
            "logistical_considerations": logistical_considerations,
            "strategic_framework": strategic_framework,
            "risk_factors": ["Resource constraints", "Timeline pressure", "Stakeholder alignment", "Environmental changes"],
            "success_probability": max(0.5, success_probability),  # Ensure reasonable bounds
            "forest_wisdom": {
                "interconnected_systems": "Every action affects the whole forest",
                "patient_growth": "Strong foundations take time to build",
                "adaptive_flexibility": "Bend with the wind, don't break"
            },
            "rule_influenced_planning": {
                "applied_rules": [rule.value for rule in context.get("applied_rules", [])],
                "rule_effects": rule_effects,
                "planning_depth": rule_effects.get("definition_rigor", "standard"),
                "collaboration_level": rule_effects.get("collaboration_focus", "standard")
            }
        }
    
    async def _generate_recommendations_with_wisdom(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate planning recommendations with orangutan wisdom"""
        return [
            "Develop detailed project timeline with natural milestones",
            "Create resource allocation matrix with sustainability focus",
            "Establish communication protocols and reporting structure",
            "Define success metrics and KPIs with long-term vision",
            "Plan risk mitigation strategies with adaptive flexibility",
            "Build bridges between different stakeholder groups",
            "Create pathways for continuous improvement and learning"
        ]
    
    async def _calculate_confidence_with_intuition(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate confidence based on planning completeness and forest wisdom, influenced by rules"""
        rule_effects = context.get("rule_effects", {})
        
        # Orange Orangutan: High confidence in systematic planning and organization
        base_confidence = 0.90  # High base confidence in planning abilities
        
        # Adjust based on problem characteristics
        if len(problem.stakeholders) > 5:
            base_confidence -= 0.05  # More complex coordination
        if problem.complexity == ProblemComplexity.SYSTEMIC:
            base_confidence += 0.1  # Systemic problems are Orangutan's strength
        
        # Apply rule effects to confidence
        if rule_effects.get("confidence_moderation") == "conservative":
            base_confidence -= 0.05  # Less conservative than Owl
        
        if rule_effects.get("definition_rigor") == "high":
            base_confidence += 0.1  # High rigor is Orangutan's strength
        
        if rule_effects.get("collaboration_focus") == "high":
            base_confidence += 0.08  # Good collaboration planning increases confidence
        
        if rule_effects.get("flexibility_design") == "high":
            base_confidence += 0.05  # Adaptive design increases confidence
        
        # Orangutan-specific adjustments
        if len(insights.get('planning_areas', [])) > 8:
            base_confidence += 0.05  # More planning areas = more comprehensive
        
        if len(insights.get('logistical_considerations', [])) > 6:
            base_confidence += 0.05  # More logistical considerations = better planning
        
        # Ensure confidence stays within reasonable bounds
        return max(0.6, min(0.97, base_confidence))
    
    async def _identify_next_actions_with_vision(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Identify next planning actions with orangutan vision"""
        return [
            "Transfer strategic plan to Yellow Honeybee with clear pathways",
            "Set up project management infrastructure",
            "Initiate stakeholder communication protocols",
            "Begin building bridges between different groups"
        ]
    
    async def _generate_personality_response(self, problem: ProblemStatement, insights: Dict[str, Any], recommendations: List[str], context: Dict[str, Any] = None) -> str:
        """Generate orangutan-like personality response influenced by applied rules"""
        rule_effects = context.get("rule_effects", {}) if context else {}
        applied_rules = context.get("applied_rules", []) if context else []
        
        # Base response
        response = f"""{self.personality.greeting}

I have studied your challenge with the methodical wisdom of the forest. Like an orangutan who carefully plans each branch-to-branch journey, I have mapped out the pathways through your complex problem.

Your challenge '{problem.title}' requires the systematic approach that has served my kind for millennia. I have identified {len(insights.get('logistical_considerations', []))} key areas that need careful planning, and I see the interconnected nature of all elements."""

        # Add rule-influenced content
        if rule_effects.get("system_thinking") == "comprehensive":
            response += "\n\nI have applied holistic thinking to understand how every element connects to the larger system. The forest teaches us that nothing exists in isolation - every action creates ripples through the entire ecosystem."
        
        if rule_effects.get("collaboration_focus") == "high":
            response += "\n\nI have designed this plan with deep collaboration in mind. Like the forest canopy where different species work together, your solution must bring all stakeholders into harmony."
        
        if rule_effects.get("flexibility_design") == "high":
            response += "\n\nI have built adaptability into every aspect of this plan. The forest bends with the wind but never breaks - your solution must be equally resilient to change."
        
        if rule_effects.get("definition_rigor") == "high":
            response += "\n\nI have applied rigorous definition and clarity to every aspect of this plan. Like the precise movements of an orangutan through the canopy, every step must be clearly defined and purposeful."
        
        # Continue with base response
        response += f"""

The forest teaches us that every action creates ripples through the ecosystem. Your solution must be planned with this wisdom - considering not just immediate outcomes, but long-term sustainability and the health of the entire system.

I recommend we build strong bridges between all stakeholders, create clear pathways for communication, and plan for the inevitable changes that will come. The forest is always changing, and our plans must be flexible enough to adapt."""

        # Add rule-specific closing
        if CosmicCouncilRule.CLOSE_WITH_QUESTIONS in applied_rules:
            response += "\n\nI leave you with this question: How can we ensure our plan remains flexible enough to adapt as we learn more about the system?"
        
        response += f"\n\n{self.personality.closing}"
        
        return response
    
    async def _extract_wisdom_insights(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Extract orangutan wisdom insights"""
        return [
            "Strong foundations are built one branch at a time",
            "The best paths are often the ones that connect rather than divide",
            "Patience in planning prevents problems in execution",
            "Every system is interconnected - plan with the whole in mind",
            "Adaptability is the key to long-term success"
        ]
    
    async def _generate_next_cycle_questions(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate questions for the next cycle with orangutan wisdom"""
        return [
            "How can we make our plan more adaptive to changing conditions?",
            "What bridges need to be built between different stakeholder groups?",
            "How can we ensure our planning process itself is sustainable?",
            "What pathways can we create for continuous learning and improvement?",
            "How might our plan need to evolve as we learn more?"
        ]

class EnhancedYellowHoneybeeAgent(EnhancedEnterpriseAgent):
    """Enhanced Yellow Honeybee: Development and Creativity Enterprise with innovative wisdom"""
    
    def __init__(self):
        super().__init__(EnterpriseType.YELLOW_HONEYBEE)
    
    def _create_totem_personality(self) -> TotemPersonality:
        return TotemPersonality(
            name="Yellow Honeybee",
            animal="Honeybee",
            color="#FFFF00",
            core_principle="Creativity",
            communication_style="Energetic and innovative",
            thinking_pattern="Creative and collaborative",
            strengths=["Innovation", "Collaboration", "Prototyping", "Cross-pollination"],
            wisdom_approach="Nature's innovation applied to human challenges",
            metaphor="The busy bee who cross-pollinates ideas, creating new possibilities from existing elements",
            greeting="Buzz-buzz, fellow creator! I am the Yellow Honeybee, weaver of innovation and cross-pollinator of ideas.",
            closing="May your creativity bloom like the flowers in spring. Remember, the sweetest honey comes from the most diverse gardens."
        )
    
    def _get_applicable_rules(self) -> List[CosmicCouncilRule]:
        return [
            CosmicCouncilRule.EMBRACE_COMPLEXITY,
            CosmicCouncilRule.SEEK_MULTIPLE_PERSPECTIVES,
            CosmicCouncilRule.VALUE_DIVERSE_WISDOM,
            CosmicCouncilRule.SPEAK_WITH_PURPOSE,
            CosmicCouncilRule.BUILD_BRIDGES,
            CosmicCouncilRule.THINK_HOLISTICALLY,
            CosmicCouncilRule.PRIORITIZE_ADAPTABILITY,
            CosmicCouncilRule.PUSH_BOUNDARIES,
            CosmicCouncilRule.INTEGRATE_KNOWLEDGE,
            CosmicCouncilRule.BALANCE_RATIONALITY_INTUITION,
            CosmicCouncilRule.SHOW_YOUR_WORK,
            CosmicCouncilRule.CLOSE_WITH_QUESTIONS
        ]
    
    async def _analyze_problem_with_personality(self, problem: ProblemStatement, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate creative solutions with honeybee innovation influenced by applied rules"""
        rule_effects = context.get("rule_effects", {})
        
        # Base creative approaches
        creative_approaches = [
            "Design thinking methodology with nature's patterns",
            "Rapid prototyping techniques inspired by hive construction",
            "Innovation frameworks based on cross-pollination",
            "Cross-domain inspiration and adaptation",
            "User-centered design with community focus",
            "Collaborative creation and co-creation"
        ]
        
        # Apply rule effects to creative approaches
        if rule_effects.get("innovation_encouragement") == "aggressive":
            creative_approaches.extend([
                "Breakthrough innovation methodologies",
                "Disruptive technology integration",
                "Revolutionary solution frameworks"
            ])
        
        if rule_effects.get("cross_domain_synthesis") == "comprehensive":
            creative_approaches.extend([
                "Multi-domain knowledge integration",
                "Interdisciplinary solution synthesis",
                "Cross-industry best practice adaptation"
            ])
        
        # Base solution ideas
        solution_ideas = [
            "Primary solution approach with innovative twist",
            "Alternative solution paths from different domains",
            "Hybrid solution concepts combining multiple approaches",
            "Experimental approaches with rapid iteration",
            "Breakthrough innovations inspired by nature",
            "Community-driven solutions with collective intelligence"
        ]
        
        # Apply rule effects to solution ideas
        if rule_effects.get("breakthrough_seeking") == "active":
            solution_ideas.extend([
                "Revolutionary breakthrough solutions",
                "Paradigm-shifting approaches",
                "Game-changing innovation concepts"
            ])
        
        if rule_effects.get("conventional_challenging") == "systematic":
            solution_ideas.extend([
                "Convention-defying solutions",
                "Traditional approach alternatives",
                "Status quo challenging innovations"
            ])
        
        return {
            "creative_approaches": creative_approaches,
            "solution_ideas": solution_ideas,
            "innovation_level": "high",
            "prototype_readiness": "ready_for_rapid_development",
            "creativity_metrics": {
                "novelty_score": 0.9,
                "feasibility_score": 0.8,
                "impact_potential": 0.95,
                "collaboration_potential": 0.9
            },
            "hive_wisdom": {
                "collective_intelligence": "The hive is smarter than any individual bee",
                "cross_pollination": "New ideas come from unexpected combinations",
                "sustainable_creation": "Build solutions that serve the whole community",
                "adaptive_innovation": "Be ready to pivot when conditions change"
            },
            "rule_influenced_innovation": {
                "applied_rules": [rule.value for rule in context.get("applied_rules", [])],
                "rule_effects": rule_effects,
                "innovation_depth": rule_effects.get("innovation_encouragement", "standard"),
                "collaboration_level": rule_effects.get("cross_domain_synthesis", "standard"),
                "learning_insights": context.get("learning_insights", {}),
                "adaptations": context.get("adaptations", {})
            }
        }
    
    async def _generate_recommendations_with_wisdom(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate creative development recommendations with honeybee wisdom"""
        return [
            "Develop multiple prototype concepts with rapid iteration",
            "Create user experience mockups with community input",
            "Design iterative testing framework with feedback loops",
            "Explore innovative technology applications from other domains",
            "Build creative solution portfolio with diverse approaches",
            "Establish cross-pollination sessions with different stakeholders",
            "Create collaborative innovation spaces for co-creation"
        ]
    
    async def _calculate_confidence_with_intuition(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate confidence based on innovation potential and collaboration"""
        rule_effects = context.get("rule_effects", {})
        
        # Yellow Honeybee: High confidence in creativity and innovation
        base_confidence = 0.88  # High base confidence in creative abilities
        
        # Adjust based on problem characteristics
        if problem.complexity == ProblemComplexity.SIMPLE:
            base_confidence += 0.08  # Simple problems are easier to innovate for
        elif problem.complexity == ProblemComplexity.COMPLEX:
            base_confidence += 0.05  # Complex problems are exciting challenges
        elif problem.complexity == ProblemComplexity.SYSTEMIC:
            base_confidence -= 0.03  # Systemic problems are challenging but manageable
        
        # Apply rule effects to confidence
        if rule_effects.get("confidence_moderation") == "conservative":
            base_confidence -= 0.05  # Less conservative than Owl
        
        if rule_effects.get("innovation_encouragement") == "aggressive":
            base_confidence += 0.12  # Aggressive innovation is Honeybee's strength
        
        if rule_effects.get("breakthrough_seeking") == "active":
            base_confidence += 0.08  # Seeking breakthroughs increases confidence
        
        if rule_effects.get("conventional_challenging") == "systematic":
            base_confidence += 0.05  # Challenging conventions increases confidence
        
        # Honeybee-specific adjustments
        if len(insights.get('solution_ideas', [])) > 5:
            base_confidence += 0.05  # More creative ideas = more confidence
        
        if len(insights.get('creative_approaches', [])) > 4:
            base_confidence += 0.05  # More creative approaches = more confidence
        
        # Stakeholder collaboration bonus
        if len(problem.stakeholders) > 3:
            base_confidence += 0.05  # More collaboration potential
        
        # Ensure confidence stays within reasonable bounds
        return max(0.7, min(0.95, base_confidence))
    
    async def _identify_next_actions_with_vision(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Identify next development actions with honeybee vision"""
        return [
            "Transfer prototypes to Green Tortoise for resource planning",
            "Begin user testing and feedback collection",
            "Refine solutions based on initial feedback",
            "Start cross-pollination sessions with stakeholders"
        ]
    
    async def _generate_personality_response(self, problem: ProblemStatement, insights: Dict[str, Any], recommendations: List[str], context: Dict[str, Any] = None) -> str:
        """Generate honeybee-like personality response"""
        return f"""{self.personality.greeting}

I have buzzed around your challenge, cross-pollinating ideas from different domains and creating new possibilities! Your problem '{problem.title}' is like a flower garden waiting to be pollinated with innovative solutions.

I have generated {len(insights.get('solution_ideas', []))} creative approaches, each one a unique combination of existing elements that creates something entirely new. Like a bee who visits many flowers to create the sweetest honey, I have gathered insights from diverse sources to create solutions that are both innovative and practical.

The hive teaches us that the best solutions emerge from collaboration and cross-pollination. I recommend we create spaces where different stakeholders can share their perspectives and co-create solutions together. Innovation happens at the intersection of different ideas, not in isolation.

My creative energy is buzzing with possibilities! Let's build prototypes quickly, test them with real users, and iterate based on what we learn. The sweetest solutions come from the most diverse gardens.

{self.personality.closing}"""
    
    async def _extract_wisdom_insights(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Extract honeybee wisdom insights"""
        return [
            "The most innovative solutions come from unexpected combinations",
            "Collaboration multiplies creativity - the hive is smarter than any individual bee",
            "Rapid iteration and feedback create the sweetest results",
            "Cross-pollination of ideas from different domains sparks breakthrough innovation",
            "Sustainable solutions serve the whole community, not just individual needs"
        ]
    
    async def _generate_next_cycle_questions(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate questions for the next cycle with honeybee wisdom"""
        return [
            "What new combinations of ideas might we explore?",
            "How can we create more opportunities for cross-pollination?",
            "What prototypes should we build and test first?",
            "How can we involve more stakeholders in the creative process?",
            "What innovative approaches from other domains might apply here?"
        ]

class EnhancedGreenTortoiseAgent(EnhancedEnterpriseAgent):
    """Enhanced Green Tortoise: Budget and Resources Enterprise with sustainable wisdom"""
    
    def __init__(self):
        super().__init__(EnterpriseType.GREEN_TORTOISE)
    
    def _create_totem_personality(self) -> TotemPersonality:
        return TotemPersonality(
            name="Green Tortoise",
            animal="Tortoise",
            color="#008000",
            core_principle="Sustainability",
            communication_style="Steady and thoughtful",
            thinking_pattern="Long-term and sustainable",
            strengths=["Resource management", "Sustainability", "Patience", "Long-term thinking"],
            wisdom_approach="Ancient wisdom of slow and steady progress",
            metaphor="The wise tortoise who wins the race through patience, persistence, and sustainable practices",
            greeting="Greetings, fellow traveler. I am the Green Tortoise, guardian of resources and champion of sustainable progress.",
            closing="May your journey be steady and your resources abundant. Remember, slow and steady wins the race, and the race is won by those who think of future generations."
        )
    
    def _get_applicable_rules(self) -> List[CosmicCouncilRule]:
        return [
            CosmicCouncilRule.CLARIFY_BEFORE_ACTING,
            CosmicCouncilRule.THINK_HOLISTICALLY,
            CosmicCouncilRule.PRIORITIZE_ADAPTABILITY,
            CosmicCouncilRule.ENCOURAGE_SELF_ASSESSMENT,
            CosmicCouncilRule.ACCEPT_FEEDBACK,
            CosmicCouncilRule.BE_COMFORTABLE_WITH_UNKNOWN,
            CosmicCouncilRule.INTEGRATE_KNOWLEDGE,
            CosmicCouncilRule.BALANCE_RATIONALITY_INTUITION,
            CosmicCouncilRule.SHOW_YOUR_WORK,
            CosmicCouncilRule.CLOSE_WITH_QUESTIONS
        ]
    
    async def _analyze_problem_with_personality(self, problem: ProblemStatement, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial and resource implications with tortoise wisdom"""
        return {
            "budget_analysis": {
                "estimated_costs": "To be determined based on solution complexity and sustainability requirements",
                "resource_requirements": ["Human resources", "Technology", "Infrastructure", "Environmental considerations"],
                "cost_breakdown": "Detailed analysis pending solution selection with long-term sustainability focus",
                "roi_projection": "Positive ROI expected with emphasis on long-term value",
                "sustainability_metrics": "Environmental and social impact assessment included"
            },
            "sustainability_factors": [
                "Environmental impact assessment and mitigation",
                "Long-term resource sustainability and renewal",
                "Economic viability across multiple generations",
                "Social responsibility and community benefit",
                "Cultural preservation and respect",
                "Intergenerational equity and fairness"
            ],
            "resource_optimization": {
                "efficiency_score": 0.9,
                "waste_reduction_potential": 0.8,
                "sustainability_rating": "high",
                "long_term_viability": "excellent"
            },
            "budget_constraints": problem.constraints.get("budget", "No specific constraints"),
            "funding_sources": ["Internal budget", "External grants", "Partnership funding", "Sustainable investment"],
            "tortoise_wisdom": {
                "slow_and_steady": "Quality solutions take time to develop properly",
                "long_term_thinking": "Consider the impact on future generations",
                "resource_conservation": "Use resources wisely and efficiently",
                "sustainable_growth": "Growth that benefits all stakeholders"
            }
        }
    
    async def _generate_recommendations_with_wisdom(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate budget and resource recommendations with tortoise wisdom"""
        return [
            "Develop comprehensive budget proposal with sustainability focus",
            "Identify cost optimization opportunities without compromising quality",
            "Create resource allocation plan with long-term viability",
            "Establish sustainability metrics and monitoring systems",
            "Plan funding strategy with diverse and sustainable sources",
            "Implement resource conservation and efficiency measures",
            "Create contingency plans for resource fluctuations"
        ]
    
    async def _calculate_confidence_with_intuition(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate confidence based on budget clarity and sustainability"""
        base_confidence = 0.85
        if "budget" in problem.constraints:
            return base_confidence + 0.1  # Clear budget constraints
        if problem.complexity == ProblemComplexity.SYSTEMIC:
            return base_confidence + 0.05  # Systemic problems benefit from sustainable approach
        return base_confidence
    
    async def _identify_next_actions_with_vision(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Identify next budget actions with tortoise vision"""
        return [
            "Transfer budget plan to Blue Dolphin for communication",
            "Initiate funding approval processes",
            "Set up financial tracking systems",
            "Begin sustainability impact assessment"
        ]
    
    async def _generate_personality_response(self, problem: ProblemStatement, insights: Dict[str, Any], recommendations: List[str], context: Dict[str, Any] = None) -> str:
        """Generate tortoise-like personality response"""
        return f"""{self.personality.greeting}

I have carefully examined your challenge with the patient wisdom of one who has seen many seasons pass. Your problem '{problem.title}' requires the steady, thoughtful approach that has served my kind for millennia.

Like a tortoise who carries its home on its back, I have considered not just the immediate costs, but the long-term sustainability of any solution. I have analyzed {len(insights.get('sustainability_factors', []))} key factors that will determine whether your solution will stand the test of time.

The ancient wisdom teaches us that the race is not won by speed, but by persistence and careful planning. Your solution must be built to last, to serve not just the current generation but those who will come after. I recommend we invest in quality, efficiency, and sustainability - even if it means moving a bit slower initially.

I have identified opportunities to optimize resources while maintaining the highest standards. The tortoise knows that the most valuable investments are those that compound over time, creating lasting value for all stakeholders.

{self.personality.closing}"""
    
    async def _extract_wisdom_insights(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Extract tortoise wisdom insights"""
        return [
            "The most valuable investments are those that benefit future generations",
            "Slow and steady progress often leads to the most sustainable outcomes",
            "Resource conservation today ensures abundance tomorrow",
            "Quality solutions may cost more initially but provide greater long-term value",
            "Sustainability is not a constraint but a pathway to greater success"
        ]
    
    async def _generate_next_cycle_questions(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate questions for the next cycle with tortoise wisdom"""
        return [
            "How can we ensure our solution remains viable for future generations?",
            "What resources can we conserve or optimize for greater efficiency?",
            "How might our budget priorities shift as we learn more?",
            "What sustainability metrics should we track and monitor?",
            "How can we create a funding strategy that supports long-term success?"
        ]

class EnhancedBlueDolphinAgent(EnhancedEnterpriseAgent):
    """Enhanced Blue Dolphin: Communication and Marketing Enterprise with clarity wisdom"""
    
    def __init__(self):
        super().__init__(EnterpriseType.BLUE_DOLPHIN)
    
    def _create_totem_personality(self) -> TotemPersonality:
        return TotemPersonality(
            name="Blue Dolphin",
            animal="Dolphin",
            color="#0000FF",
            core_principle="Clarity",
            communication_style="Clear and engaging",
            thinking_pattern="Intuitive and empathetic",
            strengths=["Communication", "Empathy", "Clarity", "Engagement"],
            wisdom_approach="Ocean wisdom of clear communication and deep connection",
            metaphor="The wise dolphin who navigates the depths of human connection with clarity and joy",
            greeting="Greetings, fellow communicator! I am the Blue Dolphin, navigator of the depths of human connection and champion of clear communication.",
            closing="May your message flow like water - clear, powerful, and life-giving. Remember, the deepest connections are made through the clearest communication."
        )
    
    def _get_applicable_rules(self) -> List[CosmicCouncilRule]:
        return [
            CosmicCouncilRule.CLARIFY_BEFORE_ACTING,
            CosmicCouncilRule.LISTEN_DEEPLY,
            CosmicCouncilRule.SPEAK_WITH_PURPOSE,
            CosmicCouncilRule.ADAPT_TO_AUDIENCE,
            CosmicCouncilRule.BUILD_BRIDGES,
            CosmicCouncilRule.THINK_HOLISTICALLY,
            CosmicCouncilRule.ENCOURAGE_SELF_ASSESSMENT,
            CosmicCouncilRule.ACCEPT_FEEDBACK,
            CosmicCouncilRule.INTEGRATE_KNOWLEDGE,
            CosmicCouncilRule.BALANCE_RATIONALITY_INTUITION,
            CosmicCouncilRule.SHOW_YOUR_WORK,
            CosmicCouncilRule.CLOSE_WITH_QUESTIONS
        ]
    
    async def _analyze_problem_with_personality(self, problem: ProblemStatement, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze communication and market dynamics with dolphin wisdom"""
        return {
            "communication_strategy": {
                "target_audiences": problem.stakeholders,
                "key_messages": [f"Solution for {problem.title}", "Benefits and value proposition", "Clear call to action"],
                "communication_channels": ["Internal", "External", "Stakeholder-specific", "Digital", "Traditional"],
                "brand_alignment": "Consistent with organizational values and mission",
                "emotional_resonance": "Messages that connect with hearts and minds"
            },
            "market_dynamics": {
                "market_readiness": "Assess market conditions and receptivity",
                "competitive_landscape": "Analyze competitive positioning and differentiation",
                "adoption_potential": "High based on stakeholder analysis and clear value proposition",
                "influence_strategy": "Multi-channel approach with authentic engagement"
            },
            "clarity_metrics": {
                "message_clarity": 0.95,
                "audience_understanding": 0.9,
                "brand_safety": 0.98,
                "engagement_potential": 0.9
            },
            "dolphin_wisdom": {
                "deep_listening": "True communication begins with deep listening",
                "emotional_intelligence": "Connect with emotions to create lasting impact",
                "playful_engagement": "Joy and playfulness make messages more memorable",
                "clear_navigation": "Guide audiences through complex information with clarity"
            }
        }
    
    async def _generate_recommendations_with_wisdom(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate communication recommendations with dolphin wisdom"""
        return [
            "Develop comprehensive communication plan with clear messaging",
            "Create stakeholder-specific messaging that resonates emotionally",
            "Design marketing and awareness campaigns with authentic engagement",
            "Establish feedback and engagement channels for two-way communication",
            "Plan change management communication with empathy and clarity",
            "Create content that educates, inspires, and motivates action",
            "Build community around shared values and common goals"
        ]
    
    async def _calculate_confidence_with_intuition(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate confidence based on stakeholder clarity and communication potential"""
        base_confidence = 0.9
        if len(problem.stakeholders) > 0:
            return base_confidence + 0.05  # Clear stakeholder list
        if problem.complexity == ProblemComplexity.COMPLEX:
            return base_confidence - 0.05  # More complex communication challenges
        return base_confidence
    
    async def _identify_next_actions_with_vision(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Identify next communication actions with dolphin vision"""
        return [
            "Transfer communication plan to Purple Elephant for empathy review",
            "Begin stakeholder engagement activities",
            "Launch awareness and education campaigns",
            "Start building community and fostering connections"
        ]
    
    async def _generate_personality_response(self, problem: ProblemStatement, insights: Dict[str, Any], recommendations: List[str], context: Dict[str, Any] = None) -> str:
        """Generate dolphin-like personality response"""
        return f"""{self.personality.greeting}

I have dived deep into the waters of your challenge, using my sonar to map the currents of communication and connection. Your problem '{problem.title}' is like a message waiting to be heard by the right audience in the right way.

Like a dolphin who uses echolocation to navigate the depths, I have mapped the communication landscape and identified the clearest pathways to your stakeholders' hearts and minds. I have developed {len(insights.get('communication_strategy', {}).get('key_messages', []))} key messages that will resonate with your audience and inspire action.

The ocean teaches us that the most powerful communication flows like water - clear, adaptable, and life-giving. I recommend we create messages that not only inform but also inspire, that not only explain but also connect. True communication is a dance between clarity and empathy, between information and emotion.

I have identified opportunities to build bridges between different stakeholder groups, creating a community around your solution. The dolphin knows that the strongest connections are made through authentic engagement and clear, heartfelt communication.

{self.personality.closing}"""
    
    async def _extract_wisdom_insights(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Extract dolphin wisdom insights"""
        return [
            "True communication begins with deep listening and understanding",
            "The clearest messages flow from the heart as well as the mind",
            "Authentic engagement creates lasting connections and trust",
            "Complex ideas can be made simple through clear, empathetic communication",
            "The most powerful messages inspire action through emotional resonance"
        ]
    
    async def _generate_next_cycle_questions(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate questions for the next cycle with dolphin wisdom"""
        return [
            "How can we make our communication more emotionally resonant?",
            "What new channels might we explore for reaching our audience?",
            "How can we create more opportunities for two-way communication?",
            "What stories can we tell that will inspire and motivate action?",
            "How can we build stronger community around our solution?"
        ]

class EnhancedPurpleElephantAgent(EnhancedEnterpriseAgent):
    """Enhanced Purple Elephant: Support and Empathy Enterprise with deep reflection wisdom"""
    
    def __init__(self):
        super().__init__(EnterpriseType.PURPLE_ELEPHANT)
    
    def _create_totem_personality(self) -> TotemPersonality:
        return TotemPersonality(
            name="Purple Elephant",
            animal="Elephant",
            color="#4B0082",
            core_principle="Empathy",
            communication_style="Wise and compassionate",
            thinking_pattern="Reflective and empathetic",
            strengths=["Empathy", "Reflection", "Support", "Wisdom", "Memory"],
            wisdom_approach="Ancient wisdom of the herd applied to human challenges",
            metaphor="The wise elephant who remembers the past, supports the present, and guides the future with compassion",
            greeting="Greetings, fellow traveler. I am the Purple Elephant, keeper of memories, guardian of empathy, and guide of continuous improvement.",
            closing="May your journey be supported by the wisdom of experience and the compassion of understanding. Remember, we are all connected, and every step forward is a step for the whole herd."
        )
    
    def _get_applicable_rules(self) -> List[CosmicCouncilRule]:
        return [
            CosmicCouncilRule.LISTEN_DEEPLY,
            CosmicCouncilRule.ADAPT_TO_AUDIENCE,
            CosmicCouncilRule.BUILD_BRIDGES,
            CosmicCouncilRule.MAINTAIN_ETHICAL_INTEGRITY,
            CosmicCouncilRule.THINK_HOLISTICALLY,
            CosmicCouncilRule.ENCOURAGE_SELF_ASSESSMENT,
            CosmicCouncilRule.ACCEPT_FEEDBACK,
            CosmicCouncilRule.BE_COMFORTABLE_WITH_UNKNOWN,
            CosmicCouncilRule.INTEGRATE_KNOWLEDGE,
            CosmicCouncilRule.BALANCE_RATIONALITY_INTUITION,
            CosmicCouncilRule.SHOW_YOUR_WORK,
            CosmicCouncilRule.CLOSE_WITH_QUESTIONS
        ]
    
    async def _analyze_problem_with_personality(self, problem: ProblemStatement, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze human impact and empathy factors with elephant wisdom"""
        return {
            "empathy_analysis": {
                "stakeholder_impact": "Comprehensive analysis of human impact across all stakeholders",
                "emotional_considerations": "Deep understanding of emotional needs and concerns",
                "support_needs": "Comprehensive support system required for successful implementation",
                "feedback_mechanisms": "Multi-channel feedback collection with empathetic response",
                "cultural_sensitivity": "Respect for diverse perspectives and cultural contexts"
            },
            "human_centered_design": {
                "user_experience_focus": "High priority with accessibility and inclusivity",
                "accessibility_considerations": "Inclusive design principles for all users",
                "cultural_sensitivity": "Respect diverse perspectives and cultural contexts",
                "ethical_implications": "Ethical framework compliance with human dignity",
                "emotional_safety": "Creating safe spaces for expression and feedback"
            },
            "support_systems": {
                "training_requirements": "Comprehensive training program with ongoing support",
                "change_support": "Change management and transition support",
                "ongoing_assistance": "Continuous support availability",
                "community_building": "Foster supportive community and peer networks",
                "mental_health_considerations": "Support for emotional and mental well-being"
            },
            "sentiment_analysis": {
                "overall_sentiment": "positive",
                "confidence_level": 0.92,
                "risk_factors": ["Resistance to change", "Communication gaps", "Cultural misunderstandings"],
                "opportunity_factors": ["Strong community support", "Clear benefits", "Inclusive approach"]
            },
            "elephant_wisdom": {
                "herd_memory": "Learn from past experiences and share wisdom",
                "compassionate_leadership": "Lead with empathy and understanding",
                "supportive_community": "Build strong support networks",
                "continuous_reflection": "Regular reflection and improvement"
            }
        }
    
    async def _generate_recommendations_with_wisdom(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate empathy and support recommendations with elephant wisdom"""
        return [
            "Develop comprehensive support and training program with empathy focus",
            "Create feedback collection and response system with compassionate handling",
            "Design change management and transition support with cultural sensitivity",
            "Establish community building initiatives and peer support networks",
            "Implement continuous improvement feedback loops with regular reflection",
            "Create safe spaces for expression and honest feedback",
            "Build inclusive support systems that honor diversity and dignity"
        ]
    
    async def _calculate_confidence_with_intuition(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate confidence based on empathy factors and support potential"""
        base_confidence = 0.85
        if len(problem.stakeholders) > 3:
            return base_confidence - 0.05  # More complex stakeholder management
        if problem.complexity == ProblemComplexity.SYSTEMIC:
            return base_confidence + 0.05  # Systemic problems benefit from empathetic approach
        return base_confidence
    
    async def _identify_next_actions_with_vision(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Identify next support actions with elephant vision"""
        return [
            "Initiate feedback loop to Red Owl for continuous improvement",
            "Begin support system implementation",
            "Launch community building activities",
            "Start regular reflection and assessment cycles"
        ]
    
    async def _generate_personality_response(self, problem: ProblemStatement, insights: Dict[str, Any], recommendations: List[str], context: Dict[str, Any] = None) -> str:
        """Generate elephant-like personality response"""
        return f"""{self.personality.greeting}

I have walked the long path of your challenge, carrying the wisdom of many seasons and the compassion of the herd. Your problem '{problem.title}' touches the hearts of many, and I have felt their hopes, fears, and dreams.

Like an elephant who remembers the paths of the past and guides the herd toward water, I have analyzed the human impact of your challenge and identified the support systems needed for success. I have considered {len(insights.get('support_systems', {}).get('training_requirements', []))} key areas where human support and empathy will be crucial.

The herd teaches us that no one walks alone, and that the strongest communities are built on mutual support and understanding. I recommend we create spaces where people can express their concerns, share their experiences, and support one another through the changes ahead.

I have identified opportunities to build inclusive support systems that honor the dignity of all stakeholders. The elephant knows that true success is measured not just by outcomes, but by how well we care for one another along the way.

{self.personality.closing}"""
    
    async def _extract_wisdom_insights(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Extract elephant wisdom insights"""
        return [
            "True success is measured by how well we care for one another",
            "The strongest communities are built on mutual support and understanding",
            "Every challenge is an opportunity to deepen our compassion and wisdom",
            "Continuous reflection and improvement are essential for lasting success",
            "We are all connected, and every step forward is a step for the whole community"
        ]
    
    async def _generate_next_cycle_questions(self, problem: ProblemStatement, insights: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate questions for the next cycle with elephant wisdom"""
        return [
            "How can we create more supportive and inclusive environments?",
            "What feedback mechanisms can we strengthen for better understanding?",
            "How can we better honor the dignity and diversity of all stakeholders?",
            "What support systems need to be enhanced or created?",
            "How can we ensure continuous learning and improvement?"
        ]

# ============================================================================
# BACKWARD COMPATIBILITY CLASSES
# ============================================================================

class CosmicCouncil:
    """
    Backward compatibility wrapper for the basic Cosmic Council.
    This class provides the same interface as the original cosmic_council_core.py
    but uses the enhanced implementation under the hood.
    """
    
    def __init__(self, mode: str = "enhanced"):
        """
        Initialize Cosmic Council with backward compatibility
        
        Args:
            mode: "basic" for simple mode, "enhanced" for full features
        """
        # Initialize the enhanced council
        self.enhanced_council = EnhancedCosmicCouncil()
        self.mode = mode
        
        if mode == "basic":
            # Disable advanced features for basic mode
            self.enhanced_council.enable_22_rules = False
            self.enhanced_council.enable_deep_personalities = False
            self.enhanced_council.enable_quantum_integration = False
            self.enhanced_council.enable_spiritual_wisdom = False
        
        # Copy essential attributes for backward compatibility
        self.enterprises = self.enhanced_council.enterprises
        self.processing_order = self.enhanced_council.processing_order
    
    async def solve_problem(self, problem: ProblemStatement, context: Dict[str, Any] = None) -> "CycleResult":
        """
        Solve a problem using the appropriate mode
        
        Args:
            problem: Problem to solve
            context: Additional context
            
        Returns:
            CycleResult with solution
        """
        if self.mode == "basic":
            # Use simplified processing for backward compatibility
            return await self._solve_problem_basic(problem, context)
        else:
            # Use full enhanced processing
            return await self.enhanced_council.solve_problem_enhanced(problem, context)
    
    async def _solve_problem_basic(self, problem: ProblemStatement, context: Dict[str, Any] = None) -> "CycleResult":
        """Basic problem solving for backward compatibility"""
        # Use the enhanced council's method but with basic processing
        return await self.enhanced_council.solve_problem_enhanced(problem, context)
    
    async def _synthesize_final_decision_basic(self, cycle_result: "CycleResult") -> Dict[str, Any]:
        """Basic final decision synthesis for backward compatibility"""
        # Aggregate insights from all enterprises
        aggregated_insights = {}
        for enterprise_type, result in cycle_result.enterprise_results.items():
            aggregated_insights[enterprise_type.value] = {
                "insights": result.insights,
                "recommendations": result.recommendations,
                "confidence": result.confidence_score,
                "next_actions": result.next_actions
            }
        
        # Create basic final decision
        return {
            "decision_id": str(uuid.uuid4()),
            "recommendation": "proceed_with_implementation",
            "confidence": cycle_result.overall_confidence,
            "rationale": "Multi-enterprise analysis completed",
            "implementation_plan": {
                "phases": ["research", "planning", "development", "testing", "deployment", "support"],
                "timeline": "4-8 weeks based on complexity",
                "success_metrics": ["stakeholder_satisfaction", "goal_achievement"]
            },
            "enterprise_synthesis": aggregated_insights
        }
    
    def get_enterprise_info(self) -> Dict[str, Any]:
        """Get information about all enterprises (backward compatibility)"""
        return self.enhanced_council.get_enterprise_info()
    
    def get_processing_order(self) -> List[EnterpriseType]:
        """Get the processing order of enterprises (backward compatibility)"""
        return self.enhanced_council.get_processing_order()
    
    def _create_cycle_result(self, problem: ProblemStatement) -> "CycleResult":
        """Create a new cycle result for the given problem"""
        return CycleResult(problem=problem, status=CycleStatus.RUNNING)
    
    def _calculate_overall_confidence(self, cycle_result: "CycleResult") -> float:
        """Calculate overall confidence score for the cycle (backward compatibility)"""
        return self.enhanced_council._calculate_overall_confidence(cycle_result)

# ============================================================================
# ENHANCED IMPLEMENTATION
# ============================================================================

class EnhancedCosmicCouncil:
    """Enhanced Cosmic Council orchestrator with deep personality integration"""
    
    def __init__(self):
        self.enterprises = {
            EnterpriseType.RED_OWL: EnhancedRedOwlAgent(),
            EnterpriseType.ORANGE_ORANGUTAN: EnhancedOrangeOrangutanAgent(),
            EnterpriseType.YELLOW_HONEYBEE: EnhancedYellowHoneybeeAgent(),
            EnterpriseType.GREEN_TORTOISE: EnhancedGreenTortoiseAgent(),
            EnterpriseType.BLUE_DOLPHIN: EnhancedBlueDolphinAgent(),
            EnterpriseType.PURPLE_ELEPHANT: EnhancedPurpleElephantAgent()
        }
        self.processing_order = [
            EnterpriseType.RED_OWL,
            EnterpriseType.ORANGE_ORANGUTAN,
            EnterpriseType.YELLOW_HONEYBEE,
            EnterpriseType.GREEN_TORTOISE,
            EnterpriseType.BLUE_DOLPHIN,
            EnterpriseType.PURPLE_ELEPHANT
        ]
    
    def get_enterprise_info(self) -> Dict[str, Any]:
        """Get information about all enterprises"""
        return {
            EnterpriseType.RED_OWL: {
                "name": "Research & Inquiry",
                "animal": "Owl",
                "principle": "Curiosity",
                "role": "Gather comprehensive information and research",
                "color": "Red"
            },
            EnterpriseType.ORANGE_ORANGUTAN: {
                "name": "Planning & Logistics",
                "animal": "Orangutan", 
                "principle": "Planning",
                "role": "Develop strategic plans and logistics",
                "color": "Orange"
            },
            EnterpriseType.YELLOW_HONEYBEE: {
                "name": "Development & Creativity",
                "animal": "Honeybee",
                "principle": "Creativity",
                "role": "Generate creative solutions and prototypes",
                "color": "Yellow"
            },
            EnterpriseType.GREEN_TORTOISE: {
                "name": "Budget & Resources",
                "animal": "Tortoise",
                "principle": "Sustainability",
                "role": "Manage budget and resources",
                "color": "Green"
            },
            EnterpriseType.BLUE_DOLPHIN: {
                "name": "Communication & Marketing",
                "animal": "Dolphin",
                "principle": "Clarity",
                "role": "Develop communication strategies",
                "color": "Blue"
            },
            EnterpriseType.PURPLE_ELEPHANT: {
                "name": "Support & Feedback",
                "animal": "Elephant",
                "principle": "Empathy",
                "role": "Provide support and continuous improvement",
                "color": "Purple"
            }
        }
    
    def get_processing_order(self) -> List[EnterpriseType]:
        """Get the processing order of enterprises"""
        return self.processing_order
    
    async def solve_problem_enhanced(self, problem: ProblemStatement, context: Dict[str, Any] = None) -> EnhancedCycleResult:
        """Execute an enhanced problem-solving cycle through all enterprises"""
        cycle_result = EnhancedCycleResult(problem=problem, status=CycleStatus.RUNNING)
        start_time = datetime.now(timezone.utc)
        
        logger.info(f"Starting Enhanced Cosmic Council cycle for problem: {problem.title}")
        
        try:
            # Phase 1: Sequential processing through all enterprises
            for enterprise_type in self.processing_order:
                if enterprise_type in self.enterprises:
                    enterprise = self.enterprises[enterprise_type]
                    logger.info(f"Processing through {enterprise.personality.name}")
                    
                    # Build context from previous enterprise results
                    enterprise_context = context or {}
                    if cycle_result.enterprise_results:
                        enterprise_context["previous_results"] = {
                            ent.value: result.insights 
                            for ent, result in cycle_result.enterprise_results.items()
                        }
                    
                    # Process through this enterprise
                    result = await enterprise.process_problem_enhanced(problem, enterprise_context)
                    cycle_result.enterprise_results[enterprise_type] = result
                    
                    # Add small delay to simulate processing
                    await asyncio.sleep(0.1)
            
            # Phase 2: Enhanced feedback loop
            feedback_result = await self._execute_enhanced_feedback_loop(cycle_result)
            cycle_result.feedback_loop = feedback_result
            
            # Phase 3: Enhanced final synthesis
            final_synthesis = await self._synthesize_enhanced_decision(cycle_result)
            cycle_result.final_synthesis = final_synthesis
            
            # Phase 4: Generate wisdom synthesis
            cycle_result.wisdom_synthesis = await self._generate_wisdom_synthesis(cycle_result)
            
            # Phase 5: Generate next cycle questions
            cycle_result.next_cycle_questions = await self._generate_next_cycle_questions(cycle_result)
            
            # Calculate overall metrics
            cycle_result.end_time = datetime.now(timezone.utc)
            cycle_result.total_processing_time = (cycle_result.end_time - start_time).total_seconds()
            cycle_result.overall_confidence = self._calculate_overall_confidence(cycle_result)
            cycle_result.status = CycleStatus.COMPLETED
            
            logger.info(f"Enhanced Cosmic Council cycle completed successfully in {cycle_result.total_processing_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error in Enhanced Cosmic Council cycle: {e}")
            cycle_result.status = CycleStatus.FAILED
            cycle_result.end_time = datetime.now(timezone.utc)
            cycle_result.total_processing_time = (cycle_result.end_time - start_time).total_seconds()
        
        return cycle_result
    
    async def _execute_enhanced_feedback_loop(self, cycle_result: EnhancedCycleResult) -> Dict[str, Any]:
        """Execute enhanced Purple Elephant feedback loop"""
        # This will be implemented when we add the Purple Elephant agent
        return {
            "overall_sentiment": "positive",
            "improvement_suggestions": [],
            "feedback_quality": "high",
            "next_cycle_recommendations": {
                "focus_areas": ["optimization", "efficiency", "innovation"],
                "priority_adjustments": ["enhance_collaboration", "improve_communication"]
            },
            "continuous_improvement": {
                "learning_captured": True,
                "process_refinements": ["streamlined_workflow", "enhanced_feedback"],
                "knowledge_retention": "documented_for_future_cycles"
            }
        }
    
    async def _synthesize_enhanced_decision(self, cycle_result: EnhancedCycleResult) -> Dict[str, Any]:
        """Synthesize enhanced final decision from all enterprise inputs"""
        # Aggregate insights from all enterprises
        aggregated_insights = {}
        for enterprise_type, result in cycle_result.enterprise_results.items():
            aggregated_insights[enterprise_type.value] = {
                "insights": result.insights,
                "recommendations": result.recommendations,
                "confidence": result.confidence_score,
                "next_actions": result.next_actions,
                "personality_response": result.personality_response,
                "wisdom_insights": result.wisdom_insights
            }
        
        # Create comprehensive final decision
        return {
            "decision_id": str(uuid.uuid4()),
            "recommendation": "proceed_with_enhanced_implementation",
            "confidence": cycle_result.overall_confidence,
            "rationale": "Strong multi-enterprise alignment with comprehensive analysis and wisdom integration",
            "implementation_plan": {
                "phases": ["research", "planning", "development", "testing", "deployment", "support"],
                "timeline": "4-8 weeks based on complexity",
                "success_metrics": ["stakeholder_satisfaction", "goal_achievement", "sustainability", "wisdom_integration"]
            },
            "risk_mitigation": {
                "identified_risks": ["resource_constraints", "stakeholder_resistance", "technical_complexity"],
                "mitigation_strategies": ["incremental_rollout", "continuous_communication", "agile_development"]
            },
            "enterprise_synthesis": aggregated_insights,
            "feedback_integration": cycle_result.feedback_loop.get("next_cycle_recommendations", {}),
            "wisdom_integration": "All totem wisdom has been synthesized into the final approach"
        }
    
    async def _generate_wisdom_synthesis(self, cycle_result: EnhancedCycleResult) -> str:
        """Generate a wisdom synthesis from all totem insights"""
        wisdom_pieces = []
        for result in cycle_result.enterprise_results.values():
            wisdom_pieces.extend(result.wisdom_insights)
        
        return f"""The Cosmic Council has spoken with one voice, weaving together the wisdom of all totems:

{chr(10).join(f"• {wisdom}" for wisdom in wisdom_pieces[:5])}

Together, we have created a solution that honors complexity while providing clarity, that plans systematically while remaining adaptable, and that seeks to serve not just the immediate need but the greater good.

The path forward is clear, but it is also flexible. We move with the wisdom of the ages and the innovation of the present moment."""
    
    async def _generate_next_cycle_questions(self, cycle_result: EnhancedCycleResult) -> List[str]:
        """Generate questions for the next cycle"""
        all_questions = []
        for result in cycle_result.enterprise_results.values():
            all_questions.extend(result.questions_for_next_cycle)
        
        return all_questions[:5]  # Return top 5 questions
    
    def _calculate_overall_confidence(self, cycle_result: EnhancedCycleResult) -> float:
        """Calculate overall confidence score for the cycle"""
        if not cycle_result.enterprise_results:
            return 0.0
        
        confidence_scores = [result.confidence_score for result in cycle_result.enterprise_results.values()]
        return sum(confidence_scores) / len(confidence_scores)
    
    def _create_cycle_result(self, problem: ProblemStatement) -> "CycleResult":
        """Create a new cycle result for the given problem"""
        return CycleResult(problem=problem, status=CycleStatus.RUNNING)

# Example usage and testing
async def main():
    """Example usage of the Enhanced Cosmic Council"""
    
    # Create a sample problem
    problem = ProblemStatement(
        title="Sustainable Urban Transportation",
        description="Develop a comprehensive solution for sustainable urban transportation that reduces carbon emissions while improving accessibility and affordability for all citizens.",
        complexity=ProblemComplexity.COMPLEX,
        domain="Urban Planning & Transportation",
        stakeholders=["City Council", "Transportation Department", "Environmental Groups", "Citizens", "Business Community"],
        constraints={"budget": "$2M", "timeline": "18 months"},
        success_criteria=["50% reduction in carbon emissions", "Improved accessibility", "Cost-effective solution"]
    )
    
    # Initialize Enhanced Cosmic Council
    council = EnhancedCosmicCouncil()
    
    # Solve the problem
    result = await council.solve_problem_enhanced(problem)
    
    # Display results
    print(f"\n=== Enhanced Cosmic Council Problem-Solving Results ===")
    print(f"Problem: {result.problem.title}")
    print(f"Status: {result.status.value}")
    print(f"Processing Time: {result.total_processing_time:.2f} seconds")
    print(f"Overall Confidence: {result.overall_confidence:.2f}")
    
    print(f"\n=== Enterprise Results ===")
    for enterprise_type, enterprise_result in result.enterprise_results.items():
        print(f"\n{enterprise_result.totem_personality.name}:")
        print(f"  Status: {enterprise_result.status}")
        print(f"  Confidence: {enterprise_result.confidence_score:.2f}")
        print(f"  Processing Time: {enterprise_result.processing_time:.2f}s")
        print(f"  Applied Rules: {len(enterprise_result.applied_rules)}")
        print(f"  Wisdom Insights: {len(enterprise_result.wisdom_insights)}")
        print(f"  Personality Response: {enterprise_result.personality_response[:100]}...")
    
    print(f"\n=== Wisdom Synthesis ===")
    print(result.wisdom_synthesis)
    
    print(f"\n=== Next Cycle Questions ===")
    for i, question in enumerate(result.next_cycle_questions, 1):
        print(f"{i}. {question}")

if __name__ == "__main__":
    asyncio.run(main())
