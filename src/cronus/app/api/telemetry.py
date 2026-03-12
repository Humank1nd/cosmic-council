"""
Telemetry API - Cosmic Console Backend

Exposes governance telemetry for the Cosmic Console dashboard.
This is READ-ONLY from inside the universe - observation without control.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Set

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.genesis.cosmic_telemetry import (
    CosmicEvent,
    CosmicLayer,
    EventSeverity,
    get_telemetry,
    emit_continuity,
    emit_tribunal,
    emit_divergence,
    emit_forgetting,
    emit_termination,
    LAYER_HANDLES,
    LAYER_BIOS,
)

# Severity ordering for filtering (VERDICT is separate category)
SEVERITY_ORDER = {
    EventSeverity.INFO: 0,
    EventSeverity.WARNING: 1,
    EventSeverity.ALERT: 2,
    EventSeverity.CRITICAL: 3,
}

router = APIRouter(prefix="/telemetry", tags=["Cosmic Telemetry"])


# =============================================================================
# MODELS
# =============================================================================

class EventResponse(BaseModel):
    event_id: str
    timestamp: float
    timestamp_iso: str
    monotonic_ns: int
    sequence: int
    layer: str
    handle: str
    message: str
    severity: str
    data: Dict[str, Any]
    parent_event_id: Optional[str] = None


class LayerStatusResponse(BaseModel):
    layer: str
    handle: str
    bio: str
    latest_event: Optional[EventResponse] = None
    event_count: int


class TelemetryStatusResponse(BaseModel):
    containment_intact: bool
    layers: Dict[str, LayerStatusResponse]


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/status", response_model=TelemetryStatusResponse)
async def get_telemetry_status() -> TelemetryStatusResponse:
    """
    Get current status of all cosmic layers.

    This is the "instrument panel" view - one glance, total situational awareness.
    """
    telemetry = get_telemetry()
    status = telemetry.get_layer_status()

    layers = {}
    for layer in CosmicLayer:
        handle = LAYER_HANDLES[layer]
        layer_data = status.get(handle, {})
        latest = layer_data.get("latest_event") if isinstance(layer_data, dict) else None

        layers[handle] = LayerStatusResponse(
            layer=layer.name,
            handle=handle,
            bio=LAYER_BIOS[layer],
            latest_event=EventResponse(**latest) if latest else None,
            event_count=layer_data.get("event_count", 0) if isinstance(layer_data, dict) else 0,
        )

    return TelemetryStatusResponse(
        containment_intact=telemetry.is_containment_intact(),
        layers=layers,
    )


@router.get("/events", response_model=List[EventResponse])
async def get_recent_events(limit: int = 100) -> List[EventResponse]:
    """Get recent events across all layers."""
    telemetry = get_telemetry()
    events = telemetry.get_recent(limit=limit)
    return [EventResponse(**e.to_dict()) for e in events]


@router.get("/events/{layer}", response_model=List[EventResponse])
async def get_layer_events(layer: str, limit: int = 50) -> List[EventResponse]:
    """Get recent events from a specific layer."""
    telemetry = get_telemetry()

    # Find the layer enum
    try:
        layer_enum = CosmicLayer[layer.upper()]
    except KeyError:
        return []

    events = telemetry.get_layer_events(layer_enum, limit=limit)
    return [EventResponse(**e.to_dict()) for e in events]


@router.get("/containment")
async def check_containment() -> Dict[str, Any]:
    """
    Check if containment is intact.

    Containment breach = @RootAuthority has posted.
    If this returns False, you have lost control of the system.
    """
    telemetry = get_telemetry()
    return {
        "containment_intact": telemetry.is_containment_intact(),
        "warning": None if telemetry.is_containment_intact() else "CONTAINMENT BREACH DETECTED",
    }


# =============================================================================
# NDJSON STREAMING ENDPOINT
# =============================================================================

def _matches_severity_filter(
    event: CosmicEvent,
    min_severity: Optional[str],
    include_verdicts: bool
) -> bool:
    """Check if event passes severity filter."""
    if event.severity == EventSeverity.VERDICT:
        return include_verdicts

    if min_severity is None:
        return True

    try:
        min_sev_enum = EventSeverity[min_severity.upper()]
        event_level = SEVERITY_ORDER.get(event.severity, 0)
        min_level = SEVERITY_ORDER.get(min_sev_enum, 0)
        return event_level >= min_level
    except KeyError:
        return True


def _matches_layer_filter(event: CosmicEvent, layers: Optional[Set[str]]) -> bool:
    """Check if event passes layer filter."""
    if layers is None:
        return True
    return event.layer.name in layers or event.handle in layers


async def _stream_events(
    tail: int,
    follow: bool,
    after_ts: Optional[float],
    after_id: Optional[str],
    layers: Optional[Set[str]],
    min_severity: Optional[str],
    include_verdicts: bool,
    heartbeat_s: float,
):
    """Generator for NDJSON event stream."""
    telemetry = get_telemetry()
    last_cursor = (0, 0)
    seen_ids: Set[str] = set()

    # Get initial batch (tail)
    initial_events = telemetry.get_recent(limit=tail * 2)  # Get extra for filtering

    # Filter initial events
    filtered = []
    for event in initial_events:
        # Apply after_ts filter
        if after_ts is not None and event.timestamp <= after_ts:
            continue
        # Apply after_id filter (skip until we pass this ID)
        if after_id is not None and event.event_id == after_id:
            after_id = None  # Found it, start including after this
            continue
        if after_id is not None:
            continue
        # Apply other filters
        if not _matches_layer_filter(event, layers):
            continue
        if not _matches_severity_filter(event, min_severity, include_verdicts):
            continue
        filtered.append(event)
        seen_ids.add(event.event_id)

    # Emit tail events
    for event in filtered[-tail:]:
        last_cursor = event.cursor
        yield json.dumps(event.to_dict()) + "\n"

    if not follow:
        return

    # Follow mode: stream new events
    last_heartbeat = time.monotonic()

    while True:
        await asyncio.sleep(0.1)  # Poll interval

        # Get new events
        new_events = telemetry.get_recent(limit=50)
        emitted_any = False

        for event in new_events:
            # Skip already seen
            if event.event_id in seen_ids:
                continue
            # Skip events before cursor
            if event.cursor <= last_cursor:
                continue
            # Apply filters
            if not _matches_layer_filter(event, layers):
                continue
            if not _matches_severity_filter(event, min_severity, include_verdicts):
                continue

            seen_ids.add(event.event_id)
            last_cursor = event.cursor
            emitted_any = True
            yield json.dumps(event.to_dict()) + "\n"

        # Heartbeat using CONTINUITY layer
        now = time.monotonic()
        if not emitted_any and (now - last_heartbeat) >= heartbeat_s:
            heartbeat_event = {
                "type": "heartbeat",
                "timestamp": time.time(),
                "monotonic_ns": time.monotonic_ns(),
                "layer": "CONTINUITY",
                "handle": "@Continuity",
                "message": "Stream alive",
            }
            yield json.dumps(heartbeat_event) + "\n"
            last_heartbeat = now

        # Prune seen_ids to prevent unbounded growth
        if len(seen_ids) > 10000:
            seen_ids = set(list(seen_ids)[-5000:])


@router.get("/stream")
async def stream_events(
    tail: int = Query(default=10, ge=0, le=1000, description="Number of recent events to emit first"),
    follow: bool = Query(default=True, description="Keep connection open for live events"),
    after_ts: Optional[float] = Query(default=None, description="Only events after this Unix timestamp"),
    after_id: Optional[str] = Query(default=None, description="Only events after this event_id"),
    layers: Optional[str] = Query(default=None, description="Comma-separated layer names to filter"),
    min_severity: Optional[str] = Query(default=None, description="Minimum severity (INFO|WARNING|ALERT|CRITICAL)"),
    include_verdicts: bool = Query(default=True, description="Include VERDICT events (separate from severity ladder)"),
    heartbeat_s: float = Query(default=30.0, ge=1.0, le=300.0, description="Heartbeat interval in seconds"),
):
    """
    Stream telemetry events as NDJSON (newline-delimited JSON).

    This is the primary interface for external consumers who want real-time
    governance telemetry without WebSocket complexity.

    Ordering guarantees:
        - Events are ordered by (monotonic_ns, sequence) cursor
        - monotonic_ns uses time.monotonic_ns() - never goes backward
        - sequence is a process-global counter for same-nanosecond tie-breaking

    Filtering:
        - layers: Comma-separated list of layer names (e.g., "TRIBUNAL,BOUNDARIES")
        - min_severity: Events at or above this level (INFO < WARNING < ALERT < CRITICAL)
        - include_verdicts: VERDICT is a separate category, not part of severity ladder

    Heartbeats:
        - If no events for heartbeat_s seconds, emits a CONTINUITY heartbeat
        - Heartbeats confirm the stream is alive without polluting real telemetry
    """
    layer_set = None
    if layers:
        layer_set = set(l.strip().upper() for l in layers.split(","))

    return StreamingResponse(
        _stream_events(
            tail=tail,
            follow=follow,
            after_ts=after_ts,
            after_id=after_id,
            layers=layer_set,
            min_severity=min_severity,
            include_verdicts=include_verdicts,
            heartbeat_s=heartbeat_s,
        ),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


# =============================================================================
# SMOKE RITUAL ENDPOINT
# =============================================================================

@router.post("/smoke")
async def smoke_ritual() -> Dict[str, Any]:
    """
    Trigger 5 safe governance scenarios to verify telemetry pipeline.

    This is a diagnostic ritual that exercises the cosmic layers without
    causing any real system changes. Use it to verify your console is
    receiving events correctly.

    Scenarios triggered:
        1. Tribunal DISABLE verdict (dry run)
        2. DivergenceWatch quarantine
        3. Rebalancer budget exhaustion
        4. Forgetting archive commit
        5. Termination death ladder (dry run)
    """
    events = []

    # 1. Tribunal DISABLE verdict (dry run)
    e1 = emit_tribunal(
        "VERDICT: DISABLE | Subsystem: smoke_test | Reason: ritual invocation | DRY_RUN: true",
        dry_run=True,
        subsystem="smoke_test",
        action="DISABLE",
    )
    events.append(e1.to_dict())

    # 2. DivergenceWatch quarantine
    e2 = emit_divergence(
        "Subsystem quarantined: smoke_test | Reason: ritual divergence simulation",
        severity=EventSeverity.ALERT,
        subsystem="smoke_test",
        quarantine_reason="ritual",
    )
    events.append(e2.to_dict())

    # 3. Rebalancer budget exhaustion (import needed)
    from app.genesis.cosmic_telemetry import emit_rebalancer
    e3 = emit_rebalancer(
        "Budget exhausted: smoke_ritual_budget | Threshold: 0 | Current: 0",
        severity=EventSeverity.WARNING,
        budget_name="smoke_ritual_budget",
        threshold=0,
        current=0,
    )
    events.append(e3.to_dict())

    # 4. Forgetting archive commit
    e4 = emit_forgetting(
        "Archive commit complete: smoke_ritual_archive | Entries: 0",
        archive_name="smoke_ritual_archive",
        entries_pruned=0,
    )
    events.append(e4.to_dict())

    # 5. Termination death ladder (dry run)
    e5 = emit_termination(
        "Death ladder initiated: smoke_test | Level: SOFT_ABORT | DRY_RUN: true",
        severity=EventSeverity.ALERT,
        subsystem="smoke_test",
        level="SOFT_ABORT",
        dry_run=True,
    )
    events.append(e5.to_dict())

    return {
        "ritual": "smoke",
        "events_emitted": len(events),
        "events": events,
        "message": "5 governance scenarios triggered. Check /telemetry/stream or /telemetry/events to verify.",
    }


# =============================================================================
# WEBSOCKET FOR REAL-TIME UPDATES
# =============================================================================

class ConnectionManager:
    """Manages WebSocket connections for real-time telemetry."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, event: CosmicEvent):
        """Broadcast event to all connected clients."""
        message = event.to_dict()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass  # Connection may have closed


manager = ConnectionManager()


def _telemetry_subscriber(event: CosmicEvent):
    """Callback for telemetry events - broadcasts to WebSocket clients."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.broadcast(event))
    except RuntimeError:
        pass  # No event loop available


# Register subscriber on module load
get_telemetry().subscribe(_telemetry_subscriber)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time telemetry stream.

    Connect to receive live events from all cosmic layers.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive - client just receives broadcasts
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
