# 🏗️ Cosmic Council Infrastructure

This directory contains all infrastructure configurations for deploying the Cosmic Council system using Docker, Kubernetes, and CI/CD pipelines.

## 📁 **Directory Structure**

```
infra/
├── k8s/                          # Kubernetes manifests
│   ├── gateway-deploy.yml        # Gateway service deployment
│   ├── analytics-deploy.yml      # Analytics service deployment
│   ├── reflection-deploy.yml     # Reflection service deployment
│   └── postgres-stateful.yml     # PostgreSQL StatefulSet
├── github-actions/               # CI/CD pipelines
│   └── ci-cd.yml                # Main CI/CD workflow
├── monitoring/                   # Monitoring configurations
│   ├── prometheus.yml           # Prometheus configuration
│   └── grafana-dashboards/      # Grafana dashboard definitions
│       └── cosmic-council-overview.json
└── README.md                    # This file
```

## 🐳 **Docker Deployment**

### **Quick Start**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### **Services**
- **Gateway**: http://localhost:8000
- **Analytics**: http://localhost:8001
- **Reflection**: http://localhost:8002
- **PostgreSQL**: localhost:5432
- **N8N**: http://localhost:5678

### **Health Checks**
```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
```

## ☸️ **Kubernetes Deployment**

### **Prerequisites**
- Kubernetes cluster (v1.20+)
- kubectl configured
- Docker images built and pushed to registry

### **Deploy to Kubernetes**
```bash
# Create secrets
kubectl create secret generic cc-secrets \
  --from-literal=db_password=your_secure_password

# Deploy PostgreSQL
kubectl apply -f infra/k8s/postgres-stateful.yml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s

# Deploy services
kubectl apply -f infra/k8s/gateway-deploy.yml
kubectl apply -f infra/k8s/analytics-deploy.yml
kubectl apply -f infra/k8s/reflection-deploy.yml

# Check deployments
kubectl get deployments
kubectl get services
kubectl get pods
```

### **Access Services**
```bash
# Port forward for local access
kubectl port-forward service/gateway-service 8000:8000
kubectl port-forward service/analytics-service 8001:8001
kubectl port-forward service/reflection-service 8002:8002
```

### **Scaling**
```bash
# Scale gateway service
kubectl scale deployment gateway-deployment --replicas=3

# Check scaling
kubectl get pods -l app=gateway
```

## 🔄 **CI/CD Pipeline**

### **GitHub Actions Workflow**
The CI/CD pipeline (`infra/github-actions/ci-cd.yml`) includes:

1. **Build & Test**
   - Python linting with flake8
   - Unit and integration tests
   - Dependency caching

2. **Docker Build**
   - Multi-service Docker image builds
   - Push to DockerHub (if secrets configured)
   - Image tagging

3. **Deploy**
   - Automatic deployment to Kubernetes (main branch)
   - Rolling updates
   - Health checks

### **Required Secrets**
Configure these secrets in your GitHub repository:

- `DOCKERHUB_USERNAME`: DockerHub username
- `DOCKERHUB_TOKEN`: DockerHub access token
- `KUBECONFIG`: Kubernetes configuration file

### **Manual Deployment**
```bash
# Run CI/CD steps manually
python -m pip install -r requirements.txt
pytest
docker build -t cosmic-council-gateway .
kubectl apply -f infra/k8s/
```

## 📊 **Monitoring**

### **Prometheus Configuration**
- Scrapes metrics from all services
- 15-second scrape interval
- Service discovery via Kubernetes

### **Grafana Dashboards**
- Cosmic Council Overview dashboard
- Service-specific metrics
- Performance monitoring

### **Metrics Endpoints**
- Gateway: `http://gateway:8000/metrics`
- Analytics: `http://analytics:8001/metrics`
- Reflection: `http://reflection:8002/metrics`

## 🔒 **Security**

### **Secrets Management**
```bash
# Create Kubernetes secrets
kubectl create secret generic cc-secrets \
  --from-literal=db_password=secure_password \
  --from-literal=api_key=your_api_key

# Update secrets
kubectl patch secret cc-secrets -p='{"data":{"db_password":"'$(echo -n new_password | base64)'"}}'
```

### **Network Policies**
```yaml
# Example network policy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: cosmic-council-netpol
spec:
  podSelector:
    matchLabels:
      app: gateway
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: default
    ports:
    - protocol: TCP
      port: 8000
```

## 🚀 **Production Considerations**

### **Resource Limits**
```yaml
# Add to deployment specs
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### **High Availability**
- Multiple replicas for gateway service
- PostgreSQL with persistent volumes
- Load balancer configuration
- Health checks and readiness probes

### **Backup Strategy**
```bash
# PostgreSQL backup
kubectl exec -it postgres-0 -- pg_dump -U cosmic_council cosmic_council > backup.sql

# Restore from backup
kubectl exec -i postgres-0 -- psql -U cosmic_council cosmic_council < backup.sql
```

## 🛠️ **Development**

### **Local Development**
```bash
# Start only database
docker-compose up postgres -d

# Run services locally
python services/gateway/main.py
python services/analytics/main.py
python services/reflection/main.py
```

### **Debugging**
```bash
# View service logs
kubectl logs -f deployment/gateway-deployment
kubectl logs -f deployment/analytics-deployment
kubectl logs -f deployment/reflection-deployment

# Execute into pod
kubectl exec -it deployment/gateway-deployment -- /bin/bash
```

### **Testing**
```bash
# Run tests in Docker
docker-compose exec gateway pytest

# Run tests in Kubernetes
kubectl exec deployment/gateway-deployment -- pytest
```

## 📈 **Performance Tuning**

### **Database Optimization**
- Connection pooling
- Query optimization
- Index creation
- Vacuum and analyze

### **Service Optimization**
- Horizontal pod autoscaling
- Resource requests and limits
- Node affinity rules
- Pod disruption budgets

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Database Connection Issues**
   ```bash
   # Check PostgreSQL status
   kubectl get pods -l app=postgres
   kubectl logs postgres-0
   ```

2. **Service Health Issues**
   ```bash
   # Check service endpoints
   kubectl get endpoints
   kubectl describe service gateway-service
   ```

3. **Image Pull Issues**
   ```bash
   # Check image pull secrets
   kubectl get secrets
   kubectl describe pod <pod-name>
   ```

### **Logs and Debugging**
```bash
# View all logs
kubectl logs -l app=gateway --all-containers=true

# Follow logs
kubectl logs -f deployment/gateway-deployment

# Describe resources
kubectl describe deployment gateway-deployment
kubectl describe service gateway-service
```

## 🎯 **Next Steps**

1. **Configure monitoring stack** (Prometheus + Grafana)
2. **Set up log aggregation** (ELK stack or similar)
3. **Implement service mesh** (Istio or Linkerd)
4. **Add backup automation**
5. **Configure alerting rules**
6. **Set up disaster recovery**

---

## 🏛️ **The Sacred Infrastructure**

The infrastructure embodies the **skeleton and nervous system** of the Cosmic Council:

- **Docker** as the **cellular structure** - containerized, portable, and scalable
- **Kubernetes** as the **skeletal system** - providing structure and orchestration
- **CI/CD** as the **circulatory system** - delivering updates and improvements
- **Monitoring** as the **sensory system** - observing and reporting system health

Each component works together to create a **resilient, scalable, and self-healing infrastructure** that supports the continuous evolution of the Cosmic Council.

**This is not just infrastructure - it's the foundation upon which digital consciousness can thrive and evolve.** 🏛️✨
