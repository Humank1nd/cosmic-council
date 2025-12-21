"""
Cosmic Council Refinement Engine - Layer Orchestration System
Manages complete ROYGBV cycles per layer and coordinates the refinement process.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
import json
import logging
import asyncio
from datetime import datetime, timezone
import uuid
from enum import Enum

try:
    from .layers import LayerDefinitions
    from .escalator import EscalatorEngine, EscalatorAction, SolutionCandidate
    from .sector_engine import SectorEngine, SectorType, SectorResult
except ImportError:
    # For testing
    from layers import LayerDefinitions
    from escalator import EscalatorEngine, EscalatorAction, SolutionCandidate
    from sector_engine import SectorEngine, SectorType, SectorResult


class LayerRunStatus(Enum):
    """Status of a layer run."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class LayerRun:
    """Represents a complete ROYGBV cycle at a specific layer."""
    layer_run_id: str
    problem_id: str
    layer: str
    revolution: int
    status: LayerRunStatus = LayerRunStatus.PENDING
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    sector_results: List[SectorResult] = field(default_factory=list)
    total_cost_usd: float = 0.0
    total_latency_ms: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class ProblemContext:
    """Context information for a problem being processed."""
    problem_id: str
    title: str
    description: str
    original_question: str
    current_layer: str
    layer_runs: List[LayerRun] = field(default_factory=list)
    refinements: List[Dict[str, Any]] = field(default_factory=list)
    answers: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LayerOrchestrator:
    """
    Orchestrates the execution of ROYGBV cycles at different layers.
    
    This is the main coordinator that:
    1. Manages layer runs and revolutions
    2. Executes complete ROYGBV cycles
    3. Coordinates with the escalator for refinement decisions
    4. Tracks progress and metrics
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the layer orchestrator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.sector_engine = SectorEngine()
        self.escalator = EscalatorEngine(config)
        self.active_problems: Dict[str, ProblemContext] = {}
    
    async def start_problem(
        self,
        problem_id: str,
        title: str,
        description: str,
        initial_layer: str = "deci"
    ) -> ProblemContext:
        """
        Start processing a new problem.
        
        Args:
            problem_id: Unique identifier for the problem
            title: Problem title
            description: Problem description
            initial_layer: Starting layer (default: deci)
            
        Returns:
            ProblemContext for the started problem
        """
        self.logger.info(f"Starting problem {problem_id} at layer {initial_layer}")
        
        # Validate initial layer
        if not LayerDefinitions.is_valid_layer(initial_layer):
            raise ValueError(f"Invalid initial layer: {initial_layer}")
        
        # Create problem context
        problem_context = ProblemContext(
            problem_id=problem_id,
            title=title,
            description=description,
            original_question=description,
            current_layer=initial_layer
        )
        
        # Store in active problems
        self.active_problems[problem_id] = problem_context
        
        # Start first layer run
        await self._start_layer_run(problem_context, initial_layer, 1)
        
        return problem_context
    
    async def _start_layer_run(
        self,
        problem_context: ProblemContext,
        layer: str,
        revolution: int
    ) -> LayerRun:
        """
        Start a new layer run.
        
        Args:
            problem_context: The problem context
            layer: The layer to run
            revolution: The revolution number at this layer
            
        Returns:
            LayerRun object
        """
        layer_run_id = str(uuid.uuid4())
        
        layer_run = LayerRun(
            layer_run_id=layer_run_id,
            problem_id=problem_context.problem_id,
            layer=layer,
            revolution=revolution,
            status=LayerRunStatus.PENDING
        )
        
        problem_context.layer_runs.append(layer_run)
        
        self.logger.info(f"Started layer run {layer_run_id} for problem {problem_context.problem_id} at {layer} layer (revolution {revolution})")
        
        return layer_run
    
    async def execute_layer_run(self, layer_run: LayerRun) -> LayerRun:
        """
        Execute a complete ROYGBV cycle for a layer run.
        
        Args:
            layer_run: The layer run to execute
            
        Returns:
            Updated LayerRun object
        """
        self.logger.info(f"Executing layer run {layer_run.layer_run_id}")
        
        try:
            # Update status
            layer_run.status = LayerRunStatus.IN_PROGRESS
            layer_run.started_at = datetime.now(timezone.utc)
            
            # Get problem context
            problem_context = self.active_problems.get(layer_run.problem_id)
            if not problem_context:
                raise ValueError(f"Problem context not found for {layer_run.problem_id}")
            
            # Execute full ROYGBV cycle
            sector_results = await self.sector_engine.execute_full_cycle(
                layer=layer_run.layer,
                problem_statement=problem_context.original_question,
                initial_context={
                    "problem_id": layer_run.problem_id,
                    "layer_run_id": layer_run.layer_run_id,
                    "revolution": layer_run.revolution
                }
            )
            
            # Store sector results
            layer_run.sector_results = sector_results
            
            # Calculate metrics
            await self._calculate_layer_metrics(layer_run)
            
            # Check if any sector failed
            failed_sectors = [r for r in sector_results if r.status == "failed"]
            if failed_sectors:
                layer_run.status = LayerRunStatus.FAILED
                layer_run.error_message = f"Failed sectors: {[s.sector.value for s in failed_sectors]}"
            else:
                layer_run.status = LayerRunStatus.COMPLETED
            
            layer_run.finished_at = datetime.now(timezone.utc)
            
            self.logger.info(f"Completed layer run {layer_run.layer_run_id} with status {layer_run.status.value}")
            
        except Exception as e:
            self.logger.error(f"Error executing layer run {layer_run.layer_run_id}: {str(e)}")
            layer_run.status = LayerRunStatus.FAILED
            layer_run.error_message = str(e)
            layer_run.finished_at = datetime.now(timezone.utc)
        
        return layer_run
    
    async def _calculate_layer_metrics(self, layer_run: LayerRun):
        """Calculate metrics for a completed layer run."""
        if not layer_run.sector_results:
            return
        
        # Calculate total cost and latency
        total_cost = sum(result.cost_usd for result in layer_run.sector_results)
        total_latency = sum(result.execution_time_ms for result in layer_run.sector_results)
        
        layer_run.total_cost_usd = total_cost
        layer_run.total_latency_ms = total_latency
        
        # Aggregate sector metrics
        confidence_scores = [result.metrics.get("confidence", 0.0) for result in layer_run.sector_results]
        completeness_scores = [result.metrics.get("completeness", 0.0) for result in layer_run.sector_results]
        novelty_scores = [result.metrics.get("novelty", 0.0) for result in layer_run.sector_results]
        
        # Calculate weighted averages (Purple sector gets higher weight for final evaluation)
        weights = [1.0, 1.0, 1.0, 1.0, 1.0, 2.0]  # Purple gets 2x weight
        
        weighted_confidence = sum(c * w for c, w in zip(confidence_scores, weights)) / sum(weights)
        weighted_completeness = sum(c * w for c, w in zip(completeness_scores, weights)) / sum(weights)
        weighted_novelty = sum(n * w for n, w in zip(novelty_scores, weights)) / sum(weights)
        
        # Store metrics
        layer_run.metrics = {
            "confidence_score": weighted_confidence,
            "completeness_score": weighted_completeness,
            "novelty_score": weighted_novelty,
            "total_cost_usd": total_cost,
            "total_latency_ms": total_latency,
            "sector_count": len(layer_run.sector_results),
            "successful_sectors": len([r for r in layer_run.sector_results if r.status == "completed"]),
            "revolutions_at_layer": layer_run.revolution
        }
    
    async def make_escalator_decision(self, problem_context: ProblemContext) -> Dict[str, Any]:
        """
        Make an escalator decision for a problem.
        
        Args:
            problem_context: The problem context
            
        Returns:
            Escalator decision result
        """
        # Get the most recent completed layer run
        completed_runs = [run for run in problem_context.layer_runs if run.status == LayerRunStatus.COMPLETED]
        if not completed_runs:
            raise ValueError("No completed layer runs found for escalator decision")
        
        latest_run = max(completed_runs, key=lambda r: r.finished_at)
        
        # Create solution candidate from latest run
        solution_candidate = SolutionCandidate(
            solution_text=f"Solution from {latest_run.layer} layer (revolution {latest_run.revolution})",
            confidence_score=latest_run.metrics.get("confidence_score", 0.0),
            completeness_score=latest_run.metrics.get("completeness_score", 0.0),
            novelty_score=latest_run.metrics.get("novelty_score", 0.0),
            alignment_score=1.0,  # Default alignment
            net_benefit_score=0.8  # Default net benefit
        )
        
        # Make escalator decision
        decision = self.escalator.decide(
            problem_id=problem_context.problem_id,
            current_layer=latest_run.layer,
            solution_candidate=solution_candidate,
            layer_metrics=latest_run.metrics,
            problem_context={
                "original_question": problem_context.original_question,
                "problem_id": problem_context.problem_id
            }
        )
        
        return self.escalator.get_decision_summary(decision)
    
    async def process_escalator_decision(
        self,
        problem_context: ProblemContext,
        decision: Dict[str, Any]
    ) -> ProblemContext:
        """
        Process an escalator decision and take appropriate action.
        
        Args:
            problem_context: The problem context
            decision: The escalator decision
            
        Returns:
            Updated ProblemContext
        """
        action = decision["action"]
        
        if action == EscalatorAction.RESOLVE.value:
            await self._resolve_problem(problem_context, decision)
        
        elif action == EscalatorAction.REFINE.value:
            await self._refine_problem(problem_context, decision)
        
        elif action == EscalatorAction.STAY.value:
            await self._stay_at_layer(problem_context, decision)
        
        else:
            raise ValueError(f"Unknown escalator action: {action}")
        
        return problem_context
    
    async def _resolve_problem(self, problem_context: ProblemContext, decision: Dict[str, Any]):
        """Resolve a problem with the current solution."""
        self.logger.info(f"Resolving problem {problem_context.problem_id}")
        
        # Get the latest completed layer run
        completed_runs = [run for run in problem_context.layer_runs if run.status == LayerRunStatus.COMPLETED]
        latest_run = max(completed_runs, key=lambda r: r.finished_at)
        
        # Create answer record
        answer = {
            "answer_id": str(uuid.uuid4()),
            "problem_id": problem_context.problem_id,
            "layer": latest_run.layer,
            "solution": {
                "layer_run_id": latest_run.layer_run_id,
                "sector_results": [
                    {
                        "sector": result.sector.value,
                        "output": result.output,
                        "metrics": result.metrics
                    }
                    for result in latest_run.sector_results
                ],
                "overall_metrics": latest_run.metrics
            },
            "confidence_score": latest_run.metrics.get("confidence_score", 0.0),
            "completeness_score": latest_run.metrics.get("completeness_score", 0.0),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        problem_context.answers.append(answer)
        
        # Mark problem as resolved
        problem_context.metadata["status"] = "resolved"
        problem_context.metadata["resolved_at"] = datetime.now(timezone.utc).isoformat()
        problem_context.metadata["resolution_decision"] = decision
    
    async def _refine_problem(self, problem_context: ProblemContext, decision: Dict[str, Any]):
        """Refine a problem to a deeper layer."""
        from_layer = decision["from_layer"]
        to_layer = decision["to_layer"]
        refined_question = decision["refined_question"]
        
        self.logger.info(f"Refining problem {problem_context.problem_id} from {from_layer} to {to_layer}")
        
        # Record refinement
        refinement = {
            "refinement_id": str(uuid.uuid4()),
            "problem_id": problem_context.problem_id,
            "from_layer": from_layer,
            "to_layer": to_layer,
            "rationale": decision["reason"],
            "refined_question": refined_question,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        problem_context.refinements.append(refinement)
        
        # Update current layer
        problem_context.current_layer = to_layer
        
        # Start new layer run
        await self._start_layer_run(problem_context, to_layer, 1)
    
    async def _stay_at_layer(self, problem_context: ProblemContext, decision: Dict[str, Any]):
        """Stay at the current layer for another revolution."""
        current_layer = problem_context.current_layer
        
        # Count current revolutions at this layer
        current_revolutions = len([run for run in problem_context.layer_runs if run.layer == current_layer])
        next_revolution = current_revolutions + 1
        
        self.logger.info(f"Staying at {current_layer} layer for revolution {next_revolution}")
        
        # Start new layer run
        await self._start_layer_run(problem_context, current_layer, next_revolution)
    
    async def process_problem_continuously(
        self,
        problem_id: str,
        title: str,
        description: str,
        max_iterations: int = 100
    ) -> ProblemContext:
        """
        Process a problem continuously until resolution or max iterations.
        
        Args:
            problem_id: Unique identifier for the problem
            title: Problem title
            description: Problem description
            max_iterations: Maximum number of iterations
            
        Returns:
            Final ProblemContext
        """
        self.logger.info(f"Starting continuous processing of problem {problem_id}")
        
        # Start the problem
        problem_context = await self.start_problem(problem_id, title, description)
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            self.logger.info(f"Processing iteration {iteration} for problem {problem_id}")
            
            # Find pending layer runs
            pending_runs = [
                run for run in problem_context.layer_runs
                if run.status == LayerRunStatus.PENDING
            ]
            
            if not pending_runs:
                # No pending runs, check if we need to make an escalator decision
                completed_runs = [
                    run for run in problem_context.layer_runs
                    if run.status == LayerRunStatus.COMPLETED
                ]
                
                if completed_runs:
                    # Make escalator decision
                    decision = await self.make_escalator_decision(problem_context)
                    await self.process_escalator_decision(problem_context, decision)
                    
                    # Check if problem is resolved
                    if problem_context.metadata.get("status") == "resolved":
                        self.logger.info(f"Problem {problem_id} resolved after {iteration} iterations")
                        break
                else:
                    # No runs at all, something went wrong
                    self.logger.error(f"No runs found for problem {problem_id}")
                    break
            
            # Execute pending layer runs
            for layer_run in pending_runs:
                await self.execute_layer_run(layer_run)
        
        if iteration >= max_iterations:
            self.logger.warning(f"Problem {problem_id} reached max iterations ({max_iterations})")
            problem_context.metadata["status"] = "max_iterations_reached"
        
        return problem_context
    
    def get_problem_status(self, problem_id: str) -> Dict[str, Any]:
        """Get the current status of a problem."""
        problem_context = self.active_problems.get(problem_id)
        if not problem_context:
            return {"error": "Problem not found"}
        
        return {
            "problem_id": problem_id,
            "title": problem_context.title,
            "current_layer": problem_context.current_layer,
            "status": problem_context.metadata.get("status", "in_progress"),
            "layer_runs_count": len(problem_context.layer_runs),
            "refinements_count": len(problem_context.refinements),
            "answers_count": len(problem_context.answers),
            "latest_layer_run": {
                "layer": problem_context.layer_runs[-1].layer if problem_context.layer_runs else None,
                "revolution": problem_context.layer_runs[-1].revolution if problem_context.layer_runs else None,
                "status": problem_context.layer_runs[-1].status.value if problem_context.layer_runs else None
            } if problem_context.layer_runs else None
        }
    
    def get_problem_genealogy(self, problem_id: str) -> Dict[str, Any]:
        """Get the complete genealogy of a problem."""
        problem_context = self.active_problems.get(problem_id)
        if not problem_context:
            return {"error": "Problem not found"}
        
        return {
            "problem_id": problem_id,
            "title": problem_context.title,
            "original_question": problem_context.original_question,
            "refinements": problem_context.refinements,
            "layer_runs": [
                {
                    "layer_run_id": run.layer_run_id,
                    "layer": run.layer,
                    "revolution": run.revolution,
                    "status": run.status.value,
                    "started_at": run.started_at.isoformat() if run.started_at else None,
                    "finished_at": run.finished_at.isoformat() if run.finished_at else None,
                    "metrics": run.metrics
                }
                for run in problem_context.layer_runs
            ],
            "answers": problem_context.answers,
            "metadata": problem_context.metadata
        }


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_layer_orchestration():
        print("=== Layer Orchestration Test ===")
        
        orchestrator = LayerOrchestrator()
        
        # Test continuous problem processing
        problem_context = await orchestrator.process_problem_continuously(
            problem_id="test-problem-001",
            title="Test Problem",
            description="How can we reduce global carbon emissions?",
            max_iterations=5
        )
        
        print(f"\nProblem processing completed:")
        print(f"Status: {problem_context.metadata.get('status', 'unknown')}")
        print(f"Layer runs: {len(problem_context.layer_runs)}")
        print(f"Refinements: {len(problem_context.refinements)}")
        print(f"Answers: {len(problem_context.answers)}")
        
        # Test status retrieval
        status = orchestrator.get_problem_status("test-problem-001")
        print(f"\nProblem status: {status}")
        
        # Test genealogy
        genealogy = orchestrator.get_problem_genealogy("test-problem-001")
        print(f"\nProblem genealogy keys: {list(genealogy.keys())}")
    
    # Run the test
    asyncio.run(test_layer_orchestration())
