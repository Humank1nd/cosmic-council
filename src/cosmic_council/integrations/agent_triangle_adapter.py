"""
Agent Triangle Adapter for Agent Orchestrator.

Bridges ROYGBV workflow stages to Service Mesh Hub triangle contracts,
transforming agent outputs to triangle-compatible payloads.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional

from ..core.cycle_context import CycleContext, get_current_cycle_optional
from ..core.confidence_calibrator import (
    CalibrationResult,
    ConfidenceCalibrator,
    ConfidenceDecision,
    TriangleRole,
    get_calibrator,
)
from .triangle_client import (
    TriangleClient,
    TriangleResponse,
    get_triangle_client,
)

logger = logging.getLogger(__name__)


# ============== Stage Type Mapping ==============

class StageType(Enum):
    """Workflow stage types corresponding to ROYGBV agents."""
    RESEARCH = "research"        # Red Owl -> WHY
    PLANNING = "planning"        # Orange Orangutan -> HOW
    DEVELOPMENT = "development"  # Yellow Honeybee -> WHAT
    BUDGET = "budget"            # Green Tortoise -> WHEN
    MARKET = "market"            # Blue Dolphin -> WHERE
    SUPPORT = "support"          # Purple Elephant -> WHO


# Stage to Triangle mapping
STAGE_TO_TRIANGLE: Dict[StageType, TriangleRole] = {
    StageType.RESEARCH: TriangleRole.WHY,
    StageType.PLANNING: TriangleRole.HOW,
    StageType.DEVELOPMENT: TriangleRole.WHAT,
    StageType.BUDGET: TriangleRole.WHEN,
    StageType.MARKET: TriangleRole.WHERE,
    StageType.SUPPORT: TriangleRole.WHO,
}


# ============== Stage Result ==============

@dataclass
class StageResult:
    """Result from a workflow stage."""
    stage_type: StageType
    success: bool
    confidence: float
    insights: Dict[str, Any]
    recommendations: list
    next_stage_input: Dict[str, Any]
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


# ============== Adapter Result ==============

@dataclass
class AdapterResult:
    """Result from triangle adapter."""
    success: bool
    triangle_role: TriangleRole
    triangle_response: Optional[TriangleResponse] = None
    calibration: Optional[CalibrationResult] = None
    error: Optional[str] = None
    should_recurse: bool = False
    should_escalate: bool = False


# ============== Triangle Payload Transformers ==============

def transform_why_payload(result: StageResult) -> Dict[str, Any]:
    """Transform Red Owl result to WHY triangle payload."""
    return {
        "root_cause": result.insights.get("root_cause", ""),
        "purpose": result.insights.get("purpose", ""),
        "assumptions": result.insights.get("assumptions", []),
        "constraints": result.insights.get("constraints", []),
        "knowledge_gaps": result.insights.get("knowledge_gaps", []),
        "research_summary": result.insights.get("summary", ""),
    }


def transform_how_payload(result: StageResult) -> Dict[str, Any]:
    """Transform Orange Orangutan result to HOW triangle payload."""
    return {
        "methods": result.insights.get("methods", []),
        "resources": result.insights.get("resources", []),
        "barriers": result.insights.get("barriers", []),
        "logistics": result.insights.get("logistics", {}),
        "approach": result.insights.get("approach", ""),
        "dependencies": result.insights.get("dependencies", []),
    }


def transform_what_payload(result: StageResult) -> Dict[str, Any]:
    """Transform Yellow Honeybee result to WHAT triangle payload."""
    return {
        "prototypes": result.insights.get("prototypes", []),
        "specifications": result.insights.get("specifications", {}),
        "alternatives": result.insights.get("alternatives", []),
        "innovations": result.insights.get("innovations", []),
        "technical_details": result.insights.get("technical_details", {}),
        "implementation_notes": result.insights.get("implementation_notes", ""),
    }


def transform_when_payload(result: StageResult) -> Dict[str, Any]:
    """Transform Green Tortoise result to WHEN triangle payload."""
    return {
        "timeline": result.insights.get("timeline", {}),
        "budget": result.insights.get("budget", {}),
        "milestones": result.insights.get("milestones", []),
        "dependencies": result.insights.get("dependencies", []),
        "critical_path": result.insights.get("critical_path", []),
        "risk_factors": result.insights.get("risk_factors", []),
    }


def transform_where_payload(result: StageResult) -> Dict[str, Any]:
    """Transform Blue Dolphin result to WHERE triangle payload."""
    return {
        "locations": result.insights.get("locations", []),
        "deployment_targets": result.insights.get("deployment_targets", []),
        "reach": result.insights.get("reach", {}),
        "channels": result.insights.get("channels", []),
        "distribution": result.insights.get("distribution", {}),
        "geographic_scope": result.insights.get("geographic_scope", ""),
    }


def transform_who_payload(result: StageResult) -> Dict[str, Any]:
    """Transform Purple Elephant result to WHO triangle payload."""
    return {
        "stakeholders": result.insights.get("stakeholders", []),
        "impact_assessment": result.insights.get("impact_assessment", {}),
        "affected_parties": result.insights.get("affected_parties", []),
        "decision_makers": result.insights.get("decision_makers", []),
        "resolution": result.insights.get("resolution", ""),
        "final_recommendation": result.insights.get("final_recommendation", ""),
    }


# Transformer registry
PAYLOAD_TRANSFORMERS: Dict[TriangleRole, Callable[[StageResult], Dict[str, Any]]] = {
    TriangleRole.WHY: transform_why_payload,
    TriangleRole.HOW: transform_how_payload,
    TriangleRole.WHAT: transform_what_payload,
    TriangleRole.WHEN: transform_when_payload,
    TriangleRole.WHERE: transform_where_payload,
    TriangleRole.WHO: transform_who_payload,
}


# ============== Triangle Contract Adapter ==============

class TriangleContractAdapter:
    """
    Adapts Agent Orchestrator workflow stages to Service Mesh Hub triangle contracts.

    Features:
    - Stage-to-triangle mapping
    - Payload transformation
    - Confidence calibration
    - Automatic triangle reporting
    - 7th step decision handling
    """

    def __init__(
        self,
        client: Optional[TriangleClient] = None,
        calibrator: Optional[ConfidenceCalibrator] = None,
        enabled: bool = True,
    ):
        self._client = client
        self._calibrator = calibrator
        self.enabled = enabled

    async def _get_client(self) -> TriangleClient:
        """Get or create triangle client."""
        if self._client is None:
            self._client = await get_triangle_client()
        return self._client

    def _get_calibrator(self) -> ConfidenceCalibrator:
        """Get or create confidence calibrator."""
        if self._calibrator is None:
            self._calibrator = get_calibrator()
        return self._calibrator

    def get_triangle_role(self, stage_type: StageType) -> TriangleRole:
        """Map stage type to triangle role."""
        return STAGE_TO_TRIANGLE[stage_type]

    def transform_to_triangle_payload(
        self,
        stage_type: StageType,
        result: StageResult,
    ) -> Dict[str, Any]:
        """
        Transform stage result to triangle-compatible payload.

        Args:
            stage_type: The workflow stage type
            result: The stage result to transform

        Returns:
            Triangle-compatible payload dict
        """
        role = self.get_triangle_role(stage_type)
        transformer = PAYLOAD_TRANSFORMERS.get(role)

        if transformer is None:
            logger.warning(f"No transformer for role {role}, using raw insights")
            return result.insights

        return transformer(result)

    async def report_stage_completion(
        self,
        stage_type: StageType,
        result: StageResult,
        cycle_id: str,
        is_final_stage: bool = False,
    ) -> AdapterResult:
        """
        Report stage completion to Service Mesh Hub.

        Args:
            stage_type: The completed stage type
            result: The stage result
            cycle_id: The cycle identifier
            is_final_stage: Whether this is the final (WHO) stage

        Returns:
            AdapterResult with triangle response and calibration
        """
        if not self.enabled:
            logger.debug("Triangle adapter disabled, skipping report")
            return AdapterResult(
                success=True,
                triangle_role=self.get_triangle_role(stage_type),
                error="Adapter disabled",
            )

        role = self.get_triangle_role(stage_type)
        calibrator = self._get_calibrator()

        # Get context for calibration
        context = get_current_cycle_optional()
        calibration_context = {
            "recursion_depth": context.recursion_depth if context else 0,
            "completed_stages": context.completed_stages if context else [],
        }

        # Calibrate confidence
        calibration = calibrator.evaluate_confidence(
            role=role,
            raw_confidence=result.confidence,
            context=calibration_context,
        )

        # Transform payload
        payload = self.transform_to_triangle_payload(stage_type, result)

        # Get client
        client = await self._get_client()

        # Report to Service Mesh Hub
        try:
            if role == TriangleRole.WHO:
                # Special handling for final stage
                is_solved = result.insights.get("is_solved", True)
                recursion_reason = result.insights.get("recursion_reason", "")

                # Override based on calibration
                if calibration.decision == ConfidenceDecision.RECURSE:
                    is_solved = False
                    recursion_reason = recursion_reason or calibration.reason

                response = await client.report_who(
                    cycle_id=cycle_id,
                    payload=payload,
                    confidence=calibration.calibrated_confidence,
                    is_solved=is_solved,
                    recursion_reason=recursion_reason,
                    correlation_id=context.correlation_id if context else None,
                )

                should_recurse = not is_solved and calibration.decision != ConfidenceDecision.HUMAN_REVIEW
                should_escalate = calibration.decision == ConfidenceDecision.HUMAN_REVIEW

            else:
                # Standard triangle report
                report_method = getattr(client, f"report_{role.value}")
                response = await report_method(
                    cycle_id=cycle_id,
                    payload=payload,
                    confidence=calibration.calibrated_confidence,
                    correlation_id=context.correlation_id if context else None,
                )

                should_recurse = False
                should_escalate = calibration.decision == ConfidenceDecision.HUMAN_REVIEW

            # Update context if available
            if context:
                context.mark_stage_complete(
                    stage=role.value,
                    confidence=calibration.calibrated_confidence,
                )

            return AdapterResult(
                success=response.success,
                triangle_role=role,
                triangle_response=response,
                calibration=calibration,
                error=response.error if not response.success else None,
                should_recurse=should_recurse,
                should_escalate=should_escalate,
            )

        except Exception as e:
            logger.error(f"Failed to report triangle {role.value}: {e}")
            return AdapterResult(
                success=False,
                triangle_role=role,
                calibration=calibration,
                error=str(e),
            )

    async def start_cycle(
        self,
        problem_id: str,
        problem_statement: str,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Start a new triangle cycle in Service Mesh Hub.

        Args:
            problem_id: Problem identifier
            problem_statement: Problem description
            correlation_id: Optional correlation ID
            metadata: Optional additional context

        Returns:
            Cycle ID if successful, None otherwise
        """
        if not self.enabled:
            logger.debug("Triangle adapter disabled")
            return None

        client = await self._get_client()
        response = await client.start_cycle(
            problem_id=problem_id,
            problem_statement=problem_statement,
            correlation_id=correlation_id,
            metadata=metadata,
        )

        if response.success:
            logger.info(f"Started triangle cycle: {response.cycle_id}")
            return response.cycle_id
        else:
            logger.error(f"Failed to start triangle cycle: {response.error}")
            return None

    async def handle_recursion(
        self,
        cycle_id: str,
        reason: str,
        enriched_context: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Handle 7th step recursion.

        Args:
            cycle_id: Current cycle ID
            reason: Recursion reason
            enriched_context: Additional context for new cycle

        Returns:
            New cycle ID if successful, None otherwise
        """
        if not self.enabled:
            return None

        client = await self._get_client()
        response = await client.trigger_recursion(
            cycle_id=cycle_id,
            reason=reason,
            enriched_context=enriched_context,
        )

        if response.success:
            new_cycle_id = response.data.get("new_cycle_id")
            logger.info(f"Triggered recursion: {cycle_id} -> {new_cycle_id}")
            return new_cycle_id
        else:
            logger.error(f"Failed to trigger recursion: {response.error}")
            return None

    async def crystallize(self, cycle_id: str) -> bool:
        """
        Crystallize triangular truth for completed cycle.

        Args:
            cycle_id: Cycle to crystallize

        Returns:
            True if successful
        """
        if not self.enabled:
            return True

        client = await self._get_client()
        response = await client.crystallize_truth(cycle_id)

        if response.success:
            logger.info(f"Crystallized truth for cycle: {cycle_id}")
            return True
        else:
            logger.error(f"Failed to crystallize: {response.error}")
            return False


# ============== Factory Functions ==============

_default_adapter: Optional[TriangleContractAdapter] = None


async def get_triangle_adapter() -> TriangleContractAdapter:
    """Get the global triangle adapter instance."""
    global _default_adapter
    if _default_adapter is None:
        _default_adapter = TriangleContractAdapter()
    return _default_adapter


def set_triangle_adapter(adapter: TriangleContractAdapter) -> None:
    """Set the global triangle adapter instance."""
    global _default_adapter
    _default_adapter = adapter


def create_adapter(
    enabled: bool = True,
    client: Optional[TriangleClient] = None,
    calibrator: Optional[ConfidenceCalibrator] = None,
) -> TriangleContractAdapter:
    """
    Create a new triangle adapter with configuration.

    Args:
        enabled: Whether adapter should report to Service Mesh Hub
        client: Optional pre-configured client
        calibrator: Optional pre-configured calibrator

    Returns:
        Configured TriangleContractAdapter
    """
    return TriangleContractAdapter(
        client=client,
        calibrator=calibrator,
        enabled=enabled,
    )
