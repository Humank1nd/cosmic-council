"""
AI-Driven Onboarding System for Cosmic Council.

Manages personalized learning paths, multimedia lessons, and adaptive quizzes
to make the Cosmic Council approachable for all users.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from .narrative_ai import NarrativeAISystem

logger = logging.getLogger(__name__)

@dataclass
class Lesson:
    id: str
    title: str
    content: str
    totem: str
    multisensory_assets: Dict[str, Any]
    quiz: Optional[Dict[str, Any]] = None

class OnboardingManager:
    """
    Manages the three-tiered AI onboarding experience.
    
    Tiers:
    1. Interactive Learning Portal (Pathways)
    2. Multi-Sensory Learning Modules (3D/Audio/Video)
    3. AI-Powered Conversational Mentor (Q&A)
    """

    def __init__(self, narrative_system: NarrativeAISystem):
        self.narrative_system = narrative_system
        self.user_progress: Dict[str, Dict[str, Any]] = {}
        self.learning_paths: Dict[str, List[str]] = {
            "foundational": ["red_owl", "orange_orangutan", "yellow_honeybee", "green_tortoise", "blue_dolphin", "purple_elephant"],
            "quantum": ["zeno_effect", "harmonics", "entanglement"]
        }
        # Achievement definitions
        self.badge_milestones = {
            "First Step": "Complete 1 lesson",
            "Pathfinder": "Complete 3 lessons",
            "Council Scholar": "Complete foundational path",
            "Resonance Master": "Score > 0.9 on any quiz"
        }

    async def initialize_user_journey(self, user_id: str, interests: List[str]) -> Dict[str, Any]:
        """
        Starts a personalized onboarding experience.
        """
        logger.info(f"🚀 Initializing onboarding for user: {user_id}")
        
        onboarding_narrative = await self.narrative_system.generate_onboarding_experience(interests)
        
        self.user_progress[user_id] = {
            "path": "foundational",
            "current_step": 0,
            "completed_lessons": [],
            "quiz_scores": {},
            "badges": [],
            "feedback_history": [],
            "interests": interests,
            "started_at": datetime.now(timezone.utc).isoformat()
        }

        return {
            "user_id": user_id,
            "narrative": onboarding_narrative,
            "path_suggestion": "Foundational Cosmic Council",
            "initial_badges": []
        }

    async def get_next_lesson(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieves the next lesson in the user's tailored pathway.
        """
        progress = self.user_progress.get(user_id)
        if not progress:
            return {"error": "User not found. Please start onboarding."}

        path_steps = self.learning_paths[progress["path"]]
        if progress["current_step"] >= len(path_steps):
            return {
                "message": "Pathway complete! You are now a Cosmic Council Scholar.",
                "achievements": progress["badges"]
            }

        totem = path_steps[progress["current_step"]]
        
        # 1. Translate concept to narrative
        narrative = await self.narrative_system.translate_concept(
            totem, {"type": "lesson_overview"}, "newcomer"
        )

        # 2. Generate multi-sensory prompts
        assets = await self.narrative_system.generate_multisensory_prompt(totem)

        # 3. Generate adaptive quiz
        quiz = await self.narrative_system.generate_adaptive_quiz(narrative.story_summary, "beginner")

        lesson = Lesson(
            id=str(uuid.uuid4()),
            title=narrative.title,
            content=narrative.story_summary,
            totem=totem,
            multisensory_assets=assets,
            quiz=quiz
        )

        return {
            "lesson": {
                "id": lesson.id,
                "title": lesson.title,
                "content": lesson.content,
                "totem": lesson.totem,
                "visual_guide": lesson.multisensory_assets.get("content"),
                "quiz": lesson.quiz
            },
            "progress": {
                "step": progress["current_step"] + 1,
                "total": len(path_steps),
                "badges_earned": len(progress["badges"])
            }
        }

    async def submit_quiz_answer(self, user_id: str, lesson_id: str, score: float) -> Dict[str, Any]:
        """
        Tracks user comprehension and awards badges (Gamification).
        """
        progress = self.user_progress.get(user_id)
        if not progress:
            return {"error": "User not found"}

        progress["quiz_scores"][lesson_id] = score
        progress["current_step"] += 1
        
        new_badges = self._check_badge_eligibility(user_id, score)
        progress["badges"].extend(new_badges)

        # Generate a celebratory message from the AI mentor
        celebration = await self.narrative_system.ai_agent.generate_response(
            "celebration_message",
            {"user_id": user_id, "score": score, "badges": new_badges}
        )

        # Suggest a community discussion based on current totem
        discussion_suggestion = await self.suggest_discussions(user_id)

        return {
            "status": "success",
            "score": score,
            "celebration_message": celebration.content,
            "new_badges": new_badges,
            "discussion_suggestion": discussion_suggestion,
            "survey_request": "How helpful was this lesson? (1-5)",
            "next_step_ready": True
        }

    async def collect_feedback(self, user_id: str, lesson_id: str, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automated feedback collection to refine future lessons (Goal 3.2).
        """
        progress = self.user_progress.get(user_id)
        if progress:
            record = {
                "lesson_id": lesson_id,
                "rating": feedback_data.get("rating"),
                "comments": feedback_data.get("comments"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            progress["feedback_history"].append(record)
            
            # Use AI to analyze if lesson needs refinement
            if record["rating"] and record["rating"] < 3:
                logger.warning(f"⚠️ Low rating for lesson {lesson_id}. Flagging for RSI refinement.")
            
            return {"status": "feedback_received", "message": "Thank you for helping the Council evolve."}
        return {"error": "User not found"}

    async def suggest_discussions(self, user_id: str) -> str:
        """
        AI suggests user-led discussions based on interests (Goal 3.3).
        """
        progress = self.user_progress.get(user_id)
        interests = progress.get("interests", ["General Wisdom"]) if progress else ["General Wisdom"]
        
        prompt_context = {"interests": interests}
        ai_response = await self.narrative_system.ai_agent.generate_response(
            "discussion_suggestion",
            prompt_context
        )
        return ai_response.content

    def _check_badge_eligibility(self, user_id: str, latest_score: float) -> List[str]:
        """Internal logic to award badges based on progress/performance."""
        progress = self.user_progress[user_id]
        earned = []
        
        current_badges = progress["badges"]
        lesson_count = progress["current_step"]
        
        if lesson_count == 1 and "First Step" not in current_badges:
            earned.append("First Step")
        if lesson_count == 3 and "Pathfinder" not in current_badges:
            earned.append("Pathfinder")
        if latest_score >= 0.9 and "Resonance Master" not in current_badges:
            earned.append("Resonance Master")
            
        return earned
