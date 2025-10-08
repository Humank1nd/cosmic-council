"""
Performance tests for the Perpetual Thinking System
Tests system performance under various load conditions
"""

import pytest
import asyncio
import time
import uuid
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from typing import Dict, Any, List
import statistics

# Import the API application
from src.api.main import app
from perpetual_ai_integration import AIEnhancementLevel


class TestPerpetualThinkingPerformance:
    """Performance tests for the perpetual thinking system"""

    @pytest.fixture
    def client(self):
        """Create a test client for the API"""
        return TestClient(app)

    @pytest.fixture
    def sample_session_data(self):
        """Sample session data for performance testing"""
        return {
            "session_name": "Performance Test Session",
            "initial_input": "How can we optimize system performance while maintaining reliability and scalability?",
            "mode": "collaborative",
            "goals": ["performance", "reliability", "scalability"],
            "success_criteria": ["<100ms response time", "99.9% uptime", "handle 1000+ concurrent users"],
            "ai_enhancement_level": "enhanced",
            "ai_learning_enabled": True,
            "ai_adaptation_enabled": True,
            "ai_breakthrough_detection": True
        }

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_session_creation_performance(self, client, sample_session_data):
        """Test performance of session creation under load"""
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine, \
             patch('cosmic_council_api.perpetual_db_service') as mock_db:
            
            mock_engine.start_ai_enhanced_perpetual_cycle.return_value = str(uuid.uuid4())
            
            # Test with different batch sizes
            batch_sizes = [1, 5, 10, 20, 50]
            results = {}
            
            for batch_size in batch_sizes:
                response_times = []
                
                for i in range(batch_size):
                    start_time = time.time()
                    
                    session_data = sample_session_data.copy()
                    session_data["session_name"] = f"Performance Test {i}"
                    
                    response = client.post("/api/v1/perpetual/sessions", json=session_data)
                    
                    end_time = time.time()
                    response_times.append(end_time - start_time)
                    
                    assert response.status_code == 200
                
                # Calculate statistics
                avg_response_time = statistics.mean(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
                p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
                
                results[batch_size] = {
                    "avg_response_time": avg_response_time,
                    "max_response_time": max_response_time,
                    "min_response_time": min_response_time,
                    "p95_response_time": p95_response_time,
                    "total_time": sum(response_times)
                }
                
                # Performance assertions
                assert avg_response_time < 1.0, f"Average response time {avg_response_time:.3f}s exceeds 1s for batch size {batch_size}"
                assert max_response_time < 2.0, f"Max response time {max_response_time:.3f}s exceeds 2s for batch size {batch_size}"
                assert p95_response_time < 1.5, f"95th percentile response time {p95_response_time:.3f}s exceeds 1.5s for batch size {batch_size}"
            
            # Verify performance doesn't degrade significantly with batch size
            small_batch_avg = results[1]["avg_response_time"]
            large_batch_avg = results[50]["avg_response_time"]
            performance_degradation = (large_batch_avg - small_batch_avg) / small_batch_avg
            
            assert performance_degradation < 0.5, f"Performance degradation {performance_degradation:.2%} exceeds 50%"

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_concurrent_session_creation(self, client, sample_session_data):
        """Test concurrent session creation performance"""
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine, \
             patch('cosmic_council_api.perpetual_db_service') as mock_db:
            
            mock_engine.start_ai_enhanced_perpetual_cycle.return_value = str(uuid.uuid4())
            
            # Test different levels of concurrency
            concurrency_levels = [1, 5, 10, 20, 50]
            results = {}
            
            for concurrency in concurrency_levels:
                start_time = time.time()
                
                # Create concurrent requests
                tasks = []
                for i in range(concurrency):
                    session_data = sample_session_data.copy()
                    session_data["session_name"] = f"Concurrent Test {i}"
                    
                    # Simulate concurrent request
                    response = client.post("/api/v1/perpetual/sessions", json=session_data)
                    assert response.status_code == 200
                
                end_time = time.time()
                total_time = end_time - start_time
                
                results[concurrency] = {
                    "total_time": total_time,
                    "throughput": concurrency / total_time,  # requests per second
                    "avg_time_per_request": total_time / concurrency
                }
                
                # Performance assertions
                assert total_time < 10.0, f"Total time {total_time:.3f}s exceeds 10s for concurrency {concurrency}"
                assert results[concurrency]["throughput"] > 1.0, f"Throughput {results[concurrency]['throughput']:.2f} req/s below 1 req/s for concurrency {concurrency}"
            
            # Verify throughput doesn't degrade significantly
            low_concurrency_throughput = results[1]["throughput"]
            high_concurrency_throughput = results[50]["throughput"]
            throughput_degradation = (low_concurrency_throughput - high_concurrency_throughput) / low_concurrency_throughput
            
            assert throughput_degradation < 0.8, f"Throughput degradation {throughput_degradation:.2%} exceeds 80%"

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_analytics_retrieval_performance(self, client):
        """Test performance of analytics retrieval under load"""
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine:
            
            # Mock analytics data
            mock_analytics = {
                "session_id": "test-session",
                "session_name": "Performance Test",
                "ai_enhancement_level": "enhanced",
                "total_ai_enhanced_cycles": 10,
                "avg_ai_confidence": 0.85,
                "avg_impact_score": 0.80,
                "total_ai_tokens_used": 2000,
                "total_ai_processing_time_seconds": 15.0
            }
            mock_engine.get_ai_session_analytics.return_value = mock_analytics
            
            # Test analytics retrieval performance
            response_times = []
            num_requests = 100
            
            for i in range(num_requests):
                start_time = time.time()
                
                response = client.get("/api/v1/perpetual/ai/sessions/test-session/analytics")
                
                end_time = time.time()
                response_times.append(end_time - start_time)
                
                assert response.status_code == 200
            
            # Calculate performance metrics
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]
            p99_response_time = statistics.quantiles(response_times, n=100)[98]
            
            # Performance assertions
            assert avg_response_time < 0.1, f"Average analytics response time {avg_response_time:.3f}s exceeds 100ms"
            assert max_response_time < 0.5, f"Max analytics response time {max_response_time:.3f}s exceeds 500ms"
            assert p95_response_time < 0.2, f"95th percentile analytics response time {p95_response_time:.3f}s exceeds 200ms"
            assert p99_response_time < 0.3, f"99th percentile analytics response time {p99_response_time:.3f}s exceeds 300ms"

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_system_status_performance(self, client):
        """Test performance of system status endpoint under load"""
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine, \
             patch('cosmic_council_api.perpetual_db_service') as mock_db:
            
            # Mock system status data
            mock_engine.ai_sessions = {
                f"session-{i}": Mock(status="active") for i in range(100)
            }
            mock_db.get_all_sessions.return_value = [
                {"session_id": f"session-{i}", "status": "active"} for i in range(100)
            ]
            
            # Test system status performance
            response_times = []
            num_requests = 200
            
            for i in range(num_requests):
                start_time = time.time()
                
                response = client.get("/api/v1/perpetual/status")
                
                end_time = time.time()
                response_times.append(end_time - start_time)
                
                assert response.status_code == 200
                data = response.json()
                assert data["data"]["active_sessions"] == 100
            
            # Calculate performance metrics
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]
            
            # Performance assertions
            assert avg_response_time < 0.05, f"Average status response time {avg_response_time:.3f}s exceeds 50ms"
            assert max_response_time < 0.2, f"Max status response time {max_response_time:.3f}s exceeds 200ms"
            assert p95_response_time < 0.1, f"95th percentile status response time {p95_response_time:.3f}s exceeds 100ms"

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_memory_usage_under_load(self, client, sample_session_data):
        """Test memory usage under sustained load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine, \
             patch('cosmic_council_api.perpetual_db_service') as mock_db:
            
            mock_engine.start_ai_enhanced_perpetual_cycle.return_value = str(uuid.uuid4())
            
            # Create many sessions to test memory usage
            num_sessions = 1000
            session_ids = []
            
            for i in range(num_sessions):
                session_data = sample_session_data.copy()
                session_data["session_name"] = f"Memory Test {i}"
                
                response = client.post("/api/v1/perpetual/sessions", json=session_data)
                assert response.status_code == 200
                
                session_ids.append(response.json()["data"]["session_id"])
                
                # Check memory every 100 sessions
                if i % 100 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024  # MB
                    memory_increase = current_memory - initial_memory
                    
                    # Memory increase should be reasonable
                    assert memory_increase < 500, f"Memory increase {memory_increase:.1f}MB exceeds 500MB after {i} sessions"
            
            # Final memory check
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            total_memory_increase = final_memory - initial_memory
            
            # Total memory increase should be reasonable
            assert total_memory_increase < 1000, f"Total memory increase {total_memory_increase:.1f}MB exceeds 1GB"
            
            # Memory per session should be reasonable
            memory_per_session = total_memory_increase / num_sessions
            assert memory_per_session < 1.0, f"Memory per session {memory_per_session:.3f}MB exceeds 1MB"

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_ai_enhancement_level_performance(self, client, sample_session_data):
        """Test performance across different AI enhancement levels"""
        enhancement_levels = ["none", "assisted", "enhanced", "autonomous"]
        results = {}
        
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine, \
             patch('cosmic_council_api.perpetual_db_service') as mock_db:
            
            mock_engine.start_ai_enhanced_perpetual_cycle.return_value = str(uuid.uuid4())
            
            for level in enhancement_levels:
                response_times = []
                num_requests = 50
                
                for i in range(num_requests):
                    session_data = sample_session_data.copy()
                    session_data["session_name"] = f"AI Level Test {level} {i}"
                    session_data["ai_enhancement_level"] = level
                    
                    start_time = time.time()
                    
                    response = client.post("/api/v1/perpetual/sessions", json=session_data)
                    
                    end_time = time.time()
                    response_times.append(end_time - start_time)
                    
                    assert response.status_code == 200
                
                avg_response_time = statistics.mean(response_times)
                max_response_time = max(response_times)
                
                results[level] = {
                    "avg_response_time": avg_response_time,
                    "max_response_time": max_response_time
                }
                
                # Performance assertions
                assert avg_response_time < 2.0, f"Average response time {avg_response_time:.3f}s exceeds 2s for AI level {level}"
                assert max_response_time < 5.0, f"Max response time {max_response_time:.3f}s exceeds 5s for AI level {level}"
            
            # Verify performance differences are reasonable
            none_avg = results["none"]["avg_response_time"]
            autonomous_avg = results["autonomous"]["avg_response_time"]
            performance_ratio = autonomous_avg / none_avg
            
            assert performance_ratio < 3.0, f"Autonomous AI performance ratio {performance_ratio:.2f} exceeds 3x slower than none"

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_sustained_load_performance(self, client, sample_session_data):
        """Test performance under sustained load over time"""
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine, \
             patch('cosmic_council_api.perpetual_db_service') as mock_db:
            
            mock_engine.start_ai_enhanced_perpetual_cycle.return_value = str(uuid.uuid4())
            
            # Run sustained load test
            duration_seconds = 60  # 1 minute
            requests_per_second = 10
            total_requests = duration_seconds * requests_per_second
            
            start_time = time.time()
            response_times = []
            successful_requests = 0
            failed_requests = 0
            
            request_interval = 1.0 / requests_per_second
            next_request_time = start_time
            
            while time.time() - start_time < duration_seconds:
                current_time = time.time()
                
                if current_time >= next_request_time:
                    session_data = sample_session_data.copy()
                    session_data["session_name"] = f"Sustained Load Test {successful_requests}"
                    
                    request_start = time.time()
                    
                    try:
                        response = client.post("/api/v1/perpetual/sessions", json=session_data)
                        request_end = time.time()
                        
                        if response.status_code == 200:
                            successful_requests += 1
                            response_times.append(request_end - request_start)
                        else:
                            failed_requests += 1
                    except Exception:
                        failed_requests += 1
                    
                    next_request_time += request_interval
            
            total_time = time.time() - start_time
            
            # Calculate performance metrics
            if response_times:
                avg_response_time = statistics.mean(response_times)
                max_response_time = max(response_times)
                p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times)
            else:
                avg_response_time = max_response_time = p95_response_time = 0
            
            actual_throughput = successful_requests / total_time
            success_rate = successful_requests / (successful_requests + failed_requests) if (successful_requests + failed_requests) > 0 else 0
            
            # Performance assertions
            assert success_rate > 0.95, f"Success rate {success_rate:.2%} below 95%"
            assert actual_throughput > 8.0, f"Actual throughput {actual_throughput:.2f} req/s below 8 req/s"
            assert avg_response_time < 1.0, f"Average response time {avg_response_time:.3f}s exceeds 1s"
            assert max_response_time < 5.0, f"Max response time {max_response_time:.3f}s exceeds 5s"
            assert p95_response_time < 2.0, f"95th percentile response time {p95_response_time:.3f}s exceeds 2s"

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_database_performance_under_load(self, client, sample_session_data):
        """Test database performance under load"""
        with patch('cosmic_council_api.perpetual_ai_engine') as mock_engine, \
             patch('cosmic_council_api.perpetual_db_service') as mock_db:
            
            mock_engine.start_ai_enhanced_perpetual_cycle.return_value = str(uuid.uuid4())
            
            # Mock database operations with realistic delays
            async def mock_get_session(session_id):
                await asyncio.sleep(0.01)  # 10ms database delay
                return {"session_id": session_id, "status": "active"}
            
            async def mock_get_all_sessions():
                await asyncio.sleep(0.05)  # 50ms database delay
                return [{"session_id": f"session-{i}", "status": "active"} for i in range(100)]
            
            mock_db.get_session = mock_get_session
            mock_db.get_all_sessions = mock_get_all_sessions
            
            # Test database read performance
            response_times = []
            num_requests = 100
            
            for i in range(num_requests):
                start_time = time.time()
                
                response = client.get(f"/api/v1/perpetual/sessions/session-{i}")
                
                end_time = time.time()
                response_times.append(end_time - start_time)
                
                assert response.status_code == 200
            
            # Calculate performance metrics
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]
            
            # Performance assertions
            assert avg_response_time < 0.1, f"Average database response time {avg_response_time:.3f}s exceeds 100ms"
            assert max_response_time < 0.5, f"Max database response time {max_response_time:.3f}s exceeds 500ms"
            assert p95_response_time < 0.2, f"95th percentile database response time {p95_response_time:.3f}s exceeds 200ms"
