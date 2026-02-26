"""
YELLOW HONEYBEE - Specification Generator.

Generates detailed implementation specifications from action steps.
This implements Criterion 1: Specification completeness.

Every action from Orange Orangutan gets a detailed specification
with exact commands, API calls, or configuration changes.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import structlog

from .models import (
    SpecificationType,
    ResourceType,
    TaskSpecification,
    CommandSpec,
    ApiCallSpec,
    ConfigChangeSpec,
    DatabaseQuerySpec,
    KubernetesSpec,
    Resource,
)

logger = structlog.get_logger(__name__)


# Specification templates by action category
SPEC_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "configuration": {
        "spec_type": SpecificationType.CONFIG_CHANGE,
        "template": {
            "config_format": "yaml",
            "backup_before": True,
            "validate_after": True,
        },
        "steps": [
            "Backup current configuration",
            "Apply configuration changes",
            "Validate new configuration",
            "Reload service if needed",
        ],
    },
    "deployment": {
        "spec_type": SpecificationType.KUBERNETES,
        "template": {
            "action": "apply",
            "wait_for_ready": True,
            "timeout_seconds": 300,
        },
        "steps": [
            "Verify current deployment state",
            "Apply deployment changes",
            "Wait for rollout completion",
            "Verify pod health",
        ],
    },
    "scaling": {
        "spec_type": SpecificationType.KUBERNETES,
        "template": {
            "action": "patch",
            "resource_type": "deployment",
            "wait_for_ready": True,
        },
        "steps": [
            "Check current replica count",
            "Apply scaling changes",
            "Wait for new pods to be ready",
            "Verify load distribution",
        ],
    },
    "restart": {
        "spec_type": SpecificationType.KUBERNETES,
        "template": {
            "action": "rollout",
            "wait_for_ready": True,
        },
        "steps": [
            "Initiate rolling restart",
            "Wait for pods to cycle",
            "Verify service health",
        ],
    },
    "database": {
        "spec_type": SpecificationType.DATABASE_QUERY,
        "template": {
            "transaction": True,
            "timeout_seconds": 60,
        },
        "steps": [
            "Create database backup",
            "Execute database operation",
            "Verify data integrity",
            "Update connection pool if needed",
        ],
    },
    "network": {
        "spec_type": SpecificationType.COMMAND,
        "template": {
            "shell": "bash",
            "capture_output": True,
        },
        "steps": [
            "Backup network configuration",
            "Apply network changes",
            "Verify connectivity",
            "Update DNS if needed",
        ],
    },
    "security": {
        "spec_type": SpecificationType.COMMAND,
        "template": {
            "shell": "bash",
            "capture_output": True,
        },
        "steps": [
            "Backup current security state",
            "Apply security changes",
            "Verify access controls",
            "Rotate credentials if needed",
        ],
    },
    "monitoring": {
        "spec_type": SpecificationType.API_CALL,
        "template": {
            "method": "PUT",
            "timeout_seconds": 30,
        },
        "steps": [
            "Get current alert configuration",
            "Update monitoring rules",
            "Verify alerts are active",
        ],
    },
    "investigation": {
        "spec_type": SpecificationType.COMMAND,
        "template": {
            "shell": "bash",
            "capture_output": True,
        },
        "steps": [
            "Gather diagnostic information",
            "Analyze collected data",
            "Document findings",
        ],
    },
    "communication": {
        "spec_type": SpecificationType.API_CALL,
        "template": {
            "method": "POST",
            "timeout_seconds": 30,
        },
        "steps": [
            "Compose notification message",
            "Send to notification channels",
            "Verify delivery",
        ],
    },
}


# Command patterns for common operations
COMMAND_PATTERNS: Dict[str, CommandSpec] = {
    "restart_service": CommandSpec(
        command="kubectl",
        args=["rollout", "restart", "deployment/{service}"],
        timeout_seconds=300,
        expected_exit_code=0,
    ),
    "scale_deployment": CommandSpec(
        command="kubectl",
        args=["scale", "deployment/{service}", "--replicas={replicas}"],
        timeout_seconds=120,
        expected_exit_code=0,
    ),
    "apply_config": CommandSpec(
        command="kubectl",
        args=["apply", "-f", "{config_file}"],
        timeout_seconds=60,
        expected_exit_code=0,
    ),
    "check_logs": CommandSpec(
        command="kubectl",
        args=["logs", "deployment/{service}", "--tail=100"],
        timeout_seconds=30,
        expected_exit_code=0,
    ),
    "describe_pod": CommandSpec(
        command="kubectl",
        args=["describe", "pod", "-l", "app={service}"],
        timeout_seconds=30,
        expected_exit_code=0,
    ),
}


# API call patterns for common operations
API_PATTERNS: Dict[str, ApiCallSpec] = {
    "health_check": ApiCallSpec(
        method="GET",
        url="http://{service}:{port}/health",
        timeout_seconds=10,
        expected_status_codes=[200],
        retry_count=3,
    ),
    "metrics_endpoint": ApiCallSpec(
        method="GET",
        url="http://{service}:{port}/metrics",
        timeout_seconds=10,
        expected_status_codes=[200],
    ),
    "config_reload": ApiCallSpec(
        method="POST",
        url="http://{service}:{port}/admin/reload",
        timeout_seconds=30,
        expected_status_codes=[200, 202],
    ),
    "send_alert": ApiCallSpec(
        method="POST",
        url="{alertmanager_url}/api/v1/alerts",
        timeout_seconds=10,
        expected_status_codes=[200],
    ),
}


@dataclass
class SpecificationResult:
    """Result of specification generation."""
    specifications: List[TaskSpecification] = field(default_factory=list)
    complete_count: int = 0
    incomplete_count: int = 0
    warnings: List[str] = field(default_factory=list)
    duration_ms: int = 0


class SpecificationGenerator:
    """
    Generates detailed implementation specifications.

    This is critical for Criterion 1: Every action gets complete specs.
    """

    def __init__(
        self,
        default_namespace: str = "default",
        default_timeout: int = 300,
    ):
        """
        Initialize the specification generator.

        Args:
            default_namespace: Default Kubernetes namespace
            default_timeout: Default timeout in seconds
        """
        self.default_namespace = default_namespace
        self.default_timeout = default_timeout
        logger.info(
            "specification_generator_initialized",
            default_namespace=default_namespace,
            default_timeout=default_timeout,
        )

    def generate_specification(
        self,
        action_id: str,
        action_title: str,
        category: str,
        target_service: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> TaskSpecification:
        """
        Generate a specification for a single action.

        Args:
            action_id: Unique action identifier
            action_title: Human-readable action title
            category: Action category (from Orange Orangutan)
            target_service: Target service name
            context: Additional context

        Returns:
            TaskSpecification for the action
        """
        context = context or {}

        # Get template for category
        template = SPEC_TEMPLATES.get(
            category.lower(),
            SPEC_TEMPLATES.get("investigation")  # Default
        )

        spec = TaskSpecification(
            action_id=action_id,
            action_title=action_title,
            spec_type=template["spec_type"],
            description=f"Implementation specification for: {action_title}",
            steps=list(template["steps"]),
            estimated_duration_seconds=self.default_timeout,
        )

        # Generate the appropriate spec based on type
        if template["spec_type"] == SpecificationType.KUBERNETES:
            spec.kubernetes_spec = self._generate_kubernetes_spec(
                action_title, target_service, template, context
            )
        elif template["spec_type"] == SpecificationType.COMMAND:
            spec.command_spec = self._generate_command_spec(
                action_title, target_service, template, context
            )
        elif template["spec_type"] == SpecificationType.API_CALL:
            spec.api_spec = self._generate_api_spec(
                action_title, target_service, template, context
            )
        elif template["spec_type"] == SpecificationType.CONFIG_CHANGE:
            spec.config_spec = self._generate_config_spec(
                action_title, target_service, template, context
            )
        elif template["spec_type"] == SpecificationType.DATABASE_QUERY:
            spec.database_spec = self._generate_database_spec(
                action_title, target_service, template, context
            )

        # Add target service as a resource
        if target_service:
            spec.resources.append(
                Resource(
                    name=target_service,
                    type=ResourceType.SERVICE,
                    identifier=target_service,
                    namespace=self.default_namespace,
                )
            )

        # Determine if idempotent and dry-run supported
        spec.idempotent = self._is_idempotent(category)
        spec.dry_run_supported = self._supports_dry_run(category)

        logger.debug(
            "specification_generated",
            action_id=action_id,
            spec_type=spec.spec_type.value,
            is_complete=spec.is_complete,
        )

        return spec

    def _generate_kubernetes_spec(
        self,
        action_title: str,
        target_service: Optional[str],
        template: Dict[str, Any],
        context: Dict[str, Any],
    ) -> KubernetesSpec:
        """Generate Kubernetes specification."""
        action = template["template"].get("action", "apply")
        resource_type = template["template"].get("resource_type", "deployment")

        # Detect scaling from action title
        if "scale" in action_title.lower():
            replicas = context.get("replicas", 3)
            return KubernetesSpec(
                action="patch",
                resource_type="deployment",
                resource_name=target_service or "unknown",
                namespace=self.default_namespace,
                patch={"spec": {"replicas": replicas}},
                wait_for_ready=True,
                timeout_seconds=self.default_timeout,
            )

        # Detect restart from action title
        if "restart" in action_title.lower():
            return KubernetesSpec(
                action="rollout",
                resource_type="deployment",
                resource_name=target_service or "unknown",
                namespace=self.default_namespace,
                wait_for_ready=True,
                timeout_seconds=self.default_timeout,
            )

        # Detect rollback from action title
        if "rollback" in action_title.lower():
            return KubernetesSpec(
                action="rollout",
                resource_type="deployment",
                resource_name=target_service or "unknown",
                namespace=self.default_namespace,
                manifest={"undo": True},
                wait_for_ready=True,
                timeout_seconds=self.default_timeout,
            )

        # Default deployment spec
        return KubernetesSpec(
            action=action,
            resource_type=resource_type,
            resource_name=target_service or "unknown",
            namespace=self.default_namespace,
            wait_for_ready=template["template"].get("wait_for_ready", True),
            timeout_seconds=self.default_timeout,
        )

    def _generate_command_spec(
        self,
        action_title: str,
        target_service: Optional[str],
        template: Dict[str, Any],
        context: Dict[str, Any],
    ) -> CommandSpec:
        """Generate command specification."""
        # Try to match a pattern
        title_lower = action_title.lower()

        if "restart" in title_lower:
            pattern = COMMAND_PATTERNS["restart_service"]
            return CommandSpec(
                command=pattern.command,
                args=[
                    arg.format(service=target_service or "unknown")
                    for arg in pattern.args
                ],
                shell=template["template"].get("shell", "bash"),
                timeout_seconds=pattern.timeout_seconds,
                capture_output=True,
                expected_exit_code=0,
            )

        if "scale" in title_lower:
            replicas = context.get("replicas", 3)
            pattern = COMMAND_PATTERNS["scale_deployment"]
            return CommandSpec(
                command=pattern.command,
                args=[
                    arg.format(service=target_service or "unknown", replicas=replicas)
                    for arg in pattern.args
                ],
                shell=template["template"].get("shell", "bash"),
                timeout_seconds=pattern.timeout_seconds,
                capture_output=True,
                expected_exit_code=0,
            )

        if "log" in title_lower or "investigate" in title_lower:
            pattern = COMMAND_PATTERNS["check_logs"]
            return CommandSpec(
                command=pattern.command,
                args=[
                    arg.format(service=target_service or "unknown")
                    for arg in pattern.args
                ],
                shell=template["template"].get("shell", "bash"),
                timeout_seconds=pattern.timeout_seconds,
                capture_output=True,
                expected_exit_code=0,
            )

        # Default: describe pod
        pattern = COMMAND_PATTERNS["describe_pod"]
        return CommandSpec(
            command=pattern.command,
            args=[
                arg.format(service=target_service or "unknown")
                for arg in pattern.args
            ],
            shell=template["template"].get("shell", "bash"),
            timeout_seconds=pattern.timeout_seconds,
            capture_output=True,
            expected_exit_code=0,
        )

    def _generate_api_spec(
        self,
        action_title: str,
        target_service: Optional[str],
        template: Dict[str, Any],
        context: Dict[str, Any],
    ) -> ApiCallSpec:
        """Generate API call specification."""
        title_lower = action_title.lower()
        port = context.get("port", 8080)

        if "health" in title_lower or "check" in title_lower:
            pattern = API_PATTERNS["health_check"]
            return ApiCallSpec(
                method=pattern.method,
                url=f"http://{target_service or 'localhost'}:{port}/health",
                timeout_seconds=pattern.timeout_seconds,
                expected_status_codes=pattern.expected_status_codes,
                retry_count=pattern.retry_count,
            )

        if "metric" in title_lower:
            pattern = API_PATTERNS["metrics_endpoint"]
            return ApiCallSpec(
                method=pattern.method,
                url=f"http://{target_service or 'localhost'}:{port}/metrics",
                timeout_seconds=pattern.timeout_seconds,
                expected_status_codes=pattern.expected_status_codes,
            )

        if "reload" in title_lower:
            pattern = API_PATTERNS["config_reload"]
            return ApiCallSpec(
                method=pattern.method,
                url=f"http://{target_service or 'localhost'}:{port}/admin/reload",
                timeout_seconds=pattern.timeout_seconds,
                expected_status_codes=pattern.expected_status_codes,
            )

        if "notify" in title_lower or "alert" in title_lower or "communicate" in title_lower:
            return ApiCallSpec(
                method="POST",
                url=context.get("notification_url", "http://notification-service/api/notify"),
                body={
                    "message": action_title,
                    "service": target_service,
                    "severity": context.get("severity", "info"),
                },
                timeout_seconds=30,
                expected_status_codes=[200, 201, 202],
            )

        # Default API spec
        return ApiCallSpec(
            method=template["template"].get("method", "GET"),
            url=f"http://{target_service or 'localhost'}:{port}/api/action",
            timeout_seconds=template["template"].get("timeout_seconds", 30),
            expected_status_codes=[200],
        )

    def _generate_config_spec(
        self,
        action_title: str,
        target_service: Optional[str],
        template: Dict[str, Any],
        context: Dict[str, Any],
    ) -> ConfigChangeSpec:
        """Generate configuration change specification."""
        config_path = context.get(
            "config_path",
            f"/etc/{target_service or 'app'}/config.yaml"
        )

        changes = context.get("changes", {})

        # Infer changes from action title
        title_lower = action_title.lower()
        if "timeout" in title_lower:
            changes["timeout"] = context.get("timeout_value", 30000)
        if "pool" in title_lower or "connection" in title_lower:
            changes["pool_size"] = context.get("pool_size", 100)
        if "cache" in title_lower:
            changes["cache_enabled"] = context.get("cache_enabled", True)
        if "rate" in title_lower or "limit" in title_lower:
            changes["rate_limit"] = context.get("rate_limit", 1000)

        return ConfigChangeSpec(
            config_path=config_path,
            config_format=template["template"].get("config_format", "yaml"),
            changes=changes,
            backup_before=True,
            validate_after=True,
            reload_command=f"kubectl rollout restart deployment/{target_service}" if target_service else None,
        )

    def _generate_database_spec(
        self,
        action_title: str,
        target_service: Optional[str],
        template: Dict[str, Any],
        context: Dict[str, Any],
    ) -> DatabaseQuerySpec:
        """Generate database query specification."""
        title_lower = action_title.lower()

        # Detect operation type
        if "pool" in title_lower:
            return DatabaseQuerySpec(
                connection_string_ref=f"secrets/{target_service}-db",
                query="ALTER SYSTEM SET max_connections = {max_connections}",
                query_type="ddl",
                parameters={"max_connections": context.get("max_connections", 200)},
                transaction=False,
                timeout_seconds=60,
            )

        if "index" in title_lower:
            return DatabaseQuerySpec(
                connection_string_ref=f"secrets/{target_service}-db",
                query="CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_name} ON {table} ({columns})",
                query_type="ddl",
                parameters={
                    "index_name": context.get("index_name", "idx_performance"),
                    "table": context.get("table", "events"),
                    "columns": context.get("columns", "created_at"),
                },
                transaction=False,
                timeout_seconds=300,
            )

        if "clean" in title_lower or "purge" in title_lower:
            return DatabaseQuerySpec(
                connection_string_ref=f"secrets/{target_service}-db",
                query="DELETE FROM {table} WHERE created_at < NOW() - INTERVAL '{retention}'",
                query_type="delete",
                parameters={
                    "table": context.get("table", "logs"),
                    "retention": context.get("retention", "30 days"),
                },
                transaction=True,
                timeout_seconds=600,
            )

        # Default: SELECT query for investigation
        return DatabaseQuerySpec(
            connection_string_ref=f"secrets/{target_service}-db",
            query="SELECT * FROM {table} ORDER BY created_at DESC LIMIT 100",
            query_type="select",
            parameters={"table": context.get("table", "events")},
            transaction=False,
            timeout_seconds=30,
        )

    def _is_idempotent(self, category: str) -> bool:
        """Determine if action category is idempotent."""
        idempotent_categories = {
            "configuration",
            "scaling",
            "monitoring",
        }
        return category.lower() in idempotent_categories

    def _supports_dry_run(self, category: str) -> bool:
        """Determine if action category supports dry run."""
        dry_run_categories = {
            "deployment",
            "scaling",
            "configuration",
        }
        return category.lower() in dry_run_categories

    def generate_for_plan(
        self,
        actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> SpecificationResult:
        """
        Generate specifications for all actions in a plan.

        Args:
            actions: List of action dictionaries from Orange Orangutan
            context: Additional context

        Returns:
            SpecificationResult with all specifications
        """
        import time
        start_time = time.time()
        context = context or {}

        specifications: List[TaskSpecification] = []
        warnings: List[str] = []
        complete = 0
        incomplete = 0

        for action in actions:
            try:
                spec = self.generate_specification(
                    action_id=action.get("id", ""),
                    action_title=action.get("title", ""),
                    category=action.get("category", "investigation"),
                    target_service=action.get("target_service"),
                    context={**context, **action.get("context", {})},
                )
                specifications.append(spec)

                if spec.is_complete:
                    complete += 1
                else:
                    incomplete += 1
                    warnings.append(f"Incomplete spec for action {action.get('id')}")

            except Exception as e:
                logger.error(
                    "specification_generation_failed",
                    action_id=action.get("id"),
                    error=str(e),
                )
                warnings.append(f"Failed to generate spec for {action.get('id')}: {e}")
                incomplete += 1

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "specifications_generated",
            total=len(specifications),
            complete=complete,
            incomplete=incomplete,
            duration_ms=duration_ms,
        )

        return SpecificationResult(
            specifications=specifications,
            complete_count=complete,
            incomplete_count=incomplete,
            warnings=warnings,
            duration_ms=duration_ms,
        )


def create_specification_generator(
    default_namespace: str = "default",
    default_timeout: int = 300,
) -> SpecificationGenerator:
    """Factory function to create a SpecificationGenerator."""
    return SpecificationGenerator(
        default_namespace=default_namespace,
        default_timeout=default_timeout,
    )
