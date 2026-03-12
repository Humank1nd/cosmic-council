"""
Enhanced Governance Enforcement Integration for Agent Orchestrator
Integrates the enhanced enforcement system with agent performance tracking
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

# Import the enhanced enforcement system
from governance.enhanced_enforcement_system import (
    EnhancedCosmicCouncilEnforcementSystem,
    AgentProfile,
    AgentLevel,
    EnforcementAction,
    EnforcementRecord
)

# Import the enhanced agent performance tracking system
from enhanced_agent_performance_tracking import (
    EnhancedAgentPerformanceTracking,
    PerformanceMetric,
    PerformanceTrend,
    AgentPerformanceProfile
)

# Import the enhanced AI agent system
from enhanced_ai_agent_system import CosmicCouncilAgent, AgentType, AgentContext, AgentResult

logger = logging.getLogger(__name__)

class GovernanceLevel(Enum):
    """Levels of governance enforcement"""
    BASIC = "basic"                         # Basic rule enforcement
    ENHANCED = "enhanced"                   # Enhanced monitoring and feedback
    INTELLIGENT = "intelligent"             # AI-driven governance
    ADAPTIVE = "adaptive"                   # Self-adapting governance
    TRANSCENDENT = "transcendent"           # Transcendent governance

class EnforcementIntegrationMode(Enum):
    """Modes of enforcement integration"""
    REACTIVE = "reactive"                   # React to violations after they occur
    PROACTIVE = "proactive"                 # Prevent violations before they occur
    PREDICTIVE = "predictive"               # Predict and prevent violations
    COLLABORATIVE = "collaborative"         # Collaborative governance with agents
    AUTONOMOUS = "autonomous"               # Fully autonomous governance

@dataclass
class GovernancePolicy:
    """A governance policy for enforcement"""
    policy_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    governance_level: GovernanceLevel = GovernanceLevel.BASIC
    enforcement_mode: EnforcementIntegrationMode = EnforcementIntegrationMode.REACTIVE
    target_agent_types: List[AgentType] = field(default_factory=list)
    target_stages: List[str] = field(default_factory=list)
    rules: List[Dict[str, Any]] = field(default_factory=list)
    thresholds: Dict[str, float] = field(default_factory=dict)
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class EnforcementIntegrationResult:
    """Result from enforcement integration"""
    agent_id: str
    agent_type: AgentType
    stage: str
    governance_level: GovernanceLevel
    enforcement_mode: EnforcementIntegrationMode
    performance_metrics: Dict[str, float]
    enforcement_actions: List[EnforcementAction]
    learning_insights: List[str]
    recommendations: List[str]
    integration_score: float
    metadata: Dict[str, Any]

@dataclass
class GovernanceAnalytics:
    """Analytics for governance enforcement system"""
    total_agents: int = 0
    total_violations: int = 0
    total_enforcement_actions: int = 0
    compliance_rate: float = 0.0
    learning_effectiveness: float = 0.0
    adaptation_rate: float = 0.0
    governance_evolution_score: float = 0.0
    system_harmony_score: float = 0.0

class EnhancedGovernanceEnforcementIntegration:
    """
    Enhanced Governance Enforcement Integration
    Integrates the enhanced enforcement system with agent performance tracking
    """
    
    def __init__(self, 
                 database_url: str,
                 openai_api_key: str,
                 session_factory: sessionmaker,
                 integration_config: Dict[str, Any] = None):
        """
        Initialize the governance enforcement integration
        
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
        
        # Initialize enforcement system
        self.enforcement_system = EnhancedCosmicCouncilEnforcementSystem(
            database_url=database_url,
            n8n_webhook_url=self.integration_config.get('n8n_webhook_url'),
            slack_webhook_url=self.integration_config.get('slack_webhook_url'),
            max_retries=self.integration_config.get('max_retries', 3),
            retry_delay=self.integration_config.get('retry_delay', 1.0)
        )
        
        # Initialize performance tracking system
        self.performance_tracking = EnhancedAgentPerformanceTracking(
            database_url=database_url,
            openai_api_key=openai_api_key,
            session_factory=session_factory
        )
        
        # Governance policies
        self.governance_policies: Dict[str, GovernancePolicy] = {}
        
        # Integration settings
        self.governance_level = GovernanceLevel(self.integration_config.get('governance_level', 'enhanced'))
        self.enforcement_mode = EnforcementIntegrationMode(self.integration_config.get('enforcement_mode', 'proactive'))
        self.learning_enabled = self.integration_config.get('learning_enabled', True)
        self.adaptation_enabled = self.integration_config.get('adaptation_enabled', True)
        
        # Analytics
        self.governance_analytics = GovernanceAnalytics()
        
        # Initialize governance policies
        self._initialize_governance_policies()
        
        logger.info("Enhanced Governance Enforcement Integration initialized")

    def _initialize_governance_policies(self):
        """Initialize governance policies for different agent types and stages"""
        
        # Research Stage Policy
        research_policy = GovernancePolicy(
            name="Research Stage Governance",
            description="Governance policy for research and inquiry agents",
            governance_level=GovernanceLevel.ENHANCED,
            enforcement_mode=EnforcementIntegrationMode.PROACTIVE,
            target_agent_types=[AgentType.RED_OWL],
            target_stages=['research'],
            rules=[
                {
                    'rule_name': 'research_quality_standard',
                    'description': 'Research must meet quality standards',
                    'threshold': 0.8,
                    'enforcement_action': 'warning'
                },
                {
                    'rule_name': 'source_verification',
                    'description': 'All sources must be verified',
                    'threshold': 1.0,
                    'enforcement_action': 'block'
                }
            ],
            thresholds={
                'quality_score': 0.8,
                'verification_rate': 1.0,
                'compliance_rate': 0.9
            }
        )
        self.governance_policies['research'] = research_policy
        
        # Planning Stage Policy
        planning_policy = GovernancePolicy(
            name="Planning Stage Governance",
            description="Governance policy for planning and logistics agents",
            governance_level=GovernanceLevel.INTELLIGENT,
            enforcement_mode=EnforcementIntegrationMode.PREDICTIVE,
            target_agent_types=[AgentType.ORANGE_ORANGUTAN],
            target_stages=['planning'],
            rules=[
                {
                    'rule_name': 'planning_completeness',
                    'description': 'Plans must be complete and comprehensive',
                    'threshold': 0.9,
                    'enforcement_action': 'warning'
                },
                {
                    'rule_name': 'resource_allocation',
                    'description': 'Resource allocation must be realistic',
                    'threshold': 0.8,
                    'enforcement_action': 'block'
                }
            ],
            thresholds={
                'completeness_score': 0.9,
                'realism_score': 0.8,
                'efficiency_score': 0.7
            }
        )
        self.governance_policies['planning'] = planning_policy
        
        # Development Stage Policy
        development_policy = GovernancePolicy(
            name="Development Stage Governance",
            description="Governance policy for development and creativity agents",
            governance_level=GovernanceLevel.ADAPTIVE,
            enforcement_mode=EnforcementIntegrationMode.COLLABORATIVE,
            target_agent_types=[AgentType.YELLOW_HONEYBEE],
            target_stages=['development'],
            rules=[
                {
                    'rule_name': 'innovation_quality',
                    'description': 'Innovations must meet quality standards',
                    'threshold': 0.7,
                    'enforcement_action': 'warning'
                },
                {
                    'rule_name': 'feasibility_check',
                    'description': 'Developments must be feasible',
                    'threshold': 0.8,
                    'enforcement_action': 'block'
                }
            ],
            thresholds={
                'innovation_score': 0.7,
                'feasibility_score': 0.8,
                'creativity_score': 0.6
            }
        )
        self.governance_policies['development'] = development_policy
        
        # Budget Stage Policy
        budget_policy = GovernancePolicy(
            name="Budget Stage Governance",
            description="Governance policy for budget and resources agents",
            governance_level=GovernanceLevel.ENHANCED,
            enforcement_mode=EnforcementIntegrationMode.PROACTIVE,
            target_agent_types=[AgentType.GREEN_TORTOISE],
            target_stages=['budget'],
            rules=[
                {
                    'rule_name': 'budget_accuracy',
                    'description': 'Budget estimates must be accurate',
                    'threshold': 0.9,
                    'enforcement_action': 'warning'
                },
                {
                    'rule_name': 'resource_efficiency',
                    'description': 'Resource allocation must be efficient',
                    'threshold': 0.8,
                    'enforcement_action': 'block'
                }
            ],
            thresholds={
                'accuracy_score': 0.9,
                'efficiency_score': 0.8,
                'sustainability_score': 0.7
            }
        )
        self.governance_policies['budget'] = budget_policy
        
        # Market Stage Policy
        market_policy = GovernancePolicy(
            name="Market Stage Governance",
            description="Governance policy for market and communication agents",
            governance_level=GovernanceLevel.INTELLIGENT,
            enforcement_mode=EnforcementIntegrationMode.PREDICTIVE,
            target_agent_types=[AgentType.BLUE_DOLPHIN],
            target_stages=['market'],
            rules=[
                {
                    'rule_name': 'market_analysis_quality',
                    'description': 'Market analysis must be comprehensive',
                    'threshold': 0.8,
                    'enforcement_action': 'warning'
                },
                {
                    'rule_name': 'communication_effectiveness',
                    'description': 'Communication must be effective',
                    'threshold': 0.7,
                    'enforcement_action': 'block'
                }
            ],
            thresholds={
                'analysis_quality': 0.8,
                'communication_effectiveness': 0.7,
                'market_penetration': 0.6
            }
        )
        self.governance_policies['market'] = market_policy
        
        # Support Stage Policy
        support_policy = GovernancePolicy(
            name="Support Stage Governance",
            description="Governance policy for support and feedback agents",
            governance_level=GovernanceLevel.TRANSCENDENT,
            enforcement_mode=EnforcementIntegrationMode.AUTONOMOUS,
            target_agent_types=[AgentType.PURPLE_ELEPHANT],
            target_stages=['support'],
            rules=[
                {
                    'rule_name': 'feedback_quality',
                    'description': 'Feedback must be constructive and actionable',
                    'threshold': 0.8,
                    'enforcement_action': 'warning'
                },
                {
                    'rule_name': 'continuous_improvement',
                    'description': 'Must demonstrate continuous improvement',
                    'threshold': 0.7,
                    'enforcement_action': 'block'
                }
            ],
            thresholds={
                'feedback_quality': 0.8,
                'improvement_rate': 0.7,
                'satisfaction_score': 0.8
            }
        )
        self.governance_policies['support'] = support_policy

    async def integrate_governance_with_performance(self, 
                                                  agent_id: str,
                                                  agent_type: AgentType,
                                                  stage: str,
                                                  performance_data: Dict[str, Any]) -> EnforcementIntegrationResult:
        """
        Integrate governance enforcement with agent performance tracking
        
        Args:
            agent_id: ID of the agent
            agent_type: Type of the agent
            stage: Workflow stage
            performance_data: Performance data from tracking system
            
        Returns:
            Integration result with enforcement actions and insights
        """
        try:
            # Get governance policy for stage
            policy = self.governance_policies.get(stage)
            if not policy:
                logger.warning(f"No governance policy found for stage: {stage}")
                return self._create_default_integration_result(agent_id, agent_type, stage)
            
            # Get agent performance profile
            performance_profile = await self.performance_tracking.get_agent_performance_profile(agent_id)
            if not performance_profile:
                logger.warning(f"No performance profile found for agent: {agent_id}")
                return self._create_default_integration_result(agent_id, agent_type, stage)
            
            # Analyze performance against governance rules
            rule_violations = await self._analyze_rule_violations(performance_data, policy)
            
            # Determine enforcement actions
            enforcement_actions = await self._determine_enforcement_actions(
                agent_id, agent_type, rule_violations, policy
            )
            
            # Generate learning insights
            learning_insights = await self._generate_learning_insights(
                performance_profile, rule_violations, policy
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                performance_profile, rule_violations, policy
            )
            
            # Calculate integration score
            integration_score = await self._calculate_integration_score(
                performance_profile, rule_violations, enforcement_actions
            )
            
            # Create integration result
            result = EnforcementIntegrationResult(
                agent_id=agent_id,
                agent_type=agent_type,
                stage=stage,
                governance_level=policy.governance_level,
                enforcement_mode=policy.enforcement_mode,
                performance_metrics=performance_data,
                enforcement_actions=enforcement_actions,
                learning_insights=learning_insights,
                recommendations=recommendations,
                integration_score=integration_score,
                metadata={
                    'policy_id': policy.policy_id,
                    'rule_violations': rule_violations,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Update governance analytics
            await self._update_governance_analytics(result)
            
            # Store integration result
            await self._store_integration_result(result)
            
            logger.info(f"Integrated governance with performance for agent {agent_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to integrate governance with performance: {e}")
            raise

    async def _analyze_rule_violations(self, 
                                     performance_data: Dict[str, Any], 
                                     policy: GovernancePolicy) -> List[Dict[str, Any]]:
        """Analyze performance data against governance rules"""
        violations = []
        
        try:
            for rule in policy.rules:
                rule_name = rule['rule_name']
                threshold = rule['threshold']
                enforcement_action = rule['enforcement_action']
                
                # Get performance metric for this rule
                metric_value = performance_data.get(rule_name, 0.0)
                
                # Check if rule is violated
                if metric_value < threshold:
                    violation = {
                        'rule_name': rule_name,
                        'description': rule['description'],
                        'threshold': threshold,
                        'actual_value': metric_value,
                        'violation_severity': self._calculate_violation_severity(metric_value, threshold),
                        'enforcement_action': enforcement_action,
                        'policy_id': policy.policy_id
                    }
                    violations.append(violation)
            
            return violations
            
        except Exception as e:
            logger.error(f"Failed to analyze rule violations: {e}")
            return []

    def _calculate_violation_severity(self, actual_value: float, threshold: float) -> str:
        """Calculate violation severity based on deviation from threshold"""
        deviation = (threshold - actual_value) / threshold
        
        if deviation >= 0.5:
            return 'critical'
        elif deviation >= 0.3:
            return 'major'
        elif deviation >= 0.1:
            return 'minor'
        else:
            return 'warning'

    async def _determine_enforcement_actions(self, 
                                           agent_id: str,
                                           agent_type: AgentType,
                                           rule_violations: List[Dict[str, Any]],
                                           policy: GovernancePolicy) -> List[EnforcementAction]:
        """Determine enforcement actions based on rule violations"""
        actions = []
        
        try:
            # Group violations by severity
            critical_violations = [v for v in rule_violations if v['violation_severity'] == 'critical']
            major_violations = [v for v in rule_violations if v['violation_severity'] == 'major']
            minor_violations = [v for v in rule_violations if v['violation_severity'] == 'minor']
            
            # Determine actions based on policy enforcement mode
            if policy.enforcement_mode == EnforcementIntegrationMode.REACTIVE:
                # React to violations after they occur
                if critical_violations:
                    actions.append(EnforcementAction.BAN)
                elif major_violations:
                    actions.append(EnforcementAction.SUSPEND)
                elif minor_violations:
                    actions.append(EnforcementAction.BLOCK)
                else:
                    actions.append(EnforcementAction.WARNING)
            
            elif policy.enforcement_mode == EnforcementIntegrationMode.PROACTIVE:
                # Prevent violations before they occur
                if critical_violations:
                    actions.append(EnforcementAction.SUSPEND)
                elif major_violations:
                    actions.append(EnforcementAction.BLOCK)
                elif minor_violations:
                    actions.append(EnforcementAction.WARNING)
            
            elif policy.enforcement_mode == EnforcementIntegrationMode.PREDICTIVE:
                # Predict and prevent violations
                if critical_violations:
                    actions.append(EnforcementAction.BLOCK)
                elif major_violations:
                    actions.append(EnforcementAction.WARNING)
                elif minor_violations:
                    actions.append(EnforcementAction.WARNING)
            
            elif policy.enforcement_mode == EnforcementIntegrationMode.COLLABORATIVE:
                # Collaborative governance with agents
                if critical_violations:
                    actions.append(EnforcementAction.WARNING)
                elif major_violations:
                    actions.append(EnforcementAction.WARNING)
                elif minor_violations:
                    actions.append(EnforcementAction.WARNING)
            
            elif policy.enforcement_mode == EnforcementIntegrationMode.AUTONOMOUS:
                # Fully autonomous governance
                if critical_violations:
                    actions.append(EnforcementAction.SUSPEND)
                elif major_violations:
                    actions.append(EnforcementAction.BLOCK)
                elif minor_violations:
                    actions.append(EnforcementAction.WARNING)
            
            return actions
            
        except Exception as e:
            logger.error(f"Failed to determine enforcement actions: {e}")
            return [EnforcementAction.WARNING]

    async def _generate_learning_insights(self, 
                                        performance_profile: AgentPerformanceProfile,
                                        rule_violations: List[Dict[str, Any]],
                                        policy: GovernancePolicy) -> List[str]:
        """Generate learning insights from performance and violations"""
        insights = []
        
        try:
            # Performance-based insights
            if performance_profile.overall_score > 0.8:
                insights.append(f"Agent demonstrates high performance with score {performance_profile.overall_score:.2f}")
            elif performance_profile.overall_score < 0.5:
                insights.append(f"Agent performance needs improvement with score {performance_profile.overall_score:.2f}")
            
            # Violation-based insights
            if rule_violations:
                critical_count = len([v for v in rule_violations if v['violation_severity'] == 'critical'])
                major_count = len([v for v in rule_violations if v['violation_severity'] == 'major'])
                minor_count = len([v for v in rule_violations if v['violation_severity'] == 'minor'])
                
                if critical_count > 0:
                    insights.append(f"Critical violations detected: {critical_count} critical, {major_count} major, {minor_count} minor")
                elif major_count > 0:
                    insights.append(f"Major violations detected: {major_count} major, {minor_count} minor")
                elif minor_count > 0:
                    insights.append(f"Minor violations detected: {minor_count} minor")
            
            # Policy-based insights
            if policy.governance_level == GovernanceLevel.TRANSCENDENT:
                insights.append("Agent operating under transcendent governance level")
            elif policy.governance_level == GovernanceLevel.ADAPTIVE:
                insights.append("Agent operating under adaptive governance level")
            elif policy.governance_level == GovernanceLevel.INTELLIGENT:
                insights.append("Agent operating under intelligent governance level")
            
            # Enforcement mode insights
            if policy.enforcement_mode == EnforcementIntegrationMode.AUTONOMOUS:
                insights.append("Agent operating under autonomous enforcement mode")
            elif policy.enforcement_mode == EnforcementIntegrationMode.COLLABORATIVE:
                insights.append("Agent operating under collaborative enforcement mode")
            elif policy.enforcement_mode == EnforcementIntegrationMode.PREDICTIVE:
                insights.append("Agent operating under predictive enforcement mode")
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate learning insights: {e}")
            return []

    async def _generate_recommendations(self, 
                                      performance_profile: AgentPerformanceProfile,
                                      rule_violations: List[Dict[str, Any]],
                                      policy: GovernancePolicy) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []
        
        try:
            # Performance-based recommendations
            if performance_profile.overall_score < 0.7:
                recommendations.append("Focus on improving overall performance through targeted training")
            
            # Violation-based recommendations
            for violation in rule_violations:
                if violation['violation_severity'] == 'critical':
                    recommendations.append(f"Address critical violation in {violation['rule_name']}: {violation['description']}")
                elif violation['violation_severity'] == 'major':
                    recommendations.append(f"Address major violation in {violation['rule_name']}: {violation['description']}")
                elif violation['violation_severity'] == 'minor':
                    recommendations.append(f"Address minor violation in {violation['rule_name']}: {violation['description']}")
            
            # Policy-based recommendations
            if policy.governance_level == GovernanceLevel.BASIC:
                recommendations.append("Consider upgrading to enhanced governance level for better monitoring")
            elif policy.governance_level == GovernanceLevel.ENHANCED:
                recommendations.append("Consider upgrading to intelligent governance level for AI-driven insights")
            elif policy.governance_level == GovernanceLevel.INTELLIGENT:
                recommendations.append("Consider upgrading to adaptive governance level for self-improvement")
            elif policy.governance_level == GovernanceLevel.ADAPTIVE:
                recommendations.append("Consider upgrading to transcendent governance level for ultimate evolution")
            
            # Enforcement mode recommendations
            if policy.enforcement_mode == EnforcementIntegrationMode.REACTIVE:
                recommendations.append("Consider upgrading to proactive enforcement mode for better prevention")
            elif policy.enforcement_mode == EnforcementIntegrationMode.PROACTIVE:
                recommendations.append("Consider upgrading to predictive enforcement mode for better forecasting")
            elif policy.enforcement_mode == EnforcementIntegrationMode.PREDICTIVE:
                recommendations.append("Consider upgrading to collaborative enforcement mode for better cooperation")
            elif policy.enforcement_mode == EnforcementIntegrationMode.COLLABORATIVE:
                recommendations.append("Consider upgrading to autonomous enforcement mode for full automation")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []

    async def _calculate_integration_score(self, 
                                         performance_profile: AgentPerformanceProfile,
                                         rule_violations: List[Dict[str, Any]],
                                         enforcement_actions: List[EnforcementAction]) -> float:
        """Calculate integration score for governance and performance"""
        try:
            # Base score from performance
            base_score = performance_profile.overall_score
            
            # Penalty for violations
            violation_penalty = 0.0
            for violation in rule_violations:
                if violation['violation_severity'] == 'critical':
                    violation_penalty += 0.3
                elif violation['violation_severity'] == 'major':
                    violation_penalty += 0.2
                elif violation['violation_severity'] == 'minor':
                    violation_penalty += 0.1
            
            # Penalty for enforcement actions
            action_penalty = 0.0
            for action in enforcement_actions:
                if action == EnforcementAction.BAN:
                    action_penalty += 0.4
                elif action == EnforcementAction.SUSPEND:
                    action_penalty += 0.3
                elif action == EnforcementAction.BLOCK:
                    action_penalty += 0.2
                elif action == EnforcementAction.WARNING:
                    action_penalty += 0.1
            
            # Calculate final score
            integration_score = max(0.0, base_score - violation_penalty - action_penalty)
            
            return integration_score
            
        except Exception as e:
            logger.error(f"Failed to calculate integration score: {e}")
            return 0.0

    def _create_default_integration_result(self, 
                                         agent_id: str, 
                                         agent_type: AgentType, 
                                         stage: str) -> EnforcementIntegrationResult:
        """Create default integration result when no policy or profile is found"""
        return EnforcementIntegrationResult(
            agent_id=agent_id,
            agent_type=agent_type,
            stage=stage,
            governance_level=GovernanceLevel.BASIC,
            enforcement_mode=EnforcementIntegrationMode.REACTIVE,
            performance_metrics={},
            enforcement_actions=[EnforcementAction.WARNING],
            learning_insights=["No governance policy or performance profile found"],
            recommendations=["Set up proper governance policy and performance tracking"],
            integration_score=0.0,
            metadata={'default_result': True}
        )

    async def _update_governance_analytics(self, result: EnforcementIntegrationResult):
        """Update governance analytics based on integration result"""
        try:
            # Update basic metrics
            self.governance_analytics.total_agents += 1
            self.governance_analytics.total_violations += len(result.metadata.get('rule_violations', []))
            self.governance_analytics.total_enforcement_actions += len(result.enforcement_actions)
            
            # Update compliance rate
            if result.integration_score > 0.8:
                self.governance_analytics.compliance_rate = (self.governance_analytics.compliance_rate + 1.0) / 2
            else:
                self.governance_analytics.compliance_rate = (self.governance_analytics.compliance_rate + 0.0) / 2
            
            # Update learning effectiveness
            if result.learning_insights:
                self.governance_analytics.learning_effectiveness = (self.governance_analytics.learning_effectiveness + 1.0) / 2
            else:
                self.governance_analytics.learning_effectiveness = (self.governance_analytics.learning_effectiveness + 0.0) / 2
            
            # Update adaptation rate
            if result.governance_level in [GovernanceLevel.ADAPTIVE, GovernanceLevel.TRANSCENDENT]:
                self.governance_analytics.adaptation_rate = (self.governance_analytics.adaptation_rate + 1.0) / 2
            else:
                self.governance_analytics.adaptation_rate = (self.governance_analytics.adaptation_rate + 0.0) / 2
            
            # Update governance evolution score
            evolution_score = 0.0
            if result.governance_level == GovernanceLevel.TRANSCENDENT:
                evolution_score = 1.0
            elif result.governance_level == GovernanceLevel.ADAPTIVE:
                evolution_score = 0.8
            elif result.governance_level == GovernanceLevel.INTELLIGENT:
                evolution_score = 0.6
            elif result.governance_level == GovernanceLevel.ENHANCED:
                evolution_score = 0.4
            else:
                evolution_score = 0.2
            
            self.governance_analytics.governance_evolution_score = (self.governance_analytics.governance_evolution_score + evolution_score) / 2
            
            # Update system harmony score
            harmony_score = result.integration_score
            self.governance_analytics.system_harmony_score = (self.governance_analytics.system_harmony_score + harmony_score) / 2
            
        except Exception as e:
            logger.error(f"Failed to update governance analytics: {e}")

    async def _store_integration_result(self, result: EnforcementIntegrationResult):
        """Store integration result in database"""
        try:
            async with self.session_factory() as session:
                await session.execute(
                    text("""
                        INSERT INTO governance_enforcement_integration_results (
                            result_id, agent_id, agent_type, stage, governance_level,
                            enforcement_mode, performance_metrics, enforcement_actions,
                            learning_insights, recommendations, integration_score, metadata
                        ) VALUES (
                            :result_id, :agent_id, :agent_type, :stage, :governance_level,
                            :enforcement_mode, :performance_metrics, :enforcement_actions,
                            :learning_insights, :recommendations, :integration_score, :metadata
                        )
                    """),
                    {
                        'result_id': str(uuid.uuid4()),
                        'agent_id': result.agent_id,
                        'agent_type': result.agent_type.value,
                        'stage': result.stage,
                        'governance_level': result.governance_level.value,
                        'enforcement_mode': result.enforcement_mode.value,
                        'performance_metrics': json.dumps(result.performance_metrics),
                        'enforcement_actions': json.dumps([action.value for action in result.enforcement_actions]),
                        'learning_insights': json.dumps(result.learning_insights),
                        'recommendations': json.dumps(result.recommendations),
                        'integration_score': result.integration_score,
                        'metadata': json.dumps(result.metadata)
                    }
                )
                
                await session.commit()
                
        except Exception as e:
            logger.error(f"Failed to store integration result: {e}")

    async def get_governance_analytics(self, days_back: int = 30) -> Dict[str, Any]:
        """Get governance analytics"""
        try:
            start_time = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            async with self.session_factory() as session:
                # Get integration results from database
                result = await session.execute(
                    text("""
                        SELECT COUNT(*) as total_results,
                               AVG(integration_score) as avg_integration_score,
                               COUNT(CASE WHEN integration_score > 0.8 THEN 1 END) as high_performance_count
                        FROM governance_enforcement_integration_results
                        WHERE created_at >= :start_time
                    """),
                    {"start_time": start_time}
                )
                
                db_stats = result.fetchone()
                
                # Combine with in-memory analytics
                analytics = {
                    'period_days': days_back,
                    'governance_analytics': {
                        'total_agents': self.governance_analytics.total_agents,
                        'total_violations': self.governance_analytics.total_violations,
                        'total_enforcement_actions': self.governance_analytics.total_enforcement_actions,
                        'compliance_rate': self.governance_analytics.compliance_rate,
                        'learning_effectiveness': self.governance_analytics.learning_effectiveness,
                        'adaptation_rate': self.governance_analytics.adaptation_rate,
                        'governance_evolution_score': self.governance_analytics.governance_evolution_score,
                        'system_harmony_score': self.governance_analytics.system_harmony_score
                    },
                    'database_stats': {
                        'total_results': db_stats.total_results if db_stats else 0,
                        'avg_integration_score': float(db_stats.avg_integration_score) if db_stats and db_stats.avg_integration_score else 0.0,
                        'high_performance_count': db_stats.high_performance_count if db_stats else 0
                    },
                    'governance_policies': {
                        policy_name: {
                            'name': policy.name,
                            'governance_level': policy.governance_level.value,
                            'enforcement_mode': policy.enforcement_mode.value,
                            'target_agent_types': [agent_type.value for agent_type in policy.target_agent_types],
                            'target_stages': policy.target_stages,
                            'enabled': policy.enabled
                        }
                        for policy_name, policy in self.governance_policies.items()
                    }
                }
                
                return analytics
                
        except Exception as e:
            logger.error(f"Failed to get governance analytics: {e}")
            return {"error": str(e)}

    async def close(self):
        """Close database connections"""
        await self.engine.dispose()
        await self.enforcement_system.close()
        logger.info("Enhanced Governance Enforcement Integration closed")

# Example usage
async def main():
    """Example usage of the enhanced governance enforcement integration"""
    
    integration = EnhancedGovernanceEnforcementIntegration(
        database_url="postgresql+asyncpg://user:password@localhost/dream_caesar",
        openai_api_key="your-openai-api-key",
        session_factory=None,  # Would be your actual session factory
        integration_config={
            'governance_level': 'enhanced',
            'enforcement_mode': 'proactive',
            'learning_enabled': True,
            'adaptation_enabled': True,
            'n8n_webhook_url': 'https://your-n8n-instance.com/webhook/governance',
            'slack_webhook_url': 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        }
    )
    
    try:
        # Integrate governance with performance
        result = await integration.integrate_governance_with_performance(
            agent_id="agent_001",
            agent_type=AgentType.RED_OWL,
            stage="research",
            performance_data={
                'research_quality_standard': 0.9,
                'source_verification': 0.8,
                'compliance_rate': 0.85
            }
        )
        
        print(f"Governance Integration Result: {json.dumps(result.__dict__, indent=2, default=str)}")
        
        # Get governance analytics
        analytics = await integration.get_governance_analytics(30)
        print(f"Governance Analytics: {json.dumps(analytics, indent=2)}")
        
    finally:
        await integration.close()

if __name__ == "__main__":
    asyncio.run(main())
