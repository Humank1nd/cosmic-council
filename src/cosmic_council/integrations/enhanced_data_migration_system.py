"""
Enhanced Data Migration System for Agent Orchestrator
Migrates data from existing schema to the detailed 6-database ROYGBV structure
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
import uuid

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Import the detailed database models
from database_models_detailed import (
    ResearchCoreProblem, ResearchFinding, ResearchPrioritizedQuestion,
    PlanningRelatedQuestion, PlanningActionPlan, PlanningDependency,
    DevelopmentPrototype, DevelopmentInternalTesting, DevelopmentCreativeNote,
    BudgetResourceInventory, BudgetAllocation, BudgetTimeCostAnalysis,
    MarketInsight, MarketCommunicationStrategy, MarketPerformanceMetric,
    SupportUserFeedback, SupportPerformanceAssessment, SupportContinuousImprovement
)

logger = logging.getLogger(__name__)

@dataclass
class MigrationResult:
    """Result of a migration operation"""
    success: bool
    migrated_records: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time_ms: int = 0
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MigrationPlan:
    """Plan for migrating data between schemas"""
    source_table: str
    target_table: str
    field_mappings: Dict[str, str]
    transformation_rules: Dict[str, Any] = field(default_factory=dict)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

class EnhancedDataMigrationSystem:
    """
    Enhanced data migration system for Agent Orchestrator
    Handles migration from existing schema to detailed ROYGBV structure
    """
    
    def __init__(self, 
                 source_database_url: str,
                 target_database_url: str,
                 migration_config: Dict[str, Any] = None):
        """
        Initialize the migration system
        
        Args:
            source_database_url: Source database connection string
            target_database_url: Target database connection string
            migration_config: Migration configuration
        """
        self.source_database_url = source_database_url
        self.target_database_url = target_database_url
        self.migration_config = migration_config or {}
        
        # Create database engines
        self.source_engine = create_async_engine(source_database_url)
        self.target_engine = create_async_engine(target_database_url)
        
        # Create session factories
        self.source_session_factory = sessionmaker(
            self.source_engine, class_=AsyncSession, expire_on_commit=False
        )
        self.target_session_factory = sessionmaker(
            self.target_engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Migration plans for each table
        self.migration_plans = self._create_migration_plans()
        
        logger.info("Enhanced Data Migration System initialized")

    def _create_migration_plans(self) -> Dict[str, MigrationPlan]:
        """Create migration plans for each table"""
        return {
            "problems_to_research_core_problems": MigrationPlan(
                source_table="problems",
                target_table="research_core_problems",
                field_mappings={
                    "id": "id",
                    "title": "main_problem_statement",
                    "description": "context",
                    "domain": "associated_themes",
                    "priority": "severity_priority_rating",
                    "status": "problem_status",
                    "created_by": "submitted_by",
                    "created_at": "created_at"
                },
                transformation_rules={
                    "associated_themes": "array_convert",
                    "severity_priority_rating": "priority_mapping",
                    "problem_status": "status_mapping"
                },
                validation_rules={
                    "required_fields": ["title", "description"],
                    "max_length": {"main_problem_statement": 10000}
                }
            ),
            
            "solutions_to_research_findings": MigrationPlan(
                source_table="solutions",
                target_table="research_findings",
                field_mappings={
                    "id": "id",
                    "problem_id": "core_problem_id",
                    "title": "source",
                    "description": "summary",
                    "created_by": "author",
                    "created_at": "date_added"
                },
                transformation_rules={
                    "credibility_rating": "default_rating",
                    "relevance_rating": "default_rating",
                    "impact_rating": "default_rating"
                },
                validation_rules={
                    "required_fields": ["title", "description"],
                    "foreign_key": "core_problem_id"
                }
            ),
            
            "cycles_to_planning_action_plans": MigrationPlan(
                source_table="cycles",
                target_table="planning_action_plans",
                field_mappings={
                    "id": "id",
                    "problem_id": "related_question_id",
                    "objective": "high_level_objective",
                    "status": "plan_status",
                    "created_at": "created_at"
                },
                transformation_rules={
                    "detailed_steps": "default_steps",
                    "priority_level": "default_priority",
                    "completion_percentage": "default_completion"
                },
                validation_rules={
                    "required_fields": ["objective"],
                    "foreign_key": "related_question_id"
                }
            ),
            
            "workflow_sessions_to_development_prototypes": MigrationPlan(
                source_table="workflow_sessions",
                target_table="development_prototypes",
                field_mappings={
                    "id": "id",
                    "problem_id": "action_plan_id",
                    "session_type": "prototype_name",
                    "notes": "prototype_description",
                    "status": "prototype_status",
                    "created_at": "created_at"
                },
                transformation_rules={
                    "design_specifications": "default_specifications",
                    "technical_requirements": "default_requirements",
                    "creative_concepts": "default_concepts"
                },
                validation_rules={
                    "required_fields": ["session_type"],
                    "foreign_key": "action_plan_id"
                }
            ),
            
            "stakeholders_to_budget_resource_inventory": MigrationPlan(
                source_table="stakeholders",
                target_table="budget_resource_inventory",
                field_mappings={
                    "id": "id",
                    "name": "resource_name",
                    "type": "resource_type",
                    "description": "resource_description",
                    "created_at": "created_at"
                },
                transformation_rules={
                    "resource_type": "stakeholder_type_mapping",
                    "current_availability": "default_availability",
                    "quantity_available": "default_quantity",
                    "unit_cost": "default_cost"
                },
                validation_rules={
                    "required_fields": ["name"],
                    "enum_values": {"resource_type": ["personnel", "material", "equipment", "software", "external_service", "facility"]}
                }
            ),
            
            "constraints_to_market_insights": MigrationPlan(
                source_table="constraints",
                target_table="market_insights",
                field_mappings={
                    "id": "id",
                    "problem_id": "prototype_id",
                    "type": "insight_type",
                    "description": "insight_description",
                    "created_at": "created_at"
                },
                transformation_rules={
                    "insight_type": "constraint_type_mapping",
                    "insight_title": "default_title",
                    "data_source": "default_source",
                    "confidence_level": "default_confidence"
                },
                validation_rules={
                    "required_fields": ["description"],
                    "foreign_key": "prototype_id"
                }
            ),
            
            "success_criteria_to_support_user_feedback": MigrationPlan(
                source_table="success_criteria",
                target_table="support_user_feedback",
                field_mappings={
                    "id": "id",
                    "problem_id": "communication_strategy_id",
                    "criterion": "feedback_content",
                    "target_value": "satisfaction_rating",
                    "created_at": "feedback_date"
                },
                transformation_rules={
                    "feedback_type": "default_feedback_type",
                    "user_type": "default_user_type",
                    "priority_level": "default_priority",
                    "feedback_status": "default_status"
                },
                validation_rules={
                    "required_fields": ["criterion"],
                    "foreign_key": "communication_strategy_id"
                }
            )
        }

    async def analyze_migration_requirements(self) -> Dict[str, Any]:
        """
        Analyze the source database and determine migration requirements
        
        Returns:
            Dictionary with migration analysis results
        """
        try:
            async with self.source_session_factory() as session:
                # Get table information
                inspector = inspect(session.bind)
                source_tables = inspector.get_table_names()
                
                # Analyze each table
                table_analysis = {}
                for table_name in source_tables:
                    if table_name in ["schema_migrations", "alembic_version"]:
                        continue
                    
                    # Get table info
                    columns = inspector.get_columns(table_name)
                    indexes = inspector.get_indexes(table_name)
                    foreign_keys = inspector.get_foreign_keys(table_name)
                    
                    # Count records
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    record_count = result.scalar()
                    
                    table_analysis[table_name] = {
                        "columns": [col["name"] for col in columns],
                        "column_details": columns,
                        "indexes": indexes,
                        "foreign_keys": foreign_keys,
                        "record_count": record_count
                    }
                
                # Determine migration strategy
                migration_strategy = self._determine_migration_strategy(table_analysis)
                
                return {
                    "source_tables": source_tables,
                    "table_analysis": table_analysis,
                    "migration_strategy": migration_strategy,
                    "estimated_migration_time": self._estimate_migration_time(table_analysis),
                    "migration_plans": list(self.migration_plans.keys())
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze migration requirements: {e}")
            raise

    def _determine_migration_strategy(self, table_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the best migration strategy based on table analysis"""
        total_records = sum(analysis["record_count"] for analysis in table_analysis.values())
        
        if total_records < 1000:
            return {"strategy": "direct_migration", "batch_size": 100}
        elif total_records < 10000:
            return {"strategy": "batched_migration", "batch_size": 500}
        else:
            return {"strategy": "streaming_migration", "batch_size": 1000}

    def _estimate_migration_time(self, table_analysis: Dict[str, Any]) -> int:
        """Estimate migration time in minutes"""
        total_records = sum(analysis["record_count"] for analysis in table_analysis.values())
        # Rough estimate: 100 records per second
        return max(1, total_records // 6000)

    async def execute_migration(self, 
                              migration_plan_name: str,
                              dry_run: bool = False) -> MigrationResult:
        """
        Execute a specific migration plan
        
        Args:
            migration_plan_name: Name of the migration plan to execute
            dry_run: If True, only validate without actually migrating
            
        Returns:
            MigrationResult with migration details
        """
        if migration_plan_name not in self.migration_plans:
            return MigrationResult(
                success=False,
                migrated_records=0,
                errors=[f"Migration plan '{migration_plan_name}' not found"]
            )
        
        plan = self.migration_plans[migration_plan_name]
        start_time = datetime.now(timezone.utc)
        
        try:
            # Validate migration plan
            validation_result = await self._validate_migration_plan(plan)
            if not validation_result["valid"]:
                return MigrationResult(
                    success=False,
                    migrated_records=0,
                    errors=validation_result["errors"]
                )
            
            if dry_run:
                return MigrationResult(
                    success=True,
                    migrated_records=0,
                    details={"dry_run": True, "validation": validation_result}
                )
            
            # Execute migration
            migrated_records = await self._execute_migration_plan(plan)
            
            end_time = datetime.now(timezone.utc)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return MigrationResult(
                success=True,
                migrated_records=migrated_records,
                execution_time_ms=execution_time_ms,
                details={"migration_plan": migration_plan_name}
            )
            
        except Exception as e:
            end_time = datetime.now(timezone.utc)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return MigrationResult(
                success=False,
                migrated_records=0,
                errors=[str(e)],
                execution_time_ms=execution_time_ms
            )

    async def _validate_migration_plan(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Validate a migration plan"""
        errors = []
        warnings = []
        
        try:
            # Check if source table exists
            async with self.source_session_factory() as session:
                inspector = inspect(session.bind)
                if plan.source_table not in inspector.get_table_names():
                    errors.append(f"Source table '{plan.source_table}' does not exist")
                    return {"valid": False, "errors": errors, "warnings": warnings}
                
                # Check if target table exists
                async with self.target_session_factory() as session:
                    inspector = inspect(session.bind)
                    if plan.target_table not in inspector.get_table_names():
                        errors.append(f"Target table '{plan.target_table}' does not exist")
                        return {"valid": False, "errors": errors, "warnings": warnings}
                
                # Validate field mappings
                source_columns = [col["name"] for col in inspector.get_columns(plan.source_table)]
                target_columns = [col["name"] for col in inspector.get_columns(plan.target_table)]
                
                for source_field, target_field in plan.field_mappings.items():
                    if source_field not in source_columns:
                        errors.append(f"Source field '{source_field}' does not exist in '{plan.source_table}'")
                    if target_field not in target_columns:
                        errors.append(f"Target field '{target_field}' does not exist in '{plan.target_table}'")
                
                # Check required fields
                if "required_fields" in plan.validation_rules:
                    for required_field in plan.validation_rules["required_fields"]:
                        if required_field not in target_columns:
                            errors.append(f"Required field '{required_field}' missing in target table")
                
                return {
                    "valid": len(errors) == 0,
                    "errors": errors,
                    "warnings": warnings
                }
                
        except Exception as e:
            return {"valid": False, "errors": [str(e)], "warnings": warnings}

    async def _execute_migration_plan(self, plan: MigrationPlan) -> int:
        """Execute a migration plan"""
        migrated_records = 0
        
        try:
            async with self.source_session_factory() as session:
                # Get source data
                source_data = await self._get_source_data(session, plan)
                
                # Transform data
                transformed_data = await self._transform_data(source_data, plan)
                
                # Insert into target database
                async with self.target_session_factory() as target_session:
                    migrated_records = await self._insert_target_data(target_session, plan, transformed_data)
                
                return migrated_records
                
        except Exception as e:
            logger.error(f"Failed to execute migration plan: {e}")
            raise

    async def _get_source_data(self, session: AsyncSession, plan: MigrationPlan) -> List[Dict[str, Any]]:
        """Get data from source table"""
        try:
            # Build SELECT query
            source_fields = list(plan.field_mappings.keys())
            query = f"SELECT {', '.join(source_fields)} FROM {plan.source_table}"
            
            result = await session.execute(text(query))
            rows = result.fetchall()
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                row_dict = {}
                for i, field in enumerate(source_fields):
                    row_dict[field] = row[i]
                data.append(row_dict)
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get source data: {e}")
            raise

    async def _transform_data(self, source_data: List[Dict[str, Any]], plan: MigrationPlan) -> List[Dict[str, Any]]:
        """Transform source data according to migration plan"""
        transformed_data = []
        
        for record in source_data:
            transformed_record = {}
            
            # Apply field mappings
            for source_field, target_field in plan.field_mappings.items():
                if source_field in record:
                    transformed_record[target_field] = record[source_field]
            
            # Apply transformation rules
            for rule_name, rule_value in plan.transformation_rules.items():
                if rule_name == "array_convert":
                    # Convert string to array
                    if isinstance(transformed_record.get(rule_name), str):
                        transformed_record[rule_name] = [transformed_record[rule_name]]
                elif rule_name == "priority_mapping":
                    # Map priority values
                    priority_mapping = {
                        "low": "low",
                        "medium": "medium", 
                        "high": "high",
                        "critical": "critical"
                    }
                    transformed_record[rule_name] = priority_mapping.get(
                        transformed_record.get(rule_name, "medium"), "medium"
                    )
                elif rule_name == "status_mapping":
                    # Map status values
                    status_mapping = {
                        "active": "active",
                        "in_progress": "in_review",
                        "completed": "resolved",
                        "archived": "archived"
                    }
                    transformed_record[rule_name] = status_mapping.get(
                        transformed_record.get(rule_name, "active"), "active"
                    )
                elif rule_name == "default_rating":
                    # Set default rating
                    transformed_record[rule_name] = 3
                elif rule_name == "default_steps":
                    # Set default steps
                    transformed_record[rule_name] = []
                elif rule_name == "default_priority":
                    # Set default priority
                    transformed_record[rule_name] = "medium"
                elif rule_name == "default_completion":
                    # Set default completion
                    transformed_record[rule_name] = 0.0
                elif rule_name == "default_specifications":
                    # Set default specifications
                    transformed_record[rule_name] = {}
                elif rule_name == "default_requirements":
                    # Set default requirements
                    transformed_record[rule_name] = []
                elif rule_name == "default_concepts":
                    # Set default concepts
                    transformed_record[rule_name] = []
                elif rule_name == "stakeholder_type_mapping":
                    # Map stakeholder types
                    type_mapping = {
                        "person": "personnel",
                        "organization": "external_service",
                        "system": "software"
                    }
                    transformed_record[rule_name] = type_mapping.get(
                        transformed_record.get(rule_name, "personnel"), "personnel"
                    )
                elif rule_name == "default_availability":
                    # Set default availability
                    transformed_record[rule_name] = "available"
                elif rule_name == "default_quantity":
                    # Set default quantity
                    transformed_record[rule_name] = 1
                elif rule_name == "default_cost":
                    # Set default cost
                    transformed_record[rule_name] = 0.0
                elif rule_name == "constraint_type_mapping":
                    # Map constraint types
                    type_mapping = {
                        "budget": "threat",
                        "time": "threat",
                        "resource": "threat",
                        "technical": "threat",
                        "regulatory": "threat"
                    }
                    transformed_record[rule_name] = type_mapping.get(
                        transformed_record.get(rule_name, "threat"), "threat"
                    )
                elif rule_name == "default_title":
                    # Set default title
                    transformed_record[rule_name] = "Migrated Constraint"
                elif rule_name == "default_source":
                    # Set default source
                    transformed_record[rule_name] = "Migration"
                elif rule_name == "default_confidence":
                    # Set default confidence
                    transformed_record[rule_name] = 3
                elif rule_name == "default_feedback_type":
                    # Set default feedback type
                    transformed_record[rule_name] = "suggestion"
                elif rule_name == "default_user_type":
                    # Set default user type
                    transformed_record[rule_name] = "stakeholder"
                elif rule_name == "default_status":
                    # Set default status
                    transformed_record[rule_name] = "received"
            
            # Add required fields if missing
            if "required_fields" in plan.validation_rules:
                for required_field in plan.validation_rules["required_fields"]:
                    if required_field not in transformed_record:
                        transformed_record[required_field] = f"Migrated {required_field}"
            
            # Add UUID for new records
            if "id" not in transformed_record:
                transformed_record["id"] = str(uuid.uuid4())
            
            transformed_data.append(transformed_record)
        
        return transformed_data

    async def _insert_target_data(self, 
                                session: AsyncSession, 
                                plan: MigrationPlan, 
                                transformed_data: List[Dict[str, Any]]) -> int:
        """Insert transformed data into target table"""
        try:
            inserted_count = 0
            
            for record in transformed_data:
                # Build INSERT query
                fields = list(record.keys())
                values = list(record.values())
                placeholders = [f":{field}" for field in fields]
                
                query = f"""
                    INSERT INTO {plan.target_table} ({', '.join(fields)})
                    VALUES ({', '.join(placeholders)})
                """
                
                await session.execute(text(query), record)
                inserted_count += 1
            
            await session.commit()
            return inserted_count
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to insert target data: {e}")
            raise

    async def execute_complete_migration(self, dry_run: bool = False) -> Dict[str, MigrationResult]:
        """
        Execute complete migration from source to target database
        
        Args:
            dry_run: If True, only validate without actually migrating
            
        Returns:
            Dictionary with results for each migration plan
        """
        results = {}
        
        # Execute migrations in dependency order
        migration_order = [
            "problems_to_research_core_problems",
            "solutions_to_research_findings", 
            "cycles_to_planning_action_plans",
            "workflow_sessions_to_development_prototypes",
            "stakeholders_to_budget_resource_inventory",
            "constraints_to_market_insights",
            "success_criteria_to_support_user_feedback"
        ]
        
        for migration_name in migration_order:
            try:
                logger.info(f"Executing migration: {migration_name}")
                result = await self.execute_migration(migration_name, dry_run)
                results[migration_name] = result
                
                if not result.success:
                    logger.error(f"Migration {migration_name} failed: {result.errors}")
                    # Continue with other migrations
                    continue
                
                logger.info(f"Migration {migration_name} completed: {result.migrated_records} records")
                
            except Exception as e:
                logger.error(f"Migration {migration_name} failed with exception: {e}")
                results[migration_name] = MigrationResult(
                    success=False,
                    migrated_records=0,
                    errors=[str(e)]
                )
        
        return results

    async def close(self):
        """Close database connections"""
        await self.source_engine.dispose()
        await self.target_engine.dispose()
        logger.info("Enhanced Data Migration System closed")

# Example usage
async def main():
    """Example usage of the enhanced data migration system"""
    
    migration_system = EnhancedDataMigrationSystem(
        source_database_url="postgresql+asyncpg://user:password@localhost/source_db",
        target_database_url="postgresql+asyncpg://user:password@localhost/target_db"
    )
    
    try:
        # Analyze migration requirements
        analysis = await migration_system.analyze_migration_requirements()
        print(f"Migration Analysis: {json.dumps(analysis, indent=2)}")
        
        # Execute complete migration (dry run first)
        results = await migration_system.execute_complete_migration(dry_run=True)
        print(f"Dry Run Results: {json.dumps(results, indent=2, default=str)}")
        
        # Execute actual migration
        results = await migration_system.execute_complete_migration(dry_run=False)
        print(f"Migration Results: {json.dumps(results, indent=2, default=str)}")
        
    finally:
        await migration_system.close()

if __name__ == "__main__":
    asyncio.run(main())
