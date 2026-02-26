"""
Narrative AI System for Agent Orchestrator.

Translates complex, esoteric concepts into digestible, story-driven formats
using AI-powered narrative generation.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json

logger = logging.getLogger(__name__)

@dataclass
class NarrativeOutcome:
    """A story-driven translation of a complex concept."""
    title: str
    story_summary: str
    analogies_used: List[str]
    practical_application: str
    target_audience: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class NarrativeAISystem:
    """
    Narrative AI for enhanced concept accessibility.
    
    Features:
    - Translates technical/esoteric concepts into relatable stories.
    - Tailors complexity based on the user's experience level.
    - Generates visualization prompts for concept grounding.
    """

    def __init__(self, ai_agent: Any):
        self.ai_agent = ai_agent

    async def translate_concept(
        self, 
        concept_name: str, 
        raw_details: Dict[str, Any], 
        audience_level: str = "newcomer"
    ) -> NarrativeOutcome:
        """
        Translates a Cosmic Council concept into a narrative.
        """
        logger.info(f"📖 Generating narrative for concept: {concept_name}")
        
        prompt_context = {
            "concept": concept_name,
            "details": raw_details,
            "audience_level": audience_level,
            "instruction": (
                "Translate the provided esoteric concept into a simple, story-driven "
                "narrative. Use relatable analogies and explain how a regular person "
                "can apply this concept in their daily life. Keep it engaging and inspiring."
            )
        }

        # We use the agent to generate a structured narrative response
        ai_response = await self.ai_agent.generate_response(
            "narrative_translation",
            prompt_context
        )

        # Parse AI response (assumes structured content or follows a template)
        content = ai_response.content
        
        return NarrativeOutcome(
            title=f"The Story of {concept_name}",
            story_summary=self._extract_section(content, "STORY:"),
            analogies_used=self._extract_list(content, "ANALOGIES:"),
            practical_application=self._extract_section(content, "APPLICATION:"),
            target_audience=audience_level
        )

    async def generate_onboarding_experience(self, user_interests: List[str]) -> Dict[str, Any]:
        """
        Creates a dynamic onboarding narrative based on user interests.
        """
        logger.info("👋 Generating dynamic onboarding experience")
        
        prompt_context = {
            "user_interests": user_interests,
            "instruction": (
                "Create a personalized onboarding journey through the Cosmic Council. "
                "Introduce the six totems (ROYGBV) as characters in a collaborative quest "
                "that relates directly to the user's interests. End with a practical first step."
            )
        }

        ai_response = await self.ai_agent.generate_response(
            "onboarding_narrative",
            prompt_context
        )

        return {
            "journey_title": "Your Cosmic Quest Begins",
            "narrative": ai_response.content,
            "initial_step": "Submit your first problem to the Red Owl.",
            "visual_hints": ["Hexagonal glow", "Spirit animal guides"]
        }

    async def generate_adaptive_quiz(self, lesson_content: str, user_level: str) -> Dict[str, Any]:
        """
        Generates an AI-powered quiz to track understanding and adapt explanations.
        """
        logger.info(f"❓ Generating adaptive quiz for level: {user_level}")
        
        prompt_context = {
            "lesson_content": lesson_content,
            "user_level": user_level,
            "instruction": (
                "Generate 3 multiple-choice questions based on the lesson content. "
                "Tailor the difficulty to the user's level. Include correct answers and explanations."
            )
        }

        ai_response = await self.ai_agent.generate_response(
            "quiz_generation",
            prompt_context
        )

        # In a real system, we'd parse this into a structured JSON/Dict
        return {
            "quiz_raw": ai_response.content,
            "level": user_level,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    async def generate_multisensory_prompt(self, totem: str) -> Dict[str, Any]:
        """
        Generates prompts for 3D visualization, audio narration, and video scripts.
        """
        logger.info(f"🎨 Generating multi-sensory prompts for totem: {totem}")
        
        prompt_context = {
            "totem": totem,
            "instruction": (
                "Provide a detailed description for a 3D visualization, a script for "
                "an audio narration, and key visual cues for a video lesson explaining "
                "the role of this totem."
            )
        }

        ai_response = await self.ai_agent.generate_response(
            "multisensory_generation",
            prompt_context
        )

        return {
            "totem": totem,
            "content": ai_response.content,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    async def generate_summary(self, content: str, style: str = "bite-sized") -> Dict[str, Any]:
        """
        AI generates bite-sized summaries of complex topics (Goal 2.2).
        """
        logger.info(f"📝 Generating {style} summary")
        
        prompt_context = {
            "content": content,
            "style": style,
            "instruction": f"Generate a {style} summary. Focus on key takeaways and actionable insights."
        }

        ai_response = await self.ai_agent.generate_response("content_summary", prompt_context)

        return {
            "summary": ai_response.content,
            "style": style,
            "word_count": len(ai_response.content.split()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def handle_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Automated FAQ with conversational NLP (Goal 2.3).
        """
        logger.info(f"💬 Handling conversational query: {query[:50]}")
        
        prompt_context = {
            "query": query,
            "context": context or {},
            "instruction": "Answer the user's question using Cosmic Council principles. Be helpful, concise, and inspiring."
        }

        ai_response = await self.ai_agent.generate_response("user_qa", prompt_context)

        return {
            "query": query,
            "response": ai_response.content,
            "suggested_topics": ["Quantum Entanglement", "ROYGBV Cycle", "Recursive Optimization"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def translate_content(self, content: str, target_language: str) -> Dict[str, Any]:
        """
        Real-time translation for multi-language accessibility (Goal 2.1).
        """
        logger.info(f"🌐 Translating content to {target_language}")
        
        prompt_context = {
            "content": content,
            "target_language": target_language,
            "instruction": f"Translate the following content into {target_language} while maintaining the technical and spiritual nuances."
        }

        ai_response = await self.ai_agent.generate_response("translation", prompt_context)

        return {
            "original_language": "en",
            "target_language": target_language,
            "translated_content": ai_response.content,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def _extract_section(self, content: str, marker: str) -> str:
        """Helper to extract sections from AI text."""
        if marker in content:
            parts = content.split(marker)
            if len(parts) > 1:
                return parts[1].split("\n\n")[0].strip()
        return "Insight pending..."

    def _extract_list(self, content: str, marker: str) -> List[str]:
        """Helper to extract lists from AI text."""
        section = self._extract_section(content, marker)
        if section == "Insight pending...":
            return []
        return [line.strip().lstrip("-•* ") for line in section.split('\n') if line.strip()]
