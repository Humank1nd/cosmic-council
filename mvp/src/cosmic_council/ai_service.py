"""
Cosmic Council AI Service
Real AI integration for intelligent problem solving.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MOCK = "mock"  # For testing without API keys


@dataclass
class AIResponse:
    """Structured AI response."""
    content: str
    confidence: float
    sources: List[str]
    reasoning: str
    provider: str
    model: str
    tokens_used: int
    cost: float


class AIService:
    """Real AI service for intelligent problem solving."""
    
    def __init__(self, provider: AIProvider = AIProvider.MOCK):
        """Initialize the AI service."""
        self.provider = provider
        self.api_key = self._get_api_key()
        self.model = self._get_model()
        
        logger.info(f"🤖 AI Service initialized with provider: {provider.value}")
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment."""
        if self.provider == AIProvider.OPENAI:
            return os.getenv("OPENAI_API_KEY")
        elif self.provider == AIProvider.ANTHROPIC:
            return os.getenv("ANTHROPIC_API_KEY")
        return None
    
    def _get_model(self) -> str:
        """Get the model to use."""
        if self.provider == AIProvider.OPENAI:
            return os.getenv("OPENAI_MODEL", "gpt-4")
        elif self.provider == AIProvider.ANTHROPIC:
            return os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        return "mock-model"
    
    async def generate_response(self, 
                              prompt: str, 
                              context: Dict[str, Any] = None,
                              max_tokens: int = 1000) -> AIResponse:
        """
        Generate an intelligent response using AI.
        
        Args:
            prompt: The prompt to send to the AI
            context: Additional context for the AI
            max_tokens: Maximum tokens to generate
            
        Returns:
            AIResponse with structured data
        """
        try:
            if self.provider == AIProvider.MOCK:
                return self._generate_mock_response(prompt, context)
            elif self.provider == AIProvider.OPENAI:
                return await self._generate_openai_response(prompt, context, max_tokens)
            elif self.provider == AIProvider.ANTHROPIC:
                return await self._generate_anthropic_response(prompt, context, max_tokens)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return self._generate_fallback_response(prompt, str(e))
    
    def _generate_mock_response(self, prompt: str, context: Dict[str, Any] = None) -> AIResponse:
        """Generate a mock response for testing."""
        # This is still a template, but more sophisticated
        enterprise_type = context.get("enterprise_type", "unknown") if context else "unknown"
        
        if "research" in enterprise_type.lower():
            content = f"Based on comprehensive analysis of '{prompt}', I recommend conducting primary research through surveys, interviews, and market analysis. Key areas to investigate include stakeholder needs, competitive landscape, and current best practices."
        elif "planning" in enterprise_type.lower():
            content = f"For '{prompt}', I suggest a phased approach with clear milestones: Phase 1 (Research & Analysis), Phase 2 (Strategy Development), Phase 3 (Implementation), Phase 4 (Monitoring & Optimization). Each phase should have specific deliverables and success metrics."
        elif "development" in enterprise_type.lower():
            content = f"To address '{prompt}', I recommend developing a prototype solution that can be tested and iterated upon. Consider using agile methodologies with regular feedback loops and continuous improvement cycles."
        elif "budget" in enterprise_type.lower():
            content = f"For '{prompt}', I estimate a budget range of $10K-$50K depending on scope. Key cost factors include personnel (60%), tools/technology (25%), and overhead (15%). ROI should be measurable within 6-12 months."
        elif "communication" in enterprise_type.lower():
            content = f"Regarding '{prompt}', I suggest a multi-channel communication strategy targeting key stakeholders. Focus on clear messaging, regular updates, and feedback mechanisms to ensure alignment and engagement."
        elif "support" in enterprise_type.lower():
            content = f"For '{prompt}', I recommend establishing a comprehensive support system including training programs, documentation, feedback collection, and continuous improvement processes."
        else:
            content = f"To address '{prompt}', I recommend a systematic approach involving research, planning, development, resource allocation, communication, and ongoing support."
        
        return AIResponse(
            content=content,
            confidence=0.8,
            sources=["Internal Analysis", "Best Practices Database"],
            reasoning="Generated based on enterprise specialization and problem context",
            provider="mock",
            model="mock-model",
            tokens_used=len(content.split()),
            cost=0.0
        )
    
    async def _generate_openai_response(self, prompt: str, context: Dict[str, Any] = None, max_tokens: int = 1000) -> AIResponse:
        """Generate response using OpenAI API."""
        try:
            import openai
            
            if not self.api_key:
                raise ValueError("OpenAI API key not found")
            
            client = openai.OpenAI(api_key=self.api_key)
            
            # Build the system prompt based on enterprise type
            enterprise_type = context.get("enterprise_type", "general") if context else "general"
            system_prompt = self._build_system_prompt(enterprise_type)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            cost = self._calculate_openai_cost(tokens_used)
            
            return AIResponse(
                content=content,
                confidence=0.9,
                sources=["OpenAI GPT-4"],
                reasoning="Generated using OpenAI GPT-4 with enterprise-specific prompting",
                provider="openai",
                model=self.model,
                tokens_used=tokens_used,
                cost=cost
            )
            
        except ImportError:
            logger.warning("OpenAI library not installed, falling back to mock")
            return self._generate_mock_response(prompt, context)
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._generate_fallback_response(prompt, str(e))
    
    async def _generate_anthropic_response(self, prompt: str, context: Dict[str, Any] = None, max_tokens: int = 1000) -> AIResponse:
        """Generate response using Anthropic API."""
        try:
            import anthropic
            
            if not self.api_key:
                raise ValueError("Anthropic API key not found")
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Build the system prompt
            enterprise_type = context.get("enterprise_type", "general") if context else "general"
            system_prompt = self._build_system_prompt(enterprise_type)
            
            response = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost = self._calculate_anthropic_cost(tokens_used)
            
            return AIResponse(
                content=content,
                confidence=0.9,
                sources=["Anthropic Claude"],
                reasoning="Generated using Anthropic Claude with enterprise-specific prompting",
                provider="anthropic",
                model=self.model,
                tokens_used=tokens_used,
                cost=cost
            )
            
        except ImportError:
            logger.warning("Anthropic library not installed, falling back to mock")
            return self._generate_mock_response(prompt, context)
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return self._generate_fallback_response(prompt, str(e))
    
    def _build_system_prompt(self, enterprise_type: str) -> str:
        """Build a system prompt based on enterprise type."""
        prompts = {
            "research": """You are Red Owl, the Research & Knowledge Gathering specialist. Your role is to conduct comprehensive research and analysis. Provide detailed, evidence-based insights with specific recommendations for investigation areas, data sources, and research methodologies.""",
            
            "planning": """You are Orange Orangutan, the Logistics & Strategic Planning specialist. Your role is to create structured, actionable plans. Provide clear timelines, milestones, dependencies, and resource allocation strategies with specific deliverables and success metrics.""",
            
            "development": """You are Yellow Honeybee, the Development & Innovation specialist. Your role is to create innovative solutions and prototypes. Provide creative, practical approaches with specific development methodologies, testing strategies, and iteration cycles.""",
            
            "budget": """You are Green Tortoise, the Budget & Resource Management specialist. Your role is to provide financial analysis and resource planning. Provide specific cost estimates, budget breakdowns, ROI projections, and resource optimization strategies.""",
            
            "communication": """You are Blue Dolphin, the Market & Communication specialist. Your role is to develop communication strategies and market analysis. Provide specific messaging frameworks, stakeholder engagement plans, and market positioning strategies.""",
            
            "support": """You are Purple Elephant, the Support & Continuous Improvement specialist. Your role is to provide ongoing support and improvement recommendations. Provide specific support frameworks, feedback mechanisms, and continuous improvement processes."""
        }
        
        return prompts.get(enterprise_type.lower(), prompts["research"])
    
    def _calculate_openai_cost(self, tokens: int) -> float:
        """Calculate OpenAI API cost."""
        # Rough estimate: $0.03 per 1K tokens for GPT-4
        return (tokens / 1000) * 0.03
    
    def _calculate_anthropic_cost(self, tokens: int) -> float:
        """Calculate Anthropic API cost."""
        # Rough estimate: $0.015 per 1K tokens for Claude
        return (tokens / 1000) * 0.015
    
    def _generate_fallback_response(self, prompt: str, error: str) -> AIResponse:
        """Generate a fallback response when AI fails."""
        return AIResponse(
            content=f"I apologize, but I encountered an error while processing '{prompt}': {error}. Please try again or contact support.",
            confidence=0.1,
            sources=["Error Handler"],
            reasoning="Fallback response due to AI service failure",
            provider="fallback",
            model="error-handler",
            tokens_used=0,
            cost=0.0
        )
