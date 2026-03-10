#!/usr/bin/env python3
"""
Production Configuration for Agent Orchestrator Framework
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ProductionConfig:
    """Production configuration settings"""
    
    # Datastore (Firestore)
    firestore_project_id: Optional[str] = None
    firestore_emulator_host: Optional[str] = None
    firebase_client_email: Optional[str] = None
    firebase_private_key: Optional[str] = None
    firebase_service_account_json: Optional[str] = None
    firebase_service_account_path: Optional[str] = None
    google_application_credentials: Optional[str] = None
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_reload: bool = False
    
    # Security
    secret_key: str = "change-this-in-production"
    jwt_secret_key: str = "change-this-jwt-secret"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: Optional[str] = None
    
    # Performance
    max_concurrent_cycles: int = 10
    session_timeout: int = 3600
    cache_ttl: int = 300
    
    # AI/LLM
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ai_confidence_threshold: float = 0.8
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 30
    
    # Environment
    debug: bool = False
    environment: str = "production"
    knowledge_base_url: str = "http://localhost:8001"
    
    @classmethod
    def from_env(cls) -> 'ProductionConfig':
        """Load configuration from environment variables"""
        return cls(
            firestore_project_id=os.getenv("FIREBASE_PROJECT_ID"),
            firestore_emulator_host=os.getenv("FIRESTORE_EMULATOR_HOST"),
            firebase_client_email=os.getenv("FIREBASE_CLIENT_EMAIL"),
            firebase_private_key=os.getenv("FIREBASE_PRIVATE_KEY"),
            firebase_service_account_json=os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON"),
            firebase_service_account_path=os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH"),
            google_application_credentials=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            
            api_host=os.getenv("API_HOST", cls.api_host),
            api_port=int(os.getenv("API_PORT", cls.api_port)),
            api_workers=int(os.getenv("API_WORKERS", cls.api_workers)),
            api_reload=os.getenv("API_RELOAD", "false").lower() == "true",
            
            secret_key=os.getenv("SECRET_KEY", cls.secret_key),
            jwt_secret_key=os.getenv("JWT_SECRET_KEY", cls.jwt_secret_key),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", cls.jwt_algorithm),
            jwt_expiration_hours=int(os.getenv("JWT_EXPIRATION_HOURS", cls.jwt_expiration_hours)),
            
            log_level=os.getenv("LOG_LEVEL", cls.log_level),
            log_format=os.getenv("LOG_FORMAT", cls.log_format),
            log_file=os.getenv("LOG_FILE", cls.log_file),
            
            max_concurrent_cycles=int(os.getenv("MAX_CONCURRENT_CYCLES", cls.max_concurrent_cycles)),
            session_timeout=int(os.getenv("SESSION_TIMEOUT", cls.session_timeout)),
            cache_ttl=int(os.getenv("CACHE_TTL", cls.cache_ttl)),
            
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            ai_confidence_threshold=float(os.getenv("AI_CONFIDENCE_THRESHOLD", cls.ai_confidence_threshold)),
            
            enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true",
            metrics_port=int(os.getenv("METRICS_PORT", cls.metrics_port)),
            health_check_interval=int(os.getenv("HEALTH_CHECK_INTERVAL", cls.health_check_interval)),
            
            debug=os.getenv("DEBUG", "false").lower() == "true",
            environment=os.getenv("ENVIRONMENT", cls.environment),
            knowledge_base_url=os.getenv("KNOWLEDGE_BASE_URL", cls.knowledge_base_url)
        )
    
    def setup_logging(self) -> None:
        """Setup production logging"""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        if self.log_format == "json":
            log_format = '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
        
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format=log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.log_file) if self.log_file else logging.NullHandler()
            ]
        )
    
    def validate(self) -> None:
        """Validate configuration"""
        if self.secret_key == "change-this-in-production":
            raise ValueError("SECRET_KEY must be changed in production")
        
        if self.jwt_secret_key == "change-this-jwt-secret":
            raise ValueError("JWT_SECRET_KEY must be changed in production")
        
        if self.environment == "production":
            if not self.firestore_project_id:
                raise ValueError("FIREBASE_PROJECT_ID is required in production")
            has_credentials = any([
                self.firebase_service_account_json,
                self.firebase_service_account_path,
                self.google_application_credentials,
                (self.firebase_client_email and self.firebase_private_key),
            ])
            if not has_credentials:
                raise ValueError("Firestore credentials are required in production")
        
        if self.api_port < 1 or self.api_port > 65535:
            raise ValueError("API_PORT must be between 1 and 65535")
        
        if self.max_concurrent_cycles < 1:
            raise ValueError("MAX_CONCURRENT_CYCLES must be at least 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "firestore_project_id": self.firestore_project_id,
            "firestore_emulator_host": self.firestore_emulator_host,
            "firebase_client_email": self.firebase_client_email,
            "firebase_private_key": "***" if self.firebase_private_key else None,
            "firebase_service_account_json": "***" if self.firebase_service_account_json else None,
            "firebase_service_account_path": self.firebase_service_account_path,
            "google_application_credentials": self.google_application_credentials,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "api_workers": self.api_workers,
            "api_reload": self.api_reload,
            "secret_key": "***" if self.secret_key != "change-this-in-production" else self.secret_key,
            "jwt_secret_key": "***" if self.jwt_secret_key != "change-this-jwt-secret" else self.jwt_secret_key,
            "jwt_algorithm": self.jwt_algorithm,
            "jwt_expiration_hours": self.jwt_expiration_hours,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "log_file": self.log_file,
            "max_concurrent_cycles": self.max_concurrent_cycles,
            "session_timeout": self.session_timeout,
            "cache_ttl": self.cache_ttl,
            "openai_api_key": "***" if self.openai_api_key else None,
            "anthropic_api_key": "***" if self.anthropic_api_key else None,
            "ai_confidence_threshold": self.ai_confidence_threshold,
            "enable_metrics": self.enable_metrics,
            "metrics_port": self.metrics_port,
            "health_check_interval": self.health_check_interval,
            "debug": self.debug,
            "environment": self.environment,
            "knowledge_base_url": self.knowledge_base_url
        }

# Global configuration instance
config = ProductionConfig.from_env()

def get_config() -> ProductionConfig:
    """Get the global configuration instance"""
    return config
