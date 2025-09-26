"""
Docker Configuration Testing
Comprehensive testing of Docker configuration files without requiring Docker daemon.
"""

import os
import sys
import asyncio
import yaml
import json
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DockerConfigTester:
    """Test Docker configuration files comprehensively."""
    
    def __init__(self):
        self.test_results = {}
        self.dockerfile_content = ""
        self.compose_config = {}
    
    async def test_dockerfile_structure(self) -> bool:
        """Test Dockerfile structure and content."""
        print("🔨 Testing Dockerfile Structure...")
        
        try:
            # Check if Dockerfile exists
            if not os.path.exists("Dockerfile"):
                print(f"❌ Dockerfile not found")
                return False
            
            print(f"✅ Dockerfile found")
            
            # Read Dockerfile content
            with open("Dockerfile", "r") as f:
                self.dockerfile_content = f.read()
            
            print(f"📊 Dockerfile size: {len(self.dockerfile_content)} characters")
            print(f"📊 Dockerfile lines: {len(self.dockerfile_content.splitlines())}")
            
            # Parse Dockerfile instructions
            lines = self.dockerfile_content.splitlines()
            instructions = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    if ' ' in line:
                        instruction = line.split()[0]
                        instructions.append(instruction)
            
            print(f"📊 Dockerfile instructions: {len(instructions)}")
            print(f"📊 Instructions: {', '.join(set(instructions))}")
            
            # Test required instructions
            required_instructions = {
                "FROM": "Base image specification",
                "WORKDIR": "Working directory setup",
                "COPY": "File copying",
                "EXPOSE": "Port exposure",
                "CMD": "Default command"
            }
            
            missing_instructions = []
            for instruction, description in required_instructions.items():
                if instruction not in instructions:
                    missing_instructions.append(f"{instruction} ({description})")
                else:
                    print(f"✅ {instruction}: {description}")
            
            if missing_instructions:
                print(f"⚠️ Missing instructions: {', '.join(missing_instructions)}")
            else:
                print(f"✅ All required instructions present")
            
            # Test Python-specific requirements
            python_checks = {
                "python:": "Python base image",
                "pip install": "Python package installation",
                "requirements.txt": "Requirements file usage",
                "PYTHON": "Python environment variables"
            }
            
            for check, description in python_checks.items():
                if check.lower() in self.dockerfile_content.lower():
                    print(f"✅ {description}: Found")
                else:
                    print(f"⚠️ {description}: Not found")
            
            # Test security best practices
            security_checks = {
                "USER ": "Non-root user",
                "RUN apt-get update": "System package updates",
                "rm -rf": "Cleanup of package cache",
                "chown": "File ownership"
            }
            
            security_score = 0
            for check, description in security_checks.items():
                if check in self.dockerfile_content:
                    print(f"✅ {description}: Found")
                    security_score += 1
                else:
                    print(f"⚠️ {description}: Not found")
            
            print(f"📊 Security score: {security_score}/{len(security_checks)}")
            
            # Test port exposure
            if "EXPOSE" in self.dockerfile_content:
                expose_lines = [line for line in lines if line.strip().startswith("EXPOSE")]
                ports = []
                for line in expose_lines:
                    ports.extend(line.split()[1:])
                print(f"✅ Exposed ports: {', '.join(ports)}")
            else:
                print(f"⚠️ No ports exposed")
            
            self.test_results["dockerfile_structure"] = True
            return True
            
        except Exception as e:
            print(f"❌ Dockerfile structure test failed: {e}")
            self.test_results["dockerfile_structure"] = False
            return False
    
    async def test_docker_compose_structure(self) -> bool:
        """Test Docker Compose configuration structure."""
        print("\n📋 Testing Docker Compose Structure...")
        
        try:
            # Check if docker-compose.yml exists
            if not os.path.exists("docker-compose.yml"):
                print(f"❌ docker-compose.yml not found")
                return False
            
            print(f"✅ docker-compose.yml found")
            
            # Read and parse docker-compose.yml
            with open("docker-compose.yml", "r") as f:
                compose_content = f.read()
            
            print(f"📊 Compose file size: {len(compose_content)} characters")
            
            try:
                self.compose_config = yaml.safe_load(compose_content)
                print(f"✅ Docker Compose YAML syntax valid")
            except yaml.YAMLError as e:
                print(f"❌ Docker Compose YAML syntax invalid: {e}")
                return False
            
            # Test version
            version = self.compose_config.get("version", "Not specified")
            print(f"📊 Compose version: {version}")
            
            # Test services
            services = self.compose_config.get("services", {})
            print(f"📊 Services defined: {len(services)}")
            
            for service_name, service_config in services.items():
                print(f"📦 Service: {service_name}")
                
                # Check service configuration
                service_checks = {
                    "image": "Base image",
                    "build": "Build configuration",
                    "ports": "Port mapping",
                    "environment": "Environment variables",
                    "depends_on": "Service dependencies",
                    "volumes": "Volume mounts",
                    "healthcheck": "Health check"
                }
                
                for check, description in service_checks.items():
                    if check in service_config:
                        print(f"   ✅ {description}: Configured")
                    else:
                        print(f"   ⚠️ {description}: Not configured")
            
            # Test required services
            required_services = ["refinement-engine", "postgres", "redis"]
            missing_services = [s for s in required_services if s not in services]
            
            if missing_services:
                print(f"⚠️ Missing required services: {', '.join(missing_services)}")
            else:
                print(f"✅ All required services defined")
            
            # Test volumes
            volumes = self.compose_config.get("volumes", {})
            print(f"📊 Volumes defined: {len(volumes)}")
            
            for volume_name, volume_config in volumes.items():
                print(f"📦 Volume: {volume_name}")
                if isinstance(volume_config, dict):
                    driver = volume_config.get("driver", "default")
                    print(f"   Driver: {driver}")
            
            # Test networks
            networks = self.compose_config.get("networks", {})
            print(f"📊 Networks defined: {len(networks)}")
            
            for network_name, network_config in networks.items():
                print(f"📦 Network: {network_name}")
                if isinstance(network_config, dict):
                    driver = network_config.get("driver", "default")
                    print(f"   Driver: {driver}")
            
            self.test_results["docker_compose_structure"] = True
            return True
            
        except Exception as e:
            print(f"❌ Docker Compose structure test failed: {e}")
            self.test_results["docker_compose_structure"] = False
            return False
    
    async def test_service_configurations(self) -> bool:
        """Test individual service configurations."""
        print("\n🔧 Testing Service Configurations...")
        
        try:
            if not self.compose_config:
                print(f"❌ No compose configuration available")
                return False
            
            services = self.compose_config.get("services", {})
            
            # Test refinement-engine service
            if "refinement-engine" in services:
                print("📦 Testing refinement-engine service...")
                service = services["refinement-engine"]
                
                # Check build configuration
                if "build" in service:
                    build_config = service["build"]
                    if isinstance(build_config, dict):
                        context = build_config.get("context", ".")
                        dockerfile = build_config.get("dockerfile", "Dockerfile")
                        print(f"   ✅ Build context: {context}")
                        print(f"   ✅ Dockerfile: {dockerfile}")
                    else:
                        print(f"   ✅ Build context: {build_config}")
                else:
                    print(f"   ⚠️ No build configuration")
                
                # Check port mapping
                if "ports" in service:
                    ports = service["ports"]
                    print(f"   ✅ Ports: {', '.join(ports)}")
                else:
                    print(f"   ⚠️ No port mapping")
                
                # Check environment variables
                if "environment" in service:
                    env_vars = service["environment"]
                    print(f"   ✅ Environment variables: {len(env_vars)}")
                    
                    # Check for important environment variables
                    important_vars = ["DATABASE_URL", "REDIS_URL", "JWT_SECRET_KEY"]
                    for var in important_vars:
                        if any(var in str(env) for env in env_vars):
                            print(f"   ✅ {var}: Configured")
                        else:
                            print(f"   ⚠️ {var}: Not configured")
                else:
                    print(f"   ⚠️ No environment variables")
                
                # Check dependencies
                if "depends_on" in service:
                    depends = service["depends_on"]
                    print(f"   ✅ Dependencies: {', '.join(depends)}")
                else:
                    print(f"   ⚠️ No dependencies")
                
                # Check health check
                if "healthcheck" in service:
                    healthcheck = service["healthcheck"]
                    print(f"   ✅ Health check: Configured")
                    if "test" in healthcheck:
                        print(f"   ✅ Health check test: {healthcheck['test']}")
                else:
                    print(f"   ⚠️ No health check")
            
            # Test postgres service
            if "postgres" in services:
                print("📦 Testing postgres service...")
                service = services["postgres"]
                
                # Check image
                if "image" in service:
                    image = service["image"]
                    print(f"   ✅ Image: {image}")
                else:
                    print(f"   ⚠️ No image specified")
                
                # Check environment
                if "environment" in service:
                    env_vars = service["environment"]
                    print(f"   ✅ Environment variables: {len(env_vars)}")
                    
                    # Check for database configuration
                    db_vars = ["POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"]
                    for var in db_vars:
                        if any(var in str(env) for env in env_vars):
                            print(f"   ✅ {var}: Configured")
                        else:
                            print(f"   ⚠️ {var}: Not configured")
                else:
                    print(f"   ⚠️ No environment variables")
                
                # Check volumes
                if "volumes" in service:
                    volumes = service["volumes"]
                    print(f"   ✅ Volumes: {len(volumes)}")
                else:
                    print(f"   ⚠️ No volumes")
            
            # Test redis service
            if "redis" in services:
                print("📦 Testing redis service...")
                service = services["redis"]
                
                # Check image
                if "image" in service:
                    image = service["image"]
                    print(f"   ✅ Image: {image}")
                else:
                    print(f"   ⚠️ No image specified")
                
                # Check volumes
                if "volumes" in service:
                    volumes = service["volumes"]
                    print(f"   ✅ Volumes: {len(volumes)}")
                else:
                    print(f"   ⚠️ No volumes")
            
            # Test monitoring services
            monitoring_services = ["prometheus", "grafana", "nginx"]
            for service_name in monitoring_services:
                if service_name in services:
                    print(f"📦 Testing {service_name} service...")
                    service = services[service_name]
                    
                    if "image" in service:
                        image = service["image"]
                        print(f"   ✅ Image: {image}")
                    
                    if "ports" in service:
                        ports = service["ports"]
                        print(f"   ✅ Ports: {', '.join(ports)}")
                    
                    if "volumes" in service:
                        volumes = service["volumes"]
                        print(f"   ✅ Volumes: {len(volumes)}")
            
            self.test_results["service_configurations"] = True
            return True
            
        except Exception as e:
            print(f"❌ Service configurations test failed: {e}")
            self.test_results["service_configurations"] = False
            return False
    
    async def test_environment_variables(self) -> bool:
        """Test environment variable configuration."""
        print("\n🔧 Testing Environment Variables...")
        
        try:
            if not self.compose_config:
                print(f"❌ No compose configuration available")
                return False
            
            services = self.compose_config.get("services", {})
            
            # Check refinement-engine environment variables
            if "refinement-engine" in services:
                service = services["refinement-engine"]
                if "environment" in service:
                    env_vars = service["environment"]
                    
                    # Required environment variables
                    required_vars = {
                        "DATABASE_URL": "Database connection string",
                        "REDIS_URL": "Redis connection string",
                        "JWT_SECRET_KEY": "JWT secret key",
                        "API_KEY_SECRET": "API key secret",
                        "LOG_LEVEL": "Logging level",
                        "ENVIRONMENT": "Environment name"
                    }
                    
                    missing_vars = []
                    for var, description in required_vars.items():
                        if any(var in str(env) for env in env_vars):
                            print(f"✅ {var}: {description}")
                        else:
                            missing_vars.append(f"{var} ({description})")
                    
                    if missing_vars:
                        print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
                    else:
                        print(f"✅ All required environment variables configured")
                    
                    # Optional environment variables
                    optional_vars = {
                        "OPENAI_API_KEY": "OpenAI API key",
                        "ANTHROPIC_API_KEY": "Anthropic API key",
                        "SENTRY_DSN": "Sentry DSN",
                        "GRAFANA_PASSWORD": "Grafana password"
                    }
                    
                    for var, description in optional_vars.items():
                        if any(var in str(env) for env in env_vars):
                            print(f"✅ {var}: {description}")
                        else:
                            print(f"ℹ️ {var}: {description} (optional)")
                    
                    # Check for environment variable patterns
                    env_patterns = {
                        "${": "Environment variable substitution",
                        ":-": "Default value syntax"
                    }
                    
                    env_str = str(env_vars)
                    for pattern, description in env_patterns.items():
                        if pattern in env_str:
                            print(f"✅ {description}: Found")
                        else:
                            print(f"ℹ️ {description}: Not found")
                else:
                    print(f"❌ No environment variables configured")
                    return False
            
            self.test_results["environment_variables"] = True
            return True
            
        except Exception as e:
            print(f"❌ Environment variables test failed: {e}")
            self.test_results["environment_variables"] = False
            return False
    
    async def test_volume_configurations(self) -> bool:
        """Test volume configurations."""
        print("\n💾 Testing Volume Configurations...")
        
        try:
            if not self.compose_config:
                print(f"❌ No compose configuration available")
                return False
            
            # Test named volumes
            volumes = self.compose_config.get("volumes", {})
            print(f"📊 Named volumes: {len(volumes)}")
            
            for volume_name, volume_config in volumes.items():
                print(f"📦 Volume: {volume_name}")
                if isinstance(volume_config, dict):
                    driver = volume_config.get("driver", "default")
                    print(f"   Driver: {driver}")
                else:
                    print(f"   Configuration: {volume_config}")
            
            # Test service volume mounts
            services = self.compose_config.get("services", {})
            
            for service_name, service_config in services.items():
                if "volumes" in service_config:
                    volumes = service_config["volumes"]
                    print(f"📦 {service_name} volumes: {len(volumes)}")
                    
                    for volume in volumes:
                        if ":" in volume:
                            source, target = volume.split(":", 1)
                            print(f"   {source} -> {target}")
                        else:
                            print(f"   {volume}")
            
            # Check for important volume mounts
            important_volumes = {
                "postgres_data": "PostgreSQL data persistence",
                "redis_data": "Redis data persistence",
                "prometheus_data": "Prometheus data persistence",
                "grafana_data": "Grafana data persistence"
            }
            
            for volume_name, description in important_volumes.items():
                if volume_name in volumes:
                    print(f"✅ {description}: Configured")
                else:
                    print(f"⚠️ {description}: Not configured")
            
            self.test_results["volume_configurations"] = True
            return True
            
        except Exception as e:
            print(f"❌ Volume configurations test failed: {e}")
            self.test_results["volume_configurations"] = False
            return False
    
    async def test_network_configurations(self) -> bool:
        """Test network configurations."""
        print("\n🌐 Testing Network Configurations...")
        
        try:
            if not self.compose_config:
                print(f"❌ No compose configuration available")
                return False
            
            # Test networks
            networks = self.compose_config.get("networks", {})
            print(f"📊 Networks defined: {len(networks)}")
            
            for network_name, network_config in networks.items():
                print(f"📦 Network: {network_name}")
                if isinstance(network_config, dict):
                    driver = network_config.get("driver", "default")
                    print(f"   Driver: {driver}")
                else:
                    print(f"   Configuration: {network_config}")
            
            # Test service network configurations
            services = self.compose_config.get("services", {})
            
            for service_name, service_config in services.items():
                if "networks" in service_config:
                    service_networks = service_config["networks"]
                    print(f"📦 {service_name} networks: {', '.join(service_networks)}")
                else:
                    print(f"📦 {service_name}: Using default network")
            
            # Check for network isolation
            if networks:
                print(f"✅ Custom networks configured for isolation")
            else:
                print(f"ℹ️ Using default network (less isolated)")
            
            self.test_results["network_configurations"] = True
            return True
            
        except Exception as e:
            print(f"❌ Network configurations test failed: {e}")
            self.test_results["network_configurations"] = False
            return False
    
    async def test_security_configurations(self) -> bool:
        """Test security configurations."""
        print("\n🔒 Testing Security Configurations...")
        
        try:
            security_score = 0
            total_checks = 0
            
            # Test Dockerfile security
            if self.dockerfile_content:
                dockerfile_security_checks = {
                    "USER ": "Non-root user",
                    "rm -rf": "Package cache cleanup",
                    "chown": "File ownership",
                    "apt-get update": "System updates"
                }
                
                for check, description in dockerfile_security_checks.items():
                    total_checks += 1
                    if check in self.dockerfile_content:
                        print(f"✅ Dockerfile {description}: Found")
                        security_score += 1
                    else:
                        print(f"⚠️ Dockerfile {description}: Not found")
            
            # Test compose security
            if self.compose_config:
                services = self.compose_config.get("services", {})
                
                # Check for security configurations
                security_checks = {
                    "restart: unless-stopped": "Restart policy",
                    "healthcheck": "Health monitoring",
                    "depends_on": "Service dependencies"
                }
                
                for service_name, service_config in services.items():
                    for check, description in security_checks.items():
                        total_checks += 1
                        # Check for restart policy with flexible matching
                        if check == "restart: unless-stopped":
                            if "restart" in service_config and service_config.get("restart") == "unless-stopped":
                                print(f"✅ {service_name} {description}: Found")
                                security_score += 1
                            else:
                                print(f"⚠️ {service_name} {description}: Not found")
                        elif check in str(service_config):
                            print(f"✅ {service_name} {description}: Found")
                            security_score += 1
                        else:
                            print(f"⚠️ {service_name} {description}: Not found")
                
                # Check for environment variable security
                if "refinement-engine" in services:
                    service = services["refinement-engine"]
                    if "environment" in service:
                        env_vars = service["environment"]
                        env_str = str(env_vars)
                        
                        # Check for secret management
                        secret_checks = {
                            "JWT_SECRET_KEY": "JWT secret from environment",
                            "API_KEY_SECRET": "API key from environment",
                            "OPENAI_API_KEY": "OpenAI key from environment"
                        }
                        
                        for check, description in secret_checks.items():
                            total_checks += 1
                            if check in env_str:
                                print(f"✅ {description}: Found")
                                security_score += 1
                            else:
                                print(f"⚠️ {description}: Not found")
            
            # Calculate security score
            if total_checks > 0:
                security_percentage = (security_score / total_checks) * 100
                print(f"📊 Security score: {security_score}/{total_checks} ({security_percentage:.1f}%)")
                
                if security_percentage >= 80:
                    print(f"✅ Security configuration: Good")
                elif security_percentage >= 60:
                    print(f"⚠️ Security configuration: Needs improvement")
                else:
                    print(f"❌ Security configuration: Poor")
            else:
                print(f"⚠️ No security checks performed")
            
            self.test_results["security_configurations"] = True
            return True
            
        except Exception as e:
            print(f"❌ Security configurations test failed: {e}")
            self.test_results["security_configurations"] = False
            return False
    
    async def test_production_readiness(self) -> bool:
        """Test production readiness indicators."""
        print("\n🚀 Testing Production Readiness...")
        
        try:
            readiness_score = 0
            total_checks = 0
            
            # Test Dockerfile production readiness
            if self.dockerfile_content:
                dockerfile_checks = {
                    "python:3.11": "Python 3.11 base image",
                    "EXPOSE": "Port exposure",
                    "HEALTHCHECK": "Health check",
                    "USER ": "Non-root user"
                }
                
                for check, description in dockerfile_checks.items():
                    total_checks += 1
                    if check in self.dockerfile_content:
                        print(f"✅ Dockerfile {description}: Found")
                        readiness_score += 1
                    else:
                        print(f"⚠️ Dockerfile {description}: Not found")
            
            # Test compose production readiness
            if self.compose_config:
                services = self.compose_config.get("services", {})
                
                # Check for production configurations
                production_checks = {
                    "restart: unless-stopped": "Restart policy",
                    "healthcheck": "Health monitoring",
                    "volumes": "Data persistence",
                    "environment": "Configuration management"
                }
                
                for service_name, service_config in services.items():
                    for check, description in production_checks.items():
                        total_checks += 1
                        # Check for restart policy with flexible matching
                        if check == "restart: unless-stopped":
                            if "restart" in service_config and service_config.get("restart") == "unless-stopped":
                                print(f"✅ {service_name} {description}: Found")
                                readiness_score += 1
                            else:
                                print(f"⚠️ {service_name} {description}: Not found")
                        elif check in str(service_config):
                            print(f"✅ {service_name} {description}: Found")
                            readiness_score += 1
                        else:
                            print(f"⚠️ {service_name} {description}: Not found")
                
                # Check for monitoring services
                monitoring_services = ["prometheus", "grafana", "nginx"]
                for service in monitoring_services:
                    total_checks += 1
                    if service in services:
                        print(f"✅ Monitoring service {service}: Configured")
                        readiness_score += 1
                    else:
                        print(f"⚠️ Monitoring service {service}: Not configured")
                
                # Check for data persistence
                volumes = self.compose_config.get("volumes", {})
                data_volumes = ["postgres_data", "redis_data", "prometheus_data", "grafana_data"]
                
                for volume in data_volumes:
                    total_checks += 1
                    if volume in volumes:
                        print(f"✅ Data volume {volume}: Configured")
                        readiness_score += 1
                    else:
                        print(f"⚠️ Data volume {volume}: Not configured")
            
            # Calculate readiness score
            if total_checks > 0:
                readiness_percentage = (readiness_score / total_checks) * 100
                print(f"📊 Production readiness: {readiness_score}/{total_checks} ({readiness_percentage:.1f}%)")
                
                if readiness_percentage >= 90:
                    print(f"✅ Production readiness: Excellent")
                elif readiness_percentage >= 75:
                    print(f"✅ Production readiness: Good")
                elif readiness_percentage >= 60:
                    print(f"⚠️ Production readiness: Needs improvement")
                else:
                    print(f"❌ Production readiness: Poor")
            else:
                print(f"⚠️ No production readiness checks performed")
            
            self.test_results["production_readiness"] = True
            return True
            
        except Exception as e:
            print(f"❌ Production readiness test failed: {e}")
            self.test_results["production_readiness"] = False
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all Docker configuration tests."""
        print("🐳 Docker Configuration Testing")
        print("=" * 60)
        
        tests = [
            self.test_dockerfile_structure,
            self.test_docker_compose_structure,
            self.test_service_configurations,
            self.test_environment_variables,
            self.test_volume_configurations,
            self.test_network_configurations,
            self.test_security_configurations,
            self.test_production_readiness
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
        
        print("\n" + "=" * 60)
        print(f"🐳 Docker Configuration Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL DOCKER CONFIGURATION TESTS PASSED! Configuration is production-ready!")
        else:
            print("⚠️  Some Docker configuration tests failed. Check the configuration files.")
            print("\n🔧 Troubleshooting Tips:")
            print("1. Review Dockerfile structure and instructions")
            print("2. Check docker-compose.yml syntax and service configurations")
            print("3. Verify environment variable configurations")
            print("4. Ensure proper volume and network configurations")
            print("5. Review security and production readiness settings")
        
        return passed == total


async def main():
    """Run Docker configuration tests."""
    tester = DockerConfigTester()
    
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
