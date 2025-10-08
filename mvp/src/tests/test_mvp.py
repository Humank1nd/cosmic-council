"""
Cosmic Council MVP Tests
The one test that proves everything works.
"""

import sys
import os
import tempfile
import unittest
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from cosmic_council import CosmicCouncilMVP
from cosmic_council.database import SimpleDatabase


class TestCosmicCouncilMVP(unittest.TestCase):
    """Test the Cosmic Council MVP functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.council = CosmicCouncilMVP()
        # Use a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = SimpleDatabase(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary database file
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_council_initialization(self):
        """Test that the council initializes correctly."""
        self.assertIsNotNone(self.council)
        self.assertEqual(self.council.get_enterprise_count(), 6)
        
        enterprise_names = self.council.get_enterprise_names()
        expected_names = [
            "Red Owl",
            "Orange Orangutan", 
            "Yellow Honeybee",
            "Green Tortoise",
            "Blue Dolphin",
            "Purple Elephant"
        ]
        
        for name in expected_names:
            self.assertIn(name, enterprise_names)
    
    def test_solve_simple_problem(self):
        """Test solving a simple problem end-to-end."""
        problem = "How do I improve team productivity?"
        
        results = self.council.solve_problem_sync(problem)
        
        # Must have results from all enterprises
        self.assertEqual(len(results), 6)
        
        # Check that all enterprises responded
        expected_enterprises = [
            "Red Owl",
            "Orange Orangutan", 
            "Yellow Honeybee",
            "Green Tortoise",
            "Blue Dolphin",
            "Purple Elephant"
        ]
        
        for enterprise in expected_enterprises:
            self.assertIn(enterprise, results)
            self.assertIsInstance(results[enterprise], str)
            self.assertGreater(len(results[enterprise]), 10)  # Must have meaningful content
            self.assertNotIn("Error:", results[enterprise])  # Must not be an error
    
    def test_enterprise_responses_are_meaningful(self):
        """Test that enterprise responses contain meaningful content."""
        problem = "How do I reduce costs?"
        
        results = self.council.solve_problem_sync(problem)
        
        # Check that each enterprise response is meaningful
        for enterprise, response in results.items():
            self.assertGreater(len(response), 20)  # Must be substantial
            self.assertIn(problem.lower(), response.lower())  # Must reference the problem
            # Check that response contains the enterprise's specialty
            if "Red Owl" in enterprise:
                self.assertIn("Research", response)
            elif "Orange Orangutan" in enterprise:
                self.assertIn("Planning", response)
            elif "Yellow Honeybee" in enterprise:
                self.assertIn("Development", response)
            elif "Green Tortoise" in enterprise:
                self.assertIn("Budget", response)
            elif "Blue Dolphin" in enterprise:
                self.assertIn("Communication", response)
            elif "Purple Elephant" in enterprise:
                self.assertIn("Support", response)
    
    def test_database_functionality(self):
        """Test that the database works correctly."""
        # Test saving a problem
        problem_text = "Test problem for database"
        problem_id = self.db.save_problem(problem_text)
        self.assertIsInstance(problem_id, int)
        self.assertGreater(problem_id, 0)
        
        # Test retrieving the problem
        problem = self.db.get_problem(problem_id)
        self.assertIsNotNone(problem)
        self.assertEqual(problem["problem_text"], problem_text)
        
        # Test saving solutions
        solutions = {
            "Red Owl": "Research solution",
            "Orange Orangutan": "Planning solution"
        }
        
        for enterprise, solution in solutions.items():
            solution_id = self.db.save_solution(problem_id, enterprise, solution)
            self.assertIsInstance(solution_id, int)
        
        # Test retrieving solutions
        retrieved_solutions = self.db.get_solutions_for_problem(problem_id)
        self.assertEqual(len(retrieved_solutions), 2)
        
        # Test saving a complete session
        session_id = self.db.save_problem_session(problem_id, solutions)
        self.assertIsInstance(session_id, int)
        
        # Test database stats
        stats = self.db.get_database_stats()
        self.assertGreaterEqual(stats["problems"], 1)
        self.assertGreaterEqual(stats["solutions"], 2)
        self.assertGreaterEqual(stats["sessions"], 1)
    
    def test_end_to_end_with_database(self):
        """Test complete end-to-end functionality with database."""
        problem_text = "How do I improve customer satisfaction?"
        
        # Solve the problem
        results = self.council.solve_problem_sync(problem_text)
        
        # Save to database
        problem_id = self.db.save_problem(problem_text)
        
        # Save all solutions
        for enterprise, solution in results.items():
            self.db.save_solution(problem_id, enterprise, solution)
        
        # Save the complete session
        session_id = self.db.save_problem_session(problem_id, results)
        
        # Verify everything was saved correctly
        retrieved_problem = self.db.get_problem(problem_id)
        self.assertEqual(retrieved_problem["problem_text"], problem_text)
        
        retrieved_solutions = self.db.get_solutions_for_problem(problem_id)
        self.assertEqual(len(retrieved_solutions), 6)
        
        # Verify all enterprises are represented
        enterprise_names = [sol["enterprise_name"] for sol in retrieved_solutions]
        expected_enterprises = [
            "Red Owl",
            "Orange Orangutan", 
            "Yellow Honeybee",
            "Green Tortoise",
            "Blue Dolphin",
            "Purple Elephant"
        ]
        
        for enterprise in expected_enterprises:
            self.assertIn(enterprise, enterprise_names)


class TestMVPSuccessCriteria(unittest.TestCase):
    """Test that the MVP meets all success criteria."""
    
    def test_system_starts_without_errors(self):
        """Test that the system can be imported and initialized without errors."""
        try:
            from cosmic_council import CosmicCouncilMVP
            council = CosmicCouncilMVP()
            self.assertIsNotNone(council)
        except Exception as e:
            self.fail(f"System failed to start: {e}")
    
    def test_can_solve_simple_problem(self):
        """Test that the system can solve a simple problem end-to-end."""
        from cosmic_council import CosmicCouncilMVP
        
        council = CosmicCouncilMVP()
        problem = "How do I improve team communication?"
        
        results = council.solve_problem_sync(problem)
        
        # Must return results
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), 6)
    
    def test_all_enterprises_respond(self):
        """Test that all enterprises respond meaningfully."""
        from cosmic_council import CosmicCouncilMVP
        
        council = CosmicCouncilMVP()
        problem = "How do I reduce waste?"
        
        results = council.solve_problem_sync(problem)
        
        for enterprise, response in results.items():
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 10)
            self.assertNotIn("Error:", response)
    
    def test_database_persistence_works(self):
        """Test that database persistence works."""
        import tempfile
        import os
        
        from cosmic_council.database import SimpleDatabase
        
        # Use temporary database
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            db = SimpleDatabase(temp_db.name)
            
            # Test basic operations
            problem_id = db.save_problem("Test problem")
            self.assertIsInstance(problem_id, int)
            
            solution_id = db.save_solution(problem_id, "Test Enterprise", "Test solution")
            self.assertIsInstance(solution_id, int)
            
            # Test retrieval
            problem = db.get_problem(problem_id)
            self.assertIsNotNone(problem)
            self.assertEqual(problem["problem_text"], "Test problem")
            
        finally:
            # Clean up
            if os.path.exists(temp_db.name):
                os.unlink(temp_db.name)


if __name__ == '__main__':
    print("🚀 Running Cosmic Council MVP Tests...")
    print("=" * 50)
    
    # Run the tests
    unittest.main(verbosity=2)
