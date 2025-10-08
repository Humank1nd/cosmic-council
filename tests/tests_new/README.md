# Cosmic Council Framework Testing Suite

## Overview

This directory contains the comprehensive testing suite for the Cosmic Council Framework. The testing suite is designed to ensure the reliability, performance, and security of all framework components.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and shared fixtures
├── README.md                   # This file
├── unit/                       # Unit tests
│   ├── test_cosmic_council_core.py
│   ├── test_enhanced_enterprise_agents.py
│   ├── test_problem_solving_workflow.py
│   ├── test_ai_integration.py
│   ├── test_database_models.py
│   ├── test_analytics_dashboard.py
│   ├── test_policy_engine.py
│   └── test_feedback_system.py
├── integration/                # Integration tests
│   ├── test_api_endpoints.py
│   ├── test_database_operations.py
│   ├── test_108_cycle_system.py
│   ├── test_policy_engine.py
│   └── test_workflow_integration.py
├── e2e/                        # End-to-end tests
│   ├── test_complete_workflow.py
│   ├── test_web_interface.py
│   └── test_analytics_dashboard.py
├── performance/                # Performance tests
│   ├── test_load_performance.py
│   ├── test_stress_performance.py
│   └── test_volume_performance.py
├── security/                   # Security tests
│   ├── test_authentication.py
│   ├── test_authorization.py
│   ├── test_input_validation.py
│   └── test_data_protection.py
└── fixtures/                   # Test fixtures and data
    ├── sample_problems.py
    ├── sample_cycles.py
    ├── sample_solutions.py
    └── mock_data.py
```

## Test Categories

### Unit Tests
- **Purpose**: Test individual components in isolation
- **Coverage**: All core classes, methods, and functions
- **Location**: `tests/unit/`
- **Markers**: `@pytest.mark.unit`

### Integration Tests
- **Purpose**: Test component interactions and API endpoints
- **Coverage**: Database operations, API endpoints, component integration
- **Location**: `tests/integration/`
- **Markers**: `@pytest.mark.integration`

### End-to-End Tests
- **Purpose**: Test complete user workflows and scenarios
- **Coverage**: Full problem-solving workflows, web interface, analytics
- **Location**: `tests/e2e/`
- **Markers**: `@pytest.mark.e2e`

### Performance Tests
- **Purpose**: Test system performance under load
- **Coverage**: Load testing, stress testing, volume testing
- **Location**: `tests/performance/`
- **Markers**: `@pytest.mark.performance`

### Security Tests
- **Purpose**: Test security vulnerabilities and compliance
- **Coverage**: Authentication, authorization, input validation
- **Location**: `tests/security/`
- **Markers**: `@pytest.mark.security`

## Running Tests

### Quick Start

```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type e2e
python run_tests.py --type performance
python run_tests.py --type security

# Run with coverage
python run_tests.py --coverage

# Run in parallel
python run_tests.py --parallel

# Generate comprehensive report
python run_tests.py --report
```

### Using pytest directly

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

# Run in parallel
pytest -n auto

# Run specific test file
pytest tests/unit/test_cosmic_council_core.py

# Run specific test
pytest tests/unit/test_cosmic_council_core.py::TestCosmicCouncil::test_initialization
```

### Test Configuration

The test suite uses `pytest.ini` for configuration:

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

## Test Fixtures

### Core Fixtures

- `cosmic_council`: Cosmic Council instance
- `enhanced_red_owl_agent`: Enhanced Red Owl agent
- `enhanced_orange_orangutan_agent`: Enhanced Orange Orangutan agent
- `problem_solving_workflow`: Problem-solving workflow
- `ai_llm_integration`: AI/LLM integration
- `analytics_dashboard`: Analytics dashboard
- `policy_engine`: Policy engine
- `feedback_system`: Feedback system

### Data Fixtures

- `sample_problem`: Sample problem statement
- `sample_complex_problem`: Complex problem statement
- `sample_simple_problem`: Simple problem statement
- `sample_systemic_problem`: Systemic problem statement
- `sample_problem_data`: Sample problem data
- `sample_cycle_data`: Sample cycle data
- `sample_solution_data`: Sample solution data

### Mock Fixtures

- `mock_llm_response`: Mock LLM response
- `mock_enterprise_result`: Mock enterprise result
- `mock_workflow_result`: Mock workflow result
- `mock_analytics_data`: Mock analytics data
- `mock_policy_rule`: Mock policy rule
- `mock_feedback_cycle`: Mock feedback cycle
- `mock_database_session`: Mock database session
- `mock_redis_client`: Mock Redis client
- `mock_http_client`: Mock HTTP client
- `mock_websocket`: Mock WebSocket
- `mock_file_system`: Mock file system
- `mock_logger`: Mock logger
- `mock_config`: Mock configuration
- `mock_environment`: Mock environment

## Test Data

### Sample Problems

The test suite includes various sample problems for testing:

- **Simple Problems**: Basic problems for unit testing
- **Moderate Problems**: Medium complexity problems for integration testing
- **Complex Problems**: High complexity problems for performance testing
- **Systemic Problems**: System-wide problems for end-to-end testing

### Mock Data

Mock data is provided for:
- LLM responses
- Enterprise results
- Workflow results
- Analytics data
- Policy rules
- Feedback cycles

## Test Coverage

### Coverage Goals

- **Unit Tests**: 95%+ coverage
- **Integration Tests**: 90%+ coverage
- **End-to-End Tests**: 80%+ coverage
- **Overall Coverage**: 85%+ coverage

### Coverage Reports

Coverage reports are generated in multiple formats:
- HTML: `htmlcov/index.html`
- Terminal: Console output
- XML: `coverage.xml`

## Performance Benchmarks

### Load Testing

- **Concurrent Problems**: 20+ problems simultaneously
- **High Volume**: 100+ problems in batches
- **Throughput**: 1+ problems per second
- **Response Time**: <10 seconds average

### Stress Testing

- **Memory Usage**: <500MB increase
- **CPU Usage**: <80% under load
- **Session Management**: 25+ concurrent sessions
- **Error Rate**: <1% under stress

## Security Testing

### Authentication & Authorization

- API key validation
- Role-based access control
- Session management
- Token expiration

### Input Validation

- SQL injection protection
- XSS protection
- Input size limits
- Data type validation

### Data Protection

- Encryption at rest
- Secure transmission
- Data anonymization
- Privacy compliance

## Continuous Integration

### GitHub Actions

The test suite is integrated with GitHub Actions for:
- Automated testing on pull requests
- Coverage reporting
- Performance benchmarking
- Security scanning

### Test Pipeline

1. **Dependency Check**: Verify all dependencies are installed
2. **Linting**: Run code quality checks
3. **Type Checking**: Run type validation
4. **Unit Tests**: Run unit tests with coverage
5. **Integration Tests**: Run integration tests
6. **End-to-End Tests**: Run end-to-end tests
7. **Performance Tests**: Run performance benchmarks
8. **Security Tests**: Run security scans
9. **Report Generation**: Generate comprehensive reports

## Best Practices

### Writing Tests

1. **Test Naming**: Use descriptive test names
2. **Test Isolation**: Tests should be independent
3. **Mocking**: Mock external dependencies
4. **Assertions**: Use specific assertions
5. **Coverage**: Aim for high test coverage

### Test Organization

1. **Group Related Tests**: Use test classes
2. **Use Fixtures**: Share common setup
3. **Mark Tests**: Use appropriate markers
4. **Document Tests**: Add docstrings
5. **Keep Tests Simple**: One concept per test

### Performance Testing

1. **Baseline Metrics**: Establish performance baselines
2. **Load Testing**: Test under expected load
3. **Stress Testing**: Test beyond expected load
4. **Memory Testing**: Monitor memory usage
5. **Response Time**: Track response times

## Troubleshooting

### Common Issues

1. **Import Errors**: Check Python path and dependencies
2. **Async Tests**: Use `@pytest.mark.asyncio`
3. **Mock Issues**: Verify mock setup and teardown
4. **Database Tests**: Ensure test database is available
5. **Performance Tests**: Run on adequate hardware

### Debug Mode

Run tests in debug mode for detailed output:

```bash
pytest --verbose --tb=long --capture=no
```

### Test Isolation

Ensure tests don't interfere with each other:

```bash
pytest --forked
```

## Contributing

### Adding New Tests

1. **Follow Naming Convention**: Use `test_` prefix
2. **Use Appropriate Markers**: Mark tests with correct category
3. **Add Fixtures**: Use existing fixtures or create new ones
4. **Update Documentation**: Update this README if needed
5. **Run Tests**: Ensure all tests pass

### Test Review

Before submitting tests:
1. Run the full test suite
2. Check coverage reports
3. Verify performance benchmarks
4. Review security test results
5. Update documentation

## Support

For testing support:
- **Documentation**: Check this README and test docstrings
- **Issues**: Report test failures or issues
- **Community**: Ask questions in the community forum
- **Email**: Contact testing-support@cosmic-council.org
