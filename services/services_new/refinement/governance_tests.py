"""
Cosmic Council Refinement Engine - Governance Tests and Invariants
Tests for order integrity, decision points, and system governance.
"""

import pytest
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import uuid

from .layer_orchestration import LayerOrchestrator, LayerRunStatus
from .refinement_tracker import RefinementTracker, TrackingEventType
from .sector_engine import SectorEngine, SectorType
from .escalator import EscalatorEngine, EscalatorAction, SolutionCandidate
from .layers import LayerDefinitions


class GovernanceInvariants:
    """
    Governance invariants that must be maintained by the system.
    
    These invariants ensure the integrity of the refinement process
    and prevent invalid states or behaviors.
    """
    
    @staticmethod
    def test_sector_order_integrity(sector_results: List[Any]) -> bool:
        """
        Test that sectors are executed in strict ROYGBV order.
        
        Args:
            sector_results: List of sector execution results
            
        Returns:
            True if order is maintained, False otherwise
        """
        expected_order = [
            SectorType.RED,
            SectorType.ORANGE,
            SectorType.YELLOW,
            SectorType.GREEN,
            SectorType.BLUE,
            SectorType.PURPLE
        ]
        
        if len(sector_results) != len(expected_order):
            return False
        
        for i, (result, expected) in enumerate(zip(sector_results, expected_order)):
            if result.sector != expected:
                return False
        
        return True
    
    @staticmethod
    def test_layer_run_completion_integrity(layer_run: Any) -> bool:
        """
        Test that a layer run is only considered complete when Purple sector finishes.
        
        Args:
            layer_run: Layer run object
            
        Returns:
            True if completion integrity is maintained, False otherwise
        """
        if layer_run.status != LayerRunStatus.COMPLETED:
            return True  # Not completed yet, so integrity is maintained
        
        # Check that all sectors completed successfully
        if not layer_run.sector_results:
            return False
        
        # Check that Purple sector is the last one and completed
        purple_result = layer_run.sector_results[-1]
        if purple_result.sector != SectorType.PURPLE:
            return False
        
        if purple_result.status != "completed":
            return False
        
        # Check that all sectors completed
        for result in layer_run.sector_results:
            if result.status != "completed":
                return False
        
        return True
    
    @staticmethod
    def test_refinement_timing_integrity(problem_context: Any) -> bool:
        """
        Test that refinements can only be created after Purple completion.
        
        Args:
            problem_context: Problem context object
            
        Returns:
            True if timing integrity is maintained, False otherwise
        """
        # Check that each refinement has a corresponding completed layer run
        for refinement in problem_context.refinements:
            from_layer = refinement.get("from_layer")
            
            # Find the corresponding layer run
            layer_runs = [run for run in problem_context.layer_runs if run.layer == from_layer]
            if not layer_runs:
                return False
            
            # Check that the latest run at that layer was completed
            latest_run = max(layer_runs, key=lambda r: r.revolution)
            if latest_run.status != LayerRunStatus.COMPLETED:
                return False
        
        return True
    
    @staticmethod
    def test_escalator_decision_integrity(decision: Any, layer_metrics: Dict[str, Any]) -> bool:
        """
        Test that escalator decisions are valid based on metrics.
        
        Args:
            decision: Escalator decision
            layer_metrics: Layer run metrics
            
        Returns:
            True if decision integrity is maintained, False otherwise
        """
        action = decision.get("action")
        confidence = layer_metrics.get("confidence_score", 0.0)
        completeness = layer_metrics.get("completeness_score", 0.0)
        revolutions = layer_metrics.get("revolutions_at_layer", 1)
        
        if action == EscalatorAction.RESOLVE.value:
            # Resolution should only happen with high confidence and completeness
            # or when at the bottom layer
            current_layer = decision.get("from_layer", "")
            if current_layer == "quecto":
                return True  # Always allow resolution at bottom layer
            
            # Check thresholds
            layer_capability = LayerDefinitions.get_layer(current_layer)
            if layer_capability:
                confidence_ok = confidence >= layer_capability.confidence_threshold
                completeness_ok = completeness >= layer_capability.completeness_threshold
                return confidence_ok and completeness_ok
        
        elif action == EscalatorAction.REFINE.value:
            # Refinement should only happen when quality is insufficient
            # or max revolutions reached
            layer_capability = LayerDefinitions.get_layer(decision.get("from_layer", ""))
            if layer_capability:
                max_revolutions = layer_capability.max_revolutions
                confidence_low = confidence < layer_capability.confidence_threshold
                completeness_low = completeness < layer_capability.completeness_threshold
                max_revs_reached = revolutions >= max_revolutions
                
                return confidence_low or completeness_low or max_revs_reached
        
        elif action == EscalatorAction.STAY.value:
            # Stay should only happen when quality is good but not perfect
            # and we haven't reached max revolutions
            layer_capability = LayerDefinitions.get_layer(decision.get("from_layer", ""))
            if layer_capability:
                max_revolutions = layer_capability.max_revolutions
                confidence_ok = confidence >= layer_capability.confidence_threshold
                completeness_ok = completeness >= layer_capability.completeness_threshold
                under_max_revs = revolutions < max_revolutions
                
                return confidence_ok and completeness_ok and under_max_revs
        
        return False
    
    @staticmethod
    def test_handoff_integrity(sector_results: List[Any]) -> bool:
        """
        Test that handoffs between sectors maintain data integrity.
        
        Args:
            sector_results: List of sector execution results
            
        Returns:
            True if handoff integrity is maintained, False otherwise
        """
        for i in range(len(sector_results) - 1):
            current_result = sector_results[i]
            next_result = sector_results[i + 1]
            
            # Check that current sector has handoff data for next sector
            if not current_result.handoff_data:
                return False
            
            # Check that handoff data is valid
            handoff = current_result.handoff_data
            if handoff.from_sector != current_result.sector:
                return False
            
            if handoff.to_sector != next_result.sector:
                return False
            
            # Check that evidence refs are preserved
            if not handoff.evidence_refs:
                return False
        
        return True
    
    @staticmethod
    def test_metrics_consistency(layer_run: Any) -> bool:
        """
        Test that layer run metrics are consistent with sector results.
        
        Args:
            layer_run: Layer run object
            
        Returns:
            True if metrics are consistent, False otherwise
        """
        if not layer_run.sector_results:
            return True
        
        # Calculate expected metrics
        expected_cost = sum(result.cost_usd for result in layer_run.sector_results)
        expected_latency = sum(result.execution_time_ms for result in layer_run.sector_results)
        
        # Check cost consistency
        if abs(layer_run.total_cost_usd - expected_cost) > 0.01:
            return False
        
        # Check latency consistency
        if layer_run.total_latency_ms != expected_latency:
            return False
        
        # Check that metrics exist
        if not layer_run.metrics:
            return False
        
        required_metrics = ["confidence_score", "completeness_score", "novelty_score"]
        for metric in required_metrics:
            if metric not in layer_run.metrics:
                return False
        
        return True


class GovernanceTests:
    """
    Test suite for governance invariants and system integrity.
    """
    
    def __init__(self):
        self.orchestrator = LayerOrchestrator()
        self.tracker = RefinementTracker()
        self.sector_engine = SectorEngine()
        self.escalator = EscalatorEngine()
        self.invariants = GovernanceInvariants()
    
    async def test_complete_problem_processing(self) -> Dict[str, Any]:
        """
        Test complete problem processing with all governance checks.
        
        Returns:
            Test results
        """
        test_results = {
            "test_name": "complete_problem_processing",
            "passed": True,
            "errors": [],
            "invariant_checks": {}
        }
        
        try:
            # Create a test problem
            problem_id = str(uuid.uuid4())
            problem_context = await self.orchestrator.start_problem(
                problem_id=problem_id,
                title="Test Problem",
                description="How can we reduce global carbon emissions?",
                initial_layer="deci"
            )
            
            # Process a few iterations
            for iteration in range(3):
                # Find pending layer runs
                pending_runs = [
                    run for run in problem_context.layer_runs
                    if run.status == LayerRunStatus.PENDING
                ]
                
                if pending_runs:
                    # Execute the first pending run
                    layer_run = await self.orchestrator.execute_layer_run(pending_runs[0])
                    
                    # Test sector order integrity
                    sector_order_ok = self.invariants.test_sector_order_integrity(layer_run.sector_results)
                    test_results["invariant_checks"][f"iteration_{iteration}_sector_order"] = sector_order_ok
                    
                    if not sector_order_ok:
                        test_results["errors"].append(f"Iteration {iteration}: Sector order integrity failed")
                    
                    # Test layer run completion integrity
                    completion_ok = self.invariants.test_layer_run_completion_integrity(layer_run)
                    test_results["invariant_checks"][f"iteration_{iteration}_completion"] = completion_ok
                    
                    if not completion_ok:
                        test_results["errors"].append(f"Iteration {iteration}: Layer run completion integrity failed")
                    
                    # Test handoff integrity
                    handoff_ok = self.invariants.test_handoff_integrity(layer_run.sector_results)
                    test_results["invariant_checks"][f"iteration_{iteration}_handoff"] = handoff_ok
                    
                    if not handoff_ok:
                        test_results["errors"].append(f"Iteration {iteration}: Handoff integrity failed")
                    
                    # Test metrics consistency
                    metrics_ok = self.invariants.test_metrics_consistency(layer_run)
                    test_results["invariant_checks"][f"iteration_{iteration}_metrics"] = metrics_ok
                    
                    if not metrics_ok:
                        test_results["errors"].append(f"Iteration {iteration}: Metrics consistency failed")
                
                # Make escalator decision if we have completed runs
                completed_runs = [
                    run for run in problem_context.layer_runs
                    if run.status == LayerRunStatus.COMPLETED
                ]
                
                if completed_runs:
                    decision = await self.orchestrator.make_escalator_decision(problem_context)
                    
                    # Test escalator decision integrity
                    latest_run = max(completed_runs, key=lambda r: r.finished_at)
                    decision_ok = self.invariants.test_escalator_decision_integrity(decision, latest_run.metrics)
                    test_results["invariant_checks"][f"iteration_{iteration}_escalator"] = decision_ok
                    
                    if not decision_ok:
                        test_results["errors"].append(f"Iteration {iteration}: Escalator decision integrity failed")
                    
                    # Process the decision
                    await self.orchestrator.process_escalator_decision(problem_context, decision)
            
            # Test refinement timing integrity
            refinement_timing_ok = self.invariants.test_refinement_timing_integrity(problem_context)
            test_results["invariant_checks"]["refinement_timing"] = refinement_timing_ok
            
            if not refinement_timing_ok:
                test_results["errors"].append("Refinement timing integrity failed")
            
            # Check if any errors occurred
            if test_results["errors"]:
                test_results["passed"] = False
            
        except Exception as e:
            test_results["passed"] = False
            test_results["errors"].append(f"Test execution error: {str(e)}")
        
        return test_results
    
    async def test_sector_execution_order(self) -> Dict[str, Any]:
        """
        Test that sectors are executed in the correct order.
        
        Returns:
            Test results
        """
        test_results = {
            "test_name": "sector_execution_order",
            "passed": True,
            "errors": [],
            "sector_order": []
        }
        
        try:
            # Execute a full ROYGBV cycle
            sector_results = await self.sector_engine.execute_full_cycle(
                layer="deci",
                problem_statement="Test problem for sector order"
            )
            
            # Record the order
            test_results["sector_order"] = [result.sector.value for result in sector_results]
            
            # Test order integrity
            order_ok = self.invariants.test_sector_order_integrity(sector_results)
            
            if not order_ok:
                test_results["passed"] = False
                test_results["errors"].append("Sectors not executed in correct ROYGBV order")
            
        except Exception as e:
            test_results["passed"] = False
            test_results["errors"].append(f"Test execution error: {str(e)}")
        
        return test_results
    
    async def test_escalator_decision_logic(self) -> Dict[str, Any]:
        """
        Test escalator decision logic with various scenarios.
        
        Returns:
            Test results
        """
        test_results = {
            "test_name": "escalator_decision_logic",
            "passed": True,
            "errors": [],
            "decision_tests": {}
        }
        
        try:
            # Test high confidence scenario (should resolve)
            high_confidence_solution = SolutionCandidate(
                solution_text="High confidence solution",
                confidence_score=0.95,
                completeness_score=0.90,
                alignment_score=0.95,
                net_benefit_score=0.85
            )
            
            high_confidence_metrics = {
                "confidence_score": 0.95,
                "completeness_score": 0.90,
                "revolutions_at_layer": 1
            }
            
            decision = self.escalator.decide(
                problem_id="test-001",
                current_layer="deci",
                solution_candidate=high_confidence_solution,
                layer_metrics=high_confidence_metrics
            )
            
            test_results["decision_tests"]["high_confidence"] = {
                "expected": "resolve",
                "actual": decision.action.value,
                "passed": decision.action == EscalatorAction.RESOLVE
            }
            
            if decision.action != EscalatorAction.RESOLVE:
                test_results["errors"].append("High confidence scenario should resolve")
            
            # Test low confidence scenario (should refine)
            low_confidence_solution = SolutionCandidate(
                solution_text="Low confidence solution",
                confidence_score=0.60,
                completeness_score=0.55,
                alignment_score=0.90,
                net_benefit_score=0.70
            )
            
            low_confidence_metrics = {
                "confidence_score": 0.60,
                "completeness_score": 0.55,
                "revolutions_at_layer": 1
            }
            
            decision = self.escalator.decide(
                problem_id="test-002",
                current_layer="deci",
                solution_candidate=low_confidence_solution,
                layer_metrics=low_confidence_metrics
            )
            
            test_results["decision_tests"]["low_confidence"] = {
                "expected": "refine",
                "actual": decision.action.value,
                "passed": decision.action == EscalatorAction.REFINE
            }
            
            if decision.action != EscalatorAction.REFINE:
                test_results["errors"].append("Low confidence scenario should refine")
            
            # Test max revolutions scenario (should refine)
            max_revolutions_solution = SolutionCandidate(
                solution_text="Max revolutions solution",
                confidence_score=0.80,
                completeness_score=0.75,
                alignment_score=0.90,
                net_benefit_score=0.80
            )
            
            max_revolutions_metrics = {
                "confidence_score": 0.80,
                "completeness_score": 0.75,
                "revolutions_at_layer": 5  # Max for deci layer
            }
            
            decision = self.escalator.decide(
                problem_id="test-003",
                current_layer="deci",
                solution_candidate=max_revolutions_solution,
                layer_metrics=max_revolutions_metrics
            )
            
            test_results["decision_tests"]["max_revolutions"] = {
                "expected": "refine",
                "actual": decision.action.value,
                "passed": decision.action == EscalatorAction.REFINE
            }
            
            if decision.action != EscalatorAction.REFINE:
                test_results["errors"].append("Max revolutions scenario should refine")
            
            # Check if any errors occurred
            if test_results["errors"]:
                test_results["passed"] = False
            
        except Exception as e:
            test_results["passed"] = False
            test_results["errors"].append(f"Test execution error: {str(e)}")
        
        return test_results
    
    async def test_refinement_tracking(self) -> Dict[str, Any]:
        """
        Test refinement tracking and genealogy logging.
        
        Returns:
            Test results
        """
        test_results = {
            "test_name": "refinement_tracking",
            "passed": True,
            "errors": [],
            "tracking_checks": {}
        }
        
        try:
            problem_id = str(uuid.uuid4())
            
            # Create initial node
            node1 = self.tracker.create_refinement_node(problem_id, "deci", 1)
            
            # Update node
            self.tracker.update_refinement_node(node1, "completed", {
                "confidence_score": 0.75,
                "completeness_score": 0.70
            })
            
            # Track refinement
            self.tracker.track_refinement(problem_id, "deci", "centi", "Low confidence", "Refined question", node1)
            
            # Create refined node
            node2 = self.tracker.create_refinement_node(problem_id, "centi", 1, parent_node_id=node1)
            
            # Update refined node
            self.tracker.update_refinement_node(node2, "completed", {
                "confidence_score": 0.85,
                "completeness_score": 0.80
            })
            
            # Get genealogy
            genealogy = self.tracker.get_problem_genealogy(problem_id)
            
            # Check genealogy structure
            test_results["tracking_checks"]["genealogy_structure"] = {
                "total_nodes": len(genealogy.get("nodes", [])),
                "layers_visited": genealogy.get("layers_visited", []),
                "max_depth": genealogy.get("max_depth", 0),
                "passed": len(genealogy.get("nodes", [])) == 2
            }
            
            if len(genealogy.get("nodes", [])) != 2:
                test_results["errors"].append("Genealogy should have 2 nodes")
            
            # Check parent-child relationship
            nodes = genealogy.get("nodes", [])
            if len(nodes) >= 2:
                parent_node = next((n for n in nodes if n["node_id"] == node1), None)
                child_node = next((n for n in nodes if n["node_id"] == node2), None)
                
                if parent_node and child_node:
                    relationship_ok = (
                        child_node["parent_node_id"] == node1 and
                        node1 in [n["node_id"] for n in nodes if n["parent_node_id"] == node1]
                    )
                    test_results["tracking_checks"]["parent_child_relationship"] = {
                        "passed": relationship_ok
                    }
                    
                    if not relationship_ok:
                        test_results["errors"].append("Parent-child relationship not properly tracked")
            
            # Get analytics
            analytics = self.tracker.get_refinement_analytics(problem_id)
            
            test_results["tracking_checks"]["analytics"] = {
                "success_rate": analytics.get("success_rate", 0.0),
                "refinement_efficiency": analytics.get("refinement_efficiency", 0.0),
                "passed": analytics.get("success_rate", 0.0) == 1.0  # Both nodes completed
            }
            
            if analytics.get("success_rate", 0.0) != 1.0:
                test_results["errors"].append("Success rate should be 100%")
            
            # Check if any errors occurred
            if test_results["errors"]:
                test_results["passed"] = False
            
        except Exception as e:
            test_results["passed"] = False
            test_results["errors"].append(f"Test execution error: {str(e)}")
        
        return test_results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all governance tests.
        
        Returns:
            Complete test results
        """
        all_results = {
            "test_suite": "governance_tests",
            "timestamp": datetime.utcnow().isoformat(),
            "tests": [],
            "overall_passed": True,
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0
            }
        }
        
        # Run all tests
        tests = [
            self.test_complete_problem_processing(),
            self.test_sector_execution_order(),
            self.test_escalator_decision_logic(),
            self.test_refinement_tracking()
        ]
        
        for test_coro in tests:
            result = await test_coro
            all_results["tests"].append(result)
            all_results["summary"]["total_tests"] += 1
            
            if result["passed"]:
                all_results["summary"]["passed_tests"] += 1
            else:
                all_results["summary"]["failed_tests"] += 1
                all_results["overall_passed"] = False
        
        return all_results


# Example usage and testing
if __name__ == "__main__":
    async def run_governance_tests():
        print("=== Governance Tests ===")
        
        tests = GovernanceTests()
        results = await tests.run_all_tests()
        
        print(f"Overall passed: {results['overall_passed']}")
        print(f"Total tests: {results['summary']['total_tests']}")
        print(f"Passed: {results['summary']['passed_tests']}")
        print(f"Failed: {results['summary']['failed_tests']}")
        
        for test in results["tests"]:
            print(f"\n{test['test_name']}: {'PASSED' if test['passed'] else 'FAILED'}")
            if test["errors"]:
                for error in test["errors"]:
                    print(f"  Error: {error}")
    
    # Run the tests
    asyncio.run(run_governance_tests())
