#!/usr/bin/env python3
"""
🔴 Red Research Unit Tests
Test the research and inquiry enterprise functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import uuid

# Import the modules to test
from red_research.tools.research_service import RedResearchService
from red_research.db.schema import CoreProblem, ResearchFinding, PrioritizedQuestion


class TestRedResearchService:
    """Test Red Research Service functionality"""
    
    @pytest.fixture
    def research_service(self):
        """Create a research service instance for testing"""
        return RedResearchService()
    
    @pytest.fixture
    def sample_problem(self):
        """Create a sample problem for testing"""
        return {
            "title": "Test Problem",
            "description": "A test problem for unit testing",
            "objective_ref": "test_objective_001"
        }
    
    @pytest.mark.asyncio
    async def test_create_core_problem(self, research_service, sample_problem):
        """Test creating a core problem"""
        with patch('red_research.tools.research_service.get_database_manager') as mock_db:
            mock_db.return_value.execute_query = AsyncMock(return_value=[{"id": str(uuid.uuid4())}])
            
            result = await research_service.create_core_problem(
                title=sample_problem["title"],
                description=sample_problem["description"],
                objective_ref=sample_problem["objective_ref"]
            )
            
            assert result is not None
            assert "id" in result
    
    @pytest.mark.asyncio
    async def test_research_findings_creation(self, research_service):
        """Test creating research findings"""
        problem_id = str(uuid.uuid4())
        finding_data = {
            "summary": "Test finding summary",
            "evidence": {"source": "test_source", "confidence": 0.8},
            "confidence": 0.8
        }
        
        with patch('red_research.tools.research_service.get_database_manager') as mock_db:
            mock_db.return_value.execute_query = AsyncMock(return_value=[{"id": str(uuid.uuid4())}])
            
            result = await research_service.create_research_finding(
                problem_id=problem_id,
                **finding_data
            )
            
            assert result is not None
            assert "id" in result
    
    @pytest.mark.asyncio
    async def test_prioritize_questions(self, research_service):
        """Test prioritizing questions from findings"""
        finding_id = str(uuid.uuid4())
        questions = [
            "What is the root cause?",
            "Who are the stakeholders?",
            "What are the constraints?"
        ]
        
        with patch('red_research.tools.research_service.get_database_manager') as mock_db:
            mock_db.return_value.execute_query = AsyncMock(return_value=[{"id": str(uuid.uuid4())} for _ in questions])
            
            result = await research_service.prioritize_questions(
                finding_id=finding_id,
                questions=questions
            )
            
            assert len(result) == len(questions)
            assert all("id" in question for question in result)
    
    @pytest.mark.asyncio
    async def test_research_workflow(self, research_service, sample_problem):
        """Test the complete research workflow"""
        with patch('red_research.tools.research_service.get_database_manager') as mock_db:
            # Mock database responses
            mock_db.return_value.execute_query = AsyncMock(side_effect=[
                [{"id": str(uuid.uuid4())}],  # Core problem creation
                [{"id": str(uuid.uuid4())}],  # Research finding creation
                [{"id": str(uuid.uuid4())} for _ in range(3)]  # Question prioritization
            ])
            
            # Execute the workflow
            result = await research_service.process_research_workflow(
                title=sample_problem["title"],
                description=sample_problem["description"],
                objective_ref=sample_problem["objective_ref"]
            )
            
            assert result is not None
            assert "problem_id" in result
            assert "findings" in result
            assert "questions" in result
            assert len(result["questions"]) == 3


class TestRedResearchSchema:
    """Test Red Research database schema and models"""
    
    def test_core_problem_creation(self):
        """Test CoreProblem model creation"""
        problem = CoreProblem(
            title="Test Problem",
            description="Test Description",
            status="draft"
        )
        
        assert problem.title == "Test Problem"
        assert problem.description == "Test Description"
        assert problem.status == "draft"
        assert problem.id is not None
    
    def test_research_finding_creation(self):
        """Test ResearchFinding model creation"""
        finding = ResearchFinding(
            problem_id=str(uuid.uuid4()),
            summary="Test finding",
            evidence={"source": "test"},
            confidence=0.8
        )
        
        assert finding.summary == "Test finding"
        assert finding.confidence == 0.8
        assert finding.evidence["source"] == "test"
    
    def test_prioritized_question_creation(self):
        """Test PrioritizedQuestion model creation"""
        question = PrioritizedQuestion(
            finding_id=str(uuid.uuid4()),
            question="Test question?",
            priority=5
        )
        
        assert question.question == "Test question?"
        assert question.priority == 5


class TestRedResearchIntegration:
    """Test Red Research integration with other components"""
    
    @pytest.mark.asyncio
    async def test_handoff_to_orange(self):
        """Test handoff to Orange Logistics"""
        research_service = RedResearchService()
        
        with patch('red_research.tools.research_service.get_database_manager') as mock_db:
            mock_db.return_value.execute_query = AsyncMock(return_value=[
                {"id": str(uuid.uuid4()), "question": "Test question", "priority": 8}
            ])
            
            # Get prioritized questions for handoff
            questions = await research_service.get_prioritized_questions_for_handoff()
            
            assert len(questions) > 0
            assert all(q["priority"] >= 7 for q in questions)  # High priority questions
    
    @pytest.mark.asyncio
    async def test_cycle_completion(self):
        """Test cycle completion and status update"""
        research_service = RedResearchService()
        cycle_id = str(uuid.uuid4())
        
        with patch('red_research.tools.research_service.get_database_manager') as mock_db:
            mock_db.return_value.execute_command = AsyncMock(return_value="UPDATE 1")
            
            result = await research_service.complete_cycle(cycle_id)
            
            assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
