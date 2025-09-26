# Cosmic Council Framework - Deployment Guide

## Overview

This document provides comprehensive deployment instructions for the Cosmic Council Framework using Docker, Kubernetes, and CI/CD pipelines. The framework supports multiple deployment strategies to meet different operational requirements.

## Deployment Options

### 1. Docker Compose (Recommended for Development)

**Best for**: Development, testing, small-scale deployments

**Features**:
- Single-command deployment
- Local development environment
- Integrated monitoring stack
- Easy debugging and troubleshooting

**Quick Start**:
```bash
# Development
docker-compose -f docker-compose.dev.yml up -d

# Production
docker-compose up -d
```

### 2. Kubernetes (Recommended for Production)

**Best for**: Production, high availability, enterprise deployments

**Features**:
- Auto-scaling and load balancing
- Rolling updates and rollbacks
- Service discovery and mesh networking
- Advanced monitoring and logging
- Multi-environment support

**Quick Start**:
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/
```

### 3. CI/CD Pipelines

**Features**:
- Automated testing and deployment
- Multi-environment support
- Security scanning and compliance
- Release management
- Community notifications

## Architecture

### Service Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   Web Interface │    │   API Service   │
│   (Load Balancer)│    │   (Port 8001)   │    │   (Port 8000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
         │   PostgreSQL    │    │   Redis Cache   │    │   Monitoring    │
         │   (Port 5432)   │    │   (Port 6379)   │    │   Stack         │
         └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Monitoring Stack

- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **Elasticsearch**: Log storage and indexing
- **Kibana**: Log analysis and visualization
- **Logstash**: Log processing and transformation

## Prerequisites

### Docker Deployment
- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

### Kubernetes Deployment
- Kubernetes cluster v1.24+
- kubectl configured
- 4 nodes with 4GB RAM each
- Persistent volume support
- Ingress controller

### CI/CD Requirements
- GitHub repository
- GitHub Actions enabled
- Container registry access
- Kubernetes cluster access

## Quick Start Guide

### 1. Clone Repository

```bash
git clone https://github.com/your-org/cosmic-council.git
cd cosmic-council
```

### 2. Environment Configuration

Create environment file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
POSTGRES_PASSWORD=your_secure_password

# Application
SECRET_KEY=your_secret_key
API_KEY=your_api_key

# AI Services
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Monitoring
GRAFANA_PASSWORD=your_grafana_password
```

### 3. Deploy with Docker Compose

```bash
# Development
./scripts/deploy.sh development deploy

# Production
./scripts/deploy.sh production deploy
```

### 4. Deploy to Kubernetes

```bash
# Create secrets
kubectl create secret generic cosmic-council-secrets \
  --from-env-file=.env \
  --namespace=cosmic-council

# Deploy
kubectl apply -f k8s/
```

## Detailed Deployment Instructions

### Docker Compose Deployment

#### Development Environment

```bash
# Start development services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

**Services**:
- API: http://localhost:8000
- Web: http://localhost:8001
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9091

#### Production Environment

```bash
# Start production services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services**:
- Web: http://localhost (Nginx)
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Kibana: http://localhost:5601

### Kubernetes Deployment

#### 1. Prepare Cluster

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl apply -f k8s/secrets.yaml

# Apply configuration
kubectl apply -f k8s/configmap.yaml
```

#### 2. Deploy Database Services

```bash
# Deploy PostgreSQL
kubectl apply -f k8s/postgres.yaml

# Deploy Redis
kubectl apply -f k8s/redis.yaml

# Wait for readiness
kubectl wait --for=condition=ready pod -l app=postgres -n cosmic-council --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n cosmic-council --timeout=300s
```

#### 3. Deploy Application Services

```bash
# Deploy API
kubectl apply -f k8s/api.yaml

# Deploy Web Interface
kubectl apply -f k8s/web.yaml

# Wait for readiness
kubectl wait --for=condition=available deployment/cosmic-council-api -n cosmic-council --timeout=300s
kubectl wait --for=condition=available deployment/cosmic-council-web -n cosmic-council --timeout=300s
```

#### 4. Configure Ingress

```bash
# Deploy ingress
kubectl apply -f k8s/ingress.yaml

# Check ingress status
kubectl get ingress -n cosmic-council
```

## CI/CD Pipeline

### GitHub Actions Workflow

The CI/CD pipeline includes:

1. **Testing**: Unit tests, integration tests, security scans
2. **Building**: Docker image creation and registry push
3. **Deployment**: Automated deployment to staging/production
4. **Monitoring**: Health checks and performance testing
5. **Notification**: Community notifications and release management

### Pipeline Stages

#### 1. Test Stage
- Python 3.9, 3.10, 3.11 compatibility
- Linting and type checking
- Security vulnerability scanning
- Unit and integration tests
- Code coverage reporting

#### 2. Build Stage
- Multi-platform Docker builds (AMD64, ARM64)
- Container registry push
- Image security scanning
- Metadata extraction and tagging

#### 3. Deploy Stage
- Staging deployment (develop branch)
- Production deployment (main branch)
- Health checks and smoke tests
- Rollback capabilities

#### 4. Release Stage
- Automated release creation
- Documentation updates
- Community notifications
- Performance testing

### Environment Configuration

#### Staging Environment
- Branch: `develop`
- Namespace: `cosmic-council-staging`
- Auto-deployment on push

#### Production Environment
- Branch: `main`
- Namespace: `cosmic-council`
- Manual approval required
- Blue-green deployment

## Monitoring and Observability

### Metrics Collection

**Prometheus Metrics**:
- Request rates and response times
- Error rates and status codes
- Database connection pool status
- Redis cache performance
- System resource usage

**Custom Metrics**:
- Problem-solving cycle duration
- Enterprise agent performance
- Solution quality scores
- User engagement metrics

### Logging

**Structured Logging**:
- JSON format for easy parsing
- Correlation IDs for request tracing
- Log levels: DEBUG, INFO, WARNING, ERROR
- Service identification and tagging

**Log Aggregation**:
- Centralized log collection
- Real-time log streaming
- Log retention and archival
- Search and analysis capabilities

### Alerting

**Critical Alerts**:
- Service downtime
- High error rates
- Database connection failures
- Resource exhaustion

**Warning Alerts**:
- Performance degradation
- Unusual traffic patterns
- Security events
- Capacity planning

## Security

### Container Security

- Non-root user execution
- Read-only root filesystems
- Minimal base images
- Regular security updates
- Vulnerability scanning

### Network Security

- Network policies and segmentation
- TLS/SSL encryption
- Service mesh integration
- Firewall rules and access control

### Secrets Management

- Kubernetes secrets
- Environment variable encryption
- API key rotation
- Secure credential storage

## Backup and Recovery

### Database Backup

```bash
# Manual backup
kubectl exec -it deployment/postgres -n cosmic-council -- \
  pg_dump -U cosmic_council cosmic_council > backup.sql

# Automated backup (CronJob)
kubectl apply -f k8s/backup-cronjob.yaml
```

### Volume Snapshots

```bash
# Create snapshot
kubectl apply -f k8s/volume-snapshot.yaml

# Restore from snapshot
kubectl apply -f k8s/volume-restore.yaml
```

### Disaster Recovery

- Multi-region deployment
- Cross-region replication
- Automated failover
- Recovery time objectives (RTO)
- Recovery point objectives (RPO)

## Performance Optimization

### Horizontal Scaling

```bash
# Scale API service
kubectl scale deployment cosmic-council-api --replicas=5 -n cosmic-council

# Scale web service
kubectl scale deployment cosmic-council-web --replicas=3 -n cosmic-council
```

### Vertical Scaling

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

### Caching Strategy

- Redis for session storage
- Application-level caching
- CDN for static assets
- Database query optimization

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check pod status
kubectl get pods -n cosmic-council

# Check logs
kubectl logs -f deployment/cosmic-council-api -n cosmic-council

# Check events
kubectl describe pod <pod-name> -n cosmic-council
```

#### Database Connection Issues
```bash
# Test database connectivity
kubectl exec -it deployment/cosmic-council-api -n cosmic-council -- \
  python -c "import psycopg2; print('Connected')"
```

#### Performance Issues
```bash
# Check resource usage
kubectl top pods -n cosmic-council
kubectl top nodes

# Check metrics
curl http://localhost:9090/metrics
```

### Debug Commands

```bash
# Service status
kubectl get all -n cosmic-council

# Network connectivity
kubectl run test-pod --image=busybox -it --rm -- nslookup postgres-service

# Port forwarding for debugging
kubectl port-forward service/cosmic-council-api-service 8000:8000 -n cosmic-council
```

## Maintenance

### Updates

```bash
# Update application
kubectl set image deployment/cosmic-council-api api=cosmic-council:v2.0.0 -n cosmic-council

# Check rollout status
kubectl rollout status deployment/cosmic-council-api -n cosmic-council

# Rollback if needed
kubectl rollout undo deployment/cosmic-council-api -n cosmic-council
```

### Health Checks

```bash
# Run health check script
./scripts/health-check.sh

# Check service health
kubectl get endpoints -n cosmic-council
```

### Log Management

```bash
# View logs
kubectl logs -f deployment/cosmic-council-api -n cosmic-council

# Archive old logs
kubectl apply -f k8s/log-rotation.yaml
```

## Support and Resources

### Documentation
- [User Guide](docs/user-guides/getting-started.md)
- [API Documentation](docs/api-documentation.md)
- [Docker Deployment](docs/deployment/docker-deployment.md)
- [Kubernetes Deployment](docs/deployment/kubernetes-deployment.md)

### Community
- [GitHub Repository](https://github.com/your-org/cosmic-council)
- [Discord Community](https://discord.gg/cosmic-council)
- [Issue Tracker](https://github.com/your-org/cosmic-council/issues)

### Support
- **Email**: support@cosmic-council.org
- **Documentation**: https://docs.cosmic-council.org
- **Status Page**: https://status.cosmic-council.org

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
