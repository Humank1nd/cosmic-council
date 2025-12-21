# Cosmic Council Framework Deployment Guide

## Overview

This guide covers deploying the Cosmic Council Framework in various environments, from development to production. We'll cover Docker containers, Kubernetes orchestration, and CI/CD pipelines.

## Prerequisites

- Docker 20.10+
- Kubernetes 1.21+
- kubectl configured
- Helm 3.0+
- PostgreSQL 13+
- Redis 6.0+

## Quick Start with Docker

### 1. Clone and Build

```bash
# Clone the repository
git clone https://github.com/cosmic-council/framework.git
cd cosmic-council-framework

# Build the Docker image
docker build -t cosmic-council:latest .
```

### 2. Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Access the Application

- **Web Interface**: http://localhost:8001
- **API**: http://localhost:8000
- **Database**: localhost:5432
- **Redis**: localhost:6379

## Environment variables and secrets

Every deployment surface in this repo derives its runtime configuration from an `.env` file generated from `.env.example`. This keeps credentials out of source control while still providing fallback defaults when you run the stacks locally.

- `docker-compose.yml` reads `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` for the managed Postgres instance and exposes the application-side settings via `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD`.
- `docker-compose.dev.yml` is driven by the `DEV_*` overrides (`DEV_POSTGRES_*`, `DEV_DATABASE_URL`, `DEV_PERPETUAL_DATABASE_URL`, etc.) so you can tailor development credentials without touching production values.
- Always keep `.env` out of the repo (`.gitignore` already ignores it) and rotate `POSTGRES_PASSWORD` / `DB_PASSWORD` before promoting to a shared environment. The `.env.example` file lists the current recommendations for each key.

### CI/CD secrets

The GitHub workflows that run after a release depend on repository secrets to post updates to social platforms:

  * `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`
  * `REDDIT_USERNAME`, `REDDIT_PASSWORD`, `REDDIT_APP_ID`, `REDDIT_APP_SECRET`

Configure those values in _Settings > Secrets and variables > Actions_ so that the release workflow can publish announcements without exposing credentials in the repo.

## Production Deployment with Kubernetes

### 1. Prepare Kubernetes Cluster

```bash
# Create namespace
kubectl create namespace cosmic-council

# Create secrets
kubectl create secret generic cosmic-council-secrets \
  --from-literal=database-url="postgresql://user:password@postgres:5432/cosmic_council" \
  --from-literal=redis-url="redis://redis:6379" \
  --from-literal=openai-api-key="your-openai-key" \
  --from-literal=anthropic-api-key="your-anthropic-key" \
  --namespace=cosmic-council
```

### 2. Deploy with Helm

```bash
# Add Helm repository
helm repo add cosmic-council https://charts.cosmic-council.org
helm repo update

# Install the chart
helm install cosmic-council cosmic-council/cosmic-council \
  --namespace cosmic-council \
  --set image.tag=latest \
  --set ingress.enabled=true \
  --set ingress.host=cosmic-council.yourdomain.com \
  --set database.enabled=true \
  --set redis.enabled=true
```

### 3. Verify Deployment

```bash
# Check pods
kubectl get pods -n cosmic-council

# Check services
kubectl get services -n cosmic-council

# Check ingress
kubectl get ingress -n cosmic-council
```

## Environment Configuration

### Development Environment

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  cosmic-council:
    build: .
    ports:
      - "8000:8000"
      - "8001:8001"
    environment:
      - ENVIRONMENT=development
      - LOG_LEVEL=DEBUG
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/cosmic_council_dev
      - REDIS_URL=redis://redis:6379
    volumes:
      - .:/app
      - /app/node_modules
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=cosmic_council_dev
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Staging Environment

```yaml
# k8s/staging/values.yaml
image:
  repository: cosmic-council
  tag: staging
  pullPolicy: Always

replicaCount: 2

resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

ingress:
  enabled: true
  host: staging.cosmic-council.yourdomain.com
  tls:
    enabled: true
    secretName: cosmic-council-staging-tls

database:
  enabled: true
  size: 20Gi
  storageClass: fast-ssd

redis:
  enabled: true
  size: 5Gi
```

### Production Environment

```yaml
# k8s/production/values.yaml
image:
  repository: cosmic-council
  tag: v1.0.0
  pullPolicy: Always

replicaCount: 5

resources:
  limits:
    cpu: 2000m
    memory: 4Gi
  requests:
    cpu: 1000m
    memory: 2Gi

autoscaling:
  enabled: true
  minReplicas: 5
  maxReplicas: 50
  targetCPUUtilizationPercentage: 60

ingress:
  enabled: true
  host: cosmic-council.yourdomain.com
  tls:
    enabled: true
    secretName: cosmic-council-prod-tls
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"

database:
  enabled: true
  size: 100Gi
  storageClass: fast-ssd
  backup:
    enabled: true
    schedule: "0 2 * * *"
    retention: "30d"

redis:
  enabled: true
  size: 20Gi
  persistence:
    enabled: true

monitoring:
  enabled: true
  prometheus:
    enabled: true
  grafana:
    enabled: true

logging:
  enabled: true
  level: INFO
  format: json
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy Cosmic Council

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
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
          python -m pytest tests/ --cov=src/ --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/staging'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/staging'
    environment: staging
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}
      
      - name: Deploy to staging
        run: |
          helm upgrade --install cosmic-council-staging ./helm/cosmic-council \
            --namespace cosmic-council-staging \
            --create-namespace \
            --set image.tag=staging \
            --set ingress.host=staging.cosmic-council.yourdomain.com

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_PRODUCTION }}
      
      - name: Deploy to production
        run: |
          helm upgrade --install cosmic-council ./helm/cosmic-council \
            --namespace cosmic-council \
            --create-namespace \
            --set image.tag=latest \
            --set ingress.host=cosmic-council.yourdomain.com
```

### Helm Chart Structure

```
helm/cosmic-council/
├── Chart.yaml
├── values.yaml
├── values-staging.yaml
├── values-production.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── pvc.yaml
│   └── hpa.yaml
└── charts/
```

## Monitoring and Observability

### Prometheus Configuration

```yaml
# monitoring/prometheus-config.yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'cosmic-council'
    static_configs:
      - targets: ['cosmic-council:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Cosmic Council Framework",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(cosmic_council_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(cosmic_council_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(cosmic_council_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      }
    ]
  }
}
```

## Security Configuration

### Network Policies

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: cosmic-council-network-policy
  namespace: cosmic-council
spec:
  podSelector:
    matchLabels:
      app: cosmic-council
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
    - protocol: TCP
      port: 8001
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: cosmic-council
    ports:
    - protocol: TCP
      port: 5432
    - protocol: TCP
      port: 6379
```

### Pod Security Policy

```yaml
# k8s/pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: cosmic-council-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

## Backup and Disaster Recovery

### Database Backup

```bash
#!/bin/bash
# scripts/backup-database.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="cosmic_council_backup_${DATE}.sql"

# Create backup
kubectl exec -n cosmic-council postgres-0 -- pg_dump -U postgres cosmic_council > "${BACKUP_DIR}/${BACKUP_FILE}"

# Compress backup
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

# Upload to S3
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}.gz" s3://cosmic-council-backups/

# Clean up old backups (keep 30 days)
find "${BACKUP_DIR}" -name "cosmic_council_backup_*.sql.gz" -mtime +30 -delete
```

### Disaster Recovery Plan

1. **RTO (Recovery Time Objective)**: 4 hours
2. **RPO (Recovery Point Objective)**: 1 hour

#### Recovery Steps

```bash
# 1. Restore database
kubectl exec -n cosmic-council postgres-0 -- psql -U postgres -d cosmic_council < backup.sql

# 2. Restart services
kubectl rollout restart deployment/cosmic-council -n cosmic-council

# 3. Verify recovery
kubectl get pods -n cosmic-council
kubectl logs -f deployment/cosmic-council -n cosmic-council
```

## Performance Optimization

### Resource Limits

```yaml
# k8s/resource-limits.yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: cosmic-council-limits
  namespace: cosmic-council
spec:
  limits:
  - default:
      cpu: 1000m
      memory: 2Gi
    defaultRequest:
      cpu: 500m
      memory: 1Gi
    type: Container
```

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: cosmic-council-hpa
  namespace: cosmic-council
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: cosmic-council
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Troubleshooting

### Common Issues

#### 1. Pod CrashLoopBackOff

```bash
# Check pod logs
kubectl logs -f pod/cosmic-council-xxx -n cosmic-council

# Check pod description
kubectl describe pod cosmic-council-xxx -n cosmic-council

# Check resource usage
kubectl top pod cosmic-council-xxx -n cosmic-council
```

#### 2. Database Connection Issues

```bash
# Check database status
kubectl get pods -n cosmic-council | grep postgres

# Check database logs
kubectl logs -f postgres-0 -n cosmic-council

# Test database connection
kubectl exec -it postgres-0 -n cosmic-council -- psql -U postgres -d cosmic_council
```

#### 3. High Memory Usage

```bash
# Check memory usage
kubectl top pods -n cosmic-council

# Check memory limits
kubectl describe pod cosmic-council-xxx -n cosmic-council | grep -A 5 "Limits:"

# Adjust resource limits
kubectl patch deployment cosmic-council -n cosmic-council -p '{"spec":{"template":{"spec":{"containers":[{"name":"cosmic-council","resources":{"limits":{"memory":"4Gi"}}}]}}}}'
```

## Support

For deployment support:

- **Documentation**: [docs.cosmic-council.org/deployment](https://docs.cosmic-council.org/deployment)
- **Issue Tracker**: [GitHub Issues](https://github.com/cosmic-council/framework/issues)
- **Email Support**: deployment-support@cosmic-council.org
- **Community Forum**: [community.cosmic-council.org](https://community.cosmic-council.org)
