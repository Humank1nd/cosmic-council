"""
Cosmic Council Refinement Engine - Test Runner
Comprehensive test runner for integration and performance tests.
"""

import os
import sys
import asyncio
import subprocess
import argparse
from typing import List, Optional, Dict, Any
from pathlib import Path
import time
import json
from datetime import datetime, timezone


class TestRunner:
    """Test runner for the refinement engine."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize test runner.
        
        Args:
            config: Test configuration
        """
        self.config = config or self._get_default_config()
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default test configuration."""
        return {
            "test_directory": "refinement_engine",
            "output_directory": "test_results",
            "coverage_report": True,
            "performance_tests": True,
            "integration_tests": True,
            "security_tests": True,
            "parallel_execution": True,
            "verbose_output": True,
            "generate_report": True,
            "cleanup_after_tests": True
        }
    
    def setup_environment(self):
        """Set up test environment."""
        print("Setting up test environment...")
        
        # Set environment variables for testing
        os.environ["TESTING"] = "true"
        os.environ["MOCK_AI_SERVICES"] = "true"
        os.environ["USE_IN_MEMORY_DB"] = "true"
        os.environ["ENABLE_METRICS_SERVER"] = "false"
        os.environ["ENABLE_SENTRY"] = "false"
        os.environ["TEST_JWT_SECRET"] = "test-secret-key-for-testing-only"
        
        # Create output directory
        output_dir = Path(self.config["output_directory"])
        output_dir.mkdir(exist_ok=True)
        
        print("Test environment setup complete.")
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        print("Running integration tests...")
        
        start_time = time.time()
        
        # Run integration tests
        cmd = [
            "python", "-m", "pytest",
            f"{self.config['test_directory']}/integration_tests.py",
            "-v",
            "--tb=short",
            "-m", "integration"
        ]
        
        if self.config["coverage_report"]:
            cmd.extend(["--cov", self.config["test_directory"]])
        
        if self.config["verbose_output"]:
            cmd.append("-s")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        end_time = time.time()
        
        return {
            "test_type": "integration",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": end_time - start_time,
            "success": result.returncode == 0
        }
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests."""
        print("Running performance tests...")
        
        start_time = time.time()
        
        # Run performance tests
        cmd = [
            "python", "-m", "pytest",
            f"{self.config['test_directory']}/performance_tests.py",
            "-v",
            "--tb=short",
            "-m", "performance"
        ]
        
        if self.config["verbose_output"]:
            cmd.append("-s")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        end_time = time.time()
        
        return {
            "test_type": "performance",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": end_time - start_time,
            "success": result.returncode == 0
        }
    
    def run_security_tests(self) -> Dict[str, Any]:
        """Run security tests."""
        print("Running security tests...")
        
        start_time = time.time()
        
        # Run security tests
        cmd = [
            "python", "-m", "pytest",
            f"{self.config['test_directory']}/security_tests.py",
            "-v",
            "--tb=short",
            "-m", "security"
        ]
        
        if self.config["verbose_output"]:
            cmd.append("-s")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        end_time = time.time()
        
        return {
            "test_type": "security",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": end_time - start_time,
            "success": result.returncode == 0
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests."""
        print("Running all tests...")
        
        start_time = time.time()
        
        # Run all tests
        cmd = [
            "python", "-m", "pytest",
            f"{self.config['test_directory']}/",
            "-v",
            "--tb=short"
        ]
        
        if self.config["coverage_report"]:
            cmd.extend(["--cov", self.config["test_directory"]])
        
        if self.config["verbose_output"]:
            cmd.append("-s")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        end_time = time.time()
        
        return {
            "test_type": "all",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": end_time - start_time,
            "success": result.returncode == 0
        }
    
    def run_specific_test(self, test_file: str, test_name: Optional[str] = None) -> Dict[str, Any]:
        """Run a specific test."""
        print(f"Running specific test: {test_file}")
        
        start_time = time.time()
        
        # Build command
        cmd = [
            "python", "-m", "pytest",
            f"{self.config['test_directory']}/{test_file}",
            "-v",
            "--tb=short"
        ]
        
        if test_name:
            cmd.extend(["-k", test_name])
        
        if self.config["verbose_output"]:
            cmd.append("-s")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        end_time = time.time()
        
        return {
            "test_type": "specific",
            "test_file": test_file,
            "test_name": test_name,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": end_time - start_time,
            "success": result.returncode == 0
        }
    
    def generate_test_report(self, results: Dict[str, Any]):
        """Generate test report."""
        if not self.config["generate_report"]:
            return
        
        print("Generating test report...")
        
        # Create report data
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "config": self.config,
            "results": results,
            "summary": self._generate_summary(results)
        }
        
        # Save report
        output_dir = Path(self.config["output_directory"])
        report_file = output_dir / "test_report.json"
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        # Generate HTML report
        html_report = self._generate_html_report(report)
        html_file = output_dir / "test_report.html"
        
        with open(html_file, "w") as f:
            f.write(html_report)
        
        print(f"Test report generated: {report_file}")
        print(f"HTML report generated: {html_file}")
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test summary."""
        total_tests = len(results)
        successful_tests = sum(1 for r in results.values() if r.get("success", False))
        failed_tests = total_tests - successful_tests
        
        total_duration = sum(r.get("duration", 0) for r in results.values())
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "average_duration": total_duration / total_tests if total_tests > 0 else 0
        }
    
    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML test report."""
        summary = report["summary"]
        results = report["results"]
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cosmic Council Refinement Engine - Test Report</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }}
                .summary {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                .summary-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .summary-card h3 {{
                    margin: 0 0 10px 0;
                    color: #333;
                }}
                .summary-card .value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #007bff;
                }}
                .results {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .result-item {{
                    padding: 15px;
                    border-bottom: 1px solid #eee;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                .result-item:last-child {{
                    border-bottom: none;
                }}
                .status {{
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-size: 12px;
                }}
                .status.success {{
                    background-color: #d4edda;
                    color: #155724;
                }}
                .status.failure {{
                    background-color: #f8d7da;
                    color: #721c24;
                }}
                .timestamp {{
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Cosmic Council Refinement Engine</h1>
                    <h2>Test Report</h2>
                    <p class="timestamp">Generated: {report['timestamp']}</p>
                </div>
                
                <div class="summary">
                    <div class="summary-card">
                        <h3>Total Tests</h3>
                        <div class="value">{summary['total_tests']}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Successful</h3>
                        <div class="value" style="color: #28a745;">{summary['successful_tests']}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Failed</h3>
                        <div class="value" style="color: #dc3545;">{summary['failed_tests']}</div>
                    </div>
                    <div class="summary-card">
                        <h3>Success Rate</h3>
                        <div class="value">{summary['success_rate']:.1f}%</div>
                    </div>
                    <div class="summary-card">
                        <h3>Total Duration</h3>
                        <div class="value">{summary['total_duration']:.2f}s</div>
                    </div>
                </div>
                
                <div class="results">
                    <h3>Test Results</h3>
        """
        
        for test_type, result in results.items():
            status_class = "success" if result.get("success", False) else "failure"
            status_text = "PASSED" if result.get("success", False) else "FAILED"
            
            html += f"""
                    <div class="result-item">
                        <div>
                            <strong>{test_type.title()} Tests</strong>
                            <br>
                            <small>Duration: {result.get('duration', 0):.2f} seconds</small>
                        </div>
                        <div>
                            <span class="status {status_class}">{status_text}</span>
                        </div>
                    </div>
            """
        
        html += """
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def cleanup(self):
        """Clean up after tests."""
        if not self.config["cleanup_after_tests"]:
            return
        
        print("Cleaning up test environment...")
        
        # Remove temporary files
        temp_files = [
            "test.db",
            "test.db-journal",
            "chroma_db",
            "test_results"
        ]
        
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                if os.path.isdir(temp_file):
                    import shutil
                    shutil.rmtree(temp_file)
                else:
                    os.remove(temp_file)
        
        print("Cleanup complete.")
    
    def run(self, test_types: List[str] = None) -> Dict[str, Any]:
        """
        Run tests.
        
        Args:
            test_types: List of test types to run
            
        Returns:
            Test results
        """
        if test_types is None:
            test_types = ["integration", "performance", "security"]
        
        print("Starting test execution...")
        self.start_time = time.time()
        
        # Setup environment
        self.setup_environment()
        
        # Run tests
        results = {}
        
        try:
            if "integration" in test_types and self.config["integration_tests"]:
                results["integration"] = self.run_integration_tests()
            
            if "performance" in test_types and self.config["performance_tests"]:
                results["performance"] = self.run_performance_tests()
            
            if "security" in test_types and self.config["security_tests"]:
                results["security"] = self.run_security_tests()
            
            # Generate report
            self.generate_test_report(results)
            
        except Exception as e:
            print(f"Test execution failed: {e}")
            results["error"] = {"error": str(e), "success": False}
        
        finally:
            self.end_time = time.time()
            self.cleanup()
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print test summary."""
        print("\n" + "="*50)
        print("TEST EXECUTION SUMMARY")
        print("="*50)
        
        total_duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        for test_type, result in results.items():
            if test_type == "error":
                print(f"ERROR: {result['error']}")
                continue
            
            status = "PASSED" if result.get("success", False) else "FAILED"
            duration = result.get("duration", 0)
            
            print(f"{test_type.title()} Tests: {status} ({duration:.2f}s)")
        
        print(f"\nTotal execution time: {total_duration:.2f} seconds")
        
        # Overall status
        all_successful = all(r.get("success", False) for r in results.values() if r.get("success") is not None)
        overall_status = "PASSED" if all_successful else "FAILED"
        
        print(f"Overall status: {overall_status}")
        print("="*50)


def main():
    """Main function for test runner."""
    parser = argparse.ArgumentParser(description="Run Cosmic Council Refinement Engine tests")
    parser.add_argument("--test-types", nargs="+", 
                       choices=["integration", "performance", "security", "all"],
                       default=["integration", "performance", "security"],
                       help="Types of tests to run")
    parser.add_argument("--config", type=str, help="Path to test configuration file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--no-cleanup", action="store_true", help="Don't cleanup after tests")
    parser.add_argument("--no-report", action="store_true", help="Don't generate test report")
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config:
        with open(args.config, "r") as f:
            config = json.load(f)
    
    # Update config with command line arguments
    config["verbose_output"] = args.verbose
    config["cleanup_after_tests"] = not args.no_cleanup
    config["generate_report"] = not args.no_report
    
    # Create test runner
    runner = TestRunner(config)
    
    # Run tests
    test_types = args.test_types
    if "all" in test_types:
        test_types = ["integration", "performance", "security"]
    
    results = runner.run(test_types)
    
    # Exit with appropriate code
    all_successful = all(r.get("success", False) for r in results.values() if r.get("success") is not None)
    sys.exit(0 if all_successful else 1)


if __name__ == "__main__":
    main()
