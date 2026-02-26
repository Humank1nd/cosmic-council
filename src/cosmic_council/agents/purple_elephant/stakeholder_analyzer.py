"""
PURPLE ELEPHANT - Stakeholder Analyzer.

Analyzes and identifies all relevant stakeholders for actions.
This implements Criterion 2: Stakeholder identification.

All relevant stakeholders must be identified for each action.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime

import structlog

from .models import (
    Stakeholder,
    StakeholderType,
    ResponsibilityType,
    PurpleElephantConfig,
    STANDARD_STAKEHOLDERS,
)

logger = structlog.get_logger(__name__)


@dataclass
class StakeholderRequirement:
    """Requirements for stakeholders on an action."""
    needs_executor: bool = True
    needs_approver: bool = False
    needs_reviewer: bool = False
    needs_observer: bool = False
    required_capabilities: Set[str] = field(default_factory=set)
    preferred_teams: List[str] = field(default_factory=list)
    exclude_stakeholders: Set[str] = field(default_factory=set)


@dataclass
class StakeholderMatch:
    """A stakeholder matched to an action."""
    stakeholder: Stakeholder
    responsibility_type: ResponsibilityType
    score: float = 0.0
    match_reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class StakeholderAnalysisResult:
    """Result of stakeholder analysis for an action."""
    action_id: str = ""
    identified_stakeholders: List[StakeholderMatch] = field(default_factory=list)
    executor: Optional[Stakeholder] = None
    approver: Optional[Stakeholder] = None
    reviewers: List[Stakeholder] = field(default_factory=list)
    observers: List[Stakeholder] = field(default_factory=list)
    success: bool = False
    reasoning: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def stakeholder_count(self) -> int:
        """Total number of stakeholders identified."""
        return len(self.identified_stakeholders)


class StakeholderAnalyzer:
    """
    Analyzes and identifies stakeholders for actions.

    Criterion 2: All relevant stakeholders are identified.
    """

    def __init__(
        self,
        stakeholders: Optional[Dict[str, Stakeholder]] = None,
        config: Optional[PurpleElephantConfig] = None,
    ):
        """
        Initialize the stakeholder analyzer.

        Args:
            stakeholders: Available stakeholders
            config: Configuration
        """
        self.stakeholders = stakeholders or STANDARD_STAKEHOLDERS
        self.config = config or PurpleElephantConfig()

        logger.info(
            "stakeholder_analyzer_initialized",
            stakeholder_count=len(self.stakeholders),
        )

    def analyze(
        self,
        action_id: str,
        category: str = "",
        risk_level: str = "MEDIUM",
        service_name: str = "",
        environment: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> StakeholderAnalysisResult:
        """
        Analyze and identify all stakeholders for an action.

        Args:
            action_id: Action identifier
            category: Action category
            risk_level: Risk level
            service_name: Service being acted upon
            environment: Target environment
            context: Additional context

        Returns:
            StakeholderAnalysisResult with all identified stakeholders
        """
        context = context or {}
        reasoning: List[str] = []
        warnings: List[str] = []

        result = StakeholderAnalysisResult(action_id=action_id)

        # Determine requirements based on action characteristics
        requirements = self._infer_requirements(
            action_id, category, risk_level, service_name, environment, context
        )

        reasoning.append(f"Analyzing stakeholders for {action_id}")

        # Find executor
        if requirements.needs_executor:
            executor_match = self._find_best_stakeholder(
                ResponsibilityType.EXECUTOR,
                requirements,
                category,
                service_name,
                context,
            )
            if executor_match:
                result.identified_stakeholders.append(executor_match)
                result.executor = executor_match.stakeholder
                reasoning.append(f"Executor: {executor_match.stakeholder.name}")
            else:
                warnings.append("No executor found")

        # Find approver for high-risk actions
        if requirements.needs_approver:
            approver_match = self._find_best_stakeholder(
                ResponsibilityType.APPROVER,
                requirements,
                category,
                service_name,
                context,
            )
            if approver_match:
                result.identified_stakeholders.append(approver_match)
                result.approver = approver_match.stakeholder
                reasoning.append(f"Approver: {approver_match.stakeholder.name}")
            else:
                warnings.append("High-risk action without approver")

        # Find reviewers
        if requirements.needs_reviewer:
            reviewer_matches = self._find_stakeholders_by_type(
                ResponsibilityType.REVIEWER,
                requirements,
                category,
                service_name,
                context,
                limit=2,
            )
            for match in reviewer_matches:
                result.identified_stakeholders.append(match)
                result.reviewers.append(match.stakeholder)
            if reviewer_matches:
                reasoning.append(f"Reviewers: {len(reviewer_matches)}")

        # Find observers (service owners, team leads)
        if requirements.needs_observer or self.config.auto_assign_service_owners:
            observer_matches = self._find_observers(
                category, service_name, context
            )
            for match in observer_matches:
                # Don't duplicate stakeholders
                existing_ids = {s.stakeholder.id for s in result.identified_stakeholders}
                if match.stakeholder.id not in existing_ids:
                    result.identified_stakeholders.append(match)
                    result.observers.append(match.stakeholder)
            if observer_matches:
                reasoning.append(f"Observers: {len(observer_matches)}")

        # Determine success
        result.success = (
            (not requirements.needs_executor or result.executor is not None) and
            (not requirements.needs_approver or result.approver is not None)
        )

        result.reasoning = reasoning
        result.warnings = warnings

        logger.info(
            "stakeholder_analysis_complete",
            action_id=action_id,
            stakeholder_count=result.stakeholder_count,
            has_executor=result.executor is not None,
            has_approver=result.approver is not None,
            success=result.success,
        )

        return result

    def _infer_requirements(
        self,
        action_id: str,
        category: str,
        risk_level: str,
        service_name: str,
        environment: str,
        context: Dict[str, Any],
    ) -> StakeholderRequirement:
        """Infer stakeholder requirements from action characteristics."""
        req = StakeholderRequirement()

        # Always need executor
        req.needs_executor = True

        # High-risk or production needs approver
        risk_upper = risk_level.upper()
        if risk_upper in ["HIGH", "CRITICAL"]:
            req.needs_approver = True
            req.needs_reviewer = True

        if environment.lower() == "production":
            req.needs_approver = True

        # Category-based capabilities
        category_lower = category.lower()
        if category_lower in ["database", "backup", "migration"]:
            req.required_capabilities.add("database")
            req.preferred_teams.append("database")
        elif category_lower in ["deployment", "scaling", "restart"]:
            req.required_capabilities.add("kubernetes")
            req.preferred_teams.append("platform")
        elif category_lower in ["monitoring", "investigation"]:
            req.required_capabilities.add("monitoring")

        # Observer for all production actions
        if environment.lower() == "production":
            req.needs_observer = True

        return req

    def _find_best_stakeholder(
        self,
        responsibility_type: ResponsibilityType,
        requirements: StakeholderRequirement,
        category: str,
        service_name: str,
        context: Dict[str, Any],
    ) -> Optional[StakeholderMatch]:
        """Find the best stakeholder for a responsibility type."""
        candidates: List[StakeholderMatch] = []

        for stakeholder in self.stakeholders.values():
            if stakeholder.id in requirements.exclude_stakeholders:
                continue

            if not self._is_available(stakeholder):
                continue

            score, reasons = self._score_stakeholder(
                stakeholder,
                responsibility_type,
                requirements,
                category,
                service_name,
            )

            if score > 0:
                candidates.append(StakeholderMatch(
                    stakeholder=stakeholder,
                    responsibility_type=responsibility_type,
                    score=score,
                    match_reasons=reasons,
                ))

        if not candidates:
            return None

        # Sort by score (highest first)
        candidates.sort(key=lambda m: m.score, reverse=True)
        return candidates[0]

    def _find_stakeholders_by_type(
        self,
        responsibility_type: ResponsibilityType,
        requirements: StakeholderRequirement,
        category: str,
        service_name: str,
        context: Dict[str, Any],
        limit: int = 3,
    ) -> List[StakeholderMatch]:
        """Find multiple stakeholders for a responsibility type."""
        candidates: List[StakeholderMatch] = []

        for stakeholder in self.stakeholders.values():
            if stakeholder.id in requirements.exclude_stakeholders:
                continue

            if not self._is_available(stakeholder):
                continue

            score, reasons = self._score_stakeholder(
                stakeholder,
                responsibility_type,
                requirements,
                category,
                service_name,
            )

            if score > 0:
                candidates.append(StakeholderMatch(
                    stakeholder=stakeholder,
                    responsibility_type=responsibility_type,
                    score=score,
                    match_reasons=reasons,
                ))

        # Sort by score and take top N
        candidates.sort(key=lambda m: m.score, reverse=True)
        return candidates[:limit]

    def _find_observers(
        self,
        category: str,
        service_name: str,
        context: Dict[str, Any],
    ) -> List[StakeholderMatch]:
        """Find observers (service owners, team leads)."""
        observers: List[StakeholderMatch] = []

        for stakeholder in self.stakeholders.values():
            reasons = []

            # Service owners are observers
            if service_name and service_name in stakeholder.services_owned:
                reasons.append(f"Owns service: {service_name}")

            # Team leads with relevant capabilities
            if stakeholder.type == StakeholderType.TEAM:
                category_lower = category.lower()
                if any(cap in category_lower for cap in stakeholder.capabilities):
                    reasons.append(f"Team with relevant capability")

            if reasons:
                observers.append(StakeholderMatch(
                    stakeholder=stakeholder,
                    responsibility_type=ResponsibilityType.OBSERVER,
                    score=len(reasons) * 10,
                    match_reasons=reasons,
                ))

        return observers

    def _score_stakeholder(
        self,
        stakeholder: Stakeholder,
        responsibility_type: ResponsibilityType,
        requirements: StakeholderRequirement,
        category: str,
        service_name: str,
    ) -> tuple[float, List[str]]:
        """Score a stakeholder for a responsibility."""
        score = 0.0
        reasons: List[str] = []

        # Base score for availability
        if stakeholder.is_available:
            score += 10.0
            reasons.append("Available")

        # On-call bonus for executors
        if responsibility_type == ResponsibilityType.EXECUTOR:
            if stakeholder.on_call:
                score += 20.0
                reasons.append("On-call")

        # Capability match
        for cap in requirements.required_capabilities:
            if cap in stakeholder.capabilities:
                score += 15.0
                reasons.append(f"Has capability: {cap}")

        # Team preference
        if stakeholder.team in requirements.preferred_teams:
            score += 10.0
            reasons.append(f"Preferred team: {stakeholder.team}")

        # Service ownership
        if service_name and service_name in stakeholder.services_owned:
            score += 25.0
            reasons.append(f"Owns service: {service_name}")

        # Automation bonus for low-risk monitoring
        if stakeholder.type == StakeholderType.AUTOMATION:
            if category.lower() in ["monitoring", "notification", "investigation"]:
                score += 15.0
                reasons.append("Automation suitable for category")

        # Escalation level (prefer primary)
        if stakeholder.escalation_level == 0:
            score += 5.0
            reasons.append("Primary contact")

        return score, reasons

    def _is_available(self, stakeholder: Stakeholder) -> bool:
        """Check if stakeholder is available."""
        if not stakeholder.is_available:
            return False

        if stakeholder.vacation_until:
            if datetime.utcnow() < stakeholder.vacation_until:
                return False

        return True

    def analyze_batch(
        self,
        actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[StakeholderAnalysisResult]:
        """
        Analyze stakeholders for multiple actions.

        Args:
            actions: List of action dictionaries
            context: Shared context

        Returns:
            List of StakeholderAnalysisResult
        """
        context = context or {}
        results = []

        for action in actions:
            result = self.analyze(
                action_id=action.get("action_id", action.get("id", "")),
                category=action.get("category", ""),
                risk_level=action.get("risk_level", "MEDIUM"),
                service_name=action.get("service_name", ""),
                environment=action.get("environment", ""),
                context=context,
            )
            results.append(result)

        logger.info(
            "batch_stakeholder_analysis_complete",
            total=len(actions),
            successful=sum(1 for r in results if r.success),
        )

        return results

    def get_stakeholder_summary(self) -> Dict[str, Any]:
        """Get summary of all stakeholders."""
        summary = {
            "total": len(self.stakeholders),
            "available": 0,
            "on_call": 0,
            "by_type": {},
            "by_team": {},
        }

        for stakeholder in self.stakeholders.values():
            if self._is_available(stakeholder):
                summary["available"] += 1
            if stakeholder.on_call:
                summary["on_call"] += 1

            type_name = stakeholder.type.value
            summary["by_type"][type_name] = summary["by_type"].get(type_name, 0) + 1

            if stakeholder.team:
                summary["by_team"][stakeholder.team] = summary["by_team"].get(stakeholder.team, 0) + 1

        return summary


def create_stakeholder_analyzer(
    stakeholders: Optional[Dict[str, Stakeholder]] = None,
    config: Optional[PurpleElephantConfig] = None,
) -> StakeholderAnalyzer:
    """Factory function to create a StakeholderAnalyzer."""
    return StakeholderAnalyzer(
        stakeholders=stakeholders,
        config=config,
    )
