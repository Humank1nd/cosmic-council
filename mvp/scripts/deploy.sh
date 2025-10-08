#!/bin/bash
# Cosmic Council MVP - Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="cosmic-council"
DOCKER_IMAGE="cosmic-council:latest"
DOCKER_REGISTRY="your-registry.com"
NAMESPACE="cosmic-council"
REPLICAS=3

echo -e "${BLUE}🚀 Cosmic Council MVP Deployment Script${NC}"
echo "=============================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Build Docker image
build_image() {
    echo "🏗️  Building Docker image..."
    
    docker build -t $DOCKER_IMAGE .
    
    if [ $? -eq 0 ]; then
        print_status "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Run tests
run_tests() {
    echo "🧪 Running tests..."
    
    # Run unit tests
    docker run --rm -v $(pwd)/src:/app/src $DOCKER_IMAGE python src/test_phase2.py
    
    if [ $? -eq 0 ]; then
        print_status "Tests passed"
    else
        print_error "Tests failed"
        exit 1
    fi
}

# Deploy with Docker Compose
deploy_compose() {
    echo "🚀 Deploying with Docker Compose..."
    
    # Stop existing containers
    docker-compose down
    
    # Start new containers
    docker-compose up -d
    
    # Wait for health check
    echo "⏳ Waiting for services to be healthy..."
    sleep 30
    
    # Check health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Services are healthy"
    else
        print_error "Health check failed"
        docker-compose logs
        exit 1
    fi
}

# Deploy to Kubernetes (if kubectl is available)
deploy_k8s() {
    if command -v kubectl &> /dev/null; then
        echo "☸️  Deploying to Kubernetes..."
        
        # Create namespace if it doesn't exist
        kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
        
        # Apply Kubernetes manifests
        kubectl apply -f k8s/ -n $NAMESPACE
        
        # Wait for deployment
        kubectl rollout status deployment/$APP_NAME -n $NAMESPACE --timeout=300s
        
        print_status "Kubernetes deployment completed"
    else
        print_warning "kubectl not found, skipping Kubernetes deployment"
    fi
}

# Run security scan
security_scan() {
    echo "🔒 Running security scan..."
    
    if command -v trivy &> /dev/null; then
        trivy image $DOCKER_IMAGE
    else
        print_warning "Trivy not found, skipping security scan"
    fi
}

# Main deployment function
main() {
    case "${1:-compose}" in
        "compose")
            check_prerequisites
            build_image
            run_tests
            security_scan
            deploy_compose
            ;;
        "k8s")
            check_prerequisites
            build_image
            run_tests
            security_scan
            deploy_k8s
            ;;
        "test")
            check_prerequisites
            build_image
            run_tests
            ;;
        "build")
            check_prerequisites
            build_image
            ;;
        *)
            echo "Usage: $0 {compose|k8s|test|build}"
            echo "  compose - Deploy with Docker Compose (default)"
            echo "  k8s     - Deploy to Kubernetes"
            echo "  test    - Run tests only"
            echo "  build   - Build image only"
            exit 1
            ;;
    esac
    
    print_status "Deployment completed successfully!"
    echo ""
    echo "🌐 Application URLs:"
    echo "  API: http://localhost:8000"
    echo "  Docs: http://localhost:8000/docs"
    echo "  Health: http://localhost:8000/health"
    echo ""
    echo "📊 Monitoring:"
    echo "  Logs: docker-compose logs -f"
    echo "  Stats: docker stats"
}

# Run main function with all arguments
main "$@"
