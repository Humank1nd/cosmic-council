# Kubernetes Deployment Guide

## Overview

This guide covers deploying the Cosmic Council Framework using Kubernetes. Kubernetes provides a robust, scalable, and production-ready deployment solution with advanced features like auto-scaling, rolling updates, and service discovery.

## Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured to access your cluster
- At least 4 nodes with 4GB RAM each
- Persistent volume support
- Ingress controller (nginx, traefik, etc.)
- cert-manager for SSL certificates (optional)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/cosmic-council.git
cd cosmic-council
```

### 2. Configure Secrets

Create a secrets file with your sensitive data:

```bash
# Create secrets
kubectl create secret generic cosmic-council-secrets \
  --from-literal=DATABASE_PASSWORD=your_secure_password \
  --from-literal=SECRET_KEY=your_secret_key \
  --from-literal=API_KEY=your_api_key \
  --from-literal=OPENAI_API_KEY=your_openai_key \
  --from-literal=ANTHROPIC_API_KEY=your_anthropic_key \
  --from-literal=GRAFANA_PASSWORD=your_grafana_password \
  --namespace=cosmic-council
```

### 3. Deploy to Kubernetes

```bash
# Apply all Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n cosmic-council
kubectl get services -n cosmic-council
kubectl get ingress -n cosmic-council
```

## Architecture Overview

### Namespace Structure

```
cosmic-council/
├── postgres (Database)
├── redis (Cache)
├── cosmic-council-api (API Service)
├── cosmic-council-web (Web Interface)
├── nginx-ingress (Load Balancer)
├── prometheus (Monitoring)
├── grafana (Dashboards)
└── elasticsearch + kibana (Logging)
```

### Service Dependencies

```
nginx-ingress
    ├── cosmic-council-web
    │   └── cosmic-council-api
    │       ├── postgres
    │       └── redis
    └── monitoring services
        ├── prometheus
        ├── grafana
        └── elasticsearch
```

## Detailed Deployment

### 1. Namespace and Configuration

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply configuration
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
```

### 2. Database Services

```bash
# Deploy PostgreSQL
kubectl apply -f k8s/postgres.yaml

# Deploy Redis
kubectl apply -f k8s/redis.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n cosmic-council --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n cosmic-council --timeout=300s
```

### 3. Application Services

```bash
# Deploy API service
kubectl apply -f k8s/api.yaml

# Deploy Web interface
kubectl apply -f k8s/web.yaml

# Wait for applications to be ready
kubectl wait --for=condition=available deployment/cosmic-council-api -n cosmic-council --timeout=300s
kubectl wait --for=condition=available deployment/cosmic-council-web -n cosmic-council --timeout=300s
```

### 4. Ingress and Networking

```bash
# Deploy ingress
kubectl apply -f k8s/ingress.yaml

# Check ingress status
kubectl get ingress -n cosmic-council
```

## Configuration Management

### ConfigMap

The ConfigMap contains non-sensitive configuration:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cosmic-council-config
  namespace: cosmic-council
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  DATABASE_HOST: "postgres-service"
  DATABASE_PORT: "5432"
  # ... other configuration
```

### Secrets

Sensitive data is stored in Kubernetes secrets:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cosmic-council-secrets
  namespace: cosmic-council
type: Opaque
data:
  DATABASE_PASSWORD: <base64-encoded>
  SECRET_KEY: <base64-encoded>
  API_KEY: <base64-encoded>
  # ... other secrets
```

## Scaling and Performance

### Horizontal Pod Autoscaler

The API service includes HPA configuration:

```yaml
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

### Resource Limits

Each service has resource requests and limits:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### Pod Disruption Budget

Ensures high availability during updates:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: cosmic-council-api-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: cosmic-council-api
```

## Monitoring and Observability

### Prometheus Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'cosmic-council-api'
      static_configs:
      - targets: ['cosmic-council-api-service:8000']
```

### Grafana Dashboards

Pre-configured dashboards for:
- Application metrics
- Database performance
- System resources
- Business metrics

### Log Aggregation

ELK stack for centralized logging:
- Elasticsearch for log storage
- Kibana for log visualization
- Logstash for log processing

## Security

### Network Policies

Restrict network traffic between pods:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: cosmic-council-network-policy
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: cosmic-council
```

### Security Context

Run containers as non-root users:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
    - ALL
```

### RBAC

Role-based access control for service accounts:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: cosmic-council-role
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
```

## SSL/TLS Configuration

### cert-manager Setup

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@cosmic-council.org
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### Ingress with SSL

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cosmic-council-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - cosmic-council.org
    secretName: cosmic-council-tls
  rules:
  - host: cosmic-council.org
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: cosmic-council-web-service
            port:
              number: 8001
```

## Backup and Disaster Recovery

### Database Backup

```bash
# Create backup job
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: cosmic-council
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:13
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h postgres-service -U cosmic_council cosmic_council > /backup/backup-$(date +%Y%m%d_%H%M%S).sql
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: cosmic-council-secrets
                  key: DATABASE_PASSWORD
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
EOF
```

### Volume Snapshots

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: postgres-snapshot
spec:
  source:
    persistentVolumeClaimName: postgres-pvc
```

## Troubleshooting

### Common Issues

#### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n cosmic-council

# Check pod logs
kubectl logs -f deployment/cosmic-council-api -n cosmic-council

# Check pod events
kubectl describe pod <pod-name> -n cosmic-council
```

#### Database Connection Issues

```bash
# Check database status
kubectl get pods -l app=postgres -n cosmic-council

# Test database connection
kubectl exec -it deployment/cosmic-council-api -n cosmic-council -- python -c "
import psycopg2
conn = psycopg2.connect('postgresql://cosmic_council:password@postgres-service:5432/cosmic_council')
print('Connected successfully')
"
```

#### Service Discovery Issues

```bash
# Check services
kubectl get services -n cosmic-council

# Test service connectivity
kubectl run test-pod --image=busybox -it --rm -- nslookup postgres-service.cosmic-council.svc.cluster.local
```

#### Resource Issues

```bash
# Check resource usage
kubectl top pods -n cosmic-council
kubectl top nodes

# Check resource quotas
kubectl describe quota -n cosmic-council
```

### Performance Optimization

#### Database Tuning

```bash
# Scale database
kubectl scale deployment postgres --replicas=2 -n cosmic-council

# Add read replicas
kubectl apply -f k8s/postgres-read-replica.yaml
```

#### Application Scaling

```bash
# Scale API service
kubectl scale deployment cosmic-council-api --replicas=5 -n cosmic-council

# Scale web service
kubectl scale deployment cosmic-council-web --replicas=3 -n cosmic-council
```

#### Cache Optimization

```bash
# Scale Redis
kubectl scale deployment redis --replicas=3 -n cosmic-council

# Configure Redis cluster
kubectl apply -f k8s/redis-cluster.yaml
```

## Maintenance

### Rolling Updates

```bash
# Update API service
kubectl set image deployment/cosmic-council-api api=cosmic-council:v2.0.0 -n cosmic-council

# Check rollout status
kubectl rollout status deployment/cosmic-council-api -n cosmic-council

# Rollback if needed
kubectl rollout undo deployment/cosmic-council-api -n cosmic-council
```

### Health Checks

```bash
# Check all deployments
kubectl get deployments -n cosmic-council

# Check service health
kubectl get endpoints -n cosmic-council

# Run health check script
./scripts/health-check-k8s.sh
```

### Log Management

```bash
# View logs
kubectl logs -f deployment/cosmic-council-api -n cosmic-council

# Archive old logs
kubectl apply -f k8s/log-rotation.yaml
```

## Production Considerations

### High Availability

- Use multiple availability zones
- Configure pod anti-affinity
- Set up database replication
- Implement circuit breakers

### Security

- Enable network policies
- Use service mesh (Istio)
- Implement secrets management
- Regular security scanning

### Monitoring

- Set up alerting rules
- Configure log aggregation
- Monitor resource usage
- Track business metrics

### Backup Strategy

- Regular database backups
- Volume snapshots
- Configuration backups
- Disaster recovery testing

## Support

For Kubernetes deployment support:
- **Documentation**: https://docs.cosmic-council.org
- **GitHub Issues**: https://github.com/your-org/cosmic-council/issues
- **Discord**: https://discord.gg/cosmic-council
- **Email**: support@cosmic-council.org