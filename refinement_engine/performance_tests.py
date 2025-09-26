"""
Cosmic Council Refinement Engine - Performance Tests
Performance and load testing for the refinement engine.
"""

import pytest
import asyncio
import time
import statistics
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import uuid
import psutil
import gc

from .test_config import TestConfig, TestDataGenerator, TestAssertions
from .integration_tests import IntegrationTestBase


class PerformanceTestBase(IntegrationTestBase):
    """Base class for performance tests."""
    
    @pytest.fixture(scope="class")
    def performance_config(self):
        """Get performance test configuration."""
        return TestConfig(
            test_database_url="sqlite:///:memory:",
            use_in_memory_db=True,
            mock_ai_services=True,
            openai_api_key=None,
            anthropic_api_key=None,
            test_jwt_secret="performance-test-secret",
            test_user_password="PerformanceTest123!",
            enable_metrics_server=False,
            metrics_port=9092,
            enable_sentry=False,
            test_timeout=600,  # 10 minutes for performance tests
            max_concurrent_tests=10,
            cleanup_after_tests=True,
            performance_test_iterations=50,
            load_test_concurrency=20
        )


class TestProblemProcessingPerformance(PerformanceTestBase):
    """Test problem processing performance."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_single_problem_processing_time(self, test_database, test_ai_manager):
        """Test single problem processing time."""
        db_manager = test_database
        ai_manager = test_ai_manager
        
        # Generate test problem
        problem_data = TestDataGenerator.generate_problem_data("carbon_emissions")
        
        # Create problem
        problem_id = await db_manager.create_problem(
            title=problem_data["title"],
            description=problem_data["description"],
            initial_layer=problem_data["initial_layer"]
        )
        
        # Measure processing time
        start_time = time.time()
        
        from .layer_orchestration import LayerOrchestrator
        orchestrator = LayerOrchestrator()
        problem_context = await orchestrator.process_problem_continuously(
            problem_id=problem_id,
            title=problem_data["title"],
            description=problem_data["description"],
            max_iterations=5
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Assertions
        TestAssertions.assert_problem_context_valid(problem_context)
        assert processing_time < 30.0  # Should complete within 30 seconds
        assert len(problem_context.layer_runs) > 0
        
        print(f"Single problem processing time: {processing_time:.2f} seconds")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_problem_processing(self, test_database, test_ai_manager):
        """Test concurrent problem processing performance."""
        db_manager = test_database
        ai_manager = test_ai_manager
        
        # Generate test problems
        problem_types = ["carbon_emissions", "renewable_energy", "sustainable_transport"]
        problems = []
        
        for i, problem_type in enumerate(problem_types):
            problem_data = TestDataGenerator.generate_problem_data(problem_type)
            problem_id = await db_manager.create_problem(
                title=f"{problem_data['title']} {i}",
                description=problem_data["description"],
                initial_layer=problem_data["initial_layer"]
            )
            problems.append((problem_id, problem_data))
        
        # Process problems concurrently
        start_time = time.time()
        
        from .layer_orchestration import LayerOrchestrator
        orchestrator = LayerOrchestrator()
        
        tasks = []
        for problem_id, problem_data in problems:
            task = orchestrator.process_problem_continuously(
                problem_id=problem_id,
                title=problem_data["title"],
                description=problem_data["description"],
                max_iterations=3
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        error_count = len([r for r in results if isinstance(r, Exception)])
        
        # Assertions
        assert len(successful_results) > 0
        assert error_count < len(results)  # Some should succeed
        assert total_time < 60.0  # Should complete within 60 seconds
        
        for result in successful_results:
            TestAssertions.assert_problem_context_valid(result)
        
        print(f"Concurrent processing time: {total_time:.2f} seconds")
        print(f"Successful results: {len(successful_results)}")
        print(f"Errors: {error_count}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_layer_processing_performance(self, test_ai_manager):
        """Test individual layer processing performance."""
        ai_manager = test_ai_manager
        
        from .sector_engine import SectorEngine
        
        # Test each layer
        layers = ["deci", "centi", "milli", "micro"]
        layer_times = {}
        
        for layer in layers:
            sector_engine = SectorEngine(layer, ai_manager)
            
            # Measure layer processing time
            start_time = time.time()
            
            # Execute all sectors for the layer
            result = await sector_engine.execute_red_sector(
                problem_statement="How can we reduce carbon emissions?",
                evidence_refs=[],
                assumptions=[],
                constraints={}
            )
            
            end_time = time.time()
            layer_time = end_time - start_time
            layer_times[layer] = layer_time
            
            # Assertions
            TestAssertions.assert_sector_result_valid(result)
            assert layer_time < 10.0  # Each layer should complete within 10 seconds
        
        # Print performance summary
        print("Layer processing times:")
        for layer, time_taken in layer_times.items():
            print(f"  {layer}: {time_taken:.2f} seconds")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_escalator_performance(self):
        """Test escalator decision performance."""
        from .escalator_fixed import EscalatorEngine, SolutionCandidate
        
        escalator = EscalatorEngine()
        
        # Generate test solutions
        solutions = []
        for i in range(100):
            solution = SolutionCandidate(
                solution_text=f"Test solution {i}",
                confidence_score=0.7 + (i * 0.002),
                completeness_score=0.6 + (i * 0.003),
                novelty_score=0.2,
                alignment_score=0.9,
                net_benefit_score=0.7
            )
            solutions.append(solution)
        
        # Measure escalator performance
        start_time = time.time()
        
        decisions = []
        for i, solution in enumerate(solutions):
            layer_metrics = TestDataGenerator.generate_layer_metrics("deci")
            problem_context = {"original_question": f"Test question {i}"}
            
            decision = escalator.decide(
                problem_id=f"test-problem-{i}",
                current_layer="deci",
                solution_candidate=solution,
                layer_metrics=layer_metrics,
                problem_context=problem_context
            )
            decisions.append(decision)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Assertions
        assert len(decisions) == 100
        assert total_time < 5.0  # Should complete within 5 seconds
        
        for decision in decisions:
            TestAssertions.assert_escalator_decision_valid(decision)
        
        print(f"Escalator performance: {total_time:.2f} seconds for 100 decisions")
        print(f"Average time per decision: {total_time/100:.4f} seconds")


class TestDatabasePerformance(PerformanceTestBase):
    """Test database performance."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_database_write_performance(self, test_database):
        """Test database write performance."""
        db_manager = test_database
        
        # Test problem creation performance
        start_time = time.time()
        
        problem_ids = []
        for i in range(100):
            problem_id = await db_manager.create_problem(
                title=f"Performance Test Problem {i}",
                description=f"Performance test description {i}",
                initial_layer="deci"
            )
            problem_ids.append(problem_id)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Assertions
        assert len(problem_ids) == 100
        assert total_time < 10.0  # Should complete within 10 seconds
        
        print(f"Database write performance: {total_time:.2f} seconds for 100 problems")
        print(f"Average time per write: {total_time/100:.4f} seconds")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_database_read_performance(self, test_database):
        """Test database read performance."""
        db_manager = test_database
        
        # Create test problems
        problem_ids = []
        for i in range(50):
            problem_id = await db_manager.create_problem(
                title=f"Read Test Problem {i}",
                description=f"Read test description {i}",
                initial_layer="deci"
            )
            problem_ids.append(problem_id)
        
        # Test read performance
        start_time = time.time()
        
        problems = []
        for problem_id in problem_ids:
            problem = await db_manager.get_problem(problem_id)
            problems.append(problem)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Assertions
        assert len(problems) == 50
        assert all(p is not None for p in problems)
        assert total_time < 5.0  # Should complete within 5 seconds
        
        print(f"Database read performance: {total_time:.2f} seconds for 50 problems")
        print(f"Average time per read: {total_time/50:.4f} seconds")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_database_concurrent_operations(self, test_database):
        """Test database concurrent operations performance."""
        db_manager = test_database
        
        # Test concurrent writes
        start_time = time.time()
        
        async def create_problem(i):
            return await db_manager.create_problem(
                title=f"Concurrent Test Problem {i}",
                description=f"Concurrent test description {i}",
                initial_layer="deci"
            )
        
        tasks = [create_problem(i) for i in range(20)]
        problem_ids = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Assertions
        assert len(problem_ids) == 20
        assert all(pid is not None for pid in problem_ids)
        assert total_time < 5.0  # Should complete within 5 seconds
        
        print(f"Database concurrent operations: {total_time:.2f} seconds for 20 concurrent writes")
        print(f"Average time per concurrent write: {total_time/20:.4f} seconds")


class TestAIPerformance(PerformanceTestBase):
    """Test AI service performance."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_ai_request_performance(self, test_ai_manager):
        """Test AI request performance."""
        ai_manager = test_ai_manager
        
        # Test OpenAI performance
        start_time = time.time()
        
        responses = []
        for i in range(20):
            response = await ai_manager.process_with_llm(
                f"What are the key factors in reducing carbon emissions? (Request {i})",
                provider="openai"
            )
            responses.append(response)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Assertions
        assert len(responses) == 20
        assert all(r is not None for r in responses)
        assert total_time < 30.0  # Should complete within 30 seconds
        
        # Calculate average response time
        avg_response_time = total_time / 20
        
        print(f"AI request performance: {total_time:.2f} seconds for 20 requests")
        print(f"Average response time: {avg_response_time:.4f} seconds")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_ai_concurrent_requests(self, test_ai_manager):
        """Test AI concurrent request performance."""
        ai_manager = test_ai_manager
        
        # Test concurrent requests
        start_time = time.time()
        
        async def make_request(i):
            return await ai_manager.process_with_llm(
                f"What are the key factors in reducing carbon emissions? (Concurrent {i})",
                provider="openai"
            )
        
        tasks = [make_request(i) for i in range(10)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_responses = [r for r in responses if not isinstance(r, Exception)]
        error_count = len([r for r in responses if isinstance(r, Exception)])
        
        # Assertions
        assert len(successful_responses) > 0
        assert error_count < len(responses)  # Some should succeed
        assert total_time < 20.0  # Should complete within 20 seconds
        
        print(f"AI concurrent requests: {total_time:.2f} seconds for 10 concurrent requests")
        print(f"Successful responses: {len(successful_responses)}")
        print(f"Errors: {error_count}")


class TestSystemResourceUsage(PerformanceTestBase):
    """Test system resource usage."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_usage(self, test_database, test_ai_manager):
        """Test memory usage during processing."""
        db_manager = test_database
        ai_manager = test_ai_manager
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process multiple problems
        from .layer_orchestration import LayerOrchestrator
        orchestrator = LayerOrchestrator()
        
        problem_ids = []
        for i in range(10):
            problem_id = await db_manager.create_problem(
                title=f"Memory Test Problem {i}",
                description=f"Memory test description {i}",
                initial_layer="deci"
            )
            problem_ids.append(problem_id)
        
        # Process problems
        tasks = []
        for problem_id in problem_ids:
            task = orchestrator.process_problem_continuously(
                problem_id=problem_id,
                title=f"Memory Test Problem",
                description="Memory test description",
                max_iterations=2
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Assertions
        assert memory_increase < 100.0  # Should not increase by more than 100MB
        
        print(f"Memory usage: {initial_memory:.2f} MB initial, {final_memory:.2f} MB final")
        print(f"Memory increase: {memory_increase:.2f} MB")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cpu_usage(self, test_database, test_ai_manager):
        """Test CPU usage during processing."""
        db_manager = test_database
        ai_manager = test_ai_manager
        
        # Get initial CPU usage
        initial_cpu = psutil.cpu_percent(interval=1)
        
        # Process problems
        from .layer_orchestration import LayerOrchestrator
        orchestrator = LayerOrchestrator()
        
        problem_ids = []
        for i in range(5):
            problem_id = await db_manager.create_problem(
                title=f"CPU Test Problem {i}",
                description=f"CPU test description {i}",
                initial_layer="deci"
            )
            problem_ids.append(problem_id)
        
        # Process problems concurrently
        tasks = []
        for problem_id in problem_ids:
            task = orchestrator.process_problem_continuously(
                problem_id=problem_id,
                title=f"CPU Test Problem",
                description="CPU test description",
                max_iterations=2
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Get final CPU usage
        final_cpu = psutil.cpu_percent(interval=1)
        
        # Assertions
        assert final_cpu < 90.0  # Should not exceed 90% CPU usage
        
        print(f"CPU usage: {initial_cpu:.2f}% initial, {final_cpu:.2f}% final")


class TestLoadTesting(PerformanceTestBase):
    """Test system under load."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_high_load_processing(self, test_database, test_ai_manager):
        """Test system under high load."""
        db_manager = test_database
        ai_manager = test_ai_manager
        
        # Create many problems
        problem_count = 50
        problem_ids = []
        
        start_time = time.time()
        
        for i in range(problem_count):
            problem_id = await db_manager.create_problem(
                title=f"Load Test Problem {i}",
                description=f"Load test description {i}",
                initial_layer="deci"
            )
            problem_ids.append(problem_id)
        
        creation_time = time.time() - start_time
        
        # Process problems in batches
        batch_size = 10
        processing_times = []
        
        from .layer_orchestration import LayerOrchestrator
        orchestrator = LayerOrchestrator()
        
        for i in range(0, len(problem_ids), batch_size):
            batch = problem_ids[i:i + batch_size]
            
            batch_start = time.time()
            
            tasks = []
            for problem_id in batch:
                task = orchestrator.process_problem_continuously(
                    problem_id=problem_id,
                    title=f"Load Test Problem",
                    description="Load test description",
                    max_iterations=1
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            batch_time = time.time() - batch_start
            processing_times.append(batch_time)
        
        total_processing_time = sum(processing_times)
        
        # Assertions
        assert creation_time < 30.0  # Should create problems quickly
        assert total_processing_time < 300.0  # Should process within 5 minutes
        
        # Calculate statistics
        avg_batch_time = statistics.mean(processing_times)
        max_batch_time = max(processing_times)
        min_batch_time = min(processing_times)
        
        print(f"Load test results:")
        print(f"  Problems created: {problem_count}")
        print(f"  Creation time: {creation_time:.2f} seconds")
        print(f"  Total processing time: {total_processing_time:.2f} seconds")
        print(f"  Average batch time: {avg_batch_time:.2f} seconds")
        print(f"  Max batch time: {max_batch_time:.2f} seconds")
        print(f"  Min batch time: {min_batch_time:.2f} seconds")
    
    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_stress_testing(self, test_database, test_ai_manager):
        """Test system under stress conditions."""
        db_manager = test_database
        ai_manager = test_ai_manager
        
        # Simulate stress conditions
        stress_levels = [10, 20, 30, 40, 50]
        results = {}
        
        for stress_level in stress_levels:
            print(f"Testing stress level: {stress_level}")
            
            # Create problems
            problem_ids = []
            for i in range(stress_level):
                problem_id = await db_manager.create_problem(
                    title=f"Stress Test Problem {i}",
                    description=f"Stress test description {i}",
                    initial_layer="deci"
                )
                problem_ids.append(problem_id)
            
            # Process problems concurrently
            start_time = time.time()
            
            from .layer_orchestration import LayerOrchestrator
            orchestrator = LayerOrchestrator()
            
            tasks = []
            for problem_id in problem_ids:
                task = orchestrator.process_problem_continuously(
                    problem_id=problem_id,
                    title=f"Stress Test Problem",
                    description="Stress test description",
                    max_iterations=1
                )
                tasks.append(task)
            
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Analyze results
            successful = len([r for r in results_list if not isinstance(r, Exception)])
            errors = len([r for r in results_list if isinstance(r, Exception)])
            
            results[stress_level] = {
                "processing_time": processing_time,
                "successful": successful,
                "errors": errors,
                "success_rate": successful / stress_level * 100
            }
            
            print(f"  Processing time: {processing_time:.2f} seconds")
            print(f"  Success rate: {results[stress_level]['success_rate']:.1f}%")
            
            # Clean up
            gc.collect()
        
        # Assertions
        for stress_level, result in results.items():
            assert result["success_rate"] > 50.0  # At least 50% success rate
            assert result["processing_time"] < 120.0  # Should complete within 2 minutes
        
        print("Stress test results:")
        for stress_level, result in results.items():
            print(f"  Level {stress_level}: {result['success_rate']:.1f}% success, {result['processing_time']:.2f}s")


# Run performance tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "performance"])
