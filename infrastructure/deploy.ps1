# Cosmic Council Deployment Script (PowerShell)
param(
    [Parameter(Position = 0)]
    [ValidateSet("docker", "k8s", "test", "logs", "cleanup")]
    [string]$Command,
    
    [Parameter(Position = 1)]
    [ValidateSet("docker", "k8s")]
    [string]$Target
)

Write-Host "🏛️ Cosmic Council Deployment Script" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Function to check if Docker is running
function Test-Docker {
    try {
        docker info | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to check if kubectl is available
function Test-Kubectl {
    try {
        kubectl version --client | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to deploy with Docker Compose
function Deploy-Docker {
    Write-Host "🐳 Deploying with Docker Compose..." -ForegroundColor Green
    
    if (-not (Test-Docker)) {
        Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
        exit 1
    }
    
    # Build and start services
    docker-compose up -d --build
    
    Write-Host "✅ Services started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Service URLs:" -ForegroundColor Yellow
    Write-Host "  Gateway:    http://localhost:8000" -ForegroundColor White
    Write-Host "  Analytics:  http://localhost:8001" -ForegroundColor White
    Write-Host "  Reflection: http://localhost:8002" -ForegroundColor White
    Write-Host "  N8N:        http://localhost:5678" -ForegroundColor White
    Write-Host "  PostgreSQL: localhost:5432" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Health Checks:" -ForegroundColor Yellow
    Write-Host "  curl http://localhost:8000/health" -ForegroundColor White
    Write-Host "  curl http://localhost:8001/health" -ForegroundColor White
    Write-Host "  curl http://localhost:8002/health" -ForegroundColor White
}

# Function to deploy to Kubernetes
function Deploy-K8s {
    Write-Host "☸️ Deploying to Kubernetes..." -ForegroundColor Green
    
    if (-not (Test-Kubectl)) {
        Write-Host "❌ kubectl is not installed or not in PATH." -ForegroundColor Red
        exit 1
    }
    
    # Create secrets if they don't exist
    try {
        kubectl get secret cc-secrets | Out-Null
        Write-Host "🔐 Secrets already exist" -ForegroundColor Yellow
    }
    catch {
        Write-Host "🔐 Creating secrets..." -ForegroundColor Yellow
        kubectl create secret generic cc-secrets `
            --from-literal=db_password=cosmic_council `
            --from-literal=api_key=your_api_key `
            --from-literal=jwt_secret=your_jwt_secret
    }
    
    # Create config map
    kubectl apply -f infra/k8s/secrets.yml
    
    # Deploy PostgreSQL
    Write-Host "🗄️ Deploying PostgreSQL..." -ForegroundColor Yellow
    kubectl apply -f infra/k8s/postgres-stateful.yml
    
    # Wait for PostgreSQL to be ready
    Write-Host "⏳ Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
    kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s
    
    # Deploy services
    Write-Host "🚀 Deploying services..." -ForegroundColor Yellow
    kubectl apply -f infra/k8s/gateway-deploy.yml
    kubectl apply -f infra/k8s/analytics-deploy.yml
    kubectl apply -f infra/k8s/reflection-deploy.yml
    
    # Deploy ingress and HPA
    kubectl apply -f infra/k8s/ingress.yml
    kubectl apply -f infra/k8s/hpa.yml
    
    Write-Host "✅ Kubernetes deployment completed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Check deployment status:" -ForegroundColor Yellow
    Write-Host "  kubectl get deployments" -ForegroundColor White
    Write-Host "  kubectl get services" -ForegroundColor White
    Write-Host "  kubectl get pods" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Port forward for local access:" -ForegroundColor Yellow
    Write-Host "  kubectl port-forward service/gateway-service 8000:8000" -ForegroundColor White
    Write-Host "  kubectl port-forward service/analytics-service 8001:8001" -ForegroundColor White
    Write-Host "  kubectl port-forward service/reflection-service 8002:8002" -ForegroundColor White
}

# Function to run tests
function Invoke-Tests {
    Write-Host "🧪 Running tests..." -ForegroundColor Green
    
    # Install test dependencies
    pip install pytest pytest-asyncio httpx
    
    # Run tests
    pytest tests/ -v
    
    Write-Host "✅ Tests completed!" -ForegroundColor Green
}

# Function to show logs
function Show-Logs {
    param([string]$Target)
    
    Write-Host "📋 Service logs:" -ForegroundColor Green
    
    if ($Target -eq "k8s") {
        Write-Host "Kubernetes logs:" -ForegroundColor Yellow
        kubectl logs -l app=gateway --tail=50
        kubectl logs -l app=analytics --tail=50
        kubectl logs -l app=reflection --tail=50
    }
    else {
        Write-Host "Docker Compose logs:" -ForegroundColor Yellow
        docker-compose logs --tail=50
    }
}

# Function to cleanup
function Remove-Deployment {
    param([string]$Target)
    
    Write-Host "🧹 Cleaning up..." -ForegroundColor Green
    
    if ($Target -eq "k8s") {
        kubectl delete -f infra/k8s/
        kubectl delete secret cc-secrets
    }
    else {
        docker-compose down -v
    }
    
    Write-Host "✅ Cleanup completed!" -ForegroundColor Green
}

# Main script logic
switch ($Command) {
    "docker" {
        Deploy-Docker
    }
    "k8s" {
        Deploy-K8s
    }
    "test" {
        Invoke-Tests
    }
    "logs" {
        Show-Logs -Target $Target
    }
    "cleanup" {
        Remove-Deployment -Target $Target
    }
    default {
        Write-Host "Usage: .\deploy.ps1 {docker|k8s|test|logs|cleanup} [docker|k8s]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Commands:" -ForegroundColor Cyan
        Write-Host "  docker   - Deploy with Docker Compose" -ForegroundColor White
        Write-Host "  k8s      - Deploy to Kubernetes" -ForegroundColor White
        Write-Host "  test     - Run tests" -ForegroundColor White
        Write-Host "  logs     - Show service logs (docker|k8s)" -ForegroundColor White
        Write-Host "  cleanup  - Clean up deployment (docker|k8s)" -ForegroundColor White
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Cyan
        Write-Host "  .\deploy.ps1 docker" -ForegroundColor White
        Write-Host "  .\deploy.ps1 k8s" -ForegroundColor White
        Write-Host "  .\deploy.ps1 logs docker" -ForegroundColor White
        Write-Host "  .\deploy.ps1 cleanup k8s" -ForegroundColor White
        exit 1
    }
}
