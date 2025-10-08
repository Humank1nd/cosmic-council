"""
Cosmic Council Configuration Management
Production-grade configuration with environment variables and validation.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from enum import Enum


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AIProvider(Enum):
    """AI provider options."""
    MOCK = "mock"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    db_path: str = "cosmic_council_production.db"
    pool_size: int = 10
    timeout: float = 30.0
    enable_wal_mode: bool = True
    enable_foreign_keys: bool = True
    backup_enabled: bool = True
    backup_interval_hours: int = 24


@dataclass
class AIConfig:
    """AI service configuration."""
    provider: AIProvider = AIProvider.MOCK
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.7
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-opus-20240229"
    anthropic_max_tokens: int = 2000
    anthropic_temperature: float = 0.7
    request_timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class ResearchConfig:
    """Research service configuration."""
    max_results: int = 5
    request_timeout: float = 10.0
    max_retries: int = 3
    enable_web_scraping: bool = False
    enable_caching: bool = True
    cache_ttl_hours: int = 24
    user_agent: str = "CosmicCouncil/1.0 (Research Bot)"


@dataclass
class SecurityConfig:
    """Security configuration."""
    enable_authentication: bool = False
    jwt_secret_key: Optional[str] = None
    jwt_expiration_hours: int = 24
    rate_limit_requests_per_minute: int = 60
    enable_cors: bool = True
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    enable_input_validation: bool = True
    max_input_length: int = 10000


@dataclass
class PerformanceConfig:
    """Performance configuration."""
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    max_concurrent_requests: int = 10
    request_timeout: float = 30.0
    enable_metrics: bool = True
    metrics_retention_days: int = 30


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size_mb: int = 10
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True


@dataclass
class CosmicCouncilConfig:
    """Main configuration class."""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    research: ResearchConfig = field(default_factory=ResearchConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Application settings
    app_name: str = "Cosmic Council MVP"
    app_version: str = "2.0.0"
    debug_mode: bool = False
    environment: str = "development"
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration values."""
        # Validate AI configuration
        if self.ai.provider == AIProvider.OPENAI and not self.ai.openai_api_key:
            if not os.getenv("OPENAI_API_KEY"):
                logging.warning("OpenAI API key not provided, falling back to mock provider")
                self.ai.provider = AIProvider.MOCK
        
        if self.ai.provider == AIProvider.ANTHROPIC and not self.ai.anthropic_api_key:
            if not os.getenv("ANTHROPIC_API_KEY"):
                logging.warning("Anthropic API key not provided, falling back to mock provider")
                self.ai.provider = AIProvider.MOCK
        
        # Validate security configuration
        if self.security.enable_authentication and not self.security.jwt_secret_key:
            if not os.getenv("JWT_SECRET_KEY"):
                logging.warning("JWT secret key not provided, authentication disabled")
                self.security.enable_authentication = False
        
        # Validate database path
        db_path = Path(self.database.db_path)
        if not db_path.parent.exists():
            db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> 'CosmicCouncilConfig':
        """Create configuration from environment variables."""
        config = cls()
        
        # Database configuration
        config.database.db_path = os.getenv("DATABASE_PATH", config.database.db_path)
        config.database.pool_size = int(os.getenv("DATABASE_POOL_SIZE", config.database.pool_size))
        config.database.timeout = float(os.getenv("DATABASE_TIMEOUT", config.database.timeout))
        
        # AI configuration
        config.ai.provider = AIProvider(os.getenv("AI_PROVIDER", config.ai.provider.value))
        config.ai.openai_api_key = os.getenv("OPENAI_API_KEY", config.ai.openai_api_key)
        config.ai.openai_model = os.getenv("OPENAI_MODEL", config.ai.openai_model)
        config.ai.openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", config.ai.openai_max_tokens))
        config.ai.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", config.ai.openai_temperature))
        config.ai.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", config.ai.anthropic_api_key)
        config.ai.anthropic_model = os.getenv("ANTHROPIC_MODEL", config.ai.anthropic_model)
        config.ai.anthropic_max_tokens = int(os.getenv("ANTHROPIC_MAX_TOKENS", config.ai.anthropic_max_tokens))
        config.ai.anthropic_temperature = float(os.getenv("ANTHROPIC_TEMPERATURE", config.ai.anthropic_temperature))
        
        # Research configuration
        config.research.max_results = int(os.getenv("RESEARCH_MAX_RESULTS", config.research.max_results))
        config.research.enable_web_scraping = os.getenv("ENABLE_WEB_SCRAPING", "false").lower() == "true"
        config.research.enable_caching = os.getenv("ENABLE_RESEARCH_CACHING", "true").lower() == "true"
        
        # Security configuration
        config.security.enable_authentication = os.getenv("ENABLE_AUTHENTICATION", "false").lower() == "true"
        config.security.jwt_secret_key = os.getenv("JWT_SECRET_KEY", config.security.jwt_secret_key)
        config.security.rate_limit_requests_per_minute = int(os.getenv("RATE_LIMIT_RPM", config.security.rate_limit_requests_per_minute))
        
        # Performance configuration
        config.performance.enable_caching = os.getenv("ENABLE_CACHING", "true").lower() == "true"
        config.performance.max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", config.performance.max_concurrent_requests))
        
        # Logging configuration
        config.logging.level = LogLevel(os.getenv("LOG_LEVEL", config.logging.level.value))
        config.logging.file_path = os.getenv("LOG_FILE_PATH", config.logging.file_path)
        config.logging.enable_console = os.getenv("ENABLE_CONSOLE_LOGGING", "true").lower() == "true"
        config.logging.enable_file = os.getenv("ENABLE_FILE_LOGGING", "true").lower() == "true"
        
        # Application settings
        config.app_name = os.getenv("APP_NAME", config.app_name)
        config.app_version = os.getenv("APP_VERSION", config.app_version)
        config.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        config.environment = os.getenv("ENVIRONMENT", config.environment)
        
        # Validate the configuration
        config._validate_config()
        
        return config
    
    @classmethod
    def from_file(cls, config_path: str) -> 'CosmicCouncilConfig':
        """Load configuration from a JSON file."""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        # Create configuration from file data
        config = cls()
        
        # Update configuration with file data
        for section, values in config_data.items():
            if hasattr(config, section):
                section_config = getattr(config, section)
                for key, value in values.items():
                    if hasattr(section_config, key):
                        setattr(section_config, key, value)
        
        config._validate_config()
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "database": {
                "db_path": self.database.db_path,
                "pool_size": self.database.pool_size,
                "timeout": self.database.timeout,
                "enable_wal_mode": self.database.enable_wal_mode,
                "enable_foreign_keys": self.database.enable_foreign_keys,
                "backup_enabled": self.database.backup_enabled,
                "backup_interval_hours": self.database.backup_interval_hours
            },
            "ai": {
                "provider": self.ai.provider.value,
                "openai_model": self.ai.openai_model,
                "openai_max_tokens": self.ai.openai_max_tokens,
                "openai_temperature": self.ai.openai_temperature,
                "anthropic_model": self.ai.anthropic_model,
                "anthropic_max_tokens": self.ai.anthropic_max_tokens,
                "anthropic_temperature": self.ai.anthropic_temperature,
                "request_timeout": self.ai.request_timeout,
                "max_retries": self.ai.max_retries,
                "retry_delay": self.ai.retry_delay
            },
            "research": {
                "max_results": self.research.max_results,
                "request_timeout": self.research.request_timeout,
                "max_retries": self.research.max_retries,
                "enable_web_scraping": self.research.enable_web_scraping,
                "enable_caching": self.research.enable_caching,
                "cache_ttl_hours": self.research.cache_ttl_hours,
                "user_agent": self.research.user_agent
            },
            "security": {
                "enable_authentication": self.security.enable_authentication,
                "jwt_expiration_hours": self.security.jwt_expiration_hours,
                "rate_limit_requests_per_minute": self.security.rate_limit_requests_per_minute,
                "enable_cors": self.security.enable_cors,
                "allowed_origins": self.security.allowed_origins,
                "enable_input_validation": self.security.enable_input_validation,
                "max_input_length": self.security.max_input_length
            },
            "performance": {
                "enable_caching": self.performance.enable_caching,
                "cache_ttl_seconds": self.performance.cache_ttl_seconds,
                "max_concurrent_requests": self.performance.max_concurrent_requests,
                "request_timeout": self.performance.request_timeout,
                "enable_metrics": self.performance.enable_metrics,
                "metrics_retention_days": self.performance.metrics_retention_days
            },
            "logging": {
                "level": self.logging.level.value,
                "format": self.logging.format,
                "file_path": self.logging.file_path,
                "max_file_size_mb": self.logging.max_file_size_mb,
                "backup_count": self.logging.backup_count,
                "enable_console": self.logging.enable_console,
                "enable_file": self.logging.enable_file
            },
            "app": {
                "name": self.app_name,
                "version": self.app_version,
                "debug_mode": self.debug_mode,
                "environment": self.environment
            }
        }
    
    def save_to_file(self, config_path: str):
        """Save configuration to a JSON file."""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        logging.info(f"Configuration saved to: {config_path}")


# Global configuration instance
_config: Optional[CosmicCouncilConfig] = None


def get_config() -> CosmicCouncilConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = CosmicCouncilConfig.from_env()
    return _config


def set_config(config: CosmicCouncilConfig):
    """Set the global configuration instance."""
    global _config
    _config = config


def initialize_config(config_path: str = None, from_env: bool = True) -> CosmicCouncilConfig:
    """Initialize the global configuration."""
    global _config
    
    if config_path and Path(config_path).exists():
        _config = CosmicCouncilConfig.from_file(config_path)
    elif from_env:
        _config = CosmicCouncilConfig.from_env()
    else:
        _config = CosmicCouncilConfig()
    
    return _config
