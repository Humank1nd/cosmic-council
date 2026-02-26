"""
ORANGE ORANGUTAN - Action Planning Engine.

The main orchestrator for Orange Orangutan action planning.
This is the ORANGE Enterprise (Level 3) in the ROYGBV hierarchy,
answering the fundamental question: HOW do we fix this?

The engine coordinates:
1. Action decomposition from root cause
2. Dependency resolution
3. Risk assessment
4. Rollback planning
5. Final plan assembly

Three falsifiable criteria this engine embodies:
1. Dependency ordering - actions are topologically sorted
2. Rollback reversibility - each action has a defined rollback
3. Risk gates - high-risk actions require approval
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

import structlog

from .models import (
    ActionCategory,
    ActionPlan,
    ActionStatus,
    ActionStep,
    Dependency,
    OrangeOrangutanConfig,
    RiskLevel,
)
from .action_decomposer import ActionDecomposer, create_action_decomposer, DecompositionResult
from .dependency_resolver import DependencyResolver, create_dependency_resolver
from .risk_assessor import RiskAssessor, create_risk_assessor
from .rollback_planner import RollbackPlanner, create_rollback_planner

logger = structlog.get_logger(__name__)


@dataclass
class OrangeOrangutanResult:
    """Complete result from Orange Orangutan planning."""
    plan: ActionPlan
    success: bool = True
    error: Optional[str] = None
    reasoning: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_ms: int = 0


class OrangeOrangutanEngine:
    """
    The Orange Orangutan Action Planning Engine.

    Orange Orangutan is the ORANGE Enterprise agent in the Cosmic Council.
    It specializes in answering HOW - the second question in
    the Six-Seven Triangle cycle.

    Usage:
        engine = OrangeOrangutanEngine()
        result = await engine.plan(
            root_cause="Database connection pool exhausted",
            confidence=0.85
        )
        print(result.plan.execution_order)
    """

    def __init__(
        self,
        config: Optional[OrangeOrangutanConfig] = None,
        llm_provider: Optional[Any] = None,
        critical_services: Optional[List[str]] = None,
    ):
        """
        Initialize the Orange Orangutan engine.

        Args:
            config: Configuration for planning behavior
            llm_provider: LLM provider for intelligent planning
            critical_services: List of critical service names
        """
        self.config = config or OrangeOrangutanConfig()
        self.llm_provider = llm_provider

        # Initialize components
        self.decomposer = create_action_decomposer(llm_provider)
        self.dependency_resolver = create_dependency_resolver(infer_implicit=True)
        self.risk_assessor = create_risk_assessor(
            critical_services=critical_services,
            risk_threshold=self.config.require_approval_min_risk,
        )
        self.rollback_planner = create_rollback_planner(
            require_all=self.config.require_rollback_for_all_actions,
        )

        logger.info(
            "orange_orangutan_engine_initialized",
            has_llm=llm_provider is not None,
            auto_execute_max_risk=self.config.auto_execute_max_risk.name,
            require_approval_min_risk=self.config.require_approval_min_risk.name,
        )

    async def plan(
        self,
        root_cause: str,
        confidence: float = 0.7,
        context: Optional[Dict[str, Any]] = None,
        problem_id: Optional[str] = None,
    ) -> OrangeOrangutanResult:
        """
        Create an action plan to address a root cause.

        This is the main entry point for Orange Orangutan planning.

        Args:
            root_cause: The root cause statement from Red Owl
            confidence: Confidence in the root cause (0-1)
            context: Additional context (service info, metrics, etc.)
            problem_id: Optional ID for tracking

        Returns:
            OrangeOrangutanResult containing the complete plan
        """
        start_time = time.time()
        context = context or {}
        problem_id = problem_id or str(uuid4())
        reasoning: List[str] = []
        warnings: List[str] = []

        try:
            logger.info(
                "orange_orangutan_planning_started",
                problem_id=problem_id,
                root_cause_length=len(root_cause),
                confidence=confidence,
            )

            # Step 1: Decompose root cause into actions
            decomposition = await self.decomposer.decompose(
                root_cause=root_cause,
                context=context,
                confidence=confidence,
            )
            reasoning.extend(decomposition.reasoning)
            reasoning.append(f"Generated {len(decomposition.actions)} actions")

            if not decomposition.actions:
                return OrangeOrangutanResult(
                    plan=ActionPlan(
                        root_cause=root_cause,
                        root_cause_confidence=confidence,
                        problem_id=problem_id,
                        title="No actions identified",
                    ),
                    success=False,
                    error="Could not identify any actions for this root cause",
                    reasoning=reasoning,
                    duration_ms=int((time.time() - start_time) * 1000),
                )

            # Step 2: Resolve dependencies
            dep_result = self.dependency_resolver.resolve(
                actions=decomposition.actions,
            )
            warnings.extend(dep_result.warnings)
            if dep_result.cycles_detected:
                warnings.append("Dependency cycles detected - order may not be optimal")
            reasoning.append(f"Resolved dependencies: {len(dep_result.dependencies)} edges")

            # Step 3: Assess risks
            # First create the plan so we can pass it to risk assessor
            plan = ActionPlan(
                root_cause=root_cause,
                root_cause_confidence=confidence,
                problem_id=problem_id,
                title=f"Action plan for: {root_cause[:50]}...",
                description=f"Generated plan to address: {root_cause}",
                actions=decomposition.actions,
                execution_order=dep_result.execution_order,
                dependencies=dep_result.dependencies,
            )

            risk_assessment = self.risk_assessor.assess_plan(plan, context)
            plan.overall_risk = risk_assessment.overall_risk
            plan.risk_summary = risk_assessment.risk_summary
            plan.requires_approval = len(risk_assessment.approval_gates) > 0
            plan.approval_gates = risk_assessment.approval_gates
            reasoning.append(f"Risk assessment: {risk_assessment.risk_summary}")

            # Step 4: Plan rollbacks (Criterion 2)
            rollback_plan = self.rollback_planner.create_plan_rollback(plan, context)
            plan.rollback_order = rollback_plan.rollback_order
            warnings.extend(rollback_plan.warnings)
            reasoning.append(f"Rollback plan: {rollback_plan.estimated_duration_seconds}s total")

            # Step 5: Validate the plan
            is_valid, validation_issues = self._validate_plan(plan)
            if not is_valid:
                warnings.extend(validation_issues)

            # Compute final metrics
            plan._compute_duration()

            duration_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "orange_orangutan_planning_complete",
                problem_id=problem_id,
                action_count=len(plan.actions),
                overall_risk=plan.overall_risk.name,
                approval_gates=len(plan.approval_gates),
                duration_ms=duration_ms,
            )

            return OrangeOrangutanResult(
                plan=plan,
                success=True,
                reasoning=reasoning,
                warnings=warnings,
                duration_ms=duration_ms,
            )

        except Exception as e:
            logger.error(
                "orange_orangutan_planning_failed",
                problem_id=problem_id,
                error=str(e),
            )

            return OrangeOrangutanResult(
                plan=ActionPlan(
                    root_cause=root_cause,
                    root_cause_confidence=confidence,
                    problem_id=problem_id,
                ),
                success=False,
                error=str(e),
                reasoning=reasoning,
                warnings=warnings,
                duration_ms=int((time.time() - start_time) * 1000),
            )

    async def quick_plan(
        self,
        root_cause: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a quick plan returning just the essentials.

        Args:
            root_cause: The root cause statement
            context: Additional context

        Returns:
            Dict with action_count, overall_risk, approval_needed, etc.
        """
        result = await self.plan(root_cause, context=context)

        return {
            "success": result.success,
            "action_count": len(result.plan.actions),
            "overall_risk": result.plan.overall_risk.name,
            "approval_needed": result.plan.requires_approval,
            "approval_gates": len(result.plan.approval_gates),
            "estimated_duration_seconds": result.plan.estimated_total_duration_seconds,
            "execution_order": result.plan.execution_order[:5],  # First 5
            "duration_ms": result.duration_ms,
        }

    def _validate_plan(self, plan: ActionPlan) -> tuple:
        """Validate that a plan meets all criteria."""
        issues: List[str] = []

        # Criterion 1: Check dependency ordering
        valid_order, order_issues = self.dependency_resolver.validate_order(
            plan.actions, plan.execution_order
        )
        if not valid_order:
            issues.extend(order_issues)

        # Criterion 2: Check all have rollback
        rollback_valid, rollback_issues = self.rollback_planner.validate_rollbacks(plan)
        if not rollback_valid:
            issues.extend(rollback_issues)

        # Criterion 3: Check high-risk actions have approval gates
        for action in plan.actions:
            if action.risk_level.requires_approval and action.id not in plan.approval_gates:
                issues.append(f"High-risk action {action.id} not in approval gates")

        return len(issues) == 0, issues

    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics about engine configuration."""
        return {
            "config": {
                "auto_execute_max_risk": self.config.auto_execute_max_risk.name,
                "require_approval_min_risk": self.config.require_approval_min_risk.name,
                "max_actions_per_plan": self.config.max_actions_per_plan,
                "require_rollback_for_all": self.config.require_rollback_for_all_actions,
            },
            "capabilities": {
                "has_llm": self.llm_provider is not None,
                "infers_dependencies": True,
                "assesses_risk": True,
                "plans_rollback": True,
            },
        }


# Factory function
def create_orange_orangutan(
    config: Optional[OrangeOrangutanConfig] = None,
    llm_provider: Optional[Any] = None,
    critical_services: Optional[List[str]] = None,
) -> OrangeOrangutanEngine:
    """Create an Orange Orangutan engine instance."""
    return OrangeOrangutanEngine(
        config=config,
        llm_provider=llm_provider,
        critical_services=critical_services,
    )


# Global instance for simple usage
_default_engine: Optional[OrangeOrangutanEngine] = None


def get_orange_orangutan() -> OrangeOrangutanEngine:
    """Get the default Orange Orangutan engine instance."""
    global _default_engine
    if _default_engine is None:
        _default_engine = create_orange_orangutan()
    return _default_engine


async def plan_actions(
    root_cause: str,
    confidence: float = 0.7,
    context: Optional[Dict[str, Any]] = None,
) -> OrangeOrangutanResult:
    """
    Convenience function to create an action plan.

    Usage:
        result = await plan_actions("Database connection pool exhausted")
        print(result.plan.execution_order)
    """
    engine = get_orange_orangutan()
    return await engine.plan(root_cause, confidence, context)
