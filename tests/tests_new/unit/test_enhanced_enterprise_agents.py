"""
Unit tests for Enhanced Enterprise Agents
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

from enhanced_enterprise_agents import (
    EnhancedEnterpriseAgent, EnhancedRedOwlAgent, EnhancedOrangeOrangutanAgent,
    Problem, ProblemComplexity, EnhancedResult
)


class TestEnhancedEnterpriseAgent:
    """Test the base EnhancedEnterpriseAgent class."""
    
    def test_enhanced_enterprise_agent_initialization(self):
        """Test enhanced enterprise agent initialization."""
        agent = EnhancedRedOwlAgent()
        
        assert agent.name == "Red Owl"
        assert agent.role == "Research & Knowledge Gathering"
        assert agent.color == "#ef4444"
        assert agent.analysis_frameworks is not None
        assert agent.quality_metrics is not None
    
    def test_enhanced_enterprise_agent_abstract_methods(self):
        """Test that abstract methods are properly defined."""
        # Test that we can't instantiate the abstract base class
        with pytest.raises(TypeError):
            EnhancedEnterpriseAgent()
    
    @pytest.mark.asyncio
    async def test_process_problem_enhanced_structure(self, sample_problem):
        """Test the structure of enhanced problem processing."""
        agent = EnhancedRedOwlAgent()
        
        result = await agent.process_problem_enhanced(sample_problem)
        
        # Test result structure
        assert isinstance(result, dict)
        assert "status" in result
        assert "confidence_score" in result
        assert "insights" in result
        assert "recommendations" in result
        assert "analysis_depth" in result
        assert "framework_applied" in result
        assert "processing_time" in result
        assert "quality_score" in result
        assert "metadata" in result
        
        # Test result values
        assert result["status"] in ["completed", "failed", "partial"]
        assert 0.0 <= result["confidence_score"] <= 1.0
        assert isinstance(result["insights"], list)
        assert isinstance(result["recommendations"], list)
        assert result["analysis_depth"] in ["shallow", "moderate", "deep"]
        assert isinstance(result["framework_applied"], str)
        assert result["processing_time"] > 0
        assert 0.0 <= result["quality_score"] <= 1.0
        assert isinstance(result["metadata"], dict)


class TestEnhancedRedOwlAgent:
    """Test the Enhanced Red Owl Agent."""
    
    def test_red_owl_agent_initialization(self):
        """Test Red Owl agent initialization."""
        agent = EnhancedRedOwlAgent()
        
        assert agent.name == "Red Owl"
        assert agent.role == "Research & Knowledge Gathering"
        assert agent.color == "#ef4444"
        assert len(agent.analysis_frameworks) > 0
        assert len(agent.quality_metrics) > 0
    
    def test_red_owl_agent_frameworks(self):
        """Test Red Owl agent analysis frameworks."""
        agent = EnhancedRedOwlAgent()
        
        frameworks = agent.analysis_frameworks
        assert "SWOT Analysis" in frameworks
        assert "PEST Analysis" in frameworks
        assert "Root Cause Analysis" in frameworks
        assert "Stakeholder Analysis" in frameworks
        assert "Risk Assessment" in frameworks
    
    def test_red_owl_agent_quality_metrics(self):
        """Test Red Owl agent quality metrics."""
        agent = EnhancedRedOwlAgent()
        
        metrics = agent.quality_metrics
        assert "data_accuracy" in metrics
        assert "source_reliability" in metrics
        assert "analysis_depth" in metrics
        assert "insight_quality" in metrics
        assert "recommendation_feasibility" in metrics
    
    @pytest.mark.asyncio
    async def test_red_owl_problem_processing(self, sample_problem):
        """Test Red Owl agent problem processing."""
        agent = EnhancedRedOwlAgent()
        
        result = await agent.process_problem_enhanced(sample_problem)
        
        assert result["status"] == "completed"
        assert result["confidence_score"] > 0.0
        assert len(result["insights"]) > 0
        assert len(result["recommendations"]) > 0
        assert result["analysis_depth"] in ["shallow", "moderate", "deep"]
        assert result["framework_applied"] in agent.analysis_frameworks
        assert result["processing_time"] > 0
        assert result["quality_score"] > 0.0
    
    @pytest.mark.asyncio
    async def test_red_owl_research_conduct(self, sample_problem):
        """Test Red Owl research conduct."""
        agent = EnhancedRedOwlAgent()
        
        result = await agent._conduct_research(sample_problem)
        
        assert isinstance(result, dict)
        assert "data_sources" in result
        assert "research_findings" in result
        assert "knowledge_gaps" in result
        assert "confidence_level" in result
        
        assert isinstance(result["data_sources"], list)
        assert isinstance(result["research_findings"], list)
        assert isinstance(result["knowledge_gaps"], list)
        assert 0.0 <= result["confidence_level"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_red_owl_analysis_depth_scaling(self):
        """Test that analysis depth scales with problem complexity."""
        agent = EnhancedRedOwlAgent()
        
        # Test simple problem
        simple_problem = Problem(
            title="Simple Test",
            description="Simple test",
            complexity=ProblemComplexity.SIMPLE,
            domain="Test"
        )
        simple_result = await agent.process_problem_enhanced(simple_problem)
        
        # Test complex problem
        complex_problem = Problem(
            title="Complex Test",
            description="Complex test",
            complexity=ProblemComplexity.COMPLEX,
            domain="Test"
        )
        complex_result = await agent.process_problem_enhanced(complex_problem)
        
        # Complex problems should have deeper analysis
        depth_order = {"shallow": 1, "moderate": 2, "deep": 3}
        assert depth_order[complex_result["analysis_depth"]] >= depth_order[simple_result["analysis_depth"]]
    
    @pytest.mark.asyncio
    async def test_red_owl_framework_selection(self, sample_problem):
        """Test that appropriate frameworks are selected."""
        agent = EnhancedRedOwlAgent()
        
        result = await agent.process_problem_enhanced(sample_problem)
        
        # Should select a valid framework
        assert result["framework_applied"] in agent.analysis_frameworks
        
        # Framework should be appropriate for the problem
        if "business" in sample_problem.domain.lower():
            assert result["framework_applied"] in ["SWOT Analysis", "PEST Analysis", "Stakeholder Analysis"]
    
    @pytest.mark.asyncio
    async def test_red_owl_quality_assurance(self, sample_problem):
        """Test Red Owl quality assurance."""
        agent = EnhancedRedOwlAgent()
        
        result = await agent.process_problem_enhanced(sample_problem)
        
        # Quality score should be reasonable
        assert 0.0 <= result["quality_score"] <= 1.0
        assert result["quality_score"] > 0.5  # Should be above minimum threshold
        
        # Metadata should include quality information
        assert "quality_metrics" in result["metadata"]
        assert "validation_results" in result["metadata"]


class TestEnhancedOrangeOrangutanAgent:
    """Test the Enhanced Orange Orangutan Agent."""
    
    def test_orange_orangutan_agent_initialization(self):
        """Test Orange Orangutan agent initialization."""
        agent = EnhancedOrangeOrangutanAgent()
        
        assert agent.name == "Orange Orangutan"
        assert agent.role == "Logistics & Strategic Planning"
        assert agent.color == "#f97316"
        assert len(agent.analysis_frameworks) > 0
        assert len(agent.quality_metrics) > 0
    
    def test_orange_orangutan_agent_frameworks(self):
        """Test Orange Orangutan agent analysis frameworks."""
        agent = EnhancedOrangeOrangutanAgent()
        
        frameworks = agent.analysis_frameworks
        assert "Strategic Planning" in frameworks
        assert "Resource Allocation" in frameworks
        assert "Timeline Planning" in frameworks
        assert "Risk Management" in frameworks
        assert "Stakeholder Coordination" in frameworks
    
    def test_orange_orangutan_agent_quality_metrics(self):
        """Test Orange Orangutan agent quality metrics."""
        agent = EnhancedOrangeOrangutanAgent()
        
        metrics = agent.quality_metrics
        assert "plan_feasibility" in metrics
        assert "resource_efficiency" in metrics
        assert "timeline_realism" in metrics
        assert "risk_coverage" in metrics
        assert "stakeholder_alignment" in metrics
    
    @pytest.mark.asyncio
    async def test_orange_orangutan_problem_processing(self, sample_problem):
        """Test Orange Orangutan agent problem processing."""
        agent = EnhancedOrangeOrangutanAgent()
        
        result = await agent.process_problem_enhanced(sample_problem)
        
        assert result["status"] == "completed"
        assert result["confidence_score"] > 0.0
        assert len(result["insights"]) > 0
        assert len(result["recommendations"]) > 0
        assert result["analysis_depth"] in ["shallow", "moderate", "deep"]
        assert result["framework_applied"] in agent.analysis_frameworks
        assert result["processing_time"] > 0
        assert result["quality_score"] > 0.0
    
    @pytest.mark.asyncio
    async def test_orange_orangutan_logistics_planning(self, sample_problem):
        """Test Orange Orangutan logistics planning."""
        agent = EnhancedOrangeOrangutanAgent()
        
        result = await agent._conduct_logistics_planning(sample_problem)
        
        assert isinstance(result, dict)
        assert "resource_requirements" in result
        assert "timeline_plan" in result
        assert "risk_assessment" in result
        assert "stakeholder_coordination" in result
        assert "efficiency_metrics" in result
        
        assert isinstance(result["resource_requirements"], dict)
        assert isinstance(result["timeline_plan"], dict)
        assert isinstance(result["risk_assessment"], list)
        assert isinstance(result["stakeholder_coordination"], list)
        assert isinstance(result["efficiency_metrics"], dict)
    
    @pytest.mark.asyncio
    async def test_orange_orangutan_resource_optimization(self, sample_problem):
        """Test Orange Orangutan resource optimization."""
        agent = EnhancedOrangeOrangutanAgent()
        
        result = await agent._optimize_resources(sample_problem)
        
        assert isinstance(result, dict)
        assert "optimized_allocation" in result
        assert "cost_analysis" in result
        assert "efficiency_improvements" in result
        assert "constraint_handling" in result
        
        assert isinstance(result["optimized_allocation"], dict)
        assert isinstance(result["cost_analysis"], dict)
        assert isinstance(result["efficiency_improvements"], list)
        assert isinstance(result["constraint_handling"], dict)
    
    @pytest.mark.asyncio
    async def test_orange_orangutan_timeline_planning(self, sample_problem):
        """Test Orange Orangutan timeline planning."""
        agent = EnhancedOrangeOrangutanAgent()
        
        result = await agent._create_timeline_plan(sample_problem)
        
        assert isinstance(result, dict)
        assert "milestones" in result
        assert "dependencies" in result
        assert "critical_path" in result
        assert "buffer_time" in result
        
        assert isinstance(result["milestones"], list)
        assert isinstance(result["dependencies"], list)
        assert isinstance(result["critical_path"], list)
        assert isinstance(result["buffer_time"], dict)
    
    @pytest.mark.asyncio
    async def test_orange_orangutan_complexity_handling(self):
        """Test Orange Orangutan handling of different problem complexities."""
        agent = EnhancedOrangeOrangutanAgent()
        
        # Test simple problem
        simple_problem = Problem(
            title="Simple Test",
            description="Simple test",
            complexity=ProblemComplexity.SIMPLE,
            domain="Test"
        )
        simple_result = await agent.process_problem_enhanced(simple_problem)
        
        # Test complex problem
        complex_problem = Problem(
            title="Complex Test",
            description="Complex test",
            complexity=ProblemComplexity.COMPLEX,
            domain="Test"
        )
        complex_result = await agent.process_problem_enhanced(complex_problem)
        
        # Complex problems should have more detailed planning
        assert len(complex_result["insights"]) >= len(simple_result["insights"])
        assert len(complex_result["recommendations"]) >= len(simple_result["recommendations"])
        
        # Complex problems should have deeper analysis
        depth_order = {"shallow": 1, "moderate": 2, "deep": 3}
        assert depth_order[complex_result["analysis_depth"]] >= depth_order[simple_result["analysis_depth"]]


class TestEnhancedResult:
    """Test the EnhancedResult class."""
    
    def test_enhanced_result_creation(self):
        """Test creating an enhanced result."""
        result = EnhancedResult(
            status="completed",
            confidence_score=0.85,
            insights=["Insight 1", "Insight 2"],
            recommendations=["Recommendation 1", "Recommendation 2"],
            analysis_depth="moderate",
            framework_applied="SWOT Analysis",
            processing_time=2.5,
            quality_score=0.9,
            metadata={"test": "value"}
        )
        
        assert result.status == "completed"
        assert result.confidence_score == 0.85
        assert result.insights == ["Insight 1", "Insight 2"]
        assert result.recommendations == ["Recommendation 1", "Recommendation 2"]
        assert result.analysis_depth == "moderate"
        assert result.framework_applied == "SWOT Analysis"
        assert result.processing_time == 2.5
        assert result.quality_score == 0.9
        assert result.metadata == {"test": "value"}
    
    def test_enhanced_result_validation(self):
        """Test enhanced result validation."""
        # Test valid confidence score
        result = EnhancedResult(
            status="completed",
            confidence_score=0.8,
            insights=[],
            recommendations=[],
            analysis_depth="moderate",
            framework_applied="Test Framework",
            processing_time=1.0,
            quality_score=0.8,
            metadata={}
        )
        assert result.confidence_score == 0.8
        
        # Test invalid confidence score
        with pytest.raises(ValueError):
            EnhancedResult(
                status="completed",
                confidence_score=1.1,  # Invalid: > 1.0
                insights=[],
                recommendations=[],
                analysis_depth="moderate",
                framework_applied="Test Framework",
                processing_time=1.0,
                quality_score=0.8,
                metadata={}
            )
        
        # Test invalid quality score
        with pytest.raises(ValueError):
            EnhancedResult(
                status="completed",
                confidence_score=0.8,
                insights=[],
                recommendations=[],
                analysis_depth="moderate",
                framework_applied="Test Framework",
                processing_time=1.0,
                quality_score=1.1,  # Invalid: > 1.0
                metadata={}
            )
    
    def test_enhanced_result_analysis_depth_validation(self):
        """Test analysis depth validation."""
        valid_depths = ["shallow", "moderate", "deep"]
        
        for depth in valid_depths:
            result = EnhancedResult(
                status="completed",
                confidence_score=0.8,
                insights=[],
                recommendations=[],
                analysis_depth=depth,
                framework_applied="Test Framework",
                processing_time=1.0,
                quality_score=0.8,
                metadata={}
            )
            assert result.analysis_depth == depth
        
        # Test invalid analysis depth
        with pytest.raises(ValueError):
            EnhancedResult(
                status="completed",
                confidence_score=0.8,
                insights=[],
                recommendations=[],
                analysis_depth="invalid_depth",
                framework_applied="Test Framework",
                processing_time=1.0,
                quality_score=0.8,
                metadata={}
            )


class TestProblemComplexityHandling:
    """Test problem complexity handling across agents."""
    
    @pytest.mark.asyncio
    async def test_complexity_scaling_across_agents(self):
        """Test that complexity scaling works across different agents."""
        red_owl = EnhancedRedOwlAgent()
        orange_orangutan = EnhancedOrangeOrangutanAgent()
        
        # Test simple problem
        simple_problem = Problem(
            title="Simple Test",
            description="Simple test",
            complexity=ProblemComplexity.SIMPLE,
            domain="Test"
        )
        
        simple_red_result = await red_owl.process_problem_enhanced(simple_problem)
        simple_orange_result = await orange_orangutan.process_problem_enhanced(simple_problem)
        
        # Test complex problem
        complex_problem = Problem(
            title="Complex Test",
            description="Complex test",
            complexity=ProblemComplexity.COMPLEX,
            domain="Test"
        )
        
        complex_red_result = await red_owl.process_problem_enhanced(complex_problem)
        complex_orange_result = await orange_orangutan.process_problem_enhanced(complex_problem)
        
        # Both agents should scale with complexity
        depth_order = {"shallow": 1, "moderate": 2, "deep": 3}
        
        assert depth_order[complex_red_result["analysis_depth"]] >= depth_order[simple_red_result["analysis_depth"]]
        assert depth_order[complex_orange_result["analysis_depth"]] >= depth_order[simple_orange_result["analysis_depth"]]
        
        # Complex problems should have more insights and recommendations
        assert len(complex_red_result["insights"]) >= len(simple_red_result["insights"])
        assert len(complex_orange_result["insights"]) >= len(simple_orange_result["insights"])
        assert len(complex_red_result["recommendations"]) >= len(simple_red_result["recommendations"])
        assert len(complex_orange_result["recommendations"]) >= len(simple_orange_result["recommendations"])
    
    @pytest.mark.asyncio
    async def test_agent_specialization(self):
        """Test that agents provide specialized results."""
        red_owl = EnhancedRedOwlAgent()
        orange_orangutan = EnhancedOrangeOrangutanAgent()
        
        problem = Problem(
            title="Specialization Test",
            description="Test agent specialization",
            complexity=ProblemComplexity.MODERATE,
            domain="Test"
        )
        
        red_result = await red_owl.process_problem_enhanced(problem)
        orange_result = await orange_orangutan.process_problem_enhanced(problem)
        
        # Red Owl should focus on research frameworks
        assert red_result["framework_applied"] in red_owl.analysis_frameworks
        assert any("research" in insight.lower() or "data" in insight.lower() 
                  for insight in red_result["insights"])
        
        # Orange Orangutan should focus on logistics frameworks
        assert orange_result["framework_applied"] in orange_orangutan.analysis_frameworks
        assert any("logistics" in insight.lower() or "planning" in insight.lower() 
                  for insight in orange_result["insights"])
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in enhanced agents."""
        agent = EnhancedRedOwlAgent()
        
        # Test with None problem
        with pytest.raises(ValueError):
            await agent.process_problem_enhanced(None)
        
        # Test with invalid problem type
        with pytest.raises(TypeError):
            await agent.process_problem_enhanced("invalid_problem")
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """Test concurrent processing of multiple problems."""
        agent = EnhancedRedOwlAgent()
        
        # Create multiple problems
        problems = []
        for i in range(5):
            problem = Problem(
                title=f"Concurrent Test {i}",
                description=f"Concurrent test problem {i}",
                complexity=ProblemComplexity.SIMPLE,
                domain="Test"
            )
            problems.append(problem)
        
        # Process all problems concurrently
        tasks = [agent.process_problem_enhanced(problem) for problem in problems]
        results = await asyncio.gather(*tasks)
        
        # Verify all problems were processed
        assert len(results) == 5
        for result in results:
            assert result["status"] == "completed"
            assert result["confidence_score"] > 0.0
            assert len(result["insights"]) > 0
            assert len(result["recommendations"]) > 0
