"""
Script to fix the remaining import issues found during validation.
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Specific mappings for the remaining issues
REMAINING_IMPORT_MAPPINGS = {
    # Test imports
    'enhanced_cosmic_council_core': 'src.core.types',
    'cosmic_council_api': 'src.api.main',
    'cosmic_council_core': 'src.core.types',
    'cosmic_council_simplified': 'src.core.services',
    'parallel_cosmic_council_processor': 'src.core.services',
}

# Problematic patterns to fix
PROBLEMATIC_PATTERNS = [
    (r'from cosmic_council\s+import', 'from src.core.types import'),
    (r'from enhanced_cosmic_council_core\s+import', 'from src.core.types import'),
    (r'from cosmic_council_api\s+import', 'from src.api.main import'),
    (r'from cosmic_council_core\s+import', 'from src.core.types import'),
    (r'from cosmic_council_simplified\s+import', 'from src.core.services import'),
    (r'from parallel_cosmic_council_processor\s+import', 'from src.core.services import'),
    (r'from cosmic_council_simplified\.enterprise\s+import', 'from src.agents.supra_enterprise import'),
]

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

def fix_imports_in_file(file_path: Path) -> bool:
    """Fix imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        updated = False
        
        # Apply problematic pattern fixes
        for pattern, replacement in PROBLEMATIC_PATTERNS:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                updated = True
                logger.info(f"Fixed import pattern in {file_path}: {pattern} -> {replacement}")
        
        # Apply specific import mappings
        for old_import, new_import in REMAINING_IMPORT_MAPPINGS.items():
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
        
        # Write back if changes were made
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error fixing imports in {file_path}: {e}")
        return False

def fix_imports_in_directory(directory: Path) -> Tuple[int, int]:
    """Fix imports in all Python files in a directory"""
    python_files = find_python_files(directory)
    updated_count = 0
    total_count = len(python_files)
    
    logger.info(f"Found {total_count} Python files in {directory}")
    
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            updated_count += 1
    
    return updated_count, total_count

def main():
    """Main function to fix remaining import issues"""
    logger.info("Starting fix for remaining import issues...")
    
    # Directories to fix (focus on tests and src where issues were found)
    directories_to_fix = [
        Path("tests"),
        Path("src")
    ]
    
    total_updated = 0
    total_files = 0
    
    for directory in directories_to_fix:
        if directory.exists():
            logger.info(f"Fixing imports in {directory}")
            updated, total = fix_imports_in_directory(directory)
            total_updated += updated
            total_files += total
            logger.info(f"Updated {updated}/{total} files in {directory}")
        else:
            logger.warning(f"Directory {directory} does not exist, skipping")
    
    logger.info(f"Remaining import fixes completed!")
    logger.info(f"Total files updated: {total_updated}/{total_files}")
    
    # Create a summary of fixes
    summary_file = Path("REMAINING_IMPORT_FIXES_SUMMARY.md")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# Remaining Import Fixes Summary\n\n")
        f.write(f"**Total files processed:** {total_files}\n")
        f.write(f"**Total files updated:** {total_updated}\n\n")
        f.write("## Import Mappings Applied\n\n")
        f.write("| Old Import | New Import |\n")
        f.write("|------------|------------|\n")
        for old, new in REMAINING_IMPORT_MAPPINGS.items():
            f.write(f"| `{old}` | `{new}` |\n")
        f.write("\n## Pattern Fixes Applied\n\n")
        f.write("| Old Pattern | New Pattern |\n")
        f.write("|-------------|-------------|\n")
        for old, new in PROBLEMATIC_PATTERNS:
            f.write(f"| `{old}` | `{new}` |\n")
        f.write("\n## Next Steps\n\n")
        f.write("1. Run the validation script again to check for remaining issues\n")
        f.write("2. Test the application to ensure all imports work\n")
        f.write("3. Run tests to verify functionality\n")
    
    logger.info(f"Summary written to {summary_file}")

if __name__ == "__main__":
    main()
