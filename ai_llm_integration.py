"""
Legacy AI LLM integration compatibility shim for tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class LLMProvider(Enum):
    MOCK = "mock"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class LLMModel(Enum):
    GPT_4 = "gpt-4"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    QWEN_2_5_CODER = "qwen2.5-coder"


@dataclass
class LLMConfig:
    provider: LLMProvider = LLMProvider.MOCK
    model: LLMModel = LLMModel.GPT_4
    temperature: float = 0.7
    max_tokens: int = 2000


@dataclass
class AILLMResponse:
    content: str
    confidence_score: float = 0.7
    reasoning: str = "mock reasoning"
    tokens_used: int = 0
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AILLMIntegration:
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()

    async def generate_response(
        self, prompt: str, context: Optional[Dict[str, Any]] = None, mode: Optional[str] = None
    ) -> AILLMResponse:
        return AILLMResponse(
            content=prompt,
            confidence_score=0.75,
            reasoning=f"mode={mode or 'default'}",
            tokens_used=min(len(prompt.split()), self.config.max_tokens),
            processing_time=0.01,
            metadata={"prompt": prompt, "context": context or {}, "model": self.config.model.value},
        )
