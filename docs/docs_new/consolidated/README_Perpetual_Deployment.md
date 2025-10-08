# Perpetual Thinking System Deployment Guide

This guide provides comprehensive instructions for deploying the Cosmic Council Perpetual Thinking System across different environments.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [Performance Tuning](#performance-tuning)

## Overview

The Perpetual Thinking System is a sophisticated AI-enhanced reasoning engine that provides continuous, adaptive problem-solving capabilities. It integrates with the existing Cosmic Council framework to offer:

- **AI-Enhanced Perpetual Sessions**: Continuous thinking cycles with AI assistance
- **Multiple Enhancement Levels**: From assisted to autonomous AI participation
- **Learning and Adaptation**: Self-improving reasoning capabilities
- **Breakthrough Detection**: Automatic identification of significant insights
- **Comprehensive Analytics**: Detailed metrics and performance tracking

## Prerequisites

### System Requirements

- **CPU**: 4+ cores recommended
- **Memory**: 8GB+ RAM recommended
- **Storage**: 20GB+ available space
- **Network**: Internet access for AI API calls

### Software Requirements

#### For Docker Deployment
- Docker 20.10+
- Docker Compose 2.0+
- Git

#### For Kubernetes Deployment
- Kubernetes 1.20+
- kubectl 1.20+
- Helm 3.0+ (optional)

### API Keys Required

- **OpenAI API Key**: For GPT-4 integration
- **Anthropic API Key**: For Claude integration (optional)
- **Database Credentials**: PostgreSQL access

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/cosmic-council.git
cd cosmic-council
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your configuration
nano .env
```

### 3. Deploy with Docker (Recommended for Development)

```bash
# Linux/macOS
./scripts/deploy_perpetual_system.sh docker --test

# Windows
scripts\deploy_perpetual_system.bat docker --test
```

### 4. Access the System

- **Web Interface**: http://localhost:8001
- **API**: http://localhost:8000
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## Docker Deployment

### Development Environment

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

### Production Environment

```bash
# Start production environment
docker-compose up -d

# Scale API service
docker-compose up -d --scale api=3

# Update services
docker-compose pull
docker-compose up -d
```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
POSTGRES_PASSWORD=your-secure-password

# API Keys
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Perpetual Thinking System
PERPETUAL_AI_PROVIDER=openai
PERPETUAL_AI_MODEL=gpt-4
PERPETUAL_AI_TEMPERATURE=0.7
PERPETUAL_AI_MAX_TOKENS=2000
PERPETUAL_MAX_CONCURRENT_SESSIONS=10
PERPETUAL_SESSION_TIMEOUT=3600

# Security
SECRET_KEY=your-secret-key
API_KEY=your-api-key

# Monitoring
GRAFANA_PASSWORD=admin
```

## Kubernetes Deployment

### 1. Prepare Kubernetes Cluster

```bash
# Create namespace
kubectl create namespace cosmic-council

# Apply namespace configuration
kubectl apply -f k8s/namespace.yaml
```

### 2. Set Up Secrets

```bash
# Create secrets
kubectl create secret generic cosmic-council-secrets \
  --from-literal=DATABASE_PASSWORD=your-secure-password \
  --from-literal=SECRET_KEY=your-secret-key \
  --from-literal=API_KEY=your-api-key \
  --from-literal=OPENAI_API_KEY=your-openai-api-key \
  --from-literal=ANTHROPIC_API_KEY=your-anthropic-api-key \
  --from-literal=JWT_SECRET=your-jwt-secret \
  --from-literal=JWT_ALGORITHM=HS256 \
  --from-literal=JWT_EXPIRATION=3600 \
  -n cosmic-council
```

### 3. Deploy Services

```bash
# Apply configuration
kubectl apply -f k8s/configmap.yaml

# Deploy databases
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/postgres-perpetual.yaml
kubectl apply -f k8s/redis.yaml

# Deploy applications
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/web.yaml

# Deploy ingress
kubectl apply -f k8s/ingress.yaml
```

### 4. Verify Deployment

```bash
# Check pod status
kubectl get pods -n cosmic-council

# Check services
kubectl get services -n cosmic-council

# Check ingress
kubectl get ingress -n cosmic-council
```

## Configuration

### Perpetual Thinking System Settings

| Setting | Description | Default | Environment Variable |
|---------|-------------|---------|---------------------|
| AI Provider | LLM provider to use | openai | `PERPETUAL_AI_PROVIDER` |
| AI Model | Specific model to use | gpt-4 | `PERPETUAL_AI_MODEL` |
| Temperature | AI creativity level | 0.7 | `PERPETUAL_AI_TEMPERATURE` |
| Max Tokens | Maximum tokens per request | 2000 | `PERPETUAL_AI_MAX_TOKENS` |
| Max Sessions | Concurrent session limit | 10 | `PERPETUAL_MAX_CONCURRENT_SESSIONS` |
| Session Timeout | Session timeout in seconds | 3600 | `PERPETUAL_SESSION_TIMEOUT` |
| Learning Enabled | Enable AI learning | true | `PERPETUAL_LEARNING_ENABLED` |
| Adaptation Enabled | Enable AI adaptation | true | `PERPETUAL_ADAPTATION_ENABLED` |
| Breakthrough Detection | Enable breakthrough detection | true | `PERPETUAL_BREAKTHROUGH_DETECTION` |

### Database Configuration

The system uses two PostgreSQL databases:

1. **Main Database** (`cosmic_council`): Core system data
2. **Perpetual Database** (`cosmic_council_perpetual`): Perpetual thinking sessions and analytics

### AI Enhancement Levels

- **None**: No AI assistance
- **Assisted**: AI provides suggestions, human makes decisions
- **Enhanced**: AI actively participates, human oversees
- **Autonomous**: AI drives the process, human monitors

## Monitoring

### Grafana Dashboards

Access Grafana at http://localhost:3000 (admin/admin) to view:

- **System Overview**: Overall system health and performance
- **Perpetual Sessions**: Active sessions and their metrics
- **AI Performance**: AI response times and token usage
- **Database Metrics**: Database performance and query statistics
- **Error Tracking**: Error rates and types

### Prometheus Metrics

Key metrics available at http://localhost:9090:

- `perpetual_sessions_active`: Number of active sessions
- `perpetual_cycles_total`: Total cycles executed
- `ai_requests_total`: Total AI API requests
- `ai_response_time_seconds`: AI response times
- `database_connections_active`: Active database connections

### Log Monitoring

```bash
# Docker logs
docker-compose logs -f api
docker-compose logs -f web

# Kubernetes logs
kubectl logs -f deployment/cosmic-council-api -n cosmic-council
kubectl logs -f deployment/cosmic-council-web -n cosmic-council
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues

```bash
# Check database connectivity
docker-compose exec api python -c "
import psycopg2
conn = psycopg2.connect('postgresql://cosmic_council:password@postgres:5432/cosmic_council')
print('Database connection successful')
"
```

#### 2. AI API Issues

```bash
# Test AI connectivity
curl -X POST http://localhost:8000/api/v1/perpetual/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "session_name": "Test Session",
    "initial_input": "Test input",
    "ai_enhancement_level": "enhanced"
  }'
```

#### 3. Memory Issues

```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 4G
```

#### 4. Performance Issues

```bash
# Check system resources
htop
iostat -x 1

# Monitor database performance
docker-compose exec postgres psql -U cosmic_council -d cosmic_council -c "
SELECT * FROM pg_stat_activity;
"
```

### Debug Mode

Enable debug logging:

```env
LOG_LEVEL=DEBUG
PERPETUAL_DEBUG=true
```

### Health Checks

```bash
# API health check
curl http://localhost:8000/health

# Perpetual system status
curl http://localhost:8000/api/v1/perpetual/status
```

## Security Considerations

### 1. API Key Management

- Store API keys in environment variables or secrets
- Rotate keys regularly
- Use different keys for different environments

### 2. Database Security

- Use strong passwords
- Enable SSL connections
- Restrict network access
- Regular backups

### 3. Network Security

- Use HTTPS in production
- Implement rate limiting
- Configure firewall rules
- Use VPN for internal access

### 4. Container Security

- Use non-root users
- Keep images updated
- Scan for vulnerabilities
- Use minimal base images

## Performance Tuning

### 1. Database Optimization

```sql
-- Optimize PostgreSQL settings
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

### 2. Application Tuning

```env
# Increase worker processes
WORKER_PROCESSES=4
WORKER_CONNECTIONS=1000

# Optimize AI settings
PERPETUAL_AI_MAX_TOKENS=1500
PERPETUAL_AI_TEMPERATURE=0.6
```

### 3. Caching

```env
# Enable Redis caching
REDIS_CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
```

### 4. Load Balancing

```yaml
# Kubernetes HPA configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: cosmic-council-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: cosmic-council-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Backup and Recovery

### Database Backups

```bash
# Create backup
docker-compose exec postgres pg_dump -U cosmic_council cosmic_council > backup_main.sql
docker-compose exec postgres-perpetual pg_dump -U cosmic_council cosmic_council_perpetual > backup_perpetual.sql

# Restore backup
docker-compose exec -T postgres psql -U cosmic_council cosmic_council < backup_main.sql
docker-compose exec -T postgres-perpetual psql -U cosmic_council cosmic_council_perpetual < backup_perpetual.sql
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * /path/to/backup_script.sh
```

## Scaling

### Horizontal Scaling

```bash
# Scale API service
docker-compose up -d --scale api=5

# Kubernetes scaling
kubectl scale deployment cosmic-council-api --replicas=5 -n cosmic-council
```

### Vertical Scaling

```yaml
# Increase resource limits
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

## Support

For additional support:

1. Check the [troubleshooting section](#troubleshooting)
2. Review the [API documentation](README_API_System.md)
3. Check the [test suite](run_perpetual_tests.py)
4. Contact the development team

## Changelog

### Version 1.0.0
- Initial release of Perpetual Thinking System
- AI-enhanced perpetual sessions
- Multiple enhancement levels
- Learning and adaptation capabilities
- Breakthrough detection
- Comprehensive analytics
- Docker and Kubernetes deployment support
