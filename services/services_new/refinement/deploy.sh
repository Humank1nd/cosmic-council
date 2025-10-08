#!/bin/bash

# Cosmic Council Refinement Engine - Deployment Script
# This script deploys the refinement engine using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p nginx/ssl
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    
    print_success "Directories created"
}

# Function to check environment file
check_environment() {
    print_status "Checking environment configuration..."
    
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from example..."
        if [ -f env.example ]; then
            cp env.example .env
            print_warning "Please update .env file with your actual configuration values"
        else
            print_error "env.example file not found. Cannot create .env file."
            exit 1
        fi
    fi
    
    print_success "Environment configuration checked"
}

# Function to generate SSL certificates (self-signed for development)
generate_ssl_certificates() {
    print_status "Generating SSL certificates..."
    
    if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        print_success "SSL certificates generated"
    else
        print_status "SSL certificates already exist"
    fi
}

# Function to build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Build the application
    docker-compose build
    
    # Start services
    docker-compose up -d
    
    print_success "Services started"
}

# Function to wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for database..."
    until docker-compose exec -T postgres pg_isready -U cosmic_council -d cosmic_council_db; do
        sleep 2
    done
    print_success "Database is ready"
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    until docker-compose exec -T redis redis-cli ping; do
        sleep 2
    done
    print_success "Redis is ready"
    
    # Wait for main application
    print_status "Waiting for main application..."
    until curl -f http://localhost:8000/health >/dev/null 2>&1; do
        sleep 5
    done
    print_success "Main application is ready"
    
    # Wait for monitoring
    print_status "Waiting for monitoring..."
    until curl -f http://localhost:8001/health >/dev/null 2>&1; do
        sleep 5
    done
    print_success "Monitoring is ready"
    
    # Wait for Prometheus
    print_status "Waiting for Prometheus..."
    until curl -f http://localhost:9091/-/ready >/dev/null 2>&1; do
        sleep 5
    done
    print_success "Prometheus is ready"
    
    # Wait for Grafana
    print_status "Waiting for Grafana..."
    until curl -f http://localhost:3000/api/health >/dev/null 2>&1; do
        sleep 5
    done
    print_success "Grafana is ready"
}

# Function to show deployment status
show_status() {
    print_status "Deployment Status:"
    echo ""
    
    # Show running containers
    docker-compose ps
    
    echo ""
    print_status "Service URLs:"
    echo "  Main API: http://localhost:8000"
    echo "  Monitoring API: http://localhost:8001"
    echo "  Prometheus: http://localhost:9091"
    echo "  Grafana: http://localhost:3000 (admin/admin)"
    echo "  Nginx: http://localhost"
    echo ""
    
    print_status "Health Checks:"
    echo "  Main API Health: $(curl -s http://localhost:8000/health | jq -r '.status' 2>/dev/null || echo 'Unknown')"
    echo "  Monitoring Health: $(curl -s http://localhost:8001/health | jq -r '.status' 2>/dev/null || echo 'Unknown')"
    echo ""
}

# Function to show logs
show_logs() {
    print_status "Showing recent logs..."
    docker-compose logs --tail=50
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose down
    print_success "Services stopped"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up..."
    docker-compose down -v
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "Cosmic Council Refinement Engine - Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy     Deploy the application (default)"
    echo "  start      Start existing services"
    echo "  stop       Stop services"
    echo "  restart    Restart services"
    echo "  status     Show deployment status"
    echo "  logs       Show service logs"
    echo "  cleanup    Stop services and clean up volumes"
    echo "  help       Show this help message"
    echo ""
}

# Main function
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            create_directories
            check_environment
            generate_ssl_certificates
            deploy_services
            wait_for_services
            show_status
            ;;
        "start")
            print_status "Starting services..."
            docker-compose start
            wait_for_services
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            print_status "Restarting services..."
            docker-compose restart
            wait_for_services
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "cleanup")
            cleanup
            ;;
        "help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
