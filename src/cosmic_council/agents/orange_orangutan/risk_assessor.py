"""
ORANGE ORANGUTAN - Risk Assessor.

Evaluates the risk of each action in the plan.
This implements Criterion 3: Risk gates - high-risk actions require approval.

Risk assessment considers:
- Action category (deployment > configuration > monitoring)
- Target service criticality
- Current system state
- Time of day / change window
- Blast radius (how many services affected)
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

from .models import (
    ActionCategory,
    ActionStep,
    ActionPlan,
    RiskLevel,
)

logger = structlog.get_logger(__name__)


@dataclass
class RiskAssessment:
    """Result of assessing risk for an action or plan."""
    action_id: str
    original_risk: RiskLevel
    assessed_risk: RiskLevel
    risk_factors: List[str] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)
    requires_approval: bool = False
    approval_reason: Optional[str] = None
    blast_radius: int = 1  # Number of services affected
    confidence: float = 0.8


@dataclass
class PlanRiskAssessment:
    """Risk assessment for an entire plan."""
    plan_id: str
    overall_risk: RiskLevel
    action_assessments: List[RiskAssessment] = field(default_factory=list)
    approval_gates: List[str] = field(default_factory=list)
    risk_summary: str = ""
    total_blast_radius: int = 1
    duration_ms: int = 0


# Category-based risk modifiers
CATEGORY_RISK_MODIFIERS: Dict[ActionCategory, int] = {
    ActionCategory.INVESTIGATION: -1,    # Lower risk
    ActionCategory.MONITORING: -1,       # Lower risk
    ActionCategory.COMMUNICATION: -1,    # Lower risk
    ActionCategory.CONFIGURATION: 0,     # Neutral
    ActionCategory.RESTART: 0,           # Neutral
    ActionCategory.SCALING: 0,           # Neutral
    ActionCategory.DATABASE: 1,          # Higher risk
    ActionCategory.DEPLOYMENT: 1,        # Higher risk
    ActionCategory.NETWORK: 1,           # Higher risk
    ActionCategory.SECURITY: 2,          # Much higher risk
    ActionCategory.CUSTOM: 0,            # Neutral
}

# Service criticality patterns
CRITICAL_SERVICE_PATTERNS = [
    r"payment", r"auth", r"database", r"gateway", r"api",
    r"core", r"main", r"primary", r"production", r"prod",
]

# Time-based risk modifiers
def get_time_risk_modifier() -> int:
    """Get risk modifier based on current time."""
    hour = datetime.now().hour
    # Higher risk during business hours
    if 9 <= hour <= 17:
        return 1
    # Lower risk during maintenance windows (2-5 AM)
    if 2 <= hour <= 5:
        return -1
    return 0


class RiskAssessor:
    """
    Assesses risk of actions and plans.

    This is critical for Criterion 3: Risk compounding.
    High-risk actions must have approval gates.
    """

    def __init__(
        self,
        critical_services: Optional[List[str]] = None,
        risk_threshold_for_approval: RiskLevel = RiskLevel.HIGH,
    ):
        """
        Initialize the risk assessor.

        Args:
            critical_services: List of critical service names
            risk_threshold_for_approval: Minimum risk level requiring approval
        """
        self.critical_services = critical_services or []
        self.risk_threshold = risk_threshold_for_approval
        logger.info(
            "risk_assessor_initialized",
            critical_services_count=len(self.critical_services),
            risk_threshold=risk_threshold_for_approval.name,
        )

    def assess_action(
        self,
        action: ActionStep,
        context: Optional[Dict[str, Any]] = None,
    ) -> RiskAssessment:
        """
        Assess the risk of a single action.

        Args:
            action: The action to assess
            context: Additional context (system state, etc.)

        Returns:
            RiskAssessment with detailed risk analysis
        """
        context = context or {}
        risk_factors = []
        mitigations = []

        # Start with the action's declared risk
        base_risk_value = action.risk_level.value

        # Apply category modifier
        category_mod = CATEGORY_RISK_MODIFIERS.get(action.category, 0)
        if category_mod > 0:
            risk_factors.append(f"Category {action.category.value} increases risk")
        elif category_mod < 0:
            mitigations.append(f"Category {action.category.value} is low-risk")

        # Check service criticality
        service_mod = 0
        if action.target_service:
            service_lower = action.target_service.lower()
            for pattern in CRITICAL_SERVICE_PATTERNS:
                if pattern in service_lower:
                    service_mod = 1
                    risk_factors.append(f"Target service '{action.target_service}' is critical")
                    break

            if action.target_service in self.critical_services:
                service_mod = 2
                risk_factors.append(f"Service '{action.target_service}' in critical list")

        # Check time of day
        time_mod = get_time_risk_modifier()
        if time_mod > 0:
            risk_factors.append("Executing during business hours")
        elif time_mod < 0:
            mitigations.append("Executing during maintenance window")

        # Check rollback availability
        if action.rollback and action.rollback.is_automated:
            mitigations.append("Automated rollback available")
        elif action.rollback and action.rollback.is_reversible:
            mitigations.append("Manual rollback procedure defined")
        else:
            risk_factors.append("No clear rollback procedure")

        # Calculate final risk
        total_modifier = category_mod + service_mod + time_mod
        final_risk_value = max(1, min(5, base_risk_value + total_modifier))
        assessed_risk = RiskLevel(final_risk_value)

        # Determine if approval needed
        requires_approval = assessed_risk.value >= self.risk_threshold.value
        approval_reason = None
        if requires_approval:
            approval_reason = f"Risk level {assessed_risk.name} requires approval"

        # Estimate blast radius
        blast_radius = 1
        if action.category == ActionCategory.DEPLOYMENT:
            blast_radius = 3
        elif action.category == ActionCategory.NETWORK:
            blast_radius = 5
        elif action.category == ActionCategory.DATABASE:
            blast_radius = 4

        return RiskAssessment(
            action_id=action.id,
            original_risk=action.risk_level,
            assessed_risk=assessed_risk,
            risk_factors=risk_factors,
            mitigations=mitigations,
            requires_approval=requires_approval,
            approval_reason=approval_reason,
            blast_radius=blast_radius,
        )

    def assess_plan(
        self,
        plan: ActionPlan,
        context: Optional[Dict[str, Any]] = None,
    ) -> PlanRiskAssessment:
        """
        Assess the overall risk of a plan.

        Args:
            plan: The action plan to assess
            context: Additional context

        Returns:
            PlanRiskAssessment with overall risk analysis
        """
        start_time = time.time()
        context = context or {}

        action_assessments = []
        approval_gates = []
        max_risk = RiskLevel.NEGLIGIBLE
        total_blast_radius = 0

        for action in plan.actions:
            assessment = self.assess_action(action, context)
            action_assessments.append(assessment)

            # Update action with assessed risk
            action.risk_level = assessment.assessed_risk
            action.risk_factors = assessment.risk_factors
            action.risk_mitigations = assessment.mitigations
            action.requires_approval = assessment.requires_approval

            if assessment.requires_approval:
                approval_gates.append(action.id)

            if assessment.assessed_risk.value > max_risk.value:
                max_risk = assessment.assessed_risk

            total_blast_radius = max(total_blast_radius, assessment.blast_radius)

        # Compound risk: multiple high-risk actions escalate overall risk
        high_risk_count = sum(
            1 for a in action_assessments
            if a.assessed_risk.value >= RiskLevel.HIGH.value
        )
        if high_risk_count >= 3:
            max_risk = RiskLevel.CRITICAL

        # Build summary
        risk_summary = (
            f"Plan has {len(plan.actions)} actions, "
            f"{len(approval_gates)} require approval, "
            f"blast radius: {total_blast_radius} services"
        )

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "plan_risk_assessed",
            plan_id=plan.id,
            overall_risk=max_risk.name,
            approval_gates=len(approval_gates),
            duration_ms=duration_ms,
        )

        return PlanRiskAssessment(
            plan_id=plan.id,
            overall_risk=max_risk,
            action_assessments=action_assessments,
            approval_gates=approval_gates,
            risk_summary=risk_summary,
            total_blast_radius=total_blast_radius,
            duration_ms=duration_ms,
        )


def create_risk_assessor(
    critical_services: Optional[List[str]] = None,
    risk_threshold: RiskLevel = RiskLevel.HIGH,
) -> RiskAssessor:
    """Factory function to create a RiskAssessor."""
    return RiskAssessor(
        critical_services=critical_services,
        risk_threshold_for_approval=risk_threshold,
    )
