"""
Agent communication system for the Cosmic Council.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone
import asyncio
import logging
import uuid

from .agent import BaseAgent

logger = logging.getLogger(__name__)


class Message:
    """Message between agents"""
    
    def __init__(self, sender_id: str, recipient_id: str, message_type: str, content: Dict[str, Any]):
        self.message_id = str(uuid.uuid4())
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.message_type = message_type
        self.content = content
        self.timestamp = datetime.now(timezone.utc)
        self.delivered = False
        self.read = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'message_type': self.message_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'delivered': self.delivered,
            'read': self.read
        }


class AgentCommunicationHub:
    """Central hub for agent communication"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_history: List[Message] = []
        self.subscribers: Dict[str, List[Callable]] = {}
        self.logger = logger
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the communication hub"""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.agent_id}")
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.logger.info(f"Unregistered agent: {agent_id}")
    
    async def send_message(self, message: Message) -> bool:
        """Send a message between agents"""
        try:
            # Validate recipient exists
            if message.recipient_id not in self.agents:
                self.logger.error(f"Recipient agent not found: {message.recipient_id}")
                return False
            
            # Add to message queue
            await self.message_queue.put(message)
            
            # Add to history
            self.message_history.append(message)
            
            self.logger.info(f"Message sent from {message.sender_id} to {message.recipient_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    async def broadcast_message(self, sender_id: str, message_type: str, content: Dict[str, Any]) -> int:
        """Broadcast a message to all agents"""
        sent_count = 0
        for agent_id in self.agents:
            if agent_id != sender_id:  # Don't send to self
                message = Message(sender_id, agent_id, message_type, content)
                if await self.send_message(message):
                    sent_count += 1
        
        return sent_count
    
    async def process_messages(self) -> None:
        """Process messages from the queue"""
        while True:
            try:
                message = await self.message_queue.get()
                await self._deliver_message(message)
                self.message_queue.task_done()
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
    
    async def _deliver_message(self, message: Message) -> None:
        """Deliver a message to its recipient"""
        try:
            recipient = self.agents.get(message.recipient_id)
            if recipient:
                # Mark as delivered
                message.delivered = True
                
                # Notify subscribers
                if message.message_type in self.subscribers:
                    for callback in self.subscribers[message.message_type]:
                        try:
                            await callback(message)
                        except Exception as e:
                            self.logger.error(f"Error in message subscriber: {e}")
                
                self.logger.info(f"Message delivered to {message.recipient_id}")
            else:
                self.logger.error(f"Recipient agent not found: {message.recipient_id}")
                
        except Exception as e:
            self.logger.error(f"Error delivering message: {e}")
    
    def subscribe_to_message_type(self, message_type: str, callback: Callable) -> None:
        """Subscribe to messages of a specific type"""
        if message_type not in self.subscribers:
            self.subscribers[message_type] = []
        self.subscribers[message_type].append(callback)
    
    def get_message_history(self, agent_id: Optional[str] = None, message_type: Optional[str] = None) -> List[Message]:
        """Get message history with optional filters"""
        filtered_messages = self.message_history
        
        if agent_id:
            filtered_messages = [m for m in filtered_messages if m.sender_id == agent_id or m.recipient_id == agent_id]
        
        if message_type:
            filtered_messages = [m for m in filtered_messages if m.message_type == message_type]
        
        return filtered_messages
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all registered agents"""
        return {
            agent_id: agent.get_status()
            for agent_id, agent in self.agents.items()
        }


class AgentCollaboration:
    """Facilitates collaboration between agents"""
    
    def __init__(self, communication_hub: AgentCommunicationHub):
        self.communication_hub = communication_hub
        self.active_collaborations: Dict[str, Dict[str, Any]] = {}
        self.logger = logger
    
    async def start_collaboration(self, collaboration_id: str, participants: List[str], goal: str) -> bool:
        """Start a collaboration between agents"""
        try:
            # Validate all participants are registered
            for agent_id in participants:
                if agent_id not in self.communication_hub.agents:
                    self.logger.error(f"Participant agent not found: {agent_id}")
                    return False
            
            # Create collaboration
            self.active_collaborations[collaboration_id] = {
                'participants': participants,
                'goal': goal,
                'started_at': datetime.now(timezone.utc),
                'status': 'active',
                'messages': []
            }
            
            # Notify all participants
            await self.communication_hub.broadcast_message(
                sender_id="system",
                message_type="collaboration_started",
                content={
                    'collaboration_id': collaboration_id,
                    'participants': participants,
                    'goal': goal
                }
            )
            
            self.logger.info(f"Started collaboration {collaboration_id} with {len(participants)} participants")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting collaboration: {e}")
            return False
    
    async def end_collaboration(self, collaboration_id: str, results: Dict[str, Any]) -> bool:
        """End a collaboration"""
        try:
            if collaboration_id not in self.active_collaborations:
                self.logger.error(f"Collaboration not found: {collaboration_id}")
                return False
            
            collaboration = self.active_collaborations[collaboration_id]
            collaboration['status'] = 'completed'
            collaboration['ended_at'] = datetime.now(timezone.utc)
            collaboration['results'] = results
            
            # Notify all participants
            await self.communication_hub.broadcast_message(
                sender_id="system",
                message_type="collaboration_ended",
                content={
                    'collaboration_id': collaboration_id,
                    'results': results
                }
            )
            
            self.logger.info(f"Ended collaboration {collaboration_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error ending collaboration: {e}")
            return False
    
    def get_collaboration_status(self, collaboration_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a collaboration"""
        return self.active_collaborations.get(collaboration_id)
    
    def get_all_collaborations(self) -> Dict[str, Dict[str, Any]]:
        """Get all active collaborations"""
        return self.active_collaborations.copy()
