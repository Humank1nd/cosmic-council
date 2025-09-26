"""
Perpetual Thinking System - Guardrail Gateway Integration
Integrates the perpetual thinking system with the Guardrail Gateway for policy enforcement and audit logging.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Import Guardrail Gateway components
try:
    from guardrail_gateway.services.gateway.app.schemas import (
        Agent, Resource, EvalInput, EvalDecision, DecisionExplanation, ViolationCode
    )
    from guardrail_gateway.services.gateway.app.policy_engine import PolicyEngine
    from guardrail_gateway.services.gateway.app.storage import log_decision
    GUARDRAIL_AVAILABLE = True
except ImportError:
    GUARDRAIL_AVAILABLE = False
    # Create mock classes for when Guardrail Gateway is not available
    class Agent:
        def __init__(self, id: str, enterprise: str, squad: str):
            self.id = id
            self.enterprise = enterprise
            self.squad = squad
    
    class Resource:
        def __init__(self, service: str, action: str):
            self.service = service
            self.action = action
    
    class EvalInput:
        def __init__(self, agent: Agent, resource: Resource, context: Dict[str, Any] = None):
            self.agent = agent
            self.resource = resource
            self.context = context or {}
    
    class EvalDecision:
        def __init__(self, allow: bool, policies: List[str] = None, explanation: Dict[str, Any] = None, 
                     obligations: List[str] = None, decision_id: str = None, timestamp: datetime = None):
            self.allow = allow
            self.policies = policies or []
            self.explanation = explanation or {}
            self.obligations = obligations or []
            self.decision_id = decision_id
            self.timestamp = timestamp
    
    class PolicyEngine:
        def __init__(self, base_url: str = None):
            self.base_url = base_url or "http://localhost:8181"
        
        async def evaluate(self, package: str, input_obj: dict) -> Tuple[bool, Dict[str, Any]]:
            # Mock evaluation - always allow for testing
            return True, {"obligations": [], "latency_ms": 10}
    
    def log_decision(payload: dict):
        # Mock logging function
        pass

# Import perpetual thinking system components
from .unified_perpetual_thinking_system import UnifiedPerpetualThinkingEngine, CycleType, PatternType
from .meta_cyclical_architecture import MetaCyclicalArchitecture, MetaCycleType
from ...applications.enhanced_master_orchestration_system import EnhancedMasterOrchestrationSystem, OrchestrationMode

logger = logging.getLogger(__name__)

class PerpetualPolicyType(Enum):
    """Policy types for perpetual thinking system operations"""
    SESSION_CREATION = "perpetual_session_creation"
    CYCLE_EXECUTION = "perpetual_cycle_execution"
    BREAKTHROUGH_ANALYSIS = "perpetual_breakthrough_analysis"
    META_CYCLE_EXECUTION = "perpetual_meta_cycle_execution"
    PATTERN_RECOGNITION = "perpetual_pattern_recognition"
    SYSTEM_ACCESS = "perpetual_system_access"
    DATA_ACCESS = "perpetual_data_access"
    AI_INTEGRATION = "perpetual_ai_integration"

class PerpetualActionType(Enum):
    """Action types for perpetual thinking system"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    ANALYZE = "analyze"
    SYNTHESIZE = "synthesize"
    OPTIMIZE = "optimize"
    INFERENCE = "inference"
    TRAIN = "train"

@dataclass
class PerpetualPolicyContext:
    """Context information for perpetual thinking policy evaluation"""
    session_id: Optional[str] = None
    cycle_id: Optional[str] = None
    user_id: Optional[str] = None
    input_complexity: Optional[float] = None
    resource_requirements: Optional[Dict[str, Any]] = None
    risk_level: Optional[str] = None
    data_sensitivity: Optional[str] = None
    processing_time_limit: Optional[int] = None
    cost_budget: Optional[float] = None
    ethical_considerations: Optional[List[str]] = None
    compliance_requirements: Optional[List[str]] = None

@dataclass
class PerpetualAuditLog:
    """Audit log entry for perpetual thinking operations"""
    log_id: str
    timestamp: datetime
    operation_type: str
    agent_id: str
    resource_service: str
    resource_action: str
    policy_decision: bool
    policy_packages: List[str]
    obligations: List[str]
    context: Dict[str, Any]
    explanation: Dict[str, Any]
    latency_ms: int
    session_id: Optional[str] = None
    cycle_id: Optional[str] = None
    user_id: Optional[str] = None
    violations: Optional[List[str]] = None
    risk_score: Optional[float] = None

class PerpetualGuardrailIntegration:
    """
    Integration layer between perpetual thinking system and Guardrail Gateway
    Handles policy enforcement and audit logging for all perpetual thinking operations
    """
    
    def __init__(self, 
                 policy_engine: Optional[PolicyEngine] = None,
                 enable_audit_logging: bool = True,
                 enable_simulation_mode: bool = False):
        """
        Initialize the perpetual guardrail integration
        
        Args:
            policy_engine: Guardrail Gateway policy engine instance
            enable_audit_logging: Whether to enable audit logging
            enable_simulation_mode: Whether to run in simulation mode
        """
        self.policy_engine = policy_engine
        self.enable_audit_logging = enable_audit_logging
        self.enable_simulation_mode = enable_simulation_mode
        self.audit_logs: List[PerpetualAuditLog] = []
        
        # Policy packages for different perpetual thinking operations
        self.policy_packages = {
            PerpetualPolicyType.SESSION_CREATION: "guard/perpetual/session",
            PerpetualPolicyType.CYCLE_EXECUTION: "guard/perpetual/cycle",
            PerpetualPolicyType.BREAKTHROUGH_ANALYSIS: "guard/perpetual/breakthrough",
            PerpetualPolicyType.META_CYCLE_EXECUTION: "guard/perpetual/meta",
            PerpetualPolicyType.PATTERN_RECOGNITION: "guard/perpetual/pattern",
            PerpetualPolicyType.SYSTEM_ACCESS: "guard/perpetual/system",
            PerpetualPolicyType.DATA_ACCESS: "guard/perpetual/data",
            PerpetualPolicyType.AI_INTEGRATION: "guard/perpetual/ai"
        }
        
        logger.info(f"Perpetual Guardrail Integration initialized - "
                   f"Audit logging: {enable_audit_logging}, "
                   f"Simulation mode: {enable_simulation_mode}")
    
    async def evaluate_perpetual_operation(self,
                                         operation_type: PerpetualPolicyType,
                                         action_type: PerpetualActionType,
                                         agent_id: str,
                                         context: PerpetualPolicyContext) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluate a perpetual thinking operation through the Guardrail Gateway
        
        Args:
            operation_type: Type of perpetual thinking operation
            action_type: Action being performed
            agent_id: ID of the agent performing the operation
            context: Context information for policy evaluation
            
        Returns:
            Tuple of (allow_decision, evaluation_metadata)
        """
        try:
            # Create agent and resource for policy evaluation
            agent = Agent(
                id=agent_id,
                enterprise="perpetual",  # Perpetual thinking system as enterprise
                squad="thinking_engine"
            )
            
            resource = Resource(
                service=operation_type.value,
                action=action_type.value
            )
            
            # Create evaluation input
            eval_input = EvalInput(
                agent=agent,
                resource=resource,
                context=asdict(context)
            )
            
            # Get policy package for this operation type
            policy_package = self.policy_packages.get(operation_type, "guard/perpetual/default")
            
            # Evaluate through policy engine
            if self.policy_engine and GUARDRAIL_AVAILABLE:
                allow, meta = await self.policy_engine.evaluate(policy_package, eval_input.model_dump())
            else:
                # Fallback evaluation when Guardrail Gateway is not available
                allow, meta = await self._fallback_evaluation(operation_type, action_type, context)
            
            # Create decision ID and timestamp
            decision_id = str(uuid.uuid4())
            timestamp = datetime.now(timezone.utc)
            
            # Log the decision if audit logging is enabled
            if self.enable_audit_logging:
                await self._log_decision(
                    log_id=decision_id,
                    timestamp=timestamp,
                    operation_type=operation_type.value,
                    agent_id=agent_id,
                    resource_service=operation_type.value,
                    resource_action=action_type.value,
                    policy_decision=allow,
                    policy_packages=[policy_package],
                    obligations=meta.get("obligations", []),
                    context=asdict(context),
                    explanation=meta,
                    latency_ms=meta.get("latency_ms", 0),
                    session_id=context.session_id,
                    cycle_id=context.cycle_id,
                    user_id=context.user_id
                )
            
            # Add decision metadata
            meta.update({
                "decision_id": decision_id,
                "timestamp": timestamp.isoformat(),
                "policy_package": policy_package,
                "operation_type": operation_type.value,
                "action_type": action_type.value
            })
            
            return allow, meta
            
        except Exception as e:
            logger.error(f"Failed to evaluate perpetual operation: {e}")
            # Default to deny on error
            return False, {
                "error": str(e),
                "decision_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "fallback": True
            }
    
    async def _fallback_evaluation(self, 
                                 operation_type: PerpetualPolicyType,
                                 action_type: PerpetualActionType,
                                 context: PerpetualPolicyContext) -> Tuple[bool, Dict[str, Any]]:
        """
        Fallback evaluation when Guardrail Gateway is not available
        Implements basic policy logic for perpetual thinking operations
        """
        # Basic policy logic
        allow = True
        obligations = []
        risk_score = 0.0
        
        # Check resource requirements
        if context.resource_requirements:
            # Deny if resource requirements exceed limits
            if context.resource_requirements.get("memory_mb", 0) > 1000:
                allow = False
                obligations.append("reduce_memory_usage")
        
        # Check processing time limits
        if context.processing_time_limit and context.processing_time_limit > 300:  # 5 minutes
            allow = False
            obligations.append("reduce_processing_time")
        
        # Check cost budget
        if context.cost_budget and context.cost_budget > 100.0:  # $100 limit
            allow = False
            obligations.append("reduce_cost_budget")
        
        # Check risk level
        if context.risk_level == "high":
            risk_score = 0.8
            obligations.append("require_approval")
        elif context.risk_level == "medium":
            risk_score = 0.5
            obligations.append("monitor_execution")
        else:
            risk_score = 0.2
        
        # Check data sensitivity
        if context.data_sensitivity == "confidential":
            obligations.append("encrypt_data")
            obligations.append("audit_access")
        
        # Check ethical considerations
        if context.ethical_considerations:
            obligations.append("ethical_review")
        
        return allow, {
            "obligations": obligations,
            "risk_score": risk_score,
            "latency_ms": 10,  # Simulated latency
            "fallback_evaluation": True
        }
    
    async def _log_decision(self, **kwargs):
        """Log a policy decision for audit purposes"""
        try:
            # Create audit log entry
            audit_log = PerpetualAuditLog(**kwargs)
            self.audit_logs.append(audit_log)
            
            # Log to Guardrail Gateway if available
            if GUARDRAIL_AVAILABLE and self.policy_engine:
                try:
                    log_decision({
                        "agent": {"id": kwargs["agent_id"]},
                        "request_json": kwargs["context"],
                        "allow": kwargs["policy_decision"],
                        "policy_refs": kwargs["policy_packages"],
                        "explanation": kwargs["explanation"],
                        "latency_ms": kwargs["latency_ms"]
                    })
                except Exception as e:
                    logger.warning(f"Failed to log to Guardrail Gateway: {e}")
            
            logger.info(f"Policy decision logged: {kwargs['operation_type']} - "
                       f"Allow: {kwargs['policy_decision']}, "
                       f"Obligations: {len(kwargs['obligations'])}")
            
        except Exception as e:
            logger.error(f"Failed to log decision: {e}")
    
    async def evaluate_session_creation(self, 
                                      agent_id: str,
                                      session_name: str,
                                      initial_input: str,
                                      user_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate permission to create a new perpetual thinking session"""
        context = PerpetualPolicyContext(
            user_id=user_id,
            input_complexity=len(initial_input) / 1000.0,  # Rough complexity measure
            risk_level="low" if len(initial_input) < 1000 else "medium",
            data_sensitivity="public"  # Default assumption
        )
        
        return await self.evaluate_perpetual_operation(
            operation_type=PerpetualPolicyType.SESSION_CREATION,
            action_type=PerpetualActionType.CREATE,
            agent_id=agent_id,
            context=context
        )
    
    async def evaluate_cycle_execution(self,
                                     agent_id: str,
                                     session_id: str,
                                     cycle_type: CycleType,
                                     input_text: str) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate permission to execute a perpetual thinking cycle"""
        context = PerpetualPolicyContext(
            session_id=session_id,
            input_complexity=len(input_text) / 1000.0,
            risk_level="medium" if cycle_type in [CycleType.BREAKTHROUGH, CycleType.META_REFLECTION] else "low",
            processing_time_limit=60,  # 1 minute default
            cost_budget=10.0  # $10 default
        )
        
        return await self.evaluate_perpetual_operation(
            operation_type=PerpetualPolicyType.CYCLE_EXECUTION,
            action_type=PerpetualActionType.EXECUTE,
            agent_id=agent_id,
            context=context
        )
    
    async def evaluate_breakthrough_analysis(self,
                                           agent_id: str,
                                           session_id: str,
                                           breakthrough_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate permission to analyze breakthrough moments"""
        context = PerpetualPolicyContext(
            session_id=session_id,
            risk_level="high",  # Breakthrough analysis is high risk
            data_sensitivity="confidential",
            ethical_considerations=["ai_safety", "bias_detection"]
        )
        
        return await self.evaluate_perpetual_operation(
            operation_type=PerpetualPolicyType.BREAKTHROUGH_ANALYSIS,
            action_type=PerpetualActionType.ANALYZE,
            agent_id=agent_id,
            context=context
        )
    
    async def evaluate_meta_cycle_execution(self,
                                          agent_id: str,
                                          session_id: str,
                                          meta_cycle_type: MetaCycleType) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate permission to execute meta-cycles"""
        context = PerpetualPolicyContext(
            session_id=session_id,
            risk_level="high",  # Meta-cycles are high risk
            processing_time_limit=300,  # 5 minutes
            cost_budget=50.0,  # $50
            ethical_considerations=["system_modification", "self_improvement"]
        )
        
        return await self.evaluate_perpetual_operation(
            operation_type=PerpetualPolicyType.META_CYCLE_EXECUTION,
            action_type=PerpetualActionType.EXECUTE,
            agent_id=agent_id,
            context=context
        )
    
    async def evaluate_pattern_recognition(self,
                                         agent_id: str,
                                         session_id: str,
                                         pattern_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate permission to perform pattern recognition"""
        context = PerpetualPolicyContext(
            session_id=session_id,
            risk_level="medium",
            data_sensitivity="internal"
        )
        
        return await self.evaluate_perpetual_operation(
            operation_type=PerpetualPolicyType.PATTERN_RECOGNITION,
            action_type=PerpetualActionType.ANALYZE,
            agent_id=agent_id,
            context=context
        )
    
    async def evaluate_system_access(self,
                                   agent_id: str,
                                   resource_type: str,
                                   action: str) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate permission to access system resources"""
        context = PerpetualPolicyContext(
            risk_level="low" if action == "read" else "medium",
            data_sensitivity="internal"
        )
        
        return await self.evaluate_perpetual_operation(
            operation_type=PerpetualPolicyType.SYSTEM_ACCESS,
            action_type=PerpetualActionType(action),
            agent_id=agent_id,
            context=context
        )
    
    async def evaluate_data_access(self,
                                 agent_id: str,
                                 data_type: str,
                                 action: str,
                                 session_id: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate permission to access data"""
        context = PerpetualPolicyContext(
            session_id=session_id,
            risk_level="low" if action == "read" else "high",
            data_sensitivity="confidential" if "personal" in data_type else "internal"
        )
        
        return await self.evaluate_perpetual_operation(
            operation_type=PerpetualPolicyType.DATA_ACCESS,
            action_type=PerpetualActionType(action),
            agent_id=agent_id,
            context=context
        )
    
    async def evaluate_ai_integration(self,
                                    agent_id: str,
                                    ai_model: str,
                                    operation: str,
                                    session_id: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate permission to use AI models"""
        context = PerpetualPolicyContext(
            session_id=session_id,
            risk_level="high" if "gpt-4" in ai_model else "medium",
            cost_budget=20.0,  # $20 for AI operations
            ethical_considerations=["ai_safety", "model_bias"]
        )
        
        return await self.evaluate_perpetual_operation(
            operation_type=PerpetualPolicyType.AI_INTEGRATION,
            action_type=PerpetualActionType(operation),
            agent_id=agent_id,
            context=context
        )
    
    def get_audit_logs(self, 
                      session_id: Optional[str] = None,
                      operation_type: Optional[str] = None,
                      limit: int = 100) -> List[PerpetualAuditLog]:
        """Get audit logs with optional filtering"""
        logs = self.audit_logs
        
        if session_id:
            logs = [log for log in logs if log.session_id == session_id]
        
        if operation_type:
            logs = [log for log in logs if log.operation_type == operation_type]
        
        return logs[-limit:]  # Return most recent logs
    
    def get_policy_violations(self, limit: int = 50) -> List[PerpetualAuditLog]:
        """Get policy violations (denied operations)"""
        violations = [log for log in self.audit_logs if not log.policy_decision]
        return violations[-limit:]
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get risk summary for perpetual thinking operations"""
        if not self.audit_logs:
            return {"total_operations": 0, "risk_score": 0.0}
        
        total_operations = len(self.audit_logs)
        denied_operations = len([log for log in self.audit_logs if not log.policy_decision])
        high_risk_operations = len([log for log in self.audit_logs if log.risk_score and log.risk_score > 0.7])
        
        return {
            "total_operations": total_operations,
            "denied_operations": denied_operations,
            "high_risk_operations": high_risk_operations,
            "denial_rate": denied_operations / total_operations if total_operations > 0 else 0.0,
            "high_risk_rate": high_risk_operations / total_operations if total_operations > 0 else 0.0,
            "average_risk_score": sum(log.risk_score or 0.0 for log in self.audit_logs) / total_operations
        }

class PerpetualPolicyEnforcer:
    """
    Policy enforcer that wraps perpetual thinking system operations
    with Guardrail Gateway policy evaluation
    """
    
    def __init__(self, 
                 perpetual_engine: UnifiedPerpetualThinkingEngine,
                 guardrail_integration: PerpetualGuardrailIntegration):
        """
        Initialize the policy enforcer
        
        Args:
            perpetual_engine: Perpetual thinking engine instance
            guardrail_integration: Guardrail integration instance
        """
        self.perpetual_engine = perpetual_engine
        self.guardrail_integration = guardrail_integration
        self.agent_id = "perpetual_policy_enforcer"
        
        logger.info("Perpetual Policy Enforcer initialized")
    
    async def create_session_with_policy(self,
                                       session_name: str,
                                       initial_input: str,
                                       user_id: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Create a perpetual thinking session with policy enforcement"""
        # Evaluate permission
        allow, meta = await self.guardrail_integration.evaluate_session_creation(
            agent_id=self.agent_id,
            session_name=session_name,
            initial_input=initial_input,
            user_id=user_id
        )
        
        if not allow:
            logger.warning(f"Session creation denied for user {user_id}: {meta}")
            return False, None, meta
        
        # Create session if allowed
        try:
            session_id = await self.perpetual_engine.create_session(
                session_name=session_name,
                initial_input=initial_input,
                user_id=user_id
            )
            
            logger.info(f"Session created with policy enforcement: {session_id}")
            return True, session_id, meta
            
        except Exception as e:
            logger.error(f"Failed to create session after policy approval: {e}")
            return False, None, {"error": str(e)}
    
    async def execute_cycle_with_policy(self,
                                      session_id: str,
                                      cycle_type: CycleType,
                                      input_text: str) -> Tuple[bool, Optional[Dict[str, Any]], Dict[str, Any]]:
        """Execute a perpetual thinking cycle with policy enforcement"""
        # Evaluate permission
        allow, meta = await self.guardrail_integration.evaluate_cycle_execution(
            agent_id=self.agent_id,
            session_id=session_id,
            cycle_type=cycle_type,
            input_text=input_text
        )
        
        if not allow:
            logger.warning(f"Cycle execution denied for session {session_id}: {meta}")
            return False, None, meta
        
        # Execute cycle if allowed
        try:
            result = await self.perpetual_engine.execute_cycle(
                session_id=session_id,
                cycle_type=cycle_type,
                input_text=input_text
            )
            
            logger.info(f"Cycle executed with policy enforcement: {session_id}")
            return True, result, meta
            
        except Exception as e:
            logger.error(f"Failed to execute cycle after policy approval: {e}")
            return False, None, {"error": str(e)}
    
    async def analyze_breakthrough_with_policy(self,
                                             session_id: str,
                                             breakthrough_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Dict[str, Any]]:
        """Analyze breakthrough moments with policy enforcement"""
        # Evaluate permission
        allow, meta = await self.guardrail_integration.evaluate_breakthrough_analysis(
            agent_id=self.agent_id,
            session_id=session_id,
            breakthrough_data=breakthrough_data
        )
        
        if not allow:
            logger.warning(f"Breakthrough analysis denied for session {session_id}: {meta}")
            return False, None, meta
        
        # Analyze breakthrough if allowed
        try:
            result = await self.perpetual_engine.analyze_breakthrough(
                session_id=session_id,
                breakthrough_data=breakthrough_data
            )
            
            logger.info(f"Breakthrough analyzed with policy enforcement: {session_id}")
            return True, result, meta
            
        except Exception as e:
            logger.error(f"Failed to analyze breakthrough after policy approval: {e}")
            return False, None, {"error": str(e)}

# Example usage and testing
async def test_perpetual_guardrail_integration():
    """Test the perpetual guardrail integration"""
    try:
        # Initialize integration
        integration = PerpetualGuardrailIntegration(
            enable_audit_logging=True,
            enable_simulation_mode=True
        )
        
        # Test session creation evaluation
        allow, meta = await integration.evaluate_session_creation(
            agent_id="test_agent",
            session_name="Test Session",
            initial_input="Test input for perpetual thinking",
            user_id="test_user"
        )
        
        print(f"Session creation evaluation: Allow={allow}, Meta={meta}")
        
        # Test cycle execution evaluation
        allow, meta = await integration.evaluate_cycle_execution(
            agent_id="test_agent",
            session_id="test_session",
            cycle_type=CycleType.STANDARD,
            input_text="Test cycle input"
        )
        
        print(f"Cycle execution evaluation: Allow={allow}, Meta={meta}")
        
        # Get audit logs
        logs = integration.get_audit_logs()
        print(f"Audit logs: {len(logs)} entries")
        
        # Get risk summary
        risk_summary = integration.get_risk_summary()
        print(f"Risk summary: {risk_summary}")
        
        print("✅ Perpetual Guardrail Integration test completed successfully")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_perpetual_guardrail_integration())
