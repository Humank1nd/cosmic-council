# 🧩 Shared Libraries & Utilities

This directory contains common utilities, libraries, and shared functionality used across all services and enterprises in the Cosmic Council system.

## 📁 **Directory Structure**

```
shared/
├── __init__.py                 # Package initialization and exports
├── README.md                   # This documentation
├── database/                   # Database utilities and models
│   ├── __init__.py
│   ├── connection.py          # Connection management and pooling
│   ├── models.py              # Base models and mixins
│   ├── migrations.py          # Database migration utilities
│   ├── queries.py             # Query builders and helpers
│   └── transactions.py        # Transaction management
├── logging/                    # Logging configuration and utilities
│   ├── __init__.py
│   ├── logger.py              # Logger setup and configuration
│   ├── formatters.py          # Custom log formatters
│   ├── handlers.py            # Custom log handlers
│   └── middleware.py          # Logging middleware
├── auth/                       # Authentication and authorization
│   ├── __init__.py
│   ├── manager.py             # Auth manager and JWT handling
│   ├── jwt.py                 # JWT utilities
│   ├── permissions.py         # Permission management
│   ├── middleware.py          # Auth middleware
│   └── models.py              # User and role models
├── config/                     # Configuration management
│   ├── __init__.py
│   ├── settings.py            # Settings and configuration
│   ├── environment.py         # Environment management
│   └── secrets.py             # Secret management
├── utils/                      # Common utility functions
│   ├── __init__.py
│   ├── common.py              # Common utilities
│   ├── datetime.py            # DateTime utilities
│   ├── validation.py          # Validation utilities
│   ├── crypto.py              # Cryptographic utilities
│   ├── files.py               # File utilities
│   ├── network.py             # Network utilities
│   └── text.py                # Text processing utilities
├── exceptions/                 # Custom exception classes
│   ├── __init__.py
│   ├── base.py                # Base exception classes
│   ├── business.py            # Business logic exceptions
│   └── infrastructure.py      # Infrastructure exceptions
├── middleware/                 # FastAPI middleware
│   ├── __init__.py
│   ├── auth.py                # Authentication middleware
│   ├── logging.py             # Logging middleware
│   ├── cors.py                # CORS middleware
│   └── rate_limit.py          # Rate limiting middleware
├── validators/                 # Data validation utilities
│   ├── __init__.py
│   ├── schemas.py             # Pydantic schemas
│   ├── validators.py          # Custom validators
│   └── sanitizers.py          # Data sanitizers
├── serializers/                # Data serialization utilities
│   ├── __init__.py
│   ├── json.py                # JSON serialization
│   ├── xml.py                 # XML serialization
│   └── csv.py                 # CSV serialization
└── cache/                      # Caching utilities
    ├── __init__.py
    ├── manager.py             # Cache manager
    ├── redis.py               # Redis cache implementation
    └── memory.py              # In-memory cache implementation
```

## 🗄️ **Database Utilities**

### **Connection Management**
```python
from shared.database import get_db_connection, DatabaseManager

# Get database connection
async with get_db_connection() as conn:
    result = await conn.fetch("SELECT * FROM cycles")

# Use database manager
db_manager = DatabaseManager()
await db_manager.initialize()
result = await db_manager.fetch("SELECT * FROM cycles")
```

### **Base Models**
```python
from shared.database import BaseModel, TimestampMixin, StatusMixin

class MyModel(BaseModel, TimestampMixin, StatusMixin):
    def validate(self) -> bool:
        return True
```

## 📝 **Logging System**

### **Logger Setup**
```python
from shared.logging import get_logger, setup_logging

# Setup logging
setup_logging()

# Get logger
logger = get_logger(__name__)
logger.info("Application started")
```

### **Structured Logging**
```python
from shared.logging import get_cosmic_logger

logger = get_cosmic_logger()
logger.set_context(cycle_id="cycle-001", user_id="user-123")
logger.info("Cycle started")
```

## 🔐 **Authentication & Authorization**

### **User Authentication**
```python
from shared.auth import get_auth_manager, create_access_token

auth_manager = get_auth_manager()
user = await auth_manager.authenticate_user("username", "password")
token = create_access_token(user)
```

### **Permission Checking**
```python
from shared.auth import check_permission, Permission

if check_permission(user, Permission.READ_CYCLES):
    # User has permission
    pass
```

## ⚙️ **Configuration Management**

### **Settings Access**
```python
from shared.config import get_settings

settings = get_settings()
db_url = settings.get_database_url()
service_url = settings.get_service_url("gateway")
```

### **Environment Variables**
```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cosmic_council
DB_USER=cosmic_council
DB_PASSWORD=cosmic_council

# Logging
LOG_LEVEL=INFO
LOG_JSON=true
LOG_FILE=logs/cosmic_council.log

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🛠️ **Utility Functions**

### **Common Utilities**
```python
from shared.utils import (
    generate_uuid, format_timestamp, validate_email,
    sanitize_string, hash_string, generate_random_string
)

# Generate UUID
id = generate_uuid()

# Format timestamp
timestamp = format_timestamp()

# Validate email
is_valid = validate_email("user@example.com")

# Sanitize string
clean_text = sanitize_string("<script>alert('xss')</script>")

# Hash string
hash_value = hash_string("password", "sha256")

# Generate random string
random_string = generate_random_string(32)
```

### **Text Processing**
```python
from shared.utils import truncate_text, slugify, extract_keywords

# Truncate text
short_text = truncate_text("Long text here", 10)

# Create slug
slug = slugify("My Awesome Title!")

# Extract keywords
keywords = extract_keywords("This is a sample text for keyword extraction")
```

## 🚨 **Exception Handling**

### **Custom Exceptions**
```python
from shared.exceptions import (
    CosmicCouncilException, ValidationError, DatabaseError,
    AuthenticationError, AuthorizationError
)

# Raise custom exceptions
raise ValidationError("Invalid input", field="email", value="invalid-email")
raise DatabaseError("Query failed", query="SELECT * FROM users", table="users")
raise AuthenticationError("Invalid credentials", user_id="user-123")
```

### **Exception Context**
```python
try:
    # Some operation
    pass
except Exception as e:
    raise CosmicCouncilException(
        "Operation failed",
        error_code="OPERATION_FAILED",
        context={"operation": "user_creation", "user_id": "user-123"},
        cause=e
    )
```

## 🔄 **Middleware**

### **FastAPI Middleware**
```python
from fastapi import FastAPI
from shared.middleware import (
    RequestLoggingMiddleware, ErrorHandlingMiddleware,
    AuthMiddleware, CORSMiddleware
)

app = FastAPI()

# Add middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(CORSMiddleware)
```

## ✅ **Validation**

### **Data Validation**
```python
from shared.validators import validate_enterprise_type, validate_cycle_status

# Validate enterprise type
is_valid = validate_enterprise_type("red_research")

# Validate cycle status
is_valid = validate_cycle_status("active")
```

### **Pydantic Schemas**
```python
from shared.validators import BaseSchema, TimestampSchema

class CycleSchema(BaseSchema, TimestampSchema):
    objective_ref: str
    status: str
```

## 📊 **Serialization**

### **JSON Serialization**
```python
from shared.serializers import JSONEncoder, serialize_result

# Custom JSON encoder
encoder = JSONEncoder()

# Serialize result
result = serialize_result(data)
```

## 💾 **Caching**

### **Cache Management**
```python
from shared.cache import get_cache, CacheManager

# Get cache instance
cache = get_cache()

# Set cache
await cache.set("key", "value", ttl=300)

# Get cache
value = await cache.get("key")
```

## 🧪 **Testing Utilities**

### **Test Helpers**
```python
from shared.utils import generate_uuid, format_timestamp
from shared.database import get_db_connection
from shared.auth import get_auth_manager

# Test data generation
test_id = generate_uuid()
test_timestamp = format_timestamp()

# Test database connection
async with get_db_connection() as conn:
    # Test database operations
    pass

# Test authentication
auth_manager = get_auth_manager()
test_user = await auth_manager.authenticate_user("test", "test")
```

## 🔧 **Development Guidelines**

### **Import Guidelines**
```python
# Preferred imports
from shared.database import get_db_connection
from shared.logging import get_logger
from shared.auth import get_auth_manager
from shared.config import get_settings

# Avoid direct imports from submodules
# from shared.database.connection import DatabaseManager  # Don't do this
```

### **Error Handling**
```python
from shared.exceptions import CosmicCouncilException
from shared.logging import get_logger

logger = get_logger(__name__)

try:
    # Some operation
    pass
except Exception as e:
    logger.error(f"Operation failed: {e}")
    raise CosmicCouncilException("Operation failed", cause=e)
```

### **Configuration**
```python
from shared.config import get_settings

settings = get_settings()

# Use settings for configuration
if settings.is_production():
    # Production-specific logic
    pass
elif settings.is_development():
    # Development-specific logic
    pass
```

## 🚀 **Usage Examples**

### **Service Initialization**
```python
from shared.logging import setup_logging, get_logger
from shared.config import get_settings
from shared.database import get_db_manager

# Initialize shared components
setup_logging()
settings = get_settings()
db_manager = await get_db_manager()

logger = get_logger(__name__)
logger.info("Service initialized successfully")
```

### **Request Handling**
```python
from fastapi import FastAPI, Depends
from shared.database import get_db
from shared.auth import get_current_user
from shared.logging import get_logger

app = FastAPI()
logger = get_logger(__name__)

@app.get("/cycles")
async def get_cycles(
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    logger.info(f"User {current_user.username} requested cycles")
    # Handle request
    pass
```

## 🏛️ **The Sacred Shared Libraries**

The shared libraries embody the **nervous system** of the Cosmic Council:

- **Database utilities** as the **memory system** - storing and retrieving knowledge
- **Logging system** as the **consciousness** - aware of all system activities
- **Authentication** as the **identity system** - knowing who is who
- **Configuration** as the **genetic code** - defining system behavior
- **Utilities** as the **tools** - common functions for all operations
- **Exceptions** as the **immune system** - handling errors gracefully
- **Middleware** as the **nervous pathways** - processing requests and responses

Each component works together to create a **unified, consistent, and maintainable system** that supports the continuous evolution of the Cosmic Council.

**This is not just shared code - it's the foundation upon which all services and enterprises can build and thrive.** 🏛️✨

---

*Shared libraries implementation completed on: $(Get-Date)*
*Status: ✅ SUCCESS - All shared utilities and libraries implemented and ready for use*
