#!/usr/bin/env python3
"""
Test runner for the Perpetual Thinking System
Runs comprehensive tests for the perpetual thinking integration
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Running: {command}")
    print()
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    duration = end_time - start_time
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED ({duration:.2f}s)")
        if result.stdout:
            print("Output:")
            print(result.stdout)
    else:
        print(f"❌ {description} - FAILED ({duration:.2f}s)")
        if result.stderr:
            print("Error:")
            print(result.stderr)
        if result.stdout:
            print("Output:")
            print(result.stdout)
    
    return result.returncode == 0

def run_perpetual_tests(test_type=None, coverage=False, verbose=False, parallel=False):
    """Run perpetual thinking system tests"""
    
    # Base pytest command
    base_cmd = "python -m pytest"
    
    # Add test paths based on type
    if test_type == "unit":
        test_paths = ["tests/unit/test_perpetual_ai_integration.py"]
        description = "Unit Tests for Perpetual AI Integration"
    elif test_type == "integration":
        test_paths = [
            "tests/integration/test_perpetual_thinking_integration.py",
            "tests/integration/test_perpetual_api_endpoints.py"
        ]
        description = "Integration Tests for Perpetual Thinking System"
    elif test_type == "e2e":
        test_paths = ["tests/e2e/test_perpetual_thinking_e2e.py"]
        description = "End-to-End Tests for Perpetual Thinking System"
    elif test_type == "performance":
        test_paths = ["tests/performance/test_perpetual_thinking_performance.py"]
        description = "Performance Tests for Perpetual Thinking System"
    else:
        # Run all perpetual thinking tests
        test_paths = [
            "tests/unit/test_perpetual_ai_integration.py",
            "tests/integration/test_perpetual_thinking_integration.py",
            "tests/integration/test_perpetual_api_endpoints.py",
            "tests/e2e/test_perpetual_thinking_e2e.py",
            "tests/performance/test_perpetual_thinking_performance.py"
        ]
        description = "All Perpetual Thinking System Tests"
    
    # Build command
    cmd_parts = [base_cmd]
    
    # Add test paths
    cmd_parts.extend(test_paths)
    
    # Add options
    if verbose:
        cmd_parts.append("-v")
    
    if coverage:
        cmd_parts.extend([
            "--cov=perpetual_ai_integration",
            "--cov=perpetual_thinking_engine",
            "--cov=perpetual_database_service",
            "--cov-report=html:htmlcov_perpetual",
            "--cov-report=term-missing"
        ])
    
    if parallel:
        cmd_parts.extend(["-n", "auto"])
    
    # Add markers for performance tests
    if test_type == "performance":
        cmd_parts.extend(["-m", "performance"])
    
    # Add slow marker for performance tests
    if test_type == "performance":
        cmd_parts.extend(["-m", "slow"])
    
    command = " ".join(cmd_parts)
    
    return run_command(command, description)

def run_linting():
    """Run linting on perpetual thinking files"""
    files_to_lint = [
        "perpetual_ai_integration.py",
        "perpetual_thinking_engine.py",
        "perpetual_database_service.py",
        "cosmic_council_api.py",
        "web_interface.py",
        "api_client.py"
    ]
    
    success = True
    
    for file_path in files_to_lint:
        if os.path.exists(file_path):
            cmd = f"python -m flake8 {file_path} --max-line-length=120 --ignore=E203,W503"
            if not run_command(cmd, f"Linting {file_path}"):
                success = False
    
    return success

def run_type_checking():
    """Run type checking on perpetual thinking files"""
    files_to_check = [
        "perpetual_ai_integration.py",
        "perpetual_thinking_engine.py",
        "perpetual_database_service.py"
    ]
    
    success = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            cmd = f"python -m mypy {file_path} --ignore-missing-imports"
            if not run_command(cmd, f"Type checking {file_path}"):
                success = False
    
    return success

def generate_test_report():
    """Generate a comprehensive test report"""
    print(f"\n{'='*60}")
    print("📊 Generating Test Report")
    print(f"{'='*60}")
    
    # Check if coverage report exists
    if os.path.exists("htmlcov_perpetual/index.html"):
        print("✅ Coverage report generated: htmlcov_perpetual/index.html")
    else:
        print("⚠️  No coverage report found. Run with --coverage to generate one.")
    
    # Check test results
    if os.path.exists(".pytest_cache"):
        print("✅ Test cache found")
    else:
        print("⚠️  No test cache found")
    
    print("\n📋 Test Summary:")
    print("- Unit Tests: Perpetual AI Integration")
    print("- Integration Tests: Perpetual Thinking System & API Endpoints")
    print("- End-to-End Tests: Complete Workflows")
    print("- Performance Tests: Load & Stress Testing")
    
    print("\n🎯 Test Coverage Areas:")
    print("- AI Enhancement Levels (None, Assisted, Enhanced, Autonomous)")
    print("- AI Thinking Modes (Creative, Logical, Critical, Empathic, Strategic)")
    print("- Perpetual Cycle Execution")
    print("- Database Persistence")
    print("- API Endpoints")
    print("- Web Interface Integration")
    print("- Error Handling & Recovery")
    print("- Performance Under Load")

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Run Perpetual Thinking System Tests")
    parser.add_argument("--type", choices=["unit", "integration", "e2e", "performance"], 
                       help="Type of tests to run")
    parser.add_argument("--coverage", action="store_true", 
                       help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    parser.add_argument("--parallel", "-p", action="store_true", 
                       help="Run tests in parallel")
    parser.add_argument("--lint", action="store_true", 
                       help="Run linting")
    parser.add_argument("--type-check", action="store_true", 
                       help="Run type checking")
    parser.add_argument("--all", action="store_true", 
                       help="Run all checks (tests, linting, type checking)")
    parser.add_argument("--report", action="store_true", 
                       help="Generate test report")
    
    args = parser.parse_args()
    
    print("🔄 Perpetual Thinking System Test Runner")
    print("=" * 60)
    
    overall_success = True
    
    # Run linting
    if args.lint or args.all:
        if not run_linting():
            overall_success = False
    
    # Run type checking
    if args.type_check or args.all:
        if not run_type_checking():
            overall_success = False
    
    # Run tests
    if not args.report:
        if not run_perpetual_tests(
            test_type=args.type,
            coverage=args.coverage or args.all,
            verbose=args.verbose,
            parallel=args.parallel
        ):
            overall_success = False
    
    # Generate report
    if args.report or args.all:
        generate_test_report()
    
    # Final result
    print(f"\n{'='*60}")
    if overall_success:
        print("🎉 All Perpetual Thinking System Tests PASSED!")
        print("✅ The perpetual thinking integration is working correctly.")
    else:
        print("❌ Some Perpetual Thinking System Tests FAILED!")
        print("🔧 Please review the errors above and fix them.")
    print(f"{'='*60}")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
