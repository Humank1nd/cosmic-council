@echo off
REM Cosmic Council Framework Deployment Script for Windows
REM This script handles deployment to different environments

setlocal enabledelayedexpansion

REM Configuration
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set ENVIRONMENT=%1
set ACTION=%2

if "%ENVIRONMENT%"=="" set ENVIRONMENT=development
if "%ACTION%"=="" set ACTION=deploy

echo [INFO] Cosmic Council Framework Deployment Script
echo [INFO] Environment: %ENVIRONMENT%
echo [INFO] Action: %ACTION%

REM Functions
:check_dependencies
echo [INFO] Checking dependencies...

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Check kubectl for Kubernetes deployment
if "%ENVIRONMENT%"=="production" goto check_kubectl
if "%ENVIRONMENT%"=="staging" goto check_kubectl
goto dependencies_ok

:check_kubectl
kubectl version --client >nul 2>&1
if errorlevel 1 (
    echo [ERROR] kubectl is not installed. Please install kubectl first.
    exit /b 1
)

:dependencies_ok
echo [SUCCESS] All dependencies are installed.
goto :eof

:build_image
echo [INFO] Building Docker image...

cd /d "%PROJECT_ROOT%"

REM Build the image
docker build -t cosmic-council:latest .

REM Tag for different environments
if "%ENVIRONMENT%"=="development" (
    docker tag cosmic-council:latest cosmic-council:dev
) else if "%ENVIRONMENT%"=="staging" (
    docker tag cosmic-council:latest cosmic-council:staging
) else if "%ENVIRONMENT%"=="production" (
    docker tag cosmic-council:latest cosmic-council:prod
)

echo [SUCCESS] Docker image built successfully.
goto :eof

:deploy_docker_compose
echo [INFO] Deploying with Docker Compose...

cd /d "%PROJECT_ROOT%"

REM Create .env file if it doesn't exist
if not exist .env (
    echo [INFO] Creating .env file...
    (
        echo # Cosmic Council Framework Environment Variables
        echo POSTGRES_PASSWORD=cosmic_council_password
        echo SECRET_KEY=your-secret-key-here
        echo API_KEY=your-api-key-here
        echo OPENAI_API_KEY=your-openai-api-key
        echo ANTHROPIC_API_KEY=your-anthropic-api-key
        echo GRAFANA_PASSWORD=admin
    ) > .env
    echo [WARNING] Please update the .env file with your actual values.
)

REM Deploy based on environment
if "%ENVIRONMENT%"=="development" (
    docker-compose -f docker-compose.dev.yml up -d
) else if "%ENVIRONMENT%"=="production" (
    docker-compose up -d
) else (
    echo [ERROR] Unknown environment: %ENVIRONMENT%
    exit /b 1
)

echo [SUCCESS] Docker Compose deployment completed.
goto :eof

:deploy_kubernetes
echo [INFO] Deploying to Kubernetes...

cd /d "%PROJECT_ROOT%\k8s"

REM Apply namespace
kubectl apply -f namespace.yaml

REM Apply secrets
kubectl apply -f secrets.yaml

REM Apply configmap
kubectl apply -f configmap.yaml

REM Apply database
kubectl apply -f postgres.yaml
kubectl apply -f redis.yaml

REM Wait for database to be ready
echo [INFO] Waiting for database to be ready...
kubectl wait --for=condition=ready pod -l app=postgres -n cosmic-council --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n cosmic-council --timeout=300s

REM Apply applications
kubectl apply -f api.yaml
kubectl apply -f web.yaml

REM Apply ingress
kubectl apply -f ingress.yaml

REM Wait for deployments to be ready
echo [INFO] Waiting for deployments to be ready...
kubectl wait --for=condition=available deployment/cosmic-council-api -n cosmic-council --timeout=300s
kubectl wait --for=condition=available deployment/cosmic-council-web -n cosmic-council --timeout=300s

echo [SUCCESS] Kubernetes deployment completed.
goto :eof

:health_check
echo [INFO] Running health checks...

if "%ENVIRONMENT%"=="development" (
    REM Check Docker Compose services
    docker-compose -f docker-compose.dev.yml ps | findstr "Up" >nul
    if errorlevel 1 (
        echo [ERROR] Some development services are not running.
        exit /b 1
    )
    echo [SUCCESS] Development services are running.
) else if "%ENVIRONMENT%"=="production" (
    REM Check Docker Compose services
    docker-compose ps | findstr "Up" >nul
    if errorlevel 1 (
        echo [ERROR] Some production services are not running.
        exit /b 1
    )
    echo [SUCCESS] Production services are running.
) else if "%ENVIRONMENT%"=="staging" (
    REM Check Kubernetes services
    kubectl get pods -n cosmic-council | findstr "Running" >nul
    if errorlevel 1 (
        echo [ERROR] Some Kubernetes services are not running.
        exit /b 1
    )
    echo [SUCCESS] Kubernetes services are running.
) else if "%ENVIRONMENT%"=="production" (
    REM Check Kubernetes services
    kubectl get pods -n cosmic-council | findstr "Running" >nul
    if errorlevel 1 (
        echo [ERROR] Some Kubernetes services are not running.
        exit /b 1
    )
    echo [SUCCESS] Kubernetes services are running.
)
goto :eof

:cleanup
echo [INFO] Cleaning up...

if "%ENVIRONMENT%"=="development" (
    docker-compose -f docker-compose.dev.yml down
) else if "%ENVIRONMENT%"=="production" (
    docker-compose down
) else if "%ENVIRONMENT%"=="staging" (
    kubectl delete namespace cosmic-council --ignore-not-found=true
) else if "%ENVIRONMENT%"=="production" (
    kubectl delete namespace cosmic-council --ignore-not-found=true
)

echo [SUCCESS] Cleanup completed.
goto :eof

:show_status
echo [INFO] Showing deployment status...

if "%ENVIRONMENT%"=="development" (
    docker-compose -f docker-compose.dev.yml ps
) else if "%ENVIRONMENT%"=="production" (
    docker-compose ps
) else if "%ENVIRONMENT%"=="staging" (
    kubectl get pods -n cosmic-council
    kubectl get services -n cosmic-council
    kubectl get ingress -n cosmic-council
) else if "%ENVIRONMENT%"=="production" (
    kubectl get pods -n cosmic-council
    kubectl get services -n cosmic-council
    kubectl get ingress -n cosmic-council
)
goto :eof

:show_logs
echo [INFO] Showing logs...

if "%ENVIRONMENT%"=="development" (
    docker-compose -f docker-compose.dev.yml logs -f
) else if "%ENVIRONMENT%"=="production" (
    docker-compose logs -f
) else if "%ENVIRONMENT%"=="staging" (
    kubectl logs -f deployment/cosmic-council-api -n cosmic-council
    kubectl logs -f deployment/cosmic-council-web -n cosmic-council
) else if "%ENVIRONMENT%"=="production" (
    kubectl logs -f deployment/cosmic-council-api -n cosmic-council
    kubectl logs -f deployment/cosmic-council-web -n cosmic-council
)
goto :eof

:main
call :check_dependencies
if errorlevel 1 exit /b 1

if "%ACTION%"=="deploy" (
    call :build_image
    if errorlevel 1 exit /b 1
    
    if "%ENVIRONMENT%"=="staging" (
        call :deploy_kubernetes
    ) else if "%ENVIRONMENT%"=="production" (
        call :deploy_kubernetes
    ) else (
        call :deploy_docker_compose
    )
    if errorlevel 1 exit /b 1
    
    call :health_check
    if errorlevel 1 exit /b 1
    
    call :show_status
) else if "%ACTION%"=="cleanup" (
    call :cleanup
) else if "%ACTION%"=="status" (
    call :show_status
) else if "%ACTION%"=="logs" (
    call :show_logs
) else if "%ACTION%"=="health" (
    call :health_check
) else (
    echo [ERROR] Unknown action: %ACTION%
    echo Usage: %0 [environment] [action]
    echo Environments: development, staging, production
    echo Actions: deploy, cleanup, status, logs, health
    exit /b 1
)

echo [SUCCESS] Deployment script completed successfully.
goto :eof

REM Run main function
call :main
