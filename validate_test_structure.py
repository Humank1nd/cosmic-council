"""
Script to validate the new test structure and ensure all tests are properly organized.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_test_structure():
    """Validate the new test structure"""
    new_tests_dir = Path("tests_new")
    
    if not new_tests_dir.exists():
        logger.error("New test directory not found")
        return False
    
    # Expected directory structure
    expected_dirs = [
        "unit",
        "integration", 
        "e2e",
        "performance",
        "mocks",
        "fixtures",
        "unit/core",
        "unit/database",
        "unit/api",
        "unit/agents",
        "unit/agents/supra_enterprise",
        "unit/agents/orchestration",
        "unit/utils",
        "integration/api",
        "integration/agents",
        "integration/database",
        "integration/services",
        "e2e/workflows",
        "e2e/agents",
        "e2e/api",
        "performance/load",
        "performance/stress",
        "mocks/data",
        "mocks/factories",
        "fixtures/database",
        "fixtures/api",
        "fixtures/agents"
    ]
    
    missing_dirs = []
    for expected_dir in expected_dirs:
        dir_path = new_tests_dir / expected_dir
        if not dir_path.exists():
            missing_dirs.append(expected_dir)
    
    if missing_dirs:
        logger.warning(f"Missing directories: {missing_dirs}")
    else:
        logger.info("✅ All expected directories exist")
    
    return len(missing_dirs) == 0

def count_test_files():
    """Count test files in the new structure"""
    new_tests_dir = Path("tests_new")
    
    test_files = []
    for root, dirs, files in os.walk(new_tests_dir):
        for file in files:
            if file.endswith('.py') and (file.startswith('test_') or file == 'conftest.py'):
                test_files.append(Path(root) / file)
    
    # Group by category
    categories = {
        'unit': [],
        'integration': [],
        'e2e': [],
        'performance': [],
        'mocks': [],
        'fixtures': [],
        'config': []
    }
    
    for test_file in test_files:
        relative_path = test_file.relative_to(new_tests_dir)
        path_str = str(relative_path)
        
        if 'unit/' in path_str:
            categories['unit'].append(test_file)
        elif 'integration/' in path_str:
            categories['integration'].append(test_file)
        elif 'e2e/' in path_str:
            categories['e2e'].append(test_file)
        elif 'performance/' in path_str:
            categories['performance'].append(test_file)
        elif 'mocks/' in path_str:
            categories['mocks'].append(test_file)
        elif 'fixtures/' in path_str:
            categories['fixtures'].append(test_file)
        elif test_file.name in ['conftest.py', 'pytest.ini', 'run_tests.py']:
            categories['config'].append(test_file)
    
    return categories

def validate_test_imports():
    """Validate that test files have correct imports"""
    new_tests_dir = Path("tests_new")
    
    test_files = []
    for root, dirs, files in os.walk(new_tests_dir):
        for file in files:
            if file.endswith('.py') and file.startswith('test_'):
                test_files.append(Path(root) / file)
    
    import_issues = []
    
    for test_file in test_files:
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for old import patterns
            problematic_patterns = [
                'from src.cosmic_council',
                'from cosmic_council',
                'from enhanced_cosmic_council',
                'from unified_ai_agent_system import',
                'from problem_solving_workflow import'
            ]
            
            for pattern in problematic_patterns:
                if pattern in content:
                    import_issues.append(f"{test_file}: {pattern}")
        
        except Exception as e:
            import_issues.append(f"{test_file}: Error reading file - {e}")
    
    return import_issues

def create_test_summary():
    """Create a comprehensive test summary"""
    new_tests_dir = Path("tests_new")
    
    # Validate structure
    structure_valid = validate_test_structure()
    
    # Count files
    categories = count_test_files()
    
    # Check imports
    import_issues = validate_test_imports()
    
    # Create summary
    summary_file = Path("TEST_STRUCTURE_VALIDATION_SUMMARY.md")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Test Structure Validation Summary\n\n")
        
        f.write(f"**Structure Validation:** {'✅ Valid' if structure_valid else '❌ Issues Found'}\n")
        f.write(f"**Import Issues:** {len(import_issues)}\n\n")
        
        f.write("## Test File Counts\n\n")
        total_files = 0
        for category, files in categories.items():
            count = len(files)
            total_files += count
            f.write(f"- **{category.title()}:** {count} files\n")
        
        f.write(f"\n**Total Test Files:** {total_files}\n\n")
        
        f.write("## Test Structure\n\n")
        f.write("```\n")
        f.write("tests_new/\n")
        f.write("├── unit/                    # Unit tests\n")
        f.write("│   ├── core/               # Core module tests\n")
        f.write("│   │   ├── test_types.py\n")
        f.write("│   │   └── test_services.py\n")
        f.write("│   ├── database/           # Database tests\n")
        f.write("│   │   ├── test_connection.py\n")
        f.write("│   │   └── test_repositories.py\n")
        f.write("│   ├── api/                # API tests\n")
        f.write("│   │   ├── test_routes.py\n")
        f.write("│   │   ├── test_problems.py\n")
        f.write("│   │   ├── test_cycles.py\n")
        f.write("│   │   └── test_solutions.py\n")
        f.write("│   ├── agents/             # Agent tests\n")
        f.write("│   │   ├── test_supra_enterprise/\n")
        f.write("│   │   │   ├── test_red_owl.py\n")
        f.write("│   │   │   ├── test_orange_orangutan.py\n")
        f.write("│   │   │   ├── test_yellow_honeybee.py\n")
        f.write("│   │   │   ├── test_green_tortoise.py\n")
        f.write("│   │   │   ├── test_blue_dolphin.py\n")
        f.write("│   │   │   └── test_purple_elephant.py\n")
        f.write("│   │   └── orchestration/\n")
        f.write("│   │       └── test_coordinator.py\n")
        f.write("│   └── utils/              # Utility tests\n")
        f.write("│       ├── test_logging.py\n")
        f.write("│       ├── test_config.py\n")
        f.write("│       ├── test_validation.py\n")
        f.write("│       └── test_helpers.py\n")
        f.write("├── integration/            # Integration tests\n")
        f.write("│   ├── api/\n")
        f.write("│   │   └── test_endpoints.py\n")
        f.write("│   ├── agents/\n")
        f.write("│   │   └── test_handoff.py\n")
        f.write("│   └── database/\n")
        f.write("│       └── test_repositories.py\n")
        f.write("├── e2e/                    # End-to-end tests\n")
        f.write("│   ├── workflows/\n")
        f.write("│   │   └── test_complete.py\n")
        f.write("│   └── api/\n")
        f.write("│       └── test_complete_api_flow.py\n")
        f.write("├── performance/            # Performance tests\n")
        f.write("│   ├── load/\n")
        f.write("│   │   └── test_load.py\n")
        f.write("│   └── stress/\n")
        f.write("│       └── test_stress.py\n")
        f.write("├── mocks/                  # Mock data and objects\n")
        f.write("│   └── data/\n")
        f.write("│       └── sample_problems.py\n")
        f.write("├── fixtures/               # Test fixtures\n")
        f.write("│   └── database/\n")
        f.write("│       └── test_data.py\n")
        f.write("├── conftest.py             # Pytest configuration\n")
        f.write("├── pytest.ini              # Pytest settings\n")
        f.write("└── run_tests.py            # Test runner\n")
        f.write("```\n\n")
        
        if import_issues:
            f.write("## Import Issues Found\n\n")
            for issue in import_issues:
                f.write(f"- {issue}\n")
            f.write("\n")
        
        f.write("## Test Categories\n\n")
        for category, files in categories.items():
            if files:
                f.write(f"### {category.title()} Tests ({len(files)} files)\n\n")
                for file in files:
                    relative_path = file.relative_to(new_tests_dir)
                    f.write(f"- `{relative_path}`\n")
                f.write("\n")
        
        f.write("## Running Tests\n\n")
        f.write("### Run All Tests\n")
        f.write("```bash\n")
        f.write("cd tests_new\n")
        f.write("python run_tests.py --type all --verbose\n")
        f.write("```\n\n")
        
        f.write("### Run Specific Test Types\n")
        f.write("```bash\n")
        f.write("# Unit tests only\n")
        f.write("python run_tests.py --type unit\n\n")
        f.write("# Integration tests only\n")
        f.write("python run_tests.py --type integration\n\n")
        f.write("# E2E tests only\n")
        f.write("python run_tests.py --type e2e\n\n")
        f.write("# Performance tests only\n")
        f.write("python run_tests.py --type performance\n")
        f.write("```\n\n")
        
        f.write("### Run with Coverage\n")
        f.write("```bash\n")
        f.write("python run_tests.py --type all --coverage\n")
        f.write("```\n\n")
        
        f.write("### Run Specific Test File\n")
        f.write("```bash\n")
        f.write("python run_tests.py --specific unit/core/test_types.py\n")
        f.write("```\n\n")
        
        f.write("## Next Steps\n\n")
        f.write("1. **Review the test structure** - Ensure all tests are properly organized\n")
        f.write("2. **Fix import issues** - Update any remaining old import patterns\n")
        f.write("3. **Run tests** - Execute the test suite to ensure everything works\n")
        f.write("4. **Add more tests** - Expand test coverage as needed\n")
        f.write("5. **Set up CI/CD** - Integrate tests into continuous integration\n")
    
    logger.info(f"Test validation summary written to {summary_file}")
    
    return {
        'structure_valid': structure_valid,
        'total_files': sum(len(files) for files in categories.values()),
        'import_issues': len(import_issues),
        'categories': categories
    }

def main():
    """Main validation function"""
    logger.info("Starting test structure validation...")
    
    # Create summary
    results = create_test_summary()
    
    logger.info("Test structure validation completed!")
    logger.info(f"Total test files: {results['total_files']}")
    logger.info(f"Structure valid: {results['structure_valid']}")
    logger.info(f"Import issues: {results['import_issues']}")
    
    if results['import_issues'] > 0:
        logger.warning("Some import issues found - check the summary for details")
    else:
        logger.info("✅ No import issues found")

if __name__ == "__main__":
    main()
