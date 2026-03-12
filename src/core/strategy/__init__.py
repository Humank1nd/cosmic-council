"""
Adaptive Agent Strategy
========================

Self-improving strategy system for triangle roles using real outcomes,
telemetry, and confidence calibration.

Components:
- Registry: Versioned strategy profiles per role
- Outcomes: Outcome signal normalization and scoring
- Calibration: Confidence threshold adjustment
- Optimizer: Adaptive policy updates
- Store: Persistent strategy storage
- API: REST endpoints for strategy management

Learning Rules:
- WHY: Penalize unsupported root causes; boost evidence-backed analyses
- HOW: Reward feasible, low-risk plans with low rework rate
- WHAT: Prioritize specs that ship without revision
- WHEN: Calibrate timeline accuracy vs delivery variance
- WHERE: Increase weights for channels with best conversion
- WHO: Calibrate stakeholder impact accuracy
"""

from .registry import (
    AgentRole,
    RiskTolerance,
    EvidenceStandard,
    ToolPreference,
    StrategyConstraint,
    StrategyProfile,
    StrategyVersion,
    StrategyRegistry,
)

from .outcomes import (
    OutcomeType,
    OutcomeSignal,
    CycleOutcome,
    OutcomeMetrics,
    OutcomeEvaluator,
    RoleScorecard,
)

from .calibration import (
    CalibrationConfig,
    ConfidenceCalibration,
    CalibrationResult,
    CalibrationEngine,
)

from .optimizer import (
    AdaptationRule,
    StrategyUpdate,
    UpdateDecision,
    AdaptivePolicyEngine,
)

from .store import (
    StrategyStore,
    SQLiteStrategyStore,
)

from .learning_loop import LearningLoopService

from .api import router

from .metrics import (
    record_profile_metrics,
    record_outcome_metrics,
    record_calibration_metrics,
    record_update_metrics,
    record_optimization_metrics,
    record_learning_loop_metrics,
    record_rule_triggered,
    record_rollback,
    update_budget_metrics,
    update_cooldown_metrics,
    update_success_rate_metrics,
    record_tool_usage,
    get_all_metrics,
)

__all__ = [
    # Registry
    "AgentRole",
    "RiskTolerance",
    "EvidenceStandard",
    "ToolPreference",
    "StrategyConstraint",
    "StrategyProfile",
    "StrategyVersion",
    "StrategyRegistry",
    # Outcomes
    "OutcomeType",
    "OutcomeSignal",
    "CycleOutcome",
    "OutcomeMetrics",
    "OutcomeEvaluator",
    "RoleScorecard",
    # Calibration
    "CalibrationConfig",
    "ConfidenceCalibration",
    "CalibrationResult",
    "CalibrationEngine",
    # Optimizer
    "AdaptationRule",
    "StrategyUpdate",
    "UpdateDecision",
    "AdaptivePolicyEngine",
    # Store
    "StrategyStore",
    "SQLiteStrategyStore",
    # Learning Loop
    "LearningLoopService",
    # API
    "router",
    # Metrics
    "record_profile_metrics",
    "record_outcome_metrics",
    "record_calibration_metrics",
    "record_update_metrics",
    "record_optimization_metrics",
    "record_learning_loop_metrics",
    "record_rule_triggered",
    "record_rollback",
    "update_budget_metrics",
    "update_cooldown_metrics",
    "update_success_rate_metrics",
    "record_tool_usage",
    "get_all_metrics",
]
