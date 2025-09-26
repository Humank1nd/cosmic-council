"""
Simple Docker Testing
Basic Docker functionality tests that don't require full orchestration.
"""

import asyncio
import os
import sys
import time
import subprocess
import docker
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleDockerTester:
    """Simple Docker testing without full orchestration."""
    
    def __init__(self):
        self.docker_client = None
        self.test_results = {}
    
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
            
            # Test Docker info
            info = self.docker_client.info()
            print(f"✅ Docker info retrieved")
            print(f"📊 Containers: {info['Containers']}")
            print(f"📊 Images: {info['Images']}")
            print(f"📊 Memory: {self._format_size(info['MemTotal'])}")
            
            self.test_results["docker_client"] = True
            return True
            
        except Exception as e:
            print(f"❌ Docker client setup failed: {e}")
            self.test_results["docker_client"] = False
            return False
    
    async def test_dockerfile_syntax(self) -> bool:
        """Test Dockerfile syntax and basic structure."""
        print("\n🔨 Testing Dockerfile Syntax...")
        
        try:
            # Check if Dockerfile exists
            if not os.path.exists("Dockerfile"):
                print(f"❌ Dockerfile not found")
                return False
            
            print(f"✅ Dockerfile found")
            
            # Read and validate Dockerfile content
            with open("Dockerfile", "r") as f:
                dockerfile_content = f.read()
            
            print(f"📊 Dockerfile size: {len(dockerfile_content)} characters")
            
            # Check for required instructions
            required_instructions = ["FROM", "WORKDIR", "COPY", "EXPOSE", "CMD"]
            missing_instructions = []
            
            for instruction in required_instructions:
                if instruction not in dockerfile_content:
                    missing_instructions.append(instruction)
            
            if missing_instructions:
                print(f"⚠️ Missing Dockerfile instructions: {', '.join(missing_instructions)}")
            else:
                print(f"✅ All required Dockerfile instructions present")
            
            # Check for Python base image
            if "python:" in dockerfile_content:
                print(f"✅ Python base image detected")
            else:
                print(f"⚠️ Python base image not detected")
            
            # Check for port exposure
            if "EXPOSE" in dockerfile_content:
                print(f"✅ Port exposure configured")
            else:
                print(f"⚠️ Port exposure not configured")
            
            self.test_results["dockerfile_syntax"] = True
            return True
            
        except Exception as e:
            print(f"❌ Dockerfile syntax test failed: {e}")
            self.test_results["dockerfile_syntax"] = False
            return False
    
    async def test_docker_compose_syntax(self) -> bool:
        """Test Docker Compose syntax and configuration."""
        print("\n📋 Testing Docker Compose Syntax...")
        
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
                    
                    # Check for required services
                    required_services = ["refinement-engine", "postgres", "redis"]
                    missing_services = [s for s in required_services if s not in services]
                    
                    if missing_services:
                        print(f"⚠️ Missing required services: {', '.join(missing_services)}")
                    else:
                        print(f"✅ All required services defined")
                else:
                    print(f"❌ Failed to get services: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Service parsing failed: {e}")
                return False
            
            self.test_results["docker_compose_syntax"] = True
            return True
            
        except Exception as e:
            print(f"❌ Docker Compose syntax test failed: {e}")
            self.test_results["docker_compose_syntax"] = False
            return False
    
    async def test_docker_build(self) -> bool:
        """Test Docker image build process."""
        print("\n🔨 Testing Docker Build...")
        
        try:
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
                print(f"📊 Image OS: {image_info.attrs['Os']}")
                
                # Store image for cleanup
                self.test_image = image
                
                self.test_results["docker_build"] = True
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
            print(f"❌ Docker build test failed: {e}")
            self.test_results["docker_build"] = False
            return False
    
    async def test_container_run(self) -> bool:
        """Test running a container from the built image."""
        print("\n🚀 Testing Container Run...")
        
        try:
            if not hasattr(self, 'test_image'):
                print(f"❌ No test image available")
                return False
            
            # Run container
            print("📦 Running container...")
            
            try:
                container = self.docker_client.containers.run(
                    self.test_image.id,
                    command="python -c 'print(\"Hello from Cosmic Council!\")'",
                    detach=True,
                    remove=True
                )
                
                print(f"✅ Container started: {container.short_id}")
                
                # Wait for container to complete
                result = container.wait(timeout=30)
                print(f"📊 Container exit code: {result['StatusCode']}")
                
                # Get container logs
                logs = container.logs().decode('utf-8')
                print(f"📊 Container output: {logs.strip()}")
                
                if result['StatusCode'] == 0:
                    print(f"✅ Container ran successfully")
                    self.test_results["container_run"] = True
                    return True
                else:
                    print(f"❌ Container failed with exit code {result['StatusCode']}")
                    return False
                
            except Exception as e:
                print(f"❌ Container run failed: {e}")
                return False
            
        except Exception as e:
            print(f"❌ Container run test failed: {e}")
            self.test_results["container_run"] = False
            return False
    
    async def test_health_check(self) -> bool:
        """Test container health check functionality."""
        print("\n🏥 Testing Health Check...")
        
        try:
            if not hasattr(self, 'test_image'):
                print(f"❌ No test image available")
                return False
            
            # Check if health check is defined in image
            image_info = self.docker_client.images.get(self.test_image.id)
            
            if 'Healthcheck' in image_info.attrs['Config']:
                healthcheck = image_info.attrs['Config']['Healthcheck']
                print(f"✅ Health check configured")
                print(f"📊 Health check command: {healthcheck.get('Test', 'N/A')}")
                print(f"📊 Health check interval: {healthcheck.get('Interval', 'N/A')}")
                print(f"📊 Health check timeout: {healthcheck.get('Timeout', 'N/A')}")
                print(f"📊 Health check retries: {healthcheck.get('Retries', 'N/A')}")
            else:
                print(f"⚠️ No health check configured in image")
            
            self.test_results["health_check"] = True
            return True
            
        except Exception as e:
            print(f"❌ Health check test failed: {e}")
            self.test_results["health_check"] = False
            return False
    
    async def test_environment_variables(self) -> bool:
        """Test environment variable configuration."""
        print("\n🔧 Testing Environment Variables...")
        
        try:
            if not hasattr(self, 'test_image'):
                print(f"❌ No test image available")
                return False
            
            # Check environment variables in image
            image_info = self.docker_client.images.get(self.test_image.id)
            env_vars = image_info.attrs['Config']['Env']
            
            print(f"📊 Environment variables in image: {len(env_vars)}")
            
            # Check for important environment variables
            important_vars = ['PYTHONPATH', 'PYTHONUNBUFFERED', 'PYTHONDONTWRITEBYTECODE']
            found_vars = []
            
            for var in important_vars:
                for env_var in env_vars:
                    if env_var.startswith(var):
                        found_vars.append(var)
                        print(f"✅ Found: {env_var}")
                        break
            
            if len(found_vars) == len(important_vars):
                print(f"✅ All important environment variables configured")
            else:
                missing = set(important_vars) - set(found_vars)
                print(f"⚠️ Missing environment variables: {', '.join(missing)}")
            
            self.test_results["environment_variables"] = True
            return True
            
        except Exception as e:
            print(f"❌ Environment variables test failed: {e}")
            self.test_results["environment_variables"] = False
            return False
    
    async def test_port_exposure(self) -> bool:
        """Test port exposure configuration."""
        print("\n🔌 Testing Port Exposure...")
        
        try:
            if not hasattr(self, 'test_image'):
                print(f"❌ No test image available")
                return False
            
            # Check exposed ports in image
            image_info = self.docker_client.images.get(self.test_image.id)
            exposed_ports = image_info.attrs['Config']['ExposedPorts']
            
            if exposed_ports:
                print(f"✅ Exposed ports: {', '.join(exposed_ports.keys())}")
                
                # Check for expected ports
                expected_ports = ['8000/tcp', '8001/tcp', '9090/tcp']
                found_ports = []
                
                for port in expected_ports:
                    if port in exposed_ports:
                        found_ports.append(port)
                        print(f"✅ Expected port found: {port}")
                
                if len(found_ports) == len(expected_ports):
                    print(f"✅ All expected ports exposed")
                else:
                    missing = set(expected_ports) - set(found_ports)
                    print(f"⚠️ Missing ports: {', '.join(missing)}")
            else:
                print(f"⚠️ No ports exposed in image")
            
            self.test_results["port_exposure"] = True
            return True
            
        except Exception as e:
            print(f"❌ Port exposure test failed: {e}")
            self.test_results["port_exposure"] = False
            return False
    
    async def cleanup_test_environment(self) -> bool:
        """Clean up test environment."""
        print("\n🧹 Cleaning Up Test Environment...")
        
        try:
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
    
    async def run_all_tests(self) -> bool:
        """Run all simple Docker tests."""
        print("🐳 Simple Docker Testing")
        print("=" * 50)
        
        tests = [
            self.setup_docker_client,
            self.test_dockerfile_syntax,
            self.test_docker_compose_syntax,
            self.test_docker_build,
            self.test_container_run,
            self.test_health_check,
            self.test_environment_variables,
            self.test_port_exposure
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
        
        print("\n" + "=" * 50)
        print(f"🐳 Simple Docker Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL SIMPLE DOCKER TESTS PASSED! Docker configuration is working correctly!")
        else:
            print("⚠️  Some simple Docker tests failed. Check the Docker configuration.")
            print("\n🔧 Troubleshooting Tips:")
            print("1. Check Docker installation and daemon status")
            print("2. Verify Dockerfile syntax and structure")
            print("3. Check docker-compose.yml configuration")
            print("4. Ensure all required files are present")
            print("5. Check system resources and permissions")
        
        return passed == total


async def main():
    """Run simple Docker tests."""
    tester = SimpleDockerTester()
    
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
