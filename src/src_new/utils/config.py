"""
Configuration management for the Cosmic Council system.
"""

import os
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    """Application configuration"""
    
    # Application settings
    app_name: str = "Cosmic Council"
    app_version: str = "2.0.0"
    debug: bool = False
    environment: str = "development"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    
    # Database settings
    database_url: str = "sqlite:///data/dream_caesar.db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Security settings
    secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 1 hour
    
    # AI/LLM settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_llm_provider: str = "mock"
    default_llm_model: str = "mock-model"
    
    # Monitoring settings
    enable_monitoring: bool = True
    prometheus_port: int = 9090
    grafana_port: int = 3000
    
    # Logging settings
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_format: str = "standard"
    
    # Cache settings
    redis_url: Optional[str] = None
    cache_ttl: int = 3600  # 1 hour
    
    # File storage settings
    upload_path: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    # Additional settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables"""
        return cls(
            # Application settings
            app_name=os.getenv("APP_NAME", "Cosmic Council"),
            app_version=os.getenv("APP_VERSION", "2.0.0"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            environment=os.getenv("ENVIRONMENT", "development"),
            
            # API settings
            api_host=os.getenv("API_HOST", "0.0.0.0"),
            api_port=int(os.getenv("API_PORT", "8000")),
            api_workers=int(os.getenv("API_WORKERS", "1")),
            
            # Database settings
            database_url=os.getenv("DATABASE_URL", "sqlite:///data/dream_caesar.db"),
            database_pool_size=int(os.getenv("DATABASE_POOL_SIZE", "10")),
            database_max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "20")),
            
            # Security settings
            secret_key=os.getenv("SECRET_KEY", "your-secret-key-here"),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            jwt_expiration=int(os.getenv("JWT_EXPIRATION", "3600")),
            
            # AI/LLM settings
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            default_llm_provider=os.getenv("DEFAULT_LLM_PROVIDER", "mock"),
            default_llm_model=os.getenv("DEFAULT_LLM_MODEL", "mock-model"),
            
            # Monitoring settings
            enable_monitoring=os.getenv("ENABLE_MONITORING", "true").lower() == "true",
            prometheus_port=int(os.getenv("PROMETHEUS_PORT", "9090")),
            grafana_port=int(os.getenv("GRAFANA_PORT", "3000")),
            
            # Logging settings
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE"),
            log_format=os.getenv("LOG_FORMAT", "standard"),
            
            # Cache settings
            redis_url=os.getenv("REDIS_URL"),
            cache_ttl=int(os.getenv("CACHE_TTL", "3600")),
            
            # File storage settings
            upload_path=os.getenv("UPLOAD_PATH", "uploads"),
            max_file_size=int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024))),
            
            # Rate limiting
            rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
            rate_limit_window=int(os.getenv("RATE_LIMIT_WINDOW", "3600")),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return getattr(self, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key"""
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            self.custom_settings[key] = value
    
    def validate(self) -> bool:
        """Validate configuration"""
        # Check required settings
        if not self.secret_key or self.secret_key == "your-secret-key-here":
            if self.environment == "production":
                return False
        
        # Check database URL
        if not self.database_url:
            return False
        
        # Check API settings
        if self.api_port <= 0 or self.api_port > 65535:
            return False
        
        return True


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance"""
    global _config
    _config = config


def load_config_from_file(config_file: str) -> Config:
    """Load configuration from a file"""
    config_path = Path(config_file)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    # This would load from YAML, JSON, or other formats
    # For now, return default config
    return Config.from_env()
