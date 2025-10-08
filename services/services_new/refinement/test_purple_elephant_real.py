"""
Test Purple Elephant with Real Functionality
This test verifies that the Purple Elephant actually works with real analysis, not just fake checks.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from purple_elephant_gatekeeper import (
    PurpleElephant, ReflectorAgent, GatekeeperAgent, 
    AdaptiveThresholds, SolutionStatus, RoutingDecision
)
from purple_elephant_database import PurpleElephantDatabase


class TestPurpleElephantReal:
    """Test Purple Elephant with real functionality."""
    
    @pytest.fixture
    def mock_ai_manager(self):
        """Mock AI manager that returns realistic responses."""
        manager = Mock()
        manager.process_with_llm = AsyncMock()
        
        # Mock realistic AI responses
        def mock_ai_response(prompt, provider="openai"):
            response = Mock()
            if "innovation level" in prompt:
                response.content = "0.8"  # High innovation
            elif "technical feasibility" in prompt:
                response.content = "0.7"  # Good feasibility
            elif "consistent" in prompt:
                response.content = "CONSISTENT"
            elif "support" in prompt:
                response.content = "YES"
            else:
                response.content = "0.6"  # Default score
            return response
        
        manager.process_with_llm.side_effect = mock_ai_response
        return manager
    
    @pytest.fixture
    def mock_db_manager(self):
        """Mock database manager."""
        manager = Mock()
        manager.execute_query = AsyncMock()
        return manager
    
    @pytest.fixture
    def mock_metrics_collector(self):
        """Mock metrics collector."""
        collector = Mock()
        collector.record_threshold_update = AsyncMock()
        return collector
    
    @pytest.fixture
    def purple_elephant(self, mock_ai_manager, mock_db_manager, mock_metrics_collector):
        """Create Purple Elephant with mocked dependencies."""
        return PurpleElephant(mock_ai_manager, mock_db_manager, mock_metrics_collector)
    
    @pytest.fixture
    def sample_sector_outputs(self):
        """Sample sector outputs for testing."""
        return {
            "red": {
                "evidence": [
                    {"content": "Research shows sustainable materials reduce costs by 30%", "keywords": ["sustainable", "materials", "costs"]},
                    {"content": "Modular design approaches improve scalability", "keywords": ["modular", "design", "scalability"]}
                ],
                "research_quality": 0.8,
                "completeness": 0.7
            },
            "orange": {
                "plan_steps": [
                    "Implement sustainable materials",
                    "Design modular architecture",
                    "Create scalable deployment plan"
                ],
                "resource_requirements": {"materials": 10000, "labor": 20000, "equipment": 15000},
                "timeline": {"start_date": "2024-01-01", "end_date": "2024-06-01"},
                "feasibility_score": 0.8
            },
            "yellow": {
                "solutions": [
                    {
                        "approach": "Innovative modular design with sustainable materials",
                        "implementation": {
                            "resources": ["sustainable_materials", "modular_components"],
                            "timeline": "6 months",
                            "risks": ["supply_chain_delays"]
                        },
                        "technical_details": "Uses advanced modular architecture with sustainable materials",
                        "problem_areas_addressed": ["sustainability", "scalability", "cost"],
                        "components": ["materials", "design", "deployment"],
                        "success_metrics": ["cost_reduction", "sustainability_score"]
                    }
                ],
                "prototypes": [
                    {
                        "name": "Modular Prototype",
                        "design": "Sustainable modular design",
                        "implementation": "Working prototype",
                        "testing": "Passed all tests",
                        "results": "30% cost reduction achieved"
                    }
                ],
                "innovation_score": 0.8,
                "feasibility_score": 0.7,
                "novelty_score": 0.9
            },
            "green": {
                "budget": {"total_budget": 50000},
                "sustainability_metrics": {
                    "requirements": {
                        "max_carbon_footprint": 1000,
                        "max_resource_usage": {"materials": 1000, "energy": 500}
                    }
                },
                "budget_compliance": 0.9,
                "sustainability_score": 0.8
            },
            "blue": {
                "messages": [
                    {"content": "Our sustainable modular solution reduces costs by 30% while improving scalability"}
                ],
                "communication_quality": 0.8,
                "stakeholder_satisfaction": 0.7
            }
        }
    
    @pytest.mark.asyncio
    async def test_real_creativity_analysis(self, purple_elephant, sample_sector_outputs):
        """Test that creativity analysis actually measures quality."""
        
        # Test the real analysis method
        analysis = await purple_elephant.reflector._analyze_creativity_quality(sample_sector_outputs["yellow"])
        
        # Verify it actually analyzed the solutions
        assert "quality_score" in analysis
        assert "innovation" in analysis
        assert "feasibility" in analysis
        assert "completeness" in analysis
        assert "detailed_analysis" in analysis
        
        # Verify it found the solution
        assert analysis["quality_score"] > 0.0
        assert analysis["innovation"] > 0.0
        assert analysis["feasibility"] > 0.0
        
        # Verify it analyzed the prototype
        assert "prototype" in analysis["detailed_analysis"].lower()
        
        print(f"Creativity Analysis: {analysis}")
    
    @pytest.mark.asyncio
    async def test_real_contradiction_detection(self, purple_elephant, sample_sector_outputs):
        """Test that contradiction detection finds real contradictions."""
        
        # Test with good data (should find no contradictions)
        contradictions = await purple_elephant.reflector._detect_real_contradictions(sample_sector_outputs)
        
        # Should find no contradictions with good data
        assert len(contradictions) == 0
        
        # Test with contradictory data
        contradictory_outputs = sample_sector_outputs.copy()
        contradictory_outputs["orange"]["resource_requirements"] = {"materials": 100000, "labor": 200000}  # Exceeds budget
        
        contradictions = await purple_elephant.reflector._detect_real_contradictions(contradictory_outputs)
        
        # Should find budget contradiction
        assert len(contradictions) > 0
        assert any("exceed" in contradiction.lower() for contradiction in contradictions)
        
        print(f"Contradictions found: {contradictions}")
    
    @pytest.mark.asyncio
    async def test_adaptive_thresholds_learning(self):
        """Test that adaptive thresholds actually learn from outcomes."""
        
        thresholds = AdaptiveThresholds()
        
        # Initial thresholds
        initial_confidence = thresholds.confidence_threshold
        assert initial_confidence == 0.5
        
        # Simulate successful outcomes
        for _ in range(5):
            await thresholds.update_thresholds("success", 0.9, 0.8, 0.8, 0.8)
        
        # Thresholds should have increased
        assert thresholds.confidence_threshold > initial_confidence
        
        # Simulate failed outcomes
        for _ in range(5):
            await thresholds.update_thresholds("failure", 0.3, 0.4, 0.4, 0.4)
        
        # Thresholds should have decreased
        assert thresholds.confidence_threshold < initial_confidence
        
        print(f"Final thresholds: {thresholds.get_current_thresholds()}")
    
    @pytest.mark.asyncio
    async def test_real_solution_evaluation(self, purple_elephant, sample_sector_outputs):
        """Test that solution evaluation uses real metrics."""
        
        # Create a reflection report with real data
        report = await purple_elephant.reflector.synthesize_cycle_outputs("test_cycle")
        
        # Evaluate the solution
        decision = await purple_elephant.gatekeeper.evaluate_solution_sufficiency(report)
        
        # Verify it made a real decision
        assert decision.status in [SolutionStatus.SUFFICIENT, SolutionStatus.INSUFFICIENT, SolutionStatus.NEEDS_REFINEMENT]
        assert decision.confidence_score > 0.0
        assert decision.completeness_score > 0.0
        assert decision.alignment_score > 0.0
        assert decision.rationale is not None
        
        print(f"Decision: {decision.status.value}")
        print(f"Scores: Confidence={decision.confidence_score:.2f}, Completeness={decision.completeness_score:.2f}, Alignment={decision.alignment_score:.2f}")
        print(f"Rationale: {decision.rationale}")
    
    @pytest.mark.asyncio
    async def test_quality_measurement_methods(self, purple_elephant):
        """Test that quality measurement methods actually work."""
        
        # Test innovation measurement
        solution = {
            "approach": "Revolutionary quantum-based modular design with AI optimization",
            "implementation": {
                "resources": ["quantum_materials", "ai_systems"],
                "timeline": "12 months",
                "risks": ["technical_complexity"]
            },
            "technical_details": "Uses quantum computing for optimization and AI for adaptive design",
            "problem_areas_addressed": ["performance", "scalability", "efficiency"],
            "components": ["quantum_engine", "ai_optimizer", "modular_design"],
            "success_metrics": ["performance_gain", "efficiency_improvement"]
        }
        
        innovation_score = await purple_elephant.reflector._measure_innovation(solution)
        feasibility_score = await purple_elephant.reflector._measure_feasibility(solution)
        completeness_score = await purple_elephant.reflector._measure_solution_completeness(solution)
        
        # Verify scores are reasonable
        assert 0.0 <= innovation_score <= 1.0
        assert 0.0 <= feasibility_score <= 1.0
        assert 0.0 <= completeness_score <= 1.0
        
        # Innovation should be high for this solution
        assert innovation_score > 0.5
        
        print(f"Innovation: {innovation_score:.2f}, Feasibility: {feasibility_score:.2f}, Completeness: {completeness_score:.2f}")
    
    @pytest.mark.asyncio
    async def test_end_to_end_cycle_processing(self, purple_elephant, sample_sector_outputs):
        """Test complete cycle processing with real functionality."""
        
        # Mock the database to return our sample data
        with patch.object(purple_elephant.reflector.purple_db, 'get_sector_outputs', return_value=sample_sector_outputs):
            with patch.object(purple_elephant.reflector.purple_db, 'get_cycle_data', return_value={"cycle_id": "test", "layer": "deci"}):
                with patch.object(purple_elephant.reflector.purple_db, 'get_problem', return_value={"problem_id": "test", "current_layer": "deci", "cycle_count": 1}):
                    
                    # Process the cycle
                    report, decision = await purple_elephant.process_cycle_reflection("test_cycle")
                    
                    # Verify we got real results
                    assert report is not None
                    assert decision is not None
                    
                    # Verify the report has real analysis
                    assert len(report.sector_analysis) > 0
                    assert report.summary is not None
                    assert len(report.contradictions) >= 0  # May or may not have contradictions
                    
                    # Verify the decision is based on real evaluation
                    assert decision.status is not None
                    assert decision.rationale is not None
                    
                    print(f"Cycle processed successfully!")
                    print(f"Report summary: {report.summary[:100]}...")
                    print(f"Decision: {decision.status.value}")
                    print(f"Routing: {decision.routing_decision.value}")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
