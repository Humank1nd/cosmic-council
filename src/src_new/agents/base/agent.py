"""
Base agent class for all AI agents in the Cosmic Council system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging
import uuid

from .llm_config import LLMConfig
from ...core.types import EnterpriseType, AgentStatus

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, agent_id: str = None, name: str = "", description: str = ""):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.logger = logger
        self.metadata = {}
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results"""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data"""
        pass
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with input validation and error handling"""
        try:
            # Validate input
            if not self.validate_input(input_data):
                raise ValueError("Invalid input data")
            
            # Update status
            self.status = AgentStatus.PROCESSING
            self.updated_at = datetime.now(timezone.utc)
            
            # Process the input
            result = await self.process(input_data)
            
            # Update status
            self.status = AgentStatus.IDLE
            self.updated_at = datetime.now(timezone.utc)
            
            return result
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.updated_at = datetime.now(timezone.utc)
            self.logger.error(f"Agent {self.agent_id} execution failed: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update agent metadata"""
        self.metadata[key] = value
        self.updated_at = datetime.now(timezone.utc)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.agent_id}, name={self.name})"


class LLMAgent(BaseAgent):
    """Base class for LLM-powered agents"""
    
    def __init__(self, agent_id: str = None, name: str = "", description: str = "", llm_config: LLMConfig = None):
        super().__init__(agent_id, name, description)
        self.llm_config = llm_config or LLMConfig(
            provider=LLMConfig.LLMProvider.MOCK,
            model=LLMConfig.LLMModel.MOCK_MODEL
        )
    
    async def call_llm(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Call the LLM with a prompt"""
        try:
            # This would integrate with actual LLM providers
            # For now, return a mock response
            if self.llm_config.provider == LLMConfig.LLMProvider.MOCK:
                return f"Mock LLM response for prompt: {prompt[:50]}..."
            
            # In a real implementation, this would call the actual LLM
            # based on the provider and model configuration
            raise NotImplementedError("LLM integration not implemented")
            
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise
    
    def build_prompt(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Build a prompt from input data"""
        # This would be implemented by specific agent types
        return f"Process this data: {input_data}"
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input using LLM"""
        try:
            # Build prompt
            prompt = self.build_prompt(input_data)
            
            # Call LLM
            response = await self.call_llm(prompt, input_data)
            
            # Parse and return result
            return {
                'agent_id': self.agent_id,
                'response': response,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'input_data': input_data
            }
            
        except Exception as e:
            self.logger.error(f"LLM agent processing failed: {e}")
            raise
