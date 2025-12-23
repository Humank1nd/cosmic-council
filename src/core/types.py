"""
Compatibility layer for tests expecting `src.core.types`.
Re-exports key types from the current `cosmic_council` package.
"""
from enum import Enum

from cosmic_council.core.core import (
    CosmicCouncil,
    CosmicCouncilRule,
)
from cosmic_council.core.types import (
    EnterpriseType,
    ProblemComplexity,
    CycleStatus,
    ErrorSeverity,
    ErrorCategory,
    HealthStatus,
    ProblemStatement,
    EnterpriseResult,
)
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class ProblemResult:
    """Result of solving a problem through the Cosmic Council."""
    problem_id: str
    status: str = "pending"
    solution: Optional[str] = None
    enterprise_results: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class AgentStatus(Enum):
    """Agent execution status (compat shim for src_new agents)."""
    IDLE = "idle"
    ACTIVE = "active"
    PROCESSING = "processing"
    ERROR = "error"
    OFFLINE = "offline"

__all__ = [
    "CosmicCouncil",
    "CosmicCouncilRule",
    "EnterpriseType",
    "ProblemComplexity",
    "CycleStatus",
    "ErrorSeverity",
    "ErrorCategory",
    "HealthStatus",
    "ProblemStatement",
    "ProblemResult",
    "EnterpriseResult",
    "AgentStatus",
]
