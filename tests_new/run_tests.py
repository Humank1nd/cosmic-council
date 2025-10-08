"""
Comprehensive test runner for the Cosmic Council system.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests with specified options."""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test path
    cmd.append("tests_new/")
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add coverage
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    # Add test type filtering
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "e2e":
        cmd.extend(["-m", "e2e"])
    elif test_type == "performance":
        cmd.extend(["-m", "performance"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    
    # Add other options
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False


def run_specific_tests(test_path):
    """Run specific test file or directory."""
    cmd = ["python", "-m", "pytest", test_path, "-v"]
    
    print(f"Running specific tests: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ Tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False


def main():
    """Main test runner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cosmic Council Test Runner")
    parser.add_argument("--type", choices=["all", "unit", "integration", "e2e", "performance", "fast"],
                       default="all", help="Type of tests to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Run with coverage")
    parser.add_argument("--specific", "-s", help="Run specific test file or directory")
    
    args = parser.parse_args()
    
    if args.specific:
        success = run_specific_tests(args.specific)
    else:
        success = run_tests(args.type, args.verbose, args.coverage)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
