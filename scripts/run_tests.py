#!/usr/bin/env python3
"""
Comprehensive test runner for the Cosmic Council Framework
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_command(command: List[str], cwd: str = None) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(
        command,
        cwd=cwd or project_root,
        capture_output=True,
        text=True
    )
    return result

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-xdist",
        "httpx",
        "fastapi",
        "uvicorn"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies are installed")
    return True

def run_unit_tests(verbose: bool = False, coverage: bool = False) -> bool:
    """Run unit tests."""
    print("\n🧪 Running unit tests...")
    
    command = ["python", "-m", "pytest", "tests/unit/", "-v" if verbose else "-q"]
    
    if coverage:
        command.extend(["--cov=src", "--cov-report=html", "--cov-report=term-missing"])
    
    result = run_command(command)
    
    if result.returncode == 0:
        print("✅ Unit tests passed")
        return True
    else:
        print("❌ Unit tests failed")
        print(result.stdout)
        print(result.stderr)
        return False

def run_integration_tests(verbose: bool = False) -> bool:
    """Run integration tests."""
    print("\n🔗 Running integration tests...")
    
    command = ["python", "-m", "pytest", "tests/integration/", "-v" if verbose else "-q"]
    result = run_command(command)
    
    if result.returncode == 0:
        print("✅ Integration tests passed")
        return True
    else:
        print("❌ Integration tests failed")
        print(result.stdout)
        print(result.stderr)
        return False

def run_e2e_tests(verbose: bool = False) -> bool:
    """Run end-to-end tests."""
    print("\n🌐 Running end-to-end tests...")
    
    command = ["python", "-m", "pytest", "tests/e2e/", "-v" if verbose else "-q"]
    result = run_command(command)
    
    if result.returncode == 0:
        print("✅ End-to-end tests passed")
        return True
    else:
        print("❌ End-to-end tests failed")
        print(result.stdout)
        print(result.stderr)
        return False

def run_performance_tests(verbose: bool = False) -> bool:
    """Run performance tests."""
    print("\n⚡ Running performance tests...")
    
    command = ["python", "-m", "pytest", "tests/performance/", "-v" if verbose else "-q"]
    result = run_command(command)
    
    if result.returncode == 0:
        print("✅ Performance tests passed")
        return True
    else:
        print("❌ Performance tests failed")
        print(result.stdout)
        print(result.stderr)
        return False

def run_security_tests(verbose: bool = False) -> bool:
    """Run security tests."""
    print("\n🔒 Running security tests...")
    
    command = ["python", "-m", "pytest", "tests/security/", "-v" if verbose else "-q"]
    result = run_command(command)
    
    if result.returncode == 0:
        print("✅ Security tests passed")
        return True
    else:
        print("❌ Security tests failed")
        print(result.stdout)
        print(result.stderr)
        return False

def run_perpetual_tests(verbose: bool = False) -> bool:
    """Run perpetual thinking system tests."""
    print("\n🔄 Running perpetual thinking system tests...")
    
    perpetual_test_files = [
        "tests/unit/test_perpetual_ai_integration.py",
        "tests/integration/test_perpetual_thinking_integration.py",
        "tests/integration/test_perpetual_api_endpoints.py",
        "tests/e2e/test_perpetual_thinking_e2e.py",
        "tests/performance/test_perpetual_thinking_performance.py"
    ]
    
    command = ["python", "-m", "pytest"] + perpetual_test_files + (["-v"] if verbose else ["-q"])
    result = run_command(command)
    
    if result.returncode == 0:
        print("✅ Perpetual thinking system tests passed")
        return True
    else:
        print("❌ Perpetual thinking system tests failed")
        print(result.stdout)
        print(result.stderr)
        return False

def run_all_tests(verbose: bool = False, coverage: bool = False, parallel: bool = False) -> bool:
    """Run all tests."""
    print("\n🚀 Running all tests...")
    
    command = ["python", "-m", "pytest", "tests/", "-v" if verbose else "-q"]
    
    if coverage:
        command.extend(["--cov=src", "--cov-report=html", "--cov-report=term-missing"])
    
    if parallel:
        command.extend(["-n", "auto"])
    
    result = run_command(command)
    
    if result.returncode == 0:
        print("✅ All tests passed")
        return True
    else:
        print("❌ Some tests failed")
        print(result.stdout)
        print(result.stderr)
        return False

def run_specific_tests(test_path: str, verbose: bool = False) -> bool:
    """Run specific tests."""
    print(f"\n🎯 Running specific tests: {test_path}")
    
    command = ["python", "-m", "pytest", test_path, "-v" if verbose else "-q"]
    result = run_command(command)
    
    if result.returncode == 0:
        print("✅ Specific tests passed")
        return True
    else:
        print("❌ Specific tests failed")
        print(result.stdout)
        print(result.stderr)
        return False

def run_linting() -> bool:
    """Run code linting."""
    print("\n🔍 Running code linting...")
    
    # Run flake8
    flake8_result = run_command(["python", "-m", "flake8", "src/", "tests/"])
    
    # Run black check
    black_result = run_command(["python", "-m", "black", "--check", "src/", "tests/"])
    
    if flake8_result.returncode == 0 and black_result.returncode == 0:
        print("✅ Code linting passed")
        return True
    else:
        print("❌ Code linting failed")
        if flake8_result.returncode != 0:
            print("Flake8 errors:")
            print(flake8_result.stdout)
            print(flake8_result.stderr)
        if black_result.returncode != 0:
            print("Black formatting errors:")
            print(black_result.stdout)
            print(black_result.stderr)
        return False

def run_type_checking() -> bool:
    """Run type checking."""
    print("\n🔍 Running type checking...")
    
    command = ["python", "-m", "mypy", "src/", "tests/"]
    result = run_command(command)
    
    if result.returncode == 0:
        print("✅ Type checking passed")
        return True
    else:
        print("❌ Type checking failed")
        print(result.stdout)
        print(result.stderr)
        return False

def generate_test_report() -> bool:
    """Generate a comprehensive test report."""
    print("\n📊 Generating test report...")
    
    command = [
        "python", "-m", "pytest", "tests/",
        "--html=test_report.html",
        "--self-contained-html",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--junitxml=test_results.xml"
    ]
    
    result = run_command(command)
    
    if result.returncode == 0:
        print("✅ Test report generated")
        print("📄 HTML report: test_report.html")
        print("📄 Coverage report: htmlcov/index.html")
        print("📄 JUnit XML: test_results.xml")
        return True
    else:
        print("❌ Test report generation failed")
        print(result.stdout)
        print(result.stderr)
        return False

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Cosmic Council Framework Test Runner")
    parser.add_argument("--type", choices=["unit", "integration", "e2e", "performance", "security", "perpetual", "all"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--path", help="Specific test path to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Generate coverage report")
    parser.add_argument("--parallel", "-p", action="store_true", help="Run tests in parallel")
    parser.add_argument("--lint", action="store_true", help="Run code linting")
    parser.add_argument("--type-check", action="store_true", help="Run type checking")
    parser.add_argument("--report", action="store_true", help="Generate comprehensive test report")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency check")
    
    args = parser.parse_args()
    
    print("🐘 Cosmic Council Framework Test Runner")
    print("=" * 50)
    
    start_time = time.time()
    
    # Check dependencies
    if not args.skip_deps:
        if not check_dependencies():
            sys.exit(1)
    
    success = True
    
    # Run linting
    if args.lint:
        if not run_linting():
            success = False
    
    # Run type checking
    if args.type_check:
        if not run_type_checking():
            success = False
    
    # Run specific tests
    if args.path:
        if not run_specific_tests(args.path, args.verbose):
            success = False
    else:
        # Run tests by type
        if args.type == "unit":
            if not run_unit_tests(args.verbose, args.coverage):
                success = False
        elif args.type == "integration":
            if not run_integration_tests(args.verbose):
                success = False
        elif args.type == "e2e":
            if not run_e2e_tests(args.verbose):
                success = False
        elif args.type == "performance":
            if not run_performance_tests(args.verbose):
                success = False
        elif args.type == "security":
            if not run_security_tests(args.verbose):
                success = False
        elif args.type == "perpetual":
            if not run_perpetual_tests(args.verbose):
                success = False
        elif args.type == "all":
            if args.quick:
                # Run only unit and integration tests for quick check
                if not run_unit_tests(args.verbose, args.coverage):
                    success = False
                if not run_integration_tests(args.verbose):
                    success = False
            else:
                if not run_all_tests(args.verbose, args.coverage, args.parallel):
                    success = False
    
    # Generate test report
    if args.report:
        if not generate_test_report():
            success = False
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests completed successfully!")
    else:
        print("❌ Some tests failed!")
    
    print(f"⏱️  Total time: {total_time:.2f} seconds")
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
