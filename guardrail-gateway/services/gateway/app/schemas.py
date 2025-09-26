from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

class Agent(BaseModel):
    id: str
    enterprise: str
    squad: str

class Resource(BaseModel):
    service: str
    action: str

class EvalInput(BaseModel):
    agent: Agent
    resource: Resource
    context: Dict[str, Any] = Field(default_factory=dict)

class EvalDecision(BaseModel):
    allow: bool
    policies: List[str] = []
    explanation: Dict[str, Any] = Field(default_factory=dict)
    obligations: List[str] = []
    decision_id: Optional[str] = None
    timestamp: Optional[datetime] = None

# Enhanced simulation schemas
class SimulationInput(BaseModel):
    agent: Agent
    resource: Resource
    context: Dict[str, Any] = Field(default_factory=dict)
    pretend_policy_version: Optional[str] = None
    pretend_context_overrides: Optional[Dict[str, Any]] = Field(default_factory=dict)
    perturbation: Optional[Dict[str, Any]] = Field(default_factory=dict)

class PolicyDiff(BaseModel):
    policy_name: str
    current_version: str
    proposed_version: str
    changes: List[str] = []

class SimulationResult(BaseModel):
    current: Dict[str, Any]
    proposed: Dict[str, Any]
    changed_policies: List[PolicyDiff] = []
    risk_delta: Optional[float] = None
    obligations_delta: List[str] = []
    simulation_id: str

# Explainability schemas
class ViolationCode(BaseModel):
    code: str
    description: str
    severity: str
    suggested_remediation: str

class DecisionExplanation(BaseModel):
    decision_id: str
    agent: Agent
    resource: Resource
    allow: bool
    policies_applied: List[str] = []
    violations: List[ViolationCode] = []
    obligations: List[str] = []
    explanation_text: str
    timestamp: datetime
    latency_ms: int

# Budget telemetry schemas
class BudgetTelemetry(BaseModel):
    job_id: str
    estimated_cost: float
    cap: float
    cost_center: str
    agent_id: str
    timestamp: datetime
    enterprise: str

# 108-Cycle Fractal System schemas
class CycleRunRequest(BaseModel):
    cycle_id: str
    objective_ref: str
    priority: Optional[int] = Field(default=5, ge=1, le=10)
    policy_bundle: Optional[str] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_by: Optional[str] = "gateway"

class CycleRunResponse(BaseModel):
    run_id: str
    cycle_id: str
    objective_ref: str
    status: str
    created_at: datetime
    message: str

class CycleCompleteRequest(BaseModel):
    run_id: str

class CycleStatus(BaseModel):
    run_id: str
    cycle_title: str
    objective_ref: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    progress: Dict[str, Any]
    current_stage: Optional[Dict[str, Any]] = None

class StageRun(BaseModel):
    stage_run_id: str
    run_id: str
    stage_id: int
    status: str
    attempted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    guard_decision_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    output: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None

class CycleMetrics(BaseModel):
    run_id: str
    stages_total: int
    stages_completed: int
    stages_failed: int
    stages_skipped: int
    total_duration_ms: Optional[int] = None
    p95_latency_ms: Optional[int] = None
    p99_latency_ms: Optional[int] = None
    false_block_rate: Optional[float] = None
    incident_rate: Optional[float] = None
    cost_estimate: Optional[float] = None
    carbon_estimate: Optional[float] = None
    policy_violations: int = 0