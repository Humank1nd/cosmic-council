"""
Configuration management for the Cosmic Council system.
Provides centralized configuration with environment variable support.
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

class Environment(Enum):
    """Environment enumeration."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    name: str = "cosmic_council"
    user: str = "cosmic_council"
    password: str = "cosmic_council"
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600

@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    file: str = "logs/cosmic_council.log"
    json: bool = False
    max_size: int = 10485760  # 10MB
    backup_count: int = 5

@dataclass
class SecurityConfig:
    """Security configuration."""
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15

@dataclass
class ServiceConfig:
    """Service configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    debug: bool = False
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_methods: List[str] = field(default_factory=lambda: ["*"])
    cors_headers: List[str] = field(default_factory=lambda: ["*"])

@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool = True
    backend: str = "memory"  # memory, redis, memcached
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    default_timeout: int = 300
    max_connections: int = 10

@dataclass
class MonitoringConfig:
    """Monitoring configuration."""
    enabled: bool = True
    prometheus_port: int = 9090
    metrics_path: str = "/metrics"
    health_check_path: str = "/health"
    readiness_path: str = "/ready"
    liveness_path: str = "/live"

@dataclass
class Settings:
    """Main settings class for the Cosmic Council system."""
    
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "cosmic_council"
    db_user: str = "cosmic_council"
    db_password: str = "cosmic_council"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    log_file: str = "logs/cosmic_council.log"
    log_json: bool = False
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Services
    gateway_host: str = "0.0.0.0"
    gateway_port: int = 8000
    analytics_host: str = "0.0.0.0"
    analytics_port: int = 8001
    reflection_host: str = "0.0.0.0"
    reflection_port: int = 8002
    
    # Cache
    cache_enabled: bool = True
    cache_backend: str = "memory"
    cache_host: str = "localhost"
    cache_port: int = 6379
    
    # Monitoring
    monitoring_enabled: bool = True
    prometheus_port: int = 9090
    
    # N8N
    n8n_host: str = "localhost"
    n8n_port: int = 5678
    n8n_webhook_url: str = "http://localhost:5678/webhook"
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Load from environment variables
        self._load_from_env()
        
        # Validate configuration
        self._validate()
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Environment
        self.environment = Environment(os.getenv("ENVIRONMENT", self.environment.value))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Database
        self.db_host = os.getenv("DB_HOST", self.db_host)
        self.db_port = int(os.getenv("DB_PORT", str(self.db_port)))
        self.db_name = os.getenv("DB_NAME", self.db_name)
        self.db_user = os.getenv("DB_USER", self.db_user)
        self.db_password = os.getenv("DB_PASSWORD", self.db_password)
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        self.log_format = os.getenv("LOG_FORMAT", self.log_format)
        self.log_file = os.getenv("LOG_FILE", self.log_file)
        self.log_json = os.getenv("LOG_JSON", "false").lower() == "true"
        
        # Security
        self.secret_key = os.getenv("SECRET_KEY", self.secret_key)
        self.algorithm = os.getenv("ALGORITHM", self.algorithm)
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(self.access_token_expire_minutes)))
        
        # Services
        self.gateway_host = os.getenv("GATEWAY_HOST", self.gateway_host)
        self.gateway_port = int(os.getenv("GATEWAY_PORT", str(self.gateway_port)))
        self.analytics_host = os.getenv("ANALYTICS_HOST", self.analytics_host)
        self.analytics_port = int(os.getenv("ANALYTICS_PORT", str(self.analytics_port)))
        self.reflection_host = os.getenv("REFLECTION_HOST", self.reflection_host)
        self.reflection_port = int(os.getenv("REFLECTION_PORT", str(self.reflection_port)))
        
        # Cache
        self.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.cache_backend = os.getenv("CACHE_BACKEND", self.cache_backend)
        self.cache_host = os.getenv("CACHE_HOST", self.cache_host)
        self.cache_port = int(os.getenv("CACHE_PORT", str(self.cache_port)))
        
        # Monitoring
        self.monitoring_enabled = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
        self.prometheus_port = int(os.getenv("PROMETHEUS_PORT", str(self.prometheus_port)))
        
        # N8N
        self.n8n_host = os.getenv("N8N_HOST", self.n8n_host)
        self.n8n_port = int(os.getenv("N8N_PORT", str(self.n8n_port)))
        self.n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL", self.n8n_webhook_url)
    
    def _validate(self) -> None:
        """Validate the configuration."""
        # Validate database configuration
        if not self.db_host or not self.db_name or not self.db_user:
            raise ValueError("Database configuration is incomplete")
        
        # Validate security configuration
        if not self.secret_key or self.secret_key == "your-secret-key-here":
            if self.environment == Environment.PRODUCTION:
                raise ValueError("Secret key must be set in production")
        
        # Validate port ranges
        for port_name, port_value in [
            ("DB_PORT", self.db_port),
            ("GATEWAY_PORT", self.gateway_port),
            ("ANALYTICS_PORT", self.analytics_port),
            ("REFLECTION_PORT", self.reflection_port),
            ("N8N_PORT", self.n8n_port)
        ]:
            if not (1 <= port_value <= 65535):
                raise ValueError(f"{port_name} must be between 1 and 65535")
    
    def get_database_url(self) -> str:
        """Get the database URL."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    def get_service_url(self, service: str) -> str:
        """Get the URL for a service."""
        if service == "gateway":
            return f"http://{self.gateway_host}:{self.gateway_port}"
        elif service == "analytics":
            return f"http://{self.analytics_host}:{self.analytics_port}"
        elif service == "reflection":
            return f"http://{self.reflection_host}:{self.reflection_port}"
        elif service == "n8n":
            return f"http://{self.n8n_host}:{self.n8n_port}"
        else:
            raise ValueError(f"Unknown service: {service}")
    
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == Environment.DEVELOPMENT
    
    def is_testing(self) -> bool:
        """Check if running in testing."""
        return self.environment == Environment.TESTING

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def load_config(config_file: Optional[str] = None) -> Settings:
    """Load configuration from a file."""
    global _settings
    if config_file:
        # TODO: Implement config file loading
        pass
    _settings = Settings()
    return _settings
