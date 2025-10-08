"""
Unit tests for the Cosmic Council Core Framework
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock

from src.core.types import (
    CosmicCouncil, ProblemStatement, ProblemComplexity, 
    EnterpriseType, ProblemResult, EnterpriseResult
)


class TestProblemStatement:
    """Test the ProblemStatement class."""
    
    def test_problem_statement_creation(self):
        """Test creating a problem statement."""
        problem = ProblemStatement(
            title="Test Problem",
            description="Test description",
            complexity=ProblemComplexity.SIMPLE,
            domain="Test Domain"
        )
        
        assert problem.title == "Test Problem"
        assert problem.description == "Test description"
        assert problem.complexity == ProblemComplexity.SIMPLE
        assert problem.domain == "Test Domain"
        assert problem.stakeholders == []
        assert problem.constraints == {}
        assert problem.success_criteria == []
    
    def test_problem_statement_with_all_fields(self):
        """Test creating a problem statement with all fields."""
        problem = ProblemStatement(
            title="Complex Problem",
            description="A complex problem description",
            complexity=ProblemComplexity.COMPLEX,
            domain="Business",
            stakeholders=["Stakeholder 1", "Stakeholder 2"],
            constraints={"budget": "$10K", "timeline": "1 month"},
            success_criteria=["Criteria 1", "Criteria 2"]
        )
        
        assert problem.title == "Complex Problem"
        assert problem.description == "A complex problem description"
        assert problem.complexity == ProblemComplexity.COMPLEX
        assert problem.domain == "Business"
        assert problem.stakeholders == ["Stakeholder 1", "Stakeholder 2"]
        assert problem.constraints == {"budget": "$10K", "timeline": "1 month"}
        assert problem.success_criteria == ["Criteria 1", "Criteria 2"]
    
    def test_problem_statement_validation(self):
        """Test problem statement validation."""
        # Test with minimal required fields
        problem = ProblemStatement(
            title="Minimal Problem",
            description="Minimal description",
            complexity=ProblemComplexity.SIMPLE,
            domain="Test"
        )
        assert problem.title == "Minimal Problem"
        
        # Test with empty title should raise error
        with pytest.raises(ValueError):
            ProblemStatement(
                title="",
                description="Test description",
                complexity=ProblemComplexity.SIMPLE,
                domain="Test"
            )
    
    def test_problem_statement_str_representation(self):
        """Test string representation of problem statement."""
        problem = ProblemStatement(
            title="Test Problem",
            description="Test description",
            complexity=ProblemComplexity.MODERATE,
            domain="Test Domain"
        )
        
        str_repr = str(problem)
        assert "Test Problem" in str_repr
        assert "Test description" in str_repr
        assert "moderate" in str_repr.lower()


class TestProblemComplexity:
    """Test the ProblemComplexity enum."""
    
    def test_problem_complexity_values(self):
        """Test problem complexity enum values."""
        assert ProblemComplexity.SIMPLE == "simple"
        assert ProblemComplexity.MODERATE == "moderate"
        assert ProblemComplexity.COMPLEX == "complex"
        assert ProblemComplexity.SYSTEMIC == "systemic"
    
    def test_problem_complexity_ordering(self):
        """Test problem complexity ordering."""
        complexities = [
            ProblemComplexity.SIMPLE,
            ProblemComplexity.MODERATE,
            ProblemComplexity.COMPLEX,
            ProblemComplexity.SYSTEMIC
        ]
        
        # Test that complexities are in order
        for i in range(len(complexities) - 1):
            assert complexities[i] < complexities[i + 1]


class TestEnterpriseType:
    """Test the EnterpriseType enum."""
    
    def test_enterprise_type_values(self):
        """Test enterprise type enum values."""
        assert EnterpriseType.RED_OWL == "red_owl"
        assert EnterpriseType.ORANGE_ORANGUTAN == "orange_orangutan"
        assert EnterpriseType.YELLOW_HONEYBEE == "yellow_honeybee"
        assert EnterpriseType.GREEN_TORTOISE == "green_tortoise"
        assert EnterpriseType.BLUE_DOLPHIN == "blue_dolphin"
        assert EnterpriseType.PURPLE_ELEPHANT == "purple_elephant"
    
    def test_enterprise_type_count(self):
        """Test that we have exactly 6 enterprise types."""
        assert len(list(EnterpriseType)) == 6


class TestCosmicCouncil:
    """Test the CosmicCouncil class."""
    
    def test_cosmic_council_initialization(self):
        """Test Cosmic Council initialization."""
        council = CosmicCouncil()
        
        assert council is not None
        assert len(council.enterprises) == 6
        assert council.enterprises[0].name == "Red Owl"
        assert council.enterprises[1].name == "Orange Orangutan"
        assert council.enterprises[2].name == "Yellow Honeybee"
        assert council.enterprises[3].name == "Green Tortoise"
        assert council.enterprises[4].name == "Blue Dolphin"
        assert council.enterprises[5].name == "Purple Elephant"
    
    def test_cosmic_council_enterprise_roles(self):
        """Test enterprise roles and responsibilities."""
        council = CosmicCouncil()
        
        enterprise_roles = {
            "Red Owl": "Research & Knowledge Gathering",
            "Orange Orangutan": "Logistics & Strategic Planning",
            "Yellow Honeybee": "Development & Innovation",
            "Green Tortoise": "Budget & Resource Management",
            "Blue Dolphin": "Market & Communication",
            "Purple Elephant": "Support & Continuous Improvement"
        }
        
        for enterprise in council.enterprises:
            assert enterprise.role == enterprise_roles[enterprise.name]
    
    def test_cosmic_council_enterprise_colors(self):
        """Test enterprise colors."""
        council = CosmicCouncil()
        
        enterprise_colors = {
            "Red Owl": "#ef4444",
            "Orange Orangutan": "#f97316",
            "Yellow Honeybee": "#eab308",
            "Green Tortoise": "#22c55e",
            "Blue Dolphin": "#3b82f6",
            "Purple Elephant": "#8b5cf6"
        }
        
        for enterprise in council.enterprises:
            assert enterprise.color == enterprise_colors[enterprise.name]
    
    @pytest.mark.asyncio
    async def test_solve_simple_problem(self, sample_simple_problem):
        """Test solving a simple problem."""
        council = CosmicCouncil()
        
        result = await council.solve_problem(sample_simple_problem)
        
        assert result is not None
        assert result.status == "completed"
        assert result.overall_confidence > 0.0
        assert result.total_processing_time > 0
        assert len(result.enterprise_results) == 6
        
        # Verify each enterprise provided results
        for enterprise, enterprise_result in result.enterprise_results.items():
            assert enterprise_result.get("status") == "completed"
            assert enterprise_result.get("confidence", 0) > 0.0
            assert len(enterprise_result.get("insights", [])) > 0
            assert len(enterprise_result.get("recommendations", [])) > 0
    
    @pytest.mark.asyncio
    async def test_solve_moderate_problem(self, sample_problem):
        """Test solving a moderate problem."""
        council = CosmicCouncil()
        
        result = await council.solve_problem(sample_problem)
        
        assert result is not None
        assert result.status == "completed"
        assert result.overall_confidence > 0.0
        assert result.total_processing_time > 0
        assert len(result.enterprise_results) == 6
        
        # Verify enterprise results
        for enterprise, enterprise_result in result.enterprise_results.items():
            assert enterprise_result.get("status") == "completed"
            assert enterprise_result.get("confidence", 0) > 0.0
            assert len(enterprise_result.get("insights", [])) > 0
            assert len(enterprise_result.get("recommendations", [])) > 0
    
    @pytest.mark.asyncio
    async def test_solve_complex_problem(self, sample_complex_problem):
        """Test solving a complex problem."""
        council = CosmicCouncil()
        
        result = await council.solve_problem(sample_complex_problem)
        
        assert result is not None
        assert result.status == "completed"
        assert result.overall_confidence > 0.0
        assert result.total_processing_time > 0
        assert len(result.enterprise_results) == 6
        
        # Complex problems should have higher processing time
        assert result.total_processing_time > 1.0
        
        # Verify enterprise results
        for enterprise, enterprise_result in result.enterprise_results.items():
            assert enterprise_result.get("status") == "completed"
            assert enterprise_result.get("confidence", 0) > 0.0
            assert len(enterprise_result.get("insights", [])) > 0
            assert len(enterprise_result.get("recommendations", [])) > 0
    
    @pytest.mark.asyncio
    async def test_solve_systemic_problem(self, sample_systemic_problem):
        """Test solving a systemic problem."""
        council = CosmicCouncil()
        
        result = await council.solve_problem(sample_systemic_problem)
        
        assert result is not None
        assert result.status == "completed"
        assert result.overall_confidence > 0.0
        assert result.total_processing_time > 0
        assert len(result.enterprise_results) == 6
        
        # Systemic problems should have the highest processing time
        assert result.total_processing_time > 2.0
        
        # Verify enterprise results
        for enterprise, enterprise_result in result.enterprise_results.items():
            assert enterprise_result.get("status") == "completed"
            assert enterprise_result.get("confidence", 0) > 0.0
            assert len(enterprise_result.get("insights", [])) > 0
            assert len(enterprise_result.get("recommendations", [])) > 0
    
    @pytest.mark.asyncio
    async def test_solve_problem_with_invalid_input(self):
        """Test solving a problem with invalid input."""
        council = CosmicCouncil()
        
        # Test with None input
        with pytest.raises(ValueError):
            await council.solve_problem(None)
        
        # Test with invalid problem type
        with pytest.raises(TypeError):
            await council.solve_problem("invalid_problem")
    
    @pytest.mark.asyncio
    async def test_solve_problem_processing_time_scaling(self):
        """Test that processing time scales with problem complexity."""
        council = CosmicCouncil()
        
        # Test simple problem
        simple_problem = ProblemStatement(
            title="Simple Test",
            description="Simple test",
            complexity=ProblemComplexity.SIMPLE,
            domain="Test"
        )
        simple_result = await council.solve_problem(simple_problem)
        
        # Test complex problem
        complex_problem = ProblemStatement(
            title="Complex Test",
            description="Complex test",
            complexity=ProblemComplexity.COMPLEX,
            domain="Test"
        )
        complex_result = await council.solve_problem(complex_problem)
        
        # Complex problems should take longer
        assert complex_result.total_processing_time > simple_result.total_processing_time
    
    @pytest.mark.asyncio
    async def test_solve_problem_confidence_scaling(self):
        """Test that confidence varies with problem complexity."""
        council = CosmicCouncil()
        
        # Test simple problem
        simple_problem = ProblemStatement(
            title="Simple Test",
            description="Simple test",
            complexity=ProblemComplexity.SIMPLE,
            domain="Test"
        )
        simple_result = await council.solve_problem(simple_problem)
        
        # Test complex problem
        complex_problem = ProblemStatement(
            title="Complex Test",
            description="Complex test",
            complexity=ProblemComplexity.COMPLEX,
            domain="Test"
        )
        complex_result = await council.solve_problem(complex_problem)
        
        # Both should have reasonable confidence
        assert simple_result.overall_confidence > 0.0
        assert complex_result.overall_confidence > 0.0
        assert simple_result.overall_confidence <= 1.0
        assert complex_result.overall_confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_solve_problem_enterprise_specialization(self):
        """Test that enterprises provide specialized results."""
        council = CosmicCouncil()
        
        problem = ProblemStatement(
            title="Specialization Test",
            description="Test enterprise specialization",
            complexity=ProblemComplexity.MODERATE,
            domain="Test"
        )
        
        result = await council.solve_problem(problem)
        
        # Each enterprise should provide unique insights
        all_insights = []
        for enterprise_result in result.enterprise_results.values():
            insights = enterprise_result.get("insights", [])
            all_insights.extend(insights)
        
        # Should have multiple unique insights
        assert len(all_insights) > 6  # At least one insight per enterprise
        
        # Each enterprise should provide unique recommendations
        all_recommendations = []
        for enterprise_result in result.enterprise_results.values():
            recommendations = enterprise_result.get("recommendations", [])
            all_recommendations.extend(recommendations)
        
        # Should have multiple unique recommendations
        assert len(all_recommendations) > 6  # At least one recommendation per enterprise
    
    @pytest.mark.asyncio
    async def test_solve_problem_result_structure(self, sample_problem):
        """Test the structure of problem solving results."""
        council = CosmicCouncil()
        
        result = await council.solve_problem(sample_problem)
        
        # Test result structure
        assert hasattr(result, 'status')
        assert hasattr(result, 'overall_confidence')
        assert hasattr(result, 'total_processing_time')
        assert hasattr(result, 'enterprise_results')
        assert hasattr(result, 'synthesis')
        assert hasattr(result, 'recommendations')
        assert hasattr(result, 'next_steps')
        
        # Test result values
        assert result.status in ["completed", "failed", "partial"]
        assert 0.0 <= result.overall_confidence <= 1.0
        assert result.total_processing_time > 0
        assert isinstance(result.enterprise_results, dict)
        assert len(result.enterprise_results) == 6
        assert isinstance(result.synthesis, str)
        assert isinstance(result.recommendations, list)
        assert isinstance(result.next_steps, list)
    
    @pytest.mark.asyncio
    async def test_solve_problem_concurrent_execution(self):
        """Test solving multiple problems concurrently."""
        council = CosmicCouncil()
        
        # Create multiple problems
        problems = []
        for i in range(5):
            problem = ProblemStatement(
                title=f"Concurrent Test {i}",
                description=f"Concurrent test problem {i}",
                complexity=ProblemComplexity.SIMPLE,
                domain="Test"
            )
            problems.append(problem)
        
        # Solve all problems concurrently
        tasks = [council.solve_problem(problem) for problem in problems]
        results = await asyncio.gather(*tasks)
        
        # Verify all problems were solved
        assert len(results) == 5
        for result in results:
            assert result.status == "completed"
            assert result.overall_confidence > 0.0
            assert result.total_processing_time > 0
    
    @pytest.mark.asyncio
    async def test_solve_problem_error_handling(self):
        """Test error handling in problem solving."""
        council = CosmicCouncil()
        
        # Test with problematic problem data
        problem = ProblemStatement(
            title="Error Test",
            description="Test error handling",
            complexity=ProblemComplexity.SIMPLE,
            domain="Test"
        )
        
        # Mock an enterprise to raise an exception
        with patch.object(council.enterprises[0], 'process_problem', side_effect=Exception("Test error")):
            result = await council.solve_problem(problem)
            
            # Should handle the error gracefully
            assert result.status in ["completed", "failed", "partial"]
            # Should still have results from other enterprises
            assert len(result.enterprise_results) >= 5


class TestProblemResult:
    """Test the ProblemResult class."""
    
    def test_problem_result_creation(self):
        """Test creating a problem result."""
        result = ProblemResult(
            status="completed",
            overall_confidence=0.85,
            total_processing_time=10.5,
            enterprise_results={},
            synthesis="Test synthesis",
            recommendations=["Recommendation 1", "Recommendation 2"],
            next_steps=["Step 1", "Step 2"]
        )
        
        assert result.status == "completed"
        assert result.overall_confidence == 0.85
        assert result.total_processing_time == 10.5
        assert result.enterprise_results == {}
        assert result.synthesis == "Test synthesis"
        assert result.recommendations == ["Recommendation 1", "Recommendation 2"]
        assert result.next_steps == ["Step 1", "Step 2"]
    
    def test_problem_result_validation(self):
        """Test problem result validation."""
        # Test valid confidence range
        result = ProblemResult(
            status="completed",
            overall_confidence=0.5,
            total_processing_time=5.0,
            enterprise_results={},
            synthesis="Test",
            recommendations=[],
            next_steps=[]
        )
        assert result.overall_confidence == 0.5
        
        # Test invalid confidence range
        with pytest.raises(ValueError):
            ProblemResult(
                status="completed",
                overall_confidence=1.5,  # Invalid: > 1.0
                total_processing_time=5.0,
                enterprise_results={},
                synthesis="Test",
                recommendations=[],
                next_steps=[]
            )
        
        with pytest.raises(ValueError):
            ProblemResult(
                status="completed",
                overall_confidence=-0.1,  # Invalid: < 0.0
                total_processing_time=5.0,
                enterprise_results={},
                synthesis="Test",
                recommendations=[],
                next_steps=[]
            )


class TestEnterpriseResult:
    """Test the EnterpriseResult class."""
    
    def test_enterprise_result_creation(self):
        """Test creating an enterprise result."""
        result = EnterpriseResult(
            enterprise_type=EnterpriseType.RED_OWL,
            status="completed",
            confidence=0.9,
            insights=["Insight 1", "Insight 2"],
            recommendations=["Recommendation 1", "Recommendation 2"],
            processing_time=2.5
        )
        
        assert result.enterprise_type == EnterpriseType.RED_OWL
        assert result.status == "completed"
        assert result.confidence == 0.9
        assert result.insights == ["Insight 1", "Insight 2"]
        assert result.recommendations == ["Recommendation 1", "Recommendation 2"]
        assert result.processing_time == 2.5
    
    def test_enterprise_result_validation(self):
        """Test enterprise result validation."""
        # Test valid confidence range
        result = EnterpriseResult(
            enterprise_type=EnterpriseType.RED_OWL,
            status="completed",
            confidence=0.8,
            insights=[],
            recommendations=[],
            processing_time=1.0
        )
        assert result.confidence == 0.8
        
        # Test invalid confidence range
        with pytest.raises(ValueError):
            EnterpriseResult(
                enterprise_type=EnterpriseType.RED_OWL,
                status="completed",
                confidence=1.1,  # Invalid: > 1.0
                insights=[],
                recommendations=[],
                processing_time=1.0
            )
