"""
RED OWL RCA Agent - Cosmic Council Integration.

This module integrates the Red Owl Root Cause Analysis engine
as a SpecializedAgent in the Cosmic Council hierarchy.

Red Owl is the RED Enterprise (Level 2), answering WHY.
It is the first step in the Six-Seven Triangle cycle.
"""

import time
from typing import Any, Dict, List, Optional

import structlog

from ..hierarchical_enterprise import (
    SpecializedAgent,
    AgentSpecialization,
    TaskContext,
    AgentResult,
    AgentHandoff,
    HandoffReason,
)
from ..agent_registry_36 import TotemType, AgentRole, BaseTotemAgent

try:
    from ..integrations.llm_provider import BaseLLMProvider, LLMRequest, LLMMessage
except ImportError:
    BaseLLMProvider = None
    LLMRequest = None
    LLMMessage = None

from .engine import RedOwlEngine, create_red_owl, RedOwlResult
from .models import RedOwlConfig, AnalysisDepth

logger = structlog.get_logger(__name__)


class AgentRole:
    """Extended agent roles for Red Owl RCA."""
    ROOT_CAUSE_ANALYST = "root_cause_analyst"


class RedOwlRCAAgent(BaseTotemAgent):
    """
    Root Cause Analysis Agent for the Red Owl Team.

    This agent specializes in answering WHY - the fundamental
    question in the Six-Seven Triangle cycle. It uses multi-depth
    analysis with recursive deepening and crystallization compounding.

    The Three Falsifiable Criteria:
    1. Recursion deepens (not retries)
    2. Crystallization compounds (past solutions boost future)
    3. E8 constraint (follows depth cycle properly)
    """

    def __init__(
        self,
        agent_id: str,
        llm_provider: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        rca_config: Optional[RedOwlConfig] = None,
        kb_client: Optional[Any] = None,
        log_client: Optional[Any] = None,
        metrics_client: Optional[Any] = None,
        crystallization_store: Optional[Any] = None,
    ):
        """
        Initialize the Red Owl RCA Agent.

        Args:
            agent_id: Unique agent identifier
            llm_provider: LLM provider for intelligent analysis
            config: General agent configuration
            rca_config: Red Owl specific configuration
            kb_client: Knowledge base client
            log_client: Log search client
            metrics_client: Metrics query client
            crystallization_store: Store for crystallized truths
        """
        # Initialize as a Red Owl team member
        super().__init__(
            agent_id=agent_id,
            totem=TotemType.RED_OWL,
            role=AgentRole.ROOT_CAUSE_ANALYST,
            llm_provider=llm_provider,
            config=config,
        )

        # Override the system prompt for RCA
        self.system_prompt = """You are the Root Cause Analyst for the Red Owl Research team.
Your role is to answer WHY - the fundamental question in problem analysis.

You use multi-depth analysis:
- SURFACE: What symptoms are present?
- CAUSAL: What mechanisms explain them?
- COUNTERFACTUAL: What conditions were necessary?
- ADVERSARIAL: How could we be wrong?
- SYNTHESIS: What's the unified root cause model?

You embody three principles:
1. Recursion deepens understanding, not just retries
2. Past solutions compound into future insights
3. Analysis follows the depth cycle rigorously"""

        # Create the RCA engine
        self.rca_engine = create_red_owl(
            config=rca_config,
            llm_provider=llm_provider,
            kb_client=kb_client,
            log_client=log_client,
            metrics_client=metrics_client,
            crystallization_store=crystallization_store,
        )

        logger.info(
            "red_owl_rca_agent_initialized",
            agent_id=agent_id,
            has_llm=llm_provider is not None,
            has_crystallization=crystallization_store is not None,
        )

    async def process_task(self, context: TaskContext) -> AgentResult:
        """
        Process a root cause analysis task.

        Args:
            context: Task context with problem description

        Returns:
            AgentResult with root cause analysis
        """
        start_time = time.time()

        try:
            # Extract problem statement from context
            problem_statement = context.task_description

            # Additional context from input_data
            analysis_context = context.input_data if context.input_data else {}

            # Run the analysis
            result: RedOwlResult = await self.rca_engine.analyze(
                problem_statement=problem_statement,
                context=analysis_context,
                problem_id=context.task_id,
            )

            # Update agent metrics
            self.tasks_completed += 1
            processing_time = time.time() - start_time
            self.avg_processing_time = (
                (self.avg_processing_time * (self.tasks_completed - 1) + processing_time)
                / self.tasks_completed
            )

            # Build output
            analysis = result.analysis
            output = {
                "root_cause": analysis.final_root_cause,
                "confidence": analysis.final_confidence,
                "depth_reached": analysis.max_depth_reached.name,
                "crystallization_hits": analysis.crystallization_hits,
                "retrieval_rate": analysis.retrieval_rate,
                "recursion_count": analysis.recursion_count,
                "depth_analyses": [
                    {
                        "depth": da.depth.name,
                        "hypotheses": len(da.hypotheses),
                        "evidence": len(da.evidence),
                        "confidence": da.confidence,
                        "insights": da.key_insights,
                    }
                    for da in analysis.depth_analyses
                ],
                "reasoning": analysis.final_reasoning,
                "reasoning_summary": result.reasoning_summary,
                "total_evidence": analysis.total_evidence_gathered,
                "total_hypotheses": analysis.total_hypotheses_generated,
                "accepted_hypotheses": analysis.total_hypotheses_accepted,
            }

            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=result.success,
                output=output,
                confidence=analysis.final_confidence,
                processing_time=processing_time,
                metadata={
                    "analysis_id": analysis.id,
                    "problem_type": analysis.metadata.get("problem_type", "unknown"),
                },
            )

        except Exception as e:
            logger.error(f"RCA analysis failed: {e}")
            return AgentResult(
                agent_id=self.agent_id,
                specialization=self.specialization,
                task_id=context.task_id,
                success=False,
                output={"error": str(e)},
                confidence=0.0,
                processing_time=time.time() - start_time,
            )

    def should_handoff(self, context: TaskContext) -> Optional[AgentHandoff]:
        """
        Determine if task should be handed off to another agent.

        Red Owl RCA hands off to:
        - Orange Orangutan (HOW) for action planning after root cause found
        - Purple Elephant Problem Resolver for immediate fixes
        """
        # Check if we've completed analysis and should hand off
        if context.metadata.get("rca_complete"):
            root_cause = context.metadata.get("root_cause")
            confidence = context.metadata.get("confidence", 0)

            if confidence >= 0.7:
                # Hand off to Orange Orangutan for action planning
                return AgentHandoff(
                    from_agent=self.agent_id,
                    to_specialization=AgentSpecialization.TASK_DECOMPOSER,
                    reason=HandoffReason.SUBTASK,
                    context={
                        "root_cause": root_cause,
                        "confidence": confidence,
                        "task": "Create action plan to resolve root cause",
                    },
                    confidence=confidence,
                )

        return None

    def get_handoff_targets(self) -> List[AgentSpecialization]:
        """Get possible handoff targets."""
        return [
            AgentSpecialization.TASK_DECOMPOSER,  # Orange Orangutan for planning
            AgentSpecialization.PROBLEM_RESOLVER,  # Purple Elephant for resolution
        ]

    def get_rca_metrics(self) -> Dict[str, Any]:
        """Get RCA-specific metrics."""
        return self.rca_engine.get_metrics()


# Factory function
def create_red_owl_rca_agent(
    agent_id: str = "red_owl_rca_1",
    llm_provider: Optional[Any] = None,
    rca_config: Optional[RedOwlConfig] = None,
    **kwargs,
) -> RedOwlRCAAgent:
    """Create a Red Owl RCA Agent instance."""
    return RedOwlRCAAgent(
        agent_id=agent_id,
        llm_provider=llm_provider,
        rca_config=rca_config,
        **kwargs,
    )


# Singleton instance
_rca_agent: Optional[RedOwlRCAAgent] = None


def get_rca_agent() -> RedOwlRCAAgent:
    """Get the default RCA agent instance."""
    global _rca_agent
    if _rca_agent is None:
        _rca_agent = create_red_owl_rca_agent()
    return _rca_agent
