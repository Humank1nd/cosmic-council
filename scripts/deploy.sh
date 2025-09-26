#!/bin/bash

# Cosmic Council Framework Deployment Script
# This script handles deployment to different environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT=${1:-development}
ACTION=${2:-deploy}

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check kubectl for Kubernetes deployment
    if [[ "$ENVIRONMENT" == "production" || "$ENVIRONMENT" == "staging" ]]; then
        if ! command -v kubectl &> /dev/null; then
            log_error "kubectl is not installed. Please install kubectl first."
            exit 1
        fi
    fi
    
    log_success "All dependencies are installed."
}

build_image() {
    log_info "Building Docker image..."
    
    cd "$PROJECT_ROOT"
    
    # Build the image
    docker build -t cosmic-council:latest .
    
    # Tag for different environments
    case $ENVIRONMENT in
        development)
            docker tag cosmic-council:latest cosmic-council:dev
            ;;
        staging)
            docker tag cosmic-council:latest cosmic-council:staging
            ;;
        production)
            docker tag cosmic-council:latest cosmic-council:prod
            ;;
    esac
    
    log_success "Docker image built successfully."
}

deploy_docker_compose() {
    log_info "Deploying with Docker Compose..."
    
    cd "$PROJECT_ROOT"
    
    # Create .env file if it doesn't exist
    if [[ ! -f .env ]]; then
        log_info "Creating .env file..."
        cat > .env << EOF
# Cosmic Council Framework Environment Variables
POSTGRES_PASSWORD=cosmic_council_password
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GRAFANA_PASSWORD=admin
EOF
        log_warning "Please update the .env file with your actual values."
    fi
    
    # Deploy based on environment
    case $ENVIRONMENT in
        development)
            docker-compose -f docker-compose.dev.yml up -d
            ;;
        production)
            docker-compose up -d
            ;;
        *)
            log_error "Unknown environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
    
    log_success "Docker Compose deployment completed."
}

deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    cd "$PROJECT_ROOT/k8s"
    
    # Apply namespace
    kubectl apply -f namespace.yaml
    
    # Apply secrets
    kubectl apply -f secrets.yaml
    
    # Apply configmap
    kubectl apply -f configmap.yaml
    
    # Apply database
    kubectl apply -f postgres.yaml
    kubectl apply -f redis.yaml
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres -n cosmic-council --timeout=300s
    kubectl wait --for=condition=ready pod -l app=redis -n cosmic-council --timeout=300s
    
    # Apply applications
    kubectl apply -f api.yaml
    kubectl apply -f web.yaml
    
    # Apply ingress
    kubectl apply -f ingress.yaml
    
    # Wait for deployments to be ready
    log_info "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available deployment/cosmic-council-api -n cosmic-council --timeout=300s
    kubectl wait --for=condition=available deployment/cosmic-council-web -n cosmic-council --timeout=300s
    
    log_success "Kubernetes deployment completed."
}

health_check() {
    log_info "Running health checks..."
    
    case $ENVIRONMENT in
        development)
            # Check Docker Compose services
            if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
                log_success "Development services are running."
            else
                log_error "Some development services are not running."
                exit 1
            fi
            ;;
        production)
            # Check Docker Compose services
            if docker-compose ps | grep -q "Up"; then
                log_success "Production services are running."
            else
                log_error "Some production services are not running."
                exit 1
            fi
            ;;
        staging|production)
            # Check Kubernetes services
            if kubectl get pods -n cosmic-council | grep -q "Running"; then
                log_success "Kubernetes services are running."
            else
                log_error "Some Kubernetes services are not running."
                exit 1
            fi
            ;;
    esac
}

cleanup() {
    log_info "Cleaning up..."
    
    case $ENVIRONMENT in
        development)
            docker-compose -f docker-compose.dev.yml down
            ;;
        production)
            docker-compose down
            ;;
        staging|production)
            kubectl delete namespace cosmic-council --ignore-not-found=true
            ;;
    esac
    
    log_success "Cleanup completed."
}

show_status() {
    log_info "Showing deployment status..."
    
    case $ENVIRONMENT in
        development)
            docker-compose -f docker-compose.dev.yml ps
            ;;
        production)
            docker-compose ps
            ;;
        staging|production)
            kubectl get pods -n cosmic-council
            kubectl get services -n cosmic-council
            kubectl get ingress -n cosmic-council
            ;;
    esac
}

show_logs() {
    log_info "Showing logs..."
    
    case $ENVIRONMENT in
        development)
            docker-compose -f docker-compose.dev.yml logs -f
            ;;
        production)
            docker-compose logs -f
            ;;
        staging|production)
            kubectl logs -f deployment/cosmic-council-api -n cosmic-council
            kubectl logs -f deployment/cosmic-council-web -n cosmic-council
            ;;
    esac
}

# Main script
main() {
    log_info "Cosmic Council Framework Deployment Script"
    log_info "Environment: $ENVIRONMENT"
    log_info "Action: $ACTION"
    
    case $ACTION in
        deploy)
            check_dependencies
            build_image
            
            if [[ "$ENVIRONMENT" == "staging" || "$ENVIRONMENT" == "production" ]]; then
                deploy_kubernetes
            else
                deploy_docker_compose
            fi
            
            health_check
            show_status
            ;;
        cleanup)
            cleanup
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        health)
            health_check
            ;;
        *)
            log_error "Unknown action: $ACTION"
            echo "Usage: $0 [environment] [action]"
            echo "Environments: development, staging, production"
            echo "Actions: deploy, cleanup, status, logs, health"
            exit 1
            ;;
    esac
    
    log_success "Deployment script completed successfully."
}

# Run main function
main "$@"
