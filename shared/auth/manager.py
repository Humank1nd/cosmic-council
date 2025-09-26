"""
Authentication and authorization manager for the Cosmic Council system.
Provides JWT-based authentication and role-based access control.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import jwt
from ..config import get_settings
from ..database import get_db_connection
from ..logging import get_logger

logger = get_logger(__name__)

class UserRole(Enum):
    """User role enumeration."""
    ADMIN = "admin"
    COUNCIL_MEMBER = "council_member"
    ENTERPRISE_AGENT = "enterprise_agent"
    OBSERVER = "observer"
    SYSTEM = "system"

class Permission(Enum):
    """Permission enumeration."""
    READ_CYCLES = "read_cycles"
    WRITE_CYCLES = "write_cycles"
    EXECUTE_CYCLES = "execute_cycles"
    READ_ENTERPRISES = "read_enterprises"
    WRITE_ENTERPRISES = "write_enterprises"
    EXECUTE_ENTERPRISES = "execute_enterprises"
    READ_ANALYTICS = "read_analytics"
    WRITE_ANALYTICS = "write_analytics"
    READ_REFLECTION = "read_reflection"
    WRITE_REFLECTION = "write_reflection"
    MANAGE_USERS = "manage_users"
    MANAGE_SYSTEM = "manage_system"

@dataclass
class User:
    """User model."""
    id: str
    username: str
    email: str
    role: UserRole
    permissions: List[Permission]
    is_active: bool = True
    created_at: datetime = None
    last_login: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions
    
    def has_role(self, role: UserRole) -> bool:
        """Check if user has a specific role."""
        return self.role == role

@dataclass
class TokenData:
    """Token data model."""
    user_id: str
    username: str
    role: str
    permissions: List[str]
    exp: datetime
    iat: datetime

class AuthManager:
    """Authentication and authorization manager."""
    
    def __init__(self):
        self.settings = get_settings()
        self.jwt_secret = self.settings.secret_key
        self.algorithm = self.settings.algorithm
        self.access_token_expire_minutes = self.settings.access_token_expire_minutes
        
        # Role-based permissions mapping
        self.role_permissions = {
            UserRole.ADMIN: list(Permission),
            UserRole.COUNCIL_MEMBER: [
                Permission.READ_CYCLES,
                Permission.WRITE_CYCLES,
                Permission.EXECUTE_CYCLES,
                Permission.READ_ENTERPRISES,
                Permission.WRITE_ENTERPRISES,
                Permission.EXECUTE_ENTERPRISES,
                Permission.READ_ANALYTICS,
                Permission.READ_REFLECTION
            ],
            UserRole.ENTERPRISE_AGENT: [
                Permission.READ_CYCLES,
                Permission.READ_ENTERPRISES,
                Permission.WRITE_ENTERPRISES,
                Permission.EXECUTE_ENTERPRISES,
                Permission.READ_ANALYTICS
            ],
            UserRole.OBSERVER: [
                Permission.READ_CYCLES,
                Permission.READ_ENTERPRISES,
                Permission.READ_ANALYTICS,
                Permission.READ_REFLECTION
            ],
            UserRole.SYSTEM: [
                Permission.READ_CYCLES,
                Permission.WRITE_CYCLES,
                Permission.EXECUTE_CYCLES,
                Permission.READ_ENTERPRISES,
                Permission.WRITE_ENTERPRISES,
                Permission.EXECUTE_ENTERPRISES,
                Permission.READ_ANALYTICS,
                Permission.WRITE_ANALYTICS,
                Permission.READ_REFLECTION,
                Permission.WRITE_REFLECTION
            ]
        }
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            salt, password_hash = hashed_password.split(':')
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == password_hash
        except ValueError:
            return False
    
    def create_access_token(self, user: User) -> str:
        """Create a JWT access token for a user."""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "permissions": [p.value for p in user.permissions],
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(token_data, self.jwt_secret, algorithm=self.algorithm)
        logger.info(f"Access token created for user {user.username}")
        return token
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.algorithm])
            token_data = TokenData(
                user_id=payload["user_id"],
                username=payload["username"],
                role=payload["role"],
                permissions=payload["permissions"],
                exp=datetime.fromtimestamp(payload["exp"]),
                iat=datetime.fromtimestamp(payload["iat"])
            )
            return token_data
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def get_user_permissions(self, role: UserRole) -> List[Permission]:
        """Get permissions for a role."""
        return self.role_permissions.get(role, [])
    
    def check_permission(self, user: User, permission: Permission) -> bool:
        """Check if a user has a specific permission."""
        return user.has_permission(permission)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        try:
            # TODO: Implement database user lookup
            # For now, return a mock user
            if username == "admin" and password == "admin":
                return User(
                    id="admin-001",
                    username="admin",
                    email="admin@cosmiccouncil.org",
                    role=UserRole.ADMIN,
                    permissions=self.get_user_permissions(UserRole.ADMIN)
                )
            return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        try:
            # TODO: Implement database user lookup
            # For now, return a mock user
            if user_id == "admin-001":
                return User(
                    id="admin-001",
                    username="admin",
                    email="admin@cosmiccouncil.org",
                    role=UserRole.ADMIN,
                    permissions=self.get_user_permissions(UserRole.ADMIN)
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    async def create_user(self, username: str, email: str, password: str, role: UserRole) -> Optional[User]:
        """Create a new user."""
        try:
            hashed_password = self.hash_password(password)
            user = User(
                id=f"user-{secrets.token_hex(8)}",
                username=username,
                email=email,
                role=role,
                permissions=self.get_user_permissions(role)
            )
            
            # TODO: Save user to database
            logger.info(f"User created: {username}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

# Global auth manager instance
_auth_manager: Optional[AuthManager] = None

def get_auth_manager() -> AuthManager:
    """Get the global auth manager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager

# Convenience functions
def create_access_token(user: User) -> str:
    """Create an access token for a user."""
    auth_manager = get_auth_manager()
    return auth_manager.create_access_token(user)

def verify_token(token: str) -> Optional[TokenData]:
    """Verify a JWT token."""
    auth_manager = get_auth_manager()
    return auth_manager.verify_token(token)

def check_permission(user: User, permission: Permission) -> bool:
    """Check if a user has a specific permission."""
    auth_manager = get_auth_manager()
    return auth_manager.check_permission(user, permission)
