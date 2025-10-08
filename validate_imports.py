"""
Script to validate that all imports are working correctly after the refactoring.
"""

import ast
import sys
import os
import logging
from pathlib import Path
from typing import List, Dict, Set

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to Python path for validation
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in the directory"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = {'__pycache__', '.git', '.pytest_cache', 'node_modules', '.venv', 'database_backup'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('.'):
                python_files.append(Path(root) / file)
    
    return python_files

def validate_imports_in_file(file_path: Path) -> List[str]:
    """Validate imports in a single file"""
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file to check for syntax errors
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            errors.append(f"Syntax error: {e}")
            return errors
        
        # Check for problematic import patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    if 'cosmic_council' in module_name and 'src.cosmic_council' not in module_name:
                        errors.append(f"Old import pattern found: {module_name}")
            
            elif isinstance(node, ast.ImportFrom):
                if node.module and 'cosmic_council' in node.module and 'src.cosmic_council' not in node.module:
                    errors.append(f"Old import pattern found: from {node.module}")
        
        # Check for specific problematic imports
        problematic_patterns = [
            'from cosmic_council',
            'import cosmic_council',
            'from src.cosmic_council.core.core import',
            'from src.cosmic_council.database.unified_database_service import',
            'from shared.utils.database import get_database_manager',
            'from shared.logging.logger import get_enterprise_logger'
        ]
        
        for pattern in problematic_patterns:
            if pattern in content:
                errors.append(f"Problematic import pattern found: {pattern}")
        
    except Exception as e:
        errors.append(f"Error reading file: {e}")
    
    return errors

def validate_imports_in_directory(directory: Path) -> Dict[str, List[str]]:
    """Validate imports in all Python files in a directory"""
    python_files = find_python_files(directory)
    all_errors = {}
    
    logger.info(f"Validating imports in {len(python_files)} Python files in {directory}")
    
    for file_path in python_files:
        errors = validate_imports_in_file(file_path)
        if errors:
            all_errors[str(file_path)] = errors
    
    return all_errors

def create_import_fix_recommendations():
    """Create recommendations for fixing common import issues"""
    recommendations = """
# Import Fix Recommendations

## Common Issues and Solutions

### 1. Old cosmic_council imports
**Problem:** `from cosmic_council.core.core import ProblemStatement`
**Solution:** `from src.core.types import ProblemStatement`

### 2. Database manager imports
**Problem:** `from shared.utils.database import get_database_manager`
**Solution:** `from src.database.connection import get_database_connection`

### 3. Logger imports
**Problem:** `from shared.logging.logger import get_enterprise_logger`
**Solution:** `from src.utils.logging import get_logger`

### 4. Core service imports
**Problem:** `from src.cosmic_council.core.hexagon import CosmicCouncilHexagon`
**Solution:** `from src.core.services import CosmicCouncilHexagon`

### 5. Agent imports
**Problem:** `from src.cosmic_council.agents.unified_ai_agent_system import UnifiedAIAgentSystem`
**Solution:** `from src.agents.orchestration.coordinator import AgentCoordinator`

## Quick Fix Script
Run this in your Python environment to fix common import issues:

```python
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Now you can import from the new structure
from src.core.types import ProblemStatement, EnterpriseType
from src.database.connection import get_database_connection
from src.utils.logging import get_logger
```

## Testing Imports
To test if your imports work:

```python
try:
    from src.core.types import ProblemStatement
    print("✅ Core types import successful")
except ImportError as e:
    print(f"❌ Core types import failed: {e}")

try:
    from src.database.connection import get_database_connection
    print("✅ Database connection import successful")
except ImportError as e:
    print(f"❌ Database connection import failed: {e}")
```
"""
    
    with open("IMPORT_FIX_RECOMMENDATIONS.md", "w", encoding="utf-8") as f:
        f.write(recommendations)
    
    logger.info("Created IMPORT_FIX_RECOMMENDATIONS.md")

def main():
    """Main function to validate imports throughout the codebase"""
    logger.info("Starting import validation...")
    
    # Directories to validate
    directories_to_validate = [
        Path("services"),
        Path("enterprises"), 
        Path("refinement_engine"),
        Path("tests"),
        Path("scripts"),
        Path("examples"),
        Path("shared"),
        Path("src")
    ]
    
    all_errors = {}
    total_files = 0
    files_with_errors = 0
    
    for directory in directories_to_validate:
        if directory.exists():
            logger.info(f"Validating imports in {directory}")
            errors = validate_imports_in_directory(directory)
            if errors:
                all_errors.update(errors)
                files_with_errors += len(errors)
            
            # Count total files
            python_files = find_python_files(directory)
            total_files += len(python_files)
        else:
            logger.warning(f"Directory {directory} does not exist, skipping")
    
    # Create recommendations
    create_import_fix_recommendations()
    
    # Report results
    logger.info(f"Import validation completed!")
    logger.info(f"Total files checked: {total_files}")
    logger.info(f"Files with import issues: {files_with_errors}")
    
    if all_errors:
        logger.warning("Import issues found:")
        for file_path, errors in all_errors.items():
            logger.warning(f"  {file_path}:")
            for error in errors:
                logger.warning(f"    - {error}")
    else:
        logger.info("✅ No import issues found!")
    
    # Create detailed validation report
    report_file = Path("IMPORT_VALIDATION_REPORT.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Import Validation Report\n\n")
        f.write(f"**Total files checked:** {total_files}\n")
        f.write(f"**Files with import issues:** {files_with_errors}\n\n")
        
        if all_errors:
            f.write("## Import Issues Found\n\n")
            for file_path, errors in all_errors.items():
                f.write(f"### {file_path}\n\n")
                for error in errors:
                    f.write(f"- {error}\n")
                f.write("\n")
        else:
            f.write("## ✅ No Import Issues Found\n\n")
            f.write("All imports are correctly updated to the new modular structure.\n")
        
        f.write("\n## Next Steps\n\n")
        if all_errors:
            f.write("1. Fix the import issues listed above\n")
            f.write("2. Run this validation script again\n")
            f.write("3. Test the application to ensure all imports work\n")
        else:
            f.write("1. Run tests to ensure all functionality works\n")
            f.write("2. Deploy the updated application\n")
            f.write("3. Monitor for any runtime import errors\n")
    
    logger.info(f"Validation report written to {report_file}")

if __name__ == "__main__":
    main()
