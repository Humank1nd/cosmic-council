"""
Supra GPTR Integration for Agent Orchestrator

Connects Agent Orchestrator to the Supra GPTR middleware for:
- Firebase/Vertex AI routing
- Twin Turbo enhanced context
- Hybrid AI + Quantum processing
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import httpx

logger = logging.getLogger("CosmicCouncil.SupraGPTR")


@dataclass
class SupraGPTRConfig:
    """Configuration for Supra GPTR connection."""
    base_url: str = "http://localhost:8005"
    timeout: float = 300.0
    enable_turbo: bool = True
    enable_quantum: bool = False
    default_boost_profile: str = "sport"


class SupraGPTRClient:
    """
    Client for Supra GPTR middleware.

    Routes Agent Orchestrator LLM requests through Supra GPTR for:
    - Intelligent Firebase project routing
    - Twin Turbo context enhancement
    - Telemetry and monitoring
    """

    def __init__(self, config: SupraGPTRConfig = None):
        self.config = config or SupraGPTRConfig()
        self._client: Optional[httpx.AsyncClient] = None
        self._connected = False

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout
            )
        return self._client

    async def connect(self) -> bool:
        """Test connection to Supra GPTR."""
        try:
            client = await self._get_client()
            response = await client.get("/health")
            if response.status_code == 200:
                self._connected = True
                logger.info(f"Connected to Supra GPTR at {self.config.base_url}")
                return True
            else:
                logger.warning(f"Supra GPTR health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"Could not connect to Supra GPTR: {e}")
            return False

    async def complete(
        self,
        messages: List[Dict[str, str]],
        task_type: str = None,
        domain: str = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a completion request through Supra GPTR.

        Args:
            messages: List of message dicts with role/content
            task_type: Task type for model routing (creative_writing, complex_reasoning, etc.)
            domain: Domain for project routing (ai_ml, creative, visualization)
            model: Specific model override
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Response dict with content, model, latency, etc.
        """
        client = await self._get_client()

        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "boost_profile": self.config.default_boost_profile,
            "enable_turbo": self.config.enable_turbo,
            "enable_quantum": self.config.enable_quantum,
        }

        # Add routing hints
        if task_type:
            payload["task_type"] = task_type
        if domain:
            payload["domain"] = domain
        if model:
            payload["model"] = model

        # Merge any additional kwargs
        payload.update(kwargs)

        try:
            response = await client.post("/v1/complete", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Supra GPTR request failed: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Supra GPTR request error: {e}")
            raise

    async def complete_for_council(
        self,
        prompt: str,
        system_prompt: str = None,
        agent_type: str = None,
        problem_domain: str = None
    ) -> str:
        """
        Convenience method for Agent Orchestrator agents.

        Maps council concepts to Supra GPTR routing:
        - Agent type -> task_type
        - Problem domain -> domain
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        # Map agent types to Supra GPTR task types
        task_type_map = {
            "researcher": "architecture_search",
            "analyst": "complex_reasoning",
            "creative": "creative_writing",
            "synthesizer": "complex_reasoning",
            "evaluator": "code_generation",
            "quick": "quick_response",
        }

        # Map problem domains to Supra GPTR domains
        domain_map = {
            "technical": "ai_ml",
            "business": "ai_ml",
            "creative": "creative",
            "visual": "visualization",
            "strategic": "creative",
        }

        task_type = task_type_map.get(agent_type, "complex_reasoning")
        domain = domain_map.get(problem_domain, "ai_ml")

        response = await self.complete(
            messages=messages,
            task_type=task_type,
            domain=domain
        )

        return response.get("content", "")

    async def get_telemetry(self) -> Dict[str, Any]:
        """Get Supra GPTR telemetry data."""
        client = await self._get_client()
        response = await client.get("/telemetry")
        return response.json()

    async def get_firebase_projects(self) -> Dict[str, Any]:
        """Get available Firebase projects."""
        client = await self._get_client()
        response = await client.get("/firebase/projects")
        return response.json()

    async def close(self):
        """Close the client connection."""
        if self._client:
            await self._client.aclose()
            self._client = None
            self._connected = False


# Global client instance
_supra_client: Optional[SupraGPTRClient] = None


def get_supra_client(config: SupraGPTRConfig = None) -> SupraGPTRClient:
    """Get the global Supra GPTR client."""
    global _supra_client
    if _supra_client is None:
        _supra_client = SupraGPTRClient(config)
    return _supra_client


async def init_supra_integration(config: SupraGPTRConfig = None) -> bool:
    """Initialize Supra GPTR integration."""
    client = get_supra_client(config)
    return await client.connect()
