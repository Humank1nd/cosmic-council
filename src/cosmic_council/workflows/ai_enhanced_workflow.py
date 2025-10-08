"""
AI-Enhanced Problem-Solving Workflow
Integrates AI/LLM capabilities with the Cosmic Council workflow system
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from ..core.core import ProblemStatement, ProblemComplexity, EnterpriseType
from .problem_solving_workflow import ProblemSolvingWorkflow, WorkflowStepData, WorkflowSession
from ..agents.unified_ai_agent_system import LLMConfig, LLMProvider, LLMModel, UnifiedCosmicCouncilAgent, AgentType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIWorkflowConfig:
    """Configuration for AI-enhanced workflow"""
    llm_config: LLMConfig
    enable_ai_enhancement: bool = True
    ai_confidence_threshold: float = 0.7
    fallback_to_standard: bool = True
    enable_conversation_memory: bool = True
    max_conversation_history: int = 10

@dataclass
class AIWorkflowStepData(WorkflowStepData):
    """Enhanced workflow step data with AI capabilities"""
    ai_enhanced: bool = False
    ai_confidence: float = 0.0
    ai_reasoning: str = ""
    ai_metadata: Dict[str, Any] = field(default_factory=dict)
    conversation_context: Optional[str] = None

@dataclass
class AIWorkflowSession(WorkflowSession):
    """Enhanced workflow session with AI capabilities"""
    ai_config: Optional[AIWorkflowConfig] = None
    ai_integration: Optional[UnifiedCosmicCouncilAgent] = None
    conversation_id: str = ""
    ai_enhanced_steps: List[str] = field(default_factory=list)
    ai_insights: Dict[str, Any] = field(default_factory=dict)
    ai_recommendations: List[str] = field(default_factory=list)

class AIEnhancedProblemSolvingWorkflow(ProblemSolvingWorkflow):
    """AI-enhanced problem-solving workflow"""
    
    def __init__(self, ai_config: AIWorkflowConfig):
        super().__init__()
        self.ai_config = ai_config
        self.ai_integration = UnifiedCosmicCouncilAgent(AgentType.RED_OWL)
        self.ai_enhanced_agents: Dict[EnterpriseType, UnifiedCosmicCouncilAgent] = {}
        self._initialize_ai_enhanced_agents()
    
    def _initialize_ai_enhanced_agents(self):
        """Initialize AI-enhanced enterprise agents"""
        # Map EnterpriseType to AgentType
        enterprise_to_agent = {
            EnterpriseType.RED_OWL: AgentType.RED_OWL,
            EnterpriseType.ORANGE_ORANGUTAN: AgentType.ORANGE_ORANGUTAN,
            EnterpriseType.YELLOW_HONEYBEE: AgentType.YELLOW_HONEYBEE,
            EnterpriseType.GREEN_TORTOISE: AgentType.GREEN_TORTOISE,
            EnterpriseType.BLUE_DOLPHIN: AgentType.BLUE_DOLPHIN,
            EnterpriseType.PURPLE_ELEPHANT: AgentType.PURPLE_ELEPHANT
        }
        
        for enterprise_type in EnterpriseType:
            agent_type = enterprise_to_agent[enterprise_type]
            self.ai_enhanced_agents[enterprise_type] = UnifiedCosmicCouncilAgent(agent_type)
    
    async def start_ai_enhanced_session(self, problem: ProblemStatement, 
                                      user_id: str = "default_user") -> AIWorkflowSession:
        """Start an AI-enhanced workflow session"""
        # Create conversation ID for AI context
        conversation_id = self.ai_integration.create_conversation()
        
        # Create AI-enhanced session
        session = AIWorkflowSession(
            session_id=str(uuid.uuid4()),
            problem=problem,
            start_time=datetime.utcnow(),
            ai_config=self.ai_config,
            ai_integration=self.ai_integration,
            conversation_id=conversation_id
        )
        
        self.current_session = session
        
        # Generate AI-powered problem analysis
        await self._generate_ai_problem_analysis(problem, conversation_id)
        
        logger.info(f"Started AI-enhanced workflow session: {session.session_id}")
        return session
    
    async def _generate_ai_problem_analysis(self, problem: ProblemStatement, conversation_id: str):
        """Generate AI-powered problem analysis"""
        try:
            # Use Red Owl for initial problem analysis
            red_owl_agent = self.ai_enhanced_agents[EnterpriseType.RED_OWL]
            
            # Prepare context for AI analysis
            context = {
                "problem_title": problem.title,
                "problem_description": problem.description,
                "problem_domain": problem.domain,
                "problem_complexity": problem.complexity.value,
                "stakeholders": ", ".join(problem.stakeholders),
                "constraints": json.dumps(problem.constraints),
                "success_criteria": ", ".join(problem.success_criteria),
                "analysis_type": "initial_problem_analysis"
            }
            
            # Generate AI response
            ai_response = await self.ai_integration.generate_response(
                "red_owl_research_analysis", context, conversation_id
            )
            
            # Store AI insights in session
            if self.current_session:
                self.current_session.ai_insights["initial_analysis"] = {
                    "content": ai_response.content,
                    "confidence": ai_response.confidence_score,
                    "reasoning": ai_response.reasoning,
                    "metadata": ai_response.metadata
                }
                
                # Extract key insights for workflow guidance
                self._extract_workflow_insights(ai_response.content)
            
        except Exception as e:
            logger.error(f"Error generating AI problem analysis: {str(e)}")
    
    def _extract_workflow_insights(self, ai_content: str):
        """Extract insights from AI content to guide workflow"""
        if not self.current_session:
            return
        
        # Extract key insights (simplified approach)
        insights = {
            "complexity_assessment": "complex" if "complex" in ai_content.lower() else "moderate",
            "key_focus_areas": [],
            "recommended_approach": "systematic",
            "critical_success_factors": []
        }
        
        # Parse content for insights (this would be more sophisticated in practice)
        lines = ai_content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                clean_line = line.lstrip('-• ').strip()
                if clean_line:
                    insights["key_focus_areas"].append(clean_line)
        
        self.current_session.ai_insights["workflow_guidance"] = insights
    
    async def execute_ai_enhanced_step(self, step_data: AIWorkflowStepData) -> Dict[str, Any]:
        """Execute a workflow step with AI enhancement"""
        if not self.current_session:
            raise ValueError("No active session")
        
        try:
            # Determine if AI enhancement should be used
            use_ai = (self.ai_config.enable_ai_enhancement and 
                     step_data.ai_confidence_threshold <= self.ai_config.ai_confidence_threshold)
            
            if use_ai:
                # Execute with AI enhancement
                result = await self._execute_ai_enhanced_step(step_data)
                step_data.ai_enhanced = True
            else:
                # Execute standard step
                result = await self._execute_standard_step(step_data)
                step_data.ai_enhanced = False
            
            # Store step data
            self.current_session.steps_completed.append(step_data)
            if step_data.ai_enhanced:
                self.current_session.ai_enhanced_steps.append(step_data.step_name)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing AI-enhanced step: {str(e)}")
            if self.ai_config.fallback_to_standard:
                # Fallback to standard execution
                return await self._execute_standard_step(step_data)
            else:
                raise
    
    async def _execute_ai_enhanced_step(self, step_data: AIWorkflowStepData) -> Dict[str, Any]:
        """Execute step with AI enhancement"""
        step_name = step_data.step_name
        
        # Get AI-enhanced agent for the step
        enterprise_mapping = {
            "red_owl_research": EnterpriseType.RED_OWL,
            "orange_orangutan_planning": EnterpriseType.ORANGE_ORANGUTAN,
            "yellow_honeybee_development": EnterpriseType.YELLOW_HONEYBEE,
            "green_tortoise_resources": EnterpriseType.GREEN_TORTOISE,
            "blue_dolphin_communication": EnterpriseType.BLUE_DOLPHIN,
            "purple_elephant_support": EnterpriseType.PURPLE_ELEPHANT
        }
        
        enterprise_type = enterprise_mapping.get(step_name)
        if not enterprise_type:
            # Fallback to standard execution
            return await self._execute_standard_step(step_data)
        
        # Get AI-enhanced agent
        ai_agent = self.ai_enhanced_agents[enterprise_type]
        
        # Prepare additional context from previous steps
        additional_context = self._prepare_step_context(step_data)
        
        # Process with AI
        ai_result = await ai_agent.process_problem_with_ai(
            self.current_session.problem, additional_context
        )
        
        # Convert AI result to workflow format
        result = self._convert_ai_result_to_workflow_format(ai_result, step_name)
        
        # Store AI metadata
        step_data.ai_confidence = ai_result.confidence_score
        step_data.ai_reasoning = ai_result.reasoning
        step_data.ai_metadata = ai_result.metadata
        
        return result
    
    async def _execute_standard_step(self, step_data: AIWorkflowStepData) -> Dict[str, Any]:
        """Execute step using standard workflow"""
        # Use the parent class method
        return await self.execute_current_step(step_data.user_inputs)
    
    def _prepare_step_context(self, step_data: AIWorkflowStepData) -> Dict[str, Any]:
        """Prepare context for AI processing based on previous steps"""
        context = {
            "user_inputs": step_data.user_inputs,
            "step_name": step_data.step_name,
            "previous_results": {}
        }
        
        # Add results from previous steps
        for completed_step in self.current_session.steps_completed:
            if completed_step.step_name != step_data.step_name:
                context["previous_results"][completed_step.step_name] = completed_step.results
        
        # Add AI insights from previous steps
        if hasattr(self.current_session, 'ai_insights'):
            context["ai_insights"] = self.current_session.ai_insights
        
        return context
    
    def _convert_ai_result_to_workflow_format(self, ai_result, step_name: str) -> Dict[str, Any]:
        """Convert AI result to workflow step format"""
        # Base result structure
        result = {
            "step_completed": True,
            "confidence_score": ai_result.confidence_score,
            "ai_enhanced": True,
            "ai_reasoning": ai_result.reasoning,
            "ai_metadata": ai_result.metadata
        }
        
        # Add step-specific results based on enterprise type
        specialized_analysis = ai_result.specialized_analysis
        
        if step_name == "red_owl_research":
            result.update({
                "research_completed": True,
                "research_scope": specialized_analysis.get("research_scope", "Comprehensive research"),
                "knowledge_gaps": specialized_analysis.get("knowledge_gaps", ["Key information gaps identified"]),
                "research_methods": specialized_analysis.get("research_methods", ["Stakeholder interviews", "Data analysis"]),
                "stakeholder_analysis": specialized_analysis.get("stakeholder_analysis", {}),
                "recommendations": ai_result.recommendations,
                "next_actions": [
                    "Proceed to Orange Orangutan planning phase",
                    "Address identified knowledge gaps",
                    "Validate research findings"
                ]
            })
        
        elif step_name == "orange_orangutan_planning":
            result.update({
                "planning_completed": True,
                "planning_complexity": specialized_analysis.get("planning_complexity", "medium"),
                "risk_factors": specialized_analysis.get("risk_factors", ["Resource constraints", "Timeline pressure"]),
                "resource_requirements": specialized_analysis.get("resource_requirements", {}),
                "strategic_plan": specialized_analysis.get("strategic_plan", {}),
                "recommendations": ai_result.recommendations,
                "next_actions": [
                    "Proceed to Yellow Honeybee development phase",
                    "Refine strategic plan based on feedback",
                    "Address identified risks"
                ]
            })
        
        elif step_name == "yellow_honeybee_development":
            result.update({
                "development_completed": True,
                "innovation_strategy": specialized_analysis.get("innovation_strategy", "Creative solution development"),
                "technical_architecture": specialized_analysis.get("technical_architecture", "Modern, scalable architecture"),
                "solution_concepts": specialized_analysis.get("solution_concepts", ["Innovative solutions"]),
                "recommendations": ai_result.recommendations,
                "next_actions": [
                    "Proceed to Green Tortoise resource planning",
                    "Refine technical specifications",
                    "Validate solution concepts"
                ]
            })
        
        elif step_name == "green_tortoise_resources":
            result.update({
                "resource_planning_completed": True,
                "budget_allocation": specialized_analysis.get("budget_allocation", {}),
                "resource_planning": specialized_analysis.get("resource_planning", {}),
                "sustainability_strategy": specialized_analysis.get("sustainability_strategy", "Long-term sustainability"),
                "recommendations": ai_result.recommendations,
                "next_actions": [
                    "Proceed to Blue Dolphin communication planning",
                    "Finalize resource allocation",
                    "Set up tracking systems"
                ]
            })
        
        elif step_name == "blue_dolphin_communication":
            result.update({
                "communication_completed": True,
                "communication_strategy": specialized_analysis.get("communication_strategy", "Comprehensive communication plan"),
                "stakeholder_engagement": specialized_analysis.get("stakeholder_engagement", "Multi-channel engagement"),
                "key_messages": specialized_analysis.get("key_messages", ["Clear value proposition"]),
                "recommendations": ai_result.recommendations,
                "next_actions": [
                    "Proceed to Purple Elephant support planning",
                    "Launch communication campaign",
                    "Monitor stakeholder engagement"
                ]
            })
        
        elif step_name == "purple_elephant_support":
            result.update({
                "support_completed": True,
                "support_framework": specialized_analysis.get("support_framework", "Comprehensive support system"),
                "human_impact": specialized_analysis.get("human_impact", "Positive human impact"),
                "equity_inclusion": specialized_analysis.get("equity_inclusion", "Equitable and inclusive approach"),
                "recommendations": ai_result.recommendations,
                "next_actions": [
                    "Proceed to synthesis and decision phase",
                    "Implement support systems",
                    "Monitor human impact"
                ]
            })
        
        return result
    
    async def generate_ai_synthesis(self) -> Dict[str, Any]:
        """Generate AI-powered synthesis of all workflow results"""
        if not self.current_session:
            raise ValueError("No active session")
        
        try:
            # Prepare synthesis context
            context = {
                "problem_title": self.current_session.problem.title,
                "problem_description": self.current_session.problem.description,
                "workflow_results": {},
                "ai_insights": self.current_session.ai_insights,
                "steps_completed": len(self.current_session.steps_completed)
            }
            
            # Add results from all completed steps
            for step in self.current_session.steps_completed:
                context["workflow_results"][step.step_name] = step.results
            
            # Generate AI synthesis
            ai_response = await self.ai_integration.generate_response(
                "workflow_synthesis", context, self.current_session.conversation_id
            )
            
            # Process synthesis result
            synthesis = {
                "synthesis_completed": True,
                "overall_confidence": ai_response.confidence_score,
                "ai_enhanced": True,
                "synthesis_content": ai_response.content,
                "key_insights": self._extract_synthesis_insights(ai_response.content),
                "recommended_approach": self._extract_recommended_approach(ai_response.content),
                "next_steps": self._extract_next_steps(ai_response.content),
                "ai_metadata": ai_response.metadata
            }
            
            # Store in session
            self.current_session.ai_insights["synthesis"] = synthesis
            
            return synthesis
            
        except Exception as e:
            logger.error(f"Error generating AI synthesis: {str(e)}")
            # Fallback to standard synthesis
            return await self.generate_synthesis()
    
    def _extract_synthesis_insights(self, content: str) -> List[str]:
        """Extract key insights from synthesis content"""
        insights = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if (line.startswith('-') or line.startswith('•') or 
                'insight' in line.lower() or 'key finding' in line.lower()):
                clean_line = line.lstrip('-• ').strip()
                if clean_line and len(clean_line) > 10:
                    insights.append(clean_line)
        
        return insights[:5]  # Limit to 5 insights
    
    def _extract_recommended_approach(self, content: str) -> str:
        """Extract recommended approach from synthesis content"""
        lines = content.split('\n')
        for line in lines:
            if 'recommended' in line.lower() or 'approach' in line.lower():
                return line.strip()
        return "Systematic implementation approach recommended"
    
    def _extract_next_steps(self, content: str) -> List[str]:
        """Extract next steps from synthesis content"""
        steps = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if (line.startswith('1.') or line.startswith('2.') or 
                line.startswith('3.') or 'next step' in line.lower()):
                clean_line = line.lstrip('123. ').strip()
                if clean_line and len(clean_line) > 5:
                    steps.append(clean_line)
        
        return steps[:3]  # Limit to 3 next steps
    
    def get_ai_session_summary(self) -> Dict[str, Any]:
        """Get summary of AI-enhanced session"""
        if not self.current_session:
            return {}
        
        session = self.current_session
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "problem_title": session.problem.title,
            "ai_enhanced": True,
            "total_steps": len(session.steps_completed),
            "ai_enhanced_steps": len(session.ai_enhanced_steps),
            "ai_enhancement_rate": len(session.ai_enhanced_steps) / max(len(session.steps_completed), 1),
            "conversation_id": session.conversation_id,
            "ai_insights_count": len(session.ai_insights),
            "ai_recommendations_count": len(session.ai_recommendations),
            "session_duration": (datetime.utcnow() - session.started_at).total_seconds()
        }

# Demo function
async def demo_ai_enhanced_workflow():
    """Demonstrate AI-enhanced workflow capabilities"""
    print("🤖 AI-Enhanced Problem-Solving Workflow")
    print("=" * 60)
    
    # Initialize AI configuration
    ai_config = AIWorkflowConfig(
        llm_config=LLMConfig(
            provider=LLMProvider.MOCK,
            model=LLMModel.GPT_4,
            temperature=0.7,
            max_tokens=2000
        ),
        enable_ai_enhancement=True,
        ai_confidence_threshold=0.7,
        fallback_to_standard=True,
        enable_conversation_memory=True
    )
    
    # Create AI-enhanced workflow
    ai_workflow = AIEnhancedProblemSolvingWorkflow(ai_config)
    
    print(f"✅ AI-Enhanced Workflow initialized")
    print(f"AI Provider: {ai_config.llm_config.provider.value}")
    print(f"AI Model: {ai_config.llm_config.model.value}")
    print(f"AI Enhancement: {ai_config.enable_ai_enhancement}")
    print()
    
    # Create sample problem
    from src.core.types import ProblemStatement, ProblemComplexity
    
    sample_problem = ProblemStatement(
        title="AI-Powered Healthcare Transformation",
        description="Transform a traditional healthcare system using AI and machine learning to improve patient outcomes, reduce costs, and enhance operational efficiency while ensuring data privacy and regulatory compliance.",
        complexity=ProblemComplexity.SYSTEMIC,
        domain="Healthcare & Artificial Intelligence",
        stakeholders=["Healthcare Providers", "Patients", "IT Department", "Administration", "Regulatory Bodies", "AI Vendors"],
        constraints={"budget": "$50M", "timeline": "3 years", "compliance": "HIPAA, GDPR", "privacy": "Patient data protection"},
        success_criteria=["Improve patient outcomes by 40%", "Reduce operational costs by 30%", "Achieve 99.9% system uptime", "Ensure 100% regulatory compliance"]
    )
    
    print("📋 Sample Problem:")
    print(f"Title: {sample_problem.title}")
    print(f"Complexity: {sample_problem.complexity.value}")
    print(f"Stakeholders: {len(sample_problem.stakeholders)}")
    print()
    
    # Start AI-enhanced session
    print("🚀 Starting AI-Enhanced Workflow Session")
    print("-" * 50)
    
    session = await ai_workflow.start_ai_enhanced_session(sample_problem, "demo_user")
    
    print(f"Session ID: {session.session_id}")
    print(f"Conversation ID: {session.conversation_id}")
    print(f"AI Insights Generated: {len(session.ai_insights)}")
    print()
    
    # Execute AI-enhanced steps
    workflow_steps = [
        ("red_owl_research", "Research and Analysis"),
        ("orange_orangutan_planning", "Strategic Planning"),
        ("yellow_honeybee_development", "Solution Development"),
        ("green_tortoise_resources", "Resource Planning"),
        ("blue_dolphin_communication", "Communication Strategy"),
        ("purple_elephant_support", "Support Systems")
    ]
    
    for step_name, step_description in workflow_steps:
        print(f"🤖 Executing AI-Enhanced Step: {step_description}")
        print("-" * 40)
        
        # Create step data
        step_data = AIWorkflowStepData(
            step_name=step_name,
            user_inputs={
                "focus_area": f"AI-powered {step_description.lower()}",
                "priority": "high",
                "stakeholders": sample_problem.stakeholders
            },
            ai_confidence_threshold=0.7
        )
        
        # Execute step
        result = await ai_workflow.execute_ai_enhanced_step(step_data)
        
        print(f"✅ Step completed: {result.get('step_completed', False)}")
        print(f"AI Enhanced: {result.get('ai_enhanced', False)}")
        print(f"Confidence: {result.get('confidence_score', 0):.2f}")
        print(f"Recommendations: {len(result.get('recommendations', []))}")
        print()
    
    # Generate AI synthesis
    print("🎯 Generating AI-Powered Synthesis")
    print("-" * 40)
    
    synthesis = await ai_workflow.generate_ai_synthesis()
    
    print(f"✅ Synthesis completed: {synthesis.get('synthesis_completed', False)}")
    print(f"Overall Confidence: {synthesis.get('overall_confidence', 0):.2f}")
    print(f"Key Insights: {len(synthesis.get('key_insights', []))}")
    print(f"Recommended Approach: {synthesis.get('recommended_approach', 'N/A')}")
    print()
    
    # Show session summary
    print("📊 AI-Enhanced Session Summary")
    print("-" * 40)
    
    summary = ai_workflow.get_ai_session_summary()
    
    print(f"Session ID: {summary['session_id']}")
    print(f"Total Steps: {summary['total_steps']}")
    print(f"AI Enhanced Steps: {summary['ai_enhanced_steps']}")
    print(f"AI Enhancement Rate: {summary['ai_enhancement_rate']:.1%}")
    print(f"AI Insights: {summary['ai_insights_count']}")
    print(f"Session Duration: {summary['session_duration']:.1f} seconds")
    print()
    
    print("✅ AI-Enhanced workflow demonstration completed!")
    print("The system provides intelligent, context-aware problem-solving with AI assistance.")

if __name__ == "__main__":
    asyncio.run(demo_ai_enhanced_workflow())
