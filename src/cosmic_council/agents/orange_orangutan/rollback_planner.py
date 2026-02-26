"""
ORANGE ORANGUTAN - Rollback Planner.

Generates rollback procedures for actions and plans.
This implements Criterion 2: Each action has a defined rollback.

The planner ensures:
- Every action has a rollback procedure
- Rollback order is reverse of execution order
- Rollback risks are assessed
- Partial rollback is possible
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import structlog

from .models import (
    ActionCategory,
    ActionStep,
    ActionPlan,
    RiskLevel,
    RollbackProcedure,
)

logger = structlog.get_logger(__name__)


@dataclass
class RollbackPlan:
    """Complete rollback plan for an action plan."""
    plan_id: str
    rollback_order: List[str] = field(default_factory=list)
    rollback_procedures: Dict[str, RollbackProcedure] = field(default_factory=dict)
    overall_risk: RiskLevel = RiskLevel.MEDIUM
    estimated_duration_seconds: int = 0
    requires_data_restore: bool = False
    backup_locations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_ms: int = 0


# Category-specific rollback templates
ROLLBACK_TEMPLATES: Dict[ActionCategory, Dict[str, Any]] = {
    ActionCategory.CONFIGURATION: {
        "steps": [
            "Restore configuration from backup",
            "Validate configuration syntax",
            "Reload configuration",
            "Verify service stability",
        ],
        "risk": RiskLevel.LOW,
        "duration": 60,
        "requires_backup": True,
    },
    ActionCategory.DEPLOYMENT: {
        "steps": [
            "Identify previous version",
            "Initiate rollback deployment",
            "Wait for rollback to complete",
            "Verify service health",
            "Monitor for errors",
        ],
        "risk": RiskLevel.MEDIUM,
        "duration": 300,
        "requires_backup": False,
    },
    ActionCategory.SCALING: {
        "steps": [
            "Restore original replica count",
            "Wait for scale operation",
            "Verify load distribution",
        ],
        "risk": RiskLevel.LOW,
        "duration": 120,
        "requires_backup": False,
    },
    ActionCategory.RESTART: {
        "steps": [
            "Service will automatically restart",
            "Verify service is running",
            "Check for startup errors",
        ],
        "risk": RiskLevel.LOW,
        "duration": 120,
        "requires_backup": False,
    },
    ActionCategory.DATABASE: {
        "steps": [
            "Stop database writes",
            "Restore from backup/snapshot",
            "Verify data integrity",
            "Resume database operations",
            "Validate application connectivity",
        ],
        "risk": RiskLevel.HIGH,
        "duration": 600,
        "requires_backup": True,
    },
    ActionCategory.NETWORK: {
        "steps": [
            "Restore previous network configuration",
            "Flush DNS caches if needed",
            "Verify connectivity",
            "Check firewall rules",
        ],
        "risk": RiskLevel.MEDIUM,
        "duration": 180,
        "requires_backup": True,
    },
    ActionCategory.SECURITY: {
        "steps": [
            "Revert security changes",
            "Restore previous credentials if rotated",
            "Verify access controls",
            "Audit security state",
        ],
        "risk": RiskLevel.HIGH,
        "duration": 300,
        "requires_backup": True,
    },
    ActionCategory.MONITORING: {
        "steps": [
            "Restore previous alert configuration",
            "Verify monitoring is active",
        ],
        "risk": RiskLevel.NEGLIGIBLE,
        "duration": 30,
        "requires_backup": True,
    },
    ActionCategory.COMMUNICATION: {
        "steps": [
            "Send correction/update notification",
        ],
        "risk": RiskLevel.NEGLIGIBLE,
        "duration": 15,
        "requires_backup": False,
    },
    ActionCategory.INVESTIGATION: {
        "steps": [
            "No rollback needed - investigation is read-only",
        ],
        "risk": RiskLevel.NEGLIGIBLE,
        "duration": 0,
        "requires_backup": False,
    },
    ActionCategory.CUSTOM: {
        "steps": [
            "Consult documentation for rollback procedure",
            "Execute manual rollback steps",
            "Verify system state",
        ],
        "risk": RiskLevel.MEDIUM,
        "duration": 180,
        "requires_backup": True,
    },
}


class RollbackPlanner:
    """
    Generates rollback procedures for actions.

    This is critical for Criterion 2: Rollback reversibility.
    Every action must have a defined way to undo it.
    """

    def __init__(
        self,
        require_rollback_for_all: bool = True,
    ):
        """
        Initialize the rollback planner.

        Args:
            require_rollback_for_all: Require rollback for every action
        """
        self.require_all = require_rollback_for_all
        logger.info(
            "rollback_planner_initialized",
            require_all=require_rollback_for_all,
        )

    def plan_rollback(
        self,
        action: ActionStep,
        context: Optional[Dict[str, Any]] = None,
    ) -> RollbackProcedure:
        """
        Generate a rollback procedure for an action.

        Args:
            action: The action to create rollback for
            context: Additional context

        Returns:
            RollbackProcedure for the action
        """
        context = context or {}

        # If action already has a good rollback, enhance it
        if action.rollback and len(action.rollback.steps) > 1:
            return self._enhance_rollback(action.rollback, action, context)

        # Generate from template
        template = ROLLBACK_TEMPLATES.get(
            action.category,
            ROLLBACK_TEMPLATES[ActionCategory.CUSTOM]
        )

        # Customize steps for this action
        steps = [
            step.format(
                action=action.title,
                service=action.target_service or "target",
            )
            for step in template["steps"]
        ]

        # Add action-specific context
        if action.target_service:
            steps = [f"Target: {action.target_service}"] + steps

        # Determine backup location
        backup_location = None
        if template["requires_backup"]:
            backup_location = f"/backups/{action.target_service or 'system'}/{action.id}"

        return RollbackProcedure(
            description=f"Rollback procedure for: {action.title}",
            steps=steps,
            estimated_duration_seconds=template["duration"],
            risk_level=template["risk"],
            requires_data_backup=template["requires_backup"],
            backup_location=backup_location,
            manual_steps=steps if template["risk"].value >= RiskLevel.HIGH.value else [],
        )

    def _enhance_rollback(
        self,
        existing: RollbackProcedure,
        action: ActionStep,
        context: Dict[str, Any],
    ) -> RollbackProcedure:
        """Enhance an existing rollback procedure."""
        # Add verification steps if missing
        if not any("verify" in s.lower() for s in existing.steps):
            existing.steps.append("Verify rollback completed successfully")

        # Ensure backup location is set if needed
        if existing.requires_data_backup and not existing.backup_location:
            existing.backup_location = f"/backups/{action.target_service or 'system'}/{action.id}"

        return existing

    def create_plan_rollback(
        self,
        plan: ActionPlan,
        context: Optional[Dict[str, Any]] = None,
    ) -> RollbackPlan:
        """
        Create a complete rollback plan for an action plan.

        Args:
            plan: The action plan to create rollback for
            context: Additional context

        Returns:
            RollbackPlan for the entire plan
        """
        start_time = time.time()
        context = context or {}
        warnings: List[str] = []

        # Generate rollback for each action
        procedures: Dict[str, RollbackProcedure] = {}
        backup_locations: List[str] = []
        requires_data_restore = False
        max_risk = RiskLevel.NEGLIGIBLE
        total_duration = 0

        for action in plan.actions:
            # Generate or get rollback procedure
            procedure = self.plan_rollback(action, context)
            procedures[action.id] = procedure

            # Update action with rollback
            action.rollback = procedure

            # Track requirements
            if procedure.requires_data_backup:
                requires_data_restore = True
                if procedure.backup_location:
                    backup_locations.append(procedure.backup_location)

            if procedure.risk_level.value > max_risk.value:
                max_risk = procedure.risk_level

            total_duration += procedure.estimated_duration_seconds

            # Check for missing rollback
            if not procedure.is_reversible and self.require_all:
                warnings.append(f"Action {action.id} has no reversible rollback")

        # Rollback order is reverse of execution order
        rollback_order = list(reversed(plan.execution_order))

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "rollback_plan_created",
            plan_id=plan.id,
            procedure_count=len(procedures),
            total_duration_seconds=total_duration,
            requires_data_restore=requires_data_restore,
            duration_ms=duration_ms,
        )

        return RollbackPlan(
            plan_id=plan.id,
            rollback_order=rollback_order,
            rollback_procedures=procedures,
            overall_risk=max_risk,
            estimated_duration_seconds=total_duration,
            requires_data_restore=requires_data_restore,
            backup_locations=backup_locations,
            warnings=warnings,
            duration_ms=duration_ms,
        )

    def validate_rollbacks(
        self,
        plan: ActionPlan,
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all actions have valid rollback procedures.

        Args:
            plan: The action plan to validate

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues: List[str] = []

        for action in plan.actions:
            if not action.rollback:
                issues.append(f"Action {action.id} ({action.title}) has no rollback")
            elif not action.rollback.is_reversible:
                issues.append(f"Action {action.id} ({action.title}) has no reversible rollback")
            elif action.rollback.requires_data_backup and not action.rollback.backup_location:
                issues.append(f"Action {action.id} needs backup but no location specified")

        return len(issues) == 0, issues


def create_rollback_planner(
    require_all: bool = True,
) -> RollbackPlanner:
    """Factory function to create a RollbackPlanner."""
    return RollbackPlanner(require_rollback_for_all=require_all)
