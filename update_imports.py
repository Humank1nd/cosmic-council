"""
Script to update all import statements throughout the codebase to reflect the new modular structure.
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import mapping from old structure to new structure
IMPORT_MAPPINGS = {
    # Core imports
    'src.cosmic_council.core.core': 'src.core.types',
    'src.cosmic_council.core.models': 'src.database.models',
    'src.cosmic_council.core.api': 'src.api.main',
    'src.cosmic_council.core.hexagon': 'src.core.services',
    
    # Database imports
    'src.cosmic_council.database.unified_database_service': 'src.database.database_service',
    'src.cosmic_council.database.unified_database_manager': 'src.database.connection',
    
    # Agent imports
    'src.cosmic_council.agents.unified_ai_agent_system': 'src.agents.orchestration.coordinator',
    'src.cosmic_council.agents.red_owl_agent': 'src.agents.supra_enterprise.red_owl',
    'src.cosmic_council.agents.orange_orangutan_agent': 'src.agents.supra_enterprise.orange_orangutan',
    'src.cosmic_council.agents.yellow_honeybee_agent': 'src.agents.supra_enterprise.yellow_honeybee',
    'src.cosmic_council.agents.green_tortoise_agent': 'src.agents.supra_enterprise.green_tortoise',
    'src.cosmic_council.agents.blue_dolphin_agent': 'src.agents.supra_enterprise.blue_dolphin',
    'src.cosmic_council.agents.purple_elephant_agent': 'src.agents.supra_enterprise.purple_elephant',
    
    # Workflow imports
    'src.cosmic_council.workflows.unified_workflow_engine': 'src.core.services',
    'src.cosmic_council.workflows.roygbv_workflow': 'src.core.services',
    
    # Integration imports
    'src.cosmic_council.integrations.unified_fractal_system': 'src.core.services',
    
    # Utility imports
    'src.cosmic_council.utils.performance_monitoring': 'src.utils.monitoring',
    'src.cosmic_council.utils.error_handling': 'src.utils.error_handling',
    'src.cosmic_council.utils.validation': 'src.utils.validation',
    'src.cosmic_council.utils.helpers': 'src.utils.helpers',
    'src.cosmic_council.utils.logging': 'src.utils.logging',
    'src.cosmic_council.utils.config': 'src.utils.config',
}

# Specific class/function mappings
CLASS_MAPPINGS = {
    # Core types
    'ProblemStatement': 'ProblemStatement',
    'ProblemComplexity': 'ProblemComplexity', 
    'EnterpriseType': 'EnterpriseType',
    'CycleStatus': 'CycleStatus',
    'CosmicCouncilRule': 'CosmicCouncilRule',
    
    # Database classes
    'UnifiedDatabaseService': 'DatabaseService',
    'UnifiedDatabaseManager': 'DatabaseConnection',
    
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
    
    # Utility classes
    'PerformanceMonitor': 'PerformanceMonitor',
    'ErrorHandler': 'ErrorHandler',
    'Validator': 'Validator',
    'Helper': 'Helper',
    'Logger': 'Logger',
    'Config': 'Config',
}

def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in the directory"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = {'__pycache__', '.git', '.pytest_cache', 'node_modules', '.venv'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return python_files

def update_imports_in_file(file_path: Path) -> bool:
    """Update imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        updated = False
        
        # Update import statements
        for old_import, new_import in IMPORT_MAPPINGS.items():
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
        
        # Update class references in imports
        for old_class, new_class in CLASS_MAPPINGS.items():
            if old_class != new_class:
                # Update in from imports
                from_import_pattern = rf'from\s+([^\s]+)\s+import\s+([^,\n]*{re.escape(old_class)}[^,\n]*)'
                def replace_from_import(match):
                    module = match.group(1)
                    imports = match.group(2)
                    new_imports = imports.replace(old_class, new_class)
                    return f'from {module} import {new_imports}'
                
                if re.search(from_import_pattern, content):
                    content = re.sub(from_import_pattern, replace_from_import, content)
                    updated = True
                    logger.info(f"Updated class import in {file_path}: {old_class} -> {new_class}")
        
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

def main():
    """Main function to update imports throughout the codebase"""
    logger.info("Starting import statement updates...")
    
    # Directories to update
    directories_to_update = [
        Path("services"),
        Path("enterprises"), 
        Path("refinement_engine"),
        Path("tests"),
        Path("scripts"),
        Path("examples"),
        Path("shared"),
        Path("src")
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
    
    logger.info(f"Import update completed!")
    logger.info(f"Total files updated: {total_updated}/{total_files}")
    
    # Create a summary of changes
    summary_file = Path("IMPORT_UPDATE_SUMMARY.md")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Import Statement Update Summary\n\n")
        f.write(f"**Total files processed:** {total_files}\n")
        f.write(f"**Total files updated:** {total_updated}\n\n")
        f.write("## Import Mappings Applied\n\n")
        f.write("| Old Import | New Import |\n")
        f.write("|------------|------------|\n")
        for old, new in IMPORT_MAPPINGS.items():
            f.write(f"| `{old}` | `{new}` |\n")
        f.write("\n## Class Mappings Applied\n\n")
        f.write("| Old Class | New Class |\n")
        f.write("|-----------|----------|\n")
        for old, new in CLASS_MAPPINGS.items():
            f.write(f"| `{old}` | `{new}` |\n")
    
    logger.info(f"Summary written to {summary_file}")

if __name__ == "__main__":
    main()
