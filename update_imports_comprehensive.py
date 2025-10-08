"""
Comprehensive script to update all import statements throughout the codebase.
This handles more complex import patterns and edge cases.
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Extended import mappings
EXTENDED_IMPORT_MAPPINGS = {
    # Core imports
    'src.cosmic_council.core.core': 'src.core.types',
    'src.cosmic_council.core.models': 'src.database.models',
    'src.cosmic_council.core.api': 'src.api.main',
    'src.cosmic_council.core.hexagon': 'src.core.services',
    'src.cosmic_council.core.workflows': 'src.core.services',
    'src.cosmic_council.core.agents': 'src.agents.orchestration',
    
    # Database imports
    'src.cosmic_council.database.unified_database_service': 'src.database.database_service',
    'src.cosmic_council.database.unified_database_manager': 'src.database.connection',
    'src.cosmic_council.database': 'src.database',
    
    # Agent imports
    'src.cosmic_council.agents.unified_ai_agent_system': 'src.agents.orchestration.coordinator',
    'src.cosmic_council.agents.red_owl_agent': 'src.agents.enterprises.red_owl',
    'src.cosmic_council.agents.orange_orangutan_agent': 'src.agents.enterprises.orange_orangutan',
    'src.cosmic_council.agents.yellow_honeybee_agent': 'src.agents.enterprises.yellow_honeybee',
    'src.cosmic_council.agents.green_tortoise_agent': 'src.agents.enterprises.green_tortoise',
    'src.cosmic_council.agents.blue_dolphin_agent': 'src.agents.enterprises.blue_dolphin',
    'src.cosmic_council.agents.purple_elephant_agent': 'src.agents.enterprises.purple_elephant',
    'src.cosmic_council.agents': 'src.agents',
    
    # Workflow imports
    'src.cosmic_council.workflows.unified_workflow_engine': 'src.core.services',
    'src.cosmic_council.workflows.roygbv_workflow': 'src.core.services',
    'src.cosmic_council.workflows': 'src.core.services',
    
    # Integration imports
    'src.cosmic_council.integrations.unified_fractal_system': 'src.core.services',
    'src.cosmic_council.integrations': 'src.core.services',
    
    # Utility imports
    'src.cosmic_council.utils.performance_monitoring': 'src.utils.monitoring',
    'src.cosmic_council.utils.error_handling': 'src.utils.error_handling',
    'src.cosmic_council.utils.validation': 'src.utils.validation',
    'src.cosmic_council.utils.helpers': 'src.utils.helpers',
    'src.cosmic_council.utils.logging': 'src.utils.logging',
    'src.cosmic_council.utils.config': 'src.utils.config',
    'src.cosmic_council.utils': 'src.utils',
    
    # Shared imports (update to new structure)
    'shared.utils.database': 'src.database.connection',
    'shared.logging.logger': 'src.utils.logging',
    'shared.utils.performance': 'src.utils.monitoring',
    'shared.utils.validation': 'src.utils.validation',
    'shared.utils.helpers': 'src.utils.helpers',
}

# Class and function mappings
CLASS_FUNCTION_MAPPINGS = {
    # Database classes
    'UnifiedDatabaseService': 'DatabaseService',
    'UnifiedDatabaseManager': 'DatabaseConnection',
    'get_database_manager': 'get_database_connection',
    
    # Agent classes
    'UnifiedAIAgentSystem': 'AgentCoordinator',
    'RedOwlAgent': 'RedOwlAgent',
    'OrangeOrangutanAgent': 'OrangeOrangutanAgent',
    'YellowHoneybeeAgent': 'YellowHoneybeeAgent',
    'GreenTortoiseAgent': 'GreenTortoiseAgent',
    'BlueDolphinAgent': 'BlueDolphinAgent',
    'PurpleElephantAgent': 'PurpleElephantAgent',
    
    # Workflow classes
    'UnifiedWorkflowEngine': 'WorkflowService',
    'ROYGBVWorkflow': 'ROYGBVWorkflow',
    
    # Integration classes
    'UnifiedFractalSystem': 'FractalService',
    
    # Utility functions
    'setup_logging': 'setup_logging',
    'get_enterprise_logger': 'get_logger',
    'load_config': 'load_config',
}

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

def update_imports_in_file(file_path: Path) -> bool:
    """Update imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        updated = False
        
        # Update import statements (from imports)
        for old_import, new_import in EXTENDED_IMPORT_MAPPINGS.items():
            # Pattern for from imports
            from_pattern = rf'from\s+{re.escape(old_import)}\s+import'
            if re.search(from_pattern, content):
                content = re.sub(from_pattern, f'from {new_import} import', content)
                updated = True
                logger.info(f"Updated from import in {file_path}: {old_import} -> {new_import}")
            
            # Pattern for direct imports
            import_pattern = rf'import\s+{re.escape(old_import)}'
            if re.search(import_pattern, content):
                content = re.sub(import_pattern, f'import {new_import}', content)
                updated = True
                logger.info(f"Updated import in {file_path}: {old_import} -> {new_import}")
        
        # Update class and function references in imports
        for old_name, new_name in CLASS_FUNCTION_MAPPINGS.items():
            if old_name != new_name:
                # Update in from imports
                from_import_pattern = rf'from\s+([^\s]+)\s+import\s+([^,\n]*{re.escape(old_name)}[^,\n]*)'
                def replace_from_import(match):
                    module = match.group(1)
                    imports = match.group(2)
                    new_imports = imports.replace(old_name, new_name)
                    return f'from {module} import {new_imports}'
                
                if re.search(from_import_pattern, content):
                    content = re.sub(from_import_pattern, replace_from_import, content)
                    updated = True
                    logger.info(f"Updated class/function import in {file_path}: {old_name} -> {new_name}")
        
        # Update sys.path.append statements to point to new structure
        sys_path_pattern = r"sys\.path\.append\(os\.path\.join\(os\.path\.dirname\(__file__\), '\.\.', '\.\.'\)\)"
        if re.search(sys_path_pattern, content):
            # Update to point to src directory
            new_sys_path = "sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))"
            content = re.sub(sys_path_pattern, new_sys_path, content)
            updated = True
            logger.info(f"Updated sys.path in {file_path}")
        
        # Update relative imports that might be broken
        # Look for imports that start with .. and might need updating
        relative_import_pattern = r'from\s+\.\.([^\s]+)\s+import'
        def update_relative_import(match):
            relative_path = match.group(1)
            # If it's importing from cosmic_council, update it
            if 'cosmic_council' in relative_path:
                new_path = relative_path.replace('cosmic_council', 'src')
                return f'from ..{new_path} import'
            return match.group(0)
        
        if re.search(relative_import_pattern, content):
            content = re.sub(relative_import_pattern, update_relative_import, content)
            updated = True
            logger.info(f"Updated relative imports in {file_path}")
        
        # Write back if changes were made
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error updating imports in {file_path}: {e}")
        return False

def update_imports_in_directory(directory: Path) -> Tuple[int, int]:
    """Update imports in all Python files in a directory"""
    python_files = find_python_files(directory)
    updated_count = 0
    total_count = len(python_files)
    
    logger.info(f"Found {total_count} Python files in {directory}")
    
    for file_path in python_files:
        if update_imports_in_file(file_path):
            updated_count += 1
    
    return updated_count, total_count

def create_import_fix_script():
    """Create a script to fix common import issues"""
    fix_script_content = '''"""
Script to fix common import issues after refactoring.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Add current directory to path for relative imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

def fix_imports():
    """Fix common import issues"""
    print("Import paths configured for new structure")
    print(f"Added to sys.path: {src_path}")
    print(f"Added to sys.path: {current_dir}")

if __name__ == "__main__":
    fix_imports()
'''
    
    with open("fix_imports.py", "w", encoding="utf-8") as f:
        f.write(fix_script_content)
    
    logger.info("Created fix_imports.py script")

def main():
    """Main function to update imports throughout the codebase"""
    logger.info("Starting comprehensive import statement updates...")
    
    # Directories to update
    directories_to_update = [
        Path("services"),
        Path("enterprises"), 
        Path("refinement_engine"),
        Path("tests"),
        Path("scripts"),
        Path("examples"),
        Path("shared"),
        Path("src"),
        Path("governance"),
        Path("infrastructure")
    ]
    
    total_updated = 0
    total_files = 0
    
    for directory in directories_to_update:
        if directory.exists():
            logger.info(f"Updating imports in {directory}")
            updated, total = update_imports_in_directory(directory)
            total_updated += updated
            total_files += total
            logger.info(f"Updated {updated}/{total} files in {directory}")
        else:
            logger.warning(f"Directory {directory} does not exist, skipping")
    
    # Create import fix script
    create_import_fix_script()
    
    logger.info(f"Comprehensive import update completed!")
    logger.info(f"Total files updated: {total_updated}/{total_files}")
    
    # Create a detailed summary of changes
    summary_file = Path("COMPREHENSIVE_IMPORT_UPDATE_SUMMARY.md")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Comprehensive Import Statement Update Summary\n\n")
        f.write(f"**Total files processed:** {total_files}\n")
        f.write(f"**Total files updated:** {total_updated}\n\n")
        f.write("## Import Mappings Applied\n\n")
        f.write("| Old Import | New Import |\n")
        f.write("|------------|------------|\n")
        for old, new in EXTENDED_IMPORT_MAPPINGS.items():
            f.write(f"| `{old}` | `{new}` |\n")
        f.write("\n## Class/Function Mappings Applied\n\n")
        f.write("| Old Name | New Name |\n")
        f.write("|----------|----------|\n")
        for old, new in CLASS_FUNCTION_MAPPINGS.items():
            f.write(f"| `{old}` | `{new}` |\n")
        f.write("\n## Additional Fixes Applied\n\n")
        f.write("- Updated `sys.path.append` statements to point to new `src` directory\n")
        f.write("- Fixed relative imports that reference old `cosmic_council` structure\n")
        f.write("- Created `fix_imports.py` script for runtime import path configuration\n")
        f.write("\n## Next Steps\n\n")
        f.write("1. Test the updated imports by running the application\n")
        f.write("2. Fix any remaining import errors manually\n")
        f.write("3. Update any hardcoded paths in configuration files\n")
        f.write("4. Run tests to ensure all imports work correctly\n")
    
    logger.info(f"Detailed summary written to {summary_file}")

if __name__ == "__main__":
    main()
