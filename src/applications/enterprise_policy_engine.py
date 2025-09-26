"""
Enterprise Policy Engine for Cosmic Council
Advanced policy engine for enterprise decision-making and resource allocation
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolicyType(Enum):
    """Types of policies in the system"""
    ACCESS_CONTROL = "access_control"
    RESOURCE_ALLOCATION = "resource_allocation"
    BUDGET_MANAGEMENT = "budget_management"
    QUALITY_ASSURANCE = "quality_assurance"
    ETHICS_COMPLIANCE = "ethics_compliance"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_POLICY = "security_policy"
    SUSTAINABILITY = "sustainability"

class EnterpriseType(Enum):
    """Six Cosmic Council Enterprises"""
    RED_OWL = "red_owl"
    ORANGE_ORANGUTAN = "orange_orangutan"
    YELLOW_HONEYBEE = "yellow_honeybee"
    GREEN_TORTOISE = "green_tortoise"
    BLUE_DOLPHIN = "blue_dolphin"
    PURPLE_ELEPHANT = "purple_elephant"

class DecisionOutcome(Enum):
    """Policy decision outcomes"""
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"
    ESCALATE = "escalate"
    AUDIT = "audit"

class PolicySeverity(Enum):
    """Policy violation severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PolicyRule:
    """Individual policy rule definition"""
    rule_id: str
    name: str
    description: str
    policy_type: PolicyType
    enterprise: EnterpriseType
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    priority: int = 1
    enabled: bool = True
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PolicyDecision:
    """Policy decision result"""
    decision_id: str
    rule_id: str
    outcome: DecisionOutcome
    confidence: float
    reasoning: str
    obligations: List[str] = field(default_factory=list)
    violations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: float = 0.0

@dataclass
class ResourceRequest:
    """Resource allocation request"""
    request_id: str
    enterprise: EnterpriseType
    resource_type: str
    amount: float
    duration_hours: float
    priority: int
    justification: str
    requester_id: str
    context: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResourceAllocation:
    """Resource allocation result"""
    allocation_id: str
    request_id: str
    enterprise: EnterpriseType
    allocated_amount: float
    allocated_duration: float
    cost_estimate: float
    conditions: List[str] = field(default_factory=list)
    monitoring_requirements: List[str] = field(default_factory=list)
    approval_chain: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class BudgetCap:
    """Budget cap configuration"""
    enterprise: EnterpriseType
    monthly_cap: float
    quarterly_cap: float
    annual_cap: float
    current_usage: float = 0.0
    last_reset: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "warning": 0.8,
        "critical": 0.95
    })

class EnterprisePolicyEngine:
    """
    Advanced policy engine for enterprise decision-making and resource allocation
    """
    
    def __init__(self):
        self.policies: Dict[str, PolicyRule] = {}
        self.decisions: Dict[str, PolicyDecision] = {}
        self.resource_requests: Dict[str, ResourceRequest] = {}
        self.resource_allocations: Dict[str, ResourceAllocation] = {}
        self.budget_caps: Dict[EnterpriseType, BudgetCap] = {}
        self.policy_history: List[Dict[str, Any]] = []
        
        # Initialize default policies
        self._initialize_default_policies()
        
        # Initialize budget caps
        self._initialize_budget_caps()
        
        logger.info("Enterprise Policy Engine initialized")

    def _initialize_default_policies(self):
        """Initialize default policies for all enterprises"""
        
        # Red Owl - Knowledge and Research Policies
        self._add_policy(PolicyRule(
            rule_id="red_owl_knowledge_access",
            name="Red Owl Knowledge Access",
            description="Controls access to knowledge and research resources",
            policy_type=PolicyType.ACCESS_CONTROL,
            enterprise=EnterpriseType.RED_OWL,
            conditions={
                "resource_type": "knowledge_base",
                "access_level": "research",
                "authentication": "required"
            },
            actions={
                "allow": True,
                "audit": True,
                "rate_limit": "1000/hour"
            },
            priority=1
        ))
        
        self._add_policy(PolicyRule(
            rule_id="red_owl_data_quality",
            name="Red Owl Data Quality",
            description="Ensures data quality standards for research",
            policy_type=PolicyType.QUALITY_ASSURANCE,
            enterprise=EnterpriseType.RED_OWL,
            conditions={
                "data_source": "external",
                "quality_score": ">= 0.8",
                "verification": "required"
            },
            actions={
                "validate": True,
                "flag_low_quality": True,
                "require_verification": True
            },
            priority=2
        ))
        
        # Orange Orangutan - Logistics and Planning Policies
        self._add_policy(PolicyRule(
            rule_id="orange_planning_approval",
            name="Orange Orangutan Planning Approval",
            description="Approves logistics and planning decisions",
            policy_type=PolicyType.ACCESS_CONTROL,
            enterprise=EnterpriseType.ORANGE_ORANGUTAN,
            conditions={
                "planning_scope": "strategic",
                "resource_impact": "high",
                "timeline": ">= 30 days"
            },
            actions={
                "require_approval": True,
                "escalate_to_ceo": True,
                "audit": True
            },
            priority=1
        ))
        
        self._add_policy(PolicyRule(
            rule_id="orange_resource_efficiency",
            name="Orange Resource Efficiency",
            description="Ensures efficient resource utilization",
            policy_type=PolicyType.PERFORMANCE_OPTIMIZATION,
            enterprise=EnterpriseType.ORANGE_ORANGUTAN,
            conditions={
                "efficiency_threshold": ">= 0.85",
                "waste_tolerance": "<= 0.05"
            },
            actions={
                "optimize": True,
                "flag_inefficiency": True,
                "recommend_improvements": True
            },
            priority=2
        ))
        
        # Yellow Honeybee - Development and Innovation Policies
        self._add_policy(PolicyRule(
            rule_id="yellow_innovation_safety",
            name="Yellow Honeybee Innovation Safety",
            description="Ensures safe innovation practices",
            policy_type=PolicyType.SECURITY_POLICY,
            enterprise=EnterpriseType.YELLOW_HONEYBEE,
            conditions={
                "innovation_risk": "<= 0.3",
                "safety_protocols": "required",
                "testing_coverage": ">= 0.8"
            },
            actions={
                "require_safety_review": True,
                "mandate_testing": True,
                "approve_innovation": True
            },
            priority=1
        ))
        
        self._add_policy(PolicyRule(
            rule_id="yellow_creativity_boost",
            name="Yellow Creativity Boost",
            description="Promotes creative thinking and innovation",
            policy_type=PolicyType.PERFORMANCE_OPTIMIZATION,
            enterprise=EnterpriseType.YELLOW_HONEYBEE,
            conditions={
                "creativity_score": ">= 0.7",
                "innovation_potential": "high"
            },
            actions={
                "allocate_creative_resources": True,
                "provide_innovation_time": True,
                "celebrate_achievements": True
            },
            priority=3
        ))
        
        # Green Tortoise - Resource and Sustainability Policies
        self._add_policy(PolicyRule(
            rule_id="green_budget_control",
            name="Green Tortoise Budget Control",
            description="Controls budget allocation and spending",
            policy_type=PolicyType.BUDGET_MANAGEMENT,
            enterprise=EnterpriseType.GREEN_TORTOISE,
            conditions={
                "budget_usage": "<= cap",
                "approval_required": "> 10000",
                "sustainability_score": ">= 0.8"
            },
            actions={
                "approve_budget": True,
                "flag_overspend": True,
                "require_justification": True
            },
            priority=1
        ))
        
        self._add_policy(PolicyRule(
            rule_id="green_sustainability",
            name="Green Sustainability",
            description="Ensures sustainable resource usage",
            policy_type=PolicyType.SUSTAINABILITY,
            enterprise=EnterpriseType.GREEN_TORTOISE,
            conditions={
                "carbon_footprint": "<= limit",
                "renewable_energy": ">= 0.5",
                "waste_reduction": ">= 0.2"
            },
            actions={
                "approve_sustainable": True,
                "flag_unsustainable": True,
                "recommend_alternatives": True
            },
            priority=1
        ))
        
        # Blue Dolphin - Communication and Marketing Policies
        self._add_policy(PolicyRule(
            rule_id="blue_brand_safety",
            name="Blue Dolphin Brand Safety",
            description="Ensures brand safety in communications",
            policy_type=PolicyType.ACCESS_CONTROL,
            enterprise=EnterpriseType.BLUE_DOLPHIN,
            conditions={
                "brand_safety_score": ">= 0.9",
                "content_approval": "required",
                "stakeholder_impact": "assessed"
            },
            actions={
                "approve_communication": True,
                "flag_risky_content": True,
                "require_review": True
            },
            priority=1
        ))
        
        self._add_policy(PolicyRule(
            rule_id="blue_stakeholder_engagement",
            name="Blue Stakeholder Engagement",
            description="Manages stakeholder communication",
            policy_type=PolicyType.ACCESS_CONTROL,
            enterprise=EnterpriseType.BLUE_DOLPHIN,
            conditions={
                "stakeholder_priority": "high",
                "communication_urgency": "normal",
                "message_clarity": ">= 0.8"
            },
            actions={
                "prioritize_communication": True,
                "ensure_clarity": True,
                "track_engagement": True
            },
            priority=2
        ))
        
        # Purple Elephant - Empathy and Ethics Policies
        self._add_policy(PolicyRule(
            rule_id="purple_ethics_compliance",
            name="Purple Elephant Ethics Compliance",
            description="Ensures ethical decision-making",
            policy_type=PolicyType.ETHICS_COMPLIANCE,
            enterprise=EnterpriseType.PURPLE_ELEPHANT,
            conditions={
                "ethics_score": ">= 0.9",
                "stakeholder_impact": "positive",
                "transparency": "required"
            },
            actions={
                "approve_ethical": True,
                "flag_unethical": True,
                "require_ethics_review": True
            },
            priority=1
        ))
        
        self._add_policy(PolicyRule(
            rule_id="purple_empathy_enhancement",
            name="Purple Empathy Enhancement",
            description="Enhances empathy in decision-making",
            policy_type=PolicyType.PERFORMANCE_OPTIMIZATION,
            enterprise=EnterpriseType.PURPLE_ELEPHANT,
            conditions={
                "empathy_score": ">= 0.8",
                "human_centered": True,
                "inclusive_design": True
            },
            actions={
                "enhance_empathy": True,
                "promote_inclusion": True,
                "celebrate_humanity": True
            },
            priority=2
        ))

    def _initialize_budget_caps(self):
        """Initialize budget caps for all enterprises"""
        default_caps = {
            EnterpriseType.RED_OWL: BudgetCap(
                enterprise=EnterpriseType.RED_OWL,
                monthly_cap=50000.0,
                quarterly_cap=150000.0,
                annual_cap=600000.0
            ),
            EnterpriseType.ORANGE_ORANGUTAN: BudgetCap(
                enterprise=EnterpriseType.ORANGE_ORANGUTAN,
                monthly_cap=40000.0,
                quarterly_cap=120000.0,
                annual_cap=480000.0
            ),
            EnterpriseType.YELLOW_HONEYBEE: BudgetCap(
                enterprise=EnterpriseType.YELLOW_HONEYBEE,
                monthly_cap=60000.0,
                quarterly_cap=180000.0,
                annual_cap=720000.0
            ),
            EnterpriseType.GREEN_TORTOISE: BudgetCap(
                enterprise=EnterpriseType.GREEN_TORTOISE,
                monthly_cap=30000.0,
                quarterly_cap=90000.0,
                annual_cap=360000.0
            ),
            EnterpriseType.BLUE_DOLPHIN: BudgetCap(
                enterprise=EnterpriseType.BLUE_DOLPHIN,
                monthly_cap=35000.0,
                quarterly_cap=105000.0,
                annual_cap=420000.0
            ),
            EnterpriseType.PURPLE_ELEPHANT: BudgetCap(
                enterprise=EnterpriseType.PURPLE_ELEPHANT,
                monthly_cap=25000.0,
                quarterly_cap=75000.0,
                annual_cap=300000.0
            )
        }
        
        for enterprise, cap in default_caps.items():
            self.budget_caps[enterprise] = cap

    def _add_policy(self, policy: PolicyRule):
        """Add a policy to the engine"""
        self.policies[policy.rule_id] = policy
        logger.info(f"Added policy: {policy.name}")

    async def evaluate_policy(self, rule_id: str, context: Dict[str, Any]) -> PolicyDecision:
        """Evaluate a specific policy rule"""
        if rule_id not in self.policies:
            raise ValueError(f"Policy rule {rule_id} not found")
        
        policy = self.policies[rule_id]
        start_time = datetime.now()
        
        try:
            # Evaluate conditions
            outcome, confidence, reasoning, obligations, violations = await self._evaluate_conditions(
                policy, context
            )
            
            decision = PolicyDecision(
                decision_id=str(uuid.uuid4()),
                rule_id=rule_id,
                outcome=outcome,
                confidence=confidence,
                reasoning=reasoning,
                obligations=obligations,
                violations=violations,
                metadata={
                    "policy_name": policy.name,
                    "policy_type": policy.policy_type.value,
                    "enterprise": policy.enterprise.value,
                    "priority": policy.priority
                }
            )
            
            decision.latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Store decision
            self.decisions[decision.decision_id] = decision
            
            # Log to history
            self.policy_history.append({
                "timestamp": decision.timestamp,
                "rule_id": rule_id,
                "outcome": outcome.value,
                "confidence": confidence,
                "context": context
            })
            
            logger.info(f"Policy {rule_id} evaluated: {outcome.value} (confidence: {confidence:.2f})")
            
            return decision
            
        except Exception as e:
            logger.error(f"Error evaluating policy {rule_id}: {str(e)}")
            raise

    async def _evaluate_conditions(self, policy: PolicyRule, context: Dict[str, Any]) -> Tuple[
        DecisionOutcome, float, str, List[str], List[Dict[str, Any]]
    ]:
        """Evaluate policy conditions and return decision components"""
        conditions = policy.conditions
        actions = policy.actions
        
        # Initialize result components
        outcome = DecisionOutcome.ALLOW
        confidence = 1.0
        reasoning = f"Policy {policy.name} evaluation"
        obligations = []
        violations = []
        
        # Evaluate based on policy type
        if policy.policy_type == PolicyType.ACCESS_CONTROL:
            outcome, confidence, reasoning, obligations, violations = await self._evaluate_access_control(
                conditions, actions, context
            )
        elif policy.policy_type == PolicyType.RESOURCE_ALLOCATION:
            outcome, confidence, reasoning, obligations, violations = await self._evaluate_resource_allocation(
                conditions, actions, context
            )
        elif policy.policy_type == PolicyType.BUDGET_MANAGEMENT:
            outcome, confidence, reasoning, obligations, violations = await self._evaluate_budget_management(
                conditions, actions, context
            )
        elif policy.policy_type == PolicyType.QUALITY_ASSURANCE:
            outcome, confidence, reasoning, obligations, violations = await self._evaluate_quality_assurance(
                conditions, actions, context
            )
        elif policy.policy_type == PolicyType.ETHICS_COMPLIANCE:
            outcome, confidence, reasoning, obligations, violations = await self._evaluate_ethics_compliance(
                conditions, actions, context
            )
        elif policy.policy_type == PolicyType.PERFORMANCE_OPTIMIZATION:
            outcome, confidence, reasoning, obligations, violations = await self._evaluate_performance_optimization(
                conditions, actions, context
            )
        elif policy.policy_type == PolicyType.SECURITY_POLICY:
            outcome, confidence, reasoning, obligations, violations = await self._evaluate_security_policy(
                conditions, actions, context
            )
        elif policy.policy_type == PolicyType.SUSTAINABILITY:
            outcome, confidence, reasoning, obligations, violations = await self._evaluate_sustainability(
                conditions, actions, context
            )
        
        return outcome, confidence, reasoning, obligations, violations

    async def _evaluate_access_control(self, conditions: Dict[str, Any], actions: Dict[str, Any], 
                                     context: Dict[str, Any]) -> Tuple[DecisionOutcome, float, str, List[str], List[Dict[str, Any]]]:
        """Evaluate access control policies"""
        # Check authentication
        if conditions.get("authentication") == "required":
            if not context.get("authenticated", False):
                return DecisionOutcome.DENY, 1.0, "Authentication required", [], [
                    {"code": "AUTH_REQUIRED", "severity": "high", "message": "User must be authenticated"}
                ]
        
        # Check access level
        required_level = conditions.get("access_level")
        user_level = context.get("access_level", "basic")
        if required_level and user_level != required_level:
            return DecisionOutcome.DENY, 0.8, f"Access level {user_level} insufficient for {required_level}", [], [
                {"code": "INSUFFICIENT_ACCESS", "severity": "medium", "message": f"Required: {required_level}, Current: {user_level}"}
            ]
        
        # Check rate limiting
        if "rate_limit" in actions:
            rate_limit = actions["rate_limit"]
            # Simplified rate limiting check
            if context.get("request_count", 0) > 1000:  # Simplified check
                return DecisionOutcome.DENY, 0.9, "Rate limit exceeded", [], [
                    {"code": "RATE_LIMIT", "severity": "medium", "message": "Request rate too high"}
                ]
        
        obligations = []
        if actions.get("audit"):
            obligations.append("audit_logging")
        if actions.get("rate_limit"):
            obligations.append("rate_monitoring")
        
        return DecisionOutcome.ALLOW, 0.95, "Access granted", obligations, []

    async def _evaluate_resource_allocation(self, conditions: Dict[str, Any], actions: Dict[str, Any], 
                                          context: Dict[str, Any]) -> Tuple[DecisionOutcome, float, str, List[str], List[Dict[str, Any]]]:
        """Evaluate resource allocation policies"""
        requested_amount = context.get("amount", 0)
        available_resources = context.get("available_resources", 0)
        
        if requested_amount > available_resources:
            return DecisionOutcome.DENY, 1.0, "Insufficient resources available", [], [
                {"code": "INSUFFICIENT_RESOURCES", "severity": "high", "message": f"Requested: {requested_amount}, Available: {available_resources}"}
            ]
        
        # Check priority
        priority = context.get("priority", 5)
        if priority < 3:  # High priority
            confidence = 0.95
        elif priority < 6:  # Medium priority
            confidence = 0.8
        else:  # Low priority
            confidence = 0.6
        
        obligations = []
        if actions.get("monitor_usage"):
            obligations.append("resource_monitoring")
        if actions.get("require_approval"):
            obligations.append("approval_workflow")
        
        return DecisionOutcome.ALLOW, confidence, "Resource allocation approved", obligations, []

    async def _evaluate_budget_management(self, conditions: Dict[str, Any], actions: Dict[str, Any], 
                                        context: Dict[str, Any]) -> Tuple[DecisionOutcome, float, str, List[str], List[Dict[str, Any]]]:
        """Evaluate budget management policies"""
        enterprise = context.get("enterprise")
        requested_amount = context.get("amount", 0)
        
        if enterprise and enterprise in self.budget_caps:
            budget_cap = self.budget_caps[enterprise]
            current_usage = budget_cap.current_usage
            monthly_cap = budget_cap.monthly_cap
            
            if current_usage + requested_amount > monthly_cap:
                return DecisionOutcome.DENY, 1.0, "Budget cap exceeded", [], [
                    {"code": "BUDGET_EXCEEDED", "severity": "critical", "message": f"Would exceed monthly cap of {monthly_cap}"}
                ]
            
            # Check warning threshold
            if current_usage + requested_amount > monthly_cap * budget_cap.alert_thresholds["warning"]:
                obligations = ["budget_warning"]
                confidence = 0.7
            else:
                obligations = []
                confidence = 0.9
        else:
            obligations = []
            confidence = 0.8
        
        if actions.get("require_justification"):
            obligations.append("budget_justification")
        if actions.get("audit"):
            obligations.append("budget_audit")
        
        return DecisionOutcome.ALLOW, confidence, "Budget allocation approved", obligations, []

    async def _evaluate_quality_assurance(self, conditions: Dict[str, Any], actions: Dict[str, Any], 
                                        context: Dict[str, Any]) -> Tuple[DecisionOutcome, float, str, List[str], List[Dict[str, Any]]]:
        """Evaluate quality assurance policies"""
        quality_score = context.get("quality_score", 0.5)
        required_score = float(conditions.get("quality_score", ">= 0.8").replace(">=", ""))
        
        if quality_score < required_score:
            return DecisionOutcome.DENY, 0.9, f"Quality score {quality_score} below required {required_score}", [], [
                {"code": "LOW_QUALITY", "severity": "high", "message": f"Quality score {quality_score} below threshold {required_score}"}
            ]
        
        obligations = []
        if actions.get("validate"):
            obligations.append("quality_validation")
        if actions.get("flag_low_quality"):
            obligations.append("quality_monitoring")
        
        confidence = min(0.95, quality_score + 0.1)
        return DecisionOutcome.ALLOW, confidence, "Quality standards met", obligations, []

    async def _evaluate_ethics_compliance(self, conditions: Dict[str, Any], actions: Dict[str, Any], 
                                        context: Dict[str, Any]) -> Tuple[DecisionOutcome, float, str, List[str], List[Dict[str, Any]]]:
        """Evaluate ethics compliance policies"""
        ethics_score = context.get("ethics_score", 0.5)
        required_score = float(conditions.get("ethics_score", ">= 0.9").replace(">=", ""))
        
        if ethics_score < required_score:
            return DecisionOutcome.DENY, 1.0, f"Ethics score {ethics_score} below required {required_score}", [], [
                {"code": "ETHICS_VIOLATION", "severity": "critical", "message": f"Ethics score {ethics_score} below threshold {required_score}"}
            ]
        
        stakeholder_impact = context.get("stakeholder_impact", "neutral")
        if stakeholder_impact == "negative":
            return DecisionOutcome.DENY, 0.95, "Negative stakeholder impact detected", [], [
                {"code": "NEGATIVE_IMPACT", "severity": "high", "message": "Negative stakeholder impact"}
            ]
        
        obligations = []
        if actions.get("require_ethics_review"):
            obligations.append("ethics_review")
        if actions.get("audit"):
            obligations.append("ethics_audit")
        
        confidence = min(0.95, ethics_score + 0.05)
        return DecisionOutcome.ALLOW, confidence, "Ethics compliance verified", obligations, []

    async def _evaluate_performance_optimization(self, conditions: Dict[str, Any], actions: Dict[str, Any], 
                                               context: Dict[str, Any]) -> Tuple[DecisionOutcome, float, str, List[str], List[Dict[str, Any]]]:
        """Evaluate performance optimization policies"""
        performance_score = context.get("performance_score", 0.5)
        efficiency_threshold = float(conditions.get("efficiency_threshold", ">= 0.85").replace(">=", ""))
        
        if performance_score < efficiency_threshold:
            obligations = ["performance_optimization"]
            confidence = 0.6
            reasoning = f"Performance score {performance_score} below threshold {efficiency_threshold}, optimization recommended"
        else:
            obligations = []
            confidence = 0.9
            reasoning = "Performance standards met"
        
        if actions.get("optimize"):
            obligations.append("performance_monitoring")
        if actions.get("recommend_improvements"):
            obligations.append("improvement_recommendations")
        
        return DecisionOutcome.ALLOW, confidence, reasoning, obligations, []

    async def _evaluate_security_policy(self, conditions: Dict[str, Any], actions: Dict[str, Any], 
                                      context: Dict[str, Any]) -> Tuple[DecisionOutcome, float, str, List[str], List[Dict[str, Any]]]:
        """Evaluate security policies"""
        risk_level = context.get("risk_level", 0.5)
        max_risk = float(conditions.get("innovation_risk", "<= 0.3").replace("<=", ""))
        
        if risk_level > max_risk:
            return DecisionOutcome.DENY, 0.95, f"Risk level {risk_level} exceeds maximum {max_risk}", [], [
                {"code": "HIGH_RISK", "severity": "high", "message": f"Risk level {risk_level} exceeds threshold {max_risk}"}
            ]
        
        safety_protocols = context.get("safety_protocols", False)
        if conditions.get("safety_protocols") == "required" and not safety_protocols:
            return DecisionOutcome.DENY, 1.0, "Safety protocols required but not implemented", [], [
                {"code": "SAFETY_PROTOCOLS", "severity": "critical", "message": "Safety protocols must be implemented"}
            ]
        
        obligations = []
        if actions.get("require_safety_review"):
            obligations.append("safety_review")
        if actions.get("mandate_testing"):
            obligations.append("testing_requirements")
        
        confidence = 0.9 - (risk_level * 0.3)  # Higher risk = lower confidence
        return DecisionOutcome.ALLOW, confidence, "Security requirements met", obligations, []

    async def _evaluate_sustainability(self, conditions: Dict[str, Any], actions: Dict[str, Any], 
                                     context: Dict[str, Any]) -> Tuple[DecisionOutcome, float, str, List[str], List[Dict[str, Any]]]:
        """Evaluate sustainability policies"""
        carbon_footprint = context.get("carbon_footprint", 100)
        carbon_limit = float(conditions.get("carbon_footprint", "<= limit").replace("<=", "").replace("limit", "50"))
        
        if carbon_footprint > carbon_limit:
            return DecisionOutcome.DENY, 0.9, f"Carbon footprint {carbon_footprint} exceeds limit {carbon_limit}", [], [
                {"code": "CARBON_EXCEEDED", "severity": "high", "message": f"Carbon footprint {carbon_footprint} exceeds limit {carbon_limit}"}
            ]
        
        renewable_energy = context.get("renewable_energy", 0.3)
        required_renewable = float(conditions.get("renewable_energy", ">= 0.5").replace(">=", ""))
        
        if renewable_energy < required_renewable:
            obligations = ["sustainability_improvement"]
            confidence = 0.7
        else:
            obligations = []
            confidence = 0.9
        
        if actions.get("recommend_alternatives"):
            obligations.append("sustainability_alternatives")
        
        return DecisionOutcome.ALLOW, confidence, "Sustainability requirements met", obligations, []

    async def request_resource_allocation(self, request: ResourceRequest) -> ResourceAllocation:
        """Process a resource allocation request"""
        # Evaluate relevant policies
        relevant_policies = [
            policy for policy in self.policies.values()
            if (policy.enterprise == request.enterprise and 
                policy.policy_type in [PolicyType.RESOURCE_ALLOCATION, PolicyType.BUDGET_MANAGEMENT])
        ]
        
        # Sort by priority
        relevant_policies.sort(key=lambda p: p.priority)
        
        # Evaluate each policy
        approved = True
        total_confidence = 1.0
        all_obligations = []
        all_conditions = []
        
        for policy in relevant_policies:
            context = {
                "enterprise": request.enterprise,
                "amount": request.amount,
                "duration_hours": request.duration_hours,
                "priority": request.priority,
                "resource_type": request.resource_type,
                **request.context
            }
            
            decision = await self.evaluate_policy(policy.rule_id, context)
            
            if decision.outcome == DecisionOutcome.DENY:
                approved = False
                break
            
            total_confidence *= decision.confidence
            all_obligations.extend(decision.obligations)
            all_conditions.extend(decision.reasoning.split("; "))
        
        if not approved:
            raise ValueError("Resource allocation request denied by policy evaluation")
        
        # Create allocation
        allocation = ResourceAllocation(
            allocation_id=str(uuid.uuid4()),
            request_id=request.request_id,
            enterprise=request.enterprise,
            allocated_amount=request.amount,
            allocated_duration=request.duration_hours,
            cost_estimate=request.amount * request.duration_hours * 0.1,  # Simplified cost calculation
            conditions=all_conditions,
            monitoring_requirements=all_obligations,
            approval_chain=[policy.rule_id for policy in relevant_policies],
            metadata={
                "confidence": total_confidence,
                "policy_evaluations": len(relevant_policies)
            }
        )
        
        # Store allocation
        self.resource_allocations[allocation.allocation_id] = allocation
        self.resource_requests[request.request_id] = request
        
        # Update budget usage
        if request.enterprise in self.budget_caps:
            self.budget_caps[request.enterprise].current_usage += allocation.cost_estimate
        
        logger.info(f"Resource allocation approved: {allocation.allocation_id}")
        return allocation

    def get_policy_analytics(self) -> Dict[str, Any]:
        """Get analytics about policy decisions and performance"""
        total_decisions = len(self.decisions)
        if total_decisions == 0:
            return {"total_decisions": 0}
        
        # Calculate decision outcomes
        outcomes = {}
        for decision in self.decisions.values():
            outcome = decision.outcome.value
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        
        # Calculate average confidence
        avg_confidence = sum(d.confidence for d in self.decisions.values()) / total_decisions
        
        # Calculate average latency
        avg_latency = sum(d.latency_ms for d in self.decisions.values()) / total_decisions
        
        # Calculate policy performance
        policy_performance = {}
        for rule_id, policy in self.policies.items():
            policy_decisions = [d for d in self.decisions.values() if d.rule_id == rule_id]
            if policy_decisions:
                policy_performance[rule_id] = {
                    "name": policy.name,
                    "total_decisions": len(policy_decisions),
                    "avg_confidence": sum(d.confidence for d in policy_decisions) / len(policy_decisions),
                    "allow_rate": sum(1 for d in policy_decisions if d.outcome == DecisionOutcome.ALLOW) / len(policy_decisions)
                }
        
        # Calculate enterprise performance
        enterprise_performance = {}
        for enterprise in EnterpriseType:
            enterprise_policies = [p for p in self.policies.values() if p.enterprise == enterprise]
            enterprise_decisions = [d for d in self.decisions.values() if d.rule_id in [p.rule_id for p in enterprise_policies]]
            
            if enterprise_decisions:
                enterprise_performance[enterprise.value] = {
                    "total_decisions": len(enterprise_decisions),
                    "avg_confidence": sum(d.confidence for d in enterprise_decisions) / len(enterprise_decisions),
                    "allow_rate": sum(1 for d in enterprise_decisions if d.outcome == DecisionOutcome.ALLOW) / len(enterprise_decisions)
                }
        
        return {
            "total_decisions": total_decisions,
            "decision_outcomes": outcomes,
            "average_confidence": avg_confidence,
            "average_latency_ms": avg_latency,
            "policy_performance": policy_performance,
            "enterprise_performance": enterprise_performance,
            "total_policies": len(self.policies),
            "total_resource_allocations": len(self.resource_allocations),
            "budget_usage": {
                enterprise.value: {
                    "current_usage": cap.current_usage,
                    "monthly_cap": cap.monthly_cap,
                    "usage_percentage": (cap.current_usage / cap.monthly_cap) * 100
                }
                for enterprise, cap in self.budget_caps.items()
            }
        }

    def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status for all enterprises"""
        return {
            enterprise.value: {
                "current_usage": cap.current_usage,
                "monthly_cap": cap.monthly_cap,
                "quarterly_cap": cap.quarterly_cap,
                "annual_cap": cap.annual_cap,
                "usage_percentage": (cap.current_usage / cap.monthly_cap) * 100,
                "warning_threshold": cap.alert_thresholds["warning"] * 100,
                "critical_threshold": cap.alert_thresholds["critical"] * 100,
                "last_reset": cap.last_reset.isoformat()
            }
            for enterprise, cap in self.budget_caps.items()
        }

    def reset_budget_usage(self, enterprise: EnterpriseType):
        """Reset budget usage for an enterprise"""
        if enterprise in self.budget_caps:
            self.budget_caps[enterprise].current_usage = 0.0
            self.budget_caps[enterprise].last_reset = datetime.now(timezone.utc)
            logger.info(f"Budget usage reset for {enterprise.value}")

    def add_policy(self, policy: PolicyRule):
        """Add a new policy to the engine"""
        self._add_policy(policy)

    def update_policy(self, rule_id: str, updates: Dict[str, Any]):
        """Update an existing policy"""
        if rule_id not in self.policies:
            raise ValueError(f"Policy {rule_id} not found")
        
        policy = self.policies[rule_id]
        for key, value in updates.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        
        policy.updated_at = datetime.now(timezone.utc)
        logger.info(f"Policy {rule_id} updated")

    def remove_policy(self, rule_id: str):
        """Remove a policy from the engine"""
        if rule_id in self.policies:
            del self.policies[rule_id]
            logger.info(f"Policy {rule_id} removed")

# Global instance
policy_engine = EnterprisePolicyEngine()
