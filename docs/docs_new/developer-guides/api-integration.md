# API Integration Guide

## Overview

This guide provides comprehensive information for developers who want to integrate with the Cosmic Council Framework API. It covers authentication, endpoints, SDKs, and best practices for building applications that leverage the Cosmic Council's problem-solving capabilities.

## Quick Start

### 1. Get API Access

```bash
# Register for API access
curl -X POST https://api.cosmic-council.org/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "organization": "Your Company",
    "use_case": "Problem-solving automation"
  }'
```

### 2. Install SDK

```bash
# Python SDK
pip install cosmic-council-sdk

# JavaScript SDK
npm install @cosmic-council/sdk

# Go SDK
go get github.com/cosmic-council/sdk-go
```

### 3. Basic Integration

```python
from cosmic_council_sdk import CosmicCouncilClient

# Initialize client
client = CosmicCouncilClient(
    api_key="your-api-key",
    base_url="https://api.cosmic-council.org/v1"
)

# Create and solve a problem
problem = client.create_problem({
    "title": "Optimize Customer Support",
    "description": "Improve response times and satisfaction",
    "complexity": "moderate",
    "domain": "Customer Service"
})

cycle = client.create_cycle({
    "problem_id": problem["problem_id"],
    "objective": "Streamline support processes"
})

result = client.execute_cycle(cycle["cycle_id"])
solutions = client.get_solutions(cycle_id=cycle["cycle_id"])
```

## Authentication

### API Key Authentication

```python
from cosmic_council_sdk import CosmicCouncilClient

client = CosmicCouncilClient(
    api_key="your-api-key-here",
    base_url="https://api.cosmic-council.org/v1"
)
```

### OAuth 2.0 Authentication

```python
from cosmic_council_sdk import CosmicCouncilClient

client = CosmicCouncilClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    base_url="https://api.cosmic-council.org/v1"
)

# The SDK will handle token refresh automatically
```

### JWT Token Authentication

```python
from cosmic_council_sdk import CosmicCouncilClient

client = CosmicCouncilClient(
    jwt_token="your-jwt-token",
    base_url="https://api.cosmic-council.org/v1"
)
```

## Core API Endpoints

### Problems

#### Create Problem

```python
problem = client.create_problem({
    "title": "Optimize Supply Chain",
    "description": "Reduce costs and improve efficiency",
    "complexity": "complex",
    "domain": "Logistics",
    "stakeholders": ["Operations", "Finance", "Customers"],
    "constraints": {
        "budget": "$100K",
        "timeline": "6 months"
    },
    "success_criteria": [
        "Cost reduction > 15%",
        "Delivery time < 48 hours",
        "Customer satisfaction > 90%"
    ]
})
```

#### Get Problem

```python
problem = client.get_problem("problem-id")
```

#### List Problems

```python
problems = client.list_problems(
    limit=20,
    offset=0,
    status="in_progress",
    complexity="complex"
)
```

#### Update Problem

```python
updated_problem = client.update_problem("problem-id", {
    "title": "Updated Problem Title",
    "description": "Updated description"
})
```

#### Delete Problem

```python
client.delete_problem("problem-id")
```

### Cycles

#### Create Cycle

```python
cycle = client.create_cycle({
    "problem_id": "problem-id",
    "objective": "Implement automated inventory management",
    "priority": 3,
    "ai_enhanced": True,
    "config": {
        "max_iterations": 5,
        "confidence_threshold": 0.85
    }
})
```

#### Execute Cycle

```python
result = client.execute_cycle("cycle-id")
```

#### Get Cycle Status

```python
cycle = client.get_cycle("cycle-id")
```

#### List Cycles

```python
cycles = client.list_cycles(
    problem_id="problem-id",
    status="completed",
    limit=20
)
```

### Solutions

#### Get Solutions

```python
solutions = client.get_solutions(
    cycle_id="cycle-id",
    limit=20
)
```

#### Create Solution

```python
solution = client.create_solution({
    "cycle_id": "cycle-id",
    "title": "Automated Inventory System",
    "description": "AI-powered inventory management solution",
    "components": [
        {
            "name": "Demand Forecasting",
            "description": "Predict demand using ML",
            "priority": 1,
            "estimated_effort": "4 weeks"
        }
    ]
})
```

#### Update Solution

```python
updated_solution = client.update_solution("solution-id", {
    "status": "implemented",
    "implementation_notes": "Successfully deployed"
})
```

### Analytics

#### Get Problem Analytics

```python
analytics = client.get_problem_analytics()
```

#### Get Cycle Analytics

```python
analytics = client.get_cycle_analytics()
```

#### Get Solution Analytics

```python
analytics = client.get_solution_analytics()
```

#### Get Enterprise Performance

```python
performance = client.get_enterprise_performance("red_owl")
```

## Advanced Features

### WebSocket Integration

```python
import asyncio
from cosmic_council_sdk import CosmicCouncilWebSocketClient

async def handle_cycle_updates():
    async with CosmicCouncilWebSocketClient(api_key="your-api-key") as ws:
        # Subscribe to cycle updates
        await ws.subscribe_cycle_updates("cycle-id")
        
        async for message in ws.listen():
            if message["type"] == "cycle_status_update":
                print(f"Cycle {message['cycle_id']} status: {message['status']}")
            elif message["type"] == "enterprise_result":
                print(f"Enterprise {message['enterprise']} completed")
            elif message["type"] == "cycle_completion":
                print(f"Cycle {message['cycle_id']} completed!")

# Run the WebSocket client
asyncio.run(handle_cycle_updates())
```

### Batch Operations

```python
# Create multiple problems
problems = client.create_problems_batch([
    {
        "title": "Problem 1",
        "description": "Description 1",
        "complexity": "simple",
        "domain": "Test"
    },
    {
        "title": "Problem 2",
        "description": "Description 2",
        "complexity": "moderate",
        "domain": "Test"
    }
])

# Execute multiple cycles
results = client.execute_cycles_batch(["cycle-id-1", "cycle-id-2"])
```

### Custom Enterprise Agents

```python
# Define custom enterprise agent
class CustomEnterpriseAgent:
    def __init__(self, name, role, capabilities):
        self.name = name
        self.role = role
        self.capabilities = capabilities
    
    async def process_problem(self, problem):
        # Custom processing logic
        return {
            "status": "completed",
            "confidence": 0.9,
            "insights": ["Custom insight"],
            "recommendations": ["Custom recommendation"]
        }

# Register custom agent
client.register_enterprise_agent(CustomEnterpriseAgent(
    name="Custom Agent",
    role="Specialized Analysis",
    capabilities=["Custom Analysis", "Domain Expertise"]
))
```

## SDK Examples

### Python SDK

```python
from cosmic_council_sdk import CosmicCouncilClient
import asyncio

class ProblemSolver:
    def __init__(self, api_key):
        self.client = CosmicCouncilClient(api_key=api_key)
    
    async def solve_business_problem(self, problem_data):
        """Solve a business problem using the Cosmic Council"""
        
        # Create problem
        problem = await self.client.create_problem(problem_data)
        print(f"Created problem: {problem['title']}")
        
        # Create and execute cycle
        cycle = await self.client.create_cycle({
            "problem_id": problem["problem_id"],
            "objective": "Find optimal solution",
            "priority": 3,
            "ai_enhanced": True
        })
        
        print(f"Created cycle: {cycle['cycle_id']}")
        
        # Execute cycle
        result = await self.client.execute_cycle(cycle["cycle_id"])
        print(f"Cycle execution started: {result['status']}")
        
        # Wait for completion
        while True:
            cycle_status = await self.client.get_cycle(cycle["cycle_id"])
            if cycle_status["status"] == "completed":
                break
            await asyncio.sleep(5)
        
        # Get solutions
        solutions = await self.client.get_solutions(cycle_id=cycle["cycle_id"])
        
        return {
            "problem": problem,
            "cycle": cycle_status,
            "solutions": solutions
        }

# Usage
async def main():
    solver = ProblemSolver("your-api-key")
    
    result = await solver.solve_business_problem({
        "title": "Optimize Customer Onboarding",
        "description": "Reduce onboarding time and improve satisfaction",
        "complexity": "moderate",
        "domain": "Customer Experience",
        "stakeholders": ["Customers", "Support Team", "Product Team"],
        "constraints": {"budget": "$25K", "timeline": "2 months"},
        "success_criteria": ["Onboarding time < 7 days", "Satisfaction > 85%"]
    })
    
    print("Problem solved!")
    print(f"Solutions found: {len(result['solutions'])}")
    for solution in result["solutions"]:
        print(f"- {solution['title']}: {solution['description']}")

asyncio.run(main())
```

### JavaScript SDK

```javascript
import { CosmicCouncilClient } from '@cosmic-council/sdk';

class ProblemSolver {
    constructor(apiKey) {
        this.client = new CosmicCouncilClient({
            apiKey: apiKey,
            baseUrl: 'https://api.cosmic-council.org/v1'
        });
    }
    
    async solveBusinessProblem(problemData) {
        try {
            // Create problem
            const problem = await this.client.createProblem(problemData);
            console.log(`Created problem: ${problem.title}`);
            
            // Create and execute cycle
            const cycle = await this.client.createCycle({
                problemId: problem.problem_id,
                objective: 'Find optimal solution',
                priority: 3,
                aiEnhanced: true
            });
            
            console.log(`Created cycle: ${cycle.cycle_id}`);
            
            // Execute cycle
            const result = await this.client.executeCycle(cycle.cycle_id);
            console.log(`Cycle execution started: ${result.status}`);
            
            // Wait for completion
            let cycleStatus;
            do {
                await new Promise(resolve => setTimeout(resolve, 5000));
                cycleStatus = await this.client.getCycle(cycle.cycle_id);
            } while (cycleStatus.status !== 'completed');
            
            // Get solutions
            const solutions = await this.client.getSolutions({
                cycleId: cycle.cycle_id
            });
            
            return {
                problem,
                cycle: cycleStatus,
                solutions
            };
            
        } catch (error) {
            console.error('Error solving problem:', error);
            throw error;
        }
    }
}

// Usage
async function main() {
    const solver = new ProblemSolver('your-api-key');
    
    const result = await solver.solveBusinessProblem({
        title: 'Optimize Customer Onboarding',
        description: 'Reduce onboarding time and improve satisfaction',
        complexity: 'moderate',
        domain: 'Customer Experience',
        stakeholders: ['Customers', 'Support Team', 'Product Team'],
        constraints: { budget: '$25K', timeline: '2 months' },
        successCriteria: ['Onboarding time < 7 days', 'Satisfaction > 85%']
    });
    
    console.log('Problem solved!');
    console.log(`Solutions found: ${result.solutions.length}`);
    result.solutions.forEach(solution => {
        console.log(`- ${solution.title}: ${solution.description}`);
    });
}

main().catch(console.error);
```

### Go SDK

```go
package main

import (
    "context"
    "fmt"
    "log"
    "time"
    
    "github.com/cosmic-council/sdk-go"
)

type ProblemSolver struct {
    client *cosmiccouncil.Client
}

func NewProblemSolver(apiKey string) *ProblemSolver {
    client := cosmiccouncil.NewClient(apiKey)
    return &ProblemSolver{client: client}
}

func (ps *ProblemSolver) SolveBusinessProblem(ctx context.Context, problemData cosmiccouncil.ProblemData) (*cosmiccouncil.SolutionResult, error) {
    // Create problem
    problem, err := ps.client.CreateProblem(ctx, problemData)
    if err != nil {
        return nil, fmt.Errorf("failed to create problem: %w", err)
    }
    
    fmt.Printf("Created problem: %s\n", problem.Title)
    
    // Create cycle
    cycle, err := ps.client.CreateCycle(ctx, cosmiccouncil.CycleData{
        ProblemID:   problem.ID,
        Objective:   "Find optimal solution",
        Priority:    3,
        AIEnhanced:  true,
    })
    if err != nil {
        return nil, fmt.Errorf("failed to create cycle: %w", err)
    }
    
    fmt.Printf("Created cycle: %s\n", cycle.ID)
    
    // Execute cycle
    result, err := ps.client.ExecuteCycle(ctx, cycle.ID)
    if err != nil {
        return nil, fmt.Errorf("failed to execute cycle: %w", err)
    }
    
    fmt.Printf("Cycle execution started: %s\n", result.Status)
    
    // Wait for completion
    for {
        time.Sleep(5 * time.Second)
        cycleStatus, err := ps.client.GetCycle(ctx, cycle.ID)
        if err != nil {
            return nil, fmt.Errorf("failed to get cycle status: %w", err)
        }
        
        if cycleStatus.Status == "completed" {
            break
        }
    }
    
    // Get solutions
    solutions, err := ps.client.GetSolutions(ctx, cosmiccouncil.SolutionQuery{
        CycleID: cycle.ID,
    })
    if err != nil {
        return nil, fmt.Errorf("failed to get solutions: %w", err)
    }
    
    return &cosmiccouncil.SolutionResult{
        Problem:   problem,
        Cycle:     cycle,
        Solutions: solutions,
    }, nil
}

func main() {
    solver := NewProblemSolver("your-api-key")
    
    result, err := solver.SolveBusinessProblem(context.Background(), cosmiccouncil.ProblemData{
        Title:       "Optimize Customer Onboarding",
        Description: "Reduce onboarding time and improve satisfaction",
        Complexity:  "moderate",
        Domain:      "Customer Experience",
        Stakeholders: []string{"Customers", "Support Team", "Product Team"},
        Constraints: map[string]string{
            "budget":   "$25K",
            "timeline": "2 months",
        },
        SuccessCriteria: []string{
            "Onboarding time < 7 days",
            "Satisfaction > 85%",
        },
    })
    
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Println("Problem solved!")
    fmt.Printf("Solutions found: %d\n", len(result.Solutions))
    for _, solution := range result.Solutions {
        fmt.Printf("- %s: %s\n", solution.Title, solution.Description)
    }
}
```

## Error Handling

### Python Error Handling

```python
from cosmic_council_sdk import CosmicCouncilClient, APIError, RateLimitError

client = CosmicCouncilClient(api_key="your-api-key")

try:
    problem = client.create_problem({
        "title": "Test Problem",
        "description": "Test description",
        "complexity": "simple",
        "domain": "Test"
    })
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
    time.sleep(e.retry_after)
except APIError as e:
    if e.status_code == 400:
        print(f"Bad request: {e.message}")
    elif e.status_code == 401:
        print("Unauthorized - check your API key")
    elif e.status_code == 429:
        print("Rate limit exceeded")
    else:
        print(f"API error: {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### JavaScript Error Handling

```javascript
try {
    const problem = await client.createProblem({
        title: 'Test Problem',
        description: 'Test description',
        complexity: 'simple',
        domain: 'Test'
    });
} catch (error) {
    if (error instanceof RateLimitError) {
        console.log(`Rate limit exceeded. Retry after ${error.retryAfter} seconds`);
        await new Promise(resolve => setTimeout(resolve, error.retryAfter * 1000));
    } else if (error instanceof APIError) {
        switch (error.status) {
            case 400:
                console.log(`Bad request: ${error.message}`);
                break;
            case 401:
                console.log('Unauthorized - check your API key');
                break;
            case 429:
                console.log('Rate limit exceeded');
                break;
            default:
                console.log(`API error: ${error.message}`);
        }
    } else {
        console.log(`Unexpected error: ${error.message}`);
    }
}
```

## Best Practices

### 1. Rate Limiting

```python
import time
from cosmic_council_sdk import CosmicCouncilClient, RateLimitError

client = CosmicCouncilClient(api_key="your-api-key")

def make_request_with_retry(func, *args, **kwargs):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except RateLimitError as e:
            if attempt < max_retries - 1:
                time.sleep(e.retry_after)
                continue
            raise

# Usage
problem = make_request_with_retry(
    client.create_problem,
    {"title": "Test Problem", "complexity": "simple", "domain": "Test"}
)
```

### 2. Caching

```python
import redis
from cosmic_council_sdk import CosmicCouncilClient

redis_client = redis.Redis(host='localhost', port=6379, db=0)
client = CosmicCouncilClient(api_key="your-api-key")

def get_problem_with_cache(problem_id):
    # Check cache first
    cached = redis_client.get(f"problem:{problem_id}")
    if cached:
        return json.loads(cached)
    
    # Fetch from API
    problem = client.get_problem(problem_id)
    
    # Cache for 1 hour
    redis_client.setex(
        f"problem:{problem_id}",
        3600,
        json.dumps(problem)
    )
    
    return problem
```

### 3. Batch Processing

```python
import asyncio
from cosmic_council_sdk import CosmicCouncilClient

client = CosmicCouncilClient(api_key="your-api-key")

async def process_problems_batch(problem_data_list):
    # Create problems in parallel
    tasks = [
        client.create_problem(problem_data)
        for problem_data in problem_data_list
    ]
    
    problems = await asyncio.gather(*tasks)
    
    # Create cycles in parallel
    cycle_tasks = [
        client.create_cycle({
            "problem_id": problem["problem_id"],
            "objective": "Solve problem",
            "priority": 3
        })
        for problem in problems
    ]
    
    cycles = await asyncio.gather(*cycle_tasks)
    
    # Execute cycles in parallel
    execution_tasks = [
        client.execute_cycle(cycle["cycle_id"])
        for cycle in cycles
    ]
    
    results = await asyncio.gather(*execution_tasks)
    
    return list(zip(problems, cycles, results))
```

### 4. Monitoring and Logging

```python
import logging
import time
from cosmic_council_sdk import CosmicCouncilClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoredCosmicCouncilClient(CosmicCouncilClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_count = 0
        self.total_time = 0
    
    def _make_request(self, method, url, **kwargs):
        start_time = time.time()
        self.request_count += 1
        
        try:
            response = super()._make_request(method, url, **kwargs)
            duration = time.time() - start_time
            self.total_time += duration
            
            logger.info(f"Request {self.request_count}: {method} {url} - {response.status_code} ({duration:.2f}s)")
            
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Request {self.request_count}: {method} {url} - ERROR ({duration:.2f}s): {e}")
            raise
    
    def get_stats(self):
        avg_time = self.total_time / self.request_count if self.request_count > 0 else 0
        return {
            "request_count": self.request_count,
            "total_time": self.total_time,
            "average_time": avg_time
        }
```

## Integration Examples

### Slack Integration

```python
import os
from slack_sdk import WebClient
from cosmic_council_sdk import CosmicCouncilClient

class SlackCosmicCouncilBot:
    def __init__(self):
        self.slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        self.cosmic_client = CosmicCouncilClient(api_key=os.environ["COSMIC_COUNCIL_API_KEY"])
    
    def handle_problem_request(self, channel, user, problem_text):
        """Handle a problem request from Slack"""
        
        # Create problem
        problem = self.cosmic_client.create_problem({
            "title": f"Slack Problem from {user}",
            "description": problem_text,
            "complexity": "moderate",
            "domain": "Slack Integration"
        })
        
        # Create and execute cycle
        cycle = self.cosmic_client.create_cycle({
            "problem_id": problem["problem_id"],
            "objective": "Solve Slack problem",
            "priority": 3
        })
        
        result = self.cosmic_client.execute_cycle(cycle["cycle_id"])
        
        # Send initial response
        self.slack_client.chat_postMessage(
            channel=channel,
            text=f"🤖 I've started working on your problem! Cycle ID: {cycle['cycle_id']}"
        )
        
        # Monitor progress and send updates
        self.monitor_cycle_progress(channel, cycle["cycle_id"])
    
    def monitor_cycle_progress(self, channel, cycle_id):
        """Monitor cycle progress and send updates"""
        while True:
            cycle = self.cosmic_client.get_cycle(cycle_id)
            
            if cycle["status"] == "completed":
                solutions = self.cosmic_client.get_solutions(cycle_id=cycle_id)
                
                message = "🎉 Problem solved! Here are the solutions:\n"
                for solution in solutions:
                    message += f"• {solution['title']}: {solution['description']}\n"
                
                self.slack_client.chat_postMessage(
                    channel=channel,
                    text=message
                )
                break
            
            time.sleep(30)  # Check every 30 seconds
```

### Zapier Integration

```python
# Zapier webhook handler
from flask import Flask, request, jsonify
from cosmic_council_sdk import CosmicCouncilClient

app = Flask(__name__)
client = CosmicCouncilClient(api_key="your-api-key")

@app.route('/zapier/cosmic-council', methods=['POST'])
def handle_zapier_webhook():
    data = request.json
    
    # Extract problem data from Zapier
    problem_data = {
        "title": data.get("title", "Zapier Problem"),
        "description": data.get("description", ""),
        "complexity": data.get("complexity", "moderate"),
        "domain": data.get("domain", "Zapier Integration"),
        "stakeholders": data.get("stakeholders", []),
        "constraints": data.get("constraints", {}),
        "success_criteria": data.get("success_criteria", [])
    }
    
    # Create problem
    problem = client.create_problem(problem_data)
    
    # Create and execute cycle
    cycle = client.create_cycle({
        "problem_id": problem["problem_id"],
        "objective": "Solve Zapier problem",
        "priority": 3
    })
    
    result = client.execute_cycle(cycle["cycle_id"])
    
    return jsonify({
        "problem_id": problem["problem_id"],
        "cycle_id": cycle["cycle_id"],
        "status": result["status"]
    })
```

## Support

For API integration support:

- **Documentation**: [docs.cosmic-council.org/api](https://docs.cosmic-council.org/api)
- **SDK Repository**: [github.com/cosmic-council/sdk](https://github.com/cosmic-council/sdk)
- **Issue Tracker**: [GitHub Issues](https://github.com/cosmic-council/framework/issues)
- **Email Support**: api-support@cosmic-council.org
- **Community Forum**: [community.cosmic-council.org](https://community.cosmic-council.org)
