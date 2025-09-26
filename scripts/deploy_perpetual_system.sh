#!/bin/bash

# Deploy Perpetual Thinking System
# This script deploys the perpetual thinking system components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="cosmic-council"
DEPLOYMENT_TYPE="${1:-docker}"  # docker, k8s, or both

echo -e "${BLUE}🔄 Deploying Perpetual Thinking System${NC}"
echo "=================================="

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    if [ "$DEPLOYMENT_TYPE" = "docker" ] || [ "$DEPLOYMENT_TYPE" = "both" ]; then
        if ! command -v docker &> /dev/null; then
            print_error "Docker is not installed"
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            print_error "Docker Compose is not installed"
            exit 1
        fi
        
        print_status "Docker and Docker Compose are available"
    fi
    
    if [ "$DEPLOYMENT_TYPE" = "k8s" ] || [ "$DEPLOYMENT_TYPE" = "both" ]; then
        if ! command -v kubectl &> /dev/null; then
            print_error "kubectl is not installed"
            exit 1
        fi
        
        if ! kubectl cluster-info &> /dev/null; then
            print_error "Kubernetes cluster is not accessible"
            exit 1
        fi
        
        print_status "Kubernetes cluster is accessible"
    fi
}

# Function to deploy with Docker
deploy_docker() {
    echo -e "${BLUE}🐳 Deploying with Docker...${NC}"
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        print_warning ".env file not found, creating from template"
        cat > .env << EOF
# Database Configuration
POSTGRES_PASSWORD=cosmic_council_password

# API Keys
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Perpetual Thinking System Configuration
PERPETUAL_AI_PROVIDER=openai
PERPETUAL_AI_MODEL=gpt-4
PERPETUAL_AI_TEMPERATURE=0.7
PERPETUAL_AI_MAX_TOKENS=2000
PERPETUAL_MAX_CONCURRENT_SESSIONS=10
PERPETUAL_SESSION_TIMEOUT=3600

# Security
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here

# Monitoring
GRAFANA_PASSWORD=admin
EOF
        print_warning "Please update .env file with your actual API keys and secrets"
    fi
    
    # Build and start services
    echo "Building Docker images..."
    docker-compose build
    
    echo "Starting services..."
    docker-compose up -d
    
    # Wait for services to be healthy
    echo "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    if docker-compose ps | grep -q "Up (healthy)"; then
        print_status "Docker services are running and healthy"
    else
        print_error "Some Docker services are not healthy"
        docker-compose ps
        exit 1
    fi
    
    echo -e "${GREEN}🎉 Docker deployment completed successfully!${NC}"
    echo "Services available at:"
    echo "  - API: http://localhost:8000"
    echo "  - Web Interface: http://localhost:8001"
    echo "  - Grafana: http://localhost:3000 (admin/admin)"
    echo "  - Prometheus: http://localhost:9090"
}

# Function to deploy with Kubernetes
deploy_k8s() {
    echo -e "${BLUE}☸️  Deploying with Kubernetes...${NC}"
    
    # Create namespace if it doesn't exist
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        echo "Creating namespace: $NAMESPACE"
        kubectl create namespace $NAMESPACE
    fi
    
    # Apply Kubernetes manifests
    echo "Applying Kubernetes manifests..."
    
    # Apply namespace
    kubectl apply -f k8s/namespace.yaml
    
    # Apply secrets (create if not exists)
    if ! kubectl get secret cosmic-council-secrets -n $NAMESPACE &> /dev/null; then
        print_warning "Creating secrets from environment variables"
        kubectl create secret generic cosmic-council-secrets \
            --from-literal=DATABASE_PASSWORD="${POSTGRES_PASSWORD:-cosmic_council_password}" \
            --from-literal=SECRET_KEY="${SECRET_KEY:-your-secret-key-here}" \
            --from-literal=API_KEY="${API_KEY:-your-api-key-here}" \
            --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY:-your-openai-api-key-here}" \
            --from-literal=ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-your-anthropic-api-key-here}" \
            --from-literal=JWT_SECRET="${JWT_SECRET:-your-jwt-secret-here}" \
            --from-literal=JWT_ALGORITHM="${JWT_ALGORITHM:-HS256}" \
            --from-literal=JWT_EXPIRATION="${JWT_EXPIRATION:-3600}" \
            -n $NAMESPACE
    fi
    
    # Apply configmap
    kubectl apply -f k8s/configmap.yaml
    
    # Apply database services
    kubectl apply -f k8s/postgres.yaml
    kubectl apply -f k8s/postgres-perpetual.yaml
    kubectl apply -f k8s/redis.yaml
    
    # Wait for databases to be ready
    echo "Waiting for databases to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app=postgres-perpetual -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s
    
    # Apply API and web services
    kubectl apply -f k8s/api.yaml
    kubectl apply -f k8s/web.yaml
    
    # Apply ingress
    kubectl apply -f k8s/ingress.yaml
    
    # Wait for services to be ready
    echo "Waiting for services to be ready..."
    kubectl wait --for=condition=ready pod -l app=cosmic-council-api -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app=cosmic-council-web -n $NAMESPACE --timeout=300s
    
    print_status "Kubernetes deployment completed successfully!"
    
    # Get service URLs
    echo "Services available at:"
    kubectl get services -n $NAMESPACE
}

# Function to run tests
run_tests() {
    echo -e "${BLUE}🧪 Running perpetual thinking system tests...${NC}"
    
    if [ -f "run_perpetual_tests.py" ]; then
        python run_perpetual_tests.py --all
    else
        print_warning "Perpetual tests not found, running general tests"
        python run_tests.py --type perpetual
    fi
}

# Function to show deployment status
show_status() {
    echo -e "${BLUE}📊 Deployment Status${NC}"
    echo "=================="
    
    if [ "$DEPLOYMENT_TYPE" = "docker" ] || [ "$DEPLOYMENT_TYPE" = "both" ]; then
        echo -e "${YELLOW}Docker Services:${NC}"
        docker-compose ps
        echo
    fi
    
    if [ "$DEPLOYMENT_TYPE" = "k8s" ] || [ "$DEPLOYMENT_TYPE" = "both" ]; then
        echo -e "${YELLOW}Kubernetes Services:${NC}"
        kubectl get pods -n $NAMESPACE
        echo
        kubectl get services -n $NAMESPACE
    fi
}

# Function to show logs
show_logs() {
    echo -e "${BLUE}📋 Recent Logs${NC}"
    echo "============="
    
    if [ "$DEPLOYMENT_TYPE" = "docker" ] || [ "$DEPLOYMENT_TYPE" = "both" ]; then
        echo -e "${YELLOW}Docker Logs:${NC}"
        docker-compose logs --tail=50
    fi
    
    if [ "$DEPLOYMENT_TYPE" = "k8s" ] || [ "$DEPLOYMENT_TYPE" = "both" ]; then
        echo -e "${YELLOW}Kubernetes Logs:${NC}"
        kubectl logs -l app=cosmic-council-api -n $NAMESPACE --tail=50
    fi
}

# Main deployment function
main() {
    echo "Deployment Type: $DEPLOYMENT_TYPE"
    echo
    
    check_prerequisites
    
    if [ "$DEPLOYMENT_TYPE" = "docker" ]; then
        deploy_docker
    elif [ "$DEPLOYMENT_TYPE" = "k8s" ]; then
        deploy_k8s
    elif [ "$DEPLOYMENT_TYPE" = "both" ]; then
        deploy_docker
        deploy_k8s
    else
        print_error "Invalid deployment type. Use: docker, k8s, or both"
        exit 1
    fi
    
    # Run tests
    if [ "$2" = "--test" ]; then
        run_tests
    fi
    
    # Show status
    show_status
    
    echo -e "${GREEN}🎉 Perpetual Thinking System deployment completed!${NC}"
    echo
    echo "Next steps:"
    echo "1. Update your .env file with actual API keys"
    echo "2. Access the web interface to start perpetual thinking sessions"
    echo "3. Monitor the system using Grafana dashboards"
    echo "4. Check logs if you encounter any issues"
    echo
    echo "For more information, see the README files in the docs/ directory"
}

# Handle command line arguments
case "${1:-}" in
    "docker")
        DEPLOYMENT_TYPE="docker"
        ;;
    "k8s")
        DEPLOYMENT_TYPE="k8s"
        ;;
    "both")
        DEPLOYMENT_TYPE="both"
        ;;
    "status")
        show_status
        exit 0
        ;;
    "logs")
        show_logs
        exit 0
        ;;
    "test")
        run_tests
        exit 0
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [deployment_type] [options]"
        echo
        echo "Deployment Types:"
        echo "  docker    Deploy using Docker Compose"
        echo "  k8s       Deploy using Kubernetes"
        echo "  both      Deploy using both Docker and Kubernetes"
        echo
        echo "Options:"
        echo "  --test    Run tests after deployment"
        echo
        echo "Commands:"
        echo "  status    Show deployment status"
        echo "  logs      Show recent logs"
        echo "  test      Run perpetual thinking system tests"
        echo "  help      Show this help message"
        echo
        echo "Examples:"
        echo "  $0 docker --test"
        echo "  $0 k8s"
        echo "  $0 both"
        echo "  $0 status"
        exit 0
        ;;
esac

# Run main function
main "$@"
