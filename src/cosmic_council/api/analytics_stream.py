"""
Real-Time Analytics Streaming for Agent Orchestrator.

Provides WebSocket-based streaming of analytics events and KPI updates
to connected dashboard clients.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from prometheus_client import Counter, Gauge

logger = logging.getLogger(__name__)


# ============== Prometheus Metrics ==============

STREAM_CONNECTIONS = Gauge(
    "analytics_stream_connections",
    "Active WebSocket connections",
)

STREAM_MESSAGES = Counter(
    "analytics_stream_messages_total",
    "Total streamed messages",
    ["event_type"],
)

STREAM_ERRORS = Counter(
    "analytics_stream_errors_total",
    "Stream errors",
    ["error_type"],
)


# ============== Enums ==============

class StreamEventType(Enum):
    """Types of streamed events."""
    CYCLE_STARTED = "cycle_started"
    CYCLE_COMPLETED = "cycle_completed"
    CYCLE_FAILED = "cycle_failed"
    TRIANGLE_COMPLETED = "triangle_completed"
    RECURSION_TRIGGERED = "recursion_triggered"
    TRUTH_CRYSTALLIZED = "truth_crystallized"
    KPI_UPDATE = "kpi_update"
    ENTERPRISE_UPDATE = "enterprise_update"
    ALERT = "alert"


class StreamChannel(Enum):
    """Subscription channels."""
    ALL = "all"
    CYCLES = "cycles"
    KPIS = "kpis"
    ENTERPRISES = "enterprises"
    ALERTS = "alerts"


# ============== Stream Event ==============

@dataclass
class StreamEvent:
    """Event to be streamed to clients."""
    event_type: StreamEventType
    channel: StreamChannel
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_id: str = field(default_factory=lambda: str(uuid4()))

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps({
            "event_id": self.event_id,
            "type": self.event_type.value,
            "channel": self.channel.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        })


# ============== Client Connection ==============

@dataclass
class StreamClient:
    """Represents a connected WebSocket client."""
    client_id: str
    websocket: WebSocket
    subscriptions: Set[StreamChannel] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)

    def is_subscribed_to(self, channel: StreamChannel) -> bool:
        """Check if client is subscribed to channel."""
        return (
            StreamChannel.ALL in self.subscriptions
            or channel in self.subscriptions
        )


# ============== Analytics Stream Manager ==============

class AnalyticsStreamManager:
    """
    Manages WebSocket connections for live dashboard updates.

    Features:
    - Multiple subscription channels
    - Event broadcasting
    - Automatic KPI updates
    - Connection health monitoring
    """

    def __init__(
        self,
        aggregator=None,
        kpi_interval: int = 5,  # KPI update interval in seconds
    ):
        self._clients: Dict[str, StreamClient] = {}
        self._aggregator = aggregator
        self.kpi_interval = kpi_interval
        self._kpi_task: Optional[asyncio.Task] = None
        self._running = False

    def set_aggregator(self, aggregator) -> None:
        """Set the analytics aggregator."""
        self._aggregator = aggregator

    @property
    def connection_count(self) -> int:
        """Get number of connected clients."""
        return len(self._clients)

    # ============== Connection Management ==============

    async def connect(
        self,
        websocket: WebSocket,
        client_id: Optional[str] = None,
    ) -> str:
        """
        Accept a new WebSocket connection.

        Args:
            websocket: FastAPI WebSocket instance
            client_id: Optional client identifier

        Returns:
            Client ID
        """
        await websocket.accept()

        client_id = client_id or str(uuid4())
        client = StreamClient(
            client_id=client_id,
            websocket=websocket,
            subscriptions={StreamChannel.ALL},  # Subscribe to all by default
        )

        self._clients[client_id] = client
        STREAM_CONNECTIONS.inc()

        logger.info(f"Client connected: {client_id}")

        # Send welcome message
        await self._send_to_client(client, StreamEvent(
            event_type=StreamEventType.KPI_UPDATE,
            channel=StreamChannel.ALL,
            data={"message": "Connected to analytics stream", "client_id": client_id},
        ))

        return client_id

    async def disconnect(self, client_id: str) -> None:
        """
        Disconnect a client.

        Args:
            client_id: Client to disconnect
        """
        if client_id in self._clients:
            del self._clients[client_id]
            STREAM_CONNECTIONS.dec()
            logger.info(f"Client disconnected: {client_id}")

    async def handle_message(
        self,
        client_id: str,
        message: str,
    ) -> None:
        """
        Handle incoming message from client.

        Supports:
        - subscribe: {"type": "subscribe", "channels": ["cycles", "kpis"]}
        - unsubscribe: {"type": "unsubscribe", "channels": ["cycles"]}
        - ping: {"type": "ping"}
        """
        client = self._clients.get(client_id)
        if not client:
            return

        client.last_activity = datetime.utcnow()

        try:
            data = json.loads(message)
            msg_type = data.get("type", "")

            if msg_type == "subscribe":
                channels = data.get("channels", [])
                for ch_name in channels:
                    try:
                        channel = StreamChannel(ch_name)
                        client.subscriptions.add(channel)
                    except ValueError:
                        pass

                await self._send_to_client(client, StreamEvent(
                    event_type=StreamEventType.KPI_UPDATE,
                    channel=StreamChannel.ALL,
                    data={"subscribed": [ch.value for ch in client.subscriptions]},
                ))

            elif msg_type == "unsubscribe":
                channels = data.get("channels", [])
                for ch_name in channels:
                    try:
                        channel = StreamChannel(ch_name)
                        client.subscriptions.discard(channel)
                    except ValueError:
                        pass

            elif msg_type == "ping":
                await self._send_to_client(client, StreamEvent(
                    event_type=StreamEventType.KPI_UPDATE,
                    channel=StreamChannel.ALL,
                    data={"type": "pong", "timestamp": datetime.utcnow().isoformat()},
                ))

        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON from client {client_id}")
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")

    # ============== Broadcasting ==============

    async def broadcast(self, event: StreamEvent) -> int:
        """
        Broadcast event to all subscribed clients.

        Args:
            event: Event to broadcast

        Returns:
            Number of clients that received the event
        """
        sent_count = 0
        failed_clients = []

        for client_id, client in self._clients.items():
            if client.is_subscribed_to(event.channel):
                try:
                    await self._send_to_client(client, event)
                    sent_count += 1
                except Exception as e:
                    logger.warning(f"Failed to send to {client_id}: {e}")
                    failed_clients.append(client_id)

        # Remove failed connections
        for client_id in failed_clients:
            await self.disconnect(client_id)

        STREAM_MESSAGES.labels(event_type=event.event_type.value).inc()
        return sent_count

    async def _send_to_client(
        self,
        client: StreamClient,
        event: StreamEvent,
    ) -> None:
        """Send event to a specific client."""
        try:
            await client.websocket.send_text(event.to_json())
        except Exception as e:
            STREAM_ERRORS.labels(error_type="send_failed").inc()
            raise

    # ============== Event Emission ==============

    async def emit_cycle_started(
        self,
        cycle_id: str,
        problem_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Emit cycle started event."""
        return await self.broadcast(StreamEvent(
            event_type=StreamEventType.CYCLE_STARTED,
            channel=StreamChannel.CYCLES,
            data={
                "cycle_id": cycle_id,
                "problem_id": problem_id,
                "metadata": metadata or {},
            },
        ))

    async def emit_cycle_completed(
        self,
        cycle_id: str,
        confidences: Dict[str, float],
        duration_seconds: float,
    ) -> int:
        """Emit cycle completed event."""
        return await self.broadcast(StreamEvent(
            event_type=StreamEventType.CYCLE_COMPLETED,
            channel=StreamChannel.CYCLES,
            data={
                "cycle_id": cycle_id,
                "confidences": confidences,
                "duration_seconds": duration_seconds,
            },
        ))

    async def emit_triangle_completed(
        self,
        cycle_id: str,
        triangle: str,
        confidence: float,
        duration_seconds: float,
    ) -> int:
        """Emit triangle completed event."""
        return await self.broadcast(StreamEvent(
            event_type=StreamEventType.TRIANGLE_COMPLETED,
            channel=StreamChannel.CYCLES,
            data={
                "cycle_id": cycle_id,
                "triangle": triangle,
                "confidence": confidence,
                "duration_seconds": duration_seconds,
            },
        ))

    async def emit_recursion_triggered(
        self,
        old_cycle_id: str,
        new_cycle_id: str,
        reason: str,
        depth: int,
    ) -> int:
        """Emit recursion triggered event."""
        return await self.broadcast(StreamEvent(
            event_type=StreamEventType.RECURSION_TRIGGERED,
            channel=StreamChannel.CYCLES,
            data={
                "old_cycle_id": old_cycle_id,
                "new_cycle_id": new_cycle_id,
                "reason": reason,
                "recursion_depth": depth,
            },
        ))

    async def emit_kpi_update(self, kpis: Dict[str, Any]) -> int:
        """Emit KPI update event."""
        return await self.broadcast(StreamEvent(
            event_type=StreamEventType.KPI_UPDATE,
            channel=StreamChannel.KPIS,
            data=kpis,
        ))

    async def emit_enterprise_update(
        self,
        enterprise: str,
        metrics: Dict[str, Any],
    ) -> int:
        """Emit enterprise update event."""
        return await self.broadcast(StreamEvent(
            event_type=StreamEventType.ENTERPRISE_UPDATE,
            channel=StreamChannel.ENTERPRISES,
            data={
                "enterprise": enterprise,
                "metrics": metrics,
            },
        ))

    async def emit_alert(
        self,
        severity: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Emit alert event."""
        return await self.broadcast(StreamEvent(
            event_type=StreamEventType.ALERT,
            channel=StreamChannel.ALERTS,
            data={
                "severity": severity,
                "message": message,
                "details": details or {},
            },
        ))

    # ============== Background KPI Updates ==============

    async def start_kpi_updates(self) -> asyncio.Task:
        """
        Start background task for periodic KPI updates.

        Returns:
            Background task
        """
        if self._kpi_task and not self._kpi_task.done():
            return self._kpi_task

        self._running = True

        async def kpi_loop():
            while self._running:
                try:
                    if self._clients and self._aggregator:
                        kpis = await self._aggregator.get_kpis()
                        await self.emit_kpi_update(kpis)
                except Exception as e:
                    logger.error(f"KPI update failed: {e}")

                await asyncio.sleep(self.kpi_interval)

        self._kpi_task = asyncio.create_task(kpi_loop())
        logger.info(f"Started KPI updates every {self.kpi_interval}s")
        return self._kpi_task

    async def stop_kpi_updates(self) -> None:
        """Stop background KPI updates."""
        self._running = False
        if self._kpi_task:
            self._kpi_task.cancel()
            try:
                await self._kpi_task
            except asyncio.CancelledError:
                pass
            self._kpi_task = None
            logger.info("Stopped KPI updates")


# ============== Global Instance ==============

_stream_manager: Optional[AnalyticsStreamManager] = None


def get_stream_manager() -> AnalyticsStreamManager:
    """Get the global stream manager."""
    global _stream_manager
    if _stream_manager is None:
        _stream_manager = AnalyticsStreamManager()
    return _stream_manager


def set_stream_manager(manager: AnalyticsStreamManager) -> None:
    """Set the global stream manager."""
    global _stream_manager
    _stream_manager = manager


# ============== FastAPI Router ==============

router = APIRouter(prefix="/analytics", tags=["analytics-stream"])


@router.websocket("/ws")
async def analytics_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for analytics streaming.

    Connect and receive real-time analytics updates.

    Subscription Protocol:
    - Send: {"type": "subscribe", "channels": ["cycles", "kpis"]}
    - Send: {"type": "unsubscribe", "channels": ["cycles"]}
    - Send: {"type": "ping"} -> Receive: {"type": "pong"}

    Available channels: all, cycles, kpis, enterprises, alerts
    """
    manager = get_stream_manager()
    client_id = await manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            await manager.handle_message(client_id, message)

    except WebSocketDisconnect:
        await manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        await manager.disconnect(client_id)


@router.get("/clients")
async def get_connected_clients() -> Dict[str, Any]:
    """Get information about connected clients."""
    manager = get_stream_manager()
    return {
        "connection_count": manager.connection_count,
    }


# ============== Event Emitter Integration ==============

def create_stream_event_handler(manager: AnalyticsStreamManager):
    """
    Create event handler that emits to stream.

    Returns callable suitable for loop_closure_handler callbacks.
    """

    async def on_recursion(old_id: str, new_id: str, context: Dict[str, Any]) -> None:
        await manager.emit_recursion_triggered(
            old_cycle_id=old_id,
            new_cycle_id=new_id,
            reason=context.get("reason", ""),
            depth=context.get("depth", 0),
        )

    async def on_completion(cycle_id: str, confidences: Dict[str, float]) -> None:
        await manager.emit_cycle_completed(
            cycle_id=cycle_id,
            confidences=confidences,
            duration_seconds=0,  # TODO: Calculate from context
        )

    return {
        "on_recursion": on_recursion,
        "on_completion": on_completion,
    }
