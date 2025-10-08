"""
Response schemas for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from ...core.types import ProblemComplexity, CycleStatus, EnterpriseType


class ProblemResponse(BaseModel):
    """Response schema for a problem"""
    id: str = Field(..., description="Problem ID")
    title: str = Field(..., description="Problem title")
    description: str = Field(..., description="Problem description")
    domain: str = Field(..., description="Problem domain")
    complexity: str = Field(..., description="Problem complexity")
    status: str = Field(..., description="Problem status")
    priority: str = Field(..., description="Problem priority")
    stakeholders: List[str] = Field(default_factory=list, description="List of stakeholder IDs")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Problem constraints")
    success_criteria: List[str] = Field(default_factory=list, description="Success criteria")
    due_date: Optional[datetime] = Field(None, description="Problem due date")
    created_by: Optional[str] = Field(None, description="User who created the problem")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @classmethod
    def from_model(cls, problem) -> "ProblemResponse":
        """Create response from problem model"""
        return cls(
            id=problem.id,
            title=problem.title,
            description=problem.description,
            domain=problem.domain,
            complexity=problem.complexity.value if hasattr(problem.complexity, 'value') else str(problem.complexity),
            status=problem.status,
            priority=problem.priority,
            stakeholders=problem.stakeholders,
            constraints=problem.constraints,
            success_criteria=problem.success_criteria,
            due_date=problem.due_date,
            created_by=problem.created_by,
            created_at=problem.created_at,
            updated_at=problem.updated_at,
            metadata=problem.metadata
        )


class ProblemListResponse(BaseModel):
    """Response schema for a list of problems"""
    problems: List[ProblemResponse] = Field(..., description="List of problems")
    total: int = Field(..., description="Total number of problems")
    limit: int = Field(..., description="Limit applied to the query")
    offset: int = Field(..., description="Offset applied to the query")


class SolutionResponse(BaseModel):
    """Response schema for a solution"""
    id: str = Field(..., description="Solution ID")
    problem_id: str = Field(..., description="ID of the problem this solution addresses")
    title: str = Field(..., description="Solution title")
    description: str = Field(..., description="Solution description")
    approach: str = Field(..., description="Solution approach")
    components: List[Dict[str, Any]] = Field(default_factory=list, description="Solution components")
    implementation_plan: Dict[str, Any] = Field(default_factory=dict, description="Implementation plan")
    success_metrics: List[str] = Field(default_factory=list, description="Success metrics")
    status: str = Field(..., description="Solution status")
    confidence_score: float = Field(..., description="Confidence score")
    created_by: Optional[str] = Field(None, description="User who created the solution")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @classmethod
    def from_model(cls, solution) -> "SolutionResponse":
        """Create response from solution model"""
        return cls(
            id=solution.id,
            problem_id=solution.problem_id,
            title=solution.title,
            description=solution.description,
            approach=solution.approach,
            components=solution.components,
            implementation_plan=solution.implementation_plan,
            success_metrics=solution.success_metrics,
            status=solution.status,
            confidence_score=solution.confidence_score,
            created_by=solution.created_by,
            created_at=solution.created_at,
            updated_at=solution.updated_at,
            metadata=solution.metadata
        )


class SolutionListResponse(BaseModel):
    """Response schema for a list of solutions"""
    solutions: List[SolutionResponse] = Field(..., description="List of solutions")
    total: int = Field(..., description="Total number of solutions")
    limit: int = Field(..., description="Limit applied to the query")
    offset: int = Field(..., description="Offset applied to the query")


class SolutionComponentResponse(BaseModel):
    """Response schema for a solution component"""
    id: str = Field(..., description="Component ID")
    solution_id: str = Field(..., description="ID of the solution this component belongs to")
    name: str = Field(..., description="Component name")
    description: str = Field(..., description="Component description")
    component_type: str = Field(..., description="Component type")
    dependencies: List[str] = Field(default_factory=list, description="Component dependencies")
    resources_required: Dict[str, Any] = Field(default_factory=dict, description="Required resources")
    estimated_effort: int = Field(..., description="Estimated effort in hours")
    priority: str = Field(..., description="Component priority")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @classmethod
    def from_model(cls, component) -> "SolutionComponentResponse":
        """Create response from solution component model"""
        return cls(
            id=component.id,
            solution_id=component.solution_id,
            name=component.name,
            description=component.description,
            component_type=component.component_type,
            dependencies=component.dependencies,
            resources_required=component.resources_required,
            estimated_effort=component.estimated_effort,
            priority=component.priority,
            created_at=component.created_at,
            updated_at=component.updated_at,
            metadata=component.metadata
        )


class CycleResponse(BaseModel):
    """Response schema for a cycle"""
    id: str = Field(..., description="Cycle ID")
    problem_id: str = Field(..., description="ID of the problem being solved")
    status: str = Field(..., description="Cycle status")
    enterprises: List[str] = Field(..., description="List of enterprise types")
    current_enterprise: Optional[str] = Field(None, description="Currently executing enterprise")
    results: Dict[str, Any] = Field(default_factory=dict, description="Cycle results")
    started_at: Optional[datetime] = Field(None, description="Cycle start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Cycle completion timestamp")
    created_by: Optional[str] = Field(None, description="User who created the cycle")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @classmethod
    def from_model(cls, cycle) -> "CycleResponse":
        """Create response from cycle model"""
        return cls(
            id=cycle.id,
            problem_id=cycle.problem_id,
            status=cycle.status.value if hasattr(cycle.status, 'value') else str(cycle.status),
            enterprises=[e.value if hasattr(e, 'value') else str(e) for e in cycle.enterprises],
            current_enterprise=cycle.current_enterprise.value if cycle.current_enterprise and hasattr(cycle.current_enterprise, 'value') else str(cycle.current_enterprise) if cycle.current_enterprise else None,
            results=cycle.results,
            started_at=cycle.started_at,
            completed_at=cycle.completed_at,
            created_by=cycle.created_by,
            created_at=cycle.created_at,
            updated_at=cycle.updated_at,
            metadata=cycle.metadata
        )


class CycleListResponse(BaseModel):
    """Response schema for a list of cycles"""
    cycles: List[CycleResponse] = Field(..., description="List of cycles")
    total: int = Field(..., description="Total number of cycles")
    limit: int = Field(..., description="Limit applied to the query")
    offset: int = Field(..., description="Offset applied to the query")
