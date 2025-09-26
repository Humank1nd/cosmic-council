# 108-Cycle Fractal System

## Overview

The 108-Cycle Fractal System implements the Cosmic Council's symbolic and structural foundations through a complete PostgreSQL + N8N orchestration framework. This system operationalizes the symbolic **108** (6 enterprises × 6 squads × 3 redundancy passes) into a concrete, auditable, and scalable **agentic loop**.

## Architecture

### Core Components

1. **PostgreSQL Database** - The "archive vault" storing all cycle data, decisions, and analytics
2. **N8N Workflows** - The "nervous system" orchestrating the 108-stage flow
3. **Guardrail Gateway** - The "spine" enforcing policies and making decisions
4. **Six Enterprises** - Distributed brains implementing the fractal intelligence network

### The 108 Stages

The system implements exactly **108 stages** representing:
- **6 Enterprises**: Red Owl, Orange Orangutan, Yellow Honeybee, Green Turtle, Blue Dolphin, Purple Elephant
- **6 Squads per Enterprise**: Each enterprise has 6 micro-Councils (fractal structure)
- **3 Redundancy Passes**: Decide → Validate → Reflect

**Mathematical Foundation**: 6 × 6 × 3 = 108

**Symbolic Meaning**: 108 represents completion and wholeness (like 108 beads in a mala), ensuring the system has full redundancy and holistic coverage.

## Database Schema

### Core Tables

- `enterprises` - 6 enterprise definitions
- `squads` - 6 squad definitions (fractal structure)
- `redundancy_pass` - 3 redundancy pass types
- `cycle_stages` - All 108 canonical stage definitions
- `cycle_runs` - Runtime cycle execution instances
- `cycle_stage_runs` - Individual stage executions
- `cycle_stage_transitions` - Directed graph of stage transitions
- `policy_evolution` - Purple Elephant's continuous improvement proposals
- `n8n_workflow_executions` - N8N workflow execution tracking

### Key Features

- **ACID Compliance** - Full transactional integrity
- **Time Partitioning** - Efficient storage and querying
- **Provenance Tracking** - Complete audit trail
- **Budget Management** - Resource tracking and caps
- **Analytics Views** - Real-time monitoring and insights

## N8N Workflow Orchestration

### Core Workflows

1. **Cycle Run Starter** (`cycle-run-starter.json`)
   - HTTP endpoint: `POST /run-cycle`
   - Creates cycle run and all 108 stage runs
   - Initiates the orchestration process

2. **Stage Runner** (`stage-runner.json`)
   - Cron trigger (every 5 seconds)
   - Executes individual stages with Guardrail Gateway integration
   - Handles transitions and error recovery
   - Manages obligations and side effects

3. **Reflection & Policy Evolution** (`reflection-policy-evolution.json`)
   - Hourly cron trigger
   - Purple Elephant's continuous reflection
   - Policy evolution proposals
   - Simulation and canary deployments

4. **Run Completer** (integrated in Stage Runner)
   - Completes cycle runs when all stages finish
   - Calculates final metrics
   - Triggers completion notifications

### Workflow Features

- **Idempotent Execution** - Safe retries and error recovery
- **Guardrail Integration** - All decisions validated through Gateway
- **Obligation Handling** - Automatic budget telemetry and provenance
- **Error Recovery** - Fallback transitions and retry logic
- **Metrics Collection** - Performance and cost tracking

## Guardrail Gateway Integration

### New Endpoints

- `POST /v1/cycle/start` - Start a new 108-stage cycle run
- `POST /v1/cycle/complete` - Mark cycle run as completed
- `GET /v1/cycle/{run_id}/status` - Get cycle run status and progress
- `GET /v1/cycles` - List available cycle templates

### Enhanced Features

- **Stage Evaluation** - Each stage calls `/v1/evaluate` with proper context
- **Decision Tracking** - All decisions linked to stage runs
- **Obligation Processing** - Automatic handling of budget and provenance obligations
- **Policy Evolution** - Support for Purple Elephant's continuous improvement

## Analytics and Monitoring

### Key Views

- `v_cycle_dashboard` - Real-time cycle progress
- `v_stage_performance_analytics` - Stage-level performance metrics
- `v_enterprise_performance` - Enterprise-level summaries
- `v_incident_heatmap` - Incident tracking by enterprise/squad/time
- `v_policy_evolution_summary` - Policy improvement tracking
- `v_system_health` - Overall system health metrics

### Monitoring Capabilities

- **Real-time Progress** - Live cycle execution tracking
- **Performance Analytics** - Latency, success rates, bottlenecks
- **Incident Tracking** - Security and policy violations
- **Resource Utilization** - Budget and cost monitoring
- **Policy Evolution** - Continuous improvement tracking

## Deployment

### Prerequisites

- PostgreSQL 13+ with `pgcrypto` extension
- N8N instance with PostgreSQL credentials
- Guardrail Gateway service
- Docker (optional, for containerized deployment)

### Setup Steps

1. **Database Setup**
   ```bash
   # Run migrations in order
   psql -d cosmic_council -f migrations/001_init.sql
   psql -d cosmic_council -f migrations/002_enterprise_architecture.sql
   psql -d cosmic_council -f migrations/003_production_hardening.sql
   psql -d cosmic_council -f migrations/004_108_cycles_fractal.sql
   ```

2. **Seed Data**
   ```bash
   psql -d cosmic_council -f scripts/seed_108_cycles.sql
   ```

3. **Analytics Views**
   ```bash
   psql -d cosmic_council -f scripts/analytics_views.sql
   ```

4. **N8N Workflows**
   - Import workflow JSON files into N8N
   - Configure PostgreSQL credentials
   - Set up webhook endpoints

5. **Gateway Configuration**
   - Deploy updated Gateway with new endpoints
   - Configure database connections
   - Test cycle run endpoints

### Configuration

#### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/cosmic_council

# N8N
N8N_WEBHOOK_URL=http://n8n:5678
N8N_API_KEY=your_api_key

# Gateway
GATEWAY_URL=http://gateway:8000
```

#### N8N Credentials

- **PostgreSQL**: Connection to cosmic_council database
- **HTTP Request**: Gateway API endpoints
- **Webhook**: Cycle run starter endpoint

## Usage Examples

### Starting a Cycle Run

```bash
curl -X POST http://gateway:8000/v1/cycle/start \
  -H "Content-Type: application/json" \
  -d '{
    "cycle_id": "00000000-0000-0000-0000-000000000001",
    "objective_ref": "demo-objective-001",
    "priority": 3,
    "context": {"problem": "Analyze customer feedback"},
    "metadata": {"source": "api", "user": "demo"}
  }'
```

### Monitoring Progress

```bash
curl http://gateway:8000/v1/cycle/{run_id}/status
```

### Analytics Queries

```sql
-- Current running cycles
SELECT * FROM v_cycle_dashboard WHERE status = 'running';

-- Stage performance
SELECT * FROM v_stage_performance_analytics 
ORDER BY p95_duration_ms DESC LIMIT 10;

-- Enterprise performance
SELECT * FROM v_enterprise_performance 
ORDER BY stage_success_rate DESC;
```

## The Cosmic Council Flow

### Stage Execution Flow

1. **Red Owl (Knowledge)** - Gather and analyze information
2. **Orange Orangutan (Logistics)** - Plan and coordinate resources
3. **Yellow Honeybee (Creativity)** - Generate innovative solutions
4. **Green Turtle (Stewardship)** - Ensure sustainability and budget compliance
5. **Blue Dolphin (Communication)** - Validate brand safety and messaging
6. **Purple Elephant (Empathy)** - Reflect and improve the system

### Redundancy Passes

- **Decide** - Primary decision and action
- **Validate** - Independent verification and cross-checking
- **Reflect** - Retrospective analysis and learning

### Continuous Improvement

- **Purple Elephant** runs hourly reflection cycles
- **Policy Evolution** proposals based on incident analysis
- **Simulation** of proposed changes before deployment
- **Canary Deployment** of improved policies
- **Metrics-Driven** decision making

## Benefits

### Operational Excellence

- **Complete Audit Trail** - Every decision and action is tracked
- **Fault Tolerance** - Redundant validation and error recovery
- **Performance Monitoring** - Real-time metrics and alerting
- **Resource Management** - Budget caps and cost tracking

### Symbolic Alignment

- **Fractal Structure** - True to Cosmic Council's design
- **108 Completion** - Mathematically and symbolically complete
- **Enterprise Harmony** - All six enterprises working in concert
- **Continuous Evolution** - Self-improving and adaptive

### Technical Robustness

- **ACID Compliance** - Data integrity guaranteed
- **Scalable Architecture** - Handles high-volume decision making
- **Policy-Driven** - All actions validated through Guardrail Gateway
- **Observable** - Comprehensive monitoring and analytics

## Future Enhancements

- **Machine Learning** - Predictive analytics for cycle optimization
- **Advanced Simulations** - More sophisticated policy testing
- **Multi-Tenant** - Support for multiple Cosmic Council instances
- **API Gateway** - Enhanced external integration capabilities
- **Real-time Dashboards** - Live monitoring interfaces

---

*This system represents the complete operationalization of the Cosmic Council's 108-cycle fractal intelligence network, providing a robust, auditable, and self-improving agentic operating system.*
