#!/bin/bash

# Cosmic Council Framework - Codex-Enhanced Deployment Script
# This script uses Codex to optimize and deploy the system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT=${1:-development}
ACTION=${2:-deploy}
CODEX_ENABLED=${3:-true}

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

log_codex() {
    echo -e "${PURPLE}[CODEX]${NC} $1"
}

check_codex_dependencies() {
    log_info "Checking Codex dependencies..."
    
    # Check if Codex CLI is installed
    if ! command -v codex &> /dev/null; then
        log_warning "Codex CLI not found. Installing..."
        npm install -g @openai/codex
    fi
    
    # Check if logged in
    if ! codex whoami &> /dev/null; then
        log_warning "Not logged into Codex. Please run: codex login --api-key YOUR_API_KEY"
        if [ -n "$OPENAI_API_KEY" ]; then
            log_info "Using OPENAI_API_KEY from environment..."
            codex login --api-key "$OPENAI_API_KEY"
        else
            log_error "No OpenAI API key found. Set OPENAI_API_KEY environment variable or run codex login"
            exit 1
        fi
    fi
    
    log_success "Codex dependencies are ready"
}

run_codex_pre_deployment() {
    if [ "$CODEX_ENABLED" = "true" ]; then
        log_codex "Running Codex pre-deployment analysis..."
        
        # Analyze codebase for deployment readiness
        codex exec --approval-policy on-failure --sandbox read-only \
            "Analyze the Cosmic Council codebase for deployment readiness. Check for:
            1. Configuration issues
            2. Missing environment variables
            3. Database migration requirements
            4. Security vulnerabilities
            5. Performance bottlenecks
            6. Missing dependencies
            
            Provide specific recommendations for the $ENVIRONMENT environment."
        
        # Optimize Docker configuration
        codex exec --approval-policy on-failure --sandbox workspace-write \
            "Review and optimize the Docker configuration for the Cosmic Council project:
            1. Analyze Dockerfile for efficiency
            2. Check docker-compose.yml for best practices
            3. Optimize image layers and caching
            4. Ensure proper health checks
            5. Review security configurations
            
            Make improvements while maintaining compatibility."
        
        log_success "Codex pre-deployment analysis completed"
    fi
}

run_codex_post_deployment() {
    if [ "$CODEX_ENABLED" = "true" ]; then
        log_codex "Running Codex post-deployment optimization..."
        
        # Generate deployment report
        codex exec --approval-policy never --sandbox read-only \
            "Generate a comprehensive deployment report for the Cosmic Council system:
            1. Deployment status and health
            2. Performance metrics analysis
            3. Resource utilization
            4. Security assessment
            5. Recommendations for improvements
            6. Monitoring and alerting suggestions
            
            Format as a detailed markdown report."
        
        # Update documentation
        codex exec --approval-policy on-failure --sandbox workspace-write \
            "Update deployment documentation based on the current deployment:
            1. Update deployment guides
            2. Add troubleshooting sections
            3. Update configuration examples
            4. Add performance tuning tips
            5. Update monitoring setup instructions"
        
        log_success "Codex post-deployment optimization completed"
    fi
}

run_codex_health_check() {
    if [ "$CODEX_ENABLED" = "true" ]; then
        log_codex "Running Codex-enhanced health checks..."
        
        # Comprehensive health analysis
        codex exec --approval-policy never --sandbox read-only \
            "Perform a comprehensive health check analysis for the Cosmic Council deployment:
            1. Analyze service status and logs
            2. Check database connectivity and performance
            3. Verify API endpoints and responses
            4. Assess resource usage and limits
            5. Check for error patterns
            6. Validate configuration consistency
            7. Test critical user workflows
            
            Provide detailed health report with recommendations."
        
        log_success "Codex health check completed"
    fi
}

run_codex_rollback_analysis() {
    if [ "$CODEX_ENABLED" = "true" ]; then
        log_codex "Running Codex rollback analysis..."
        
        # Analyze rollback requirements
        codex exec --approval-policy never --sandbox read-only \
            "Analyze the current deployment state and prepare rollback strategy:
            1. Identify critical components that need rollback
            2. Check database migration rollback requirements
            3. Analyze configuration changes
            4. Prepare rollback scripts and procedures
            5. Identify potential data consistency issues
            6. Create rollback validation checklist
            
            Provide step-by-step rollback procedure."
        
        log_success "Codex rollback analysis completed"
    fi
}

# Enhanced deployment functions with Codex integration
deploy_with_codex() {
    log_info "Starting Codex-enhanced deployment..."
    
    # Pre-deployment analysis
    run_codex_pre_deployment
    
    # Standard deployment
    case $ENVIRONMENT in
        development)
            log_info "Deploying to development environment..."
            docker-compose -f docker-compose.dev.yml up -d --build
            ;;
        staging)
            log_info "Deploying to staging environment..."
            docker-compose -f docker-compose.yml up -d --build
            ;;
        production)
            log_info "Deploying to production environment..."
            # Use Kubernetes for production
            kubectl apply -f infrastructure/k8s/
            kubectl rollout status deployment/cosmic-council-api -n cosmic-council
            kubectl rollout status deployment/cosmic-council-web -n cosmic-council
            ;;
        *)
            log_error "Unknown environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Post-deployment optimization
    run_codex_post_deployment
    
    log_success "Codex-enhanced deployment completed"
}

# Enhanced health check with Codex
health_check_with_codex() {
    log_info "Running enhanced health checks..."
    
    # Standard health checks
    case $ENVIRONMENT in
        development)
            if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
                log_success "Development services are running"
            else
                log_error "Some development services are not running"
                return 1
            fi
            ;;
        staging|production)
            if kubectl get pods -n cosmic-council | grep -q "Running"; then
                log_success "Kubernetes services are running"
            else
                log_error "Some Kubernetes services are not running"
                return 1
            fi
            ;;
    esac
    
    # Codex-enhanced health analysis
    run_codex_health_check
    
    log_success "Enhanced health checks completed"
}

# Enhanced rollback with Codex
rollback_with_codex() {
    log_info "Starting Codex-enhanced rollback..."
    
    # Analyze rollback requirements
    run_codex_rollback_analysis
    
    # Perform rollback
    case $ENVIRONMENT in
        development)
            log_info "Rolling back development environment..."
            docker-compose -f docker-compose.dev.yml down
            docker-compose -f docker-compose.dev.yml up -d
            ;;
        staging|production)
            log_info "Rolling back Kubernetes deployment..."
            kubectl rollout undo deployment/cosmic-council-api -n cosmic-council
            kubectl rollout undo deployment/cosmic-council-web -n cosmic-council
            ;;
    esac
    
    # Verify rollback
    health_check_with_codex
    
    log_success "Codex-enhanced rollback completed"
}

# Main script
main() {
    log_info "Cosmic Council Framework - Codex-Enhanced Deployment"
    log_info "Environment: $ENVIRONMENT"
    log_info "Action: $ACTION"
    log_info "Codex Enabled: $CODEX_ENABLED"
    
    # Check dependencies
    if [ "$CODEX_ENABLED" = "true" ]; then
        check_codex_dependencies
    fi
    
    case $ACTION in
        deploy)
            deploy_with_codex
            ;;
        health)
            health_check_with_codex
            ;;
        rollback)
            rollback_with_codex
            ;;
        codex-analyze)
            if [ "$CODEX_ENABLED" = "true" ]; then
                run_codex_pre_deployment
            else
                log_error "Codex is disabled. Enable with: $0 $ENVIRONMENT $ACTION true"
                exit 1
            fi
            ;;
        codex-optimize)
            if [ "$CODEX_ENABLED" = "true" ]; then
                run_codex_post_deployment
            else
                log_error "Codex is disabled. Enable with: $0 $ENVIRONMENT $ACTION true"
                exit 1
            fi
            ;;
        *)
            log_error "Unknown action: $ACTION"
            echo "Usage: $0 [environment] [action] [codex_enabled]"
            echo "Environments: development, staging, production"
            echo "Actions: deploy, health, rollback, codex-analyze, codex-optimize"
            echo "Codex: true (default) or false"
            exit 1
            ;;
    esac
    
    log_success "Codex-enhanced deployment script completed successfully"
}

# Run main function
main "$@"
