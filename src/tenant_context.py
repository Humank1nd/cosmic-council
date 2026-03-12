"""
Tenant Context for Agent Orchestrator
E8-Engine Phase 30.2 - Multi-Tenant Governance

Tenant context propagation and audit metadata for agent operations:
- Request-scoped tenant context
- Audit trail enrichment
- Cross-service tenant propagation
"""

import json
import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog


logger = structlog.get_logger(__name__)


# Context variables for tenant scoping
_tenant_context: ContextVar[Optional["TenantContext"]] = ContextVar(
    "tenant_context", default=None
)
_audit_context: ContextVar[Optional["AuditContext"]] = ContextVar(
    "audit_context", default=None
)


@dataclass
class TenantContext:
    """
    Tenant context for Agent Orchestrator operations.

    Propagated through the entire request lifecycle.
    """
    tenant_id: str
    user_id: str
    role: str

    # Request context
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None

    # Cycle context
    cycle_id: Optional[str] = None
    parent_cycle_id: Optional[str] = None
    recursion_depth: int = 0

    # Auth context
    auth_method: str = "jwt"
    permissions: List[str] = field(default_factory=list)

    # Plan context
    plan_tier: str = "free"
    plan_limits: Dict[str, int] = field(default_factory=dict)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_headers(self) -> Dict[str, str]:
        """Convert to HTTP headers for propagation."""
        return {
            "X-Tenant-ID": self.tenant_id,
            "X-User-ID": self.user_id,
            "X-Request-ID": self.request_id,
            "X-Correlation-ID": self.correlation_id or self.request_id,
            "X-Cycle-ID": self.cycle_id or "",
            "X-Recursion-Depth": str(self.recursion_depth),
            "X-Plan-Tier": self.plan_tier,
            "X-Auth-Method": self.auth_method,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "role": self.role,
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
            "cycle_id": self.cycle_id,
            "parent_cycle_id": self.parent_cycle_id,
            "recursion_depth": self.recursion_depth,
            "auth_method": self.auth_method,
            "plan_tier": self.plan_tier,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> Optional["TenantContext"]:
        """Create from HTTP headers."""
        tenant_id = headers.get("X-Tenant-ID") or headers.get("x-tenant-id")
        if not tenant_id:
            return None

        return cls(
            tenant_id=tenant_id,
            user_id=headers.get("X-User-ID", headers.get("x-user-id", "")),
            role=headers.get("X-User-Role", headers.get("x-user-role", "viewer")),
            request_id=headers.get("X-Request-ID", headers.get("x-request-id", str(uuid.uuid4()))),
            correlation_id=headers.get("X-Correlation-ID", headers.get("x-correlation-id")),
            cycle_id=headers.get("X-Cycle-ID", headers.get("x-cycle-id")),
            recursion_depth=int(headers.get("X-Recursion-Depth", headers.get("x-recursion-depth", "0"))),
            plan_tier=headers.get("X-Plan-Tier", headers.get("x-plan-tier", "free")),
            auth_method=headers.get("X-Auth-Method", headers.get("x-auth-method", "jwt")),
        )


@dataclass
class AuditContext:
    """
    Audit context for tracking operations.

    Captures who did what, when, and on what.
    """
    # Identity
    tenant_id: str
    user_id: str
    role: str

    # Request
    request_id: str
    correlation_id: Optional[str] = None

    # Action
    action: str = ""
    resource_type: str = ""
    resource_id: Optional[str] = None

    # Timing
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    # Result
    success: bool = True
    error_message: Optional[str] = None

    # Details
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    changes: List[Dict[str, Any]] = field(default_factory=list)

    # Context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    plan_tier: str = "free"

    def complete(
        self,
        success: bool = True,
        error_message: Optional[str] = None,
        output_summary: Optional[str] = None,
    ) -> None:
        """Mark the audit context as complete."""
        self.completed_at = datetime.utcnow()
        self.success = success
        self.error_message = error_message
        self.output_summary = output_summary

    def add_change(
        self,
        field_name: str,
        old_value: Any,
        new_value: Any,
    ) -> None:
        """Record a change."""
        self.changes.append({
            "field": field_name,
            "old": old_value,
            "new": new_value,
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        duration_ms = None
        if self.completed_at:
            duration_ms = (self.completed_at - self.started_at).total_seconds() * 1000

        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "role": self.role,
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": duration_ms,
            "success": self.success,
            "error_message": self.error_message,
            "changes_count": len(self.changes),
            "plan_tier": self.plan_tier,
        }

    def to_log_dict(self) -> Dict[str, Any]:
        """Convert to structured log format."""
        return {
            **self.to_dict(),
            "changes": self.changes,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
        }


# Context management functions

def set_tenant_context(context: TenantContext) -> None:
    """Set the current tenant context."""
    _tenant_context.set(context)

    # Also set structlog context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        request_id=context.request_id,
        cycle_id=context.cycle_id,
    )


def get_tenant_context() -> Optional[TenantContext]:
    """Get the current tenant context."""
    return _tenant_context.get()


def require_tenant_context() -> TenantContext:
    """Get the current tenant context or raise an error."""
    context = get_tenant_context()
    if context is None:
        raise ValueError("Tenant context not set")
    return context


def clear_tenant_context() -> None:
    """Clear the current tenant context."""
    _tenant_context.set(None)
    structlog.contextvars.clear_contextvars()


def set_audit_context(context: AuditContext) -> None:
    """Set the current audit context."""
    _audit_context.set(context)


def get_audit_context() -> Optional[AuditContext]:
    """Get the current audit context."""
    return _audit_context.get()


def clear_audit_context() -> None:
    """Clear the current audit context."""
    _audit_context.set(None)


# Decorators for tenant-scoped operations

def with_tenant_context(func):
    """
    Decorator to ensure tenant context is available.

    Usage:
        @with_tenant_context
        async def process_report(report_data):
            tenant = require_tenant_context()
            ...
    """
    import functools

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        context = get_tenant_context()
        if context is None:
            raise ValueError("Tenant context required for this operation")
        return await func(*args, **kwargs)

    return wrapper


def audit_action(action: str, resource_type: str):
    """
    Decorator to automatically create audit context.

    Usage:
        @audit_action("create", "cycle")
        async def create_cycle(...):
            ...
    """
    import functools

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            tenant_ctx = get_tenant_context()

            if tenant_ctx:
                audit_ctx = AuditContext(
                    tenant_id=tenant_ctx.tenant_id,
                    user_id=tenant_ctx.user_id,
                    role=tenant_ctx.role,
                    request_id=tenant_ctx.request_id,
                    correlation_id=tenant_ctx.correlation_id,
                    action=action,
                    resource_type=resource_type,
                    plan_tier=tenant_ctx.plan_tier,
                )
                set_audit_context(audit_ctx)

            try:
                result = await func(*args, **kwargs)

                if tenant_ctx:
                    audit_ctx = get_audit_context()
                    if audit_ctx:
                        audit_ctx.complete(success=True)
                        _log_audit(audit_ctx)

                return result

            except Exception as e:
                if tenant_ctx:
                    audit_ctx = get_audit_context()
                    if audit_ctx:
                        audit_ctx.complete(success=False, error_message=str(e))
                        _log_audit(audit_ctx)
                raise

            finally:
                clear_audit_context()

        return wrapper
    return decorator


def _log_audit(audit_ctx: AuditContext) -> None:
    """Log audit event."""
    logger.info(
        "audit_event",
        **audit_ctx.to_log_dict(),
    )


# Agent context enrichment

@dataclass
class AgentTenantMetadata:
    """
    Tenant metadata attached to agent operations.

    Provides tenant context to agents for policy awareness.
    """
    tenant_id: str
    plan_tier: str

    # Limits
    max_tokens: int = 100000
    max_recursion: int = 3
    min_confidence: float = 0.3

    # Features
    custom_models_enabled: bool = False
    priority_processing: bool = False

    # Tracking
    cycle_id: str = ""
    parent_cycle_id: Optional[str] = None
    recursion_depth: int = 0

    @classmethod
    def from_tenant_context(
        cls,
        context: TenantContext,
    ) -> "AgentTenantMetadata":
        """Create from tenant context."""
        limits = context.plan_limits

        return cls(
            tenant_id=context.tenant_id,
            plan_tier=context.plan_tier,
            max_tokens=limits.get("tokens_per_cycle", 100000),
            max_recursion=limits.get("max_recursion", 3),
            min_confidence=limits.get("min_confidence", 0.3),
            custom_models_enabled=limits.get("custom_models", False),
            priority_processing=limits.get("priority", False),
            cycle_id=context.cycle_id or "",
            parent_cycle_id=context.parent_cycle_id,
            recursion_depth=context.recursion_depth,
        )

    def to_agent_context(self) -> Dict[str, Any]:
        """Convert to context dict for agent prompt."""
        return {
            "tenant": {
                "id": self.tenant_id,
                "plan": self.plan_tier,
            },
            "limits": {
                "max_tokens": self.max_tokens,
                "max_recursion": self.max_recursion,
                "min_confidence": self.min_confidence,
            },
            "cycle": {
                "id": self.cycle_id,
                "parent_id": self.parent_cycle_id,
                "depth": self.recursion_depth,
            },
        }


# Policy violation callback for agents

class AgentPolicyViolation(Exception):
    """Exception raised when agent violates tenant policy."""

    def __init__(
        self,
        message: str,
        violation_type: str,
        tenant_id: str,
        agent_id: Optional[str] = None,
    ):
        super().__init__(message)
        self.violation_type = violation_type
        self.tenant_id = tenant_id
        self.agent_id = agent_id
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": str(self),
            "violation_type": self.violation_type,
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
        }


def check_agent_policy(
    agent_id: str,
    action: str,
    metadata: AgentTenantMetadata,
) -> None:
    """
    Check if agent action is allowed by tenant policy.

    Raises AgentPolicyViolation if not allowed.
    """
    # Check recursion depth
    if action == "spawn_child_cycle":
        if metadata.recursion_depth >= metadata.max_recursion:
            raise AgentPolicyViolation(
                f"Maximum recursion depth exceeded ({metadata.recursion_depth}/{metadata.max_recursion})",
                "recursion_limit",
                metadata.tenant_id,
                agent_id,
            )

    # Additional policy checks can be added here


# Cross-service propagation helpers

def create_propagation_headers(
    tenant_context: Optional[TenantContext] = None,
) -> Dict[str, str]:
    """Create headers for cross-service propagation."""
    context = tenant_context or get_tenant_context()
    if context is None:
        return {}

    return context.to_headers()


def extract_tenant_from_request(
    headers: Dict[str, str],
) -> Optional[TenantContext]:
    """Extract tenant context from incoming request headers."""
    return TenantContext.from_headers(headers)
