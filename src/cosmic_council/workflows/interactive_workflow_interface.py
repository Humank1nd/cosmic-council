"""
Interactive Workflow Interface
User-friendly interface for navigating the problem-solving workflow
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from .problem_solving_workflow import ProblemSolvingWorkflow, WorkflowStep, WorkflowStatus
from ..core.core import ProblemStatement, ProblemComplexity

class InteractiveWorkflowInterface:
    """Interactive interface for the problem-solving workflow"""
    
    def __init__(self):
        self.workflow = ProblemSolvingWorkflow()
        self.current_session = None
        self.user_responses = {}
        
    async def start_interactive_session(self):
        """Start an interactive workflow session"""
        print("🌌 Welcome to the Agent Orchestrator Problem-Solving Workflow")
        print("=" * 60)
        print("This guided workflow will help you solve complex problems using")
        print("the Agent Orchestrator's hexagonal methodology.")
        print()
        
        # Start new session
        self.current_session = self.workflow.start_new_session()
        print(f"Session started: {self.current_session.session_id}")
        print()
        
        # Begin workflow
        await self._run_workflow_interactive()
    
    async def _run_workflow_interactive(self):
        """Run the workflow interactively"""
        while self.current_session.status == WorkflowStatus.IN_PROGRESS:
            current_step_info = self.workflow.get_current_step_info()
            
            print(f"\n📍 Current Step: {current_step_info['current_step']}")
            print(f"🎯 {current_step_info['title']}")
            print(f"📝 {current_step_info['description']}")
            
            if current_step_info['enterprise']:
                print(f"🏢 Enterprise: {current_step_info['enterprise']}")
            
            print(f"📊 Progress: {current_step_info['session_progress']['progress_percentage']:.1f}%")
            print()
            
            # Show guidance notes
            if current_step_info['guidance_notes']:
                print("💡 Guidance Notes:")
                for i, note in enumerate(current_step_info['guidance_notes'], 1):
                    print(f"   {i}. {note}")
                print()
            
            # Get user input for this step
            user_inputs = await self._get_user_input_for_step(current_step_info)
            
            if user_inputs is None:  # User chose to exit
                print("Workflow paused. You can resume later.")
                break
            
            # Execute the step
            print(f"\n⚙️  Executing {current_step_info['title']}...")
            result = await self.workflow.execute_current_step(user_inputs)
            
            if "step_completed" in result:
                print(f"✅ {result['step_completed']} completed successfully!")
                print(f"🎯 Confidence Score: {result['confidence_score']:.2f}")
                
                if result.get('next_step'):
                    print(f"➡️  Next: {result['next_step']}")
                else:
                    print("🎉 Workflow completed!")
            else:
                print(f"❌ Step failed: {result.get('error', 'Unknown error')}")
                break
            
            # Show results summary
            if "results" in result:
                await self._show_step_results(result["results"])
            
            print("\n" + "─" * 60)
        
        # Show final summary
        await self._show_final_summary()
    
    async def _get_user_input_for_step(self, step_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get user input for a specific step"""
        step_name = step_info['current_step']
        
        print("📋 Please provide the following information:")
        print("   (Type 'skip' to use default values, 'exit' to quit)")
        print()
        
        user_inputs = {}
        
        if step_name == "problem_definition":
            user_inputs = await self._get_problem_definition_inputs()
        elif step_name == "red_owl_research":
            user_inputs = await self._get_research_inputs()
        elif step_name == "orange_orangutan_planning":
            user_inputs = await self._get_planning_inputs()
        elif step_name == "yellow_honeybee_development":
            user_inputs = await self._get_development_inputs()
        elif step_name == "green_tortoise_resources":
            user_inputs = await self._get_resource_inputs()
        elif step_name == "blue_dolphin_communication":
            user_inputs = await self._get_communication_inputs()
        elif step_name == "purple_elephant_support":
            user_inputs = await self._get_support_inputs()
        elif step_name == "synthesis_and_decision":
            user_inputs = await self._get_synthesis_inputs()
        elif step_name == "implementation_planning":
            user_inputs = await self._get_implementation_inputs()
        elif step_name == "monitoring_and_feedback":
            user_inputs = await self._get_monitoring_inputs()
        
        if user_inputs is None:  # User chose to exit
            return None
        
        return user_inputs
    
    async def _get_problem_definition_inputs(self) -> Optional[Dict[str, Any]]:
        """Get problem definition inputs"""
        inputs = {}
        
        # Problem title
        title = input("📌 Problem Title: ").strip()
        if title.lower() == 'exit':
            return None
        if title.lower() == 'skip':
            title = "Sample Problem"
        inputs['title'] = title
        
        # Problem description
        print("📝 Problem Description (press Enter twice when done):")
        description_lines = []
        while True:
            line = input()
            if line.strip() == '' and description_lines:
                break
            if line.strip().lower() == 'exit':
                return None
            description_lines.append(line)
        inputs['description'] = '\n'.join(description_lines) if description_lines else "No description provided"
        
        # Complexity
        print("\n🎯 Problem Complexity:")
        print("   1. Simple")
        print("   2. Moderate") 
        print("   3. Complex")
        print("   4. Systemic")
        complexity_choice = input("Choose (1-4): ").strip()
        complexity_map = {"1": "simple", "2": "moderate", "3": "complex", "4": "systemic"}
        inputs['complexity'] = complexity_map.get(complexity_choice, "moderate")
        
        # Domain
        domain = input("🏢 Domain/Industry: ").strip()
        if domain.lower() == 'exit':
            return None
        inputs['domain'] = domain if domain else "General"
        
        # Stakeholders
        print("\n👥 Stakeholders (one per line, press Enter twice when done):")
        stakeholders = []
        while True:
            stakeholder = input()
            if stakeholder.strip() == '' and stakeholders:
                break
            if stakeholder.strip().lower() == 'exit':
                return None
            stakeholders.append(stakeholder.strip())
        inputs['stakeholders'] = stakeholders if stakeholders else ["General Stakeholders"]
        
        # Constraints
        print("\n⚠️  Constraints (one per line, press Enter twice when done):")
        constraints = []
        while True:
            constraint = input()
            if constraint.strip() == '' and constraints:
                break
            if constraint.strip().lower() == 'exit':
                return None
            constraints.append(constraint.strip())
        inputs['constraints'] = constraints if constraints else ["No specific constraints"]
        
        # Success criteria
        print("\n🎯 Success Criteria (one per line, press Enter twice when done):")
        criteria = []
        while True:
            criterion = input()
            if criterion.strip() == '' and criteria:
                break
            if criterion.strip().lower() == 'exit':
                return None
            criteria.append(criterion.strip())
        inputs['success_criteria'] = criteria if criteria else ["Problem resolved successfully"]
        
        return inputs
    
    async def _get_research_inputs(self) -> Optional[Dict[str, Any]]:
        """Get research inputs"""
        inputs = {}
        
        print("🔍 Research Questions (one per line, press Enter twice when done):")
        questions = []
        while True:
            question = input()
            if question.strip() == '' and questions:
                break
            if question.strip().lower() == 'exit':
                return None
            questions.append(question.strip())
        inputs['research_questions'] = questions if questions else ["What information is needed?"]
        
        print("\n📊 Data Sources (one per line, press Enter twice when done):")
        sources = []
        while True:
            source = input()
            if source.strip() == '' and sources:
                break
            if source.strip().lower() == 'exit':
                return None
            sources.append(source.strip())
        inputs['data_sources'] = sources if sources else ["Internal data", "External research"]
        
        print("\n👥 Stakeholder Interviews (one per line, press Enter twice when done):")
        interviews = []
        while True:
            interview = input()
            if interview.strip() == '' and interviews:
                break
            if interview.strip().lower() == 'exit':
                return None
            interviews.append(interview.strip())
        inputs['stakeholder_interviews'] = interviews if interviews else ["Key stakeholders"]
        
        return inputs
    
    async def _get_planning_inputs(self) -> Optional[Dict[str, Any]]:
        """Get planning inputs"""
        inputs = {}
        
        print("🎯 Objectives (one per line, press Enter twice when done):")
        objectives = []
        while True:
            objective = input()
            if objective.strip() == '' and objectives:
                break
            if objective.strip().lower() == 'exit':
                return None
            objectives.append(objective.strip())
        inputs['objectives'] = objectives if objectives else ["Achieve project goals"]
        
        timeline = input("\n⏰ Timeline: ").strip()
        if timeline.lower() == 'exit':
            return None
        inputs['timeline'] = timeline if timeline else "6 months"
        
        print("\n💼 Resources (one per line, press Enter twice when done):")
        resources = []
        while True:
            resource = input()
            if resource.strip() == '' and resources:
                break
            if resource.strip().lower() == 'exit':
                return None
            resources.append(resource.strip())
        inputs['resources'] = resources if resources else ["Team members", "Budget", "Technology"]
        
        print("\n⚠️  Risks (one per line, press Enter twice when done):")
        risks = []
        while True:
            risk = input()
            if risk.strip() == '' and risks:
                break
            if risk.strip().lower() == 'exit':
                return None
            risks.append(risk.strip())
        inputs['risks'] = risks if risks else ["Resource constraints", "Timeline pressure"]
        
        return inputs
    
    async def _get_development_inputs(self) -> Optional[Dict[str, Any]]:
        """Get development inputs"""
        inputs = {}
        
        print("💡 Creative Solutions (one per line, press Enter twice when done):")
        solutions = []
        while True:
            solution = input()
            if solution.strip() == '' and solutions:
                break
            if solution.strip().lower() == 'exit':
                return None
            solutions.append(solution.strip())
        inputs['creative_solutions'] = solutions if solutions else ["Innovative approach"]
        
        print("\n🚀 Innovation Approaches (one per line, press Enter twice when done):")
        approaches = []
        while True:
            approach = input()
            if approach.strip() == '' and approaches:
                break
            if approach.strip().lower() == 'exit':
                return None
            approaches.append(approach.strip())
        inputs['innovation_approaches'] = approaches if approaches else ["Technology integration"]
        
        print("\n🧪 Prototype Ideas (one per line, press Enter twice when done):")
        prototypes = []
        while True:
            prototype = input()
            if prototype.strip() == '' and prototypes:
                break
            if prototype.strip().lower() == 'exit':
                return None
            prototypes.append(prototype.strip())
        inputs['prototype_ideas'] = prototypes if prototypes else ["MVP prototype"]
        
        testing = input("\n🧪 Testing Strategy: ").strip()
        if testing.lower() == 'exit':
            return None
        inputs['testing_strategy'] = testing if testing else "Iterative testing with stakeholders"
        
        return inputs
    
    async def _get_resource_inputs(self) -> Optional[Dict[str, Any]]:
        """Get resource inputs"""
        inputs = {}
        
        budget = input("💰 Budget: ").strip()
        if budget.lower() == 'exit':
            return None
        inputs['budget'] = budget if budget else "$100,000"
        
        timeline = input("\n⏰ Timeline: ").strip()
        if timeline.lower() == 'exit':
            return None
        inputs['timeline'] = timeline if timeline else "6 months"
        
        print("\n📦 Resource Requirements (one per line, press Enter twice when done):")
        resources = []
        while True:
            resource = input()
            if resource.strip() == '' and resources:
                break
            if resource.strip().lower() == 'exit':
                return None
            resources.append(resource.strip())
        inputs['resources'] = resources if resources else ["Personnel", "Technology", "Materials"]
        
        print("\n🌱 Sustainability Considerations (one per line, press Enter twice when done):")
        sustainability = []
        while True:
            consideration = input()
            if consideration.strip() == '' and sustainability:
                break
            if consideration.strip().lower() == 'exit':
                return None
            sustainability.append(consideration.strip())
        inputs['sustainability'] = sustainability if sustainability else ["Long-term viability"]
        
        return inputs
    
    async def _get_communication_inputs(self) -> Optional[Dict[str, Any]]:
        """Get communication inputs"""
        inputs = {}
        
        print("💬 Key Messages (one per line, press Enter twice when done):")
        messages = []
        while True:
            message = input()
            if message.strip() == '' and messages:
                break
            if message.strip().lower() == 'exit':
                return None
            messages.append(message.strip())
        inputs['key_messages'] = messages if messages else ["Clear value proposition"]
        
        print("\n🎯 Target Audiences (one per line, press Enter twice when done):")
        audiences = []
        while True:
            audience = input()
            if audience.strip() == '' and audiences:
                break
            if audience.strip().lower() == 'exit':
                return None
            audiences.append(audience.strip())
        inputs['target_audiences'] = audiences if audiences else ["Primary stakeholders"]
        
        print("\n📡 Communication Channels (one per line, press Enter twice when done):")
        channels = []
        while True:
            channel = input()
            if channel.strip() == '' and channels:
                break
            if channel.strip().lower() == 'exit':
                return None
            channels.append(channel.strip())
        inputs['communication_channels'] = channels if channels else ["Email", "Meetings", "Reports"]
        
        engagement = input("\n🤝 Engagement Strategy: ").strip()
        if engagement.lower() == 'exit':
            return None
        inputs['engagement_strategy'] = engagement if engagement else "Regular stakeholder communication"
        
        return inputs
    
    async def _get_support_inputs(self) -> Optional[Dict[str, Any]]:
        """Get support inputs"""
        inputs = {}
        
        print("👥 Stakeholder Impact (one per line, press Enter twice when done):")
        impacts = []
        while True:
            impact = input()
            if impact.strip() == '' and impacts:
                break
            if impact.strip().lower() == 'exit':
                return None
            impacts.append(impact.strip())
        inputs['stakeholder_impact'] = impacts if impacts else ["Positive impact on stakeholders"]
        
        print("\n🛠️  Support Systems (one per line, press Enter twice when done):")
        systems = []
        while True:
            system = input()
            if system.strip() == '' and systems:
                break
            if system.strip().lower() == 'exit':
                return None
            systems.append(system.strip())
        inputs['support_systems'] = systems if systems else ["Help desk", "Training", "Documentation"]
        
        print("\n📝 Feedback Mechanisms (one per line, press Enter twice when done):")
        mechanisms = []
        while True:
            mechanism = input()
            if mechanism.strip() == '' and mechanisms:
                break
            if mechanism.strip().lower() == 'exit':
                return None
            mechanisms.append(mechanism.strip())
        inputs['feedback_mechanisms'] = mechanisms if mechanisms else ["Surveys", "Interviews", "Analytics"]
        
        accessibility = input("\n♿ Accessibility Considerations: ").strip()
        if accessibility.lower() == 'exit':
            return None
        inputs['accessibility'] = accessibility if accessibility else "Ensure inclusive design"
        
        return inputs
    
    async def _get_synthesis_inputs(self) -> Optional[Dict[str, Any]]:
        """Get synthesis inputs"""
        inputs = {}
        
        decision = input("🎯 Final Decision: ").strip()
        if decision.lower() == 'exit':
            return None
        inputs['final_decision'] = decision if decision else "Proceed with recommended approach"
        
        approach = input("\n📋 Selected Approach: ").strip()
        if approach.lower() == 'exit':
            return None
        inputs['approach_selection'] = approach if approach else "Integrated solution approach"
        
        tradeoffs = input("\n⚖️  Key Trade-offs: ").strip()
        if tradeoffs.lower() == 'exit':
            return None
        inputs['trade_offs'] = tradeoffs if tradeoffs else "Balanced approach considering all factors"
        
        return inputs
    
    async def _get_implementation_inputs(self) -> Optional[Dict[str, Any]]:
        """Get implementation inputs"""
        inputs = {}
        
        timeline = input("⏰ Implementation Timeline: ").strip()
        if timeline.lower() == 'exit':
            return None
        inputs['timeline'] = timeline if timeline else "6 months with monthly milestones"
        
        print("\n🎯 Milestones (one per line, press Enter twice when done):")
        milestones = []
        while True:
            milestone = input()
            if milestone.strip() == '' and milestones:
                break
            if milestone.strip().lower() == 'exit':
                return None
            milestones.append(milestone.strip())
        inputs['milestones'] = milestones if milestones else ["Phase 1: Setup", "Phase 2: Implementation", "Phase 3: Launch"]
        
        print("\n👥 Responsibilities (one per line, press Enter twice when done):")
        responsibilities = []
        while True:
            responsibility = input()
            if responsibility.strip() == '' and responsibilities:
                break
            if responsibility.strip().lower() == 'exit':
                return None
            responsibilities.append(responsibility.strip())
        inputs['responsibilities'] = responsibilities if responsibilities else ["Project manager", "Development team", "Stakeholders"]
        
        print("\n📊 Success Metrics (one per line, press Enter twice when done):")
        metrics = []
        while True:
            metric = input()
            if metric.strip() == '' and metrics:
                break
            if metric.strip().lower() == 'exit':
                return None
            metrics.append(metric.strip())
        inputs['success_metrics'] = metrics if metrics else ["Timeline adherence", "Quality standards", "Stakeholder satisfaction"]
        
        return inputs
    
    async def _get_monitoring_inputs(self) -> Optional[Dict[str, Any]]:
        """Get monitoring inputs"""
        inputs = {}
        
        print("📊 Tracking Metrics (one per line, press Enter twice when done):")
        metrics = []
        while True:
            metric = input()
            if metric.strip() == '' and metrics:
                break
            if metric.strip().lower() == 'exit':
                return None
            metrics.append(metric.strip())
        inputs['tracking_metrics'] = metrics if metrics else ["Performance indicators", "User satisfaction", "System reliability"]
        
        print("\n📡 Feedback Channels (one per line, press Enter twice when done):")
        channels = []
        while True:
            channel = input()
            if channel.strip() == '' and channels:
                break
            if channel.strip().lower() == 'exit':
                return None
            channels.append(channel.strip())
        inputs['feedback_channels'] = channels if channels else ["User surveys", "System analytics", "Stakeholder meetings"]
        
        schedule = input("\n📅 Review Schedule: ").strip()
        if schedule.lower() == 'exit':
            return None
        inputs['review_schedule'] = schedule if schedule else "Monthly reviews with quarterly deep dives"
        
        improvement = input("\n🔄 Improvement Process: ").strip()
        if improvement.lower() == 'exit':
            return None
        inputs['improvement_process'] = improvement if improvement else "Continuous improvement based on feedback"
        
        return inputs
    
    async def _show_step_results(self, results: Dict[str, Any]):
        """Show results from a completed step"""
        print("\n📋 Step Results:")
        
        # Show key results based on step type
        if "problem_defined" in results:
            print(f"   ✅ Problem: {results['problem_summary']['title']}")
            print(f"   🎯 Complexity: {results['problem_summary']['complexity']}")
            print(f"   🏢 Domain: {results['problem_summary']['domain']}")
            print(f"   👥 Stakeholders: {results['problem_summary']['stakeholders_count']}")
        
        elif "research_completed" in results:
            print(f"   🔍 Research Scope: {results['research_scope']}")
            print(f"   📊 Knowledge Gaps: {len(results['knowledge_gaps'])} identified")
            print(f"   🧪 Research Methods: {len(results['research_methods'])} selected")
        
        elif "planning_completed" in results:
            print(f"   📋 Planning Complexity: {results['planning_complexity']}")
            print(f"   ⚠️  Risk Factors: {len(results['risk_factors'])} identified")
            print(f"   💼 Resource Requirements: {len(results['resource_requirements'])} categories")
        
        elif "development_completed" in results:
            print(f"   💡 Creative Solutions: {len(results['creative_solutions'])} generated")
            print(f"   🚀 Innovation Approaches: {len(results['innovation_approaches'])} identified")
            print(f"   🧪 Prototype Ideas: {len(results['prototype_ideas'])} developed")
        
        elif "resource_planning_completed" in results:
            print(f"   💰 Budget: {results['budget_allocation']['total_budget']}")
            print(f"   ⏰ Timeline: {results['timeline']}")
            print(f"   📦 Resources: {len(results['resource_requirements'])} categories")
        
        elif "communication_planning_completed" in results:
            print(f"   💬 Key Messages: {len(results['key_messages'])} developed")
            print(f"   🎯 Target Audiences: {len(results['target_audiences'])} identified")
            print(f"   📡 Communication Channels: {len(results['communication_channels'])} selected")
        
        elif "support_planning_completed" in results:
            print(f"   👥 Stakeholder Impact: {len(results['stakeholder_impact'])} considerations")
            print(f"   🛠️  Support Systems: {len(results['support_systems'])} planned")
            print(f"   📝 Feedback Mechanisms: {len(results['feedback_mechanisms'])} established")
        
        elif "synthesis_completed" in results:
            print(f"   🎯 Overall Confidence: {results['synthesis']['overall_confidence']:.2f}")
            print(f"   💡 Key Insights: {len(results['synthesis']['key_insights'])} identified")
            print(f"   📋 Recommended Approach: {results['synthesis']['recommended_approach']}")
        
        elif "implementation_planning_completed" in results:
            print(f"   ⏰ Timeline: {results['implementation_plan']['timeline']}")
            print(f"   🎯 Milestones: {len(results['implementation_plan']['milestones'])} planned")
            print(f"   📊 Success Metrics: {len(results['implementation_plan']['success_metrics'])} defined")
        
        elif "monitoring_setup_completed" in results:
            print(f"   📊 Tracking Metrics: {len(results['monitoring_system']['tracking_metrics'])} established")
            print(f"   📡 Feedback Channels: {len(results['monitoring_system']['feedback_channels'])} set up")
            print(f"   📅 Review Schedule: {results['monitoring_system']['review_schedule']}")
        
        # Show recommendations
        if "recommendations" in results:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(results["recommendations"], 1):
                print(f"   {i}. {rec}")
    
    async def _show_final_summary(self):
        """Show final workflow summary"""
        print("\n" + "=" * 60)
        print("🎉 COSMIC COUNCIL WORKFLOW COMPLETED!")
        print("=" * 60)
        
        summary = self.workflow.get_session_summary()
        
        print(f"📋 Session ID: {summary['session_id']}")
        print(f"⏰ Duration: {summary['total_duration']}")
        print(f"📊 Progress: {summary['progress']['progress_percentage']:.1f}%")
        print()
        
        if summary['problem']:
            print("🎯 Problem Summary:")
            print(f"   Title: {summary['problem']['title']}")
            print(f"   Complexity: {summary['problem']['complexity']}")
            print(f"   Domain: {summary['problem']['domain']}")
            print()
        
        print("📈 Steps Completed:")
        for step, step_summary in summary['steps_summary'].items():
            if step_summary['status'] == 'completed':
                print(f"   ✅ {step}: {step_summary['confidence_score']:.2f} confidence")
            else:
                print(f"   ○ {step}: {step_summary['status']}")
        
        if summary['final_synthesis']:
            print(f"\n🎯 Final Synthesis:")
            synthesis = summary['final_synthesis']
            print(f"   Overall Confidence: {synthesis['overall_confidence']:.2f}")
            print(f"   Key Insights: {len(synthesis['key_insights'])} identified")
            print(f"   Recommended Approach: {synthesis['recommended_approach']}")
        
        print(f"\n💾 Session data saved. You can resume or review this session later.")
        print("Thank you for using the Agent Orchestrator Problem-Solving Workflow! 🌌")

# Demo function
async def demo_interactive_workflow():
    """Demonstrate the interactive workflow interface"""
    interface = InteractiveWorkflowInterface()
    await interface.start_interactive_session()

def main():
    """Main function to start the workflow interface"""
    asyncio.run(demo_interactive_workflow())

if __name__ == "__main__":
    main()
