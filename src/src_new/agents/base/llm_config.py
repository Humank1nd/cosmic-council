"""
LLM configuration classes for AI agents.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MOCK = "mock"


class LLMModel(Enum):
    """Supported LLM models"""
    # OpenAI models
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    
    # Anthropic models
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"
    
    # Mock model for testing
    MOCK_MODEL = "mock-model"


@dataclass
class LLMConfig:
    """Configuration for LLM interactions"""
    provider: LLMProvider
    model: LLMModel
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30
    retry_attempts: int = 3
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'provider': self.provider.value,
            'model': self.model.value,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'timeout': self.timeout,
            'retry_attempts': self.retry_attempts,
            'api_key': self.api_key,
            'base_url': self.base_url,
            'custom_headers': self.custom_headers
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "LLMConfig":
        """Create config from dictionary"""
        return cls(
            provider=LLMProvider(config_dict['provider']),
            model=LLMModel(config_dict['model']),
            temperature=config_dict.get('temperature', 0.7),
            max_tokens=config_dict.get('max_tokens', 2000),
            top_p=config_dict.get('top_p', 1.0),
            frequency_penalty=config_dict.get('frequency_penalty', 0.0),
            presence_penalty=config_dict.get('presence_penalty', 0.0),
            timeout=config_dict.get('timeout', 30),
            retry_attempts=config_dict.get('retry_attempts', 3),
            api_key=config_dict.get('api_key'),
            base_url=config_dict.get('base_url'),
            custom_headers=config_dict.get('custom_headers')
        )
