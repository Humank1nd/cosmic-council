# Cosmic Council Framework API Documentation

## Overview

The Cosmic Council Framework provides a comprehensive REST API for programmatic access to all framework capabilities. This API enables integration with external systems, custom applications, and automated workflows.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

The API uses API key authentication. Include your API key in the request headers:

```http
Authorization: Bearer your-api-key-here
```

## Rate Limiting

- **Standard Rate Limit**: 1000 requests per hour
- **Premium Rate Limit**: 10000 requests per hour
- **Rate Limit Headers**: 
  - `X-RateLimit-Limit`: Maximum requests per hour
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when rate limit resets

## Error Handling

All API responses follow a consistent error format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional error details"
    }
  }
}
```

### Common Error Codes

- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

## Core Endpoints

### Problems

#### Create Problem

```http
POST /problems
```

**Request Body:**
```json
{
  "title": "Optimize Customer Support",
  "description": "Improve customer satisfaction and reduce response times",
  "complexity": "complex",
  "domain": "Customer Service",
  "stakeholders": ["Support Team", "Customers", "Management"],
  "constraints": {
    "budget": "$50K",
    "timeline": "3 months"
  },
  "success_criteria": [
    "Response time < 2 hours",
    "Satisfaction > 90%"
  ]
}
```

**Response:**
```json
{
  "problem_id": "uuid-string",
  "title": "Optimize Customer Support",
  "status": "pending",
  "created_at": "2023-01-01T00:00:00Z",
  "complexity": "complex",
  "domain": "Customer Service"
}
```

#### Get Problem

```http
GET /problems/{problem_id}
```

**Response:**
```json
{
  "problem_id": "uuid-string",
  "title": "Optimize Customer Support",
  "description": "Improve customer satisfaction and reduce response times",
  "complexity": "complex",
  "domain": "Customer Service",
  "status": "in_progress",
  "stakeholders": ["Support Team", "Customers", "Management"],
  "constraints": {
    "budget": "$50K",
    "timeline": "3 months"
  },
  "success_criteria": [
    "Response time < 2 hours",
    "Satisfaction > 90%"
  ],
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T01:00:00Z"
}
```

#### List Problems

```http
GET /problems?limit=20&offset=0&status=in_progress&complexity=complex
```

**Query Parameters:**
- `limit` (optional): Number of results to return (default: 20, max: 100)
- `offset` (optional): Number of results to skip (default: 0)
- `status` (optional): Filter by status (pending, in_progress, completed, failed)
- `complexity` (optional): Filter by complexity (simple, moderate, complex, systemic)
- `domain` (optional): Filter by domain

**Response:**
```json
{
  "problems": [
    {
      "problem_id": "uuid-string",
      "title": "Optimize Customer Support",
      "status": "in_progress",
      "complexity": "complex",
      "domain": "Customer Service",
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

### Cycles

#### Create Cycle

```http
POST /cycles
```

**Request Body:**
```json
{
  "problem_id": "uuid-string",
  "objective": "Streamline customer onboarding process",
  "priority": 3,
  "ai_enhanced": true,
  "config": {
    "max_iterations": 3,
    "confidence_threshold": 0.8
  }
}
```

**Response:**
```json
{
  "cycle_id": "uuid-string",
  "problem_id": "uuid-string",
  "objective": "Streamline customer onboarding process",
  "status": "pending",
  "priority": 3,
  "created_at": "2023-01-01T00:00:00Z"
}
```

#### Execute Cycle

```http
POST /cycles/{cycle_id}/execute
```

**Response:**
```json
{
  "cycle_id": "uuid-string",
  "status": "running",
  "started_at": "2023-01-01T00:00:00Z",
  "estimated_completion": "2023-01-01T00:30:00Z"
}
```

#### Get Cycle Status

```http
GET /cycles/{cycle_id}
```

**Response:**
```json
{
  "cycle_id": "uuid-string",
  "problem_id": "uuid-string",
  "objective": "Streamline customer onboarding process",
  "status": "completed",
  "priority": 3,
  "created_at": "2023-01-01T00:00:00Z",
  "started_at": "2023-01-01T00:00:00Z",
  "completed_at": "2023-01-01T00:25:00Z",
  "total_processing_time": 1500.0,
  "overall_confidence": 0.92,
  "enterprise_results": {
    "red_owl": {
      "status": "completed",
      "confidence": 0.89,
      "insights": ["Customer data analysis completed"],
      "recommendations": ["Implement automated data collection"]
    }
  }
}
```

#### List Cycles

```http
GET /cycles?problem_id=uuid-string&status=completed&limit=20
```

**Query Parameters:**
- `problem_id` (optional): Filter by problem ID
- `status` (optional): Filter by status
- `limit` (optional): Number of results to return
- `offset` (optional): Number of results to skip

### Solutions

#### Get Solutions

```http
GET /solutions?cycle_id=uuid-string&limit=20
```

**Response:**
```json
{
  "solutions": [
    {
      "solution_id": "uuid-string",
      "cycle_id": "uuid-string",
      "title": "Automated Customer Onboarding",
      "description": "Implement automated onboarding workflow",
      "status": "implemented",
      "confidence": 0.92,
      "feasibility": 0.88,
      "components": [
        {
          "component_id": "uuid-string",
          "name": "Automated Email Sequence",
          "description": "Send welcome emails automatically",
          "priority": 1,
          "estimated_effort": "2 weeks"
        }
      ],
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

#### Create Solution

```http
POST /solutions
```

**Request Body:**
```json
{
  "cycle_id": "uuid-string",
  "title": "Custom Solution",
  "description": "Manually created solution",
  "components": [
    {
      "name": "Component 1",
      "description": "First component",
      "priority": 1,
      "estimated_effort": "1 week"
    }
  ]
}
```

### Analytics

#### Get Problem Analytics

```http
GET /analytics/problems
```

**Response:**
```json
{
  "total_problems": 150,
  "by_complexity": {
    "simple": 45,
    "moderate": 67,
    "complex": 32,
    "systemic": 6
  },
  "by_domain": {
    "business": 38,
    "technical": 42,
    "personal": 25,
    "global": 45
  },
  "by_status": {
    "pending": 12,
    "in_progress": 6,
    "completed": 125,
    "failed": 7
  },
  "success_rate": 0.947,
  "average_resolution_time": 1800.0
}
```

#### Get Cycle Analytics

```http
GET /analytics/cycles
```

**Response:**
```json
{
  "total_cycles": 108,
  "by_status": {
    "pending": 8,
    "running": 2,
    "completed": 95,
    "failed": 3
  },
  "average_duration": 2400.0,
  "average_confidence": 0.89,
  "enterprise_performance": {
    "red_owl": {
      "cycles_processed": 18,
      "success_rate": 0.96,
      "average_confidence": 0.89
    }
  }
}
```

#### Get Solution Analytics

```http
GET /analytics/solutions
```

**Response:**
```json
{
  "total_solutions": 142,
  "by_status": {
    "pending": 12,
    "implemented": 128,
    "rejected": 2
  },
  "average_confidence": 0.87,
  "average_feasibility": 0.85,
  "implementation_success_rate": 0.901
}
```

### Enterprises

#### Get Enterprise Information

```http
GET /supra_enterprise
```

**Response:**
```json
{
  "enterprises": [
    {
      "enterprise_id": "red_owl",
      "name": "Red Owl",
      "role": "Research & Knowledge Gathering",
      "description": "Gathers information and conducts research",
      "color": "#ef4444",
      "status": "active",
      "capabilities": [
        "Data collection",
        "Analysis",
        "Knowledge synthesis"
      ]
    }
  ]
}
```

#### Get Enterprise Performance

```http
GET /supra_enterprise/{enterprise_id}/performance
```

**Response:**
```json
{
  "enterprise_id": "red_owl",
  "name": "Red Owl",
  "performance_metrics": {
    "cycles_processed": 18,
    "success_rate": 0.96,
    "average_confidence": 0.89,
    "average_processing_time": 2200.0,
    "specialization_score": 0.92,
    "collaboration_score": 0.85
  },
  "recent_activity": [
    {
      "cycle_id": "uuid-string",
      "problem_title": "Customer Support Optimization",
      "status": "completed",
      "confidence": 0.89,
      "completed_at": "2023-01-01T00:00:00Z"
    }
  ]
}
```

## WebSocket API

### Real-Time Updates

Connect to the WebSocket endpoint for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function(event) {
    console.log('Connected to Cosmic Council WebSocket');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received update:', data);
};

ws.onclose = function(event) {
    console.log('WebSocket connection closed');
};
```

### WebSocket Message Types

#### Cycle Status Update

```json
{
  "type": "cycle_status_update",
  "cycle_id": "uuid-string",
  "status": "running",
  "progress": 0.45,
  "current_enterprise": "yellow_honeybee",
  "estimated_completion": "2023-01-01T00:30:00Z"
}
```

#### Enterprise Result

```json
{
  "type": "enterprise_result",
  "cycle_id": "uuid-string",
  "enterprise": "red_owl",
  "status": "completed",
  "confidence": 0.89,
  "insights": ["Research completed"],
  "recommendations": ["Implement findings"]
}
```

#### Cycle Completion

```json
{
  "type": "cycle_completion",
  "cycle_id": "uuid-string",
  "status": "completed",
  "overall_confidence": 0.92,
  "total_processing_time": 1500.0,
  "enterprise_results": {
    "red_owl": {
      "status": "completed",
      "confidence": 0.89
    }
  }
}
```

## SDK Examples

### Python SDK

```python
from cosmic_council_api import CosmicCouncilClient

# Initialize client
client = CosmicCouncilClient(
    base_url="http://localhost:8000/api/v1",
    api_key="your-api-key"
)

# Create a problem
problem = client.create_problem(
    title="Optimize Customer Support",
    description="Improve customer satisfaction and reduce response times",
    complexity="complex",
    domain="Customer Service",
    stakeholders=["Support Team", "Customers", "Management"],
    constraints={"budget": "$50K", "timeline": "3 months"},
    success_criteria=["Response time < 2 hours", "Satisfaction > 90%"]
)

# Create and execute a cycle
cycle = client.create_cycle(
    problem_id=problem["problem_id"],
    objective="Streamline customer onboarding process",
    priority=3,
    ai_enhanced=True
)

# Execute the cycle
result = client.execute_cycle(cycle["cycle_id"])

# Get results
solutions = client.get_solutions(cycle_id=cycle["cycle_id"])
```

### JavaScript SDK

```javascript
import { CosmicCouncilClient } from '@cosmic-council/sdk';

// Initialize client
const client = new CosmicCouncilClient({
    baseUrl: 'http://localhost:8000/api/v1',
    apiKey: 'your-api-key'
});

// Create a problem
const problem = await client.createProblem({
    title: 'Optimize Customer Support',
    description: 'Improve customer satisfaction and reduce response times',
    complexity: 'complex',
    domain: 'Customer Service',
    stakeholders: ['Support Team', 'Customers', 'Management'],
    constraints: { budget: '$50K', timeline: '3 months' },
    successCriteria: ['Response time < 2 hours', 'Satisfaction > 90%']
});

// Create and execute a cycle
const cycle = await client.createCycle({
    problemId: problem.problem_id,
    objective: 'Streamline customer onboarding process',
    priority: 3,
    aiEnhanced: true
});

// Execute the cycle
const result = await client.executeCycle(cycle.cycle_id);

// Get results
const solutions = await client.getSolutions({ cycleId: cycle.cycle_id });
```

## Error Handling Examples

### Python

```python
from cosmic_council_api import CosmicCouncilClient, APIError

client = CosmicCouncilClient(api_key="your-api-key")

try:
    problem = client.create_problem({
        "title": "Test Problem",
        "description": "Test description"
    })
except APIError as e:
    if e.status_code == 400:
        print(f"Bad request: {e.message}")
    elif e.status_code == 401:
        print("Unauthorized - check your API key")
    elif e.status_code == 429:
        print("Rate limit exceeded - wait before retrying")
    else:
        print(f"API error: {e.message}")
```

### JavaScript

```javascript
try {
    const problem = await client.createProblem({
        title: 'Test Problem',
        description: 'Test description'
    });
} catch (error) {
    if (error.status === 400) {
        console.log(`Bad request: ${error.message}`);
    } else if (error.status === 401) {
        console.log('Unauthorized - check your API key');
    } else if (error.status === 429) {
        console.log('Rate limit exceeded - wait before retrying');
    } else {
        console.log(`API error: ${error.message}`);
    }
}
```

## Best Practices

### 1. Error Handling
- Always implement proper error handling
- Check status codes and handle different error types
- Implement retry logic for transient errors
- Log errors for debugging

### 2. Rate Limiting
- Monitor rate limit headers
- Implement exponential backoff for retries
- Cache responses when appropriate
- Use batch operations when possible

### 3. Performance
- Use pagination for large result sets
- Implement caching for frequently accessed data
- Use WebSocket connections for real-time updates
- Optimize request payloads

### 4. Security
- Keep API keys secure
- Use HTTPS in production
- Implement proper authentication
- Validate all input data

## Support

For API support:

- **Documentation**: [docs.cosmic-council.org/api](https://docs.cosmic-council.org/api)
- **SDK Repository**: [github.com/cosmic-council/sdk](https://github.com/cosmic-council/sdk)
- **Issue Tracker**: [GitHub Issues](https://github.com/cosmic-council/framework/issues)
- **Email Support**: api-support@cosmic-council.org
