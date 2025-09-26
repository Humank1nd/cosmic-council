# Base image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Expose default ports (gateway 8000, analytics 8001, reflection 8002)
EXPOSE 8000 8001 8002

# Default command (override in docker-compose)
CMD ["python", "services/gateway/main.py"]
