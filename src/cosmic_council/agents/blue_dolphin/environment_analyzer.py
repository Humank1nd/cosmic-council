"""
BLUE DOLPHIN - Environment Analyzer.

Analyzes environment requirements for scheduled actions.
This implements Criterion 2: Environment matching.

Every action must be matched to an appropriate environment
based on its characteristics and requirements.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime

import structlog

from .models import (
    Environment,
    EnvironmentType,
    Location,
    LocationType,
    ExecutionTarget,
    TargetStatus,
    ConnectivityStatus,
    BlueDolphinConfig,
    STANDARD_ENVIRONMENTS,
)

logger = structlog.get_logger(__name__)


@dataclass
class EnvironmentRequirement:
    """Requirements for an environment."""
    min_cpu: float = 0.0
    min_memory_gb: float = 0.0
    min_storage_gb: float = 0.0
    required_capabilities: Set[str] = field(default_factory=set)
    required_labels: Dict[str, str] = field(default_factory=dict)
    preferred_provider: Optional[str] = None
    preferred_region: Optional[str] = None
    requires_production: bool = False
    requires_staging_first: bool = False
    allows_edge: bool = True


@dataclass
class EnvironmentMatch:
    """Result of environment matching."""
    environment: Environment
    score: float = 0.0
    matched_requirements: List[str] = field(default_factory=list)
    unmatched_requirements: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def is_suitable(self) -> bool:
        """Check if environment is suitable."""
        return len(self.unmatched_requirements) == 0 and self.score > 0


@dataclass
class EnvironmentAnalysisResult:
    """Result of environment analysis."""
    action_id: str = ""
    recommended_environment: Optional[Environment] = None
    all_matches: List[EnvironmentMatch] = field(default_factory=list)
    success: bool = False
    reasoning: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class EnvironmentAnalyzer:
    """
    Analyzes and matches environments to actions.

    Criterion 2: Every action is matched to an appropriate environment.
    """

    def __init__(
        self,
        environments: Optional[Dict[str, Environment]] = None,
        config: Optional[BlueDolphinConfig] = None,
    ):
        """
        Initialize the environment analyzer.

        Args:
            environments: Available environments
            config: Configuration
        """
        self.environments = environments or STANDARD_ENVIRONMENTS
        self.config = config or BlueDolphinConfig()

        logger.info(
            "environment_analyzer_initialized",
            environment_count=len(self.environments),
        )

    def analyze(
        self,
        action_id: str,
        category: str = "",
        risk_level: str = "MEDIUM",
        requirements: Optional[EnvironmentRequirement] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> EnvironmentAnalysisResult:
        """
        Analyze and find the best environment for an action.

        Args:
            action_id: Action identifier
            category: Action category
            risk_level: Risk level
            requirements: Specific requirements
            context: Additional context

        Returns:
            EnvironmentAnalysisResult with recommendations
        """
        context = context or {}
        requirements = requirements or self._infer_requirements(
            action_id, category, risk_level, context
        )

        reasoning: List[str] = []
        warnings: List[str] = []
        all_matches: List[EnvironmentMatch] = []

        # Analyze each environment
        for env_id, environment in self.environments.items():
            match = self._evaluate_environment(
                environment, requirements, category, risk_level, context
            )
            all_matches.append(match)

        # Sort by score (highest first)
        all_matches.sort(key=lambda m: m.score, reverse=True)

        # Find recommended environment
        recommended = None
        for match in all_matches:
            if match.is_suitable:
                recommended = match.environment
                reasoning.append(
                    f"Selected {match.environment.name} with score {match.score:.2f}"
                )
                reasoning.extend(
                    [f"Matched: {r}" for r in match.matched_requirements[:3]]
                )
                break

        if not recommended:
            # Fallback logic
            if self.config.fallback_enabled:
                # Try to find any available environment
                for match in all_matches:
                    if match.environment.locations:
                        recommended = match.environment
                        warnings.append(
                            f"Using fallback environment: {match.environment.name}"
                        )
                        reasoning.append("No ideal match found, using fallback")
                        break

        if not recommended:
            warnings.append("No suitable environment found")
            reasoning.append("All environments failed to meet requirements")

        success = recommended is not None

        logger.info(
            "environment_analysis_complete",
            action_id=action_id,
            recommended=recommended.name if recommended else None,
            success=success,
            matches_evaluated=len(all_matches),
        )

        return EnvironmentAnalysisResult(
            action_id=action_id,
            recommended_environment=recommended,
            all_matches=all_matches,
            success=success,
            reasoning=reasoning,
            warnings=warnings,
        )

    def _infer_requirements(
        self,
        action_id: str,
        category: str,
        risk_level: str,
        context: Dict[str, Any],
    ) -> EnvironmentRequirement:
        """Infer requirements from action characteristics."""
        req = EnvironmentRequirement()

        # Category-based inference
        category_lower = category.lower()
        if category_lower in ["deployment", "release"]:
            req.requires_staging_first = True
            req.min_memory_gb = 1.0
        elif category_lower in ["database", "migration"]:
            req.min_storage_gb = 10.0
            req.required_capabilities.add("database")
        elif category_lower in ["scaling", "autoscale"]:
            req.min_cpu = 2.0
            req.required_capabilities.add("scaling")
        elif category_lower in ["investigation", "monitoring"]:
            req.allows_edge = True

        # Risk-based inference
        risk_upper = risk_level.upper()
        if risk_upper in ["HIGH", "CRITICAL"]:
            req.requires_staging_first = True
        elif risk_upper == "NEGLIGIBLE":
            req.allows_edge = True

        # Context overrides
        if context.get("requires_production"):
            req.requires_production = True
        if context.get("preferred_region"):
            req.preferred_region = context["preferred_region"]

        return req

    def _evaluate_environment(
        self,
        environment: Environment,
        requirements: EnvironmentRequirement,
        category: str,
        risk_level: str,
        context: Dict[str, Any],
    ) -> EnvironmentMatch:
        """Evaluate how well an environment matches requirements."""
        score = 0.0
        matched: List[str] = []
        unmatched: List[str] = []
        warnings: List[str] = []

        # Check basic availability
        available_locations = [
            loc for loc in environment.locations
            if loc.status == TargetStatus.AVAILABLE
        ]

        if not available_locations:
            unmatched.append("No available locations")
            return EnvironmentMatch(
                environment=environment,
                score=0.0,
                matched_requirements=matched,
                unmatched_requirements=unmatched,
                warnings=warnings,
            )

        score += 10.0
        matched.append("Has available locations")

        # Check production requirement
        if requirements.requires_production:
            if environment.is_production:
                score += 20.0
                matched.append("Is production environment")
            else:
                unmatched.append("Requires production but is not production")

        # Check staging requirement for risky actions
        if requirements.requires_staging_first:
            if environment.type == EnvironmentType.STAGING:
                score += 15.0
                matched.append("Staging environment for staged rollout")
            elif environment.is_production:
                warnings.append("High-risk action going directly to production")
                score -= 5.0

        # Check resource capacity
        total_cpu = sum(loc.cpu_available for loc in available_locations)
        total_memory = sum(loc.memory_available_gb for loc in available_locations)
        total_storage = sum(loc.storage_available_gb for loc in available_locations)

        if total_cpu >= requirements.min_cpu:
            score += 5.0
            matched.append(f"CPU capacity: {total_cpu:.1f} cores")
        elif requirements.min_cpu > 0:
            unmatched.append(f"Insufficient CPU: {total_cpu:.1f} < {requirements.min_cpu}")

        if total_memory >= requirements.min_memory_gb:
            score += 5.0
            matched.append(f"Memory capacity: {total_memory:.1f} GB")
        elif requirements.min_memory_gb > 0:
            unmatched.append(f"Insufficient memory: {total_memory:.1f} < {requirements.min_memory_gb}")

        if total_storage >= requirements.min_storage_gb:
            score += 5.0
            matched.append(f"Storage capacity: {total_storage:.1f} GB")
        elif requirements.min_storage_gb > 0:
            unmatched.append(f"Insufficient storage: {total_storage:.1f} < {requirements.min_storage_gb}")

        # Check region preference
        if requirements.preferred_region:
            regional_locations = [
                loc for loc in available_locations
                if loc.region == requirements.preferred_region
            ]
            if regional_locations:
                score += 10.0
                matched.append(f"Has locations in {requirements.preferred_region}")
            else:
                warnings.append(f"No locations in preferred region {requirements.preferred_region}")

        # Check provider preference
        if requirements.preferred_provider:
            provider_locations = [
                loc for loc in available_locations
                if loc.provider.value == requirements.preferred_provider
            ]
            if provider_locations:
                score += 5.0
                matched.append(f"Has {requirements.preferred_provider} locations")

        # Check capabilities
        env_capabilities = self._get_environment_capabilities(environment)
        for cap in requirements.required_capabilities:
            if cap in env_capabilities:
                score += 5.0
                matched.append(f"Has capability: {cap}")
            else:
                unmatched.append(f"Missing capability: {cap}")

        # Check labels
        for key, value in requirements.required_labels.items():
            if self._environment_has_label(environment, key, value):
                score += 3.0
                matched.append(f"Has label {key}={value}")
            else:
                unmatched.append(f"Missing label {key}={value}")

        # Check change freeze
        if environment.change_freeze:
            unmatched.append("Environment is in change freeze")
            score -= 50.0

        # Check maintenance window requirement
        if environment.maintenance_window_only:
            # In real implementation, check if we're in a maintenance window
            warnings.append("Environment requires maintenance window")

        # Check allowed/blocked actions
        if environment.blocked_actions:
            for blocked in environment.blocked_actions:
                if blocked in category.lower():
                    unmatched.append(f"Action category blocked: {blocked}")
                    score -= 100.0

        if environment.allowed_actions:
            action_allowed = False
            for allowed in environment.allowed_actions:
                if allowed in category.lower():
                    action_allowed = True
                    score += 5.0
                    matched.append(f"Action explicitly allowed: {allowed}")
                    break
            if not action_allowed and environment.allowed_actions:
                unmatched.append("Action not in allowed list")

        return EnvironmentMatch(
            environment=environment,
            score=max(0, score),
            matched_requirements=matched,
            unmatched_requirements=unmatched,
            warnings=warnings,
        )

    def _get_environment_capabilities(
        self,
        environment: Environment,
    ) -> Set[str]:
        """Get capabilities from environment and its locations."""
        capabilities: Set[str] = set()

        # Add from environment metadata
        if "capabilities" in environment.metadata:
            capabilities.update(environment.metadata["capabilities"])

        # Add from location labels
        for location in environment.locations:
            if "capability" in location.labels:
                capabilities.add(location.labels["capability"])
            if "capabilities" in location.metadata:
                capabilities.update(location.metadata["capabilities"])

        # Infer from location types
        for location in environment.locations:
            if location.type == LocationType.KUBERNETES_CLUSTER:
                capabilities.add("kubernetes")
                capabilities.add("scaling")
            elif location.type == LocationType.SERVERLESS:
                capabilities.add("serverless")
            elif location.type == LocationType.EDGE_NODE:
                capabilities.add("edge")

        return capabilities

    def _environment_has_label(
        self,
        environment: Environment,
        key: str,
        value: str,
    ) -> bool:
        """Check if environment or any location has the label."""
        # Check environment metadata
        if environment.metadata.get(key) == value:
            return True

        # Check location labels
        for location in environment.locations:
            if location.labels.get(key) == value:
                return True

        return False

    def analyze_batch(
        self,
        actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[EnvironmentAnalysisResult]:
        """
        Analyze environments for multiple actions.

        Args:
            actions: List of action dictionaries
            context: Shared context

        Returns:
            List of EnvironmentAnalysisResult
        """
        context = context or {}
        results = []

        for action in actions:
            result = self.analyze(
                action_id=action.get("action_id", action.get("id", "")),
                category=action.get("category", ""),
                risk_level=action.get("risk_level", "MEDIUM"),
                context=context,
            )
            results.append(result)

        logger.info(
            "batch_environment_analysis_complete",
            total=len(actions),
            successful=sum(1 for r in results if r.success),
        )

        return results

    def get_environment_status(self) -> Dict[str, Any]:
        """Get status of all environments."""
        status = {}

        for env_id, environment in self.environments.items():
            available_count = sum(
                1 for loc in environment.locations
                if loc.status == TargetStatus.AVAILABLE
            )
            total_count = len(environment.locations)

            status[env_id] = {
                "name": environment.name,
                "type": environment.type.value,
                "is_production": environment.is_production,
                "change_freeze": environment.change_freeze,
                "locations_available": available_count,
                "locations_total": total_count,
                "requires_approval": environment.requires_approval,
            }

        return status


def create_environment_analyzer(
    environments: Optional[Dict[str, Environment]] = None,
    config: Optional[BlueDolphinConfig] = None,
) -> EnvironmentAnalyzer:
    """Factory function to create an EnvironmentAnalyzer."""
    return EnvironmentAnalyzer(
        environments=environments,
        config=config,
    )
