"""
Authentication middleware for the API.
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware"""
    
    def __init__(self, app, secret_key: str = None):
        super().__init__(app)
        self.secret_key = secret_key or "default-secret-key"
    
    async def dispatch(self, request: Request, call_next):
        """Process request with authentication"""
        try:
            # Skip auth for health checks and public endpoints
            if self._is_public_endpoint(request.url.path):
                return await call_next(request)
            
            # Extract token from Authorization header
            authorization = request.headers.get("Authorization")
            if not authorization:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization header required"
                )
            
            # Validate token (simplified implementation)
            if not self._validate_token(authorization):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Add user info to request state
            request.state.user = self._extract_user_from_token(authorization)
            
            return await call_next(request)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication error"
            )
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no auth required)"""
        public_paths = [
            "/api/v1/health",
            "/docs",
            "/openapi.json",
            "/redoc"
        ]
        return any(path.startswith(public_path) for public_path in public_paths)
    
    def _validate_token(self, authorization: str) -> bool:
        """Validate authentication token (simplified)"""
        # In a real implementation, this would validate JWT tokens
        # For now, just check if it starts with "Bearer "
        return authorization.startswith("Bearer ")
    
    def _extract_user_from_token(self, authorization: str) -> dict:
        """Extract user information from token (simplified)"""
        # In a real implementation, this would decode JWT and extract user info
        # For now, return a mock user
        return {
            "user_id": "mock-user-id",
            "username": "mock-user",
            "role": "user"
        }
