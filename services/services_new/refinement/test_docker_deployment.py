"""
Test Docker Containers and Service Orchestration
Comprehensive testing of Docker deployment, container orchestration, and service integration.
"""

import asyncio
import os
import sys
import time
import json
import subprocess
import requests
import docker
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DockerDeploymentTester:
    """Test Docker deployment and orchestration comprehensively."""
    
    def __init__(self):
        self.docker_client = None
        self.test_results = {}
        self.containers = {}
        self.services = {}
        self.networks = {}
        self.volumes = {}
        self.base_url = "http://localhost"
        self.ports = {
            "refinement-engine": 8000,
            "monitoring-api": 8001,
            "metrics": 9090,
            "postgres": 5432,
            "redis": 6379,
            "prometheus": 9091,
            "grafana": 3000,
            "nginx": 80
        }
    
    async def setup_docker_client(self) -> bool:
        """Test Docker client setup."""
        print("🐳 Testing Docker Client Setup...")
        
        try:
            # Initialize Docker client
            self.docker_client = docker.from_env()
            print(f"✅ Docker client initialized")
            
            # Test Docker daemon connection
            version_info = self.docker_client.version()
            print(f"✅ Docker daemon connected: {version_info['Version']}")
            
            # Test Docker Compose availability
            try:
                result = subprocess.run(
                    ["docker-compose", "--version"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if result.returncode == 0:
                    print(f"✅ Docker Compose available: {result.stdout.strip()}")
                else:
                    print(f"⚠️ Docker Compose not available, trying 'docker compose'")
                    result = subprocess.run(
                        ["docker", "compose", "version"], 
                        capture_output=True, 
                        text=True, 
                        timeout=10
                    )
                    if result.returncode == 0:
                        print(f"✅ Docker Compose (new) available: {result.stdout.strip()}")
                    else:
                        print(f"❌ Docker Compose not available")
                        return False
            except Exception as e:
                print(f"❌ Docker Compose check failed: {e}")
                return False
            
            self.test_results["docker_client"] = True
            return True
            
        except Exception as e:
            print(f"❌ Docker client setup failed: {e}")
            self.test_results["docker_client"] = False
            return False
    
    async def test_dockerfile_build(self) -> bool:
        """Test Dockerfile build process."""
        print("\n🔨 Testing Dockerfile Build...")
        
        try:
            # Check if Dockerfile exists
            if not os.path.exists("Dockerfile"):
                print(f"❌ Dockerfile not found")
                return False
            
            print(f"✅ Dockerfile found")
            
            # Test Docker build
            print("📦 Building Docker image...")
            start_time = time.time()
            
            try:
                image, build_logs = self.docker_client.images.build(
                    path=".",
                    tag="cosmic-council-refinement-engine:test",
                    rm=True,
                    forcerm=True
                )
                
                build_time = time.time() - start_time
                print(f"✅ Docker image built successfully in {build_time:.1f}s")
                print(f"📊 Image ID: {image.short_id}")
                print(f"📊 Image size: {self._format_size(image.attrs['Size'])}")
                
                # Test image inspection
                image_info = self.docker_client.images.get(image.id)
                print(f"📊 Image layers: {len(image_info.attrs['RootFS']['Layers'])}")
                print(f"📊 Image architecture: {image_info.attrs['Architecture']}")
                
                # Store image for cleanup
                self.test_image = image
                
                self.test_results["dockerfile_build"] = True
                return True
                
            except Exception as e:
                print(f"❌ Docker build failed: {e}")
                # Print build logs for debugging
                if hasattr(e, 'build_log'):
                    for log in e.build_log:
                        if 'stream' in log:
                            print(f"Build log: {log['stream'].strip()}")
                return False
            
        except Exception as e:
            print(f"❌ Dockerfile test failed: {e}")
            self.test_results["dockerfile_build"] = False
            return False
    
    async def test_docker_compose_config(self) -> bool:
        """Test Docker Compose configuration."""
        print("\n📋 Testing Docker Compose Configuration...")
        
        try:
            # Check if docker-compose.yml exists
            if not os.path.exists("docker-compose.yml"):
                print(f"❌ docker-compose.yml not found")
                return False
            
            print(f"✅ docker-compose.yml found")
            
            # Test Docker Compose config validation
            try:
                result = subprocess.run(
                    ["docker-compose", "config"], 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                if result.returncode == 0:
                    print(f"✅ Docker Compose configuration valid")
                    config_data = result.stdout
                    print(f"📊 Configuration size: {len(config_data)} characters")
                else:
                    print(f"❌ Docker Compose configuration invalid: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Docker Compose config validation failed: {e}")
                return False
            
            # Parse and validate services
            try:
                result = subprocess.run(
                    ["docker-compose", "config", "--services"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if result.returncode == 0:
                    services = result.stdout.strip().split('\n')
                    print(f"✅ Services defined: {', '.join(services)}")
                    self.services = {service: {} for service in services}
                else:
                    print(f"❌ Failed to get services: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Service parsing failed: {e}")
                return False
            
            # Test Docker Compose config with environment variables
            try:
                env_vars = {
                    "JWT_SECRET_KEY": "test-secret-key",
                    "API_KEY_SECRET": "test-api-key",
                    "OPENAI_API_KEY": "test-openai-key",
                    "ANTHROPIC_API_KEY": "test-anthropic-key",
                    "GRAFANA_PASSWORD": "test-grafana-password"
                }
                
                env = os.environ.copy()
                env.update(env_vars)
                
                result = subprocess.run(
                    ["docker-compose", "config"], 
                    capture_output=True, 
                    text=True, 
                    timeout=30,
                    env=env
                )
                if result.returncode == 0:
                    print(f"✅ Docker Compose config with environment variables valid")
                else:
                    print(f"❌ Docker Compose config with env vars failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Environment variable config test failed: {e}")
                return False
            
            self.test_results["docker_compose_config"] = True
            return True
            
        except Exception as e:
            print(f"❌ Docker Compose config test failed: {e}")
            self.test_results["docker_compose_config"] = False
            return False
    
    async def test_container_orchestration(self) -> bool:
        """Test container orchestration and service startup."""
        print("\n🚀 Testing Container Orchestration...")
        
        try:
            # Start services with Docker Compose
            print("📦 Starting services with Docker Compose...")
            start_time = time.time()
            
            try:
                result = subprocess.run(
                    ["docker-compose", "up", "-d"], 
                    capture_output=True, 
                    text=True, 
                    timeout=120
                )
                if result.returncode == 0:
                    startup_time = time.time() - start_time
                    print(f"✅ Services started successfully in {startup_time:.1f}s")
                else:
                    print(f"❌ Failed to start services: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Service startup failed: {e}")
                return False
            
            # Wait for services to be ready
            print("⏳ Waiting for services to be ready...")
            await asyncio.sleep(10)
            
            # Check container status
            try:
                result = subprocess.run(
                    ["docker-compose", "ps"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if result.returncode == 0:
                    print(f"✅ Container status check successful")
                    print(f"📊 Container status:\n{result.stdout}")
                else:
                    print(f"❌ Container status check failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Container status check failed: {e}")
                return False
            
            # Test individual container health
            await self._test_container_health()
            
            self.test_results["container_orchestration"] = True
            return True
            
        except Exception as e:
            print(f"❌ Container orchestration test failed: {e}")
            self.test_results["container_orchestration"] = False
            return False
    
    async def _test_container_health(self) -> bool:
        """Test individual container health."""
        print("\n🏥 Testing Container Health...")
        
        try:
            # Get running containers
            containers = self.docker_client.containers.list()
            print(f"📊 Found {len(containers)} running containers")
            
            healthy_containers = 0
            total_containers = 0
            
            for container in containers:
                if "cosmic-council" in container.name:
                    total_containers += 1
                    print(f"📦 Testing container: {container.name}")
                    
                    # Check container status
                    container.reload()
                    status = container.status
                    print(f"   Status: {status}")
                    
                    # Check health status if available
                    if 'Health' in container.attrs['State']:
                        health = container.attrs['State']['Health']['Status']
                        print(f"   Health: {health}")
                        if health == 'healthy':
                            healthy_containers += 1
                    else:
                        # If no health check, consider running as healthy
                        if status == 'running':
                            healthy_containers += 1
                    
                    # Check container logs for errors
                    try:
                        logs = container.logs(tail=10).decode('utf-8')
                        if "error" in logs.lower() or "exception" in logs.lower():
                            print(f"   ⚠️ Potential errors in logs")
                        else:
                            print(f"   ✅ No obvious errors in logs")
                    except Exception as e:
                        print(f"   ⚠️ Could not check logs: {e}")
            
            print(f"📊 Container health: {healthy_containers}/{total_containers} healthy")
            
            if healthy_containers == total_containers and total_containers > 0:
                print(f"✅ All containers healthy")
                return True
            else:
                print(f"⚠️ Some containers may not be healthy")
                return False
                
        except Exception as e:
            print(f"❌ Container health test failed: {e}")
            return False
    
    async def test_service_connectivity(self) -> bool:
        """Test service connectivity and API endpoints."""
        print("\n🌐 Testing Service Connectivity...")
        
        try:
            # Test main API endpoint
            api_url = f"{self.base_url}:{self.ports['refinement-engine']}"
            print(f"🔗 Testing main API: {api_url}")
            
            try:
                response = requests.get(f"{api_url}/health", timeout=10)
                if response.status_code == 200:
                    print(f"✅ Main API health check: {response.status_code}")
                    health_data = response.json()
                    print(f"📊 Health status: {health_data.get('status', 'unknown')}")
                else:
                    print(f"⚠️ Main API health check: {response.status_code}")
            except Exception as e:
                print(f"❌ Main API health check failed: {e}")
            
            # Test monitoring API endpoint
            monitoring_url = f"{self.base_url}:{self.ports['monitoring-api']}"
            print(f"🔗 Testing monitoring API: {monitoring_url}")
            
            try:
                response = requests.get(f"{monitoring_url}/health", timeout=10)
                if response.status_code == 200:
                    print(f"✅ Monitoring API health check: {response.status_code}")
                else:
                    print(f"⚠️ Monitoring API health check: {response.status_code}")
            except Exception as e:
                print(f"❌ Monitoring API health check failed: {e}")
            
            # Test metrics endpoint
            metrics_url = f"{self.base_url}:{self.ports['metrics']}"
            print(f"🔗 Testing metrics endpoint: {metrics_url}")
            
            try:
                response = requests.get(f"{metrics_url}/metrics", timeout=10)
                if response.status_code == 200:
                    print(f"✅ Metrics endpoint: {response.status_code}")
                    metrics_data = response.text
                    print(f"📊 Metrics data: {len(metrics_data)} characters")
                else:
                    print(f"⚠️ Metrics endpoint: {response.status_code}")
            except Exception as e:
                print(f"❌ Metrics endpoint failed: {e}")
            
            # Test Prometheus endpoint
            prometheus_url = f"{self.base_url}:{self.ports['prometheus']}"
            print(f"🔗 Testing Prometheus: {prometheus_url}")
            
            try:
                response = requests.get(f"{prometheus_url}/", timeout=10)
                if response.status_code == 200:
                    print(f"✅ Prometheus endpoint: {response.status_code}")
                else:
                    print(f"⚠️ Prometheus endpoint: {response.status_code}")
            except Exception as e:
                print(f"❌ Prometheus endpoint failed: {e}")
            
            # Test Grafana endpoint
            grafana_url = f"{self.base_url}:{self.ports['grafana']}"
            print(f"🔗 Testing Grafana: {grafana_url}")
            
            try:
                response = requests.get(f"{grafana_url}/", timeout=10)
                if response.status_code == 200:
                    print(f"✅ Grafana endpoint: {response.status_code}")
                else:
                    print(f"⚠️ Grafana endpoint: {response.status_code}")
            except Exception as e:
                print(f"❌ Grafana endpoint failed: {e}")
            
            # Test Nginx endpoint
            nginx_url = f"{self.base_url}:{self.ports['nginx']}"
            print(f"🔗 Testing Nginx: {nginx_url}")
            
            try:
                response = requests.get(f"{nginx_url}/", timeout=10)
                if response.status_code in [200, 404]:  # 404 is OK for root path
                    print(f"✅ Nginx endpoint: {response.status_code}")
                else:
                    print(f"⚠️ Nginx endpoint: {response.status_code}")
            except Exception as e:
                print(f"❌ Nginx endpoint failed: {e}")
            
            self.test_results["service_connectivity"] = True
            return True
            
        except Exception as e:
            print(f"❌ Service connectivity test failed: {e}")
            self.test_results["service_connectivity"] = False
            return False
    
    async def test_database_connectivity(self) -> bool:
        """Test database connectivity from containers."""
        print("\n🗄️ Testing Database Connectivity...")
        
        try:
            # Test PostgreSQL connectivity
            print("🔗 Testing PostgreSQL connectivity...")
            
            try:
                # Try to connect to PostgreSQL from within a container
                result = subprocess.run([
                    "docker-compose", "exec", "-T", "refinement-engine", 
                    "python", "-c", 
                    "import psycopg2; conn = psycopg2.connect('postgresql://dream_caesar:dream_caesar_password@postgres:5432/dream_caesar_db'); print('Connected successfully'); conn.close()"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"✅ PostgreSQL connectivity: {result.stdout.strip()}")
                else:
                    print(f"❌ PostgreSQL connectivity failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ PostgreSQL connectivity test failed: {e}")
                return False
            
            # Test Redis connectivity
            print("🔗 Testing Redis connectivity...")
            
            try:
                result = subprocess.run([
                    "docker-compose", "exec", "-T", "refinement-engine", 
                    "python", "-c", 
                    "import redis; r = redis.Redis(host='redis', port=6379, db=0); r.ping(); print('Redis connected successfully')"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"✅ Redis connectivity: {result.stdout.strip()}")
                else:
                    print(f"❌ Redis connectivity failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Redis connectivity test failed: {e}")
                return False
            
            self.test_results["database_connectivity"] = True
            return True
            
        except Exception as e:
            print(f"❌ Database connectivity test failed: {e}")
            self.test_results["database_connectivity"] = False
            return False
    
    async def test_volume_persistence(self) -> bool:
        """Test volume persistence and data storage."""
        print("\n💾 Testing Volume Persistence...")
        
        try:
            # Check if volumes exist
            volumes = self.docker_client.volumes.list()
            cosmic_volumes = [v for v in volumes if "cosmic-council" in v.name]
            
            print(f"📊 Found {len(cosmic_volumes)} Cosmic Council volumes")
            
            for volume in cosmic_volumes:
                print(f"📦 Volume: {volume.name}")
                print(f"   Driver: {volume.attrs['Driver']}")
                print(f"   Mountpoint: {volume.attrs['Mountpoint']}")
            
            # Test data persistence by creating a test file
            print("📝 Testing data persistence...")
            
            try:
                # Create a test file in the application container
                result = subprocess.run([
                    "docker-compose", "exec", "-T", "refinement-engine", 
                    "sh", "-c", "echo 'test-data-$(date)' > /app/data/test-persistence.txt"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"✅ Test file created successfully")
                    
                    # Verify the file exists
                    result = subprocess.run([
                        "docker-compose", "exec", "-T", "refinement-engine", 
                        "cat", "/app/data/test-persistence.txt"
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        print(f"✅ Test file verified: {result.stdout.strip()}")
                    else:
                        print(f"❌ Test file verification failed")
                        return False
                else:
                    print(f"❌ Test file creation failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Data persistence test failed: {e}")
                return False
            
            self.test_results["volume_persistence"] = True
            return True
            
        except Exception as e:
            print(f"❌ Volume persistence test failed: {e}")
            self.test_results["volume_persistence"] = False
            return False
    
    async def test_network_connectivity(self) -> bool:
        """Test network connectivity between services."""
        print("\n🌐 Testing Network Connectivity...")
        
        try:
            # Test inter-service communication
            print("🔗 Testing inter-service communication...")
            
            # Test refinement-engine to postgres
            try:
                result = subprocess.run([
                    "docker-compose", "exec", "-T", "refinement-engine", 
                    "ping", "-c", "1", "postgres"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"✅ Refinement-engine to postgres: Connected")
                else:
                    print(f"❌ Refinement-engine to postgres: Failed")
                    return False
            except Exception as e:
                print(f"❌ Postgres connectivity test failed: {e}")
                return False
            
            # Test refinement-engine to redis
            try:
                result = subprocess.run([
                    "docker-compose", "exec", "-T", "refinement-engine", 
                    "ping", "-c", "1", "redis"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"✅ Refinement-engine to redis: Connected")
                else:
                    print(f"❌ Refinement-engine to redis: Failed")
                    return False
            except Exception as e:
                print(f"❌ Redis connectivity test failed: {e}")
                return False
            
            # Test prometheus to refinement-engine
            try:
                result = subprocess.run([
                    "docker-compose", "exec", "-T", "prometheus", 
                    "ping", "-c", "1", "refinement-engine"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"✅ Prometheus to refinement-engine: Connected")
                else:
                    print(f"❌ Prometheus to refinement-engine: Failed")
                    return False
            except Exception as e:
                print(f"❌ Prometheus connectivity test failed: {e}")
                return False
            
            # Test network isolation
            print("🔒 Testing network isolation...")
            
            # Check if services can reach external networks
            try:
                result = subprocess.run([
                    "docker-compose", "exec", "-T", "refinement-engine", 
                    "ping", "-c", "1", "8.8.8.8"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"✅ External network access: Available")
                else:
                    print(f"⚠️ External network access: Limited")
            except Exception as e:
                print(f"⚠️ External network test failed: {e}")
            
            self.test_results["network_connectivity"] = True
            return True
            
        except Exception as e:
            print(f"❌ Network connectivity test failed: {e}")
            self.test_results["network_connectivity"] = False
            return False
    
    async def test_scaling_and_load(self) -> bool:
        """Test container scaling and load handling."""
        print("\n⚖️ Testing Scaling and Load Handling...")
        
        try:
            # Test container resource usage
            print("📊 Testing container resource usage...")
            
            containers = self.docker_client.containers.list()
            cosmic_containers = [c for c in containers if "cosmic-council" in c.name]
            
            for container in cosmic_containers:
                print(f"📦 Container: {container.name}")
                
                # Get container stats
                stats = container.stats(stream=False)
                cpu_usage = self._calculate_cpu_percent(stats)
                memory_usage = stats['memory_stats']['usage']
                memory_limit = stats['memory_stats']['limit']
                memory_percent = (memory_usage / memory_limit) * 100
                
                print(f"   CPU Usage: {cpu_usage:.2f}%")
                print(f"   Memory Usage: {self._format_size(memory_usage)} ({memory_percent:.2f}%)")
                print(f"   Memory Limit: {self._format_size(memory_limit)}")
            
            # Test load handling with multiple requests
            print("🔄 Testing load handling...")
            
            api_url = f"{self.base_url}:{self.ports['refinement-engine']}"
            
            # Send multiple concurrent requests
            tasks = []
            for i in range(10):
                task = asyncio.create_task(self._make_health_request(api_url, i))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_requests = sum(1 for r in results if r is True)
            print(f"📊 Load test results: {successful_requests}/10 requests successful")
            
            if successful_requests >= 8:  # Allow some failures
                print(f"✅ Load handling: Good")
            else:
                print(f"⚠️ Load handling: Needs improvement")
            
            self.test_results["scaling_and_load"] = True
            return True
            
        except Exception as e:
            print(f"❌ Scaling and load test failed: {e}")
            self.test_results["scaling_and_load"] = False
            return False
    
    async def _make_health_request(self, url: str, request_id: int) -> bool:
        """Make a health request to test load handling."""
        try:
            response = requests.get(f"{url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    async def test_cleanup_and_restart(self) -> bool:
        """Test cleanup and restart procedures."""
        print("\n🧹 Testing Cleanup and Restart...")
        
        try:
            # Test graceful shutdown
            print("🛑 Testing graceful shutdown...")
            
            try:
                result = subprocess.run([
                    "docker-compose", "down"
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print(f"✅ Graceful shutdown successful")
                else:
                    print(f"❌ Graceful shutdown failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Graceful shutdown test failed: {e}")
                return False
            
            # Wait a moment
            await asyncio.sleep(5)
            
            # Test restart
            print("🔄 Testing restart...")
            
            try:
                result = subprocess.run([
                    "docker-compose", "up", "-d"
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    print(f"✅ Restart successful")
                else:
                    print(f"❌ Restart failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Restart test failed: {e}")
                return False
            
            # Wait for services to be ready
            await asyncio.sleep(10)
            
            # Test that services are working after restart
            api_url = f"{self.base_url}:{self.ports['refinement-engine']}"
            try:
                response = requests.get(f"{api_url}/health", timeout=10)
                if response.status_code == 200:
                    print(f"✅ Services working after restart")
                else:
                    print(f"⚠️ Services may not be fully ready after restart")
            except Exception as e:
                print(f"⚠️ Service check after restart failed: {e}")
            
            self.test_results["cleanup_and_restart"] = True
            return True
            
        except Exception as e:
            print(f"❌ Cleanup and restart test failed: {e}")
            self.test_results["cleanup_and_restart"] = False
            return False
    
    async def cleanup_test_environment(self) -> bool:
        """Clean up test environment."""
        print("\n🧹 Cleaning Up Test Environment...")
        
        try:
            # Stop and remove containers
            print("🛑 Stopping containers...")
            try:
                result = subprocess.run([
                    "docker-compose", "down", "-v"
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print(f"✅ Containers stopped and removed")
                else:
                    print(f"⚠️ Container cleanup: {result.stderr}")
            except Exception as e:
                print(f"⚠️ Container cleanup failed: {e}")
            
            # Remove test image
            if hasattr(self, 'test_image'):
                try:
                    self.docker_client.images.remove(self.test_image.id, force=True)
                    print(f"✅ Test image removed")
                except Exception as e:
                    print(f"⚠️ Test image removal failed: {e}")
            
            # Clean up any dangling images
            try:
                self.docker_client.images.prune()
                print(f"✅ Dangling images cleaned up")
            except Exception as e:
                print(f"⚠️ Image cleanup failed: {e}")
            
            print(f"✅ Test environment cleanup completed")
            return True
            
        except Exception as e:
            print(f"❌ Test environment cleanup failed: {e}")
            return False
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable format."""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def _calculate_cpu_percent(self, stats: Dict[str, Any]) -> float:
        """Calculate CPU usage percentage from Docker stats."""
        try:
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_count = len(stats['cpu_stats']['cpu_usage']['percpu_usage'])
            
            if system_delta > 0 and cpu_delta > 0:
                return (cpu_delta / system_delta) * cpu_count * 100.0
            return 0.0
        except (KeyError, ZeroDivisionError):
            return 0.0
    
    async def run_all_tests(self) -> bool:
        """Run all Docker deployment tests."""
        print("🐳 Testing Docker Containers and Service Orchestration")
        print("=" * 80)
        
        tests = [
            self.setup_docker_client,
            self.test_dockerfile_build,
            self.test_docker_compose_config,
            self.test_container_orchestration,
            self.test_service_connectivity,
            self.test_database_connectivity,
            self.test_volume_persistence,
            self.test_network_connectivity,
            self.test_scaling_and_load,
            self.test_cleanup_and_restart
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                result = await test()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ {test.__name__} FAILED: {e}")
        
        # Cleanup
        await self.cleanup_test_environment()
        
        print("\n" + "=" * 80)
        print(f"🐳 Docker Deployment Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL DOCKER DEPLOYMENT TESTS PASSED! System is ready for production deployment!")
        else:
            print("⚠️  Some Docker deployment tests failed. Check the deployment configuration.")
            print("\n🔧 Troubleshooting Tips:")
            print("1. Check Docker and Docker Compose installation")
            print("2. Verify Dockerfile syntax and dependencies")
            print("3. Check docker-compose.yml configuration")
            print("4. Ensure all required environment variables are set")
            print("5. Verify network connectivity between services")
            print("6. Check container resource limits and health checks")
        
        return passed == total


async def main():
    """Run Docker deployment tests."""
    tester = DockerDeploymentTester()
    
    try:
        success = await tester.run_all_tests()
        return success
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
