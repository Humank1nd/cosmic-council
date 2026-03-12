"""
Service Mesh Hub Triangle Client for Agent Orchestrator.

HTTP client for submitting triangle reports to the Service Mesh Hub
and managing cycle lifecycle.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)


# ============== Prometheus Metrics ==============

TRIANGLE_REQUESTS = Counter(
    "triangle_client_requests_total",
    "Total triangle client requests",
    ["operation", "status"],
)

TRIANGLE_LATENCY = Histogram(
    "triangle_client_latency_seconds",
    "Triangle client request latency",
    ["operation"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)


# ============== Enums ==============

class TriangleRole(Enum):
    """Triangle roles for the Six-Seven cycle."""
    WHY = "why"
    HOW = "how"
    WHAT = "what"
    WHEN = "when"
    WHERE = "where"
    WHO = "who"


# ============== Response Models ==============

@dataclass
class TriangleResponse:
    """Response from triangle API."""
    success: bool
    cycle_id: Optional[str] = None
    message: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class CycleStatus:
    """Status of a triangle cycle."""
    cycle_id: str
    problem_id: str
    status: str  # pending, in_progress, completed, failed
    current_triangle: Optional[str] = None
    completed_triangles: List[str] = field(default_factory=list)
    recursion_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============== Client Configuration ==============

@dataclass
class TriangleClientConfig:
    """Configuration for triangle client."""
    base_url: str = "http://localhost:8002"
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    correlation_header: str = "X-Correlation-ID"
    cycle_header: str = "X-Cycle-ID"


# ============== Triangle Client ==============

class TriangleClient:
    """
    Async HTTP client for Service Mesh Hub triangle API.

    Features:
    - Automatic retries with exponential backoff
    - Correlation ID propagation
    - Prometheus metrics
    - Graceful degradation
    """

    def __init__(self, config: Optional[TriangleClientConfig] = None):
        self.config = config or TriangleClientConfig()
        self._client: Optional[httpx.AsyncClient] = None
        self._is_available: bool = True

    async def __aenter__(self) -> "TriangleClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self) -> None:
        """Initialize HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
            )
            logger.info(f"Triangle client connected to {self.config.base_url}")

    async def disconnect(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Triangle client disconnected")

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._client is not None

    # ============== Cycle Management ==============

    async def start_cycle(
        self,
        problem_id: str,
        problem_statement: str,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TriangleResponse:
        """
        Start a new triangle cycle.

        Args:
            problem_id: Unique problem identifier
            problem_statement: Problem description
            correlation_id: Optional correlation ID for tracing
            metadata: Optional additional context

        Returns:
            TriangleResponse with cycle_id if successful
        """
        payload = {
            "problem_id": problem_id,
            "problem_statement": problem_statement,
            "metadata": metadata or {},
        }

        return await self._request(
            method="POST",
            endpoint="/api/v1/triangle/start",
            payload=payload,
            correlation_id=correlation_id,
            operation="start_cycle",
        )

    async def get_cycle_status(
        self,
        cycle_id: str,
        correlation_id: Optional[str] = None,
    ) -> Optional[CycleStatus]:
        """
        Get current status of a cycle.

        Args:
            cycle_id: Cycle identifier
            correlation_id: Optional correlation ID

        Returns:
            CycleStatus if found, None otherwise
        """
        response = await self._request(
            method="GET",
            endpoint=f"/api/v1/triangle/cycle/{cycle_id}",
            correlation_id=correlation_id,
            operation="get_cycle_status",
        )

        if not response.success:
            return None

        data = response.data
        return CycleStatus(
            cycle_id=data.get("cycle_id", cycle_id),
            problem_id=data.get("problem_id", ""),
            status=data.get("status", "unknown"),
            current_triangle=data.get("current_triangle"),
            completed_triangles=data.get("completed_triangles", []),
            recursion_count=data.get("recursion_count", 0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )

    # ============== Triangle Reports ==============

    async def report_why(
        self,
        cycle_id: str,
        payload: Dict[str, Any],
        confidence: float,
        correlation_id: Optional[str] = None,
    ) -> TriangleResponse:
        """Report WHY triangle (Red Owl) result."""
        return await self._report_triangle(
            cycle_id=cycle_id,
            role=TriangleRole.WHY,
            payload=payload,
            confidence=confidence,
            correlation_id=correlation_id,
        )

    async def report_how(
        self,
        cycle_id: str,
        payload: Dict[str, Any],
        confidence: float,
        correlation_id: Optional[str] = None,
    ) -> TriangleResponse:
        """Report HOW triangle (Orange Orangutan) result."""
        return await self._report_triangle(
            cycle_id=cycle_id,
            role=TriangleRole.HOW,
            payload=payload,
            confidence=confidence,
            correlation_id=correlation_id,
        )

    async def report_what(
        self,
        cycle_id: str,
        payload: Dict[str, Any],
        confidence: float,
        correlation_id: Optional[str] = None,
    ) -> TriangleResponse:
        """Report WHAT triangle (Yellow Honeybee) result."""
        return await self._report_triangle(
            cycle_id=cycle_id,
            role=TriangleRole.WHAT,
            payload=payload,
            confidence=confidence,
            correlation_id=correlation_id,
        )

    async def report_when(
        self,
        cycle_id: str,
        payload: Dict[str, Any],
        confidence: float,
        correlation_id: Optional[str] = None,
    ) -> TriangleResponse:
        """Report WHEN triangle (Green Tortoise) result."""
        return await self._report_triangle(
            cycle_id=cycle_id,
            role=TriangleRole.WHEN,
            payload=payload,
            confidence=confidence,
            correlation_id=correlation_id,
        )

    async def report_where(
        self,
        cycle_id: str,
        payload: Dict[str, Any],
        confidence: float,
        correlation_id: Optional[str] = None,
    ) -> TriangleResponse:
        """Report WHERE triangle (Blue Dolphin) result."""
        return await self._report_triangle(
            cycle_id=cycle_id,
            role=TriangleRole.WHERE,
            payload=payload,
            confidence=confidence,
            correlation_id=correlation_id,
        )

    async def report_who(
        self,
        cycle_id: str,
        payload: Dict[str, Any],
        confidence: float,
        is_solved: bool = True,
        recursion_reason: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> TriangleResponse:
        """
        Report WHO triangle (Purple Elephant) result.

        This is the critical decision point for the 7th step.

        Args:
            cycle_id: Cycle identifier
            payload: WHO triangle payload
            confidence: Confidence score
            is_solved: Whether the problem is considered solved
            recursion_reason: Reason for recursion if not solved
            correlation_id: Optional correlation ID
        """
        extended_payload = {
            **payload,
            "solved": is_solved,
            "recursion_reason": recursion_reason or "",
        }

        return await self._report_triangle(
            cycle_id=cycle_id,
            role=TriangleRole.WHO,
            payload=extended_payload,
            confidence=confidence,
            correlation_id=correlation_id,
        )

    async def _report_triangle(
        self,
        cycle_id: str,
        role: TriangleRole,
        payload: Dict[str, Any],
        confidence: float,
        correlation_id: Optional[str] = None,
    ) -> TriangleResponse:
        """Internal method to report any triangle."""
        request_payload = {
            "role": role.value,
            "payload": payload,
            "confidence": confidence,
        }

        return await self._request(
            method="POST",
            endpoint=f"/api/v1/triangle/cycle/{cycle_id}/report/{role.value}",
            payload=request_payload,
            correlation_id=correlation_id,
            cycle_id=cycle_id,
            operation=f"report_{role.value}",
        )

    # ============== Recursion Control ==============

    async def trigger_recursion(
        self,
        cycle_id: str,
        reason: str,
        enriched_context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> TriangleResponse:
        """
        Trigger recursion back to Red Owl.

        Args:
            cycle_id: Current cycle ID
            reason: Reason for recursion
            enriched_context: Additional context for new cycle
            correlation_id: Optional correlation ID

        Returns:
            TriangleResponse with new cycle_id
        """
        payload = {
            "reason": reason,
            "enriched_context": enriched_context or {},
        }

        return await self._request(
            method="POST",
            endpoint=f"/api/v1/triangle/cycle/{cycle_id}/recurse",
            payload=payload,
            correlation_id=correlation_id,
            cycle_id=cycle_id,
            operation="trigger_recursion",
        )

    async def crystallize_truth(
        self,
        cycle_id: str,
        correlation_id: Optional[str] = None,
    ) -> TriangleResponse:
        """
        Crystallize the triangular truth for a completed cycle.

        Args:
            cycle_id: Cycle to crystallize
            correlation_id: Optional correlation ID

        Returns:
            TriangleResponse with crystallized truth data
        """
        return await self._request(
            method="POST",
            endpoint=f"/api/v1/triangle/cycle/{cycle_id}/crystallize",
            correlation_id=correlation_id,
            cycle_id=cycle_id,
            operation="crystallize_truth",
        )

    # ============== Internal Request Handler ==============

    async def _request(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        cycle_id: Optional[str] = None,
        operation: str = "request",
    ) -> TriangleResponse:
        """
        Internal request handler with retries and metrics.
        """
        if not self._client:
            await self.connect()

        headers = {}
        if correlation_id:
            headers[self.config.correlation_header] = correlation_id
        if cycle_id:
            headers[self.config.cycle_header] = cycle_id

        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                with TRIANGLE_LATENCY.labels(operation=operation).time():
                    if method.upper() == "GET":
                        response = await self._client.get(endpoint, headers=headers)
                    elif method.upper() == "POST":
                        response = await self._client.post(
                            endpoint,
                            json=payload,
                            headers=headers,
                        )
                    else:
                        raise ValueError(f"Unsupported method: {method}")

                if response.status_code >= 200 and response.status_code < 300:
                    TRIANGLE_REQUESTS.labels(operation=operation, status="success").inc()
                    data = response.json() if response.content else {}
                    return TriangleResponse(
                        success=True,
                        cycle_id=data.get("cycle_id"),
                        message=data.get("message"),
                        data=data,
                    )
                elif response.status_code == 404:
                    TRIANGLE_REQUESTS.labels(operation=operation, status="not_found").inc()
                    return TriangleResponse(
                        success=False,
                        error=f"Not found: {endpoint}",
                    )
                elif response.status_code >= 500:
                    # Server error - retry
                    last_error = f"Server error: {response.status_code}"
                    logger.warning(f"Retry {attempt + 1}/{self.config.max_retries}: {last_error}")
                else:
                    TRIANGLE_REQUESTS.labels(operation=operation, status="error").inc()
                    return TriangleResponse(
                        success=False,
                        error=f"Request failed: {response.status_code} - {response.text}",
                    )

            except httpx.TimeoutException as e:
                last_error = f"Timeout: {e}"
                logger.warning(f"Retry {attempt + 1}/{self.config.max_retries}: {last_error}")

            except httpx.ConnectError as e:
                last_error = f"Connection error: {e}"
                logger.warning(f"Retry {attempt + 1}/{self.config.max_retries}: {last_error}")
                self._is_available = False

            except Exception as e:
                last_error = f"Unexpected error: {e}"
                logger.error(f"Request failed: {last_error}")
                break

            # Wait before retry with exponential backoff
            if attempt < self.config.max_retries - 1:
                delay = self.config.retry_delay * (2 ** attempt)
                await asyncio.sleep(delay)

        TRIANGLE_REQUESTS.labels(operation=operation, status="failed").inc()
        return TriangleResponse(
            success=False,
            error=last_error or "Request failed after retries",
        )

    # ============== Health Check ==============

    async def health_check(self) -> bool:
        """
        Check if Service Mesh Hub is available.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = await self._request(
                method="GET",
                endpoint="/health",
                operation="health_check",
            )
            self._is_available = response.success
            return response.success
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self._is_available = False
            return False

    @property
    def is_available(self) -> bool:
        """Check if service is available based on last request."""
        return self._is_available


# ============== Factory Functions ==============

_default_client: Optional[TriangleClient] = None


async def get_triangle_client() -> TriangleClient:
    """Get the global triangle client instance."""
    global _default_client
    if _default_client is None:
        _default_client = TriangleClient()
        await _default_client.connect()
    return _default_client


def set_triangle_client(client: TriangleClient) -> None:
    """Set the global triangle client instance."""
    global _default_client
    _default_client = client


async def close_triangle_client() -> None:
    """Close the global triangle client."""
    global _default_client
    if _default_client:
        await _default_client.disconnect()
        _default_client = None
