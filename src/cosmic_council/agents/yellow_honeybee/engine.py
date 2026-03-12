"""
YELLOW HONEYBEE - Implementation Planning Engine.

Main engine that orchestrates:
- Specification generation (Criterion 1)
- Validation building (Criterion 2)
- Resource identification (Criterion 3)

Takes action plans from Orange Orangutan and produces
detailed implementation specifications.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import structlog

from .models import (
    TaskSpecification,
    ImplementationPlan,
    YellowHoneybeeConfig,
)
from .specification_generator import (
    SpecificationGenerator,
    create_specification_generator,
)
from .resource_identifier import (
    ResourceIdentifier,
    create_resource_identifier,
)
from .validation_builder import (
    ValidationBuilder,
    create_validation_builder,
)

logger = structlog.get_logger(__name__)


@dataclass
class YellowHoneybeeResult:
    """Result of Yellow Honeybee implementation planning."""
    success: bool
    plan: ImplementationPlan
    reasoning: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None
    duration_ms: int = 0

    # Criterion metrics
    specification_completeness: float = 0.0
    validation_coverage: float = 0.0
    resource_identification: float = 0.0


class YellowHoneybeeEngine:
    """
    Yellow Honeybee Implementation Planning Engine.

    Answers the WHAT question: What exactly needs to be done?

    Three Falsifiable Criteria:
    1. Specification completeness - every action gets detailed specs
    2. Validation rules - pre/post conditions for each step
    3. Resource identification - specific resources identified
    """

    def __init__(
        self,
        config: Optional[YellowHoneybeeConfig] = None,
        llm_provider: Optional[Any] = None,
        default_namespace: str = "default",
        service_registry: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """
        Initialize the Yellow Honeybee engine.

        Args:
            config: Engine configuration
            llm_provider: Optional LLM provider for intelligent specification
            default_namespace: Default Kubernetes namespace
            service_registry: Optional service registry for resource discovery
        """
        self.config = config or YellowHoneybeeConfig()
        self.llm_provider = llm_provider

        # Initialize components
        self.spec_generator = create_specification_generator(
            default_namespace=default_namespace,
            default_timeout=self.config.default_timeout_seconds,
        )
        self.resource_identifier = create_resource_identifier(
            default_namespace=default_namespace,
            service_registry=service_registry,
        )
        self.validation_builder = create_validation_builder(
            min_pre_conditions=self.config.min_pre_conditions_per_action,
            min_post_conditions=self.config.min_post_conditions_per_action,
        )

        logger.info(
            "yellow_honeybee_engine_initialized",
            has_llm=llm_provider is not None,
            require_complete_specs=self.config.require_complete_specs,
        )

    async def specify(
        self,
        action_plan_id: str,
        actions: List[Dict[str, Any]],
        root_cause: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> YellowHoneybeeResult:
        """
        Generate implementation specifications for an action plan.

        Args:
            action_plan_id: ID of the source action plan
            actions: List of actions from Orange Orangutan
            root_cause: Original root cause
            context: Additional context

        Returns:
            YellowHoneybeeResult with implementation plan
        """
        start_time = time.time()
        context = context or {}
        reasoning: List[str] = []
        warnings: List[str] = []

        try:
            reasoning.append(f"Processing {len(actions)} actions from plan {action_plan_id}")

            # Step 1: Generate specifications (Criterion 1)
            spec_result = self.spec_generator.generate_for_plan(actions, context)
            specifications = spec_result.specifications
            warnings.extend(spec_result.warnings)

            reasoning.append(
                f"Generated {len(specifications)} specifications "
                f"({spec_result.complete_count} complete, {spec_result.incomplete_count} incomplete)"
            )

            # Step 2: Identify resources (Criterion 3)
            for spec in specifications:
                resources = self.resource_identifier.identify_resources(spec, context)
                spec.resources = resources

            resource_result = self.resource_identifier.discover_for_plan(specifications, context)
            warnings.extend(resource_result.warnings)

            reasoning.append(
                f"Identified {len(resource_result.resources)} resources: "
                f"{len(resource_result.services)} services, "
                f"{len(resource_result.databases)} databases"
            )

            # Step 3: Build validations (Criterion 2)
            for spec in specifications:
                validation_result = self.validation_builder.build_validations(spec, context)
                spec.pre_conditions = validation_result.pre_conditions
                spec.post_conditions = validation_result.post_conditions
                warnings.extend(validation_result.warnings)

            total_pre = sum(len(s.pre_conditions) for s in specifications)
            total_post = sum(len(s.post_conditions) for s in specifications)
            reasoning.append(
                f"Built {total_pre} pre-conditions and {total_post} post-conditions"
            )

            # Step 4: Create execution order
            execution_order = [spec.id for spec in specifications]

            # Step 5: Build implementation plan
            plan = ImplementationPlan(
                action_plan_id=action_plan_id,
                root_cause=root_cause,
                specifications=specifications,
                execution_order=execution_order,
                all_resources=resource_result.resources,
                resource_dependencies=self.resource_identifier.build_dependency_graph(
                    resource_result.resources
                ),
            )

            # Step 6: Validate the plan
            is_valid, issues = self._validate_plan(plan)
            if not is_valid:
                warnings.extend(issues)
                if self.config.require_complete_specs:
                    reasoning.append(f"Plan has {len(issues)} validation issues")

            # Calculate criterion metrics
            spec_completeness = plan.completeness_ratio
            validation_coverage = self._calculate_validation_coverage(plan)
            resource_identification = self._calculate_resource_coverage(plan)

            reasoning.append(
                f"Criterion metrics: "
                f"specs={spec_completeness:.1%}, "
                f"validation={validation_coverage:.1%}, "
                f"resources={resource_identification:.1%}"
            )

            duration_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "yellow_honeybee_planning_complete",
                plan_id=plan.id,
                spec_count=len(specifications),
                resource_count=len(resource_result.resources),
                duration_ms=duration_ms,
            )

            return YellowHoneybeeResult(
                success=True,
                plan=plan,
                reasoning=reasoning,
                warnings=warnings,
                duration_ms=duration_ms,
                specification_completeness=spec_completeness,
                validation_coverage=validation_coverage,
                resource_identification=resource_identification,
            )

        except Exception as e:
            logger.error(
                "yellow_honeybee_planning_failed",
                error=str(e),
            )
            return YellowHoneybeeResult(
                success=False,
                plan=ImplementationPlan(),
                reasoning=reasoning,
                warnings=warnings,
                error=str(e),
                duration_ms=int((time.time() - start_time) * 1000),
            )

    async def quick_specify(
        self,
        actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Quick specification returning just the essentials.

        Args:
            actions: List of actions to specify
            context: Additional context

        Returns:
            Dict with essential specification info
        """
        result = await self.specify(
            action_plan_id="quick",
            actions=actions,
            context=context,
        )

        return {
            "success": result.success,
            "spec_count": len(result.plan.specifications),
            "completeness": result.specification_completeness,
            "validation_coverage": result.validation_coverage,
            "resource_count": len(result.plan.all_resources),
            "duration_ms": result.duration_ms,
        }

    def _validate_plan(
        self,
        plan: ImplementationPlan,
    ) -> tuple[bool, List[str]]:
        """Validate the implementation plan."""
        issues: List[str] = []

        # Check specification completeness
        for spec in plan.specifications:
            if not spec.is_complete:
                issues.append(f"Spec {spec.id} is incomplete")

            if not spec.has_validation:
                issues.append(f"Spec {spec.id} has no validation rules")

            if not spec.resources:
                issues.append(f"Spec {spec.id} has no resources identified")

        # Check for orphaned resources
        spec_resource_ids = set()
        for spec in plan.specifications:
            for resource in spec.resources:
                spec_resource_ids.add(resource.id)

        for resource in plan.all_resources:
            if resource.id not in spec_resource_ids:
                issues.append(f"Resource {resource.name} is not used by any spec")

        return len(issues) == 0, issues

    def _calculate_validation_coverage(
        self,
        plan: ImplementationPlan,
    ) -> float:
        """Calculate validation coverage ratio."""
        if not plan.specifications:
            return 0.0

        specs_with_validation = sum(
            1 for s in plan.specifications
            if s.pre_conditions or s.post_conditions
        )
        return specs_with_validation / len(plan.specifications)

    def _calculate_resource_coverage(
        self,
        plan: ImplementationPlan,
    ) -> float:
        """Calculate resource identification coverage."""
        if not plan.specifications:
            return 0.0

        specs_with_resources = sum(
            1 for s in plan.specifications
            if s.resources
        )
        return specs_with_resources / len(plan.specifications)

    def get_metrics(self) -> Dict[str, Any]:
        """Get engine metrics and capabilities."""
        return {
            "config": {
                "require_complete_specs": self.config.require_complete_specs,
                "require_validation_rules": self.config.require_validation_rules,
                "require_resource_identification": self.config.require_resource_identification,
                "min_pre_conditions": self.config.min_pre_conditions_per_action,
                "min_post_conditions": self.config.min_post_conditions_per_action,
            },
            "capabilities": {
                "has_llm": self.llm_provider is not None,
                "auto_discover_resources": self.config.auto_discover_resources,
                "enable_dry_run": self.config.enable_dry_run,
            },
        }


# Singleton instance
_engine: Optional[YellowHoneybeeEngine] = None


def create_yellow_honeybee(
    config: Optional[YellowHoneybeeConfig] = None,
    llm_provider: Optional[Any] = None,
    default_namespace: str = "default",
    service_registry: Optional[Dict[str, Dict[str, Any]]] = None,
) -> YellowHoneybeeEngine:
    """Create a Yellow Honeybee engine instance."""
    return YellowHoneybeeEngine(
        config=config,
        llm_provider=llm_provider,
        default_namespace=default_namespace,
        service_registry=service_registry,
    )


def get_yellow_honeybee() -> YellowHoneybeeEngine:
    """Get the default Yellow Honeybee engine instance."""
    global _engine
    if _engine is None:
        _engine = create_yellow_honeybee()
    return _engine


async def specify_implementation(
    actions: List[Dict[str, Any]],
    action_plan_id: str = "",
    root_cause: str = "",
    context: Optional[Dict[str, Any]] = None,
) -> YellowHoneybeeResult:
    """
    Convenience function for quick implementation specification.

    Args:
        actions: List of actions from Orange Orangutan
        action_plan_id: Source action plan ID
        root_cause: Original root cause
        context: Additional context

    Returns:
        YellowHoneybeeResult with implementation plan
    """
    engine = get_yellow_honeybee()
    return await engine.specify(
        action_plan_id=action_plan_id,
        actions=actions,
        root_cause=root_cause,
        context=context,
    )
