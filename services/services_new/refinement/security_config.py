"""
Cosmic Council Refinement Engine - Security Configuration
Centralized security configuration and environment management.
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class SecurityLevel(Enum):
    """Security levels for different environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class SecurityConfig:
    """Security configuration class."""
    
    # Environment
    environment: SecurityLevel
    debug: bool
    
    # JWT Configuration
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    
    # Password Policy
    min_password_length: int
    require_uppercase: bool
    require_lowercase: bool
    require_digits: bool
    require_special_chars: bool
    max_password_length: int
    
    # Account Security
    max_login_attempts: int
    lockout_duration_minutes: int
    session_timeout_minutes: int
    
    # API Security
    enable_rate_limiting: bool
    rate_limit_requests_per_minute: int
    rate_limit_requests_per_hour: int
    enable_cors: bool
    allowed_origins: List[str]
    allowed_hosts: List[str]
    
    # Input Validation
    enable_input_sanitization: bool
    max_input_length: int
    allowed_file_types: List[str]
    max_file_size_mb: int
    
    # Database Security
    enable_sql_injection_protection: bool
    enable_connection_encryption: bool
    connection_timeout_seconds: int
    
    # Monitoring
    enable_security_logging: bool
    enable_audit_trail: bool
    log_failed_attempts: bool
    alert_on_suspicious_activity: bool
    
    # API Keys
    api_key_expire_days: int
    max_api_keys_per_user: int
    enable_api_key_rotation: bool
    
    # CORS Configuration
    cors_allow_credentials: bool
    cors_allow_methods: List[str]
    cors_allow_headers: List[str]
    cors_expose_headers: List[str]
    
    # Security Headers
    enable_security_headers: bool
    hsts_max_age: int
    content_type_nosniff: bool
    xss_protection: bool
    frame_options: str
    
    # Redis Configuration
    redis_url: str
    redis_password: str
    redis_ssl: bool
    redis_connection_pool_size: int
    
    # Rate Limiting
    rate_limit_storage_backend: str  # "memory" or "redis"
    rate_limit_key_prefix: str
    
    # Brute Force Protection
    enable_brute_force_protection: bool
    brute_force_threshold: int
    brute_force_window_minutes: int
    
    # Input Validation Rules
    username_pattern: str
    email_pattern: str
    problem_title_pattern: str
    problem_description_pattern: str
    
    # File Upload Security
    enable_file_upload: bool
    upload_directory: str
    scan_uploads_for_malware: bool
    
    # Network Security
    enable_ip_whitelist: bool
    allowed_ip_ranges: List[str]
    enable_geo_blocking: bool
    blocked_countries: List[str]
    
    # Encryption
    enable_data_encryption: bool
    encryption_key: str
    enable_field_level_encryption: bool
    
    # Compliance
    enable_gdpr_compliance: bool
    enable_ccpa_compliance: bool
    data_retention_days: int
    enable_data_anonymization: bool


def get_security_config() -> SecurityConfig:
    """
    Get security configuration based on environment variables.
    
    Returns:
        SecurityConfig object with all security settings
    """
    environment = SecurityLevel(os.getenv("ENVIRONMENT", "development"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    # JWT Configuration
    jwt_secret_key = os.getenv("JWT_SECRET_KEY")
    if not jwt_secret_key:
        if environment == SecurityLevel.PRODUCTION:
            raise ValueError("JWT_SECRET_KEY must be set in production")
        jwt_secret_key = "development-secret-key-change-in-production"
    
    # Password Policy
    min_password_length = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))
    max_password_length = int(os.getenv("MAX_PASSWORD_LENGTH", "128"))
    
    # Account Security
    max_login_attempts = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    lockout_duration_minutes = int(os.getenv("LOCKOUT_DURATION_MINUTES", "30"))
    
    # API Security
    enable_rate_limiting = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    rate_limit_requests_per_minute = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))
    rate_limit_requests_per_hour = int(os.getenv("RATE_LIMIT_REQUESTS_PER_HOUR", "1000"))
    
    # CORS Configuration
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    
    # Input Validation
    enable_input_sanitization = os.getenv("ENABLE_INPUT_SANITIZATION", "true").lower() == "true"
    max_input_length = int(os.getenv("MAX_INPUT_LENGTH", "10000"))
    
    # Database Security
    enable_sql_injection_protection = os.getenv("ENABLE_SQL_INJECTION_PROTECTION", "true").lower() == "true"
    enable_connection_encryption = os.getenv("ENABLE_CONNECTION_ENCRYPTION", "true").lower() == "true"
    
    # Monitoring
    enable_security_logging = os.getenv("ENABLE_SECURITY_LOGGING", "true").lower() == "true"
    enable_audit_trail = os.getenv("ENABLE_AUDIT_TRAIL", "true").lower() == "true"
    log_failed_attempts = os.getenv("LOG_FAILED_ATTEMPTS", "true").lower() == "true"
    alert_on_suspicious_activity = os.getenv("ALERT_ON_SUSPICIOUS_ACTIVITY", "true").lower() == "true"
    
    # API Keys
    api_key_expire_days = int(os.getenv("API_KEY_EXPIRE_DAYS", "365"))
    max_api_keys_per_user = int(os.getenv("MAX_API_KEYS_PER_USER", "10"))
    enable_api_key_rotation = os.getenv("ENABLE_API_KEY_ROTATION", "true").lower() == "true"
    
    # CORS Configuration
    cors_allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    cors_allow_methods = os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE").split(",")
    cors_allow_headers = os.getenv("CORS_ALLOW_HEADERS", "*").split(",")
    cors_expose_headers = os.getenv("CORS_EXPOSE_HEADERS", "X-Request-ID").split(",")
    
    # Security Headers
    enable_security_headers = os.getenv("ENABLE_SECURITY_HEADERS", "true").lower() == "true"
    hsts_max_age = int(os.getenv("HSTS_MAX_AGE", "31536000"))
    content_type_nosniff = os.getenv("CONTENT_TYPE_NOSNIFF", "true").lower() == "true"
    xss_protection = os.getenv("XSS_PROTECTION", "true").lower() == "true"
    frame_options = os.getenv("FRAME_OPTIONS", "DENY")
    
    # Redis Configuration
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_password = os.getenv("REDIS_PASSWORD", "")
    redis_ssl = os.getenv("REDIS_SSL", "false").lower() == "true"
    redis_connection_pool_size = int(os.getenv("REDIS_CONNECTION_POOL_SIZE", "10"))
    
    # Rate Limiting
    rate_limit_storage_backend = os.getenv("RATE_LIMIT_STORAGE_BACKEND", "memory")
    rate_limit_key_prefix = os.getenv("RATE_LIMIT_KEY_PREFIX", "rate_limit")
    
    # Brute Force Protection
    enable_brute_force_protection = os.getenv("ENABLE_BRUTE_FORCE_PROTECTION", "true").lower() == "true"
    brute_force_threshold = int(os.getenv("BRUTE_FORCE_THRESHOLD", "5"))
    brute_force_window_minutes = int(os.getenv("BRUTE_FORCE_WINDOW_MINUTES", "15"))
    
    # Input Validation Rules
    username_pattern = os.getenv("USERNAME_PATTERN", r'^[a-zA-Z0-9_-]+$')
    email_pattern = os.getenv("EMAIL_PATTERN", r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    problem_title_pattern = os.getenv("PROBLEM_TITLE_PATTERN", r'^[a-zA-Z0-9\s\-_.,!?()]+$')
    problem_description_pattern = os.getenv("PROBLEM_DESCRIPTION_PATTERN", r'^[a-zA-Z0-9\s\-_.,!?()\n\r]+$')
    
    # File Upload Security
    enable_file_upload = os.getenv("ENABLE_FILE_UPLOAD", "false").lower() == "true"
    upload_directory = os.getenv("UPLOAD_DIRECTORY", "./uploads")
    scan_uploads_for_malware = os.getenv("SCAN_UPLOADS_FOR_MALWARE", "true").lower() == "true"
    
    # Network Security
    enable_ip_whitelist = os.getenv("ENABLE_IP_WHITELIST", "false").lower() == "true"
    allowed_ip_ranges = os.getenv("ALLOWED_IP_RANGES", "").split(",") if os.getenv("ALLOWED_IP_RANGES") else []
    enable_geo_blocking = os.getenv("ENABLE_GEO_BLOCKING", "false").lower() == "true"
    blocked_countries = os.getenv("BLOCKED_COUNTRIES", "").split(",") if os.getenv("BLOCKED_COUNTRIES") else []
    
    # Encryption
    enable_data_encryption = os.getenv("ENABLE_DATA_ENCRYPTION", "true").lower() == "true"
    encryption_key = os.getenv("ENCRYPTION_KEY", "")
    enable_field_level_encryption = os.getenv("ENABLE_FIELD_LEVEL_ENCRYPTION", "false").lower() == "true"
    
    # Compliance
    enable_gdpr_compliance = os.getenv("ENABLE_GDPR_COMPLIANCE", "true").lower() == "true"
    enable_ccpa_compliance = os.getenv("ENABLE_CCPA_COMPLIANCE", "true").lower() == "true"
    data_retention_days = int(os.getenv("DATA_RETENTION_DAYS", "2555"))  # 7 years
    enable_data_anonymization = os.getenv("ENABLE_DATA_ANONYMIZATION", "true").lower() == "true"
    
    return SecurityConfig(
        # Environment
        environment=environment,
        debug=debug,
        
        # JWT Configuration
        jwt_secret_key=jwt_secret_key,
        jwt_algorithm="HS256",
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        refresh_token_expire_days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
        
        # Password Policy
        min_password_length=min_password_length,
        require_uppercase=os.getenv("REQUIRE_UPPERCASE", "true").lower() == "true",
        require_lowercase=os.getenv("REQUIRE_LOWERCASE", "true").lower() == "true",
        require_digits=os.getenv("REQUIRE_DIGITS", "true").lower() == "true",
        require_special_chars=os.getenv("REQUIRE_SPECIAL_CHARS", "true").lower() == "true",
        max_password_length=max_password_length,
        
        # Account Security
        max_login_attempts=max_login_attempts,
        lockout_duration_minutes=lockout_duration_minutes,
        session_timeout_minutes=int(os.getenv("SESSION_TIMEOUT_MINUTES", "30")),
        
        # API Security
        enable_rate_limiting=enable_rate_limiting,
        rate_limit_requests_per_minute=rate_limit_requests_per_minute,
        rate_limit_requests_per_hour=rate_limit_requests_per_hour,
        enable_cors=os.getenv("ENABLE_CORS", "true").lower() == "true",
        allowed_origins=allowed_origins,
        allowed_hosts=allowed_hosts,
        
        # Input Validation
        enable_input_sanitization=enable_input_sanitization,
        max_input_length=max_input_length,
        allowed_file_types=os.getenv("ALLOWED_FILE_TYPES", "txt,pdf,doc,docx").split(","),
        max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "10")),
        
        # Database Security
        enable_sql_injection_protection=enable_sql_injection_protection,
        enable_connection_encryption=enable_connection_encryption,
        connection_timeout_seconds=int(os.getenv("CONNECTION_TIMEOUT_SECONDS", "30")),
        
        # Monitoring
        enable_security_logging=enable_security_logging,
        enable_audit_trail=enable_audit_trail,
        log_failed_attempts=log_failed_attempts,
        alert_on_suspicious_activity=alert_on_suspicious_activity,
        
        # API Keys
        api_key_expire_days=api_key_expire_days,
        max_api_keys_per_user=max_api_keys_per_user,
        enable_api_key_rotation=enable_api_key_rotation,
        
        # CORS Configuration
        cors_allow_credentials=cors_allow_credentials,
        cors_allow_methods=cors_allow_methods,
        cors_allow_headers=cors_allow_headers,
        cors_expose_headers=cors_expose_headers,
        
        # Security Headers
        enable_security_headers=enable_security_headers,
        hsts_max_age=hsts_max_age,
        content_type_nosniff=content_type_nosniff,
        xss_protection=xss_protection,
        frame_options=frame_options,
        
        # Redis Configuration
        redis_url=redis_url,
        redis_password=redis_password,
        redis_ssl=redis_ssl,
        redis_connection_pool_size=redis_connection_pool_size,
        
        # Rate Limiting
        rate_limit_storage_backend=rate_limit_storage_backend,
        rate_limit_key_prefix=rate_limit_key_prefix,
        
        # Brute Force Protection
        enable_brute_force_protection=enable_brute_force_protection,
        brute_force_threshold=brute_force_threshold,
        brute_force_window_minutes=brute_force_window_minutes,
        
        # Input Validation Rules
        username_pattern=username_pattern,
        email_pattern=email_pattern,
        problem_title_pattern=problem_title_pattern,
        problem_description_pattern=problem_description_pattern,
        
        # File Upload Security
        enable_file_upload=enable_file_upload,
        upload_directory=upload_directory,
        scan_uploads_for_malware=scan_uploads_for_malware,
        
        # Network Security
        enable_ip_whitelist=enable_ip_whitelist,
        allowed_ip_ranges=allowed_ip_ranges,
        enable_geo_blocking=enable_geo_blocking,
        blocked_countries=blocked_countries,
        
        # Encryption
        enable_data_encryption=enable_data_encryption,
        encryption_key=encryption_key,
        enable_field_level_encryption=enable_field_level_encryption,
        
        # Compliance
        enable_gdpr_compliance=enable_gdpr_compliance,
        enable_ccpa_compliance=enable_ccpa_compliance,
        data_retention_days=data_retention_days,
        enable_data_anonymization=enable_data_anonymization
    )


def validate_security_config(config: SecurityConfig) -> List[str]:
    """
    Validate security configuration and return any issues.
    
    Args:
        config: Security configuration to validate
        
    Returns:
        List of validation issues
    """
    issues = []
    
    # Check required fields
    if not config.jwt_secret_key:
        issues.append("JWT secret key is required")
    
    if config.environment == SecurityLevel.PRODUCTION:
        if config.jwt_secret_key == "development-secret-key-change-in-production":
            issues.append("JWT secret key must be changed in production")
        
        if config.debug:
            issues.append("Debug mode should be disabled in production")
        
        if not config.enable_rate_limiting:
            issues.append("Rate limiting should be enabled in production")
        
        if not config.enable_security_logging:
            issues.append("Security logging should be enabled in production")
        
        if not config.enable_audit_trail:
            issues.append("Audit trail should be enabled in production")
        
        if not config.enable_input_sanitization:
            issues.append("Input sanitization should be enabled in production")
        
        if not config.enable_sql_injection_protection:
            issues.append("SQL injection protection should be enabled in production")
        
        if not config.enable_connection_encryption:
            issues.append("Connection encryption should be enabled in production")
        
        if not config.enable_security_headers:
            issues.append("Security headers should be enabled in production")
        
        if not config.enable_brute_force_protection:
            issues.append("Brute force protection should be enabled in production")
    
    # Check password policy
    if config.min_password_length < 8:
        issues.append("Minimum password length should be at least 8 characters")
    
    if config.max_password_length < config.min_password_length:
        issues.append("Maximum password length must be greater than minimum password length")
    
    # Check rate limiting
    if config.rate_limit_requests_per_minute < 1:
        issues.append("Rate limit requests per minute must be at least 1")
    
    if config.rate_limit_requests_per_hour < config.rate_limit_requests_per_minute:
        issues.append("Rate limit requests per hour must be greater than per minute")
    
    # Check session timeout
    if config.session_timeout_minutes < 1:
        issues.append("Session timeout must be at least 1 minute")
    
    # Check API key expiration
    if config.api_key_expire_days < 1:
        issues.append("API key expiration must be at least 1 day")
    
    # Check data retention
    if config.data_retention_days < 1:
        issues.append("Data retention period must be at least 1 day")
    
    return issues


# Example usage and testing
if __name__ == "__main__":
    import os
    
    # Set test environment variables
    os.environ["ENVIRONMENT"] = "development"
    os.environ["DEBUG"] = "true"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key"
    os.environ["ENABLE_RATE_LIMITING"] = "true"
    os.environ["ENABLE_SECURITY_LOGGING"] = "true"
    
    # Get configuration
    config = get_security_config()
    
    print("=== Security Configuration ===")
    print(f"Environment: {config.environment.value}")
    print(f"Debug: {config.debug}")
    print(f"Rate Limiting: {config.enable_rate_limiting}")
    print(f"Security Logging: {config.enable_security_logging}")
    print(f"Input Sanitization: {config.enable_input_sanitization}")
    print(f"Brute Force Protection: {config.enable_brute_force_protection}")
    print(f"Min Password Length: {config.min_password_length}")
    print(f"Max Login Attempts: {config.max_login_attempts}")
    print(f"Session Timeout: {config.session_timeout_minutes} minutes")
    print(f"API Key Expiration: {config.api_key_expire_days} days")
    
    # Validate configuration
    issues = validate_security_config(config)
    if issues:
        print("\n=== Configuration Issues ===")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("\n✅ Configuration is valid")
    
    # Test production configuration
    os.environ["ENVIRONMENT"] = "production"
    os.environ["DEBUG"] = "false"
    
    prod_config = get_security_config()
    prod_issues = validate_security_config(prod_config)
    
    print(f"\n=== Production Configuration Issues ===")
    if prod_issues:
        for issue in prod_issues:
            print(f"- {issue}")
    else:
        print("✅ Production configuration is valid")
