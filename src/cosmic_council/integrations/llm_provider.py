"""
LLM Provider Interface for Agent Orchestrator
Abstract interface that allows any AI model to be plugged into the system.

This is the core "supercharger" architecture - Agent Orchestrator works with ANY AI model
by implementing this simple interface. The goal is to leverage larger foundation models to
train and orchestrate a supply chain of six enterprise-level operations, each staffed with
departments of agents that master a single task and know precisely when to hand work off.
As those agents learn, they evolve their own operational frameworks and distill the acquired
capabilities into lighter-weight models so they can run locally where needed.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProviderType(Enum):
    """Supported LLM provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure_openai"
    COHERE = "cohere"
    MISTRAL = "mistral"
    OLLAMA = "ollama"
    LOCAL = "local"
    CUSTOM = "custom"
    MOCK = "mock"  # For testing


@dataclass
class LLMMessage:
    """A message in the LLM conversation"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Response from an LLM provider"""
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMRequest:
    """Request to an LLM provider"""
    messages: List[LLMMessage]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    This is the core interface that makes Agent Orchestrator a "supercharger" -
    any AI model can be integrated by implementing this interface. It keeps the product
    model-agnostic so larger models can teach the supply chain and the agents can in turn
    distill their behavior into smaller models over time.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LLM provider.
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config or {}
        self.provider_type = self.config.get("provider_type", LLMProviderType.CUSTOM)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def generate(
        self,
        request: LLMRequest
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        This is the core method that all providers must implement.
        Agent Orchestrator agents call this method, making the system
        completely model-agnostic.
        
        Args:
            request: The LLM request with messages and parameters
            
        Returns:
            LLMResponse: The generated response
            
        Raises:
            Exception: If generation fails
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get list of available models for this provider.
        
        Returns:
            List of model identifiers
        """
        pass
    
    def get_default_model(self) -> Optional[str]:
        """
        Get the default model for this provider.
        
        Returns:
            Default model identifier, or None if not applicable
        """
        return None
    
    def validate_request(self, request: LLMRequest) -> bool:
        """
        Validate that the request is compatible with this provider.
        
        Args:
            request: The LLM request to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not request.messages:
            return False
        if request.temperature < 0 or request.temperature > 2:
            return False
        return True
    
    async def health_check(self) -> bool:
        """
        Check if the provider is healthy and available.
        
        Returns:
            True if provider is available, False otherwise
        """
        return True


class MockLLMProvider(BaseLLMProvider):
    """
    Mock LLM provider for testing without actual AI models.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.provider_type = LLMProviderType.MOCK
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a mock response"""
        # Extract the last user message as context
        user_messages = [msg.content for msg in request.messages if msg.role == "user"]
        last_message = user_messages[-1] if user_messages else "No message"
        
        mock_content = f"[MOCK] Response to: {last_message[:100]}..."
        
        return LLMResponse(
            content=mock_content,
            model=request.model or "mock-model",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            metadata={"provider": "mock"}
        )
    
    def get_available_models(self) -> List[str]:
        return ["mock-model"]
    
    def get_default_model(self) -> str:
        return "mock-model"

