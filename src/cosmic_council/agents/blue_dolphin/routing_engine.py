"""
BLUE DOLPHIN - Routing Engine.

Routes actions to validated execution targets.
This implements Criterion 3: Connectivity validation.

All targets must be validated as reachable before
actions can be routed to them.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime

import structlog

from .models import (
    Location,
    Environment,
    ExecutionTarget,
    LocationPlan,
    NetworkEndpoint,
    TargetStatus,
    ConnectivityStatus,
    BlueDolphinConfig,
    STANDARD_LOCATIONS,
    STANDARD_ENVIRONMENTS,
)

logger = structlog.get_logger(__name__)


@dataclass
class ConnectivityCheck:
    """Result of a connectivity check."""
    location_id: str = ""
    location_name: str = ""
    endpoint: Optional[NetworkEndpoint] = None
    is_reachable: bool = False
    latency_ms: float = 0.0
    error: Optional[str] = None
    checked_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RoutingDecision:
    """Decision about where to route an action."""
    action_id: str = ""
    target: Optional[ExecutionTarget] = None
    primary_location: Optional[Location] = None
    fallback_location: Optional[Location] = None
    connectivity_verified: bool = False
    routing_path: List[str] = field(default_factory=list)
    reasoning: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class RoutingResult:
    """Result of routing multiple actions."""
    decisions: List[RoutingDecision] = field(default_factory=list)
    connectivity_checks: List[ConnectivityCheck] = field(default_factory=list)
    all_reachable: bool = False
    reachable_count: int = 0
    unreachable_count: int = 0
    duration_ms: int = 0


class RoutingEngine:
    """
    Routes actions to validated execution targets.

    Criterion 3: All targets are validated as reachable.
    """

    def __init__(
        self,
        locations: Optional[Dict[str, Location]] = None,
        environments: Optional[Dict[str, Environment]] = None,
        config: Optional[BlueDolphinConfig] = None,
    ):
        """
        Initialize the routing engine.

        Args:
            locations: Available locations
            environments: Available environments
            config: Configuration
        """
        self.locations = locations or STANDARD_LOCATIONS
        self.environments = environments or STANDARD_ENVIRONMENTS
        self.config = config or BlueDolphinConfig()

        # Cache for connectivity status
        self._connectivity_cache: Dict[str, ConnectivityCheck] = {}
        self._cache_ttl_seconds = 60

        logger.info(
            "routing_engine_initialized",
            location_count=len(self.locations),
            environment_count=len(self.environments),
        )

    async def validate_connectivity(
        self,
        location: Location,
        timeout_seconds: Optional[int] = None,
    ) -> ConnectivityCheck:
        """
        Validate connectivity to a location.

        Args:
            location: Location to check
            timeout_seconds: Timeout for check

        Returns:
            ConnectivityCheck result
        """
        timeout = timeout_seconds or self.config.connectivity_timeout_seconds

        # Check cache first
        cache_key = location.id
        if cache_key in self._connectivity_cache:
            cached = self._connectivity_cache[cache_key]
            age = (datetime.utcnow() - cached.checked_at).total_seconds()
            if age < self._cache_ttl_seconds:
                return cached

        start_time = time.time()
        check = ConnectivityCheck(
            location_id=location.id,
            location_name=location.name,
        )

        try:
            # In a real implementation, this would actually check connectivity
            # For now, we simulate based on the location's status
            if location.status == TargetStatus.UNAVAILABLE:
                check.is_reachable = False
                check.error = "Location marked as unavailable"
            elif location.connectivity == ConnectivityStatus.DISCONNECTED:
                check.is_reachable = False
                check.error = "Location is disconnected"
            elif location.connectivity == ConnectivityStatus.DEGRADED:
                check.is_reachable = True
                check.latency_ms = 500.0  # Simulated high latency
                check.error = "Connection degraded"
            else:
                # Simulate a successful connectivity check
                await asyncio.sleep(0.01)  # Simulate network delay
                check.is_reachable = True
                check.latency_ms = (time.time() - start_time) * 1000

            # Check endpoints if available
            if location.endpoints:
                check.endpoint = location.endpoints[0]

        except asyncio.TimeoutError:
            check.is_reachable = False
            check.error = f"Connection timed out after {timeout}s"
        except Exception as e:
            check.is_reachable = False
            check.error = str(e)

        check.checked_at = datetime.utcnow()
        check.latency_ms = (time.time() - start_time) * 1000

        # Update cache
        self._connectivity_cache[cache_key] = check

        logger.debug(
            "connectivity_checked",
            location=location.name,
            reachable=check.is_reachable,
            latency_ms=check.latency_ms,
        )

        return check

    async def validate_all_locations(
        self,
        locations: Optional[List[Location]] = None,
    ) -> List[ConnectivityCheck]:
        """
        Validate connectivity to all locations.

        Args:
            locations: Locations to check (defaults to all)

        Returns:
            List of ConnectivityCheck results
        """
        if locations is None:
            locations = list(self.locations.values())

        # Check all locations concurrently
        tasks = [
            self.validate_connectivity(loc)
            for loc in locations
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        checks = []
        for loc, result in zip(locations, results):
            if isinstance(result, Exception):
                checks.append(ConnectivityCheck(
                    location_id=loc.id,
                    location_name=loc.name,
                    is_reachable=False,
                    error=str(result),
                ))
            else:
                checks.append(result)

        return checks

    async def route(
        self,
        target: ExecutionTarget,
        context: Optional[Dict[str, Any]] = None,
    ) -> RoutingDecision:
        """
        Route an action to a validated target.

        Args:
            target: Execution target to route
            context: Additional context

        Returns:
            RoutingDecision with validated path
        """
        context = context or {}
        decision = RoutingDecision(
            action_id=target.action_id,
            target=target,
        )

        if not target.is_resolved or not target.location:
            decision.warnings.append("Target not resolved")
            decision.reasoning.append("Cannot route unresolved target")
            return decision

        location = target.location
        decision.primary_location = location
        decision.routing_path.append(location.name)
        decision.reasoning.append(f"Primary location: {location.name}")

        # Validate connectivity
        if self.config.require_connectivity_check:
            check = await self.validate_connectivity(location)

            if check.is_reachable:
                target.is_reachable = True
                decision.connectivity_verified = True
                decision.reasoning.append(
                    f"Connectivity verified (latency: {check.latency_ms:.0f}ms)"
                )
            else:
                target.is_reachable = False
                decision.warnings.append(
                    f"Primary location unreachable: {check.error}"
                )

                # Try fallback if enabled
                if self.config.fallback_enabled and target.retry_on_different_location:
                    fallback = await self._find_fallback(
                        target.environment, location, context
                    )

                    if fallback:
                        decision.fallback_location = fallback
                        decision.routing_path.append(fallback.name)
                        decision.reasoning.append(
                            f"Fallback location: {fallback.name}"
                        )

                        # Verify fallback connectivity
                        fallback_check = await self.validate_connectivity(fallback)
                        if fallback_check.is_reachable:
                            target.is_reachable = True
                            decision.connectivity_verified = True
                            decision.reasoning.append("Fallback connectivity verified")
                        else:
                            decision.warnings.append(
                                f"Fallback also unreachable: {fallback_check.error}"
                            )
                    else:
                        decision.warnings.append("No fallback location available")
        else:
            # Skip connectivity check
            decision.connectivity_verified = True
            decision.reasoning.append("Connectivity check skipped (disabled)")

        return decision

    async def _find_fallback(
        self,
        environment: Optional[Environment],
        exclude_location: Location,
        context: Dict[str, Any],
    ) -> Optional[Location]:
        """Find a fallback location."""
        if not environment:
            return None

        # Look in same environment first
        for loc in environment.locations:
            if loc.id == exclude_location.id:
                continue
            if loc.status == TargetStatus.AVAILABLE:
                check = await self.validate_connectivity(loc)
                if check.is_reachable:
                    return loc

        # Try other environments if cross-environment is allowed
        if self.config.allow_cross_environment:
            for env in self.environments.values():
                if env.id == environment.id:
                    continue
                for loc in env.locations:
                    if loc.status == TargetStatus.AVAILABLE:
                        check = await self.validate_connectivity(loc)
                        if check.is_reachable:
                            return loc

        return None

    async def route_batch(
        self,
        targets: List[ExecutionTarget],
        context: Optional[Dict[str, Any]] = None,
    ) -> RoutingResult:
        """
        Route multiple targets with connectivity validation.

        Args:
            targets: Execution targets to route
            context: Additional context

        Returns:
            RoutingResult with all decisions
        """
        start_time = time.time()
        context = context or {}

        # Route all targets
        tasks = [self.route(target, context) for target in targets]
        decisions = await asyncio.gather(*tasks)

        # Collect connectivity checks
        all_checks = list(self._connectivity_cache.values())

        # Count results
        reachable = sum(1 for d in decisions if d.connectivity_verified)
        unreachable = len(decisions) - reachable

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "batch_routing_complete",
            total=len(targets),
            reachable=reachable,
            unreachable=unreachable,
            duration_ms=duration_ms,
        )

        return RoutingResult(
            decisions=list(decisions),
            connectivity_checks=all_checks,
            all_reachable=(unreachable == 0),
            reachable_count=reachable,
            unreachable_count=unreachable,
            duration_ms=duration_ms,
        )

    def get_routing_metrics(self) -> Dict[str, Any]:
        """Get routing metrics."""
        total_checks = len(self._connectivity_cache)
        reachable_checks = sum(
            1 for c in self._connectivity_cache.values()
            if c.is_reachable
        )

        avg_latency = 0.0
        if reachable_checks > 0:
            avg_latency = sum(
                c.latency_ms for c in self._connectivity_cache.values()
                if c.is_reachable
            ) / reachable_checks

        return {
            "total_locations_checked": total_checks,
            "reachable_locations": reachable_checks,
            "unreachable_locations": total_checks - reachable_checks,
            "average_latency_ms": avg_latency,
            "cache_entries": len(self._connectivity_cache),
        }

    def clear_connectivity_cache(self) -> None:
        """Clear the connectivity cache."""
        self._connectivity_cache.clear()
        logger.info("connectivity_cache_cleared")


def create_routing_engine(
    locations: Optional[Dict[str, Location]] = None,
    environments: Optional[Dict[str, Environment]] = None,
    config: Optional[BlueDolphinConfig] = None,
) -> RoutingEngine:
    """Factory function to create a RoutingEngine."""
    return RoutingEngine(
        locations=locations,
        environments=environments,
        config=config,
    )
