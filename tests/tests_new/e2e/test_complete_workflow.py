"""
End-to-end tests for complete workflow scenarios
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

from src.core.types import CosmicCouncil, ProblemStatement, ProblemComplexity
from problem_solving_workflow import ProblemSolvingWorkflow
from ai_enhanced_workflow import AIEnhancedProblemSolvingWorkflow, AIWorkflowConfig
from analytics_dashboard import AnalyticsDashboard
from enterprise_policy_engine import EnterprisePolicyEngine
from purple_elephant_feedback_system import PurpleElephantFeedbackSystem


class TestCompleteWorkflowE2E:
    """Test complete end-to-end workflow scenarios."""
    
    @pytest.mark.asyncio
    async def test_business_problem_solving_workflow(self):
        """Test complete business problem solving workflow."""
        # Initialize components
        council = CosmicCouncil()
        workflow = ProblemSolvingWorkflow()
        
        # Create a complex business problem
        problem = ProblemStatement(
            title="Optimize Customer Onboarding Process",
            description="Our current customer onboarding process takes too long and has a high dropout rate. We need to streamline the process while maintaining quality and ensuring customer satisfaction.",
            complexity=ProblemComplexity.COMPLEX,
            domain="Customer Experience",
            stakeholders=["New Customers", "Customer Success Team", "Product Team", "Sales Team", "Support Team"],
            constraints={"budget": "$50K", "timeline": "3 months", "team_size": "8 people"},
            success_criteria=[
                "Onboarding time reduced by 50%",
                "Dropout rate reduced to <15%",
                "Customer satisfaction score >85%",
                "Support ticket volume reduced by 30%"
            ]
        )
        
        # Solve using Cosmic Council
        council_result = await council.solve_problem(problem)
        
        assert council_result.status == "completed"
        assert council_result.overall_confidence > 0.0
        assert len(council_result.enterprise_results) == 6
        
        # Verify each enterprise provided results
        for enterprise, enterprise_result in council_result.enterprise_results.items():
            assert enterprise_result.get("status") == "completed"
            assert enterprise_result.get("confidence", 0) > 0.0
            assert len(enterprise_result.get("insights", [])) > 0
            assert len(enterprise_result.get("recommendations", [])) > 0
        
        # Solve using Workflow
        problem_data = {
            "title": problem.title,
            "description": problem.description,
            "complexity": problem.complexity.value,
            "domain": problem.domain,
            "stakeholders": problem.stakeholders,
            "constraints": problem.constraints,
            "success_criteria": problem.success_criteria
        }
        
        session = await workflow.start_session(problem_data)
        workflow_result = await workflow.execute_complete_workflow(session.session_id)
        
        assert workflow_result["status"] == "completed"
        assert workflow_result["overall_confidence"] > 0.0
        assert len(workflow_result["step_results"]) == 10
        assert len(workflow_result["enterprise_results"]) == 6
        
        # Compare results
        assert abs(council_result.overall_confidence - workflow_result["overall_confidence"]) < 0.1
        
        # Verify comprehensive solution
        assert len(workflow_result["recommendations"]) > 0
        assert len(workflow_result["next_steps"]) > 0
        assert workflow_result["synthesis"] is not None
    
    @pytest.mark.asyncio
    async def test_ai_enhanced_workflow(self):
        """Test AI-enhanced workflow execution."""
        ai_config = AIWorkflowConfig(
            enable_ai_enhancement=True,
            ai_confidence_threshold=0.8,
            max_ai_iterations=3
        )
        
        workflow = AIEnhancedProblemSolvingWorkflow(ai_config=ai_config)
        
        problem_data = {
            "title": "AI-Enhanced Digital Transformation",
            "description": "Implement AI-driven digital transformation for a traditional manufacturing company to improve efficiency, reduce costs, and enhance customer experience.",
            "complexity": "complex",
            "domain": "Digital Transformation",
            "stakeholders": ["Management", "IT Team", "Operations", "Customers", "Suppliers"],
            "constraints": {"budget": "$2M", "timeline": "18 months", "regulatory": "strict"},
            "success_criteria": [
                "30% efficiency improvement",
                "25% cost reduction",
                "40% customer satisfaction increase",
                "Zero regulatory violations"
            ]
        }
        
        session = await workflow.start_ai_enhanced_session(problem_data)
        result = await workflow.execute_ai_enhanced_workflow(session.session_id)
        
        assert result["status"] == "completed"
        assert result["ai_enhancement_used"] is True
        assert result["ai_confidence_improvement"] > 0.0
        assert result["overall_confidence"] > 0.0
        assert len(result["step_results"]) == 10
        assert len(result["enterprise_results"]) == 6
        
        # Verify AI enhancement
        assert result["ai_iterations_used"] > 0
        assert result["ai_confidence_improvement"] > 0.0
        assert result["ai_insights_generated"] > 0
    
    @pytest.mark.asyncio
    async def test_systemic_problem_workflow(self):
        """Test systemic problem solving workflow."""
        council = CosmicCouncil()
        
        # Create a systemic problem
        problem = ProblemStatement(
            title="Climate Change Mitigation Strategy",
            description="Develop a comprehensive strategy to mitigate climate change impacts across multiple sectors including energy, transportation, agriculture, and manufacturing.",
            complexity=ProblemComplexity.SYSTEMIC,
            domain="Environmental",
            stakeholders=[
                "Government", "Energy Companies", "Transportation Companies",
                "Agricultural Sector", "Manufacturing Sector", "Environmental Groups",
                "Citizens", "International Organizations"
            ],
            constraints={
                "budget": "$10B", "timeline": "10 years", "regulatory": "complex",
                "international": "required", "political": "sensitive"
            },
            success_criteria=[
                "50% reduction in carbon emissions",
                "100% renewable energy by 2030",
                "Zero net deforestation",
                "International cooperation achieved",
                "Economic growth maintained"
            ]
        )
        
        result = await council.solve_problem(problem)
        
        assert result.status == "completed"
        assert result.overall_confidence > 0.0
        assert result.total_processing_time > 0
        assert len(result.enterprise_results) == 6
        
        # Systemic problems should have comprehensive results
        assert len(result.synthesis) > 100  # Should be comprehensive
        assert len(result.recommendations) > 10  # Should have many recommendations
        assert len(result.next_steps) > 5  # Should have many next steps
        
        # Verify enterprise specialization
        red_owl_result = result.enterprise_results.get("red_owl", {})
        assert len(red_owl_result.get("insights", [])) > 0
        assert any("research" in insight.lower() or "data" in insight.lower() 
                  for insight in red_owl_result.get("insights", []))
        
        orange_orangutan_result = result.enterprise_results.get("orange_orangutan", {})
        assert len(orange_orangutan_result.get("insights", [])) > 0
        assert any("logistics" in insight.lower() or "planning" in insight.lower() 
                  for insight in orange_orangutan_result.get("insights", []))
    
    @pytest.mark.asyncio
    async def test_policy_engine_integration(self):
        """Test policy engine integration with workflow."""
        policy_engine = EnterprisePolicyEngine()
        workflow = ProblemSolvingWorkflow()
        
        # Create a problem that requires policy evaluation
        problem_data = {
            "title": "AI Ethics Implementation",
            "description": "Implement AI ethics framework for autonomous systems in healthcare",
            "complexity": "complex",
            "domain": "AI Ethics",
            "stakeholders": ["Healthcare Providers", "Patients", "AI Developers", "Regulators"],
            "constraints": {"budget": "$5M", "timeline": "2 years", "regulatory": "strict"},
            "success_criteria": [
                "100% compliance with AI ethics standards",
                "Zero bias incidents",
                "95% stakeholder approval",
                "Regulatory approval achieved"
            ]
        }
        
        # Start workflow
        session = await workflow.start_session(problem_data)
        
        # Execute workflow with policy evaluation
        result = await workflow.execute_complete_workflow(session.session_id)
        
        assert result["status"] == "completed"
        assert result["overall_confidence"] > 0.0
        
        # Verify policy compliance
        assert "policy_evaluation" in result
        assert result["policy_evaluation"]["compliance_score"] > 0.8
        assert len(result["policy_evaluation"]["violations"]) == 0
        assert len(result["policy_evaluation"]["recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_feedback_system_integration(self):
        """Test feedback system integration with workflow."""
        feedback_system = PurpleElephantFeedbackSystem()
        workflow = ProblemSolvingWorkflow()
        
        # Create a problem
        problem_data = {
            "title": "Process Improvement Initiative",
            "description": "Improve internal processes for better efficiency and employee satisfaction",
            "complexity": "moderate",
            "domain": "Process Improvement",
            "stakeholders": ["Employees", "Management", "HR", "IT"],
            "constraints": {"budget": "$100K", "timeline": "6 months"},
            "success_criteria": [
                "20% efficiency improvement",
                "90% employee satisfaction",
                "50% reduction in process time"
            ]
        }
        
        # Start workflow
        session = await workflow.start_session(problem_data)
        result = await workflow.execute_complete_workflow(session.session_id)
        
        assert result["status"] == "completed"
        
        # Generate feedback
        feedback_cycle = await feedback_system.generate_feedback_cycle(
            cycle_id=session.session_id,
            feedback_type="system_reflection",
            scope="enterprise_level"
        )
        
        assert feedback_cycle is not None
        assert feedback_cycle["status"] == "completed"
        assert len(feedback_cycle["insights"]) > 0
        assert len(feedback_cycle["recommendations"]) > 0
        assert feedback_cycle["improvement_score"] > 0.0
    
    @pytest.mark.asyncio
    async def test_analytics_dashboard_integration(self):
        """Test analytics dashboard integration with workflow."""
        dashboard = AnalyticsDashboard()
        workflow = ProblemSolvingWorkflow()
        
        # Create and solve multiple problems
        problems = []
        for i in range(5):
            problem_data = {
                "title": f"Analytics Test Problem {i}",
                "description": f"A problem for analytics testing {i}",
                "complexity": "moderate",
                "domain": "Analytics Testing",
                "stakeholders": ["Test Stakeholder"],
                "constraints": {"budget": "$10K"},
                "success_criteria": ["Test criteria"]
            }
            
            session = await workflow.start_session(problem_data)
            result = await workflow.execute_complete_workflow(session.session_id)
            problems.append(result)
        
        # Get analytics
        analytics = await dashboard.get_system_analytics()
        
        assert analytics is not None
        assert analytics["total_problems"] >= 5
        assert analytics["total_cycles"] >= 5
        assert analytics["success_rate"] > 0.0
        assert analytics["average_confidence"] > 0.0
        
        # Get enterprise performance
        enterprise_performance = await dashboard.get_enterprise_performance()
        
        assert enterprise_performance is not None
        assert len(enterprise_performance) == 6
        
        for enterprise, performance in enterprise_performance.items():
            assert performance["cycles_processed"] >= 0
            assert performance["success_rate"] >= 0.0
            assert performance["average_confidence"] >= 0.0
    
    @pytest.mark.asyncio
    async def test_concurrent_problem_solving(self):
        """Test concurrent problem solving scenarios."""
        council = CosmicCouncil()
        
        # Create multiple problems
        problems = []
        for i in range(10):
            problem = ProblemStatement(
                title=f"Concurrent Test Problem {i}",
                description=f"A problem for concurrent testing {i}",
                complexity=ProblemComplexity.MODERATE,
                domain="Concurrent Testing",
                stakeholders=["Test Stakeholder"],
                constraints={"budget": "$5K"},
                success_criteria=["Test criteria"]
            )
            problems.append(problem)
        
        # Solve all problems concurrently
        start_time = datetime.now(timezone.utc)
        tasks = [council.solve_problem(problem) for problem in problems]
        results = await asyncio.gather(*tasks)
        end_time = datetime.now(timezone.utc)
        
        total_time = (end_time - start_time).total_seconds()
        
        # Verify all problems were solved
        assert len(results) == 10
        for result in results:
            assert result.status == "completed"
            assert result.overall_confidence > 0.0
            assert result.total_processing_time > 0
        
        # Concurrent execution should be faster than sequential
        assert total_time < 60.0  # Should complete within 60 seconds
        
        # Calculate total processing time
        total_processing_time = sum(result.total_processing_time for result in results)
        assert total_time < total_processing_time  # Concurrent should be faster
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self):
        """Test error recovery in workflow execution."""
        workflow = ProblemSolvingWorkflow()
        
        problem_data = {
            "title": "Error Recovery Test Problem",
            "description": "A problem for testing error recovery",
            "complexity": "moderate",
            "domain": "Error Testing",
            "stakeholders": ["Test Stakeholder"],
            "constraints": {"budget": "$5K"},
            "success_criteria": ["Test criteria"]
        }
        
        session = await workflow.start_session(problem_data)
        
        # Mock a step to fail
        with patch.object(workflow, '_execute_problem_definition', side_effect=Exception("Test error")):
            result = await workflow.execute_complete_workflow(session.session_id)
            
            # Should handle error gracefully
            assert result["status"] in ["completed", "partial", "failed"]
            
            # Should still have results from other steps
            assert len(result["step_results"]) > 0
            
            # Failed step should be marked as failed
            if "problem_definition" in result["step_results"]:
                assert result["step_results"]["problem_definition"]["status"] in ["failed", "partial"]
    
    @pytest.mark.asyncio
    async def test_workflow_persistence(self):
        """Test workflow session persistence."""
        workflow = ProblemSolvingWorkflow()
        
        problem_data = {
            "title": "Persistence Test Problem",
            "description": "A problem for testing persistence",
            "complexity": "moderate",
            "domain": "Persistence Testing",
            "stakeholders": ["Test Stakeholder"],
            "constraints": {"budget": "$5K"},
            "success_criteria": ["Test criteria"]
        }
        
        # Start workflow
        session = await workflow.start_session(problem_data)
        session_id = session.session_id
        
        # Execute a few steps
        await workflow.execute_step(session_id, "problem_definition")
        await workflow.execute_step(session_id, "stakeholder_analysis")
        
        # Get session again
        retrieved_session = workflow.get_session(session_id)
        
        # Should have the same data
        assert retrieved_session.session_id == session_id
        assert retrieved_session.progress > 0.0
        assert len(retrieved_session.step_results) == 2
        
        # Continue workflow
        result = await workflow.execute_complete_workflow(session_id)
        
        assert result["status"] == "completed"
        assert len(result["step_results"]) == 10
    
    @pytest.mark.asyncio
    async def test_workflow_quality_assurance(self):
        """Test workflow quality assurance."""
        workflow = ProblemSolvingWorkflow()
        
        problem_data = {
            "title": "Quality Assurance Test Problem",
            "description": "A problem for testing quality assurance",
            "complexity": "complex",
            "domain": "Quality Testing",
            "stakeholders": ["Test Stakeholder 1", "Test Stakeholder 2"],
            "constraints": {"budget": "$10K", "timeline": "2 months"},
            "success_criteria": ["Quality criteria 1", "Quality criteria 2"]
        }
        
        session = await workflow.start_session(problem_data)
        result = await workflow.execute_complete_workflow(session.session_id)
        
        # Quality checks
        assert result["status"] == "completed"
        assert result["overall_confidence"] > 0.5  # Should be above minimum threshold
        assert result["total_processing_time"] > 0
        
        # All steps should have reasonable confidence
        for step_result in result["step_results"].values():
            assert 0.0 <= step_result["confidence"] <= 1.0
            assert step_result["confidence"] > 0.0
        
        # All enterprise results should have reasonable confidence
        for enterprise_result in result["enterprise_results"].values():
            assert 0.0 <= enterprise_result["confidence"] <= 1.0
            assert enterprise_result["confidence"] > 0.0
        
        # Should have comprehensive results
        assert len(result["synthesis"]) > 50  # Should be comprehensive
        assert len(result["recommendations"]) > 0
        assert len(result["next_steps"]) > 0
    
    @pytest.mark.asyncio
    async def test_workflow_performance_benchmark(self):
        """Test workflow performance benchmarking."""
        workflow = ProblemSolvingWorkflow()
        
        # Test different problem complexities
        complexities = ["simple", "moderate", "complex", "systemic"]
        results = {}
        
        for complexity in complexities:
            problem_data = {
                "title": f"Performance Test {complexity.title()}",
                "description": f"A {complexity} problem for performance testing",
                "complexity": complexity,
                "domain": "Performance Testing",
                "stakeholders": ["Test Stakeholder"],
                "constraints": {"budget": "$5K"},
                "success_criteria": ["Test criteria"]
            }
            
            session = await workflow.start_session(problem_data)
            start_time = datetime.now(timezone.utc)
            
            result = await workflow.execute_complete_workflow(session.session_id)
            
            end_time = datetime.now(timezone.utc)
            total_time = (end_time - start_time).total_seconds()
            
            results[complexity] = {
                "total_time": total_time,
                "processing_time": result["total_processing_time"],
                "confidence": result["overall_confidence"],
                "status": result["status"]
            }
        
        # Verify performance scaling
        assert results["simple"]["total_time"] < results["moderate"]["total_time"]
        assert results["moderate"]["total_time"] < results["complex"]["total_time"]
        assert results["complex"]["total_time"] < results["systemic"]["total_time"]
        
        # All should complete successfully
        for complexity, result in results.items():
            assert result["status"] == "completed"
            assert result["confidence"] > 0.0
            assert result["total_time"] < 60.0  # Should complete within 60 seconds
    
    @pytest.mark.asyncio
    async def test_workflow_integration_test(self):
        """Test complete workflow integration."""
        # Initialize all components
        council = CosmicCouncil()
        workflow = ProblemSolvingWorkflow()
        ai_config = AIWorkflowConfig(enable_ai_enhancement=True)
        ai_workflow = AIEnhancedProblemSolvingWorkflow(ai_config=ai_config)
        policy_engine = EnterprisePolicyEngine()
        feedback_system = PurpleElephantFeedbackSystem()
        dashboard = AnalyticsDashboard()
        
        # Create a comprehensive problem
        problem_data = {
            "title": "Comprehensive Integration Test",
            "description": "A comprehensive problem for testing all system components working together",
            "complexity": "complex",
            "domain": "Integration Testing",
            "stakeholders": ["Stakeholder 1", "Stakeholder 2", "Stakeholder 3"],
            "constraints": {"budget": "$50K", "timeline": "6 months", "regulatory": "moderate"},
            "success_criteria": [
                "Integration criteria 1",
                "Integration criteria 2",
                "Integration criteria 3"
            ]
        }
        
        # Test 1: Basic workflow
        session1 = await workflow.start_session(problem_data)
        result1 = await workflow.execute_complete_workflow(session1.session_id)
        
        assert result1["status"] == "completed"
        assert result1["overall_confidence"] > 0.0
        
        # Test 2: AI-enhanced workflow
        session2 = await ai_workflow.start_ai_enhanced_session(problem_data)
        result2 = await ai_workflow.execute_ai_enhanced_workflow(session2.session_id)
        
        assert result2["status"] == "completed"
        assert result2["ai_enhancement_used"] is True
        
        # Test 3: Policy evaluation
        policy_result = await policy_engine.evaluate_policies(problem_data)
        assert policy_result["compliance_score"] > 0.0
        
        # Test 4: Feedback generation
        feedback_result = await feedback_system.generate_feedback_cycle(
            cycle_id=session1.session_id,
            feedback_type="system_reflection",
            scope="enterprise_level"
        )
        assert feedback_result["status"] == "completed"
        
        # Test 5: Analytics
        analytics = await dashboard.get_system_analytics()
        assert analytics["total_problems"] >= 2
        
        # Verify integration
        assert result1["overall_confidence"] > 0.0
        assert result2["overall_confidence"] > 0.0
        assert policy_result["compliance_score"] > 0.0
        assert feedback_result["improvement_score"] > 0.0
        assert analytics["success_rate"] > 0.0
