"""
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
