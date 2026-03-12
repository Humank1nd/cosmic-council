"""
Hierarchical Enterprise System for Agent Orchestrator
Implements the multi-level agent architecture:
- Level 1: Large model orchestrator (trains and coordinates)
- Level 2: 6 Enterprise operations (ROYGBV)
- Level 3: Departments within each enterprise
- Level 4: Specialized AI agents (one task each, with handoff logic)

This stack is the supercharger supply chain: large models first teach the
enterprises, departments, and specialists, then the agents distill those
abilities into lighter-weight models that can run locally and evolve autonomously.
Long-term goal: Agents build their own frameworks, distill larger models
into smaller local ones, and evolve autonomously.
"""

import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime

from ..integrations.llm_provider import BaseLLMProvider, LLMRequest, LLMMessage

logger = logging.getLogger(__name__)


class AgentSpecialization(Enum):
    """Specialized task types for department agents"""
    # Research Department
    DATA_COLLECTOR = "data_collector"
    LITERATURE_REVIEWER = "literature_reviewer"
    HYPOTHESIS_GENERATOR = "hypothesis_generator"
    VALIDATION_SPECIALIST = "validation_specialist"
    
    # Planning Department
    TASK_DECOMPOSER = "task_decomposer"
    DEPENDENCY_MAPPER = "dependency_mapper"
    TIMELINE_OPTIMIZER = "timeline_optimizer"
    RESOURCE_ALLOCATOR = "resource_allocator"
    
    # Development Department
    PROTOTYPE_BUILDER = "prototype_builder"
    CODE_GENERATOR = "code_generator"
    TEST_WRITER = "test_writer"
    DOCUMENTATION_SPECIALIST = "documentation_specialist"
    
    # Budget Department
    COST_ESTIMATOR = "cost_estimator"
    BUDGET_ANALYZER = "budget_analyzer"
    ROI_CALCULATOR = "roi_calculator"
    FINANCIAL_REPORTER = "financial_reporter"
    
    # Market Department
    AUDIENCE_ANALYZER = "audience_analyzer"
    MESSAGE_CRAFTER = "message_crafter"
    CHANNEL_OPTIMIZER = "channel_optimizer"
    METRIC_TRACKER = "metric_tracker"
    
    # Support Department
    FEEDBACK_COLLECTOR = "feedback_collector"
    ISSUE_TRIAGER = "issue_triager"
    SOLUTION_PROVIDER = "solution_provider"
    IMPROVEMENT_ANALYZER = "improvement_analyzer"


class HandoffReason(Enum):
    """Reasons for agent handoff"""
    TASK_COMPLETE = "task_complete"
    OUT_OF_SCOPE = "out_of_scope"
    REQUIRES_SPECIALIST = "requires_specialist"
    BLOCKED = "blocked"
    ERROR = "error"
    OPTIMIZATION_NEEDED = "optimization_needed"


@dataclass
class TaskContext:
    """Context for a task being processed"""
    task_id: str
    problem_id: str
    enterprise: str
    department: str
    current_agent: str
    task_description: str
    input_data: Dict[str, Any]
    history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentHandoff:
    """Represents a handoff between agents"""
    from_agent: str
    to_agent: str
    reason: HandoffReason
    context: TaskContext
    handoff_data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentResult:
    """Result from a specialized agent"""
    agent_id: str
    specialization: AgentSpecialization
    task_id: str
    success: bool
    output: Dict[str, Any]
    confidence: float
    handoff: Optional[AgentHandoff] = None
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class SpecializedAgent(ABC):
    """
    Base class for specialized department agents.
    Each agent does ONE specific task extremely well.
    """
    
    def __init__(
        self,
        agent_id: str,
        specialization: AgentSpecialization,
        llm_provider: Optional[BaseLLMProvider] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.specialization = specialization
        self.llm_provider = llm_provider
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{specialization.value}")
        
        # Performance tracking
        self.tasks_completed = 0
        self.handoffs_made = 0
        self.success_rate = 1.0
        self.avg_processing_time = 0.0
    
    @abstractmethod
    async def process_task(self, context: TaskContext) -> AgentResult:
        """
        Process a task. Returns result and optionally a handoff.
        
        Args:
            context: Task context with input data
            
        Returns:
            AgentResult with output and optional handoff
        """
        pass
    
    @abstractmethod
    def should_handoff(self, context: TaskContext) -> Optional[AgentHandoff]:
        """
        Determine if this agent should hand off to another agent.
        
        Args:
            context: Current task context
            
        Returns:
            AgentHandoff if handoff needed, None otherwise
        """
        pass
    
    @abstractmethod
    def get_handoff_targets(self) -> List[AgentSpecialization]:
        """
        Get list of specializations this agent can hand off to.
        
        Returns:
            List of target specializations
        """
        pass
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities description"""
        return {
            "agent_id": self.agent_id,
            "specialization": self.specialization.value,
            "tasks_completed": self.tasks_completed,
            "success_rate": self.success_rate,
            "avg_processing_time": self.avg_processing_time
        }


class Department:
    """
    A department within an enterprise.
    Contains multiple specialized agents.
    """
    
    def __init__(
        self,
        department_id: str,
        name: str,
        enterprise: str,
        agents: List[SpecializedAgent],
        coordinator_llm: Optional[BaseLLMProvider] = None
    ):
        self.department_id = department_id
        self.name = name
        self.enterprise = enterprise
        self.agents: Dict[AgentSpecialization, SpecializedAgent] = {
            agent.specialization: agent for agent in agents
        }
        self.coordinator_llm = coordinator_llm
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    def get_agent(self, specialization: AgentSpecialization) -> Optional[SpecializedAgent]:
        """Get agent by specialization"""
        return self.agents.get(specialization)
    
    async def route_task(
        self,
        task_description: str,
        context: TaskContext
    ) -> AgentResult:
        """
        Route a task to the appropriate agent in this department.
        Uses coordinator LLM to determine best agent if available.
        """
        # Determine which agent should handle this
        target_specialization = await self._select_agent(task_description, context)
        
        agent = self.get_agent(target_specialization)
        if not agent:
            raise ValueError(f"No agent available for {target_specialization.value}")
        
        # Process task
        result = await agent.process_task(context)
        
        # Handle handoffs
        if result.handoff:
            if result.handoff.to_agent in [a.agent_id for a in self.agents.values()]:
                # Handoff within department
                target_agent = next(
                    a for a in self.agents.values()
                    if a.agent_id == result.handoff.to_agent
                )
                new_context = TaskContext(
                    task_id=context.task_id,
                    problem_id=context.problem_id,
                    enterprise=context.enterprise,
                    department=context.department,
                    current_agent=target_agent.agent_id,
                    task_description=result.handoff.handoff_data.get("task_description", context.task_description),
                    input_data=result.handoff.handoff_data.get("input_data", result.output),
                    history=context.history + [{"agent": context.current_agent, "result": result.output}]
                )
                return await target_agent.process_task(new_context)
        
        return result
    
    async def _select_agent(
        self,
        task_description: str,
        context: TaskContext
    ) -> AgentSpecialization:
        """Select the best agent for a task"""
        if self.coordinator_llm:
            # Use LLM to select best agent
            prompt = f"""
            Task: {task_description}
            Available agents: {[s.value for s in self.agents.keys()]}
            
            Select the best agent specialization for this task.
            Return only the specialization name.
            """
            request = LLMRequest(
                messages=[LLMMessage(role="user", content=prompt)],
                temperature=0.3,
                max_tokens=50
            )
            response = await self.coordinator_llm.generate(request)
            try:
                return AgentSpecialization(response.content.strip().lower())
            except ValueError:
                pass
        
        # Fallback: simple keyword matching
        task_lower = task_description.lower()
        for specialization in self.agents.keys():
            if specialization.value.replace("_", " ") in task_lower:
                return specialization
        
        # Default to first available agent
        return list(self.agents.keys())[0]


class EnterpriseOperation:
    """
    An enterprise-level operation (one of the 6 ROYGBV enterprises).
    Contains multiple departments, each with specialized agents.
    """
    
    def __init__(
        self,
        enterprise_id: str,
        name: str,
        enterprise_type: str,  # red_owl, orange_orangutan, etc.
        departments: List[Department],
        coordinator_llm: Optional[BaseLLMProvider] = None
    ):
        self.enterprise_id = enterprise_id
        self.name = name
        self.enterprise_type = enterprise_type
        self.departments: Dict[str, Department] = {
            dept.department_id: dept for dept in departments
        }
        self.coordinator_llm = coordinator_llm
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    def get_department(self, department_id: str) -> Optional[Department]:
        """Get department by ID"""
        return self.departments.get(department_id)
    
    async def process_problem(
        self,
        problem_id: str,
        problem_description: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a problem through this enterprise's departments.
        Coordinates across departments using the coordinator LLM.
        """
        results = {}
        
        # Determine which departments need to be involved
        departments_to_use = await self._select_departments(problem_description)
        
        # Process through each department
        current_data = input_data
        for dept_id in departments_to_use:
            dept = self.get_department(dept_id)
            if not dept:
                continue
            
            context = TaskContext(
                task_id=str(uuid.uuid4()),
                problem_id=problem_id,
                enterprise=self.enterprise_type,
                department=dept_id,
                current_agent="",
                task_description=problem_description,
                input_data=current_data
            )
            
            result = await dept.route_task(problem_description, context)
            results[dept_id] = result.output
            current_data = result.output  # Pass output to next department
        
        return results
    
    async def _select_departments(self, problem_description: str) -> List[str]:
        """Select which departments should handle this problem"""
        if self.coordinator_llm:
            prompt = f"""
            Problem: {problem_description}
            Available departments: {list(self.departments.keys())}
            
            Select which departments should handle this problem.
            Return a comma-separated list of department IDs.
            """
            request = LLMRequest(
                messages=[LLMMessage(role="user", content=prompt)],
                temperature=0.3,
                max_tokens=200
            )
            response = await self.coordinator_llm.generate(request)
            dept_names = [d.strip() for d in response.content.split(",")]
            return [d for d in dept_names if d in self.departments]
        
        # Default: use all departments
        return list(self.departments.keys())


class ModelDistillationManager:
    """
    Manages distillation of larger models into smaller, specialized ones.
    Enables agents to create optimized local versions of themselves.
    """
    
    def __init__(
        self,
        teacher_llm: BaseLLMProvider,  # Large model
        student_llm: Optional[BaseLLMProvider] = None  # Smaller local model
    ):
        self.teacher_llm = teacher_llm
        self.student_llm = student_llm
        self.logger = logging.getLogger(__name__)
    
    async def distill_agent(
        self,
        agent: SpecializedAgent,
        training_examples: List[Dict[str, Any]],
        target_model_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Distill a specialized agent's knowledge into a smaller model.
        
        Args:
            agent: The agent to distill
            training_examples: Examples of agent's task performance
            target_model_path: Where to save the distilled model
            
        Returns:
            Distillation results and model configuration
        """
        self.logger.info(f"Distilling agent {agent.agent_id} ({agent.specialization.value})")
        
        # Generate training data from examples
        training_data = await self._generate_training_data(agent, training_examples)
        
        # Create distilled model configuration
        distilled_config = {
            "agent_id": agent.agent_id,
            "specialization": agent.specialization.value,
            "capabilities": agent.get_capabilities(),
            "training_data": training_data,
            "model_path": target_model_path,
            "distillation_date": datetime.now().isoformat()
        }
        
        # If student LLM available, fine-tune it
        if self.student_llm and target_model_path:
            await self._fine_tune_student(training_data, target_model_path)
        
        return distilled_config
    
    async def _generate_training_data(
        self,
        agent: SpecializedAgent,
        examples: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate training data using teacher model"""
        training_data = []
        
        for example in examples:
            prompt = f"""
            Task: {example.get('task', '')}
            Expected output: {example.get('output', '')}
            
            Generate a training example that captures the agent's specialization:
            {agent.specialization.value}
            """
            
            request = LLMRequest(
                messages=[LLMMessage(role="user", content=prompt)],
                temperature=0.7
            )
            
            response = await self.teacher_llm.generate(request)
            training_data.append({
                "input": example.get('task', ''),
                "output": example.get('output', ''),
                "specialization": agent.specialization.value
            })
        
        return training_data
    
    async def _fine_tune_student(
        self,
        training_data: List[Dict[str, Any]],
        model_path: str
    ):
        """Fine-tune the student model with training data"""
        # This would integrate with model fine-tuning APIs
        # For now, save configuration for later training
        self.logger.info(f"Saving training configuration to {model_path}")
        # Implementation would depend on the student model type


class FrameworkEvolutionManager:
    """
    Manages the evolution of agent frameworks.
    Agents can build and evolve their own organizational structures.
    """
    
    def __init__(self, coordinator_llm: BaseLLMProvider):
        self.coordinator_llm = coordinator_llm
        self.logger = logging.getLogger(__name__)
        self.evolution_history: List[Dict[str, Any]] = []
    
    async def evolve_enterprise_structure(
        self,
        enterprise: EnterpriseOperation,
        performance_metrics: Dict[str, Any],
        goals: List[str]
    ) -> EnterpriseOperation:
        """
        Evolve an enterprise's structure based on performance and goals.
        
        Args:
            enterprise: Current enterprise structure
            performance_metrics: Performance data
            goals: Evolution goals
            
        Returns:
            Evolved enterprise structure
        """
        self.logger.info(f"Evolving enterprise {enterprise.name}")
        
        # Analyze current structure
        analysis = await self._analyze_structure(enterprise, performance_metrics)
        
        # Generate evolution plan
        evolution_plan = await self._generate_evolution_plan(
            enterprise, analysis, goals
        )
        
        # Apply evolution
        evolved_enterprise = await self._apply_evolution(enterprise, evolution_plan)
        
        # Record evolution
        self.evolution_history.append({
            "enterprise": enterprise.enterprise_id,
            "timestamp": datetime.now().isoformat(),
            "plan": evolution_plan,
            "changes": evolution_plan.get("changes", [])
        })
        
        return evolved_enterprise
    
    async def _analyze_structure(
        self,
        enterprise: EnterpriseOperation,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze current enterprise structure"""
        prompt = f"""
        Analyze this enterprise structure:
        Enterprise: {enterprise.name}
        Departments: {list(enterprise.departments.keys())}
        Performance metrics: {metrics}
        
        Identify:
        1. Bottlenecks
        2. Underutilized resources
        3. Missing capabilities
        4. Optimization opportunities
        """
        
        request = LLMRequest(
            messages=[LLMMessage(role="user", content=prompt)],
            temperature=0.5
        )
        
        response = await self.coordinator_llm.generate(request)
        return {"analysis": response.content, "metrics": metrics}
    
    async def _generate_evolution_plan(
        self,
        enterprise: EnterpriseOperation,
        analysis: Dict[str, Any],
        goals: List[str]
    ) -> Dict[str, Any]:
        """Generate evolution plan"""
        prompt = f"""
        Current structure analysis: {analysis.get('analysis', '')}
        Evolution goals: {goals}
        
        Generate a detailed evolution plan including:
        1. New departments to add
        2. Agents to create
        3. Handoff patterns to optimize
        4. Model distillation opportunities
        """
        
        request = LLMRequest(
            messages=[LLMMessage(role="user", content=prompt)],
            temperature=0.7
        )
        
        response = await self.coordinator_llm.generate(request)
        return {"plan": response.content, "goals": goals}
    
    async def _apply_evolution(
        self,
        enterprise: EnterpriseOperation,
        plan: Dict[str, Any]
    ) -> EnterpriseOperation:
        """Apply evolution plan to enterprise"""
        # This would parse the plan and modify the enterprise structure
        # For now, return the enterprise as-is
        self.logger.info(f"Evolution plan generated: {plan.get('plan', '')}")
        return enterprise


class HierarchicalOrchestrator:
    """
    Top-level orchestrator that uses large models to train and coordinate
    the 6 enterprise operations with their departments and specialized agents.
    """
    
    def __init__(
        self,
        coordinator_llm: BaseLLMProvider,  # Large model for coordination
        enterprises: List[EnterpriseOperation],
        distillation_manager: Optional[ModelDistillationManager] = None,
        evolution_manager: Optional[FrameworkEvolutionManager] = None
    ):
        self.coordinator_llm = coordinator_llm
        self.enterprises: Dict[str, EnterpriseOperation] = {
            ent.enterprise_type: ent for ent in enterprises
        }
        self.distillation_manager = distillation_manager
        self.evolution_manager = evolution_manager or FrameworkEvolutionManager(coordinator_llm)
        self.logger = logging.getLogger(__name__)
    
    async def process_problem(
        self,
        problem_id: str,
        problem_description: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a problem through the hierarchical system.
        Large model coordinates which enterprises to use.
        """
        # Use coordinator to determine which enterprises should handle this
        enterprise_types = await self._select_enterprises(problem_description)
        
        results = {}
        for enterprise_type in enterprise_types:
            enterprise = self.enterprises.get(enterprise_type)
            if not enterprise:
                continue
            
            enterprise_results = await enterprise.process_problem(
                problem_id, problem_description, input_data
            )
            results[enterprise_type] = enterprise_results
        
        return results
    
    async def _select_enterprises(self, problem_description: str) -> List[str]:
        """Use coordinator LLM to select which enterprises to use"""
        prompt = f"""
        Problem: {problem_description}
        Available enterprises: {list(self.enterprises.keys())}
        
        Select which enterprises should handle this problem.
        Return a comma-separated list of enterprise types.
        """
        
        request = LLMRequest(
            messages=[LLMMessage(role="user", content=prompt)],
            temperature=0.3,
            max_tokens=100
        )
        
        response = await self.coordinator_llm.generate(request)
        selected = [e.strip() for e in response.content.split(",")]
        return [e for e in selected if e in self.enterprises]
    
    async def distill_enterprises(self) -> Dict[str, Any]:
        """Distill all enterprises into smaller local models"""
        if not self.distillation_manager:
            raise ValueError("Distillation manager not configured")
        
        distillation_results = {}
        
        for enterprise in self.enterprises.values():
            for department in enterprise.departments.values():
                for agent in department.agents.values():
                    # Collect training examples
                    training_examples = self._collect_training_examples(agent)
                    
                    # Distill agent
                    result = await self.distillation_manager.distill_agent(
                        agent, training_examples
                    )
                    distillation_results[agent.agent_id] = result
        
        return distillation_results
    
    def _collect_training_examples(self, agent: SpecializedAgent) -> List[Dict[str, Any]]:
        """Collect training examples from agent's history"""
        # This would pull from agent's performance history
        return []
    
    async def evolve_framework(self, goals: List[str]) -> Dict[str, Any]:
        """Evolve the entire framework structure"""
        evolution_results = {}
        
        for enterprise in self.enterprises.values():
            # Collect performance metrics
            metrics = self._collect_metrics(enterprise)
            
            # Evolve enterprise
            evolved = await self.evolution_manager.evolve_enterprise_structure(
                enterprise, metrics, goals
            )
            evolution_results[enterprise.enterprise_type] = evolved
        
        return evolution_results
    
    def _collect_metrics(self, enterprise: EnterpriseOperation) -> Dict[str, Any]:
        """Collect performance metrics for an enterprise"""
        return {
            "tasks_completed": sum(
                sum(a.tasks_completed for a in dept.agents.values())
                for dept in enterprise.departments.values()
            ),
            "success_rate": 0.95,  # Would calculate from actual data
            "avg_processing_time": 1.5  # Would calculate from actual data
        }

