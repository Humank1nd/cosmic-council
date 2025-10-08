"""
Migration script to update the database layer with repository pattern.
"""

import os
import shutil
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database_layer():
    """Migrate the database layer to use repository pattern"""
    
    # Create backup of old database files
    old_db_path = Path("src/cosmic_council/database")
    backup_path = Path("src/cosmic_council/database_backup")
    
    if old_db_path.exists():
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(old_db_path, backup_path)
        logger.info(f"Backed up old database layer to {backup_path}")
    
    # Create new database directory structure
    new_db_path = Path("src/database")
    new_db_path.mkdir(exist_ok=True)
    
    # Create subdirectories
    subdirs = [
        "models",
        "repositories", 
        "migrations",
        "seeds"
    ]
    
    for subdir in subdirs:
        (new_db_path / subdir).mkdir(exist_ok=True)
        logger.info(f"Created directory: {new_db_path / subdir}")
    
    # Create __init__.py files
    init_files = [
        new_db_path / "__init__.py",
        new_db_path / "models" / "__init__.py",
        new_db_path / "repositories" / "__init__.py"
    ]
    
    for init_file in init_files:
        if not init_file.exists():
            init_file.write_text('"""Database layer for the Cosmic Council system."""\n')
            logger.info(f"Created {init_file}")
    
    # Create migration files
    migration_files = [
        "001_create_base_tables.sql",
        "002_create_problem_tables.sql", 
        "003_create_solution_tables.sql",
        "004_create_cycle_tables.sql",
        "005_create_enterprise_tables.sql",
        "006_create_user_tables.sql",
        "007_create_analytics_tables.sql"
    ]
    
    for migration_file in migration_files:
        migration_path = new_db_path / "migrations" / migration_file
        if not migration_path.exists():
            migration_path.write_text(f"-- Migration: {migration_file}\n-- TODO: Add migration SQL\n")
            logger.info(f"Created migration file: {migration_path}")
    
    # Create seed files
    seed_files = [
        "enterprises.csv",
        "users.csv",
        "constraints.csv"
    ]
    
    for seed_file in seed_files:
        seed_path = new_db_path / "seeds" / seed_file
        if not seed_path.exists():
            seed_path.write_text(f"# Seed data: {seed_file}\n# TODO: Add seed data\n")
            logger.info(f"Created seed file: {seed_path}")
    
    logger.info("Database layer migration completed successfully!")
    logger.info("New structure created at: src/database/")
    logger.info("Old structure backed up at: src/cosmic_council/database_backup/")

if __name__ == "__main__":
    migrate_database_layer()
