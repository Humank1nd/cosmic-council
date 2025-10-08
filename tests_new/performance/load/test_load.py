"""
Load testing for the Cosmic Council system.
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from src.api.main import app


class TestLoadPerformance:
    """Test system load performance."""
    
    def test_concurrent_problem_creation(self):
        """Test concurrent problem creation."""
        client = TestClient(app)
        
        def create_problem(i):
            problem_data = {
                "title": f"Load Test Problem {i}",
                "description": f"Load test problem {i}",
                "domain": "technology",
                "complexity": "simple"
            }
            return client.post("/api/v1/problems", json=problem_data)
        
        # Test with 10 concurrent requests
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_problem, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # All requests should complete
        assert len(results) == 10
        
        # Should complete within reasonable time (adjust as needed)
        assert execution_time < 10.0  # 10 seconds max
        
        # Most requests should succeed
        success_count = sum(1 for r in results if r.status_code in [200, 201])
        assert success_count >= 8  # At least 80% success rate
