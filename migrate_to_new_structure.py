#!/usr/bin/env python3
"""
Migration script to move files from old structure to new structure.
"""

import os
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_files():
    """Migrate files from old structure to new structure"""
    
    # Define migration mappings
    migrations = [
        # Move static files
        ("static/css", "src_new/web/static/css"),
        ("static/js", "src_new/web/static/js"),
        ("templates", "src_new/web/templates"),
        
        # Move existing services
        ("services/gateway", "services_new/gateway"),
        ("services/analytics", "services_new/analytics"),
        ("services/reflection", "services_new/reflection"),
        
        # Move refinement engine
        ("refinement_engine", "services_new/refinement"),
        
        # Move infrastructure
        ("infrastructure", "infrastructure_new"),
        
        # Move governance
        ("governance", "governance_new"),
        
        # Move enterprises
        ("enterprises", "enterprises_new"),
        
        # Move scripts
        ("scripts", "scripts_new"),
        
        # Move config
        ("config", "config_new"),
        
        # Move docs
        ("docs", "docs_new"),
        
        # Move tests
        ("tests", "tests_new"),
    ]
    
    # Create new directories
    new_dirs = [
        "services_new",
        "infrastructure_new", 
        "governance_new",
        "enterprises_new",
        "scripts_new",
        "config_new",
        "docs_new",
        "tests_new"
    ]
    
    for dir_name in new_dirs:
        os.makedirs(dir_name, exist_ok=True)
        logger.info(f"Created directory: {dir_name}")
    
    # Perform migrations
    for source, destination in migrations:
        if os.path.exists(source):
            if os.path.isdir(source):
                if os.path.exists(destination):
                    shutil.rmtree(destination)
                shutil.copytree(source, destination)
                logger.info(f"Migrated directory: {source} -> {destination}")
            else:
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                shutil.copy2(source, destination)
                logger.info(f"Migrated file: {source} -> {destination}")
        else:
            logger.warning(f"Source not found: {source}")
    
    # Move root files
    root_files = [
        "main.py",
        "requirements.txt",
        "docker-compose.yml",
        "Dockerfile",
        "README.md",
        "LICENSE",
        "pytest.ini"
    ]
    
    for file_name in root_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, f"root_{file_name}")
            logger.info(f"Backed up root file: {file_name} -> root_{file_name}")
    
    logger.info("Migration completed successfully!")

def cleanup_old_structure():
    """Clean up old structure (optional)"""
    old_dirs = [
        "src/cosmic_council",
        "src/applications", 
        "static",
        "templates"
    ]
    
    for dir_name in old_dirs:
        if os.path.exists(dir_name):
            response = input(f"Remove old directory {dir_name}? (y/N): ")
            if response.lower() == 'y':
                shutil.rmtree(dir_name)
                logger.info(f"Removed old directory: {dir_name}")

if __name__ == "__main__":
    print("Cosmic Council Structure Migration")
    print("==================================")
    print()
    print("This script will migrate files from the old structure to the new structure.")
    print("The old files will be preserved with 'root_' prefix.")
    print()
    
    response = input("Proceed with migration? (y/N): ")
    if response.lower() == 'y':
        migrate_files()
        
        print()
        response = input("Clean up old structure? (y/N): ")
        if response.lower() == 'y':
            cleanup_old_structure()
        
        print()
        print("Migration completed!")
        print("Next steps:")
        print("1. Review the new structure in src_new/")
        print("2. Update import statements in migrated files")
        print("3. Test the new structure")
        print("4. Update deployment configurations")
    else:
        print("Migration cancelled.")
