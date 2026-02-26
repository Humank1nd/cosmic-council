"""
PURPLE ELEPHANT - Responsibility Resolver.

Resolves responsibility assignments for located actions.
This implements Criterion 1: Responsibility assignment.

Every action must have a designated executor.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
import fnmatch

import structlog

from .models import (
    Stakeholder,
    StakeholderType,
    ResponsibilityAssignment,
    ResponsibilityType,
    AssignmentStatus,
    PurpleElephantConfig,
    STANDARD_STAKEHOLDERS,
)

logger = structlog.get_logger(__name__)


@dataclass
class AssignmentRule:
    """Rule for assigning responsibilities."""
    id: str = ""
    name: str = ""
    description: str = ""

    # Matching criteria
    action_patterns: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    risk_levels: List[str] = field(default_factory=list)
    service_patterns: List[str] = field(default_factory=list)

    # Assignment target
    stakeholder_id: Optional[str] = None
    team: Optional[str] = None
    responsibility_type: ResponsibilityType = ResponsibilityType.EXECUTOR

    # Priority
    priority: int = 100
    enabled: bool = True


# Default assignment rules
DEFAULT_ASSIGNMENT_RULES: List[AssignmentRule] = [
    AssignmentRule(
        name="database_to_dba",
        description="Database actions go to DBA team",
        categories=["database", "backup", "migration"],
        stakeholder_id="database-team",
        responsibility_type=ResponsibilityType.EXECUTOR,
        priority=10,
    ),
    AssignmentRule(
        name="deployment_to_platform",
        description="Deployment actions go to platform team",
        categories=["deployment", "scaling", "restart"],
        stakeholder_id="platform-team",
        responsibility_type=ResponsibilityType.EXECUTOR,
        priority=20,
    ),
    AssignmentRule(
        name="high_risk_needs_approver",
        description="High-risk actions need approver",
        risk_levels=["HIGH", "CRITICAL"],
        stakeholder_id="on-call-primary",
        responsibility_type=ResponsibilityType.APPROVER,
        priority=5,
    ),
    AssignmentRule(
        name="automation_for_monitoring",
        description="Monitoring can be automated",
        categories=["monitoring", "investigation", "notification"],
        stakeholder_id="automation-service",
        responsibility_type=ResponsibilityType.EXECUTOR,
        priority=30,
    ),
]


@dataclass
class ResolutionResult:
    """Result of responsibility resolution."""
    assignment: ResponsibilityAssignment
    success: bool = False
    matched_rules: List[str] = field(default_factory=list)
    fallback_used: bool = False
    warnings: List[str] = field(default_factory=list)


@dataclass
class BatchResolutionResult:
    """Result of batch responsibility resolution."""
    assignments: List[ResponsibilityAssignment] = field(default_factory=list)
    resolved_count: int = 0
    unresolved_count: int = 0
    warnings: List[str] = field(default_factory=list)
    duration_ms: int = 0


class ResponsibilityResolver:
    """
    Resolves responsibility assignments.

    Criterion 1: Every action has a designated executor.
    """

    def __init__(
        self,
        stakeholders: Optional[Dict[str, Stakeholder]] = None,
        assignment_rules: Optional[List[AssignmentRule]] = None,
        config: Optional[PurpleElephantConfig] = None,
    ):
        """
        Initialize the responsibility resolver.

        Args:
            stakeholders: Available stakeholders
            assignment_rules: Assignment rules
            config: Configuration
        """
        self.stakeholders = stakeholders or STANDARD_STAKEHOLDERS
        self.assignment_rules = assignment_rules or DEFAULT_ASSIGNMENT_RULES
        self.config = config or PurpleElephantConfig()

        logger.info(
            "responsibility_resolver_initialized",
            stakeholder_count=len(self.stakeholders),
            rule_count=len(self.assignment_rules),
        )

    def resolve(
        self,
        action_id: str,
        target_id: str = "",
        slot_id: str = "",
        category: str = "",
        risk_level: str = "MEDIUM",
        service_name: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> ResolutionResult:
        """
        Resolve responsibility for an action.

        Args:
            action_id: Action identifier
            target_id: Execution target ID from Blue Dolphin
            slot_id: Schedule slot ID from Green Turtle
            category: Action category
            risk_level: Risk level
            service_name: Service being acted upon
            context: Additional context

        Returns:
            ResolutionResult with assignment
        """
        context = context or {}
        warnings: List[str] = []
        matched_rules: List[str] = []

        # Create assignment
        assignment = ResponsibilityAssignment(
            action_id=action_id,
            target_id=target_id,
            slot_id=slot_id,
        )

        # Apply assignment rules
        sorted_rules = sorted(self.assignment_rules, key=lambda r: r.priority)
        selected_stakeholder = None

        for rule in sorted_rules:
            if not rule.enabled:
                continue

            if self._rule_matches(rule, action_id, category, risk_level, service_name):
                matched_rules.append(rule.name)

                # Find stakeholder
                stakeholder = self._find_stakeholder(rule, context)
                if stakeholder:
                    selected_stakeholder = stakeholder
                    assignment.responsibility_type = rule.responsibility_type
                    assignment.reason = f"Matched rule: {rule.name}"
                    break

        # Fallback logic
        if not selected_stakeholder:
            selected_stakeholder = self._find_fallback_stakeholder(
                category, risk_level, service_name, context
            )
            if selected_stakeholder:
                warnings.append(f"Using fallback: {selected_stakeholder.name}")
                assignment.reason = "Fallback assignment"

        if selected_stakeholder:
            assignment.stakeholder = selected_stakeholder
            assignment.status = AssignmentStatus.ASSIGNED
            assignment.assigned_at = datetime.utcnow()

            # Build escalation chain
            assignment.escalation_chain = self._build_escalation_chain(
                selected_stakeholder, context
            )

            logger.debug(
                "responsibility_resolved",
                action_id=action_id,
                stakeholder=selected_stakeholder.name,
                type=assignment.responsibility_type.value,
                rules_matched=len(matched_rules),
            )

            return ResolutionResult(
                assignment=assignment,
                success=True,
                matched_rules=matched_rules,
                fallback_used=len(matched_rules) == 0,
                warnings=warnings,
            )
        else:
            assignment.status = AssignmentStatus.PENDING
            warnings.append("No suitable stakeholder found")

            return ResolutionResult(
                assignment=assignment,
                success=False,
                matched_rules=matched_rules,
                warnings=warnings,
            )

    def _rule_matches(
        self,
        rule: AssignmentRule,
        action_id: str,
        category: str,
        risk_level: str,
        service_name: str,
    ) -> bool:
        """Check if a rule matches the action."""
        # Check action patterns
        if rule.action_patterns:
            if not any(fnmatch.fnmatch(action_id, p) for p in rule.action_patterns):
                return False

        # Check categories
        if rule.categories:
            if category.lower() not in [c.lower() for c in rule.categories]:
                return False

        # Check risk levels
        if rule.risk_levels:
            if risk_level.upper() not in [r.upper() for r in rule.risk_levels]:
                return False

        # Check service patterns
        if rule.service_patterns:
            if not any(fnmatch.fnmatch(service_name, p) for p in rule.service_patterns):
                return False

        return True

    def _find_stakeholder(
        self,
        rule: AssignmentRule,
        context: Dict[str, Any],
    ) -> Optional[Stakeholder]:
        """Find stakeholder based on rule."""
        # Direct stakeholder ID
        if rule.stakeholder_id:
            stakeholder = self.stakeholders.get(rule.stakeholder_id)
            if stakeholder and self._is_available(stakeholder):
                return stakeholder

        # Find by team
        if rule.team:
            for stakeholder in self.stakeholders.values():
                if stakeholder.team == rule.team and self._is_available(stakeholder):
                    return stakeholder

        return None

    def _is_available(self, stakeholder: Stakeholder) -> bool:
        """Check if stakeholder is available."""
        if not stakeholder.is_available:
            return False

        if stakeholder.vacation_until:
            if datetime.utcnow() < stakeholder.vacation_until:
                return False

        return True

    def _find_fallback_stakeholder(
        self,
        category: str,
        risk_level: str,
        service_name: str,
        context: Dict[str, Any],
    ) -> Optional[Stakeholder]:
        """Find a fallback stakeholder."""
        # Try on-call if enabled
        if self.config.fallback_to_on_call:
            for stakeholder in self.stakeholders.values():
                if stakeholder.on_call and self._is_available(stakeholder):
                    return stakeholder

        # Try automation service for low-risk
        if risk_level.upper() in ["LOW", "NEGLIGIBLE"]:
            for stakeholder in self.stakeholders.values():
                if stakeholder.type == StakeholderType.AUTOMATION:
                    return stakeholder

        # Try any available team
        if self.config.fallback_to_team:
            for stakeholder in self.stakeholders.values():
                if stakeholder.type == StakeholderType.TEAM and self._is_available(stakeholder):
                    return stakeholder

        return None

    def _build_escalation_chain(
        self,
        primary: Stakeholder,
        context: Dict[str, Any],
    ) -> List[str]:
        """Build escalation chain for a stakeholder."""
        chain = []

        # Find stakeholders at higher escalation levels
        for level in range(1, self.config.max_escalation_levels + 1):
            for stakeholder in self.stakeholders.values():
                if stakeholder.escalation_level == level:
                    chain.append(stakeholder.id)
                    break

        return chain

    def resolve_batch(
        self,
        actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> BatchResolutionResult:
        """
        Resolve responsibilities for multiple actions.

        Args:
            actions: List of action dictionaries
            context: Additional context

        Returns:
            BatchResolutionResult
        """
        import time
        start_time = time.time()
        context = context or {}

        assignments: List[ResponsibilityAssignment] = []
        warnings: List[str] = []
        resolved = 0
        unresolved = 0

        for action in actions:
            result = self.resolve(
                action_id=action.get("action_id", action.get("id", "")),
                target_id=action.get("target_id", ""),
                slot_id=action.get("slot_id", ""),
                category=action.get("category", ""),
                risk_level=action.get("risk_level", "MEDIUM"),
                service_name=action.get("service_name", ""),
                context=context,
            )

            assignments.append(result.assignment)
            warnings.extend(result.warnings)

            if result.success:
                resolved += 1
            else:
                unresolved += 1

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "batch_resolution_complete",
            total=len(actions),
            resolved=resolved,
            unresolved=unresolved,
            duration_ms=duration_ms,
        )

        return BatchResolutionResult(
            assignments=assignments,
            resolved_count=resolved,
            unresolved_count=unresolved,
            warnings=warnings,
            duration_ms=duration_ms,
        )

    def get_stakeholder_by_capability(
        self,
        capability: str,
    ) -> Optional[Stakeholder]:
        """Find a stakeholder with a specific capability."""
        for stakeholder in self.stakeholders.values():
            if capability in stakeholder.capabilities and self._is_available(stakeholder):
                return stakeholder
        return None

    def get_service_owner(
        self,
        service_name: str,
    ) -> Optional[Stakeholder]:
        """Find the owner of a service."""
        for stakeholder in self.stakeholders.values():
            if service_name in stakeholder.services_owned:
                return stakeholder
        return None


def create_responsibility_resolver(
    stakeholders: Optional[Dict[str, Stakeholder]] = None,
    assignment_rules: Optional[List[AssignmentRule]] = None,
    config: Optional[PurpleElephantConfig] = None,
) -> ResponsibilityResolver:
    """Factory function to create a ResponsibilityResolver."""
    return ResponsibilityResolver(
        stakeholders=stakeholders,
        assignment_rules=assignment_rules,
        config=config,
    )
