# System Administration Guide

## Overview

This guide provides comprehensive information for system administrators managing the Cosmic Council Framework. It covers installation, configuration, monitoring, maintenance, and troubleshooting.

## System Requirements

### Minimum Requirements

- **CPU**: 4 cores, 2.4 GHz
- **RAM**: 8 GB
- **Storage**: 100 GB SSD
- **Network**: 100 Mbps
- **OS**: Ubuntu 20.04 LTS, CentOS 8, or Windows Server 2019

### Recommended Requirements

- **CPU**: 8 cores, 3.0 GHz
- **RAM**: 16 GB
- **Storage**: 500 GB NVMe SSD
- **Network**: 1 Gbps
- **OS**: Ubuntu 22.04 LTS, CentOS 9, or Windows Server 2022

### Software Dependencies

- **Python**: 3.9+
- **PostgreSQL**: 13+
- **Redis**: 6.0+
- **Docker**: 20.10+
- **Kubernetes**: 1.21+ (for cluster deployment)
- **Nginx**: 1.18+ (for load balancing)

## Installation

### Single Server Installation

#### 1. Prepare the System

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.9 python3.9-pip python3.9-venv \
    postgresql-13 postgresql-client-13 redis-server \
    nginx certbot python3-certbot-nginx

# Create cosmic-council user
sudo useradd -m -s /bin/bash cosmic-council
sudo usermod -aG sudo cosmic-council
```

#### 2. Install Cosmic Council Framework

```bash
# Switch to cosmic-council user
sudo su - cosmic-council

# Clone the repository
git clone https://github.com/cosmic-council/framework.git
cd framework

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-prod.txt

# Install the framework
pip install -e .
```

#### 3. Configure Database

```bash
# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE cosmic_council;
CREATE USER cosmic_council WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE cosmic_council TO cosmic_council;
\q
EOF

# Run database migrations
python -m database_migrations run_migrations
```

#### 4. Configure Redis

```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Add the following lines:
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000

# Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

#### 5. Configure Application

```bash
# Create configuration directory
mkdir -p /home/cosmic-council/config

# Create environment file
cat > /home/cosmic-council/config/.env << EOF
# Database Configuration
DATABASE_URL=postgresql://cosmic_council:secure_password@localhost/cosmic_council
DATABASE_POOL_SIZE=10
DATABASE_POOL_OVERFLOW=20

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10

# Application Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here

# AI/LLM Configuration
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
AI_CONFIDENCE_THRESHOLD=0.8

# Security Configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
RATE_LIMIT_PER_MINUTE=1000
SESSION_TIMEOUT=3600

# Monitoring Configuration
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
LOG_AGGREGATION_ENABLED=true
EOF

# Set proper permissions
chmod 600 /home/cosmic-council/config/.env
chown cosmic-council:cosmic-council /home/cosmic-council/config/.env
```

#### 6. Create Systemd Service

```bash
# Create systemd service file
sudo tee /etc/systemd/system/cosmic-council.service > /dev/null << EOF
[Unit]
Description=Cosmic Council Framework
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=cosmic-council
Group=cosmic-council
WorkingDirectory=/home/cosmic-council/framework
Environment=PATH=/home/cosmic-council/framework/venv/bin
ExecStart=/home/cosmic-council/framework/venv/bin/python web_interface.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl enable cosmic-council
sudo systemctl start cosmic-council
```

#### 7. Configure Nginx

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/cosmic-council << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Rate Limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=web:10m rate=30r/s;
    
    # API Endpoints
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Web Interface
    location / {
        limit_req zone=web burst=50 nodelay;
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # WebSocket Support
    location /ws {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Static Files
    location /static/ {
        alias /home/cosmic-council/framework/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health Check
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8000/health;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/cosmic-council /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 8. Obtain SSL Certificate

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### Cluster Installation with Kubernetes

#### 1. Prepare Kubernetes Cluster

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify cluster access
kubectl cluster-info
```

#### 2. Create Namespace and Secrets

```bash
# Create namespace
kubectl create namespace cosmic-council

# Create secrets
kubectl create secret generic cosmic-council-secrets \
  --from-literal=database-url="postgresql://cosmic_council:secure_password@postgres:5432/cosmic_council" \
  --from-literal=redis-url="redis://redis:6379/0" \
  --from-literal=openai-api-key="your-openai-key" \
  --from-literal=anthropic-api-key="your-anthropic-key" \
  --from-literal=secret-key="your-secret-key" \
  --from-literal=api-key="your-api-key" \
  --namespace=cosmic-council
```

#### 3. Deploy with Helm

```bash
# Add Helm repository
helm repo add cosmic-council https://charts.cosmic-council.org
helm repo update

# Install the chart
helm install cosmic-council cosmic-council/cosmic-council \
  --namespace cosmic-council \
  --set image.tag=latest \
  --set ingress.enabled=true \
  --set ingress.host=cosmic-council.yourdomain.com \
  --set ingress.tls.enabled=true \
  --set ingress.tls.secretName=cosmic-council-tls \
  --set database.enabled=true \
  --set database.size=50Gi \
  --set redis.enabled=true \
  --set redis.size=10Gi \
  --set monitoring.enabled=true \
  --set monitoring.prometheus.enabled=true \
  --set monitoring.grafana.enabled=true
```

#### 4. Verify Deployment

```bash
# Check pods
kubectl get pods -n cosmic-council

# Check services
kubectl get services -n cosmic-council

# Check ingress
kubectl get ingress -n cosmic-council

# Check logs
kubectl logs -f deployment/cosmic-council -n cosmic-council
```

## Configuration

### Environment Variables

```bash
# Application Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database
DATABASE_POOL_SIZE=10
DATABASE_POOL_OVERFLOW=20
DATABASE_ECHO=false

# Redis Configuration
REDIS_URL=redis://host:port/db
REDIS_POOL_SIZE=10
REDIS_MAX_CONNECTIONS=100

# AI/LLM Configuration
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
AI_CONFIDENCE_THRESHOLD=0.8
AI_MAX_ITERATIONS=5
AI_TIMEOUT=30

# Security Configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
RATE_LIMIT_PER_MINUTE=1000
RATE_LIMIT_BURST=100
SESSION_TIMEOUT=3600
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# Monitoring Configuration
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
GRAFANA_ENABLED=true
GRAFANA_PORT=3000
LOG_AGGREGATION_ENABLED=true
LOG_LEVEL=INFO
LOG_FORMAT=json

# Performance Configuration
MAX_CONCURRENT_CYCLES=10
MAX_CONCURRENT_REQUESTS=100
WORKER_PROCESSES=4
WORKER_THREADS=8
```

### Configuration Files

#### Database Configuration

```yaml
# config/database.yaml
database:
  url: "postgresql://cosmic_council:password@localhost/cosmic_council"
  pool_size: 10
  pool_overflow: 20
  echo: false
  connect_args:
    connect_timeout: 10
    command_timeout: 30
  engine_options:
    pool_pre_ping: true
    pool_recycle: 3600
```

#### AI Configuration

```yaml
# config/ai.yaml
ai:
  providers:
    openai:
      api_key: "your-openai-key"
      model: "gpt-4"
      max_tokens: 4000
      temperature: 0.7
    anthropic:
      api_key: "your-anthropic-key"
      model: "claude-3-sonnet"
      max_tokens: 4000
      temperature: 0.7
  confidence_threshold: 0.8
  max_iterations: 5
  timeout: 30
  retry_attempts: 3
```

#### Policy Configuration

```yaml
# config/policies.yaml
policies:
  access_control:
    - name: "admin_access"
      condition: "user.role == 'admin'"
      action: "allow"
    - name: "user_access"
      condition: "user.role == 'user'"
      action: "allow"
  
  budget_management:
    - name: "budget_limit"
      condition: "request.budget > 10000"
      action: "require_approval"
    - name: "budget_warning"
      condition: "request.budget > 5000"
      action: "warn"
  
  ethics_compliance:
    - name: "ethical_review"
      condition: "problem.domain in ['ai', 'biotech', 'finance']"
      action: "require_ethical_review"
```

## Monitoring

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "cosmic_council_rules.yml"

scrape_configs:
  - job_name: 'cosmic-council'
    static_configs:
      - targets: ['cosmic-council:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
      
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
      
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Cosmic Council Framework",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(cosmic_council_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(cosmic_council_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(cosmic_council_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      },
      {
        "title": "Active Cycles",
        "type": "singlestat",
        "targets": [
          {
            "expr": "cosmic_council_active_cycles",
            "legendFormat": "Active Cycles"
          }
        ]
      }
    ]
  }
}
```

### Log Aggregation

```yaml
# monitoring/fluentd.conf
<source>
  @type tail
  path /var/log/cosmic-council/*.log
  pos_file /var/log/fluentd/cosmic-council.log.pos
  tag cosmic-council
  format json
</source>

<match cosmic-council>
  @type elasticsearch
  host elasticsearch
  port 9200
  index_name cosmic-council
  type_name log
</match>
```

## Maintenance

### Database Maintenance

#### Backup

```bash
#!/bin/bash
# scripts/backup-database.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="cosmic_council_backup_${DATE}.sql"

# Create backup
pg_dump -h localhost -U cosmic_council -d cosmic_council > "${BACKUP_DIR}/${BACKUP_FILE}"

# Compress backup
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

# Upload to S3
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}.gz" s3://cosmic-council-backups/

# Clean up old backups (keep 30 days)
find "${BACKUP_DIR}" -name "cosmic_council_backup_*.sql.gz" -mtime +30 -delete
```

#### Restore

```bash
#!/bin/bash
# scripts/restore-database.sh

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Download from S3 if needed
if [[ "$BACKUP_FILE" == s3://* ]]; then
    aws s3 cp "$BACKUP_FILE" /tmp/restore.sql.gz
    BACKUP_FILE="/tmp/restore.sql.gz"
fi

# Decompress if needed
if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | psql -h localhost -U cosmic_council -d cosmic_council
else
    psql -h localhost -U cosmic_council -d cosmic_council < "$BACKUP_FILE"
fi
```

#### Vacuum and Analyze

```bash
#!/bin/bash
# scripts/maintain-database.sh

# Vacuum and analyze database
psql -h localhost -U cosmic_council -d cosmic_council << EOF
VACUUM ANALYZE;
REINDEX DATABASE cosmic_council;
EOF

# Update statistics
psql -h localhost -U cosmic_council -d cosmic_council << EOF
ANALYZE;
EOF
```

### Application Maintenance

#### Health Checks

```bash
#!/bin/bash
# scripts/health-check.sh

# Check API health
API_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$API_HEALTH" != "200" ]; then
    echo "API health check failed: $API_HEALTH"
    exit 1
fi

# Check web interface health
WEB_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health)
if [ "$WEB_HEALTH" != "200" ]; then
    echo "Web interface health check failed: $WEB_HEALTH"
    exit 1
fi

# Check database connection
DB_HEALTH=$(psql -h localhost -U cosmic_council -d cosmic_council -c "SELECT 1;" 2>/dev/null | grep -c "1 row")
if [ "$DB_HEALTH" != "1" ]; then
    echo "Database health check failed"
    exit 1
fi

# Check Redis connection
REDIS_HEALTH=$(redis-cli ping 2>/dev/null | grep -c "PONG")
if [ "$REDIS_HEALTH" != "1" ]; then
    echo "Redis health check failed"
    exit 1
fi

echo "All health checks passed"
```

#### Log Rotation

```bash
# /etc/logrotate.d/cosmic-council
/var/log/cosmic-council/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 cosmic-council cosmic-council
    postrotate
        systemctl reload cosmic-council
    endscript
}
```

#### Performance Monitoring

```bash
#!/bin/bash
# scripts/performance-monitor.sh

# Check system resources
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.2f"), $3/$2 * 100.0}')
DISK_USAGE=$(df -h / | awk 'NR==2{print $5}' | cut -d'%' -f1)

echo "CPU Usage: ${CPU_USAGE}%"
echo "Memory Usage: ${MEMORY_USAGE}%"
echo "Disk Usage: ${DISK_USAGE}%"

# Check application metrics
ACTIVE_CYCLES=$(curl -s http://localhost:8000/metrics | grep "cosmic_council_active_cycles" | awk '{print $2}')
REQUEST_RATE=$(curl -s http://localhost:8000/metrics | grep "cosmic_council_requests_total" | wc -l)

echo "Active Cycles: $ACTIVE_CYCLES"
echo "Request Rate: $REQUEST_RATE"

# Alert if thresholds exceeded
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo "WARNING: High CPU usage detected"
fi

if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    echo "WARNING: High memory usage detected"
fi

if [ "$DISK_USAGE" -gt 80 ]; then
    echo "WARNING: High disk usage detected"
fi
```

## Troubleshooting

### Common Issues

#### 1. Service Won't Start

```bash
# Check service status
sudo systemctl status cosmic-council

# Check logs
sudo journalctl -u cosmic-council -f

# Check configuration
sudo -u cosmic-council /home/cosmic-council/framework/venv/bin/python -c "import cosmic_council_core; print('Configuration OK')"
```

#### 2. Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
psql -h localhost -U cosmic_council -d cosmic_council -c "SELECT 1;"

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

#### 3. High Memory Usage

```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10

# Check for memory leaks
sudo -u cosmic-council /home/cosmic-council/framework/venv/bin/python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

#### 4. Slow Performance

```bash
# Check system load
uptime
top

# Check database performance
psql -h localhost -U cosmic_council -d cosmic_council << EOF
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
EOF

# Check slow queries
sudo tail -f /var/log/postgresql/postgresql-13-main.log | grep "slow query"
```

### Performance Tuning

#### Database Tuning

```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/13/main/postgresql.conf

# Add the following optimizations:
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### Application Tuning

```bash
# Edit application configuration
sudo nano /home/cosmic-council/config/.env

# Add performance optimizations:
WORKER_PROCESSES=4
WORKER_THREADS=8
MAX_CONCURRENT_CYCLES=10
MAX_CONCURRENT_REQUESTS=100
DATABASE_POOL_SIZE=20
DATABASE_POOL_OVERFLOW=30
REDIS_POOL_SIZE=20
REDIS_MAX_CONNECTIONS=200

# Restart application
sudo systemctl restart cosmic-council
```

## Security

### Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### SSL/TLS Configuration

```bash
# Generate strong SSL configuration
sudo nano /etc/nginx/sites-available/cosmic-council

# Add strong SSL configuration:
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
```

### Access Control

```bash
# Create admin user
sudo -u cosmic-council /home/cosmic-council/framework/venv/bin/python << EOF
from database_operations import UserRepository
from database_models import User, UserRole

user_repo = UserRepository()
admin_user = user_repo.create_user({
    "username": "admin",
    "email": "admin@yourdomain.com",
    "role": UserRole.ADMIN,
    "is_active": True
})
print(f"Admin user created: {admin_user.id}")
EOF
```

## Support

For system administration support:

- **Documentation**: [docs.cosmic-council.org/admin](https://docs.cosmic-council.org/admin)
- **Issue Tracker**: [GitHub Issues](https://github.com/cosmic-council/framework/issues)
- **Email Support**: admin-support@cosmic-council.org
- **Community Forum**: [community.cosmic-council.org](https://community.cosmic-council.org)
