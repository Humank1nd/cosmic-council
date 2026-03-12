import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx
from httpx import AsyncClient, RequestError, TimeoutException

try:
    from production_config import get_config
except ModuleNotFoundError:
    # Support imports when the repository root is on PYTHONPATH but config/ is not.
    from config.production_config import get_config

logger = logging.getLogger(__name__)


class KnowledgeBaseClient:
    """Async knowledge-base API client used by the Agent Orchestrator."""

    def __init__(self, base_url: Optional[str] = None, timeout: float = 8.0) -> None:
        config = get_config()
        self.base_url = base_url or config.knowledge_base_url
        self._timeout = timeout
        self._client = AsyncClient(base_url=self.base_url, timeout=self._timeout)

    async def search(
        self,
        query: str,
        limit: int = 5,
        min_quality: int = 3,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Search the knowledge base and return the raw results."""

        params = {
            "q": query,
            "limit": limit,
            "min_quality": min_quality,
        }
        params.update(kwargs)

        response = await self._safe_request("/kb/search", params=params)
        if not response:
            return []

        return response.get("results", [])

    async def gather_gap_contexts(
        self,
        gaps: List[str],
        limit_per_gap: int = 2,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Return focused KB contexts for each knowledge gap."""

        if not gaps:
            return {}

        tasks = [self._context_for_gap(gap, limit_per_gap) for gap in gaps]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        context_map: Dict[str, List[Dict[str, Any]]] = {}
        for gap, candidate in zip(gaps, results):
            if isinstance(candidate, Exception):
                logger.warning("Knowledge base request failed for gap=%s: %s", gap, str(candidate))
                context_map[gap] = []
            else:
                context_map[gap] = candidate

        return context_map

    async def _context_for_gap(self, gap: str, limit: int) -> List[Dict[str, Any]]:
        """Helper to fetch context for a single gap."""

        raw_results = await self.search(query=gap, limit=limit, min_quality=2)
        return [
            {
                "title": result.get("document", {}).get("title", "Untitled"),
                "path": result.get("document", {}).get("path"),
                "summary": result.get("document", {}).get("summary") or "",
                "score": result.get("score", 0.0),
                "highlights": result.get("highlights", []),
            }
            for result in raw_results
        ]

    async def _safe_request(self, url: str, *, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Wrap HTTP requests and log failures."""

        try:
            response = await self._client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except (RequestError, TimeoutException, httpx.HTTPStatusError) as exc:
            logger.warning("Knowledge base request error: url=%s params=%s error=%s", url, params, str(exc))
            return None

    async def close(self) -> None:
        """Close the HTTP transport gracefully."""

        await self._client.aclose()


knowledge_base_client = KnowledgeBaseClient()
