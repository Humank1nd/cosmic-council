"""
Unit tests for the Problem-Solving Workflow
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

from problem_solving_workflow import (
    ProblemSolvingWorkflow, WorkflowStep, WorkflowSession, 
    WorkflowStepData, WorkflowResult
)


class TestWorkflowStep:
    """Test the WorkflowStep enum."""
    
    def test_workflow_step_values(self):
        """Test workflow step enum values."""
        assert WorkflowStep.PROBLEM_DEFINITION == "problem_definition"
        assert WorkflowStep.STAKEHOLDER_ANALYSIS == "stakeholder_analysis"
        assert WorkflowStep.CONSTRAINT_ANALYSIS == "constraint_analysis"
        assert WorkflowStep.RED_OWL_RESEARCH == "red_owl_research"
        assert WorkflowStep.ORANGE_ORANGUTAN_PLANNING == "orange_orangutan_planning"
        assert WorkflowStep.YELLOW_HONEYBEE_DEVELOPMENT == "yellow_honeybee_development"
        assert WorkflowStep.GREEN_TORTOISE_RESOURCES == "green_tortoise_resources"
        assert WorkflowStep.BLUE_DOLPHIN_COMMUNICATION == "blue_dolphin_communication"
        assert WorkflowStep.PURPLE_ELEPHANT_SUPPORT == "purple_elephant_support"
        assert WorkflowStep.FINAL_SYNTHESIS == "final_synthesis"
    
    def test_workflow_step_count(self):
        """Test that we have exactly 10 workflow steps."""
        assert len(list(WorkflowStep)) == 10


class TestWorkflowStepData:
    """Test the WorkflowStepData class."""
    
    def test_workflow_step_data_creation(self):
        """Test creating workflow step data."""
        step_data = WorkflowStepData(
            step=WorkflowStep.PROBLEM_DEFINITION,
            inputs={"problem": "test problem"},
            outputs={"defined_problem": "test problem"},
            status="completed",
            confidence=0.9,
            processing_time=1.5,
            metadata={"test": "value"}
        )
        
        assert step_data.step == WorkflowStep.PROBLEM_DEFINITION
        assert step_data.inputs == {"problem": "test problem"}
        assert step_data.outputs == {"defined_problem": "test problem"}
        assert step_data.status == "completed"
        assert step_data.confidence == 0.9
        assert step_data.processing_time == 1.5
        assert step_data.metadata == {"test": "value"}
    
    def test_workflow_step_data_validation(self):
        """Test workflow step data validation."""
        # Test valid confidence range
        step_data = WorkflowStepData(
            step=WorkflowStep.PROBLEM_DEFINITION,
            inputs={},
            outputs={},
            status="completed",
            confidence=0.8,
            processing_time=1.0,
            metadata={}
        )
        assert step_data.confidence == 0.8
        
        # Test invalid confidence range
        with pytest.raises(ValueError):
            WorkflowStepData(
                step=WorkflowStep.PROBLEM_DEFINITION,
                inputs={},
                outputs={},
                status="completed",
                confidence=1.1,  # Invalid: > 1.0
                processing_time=1.0,
                metadata={}
            )


class TestWorkflowSession:
    """Test the WorkflowSession class."""
    
    def test_workflow_session_creation(self):
        """Test creating a workflow session."""
        session = WorkflowSession(
            session_id="test_session_1",
            problem_data={"title": "Test Problem"},
            start_time=datetime.now(timezone.utc),
            status="active"
        )
        
        assert session.session_id == "test_session_1"
        assert session.problem_data == {"title": "Test Problem"}
        assert session.status == "active"
        assert session.step_results == {}
        assert session.current_step is None
        assert session.progress == 0.0
    
    def test_workflow_session_step_management(self):
        """Test workflow session step management."""
        session = WorkflowSession(
            session_id="test_session_1",
            problem_data={"title": "Test Problem"},
            start_time=datetime.now(timezone.utc),
            status="active"
        )
        
        # Add step result
        step_data = WorkflowStepData(
            step=WorkflowStep.PROBLEM_DEFINITION,
            inputs={},
            outputs={},
            status="completed",
            confidence=0.9,
            processing_time=1.0,
            metadata={}
        )
        
        session.add_step_result(step_data)
        
        assert WorkflowStep.PROBLEM_DEFINITION.value in session.step_results
        assert session.progress == 0.1  # 1 out of 10 steps completed
    
    def test_workflow_session_progress_calculation(self):
        """Test workflow session progress calculation."""
        session = WorkflowSession(
            session_id="test_session_1",
            problem_data={"title": "Test Problem"},
            start_time=datetime.now(timezone.utc),
            status="active"
        )
        
        # Add multiple step results
        for i, step in enumerate(list(WorkflowStep)[:5]):
            step_data = WorkflowStepData(
                step=step,
                inputs={},
                outputs={},
                status="completed",
                confidence=0.9,
                processing_time=1.0,
                metadata={}
            )
            session.add_step_result(step_data)
        
        assert session.progress == 0.5  # 5 out of 10 steps completed


class TestWorkflowResult:
    """Test the WorkflowResult class."""
    
    def test_workflow_result_creation(self):
        """Test creating a workflow result."""
        result = WorkflowResult(
            session_id="test_session_1",
            status="completed",
            overall_confidence=0.85,
            total_processing_time=15.5,
            step_results={},
            enterprise_results={},
            synthesis="Test synthesis",
            recommendations=["Recommendation 1", "Recommendation 2"],
            next_steps=["Step 1", "Step 2"]
        )
        
        assert result.session_id == "test_session_1"
        assert result.status == "completed"
        assert result.overall_confidence == 0.85
        assert result.total_processing_time == 15.5
        assert result.step_results == {}
        assert result.enterprise_results == {}
        assert result.synthesis == "Test synthesis"
        assert result.recommendations == ["Recommendation 1", "Recommendation 2"]
        assert result.next_steps == ["Step 1", "Step 2"]


class TestProblemSolvingWorkflow:
    """Test the ProblemSolvingWorkflow class."""
    
    def test_workflow_initialization(self):
        """Test workflow initialization."""
        workflow = ProblemSolvingWorkflow()
        
        assert workflow is not None
        assert len(workflow.steps) == 10
        assert workflow.sessions == {}
        assert workflow.active_sessions == 0
    
    def test_workflow_steps_order(self):
        """Test that workflow steps are in the correct order."""
        workflow = ProblemSolvingWorkflow()
        
        expected_order = [
            WorkflowStep.PROBLEM_DEFINITION,
            WorkflowStep.STAKEHOLDER_ANALYSIS,
            WorkflowStep.CONSTRAINT_ANALYSIS,
            WorkflowStep.RED_OWL_RESEARCH,
            WorkflowStep.ORANGE_ORANGUTAN_PLANNING,
            WorkflowStep.YELLOW_HONEYBEE_DEVELOPMENT,
            WorkflowStep.GREEN_TORTOISE_RESOURCES,
            WorkflowStep.BLUE_DOLPHIN_COMMUNICATION,
            WorkflowStep.PURPLE_ELEPHANT_SUPPORT,
            WorkflowStep.FINAL_SYNTHESIS
        ]
        
        assert workflow.steps == expected_order
    
    @pytest.mark.asyncio
    async def test_start_session(self, sample_problem_data):
        """Test starting a workflow session."""
        workflow = ProblemSolvingWorkflow()
        
        session = await workflow.start_session(sample_problem_data)
        
        assert session is not None
        assert session.session_id is not None
        assert session.problem_data == sample_problem_data
        assert session.status == "active"
        assert session.start_time is not None
        assert session.progress == 0.0
        
        # Session should be stored in workflow
        assert session.session_id in workflow.sessions
        assert workflow.active_sessions == 1
    
    @pytest.mark.asyncio
    async def test_execute_step(self, sample_problem_data):
        """Test executing a single workflow step."""
        workflow = ProblemSolvingWorkflow()
        
        session = await workflow.start_session(sample_problem_data)
        step_result = await workflow.execute_step(session.session_id, WorkflowStep.PROBLEM_DEFINITION)
        
        assert step_result is not None
        assert step_result.step == WorkflowStep.PROBLEM_DEFINITION
        assert step_result.status == "completed"
        assert step_result.confidence > 0.0
        assert step_result.processing_time > 0
        
        # Step result should be added to session
        assert WorkflowStep.PROBLEM_DEFINITION.value in session.step_results
        assert session.progress > 0.0
    
    @pytest.mark.asyncio
    async def test_execute_complete_workflow(self, sample_problem_data):
        """Test executing a complete workflow."""
        workflow = ProblemSolvingWorkflow()
        
        session = await workflow.start_session(sample_problem_data)
        result = await workflow.execute_complete_workflow(session.session_id)
        
        assert result is not None
        assert result.status == "completed"
        assert result.overall_confidence > 0.0
        assert result.total_processing_time > 0
        assert len(result.step_results) == 10
        assert len(result.enterprise_results) == 6
        assert result.synthesis is not None
        assert len(result.recommendations) > 0
        assert len(result.next_steps) > 0
        
        # All steps should be completed
        for step in WorkflowStep:
            assert step.value in result.step_results
            step_result = result.step_results[step.value]
            assert step_result["status"] == "completed"
            assert step_result["confidence"] > 0.0
    
    @pytest.mark.asyncio
    async def test_workflow_step_dependencies(self, sample_problem_data):
        """Test that workflow steps respect dependencies."""
        workflow = ProblemSolvingWorkflow()
        
        session = await workflow.start_session(sample_problem_data)
        
        # Try to execute a step that depends on previous steps
        with pytest.raises(ValueError):
            await workflow.execute_step(session.session_id, WorkflowStep.FINAL_SYNTHESIS)
        
        # Execute steps in order
        await workflow.execute_step(session.session_id, WorkflowStep.PROBLEM_DEFINITION)
        await workflow.execute_step(session.session_id, WorkflowStep.STAKEHOLDER_ANALYSIS)
        await workflow.execute_step(session.session_id, WorkflowStep.CONSTRAINT_ANALYSIS)
        
        # Now should be able to execute enterprise steps
        await workflow.execute_step(session.session_id, WorkflowStep.RED_OWL_RESEARCH)
        await workflow.execute_step(session.session_id, WorkflowStep.ORANGE_ORANGUTAN_PLANNING)
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, sample_problem_data):
        """Test workflow error handling."""
        workflow = ProblemSolvingWorkflow()
        
        # Test with invalid session ID
        with pytest.raises(ValueError):
            await workflow.execute_step("invalid_session_id", WorkflowStep.PROBLEM_DEFINITION)
        
        # Test with invalid step
        session = await workflow.start_session(sample_problem_data)
        with pytest.raises(ValueError):
            await workflow.execute_step(session.session_id, "invalid_step")
    
    @pytest.mark.asyncio
    async def test_workflow_concurrent_sessions(self):
        """Test handling multiple concurrent workflow sessions."""
        workflow = ProblemSolvingWorkflow()
        
        # Create multiple sessions
        sessions = []
        for i in range(5):
            problem_data = {
                "title": f"Concurrent Test {i}",
                "description": f"Concurrent test problem {i}",
                "complexity": "simple",
                "domain": "Test"
            }
            session = await workflow.start_session(problem_data)
            sessions.append(session)
        
        assert workflow.active_sessions == 5
        
        # Execute steps concurrently
        tasks = []
        for session in sessions:
            task = workflow.execute_step(session.session_id, WorkflowStep.PROBLEM_DEFINITION)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Verify all steps were executed
        assert len(results) == 5
        for result in results:
            assert result.status == "completed"
            assert result.confidence > 0.0
    
    @pytest.mark.asyncio
    async def test_workflow_step_specialization(self, sample_problem_data):
        """Test that each workflow step provides specialized results."""
        workflow = ProblemSolvingWorkflow()
        
        session = await workflow.start_session(sample_problem_data)
        
        # Execute all steps
        for step in WorkflowStep:
            step_result = await workflow.execute_step(session.session_id, step)
            
            # Each step should provide unique outputs
            assert len(step_result.outputs) > 0
            
            # Step-specific validations
            if step == WorkflowStep.PROBLEM_DEFINITION:
                assert "defined_problem" in step_result.outputs
            elif step == WorkflowStep.STAKEHOLDER_ANALYSIS:
                assert "stakeholder_map" in step_result.outputs
            elif step == WorkflowStep.CONSTRAINT_ANALYSIS:
                assert "constraint_analysis" in step_result.outputs
            elif step == WorkflowStep.RED_OWL_RESEARCH:
                assert "research_findings" in step_result.outputs
            elif step == WorkflowStep.ORANGE_ORANGUTAN_PLANNING:
                assert "logistics_plan" in step_result.outputs
            elif step == WorkflowStep.YELLOW_HONEYBEE_DEVELOPMENT:
                assert "solution_prototypes" in step_result.outputs
            elif step == WorkflowStep.GREEN_TORTOISE_RESOURCES:
                assert "resource_allocation" in step_result.outputs
            elif step == WorkflowStep.BLUE_DOLPHIN_COMMUNICATION:
                assert "communication_strategy" in step_result.outputs
            elif step == WorkflowStep.PURPLE_ELEPHANT_SUPPORT:
                assert "support_plan" in step_result.outputs
            elif step == WorkflowStep.FINAL_SYNTHESIS:
                assert "final_synthesis" in step_result.outputs
    
    @pytest.mark.asyncio
    async def test_workflow_progress_tracking(self, sample_problem_data):
        """Test workflow progress tracking."""
        workflow = ProblemSolvingWorkflow()
        
        session = await workflow.start_session(sample_problem_data)
        
        # Execute steps and track progress
        for i, step in enumerate(WorkflowStep):
            await workflow.execute_step(session.session_id, step)
            expected_progress = (i + 1) / len(WorkflowStep)
            assert abs(session.progress - expected_progress) < 0.01
    
    @pytest.mark.asyncio
    async def test_workflow_session_cleanup(self, sample_problem_data):
        """Test workflow session cleanup."""
        workflow = ProblemSolvingWorkflow()
        
        session = await workflow.start_session(sample_problem_data)
        session_id = session.session_id
        
        # Complete the workflow
        await workflow.execute_complete_workflow(session_id)
        
        # Session should still exist but be completed
        assert session_id in workflow.sessions
        assert workflow.sessions[session_id].status == "completed"
        
        # Clean up session
        workflow.cleanup_session(session_id)
        
        # Session should be removed
        assert session_id not in workflow.sessions
        assert workflow.active_sessions == 0
    
    @pytest.mark.asyncio
    async def test_workflow_enterprise_integration(self, sample_problem_data):
        """Test workflow integration with enterprise agents."""
        workflow = ProblemSolvingWorkflow()
        
        session = await workflow.start_session(sample_problem_data)
        result = await workflow.execute_complete_workflow(session.session_id)
        
        # Verify enterprise results are included
        assert len(result.enterprise_results) == 6
        
        expected_enterprises = [
            "red_owl", "orange_orangutan", "yellow_honeybee",
            "green_tortoise", "blue_dolphin", "purple_elephant"
        ]
        
        for enterprise in expected_enterprises:
            assert enterprise in result.enterprise_results
            enterprise_result = result.enterprise_results[enterprise]
            assert enterprise_result["status"] == "completed"
            assert enterprise_result["confidence"] > 0.0
            assert len(enterprise_result["insights"]) > 0
            assert len(enterprise_result["recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_workflow_quality_assurance(self, sample_problem_data):
        """Test workflow quality assurance."""
        workflow = ProblemSolvingWorkflow()
        
        session = await workflow.start_session(sample_problem_data)
        result = await workflow.execute_complete_workflow(session.session_id)
        
        # Overall confidence should be reasonable
        assert 0.0 <= result.overall_confidence <= 1.0
        assert result.overall_confidence > 0.5  # Should be above minimum threshold
        
        # All steps should have reasonable confidence
        for step_result in result.step_results.values():
            assert 0.0 <= step_result["confidence"] <= 1.0
            assert step_result["confidence"] > 0.0
        
        # All enterprise results should have reasonable confidence
        for enterprise_result in result.enterprise_results.values():
            assert 0.0 <= enterprise_result["confidence"] <= 1.0
            assert enterprise_result["confidence"] > 0.0
    
    @pytest.mark.asyncio
    async def test_workflow_performance(self, sample_problem_data):
        """Test workflow performance."""
        workflow = ProblemSolvingWorkflow()
        
        session = await workflow.start_session(sample_problem_data)
        start_time = datetime.now(timezone.utc)
        
        result = await workflow.execute_complete_workflow(session.session_id)
        
        end_time = datetime.now(timezone.utc)
        total_time = (end_time - start_time).total_seconds()
        
        # Workflow should complete within reasonable time
        assert total_time < 60.0  # Should complete within 60 seconds
        assert result.total_processing_time > 0
        assert result.total_processing_time <= total_time
    
    @pytest.mark.asyncio
    async def test_workflow_resilience(self, sample_problem_data):
        """Test workflow resilience to failures."""
        workflow = ProblemSolvingWorkflow()
        
        session = await workflow.start_session(sample_problem_data)
        
        # Mock a step to fail
        with patch.object(workflow, '_execute_problem_definition', side_effect=Exception("Test error")):
            step_result = await workflow.execute_step(session.session_id, WorkflowStep.PROBLEM_DEFINITION)
            
            # Should handle error gracefully
            assert step_result.status in ["failed", "partial"]
            assert step_result.confidence >= 0.0  # Should not be negative
    
    @pytest.mark.asyncio
    async def test_workflow_data_persistence(self, sample_problem_data):
        """Test workflow data persistence."""
        workflow = ProblemSolvingWorkflow()
        
        session = await workflow.start_session(sample_problem_data)
        session_id = session.session_id
        
        # Execute a few steps
        await workflow.execute_step(session_id, WorkflowStep.PROBLEM_DEFINITION)
        await workflow.execute_step(session_id, WorkflowStep.STAKEHOLDER_ANALYSIS)
        
        # Get session again
        retrieved_session = workflow.get_session(session_id)
        
        # Should have the same data
        assert retrieved_session.session_id == session_id
        assert retrieved_session.progress > 0.0
        assert len(retrieved_session.step_results) == 2
        assert WorkflowStep.PROBLEM_DEFINITION.value in retrieved_session.step_results
        assert WorkflowStep.STAKEHOLDER_ANALYSIS.value in retrieved_session.step_results
