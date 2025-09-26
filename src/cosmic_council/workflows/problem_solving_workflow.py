"""
Step-by-Step Problem-Solving Workflow
Implements the Cosmic Council's hexagon methodology with guided workflows
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

# Import Cosmic Council components
from ..core.core import (
    CosmicCouncil, ProblemStatement, ProblemComplexity, 
    EnterpriseType, CycleStatus
)
from ..agents.working_enhanced_agents import (
    WorkingEnhancedRedOwlAgent, WorkingEnhancedOrangeOrangutanAgent,
    AnalysisDepth
)

logger = logging.getLogger(__name__)

class WorkflowStep(Enum):
    """Steps in the problem-solving workflow"""
    PROBLEM_DEFINITION = "problem_definition"
    RED_OWL_RESEARCH = "red_owl_research"
    ORANGE_ORANGUTAN_PLANNING = "orange_orangutan_planning"
    YELLOW_HONEYBEE_DEVELOPMENT = "yellow_honeybee_development"
    GREEN_TORTOISE_RESOURCES = "green_tortoise_resources"
    BLUE_DOLPHIN_COMMUNICATION = "blue_dolphin_communication"
    PURPLE_ELEPHANT_SUPPORT = "purple_elephant_support"
    SYNTHESIS_AND_DECISION = "synthesis_and_decision"
    IMPLEMENTATION_PLANNING = "implementation_planning"
    MONITORING_AND_FEEDBACK = "monitoring_and_feedback"

class WorkflowStatus(Enum):
    """Status of workflow execution"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"

class UserInteractionType(Enum):
    """Types of user interactions"""
    INPUT_REQUIRED = "input_required"
    CONFIRMATION = "confirmation"
    CHOICE = "choice"
    INFORMATION = "information"
    GUIDANCE = "guidance"

@dataclass
class WorkflowStepData:
    """Data for a workflow step"""
    step: WorkflowStep
    title: str
    description: str
    enterprise: Optional[EnterpriseType] = None
    status: WorkflowStatus = WorkflowStatus.NOT_STARTED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[timedelta] = None
    user_inputs: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    next_steps: List[str] = field(default_factory=list)
    requires_user_input: bool = False
    interaction_type: Optional[UserInteractionType] = None
    guidance_notes: List[str] = field(default_factory=list)

@dataclass
class WorkflowSession:
    """Complete workflow session"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    problem: Optional[ProblemStatement] = None
    steps: Dict[WorkflowStep, WorkflowStepData] = field(default_factory=dict)
    current_step: Optional[WorkflowStep] = None
    status: WorkflowStatus = WorkflowStatus.NOT_STARTED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_duration: Optional[timedelta] = None
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    session_notes: List[str] = field(default_factory=list)
    final_synthesis: Dict[str, Any] = field(default_factory=dict)

class ProblemSolvingWorkflow:
    """Step-by-step problem-solving workflow following hexagon methodology"""
    
    def __init__(self):
        self.council = CosmicCouncil()
        self.enterprise_agents = {
            EnterpriseType.RED_OWL: WorkingEnhancedRedOwlAgent(AnalysisDepth.COMPREHENSIVE),
            EnterpriseType.ORANGE_ORANGUTAN: WorkingEnhancedOrangeOrangutanAgent(AnalysisDepth.COMPREHENSIVE)
        }
        self.current_session: Optional[WorkflowSession] = None
        self.user_interaction_callbacks: List[Callable] = []
        
        # Initialize workflow steps
        self._initialize_workflow_steps()
    
    def _initialize_workflow_steps(self):
        """Initialize all workflow steps with their configurations"""
        self.workflow_steps = {
            WorkflowStep.PROBLEM_DEFINITION: WorkflowStepData(
                step=WorkflowStep.PROBLEM_DEFINITION,
                title="Problem Definition",
                description="Define and clarify the problem to be solved",
                status=WorkflowStatus.NOT_STARTED,
                requires_user_input=True,
                interaction_type=UserInteractionType.INPUT_REQUIRED,
                guidance_notes=[
                    "Clearly define what problem you're trying to solve",
                    "Identify the root cause, not just symptoms",
                    "Consider who is affected by this problem",
                    "Think about what success would look like"
                ]
            ),
            WorkflowStep.RED_OWL_RESEARCH: WorkflowStepData(
                step=WorkflowStep.RED_OWL_RESEARCH,
                title="Red Owl Research & Inquiry",
                description="Gather comprehensive information and conduct research",
                enterprise=EnterpriseType.RED_OWL,
                status=WorkflowStatus.NOT_STARTED,
                requires_user_input=True,
                interaction_type=UserInteractionType.GUIDANCE,
                guidance_notes=[
                    "What information do you need to understand this problem?",
                    "Who are the key stakeholders and what are their perspectives?",
                    "What research has already been done on similar problems?",
                    "What data sources are available and reliable?"
                ]
            ),
            WorkflowStep.ORANGE_ORANGUTAN_PLANNING: WorkflowStepData(
                step=WorkflowStep.ORANGE_ORANGUTAN_PLANNING,
                title="Orange Orangutan Planning & Strategy",
                description="Develop comprehensive planning and strategic approach",
                enterprise=EnterpriseType.ORANGE_ORANGUTAN,
                status=WorkflowStatus.NOT_STARTED,
                requires_user_input=True,
                interaction_type=UserInteractionType.GUIDANCE,
                guidance_notes=[
                    "What are the key objectives and milestones?",
                    "What resources will be needed and when?",
                    "What are the potential risks and how can they be mitigated?",
                    "What is the timeline and what are the critical dependencies?"
                ]
            ),
            WorkflowStep.YELLOW_HONEYBEE_DEVELOPMENT: WorkflowStepData(
                step=WorkflowStep.YELLOW_HONEYBEE_DEVELOPMENT,
                title="Yellow Honeybee Development & Innovation",
                description="Generate creative solutions and develop prototypes",
                enterprise=EnterpriseType.YELLOW_HONEYBEE,
                status=WorkflowStatus.NOT_STARTED,
                requires_user_input=True,
                interaction_type=UserInteractionType.CHOICE,
                guidance_notes=[
                    "What creative approaches could solve this problem?",
                    "What innovative solutions have you considered?",
                    "How can you prototype and test different approaches?",
                    "What constraints limit your creative options?"
                ]
            ),
            WorkflowStep.GREEN_TORTOISE_RESOURCES: WorkflowStepData(
                step=WorkflowStep.GREEN_TORTOISE_RESOURCES,
                title="Green Tortoise Resource Management",
                description="Plan budget, resources, and sustainability",
                enterprise=EnterpriseType.GREEN_TORTOISE,
                status=WorkflowStatus.NOT_STARTED,
                requires_user_input=True,
                interaction_type=UserInteractionType.INPUT_REQUIRED,
                guidance_notes=[
                    "What is your budget and how should it be allocated?",
                    "What human, technical, and material resources are needed?",
                    "How can you ensure long-term sustainability?",
                    "What are the cost-benefit trade-offs?"
                ]
            ),
            WorkflowStep.BLUE_DOLPHIN_COMMUNICATION: WorkflowStepData(
                step=WorkflowStep.BLUE_DOLPHIN_COMMUNICATION,
                title="Blue Dolphin Communication & Marketing",
                description="Develop communication strategy and stakeholder engagement",
                enterprise=EnterpriseType.BLUE_DOLPHIN,
                status=WorkflowStatus.NOT_STARTED,
                requires_user_input=True,
                interaction_type=UserInteractionType.GUIDANCE,
                guidance_notes=[
                    "How will you communicate the solution to stakeholders?",
                    "What are the key messages and value propositions?",
                    "What communication channels will be most effective?",
                    "How will you handle resistance and build support?"
                ]
            ),
            WorkflowStep.PURPLE_ELEPHANT_SUPPORT: WorkflowStepData(
                step=WorkflowStep.PURPLE_ELEPHANT_SUPPORT,
                title="Purple Elephant Support & Empathy",
                description="Ensure human-centered design and support systems",
                enterprise=EnterpriseType.PURPLE_ELEPHANT,
                status=WorkflowStatus.NOT_STARTED,
                requires_user_input=True,
                interaction_type=UserInteractionType.GUIDANCE,
                guidance_notes=[
                    "How will this solution impact people emotionally?",
                    "What support systems will be needed during implementation?",
                    "How can you ensure the solution is accessible and inclusive?",
                    "What feedback mechanisms will you establish?"
                ]
            ),
            WorkflowStep.SYNTHESIS_AND_DECISION: WorkflowStepData(
                step=WorkflowStep.SYNTHESIS_AND_DECISION,
                title="Synthesis & Final Decision",
                description="Synthesize all inputs and make final decision",
                status=WorkflowStatus.NOT_STARTED,
                requires_user_input=True,
                interaction_type=UserInteractionType.CONFIRMATION,
                guidance_notes=[
                    "Review all enterprise inputs and recommendations",
                    "Identify the best overall approach",
                    "Consider trade-offs and compromises",
                    "Make final decision on implementation approach"
                ]
            ),
            WorkflowStep.IMPLEMENTATION_PLANNING: WorkflowStepData(
                step=WorkflowStep.IMPLEMENTATION_PLANNING,
                title="Implementation Planning",
                description="Create detailed implementation plan",
                status=WorkflowStatus.NOT_STARTED,
                requires_user_input=True,
                interaction_type=UserInteractionType.INPUT_REQUIRED,
                guidance_notes=[
                    "Create detailed timeline and milestones",
                    "Assign responsibilities and resources",
                    "Establish success metrics and KPIs",
                    "Plan for monitoring and adjustment"
                ]
            ),
            WorkflowStep.MONITORING_AND_FEEDBACK: WorkflowStepData(
                step=WorkflowStep.MONITORING_AND_FEEDBACK,
                title="Monitoring & Feedback",
                description="Establish monitoring systems and feedback loops",
                status=WorkflowStatus.NOT_STARTED,
                requires_user_input=True,
                interaction_type=UserInteractionType.INFORMATION,
                guidance_notes=[
                    "Set up monitoring and tracking systems",
                    "Establish regular feedback collection",
                    "Plan for continuous improvement",
                    "Document lessons learned"
                ]
            )
        }
    
    def start_new_session(self, problem: ProblemStatement = None) -> WorkflowSession:
        """Start a new workflow session"""
        self.current_session = WorkflowSession()
        
        if problem:
            self.current_session.problem = problem
            self.current_session.status = WorkflowStatus.IN_PROGRESS
            self.current_session.start_time = datetime.utcnow()
            self.current_session.current_step = WorkflowStep.PROBLEM_DEFINITION
        else:
            # Start with problem definition
            self.current_session.status = WorkflowStatus.IN_PROGRESS
            self.current_session.start_time = datetime.utcnow()
            self.current_session.current_step = WorkflowStep.PROBLEM_DEFINITION
        
        # Initialize all steps
        for step_type, step_data in self.workflow_steps.items():
            self.current_session.steps[step_type] = WorkflowStepData(
                step=step_data.step,
                title=step_data.title,
                description=step_data.description,
                enterprise=step_data.enterprise,
                status=WorkflowStatus.NOT_STARTED,
                requires_user_input=step_data.requires_user_input,
                interaction_type=step_data.interaction_type,
                guidance_notes=step_data.guidance_notes.copy()
            )
        
        logger.info(f"Started new workflow session: {self.current_session.session_id}")
        return self.current_session
    
    async def execute_current_step(self, user_inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the current workflow step"""
        if not self.current_session or not self.current_session.current_step:
            raise ValueError("No active workflow session")
        
        current_step = self.current_session.current_step
        step_data = self.current_session.steps[current_step]
        
        # Mark step as in progress
        step_data.status = WorkflowStatus.IN_PROGRESS
        step_data.start_time = datetime.utcnow()
        
        if user_inputs:
            step_data.user_inputs.update(user_inputs)
        
        try:
            # Execute step-specific logic
            if current_step == WorkflowStep.PROBLEM_DEFINITION:
                result = await self._execute_problem_definition(step_data)
            elif current_step == WorkflowStep.RED_OWL_RESEARCH:
                result = await self._execute_red_owl_research(step_data)
            elif current_step == WorkflowStep.ORANGE_ORANGUTAN_PLANNING:
                result = await self._execute_orange_orangutan_planning(step_data)
            elif current_step == WorkflowStep.YELLOW_HONEYBEE_DEVELOPMENT:
                result = await self._execute_yellow_honeybee_development(step_data)
            elif current_step == WorkflowStep.GREEN_TORTOISE_RESOURCES:
                result = await self._execute_green_tortoise_resources(step_data)
            elif current_step == WorkflowStep.BLUE_DOLPHIN_COMMUNICATION:
                result = await self._execute_blue_dolphin_communication(step_data)
            elif current_step == WorkflowStep.PURPLE_ELEPHANT_SUPPORT:
                result = await self._execute_purple_elephant_support(step_data)
            elif current_step == WorkflowStep.SYNTHESIS_AND_DECISION:
                result = await self._execute_synthesis_and_decision(step_data)
            elif current_step == WorkflowStep.IMPLEMENTATION_PLANNING:
                result = await self._execute_implementation_planning(step_data)
            elif current_step == WorkflowStep.MONITORING_AND_FEEDBACK:
                result = await self._execute_monitoring_and_feedback(step_data)
            else:
                raise ValueError(f"Unknown workflow step: {current_step}")
            
            # Update step data
            step_data.results = result
            step_data.status = WorkflowStatus.COMPLETED
            step_data.end_time = datetime.utcnow()
            step_data.duration = step_data.end_time - step_data.start_time
            step_data.confidence_score = result.get("confidence_score", 0.0)
            
            # Determine next step
            next_step = self._determine_next_step(current_step)
            self.current_session.current_step = next_step
            
            if next_step is None:
                # Workflow completed
                self.current_session.status = WorkflowStatus.COMPLETED
                self.current_session.end_time = datetime.utcnow()
                self.current_session.total_duration = self.current_session.end_time - self.current_session.start_time
            
            return {
                "step_completed": current_step.value,
                "results": result,
                "next_step": next_step.value if next_step else None,
                "session_status": self.current_session.status.value,
                "confidence_score": step_data.confidence_score
            }
            
        except Exception as e:
            logger.error(f"Error executing step {current_step}: {e}")
            step_data.status = WorkflowStatus.FAILED
            step_data.end_time = datetime.utcnow()
            if step_data.start_time:
                step_data.duration = step_data.end_time - step_data.start_time
            
            return {
                "step_failed": current_step.value,
                "error": str(e),
                "session_status": self.current_session.status.value
            }
    
    async def _execute_problem_definition(self, step_data: WorkflowStepData) -> Dict[str, Any]:
        """Execute problem definition step"""
        user_inputs = step_data.user_inputs
        
        # Create ProblemStatement from user inputs
        problem = ProblemStatement(
            title=user_inputs.get("title", "Untitled Problem"),
            description=user_inputs.get("description", ""),
            complexity=ProblemComplexity(user_inputs.get("complexity", "moderate")),
            domain=user_inputs.get("domain", ""),
            stakeholders=user_inputs.get("stakeholders", []),
            constraints=user_inputs.get("constraints", {}),
            success_criteria=user_inputs.get("success_criteria", [])
        )
        
        self.current_session.problem = problem
        
        return {
            "problem_defined": True,
            "problem_summary": {
                "title": problem.title,
                "complexity": problem.complexity.value,
                "domain": problem.domain,
                "stakeholders_count": len(problem.stakeholders),
                "constraints": problem.constraints,
                "success_criteria_count": len(problem.success_criteria)
            },
            "confidence_score": 0.8,
            "next_actions": [
                "Proceed to Red Owl research phase",
                "Gather additional problem details if needed"
            ]
        }
    
    async def _execute_red_owl_research(self, step_data: WorkflowStepData) -> Dict[str, Any]:
        """Execute Red Owl research step"""
        if not self.current_session.problem:
            raise ValueError("No problem defined for research")
        
        # Use enhanced Red Owl agent
        red_owl_agent = self.enterprise_agents[EnterpriseType.RED_OWL]
        result = await red_owl_agent.process_problem_enhanced(self.current_session.problem)
        
        # Handle the result properly - it's an EnhancedResult object
        if hasattr(result, 'specialized_analysis'):
            analysis = result.specialized_analysis
        else:
            analysis = result.get("specialized_analysis", {})
        
        return {
            "research_completed": True,
            "research_scope": analysis.get("research_scope", "Comprehensive research"),
            "knowledge_gaps": analysis.get("knowledge_gaps", ["Key information gaps identified"]),
            "research_methods": analysis.get("research_methods", ["Stakeholder interviews", "Data analysis"]),
            "stakeholder_analysis": analysis.get("stakeholder_analysis", {"primary_stakeholders": self.current_session.problem.stakeholders}),
            "confidence_score": getattr(result, 'confidence_score', 0.8),
            "recommendations": getattr(result, 'recommendations', ["Conduct comprehensive research", "Validate findings"]),
            "next_actions": [
                "Proceed to Orange Orangutan planning phase",
                "Address identified knowledge gaps",
                "Validate research findings"
            ]
        }
    
    async def _execute_orange_orangutan_planning(self, step_data: WorkflowStepData) -> Dict[str, Any]:
        """Execute Orange Orangutan planning step"""
        if not self.current_session.problem:
            raise ValueError("No problem defined for planning")
        
        # Use enhanced Orange Orangutan agent
        orange_agent = self.enterprise_agents[EnterpriseType.ORANGE_ORANGUTAN]
        result = await orange_agent.process_problem_enhanced(self.current_session.problem)
        
        # Handle the result properly - it's an EnhancedResult object
        if hasattr(result, 'specialized_analysis'):
            analysis = result.specialized_analysis
        else:
            analysis = result.get("specialized_analysis", {})
        
        return {
            "planning_completed": True,
            "planning_complexity": analysis.get("planning_complexity", "medium"),
            "risk_factors": analysis.get("risk_factors", ["Resource constraints", "Timeline pressure"]),
            "resource_requirements": analysis.get("resource_requirements", {"personnel": "Team members", "budget": "Project budget"}),
            "strategic_plan": analysis.get("strategic_plan", {"objectives": ["Achieve project goals"], "strategies": ["Strategic approach"]}),
            "confidence_score": getattr(result, 'confidence_score', 0.8),
            "recommendations": getattr(result, 'recommendations', ["Develop detailed plan", "Address risks"]),
            "next_actions": [
                "Proceed to Yellow Honeybee development phase",
                "Refine strategic plan based on feedback",
                "Address identified risks"
            ]
        }
    
    async def _execute_yellow_honeybee_development(self, step_data: WorkflowStepData) -> Dict[str, Any]:
        """Execute Yellow Honeybee development step"""
        user_inputs = step_data.user_inputs
        
        # Simulate creative development process
        creative_solutions = user_inputs.get("creative_solutions", [])
        innovation_approaches = user_inputs.get("innovation_approaches", [])
        
        return {
            "development_completed": True,
            "creative_solutions": creative_solutions,
            "innovation_approaches": innovation_approaches,
            "prototype_ideas": user_inputs.get("prototype_ideas", []),
            "testing_strategy": user_inputs.get("testing_strategy", ""),
            "confidence_score": 0.75,
            "recommendations": [
                "Develop prototypes for top solutions",
                "Test solutions with stakeholders",
                "Refine based on feedback"
            ],
            "next_actions": [
                "Proceed to Green Tortoise resource planning",
                "Prioritize solutions for development",
                "Plan prototype testing"
            ]
        }
    
    async def _execute_green_tortoise_resources(self, step_data: WorkflowStepData) -> Dict[str, Any]:
        """Execute Green Tortoise resource planning step"""
        user_inputs = step_data.user_inputs
        
        budget = user_inputs.get("budget", "$100,000")
        timeline = user_inputs.get("timeline", "6 months")
        resources = user_inputs.get("resources", ["Personnel", "Technology", "Materials"])
        
        # Handle budget as string or number
        if isinstance(budget, str):
            budget_value = budget
        else:
            budget_value = f"${budget:,.2f}"
        
        return {
            "resource_planning_completed": True,
            "budget_allocation": {
                "total_budget": budget_value,
                "allocation_breakdown": user_inputs.get("budget_breakdown", {"Personnel": "60%", "Technology": "30%", "Other": "10%"}),
                "contingency": "10% of total budget"
            },
            "timeline": timeline,
            "resource_requirements": resources,
            "sustainability_considerations": user_inputs.get("sustainability", ["Long-term viability", "Environmental impact"]),
            "confidence_score": 0.8,
            "recommendations": [
                "Monitor budget utilization closely",
                "Establish resource tracking systems",
                "Plan for sustainability"
            ],
            "next_actions": [
                "Proceed to Blue Dolphin communication planning",
                "Finalize resource allocation",
                "Set up tracking systems"
            ]
        }
    
    async def _execute_blue_dolphin_communication(self, step_data: WorkflowStepData) -> Dict[str, Any]:
        """Execute Blue Dolphin communication step"""
        user_inputs = step_data.user_inputs
        
        return {
            "communication_planning_completed": True,
            "key_messages": user_inputs.get("key_messages", []),
            "target_audiences": user_inputs.get("target_audiences", []),
            "communication_channels": user_inputs.get("communication_channels", []),
            "engagement_strategy": user_inputs.get("engagement_strategy", ""),
            "brand_alignment": user_inputs.get("brand_alignment", ""),
            "confidence_score": 0.85,
            "recommendations": [
                "Develop communication materials",
                "Train communication team",
                "Monitor stakeholder engagement"
            ],
            "next_actions": [
                "Proceed to Purple Elephant support planning",
                "Create communication materials",
                "Launch stakeholder engagement"
            ]
        }
    
    async def _execute_purple_elephant_support(self, step_data: WorkflowStepData) -> Dict[str, Any]:
        """Execute Purple Elephant support step"""
        user_inputs = step_data.user_inputs
        
        return {
            "support_planning_completed": True,
            "stakeholder_impact": user_inputs.get("stakeholder_impact", {}),
            "support_systems": user_inputs.get("support_systems", []),
            "feedback_mechanisms": user_inputs.get("feedback_mechanisms", []),
            "accessibility_considerations": user_inputs.get("accessibility", []),
            "ethical_implications": user_inputs.get("ethical_implications", []),
            "confidence_score": 0.8,
            "recommendations": [
                "Establish support systems",
                "Train support staff",
                "Monitor stakeholder satisfaction"
            ],
            "next_actions": [
                "Proceed to synthesis and decision phase",
                "Set up support infrastructure",
                "Begin stakeholder preparation"
            ]
        }
    
    async def _execute_synthesis_and_decision(self, step_data: WorkflowStepData) -> Dict[str, Any]:
        """Execute synthesis and decision step"""
        # Gather results from all previous steps
        all_results = {}
        for step_type, step_data in self.current_session.steps.items():
            if step_data.status == WorkflowStatus.COMPLETED:
                all_results[step_type.value] = step_data.results
        
        # Perform synthesis
        synthesis = {
            "overall_confidence": sum(step_data.confidence_score for step_data in self.current_session.steps.values() 
                                    if step_data.status == WorkflowStatus.COMPLETED) / len([s for s in self.current_session.steps.values() 
                                    if s.status == WorkflowStatus.COMPLETED]),
            "key_insights": [],
            "recommended_approach": "",
            "implementation_priorities": [],
            "risk_mitigation": []
        }
        
        # Extract key insights from each enterprise
        for step_type, step_data in self.current_session.steps.items():
            if step_data.status == WorkflowStatus.COMPLETED and step_data.results:
                if "recommendations" in step_data.results:
                    synthesis["key_insights"].extend(step_data.results["recommendations"][:2])
        
        self.current_session.final_synthesis = synthesis
        
        return {
            "synthesis_completed": True,
            "synthesis": synthesis,
            "confidence_score": synthesis["overall_confidence"],
            "recommendations": [
                "Review synthesis with stakeholders",
                "Make final implementation decision",
                "Proceed to implementation planning"
            ],
            "next_actions": [
                "Proceed to implementation planning",
                "Finalize decision and approach",
                "Prepare for implementation"
            ]
        }
    
    async def _execute_implementation_planning(self, step_data: WorkflowStepData) -> Dict[str, Any]:
        """Execute implementation planning step"""
        user_inputs = step_data.user_inputs
        
        implementation_plan = {
            "timeline": user_inputs.get("timeline", ""),
            "milestones": user_inputs.get("milestones", []),
            "responsibilities": user_inputs.get("responsibilities", {}),
            "success_metrics": user_inputs.get("success_metrics", []),
            "monitoring_plan": user_inputs.get("monitoring_plan", ""),
            "risk_management": user_inputs.get("risk_management", {})
        }
        
        return {
            "implementation_planning_completed": True,
            "implementation_plan": implementation_plan,
            "confidence_score": 0.85,
            "recommendations": [
                "Finalize implementation plan",
                "Assign team members",
                "Begin implementation"
            ],
            "next_actions": [
                "Proceed to monitoring and feedback setup",
                "Launch implementation",
                "Begin monitoring"
            ]
        }
    
    async def _execute_monitoring_and_feedback(self, step_data: WorkflowStepData) -> Dict[str, Any]:
        """Execute monitoring and feedback step"""
        user_inputs = step_data.user_inputs
        
        monitoring_system = {
            "tracking_metrics": user_inputs.get("tracking_metrics", []),
            "feedback_channels": user_inputs.get("feedback_channels", []),
            "review_schedule": user_inputs.get("review_schedule", ""),
            "improvement_process": user_inputs.get("improvement_process", "")
        }
        
        return {
            "monitoring_setup_completed": True,
            "monitoring_system": monitoring_system,
            "confidence_score": 0.8,
            "recommendations": [
                "Implement monitoring systems",
                "Begin regular reviews",
                "Establish continuous improvement"
            ],
            "next_actions": [
                "Complete workflow",
                "Begin implementation",
                "Start monitoring"
            ]
        }
    
    def _determine_next_step(self, current_step: WorkflowStep) -> Optional[WorkflowStep]:
        """Determine the next step in the workflow"""
        step_sequence = [
            WorkflowStep.PROBLEM_DEFINITION,
            WorkflowStep.RED_OWL_RESEARCH,
            WorkflowStep.ORANGE_ORANGUTAN_PLANNING,
            WorkflowStep.YELLOW_HONEYBEE_DEVELOPMENT,
            WorkflowStep.GREEN_TORTOISE_RESOURCES,
            WorkflowStep.BLUE_DOLPHIN_COMMUNICATION,
            WorkflowStep.PURPLE_ELEPHANT_SUPPORT,
            WorkflowStep.SYNTHESIS_AND_DECISION,
            WorkflowStep.IMPLEMENTATION_PLANNING,
            WorkflowStep.MONITORING_AND_FEEDBACK
        ]
        
        try:
            current_index = step_sequence.index(current_step)
            if current_index < len(step_sequence) - 1:
                return step_sequence[current_index + 1]
            else:
                return None  # Workflow completed
        except ValueError:
            return None
    
    def get_current_step_info(self) -> Dict[str, Any]:
        """Get information about the current step"""
        if not self.current_session or not self.current_session.current_step:
            return {"error": "No active workflow session"}
        
        current_step = self.current_session.current_step
        step_data = self.current_session.steps[current_step]
        
        return {
            "current_step": current_step.value,
            "title": step_data.title,
            "description": step_data.description,
            "enterprise": step_data.enterprise.value if step_data.enterprise else None,
            "status": step_data.status.value,
            "requires_user_input": step_data.requires_user_input,
            "interaction_type": step_data.interaction_type.value if step_data.interaction_type else None,
            "guidance_notes": step_data.guidance_notes,
            "session_progress": self._calculate_session_progress()
        }
    
    def _calculate_session_progress(self) -> Dict[str, Any]:
        """Calculate overall session progress"""
        if not self.current_session:
            return {"progress_percentage": 0, "completed_steps": 0, "total_steps": 0}
        
        total_steps = len(self.workflow_steps)
        completed_steps = len([s for s in self.current_session.steps.values() 
                              if s.status == WorkflowStatus.COMPLETED])
        
        return {
            "progress_percentage": (completed_steps / total_steps) * 100,
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "current_step_index": list(self.workflow_steps.keys()).index(self.current_session.current_step) + 1 if self.current_session.current_step else 0
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get complete session summary"""
        if not self.current_session:
            return {"error": "No active workflow session"}
        
        return {
            "session_id": self.current_session.session_id,
            "status": self.current_session.status.value,
            "start_time": self.current_session.start_time.isoformat() if self.current_session.start_time else None,
            "end_time": self.current_session.end_time.isoformat() if self.current_session.end_time else None,
            "total_duration": str(self.current_session.total_duration) if self.current_session.total_duration else None,
            "problem": {
                "title": self.current_session.problem.title if self.current_session.problem else None,
                "complexity": self.current_session.problem.complexity.value if self.current_session.problem else None,
                "domain": self.current_session.problem.domain if self.current_session.problem else None
            },
            "progress": self._calculate_session_progress(),
            "steps_summary": {
                step.value: {
                    "status": step_data.status.value,
                    "confidence_score": step_data.confidence_score,
                    "duration": str(step_data.duration) if step_data.duration else None
                }
                for step, step_data in self.current_session.steps.items()
            },
            "final_synthesis": self.current_session.final_synthesis
        }
    
    def add_user_interaction_callback(self, callback: Callable):
        """Add callback for user interactions"""
        self.user_interaction_callbacks.append(callback)
    
    async def request_user_input(self, step_data: WorkflowStepData) -> Dict[str, Any]:
        """Request user input for a step"""
        interaction_request = {
            "step": step_data.step.value,
            "title": step_data.title,
            "description": step_data.description,
            "interaction_type": step_data.interaction_type.value if step_data.interaction_type else None,
            "guidance_notes": step_data.guidance_notes,
            "required_inputs": self._get_required_inputs_for_step(step_data.step)
        }
        
        # Call all registered callbacks
        for callback in self.user_interaction_callbacks:
            await callback(interaction_request)
        
        return interaction_request
    
    def _get_required_inputs_for_step(self, step: WorkflowStep) -> List[str]:
        """Get required inputs for a specific step"""
        input_requirements = {
            WorkflowStep.PROBLEM_DEFINITION: [
                "title", "description", "complexity", "domain", 
                "stakeholders", "constraints", "success_criteria"
            ],
            WorkflowStep.RED_OWL_RESEARCH: [
                "research_questions", "data_sources", "stakeholder_interviews"
            ],
            WorkflowStep.ORANGE_ORANGUTAN_PLANNING: [
                "objectives", "timeline", "resources", "risks"
            ],
            WorkflowStep.YELLOW_HONEYBEE_DEVELOPMENT: [
                "creative_solutions", "innovation_approaches", "prototype_ideas"
            ],
            WorkflowStep.GREEN_TORTOISE_RESOURCES: [
                "budget", "timeline", "resources", "sustainability"
            ],
            WorkflowStep.BLUE_DOLPHIN_COMMUNICATION: [
                "key_messages", "target_audiences", "communication_channels"
            ],
            WorkflowStep.PURPLE_ELEPHANT_SUPPORT: [
                "stakeholder_impact", "support_systems", "feedback_mechanisms"
            ],
            WorkflowStep.SYNTHESIS_AND_DECISION: [
                "final_decision", "approach_selection", "trade_offs"
            ],
            WorkflowStep.IMPLEMENTATION_PLANNING: [
                "timeline", "milestones", "responsibilities", "success_metrics"
            ],
            WorkflowStep.MONITORING_AND_FEEDBACK: [
                "tracking_metrics", "feedback_channels", "review_schedule"
            ]
        }
        
        return input_requirements.get(step, [])

# Demo function
async def demo_workflow():
    """Demonstrate the problem-solving workflow"""
    print("🌌 Cosmic Council Problem-Solving Workflow Demo")
    print("=" * 60)
    
    # Create workflow instance
    workflow = ProblemSolvingWorkflow()
    
    # Start new session
    session = workflow.start_new_session()
    print(f"Started workflow session: {session.session_id}")
    
    # Simulate problem definition
    problem_inputs = {
        "title": "AI-Powered Customer Service Transformation",
        "description": "Transform customer service operations using AI and automation while maintaining human touch and improving customer satisfaction.",
        "complexity": "complex",
        "domain": "Customer Service & AI Technology",
        "stakeholders": ["Customer Service Team", "IT Department", "Customers", "Management"],
        "constraints": {"budget": "$1M", "timeline": "12 months", "compliance": "GDPR required"},
        "success_criteria": ["50% reduction in response time", "90% customer satisfaction", "Cost reduction of 30%"]
    }
    
    # Execute problem definition step
    print("\n1. Problem Definition Step")
    result = await workflow.execute_current_step(problem_inputs)
    print(f"   Status: {result['step_completed']}")
    print(f"   Confidence: {result['confidence_score']:.2f}")
    print(f"   Next Step: {result['next_step']}")
    
    # Execute Red Owl research step
    print("\n2. Red Owl Research Step")
    research_inputs = {
        "research_questions": ["What are current pain points?", "What AI solutions exist?"],
        "data_sources": ["Customer feedback", "Industry reports", "Technical documentation"],
        "stakeholder_interviews": ["Customer service team", "IT department", "Customers"]
    }
    result = await workflow.execute_current_step(research_inputs)
    print(f"   Status: {result['step_completed']}")
    print(f"   Confidence: {result['confidence_score']:.2f}")
    print(f"   Research Scope: {result['results']['research_scope']}")
    
    # Execute Orange Orangutan planning step
    print("\n3. Orange Orangutan Planning Step")
    planning_inputs = {
        "objectives": ["Implement AI chatbot", "Improve response times", "Maintain quality"],
        "timeline": "12 months with quarterly milestones",
        "resources": ["AI development team", "Customer service training", "Technology infrastructure"],
        "risks": ["Technical complexity", "User adoption", "Data privacy"]
    }
    result = await workflow.execute_current_step(planning_inputs)
    print(f"   Status: {result['step_completed']}")
    print(f"   Confidence: {result['confidence_score']:.2f}")
    print(f"   Planning Complexity: {result['results']['planning_complexity']}")
    
    # Get session summary
    print("\n" + "=" * 60)
    print("Workflow Session Summary:")
    summary = workflow.get_session_summary()
    print(f"Session ID: {summary['session_id']}")
    print(f"Status: {summary['status']}")
    print(f"Progress: {summary['progress']['progress_percentage']:.1f}%")
    print(f"Completed Steps: {summary['progress']['completed_steps']}/{summary['progress']['total_steps']}")
    
    print("\nSteps Summary:")
    for step, step_summary in summary['steps_summary'].items():
        if step_summary['status'] == 'completed':
            print(f"  ✓ {step}: {step_summary['confidence_score']:.2f} confidence")
        else:
            print(f"  ○ {step}: {step_summary['status']}")

if __name__ == "__main__":
    asyncio.run(demo_workflow())
