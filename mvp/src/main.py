#!/usr/bin/env python3
"""
Cosmic Council MVP - Main Entry Point
The simplest working implementation that proves the concept.
"""

import sys
import argparse
from pathlib import Path

# Add the current directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cosmic_council import CosmicCouncilMVP
from cosmic_council.database import SimpleDatabase


def main():
    """Main entry point for the Cosmic Council MVP."""
    parser = argparse.ArgumentParser(
        description="Cosmic Council MVP - The Ultimate Problem-Solving Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "How do I improve team productivity?"
  python main.py --interactive
  python main.py --test
  python main.py --demo
        """
    )
    
    parser.add_argument(
        'problem',
        nargs='?',
        help='The problem to solve'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run the MVP tests'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run a demo problem'
    )
    
    parser.add_argument(
        '--database',
        default='cosmic_council_mvp.db',
        help='Database file path (default: cosmic_council_mvp.db)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.test:
            run_tests()
        elif args.demo:
            run_demo()
        elif args.interactive:
            run_interactive_mode(args.database)
        elif args.problem:
            solve_problem(args.problem, args.database)
        else:
            # No arguments provided, show help
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def solve_problem(problem: str, db_path: str):
    """Solve a specific problem."""
    print("🚀 Cosmic Council MVP - Problem Solver")
    print("=" * 50)
    
    # Initialize the council
    council = CosmicCouncilMVP()
    
    # Initialize database
    db = SimpleDatabase(db_path)
    
    # Solve the problem
    print(f"🎯 Problem: {problem}")
    print()
    
    results = council.solve_problem_sync(problem)
    
    # Save to database
    problem_id = db.save_problem(problem)
    
    for enterprise, solution in results.items():
        db.save_solution(problem_id, enterprise, solution)
        print(f"{solution}")
        print()
    
    # Save the complete session
    db.save_problem_session(problem_id, results)
    
    # Show database stats
    stats = db.get_database_stats()
    print("📊 Database Stats:")
    print(f"  Problems: {stats['problems']}")
    print(f"  Solutions: {stats['solutions']}")
    print(f"  Sessions: {stats['sessions']}")
    
    print("\n🎉 Problem solving complete!")


def run_interactive_mode(db_path: str):
    """Run in interactive mode."""
    print("🚀 Cosmic Council MVP - Interactive Mode")
    print("=" * 50)
    print("Enter problems to solve. Type 'quit' to exit.")
    print()
    
    # Initialize the council
    council = CosmicCouncilMVP()
    
    # Initialize database
    db = SimpleDatabase(db_path)
    
    while True:
        try:
            problem = input("🎯 Enter your problem: ").strip()
            
            if problem.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not problem:
                print("Please enter a problem to solve.")
                continue
            
            print(f"\n🔄 Solving: {problem}")
            print("-" * 30)
            
            # Solve the problem
            results = council.solve_problem_sync(problem)
            
            # Save to database
            problem_id = db.save_problem(problem)
            
            for enterprise, solution in results.items():
                db.save_solution(problem_id, enterprise, solution)
                print(f"{solution}")
                print()
            
            # Save the complete session
            db.save_problem_session(problem_id, results)
            
            print("✅ Problem solved and saved to database!")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print()


def run_demo():
    """Run a demo problem."""
    demo_problems = [
        "How do I improve team productivity?",
        "How do I reduce operational costs?",
        "How do I improve customer satisfaction?",
        "How do I implement a new technology?",
        "How do I manage remote teams effectively?"
    ]
    
    print("🚀 Cosmic Council MVP - Demo Mode")
    print("=" * 50)
    
    # Initialize the council
    council = CosmicCouncilMVP()
    
    # Initialize database
    db = SimpleDatabase("demo_mvp.db")
    
    for i, problem in enumerate(demo_problems, 1):
        print(f"\n🎯 Demo Problem {i}: {problem}")
        print("-" * 50)
        
        # Solve the problem
        results = council.solve_problem_sync(problem)
        
        # Save to database
        problem_id = db.save_problem(problem)
        
        for enterprise, solution in results.items():
            db.save_solution(problem_id, enterprise, solution)
            print(f"{solution}")
            print()
        
        # Save the complete session
        db.save_problem_session(problem_id, results)
        
        print("✅ Demo problem solved!")
        
        if i < len(demo_problems):
            input("\nPress Enter to continue to the next demo problem...")
    
    # Show final database stats
    stats = db.get_database_stats()
    print(f"\n📊 Final Database Stats:")
    print(f"  Problems: {stats['problems']}")
    print(f"  Solutions: {stats['solutions']}")
    print(f"  Sessions: {stats['sessions']}")
    
    print("\n🎉 Demo complete!")


def run_tests():
    """Run the MVP tests."""
    print("🚀 Cosmic Council MVP - Running Tests")
    print("=" * 50)
    
    import unittest
    from tests.test_mvp import TestCosmicCouncilMVP, TestMVPSuccessCriteria
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCosmicCouncilMVP))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMVPSuccessCriteria))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 All tests passed! MVP is working correctly.")
        return 0
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
