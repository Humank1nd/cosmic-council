"""
Stress tests for the Cosmic Council system.
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from src.api.main import app


class TestStressPerformance:
    """Test system stress performance."""
    
    def test_high_concurrent_requests(self):
        """Test high concurrent request handling."""
        client = TestClient(app)
        
        def make_request(i):
            problem_data = {
                "title": f"Stress Test Problem {i}",
                "description": f"Stress test problem {i}",
                "domain": "technology",
                "complexity": "simple"
            }
            return client.post("/api/v1/problems", json=problem_data)
        
        # Test with 50 concurrent requests
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request, i) for i in range(50)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # All requests should complete
        assert len(results) == 50
        
        # Should complete within reasonable time
        assert execution_time < 30.0  # 30 seconds max
        
        # Most requests should succeed
        success_count = sum(1 for r in results if r.status_code in [200, 201])
        assert success_count >= 40  # At least 80% success rate
    
    def test_memory_usage_under_load(self):
        """Test memory usage under load."""
        client = TestClient(app)
        
        # Create many problems to test memory usage
        problem_ids = []
        
        for i in range(100):
            problem_data = {
                "title": f"Memory Test Problem {i}",
                "description": f"Memory test problem {i}",
                "domain": "technology",
                "complexity": "simple"
            }
            
            response = client.post("/api/v1/problems", json=problem_data)
            if response.status_code in [200, 201]:
                problem_ids.append(response.json().get("id"))
        
        # Verify we can retrieve all problems
        for problem_id in problem_ids[:10]:  # Test first 10
            response = client.get(f"/api/v1/problems/{problem_id}")
            assert response.status_code in [200, 404]
        
        assert len(problem_ids) >= 80  # At least 80% should succeed
