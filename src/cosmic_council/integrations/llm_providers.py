"""
Concrete LLM Provider Implementations
Provides adapters for common AI model providers (OpenAI, Anthropic, etc.)
"""

import os
import logging
from typing import List, Optional, Dict, Any

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

from .llm_provider import (
    BaseLLMProvider, LLMProviderType, LLMRequest, LLMResponse, LLMMessage
)

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider adapter"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.provider_type = LLMProviderType.OPENAI
        api_key = config.get("api_key") if config else os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required")
        self.client = AsyncOpenAI(api_key=api_key) if AsyncOpenAI else None
        if not self.client:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI API"""
        if not self.validate_request(request):
            raise ValueError("Invalid request")
        
        # Convert messages to OpenAI format
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        model = request.model or self.get_default_model()
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
            stop=request.stop
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            metadata={"provider": "openai", "finish_reason": response.choices[0].finish_reason}
        )
    
    def get_available_models(self) -> List[str]:
        return [
            "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini",
            "gpt-3.5-turbo", "gpt-3.5-turbo-16k"
        ]
    
    def get_default_model(self) -> str:
        return "gpt-4"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider adapter"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.provider_type = LLMProviderType.ANTHROPIC
        api_key = config.get("api_key") if config else os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key required")
        self.client = anthropic.AsyncAnthropic(api_key=api_key) if anthropic else None
        if not self.client:
            raise ImportError("Anthropic package not installed. Install with: pip install anthropic")
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Anthropic API"""
        if not self.validate_request(request):
            raise ValueError("Invalid request")
        
        # Convert messages to Anthropic format
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        model = request.model or self.get_default_model()
        
        response = await self.client.messages.create(
            model=model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens or 4096,
            top_p=request.top_p
        )
        
        # Extract text from content blocks
        content = ""
        if hasattr(response, "content"):
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text
        
        return LLMResponse(
            content=content,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            },
            metadata={"provider": "anthropic"}
        )
    
    def get_available_models(self) -> List[str]:
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    
    def get_default_model(self) -> str:
        return "claude-3-5-sonnet-20241022"


class OllamaProvider(BaseLLMProvider):
    """Ollama local model provider adapter"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.provider_type = LLMProviderType.OLLAMA
        self.base_url = config.get("base_url", "http://localhost:11434") if config else "http://localhost:11434"
        try:
            import httpx
            self.client = httpx.AsyncClient(base_url=self.base_url, timeout=300.0)
        except ImportError:
            raise ImportError("httpx package required for Ollama. Install with: pip install httpx")
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Ollama API"""
        if not self.validate_request(request):
            raise ValueError("Invalid request")
        
        # Convert messages to Ollama format
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        model = request.model or self.get_default_model()
        
        response = await self.client.post(
            "/api/chat",
            json={
                "model": model,
                "messages": messages,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens
                }
            }
        )
        response.raise_for_status()
        data = response.json()
        
        return LLMResponse(
            content=data.get("message", {}).get("content", ""),
            model=model,
            metadata={"provider": "ollama", "base_url": self.base_url}
        )
    
    def get_available_models(self) -> List[str]:
        """Fetch available models from Ollama"""
        try:
            import asyncio
            response = asyncio.run(self.client.get("/api/tags"))
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m.get("name", "") for m in models if m.get("name")]
        except Exception:
            pass
        return ["llama2", "mistral", "codellama", "phi"]
    
    def get_default_model(self) -> str:
        return "llama2"
    
    async def health_check(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = await self.client.get("/api/tags")
            return response.status_code == 200
        except Exception:
            return False


class LocalModelProvider(BaseLLMProvider):
    """
    Generic local model provider for running models locally.
    Supports various local inference servers (vLLM, llama.cpp, etc.)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.provider_type = LLMProviderType.LOCAL
        self.base_url = config.get("base_url", "http://localhost:8000") if config else "http://localhost:8000"
        self.api_format = config.get("api_format", "openai")  # "openai" or "custom"
        try:
            import httpx
            self.client = httpx.AsyncClient(base_url=self.base_url, timeout=300.0)
        except ImportError:
            raise ImportError("httpx package required. Install with: pip install httpx")
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using local model API"""
        if not self.validate_request(request):
            raise ValueError("Invalid request")
        
        if self.api_format == "openai":
            # OpenAI-compatible API
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ]
            
            model = request.model or self.get_default_model()
            
            response = await self.client.post(
                "/v1/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data["model"],
                usage=data.get("usage"),
                metadata={"provider": "local", "api_format": self.api_format}
            )
        else:
            # Custom API format
            raise NotImplementedError("Custom API format not yet implemented")
    
    def get_available_models(self) -> List[str]:
        """Try to fetch available models from local server"""
        try:
            import asyncio
            response = asyncio.run(self.client.get("/v1/models"))
            if response.status_code == 200:
                data = response.json()
                return [m["id"] for m in data.get("data", [])]
        except Exception:
            pass
        return ["local-model"]
    
    def get_default_model(self) -> str:
        return "local-model"
    
    async def health_check(self) -> bool:
        """Check if local model server is running"""
        try:
            response = await self.client.get("/health")
            return response.status_code == 200
        except Exception:
            return False

