"""
Database Migrations and Schema Management for Agent Orchestrator System
"""

import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from database_connection import get_database_connection, get_session_context
from database_models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MigrationManager:
    """Manages database migrations and schema changes"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
        self.migrations_table = "schema_migrations"
    
    def create_migrations_table(self):
        """Create the migrations tracking table"""
        try:
            with get_session_context() as session:
                # Check if migrations table exists
                inspector = inspect(session.bind)
                if self.migrations_table in inspector.get_table_names():
                    logger.info("Migrations table already exists")
                    return
                
                # Create migrations table
                session.execute(text(f"""
                    CREATE TABLE {self.migrations_table} (
                        id SERIAL PRIMARY KEY,
                        version VARCHAR(50) UNIQUE NOT NULL,
                        description TEXT,
                        applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        checksum VARCHAR(64),
                        execution_time_ms INTEGER
                    )
                """))
                
                logger.info(f"Created migrations table: {self.migrations_table}")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create migrations table: {str(e)}")
            raise
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations"""
        try:
            with get_session_context() as session:
                result = session.execute(text(f"""
                    SELECT version FROM {self.migrations_table} 
                    ORDER BY applied_at
                """))
                return [row[0] for row in result.fetchall()]
        except SQLAlchemyError as e:
            logger.error(f"Failed to get applied migrations: {str(e)}")
            return []
    
    def record_migration(self, version: str, description: str, checksum: str, execution_time_ms: int):
        """Record a migration as applied"""
        try:
            with get_session_context() as session:
                session.execute(text(f"""
                    INSERT INTO {self.migrations_table} 
                    (version, description, checksum, execution_time_ms)
                    VALUES (:version, :description, :checksum, :execution_time_ms)
                """), {
                    'version': version,
                    'description': description,
                    'checksum': checksum,
                    'execution_time_ms': execution_time_ms
                })
                logger.info(f"Recorded migration: {version}")
        except SQLAlchemyError as e:
            logger.error(f"Failed to record migration {version}: {str(e)}")
            raise
    
    def apply_migration(self, version: str, description: str, sql: str):
        """Apply a migration"""
        try:
            start_time = datetime.now(timezone.utc)
            
            with get_session_context() as session:
                # Execute the migration SQL
                session.execute(text(sql))
                
            end_time = datetime.now(timezone.utc)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Record the migration
            checksum = self._calculate_checksum(sql)
            self.record_migration(version, description, checksum, execution_time_ms)
            
            logger.info(f"Applied migration {version} in {execution_time_ms}ms")
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to apply migration {version}: {str(e)}")
            raise
    
    def _calculate_checksum(self, content: str) -> str:
        """Calculate checksum for migration content"""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get migration status information"""
        try:
            with get_session_context() as session:
                # Get applied migrations
                applied_result = session.execute(text(f"""
                    SELECT version, description, applied_at, execution_time_ms
                    FROM {self.migrations_table}
                    ORDER BY applied_at DESC
                """))
                applied_migrations = [
                    {
                        'version': row[0],
                        'description': row[1],
                        'applied_at': row[2],
                        'execution_time_ms': row[3]
                    }
                    for row in applied_result.fetchall()
                ]
                
                # Get database schema version
                schema_version = self._get_schema_version()
                
                return {
                    'schema_version': schema_version,
                    'applied_migrations': applied_migrations,
                    'total_migrations': len(applied_migrations),
                    'last_migration': applied_migrations[0] if applied_migrations else None
                }
        except SQLAlchemyError as e:
            logger.error(f"Failed to get migration status: {str(e)}")
            return {'error': str(e)}
    
    def _get_schema_version(self) -> str:
        """Get current schema version"""
        try:
            with get_session_context() as session:
                result = session.execute(text(f"""
                    SELECT version FROM {self.migrations_table}
                    ORDER BY applied_at DESC LIMIT 1
                """))
                row = result.fetchone()
                return row[0] if row else "0.0.0"
        except:
            return "0.0.0"

# Predefined migrations
MIGRATIONS = {
    "001_initial_schema": {
        "description": "Create initial database schema with core tables",
        "sql": """
            -- Create initial schema
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
            
            -- Create core tables (this will be handled by SQLAlchemy models)
            -- The actual table creation is done by Base.metadata.create_all()
        """
    },
    
    "002_add_indexes": {
        "description": "Add performance indexes to core tables",
        "sql": """
            -- Add performance indexes
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_problems_domain_complexity 
            ON problems(domain, complexity);
            
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_problems_status_priority 
            ON problems(status, priority);
            
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cycles_problem_status 
            ON cycles(problem_id, status);
            
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_enterprise_results_cycle_enterprise 
            ON enterprise_results(cycle_id, enterprise_id);
            
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_solutions_problem_confidence 
            ON solutions(problem_id, confidence_score);
            
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workflow_sessions_problem_user 
            ON workflow_sessions(problem_id, user_id);
            
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_resource_timestamp 
            ON audit_logs(resource_type, timestamp);
            
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_system_metrics_name_timestamp 
            ON system_metrics(metric_name, recorded_at);
        """
    },
    
    "003_add_constraints": {
        "description": "Add data integrity constraints",
        "sql": """
            -- Add check constraints for data integrity
            ALTER TABLE problems 
            ADD CONSTRAINT chk_problems_complexity 
            CHECK (complexity IN ('simple', 'moderate', 'complex', 'systemic'));
            
            ALTER TABLE problems 
            ADD CONSTRAINT chk_problems_status 
            CHECK (status IN ('active', 'in_progress', 'completed', 'archived'));
            
            ALTER TABLE problems 
            ADD CONSTRAINT chk_problems_priority 
            CHECK (priority IN ('low', 'medium', 'high', 'critical'));
            
            ALTER TABLE cycles 
            ADD CONSTRAINT chk_cycles_status 
            CHECK (status IN ('pending', 'in_progress', 'completed', 'failed'));
            
            ALTER TABLE enterprise_results 
            ADD CONSTRAINT chk_enterprise_results_status 
            CHECK (status IN ('completed', 'failed', 'skipped'));
            
            ALTER TABLE solutions 
            ADD CONSTRAINT chk_solutions_status 
            CHECK (status IN ('draft', 'reviewed', 'approved', 'implemented', 'archived'));
            
            ALTER TABLE solutions 
            ADD CONSTRAINT chk_solutions_risk_level 
            CHECK (risk_level IN ('low', 'medium', 'high', 'critical'));
            
            ALTER TABLE workflow_sessions 
            ADD CONSTRAINT chk_workflow_sessions_status 
            CHECK (status IN ('active', 'completed', 'paused', 'cancelled'));
            
            ALTER TABLE workflow_steps 
            ADD CONSTRAINT chk_workflow_steps_status 
            CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'skipped'));
        """
    },
    
    "004_add_triggers": {
        "description": "Add database triggers for automatic updates",
        "sql": """
            -- Create function to update updated_at timestamp
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            
            -- Add triggers for updated_at columns
            CREATE TRIGGER update_problems_updated_at 
            BEFORE UPDATE ON problems 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
            CREATE TRIGGER update_cycles_updated_at 
            BEFORE UPDATE ON cycles 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
            CREATE TRIGGER update_solutions_updated_at 
            BEFORE UPDATE ON solutions 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
            CREATE TRIGGER update_solution_components_updated_at 
            BEFORE UPDATE ON solution_components 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
            CREATE TRIGGER update_implementation_tracking_updated_at 
            BEFORE UPDATE ON implementation_tracking 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
            CREATE TRIGGER update_users_updated_at 
            BEFORE UPDATE ON users 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
    },
    
    "005_add_partitions": {
        "description": "Add table partitioning for large tables",
        "sql": """
            -- Partition system_metrics by month for better performance
            -- This is a placeholder for future partitioning implementation
            -- Actual partitioning would require more complex setup
            
            -- Create partitioned table for audit logs (if needed for high volume)
            -- CREATE TABLE audit_logs_partitioned (
            --     LIKE audit_logs INCLUDING ALL
            -- ) PARTITION BY RANGE (timestamp);
            
            -- Add comments for documentation
            COMMENT ON TABLE problems IS 'Problems to be solved by the Agent Orchestrator';
            COMMENT ON TABLE cycles IS 'Problem-solving cycles executed by the Agent Orchestrator';
            COMMENT ON TABLE solutions IS 'Solutions generated by the Agent Orchestrator';
            COMMENT ON TABLE enterprises IS 'Agent Orchestrator Enterprise Agents';
            COMMENT ON TABLE enterprise_results IS 'Results from individual enterprise processing';
            COMMENT ON TABLE workflow_sessions IS 'Workflow sessions for step-by-step problem solving';
            COMMENT ON TABLE audit_logs IS 'Audit log for system activities';
            COMMENT ON TABLE system_metrics IS 'System-wide metrics and analytics';
        """
    },
    
    "006_add_views": {
        "description": "Add useful database views for reporting",
        "sql": """
            -- Create view for problem summary with cycle count
            CREATE OR REPLACE VIEW problem_summary AS
            SELECT 
                p.id,
                p.title,
                p.domain,
                p.complexity,
                p.status,
                p.priority,
                p.created_at,
                p.updated_at,
                COUNT(c.id) as cycle_count,
                MAX(c.created_at) as last_cycle_at,
                AVG(c.confidence_score) as avg_confidence
            FROM problems p
            LEFT JOIN cycles c ON p.id = c.problem_id
            GROUP BY p.id, p.title, p.domain, p.complexity, p.status, p.priority, p.created_at, p.updated_at;
            
            -- Create view for cycle performance metrics
            CREATE OR REPLACE VIEW cycle_performance AS
            SELECT 
                c.id,
                c.problem_id,
                c.cycle_number,
                c.status,
                c.total_duration,
                c.confidence_score,
                c.created_at,
                COUNT(er.id) as enterprise_results_count,
                AVG(er.confidence_score) as avg_enterprise_confidence,
                AVG(er.processing_time) as avg_processing_time,
                COUNT(CASE WHEN er.status = 'completed' THEN 1 END) as successful_enterprises
            FROM cycles c
            LEFT JOIN enterprise_results er ON c.id = er.cycle_id
            GROUP BY c.id, c.problem_id, c.cycle_number, c.status, c.total_duration, c.confidence_score, c.created_at;
            
            -- Create view for solution effectiveness
            CREATE OR REPLACE VIEW solution_effectiveness AS
            SELECT 
                s.id,
                s.problem_id,
                s.title,
                s.status,
                s.confidence_score,
                s.feasibility_score,
                s.impact_score,
                s.estimated_cost,
                s.estimated_duration,
                s.created_at,
                COUNT(sc.id) as component_count,
                COUNT(CASE WHEN sc.status = 'completed' THEN 1 END) as completed_components,
                COUNT(it.id) as implementation_tracking_count
            FROM solutions s
            LEFT JOIN solution_components sc ON s.id = sc.solution_id
            LEFT JOIN implementation_tracking it ON s.id = it.solution_id
            GROUP BY s.id, s.problem_id, s.title, s.status, s.confidence_score, s.feasibility_score, s.impact_score, s.estimated_cost, s.estimated_duration, s.created_at;
        """
    }
}

def run_migrations():
    """Run all pending migrations"""
    try:
        migration_manager = MigrationManager()
        
        # Create migrations table if it doesn't exist
        migration_manager.create_migrations_table()
        
        # Get applied migrations
        applied_migrations = migration_manager.get_applied_migrations()
        
        # Run pending migrations
        for version, migration in MIGRATIONS.items():
            if version not in applied_migrations:
                logger.info(f"Applying migration: {version}")
                migration_manager.apply_migration(
                    version,
                    migration["description"],
                    migration["sql"]
                )
            else:
                logger.info(f"Migration {version} already applied")
        
        logger.info("All migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise

def rollback_migration(version: str):
    """Rollback a specific migration (use with caution!)"""
    try:
        migration_manager = MigrationManager()
        
        with get_session_context() as session:
            # Remove migration record
            session.execute(text(f"""
                DELETE FROM {migration_manager.migrations_table} 
                WHERE version = :version
            """), {'version': version})
        
        logger.warning(f"Rolled back migration: {version}")
        
    except Exception as e:
        logger.error(f"Failed to rollback migration {version}: {str(e)}")
        raise

def get_migration_status():
    """Get current migration status"""
    try:
        migration_manager = MigrationManager()
        return migration_manager.get_migration_status()
    except Exception as e:
        logger.error(f"Failed to get migration status: {str(e)}")
        return {'error': str(e)}

def create_database_backup(backup_file: str):
    """Create a database backup before migrations"""
    try:
        from database_connection import backup_database, get_database_manager
        
        db_manager = get_database_manager()
        backup_database(db_manager.database_url, backup_file)
        logger.info(f"Database backup created: {backup_file}")
        
    except Exception as e:
        logger.error(f"Failed to create database backup: {str(e)}")
        raise

def validate_schema():
    """Validate database schema integrity"""
    try:
        with get_session_context() as session:
            inspector = inspect(session.bind)
            
            # Get all tables
            tables = inspector.get_table_names()
            
            # Expected tables from our models
            expected_tables = [
                'problems', 'solutions', 'cycles', 'enterprises',
                'enterprise_results', 'workflow_sessions', 'workflow_steps',
                'users', 'stakeholders', 'constraints', 'success_criteria',
                'solution_components', 'implementation_tracking',
                'cycle_analytics', 'system_metrics', 'audit_logs',
                'schema_migrations'
            ]
            
            # Check for missing tables
            missing_tables = [table for table in expected_tables if table not in tables]
            extra_tables = [table for table in tables if table not in expected_tables]
            
            # Validate key constraints
            validation_results = {
                'tables_exist': len(missing_tables) == 0,
                'missing_tables': missing_tables,
                'extra_tables': extra_tables,
                'total_tables': len(tables),
                'expected_tables': len(expected_tables)
            }
            
            # Check for key indexes
            key_indexes = [
                'idx_problems_domain_complexity',
                'idx_cycles_problem_status',
                'idx_enterprise_results_cycle_enterprise'
            ]
            
            existing_indexes = []
            missing_indexes = []
            
            for index_name in key_indexes:
                try:
                    result = session.execute(text(f"""
                        SELECT 1 FROM pg_indexes 
                        WHERE indexname = :index_name
                    """), {'index_name': index_name})
                    if result.fetchone():
                        existing_indexes.append(index_name)
                    else:
                        missing_indexes.append(index_name)
                except:
                    missing_indexes.append(index_name)
            
            validation_results.update({
                'indexes_exist': len(missing_indexes) == 0,
                'existing_indexes': existing_indexes,
                'missing_indexes': missing_indexes
            })
            
            return validation_results
            
    except Exception as e:
        logger.error(f"Schema validation failed: {str(e)}")
        return {'error': str(e)}

# Demo function
def demo_database_migrations():
    """Demonstrate database migrations"""
    print("🗄️ Agent Orchestrator Database Migrations Demo")
    print("=" * 60)
    
    try:
        from database_connection import initialize_database
        
        # Initialize database
        db_manager = initialize_database()
        
        print("✅ Database initialized")
        
        # Create initial schema
        print("\n🏗️ Creating initial schema...")
        db_manager.create_tables()
        print("✅ Initial schema created")
        
        # Run migrations
        print("\n🔄 Running migrations...")
        run_migrations()
        print("✅ Migrations completed")
        
        # Get migration status
        print("\n📊 Migration Status:")
        status = get_migration_status()
        print(f"   Schema Version: {status.get('schema_version', 'Unknown')}")
        print(f"   Total Migrations: {status.get('total_migrations', 0)}")
        
        if status.get('applied_migrations'):
            print("   Applied Migrations:")
            for migration in status['applied_migrations'][:5]:  # Show first 5
                print(f"     • {migration['version']}: {migration['description']}")
        
        # Validate schema
        print("\n🔍 Schema Validation:")
        validation = validate_schema()
        if validation.get('error'):
            print(f"   ❌ Validation Error: {validation['error']}")
        else:
            print(f"   ✅ Tables Exist: {validation.get('tables_exist', False)}")
            print(f"   ✅ Indexes Exist: {validation.get('indexes_exist', False)}")
            print(f"   Total Tables: {validation.get('total_tables', 0)}")
            print(f"   Missing Tables: {len(validation.get('missing_tables', []))}")
            print(f"   Missing Indexes: {len(validation.get('missing_indexes', []))}")
        
        print("\n✅ Database migrations demonstration completed!")
        
    except Exception as e:
        print(f"❌ Database migrations demo failed: {str(e)}")
        logger.error(f"Database migrations demo error: {str(e)}")

if __name__ == "__main__":
    demo_database_migrations()
