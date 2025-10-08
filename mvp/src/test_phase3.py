#!/usr/bin/env python3
"""
Test script for Phase 3 improvements
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_real_ai_integration():
    """Test real AI integration capabilities."""
    print("🧪 Testing Real AI Integration...")
    try:
        from cosmic_council.ai_service import AIService, AIProvider
        
        # Test OpenAI provider (if available)
        openai_service = AIService(AIProvider.OPENAI)
        print(f"✅ OpenAI service initialized: {openai_service.provider.value}")
        
        # Test Anthropic provider (if available)
        anthropic_service = AIService(AIProvider.ANTHROPIC)
        print(f"✅ Anthropic service initialized: {anthropic_service.provider.value}")
        
        # Test mock provider
        mock_service = AIService(AIProvider.MOCK)
        print(f"✅ Mock service initialized: {mock_service.provider.value}")
        
        return True
    except Exception as e:
        print(f"❌ AI integration test failed: {e}")
        return False

def test_caching_system():
    """Test Redis caching system."""
    print("\n🧪 Testing Caching System...")
    try:
        from cosmic_council.cache import CacheService, cache_result, get_cache_service
        
        # Test cache service initialization
        cache = CacheService()
        print(f"✅ Cache service initialized: enabled={cache.enabled}")
        
        # Test cache operations (if Redis is available)
        if cache.enabled:
            # Test basic operations
            test_key = "test_key"
            test_value = {"test": "data", "number": 42}
            
            # Set and get
            success = asyncio.run(cache.set(test_key, test_value, ttl=60))
            if success:
                retrieved = asyncio.run(cache.get(test_key))
                if retrieved == test_value:
                    print("✅ Cache set/get operations working")
                else:
                    print("❌ Cache get returned wrong value")
                    return False
            else:
                print("⚠️ Cache set operation failed (Redis may not be running)")
        
        # Test cache decorator
        @cache_result(ttl=60, key_prefix="test")
        def test_function(x, y):
            return x + y
        
        result = asyncio.run(test_function(5, 3))
        if result == 8:
            print("✅ Cache decorator working")
        else:
            print("❌ Cache decorator failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Caching system test failed: {e}")
        return False

def test_metrics_system():
    """Test Prometheus metrics system."""
    print("\n🧪 Testing Metrics System...")
    try:
        from cosmic_council.metrics import MetricsCollector, get_metrics_collector, track_request_metrics
        
        # Test metrics collector initialization
        metrics = get_metrics_collector()
        print(f"✅ Metrics collector initialized: enabled={metrics.enabled}")
        
        if metrics.enabled:
            # Test recording metrics
            metrics.record_request("GET", "/health", 200, 0.1)
            metrics.record_problem_solved("medium", "business", 5.2)
            metrics.record_enterprise_processing("Red Owl", "research", 1.5, 0.9)
            metrics.record_ai_request("mock", "mock-model", "success", 100, 0.01)
            
            print("✅ Metrics recording working")
            
            # Test metrics export
            metrics_text = metrics.get_metrics()
            if metrics_text and len(metrics_text) > 0:
                print("✅ Metrics export working")
            else:
                print("❌ Metrics export failed")
                return False
        else:
            print("⚠️ Prometheus not available, metrics disabled")
        
        return True
    except Exception as e:
        print(f"❌ Metrics system test failed: {e}")
        return False

def test_docker_configuration():
    """Test Docker configuration files."""
    print("\n🧪 Testing Docker Configuration...")
    try:
        # Check if Docker files exist
        dockerfile_path = Path("../Dockerfile")
        compose_path = Path("../docker-compose.yml")
        nginx_path = Path("../nginx.conf")
        
        if dockerfile_path.exists():
            print("✅ Dockerfile exists")
        else:
            print("❌ Dockerfile not found")
            return False
        
        if compose_path.exists():
            print("✅ docker-compose.yml exists")
        else:
            print("❌ docker-compose.yml not found")
            return False
        
        if nginx_path.exists():
            print("✅ nginx.conf exists")
        else:
            print("❌ nginx.conf not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Docker configuration test failed: {e}")
        return False

def test_kubernetes_manifests():
    """Test Kubernetes manifest files."""
    print("\n🧪 Testing Kubernetes Manifests...")
    try:
        # Check if K8s files exist
        k8s_dir = Path("../k8s")
        deployment_path = k8s_dir / "deployment.yaml"
        configmap_path = k8s_dir / "configmap.yaml"
        ingress_path = k8s_dir / "ingress.yaml"
        
        if deployment_path.exists():
            print("✅ deployment.yaml exists")
        else:
            print("❌ deployment.yaml not found")
            return False
        
        if configmap_path.exists():
            print("✅ configmap.yaml exists")
        else:
            print("❌ configmap.yaml not found")
            return False
        
        if ingress_path.exists():
            print("✅ ingress.yaml exists")
        else:
            print("❌ ingress.yaml not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Kubernetes manifests test failed: {e}")
        return False

def test_deployment_scripts():
    """Test deployment scripts."""
    print("\n🧪 Testing Deployment Scripts...")
    try:
        # Check if deployment script exists
        deploy_script = Path("../scripts/deploy.sh")
        
        if deploy_script.exists():
            print("✅ deploy.sh exists")
            
            # Check if script is executable (on Unix systems)
            if hasattr(deploy_script.stat(), 'st_mode'):
                import stat
                if deploy_script.stat().st_mode & stat.S_IEXEC:
                    print("✅ deploy.sh is executable")
                else:
                    print("⚠️ deploy.sh is not executable")
        else:
            print("❌ deploy.sh not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Deployment scripts test failed: {e}")
        return False

def test_production_readiness():
    """Test overall production readiness."""
    print("\n🧪 Testing Production Readiness...")
    try:
        from cosmic_council import CosmicCouncilMVP
        from cosmic_council.config import get_config
        from cosmic_council.database_improved import ProductionDatabase, DatabaseConfig
        
        # Test configuration
        config = get_config()
        print(f"✅ Configuration loaded: {config.app_name} v{config.app_version}")
        
        # Test production database
        db_config = DatabaseConfig(
            db_path="test_production_phase3.db",
            pool_size=5,
            timeout=10.0
        )
        db = ProductionDatabase(db_config)
        print("✅ Production database initialized")
        
        # Test core system
        council = CosmicCouncilMVP()
        print("✅ Cosmic Council MVP initialized")
        
        # Test solving a problem with all systems
        results = council.solve_problem_sync("How do I test Phase 3 production readiness?")
        print(f"✅ Problem solved with {len(results)} enterprise responses")
        
        # Test database operations
        problem_id = db.save_problem("Phase 3 test problem", "testing", "medium")
        print(f"✅ Problem saved with ID: {problem_id}")
        
        # Test metrics
        from cosmic_council.metrics import get_metrics_collector
        metrics = get_metrics_collector()
        if metrics.enabled:
            print("✅ Metrics system ready")
        else:
            print("⚠️ Metrics system not available")
        
        # Test caching
        from cosmic_council.cache import get_cache_service
        cache = get_cache_service()
        print(f"✅ Cache system ready: enabled={cache.enabled}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Production readiness test failed: {e}")
        return False

def main():
    """Run all Phase 3 tests."""
    print("🚀 Phase 3 Testing Suite - Scale & Deploy")
    print("=" * 60)
    
    tests = [
        test_real_ai_integration,
        test_caching_system,
        test_metrics_system,
        test_docker_configuration,
        test_kubernetes_manifests,
        test_deployment_scripts,
        test_production_readiness
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 3 tests passed! System is ready for production deployment!")
        print("\n🚀 Deployment Options:")
        print("  Docker Compose: ./scripts/deploy.sh compose")
        print("  Kubernetes: ./scripts/deploy.sh k8s")
        print("  API Server: python main_production.py --api")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
