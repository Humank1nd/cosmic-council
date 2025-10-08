# Cosmic Council Refinement Engine - Production Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies with security updates
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    wget \
    ca-certificates \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with security
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

# Copy application code
COPY . .

# Create non-root user with specific UID/GID for security
RUN groupadd -r app && useradd -r -g app -d /app -s /bin/bash app && \
    chown -R app:app /app && \
    chmod -R 755 /app

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/data /app/temp && \
    chown -R app:app /app/logs /app/data /app/temp && \
    chmod -R 755 /app/logs /app/data /app/temp

# Switch to non-root user
USER app

# Expose ports
EXPOSE 8000 8001 9090

# Health check with security considerations
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command with security flags
CMD ["python", "-m", "uvicorn", "refinement_engine.secure_api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
