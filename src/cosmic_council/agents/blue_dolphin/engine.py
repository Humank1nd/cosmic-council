"""
BLUE DOLPHIN - Location Engine.

Main orchestrator for the Blue Dolphin Location Agent.
Coordinates location resolution, environment matching, and routing validation.

Three Falsifiable Criteria:
1. Location resolution - every action has a specific execution target
2. Environment matching - actions matched to appropriate environments
3. Connectivity validation - all targets are reachable
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

import structlog

from .models import (
    Location,
    Environment,
    EnvironmentType,
    ExecutionTarget,
    LocationPlan,
    RoutingRule,
    BlueDolphinConfig,
    STANDARD_LOCATIONS,
    STANDARD_ENVIRONMENTS,
)
from .location_resolver import (
    LocationResolver,
    ResolutionResult,
    create_location_resolver,
)
from .environment_analyzer import (
    EnvironmentAnalyzer,
    EnvironmentAnalysisResult,
    create_environment_analyzer,
)
from .routing_engine import (
    RoutingEngine,
    RoutingResult,
    RoutingDecision,
    create_routing_engine,
)

logger = structlog.get_logger(__name__)


@dataclass
class BlueDolphinResult:
    """Result of Blue Dolphin location processing."""
    location_plan: LocationPlan = field(default_factory=LocationPlan)
    success: bool = False
    duration_ms: int = 0

    # Criterion metrics
    location_resolution: float = 0.0  # % of actions with resolved locations
    environment_matching: float = 0.0  # % of actions matched to environments
    connectivity_validation: float = 0.0  # % of targets that are reachable

    # Details
    resolution_results: List[ResolutionResult] = field(default_factory=list)
    environment_results: List[EnvironmentAnalysisResult] = field(default_factory=list)
    routing_result: Optional[RoutingResult] = None

    reasoning: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class BlueDolphinEngine:
    """
    Main engine for Blue Dolphin location agent.

    Orchestrates the three criteria:
    1. Location resolution (LocationResolver)
    2. Environment matching (EnvironmentAnalyzer)
    3. Connectivity validation (RoutingEngine)
    """

    def __init__(
        self,
        config: Optional[BlueDolphinConfig] = None,
        locations: Optional[Dict[str, Location]] = None,
        environments: Optional[Dict[str, Environment]] = None,
        routing_rules: Optional[List[RoutingRule]] = None,
        llm_provider: Optional[Any] = None,
    ):
        """
        Initialize the Blue Dolphin engine.

        Args:
            config: Configuration
            locations: Available locations
            environments: Available environments
            routing_rules: Routing rules
            llm_provider: Optional LLM for intelligent routing
        """
        self.config = config or BlueDolphinConfig()
        self.locations = locations or STANDARD_LOCATIONS
        self.environments = environments or STANDARD_ENVIRONMENTS
        self.llm_provider = llm_provider

        # Initialize components
        self.location_resolver = create_location_resolver(
            locations=self.locations,
            environments=self.environments,
            routing_rules=routing_rules,
            default_environment=self.config.default_environment,
        )

        self.environment_analyzer = create_environment_analyzer(
            environments=self.environments,
            config=self.config,
        )

        self.routing_engine = create_routing_engine(
            locations=self.locations,
            environments=self.environments,
            config=self.config,
        )

        # Metrics
        self._plans_created = 0
        self._total_targets_resolved = 0
        self._total_targets_reachable = 0

        logger.info(
            "blue_dolphin_engine_initialized",
            location_count=len(self.locations),
            environment_count=len(self.environments),
            has_llm=llm_provider is not None,
        )

    async def locate(
        self,
        schedule_id: str,
        slots: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> BlueDolphinResult:
        """
        Determine execution locations for scheduled slots.

        This is the main entry point that coordinates all three criteria.

        Args:
            schedule_id: ID of the schedule from Green Turtle
            slots: Scheduled execution slots
            context: Additional context

        Returns:
            BlueDolphinResult with location plan
        """
        start_time = time.time()
        context = context or {}

        reasoning: List[str] = []
        warnings: List[str] = []

        # Create location plan
        plan = LocationPlan(
            schedule_id=schedule_id,
        )

        reasoning.append(f"Processing {len(slots)} scheduled slots")

        # ====================================================================
        # CRITERION 1: Location Resolution
        # ====================================================================
        resolution_results: List[ResolutionResult] = []
        targets: List[ExecutionTarget] = []

        for slot in slots:
            # First analyze environment to inform location resolution
            env_result = self.environment_analyzer.analyze(
                action_id=slot.get("action_id", ""),
                category=slot.get("category", ""),
                risk_level=slot.get("risk_level", "MEDIUM"),
                context=context,
            )

            # Resolve location
            result = self.location_resolver.resolve(
                action_id=slot.get("action_id", ""),
                spec_id=slot.get("spec_id", ""),
                slot_id=slot.get("id", slot.get("slot_id", "")),
                category=slot.get("category", ""),
                risk_level=slot.get("risk_level", "MEDIUM"),
                spec_type=slot.get("spec_type", ""),
                context={
                    **context,
                    "recommended_environment": env_result.recommended_environment,
                },
            )

            resolution_results.append(result)
            targets.append(result.target)
            warnings.extend(result.warnings)

        # Calculate resolution rate
        resolved_count = sum(1 for r in resolution_results if r.success)
        resolution_rate = resolved_count / len(slots) if slots else 0.0

        plan.targets = targets
        plan.targets_resolved = resolved_count
        plan.targets_unresolved = len(slots) - resolved_count

        reasoning.append(
            f"Location resolution: {resolved_count}/{len(slots)} ({resolution_rate:.0%})"
        )

        # ====================================================================
        # CRITERION 2: Environment Matching
        # ====================================================================
        environment_results = self.environment_analyzer.analyze_batch(
            slots, context
        )

        matched_count = sum(1 for r in environment_results if r.success)
        matching_rate = matched_count / len(slots) if slots else 0.0

        # Collect unique environments
        unique_envs = set()
        for result in environment_results:
            if result.recommended_environment:
                unique_envs.add(result.recommended_environment.id)
                if result.recommended_environment not in plan.environments:
                    plan.environments.append(result.recommended_environment)

        reasoning.append(
            f"Environment matching: {matched_count}/{len(slots)} ({matching_rate:.0%})"
        )
        reasoning.append(f"Using {len(unique_envs)} unique environments")

        # ====================================================================
        # CRITERION 3: Connectivity Validation
        # ====================================================================
        routing_result = await self.routing_engine.route_batch(targets, context)

        plan.targets_reachable = routing_result.reachable_count
        plan.targets_unreachable = routing_result.unreachable_count

        connectivity_rate = (
            routing_result.reachable_count / len(targets) if targets else 0.0
        )

        reasoning.append(
            f"Connectivity validation: {routing_result.reachable_count}/{len(targets)} ({connectivity_rate:.0%})"
        )

        if routing_result.unreachable_count > 0:
            warnings.append(
                f"{routing_result.unreachable_count} targets are unreachable"
            )

        # ====================================================================
        # Collect locations and finalize plan
        # ====================================================================
        unique_locations = set()
        for target in targets:
            if target.location:
                unique_locations.add(target.location.id)
                if target.location not in plan.locations:
                    plan.locations.append(target.location)

        # Determine plan validity
        plan.is_valid = (
            resolution_rate >= 0.8 and
            matching_rate >= 0.8 and
            connectivity_rate >= 0.8
        )

        if not plan.is_valid:
            if resolution_rate < 0.8:
                plan.validation_errors.append(
                    f"Location resolution too low: {resolution_rate:.0%}"
                )
            if matching_rate < 0.8:
                plan.validation_errors.append(
                    f"Environment matching too low: {matching_rate:.0%}"
                )
            if connectivity_rate < 0.8:
                plan.validation_errors.append(
                    f"Connectivity validation too low: {connectivity_rate:.0%}"
                )

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Update metrics
        self._plans_created += 1
        self._total_targets_resolved += resolved_count
        self._total_targets_reachable += routing_result.reachable_count

        logger.info(
            "location_plan_created",
            schedule_id=schedule_id,
            targets=len(targets),
            resolved=resolved_count,
            matched=matched_count,
            reachable=routing_result.reachable_count,
            is_valid=plan.is_valid,
            duration_ms=duration_ms,
        )

        return BlueDolphinResult(
            location_plan=plan,
            success=plan.is_valid,
            duration_ms=duration_ms,
            location_resolution=resolution_rate,
            environment_matching=matching_rate,
            connectivity_validation=connectivity_rate,
            resolution_results=resolution_results,
            environment_results=environment_results,
            routing_result=routing_result,
            reasoning=reasoning,
            warnings=warnings,
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get engine metrics."""
        routing_metrics = self.routing_engine.get_routing_metrics()
        env_status = self.environment_analyzer.get_environment_status()

        return {
            "plans_created": self._plans_created,
            "total_targets_resolved": self._total_targets_resolved,
            "total_targets_reachable": self._total_targets_reachable,
            "location_count": len(self.locations),
            "environment_count": len(self.environments),
            "routing": routing_metrics,
            "environments": env_status,
        }


# Singleton instance
_blue_dolphin_engine: Optional[BlueDolphinEngine] = None


def create_blue_dolphin(
    config: Optional[BlueDolphinConfig] = None,
    locations: Optional[Dict[str, Location]] = None,
    environments: Optional[Dict[str, Environment]] = None,
    routing_rules: Optional[List[RoutingRule]] = None,
    llm_provider: Optional[Any] = None,
) -> BlueDolphinEngine:
    """Factory function to create a BlueDolphinEngine."""
    return BlueDolphinEngine(
        config=config,
        locations=locations,
        environments=environments,
        routing_rules=routing_rules,
        llm_provider=llm_provider,
    )


def get_blue_dolphin() -> BlueDolphinEngine:
    """Get the default Blue Dolphin engine instance."""
    global _blue_dolphin_engine
    if _blue_dolphin_engine is None:
        _blue_dolphin_engine = create_blue_dolphin()
    return _blue_dolphin_engine


async def locate_execution(
    schedule_id: str,
    slots: List[Dict[str, Any]],
    context: Optional[Dict[str, Any]] = None,
) -> BlueDolphinResult:
    """
    Convenience function to locate execution targets.

    Args:
        schedule_id: Schedule ID from Green Turtle
        slots: Scheduled slots to locate
        context: Additional context

    Returns:
        BlueDolphinResult with location plan
    """
    engine = get_blue_dolphin()
    return await engine.locate(schedule_id, slots, context)
