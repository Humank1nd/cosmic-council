#!/usr/bin/env python3
"""
Codex-Enhanced Test Runner for Cosmic Council Framework
Integrates Codex for intelligent test generation and optimization
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

class CodexTestRunner:
    """Enhanced test runner with Codex integration."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.codex_config = self._load_codex_config()
        self.test_results = {}
    
    def _load_codex_config(self) -> Dict[str, Any]:
        """Load Codex configuration."""
        config_file = self.project_root / ".codex" / "config.toml"
        if config_file.exists():
            # Simple TOML parsing for basic config
            config = {}
            with open(config_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key.strip()] = value.strip().strip('"')
            return config
        return {}
    
    async def run_codex_command(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Run a Codex command and return the result."""
        cmd = ["codex", "exec"]
        
        # Add configuration options
        if "approval_policy" in kwargs:
            cmd.extend(["--approval-policy", kwargs["approval_policy"]])
        if "sandbox" in kwargs:
            cmd.extend(["--sandbox", kwargs["sandbox"]])
        if "model" in kwargs:
            cmd.extend(["--model", kwargs["model"]])
        if "cwd" in kwargs:
            cmd.extend(["--cwd", kwargs["cwd"]])
        
        cmd.append(prompt)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600  # 10 minute timeout
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": " ".join(cmd)
            }
        except subprocess.TimeoutExpired:
            return {"error": "Codex execution timed out after 10 minutes"}
        except Exception as e:
            return {"error": f"Error executing Codex: {str(e)}"}
    
    async def analyze_test_coverage(self) -> Dict[str, Any]:
        """Analyze current test coverage using Codex."""
        console.print("\n[blue]🔍 Analyzing test coverage with Codex...[/blue]")
        
        prompt = """
        Analyze the test coverage for the Cosmic Council Framework:
        
        1. Run pytest with coverage to get current coverage metrics
        2. Identify files and functions with low coverage
        3. Analyze the existing test structure in tests/ directory
        4. Identify critical code paths that need more testing
        5. Suggest specific test cases to improve coverage
        6. Check for missing edge cases and error conditions
        
        Provide a detailed analysis with specific recommendations.
        """
        
        result = await self.run_codex_command(
            prompt,
            approval_policy="on-failure",
            sandbox="workspace-write"
        )
        
        return result
    
    async def generate_missing_tests(self, target_files: List[str] = None) -> Dict[str, Any]:
        """Generate tests for files with missing coverage."""
        console.print("\n[green]🧪 Generating missing tests with Codex...[/green]")
        
        if target_files:
            files_str = ", ".join(target_files)
            prompt = f"""
            Generate comprehensive tests for the following files: {files_str}
            
            Requirements:
            - Follow the existing test patterns in tests/ directory
            - Use pytest framework
            - Include unit tests, integration tests, and edge cases
            - Add proper fixtures and mocks
            - Ensure good test coverage
            - Follow Cosmic Council testing standards
            - Add docstrings to test functions
            - Use descriptive test names
            - Test both success and failure scenarios
            
            Create test files in the appropriate tests/ subdirectory.
            """
        else:
            prompt = """
            Analyze the codebase and generate tests for files with missing or insufficient test coverage:
            
            1. Identify files in src/ that need more tests
            2. Generate comprehensive test suites
            3. Focus on critical business logic and API endpoints
            4. Include edge cases and error conditions
            5. Follow the existing test patterns and structure
            6. Ensure tests are maintainable and well-documented
            
            Create test files in the appropriate tests/ subdirectory.
            """
        
        result = await self.run_codex_command(
            prompt,
            approval_policy="on-failure",
            sandbox="workspace-write"
        )
        
        return result
    
    async def optimize_test_performance(self) -> Dict[str, Any]:
        """Optimize test performance using Codex."""
        console.print("\n[yellow]⚡ Optimizing test performance with Codex...[/yellow]")
        
        prompt = """
        Analyze and optimize the test suite performance for the Cosmic Council Framework:
        
        1. Identify slow-running tests
        2. Analyze test dependencies and fixtures
        3. Suggest parallel test execution opportunities
        4. Optimize database setup and teardown
        5. Improve test isolation and independence
        6. Suggest caching strategies for expensive operations
        7. Identify tests that can be run in parallel
        8. Optimize test data generation and cleanup
        
        Provide specific recommendations and implement optimizations.
        """
        
        result = await self.run_codex_command(
            prompt,
            approval_policy="on-failure",
            sandbox="workspace-write"
        )
        
        return result
    
    async def generate_test_data(self) -> Dict[str, Any]:
        """Generate comprehensive test data using Codex."""
        console.print("\n[purple]📊 Generating test data with Codex...[/purple]")
        
        prompt = """
        Generate comprehensive test data for the Cosmic Council Framework:
        
        1. Create realistic test fixtures for all models
        2. Generate test data for different scenarios (success, failure, edge cases)
        3. Create factory classes for test data generation
        4. Ensure test data covers all business logic paths
        5. Create test data for API endpoints
        6. Generate test data for database operations
        7. Create mock data for external integrations
        8. Ensure test data is consistent and maintainable
        
        Use factory-boy and faker libraries where appropriate.
        Create fixtures in tests/fixtures/ directory.
        """
        
        result = await self.run_codex_command(
            prompt,
            approval_policy="on-failure",
            sandbox="workspace-write"
        )
        
        return result
    
    async def run_intelligent_tests(self, test_type: str = "all") -> Dict[str, Any]:
        """Run tests with intelligent analysis and optimization."""
        console.print(f"\n[cyan]🚀 Running intelligent tests ({test_type})...[/cyan]")
        
        # First, analyze what tests to run
        analysis_prompt = f"""
        Analyze the current state of the Cosmic Council codebase and determine the optimal test strategy:
        
        1. Identify which tests should be run based on recent changes
        2. Determine the most efficient test execution order
        3. Identify tests that can be skipped or run in parallel
        4. Check for test dependencies and conflicts
        5. Suggest test execution optimizations
        
        Focus on {test_type} tests and provide a test execution plan.
        """
        
        analysis_result = await self.run_codex_command(
            analysis_prompt,
            approval_policy="never",
            sandbox="read-only"
        )
        
        # Then run the optimized test suite
        test_prompt = f"""
        Execute the optimized test suite for the Cosmic Council Framework:
        
        1. Run the test execution plan from the analysis
        2. Use pytest with appropriate flags for {test_type} tests
        3. Generate detailed test reports
        4. Capture performance metrics
        5. Identify and report any test failures
        6. Provide recommendations for failed tests
        
        Ensure comprehensive test execution with detailed reporting.
        """
        
        test_result = await self.run_codex_command(
            test_prompt,
            approval_policy="on-failure",
            sandbox="workspace-write"
        )
        
        return {
            "analysis": analysis_result,
            "execution": test_result
        }
    
    def display_results(self, results: Dict[str, Any]):
        """Display test results in a formatted table."""
        table = Table(title="Codex Test Runner Results")
        table.add_column("Operation", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="white")
        
        for operation, result in results.items():
            if isinstance(result, dict):
                if "error" in result:
                    status = "❌ Error"
                    details = result["error"]
                elif result.get("returncode", 0) == 0:
                    status = "✅ Success"
                    details = "Completed successfully"
                else:
                    status = "⚠️ Warning"
                    details = f"Exit code: {result.get('returncode', 'unknown')}"
            else:
                status = "✅ Success"
                details = "Completed successfully"
            
            table.add_row(operation, status, details)
        
        console.print(table)
    
    async def run_full_analysis(self) -> Dict[str, Any]:
        """Run a complete test analysis and optimization."""
        console.print("\n[bold blue]🔬 Running Full Codex Test Analysis[/bold blue]")
        
        results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Coverage analysis
            task1 = progress.add_task("Analyzing test coverage...", total=None)
            results["coverage_analysis"] = await self.analyze_test_coverage()
            progress.update(task1, completed=True)
            
            # Generate missing tests
            task2 = progress.add_task("Generating missing tests...", total=None)
            results["test_generation"] = await self.generate_missing_tests()
            progress.update(task2, completed=True)
            
            # Optimize performance
            task3 = progress.add_task("Optimizing test performance...", total=None)
            results["performance_optimization"] = await self.optimize_test_performance()
            progress.update(task3, completed=True)
            
            # Generate test data
            task4 = progress.add_task("Generating test data...", total=None)
            results["test_data_generation"] = await self.generate_test_data()
            progress.update(task4, completed=True)
            
            # Run intelligent tests
            task5 = progress.add_task("Running intelligent tests...", total=None)
            results["intelligent_testing"] = await self.run_intelligent_tests()
            progress.update(task5, completed=True)
        
        return results

@click.command()
@click.option("--action", "-a", 
              type=click.Choice(["analyze", "generate", "optimize", "data", "run", "full"]),
              default="full", help="Action to perform")
@click.option("--files", "-f", multiple=True, help="Specific files to target")
@click.option("--test-type", "-t", 
              type=click.Choice(["unit", "integration", "e2e", "all"]),
              default="all", help="Type of tests to focus on")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def main(action: str, files: List[str], test_type: str, verbose: bool):
    """Codex-Enhanced Test Runner for Cosmic Council Framework."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    project_root = Path(__file__).parent.parent
    runner = CodexTestRunner(project_root)
    
    async def run_action():
        if action == "analyze":
            results = {"coverage_analysis": await runner.analyze_test_coverage()}
        elif action == "generate":
            results = {"test_generation": await runner.generate_missing_tests(list(files))}
        elif action == "optimize":
            results = {"performance_optimization": await runner.optimize_test_performance()}
        elif action == "data":
            results = {"test_data_generation": await runner.generate_test_data()}
        elif action == "run":
            results = {"intelligent_testing": await runner.run_intelligent_tests(test_type)}
        elif action == "full":
            results = await runner.run_full_analysis()
        
        runner.display_results(results)
        
        # Save results to file
        results_file = project_root / "codex_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        console.print(f"\n[green]Results saved to: {results_file}[/green]")
    
    asyncio.run(run_action())

if __name__ == "__main__":
    main()
