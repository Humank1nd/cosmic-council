"""
Performance tests for load testing
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import List, Dict, Any

from src.core.types import CosmicCouncil, ProblemStatement, ProblemComplexity
from problem_solving_workflow import ProblemSolvingWorkflow
from ai_enhanced_workflow import AIEnhancedProblemSolvingWorkflow, AIWorkflowConfig


class TestLoadPerformance:
    """Test system performance under load."""
    
    @pytest.mark.asyncio
    async def test_concurrent_problem_solving(self):
        """Test concurrent problem solving performance."""
        council = CosmicCouncil()
        
        # Create multiple problems
        problems = []
        for i in range(20):
            problem = ProblemStatement(
                title=f"Load Test Problem {i}",
                description=f"Problem {i} for load testing",
                complexity=ProblemComplexity.MODERATE,
                domain="Load Testing",
                stakeholders=["Test Stakeholder"],
                constraints={"budget": "$5K"},
                success_criteria=["Test criteria"]
            )
            problems.append(problem)
        
        # Solve problems concurrently
        start_time = time.time()
        
        tasks = [council.solve_problem(problem) for problem in problems]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all problems were solved
        for result in results:
            assert result.status == "completed"
            assert result.overall_confidence > 0.0
        
        # Performance assertions
        assert total_time < 120  # Should complete within 2 minutes
        assert len(results) == 20  # All problems solved
        
        print(f"Solved {len(problems)} problems in {total_time:.2f} seconds")
        print(f"Average time per problem: {total_time/len(problems):.2f} seconds")
        print(f"Throughput: {len(problems)/total_time:.2f} problems/second")
    
    @pytest.mark.asyncio
    async def test_high_volume_problem_solving(self):
        """Test high volume problem solving."""
        council = CosmicCouncil()
        
        # Create many simple problems
        problems = []
        for i in range(100):
            problem = ProblemStatement(
                title=f"Volume Test Problem {i}",
                description=f"Problem {i} for volume testing",
                complexity=ProblemComplexity.SIMPLE,
                domain="Volume Testing",
                stakeholders=["Test Stakeholder"],
                constraints={"budget": "$1K"},
                success_criteria=["Simple criteria"]
            )
            problems.append(problem)
        
        # Solve problems in batches
        batch_size = 10
        results = []
        
        start_time = time.time()
        
        for i in range(0, len(problems), batch_size):
            batch = problems[i:i + batch_size]
            tasks = [council.solve_problem(problem) for problem in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify results
        assert len(results) == 100
        for result in results:
            assert result.status == "completed"
            assert result.overall_confidence > 0.0
        
        print(f"Solved {len(problems)} problems in {total_time:.2f} seconds")
        print(f"Throughput: {len(problems)/total_time:.2f} problems/second")
        print(f"Average time per problem: {total_time/len(problems):.2f} seconds")
        
        # Performance assertions
        assert total_time < 300  # Should complete within 5 minutes
        assert len(problems)/total_time > 0.5  # At least 0.5 problems per second
    
    @pytest.mark.asyncio
    async def test_workflow_concurrent_execution(self):
        """Test concurrent workflow execution."""
        workflow = ProblemSolvingWorkflow()
        
        # Create multiple problems
        problems = []
        for i in range(15):
            problem_data = {
                "title": f"Workflow Load Test {i}",
                "description": f"Workflow problem {i} for load testing",
                "complexity": "moderate",
                "domain": "Workflow Testing",
                "stakeholders": ["Test Stakeholder"],
                "constraints": {"budget": "$5K"},
                "success_criteria": ["Test criteria"]
            }
            problems.append(problem_data)
        
        # Execute workflows concurrently
        start_time = time.time()
        
        tasks = []
        for problem_data in problems:
            task = self._execute_workflow(workflow, problem_data)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all workflows completed
        for result in results:
            assert result["status"] == "completed"
            assert result["overall_confidence"] > 0.0
        
        print(f"Executed {len(problems)} workflows in {total_time:.2f} seconds")
        print(f"Average time per workflow: {total_time/len(problems):.2f} seconds")
        print(f"Throughput: {len(problems)/total_time:.2f} workflows/second")
        
        # Performance assertions
        assert total_time < 180  # Should complete within 3 minutes
        assert len(results) == 15  # All workflows completed
    
    async def _execute_workflow(self, workflow: ProblemSolvingWorkflow, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method to execute a workflow."""
        session = await workflow.start_session(problem_data)
        result = await workflow.execute_complete_workflow(session.session_id)
        return result
    
    @pytest.mark.asyncio
    async def test_ai_enhanced_workflow_load(self):
        """Test AI-enhanced workflow under load."""
        ai_config = AIWorkflowConfig(
            enable_ai_enhancement=True,
            ai_confidence_threshold=0.8,
            max_ai_iterations=2
        )
        
        workflow = AIEnhancedProblemSolvingWorkflow(ai_config=ai_config)
        
        # Create multiple problems
        problems = []
        for i in range(10):
            problem_data = {
                "title": f"AI Load Test {i}",
                "description": f"AI-enhanced problem {i} for load testing",
                "complexity": "moderate",
                "domain": "AI Testing",
                "stakeholders": ["Test Stakeholder"],
                "constraints": {"budget": "$5K"},
                "success_criteria": ["Test criteria"]
            }
            problems.append(problem_data)
        
        # Execute AI-enhanced workflows concurrently
        start_time = time.time()
        
        tasks = []
        for problem_data in problems:
            task = self._execute_ai_workflow(workflow, problem_data)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all workflows completed
        for result in results:
            assert result["status"] == "completed"
            assert result["ai_enhancement_used"] is True
            assert result["overall_confidence"] > 0.0
        
        print(f"Executed {len(problems)} AI-enhanced workflows in {total_time:.2f} seconds")
        print(f"Average time per AI workflow: {total_time/len(problems):.2f} seconds")
        print(f"Throughput: {len(problems)/total_time:.2f} AI workflows/second")
        
        # Performance assertions
        assert total_time < 240  # Should complete within 4 minutes
        assert len(results) == 10  # All workflows completed
    
    async def _execute_ai_workflow(self, workflow: AIEnhancedProblemSolvingWorkflow, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method to execute an AI-enhanced workflow."""
        session = await workflow.start_ai_enhanced_session(problem_data)
        result = await workflow.execute_ai_enhanced_workflow(session.session_id)
        return result
    
    @pytest.mark.asyncio
    async def test_mixed_complexity_load(self):
        """Test load with mixed problem complexities."""
        council = CosmicCouncil()
        
        # Create problems with different complexities
        complexities = [ProblemComplexity.SIMPLE, ProblemComplexity.MODERATE, ProblemComplexity.COMPLEX]
        problems = []
        
        for complexity in complexities:
            for i in range(10):
                problem = ProblemStatement(
                    title=f"Mixed Load Test {complexity.value} {i}",
                    description=f"Problem {i} with {complexity.value} complexity",
                    complexity=complexity,
                    domain="Mixed Testing",
                    stakeholders=["Test Stakeholder"],
                    constraints={"budget": "$5K"},
                    success_criteria=["Test criteria"]
                )
                problems.append(problem)
        
        # Solve all problems concurrently
        start_time = time.time()
        
        tasks = [council.solve_problem(problem) for problem in problems]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all problems were solved
        for result in results:
            assert result.status == "completed"
            assert result.overall_confidence > 0.0
        
        # Analyze performance by complexity
        complexity_times = {}
        for i, result in enumerate(results):
            complexity = problems[i].complexity.value
            if complexity not in complexity_times:
                complexity_times[complexity] = []
            complexity_times[complexity].append(result.total_processing_time)
        
        print(f"Solved {len(problems)} mixed complexity problems in {total_time:.2f} seconds")
        for complexity, times in complexity_times.items():
            avg_time = sum(times) / len(times)
            print(f"Average time for {complexity} problems: {avg_time:.2f} seconds")
        
        # Performance assertions
        assert total_time < 180  # Should complete within 3 minutes
        assert len(results) == 30  # All problems solved
        
        # Complex problems should take longer than simple ones
        simple_avg = sum(complexity_times["simple"]) / len(complexity_times["simple"])
        complex_avg = sum(complexity_times["complex"]) / len(complexity_times["complex"])
        assert complex_avg > simple_avg
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """Test memory usage under load."""
        import psutil
        import os
        
        council = CosmicCouncil()
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create and solve many problems
        problems = []
        for i in range(50):
            problem = ProblemStatement(
                title=f"Memory Test Problem {i}",
                description=f"Problem {i} for memory testing",
                complexity=ProblemComplexity.SIMPLE,
                domain="Memory Testing",
                stakeholders=["Test Stakeholder"],
                constraints={"budget": "$1K"},
                success_criteria=["Test criteria"]
            )
            problems.append(problem)
        
        # Solve problems in batches to monitor memory
        batch_size = 10
        max_memory = initial_memory
        
        for i in range(0, len(problems), batch_size):
            batch = problems[i:i + batch_size]
            tasks = [council.solve_problem(problem) for problem in batch]
            await asyncio.gather(*tasks)
            
            # Check memory usage
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            max_memory = max(max_memory, current_memory)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        peak_memory_increase = max_memory - initial_memory
        
        print(f"Initial memory: {initial_memory:.2f} MB")
        print(f"Final memory: {final_memory:.2f} MB")
        print(f"Memory increase: {memory_increase:.2f} MB")
        print(f"Peak memory increase: {peak_memory_increase:.2f} MB")
        
        # Memory assertions
        assert memory_increase < 500  # Should not increase by more than 500MB
        assert peak_memory_increase < 1000  # Peak should not exceed 1GB increase
    
    @pytest.mark.asyncio
    async def test_concurrent_session_management(self):
        """Test concurrent session management."""
        workflow = ProblemSolvingWorkflow()
        
        # Create many concurrent sessions
        sessions = []
        for i in range(25):
            problem_data = {
                "title": f"Session Test {i}",
                "description": f"Problem {i} for session testing",
                "complexity": "simple",
                "domain": "Session Testing",
                "stakeholders": ["Test Stakeholder"],
                "constraints": {"budget": "$1K"},
                "success_criteria": ["Test criteria"]
            }
            session = await workflow.start_session(problem_data)
            sessions.append(session)
        
        # Verify all sessions were created
        assert len(sessions) == 25
        assert workflow.active_sessions == 25
        
        # Execute steps concurrently across sessions
        start_time = time.time()
        
        tasks = []
        for session in sessions:
            task = workflow.execute_step(session.session_id, "problem_definition")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all steps completed
        for result in results:
            assert result.status == "completed"
            assert result.confidence > 0.0
        
        print(f"Executed {len(sessions)} concurrent sessions in {total_time:.2f} seconds")
        print(f"Average time per session: {total_time/len(sessions):.2f} seconds")
        
        # Performance assertions
        assert total_time < 60  # Should complete within 1 minute
        assert len(results) == 25  # All sessions completed
        
        # Clean up sessions
        for session in sessions:
            workflow.cleanup_session(session.session_id)
        
        assert workflow.active_sessions == 0
    
    @pytest.mark.asyncio
    async def test_throughput_benchmark(self):
        """Test system throughput benchmark."""
        council = CosmicCouncil()
        
        # Create simple problems for throughput testing
        problems = []
        for i in range(100):
            problem = ProblemStatement(
                title=f"Throughput Test {i}",
                description=f"Problem {i} for throughput testing",
                complexity=ProblemComplexity.SIMPLE,
                domain="Throughput Testing",
                stakeholders=["Test Stakeholder"],
                constraints={"budget": "$1K"},
                success_criteria=["Test criteria"]
            )
            problems.append(problem)
        
        # Measure throughput
        start_time = time.time()
        
        # Process in batches for better throughput
        batch_size = 20
        total_processed = 0
        
        for i in range(0, len(problems), batch_size):
            batch = problems[i:i + batch_size]
            tasks = [council.solve_problem(problem) for problem in batch]
            results = await asyncio.gather(*tasks)
            total_processed += len(results)
        
        end_time = time.time()
        total_time = end_time - start_time
        throughput = total_processed / total_time
        
        print(f"Processed {total_processed} problems in {total_time:.2f} seconds")
        print(f"Throughput: {throughput:.2f} problems/second")
        
        # Throughput assertions
        assert throughput > 1.0  # Should process at least 1 problem per second
        assert total_processed == 100  # All problems processed
        assert total_time < 120  # Should complete within 2 minutes
    
    @pytest.mark.asyncio
    async def test_response_time_consistency(self):
        """Test response time consistency under load."""
        council = CosmicCouncil()
        
        # Create problems for consistency testing
        problems = []
        for i in range(30):
            problem = ProblemStatement(
                title=f"Consistency Test {i}",
                description=f"Problem {i} for consistency testing",
                complexity=ProblemComplexity.MODERATE,
                domain="Consistency Testing",
                stakeholders=["Test Stakeholder"],
                constraints={"budget": "$5K"},
                success_criteria=["Test criteria"]
            )
            problems.append(problem)
        
        # Solve problems and measure response times
        response_times = []
        
        for problem in problems:
            start_time = time.time()
            result = await council.solve_problem(problem)
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            
            assert result.status == "completed"
            assert result.overall_confidence > 0.0
        
        # Analyze response time consistency
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        std_deviation = (sum((t - avg_response_time) ** 2 for t in response_times) / len(response_times)) ** 0.5
        
        print(f"Average response time: {avg_response_time:.2f} seconds")
        print(f"Min response time: {min_response_time:.2f} seconds")
        print(f"Max response time: {max_response_time:.2f} seconds")
        print(f"Standard deviation: {std_deviation:.2f} seconds")
        
        # Consistency assertions
        assert avg_response_time < 10.0  # Average should be under 10 seconds
        assert max_response_time < 30.0  # Max should be under 30 seconds
        assert std_deviation < 5.0  # Standard deviation should be reasonable
        assert len(response_times) == 30  # All problems processed
