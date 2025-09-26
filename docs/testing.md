# Cosmic Council Framework Testing Guide

## Overview

This guide covers comprehensive testing strategies for the Cosmic Council Framework, including unit tests, integration tests, end-to-end tests, and performance testing.

## Testing Philosophy

The Cosmic Council Framework follows a comprehensive testing strategy:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete user workflows
- **Performance Tests**: Test system performance under load
- **Security Tests**: Test security vulnerabilities
- **Chaos Engineering**: Test system resilience

## Test Structure

```
tests/
├── unit/
│   ├── test_cosmic_council_core.py
│   ├── test_enterprise_agents.py
│   ├── test_workflow.py
│   ├── test_ai_integration.py
│   └── test_analytics.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_database_operations.py
│   ├── test_108_cycle_system.py
│   └── test_policy_engine.py
├── e2e/
│   ├── test_problem_solving_workflow.py
│   ├── test_web_interface.py
│   └── test_analytics_dashboard.py
├── performance/
│   ├── test_load.py
│   ├── test_stress.py
│   └── test_volume.py
├── security/
│   ├── test_authentication.py
│   ├── test_authorization.py
│   └── test_input_validation.py
├── fixtures/
│   ├── sample_problems.py
│   ├── sample_cycles.py
│   └── sample_solutions.py
└── conftest.py
```

## Unit Testing

### Core Framework Tests

```python
# tests/unit/test_cosmic_council_core.py
import pytest
from cosmic_council_core import CosmicCouncil, ProblemStatement, ProblemComplexity

class TestCosmicCouncil:
    def test_initialization(self):
        """Test Cosmic Council initialization"""
        council = CosmicCouncil()
        assert council is not None
        assert len(council.enterprises) == 6
        assert council.enterprises[0].name == "Red Owl"
    
    def test_problem_statement_creation(self):
        """Test problem statement creation"""
        problem = ProblemStatement(
            title="Test Problem",
            description="Test description",
            complexity=ProblemComplexity.SIMPLE,
            domain="Test Domain"
        )
        assert problem.title == "Test Problem"
        assert problem.complexity == ProblemComplexity.SIMPLE
    
    @pytest.mark.asyncio
    async def test_solve_simple_problem(self):
        """Test solving a simple problem"""
        council = CosmicCouncil()
        problem = ProblemStatement(
            title="Simple Test Problem",
            description="A simple test problem",
            complexity=ProblemComplexity.SIMPLE,
            domain="Test"
        )
        
        result = await council.solve_problem(problem)
        
        assert result.status == "completed"
        assert result.overall_confidence > 0.0
        assert len(result.enterprise_results) == 6
    
    @pytest.mark.asyncio
    async def test_solve_complex_problem(self):
        """Test solving a complex problem"""
        council = CosmicCouncil()
        problem = ProblemStatement(
            title="Complex Test Problem",
            description="A complex test problem with multiple facets",
            complexity=ProblemComplexity.COMPLEX,
            domain="Test",
            stakeholders=["Stakeholder 1", "Stakeholder 2"],
            constraints={"budget": "$10K", "timeline": "1 month"}
        )
        
        result = await council.solve_problem(problem)
        
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
```

### Enterprise Agent Tests

```python
# tests/unit/test_enterprise_agents.py
import pytest
from enhanced_enterprise_agents import (
    EnhancedRedOwlAgent, EnhancedOrangeOrangutanAgent,
    Problem, ProblemComplexity
)

class TestEnhancedEnterpriseAgents:
    def test_red_owl_agent_initialization(self):
        """Test Red Owl agent initialization"""
        agent = EnhancedRedOwlAgent()
        assert agent.name == "Red Owl"
        assert agent.role == "Research & Knowledge Gathering"
        assert agent.color == "#ef4444"
    
    @pytest.mark.asyncio
    async def test_red_owl_problem_processing(self):
        """Test Red Owl agent problem processing"""
        agent = EnhancedRedOwlAgent()
        problem = Problem(
            title="Research Test Problem",
            description="A problem requiring research",
            complexity=ProblemComplexity.MODERATE,
            domain="Research"
        )
        
        result = await agent.process_problem_enhanced(problem)
        
        assert result["status"] == "completed"
        assert result["confidence_score"] > 0.0
        assert result["analysis_depth"] in ["shallow", "moderate", "deep"]
        assert result["framework_applied"] is not None
        assert len(result["insights"]) > 0
        assert len(result["recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_orange_orangutan_problem_processing(self):
        """Test Orange Orangutan agent problem processing"""
        agent = EnhancedOrangeOrangutanAgent()
        problem = Problem(
            title="Logistics Test Problem",
            description="A problem requiring logistics planning",
            complexity=ProblemComplexity.COMPLEX,
            domain="Logistics"
        )
        
        result = await agent.process_problem_enhanced(problem)
        
        assert result["status"] == "completed"
        assert result["confidence_score"] > 0.0
        assert result["analysis_depth"] in ["shallow", "moderate", "deep"]
        assert result["framework_applied"] is not None
        assert len(result["insights"]) > 0
        assert len(result["recommendations"]) > 0
        assert "logistics_plan" in result
        assert "resource_requirements" in result
```

### Workflow Tests

```python
# tests/unit/test_workflow.py
import pytest
from problem_solving_workflow import ProblemSolvingWorkflow, WorkflowStep

class TestProblemSolvingWorkflow:
    def test_workflow_initialization(self):
        """Test workflow initialization"""
        workflow = ProblemSolvingWorkflow()
        assert workflow is not None
        assert len(workflow.steps) == 10
    
    @pytest.mark.asyncio
    async def test_workflow_execution(self):
        """Test complete workflow execution"""
        workflow = ProblemSolvingWorkflow()
        problem_data = {
            "title": "Workflow Test Problem",
            "description": "A problem for workflow testing",
            "complexity": "moderate",
            "domain": "Test"
        }
        
        session = await workflow.start_session(problem_data)
        result = await workflow.execute_complete_workflow(session.session_id)
        
        assert result["status"] == "completed"
        assert result["overall_confidence"] > 0.0
        assert len(result["step_results"]) == 10
        
        # Verify each step was executed
        for step in WorkflowStep:
            assert step.value in result["step_results"]
            step_result = result["step_results"][step.value]
            assert step_result["status"] == "completed"
            assert step_result["confidence"] > 0.0
```

## Integration Testing

### API Endpoint Tests

```python
# tests/integration/test_api_endpoints.py
import pytest
import httpx
from fastapi.testclient import TestClient
from cosmic_council_api import app

class TestAPIEndpoints:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_create_problem(self, client):
        """Test problem creation endpoint"""
        problem_data = {
            "title": "API Test Problem",
            "description": "A problem for API testing",
            "complexity": "moderate",
            "domain": "Test",
            "stakeholders": ["Test Stakeholder"],
            "constraints": {"budget": "$5K"},
            "success_criteria": ["Test criteria"]
        }
        
        response = client.post("/api/v1/problems", json=problem_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "API Test Problem"
        assert "problem_id" in data
        assert data["status"] == "pending"
    
    def test_get_problem(self, client):
        """Test problem retrieval endpoint"""
        # First create a problem
        problem_data = {
            "title": "Get Test Problem",
            "description": "A problem for get testing",
            "complexity": "simple",
            "domain": "Test"
        }
        
        create_response = client.post("/api/v1/problems", json=problem_data)
        problem_id = create_response.json()["problem_id"]
        
        # Then retrieve it
        response = client.get(f"/api/v1/problems/{problem_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["problem_id"] == problem_id
        assert data["title"] == "Get Test Problem"
    
    def test_create_and_execute_cycle(self, client):
        """Test cycle creation and execution"""
        # Create a problem first
        problem_data = {
            "title": "Cycle Test Problem",
            "description": "A problem for cycle testing",
            "complexity": "moderate",
            "domain": "Test"
        }
        
        problem_response = client.post("/api/v1/problems", json=problem_data)
        problem_id = problem_response.json()["problem_id"]
        
        # Create a cycle
        cycle_data = {
            "problem_id": problem_id,
            "objective": "Test cycle objective",
            "priority": 3
        }
        
        cycle_response = client.post("/api/v1/cycles", json=cycle_data)
        assert cycle_response.status_code == 201
        cycle_id = cycle_response.json()["cycle_id"]
        
        # Execute the cycle
        execute_response = client.post(f"/api/v1/cycles/{cycle_id}/execute")
        assert execute_response.status_code == 200
        
        # Check cycle status
        status_response = client.get(f"/api/v1/cycles/{cycle_id}")
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["status"] in ["running", "completed"]
```

### Database Integration Tests

```python
# tests/integration/test_database_operations.py
import pytest
from database_operations import (
    ProblemRepository, CycleRepository, SolutionRepository,
    get_db_session
)
from database_models import Problem, Cycle, Solution

class TestDatabaseOperations:
    @pytest.fixture
    def db_session(self):
        with get_db_session() as session:
            yield session
    
    def test_problem_crud_operations(self, db_session):
        """Test problem CRUD operations"""
        repo = ProblemRepository()
        
        # Create
        problem_data = {
            "title": "Database Test Problem",
            "description": "A problem for database testing",
            "complexity": "moderate",
            "domain": "Test"
        }
        
        problem = repo.create_problem(problem_data)
        assert problem.id is not None
        assert problem.title == "Database Test Problem"
        
        # Read
        retrieved_problem = repo.get_problem(problem.id)
        assert retrieved_problem.title == "Database Test Problem"
        
        # Update
        updated_data = {"title": "Updated Database Test Problem"}
        updated_problem = repo.update_problem(problem.id, updated_data)
        assert updated_problem.title == "Updated Database Test Problem"
        
        # Delete
        repo.delete_problem(problem.id)
        deleted_problem = repo.get_problem(problem.id)
        assert deleted_problem is None
    
    def test_cycle_operations(self, db_session):
        """Test cycle operations"""
        repo = CycleRepository()
        
        # Create a problem first
        problem_repo = ProblemRepository()
        problem = problem_repo.create_problem({
            "title": "Cycle Test Problem",
            "description": "A problem for cycle testing",
            "complexity": "moderate",
            "domain": "Test"
        })
        
        # Create a cycle
        cycle_data = {
            "problem_id": problem.id,
            "objective": "Test cycle objective",
            "priority": 3
        }
        
        cycle = repo.create_cycle(cycle_data)
        assert cycle.id is not None
        assert cycle.objective == "Test cycle objective"
        
        # Get cycles by problem
        cycles = repo.get_cycles_by_problem(problem.id)
        assert len(cycles) == 1
        assert cycles[0].id == cycle.id
```

## End-to-End Testing

### Problem Solving Workflow E2E

```python
# tests/e2e/test_problem_solving_workflow.py
import pytest
import asyncio
from cosmic_council_core import CosmicCouncil, ProblemStatement, ProblemComplexity
from problem_solving_workflow import ProblemSolvingWorkflow

class TestProblemSolvingWorkflowE2E:
    @pytest.mark.asyncio
    async def test_complete_problem_solving_workflow(self):
        """Test complete problem-solving workflow from start to finish"""
        # Initialize components
        council = CosmicCouncil()
        workflow = ProblemSolvingWorkflow()
        
        # Create a complex problem
        problem = ProblemStatement(
            title="E2E Test Problem",
            description="A comprehensive problem for end-to-end testing",
            complexity=ProblemComplexity.COMPLEX,
            domain="E2E Testing",
            stakeholders=["Test Stakeholder 1", "Test Stakeholder 2"],
            constraints={"budget": "$20K", "timeline": "2 months"},
            success_criteria=["Criteria 1", "Criteria 2", "Criteria 3"]
        )
        
        # Solve using Cosmic Council
        council_result = await council.solve_problem(problem)
        
        assert council_result.status == "completed"
        assert council_result.overall_confidence > 0.0
        assert len(council_result.enterprise_results) == 6
        
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
        
        # Compare results
        assert abs(council_result.overall_confidence - workflow_result["overall_confidence"]) < 0.1
    
    @pytest.mark.asyncio
    async def test_ai_enhanced_workflow(self):
        """Test AI-enhanced workflow execution"""
        from ai_enhanced_workflow import AIEnhancedProblemSolvingWorkflow, AIWorkflowConfig
        
        ai_config = AIWorkflowConfig(
            enable_ai_enhancement=True,
            ai_confidence_threshold=0.8,
            max_ai_iterations=3
        )
        
        workflow = AIEnhancedProblemSolvingWorkflow(ai_config=ai_config)
        
        problem_data = {
            "title": "AI Enhanced Test Problem",
            "description": "A problem for AI-enhanced workflow testing",
            "complexity": "complex",
            "domain": "AI Testing"
        }
        
        session = await workflow.start_ai_enhanced_session(problem_data)
        result = await workflow.execute_ai_enhanced_workflow(session.session_id)
        
        assert result["status"] == "completed"
        assert result["ai_enhancement_used"] is True
        assert result["ai_confidence_improvement"] > 0.0
        assert result["overall_confidence"] > 0.0
```

### Web Interface E2E

```python
# tests/e2e/test_web_interface.py
import pytest
from playwright.async_api import async_playwright

class TestWebInterfaceE2E:
    @pytest.mark.asyncio
    async def test_complete_web_workflow(self):
        """Test complete web interface workflow"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate to the web interface
            await page.goto("http://localhost:8001")
            
            # Wait for page to load
            await page.wait_for_selector(".main-header")
            
            # Test navigation
            await page.click("text=Problems")
            await page.wait_for_selector(".problems-page")
            
            # Create a new problem
            await page.click("text=Create New Problem")
            await page.wait_for_selector(".problem-form")
            
            # Fill in problem details
            await page.fill("input[name='title']", "Web E2E Test Problem")
            await page.fill("textarea[name='description']", "A problem for web E2E testing")
            await page.select_option("select[name='complexity']", "moderate")
            await page.fill("input[name='domain']", "Web Testing")
            
            # Submit the form
            await page.click("button[type='submit']")
            
            # Wait for problem creation
            await page.wait_for_selector(".problem-created")
            
            # Navigate to cycles
            await page.click("text=Cycles")
            await page.wait_for_selector(".cycles-page")
            
            # Create a cycle
            await page.click("text=Create New Cycle")
            await page.wait_for_selector(".cycle-form")
            
            await page.fill("input[name='objective']", "Web E2E Test Cycle")
            await page.select_option("select[name='priority']", "3")
            
            await page.click("button[type='submit']")
            
            # Wait for cycle creation
            await page.wait_for_selector(".cycle-created")
            
            # Execute the cycle
            await page.click("text=Execute Cycle")
            await page.wait_for_selector(".cycle-executing")
            
            # Wait for completion
            await page.wait_for_selector(".cycle-completed", timeout=60000)
            
            # Check results
            results = await page.query_selector(".cycle-results")
            assert results is not None
            
            await browser.close()
```

## Performance Testing

### Load Testing

```python
# tests/performance/test_load.py
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from cosmic_council_core import CosmicCouncil, ProblemStatement, ProblemComplexity

class TestLoadPerformance:
    @pytest.mark.asyncio
    async def test_concurrent_problem_solving(self):
        """Test concurrent problem solving performance"""
        council = CosmicCouncil()
        
        # Create multiple problems
        problems = []
        for i in range(10):
            problem = ProblemStatement(
                title=f"Load Test Problem {i}",
                description=f"Problem {i} for load testing",
                complexity=ProblemComplexity.MODERATE,
                domain="Load Testing"
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
        assert total_time < 60  # Should complete within 60 seconds
        assert len(results) == 10  # All problems solved
        
        print(f"Solved {len(problems)} problems in {total_time:.2f} seconds")
        print(f"Average time per problem: {total_time/len(problems):.2f} seconds")
    
    @pytest.mark.asyncio
    async def test_high_volume_problem_solving(self):
        """Test high volume problem solving"""
        council = CosmicCouncil()
        
        # Create many simple problems
        problems = []
        for i in range(100):
            problem = ProblemStatement(
                title=f"Volume Test Problem {i}",
                description=f"Problem {i} for volume testing",
                complexity=ProblemComplexity.SIMPLE,
                domain="Volume Testing"
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
        
        print(f"Solved {len(problems)} problems in {total_time:.2f} seconds")
        print(f"Throughput: {len(problems)/total_time:.2f} problems/second")
```

### Stress Testing

```python
# tests/performance/test_stress.py
import pytest
import asyncio
import time
from cosmic_council_core import CosmicCouncil, ProblemStatement, ProblemComplexity

class TestStressPerformance:
    @pytest.mark.asyncio
    async def test_stress_problem_solving(self):
        """Test system under stress conditions"""
        council = CosmicCouncil()
        
        # Create complex problems to stress the system
        problems = []
        for i in range(50):
            problem = ProblemStatement(
                title=f"Stress Test Problem {i}",
                description=f"Complex problem {i} for stress testing with multiple stakeholders and constraints",
                complexity=ProblemComplexity.COMPLEX,
                domain="Stress Testing",
                stakeholders=[f"Stakeholder {j}" for j in range(5)],
                constraints={"budget": f"${i*1000}K", "timeline": f"{i} months"},
                success_criteria=[f"Criteria {j}" for j in range(3)]
            )
            problems.append(problem)
        
        # Solve all problems concurrently to stress the system
        start_time = time.time()
        
        tasks = [council.solve_problem(problem) for problem in problems]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Count successful results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        # Performance assertions
        assert len(successful_results) >= 45  # At least 90% success rate
        assert len(failed_results) <= 5  # At most 10% failure rate
        assert total_time < 300  # Should complete within 5 minutes
        
        print(f"Stress test completed:")
        print(f"  Total problems: {len(problems)}")
        print(f"  Successful: {len(successful_results)}")
        print(f"  Failed: {len(failed_results)}")
        print(f"  Total time: {total_time:.2f} seconds")
        print(f"  Success rate: {len(successful_results)/len(problems)*100:.1f}%")
```

## Security Testing

### Authentication and Authorization

```python
# tests/security/test_authentication.py
import pytest
from fastapi.testclient import TestClient
from cosmic_council_api import app

class TestAuthentication:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_unauthenticated_access(self, client):
        """Test that unauthenticated access is denied"""
        response = client.get("/api/v1/problems")
        assert response.status_code == 401
    
    def test_invalid_api_key(self, client):
        """Test that invalid API key is rejected"""
        headers = {"Authorization": "Bearer invalid-key"}
        response = client.get("/api/v1/problems", headers=headers)
        assert response.status_code == 401
    
    def test_valid_api_key(self, client):
        """Test that valid API key is accepted"""
        headers = {"Authorization": "Bearer valid-api-key"}
        response = client.get("/api/v1/problems", headers=headers)
        assert response.status_code == 200
    
    def test_rate_limiting(self, client):
        """Test rate limiting functionality"""
        headers = {"Authorization": "Bearer valid-api-key"}
        
        # Make many requests quickly
        for i in range(1001):  # Exceed rate limit
            response = client.get("/api/v1/problems", headers=headers)
            if response.status_code == 429:
                break
        
        assert response.status_code == 429
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
```

### Input Validation

```python
# tests/security/test_input_validation.py
import pytest
from fastapi.testclient import TestClient
from cosmic_council_api import app

class TestInputValidation:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection"""
        headers = {"Authorization": "Bearer valid-api-key"}
        
        malicious_input = "'; DROP TABLE problems; --"
        
        response = client.get(
            f"/api/v1/problems?title={malicious_input}",
            headers=headers
        )
        
        # Should not cause an error
        assert response.status_code in [200, 400]
        assert "error" not in response.text.lower()
    
    def test_xss_protection(self, client):
        """Test protection against XSS attacks"""
        headers = {"Authorization": "Bearer valid-api-key"}
        
        xss_payload = "<script>alert('XSS')</script>"
        
        problem_data = {
            "title": xss_payload,
            "description": "Test description",
            "complexity": "simple",
            "domain": "Test"
        }
        
        response = client.post("/api/v1/problems", json=problem_data, headers=headers)
        
        # Should sanitize the input
        if response.status_code == 201:
            data = response.json()
            assert "<script>" not in data["title"]
    
    def test_input_size_limits(self, client):
        """Test input size limits"""
        headers = {"Authorization": "Bearer valid-api-key"}
        
        # Create a very large description
        large_description = "x" * 10000
        
        problem_data = {
            "title": "Test Problem",
            "description": large_description,
            "complexity": "simple",
            "domain": "Test"
        }
        
        response = client.post("/api/v1/problems", json=problem_data, headers=headers)
        
        # Should reject oversized input
        assert response.status_code == 400
```

## Test Configuration

### pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    security: Security tests
    slow: Slow running tests
```

### conftest.py

```python
# tests/conftest.py
import pytest
import asyncio
from typing import AsyncGenerator
from database_connection import get_db_session
from cosmic_council_core import CosmicCouncil

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def cosmic_council() -> AsyncGenerator[CosmicCouncil, None]:
    """Provide a Cosmic Council instance for testing."""
    council = CosmicCouncil()
    yield council

@pytest.fixture
def db_session():
    """Provide a database session for testing."""
    with get_db_session() as session:
        yield session

@pytest.fixture
def sample_problem():
    """Provide a sample problem for testing."""
    return {
        "title": "Sample Test Problem",
        "description": "A sample problem for testing",
        "complexity": "moderate",
        "domain": "Testing",
        "stakeholders": ["Test Stakeholder"],
        "constraints": {"budget": "$5K"},
        "success_criteria": ["Test criteria"]
    }

@pytest.fixture
def sample_cycle():
    """Provide a sample cycle for testing."""
    return {
        "objective": "Sample cycle objective",
        "priority": 3,
        "ai_enhanced": False
    }
```

## Running Tests

### Command Line

```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit
pytest -m integration
pytest -m e2e
pytest -m performance
pytest -m security

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_cosmic_council_core.py

# Run specific test
pytest tests/unit/test_cosmic_council_core.py::TestCosmicCouncil::test_initialization

# Run with verbose output
pytest -v

# Run in parallel
pytest -n auto
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: cosmic_council_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Test Data Management

### Fixtures

```python
# tests/fixtures/sample_problems.py
import pytest
from cosmic_council_core import ProblemStatement, ProblemComplexity

@pytest.fixture
def simple_problem():
    return ProblemStatement(
        title="Simple Test Problem",
        description="A simple problem for testing",
        complexity=ProblemComplexity.SIMPLE,
        domain="Testing"
    )

@pytest.fixture
def complex_problem():
    return ProblemStatement(
        title="Complex Test Problem",
        description="A complex problem with multiple facets",
        complexity=ProblemComplexity.COMPLEX,
        domain="Testing",
        stakeholders=["Stakeholder 1", "Stakeholder 2"],
        constraints={"budget": "$10K", "timeline": "1 month"},
        success_criteria=["Criteria 1", "Criteria 2"]
    )

@pytest.fixture
def business_problem():
    return ProblemStatement(
        title="Business Optimization Problem",
        description="Optimize business processes for efficiency",
        complexity=ProblemComplexity.MODERATE,
        domain="Business",
        stakeholders=["Management", "Employees", "Customers"],
        constraints={"budget": "$50K", "timeline": "3 months"},
        success_criteria=["Efficiency > 90%", "Cost reduction > 20%"]
    )
```

## Best Practices

### 1. Test Organization
- Group tests by functionality
- Use descriptive test names
- Keep tests focused and atomic
- Use fixtures for common setup

### 2. Test Data
- Use realistic test data
- Create reusable fixtures
- Clean up test data after tests
- Use factories for complex objects

### 3. Assertions
- Use specific assertions
- Test both positive and negative cases
- Verify side effects
- Check error conditions

### 4. Performance
- Run tests in parallel when possible
- Use appropriate test markers
- Mock external dependencies
- Optimize test execution time

### 5. Maintenance
- Keep tests up to date
- Refactor tests with code changes
- Remove obsolete tests
- Document test requirements

## Support

For testing support:

- **Documentation**: [docs.cosmic-council.org/testing](https://docs.cosmic-council.org/testing)
- **Issue Tracker**: [GitHub Issues](https://github.com/cosmic-council/framework/issues)
- **Email Support**: testing-support@cosmic-council.org
- **Community Forum**: [community.cosmic-council.org](https://community.cosmic-council.org)
