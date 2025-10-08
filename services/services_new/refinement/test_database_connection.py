"""
Test Database Connection and Schema Validation
Tests the actual PostgreSQL database connection, schema creation, and data operations.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import (
    DatabaseManager, ProblemModel, LayerModel, LayerRunModel, 
    SectorRunModel, RefinementModel, AnswerModel, initialize_database
)
from layers import LayerDefinitions
from escalator import EscalatorAction
from sector_engine import SectorType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnectionTester:
    """Test database connection and operations."""
    
    def __init__(self):
        self.db_manager = None
        self.test_results = {}
    
    async def setup_database_connection(self) -> bool:
        """Test database connection setup."""
        print("🔌 Testing Database Connection Setup...")
        
        try:
            # Get database URL from environment or use default
            database_url = os.getenv(
                "DATABASE_URL", 
                "postgresql+asyncpg://cosmic_council:cosmic_password@localhost:5432/cosmic_council_db"
            )
            
            print(f"📡 Connecting to: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")
            
            # Create database manager
            self.db_manager = DatabaseManager(database_url)
            
            # Test connection
            await self.db_manager.initialize()
            print("✅ Database connection established successfully")
            
            self.test_results["connection"] = True
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.test_results["connection"] = False
            return False
    
    async def test_schema_creation(self) -> bool:
        """Test database schema creation and validation."""
        print("\n🏗️ Testing Database Schema Creation...")
        
        try:
            # Initialize database schema
            await initialize_database(self.db_manager.database_url)
            print("✅ Database schema created successfully")
            
            # Test that tables exist by querying them
            async with self.db_manager.async_session() as session:
                # Test problems table
                result = await session.execute("SELECT COUNT(*) FROM problems")
                problem_count = result.scalar()
                print(f"📊 Problems table: {problem_count} records")
                
                # Test layers table
                result = await session.execute("SELECT COUNT(*) FROM layers")
                layer_count = result.scalar()
                print(f"📊 Layers table: {layer_count} records")
                
                # Test layer_runs table
                result = await session.execute("SELECT COUNT(*) FROM layer_runs")
                layer_run_count = result.scalar()
                print(f"📊 Layer runs table: {layer_run_count} records")
            
            self.test_results["schema"] = True
            return True
            
        except Exception as e:
            print(f"❌ Schema creation failed: {e}")
            self.test_results["schema"] = False
            return False
    
    async def test_crud_operations(self) -> bool:
        """Test Create, Read, Update, Delete operations."""
        print("\n📝 Testing CRUD Operations...")
        
        try:
            # Create a test problem
            problem_id = await self.db_manager.create_problem(
                title="Test Problem - Database Connection",
                description="Testing database CRUD operations",
                confidence_threshold=0.8
            )
            print(f"✅ Created problem: {problem_id}")
            
            # Read the problem
            problem = await self.db_manager.get_problem(problem_id)
            assert problem is not None, "Problem not found after creation"
            assert problem.title == "Test Problem - Database Connection"
            print("✅ Problem read successfully")
            
            # Update the problem
            await self.db_manager.update_problem_status(problem_id, "in_progress")
            updated_problem = await self.db_manager.get_problem(problem_id)
            assert updated_problem.status == "in_progress"
            print("✅ Problem updated successfully")
            
            # Create a layer run
            layer_run_id = await self.db_manager.create_layer_run(
                problem_id=problem_id,
                layer_id=LayerDefinitions.DECI.layer_id,
                revolution=1
            )
            print(f"✅ Created layer run: {layer_run_id}")
            
            # Create a sector run
            sector_run_id = await self.db_manager.create_sector_run(
                layer_run_id=layer_run_id,
                sector=SectorType.RED,
                status="completed"
            )
            print(f"✅ Created sector run: {sector_run_id}")
            
            # Test problem genealogy
            genealogy = await self.db_manager.get_problem_genealogy(problem_id)
            assert len(genealogy["layer_runs"]) == 1
            assert len(genealogy["sector_runs"]) == 1
            print("✅ Problem genealogy retrieved successfully")
            
            # Clean up test data
            await self.db_manager.delete_problem(problem_id)
            print("✅ Test data cleaned up")
            
            self.test_results["crud"] = True
            return True
            
        except Exception as e:
            print(f"❌ CRUD operations failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results["crud"] = False
            return False
    
    async def test_transaction_handling(self) -> bool:
        """Test database transaction handling and rollback."""
        print("\n🔄 Testing Transaction Handling...")
        
        try:
            # Create a problem
            problem_id = await self.db_manager.create_problem(
                title="Transaction Test Problem",
                description="Testing transaction rollback",
                confidence_threshold=0.8
            )
            
            # Test transaction rollback
            try:
                async with self.db_manager.async_session() as session:
                    # Start a transaction
                    await session.begin()
                    
                    # Create a layer run
                    layer_run = LayerRunModel(
                        layer_run_id=uuid.uuid4(),
                        problem_id=problem_id,
                        layer_id=LayerDefinitions.DECI.layer_id,
                        revolution=1,
                        status="started",
                        started_at=datetime.utcnow()
                    )
                    session.add(layer_run)
                    await session.flush()
                    
                    # Intentionally cause an error to test rollback
                    raise Exception("Intentional error for rollback test")
                    
            except Exception:
                # Transaction should be rolled back
                pass
            
            # Verify the layer run was not created (rollback worked)
            async with self.db_manager.async_session() as session:
                result = await session.execute(
                    "SELECT COUNT(*) FROM layer_runs WHERE problem_id = :problem_id",
                    {"problem_id": problem_id}
                )
                count = result.scalar()
                assert count == 0, "Transaction rollback failed"
            
            print("✅ Transaction rollback working correctly")
            
            # Clean up
            await self.db_manager.delete_problem(problem_id)
            
            self.test_results["transactions"] = True
            return True
            
        except Exception as e:
            print(f"❌ Transaction handling failed: {e}")
            self.test_results["transactions"] = False
            return False
    
    async def test_performance_metrics(self) -> bool:
        """Test database performance with multiple operations."""
        print("\n⚡ Testing Database Performance...")
        
        try:
            start_time = datetime.utcnow()
            
            # Create multiple problems
            problem_ids = []
            for i in range(10):
                problem_id = await self.db_manager.create_problem(
                    title=f"Performance Test Problem {i}",
                    description=f"Testing database performance with batch operations {i}",
                    confidence_threshold=0.8
                )
                problem_ids.append(problem_id)
            
            # Create layer runs for each problem
            layer_run_ids = []
            for problem_id in problem_ids:
                layer_run_id = await self.db_manager.create_layer_run(
                    problem_id=problem_id,
                    layer_id=LayerDefinitions.DECI.layer_id,
                    revolution=1
                )
                layer_run_ids.append(layer_run_id)
            
            # Create sector runs
            for layer_run_id in layer_run_ids:
                await self.db_manager.create_sector_run(
                    layer_run_id=layer_run_id,
                    sector=SectorType.RED,
                    status="completed"
                )
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            print(f"✅ Created 10 problems, 10 layer runs, 10 sector runs in {duration:.2f} seconds")
            print(f"📊 Average: {duration/30:.3f} seconds per operation")
            
            # Clean up
            for problem_id in problem_ids:
                await self.db_manager.delete_problem(problem_id)
            
            self.test_results["performance"] = True
            return True
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            self.test_results["performance"] = False
            return False
    
    async def test_connection_pooling(self) -> bool:
        """Test database connection pooling."""
        print("\n🏊 Testing Connection Pooling...")
        
        try:
            # Test concurrent operations
            async def create_problem(i):
                return await self.db_manager.create_problem(
                    title=f"Concurrent Test Problem {i}",
                    description=f"Testing concurrent database operations {i}",
                    confidence_threshold=0.8
                )
            
            # Create 5 problems concurrently
            tasks = [create_problem(i) for i in range(5)]
            problem_ids = await asyncio.gather(*tasks)
            
            print(f"✅ Created {len(problem_ids)} problems concurrently")
            
            # Clean up
            for problem_id in problem_ids:
                await self.db_manager.delete_problem(problem_id)
            
            self.test_results["pooling"] = True
            return True
            
        except Exception as e:
            print(f"❌ Connection pooling test failed: {e}")
            self.test_results["pooling"] = False
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all database tests."""
        print("🧪 Testing Database Connection and Schema Validation")
        print("=" * 60)
        
        tests = [
            self.setup_database_connection,
            self.test_schema_creation,
            self.test_crud_operations,
            self.test_transaction_handling,
            self.test_performance_metrics,
            self.test_connection_pooling
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                result = await test()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ {test.__name__} FAILED: {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 Database Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL DATABASE TESTS PASSED! Database integration is working correctly!")
        else:
            print("⚠️  Some database tests failed. Check the database configuration.")
            print("\n🔧 Troubleshooting Tips:")
            print("1. Ensure PostgreSQL is running on localhost:5432")
            print("2. Create database 'cosmic_council_db' with user 'cosmic_council'")
            print("3. Set DATABASE_URL environment variable if using different connection")
            print("4. Check database permissions and firewall settings")
        
        return passed == total
    
    async def cleanup(self):
        """Clean up database connections."""
        if self.db_manager:
            await self.db_manager.close()


async def main():
    """Run database connection tests."""
    tester = DatabaseConnectionTester()
    
    try:
        success = await tester.run_all_tests()
        return success
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
