"""
ORANGE ORANGUTAN - Action Decomposer.

Takes a root cause from Red Owl and decomposes it into actionable steps.
This is the first stage of HOW - breaking down the problem into solvable pieces.

The decomposer uses pattern matching and LLM (when available) to identify:
- What category of actions are needed
- What specific steps should be taken
- What order makes sense initially (refined later by dependency resolver)
"""

import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import structlog

from .models import (
    ActionCategory,
    ActionStep,
    RiskLevel,
    RollbackProcedure,
)

logger = structlog.get_logger(__name__)


@dataclass
class DecompositionResult:
    """Result of decomposing a root cause into actions."""
    actions: List[ActionStep] = field(default_factory=list)
    root_cause: str = ""
    root_cause_type: str = "unknown"
    confidence: float = 0.0
    reasoning: List[str] = field(default_factory=list)
    duration_ms: int = 0


# Pattern-based action templates
ACTION_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "database": [
        {
            "title": "Check database connection pool",
            "category": ActionCategory.DATABASE,
            "risk": RiskLevel.LOW,
            "duration": 60,
        },
        {
            "title": "Analyze slow queries",
            "category": ActionCategory.INVESTIGATION,
            "risk": RiskLevel.NEGLIGIBLE,
            "duration": 120,
        },
        {
            "title": "Add missing indexes",
            "category": ActionCategory.DATABASE,
            "risk": RiskLevel.MEDIUM,
            "duration": 300,
        },
        {
            "title": "Optimize connection pool settings",
            "category": ActionCategory.CONFIGURATION,
            "risk": RiskLevel.MEDIUM,
            "duration": 120,
        },
    ],
    "memory": [
        {
            "title": "Capture heap dump",
            "category": ActionCategory.INVESTIGATION,
            "risk": RiskLevel.LOW,
            "duration": 60,
        },
        {
            "title": "Analyze memory usage patterns",
            "category": ActionCategory.INVESTIGATION,
            "risk": RiskLevel.NEGLIGIBLE,
            "duration": 180,
        },
        {
            "title": "Restart affected service",
            "category": ActionCategory.RESTART,
            "risk": RiskLevel.MEDIUM,
            "duration": 120,
        },
        {
            "title": "Deploy memory fix",
            "category": ActionCategory.DEPLOYMENT,
            "risk": RiskLevel.HIGH,
            "duration": 600,
        },
    ],
    "deployment": [
        {
            "title": "Compare deployment configurations",
            "category": ActionCategory.INVESTIGATION,
            "risk": RiskLevel.NEGLIGIBLE,
            "duration": 60,
        },
        {
            "title": "Rollback to previous version",
            "category": ActionCategory.DEPLOYMENT,
            "risk": RiskLevel.HIGH,
            "duration": 300,
        },
        {
            "title": "Verify rollback success",
            "category": ActionCategory.MONITORING,
            "risk": RiskLevel.NEGLIGIBLE,
            "duration": 120,
        },
        {
            "title": "Notify stakeholders",
            "category": ActionCategory.COMMUNICATION,
            "risk": RiskLevel.NEGLIGIBLE,
            "duration": 30,
        },
    ],
    "network": [
        {
            "title": "Check network connectivity",
            "category": ActionCategory.INVESTIGATION,
            "risk": RiskLevel.NEGLIGIBLE,
            "duration": 60,
        },
        {
            "title": "Verify DNS resolution",
            "category": ActionCategory.INVESTIGATION,
            "risk": RiskLevel.NEGLIGIBLE,
            "duration": 30,
        },
        {
            "title": "Check firewall rules",
            "category": ActionCategory.NETWORK,
            "risk": RiskLevel.LOW,
            "duration": 60,
        },
        {
            "title": "Update network configuration",
            "category": ActionCategory.NETWORK,
            "risk": RiskLevel.HIGH,
            "duration": 180,
        },
    ],
    "scaling": [
        {
            "title": "Check current resource utilization",
            "category": ActionCategory.INVESTIGATION,
            "risk": RiskLevel.NEGLIGIBLE,
            "duration": 30,
        },
        {
            "title": "Scale up service replicas",
            "category": ActionCategory.SCALING,
            "risk": RiskLevel.MEDIUM,
            "duration": 120,
        },
        {
            "title": "Verify load distribution",
            "category": ActionCategory.MONITORING,
            "risk": RiskLevel.NEGLIGIBLE,
            "duration": 60,
        },
        {
            "title": "Update autoscaling thresholds",
            "category": ActionCategory.CONFIGURATION,
            "risk": RiskLevel.MEDIUM,
            "duration": 60,
        },
    ],
    "configuration": [
        {
            "title": "Backup current configuration",
            "category": ActionCategory.CONFIGURATION,
            "risk": RiskLevel.NEGLIGIBLE,
            "duration": 30,
        },
        {
            "title": "Identify configuration drift",
            "category": ActionCategory.INVESTIGATION,
            "risk": RiskLevel.NEGLIGIBLE,
            "duration": 60,
        },
        {
            "title": "Apply configuration fix",
            "category": ActionCategory.CONFIGURATION,
            "risk": RiskLevel.MEDIUM,
            "duration": 60,
        },
        {
            "title": "Restart service to apply changes",
            "category": ActionCategory.RESTART,
            "risk": RiskLevel.MEDIUM,
            "duration": 120,
        },
    ],
    "security": [
        {
            "title": "Assess security impact",
            "category": ActionCategory.INVESTIGATION,
            "risk": RiskLevel.LOW,
            "duration": 120,
        },
        {
            "title": "Notify security team",
            "category": ActionCategory.COMMUNICATION,
            "risk": RiskLevel.NEGLIGIBLE,
            "duration": 30,
        },
        {
            "title": "Apply security patch",
            "category": ActionCategory.SECURITY,
            "risk": RiskLevel.CRITICAL,
            "duration": 300,
        },
        {
            "title": "Verify security posture",
            "category": ActionCategory.SECURITY,
            "risk": RiskLevel.LOW,
            "duration": 120,
        },
    ],
    "unknown": [
        {
            "title": "Gather additional diagnostics",
            "category": ActionCategory.INVESTIGATION,
            "risk": RiskLevel.NEGLIGIBLE,
            "duration": 180,
        },
        {
            "title": "Escalate to on-call team",
            "category": ActionCategory.COMMUNICATION,
            "risk": RiskLevel.NEGLIGIBLE,
            "duration": 30,
        },
        {
            "title": "Apply temporary mitigation",
            "category": ActionCategory.CUSTOM,
            "risk": RiskLevel.MEDIUM,
            "duration": 120,
        },
        {
            "title": "Monitor for recurrence",
            "category": ActionCategory.MONITORING,
            "risk": RiskLevel.NEGLIGIBLE,
            "duration": 300,
        },
    ],
}

# Patterns to identify root cause type
ROOT_CAUSE_PATTERNS: Dict[str, List[str]] = {
    "database": [
        r"database", r"db\b", r"query", r"sql", r"connection pool",
        r"deadlock", r"index", r"table", r"postgresql", r"mysql", r"mongodb",
    ],
    "memory": [
        r"memory", r"heap", r"oom", r"out of memory", r"memory leak",
        r"garbage collection", r"gc\b", r"allocation",
    ],
    "deployment": [
        r"deploy", r"release", r"version", r"rollback", r"after.*deploy",
        r"new.*version", r"code change", r"regression",
    ],
    "network": [
        r"network", r"dns", r"connection", r"timeout", r"firewall",
        r"latency", r"packet", r"tcp", r"http",
    ],
    "scaling": [
        r"scal", r"capacity", r"load", r"traffic", r"spike",
        r"resource", r"cpu", r"utilization", r"overwhelm",
    ],
    "configuration": [
        r"config", r"setting", r"parameter", r"environment",
        r"variable", r"misconfigur", r"wrong.*value",
    ],
    "security": [
        r"security", r"auth", r"permission", r"access", r"credential",
        r"certificate", r"ssl", r"tls", r"token",
    ],
}


class ActionDecomposer:
    """
    Decomposes root causes into actionable steps.

    Uses pattern matching to identify the type of root cause,
    then generates appropriate actions from templates.
    With LLM, can generate more specific and contextual actions.
    """

    def __init__(
        self,
        llm_provider: Optional[Any] = None,
    ):
        """
        Initialize the action decomposer.

        Args:
            llm_provider: Optional LLM provider for intelligent decomposition
        """
        self.llm_provider = llm_provider
        logger.info(
            "action_decomposer_initialized",
            has_llm=llm_provider is not None,
        )

    async def decompose(
        self,
        root_cause: str,
        context: Optional[Dict[str, Any]] = None,
        confidence: float = 0.7,
    ) -> DecompositionResult:
        """
        Decompose a root cause into actionable steps.

        Args:
            root_cause: The root cause statement from Red Owl
            context: Additional context (service info, metrics, etc.)
            confidence: Confidence in the root cause

        Returns:
            DecompositionResult with list of actions
        """
        start_time = time.time()
        context = context or {}

        # Identify root cause type
        cause_type, type_confidence = self._identify_cause_type(root_cause)

        # Generate actions
        if self.llm_provider:
            actions = await self._decompose_with_llm(
                root_cause, cause_type, context, confidence
            )
        else:
            actions = self._decompose_with_patterns(
                root_cause, cause_type, context, confidence
            )

        # Build reasoning
        reasoning = [
            f"Identified root cause type: {cause_type} (confidence: {type_confidence:.2f})",
            f"Generated {len(actions)} actions from {'LLM' if self.llm_provider else 'templates'}",
        ]

        if context.get("service_name"):
            reasoning.append(f"Target service: {context['service_name']}")

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "root_cause_decomposed",
            cause_type=cause_type,
            action_count=len(actions),
            duration_ms=duration_ms,
        )

        return DecompositionResult(
            actions=actions,
            root_cause=root_cause,
            root_cause_type=cause_type,
            confidence=type_confidence * confidence,
            reasoning=reasoning,
            duration_ms=duration_ms,
        )

    def _identify_cause_type(self, root_cause: str) -> Tuple[str, float]:
        """Identify the type of root cause using patterns."""
        root_cause_lower = root_cause.lower()
        scores: Dict[str, float] = {}

        for cause_type, patterns in ROOT_CAUSE_PATTERNS.items():
            score = 0.0
            for pattern in patterns:
                if re.search(pattern, root_cause_lower):
                    score += 1.0

            if patterns:
                scores[cause_type] = score / len(patterns)

        if not scores or max(scores.values()) == 0:
            return "unknown", 0.3

        best_type = max(scores, key=lambda k: scores[k])
        return best_type, min(scores[best_type] * 2, 1.0)

    def _decompose_with_patterns(
        self,
        root_cause: str,
        cause_type: str,
        context: Dict[str, Any],
        confidence: float,
    ) -> List[ActionStep]:
        """Generate actions using pattern-based templates."""
        templates = ACTION_TEMPLATES.get(cause_type, ACTION_TEMPLATES["unknown"])
        actions = []

        service_name = context.get("service_name", "target-service")

        for i, template in enumerate(templates):
            # Create rollback procedure
            rollback = RollbackProcedure(
                description=f"Undo: {template['title']}",
                steps=[
                    f"Verify current state of {service_name}",
                    f"Revert changes from: {template['title']}",
                    "Validate system stability",
                ],
                risk_level=template["risk"],
            )

            action = ActionStep(
                title=template["title"],
                description=f"{template['title']} for {service_name} - addressing: {root_cause[:100]}",
                category=template["category"],
                target_service=service_name,
                risk_level=template["risk"],
                estimated_duration_seconds=template["duration"],
                rollback=rollback,
                metadata={
                    "source": "pattern_template",
                    "cause_type": cause_type,
                    "sequence": i,
                },
            )
            actions.append(action)

        return actions

    async def _decompose_with_llm(
        self,
        root_cause: str,
        cause_type: str,
        context: Dict[str, Any],
        confidence: float,
    ) -> List[ActionStep]:
        """Generate actions using LLM for more specific actions."""
        # Fall back to patterns if LLM call fails
        try:
            # TODO: Implement LLM-based decomposition
            # For now, use enhanced pattern matching
            return self._decompose_with_patterns(
                root_cause, cause_type, context, confidence
            )
        except Exception as e:
            logger.warning("llm_decomposition_failed", error=str(e))
            return self._decompose_with_patterns(
                root_cause, cause_type, context, confidence
            )

    def get_supported_cause_types(self) -> List[str]:
        """Get list of supported root cause types."""
        return list(ROOT_CAUSE_PATTERNS.keys())


def create_action_decomposer(
    llm_provider: Optional[Any] = None,
) -> ActionDecomposer:
    """Factory function to create an ActionDecomposer."""
    return ActionDecomposer(llm_provider=llm_provider)
