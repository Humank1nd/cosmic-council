@echo off
REM Cosmic Council Framework - Codex-Enhanced Deployment Script for Windows
REM This script uses Codex to optimize and deploy the system

setlocal enabledelayedexpansion

REM Configuration
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set ENVIRONMENT=%1
set ACTION=%2
set CODEX_ENABLED=%3

if "%ENVIRONMENT%"=="" set ENVIRONMENT=development
if "%ACTION%"=="" set ACTION=deploy
if "%CODEX_ENABLED%"=="" set CODEX_ENABLED=true

echo [INFO] Cosmic Council Framework - Codex-Enhanced Deployment
echo [INFO] Environment: %ENVIRONMENT%
echo [INFO] Action: %ACTION%
echo [INFO] Codex Enabled: %CODEX_ENABLED%

REM Functions
:log_info
echo [INFO] %~1
goto :eof

:log_success
echo [SUCCESS] %~1
goto :eof

:log_warning
echo [WARNING] %~1
goto :eof

:log_error
echo [ERROR] %~1
goto :eof

:log_codex
echo [CODEX] %~1
goto :eof

:check_codex_dependencies
call :log_info "Checking Codex dependencies..."

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Node.js is not installed. Please install Node.js first."
    exit /b 1
)

REM Check if Codex CLI is installed
codex --version >nul 2>&1
if errorlevel 1 (
    call :log_warning "Codex CLI not found. Installing..."
    npm install -g @openai/codex
    if errorlevel 1 (
        call :log_error "Failed to install Codex CLI"
        exit /b 1
    )
)

REM Check if logged in
codex whoami >nul 2>&1
if errorlevel 1 (
    call :log_warning "Not logged into Codex. Checking for API key..."
    if defined OPENAI_API_KEY (
        call :log_info "Using OPENAI_API_KEY from environment..."
        codex login --api-key "%OPENAI_API_KEY%"
        if errorlevel 1 (
            call :log_error "Failed to login to Codex"
            exit /b 1
        )
    ) else (
        call :log_error "No OpenAI API key found. Set OPENAI_API_KEY environment variable or run codex login"
        exit /b 1
    )
)

call :log_success "Codex dependencies are ready"
goto :eof

:run_codex_pre_deployment
if "%CODEX_ENABLED%"=="true" (
    call :log_codex "Running Codex pre-deployment analysis..."
    
    REM Analyze codebase for deployment readiness
    codex exec --approval-policy on-failure --sandbox read-only "Analyze the Cosmic Council codebase for deployment readiness. Check for: 1. Configuration issues 2. Missing environment variables 3. Database migration requirements 4. Security vulnerabilities 5. Performance bottlenecks 6. Missing dependencies. Provide specific recommendations for the %ENVIRONMENT% environment."
    
    REM Optimize Docker configuration
    codex exec --approval-policy on-failure --sandbox workspace-write "Review and optimize the Docker configuration for the Cosmic Council project: 1. Analyze Dockerfile for efficiency 2. Check docker-compose.yml for best practices 3. Optimize image layers and caching 4. Ensure proper health checks 5. Review security configurations. Make improvements while maintaining compatibility."
    
    call :log_success "Codex pre-deployment analysis completed"
)
goto :eof

:run_codex_post_deployment
if "%CODEX_ENABLED%"=="true" (
    call :log_codex "Running Codex post-deployment optimization..."
    
    REM Generate deployment report
    codex exec --approval-policy never --sandbox read-only "Generate a comprehensive deployment report for the Cosmic Council system: 1. Deployment status and health 2. Performance metrics analysis 3. Resource utilization 4. Security assessment 5. Recommendations for improvements 6. Monitoring and alerting suggestions. Format as a detailed markdown report."
    
    REM Update documentation
    codex exec --approval-policy on-failure --sandbox workspace-write "Update deployment documentation based on the current deployment: 1. Update deployment guides 2. Add troubleshooting sections 3. Update configuration examples 4. Add performance tuning tips 5. Update monitoring setup instructions"
    
    call :log_success "Codex post-deployment optimization completed"
)
goto :eof

:run_codex_health_check
if "%CODEX_ENABLED%"=="true" (
    call :log_codex "Running Codex-enhanced health checks..."
    
    REM Comprehensive health analysis
    codex exec --approval-policy never --sandbox read-only "Perform a comprehensive health check analysis for the Cosmic Council deployment: 1. Analyze service status and logs 2. Check database connectivity and performance 3. Verify API endpoints and responses 4. Assess resource usage and limits 5. Check for error patterns 6. Validate configuration consistency 7. Test critical user workflows. Provide detailed health report with recommendations."
    
    call :log_success "Codex health check completed"
)
goto :eof

:deploy_with_codex
call :log_info "Starting Codex-enhanced deployment..."

REM Pre-deployment analysis
call :run_codex_pre_deployment

REM Standard deployment
if "%ENVIRONMENT%"=="development" (
    call :log_info "Deploying to development environment..."
    docker-compose -f docker-compose.dev.yml up -d --build
) else if "%ENVIRONMENT%"=="staging" (
    call :log_info "Deploying to staging environment..."
    docker-compose -f docker-compose.yml up -d --build
) else if "%ENVIRONMENT%"=="production" (
    call :log_info "Deploying to production environment..."
    REM Use Kubernetes for production
    kubectl apply -f infrastructure/k8s/
    kubectl rollout status deployment/cosmic-council-api -n cosmic-council
    kubectl rollout status deployment/cosmic-council-web -n cosmic-council
) else (
    call :log_error "Unknown environment: %ENVIRONMENT%"
    exit /b 1
)

REM Wait for services to be ready
call :log_info "Waiting for services to be ready..."
timeout /t 30 /nobreak >nul

REM Post-deployment optimization
call :run_codex_post_deployment

call :log_success "Codex-enhanced deployment completed"
goto :eof

:health_check_with_codex
call :log_info "Running enhanced health checks..."

REM Standard health checks
if "%ENVIRONMENT%"=="development" (
    docker-compose -f docker-compose.dev.yml ps | findstr "Up" >nul
    if errorlevel 1 (
        call :log_error "Some development services are not running"
        exit /b 1
    ) else (
        call :log_success "Development services are running"
    )
) else if "%ENVIRONMENT%"=="staging" (
    kubectl get pods -n cosmic-council | findstr "Running" >nul
    if errorlevel 1 (
        call :log_error "Some Kubernetes services are not running"
        exit /b 1
    ) else (
        call :log_success "Kubernetes services are running"
    )
) else if "%ENVIRONMENT%"=="production" (
    kubectl get pods -n cosmic-council | findstr "Running" >nul
    if errorlevel 1 (
        call :log_error "Some Kubernetes services are not running"
        exit /b 1
    ) else (
        call :log_success "Kubernetes services are running"
    )
)

REM Codex-enhanced health analysis
call :run_codex_health_check

call :log_success "Enhanced health checks completed"
goto :eof

:rollback_with_codex
call :log_info "Starting Codex-enhanced rollback..."

REM Analyze rollback requirements
if "%CODEX_ENABLED%"=="true" (
    call :log_codex "Running Codex rollback analysis..."
    codex exec --approval-policy never --sandbox read-only "Analyze the current deployment state and prepare rollback strategy: 1. Identify critical components that need rollback 2. Check database migration rollback requirements 3. Analyze configuration changes 4. Prepare rollback scripts and procedures 5. Identify potential data consistency issues 6. Create rollback validation checklist. Provide step-by-step rollback procedure."
    call :log_success "Codex rollback analysis completed"
)

REM Perform rollback
if "%ENVIRONMENT%"=="development" (
    call :log_info "Rolling back development environment..."
    docker-compose -f docker-compose.dev.yml down
    docker-compose -f docker-compose.dev.yml up -d
) else if "%ENVIRONMENT%"=="staging" (
    call :log_info "Rolling back Kubernetes deployment..."
    kubectl rollout undo deployment/cosmic-council-api -n cosmic-council
    kubectl rollout undo deployment/cosmic-council-web -n cosmic-council
) else if "%ENVIRONMENT%"=="production" (
    call :log_info "Rolling back Kubernetes deployment..."
    kubectl rollout undo deployment/cosmic-council-api -n cosmic-council
    kubectl rollout undo deployment/cosmic-council-web -n cosmic-council
)

REM Verify rollback
call :health_check_with_codex

call :log_success "Codex-enhanced rollback completed"
goto :eof

REM Main script logic
if "%ACTION%"=="deploy" (
    if "%CODEX_ENABLED%"=="true" (
        call :check_codex_dependencies
    )
    call :deploy_with_codex
) else if "%ACTION%"=="health" (
    call :health_check_with_codex
) else if "%ACTION%"=="rollback" (
    call :rollback_with_codex
) else if "%ACTION%"=="codex-analyze" (
    if "%CODEX_ENABLED%"=="true" (
        call :check_codex_dependencies
        call :run_codex_pre_deployment
    ) else (
        call :log_error "Codex is disabled. Enable with: %0 %ENVIRONMENT% %ACTION% true"
        exit /b 1
    )
) else if "%ACTION%"=="codex-optimize" (
    if "%CODEX_ENABLED%"=="true" (
        call :check_codex_dependencies
        call :run_codex_post_deployment
    ) else (
        call :log_error "Codex is disabled. Enable with: %0 %ENVIRONMENT% %ACTION% true"
        exit /b 1
    )
) else (
    call :log_error "Unknown action: %ACTION%"
    echo Usage: %0 [environment] [action] [codex_enabled]
    echo Environments: development, staging, production
    echo Actions: deploy, health, rollback, codex-analyze, codex-optimize
    echo Codex: true (default) or false
    exit /b 1
)

call :log_success "Codex-enhanced deployment script completed successfully"
