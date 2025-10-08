"""
Request schemas for API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime

from ...core.types import ProblemComplexity, EnterpriseType


class CreateProblemRequest(BaseModel):
    """Request schema for creating a problem"""
    title: str = Field(..., min_length=1, max_length=500, description="Problem title")
    description: str = Field(..., min_length=1, description="Problem description")
    domain: str = Field(..., min_length=1, max_length=200, description="Problem domain")
    complexity: ProblemComplexity = Field(default=ProblemComplexity.MODERATE, description="Problem complexity")
    priority: str = Field(default="medium", description="Problem priority")
    stakeholders: List[str] = Field(default_factory=list, description="List of stakeholder IDs")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Problem constraints")
    success_criteria: List[str] = Field(default_factory=list, description="Success criteria")
    due_date: Optional[datetime] = Field(None, description="Problem due date")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class UpdateProblemRequest(BaseModel):
    """Request schema for updating a problem"""
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Problem title")
    description: Optional[str] = Field(None, min_length=1, description="Problem description")
    domain: Optional[str] = Field(None, min_length=1, max_length=200, description="Problem domain")
    complexity: Optional[ProblemComplexity] = Field(None, description="Problem complexity")
    status: Optional[str] = Field(None, description="Problem status")
    priority: Optional[str] = Field(None, description="Problem priority")
    stakeholders: Optional[List[str]] = Field(None, description="List of stakeholder IDs")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Problem constraints")
    success_criteria: Optional[List[str]] = Field(None, description="Success criteria")
    due_date: Optional[datetime] = Field(None, description="Problem due date")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CreateSolutionRequest(BaseModel):
    """Request schema for creating a solution"""
    problem_id: str = Field(..., description="ID of the problem this solution addresses")
    title: str = Field(..., min_length=1, max_length=500, description="Solution title")
    description: str = Field(..., min_length=1, description="Solution description")
    approach: str = Field(..., min_length=1, description="Solution approach")
    components: List[Dict[str, Any]] = Field(default_factory=list, description="Solution components")
    implementation_plan: Dict[str, Any] = Field(default_factory=dict, description="Implementation plan")
    success_metrics: List[str] = Field(default_factory=list, description="Success metrics")
    status: str = Field(default="draft", description="Solution status")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class UpdateSolutionRequest(BaseModel):
    """Request schema for updating a solution"""
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Solution title")
    description: Optional[str] = Field(None, min_length=1, description="Solution description")
    approach: Optional[str] = Field(None, min_length=1, description="Solution approach")
    components: Optional[List[Dict[str, Any]]] = Field(None, description="Solution components")
    implementation_plan: Optional[Dict[str, Any]] = Field(None, description="Implementation plan")
    success_metrics: Optional[List[str]] = Field(None, description="Success metrics")
    status: Optional[str] = Field(None, description="Solution status")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CreateSolutionComponentRequest(BaseModel):
    """Request schema for creating a solution component"""
    name: str = Field(..., min_length=1, max_length=200, description="Component name")
    description: str = Field(..., min_length=1, description="Component description")
    component_type: str = Field(..., min_length=1, description="Component type")
    dependencies: List[str] = Field(default_factory=list, description="Component dependencies")
    resources_required: Dict[str, Any] = Field(default_factory=dict, description="Required resources")
    estimated_effort: int = Field(default=0, ge=0, description="Estimated effort in hours")
    priority: str = Field(default="medium", description="Component priority")


class CreateCycleRequest(BaseModel):
    """Request schema for creating a cycle"""
    problem_id: str = Field(..., description="ID of the problem to solve")
    enterprises: List[EnterpriseType] = Field(..., min_items=1, description="List of enterprises to execute")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class UpdateCycleRequest(BaseModel):
    """Request schema for updating a cycle"""
    enterprises: Optional[List[EnterpriseType]] = Field(None, min_items=1, description="List of enterprises to execute")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
