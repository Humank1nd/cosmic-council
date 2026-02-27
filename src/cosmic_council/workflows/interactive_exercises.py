"""
Interactive Exercises for Agent Orchestrator Learning
Hands-on exercises for facet identification, solution brainstorming, and action planning
"""

import asyncio
import random
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import json

from src.core.types import ProblemStatement, ProblemComplexity, EnterpriseType
from case_study_templates import CaseStudyTemplateLibrary, CaseStudyTemplate

class ExerciseType(Enum):
    """Types of interactive exercises"""
    FACET_IDENTIFICATION = "facet_identification"
    SOLUTION_BRAINSTORMING = "solution_brainstorming"
    ACTION_PLANNING = "action_planning"
    STAKEHOLDER_MAPPING = "stakeholder_mapping"
    CONSTRAINT_ANALYSIS = "constraint_analysis"
    SUCCESS_METRICS = "success_metrics"
    ENTERPRISE_ROLE_PLAY = "enterprise_role_play"
    SCENARIO_ANALYSIS = "scenario_analysis"

class DifficultyLevel(Enum):
    """Exercise difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class ExerciseResult:
    """Result of an exercise completion"""
    exercise_id: str
    user_id: str
    score: float
    time_taken: float
    answers: Dict[str, Any]
    feedback: List[str]
    completed_at: datetime
    difficulty: DifficultyLevel

@dataclass
class Exercise:
    """Base exercise class"""
    id: str
    title: str
    description: str
    exercise_type: ExerciseType
    difficulty: DifficultyLevel
    estimated_time: str
    learning_objectives: List[str]
    instructions: List[str]
    success_criteria: List[str]
    hints: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)

class FacetIdentificationExercise(Exercise):
    """Exercise for identifying which enterprise facets apply to a problem"""
    
    def __init__(self, problem_scenario: str, correct_facets: List[EnterpriseType]):
        super().__init__(
            id=f"facet_id_{random.randint(1000, 9999)}",
            title="Enterprise Facet Identification",
            description="Identify which Agent Orchestrator enterprise facets are most relevant to the given problem scenario.",
            exercise_type=ExerciseType.FACET_IDENTIFICATION,
            difficulty=DifficultyLevel.INTERMEDIATE,
            estimated_time="10-15 minutes",
            learning_objectives=[
                "Understand the six enterprise facets and their roles",
                "Learn to identify which facets apply to different problem types",
                "Develop pattern recognition for problem categorization"
            ],
            instructions=[
                "Read the problem scenario carefully",
                "Consider each of the six enterprise facets:",
                "  • Red Owl (Research & Knowledge)",
                "  • Orange Orangutan (Logistics & Planning)",
                "  • Yellow Honeybee (Development & Innovation)",
                "  • Green Tortoise (Resources & Sustainability)",
                "  • Blue Dolphin (Communication & Marketing)",
                "  • Purple Elephant (Support & Empathy)",
                "Select the 3-4 most relevant facets for this problem",
                "Explain your reasoning for each selection"
            ],
            success_criteria=[
                "Correctly identify primary relevant facets",
                "Provide clear reasoning for selections",
                "Consider multiple perspectives and stakeholders"
            ]
        )
        self.problem_scenario = problem_scenario
        self.correct_facets = correct_facets
        self.facet_descriptions = {
            EnterpriseType.RED_OWL: "Research, data gathering, knowledge analysis, and information synthesis",
            EnterpriseType.ORANGE_ORANGUTAN: "Logistics, planning, organization, and strategic coordination",
            EnterpriseType.YELLOW_HONEYBEE: "Development, innovation, creativity, and solution design",
            EnterpriseType.GREEN_TORTOISE: "Resources, budget, sustainability, and long-term planning",
            EnterpriseType.BLUE_DOLPHIN: "Communication, marketing, stakeholder engagement, and messaging",
            EnterpriseType.PURPLE_ELEPHANT: "Support, empathy, human factors, and community care"
        }

class SolutionBrainstormingExercise(Exercise):
    """Exercise for brainstorming solutions using enterprise perspectives"""
    
    def __init__(self, problem_statement: ProblemStatement, focus_facets: List[EnterpriseType]):
        super().__init__(
            id=f"brainstorm_{random.randint(1000, 9999)}",
            title="Multi-Facet Solution Brainstorming",
            description="Generate creative solutions by considering the problem from multiple enterprise perspectives.",
            exercise_type=ExerciseType.SOLUTION_BRAINSTORMING,
            difficulty=DifficultyLevel.ADVANCED,
            estimated_time="20-30 minutes",
            learning_objectives=[
                "Practice creative problem-solving from multiple perspectives",
                "Learn to generate diverse solution approaches",
                "Develop skills in solution evaluation and prioritization"
            ],
            instructions=[
                "Review the problem statement and constraints",
                "For each selected enterprise facet, brainstorm solutions:",
                "  • Think from that enterprise's unique perspective",
                "  • Consider their specific expertise and concerns",
                "  • Generate 3-5 creative solution ideas per facet",
                "Combine and synthesize solutions across facets",
                "Evaluate solutions based on feasibility and impact",
                "Select top 3 integrated solutions with rationale"
            ],
            success_criteria=[
                "Generate diverse, creative solutions",
                "Consider multiple enterprise perspectives",
                "Provide clear evaluation criteria",
                "Demonstrate synthesis and integration skills"
            ]
        )
        self.problem_statement = problem_statement
        self.focus_facets = focus_facets

class ActionPlanningExercise(Exercise):
    """Exercise for creating detailed action plans"""
    
    def __init__(self, solution_concept: str, timeline: str, resources: List[str]):
        super().__init__(
            id=f"action_plan_{random.randint(1000, 9999)}",
            title="Detailed Action Planning",
            description="Create a comprehensive action plan for implementing a selected solution.",
            exercise_type=ExerciseType.ACTION_PLANNING,
            difficulty=DifficultyLevel.ADVANCED,
            estimated_time="25-35 minutes",
            learning_objectives=[
                "Develop detailed implementation planning skills",
                "Learn to break down complex solutions into actionable steps",
                "Practice resource allocation and timeline management"
            ],
            instructions=[
                "Review the solution concept and requirements",
                "Break down the solution into major phases",
                "For each phase, identify:",
                "  • Specific tasks and deliverables",
                "  • Required resources and skills",
                "  • Dependencies and prerequisites",
                "  • Timeline and milestones",
                "  • Risk factors and mitigation strategies",
                "Create a detailed project timeline",
                "Identify success metrics and checkpoints"
            ],
            success_criteria=[
                "Create detailed, actionable task breakdown",
                "Realistic timeline and resource allocation",
                "Clear dependencies and risk management",
                "Measurable success criteria"
            ]
        )
        self.solution_concept = solution_concept
        self.timeline = timeline
        self.resources = resources

class InteractiveExerciseEngine:
    """Engine for managing and executing interactive exercises"""
    
    def __init__(self):
        self.template_library = CaseStudyTemplateLibrary()
        self.exercise_sessions: Dict[str, Dict[str, Any]] = {}
        self.exercise_results: List[ExerciseResult] = []
        self.current_session = None
    
    async def start_exercise_session(self, user_id: str = "default_user"):
        """Start a new exercise session"""
        session_id = f"session_{random.randint(10000, 99999)}"
        self.current_session = {
            "session_id": session_id,
            "user_id": user_id,
            "started_at": datetime.now(timezone.utc),
            "exercises_completed": [],
            "current_exercise": None,
            "session_score": 0.0
        }
        self.exercise_sessions[session_id] = self.current_session
        return session_id
    
    async def create_facet_identification_exercise(self, difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE) -> FacetIdentificationExercise:
        """Create a facet identification exercise"""
        # Get a random case study template
        templates = self.template_library.list_all_templates()
        template = random.choice(templates)
        
        # Determine correct facets based on the problem
        correct_facets = self._determine_relevant_facets(template.problem_statement)
        
        return FacetIdentificationExercise(
            problem_scenario=template.description,
            correct_facets=correct_facets
        )
    
    async def create_solution_brainstorming_exercise(self, difficulty: DifficultyLevel = DifficultyLevel.ADVANCED) -> SolutionBrainstormingExercise:
        """Create a solution brainstorming exercise"""
        # Get a random case study template
        templates = self.template_library.list_all_templates()
        template = random.choice(templates)
        
        # Select 3-4 relevant facets for brainstorming
        relevant_facets = self._determine_relevant_facets(template.problem_statement)
        focus_facets = relevant_facets[:4] if len(relevant_facets) >= 4 else relevant_facets
        
        return SolutionBrainstormingExercise(
            problem_statement=template.problem_statement,
            focus_facets=focus_facets
        )
    
    async def create_action_planning_exercise(self, difficulty: DifficultyLevel = DifficultyLevel.ADVANCED) -> ActionPlanningExercise:
        """Create an action planning exercise"""
        # Generate a solution concept
        solution_concept = self._generate_solution_concept()
        timeline = "6-12 months"
        resources = ["Personnel", "Technology", "Budget", "External Partners"]
        
        return ActionPlanningExercise(
            solution_concept=solution_concept,
            timeline=timeline,
            resources=resources
        )
    
    def _determine_relevant_facets(self, problem_statement: ProblemStatement) -> List[EnterpriseType]:
        """Determine which facets are most relevant to a problem"""
        facets = []
        
        # Analyze problem characteristics to determine relevant facets
        domain = problem_statement.domain.lower()
        description = problem_statement.description.lower()
        
        # Red Owl - Research and knowledge
        if any(keyword in domain or keyword in description for keyword in 
               ["research", "data", "analysis", "information", "knowledge", "study"]):
            facets.append(EnterpriseType.RED_OWL)
        
        # Orange Orangutan - Logistics and planning
        if any(keyword in domain or keyword in description for keyword in 
               ["planning", "strategy", "logistics", "organization", "coordination", "management"]):
            facets.append(EnterpriseType.ORANGE_ORANGUTAN)
        
        # Yellow Honeybee - Development and innovation
        if any(keyword in domain or keyword in description for keyword in 
               ["development", "innovation", "technology", "creative", "design", "solution"]):
            facets.append(EnterpriseType.YELLOW_HONEYBEE)
        
        # Green Tortoise - Resources and sustainability
        if any(keyword in domain or keyword in description for keyword in 
               ["budget", "resources", "sustainability", "environment", "cost", "financial"]):
            facets.append(EnterpriseType.GREEN_TORTOISE)
        
        # Blue Dolphin - Communication and marketing
        if any(keyword in domain or keyword in description for keyword in 
               ["communication", "marketing", "stakeholder", "engagement", "messaging", "brand"]):
            facets.append(EnterpriseType.BLUE_DOLPHIN)
        
        # Purple Elephant - Support and empathy
        if any(keyword in domain or keyword in description for keyword in 
               ["support", "empathy", "human", "community", "care", "wellbeing", "equity"]):
            facets.append(EnterpriseType.PURPLE_ELEPHANT)
        
        # If no specific facets identified, include common ones
        if not facets:
            facets = [EnterpriseType.RED_OWL, EnterpriseType.ORANGE_ORANGUTAN, 
                     EnterpriseType.YELLOW_HONEYBEE, EnterpriseType.GREEN_TORTOISE]
        
        return facets[:4]  # Limit to 4 facets
    
    def _generate_solution_concept(self) -> str:
        """Generate a solution concept for action planning"""
        concepts = [
            "Implement a comprehensive digital transformation strategy",
            "Develop a multi-stakeholder collaboration platform",
            "Create an innovative customer experience program",
            "Establish a sustainable resource management system",
            "Launch a community engagement and education initiative",
            "Build an AI-powered decision support system",
            "Design a flexible and scalable organizational structure",
            "Implement a data-driven performance monitoring system"
        ]
        return random.choice(concepts)
    
    async def execute_facet_identification_exercise(self, exercise: FacetIdentificationExercise, user_answers: Dict[str, Any]) -> ExerciseResult:
        """Execute and evaluate a facet identification exercise"""
        start_time = datetime.now(timezone.utc)
        
        # Evaluate user answers
        selected_facets = user_answers.get("selected_facets", [])
        reasoning = user_answers.get("reasoning", {})
        
        # Calculate score
        correct_selections = 0
        total_correct = len(exercise.correct_facets)
        
        for facet in selected_facets:
            if facet in exercise.correct_facets:
                correct_selections += 1
        
        score = (correct_selections / max(total_correct, 1)) * 100
        
        # Generate feedback
        feedback = []
        if score >= 80:
            feedback.append("Excellent! You correctly identified the most relevant enterprise facets.")
        elif score >= 60:
            feedback.append("Good job! You identified most of the relevant facets.")
        else:
            feedback.append("Consider reviewing the enterprise facet descriptions and problem characteristics.")
        
        # Specific feedback for each facet
        for facet in exercise.correct_facets:
            if facet in selected_facets:
                feedback.append(f"✓ Correctly identified {facet.value} as relevant")
            else:
                feedback.append(f"✗ Missed {facet.value} - consider: {exercise.facet_descriptions[facet]}")
        
        end_time = datetime.now(timezone.utc)
        time_taken = (end_time - start_time).total_seconds()
        
        result = ExerciseResult(
            exercise_id=exercise.id,
            user_id=self.current_session["user_id"] if self.current_session else "unknown",
            score=score,
            time_taken=time_taken,
            answers=user_answers,
            feedback=feedback,
            completed_at=end_time,
            difficulty=exercise.difficulty
        )
        
        self.exercise_results.append(result)
        if self.current_session:
            self.current_session["exercises_completed"].append(result)
            self.current_session["session_score"] = self._calculate_session_score()
        
        return result
    
    async def execute_solution_brainstorming_exercise(self, exercise: SolutionBrainstormingExercise, user_answers: Dict[str, Any]) -> ExerciseResult:
        """Execute and evaluate a solution brainstorming exercise"""
        start_time = datetime.now(timezone.utc)
        
        # Evaluate user answers
        solutions_by_facet = user_answers.get("solutions_by_facet", {})
        integrated_solutions = user_answers.get("integrated_solutions", [])
        evaluation_criteria = user_answers.get("evaluation_criteria", [])
        
        # Calculate score based on solution quality and diversity
        score = 0.0
        
        # Check if solutions were provided for each facet
        facets_covered = len(solutions_by_facet)
        score += (facets_covered / len(exercise.focus_facets)) * 30
        
        # Check solution diversity and creativity
        total_solutions = sum(len(solutions) for solutions in solutions_by_facet.values())
        if total_solutions >= 12:  # At least 3 per facet for 4 facets
            score += 30
        elif total_solutions >= 8:
            score += 20
        else:
            score += 10
        
        # Check integration quality
        if len(integrated_solutions) >= 3:
            score += 25
        elif len(integrated_solutions) >= 2:
            score += 15
        else:
            score += 5
        
        # Check evaluation criteria
        if len(evaluation_criteria) >= 3:
            score += 15
        else:
            score += 5
        
        # Generate feedback
        feedback = []
        if score >= 80:
            feedback.append("Outstanding brainstorming! You demonstrated excellent creative thinking and synthesis skills.")
        elif score >= 60:
            feedback.append("Good brainstorming session! You generated diverse solutions and showed good integration.")
        else:
            feedback.append("Consider spending more time on each facet and focusing on solution integration.")
        
        feedback.append(f"Generated {total_solutions} solutions across {facets_covered} enterprise facets")
        feedback.append(f"Created {len(integrated_solutions)} integrated solutions")
        feedback.append(f"Defined {len(evaluation_criteria)} evaluation criteria")
        
        end_time = datetime.now(timezone.utc)
        time_taken = (end_time - start_time).total_seconds()
        
        result = ExerciseResult(
            exercise_id=exercise.id,
            user_id=self.current_session["user_id"] if self.current_session else "unknown",
            score=score,
            time_taken=time_taken,
            answers=user_answers,
            feedback=feedback,
            completed_at=end_time,
            difficulty=exercise.difficulty
        )
        
        self.exercise_results.append(result)
        if self.current_session:
            self.current_session["exercises_completed"].append(result)
            self.current_session["session_score"] = self._calculate_session_score()
        
        return result
    
    async def execute_action_planning_exercise(self, exercise: ActionPlanningExercise, user_answers: Dict[str, Any]) -> ExerciseResult:
        """Execute and evaluate an action planning exercise"""
        start_time = datetime.now(timezone.utc)
        
        # Evaluate user answers
        phases = user_answers.get("phases", [])
        timeline = user_answers.get("timeline", {})
        resources = user_answers.get("resources", {})
        risks = user_answers.get("risks", [])
        metrics = user_answers.get("success_metrics", [])
        
        # Calculate score based on planning completeness
        score = 0.0
        
        # Check phase breakdown
        if len(phases) >= 3:
            score += 25
        elif len(phases) >= 2:
            score += 15
        else:
            score += 5
        
        # Check timeline detail
        if timeline and len(timeline) >= 3:
            score += 20
        elif timeline and len(timeline) >= 2:
            score += 10
        else:
            score += 5
        
        # Check resource allocation
        if resources and len(resources) >= 3:
            score += 20
        elif resources and len(resources) >= 2:
            score += 10
        else:
            score += 5
        
        # Check risk management
        if len(risks) >= 3:
            score += 15
        elif len(risks) >= 2:
            score += 10
        else:
            score += 5
        
        # Check success metrics
        if len(metrics) >= 3:
            score += 20
        elif len(metrics) >= 2:
            score += 10
        else:
            score += 5
        
        # Generate feedback
        feedback = []
        if score >= 80:
            feedback.append("Excellent action planning! You created a comprehensive and realistic implementation plan.")
        elif score >= 60:
            feedback.append("Good action planning! Your plan covers the key elements with room for more detail.")
        else:
            feedback.append("Consider adding more detail to your action plan, especially around timeline and resources.")
        
        feedback.append(f"Defined {len(phases)} implementation phases")
        feedback.append(f"Identified {len(risks)} risk factors")
        feedback.append(f"Established {len(metrics)} success metrics")
        
        end_time = datetime.now(timezone.utc)
        time_taken = (end_time - start_time).total_seconds()
        
        result = ExerciseResult(
            exercise_id=exercise.id,
            user_id=self.current_session["user_id"] if self.current_session else "unknown",
            score=score,
            time_taken=time_taken,
            answers=user_answers,
            feedback=feedback,
            completed_at=end_time,
            difficulty=exercise.difficulty
        )
        
        self.exercise_results.append(result)
        if self.current_session:
            self.current_session["exercises_completed"].append(result)
            self.current_session["session_score"] = self._calculate_session_score()
        
        return result
    
    def _calculate_session_score(self) -> float:
        """Calculate overall session score"""
        if not self.current_session or not self.current_session["exercises_completed"]:
            return 0.0
        
        total_score = sum(exercise.score for exercise in self.current_session["exercises_completed"])
        return total_score / len(self.current_session["exercises_completed"])
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of a completed session"""
        session = self.exercise_sessions.get(session_id)
        if not session:
            return {}
        
        return {
            "session_id": session_id,
            "user_id": session["user_id"],
            "started_at": session["started_at"].isoformat(),
            "exercises_completed": len(session["exercises_completed"]),
            "session_score": session["session_score"],
            "exercise_types": [ex.difficulty.value for ex in session["exercises_completed"]],
            "total_time": sum(ex.time_taken for ex in session["exercises_completed"])
        }
    
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's overall progress across all sessions"""
        user_results = [result for result in self.exercise_results if result.user_id == user_id]
        
        if not user_results:
            return {"user_id": user_id, "total_exercises": 0, "average_score": 0.0}
        
        return {
            "user_id": user_id,
            "total_exercises": len(user_results),
            "average_score": sum(result.score for result in user_results) / len(user_results),
            "best_score": max(result.score for result in user_results),
            "total_time": sum(result.time_taken for result in user_results),
            "exercise_types_completed": list(set(result.difficulty.value for result in user_results)),
            "recent_activity": [result.completed_at.isoformat() for result in user_results[-5:]]
        }

# Demo function
async def demo_interactive_exercises():
    """Demonstrate the interactive exercise system"""
    print("🌌 Agent Orchestrator Interactive Exercises")
    print("=" * 60)
    
    # Initialize exercise engine
    engine = InteractiveExerciseEngine()
    
    # Start a session
    session_id = await engine.start_exercise_session("demo_user")
    print(f"📚 Started exercise session: {session_id}")
    print()
    
    # Demo 1: Facet Identification Exercise
    print("🎯 DEMO 1: Facet Identification Exercise")
    print("-" * 50)
    
    facet_exercise = await engine.create_facet_identification_exercise()
    print(f"Exercise: {facet_exercise.title}")
    print(f"Problem Scenario: {facet_exercise.problem_scenario[:100]}...")
    print(f"Correct Facets: {[f.value for f in facet_exercise.correct_facets]}")
    print()
    
    # Simulate user answers
    user_answers = {
        "selected_facets": [EnterpriseType.RED_OWL, EnterpriseType.ORANGE_ORANGUTAN, EnterpriseType.YELLOW_HONEYBEE],
        "reasoning": {
            EnterpriseType.RED_OWL.value: "Need research to understand the problem",
            EnterpriseType.ORANGE_ORANGUTAN.value: "Requires strategic planning and coordination",
            EnterpriseType.YELLOW_HONEYBEE.value: "Innovation and development needed"
        }
    }
    
    result = await engine.execute_facet_identification_exercise(facet_exercise, user_answers)
    print(f"✅ Exercise completed!")
    print(f"Score: {result.score:.1f}%")
    print(f"Time taken: {result.time_taken:.1f} seconds")
    print("Feedback:")
    for feedback_item in result.feedback:
        print(f"  • {feedback_item}")
    print()
    
    # Demo 2: Solution Brainstorming Exercise
    print("💡 DEMO 2: Solution Brainstorming Exercise")
    print("-" * 50)
    
    brainstorm_exercise = await engine.create_solution_brainstorming_exercise()
    print(f"Exercise: {brainstorm_exercise.title}")
    print(f"Problem: {brainstorm_exercise.problem_statement.title}")
    print(f"Focus Facets: {[f.value for f in brainstorm_exercise.focus_facets]}")
    print()
    
    # Simulate user answers
    user_answers = {
        "solutions_by_facet": {
            EnterpriseType.RED_OWL.value: ["Market research", "Data analysis", "Stakeholder interviews"],
            EnterpriseType.ORANGE_ORANGUTAN.value: ["Project planning", "Resource allocation", "Timeline management"],
            EnterpriseType.YELLOW_HONEYBEE.value: ["Innovative solutions", "Technology integration", "Creative approaches"],
            EnterpriseType.GREEN_TORTOISE.value: ["Budget planning", "Sustainability measures", "Resource optimization"]
        },
        "integrated_solutions": [
            "Comprehensive digital transformation with research-backed planning",
            "Sustainable innovation program with stakeholder engagement",
            "Data-driven resource optimization with creative solutions"
        ],
        "evaluation_criteria": ["Feasibility", "Impact", "Cost-effectiveness", "Timeline"]
    }
    
    result = await engine.execute_solution_brainstorming_exercise(brainstorm_exercise, user_answers)
    print(f"✅ Exercise completed!")
    print(f"Score: {result.score:.1f}%")
    print(f"Time taken: {result.time_taken:.1f} seconds")
    print("Feedback:")
    for feedback_item in result.feedback:
        print(f"  • {feedback_item}")
    print()
    
    # Demo 3: Action Planning Exercise
    print("📋 DEMO 3: Action Planning Exercise")
    print("-" * 50)
    
    action_exercise = await engine.create_action_planning_exercise()
    print(f"Exercise: {action_exercise.title}")
    print(f"Solution Concept: {action_exercise.solution_concept}")
    print(f"Timeline: {action_exercise.timeline}")
    print()
    
    # Simulate user answers
    user_answers = {
        "phases": [
            "Phase 1: Research and Planning (Months 1-2)",
            "Phase 2: Development and Testing (Months 3-6)",
            "Phase 3: Implementation and Rollout (Months 7-10)",
            "Phase 4: Monitoring and Optimization (Months 11-12)"
        ],
        "timeline": {
            "Phase 1": "2 months",
            "Phase 2": "4 months",
            "Phase 3": "4 months",
            "Phase 4": "2 months"
        },
        "resources": {
            "Personnel": "Project team of 8-10 people",
            "Technology": "Development tools and infrastructure",
            "Budget": "$500,000 total project budget",
            "External Partners": "Consultants and technology vendors"
        },
        "risks": [
            "Resource constraints affecting timeline",
            "Technology integration challenges",
            "Stakeholder resistance to change"
        ],
        "success_metrics": [
            "Project completion on time and within budget",
            "User adoption rate > 80%",
            "Performance improvement > 30%"
        ]
    }
    
    result = await engine.execute_action_planning_exercise(action_exercise, user_answers)
    print(f"✅ Exercise completed!")
    print(f"Score: {result.score:.1f}%")
    print(f"Time taken: {result.time_taken:.1f} seconds")
    print("Feedback:")
    for feedback_item in result.feedback:
        print(f"  • {feedback_item}")
    print()
    
    # Show session summary
    print("📊 SESSION SUMMARY")
    print("-" * 30)
    summary = engine.get_session_summary(session_id)
    print(f"Session ID: {summary['session_id']}")
    print(f"Exercises Completed: {summary['exercises_completed']}")
    print(f"Session Score: {summary['session_score']:.1f}%")
    print(f"Total Time: {summary['total_time']:.1f} seconds")
    print()
    
    # Show user progress
    print("👤 USER PROGRESS")
    print("-" * 30)
    progress = engine.get_user_progress("demo_user")
    print(f"Total Exercises: {progress['total_exercises']}")
    print(f"Average Score: {progress['average_score']:.1f}%")
    print(f"Best Score: {progress['best_score']:.1f}%")
    print(f"Total Time: {progress['total_time']:.1f} seconds")
    print()
    
    print("✅ Interactive exercise system demonstration completed!")
    print("The system provides hands-on learning experiences for the Agent Orchestrator methodology.")

if __name__ == "__main__":
    asyncio.run(demo_interactive_exercises())
