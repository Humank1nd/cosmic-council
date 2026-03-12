"""
WebSocket Manager for Real-Time Hexagon Visualization Updates
Manages WebSocket connections and broadcasts real-time state updates
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Set, Optional
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types"""
    PING = "ping"
    PONG = "pong"
    STATE_UPDATE = "state_update"
    SECTOR_UPDATE = "sector_update"
    CYCLE_START = "cycle_start"
    CYCLE_PROGRESS = "cycle_progress"
    CYCLE_COMPLETE = "cycle_complete"
    ERROR = "error"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"


class SectorState(str, Enum):
    """Sector states for hexagon visualization"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class WebSocketConnectionManager:
    """Manages WebSocket connections and broadcasts"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, Set[WebSocket]] = {
            "hexagon": set(),
            "sectors": set(),
            "cycles": set(),
            "all": set()
        }
        self.hexagon_state: Dict[str, Any] = {
            "problem": None,
            "sectors": {},
            "cycle_in_progress": False,
            "last_update": None
        }
    
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> str:
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if not client_id:
            client_id = f"client_{len(self.active_connections)}_{datetime.now(timezone.utc).timestamp()}"
        
        logger.info(f"WebSocket connected: {client_id} (Total: {len(self.active_connections)})")
        
        # Send current state to new client
        await self.send_personal_message(websocket, {
            "type": MessageType.STATE_UPDATE.value,
            "data": self.hexagon_state,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return client_id
    
    def disconnect(self, websocket: WebSocket, client_id: Optional[str] = None):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all subscriptions
        for topic_subscribers in self.subscriptions.values():
            topic_subscribers.discard(websocket)
        
        logger.info(f"WebSocket disconnected: {client_id or 'unknown'} (Total: {len(self.active_connections)})")
    
    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any], topic: Optional[str] = None):
        """Broadcast a message to all connected clients or a specific topic"""
        subscribers = self.subscriptions.get(topic, set()) if topic else self.active_connections
        
        if not subscribers:
            return
        
        message_json = json.dumps(message)
        disconnected = []
        
        for websocket in subscribers:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def subscribe(self, websocket: WebSocket, topic: str):
        """Subscribe a client to a specific topic"""
        if topic in self.subscriptions:
            self.subscriptions[topic].add(websocket)
            logger.debug(f"Client subscribed to topic: {topic}")
        else:
            await self.send_personal_message(websocket, {
                "type": MessageType.ERROR.value,
                "error": f"Invalid topic: {topic}",
                "valid_topics": list(self.subscriptions.keys())
            })
    
    async def unsubscribe(self, websocket: WebSocket, topic: str):
        """Unsubscribe a client from a specific topic"""
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(websocket)
            logger.debug(f"Client unsubscribed from topic: {topic}")
    
    def update_hexagon_state(self, state: Dict[str, Any]):
        """Update the hexagon state and broadcast to subscribers"""
        self.hexagon_state.update(state)
        self.hexagon_state["last_update"] = datetime.now(timezone.utc).isoformat()
        
        asyncio.create_task(self.broadcast({
            "type": MessageType.STATE_UPDATE.value,
            "data": self.hexagon_state,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, topic="hexagon"))
    
    async def update_sector(
        self,
        enterprise: str,
        state: SectorState,
        progress: float = 0.0,
        confidence: float = 0.0,
        data: Optional[Dict[str, Any]] = None
    ):
        """Update a sector state and broadcast to subscribers"""
        sector_update = {
            "enterprise": enterprise,
            "state": state.value,
            "progress": progress,
            "confidence": confidence,
            "data": data or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Update hexagon state
        if "sectors" not in self.hexagon_state:
            self.hexagon_state["sectors"] = {}
        
        self.hexagon_state["sectors"][enterprise] = sector_update
        self.hexagon_state["last_update"] = datetime.now(timezone.utc).isoformat()
        
        # Broadcast sector update
        await self.broadcast({
            "type": MessageType.SECTOR_UPDATE.value,
            "data": sector_update,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, topic="sectors")
    
    async def notify_cycle_start(self, cycle_id: str, problem_id: str):
        """Notify clients that a cycle has started"""
        self.hexagon_state["cycle_in_progress"] = True
        self.hexagon_state["current_cycle_id"] = cycle_id
        self.hexagon_state["current_problem_id"] = problem_id
        
        await self.broadcast({
            "type": MessageType.CYCLE_START.value,
            "data": {
                "cycle_id": cycle_id,
                "problem_id": problem_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, topic="cycles")
    
    async def notify_cycle_progress(
        self,
        cycle_id: str,
        enterprise: str,
        progress: float,
        confidence: float
    ):
        """Notify clients of cycle progress"""
        await self.broadcast({
            "type": MessageType.CYCLE_PROGRESS.value,
            "data": {
                "cycle_id": cycle_id,
                "enterprise": enterprise,
                "progress": progress,
                "confidence": confidence,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, topic="cycles")
    
    async def notify_cycle_complete(self, cycle_id: str, result: Dict[str, Any]):
        """Notify clients that a cycle has completed"""
        self.hexagon_state["cycle_in_progress"] = False
        
        await self.broadcast({
            "type": MessageType.CYCLE_COMPLETE.value,
            "data": {
                "cycle_id": cycle_id,
                "result": result,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, topic="cycles")


# Global WebSocket manager instance
websocket_manager = WebSocketConnectionManager()

