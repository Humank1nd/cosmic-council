"""
Contract tests for API surface compatibility between legacy and core entrypoints.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from src.api.main import app as compat_app
from src.cosmic_council.core.api import app as core_app


@pytest.fixture(autouse=True)
def _allow_anonymous(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLOW_ANONYMOUS", "true")


@pytest.fixture
def client() -> TestClient:
    return TestClient(compat_app)


def _assert_response_wrapper(payload: dict[str, Any]) -> None:
    assert "success" in payload
    assert "message" in payload
    assert "data" in payload and isinstance(payload["data"], dict)
    assert "timestamp" in payload


def test_legacy_entrypoint_uses_core_app_object() -> None:
    assert compat_app is core_app


def test_root_endpoint_wrapper_contract(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    _assert_response_wrapper(body)

    data = body["data"]
    assert "version" in data
    assert "description" in data
    assert "endpoints" in data and isinstance(data["endpoints"], dict)
    assert "agent_process" in data["endpoints"]


def test_health_endpoint_wrapper_contract(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    _assert_response_wrapper(body)

    health = body["data"]
    assert "overall_status" in health
    assert health["overall_status"] in {"healthy", "unhealthy"}
    assert "database" in health


def test_perpetual_status_wrapper_contract(client: TestClient) -> None:
    response = client.get("/api/v1/perpetual/status")
    assert response.status_code == 200
    body = response.json()
    _assert_response_wrapper(body)

    data = body["data"]
    assert "system_available" in data
    assert "active_sessions" in data
    assert "active_ai_sessions" in data
    assert "perpetual_ai_engine_available" in data


def test_web_perpetual_sessions_compat_contract(client: TestClient) -> None:
    response = client.get("/api/web/perpetual/sessions")
    assert response.status_code == 200
    body = response.json()
    _assert_response_wrapper(body)

    data = body["data"]
    assert "sessions" in data
    assert isinstance(data["sessions"], list)


def test_web_perpetual_status_compat_contract(client: TestClient) -> None:
    response = client.get("/api/web/perpetual/status")
    assert response.status_code == 200
    body = response.json()
    _assert_response_wrapper(body)

    data = body["data"]
    assert "active_ai_sessions" in data
    assert "perpetual_ai_engine_available" in data


def test_web_perpetual_ai_sessions_compat_contract(client: TestClient) -> None:
    response = client.get("/api/web/perpetual/ai/sessions")
    assert response.status_code == 200
    body = response.json()
    _assert_response_wrapper(body)

    data = body["data"]
    assert "sessions" in data
    assert isinstance(data["sessions"], list)
