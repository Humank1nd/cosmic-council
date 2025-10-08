#!/usr/bin/env python3
"""
Test script for Phase 2 improvements
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_config_system():
    """Test the configuration system."""
    print("🧪 Testing Configuration System...")
    try:
        from cosmic_council.config import get_config, CosmicCouncilConfig
        config = get_config()
        print(f"✅ Config loaded: {config.app_name} v{config.app_version}")
        print(f"✅ Environment: {config.environment}")
        print(f"✅ AI Provider: {config.ai.provider.value}")
        print(f"✅ Database: {config.database.db_path}")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_database_system():
    """Test the production database system."""
    print("\n🧪 Testing Production Database System...")
    try:
        from cosmic_council.database_improved import ProductionDatabase, DatabaseConfig
        from cosmic_council.config import get_config
        
        config = get_config()
        db_config = DatabaseConfig(
            db_path="test_production.db",
            pool_size=5,
            timeout=10.0
        )
        
        db = ProductionDatabase(db_config)
        
        # Test saving a problem
        problem_id = db.save_problem("Test problem for Phase 2")
        print(f"✅ Problem saved with ID: {problem_id}")
        
        # Test saving a solution
        solution_id = db.save_solution(problem_id, "Test Enterprise", "Test solution", confidence=0.9)
        print(f"✅ Solution saved with ID: {solution_id}")
        
        # Test getting stats
        stats = db.get_database_stats()
        print(f"✅ Database stats: {stats['problems']} problems, {stats['solutions']} solutions")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_logging_system():
    """Test the logging system."""
    print("\n🧪 Testing Logging System...")
    try:
        from cosmic_council.logging_config import setup_logging, get_logger
        from cosmic_council.config import get_config
        
        config = get_config()
        loggers = setup_logging(config.logging)
        
        app_logger = loggers['app']
        app_logger.info("Test log message from Phase 2")
        app_logger.log_performance_metric("test_metric", 123.45, "ms")
        
        print("✅ Logging system working")
        return True
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        return False

def test_api_models():
    """Test the API models."""
    print("\n🧪 Testing API Models...")
    try:
        from cosmic_council.api import ProblemRequest, SolutionResponse, ProblemResponse
        
        # Test ProblemRequest
        request = ProblemRequest(
            problem="Test problem",
            domain="testing",
            complexity="medium"
        )
        print(f"✅ ProblemRequest created: {request.problem}")
        
        # Test SolutionResponse
        solution = SolutionResponse(
            enterprise="Test Enterprise",
            solution="Test solution",
            confidence=0.9,
            processing_time=1.0
        )
        print(f"✅ SolutionResponse created: {solution.enterprise}")
        
        print("✅ API models working")
        return True
    except Exception as e:
        print(f"❌ API models test failed: {e}")
        return False

def test_core_system():
    """Test the core system with production components."""
    print("\n🧪 Testing Core System with Production Components...")
    try:
        from cosmic_council import CosmicCouncilMVP
        
        council = CosmicCouncilMVP()
        print("✅ Cosmic Council MVP initialized")
        
        # Test solving a simple problem
        results = council.solve_problem_sync("How do I test Phase 2?")
        print(f"✅ Problem solved with {len(results)} enterprise responses")
        
        for enterprise, response in results.items():
            print(f"  - {enterprise}: {len(response)} characters")
        
        return True
    except Exception as e:
        print(f"❌ Core system test failed: {e}")
        return False

def main():
    """Run all Phase 2 tests."""
    print("🚀 Phase 2 Testing Suite")
    print("=" * 50)
    
    tests = [
        test_config_system,
        test_database_system,
        test_logging_system,
        test_api_models,
        test_core_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 2 tests passed! Production system is ready!")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
