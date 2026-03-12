"""
YELLOW HONEYBEE - Validation Builder.

Builds pre/post conditions for implementation specifications.
This implements Criterion 2: Validation rules for each step.

Every specification gets:
- Pre-conditions that must be true before execution
- Post-conditions that must be true after execution
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import structlog

from .models import (
    SpecificationType,
    ResourceType,
    TaskSpecification,
    ValidationRule,
    PreCondition,
    PostCondition,
    ValidationStatus,
    Resource,
)

logger = structlog.get_logger(__name__)


# Pre-condition templates by specification type
PRE_CONDITION_TEMPLATES: Dict[SpecificationType, List[Dict[str, Any]]] = {
    SpecificationType.KUBERNETES: [
        {
            "name": "cluster_accessible",
            "description": "Kubernetes cluster is accessible",
            "check_type": "command",
            "check_expression": "kubectl cluster-info",
            "expected_value": 0,
            "comparison": "exit_code",
        },
        {
            "name": "namespace_exists",
            "description": "Target namespace exists",
            "check_type": "command",
            "check_expression": "kubectl get namespace {namespace}",
            "expected_value": 0,
            "comparison": "exit_code",
        },
        {
            "name": "resource_exists",
            "description": "Target resource exists",
            "check_type": "command",
            "check_expression": "kubectl get {resource_type} {resource_name} -n {namespace}",
            "expected_value": 0,
            "comparison": "exit_code",
        },
    ],
    SpecificationType.API_CALL: [
        {
            "name": "endpoint_reachable",
            "description": "API endpoint is reachable",
            "check_type": "api_call",
            "check_expression": "GET {health_endpoint}",
            "expected_value": 200,
            "comparison": "status_code",
        },
    ],
    SpecificationType.COMMAND: [
        {
            "name": "command_available",
            "description": "Required command is available",
            "check_type": "command",
            "check_expression": "which {command}",
            "expected_value": 0,
            "comparison": "exit_code",
        },
    ],
    SpecificationType.CONFIG_CHANGE: [
        {
            "name": "config_file_exists",
            "description": "Configuration file exists",
            "check_type": "command",
            "check_expression": "test -f {config_path}",
            "expected_value": 0,
            "comparison": "exit_code",
        },
        {
            "name": "config_writable",
            "description": "Configuration file is writable",
            "check_type": "command",
            "check_expression": "test -w {config_path}",
            "expected_value": 0,
            "comparison": "exit_code",
        },
    ],
    SpecificationType.DATABASE_QUERY: [
        {
            "name": "database_accessible",
            "description": "Database is accessible",
            "check_type": "query",
            "check_expression": "SELECT 1",
            "expected_value": 1,
            "comparison": "equals",
        },
    ],
}


# Post-condition templates by specification type
POST_CONDITION_TEMPLATES: Dict[SpecificationType, List[Dict[str, Any]]] = {
    SpecificationType.KUBERNETES: [
        {
            "name": "resource_ready",
            "description": "Resource is in ready state",
            "check_type": "command",
            "check_expression": "kubectl rollout status {resource_type}/{resource_name} -n {namespace}",
            "expected_value": 0,
            "comparison": "exit_code",
            "timeout_seconds": 300,
        },
        {
            "name": "pods_running",
            "description": "All pods are running",
            "check_type": "command",
            "check_expression": "kubectl get pods -l app={resource_name} -n {namespace} -o jsonpath='{.items[*].status.phase}'",
            "expected_value": "Running",
            "comparison": "contains",
        },
    ],
    SpecificationType.API_CALL: [
        {
            "name": "api_response_valid",
            "description": "API returned expected status",
            "check_type": "api_call",
            "check_expression": "GET {endpoint}",
            "expected_value": [200, 201, 202],
            "comparison": "in_list",
        },
    ],
    SpecificationType.COMMAND: [
        {
            "name": "command_succeeded",
            "description": "Command completed successfully",
            "check_type": "assertion",
            "check_expression": "exit_code",
            "expected_value": 0,
            "comparison": "equals",
        },
    ],
    SpecificationType.CONFIG_CHANGE: [
        {
            "name": "config_valid",
            "description": "Configuration is valid",
            "check_type": "command",
            "check_expression": "cat {config_path} | {validator}",
            "expected_value": 0,
            "comparison": "exit_code",
        },
        {
            "name": "service_reloaded",
            "description": "Service reloaded successfully",
            "check_type": "command",
            "check_expression": "{reload_command}",
            "expected_value": 0,
            "comparison": "exit_code",
        },
    ],
    SpecificationType.DATABASE_QUERY: [
        {
            "name": "query_succeeded",
            "description": "Query executed successfully",
            "check_type": "assertion",
            "check_expression": "affected_rows >= 0",
            "expected_value": True,
            "comparison": "equals",
        },
        {
            "name": "data_integrity",
            "description": "Data integrity maintained",
            "check_type": "query",
            "check_expression": "{integrity_check}",
            "expected_value": True,
            "comparison": "equals",
        },
    ],
}


# Health check templates by resource type
HEALTH_CHECK_TEMPLATES: Dict[ResourceType, Dict[str, Any]] = {
    ResourceType.SERVICE: {
        "check_type": "api_call",
        "check_expression": "GET http://{identifier}:{port}/health",
        "expected_value": 200,
        "comparison": "status_code",
        "timeout_seconds": 10,
        "retry_count": 3,
    },
    ResourceType.DATABASE: {
        "check_type": "query",
        "check_expression": "SELECT 1",
        "expected_value": 1,
        "comparison": "equals",
        "timeout_seconds": 5,
    },
    ResourceType.DEPLOYMENT: {
        "check_type": "command",
        "check_expression": "kubectl rollout status deployment/{identifier} -n {namespace}",
        "expected_value": 0,
        "comparison": "exit_code",
        "timeout_seconds": 300,
    },
    ResourceType.POD: {
        "check_type": "command",
        "check_expression": "kubectl get pod {identifier} -n {namespace} -o jsonpath='{.status.phase}'",
        "expected_value": "Running",
        "comparison": "equals",
        "timeout_seconds": 60,
    },
}


@dataclass
class ValidationResult:
    """Result of validation building."""
    pre_conditions: List[PreCondition] = field(default_factory=list)
    post_conditions: List[PostCondition] = field(default_factory=list)
    health_checks: List[ValidationRule] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_ms: int = 0


class ValidationBuilder:
    """
    Builds validation rules for specifications.

    This is critical for Criterion 2: Every step has validation rules.
    """

    def __init__(
        self,
        min_pre_conditions: int = 1,
        min_post_conditions: int = 1,
        default_timeout: int = 30,
    ):
        """
        Initialize the validation builder.

        Args:
            min_pre_conditions: Minimum pre-conditions per spec
            min_post_conditions: Minimum post-conditions per spec
            default_timeout: Default timeout for checks
        """
        self.min_pre_conditions = min_pre_conditions
        self.min_post_conditions = min_post_conditions
        self.default_timeout = default_timeout

        logger.info(
            "validation_builder_initialized",
            min_pre=min_pre_conditions,
            min_post=min_post_conditions,
        )

    def build_validations(
        self,
        spec: TaskSpecification,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        Build validation rules for a specification.

        Args:
            spec: The task specification
            context: Additional context

        Returns:
            ValidationResult with pre/post conditions
        """
        import time
        start_time = time.time()
        context = context or {}

        pre_conditions: List[PreCondition] = []
        post_conditions: List[PostCondition] = []
        health_checks: List[ValidationRule] = []
        warnings: List[str] = []

        # Build pre-conditions from templates
        pre_templates = PRE_CONDITION_TEMPLATES.get(spec.spec_type, [])
        for template in pre_templates:
            try:
                pre_condition = self._build_pre_condition(template, spec, context)
                pre_conditions.append(pre_condition)
            except Exception as e:
                warnings.append(f"Failed to build pre-condition {template['name']}: {e}")

        # Build post-conditions from templates
        post_templates = POST_CONDITION_TEMPLATES.get(spec.spec_type, [])
        for template in post_templates:
            try:
                post_condition = self._build_post_condition(template, spec, context)
                post_conditions.append(post_condition)
            except Exception as e:
                warnings.append(f"Failed to build post-condition {template['name']}: {e}")

        # Build health checks for resources
        for resource in spec.resources:
            try:
                health_check = self._build_health_check(resource, context)
                if health_check:
                    health_checks.append(health_check)
            except Exception as e:
                warnings.append(f"Failed to build health check for {resource.name}: {e}")

        # Ensure minimum conditions
        if len(pre_conditions) < self.min_pre_conditions:
            pre_conditions.append(self._create_default_pre_condition(spec))

        if len(post_conditions) < self.min_post_conditions:
            post_conditions.append(self._create_default_post_condition(spec))

        duration_ms = int((time.time() - start_time) * 1000)

        logger.debug(
            "validations_built",
            spec_id=spec.id,
            pre_conditions=len(pre_conditions),
            post_conditions=len(post_conditions),
            health_checks=len(health_checks),
            duration_ms=duration_ms,
        )

        return ValidationResult(
            pre_conditions=pre_conditions,
            post_conditions=post_conditions,
            health_checks=health_checks,
            warnings=warnings,
            duration_ms=duration_ms,
        )

    def _build_pre_condition(
        self,
        template: Dict[str, Any],
        spec: TaskSpecification,
        context: Dict[str, Any],
    ) -> PreCondition:
        """Build a pre-condition from template."""
        # Get substitution values
        subs = self._get_substitutions(spec, context)

        return PreCondition(
            name=template["name"],
            description=template["description"],
            check_type=template["check_type"],
            check_expression=template["check_expression"].format(**subs),
            expected_value=template.get("expected_value"),
            comparison=template.get("comparison", "equals"),
            timeout_seconds=template.get("timeout_seconds", self.default_timeout),
            retry_count=template.get("retry_count", 3),
            retry_delay_seconds=template.get("retry_delay_seconds", 5),
            is_blocking=template.get("is_blocking", True),
        )

    def _build_post_condition(
        self,
        template: Dict[str, Any],
        spec: TaskSpecification,
        context: Dict[str, Any],
    ) -> PostCondition:
        """Build a post-condition from template."""
        subs = self._get_substitutions(spec, context)

        return PostCondition(
            name=template["name"],
            description=template["description"],
            check_type=template["check_type"],
            check_expression=template["check_expression"].format(**subs),
            expected_value=template.get("expected_value"),
            comparison=template.get("comparison", "equals"),
            timeout_seconds=template.get("timeout_seconds", self.default_timeout),
            retry_count=template.get("retry_count", 3),
            retry_delay_seconds=template.get("retry_delay_seconds", 5),
            is_blocking=template.get("is_blocking", True),
        )

    def _build_health_check(
        self,
        resource: Resource,
        context: Dict[str, Any],
    ) -> Optional[ValidationRule]:
        """Build a health check for a resource."""
        template = HEALTH_CHECK_TEMPLATES.get(resource.type)
        if not template:
            return None

        subs = {
            "identifier": resource.identifier,
            "name": resource.name,
            "namespace": resource.namespace or "default",
            "port": resource.port or 8080,
            "endpoint": resource.endpoint or f"http://{resource.identifier}",
        }

        return ValidationRule(
            name=f"health_check_{resource.name}",
            description=f"Health check for {resource.name}",
            check_type=template["check_type"],
            check_expression=template["check_expression"].format(**subs),
            expected_value=template.get("expected_value"),
            comparison=template.get("comparison", "equals"),
            timeout_seconds=template.get("timeout_seconds", self.default_timeout),
            retry_count=template.get("retry_count", 3),
            is_blocking=False,  # Health checks are not blocking by default
        )

    def _get_substitutions(
        self,
        spec: TaskSpecification,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Get substitution values for templates."""
        subs: Dict[str, Any] = {
            "spec_id": spec.id,
            "action_title": spec.action_title,
            "namespace": "default",
            "resource_type": "deployment",
            "resource_name": "unknown",
            "command": "kubectl",
            "config_path": "/etc/config/app.yaml",
            "validator": "yamllint -",
            "reload_command": "systemctl reload app",
            "health_endpoint": "http://localhost:8080/health",
            "endpoint": "http://localhost:8080",
            "integrity_check": "SELECT COUNT(*) FROM health_checks",
            "port": 8080,
        }

        # Override from Kubernetes spec
        if spec.kubernetes_spec:
            subs["namespace"] = spec.kubernetes_spec.namespace
            subs["resource_type"] = spec.kubernetes_spec.resource_type
            subs["resource_name"] = spec.kubernetes_spec.resource_name

        # Override from API spec
        if spec.api_spec:
            subs["endpoint"] = spec.api_spec.url
            subs["health_endpoint"] = spec.api_spec.url.replace("/api", "/health")

        # Override from Command spec
        if spec.command_spec:
            subs["command"] = spec.command_spec.command

        # Override from Config spec
        if spec.config_spec:
            subs["config_path"] = spec.config_spec.config_path
            if spec.config_spec.reload_command:
                subs["reload_command"] = spec.config_spec.reload_command

        # Override from resources
        if spec.resources:
            first_resource = spec.resources[0]
            subs["resource_name"] = first_resource.name
            if first_resource.namespace:
                subs["namespace"] = first_resource.namespace
            if first_resource.port:
                subs["port"] = first_resource.port

        # Override from context
        subs.update(context)

        return subs

    def _create_default_pre_condition(
        self,
        spec: TaskSpecification,
    ) -> PreCondition:
        """Create a default pre-condition."""
        return PreCondition(
            name="system_ready",
            description="System is ready for operation",
            check_type="assertion",
            check_expression="system.status == 'ready'",
            expected_value=True,
            comparison="equals",
            timeout_seconds=self.default_timeout,
            is_blocking=True,
        )

    def _create_default_post_condition(
        self,
        spec: TaskSpecification,
    ) -> PostCondition:
        """Create a default post-condition."""
        return PostCondition(
            name="operation_complete",
            description="Operation completed without errors",
            check_type="assertion",
            check_expression="operation.status == 'complete'",
            expected_value=True,
            comparison="equals",
            timeout_seconds=self.default_timeout,
            is_blocking=True,
        )

    def build_for_plan(
        self,
        specifications: List[TaskSpecification],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, ValidationResult]:
        """
        Build validations for all specifications in a plan.

        Args:
            specifications: List of specifications
            context: Additional context

        Returns:
            Dict mapping spec ID to ValidationResult
        """
        results: Dict[str, ValidationResult] = {}
        context = context or {}

        for spec in specifications:
            results[spec.id] = self.build_validations(spec, context)

        logger.info(
            "plan_validations_built",
            spec_count=len(specifications),
            total_pre=sum(len(r.pre_conditions) for r in results.values()),
            total_post=sum(len(r.post_conditions) for r in results.values()),
        )

        return results

    def validate_coverage(
        self,
        specifications: List[TaskSpecification],
    ) -> tuple[bool, List[str]]:
        """
        Validate that all specs have adequate validation coverage.

        Args:
            specifications: List of specifications

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues: List[str] = []

        for spec in specifications:
            if len(spec.pre_conditions) < self.min_pre_conditions:
                issues.append(
                    f"Spec {spec.id} has {len(spec.pre_conditions)} pre-conditions, "
                    f"minimum is {self.min_pre_conditions}"
                )

            if len(spec.post_conditions) < self.min_post_conditions:
                issues.append(
                    f"Spec {spec.id} has {len(spec.post_conditions)} post-conditions, "
                    f"minimum is {self.min_post_conditions}"
                )

            # Check for blocking conditions
            has_blocking_pre = any(c.is_blocking for c in spec.pre_conditions)
            has_blocking_post = any(c.is_blocking for c in spec.post_conditions)

            if not has_blocking_pre and not has_blocking_post:
                issues.append(
                    f"Spec {spec.id} has no blocking validation rules"
                )

        return len(issues) == 0, issues


def create_validation_builder(
    min_pre_conditions: int = 1,
    min_post_conditions: int = 1,
    default_timeout: int = 30,
) -> ValidationBuilder:
    """Factory function to create a ValidationBuilder."""
    return ValidationBuilder(
        min_pre_conditions=min_pre_conditions,
        min_post_conditions=min_post_conditions,
        default_timeout=default_timeout,
    )
