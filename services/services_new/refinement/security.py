"""
Cosmic Council Refinement Engine - Security Layer
Implements authentication, authorization, input validation, and security controls.
"""

import os
import secrets
import hashlib
import hmac
import time
from typing import Dict, Any, Optional, List, Set, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import asyncio
from functools import wraps

import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
import redis.asyncio as redis
from fastapi import HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel, Field, validator, root_validator
import structlog

try:
    from .error_handling import ErrorHandler, ErrorSeverity, ErrorCategory, error_handler
except ImportError:
    # For testing
    from error_handling import ErrorHandler, ErrorSeverity, ErrorCategory, error_handler


class UserRole(Enum):
    """User roles for authorization."""
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"
    SERVICE = "service"


class Permission(Enum):
    """System permissions."""
    CREATE_PROBLEM = "create_problem"
    READ_PROBLEM = "read_problem"
    UPDATE_PROBLEM = "update_problem"
    DELETE_PROBLEM = "delete_problem"
    EXECUTE_LAYER_RUN = "execute_layer_run"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_USERS = "manage_users"
    SYSTEM_ADMIN = "system_admin"


@dataclass
class User:
    """User model for authentication."""
    user_id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    permissions: Set[Permission] = field(default_factory=set)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None


@dataclass
class APIKey:
    """API key model for service authentication."""
    key_id: str
    key_hash: str
    name: str
    user_id: str
    permissions: Set[Permission] = field(default_factory=set)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None


@dataclass
class SecurityContext:
    """Security context for request processing."""
    user: Optional[User] = None
    api_key: Optional[APIKey] = None
    permissions: Set[Permission] = field(default_factory=set)
    request_id: str = ""
    ip_address: str = ""
    user_agent: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# Pydantic models for validation
class LoginRequest(BaseModel):
    """Login request model."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must contain only alphanumeric characters, underscores, and hyphens')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class ProblemSubmissionRequest(BaseModel):
    """Validated problem submission request."""
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=10, max_length=10000)
    initial_layer: str = Field(default="deci")
    max_iterations: int = Field(default=100, ge=1, le=1000)
    
    @validator('title')
    def validate_title(cls, v):
        # Remove potentially dangerous characters
        v = re.sub(r'[<>"\']', '', v)
        if len(v.strip()) < 5:
            raise ValueError('Title must be at least 5 characters long')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        # Remove potentially dangerous characters
        v = re.sub(r'[<>"\']', '', v)
        if len(v.strip()) < 10:
            raise ValueError('Description must be at least 10 characters long')
        return v.strip()
    
    @validator('initial_layer')
    def validate_initial_layer(cls, v):
        valid_layers = ['deci', 'centi', 'milli', 'micro', 'nano', 'pico', 
                       'femto', 'atto', 'zepto', 'yocto', 'ronto', 'quecto']
        if v not in valid_layers:
            raise ValueError(f'Initial layer must be one of: {", ".join(valid_layers)}')
        return v


class UserCreateRequest(BaseModel):
    """User creation request model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(default="user")
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must contain only alphanumeric characters, underscores, and hyphens')
        return v.lower()
    
    @validator('email')
    def validate_email(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        valid_roles = ['admin', 'user', 'readonly', 'service']
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v


class SecurityManager:
    """
    Centralized security manager for authentication, authorization, and validation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize security manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._get_default_config()
        self.logger = structlog.get_logger(__name__)
        
        # Password hashing (use pbkdf2_sha256 for better compatibility)
        self.pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        
        # JWT settings
        self.secret_key = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
        self.algorithm = "HS256"
        self.access_token_expire_minutes = self.config["access_token_expire_minutes"]
        
        # Redis for session management
        self.redis_client = None
        
        # In-memory storage for demo (replace with database in production)
        self.users: Dict[str, User] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Rate limiting
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default admin user
        self._create_default_admin()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default security configuration."""
        return {
            "access_token_expire_minutes": 30,
            "refresh_token_expire_days": 7,
            "max_login_attempts": 5,
            "lockout_duration_minutes": 30,
            "api_key_expire_days": 365,
            "rate_limit_requests_per_minute": 60,
            "rate_limit_requests_per_hour": 1000,
            "enable_brute_force_protection": True,
            "enable_rate_limiting": True,
            "enable_input_sanitization": True,
            "enable_cors": True,
            "allowed_origins": ["*"],
            "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
            "allowed_headers": ["*"]
        }
    
    async def initialize_redis(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis connection for session management."""
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            self.logger.info("Redis connection established for session management")
        except Exception as e:
            self.logger.warning(f"Redis connection failed, using in-memory storage: {e}")
            self.redis_client = None
    
    def _create_default_admin(self):
        """Create default admin user."""
        admin_user = User(
            user_id="admin",
            username="admin",
            email="admin@cosmiccouncil.com",
            password_hash=self.hash_password("admin123"),
            role=UserRole.ADMIN,
            permissions={
                Permission.CREATE_PROBLEM,
                Permission.READ_PROBLEM,
                Permission.UPDATE_PROBLEM,
                Permission.DELETE_PROBLEM,
                Permission.EXECUTE_LAYER_RUN,
                Permission.VIEW_ANALYTICS,
                Permission.MANAGE_USERS,
                Permission.SYSTEM_ADMIN
            }
        )
        self.users["admin"] = admin_user
        self.logger.info("Default admin user created")
    
    def hash_password(self, password: str) -> str:
        """Hash a password."""
        # Truncate password to 72 bytes to avoid bcrypt limit
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user_id: str, permissions: Set[Permission]) -> str:
        """Create JWT access token."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "permissions": [p.value for p in permissions]
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT access token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        user = self.users.get(username)
        if not user:
            return None
        
        # Check if user is locked
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            self.logger.warning(f"Login attempt for locked user: {username}")
            return None
        
        # Check if user is active
        if not user.is_active:
            self.logger.warning(f"Login attempt for inactive user: {username}")
            return None
        
        # Verify password
        if not self.verify_password(password, user.password_hash):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            
            # Lock user if max attempts exceeded
            if user.failed_login_attempts >= self.config["max_login_attempts"]:
                user.locked_until = datetime.now(timezone.utc) + timedelta(
                    minutes=self.config["lockout_duration_minutes"]
                )
                self.logger.warning(f"User {username} locked due to failed login attempts")
            
            return None
        
        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now(timezone.utc)
        
        return user
    
    async def create_user(self, user_data: UserCreateRequest) -> User:
        """Create a new user."""
        # Check if username already exists
        if user_data.username in self.users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email already exists
        for user in self.users.values():
            if user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        # Create user
        user = User(
            user_id=secrets.token_urlsafe(16),
            username=user_data.username,
            email=user_data.email,
            password_hash=self.hash_password(user_data.password),
            role=UserRole(user_data.role),
            permissions=self._get_default_permissions(UserRole(user_data.role))
        )
        
        # Store user
        self.users[user_data.username] = user
        
        self.logger.info(f"User created: {user_data.username}")
        return user
    
    def _get_default_permissions(self, role: UserRole) -> Set[Permission]:
        """Get default permissions for a role."""
        if role == UserRole.ADMIN:
            return {
                Permission.CREATE_PROBLEM,
                Permission.READ_PROBLEM,
                Permission.UPDATE_PROBLEM,
                Permission.DELETE_PROBLEM,
                Permission.EXECUTE_LAYER_RUN,
                Permission.VIEW_ANALYTICS,
                Permission.MANAGE_USERS,
                Permission.SYSTEM_ADMIN
            }
        elif role == UserRole.USER:
            return {
                Permission.CREATE_PROBLEM,
                Permission.READ_PROBLEM,
                Permission.EXECUTE_LAYER_RUN,
                Permission.VIEW_ANALYTICS
            }
        elif role == UserRole.READONLY:
            return {
                Permission.READ_PROBLEM,
                Permission.VIEW_ANALYTICS
            }
        elif role == UserRole.SERVICE:
            return {
                Permission.CREATE_PROBLEM,
                Permission.READ_PROBLEM,
                Permission.EXECUTE_LAYER_RUN
            }
        else:
            return set()
    
    async def create_api_key(self, name: str, user_id: str, permissions: Set[Permission]) -> str:
        """Create a new API key."""
        # Generate API key
        api_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Create API key record
        api_key_record = APIKey(
            key_id=secrets.token_urlsafe(16),
            key_hash=key_hash,
            name=name,
            user_id=user_id,
            permissions=permissions,
            expires_at=datetime.now(timezone.utc) + timedelta(days=self.config["api_key_expire_days"])
        )
        
        # Store API key
        self.api_keys[key_hash] = api_key_record
        
        self.logger.info(f"API key created: {name}")
        return api_key
    
    async def authenticate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Authenticate an API key."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        api_key_record = self.api_keys.get(key_hash)
        
        if not api_key_record:
            return None
        
        # Check if API key is active
        if not api_key_record.is_active:
            return None
        
        # Check if API key has expired
        if api_key_record.expires_at and api_key_record.expires_at < datetime.now(timezone.utc):
            return None
        
        # Update last used
        api_key_record.last_used = datetime.now(timezone.utc)
        
        return api_key_record
    
    def check_permission(self, user_permissions: Set[Permission], required_permission: Permission) -> bool:
        """Check if user has required permission."""
        return required_permission in user_permissions
    
    def check_permissions(self, user_permissions: Set[Permission], required_permissions: Set[Permission]) -> bool:
        """Check if user has all required permissions."""
        return required_permissions.issubset(user_permissions)
    
    async def rate_limit_check(self, identifier: str, limit: int, window: int) -> bool:
        """Check if request is within rate limit."""
        if not self.config["enable_rate_limiting"]:
            return True
        
        current_time = int(time.time())
        window_start = current_time - window
        
        # Get current requests for this identifier
        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = []
        
        # Remove old requests outside the window
        self.rate_limits[identifier] = [
            req_time for req_time in self.rate_limits[identifier]
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(self.rate_limits[identifier]) >= limit:
            return False
        
        # Add current request
        self.rate_limits[identifier].append(current_time)
        return True
    
    def sanitize_input(self, input_string: str) -> str:
        """Sanitize input string to prevent injection attacks."""
        if not self.config["enable_input_sanitization"]:
            return input_string
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', input_string)
        
        # Remove SQL injection patterns
        sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)',
            r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
            r'(\b(OR|AND)\s+\w+\s*=\s*\w+)',
            r'(\b(OR|AND)\s+\w+\s*LIKE\s*[\'"])',
            r'(\b(OR|AND)\s+\w+\s*IN\s*\()',
        ]
        
        for pattern in sql_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Remove script tags
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove javascript: protocols
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    def validate_problem_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize problem input data."""
        validated_data = {}
        
        # Validate title
        if 'title' in data:
            title = self.sanitize_input(str(data['title']))
            if len(title) < 5 or len(title) > 500:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Title must be between 5 and 500 characters"
                )
            validated_data['title'] = title
        
        # Validate description
        if 'description' in data:
            description = self.sanitize_input(str(data['description']))
            if len(description) < 10 or len(description) > 10000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Description must be between 10 and 10000 characters"
                )
            validated_data['description'] = description
        
        # Validate initial_layer
        if 'initial_layer' in data:
            valid_layers = ['deci', 'centi', 'milli', 'micro', 'nano', 'pico', 
                           'femto', 'atto', 'zepto', 'yocto', 'ronto', 'quecto']
            if data['initial_layer'] not in valid_layers:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Initial layer must be one of: {', '.join(valid_layers)}"
                )
            validated_data['initial_layer'] = data['initial_layer']
        
        # Validate max_iterations
        if 'max_iterations' in data:
            try:
                max_iterations = int(data['max_iterations'])
                if max_iterations < 1 or max_iterations > 1000:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Max iterations must be between 1 and 1000"
                    )
                validated_data['max_iterations'] = max_iterations
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Max iterations must be a valid integer"
                )
        
        return validated_data


# Global security manager instance
_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """Get the global security manager instance."""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


def initialize_security(config: Optional[Dict[str, Any]] = None) -> SecurityManager:
    """
    Initialize security system.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Security manager instance
    """
    global _security_manager
    _security_manager = SecurityManager(config)
    return _security_manager


# FastAPI dependencies
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user."""
    security_manager = get_security_manager()
    
    # Verify token
    payload = security_manager.verify_access_token(credentials.credentials)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Get user
    user = None
    for u in security_manager.users.values():
        if u.user_id == user_id:
            user = u
            break
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


async def get_current_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> APIKey:
    """Get current authenticated API key."""
    security_manager = get_security_manager()
    
    # Authenticate API key
    api_key = await security_manager.authenticate_api_key(credentials.credentials)
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return api_key


def require_permission(permission: Permission):
    """Decorator to require specific permission."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get security context from request
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )
            
            # Get user from request state
            user = getattr(request.state, 'user', None)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not authenticated"
                )
            
            # Check permission
            security_manager = get_security_manager()
            if not security_manager.check_permission(user.permissions, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {permission.value}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_permissions(permissions: Set[Permission]):
    """Decorator to require multiple permissions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get security context from request
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )
            
            # Get user from request state
            user = getattr(request.state, 'user', None)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not authenticated"
                )
            
            # Check permissions
            security_manager = get_security_manager()
            if not security_manager.check_permissions(user.permissions, permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissions required: {[p.value for p in permissions]}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def rate_limit_dependency(request: Request):
    """Rate limiting dependency."""
    security_manager = get_security_manager()
    
    # Get client identifier
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    identifier = f"{client_ip}:{hash(user_agent)}"
    
    # Check rate limit
    if not await security_manager.rate_limit_check(identifier, 60, 60):  # 60 requests per minute
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_security():
        print("=== Security System Test ===")
        
        # Initialize security manager
        security_manager = initialize_security()
        
        # Test user creation
        user_data = UserCreateRequest(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
            role="user"
        )
        
        try:
            user = await security_manager.create_user(user_data)
            print(f"User created: {user.username}")
        except Exception as e:
            print(f"User creation failed: {e}")
        
        # Test authentication
        try:
            authenticated_user = await security_manager.authenticate_user("testuser", "TestPassword123!")
            if authenticated_user:
                print(f"User authenticated: {authenticated_user.username}")
                
                # Create access token
                token = security_manager.create_access_token(
                    authenticated_user.user_id,
                    authenticated_user.permissions
                )
                print(f"Access token created: {token[:50]}...")
                
                # Verify token
                payload = security_manager.verify_access_token(token)
                print(f"Token verified: {payload['sub']}")
            else:
                print("Authentication failed")
        except Exception as e:
            print(f"Authentication test failed: {e}")
        
        # Test API key creation
        try:
            api_key = await security_manager.create_api_key(
                "test-key",
                "testuser",
                {Permission.CREATE_PROBLEM, Permission.READ_PROBLEM}
            )
            print(f"API key created: {api_key[:20]}...")
            
            # Test API key authentication
            api_key_record = await security_manager.authenticate_api_key(api_key)
            if api_key_record:
                print(f"API key authenticated: {api_key_record.name}")
            else:
                print("API key authentication failed")
        except Exception as e:
            print(f"API key test failed: {e}")
        
        # Test input validation
        try:
            validated_data = security_manager.validate_problem_input({
                "title": "Test Problem",
                "description": "This is a test problem description",
                "initial_layer": "deci",
                "max_iterations": 100
            })
            print(f"Input validated: {validated_data}")
        except Exception as e:
            print(f"Input validation failed: {e}")
    
    # Run the test
    asyncio.run(test_security())
