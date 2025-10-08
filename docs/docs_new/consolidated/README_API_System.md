# Cosmic Council API System

## Overview

The Cosmic Council API System provides comprehensive REST API capabilities for all system operations. Built with FastAPI and featuring async support, comprehensive error handling, and full integration with the Cosmic Council framework.

## Architecture

### Core Components

#### 1. API Server (`cosmic_council_api.py`)
- **FastAPI Application**: Modern, fast web framework for building APIs
- **Async Support**: Full async/await support for high performance
- **Middleware**: CORS, authentication, and security middleware
- **Background Tasks**: Async task processing for long-running operations
- **Error Handling**: Comprehensive error handling and validation
- **Documentation**: Auto-generated OpenAPI/Swagger documentation

#### 2. API Client (`api_client.py`)
- **Async Client**: High-performance async HTTP client
- **Type Safety**: Full type hints and validation
- **Session Management**: Automatic session and connection management
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Context Manager**: Resource cleanup with async context managers
- **Authentication**: Built-in authentication support

#### 3. Demo System (`demo_api_system.py`)
- **Comprehensive Testing**: Full system demonstration and testing
- **Integration Examples**: Real-world usage examples
- **Performance Testing**: API performance and load testing
- **Error Scenarios**: Error handling demonstration
- **Documentation**: Live documentation and examples

## API Endpoints

### Health & Status

#### GET /
Root endpoint with API information
```json
{
  "success": true,
  "message": "Cosmic Council API is running",
  "data": {
    "version": "1.0.0",
    "description": "REST API for the Cosmic Council problem-solving framework",
    "endpoints": {
      "problems": "/api/v1/problems",
      "cycles": "/api/v1/cycles",
      "solutions": "/api/v1/solutions",
      "workflows": "/api/v1/workflows",
      "analytics": "/api/v1/analytics",
      "enterprises": "/api/v1/enterprises"
    }
  }
}
```

#### GET /health
Health check endpoint
```json
{
  "success": true,
  "message": "Health check completed",
  "data": {
    "database": true,
    "workflow_engine": true,
    "ai_integration": true,
    "overall_status": "healthy"
  }
}
```

### Problem Management

#### POST /api/v1/problems
Create a new problem
```json
{
  "title": "AI Healthcare Transformation",
  "description": "Transform healthcare system using AI and machine learning",
  "domain": "Healthcare & AI",
  "complexity": "complex",
  "priority": "high",
  "stakeholders": ["Healthcare Providers", "Patients", "IT Department"],
  "constraints": {
    "budget": 50000000,
    "timeline": "2 years",
    "compliance": "HIPAA"
  },
  "success_criteria": [
    "Improved patient outcomes",
    "Reduced operational costs",
    "Enhanced system efficiency"
  ],
  "due_date": "2025-12-31T23:59:59Z"
}
```

#### GET /api/v1/problems
Get problems with filtering
**Query Parameters:**
- `domain` (optional): Filter by domain
- `complexity` (optional): Filter by complexity
- `status` (optional): Filter by status
- `limit` (default: 100): Number of results
- `offset` (default: 0): Pagination offset

#### GET /api/v1/problems/{problem_id}
Get a specific problem by ID

#### PUT /api/v1/problems/{problem_id}
Update a problem
```json
{
  "title": "Updated Problem Title",
  "status": "in_progress",
  "priority": "critical"
}
```

### Cycle Management

#### POST /api/v1/cycles
Create a new cycle
```json
{
  "problem_id": "123e4567-e89b-12d3-a456-426614174000",
  "cycle_number": 1,
  "max_iterations": 3
}
```

#### GET /api/v1/cycles/{cycle_id}
Get a specific cycle by ID

#### POST /api/v1/cycles/{cycle_id}/execute
Execute a cycle (start problem-solving process)
```json
{
  "success": true,
  "message": "Cycle execution started",
  "data": {
    "cycle_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "in_progress",
    "message": "Cycle execution is running in the background"
  }
}
```

### Solution Management

#### POST /api/v1/solutions
Create a new solution
```json
{
  "problem_id": "123e4567-e89b-12d3-a456-426614174000",
  "cycle_id": "123e4567-e89b-12d3-a456-426614174001",
  "title": "AI Healthcare Platform",
  "description": "Comprehensive AI-powered healthcare transformation solution",
  "approach": "Multi-phase implementation with AI integration",
  "confidence_score": 0.85,
  "feasibility_score": 0.90,
  "impact_score": 0.80,
  "estimated_cost": 50000000.0,
  "estimated_duration": 730,
  "risk_level": "medium"
}
```

#### GET /api/v1/solutions
Get solutions with filtering
**Query Parameters:**
- `problem_id` (optional): Filter by problem ID
- `cycle_id` (optional): Filter by cycle ID
- `limit` (default: 100): Number of results
- `offset` (default: 0): Pagination offset

### Analytics

#### GET /api/v1/analytics/problems
Get problem analytics and statistics
```json
{
  "success": true,
  "message": "Problem analytics retrieved successfully",
  "data": {
    "total_problems": 150,
    "by_complexity": {
      "simple": 25,
      "moderate": 60,
      "complex": 50,
      "systemic": 15
    },
    "by_domain": {
      "Healthcare & AI": 45,
      "Business & Technology": 35,
      "Education": 25,
      "Environment": 20,
      "Social Issues": 25
    },
    "by_status": {
      "active": 80,
      "in_progress": 40,
      "completed": 25,
      "archived": 5
    },
    "recent_problems": 12
  }
}
```

#### GET /api/v1/analytics/cycles
Get cycle analytics and statistics
```json
{
  "success": true,
  "message": "Cycle analytics retrieved successfully",
  "data": {
    "total_cycles": 300,
    "by_status": {
      "pending": 50,
      "in_progress": 80,
      "completed": 150,
      "failed": 20
    },
    "average_duration": 45.5,
    "average_confidence": 0.82
  }
}
```

#### GET /api/v1/analytics/solutions
Get solution analytics and statistics
```json
{
  "success": true,
  "message": "Solution analytics retrieved successfully",
  "data": {
    "total_solutions": 200,
    "by_status": {
      "draft": 30,
      "reviewed": 50,
      "approved": 80,
      "implemented": 35,
      "archived": 5
    },
    "average_confidence": 0.78,
    "average_feasibility": 0.75
  }
}
```

### Enterprise Management

#### GET /api/v1/enterprises
Get all enterprises
```json
{
  "success": true,
  "message": "Retrieved 6 enterprises",
  "data": {
    "enterprises": [
      {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Red Owl",
        "type": "red_owl",
        "description": "Research & Knowledge analysis with specialized frameworks",
        "color": "#FF0000",
        "symbol": "🦉",
        "core_principle": "Deep research and knowledge synthesis",
        "expertise_areas": ["Research", "Analysis", "Knowledge Management"],
        "processing_order": 1,
        "is_active": true
      }
    ]
  }
}
```

## API Client Usage

### Basic Usage

```python
import asyncio
from api_client import CosmicCouncilAPIClient

async def main():
    async with CosmicCouncilAPIClient() as client:
        # Check API health
        health = await client.health_check()
        print(f"API Status: {health['success']}")
        
        # Create a problem
        problem = await client.create_problem(
            title="AI Healthcare Transformation",
            description="Transform healthcare using AI",
            domain="Healthcare & AI",
            complexity="complex",
            priority="high"
        )
        
        problem_id = problem['data']['problem_id']
        print(f"Created problem: {problem_id}")
        
        # Create and execute a cycle
        cycle = await client.create_cycle(
            problem_id=problem_id,
            cycle_number=1
        )
        
        cycle_id = cycle['data']['cycle_id']
        execution = await client.execute_cycle(cycle_id)
        print(f"Cycle execution: {execution['data']['status']}")

asyncio.run(main())
```

### Error Handling

```python
from api_client import CosmicCouncilAPIClient, APIException

async def main():
    async with CosmicCouncilAPIClient() as client:
        try:
            # This will raise an APIException for invalid ID
            result = await client.get_problem("invalid-id")
        except APIException as e:
            print(f"API Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
```

### Advanced Usage

```python
async def comprehensive_workflow():
    async with CosmicCouncilAPIClient() as client:
        # Create problem
        problem = await client.create_problem(
            title="Digital Transformation Initiative",
            description="Transform business operations using digital technologies",
            domain="Business & Technology",
            complexity="complex",
            priority="high",
            stakeholders=["Management", "IT Department", "Employees"],
            constraints={"budget": 1000000, "timeline": "6 months"},
            success_criteria=["Improved efficiency", "Cost reduction", "Better user experience"]
        )
        
        problem_id = problem['data']['problem_id']
        
        # Create cycle
        cycle = await client.create_cycle(
            problem_id=problem_id,
            cycle_number=1,
            max_iterations=3
        )
        
        cycle_id = cycle['data']['cycle_id']
        
        # Execute cycle
        execution = await client.execute_cycle(cycle_id)
        
        # Wait for completion (in real implementation, you'd poll or use webhooks)
        await asyncio.sleep(5)
        
        # Create solution
        solution = await client.create_solution(
            problem_id=problem_id,
            cycle_id=cycle_id,
            title="Digital Transformation Platform",
            description="Comprehensive digital transformation solution",
            approach="Phased implementation with change management",
            confidence_score=0.85,
            feasibility_score=0.90,
            impact_score=0.80,
            estimated_cost=800000.0,
            estimated_duration=180,
            risk_level="medium"
        )
        
        # Get analytics
        problem_analytics = await client.get_problem_analytics()
        cycle_analytics = await client.get_cycle_analytics()
        solution_analytics = await client.get_solution_analytics()
        
        print("Workflow completed successfully!")
        print(f"Problem: {problem['data']['title']}")
        print(f"Solution: {solution['data']['title']}")
        print(f"Total Problems: {problem_analytics['data']['total_problems']}")
```

## Request/Response Models

### ProblemCreateRequest
```python
class ProblemCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    domain: str = Field(..., min_length=1, max_length=200)
    complexity: str = Field(..., description="simple|moderate|complex|systemic")
    priority: str = Field(default="medium", description="low|medium|high|critical")
    stakeholders: List[str] = Field(default=[])
    constraints: Dict[str, Any] = Field(default={})
    success_criteria: List[str] = Field(default=[])
    due_date: Optional[datetime] = Field(default=None)
```

### CycleCreateRequest
```python
class CycleCreateRequest(BaseModel):
    problem_id: str = Field(..., description="Problem ID")
    cycle_number: int = Field(..., ge=1, description="Cycle number")
    max_iterations: int = Field(default=3, ge=1, le=10)
```

### SolutionCreateRequest
```python
class SolutionCreateRequest(BaseModel):
    problem_id: str = Field(..., description="Problem ID")
    cycle_id: str = Field(..., description="Cycle ID")
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    approach: Optional[str] = Field(None)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    feasibility_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    impact_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    estimated_cost: Optional[float] = Field(None, ge=0.0)
    estimated_duration: Optional[int] = Field(None, ge=1)
    risk_level: Optional[str] = Field(None, description="low|medium|high|critical")
```

### ResponseModel
```python
class ResponseModel(BaseModel):
    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

## Error Handling

### HTTP Status Codes
- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Access denied
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

### Error Response Format
```json
{
  "success": false,
  "message": "Error description",
  "data": {
    "status_code": 400,
    "error": "Detailed error information"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Custom Exceptions
```python
class APIException(Exception):
    """Exception raised for API errors"""
    pass
```

## Authentication

### Bearer Token Authentication
```python
# Client with authentication
async with CosmicCouncilAPIClient(
    base_url="https://api.cosmiccouncil.com",
    api_key="your-api-key"
) as client:
    # Authenticated requests
    result = await client.get_problems()
```

### JWT Token Support
```python
# JWT token authentication
headers = {"Authorization": "Bearer your-jwt-token"}
```

## Performance Features

### Async Support
- **Non-blocking Operations**: All API calls are async
- **Concurrent Requests**: Multiple requests can be made simultaneously
- **Connection Pooling**: Efficient HTTP connection management
- **Background Tasks**: Long-running operations run in background

### Caching
```python
# Client with caching
async with CosmicCouncilAPIClient() as client:
    # First request - hits API
    enterprises = await client.get_enterprises()
    
    # Second request - uses cache (if implemented)
    enterprises = await client.get_enterprises()
```

### Rate Limiting
```python
# Rate limiting support
import asyncio

async def rate_limited_requests():
    async with CosmicCouncilAPIClient() as client:
        for i in range(10):
            result = await client.get_problems()
            await asyncio.sleep(0.1)  # Rate limiting
```

## Security Features

### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cosmiccouncil.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Input Validation
- **Pydantic Models**: Automatic request validation
- **Type Checking**: Runtime type validation
- **Sanitization**: Input sanitization and cleaning
- **SQL Injection Prevention**: Parameterized queries

### Audit Logging
```python
# All operations are automatically logged
AuditLogRepository.log_action(
    action="create",
    resource_type="problem",
    resource_id=problem.id,
    user_id=current_user,
    new_values=request.dict()
)
```

## Monitoring and Analytics

### Health Monitoring
```python
# Health check endpoint
health = await client.health_check()
if not health['success']:
    # Handle unhealthy state
    pass
```

### Performance Metrics
```python
# System metrics collection
SystemMetricsRepository.record_metric(
    metric_name="api_request_duration",
    metric_type="histogram",
    metric_value=duration_ms,
    tags=["endpoint", "method"]
)
```

### Request Logging
```python
# Request/response logging
logger.info(f"API Request: {method} {path} - {status_code} - {duration}ms")
```

## Deployment

### Development Server
```bash
# Run development server
python cosmic_council_api.py
```

### Production Deployment
```bash
# Using uvicorn
uvicorn cosmic_council_api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "cosmic_council_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration
```bash
# Environment variables
export DATABASE_URL="postgresql://user:pass@localhost/cosmic_council"
export API_KEY="your-secret-api-key"
export CORS_ORIGINS="https://cosmiccouncil.com,https://app.cosmiccouncil.com"
export LOG_LEVEL="info"
```

## Testing

### Unit Tests
```python
import pytest
from api_client import CosmicCouncilAPIClient

@pytest.mark.asyncio
async def test_create_problem():
    async with CosmicCouncilAPIClient() as client:
        result = await client.create_problem(
            title="Test Problem",
            description="Test Description",
            domain="Testing",
            complexity="simple"
        )
        assert result['success'] == True
        assert 'problem_id' in result['data']
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_complete_workflow():
    async with CosmicCouncilAPIClient() as client:
        # Create problem
        problem = await client.create_problem(...)
        
        # Create cycle
        cycle = await client.create_cycle(...)
        
        # Execute cycle
        execution = await client.execute_cycle(...)
        
        # Verify results
        assert execution['success'] == True
```

### Load Testing
```python
import asyncio
import aiohttp

async def load_test():
    async with CosmicCouncilAPIClient() as client:
        tasks = []
        for i in range(100):
            task = client.get_problems()
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        print(f"Completed {len(results)} requests")
```

## Documentation

### OpenAPI/Swagger
- **Auto-generated Documentation**: Available at `/docs`
- **Interactive API Explorer**: Test endpoints directly
- **Schema Validation**: Request/response schema validation
- **Code Generation**: Generate client code from OpenAPI spec

### API Documentation
```python
# Custom documentation
app = FastAPI(
    title="Cosmic Council API",
    description="REST API for the Cosmic Council problem-solving framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

## Conclusion

The Cosmic Council API System provides a comprehensive, production-ready REST API for all system operations. With features including:

- **Complete REST API**: 20+ endpoints covering all system functionality
- **Async Support**: High-performance async operations
- **Type Safety**: Full type hints and validation
- **Error Handling**: Comprehensive error handling and validation
- **Security**: Authentication, authorization, and input validation
- **Performance**: Connection pooling, caching, and optimization
- **Monitoring**: Health checks, metrics, and audit logging
- **Documentation**: Auto-generated OpenAPI documentation

The system is ready for production use and provides a solid foundation for integrating the Cosmic Council framework with external systems and applications.

Key benefits include:
- **Scalability**: Designed to handle high-volume API requests
- **Reliability**: Comprehensive error handling and validation
- **Security**: Built-in security features and audit logging
- **Performance**: Optimized for high-performance operations
- **Maintainability**: Clean architecture with separation of concerns
- **Documentation**: Comprehensive documentation and examples

The API system successfully integrates with all other Cosmic Council components and provides the interface layer for external system integration.
