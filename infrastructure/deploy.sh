#!/bin/bash

# Cosmic Council Deployment Script
set -e

echo "🏛️ Cosmic Council Deployment Script"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH."
    exit 1
fi

# Function to deploy with Docker Compose
deploy_docker() {
    echo "🐳 Deploying with Docker Compose..."
    
    # Build and start services
    docker-compose up -d --build
    
    echo "✅ Services started successfully!"
    echo ""
    echo "🌐 Service URLs:"
    echo "  Gateway:    http://localhost:8000"
    echo "  Analytics:  http://localhost:8001"
    echo "  Reflection: http://localhost:8002"
    echo "  N8N:        http://localhost:5678"
    echo "  PostgreSQL: localhost:5432"
    echo ""
    echo "📊 Health Checks:"
    echo "  curl http://localhost:8000/health"
    echo "  curl http://localhost:8001/health"
    echo "  curl http://localhost:8002/health"
}

# Function to deploy to Kubernetes
deploy_k8s() {
    echo "☸️ Deploying to Kubernetes..."
    
    # Create secrets if they don't exist
    if ! kubectl get secret cc-secrets > /dev/null 2>&1; then
        echo "🔐 Creating secrets..."
        kubectl create secret generic cc-secrets \
            --from-literal=db_password=dream_caesar \
            --from-literal=api_key=your_api_key \
            --from-literal=jwt_secret=your_jwt_secret
    fi
    
    # Create config map
    kubectl apply -f infra/k8s/secrets.yml
    
    # Deploy PostgreSQL
    echo "🗄️ Deploying PostgreSQL..."
    kubectl apply -f infra/k8s/postgres-stateful.yml
    
    # Wait for PostgreSQL to be ready
    echo "⏳ Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s
    
    # Deploy services
    echo "🚀 Deploying services..."
    kubectl apply -f infra/k8s/gateway-deploy.yml
    kubectl apply -f infra/k8s/analytics-deploy.yml
    kubectl apply -f infra/k8s/reflection-deploy.yml
    
    # Deploy ingress and HPA
    kubectl apply -f infra/k8s/ingress.yml
    kubectl apply -f infra/k8s/hpa.yml
    
    echo "✅ Kubernetes deployment completed!"
    echo ""
    echo "📊 Check deployment status:"
    echo "  kubectl get deployments"
    echo "  kubectl get services"
    echo "  kubectl get pods"
    echo ""
    echo "🌐 Port forward for local access:"
    echo "  kubectl port-forward service/gateway-service 8000:8000"
    echo "  kubectl port-forward service/analytics-service 8001:8001"
    echo "  kubectl port-forward service/reflection-service 8002:8002"
}

# Function to run tests
run_tests() {
    echo "🧪 Running tests..."
    
    # Install test dependencies
    pip install pytest pytest-asyncio httpx
    
    # Run tests
    pytest tests/ -v
    
    echo "✅ Tests completed!"
}

# Function to show logs
show_logs() {
    echo "📋 Service logs:"
    
    if [ "$1" = "k8s" ]; then
        echo "Kubernetes logs:"
        kubectl logs -l app=gateway --tail=50
        kubectl logs -l app=analytics --tail=50
        kubectl logs -l app=reflection --tail=50
    else
        echo "Docker Compose logs:"
        docker-compose logs --tail=50
    fi
}

# Function to cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    
    if [ "$1" = "k8s" ]; then
        kubectl delete -f infra/k8s/
        kubectl delete secret cc-secrets
    else
        docker-compose down -v
    fi
    
    echo "✅ Cleanup completed!"
}

# Main script logic
case "$1" in
    "docker")
        deploy_docker
        ;;
    "k8s")
        deploy_k8s
        ;;
    "test")
        run_tests
        ;;
    "logs")
        show_logs "$2"
        ;;
    "cleanup")
        cleanup "$2"
        ;;
    *)
        echo "Usage: $0 {docker|k8s|test|logs|cleanup}"
        echo ""
        echo "Commands:"
        echo "  docker   - Deploy with Docker Compose"
        echo "  k8s      - Deploy to Kubernetes"
        echo "  test     - Run tests"
        echo "  logs     - Show service logs (docker|k8s)"
        echo "  cleanup  - Clean up deployment (docker|k8s)"
        echo ""
        echo "Examples:"
        echo "  $0 docker"
        echo "  $0 k8s"
        echo "  $0 logs docker"
        echo "  $0 cleanup k8s"
        exit 1
        ;;
esac
