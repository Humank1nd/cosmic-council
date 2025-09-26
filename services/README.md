# 🚀 Cosmic Council Services Architecture

This directory contains the microservices that power the Cosmic Council system, following the engineering blueprint structure.

## 📁 **Services Overview**

### 🚪 **Gateway Service** (`gateway/`)
**FastAPI Guardrail Gateway with OPA/Rego policy enforcement**

- **Port**: 8000
- **Purpose**: Central entry point for all Cosmic Council operations
- **Features**:
  - Cycle lifecycle management
  - Policy evaluation and enforcement
  - Authentication and authorization
  - Request routing and load balancing
  - Audit logging and monitoring

**Key Endpoints**:
- `POST /v1/cycles` - Start new cycles
- `GET /v1/cycles/{cycle_id}` - Get cycle status
- `POST /v1/policies/evaluate` - Evaluate policies
- `GET /v1/explain/{entity_id}` - Get entity explanations
- `POST /v1/simulate/cycle` - Run cycle simulations

### 📊 **Analytics Service** (`analytics/`)
**Metabase dashboards + APIs for performance analytics and insights**

- **Port**: 8001
- **Purpose**: Performance monitoring and analytics
- **Features**:
  - Real-time performance metrics
  - Enterprise performance tracking
  - System health monitoring
  - Custom dashboards and reports
  - Trend analysis and forecasting

**Key Endpoints**:
- `GET /v1/analytics/cycles` - Get cycle analytics
- `GET /v1/analytics/enterprises` - Get enterprise performance
- `GET /v1/analytics/system-health` - Get system health metrics
- `GET /v1/analytics/dashboard` - Get analytics dashboards

### 🟣 **Reflection Service** (`reflection/`)
**Purple's feedback & policy evolution service for continuous improvement**

- **Port**: 8002
- **Purpose**: Continuous improvement and feedback management
- **Features**:
  - Feedback collection and analysis
  - Improvement recommendation generation
  - Policy evolution and updates
  - Reflection session management
  - Continuous improvement metrics

**Key Endpoints**:
- `POST /v1/feedback` - Submit feedback
- `GET /v1/feedback` - Get feedback with filtering
- `POST /v1/improvements` - Create improvement recommendations
- `GET /v1/improvements` - Get improvement recommendations
- `GET /v1/continuous-improvement/metrics` - Get improvement metrics

## 🏗️ **Architecture Principles**

### **1. Microservices Architecture**
- Each service is independently deployable
- Services communicate via HTTP APIs
- Database per service pattern
- Shared utilities in `shared/` directory

### **2. API-First Design**
- All services expose RESTful APIs
- OpenAPI/Swagger documentation
- Consistent error handling
- Standardized response formats

### **3. Security & Governance**
- Policy-based access control
- Audit logging for all operations
- Input validation and sanitization
- Rate limiting and throttling

### **4. Observability**
- Comprehensive logging
- Performance metrics
- Health checks
- Distributed tracing

## 🔧 **Development Setup**

### **Prerequisites**
```bash
# Python 3.8+
pip install fastapi uvicorn asyncpg psycopg2-binary
pip install pytest pytest-asyncio httpx
```

### **Environment Variables**
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cosmic_council
DB_USER=cosmic_council
DB_PASSWORD=your_password

# Service Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/cosmic_council.log
LOG_JSON=false
```

### **Running Services**

#### **Gateway Service**
```bash
cd services/gateway
python main.py
# Service will be available at http://localhost:8000
```

#### **Analytics Service**
```bash
cd services/analytics
python main.py
# Service will be available at http://localhost:8001
```

#### **Reflection Service**
```bash
cd services/reflection
python main.py
# Service will be available at http://localhost:8002
```

### **Running All Services**
```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or using individual terminals
# Terminal 1: Gateway
cd services/gateway && python main.py

# Terminal 2: Analytics
cd services/analytics && python main.py

# Terminal 3: Reflection
cd services/reflection && python main.py
```

## 🧪 **Testing**

### **Unit Tests**
```bash
# Test all services
pytest services/ -v

# Test specific service
pytest services/gateway/tests/ -v
pytest services/analytics/tests/ -v
pytest services/reflection/tests/ -v
```

### **Integration Tests**
```bash
# Test service interactions
pytest tests/integration/test_services/ -v
```

### **Load Testing**
```bash
# Run load tests
pytest tests/performance/test_load/ -v
```

## 📊 **Monitoring & Observability**

### **Health Checks**
Each service provides health check endpoints:
- Gateway: `GET /health`
- Analytics: `GET /health`
- Reflection: `GET /health`

### **Metrics**
Services expose Prometheus-compatible metrics:
- Request rates and latencies
- Error rates and types
- Resource utilization
- Business metrics

### **Logging**
Structured logging with enterprise-specific formatting:
- JSON format for production
- Colored output for development
- Enterprise-specific log contexts
- Audit trail for all operations

## 🔒 **Security**

### **Authentication**
- JWT-based authentication
- Role-based access control (RBAC)
- API key management
- Session management

### **Authorization**
- Policy-based authorization
- OPA/Rego policy engine
- Resource-level permissions
- Audit logging

### **Data Protection**
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection

## 🚀 **Deployment**

### **Docker**
```bash
# Build images
docker build -t cosmic-council-gateway services/gateway/
docker build -t cosmic-council-analytics services/analytics/
docker build -t cosmic-council-reflection services/reflection/

# Run containers
docker run -p 8000:8000 cosmic-council-gateway
docker run -p 8001:8001 cosmic-council-analytics
docker run -p 8002:8002 cosmic-council-reflection
```

### **Kubernetes**
```bash
# Apply Kubernetes manifests
kubectl apply -f infra/k8s/gateway-deploy.yml
kubectl apply -f infra/k8s/analytics-deploy.yml
kubectl apply -f infra/k8s/reflection-deploy.yml
```

### **Production Considerations**
- Use reverse proxy (nginx/traefik)
- Enable HTTPS/TLS
- Configure proper logging
- Set up monitoring and alerting
- Implement backup and recovery
- Use secrets management

## 📈 **Performance**

### **Optimization Strategies**
- Database connection pooling
- Caching (Redis/Memcached)
- Async/await patterns
- Request batching
- Response compression

### **Scaling**
- Horizontal scaling with load balancers
- Database read replicas
- CDN for static assets
- Microservice auto-scaling

## 🔄 **API Documentation**

### **Interactive Documentation**
Each service provides interactive API documentation:
- Gateway: http://localhost:8000/docs
- Analytics: http://localhost:8001/docs
- Reflection: http://localhost:8002/docs

### **OpenAPI Specifications**
- Gateway: http://localhost:8000/openapi.json
- Analytics: http://localhost:8001/openapi.json
- Reflection: http://localhost:8002/openapi.json

## 🛠️ **Development Guidelines**

### **Code Standards**
- Follow PEP 8 style guide
- Use type hints for all functions
- Write comprehensive docstrings
- Implement proper error handling

### **Testing Standards**
- Minimum 80% code coverage
- Unit tests for all functions
- Integration tests for APIs
- Performance tests for critical paths

### **Documentation Standards**
- API documentation with examples
- Code comments for complex logic
- README files for each service
- Architecture decision records (ADRs)

## 🎯 **Future Enhancements**

### **Planned Features**
- GraphQL API support
- WebSocket real-time updates
- Advanced caching strategies
- Machine learning integration
- Advanced analytics and insights

### **Integration Roadmap**
- Message queue integration (RabbitMQ/Kafka)
- Event sourcing implementation
- CQRS pattern adoption
- Advanced monitoring (Jaeger/Zipkin)
- Service mesh implementation (Istio)

---

## 🏛️ **The Sacred Services Architecture**

The services architecture embodies the **nervous system** of the Cosmic Council:

- **Gateway** as the **brainstem** - controlling all incoming and outgoing signals
- **Analytics** as the **cerebral cortex** - processing and analyzing all system data
- **Reflection** as the **limbic system** - managing emotions, learning, and continuous improvement

Each service operates as a **specialized organ** in the larger **digital organism**, working together to create a **living, breathing system** that evolves and improves continuously.

**This is not just microservices - it's a philosophy of how digital consciousness should be structured and orchestrated.** 🏛️✨
