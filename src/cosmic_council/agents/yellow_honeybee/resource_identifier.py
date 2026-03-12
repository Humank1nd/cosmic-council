"""
YELLOW HONEYBEE - Resource Identifier.

Identifies specific resources needed for implementation.
This implements Criterion 3: Resource identification.

Every specification must have concrete, identifiable resources:
- Services with endpoints
- Databases with connection strings
- Configurations with paths
- Secrets with references
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

import structlog

from .models import (
    Resource,
    ResourceType,
    TaskSpecification,
    SpecificationType,
)

logger = structlog.get_logger(__name__)


# Resource discovery patterns
SERVICE_PATTERNS = [
    r"service[:\s]+(\w+[-\w]*)",
    r"(\w+[-\w]*)-service",
    r"deployment/(\w+[-\w]*)",
    r"pod/(\w+[-\w]*)",
]

DATABASE_PATTERNS = [
    r"database[:\s]+(\w+[-\w]*)",
    r"(\w+[-\w]*)-db",
    r"(\w+[-\w]*)_database",
    r"postgres://([^/]+)",
    r"mysql://([^/]+)",
]

ENDPOINT_PATTERNS = [
    r"https?://([^\s/]+)",
    r"(\w+[-\w]*):(\d+)",
    r"api\.(\w+[-\w]*)",
]

CONFIG_PATTERNS = [
    r"/etc/(\w+[-\w/]*)",
    r"configmap/(\w+[-\w]*)",
    r"(\w+[-\w]*)\.ya?ml",
    r"(\w+[-\w]*)\.json",
    r"(\w+[-\w]*)\.conf",
]

SECRET_PATTERNS = [
    r"secret/(\w+[-\w]*)",
    r"secrets/(\w+[-\w]*)",
    r"(\w+[-\w]*)-credentials",
    r"(\w+[-\w]*)-token",
    r"(\w+[-\w]*)-key",
]


# Default resource configurations by type
DEFAULT_RESOURCES: Dict[str, Dict[str, Any]] = {
    "service": {
        "port": 8080,
        "protocol": "http",
        "health_path": "/health",
        "metrics_path": "/metrics",
    },
    "database": {
        "port": 5432,
        "protocol": "postgresql",
        "requires_auth": True,
    },
    "cache": {
        "port": 6379,
        "protocol": "redis",
    },
    "queue": {
        "port": 5672,
        "protocol": "amqp",
    },
    "storage": {
        "protocol": "s3",
        "requires_auth": True,
    },
}


@dataclass
class ResourceDiscoveryResult:
    """Result of resource discovery."""
    resources: List[Resource] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    endpoints: List[str] = field(default_factory=list)
    configs: List[str] = field(default_factory=list)
    secrets: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_ms: int = 0


class ResourceIdentifier:
    """
    Identifies resources needed for implementation.

    This is critical for Criterion 3: Every resource must be identified.
    """

    def __init__(
        self,
        default_namespace: str = "default",
        service_registry: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """
        Initialize the resource identifier.

        Args:
            default_namespace: Default Kubernetes namespace
            service_registry: Optional pre-populated service registry
        """
        self.default_namespace = default_namespace
        self.service_registry = service_registry or {}
        self._discovered_resources: Dict[str, Resource] = {}

        logger.info(
            "resource_identifier_initialized",
            default_namespace=default_namespace,
            registry_size=len(self.service_registry),
        )

    def identify_resources(
        self,
        spec: TaskSpecification,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Resource]:
        """
        Identify resources needed for a specification.

        Args:
            spec: The task specification to analyze
            context: Additional context for discovery

        Returns:
            List of identified resources
        """
        context = context or {}
        resources: List[Resource] = []
        seen: Set[str] = set()

        # Start with any existing resources in the spec
        for existing in spec.resources:
            if existing.identifier not in seen:
                resources.append(existing)
                seen.add(existing.identifier)

        # Discover from spec content
        discovered = self._discover_from_spec(spec, context)
        for resource in discovered:
            if resource.identifier not in seen:
                resources.append(resource)
                seen.add(resource.identifier)

        # Discover from action title and description
        text_resources = self._discover_from_text(
            f"{spec.action_title} {spec.description}",
            context,
        )
        for resource in text_resources:
            if resource.identifier not in seen:
                resources.append(resource)
                seen.add(resource.identifier)

        # Add from context if provided
        if "target_service" in context:
            service_name = context["target_service"]
            if service_name not in seen:
                resources.append(self._create_service_resource(service_name, context))
                seen.add(service_name)

        # Enrich resources with additional details
        enriched = [self._enrich_resource(r, context) for r in resources]

        logger.debug(
            "resources_identified",
            spec_id=spec.id,
            resource_count=len(enriched),
        )

        return enriched

    def _discover_from_spec(
        self,
        spec: TaskSpecification,
        context: Dict[str, Any],
    ) -> List[Resource]:
        """Discover resources from specification content."""
        resources: List[Resource] = []

        # Kubernetes spec resources
        if spec.kubernetes_spec:
            k8s = spec.kubernetes_spec
            if k8s.resource_name:
                resources.append(Resource(
                    name=k8s.resource_name,
                    type=self._k8s_resource_type(k8s.resource_type),
                    identifier=f"{k8s.namespace}/{k8s.resource_name}",
                    namespace=k8s.namespace,
                ))

        # API spec resources
        if spec.api_spec:
            api = spec.api_spec
            if api.url:
                endpoint = self._extract_endpoint(api.url)
                if endpoint:
                    resources.append(Resource(
                        name=endpoint,
                        type=ResourceType.ENDPOINT,
                        identifier=api.url,
                        endpoint=api.url,
                    ))

        # Command spec resources
        if spec.command_spec:
            cmd = spec.command_spec
            # Extract service from command args
            for arg in cmd.args:
                for pattern in SERVICE_PATTERNS:
                    match = re.search(pattern, arg)
                    if match:
                        service_name = match.group(1)
                        resources.append(self._create_service_resource(
                            service_name, context
                        ))

        # Config spec resources
        if spec.config_spec:
            cfg = spec.config_spec
            if cfg.config_path:
                resources.append(Resource(
                    name=cfg.config_path.split("/")[-1],
                    type=ResourceType.CONFIG,
                    identifier=cfg.config_path,
                ))

        # Database spec resources
        if spec.database_spec:
            db = spec.database_spec
            if db.connection_string_ref:
                resources.append(Resource(
                    name=db.connection_string_ref,
                    type=ResourceType.SECRET,
                    identifier=db.connection_string_ref,
                    requires_auth=True,
                ))

        return resources

    def _discover_from_text(
        self,
        text: str,
        context: Dict[str, Any],
    ) -> List[Resource]:
        """Discover resources from text content."""
        resources: List[Resource] = []
        text_lower = text.lower()

        # Discover services
        for pattern in SERVICE_PATTERNS:
            for match in re.finditer(pattern, text_lower):
                service_name = match.group(1)
                resources.append(self._create_service_resource(service_name, context))

        # Discover databases
        for pattern in DATABASE_PATTERNS:
            for match in re.finditer(pattern, text_lower):
                db_name = match.group(1)
                resources.append(Resource(
                    name=db_name,
                    type=ResourceType.DATABASE,
                    identifier=db_name,
                    requires_auth=True,
                ))

        # Discover endpoints
        for pattern in ENDPOINT_PATTERNS:
            for match in re.finditer(pattern, text):
                endpoint = match.group(0)
                resources.append(Resource(
                    name=endpoint,
                    type=ResourceType.ENDPOINT,
                    identifier=endpoint,
                    endpoint=endpoint,
                ))

        # Discover configs
        for pattern in CONFIG_PATTERNS:
            for match in re.finditer(pattern, text):
                config_name = match.group(1)
                resources.append(Resource(
                    name=config_name,
                    type=ResourceType.CONFIG,
                    identifier=config_name,
                ))

        # Discover secrets
        for pattern in SECRET_PATTERNS:
            for match in re.finditer(pattern, text_lower):
                secret_name = match.group(1)
                resources.append(Resource(
                    name=secret_name,
                    type=ResourceType.SECRET,
                    identifier=secret_name,
                    requires_auth=True,
                ))

        return resources

    def _create_service_resource(
        self,
        service_name: str,
        context: Dict[str, Any],
    ) -> Resource:
        """Create a service resource with defaults."""
        defaults = DEFAULT_RESOURCES["service"]
        registry_info = self.service_registry.get(service_name, {})

        port = registry_info.get("port", context.get("port", defaults["port"]))
        protocol = registry_info.get("protocol", defaults["protocol"])

        return Resource(
            name=service_name,
            type=ResourceType.SERVICE,
            identifier=service_name,
            namespace=self.default_namespace,
            endpoint=f"{protocol}://{service_name}:{port}",
            port=port,
            protocol=protocol,
        )

    def _k8s_resource_type(self, k8s_type: str) -> ResourceType:
        """Map Kubernetes resource type to ResourceType."""
        mapping = {
            "deployment": ResourceType.DEPLOYMENT,
            "pod": ResourceType.POD,
            "service": ResourceType.SERVICE,
            "configmap": ResourceType.CONFIG,
            "secret": ResourceType.SECRET,
            "container": ResourceType.CONTAINER,
        }
        return mapping.get(k8s_type.lower(), ResourceType.CUSTOM)

    def _extract_endpoint(self, url: str) -> Optional[str]:
        """Extract endpoint name from URL."""
        match = re.search(r"https?://([^/:]+)", url)
        if match:
            return match.group(1)
        return None

    def _enrich_resource(
        self,
        resource: Resource,
        context: Dict[str, Any],
    ) -> Resource:
        """Enrich resource with additional details."""
        # Check service registry
        if resource.name in self.service_registry:
            info = self.service_registry[resource.name]
            if not resource.endpoint:
                resource.endpoint = info.get("endpoint")
            if not resource.port:
                resource.port = info.get("port")
            if not resource.protocol:
                resource.protocol = info.get("protocol")

        # Add namespace if missing
        if not resource.namespace:
            resource.namespace = context.get("namespace", self.default_namespace)

        return resource

    def discover_for_plan(
        self,
        specifications: List[TaskSpecification],
        context: Optional[Dict[str, Any]] = None,
    ) -> ResourceDiscoveryResult:
        """
        Discover all resources for a plan.

        Args:
            specifications: List of task specifications
            context: Additional context

        Returns:
            ResourceDiscoveryResult with all discovered resources
        """
        import time
        start_time = time.time()
        context = context or {}

        all_resources: List[Resource] = []
        services: Set[str] = set()
        databases: Set[str] = set()
        endpoints: Set[str] = set()
        configs: Set[str] = set()
        secrets: Set[str] = set()
        warnings: List[str] = []
        seen: Set[str] = set()

        for spec in specifications:
            try:
                resources = self.identify_resources(spec, context)

                for resource in resources:
                    # Avoid duplicates
                    if resource.identifier in seen:
                        continue
                    seen.add(resource.identifier)
                    all_resources.append(resource)

                    # Categorize
                    if resource.type == ResourceType.SERVICE:
                        services.add(resource.name)
                    elif resource.type == ResourceType.DATABASE:
                        databases.add(resource.name)
                    elif resource.type == ResourceType.ENDPOINT:
                        endpoints.add(resource.identifier)
                    elif resource.type == ResourceType.CONFIG:
                        configs.add(resource.identifier)
                    elif resource.type == ResourceType.SECRET:
                        secrets.add(resource.identifier)

            except Exception as e:
                logger.error(
                    "resource_discovery_failed",
                    spec_id=spec.id,
                    error=str(e),
                )
                warnings.append(f"Failed to discover resources for {spec.id}: {e}")

        # Warn if no resources found
        for spec in specifications:
            spec_resources = [r for r in all_resources if r.identifier in seen]
            if not spec_resources:
                warnings.append(f"No resources identified for spec {spec.id}")

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "resource_discovery_complete",
            total_resources=len(all_resources),
            services=len(services),
            databases=len(databases),
            endpoints=len(endpoints),
            configs=len(configs),
            secrets=len(secrets),
            duration_ms=duration_ms,
        )

        return ResourceDiscoveryResult(
            resources=all_resources,
            services=list(services),
            databases=list(databases),
            endpoints=list(endpoints),
            configs=list(configs),
            secrets=list(secrets),
            warnings=warnings,
            duration_ms=duration_ms,
        )

    def build_dependency_graph(
        self,
        resources: List[Resource],
    ) -> Dict[str, List[str]]:
        """
        Build a dependency graph between resources.

        Args:
            resources: List of resources

        Returns:
            Dict mapping resource ID to list of dependencies
        """
        dependencies: Dict[str, List[str]] = {}

        for resource in resources:
            deps: List[str] = []

            # Secrets are dependencies for things that require auth
            if resource.requires_auth:
                for secret in resources:
                    if secret.type == ResourceType.SECRET:
                        if resource.name in secret.name or secret.name in resource.name:
                            deps.append(secret.identifier)

            # Services depend on their configs
            if resource.type == ResourceType.SERVICE:
                for config in resources:
                    if config.type == ResourceType.CONFIG:
                        if resource.name in config.name:
                            deps.append(config.identifier)

            dependencies[resource.identifier] = deps

        return dependencies


def create_resource_identifier(
    default_namespace: str = "default",
    service_registry: Optional[Dict[str, Dict[str, Any]]] = None,
) -> ResourceIdentifier:
    """Factory function to create a ResourceIdentifier."""
    return ResourceIdentifier(
        default_namespace=default_namespace,
        service_registry=service_registry,
    )
