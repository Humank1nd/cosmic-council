# Shared utilities and libraries for the Cosmic Council
# This package provides common functionality across all services and enterprises

from .database import DatabaseManager, get_db_connection
from .logging import get_logger, setup_logging
from .auth import AuthManager, get_current_user
from .config import Settings, get_settings
from .exceptions import CosmicCouncilException, ValidationError, DatabaseError
from .utils import generate_uuid, format_timestamp, validate_email
from .validators import validate_enterprise_type, validate_cycle_status
from .serializers import JSONEncoder, serialize_result
from .cache import CacheManager, get_cache
from .middleware import RequestLoggingMiddleware, ErrorHandlingMiddleware

__all__ = [
    # Database
    'DatabaseManager',
    'get_db_connection',
    
    # Logging
    'get_logger',
    'setup_logging',
    
    # Authentication
    'AuthManager',
    'get_current_user',
    
    # Configuration
    'Settings',
    'get_settings',
    
    # Exceptions
    'CosmicCouncilException',
    'ValidationError',
    'DatabaseError',
    
    # Utilities
    'generate_uuid',
    'format_timestamp',
    'validate_email',
    
    # Validators
    'validate_enterprise_type',
    'validate_cycle_status',
    
    # Serializers
    'JSONEncoder',
    'serialize_result',
    
    # Cache
    'CacheManager',
    'get_cache',
    
    # Middleware
    'RequestLoggingMiddleware',
    'ErrorHandlingMiddleware'
]

__version__ = "1.0.0"
__author__ = "Cosmic Council"
__description__ = "Shared utilities and libraries for the Cosmic Council system"
