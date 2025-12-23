import sys
from pathlib import Path

import pytest

# Ensure cosmic_council package is importable when running from repo root
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from cosmic_council.agents.unified_ai_agent_system import (
    AgentMode,
    AgentResult,
    AgentStatus,
    AgentType,
    UnifiedCosmicCouncilAgentOrchestrator,
)
from core.memory import MemoryManager


class DummyAgent:
    def __init__(self, agent_type: AgentType, confidence: float, recommendation: str):
        self.agent_type = agent_type
        self._confidence = confidence
        self._recommendation = recommendation
        self.status = AgentStatus.IDLE

    async def process(self, context):
        self.status = AgentStatus.COMPLETED
        return AgentResult(
            agent_type=self.agent_type,
            agent_id=f"{self.agent_type.value}-id",
            status=AgentStatus.COMPLETED,
            confidence_score=self._confidence,
            processed_data={
                "summary": f"Summary from {self.agent_type.value}",
                "decision": self._recommendation,
            },
            insights=[f"Insight for {self.agent_type.value}"],
            recommendations=[self._recommendation],
            next_stage_input={},
        )


@pytest.mark.asyncio
async def test_collaboration_report_tracks_consensus(tmp_path):
    orchestrator = UnifiedCosmicCouncilAgentOrchestrator(mode=AgentMode.BASIC)
    orchestrator._memory = MemoryManager(db_path=str(tmp_path / "memory.db"))
    orchestrator.agents = {
        AgentType.RED_OWL: DummyAgent(AgentType.RED_OWL, 0.65, "plan_a"),
        AgentType.YELLOW_HONEYBEE: DummyAgent(AgentType.YELLOW_HONEYBEE, 0.75, "plan_b"),
    }
    orchestrator.collaboration_order = [AgentType.RED_OWL, AgentType.YELLOW_HONEYBEE]

    results = await orchestrator.process_problem("problem-1", "Test problem")
    assert set(results.keys()) == {AgentType.RED_OWL, AgentType.YELLOW_HONEYBEE}

    report = orchestrator.get_collaboration_report("problem-1")
    assert report["problem_id"] == "problem-1"
    assert report["consensus"]["decision"] in {"plan_a", "plan_b"}
    assert len(report["records"]) == 2

    recent_context = await orchestrator._memory.get_recent_context("problem-1")
    assert len(recent_context) == 2


@pytest.mark.asyncio
async def test_consultation_added_for_low_confidence(tmp_path):
    orchestrator = UnifiedCosmicCouncilAgentOrchestrator(mode=AgentMode.BASIC)
    orchestrator._memory = MemoryManager(db_path=str(tmp_path / "memory.db"))
    orchestrator.agents = {
        AgentType.RED_OWL: DummyAgent(AgentType.RED_OWL, 0.9, "insight"),
        AgentType.YELLOW_HONEYBEE: DummyAgent(AgentType.YELLOW_HONEYBEE, 0.45, "idea"),
    }
    orchestrator.collaboration_order = [AgentType.RED_OWL, AgentType.YELLOW_HONEYBEE]

    await orchestrator.process_problem("problem-2", "Another test")
    report = orchestrator.get_collaboration_report("problem-2")
    yellow_record = next(
        record
        for record in report["records"]
        if record["agent_type"] == AgentType.YELLOW_HONEYBEE.value
    )
    assert yellow_record["consultations"], "Consultations should be recorded for low confidence agent"


@pytest.mark.asyncio
async def test_memory_manager_persists_learnings(tmp_path):
    memory = MemoryManager(db_path=str(tmp_path / "memory.db"))
    await memory.record_contribution("problem-3", "orange_orangutan", "planning", {"detail": "A"})
    recent = await memory.get_recent_context("problem-3")
    assert recent and recent[0]["summary"] == "planning"

    await memory.add_shared_knowledge("planning", {"key": "value"}, tags=["orange_orangutan"])
    shared = await memory.query_shared_knowledge(tags=["orange_orangutan"])
    assert shared and shared[0]["payload"]["key"] == "value"
