# Docker Deployment Guide

## Overview

This guide covers deploying the Cosmic Council Framework using Docker and Docker Compose. Docker provides a containerized deployment solution that's easy to set up and manage.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM
- At least 10GB disk space

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/cosmic-council.git
cd cosmic-council
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Database Configuration
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=cosmic_council
POSTGRES_USER=cosmic_council

# Application Configuration
SECRET_KEY=your_secret_key_here
API_KEY=your_api_key_here
ENVIRONMENT=production
LOG_LEVEL=INFO

# AI/LLM Configuration
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Monitoring Configuration
GRAFANA_PASSWORD=your_grafana_password

# Security Configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_email_password
SMTP_TLS=true

# File Upload Configuration
MAX_FILE_SIZE=10MB
ALLOWED_FILE_TYPES=pdf,doc,docx,txt,jpg,jpeg,png,gif
UPLOAD_PATH=/app/uploads

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION=30
BACKUP_PATH=/app/backups
```

### 3. Deploy with Docker Compose

#### Production Deployment

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Development Deployment

```bash
# Start development services
docker-compose -f docker-compose.dev.yml up -d

# Check service status
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

## Service Architecture

### Core Services

- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **API**: Cosmic Council REST API
- **Web**: Web interface
- **Nginx**: Reverse proxy and load balancer

### Monitoring Services

- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization
- **Elasticsearch**: Log storage
- **Kibana**: Log visualization
- **Logstash**: Log processing

## Service Configuration

### PostgreSQL Configuration

```yaml
postgres:
  image: postgres:13
  environment:
    POSTGRES_DB: cosmic_council
    POSTGRES_USER: cosmic_council
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"
```

### Redis Configuration

```yaml
redis:
  image: redis:6-alpine
  command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
  volumes:
    - redis_data:/data
  ports:
    - "6379:6379"
```

### API Service Configuration

```yaml
api:
  build:
    context: .
    dockerfile: Dockerfile
    target: api
  environment:
    - DATABASE_URL=postgresql://cosmic_council:${POSTGRES_PASSWORD}@postgres:5432/cosmic_council
    - REDIS_URL=redis://redis:6379/0
  ports:
    - "8000:8000"
  depends_on:
    - postgres
    - redis
```

### Web Service Configuration

```yaml
web:
  build:
    context: .
    dockerfile: Dockerfile
    target: web
  environment:
    - API_URL=http://api:8000
  ports:
    - "8001:8001"
  depends_on:
    - api
```

## Health Checks

### Service Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check Web interface health
curl http://localhost:8001/health

# Check database connection
docker-compose exec postgres pg_isready -U cosmic_council

# Check Redis connection
docker-compose exec redis redis-cli ping
```

### Comprehensive Health Check

```bash
# Run health check script
./scripts/health-check.sh

# Or use Docker Compose
docker-compose exec api python -m pytest tests/health/ -v
```

## Monitoring and Logging

### Accessing Monitoring Services

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200

### Viewing Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
docker-compose logs -f web
docker-compose logs -f postgres
docker-compose logs -f redis

# View logs with timestamps
docker-compose logs -f -t

# View last 100 lines
docker-compose logs --tail=100 -f
```

### Metrics Collection

The system automatically collects metrics for:
- Request rates and response times
- Error rates and status codes
- Database connection pool status
- Redis cache hit/miss rates
- System resource usage

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U cosmic_council cosmic_council > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec -T postgres psql -U cosmic_council cosmic_council < backup_20231201_120000.sql
```

### Automated Backups

```bash
# Set up cron job for daily backups
echo "0 2 * * * cd /path/to/cosmic-council && docker-compose exec postgres pg_dump -U cosmic_council cosmic_council > backups/backup_\$(date +\%Y\%m\%d_\%H\%M\%S).sql" | crontab -
```

### Volume Backups

```bash
# Backup volumes
docker run --rm -v cosmic-council_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
docker run --rm -v cosmic-council_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz -C /data .
```

## Scaling

### Horizontal Scaling

```bash
# Scale API service
docker-compose up -d --scale api=3

# Scale Web service
docker-compose up -d --scale web=2
```

### Load Balancing

The Nginx service automatically load balances between multiple instances:

```yaml
nginx:
  depends_on:
    - api
    - web
  # Nginx configuration handles load balancing
```

## Security

### SSL/TLS Configuration

1. Obtain SSL certificates
2. Place certificates in `docker/ssl/` directory
3. Update Nginx configuration
4. Restart services

```bash
# Generate self-signed certificate for testing
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/ssl/key.pem \
  -out docker/ssl/cert.pem
```

### Network Security

```bash
# Create custom network
docker network create cosmic-council-network

# Update docker-compose.yml to use custom network
networks:
  cosmic-council-network:
    external: true
```

### Container Security

- Run containers as non-root users
- Use read-only root filesystems
- Drop unnecessary capabilities
- Use security scanning tools

## Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs service_name

# Check resource usage
docker stats
```

#### Database Connection Issues

```bash
# Check database status
docker-compose exec postgres pg_isready -U cosmic_council

# Check database logs
docker-compose logs postgres

# Test connection
docker-compose exec api python -c "import psycopg2; print('Connected')"
```

#### Memory Issues

```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 2G
```

#### Port Conflicts

```bash
# Check port usage
netstat -tulpn | grep :8000

# Change ports in docker-compose.yml
services:
  api:
    ports:
      - "8001:8000"  # Change external port
```

### Performance Optimization

#### Database Optimization

```bash
# Tune PostgreSQL settings
docker-compose exec postgres psql -U cosmic_council -c "
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();
"
```

#### Redis Optimization

```bash
# Tune Redis settings
docker-compose exec redis redis-cli CONFIG SET maxmemory 2gb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## Maintenance

### Updates

```bash
# Pull latest images
docker-compose pull

# Rebuild and restart services
docker-compose up -d --build

# Clean up old images
docker image prune -f
```

### Log Rotation

```bash
# Configure log rotation
docker-compose exec api logrotate -f /etc/logrotate.conf
```

### Health Monitoring

```bash
# Set up monitoring alerts
curl -X POST http://localhost:9090/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{"alerts": [{"labels": {"alertname": "HighErrorRate"}}]}'
```

## Production Considerations

### Resource Requirements

- **Minimum**: 4GB RAM, 2 CPU cores, 20GB disk
- **Recommended**: 8GB RAM, 4 CPU cores, 50GB disk
- **High Load**: 16GB RAM, 8 CPU cores, 100GB disk

### High Availability

- Use external database (AWS RDS, Google Cloud SQL)
- Use managed Redis (AWS ElastiCache, Google Cloud Memorystore)
- Set up load balancer with multiple instances
- Implement health checks and auto-recovery

### Disaster Recovery

- Regular database backups
- Volume snapshots
- Configuration backups
- Documentation of recovery procedures

## Support

For deployment support:
- **Documentation**: https://docs.cosmic-council.org
- **GitHub Issues**: https://github.com/your-org/cosmic-council/issues
- **Discord**: https://discord.gg/cosmic-council
- **Email**: support@cosmic-council.org
