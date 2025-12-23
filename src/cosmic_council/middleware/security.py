"""
API Security Middleware for Cosmic Council.

Provides:
- JWT authentication
- Rate limiting
- Request validation
- Audit logging
"""

import asyncio
import hashlib
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Callable, Dict, Optional, List, Any

import jwt
import structlog
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


# ============== Configuration ==============

@dataclass
class SecurityConfig:
    """Security configuration."""
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    rate_limit_burst: int = 20
    allow_anonymous: bool = False
    audit_enabled: bool = True


# Default config - override in production
config = SecurityConfig()


# ============== JWT Authentication ==============

security = HTTPBearer(auto_error=False)


@dataclass
class TokenPayload:
    """JWT token payload."""
    sub: str  # Subject (user/service ID)
    exp: datetime
    iat: datetime
    roles: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)


def create_token(
    subject: str,
    roles: List[str] = None,
    scopes: List[str] = None,
    expires_in_hours: int = None,
) -> str:
    """Create a JWT token."""
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=expires_in_hours or config.jwt_expiry_hours)

    payload = {
        "sub": subject,
        "iat": now.timestamp(),
        "exp": expires.timestamp(),
        "roles": roles or [],
        "scopes": scopes or [],
    }

    return jwt.encode(payload, config.jwt_secret, algorithm=config.jwt_algorithm)


def decode_token(token: str) -> Optional[TokenPayload]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            config.jwt_secret,
            algorithms=[config.jwt_algorithm],
        )
        return TokenPayload(
            sub=payload["sub"],
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
            roles=payload.get("roles", []),
            scopes=payload.get("scopes", []),
        )
    except jwt.ExpiredSignatureError:
        logger.warning("jwt_expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning("jwt_invalid", error=str(e))
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[TokenPayload]:
    """FastAPI dependency to get current user from JWT."""
    if not credentials:
        if config.allow_anonymous:
            return None
        raise HTTPException(status_code=401, detail="Missing authentication")

    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


def require_role(required_role: str):
    """Decorator to require a specific role."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: TokenPayload = Depends(get_current_user), **kwargs):
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")
            if required_role not in user.roles:
                raise HTTPException(status_code=403, detail=f"Role '{required_role}' required")
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator


def require_scope(required_scope: str):
    """Decorator to require a specific scope."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: TokenPayload = Depends(get_current_user), **kwargs):
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")
            if required_scope not in user.scopes:
                raise HTTPException(status_code=403, detail=f"Scope '{required_scope}' required")
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator


# ============== Rate Limiting ==============

class RateLimiter:
    """
    Token bucket rate limiter.

    Allows burst traffic while enforcing average rate limits.
    """

    def __init__(
        self,
        requests_per_window: int = 100,
        window_seconds: int = 60,
        burst_size: int = 20,
    ):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.burst_size = burst_size
        self.tokens: Dict[str, float] = defaultdict(lambda: float(burst_size))
        self.last_update: Dict[str, float] = defaultdict(time.monotonic)
        self._lock = asyncio.Lock()

    def _get_key(self, request: Request) -> str:
        """Get rate limit key from request."""
        # Use IP address as default key
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"

        # Include user ID if authenticated
        user = getattr(request.state, "user", None)
        if user:
            return f"user:{user.sub}"
        return f"ip:{ip}"

    async def is_allowed(self, request: Request) -> bool:
        """Check if request is allowed under rate limit."""
        key = self._get_key(request)
        now = time.monotonic()

        async with self._lock:
            # Refill tokens based on time elapsed
            elapsed = now - self.last_update[key]
            refill = elapsed * (self.requests_per_window / self.window_seconds)
            self.tokens[key] = min(self.burst_size, self.tokens[key] + refill)
            self.last_update[key] = now

            # Check if we have tokens
            if self.tokens[key] >= 1:
                self.tokens[key] -= 1
                return True
            return False

    async def get_retry_after(self, request: Request) -> int:
        """Get seconds until next request is allowed."""
        key = self._get_key(request)
        tokens_needed = 1 - self.tokens[key]
        refill_rate = self.requests_per_window / self.window_seconds
        return max(1, int(tokens_needed / refill_rate))


# Global rate limiter instance
rate_limiter = RateLimiter(
    requests_per_window=config.rate_limit_requests,
    window_seconds=config.rate_limit_window_seconds,
    burst_size=config.rate_limit_burst,
)


# ============== Middleware ==============

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Combined security middleware.

    Handles:
    - Rate limiting
    - Request logging
    - Security headers
    """

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.monotonic()
        request_id = hashlib.sha256(
            f"{time.time()}{request.client.host if request.client else ''}".encode()
        ).hexdigest()[:12]

        # Add request ID to state
        request.state.request_id = request_id

        # Check rate limit
        if not await rate_limiter.is_allowed(request):
            retry_after = await rate_limiter.get_retry_after(request)
            logger.warning(
                "rate_limited",
                request_id=request_id,
                path=request.url.path,
                retry_after=retry_after,
            )
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers={"Retry-After": str(retry_after)},
            )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(
                "request_error",
                request_id=request_id,
                path=request.url.path,
                error=str(e),
            )
            raise

        # Add security headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Log request
        duration_ms = (time.monotonic() - start_time) * 1000
        logger.info(
            "request_completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(duration_ms, 2),
        )

        return response


# ============== Audit Logging ==============

@dataclass
class AuditEvent:
    """Audit log event."""
    event_type: str
    user_id: Optional[str]
    resource: str
    action: str
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    request_id: Optional[str] = None


class AuditLogger:
    """Audit logging service."""

    def __init__(self):
        self._events: List[AuditEvent] = []
        self._lock = asyncio.Lock()

    async def log(self, event: AuditEvent):
        """Log an audit event."""
        if not config.audit_enabled:
            return

        async with self._lock:
            self._events.append(event)

        logger.info(
            "audit_event",
            event_type=event.event_type,
            user_id=event.user_id,
            resource=event.resource,
            action=event.action,
            request_id=event.request_id,
        )

    async def get_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Query audit events."""
        async with self._lock:
            events = self._events.copy()

        if user_id:
            events = [e for e in events if e.user_id == user_id]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if since:
            events = [e for e in events if e.timestamp >= since]

        return events[-limit:]


# Global audit logger
audit_logger = AuditLogger()


# ============== Helper Functions ==============

def configure_security(
    jwt_secret: str = None,
    allow_anonymous: bool = None,
    rate_limit_requests: int = None,
    rate_limit_window_seconds: int = None,
):
    """Configure security settings."""
    global config, rate_limiter

    if jwt_secret:
        config.jwt_secret = jwt_secret
    if allow_anonymous is not None:
        config.allow_anonymous = allow_anonymous
    if rate_limit_requests:
        config.rate_limit_requests = rate_limit_requests
    if rate_limit_window_seconds:
        config.rate_limit_window_seconds = rate_limit_window_seconds

    # Recreate rate limiter with new settings
    rate_limiter = RateLimiter(
        requests_per_window=config.rate_limit_requests,
        window_seconds=config.rate_limit_window_seconds,
        burst_size=config.rate_limit_burst,
    )
