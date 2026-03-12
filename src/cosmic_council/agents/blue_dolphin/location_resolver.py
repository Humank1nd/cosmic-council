"""
BLUE DOLPHIN - Location Resolver.

Resolves execution locations for scheduled actions.
This implements Criterion 1: Location resolution.

Every action must have a specific, resolved execution target.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import fnmatch

import structlog

from .models import (
    Location,
    LocationType,
    Environment,
    EnvironmentType,
    ExecutionTarget,
    RoutingRule,
    TargetStatus,
    ConnectivityStatus,
    STANDARD_LOCATIONS,
    STANDARD_ENVIRONMENTS,
)

logger = structlog.get_logger(__name__)


# Default routing rules
DEFAULT_ROUTING_RULES: List[RoutingRule] = [
    RoutingRule(
        name="high_risk_to_staging",
        description="Route high-risk actions to staging first",
        risk_levels=["HIGH", "CRITICAL"],
        target_environment="staging",
        priority=10,
    ),
    RoutingRule(
        name="database_to_primary",
        description="Route database actions to primary region",
        categories=["database"],
        target_region="us-east-1",
        priority=20,
    ),
    RoutingRule(
        name="deployment_to_all",
        description="Deployments go to production",
        categories=["deployment", "scaling", "restart"],
        target_environment="production",
        priority=50,
    ),
    RoutingRule(
        name="investigation_anywhere",
        description="Investigation can run anywhere",
        categories=["investigation", "monitoring"],
        target_environment="production",
        priority=100,
    ),
]


@dataclass
class ResolutionResult:
    """Result of location resolution."""
    target: ExecutionTarget
    success: bool = False
    matched_rules: List[str] = field(default_factory=list)
    fallback_used: bool = False
    warnings: List[str] = field(default_factory=list)


@dataclass
class BatchResolutionResult:
    """Result of batch location resolution."""
    targets: List[ExecutionTarget] = field(default_factory=list)
    resolved_count: int = 0
    unresolved_count: int = 0
    warnings: List[str] = field(default_factory=list)
    duration_ms: int = 0


class LocationResolver:
    """
    Resolves execution locations.

    Criterion 1: Every action has a specific execution target.
    """

    def __init__(
        self,
        locations: Optional[Dict[str, Location]] = None,
        environments: Optional[Dict[str, Environment]] = None,
        routing_rules: Optional[List[RoutingRule]] = None,
        default_environment: EnvironmentType = EnvironmentType.PRODUCTION,
    ):
        """
        Initialize the location resolver.

        Args:
            locations: Available locations
            environments: Available environments
            routing_rules: Routing rules
            default_environment: Default environment type
        """
        self.locations = locations or STANDARD_LOCATIONS
        self.environments = environments or STANDARD_ENVIRONMENTS
        self.routing_rules = routing_rules or DEFAULT_ROUTING_RULES
        self.default_environment = default_environment

        # Link locations to environments
        self._link_locations_to_environments()

        logger.info(
            "location_resolver_initialized",
            location_count=len(self.locations),
            environment_count=len(self.environments),
            rule_count=len(self.routing_rules),
        )

    def _link_locations_to_environments(self):
        """Link locations to their environments."""
        for env in self.environments.values():
            env.locations = []

        for loc_id, location in self.locations.items():
            # Match by namespace or labels
            if "production" in location.namespace.lower():
                if "production" in self.environments:
                    self.environments["production"].locations.append(location)
            elif "staging" in location.namespace.lower():
                if "staging" in self.environments:
                    self.environments["staging"].locations.append(location)
            elif "dev" in loc_id.lower() or location.type == LocationType.LOCAL:
                if "development" in self.environments:
                    self.environments["development"].locations.append(location)

    def resolve(
        self,
        action_id: str,
        spec_id: str = "",
        slot_id: str = "",
        category: str = "",
        risk_level: str = "MEDIUM",
        spec_type: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> ResolutionResult:
        """
        Resolve location for an action.

        Args:
            action_id: Action identifier
            spec_id: Specification ID
            slot_id: Schedule slot ID
            category: Action category
            risk_level: Risk level
            spec_type: Specification type
            context: Additional context

        Returns:
            ResolutionResult with target
        """
        context = context or {}
        warnings: List[str] = []
        matched_rules: List[str] = []

        # Create target
        target = ExecutionTarget(
            action_id=action_id,
            spec_id=spec_id,
            slot_id=slot_id,
        )

        # Apply routing rules
        target_env_name = None
        target_region = None
        target_location_name = None

        sorted_rules = sorted(self.routing_rules, key=lambda r: r.priority)
        for rule in sorted_rules:
            if not rule.enabled:
                continue

            if self._rule_matches(rule, action_id, category, risk_level, spec_type):
                matched_rules.append(rule.name)

                if rule.target_environment and not target_env_name:
                    target_env_name = rule.target_environment
                if rule.target_region and not target_region:
                    target_region = rule.target_region
                if rule.target_location and not target_location_name:
                    target_location_name = rule.target_location

        # Default environment
        if not target_env_name:
            target_env_name = self.default_environment.value
            warnings.append(f"Using default environment: {target_env_name}")

        # Find environment
        environment = self.environments.get(target_env_name)
        if not environment:
            # Try to find by type
            for env in self.environments.values():
                if env.type.value == target_env_name:
                    environment = env
                    break

        if not environment:
            target.resolution_error = f"Environment not found: {target_env_name}"
            return ResolutionResult(
                target=target,
                success=False,
                matched_rules=matched_rules,
                warnings=[target.resolution_error],
            )

        target.environment = environment

        # Find location
        location = self._find_best_location(
            environment, target_region, target_location_name, context
        )

        if not location:
            # Fallback
            location = self._find_fallback_location(environment, context)
            if location:
                warnings.append(f"Using fallback location: {location.name}")

        if not location:
            target.resolution_error = "No available location found"
            return ResolutionResult(
                target=target,
                success=False,
                matched_rules=matched_rules,
                warnings=[target.resolution_error],
            )

        target.location = location
        target.namespace = location.namespace
        target.is_resolved = True

        logger.debug(
            "location_resolved",
            action_id=action_id,
            location=location.name,
            environment=environment.name,
            rules_matched=len(matched_rules),
        )

        return ResolutionResult(
            target=target,
            success=True,
            matched_rules=matched_rules,
            fallback_used=len(warnings) > 0 and "fallback" in str(warnings),
            warnings=warnings,
        )

    def _rule_matches(
        self,
        rule: RoutingRule,
        action_id: str,
        category: str,
        risk_level: str,
        spec_type: str,
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

        # Check spec types
        if rule.spec_types:
            if spec_type.lower() not in [s.lower() for s in rule.spec_types]:
                return False

        return True

    def _find_best_location(
        self,
        environment: Environment,
        target_region: Optional[str],
        target_location_name: Optional[str],
        context: Dict[str, Any],
    ) -> Optional[Location]:
        """Find the best location in an environment."""
        candidates = [loc for loc in environment.locations if loc.is_available]

        if not candidates:
            return None

        # Filter by specific location name
        if target_location_name:
            for loc in candidates:
                if loc.name == target_location_name or loc.id == target_location_name:
                    return loc

        # Filter by region
        if target_region:
            regional = [loc for loc in candidates if loc.region == target_region]
            if regional:
                candidates = regional

        # Prefer primary location
        if environment.primary_location_id:
            for loc in candidates:
                if loc.id == environment.primary_location_id:
                    return loc

        # Return first available
        return candidates[0] if candidates else None

    def _find_fallback_location(
        self,
        environment: Environment,
        context: Dict[str, Any],
    ) -> Optional[Location]:
        """Find a fallback location."""
        # Try any location in the environment
        for loc in environment.locations:
            if loc.status != TargetStatus.UNAVAILABLE:
                return loc

        # Try other environments
        for env in self.environments.values():
            if env.id == environment.id:
                continue
            for loc in env.locations:
                if loc.is_available:
                    return loc

        return None

    def resolve_batch(
        self,
        actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> BatchResolutionResult:
        """
        Resolve locations for multiple actions.

        Args:
            actions: List of action dictionaries
            context: Additional context

        Returns:
            BatchResolutionResult
        """
        import time
        start_time = time.time()
        context = context or {}

        targets: List[ExecutionTarget] = []
        warnings: List[str] = []
        resolved = 0
        unresolved = 0

        for action in actions:
            result = self.resolve(
                action_id=action.get("action_id", action.get("id", "")),
                spec_id=action.get("spec_id", ""),
                slot_id=action.get("slot_id", ""),
                category=action.get("category", ""),
                risk_level=action.get("risk_level", "MEDIUM"),
                spec_type=action.get("spec_type", ""),
                context=context,
            )

            targets.append(result.target)
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
            targets=targets,
            resolved_count=resolved,
            unresolved_count=unresolved,
            warnings=warnings,
            duration_ms=duration_ms,
        )


def create_location_resolver(
    locations: Optional[Dict[str, Location]] = None,
    environments: Optional[Dict[str, Environment]] = None,
    routing_rules: Optional[List[RoutingRule]] = None,
    default_environment: EnvironmentType = EnvironmentType.PRODUCTION,
) -> LocationResolver:
    """Factory function to create a LocationResolver."""
    return LocationResolver(
        locations=locations,
        environments=environments,
        routing_rules=routing_rules,
        default_environment=default_environment,
    )
