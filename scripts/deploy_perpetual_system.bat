@echo off
REM Deploy Perpetual Thinking System - Windows Batch Script
REM This script deploys the perpetual thinking system components

setlocal enabledelayedexpansion

REM Configuration
set NAMESPACE=cosmic-council
set DEPLOYMENT_TYPE=%1
if "%DEPLOYMENT_TYPE%"=="" set DEPLOYMENT_TYPE=docker

echo 🔄 Deploying Perpetual Thinking System
echo ==================================

REM Function to check prerequisites
:check_prerequisites
echo 🔍 Checking prerequisites...

if "%DEPLOYMENT_TYPE%"=="docker" (
    docker --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker is not installed
        exit /b 1
    )
    
    docker-compose --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker Compose is not installed
        exit /b 1
    )
    
    echo ✅ Docker and Docker Compose are available
)

if "%DEPLOYMENT_TYPE%"=="k8s" (
    kubectl version --client >nul 2>&1
    if errorlevel 1 (
        echo ❌ kubectl is not installed
        exit /b 1
    )
    
    kubectl cluster-info >nul 2>&1
    if errorlevel 1 (
        echo ❌ Kubernetes cluster is not accessible
        exit /b 1
    )
    
    echo ✅ Kubernetes cluster is accessible
)

goto :eof

REM Function to deploy with Docker
:deploy_docker
echo 🐳 Deploying with Docker...

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found, creating from template
    (
        echo # Database Configuration
        echo POSTGRES_PASSWORD=cosmic_council_password
        echo.
        echo # API Keys
        echo OPENAI_API_KEY=your-openai-api-key-here
        echo ANTHROPIC_API_KEY=your-anthropic-api-key-here
        echo.
        echo # Perpetual Thinking System Configuration
        echo PERPETUAL_AI_PROVIDER=openai
        echo PERPETUAL_AI_MODEL=gpt-4
        echo PERPETUAL_AI_TEMPERATURE=0.7
        echo PERPETUAL_AI_MAX_TOKENS=2000
        echo PERPETUAL_MAX_CONCURRENT_SESSIONS=10
        echo PERPETUAL_SESSION_TIMEOUT=3600
        echo.
        echo # Security
        echo SECRET_KEY=your-secret-key-here
        echo API_KEY=your-api-key-here
        echo.
        echo # Monitoring
        echo GRAFANA_PASSWORD=admin
    ) > .env
    echo ⚠️  Please update .env file with your actual API keys and secrets
)

REM Build and start services
echo Building Docker images...
docker-compose build

echo Starting services...
docker-compose up -d

REM Wait for services to be healthy
echo Waiting for services to be healthy...
timeout /t 30 /nobreak >nul

REM Check service health
docker-compose ps | findstr "Up (healthy)" >nul
if errorlevel 1 (
    echo ❌ Some Docker services are not healthy
    docker-compose ps
    exit /b 1
) else (
    echo ✅ Docker services are running and healthy
)

echo 🎉 Docker deployment completed successfully!
echo Services available at:
echo   - API: http://localhost:8000
echo   - Web Interface: http://localhost:8001
echo   - Grafana: http://localhost:3000 (admin/admin)
echo   - Prometheus: http://localhost:9090

goto :eof

REM Function to deploy with Kubernetes
:deploy_k8s
echo ☸️  Deploying with Kubernetes...

REM Create namespace if it doesn't exist
kubectl get namespace %NAMESPACE% >nul 2>&1
if errorlevel 1 (
    echo Creating namespace: %NAMESPACE%
    kubectl create namespace %NAMESPACE%
)

REM Apply Kubernetes manifests
echo Applying Kubernetes manifests...

REM Apply namespace
kubectl apply -f k8s/namespace.yaml

REM Apply secrets (create if not exists)
kubectl get secret cosmic-council-secrets -n %NAMESPACE% >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Creating secrets from environment variables
    kubectl create secret generic cosmic-council-secrets ^
        --from-literal=DATABASE_PASSWORD=%POSTGRES_PASSWORD% ^
        --from-literal=SECRET_KEY=%SECRET_KEY% ^
        --from-literal=API_KEY=%API_KEY% ^
        --from-literal=OPENAI_API_KEY=%OPENAI_API_KEY% ^
        --from-literal=ANTHROPIC_API_KEY=%ANTHROPIC_API_KEY% ^
        --from-literal=JWT_SECRET=%JWT_SECRET% ^
        --from-literal=JWT_ALGORITHM=%JWT_ALGORITHM% ^
        --from-literal=JWT_EXPIRATION=%JWT_EXPIRATION% ^
        -n %NAMESPACE%
)

REM Apply configmap
kubectl apply -f k8s/configmap.yaml

REM Apply database services
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/postgres-perpetual.yaml
kubectl apply -f k8s/redis.yaml

REM Wait for databases to be ready
echo Waiting for databases to be ready...
kubectl wait --for=condition=ready pod -l app=postgres -n %NAMESPACE% --timeout=300s
kubectl wait --for=condition=ready pod -l app=postgres-perpetual -n %NAMESPACE% --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n %NAMESPACE% --timeout=300s

REM Apply API and web services
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/web.yaml

REM Apply ingress
kubectl apply -f k8s/ingress.yaml

REM Wait for services to be ready
echo Waiting for services to be ready...
kubectl wait --for=condition=ready pod -l app=cosmic-council-api -n %NAMESPACE% --timeout=300s
kubectl wait --for=condition=ready pod -l app=cosmic-council-web -n %NAMESPACE% --timeout=300s

echo ✅ Kubernetes deployment completed successfully!

REM Get service URLs
echo Services available at:
kubectl get services -n %NAMESPACE%

goto :eof

REM Function to run tests
:run_tests
echo 🧪 Running perpetual thinking system tests...

if exist "run_perpetual_tests.py" (
    python run_perpetual_tests.py --all
) else (
    echo ⚠️  Perpetual tests not found, running general tests
    python run_tests.py --type perpetual
)

goto :eof

REM Function to show deployment status
:show_status
echo 📊 Deployment Status
echo ==================

if "%DEPLOYMENT_TYPE%"=="docker" (
    echo 🐳 Docker Services:
    docker-compose ps
    echo.
)

if "%DEPLOYMENT_TYPE%"=="k8s" (
    echo ☸️  Kubernetes Services:
    kubectl get pods -n %NAMESPACE%
    echo.
    kubectl get services -n %NAMESPACE%
)

goto :eof

REM Function to show logs
:show_logs
echo 📋 Recent Logs
echo =============

if "%DEPLOYMENT_TYPE%"=="docker" (
    echo 🐳 Docker Logs:
    docker-compose logs --tail=50
)

if "%DEPLOYMENT_TYPE%"=="k8s" (
    echo ☸️  Kubernetes Logs:
    kubectl logs -l app=cosmic-council-api -n %NAMESPACE% --tail=50
)

goto :eof

REM Main deployment function
:main
echo Deployment Type: %DEPLOYMENT_TYPE%
echo.

call :check_prerequisites
if errorlevel 1 exit /b 1

if "%DEPLOYMENT_TYPE%"=="docker" (
    call :deploy_docker
) else if "%DEPLOYMENT_TYPE%"=="k8s" (
    call :deploy_k8s
) else if "%DEPLOYMENT_TYPE%"=="both" (
    call :deploy_docker
    call :deploy_k8s
) else (
    echo ❌ Invalid deployment type. Use: docker, k8s, or both
    exit /b 1
)

REM Run tests if requested
if "%2"=="--test" (
    call :run_tests
)

REM Show status
call :show_status

echo 🎉 Perpetual Thinking System deployment completed!
echo.
echo Next steps:
echo 1. Update your .env file with actual API keys
echo 2. Access the web interface to start perpetual thinking sessions
echo 3. Monitor the system using Grafana dashboards
echo 4. Check logs if you encounter any issues
echo.
echo For more information, see the README files in the docs/ directory

goto :eof

REM Handle command line arguments
if "%1"=="status" (
    call :show_status
    exit /b 0
)

if "%1"=="logs" (
    call :show_logs
    exit /b 0
)

if "%1"=="test" (
    call :run_tests
    exit /b 0
)

if "%1"=="help" (
    echo Usage: %0 [deployment_type] [options]
    echo.
    echo Deployment Types:
    echo   docker    Deploy using Docker Compose
    echo   k8s       Deploy using Kubernetes
    echo   both      Deploy using both Docker and Kubernetes
    echo.
    echo Options:
    echo   --test    Run tests after deployment
    echo.
    echo Commands:
    echo   status    Show deployment status
    echo   logs      Show recent logs
    echo   test      Run perpetual thinking system tests
    echo   help      Show this help message
    echo.
    echo Examples:
    echo   %0 docker --test
    echo   %0 k8s
    echo   %0 both
    echo   %0 status
    exit /b 0
)

REM Run main function
call :main %*

endlocal
