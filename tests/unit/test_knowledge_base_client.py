import pytest

import httpx

from cosmic_council.integrations.knowledge_base_client import KnowledgeBaseClient


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


@pytest.mark.asyncio
async def test_gather_gap_contexts_returns_context(monkeypatch):
    async def fake_get(self, url, params=None):
        return DummyResponse({
            "results": [
                {
                    "document": {
                        "path": "/knowledge/1",
                        "title": "Context Title",
                        "summary": "A helpful summary",
                    },
                    "score": 0.94,
                    "highlights": ["summary"],
                }
            ]
        })

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    client = KnowledgeBaseClient(base_url="http://kb-api")
    contexts = await client.gather_gap_contexts(["market", "policy"])
    assert "market" in contexts
    assert contexts["market"][0]["title"] == "Context Title"
    await client.close()


@pytest.mark.asyncio
async def test_gather_gap_contexts_handles_errors(monkeypatch):
    async def fake_get(self, url, params=None):
        raise httpx.RequestError("boom")

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)
    client = KnowledgeBaseClient(base_url="http://kb-api")
    contexts = await client.gather_gap_contexts(["risk"])
    assert contexts["risk"] == []
    await client.close()
