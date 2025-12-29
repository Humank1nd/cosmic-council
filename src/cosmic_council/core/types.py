#!/usr/bin/env python3
"""
Core Types and Enums for Agent Orchestrator Framework
Centralized definitions to avoid duplication
"""

from enum import Enum
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

class EnterpriseType(Enum):
    """The six enterprise types in the Agent Orchestrator"""
    RED_OWL = "red_owl"
    ORANGE_ORANGUTAN = "orange_orangutan"
    YELLOW_HONEYBEE = "yellow_honeybee"
    GREEN_TORTOISE = "green_tortoise"
    BLUE_DOLPHIN = "blue_dolphin"
    PURPLE_ELEPHANT = "purple_elephant"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)

    def __hash__(self):
        return hash(self.value)

class ProblemComplexity(Enum):
    """Problem complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    SYSTEMIC = "systemic"

    def __lt__(self, other):
        if not isinstance(other, ProblemComplexity):
            return NotImplemented
        order = [ProblemComplexity.SIMPLE, ProblemComplexity.MODERATE,
                 ProblemComplexity.COMPLEX, ProblemComplexity.SYSTEMIC]
        return order.index(self) < order.index(other)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)

    def __hash__(self):
        return hash(self.value)

class CycleStatus(Enum):
    """Cycle processing status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories"""
    VALIDATION = "validation"
    DATABASE = "database"
    API = "api"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    SYSTEM = "system"
    SECURITY = "security"

class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class ProblemStatement:
    """Problem statement for the Agent Orchestrator to solve"""
    title: str
    description: str
    complexity: ProblemComplexity
    domain: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    stakeholders: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.title:
            raise ValueError("title cannot be empty")

    def __str__(self) -> str:
        return f"ProblemStatement(title={self.title!r}, description={self.description!r}, complexity={self.complexity.value})"

@dataclass
class EnterpriseResult:
    """Result from an enterprise's processing"""
    enterprise_type: EnterpriseType
    status: str = "pending"
    confidence: float = 0.0
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    next_actions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    @property
    def enterprise(self) -> EnterpriseType:
        """Backward compatibility alias for enterprise_type"""
        return self.enterprise_type

@dataclass
class CycleResult:
    """Result from a complete cycle"""
    cycle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    problem: ProblemStatement = None
    status: CycleStatus = CycleStatus.PENDING
    enterprise_results: Dict[EnterpriseType, EnterpriseResult] = field(default_factory=dict)
    final_synthesis: Dict[str, Any] = field(default_factory=dict)
    feedback_loop: Dict[str, Any] = field(default_factory=dict)
    overall_confidence: float = 0.0
    total_processing_time: float = 0.0
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

# Import uuid here to avoid circular imports
import uuid
