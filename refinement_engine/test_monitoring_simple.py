"""
Simple monitoring test to verify basic functionality.
"""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_basic_monitoring():
    """Test basic monitoring functionality."""
    print("📊 Testing Basic Monitoring Functionality...")
    
    try:
        # Test imports
        from monitoring import get_metrics_collector, get_sentry_integration
        from health_checks import get_health_checker
        print("✅ All imports successful")
        
        # Test metrics collector
        metrics_collector = get_metrics_collector()
        print("✅ Metrics collector initialized")
        
        # Test basic metrics recording
        metrics_collector.record_http_request("GET", "/test", 200, 0.5, "test_user")
        print("✅ HTTP request metric recorded")
        
        # Test metrics export
        metrics_data = metrics_collector.generate_metrics_export()
        print(f"✅ Metrics exported: {len(metrics_data)} characters")
        
        # Test Sentry integration
        sentry = get_sentry_integration()
        print("✅ Sentry integration initialized")
        
        # Test health checker
        health_checker = get_health_checker()
        print("✅ Health checker initialized")
        
        # Test basic health check
        health_status = await health_checker.run_all_checks()
        print(f"✅ Health check completed: {health_status.status.value}")
        
        print("\n🎉 Basic monitoring test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Basic monitoring test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_basic_monitoring())
    exit(0 if success else 1)
