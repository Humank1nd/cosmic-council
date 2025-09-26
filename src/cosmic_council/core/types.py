#!/usr/bin/env python3
"""
Core Types and Enums for Cosmic Council Framework
Centralized definitions to avoid duplication
"""

from enum import Enum
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

class EnterpriseType(Enum):
    """The six enterprise types in the Cosmic Council"""
    RED_OWL = "red_owl"
    ORANGE_ORANGUTAN = "orange_orangutan"
    YELLOW_HONEYBEE = "yellow_honeybee"
    GREEN_TORTOISE = "green_tortoise"
    BLUE_DOLPHIN = "blue_dolphin"
    PURPLE_ELEPHANT = "purple_elephant"

class ProblemComplexity(Enum):
    """Problem complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXTREME = "extreme"

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
    """Problem statement for the Cosmic Council to solve"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    complexity: ProblemComplexity = ProblemComplexity.MODERATE
    domain: str = ""
    stakeholders: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EnterpriseResult:
    """Result from an enterprise's processing"""
    enterprise: EnterpriseType
    status: str = "pending"
    insights: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
    confidence: float = 0.0
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

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
