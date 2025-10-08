"""
Interactive Exercise Interface
User-friendly interface for accessing and completing Cosmic Council exercises
"""

import asyncio
from typing import Dict, Any, List, Optional
from interactive_exercises import (
    InteractiveExerciseEngine, FacetIdentificationExercise, 
    SolutionBrainstormingExercise, ActionPlanningExercise,
    ExerciseType, DifficultyLevel, EnterpriseType
)
from src.core.types import ProblemStatement, ProblemComplexity

class InteractiveExerciseInterface:
    """User-friendly interface for interactive exercises"""
    
    def __init__(self):
        self.engine = InteractiveExerciseEngine()
        self.current_exercise = None
        self.current_session = None
    
    async def start_interactive_session(self):
        """Start an interactive exercise session"""
        print("🌌 Cosmic Council Interactive Exercises")
        print("=" * 60)
        print("Welcome to the interactive exercise system!")
        print("Practice the Cosmic Council methodology through hands-on exercises.")
        print()
        
        # Get user information
        user_id = input("Enter your name or user ID: ").strip() or "anonymous_user"
        
        # Start session
        session_id = await self.engine.start_exercise_session(user_id)
        self.current_session = session_id
        
        print(f"✅ Session started: {session_id}")
        print(f"👤 User: {user_id}")
        print()
        
        while True:
            print("\n📚 Exercise Menu:")
            print("1. Facet Identification Exercise")
            print("2. Solution Brainstorming Exercise")
            print("3. Action Planning Exercise")
            print("4. Random Exercise")
            print("5. View Session Progress")
            print("6. View User Progress")
            print("7. Exercise Help & Tips")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-7): ").strip()
            
            if choice == "0":
                await self._show_session_summary()
                print("Thank you for using the Cosmic Council Interactive Exercises! 🌌")
                break
            elif choice == "1":
                await self._run_facet_identification_exercise()
            elif choice == "2":
                await self._run_solution_brainstorming_exercise()
            elif choice == "3":
                await self._run_action_planning_exercise()
            elif choice == "4":
                await self._run_random_exercise()
            elif choice == "5":
                await self._view_session_progress()
            elif choice == "6":
                await self._view_user_progress()
            elif choice == "7":
                await self._show_help_and_tips()
            else:
                print("Invalid choice. Please try again.")
    
    async def _run_facet_identification_exercise(self):
        """Run a facet identification exercise"""
        print("\n🎯 Facet Identification Exercise")
        print("-" * 50)
        print("In this exercise, you'll identify which Cosmic Council enterprise")
        print("facets are most relevant to a given problem scenario.")
        print()
        
        # Get difficulty level
        difficulty = await self._get_difficulty_level()
        
        # Create exercise
        exercise = await self.engine.create_facet_identification_exercise(difficulty)
        self.current_exercise = exercise
        
        print(f"📋 Exercise: {exercise.title}")
        print(f"⏱️  Estimated time: {exercise.estimated_time}")
        print(f"🎯 Difficulty: {exercise.difficulty.value.title()}")
        print()
        
        print("📖 Problem Scenario:")
        print(exercise.problem_scenario)
        print()
        
        print("🏢 The Six Enterprise Facets:")
        facet_descriptions = {
            EnterpriseType.RED_OWL: "Research & Knowledge - Data gathering, analysis, information synthesis",
            EnterpriseType.ORANGE_ORANGUTAN: "Logistics & Planning - Strategic coordination, organization, planning",
            EnterpriseType.YELLOW_HONEYBEE: "Development & Innovation - Creative solutions, technology, innovation",
            EnterpriseType.GREEN_TORTOISE: "Resources & Sustainability - Budget, resources, long-term planning",
            EnterpriseType.BLUE_DOLPHIN: "Communication & Marketing - Stakeholder engagement, messaging, marketing",
            EnterpriseType.PURPLE_ELEPHANT: "Support & Empathy - Human factors, community care, support systems"
        }
        
        for facet, description in facet_descriptions.items():
            print(f"  • {facet.value}: {description}")
        print()
        
        print("📝 Instructions:")
        for instruction in exercise.instructions:
            print(f"  • {instruction}")
        print()
        
        # Get user input
        print("🤔 Your Analysis:")
        selected_facets = []
        reasoning = {}
        
        print("Select the 3-4 most relevant facets (enter numbers, separated by commas):")
        print("1. Red Owl  2. Orange Orangutan  3. Yellow Honeybee")
        print("4. Green Tortoise  5. Blue Dolphin  6. Purple Elephant")
        
        facet_choice = input("Your selection: ").strip()
        
        try:
            facet_numbers = [int(x.strip()) for x in facet_choice.split(",")]
            facet_mapping = {
                1: EnterpriseType.RED_OWL,
                2: EnterpriseType.ORANGE_ORANGUTAN,
                3: EnterpriseType.YELLOW_HONEYBEE,
                4: EnterpriseType.GREEN_TORTOISE,
                5: EnterpriseType.BLUE_DOLPHIN,
                6: EnterpriseType.PURPLE_ELEPHANT
            }
            
            selected_facets = [facet_mapping[num] for num in facet_numbers if num in facet_mapping]
            
            print(f"\nSelected facets: {[f.value for f in selected_facets]}")
            print("\nPlease provide reasoning for each selected facet:")
            
            for facet in selected_facets:
                reason = input(f"Why is {facet.value} relevant? ").strip()
                reasoning[facet.value] = reason
            
        except (ValueError, KeyError):
            print("Invalid input. Please enter numbers separated by commas.")
            return
        
        # Submit answers
        user_answers = {
            "selected_facets": selected_facets,
            "reasoning": reasoning
        }
        
        print("\n🔄 Evaluating your answers...")
        result = await self.engine.execute_facet_identification_exercise(exercise, user_answers)
        
        # Show results
        await self._show_exercise_results(result)
    
    async def _run_solution_brainstorming_exercise(self):
        """Run a solution brainstorming exercise"""
        print("\n💡 Solution Brainstorming Exercise")
        print("-" * 50)
        print("In this exercise, you'll generate creative solutions by considering")
        print("a problem from multiple enterprise perspectives.")
        print()
        
        # Get difficulty level
        difficulty = await self._get_difficulty_level()
        
        # Create exercise
        exercise = await self.engine.create_solution_brainstorming_exercise(difficulty)
        self.current_exercise = exercise
        
        print(f"📋 Exercise: {exercise.title}")
        print(f"⏱️  Estimated time: {exercise.estimated_time}")
        print(f"🎯 Difficulty: {exercise.difficulty.value.title()}")
        print()
        
        print("📖 Problem Statement:")
        print(f"Title: {exercise.problem_statement.title}")
        print(f"Description: {exercise.problem_statement.description}")
        print(f"Domain: {exercise.problem_statement.domain}")
        print(f"Complexity: {exercise.problem_statement.complexity.value}")
        print()
        
        print("🏢 Focus Enterprise Facets:")
        for facet in exercise.focus_facets:
            print(f"  • {facet.value}")
        print()
        
        print("📝 Instructions:")
        for instruction in exercise.instructions:
            print(f"  • {instruction}")
        print()
        
        # Get user input
        print("🤔 Your Brainstorming Session:")
        solutions_by_facet = {}
        
        for facet in exercise.focus_facets:
            print(f"\n💭 Solutions from {facet.value} perspective:")
            print("Enter 3-5 creative solution ideas (one per line, press Enter twice when done):")
            
            solutions = []
            while True:
                solution = input()
                if solution.strip() == '' and solutions:
                    break
                if solution.strip():
                    solutions.append(solution.strip())
            
            solutions_by_facet[facet.value] = solutions
            print(f"Generated {len(solutions)} solutions for {facet.value}")
        
        print("\n🔄 Integration Phase:")
        print("Now combine and synthesize solutions across facets.")
        print("Enter 3 integrated solutions (one per line, press Enter twice when done):")
        
        integrated_solutions = []
        while True:
            solution = input()
            if solution.strip() == '' and integrated_solutions:
                break
            if solution.strip():
                integrated_solutions.append(solution.strip())
        
        print("\n📊 Evaluation Criteria:")
        print("Define criteria for evaluating solutions (one per line, press Enter twice when done):")
        
        evaluation_criteria = []
        while True:
            criterion = input()
            if criterion.strip() == '' and evaluation_criteria:
                break
            if criterion.strip():
                evaluation_criteria.append(criterion.strip())
        
        # Submit answers
        user_answers = {
            "solutions_by_facet": solutions_by_facet,
            "integrated_solutions": integrated_solutions,
            "evaluation_criteria": evaluation_criteria
        }
        
        print("\n🔄 Evaluating your brainstorming session...")
        result = await self.engine.execute_solution_brainstorming_exercise(exercise, user_answers)
        
        # Show results
        await self._show_exercise_results(result)
    
    async def _run_action_planning_exercise(self):
        """Run an action planning exercise"""
        print("\n📋 Action Planning Exercise")
        print("-" * 50)
        print("In this exercise, you'll create a detailed action plan for")
        print("implementing a selected solution.")
        print()
        
        # Get difficulty level
        difficulty = await self._get_difficulty_level()
        
        # Create exercise
        exercise = await self.engine.create_action_planning_exercise(difficulty)
        self.current_exercise = exercise
        
        print(f"📋 Exercise: {exercise.title}")
        print(f"⏱️  Estimated time: {exercise.estimated_time}")
        print(f"🎯 Difficulty: {exercise.difficulty.value.title()}")
        print()
        
        print("📖 Solution Concept:")
        print(exercise.solution_concept)
        print()
        
        print("📅 Timeline:")
        print(exercise.timeline)
        print()
        
        print("📦 Available Resources:")
        for resource in exercise.resources:
            print(f"  • {resource}")
        print()
        
        print("📝 Instructions:")
        for instruction in exercise.instructions:
            print(f"  • {instruction}")
        print()
        
        # Get user input
        print("🤔 Your Action Planning Session:")
        
        print("\n📋 Implementation Phases:")
        print("Break down the solution into major phases (one per line, press Enter twice when done):")
        
        phases = []
        while True:
            phase = input()
            if phase.strip() == '' and phases:
                break
            if phase.strip():
                phases.append(phase.strip())
        
        print("\n⏰ Timeline Details:")
        print("For each phase, specify the timeline (format: Phase Name: Duration):")
        
        timeline = {}
        for phase in phases:
            duration = input(f"Timeline for '{phase}': ").strip()
            if duration:
                timeline[phase] = duration
        
        print("\n📦 Resource Allocation:")
        print("Specify resources needed for each category:")
        
        resources = {}
        for resource_type in exercise.resources:
            allocation = input(f"Resources for {resource_type}: ").strip()
            if allocation:
                resources[resource_type] = allocation
        
        print("\n⚠️  Risk Factors:")
        print("Identify potential risks and challenges (one per line, press Enter twice when done):")
        
        risks = []
        while True:
            risk = input()
            if risk.strip() == '' and risks:
                break
            if risk.strip():
                risks.append(risk.strip())
        
        print("\n📊 Success Metrics:")
        print("Define measurable success criteria (one per line, press Enter twice when done):")
        
        success_metrics = []
        while True:
            metric = input()
            if metric.strip() == '' and success_metrics:
                break
            if metric.strip():
                success_metrics.append(metric.strip())
        
        # Submit answers
        user_answers = {
            "phases": phases,
            "timeline": timeline,
            "resources": resources,
            "risks": risks,
            "success_metrics": success_metrics
        }
        
        print("\n🔄 Evaluating your action plan...")
        result = await self.engine.execute_action_planning_exercise(exercise, user_answers)
        
        # Show results
        await self._show_exercise_results(result)
    
    async def _run_random_exercise(self):
        """Run a random exercise"""
        print("\n🎲 Random Exercise")
        print("-" * 50)
        print("Let's surprise you with a random exercise!")
        print()
        
        exercise_types = [
            ("Facet Identification", self._run_facet_identification_exercise),
            ("Solution Brainstorming", self._run_solution_brainstorming_exercise),
            ("Action Planning", self._run_action_planning_exercise)
        ]
        
        import random
        exercise_name, exercise_func = random.choice(exercise_types)
        
        print(f"🎯 Selected: {exercise_name}")
        print("Starting exercise...")
        print()
        
        await exercise_func()
    
    async def _get_difficulty_level(self) -> DifficultyLevel:
        """Get difficulty level from user"""
        print("🎯 Select Difficulty Level:")
        print("1. Beginner")
        print("2. Intermediate")
        print("3. Advanced")
        print("4. Expert")
        
        choice = input("Enter choice (1-4): ").strip()
        
        difficulty_mapping = {
            "1": DifficultyLevel.BEGINNER,
            "2": DifficultyLevel.INTERMEDIATE,
            "3": DifficultyLevel.ADVANCED,
            "4": DifficultyLevel.EXPERT
        }
        
        return difficulty_mapping.get(choice, DifficultyLevel.INTERMEDIATE)
    
    async def _show_exercise_results(self, result):
        """Show exercise results to user"""
        print("\n" + "=" * 60)
        print("📊 EXERCISE RESULTS")
        print("=" * 60)
        
        print(f"🎯 Score: {result.score:.1f}%")
        print(f"⏱️  Time taken: {result.time_taken:.1f} seconds")
        print(f"📅 Completed: {result.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        print("💬 Feedback:")
        for feedback_item in result.feedback:
            print(f"  • {feedback_item}")
        print()
        
        if result.score >= 80:
            print("🎉 Excellent work! You demonstrated strong understanding of the Cosmic Council methodology.")
        elif result.score >= 60:
            print("👍 Good job! You're making solid progress with the methodology.")
        else:
            print("📚 Keep practicing! Review the feedback and try again.")
        
        print("\nPress Enter to continue...")
        input()
    
    async def _view_session_progress(self):
        """View current session progress"""
        if not self.current_session:
            print("No active session found.")
            return
        
        print("\n📊 SESSION PROGRESS")
        print("-" * 40)
        
        summary = self.engine.get_session_summary(self.current_session)
        
        print(f"Session ID: {summary['session_id']}")
        print(f"User: {summary['user_id']}")
        print(f"Started: {summary['started_at']}")
        print(f"Exercises Completed: {summary['exercises_completed']}")
        print(f"Session Score: {summary['session_score']:.1f}%")
        print(f"Total Time: {summary['total_time']:.1f} seconds")
        print()
        
        if summary['exercises_completed'] > 0:
            print("📋 Exercise History:")
            session = self.engine.exercise_sessions[self.current_session]
            for i, exercise_result in enumerate(session['exercises_completed'], 1):
                print(f"  {i}. Score: {exercise_result.score:.1f}% | Time: {exercise_result.time_taken:.1f}s | Difficulty: {exercise_result.difficulty.value}")
        
        print("\nPress Enter to continue...")
        input()
    
    async def _view_user_progress(self):
        """View user's overall progress"""
        if not self.current_session:
            print("No active session found.")
            return
        
        session = self.engine.exercise_sessions[self.current_session]
        user_id = session['user_id']
        
        print("\n👤 USER PROGRESS")
        print("-" * 40)
        
        progress = self.engine.get_user_progress(user_id)
        
        print(f"User: {progress['user_id']}")
        print(f"Total Exercises: {progress['total_exercises']}")
        print(f"Average Score: {progress['average_score']:.1f}%")
        print(f"Best Score: {progress['best_score']:.1f}%")
        print(f"Total Time: {progress['total_time']:.1f} seconds")
        print()
        
        if progress['exercise_types_completed']:
            print("🎯 Exercise Types Completed:")
            for exercise_type in progress['exercise_types_completed']:
                print(f"  • {exercise_type.title()}")
        
        if progress['recent_activity']:
            print("\n📅 Recent Activity:")
            for activity in progress['recent_activity']:
                print(f"  • {activity}")
        
        print("\nPress Enter to continue...")
        input()
    
    async def _show_help_and_tips(self):
        """Show help and tips for exercises"""
        print("\n📚 EXERCISE HELP & TIPS")
        print("-" * 50)
        
        print("🎯 Facet Identification Exercise:")
        print("  • Read the problem scenario carefully")
        print("  • Consider each enterprise facet's unique perspective")
        print("  • Think about what information, skills, or approaches each facet would bring")
        print("  • Select 3-4 most relevant facets")
        print("  • Provide clear reasoning for your selections")
        print()
        
        print("💡 Solution Brainstorming Exercise:")
        print("  • Think creatively from each enterprise perspective")
        print("  • Generate diverse, innovative solutions")
        print("  • Don't worry about feasibility initially - focus on creativity")
        print("  • Look for ways to combine solutions across facets")
        print("  • Consider both short-term and long-term approaches")
        print()
        
        print("📋 Action Planning Exercise:")
        print("  • Break down the solution into logical phases")
        print("  • Consider dependencies between tasks")
        print("  • Be realistic about timelines and resources")
        print("  • Identify potential risks and mitigation strategies")
        print("  • Define measurable success criteria")
        print()
        
        print("💡 General Tips:")
        print("  • Take your time - there's no rush")
        print("  • Think systematically and comprehensively")
        print("  • Consider multiple perspectives and stakeholders")
        print("  • Practice regularly to improve your skills")
        print("  • Review feedback to learn and improve")
        print()
        
        print("Press Enter to continue...")
        input()
    
    async def _show_session_summary(self):
        """Show final session summary"""
        if not self.current_session:
            return
        
        print("\n" + "=" * 60)
        print("📊 FINAL SESSION SUMMARY")
        print("=" * 60)
        
        summary = self.engine.get_session_summary(self.current_session)
        
        print(f"Session ID: {summary['session_id']}")
        print(f"User: {summary['user_id']}")
        print(f"Exercises Completed: {summary['exercises_completed']}")
        print(f"Session Score: {summary['session_score']:.1f}%")
        print(f"Total Time: {summary['total_time']:.1f} seconds")
        print()
        
        if summary['exercises_completed'] > 0:
            print("🎯 Exercise Summary:")
            session = self.engine.exercise_sessions[self.current_session]
            for i, exercise_result in enumerate(session['exercises_completed'], 1):
                print(f"  {i}. Score: {exercise_result.score:.1f}% | Time: {exercise_result.time_taken:.1f}s")
        
        print("\nThank you for practicing with the Cosmic Council methodology!")
        print("Keep exercising to improve your problem-solving skills! 🚀")

# Demo function
async def demo_interactive_interface():
    """Demonstrate the interactive exercise interface"""
    interface = InteractiveExerciseInterface()
    await interface.start_interactive_session()

if __name__ == "__main__":
    asyncio.run(demo_interactive_interface())
