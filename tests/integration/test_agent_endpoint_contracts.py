"""
Contract tests for agent interaction endpoints.

These tests pin response schemas so high-risk mirror merges in agent paths can
be validated quickly and deterministically.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.cosmic_council.api import agent_interactions as agent_api


ENTERPRISES = [
    "red_owl",
    "orange_orangutan",
    "yellow_honeybee",
    "green_tortoise",
    "blue_dolphin",
    "purple_elephant",
]


class _StubEnhancedResult:
    def __init__(self, enterprise: str) -> None:
        self.enterprise = enterprise
        self.status = "completed"
        self.confidence_score = 0.88
        self.recommendations = ["r1", "r2"]
        self.next_actions = ["n1"]
        self.specialized_analysis = {"summary": "stubbed", "score": 0.88}
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.processing_time = 0.01


class _StubCoreResult:
    def __init__(self, enterprise: str) -> None:
        self.status = "completed"
        self.confidence_score = 0.86
        self.processing_time = 0.01
        self.insights = {"summary": f"{enterprise}-core-stub"}
        self.recommendations = ["r1"]
        self.next_actions = ["n1"]
        self.dependencies = []
        self.personality_response = f"{enterprise} personality response"
        self.applied_rules = []
        self.wisdom_insights = []
        self.questions_for_next_cycle = []
        self.timestamp = datetime.now(timezone.utc)


def _sample_process_payload() -> dict[str, Any]:
    return {
        "title": "Contract test problem",
        "description": "Schema verification payload",
        "domain": "ops",
        "complexity": "moderate",
        "stakeholders": ["andre"],
        "constraints": {"budget": "n/a"},
        "success_criteria": ["response schema stable"],
        "context": {"source": "contract-test"},
        "analysis_depth": "quick",
    }


@pytest.fixture(autouse=True)
def _setup_agent_api(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLOW_ANONYMOUS", "true")
    agent_api.initialize_agents()
    agent_api.pre_warm_agent_list_cache()
    agent_api._rate_limit_state.clear()
    agent_api._agent_response_cache.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_list_agents_contract(client: TestClient) -> None:
    response = client.get("/api/v1/agents/")
    assert response.status_code == 200
    payload = response.json()

    assert payload.get("success") is True
    assert "message" in payload
    assert "timestamp" in payload
    assert "data" in payload and isinstance(payload["data"], dict)

    data = payload["data"]
    assert "agents" in data and isinstance(data["agents"], list)
    assert "total_count" in data and isinstance(data["total_count"], int)
    assert data["total_count"] >= 6

    enterprises = {item.get("enterprise") for item in data["agents"] if isinstance(item, dict)}
    for expected in ENTERPRISES:
        assert expected in enterprises


def test_process_endpoint_contract_all_enterprises(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _fake_process(*_args: Any, **_kwargs: Any) -> Any:
        enterprise = getattr(_args[0], "value", str(_args[0]))
        if enterprise in {"red_owl", "orange_orangutan"}:
            return _StubEnhancedResult(enterprise)
        return _StubCoreResult(enterprise)

    monkeypatch.setattr(agent_api, "_process_agent_with_fallback", _fake_process)
    payload = _sample_process_payload()

    required_keys = {
        "enterprise",
        "status",
        "confidence_score",
        "processing_time",
        "insights",
        "recommendations",
        "next_actions",
        "dependencies",
        "personality_response",
        "applied_rules",
        "wisdom_insights",
        "questions_for_next_cycle",
        "timestamp",
    }

    for enterprise in ENTERPRISES:
        response = client.post(f"/api/v1/agents/{enterprise}/process", json=payload)
        assert response.status_code == 200
        body = response.json()

        assert required_keys.issubset(body.keys())
        assert body["enterprise"] == enterprise
        assert isinstance(body["insights"], dict)
        assert isinstance(body["recommendations"], list)
        assert isinstance(body["next_actions"], list)
        assert isinstance(body["dependencies"], list)
        assert isinstance(body["applied_rules"], list)
        assert isinstance(body["wisdom_insights"], list)
        assert isinstance(body["questions_for_next_cycle"], list)


def test_sequence_endpoint_contract(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _fake_process(*_args: Any, **_kwargs: Any) -> Any:
        enterprise = getattr(_args[0], "value", str(_args[0]))
        if enterprise in {"red_owl", "orange_orangutan"}:
            return _StubEnhancedResult(enterprise)
        return _StubCoreResult(enterprise)

    monkeypatch.setattr(agent_api, "_process_agent_with_fallback", _fake_process)

    payload = {
        "problem": _sample_process_payload(),
        "agent_sequence": ["red_owl", "orange_orangutan"],
        "parallel": False,
        "synthesize": True,
    }
    response = client.post("/api/v1/agents/sequence", json=payload)
    assert response.status_code == 200
    body = response.json()

    assert isinstance(body.get("sequence_id"), str)
    assert body.get("status") == "completed"
    assert isinstance(body.get("total_processing_time"), (int, float))
    assert isinstance(body.get("agent_results"), dict)
    assert isinstance(body.get("overall_confidence"), (int, float))
    assert "timestamp" in body
    assert set(payload["agent_sequence"]).issubset(set(body["agent_results"].keys()))


def test_status_endpoint_contract(client: TestClient) -> None:
    response = client.get("/api/v1/agents/red_owl/status")
    assert response.status_code == 200
    body = response.json()

    assert body.get("enterprise") == "red_owl"
    assert body.get("status") in {"available", "unavailable"}
    assert isinstance(body.get("is_available"), bool)
    assert isinstance(body.get("current_processing_count"), int)
    assert isinstance(body.get("total_processed"), int)
    assert isinstance(body.get("average_confidence"), (int, float))
    assert isinstance(body.get("average_processing_time"), (int, float))
