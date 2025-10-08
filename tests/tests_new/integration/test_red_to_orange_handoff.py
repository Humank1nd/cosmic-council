#!/usr/bin/env python3
"""
🔄 Red to Orange Handoff Integration Tests
Test the integration between Red Research and Orange Logistics enterprises
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import uuid
from datetime import datetime

# Import the services to test
from red_research.tools.research_service import RedResearchService
from orange_logistics.tools.planning_service import OrangeLogisticsService


class TestRedToOrangeHandoff:
    """Test the handoff process from Red Research to Orange Logistics"""
    
    @pytest.fixture
    def red_service(self):
        """Create Red Research service instance"""
        return RedResearchService()
    
    @pytest.fixture
    def orange_service(self):
        """Create Orange Logistics service instance"""
        return OrangeLogisticsService()
    
    @pytest.fixture
    def sample_cycle_data(self):
        """Create sample cycle data for testing"""
        return {
            "cycle_id": str(uuid.uuid4()),
            "objective_ref": "integration_test_001",
            "problem_title": "Test Integration Problem",
            "problem_description": "Testing the handoff between Red and Orange enterprises"
        }
    
    @pytest.mark.asyncio
    async def test_complete_red_to_orange_workflow(self, red_service, orange_service, sample_cycle_data):
        """Test the complete workflow from Red Research to Orange Logistics"""
        
        with patch('shared.utils.database.get_database_manager') as mock_db:
            # Mock database responses for Red Research
            mock_db.return_value.execute_query = AsyncMock(side_effect=[
                # Red Research: Create core problem
                [{"id": str(uuid.uuid4())}],
                # Red Research: Create research findings
                [{"id": str(uuid.uuid4())}],
                # Red Research: Prioritize questions
                [
                    {"id": str(uuid.uuid4()), "question": "What is the root cause?", "priority": 9},
                    {"id": str(uuid.uuid4()), "question": "Who are the stakeholders?", "priority": 8},
                    {"id": str(uuid.uuid4()), "question": "What are the constraints?", "priority": 7}
                ],
                # Orange Logistics: Create action plans
                [{"id": str(uuid.uuid4())} for _ in range(3)],
                # Orange Logistics: Create dependencies
                [{"id": str(uuid.uuid4())} for _ in range(2)]
            ])
            
            mock_db.return_value.execute_command = AsyncMock(return_value="UPDATE 1")
            
            # Step 1: Red Research completes its work
            red_result = await red_service.process_research_workflow(
                title=sample_cycle_data["problem_title"],
                description=sample_cycle_data["problem_description"],
                objective_ref=sample_cycle_data["objective_ref"]
            )
            
            assert red_result is not None
            assert "problem_id" in red_result
            assert "questions" in red_result
            assert len(red_result["questions"]) == 3
            
            # Step 2: Orange Logistics receives the handoff
            orange_result = await orange_service.process_planning_workflow(
                questions=red_result["questions"],
                cycle_id=sample_cycle_data["cycle_id"]
            )
            
            assert orange_result is not None
            assert "action_plans" in orange_result
            assert "dependencies" in orange_result
            assert len(orange_result["action_plans"]) == 3
    
    @pytest.mark.asyncio
    async def test_question_priority_filtering(self, red_service, orange_service):
        """Test that only high-priority questions are passed to Orange"""
        
        with patch('shared.utils.database.get_database_manager') as mock_db:
            # Mock questions with varying priorities
            mock_questions = [
                {"id": str(uuid.uuid4()), "question": "High priority question", "priority": 9},
                {"id": str(uuid.uuid4()), "question": "Medium priority question", "priority": 6},
                {"id": str(uuid.uuid4()), "question": "Low priority question", "priority": 3}
            ]
            
            mock_db.return_value.execute_query = AsyncMock(return_value=mock_questions)
            
            # Get prioritized questions for handoff
            handoff_questions = await red_service.get_prioritized_questions_for_handoff()
            
            # Only high priority questions (>= 7) should be included
            assert len(handoff_questions) == 1
            assert handoff_questions[0]["priority"] >= 7
    
    @pytest.mark.asyncio
    async def test_data_integrity_across_handoff(self, red_service, orange_service, sample_cycle_data):
        """Test that data integrity is maintained across the handoff"""
        
        with patch('shared.utils.database.get_database_manager') as mock_db:
            # Mock database responses
            problem_id = str(uuid.uuid4())
            finding_id = str(uuid.uuid4())
            question_ids = [str(uuid.uuid4()) for _ in range(3)]
            
            mock_db.return_value.execute_query = AsyncMock(side_effect=[
                # Red Research responses
                [{"id": problem_id}],
                [{"id": finding_id}],
                [{"id": qid, "question": f"Question {i}", "priority": 8} for i, qid in enumerate(question_ids)],
                # Orange Logistics responses
                [{"id": str(uuid.uuid4())} for _ in range(3)]
            ])
            
            mock_db.return_value.execute_command = AsyncMock(return_value="UPDATE 1")
            
            # Execute Red Research workflow
            red_result = await red_service.process_research_workflow(
                title=sample_cycle_data["problem_title"],
                description=sample_cycle_data["problem_description"],
                objective_ref=sample_cycle_data["objective_ref"]
            )
            
            # Execute Orange Logistics workflow
            orange_result = await orange_service.process_planning_workflow(
                questions=red_result["questions"],
                cycle_id=sample_cycle_data["cycle_id"]
            )
            
            # Verify data integrity
            assert red_result["problem_id"] == problem_id
            assert len(red_result["questions"]) == 3
            assert all(q["id"] in question_ids for q in red_result["questions"])
            assert orange_result["action_plans"] is not None
            assert len(orange_result["action_plans"]) == 3
    
    @pytest.mark.asyncio
    async def test_error_handling_in_handoff(self, red_service, orange_service):
        """Test error handling during the handoff process"""
        
        with patch('shared.utils.database.get_database_manager') as mock_db:
            # Mock database error
            mock_db.return_value.execute_query = AsyncMock(side_effect=Exception("Database connection failed"))
            
            # Test that errors are properly handled
            with pytest.raises(Exception, match="Database connection failed"):
                await red_service.process_research_workflow(
                    title="Test Problem",
                    description="Test Description",
                    objective_ref="test_ref"
                )
    
    @pytest.mark.asyncio
    async def test_cycle_status_updates(self, red_service, orange_service, sample_cycle_data):
        """Test that cycle status is properly updated during handoff"""
        
        with patch('shared.utils.database.get_database_manager') as mock_db:
            # Mock successful database operations
            mock_db.return_value.execute_query = AsyncMock(side_effect=[
                [{"id": str(uuid.uuid4())}],  # Red: Create problem
                [{"id": str(uuid.uuid4())}],  # Red: Create finding
                [{"id": str(uuid.uuid4()), "question": "Test question", "priority": 8}],  # Red: Questions
                [{"id": str(uuid.uuid4())}]   # Orange: Create action plan
            ])
            
            mock_db.return_value.execute_command = AsyncMock(return_value="UPDATE 1")
            
            # Execute Red Research workflow
            red_result = await red_service.process_research_workflow(
                title=sample_cycle_data["problem_title"],
                description=sample_cycle_data["problem_description"],
                objective_ref=sample_cycle_data["objective_ref"]
            )
            
            # Verify Red stage completion
            assert red_result["status"] == "completed"
            
            # Execute Orange Logistics workflow
            orange_result = await orange_service.process_planning_workflow(
                questions=red_result["questions"],
                cycle_id=sample_cycle_data["cycle_id"]
            )
            
            # Verify Orange stage completion
            assert orange_result["status"] == "completed"


class TestHandoffDataValidation:
    """Test data validation during handoff process"""
    
    @pytest.mark.asyncio
    async def test_question_data_validation(self):
        """Test that question data is properly validated"""
        red_service = RedResearchService()
        
        # Test with invalid question data
        invalid_questions = [
            {"id": "invalid-uuid", "question": "", "priority": 15},  # Invalid UUID, empty question, invalid priority
            {"id": str(uuid.uuid4()), "question": "Valid question", "priority": -1}  # Invalid priority
        ]
        
        with patch('shared.utils.database.get_database_manager') as mock_db:
            mock_db.return_value.execute_query = AsyncMock(return_value=invalid_questions)
            
            # Should filter out invalid questions
            valid_questions = await red_service.validate_questions_for_handoff(invalid_questions)
            
            # Only valid questions should remain
            assert len(valid_questions) == 0  # All questions were invalid
    
    @pytest.mark.asyncio
    async def test_cycle_id_validation(self):
        """Test that cycle IDs are properly validated"""
        orange_service = OrangeLogisticsService()
        
        # Test with invalid cycle ID
        invalid_cycle_id = "not-a-uuid"
        
        with pytest.raises(ValueError, match="Invalid cycle ID format"):
            await orange_service.process_planning_workflow(
                questions=[],
                cycle_id=invalid_cycle_id
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
