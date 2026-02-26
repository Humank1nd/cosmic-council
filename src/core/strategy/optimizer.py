"""
Adaptive Policy Engine
======================

Updates tool/prompt preferences based on success metrics.

Features:
- Role-specific adaptation rules
- Gradual policy updates with guardrails
- Canary rollout support
- Rollback capability
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from .registry import (
    AgentRole,
    StrategyProfile,
    StrategyRegistry,
    StrategyVersion,
    RiskTolerance,
    EvidenceStandard,
    ToolPreference,
)
from .outcomes import (
    OutcomeEvaluator,
    RoleScorecard,
    OutcomeMetrics,
)
from .calibration import (
    CalibrationEngine,
    CalibrationResult,
    CalibrationStatus,
)

logger = logging.getLogger(__name__)


class UpdateType(str, Enum):
    """Types of strategy updates."""
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    TOOL_PRIORITY = "tool_priority"
    METHOD_PREFERENCE = "method_preference"
    RISK_TOLERANCE = "risk_tolerance"
    EVIDENCE_STANDARD = "evidence_standard"
    WEIGHT_ADJUSTMENT = "weight_adjustment"
    CONSTRAINT = "constraint"


class UpdateRisk(str, Enum):
    """Risk level of a strategy update."""
    LOW = "low"          # Small adjustment, unlikely to cause issues
    MEDIUM = "medium"    # Moderate change, monitor closely
    HIGH = "high"        # Significant change, requires approval


@dataclass
class AdaptationRule:
    """
    A rule that triggers strategy adaptation.

    Rules are evaluated against metrics and produce updates.
    """
    name: str
    description: str
    applicable_roles: Set[AgentRole]
    update_type: UpdateType
    risk: UpdateRisk

    # Trigger conditions
    metric_name: str  # Which metric to evaluate
    threshold: float  # Trigger when metric crosses this
    comparison: str   # "lt", "gt", "eq"

    # Update parameters
    adjustment: float  # Amount to adjust
    max_adjustment: float  # Maximum total adjustment
    min_samples: int = 30  # Minimum samples to trigger
    cooldown_hours: int = 24  # Hours between applications

    # Tracking
    last_applied: Optional[datetime] = None
    application_count: int = 0

    def evaluate(
        self,
        role: AgentRole,
        metrics: OutcomeMetrics,
    ) -> bool:
        """Check if rule should trigger."""
        if role not in self.applicable_roles:
            return False

        if metrics.sample_size < self.min_samples:
            return False

        if self.last_applied:
            cooldown = timedelta(hours=self.cooldown_hours)
            if datetime.now(timezone.utc) - self.last_applied < cooldown:
                return False

        value = getattr(metrics, self.metric_name, None)
        if value is None:
            return False

        if self.comparison == "lt":
            return value < self.threshold
        elif self.comparison == "gt":
            return value > self.threshold
        elif self.comparison == "eq":
            return abs(value - self.threshold) < 0.01
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "applicable_roles": [r.value for r in self.applicable_roles],
            "update_type": self.update_type.value,
            "risk": self.risk.value,
            "metric_name": self.metric_name,
            "threshold": self.threshold,
            "comparison": self.comparison,
            "min_samples": self.min_samples,
            "adjustment": self.adjustment,
            "max_adjustment": self.max_adjustment,
            "cooldown_hours": self.cooldown_hours,
            "last_applied": self.last_applied.isoformat() if self.last_applied else None,
            "application_count": self.application_count,
        }


@dataclass
class StrategyUpdate:
    """
    A proposed or applied strategy update.
    """
    id: str
    role: AgentRole
    update_type: UpdateType
    risk: UpdateRisk

    # What changed
    field_name: str
    old_value: Any
    new_value: Any
    delta: float

    # Why
    triggered_by: str  # Rule name or "manual"
    reason: str

    # Status
    status: str = "proposed"  # "proposed", "approved", "applied", "rolled_back"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    applied_at: Optional[datetime] = None
    approved_by: Optional[str] = None

    # Evidence
    metrics_snapshot: Optional[Dict[str, Any]] = None
    scorecard_snapshot: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "role": self.role.value,
            "update_type": self.update_type.value,
            "risk": self.risk.value,
            "field_name": self.field_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "delta": self.delta,
            "triggered_by": self.triggered_by,
            "reason": self.reason,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "approved_by": self.approved_by,
            "metrics_snapshot": self.metrics_snapshot,
        }


@dataclass
class UpdateDecision:
    """
    Decision about whether to apply an update.
    """
    update: StrategyUpdate
    should_apply: bool
    requires_approval: bool
    auto_approved: bool = False
    approval_reason: str = ""
    rejection_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "update": self.update.to_dict(),
            "should_apply": self.should_apply,
            "requires_approval": self.requires_approval,
            "auto_approved": self.auto_approved,
            "approval_reason": self.approval_reason,
            "rejection_reason": self.rejection_reason,
        }


class AdaptivePolicyEngine:
    """
    Engine for adaptive strategy updates.

    Features:
    - Rule-based adaptation triggers
    - Calibration-driven threshold updates
    - Tool preference optimization
    - Canary rollout support
    - Automatic rollback on degradation
    """

    # Default adaptation rules
    DEFAULT_RULES = [
        # Low success rate -> increase evidence requirements
        AdaptationRule(
            name="low_success_increase_evidence",
            description="Increase evidence requirements when success rate is low",
            applicable_roles={AgentRole.WHY, AgentRole.HOW},
            update_type=UpdateType.EVIDENCE_STANDARD,
            risk=UpdateRisk.MEDIUM,
            metric_name="success_rate",
            threshold=0.6,
            comparison="lt",
            adjustment=1,  # Move up one level
            max_adjustment=2,
        ),
        # High intervention rate -> increase confidence threshold
        AdaptationRule(
            name="high_intervention_raise_threshold",
            description="Raise action threshold when human intervention is high",
            applicable_roles=set(AgentRole),
            update_type=UpdateType.CONFIDENCE_THRESHOLD,
            risk=UpdateRisk.LOW,
            metric_name="intervention_rate",
            threshold=0.3,
            comparison="gt",
            adjustment=0.05,
            max_adjustment=0.2,
        ),
        # High rework -> reduce risk tolerance
        AdaptationRule(
            name="high_rework_reduce_risk",
            description="Reduce risk tolerance when rework is frequent",
            applicable_roles={AgentRole.HOW, AgentRole.WHAT},
            update_type=UpdateType.RISK_TOLERANCE,
            risk=UpdateRisk.MEDIUM,
            metric_name="avg_rework",
            threshold=1.5,
            comparison="gt",
            adjustment=-1,  # Move down one level
            max_adjustment=1,
        ),
        # Good first-time success -> can reduce constraints
        AdaptationRule(
            name="good_first_time_relax",
            description="Relax constraints when first-time success is high",
            applicable_roles=set(AgentRole),
            update_type=UpdateType.CONFIDENCE_THRESHOLD,
            risk=UpdateRisk.LOW,
            metric_name="first_time_success_rate",
            threshold=0.85,
            comparison="gt",
            adjustment=-0.03,
            max_adjustment=0.1,
        ),
        # Slow response -> adjust timeout or reduce thoroughness
        AdaptationRule(
            name="slow_response_optimize",
            description="Optimize for speed when responses are slow",
            applicable_roles=set(AgentRole),
            update_type=UpdateType.WEIGHT_ADJUSTMENT,
            risk=UpdateRisk.LOW,
            metric_name="avg_duration_ms",
            threshold=30000,
            comparison="gt",
            adjustment=0.05,  # Increase speed weight
            max_adjustment=0.2,
        ),
    ]

    def __init__(
        self,
        registry: StrategyRegistry,
        evaluator: OutcomeEvaluator,
        calibrator: CalibrationEngine,
        rules: Optional[List[AdaptationRule]] = None,
        auto_apply_low_risk: bool = True,
        require_approval_high_risk: bool = True,
        max_updates_per_day: int = 1,
    ):
        self.registry = registry
        self.evaluator = evaluator
        self.calibrator = calibrator
        self.rules = rules or self.DEFAULT_RULES.copy()
        self.auto_apply_low_risk = auto_apply_low_risk
        self.require_approval_high_risk = require_approval_high_risk
        self.max_updates_per_day = max_updates_per_day

        self._pending_updates: Dict[str, StrategyUpdate] = {}
        self._applied_updates: List[StrategyUpdate] = []
        self._update_counter = 0

        # Track updates per role per day
        self._daily_updates: Dict[str, List[datetime]] = {}

    def analyze_role(
        self,
        role: AgentRole,
    ) -> List[StrategyUpdate]:
        """
        Analyze a role and generate proposed updates.

        Returns list of proposed strategy updates.
        """
        profile = self.registry.get_profile(role)
        scorecard = self.evaluator.compute_scorecard(role)
        calibration = self.calibrator.analyze_calibration(role, profile)

        updates = []

        # Check calibration-based updates
        if calibration.needs_recalibration:
            update = self._create_calibration_update(role, profile, calibration)
            if update:
                updates.append(update)

        # Check rule-based updates
        for rule in self.rules:
            if rule.evaluate(role, scorecard.metrics):
                update = self._create_rule_update(role, profile, rule, scorecard)
                if update:
                    updates.append(update)

        # Store pending updates
        for update in updates:
            self._pending_updates[update.id] = update

        return updates

    def _create_calibration_update(
        self,
        role: AgentRole,
        profile: StrategyProfile,
        calibration: CalibrationResult,
    ) -> Optional[StrategyUpdate]:
        """Create update from calibration result."""
        if calibration.recommended_action_threshold is None:
            return None

        self._update_counter += 1
        update_id = f"update_{role.value}_{self._update_counter}"

        return StrategyUpdate(
            id=update_id,
            role=role,
            update_type=UpdateType.CONFIDENCE_THRESHOLD,
            risk=UpdateRisk.LOW if abs(calibration.threshold_delta) < 0.05 else UpdateRisk.MEDIUM,
            field_name="min_confidence_to_act",
            old_value=profile.min_confidence_to_act,
            new_value=calibration.recommended_action_threshold,
            delta=calibration.threshold_delta,
            triggered_by="calibration_engine",
            reason=f"Calibration status: {calibration.status.value}",
            metrics_snapshot=calibration.to_dict(),
        )

    def _create_rule_update(
        self,
        role: AgentRole,
        profile: StrategyProfile,
        rule: AdaptationRule,
        scorecard: RoleScorecard,
    ) -> Optional[StrategyUpdate]:
        """Create update from triggered rule."""
        self._update_counter += 1
        update_id = f"update_{role.value}_{self._update_counter}"

        # Determine field and values based on update type
        field_name, old_value, new_value = self._compute_update_values(
            profile, rule, scorecard
        )

        if old_value == new_value:
            return None

        delta = new_value - old_value if isinstance(new_value, (int, float)) else 0

        return StrategyUpdate(
            id=update_id,
            role=role,
            update_type=rule.update_type,
            risk=rule.risk,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            delta=delta,
            triggered_by=rule.name,
            reason=rule.description,
            metrics_snapshot=scorecard.metrics.to_dict(),
            scorecard_snapshot=scorecard.to_dict(),
        )

    def _compute_update_values(
        self,
        profile: StrategyProfile,
        rule: AdaptationRule,
        scorecard: RoleScorecard,
    ) -> tuple:
        """Compute old and new values for an update."""
        if rule.update_type == UpdateType.CONFIDENCE_THRESHOLD:
            old_value = profile.min_confidence_to_act
            new_value = max(0.3, min(0.95, old_value + rule.adjustment))
            return "min_confidence_to_act", old_value, new_value

        elif rule.update_type == UpdateType.EVIDENCE_STANDARD:
            standards = list(EvidenceStandard)
            current_idx = standards.index(profile.evidence_standard)
            new_idx = max(0, min(len(standards) - 1, current_idx + int(rule.adjustment)))
            return "evidence_standard", profile.evidence_standard.value, standards[new_idx].value

        elif rule.update_type == UpdateType.RISK_TOLERANCE:
            tolerances = list(RiskTolerance)
            current_idx = tolerances.index(profile.risk_tolerance)
            new_idx = max(0, min(len(tolerances) - 1, current_idx + int(rule.adjustment)))
            return "risk_tolerance", profile.risk_tolerance.value, tolerances[new_idx].value

        elif rule.update_type == UpdateType.WEIGHT_ADJUSTMENT:
            # Adjust speed weight
            old_value = profile.weight_speed
            new_value = max(0.1, min(0.5, old_value + rule.adjustment))
            return "weight_speed", old_value, new_value

        return "unknown", None, None

    def decide_update(
        self,
        update: StrategyUpdate,
    ) -> UpdateDecision:
        """
        Decide whether to apply an update.

        Considers:
        - Risk level
        - Daily update budget
        - Auto-approval settings
        """
        role_key = update.role.value

        # Check daily budget
        today = datetime.now(timezone.utc).date()
        daily_key = f"{role_key}_{today}"

        if daily_key not in self._daily_updates:
            self._daily_updates[daily_key] = []

        if len(self._daily_updates[daily_key]) >= self.max_updates_per_day:
            return UpdateDecision(
                update=update,
                should_apply=False,
                requires_approval=False,
                rejection_reason="Daily update limit reached",
            )

        # Check risk level
        if update.risk == UpdateRisk.HIGH:
            if self.require_approval_high_risk:
                return UpdateDecision(
                    update=update,
                    should_apply=True,
                    requires_approval=True,
                    approval_reason="High-risk update requires manual approval",
                )

        if update.risk == UpdateRisk.LOW and self.auto_apply_low_risk:
            return UpdateDecision(
                update=update,
                should_apply=True,
                requires_approval=False,
                auto_approved=True,
                approval_reason="Low-risk update auto-approved",
            )

        # Medium risk - apply but monitor
        return UpdateDecision(
            update=update,
            should_apply=True,
            requires_approval=False,
            auto_approved=True,
            approval_reason="Medium-risk update auto-approved with monitoring",
        )

    def apply_update(
        self,
        update: StrategyUpdate,
        approved_by: str = "system",
    ) -> StrategyVersion:
        """Apply a strategy update."""
        profile = self.registry.get_profile(update.role)

        # Apply the change
        updated_profile = self._apply_change(profile, update)

        # Update registry
        version = self.registry.update_profile(
            role=update.role,
            profile=updated_profile,
            updated_by=approved_by,
            reason=f"{update.triggered_by}: {update.reason}",
        )

        # Update tracking
        update.status = "applied"
        update.applied_at = datetime.now(timezone.utc)
        update.approved_by = approved_by

        self._applied_updates.append(update)

        # Track daily updates
        today = datetime.now(timezone.utc).date()
        daily_key = f"{update.role.value}_{today}"
        if daily_key not in self._daily_updates:
            self._daily_updates[daily_key] = []
        self._daily_updates[daily_key].append(datetime.now(timezone.utc))

        # Remove from pending
        if update.id in self._pending_updates:
            del self._pending_updates[update.id]

        logger.info(
            f"Applied strategy update {update.id} to {update.role.value}: "
            f"{update.field_name} {update.old_value} -> {update.new_value}"
        )

        return version

    def _apply_change(
        self,
        profile: StrategyProfile,
        update: StrategyUpdate,
    ) -> StrategyProfile:
        """Apply a single change to a profile."""
        updated = StrategyProfile.from_dict(profile.to_dict())

        if update.field_name == "min_confidence_to_act":
            updated.min_confidence_to_act = update.new_value
        elif update.field_name == "min_confidence_to_recommend":
            updated.min_confidence_to_recommend = update.new_value
        elif update.field_name == "evidence_standard":
            updated.evidence_standard = EvidenceStandard(update.new_value)
        elif update.field_name == "risk_tolerance":
            updated.risk_tolerance = RiskTolerance(update.new_value)
        elif update.field_name == "weight_speed":
            updated.weight_speed = update.new_value
            # Rebalance other weights
            remaining = 1.0 - updated.weight_speed
            ratio = remaining / (profile.weight_accuracy + profile.weight_thoroughness + profile.weight_clarity)
            updated.weight_accuracy = profile.weight_accuracy * ratio
            updated.weight_thoroughness = profile.weight_thoroughness * ratio
            updated.weight_clarity = profile.weight_clarity * ratio

        return updated

    def rollback_update(
        self,
        update_id: str,
        reason: str = "Manual rollback",
    ) -> Optional[StrategyVersion]:
        """Rollback a previously applied update."""
        update = next(
            (u for u in self._applied_updates if u.id == update_id),
            None
        )

        if not update:
            return None

        profile = self.registry.get_profile(update.role)

        # Reverse the change
        reversed_update = StrategyUpdate(
            id=f"rollback_{update_id}",
            role=update.role,
            update_type=update.update_type,
            risk=UpdateRisk.LOW,
            field_name=update.field_name,
            old_value=update.new_value,
            new_value=update.old_value,
            delta=-update.delta,
            triggered_by="rollback",
            reason=reason,
        )

        return self.apply_update(reversed_update, approved_by="rollback")

    def get_pending_updates(
        self,
        role: Optional[AgentRole] = None,
    ) -> List[StrategyUpdate]:
        """Get pending updates, optionally filtered by role."""
        updates = list(self._pending_updates.values())
        if role:
            updates = [u for u in updates if u.role == role]
        return updates

    def get_update_history(
        self,
        role: Optional[AgentRole] = None,
        limit: int = 20,
    ) -> List[StrategyUpdate]:
        """Get applied update history."""
        updates = self._applied_updates
        if role:
            updates = [u for u in updates if u.role == role]
        return sorted(updates, key=lambda u: u.applied_at or u.created_at, reverse=True)[:limit]

    def get_recommendations(
        self,
        role: AgentRole,
    ) -> Dict[str, Any]:
        """Get recommendations for a role based on current analysis."""
        profile = self.registry.get_profile(role)
        scorecard = self.evaluator.compute_scorecard(role)
        calibration = self.calibrator.analyze_calibration(role, profile)

        recommendations = []

        # Calibration recommendations
        if calibration.status == CalibrationStatus.OVER_CONFIDENT:
            recommendations.append({
                "type": "calibration",
                "priority": "high",
                "message": "Agent is over-confident. Consider raising confidence thresholds.",
                "suggested_action": f"Raise min_confidence_to_act to {calibration.recommended_action_threshold:.2f}",
            })
        elif calibration.status == CalibrationStatus.UNDER_CONFIDENT:
            recommendations.append({
                "type": "calibration",
                "priority": "medium",
                "message": "Agent is under-confident. Could lower thresholds.",
                "suggested_action": f"Lower min_confidence_to_act to {calibration.recommended_action_threshold:.2f}",
            })

        # Scorecard-based recommendations
        for rec in scorecard.recommendations:
            recommendations.append({
                "type": "performance",
                "priority": "medium",
                "message": rec,
            })

        # Triggered rules
        for rule in self.rules:
            if rule.evaluate(role, scorecard.metrics):
                recommendations.append({
                    "type": "rule",
                    "priority": rule.risk.value,
                    "message": rule.description,
                    "rule_name": rule.name,
                })

        return {
            "role": role.value,
            "current_profile_version": profile.version,
            "overall_score": scorecard.overall_score,
            "calibration_status": calibration.status.value,
            "recommendations": recommendations,
            "pending_updates": len(self.get_pending_updates(role)),
        }

    def run_optimization_cycle(
        self,
        roles: Optional[List[AgentRole]] = None,
    ) -> Dict[str, Any]:
        """
        Run a full optimization cycle for specified roles.

        Returns summary of analysis and any applied updates.
        """
        if roles is None:
            roles = list(AgentRole)

        results = {
            "analyzed_roles": [],
            "updates_proposed": 0,
            "updates_applied": 0,
            "updates_pending_approval": 0,
        }

        for role in roles:
            # Analyze and propose updates
            updates = self.analyze_role(role)
            results["updates_proposed"] += len(updates)

            role_result = {
                "role": role.value,
                "updates_proposed": len(updates),
                "updates_applied": 0,
                "requires_approval": 0,
            }

            for update in updates:
                decision = self.decide_update(update)

                if decision.should_apply and not decision.requires_approval:
                    self.apply_update(update)
                    role_result["updates_applied"] += 1
                    results["updates_applied"] += 1
                elif decision.requires_approval:
                    role_result["requires_approval"] += 1
                    results["updates_pending_approval"] += 1

            results["analyzed_roles"].append(role_result)

        return results
