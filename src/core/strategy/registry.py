"""
Strategy Registry
=================

Versioned strategy profiles per agent role.

A strategy profile defines:
- Constraints: Boundaries for the agent's operation
- Preferred methods: How the agent approaches problems
- Risk tolerance: How much uncertainty is acceptable
- Tool priority: Which tools to prefer
- Evidence standards: What constitutes sufficient evidence
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Triangle agent roles."""
    WHY = "WHY"      # Root cause analysis
    HOW = "HOW"      # Solution planning
    WHAT = "WHAT"    # Specification
    WHEN = "WHEN"    # Timeline/scheduling
    WHERE = "WHERE"  # Channel/target selection
    WHO = "WHO"      # Stakeholder impact


class RiskTolerance(str, Enum):
    """Risk tolerance levels."""
    CONSERVATIVE = "conservative"  # Prefer safe, proven approaches
    MODERATE = "moderate"          # Balanced risk/reward
    AGGRESSIVE = "aggressive"      # Willing to try novel approaches


class EvidenceStandard(str, Enum):
    """Evidence requirements for conclusions."""
    MINIMAL = "minimal"          # Single source acceptable
    STANDARD = "standard"        # Multiple independent sources
    RIGOROUS = "rigorous"        # Verified, cross-referenced evidence
    SCIENTIFIC = "scientific"    # Reproducible, peer-reviewed level


@dataclass
class ToolPreference:
    """Preference for a specific tool."""
    tool_name: str
    priority: float  # 0-1, higher = more preferred
    success_rate: float  # Historical success rate
    avg_latency_ms: float
    last_used: Optional[datetime] = None
    use_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "priority": self.priority,
            "success_rate": self.success_rate,
            "avg_latency_ms": self.avg_latency_ms,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "use_count": self.use_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolPreference":
        return cls(
            tool_name=data["tool_name"],
            priority=data["priority"],
            success_rate=data["success_rate"],
            avg_latency_ms=data["avg_latency_ms"],
            last_used=datetime.fromisoformat(data["last_used"]) if data.get("last_used") else None,
            use_count=data.get("use_count", 0),
        )


@dataclass
class StrategyConstraint:
    """Operational constraint for an agent."""
    name: str
    description: str
    constraint_type: str  # "threshold", "limit", "require", "forbid"
    value: Any
    is_hard: bool = True  # Hard = must not violate; soft = penalty

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "constraint_type": self.constraint_type,
            "value": self.value,
            "is_hard": self.is_hard,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StrategyConstraint":
        return cls(
            name=data["name"],
            description=data["description"],
            constraint_type=data["constraint_type"],
            value=data["value"],
            is_hard=data.get("is_hard", True),
        )


@dataclass
class StrategyProfile:
    """
    Complete strategy profile for an agent role.

    Contains all configurable parameters that affect how the agent
    approaches problems and makes decisions.
    """
    role: AgentRole
    version: int = 1

    # Core parameters
    risk_tolerance: RiskTolerance = RiskTolerance.MODERATE
    evidence_standard: EvidenceStandard = EvidenceStandard.STANDARD

    # Confidence thresholds
    min_confidence_to_act: float = 0.6
    min_confidence_to_recommend: float = 0.4
    confidence_decay_rate: float = 0.1  # Per day decay

    # Tool preferences
    tool_preferences: List[ToolPreference] = field(default_factory=list)

    # Operational constraints
    constraints: List[StrategyConstraint] = field(default_factory=list)

    # Method preferences (role-specific)
    preferred_methods: List[str] = field(default_factory=list)
    avoided_methods: List[str] = field(default_factory=list)

    # Resource limits
    max_iterations: int = 5
    max_tool_calls: int = 10
    timeout_seconds: int = 300

    # Quality thresholds
    min_evidence_count: int = 2
    max_uncertainty_ratio: float = 0.3
    require_human_review: bool = False

    # Weights for scoring
    weight_accuracy: float = 0.3
    weight_speed: float = 0.2
    weight_thoroughness: float = 0.3
    weight_clarity: float = 0.2

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    created_by: str = "system"
    update_reason: str = ""

    def __post_init__(self):
        if not self.tool_preferences:
            self.tool_preferences = self._default_tool_preferences()
        if not self.constraints:
            self.constraints = self._default_constraints()
        if not self.preferred_methods:
            self.preferred_methods = self._default_methods()

    def _default_tool_preferences(self) -> List[ToolPreference]:
        """Get default tool preferences for this role."""
        role_tools = {
            AgentRole.WHY: [
                ToolPreference("memory_query", 0.9, 0.85, 50),
                ToolPreference("evidence_search", 0.85, 0.8, 100),
                ToolPreference("root_cause_analysis", 0.8, 0.75, 200),
            ],
            AgentRole.HOW: [
                ToolPreference("solution_generator", 0.9, 0.8, 150),
                ToolPreference("feasibility_check", 0.85, 0.85, 100),
                ToolPreference("risk_assessment", 0.8, 0.9, 80),
            ],
            AgentRole.WHAT: [
                ToolPreference("spec_generator", 0.9, 0.85, 200),
                ToolPreference("requirement_analyzer", 0.85, 0.8, 100),
                ToolPreference("prototype_builder", 0.75, 0.7, 300),
            ],
            AgentRole.WHEN: [
                ToolPreference("timeline_estimator", 0.9, 0.75, 100),
                ToolPreference("dependency_analyzer", 0.85, 0.85, 80),
                ToolPreference("milestone_planner", 0.8, 0.8, 120),
            ],
            AgentRole.WHERE: [
                ToolPreference("channel_analyzer", 0.9, 0.8, 100),
                ToolPreference("audience_matcher", 0.85, 0.75, 150),
                ToolPreference("delivery_optimizer", 0.8, 0.85, 80),
            ],
            AgentRole.WHO: [
                ToolPreference("stakeholder_analyzer", 0.9, 0.85, 100),
                ToolPreference("impact_assessor", 0.85, 0.8, 120),
                ToolPreference("communication_planner", 0.8, 0.75, 150),
            ],
        }
        return role_tools.get(self.role, [])

    def _default_constraints(self) -> List[StrategyConstraint]:
        """Get default constraints for this role."""
        base_constraints = [
            StrategyConstraint(
                "max_response_time",
                "Maximum time to generate response",
                "limit",
                self.timeout_seconds,
            ),
            StrategyConstraint(
                "min_confidence",
                "Minimum confidence for recommendations",
                "threshold",
                self.min_confidence_to_recommend,
            ),
        ]

        role_constraints = {
            AgentRole.WHY: [
                StrategyConstraint(
                    "require_evidence",
                    "All root causes must have supporting evidence",
                    "require",
                    True,
                ),
            ],
            AgentRole.HOW: [
                StrategyConstraint(
                    "feasibility_check",
                    "All solutions must pass feasibility check",
                    "require",
                    True,
                ),
            ],
            AgentRole.WHAT: [
                StrategyConstraint(
                    "spec_completeness",
                    "Specifications must cover all requirements",
                    "threshold",
                    0.9,
                ),
            ],
            AgentRole.WHEN: [
                StrategyConstraint(
                    "buffer_margin",
                    "Timeline must include buffer percentage",
                    "threshold",
                    0.2,
                ),
            ],
        }

        return base_constraints + role_constraints.get(self.role, [])

    def _default_methods(self) -> List[str]:
        """Get default preferred methods for this role."""
        role_methods = {
            AgentRole.WHY: ["5_whys", "fishbone_diagram", "fault_tree"],
            AgentRole.HOW: ["design_patterns", "risk_mitigation", "incremental_delivery"],
            AgentRole.WHAT: ["user_stories", "acceptance_criteria", "api_contracts"],
            AgentRole.WHEN: ["critical_path", "agile_sprints", "milestones"],
            AgentRole.WHERE: ["channel_matrix", "audience_segmentation", "a_b_testing"],
            AgentRole.WHO: ["stakeholder_map", "impact_assessment", "communication_plan"],
        }
        return role_methods.get(self.role, [])

    def get_tool_priority(self, tool_name: str) -> float:
        """Get priority for a specific tool."""
        for pref in self.tool_preferences:
            if pref.tool_name == tool_name:
                return pref.priority
        return 0.5  # Default priority

    def update_tool_stats(
        self,
        tool_name: str,
        success: bool,
        latency_ms: float,
    ) -> None:
        """Update tool statistics after use."""
        for pref in self.tool_preferences:
            if pref.tool_name == tool_name:
                # Update success rate with exponential moving average
                alpha = 0.1
                pref.success_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * pref.success_rate

                # Update latency
                pref.avg_latency_ms = alpha * latency_ms + (1 - alpha) * pref.avg_latency_ms

                pref.last_used = datetime.now(timezone.utc)
                pref.use_count += 1
                return

        # Tool not found, add it
        self.tool_preferences.append(ToolPreference(
            tool_name=tool_name,
            priority=0.5,
            success_rate=1.0 if success else 0.0,
            avg_latency_ms=latency_ms,
            last_used=datetime.now(timezone.utc),
            use_count=1,
        ))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "version": self.version,
            "risk_tolerance": self.risk_tolerance.value,
            "evidence_standard": self.evidence_standard.value,
            "min_confidence_to_act": self.min_confidence_to_act,
            "min_confidence_to_recommend": self.min_confidence_to_recommend,
            "confidence_decay_rate": self.confidence_decay_rate,
            "tool_preferences": [t.to_dict() for t in self.tool_preferences],
            "constraints": [c.to_dict() for c in self.constraints],
            "preferred_methods": self.preferred_methods,
            "avoided_methods": self.avoided_methods,
            "max_iterations": self.max_iterations,
            "max_tool_calls": self.max_tool_calls,
            "timeout_seconds": self.timeout_seconds,
            "min_evidence_count": self.min_evidence_count,
            "max_uncertainty_ratio": self.max_uncertainty_ratio,
            "require_human_review": self.require_human_review,
            "weight_accuracy": self.weight_accuracy,
            "weight_speed": self.weight_speed,
            "weight_thoroughness": self.weight_thoroughness,
            "weight_clarity": self.weight_clarity,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "update_reason": self.update_reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StrategyProfile":
        return cls(
            role=AgentRole(data["role"]),
            version=data["version"],
            risk_tolerance=RiskTolerance(data["risk_tolerance"]),
            evidence_standard=EvidenceStandard(data["evidence_standard"]),
            min_confidence_to_act=data["min_confidence_to_act"],
            min_confidence_to_recommend=data["min_confidence_to_recommend"],
            confidence_decay_rate=data.get("confidence_decay_rate", 0.1),
            tool_preferences=[ToolPreference.from_dict(t) for t in data.get("tool_preferences", [])],
            constraints=[StrategyConstraint.from_dict(c) for c in data.get("constraints", [])],
            preferred_methods=data.get("preferred_methods", []),
            avoided_methods=data.get("avoided_methods", []),
            max_iterations=data.get("max_iterations", 5),
            max_tool_calls=data.get("max_tool_calls", 10),
            timeout_seconds=data.get("timeout_seconds", 300),
            min_evidence_count=data.get("min_evidence_count", 2),
            max_uncertainty_ratio=data.get("max_uncertainty_ratio", 0.3),
            require_human_review=data.get("require_human_review", False),
            weight_accuracy=data.get("weight_accuracy", 0.3),
            weight_speed=data.get("weight_speed", 0.2),
            weight_thoroughness=data.get("weight_thoroughness", 0.3),
            weight_clarity=data.get("weight_clarity", 0.2),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            created_by=data.get("created_by", "system"),
            update_reason=data.get("update_reason", ""),
        )

    def content_hash(self) -> str:
        """Generate hash of strategy content for comparison."""
        content = json.dumps({
            "risk_tolerance": self.risk_tolerance.value,
            "evidence_standard": self.evidence_standard.value,
            "min_confidence_to_act": self.min_confidence_to_act,
            "min_confidence_to_recommend": self.min_confidence_to_recommend,
            "preferred_methods": sorted(self.preferred_methods),
            "avoided_methods": sorted(self.avoided_methods),
            "weights": {
                "accuracy": self.weight_accuracy,
                "speed": self.weight_speed,
                "thoroughness": self.weight_thoroughness,
                "clarity": self.weight_clarity,
            },
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class StrategyVersion:
    """A versioned snapshot of a strategy profile."""
    role: AgentRole
    version: int
    profile: StrategyProfile
    content_hash: str
    created_at: datetime
    created_by: str
    update_reason: str
    parent_version: Optional[int] = None

    # Performance metrics at time of snapshot
    success_rate: Optional[float] = None
    avg_score: Optional[float] = None
    sample_size: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "version": self.version,
            "profile": self.profile.to_dict(),
            "content_hash": self.content_hash,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "update_reason": self.update_reason,
            "parent_version": self.parent_version,
            "success_rate": self.success_rate,
            "avg_score": self.avg_score,
            "sample_size": self.sample_size,
        }


class StrategyRegistry:
    """
    In-memory registry of strategy profiles with versioning.

    Manages current and historical strategy profiles for each role.
    """

    def __init__(self):
        self._profiles: Dict[AgentRole, StrategyProfile] = {}
        self._history: Dict[AgentRole, List[StrategyVersion]] = {}
        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        """Initialize default profiles for all roles."""
        for role in AgentRole:
            profile = StrategyProfile(role=role)
            self._profiles[role] = profile
            self._history[role] = [
                StrategyVersion(
                    role=role,
                    version=1,
                    profile=profile,
                    content_hash=profile.content_hash(),
                    created_at=profile.created_at,
                    created_by="system",
                    update_reason="Initial default strategy",
                )
            ]

    def get_profile(self, role: AgentRole) -> StrategyProfile:
        """Get current strategy profile for a role."""
        return self._profiles.get(role, StrategyProfile(role=role))

    def get_all_profiles(self) -> Dict[AgentRole, StrategyProfile]:
        """Get all current profiles."""
        return dict(self._profiles)

    def update_profile(
        self,
        role: AgentRole,
        profile: StrategyProfile,
        updated_by: str = "system",
        reason: str = "",
    ) -> StrategyVersion:
        """Update strategy profile, creating a new version."""
        current = self._profiles.get(role)
        new_version = current.version + 1 if current else 1

        profile.version = new_version
        profile.updated_at = datetime.now(timezone.utc)
        profile.update_reason = reason

        # Create version snapshot
        version = StrategyVersion(
            role=role,
            version=new_version,
            profile=profile,
            content_hash=profile.content_hash(),
            created_at=datetime.now(timezone.utc),
            created_by=updated_by,
            update_reason=reason,
            parent_version=current.version if current else None,
        )

        self._profiles[role] = profile
        self._history[role].append(version)

        logger.info(f"Updated strategy for {role.value} to v{new_version}: {reason}")
        return version

    def get_version(self, role: AgentRole, version: int) -> Optional[StrategyVersion]:
        """Get a specific version of a strategy."""
        history = self._history.get(role, [])
        for v in history:
            if v.version == version:
                return v
        return None

    def get_history(
        self,
        role: AgentRole,
        limit: int = 10,
    ) -> List[StrategyVersion]:
        """Get version history for a role."""
        history = self._history.get(role, [])
        return sorted(history, key=lambda v: v.version, reverse=True)[:limit]

    def rollback(
        self,
        role: AgentRole,
        to_version: int,
        reason: str = "Rollback",
    ) -> Optional[StrategyVersion]:
        """Rollback to a previous version."""
        target = self.get_version(role, to_version)
        if not target:
            return None

        # Create new version with rolled-back content
        return self.update_profile(
            role=role,
            profile=target.profile,
            updated_by="system",
            reason=f"{reason} (rollback to v{to_version})",
        )

    def compare_versions(
        self,
        role: AgentRole,
        version1: int,
        version2: int,
    ) -> Dict[str, Any]:
        """Compare two versions of a strategy."""
        v1 = self.get_version(role, version1)
        v2 = self.get_version(role, version2)

        if not v1 or not v2:
            return {"error": "Version not found"}

        p1 = v1.profile
        p2 = v2.profile

        changes = {}

        # Compare key attributes
        if p1.risk_tolerance != p2.risk_tolerance:
            changes["risk_tolerance"] = {
                "from": p1.risk_tolerance.value,
                "to": p2.risk_tolerance.value,
            }

        if p1.evidence_standard != p2.evidence_standard:
            changes["evidence_standard"] = {
                "from": p1.evidence_standard.value,
                "to": p2.evidence_standard.value,
            }

        if p1.min_confidence_to_act != p2.min_confidence_to_act:
            changes["min_confidence_to_act"] = {
                "from": p1.min_confidence_to_act,
                "to": p2.min_confidence_to_act,
                "delta": p2.min_confidence_to_act - p1.min_confidence_to_act,
            }

        # Compare weights
        weight_changes = {}
        for attr in ["weight_accuracy", "weight_speed", "weight_thoroughness", "weight_clarity"]:
            val1 = getattr(p1, attr)
            val2 = getattr(p2, attr)
            if val1 != val2:
                weight_changes[attr] = {"from": val1, "to": val2}
        if weight_changes:
            changes["weights"] = weight_changes

        # Compare methods
        added_methods = set(p2.preferred_methods) - set(p1.preferred_methods)
        removed_methods = set(p1.preferred_methods) - set(p2.preferred_methods)
        if added_methods or removed_methods:
            changes["methods"] = {
                "added": list(added_methods),
                "removed": list(removed_methods),
            }

        return {
            "role": role.value,
            "version1": version1,
            "version2": version2,
            "changes": changes,
            "has_changes": len(changes) > 0,
        }
